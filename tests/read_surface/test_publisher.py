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
from boilerack.read_surface.payload import format_scalar
from boilerack.read_surface.publisher import ReadSurfacePublisher
from boilerack.read_surface.state import ChainStatus
from boilerack.read_surface.topics import V1_SUFFIXES
from boilerack.testing import FakeMqttClient, VirtualClock
from boilerack.connection_state import ConnectionState
from boilerack.transport.mqtt import MqttWill, NotConnectedError
from boilerack.transport.vclient import ReadResult, TransportStatus

_DEBUT = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)


def _clock() -> VirtualClock:
    return VirtualClock(_DEBUT, monotonic_start=1000.0)


def _publieur(prefix: str = "boiler", mqtt=None, reader=None, clock=None, config=None,
              connection=None):
    client = mqtt if mqtt is not None else FakeMqttClient()
    p = ReadSurfacePublisher(
        mqtt=client,
        clock=clock if clock is not None else _clock(),
        connection=connection if connection is not None else ConnectionState(),
        reader=reader,
        config=config if config is not None else ReadSurfaceConfig(prefix=prefix),
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
    p = ReadSurfacePublisher(mqtt=FakeMqttClient(), clock=_clock(),
                             connection=ConnectionState())
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
# Limites assumees apres C7-C3B
# ---------------------------------------------------------------------------


def test_api_publique_minimale() -> None:
    """C7-C3B ajoute `due_at` et `run_due` — et rien d'autre.

    Restent absents, faute de consommateur : une boucle propre, une politique de
    reconnexion, et des publications d'instantane ou de battement exposees
    publiquement. Ce test fige la limite pour qu'elle ne passe pas pour un oubli.
    """
    for present in ("start", "stop", "due_at", "run_due", "will", "state"):
        assert hasattr(ReadSurfacePublisher, present)
    for absent in (
        "run_forever", "reconnect", "publish_snapshot", "publish_heartbeat",
        "read_cycle", "loop",
    ):
        assert not hasattr(ReadSurfacePublisher, absent)


def test_lecteur_injecte_jamais_construit() -> None:
    """Le lecteur est une dependance INJECTEE, comme le client MQTT."""
    import inspect

    parametres = set(inspect.signature(ReadSurfacePublisher.__init__).parameters)
    assert parametres == {
        "self", "mqtt", "clock", "connection", "reader", "specs", "config"
    }


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
    """Le client et le lecteur sont injectes : pas de composition root.

    Le controle porte sur les symboles REELLEMENT references — le nom
    `adapters` figure desormais dans une docstring qui explique precisement
    pourquoi le paquet n'en depend pas.
    """
    source = pathlib.Path(publisher_module.__file__).read_text(encoding="utf-8")
    noms: set[str] = set()
    for noeud in ast.walk(ast.parse(source)):
        if isinstance(noeud, ast.Name):
            noms.add(noeud.id)
        elif isinstance(noeud, ast.Attribute):
            noms.add(noeud.attr)
        elif isinstance(noeud, (ast.Import, ast.ImportFrom)):
            noms.update(a.name.split(".")[0] for a in noeud.names)
            if isinstance(noeud, ast.ImportFrom) and noeud.module:
                noms.add(noeud.module)
    assert not noms & {"PahoMqttClient", "SubprocessRunner", "SystemClock"}
    assert not any(n.startswith("boilerack.adapters") for n in noms)


# ===========================================================================
# C7-C3B — lectures dues, publications scalaires, cadences et battement
# ===========================================================================

_ECHECS = [s for s in TransportStatus if s is not TransportStatus.OK]
_ROLES = [s.role for s in V1_MEASUREMENTS]
_CMDS = [s.read for s in V1_MEASUREMENTS]
_TEMPS_30S = [s for s in V1_MEASUREMENTS if s.period_s == 30]


class _Lecteur:
    """Lecteur programmable : aucun processus, aucun `vclient` reel."""

    def __init__(self, plan: dict | None = None, valeur: float = 21.5) -> None:
        self.plan = plan or {}
        self.valeur = valeur
        self.appels: list[str] = []

    def read(self, command: str):
        self.appels.append(command)
        statut = self.plan.get(command, TransportStatus.OK)
        if statut is TransportStatus.OK:
            return ReadResult(status=statut, value=self.valeur)
        return ReadResult(status=statut)


class _LecteurQuiLeve(_Lecteur):
    """Leve une exception inattendue a la N-ieme lecture."""

    def __init__(self, a_la_lecture: int = 3, **kw) -> None:
        super().__init__(**kw)
        self.seuil = a_la_lecture

    def read(self, command: str):
        if len(self.appels) + 1 >= self.seuil:
            self.appels.append(command)
            raise RuntimeError("defaut inattendu du lecteur")
        return super().read(command)


def _demarre(reader=None, mqtt=None, config=None, clock=None):
    c = clock if clock is not None else _clock()
    p, client = _publieur(mqtt=mqtt, reader=reader, clock=c, config=config)
    p.start()
    return p, client, c


def _topics(client) -> list[str]:
    return [h.publication.topic for h in client.publications]


def _depuis(client, n: int) -> list[tuple[str, bytes, int, bool]]:
    return _publies(client)[n:]


# ---------------------------------------------------------------------------
# Demarrage et echeances initiales
# ---------------------------------------------------------------------------


def test_snapshot_initial_avant_toute_lecture() -> None:
    r = _Lecteur()
    p, client, _ = _demarre(reader=r)
    assert r.appels == []
    assert _topics(client) == ["boiler/bridge/online", "boiler/bridge/telemetry_status"]


def test_mesures_immediatement_dues_apres_le_demarrage() -> None:
    """Decision d'implementation : le demarrage est le premier reveil."""
    p, _, c = _demarre(reader=_Lecteur())
    assert p.due_at() == c.monotonic()
    assert [s.role for s in p.due_measurements()] == _ROLES


def test_echeances_snapshot_et_heartbeat_initialisees() -> None:
    p, _, c = _demarre(reader=_Lecteur())
    assert p.due_at() == c.monotonic()
    p.run_due()
    assert p.due_at() == c.monotonic() + 30


def test_heartbeat_desactive_absent_de_toute_publication() -> None:
    config = ReadSurfaceConfig(heartbeat_period_s=None)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    c.advance(3600)
    p.run_due()
    assert not any("heartbeat" in t for t in _topics(client))


def test_due_at_refuse_avant_start() -> None:
    p, _ = _publieur(reader=_Lecteur())
    with pytest.raises(RuntimeError, match="sans start"):
        p.due_at()


def test_run_due_refuse_avant_start() -> None:
    r = _Lecteur()
    p, _ = _publieur(reader=r)
    with pytest.raises(RuntimeError, match="sans start"):
        p.run_due()
    assert r.appels == []


def test_due_at_ne_modifie_rien() -> None:
    p, client, _ = _demarre(reader=_Lecteur())
    avant = (p.state, len(client.publications))
    p.due_at()
    p.due_at()
    assert (p.state, len(client.publications)) == avant


# ---------------------------------------------------------------------------
# Mesures dues
# ---------------------------------------------------------------------------


def test_aucune_mesure_due_ne_declenche_aucune_lecture() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=90, heartbeat_period_s=None)
    r = _Lecteur()
    p, client, c = _demarre(reader=r, config=config)
    p.run_due()
    r.appels.clear()
    n = len(client.publications)
    p.run_due()
    assert r.appels == []
    assert len(client.publications) == n


