"""Adaptateur MQTT Paho v2 sous faux client : honnetete du `PublishHandle`,
course PUBACK, entree des messages bruts. Aucun reseau, aucun broker.
"""

from __future__ import annotations

import logging

import pytest

from boilerack.adapters.config import MqttConfig
from boilerack.adapters.mqtt_paho import PahoMqttClient
from boilerack.transport.mqtt import (
    ConnectionEvents,
    Message,
    MqttClient,
    MqttWill,
    PresenceMqttClient,
)
from adapter_support import FakeMqttMessage, FakePahoClient


class FakePahoWithWill(FakePahoClient):
    """`FakePahoClient` etendu du testament, avec journal d'appels ORDONNE.

    L'extension vit ici plutot que dans `adapter_support` : seul ce module
    exerce `connect()`, et l'ordre `will_set` -> `connect` -> `loop_start` est
    precisement ce que ces tests doivent prouver.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calls: list = []
        self.will_sets: list = []
        self.will_clears: int = 0

    def will_set(self, topic, payload=None, qos=0, retain=False):
        self.will_sets.append((topic, payload, qos, retain))
        self.calls.append("will_set")

    def will_clear(self):
        self.will_clears += 1
        self.calls.append("will_clear")

    def connect(self, host, port, keepalive):
        self.calls.append("connect")
        super().connect(host, port, keepalive)

    def loop_start(self):
        self.calls.append("loop_start")
        super().loop_start()

    def loop_stop(self):
        self.calls.append("loop_stop")
        super().loop_stop()

    def disconnect(self):
        self.calls.append("disconnect")
        super().disconnect()


_WILL = MqttWill(topic="boiler/bridge/online", payload=b"offline", qos=1, retain=True)


def _adapter(fake=None, **cfg):
    fake = fake or FakePahoWithWill()
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


# -- testament ----------------------------------------------------------------

def test_testament_pose_avant_la_connexion() -> None:
    """Paho : « will_set must be called before connect() to have any effect »."""
    adapter, fake = _adapter()
    adapter.connect(will=_WILL)
    assert fake.calls == ["will_set", "connect", "loop_start"]


def test_arguments_exacts_du_testament() -> None:
    adapter, fake = _adapter()
    adapter.connect(will=_WILL)
    assert fake.will_sets == [("boiler/bridge/online", b"offline", 1, True)]
    assert fake.will_clears == 0


def test_sans_testament_le_precedent_est_efface() -> None:
    """Sans `will_clear()`, un testament anterieur survivrait silencieusement."""
    adapter, fake = _adapter()
    adapter.connect(will=_WILL)
    adapter.connect()
    assert fake.calls == [
        "will_set", "connect", "loop_start",
        "will_clear", "connect", "loop_start",
    ]
    assert fake.will_clears == 1


def test_connexion_sans_testament_n_appelle_jamais_will_set() -> None:
    adapter, fake = _adapter()
    adapter.connect()
    assert fake.will_sets == []
    assert fake.will_clears == 1
    assert fake.connected_args == ("broker.local", 1883, 60)


def test_deconnexion_inchangee_par_le_testament() -> None:
    """La sequence de deconnexion existante n'est pas touchee par ce lot."""
    adapter, fake = _adapter()
    adapter.connect(will=_WILL)
    adapter.disconnect()
    assert fake.calls == [
        "will_set", "connect", "loop_start", "loop_stop", "disconnect",
    ]
    assert adapter.connected is False


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


def test_course_puback_pendant_enregistrement() -> None:
    # Course RÉELLE : le PUBACK arrive PENDANT `publish()` (fenêtre de corrélation
    # ouverte), le `mid` étant attribué à l'intérieur de `client.publish()`.
    fake = FakePahoClient(ack_during_publish=True)
    adapter, _ = _adapter(fake)
    handle = adapter.publish("t", b"x", qos=1)
    # Confirmé par le crédit d'ACK précoce légitime, consommé à l'enregistrement.
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


# -- C4-CORR : registre PUBACK borné et réutilisation de mid sûre -------------

def test_ack_orphelin_hors_fenetre_non_memorise() -> None:
    # Aucun publish en cours : un PUBACK orphelin (mid inconnu) ne doit créer
    # AUCUN crédit persistant.
    adapter, fake = _adapter()
    for m in range(1000, 1050):
        fake.fire_on_publish(m)  # 50 PUBACK orphelins, hors de toute fenêtre
    assert adapter._early_acks == set()  # rien mémorisé -> pas de croissance


