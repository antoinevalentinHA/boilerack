"""Tests de `boilerack.runtime` — composition root et boucle exterieure (C8).

Aucun broker, aucun processus, aucun reseau, aucune horloge systeme. La frontiere
Paho n'est jamais franchie : le seul test qui exerce `build_runtime` remplace la
construction du client Paho par un double.
"""

from __future__ import annotations

import ast
import pathlib
import threading
from collections import Counter
from datetime import datetime, timezone

import pytest

from boilerack import runtime as runtime_module
from boilerack.adapters.config import MqttConfig, VclientConfig
from boilerack.adapters.mqtt_paho import PahoMqttClient
from boilerack.adapters.vclient_cli import VClientCliReader
from boilerack.clock import SystemClock
from boilerack.connection_state import ConnectionState
from boilerack.read_surface import ReadSurfaceConfig, ReadSurfacePublisher
from boilerack.read_surface.measurements import V1_MEASUREMENTS, MeasurementSpec
from boilerack.read_surface.state import ChainStatus
from boilerack.read_surface.topics import V1_SUFFIXES
from boilerack.runtime import (
    NeverStop,
    ReadSurfaceRunner,
    Runtime,
    RuntimeConfig,
    StopSignal,
    TransactionSurfaceConfig,
    build_runtime,
)
from boilerack.testing import FakeMqttClient, VirtualClock
from boilerack.transport.vclient import ReadResult, TransportStatus

_DEBUT = datetime(2026, 8, 6, 9, 0, 0, tzinfo=timezone.utc)
_CMDS = [s.read for s in V1_MEASUREMENTS]


def _clock() -> VirtualClock:
    return VirtualClock(_DEBUT, monotonic_start=1000.0)


class _Lecteur:
    """Lecteur programmable. Aucun processus, aucun `vclient` reel."""

    def __init__(self, plan: dict | None = None) -> None:
        self.plan = plan or {}
        self.appels: list[str] = []

    def read(self, command: str) -> ReadResult:
        self.appels.append(command)
        statut = self.plan.get(command, TransportStatus.OK)
        if statut is TransportStatus.OK:
            return ReadResult(status=statut, value=21.5)
        return ReadResult(status=statut)


class _ArretApres:
    """Demande l'arret apres `n` cycles complets.

    La boucle consulte le signal DEUX fois par cycle — a l'entree, puis apres
    l'attente. Compter les consultations plutot que les cycles rendrait les
    tests dependants de cette cadence interne ; on la neutralise ici.
    """

    def __init__(self, n: int) -> None:
        self.n = n
        self.consultations = 0

    def is_set(self) -> bool:
        self.consultations += 1
        return self.consultations > 2 * self.n


class _ArretImmediat:
    def is_set(self) -> bool:
        return True


class _Journal:
    """Publieur factice : journalise l'ordre exact des appels du runner."""

    def __init__(self, echeances: list[float] | None = None) -> None:
        self.appels: list[str] = []
        self.echeances = echeances or [1000.0]
        self._i = 0
        self.started = False

    def start(self) -> None:
        self.appels.append("start")
        self.started = True

    def stop(self) -> None:
        self.appels.append("stop")
        self.started = False

    def due_at(self) -> float:
        self.appels.append("due_at")
        valeur = self.echeances[min(self._i, len(self.echeances) - 1)]
        self._i += 1
        return valeur

    def run_due(self) -> None:
        self.appels.append("run_due")


