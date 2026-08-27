"""Fabriques partagees pour les tests du coeur transactionnel (C3).

Aucune attente reelle, aucun reseau : uniquement les doubles deterministes de
C2 et le profil factice.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from boilerack.core import TransactionalCore
from boilerack.testing import (
    FakeMqttClient,
    FakeVClient,
    VirtualClock,
    build_fake_profile,
)
from boilerack.transport import Message

START = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def rid(n: int) -> str:
    """UUID v4 canonique minuscule, deterministe et distinct par `n`."""
    return f"00000000-0000-4000-8000-{n:012d}"


def payload(
    request_id: str,
    role: str,
    value,
    *,
    ttl_seconds: float = 60.0,
    start: datetime = START,
    extra: dict | None = None,
    drop: tuple[str, ...] = (),
) -> bytes:
    """Construit un payload JSON de commande.

    `extra` ajoute des champs (pour tester le rejet de champ supplementaire) ;
    `drop` retire des champs obligatoires (pour tester un payload incomplet).
    """
    body = {
        "request_id": request_id,
        "ts": start.isoformat(),
        "expires_at": (start + timedelta(seconds=ttl_seconds)).isoformat(),
        "source": "test",
        "role": role,
        "value": value,
    }
    for field in drop:
        body.pop(field, None)
    if extra:
        body.update(extra)
    return json.dumps(body).encode("utf-8")


def message(
    payload_bytes: bytes, *, topic: str = "cmd/in", qos: int = 1, dup: bool = False
) -> Message:
    return Message(topic=topic, payload=payload_bytes, qos=qos, dup=dup)


class Harness:
    """Regroupe horloge, doubles, profil et coeur pour un test."""

    def __init__(
        self,
        *,
        queue_capacity: int = 16,
        confirm_budget_s: float = 5.0,
        confirm_interval_s: float = 0.5,
        terminal_ttl_s: float = 60.0,
        connected: bool = True,
    ) -> None:
        self.clock = VirtualClock(START)
        self.vclient = FakeVClient(self.clock)
        self.mqtt = FakeMqttClient()
        if connected:
            self.mqtt.connect()
        self.profile = build_fake_profile()
        self.core = TransactionalCore(
            clock=self.clock,
            vclient=self.vclient,
            mqtt=self.mqtt,
            profile=self.profile,
            queue_capacity=queue_capacity,
            confirm_budget_s=confirm_budget_s,
            confirm_interval_s=confirm_interval_s,
            terminal_ttl_s=terminal_ttl_s,
        )

    def ack_payloads(self) -> list[dict]:
        """Contenu decode des ACK publies, dans l'ordre."""
        return [json.loads(h.publication.payload) for h in self.mqtt.publications]

    def write_calls(self) -> list:
        return [c for c in self.vclient.calls if c.op == "write"]

    def read_calls(self) -> list:
        return [c for c in self.vclient.calls if c.op == "read"]
