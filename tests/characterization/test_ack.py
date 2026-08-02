"""Caracterisation des payloads d'ACK et d'erreur, et de la serialisation JSON.

Sources : `publish_ack` L328-345 et `publish_error` L348-366, dont la
construction de payload a ete extraite mecaniquement ; `json_dumps` L134-135.

Ces deux fonctions d'origine melangent construction et publication MQTT :
elles ne sont pas isolables telles quelles. Seul le corps est reproduit.
"""

import json

import pytest

from boilerack._legacy.primitives import (
    json_dumps,
    legacy_build_ack_payload,
    legacy_build_error_payload,
)

REQ = "550e8400-e29b-41d4-a716-446655440000"
TS = "2026-08-01T10:00:00Z"


@pytest.mark.reference
@pytest.mark.parametrize("statut", ["accepted", "applied", "timeout"])
def test_ack_sans_raison_ne_porte_que_trois_cles(statut: str) -> None:
    """`reason` est absent — et non pas present a `null`. La distinction compte
    pour un consommateur qui teste la presence de la cle."""
    payload = legacy_build_ack_payload(REQ, statut, TS)
    assert payload == {"request_id": REQ, "status": statut, "ts": TS}
    assert "reason" not in payload


@pytest.mark.reference
def test_ack_rejete_porte_la_raison() -> None:
    payload = legacy_build_ack_payload(REQ, "rejected", TS, reason="invalid_step")
    assert payload == {
        "request_id": REQ,
        "status": "rejected",
        "ts": TS,
        "reason": "invalid_step",
    }


@pytest.mark.reference
def test_l_ordre_des_cles_est_stable() -> None:
    """L'ordre d'insertion est deterministe en Python 3.7+ et `json_dumps` ne
    trie pas : la serialisation est donc reproductible a l'octet."""
    payload = legacy_build_ack_payload(REQ, "rejected", TS, reason="expired")
    assert list(payload.keys()) == ["request_id", "status", "ts", "reason"]
    assert json_dumps(payload) == (
        '{"request_id":"' + REQ + '","status":"rejected","ts":"' + TS + '","reason":"expired"}'
    )


@pytest.mark.accident
def test_aucun_controle_du_statut_ni_de_la_raison() -> None:
    """La fonction accepte n'importe quelle chaine comme statut ou raison.

    Rien n'empeche de publier un statut hors de la machine a quatre etats. La
    protection n'existe que par convention d'appel.

    Classe ACCIDENT : le produit public devra typer ces valeurs.
    """
    payload = legacy_build_ack_payload(REQ, "statut_inexistant", TS, reason="raison_inventee")
    assert payload["status"] == "statut_inexistant"
    assert payload["reason"] == "raison_inventee"


@pytest.mark.reference
def test_payload_erreur_complet() -> None:
    payload = legacy_build_error_payload(
        request_id=REQ,
        domain="heating",
        action="set_curve_slope",
        reason="write_timeout",
        details="No confirmation from getNeigungM1",
        ts=TS,
    )
    assert list(payload.keys()) == ["request_id", "domain", "action", "reason", "details", "ts"]
    assert payload["request_id"] == REQ


@pytest.mark.reference
def test_payload_erreur_admet_un_request_id_nul() -> None:
    """Le champ est present et vaut `null` — contrairement a `reason` dans l'ACK,
    qui est absent. Les deux conventions coexistent dans le meme composant."""
    payload = legacy_build_error_payload(None, "dhw", "set_setpoint", "bridge_exception", "boom", TS)
    assert payload["request_id"] is None
    assert '"request_id":null' in json_dumps(payload)


# ----------------------------------------------------------
# Serialisation
# ----------------------------------------------------------


@pytest.mark.reference
def test_serialisation_compacte_sans_espace() -> None:
    assert json_dumps({"a": 1, "b": 2}) == '{"a":1,"b":2}'


@pytest.mark.reference
def test_non_ascii_conserve_tel_quel() -> None:
    """`ensure_ascii=False` : les accents ne sont pas echappes.

    Le payload est donc emis en UTF-8 reel, ce qui suppose un consommateur
    qui le decode comme tel.
    """
    rendu = json_dumps({"details": "confirmation non obtenue — délai dépassé"})
    assert "délai dépassé" in rendu
    assert "\\u" not in rendu


@pytest.mark.reference
def test_aller_retour_json() -> None:
    payload = legacy_build_ack_payload(REQ, "applied", TS)
    assert json.loads(json_dumps(payload)) == payload


@pytest.mark.accident
def test_valeurs_flottantes_speciales_produisent_un_json_invalide() -> None:
    """`json.dumps` emet NaN et Infinity, qui ne sont PAS du JSON valide.

    Aucun payload actuel ne contient de flottant, le defaut n'est donc pas
    atteignable aujourd'hui. Il le deviendrait si une valeur numerique etait
    ajoutee a un ACK sans validation prealable.

    Classe ACCIDENT : le produit public devra utiliser `allow_nan=False`.
    """
    rendu = json_dumps({"v": float("nan")})
    assert rendu == '{"v":NaN}'

    # Le decodeur de Python accepte NaN et Infinity par defaut : le probleme
    # ne se voit qu'avec un decodeur strict, comme en aurait un consommateur
    # ecrit dans un autre langage.
    def _strict(constante: str) -> None:
        raise ValueError(f"jeton non conforme au JSON : {constante}")

    assert json.loads(rendu)["v"] != json.loads(rendu)["v"]  # NaN accepte tel quel
    with pytest.raises(ValueError, match="non conforme"):
        json.loads(rendu, parse_constant=_strict)
