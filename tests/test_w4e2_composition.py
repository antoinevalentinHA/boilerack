"""Barrieres normatives du lot W4-E2 — composition sous autorite.

Autorite : `docs/design/w4e-composition-activation.md` §12, references **B1** a
**B19**. Chaque test nomme la barriere qu'il porte ; celles qui pre-existent
sont recensees en fin de fichier, avec leur emplacement, afin que la table §12
reste verifiable d'un seul endroit.

HORS LIGNE, INTEGRALEMENT
    Aucun broker, aucun Pi, aucun `vcontrold`, aucune chaudiere, aucune socket,
    aucun sous-processus, aucune ecriture, aucun `sleep`. Les seuls
    interpreteurs lances le sont par `subprocess` pour les preuves d'import en
    interpreteur NEUF, qui n'executent que `import` et `print`.

CE QUE CE FICHIER NE PROUVE PAS
    Que Boilerack soit l'ecrivain legitime de l'installation. `enabled = true`
    autorise la COMPOSITION de la voie ; la neutralisation de l'ecrivain
    historique appartient a W4-F (§15).
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import pathlib
import subprocess
import sys
import tomllib
from datetime import datetime, timezone

import pytest

from boilerack.adapters.config import MqttConfig, VclientConfig
from boilerack.config import ConfigurationError, load_config
from boilerack.lifecycle import _composer_transaction, _config_mqtt_transactionnelle
from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.topics import InvalidMqttTopic
from boilerack.runtime import (
    NeverStop,
    RuntimeConfig,
    TransactionSurfaceConfig,
    build_runtime,
)
from boilerack.testing import VirtualClock
from boilerack.transaction_wiring import TransactionSurface

from wiring_support import PahoDouble

DEBUT = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

RACINE = pathlib.Path(__file__).resolve().parents[1] / "src" / "boilerack"

#: Configuration minimale valide. `host` MQTT et `executable` sont les deux
#: seules valeurs obligatoires (C10) ; rien ici n'est une valeur de site.
BASE = dict(
    mqtt=MqttConfig(host="broker.test"),
    vclient=VclientConfig(executable="vclient", host="demon.test", port=4242),
)


def config(**kw) -> RuntimeConfig:
    return RuntimeConfig(**{**BASE, **kw})


def ouvert(**kw) -> RuntimeConfig:
    """Configuration dont l'autorite transactionnelle est OUVERTE."""
    return config(transaction_surface=TransactionSurfaceConfig(enabled=True), **kw)


@pytest.fixture
def paho_double(monkeypatch):
    """Neutralise la creation du client Paho reel — aucune socket n'est ouverte.

    `PahoMqttClient` reste la classe REELLE : seule sa fabrique de client bas
    niveau est remplacee. Ce que les tests observent est donc bien l'adaptateur
    de production, cable sur un double a la frontiere deja prevue par C4.
    """
    from boilerack.adapters.mqtt_paho import PahoMqttClient

    doubles: list[PahoDouble] = []

    def fabriquer(config):
        double = PahoDouble()
        doubles.append(double)
        return double

    monkeypatch.setattr(PahoMqttClient, "_build_client", staticmethod(fabriquer))
    return doubles


def toml(texte: str, tmp_path) -> RuntimeConfig:
    """Charge une configuration TOML depuis un fichier temporaire."""
    fichier = tmp_path / "boilerack.toml"
    entete = '[mqtt]\nhost = "broker.test"\n\n[vclient]\nexecutable = "vclient"\n'
    fichier.write_text(entete + texte, encoding="utf-8")
    return load_config(str(fichier))


# ---------------------------------------------------------------------------
# A. Autorite d'activation — B1, B2, B3
# ---------------------------------------------------------------------------


def test_b1_autorite_absente_ne_compose_rien(paho_double) -> None:
    """**B1** — autorite ABSENTE : aucune composition, `transaction is None`.

    « Absente » se lit ici au sens ou l'utilisateur ne l'a pas ecrite : le
    defaut de `RuntimeConfig` s'applique, et il est ferme.
    """
    assert _composer_transaction(config()) is None
    runtime = build_runtime(config(), NeverStop())
    assert runtime.transaction is None
    assert runtime.runner.transaction is None


def test_b2_autorite_fausse_ne_compose_rien(paho_double) -> None:
    """**B2** — autorite explicitement `false` : aucune composition."""
    ferme = config(transaction_surface=TransactionSurfaceConfig(enabled=False))
    assert _composer_transaction(ferme) is None
    runtime = build_runtime(
        ferme, NeverStop(), transaction_factory=_composer_transaction(ferme)
    )
    assert runtime.transaction is None
    assert runtime.runner.transaction is None


