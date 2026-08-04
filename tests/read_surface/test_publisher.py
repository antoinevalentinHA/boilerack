"""Tests de `boilerack.read_surface.publisher` — §5, §7.3 et §8.2 de C7-B."""

from __future__ import annotations

import ast
import json
import pathlib
from datetime import datetime, timezone

import pytest

from boilerack.read_surface import publisher as publisher_module
from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.measurements import V1_MEASUREMENTS
from boilerack.read_surface.publisher import ReadSurfacePublisher
from boilerack.read_surface.state import ChainStatus
from boilerack.read_surface.topics import V1_SUFFIXES
from boilerack.testing import FakeMqttClient, VirtualClock
from boilerack.transport.mqtt import MqttWill, NotConnectedError

_DEBUT = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)


def _clock() -> VirtualClock:
    return VirtualClock(_DEBUT, monotonic_start=1000.0)


def _publieur(prefix: str = "boiler", mqtt=None):
    client = mqtt if mqtt is not None else FakeMqttClient()
    p = ReadSurfacePublisher(
        mqtt=client, clock=_clock(), config=ReadSurfaceConfig(prefix=prefix)
    )
    return p, client


def _publies(client) -> list[tuple[str, bytes, int, bool]]:
    return [
        (h.publication.topic, h.publication.payload, h.publication.qos, h.publication.retain)
        for h in client.publications
    ]


# ---------------------------------------------------------------------------
# Construction et etat initial
# ---------------------------------------------------------------------------


def test_suffixes_employes_appartiennent_a_la_surface_v1() -> None:
    """Garde contre toute derive avec l'autorite close de §11."""
    assert publisher_module._ONLINE_SUFFIX in V1_SUFFIXES
    assert publisher_module._STATUS_SUFFIX in V1_SUFFIXES


def test_topics_derives_du_prefixe() -> None:
    p, _ = _publieur()
    assert p.online_topic == "boiler/bridge/online"
    assert p.status_topic == "boiler/bridge/telemetry_status"


def test_prefixe_personnalise_normalise() -> None:
    p, _ = _publieur(prefix="/maison//boiler/")
    assert p.online_topic == "maison/boiler/bridge/online"
    assert p.status_topic == "maison/boiler/bridge/telemetry_status"


def test_configuration_par_defaut_sans_argument() -> None:
    p = ReadSurfacePublisher(mqtt=FakeMqttClient(), clock=_clock())
    assert p.online_topic == "boiler/bridge/online"


def test_etat_initial_construit_a_la_construction() -> None:
    """§7.3 et §8.2 : aucune valeur, aucun resultat, chaine indisponible."""
    p, client = _publieur()
    assert client.publications == ()  # rien n'est publie avant start()
    etat = p.state
    assert set(etat.measurements) == {s.role for s in V1_MEASUREMENTS}
    for mesure in etat.measurements.values():
        assert mesure.has_value is False and mesure.last_result is None
    assert etat.chain_status is ChainStatus.UNAVAILABLE
    assert etat.chain_cause is None
    assert etat.cycle_completed is False


def test_non_demarre_a_la_construction() -> None:
    p, _ = _publieur()
    assert p.started is False


# ---------------------------------------------------------------------------
# Testament
# ---------------------------------------------------------------------------


def test_testament_exact() -> None:
    """§5 : testament `offline`, QoS 1, retenu, sur le topic de presence."""
    p, _ = _publieur()
    assert p.will() == MqttWill(
        topic="boiler/bridge/online", payload=b"offline", qos=1, retain=True
    )


def test_testament_suit_le_prefixe() -> None:
    p, _ = _publieur(prefix="maison/boiler")
    assert p.will().topic == "maison/boiler/bridge/online"


def test_testament_pose_a_la_connexion() -> None:
    p, client = _publieur()
    p.start()
    assert client.connected_will == p.will()


def test_aucun_demarrage_sans_testament() -> None:
    """Le testament n'est jamais optionnel pour ce producteur."""
    p, client = _publieur()
    p.start()
    assert client.connected_will is not None


# ---------------------------------------------------------------------------
# start()
# ---------------------------------------------------------------------------


def test_connexion_avant_toute_publication() -> None:
    """Le double refuse une publication hors connexion : l'ordre est prouve."""
    p, client = _publieur()
    p.start()  # ne leve pas => connect() a bien precede les publications
    assert client.connection_events == ("connect",)
    assert client.connected is True


