"""Conclusion transactionnelle garantie : exceptions, frontiere d'ecriture, cache.

Ces tests verrouillent les garanties de surete durcies apres l'audit C3 :

- toute transaction admise produit un verdict terminal, meme sur exception de
  transport (aucune transaction abandonnee, aucun `in_flight` qui fuit) ;
- la frontiere AVANT / A PARTIR de l'invocation de l'ecriture decide la
  classification (`bridge_unavailable` vs relecture) ;
- le verdict est mis en cache AVANT toute publication (une publication qui leve
  ne perd pas le verdict) ;
- pour un role entier, la confirmation reste une egalite STRICTE, meme si une
  `confirm_tolerance` non nulle est declaree ;
- le TTL du cache terminal n'est PAS glissant.

Les doubles de transport de ce fichier peuvent LEVER, ce que les doubles C2
programmables ne permettent pas d'exprimer proprement ; ils restent en memoire,
sans reseau, sans Paho, sans I/O reelle.
"""

from __future__ import annotations


from boilerack.clock import Clock
from boilerack.core import TransactionalCore
from boilerack.core.ack import Ack, AckStatus, Reason, ReasonClass
from boilerack.core.dedup import TerminalCache
from boilerack.core.profile import CommandSpec, Profile, ValueType
from boilerack.testing import VirtualClock, build_fake_profile
from boilerack.transport.mqtt import Message, NotConnectedError
from boilerack.transport.vclient import ReadResult, TransportStatus, WriteResult
from support import START, message, payload, rid


# -- doubles de transport pouvant lever ---------------------------------------

class _MqttRaisingOnNth:
    """Double MQTT minimal qui LEVE sur certaines publications (1-based)."""

    def __init__(self, raise_on: set[int] | None = None) -> None:
        self._raise_on = set(raise_on or ())
        self._n = 0
        self.published: list[tuple[str, bytes]] = []
        self._handler = None

    def connect(self) -> None:  # pragma: no cover - non utilise ici
        pass

    def disconnect(self) -> None:  # pragma: no cover
        pass

    def subscribe(self, topic: str, qos: int = 0) -> None:  # pragma: no cover
        pass

    def set_message_handler(self, handler) -> None:
        self._handler = handler

    def publish(self, topic: str, payload: bytes, qos: int = 0, retain: bool = False):
        self._n += 1
        if self._n in self._raise_on:
            raise NotConnectedError(f"publication #{self._n} indisponible")
        self.published.append((topic, payload))
        return None  # handle non observe ici (ni confirme ni echoue)


class _ScriptedVClient:
    """Double transport dont `write`/`read` peuvent lever ou renvoyer un resultat.

    Compte les invocations pour prouver « une seule ecriture » et « pas de
    double execution ».
    """

    def __init__(
        self,
        *,
        write_raises: BaseException | None = None,
        write_result: WriteResult | None = None,
        reads: list | None = None,
    ) -> None:
        self._write_raises = write_raises
        self._write_result = write_result or WriteResult(TransportStatus.OK)
        self._reads = list(reads or [])
        self.writes = 0
        self.reads_done = 0

    def write(self, command: str, value: float) -> WriteResult:
        self.writes += 1
        if self._write_raises is not None:
            raise self._write_raises
        return self._write_result

    def read(self, command: str) -> ReadResult:
        self.reads_done += 1
        if not self._reads:
            raise RuntimeError("lecture non programmee")
        item = self._reads.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def _core(clock: Clock, vclient, mqtt, profile: Profile | None = None, **kw) -> TransactionalCore:
    return TransactionalCore(
        clock=clock,
        vclient=vclient,
        mqtt=mqtt,
        profile=profile if profile is not None else build_fake_profile(),
        **kw,
    )


def _cmd(role: str = "temp_consigne", value=21.0, request_id=None) -> Message:
    return message(payload(request_id or rid(1), role, value))


# -- 1. exception a l'admission (avant toute ecriture) ------------------------

