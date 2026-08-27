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
  `UNUSABLE_OUTPUT`, `TRANSPORT_ERROR` -- ET TOUT STATUT IMPREVU -- peuvent
  avoir emis l'ecriture -> jamais `bridge_unavailable`, relecture puis
  `applied`/`timeout`. Seul un statut EXPLICITEMENT demontre « non emis » peut
  produire `bridge_unavailable`.
- Publication de `accepted` (arbitrage 2, fail-closed) : si l'ACK `accepted`
  echoue de facon ETABLIE avant l'ecriture, la commande n'est PAS executee.
- Un echec de publication ne transforme jamais une commande en succes ; le
  verdict est decide par le fait physique, la livraison MQTT est un fait
  distinct, sans retry automatique.
- CONCLUSION GARANTIE : toute transaction admise (identifiant reserve dans
  `in_flight`) produit un verdict terminal, met ce verdict en cache AVANT toute
  publication, et libere `in_flight`. Aucune exception de transport n'abandonne
  une transaction en vol. La frontiere avant/apres invocation de l'ecriture est
  EXPLICITE (`write_invoked`), jamais deduite implicitement d'une exception.
"""

from __future__ import annotations

import logging

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

# Observabilite minimale (C4) : les `except Exception` conservateurs ci-dessous
# convertissent une erreur en verdict prudent SANS jamais fabriquer un faux
# succes. On les rend VISIBLES via `logging`, sans changer aucun verdict. Aucun
# secret ni payload complet n'est journalise : uniquement `request_id`, role,
# etape et TYPE d'exception. La journalisation est capturable en test (`caplog`).
logger = logging.getLogger(__name__)

# Statuts d'ecriture qui prouvent, de facon TYPEE, qu'aucune ecriture n'a ete
# emise. Eux seuls autorisent `bridge_unavailable`. Tout autre statut connu
# (`OK`, `TIMEOUT`, `UNUSABLE_OUTPUT`, `TRANSPORT_ERROR`) OU IMPREVU est traite
# comme « potentiellement emis » : relecture puis `applied`/`timeout`.
_PROVEN_NOT_EMITTED = frozenset({TransportStatus.DAEMON_UNREACHABLE})

# Statuts « potentiellement emis » explicitement cartographies (les six statuts
# actuels). Conserve a titre documentaire : le code ne s'appuie PAS sur cette
# liste pour decider (un statut absent est traite comme potentiellement emis),
# afin qu'un futur statut ne bascule jamais par defaut vers « non emis ».
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
        # `submit` rend `Ack | None`, la ou `MessageHandler` est typé
        # `Callable[[Message], None]` : l'ecart est DELIBERE. W1 §11.4 interdit
        # d'y toucher — « MUST NOT modifier la signature de `MessageHandler`
        # pour la recuperer » — la valeur rendue etant ignoree par le transport,
        # l'acquittement passant par MQTT et jamais par un retour d'appel.
        target.set_message_handler(self.submit)  # type: ignore[arg-type]

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
                # Rejeu du verdict terminal, SANS reexecution. Publication au
                # mieux : le verdict est deja en cache, un echec MQTT ne le perd
                # pas et ne fait pas remonter d'exception.
                self._publish_terminal(replayed, self._topic_role(payload))
                return replayed
            if self._in_flight.contains(request_id):
                # Doublon en vol : aucun second travail, pas de nouveau accepted ;
                # le verdict de la transaction initiale suffira.
                return None

        result = validate(payload, self._profile, self._clock.now())

        if isinstance(result, Rejection):
            # Rejet d'admission : aucun `in_flight` n'a ete reserve. On met le
            # verdict en cache (si canonique) AVANT de publier au mieux.
            ack = Ack.rejected(request_id, result.reason)
            if canonical:
                self._terminal.put(request_id, ack)
            self._publish_terminal(ack, self._topic_role(payload))
            return ack

        return self._admit(result)

    def _admit(self, validated: ValidatedCommand) -> Ack:
        request_id = validated.command.request_id
        role = validated.spec.role

        # Saturation : ne PAS reserver l'identifiant, pas de `accepted`.
        # `queue_full` est un verdict terminal, mis en cache comme tout verdict.
        if self._queue.depth >= self._queue.capacity:
            return self._conclude(
                request_id, Ack.rejected(request_id, Reason.QUEUE_FULL), role
            )

        # Place disponible : reserver, publier `accepted`, PUIS mettre en file.
        # A partir de la reservation, TOUT chemin de sortie passe par un verdict
        # terminal + liberation de `in_flight` : le `try/except` garantit qu'une
        # exception de transport (p. ex. MQTT injoignable a la publication de
        # `accepted`) ne laisse jamais l'identifiant coince en vol.
        self._in_flight.reserve(request_id)
        try:
            accepted = Ack.accepted(request_id)
            handle = self._publish_ack(accepted, role)

            # Arbitrage 2 (fail-closed) : echec ETABLI de `accepted` avant
            # ecriture. Un handle simplement demande (ni confirme ni echoue)
            # n'est PAS un echec : on ne bloque pas en attente du PUBACK.
            if handle is not None and handle.failed:
                return self._conclude(
                    request_id,
                    Ack.rejected(request_id, Reason.BRIDGE_UNAVAILABLE),
                    role,
                )

            self._queue.put(validated)
            return accepted
        except Exception as exc:
            # Exception apres reservation mais AVANT toute invocation d'ecriture
            # (la mise en file n'ecrit rien) : la commande n'est pas executee.
            # Verdict fail-closed, `in_flight` libere, aucune ecriture physique.
            logger.warning(
                "exception a l'admission apres reservation, fail-closed "
                "bridge_unavailable request_id=%s role=%s exc=%s",
                request_id,
                role,
                type(exc).__name__,
            )
            return self._conclude(
                request_id,
                Ack.rejected(request_id, Reason.BRIDGE_UNAVAILABLE),
                role,
            )

    # -- execution -----------------------------------------------------------

    def process_next(self) -> Ack | None:
        """Execute la prochaine commande admise, ou `None` si la file est vide."""
        try:
            validated = self._queue.get()
        except QueueEmpty:
            return None

        request_id = validated.command.request_id
        role = validated.spec.role

        # `_run_transaction` ne leve JAMAIS : il renvoie toujours un verdict
        # terminal, y compris sur exception de transport. La conclusion (cache +
        # liberation de `in_flight` + publication au mieux) est centralisee ici.
        verdict = self._run_transaction(validated)
        return self._conclude(request_id, verdict, role)

    def drain(self) -> list[Ack]:
        """Execute toutes les commandes admises en attente, dans l'ordre FIFO."""
        verdicts: list[Ack] = []
        while True:
            ack = self.process_next()
            if ack is None:
                break
            verdicts.append(ack)
        return verdicts

    def _run_transaction(self, validated: ValidatedCommand) -> Ack:
        """Deroule une transaction admise et renvoie TOUJOURS un verdict terminal.

        Ne leve jamais : toute exception de transport est convertie en verdict,
        selon la frontiere EXPLICITE `write_invoked` :

        - exception AVANT invocation de l'ecriture  -> `bridge_unavailable`
          (non emise) ;
        - exception A PARTIR de l'invocation (ecriture ou confirmation) ->
          ecriture consideree comme POTENTIELLEMENT emise : on tente la
          confirmation, `applied` si elle confirme, sinon `timeout`.

        Une SEULE invocation d'ecriture par transaction, jamais de retry.
        """
        request_id = validated.command.request_id
        spec = validated.spec

        # Revalidation de l'expiration IMMEDIATEMENT avant l'ecriture. Aucune
        # ecriture n'est encore invoquee : une commande expiree ici est rejetee.
        if self._clock.now() >= validated.command.expires_at:
            return Ack.rejected(request_id, Reason.EXPIRED)

        assert spec.write is not None  # garanti : un role lecture seule est rejete

        write_invoked = False
        try:
            write_command = spec.write
            write_value = float(validated.target)
            # --- FRONTIERE : tout ce qui suit peut avoir sollicite la chaudiere.
            write_invoked = True
            write = self._vclient.write(write_command, write_value)
            status = write.status

            if status in _PROVEN_NOT_EMITTED:
                # Preuve TYPEE qu'aucune ecriture n'a ete emise.
                return Ack.rejected(request_id, Reason.BRIDGE_UNAVAILABLE)
            if status is TransportStatus.UNKNOWN_COMMAND:
                # Defaut permanent : commande declaree non reconnue par le transport.
                return Ack.rejected(request_id, Reason.UNSUPPORTED_COMMAND)
            # Tout autre statut connu (`OK`, `TIMEOUT`, `UNUSABLE_OUTPUT`,
            # `TRANSPORT_ERROR`) OU IMPREVU : potentiellement emis -> relecture.
            # On ne pretend jamais l'absence d'ecriture par defaut.
            return self._confirm(validated)
        except Exception as exc:
            if not write_invoked:
                # Exception avant l'invocation de l'ecriture : rien n'a ete emis.
                logger.warning(
                    "exception AVANT invocation d'ecriture, non emise -> "
                    "bridge_unavailable request_id=%s role=%s exc=%s",
                    request_id,
                    spec.role,
                    type(exc).__name__,
                )
                return Ack.rejected(request_id, Reason.BRIDGE_UNAVAILABLE)
            # Exception A PARTIR de l'invocation : l'ecriture a pu etre emise. On
            # ne la rejoue pas ; on tente une confirmation. Si meme la
            # confirmation echoue, verdict `timeout` (jamais `bridge_unavailable`).
            logger.warning(
                "exception A PARTIR de l'invocation d'ecriture (potentiellement "
                "emise), tentative de confirmation request_id=%s role=%s exc=%s",
                request_id,
                spec.role,
                type(exc).__name__,
            )
            try:
                return self._confirm(validated)
            except Exception as exc2:
                logger.warning(
                    "confirmation en echec apres exception d'ecriture -> timeout "
                    "request_id=%s role=%s exc=%s",
                    request_id,
                    spec.role,
                    type(exc2).__name__,
                )
                return Ack.timeout(request_id)

    def _confirm(self, validated: ValidatedCommand) -> Ack:
        request_id = validated.command.request_id
        spec = validated.spec
        target = validated.target

        deadline = self._clock.monotonic() + self._confirm_budget_s
        while True:
            try:
                read = self._vclient.read(spec.read)
                # `ReadResult` durci : OK implique une valeur finie ; une lecture
                # non OK (y compris sortie NaN/inexploitable) ne confirme rien.
                confirmed = read.ok and _confirms(
                    read.value, target, spec.confirm_tolerance, spec
                )
            except Exception as exc:
                # Une lecture qui echoue ne confirme rien : on n'abandonne pas la
                # confirmation, on epuise le budget avant de conclure `timeout`.
                logger.warning(
                    "lecture de confirmation en echec (ne confirme pas) "
                    "request_id=%s role=%s exc=%s",
                    request_id,
                    spec.role,
                    type(exc).__name__,
                )
                confirmed = False
            if confirmed:
                return Ack.applied(request_id)
            if self._clock.monotonic() >= deadline:
                return Ack.timeout(request_id)
            self._clock.sleep(self._confirm_interval_s)

    # -- cloture et publication ---------------------------------------------

    def _conclude(self, request_id: str, verdict: Ack, role: str) -> Ack:
        """Conclut une transaction : cache AVANT publication, `in_flight` libere.

        Le verdict est decide par le FAIT PHYSIQUE. On le memorise puis on libere
        l'identifiant AVANT toute tentative de publication : une livraison MQTT
        ratee -- echec etabli OU exception -- ne change ni ne perd le verdict, et
        n'est jamais retentee (pas de retry MQTT en v1).

        `in_flight.release` est un `discard` : l'appeler pour un identifiant non
        reserve (rejet `queue_full`) est un no-op sans effet de bord.

        INVARIANT (contre-verification C3, reserve theorique) : avec les
        implementations memoire actuelles, `terminal_cache.put` (verdict toujours
        terminal ici) et `in_flight.release` (`set.discard`) NE LEVENT PAS. Ce
        flux n'est donc pas enveloppe d'un `try/except` qui pourrait masquer une
        corruption interne du cache. Une eventuelle levee ici signalerait un
        defaut de programmation, a traiter comme tel, pas a absorber.
        """
        self._terminal.put(request_id, verdict)
        self._in_flight.release(request_id)
        self._publish_terminal(verdict, role)
        return verdict

    def _publish_terminal(self, ack: Ack, role: str) -> None:
        """Publie un verdict terminal AU MIEUX : toute erreur est absorbee.

        Le verdict est deja en cache avant cet appel : ni un echec etabli de
        publication, ni une exception de transport ne doivent le perdre ni le
        faire remonter au demandeur.
        """
        try:
            self._publish_ack(ack, role)
        except Exception as exc:
            # Verdict deja en cache : une publication ratee ne le perd pas et ne
            # remonte pas. On la rend visible sans changer le verdict.
            logger.warning(
                "publication terminale au mieux en echec, verdict conserve "
                "request_id=%s role=%s exc=%s",
                ack.request_id,
                role,
                type(exc).__name__,
            )

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