class _HorlogeJournal(VirtualClock):
    """Horloge virtuelle qui journalise ses sommeils dans une trace partagee."""

    def __init__(self, trace: list[str], *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.trace = trace

    def sleep(self, seconds: float) -> None:
        self.trace.append(f"sleep({seconds})")
        super().sleep(seconds)


def _runner(publisher, clock=None, stop=None) -> ReadSurfaceRunner:
    return ReadSurfaceRunner(
        publisher=publisher,
        clock=clock if clock is not None else _clock(),
        stop=stop if stop is not None else _ArretApres(1),
    )


def _reel(reader=None, mqtt=None, clock=None, config=None, stop=None, connection=None):
    """Vrai publieur, vrai runner, doubles pour MQTT, lecteur et horloge."""
    c = clock if clock is not None else _clock()
    client = mqtt if mqtt is not None else FakeMqttClient()
    p = ReadSurfacePublisher(
        mqtt=client,
        clock=c,
        connection=connection if connection is not None else ConnectionState(),
        reader=reader if reader is not None else _Lecteur(),
        config=config if config is not None else ReadSurfaceConfig(),
    )
    return ReadSurfaceRunner(
        publisher=p, clock=c, stop=stop if stop is not None else _ArretApres(1)
    ), p, client, c


# ---------------------------------------------------------------------------
# Construction et frontieres a l'import
# ---------------------------------------------------------------------------


def test_aucun_effet_de_bord_a_l_import() -> None:
    """Le module ne fait, au niveau superieur, que declarer.

    Verifie sur l'AST plutot qu'en rechargeant le module : un `importlib.reload`
    recreerait les classes et casserait l'identite des types pour les autres
    tests. Aucun appel au niveau superieur, sauf ceux des decorateurs et des
    valeurs par defaut de champs, qui ne construisent aucune ressource.
    """
    arbre = ast.parse(pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8"))
    autorises = (
        ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef,
        ast.AnnAssign, ast.Assign, ast.Expr, ast.If,
    )
    for noeud in arbre.body:
        assert isinstance(noeud, autorises), ast.dump(noeud)
        if isinstance(noeud, (ast.Assign, ast.AnnAssign)) and noeud.value is not None:
            assert isinstance(noeud.value, (ast.Constant, ast.List, ast.Tuple)), ast.dump(noeud)
        if isinstance(noeud, ast.Expr):  # seule une docstring est toleree
            assert isinstance(noeud.value, ast.Constant)
        if isinstance(noeud, ast.If):
            # SEULE forme de `if` toleree : la garde `TYPE_CHECKING`, dont le
            # corps n'est JAMAIS execute a l'import et ne peut donc rien
            # construire. Elle est admise strictement : test litteral, corps
            # d'imports uniquement, aucun `else`. Toute autre condition, ou un
            # corps portant autre chose que des imports, reste refusee.
            assert isinstance(noeud.test, ast.Name), ast.dump(noeud)
            assert noeud.test.id == "TYPE_CHECKING", ast.dump(noeud)
            assert noeud.orelse == [], ast.dump(noeud)
            for interne in noeud.body:
                assert isinstance(interne, (ast.Import, ast.ImportFrom)), ast.dump(interne)


def test_le_publieur_ne_construit_aucun_adaptateur() -> None:
    """La frontiere de C7-C3 est preservee : tout lui est injecte."""
    import inspect

    parametres = set(inspect.signature(ReadSurfacePublisher.__init__).parameters)
    assert parametres == {
        "self", "mqtt", "clock", "connection", "reader", "specs", "config"
    }
    source = pathlib.Path(
        inspect.getfile(ReadSurfacePublisher)
    ).read_text(encoding="utf-8")
    arbre = ast.parse(source)
    noms = {n.id for n in ast.walk(arbre) if isinstance(n, ast.Name)}
    assert not noms & {"PahoMqttClient", "SubprocessRunner", "SystemClock", "VClientCliReader"}


def test_seul_le_composition_root_construit_les_adaptateurs() -> None:
    source = pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8")
    for concret in ("SystemClock", "PahoMqttClient", "SubprocessRunner", "VClientCliReader"):
        assert f"{concret}(" in source


def test_runner_ne_porte_aucune_logique_metier() -> None:
    """Le runner ignore mesures, statuts, topics et instantanes."""
    source = pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8")
    arbre = ast.parse(source)
    for n in ast.walk(arbre):  # retire les docstrings avant analyse
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)) and n.body:
            p = n.body[0]
            if isinstance(p, ast.Expr) and isinstance(p.value, ast.Constant) and isinstance(
                p.value.value, str
            ):
                n.body.pop(0)
    code = ast.unparse(arbre)
    for metier in (
        "TransportStatus", "record_result", "complete_cycle", "build_snapshot",
        "format_scalar", "telemetry", "heartbeat", "bridge/", "MqttWill",
    ):
        assert metier not in code, metier


# ---------------------------------------------------------------------------
# Configuration d'assemblage
# ---------------------------------------------------------------------------


def _config(**surcharges) -> RuntimeConfig:
    base = dict(
        mqtt=MqttConfig(host="broker.invalid"),
        vclient=VclientConfig(executable="vclient"),
    )
    base.update(surcharges)
    return RuntimeConfig(**base)  # type: ignore[arg-type]


