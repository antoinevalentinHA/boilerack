"""Configuration de la surface MQTT de lecture.

Implemente §3.1 et §3.3 du contrat `c7-mqtt-read-contract.md` : un parametre
`mqtt_prefix`, de defaut contractuel `boiler`, normalise et valide **a la
construction de la configuration**, avant toute connexion.

AUTORITE UNIQUE DU PREFIXE
    `boilerack.adapters.config.MqttConfig` n'est ni modifie ni reutilise. Il
    porte la connexion au broker et les topics de la surface TRANSACTIONNELLE
    (`command_topic`, `ack_topic_prefix`) ; y loger le prefixe de lecture
    creerait une seconde autorite et rouvrirait la dette de convergence des
    namespaces enregistree en §14, que ce lot n'a pas a arbitrer.

AUCUN TOPIC COMPLET N'EST STOCKE : tout topic se derive du prefixe et d'un
suffixe contractuel, via `build_topic` (§3.2).

Module PUR : aucune horloge, aucun reseau, aucun processus, aucun etat.
"""

from __future__ import annotations

from dataclasses import dataclass

from boilerack.read_surface.topics import normalize_prefix

__all__ = ["ReadSurfaceConfig"]

#: Defaut contractuel du prefixe (§3.1), retenu pour preserver la
#: compatibilite avec le consommateur historique.
_DEFAULT_PREFIX = "boiler"


@dataclass(frozen=True)
class ReadSurfaceConfig:
    """Configuration de la surface de lecture. Un seul champ en C7-C3A.

    `prefix` est NORMALISE a la construction et seule la forme normalisee est
    conservee : §3.3 exige que « le rejet **MUST** survenir a la construction
    de la configuration, avant toute connexion ». Une entree invalide leve donc
    `InvalidMqttTopic` ici, jamais plus tard.

    Ne portent PAS encore de cadence : `snapshot_period_s` et
    `heartbeat_period_s` n'auraient aucun consommateur dans ce lot, qui ne
    publie ni sur cadence ni de battement. Ils seront introduits en C7-C3B,
    avec l'ordonnancement qui les utilise.
    """

    prefix: str = _DEFAULT_PREFIX

    def __post_init__(self) -> None:
        # `normalize_prefix` refuse deja une entree non textuelle, la chaine
        # vide, les jokers, les caracteres de controle et un prefixe commencant
        # par `$`. On ne duplique pas ces controles.
        object.__setattr__(self, "prefix", normalize_prefix(self.prefix))
