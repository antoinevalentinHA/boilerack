"""Modeles de configuration immuables et valides (C4, section 8)."""

from __future__ import annotations

import math

import pytest

from boilerack.adapters.config import MqttConfig, VclientConfig


# -- MqttConfig ---------------------------------------------------------------

def test_mqtt_config_valeurs_par_defaut() -> None:
    cfg = MqttConfig(host="broker.local")
    assert cfg.port == 1883
    assert cfg.client_id == "boilerack"
    assert cfg.keepalive == 60
    assert cfg.tls is False
    assert cfg.command_topic == "boilerack/command"
    assert cfg.ack_topic_prefix == "boilerack/ack"


def test_mqtt_config_est_immuable() -> None:
    cfg = MqttConfig(host="broker.local")
    with pytest.raises(Exception):
        cfg.host = "autre"  # type: ignore[misc]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"host": ""},
        {"host": "broker.local", "port": 0},
        {"host": "broker.local", "port": 70000},
        {"host": "broker.local", "port": True},
        {"host": "broker.local", "client_id": ""},
        {"host": "broker.local", "keepalive": 0},
        {"host": "broker.local", "keepalive": -1},
        {"host": "broker.local", "command_topic": ""},
        {"host": "broker.local", "ack_topic_prefix": ""},
    ],
)
def test_mqtt_config_refuse_les_valeurs_invalides(kwargs) -> None:
    with pytest.raises(ValueError):
        MqttConfig(**kwargs)


def test_mqtt_config_repr_masque_le_mot_de_passe() -> None:
    cfg = MqttConfig(host="broker.local", username="u", password="s3cr3t")
    texte = repr(cfg)
    assert "s3cr3t" not in texte
    assert "***" in texte
    # la simple presence est visible, jamais la valeur
    assert "password='***'" in texte or 'password="***"' in texte


def test_mqtt_config_repr_sans_mot_de_passe() -> None:
    cfg = MqttConfig(host="broker.local")
    assert "***" not in repr(cfg)
    assert "password=None" in repr(cfg)


def test_mqtt_config_aucun_secret_par_defaut() -> None:
    cfg = MqttConfig(host="broker.local")
    assert cfg.username is None
    assert cfg.password is None


# -- VclientConfig ------------------------------------------------------------

def test_vclient_config_minimal() -> None:
    cfg = VclientConfig(executable="/usr/bin/vclient")
    assert cfg.read_timeout_s == 5.0
    assert cfg.write_timeout_s == 5.0
    assert cfg.host is None
    assert cfg.port is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"executable": ""},
        {"executable": "/x", "read_timeout_s": 0},
        {"executable": "/x", "read_timeout_s": -1.0},
        {"executable": "/x", "write_timeout_s": 0},
        {"executable": "/x", "read_timeout_s": math.inf},
        {"executable": "/x", "write_timeout_s": math.nan},
        {"executable": "/x", "host": ""},
        {"executable": "/x", "port": 0},
        {"executable": "/x", "port": 99999},
    ],
)
def test_vclient_config_refuse_les_valeurs_invalides(kwargs) -> None:
    with pytest.raises(ValueError):
        VclientConfig(**kwargs)


def test_vclient_config_est_immuable() -> None:
    cfg = VclientConfig(executable="/usr/bin/vclient")
    with pytest.raises(Exception):
        cfg.executable = "/autre"  # type: ignore[misc]
