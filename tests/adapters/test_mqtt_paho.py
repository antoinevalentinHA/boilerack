"""Adaptateur MQTT Paho v2 sous faux client : honnetete du `PublishHandle`,
course PUBACK, entree des messages bruts. Aucun reseau, aucun broker.
"""

from __future__ import annotations

import logging
import threading

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


# ---------------------------------------------------------------------------
# W0 — Persistance fonctionnelle des souscriptions
# ---------------------------------------------------------------------------
#
# Autorite : docs/design/w0-mqtt-subscription-recovery.md
#
# Tous ces tests sont HORS LIGNE et DETERMINISTES : faux client Paho, callbacks
# declenches explicitement, aucune concurrence reelle, aucun `sleep`. Les deux
# preuves d'ordonnancement — enregistrement avant transmission, notification
# avant restauration — reposent sur une OBSERVATION prise par le faux client au
# moment precis de son appel, jamais sur un ordonnancement suppose.
#
# Ces tests inspectent `_souscriptions` et `_lock`, membres internes de
# l'adaptateur. C'est voulu : le contrat W0 §6 fait du registre un mecanisme
# INTERNE, et lui ajouter une surface publique pour le seul confort des tests
# serait une dette gratuite.


def _adaptateur_observe(**kwargs):
    """Adaptateur cable a un faux client qui l'observe. Non connecte."""
    fake = FakePahoClient(**kwargs)
    adapter = PahoMqttClient(MqttConfig(host="h"), client=fake)
    fake.adaptateur = adapter
    return adapter, fake


def _registre(adapter) -> dict:
    return dict(adapter._souscriptions)


# -- enregistrement ---------------------------------------------------------


def test_subscribe_enregistre_l_intention() -> None:
    """W-P1 : un registre local existe, indexe par topic."""
    adapter, _ = _adaptateur_observe()
    adapter.subscribe("a/b", qos=1)
    assert _registre(adapter) == {"a/b": 1}


def test_subscribe_transmet_au_client() -> None:
    """La transmission directe a bien lieu : W0 n'en supprime aucune."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a/b", qos=1)
    assert fake.subscriptions == [("a/b", 1)]


def test_l_enregistrement_precede_la_transmission() -> None:
    """W-P2, observe AU MOMENT de l'appel, non deduit de l'ordre du code."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a/b", qos=2)
    assert fake.observations[0]["deja_enregistre"] is True
    assert fake.observations[0]["registre"] == {"a/b": 2}


def test_l_intention_survit_a_un_echec_de_transmission() -> None:
    """W-P3 et W0 §7.1 : l'irretractabilite vaut aussi apres un echec."""
    adapter, fake = _adaptateur_observe(echec_subscribe={"a/b"})
    with pytest.raises(RuntimeError):
        adapter.subscribe("a/b", qos=1)
    assert _registre(adapter) == {"a/b": 1}


def test_l_intention_echouee_est_reemise_au_connack() -> None:
    """La contrepartie de W0 §7.1 : ce qui reste declare est bien rejoue."""
    adapter, fake = _adaptateur_observe(echec_subscribe={"a/b"})
    with pytest.raises(RuntimeError):
        adapter.subscribe("a/b", qos=1)
    fake.echec_subscribe.clear()
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("a/b", 1)]


def test_subscribe_hors_connexion_enregistre_et_transmet() -> None:
    """R2 : le comportement de PahoMqttClient hors connexion, eprouve.

    Aucune harmonisation avec `FakeMqttClient`, qui leve `NotConnectedError` :
    W0 §2 limite sa portee a l'adaptateur Paho, et les deux semantiques
    coexistent volontairement.
    """
    adapter, fake = _adaptateur_observe()
    assert adapter.connected is False
    adapter.subscribe("a/b", qos=1)
    assert _registre(adapter) == {"a/b": 1}
    assert fake.subscriptions == [("a/b", 1)]
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("a/b", 1)]


# -- doublons, QoS, ordre ---------------------------------------------------


