"""Tests du lot C9 — cycle de vie du processus et arret sur signal.

Deux natures de tests cohabitent, deliberement :

1. les tests du module de production `boilerack.lifecycle` — etat d'arret,
   horloge interruptible, portee de signaux, fonction de cycle de vie ;
2. les tests de **caracterisation** conserves parce qu'ils verrouillent un
   invariant reel : le comportement de la bibliotheque standard sur lequel le
   module repose, et surtout la **preuve du defaut qui a fait rejeter**
   l'architecture initiale — appeler `threading.Event.set()` depuis un
   gestionnaire de signal peut bloquer le processus, garde comprise.

Rien ici ne contacte de broker, de `vclient`, de `vcontrold` ni de chaudiere.
Les seuls sous-processus lances sont des interpreteurs Python de test, sans
reseau, tous bornes par un delai dur.

Marqueurs, selon la convention du depot :

- `reference` — comportement eprouve, a conserver ;
- `unknown`   — non demontrable sur cette plateforme.
"""

from __future__ import annotations

import ast
import gc
import inspect
import os
import pathlib
import queue
import re
import selectors
import signal
import socket
import subprocess
import sys
import threading
import textwrap
import time
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

import boilerack.lifecycle

from boilerack.adapters.config import MqttConfig, VclientConfig
from boilerack.adapters.mqtt_paho import PahoMqttClient
from boilerack.clock import Clock, SystemClock, check_duration
from boilerack.lifecycle import (
    CODE_ARRET_NORMAL,
    CODE_INTERRUPTION,
    SIGNALS_SURVEILLES,
    SignalScope,
    SignalStop,
    Wakeup,
    WakeupClock,
    resultat_logique,
    run_lifecycle,
)
from boilerack.runtime import (
    NeverStop,
    ReadSurfaceRunner,
    RuntimeConfig,
    StopSignal,
    TransactionSurfaceConfig,
    build_runtime,
)
from boilerack.testing import VirtualClock

POSIX = os.name == "posix"


class _FauxPaho:
    """Surface `PahoLike` minimale. Aucune socket, aucun reseau."""

    on_connect = on_disconnect = on_publish = on_message = None

    def connect(self, host, port, keepalive): ...
    def disconnect(self): ...
    def loop_start(self): ...
    def loop_stop(self): ...
    def subscribe(self, topic, qos=0): ...
    def publish(self, topic, payload, qos=0, retain=False): ...
    def will_set(self, topic, payload=None, qos=0, retain=False): ...
    def will_clear(self): ...


def _config_runtime(*, transactionnelle: bool = False) -> RuntimeConfig:
    """Configuration d'assemblage sans aucune valeur de site.

    `transactionnelle` ouvre l'autorite W4-E2. Le defaut reste FERME : les
    dizaines de tests C9 qui appellent cette fabrique gardent exactement le
    comportement qu'ils eprouvaient avant W4-E2.
    """
    return RuntimeConfig(
        mqtt=MqttConfig(host="broker.invalid"),
        vclient=VclientConfig(executable="vclient"),
        transaction_surface=TransactionSurfaceConfig(enabled=transactionnelle),
    )

# ---------------------------------------------------------------------------
# A. Mecanisme d'attente interruptible — `threading.Event`
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_event_etat_initial_et_type() -> None:
    """Non arme au depart, et `is_set()` rend un vrai `bool`.

    C8 consomme `StopSignal.is_set() -> bool` : le type importe autant que la
    valeur.
    """
    evenement = threading.Event()
    assert evenement.is_set() is False
    assert isinstance(evenement.is_set(), bool)


@pytest.mark.reference
def test_event_armement_idempotent() -> None:
    """Deux armements successifs laissent exactement le meme etat.

    C'est ce qui rend inutile toute politique de « second signal ».
    """
    evenement = threading.Event()
    evenement.set()
    premier = evenement.is_set()
    evenement.set()
    assert premier is evenement.is_set() is True


#: Tolerance de granularite d'horloge, en secondes. `Event.wait(t)` peut rendre
#: la main quelques millisecondes AVANT `t` mesure sur `time.monotonic()` : les
#: deux ne derivent pas de la meme source. Ecart d'avance maximal observe sur la
#: machine de developpement : 7.2 ms sur 60 mesures. La marge retenue est large
#: pour que le test reste stable sur une machine d'integration chargee, tout en
#: restant tres inferieure aux durees comparees.
_TOLERANCE_HORLOGE_S = 0.05


@pytest.mark.reference
def test_event_wait_respecte_l_echeance_quand_rien_n_est_arme() -> None:
    """L'attente va a son terme, a la granularite d'horloge pres.

    Fait a connaitre pour C9 : aucun test ne doit exiger `ecoule >= duree` au
    sens strict — voir `_TOLERANCE_HORLOGE_S`.
    """
    evenement = threading.Event()
    debut = time.monotonic()
    reveille = evenement.wait(0.30)
    ecoule = time.monotonic() - debut
    assert reveille is False
    assert ecoule >= 0.30 - _TOLERANCE_HORLOGE_S


@pytest.mark.reference
def test_event_wait_rend_la_main_immediatement_si_deja_arme() -> None:
    """Un arret arme AVANT l'attente ne doit provoquer aucune attente.

    Sans cela, un signal recu entre deux cycles serait paye au prix fort.
    """
    evenement = threading.Event()
    evenement.set()
    debut = time.monotonic()
    assert evenement.wait(30.0) is True
    assert time.monotonic() - debut < 1.0


@pytest.mark.reference
def test_event_wait_est_ecourtee_par_un_armement_concurrent() -> None:
    """La propriete centrale de C9 : armer reveille, au lieu d'attendre."""
    evenement = threading.Event()
    minuterie = threading.Timer(0.10, evenement.set)
    minuterie.start()
    try:
        debut = time.monotonic()
        reveille = evenement.wait(30.0)
        ecoule = time.monotonic() - debut
    finally:
        minuterie.cancel()
    assert reveille is True
    assert ecoule < 5.0, "l'attente n'a pas ete ecourtee"


@pytest.mark.reference
def test_event_wait_est_passive_et_ne_scrute_pas() -> None:
    """Aucune scrutation active : le temps CPU consomme reste negligeable.

    Ecarte de fait la solution « boucle de petits sleep() », qui consommerait
    proportionnellement a la duree.
    """
    evenement = threading.Event()
    cpu_avant = time.process_time()
    mur_avant = time.monotonic()
    evenement.wait(0.50)
    cpu = time.process_time() - cpu_avant
    mur = time.monotonic() - mur_avant
    assert mur >= 0.50 - _TOLERANCE_HORLOGE_S
    assert cpu < 0.10, f"attente non passive : {cpu:.3f}s de CPU pour {mur:.3f}s"


@pytest.mark.reference
def test_event_satisfait_structurellement_stop_signal() -> None:
    """Un `Event` peut servir directement de `StopSignal` pour C8.

    `StopSignal` n'est pas `runtime_checkable` : la conformite se prouve en
    l'utilisant, comme le fait deja `tests/test_runtime.py`.
    """
    evenement = threading.Event()
    with pytest.raises(TypeError, match="runtime_checkable"):
        isinstance(evenement, StopSignal)  # noqa: B015
    assert hasattr(evenement, "is_set") and callable(evenement.is_set)


@pytest.mark.reference
def test_le_verrou_interne_de_event_n_est_pas_reentrant() -> None:
    """Le fait qui a fait REJETER l'architecture « set() depuis le gestionnaire ».

    `Event.set()` prend un `Lock` non reentrant, tandis que `is_set()` ne prend
    aucun verrou. Un second signal qui arrive pendant l'execution de `set()` et
    rappelle `set()` sur le meme fil se bloque definitivement.

    La garde `if not etat.is_set()` avait ete envisagee comme attenuation. Elle
    est **inefficace** : le drapeau n'est pose qu'APRES l'acquisition du verrou,
    donc la garde laisse passer precisement dans la fenetre dangereuse. Voir la
    reproduction deterministe plus bas.
    """
    evenement = threading.Event()
    verrou = evenement._cond._lock  # type: ignore[attr-defined]
    assert verrou.acquire(timeout=0.5) is True
    try:
        assert verrou.acquire(timeout=0.2) is False, "verrou reentrant : analyse a refaire"
    finally:
        verrou.release()
    assert "self._cond" not in inspect.getsource(threading.Event.is_set)


@pytest.mark.reference
def test_simple_queue_est_documentee_reentrante() -> None:
    """Solution de repli si la cause devait etre posee sans verrou du tout."""
    assert "reentrant" in (inspect.getdoc(queue.SimpleQueue) or "").lower()


# ---------------------------------------------------------------------------
# A bis. Le blocage est CONSTRUCTIBLE — reproduction deterministe
# ---------------------------------------------------------------------------

#: Deux vrais gestionnaires, aucun verrou pris a la main. `Event` est instrumente
#: pour delivrer le second signal a l'interieur meme de `set()`, entre
#: l'acquisition du verrou et la pose du drapeau : la fenetre exacte decrite.
_ENFANT_BLOCAGE = """
import signal, sys, threading

AVEC_GARDE = sys.argv[1] == 'garde'

class EventInstrumente(threading.Event):
    declenche = False
    def set(self):
        with self._cond:
            if not EventInstrumente.declenche:
                EventInstrumente.declenche = True
                signal.raise_signal(signal.SIGTERM)
            self._flag = True
            self._cond.notify_all()

ev = EventInstrumente()

def poser():
    if AVEC_GARDE:
        if not ev.is_set():
            ev.set()
    else:
        ev.set()

signal.signal(signal.SIGINT, lambda n, f: poser())
signal.signal(signal.SIGTERM, lambda n, f: poser())
print('DEBUT', flush=True)
signal.raise_signal(signal.SIGINT)
print('TERMINE', flush=True)
"""


#: Delai au-dela duquel l'enfant est declare bloque. Le blocage, lorsqu'il se
#: produit, est immediat : cette valeur est un garde-fou, pas une mesure.
_DELAI_BLOCAGE_S = 5


def _enfant_bloque(variante: str) -> bool:
    """Lance l'enfant et rend True s'il s'est bloque. Jamais d'attente infinie."""
    proc = subprocess.Popen(
        [sys.executable, "-u", "-c", _ENFANT_BLOCAGE, variante],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        proc.wait(timeout=_DELAI_BLOCAGE_S)
        bloque = False
    except subprocess.TimeoutExpired:
        bloque = True
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=30)
    return bloque


@pytest.mark.reference
def test_appeler_set_depuis_un_gestionnaire_peut_bloquer_le_processus() -> None:
    """Le defaut n'est pas theorique : il se construit, et de facon deterministe."""
    assert _enfant_bloque("nu") is True, "le blocage attendu ne s'est pas produit"


@pytest.mark.reference
def test_la_garde_is_set_ne_supprime_pas_le_blocage() -> None:
    """Refute l'attenuation envisagee lors de la caracterisation precedente.

    `is_set()` est encore faux quand le verrou est deja detenu : la garde laisse
    donc passer exactement dans la fenetre qu'elle etait censee fermer. C'est
    cette mesure qui a fait rejeter l'architecture « `set()` depuis le
    gestionnaire » au profit du reveil par descripteur.
    """
    assert _enfant_bloque("garde") is True, "la garde a supprime le blocage : analyse a refaire"