def test_b3_autorite_vraie_compose_reellement(paho_double) -> None:
    """**B3** — autorite `true` : `lifecycle` fournit une fabrique, et elle prend.

    Le test parcourt la chaine ENTIERE telle que `run_lifecycle` la parcourt —
    decision dans `lifecycle`, application dans `build_runtime` — sans executer
    le runner ni ouvrir quoi que ce soit.
    """
    fabrique = _composer_transaction(ouvert())
    assert fabrique is not None

    runtime = build_runtime(ouvert(), NeverStop(), transaction_factory=fabrique)
    assert isinstance(runtime.transaction, TransactionSurface)
    # Exposee dans `Runtime`, ET remise au runner : le meme objet, pas deux.
    assert runtime.runner.transaction is runtime.transaction


def test_b3_la_fabrique_recoit_le_client_mqtt_unique(paho_double) -> None:
    """**B3**, **B18** — la surface consomme l'instance de la racine (W1 §7.5).

    Preuve d'IDENTITE, pas de ressemblance : `is`. Une seconde instance
    construite depuis le meme `MqttConfig` porterait le meme `client_id` et
    provoquerait des deconnexions mutuelles en boucle.
    """
    runtime = build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )
    assert runtime.transaction._mqtt is runtime.publisher._mqtt
    assert runtime.transaction.core._mqtt is runtime.publisher._mqtt
    # Un seul client Paho bas niveau a ete fabrique dans tout l'assemblage.
    assert len(paho_double) == 1


def test_b3_la_fabrique_recoit_l_horloge_retenue(paho_double) -> None:
    """**B3** — la surface partage l'horloge de la racine, jamais une autre.

    Deux horloges donneraient deux notions du temps dans un meme processus : la
    peremption des commandes et la fraicheur des mesures divergeraient.
    """
    horloge = VirtualClock(DEBUT)
    runtime = build_runtime(
        ouvert(),
        NeverStop(),
        clock=horloge,
        transaction_factory=_composer_transaction(ouvert()),
    )
    assert runtime.transaction.core._clock is horloge
    assert runtime.runner._clock is horloge


def test_b3_la_fabrique_n_est_appelee_qu_une_fois(paho_double) -> None:
    """**B3**, **B12** — un seul appel, donc une seule surface."""
    appels = []
    reelle = _composer_transaction(ouvert())

    def espionne(mqtt, clock):
        appels.append((mqtt, clock))
        return reelle(mqtt, clock)

    runtime = build_runtime(ouvert(), NeverStop(), transaction_factory=espionne)
    assert len(appels) == 1
    assert runtime.transaction is not None


def test_b3_la_surface_precede_le_runner(paho_double) -> None:
    """**B3** — la surface est creee AVANT le `ReadSurfaceRunner`.

    Deux preuves, et il en faut deux.

    La premiere est comportementale : le runner DETIENT la surface. Un runner
    construit avant elle n'aurait pu recevoir que `None`, et l'identite
    `runner.transaction is transaction` serait fausse.

    La seconde est structurelle, sur le source de `build_runtime` : l'ordre des
    deux constructions est lisible, et une inversion future — qui laisserait la
    premiere preuve verte en passant la surface apres coup par affectation —
    ferait rougir celle-ci.
    """
    runtime = build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )
    assert runtime.runner.transaction is runtime.transaction is not None

    source = inspect.getsource(build_runtime)
    assert source.index("transaction_factory(") < source.index("ReadSurfaceRunner(")


def test_la_racine_ne_decide_pas_meme_sur_autorite_ouverte(paho_double) -> None:
    """**B7** renforce — l'autorite ouverte ne suffit PAS a faire composer la racine.

    `build_runtime` ne consulte jamais `transaction_surface`. Sans fabrique, une
    configuration OUVERTE doit produire exactement le meme resultat qu'une
    configuration fermee : rien. C'est ce qui distingue « appliquer une fabrique
    injectee » de « decider de composer ».

    Preuve comportementale, complementaire de la preuve statique qui suit.
    """
    runtime = build_runtime(ouvert(), NeverStop())
    assert runtime.transaction is None
    assert runtime.runner.transaction is None


#: Seul module autorise a CONSULTER l'autorite d'activation (W4-E1 §6, §7.2).
_LIEU_DE_L_AUTORITE = "lifecycle.py"