def test_doublon_identique_une_entree_deux_transmissions() -> None:
    """R1 : l'appelant a demande deux fois ; l'adaptateur n'a pas a le taire."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a/b", qos=1)
    adapter.subscribe("a/b", qos=1)
    assert _registre(adapter) == {"a/b": 1}
    assert fake.subscriptions == [("a/b", 1), ("a/b", 1)]


def test_qos_redeclare_le_dernier_gagne() -> None:
    """W-P9 : restaurer un QoS remplace retablirait une intention perimee."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a/b", qos=0)
    adapter.subscribe("a/b", qos=2)
    assert _registre(adapter) == {"a/b": 2}
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("a/b", 2)]


def test_qos_redeclare_ne_deplace_pas_l_ordre() -> None:
    """W-P7 : la redeclaration met a jour la valeur, jamais la position."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("un", qos=0)
    adapter.subscribe("deux", qos=0)
    adapter.subscribe("un", qos=2)
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("un", 2), ("deux", 0)]


def test_ordre_du_premier_enregistrement() -> None:
    """W-P7 : ni tri lexical, ni ordre de derniere declaration."""
    adapter, fake = _adaptateur_observe()
    for topic in ("zeta", "alpha", "mu"):
        adapter.subscribe(topic, qos=1)
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert [t for t, _q in fake.subscriptions] == ["zeta", "alpha", "mu"]


# -- restauration -----------------------------------------------------------


def test_connack_reussi_restaure_toutes_les_souscriptions() -> None:
    """W-P4 : toutes, jamais un sous-ensemble."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=0)
    adapter.subscribe("b", qos=1)
    adapter.subscribe("c", qos=2)
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("a", 0), ("b", 1), ("c", 2)]


def test_le_qos_exact_est_reemis() -> None:
    """W-P6 : aucun defaut ne se substitue au QoS enregistre."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=2)
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("a", 2)]


def test_connack_refuse_ne_restaure_rien() -> None:
    """W-P5 : une connexion non etablie n'a rien a restaurer."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    fake.subscriptions.clear()
    fake.fire_on_connect(success=False)
    assert fake.subscriptions == []


def test_aucun_topic_jamais_declare_n_est_reemis() -> None:
    """W-P18 : l'ensemble emis est exactement celui declare."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("declare", qos=1)
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert {t for t, _q in fake.subscriptions} == {"declare"}


def test_registre_vide_restauration_sans_effet() -> None:
    """La regle est uniforme : la connexion initiale n'est pas un cas special."""
    adapter, fake = _adaptateur_observe()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == []


def test_reconnexions_repetees_restaurent_sans_croissance() -> None:
    """W-P10 : le registre est un etat, pas un journal."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    adapter.subscribe("b", qos=0)
    for _ in range(3):
        fake.subscriptions.clear()
        fake.fire_on_disconnect(reason=7)
        fake.fire_on_connect(success=True)
        assert fake.subscriptions == [("a", 1), ("b", 0)]
        assert _registre(adapter) == {"a": 1, "b": 0}


def test_disconnect_propre_conserve_le_registre() -> None:
    """W-P11 : une deconnexion ne retire aucune declaration."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    adapter.disconnect()
    assert _registre(adapter) == {"a": 1}
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("a", 1)]


# -- ordre vis-a-vis de C11 -------------------------------------------------


def test_la_notification_de_presence_precede_la_restauration() -> None:
    """W-P12, observe par un journal ORDONNE commun, sur le chemin nominal."""
    adapter, fake = _adaptateur_observe()
    adapter.set_connection_handler(
        lambda connecte: fake.journal.append(("notification", connecte))
    )
    adapter.subscribe("a", qos=1)
    fake.journal.clear()
    fake.fire_on_connect(success=True)
    assert fake.journal[0] == ("notification", True)
    assert ("subscribe", "a", 1) in fake.journal[1:]


def test_la_notification_n_est_pas_conditionnee_a_la_restauration() -> None:
    """W-P13 : un echec de restauration ne prive pas C11 de sa notification."""
    adapter, fake = _adaptateur_observe()
    vues: list = []
    adapter.set_connection_handler(vues.append)
    adapter.subscribe("a", qos=1)
    fake.echec_subscribe.add("a")  # l'echec vise la RESTAURATION, pas l'appel direct
    vues.clear()
    fake.fire_on_connect(success=True)
    assert vues == [True]


# -- echec de restauration ---------------------------------------------------