def test_ensemble_exact_des_deux_topics_au_demarrage() -> None:
    """§11 : tout autre topic **MUST NOT** etre publie."""
    p, client = _publieur()
    p.start()
    assert [t for t, _, _, _ in _publies(client)] == [
        "boiler/bridge/online",
        "boiler/bridge/telemetry_status",
    ]


def test_online_publie_en_premier_qos1_retenu() -> None:
    p, client = _publieur()
    p.start()
    topic, payload, qos, retain = _publies(client)[0]
    assert (topic, payload, qos, retain) == (
        "boiler/bridge/online", b"online", 1, True,
    )


def test_snapshot_publie_apres_online_qos1_retenu() -> None:
    p, client = _publieur()
    p.start()
    topic, payload, qos, retain = _publies(client)[1]
    assert topic == "boiler/bridge/telemetry_status"
    assert (qos, retain) == (1, True)
    assert isinstance(payload, bytes)


def test_snapshot_initial_conforme() -> None:
    """§7.3 ligne 1 et §8.2 etat initial."""
    p, client = _publieur()
    p.start()
    snap = json.loads(_publies(client)[1][1].decode("utf-8"))
    assert snap["schema"] == 1
    assert snap["ts"] == "2026-08-02T20:00:00Z"
    assert snap["chain"] == {"status": "unavailable", "cause": None}
    assert set(snap["measurements"]) == {s.role for s in V1_MEASUREMENTS}
    for mesure in snap["measurements"].values():
        assert mesure == {
            "has_value": False,
            "fresh": False,
            "last_success": None,
            "age_s": None,
            "last_result": None,
        }


def test_echec_de_connexion_remonte_et_ne_publie_rien() -> None:
    """Aucune compensation : si `connect()` leve, `start()` n'a rien commence."""

    class _MqttRefusantLaConnexion(FakeMqttClient):
        def connect(self, will=None) -> None:
            raise OSError("broker injoignable")

    client = _MqttRefusantLaConnexion()
    p, _ = _publieur(mqtt=client)
    with pytest.raises(OSError, match="broker injoignable"):
        p.start()
    assert client.publications == ()
    assert client.connection_events == ()
    assert p.started is False
    with pytest.raises(RuntimeError, match="sans start"):
        p.stop()


def test_start_marque_le_cycle_de_vie() -> None:
    p, _ = _publieur()
    p.start()
    assert p.started is True


def test_start_ne_publie_aucun_scalaire() -> None:
    p, client = _publieur()
    p.start()
    assert not any(t.startswith("boiler/telemetry/") for t, _, _, _ in _publies(client))


def test_start_ne_publie_aucun_battement() -> None:
    p, client = _publieur()
    p.start()
    assert not any(t.endswith("bridge/heartbeat") for t, _, _, _ in _publies(client))


# ---------------------------------------------------------------------------
# stop()
# ---------------------------------------------------------------------------


def test_offline_publie_avant_deconnexion() -> None:
    """§5 : `offline` **avant** deconnexion, le testament n'etant pas emis
    lors d'une deconnexion propre."""
    p, client = _publieur()
    p.start()
    p.stop()
    dernier = _publies(client)[-1]
    assert dernier == ("boiler/bridge/online", b"offline", 1, True)
    assert client.connection_events == ("connect", "disconnect")
    assert client.connected is False


def test_stop_ne_publie_rien_d_autre() -> None:
    p, client = _publieur()
    p.start()
    avant = len(_publies(client))
    p.stop()
    assert len(_publies(client)) == avant + 1


def test_sequence_complete_de_topics() -> None:
    p, client = _publieur()
    p.start()
    p.stop()
    assert [(t, pl) for t, pl, _, _ in _publies(client)] == [
        ("boiler/bridge/online", b"online"),
        ("boiler/bridge/telemetry_status", _publies(client)[1][1]),
        ("boiler/bridge/online", b"offline"),
    ]