def test_seules_les_trois_mesures_30s_dues() -> None:
    r = _Lecteur()
    p, _, c = _demarre(reader=r)
    p.run_due()
    r.appels.clear()
    c.advance(30)
    p.run_due()
    assert r.appels == [s.read for s in _TEMPS_30S]


def test_les_huit_mesures_dues_a_60s() -> None:
    r = _Lecteur()
    p, _, c = _demarre(reader=r)
    p.run_due()
    r.appels.clear()
    c.advance(60)
    p.run_due()
    assert r.appels == _CMDS


def test_ordre_exact_des_specs() -> None:
    """Aucun tri alphabetique : l'ordre de la table §4.2 est conserve."""
    r = _Lecteur()
    p, _, _ = _demarre(reader=r)
    p.run_due()
    assert r.appels == _CMDS


def test_un_seul_appel_par_role() -> None:
    r = _Lecteur()
    p, _, _ = _demarre(reader=r)
    p.run_due()
    assert len(r.appels) == len(set(r.appels)) == 8


# ---------------------------------------------------------------------------
# Lecture reussie
# ---------------------------------------------------------------------------


def test_scalaire_publie_sur_le_bon_topic_qos1_retenu() -> None:
    r = _Lecteur(valeur=21.5)
    p, client, _ = _demarre(reader=r)
    n = len(client.publications)
    p.run_due()
    scalaires = [x for x in _depuis(client, n) if "/telemetry/" in x[0]]
    assert len(scalaires) == 8
    assert all(q == 1 and ret is True for _, _, q, ret in scalaires)
    assert scalaires[0][0] == "boiler/telemetry/temperatures/outdoor"


def test_payload_scalaire_produit_par_format_scalar() -> None:
    r = _Lecteur(valeur=21.5)
    p, client, _ = _demarre(reader=r)
    p.run_due()
    charge = next(
        pl for t, pl, _, _ in _publies(client) if t.endswith("temperatures/outdoor")
    )
    assert charge == format_scalar(21.5)


def test_commande_exacte_transmise_au_lecteur() -> None:
    r = _Lecteur()
    p, _, _ = _demarre(reader=r)
    p.run_due()
    assert r.appels[0] == "getTempA"
    assert r.appels[1] == "getTempKist"


def test_etat_mis_a_jour_apres_publication_scalaire() -> None:
    """§4.6 : scalaire, PUIS etat, PUIS instantane."""
    r = _Lecteur()
    p, _, _ = _demarre(reader=r)
    p.run_due()
    for role in _ROLES:
        mesure = p.state.measurements[role]
        assert mesure.last_result is TransportStatus.OK
        assert mesure.has_value is True


def test_snapshot_publie_apres_chaque_succes() -> None:
    r = _Lecteur()
    p, client, _ = _demarre(reader=r)
    n = len(client.publications)
    p.run_due()
    sequence = [t for t, _, _, _ in _depuis(client, n)]
    assert len(sequence) == 17
    for i in range(8):
        assert "/telemetry/" in sequence[2 * i]
        assert sequence[2 * i + 1] == "boiler/bridge/telemetry_status"
    assert sequence[-1] == "boiler/bridge/telemetry_status"


def test_aucune_valeur_scalaire_stockee() -> None:
    import dataclasses

    from boilerack.read_surface.state import MeasurementState

    p, _, _ = _demarre(reader=_Lecteur())
    p.run_due()
    champs = {f.name for f in dataclasses.fields(MeasurementState)}
    assert not champs & {"value", "last_value", "raw", "detail"}
    assert not any("21.5" in repr(v) for v in p.state.measurements.values())


# ---------------------------------------------------------------------------
# Lecture echouee
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("statut", _ECHECS, ids=[s.name for s in _ECHECS])
def test_aucun_scalaire_sur_echec(statut: TransportStatus) -> None:
    r = _Lecteur(plan={cmd: statut for cmd in _CMDS})
    p, client, _ = _demarre(reader=r)
    n = len(client.publications)
    p.run_due()
    assert not any("/telemetry/" in t for t, _, _, _ in _depuis(client, n))


def test_aucune_sentinelle_sur_echec() -> None:
    r = _Lecteur(plan={cmd: TransportStatus.TIMEOUT for cmd in _CMDS})
    p, client, _ = _demarre(reader=r)
    p.run_due()
    assert [pl for t, pl, _, _ in _publies(client) if "/telemetry/" in t] == []


def test_etat_mis_a_jour_sur_echec() -> None:
    r = _Lecteur(plan={"getTempA": TransportStatus.TIMEOUT})
    p, _, _ = _demarre(reader=r)
    p.run_due()
    mesure = p.state.measurements["outdoor_temperature"]
    assert mesure.last_result is TransportStatus.TIMEOUT
    assert mesure.has_value is False


