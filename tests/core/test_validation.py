"""Tests de validation pilotee par le profil (forme, type, borne, pas, role).

La validation est exercee au travers du coeur (`submit`) : le verdict d'un rejet
est un ACK terminal `rejected` porteur d'une raison typee.
"""

from __future__ import annotations

import math

import pytest

from boilerack.core import Reason, ReasonClass, validate
from boilerack.core.ack import AckStatus
from boilerack.core.validation import Rejection, ValidatedCommand
from boilerack.testing import build_fake_profile
from support import START, Harness, message, payload, rid


def _submit(h: Harness, pb: bytes):
    return h.core.submit(message(pb))


def _reject_reason(pb: bytes) -> Reason:
    result = validate(pb, build_fake_profile(), START)
    assert isinstance(result, Rejection)
    return result.reason


# -- forme / UUID --------------------------------------------------------------

def test_uuid_canonique_admis() -> None:
    h = Harness()
    ack = _submit(h, payload(rid(1), "mode", 2))
    assert ack.status is AckStatus.ACCEPTED


def test_uuid_majuscule_refuse() -> None:
    # UUID v4 valide comportant des lettres hexadecimales, en MAJUSCULES.
    upper = "AAAAAAAA-0000-4000-8000-AAAAAAAAAAAA"
    assert _reject_reason(payload(upper, "mode", 2)) is Reason.INVALID_PAYLOAD


def test_payload_incomplet() -> None:
    assert _reject_reason(payload(rid(1), "mode", 2, drop=("expires_at",))) is Reason.INVALID_PAYLOAD


def test_champ_supplementaire() -> None:
    pb = payload(rid(1), "mode", 2, extra={"unexpected": 1})
    assert _reject_reason(pb) is Reason.INVALID_PAYLOAD


def test_payload_non_json() -> None:
    assert _reject_reason(b"pas du json") is Reason.INVALID_PAYLOAD


# -- type / finitude -----------------------------------------------------------

def test_booleen_refuse() -> None:
    assert _reject_reason(payload(rid(1), "mode", True)) is Reason.INVALID_TYPE


def test_chaine_numerique_refusee() -> None:
    assert _reject_reason(payload(rid(1), "mode", "2")) is Reason.INVALID_TYPE


def test_nan_refuse() -> None:
    # NaN injecte via une constante JSON non standard, capturee a la finitude.
    pb = b'{"request_id":"%s","ts":"%s","expires_at":"%s","source":"t","role":"mode","value":NaN}' % (
        rid(1).encode(),
        START.isoformat().encode(),
        START.isoformat().encode(),
    )
    assert _reject_reason(pb) is Reason.INVALID_TYPE


def test_infinities_refusees() -> None:
    for token in (b"Infinity", b"-Infinity"):
        pb = b'{"request_id":"%s","ts":"%s","expires_at":"%s","source":"t","role":"temp_consigne","value":%s}' % (
            rid(1).encode(),
            START.isoformat().encode(),
            (START.isoformat()).encode(),
            token,
        )
        assert _reject_reason(pb) is Reason.INVALID_TYPE


# -- valeurs entieres / flottantes ---------------------------------------------

def test_entier_admis() -> None:
    result = validate(payload(rid(1), "mode", 2), build_fake_profile(), START)
    assert isinstance(result, ValidatedCommand)
    assert result.target == 2 and isinstance(result.target, int)


def test_flottant_entier_admis_et_normalise() -> None:
    # 2.0 represente l'entier 2 pour un role entier.
    result = validate(payload(rid(1), "mode", 2.0), build_fake_profile(), START)
    assert isinstance(result, ValidatedCommand)
    assert result.target == 2 and isinstance(result.target, int)


def test_borne_basse_admise() -> None:
    result = validate(payload(rid(1), "temp_consigne", 10.0), build_fake_profile(), START)
    assert isinstance(result, ValidatedCommand)


def test_borne_haute_admise() -> None:
    result = validate(payload(rid(1), "temp_consigne", 30.0), build_fake_profile(), START)
    assert isinstance(result, ValidatedCommand)


def test_hors_borne_refuse() -> None:
    assert _reject_reason(payload(rid(1), "temp_consigne", 30.5)) is Reason.INVALID_VALUE_OUT_OF_RANGE
    assert _reject_reason(payload(rid(1), "temp_consigne", 9.5)) is Reason.INVALID_VALUE_OUT_OF_RANGE


def test_pas_exact_admis() -> None:
    result = validate(payload(rid(1), "temp_consigne", 20.5), build_fake_profile(), START)
    assert isinstance(result, ValidatedCommand)
    assert result.target == pytest.approx(20.5)


def test_artefact_flottant_hors_pas_refuse() -> None:
    # 20.4 n'est pas sur la grille 0.5 ; il ne doit jamais etre arrondi.
    assert _reject_reason(payload(rid(1), "temp_consigne", 20.4)) is Reason.INVALID_STEP


def test_valeur_intermediaire_hors_pas_refusee() -> None:
    assert _reject_reason(payload(rid(1), "temp_consigne", 20.25)) is Reason.INVALID_STEP


def test_priorite_borne_avant_pas() -> None:
    # Valeur a la fois hors borne ET hors grille -> la borne l'emporte (etape 4 < 5).
    assert _reject_reason(payload(rid(1), "temp_consigne", 40.3)) is Reason.INVALID_VALUE_OUT_OF_RANGE


# -- role ----------------------------------------------------------------------

def test_role_absent_refuse() -> None:
    assert _reject_reason(payload(rid(1), "inconnu", 1)) is Reason.INVALID_PAYLOAD


def test_role_lecture_seule_refuse() -> None:
    # `sonde` n'a pas de surface d'ecriture.
    assert _reject_reason(payload(rid(1), "sonde", 5.0)) is Reason.INVALID_PAYLOAD


# -- classes de raison ---------------------------------------------------------

def test_classes_de_raison_permanentes() -> None:
    from boilerack.core.ack import REASON_CLASS

    for reason in (
        Reason.INVALID_PAYLOAD,
        Reason.INVALID_TYPE,
        Reason.INVALID_VALUE_OUT_OF_RANGE,
        Reason.INVALID_STEP,
    ):
        assert REASON_CLASS[reason] is ReasonClass.PERMANENT