def test_config_contient_les_configurations_existantes() -> None:
    """Aucune redeclaration : les configurations existantes restent seules autorites.

    W4-E2 ajoute `transaction_surface`, qui est une AUTORITE D'ACTIVATION et non
    une redeclaration : elle ne reprend aucun champ d'une autre structure.

    `g2-sortie-preuve-transport.md` ajoute `evidence_dir`, pour la meme raison :
    c'est un INTERRUPTEUR DE CAMPAGNE, resolu depuis l'environnement, qui ne
    reprend aucun champ d'aucune autre structure. Ni l'un ni l'autre ne relache
    ce que ce test garde.

    La liste reste FERMEE — un septieme membre fait rougir ce test.
    """
    import dataclasses

    champs = {f.name for f in dataclasses.fields(RuntimeConfig)}
    assert champs == {
        "mqtt",
        "vclient",
        "read_surface",
        "specs",
        "transaction_surface",
        "evidence_dir",
    }
    for interdit in ("host", "port", "prefix", "snapshot_period_s", "heartbeat_period_s"):
        assert interdit not in champs
    # L'autorite ne porte qu'un booleen : elle ne duplique rien.
    assert {f.name for f in dataclasses.fields(TransactionSurfaceConfig)} == {"enabled"}


def test_config_gelee_et_specs_immuables() -> None:
    config = _config()
    with pytest.raises(Exception):
        config.mqtt = MqttConfig(host="autre")  # type: ignore[misc]
    assert isinstance(config.specs, tuple)


def test_config_defaut_read_surface() -> None:
    assert _config().read_surface == ReadSurfaceConfig()


@pytest.mark.parametrize(
    ("champ", "valeur"),
    [("mqtt", "broker"), ("vclient", None), ("read_surface", 30)],
)
def test_config_refuse_un_type_errone(champ: str, valeur: object) -> None:
    with pytest.raises(ValueError, match="doit etre un"):
        _config(**{champ: valeur})


def test_config_ne_porte_aucune_valeur_de_site() -> None:
    """Ni hote, ni executable par defaut : ce sont des valeurs de site."""
    import dataclasses

    champs = {f.name: f for f in dataclasses.fields(RuntimeConfig)}
    assert champs["mqtt"].default is dataclasses.MISSING
    assert champs["vclient"].default is dataclasses.MISSING


# ---------------------------------------------------------------------------
# Boucle : ordre des appels
# ---------------------------------------------------------------------------


def test_ordre_start_due_at_wait_run_due_stop() -> None:
    trace: list[str] = []
    journal = _Journal(echeances=[1030.0])
    horloge = _HorlogeJournal(trace, _DEBUT, monotonic_start=1000.0)
    runner = _runner(journal, clock=horloge, stop=_ArretApres(1))
    runner.run()
    # `sleep` est intercale dans la trace du publieur au bon endroit.
    assert journal.appels == ["start", "due_at", "run_due", "stop"]
    assert trace == ["sleep(30.0)"]


def test_start_appele_une_seule_fois() -> None:
    journal = _Journal()
    _runner(journal, stop=_ArretApres(3)).run()
    assert journal.appels.count("start") == 1
    assert journal.appels.count("stop") == 1


def test_plusieurs_cycles() -> None:
    journal = _Journal(echeances=[1010.0, 1020.0, 1030.0])
    horloge = _clock()
    _runner(journal, clock=horloge, stop=_ArretApres(3)).run()
    assert journal.appels == [
        "start",
        "due_at", "run_due",
        "due_at", "run_due",
        "due_at", "run_due",
        "stop",
    ]
    assert list(horloge.sleeps) == [10.0, 10.0, 10.0]


def test_aucun_appel_apres_l_arret() -> None:
    journal = _Journal()
    _runner(journal, stop=_ArretApres(2)).run()
    assert journal.appels[-1] == "stop"
    assert "run_due" not in journal.appels[journal.appels.index("stop"):]


def test_le_runner_ne_cree_aucune_derive() -> None:
    """Il dort jusqu'a l'echeance demandee, sans marge ni rattrapage propre."""
    journal = _Journal(echeances=[1030.0, 1060.0, 1090.0])
    horloge = _clock()
    _runner(journal, clock=horloge, stop=_ArretApres(3)).run()
    assert list(horloge.sleeps) == [30.0, 30.0, 30.0]
    assert horloge.monotonic() == 1090.0