def test_snapshot_final_porte_le_dernier_resultat_echoue() -> None:
    r = _Lecteur(plan={"getTempA": TransportStatus.TIMEOUT})
    p, client, _ = _demarre(reader=r)
    p.run_due()
    final = json.loads(_publies(client)[-1][1].decode("utf-8"))
    assert final["measurements"]["outdoor_temperature"]["last_result"] == "timeout"
    assert final["measurements"]["supply_temperature"]["last_result"] == "ok"


def test_aucun_snapshot_intermediaire_apres_un_echec() -> None:
    """§4.6 n'impose l'instantane qu'APRES une lecture reussie."""
    r = _Lecteur(plan={cmd: TransportStatus.TIMEOUT for cmd in _CMDS})
    p, client, _ = _demarre(reader=r)
    n = len(client.publications)
    p.run_due()
    assert [t for t, _, _, _ in _depuis(client, n)] == ["boiler/bridge/telemetry_status"]


# ---------------------------------------------------------------------------
# Cloture de cycle et chain
# ---------------------------------------------------------------------------


def test_chain_ok_sur_cycle_entierement_reussi() -> None:
    p, _, _ = _demarre(reader=_Lecteur())
    p.run_due()
    assert p.state.chain_status is ChainStatus.OK
    assert p.state.chain_cause is None
    assert p.state.cycle_completed is True


def test_chain_degrade_sur_cycle_partiel() -> None:
    r = _Lecteur(plan={"getTempA": TransportStatus.DAEMON_UNREACHABLE})
    p, _, _ = _demarre(reader=r)
    p.run_due()
    assert p.state.chain_status is ChainStatus.DEGRADED
    assert p.state.chain_cause is TransportStatus.DAEMON_UNREACHABLE


def test_chain_indisponible_si_tout_echoue() -> None:
    r = _Lecteur(plan={cmd: TransportStatus.TIMEOUT for cmd in _CMDS})
    p, _, _ = _demarre(reader=r)
    p.run_due()
    assert p.state.chain_status is ChainStatus.UNAVAILABLE
    assert p.state.chain_cause is TransportStatus.TIMEOUT


def test_aucun_cycle_cloture_si_aucune_mesure_due() -> None:
    """`chain` reflete le dernier cycle TERMINE, jamais un reveil vide."""
    config = ReadSurfaceConfig(snapshot_period_s=90, heartbeat_period_s=None)
    p, _, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    etat = p.state
    c.advance(1)
    p.run_due()
    assert p.state is etat


def test_snapshot_de_fin_de_cycle_meme_si_tout_echoue() -> None:
    r = _Lecteur(plan={cmd: TransportStatus.TIMEOUT for cmd in _CMDS})
    p, client, _ = _demarre(reader=r)
    n = len(client.publications)
    p.run_due()
    assert _depuis(client, n)[-1][0] == "boiler/bridge/telemetry_status"


def test_chain_ne_retient_que_les_mesures_du_cycle() -> None:
    r = _Lecteur(plan={"getTempWWsoll": TransportStatus.DAEMON_UNREACHABLE})
    p, _, c = _demarre(reader=r)
    p.run_due()
    assert p.state.chain_cause is TransportStatus.DAEMON_UNREACHABLE
    r.plan = {}
    c.advance(30)
    p.run_due()
    assert p.state.chain_status is ChainStatus.OK
    assert p.state.chain_cause is None


# ---------------------------------------------------------------------------
# Echeances
# ---------------------------------------------------------------------------


def test_prochaine_echeance_depuis_la_fin_de_la_tentative() -> None:
    p, _, _ = _demarre(reader=_Lecteur())
    p.run_due()
    assert p.due_at() == 1030.0


def test_aucun_rattrapage_apres_un_reveil_tardif() -> None:
    """Une periode manquee n'engendre aucune rafale : on repart de maintenant."""
    r = _Lecteur()
    p, _, c = _demarre(reader=r)
    p.run_due()
    r.appels.clear()
    c.advance(300)
    p.run_due()
    assert r.appels == _CMDS
    assert p.due_at() == 1300.0 + 30


def test_mesures_non_traitees_restent_dues_apres_exception() -> None:
    p, _, _ = _demarre(reader=_LecteurQuiLeve(a_la_lecture=3))
    with pytest.raises(RuntimeError, match="defaut inattendu"):
        p.run_due()
    restantes = {s.role for s in p.due_measurements()}
    assert "outdoor_temperature" not in restantes
    assert "supply_temperature" not in restantes
    assert "dhw_temperature" in restantes


def test_due_at_retourne_le_minimum() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=5, heartbeat_period_s=7)
    p, _, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    assert p.due_at() == c.monotonic() + 5


# ---------------------------------------------------------------------------
# Instantane periodique
# ---------------------------------------------------------------------------


def test_snapshot_republie_sans_aucune_mesure_due() -> None:
    """§7.4 : republication **meme si rien n'a change**."""
    config = ReadSurfaceConfig(snapshot_period_s=5, heartbeat_period_s=None)
    r = _Lecteur()
    p, client, c = _demarre(reader=r, config=config)
    p.run_due()
    r.appels.clear()
    n = len(client.publications)
    c.advance(5)
    p.run_due()
    assert r.appels == []
    assert [t for t, _, _, _ in _depuis(client, n)] == ["boiler/bridge/telemetry_status"]


def test_snapshot_periodique_porte_un_ts_a_jour() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=5, heartbeat_period_s=None)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    premier = json.loads(_publies(client)[-1][1].decode("utf-8"))["ts"]
    c.advance(5)
    p.run_due()
    second = json.loads(_publies(client)[-1][1].decode("utf-8"))["ts"]
    assert premier != second