def _lecteurs_de_l_autorite(modules) -> list[str]:
    """Modules qui CONSULTENT l'autorite d'activation, c'est-a-dire `.enabled`.

    CONSULTER N'EST PAS DECLARER
        `runtime.py` DECLARE le champ et en valide le TYPE
        (`isinstance(self.transaction_surface, …)`) ; `config.py` le RENSEIGNE
        par argument nomme. Aucun des deux ne lit `.enabled`, et aucun des deux
        ne decide donc quoi que ce soit. La detection porte sur la LECTURE DE LA
        VALEUR, seul geste qui soit une decision.

    TROIS FORMES, PARCE QUE TROIS FORMES EXISTENT
        1. la chaine directe        `config.transaction_surface.enabled`
        2. l'alias en deux temps    `a = config.transaction_surface` puis `a.enabled`
        3. l'acces dynamique        `getattr(config.transaction_surface, "enabled")`

        La deuxieme est celle qui compte : c'est la forme qu'un module tente de
        decider emploierait pour echapper a une detection de chaine, et c'est
        exactement celle que l'audit a signalee.
    """

    def est_l_autorite(noeud, alias) -> bool:
        if isinstance(noeud, ast.Attribute) and noeud.attr == "transaction_surface":
            return True
        return isinstance(noeud, ast.Name) and noeud.id in alias

    lecteurs = []
    for fichier in modules:
        arbre = ast.parse(fichier.read_text(encoding="utf-8"))

        # Noms locaux lies a l'autorite : `autorite = config.transaction_surface`.
        alias: set[str] = set()
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.Assign) and est_l_autorite(noeud.value, set()):
                for cible in noeud.targets:
                    if isinstance(cible, ast.Name):
                        alias.add(cible.id)

        for noeud in ast.walk(arbre):
            lit = False
            if isinstance(noeud, ast.Attribute) and noeud.attr == "enabled":
                lit = est_l_autorite(noeud.value, alias)
            elif (
                isinstance(noeud, ast.Call)
                and isinstance(noeud.func, ast.Name)
                and noeud.func.id == "getattr"
                and len(noeud.args) >= 2
                and isinstance(noeud.args[1], ast.Constant)
                and noeud.args[1].value == "enabled"
            ):
                lit = est_l_autorite(noeud.args[0], alias)
            if lit:
                lecteurs.append(fichier.name)
                break
    return sorted(lecteurs)


def _modules() -> list[pathlib.Path]:
    modules = [f for f in RACINE.rglob("*.py") if "__pycache__" not in f.parts]
    assert modules, f"balayage vide : {RACINE}"
    assert any(f.name == _LIEU_DE_L_AUTORITE for f in modules)
    return modules


def test_seul_lifecycle_consulte_l_autorite_d_activation() -> None:
    """**B4** complete — la liste fermee porte aussi sur le lieu de LECTURE.

    Les barrieres B4 existantes recensent les lieux d'APPEL des quatre symboles
    de composition. Elles ne voyaient pas une forme intermediaire : un module
    qui lirait l'autorite puis DELEGUERAIT la composition a `lifecycle`. Le
    lieu d'appel resterait alors `lifecycle.py`, et la decision aurait pourtant
    migre ailleurs.

    Cette barriere ferme cet interstice : consulter l'autorite est le geste de
    DECIDER, et un seul module y a droit.
    """
    assert _lecteurs_de_l_autorite(_modules()) == [_LIEU_DE_L_AUTORITE]


def test_la_barriere_de_l_autorite_n_est_pas_vacante() -> None:
    """Controle de non-vacuite : `lifecycle.py` lit REELLEMENT l'autorite.

    Sans ce controle, la barriere precedente resterait verte si la lecture
    disparaissait de `lifecycle.py` — c'est-a-dire si l'autorite cessait d'etre
    consultee du tout, ce qui est exactement le defaut que W4-E2 doit exclure.
    """
    lifecycle = (RACINE / "lifecycle.py").read_text(encoding="utf-8")
    chaines = []
    for noeud in ast.walk(ast.parse(lifecycle)):
        if (
            isinstance(noeud, ast.Attribute)
            and noeud.attr == "enabled"
            and isinstance(noeud.value, ast.Attribute)
            and noeud.value.attr == "transaction_surface"
        ):
            chaines.append(noeud)
    assert chaines, "lifecycle.py ne consulte plus l'autorite d'activation"


@pytest.mark.parametrize(
    "forme",
    [
        # Chaine directe.
        "def build_runtime(config, stop):\n"
        "    if config.transaction_surface.enabled:\n"
        "        return composer()\n",
        # En deux temps : une detection de chaine seule serait aveugle.
        "def build_runtime(config, stop):\n"
        "    autorite = config.transaction_surface\n"
        "    if autorite.enabled:\n"
        "        return composer()\n",
        # Par delegation indirecte a `lifecycle`.
        "def build_runtime(config, stop):\n"
        "    from boilerack.lifecycle import _composer_transaction\n"
        "    if getattr(config.transaction_surface, 'enabled', False):\n"
        "        return _composer_transaction(config)(mqtt, clock)\n",
    ],
)
def test_la_barriere_de_l_autorite_voit_une_lecture_deplacee(
    forme: str, tmp_path
) -> None:
    """La barriere rougit-elle vraiment sur une autorite deplacee ?

    Les trois formes sont soumises a un module FICTIF : eprouver la barriere sur
    le depot reel exigerait d'y ecrire un defaut, ce que §13 reserve aux sondes
    jetables. La forme en deux temps est celle qui compte : une detection de la
    seule chaine `…transaction_surface.enabled` la laisserait passer.
    """
    intrus = tmp_path / "runtime.py"
    intrus.write_text(forme, encoding="utf-8")
    assert _lecteurs_de_l_autorite([intrus]) == ["runtime.py"]


# ---------------------------------------------------------------------------
# B. Forme de la configuration — B17 (§14)
# ---------------------------------------------------------------------------


def test_b17_table_absente_donne_ferme(tmp_path) -> None:
    assert toml("", tmp_path).transaction_surface.enabled is False