# ---------------------------------------------------------------------------
# Attente
# ---------------------------------------------------------------------------


def test_echeance_passee_aucune_attente() -> None:
    """Aucune duree negative, et `sleep` n'est meme pas appele."""
    journal = _Journal(echeances=[900.0])
    horloge = _clock()
    _runner(journal, clock=horloge, stop=_ArretApres(1)).run()
    assert list(horloge.sleeps) == []
    assert journal.appels == ["start", "due_at", "run_due", "stop"]


def test_echeance_exactement_atteinte_aucune_attente() -> None:
    journal = _Journal(echeances=[1000.0])
    horloge = _clock()
    _runner(journal, clock=horloge, stop=_ArretApres(1)).run()
    assert list(horloge.sleeps) == []


def test_attente_fondee_sur_le_monotone_pas_sur_l_heure_murale() -> None:
    source = pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8")
    assert "monotonic()" in source
    for interdit in ("datetime.now(", "utcnow(", "time.sleep(", "time.monotonic("):
        assert interdit not in source


# ---------------------------------------------------------------------------
# Arret
# ---------------------------------------------------------------------------


def test_arret_demande_avant_le_premier_cycle() -> None:
    journal = _Journal()
    _runner(journal, stop=_ArretImmediat()).run()
    assert journal.appels == ["start", "stop"]


def test_arret_apres_un_cycle() -> None:
    journal = _Journal()
    _runner(journal, stop=_ArretApres(1)).run()
    assert journal.appels.count("run_due") == 1


def test_arret_apres_plusieurs_cycles() -> None:
    journal = _Journal()
    _runner(journal, stop=_ArretApres(4)).run()
    assert journal.appels.count("run_due") == 4


def test_arret_survenant_pendant_l_attente_evite_un_cycle_superflu() -> None:
    """Consulte apres l'attente : aucun travail n'est fait apres la demande."""

    class _ArretPendantAttente:
        def __init__(self) -> None:
            self.consultations = 0

        def is_set(self) -> bool:
            self.consultations += 1
            # 1re : entree dans la boucle -> False ; 2e, apres l'attente -> True.
            return self.consultations >= 2

    journal = _Journal(echeances=[1030.0])
    horloge = _clock()
    _runner(journal, clock=horloge, stop=_ArretPendantAttente()).run()
    assert journal.appels == ["start", "due_at", "stop"]
    assert list(horloge.sleeps) == [30.0]  # l'attente a bien eu lieu


def test_le_signal_d_arret_est_obligatoire() -> None:
    """Aucun signal d'arret implicite : une boucle sans sortie se DEMANDE.

    Verrouille la decision de C8 : `stop` n'a pas de valeur par defaut. Une
    boucle qui ne s'arrete jamais doit etre reclamee explicitement — en passant
    `NeverStop()` —, elle ne s'obtient jamais par omission de l'argument.

    Le message de la `TypeError` n'est pas verifie : il appartient a CPython.
    """
    journal = _Journal()
    horloge = _clock()
    # Le meme appel, complet, reussit : seul `stop` manque ci-dessous.
    ReadSurfaceRunner(publisher=journal, clock=horloge, stop=NeverStop())
    with pytest.raises(TypeError):
        ReadSurfaceRunner(publisher=journal, clock=horloge)  # type: ignore[call-arg]


def test_never_stop_ne_demande_jamais_l_arret() -> None:
    assert NeverStop().is_set() is False


def test_threading_event_satisfait_le_protocole() -> None:
    """`threading.Event` convient structurellement, sans import dans le module."""
    evenement = threading.Event()
    # `StopSignal` n'est volontairement pas `runtime_checkable` : la conformite
    # se prouve en l'utilisant, pas par un `isinstance` qui n'inspecte que les
    # noms de methodes.
    with pytest.raises(TypeError, match="runtime_checkable"):
        isinstance(evenement, StopSignal)  # noqa: B015
    journal = _Journal()
    evenement.set()
    _runner(journal, stop=evenement).run()
    assert journal.appels == ["start", "stop"]
    source = pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8")
    arbre = ast.parse(source)
    imports = {
        a.name.split(".")[0]
        for n in ast.walk(arbre)
        if isinstance(n, (ast.Import, ast.ImportFrom))
        for a in n.names
    }
    assert "threading" not in imports


