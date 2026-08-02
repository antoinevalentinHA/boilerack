"""Moteur transactionnel generique.

Orchestre, pour chaque commande, la sequence contractuelle : validation,
expiration, reservation d'identifiant, publication de `accepted`, ecriture via
le transport, confirmation par relecture, verdict terminal, mise en cache et
neutralisation des doublons. Il ne connait AUCUN transport reel : il ne parle
qu'aux interfaces C2 (`Clock`, `VClient`, `MqttClient`).

Deux temps distincts, pour rester deterministe et sans attente reelle :

- `submit(message)` : ADMISSION. Decode, valide, deduplique, controle la file
  bornee, reserve l'identifiant et publie `accepted`. N'ECRIT jamais.
- `process_next()` : EXECUTION. Depile une commande admise, revalide
  l'expiration, ecrit UNE fois, confirme par relecture, conclut.

Cette separation permet a un test de faire expirer une commande PENDANT son
attente en file, entre l'admission et l'execution.

Doctrine appliquee :

- « Le coeur ne suppose jamais qu'une commande a reussi. Seule une relecture
  conforme permet d'emettre `applied`. »
- Frontiere transport (arbitrages 1.a / 1.b) : seul `DAEMON_UNREACHABLE` prouve
  qu'aucune ecriture n'a ete emise (`bridge_unavailable`) ; `UNKNOWN_COMMAND`
  est un defaut permanent (`unsupported_command`) ; `TIMEOUT`,
  `UNUSABLE_OUTPUT` et `TRANSPORT_ERROR` peuvent avoir emis l'ecriture -> jamais
  `bridge_unavailable`, relecture puis `applied`/`timeout`.
- Publication de `accepted` (arbitrage 2, fail-closed) : si l'ACK `accepted`
  echoue de facon ETABLIE avant l'ecriture, la commande n'est PAS executee.
- Un echec de publication ne transforme jamais une commande en succes ; le
  verdict est decide par le fait physique, la livraison MQTT est un fait
  distinct, sans retry automatique.
"""

from __future__ import annotations

from datetime import datetime

from boilerack.clock import Clock
from boilerack.core.ack import Ack, Reason, ack_to_json
from boilerack.core.command import extract_request_id, is_canonical_uuid4
from boilerack.core.dedup import (
    DEFAULT_TERMINAL_TTL_SECONDS,
    InFlightRegistry,
    TerminalCache,
)
from boilerack.core.profile import Profile
from boilerack.core.validation import Rejection, ValidatedCommand, validate
from boilerack.bounded_queue import BoundedQueue, QueueEmpty
from boilerack.transport.mqtt import Message, MqttClient, PublishHandle
from boilerack.transport.vclient import TransportStatus, VClient

# Statuts d'ecriture pour lesquels la chaudiere PEUT avoir ete sollicitee : on
# ne pretend jamais l'absence d'ecriture, on releit puis on conclut.
_MAYBE_EMITTED = frozenset(
    {
        TransportStatus.OK,
        TransportStatus.TIMEOUT,
        TransportStatus.UNUSABLE_OUTPUT,
        TransportStatus.TRANSPORT_ERROR,
    }
)

DEFAULT_QUEUE_CAPACITY = 16
DEFAULT_CONFIRM_BUDGET_SECONDS = 5.0
DEFAULT_CONFIRM_INTERVAL_SECONDS = 0.5
DEFAULT_ACK_TOPIC_PREFIX = "boilerack/ack"
_UNKNOWN_ROLE_TOPIC = "_unknown"

_ACK_QOS = 1
_ACK_RETAIN = False