class _MqttEchouantALaPublication(FakeMqttClient):
    """Double dont `publish()` — et au besoin `disconnect()` — leve.

    Sert a eprouver les quatre issues de `stop()`.
    """

    def __init__(
        self, echouer_a_partir_de: int | None = 0, disconnect_ko: bool = False
    ) -> None:
        super().__init__()
        self._compteur = 0
        self._seuil = echouer_a_partir_de
        self._disconnect_ko = disconnect_ko

    def publish(self, topic, payload, qos=0, retain=False):
        self._compteur += 1
        if self._seuil is not None and self._compteur > self._seuil:
            raise RuntimeError("publication impossible")
        return super().publish(topic, payload, qos=qos, retain=retain)

    def disconnect(self) -> None:
        super().disconnect()
        if self._disconnect_ko:
            raise OSError("deconnexion impossible")


def test_arret_nominal_sans_exception() -> None:
    """1/4 : annonce et deconnexion reussies."""
    p, client = _publieur()
    p.start()
    p.stop()
    assert client.publications[-1].publication.payload == b"offline"
    assert client.connection_events == ("connect", "disconnect")
    assert p.started is False


def test_deconnexion_tentee_meme_si_offline_echoue() -> None:
    """2/4 : l'annonce echoue seule — la connexion est tout de meme refermee."""
    client = _MqttEchouantALaPublication(echouer_a_partir_de=2)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(RuntimeError, match="publication impossible") as capture:
        p.stop()
    assert not isinstance(capture.value, ExceptionGroup)
    assert client.connection_events == ("connect", "disconnect")
    assert client.connected is False
    assert p.started is False


def test_erreur_de_deconnexion_seule_remonte_inchangee() -> None:
    """3/4 : l'annonce reussit, la deconnexion echoue."""
    client = _MqttEchouantALaPublication(echouer_a_partir_de=None, disconnect_ko=True)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(OSError, match="deconnexion impossible") as capture:
        p.stop()
    assert not isinstance(capture.value, ExceptionGroup)
    assert client.publications[-1].publication.payload == b"offline"
    assert p.started is False


def test_double_echec_preserve_les_deux_exceptions() -> None:
    """4/4 : les deux echouent — aucune des deux erreurs n'est perdue.

    Sans ce traitement, la semantique d'un `finally` ferait masquer l'erreur
    d'annonce par celle de deconnexion.
    """
    client = _MqttEchouantALaPublication(echouer_a_partir_de=2, disconnect_ko=True)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(ExceptionGroup) as capture:
        p.stop()
    assert len(capture.value.exceptions) == 2
    assert p.started is False


def test_ordre_des_exceptions_du_groupe() -> None:
    """Ordre stable : annonce `offline` d'abord, deconnexion ensuite."""
    client = _MqttEchouantALaPublication(echouer_a_partir_de=2, disconnect_ko=True)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(ExceptionGroup) as capture:
        p.stop()
    annonce, deconnexion = capture.value.exceptions
    assert isinstance(annonce, RuntimeError)
    assert str(annonce) == "publication impossible"
    assert isinstance(deconnexion, OSError)
    assert str(deconnexion) == "deconnexion impossible"


def test_exceptions_originales_non_converties() -> None:
    """Les objets d'origine sont conserves, pas re-emballes."""
    levees: list[BaseException] = []

    class _Tracant(_MqttEchouantALaPublication):
        def publish(self, topic, payload, qos=0, retain=False):
            try:
                return super().publish(topic, payload, qos=qos, retain=retain)
            except RuntimeError as exc:
                levees.append(exc)
                raise

        def disconnect(self) -> None:
            try:
                super().disconnect()
            except OSError as exc:
                levees.append(exc)
                raise

    client = _Tracant(echouer_a_partir_de=2, disconnect_ko=True)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(ExceptionGroup) as capture:
        p.stop()
    assert list(capture.value.exceptions) == levees
    assert capture.value.exceptions[0] is levees[0]
    assert capture.value.exceptions[1] is levees[1]


class _MqttInterrompu(FakeMqttClient):
    """Double levant une `BaseException` — controle de flux, pas un echec."""

    def __init__(self, sur_publish: bool = True) -> None:
        super().__init__()
        self._sur_publish = sur_publish
        self._compteur = 0

    def publish(self, topic, payload, qos=0, retain=False):
        self._compteur += 1
        if self._sur_publish and self._compteur > 2:
            raise KeyboardInterrupt("interruption utilisateur")
        return super().publish(topic, payload, qos=qos, retain=retain)

    def disconnect(self) -> None:
        super().disconnect()
        if not self._sur_publish:
            raise KeyboardInterrupt("interruption utilisateur")


