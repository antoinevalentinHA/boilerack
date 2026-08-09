"""Cycle de vie du processus et arret sur signal (lot C9).

Transforme `SIGINT` ou `SIGTERM` en **demande d'arret propre** pour le runner de
C8, et rend un resultat logique qui distingue l'arret demande de la panne.

CE MODULE N'EST PAS UN POINT D'ENTREE
    Il n'offre ni commande, ni lecture de configuration, ni nom de cle publique,
    et ne configure PAS la journalisation : une fonction appelee
    programmatiquement n'impose pas sa politique de journaux au processus hote.
    Le point d'entree installe et la configuration utilisateur relevent d'un lot
    ulterieur.

POURQUOI UN DESCRIPTEUR DE REVEIL, ET PAS UN `threading.Event`
    Deux faits, mesures avant d'ecrire ce module :

    1. `SystemClock.sleep()` delegue a `time.sleep()`, que CPython **reprend**
       apres un gestionnaire de signal qui ne leve pas (PEP 475). Armer un
       drapeau depuis un gestionnaire ne reveille donc rien ;
    2. armer un `threading.Event` DEPUIS un gestionnaire peut **bloquer le
       processus** : `Event.set()` prend un verrou non reentrant, et un second
       signal survenant dans cette fenetre rappelle `set()` sur le meme fil. Le
       blocage a ete reproduit de facon deterministe, y compris avec la garde
       `if not etat.is_set()`, inefficace parce que le drapeau n'est pose
       qu'APRES l'acquisition du verrou.

    `signal.set_wakeup_fd` fait ecrire l'octet du numero de signal par le
    **niveau C** de CPython. Le gestionnaire Python peut alors etre vide, et
    plus rien dans le chemin de signal n'acquiert de verrou : la course devient
    structurellement impossible.

CE QUE LE LOT NE PROMET PAS
    Aucune borne sur la duree totale de sortie. Un `run_due()` deja engage n'est
    pas tronque, et ni le publieur, ni le reseau, ni le broker ne sont bornes
    par un contrat. Seul le **reveil** est rendu prompt : voir
    docs/design/c9-process-lifecycle.md.

AUCUNE CONFORMITE PRODUCTION N'EST REVENDIQUEE.
"""

from __future__ import annotations

import selectors
import signal
import socket
import threading
from dataclasses import dataclass
from datetime import datetime
from types import TracebackType
from typing import Final, Iterable, Sequence

from boilerack.clock import Clock, SystemClock, check_duration
from boilerack.runtime import Runtime, RuntimeConfig, build_runtime

__all__ = [
    "SIGNALS_SURVEILLES",
    "CODE_ARRET_NORMAL",
    "CODE_INTERRUPTION",
    "SignalStop",
    "WakeupClock",
    "Wakeup",
    "SignalScope",
    "resultat_logique",
    "run_lifecycle",
]

#: Les deux seuls signaux que C9 traduit en demande d'arret.
SIGNALS_SURVEILLES: Final[tuple[signal.Signals, ...]] = (signal.SIGINT, signal.SIGTERM)

#: Resultats logiques. Ce ne sont PAS des codes de sortie de processus : c'est
#: l'appelant qui decidera d'en faire un. `130` est la convention Unix pour un
#: arret demande par `SIGINT`.
CODE_ARRET_NORMAL: Final = 0
CODE_INTERRUPTION: Final = 130

#: Taille de lecture au drainage. Sans importance fonctionnelle : le drainage
#: boucle jusqu'a epuisement.
_TAILLE_LECTURE: Final = 4096

#: Messages des groupes d'erreurs. Non contractuels : seule importe la
#: preservation des exceptions d'origine.
_ENTREE_ET_NETTOYAGE_ECHOUES: Final = "echec de l'entree, puis du nettoyage"
_CORPS_ET_RESTAURATION_ECHOUES: Final = "echec du corps, puis de la restauration"
_RESTAURATION_ECHOUEE: Final = "echec de la restauration de la portee de signaux"


def _gestionnaire_vide(numero: int, cadre: object) -> None:
    """Gestionnaire de signal **volontairement vide**.

    Il n'arme rien, n'ecrit rien, n'acquiert aucun verrou et n'appelle aucun
    code metier. C'est le niveau C de CPython qui ecrit l'octet dans le
    descripteur de reveil.

    Il doit neanmoins exister : sous `SIG_IGN`, **aucun octet n'est ecrit** —
    mesure faite, pas suppose. Sa seule raison d'etre est donc d'obtenir
    l'installation du gestionnaire C qui, lui, ecrit.
    """


