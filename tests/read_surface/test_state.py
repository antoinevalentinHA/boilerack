"""Tests de `boilerack.read_surface.state` — §6.5, §7.3 et §8.2 de C7-B."""

from __future__ import annotations

import ast
import pathlib
from datetime import datetime, timedelta, timezone

import pytest

from boilerack.read_surface import state as state_module
from boilerack.read_surface.measurements import V1_MEASUREMENTS, MeasurementSpec
from boilerack.read_surface.state import (
    ChainStatus,
    MeasurementState,
    ReadSurfaceState,
    complete_cycle,
    record_result,
)
from boilerack.testing import VirtualClock
from boilerack.transport.vclient import TransportStatus

_DEBUT = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)
_ECHECS = [s for s in TransportStatus if s is not TransportStatus.OK]


def _clock(monotonic_start: float = 1000.0) -> VirtualClock:
    return VirtualClock(_DEBUT, monotonic_start=monotonic_start)


def _initial() -> ReadSurfaceState:
    return ReadSurfaceState.initial(V1_MEASUREMENTS)


# ---------------------------------------------------------------------------
# Etat initial
# ---------------------------------------------------------------------------


def test_etat_initial_couvre_les_huit_roles() -> None:
    st = _initial()
    assert set(st.measurements) == {s.role for s in V1_MEASUREMENTS}


def test_etat_initial_de_chaque_mesure() -> None:
    """§7.3 : avant la premiere lecture, aucune valeur, aucun resultat."""
    for etat in _initial().measurements.values():
        assert etat.last_success_wall is None
        assert etat.last_success_monotonic is None
        assert etat.last_result is None
        assert etat.has_value is False


def test_chaine_initiale() -> None:
    """§8.2 : avant le premier cycle termine, `unavailable` et cause nulle."""
    st = _initial()
    assert st.chain_status is ChainStatus.UNAVAILABLE
    assert st.chain_cause is None
    assert st.cycle_completed is False


def test_collection_reellement_immutable() -> None:
    st = _initial()
    with pytest.raises(TypeError):
        st.measurements["supply_temperature"] = MeasurementState()  # type: ignore[index]


def test_collection_isolee_de_la_source() -> None:
    """Muter le dictionnaire fourni ne doit pas alterer l'etat construit."""
    source = {"a": MeasurementState()}
    st = ReadSurfaceState(measurements=source)
    source["b"] = MeasurementState()
    assert set(st.measurements) == {"a"}


def test_etat_gele() -> None:
    with pytest.raises(Exception):
        _initial().cycle_completed = True  # type: ignore[misc]


def test_chain_cause_interdite_quand_ok() -> None:
    with pytest.raises(ValueError, match="nulle quand chain_status vaut ok"):
        ReadSurfaceState(
            measurements={},
            chain_status=ChainStatus.OK,
            chain_cause=TransportStatus.TIMEOUT,
        )


# ---------------------------------------------------------------------------
# Invariants de `MeasurementState`
# ---------------------------------------------------------------------------


def test_estampilles_solidaires_wall_seule() -> None:
    with pytest.raises(ValueError, match="ensemble"):
        MeasurementState(last_success_wall=_DEBUT)


def test_estampilles_solidaires_monotone_seul() -> None:
    with pytest.raises(ValueError, match="ensemble"):
        MeasurementState(last_success_monotonic=10.0)


def test_datetime_naif_refuse() -> None:
    with pytest.raises(ValueError, match="fuseau horaire"):
        MeasurementState(
            last_success_wall=datetime(2026, 8, 2, 20, 0, 0), last_success_monotonic=1.0
        )


def test_datetime_normalise_vers_utc() -> None:
    autre = timezone(timedelta(hours=2))
    etat = MeasurementState(
        last_success_wall=datetime(2026, 8, 2, 22, 0, 0, tzinfo=autre),
        last_success_monotonic=1.0,
    )
    assert etat.last_success_wall == _DEBUT
    assert etat.last_success_wall.tzinfo is timezone.utc


@pytest.mark.parametrize("mono", [float("nan"), float("inf"), float("-inf")])
def test_monotone_non_fini_refuse(mono: float) -> None:
    with pytest.raises(ValueError, match="fini"):
        MeasurementState(last_success_wall=_DEBUT, last_success_monotonic=mono)


def test_last_result_doit_etre_un_transport_status() -> None:
    with pytest.raises(ValueError, match="TransportStatus"):
        MeasurementState(last_result="ok")  # type: ignore[arg-type]


