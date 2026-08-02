"""Tests de l'execution transactionnelle : ecriture, mapping transport, relecture.

Applique les arbitrages ratifies :

- 1.a : `OK`/`TIMEOUT`/`UNUSABLE_OUTPUT`/`TRANSPORT_ERROR` -> relecture ->
  `applied`/`timeout` (jamais `bridge_unavailable`) ; `DAEMON_UNREACHABLE` ->
  `bridge_unavailable` ;
- 1.b : `UNKNOWN_COMMAND` a l'ecriture -> `unsupported_command` / `permanent` ;
- une seule invocation d'ecriture par transaction.
"""

from __future__ import annotations

from boilerack.core import Reason, ReasonClass
from boilerack.core.ack import AckStatus
from boilerack.transport import TransportStatus
from boilerack.transport.vclient import ReadResult, WriteResult
from support import Harness, message, payload, rid


def _submit_temp(h: Harness, value=21.0, request_id=None):
    request_id = request_id or rid(1)
    return h.core.submit(message(payload(request_id, "temp_consigne", value)))


# -- succes --------------------------------------------------------------------

def test_ecriture_ok_relecture_conforme_applied() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0, result=WriteResult(TransportStatus.OK))
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED
    h.vclient.assert_all_consumed()


def test_relecture_conforme_immediate() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0)
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED
    assert len(h.read_calls()) == 1  # confirmee des la premiere relecture


def test_plusieurs_relectures_avant_conformite() -> None:
    h = Harness(confirm_budget_s=5.0, confirm_interval_s=0.5)
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0)
    h.vclient.expect_read("get_temp_consigne", returns=20.0)  # hors tolerance (0.2)
    h.vclient.expect_read("get_temp_consigne", returns=20.5)  # hors tolerance (0.2)
    h.vclient.expect_read("get_temp_consigne", returns=21.0)  # conforme
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED
    assert len(h.read_calls()) == 3
    # Sans attente reelle : le temps virtuel a avance de 2 intervalles.
    assert h.clock.monotonic() == 1.0


def test_lecture_temporairement_en_echec_puis_conforme() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0)
    h.vclient.expect_read("get_temp_consigne", result=ReadResult(TransportStatus.TIMEOUT))
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED


def test_tolerance_flottante_confirme() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0)
    h.vclient.expect_read("get_temp_consigne", returns=21.15)  # dans la tolerance 0.2
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED


# -- 1.a : statuts potentiellement emis ---------------------------------------

def test_ecriture_timeout_puis_confirmee_applied() -> None:
    # L'ecriture peut avoir ete emise (TIMEOUT) : relecture conforme -> applied.
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0, result=WriteResult(TransportStatus.TIMEOUT))
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED


def test_sortie_inexploitable_a_l_ecriture_puis_confirmee() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write(
        "set_temp_consigne", 21.0, result=WriteResult(TransportStatus.UNUSABLE_OUTPUT)
    )
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED


def test_transport_error_a_l_ecriture_puis_confirmee() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write(
        "set_temp_consigne", 21.0, result=WriteResult(TransportStatus.TRANSPORT_ERROR)
    )
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED


def test_ecriture_potentiellement_emise_sans_confirmation_timeout() -> None:
    h = Harness(confirm_budget_s=1.0, confirm_interval_s=0.5)
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0, result=WriteResult(TransportStatus.TIMEOUT))
    for _ in range(3):  # relectures a t=0, 0.5, 1.0
        h.vclient.expect_read("get_temp_consigne", returns=20.0)  # jamais conforme
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.TIMEOUT
    h.vclient.assert_all_consumed()


def test_valeur_relue_incorrecte_jusqu_au_budget_timeout() -> None:
    h = Harness(confirm_budget_s=1.0, confirm_interval_s=0.5)
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0)
    for _ in range(3):
        h.vclient.expect_read("get_temp_consigne", returns=25.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.TIMEOUT


def test_valeur_relue_nan_ne_confirme_pas() -> None:
    # `ReadResult` durci interdit OK + NaN : une sortie NaN est portee par
    # UNUSABLE_OUTPUT et ne confirme jamais -> timeout.
    h = Harness(confirm_budget_s=1.0, confirm_interval_s=0.5)
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0)
    for _ in range(3):
        h.vclient.expect_read(
            "get_temp_consigne", result=ReadResult(TransportStatus.UNUSABLE_OUTPUT, raw="nan")
        )
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.TIMEOUT


# -- 1.a : DAEMON_UNREACHABLE / 1.b : UNKNOWN_COMMAND --------------------------

def test_ecriture_impossible_avant_invocation_bridge_unavailable() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write(
        "set_temp_consigne", 21.0, result=WriteResult(TransportStatus.DAEMON_UNREACHABLE)
    )
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.BRIDGE_UNAVAILABLE
    assert verdict.reason_class is ReasonClass.TRANSIENT
    # Aucune relecture : on ne confirme pas ce qui n'a pas ete emis.
    assert h.read_calls() == []


def test_commande_inconnue_unsupported_command() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write(
        "set_temp_consigne", 21.0, result=WriteResult(TransportStatus.UNKNOWN_COMMAND)
    )
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.UNSUPPORTED_COMMAND
    assert verdict.reason_class is ReasonClass.PERMANENT
    assert h.read_calls() == []


# -- une seule ecriture --------------------------------------------------------

def test_aucune_seconde_ecriture() -> None:
    h = Harness()
    _submit_temp(h, 21.0)
    h.vclient.expect_write("set_temp_consigne", 21.0)
    # Plusieurs relectures non conformes puis conforme : l'ecriture ne doit
    # jamais etre rejouee, seules les lectures se repetent.
    h.vclient.expect_read("get_temp_consigne", returns=20.0)
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    h.core.process_next()
    assert len(h.write_calls()) == 1


# -- arbitrage 2 : fail-closed sur accepted echoue ----------------------------

def test_fail_closed_si_accepted_echoue_avant_ecriture() -> None:
    h = Harness()
    h.mqtt.program_publish_failure(1)  # le prochain publish (accepted) echoue
    verdict = _submit_temp(h, 21.0)
    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.BRIDGE_UNAVAILABLE
    # Aucune ecriture, rien en file, identifiant libere.
    assert h.write_calls() == []
    assert h.core.queue_depth == 0
    assert h.core.in_flight_count == 0
    h.vclient.assert_all_consumed()


def test_accepted_demande_non_confirme_ne_bloque_pas_l_ecriture() -> None:
    # Publication de `accepted` demandee mais non confirmee (PUBACK non arrive) :
    # ce n'est PAS un echec etabli -> l'ecriture doit avoir lieu normalement.
    h = Harness()
    accepted = _submit_temp(h, 21.0)
    assert accepted.status is AckStatus.ACCEPTED
    handle = h.mqtt.publications[0]
    assert handle.confirmed is False and handle.failed is False  # simplement demandee
    h.vclient.expect_write("set_temp_consigne", 21.0)
    h.vclient.expect_read("get_temp_consigne", returns=21.0)
    verdict = h.core.process_next()
    assert verdict.status is AckStatus.APPLIED