def test_interruption_pendant_l_annonce_remonte_inchangee() -> None:
    """`KeyboardInterrupt` n'est pas une `Exception` : elle traverse `stop()`."""
    client = _MqttInterrompu(sur_publish=True)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(KeyboardInterrupt, match="interruption utilisateur") as capture:
        p.stop()
    assert not isinstance(capture.value, ExceptionGroup)
    assert p.started is False


def test_interruption_pendant_l_annonce_n_appelle_pas_disconnect() -> None:
    """Interrompre une interruption pour faire du menage serait la trahir."""
    client = _MqttInterrompu(sur_publish=True)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(KeyboardInterrupt):
        p.stop()
    assert client.connection_events == ("connect",)
    assert client.connected is True


def test_interruption_pendant_la_deconnexion_remonte_inchangee() -> None:
    client = _MqttInterrompu(sur_publish=False)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(KeyboardInterrupt) as capture:
        p.stop()
    assert not isinstance(capture.value, ExceptionGroup)
    assert client.publications[-1].publication.payload == b"offline"
    assert p.started is False


class _MqttEchecPuisInterruption(_MqttEchouantALaPublication):
    """L'annonce echoue, puis la deconnexion est interrompue."""

    def disconnect(self) -> None:
        FakeMqttClient.disconnect(self)
        raise SystemExit("arret du processus")


def test_interruption_a_la_deconnexion_ne_groupe_pas_l_erreur_d_annonce() -> None:
    """Une `BaseException` n'entre jamais dans un `ExceptionGroup` ici.

    L'erreur d'annonce est alors perdue — consequence assumee : un `SystemExit`
    prime sur la restitution d'un echec de publication.
    """
    client = _MqttEchecPuisInterruption(echouer_a_partir_de=2)
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(SystemExit, match="arret du processus") as capture:
        p.stop()
    assert not isinstance(capture.value, ExceptionGroup)
    assert p.started is False


def test_seules_les_exceptions_sont_interceptees() -> None:
    """Le code n'intercepte jamais `BaseException`."""
    source = pathlib.Path(publisher_module.__file__).read_text(encoding="utf-8")
    lignes_code = [
        l for l in source.splitlines() if l.lstrip().startswith(("except ", "annonce:"))
    ]
    assert lignes_code, "les clauses attendues sont introuvables"
    assert not any("BaseException" in l for l in lignes_code)


@pytest.mark.parametrize(
    ("seuil", "disconnect_ko"), [(2, False), (None, True), (2, True)]
)
def test_redemarrage_possible_apres_un_arret_en_echec(
    seuil: int | None, disconnect_ko: bool
) -> None:
    """Le drapeau est arrete dans les trois cas : `start()` reste possible."""
    client = _MqttEchouantALaPublication(
        echouer_a_partir_de=seuil, disconnect_ko=disconnect_ko
    )
    p, _ = _publieur(mqtt=client)
    p.start()
    with pytest.raises(BaseException):
        p.stop()
    assert p.started is False
    client._seuil = None  # l'obstacle est leve pour le second demarrage
    client._disconnect_ko = False
    p.start()
    assert p.started is True


def test_erreur_de_publication_au_demarrage_remonte_telle_quelle() -> None:
    """Aucune traduction, aucune taxonomie nouvelle, aucune compensation."""
    client = _MqttEchouantALaPublication(echouer_a_partir_de=0)
    p, _ = _publieur(mqtt=client)
    with pytest.raises(RuntimeError, match="publication impossible"):
        p.start()
    # Le client EST connecte : le drapeau reflete la realite et `stop()` reste
    # appelable pour refermer proprement.
    assert client.connected is True
    assert p.started is True


def test_arret_possible_apres_un_demarrage_partiellement_echoue() -> None:
    client = _MqttEchouantALaPublication(echouer_a_partir_de=0)
    p, _ = _publieur(mqtt=client)
    with pytest.raises(RuntimeError):
        p.start()
    with pytest.raises(RuntimeError):
        p.stop()  # la publication `offline` echoue aussi
    assert client.connected is False  # mais la deconnexion a bien eu lieu


# ---------------------------------------------------------------------------
# Cycle de vie
# ---------------------------------------------------------------------------