def test_b17_table_vide_donne_ferme(tmp_path) -> None:
    """La table peut exister sans sa cle : le defaut reste FERME."""
    assert toml("[transaction_surface]\n", tmp_path).transaction_surface.enabled is False


@pytest.mark.parametrize(
    ("litteral", "attendu"), [("false", False), ("true", True)]
)
def test_b17_un_booleen_strict_est_accepte(litteral, attendu, tmp_path) -> None:
    contenu = f"[transaction_surface]\nenabled = {litteral}\n"
    assert toml(contenu, tmp_path).transaction_surface.enabled is attendu


@pytest.mark.parametrize("valeur", ["1", "0", '"true"', '"false"', '"yes"', "1.0"])
def test_b17_aucune_valeur_verite_approchee_n_est_acceptee(valeur, tmp_path) -> None:
    """Booleen STRICT : `1` et `"true"` sont des fautes, jamais des synonymes.

    Accepter `1` reviendrait a deviner l'intention de l'utilisateur sur la seule
    cle qui ouvre une voie d'ecriture. La configuration la plus dangereuse du
    depot est celle qui doit tolerer le moins.
    """
    with pytest.raises(ConfigurationError):
        toml(f"[transaction_surface]\nenabled = {valeur}\n", tmp_path)


def test_b17_une_cle_inconnue_de_la_table_est_refusee(tmp_path) -> None:
    with pytest.raises(ConfigurationError):
        toml("[transaction_surface]\nenabled = true\nforce = true\n", tmp_path)


def test_b17_une_table_inconnue_reste_refusee(tmp_path) -> None:
    """La table nouvelle n'a pas relache le refus general des tables inconnues."""
    with pytest.raises(ConfigurationError):
        toml("[transaction_surfaces]\nenabled = true\n", tmp_path)


def test_b17_la_structure_ne_porte_qu_une_cle() -> None:
    """Surface FERMEE : une seconde cle exigerait un lot, pas un ajout discret."""
    champs = {f.name for f in dataclasses.fields(TransactionSurfaceConfig)}
    assert champs == {"enabled"}
    assert TransactionSurfaceConfig().enabled is False


def test_b17_la_structure_refuse_un_non_booleen_a_la_construction() -> None:
    """La validation ne depend pas du chargeur TOML : elle est dans le type.

    Un appelant programmatique — un test, un futur point d'entree — obtient le
    meme refus que l'utilisateur d'un fichier.
    """
    for mauvais in (1, 0, "true", None, 1.0):
        with pytest.raises(ValueError):
            TransactionSurfaceConfig(enabled=mauvais)  # type: ignore[arg-type]


def test_b17_l_exemple_livre_reste_ferme() -> None:
    """§14 : copier `boilerack.example.toml` donne une installation FERMEE.

    Le fichier est lu tel qu'il est livre. Si sa table venait a etre
    decommentee, la cle devrait rester `false` — les deux etats sont verifies.
    """
    chemin = pathlib.Path(__file__).resolve().parents[1] / "docs" / "boilerack.example.toml"
    texte = chemin.read_text(encoding="utf-8")

    livre = tomllib.loads(texte)
    assert "transaction_surface" not in livre, "l'exemple livre une voie composee"

    decommente = tomllib.loads(
        texte.replace("# [transaction_surface]", "[transaction_surface]").replace(
            "# enabled = false", "enabled = false"
        )
    )
    assert decommente["transaction_surface"] == {"enabled": False}


# ---------------------------------------------------------------------------
# C. Namespace derive — B16, B19 (§8.4)
# ---------------------------------------------------------------------------


#: Defauts de BIBLIOTHEQUE de `MqttConfig`. Legitimes pour qui construit une
#: configuration sans composition ; jamais l'autorite runtime (W1 §8.3).
_DEFAUTS_DE_BIBLIOTHEQUE = ("boilerack/command", "boilerack/ack")


def test_b16_les_topics_derivent_de_la_racine_par_defaut() -> None:
    derive = _config_mqtt_transactionnelle(config())
    assert derive.command_topic == "boiler/command"
    assert derive.ack_topic_prefix == "boiler/ack"


def test_b16_les_topics_suivent_une_racine_imbriquee() -> None:
    """La racine peut comporter plusieurs segments : les quatre sous-arbres suivent."""
    nichee = config(read_surface=ReadSurfaceConfig(prefix="maison/chaudiere"))
    derive = _config_mqtt_transactionnelle(nichee)
    assert derive.command_topic == "maison/chaudiere/command"
    assert derive.ack_topic_prefix == "maison/chaudiere/ack"