def test_double_ack_apres_confirmation_ne_cree_pas_de_credit_futur() -> None:
    adapter, fake = _adapter()
    h1 = adapter.publish("t", b"a", qos=1)
    mid = fake.published[0]["mid"]
    fake.fire_on_publish(mid)   # confirme h1
    fake.fire_on_publish(mid)   # double PUBACK, hors fenêtre -> abandonné
    assert h1.confirmed is True
    assert adapter._early_acks == set()


def test_reutilisation_de_mid_ne_confirme_pas_sans_nouveau_puback() -> None:
    # Scénario C4-1 : un ACK obsolète ne doit JAMAIS confirmer une publication
    # ultérieure réutilisant le même mid.
    adapter, fake = _adapter()
    h1 = adapter.publish("t", b"a", qos=1)
    mid = fake.published[0]["mid"]
    fake.fire_on_publish(mid)   # confirme h1
    fake.fire_on_publish(mid)   # double PUBACK obsolète (hors fenêtre -> abandonné)
    # Réutilisation forcée du même mid par une nouvelle publication.
    fake.next_mid = mid
    h2 = adapter.publish("t", b"b", qos=1)
    # h2 NE doit PAS être confirmé sans son propre PUBACK.
    assert h2.confirmed is False
    assert h2.failed is False
    assert adapter.pending_publish_count == 1
    # Son vrai PUBACK, lui, confirme.
    fake.fire_on_publish(mid)
    assert h2.confirmed is True


def test_early_acks_purge_a_la_quiescence() -> None:
    # Même sous publications concurrentes simulées, aucun crédit ne survit à la
    # quiescence (plus aucune publication en enregistrement).
    adapter, fake = _adapter()
    h = adapter.publish("t", b"a", qos=1)
    fake.fire_on_publish(fake.published[0]["mid"])  # confirme h
    fake.fire_on_publish(4242)  # orphelin hors fenêtre
    assert adapter._early_acks == set()
    assert adapter._registering == 0


def test_ack_orphelin_stocke_en_fenetre_est_purge_a_la_quiescence() -> None:
    # Un ACK orphelin (mid 9999) arrive PENDANT la fenêtre d'un publish concurrent :
    # il est déposé comme crédit, mais DOIT être purgé dès la quiescence, sinon il
    # pourrait confirmer à tort une réutilisation ultérieure de ce mid.
    fake = FakePahoClient(orphan_ack_during_publish=9999)
    adapter, _ = _adapter(fake)
    h = adapter.publish("t", b"a", qos=1)  # fenêtre ouverte -> 9999 crédité, puis purgé
    assert adapter._early_acks == set()    # purge effective (sans elle, {9999} survivrait)
    fake.fire_on_publish(fake.published[0]["mid"])  # PUBACK propre de A -> confirme, vide _pending
    assert h.confirmed is True
    assert adapter.pending_publish_count == 0
    # Réutilisation du mid orphelin : aucune confirmation sans PUBACK propre.
    fake.orphan_ack_during_publish = None
    fake.next_mid = 9999
    h2 = adapter.publish("t", b"b", qos=1)
    assert h2.confirmed is False
    assert adapter.pending_publish_count == 1


def test_qos0_confirmation_est_une_remise_locale_pas_broker() -> None:
    # QoS 0 : `on_publish` = remise LOCALE a Paho, PAS un accusé broker. La
    # sémantique diffère de QoS 1 (PUBACK) meme si le champ `confirmed` est le
    # meme type. Ce test verrouille le QoS transmis et documente la différence.
    adapter, fake = _adapter()
    h0 = adapter.publish("boilerack/ack/mode", b"{}", qos=0, retain=False)
    assert fake.published[0]["qos"] == 0
    assert h0.confirmed is False  # tant qu'aucun on_publish n'est survenu
    fake.fire_on_publish(fake.published[0]["mid"])
    # `confirmed` ici signifie « remis localement au transport », PAS « recu par
    # le broker » : un consommateur ne doit pas y lire la garantie d'un PUBACK QoS 1.
    assert h0.confirmed is True


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


# ---------------------------------------------------------------------------
# C11 — capacite de cycle de connexion
# ---------------------------------------------------------------------------


class _ReasonCode:
    """Double FIDELE au `ReasonCode` de Paho 2.1.0 sur le seul point qui compte.

    Le vrai objet expose `is_failure` et **ne supporte pas** `int()` : la
    conversion y leve. Un double qui se contenterait d'un entier emprunterait le
    chemin de repli de `_reason_is_success` et laisserait la discrimination
    reelle de C11 sans preuve.

    Borne a cet usage : ce double ne pretend rien reproduire d'autre de Paho.
    """

    def __init__(self, is_failure: bool) -> None:
        self.is_failure = is_failure

    def __int__(self) -> int:  # pragma: no cover - doit lever, jamais reussir
        raise TypeError("int() n'est pas supporte par ReasonCode")

    def __str__(self) -> str:
        return "echec" if self.is_failure else "succes"