class SignalStop:
    """Etat d'arret arme par drainage du descripteur de reveil.

    Satisfait `boilerack.runtime.StopSignal` : `is_set() -> bool`.

    Conserve la **premiere** cause reconnue. Les signaux suivants sont draines
    mais ne la remplacent jamais : le resultat logique doit rester deterministe,
    et C9 n'a aucune politique de second signal. Aucune priorite entre `SIGINT`
    et `SIGTERM` n'est introduite — l'ordre d'arrivee decide, et lui seul.

    Les octets correspondant a un signal NON surveille sont draines et
    **ignores** : `signal.set_wakeup_fd` est global au processus, donc un
    gestionnaire pose par l'hote pour un autre signal ecrirait aussi ici. Un tel
    octet ne doit ni armer l'arret, ni fournir une cause.

    Rien n'est ecrit depuis un gestionnaire de signal : l'etat et la cause ne
    sont modifies qu'au drainage, sur le fil qui appelle. Aucun verrou n'est
    donc necessaire, et aucun n'est pris.
    """

    def __init__(
        self,
        receiver: socket.socket,
        surveilles: Iterable[int] = SIGNALS_SURVEILLES,
    ) -> None:
        self._receiver = receiver
        self._surveilles = frozenset(int(n) for n in surveilles)
        self._arme = False
        self._cause: signal.Signals | None = None
        self._ignores: list[int] = []

    # -- drainage -------------------------------------------------------------

    def drain(self) -> None:
        """Consomme tout ce qui attend dans le descripteur, sans jamais bloquer.

        Le descripteur est non bloquant : `BlockingIOError` signale simplement
        qu'il n'y a plus rien a lire.
        """
        while True:
            try:
                octets = self._receiver.recv(_TAILLE_LECTURE)
            except BlockingIOError:
                return
            except OSError:
                # Descripteur ferme ou inutilisable : plus rien a drainer. Ne
                # jamais faire echouer une interrogation d'etat pour cela.
                return
            if not octets:
                return
            for octet in octets:
                self._enregistrer(octet)

    def _enregistrer(self, numero: int) -> None:
        if numero not in self._surveilles:
            self._ignores.append(numero)
            return
        self._arme = True
        if self._cause is None:
            self._cause = signal.Signals(numero)

    # -- interrogation --------------------------------------------------------

    def is_set(self) -> bool:
        """Draine PUIS repond.

        `is_set()` n'est pas une simple lecture passive : il draine le
        descripteur de reveil avant de repondre, afin de rendre visibles les
        signaux arrives en dehors d'une attente.

        C'est necessaire, et mesure : lorsque l'echeance suivante est deja
        depassee, C8 n'appelle pas `sleep()` — comportement normal et teste. Si
        seul `sleep()` drainait, l'arret passerait inapercu et des cycles
        superflus s'executeraient, voire une boucle sans fin.
        """
        self.drain()
        return self._arme

    @property
    def cause(self) -> signal.Signals | None:
        """Premiere cause reconnue, ou `None` si l'arret n'a pas ete demande.

        Ne draine pas : a lire apres `is_set()` ou apres le retour du runner.
        """
        return self._cause

    @property
    def signaux_ignores(self) -> tuple[int, ...]:
        """Octets draines ne correspondant a aucun signal surveille.

        Exposes pour l'observabilite et les tests ; sans effet sur l'arret.
        """
        return tuple(self._ignores)


class WakeupClock:
    """Horloge dont l'attente est interrompue par un signal.

    Satisfait `boilerack.clock.Clock`. `now()` et `monotonic()` sont delegues a
    une horloge de base — `SystemClock` par defaut — afin de ne rien reinventer
    de la semantique temporelle deja etablie.

    `sleep()` attend sur le descripteur de reveil : il rend la main a
    l'expiration de la duree demandee, ou des qu'un octet y est disponible — y
    compris s'il y a ete ecrit AVANT l'entree dans l'attente, puisque le
    descripteur le memorise.

    Aucune boucle active, aucune succession de petits sommeils : l'attente est
    passive.

    Reveil etranger : un signal non surveille, dont un gestionnaire aurait ete
    pose par le processus hote, ecrit lui aussi dans le descripteur et reveille
    donc l'attente sans armer l'arret. La consequence est benigne — le runner
    reconsulte l'etat, ne trouve pas d'arret, et rappelle `run_due()`, qui ne
    trouve alors rien de du. Aucune reprise d'attente n'est tentee : ce serait
    une politique, et rien ne l'exige.
    """

    def __init__(
        self,
        stop: SignalStop,
        receiver: socket.socket,
        base: Clock | None = None,
    ) -> None:
        self._stop = stop
        self._base: Clock = base if base is not None else SystemClock()
        self._selecteur = selectors.DefaultSelector()
        self._selecteur.register(receiver, selectors.EVENT_READ)

    # -- protocole `Clock` ----------------------------------------------------

    def now(self) -> datetime:
        return self._base.now()

    def monotonic(self) -> float:
        return self._base.monotonic()

    def sleep(self, seconds: float) -> None:
        """Attend au plus `seconds`, ou jusqu'au premier signal recu.

        Valide la duree exactement comme les autres horloges du depot, afin que
        l'horloge reelle, l'horloge virtuelle et celle-ci refusent les memes
        entrees.
        """
        duree = check_duration(seconds, op="sleep()")
        if self._selecteur.select(timeout=duree):
            self._stop.drain()

    # -- cycle de vie ---------------------------------------------------------

    def close(self) -> None:
        self._selecteur.close()