def test_pas_de_double_snapshot_dans_le_meme_appel() -> None:
    """La publication de fin de cycle satisfait aussi l'echeance periodique."""
    config = ReadSurfaceConfig(snapshot_period_s=5, heartbeat_period_s=None)
    r = _Lecteur(plan={cmd: TransportStatus.TIMEOUT for cmd in _CMDS})
    p, client, c = _demarre(reader=r, config=config)
    p.run_due()
    n = len(client.publications)
    c.advance(60)
    p.run_due()
    finaux = [t for t, _, _, _ in _depuis(client, n) if t.endswith("telemetry_status")]
    assert len(finaux) == 1


def test_echeance_periodique_repoussee_apres_toute_tentative() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=5, heartbeat_period_s=None)
    p, _, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    assert p.due_at() == c.monotonic() + 5


def test_echec_du_snapshot_periodique_n_altere_pas_l_etat() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=5, heartbeat_period_s=None)
    client = _MqttEchouantSur("telemetry_status")
    r = _Lecteur(plan={cmd: TransportStatus.TIMEOUT for cmd in _CMDS})
    c = _clock()
    p, _ = _publieur(mqtt=client, reader=r, config=config, clock=c)
    client.actif = False
    p.start()
    client.actif = True
    with pytest.raises(ExceptionGroup):
        p.run_due()
    avant = p.state
    c.advance(5)
    with pytest.raises(ExceptionGroup):
        p.run_due()
    assert p.state is avant


# ---------------------------------------------------------------------------
# Battement
# ---------------------------------------------------------------------------


def test_battement_topic_payload_qos_et_retain() -> None:
    """§9 : QoS 0, non retenu, `{"ts":"…"}` RFC 3339 UTC."""
    config = ReadSurfaceConfig(snapshot_period_s=90, heartbeat_period_s=10)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    n = len(client.publications)
    c.advance(10)
    p.run_due()
    battements = [x for x in _depuis(client, n) if x[0].endswith("bridge/heartbeat")]
    assert len(battements) == 1
    topic, charge, qos, retain = battements[0]
    assert topic == "boiler/bridge/heartbeat"
    assert (qos, retain) == (0, False)
    assert json.loads(charge.decode("utf-8")) == {"ts": "2026-08-02T20:00:10Z"}


def test_battement_aucun_champ_supplementaire() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=90, heartbeat_period_s=10)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    c.advance(10)
    p.run_due()
    charge = next(
        pl for t, pl, _, _ in _publies(client) if t.endswith("bridge/heartbeat")
    )
    assert set(json.loads(charge.decode("utf-8"))) == {"ts"}


def test_battement_compact_et_utf8() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=90, heartbeat_period_s=10)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    c.advance(10)
    p.run_due()
    charge = next(
        pl for t, pl, _, _ in _publies(client) if t.endswith("bridge/heartbeat")
    )
    assert isinstance(charge, bytes)
    assert b", " not in charge and b": " not in charge


def test_battement_meme_format_de_ts_que_l_instantane() -> None:
    """Garde contre une derive entre les deux formateurs d'horodatage."""
    config = ReadSurfaceConfig(snapshot_period_s=10, heartbeat_period_s=10)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    c.advance(10)
    p.run_due()
    pubs = _publies(client)
    ts_snapshot = next(
        json.loads(pl.decode())["ts"]
        for t, pl, _, _ in reversed(pubs)
        if t.endswith("telemetry_status")
    )
    ts_battement = next(
        json.loads(pl.decode())["ts"]
        for t, pl, _, _ in reversed(pubs)
        if t.endswith("bridge/heartbeat")
    )
    assert ts_snapshot == ts_battement


def test_battement_sans_rattrapage() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=90, heartbeat_period_s=10)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    n = len(client.publications)
    c.advance(100)
    p.run_due()
    battements = [x for x in _depuis(client, n) if x[0].endswith("bridge/heartbeat")]
    assert len(battements) == 1


def test_aucun_battement_au_demarrage() -> None:
    """§9 ne l'exige pas : le publier laisserait croire a une vitalite etablie."""
    p, client, _ = _demarre(reader=_Lecteur())
    assert not any("heartbeat" in t for t in _topics(client))


# ---------------------------------------------------------------------------
# Erreurs de publication MQTT
# ---------------------------------------------------------------------------


class _MqttEchouantSur(FakeMqttClient):
    """Fait echouer les publications dont le topic contient un fragment."""

    def __init__(self, fragment: str) -> None:
        super().__init__()
        self.fragment = fragment
        self.actif = True

    def publish(self, topic, payload, qos=0, retain=False):
        if self.actif and self.fragment in topic:
            raise RuntimeError(f"publication impossible : {topic}")
        return super().publish(topic, payload, qos=qos, retain=retain)


def test_erreur_scalaire_n_empeche_ni_l_etat_ni_le_cycle() -> None:
    client = _MqttEchouantSur("/telemetry/")
    r = _Lecteur()
    p, _, _ = _demarre(reader=r, mqtt=client)
    with pytest.raises(ExceptionGroup) as capture:
        p.run_due()
    assert len(capture.value.exceptions) == 8
    assert all(
        m.last_result is TransportStatus.OK for m in p.state.measurements.values()
    )
    assert p.state.chain_status is ChainStatus.OK
    assert r.appels == _CMDS


def test_erreur_de_publication_ne_transforme_pas_le_statut() -> None:
    client = _MqttEchouantSur("/telemetry/")
    p, _, _ = _demarre(reader=_Lecteur(), mqtt=client)
    with pytest.raises(ExceptionGroup):
        p.run_due()
    assert p.state.chain_cause is None
    assert not any(
        m.last_result is TransportStatus.TRANSPORT_ERROR
        for m in p.state.measurements.values()
    )


def test_erreur_de_snapshot_collectee_et_cycle_poursuivi() -> None:
    client = _MqttEchouantSur("telemetry_status")
    r = _Lecteur()
    p, _ = _publieur(mqtt=client, reader=r)
    client.actif = False
    p.start()
    client.actif = True
    with pytest.raises(ExceptionGroup) as capture:
        p.run_due()
    assert len(capture.value.exceptions) == 9
    assert r.appels == _CMDS


