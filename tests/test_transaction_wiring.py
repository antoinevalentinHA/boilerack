"""Cablage runtime de la voie transactionnelle (lot W3).

Ces tests prouvent que W0 + W1 + W2 se composent REELLEMENT, avec les classes de
PRODUCTION partout ou W4 n'est pas necessaire :

    PahoMqttClient (reel)  -> CommandIntake (reel)  -> TransactionalCore (reel)
    -> TransactionSurface (reel) -> ReadSurfaceRunner (reel)

Les seuls doubles se tiennent aux deux frontieres de W4 — le transport
`vclient` et le profil — plus le client Paho lui-meme, frontiere de test deja
prevue par C4 (`PahoLike` est injectable).

Depuis W4-D, un profil de PRODUCTION existe ; ces tests continuent d'employer le
DOUBLE, et c'est deliberé : ils eprouvent le cablage W3, pas le contenu du
profil reel, et le double porte les roles varies dont ils ont besoin. Le profil
de production a ses propres tests.

Aucun broker, aucun Pi, aucun `vcontrold`, aucune chaudiere, aucun reseau,
aucune attente reelle, aucun `sleep` de test.
"""

from __future__ import annotations

import ast
import inspect
import json
import logging
import pathlib
import threading
from datetime import datetime, timedelta, timezone

import pytest

from boilerack.adapters.config import MqttConfig
from boilerack.adapters.mqtt_paho import PahoMqttClient
from boilerack.command_intake import CommandIntake
from boilerack.connection_state import ConnectionState
from boilerack.core.ack import AckStatus, Reason
from boilerack.core.engine import DEFAULT_QUEUE_CAPACITY
from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.measurements import MeasurementSpec
from boilerack.read_surface.publisher import ReadSurfacePublisher
from boilerack.runtime import ReadSurfaceRunner
from boilerack.testing import VirtualClock, build_fake_profile
from boilerack.transaction_wiring import (
    COMMAND_QOS,
    build_transaction_surface,
)
from boilerack.transport.mqtt import Message
from wiring_support import (
    OperationVClientSimultanee,
    PahoDouble,
    PahoMessage,
    StopApres,
    StopArme,
    VClientEnregistreur,
    sans_bloquer,
)

DEBUT = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

#: Configuration MQTT de test aux autorites NON DEFAUT, afin qu'un cablage qui
#: se rabattrait sur un defaut de bibliotheque soit immediatement visible.
CONFIG = MqttConfig(
    host="broker.test",
    command_topic="site/commande",
    ack_topic_prefix="site/acquittement",
)

SPEC = MeasurementSpec(
    role="sonde", read="get_sonde", suffix="sonde", period_s=60, fresh_max_s=180
)


# ---------------------------------------------------------------------------
# Outillage
# ---------------------------------------------------------------------------


def rid(n: int) -> str:
    """UUID v4 canonique, deterministe et distinct par `n`."""
    return f"00000000-0000-4000-8000-{n:012d}"


def payload(request_id: str, role: str, value, *, ttl_s: float = 3600.0) -> bytes:
    """Payload de commande valide au sens C3 : six champs exacts."""
    corps = {
        "request_id": request_id,
        "ts": DEBUT.isoformat(),
        "expires_at": (DEBUT + timedelta(seconds=ttl_s)).isoformat(),
        "source": "test-w3",
        "role": role,
        "value": value,
    }
    return json.dumps(corps).encode("utf-8")


def message(request_id: str = None, role: str = "temp_consigne", value=21.0, **kw):
    """`Message` entrant, tel que l'adaptateur le fabrique."""
    return Message(
        topic=CONFIG.command_topic,
        payload=payload(request_id or rid(1), role, value, **kw),
        qos=COMMAND_QOS,
    )


def paho_message(request_id: str = None, role: str = "temp_consigne", value=21.0, **kw):
    """Message au format Paho, pour traverser `_on_message`."""
    return PahoMessage(
        topic=CONFIG.command_topic,
        payload=payload(request_id or rid(1), role, value, **kw),
        qos=COMMAND_QOS,
    )


def _surface(*, config: MqttConfig = CONFIG, lectures: dict | None = None, **kw):
    """Surface transactionnelle REELLE, cablee sur des doubles de frontiere."""
    paho = PahoDouble()
    mqtt = PahoMqttClient(config, client=paho)
    paho.adaptateur = mqtt
    clock = VirtualClock(DEBUT)
    vclient = VClientEnregistreur(lectures)
    surface = build_transaction_surface(
        mqtt=mqtt,
        clock=clock,
        config=config,
        vclient=vclient,
        profile=build_fake_profile(),
        **kw,
    )
    return surface, mqtt, paho, vclient, clock


def _runner(surface, mqtt, vclient, clock, stop):
    """Runner REEL, avec publieur reel, partageant l'unique client MQTT."""
    publisher = ReadSurfacePublisher(
        mqtt=mqtt,
        clock=clock,
        connection=ConnectionState(),
        reader=vclient,
        specs=(SPEC,),
        config=ReadSurfaceConfig(),
    )
    return ReadSurfaceRunner(
        publisher=publisher, clock=clock, stop=stop, transaction=surface
    )


def _poll(depot):
    """`poll()` BORNE. Voir `_pomper` pour le motif."""
    return sans_bloquer(depot.poll)


def _admettre(surface):
    """`admettre_un()` BORNE."""
    return sans_bloquer(surface.admettre_un)