class TransactionalCore:
    """Coeur transactionnel, pilote par un profil declaratif."""

    def __init__(
        self,
        *,
        clock: Clock,
        vclient: VClient,
        mqtt: MqttClient,
        profile: Profile,
        queue_capacity: int = DEFAULT_QUEUE_CAPACITY,
        confirm_budget_s: float = DEFAULT_CONFIRM_BUDGET_SECONDS,
        confirm_interval_s: float = DEFAULT_CONFIRM_INTERVAL_SECONDS,
        terminal_ttl_s: float = DEFAULT_TERMINAL_TTL_SECONDS,
        ack_topic_prefix: str = DEFAULT_ACK_TOPIC_PREFIX,
    ) -> None:
        if confirm_budget_s < 0:
            raise ValueError("confirm_budget_s doit etre >= 0.")
        if confirm_interval_s <= 0:
            raise ValueError("confirm_interval_s doit etre > 0.")
        self._clock = clock
        self._vclient = vclient
        self._mqtt = mqtt
        self._profile = profile
        self._queue: BoundedQueue[ValidatedCommand] = BoundedQueue(queue_capacity)
        self._in_flight = InFlightRegistry()
        self._terminal = TerminalCache(clock, terminal_ttl_s)
        self._confirm_budget_s = float(confirm_budget_s)
        self._confirm_interval_s = float(confirm_interval_s)
        self._ack_prefix = ack_topic_prefix

    # -- couture d'entree MQTT ----------------------------------------------

    def attach(self, mqtt: MqttClient | None = None) -> None:
        """Enregistre `submit` comme handler de message entrant.

        La voie d'entree reste minimale : chaque `Message` recu est soumis a
        l'admission. Le pilotage de l'execution (`process_next`) reste explicite.
        """
        target = mqtt if mqtt is not None else self._mqtt
        target.set_message_handler(self.submit)

    # -- admission -----------------------------------------------------------

    def submit(self, message: Message) -> Ack | None:
        """Admet (ou rejette) une commande. N'ECRIT jamais.

        Renvoie l'ACK immediat (`accepted` ou rejet terminal), le verdict rejoue
        pour un doublon deja conclu, ou `None` pour un doublon encore en vol.
        """
        payload = message.payload
        request_id = extract_request_id(payload)
        canonical = is_canonical_uuid4(request_id)

        # Deduplication (uniquement pour un request_id canonique : sans lui, il
        # n'y a pas d'identite stable a dedupliquer).
        if canonical:
            replayed = self._terminal.get(request_id)
            if replayed is not None:
                # Rejeu du verdict terminal, SANS reexecution.
                self._publish_ack(replayed, self._topic_role(payload))
                return replayed
            if self._in_flight.contains(request_id):
                # Doublon en vol : aucun second travail, pas de nouveau accepted ;
                # le verdict de la transaction initiale suffira.
                return None

        result = validate(payload, self._profile, self._clock.now())

        if isinstance(result, Rejection):
            ack = Ack.rejected(request_id, result.reason)
            if canonical:
                self._terminal.put(request_id, ack)
            self._publish_ack(ack, self._topic_role(payload))
            return ack

        return self._admit(result)

    def _admit(self, validated: ValidatedCommand) -> Ack:
        request_id = validated.command.request_id
        role = validated.spec.role

        # Saturation : ne PAS reserver l'identifiant, pas de `accepted`.
        if self._queue.depth >= self._queue.capacity:
            ack = Ack.rejected(request_id, Reason.QUEUE_FULL)
            self._terminal.put(request_id, ack)
            self._publish_ack(ack, role)
            return ack

        # Place disponible : reserver, publier `accepted`, PUIS mettre en file.
        self._in_flight.reserve(request_id)
        accepted = Ack.accepted(request_id)
        handle = self._publish_ack(accepted, role)

        # Arbitrage 2 (fail-closed) : echec ETABLI de `accepted` avant ecriture.
        # Un handle simplement demande (ni confirme ni echoue) n'est PAS un echec :
        # on ne bloque pas en attente du PUBACK.
        if handle is not None and handle.failed:
            self._in_flight.release(request_id)
            verdict = Ack.rejected(request_id, Reason.BRIDGE_UNAVAILABLE)
            self._terminal.put(request_id, verdict)
            self._publish_ack(verdict, role)  # meilleure effort ; ne change rien
            return verdict

        self._queue.put(validated)
        return accepted

    # -- execution -----------------------------------------------------------

    def process_next(self) -> Ack | None:
        """Execute la prochaine commande admise, ou `None` si la file est vide."""
        try:
            validated = self._queue.get()
        except QueueEmpty:
            return None

        request_id = validated.command.request_id
        role = validated.spec.role

        # Revalidation de l'expiration IMMEDIATEMENT avant l'ecriture.
        if self._clock.now() >= validated.command.expires_at:
            return self._finish(request_id, Ack.rejected(request_id, Reason.EXPIRED), role)

        verdict = self._execute(validated)
        return self._finish(request_id, verdict, role)

    def drain(self) -> list[Ack]:
        """Execute toutes les commandes admises en attente, dans l'ordre FIFO."""
        verdicts: list[Ack] = []
        while True:
            ack = self.process_next()
            if ack is None:
                break
            verdicts.append(ack)
        return verdicts

    def _execute(self, validated: ValidatedCommand) -> Ack:
        request_id = validated.command.request_id
        spec = validated.spec
        assert spec.write is not None  # garanti : un role lecture seule est rejete

        # UNE SEULE invocation d'ecriture par transaction. Jamais de retry d'ecriture.
        write = self._vclient.write(spec.write, float(validated.target))
        status = write.status

        if status in _MAYBE_EMITTED:
            # La chaudiere peut avoir ete sollicitee : on confirme par relecture.
            return self._confirm(validated)
        if status is TransportStatus.DAEMON_UNREACHABLE:
            # Preuve typee qu'aucune ecriture n'a ete emise.
            return Ack.rejected(request_id, Reason.BRIDGE_UNAVAILABLE)
        if status is TransportStatus.UNKNOWN_COMMAND:
            # Defaut permanent : commande declaree non reconnue par le transport.
            return Ack.rejected(request_id, Reason.UNSUPPORTED_COMMAND)
        # Defense : les 6 statuts sont couverts ci-dessus. Par prudence, on ne
        # pretend pas l'absence d'ecriture pour un statut imprevu.
        return Ack.rejected(request_id, Reason.BRIDGE_UNAVAILABLE)

    def _confirm(self, validated: ValidatedCommand) -> Ack:
        request_id = validated.command.request_id
        spec = validated.spec
        target = validated.target

        deadline = self._clock.monotonic() + self._confirm_budget_s
        while True:
            read = self._vclient.read(spec.read)
            # `ReadResult` durci : OK implique une valeur finie ; une lecture non
            # OK (y compris sortie NaN/inexploitable) ne confirme rien.
            if read.ok and _confirms(read.value, target, spec.confirm_tolerance, spec):
                return Ack.applied(request_id)
            if self._clock.monotonic() >= deadline:
                return Ack.timeout(request_id)
            self._clock.sleep(self._confirm_interval_s)

    # -- cloture et publication ---------------------------------------------

    def _finish(self, request_id: str, verdict: Ack, role: str) -> Ack:
        # Le verdict est decide par le fait physique. On le memorise et on libere
        # l'identifiant AVANT de tenter la publication : une livraison MQTT
        # ratee ne doit ni changer le verdict, ni etre retentee.
        self._terminal.put(request_id, verdict)
        self._in_flight.release(request_id)
        self._publish_ack(verdict, role)
        return verdict

    def _publish_ack(self, ack: Ack, role: str) -> PublishHandle:
        topic = f"{self._ack_prefix}/{role}"
        return self._mqtt.publish(
            topic, ack_to_json(ack), qos=_ACK_QOS, retain=_ACK_RETAIN
        )

    def _topic_role(self, payload: bytes) -> str:
        """Deduit le role de topic depuis le payload, pour un ACK de rejet.

        Utilise le champ `role` s'il est une chaine non vide, sinon un bucket
        neutre : un rejet de forme peut ne pas exposer de role valable.
        """
        from boilerack.core.command import decode_payload, CommandFormError

        try:
            obj = decode_payload(payload)
        except CommandFormError:
            return _UNKNOWN_ROLE_TOPIC
        role = obj.get("role")
        return role if isinstance(role, str) and role != "" else _UNKNOWN_ROLE_TOPIC

    # -- inspection ----------------------------------------------------------

    @property
    def queue_depth(self) -> int:
        return self._queue.depth

    @property
    def max_queue_depth(self) -> int:
        return self._queue.max_depth_observed

    @property
    def in_flight_count(self) -> int:
        return len(self._in_flight)

    @property
    def terminal_cache_size(self) -> int:
        return len(self._terminal)

    def purge_terminal_cache(self) -> int:
        return self._terminal.purge()


def _confirms(read_value, target, tolerance: float, spec) -> bool:
    """Vrai si la valeur relue confirme la cible, selon le type du role.

    - entier : egalite exacte (`read == target`) ;
    - flottant : `abs(read - target) <= confirm_tolerance`.

    `read_value` est fini par construction (`ReadResult` OK). La comparaison
    n'applique aucun clamp ni valeur par defaut.
    """
    from boilerack.core.profile import ValueType

    if read_value is None:
        return False
    if spec.type is ValueType.INTEGER:
        return read_value == target
    return abs(read_value - target) <= tolerance
