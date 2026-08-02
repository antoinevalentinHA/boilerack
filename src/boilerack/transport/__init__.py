"""Frontieres techniques du bridge : transport `vcontrold` et transport MQTT.

Interfaces et types uniquement. Aucune implementation reelle (ni socket, ni
Paho, ni sous-processus) n'est fournie a ce stade : les seuls objets concrets
vivent dans `boilerack.testing`.
"""

from __future__ import annotations

from boilerack.transport.mqtt import (
    Message,
    MqttClient,
    NotConnectedError,
    Publication,
    PublishHandle,
    Subscription,
)
from boilerack.transport.vclient import (
    ReadResult,
    TransportStatus,
    VClient,
    WriteResult,
)

__all__ = [
    "Message",
    "MqttClient",
    "NotConnectedError",
    "Publication",
    "PublishHandle",
    "Subscription",
    "ReadResult",
    "TransportStatus",
    "VClient",
    "WriteResult",
]