def test_echec_de_restauration_journalise_avec_le_topic(caplog) -> None:
    """W-P14 et R4 : le defaut est rendu observable, jamais tu."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("perdu", qos=1)
    fake.echec_subscribe.add("perdu")
    with caplog.at_level(logging.WARNING, logger="boilerack.adapters.mqtt_paho"):
        fake.fire_on_connect(success=True)
    trace = "\n".join(r.getMessage() for r in caplog.records)
    assert "perdu" in trace
    assert "echec" in trace


def test_echec_de_restauration_non_propage() -> None:
    """W-P15 : rien ne remonte dans la boucle Paho."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    fake.echec_subscribe.add("a")
    fake.fire_on_connect(success=True)  # ne doit pas lever


def test_echec_de_restauration_conserve_l_intention() -> None:
    """W-P16 : l'intention reste declaree et sera rejouee."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    fake.echec_subscribe.add("a")
    fake.fire_on_connect(success=True)
    assert _registre(adapter) == {"a": 1}
    fake.echec_subscribe.clear()
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert fake.subscriptions == [("a", 1)]


def test_echec_sur_un_topic_n_interrompt_pas_les_suivants() -> None:
    """W0 §11 : la restauration continue pour les autres souscriptions."""
    adapter, fake = _adaptateur_observe()
    for topic in ("a", "b", "c"):
        adapter.subscribe(topic, qos=1)
    fake.echec_subscribe.add("b")
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)
    assert [t for t, _q in fake.subscriptions] == ["a", "b", "c"]


def test_echec_de_restauration_ne_produit_aucun_faux_succes() -> None:
    """R4 : aucun signal ne laisse croire que la restauration a reussi.

    `connected` reste vrai — c'est le fait de la connexion, et W0 §11.2 dit
    expressement que `online` ne signifie pas « souscriptions restaurees ».
    Ce que ce test verrouille, c'est qu'aucun ACQUITTEMENT ni indicateur de
    sante nouveau n'apparait : l'adaptateur expose exactement la meme surface
    qu'avant l'echec.
    """
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    fake.echec_subscribe.add("a")
    surface_avant = set(dir(adapter))
    fake.fire_on_connect(success=True)
    assert adapter.connected is True
    assert set(dir(adapter)) == surface_avant
    assert fake.published == []


# -- verrou ------------------------------------------------------------------


def test_aucune_emission_sous_verrou_a_l_appel_direct() -> None:
    """W-P17, verdict immediat et deterministe, sans concurrence reelle."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    assert all(o["verrou_libre"] for o in fake.observations)


def test_aucune_emission_sous_verrou_a_la_restauration() -> None:
    """W-P17 sur le chemin de restauration, celui que W0 ajoute."""
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    adapter.subscribe("b", qos=0)
    fake.observations.clear()
    fake.fire_on_connect(success=True)
    assert len(fake.observations) == 2
    assert all(o["verrou_libre"] for o in fake.observations)


def test_la_restauration_opere_sur_un_instantane() -> None:
    """W0 §14 : un `subscribe` concurrent ne modifie pas le parcours en cours.

    Un AUTRE FIL souscrit un topic supplementaire PENDANT la restauration,
    exactement comme le ferait un appelant reel. Le parcours en cours doit
    rester celui de l'instantane.

    Le fil est joint avec un DELAI BORNE et son aboutissement est AFFIRME. Si
    l'adaptateur emettait sous verrou (W0 §14), ce fil resterait bloque sur un
    `threading.Lock` non reentrant : le test doit alors ECHOUER, jamais geler.
    Une suite qui pend ne prouve rien et immobiliserait l'integration continue.
    """
    adapter, fake = _adaptateur_observe()
    adapter.subscribe("a", qos=1)
    adapter.subscribe("b", qos=1)

    injecte = {"fait": False, "abouti": False}
    souscrire_reel = fake.subscribe

    def souscrire_tardivement() -> None:
        adapter.subscribe("tardif", qos=2)
        injecte["abouti"] = True

    def subscribe_avec_injection(topic, qos=0):
        souscrire_reel(topic, qos)
        if topic == "a" and not injecte["fait"]:
            injecte["fait"] = True
            # `daemon` : sous une implementation fautive ce fil ne se termine
            # jamais ; il ne doit pas retenir l'interpreteur a la sortie.
            fil = threading.Thread(target=souscrire_tardivement, daemon=True)
            fil.start()
            fil.join(timeout=5.0)

    fake.subscribe = subscribe_avec_injection
    fake.subscriptions.clear()
    fake.fire_on_connect(success=True)

    assert injecte["abouti"], "souscription concurrente bloquee : emission sous verrou"
    restauration = [t for t, _q in fake.subscriptions]
    # L'instantane portait « a » et « b ». Le « tardif » apparait comme un appel
    # direct de l'appelant, jamais comme un element du parcours restaure.
    assert restauration[0] == "a"
    assert restauration.count("b") == 1
    assert restauration.count("tardif") == 1
    assert _registre(adapter) == {"a": 1, "b": 1, "tardif": 2}


