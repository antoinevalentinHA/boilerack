"""Tests du modele public de transport MQTT — `MqttWill`.

Ces tests portent sur la FRONTIERE elle-meme, pas sur un adaptateur ni sur un
double : ils vivent donc a cote du module qu'ils verrouillent.

Chaque garde de `MqttWill.__post_init__` doit avoir ici au moins un cas qui
echoue si on la retire. Les messages d'exception ne sont pas verifies : ils ne
sont pas contractuels.
"""

from __future__ import annotations

import dataclasses

import pytest

from boilerack.transport import MqttWill

_VALIDE = dict(topic="boiler/bridge/online", payload=b"offline", qos=1, retain=True)


def _will(**surcharges: object) -> MqttWill:
    return MqttWill(**{**_VALIDE, **surcharges})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Cas valides
# ---------------------------------------------------------------------------


def test_testament_de_reference_accepte() -> None:
    will = MqttWill(
        topic="boiler/bridge/online", payload=b"offline", qos=1, retain=True
    )
    assert (will.topic, will.payload, will.qos, will.retain) == (
        "boiler/bridge/online",
        b"offline",
        1,
        True,
    )


@pytest.mark.parametrize("qos", [0, 1, 2])
def test_les_trois_qos_mqtt_acceptes(qos: int) -> None:
    assert _will(qos=qos).qos == qos


@pytest.mark.parametrize("retain", [True, False])
def test_les_deux_booleens_acceptes(retain: bool) -> None:
    assert _will(retain=retain).retain is retain


def test_payload_vide_accepte() -> None:
    """Un testament de longueur nulle est licite en MQTT."""
    assert _will(payload=b"").payload == b""


def test_topic_multi_niveaux_accepte() -> None:
    assert _will(topic="maison/boiler/bridge/online").topic.count("/") == 3


def test_topic_d_espaces_accepte() -> None:
    """LIMITE CONSTATEE, non corrigee ici : le validateur ne refuse que la
    chaine strictement vide, pas une chaine d'espaces.

    Le contrat ne dit rien des espaces (§3.3 est muet sur ce point pour les
    prefixes, et rien ne les interdit dans un topic MQTT). Ce test fige donc le
    comportement REEL plutot que de le presumer.
    """
    assert _will(topic="   ").topic == "   "


# ---------------------------------------------------------------------------
# Topic
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("topic", ["", None, 42, b"boiler/bridge/online"])
def test_topic_non_textuel_ou_vide_refuse(topic: object) -> None:
    with pytest.raises(ValueError):
        _will(topic=topic)


@pytest.mark.parametrize("topic", ["+", "a/+", "a/+/b", "#", "a/#", "a#b"])
def test_jokers_mqtt_refuses(topic: str) -> None:
    """Un topic de PUBLICATION ne peut pas porter de joker."""
    with pytest.raises(ValueError):
        _will(topic=topic)


@pytest.mark.parametrize(
    "controle", ["\n", "\r", "\t", "\x00", "\x01", "\x1f", "\x7f", "\x9f"]
)
def test_caracteres_de_controle_refuses(controle: str) -> None:
    with pytest.raises(ValueError):
        _will(topic=f"boiler{controle}online")


# ---------------------------------------------------------------------------
# Payload
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    ["offline", bytearray(b"offline"), memoryview(b"offline"), None, 0, ["offline"]],
)
def test_payload_non_bytes_refuse(payload: object) -> None:
    """Le contrat exige STRICTEMENT `bytes` : ni `str`, ni tampon assimilable."""
    with pytest.raises(ValueError):
        _will(payload=payload)


# ---------------------------------------------------------------------------
# QoS
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("qos", [True, False])
def test_qos_booleen_refuse(qos: bool) -> None:
    """`isinstance(True, int)` vaut `True` : le booleen doit etre ecarte."""
    with pytest.raises(ValueError):
        _will(qos=qos)


@pytest.mark.parametrize("qos", [-1, 3, 42])
def test_qos_hors_plage_refuse(qos: int) -> None:
    with pytest.raises(ValueError):
        _will(qos=qos)


@pytest.mark.parametrize("qos", [1.0, 0.5, "1", None])
def test_qos_non_entier_refuse(qos: object) -> None:
    with pytest.raises(ValueError):
        _will(qos=qos)


# ---------------------------------------------------------------------------
# Retain
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("retain", [0, 1, None, "true", "", 1.0])
def test_retain_non_booleen_refuse(retain: object) -> None:
    """Seuls `True` et `False` reels sont admis, jamais un equivalent."""
    with pytest.raises(ValueError):
        _will(retain=retain)


# ---------------------------------------------------------------------------
# Immutabilite
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("champ", ["topic", "payload", "qos", "retain"])
def test_dataclass_gelee(champ: str) -> None:
    will = _will()
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(will, champ, None)


def test_egalite_structurelle() -> None:
    assert _will() == _will()
    assert _will() != _will(qos=0)


def test_champs_exacts() -> None:
    champs = [f.name for f in dataclasses.fields(MqttWill)]
    assert champs == ["topic", "payload", "qos", "retain"]
