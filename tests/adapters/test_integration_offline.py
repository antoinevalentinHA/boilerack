"""Integration HORS LIGNE : `TransactionalCore` + adaptateur MQTT reel (sous faux
client Paho) + `VirtualClock` + profil factice.

Le cote `vclient` utilise le double C2 `FakeVClient` : l'adaptateur `vclient`
CONCRET reste bloque (contrat reel non caracterise), mais le cœur exige un
`VClient`, et le double C2 produit deja des `TransportStatus` deterministes. Ces
tests exercent donc le chemin MQTT reel de bout en bout (publication de
`accepted`, detection d'echec etabli, remise d'un message entrant), sans reseau,
sans broker, sans processus, sans attente reelle.
"""

from __future__ import annotations

from boilerack.adapters.config import MqttConfig
from boilerack.adapters.mqtt_paho import PahoMqttClient
from boilerack.core import TransactionalCore
from boilerack.core.ack import AckStatus, Reason
from boilerack.testing import FakeVClient, VirtualClock, build_fake_profile
from boilerack.transport.vclient import TransportStatus, WriteResult
from adapter_support import (
    START,
    FakeMqttMessage,
    FakePahoClient,
    command_message,
    command_payload,
    rid,
)


def _build(*, publish_rc=0, confirm_budget_s=5.0, confirm_interval_s=0.5):
    clock = VirtualClock(START)
    vc = FakeVClient(clock)
    paho = FakePahoClient(publish_rc=publish_rc)
    mqtt = PahoMqttClient(MqttConfig(host="broker.local"), client=paho)
    core = TransactionalCore(
        clock=clock, vclient=vc, mqtt=mqtt, profile=build_fake_profile(),
        confirm_budget_s=confirm_budget_s, confirm_interval_s=confirm_interval_s,
    )
    return core, vc, paho, clock


# 1. valide -> accepted -> ecriture -> relecture conforme -> applied
def test_1_flux_nominal_applied() -> None:
    core, vc, paho, _ = _build()
    vc.expect_write("set_temp_consigne", 21.0, result=WriteResult(TransportStatus.OK))
    vc.expect_read("get_temp_consigne", returns=21.0)

    accepted = core.submit(command_message(command_payload(rid(1), "temp_consigne", 21.0)))
    assert accepted.status is AckStatus.ACCEPTED
    # `accepted` a bien ete publie via l'adaptateur reel.
    assert paho.published[0]["topic"] == "boilerack/ack/temp_consigne"
    assert paho.published[0]["qos"] == 1 and paho.published[0]["retain"] is False

    verdict = core.process_next()
    assert verdict.status is AckStatus.APPLIED
    assert len(vc.calls) == 2  # une ecriture, une relecture


# 2. demon injoignable AVANT ecriture -> rejected / bridge_unavailable
def test_2_daemon_injoignable_bridge_unavailable() -> None:
    core, vc, paho, _ = _build()
    vc.expect_write(
        "set_temp_consigne", 21.0,
        result=WriteResult(TransportStatus.DAEMON_UNREACHABLE),
    )
    core.submit(command_message(command_payload(rid(2), "temp_consigne", 21.0)))
    verdict = core.process_next()
    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.BRIDGE_UNAVAILABLE


# 3. ecriture ambigue -> relecture conforme -> applied
def test_3_ecriture_ambigue_puis_confirmee_applied() -> None:
    core, vc, paho, _ = _build()
    vc.expect_write(
        "set_temp_consigne", 21.0,
        result=WriteResult(TransportStatus.TRANSPORT_ERROR),  # potentiellement emise
    )
    vc.expect_read("get_temp_consigne", returns=21.0)
    core.submit(command_message(command_payload(rid(3), "temp_consigne", 21.0)))
    verdict = core.process_next()
    assert verdict.status is AckStatus.APPLIED


# 4. ecriture ambigue -> aucune confirmation -> timeout
def test_4_ecriture_ambigue_sans_confirmation_timeout() -> None:
    core, vc, paho, _ = _build(confirm_budget_s=1.0, confirm_interval_s=0.5)
    vc.expect_write(
        "set_temp_consigne", 21.0,
        result=WriteResult(TransportStatus.TIMEOUT),
    )
    # relectures non conformes a t=0, 0.5, 1.0
    for _ in range(3):
        vc.expect_read("get_temp_consigne", returns=25.0)
    core.submit(command_message(command_payload(rid(4), "temp_consigne", 21.0)))
    verdict = core.process_next()
    assert verdict.status is AckStatus.TIMEOUT


# 5. publication `accepted` explicitement echouee -> AUCUNE invocation vclient
def test_5_accepted_echoue_aucune_ecriture() -> None:
    core, vc, paho, _ = _build(publish_rc=4)  # rc != 0 : echec etabli immediat
    verdict = core.submit(command_message(command_payload(rid(5), "temp_consigne", 21.0)))
    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.BRIDGE_UNAVAILABLE
    # fail-closed : le cœur n'a jamais depile ni ecrit.
    assert vc.calls == ()
    assert core.queue_depth == 0
    assert core.in_flight_count == 0


# 6. PUBACK simplement absent -> ecriture autorisee
def test_6_puback_absent_ecriture_autorisee() -> None:
    core, vc, paho, _ = _build()
    # publish_rc=0 et on NE declenche PAS on_publish : handle DEMANDE, non echoue.
    vc.expect_write("set_temp_consigne", 21.0, result=WriteResult(TransportStatus.OK))
    vc.expect_read("get_temp_consigne", returns=21.0)
    accepted = core.submit(command_message(command_payload(rid(6), "temp_consigne", 21.0)))
    assert accepted.status is AckStatus.ACCEPTED
    verdict = core.process_next()
    assert verdict.status is AckStatus.APPLIED  # l'ecriture a bien eu lieu
    assert len(vc.calls) == 2


# 7. message entrant brut remis au point d'entree du cœur
def test_7_message_entrant_remis_au_coeur() -> None:
    core, vc, paho, _ = _build()
    # Cablage minimal : les messages MQTT entrants alimentent l'admission.
    # L'adaptateur reel a deja cable paho.on_message ; on enregistre le handler
    # metier (l'admission du cœur) via la couture prevue.
    mqtt = core._mqtt  # l'adaptateur reel
    mqtt.set_message_handler(core.submit)

    paho.fire_on_message(
        FakeMqttMessage(
            topic="boilerack/command",
            payload=command_payload(rid(7), "temp_consigne", 21.0),
            qos=1,
        )
    )
    # Le cœur a admis la commande recue (mise en file), sans ecriture encore.
    assert core.queue_depth == 1
    assert vc.calls == ()
