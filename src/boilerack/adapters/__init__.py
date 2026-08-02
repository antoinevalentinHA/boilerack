"""Adaptateurs techniques reels du bridge (lot C4).

Ce paquet relie les frontieres abstraites de C2 (`MqttClient`, `VClient`) a des
implementations reelles, sans jamais contacter la production :

- `MqttConfig` / `VclientConfig` : modeles de configuration immuables et valides ;
- `PahoMqttClient` : adaptateur MQTT reel fonde sur Paho MQTT v2 ;
- `ProcessRunner` / `SubprocessRunner` / `ProcessResult` : frontiere generique et
  injectable autour d'un sous-processus borne, sans dialecte `vclient`.

L'adaptateur `vclient` concret (traduction sortie -> `TransportStatus`) reste
DELIBEREMENT absent : son contrat reel (arguments, sorties, codes retour, erreurs)
n'est pas encore caracterise a partir d'une source explicite. Voir
docs/design/c4-real-adapters.md.
"""

from __future__ import annotations

from boilerack.adapters.config import MqttConfig, VclientConfig
from boilerack.adapters.mqtt_paho import PahoLike, PahoMqttClient
from boilerack.adapters.process_runner import (
    ProcessResult,
    ProcessRunner,
    SubprocessRunner,
)

__all__ = [
    "MqttConfig",
    "VclientConfig",
    "PahoMqttClient",
    "PahoLike",
    "ProcessResult",
    "ProcessRunner",
    "SubprocessRunner",
]