def test_erreur_de_battement_collectee() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=90, heartbeat_period_s=10)
    client = _MqttEchouantSur("bridge/heartbeat")
    p, _, c = _demarre(reader=_Lecteur(), mqtt=client, config=config)
    p.run_due()
    c.advance(10)
    with pytest.raises(ExceptionGroup) as capture:
        p.run_due()
    assert len(capture.value.exceptions) == 1
    assert "heartbeat" in str(capture.value.exceptions[0])


def test_erreurs_groupees_dans_l_ordre_de_survenue() -> None:
    client = _MqttEchouantSur("boiler/")
    p, _ = _publieur(mqtt=client, reader=_Lecteur())
    client.actif = False
    p.start()
    client.actif = True
    with pytest.raises(ExceptionGroup) as capture:
        p.run_due()
    messages = [str(e) for e in capture.value.exceptions]
    assert "temperatures/outdoor" in messages[0]
    assert "telemetry_status" in messages[1]
    assert all(isinstance(e, RuntimeError) for e in capture.value.exceptions)


def test_identite_des_exceptions_preservee() -> None:
    levees: list[BaseException] = []

    class _Tracant(FakeMqttClient):
        def publish(self, topic, payload, qos=0, retain=False):
            if "/telemetry/" in topic:
                exc = RuntimeError(f"KO {topic}")
                levees.append(exc)
                raise exc
            return super().publish(topic, payload, qos=qos, retain=retain)

    p, _, _ = _demarre(reader=_Lecteur(), mqtt=_Tracant())
    with pytest.raises(ExceptionGroup) as capture:
        p.run_due()
    assert list(capture.value.exceptions) == levees


def test_base_exception_non_capturee_pendant_le_cycle() -> None:
    class _MqttInterrompu(FakeMqttClient):
        def publish(self, topic, payload, qos=0, retain=False):
            if "/telemetry/" in topic:
                raise KeyboardInterrupt("Ctrl-C")
            return super().publish(topic, payload, qos=qos, retain=retain)

    p, _, _ = _demarre(reader=_Lecteur(), mqtt=_MqttInterrompu())
    with pytest.raises(KeyboardInterrupt) as capture:
        p.run_due()
    assert not isinstance(capture.value, ExceptionGroup)


# ---------------------------------------------------------------------------
# Exception inattendue du lecteur
# ---------------------------------------------------------------------------


def test_exception_du_lecteur_remonte_telle_quelle() -> None:
    """C6 garantit qu'aucune issue de transport ne leve : c'est un DEFAUT."""
    p, _, _ = _demarre(reader=_LecteurQuiLeve(a_la_lecture=3))
    with pytest.raises(RuntimeError, match="defaut inattendu") as capture:
        p.run_due()
    assert not isinstance(capture.value, ExceptionGroup)


def test_cycle_non_cloture_sur_exception_du_lecteur() -> None:
    p, _, _ = _demarre(reader=_LecteurQuiLeve(a_la_lecture=3))
    with pytest.raises(RuntimeError):
        p.run_due()
    assert p.state.chain_status is ChainStatus.UNAVAILABLE
    assert p.state.cycle_completed is False


def test_mesures_deja_traitees_restent_projetees_apres_exception() -> None:
    p, _, _ = _demarre(reader=_LecteurQuiLeve(a_la_lecture=3))
    with pytest.raises(RuntimeError):
        p.run_due()
    assert p.state.measurements["outdoor_temperature"].last_result is TransportStatus.OK
    assert p.state.measurements["dhw_temperature"].last_result is None


def test_aucun_lecteur_injecte_refuse_toute_lecture() -> None:
    p, _, _ = _demarre(reader=None)
    with pytest.raises(RuntimeError, match="aucun lecteur injecte"):
        p.run_due()


# ---------------------------------------------------------------------------
# Cycle de vie
# ---------------------------------------------------------------------------


def test_redemarrage_reinitialise_les_echeances_sans_toucher_l_etat() -> None:
    p, _, c = _demarre(reader=_Lecteur())
    p.run_due()
    etat = p.state
    c.advance(10)
    p.stop()
    p.start()
    assert p.state is etat
    assert p.due_at() == c.monotonic()


def test_due_at_refuse_apres_stop() -> None:
    p, _, _ = _demarre(reader=_Lecteur())
    p.stop()
    with pytest.raises(RuntimeError, match="sans start"):
        p.due_at()


def test_aucun_lecteur_appele_avant_start() -> None:
    r = _Lecteur()
    ReadSurfacePublisher(mqtt=FakeMqttClient(), clock=_clock(),
                         connection=ConnectionState(), reader=r)
    assert r.appels == []


# ---------------------------------------------------------------------------
# Borne du snapshot, dependante des specs
# ---------------------------------------------------------------------------


def test_snapshot_period_superieure_au_plus_petit_fresh_max_refusee() -> None:
    """§7.4 : « **MUST** etre inferieure ou egale au plus petit `fresh_max` »."""
    with pytest.raises(ValueError, match="plus petit fresh_max_s"):
        ReadSurfacePublisher(
            mqtt=FakeMqttClient(),
            clock=_clock(),
            connection=ConnectionState(),
            config=ReadSurfaceConfig(snapshot_period_s=91),
        )


def test_snapshot_period_egale_au_plus_petit_fresh_max_acceptee() -> None:
    p = ReadSurfacePublisher(
        mqtt=FakeMqttClient(),
        clock=_clock(),
        connection=ConnectionState(),
        config=ReadSurfaceConfig(snapshot_period_s=90),
    )
    assert p.started is False


def test_borne_verifiee_contre_les_specs_injectees() -> None:
    """La borne suit les specs REELLEMENT injectees, pas une constante globale."""
    from boilerack.read_surface.measurements import MeasurementSpec

    lentes = (
        MeasurementSpec(
            role="x", read="getX", suffix="telemetry/x", period_s=100, fresh_max_s=300
        ),
    )
    p = ReadSurfacePublisher(
        mqtt=FakeMqttClient(),
        clock=_clock(),
        connection=ConnectionState(),
        specs=lentes,
        config=ReadSurfaceConfig(snapshot_period_s=200),
    )
    assert p.started is False


