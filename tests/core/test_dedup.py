"""Tests de deduplication : registre in_flight et cache terminal volatil."""

from __future__ import annotations

import pytest

from boilerack.core import TerminalCache
from boilerack.core.ack import Ack, AckStatus
from boilerack.transport.vclient import ReadResult, WriteResult
from boilerack.transport import TransportStatus
from support import START, Harness, message, payload, rid


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


def test_accepted_jamais_mis_en_cache() -> None:
    h = Harness()
    h.core.submit(message(payload(rid(1), "mode", 1)))  # accepted, non traite
    assert h.core.terminal_cache_size == 0  # accepted n'est pas mis en cache
    assert h.core.in_flight_count == 1

    # Et le cache refuse explicitement un ACK non terminal.
    cache = TerminalCache(h.clock)
    with pytest.raises(ValueError, match="non terminal"):
        cache.put(rid(2), Ack.accepted(rid(2)))
