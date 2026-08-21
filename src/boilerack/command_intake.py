"""Depot inter-fils des commandes MQTT entrantes (lot W3).

Applique W2 §14 et §16. C'est la SEULE structure que le contexte de rappel Paho
a le droit de toucher : il y depose le `Message` BRUT et rend la main.

POURQUOI UNE FILE STANDARD, ET PAS UNE ABSTRACTION MAISON
    W2 §14.2 constate qu'aucune primitive du depot ne convient — `ConnectionState`
    porte un booleen idempotent sans historique, `SignalStop` compte des octets,
    et `BoundedQueue` n'est pas sure entre fils — puis note que la bibliotheque
    standard offre deja exactement ce qu'il faut. `queue.Queue` est bornee et
    sure entre fils ; cette classe ne fait que lui donner la SEMANTIQUE
    contractee, sans reimplementer sa mecanique.

CE QUE CETTE CLASSE GARANTIT
    - depot NON BLOQUANT : `offer()` ne fait jamais attendre le fil reseau de
      Paho. W2 §6 fait 5 : un rappel qui n'en finit pas empeche `loop_misc()`
      d'etre atteint, donc gele le keepalive et fait deconnecter le broker ;
    - borne : la capacite est fixe, et le debordement est un fait observable,
      jamais une croissance memoire alimentee par le reseau (W2 §16.1) ;
    - debordement JOURNALISE et compte, sans aucun ACK (W2 §16.4) : il n'y a pas
      eu d'admission, donc aucun `request_id` connu du coeur, donc rien a
      acquitter et aucune promesse de C3 engagee.

CE QUE CETTE CLASSE N'EST PAS
    Ni une file du coeur — `BoundedQueue` reste seule a porter `queue_full` —,
    ni un point de deduplication, ni un decodeur. Elle transporte des octets
    deja empaquetes par l'adaptateur, sans les lire.

CONSOMMATION PAR UN SEUL FIL
    `poll()` est appele par le PROPRIETAIRE au sens de W2 §12, jamais par le fil
    de rappel. Le patron est celui de `ConnectionState` et de `SignalStop` :
    ecriture depuis n'importe quel fil, consommation par un seul.
"""

from __future__ import annotations

import logging
import queue

from boilerack.transport.mqtt import Message

__all__ = ["CommandIntake"]

logger = logging.getLogger(__name__)


class CommandIntake:
    """File bornee et sure entre fils, deposee par Paho, consommee par le proprietaire.

    La capacite est fournie par l'appelant : c'est la composition qui connait a
    la fois cette valeur et la `queue_capacity` du coeur, et c'est donc elle qui
    fait respecter le plancher de W2 §16.3. Cette classe reste une feuille sans
    dependance vers `boilerack.core`.
    """

    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise ValueError(f"la capacite doit etre un entier : {capacity!r}")
        if capacity <= 0:
            raise ValueError(f"la capacite doit etre strictement positive : {capacity!r}")
        self._capacity = capacity
        self._file: queue.Queue[Message] = queue.Queue(maxsize=capacity)
        self._debordements = 0

    # -- depot, depuis n'importe quel fil ------------------------------------

    def offer(self, message: Message) -> bool:
        """Depose un message. NE BLOQUE JAMAIS. Rend `False` si le depot est plein.

        Aucun ACK n'est produit ni suggere par cette valeur de retour : elle sert
        a l'observabilite et aux tests, pas a acquitter un demandeur.
        """
        try:
            self._file.put_nowait(message)
        except queue.Full:
            self._debordements += 1
            # W2 §16.4 : journalise, sans ACK, et NON assimilable a la fenetre de
            # coupure de W1 §17.3 — le pont est ici connecte et sain.
            logger.warning(
                "depot de commande sature, message abandonne sans acquittement "
                "capacite=%d topic=%s debordements=%d",
                self._capacity,
                message.topic,
                self._debordements,
            )
            return False
        return True

    # -- consommation, proprietaire uniquement -------------------------------

    def poll(self) -> Message | None:
        """Retire le plus ancien message, ou `None` si le depot est vide.

        Ne bloque jamais. Appele par le seul contexte proprietaire (W2 §12).
        """
        try:
            return self._file.get_nowait()
        except queue.Empty:
            return None

    # -- inspection ----------------------------------------------------------

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def depth(self) -> int:
        """Profondeur courante. Indicative : un autre fil peut deposer entre-temps."""
        return self._file.qsize()

    @property
    def overflows(self) -> int:
        """Nombre de messages abandonnes faute de place, depuis la creation."""
        return self._debordements
