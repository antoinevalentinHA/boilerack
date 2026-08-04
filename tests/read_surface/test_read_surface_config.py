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


def test_un_seul_champ_en_c7c3a() -> None:
    """Ni `snapshot_period_s` ni `heartbeat_period_s` : aucun consommateur ici."""
    champs = {f.name for f in dataclasses.fields(ReadSurfaceConfig)}
    assert champs == {"prefix"}


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
