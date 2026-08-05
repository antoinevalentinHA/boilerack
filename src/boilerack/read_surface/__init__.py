"""Surface MQTT de lecture — parties pures (lots C7-C1 et C7-C2).

Ce paquet implemente les parties du contrat `c7-mqtt-read-contract.md` qui sont
entierement specifiees et sans dependance technique :

- **C7-C1** : construction des topics (§3.2 a §3.4) et serialisation du payload
  scalaire (§4.5) ;
- **C7-C2** : declaration des huit mesures (§4.2), etat de lecture (§6.5),
  politique de fraicheur (§7.2, §7.3), cloture de cycle et etat de chaine
  (§8.2), instantane `bridge/telemetry_status` (§6.2, §6.6) ;
- **C7-C3A** : configuration du prefixe (§3.1, §3.3), testament MQTT, presence
  `bridge/online` et instantane de demarrage (§5, §7.3) ;
- **C7-C3B** : lecture des mesures dues, publication scalaire (§4.4, §4.5),
  ordre par mesure (§4.6), cloture de cycle (§8.2), echeances et republication
  periodique de l'instantane (§7.2, §7.4), battement (§9).

Les modules C7-C1 et C7-C2 restent **purs** : aucun processus, aucun socket,
aucun client MQTT, aucun lecteur `vclient`. `publisher` est le seul module du
paquet a dialoguer avec un client MQTT et un lecteur — tous deux **injectes**,
jamais construits. L'horloge est toujours injectee ; aucune horloge systeme
n'est lue. Il n'existe ni boucle, ni thread, ni sommeil : l'appelant pilote.

Aucune valeur scalaire n'est conservee : elle va du `ReadResult` au payload sans
transiter par l'etat, qui est une **projection des issues**. Voir
`state.py` et docs/design/c7c2-read-surface-state.md.

Sont DELIBEREMENT absents : toute composition root, toute CLI, tout service,
toute politique de reconnexion et tout chemin d'ecriture.
"""

from __future__ import annotations

from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.measurements import (
    V1_MEASUREMENTS,
    MeasurementSpec,
    default_fresh_max,
)
from boilerack.read_surface.publisher import MeasurementReader, ReadSurfacePublisher
from boilerack.read_surface.payload import format_scalar
from boilerack.read_surface.snapshot import (
    PublicResult,
    build_snapshot,
    snapshot_to_json,
)
from boilerack.read_surface.state import (
    ChainStatus,
    MeasurementState,
    ReadSurfaceState,
    complete_cycle,
    record_result,
)
from boilerack.read_surface.topics import (
    BRIDGE_SUFFIXES,
    TELEMETRY_SUFFIXES,
    V1_SUFFIXES,
    InvalidMqttTopic,
    build_topic,
    normalize_prefix,
)

__all__ = [
    # C7-C1 — topics
    "InvalidMqttTopic",
    "normalize_prefix",
    "build_topic",
    "TELEMETRY_SUFFIXES",
    "BRIDGE_SUFFIXES",
    "V1_SUFFIXES",
    # C7-C1 — payload
    "format_scalar",
    # C7-C2 — declaration
    "MeasurementSpec",
    "default_fresh_max",
    "V1_MEASUREMENTS",
    # C7-C2 — etat et cycles
    "MeasurementState",
    "ReadSurfaceState",
    "ChainStatus",
    "record_result",
    "complete_cycle",
    # C7-C2 — instantane
    "PublicResult",
    "build_snapshot",
    "snapshot_to_json",
    # C7-C3A/B — configuration, presence et publieur
    "ReadSurfaceConfig",
    "MeasurementReader",
    "ReadSurfacePublisher",
]
