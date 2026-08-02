"""Adaptateur MQTT Paho v2 sous faux client : honnetete du `PublishHandle`,
course PUBACK, entree des messages bruts. Aucun reseau, aucun broker.
"""

from __future__ import annotations

import logging

import pytest

from boilerack.adapters.config import MqttConfig
from boilerack.adapters.mqtt_paho import PahoMqttClient
from boilerack.transport.mqtt import Message, MqttClient
from adapter_support import FakeMqttMessage, FakePahoClient


def _adapter(fake=None, **cfg):
    fake = fake or FakePahoClient()
    config = MqttConfig(host="broker.local", **cfg)
    return PahoMqttClient(config, client=fake), fake


# -- conformite ---------------------------------------------------------------

def test_conforme_au_protocole_mqttclient() -> None:
    adapter, _ = _adapter()
    assert isinstance(adapter, MqttClient)


# -- connexion / souscription -------------------------------------------------

def test_connexion_demarre_la_boucle_native() -> None:
    adapter, fake = _adapter(port=1884, keepalive=30)
    adapter.connect()
    assert fake.connected_args == ("broker.local", 1884, 30)
    assert fake.loop_started == 1


def test_on_connect_succes_puis_deconnexion_honnete() -> None:
    adapter, fake = _adapter()
    adapter.connect()
    fake.fire_on_connect(success=True)
    assert adapter.connected is True
    # Une deconnexion n'est jamais masquee en connexion saine.
    fake.fire_on_disconnect(reason=7)
    assert adapter.connected is False


def test_echec_de_connexion_ne_marque_pas_connecte() -> None:
    adapter, fake = _adapter()
    adapter.connect()
    fake.fire_on_connect(success=False)
    assert adapter.connected is False


def test_disconnect_arrete_la_boucle() -> None:
    adapter, fake = _adapter()
    adapter.disconnect()
    assert fake.loop_stopped == 1
    assert fake.disconnected == 1
    assert adapter.connected is False


def test_souscription_transmise() -> None:
    adapter, fake = _adapter()
    adapter.subscribe("boilerack/command", qos=1)
    assert fake.subscriptions == [("boilerack/command", 1)]


# -- publication : honnetete du PublishHandle ---------------------------------

def test_publish_qos1_non_retained_reste_demandee_sans_puback() -> None:
    adapter, fake = _adapter()
    handle = adapter.publish("boilerack/ack/mode", b"{}", qos=1, retain=False)
    # DEMANDEE : ni confirmee (pas de PUBACK), ni echouee. Le retour de publish()
    # ne vaut JAMAIS confirmation.
    assert handle.confirmed is False
    assert handle.failed is False
    assert fake.published[0]["qos"] == 1
    assert fake.published[0]["retain"] is False
    assert adapter.pending_publish_count == 1


def test_retour_immediat_echoue_marque_failed() -> None:
    fake = FakePahoClient(publish_rc=4)  # rc != MQTT_ERR_SUCCESS
    adapter, _ = _adapter(fake)
    handle = adapter.publish("t", b"x", qos=1)
    assert handle.failed is True
    assert handle.confirmed is False
    # non enregistre en attente : echec etabli immediat
    assert adapter.pending_publish_count == 0


def test_puback_confirme_le_handle() -> None:
    adapter, fake = _adapter()
    handle = adapter.publish("t", b"x", qos=1)
    mid = fake.published[0]["mid"]
    fake.fire_on_publish(mid)
    assert handle.confirmed is True
    assert handle.failed is False
    assert adapter.pending_publish_count == 0


def test_course_puback_avant_enregistrement() -> None:
    # Simule le PUBACK arrivant AVANT que publish() n'enregistre le handle :
    # on declenche on_publish pour le mid que le faux client attribuera ensuite.
    adapter, fake = _adapter()
    attendu = fake.next_mid  # mid que publish() va attribuer
    fake.fire_on_publish(attendu)  # PUBACK en avance
    handle = adapter.publish("t", b"x", qos=1)
    # Le handle est confirme immediatement a l'enregistrement (course geree).
    assert handle.confirmed is True
    assert adapter.pending_publish_count == 0