def test_exception_publication_accepted_conclut_fail_closed() -> None:
    clock = VirtualClock(START)
    vc = _ScriptedVClient()
    mqtt = _MqttRaisingOnNth(raise_on={1})  # la publication de `accepted` leve
    core = _core(clock, vc, mqtt)

    verdict = core.submit(_cmd())

    # Verdict terminal produit, pas d'exception qui traverse le coeur.
    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.BRIDGE_UNAVAILABLE
    assert verdict.reason_class is ReasonClass.TRANSIENT
    # Aucune ecriture physique, rien en file, `in_flight` libere.
    assert vc.writes == 0
    assert core.queue_depth == 0
    assert core.in_flight_count == 0
    # Verdict mis en cache : un doublon le rejoue sans re-executer.
    replay = core.submit(_cmd())
    assert replay.status is AckStatus.REJECTED
    assert replay.reason is Reason.BRIDGE_UNAVAILABLE
    assert vc.writes == 0


# -- 2. exception a l'invocation de l'ecriture (potentiellement emise) --------

def test_exception_pendant_write_est_potentiellement_emise_puis_confirmee() -> None:
    clock = VirtualClock(START)
    # `write` leve : au-dela de la frontiere, l'ecriture PEUT avoir ete emise.
    vc = _ScriptedVClient(
        write_raises=RuntimeError("transport casse pendant l'ecriture"),
        reads=[ReadResult(TransportStatus.OK, value=21.0)],  # relecture conforme
    )
    mqtt = _MqttRaisingOnNth()
    core = _core(clock, vc, mqtt)

    core.submit(_cmd(value=21.0))
    verdict = core.process_next()

    # Potentiellement emise -> relecture conforme -> applied (jamais bridge_unavailable).
    assert verdict.status is AckStatus.APPLIED
    assert vc.writes == 1            # une seule invocation d'ecriture
    assert vc.reads_done == 1        # confirmee des la premiere relecture
    assert core.in_flight_count == 0
    assert core.terminal_cache_size == 1


def test_exception_pendant_write_sans_confirmation_donne_timeout() -> None:
    clock = VirtualClock(START)
    vc = _ScriptedVClient(
        write_raises=RuntimeError("boom"),
        reads=[
            ReadResult(TransportStatus.OK, value=20.0),  # hors tolerance
            ReadResult(TransportStatus.OK, value=20.0),
            ReadResult(TransportStatus.OK, value=20.0),
        ],
    )
    core = _core(clock, vc, _MqttRaisingOnNth(), confirm_budget_s=1.0, confirm_interval_s=0.5)

    core.submit(_cmd(value=21.0))
    verdict = core.process_next()

    # Ecriture potentiellement emise mais jamais confirmee -> timeout, PAS rejected.
    assert verdict.status is AckStatus.TIMEOUT
    assert vc.writes == 1
    assert core.in_flight_count == 0


# -- 3. exception de lecture pendant la confirmation --------------------------

def test_exception_de_lecture_ne_confirme_pas_mais_n_abandonne_pas() -> None:
    clock = VirtualClock(START)
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[
            RuntimeError("lecture indisponible"),          # leve : ne confirme pas
            ReadResult(TransportStatus.OK, value=21.0),    # puis conforme
        ],
    )
    core = _core(clock, vc, _MqttRaisingOnNth(), confirm_budget_s=5.0, confirm_interval_s=0.5)

    core.submit(_cmd(value=21.0))
    verdict = core.process_next()

    assert verdict.status is AckStatus.APPLIED
    assert vc.writes == 1
    assert vc.reads_done == 2
    assert core.in_flight_count == 0


def test_exceptions_de_lecture_repetees_jusqu_au_budget_donnent_timeout() -> None:
    clock = VirtualClock(START)
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[RuntimeError("ko"), RuntimeError("ko"), RuntimeError("ko")],
    )
    core = _core(clock, vc, _MqttRaisingOnNth(), confirm_budget_s=1.0, confirm_interval_s=0.5)

    core.submit(_cmd(value=21.0))
    verdict = core.process_next()

    # Lectures qui levent jusqu'a epuisement du budget -> timeout borne, sans
    # boucle infinie ni exception qui traverse le coeur.
    assert verdict.status is AckStatus.TIMEOUT
    assert vc.writes == 1
    assert vc.reads_done == 3  # relectures a t=0, 0.5, 1.0
    assert core.in_flight_count == 0


# -- 4. cache AVANT publication du verdict terminal ---------------------------

