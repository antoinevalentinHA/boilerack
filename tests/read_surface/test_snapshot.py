"""Tests de `boilerack.read_surface.snapshot` — §6.2, §6.4, §6.5, §6.6, §7.2 de C7-B."""

from __future__ import annotations

import ast
import json
import math
import pathlib
from datetime import datetime, timedelta, timezone

import pytest

from boilerack.read_surface import snapshot as snapshot_module
from boilerack.read_surface.measurements import V1_MEASUREMENTS, MeasurementSpec
from boilerack.read_surface.snapshot import (
    PublicResult,
    build_snapshot,
    snapshot_to_json,
)
from boilerack.read_surface.state import (
    ChainStatus,
    ReadSurfaceState,
    complete_cycle,
    record_result,
)
from boilerack.testing import VirtualClock
from boilerack.transport.vclient import TransportStatus

_DEBUT = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)
_CLES_GLOBALES = {"schema", "ts", "chain", "measurements"}
_CLES_MESURE = {"has_value", "fresh", "last_success", "age_s", "last_result"}

#: Une seule mesure suffit a la plupart des scenarios : `fresh_max` vaut 90 s.
_SUPPLY = next(s for s in V1_MEASUREMENTS if s.role == "supply_temperature")


class _HorlogeDissociee:
    """Double local : `VirtualClock` ne peut pas dissocier mural et monotone."""

    def __init__(self, wall: object, monotonic: object) -> None:
        self.wall, self.monotonic_value = wall, monotonic

    def now(self):  # type: ignore[no-untyped-def]
        return self.wall

    def monotonic(self):  # type: ignore[no-untyped-def]
        return self.monotonic_value

    def sleep(self, seconds: float) -> None:  # pragma: no cover
        raise AssertionError("aucun sommeil ne doit etre demande")


def _clock(monotonic_start: float = 1000.0) -> VirtualClock:
    return VirtualClock(_DEBUT, monotonic_start=monotonic_start)


def _initial() -> ReadSurfaceState:
    return ReadSurfaceState.initial(V1_MEASUREMENTS)


def _apres_succes(c: VirtualClock) -> ReadSurfaceState:
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    return complete_cycle(st, {"supply_temperature": TransportStatus.OK})


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------


def test_cles_globales_exactes() -> None:
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    assert set(snap) == _CLES_GLOBALES


def test_cles_de_mesure_exactes() -> None:
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    for mesure in snap["measurements"].values():
        assert set(mesure) == _CLES_MESURE


@pytest.mark.parametrize(
    "interdite", ["value", "raw", "detail", "last_attempt", "status", "unit"]
)
def test_aucun_champ_interdit_par_mesure(interdite: str) -> None:
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    assert all(interdite not in m for m in snap["measurements"].values())


def test_aucune_valeur_scalaire_dans_le_snapshot() -> None:
    """L'instantane decrit l'ETAT DE LECTURE ; la valeur vit sur son topic."""
    c = _clock()
    snap = build_snapshot(_apres_succes(c), V1_MEASUREMENTS, c)
    brut = snapshot_to_json(snap).decode("utf-8")
    assert "value" not in brut.replace("has_value", "")


def test_schema_vaut_un() -> None:
    assert build_snapshot(_initial(), V1_MEASUREMENTS, _clock())["schema"] == 1


def test_les_huit_mesures_sont_presentes() -> None:
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    assert set(snap["measurements"]) == {s.role for s in V1_MEASUREMENTS}


def test_ordre_des_mesures_conforme_aux_specs() -> None:
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    assert list(snap["measurements"]) == [s.role for s in V1_MEASUREMENTS]


def test_sous_ensemble_de_specs_accepte() -> None:
    snap = build_snapshot(_initial(), [_SUPPLY], _clock())
    assert list(snap["measurements"]) == ["supply_temperature"]


def test_spec_absente_de_l_etat_refusee() -> None:
    inconnue = MeasurementSpec(
        role="inconnue", read="getX", suffix="telemetry/x", period_s=10, fresh_max_s=30
    )
    with pytest.raises(ValueError, match="absent de l'etat"):
        build_snapshot(_initial(), [inconnue], _clock())


def test_spec_repetee_refusee() -> None:
    with pytest.raises(ValueError, match="repete"):
        build_snapshot(_initial(), [_SUPPLY, _SUPPLY], _clock())


# ---------------------------------------------------------------------------
# Etat initial, succes, echecs
# ---------------------------------------------------------------------------


