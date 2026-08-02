"""Tests du modele d'ACK, de sa serialisation et de sa publication."""

from __future__ import annotations

import json

import pytest

from boilerack.core import Reason, ReasonClass, ack_to_json
from boilerack.core.ack import Ack, AckStatus, ack_to_dict
from boilerack.transport import TransportStatus
from boilerack.transport.vclient import WriteResult
from support import Harness, message, payload, rid


# -- invariants du modele ------------------------------------------------------

def test_reason_et_classe_uniquement_pour_rejected() -> None:
    rejected = Ack.rejected("x", Reason.QUEUE_FULL)
    assert rejected.reason is Reason.QUEUE_FULL
    assert rejected.reason_class is ReasonClass.TRANSIENT


def test_pas_de_reason_sur_applied() -> None:
    ack = Ack.applied("x")
    assert ack.reason is None and ack.reason_class is None
    with pytest.raises(ValueError):
        Ack("x", AckStatus.APPLIED, reason=Reason.EXPIRED)


def test_pas_de_reason_sur_timeout() -> None:
    ack = Ack.timeout("x")
    assert ack.reason is None and ack.reason_class is None


def test_accepted_non_terminal_les_autres_terminaux() -> None:
    assert Ack.accepted("x").is_terminal is False
    assert Ack.applied("x").is_terminal is True
    assert Ack.timeout("x").is_terminal is True
    assert Ack.rejected("x", Reason.EXPIRED).is_terminal is True


def test_classe_incoherente_refusee() -> None:
    with pytest.raises(ValueError, match="reason_class"):
        Ack("x", AckStatus.REJECTED, reason=Reason.EXPIRED, reason_class=ReasonClass.PERMANENT)


def test_unsupported_command_est_permanent() -> None:
    ack = Ack.rejected("x", Reason.UNSUPPORTED_COMMAND)
    assert ack.reason_class is ReasonClass.PERMANENT


# -- serialisation -------------------------------------------------------------

def test_schema_exact_applied() -> None:
    data = json.loads(ack_to_json(Ack.applied("abc")))
    assert data == {"request_id": "abc", "status": "applied"}


def test_schema_exact_rejected() -> None:
    data = json.loads(ack_to_json(Ack.rejected("abc", Reason.EXPIRED)))
    assert data == {
        "request_id": "abc",
        "status": "rejected",
        "reason": "expired",
        "reason_class": "temporal",
    }


def test_json_compact_et_deterministe() -> None:
    raw = ack_to_json(Ack.rejected("abc", Reason.QUEUE_FULL))
    # Compact : aucun espace.
    assert b" " not in raw
    # Deterministe : deux serialisations identiques.
    assert raw == ack_to_json(Ack.rejected("abc", Reason.QUEUE_FULL))
    # UTF-8 valide, JSON standard strict.
    assert json.loads(raw.decode("utf-8"))["status"] == "rejected"


def test_serialisation_refuse_nan() -> None:
    # allow_nan=False : un flottant non fini serait rejete a la serialisation.
    with pytest.raises(ValueError):
        json.dumps({"x": float("inf")}, allow_nan=False)


def test_dict_terminal_sans_reason() -> None:
    assert ack_to_dict(Ack.timeout("x")) == {"request_id": "x", "status": "timeout"}


# -- publication ---------------------------------------------------------------

def test_ordre_accepted_puis_terminal_et_qos_retain() -> None:
    h = Harness()
    h.core.submit(message(payload(rid(1), "temp_consigne", 21.0)))
    h.vclient.expect_write("set_temp_consigne", 21.0, result=WriteResult(TransportStatus.OK))
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    h.core.process_next()

    statuses = [a["status"] for a in h.ack_payloads()]
    assert statuses == ["accepted", "applied"]  # accepted STRICTEMENT avant le terminal

    for handle in h.mqtt.publications:
        assert handle.publication.qos == 1
        assert handle.publication.retain is False


def test_doublon_terminal_rejoue_publie_le_verdict() -> None:
    h = Harness()
    h.core.submit(message(payload(rid(1), "temp_consigne", 21.0)))
    h.vclient.expect_write("set_temp_consigne", 21.0)
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    h.core.process_next()
    n_before = len(h.mqtt.publications)

    replayed = h.core.submit(message(payload(rid(1), "temp_consigne", 21.0)))
    assert replayed.status is AckStatus.APPLIED
    # Le rejeu republie le verdict (sans reexecution).
    assert len(h.mqtt.publications) == n_before + 1
    assert h.ack_payloads()[-1]["status"] == "applied"
    assert len(h.write_calls()) == 1