# ---------------------------------------------------------------------------
# Politique d'erreur
# ---------------------------------------------------------------------------


class _JournalQuiLeve(_Journal):
    """Publieur factice qui echoue a un endroit precis.

    `stop_echoue` est independant de `ou` : c'est ce qui permet d'exercer les
    deux echecs simultanes sans ambiguite.
    """

    def __init__(
        self,
        ou: str | None,
        exc: Exception | None = None,
        demarre: bool = True,
        stop_echoue: bool = False,
        **kw,
    ) -> None:
        super().__init__(**kw)
        self.ou = ou
        self.exc = exc or RuntimeError("panne")
        self._demarre = demarre
        self.stop_echoue = stop_echoue

    def start(self) -> None:
        super().start()
        self.started = self._demarre
        if self.ou == "start":
            raise self.exc

    def due_at(self) -> float:
        if self.ou == "due_at":
            self.appels.append("due_at")
            raise self.exc
        return super().due_at()

    def run_due(self) -> None:
        super().run_due()
        if self.ou == "run_due":
            raise self.exc

    def stop(self) -> None:
        super().stop()
        if self.stop_echoue:
            raise RuntimeError("arret impossible")


def test_start_echoue_sans_demarrage_declare() -> None:
    """Rien n'a ete ouvert : aucun arret de secours, aucune boucle."""
    journal = _JournalQuiLeve("start", OSError("connexion refusee"), demarre=False)
    with pytest.raises(OSError, match="connexion refusee") as capture:
        _runner(journal).run()
    assert not isinstance(capture.value, ExceptionGroup)
    assert journal.appels == ["start"]


def test_start_echoue_apres_connexion_declenche_un_arret_de_secours() -> None:
    """C7-C3A : la connexion peut etre ouverte alors qu'une publication echoue."""
    journal = _JournalQuiLeve("start", OSError("publication impossible"), demarre=True)
    with pytest.raises(OSError, match="publication impossible"):
        _runner(journal).run()
    assert journal.appels == ["start", "stop"]  # la connexion n'est pas fuitee


def test_start_puis_arret_de_secours_echouent_tous_deux() -> None:
    journal = _JournalQuiLeve(
        "start", OSError("publication impossible"), demarre=True, stop_echoue=True
    )
    with pytest.raises(ExceptionGroup) as capture:
        _runner(journal).run()
    assert len(capture.value.exceptions) == 2
    assert isinstance(capture.value.exceptions[0], OSError)
    assert isinstance(capture.value.exceptions[1], RuntimeError)


def test_due_at_echoue() -> None:
    journal = _JournalQuiLeve("due_at", RuntimeError("sans start"))
    with pytest.raises(RuntimeError, match="sans start"):
        _runner(journal).run()
    assert journal.appels == ["start", "due_at", "stop"]  # l'arret est tente


def test_attente_echoue() -> None:
    class _HorlogeQuiLeve(VirtualClock):
        def sleep(self, seconds: float) -> None:
            raise OSError("sommeil interrompu")

    journal = _Journal(echeances=[1030.0])
    horloge = _HorlogeQuiLeve(_DEBUT, monotonic_start=1000.0)
    with pytest.raises(OSError, match="sommeil interrompu"):
        _runner(journal, clock=horloge).run()
    assert journal.appels == ["start", "due_at", "stop"]


def test_run_due_echoue_arrete_la_boucle_et_remonte() -> None:
    """Le runner ne decide d'aucune politique de reprise."""
    groupe = ExceptionGroup("echecs MQTT", [RuntimeError("KO topic")])
    journal = _JournalQuiLeve("run_due", groupe)
    with pytest.raises(ExceptionGroup) as capture:
        _runner(journal, stop=_ArretApres(5)).run()
    assert capture.value is groupe  # identite preservee, aucune traduction
    assert journal.appels == ["start", "due_at", "run_due", "stop"]


