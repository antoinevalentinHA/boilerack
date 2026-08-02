"""Adaptateurs techniques reels du bridge (lot C4).

Ce paquet relie les frontieres abstraites de C2 (`MqttClient`, `VClient`) a des
implementations reelles, sans jamais contacter la production :

- `MqttConfig` / `VclientConfig` : modeles de configuration immuables et valides ;
- `PahoMqttClient` : adaptateur MQTT reel fonde sur Paho MQTT v2 ;
- `ProcessRunner` / `SubprocessRunner` / `ProcessResult` : frontiere generique et
  injectable autour d'un sous-processus borne, sans dialecte `vclient`.

Depuis C6, le volet LECTURE de l'adaptateur `vclient` est disponible :

- `VClientCliReader` : execute `vclient -J` et classe l'issue selon les seules
  signatures caracterisees en C5.

Le volet ECRITURE reste DELIBEREMENT absent : le contrat reel d'une commande
`set…` n'est toujours pas caracterise. `VClientCliReader` n'expose donc aucune
methode `write` et ne satisfait pas le protocole `VClient` complet — il ne peut
pas etre branche au moteur transactionnel. Voir docs/design/c6-vclient-read-adapter.md.
"""

from __future__ import annotations

from boilerack.adapters.config import MqttConfig, VclientConfig
from boilerack.adapters.mqtt_paho import PahoLike, PahoMqttClient
from boilerack.adapters.process_runner import (
    ProcessResult,
    ProcessRunner,
    SubprocessRunner,
)
from boilerack.adapters.vclient_cli import InvalidCommandName, VClientCliReader

__all__ = [
    "MqttConfig",
    "VclientConfig",
    "PahoMqttClient",
    "PahoLike",
    "ProcessResult",
    "ProcessRunner",
    "SubprocessRunner",
    "VClientCliReader",
    "InvalidCommandName",
]
