"""Doubles de test deterministes du projet.

Infrastructure INTERNE : ces doubles simulent les frontieres techniques (horloge,
transport `vcontrold`, transport MQTT) pour permettre de tester le futur coeur
sans chaudiere, sans reseau, sans broker et sans attente reelle.

Ce n'est PAS une API publique garantie. Le contenu peut evoluer avec les besoins
des tests, sans preavis de compatibilite.
"""

from __future__ import annotations

from boilerack.testing.fake_clock import VirtualClock
from boilerack.testing.fake_mqtt import FakeMqttClient
from boilerack.testing.fake_profile import build_fake_profile
from boilerack.testing.fake_vclient import (
    FakeVClient,
    FakeVClientError,
    RecordedCall,
    UnconsumedExpectations,
    UnexpectedCall,
)

__all__ = [
    "VirtualClock",
    "FakeMqttClient",
    "build_fake_profile",
    "FakeVClient",
    "FakeVClientError",
    "RecordedCall",
    "UnconsumedExpectations",
    "UnexpectedCall",
]