# ---------------------------------------------------------------------------
# Frontieres C7-C3B
# ---------------------------------------------------------------------------


def test_aucun_topic_hors_surface_v1() -> None:
    config = ReadSurfaceConfig(snapshot_period_s=10, heartbeat_period_s=10)
    p, client, c = _demarre(reader=_Lecteur(), config=config)
    p.run_due()
    c.advance(60)
    p.run_due()
    p.stop()
    suffixes = {t.removeprefix("boiler/") for t in _topics(client)}
    assert suffixes <= set(V1_SUFFIXES)


def test_aucune_ecriture() -> None:
    source = pathlib.Path(publisher_module.__file__).read_text(encoding="utf-8")
    for interdit in ("def write", "WriteResult", ".write("):
        assert interdit not in source


# ---------------------------------------------------------------------------
# Comportements combines, caracterises explicitement
# ---------------------------------------------------------------------------


def test_exception_du_lecteur_apres_une_erreur_mqtt_deja_collectee() -> None:
    """CARACTERISATION d'un comportement DELIBERE et DOCUMENTE, pas une recette.

    Quand une erreur de publication a deja ete collectee et qu'une lecture
    ulterieure fait lever le lecteur, l'exception du lecteur remonte SEULE : les
    erreurs MQTT deja collectees sont perdues.

    Ce n'est pas une recommandation generale de perdre des erreurs. C'est le
    prix assume d'un arbitrage precis : une exception du lecteur signale un
    DEFAUT — C6 garantit qu'aucune issue de transport ne leve —, et l'emballer
    dans un `ExceptionGroup` avec du bruit de publication le noierait. Le
    diagnostic prime sur l'exhaustivite.

    Ce test FIGE ce comportement pour qu'il ne puisse ni changer en silence, ni
    passer pour un oubli.
    """

    class _MqttKoSurTelemetrie(FakeMqttClient):
        def publish(self, topic, payload, qos=0, retain=False):
            if "/telemetry/" in topic:
                raise RuntimeError(f"KO scalaire {topic}")
            return super().publish(topic, payload, qos=qos, retain=retain)

    class _LecteurQuiLeveALaSeconde(_Lecteur):
        def read(self, command: str):
            if len(self.appels) >= 1:
                self.appels.append(command)
                raise LookupError("defaut identifiable du lecteur")
            return super().read(command)

    client = _MqttKoSurTelemetrie()
    r = _LecteurQuiLeveALaSeconde()
    p, _, c = _demarre(reader=r, mqtt=client)
    etat_chaine_avant = p.state.chain_status

    with pytest.raises(LookupError, match="defaut identifiable") as capture:
        p.run_due()

    # L'exception du lecteur remonte SEULE, identite intacte.
    assert type(capture.value) is LookupError
    assert not isinstance(capture.value, ExceptionGroup)
    assert capture.value.__cause__ is None
    assert capture.value.__context__ is None

    # Une erreur MQTT avait bien ete collectee avant : elle ne remonte pas.
    assert r.appels == ["getTempA", "getTempKist"]
    assert not any(
        "/telemetry/" in h.publication.topic for h in client.publications
    )

    # La premiere mesure reste projetee OK et replanifiee.
    premiere = p.state.measurements["outdoor_temperature"]
    assert premiere.last_result is TransportStatus.OK
    assert premiere.has_value is True
    dues = {s.role for s in p.due_measurements()}
    assert "outdoor_temperature" not in dues

    # La mesure ayant leve, et toutes les suivantes, restent dues.
    assert "supply_temperature" in dues
    assert dues == {s.role for s in V1_MEASUREMENTS[1:]}

    # Aucun cycle cloture, aucune `chain` fabriquee, aucune conversion.
    assert p.state.cycle_completed is False
    assert p.state.chain_status is etat_chaine_avant
    assert p.state.chain_cause is None
    assert p.state.measurements["supply_temperature"].last_result is None
    assert not any(
        m.last_result is TransportStatus.TRANSPORT_ERROR
        for m in p.state.measurements.values()
    )


class _HorlogeQuiAvanceALaLecture(VirtualClock):
    """Fait avancer le monotone a chaque consultation, comme un cycle long.

    `VirtualClock.advance` deplace `now()` ET `monotonic()` ensemble, ce qui
    reproduit fidelement le temps qui passe pendant des lectures sequentielles
    de plusieurs secondes (C5 : 2,7 a 4,0 s par lecture).
    """

    def __init__(self, *a, pas: float = 0.0, **kw) -> None:
        super().__init__(*a, **kw)
        self.pas = pas

    def monotonic(self) -> float:
        valeur = super().monotonic()
        if self.pas:
            self.advance(self.pas)
        return valeur


