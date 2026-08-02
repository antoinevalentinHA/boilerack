"""Tests du double programmable du transport `vcontrold`."""

from datetime import datetime, timezone

import pytest

from boilerack.testing import (
    FakeVClient,
    RecordedCall,
    UnconsumedExpectations,
    UnexpectedCall,
    VirtualClock,
)
from boilerack.transport import ReadResult, TransportStatus, VClient, WriteResult

START = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def _fake() -> FakeVClient:
    return FakeVClient(VirtualClock(START))


def test_conforme_au_protocole() -> None:
    assert isinstance(_fake(), VClient)


def test_sequence_lecture_ecriture_relecture() -> None:
    fake = _fake()
    fake.expect_read("get_value", returns=42.0)
    fake.expect_write("set_value", 50, result=WriteResult(TransportStatus.OK))
    fake.expect_read("get_value", returns=50.0)

    assert fake.read("get_value") == ReadResult(TransportStatus.OK, value=42.0)
    assert fake.write("set_value", 50).ok is True
    assert fake.read("get_value").value == 50.0

    fake.assert_all_consumed()


def test_ordre_exact_des_appels_enregistre() -> None:
    fake = _fake()
    fake.expect_read("get_value", returns=1.0)
    fake.expect_write("set_value", 7, result=WriteResult(TransportStatus.OK))

    fake.read("get_value")
    fake.write("set_value", 7)

    assert fake.calls == (
        RecordedCall("read", "get_value", None),
        RecordedCall("write", "set_value", 7),
    )


def test_appel_inattendu_quand_sequence_epuisee() -> None:
    fake = _fake()
    with pytest.raises(UnexpectedCall, match="plus aucune interaction"):
        fake.read("get_value")


def test_appel_inattendu_mauvaise_operation() -> None:
    fake = _fake()
    fake.expect_read("get_value", returns=1.0)
    with pytest.raises(UnexpectedCall, match="attendu read"):
        fake.write("set_value", 3)


def test_appel_inattendu_mauvaise_commande() -> None:
    fake = _fake()
    fake.expect_read("get_value", returns=1.0)
    with pytest.raises(UnexpectedCall, match="attendu read 'get_value'"):
        fake.read("get_other")


def test_arguments_incorrects_sur_ecriture() -> None:
    fake = _fake()
    fake.expect_write("set_value", 50, result=WriteResult(TransportStatus.OK))
    with pytest.raises(UnexpectedCall, match="argument inattendu"):
        fake.write("set_value", 51)


def test_reponse_programmee_non_consommee() -> None:
    fake = _fake()
    fake.expect_read("get_value", returns=1.0)
    fake.expect_read("get_value", returns=2.0)
    fake.read("get_value")

    assert len(fake.unconsumed()) == 1
    with pytest.raises(UnconsumedExpectations, match="1 interaction"):
        fake.assert_all_consumed()


def test_timeout_en_lecture() -> None:
    fake = _fake()
    fake.expect_read("get_value", result=ReadResult(TransportStatus.TIMEOUT))
    resultat = fake.read("get_value")
    assert resultat.status is TransportStatus.TIMEOUT
    assert resultat.value is None
    assert resultat.ok is False


def test_demon_indisponible_en_ecriture() -> None:
    fake = _fake()
    fake.expect_write(
        "set_value", 50, result=WriteResult(TransportStatus.DAEMON_UNREACHABLE)
    )
    resultat = fake.write("set_value", 50)
    assert resultat.status is TransportStatus.DAEMON_UNREACHABLE


def test_sortie_invalide_en_lecture() -> None:
    fake = _fake()
    fake.expect_read(
        "get_value",
        result=ReadResult(TransportStatus.UNUSABLE_OUTPUT, raw="---"),
    )
    resultat = fake.read("get_value")
    assert resultat.status is TransportStatus.UNUSABLE_OUTPUT
    assert resultat.value is None
    assert resultat.raw == "---"


def test_latence_virtuelle_fait_avancer_l_horloge_sans_attente() -> None:
    clock = VirtualClock(START)
    fake = FakeVClient(clock)
    fake.expect_read("get_value", returns=1.0, latency=2.5)

    debut = clock.monotonic()
    fake.read("get_value")
    assert clock.monotonic() - debut == 2.5


def test_operation_bloquee_jusqu_au_depassement_d_un_budget() -> None:
    """Une operation « bloquee » se programme en TIMEOUT + latence > budget.

    Le budget est un ecart de temps monotone ; on prouve que l'horloge le
    depasse, sans aucune attente reelle.
    """
    clock = VirtualClock(START)
    fake = FakeVClient(clock)
    budget_secondes = 3.0
    fake.expect_read(
        "get_value",
        result=ReadResult(TransportStatus.TIMEOUT),
        latency=5.0,
    )

    echeance = clock.monotonic() + budget_secondes
    resultat = fake.read("get_value")

    assert resultat.status is TransportStatus.TIMEOUT
    assert clock.monotonic() > echeance  # le budget est depasse
