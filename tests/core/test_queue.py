"""Tests de la file bornee comme premier consommateur reel.

Admission FIFO, rejet explicite a saturation, aucune perte silencieuse, et
aucun `accepted` pour une commande refusee par saturation.
"""

from __future__ import annotations

from boilerack.core import Reason
from boilerack.core.ack import AckStatus
from boilerack.transport.vclient import WriteResult
from boilerack.transport import TransportStatus
from support import Harness, message, payload, rid


def _program_ok(h: Harness, role: str, read_cmd: str, write_cmd: str, value) -> None:
    h.vclient.expect_write(write_cmd, float(value), result=WriteResult(TransportStatus.OK))
    h.vclient.expect_read(read_cmd, returns=float(value))


def test_admission_met_en_file_et_publie_accepted() -> None:
    h = Harness()
    ack = h.core.submit(message(payload(rid(1), "mode", 1)))
    assert ack.status is AckStatus.ACCEPTED
    assert h.core.queue_depth == 1
    assert h.core.in_flight_count == 1
    assert h.ack_payloads()[-1]["status"] == "accepted"


def test_saturation_rejette_queue_full() -> None:
    h = Harness(queue_capacity=2)
    a = h.core.submit(message(payload(rid(1), "mode", 1)))
    b = h.core.submit(message(payload(rid(2), "mode", 2)))
    c = h.core.submit(message(payload(rid(3), "mode", 3)))
    assert a.status is AckStatus.ACCEPTED
    assert b.status is AckStatus.ACCEPTED
    assert c.status is AckStatus.REJECTED
    assert c.reason is Reason.QUEUE_FULL


def test_pas_d_accepted_si_queue_full() -> None:
    h = Harness(queue_capacity=1)
    h.core.submit(message(payload(rid(1), "mode", 1)))
    h.core.submit(message(payload(rid(2), "mode", 2)))  # sature
    statuses = [a["status"] for a in h.ack_payloads()]
    # Un seul accepted (le premier) ; le second est un rejet queue_full.
    assert statuses.count("accepted") == 1
    assert statuses[-1] == "rejected"
    # L'identifiant refuse n'entre pas dans in_flight.
    assert h.core.in_flight_count == 1


def test_fifo_a_l_execution() -> None:
    h = Harness(queue_capacity=3)
    for n in (1, 2, 3):
        h.core.submit(message(payload(rid(n), "mode", n)))
    # Programme les writes/reads dans l'ordre FIFO attendu.
    for n in (1, 2, 3):
        _program_ok(h, "mode", "get_mode", "set_mode", n)

    verdicts = h.core.drain()
    assert [v.status for v in verdicts] == [AckStatus.APPLIED] * 3
    # Les ecritures ont eu lieu dans l'ordre 1, 2, 3.
    assert [c.value for c in h.write_calls()] == [1.0, 2.0, 3.0]
    h.vclient.assert_all_consumed()


def test_profondeur_maximale_observee() -> None:
    h = Harness(queue_capacity=5)
    for n in (1, 2, 3):
        h.core.submit(message(payload(rid(n), "mode", n)))
    assert h.core.queue_depth == 3
    for n in (1, 2, 3):
        _program_ok(h, "mode", "get_mode", "set_mode", n)
    h.core.drain()
    assert h.core.queue_depth == 0
    assert h.core.max_queue_depth == 3