def test_b16_aucun_defaut_de_bibliotheque_ne_survit_a_la_composition() -> None:
    """**B16** — la composition n'emploie JAMAIS `boilerack/…`.

    Le cas piege est celui d'une racine litteralement nommee `boilerack` : les
    topics valent alors `boilerack/command` et `boilerack/ack`, mais par
    DERIVATION et non par defaut. Le test verifie donc que la valeur suit la
    racine, ce qu'un defaut fige ne ferait pas.
    """
    for racine in ("boiler", "maison/chaudiere", "boilerack"):
        derive = _config_mqtt_transactionnelle(
            config(read_surface=ReadSurfaceConfig(prefix=racine))
        )
        assert derive.command_topic == f"{racine}/command"
        assert derive.ack_topic_prefix == f"{racine}/ack"

    # Et hors de ce cas nomme, les defauts de bibliotheque n'apparaissent pas.
    derive = _config_mqtt_transactionnelle(config())
    assert derive.command_topic not in _DEFAUTS_DE_BIBLIOTHEQUE
    assert derive.ack_topic_prefix not in _DEFAUTS_DE_BIBLIOTHEQUE


@pytest.mark.parametrize("mauvaise", ["maison/#", "maison/+", ""])
def test_b16_une_racine_mal_formee_est_refusee_par_la_validation_existante(
    mauvaise: str,
) -> None:
    """La derivation reutilise `build_topic` : elle n'invente aucune validation.

    Une racine que la surface de LECTURE refuse doit l'etre ici aussi ; le
    contraire signifierait deux regles de topic dans un meme depot. Les jokers
    sont le cas qui compte : souscrire `maison/#/command` capterait le trafic
    d'installations voisines.
    """
    with pytest.raises(InvalidMqttTopic):
        _config_mqtt_transactionnelle(
            config(read_surface=ReadSurfaceConfig(prefix=mauvaise))
        )


def test_b16_la_normalisation_de_la_racine_est_celle_de_la_lecture() -> None:
    """Et symetriquement : ce que la lecture NORMALISE, la commande normalise.

    `a//b` et `/a/b/` ne sont pas des fautes pour C7 §3.2, qui les ramene a
    `a/b`. La voie de commande herite de ce comportement au lieu d'en inventer
    un second, sans quoi une meme racine donnerait deux arbres distincts.
    """
    for brute in ("maison//chaudiere", "/maison/chaudiere/"):
        derive = _config_mqtt_transactionnelle(
            config(read_surface=ReadSurfaceConfig(prefix=brute))
        )
        assert derive.command_topic == "maison/chaudiere/command"
        assert derive.ack_topic_prefix == "maison/chaudiere/ack"


def test_b19_exactement_deux_champs_different() -> None:
    """**B19** — toute propriete de CONNEXION est preservee a l'identique.

    C'est la disposition de la tension avec W1 §7.5 (§8.4) : un derive qui ne
    change que les deux topics n'est pas une seconde connexion. Le test le
    prouve par difference exhaustive, et non par une liste choisie a la main —
    un champ ajoute plus tard a `MqttConfig` entre automatiquement dans le
    perimetre.
    """
    source = MqttConfig(
        host="broker.test",
        port=8883,
        client_id="identite-unique",
        keepalive=42,
        username="utilisateur",
        password="secret-non-versionne",
        tls=True,
    )
    derive = _config_mqtt_transactionnelle(config(mqtt=source))

    differents = {
        f.name
        for f in dataclasses.fields(MqttConfig)
        if getattr(source, f.name) != getattr(derive, f.name)
    }
    assert differents == {"command_topic", "ack_topic_prefix"}

    # Enonce a nouveau nommement : une regression sur `client_id` est la plus
    # couteuse de toutes, et merite d'echouer sous son propre nom.
    assert derive.client_id == source.client_id
    assert (derive.host, derive.port, derive.keepalive) == (
        source.host,
        source.port,
        source.keepalive,
    )
    assert (derive.username, derive.password, derive.tls) == (
        source.username,
        source.password,
        source.tls,
    )


def test_b19_le_derive_est_bien_celui_que_recoit_la_surface(paho_double) -> None:
    """Le derive n'est pas qu'une fonction testable : c'est celui qui circule."""
    nichee = ouvert(read_surface=ReadSurfaceConfig(prefix="maison/chaudiere"))
    runtime = build_runtime(
        nichee, NeverStop(), transaction_factory=_composer_transaction(nichee)
    )
    assert runtime.transaction.core._ack_prefix == "maison/chaudiere/ack"


# ---------------------------------------------------------------------------
# D. Rien ne se produit a l'assemblage — B6, B8, B9
# ---------------------------------------------------------------------------


#: Modules dont le chargement signalerait que l'import suffit a armer la voie.
_MODULES_TRANSACTIONNELS = (
    "boilerack.transaction_wiring",
    "boilerack.core.engine",
    "boilerack.core.production_profile",
    "boilerack.adapters.vclient_write",
)


@pytest.mark.parametrize("module", ["boilerack.runtime", "boilerack.lifecycle"])
def test_b6_importer_n_arme_rien(module: str) -> None:
    """**B6** — dans un interpreteur NEUF, l'import ne charge pas la voie.

    `boilerack.lifecycle` est inclus, et c'est le point : depuis W4-E2 il PORTE
    la composition. Ce sont ses imports TARDIFS — a l'interieur de la fabrique —
    qui tiennent cette barriere. Les remonter au niveau du module la ferait
    rougir immediatement.

    La mesure exige un interpreteur neuf : la session de test a deja importe ces
    modules, et interroger `sys.modules` ici ne prouverait rien. Seul un
    interpreteur Python est lance — aucun reseau, aucun broker.
    """
    code = (
        f"import sys, boilerack, {module}\n"
        "charges = [m for m in "
        f"{_MODULES_TRANSACTIONNELS!r} if m in sys.modules]\n"
        "print('|'.join(charges))\n"
    )
    issue = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert issue.returncode == 0, issue.stderr
    assert issue.stdout.strip() == "", (
        f"importer {module} charge deja : {issue.stdout.strip()}"
    )