def _pomper(runner):
    """Une iteration de pompage, BORNEE.

    Toutes les operations du proprietaire qui interrogent le depot passent par
    `sans_bloquer`. Motif : le depot MUST etre non bloquant (W2 §14.1), et une
    implementation qui attendrait ferait GELER la suite au lieu de la faire
    rougir. Une suite qui pend ne prouve rien et immobiliserait l'integration
    continue ; ces enveloppes transforment le gel en echec observable.
    """
    return sans_bloquer(runner._pomper)


def _run(runner):
    """`_run(runner)` BORNE, meme motif."""
    return sans_bloquer(runner.run, delai=20.0)


def _acks(paho) -> list:
    """ACK publies, decodes, dans l'ordre."""
    return [
        json.loads(p["payload"].decode("utf-8"))
        for p in paho.published
        if p["topic"].startswith(CONFIG.ack_topic_prefix)
    ]


# ---------------------------------------------------------------------------
# A. Depot inter-fils — W2 §14, §16
# ---------------------------------------------------------------------------


def test_le_depot_refuse_une_capacite_non_positive() -> None:
    for mauvais in (0, -1):
        with pytest.raises(ValueError):
            CommandIntake(mauvais)


def test_le_depot_refuse_une_capacite_non_entiere() -> None:
    with pytest.raises(ValueError):
        CommandIntake(True)  # type: ignore[arg-type]


def test_le_depot_rend_les_messages_en_fifo() -> None:
    depot = CommandIntake(4)
    for n in (1, 2, 3):
        assert depot.offer(message(rid(n))) is True
    rendus = [_poll(depot), _poll(depot), _poll(depot)]
    assert [json.loads(m.payload)["request_id"] for m in rendus] == [
        rid(1),
        rid(2),
        rid(3),
    ]
    assert _poll(depot) is None


def test_poll_sur_depot_vide_ne_bloque_jamais() -> None:
    """W2 §12 : le proprietaire ne doit jamais attendre sur un depot vide.

    La preuve porte sur le MODE d'appel, pas sur une duree. Chronometrer
    distinguerait mal un `get()` reellement bloquant d'un `get(timeout=0.01)`
    sans devenir instable ; observer l'argument `block` les tue tous les deux,
    de facon deterministe et sans le moindre `sleep`.

    `sans_bloquer` garde en outre le cas extreme : un `get()` sans delai ferait
    ECHOUER ce test au lieu de le geler.
    """
    depot = CommandIntake(4)
    appels: list = []
    get_reel = depot._file.get

    def get_espionne(*args, **kwargs):
        appels.append((args, kwargs))
        return get_reel(*args, **kwargs)

    depot._file.get = get_espionne  # type: ignore[method-assign]

    assert sans_bloquer(depot.poll) is None

    assert len(appels) == 1, "poll() doit interroger la file exactement une fois"
    args, kwargs = appels[0]
    bloquant = kwargs.get("block", args[0] if args else True)
    assert bloquant is False, "poll() attend sur un depot vide"
    assert kwargs.get("timeout") is None, "poll() s'accorde un delai d'attente"
    assert len(args) < 2, f"un delai a ete passe positionnellement : {args!r}"


def test_poll_sur_depot_non_vide_reste_non_bloquant() -> None:
    """La meme garantie tient quand un message est disponible."""
    depot = CommandIntake(4)
    depot.offer(message(rid(1)))
    appels: list = []
    get_reel = depot._file.get

    def get_espionne(*args, **kwargs):
        appels.append((args, kwargs))
        return get_reel(*args, **kwargs)

    depot._file.get = get_espionne  # type: ignore[method-assign]

    assert sans_bloquer(depot.poll) is not None
    args, kwargs = appels[0]
    assert kwargs.get("block", args[0] if args else True) is False


def test_le_depot_sature_refuse_sans_bloquer() -> None:
    """W2 §14.1, A-4 : un depot plein rend la main IMMEDIATEMENT.

    Le troisieme depot est tente sur un AUTRE FIL, joint avec un delai borne, et
    son aboutissement est AFFIRME. Un `offer` bloquant ferait donc ECHOUER ce
    test au lieu de le geler : une suite qui pend ne prouve rien et
    immobiliserait l'integration continue.
    """
    depot = CommandIntake(2)
    assert depot.offer(message(rid(1))) is True
    assert depot.offer(message(rid(2))) is True

    assert sans_bloquer(lambda: depot.offer(message(rid(3)))) is False
    assert depot.depth == 2
    assert depot.overflows == 1


def test_le_debordement_est_journalise(caplog) -> None:
    """W2 §16.4 : journalise, et rien d'autre."""
    depot = CommandIntake(1)
    depot.offer(message(rid(1)))
    with caplog.at_level(logging.WARNING, logger="boilerack.command_intake"):
        sans_bloquer(lambda: depot.offer(message(rid(2))))
    assert any("depot de commande sature" in r.getMessage() for r in caplog.records)


def test_le_depot_est_sur_entre_fils() -> None:
    """Depot concurrent depuis plusieurs fils : aucune perte, aucun doublon."""
    depot = CommandIntake(200)
    depart = threading.Barrier(5)

    def deposer(base: int) -> None:
        depart.wait(timeout=5.0)
        for n in range(20):
            depot.offer(message(rid(base * 100 + n)))

    fils = [threading.Thread(target=deposer, args=(i,), daemon=True) for i in range(5)]
    for f in fils:
        f.start()
    for f in fils:
        f.join(timeout=5.0)
        assert not f.is_alive(), "un fil deposant est reste bloque"

    vus = []
    while (m := _poll(depot)) is not None:
        vus.append(json.loads(m.payload)["request_id"])
    assert len(vus) == 100
    assert len(set(vus)) == 100


# ---------------------------------------------------------------------------
# B. Composition — autorites W1, capacite W2 §16.3
# ---------------------------------------------------------------------------