@dataclass(frozen=True)
class Wakeup:
    """Les deux coutures que la portee met a disposition.

    Construites ensemble a partir du meme descripteur : il est structurellement
    impossible que l'etat d'arret et l'attente en surveillent deux differents.
    """

    stop: SignalStop
    clock: WakeupClock


class SignalScope:
    """Portee qui installe le reveil par signal, et le retire integralement.

    A l'entree : une paire de sockets locales est creee, le descripteur de
    reveil est installe, et un gestionnaire **vide** est pose pour chaque signal
    surveille.

    A la sortie, quoi qu'il arrive : les gestionnaires precedents sont
    restaures a l'identique, le descripteur de reveil precedent est remis, et
    les deux sockets sont fermees. Rien n'est laisse dans le processus hote.

    ENTREE PARTIELLE — si une etape de l'installation echoue alors que les
    precedentes ont reussi, tout ce qui a ete pose est retire avant que
    l'erreur ne remonte. Et si ce nettoyage echoue a son tour, les deux erreurs
    sont conservees dans un groupe, **entree d'abord** — meme politique que
    `__exit__`, et pour la meme raison : aucune erreur ne doit disparaitre.

    FIL PRINCIPAL — `signal.signal` comme `signal.set_wakeup_fd` echouent
    ailleurs. La verification est faite AVANT toute allocation, pour ne rien
    laisser derriere en cas de refus.

    PAS DE RESEAU — `socket.socketpair()` cree deux extremites locales
    appariees, jamais publiees, jamais joignables de l'exterieur. C'est un
    tuyau interne, pas un port ouvert.
    """

    def __init__(self, surveilles: Sequence[int] = SIGNALS_SURVEILLES) -> None:
        self._surveilles = tuple(int(n) for n in surveilles)
        self._emetteur: socket.socket | None = None
        self._recepteur: socket.socket | None = None
        self._clock: WakeupClock | None = None
        self._anciens_gestionnaires: dict[int, object] = {}
        self._ancien_fd: int | None = None

    # -- entree ---------------------------------------------------------------

    def __enter__(self) -> Wakeup:
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError(
                "la portee de signaux exige le fil principal : signal.signal et "
                "signal.set_wakeup_fd n'y fonctionnent pas autrement"
            )
        emetteur, recepteur = socket.socketpair()
        try:
            # `set_wakeup_fd` exige un descripteur non bloquant ; il ne le
            # verifie pas, c'est donc a l'appelant de le garantir. Le recepteur
            # l'est aussi, pour que le drainage ne bloque jamais.
            emetteur.setblocking(False)
            recepteur.setblocking(False)
            self._ancien_fd = signal.set_wakeup_fd(emetteur.fileno())
            for numero in self._surveilles:
                self._anciens_gestionnaires[numero] = signal.getsignal(numero)
                signal.signal(numero, _gestionnaire_vide)
        except BaseException as entree:
            # Meme politique que `__exit__`, pour la meme raison : ni l'erreur
            # d'entree ni celle du nettoyage ne doit etre perdue, et l'erreur
            # d'entree reste la premiere. Sans ce groupe, l'erreur de nettoyage
            # deviendrait l'exception principale et l'entree ne survivrait que
            # dans `__context__` — reproduit avant d'etre corrige.
            self._emetteur, self._recepteur = emetteur, recepteur
            try:
                self._restaurer()
            except Exception as nettoyage:
                raise BaseExceptionGroup(
                    _ENTREE_ET_NETTOYAGE_ECHOUES, [entree, nettoyage]
                ) from None
            raise
        self._emetteur, self._recepteur = emetteur, recepteur
        stop = SignalStop(recepteur, self._surveilles)
        self._clock = WakeupClock(stop, recepteur)
        return Wakeup(stop=stop, clock=self._clock)

    # -- sortie ---------------------------------------------------------------

    def __exit__(
        self,
        type_exc: type[BaseException] | None,
        exc: BaseException | None,
        trace: TracebackType | None,
    ) -> bool:
        """Restaure tout, et ne perd jamais une erreur.

        Politique alignee sur celle de C8, et non inventee ici :

        - si la restauration reussit, l'exception du corps poursuit sa route ;
        - si la restauration echoue seule, son erreur remonte telle quelle ;
        - si les deux echouent, un groupe porte les deux, dans l'ordre : erreur
          du corps d'abord, erreur de restauration ensuite.

        Le groupe est construit avec `BaseExceptionGroup` et non avec
        `ExceptionGroup`, parce que le corps peut sortir sur une
        `BaseException` — `SystemExit`, par exemple. `ExceptionGroup` refuse
        alors de l'imbriquer et leve `TypeError`, ce qui **perdrait**
        l'exception d'origine.

        Ce choix ne change rien au cas courant : `BaseExceptionGroup` rend un
        `ExceptionGroup` des lors que tous ses membres sont des `Exception`.
        Le type observe reste donc celui d'avant quand les deux erreurs sont
        ordinaires, et devient `BaseExceptionGroup` seulement lorsqu'il le faut.
        """
        try:
            self._restaurer()
        except Exception as restauration:
            if exc is not None:
                raise BaseExceptionGroup(
                    _CORPS_ET_RESTAURATION_ECHOUES, [exc, restauration]
                ) from None
            raise
        return False

    def _restaurer(self) -> None:
        """Tente TOUTES les etapes, meme si l'une echoue, puis groupe les echecs."""
        echecs: list[Exception] = []

        for etape in (self._fermer_selecteur, self._retirer_gestionnaires,
                      self._retirer_descripteur, self._fermer_sockets):
            try:
                etape()
            except Exception as erreur:  # pragma: no cover - defense en profondeur
                echecs.append(erreur)

        if len(echecs) == 1:
            raise echecs[0]
        if echecs:  # pragma: no cover - defense en profondeur
            raise ExceptionGroup(_RESTAURATION_ECHOUEE, echecs)

    def _fermer_selecteur(self) -> None:
        if self._clock is not None:
            self._clock.close()
            self._clock = None

    def _retirer_gestionnaires(self) -> None:
        while self._anciens_gestionnaires:
            numero, ancien = self._anciens_gestionnaires.popitem()
            signal.signal(numero, ancien)  # type: ignore[arg-type]

    def _retirer_descripteur(self) -> None:
        if self._ancien_fd is not None:
            ancien, self._ancien_fd = self._ancien_fd, None
            signal.set_wakeup_fd(ancien)

    def _fermer_sockets(self) -> None:
        for nom in ("_emetteur", "_recepteur"):
            douille: socket.socket | None = getattr(self, nom)
            if douille is not None:
                setattr(self, nom, None)
                douille.close()