def test_double_callback_idempotent() -> None:
    adapter, fake = _adapter()
    handle = adapter.publish("t", b"x", qos=1)
    mid = fake.published[0]["mid"]
    fake.fire_on_publish(mid)
    fake.fire_on_publish(mid)  # rappel en double : aucune exception, reste confirme
    assert handle.confirmed is True
    assert handle.failed is False


def test_mid_inconnu_sans_faux_rattachement() -> None:
    adapter, fake = _adapter()
    handle = adapter.publish("t", b"x", qos=1)
    mid = fake.published[0]["mid"]
    fake.fire_on_publish(mid + 999)  # PUBACK d'un mid jamais publie
    # Le handle en attente n'est PAS confirme a tort.
    assert handle.confirmed is False
    assert handle.failed is False


def test_publication_non_confirmee_reste_demandee() -> None:
    adapter, fake = _adapter()
    h1 = adapter.publish("t", b"a", qos=1)
    h2 = adapter.publish("t", b"b", qos=1)
    # Seul le second recoit son PUBACK.
    fake.fire_on_publish(fake.published[1]["mid"])
    assert h2.confirmed is True
    assert h1.confirmed is False and h1.failed is False


# -- entree des messages ------------------------------------------------------

def test_message_entrant_remis_brut_au_handler() -> None:
    adapter, fake = _adapter()
    recu = []
    adapter.set_message_handler(recu.append)
    fake.fire_on_message(
        FakeMqttMessage(topic="boilerack/command", payload=b'{"x":1}', qos=1, dup=True)
    )
    assert len(recu) == 1
    msg = recu[0]
    assert isinstance(msg, Message)
    assert msg.topic == "boilerack/command"
    assert msg.payload == b'{"x":1}'
    assert msg.qos == 1
    assert msg.dup is True


def test_payload_binaire_non_utf8_reste_octets() -> None:
    adapter, fake = _adapter()
    recu = []
    adapter.set_message_handler(recu.append)
    brut = b"\xff\xfe\x00\x01"  # invalide en UTF-8
    fake.fire_on_message(FakeMqttMessage(topic="t", payload=brut))
    assert recu[0].payload == brut  # aucun decodage, octets preserves


def test_payload_vide() -> None:
    adapter, fake = _adapter()
    recu = []
    adapter.set_message_handler(recu.append)
    fake.fire_on_message(FakeMqttMessage(topic="t", payload=b""))
    assert recu[0].payload == b""


def test_topic_unicode() -> None:
    adapter, fake = _adapter()
    recu = []
    adapter.set_message_handler(recu.append)
    fake.fire_on_message(FakeMqttMessage(topic="boilerack/ack/chauffe-é", payload=b"x"))
    assert recu[0].topic == "boilerack/ack/chauffe-é"


def test_aucun_decodage_json_dans_l_adaptateur() -> None:
    # Un payload non-JSON est remis tel quel : l'adaptateur ne parse jamais.
    adapter, fake = _adapter()
    recu = []
    adapter.set_message_handler(recu.append)
    fake.fire_on_message(FakeMqttMessage(topic="t", payload=b"pas du json"))
    assert recu[0].payload == b"pas du json"


def test_handler_absent_message_ignore(caplog) -> None:
    adapter, fake = _adapter()
    with caplog.at_level(logging.WARNING):
        fake.fire_on_message(FakeMqttMessage(topic="t", payload=b"x"))
    assert any("sans handler" in r.message for r in caplog.records)


def test_handler_remplace() -> None:
    adapter, fake = _adapter()
    a, b = [], []
    adapter.set_message_handler(a.append)
    adapter.set_message_handler(b.append)  # remplace
    fake.fire_on_message(FakeMqttMessage(topic="t", payload=b"x"))
    assert a == [] and len(b) == 1


def test_exception_du_handler_capturee_non_propagee(caplog) -> None:
    adapter, fake = _adapter()

    def _boom(_msg):
        raise RuntimeError("handler casse")

    adapter.set_message_handler(_boom)
    with caplog.at_level(logging.ERROR):
        # Ne doit PAS remonter dans la boucle Paho.
        fake.fire_on_message(FakeMqttMessage(topic="t", payload=b"x"))
    assert any("handler" in r.message for r in caplog.records)