def test_le_topic_de_commande_vient_de_la_configuration() -> None:
    surface, _, paho, _, _ = _surface()
    surface.install()
    assert surface.command_topic == "site/commande"
    assert paho.subscriptions == [("site/commande", COMMAND_QOS)]


def test_le_prefixe_d_ack_vient_de_la_configuration() -> None:
    """W1 §8.3 : la composition transmet l'autorite, elle ne subit pas le defaut."""
    surface, _, paho, _, _ = _surface()
    surface.install()
    surface.intake.offer(message(rid(1), "temp_consigne", 21.0))
    _admettre(surface)
    topics = [p["topic"] for p in paho.published]
    assert topics == ["site/acquittement/temp_consigne"]
    # Le defaut de bibliotheque du coeur ne doit apparaitre nulle part.
    assert not any(t.startswith("boilerack/ack") for t in topics)


def test_la_capacite_du_depot_egale_celle_du_coeur_par_defaut() -> None:
    surface, _, _, _, _ = _surface()
    assert surface.intake.capacity == DEFAULT_QUEUE_CAPACITY


def test_la_capacite_du_depot_ne_peut_etre_inferieure_a_celle_du_coeur() -> None:
    """W2 §16.3 : le plancher est verifie la ou les deux valeurs sont connues."""
    with pytest.raises(ValueError, match="16.3"):
        _surface(queue_capacity=8, intake_capacity=7)


def test_la_capacite_du_depot_peut_etre_superieure() -> None:
    surface, _, _, _, _ = _surface(queue_capacity=8, intake_capacity=32)
    assert surface.intake.capacity == 32


# ---------------------------------------------------------------------------
# C. Installation — W2 §18.3, W1 §7.2, W0
# ---------------------------------------------------------------------------


def test_le_gestionnaire_est_installe_avant_connect() -> None:
    """W2 §18.3, prouve par OBSERVATION a l'instant precis du `connect()`."""
    surface, mqtt, paho, vclient, clock = _surface(lectures={"get_sonde": 20.0})
    runner = _runner(surface, mqtt, vclient, clock, StopArme(arme=True))
    _run(runner)
    assert paho.handler_present_au_connect is True


def test_la_souscription_est_demandee_avant_connect() -> None:
    """W0 enregistre l'intention inconditionnellement ; l'ordre reste prouve."""
    surface, mqtt, paho, vclient, clock = _surface(lectures={"get_sonde": 20.0})
    runner = _runner(surface, mqtt, vclient, clock, StopArme(arme=True))
    _run(runner)
    assert paho.souscriptions_au_connect == (("site/commande", COMMAND_QOS),)


def test_une_seule_souscription_en_qos_1() -> None:
    """W1 §7.2 et §7.3 : une fois, ce seul topic, QoS 1 EXPLICITE."""
    surface, _, paho, _, _ = _surface()
    surface.install()
    assert paho.subscriptions == [("site/commande", 1)]
    assert COMMAND_QOS == 1


def test_aucun_joker_dans_le_topic_souscrit() -> None:
    surface, _, paho, _, _ = _surface()
    surface.install()
    (topic, _qos), = paho.subscriptions
    assert "+" not in topic and "#" not in topic


def test_double_installation_refusee() -> None:
    surface, _, _, _, _ = _surface()
    surface.install()
    with pytest.raises(RuntimeError):
        surface.install()


def test_la_souscription_est_restauree_apres_reconnexion() -> None:
    """W0 : la couture W3 ne duplique aucune logique de reconnexion."""
    surface, _, paho, _, _ = _surface()
    surface.install()
    paho.subscriptions.clear()
    paho.fire_on_connect(success=True)
    assert paho.subscriptions == [("site/commande", COMMAND_QOS)]


def test_un_connack_refuse_ne_restaure_rien() -> None:
    surface, _, paho, _, _ = _surface()
    surface.install()
    paho.subscriptions.clear()
    paho.fire_on_connect(success=False)
    assert paho.subscriptions == []


# ---------------------------------------------------------------------------
# D. Contexte de rappel — W2 §12, §14
# ---------------------------------------------------------------------------


def test_le_rappel_depose_et_n_admet_pas() -> None:
    """W2 §14.1 : le fil Paho depose, et rien de plus."""
    surface, _, paho, vclient, _ = _surface()
    surface.install()
    paho.published.clear()

    paho.fire_on_message(paho_message(rid(1)))

    assert surface.intake.depth == 1  # depose
    assert surface.core.queue_depth == 0  # PAS admis
    assert surface.core.in_flight_count == 0
    assert paho.published == []  # aucun ACK depuis le fil de rappel
    assert vclient.appels == []  # aucun acces vclient depuis le fil de rappel


def test_le_rappel_ne_bloque_pas_a_saturation() -> None:
    """W2 §6 fait 5 : un rappel bloquant gelerait le keepalive."""
    surface, _, paho, _, _ = _surface(queue_capacity=2, intake_capacity=2)
    surface.install()
    for n in range(5):
        # Le rappel DOIT rendre la main, sature ou non (W2 §6 fait 5).
        sans_bloquer(lambda n=n: paho.fire_on_message(paho_message(rid(n + 1))))
    assert surface.intake.depth == 2
    assert surface.intake.overflows == 3
    assert surface.core.queue_depth == 0


def test_le_debordement_ne_produit_aucun_acquittement() -> None:
    surface, _, paho, _, _ = _surface(queue_capacity=1, intake_capacity=1)
    surface.install()
    paho.published.clear()
    for n in range(4):
        sans_bloquer(lambda n=n: paho.fire_on_message(paho_message(rid(n + 1))))
    assert _acks(paho) == []