def test_has_value_est_derive_et_non_stocke() -> None:
    import dataclasses

    champs = {f.name for f in dataclasses.fields(MeasurementState)}
    assert champs == {"last_success_wall", "last_success_monotonic", "last_result"}
    assert isinstance(MeasurementState.has_value, property)


def test_aucune_valeur_scalaire_stockee() -> None:
    import dataclasses

    champs = {f.name for f in dataclasses.fields(MeasurementState)}
    assert not champs & {"value", "last_value", "raw", "detail", "last_attempt"}


# ---------------------------------------------------------------------------
# `record_result` — succes
# ---------------------------------------------------------------------------


def test_succes_initial() -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    etat = st.measurements["supply_temperature"]
    assert etat.last_success_wall == _DEBUT
    assert etat.last_success_monotonic == 1000.0
    assert etat.last_result is TransportStatus.OK
    assert etat.has_value is True


def test_succes_ulterieur_deplace_les_deux_estampilles() -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    c.advance(30)
    st = record_result(st, "supply_temperature", TransportStatus.OK, c)
    etat = st.measurements["supply_temperature"]
    assert etat.last_success_wall == _DEBUT + timedelta(seconds=30)
    assert etat.last_success_monotonic == 1030.0


def test_succes_ne_touche_aucune_autre_mesure() -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    for role, etat in st.measurements.items():
        if role != "supply_temperature":
            assert etat.last_result is None and etat.has_value is False


def test_record_result_ne_touche_pas_la_chaine() -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    assert st.chain_status is ChainStatus.UNAVAILABLE
    assert st.cycle_completed is False


def test_etat_source_inchange() -> None:
    c = _clock()
    avant = _initial()
    record_result(avant, "supply_temperature", TransportStatus.OK, c)
    assert avant.measurements["supply_temperature"].has_value is False


# ---------------------------------------------------------------------------
# `record_result` — echec
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("statut", _ECHECS, ids=[s.name for s in _ECHECS])
def test_echec_avant_tout_succes(statut: TransportStatus) -> None:
    c = _clock()
    st = record_result(_initial(), "supply_temperature", statut, c)
    etat = st.measurements["supply_temperature"]
    assert etat.last_result is statut
    assert etat.has_value is False
    assert etat.last_success_wall is None and etat.last_success_monotonic is None


@pytest.mark.parametrize("statut", _ECHECS, ids=[s.name for s in _ECHECS])
def test_echec_apres_succes_conserve_les_estampilles(statut: TransportStatus) -> None:
    """§7.3 : un echec isole ne perime pas la derniere valeur connue."""
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    c.advance(30)
    st = record_result(st, "supply_temperature", statut, c)
    etat = st.measurements["supply_temperature"]
    assert etat.last_success_wall == _DEBUT
    assert etat.last_success_monotonic == 1000.0
    assert etat.last_result is statut
    assert etat.has_value is True


def test_echec_ne_lit_pas_l_horloge() -> None:
    """Aucun `sleep` ni avance : l'horloge n'est sollicitee que sur un succes."""
    c = _clock()
    record_result(_initial(), "supply_temperature", TransportStatus.TIMEOUT, c)
    assert c.now() == _DEBUT and c.monotonic() == 1000.0


# ---------------------------------------------------------------------------
# `record_result` — erreurs de programmation
# ---------------------------------------------------------------------------


def test_role_inconnu_refuse() -> None:
    with pytest.raises(ValueError, match="role inconnu"):
        record_result(_initial(), "inexistant", TransportStatus.OK, _clock())


@pytest.mark.parametrize("statut", ["ok", None, 1, True])
def test_statut_invalide_refuse(statut: object) -> None:
    with pytest.raises(ValueError, match="TransportStatus"):
        record_result(_initial(), "supply_temperature", statut, _clock())  # type: ignore[arg-type]


class _HorlogeBancale:
    """Double local : `VirtualClock` fait avancer mural et monotone ensemble."""

    def __init__(self, wall: object, monotonic: object) -> None:
        self._wall, self._monotonic = wall, monotonic

    def now(self):  # type: ignore[no-untyped-def]
        return self._wall

    def monotonic(self):  # type: ignore[no-untyped-def]
        return self._monotonic

    def sleep(self, seconds: float) -> None:  # pragma: no cover - jamais appele
        raise AssertionError("aucun sommeil ne doit etre demande")