def test_lot_de_taches_fige_au_debut_de_run_due() -> None:
    """Une tache devenue due PENDANT l'appel n'est jamais traitee dans cet appel.

    Sans ce gel, un cycle long declencherait en cascade le battement et
    l'instantane periodique dont les echeances tombent en cours de route — puis,
    au reveil suivant, de nouveau. Le lot est fige des la premiere lecture du
    monotone.
    """
    # 8 lectures + recalculs : le monotone progresse largement au-dela de 10 s
    # pendant l'appel, donc au-dela des echeances de battement et d'instantane.
    horloge = _HorlogeQuiAvanceALaLecture(_DEBUT, monotonic_start=1000.0, pas=1.0)
    config = ReadSurfaceConfig(snapshot_period_s=10, heartbeat_period_s=10)
    r = _Lecteur()
    p, client, _ = _demarre(reader=r, clock=horloge, config=config)

    debut = len(client.publications)
    p.run_due()
    premier = [t for t, _, _, _ in _depuis(client, debut)]

    # Le monotone a franchi les echeances de +10 s pendant l'appel.
    assert horloge.monotonic() > 1010.0

    # Chaque mesure initialement due est traitee AU PLUS UNE FOIS.
    assert r.appels == _CMDS
    assert len(r.appels) == len(set(r.appels))

    # Aucun battement : son echeance a ete franchie EN COURS d'appel.
    assert not any(t.endswith("bridge/heartbeat") for t in premier)

    # Instantanes : 8 intermediaires + 1 de fin de cycle, et RIEN de plus. Aucun
    # instantane periodique supplementaire du seul fait du franchissement.
    assert premier.count("boiler/bridge/telemetry_status") == 9
    assert sum(1 for t in premier if "/telemetry/" in t) == 8
    assert len(premier) == 17

    # -- second appel : la tache devenue due est traitee, une seule fois -----
    r.appels.clear()
    milieu = len(client.publications)
    p.run_due()
    second = [t for t, _, _, _ in _depuis(client, milieu)]

    # Le battement, reporte du premier appel, est publie ICI — et une seule
    # fois, bien que plusieurs periodes de 10 s aient ete franchies.
    assert second == ["boiler/bridge/heartbeat"]

    # Les mesures ne sont PAS encore dues : leurs echeances ont ete recalculees
    # a la fin de chaque tentative, jamais depuis l'echeance theorique manquee.
    assert r.appels == []

    # -- troisieme appel : rien n'est du, donc rien n'est publie ------------
    fin = len(client.publications)
    p.run_due()
    assert _depuis(client, fin) == []

    # -- quatrieme appel, apres une avance franche : un seul cycle ----------
    horloge.pas = 0.0  # horloge stable, pour une assertion exacte
    horloge.advance(120)
    r.appels.clear()
    dernier = len(client.publications)
    p.run_due()
    quatrieme = [t for t, _, _, _ in _depuis(client, dernier)]

    assert r.appels == _CMDS  # UN passage, pas douze
    assert quatrieme.count("boiler/bridge/telemetry_status") == 9
    assert quatrieme.count("boiler/bridge/heartbeat") == 1  # UN au maximum
    # Ordre deterministe : le battement vient en dernier.
    assert quatrieme[-1] == "boiler/bridge/heartbeat"


# ---------------------------------------------------------------------------
# C11 — reprise de presence apres reconnexion
# ---------------------------------------------------------------------------


class _SansCapacite:
    """Client conforme a `MqttClient` mais DEPOURVU de la capacite C11."""

    def connect(self, will=None): ...
    def disconnect(self): ...
    def subscribe(self, topic, qos=0): ...
    def publish(self, topic, payload, qos=0, retain=False): ...
    def set_message_handler(self, handler): ...


class _ConnexionQuiLeve(FakeMqttClient):
    def connect(self, will=None):
        raise OSError("ouverture impossible")


class _PresenceQuiLeve(FakeMqttClient):
    """Fait echouer, une fois, la publication de presence — et elle seule."""

    def __init__(self) -> None:
        super().__init__()
        self.armee = False

    def publish(self, topic, payload, qos=0, retain=False):
        if self.armee and topic.endswith("bridge/online"):
            self.armee = False
            raise RuntimeError("publication de presence impossible")
        return super().publish(topic, payload, qos=qos, retain=retain)


def _online_depuis(client, repere: int) -> list[tuple[str, bytes, int, bool]]:
    """Publications de presence emises APRES l'indice `repere`.

    La tranche est prise sur le journal COMPLET puis filtree : filtrer d'abord
    puis trancher avec un indice global rendrait l'assertion vacue.
    """
    return [p for p in _publies(client)[repere:] if p[0].endswith("bridge/online")]


def test_composition_sans_capacite_echoue_a_la_construction() -> None:
    """C11 §6.3 : ni `hasattr`, ni repli — un echec dur, visible, immediat."""
    from boilerack.transport.mqtt import MqttClient

    client = _SansCapacite()
    assert isinstance(client, MqttClient)  # le port est bien satisfait
    with pytest.raises(AttributeError):
        ReadSurfacePublisher(
            mqtt=client, clock=_clock(), connection=ConnectionState()
        )


def test_le_publieur_abonne_la_primitive_au_client() -> None:
    etat = ConnectionState()
    _, client = _publieur(connection=etat)
    client.fire_connected()
    assert etat.connected is True


def test_reconnexion_republie_online_une_fois() -> None:
    """Le defaut historique : telemetrie fraiche et presence retenue `offline`."""
    etat = ConnectionState()
    p, client = _publieur(connection=etat, reader=_Lecteur())
    p.start()
    repere = len(client.publications)

    client.fire_disconnected()  # perte inattendue ; le broker applique le testament
    client.fire_connected()  # Paho se reconnecte
    p.run_due()

    neuf = [
        (h.publication.topic, h.publication.payload, h.publication.qos, h.publication.retain)
        for h in client.publications[repere:]
    ]
    online = [x for x in neuf if x[0] == "boiler/bridge/online"]
    assert online == [("boiler/bridge/online", b"online", 1, True)]


def test_connack_initial_reussi_ne_republie_rien() -> None:
    """La base posee par `start()` neutralise le CONNACK initial."""
    p, client = _publieur(reader=_Lecteur())
    p.start()
    repere = len(client.publications)
    client.fire_connected()
    p.run_due()
    assert _online_depuis(client, repere) == []


def test_echec_initial_n_est_pas_ecrase_par_la_base() -> None:
    """§8.3 : le fait observe a autorite, meme s'il precede la fin de `start()`."""
    etat = ConnectionState()
    p, client = _publieur(connection=etat, reader=_Lecteur())
    p.start()
    client.fire_disconnected()  # CONNACK initial en echec
    assert etat.connected is False


def test_echec_initial_puis_reussite_republie_exactement_une_fois() -> None:
    """La sequence que l'ancien placement de la base faisait perdre."""
    p, client = _publieur(reader=_Lecteur())
    p.start()
    client.fire_disconnected()
    repere = len(client.publications)
    client.fire_connected()
    p.run_due()
    p.run_due()  # un second cycle ne republie pas
    neuf = [x for x in _publies(client)[repere:] if x[0] == "boiler/bridge/online"]
    assert neuf == [("boiler/bridge/online", b"online", 1, True)]


