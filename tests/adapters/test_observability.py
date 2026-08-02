"""Observabilite minimale (C4, section 9) : les `except Exception` conservateurs
de C3 sont rendus VISIBLES via `logging`, sans changer aucun verdict.

Ces tests verifient a la fois que le verdict est inchange ET qu'une trace
capturable est emise (jamais de secret ni de payload complet).
"""

from __future__ import annotations

import logging

from boilerack.core import TransactionalCore
from boilerack.core.ack import AckStatus, Reason
from boilerack.testing import VirtualClock, build_fake_profile
from boilerack.transport.mqtt import NotConnectedError
from boilerack.transport.vclient import ReadResult, TransportStatus, WriteResult
from adapter_support import START, command_message, command_payload, rid


class _MqttRaisingOnNth:
    def __init__(self, raise_on=None):
        self._raise_on = set(raise_on or ())
        self._n = 0
        self._handler = None

    def connect(self): ...
    def disconnect(self): ...
    def subscribe(self, *a, **k): ...
    def set_message_handler(self, h): self._handler = h

    def publish(self, topic, payload, qos=0, retain=False):
        self._n += 1
        if self._n in self._raise_on:
            raise NotConnectedError(f"pub #{self._n}")
        return None


class _ScriptedVClient:
    def __init__(self, *, write_raises=None, write_result=None, reads=None):
        self._write_raises = write_raises
        self._write_result = write_result or WriteResult(TransportStatus.OK)
        self._reads = list(reads or [])
        self.writes = 0

    def write(self, command, value):
        self.writes += 1
        if self._write_raises is not None:
            raise self._write_raises
        return self._write_result

    def read(self, command):
        if not self._reads:
            raise RuntimeError("lecture non programmee")
        item = self._reads.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def _core(vc, mqtt, **kw):
    return TransactionalCore(
        clock=VirtualClock(START), vclient=vc, mqtt=mqtt,
        profile=build_fake_profile(), **kw,
    )


def _cmd(role="temp_consigne", value=21.0, n=1):
    return command_message(command_payload(rid(n), role, value))


def test_exception_publication_accepted_journalisee(caplog) -> None:
    vc = _ScriptedVClient()
    core = _core(vc, _MqttRaisingOnNth(raise_on={1}))
    with caplog.at_level(logging.WARNING, logger="boilerack.core.engine"):
        verdict = core.submit(_cmd())
    assert verdict.reason is Reason.BRIDGE_UNAVAILABLE  # verdict inchange
    rec = [r for r in caplog.records if "admission" in r.message]
    assert rec and "bridge_unavailable" in rec[0].message
    # request_id present, aucun payload complet ni secret dans la trace
    assert rid(1) in rec[0].message
    assert "value" not in rec[0].message


def test_exception_pendant_write_journalisee_potentiellement_emise(caplog) -> None:
    vc = _ScriptedVClient(
        write_raises=RuntimeError("boom"),
        reads=[ReadResult(TransportStatus.OK, value=21.0)],
    )
    core = _core(vc, _MqttRaisingOnNth())
    core.submit(_cmd(value=21.0))
    with caplog.at_level(logging.WARNING, logger="boilerack.core.engine"):
        verdict = core.process_next()
    assert verdict.status is AckStatus.APPLIED  # verdict inchange
    assert any("A PARTIR de l'invocation" in r.message for r in caplog.records)


def test_lecture_de_confirmation_en_echec_journalisee(caplog) -> None:
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[RuntimeError("ko"), RuntimeError("ko"), RuntimeError("ko")],
    )
    core = _core(vc, _MqttRaisingOnNth(), confirm_budget_s=1.0, confirm_interval_s=0.5)
    core.submit(_cmd(value=21.0))
    with caplog.at_level(logging.WARNING, logger="boilerack.core.engine"):
        verdict = core.process_next()
    assert verdict.status is AckStatus.TIMEOUT  # verdict inchange
    assert any("confirmation en echec" in r.message for r in caplog.records)


def test_publication_terminale_en_echec_journalisee(caplog) -> None:
    vc = _ScriptedVClient(
        write_result=WriteResult(TransportStatus.OK),
        reads=[ReadResult(TransportStatus.OK, value=21.0)],
    )
    # pub #1 = accepted (OK), #2 = terminal (leve)
    core = _core(vc, _MqttRaisingOnNth(raise_on={2}))
    core.submit(_cmd(value=21.0))
    with caplog.at_level(logging.WARNING, logger="boilerack.core.engine"):
        verdict = core.process_next()
    assert verdict.status is AckStatus.APPLIED  # verdict conserve
    assert core.terminal_cache_size == 1
    assert any("publication terminale" in r.message for r in caplog.records)