def _connecte(adapter):
    """Enregistre un collecteur de transitions et le rend."""
    vues: list[bool] = []
    adapter.set_connection_handler(vues.append)
    return vues


def test_adaptateur_porte_la_capacite_de_connexion() -> None:
    adapter, _ = _adapter()
    assert isinstance(adapter, ConnectionEvents)
    assert isinstance(adapter, PresenceMqttClient)


def test_connack_reussi_notifie_vrai() -> None:
    adapter, fake = _adapter()
    vues = _connecte(adapter)
    fake.on_connect(fake, None, {}, _ReasonCode(is_failure=False), None)
    assert vues == [True]
    assert adapter.connected is True


def test_connack_echoue_notifie_faux() -> None:
    """R6 : obligatoire. Sans cela, une reussite ulterieure n'est plus une transition."""
    adapter, fake = _adapter()
    vues = _connecte(adapter)
    fake.on_connect(fake, None, {}, _ReasonCode(is_failure=True), None)
    assert vues == [False]
    assert adapter.connected is False


def test_is_failure_est_reellement_lu_et_non_le_repli_entier() -> None:
    """`int()` leve sur le vrai `ReasonCode` : seul `is_failure` est praticable."""
    with pytest.raises(TypeError):
        int(_ReasonCode(is_failure=False))
    adapter, fake = _adapter()
    vues = _connecte(adapter)
    fake.on_connect(fake, None, {}, _ReasonCode(is_failure=False), None)
    fake.on_connect(fake, None, {}, _ReasonCode(is_failure=True), None)
    assert vues == [True, False]


def test_deconnexion_notifie_faux() -> None:
    adapter, fake = _adapter()
    vues = _connecte(adapter)
    fake.fire_on_disconnect(reason=7)
    assert vues == [False]


def test_sans_handler_les_transitions_ne_levent_pas() -> None:
    """Un consommateur sans obligation de presence n'enregistre rien : legitime."""
    adapter, fake = _adapter()
    fake.fire_on_connect(success=True)
    fake.fire_on_disconnect(reason=7)  # ne doit rien lever


def test_handler_remplace_pour_la_connexion() -> None:
    adapter, fake = _adapter()
    a, b = [], []
    adapter.set_connection_handler(a.append)
    adapter.set_connection_handler(b.append)
    fake.fire_on_connect(success=True)
    assert a == [] and b == [True]


def test_enregistrement_du_handler_ne_rejoue_aucun_etat() -> None:
    """Enregistrer apres coup ne fabrique pas une transition qui n'a pas eu lieu."""
    adapter, fake = _adapter()
    fake.fire_on_connect(success=True)
    vues = _connecte(adapter)
    assert vues == []


def test_exception_du_handler_de_connexion_absorbee(caplog) -> None:
    """Paho relancerait l'exception dans sa boucle reseau : elle meurt ici."""
    adapter, fake = _adapter()

    def _boom(_connected):
        raise RuntimeError("handler de connexion casse")

    adapter.set_connection_handler(_boom)
    with caplog.at_level(logging.ERROR):
        fake.fire_on_connect(success=True)
        fake.fire_on_disconnect(reason=7)
    assert any("handler de connexion" in r.message for r in caplog.records)


def test_le_callback_est_possible_seulement_apres_l_ouverture_reseau() -> None:
    """R4 : `loop_start()` est le DERNIER appel de `connect()`.

    C'est ce qui rend sure la base posee avant l'ouverture : tant que la boucle
    reseau n'est pas armee, aucun rappel ne peut survenir. Verrouille ici pour
    qu'un reordonnancement de `connect()` ne passe pas inapercu.
    """
    fake = FakePahoWithWill()
    adapter = PahoMqttClient(MqttConfig(host="h"), client=fake)
    adapter.connect(will=_WILL)
    assert fake.calls == ["will_set", "connect", "loop_start"]
    assert fake.calls[-1] == "loop_start"


def test_aucun_second_will_set_hors_connexion() -> None:
    """Le testament est pose une fois ; Paho le reemet dans ses CONNECT suivants."""
    fake = FakePahoWithWill()
    adapter = PahoMqttClient(MqttConfig(host="h"), client=fake)
    adapter.set_connection_handler(lambda _c: None)
    adapter.connect(will=_WILL)
    fake.fire_on_disconnect(reason=7)
    fake.fire_on_connect(success=True)
    assert len(fake.will_sets) == 1
