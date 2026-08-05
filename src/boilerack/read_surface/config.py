"""Configuration de la surface MQTT de lecture.

Implemente §3.1 et §3.3 du contrat `c7-mqtt-read-contract.md` — un parametre
`mqtt_prefix`, de defaut contractuel `boiler`, normalise et valide **a la
construction de la configuration**, avant toute connexion — ainsi que les
cadences de §7.4 (instantane) et §9 (battement).

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

#: §7.4 : la periode de republication de l'instantane **SHOULD** valoir la plus
#: petite periode cible de la surface — 30 s pour les trois temperatures (§4.2).
_DEFAULT_SNAPSHOT_PERIOD_S = 30

#: §9 : cadence historique configuree du battement. Le contrat ne fixe AUCUNE
#: cadence normative pour lui ; 30 s reprend simplement l'existant.
_DEFAULT_HEARTBEAT_PERIOD_S = 30


def _check_periode(value: int, champ: str) -> int:
    """Entier strictement positif. Le booleen est ecarte explicitement."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{champ} doit etre un entier : {value!r}")
    if value <= 0:
        raise ValueError(f"{champ} doit etre strictement positif : {value!r}")
    return value


@dataclass(frozen=True)
class ReadSurfaceConfig:
    """Configuration de la surface de lecture.

    `prefix` est NORMALISE a la construction et seule la forme normalisee est
    conservee : §3.3 exige que « le rejet **MUST** survenir a la construction
    de la configuration, avant toute connexion ». Une entree invalide leve donc
    `InvalidMqttTopic` ici, jamais plus tard.

    `snapshot_period_s` : periode de republication de l'instantane (§7.4).
    Sa borne haute — « **MUST** etre inferieure ou egale au plus petit
    `fresh_max` de la surface » — depend des mesures REELLEMENT injectees au
    publieur, que cette configuration ne connait pas. Elle est donc verifiee
    dans `ReadSurfacePublisher.__init__`, ou les deux sont disponibles ; ici on
    ne controle que ce qui est independant des specs.

    `heartbeat_period_s` : cadence du battement (§9), ou `None` pour le
    desactiver — §9 : « Un producteur **MAY** l'omettre s'il documente la
    rupture ». Le contrat ne fixe aucune cadence normative ; le defaut reprend
    la cadence historique.
    """

    prefix: str = _DEFAULT_PREFIX
    snapshot_period_s: int = _DEFAULT_SNAPSHOT_PERIOD_S
    heartbeat_period_s: int | None = _DEFAULT_HEARTBEAT_PERIOD_S

    def __post_init__(self) -> None:
        # `normalize_prefix` refuse deja une entree non textuelle, la chaine
        # vide, les jokers, les caracteres de controle et un prefixe commencant
        # par `$`. On ne duplique pas ces controles.
        object.__setattr__(self, "prefix", normalize_prefix(self.prefix))
        _check_periode(self.snapshot_period_s, "snapshot_period_s")
        if self.heartbeat_period_s is not None:
            _check_periode(self.heartbeat_period_s, "heartbeat_period_s")

    @property
    def heartbeat_enabled(self) -> bool:
        """Vrai si le battement doit etre publie."""
        return self.heartbeat_period_s is not None