def test_deconnexion_avant_consommation_ne_republie_rien() -> None:
    p, client = _publieur(reader=_Lecteur())
    p.start()
    client.fire_disconnected()
    client.fire_connected()
    client.fire_disconnected()  # annule la reprise en attente
    repere = len(client.publications)
    p.run_due()
    assert _online_depuis(client, repere) == []


def test_reprise_ne_publie_aucun_autre_topic() -> None:
    """Ni scalaire, ni instantane, ni battement : seule la presence est restauree."""
    horloge = _clock()
    p, client = _publieur(clock=horloge, reader=_Lecteur())
    p.start()
    p.run_due()  # epuise les echeances initiales
    repere = len(client.publications)
    client.fire_disconnected()
    client.fire_connected()
    p.run_due()  # aucune echeance due : la reprise est seule
    assert [x[0] for x in _publies(client)[repere:]] == ["boiler/bridge/online"]


def test_reprise_ne_touche_ni_echeances_ni_fraicheur() -> None:
    """La reprise est ORTHOGONALE a l'ordonnancement et a l'etat de lecture."""
    p, client = _publieur(reader=_Lecteur())
    p.start()
    p.run_due()
    echeances = (p.due_at(), dict(p._next_due), p._next_snapshot_due, p._next_heartbeat_due)
    etat_avant = p.state

    client.fire_disconnected()
    client.fire_connected()
    p.run_due()

    assert (p.due_at(), dict(p._next_due), p._next_snapshot_due, p._next_heartbeat_due) == echeances
    assert p.state is etat_avant


def test_aucune_reprise_apres_arret() -> None:
    p, client = _publieur(reader=_Lecteur())
    p.start()
    client.fire_disconnected()
    client.fire_connected()  # reprise armee
    p.stop()
    with pytest.raises(RuntimeError):
        p.run_due()


def test_arret_sur_sans_notification_de_deconnexion() -> None:
    """R5 : la surete de `stop()` ne depend d'aucun rappel volontaire.

    Aucun `fire_disconnected()` n'est emis pendant l'arret : un `start()`
    ulterieur ne doit produire aucune republication redondante.
    """
    p, client = _publieur(reader=_Lecteur())
    p.start()
    client.fire_connected()
    p.stop()
    repere = len(client.publications)
    p.start()
    client.fire_connected()
    p.run_due()
    assert _online_depuis(client, repere) == [
        ("boiler/bridge/online", b"online", 1, True)
    ]  # celui de start()


def test_ouverture_qui_leve_laisse_le_publieur_non_demarre() -> None:
    """§12 : politique d'erreur inchangee, etat residuel inobservable."""
    p, _ = _publieur(mqtt=_ConnexionQuiLeve(), reader=_Lecteur())
    with pytest.raises(OSError):
        p.start()
    assert p.started is False
    with pytest.raises(RuntimeError):
        p.run_due()


def test_echec_de_publication_de_reprise_rejoint_le_groupe_du_cycle() -> None:
    """Aucune politique d'erreur nouvelle : la reprise suit celle des autres.

    L'erreur est COLLECTEE, jamais absorbee, et n'interrompt pas le cycle : les
    mesures dues restent traitees.
    """
    client = _PresenceQuiLeve()
    lecteur = _Lecteur()
    p, _ = _publieur(mqtt=client, reader=lecteur)
    p.start()
    p.run_due()  # epuise les echeances initiales
    client.fire_disconnected()
    client.fire_connected()
    client.armee = True
    lus_avant = len(lecteur.appels)

    with pytest.raises(ExceptionGroup) as capture:
        p.run_due()

    assert len(capture.value.exceptions) == 1
    assert isinstance(capture.value.exceptions[0], RuntimeError)
    assert len(lecteur.appels) >= lus_avant  # le cycle n'a pas ete interrompu


def test_arret_desarme_toute_reprise_en_attente() -> None:
    """§8.3 : `stop()` desarme. Verifie sur la primitive, seul point observable."""
    etat = ConnectionState()
    p, client = _publieur(connection=etat, reader=_Lecteur())
    p.start()
    client.fire_disconnected()
    client.fire_connected()  # reprise armee
    p.stop()
    assert etat.consume_recovery() is False


class _ConnackPendantStart(FakeMqttClient):
    """Client dont le CONNACK survient PENDANT `start()`, avant sa fin.

    Fidele au point qui compte : l'ouverture arme la boucle reseau en son sein,
    de sorte qu'un rappel peut etre traite avant que `start()` ne rende la main.
    Aucune autre mecanique de Paho n'est reproduite.
    """

    def __init__(self, etabli: bool) -> None:
        super().__init__()
        self.etabli = etabli

    def connect(self, will=None):
        super().connect(will)
        self._fire_connection(self.etabli)


def test_connack_reussi_pendant_start_ne_republie_rien() -> None:
    """La base precede l'ouverture : un succes recu tot n'arme rien."""
    client = _ConnackPendantStart(etabli=True)
    p, _ = _publieur(mqtt=client, reader=_Lecteur())
    p.start()
    repere = len(client.publications)
    p.run_due()
    assert _online_depuis(client, repere) == []


def test_connack_echoue_pendant_start_puis_reussite_republie_une_fois() -> None:
    """LE test de la course initiale.

    Un echec de CONNACK observe AVANT la fin de `start()` ne doit pas etre
    ecrase par la base : sans quoi la reussite suivante ne serait plus une
    transition, et la reprise serait definitivement perdue. C'est le defaut
    exact que corrige le placement de la base avant l'ouverture.
    """
    etat = ConnectionState()
    client = _ConnackPendantStart(etabli=False)
    p, _ = _publieur(mqtt=client, connection=etat, reader=_Lecteur())
    p.start()

    assert etat.connected is False  # le fait observe a eu autorite sur la base

    repere = len(client.publications)
    client.fire_connected()  # reussite ulterieure
    p.run_due()
    assert _online_depuis(client, repere) == [
        ("boiler/bridge/online", b"online", 1, True)
    ]