def test_b6_les_imports_transactionnels_de_lifecycle_sont_tous_tardifs() -> None:
    """Preuve statique, complementaire de la mesure en interpreteur neuf.

    L'interpreteur neuf constate un FAIT a un instant ; celle-ci dit POURQUOI il
    tient, et rougit sur la modification qui le romprait — un import remonte au
    niveau du module.
    """
    arbre = ast.parse((RACINE / "lifecycle.py").read_text(encoding="utf-8"))
    au_niveau_module = {
        noeud.module
        for noeud in arbre.body
        if isinstance(noeud, ast.ImportFrom) and noeud.module
    }
    for interdit in _MODULES_TRANSACTIONNELS:
        assert interdit not in au_niveau_module, f"{interdit} importe au niveau module"


def test_b8_aucun_sous_processus_au_simple_assemblage(paho_double, monkeypatch) -> None:
    """**B8** — composer n'execute rien. Construire un ecrivain n'est pas ecrire.

    `VClientCli` ne fait que retenir sa configuration et son lanceur ; seul un
    `write()` reel invoquerait `vclient`. La preuve sabote les trois portes de
    lancement de processus : les laisser intactes ne prouverait qu'une absence
    d'effet observe, pas une absence d'appel.
    """
    import subprocess as sp

    def interdit(*a, **kw):  # pragma: no cover - doit ne jamais courir
        raise AssertionError(f"un processus a ete lance a l'assemblage : {a!r}")

    monkeypatch.setattr(sp, "Popen", interdit)
    monkeypatch.setattr(sp, "run", interdit)
    monkeypatch.setattr(sp, "check_output", interdit)

    runtime = build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )
    assert runtime.transaction is not None


def test_b9_aucune_ecriture_chaudiere_au_demarrage(paho_double, monkeypatch) -> None:
    """**B9** — l'assemblage n'ecrit pas, et la preuve emploie un ESPION.

    L'ecrivain reel est remplace par un double dont `write` LEVE. Un assemblage
    qui ecrirait — pour sonder le demon, pour relire un etat initial, pour
    n'importe quel motif — ferait rougir ce test au lieu de toucher la
    chaudiere. C'est exactement la sonde n° 5 de §16, rendue permanente.

    La substitution porte sur l'attribut du module d'adaptateur, et elle est
    possible PARCE QUE l'import est tardif : la fabrique resout `VClientCli` a
    l'appel, pas au chargement de `lifecycle`.
    """
    import boilerack.adapters.vclient_write as module_ecriture

    ecritures = []

    class EcrivainEspion:
        def __init__(
            self, config, runner, *, invocation=None, clock=None, evidence=None
        ):
            # `clock` suit la signature reelle depuis
            # `g2-observabilite-preuve.md` : elle ne sert qu'a MESURER une
            # duree d'ecriture, et aucune ecriture n'a lieu a l'assemblage.
            # `evidence` la suit depuis `g2-sortie-preuve-transport.md` : sans
            # interrupteur de campagne il vaut `None`, et rien n'est depose.
            self.config = config
            self.evidence = evidence

        def read(self, command):  # pragma: no cover - non sollicite ici
            raise AssertionError("lecture par la voie transactionnelle a l'assemblage")

        def write(self, command, value):  # pragma: no cover - doit ne jamais courir
            ecritures.append((command, value))
            raise AssertionError(f"ECRITURE au demarrage : {command} {value}")

    monkeypatch.setattr(module_ecriture, "VClientCli", EcrivainEspion)

    runtime = build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )
    assert runtime.transaction is not None
    assert ecritures == []


def test_b9_aucune_connexion_mqtt_au_simple_assemblage(paho_double) -> None:
    """**B9**, complement — assembler ne connecte pas non plus.

    Le double Paho enregistre `connect()`. La racine construit l'adaptateur ;
    c'est le runner qui, en s'executant, etablirait la connexion — et il n'est
    pas execute ici.
    """
    build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )
    assert len(paho_double) == 1
    assert paho_double[0].connected_args is None
    assert paho_double[0].loop_started == 0
    assert paho_double[0].subscriptions == []


# ---------------------------------------------------------------------------
# E. Unicite des pieces composees — B10, B11, B12, B18
# ---------------------------------------------------------------------------