# ---------------------------------------------------------------------------
# B. Premiere cause conservee — idiome, pas encore implementation
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_premiere_cause_conservee_par_setdefault() -> None:
    """« La premiere cause reste la cause », sans verrou ni relecture.

    `dict.setdefault` effectue le test et l'ecriture en une seule operation :
    le second signal ne reecrit pas l'histoire, et le resultat logique reste
    deterministe.
    """
    etat: dict[str, int] = {}
    etat.setdefault("cause", int(signal.SIGINT))
    etat.setdefault("cause", int(signal.SIGTERM))
    assert etat["cause"] == int(signal.SIGINT)


@pytest.mark.reference
def test_premiere_cause_conservee_quel_que_soit_l_ordre() -> None:
    etat: dict[str, int] = {}
    etat.setdefault("cause", int(signal.SIGTERM))
    etat.setdefault("cause", int(signal.SIGINT))
    assert etat["cause"] == int(signal.SIGTERM)


# ---------------------------------------------------------------------------
# C. Gestionnaires de signaux
# ---------------------------------------------------------------------------


@pytest.fixture
def gestionnaires_restaures():
    """Restaure les gestionnaires SIGINT/SIGTERM quoi qu'il arrive.

    Aucun test de ce fichier ne doit laisser l'etat global du processus
    modifie, meme s'il echoue.
    """
    numeros = [signal.SIGINT] + ([signal.SIGTERM] if hasattr(signal, "SIGTERM") else [])
    anciens = {n: signal.getsignal(n) for n in numeros}
    try:
        yield numeros
    finally:
        for n, ancien in anciens.items():
            signal.signal(n, ancien)


@pytest.mark.reference
def test_signal_signal_rend_le_gestionnaire_precedent(gestionnaires_restaures) -> None:
    """C'est cette valeur de retour qui rendra la restauration exacte possible."""

    def gestionnaire(numero, cadre):  # pragma: no cover - jamais declenche ici
        ...

    avant = signal.getsignal(signal.SIGINT)
    retour = signal.signal(signal.SIGINT, gestionnaire)
    assert retour is avant
    assert signal.getsignal(signal.SIGINT) is gestionnaire
    signal.signal(signal.SIGINT, retour)
    assert signal.getsignal(signal.SIGINT) is avant


@pytest.mark.reference
def test_restauration_possible_meme_lorsque_le_corps_leve(gestionnaires_restaures) -> None:
    """La portee de C9 devra restaurer dans un `finally`, pas en fin de bloc."""

    def gestionnaire(numero, cadre):  # pragma: no cover - jamais declenche ici
        ...

    avant = signal.getsignal(signal.SIGINT)
    ancien = signal.signal(signal.SIGINT, gestionnaire)
    with pytest.raises(RuntimeError, match="panne simulee"):
        try:
            raise RuntimeError("panne simulee")
        finally:
            signal.signal(signal.SIGINT, ancien)
    assert signal.getsignal(signal.SIGINT) is avant


@pytest.mark.reference
def test_signal_signal_echoue_hors_du_fil_principal() -> None:
    """Contrainte structurante : la portee de C9 exige le fil principal."""
    resultat: dict[str, object] = {}

    def dans_un_fil() -> None:
        try:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            resultat["issue"] = "installe"
        except Exception as exc:
            resultat["issue"] = type(exc).__name__
            resultat["message"] = str(exc)

    fil = threading.Thread(target=dans_un_fil)
    fil.start()
    fil.join(timeout=10)
    assert resultat["issue"] == "ValueError"
    assert "main thread" in str(resultat["message"])


@pytest.mark.reference
def test_sigint_est_disponible_partout() -> None:
    assert hasattr(signal, "SIGINT")
    assert hasattr(signal, "SIGTERM")


# ---------------------------------------------------------------------------
# D. SIGINT propre, sans KeyboardInterrupt — en processus
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_sigint_arme_sans_lever_keyboard_interrupt(gestionnaires_restaures) -> None:
    """Le comportement vise par C9, isole de tout le reste.

    Un gestionnaire qui arme l'etat et ne leve rien remplace le
    `KeyboardInterrupt` par une demande d'arret. La cause est enregistree.
    """
    etat = threading.Event()
    cause: dict[str, int] = {}

    def gestionnaire(numero, cadre) -> None:
        cause.setdefault("cause", numero)
        if not etat.is_set():
            etat.set()

    signal.signal(signal.SIGINT, gestionnaire)
    signal.raise_signal(signal.SIGINT)  # aucune KeyboardInterrupt attendue
    assert etat.is_set() is True
    assert cause["cause"] == int(signal.SIGINT)


@pytest.mark.reference
def test_un_gestionnaire_python_ne_s_execute_que_sur_le_fil_principal(
    gestionnaires_restaures,
) -> None:
    """Fait portable, et **troisieme** raison de rejeter l'architecture `Event`.

    `signal.raise_signal` leve le signal dans le fil **appelant**. Le
    gestionnaire Python, lui, ne s'execute que sur le fil principal, et
    seulement lorsque celui-ci reprend l'execution de bytecode.

    Consequence sous POSIX : si le fil principal est bloque dans
    `Event.wait()`, un signal leve depuis un autre fil n'arme rien avant la fin
    de l'attente. L'attente n'est donc PAS ecourtee. Une version anterieure de
    ce fichier affirmait le contraire — c'etait une particularite de la
    plateforme de developpement, pas une propriete portable.

    Le mecanisme retenu par C9 ne souffre pas de cette limite : l'octet du
    reveil est ecrit par le **niveau C**, depuis n'importe quel fil, sans
    attendre l'execution d'un gestionnaire Python. Les tests de production plus
    bas le demontrent.
    """
    fil_du_gestionnaire: list[str] = []

    def gestionnaire(numero, cadre) -> None:
        fil_du_gestionnaire.append(threading.current_thread().name)

    signal.signal(signal.SIGINT, gestionnaire)
    fil = threading.Thread(
        target=lambda: signal.raise_signal(signal.SIGINT), name="fil-secondaire"
    )
    fil.start()
    fil.join(timeout=10)
    # Rendre la main a l'interprete pour qu'il traite l'appel en attente.
    for _ in range(100):
        if fil_du_gestionnaire:
            break
        time.sleep(0.01)
    assert fil_du_gestionnaire == ["MainThread"], (
        "le gestionnaire Python doit s'executer sur le fil principal, "
        f"observe : {fil_du_gestionnaire}"
    )


@pytest.mark.skipif(
    POSIX, reason="sous POSIX, raise_signal vise le fil appelant : voir la docstring"
)
@pytest.mark.unknown
def test_hors_posix_sigint_ecourte_une_attente_sur_event(gestionnaires_restaures) -> None:
    """Particularite de plateforme, conservee mais explicitement bornee.

    Hors POSIX, un `SIGINT` leve depuis un fil secondaire fait tout de meme
    executer le gestionnaire sur le fil principal pendant que celui-ci attend,
    et l'attente est ecourtee. **Ce n'est pas portable** : sous POSIX,
    `raise_signal` vise le fil appelant et le gestionnaire n'est traite qu'apres
    la fin de l'attente du fil principal.

    Ce test est conserve pour que la difference reste visible et datee, et non
    pour fonder quoi que ce soit : l'architecture `Event` est rejetee.
    """
    etat = threading.Event()

    def gestionnaire(numero, cadre) -> None:
        if not etat.is_set():
            etat.set()

    signal.signal(signal.SIGINT, gestionnaire)
    minuterie = threading.Timer(0.10, lambda: signal.raise_signal(signal.SIGINT))
    minuterie.start()
    try:
        debut = time.monotonic()
        reveille = etat.wait(30.0)
        ecoule = time.monotonic() - debut
    finally:
        minuterie.cancel()
    assert reveille is True
    assert ecoule < 5.0


@pytest.mark.reference
def test_time_sleep_n_est_pas_ecourte_par_un_gestionnaire_pose_drapeau(
    gestionnaires_restaures,
) -> None:
    """Le fait qui justifie tout le lot (PEP 475).

    `SystemClock.sleep` delegue a `time.sleep`, que CPython **reprend** apres
    un gestionnaire qui ne leve pas. Armer un drapeau ne reveille donc rien :
    c'est pourquoi C9 a besoin d'une attente interruptible, et non seulement
    d'un gestionnaire.
    """
    etat = threading.Event()
    signal.signal(signal.SIGINT, lambda numero, cadre: etat.set())
    minuterie = threading.Timer(0.10, lambda: signal.raise_signal(signal.SIGINT))
    minuterie.start()
    try:
        debut = time.monotonic()
        time.sleep(0.60)
        ecoule = time.monotonic() - debut
    finally:
        minuterie.cancel()
    assert etat.is_set() is True, "le gestionnaire n'a pas ete execute"
    assert ecoule >= 0.60 - _TOLERANCE_HORLOGE_S, (
        "time.sleep a ete ecourte : PEP 475 ne s'applique pas ici"
    )


# ---------------------------------------------------------------------------
# E. Compatibilite de la couture avec le runner C8, sans le modifier
# ---------------------------------------------------------------------------


class _HorlogeSurEvenement:
    """Specimen de caracterisation, PAS le futur code de production.

    Satisfait `Clock` et rend la main des que l'etat est arme. Sert uniquement
    a prouver que le `ReadSurfaceRunner` de C8 honore un arret arme pendant son
    attente, sans qu'aucune ligne de C8 ne change.
    """

    def __init__(self, etat: threading.Event) -> None:
        self._etat = etat
        self.attentes: list[float] = []

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        duree = check_duration(seconds, op="sleep()")
        self.attentes.append(duree)
        self._etat.wait(duree)


class _PublieurJournal:
    """Publieur factice : journalise, ne publie rien, ne contacte rien."""

    def __init__(self, horizon_s: float) -> None:
        self.appels: list[str] = []
        self.started = False
        self._horizon = horizon_s

    def start(self) -> None:
        self.appels.append("start")
        self.started = True

    def stop(self) -> None:
        self.appels.append("stop")
        self.started = False

    def due_at(self) -> float:
        self.appels.append("due_at")
        return time.monotonic() + self._horizon

    def run_due(self) -> None:  # pragma: no cover - jamais atteint ici
        self.appels.append("run_due")


@pytest.mark.reference
def test_le_specimen_satisfait_le_protocole_clock() -> None:
    horloge = _HorlogeSurEvenement(threading.Event())
    assert isinstance(horloge, Clock)  # `Clock` est runtime_checkable
    assert isinstance(horloge.now(), datetime)
    assert isinstance(horloge.monotonic(), float)


