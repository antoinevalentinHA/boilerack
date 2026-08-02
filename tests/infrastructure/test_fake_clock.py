"""Tests de l'horloge virtuelle et de l'horloge systeme."""

from datetime import datetime, timedelta, timezone

import pytest

from boilerack.clock import Clock, SystemClock
from boilerack.testing import VirtualClock

START = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_les_deux_horloges_satisfont_le_protocole() -> None:
    assert isinstance(SystemClock(), Clock)
    assert isinstance(VirtualClock(START), Clock)


def test_instant_initial_fixe() -> None:
    clock = VirtualClock(START, monotonic_start=100.0)
    assert clock.now() == START
    assert clock.monotonic() == 100.0


def test_instant_initial_exige_un_fuseau() -> None:
    with pytest.raises(ValueError, match="aware"):
        VirtualClock(datetime(2026, 1, 1, 12, 0, 0))


def test_now_ne_depend_pas_de_l_heure_reelle() -> None:
    """Deux lectures successives sans avance rendent exactement le meme instant."""
    clock = VirtualClock(START)
    premier = clock.now()
    deuxieme = clock.now()
    assert premier == deuxieme == START


def test_advance_fait_progresser_utc_et_monotone_ensemble() -> None:
    clock = VirtualClock(START, monotonic_start=0.0)
    clock.advance(30.0)
    assert clock.now() == START + timedelta(seconds=30)
    assert clock.monotonic() == 30.0


def test_sleep_avance_le_temps_sans_attente_reelle() -> None:
    clock = VirtualClock(START, monotonic_start=0.0)
    clock.sleep(5.0)
    assert clock.now() == START + timedelta(seconds=5)
    assert clock.monotonic() == 5.0


def test_historique_des_sommeils() -> None:
    clock = VirtualClock(START)
    clock.sleep(1.0)
    clock.sleep(2.5)
    clock.sleep(0.0)
    assert clock.sleeps == (1.0, 2.5, 0.0)


def test_advance_refuse_une_duree_negative() -> None:
    clock = VirtualClock(START)
    with pytest.raises(ValueError, match="negative"):
        clock.advance(-1.0)


def test_sleep_refuse_une_duree_negative() -> None:
    clock = VirtualClock(START)
    with pytest.raises(ValueError, match="negative"):
        clock.sleep(-0.001)
    assert clock.sleeps == ()  # rien enregistre si refuse


def test_sequence_deterministe() -> None:
    """Deux horloges pilotees a l'identique produisent exactement le meme etat."""
    a = VirtualClock(START)
    b = VirtualClock(START)
    for pas in (1.0, 3.0, 0.5):
        a.advance(pas)
        b.advance(pas)
    assert a.now() == b.now()
    assert a.monotonic() == b.monotonic()


# ----------------------------------------------------------
# Horloge systeme (production) — verifications sans attente reelle
# ----------------------------------------------------------


def test_system_clock_now_est_aware_utc() -> None:
    maintenant = SystemClock().now()
    assert maintenant.tzinfo is not None
    assert maintenant.utcoffset() == timedelta(0)


def test_system_clock_monotonic_est_un_flottant() -> None:
    assert isinstance(SystemClock().monotonic(), float)


def test_system_clock_refuse_un_sommeil_negatif() -> None:
    with pytest.raises(ValueError, match="negative"):
        SystemClock().sleep(-1.0)
