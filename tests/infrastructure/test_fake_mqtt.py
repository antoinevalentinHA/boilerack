"""Tests du double du transport MQTT."""

import pytest

from boilerack.testing import FakeMqttClient
from boilerack.transport import Message, MqttClient, NotConnectedError
from boilerack.transport.mqtt import MqttWill

_WILL = MqttWill(topic="boiler/bridge/online", payload=b"offline", qos=1, retain=True)


def _connected() -> FakeMqttClient:
    client = FakeMqttClient()
    client.connect()
    return client


def test_conforme_au_protocole() -> None:
    assert isinstance(FakeMqttClient(), MqttClient)


def test_mqtt_will_reexporte_publiquement() -> None:
    """`MqttWill` fait partie de l'API publique de `boilerack.transport`."""
    from boilerack.transport import MqttWill as Public
    from boilerack.transport.mqtt import MqttWill as Direct

    assert Public is Direct


def test_exports_historiques_de_transport_conserves() -> None:
    import boilerack.transport as transport

    historiques = {
        "Message", "MessageHandler", "MqttClient", "NotConnectedError",
        "Publication", "PublishHandle", "Subscription",
        "ReadResult", "TransportStatus", "VClient", "WriteResult",
    }
    assert historiques <= set(transport.__all__)
    assert "MqttWill" in transport.__all__
    assert all(hasattr(transport, nom) for nom in transport.__all__)


def test_conformite_isinstance_ne_prouve_pas_le_testament() -> None:
    """`runtime_checkable` ne verifie QUE la presence des methodes.

    Un double dont `connect()` ignorerait le testament satisferait encore
    `isinstance`. La conformite reelle doit donc etre etablie par le
    COMPORTEMENT, ce que fait le test suivant.
    """

    class SansTestament:
        def connect(self): ...
        def disconnect(self): ...
        def subscribe(self, topic, qos=0): ...
        def publish(self, topic, payload, qos=0, retain=False): ...
        def set_message_handler(self, handler): ...

    assert isinstance(SansTestament(), MqttClient)


def test_testament_reellement_conserve() -> None:
    """Test de COMPORTEMENT : le double accepte et retient le testament."""
    client = FakeMqttClient()
    assert client.connected_will is None
    client.connect(will=_WILL)
    assert client.connected_will == _WILL
    assert client.connected_will.payload == b"offline"
    assert (client.connected_will.qos, client.connected_will.retain) == (1, True)


def test_connexion_sans_testament_efface_le_precedent() -> None:
    client = FakeMqttClient()
    client.connect(will=_WILL)
    client.disconnect()
    client.connect()
    assert client.connected_will is None


def test_testament_n_est_jamais_emis_automatiquement() -> None:
    """Un double de connexion n'invente aucune deconnexion brutale."""
    client = FakeMqttClient()
    client.connect(will=_WILL)
    assert client.publications == ()
    client.disconnect()
    assert client.publications == ()


def test_publication_enregistree_exactement() -> None:
    client = _connected()
    client.publish("t/topic", b"payload", qos=1, retain=True)
    pub = client.publications[0].publication
    assert pub.topic == "t/topic"
    assert pub.payload == b"payload"
    assert pub.qos == 1
    assert pub.retain is True


def test_qos_et_retain_preserves() -> None:
    client = _connected()
    client.publish("a", b"x", qos=2, retain=False)
    client.publish("b", b"y", qos=0, retain=True)
    a, b = client.publications
    assert (a.publication.qos, a.publication.retain) == (2, False)
    assert (b.publication.qos, b.publication.retain) == (0, True)


def test_ordre_des_messages() -> None:
    client = _connected()
    for i in range(3):
        client.publish(f"topic/{i}", str(i).encode(), qos=0)
    topics = [h.publication.topic for h in client.publications]
    assert topics == ["topic/0", "topic/1", "topic/2"]


def test_publication_demandee_puis_confirmee() -> None:
    client = _connected()
    handle = client.publish("t", b"m", qos=1)
    assert handle.confirmed is False
    assert handle.failed is False

    client.confirm_pending()
    assert handle.confirmed is True
    assert handle.failed is False


def test_echec_de_publication_programme() -> None:
    client = _connected()
    client.program_publish_failure()
    handle = client.publish("t", b"m", qos=1)
    assert handle.failed is True
    assert handle.confirmed is False

    # confirm_pending ne doit pas ressusciter une publication echouee.
    client.confirm_pending()
    assert handle.confirmed is False
    assert handle.failed is True


def test_echec_puis_publication_normale() -> None:
    client = _connected()
    client.program_publish_failure(1)
    premiere = client.publish("t", b"1")
    seconde = client.publish("t", b"2")
    assert premiere.failed is True
    assert seconde.failed is False


def test_publication_sans_connexion_refusee() -> None:
    client = FakeMqttClient()
    with pytest.raises(NotConnectedError):
        client.publish("t", b"m")


def test_souscription_sans_connexion_refusee() -> None:
    client = FakeMqttClient()
    with pytest.raises(NotConnectedError):
        client.subscribe("t")


def test_souscriptions_enregistrees() -> None:
    client = _connected()
    client.subscribe("cmd/+", qos=1)
    client.subscribe("state/#", qos=0)
    paires = [(s.topic, s.qos) for s in client.subscriptions]
    assert paires == [("cmd/+", 1), ("state/#", 0)]


def test_connexion_et_deconnexion_enregistrees() -> None:
    client = FakeMqttClient()
    assert client.connected is False
    client.connect()
    client.disconnect()
    assert client.connected is False
    assert client.connection_events == ("connect", "disconnect")


def test_message_entrant_avec_dup() -> None:
    client = _connected()
    recus: list[Message] = []
    client.set_message_handler(recus.append)

    client.deliver(Message(topic="cmd", payload=b"{}", qos=1, dup=True))

    assert len(recus) == 1
    assert recus[0].dup is True
    assert client.inbox[0].dup is True


def test_message_entrant_par_defaut_non_dup() -> None:
    client = _connected()
    client.deliver(Message(topic="cmd", payload=b"{}"))
    assert client.inbox[0].dup is False


def test_aucune_publication_sans_appel() -> None:
    client = _connected()
    assert client.publications == ()
    assert client.subscriptions == ()
