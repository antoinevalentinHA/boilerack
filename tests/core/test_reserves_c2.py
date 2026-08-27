"""Tests des reserves C2 resolues en C3.

- durcissement de `ReadResult` (OK <=> valeur finie ; non-OK <=> None) ;
- gardes `NaN` / `+Inf` / `-Inf` sur les horloges ;
- voie d'entree MQTT (handler de message) reellement branchee au coeur.
"""

from __future__ import annotations


import pytest

from boilerack.clock import SystemClock
from boilerack.testing import VirtualClock
from boilerack.transport import TransportStatus
from boilerack.transport.vclient import ReadResult
from support import START, Harness, message, payload, rid


# -- ReadResult durci ----------------------------------------------------------

def test_readresult_ok_exige_valeur_finie() -> None:
    assert ReadResult(TransportStatus.OK, value=21.0).value == 21.0
    with pytest.raises(ValueError, match="non nulle"):
        ReadResult(TransportStatus.OK, value=None)
    with pytest.raises(ValueError, match="finie"):
        ReadResult(TransportStatus.OK, value=float("nan"))
    with pytest.raises(ValueError, match="finie"):
        ReadResult(TransportStatus.OK, value=float("inf"))


def test_readresult_non_ok_exige_value_none() -> None:
    assert ReadResult(TransportStatus.TIMEOUT).value is None
    assert ReadResult(TransportStatus.UNUSABLE_OUTPUT, raw="junk").value is None
    with pytest.raises(ValueError, match="value is None"):
        ReadResult(TransportStatus.TIMEOUT, value=5.0)


# -- gardes d'horloge ----------------------------------------------------------

def test_virtual_clock_refuse_nan_et_infinis() -> None:
    clock = VirtualClock(START)
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            clock.advance(bad)
        with pytest.raises(ValueError):
            clock.sleep(bad)
    assert clock.sleeps == ()  # rien enregistre sur refus


def test_virtual_clock_refuse_monotonic_start_non_fini() -> None:
    with pytest.raises(ValueError, match="fini"):
        VirtualClock(START, monotonic_start=float("nan"))


def test_system_clock_refuse_nan_et_infini() -> None:
    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            SystemClock().sleep(bad)


# -- voie d'entree MQTT --------------------------------------------------------

def test_handler_de_message_branche_l_admission() -> None:
    h = Harness()
    h.core.attach()  # enregistre core.submit comme handler
    # Un message livre par le transport declenche l'admission.
    h.mqtt.deliver(message(payload(rid(1), "mode", 2)))
    assert h.core.in_flight_count == 1
    assert h.ack_payloads()[-1]["status"] == "accepted"


def test_message_dup_est_admis_par_request_id() -> None:
    # Le drapeau `dup` n'altere pas la logique : la dedup se fait par request_id.
    h = Harness()
    h.core.attach()
    h.mqtt.deliver(message(payload(rid(1), "mode", 2), dup=True))
    assert h.core.in_flight_count == 1
