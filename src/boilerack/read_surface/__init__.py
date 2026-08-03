"""Primitives pures de la surface MQTT de lecture (lot C7-C1).

Ce paquet implemente les seules parties du contrat `c7-mqtt-read-contract.md`
qui sont entierement specifiees et sans aucune dependance : la construction des
topics (§3.2 a §3.4) et la serialisation du payload scalaire (§4.5).

Tout y est **pur** : aucune horloge, aucun processus, aucun socket, aucun
client MQTT, aucun lecteur `vclient`, aucun etat. Ce paquet ne publie rien et
ne peut rien publier.

Sont DELIBEREMENT absents de ce lot, faute de consommateur :

- la declaration des mesures, la fraicheur et l'instantane `bridge/telemetry_status`
  (reportes en C7-C2) ;
- le testament MQTT, la presence, le battement, le publieur et l'ordonnancement
  (reportes en C7-C3).

Voir docs/design/c7c1-read-surface-primitives.md.
"""

from __future__ import annotations

from boilerack.read_surface.payload import format_scalar
from boilerack.read_surface.topics import (
    BRIDGE_SUFFIXES,
    TELEMETRY_SUFFIXES,
    V1_SUFFIXES,
    InvalidMqttTopic,
    build_topic,
    normalize_prefix,
)

__all__ = [
    "InvalidMqttTopic",
    "normalize_prefix",
    "build_topic",
    "TELEMETRY_SUFFIXES",
    "BRIDGE_SUFFIXES",
    "V1_SUFFIXES",
    "format_scalar",
]