def resultat_logique(cause: signal.Signals | None) -> int:
    """Traduit la cause d'arret en resultat logique.

    `SIGINT` rend `130` — convention Unix pour un arret demande par
    l'utilisateur — ; tout le reste rend `0`. Aucune autre valeur n'est
    inventee : une panne ne passe pas par ici, elle remonte en exception.
    """
    if cause == signal.SIGINT:
        return CODE_INTERRUPTION
    return CODE_ARRET_NORMAL


def run_lifecycle(
    config: RuntimeConfig,
    *,
    surveilles: Sequence[int] = SIGNALS_SURVEILLES,
) -> int:
    """Assemble, execute jusqu'a l'arret demande, et rend le resultat logique.

    Prend une `RuntimeConfig` **deja construite** : C9 ne lit aucune source de
    configuration et n'invente aucun nom de cle publique.

    Sequence :

        portee de signaux ouverte
            build_runtime(config, stop, clock=horloge interruptible)
            runtime.runner.run()          <- C8 gere start / boucle / stop
        portee refermee, tout restaure
        resultat logique calcule a partir de la premiere cause

    RESULTAT — `0` pour un retour normal ou un arret demande par `SIGTERM`,
    `130` pour un arret demande par `SIGINT`. Ce n'est pas un code de sortie de
    processus : c'est a l'appelant d'en faire un s'il le souhaite.

    PANNE — rien n'est masque ni traduit. Une exception levee par C8 traverse
    avec son identite, `ExceptionGroup` compris. Elle n'est jamais convertie en
    resultat logique : un arret demande et une panne ne doivent pas se
    confondre.

    FIL PRINCIPAL requis.
    """
    with SignalScope(surveilles) as wakeup:
        runtime: Runtime = build_runtime(config, wakeup.stop, clock=wakeup.clock)
        runtime.runner.run()
        # Drainage ULTIME avant de conclure. Un signal peut arriver apres le
        # dernier point de controle du runner — pendant `stop()`, par exemple —
        # et il doit tout de meme etre rapporte. Sans cela, le resultat logique
        # dependrait du nombre d'interrogations faites par le runner.
        wakeup.stop.drain()
        return resultat_logique(wakeup.stop.cause)