def test_double_start_refuse() -> None:
    p, _ = _publieur()
    p.start()
    with pytest.raises(RuntimeError, match="deja ete appele"):
        p.start()


def test_stop_avant_start_refuse() -> None:
    p, _ = _publieur()
    with pytest.raises(RuntimeError, match="sans start"):
        p.stop()


def test_double_stop_refuse() -> None:
    p, _ = _publieur()
    p.start()
    p.stop()
    with pytest.raises(RuntimeError, match="sans start"):
        p.stop()


def test_redemarrage_republie_l_etat_courant_sans_le_reinitialiser() -> None:
    """L'etat vit avec le composant, pas avec la connexion."""
    p, client = _publieur()
    p.start()
    avant = p.state
    p.stop()
    p.start()
    assert p.state is avant


def test_publication_refusee_hors_connexion() -> None:
    """Le double garantit qu'aucune publication ne precede la connexion."""
    client = FakeMqttClient()
    with pytest.raises(NotConnectedError):
        client.publish("t", b"x")


# ---------------------------------------------------------------------------
# Limites assumees de C7-C3A
# ---------------------------------------------------------------------------


def test_pas_encore_un_producteur_de_telemetrie() -> None:
    """C7-C3A ne lit rien et ne publie aucune mesure.

    Ni lecteur, ni cycle, ni cadence, ni battement, ni reconnexion : tout cela
    releve de C7-C3B. Ce test fige la limite pour qu'elle ne passe pas pour un
    oubli — et il devra changer de facon VISIBLE le jour ou C7-C3B l'etendra.
    """
    for absent in (
        "read", "run_due", "due_at", "publish_snapshot", "publish_heartbeat",
        "run_forever", "reconnect",
    ):
        assert not hasattr(ReadSurfacePublisher, absent)


def test_aucun_lecteur_injecte() -> None:
    import inspect

    parametres = set(inspect.signature(ReadSurfacePublisher.__init__).parameters)
    assert parametres == {"self", "mqtt", "clock", "specs", "config"}
    assert "reader" not in parametres


def test_aucune_attente_de_confirmation() -> None:
    """§4.6 : les publications ne sont pas transactionnelles."""
    source = pathlib.Path(publisher_module.__file__).read_text(encoding="utf-8")
    for interdit in ("wait_for_publish", ".confirmed", ".failed"):
        assert interdit not in source


def test_publish_handle_ignore() -> None:
    p, client = _publieur()
    p.start()
    # Les handles restent DEMANDES : rien n'a ete confirme ni attendu.
    assert all(not h.confirmed and not h.failed for h in client.publications)


# ---------------------------------------------------------------------------
# Absence d'effet de bord
# ---------------------------------------------------------------------------

_INTERDITS = {"paho", "socket", "subprocess", "threading", "asyncio", "ssl", "time"}


def _modules_importes(module: object) -> set[str]:
    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")  # type: ignore[arg-type]
    noms: set[str] = set()
    for noeud in ast.walk(ast.parse(source)):
        if isinstance(noeud, ast.Import):
            noms.update(alias.name.split(".")[0] for alias in noeud.names)
        elif isinstance(noeud, ast.ImportFrom) and noeud.module:
            noms.add(noeud.module.split(".")[0])
    return noms


def test_module_sans_dependance_technique() -> None:
    """Aucun Paho, aucun socket, aucun processus, aucun thread."""
    assert _modules_importes(publisher_module) & _INTERDITS == set()


def test_aucune_horloge_systeme_lue() -> None:
    source = pathlib.Path(publisher_module.__file__).read_text(encoding="utf-8")
    for interdit in ("datetime.now(", "utcnow(", "time.monotonic(", "time.time("):
        assert interdit not in source


def test_aucune_boucle_ni_sommeil() -> None:
    source = pathlib.Path(publisher_module.__file__).read_text(encoding="utf-8")
    for interdit in ("while ", "sleep(", "Thread("):
        assert interdit not in source


def test_aucun_adaptateur_construit() -> None:
    """Le client est injecte : ce composant n'est pas une composition root."""
    source = pathlib.Path(publisher_module.__file__).read_text(encoding="utf-8")
    for interdit in ("PahoMqttClient", "SubprocessRunner", "SystemClock", "adapters"):
        assert interdit not in source
