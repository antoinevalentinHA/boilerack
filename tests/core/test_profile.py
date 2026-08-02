"""Tests du schema de profil declaratif."""

from __future__ import annotations

import pytest

from boilerack.core.profile import CommandSpec, Profile, ProfileError, ValueType
from boilerack.testing import build_fake_profile


def _spec(**overrides) -> None:
    base = dict(
        role="r",
        read="get_r",
        write="set_r",
        type=ValueType.FLOAT,
        min=0.0,
        max=10.0,
        step=0.5,
        confirm_tolerance=0.1,
        idempotent=True,
        bounds_source="source fictive",
    )
    base.update(overrides)
    CommandSpec(**base)


def test_profil_factice_valide() -> None:
    profile = build_fake_profile()
    assert profile.get("temp_consigne").writable is True
    assert profile.get("sonde").writable is False
    assert profile.get("inconnu") is None


def test_read_seul_sans_surface_ecriture() -> None:
    spec = CommandSpec(
        role="ro", read="get_ro", write=None, type=ValueType.FLOAT,
        min=0.0, max=1.0, step=0.1, confirm_tolerance=0.0,
        idempotent=True, bounds_source="src",
    )
    assert spec.writable is False


def test_idempotence_obligatoire() -> None:
    with pytest.raises(ProfileError, match="idempotent"):
        _spec(idempotent=False)


def test_bounds_source_obligatoire() -> None:
    with pytest.raises(ProfileError, match="bounds_source"):
        _spec(bounds_source="")


def test_step_strictement_positif() -> None:
    with pytest.raises(ProfileError, match="step"):
        _spec(step=0.0)


def test_min_inferieur_ou_egal_max() -> None:
    with pytest.raises(ProfileError, match="min"):
        _spec(min=5.0, max=1.0)


def test_type_entier_exige_bornes_entieres() -> None:
    with pytest.raises(ProfileError, match="integer"):
        _spec(type=ValueType.INTEGER, min=0.0, max=3.5, step=1)


def test_cle_de_role_coherente() -> None:
    spec = CommandSpec(
        role="a", read="g", write="s", type=ValueType.FLOAT,
        min=0.0, max=1.0, step=0.1, confirm_tolerance=0.0,
        idempotent=True, bounds_source="src",
    )
    with pytest.raises(ProfileError, match="cle de role"):
        Profile(name="p", commands={"b": spec})