def test_mesure_jamais_lue() -> None:
    """§6.5 : `has_value: false`, `fresh: false`, `last_success: null`, `age_s: null`."""
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    mesure = snap["measurements"]["supply_temperature"]
    assert mesure == {
        "has_value": False,
        "fresh": False,
        "last_success": None,
        "age_s": None,
        "last_result": None,
    }


def test_mesure_apres_succes() -> None:
    c = _clock()
    st = _apres_succes(c)
    c.advance(2)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure == {
        "has_value": True,
        "fresh": True,
        "last_success": "2026-08-02T20:00:00Z",
        "age_s": 2,
        "last_result": "ok",
    }


def test_echec_avant_tout_succes() -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.TIMEOUT, c)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["has_value"] is False
    assert mesure["fresh"] is False
    assert mesure["last_success"] is None
    assert mesure["age_s"] is None
    assert mesure["last_result"] == "timeout"


def test_echec_apres_succes_conserve_la_fraicheur() -> None:
    """§7.3 : `fresh` reste vrai tant que `age_s ≤ fresh_max`."""
    c = _clock()
    st = _apres_succes(c)
    c.advance(10)
    st = record_result(st, "supply_temperature", TransportStatus.TIMEOUT, c)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["has_value"] is True
    assert mesure["fresh"] is True
    assert mesure["age_s"] == 10
    assert mesure["last_result"] == "timeout"


def test_echecs_repetes_jusqu_au_depassement() -> None:
    """§7.3 : `fresh` devient faux ; la valeur retenue subsiste."""
    c = _clock()
    st = _apres_succes(c)
    c.advance(200)
    st = record_result(st, "supply_temperature", TransportStatus.TIMEOUT, c)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["has_value"] is True
    assert mesure["fresh"] is False
    assert mesure["age_s"] == 200


# ---------------------------------------------------------------------------
# `age_s` et fraicheur
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("ecoule", "attendu"), [(0, 0), (0.9, 0), (1.0, 1), (1.9, 1), (89.9, 89), (90.0, 90)]
)
def test_age_tronque_a_la_seconde_inferieure(ecoule: float, attendu: int) -> None:
    """Secondes ENTIERES ecoulees : `floor`, jamais d'arrondi au plus proche."""
    c = _clock()
    st = _apres_succes(c)
    c.advance(ecoule)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["age_s"] == attendu


@pytest.mark.parametrize(
    ("ecoule", "frais"), [(0, True), (89, True), (90, True), (90.5, True), (91, False)]
)
def test_frontiere_de_fraicheur_inclusive(ecoule: float, frais: bool) -> None:
    """§6.5 : `age_s` inferieur ou EGAL au seuil. `fresh_max` vaut 90 s ici."""
    c = _clock()
    st = _apres_succes(c)
    c.advance(ecoule)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["fresh"] is frais


def test_fraicheur_calculee_sur_l_entier_publie() -> None:
    """A 90,5 s l'age publie vaut 90 : le consommateur doit pouvoir refaire le calcul."""
    c = _clock()
    st = _apres_succes(c)
    c.advance(90.5)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["age_s"] == 90 and mesure["fresh"] is True


def test_seuil_propre_a_chaque_mesure() -> None:
    """Les mesures a 60 s tolerent 180 s la ou celles a 30 s ne tolerent que 90 s."""
    c = _clock()
    st = _initial()
    for role in ("supply_temperature", "dhw_setpoint"):
        st = record_result(st, role, TransportStatus.OK, c)
    c.advance(120)
    mesures = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]
    assert mesures["supply_temperature"]["fresh"] is False
    assert mesures["dhw_setpoint"]["fresh"] is True


def test_horloge_murale_deplacee_sans_effet_sur_l_age() -> None:
    """L'age se mesure sur le monotone : un reglage systeme ne le fausse pas."""
    c = _clock()
    st = _apres_succes(c)
    decalee = _HorlogeDissociee(_DEBUT + timedelta(hours=5), 1003.0)
    mesure = build_snapshot(st, V1_MEASUREMENTS, decalee)["measurements"][  # type: ignore[arg-type]
        "supply_temperature"
    ]
    assert mesure["age_s"] == 3
    assert mesure["last_success"] == "2026-08-02T20:00:00Z"


def test_horloge_murale_reculee_sans_effet_sur_l_age() -> None:
    c = _clock()
    st = _apres_succes(c)
    reculee = _HorlogeDissociee(_DEBUT - timedelta(hours=5), 1042.0)
    mesure = build_snapshot(st, V1_MEASUREMENTS, reculee)["measurements"][  # type: ignore[arg-type]
        "supply_temperature"
    ]
    assert mesure["age_s"] == 42


