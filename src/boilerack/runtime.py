"""Composition root et boucle d'execution (lot C8).

Premier module qui **assemble** Boilerack au lieu de le decrire. Il fait deux
choses, et rien d'autre :

1. `build_runtime` construit les adaptateurs concrets et les cable ;
2. `ReadSurfaceRunner` pilote le publieur de l'exterieur — `due_at`, attente,
   `run_due` — jusqu'a ce qu'un arret soit demande.

BIBLIOTHEQUE CONTRE PROGRAMME
    Tout ce qui precede C8 est une **bibliotheque** : des composants qui ne
    construisent rien et ne decident de rien. Ce module est la premiere brique
    de **programme**. La frontiere est nette et doit le rester : le publieur ne
    construit toujours aucune dependance, et ce module ne porte **aucune
    logique metier** — ni lecture, ni statut, ni cadence. Il compose et il
    boucle.

AUCUN EFFET DE BORD A L'IMPORT
    Importer ce module ne construit rien, n'ouvre aucune connexion et ne lance
    aucun processus. `build_runtime` est une fonction : c'est l'appeler qui
    construit — et construire un client Paho n'ouvre toujours aucune socket,
    seul `connect()` le ferait.

L'HORLOGE SUFFIT, IL N'Y A PAS DE `Waiter`
    `boilerack.clock.Clock` porte deja `sleep()`, et `VirtualClock` l'implemente
    en avancant le temps virtuel **sans jamais attendre**. Introduire une
    abstraction d'attente separee dupliquerait une couture qui existe. La boucle
    dort donc via l'horloge injectee : reelle en production, virtuelle en test.

AUCUNE CONFORMITE PRODUCTION N'EST REVENDIQUEE. Rien n'a ete eprouve contre un
broker, un demon `vcontrold` ou une chaudiere reels. Il n'y a ni point d'entree
installe, ni service, ni gestion de signaux : voir les reports en fin de
docs/design/c8-composition-root.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, Protocol, Sequence

from boilerack.adapters.config import MqttConfig, VclientConfig
from boilerack.adapters.mqtt_paho import PahoMqttClient
from boilerack.adapters.process_runner import SubprocessRunner
from boilerack.adapters.vclient_cli import VClientCliReader
from boilerack.clock import Clock, SystemClock
from boilerack.connection_state import ConnectionState
from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.measurements import V1_MEASUREMENTS, MeasurementSpec
from boilerack.read_surface.publisher import MeasurementReader, ReadSurfacePublisher
from boilerack.transport.mqtt import PresenceMqttClient

if TYPE_CHECKING:  # pragma: no cover - reserve a la verification de types
    # W3 : `TransactionSurface` n'apparait QUE dans des annotations. Sous
    # `from __future__ import annotations`, celles-ci ne sont jamais
    # evaluees a l'execution, donc importer ce module au niveau global
    # chargerait le coeur transactionnel et son transport pour un runtime
    # de production qui reste en LECTURE SEULE. L'import est donc reserve
    # aux verificateurs de types.
    from boilerack.transaction_wiring import TransactionSurface

__all__ = [
    "StopSignal",
    "NeverStop",
    "RuntimeConfig",
    "Runtime",
    "ReadSurfaceRunner",
    "build_runtime",
]

#: Messages des groupes d'erreurs. Non contractuels : seule importe la
#: preservation des exceptions d'origine.
_DEMARRAGE_ECHOUE: Final = "echec du demarrage, puis de l'arret de secours"
_BOUCLE_ET_ARRET_ECHOUES: Final = "echec de la boucle, puis de l'arret"


class StopSignal(Protocol):
    """Demande d'arret, consultee entre deux etapes de la boucle.

    La forme `is_set()` est celle de `threading.Event` : un `Event` reel
    satisfait donc ce protocole **structurellement**, sans que ce module ait a
    importer `threading` ni a imposer un modele de concurrence.
    """

    def is_set(self) -> bool:
        ...


class NeverStop:
    """Signal qui ne demande jamais l'arret.

    Utile pour un processus destine a tourner jusqu'a interruption externe.
    N'est PAS le defaut de `ReadSurfaceRunner` : une boucle sans sortie doit
    etre demandee explicitement, jamais obtenue par omission.
    """

    def is_set(self) -> bool:
        return False


@dataclass(frozen=True)
class RuntimeConfig:
    """Configuration d'assemblage. **Contient** les configurations existantes.

    Elle ne redeclare aucun de leurs champs et ne revalide aucun de leurs
    invariants : `MqttConfig`, `VclientConfig` et `ReadSurfaceConfig` restent
    seules autorites de ce qu'elles portent. Cette structure ne fait que dire
    lesquelles composer.

    Aucun defaut n'est fourni pour l'hote du broker ni pour l'executable
    `vclient` : ce sont des valeurs de site, et le depot n'en porte aucune.
    """

    mqtt: MqttConfig
    vclient: VclientConfig
    read_surface: ReadSurfaceConfig = field(default_factory=ReadSurfaceConfig)
    specs: Sequence[MeasurementSpec] = V1_MEASUREMENTS

    def __post_init__(self) -> None:
        if not isinstance(self.mqtt, MqttConfig):
            raise ValueError(f"mqtt doit etre un MqttConfig : {type(self.mqtt).__name__}")
        if not isinstance(self.vclient, VclientConfig):
            raise ValueError(
                f"vclient doit etre un VclientConfig : {type(self.vclient).__name__}"
            )
        if not isinstance(self.read_surface, ReadSurfaceConfig):
            raise ValueError(
                f"read_surface doit etre un ReadSurfaceConfig : "
                f"{type(self.read_surface).__name__}"
            )
        object.__setattr__(self, "specs", tuple(self.specs))


class ReadSurfaceRunner:
    """Boucle exterieure : demarre, reveille, cadence, arrete.

    Ne porte AUCUNE logique metier. Elle ne sait ni ce qu'est une mesure, ni ce
    qu'est un instantane : elle demande au publieur **quand** revenir, attend, et
    lui rend la main. Tout le reste appartient a C7-C3.

    ARRET — la demande est consultee a trois moments : avant le premier cycle,
    apres chaque attente, et apres chaque cycle. Consequence a connaitre : un
    arret demande **pendant** une attente n'est vu qu'a la fin de celle-ci. La
    latence d'arret est donc bornee par la prochaine echeance — au plus la plus
    petite periode de la surface. Aucune tranche d'attente maximale n'est
    introduite : ce serait une politique, et rien ne l'exige encore.

    ATTENTE — fondee sur le temps MONOTONE, jamais sur l'heure murale. Une
    echeance deja passee ne provoque aucune attente ; il n'y a jamais de duree
    negative.
    """

    def __init__(
        self,
        publisher: ReadSurfacePublisher,
        clock: Clock,
        stop: StopSignal,
        *,
        transaction: TransactionSurface | None = None,
    ) -> None:
        self._publisher = publisher
        self._clock = clock
        self._stop = stop
        # W3 : voie transactionnelle OPTIONNELLE. `None` est le cas nominal
        # d'aujourd'hui — aucune commande n'est recue, la boucle est exactement
        # celle de C8. Une surface fournie ne peut venir que d'un appelant
        # capable de produire un `VClient` ecrivain et un `Profile` reels, ce
        # qu'aucun code de production ne sait faire avant W4.
        self._transaction = transaction

    @property
    def publisher(self) -> ReadSurfacePublisher:
        return self._publisher

    @property
    def transaction(self) -> TransactionSurface | None:
        return self._transaction

    # -- boucle --------------------------------------------------------------

    def run(self) -> None:
        """Demarre, boucle jusqu'a l'arret demande, puis arrete proprement.

        Sequence :

            start()                       <- installation W3 d'abord, si voie
            tant que l'arret n'est pas demande :
                attendre jusqu'a due_at()
                run_due()
                admettre AU PLUS UN message   <- W2 §13.3, si voie
                process_next() AU PLUS UNE FOIS
            stop()

        POLITIQUE D'ERREUR — rien n'est masque, rien n'est traduit, aucune
        taxonomie nouvelle n'est creee.

        - `start()` qui echoue interrompt tout : aucune boucle. Si le publieur
          s'est neanmoins declare demarre — C7-C3A : la connexion peut etre
          ouverte alors qu'une publication a echoue —, un arret de secours est
          tente pour ne pas fuir la connexion, et les deux erreurs sont groupees
          si cet arret echoue lui aussi ;
        - toute erreur de la boucle — `ExceptionGroup` d'erreurs MQTT collectees
          par `run_due`, defaut inattendu du lecteur, echec de `due_at` ou de
          l'attente — **arrete la boucle**. Le runner ne decide d'aucune
          politique de reprise : ce serait inventer une resilience que rien
          n'etablit. `stop()` est neanmoins tente, pour annoncer `offline` et
          refermer la connexion ;
        - si `stop()` echoue a son tour, les deux erreurs sont groupees, dans
          l'ordre : erreur de boucle d'abord, erreur d'arret ensuite ;
        - `stop()` qui echoue seul remonte tel quel.

        Seules les `Exception` sont interceptees. `KeyboardInterrupt`,
        `SystemExit` et `GeneratorExit` traversent immediatement : ce sont des
        controles de flux, pas des pannes. Consequence assumee et testee : une
        interruption clavier ne declenche PAS d'arret propre — la brancher a un
        arret gracieux releve de la gestion de signaux, reportee.
        """
        self._demarrer()

        boucle: Exception | None = None
        try:
            self._boucler()
        except Exception as exc:  # large mais non aveugle : conservee, jamais absorbee
            boucle = exc

        try:
            self._publisher.stop()
        except Exception as exc:
            if boucle is not None:
                raise ExceptionGroup(_BOUCLE_ET_ARRET_ECHOUES, [boucle, exc]) from None
            raise

        if boucle is not None:
            raise boucle

    # -- interne -------------------------------------------------------------

    def _demarrer(self) -> None:
        if self._transaction is not None:
            # W2 §18.3 : gestionnaire enregistre et souscription demandee AVANT
            # `connect()`, que `publisher.start()` declenche. Aucun rappel ne
            # peut donc preceder l'ecriture de `_handler`, et l'absence de
            # verrou sur ce champ devient sure PAR CONSTRUCTION.
            self._transaction.install()
        try:
            self._publisher.start()
        except Exception as exc:
            if not self._publisher.started:
                # Rien n'a ete ouvert : aucun arret de secours a tenter.
                raise
            try:
                self._publisher.stop()
            except Exception as arret:
                raise ExceptionGroup(_DEMARRAGE_ECHOUE, [exc, arret]) from None
            raise

    def _boucler(self) -> None:
        while not self._stop.is_set():
            self._attendre(self._publisher.due_at())
            if self._stop.is_set():
                # Un arret demande pendant l'attente est honore AVANT de
                # travailler : aucun cycle superflu.
                return
            self._publisher.run_due()
            self._pomper()

    def _pomper(self) -> None:
        """Admet au plus un message, puis execute au plus une transaction.

        Position et cadence fixees par W2 §13.3 : APRES `run_due()`, dont
        l'etape 0 est la reprise de presence C11, et jamais avant.

        "Au plus une" n'est jamais transforme en "exactement une" : un depot
        vide n'admet rien, et `process_next()` sur file vide ne fait rien.
        """
        if self._transaction is None:
            return
        # W2 §19.3.1 : des que l'arret est demande, plus AUCUNE admission.
        if not self._stop.is_set():
            self._transaction.admettre_un()
        # W2 §19.3.2 : une commande admise dans cette iteration MUST etre
        # executee dans cette MEME iteration, que l'arret ait ete demande
        # entre-temps ou non. W2 §13.3 enonce par ailleurs qu'aucune
        # consultation d'arret supplementaire n'est requise entre l'admission et
        # `process_next()` : le contrat prescrit le comportement, et lui seul.
        self._transaction.executer_un()

    def _attendre(self, echeance_monotone: float) -> None:
        """Dort jusqu'a l'echeance, sur le temps monotone.

        Une echeance deja atteinte ne provoque aucune attente : `sleep` n'est
        alors pas appele du tout, et jamais avec une duree negative.
        """
        reste = echeance_monotone - self._clock.monotonic()
        if reste > 0:
            self._clock.sleep(reste)


@dataclass(frozen=True)
class Runtime:
    """Assemblage pret a tourner.

    Deux membres, chacun avec un usage distinct : `runner` pour executer,
    `publisher` pour inspecter l'etat sans passer par la boucle. Un troisieme,
    optionnel, expose la voie transactionnelle quand elle a ete composee.
    """

    publisher: ReadSurfacePublisher
    runner: ReadSurfaceRunner
    transaction: TransactionSurface | None = None


def build_runtime(
    config: RuntimeConfig,
    stop: StopSignal,
    *,
    clock: Clock | None = None,
    transaction: TransactionSurface | None = None,
) -> Runtime:
    """Construit les adaptateurs concrets et les cable. **Seul endroit** ou ils le sont.

    Assemble :

    - `SystemClock` — horloge reelle, sauf si une autre est injectee ;
    - `PahoMqttClient` — client MQTT reel ; sa construction n'ouvre **aucune
      socket**, seul `connect()` le ferait ;
    - `SubprocessRunner` + `VClientCliReader` — lecteur reel ; la construction ne
      lance **aucun processus**, seule une lecture le ferait ;
    - `ReadSurfacePublisher` et `ReadSurfaceRunner`.

    Aucune connexion, aucune lecture, aucune publication n'a lieu ici : c'est
    `runner.run()` qui agit. Cette fonction ne doit jamais etre appelee dans un
    test sans double ni monkeypatch de la frontiere Paho.

    HORLOGE — `clock` est optionnel et reserve aux mots-cles. Omis, le
    comportement est celui d'origine : une nouvelle `SystemClock`. Fourni, c'est
    cette instance qui est utilisee — le lot C9 y injecte une horloge dont
    l'attente est interrompue par un signal. Dans les deux cas, le publieur et
    le runner recoivent **exactement la meme instance** : sans quoi le temps du
    runner et celui du publieur pourraient diverger.

    VOIE TRANSACTIONNELLE — `transaction` est optionnel et vaut `None` par
    defaut : la racine de composition n'en construit AUCUNE, et ne le peut pas.
    `build_transaction_surface` exige un `VClient` — donc `read` ET `write` — et
    un `Profile` ; or `VClientCliReader` n'implemente que `read`, et aucun
    `Profile` reel n'existe dans ce depot. La voie reste donc fermee en
    production tant que W4 n'a pas livre ces deux dependances. Fournir une
    surface deja construite est le point d'entree prevu pour W4 et pour les
    preuves hors terrain ; ce n'est pas un interrupteur qu'on pourrait laisser
    ouvert par megarde, mais l'absence de deux dependances obligatoires.
    """
    clock = clock if clock is not None else SystemClock()
    # L'annotation dit ce que la surface de lecture EXIGE : le port MQTT et la
    # capacite de notification de connexion (C11).
    mqtt: PresenceMqttClient = PahoMqttClient(config.mqtt)
    reader: MeasurementReader = VClientCliReader(config.vclient, SubprocessRunner())
    # C11 : l'etat de connexion est cree ici et remis au publieur, qui l'abonne
    # lui-meme au client. La racine assemble ; elle ne cable pas de rappel.
    connection = ConnectionState()
    publisher = ReadSurfacePublisher(
        mqtt=mqtt,
        clock=clock,
        connection=connection,
        reader=reader,
        specs=config.specs,
        config=config.read_surface,
    )
    return Runtime(
        publisher=publisher,
        runner=ReadSurfaceRunner(
            publisher=publisher, clock=clock, stop=stop, transaction=transaction
        ),
        transaction=transaction,
    )