def test_le_cablage_n_utilise_pas_attach() -> None:
    """W2 §12.1.2 : `attach()` cablerait `submit` sur le fil de rappel."""
    import boilerack.transaction_wiring as module

    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
    arbre = ast.parse(source)
    appels = {
        n.func.attr
        for n in ast.walk(arbre)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    assert "attach" not in appels


def test_le_gestionnaire_installe_n_est_pas_submit() -> None:
    surface, mqtt, _, _, _ = _surface()
    surface.install()
    assert mqtt._handler is not surface.core.submit
    assert mqtt._handler == surface._deposer


# ---------------------------------------------------------------------------
# E. Cadence et ordre d'iteration — W2 §13
# ---------------------------------------------------------------------------


class _Journal:
    """Trace l'ordre reel des operations du proprietaire."""

    def __init__(self) -> None:
        self.evenements: list = []


def _instrumenter(runner, surface, journal) -> None:
    """Enveloppe les trois operations de l'iteration, sans changer leur effet."""
    publieur = runner.publisher
    run_due_reel = publieur.run_due
    admettre_reel = surface.admettre_un
    executer_reel = surface.executer_un

    def run_due():
        journal.evenements.append("run_due")
        return run_due_reel()

    def admettre():
        resultat = admettre_reel()
        journal.evenements.append(f"admission={resultat}")
        return resultat

    def executer():
        journal.evenements.append("process_next")
        return executer_reel()

    publieur.run_due = run_due  # type: ignore[method-assign]
    surface.admettre_un = admettre  # type: ignore[method-assign]
    surface.executer_un = executer  # type: ignore[method-assign]


def test_ordre_run_due_puis_admission_puis_process_next() -> None:
    """W2 §13.3 : l'ordre d'iteration est normatif."""
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    stop = StopArme()
    runner = _runner(surface, mqtt, vclient, clock, stop)
    journal = _Journal()
    _instrumenter(runner, surface, journal)

    surface.install()
    runner.publisher.start()
    surface.intake.offer(message(rid(1)))
    # Une seule iteration, pilotee directement, dans l'ordre du contrat.
    runner.publisher.run_due()
    _pomper(runner)

    assert journal.evenements == ["run_due", "admission=True", "process_next"]


def test_ordre_dans_la_vraie_boucle_du_runner() -> None:
    """W2 §13.3 : l'ordre est prouve dans `run()`, pas seulement a la main.

    Le test precedent pilote les trois operations lui-meme ; il ne pourrait donc
    pas voir un `_boucler` qui les enchainerait dans le mauvais ordre. Celui-ci
    execute la boucle REELLE, sur exactement une iteration.
    """
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    # Trois consultations d'arret par iteration : la quatrieme sort de la boucle.
    stop = StopApres(3)
    runner = _runner(surface, mqtt, vclient, clock, stop)
    journal = _Journal()
    _instrumenter(runner, surface, journal)
    surface.intake.offer(message(rid(1)))

    _run(runner)

    assert journal.evenements == ["run_due", "admission=True", "process_next"]
    assert [a["status"] for a in _acks(paho)] == [
        AckStatus.ACCEPTED.value,
        AckStatus.APPLIED.value,
    ]


def test_au_plus_une_admission_par_iteration() -> None:
    """W2 §13.1 : une rafale ne fait pas admettre plus d'un message par tour."""
    surface, _, _, _, _ = _surface()
    surface.install()
    for n in range(5):
        surface.intake.offer(message(rid(n + 1)))

    assert _admettre(surface) is True
    assert surface.core.queue_depth == 1
    assert surface.intake.depth == 4  # les quatre autres attendent leur tour


def test_admettre_sur_depot_vide_ne_fait_rien() -> None:
    """« Au plus une » n'est jamais « exactement une »."""
    surface, _, paho, _, _ = _surface()
    surface.install()
    paho.published.clear()
    assert _admettre(surface) is False
    assert surface.core.queue_depth == 0
    assert _acks(paho) == []


def test_executer_sur_file_vide_ne_fait_rien() -> None:
    surface, _, _, vclient, _ = _surface()
    surface.install()
    surface.executer_un()
    assert vclient.appels == []


def test_la_profondeur_du_coeur_revient_a_zero_apres_chaque_iteration() -> None:
    """W2 §13.1 : la file du coeur ne diverge pas — exposition bornee a 1."""
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    surface.install()
    for n in range(4):
        surface.intake.offer(message(rid(n + 1), "temp_consigne", 21.0))

    profondeurs = []
    for _ in range(4):
        _admettre(surface)
        profondeurs.append(surface.core.queue_depth)
        surface.executer_un()
        profondeurs.append(surface.core.queue_depth)

    # Apres chaque admission : 1. Apres chaque execution : 0.
    assert profondeurs == [1, 0, 1, 0, 1, 0, 1, 0]
    assert surface.core.queue_depth == 0


def test_la_voie_transactionnelle_est_reservee_aux_mots_cles() -> None:
    """La dependance transactionnelle ne peut pas etre fournie par position.

    C9 avait verrouille la signature du runner ; W3 y ajoute une couture. Elle
    doit rester **reservee aux mots-cles**, pour que l'ordre des parametres
    historiques ne devienne jamais porteur de sens nouveau et qu'aucun appel ne
    puisse l'injecter par megarde.
    """
    parametres = inspect.signature(ReadSurfaceRunner.__init__).parameters
    assert parametres["transaction"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parametres["transaction"].default is None
    # Les trois dependances historiques restent positionnelles, dans l'ordre.
    positionnels = [
        nom
        for nom, p in parametres.items()
        if p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]
    assert positionnels == ["self", "publisher", "clock", "stop"]


def test_une_voie_fournie_par_position_est_refusee() -> None:
    """Preuve d'execution, complementaire de l'inspection de signature."""
    surface, mqtt, paho, vclient, clock = _surface()
    publisher = ReadSurfacePublisher(
        mqtt=mqtt,
        clock=clock,
        connection=ConnectionState(),
        reader=vclient,
        specs=(SPEC,),
        config=ReadSurfaceConfig(),
    )
    with pytest.raises(TypeError):
        ReadSurfaceRunner(publisher, clock, StopArme(), surface)  # type: ignore[misc]


def test_sans_voie_transactionnelle_la_boucle_reste_celle_de_c8() -> None:
    """Regression : `transaction=None` laisse le runner strictement inchange."""
    paho = PahoDouble()
    mqtt = PahoMqttClient(CONFIG, client=paho)
    paho.adaptateur = mqtt
    clock = VirtualClock(DEBUT)
    vclient = VClientEnregistreur({"get_sonde": 20.0})
    publisher = ReadSurfacePublisher(
        mqtt=mqtt,
        clock=clock,
        connection=ConnectionState(),
        reader=vclient,
        specs=(SPEC,),
        config=ReadSurfaceConfig(),
    )
    runner = ReadSurfaceRunner(publisher=publisher, clock=clock, stop=StopArme(True))
    _run(runner)
    assert runner.transaction is None
    assert paho.subscriptions == []  # aucune souscription de commande
    assert paho.handler_present_au_connect is False


# ---------------------------------------------------------------------------
# F. Arret — W2 §19
# ---------------------------------------------------------------------------


def test_arret_demande_n_admet_plus_rien() -> None:
    """W2 §19.3.1 : plus aucune admission apres la demande d'arret."""
    surface, mqtt, paho, vclient, clock = _surface(lectures={"get_sonde": 20.0})
    stop = StopArme(arme=True)
    runner = _runner(surface, mqtt, vclient, clock, stop)
    surface.install()
    surface.intake.offer(message(rid(1)))
    paho.published.clear()

    _pomper(runner)

    assert surface.core.queue_depth == 0
    assert surface.intake.depth == 1  # depose, jamais admis
    assert _acks(paho) == []  # etat B : aucun ACK


def test_arret_apres_admission_execute_la_transaction_de_l_iteration() -> None:
    """W2 §19.3.2 : la commande admise dans l'iteration y est executee."""
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    stop = StopArme(arme=False)
    runner = _runner(surface, mqtt, vclient, clock, stop)
    surface.install()
    surface.intake.offer(message(rid(1)))
    paho.published.clear()

    # L'arret survient PENDANT l'iteration, entre l'admission et l'execution.
    def arreter(quoi, command, value):
        if quoi == "write":
            stop.arme = True

    vclient.pendant = arreter
    _pomper(runner)

    statuts = [a["status"] for a in _acks(paho)]
    assert statuts == [AckStatus.ACCEPTED.value, AckStatus.APPLIED.value]
    assert surface.core.queue_depth == 0


def test_arret_entre_admission_et_execution_execute_quand_meme() -> None:
    """W2 §19.3.2 : l'arret survient EXACTEMENT entre les deux operations.

    Il est arme au moment ou `accepted` est publie, c'est-a-dire a la fin de
    l'admission et avant `process_next()`. Un cablage qui subordonnerait
    l'execution a l'arret laisserait ici un `accepted` orphelin.
    """
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    stop = StopArme(arme=False)
    runner = _runner(surface, mqtt, vclient, clock, stop)
    surface.install()
    surface.intake.offer(message(rid(1)))
    paho.published.clear()

    publier_reel = paho.publish

    def publier(topic, payload, qos=0, retain=False):
        info = publier_reel(topic, payload, qos=qos, retain=retain)
        if topic.startswith(CONFIG.ack_topic_prefix):
            stop.arme = True
        return info

    paho.publish = publier  # type: ignore[method-assign]
    _pomper(runner)

    assert [a["status"] for a in _acks(paho)] == [
        AckStatus.ACCEPTED.value,
        AckStatus.APPLIED.value,
    ], "une commande admise a ete abandonnee au lieu d'etre executee"
    assert surface.core.in_flight_count == 0


def test_aucun_drain_au_shutdown() -> None:
    """W2 §19.5, §21 : jamais de `drain()`, ni en nominal ni a l'arret."""
    import boilerack.runtime as runtime_module
    import boilerack.transaction_wiring as wiring_module

    for module in (runtime_module, wiring_module):
        source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
        appels = {
            n.func.attr
            for n in ast.walk(ast.parse(source))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        }
        assert "drain" not in appels, module.__name__


def test_une_seule_execution_par_iteration_meme_avec_plusieurs_admises() -> None:
    """Le pompage n'appelle `process_next` qu'une fois : pas de drainage cache."""
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    runner = _runner(surface, mqtt, vclient, clock, StopArme())
    surface.install()
    # Deux commandes admises « a la main », comme si une cadence fautive avait eu lieu.
    surface.core.submit(message(rid(1)))
    surface.core.submit(message(rid(2)))
    assert surface.core.queue_depth == 2

    _pomper(runner)

    # Une seule a ete executee : la profondeur ne tombe pas a zero.
    assert surface.core.queue_depth == 1
    assert len(vclient.ecritures) == 1


# ---------------------------------------------------------------------------
# G. Bout en bout hors terrain
# ---------------------------------------------------------------------------


def test_e2e_accepted_puis_applied() -> None:
    """Chaine complete : rappel Paho -> depot -> admission -> execution -> ACK."""
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    runner = _runner(surface, mqtt, vclient, clock, StopArme())
    surface.install()
    runner.publisher.start()
    paho.published.clear()

    # Le message entre par le VRAI chemin : callback de l'adaptateur reel.
    paho.fire_on_message(paho_message(rid(1), "temp_consigne", 21.0))
    assert surface.core.queue_depth == 0  # rien n'est admis sur le fil de rappel

    runner.publisher.run_due()
    _pomper(runner)

    acks = _acks(paho)
    assert [a["status"] for a in acks] == [
        AckStatus.ACCEPTED.value,
        AckStatus.APPLIED.value,
    ]
    assert {a["request_id"] for a in acks} == {rid(1)}
    assert vclient.ecritures == (("write", "set_temp_consigne", 21.0),)
    assert surface.core.in_flight_count == 0


def test_e2e_verdict_terminal_rejete() -> None:
    """Un role inconnu du profil produit un terminal C3, sans aucune ecriture."""
    surface, mqtt, paho, vclient, clock = _surface(lectures={"get_sonde": 20.0})
    runner = _runner(surface, mqtt, vclient, clock, StopArme())
    surface.install()
    paho.published.clear()

    paho.fire_on_message(paho_message(rid(2), "role_inconnu", 21.0))
    _pomper(runner)

    acks = _acks(paho)
    assert [a["status"] for a in acks] == [AckStatus.REJECTED.value]
    assert acks[0]["reason"] == Reason.UNSUPPORTED_ROLE.value
    assert vclient.ecritures == ()


def test_e2e_commande_expiree_rejetee_sans_ecriture() -> None:
    surface, mqtt, paho, vclient, clock = _surface(lectures={"get_sonde": 20.0})
    runner = _runner(surface, mqtt, vclient, clock, StopArme())
    surface.install()
    paho.published.clear()

    paho.fire_on_message(paho_message(rid(3), "temp_consigne", 21.0, ttl_s=-1.0))
    _pomper(runner)

    acks = _acks(paho)
    assert [a["status"] for a in acks] == [AckStatus.REJECTED.value]
    assert acks[0]["reason"] == Reason.EXPIRED.value
    assert vclient.ecritures == ()


def test_aucune_operation_vclient_simultanee() -> None:
    """W2 §15.2 : lecture de telemetrie et ecriture partagent le proprietaire."""
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    runner = _runner(surface, mqtt, vclient, clock, StopArme())
    surface.install()
    runner.publisher.start()
    paho.fire_on_message(paho_message(rid(1), "temp_consigne", 21.0))

    runner.publisher.run_due()
    _pomper(runner)

    assert vclient.recouvrements == 0
    # L'ordre est celui du contrat : telemetrie d'abord, transaction ensuite.
    assert vclient.appels[0] == ("read", "get_sonde", None)
    assert ("write", "set_temp_consigne", 21.0) in vclient.appels


def test_une_lecture_concurrente_pendant_une_ecriture_serait_detectee() -> None:
    """Le detecteur de recouvrement n'est pas vacant : il sait echouer."""
    vclient = VClientEnregistreur({"get_sonde": 1.0})

    def intrusion(quoi, command, value):
        if quoi == "write":
            vclient.read("get_sonde")

    vclient.pendant = intrusion
    with pytest.raises(OperationVClientSimultanee):
        vclient.write("set_temp_consigne", 21.0)


def test_coupure_mqtt_ne_modifie_pas_le_verdict_metier() -> None:
    """W2 §24 : le verdict depend de `vclient`, jamais du transport."""
    surface, mqtt, paho, vclient, clock = _surface(
        lectures={"get_sonde": 20.0, "get_temp_consigne": 21.0}
    )
    _runner(surface, mqtt, vclient, clock, StopArme())
    surface.install()
    paho.fire_on_message(paho_message(rid(1), "temp_consigne", 21.0))
    _admettre(surface)

    # La connexion tombe APRES `accepted`, AVANT le verdict terminal.
    paho.fire_on_disconnect(reason=1)
    paho.publish_rc = 1  # toute publication ulterieure echoue
    paho.published.clear()

    surface.executer_un()

    # L'ecriture a bien eu lieu, et le verdict est en cache malgre l'echec MQTT.
    assert vclient.ecritures == (("write", "set_temp_consigne", 21.0),)
    assert surface.core.in_flight_count == 0
    assert surface.core.terminal_cache_size >= 1


# ---------------------------------------------------------------------------
# H. Frontiere W4 — ce qui reste fermé
# ---------------------------------------------------------------------------


def test_la_racine_de_composition_ne_construit_aucune_voie(monkeypatch) -> None:
    """`build_runtime` ne peut pas composer la voie, et ne l'essaie pas."""
    from boilerack.adapters.config import VclientConfig
    from boilerack.runtime import NeverStop, RuntimeConfig, build_runtime

    monkeypatch.setattr(
        PahoMqttClient, "_build_client", staticmethod(lambda config: PahoDouble())
    )
    runtime = build_runtime(
        RuntimeConfig(mqtt=CONFIG, vclient=VclientConfig(executable="x", host="h")),
        NeverStop(),
    )
    assert runtime.transaction is None
    assert runtime.runner.transaction is None


def test_l_adaptateur_vclient_reel_ne_sait_pas_ecrire() -> None:
    """Barriere W4 n° 1 — LEVEE par W4-B, et remplacee par une liste fermee.

    Jusqu'a W4-B, aucun adaptateur ne savait ecrire, et c'etait la derniere des
    deux dependances qui fermaient la production. W4-B en livre un : la barriere
    n° 1 ne tient plus, et le pretendre serait faux.

    Deux choses restent verifiables, et le restent ici.

    D'abord, le LECTEUR n'a pas change : il n'ecrit toujours pas, et ne satisfait
    toujours pas `VClient` a lui seul. W4-B l'a etendu par heritage sans le
    toucher.

    Ensuite, les types qui satisfont `VClient` forment une liste FERMEE. Un
    troisieme apparaissant sans lot dedie fait echouer ce test.

    La fermeture de la production ne repose donc PLUS sur une dependance
    absente : les deux existent. Elle repose entierement sur le fait que RIEN ne
    les compose — ce que prouvent
    `test_la_surface_n_est_construite_nulle_part_en_production`,
    `test_la_racine_de_composition_ne_construit_aucune_voie` et les barrieres de
    `tests/adapters/test_vclient_write.py`.
    """
    from boilerack.adapters.vclient_cli import VClientCliReader
    from boilerack.adapters.vclient_write import VClientCli
    from boilerack.transport.vclient import VClient

    assert hasattr(VClientCliReader, "read")
    assert not hasattr(VClientCliReader, "write")

    # Implementations de `write` dans la couche ADAPTATEURS. Le scan reste borne
    # a `adapters/` comme avant W4-B : `transport/vclient.py` y DECLARE `write`
    # dans le Protocol, et une declaration n'est pas une implementation.
    racine = pathlib.Path(__file__).resolve().parents[1] / "src" / "boilerack"
    ecrivains = []
    for fichier in (racine / "adapters").rglob("*.py"):
        if "__pycache__" in fichier.parts:
            continue
        for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
            if isinstance(noeud, ast.FunctionDef) and noeud.name == "write":
                ecrivains.append(fichier.name)
    assert sorted(ecrivains) == ["vclient_write.py"]

    # L'unique ecrivain etend le lecteur au lieu de le dupliquer, et satisfait
    # enfin `VClient` — ce que le lecteur seul ne fait toujours pas.
    assert issubclass(VClientCli, VClientCliReader)
    assert issubclass(VClientCli, VClient) is True
    assert issubclass(VClientCliReader, VClient) is False


def test_les_constructeurs_de_profil_sont_une_liste_fermee() -> None:
    """Barriere W4 n° 2 — LEVEE par W4-D, remplacee par une liste fermee.

    Jusqu'a W4-D, aucun `Profile` reel n'existait, et c'etait la seconde des deux
    dependances qui fermaient la production. W4-D en livre un : la barriere n° 2
    ne tient donc plus, et le pretendre serait faux.

    Ce qui reste verifiable, et le reste ici : les constructeurs de `Profile`
    forment une liste FERMEE. Un troisieme apparaissant sans lot dedie fait
    echouer ce test.

    La fermeture de la production repose desormais sur la SEULE barriere n° 1 —
    aucun adaptateur d'ecriture reel — et sur le fait qu'aucun module de
    production n'appelle la fabrique (`tests/core/test_production_profile.py`).
    """
    racine = pathlib.Path(__file__).resolve().parents[1] / "src" / "boilerack"
    constructeurs = []
    for fichier in racine.rglob("*.py"):
        if "__pycache__" in fichier.parts:
            continue
        for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
            if (
                isinstance(noeud, ast.Call)
                and isinstance(noeud.func, ast.Name)
                and noeud.func.id == "Profile"
            ):
                constructeurs.append(fichier.relative_to(racine).as_posix())
    assert sorted(constructeurs) == [
        "core/production_profile.py",
        "testing/fake_profile.py",
    ]


def test_aucun_double_de_test_importe_par_le_code_de_production() -> None:
    """Aucun module de production n'IMPORTE `boilerack.testing`.

    La preuve porte sur les imports reels, releves par AST : une mention en
    commentaire ou en docstring — `clock.py` cite `VirtualClock` pour expliquer
    sa propre couture — n'est pas une dependance.
    """
    racine = pathlib.Path(__file__).resolve().parents[1] / "src" / "boilerack"
    fautifs = []
    for fichier in racine.rglob("*.py"):
        if "__pycache__" in fichier.parts or "testing" in fichier.parts:
            continue
        for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
            cible = None
            if isinstance(noeud, ast.Import):
                cible = " ".join(a.name for a in noeud.names)
            elif isinstance(noeud, ast.ImportFrom) and noeud.module:
                cible = noeud.module
            if cible and "boilerack.testing" in cible:
                fautifs.append(fichier.relative_to(racine).as_posix())
    assert fautifs == []


def test_aucune_ecriture_vclient_reelle_dans_le_code_de_production() -> None:
    """Aucun nom de commande d'ecriture FICTIF ne sort de `testing/`.

    Ce test portait aussi, jusqu'a W4-B, sur l'absence de toute definition de
    `write` dans la couche adaptateurs. W4-B en livre une : ce volet a donc
    migre vers `test_l_adaptateur_vclient_reel_ne_sait_pas_ecrire`, ou il est
    devenu une liste fermee au lieu d'une absence.

    Depuis W4-D, un nom de commande d'ecriture REEL existe egalement en
    production — `setNiveauM1`, dans le profil. Ce qui reste interdit hors de
    `testing/`, ce sont les noms FICTIFS du double : les y trouver signalerait
    qu'un test a fui dans le produit.
    """
    racine = pathlib.Path(__file__).resolve().parents[1] / "src" / "boilerack"
    for fichier in racine.rglob("*.py"):
        if "__pycache__" in fichier.parts or "testing" in fichier.parts:
            continue
        source = fichier.read_text(encoding="utf-8")
        for interdit in ("setTempConsigne", "set_temp_consigne", "set_mode"):
            assert interdit not in source, f"{fichier.name} : {interdit}"


def test_la_surface_exige_les_deux_dependances_de_w4() -> None:
    """La barriere est un TYPE : `vclient` et `profile` sont obligatoires."""
    parametres = inspect.signature(build_transaction_surface).parameters
    for obligatoire in ("mqtt", "clock", "config", "vclient", "profile"):
        assert parametres[obligatoire].default is inspect.Parameter.empty
        assert parametres[obligatoire].kind is inspect.Parameter.KEYWORD_ONLY


def test_la_surface_n_est_composee_que_par_lifecycle() -> None:
    """Barriere W3 « aucune composition » — REMPLACEE par une liste FERMEE.

    Jusqu'a W4-E2, aucun module de production n'appelait
    `build_transaction_surface`, et c'etait la garantie de fermeture. W4-E1 §11
    prescrit son remplacement : la composition existe desormais, mais un seul
    lieu a le droit de la DECIDER.

    La preuve porte sur des APPELS releves par AST — une definition et un import
    n'en sont pas — et sur la liste fermee de leurs sites. Un second appelant
    fait echouer ce test.

    Ce que cette barriere ne dit plus, et qui est porte ailleurs : que la
    composition n'a lieu QUE sous autorite. Deux tests de
    `tests/test_lifecycle.py` l'etablissent sur la couture reelle
    `run_lifecycle` -> `build_runtime` —
    `test_le_cycle_de_vie_ne_transmet_aucune_fabrique_si_l_autorite_est_fermee`
    et `test_le_cycle_de_vie_transmet_une_fabrique_si_l_autorite_est_ouverte`.
    Le cas OUVERT est le necessaire : le cas ferme seul serait satisfait par une
    couture supprimee.
    """
    racine = pathlib.Path(__file__).resolve().parents[1] / "src" / "boilerack"
    appelants = []
    for fichier in racine.rglob("*.py"):
        if "__pycache__" in fichier.parts:
            continue
        arbre = ast.parse(fichier.read_text(encoding="utf-8"))
        alias: dict[str, str] = {}
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.ImportFrom):
                for nom in noeud.names:
                    alias[nom.asname or nom.name] = nom.name
        for noeud in ast.walk(arbre):
            if not isinstance(noeud, ast.Call):
                continue
            cible = noeud.func
            nom = None
            if isinstance(cible, ast.Name):
                nom = alias.get(cible.id, cible.id)
            elif isinstance(cible, ast.Attribute):
                nom = cible.attr
            if nom == "build_transaction_surface":
                appelants.append(fichier.relative_to(racine).as_posix())
    assert sorted(appelants) == ["lifecycle.py"]


def test_aucun_second_client_mqtt() -> None:
    """W1 §7.5 : la voie partage l'instance construite par la racine."""
    surface, mqtt, _, _, _ = _surface()
    assert surface._mqtt is mqtt
    assert surface.core._mqtt is mqtt

    racine = pathlib.Path(__file__).resolve().parents[1] / "src" / "boilerack"
    constructions = []
    for fichier in racine.rglob("*.py"):
        if "__pycache__" in fichier.parts:
            continue
        source = fichier.read_text(encoding="utf-8")
        constructions += [fichier.name] * source.count("PahoMqttClient(")
    # Une seule construction dans tout le code de production : `build_runtime`.
    assert constructions == ["runtime.py"]


def test_l_import_du_runtime_ne_charge_pas_la_voie_transactionnelle() -> None:
    """Le runtime de production reste en lecture seule, jusque dans ses imports.

    `TransactionSurface` n'apparait dans `runtime.py` que dans des annotations.
    L'importer au niveau global chargerait `transaction_wiring`, donc le coeur
    transactionnel et son transport, pour un processus qui n'en execute rien.

    La mesure est faite dans un interpreteur NEUF : la session de test a deja
    importe ces modules, et interroger `sys.modules` ici ne prouverait rien.
    Aucun reseau, aucun broker : seul un interpreteur Python est lance.
    """
    import subprocess
    import sys

    code = (
        "import sys; import boilerack.runtime; "
        "print('transaction_wiring' if 'boilerack.transaction_wiring' in sys.modules "
        "else '-', 'core.engine' if 'boilerack.core.engine' in sys.modules else '-')"
    )
    issue = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert issue.returncode == 0, issue.stderr
    assert issue.stdout.split() == ["-", "-"], (
        f"l'import de boilerack.runtime charge encore : {issue.stdout.strip()}"
    )


def test_l_import_de_transaction_surface_est_reserve_au_typage() -> None:
    """Preuve statique, complementaire de la mesure en interpreteur neuf."""
    import boilerack.runtime as module

    arbre = ast.parse(pathlib.Path(module.__file__).read_text(encoding="utf-8"))
    au_niveau_module, sous_type_checking = [], []
    for noeud in arbre.body:
        if isinstance(noeud, ast.ImportFrom) and noeud.module == "boilerack.transaction_wiring":
            au_niveau_module.append(noeud.module)
        if isinstance(noeud, ast.If) and getattr(noeud.test, "id", None) == "TYPE_CHECKING":
            for interne in noeud.body:
                if isinstance(interne, ast.ImportFrom):
                    sous_type_checking.append(interne.module)
    assert au_niveau_module == [], "import transactionnel au niveau module"
    assert "boilerack.transaction_wiring" in sous_type_checking


def test_aucun_statut_ni_reason_nouveau() -> None:
    """W2 §23 : la taxonomie C3 n'est ni etendue ni contournee."""
    import boilerack.command_intake as intake_module
    import boilerack.transaction_wiring as wiring_module

    for module in (intake_module, wiring_module):
        source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
        assert "class Reason" not in source
        assert "class AckStatus" not in source
        assert "Ack.rejected" not in source
        assert "Ack.accepted" not in source