def test_monotone_recule_refuse() -> None:
    c = _clock()
    st = _apres_succes(c)
    recule = _HorlogeDissociee(_DEBUT, 900.0)
    with pytest.raises(ValueError, match="recule"):
        build_snapshot(st, V1_MEASUREMENTS, recule)  # type: ignore[arg-type]


@pytest.mark.parametrize("mono", [float("nan"), float("inf"), float("-inf")])
def test_monotone_non_fini_refuse(mono: float) -> None:
    with pytest.raises(ValueError, match="fini"):
        build_snapshot(_initial(), V1_MEASUREMENTS, _HorlogeDissociee(_DEBUT, mono))  # type: ignore[arg-type]


def test_monotone_non_numerique_refuse() -> None:
    with pytest.raises(ValueError, match="numerique"):
        build_snapshot(_initial(), V1_MEASUREMENTS, _HorlogeDissociee(_DEBUT, "1000"))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Horodatages
# ---------------------------------------------------------------------------


def test_ts_au_format_rfc3339_utc() -> None:
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    assert snap["ts"] == "2026-08-02T20:00:00Z"


def test_ts_converti_depuis_un_autre_fuseau() -> None:
    autre = _HorlogeDissociee(
        datetime(2026, 8, 2, 22, 0, 0, tzinfo=timezone(timedelta(hours=2))), 1000.0
    )
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, autre)  # type: ignore[arg-type]
    assert snap["ts"] == "2026-08-02T20:00:00Z"


def test_horloge_murale_naive_refusee() -> None:
    naive = _HorlogeDissociee(datetime(2026, 8, 2, 20, 0, 0), 1000.0)
    with pytest.raises(ValueError, match="fuseau horaire"):
        build_snapshot(_initial(), V1_MEASUREMENTS, naive)  # type: ignore[arg-type]


def test_horloge_murale_non_datetime_refusee() -> None:
    with pytest.raises(ValueError, match="instant attendu"):
        build_snapshot(_initial(), V1_MEASUREMENTS, _HorlogeDissociee("2026", 1000.0))  # type: ignore[arg-type]


def test_aucune_horloge_monotone_exposee() -> None:
    """§6.4 : « Une horloge monotone **MUST NOT** etre exposee »."""
    c = _clock(monotonic_start=123456.75)
    brut = snapshot_to_json(build_snapshot(_apres_succes(c), V1_MEASUREMENTS, c))
    assert b"123456" not in brut


# ---------------------------------------------------------------------------
# Taxonomie publique
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("interne", "public"),
    [
        (TransportStatus.OK, "ok"),
        (TransportStatus.TIMEOUT, "timeout"),
        (TransportStatus.DAEMON_UNREACHABLE, "daemon_unreachable"),
        (TransportStatus.UNUSABLE_OUTPUT, "unusable_output"),
        (TransportStatus.UNKNOWN_COMMAND, "unsupported_command"),
        (TransportStatus.TRANSPORT_ERROR, "transport_error"),
    ],
)
def test_les_six_correspondances_publiques(
    interne: TransportStatus, public: str
) -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", interne, c)
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["last_result"] == public


def test_unknown_command_devient_unsupported_command() -> None:
    """Piege : `TransportStatus.UNKNOWN_COMMAND.value` vaut `unknown_command`."""
    assert TransportStatus.UNKNOWN_COMMAND.value == "unknown_command"
    c = _clock()
    st = record_result(
        _initial(), "supply_temperature", TransportStatus.UNKNOWN_COMMAND, c
    )
    mesure = build_snapshot(st, V1_MEASUREMENTS, c)["measurements"]["supply_temperature"]
    assert mesure["last_result"] == "unsupported_command"
    assert mesure["last_result"] != TransportStatus.UNKNOWN_COMMAND.value


def test_taxonomie_publique_couvre_les_six_statuts() -> None:
    assert set(snapshot_module._PUBLIC) == set(TransportStatus)


def test_valeurs_publiques_contractuelles() -> None:
    """§6.6 : six valeurs stables et contractuelles."""
    assert {r.value for r in PublicResult} == {
        "ok",
        "timeout",
        "daemon_unreachable",
        "unusable_output",
        "unsupported_command",
        "transport_error",
    }


# ---------------------------------------------------------------------------
# Bloc `chain`
# ---------------------------------------------------------------------------


def test_chain_avant_tout_cycle() -> None:
    """§8.2 : `{ "status": "unavailable", "cause": null }`."""
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    assert snap["chain"] == {"status": "unavailable", "cause": None}


def test_chain_apres_cycle_reussi() -> None:
    c = _clock()
    snap = build_snapshot(_apres_succes(c), V1_MEASUREMENTS, c)
    assert snap["chain"] == {"status": "ok", "cause": None}


