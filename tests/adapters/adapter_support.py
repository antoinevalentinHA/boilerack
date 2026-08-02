"""Doubles hors ligne pour les tests d'adaptateurs C4.

Aucun reseau, aucun broker, aucun processus reel. Le faux client Paho reproduit
la surface `PahoLike` reellement utilisee par l'adaptateur et laisse le test
declencher explicitement les callbacks (`on_connect`, `on_disconnect`,
`on_publish`, `on_message`), y compris pour simuler la course PUBACK.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from boilerack.transport import Message

START = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def rid(n: int) -> str:
    """UUID v4 canonique minuscule, deterministe et distinct par `n`."""
    return f"00000000-0000-4000-8000-{n:012d}"


def command_payload(request_id, role, value, *, ttl_seconds=60.0, start=START):
    """Payload JSON de commande valide, pour les tests d'integration."""
    body = {
        "request_id": request_id,
        "ts": start.isoformat(),
        "expires_at": (start + timedelta(seconds=ttl_seconds)).isoformat(),
        "source": "test",
        "role": role,
        "value": value,
    }
    return json.dumps(body).encode("utf-8")


def command_message(payload_bytes, *, topic="boilerack/command", qos=1, dup=False):
    return Message(topic=topic, payload=payload_bytes, qos=qos, dup=dup)


@dataclass
class FakeMessageInfo:
    """Reproduit `MQTTMessageInfo` : code retour immediat + `mid`."""

    rc: int
    mid: int


@dataclass
class FakeMqttMessage:
    """Reproduit un message Paho entrant."""

    topic: str
    payload: bytes
    qos: int = 0
    retain: bool = False
    dup: bool = False


@dataclass
class FakePahoClient:
    """Faux client Paho injectable, deterministe et hors ligne."""

    next_mid: int = 1
    publish_rc: int = 0  # 0 = MQTT_ERR_SUCCESS
    # journaux d'appels
    connected_args: tuple | None = None
    loop_started: int = 0
    loop_stopped: int = 0
    disconnected: int = 0
    subscriptions: list = field(default_factory=list)
    published: list = field(default_factory=list)
    # callbacks cables par l'adaptateur
    on_connect: object = None
    on_disconnect: object = None
    on_publish: object = None
    on_message: object = None

    # -- surface PahoLike ----------------------------------------------------

    def connect(self, host, port, keepalive):
        self.connected_args = (host, port, keepalive)

    def disconnect(self):
        self.disconnected += 1

    def loop_start(self):
        self.loop_started += 1

    def loop_stop(self):
        self.loop_stopped += 1

    def subscribe(self, topic, qos=0):
        self.subscriptions.append((topic, qos))

    def publish(self, topic, payload, qos=0, retain=False):
        mid = self.next_mid
        self.next_mid += 1
        self.published.append(
            {"topic": topic, "payload": payload, "qos": qos, "retain": retain, "mid": mid}
        )
        return FakeMessageInfo(rc=self.publish_rc, mid=mid)

    # -- declencheurs de callbacks (cote test) -------------------------------

    def fire_on_publish(self, mid):
        self.on_publish(self, None, mid, None, None)

    def fire_on_message(self, message):
        self.on_message(self, None, message)

    def fire_on_connect(self, *, success=True):
        rc = 0 if success else 1
        self.on_connect(self, None, {}, rc, None)

    def fire_on_disconnect(self, *, reason=0):
        self.on_disconnect(self, None, None, reason, None)
