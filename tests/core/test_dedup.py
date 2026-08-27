"""Tests de deduplication : registre in_flight et cache terminal volatil."""

from __future__ import annotations

import pytest

from boilerack.core import TerminalCache
from boilerack.core.ack import Ack, AckStatus, Reason
from boilerack.transport.vclient import WriteResult
from boilerack.transport import TransportStatus
from support import Harness, message, payload, rid


def _apply_ok(h: Harness, request_id: str, value=1) -> None:
    h.vclient.expect_write("set_mode", float(value), result=WriteResult(TransportStatus.OK))
    h.vclient.expect_read("get_mode", returns=float(value))
    h.core.submit(message(payload(request_id, "mode", value)))
    h.core.process_next()


def test_doublon_terminal_rejoue_sans_reexecution() -> None:
    h = Harness()
    _apply_ok(h, rid(1), 1)
    assert h.write_calls() and len(h.write_calls()) == 1
    h.vclient.assert_all_consumed()  # plus aucune interaction programmee

    replayed = h.core.submit(message(payload(rid(1), "mode", 1)))
    assert replayed.status is AckStatus.APPLIED
    # Aucune ecriture/lecture supplementaire : rejeu pur.
    assert len(h.write_calls()) == 1


def test_doublon_pendant_in_flight_supprime() -> None:
    h = Harness()
    accepted = h.core.submit(message(payload(rid(1), "mode", 1)))
    assert accepted.status is AckStatus.ACCEPTED
    acks_avant = len(h.mqtt.publications)

    # Doublon pendant que la transaction initiale est encore en file.
    duplicate = h.core.submit(message(payload(rid(1), "mode", 1)))
    assert duplicate is None
    # Aucun nouvel ACK (pas de second accepted).
    assert len(h.mqtt.publications) == acks_avant
    assert h.core.in_flight_count == 1


def test_expiration_du_ttl_reautorise_l_execution() -> None:
    h = Harness(terminal_ttl_s=60.0)
    _apply_ok(h, rid(1), 1)

    h.clock.advance(61)  # depasse le TTL du cache terminal

    # Le meme identifiant est de nouveau admis (pas de rejeu) : il faut donc
    # reprogrammer une execution complete. Le payload est date sur l'instant
    # courant pour rester valide apres l'avance du temps.
    h.vclient.expect_write("set_mode", 1.0, result=WriteResult(TransportStatus.OK))
    h.vclient.expect_read("get_mode", returns=1.0)
    reack = h.core.submit(message(payload(rid(1), "mode", 1, start=h.clock.now())))
    assert reack.status is AckStatus.ACCEPTED
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED
    assert len(h.write_calls()) == 2  # reexecutee


def test_purge_deterministe() -> None:
    h = Harness(terminal_ttl_s=30.0)
    cache = TerminalCache(h.clock, ttl_seconds=30.0)
    cache.put(rid(1), Ack.applied(rid(1)))
    cache.put(rid(2), Ack.timeout(rid(2)))
    assert len(cache) == 2
    h.clock.advance(31)
    assert cache.purge() == 2
    assert len(cache) == 0


def test_aucune_memoire_apres_nouvelle_instance() -> None:
    h1 = Harness()
    _apply_ok(h1, rid(1), 1)

    # Nouvelle instance = memoire vierge : pas de rejeu, admission normale.
    h2 = Harness()
    ack = h2.core.submit(message(payload(rid(1), "mode", 1)))
    assert ack.status is AckStatus.ACCEPTED


def test_rejet_queue_full_est_mis_en_cache_et_rejoue() -> None:
    # POLITIQUE RATIFIEE : TOUT verdict terminal est mis en cache pendant le TTL,
    # y compris les rejets `transient`. Un meme `request_id` designe la meme
    # transaction et rejoue le meme verdict ; une nouvelle tentative apres une
    # cause transitoire doit utiliser un NOUVEAU `request_id`.
    h = Harness(queue_capacity=1)
    h.core.submit(message(payload(rid(1), "mode", 1)))       # occupe la file
    full = h.core.submit(message(payload(rid(2), "mode", 2)))  # sature
    assert full.status is AckStatus.REJECTED
    assert full.reason is Reason.QUEUE_FULL
    assert h.core.terminal_cache_size == 1  # queue_full EST mis en cache

    # Meme identifiant : rejeu du meme verdict, aucune re-admission ni ecriture,
    # meme si la file s'est videe entre-temps.
    h.vclient.expect_write("set_mode", 1.0, result=WriteResult(TransportStatus.OK))
    h.vclient.expect_read("get_mode", returns=1.0)
    h.core.process_next()  # vide la file
    assert h.core.queue_depth == 0
    replay = h.core.submit(message(payload(rid(2), "mode", 2)))
    assert replay.status is AckStatus.REJECTED
    assert replay.reason is Reason.QUEUE_FULL  # rejoue, pas readmis


def test_rejet_bridge_unavailable_fail_closed_est_mis_en_cache_et_rejoue() -> None:
    # Idem pour le fail-closed sur echec etabli de `accepted` : verdict terminal
    # `bridge_unavailable`, mis en cache et rejoue a l'identique.
    h = Harness()
    h.mqtt.program_publish_failure(1)  # la publication de `accepted` echoue
    verdict = h.core.submit(message(payload(rid(1), "mode", 1)))
    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.BRIDGE_UNAVAILABLE
    assert h.core.terminal_cache_size == 1

    replay = h.core.submit(message(payload(rid(1), "mode", 1)))
    assert replay.status is AckStatus.REJECTED
    assert replay.reason is Reason.BRIDGE_UNAVAILABLE
    assert h.core.in_flight_count == 0


def test_accepted_jamais_mis_en_cache() -> None:
    h = Harness()
    h.core.submit(message(payload(rid(1), "mode", 1)))  # accepted, non traite
    assert h.core.terminal_cache_size == 0  # accepted n'est pas mis en cache
    assert h.core.in_flight_count == 1

    # Et le cache refuse explicitement un ACK non terminal.
    cache = TerminalCache(h.clock)
    with pytest.raises(ValueError, match="non terminal"):
        cache.put(rid(2), Ack.accepted(rid(2)))