def test_chain_apres_cycle_degrade() -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    st = record_result(
        st, "dhw_temperature", TransportStatus.DAEMON_UNREACHABLE, c
    )
    st = complete_cycle(
        st,
        {
            "supply_temperature": TransportStatus.OK,
            "dhw_temperature": TransportStatus.DAEMON_UNREACHABLE,
        },
    )
    snap = build_snapshot(st, V1_MEASUREMENTS, c)
    assert snap["chain"] == {"status": "degraded", "cause": "daemon_unreachable"}


def test_chain_apres_cycle_indisponible() -> None:
    c = _clock()
    st = record_result(
        _initial(), "supply_temperature", TransportStatus.UNKNOWN_COMMAND, c
    )
    st = complete_cycle(st, {"supply_temperature": TransportStatus.UNKNOWN_COMMAND})
    snap = build_snapshot(st, V1_MEASUREMENTS, c)
    assert snap["chain"] == {"status": "unavailable", "cause": "unsupported_command"}


def test_snapshot_produit_hors_cycle() -> None:
    """§7.4 : l'instantane est republie meme si rien n'a change ; `chain` reflete
    alors le dernier cycle TERMINE."""
    c = _clock()
    st = _apres_succes(c)
    c.advance(30)
    st = record_result(st, "dhw_temperature", TransportStatus.TIMEOUT, c)
    snap = build_snapshot(st, V1_MEASUREMENTS, c)
    assert snap["chain"]["status"] == ChainStatus.OK.value
    assert snap["measurements"]["dhw_temperature"]["last_result"] == "timeout"


def test_ts_a_jour_a_chaque_construction() -> None:
    c = _clock()
    st = _apres_succes(c)
    premier = build_snapshot(st, V1_MEASUREMENTS, c)
    c.advance(30)
    second = build_snapshot(st, V1_MEASUREMENTS, c)
    assert premier["ts"] != second["ts"]
    assert second["ts"] == "2026-08-02T20:00:30Z"


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


def test_json_en_octets_utf8() -> None:
    brut = snapshot_to_json(build_snapshot(_initial(), V1_MEASUREMENTS, _clock()))
    assert isinstance(brut, bytes)
    assert json.loads(brut.decode("utf-8"))["schema"] == 1


def test_json_compact() -> None:
    brut = snapshot_to_json(build_snapshot(_initial(), V1_MEASUREMENTS, _clock()))
    assert b", " not in brut and b": " not in brut


def test_json_deterministe_et_trie() -> None:
    snap = build_snapshot(_initial(), V1_MEASUREMENTS, _clock())
    assert snapshot_to_json(snap) == snapshot_to_json(snap)
    decode = json.loads(snapshot_to_json(snap).decode("utf-8"))
    assert list(decode) == sorted(decode)


def test_json_refuse_les_valeurs_non_finies() -> None:
    """§6.2 : « `allow_nan` interdit »."""
    for interdite in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            snapshot_to_json({"schema": 1, "x": interdite})


def test_json_conserve_l_unicode_sans_echappement() -> None:
    assert snapshot_to_json({"x": "é"}) == '{"x":"é"}'.encode("utf-8")


def test_aller_retour_json_fidele() -> None:
    c = _clock()
    snap = build_snapshot(_apres_succes(c), V1_MEASUREMENTS, c)
    assert json.loads(snapshot_to_json(snap).decode("utf-8")) == snap


def test_legacy_json_dumps_non_reutilise() -> None:
    """`_legacy.primitives.json_dumps` emet `NaN` : il est classe accident."""
    source = pathlib.Path(snapshot_module.__file__).read_text(encoding="utf-8")
    assert "_legacy" not in source.replace("`boilerack._legacy", "")
    assert "allow_nan=False" in source


# ---------------------------------------------------------------------------
# Absence d'effet de bord
# ---------------------------------------------------------------------------

_INTERDITS = {"paho", "socket", "subprocess", "threading", "asyncio", "time", "os"}


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
    assert _modules_importes(snapshot_module) & _INTERDITS == set()


def test_aucune_horloge_systeme_lue() -> None:
    source = pathlib.Path(snapshot_module.__file__).read_text(encoding="utf-8")
    for interdit in ("datetime.now(", "utcnow(", "time.monotonic(", "time.time("):
        assert interdit not in source


def test_ne_depend_pas_du_paquet_mqtt() -> None:
    source = pathlib.Path(snapshot_module.__file__).read_text(encoding="utf-8")
    assert "transport.mqtt" not in source
    assert "adapters" not in source