def test_verdict_mis_en_cache_meme_si_la_publication_terminale_leve() -> None:
    clock = VirtualClock(START)
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[ReadResult(TransportStatus.OK, value=21.0)],
    )
    # publication #1 = accepted (OK) ; #2 = verdict terminal (LEVE).
    mqtt = _MqttRaisingOnNth(raise_on={2})
    core = _core(clock, vc, mqtt)

    core.submit(_cmd(value=21.0))
    verdict = core.process_next()

    # La publication du verdict a leve, mais le verdict est decide et CONSERVE.
    assert verdict.status is AckStatus.APPLIED
    assert core.terminal_cache_size == 1
    assert core.in_flight_count == 0
    # Doublon rejoue depuis le cache, sans reexecution.
    replay = core.submit(_cmd(value=21.0))
    assert replay.status is AckStatus.APPLIED
    assert vc.writes == 1  # aucune seconde ecriture


# -- 5. entier + tolerance non nulle : egalite STRICTE ------------------------

def _integer_tolerant_profile() -> Profile:
    spec = CommandSpec(
        role="mode",
        read="get_mode",
        write="set_mode",
        type=ValueType.INTEGER,
        min=0,
        max=10,
        step=1,
        confirm_tolerance=2.0,  # non nulle : ne doit JAMAIS relacher l'egalite entiere
        idempotent=True,
        bounds_source="profil de test — tolerance entiere volontairement non nulle",
    )
    return Profile(name="int-tol", commands={"mode": spec})


def test_entier_ignore_la_tolerance_ecart_de_1_ne_confirme_pas() -> None:
    clock = VirtualClock(START)
    prof = _integer_tolerant_profile()
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[ReadResult(TransportStatus.OK, value=5.0)] * 3,  # cible 4, ecart 1
    )
    core = _core(clock, vc, _MqttRaisingOnNth(), prof, confirm_budget_s=1.0, confirm_interval_s=0.5)

    core.submit(message(payload(rid(1), "mode", 4)))
    verdict = core.process_next()

    # Malgre confirm_tolerance=2.0, un ecart de 1 sur un entier ne confirme PAS.
    assert verdict.status is AckStatus.TIMEOUT


def test_entier_confirme_uniquement_sur_egalite_exacte() -> None:
    clock = VirtualClock(START)
    prof = _integer_tolerant_profile()
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[ReadResult(TransportStatus.OK, value=4.0)],  # cible 4, exact
    )
    core = _core(clock, vc, _MqttRaisingOnNth(), prof)

    core.submit(message(payload(rid(1), "mode", 4)))
    verdict = core.process_next()

    assert verdict.status is AckStatus.APPLIED


# -- 6. TTL du cache terminal : NON glissant ----------------------------------

def test_ttl_non_glissant() -> None:
    clock = VirtualClock(START)
    cache = TerminalCache(clock, ttl_seconds=30.0)
    cache.put(rid(1), Ack.applied(rid(1)))  # deadline = monotonic(0) + 30 = 30

    clock.advance(20)  # t=20 < 30 : encore valide
    assert cache.get(rid(1)) is not None  # lecture NE prolonge PAS le TTL

    clock.advance(11)  # t=31 > 30 : expire a la deadline INITIALE, pas 20+30
    assert cache.get(rid(1)) is None


def test_ttl_non_glissant_via_rejeu_du_coeur() -> None:
    # Meme garantie observee de bout en bout : rejouer un verdict ne repousse pas
    # son expiration.
    clock = VirtualClock(START)
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[ReadResult(TransportStatus.OK, value=21.0)],
    )
    core = _core(clock, vc, _MqttRaisingOnNth(), terminal_ttl_s=30.0)

    core.submit(_cmd(value=21.0))
    core.process_next()  # verdict applied cache a t=0, deadline 30

    clock.advance(20)
    assert core.submit(_cmd(value=21.0)).status is AckStatus.APPLIED  # rejeu, t=20
    clock.advance(11)  # t=31 : au-dela de la deadline initiale
    # Le cache a expire ; le meme identifiant est de nouveau admis (pas de rejeu).
    # (payload redate pour rester valide apres l'avance du temps.)
    reack = core.submit(message(payload(rid(1), "temp_consigne", 21.0, start=clock.now())))
    assert reack.status is AckStatus.ACCEPTED