def test_horloge_murale_naive_refusee() -> None:
    bancale = _HorlogeBancale(datetime(2026, 8, 2, 20, 0, 0), 1000.0)
    with pytest.raises(ValueError, match="fuseau horaire"):
        record_result(_initial(), "supply_temperature", TransportStatus.OK, bancale)  # type: ignore[arg-type]


@pytest.mark.parametrize("mono", [float("nan"), float("inf")])
def test_monotone_non_fini_refuse_a_l_enregistrement(mono: float) -> None:
    bancale = _HorlogeBancale(_DEBUT, mono)
    with pytest.raises(ValueError, match="fini"):
        record_result(_initial(), "supply_temperature", TransportStatus.OK, bancale)  # type: ignore[arg-type]


def test_recul_monotone_refuse() -> None:
    """Borner a zero publierait la fraicheur maximale pour une horloge cassee."""
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, _clock())
    recule = _HorlogeBancale(_DEBUT + timedelta(seconds=10), 900.0)
    with pytest.raises(ValueError, match="recule"):
        record_result(st, "supply_temperature", TransportStatus.OK, recule)  # type: ignore[arg-type]


def test_recul_monotone_non_detectable_sur_une_autre_mesure() -> None:
    """Le controle est LOCAL : aucune coherence globale d'horloge n'est supposee."""
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, _clock())
    recule = _HorlogeBancale(_DEBUT, 900.0)
    st = record_result(st, "dhw_temperature", TransportStatus.OK, recule)  # type: ignore[arg-type]
    assert st.measurements["dhw_temperature"].last_success_monotonic == 900.0


# ---------------------------------------------------------------------------
# `complete_cycle`
# ---------------------------------------------------------------------------


def _cycle(st: ReadSurfaceState, resultats: dict[str, TransportStatus], c: VirtualClock):
    for role, statut in resultats.items():
        st = record_result(st, role, statut, c)
    return complete_cycle(st, resultats)


def test_cycle_entierement_reussi() -> None:
    c = _clock()
    st = _cycle(
        _initial(),
        {"supply_temperature": TransportStatus.OK, "dhw_temperature": TransportStatus.OK},
        c,
    )
    assert st.chain_status is ChainStatus.OK
    assert st.chain_cause is None
    assert st.cycle_completed is True


def test_cycle_partiellement_reussi() -> None:
    c = _clock()
    st = _cycle(
        _initial(),
        {
            "supply_temperature": TransportStatus.OK,
            "dhw_temperature": TransportStatus.TIMEOUT,
        },
        c,
    )
    assert st.chain_status is ChainStatus.DEGRADED
    assert st.chain_cause is TransportStatus.TIMEOUT


def test_cycle_entierement_echoue() -> None:
    c = _clock()
    st = _cycle(
        _initial(),
        {
            "supply_temperature": TransportStatus.TIMEOUT,
            "dhw_temperature": TransportStatus.UNUSABLE_OUTPUT,
        },
        c,
    )
    assert st.chain_status is ChainStatus.UNAVAILABLE
    assert st.chain_cause is TransportStatus.TIMEOUT


def test_cycle_d_une_seule_mesure_reussie() -> None:
    c = _clock()
    st = _cycle(_initial(), {"supply_temperature": TransportStatus.OK}, c)
    assert st.chain_status is ChainStatus.OK


@pytest.mark.parametrize(
    ("melange", "attendue"),
    [
        (
            (TransportStatus.UNKNOWN_COMMAND, TransportStatus.DAEMON_UNREACHABLE),
            TransportStatus.DAEMON_UNREACHABLE,
        ),
        (
            (TransportStatus.TIMEOUT, TransportStatus.TRANSPORT_ERROR),
            TransportStatus.TRANSPORT_ERROR,
        ),
        (
            (TransportStatus.UNUSABLE_OUTPUT, TransportStatus.TIMEOUT),
            TransportStatus.TIMEOUT,
        ),
        (
            (TransportStatus.UNKNOWN_COMMAND, TransportStatus.UNUSABLE_OUTPUT),
            TransportStatus.UNUSABLE_OUTPUT,
        ),
        ((TransportStatus.UNKNOWN_COMMAND,), TransportStatus.UNKNOWN_COMMAND),
    ],
)
def test_cause_la_plus_severe(
    melange: tuple[TransportStatus, ...], attendue: TransportStatus
) -> None:
    """§8.2 : daemon_unreachable > transport_error > timeout > unusable_output
    > unsupported_command."""
    c = _clock()
    roles = [s.role for s in V1_MEASUREMENTS][: len(melange)]
    st = _cycle(_initial(), dict(zip(roles, melange)), c)
    assert st.chain_cause is attendue


