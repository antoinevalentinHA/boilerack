"""Couture runtime de la voie transactionnelle (lot W3).

Assemble W0 + W1 + W2 en un objet unique, `TransactionSurface`, que la boucle du
runner pilote. Ce module ne decide RIEN : il applique.

    W1 -> quel topic, quel QoS, quel prefixe d'ACK
    W2 -> quel fil, quelle cadence, quel ordre, quel demarrage, quel arret
    W0 -> la souscription survit a une reconnexion, sans que ce module s'en mele

FRONTIERE W4 — LA BARRIERE EST UN TYPE, PAS UNE POLITIQUE
    `build_transaction_surface` exige un `VClient` (donc `read` ET `write`) et un
    `Profile`. Or, dans ce depot :

    - le seul adaptateur `vclient` reel, `VClientCliReader`, n'implemente que
      `read` : il ne satisfait PAS `VClient` ;
    - aucun `Profile` reel n'existe — le seul constructeur est
      `boilerack.testing.fake_profile`, declare infrastructure de test.

    Aucun appelant de production ne peut donc construire cette surface. Ce n'est
    pas un interrupteur qu'on pourrait oublier ouvert : c'est l'absence des deux
    dependances obligatoires. Ouvrir la voie exige W4, et W4 seul.

CE QUE CE MODULE NE FAIT PAS
    Aucun decodage JSON, aucune validation, aucune deduplication : W1 §11.3 remet
    le payload BRUT au coeur, qui est seul juge. Aucun retry d'ACK, aucun SUBACK,
    aucun second client MQTT, aucun verrou ajoute au coeur.
"""

from __future__ import annotations

import logging
from typing import Final

from boilerack.adapters.config import MqttConfig
from boilerack.clock import Clock
from boilerack.command_intake import CommandIntake
from boilerack.core.engine import DEFAULT_QUEUE_CAPACITY, TransactionalCore
from boilerack.core.profile import Profile
from boilerack.transport.mqtt import Message, MqttClient
from boilerack.transport.vclient import VClient

__all__ = ["COMMAND_QOS", "TransactionSurface", "build_transaction_surface"]

logger = logging.getLogger(__name__)

#: QoS de souscription au topic de commande. W1 §7.3 l'exige EXPLICITE : la
#: valeur par defaut de `MqttClient.subscribe` est 0, et s'y fier reviendrait a
#: demander QoS 0 sans le dire.
COMMAND_QOS: Final = 1


class TransactionSurface:
    """Voie transactionnelle cablee, pilotee de l'exterieur par le proprietaire.

    Trois methodes, appelees dans cet ordre exact par la boucle du runner
    (W2 §13.3), APRES `run_due()` :

        install()        une fois, AVANT connect()
        admettre_un()    au plus UNE admission par iteration
        executer_un()    au plus UNE execution par iteration

    Aucune de ces methodes n'est appelee depuis le fil reseau de Paho. Le seul
    code qui s'y execute est `_deposer`, qui ne fait qu'un depot borne.
    """

    def __init__(
        self,
        *,
        core: TransactionalCore,
        intake: CommandIntake,
        mqtt: MqttClient,
        command_topic: str,
    ) -> None:
        self._core = core
        self._intake = intake
        self._mqtt = mqtt
        self._command_topic = command_topic
        self._installe = False

    # -- installation, AVANT connect ----------------------------------------

    def install(self) -> None:
        """Enregistre le gestionnaire PUIS souscrit. A appeler avant `connect()`.

        L'ordre importe deux fois :

        - W2 §18.3 — le gestionnaire doit etre en place avant qu'un rappel soit
          possible. `PahoMqttClient._handler` est ecrit ici et lu par
          `_on_message` sans verrou ; poser l'ecriture avant `connect()` rend
          cette absence de verrou sure PAR CONSTRUCTION, jamais par
          chronometrie. C'est le raisonnement deja tenu par C11 pour
          `mark_connected()` ;
        - W1 §7.2 — une seule souscription, a ce seul topic, sans joker.

        La souscription est demandee meme hors connexion : W0 enregistre
        l'intention INCONDITIONNELLEMENT et la reemet apres chaque CONNACK
        reussi. Ce module ne duplique donc aucune logique de reconnexion.

        `TransactionalCore.attach()` n'est PAS utilise : il cablerait `submit`
        directement sur le rappel, ce que W2 §12.1.2 interdit en runtime.
        """
        if self._installe:
            raise RuntimeError("la surface transactionnelle est deja installee.")
        self._mqtt.set_message_handler(self._deposer)
        self._mqtt.subscribe(self._command_topic, qos=COMMAND_QOS)
        self._installe = True

    # -- contexte de rappel Paho : depot, et rien d'autre --------------------

    def _deposer(self, message: Message) -> None:
        """Unique code execute sur le fil reseau de Paho (W2 §14.1).

        Ne publie pas, ne lit pas `vclient`, ne touche aucune structure du coeur,
        ne prend aucun verrou, et ne bloque jamais. La valeur rendue par `offer`
        est volontairement ignoree : un debordement se journalise, il ne
        s'acquitte pas (W2 §16.4).
        """
        self._intake.offer(message)

    # -- proprietaire : admission puis execution ----------------------------

    def admettre_un(self) -> bool:
        """Admet AU PLUS UN message. Rend `True` si un message a ete admis.

        W2 §13.1 : une admission par iteration. C'est la seule cadence pour
        laquelle l'admission n'alimente pas le coeur plus vite que l'execution ne
        le vide ; la profondeur de la file du coeur revient donc a zero a la fin
        de chaque iteration nominale.

        La valeur rendue par `submit` est ignoree : W1 §11.4 interdit de fonder
        un comportement dessus, l'acquittement passant par MQTT.
        """
        message = self._intake.poll()
        if message is None:
            return False
        self._core.submit(message)
        return True

    def executer_un(self) -> None:
        """Execute AU PLUS UNE transaction admise (W2 §13.1).

        `process_next()` rend `None` sans rien faire quand la file est vide :
        « au plus une » n'est jamais transforme en « exactement une ».

        `drain()` n'est appele NI ici, NI a l'arret (W2 §19.5, §21) : il herite
        de la non-borne de l'ecriture, et un drainage complet excede la marge de
        `TimeoutStopSec` etablie par C12 §10.
        """
        self._core.process_next()

    # -- inspection ----------------------------------------------------------

    @property
    def core(self) -> TransactionalCore:
        return self._core

    @property
    def intake(self) -> CommandIntake:
        return self._intake

    @property
    def command_topic(self) -> str:
        return self._command_topic

    @property
    def installed(self) -> bool:
        return self._installe


