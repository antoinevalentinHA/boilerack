"""Tests de `boilerack.read_surface.measurements` — §4.2 et §7.2 de C7-B."""

from __future__ import annotations

import ast
import pathlib

import pytest

from boilerack.read_surface import measurements as measurements_module
from boilerack.read_surface.measurements import (
    V1_MEASUREMENTS,
    MeasurementSpec,
    default_fresh_max,
)
from boilerack.read_surface.topics import TELEMETRY_SUFFIXES

#: Transcription independante de la table normative §4.2, ecrite ici a la main
#: pour que le test ne se contente pas de relire la declaration qu'il verifie.
_TABLE = (
    ("outdoor_temperature", "getTempA", "telemetry/temperatures/outdoor", 30, 90),
    ("supply_temperature", "getTempKist", "telemetry/temperatures/supply", 30, 90),
    ("dhw_temperature", "getTempWWist", "telemetry/temperatures/dhw", 30, 90),
    ("dhw_setpoint", "getTempWWsoll", "telemetry/dhw/setpoint", 60, 180),
    ("heating_setpoint", "getTempRaumNorSollM1", "telemetry/heating/setpoint", 60, 180),
    (
        "heating_reduced_reference",
        "getTempRaumRedSollM1",
        "telemetry/heating/reduced_reference",
        60,
        180,
    ),
    ("heating_curve_slope", "getNeigungM1", "telemetry/heating/curve/slope", 60, 180),
    ("heating_curve_shift", "getNiveauM1", "telemetry/heating/curve/shift", 60, 180),
)