def test_run_due_puis_stop_echouent_tous_deux() -> None:
    groupe = ExceptionGroup("echecs MQTT", [RuntimeError("KO topic")])
    journal = _JournalQuiLeve("run_due", groupe, stop_echoue=True)
    with pytest.raises(ExceptionGroup) as capture:
        _runner(journal, stop=_ArretApres(5)).run()
    assert len(capture.value.exceptions) == 2
    assert capture.value.exceptions[0] is groupe
    assert isinstance(capture.value.exceptions[1], RuntimeError)


def test_stop_echoue_seul_remonte_tel_quel() -> None:
    journal = _JournalQuiLeve(None, stop_echoue=True)
    with pytest.raises(RuntimeError, match="arret impossible") as capture:
        _runner(journal, stop=_ArretImmediat()).run()
    assert not isinstance(capture.value, ExceptionGroup)


def test_base_exception_non_capturee() -> None:
    """Une interruption traverse : ce n'est pas une panne, et l'arret propre
    n'est PAS declenche — le brancher releve de la gestion de signaux, reportee."""
    _journal = _JournalQuiLeve("run_due", RuntimeError("jamais"))

    class _Interrupteur(_Journal):
        def run_due(self) -> None:
            self.appels.append("run_due")
            raise KeyboardInterrupt("Ctrl-C")

    interrupteur = _Interrupteur()
    with pytest.raises(KeyboardInterrupt) as capture:
        _runner(interrupteur, stop=_ArretApres(5)).run()
    assert not isinstance(capture.value, ExceptionGroup)
    assert "stop" not in interrupteur.appels


# ---------------------------------------------------------------------------
# Integration hors production : vrai publieur, doubles pour tout le reste
# ---------------------------------------------------------------------------


def test_integration_hors_production() -> None:
    """start -> lectures initiales -> cycle 30 s -> battement -> instantane -> stop.

    Vrai `ReadSurfacePublisher`, vrai `ReadSurfaceRunner`. Faux MQTT, faux
    lecteur, horloge virtuelle, arret virtuel. Aucun adaptateur reel.
    """
    lecteur = _Lecteur()
    config = ReadSurfaceConfig(snapshot_period_s=30, heartbeat_period_s=30)
    runner, publisher, client, horloge = _reel(
        reader=lecteur, config=config, stop=_ArretApres(3)
    )
    runner.run()

    topics = [h.publication.topic for h in client.publications]
    comptes = Counter(topics)

    # -- cycle de vie ------------------------------------------------------
    assert client.connection_events == ("connect", "disconnect")
    assert topics[0] == "boiler/bridge/online"
    assert client.publications[0].publication.payload == b"online"
    assert topics[-1] == "boiler/bridge/online"
    assert client.publications[-1].publication.payload == b"offline"
    assert comptes["boiler/bridge/online"] == 2

    # -- calendrier reellement parcouru ------------------------------------
    # Le premier cycle est du immediatement : aucune attente. Les deux
    # suivants dorment 30 s. Le temps virtuel avance de 1000 a 1060.
    assert list(horloge.sleeps) == [30.0, 30.0]
    assert horloge.monotonic() == 1060.0

    # t=1000 : les huit mesures ; t=1030 : les trois de periode 30 s ;
    # t=1060 : ces trois-la de nouveau, plus les cinq de periode 60 s.
    assert lecteur.appels[:8] == _CMDS
    assert lecteur.appels[8:11] == _CMDS[:3]
    assert lecteur.appels[11:] == _CMDS
    assert len(lecteur.appels) == 19

    # -- publications scalaires : exactement une par lecture reussie -------
    for spec in V1_MEASUREMENTS:
        attendu = 3 if spec.period_s == 30 else 2
        assert comptes[f"boiler/{spec.suffix}"] == attendu, spec.role
    assert sum(v for k, v in comptes.items() if "/telemetry/" in k) == 19

    # -- instantanes et battement ------------------------------------------
    assert comptes["boiler/bridge/telemetry_status"] == 23
    assert comptes["boiler/bridge/heartbeat"] == 2

    # -- aucun topic hors de la surface v1 ---------------------------------
    assert {t.removeprefix("boiler/") for t in topics} <= set(V1_SUFFIXES)

    # -- etat final ---------------------------------------------------------
    assert publisher.state.chain_status is ChainStatus.OK
    assert all(m.has_value for m in publisher.state.measurements.values())
    assert publisher.started is False