def test_ordre_de_severite_couvre_tous_les_echecs() -> None:
    """Aucun statut non-`OK` ne peut echapper a la table de severite."""
    assert set(state_module._SEVERITY) == set(_ECHECS)


def test_cycle_ne_modifie_aucune_mesure() -> None:
    c = _clock()
    avant = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    apres = complete_cycle(avant, {"supply_temperature": TransportStatus.OK})
    assert apres.measurements["supply_temperature"] == avant.measurements[
        "supply_temperature"
    ]


def test_mesure_non_incluse_reste_inchangee() -> None:
    c = _clock()
    st = _cycle(_initial(), {"supply_temperature": TransportStatus.OK}, c)
    assert st.measurements["dhw_temperature"].last_result is None


def test_cause_ignore_les_mesures_hors_cycle() -> None:
    """Un echec ancien, non retente, ne doit pas contaminer la cause du cycle."""
    c = _clock()
    st = record_result(
        _initial(), "dhw_temperature", TransportStatus.DAEMON_UNREACHABLE, c
    )
    st = record_result(st, "supply_temperature", TransportStatus.TIMEOUT, c)
    st = complete_cycle(st, {"supply_temperature": TransportStatus.TIMEOUT})
    assert st.chain_cause is TransportStatus.TIMEOUT


def test_cycle_vide_refuse() -> None:
    """§8.2 : un ensemble vide satisferait vacuement « termine » et basculerait
    la chaine en `unavailable`."""
    with pytest.raises(ValueError, match="cycle vide"):
        complete_cycle(_initial(), {})


def test_cycle_role_inconnu_refuse() -> None:
    with pytest.raises(ValueError, match="role inconnu"):
        complete_cycle(_initial(), {"inexistant": TransportStatus.OK})


def test_cycle_statut_invalide_refuse() -> None:
    with pytest.raises(ValueError, match="TransportStatus"):
        complete_cycle(_initial(), {"supply_temperature": "ok"})  # type: ignore[dict-item]


def test_cycle_non_mapping_refuse() -> None:
    with pytest.raises(ValueError, match="Mapping"):
        complete_cycle(_initial(), [("supply_temperature", TransportStatus.OK)])  # type: ignore[arg-type]


def test_incoherence_avec_last_result_refusee() -> None:
    """Le cycle annonce un statut que `record_result` n'a pas enregistre."""
    c = _clock()
    st = record_result(_initial(), "supply_temperature", TransportStatus.OK, c)
    with pytest.raises(ValueError, match="incoherence"):
        complete_cycle(st, {"supply_temperature": TransportStatus.TIMEOUT})


def test_cloture_sans_enregistrement_prealable_refusee() -> None:
    with pytest.raises(ValueError, match="incoherence"):
        complete_cycle(_initial(), {"supply_temperature": TransportStatus.OK})


def test_cycle_suivant_remplace_la_chaine() -> None:
    c = _clock()
    st = _cycle(_initial(), {"supply_temperature": TransportStatus.TIMEOUT}, c)
    assert st.chain_status is ChainStatus.UNAVAILABLE
    c.advance(30)
    st = _cycle(st, {"supply_temperature": TransportStatus.OK}, c)
    assert st.chain_status is ChainStatus.OK
    assert st.chain_cause is None


# ---------------------------------------------------------------------------
# Absence d'effet de bord
# ---------------------------------------------------------------------------

_INTERDITS = {"paho", "socket", "subprocess", "threading", "asyncio", "time", "os", "json"}


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
    assert _modules_importes(state_module) & _INTERDITS == set()


def test_aucune_horloge_systeme_lue() -> None:
    """L'horloge est toujours injectee : aucun appel direct a la stdlib."""
    source = pathlib.Path(state_module.__file__).read_text(encoding="utf-8")
    for interdit in ("datetime.now(", "utcnow(", "time.monotonic(", "time.time("):
        assert interdit not in source


def test_ne_depend_pas_du_paquet_mqtt() -> None:
    source = pathlib.Path(state_module.__file__).read_text(encoding="utf-8")
    assert "transport.mqtt" not in source
    assert "adapters" not in source


def test_declaration_utilisable_hors_v1() -> None:
    """L'etat n'est pas cable sur les huit : toute collection valide convient."""
    spec = MeasurementSpec(
        role="x", read="getX", suffix="telemetry/x", period_s=10, fresh_max_s=30
    )
    st = ReadSurfaceState.initial([spec])
    assert set(st.measurements) == {"x"}