def build_transaction_surface(
    *,
    mqtt: MqttClient,
    clock: Clock,
    config: MqttConfig,
    vclient: VClient,
    profile: Profile,
    queue_capacity: int = DEFAULT_QUEUE_CAPACITY,
    intake_capacity: int | None = None,
) -> TransactionSurface:
    """Compose la voie transactionnelle. **Seul endroit** ou elle est assemblee.

    `mqtt` est l'instance DEJA construite par la racine de composition : W1 §7.5
    n'admet qu'un seul client MQTT en runtime, et W2 §26 le rappelle. Aucune
    seconde instance, aucun second `client_id`, aucune seconde boucle reseau.

    `clock` doit etre l'instance DEJA remise au runner et au publieur (W2, A-9) :
    sans quoi le temps du coeur et celui de la boucle divergeraient.

    AUTORITES DE CONFIGURATION — `config.command_topic` et
    `config.ack_topic_prefix` sont transmis EXPLICITEMENT. Le defaut de
    `TransactionalCore` reste un defaut de bibliotheque, mais la composition ne
    s'y fie pas : W1 §8.3 a supprime la double autorite, et laisser le defaut
    agir la recreerait.

    CAPACITE DU DEPOT — W2 §16.3 : la capacite MUST etre >= `queue_capacity` du
    coeur. Cette fonction est le seul endroit qui connaisse les deux valeurs,
    c'est donc ici que le plancher est verifie. Par defaut, la capacite du depot
    EGALE `queue_capacity`.

    HYPOTHESE RETENUE, ET CE QU'ELLE N'EST PAS — ce plancher n'est pas derive
    d'un debit d'arrivee mesure : ce debit est l'inconnue I5 de W2, et ce depot
    ne pretend pas la resoudre. `queue_capacity` est retenue parce qu'elle est la
    seule grandeur du depot exprimant combien de commandes en attente Boilerack
    est concu a retenir, et parce que ce plancher survit a un changement de
    cadence. Aucune cle de configuration utilisateur n'est creee : C10 et W1 §18
    l'interdisent.
    """
    if intake_capacity is None:
        intake_capacity = queue_capacity
    if intake_capacity < queue_capacity:
        raise ValueError(
            "W2 §16.3 : la capacite du depot doit etre >= queue_capacity du coeur "
            f"(depot={intake_capacity}, coeur={queue_capacity})."
        )
    core = TransactionalCore(
        clock=clock,
        vclient=vclient,
        mqtt=mqtt,
        profile=profile,
        queue_capacity=queue_capacity,
        ack_topic_prefix=config.ack_topic_prefix,
    )
    return TransactionSurface(
        core=core,
        intake=CommandIntake(intake_capacity),
        mqtt=mqtt,
        command_topic=config.command_topic,
    )