def test_b10_b11_b12_une_seule_piece_de_chaque_est_construite(
    paho_double, monkeypatch
) -> None:
    """**B10**, **B11**, **B12** — un profil, un ecrivain, une surface. Comptes.

    Les barrieres statiques voisines disent qu'il n'existe qu'un seul LIEU
    d'appel ; celle-ci dit qu'un passage par ce lieu ne produit qu'un seul
    exemplaire. Une boucle, un rappel de reconnexion ou une double application
    de la fabrique feraient rougir ce test sans toucher aux precedentes.
    """
    import boilerack.adapters.vclient_write as module_ecriture
    import boilerack.core.production_profile as module_profil
    import boilerack.transaction_wiring as module_cablage

    comptes = {"profil": 0, "ecrivain": 0, "surface": 0}

    def compter(cle, reel):
        def enveloppe(*a, **kw):
            comptes[cle] += 1
            return reel(*a, **kw)

        return enveloppe

    monkeypatch.setattr(
        module_profil,
        "build_production_profile",
        compter("profil", module_profil.build_production_profile),
    )
    monkeypatch.setattr(
        module_ecriture, "VClientCli", compter("ecrivain", module_ecriture.VClientCli)
    )
    monkeypatch.setattr(
        module_cablage,
        "build_transaction_surface",
        compter("surface", module_cablage.build_transaction_surface),
    )

    build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )
    assert comptes == {"profil": 1, "ecrivain": 1, "surface": 1}


def test_b10_le_profil_compose_est_celui_de_production(paho_double) -> None:
    """La composition ne fabrique pas un profil a elle : elle prend CELUI de W4-D."""
    from boilerack.core import build_production_profile

    runtime = build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )
    attendu = build_production_profile()
    obtenu = runtime.transaction.core._profile
    assert obtenu.name == attendu.name
    assert sorted(obtenu.commands) == sorted(attendu.commands) == [
        "dhw_setpoint",
        "heating_curve_shift",
        "heating_curve_slope",
        "heating_setpoint",
    ]


def test_b18_une_seule_construction_de_paho_dans_tout_le_source() -> None:
    """**B18** — le site unique reste celui de `runtime.py`, et lui seul.

    Le balayage est TEXTUEL et couvre tout `src/boilerack`, `lifecycle.py`
    compris. C'est la barriere que la sonde n° 7 de §16 doit faire rougir en
    construisant un second client dans `lifecycle`.
    """
    constructions = []
    for fichier in RACINE.rglob("*.py"):
        if "__pycache__" in fichier.parts:
            continue
        source = fichier.read_text(encoding="utf-8")
        constructions += [fichier.relative_to(RACINE).as_posix()] * source.count(
            "PahoMqttClient("
        )
    assert constructions == ["runtime.py"]


# ---------------------------------------------------------------------------
# F. La barriere B4 est-elle falsifiable ? — B5
# ---------------------------------------------------------------------------


def _lieux_de_decision(sources: dict[str, str]) -> list[str]:
    """Logique de B4, appliquee a un arbre de sources ARBITRAIRE.

    Extraite pour que B5 puisse la soumettre a un depot fictif : eprouver une
    barriere sur le depot reel exigerait d'y ecrire un defaut, ce que §13
    interdit hors sonde jetable.
    """
    trouves = []
    for nom, source in sources.items():
        arbre = ast.parse(source)
        alias = {
            a.asname or a.name: a.name
            for n in ast.walk(arbre)
            if isinstance(n, ast.ImportFrom)
            for a in n.names
        }
        for noeud in ast.walk(arbre):
            if not isinstance(noeud, ast.Call):
                continue
            cible = noeud.func
            appele = None
            if isinstance(cible, ast.Name):
                appele = alias.get(cible.id, cible.id)
            elif isinstance(cible, ast.Attribute):
                appele = cible.attr
            if appele == "build_transaction_surface":
                trouves.append(nom)
    return sorted(trouves)


_APPEL = (
    "from boilerack.transaction_wiring import build_transaction_surface\n"
    "s = build_transaction_surface(mqtt=m, clock=k, config=c, vclient=v, profile=p)\n"
)


def test_b5_un_seul_lieu_de_decision_laisse_la_barriere_verte() -> None:
    """Controle negatif : sans quoi B5 pourrait rougir pour une autre raison."""
    assert _lieux_de_decision({"lifecycle.py": _APPEL}) == ["lifecycle.py"]


def test_b5_un_second_lieu_de_decision_fait_rougir_la_barriere() -> None:
    """**B5** — la liste fermee de B4 detecte un second decideur.

    C'est la sonde n° 1 de §16, rendue permanente et sans ecriture dans le
    depot : la meme logique, soumise a un arbre fictif ou un second module
    compose.
    """
    trouves = _lieux_de_decision({"lifecycle.py": _APPEL, "cli.py": _APPEL})
    assert trouves == ["cli.py", "lifecycle.py"]
    assert trouves != ["lifecycle.py"], "la barriere B4 n'aurait pas rougi"