def _spec(**surcharges: object) -> MeasurementSpec:
    base: dict[str, object] = {
        "role": "r",
        "read": "getX",
        "suffix": "telemetry/x",
        "period_s": 30,
        "fresh_max_s": 90,
    }
    base.update(surcharges)
    return MeasurementSpec(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Conformite de la surface v1
# ---------------------------------------------------------------------------


def test_huit_mesures_exactement() -> None:
    assert len(V1_MEASUREMENTS) == 8


def test_autorite_immutable() -> None:
    assert isinstance(V1_MEASUREMENTS, tuple)


def test_contenu_et_ordre_exacts() -> None:
    obtenu = tuple(
        (s.role, s.read, s.suffix, s.period_s, s.fresh_max_s) for s in V1_MEASUREMENTS
    )
    assert obtenu == _TABLE


@pytest.mark.parametrize("attendu", _TABLE, ids=[t[0] for t in _TABLE])
def test_chaque_mesure_du_contrat(attendu: tuple[str, str, str, int, int]) -> None:
    role, read, suffix, period, fresh = attendu
    spec = next(s for s in V1_MEASUREMENTS if s.role == role)
    assert (spec.read, spec.suffix, spec.period_s, spec.fresh_max_s) == (
        read,
        suffix,
        period,
        fresh,
    )


def test_suffixes_identiques_et_ordonnes_comme_c7c1() -> None:
    """Garde contre toute derive entre la declaration et l'autorite close de §11."""
    assert tuple(s.suffix for s in V1_MEASUREMENTS) == TELEMETRY_SUFFIXES


def test_roles_uniques() -> None:
    roles = [s.role for s in V1_MEASUREMENTS]
    assert len(set(roles)) == 8


def test_suffixes_uniques() -> None:
    suffixes = [s.suffix for s in V1_MEASUREMENTS]
    assert len(set(suffixes)) == 8


def test_commandes_de_lecture_uniques_en_v1() -> None:
    """Constat de la v1, PAS une regle generique : le contrat n'interdit nulle
    part que deux roles partagent une commande de lecture."""
    lectures = [s.read for s in V1_MEASUREMENTS]
    assert len(set(lectures)) == 8


def test_seuils_conformes_a_la_regle_trois_fois_p() -> None:
    for spec in V1_MEASUREMENTS:
        assert spec.fresh_max_s == default_fresh_max(spec.period_s)


def test_periodes_du_contrat() -> None:
    """Trois mesures a 30 s, cinq a 60 s (§4.2)."""
    periodes = [s.period_s for s in V1_MEASUREMENTS]
    assert periodes.count(30) == 3
    assert periodes.count(60) == 5


def test_plus_petit_seuil_de_fraicheur() -> None:
    """Utile a §7.4, applique en C7-C3 : la republication doit lui rester inferieure."""
    assert min(s.fresh_max_s for s in V1_MEASUREMENTS) == 90


def test_aucune_mesure_de_brulleur() -> None:
    """§4.3 : `burner_modulation` et `burner_state` sont reportes hors v1."""
    assert not any("burner" in s.role or "burner" in s.suffix for s in V1_MEASUREMENTS)


# ---------------------------------------------------------------------------
# `default_fresh_max`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("periode", "attendu"), [(1, 3), (30, 90), (60, 180)])
def test_default_fresh_max(periode: int, attendu: int) -> None:
    assert default_fresh_max(periode) == attendu


@pytest.mark.parametrize("periode", [0, -1, -30])
def test_default_fresh_max_refuse_une_periode_non_positive(periode: int) -> None:
    with pytest.raises(ValueError, match="strictement positif"):
        default_fresh_max(periode)


@pytest.mark.parametrize("periode", [True, False, 30.0, "30", None])
def test_default_fresh_max_refuse_un_type_invalide(periode: object) -> None:
    with pytest.raises(ValueError, match="doit etre un entier"):
        default_fresh_max(periode)  # type: ignore[arg-type]


def test_default_fresh_max_respecte_toujours_l_invariant() -> None:
    for periode in (1, 7, 30, 60, 3600):
        assert default_fresh_max(periode) > periode


# ---------------------------------------------------------------------------
# Invariants generiques d'une mesure
# ---------------------------------------------------------------------------


def test_declaration_valide_acceptee() -> None:
    spec = _spec()
    assert (spec.role, spec.period_s, spec.fresh_max_s) == ("r", 30, 90)


@pytest.mark.parametrize("champ", ["role", "read", "suffix"])
@pytest.mark.parametrize("valeur", ["", None, 7, b"x"])
def test_chaines_obligatoires(champ: str, valeur: object) -> None:
    with pytest.raises(ValueError, match="chaine non vide"):
        _spec(**{champ: valeur})


@pytest.mark.parametrize("champ", ["period_s", "fresh_max_s"])
@pytest.mark.parametrize("valeur", [True, False, 30.0, "30", None])
def test_entiers_obligatoires_booleens_refuses(champ: str, valeur: object) -> None:
    with pytest.raises(ValueError, match="doit etre un entier"):
        _spec(**{champ: valeur})


@pytest.mark.parametrize("periode", [0, -5])
def test_periode_strictement_positive(periode: int) -> None:
    with pytest.raises(ValueError, match="strictement positif"):
        _spec(period_s=periode, fresh_max_s=999)


@pytest.mark.parametrize("seuil", [0, -5])
def test_seuil_strictement_positif(seuil: int) -> None:
    with pytest.raises(ValueError, match="strictement positif"):
        _spec(fresh_max_s=seuil)


@pytest.mark.parametrize("seuil", [30, 29, 1])
def test_seuil_doit_depasser_strictement_la_periode(seuil: int) -> None:
    """§7.2 : « `fresh_max` **MUST** etre strictement superieur a `P` »."""
    with pytest.raises(ValueError, match="strictement superieur"):
        _spec(period_s=30, fresh_max_s=seuil)


def test_seuil_juste_au_dessus_accepte() -> None:
    assert _spec(period_s=30, fresh_max_s=31).fresh_max_s == 31


def test_seuil_personnalise_accepte() -> None:
    """§7.2 : `fresh_max` **MAY** etre configure par mesure."""
    assert _spec(period_s=30, fresh_max_s=45).fresh_max_s == 45


def test_declaration_gelee() -> None:
    spec = _spec()
    with pytest.raises(Exception):
        spec.role = "autre"  # type: ignore[misc]


def test_aucun_champ_supplementaire() -> None:
    """Ni unite, ni type metier, ni forme, ni valeur, ni bornes, ni tolerance."""
    import dataclasses

    champs = {f.name for f in dataclasses.fields(MeasurementSpec)}
    assert champs == {"role", "read", "suffix", "period_s", "fresh_max_s"}


# ---------------------------------------------------------------------------
# Absence d'effet de bord
# ---------------------------------------------------------------------------

_INTERDITS = {
    "paho",
    "socket",
    "subprocess",
    "threading",
    "asyncio",
    "time",
    "os",
    "pathlib",
    "json",
}


def _modules_importes(module: object) -> set[str]:
    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")  # type: ignore[arg-type]
    noms: set[str] = set()
    for noeud in ast.walk(ast.parse(source)):
        if isinstance(noeud, ast.Import):
            noms.update(alias.name.split(".")[0] for alias in noeud.names)
        elif isinstance(noeud, ast.ImportFrom) and noeud.module:
            noms.add(noeud.module.split(".")[0])
    return noms


def test_module_sans_dependance_technique() -> None:
    assert _modules_importes(measurements_module) & _INTERDITS == set()


def test_module_ne_depend_d_aucune_autre_partie_du_projet() -> None:
    assert "boilerack" not in _modules_importes(measurements_module)