@pytest.mark.reference
def test_le_specimen_refuse_les_memes_durees_que_les_autres_horloges() -> None:
    """Invariant `Clock` : les trois horloges doivent refuser les memes entrees."""
    horloge = _HorlogeSurEvenement(threading.Event())
    for invalide in (-1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            horloge.sleep(invalide)
    for invalide in (-1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            SystemClock().sleep(invalide)


@pytest.mark.reference
def test_le_runner_c8_honore_un_arret_arme_pendant_son_attente() -> None:
    """Preuve que la couture prevue fonctionne sur le C8 REEL, non modifie.

    Le runner dort jusqu'a une echeance lointaine ; l'etat est arme pendant
    l'attente ; l'horloge rend la main ; le runner voit l'arret a sa
    reconsultation post-attente et sort par `stop()`.
    """
    etat = threading.Event()
    horloge = _HorlogeSurEvenement(etat)
    publieur = _PublieurJournal(horizon_s=30.0)
    minuterie = threading.Timer(0.10, etat.set)
    minuterie.start()
    try:
        debut = time.monotonic()
        ReadSurfaceRunner(publisher=publieur, clock=horloge, stop=etat).run()
        ecoule = time.monotonic() - debut
    finally:
        minuterie.cancel()

    assert publieur.appels == ["start", "due_at", "stop"]
    assert "run_due" not in publieur.appels, "un cycle superflu a ete execute"
    assert publieur.started is False
    assert ecoule < 10.0, "le runner n'a pas ete reveille"
    assert horloge.attentes and horloge.attentes[0] > 20.0


@pytest.mark.reference
def test_le_runner_c8_sort_immediatement_si_l_arret_est_deja_arme() -> None:
    etat = threading.Event()
    etat.set()
    publieur = _PublieurJournal(horizon_s=30.0)
    horloge = _HorlogeSurEvenement(etat)
    debut = time.monotonic()
    ReadSurfaceRunner(publisher=publieur, clock=horloge, stop=etat).run()
    assert publieur.appels == ["start", "stop"]
    assert horloge.attentes == []
    assert time.monotonic() - debut < 5.0


# ---------------------------------------------------------------------------
# F. `build_runtime` — la couture d'horloge, ouverte par C9
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_build_runtime_reste_appelable_avec_deux_arguments_positionnels() -> None:
    """Compatibilite : tous les sites d'appel anterieurs passent `(config, stop)`.

    REVISE PAR W3. L'assertion d'origine figeait la LISTE exacte des parametres,
    ce qui interdisait toute couture ulterieure. Ce qu'elle protegeait vraiment
    est plus precis, et c'est cela qui est desormais affirme :

    1. `config` et `stop` restent les DEUX seuls parametres positionnels, tous
       deux obligatoires — aucun site d'appel anterieur n'est casse ;
    2. TOUT autre parametre est reserve aux mots-cles ET optionnel, donc aucun
       ne peut etre fourni par accident ni omis par erreur.

    Formule ainsi, l'invariant tient quel que soit le nombre de coutures
    ajoutees, et il en dit davantage que l'egalite de liste qu'il remplace.
    """
    parametres = inspect.signature(build_runtime).parameters
    positionnels = [
        nom
        for nom, p in parametres.items()
        if p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]
    assert positionnels == ["config", "stop"]
    assert parametres["config"].default is inspect.Parameter.empty
    assert parametres["stop"].default is inspect.Parameter.empty
    for nom, p in parametres.items():
        if nom in ("config", "stop"):
            continue
        assert p.kind is inspect.Parameter.KEYWORD_ONLY, nom
        assert p.default is None, nom
    # La couture d'horloge de C9 est toujours la, inchangee.
    assert parametres["clock"].default is None
    assert parametres["clock"].kind is inspect.Parameter.KEYWORD_ONLY


@pytest.mark.reference
def test_build_runtime_injecte_l_horloge_fournie(monkeypatch) -> None:
    """Cible du lot C9 : l'horloge fournie est celle reellement cablee.

    Remplace la caracterisation qui constatait l'impossibilite de l'injection.
    """
    monkeypatch.setattr(
        PahoMqttClient, "_build_client", staticmethod(lambda config: _FauxPaho())
    )
    horloge = VirtualClock(datetime(2026, 8, 9, tzinfo=timezone.utc))
    runtime = build_runtime(_config_runtime(), NeverStop(), clock=horloge)
    assert runtime.runner._clock is horloge  # type: ignore[attr-defined]
    assert runtime.publisher._clock is horloge  # type: ignore[attr-defined]


@pytest.mark.reference
def test_build_runtime_partage_l_instance_injectee(monkeypatch) -> None:
    """L'invariant C8 tient aussi pour une horloge injectee : une seule instance."""
    monkeypatch.setattr(
        PahoMqttClient, "_build_client", staticmethod(lambda config: _FauxPaho())
    )
    horloge = VirtualClock(datetime(2026, 8, 9, tzinfo=timezone.utc))
    runtime = build_runtime(_config_runtime(), NeverStop(), clock=horloge)
    assert runtime.runner._clock is runtime.publisher._clock  # type: ignore[attr-defined]


@pytest.mark.reference
def test_build_runtime_conserve_son_defaut_historique(monkeypatch) -> None:
    """Sans injection, rien ne change : une `SystemClock` neuve, partagee."""
    monkeypatch.setattr(
        PahoMqttClient, "_build_client", staticmethod(lambda config: _FauxPaho())
    )
    runtime = build_runtime(_config_runtime(), NeverStop())
    assert isinstance(runtime.runner._clock, SystemClock)  # type: ignore[attr-defined]
    assert runtime.runner._clock is runtime.publisher._clock  # type: ignore[attr-defined]


@pytest.mark.reference
def test_le_runner_accepte_deja_n_importe_quelle_horloge() -> None:
    """`ReadSurfaceRunner` prenait deja une `Clock`, et cela n'a pas change.

    REVISE PAR W3. L'assertion d'origine figeait la liste exacte des parametres
    pour montrer que la couture C9 se limitait a `build_runtime`. W3 ajoute au
    runner une voie transactionnelle OPTIONNELLE, ce que W2 §13.3 exige.

    Ce qui doit rester vrai, et qui est desormais affirme explicitement :

    1. les trois premiers parametres sont inchanges, dans le meme ordre ;
    2. `clock` porte toujours l'annotation `Clock` — la couture C9 est intacte ;
    3. tout parametre AJOUTE est **reserve aux mots-cles** et vaut `None` par
       defaut, donc un runner construit comme avant se comporte exactement comme
       avant, et aucune dependance ajoutee ne peut etre fournie par position.
    """
    parametres = inspect.signature(ReadSurfaceRunner.__init__).parameters
    assert list(parametres)[:4] == ["self", "publisher", "clock", "stop"]
    assert parametres["clock"].annotation == "Clock"
    for nom in list(parametres)[4:]:
        assert parametres[nom].kind is inspect.Parameter.KEYWORD_ONLY, nom
        assert parametres[nom].default is None, nom


# ---------------------------------------------------------------------------
# G. Preuve OS reelle — POSIX uniquement
# ---------------------------------------------------------------------------

#: Programme enfant : il utilise les composants de PRODUCTION de C9, pas des
#: doubles. Aucun broker, aucun `vclient`, aucun reseau, aucune chaudiere ; seul
#: un interpreteur Python de test est lance.
_ENFANT = """
import sys, time
sys.path.insert(0, %r)
import signal
from boilerack.lifecycle import SignalScope, resultat_logique

with SignalScope() as wakeup:
    print('READY', flush=True)
    debut = time.monotonic()
    wakeup.clock.sleep(60.0)
    ecoule = time.monotonic() - debut
    arme = wakeup.stop.is_set()
    cause = wakeup.stop.cause
    code = resultat_logique(cause)
print('WOKE %%s %%.4f %%s %%s' %% (arme, ecoule, int(cause) if cause else -1, code),
      flush=True)
sys.exit(0 if arme else 3)
"""


def _lignes_du_processus(proc) -> queue.Queue:
    fifo: queue.Queue = queue.Queue()

    def lire() -> None:
        for ligne in proc.stdout:  # type: ignore[union-attr]
            fifo.put(ligne.strip())
        fifo.put(None)

    threading.Thread(target=lire, daemon=True).start()
    return fifo


@pytest.mark.skipif(not POSIX, reason="SIGTERM n'est pas delivrable ainsi hors POSIX")
@pytest.mark.reference
def test_sigterm_reveille_une_attente_dans_un_vrai_processus() -> None:
    """Preuve reelle de la couture OS -> niveau C -> descripteur -> reveil.

    Exerce les composants de **production** de C9 — `SignalScope`, `WakeupClock`,
    `SignalStop`, `resultat_logique` — dans un vrai processus recevant un vrai
    `SIGTERM`.

    Ne prouve pas Boilerack en production : aucun broker, aucun `vclient`,
    aucun reseau. Seul un interpreteur Python de test est lance.

    Le delai est mesure a titre **informatif** ; la propriete verifiee est
    fonctionnelle : l'attente de 60 s est interrompue bien avant son echeance.
    Les bornes utilisees ici sont des garde-fous de test, pas des promesses.
    """
    racine_src = str(pathlib.Path(boilerack.lifecycle.__file__).parents[2])
    proc = subprocess.Popen(
        [sys.executable, "-u", "-c", _ENFANT % racine_src],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        fifo = _lignes_du_processus(proc)
        assert fifo.get(timeout=30) == "READY", "l'enfant n'a pas signale sa disponibilite"

        envoi = time.monotonic()
        proc.send_signal(signal.SIGTERM)

        ligne = fifo.get(timeout=30)
        aller_retour = time.monotonic() - envoi
        code = proc.wait(timeout=30)
    finally:
        if proc.poll() is None:  # pragma: no cover - filet de securite
            proc.kill()
            proc.wait(timeout=30)

    marqueur, arme, mesure_enfant, cause, resultat = ligne.split()
    assert marqueur == "WOKE"
    assert arme == "True", "l'attente n'a pas ete reveillee par SIGTERM"
    assert int(cause) == int(signal.SIGTERM)
    assert int(resultat) == CODE_ARRET_NORMAL, "SIGTERM doit rendre 0"
    assert code == 0
    # Propriete FONCTIONNELLE : interrompue avant l'echeance de 60 s.
    assert float(mesure_enfant) < 30.0
    assert aller_retour < 30.0
    print(
        f"\n  latence de reveil mesuree (informative) : "
        f"enfant={float(mesure_enfant) * 1000:.1f} ms, "
        f"aller-retour={aller_retour * 1000:.1f} ms"
    )


@pytest.mark.skipif(POSIX, reason="ce constat ne concerne que les plateformes non POSIX")
@pytest.mark.unknown
def test_hors_posix_la_preuve_sigterm_n_est_pas_realisable() -> None:
    """Rend le saut de plateforme visible et verifiable, plutot que silencieux.

    Sur Windows, `SIGTERM` n'est pas delivre a un fil principal bloque dans une
    attente : le gestionnaire n'y est pas execute. La preuve de la section G ne
    peut donc etre faite qu'en integration continue, sur Linux. Aucune preuve
    n'est simulee ici.
    """
    assert os.name != "posix"
    assert hasattr(signal, "SIGTERM"), "la constante existe, la semantique differe"


# ---------------------------------------------------------------------------
# H. Reveil par descripteur — `signal.set_wakeup_fd`
# ---------------------------------------------------------------------------


@pytest.fixture
def reveil():
    """Paire de sockets locales + wakeup fd + gestionnaires, tout restaure.

    Restaure l'etat global et ferme les descripteurs **meme si le test echoue** :
    aucun descripteur residuel, aucun gestionnaire laisse en place, aucun wakeup
    fd oublie.
    """
    numeros = [signal.SIGINT, signal.SIGTERM]
    anciens = {n: signal.getsignal(n) for n in numeros}
    ecriture, lecture = socket.socketpair()
    ecriture.setblocking(False)
    lecture.setblocking(False)
    ancien_fd = signal.set_wakeup_fd(ecriture.fileno())
    for n in numeros:
        # Gestionnaire VIDE : il n'acquiert aucun verrou et ne touche a rien.
        signal.signal(n, lambda numero, cadre: None)
    try:
        yield lecture
    finally:
        signal.set_wakeup_fd(ancien_fd)
        for n, ancien in anciens.items():
            signal.signal(n, ancien)
        ecriture.close()
        lecture.close()


def _draine(lecture: socket.socket) -> list[int]:
    try:
        return list(lecture.recv(4096))
    except BlockingIOError:
        return []


@pytest.mark.reference
def test_set_wakeup_fd_exige_le_fil_principal() -> None:
    """Meme contrainte que `signal.signal` : aucune contrainte nouvelle."""
    resultat: dict[str, str] = {}

    def dans_un_fil() -> None:
        a, b = socket.socketpair()
        a.setblocking(False)
        try:
            signal.set_wakeup_fd(a.fileno())
            signal.set_wakeup_fd(-1)
            resultat["issue"] = "accepte"
        except Exception as exc:
            resultat["issue"] = type(exc).__name__
            resultat["message"] = str(exc)
        finally:
            a.close()
            b.close()

    fil = threading.Thread(target=dans_un_fil)
    fil.start()
    fil.join(timeout=10)
    assert resultat["issue"] == "ValueError"
    assert "main thread" in resultat["message"]


@pytest.mark.reference
def test_set_wakeup_fd_rend_le_descripteur_precedent(reveil) -> None:
    """C'est cette valeur de retour qui permet une restauration exacte."""
    a, b = socket.socketpair()
    a.setblocking(False)
    try:
        precedent = signal.set_wakeup_fd(a.fileno())
        assert precedent >= 0, "le fd installe par la fixture doit etre rendu"
        rendu = signal.set_wakeup_fd(precedent)
        assert rendu == a.fileno()
    finally:
        a.close()
        b.close()


@pytest.mark.reference
def test_l_octet_ecrit_est_le_numero_du_signal(reveil) -> None:
    signal.raise_signal(signal.SIGINT)
    assert _draine(reveil) == [int(signal.SIGINT)]
    signal.raise_signal(signal.SIGTERM)
    assert _draine(reveil) == [int(signal.SIGTERM)]


@pytest.mark.reference
def test_un_gestionnaire_python_est_indispensable_a_l_ecriture(reveil) -> None:
    """`SIG_IGN` n'ecrit rien : le gestionnaire vide n'est pas decoratif.

    C'est le niveau C de CPython qui ecrit l'octet, et il n'est installe que si
    un gestionnaire Python existe pour ce signal.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.raise_signal(signal.SIGINT)
    assert _draine(reveil) == []

    signal.signal(signal.SIGINT, lambda numero, cadre: None)
    signal.raise_signal(signal.SIGINT)
    assert _draine(reveil) == [int(signal.SIGINT)]


@pytest.mark.reference
def test_le_gestionnaire_n_a_rien_a_faire_pour_que_l_octet_soit_ecrit(reveil) -> None:
    """Le point qui elimine toute reentrance : le gestionnaire ne touche a rien."""
    executions: list[int] = []
    signal.signal(signal.SIGINT, lambda numero, cadre: executions.append(numero))
    signal.raise_signal(signal.SIGINT)
    assert _draine(reveil) == [int(signal.SIGINT)]
    assert executions == [int(signal.SIGINT)]


@pytest.mark.reference
@pytest.mark.parametrize(
    ("premier", "second"),
    [(signal.SIGINT, signal.SIGTERM), (signal.SIGTERM, signal.SIGINT)],
)
def test_l_ordre_des_octets_donne_la_premiere_cause(reveil, premier, second) -> None:
    """« Premiere cause consommee = cause conservee », sans priorite inventee."""
    signal.raise_signal(premier)
    signal.raise_signal(second)
    octets = _draine(reveil)
    assert octets[0] == int(premier)
    assert sorted(octets) == sorted([int(premier), int(second)])


@pytest.mark.reference
def test_le_descripteur_reste_lisible_jusqu_au_drainage(reveil) -> None:
    """Le signal est MEMORISE : c'est ce qui permet de ne pas tronquer un cycle."""
    signal.raise_signal(signal.SIGTERM)
    selecteur = selectors.DefaultSelector()
    selecteur.register(reveil, selectors.EVENT_READ)
    try:
        debut = time.monotonic()
        prets = selecteur.select(timeout=30.0)
        ecoule = time.monotonic() - debut
    finally:
        selecteur.close()
    assert prets, "le descripteur aurait du etre deja lisible"
    assert ecoule < 5.0, "l'attente n'a pas rendu la main immediatement"
    assert _draine(reveil) == [int(signal.SIGTERM)]


@pytest.mark.reference
def test_un_signal_ecourte_une_attente_sur_selecteur(reveil) -> None:
    """Le maillon complet OS -> niveau C -> descripteur -> reveil, en processus."""
    selecteur = selectors.DefaultSelector()
    selecteur.register(reveil, selectors.EVENT_READ)
    minuterie = threading.Timer(0.10, lambda: signal.raise_signal(signal.SIGINT))
    minuterie.start()
    try:
        debut = time.monotonic()
        prets = selecteur.select(timeout=30.0)
        ecoule = time.monotonic() - debut
    finally:
        minuterie.cancel()
        selecteur.close()
    assert prets
    assert ecoule < 5.0
    assert _draine(reveil) == [int(signal.SIGINT)]


@pytest.mark.reference
def test_la_saturation_ne_leve_jamais_et_ne_perd_jamais_le_reveil(reveil) -> None:
    """Beaucoup de signaux sans consommation : aucune exception cote emetteur.

    En cas de tampon plein, CPython ABANDONNE les octets excedentaires. La
    consequence est benigne ici : le descripteur reste lisible tant qu'un seul
    octet subsiste, donc le reveil n'est jamais perdu ; seules des causes
    surnumeraires le seraient, et la politique de C9 ne retient que la premiere.
    """
    for _ in range(5000):
        signal.raise_signal(signal.SIGINT)
    octets = _draine(reveil)
    assert octets, "le descripteur doit rester lisible"
    assert set(octets) == {int(signal.SIGINT)}


# ---------------------------------------------------------------------------
# I. Primitive de transport : tube ou paire de sockets
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_les_deux_transports_sont_acceptes_par_set_wakeup_fd() -> None:
    """`os.pipe` comme `socket.socketpair` sont acceptes : le tri se fait ailleurs."""
    ancien_sigint = signal.getsignal(signal.SIGINT)
    lecture_p, ecriture_p = os.pipe()
    a, b = socket.socketpair()
    try:
        os.set_blocking(ecriture_p, False)
        a.setblocking(False)
        signal.signal(signal.SIGINT, lambda numero, cadre: None)
        for descripteur in (ecriture_p, a.fileno()):
            precedent = signal.set_wakeup_fd(descripteur)
            signal.set_wakeup_fd(precedent)
    finally:
        signal.set_wakeup_fd(-1)
        signal.signal(signal.SIGINT, ancien_sigint)
        os.close(lecture_p)
        os.close(ecriture_p)
        a.close()
        b.close()


@pytest.mark.skipif(POSIX, reason="constat propre aux plateformes non POSIX")
@pytest.mark.reference
def test_hors_posix_un_tube_n_est_pas_selectionnable() -> None:
    """Ce qui elimine `os.pipe` comme transport portable.

    Le descripteur est enregistrable sans erreur, mais l'attente elle-meme
    echoue : hors POSIX, `select` ne connait que les sockets. Une paire de
    sockets locales est donc le seul transport valable sur les deux familles.
    """
    lecture, ecriture = os.pipe()
    os.set_blocking(lecture, False)
    selecteur = selectors.DefaultSelector()
    try:
        selecteur.register(lecture, selectors.EVENT_READ)
        with pytest.raises(OSError):
            selecteur.select(timeout=0.2)
    finally:
        selecteur.close()
        os.close(lecture)
        os.close(ecriture)


@pytest.mark.skipif(not POSIX, reason="un tube n'est selectionnable que sous POSIX")
@pytest.mark.reference
def test_sous_posix_un_tube_est_selectionnable() -> None:
    lecture, ecriture = os.pipe()
    os.set_blocking(lecture, False)
    selecteur = selectors.DefaultSelector()
    try:
        selecteur.register(lecture, selectors.EVENT_READ)
        assert selecteur.select(timeout=0.05) == []
        os.write(ecriture, b"\x02")
        assert selecteur.select(timeout=5.0)
        assert os.read(lecture, 16) == b"\x02"
    finally:
        selecteur.close()
        os.close(lecture)
        os.close(ecriture)


@pytest.mark.reference
def test_une_paire_de_sockets_locales_est_selectionnable() -> None:
    """Aucune connexion reseau : deux extremites locales, jamais publiees."""
    a, b = socket.socketpair()
    selecteur = selectors.DefaultSelector()
    try:
        a.setblocking(False)
        b.setblocking(False)
        selecteur.register(b, selectors.EVENT_READ)
        assert selecteur.select(timeout=0.05) == []
        a.send(b"\x02")
        assert selecteur.select(timeout=5.0), "la paire de sockets n'a pas reveille"
        assert b.recv(16) == b"\x02"
    finally:
        selecteur.close()
        a.close()
        b.close()


# ---------------------------------------------------------------------------
# J. La couture par descripteur, confrontee au runner C8 REEL
# ---------------------------------------------------------------------------


class _EtatArretParDescripteur:
    """Specimen de caracterisation, PAS le futur code de production.

    `is_set()` **draine** le descripteur avant de repondre : le maillon complet
    reste ainsi observable meme lorsque `sleep()` n'est pas appele — voir le
    test de l'echeance deja passee.
    """

    def __init__(self, lecture: socket.socket, draine_dans_is_set: bool = True) -> None:
        self._lecture = lecture
        self._draine_dans_is_set = draine_dans_is_set
        self.arme = False
        self.cause: int | None = None

    def drainer(self) -> None:
        for octet in _draine(self._lecture):
            self.arme = True
            if self.cause is None:
                self.cause = octet

    def is_set(self) -> bool:
        if self._draine_dans_is_set:
            self.drainer()
        return self.arme


class _HorlogeParDescripteur:
    """Specimen de caracterisation. Satisfait `Clock`, attend sur le descripteur."""

    def __init__(self, etat: _EtatArretParDescripteur, lecture: socket.socket) -> None:
        self._etat = etat
        self._selecteur = selectors.DefaultSelector()
        self._selecteur.register(lecture, selectors.EVENT_READ)
        self.attentes: list[float] = []

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        duree = check_duration(seconds, op="sleep()")
        self.attentes.append(duree)
        if self._selecteur.select(timeout=duree):
            self._etat.drainer()

    def close(self) -> None:
        self._selecteur.close()


class _PublieurSignalant:
    """Publieur factice qui se signale a lui-meme au milieu du premier cycle."""

    def __init__(self, echeances: list[float], numero: int | None) -> None:
        self.appels: list[str] = []
        self.started = False
        self.cycles = 0
        self._echeances = echeances
        self._numero = numero

    def start(self) -> None:
        self.appels.append("start")
        self.started = True

    def stop(self) -> None:
        self.appels.append("stop")
        self.started = False

    def due_at(self) -> float:
        self.appels.append("due_at")
        indice = min(len(self._echeances) - 1, self.appels.count("due_at") - 1)
        return time.monotonic() + self._echeances[indice]

    def run_due(self) -> None:
        self.appels.append("run_due:debut")
        if self._numero is not None and self.cycles == 0:
            signal.raise_signal(self._numero)
        self.cycles += 1
        self.appels.append("run_due:fin")


def _executer(lecture, echeances, numero, draine_dans_is_set):
    etat = _EtatArretParDescripteur(lecture, draine_dans_is_set)
    horloge = _HorlogeParDescripteur(etat, lecture)
    publieur = _PublieurSignalant(echeances, numero)
    try:
        ReadSurfaceRunner(publisher=publieur, clock=horloge, stop=etat).run()
    finally:
        horloge.close()
    return publieur, etat


@pytest.mark.reference
def test_un_signal_pendant_run_due_ne_tronque_pas_le_cycle(reveil) -> None:
    """Invariant C8 preserve : le cycle engage va jusqu'a son terme.

    Le signal survient au milieu de `run_due()` ; le gestionnaire vide n'y
    touche pas ; l'octet est memorise ; le cycle s'acheve ; l'arret est vu au
    point de controle suivant, sans cycle superflu.
    """
    publieur, etat = _executer(reveil, [0.0, 30.0], int(signal.SIGINT), True)
    assert publieur.appels == [
        "start",
        "due_at",
        "run_due:debut",
        "run_due:fin",
        "stop",
    ]
    assert publieur.cycles == 1
    assert etat.arme is True
    assert etat.cause == int(signal.SIGINT)
    assert publieur.started is False


@pytest.mark.reference
def test_le_drainage_dans_is_set_evite_des_cycles_superflus(reveil) -> None:
    """Pourquoi `is_set()` doit drainer : le cas de l'echeance deja passee.

    Quand l'echeance suivante est deja depassee, C8 n'appelle pas `sleep()` —
    c'est son comportement, correct et deja teste. Si seul `sleep()` drainait,
    l'arret ne serait pas vu et des cycles supplementaires s'executeraient.
    Mesure ici : trois cycles au lieu d'un seul.
    """
    echeances = [0.0, -1.0, -1.0, 30.0]
    avec, etat_avec = _executer(reveil, echeances, int(signal.SIGINT), True)
    assert avec.cycles == 1
    assert etat_avec.cause == int(signal.SIGINT)

    signal.raise_signal(signal.SIGTERM)  # rearme le descripteur pour la variante
    sans, etat_sans = _executer(reveil, echeances, None, False)
    assert sans.cycles == 3, "la variante sans drainage doit executer des cycles superflus"
    assert etat_sans.arme is True


@pytest.mark.reference
def test_aucun_verrou_n_est_pris_dans_le_chemin_de_signal(reveil) -> None:
    """La propriete qui distingue cette architecture : le gestionnaire ne fait rien.

    Il n'appelle ni `set()`, ni aucune primitive de synchronisation : la course
    de reentrance reproduite plus haut est structurellement impossible.
    """
    gestionnaire = signal.getsignal(signal.SIGINT)
    source = inspect.getsource(gestionnaire)
    assert "lambda numero, cadre: None" in source
    signal.raise_signal(signal.SIGINT)
    assert _draine(reveil) == [int(signal.SIGINT)]


# ---------------------------------------------------------------------------
# K. `SignalStop` — etat d'arret de production
# ---------------------------------------------------------------------------


@pytest.fixture
def portee():
    """Ouvre une vraie `SignalScope` et garantit sa fermeture.

    Verifie en sortie que rien n'a fuite : gestionnaires restaures, descripteur
    de reveil restaure. La portee est responsable de tout le reste.
    """
    anciens = {n: signal.getsignal(n) for n in SIGNALS_SURVEILLES}
    ancien_fd = signal.set_wakeup_fd(-1)
    signal.set_wakeup_fd(ancien_fd)
    scope = SignalScope()
    with scope as wakeup:
        yield wakeup
    assert all(signal.getsignal(n) is anciens[n] for n in SIGNALS_SURVEILLES)
    courant = signal.set_wakeup_fd(-1)
    signal.set_wakeup_fd(courant)
    assert courant == ancien_fd


@pytest.mark.reference
def test_stop_initialement_faux(portee) -> None:
    assert portee.stop.is_set() is False
    assert portee.stop.cause is None


@pytest.mark.reference
def test_stop_arme_apres_drainage_d_un_signal(portee) -> None:
    signal.raise_signal(signal.SIGTERM)
    assert portee.stop.is_set() is True
    assert portee.stop.cause is signal.SIGTERM


@pytest.mark.reference
@pytest.mark.parametrize(
    ("premier", "second"),
    [(signal.SIGINT, signal.SIGTERM), (signal.SIGTERM, signal.SIGINT)],
)
def test_stop_conserve_la_premiere_cause(portee, premier, second) -> None:
    """Aucune priorite, aucune escalade : l'ordre d'arrivee decide."""
    signal.raise_signal(premier)
    signal.raise_signal(second)
    assert portee.stop.is_set() is True
    assert portee.stop.cause == premier


@pytest.mark.reference
def test_stop_un_signal_ulterieur_ne_remplace_pas_la_cause(portee) -> None:
    signal.raise_signal(signal.SIGTERM)
    assert portee.stop.is_set() is True
    signal.raise_signal(signal.SIGINT)
    assert portee.stop.is_set() is True
    assert portee.stop.cause is signal.SIGTERM


@pytest.mark.reference
def test_stop_draine_sans_aucun_sleep(portee) -> None:
    """Le point qui evite les cycles superflus : `is_set()` suffit."""
    signal.raise_signal(signal.SIGINT)
    assert portee.stop.is_set() is True  # aucun sleep() n'a eu lieu


@pytest.mark.reference
def test_stop_est_idempotent_sur_plusieurs_interrogations(portee) -> None:
    signal.raise_signal(signal.SIGINT)
    premier = portee.stop.is_set()
    assert premier is portee.stop.is_set() is True
    assert portee.stop.cause is signal.SIGINT


@pytest.mark.reference
def test_stop_ignore_un_signal_non_surveille() -> None:
    """`set_wakeup_fd` est global : un signal de l'hote ne doit pas armer C9.

    Le comportement retenu — drainer sans armer — est explicite, et non un
    effet de bord silencieux.
    """
    emetteur, recepteur = socket.socketpair()
    try:
        emetteur.setblocking(False)
        recepteur.setblocking(False)
        stop = SignalStop(recepteur, (signal.SIGINT, signal.SIGTERM))
        emetteur.send(bytes([99, int(signal.SIGTERM)]))
        assert stop.is_set() is True
        assert stop.cause is signal.SIGTERM
        assert stop.signaux_ignores == (99,)
    finally:
        emetteur.close()
        recepteur.close()


@pytest.mark.reference
def test_stop_reste_faux_si_seuls_des_signaux_etrangers_arrivent() -> None:
    emetteur, recepteur = socket.socketpair()
    try:
        emetteur.setblocking(False)
        recepteur.setblocking(False)
        stop = SignalStop(recepteur, (signal.SIGINT,))
        emetteur.send(bytes([int(signal.SIGTERM), 99]))
        assert stop.is_set() is False
        assert stop.cause is None
        assert stop.signaux_ignores == (int(signal.SIGTERM), 99)
    finally:
        emetteur.close()
        recepteur.close()


@pytest.mark.reference
def test_stop_satisfait_le_protocole_attendu_par_c8(portee) -> None:
    assert isinstance(portee.stop.is_set(), bool)
    with pytest.raises(TypeError, match="runtime_checkable"):
        isinstance(portee.stop, StopSignal)  # noqa: B015


# ---------------------------------------------------------------------------
# L. `WakeupClock` — attente interruptible de production
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_horloge_satisfait_le_protocole_clock(portee) -> None:
    assert isinstance(portee.clock, Clock)
    assert isinstance(portee.clock.now(), datetime)
    assert portee.clock.now().tzinfo is not None
    assert isinstance(portee.clock.monotonic(), float)


@pytest.mark.reference
def test_horloge_delegue_le_temps_a_une_horloge_de_base() -> None:
    """`now()` et `monotonic()` ne reinventent rien : ils delegent."""
    emetteur, recepteur = socket.socketpair()
    base = VirtualClock(datetime(2026, 8, 9, 12, tzinfo=timezone.utc), monotonic_start=500.0)
    try:
        recepteur.setblocking(False)
        horloge = WakeupClock(SignalStop(recepteur), recepteur, base=base)
        try:
            assert horloge.now() == base.now()
            assert horloge.monotonic() == 500.0
        finally:
            horloge.close()
    finally:
        emetteur.close()
        recepteur.close()


@pytest.mark.reference
def test_horloge_attend_la_duree_demandee_sans_signal(portee) -> None:
    debut = time.monotonic()
    assert portee.clock.sleep(0.30) is None
    assert time.monotonic() - debut >= 0.30 - _TOLERANCE_HORLOGE_S


@pytest.mark.reference
def test_horloge_est_ecourtee_par_un_signal(portee) -> None:
    minuterie = threading.Timer(0.10, lambda: signal.raise_signal(signal.SIGTERM))
    minuterie.start()
    try:
        debut = time.monotonic()
        portee.clock.sleep(30.0)
        ecoule = time.monotonic() - debut
    finally:
        minuterie.cancel()
    assert ecoule < 5.0, "l'attente n'a pas ete ecourtee"
    assert portee.stop.cause is signal.SIGTERM


@pytest.mark.reference
def test_horloge_draine_pendant_l_attente(portee) -> None:
    """Apres reveil, l'etat est deja arme : C8 le verra a sa reconsultation."""
    minuterie = threading.Timer(0.10, lambda: signal.raise_signal(signal.SIGINT))
    minuterie.start()
    try:
        portee.clock.sleep(30.0)
    finally:
        minuterie.cancel()
    assert portee.stop.cause is signal.SIGINT


@pytest.mark.reference
def test_horloge_rend_la_main_immediatement_si_le_signal_precede_l_attente(portee) -> None:
    signal.raise_signal(signal.SIGTERM)
    debut = time.monotonic()
    portee.clock.sleep(30.0)
    assert time.monotonic() - debut < 5.0
    assert portee.stop.cause is signal.SIGTERM


@pytest.mark.reference
def test_horloge_n_effectue_aucune_scrutation(portee) -> None:
    cpu_avant = time.process_time()
    mur_avant = time.monotonic()
    portee.clock.sleep(0.50)
    cpu = time.process_time() - cpu_avant
    mur = time.monotonic() - mur_avant
    assert mur >= 0.50 - _TOLERANCE_HORLOGE_S
    assert cpu < 0.10, f"attente non passive : {cpu:.3f}s de CPU pour {mur:.3f}s"


@pytest.mark.reference
@pytest.mark.parametrize("invalide", [-1.0, float("nan"), float("inf")])
def test_horloge_refuse_les_memes_durees_que_les_autres(portee, invalide) -> None:
    with pytest.raises(ValueError):
        portee.clock.sleep(invalide)
    with pytest.raises(ValueError):
        SystemClock().sleep(invalide)


# ---------------------------------------------------------------------------
# M. `SignalScope` — installation, restauration, hygiene
# ---------------------------------------------------------------------------


def _etat_global() -> tuple[dict, int]:
    gestionnaires = {n: signal.getsignal(n) for n in SIGNALS_SURVEILLES}
    fd = signal.set_wakeup_fd(-1)
    signal.set_wakeup_fd(fd)
    return gestionnaires, fd


@pytest.mark.reference
def test_portee_installe_puis_restaure_exactement() -> None:
    avant_gestionnaires, avant_fd = _etat_global()
    with SignalScope() as wakeup:
        assert isinstance(wakeup, Wakeup)
        pendant_gestionnaires, pendant_fd = _etat_global()
        assert all(
            pendant_gestionnaires[n] is not avant_gestionnaires[n]
            for n in SIGNALS_SURVEILLES
        )
        assert pendant_fd != avant_fd
    apres_gestionnaires, apres_fd = _etat_global()
    assert all(apres_gestionnaires[n] is avant_gestionnaires[n] for n in SIGNALS_SURVEILLES)
    assert apres_fd == avant_fd


@pytest.mark.reference
def test_portee_restaure_meme_lorsque_le_corps_leve() -> None:
    avant_gestionnaires, avant_fd = _etat_global()
    with pytest.raises(RuntimeError, match="panne simulee"):
        with SignalScope():
            raise RuntimeError("panne simulee")
    apres_gestionnaires, apres_fd = _etat_global()
    assert all(apres_gestionnaires[n] is avant_gestionnaires[n] for n in SIGNALS_SURVEILLES)
    assert apres_fd == avant_fd


@pytest.mark.reference
def test_portee_ferme_les_deux_sockets() -> None:
    scope = SignalScope()
    with scope as wakeup:
        emetteur = scope._emetteur  # type: ignore[attr-defined]
        recepteur = scope._recepteur  # type: ignore[attr-defined]
        assert emetteur.fileno() >= 0
        assert recepteur.fileno() >= 0
        del wakeup
    assert emetteur.fileno() == -1, "socket emettrice non fermee"
    assert recepteur.fileno() == -1, "socket receptrice non fermee"


@pytest.mark.reference
def test_portee_ferme_les_sockets_meme_sur_exception() -> None:
    scope = SignalScope()
    with pytest.raises(RuntimeError):
        with scope:
            emetteur = scope._emetteur  # type: ignore[attr-defined]
            recepteur = scope._recepteur  # type: ignore[attr-defined]
            raise RuntimeError("panne simulee")
    assert emetteur.fileno() == -1
    assert recepteur.fileno() == -1


@pytest.mark.reference
def test_portee_pose_un_gestionnaire_vide() -> None:
    """Il doit exister — sinon aucun octet n'est ecrit — mais ne rien faire.

    Verifie sur l'AST, et non par recherche de texte : le corps du gestionnaire
    ne doit contenir **aucune instruction** hormis sa docstring. C'est la
    formulation qui resiste, la ou une recherche de sous-chaines se laisse
    contourner par la premiere ligne venue.
    """
    with SignalScope():
        gestionnaire = signal.getsignal(signal.SIGINT)
        assert callable(gestionnaire)
        arbre = ast.parse(textwrap.dedent(inspect.getsource(gestionnaire)))
        fonction = arbre.body[0]
        assert isinstance(fonction, ast.FunctionDef)
        instructions = [
            n for n in fonction.body
            if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                    and isinstance(n.value.value, str))
        ]
        assert instructions == [], (
            "le gestionnaire de signal doit rester vide : "
            + "; ".join(ast.unparse(n) for n in instructions)
        )


@pytest.mark.reference
def test_le_module_ne_definit_aucun_etat_mutable_global() -> None:
    """Verrou complementaire : rien au niveau module que le gestionnaire pourrait muter."""
    arbre = ast.parse(pathlib.Path(boilerack.lifecycle.__file__).read_text(encoding="utf-8"))
    for noeud in arbre.body:
        if not isinstance(noeud, (ast.Assign, ast.AnnAssign)) or noeud.value is None:
            continue
        cibles = (
            [noeud.target] if isinstance(noeud, ast.AnnAssign) else list(noeud.targets)
        )
        noms = {c.id for c in cibles if isinstance(c, ast.Name)}
        if noms == {"__all__"}:  # convention du langage, jamais mutee ici
            continue
        assert isinstance(noeud.value, (ast.Constant, ast.Tuple)), ast.unparse(noeud)


@pytest.mark.reference
def test_portee_refuse_le_hors_fil_principal() -> None:
    resultat: dict[str, str] = {}

    def dans_un_fil() -> None:
        try:
            with SignalScope():
                resultat["issue"] = "acceptee"
        except Exception as exc:
            resultat["issue"] = type(exc).__name__
            resultat["message"] = str(exc)

    fil = threading.Thread(target=dans_un_fil)
    fil.start()
    fil.join(timeout=10)
    assert resultat["issue"] == "RuntimeError"
    assert "fil principal" in resultat["message"]


@pytest.mark.reference
def test_portee_hors_fil_principal_n_alloue_rien() -> None:
    """Le refus survient AVANT toute allocation : rien a nettoyer."""
    avant = len([o for o in gc.get_objects() if isinstance(o, socket.socket)])

    def dans_un_fil() -> None:
        try:
            with SignalScope():
                pass
        except RuntimeError:
            pass

    fil = threading.Thread(target=dans_un_fil)
    fil.start()
    fil.join(timeout=10)
    gc.collect()
    assert len([o for o in gc.get_objects() if isinstance(o, socket.socket)]) == avant


@pytest.mark.reference
def test_portees_imbriquees_restaurent_dans_le_bon_ordre() -> None:
    """Une portee interne doit rendre exactement ce que l'externe avait pose."""
    avant_gestionnaires, avant_fd = _etat_global()
    with SignalScope():
        externe_gestionnaires, externe_fd = _etat_global()
        with SignalScope():
            interne_fd = _etat_global()[1]
            assert interne_fd != externe_fd
        rendu_gestionnaires, rendu_fd = _etat_global()
        assert rendu_fd == externe_fd
        assert all(
            rendu_gestionnaires[n] is externe_gestionnaires[n] for n in SIGNALS_SURVEILLES
        )
    apres_gestionnaires, apres_fd = _etat_global()
    assert apres_fd == avant_fd
    assert all(apres_gestionnaires[n] is avant_gestionnaires[n] for n in SIGNALS_SURVEILLES)


@pytest.mark.reference
def test_le_corps_et_la_restauration_en_echec_sont_groupes() -> None:
    """Politique alignee sur C8 : aucune erreur n'est perdue.

    La restauration est sabotee en rendant l'une de ses etapes defaillante.
    """
    scope = SignalScope()
    origine = OSError("panne du corps")
    with pytest.raises(ExceptionGroup) as capture:
        with scope:
            scope._retirer_descripteur = _lever_restauration  # type: ignore[assignment]
            raise origine
    assert len(capture.value.exceptions) == 2
    assert capture.value.exceptions[0] is origine
    assert isinstance(capture.value.exceptions[1], RuntimeError)
    signal.set_wakeup_fd(-1)  # nettoyage : la restauration a ete sabotee


def _lever_restauration() -> None:
    raise RuntimeError("restauration impossible")


@pytest.mark.reference
def test_une_restauration_en_echec_seule_remonte_telle_quelle() -> None:
    scope = SignalScope()
    with pytest.raises(RuntimeError, match="restauration impossible") as capture:
        with scope:
            scope._retirer_descripteur = _lever_restauration  # type: ignore[assignment]
    assert not isinstance(capture.value, ExceptionGroup)
    signal.set_wakeup_fd(-1)


# ---------------------------------------------------------------------------
# N. `run_lifecycle` — resultat logique et politique d'exceptions
# ---------------------------------------------------------------------------


class _RunnerFactice:
    """Remplace `runtime.runner` : ne demarre rien, ne publie rien."""

    def __init__(self, action=None) -> None:
        self.appels: list[str] = []
        self._action = action

    def run(self) -> None:
        self.appels.append("run")
        if self._action is not None:
            self._action()


def _monter_runtime(monkeypatch, action=None) -> _RunnerFactice:
    """Fait rendre a `build_runtime` un `Runtime` dont le runner est factice."""
    runner = _RunnerFactice(action)
    vrai = boilerack.lifecycle.build_runtime

    def faux(config, stop, *, clock=None, transaction_factory=None):
        assert clock is not None, "l'horloge C9 doit etre injectee"
        assert hasattr(stop, "is_set")
        # W4-E2 : la fabrique est RELEVEE, jamais appliquee ici. Ces tests C9
        # portent sur le cycle de vie, pas sur la composition — et la relever
        # permet de prouver qu'elle vaut `None` quand l'autorite est fermee.
        faux.vu = (config, stop, clock)  # type: ignore[attr-defined]
        faux.fabrique = transaction_factory  # type: ignore[attr-defined]
        return SimpleNamespace(publisher=None, runner=runner, transaction=None)

    monkeypatch.setattr(boilerack.lifecycle, "build_runtime", faux)
    assert vrai is not faux
    return runner


@pytest.mark.reference
def test_retour_normal_sans_signal_rend_zero(monkeypatch) -> None:
    _monter_runtime(monkeypatch)
    assert run_lifecycle(_config_runtime()) == CODE_ARRET_NORMAL


@pytest.mark.reference
def test_sigterm_puis_arret_propre_rend_zero(monkeypatch) -> None:
    """`0`, et pour la bonne raison : la cause doit bien etre `SIGTERM`.

    Sans cette seconde assertion, le test passerait aussi avec une cause jamais
    lue — c'est exactement le defaut qu'a revele le cas `SIGINT`.
    """
    _monter_runtime(monkeypatch, action=lambda: signal.raise_signal(signal.SIGTERM))
    assert run_lifecycle(_config_runtime()) == CODE_ARRET_NORMAL
    _, stop, _ = boilerack.lifecycle.build_runtime.vu  # type: ignore[attr-defined]
    assert stop.cause is signal.SIGTERM


@pytest.mark.reference
def test_sigint_puis_arret_propre_rend_130(monkeypatch) -> None:
    """Ctrl-C ne leve plus `KeyboardInterrupt` : il devient un arret propre."""
    _monter_runtime(monkeypatch, action=lambda: signal.raise_signal(signal.SIGINT))
    assert run_lifecycle(_config_runtime()) == CODE_INTERRUPTION
    _, stop, _ = boilerack.lifecycle.build_runtime.vu  # type: ignore[attr-defined]
    assert stop.cause is signal.SIGINT


@pytest.mark.reference
def test_le_drainage_ultime_rattrape_un_signal_tardif(monkeypatch) -> None:
    """Un signal recu apres le dernier point de controle du runner compte aussi.

    Le runner factice n'interroge jamais `is_set()` : seul le drainage final de
    `run_lifecycle` peut voir la cause. C'est le defaut qu'a revele ce test.
    """
    _monter_runtime(monkeypatch, action=lambda: signal.raise_signal(signal.SIGINT))
    assert run_lifecycle(_config_runtime()) == CODE_INTERRUPTION


@pytest.mark.reference
def test_sigint_ne_leve_plus_keyboard_interrupt(monkeypatch) -> None:
    _monter_runtime(monkeypatch, action=lambda: signal.raise_signal(signal.SIGINT))
    try:
        code = run_lifecycle(_config_runtime())
    except KeyboardInterrupt:  # pragma: no cover - regression
        pytest.fail("KeyboardInterrupt levee : le chemin brutal est revenu")
    assert code == CODE_INTERRUPTION


@pytest.mark.reference
def test_une_panne_traverse_avec_son_identite(monkeypatch) -> None:
    """Aucune conversion en resultat logique : une panne reste une panne."""
    origine = OSError("publication impossible")

    def lever() -> None:
        raise origine

    _monter_runtime(monkeypatch, action=lever)
    with pytest.raises(OSError) as capture:
        run_lifecycle(_config_runtime())
    assert capture.value is origine


@pytest.mark.reference
def test_un_exception_group_c8_traverse_inchange(monkeypatch) -> None:
    groupe = ExceptionGroup(
        "echec de la boucle, puis de l'arret", [OSError("a"), RuntimeError("b")]
    )

    def lever() -> None:
        raise groupe

    _monter_runtime(monkeypatch, action=lever)
    with pytest.raises(ExceptionGroup) as capture:
        run_lifecycle(_config_runtime())
    assert capture.value is groupe
    assert [type(e).__name__ for e in capture.value.exceptions] == ["OSError", "RuntimeError"]


@pytest.mark.reference
def test_une_panne_n_empeche_pas_la_restauration(monkeypatch) -> None:
    avant_gestionnaires, avant_fd = _etat_global()

    def lever() -> None:
        raise OSError("panne")

    _monter_runtime(monkeypatch, action=lever)
    with pytest.raises(OSError):
        run_lifecycle(_config_runtime())
    apres_gestionnaires, apres_fd = _etat_global()
    assert apres_fd == avant_fd
    assert all(apres_gestionnaires[n] is avant_gestionnaires[n] for n in SIGNALS_SURVEILLES)


@pytest.mark.reference
def test_le_cycle_de_vie_injecte_bien_l_etat_et_l_horloge_c9(monkeypatch) -> None:
    runner = _monter_runtime(monkeypatch)
    run_lifecycle(_config_runtime())
    config, stop, clock = boilerack.lifecycle.build_runtime.vu  # type: ignore[attr-defined]
    assert isinstance(stop, SignalStop)
    assert isinstance(clock, WakeupClock)
    assert runner.appels == ["run"]


@pytest.mark.reference
def test_le_cycle_de_vie_ne_transmet_aucune_fabrique_si_l_autorite_est_fermee(
    monkeypatch,
) -> None:
    """La COUTURE elle-meme est eprouvee, pas seulement ses deux extremites.

    POURQUOI CE TEST EXISTE
        `_composer_transaction` rend bien `None` sur autorite fermee, et
        `build_runtime` compose bien ce qu'on lui donne : ces deux faits ont
        leurs propres preuves. Ils ne disent RIEN du fil qui les relie. Retirer
        l'argument `transaction_factory=` de l'appel reel laissait toute la suite
        verte — la voie devenait alors morte en production sans qu'aucune
        barriere ne bouge.

        Ce test porte donc sur l'ARGUMENT REELLEMENT TRANSMIS par `run_lifecycle`
        a `build_runtime`, releve par le double de `_monter_runtime`.
    """
    _monter_runtime(monkeypatch)
    run_lifecycle(_config_runtime())
    assert boilerack.lifecycle.build_runtime.fabrique is None  # type: ignore[attr-defined]


@pytest.mark.reference
def test_le_cycle_de_vie_transmet_une_fabrique_si_l_autorite_est_ouverte(
    monkeypatch,
) -> None:
    """Le pendant du precedent : ouverte, l'autorite fait circuler la fabrique.

    Les deux sont indispensables. Le cas ferme seul serait satisfait par une
    couture supprimee — `None` y est justement la valeur attendue. C'est le cas
    OUVERT qui rougit lorsque l'argument disparait de l'appel.

    Le double RELEVE la fabrique sans jamais l'appliquer : rien n'est compose
    ici, aucun `vclient` n'est construit, aucun processus n'est lance.
    """
    _monter_runtime(monkeypatch)
    run_lifecycle(_config_runtime(transactionnelle=True))
    fabrique = boilerack.lifecycle.build_runtime.fabrique  # type: ignore[attr-defined]
    assert fabrique is not None, "la couture lifecycle -> build_runtime est rompue"
    assert callable(fabrique)


@pytest.mark.reference
def test_resultat_logique_ne_connait_que_deux_valeurs() -> None:
    assert resultat_logique(None) == CODE_ARRET_NORMAL
    assert resultat_logique(signal.SIGTERM) == CODE_ARRET_NORMAL
    assert resultat_logique(signal.SIGINT) == CODE_INTERRUPTION


# ---------------------------------------------------------------------------
# O. Signal pendant `run_due()`, avec les composants de production
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_signal_pendant_run_due_avec_les_composants_de_production(portee) -> None:
    """Le cycle engage n'est pas tronque, l'arret est vu au point suivant."""
    journal: list[str] = []

    class _Publieur:
        started = False

        def start(self) -> None:
            journal.append("start")
            self.started = True

        def stop(self) -> None:
            journal.append("stop")
            self.started = False

        def due_at(self) -> float:
            journal.append("due_at")
            return time.monotonic() + (0.0 if len(journal) < 3 else 30.0)

        def run_due(self) -> None:
            journal.append("run_due:debut")
            signal.raise_signal(signal.SIGTERM)
            journal.append("run_due:fin")

    ReadSurfaceRunner(publisher=_Publieur(), clock=portee.clock, stop=portee.stop).run()
    assert journal == ["start", "due_at", "run_due:debut", "run_due:fin", "stop"]
    assert portee.stop.cause is signal.SIGTERM


@pytest.mark.reference
def test_arret_deja_demande_avant_le_premier_cycle(portee) -> None:
    journal: list[str] = []

    class _Publieur:
        started = False

        def start(self) -> None:
            journal.append("start")
            self.started = True

        def stop(self) -> None:
            journal.append("stop")
            self.started = False

        def due_at(self) -> float:  # pragma: no cover - jamais atteint
            journal.append("due_at")
            return time.monotonic()

        def run_due(self) -> None:  # pragma: no cover - jamais atteint
            journal.append("run_due")

    signal.raise_signal(signal.SIGINT)
    ReadSurfaceRunner(publisher=_Publieur(), clock=portee.clock, stop=portee.stop).run()
    assert journal == ["start", "stop"]
    assert portee.stop.cause is signal.SIGINT


# ---------------------------------------------------------------------------
# P. Frontieres du module de production
# ---------------------------------------------------------------------------


@pytest.mark.reference
def test_le_module_n_a_aucun_effet_de_bord_a_l_import() -> None:
    """Ni gestionnaire pose, ni socket ouverte, ni descripteur installe."""
    arbre = ast.parse(pathlib.Path(boilerack.lifecycle.__file__).read_text(encoding="utf-8"))
    autorises = (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef,
                 ast.AnnAssign, ast.Assign, ast.Expr)
    for noeud in arbre.body:
        assert isinstance(noeud, autorises), ast.dump(noeud)
        if isinstance(noeud, ast.Expr):
            assert isinstance(noeud.value, ast.Constant)


@pytest.mark.reference
def test_le_module_ne_configure_pas_la_journalisation() -> None:
    """C9 n'est pas le point d'entree : il n'impose rien au processus hote."""
    source = pathlib.Path(boilerack.lifecycle.__file__).read_text(encoding="utf-8")
    for interdit in ("basicConfig", "addHandler", "StreamHandler", "getLogger"):
        assert interdit not in source


@pytest.mark.reference
def test_le_module_n_utilise_aucun_verrou_ni_thread_event() -> None:
    """La primitive rejetee ne doit pas revenir par la porte de derriere."""
    source = pathlib.Path(boilerack.lifecycle.__file__).read_text(encoding="utf-8")
    code = source.split('"""')[2] if source.count('"""') >= 3 else source
    for interdit in ("threading.Event", "Lock(", ".acquire(", "SimpleQueue"):
        assert interdit not in code, interdit


@pytest.mark.reference
def test_le_module_n_importe_ni_argparse_ni_os_environ() -> None:
    source = pathlib.Path(boilerack.lifecycle.__file__).read_text(encoding="utf-8")
    for interdit in ("argparse", "os.environ", "getenv", "tomllib", "yaml", "sys.exit"):
        assert interdit not in source


@pytest.mark.reference
def test_le_module_n_ouvre_aucune_connexion_reseau() -> None:
    """Seule `socketpair` est employee : aucune adresse, aucun `connect`."""
    source = pathlib.Path(boilerack.lifecycle.__file__).read_text(encoding="utf-8")
    assert "socket.socketpair()" in source
    for interdit in ("socket.socket(", ".connect(", ".bind(", ".listen(", "AF_INET"):
        assert interdit not in source


@pytest.mark.reference
def test_aucun_secret_ni_valeur_de_site_dans_le_module() -> None:
    source = pathlib.Path(boilerack.lifecycle.__file__).read_text(encoding="utf-8")
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", source)
    for interdit in ("password", "passwd", "/home/", "localhost", "192.168"):
        assert interdit not in source.lower()


# ---------------------------------------------------------------------------
# Q. Echec PARTIEL de `SignalScope.__enter__` — rien ne doit fuiter
# ---------------------------------------------------------------------------


def _capturer_la_paire(monkeypatch) -> list:
    """Retient la paire de sockets creee par la portee, pour l'inspecter apres."""
    paires: list = []
    vrai = socket.socketpair

    def espion(*args, **kwargs):
        paire = vrai(*args, **kwargs)
        paires.append(paire)
        return paire

    monkeypatch.setattr(socket, "socketpair", espion)
    return paires


@pytest.mark.reference
def test_echec_partiel_de_l_entree_ne_laisse_rien_installe(monkeypatch) -> None:
    """Une installation qui echoue A MI-CHEMIN doit tout defaire.

    Scenario : la paire de sockets est creee, le descripteur de reveil est
    installe, le gestionnaire `SIGINT` est pose — puis la pose de `SIGTERM`
    echoue. `__enter__` doit remonter l'erreur ET avoir tout rendu.

    Tue le mutant « retirer le nettoyage du chemin d'echec de `__enter__` ».
    """
    avant_gestionnaires = {n: signal.getsignal(n) for n in SIGNALS_SURVEILLES}
    avant_fd = signal.set_wakeup_fd(-1)
    signal.set_wakeup_fd(avant_fd)

    paires = _capturer_la_paire(monkeypatch)
    vrai_signal = signal.signal
    poses: list[int] = []

    def signal_defaillant(numero, gestionnaire):
        if (
            numero == signal.SIGTERM
            and gestionnaire is boilerack.lifecycle._gestionnaire_vide
        ):
            raise OSError("installation impossible")
        poses.append(int(numero))
        return vrai_signal(numero, gestionnaire)

    monkeypatch.setattr(signal, "signal", signal_defaillant)

    with pytest.raises(OSError, match="installation impossible"):
        with SignalScope():
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()

    assert paires, "aucune paire de sockets n'a ete creee : scenario invalide"
    emetteur, recepteur = paires[0]
    assert emetteur.fileno() == -1, "socket emettrice laissee ouverte"
    assert recepteur.fileno() == -1, "socket receptrice laissee ouverte"

    apres_fd = signal.set_wakeup_fd(-1)
    signal.set_wakeup_fd(apres_fd)
    assert apres_fd == avant_fd, "descripteur de reveil non restaure"

    for numero, ancien in avant_gestionnaires.items():
        assert signal.getsignal(numero) is ancien, f"gestionnaire {numero} non restaure"

    assert int(signal.SIGINT) in poses, "le scenario n'a pas atteint l'installation partielle"


@pytest.mark.reference
def test_echec_des_l_installation_du_descripteur_ne_laisse_rien_ouvert(monkeypatch) -> None:
    """Meme exigence lorsque l'echec survient encore plus tot."""
    avant_gestionnaires = {n: signal.getsignal(n) for n in SIGNALS_SURVEILLES}
    paires = _capturer_la_paire(monkeypatch)

    def wakeup_defaillant(descripteur, **kwargs):
        raise OSError("descripteur refuse")

    monkeypatch.setattr(signal, "set_wakeup_fd", wakeup_defaillant)

    with pytest.raises(OSError, match="descripteur refuse"):
        with SignalScope():
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()

    emetteur, recepteur = paires[0]
    assert emetteur.fileno() == -1
    assert recepteur.fileno() == -1
    for numero, ancien in avant_gestionnaires.items():
        assert signal.getsignal(numero) is ancien


# ---------------------------------------------------------------------------
# R. Double echec incluant une `BaseException`
# ---------------------------------------------------------------------------


class _PanneDeBase(BaseException):
    """`BaseException` factice : montre que la correction ne vise pas `SystemExit` seul."""


@pytest.mark.reference
def test_system_exit_et_restauration_en_echec_sont_tous_deux_conserves() -> None:
    """`ExceptionGroup` refuserait d'imbriquer un `SystemExit` et perdrait l'origine.

    Le groupe doit donc etre un `BaseExceptionGroup`. Les deux exceptions sont
    conservees, dans l'ordre, avec leur identite.
    """
    scope = SignalScope()
    origine = SystemExit(3)
    with pytest.raises(BaseExceptionGroup) as capture:
        with scope:
            scope._retirer_descripteur = _lever_restauration  # type: ignore[assignment]
            raise origine
    groupe = capture.value
    assert not isinstance(groupe, ExceptionGroup), (
        "un melange contenant une BaseException ne doit pas etre un ExceptionGroup"
    )
    assert len(groupe.exceptions) == 2
    assert groupe.exceptions[0] is origine
    assert isinstance(groupe.exceptions[1], RuntimeError)
    assert str(groupe.exceptions[1]) == "restauration impossible"
    signal.set_wakeup_fd(-1)  # la restauration a ete sabotee


@pytest.mark.reference
def test_une_base_exception_quelconque_est_conservee_de_la_meme_facon() -> None:
    """La correction ne depend pas de `SystemExit` en particulier."""
    scope = SignalScope()
    origine = _PanneDeBase("panne de base")
    with pytest.raises(BaseExceptionGroup) as capture:
        with scope:
            scope._retirer_descripteur = _lever_restauration  # type: ignore[assignment]
            raise origine
    assert capture.value.exceptions[0] is origine
    assert isinstance(capture.value.exceptions[1], RuntimeError)
    signal.set_wakeup_fd(-1)


@pytest.mark.reference
def test_keyboard_interrupt_et_restauration_en_echec() -> None:
    """`KeyboardInterrupt` levee directement — aucun vrai Ctrl-C n'est declenche."""
    scope = SignalScope()
    origine = KeyboardInterrupt()
    with pytest.raises(BaseExceptionGroup) as capture:
        with scope:
            scope._retirer_descripteur = _lever_restauration  # type: ignore[assignment]
            raise origine
    assert capture.value.exceptions[0] is origine
    signal.set_wakeup_fd(-1)


@pytest.mark.reference
def test_deux_exceptions_ordinaires_donnent_toujours_un_exception_group() -> None:
    """Le cas courant est inchange : `BaseExceptionGroup` rend un `ExceptionGroup`.

    C'est le comportement documente du constructeur lorsque tous les membres
    sont des `Exception` — verifie ici, non suppose.
    """
    scope = SignalScope()
    origine = OSError("panne du corps")
    with pytest.raises(ExceptionGroup) as capture:
        with scope:
            scope._retirer_descripteur = _lever_restauration  # type: ignore[assignment]
            raise origine
    assert type(capture.value) is ExceptionGroup
    assert capture.value.exceptions[0] is origine
    signal.set_wakeup_fd(-1)


@pytest.mark.reference
def test_base_exception_seule_traverse_sans_groupe() -> None:
    """Sans echec de restauration, rien n'est emballe."""
    with pytest.raises(SystemExit) as capture:
        with SignalScope():
            raise SystemExit(7)
    assert not isinstance(capture.value, BaseExceptionGroup)
    assert capture.value.code == 7


@pytest.mark.reference
def test_base_exception_seule_laisse_l_etat_global_restaure() -> None:
    avant_gestionnaires, avant_fd = _etat_global()
    with pytest.raises(SystemExit):
        with SignalScope():
            raise SystemExit(7)
    apres_gestionnaires, apres_fd = _etat_global()
    assert apres_fd == avant_fd
    assert all(apres_gestionnaires[n] is avant_gestionnaires[n] for n in SIGNALS_SURVEILLES)


# ---------------------------------------------------------------------------
# S. Double echec de l'ENTREE : erreur d'installation + erreur de nettoyage
# ---------------------------------------------------------------------------


def _entree_qui_echoue(monkeypatch, origine: BaseException) -> None:
    """Fait echouer la pose de `SIGTERM`, apres que tout le reste a reussi."""
    vrai_signal = signal.signal

    def signal_defaillant(numero, gestionnaire):
        if (
            numero == signal.SIGTERM
            and gestionnaire is boilerack.lifecycle._gestionnaire_vide
        ):
            raise origine
        return vrai_signal(numero, gestionnaire)

    monkeypatch.setattr(signal, "signal", signal_defaillant)


def _saboter_le_nettoyage(scope: SignalScope) -> RuntimeError:
    """Laisse le nettoyage se faire, puis le fait echouer.

    Les ressources sont donc bel et bien rendues : seul le compte rendu du
    nettoyage echoue. C'est le cas le plus exigeant pour la politique d'erreur,
    puisque rien ne justifierait de perdre l'erreur d'entree.
    """
    vrai_restaurer = scope._restaurer  # type: ignore[attr-defined]
    panne = RuntimeError("nettoyage impossible")

    def restaurer_defaillant() -> None:
        try:
            vrai_restaurer()
        finally:
            raise panne

    scope._restaurer = restaurer_defaillant  # type: ignore[assignment]
    return panne


@pytest.mark.reference
def test_entree_et_nettoyage_en_echec_sont_tous_deux_conserves(monkeypatch) -> None:
    """Politique alignee sur `__exit__` : entree d'abord, nettoyage ensuite.

    Avant correction, l'erreur de nettoyage devenait l'exception principale et
    l'erreur d'entree ne survivait que dans `__context__`. Ce test verrouille le
    comportement corrige.
    """
    origine = OSError("entree impossible")
    _entree_qui_echoue(monkeypatch, origine)
    scope = SignalScope()
    panne = _saboter_le_nettoyage(scope)

    with pytest.raises(ExceptionGroup) as capture:
        with scope:
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()
    groupe = capture.value
    assert len(groupe.exceptions) == 2
    assert groupe.exceptions[0] is origine
    assert groupe.exceptions[1] is panne
    signal.set_wakeup_fd(-1)


@pytest.mark.reference
def test_entree_base_exception_et_nettoyage_en_echec(monkeypatch) -> None:
    """`SystemExit` a l'entree : `ExceptionGroup` refuserait de l'imbriquer."""
    origine = SystemExit(4)
    _entree_qui_echoue(monkeypatch, origine)
    scope = SignalScope()
    panne = _saboter_le_nettoyage(scope)

    with pytest.raises(BaseExceptionGroup) as capture:
        with scope:
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()
    groupe = capture.value
    assert not isinstance(groupe, ExceptionGroup)
    assert groupe.exceptions[0] is origine
    assert groupe.exceptions[1] is panne
    signal.set_wakeup_fd(-1)


@pytest.mark.reference
def test_entree_base_exception_factice_et_nettoyage_en_echec(monkeypatch) -> None:
    """La correction ne depend pas de `SystemExit` en particulier."""
    origine = _PanneDeBase("entree impossible")
    _entree_qui_echoue(monkeypatch, origine)
    scope = SignalScope()
    panne = _saboter_le_nettoyage(scope)

    with pytest.raises(BaseExceptionGroup) as capture:
        with scope:
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()
    assert capture.value.exceptions[0] is origine
    assert capture.value.exceptions[1] is panne
    signal.set_wakeup_fd(-1)


@pytest.mark.reference
def test_entree_en_echec_avec_nettoyage_reussi_ne_cree_aucun_groupe(monkeypatch) -> None:
    """Non-regression : sans echec de nettoyage, rien n'est emballe."""
    origine = OSError("entree impossible")
    _entree_qui_echoue(monkeypatch, origine)

    with pytest.raises(OSError) as capture:
        with SignalScope():
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()
    assert capture.value is origine
    assert not isinstance(capture.value, BaseExceptionGroup)


@pytest.mark.reference
def test_entree_base_exception_avec_nettoyage_reussi_traverse_telle_quelle(
    monkeypatch,
) -> None:
    origine = SystemExit(5)
    _entree_qui_echoue(monkeypatch, origine)

    with pytest.raises(SystemExit) as capture:
        with SignalScope():
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()
    assert capture.value is origine
    assert not isinstance(capture.value, BaseExceptionGroup)


@pytest.mark.reference
def test_le_double_echec_d_entree_rend_tout_de_meme_les_ressources(monkeypatch) -> None:
    """Le nettoyage a bien eu lieu, meme si son compte rendu a echoue."""
    avant_gestionnaires = {n: signal.getsignal(n) for n in SIGNALS_SURVEILLES}
    avant_fd = signal.set_wakeup_fd(-1)
    signal.set_wakeup_fd(avant_fd)
    paires = _capturer_la_paire(monkeypatch)

    _entree_qui_echoue(monkeypatch, OSError("entree impossible"))
    scope = SignalScope()
    _saboter_le_nettoyage(scope)

    with pytest.raises(ExceptionGroup):
        with scope:
            pytest.fail("l'entree aurait du echouer")  # pragma: no cover

    monkeypatch.undo()
    emetteur, recepteur = paires[0]
    assert emetteur.fileno() == -1
    assert recepteur.fileno() == -1
    apres_fd = signal.set_wakeup_fd(-1)
    signal.set_wakeup_fd(apres_fd)
    assert apres_fd == avant_fd
    for numero, ancien in avant_gestionnaires.items():
        assert signal.getsignal(numero) is ancien