@pytest.mark.parametrize(
    "forme",
    [
        "from boilerack.transaction_wiring import build_transaction_surface as S\n"
        "s = S(mqtt=m, clock=k, config=c, vclient=v, profile=p)\n",
        "import boilerack.transaction_wiring as tw\n"
        "s = tw.build_transaction_surface(mqtt=m, clock=k, config=c)\n",
        "from boilerack import transaction_wiring\n"
        "s = transaction_wiring.build_transaction_surface(mqtt=m)\n",
    ],
)
def test_b5_les_formes_detournees_sont_vues(forme: str) -> None:
    """Un second decideur ne s'echappe pas par un alias ni par un attribut.

    L'audit de W4-B avait montre une barriere aveugle a ces trois formes ; la
    regression serait silencieuse, donc elle est testee nommement.
    """
    assert _lieux_de_decision({"intrus.py": forme}) == ["intrus.py"]


# ---------------------------------------------------------------------------
# G. Recensement — barrieres portees ailleurs
# ---------------------------------------------------------------------------


def test_le_recensement_des_barrieres_est_exhaustif() -> None:
    """La table §12 compte dix-neuf barrieres : aucune n'est orpheline.

    Ce test ne prouve aucune propriete du produit. Il prouve que la
    CORRESPONDANCE entre la table normative et la suite est tenue a jour, et
    rougit si une reference disparait du recensement.
    """
    portees_ici = {
        "B1", "B2", "B3", "B5", "B6", "B8", "B9",
        "B10", "B11", "B12", "B16", "B17", "B18", "B19",
    }
    portees_ailleurs = {
        # B4 : liste fermee des lieux de DECISION.
        "B4": (
            "tests/test_transaction_wiring.py"
            "::test_la_surface_n_est_composee_que_par_lifecycle ; "
            "tests/adapters/test_vclient_write.py"
            "::test_seul_lifecycle_compose_la_voie_ecrivable ; "
            "tests/core/test_production_profile.py"
            "::test_le_profil_de_production_n_est_construit_que_par_lifecycle"
        ),
        # B7 : `build_runtime` seul ne compose rien implicitement.
        "B7": (
            "tests/test_transaction_wiring.py"
            "::test_la_racine_de_composition_ne_construit_aucune_voie"
        ),
        # B13 : liste fermee des implementations de `write`.
        "B13": (
            "tests/adapters/test_vclient_write.py"
            "::test_les_implementations_de_write_forment_une_liste_fermee"
        ),
        # B14 : aucun `applied` sans relecture — verdict rendu par le coeur.
        "B14": (
            "tests/adapters/test_vclient_write.py"
            "::test_l_adaptateur_ne_relit_jamais_pour_confirmer ; "
            "tests/core/test_execution.py"
        ),
        # B15 : aucun reessai.
        "B15": (
            "tests/adapters/test_vclient_write.py"
            "::test_aucune_boucle_ni_reessai_dans_le_source ; "
            "tests/adapters/test_vclient_write.py"
            "::test_un_appel_declenche_au_plus_une_invocation"
        ),
    }
    couvertes = portees_ici | set(portees_ailleurs)
    attendues = {f"B{n}" for n in range(1, 20)}
    assert couvertes == attendues, f"non couvertes : {sorted(attendues - couvertes)}"


def _temoin_d_ecrivain(recus):
    """Double d'ecrivain qui ne retient que le puits recu a la construction."""

    class EcrivainTemoin:
        def __init__(
            self, config, runner, *, invocation=None, clock=None, evidence=None
        ):
            recus.append(evidence)

        def read(self, command):  # pragma: no cover - non sollicite ici
            raise AssertionError("lecture a l'assemblage")

        def write(self, command, value):  # pragma: no cover - non sollicite ici
            raise AssertionError("ecriture a l'assemblage")

    return EcrivainTemoin


def test_aucun_puits_de_preuve_sans_interrupteur(monkeypatch) -> None:
    """INERTE PAR DEFAUT, jusque dans la racine de composition.

    `evidence_dir` vaut `None` dans toute exploitation ordinaire : aucun
    `FileEvidenceSink` n'est construit, et l'adaptateur ne prendra meme pas la
    branche de depot.
    """
    import boilerack.adapters.vclient_write as module_ecriture

    recus = []
    monkeypatch.setattr(module_ecriture, "VClientCli", _temoin_d_ecrivain(recus))

    build_runtime(
        ouvert(), NeverStop(), transaction_factory=_composer_transaction(ouvert())
    )

    assert recus == [None]


def test_un_puits_est_construit_quand_l_interrupteur_est_pose(
    monkeypatch, tmp_path
) -> None:
    """Et il vise le repertoire designe, sans rien y ecrire a l'assemblage."""
    import dataclasses

    import boilerack.adapters.vclient_write as module_ecriture
    from boilerack.adapters.evidence_sink import FileEvidenceSink

    recus = []
    monkeypatch.setattr(module_ecriture, "VClientCli", _temoin_d_ecrivain(recus))

    config = dataclasses.replace(ouvert(), evidence_dir=str(tmp_path))
    build_runtime(config, NeverStop(), transaction_factory=_composer_transaction(config))

    assert len(recus) == 1
    assert isinstance(recus[0], FileEvidenceSink)
    # Construire le puits n'ecrit RIEN : l'atelier reste vide.
    assert list(tmp_path.iterdir()) == []
