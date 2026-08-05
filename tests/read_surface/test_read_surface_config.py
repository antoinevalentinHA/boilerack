"""Tests de `boilerack.read_surface.config` — §3.1 et §3.3 de C7-B.

La normalisation elle-meme est deja verrouillee par `test_topics.py` : on ne
duplique pas ses cas, on prouve que la configuration DELEGUE bien a
`normalize_prefix` et ne conserve que la forme normalisee.
"""

from __future__ import annotations

import dataclasses

import pytest

from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.topics import InvalidMqttTopic, normalize_prefix


def test_defaut_contractuel() -> None:
    """§3.1 : defaut `boiler`, sans barre oblique terminale."""
    assert ReadSurfaceConfig().prefix == "boiler"


def test_champs_exacts() -> None:
    """Trois champs apres C7-C3B, et rien d'autre : chacun a un consommateur."""
    champs = {f.name for f in dataclasses.fields(ReadSurfaceConfig)}
    assert champs == {"prefix", "snapshot_period_s", "heartbeat_period_s"}


def test_defauts_contractuels_des_cadences() -> None:
    """§7.4 : la republication **SHOULD** valoir la plus petite periode cible."""
    config = ReadSurfaceConfig()
    assert config.snapshot_period_s == 30
    assert config.heartbeat_period_s == 30
    assert config.heartbeat_enabled is True


@pytest.mark.parametrize("periode", [1, 30, 90, 3600])
def test_periode_snapshot_valide(periode: int) -> None:
    assert ReadSurfaceConfig(snapshot_period_s=periode).snapshot_period_s == periode


@pytest.mark.parametrize("periode", [True, False, 30.0, "30", None])
def test_periode_snapshot_non_entiere_refusee(periode: object) -> None:
    with pytest.raises(ValueError, match="snapshot_period_s doit etre un entier"):
        ReadSurfaceConfig(snapshot_period_s=periode)  # type: ignore[arg-type]


@pytest.mark.parametrize("periode", [0, -1, -30])
def test_periode_snapshot_non_positive_refusee(periode: int) -> None:
    with pytest.raises(ValueError, match="strictement positif"):
        ReadSurfaceConfig(snapshot_period_s=periode)


def test_heartbeat_desactivable() -> None:
    """§9 : « Un producteur **MAY** l'omettre s'il documente la rupture »."""
    config = ReadSurfaceConfig(heartbeat_period_s=None)
    assert config.heartbeat_period_s is None
    assert config.heartbeat_enabled is False


@pytest.mark.parametrize("periode", [1, 30, 60])
def test_heartbeat_periode_positive_acceptee(periode: int) -> None:
    assert ReadSurfaceConfig(heartbeat_period_s=periode).heartbeat_period_s == periode


@pytest.mark.parametrize("periode", [True, False, 30.0, "30"])
def test_heartbeat_non_entier_refuse(periode: object) -> None:
    with pytest.raises(ValueError, match="heartbeat_period_s doit etre un entier"):
        ReadSurfaceConfig(heartbeat_period_s=periode)  # type: ignore[arg-type]


@pytest.mark.parametrize("periode", [0, -1])
def test_heartbeat_non_positif_refuse(periode: int) -> None:
    with pytest.raises(ValueError, match="strictement positif"):
        ReadSurfaceConfig(heartbeat_period_s=periode)


def test_borne_haute_du_snapshot_non_verifiee_ici() -> None:
    """La borne de §7.4 depend des specs : elle est verifiee par le publieur.

    `ReadSurfaceConfig` ne connait pas les mesures injectees ; une periode de
    120 s est donc acceptee ici, et refusee a la construction du publieur avec
    `V1_MEASUREMENTS` (plus petit `fresh_max_s` = 90 s).
    """
    assert ReadSurfaceConfig(snapshot_period_s=120).snapshot_period_s == 120


def test_gelee() -> None:
    with pytest.raises(Exception):
        ReadSurfaceConfig().prefix = "autre"  # type: ignore[misc]


@pytest.mark.parametrize(
    "entree", ["boiler", "boiler/", "/boiler", "/boiler/", "maison//boiler", "a/b/c"]
)
def test_forme_normalisee_seule_conservee(entree: str) -> None:
    """La configuration delegue : le resultat est exactement `normalize_prefix`."""
    assert ReadSurfaceConfig(prefix=entree).prefix == normalize_prefix(entree)


def test_barres_de_bordure_retirees() -> None:
    assert ReadSurfaceConfig(prefix="/boiler/").prefix == "boiler"


def test_barres_consecutives_reduites() -> None:
    assert ReadSurfaceConfig(prefix="maison//boiler").prefix == "maison/boiler"


def test_prefixe_multi_niveaux() -> None:
    assert ReadSurfaceConfig(prefix="maison/cave/boiler").prefix == "maison/cave/boiler"


def test_normalisation_idempotente() -> None:
    une_fois = ReadSurfaceConfig(prefix="/maison//boiler/").prefix
    assert ReadSurfaceConfig(prefix=une_fois).prefix == une_fois


@pytest.mark.parametrize("entree", ["", "/", "boiler+", "boiler#", "$SYS", "\x00", 42])
def test_rejet_a_la_construction(entree: object) -> None:
    """§3.3 : « Le rejet **MUST** survenir a la construction de la configuration »."""
    with pytest.raises(InvalidMqttTopic):
        ReadSurfaceConfig(prefix=entree)  # type: ignore[arg-type]


def test_aucun_topic_complet_stocke() -> None:
    """Les topics se derivent du prefixe (§3.2), ils ne sont jamais memorises."""
    config = ReadSurfaceConfig(prefix="maison/boiler")
    valeurs = [getattr(config, f.name) for f in dataclasses.fields(config)]
    assert not any("bridge/" in v for v in valeurs if isinstance(v, str))