# -- non-regression et absence de derive -------------------------------------


def test_le_fake_mqtt_client_conserve_sa_semantique_hors_connexion() -> None:
    """W-P22 : W0 ne redefinit pas la frontiere abstraite (W0 §2)."""
    from boilerack.testing.fake_mqtt import FakeMqttClient
    from boilerack.transport import NotConnectedError

    double = FakeMqttClient()
    with pytest.raises(NotConnectedError):
        double.subscribe("a", qos=1)


def test_aucune_correlation_suback_introduite() -> None:
    """W-P20 : ni `on_subscribe`, ni registre de `mid` de souscription."""
    import pathlib

    import boilerack.adapters.mqtt_paho as module

    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
    assert "on_subscribe" not in source
    assert "suback" not in source.lower()


def test_clean_session_inchange() -> None:
    """W-P21 : aucune session persistante n'est introduite."""
    import pathlib

    import boilerack.adapters.mqtt_paho as module

    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
    assert "clean_session" not in source


def test_la_voie_de_commande_n_est_pas_activee_par_la_racine() -> None:
    """REMPLACE `test_aucune_voie_de_commande_ouverte`, comme W1 §21.10 l'exigeait.

    L'ancienne assertion cherchait quatre chaines dans `runtime.py`,
    `lifecycle.py` et `cli.py`. W3 ayant livre le cablage, elle est devenue un
    FAUX NEGATIF : la couture transactionnelle existe desormais dans le runner,
    et l'ancien test passait pourtant encore, parce que le cablage passe par
    `TransactionSurface` et non par les quatre noms surveilles.

    Le nouvel oracle est plus PRECIS, pas plus faible. Il porte sur ce qui
    compte reellement : la racine de composition **compose** la voie, mais ne
    l'**active** pas. La preuve tient en deux faits verifiables :

    1. `boilerack.runtime` n'appelle jamais `build_transaction_surface` — la
       seule fonction capable de construire la voie ;
    2. `build_runtime` expose la voie en parametre OPTIONNEL valant `None`, et
       ne peut pas la fabriquer : elle exigerait un `VClient` ecrivain et un
       `Profile` reels, dont ce depot ne possede aucun.

    La preuve complete de la frontiere W4 — absence de `write` reel, absence de
    profil reel, absence de double de test en production — vit dans
    `tests/test_transaction_wiring.py`, avec le cablage qu'elle gouverne.
    """
    import ast
    import inspect
    import pathlib

    import boilerack.runtime as runtime

    # La preuve porte sur les APPELS, releves par AST : `build_runtime` cite la
    # fonction dans sa docstring pour expliquer pourquoi elle ne l'appelle pas,
    # et cette mention est une information, pas une activation.
    source = pathlib.Path(runtime.__file__).read_text(encoding="utf-8")
    appeles = {
        n.func.id
        for n in ast.walk(ast.parse(source))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    assert "build_transaction_surface" not in appeles
    assert "TransactionalCore" not in appeles

    parametres = inspect.signature(runtime.build_runtime).parameters
    assert parametres["transaction"].default is None
    assert parametres["transaction"].kind is inspect.Parameter.KEYWORD_ONLY


def test_aucun_unsubscribe_ajoute() -> None:
    """W0 §12 : aucune surface de retrait n'est creee."""
    adapter, _ = _adaptateur_observe()
    assert not hasattr(adapter, "unsubscribe")