def test_integration_un_echec_de_lecture_se_voit_dans_chain() -> None:
    lecteur = _Lecteur(plan={"getTempA": TransportStatus.TIMEOUT})
    runner, publisher, _, _ = _reel(reader=lecteur, stop=_ArretApres(1))
    runner.run()
    assert publisher.state.chain_status is ChainStatus.DEGRADED
    assert publisher.state.chain_cause is TransportStatus.TIMEOUT


# ---------------------------------------------------------------------------
# `build_runtime` — cablage reel, frontiere Paho remplacee
# ---------------------------------------------------------------------------


class _FauxPaho:
    """Surface `PahoLike` minimale. Aucune socket, aucun reseau."""

    on_connect = on_disconnect = on_publish = on_message = None

    def connect(self, host, port, keepalive): ...
    def disconnect(self): ...
    def loop_start(self): ...
    def loop_stop(self): ...
    def subscribe(self, topic, qos=0): ...
    def publish(self, topic, payload, qos=0, retain=False): ...
    def will_set(self, topic, payload=None, qos=0, retain=False): ...
    def will_clear(self): ...


def test_build_runtime_cable_les_adaptateurs_reels(monkeypatch) -> None:
    """Vrais `PahoMqttClient`, `VClientCliReader` et publieur ; Paho remplace."""
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))

    config = RuntimeConfig(
        mqtt=MqttConfig(host="broker.invalid", port=1884),
        vclient=VclientConfig(executable="vclient", host="pi.invalid", port=3002),
        read_surface=ReadSurfaceConfig(prefix="maison/boiler"),
    )
    rt = build_runtime(config, NeverStop())

    assert isinstance(rt, Runtime)
    assert isinstance(rt.publisher, ReadSurfacePublisher)
    assert isinstance(rt.runner, ReadSurfaceRunner)
    assert rt.runner.publisher is rt.publisher

    # La configuration de lecture a bien ete cablee, et rien n'a demarre.
    assert rt.publisher.online_topic == "maison/boiler/bridge/online"
    assert rt.publisher.started is False


def test_build_runtime_construit_un_lecteur_reel(monkeypatch) -> None:
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))
    rt = build_runtime(_config(), NeverStop())
    lecteur = rt.publisher._reader  # type: ignore[attr-defined]
    assert isinstance(lecteur, VClientCliReader)
    # Construit avec sa configuration : la commande porte l'executable demande.
    assert lecteur.build_args("getTempA")[0] == "vclient"


def test_build_runtime_utilise_l_horloge_systeme(monkeypatch) -> None:
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))
    rt = build_runtime(_config(), NeverStop())
    assert isinstance(rt.runner._clock, SystemClock)  # type: ignore[attr-defined]


def test_build_runtime_partage_une_seule_horloge(monkeypatch) -> None:
    """Le publieur et le runner recoivent EXACTEMENT la meme instance.

    Deux `SystemClock` distinctes se comporteraient de facon equivalente : une
    comparaison de valeurs ne prouverait donc rien. C'est l'identite qui compte,
    parce qu'elle est ce qui rend l'assemblage substituable par une horloge
    virtuelle unique — sans quoi le temps du runner et celui du publieur
    pourraient diverger sous test.

    Inspection d'attributs prives assumee : c'est un test d'architecture, et
    exposer une propriete publique pour le seul confort du test elargirait
    l'API sans consommateur.
    """
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))
    rt = build_runtime(_config(), NeverStop())
    horloge_runner = rt.runner._clock  # type: ignore[attr-defined]
    horloge_publieur = rt.publisher._clock  # type: ignore[attr-defined]
    assert horloge_runner is horloge_publieur
    assert build_runtime(_config(), NeverStop()).runner._clock is not horloge_runner  # type: ignore[attr-defined]


def test_build_runtime_n_ouvre_ni_socket_ni_processus(monkeypatch) -> None:
    """Construire n'est pas connecter : aucune socket, aucun sous-processus."""
    import socket
    import subprocess

    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))
    monkeypatch.setattr(
        socket, "socket", lambda *a, **k: pytest.fail("socket interdite")
    )
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: pytest.fail("subprocess interdit")
    )
    monkeypatch.setattr(
        subprocess, "Popen", lambda *a, **k: pytest.fail("subprocess interdit")
    )
    rt = build_runtime(_config(), NeverStop())
    assert rt.publisher.started is False


def test_build_runtime_accepte_une_horloge_injectee(monkeypatch) -> None:
    """Couture ouverte par C9 : l'horloge fournie est celle qui est cablee.

    Le parametre est optionnel et reserve aux mots-cles ; les appels a deux
    arguments positionnels de ce fichier restent valides sans modification.
    """
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))
    horloge = _clock()
    rt = build_runtime(_config(), NeverStop(), clock=horloge)
    assert rt.runner._clock is horloge  # type: ignore[attr-defined]
    assert rt.publisher._clock is horloge  # type: ignore[attr-defined]


def test_build_runtime_partage_l_horloge_injectee(monkeypatch) -> None:
    """L'invariant d'instance unique vaut aussi pour une horloge injectee."""
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))
    rt = build_runtime(_config(), NeverStop(), clock=_clock())
    assert rt.runner._clock is rt.publisher._clock  # type: ignore[attr-defined]


def test_le_parametre_d_horloge_est_reserve_aux_mots_cles() -> None:
    """Une horloge ne peut pas etre fournie par accident en position."""
    import inspect

    parametres = inspect.signature(build_runtime).parameters
    assert parametres["clock"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parametres["clock"].default is None


def test_build_runtime_accepte_des_specs_personnalisees(monkeypatch) -> None:
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: _FauxPaho()))
    lentes = (
        MeasurementSpec(
            role="x", read="getX", suffix="telemetry/x", period_s=100, fresh_max_s=300
        ),
    )
    rt = build_runtime(_config(specs=lentes), NeverStop())
    assert set(rt.publisher.state.measurements) == {"x"}


# ---------------------------------------------------------------------------
# Frontieres du module
# ---------------------------------------------------------------------------

_INTERDITS = {"paho", "asyncio", "threading", "signal", "argparse", "os"}


def _imports(module) -> set[str]:
    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
    noms: set[str] = set()
    for n in ast.walk(ast.parse(source)):
        if isinstance(n, ast.Import):
            noms.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            noms.add(n.module.split(".")[0])
    return noms


def test_aucun_import_technique_direct() -> None:
    """Ni Paho, ni asyncio, ni thread, ni signal, ni CLI dans ce module."""
    assert _imports(runtime_module) & _INTERDITS == set()


def test_aucune_boucle_infinie_sans_sortie() -> None:
    source = pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8")
    assert "while True" not in source
    assert "while not self._stop.is_set()" in source


def test_aucune_ecriture_chaudiere() -> None:
    source = pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8")
    for interdit in ("def write", "WriteResult", "set_temp", ".write("):
        assert interdit not in source


def test_aucun_secret_ni_valeur_de_site() -> None:
    """Aucun hote, aucun chemin, aucun identifiant en dur."""
    source = pathlib.Path(runtime_module.__file__).read_text(encoding="utf-8")
    import re

    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", source)  # adresse IP
    for interdit in ("password", "passwd", "/home/", "/dev/tty", "localhost", "192.168"):
        assert interdit not in source.lower()


# ---------------------------------------------------------------------------
# C11 — cablage de l'etat de connexion par la racine de composition
# ---------------------------------------------------------------------------


def test_build_runtime_cable_l_etat_de_connexion(monkeypatch) -> None:
    """La racine cree la primitive ; le publieur l'abonne au client reel."""
    vues: list[str] = []

    class _Paho:
        on_connect = on_disconnect = on_publish = on_message = None

        def will_set(self, *a, **k): ...
        def will_clear(self): ...
        def connect(self, *a, **k): ...
        def disconnect(self): ...
        def loop_start(self): ...
        def loop_stop(self): ...
        def subscribe(self, *a, **k): ...
        def publish(self, *a, **k): ...

    faux = _Paho()
    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(lambda cfg: faux))
    rt = build_runtime(
        RuntimeConfig(
            mqtt=MqttConfig(host="broker.invalid"),
            vclient=VclientConfig(executable="vclient"),
        ),
        NeverStop(),
    )
    # Le rappel a bien ete enregistre par le publieur sur le client construit.
    assert rt.publisher._mqtt._connection_handler is not None
    # Et il alimente reellement la primitive du publieur.
    rt.publisher._mqtt._connection_handler(False)
    rt.publisher._mqtt._connection_handler(True)
    assert rt.publisher._connection.consume_recovery() is True
    assert vues == []
