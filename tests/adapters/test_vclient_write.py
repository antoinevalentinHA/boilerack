"""Tests de l'adaptateur `vclient` d'ECRITURE (lot W4-B).

Entierement deterministes et HORS LIGNE : aucun processus reel, aucun `vclient`,
aucune socket, aucun shell, aucune chaudiere. Le `ProcessRunner` est un double
qui rend un `ProcessResult` fabrique.

UNE MISE EN GARDE SUR LES DOUBLES
    Une seule signature d'ecriture a jamais ete observee : celle du succes,
    capturee par la campagne W4-C. Toutes les autres reponses employees ici sont
    **SYNTHETIQUES** : elles servent a eprouver le repli conservateur de W4-A §9,
    et ne pretendent reproduire aucun comportement reel de chaudiere. Aucune
    d'elles n'est une capture terrain, et aucune ne doit jamais etre presentee
    comme telle.
"""

from __future__ import annotations

import ast
import json
import pathlib
from dataclasses import dataclass, field
from typing import Mapping

import pytest

from boilerack.adapters.config import VclientConfig
from boilerack.adapters.process_runner import ProcessResult
from boilerack.adapters.vclient_cli import InvalidCommandName, VClientCliReader
from boilerack.adapters.vclient_write import (
    Invocation,
    UnrenderableValue,
    VClientCli,
    VclientWriteInvocation,
)
from boilerack.transport.vclient import TransportStatus, VClient, WriteResult

CONFIG = VclientConfig(
    executable="vclient", host="demon.test", port=4242, write_timeout_s=5.0
)


# ---------------------------------------------------------------------------
# Doubles
# ---------------------------------------------------------------------------


@dataclass
class FauxRunner:
    """Rend un resultat programme et enregistre chaque appel recu."""

    resultat: ProcessResult
    appels: list[tuple[list[str], float]] = field(default_factory=list)

    def run(
        self,
        args: list[str],
        timeout: float,
        env: Mapping[str, str] | None = None,
    ) -> ProcessResult:
        self.appels.append((list(args), timeout))
        return self.resultat


class RunnerInterdit:
    """Fait echouer le test si un processus est lance."""

    def run(self, args, timeout, env=None):  # pragma: no cover - doit ne jamais courir
        raise AssertionError(f"aucun processus ne devait etre lance : {args!r}")


@dataclass
class FabriqueDouble:
    """Partie B substituee — prouve que la frontiere de W4-A §8.1 est reelle."""

    invocation: Invocation
    appels: list[tuple[str, float]] = field(default_factory=list)

    def build(self, command: str, value: float) -> Invocation:
        self.appels.append((command, value))
        return self.invocation


def resultat(
    *,
    returncode: int | None = 0,
    stdout: bytes = b"",
    stderr: bytes = b"",
    timed_out: bool = False,
    launch_failed: bool = False,
    launch_error: str = "",
) -> ProcessResult:
    return ProcessResult(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        launch_failed=launch_failed,
        launch_error=launch_error,
    )


#: LA sortie reellement observee le 22 aout 2026 (W4-C §16.3), a l'octet pres.
SUCCES_REEL: bytes = (
    b'[{"command":"setNiveauM1 2","value":0.000000,"raw":"OK","error":""}]'
)


def sortie(**champs) -> bytes:
    """Reponse SYNTHETIQUE, construite a partir de la forme observee."""
    objet = {"command": "setNiveauM1 2", "value": 0.0, "raw": "OK", "error": ""}
    objet.update(champs)
    return json.dumps([objet]).encode("utf-8")


def adaptateur(res: ProcessResult, *, config: VclientConfig = CONFIG):
    runner = FauxRunner(res)
    return VClientCli(config, runner, invocation=VclientWriteInvocation(config)), runner


# ---------------------------------------------------------------------------
# A. Le Protocol, enfin satisfait
# ---------------------------------------------------------------------------


def test_l_adaptateur_complet_satisfait_le_protocol_vclient() -> None:
    """Obligation 1 de W4-A §18 : `VClient` exige `read` ET `write`."""
    adapt, _ = adaptateur(resultat())
    assert isinstance(adapt, VClient)
    assert callable(adapt.read) and callable(adapt.write)


def test_le_lecteur_seul_reste_en_lecture_seule() -> None:
    """W4-B n'a pas touche au lecteur : il n'ecrit toujours pas."""
    assert not hasattr(VClientCliReader, "write")
    assert not isinstance(VClientCliReader(CONFIG, RunnerInterdit()), VClient)


# ---------------------------------------------------------------------------
# B. LA signature de succes — la seule jamais observee
# ---------------------------------------------------------------------------


def test_la_signature_reelle_de_w4c_donne_ok() -> None:
    """Rejoue la sortie terrain a l'octet pres (W4-C §16.3) : rc 0, stderr vide."""
    adapt, _ = adaptateur(resultat(returncode=0, stdout=SUCCES_REEL, stderr=b""))
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is TransportStatus.OK
    assert r.ok is True


def test_la_ligne_d_invocation_est_celle_caracterisee() -> None:
    """Ordre repris de la ligne REELLEMENT executee (W4-C, `03-ecriture-json`).

    `-J` precede `-h` et `-p`, contrairement au chemin de lecture qui le place en
    dernier. Les deux ordres se valent pour un analyseur d'options ; seul
    celui-ci a ete observe en ecriture, et c'est le seul motif de ce choix.
    """
    adapt, runner = adaptateur(resultat(stdout=SUCCES_REEL))
    adapt.write("setNiveauM1", 2.0)
    args, timeout = runner.appels[0]
    assert args == [
        "vclient", "-J", "-h", "demon.test", "-p", "4242", "-c", "setNiveauM1 2",
    ]
    assert timeout == 5.0


# ---------------------------------------------------------------------------
# C. `value` — le verrou central
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("valeur_json", [0.0, 2.0, 42.0, -1.0, 1e9])
def test_value_n_est_jamais_consulte_pour_classer(valeur_json: float) -> None:
    """`value` **MUST NOT** produire un statut (W4-A §9.3).

    Sur une ecriture acceptee, il vaut `0.000000` alors que le datapoint vaut
    `2` : il ne designe RIEN. Le verdict doit donc etre identique quelle que soit
    sa valeur — y compris egale a la cible, y compris nulle.

    Ce test tue deux implementations naives a la fois : `value == cible` et
    `value != 0`.
    """
    adapt, _ = adaptateur(resultat(stdout=sortie(value=valeur_json)))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.OK


def test_value_absente_rend_la_sortie_inexploitable() -> None:
    """Ignorer `value` n'est pas l'omettre : la structure reste verifiee."""
    charge = json.dumps(
        [{"command": "setNiveauM1 2", "raw": "OK", "error": ""}]
    ).encode("utf-8")
    adapt, _ = adaptateur(resultat(stdout=charge))
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is TransportStatus.UNUSABLE_OUTPUT


def test_aucune_valeur_metier_ne_sort_de_l_adaptateur() -> None:
    """`WriteResult` ne porte que `status` et `detail` — jamais une valeur.

    Verrou structurel : aucune implementation future ne peut y faire remonter
    `value`, le champ n'existe pas.
    """
    champs = set(WriteResult.__dataclass_fields__)
    assert champs == {"status", "detail"}


def test_l_adaptateur_ne_prononce_aucun_verdict_metier() -> None:
    """`applied`, `accepted`, `rejected` : vocabulaire du coeur, pas du transport."""
    source = pathlib.Path(
        "src/boilerack/adapters/vclient_write.py"
    ).read_text(encoding="utf-8")
    corps = source.split('"""', 2)[2]
    for interdit in ("applied", "accepted", "rejected", "Reason", "Ack"):
        assert interdit not in corps, f"verdict metier dans l'adaptateur : {interdit}"


# ---------------------------------------------------------------------------
# D. `raw` — la levee est bornee a la chaine exacte
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw_synthetique",
    ["ok", "OK ", " OK", "OKAY", "OK\n", "SUCCESS", "DONE", "", "0", "true"],
)
def test_un_autre_raw_n_est_pas_la_signature(raw_synthetique: str) -> None:
    """W4-A §9.3 : « rien au-dela ».

    Toutes ces chaines sont SYNTHETIQUES et n'ont jamais ete observees. Aucune
    n'est `"OK"` : aucune ne doit donner `OK`, si « positive » qu'elle paraisse.
    """
    adapt, _ = adaptateur(resultat(stdout=sortie(raw=raw_synthetique)))
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is TransportStatus.TRANSPORT_ERROR


def test_un_raw_non_textuel_n_est_pas_la_signature() -> None:
    adapt, _ = adaptateur(resultat(stdout=sortie(raw=1)))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.TRANSPORT_ERROR


# ---------------------------------------------------------------------------
# E. Les trois autres conditions conjointes de la signature
# ---------------------------------------------------------------------------


def test_un_code_retour_non_nul_n_est_pas_la_signature() -> None:
    adapt, _ = adaptateur(resultat(returncode=1, stdout=SUCCES_REEL))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.TRANSPORT_ERROR


def test_un_stderr_non_vide_n_est_pas_la_signature() -> None:
    """Divergence ASSUMEE avec le chemin de lecture.

    En lecture, `stderr` ne participe jamais a la classification. En ecriture,
    W4-A §9.3 le fait entrer dans la signature : « `stderr` vide, 0 octet ». Le
    contrat decide, pas la symetrie.
    """
    adapt, _ = adaptateur(resultat(stdout=SUCCES_REEL, stderr=b"quelque chose"))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.TRANSPORT_ERROR


def test_un_error_non_vide_n_est_pas_la_signature() -> None:
    adapt, _ = adaptateur(resultat(stdout=sortie(error="ERR: quelque chose")))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.TRANSPORT_ERROR


def test_un_code_retour_nul_ne_suffit_jamais() -> None:
    """W4-A §9.2 : `returncode == 0` **MUST NOT** produire un statut favorable."""
    adapt, _ = adaptateur(resultat(returncode=0, stdout=b"", stderr=b""))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.UNUSABLE_OUTPUT


# ---------------------------------------------------------------------------
# F. Les deux statuts qui restent interdits
# ---------------------------------------------------------------------------


def test_la_signature_de_demon_injoignable_n_est_pas_transposee() -> None:
    """W4-A §11.6 tient : `DAEMON_UNREACHABLE` reste interdit en ecriture.

    La forme employee ici — rc 1, deux flux vides — est celle observee en
    LECTURE (fixture C5 `daemon_unreachable`). Rien ne prouve qu'une ecriture s'y
    comporte de meme, et W4-C n'a provoque aucune panne. Le repli conservateur
    est donc attendu.
    """
    adapt, _ = adaptateur(resultat(returncode=1, stdout=b"", stderr=b""))
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is not TransportStatus.DAEMON_UNREACHABLE
    assert r.status is TransportStatus.UNUSABLE_OUTPUT


def test_la_signature_de_commande_inconnue_n_est_pas_transposee() -> None:
    """W4-A §12.3 tient : `UNKNOWN_COMMAND` reste interdit en ecriture.

    La chaine employee est celle observee en LECTURE. La transposer serait
    exactement la faute que §12.3 interdit.
    """
    adapt, _ = adaptateur(
        resultat(returncode=0, stdout=sortie(error="ERR: command unknown"))
    )
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is not TransportStatus.UNKNOWN_COMMAND
    assert r.status is TransportStatus.TRANSPORT_ERROR


def test_ces_deux_statuts_sont_absents_du_module() -> None:
    """Preuve structurelle : ils ne sont pas seulement evites, ils sont absents."""
    source = pathlib.Path(
        "src/boilerack/adapters/vclient_write.py"
    ).read_text(encoding="utf-8")
    corps = source.split('"""', 2)[2]
    assert "TransportStatus.DAEMON_UNREACHABLE" not in corps
    assert "TransportStatus.UNKNOWN_COMMAND" not in corps


# ---------------------------------------------------------------------------
# G. Repli conservateur — table fermee de W4-A §9
# ---------------------------------------------------------------------------


def test_echec_de_lancement_donne_transport_error() -> None:
    """Ligne 1 : C6 ne ratifie pas `CLIENT_UNAVAILABLE`, on reste prudent."""
    adapt, _ = adaptateur(
        resultat(returncode=None, launch_failed=True, launch_error="FileNotFoundError")
    )
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "FileNotFoundError" in r.detail


def test_delai_epuise_donne_timeout() -> None:
    """Ligne 2. W4-A §10.1 : n'affirme rien sur l'emission."""
    adapt, _ = adaptateur(resultat(returncode=None, timed_out=True))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.TIMEOUT


def test_stdout_non_decodable_donne_unusable_output() -> None:
    """Ligne 3."""
    adapt, _ = adaptateur(resultat(stdout=b"\xff\xfe invalide"))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.UNUSABLE_OUTPUT


@pytest.mark.parametrize(
    "charge",
    [
        b"pas du json",
        b"{}",
        b"[]",
        b'[{"command":"setNiveauM1 2","value":0.0,"raw":"OK","error":""},{"x":1}]',
        b'["texte"]',
        b'[{"command":"setNiveauM1 2","raw":"OK"}]',
        b'[{"command":42,"value":0.0,"raw":"OK","error":""}]',
        b'[{"command":"setNiveauM1 2","value":0.0,"raw":"OK","error":7}]',
    ],
)
def test_forme_inattendue_donne_unusable_output(charge: bytes) -> None:
    """Ligne 4 : toute ambiguite de structure est un echec, jamais un succes."""
    adapt, _ = adaptateur(resultat(stdout=charge))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.UNUSABLE_OUTPUT


def test_un_echo_qui_ne_correspond_pas_est_inexploitable() -> None:
    """On ne saurait pas de quelle invocation la reponse parle."""
    adapt, _ = adaptateur(resultat(stdout=sortie(command="setNiveauM1 7")))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.UNUSABLE_OUTPUT


def test_l_echo_attendu_porte_la_commande_ET_l_argument() -> None:
    """Difference etablie par W4-C : en lecture le nom seul, en ecriture les deux."""
    adapt, _ = adaptateur(resultat(stdout=sortie(command="setNiveauM1")))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.UNUSABLE_OUTPUT


# ---------------------------------------------------------------------------
# H. Aucun retry — W4-A §13
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "res",
    [
        resultat(stdout=SUCCES_REEL),
        resultat(returncode=None, timed_out=True),
        resultat(returncode=None, launch_failed=True, launch_error="OSError"),
        resultat(returncode=3, stdout=b"pas du json"),
        resultat(returncode=0, stdout=b""),
        resultat(stdout=sortie(raw="SUCCESS")),
        resultat(stdout=sortie(error="ERR: quelque chose")),
    ],
)
def test_un_appel_declenche_au_plus_une_invocation(res: ProcessResult) -> None:
    """Quelle que soit l'issue : jamais de seconde tentative."""
    adapt, runner = adaptateur(res)
    adapt.write("setNiveauM1", 2.0)
    assert len(runner.appels) == 1


def test_aucune_boucle_ni_reessai_dans_le_source() -> None:
    """Preuve structurelle : `write` ne contient ni boucle ni seconde invocation."""
    source = pathlib.Path("src/boilerack/adapters/vclient_write.py").read_text(
        encoding="utf-8"
    )
    arbre = ast.parse(source)
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.FunctionDef) and noeud.name == "write":
            boucles = [
                n for n in ast.walk(noeud) if isinstance(n, (ast.For, ast.While))
            ]
            assert boucles == [], "une boucle dans write() ouvrirait la porte au retry"
            appels = [
                n
                for n in ast.walk(noeud)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "run"
            ]
            assert len(appels) == 1, "write() doit lancer au plus un processus"
            break
    else:  # pragma: no cover - la methode existe
        pytest.fail("write() introuvable")


def test_l_adaptateur_ne_relit_jamais_pour_confirmer() -> None:
    """Obligation 16 : la confirmation appartient au coeur."""
    adapt, runner = adaptateur(resultat(stdout=SUCCES_REEL))
    adapt.write("setNiveauM1", 2.0)
    assert len(runner.appels) == 1
    args, _ = runner.appels[0]
    assert not any(a.startswith("get") for a in args)


# ---------------------------------------------------------------------------
# I. Exceptions et validation du nom
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mauvais", ["", " setNiveauM1", "setNiveauM1 ", "set\x00Niveau", "a,b", "-J"]
)
def test_un_nom_invalide_leve_avant_toute_invocation(mauvais: str) -> None:
    """W4-A §7.2 et §8 : memes regles que le lecteur, avant tout processus."""
    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=VclientWriteInvocation(CONFIG)
    )
    with pytest.raises(InvalidCommandName):
        adapt.write(mauvais, 2.0)


@pytest.mark.parametrize(
    "res",
    [
        resultat(stdout=SUCCES_REEL),
        resultat(returncode=None, timed_out=True),
        resultat(returncode=None, launch_failed=True),
        resultat(stdout=b"\xff\xfe"),
        resultat(stdout=b"pas du json"),
        resultat(stdout=sortie(raw="autre")),
    ],
)
def test_aucune_issue_de_transport_ne_leve(res: ProcessResult) -> None:
    """W4-A §7.2 : toute cause est portee par `status`, jamais par une exception."""
    adapt, _ = adaptateur(res)
    assert isinstance(adapt.write("setNiveauM1", 2.0), WriteResult)


# ---------------------------------------------------------------------------
# J. Partie B — fabrication de l'invocation (W4-A §8.1)
# ---------------------------------------------------------------------------


def test_la_fabrique_est_injectee_sans_valeur_par_defaut() -> None:
    """Livrer une piece n'est pas la brancher : rien ne se resout tout seul."""
    import inspect

    p = inspect.signature(VClientCli.__init__).parameters["invocation"]
    assert p.default is inspect.Parameter.empty
    assert p.kind is inspect.Parameter.KEYWORD_ONLY


def test_la_fabrique_est_reellement_substituable() -> None:
    """La frontiere A/B est effective : un double la remplace entierement."""
    double = FabriqueDouble(Invocation(args=["faux", "--x"], echo="echo-double"))
    runner = FauxRunner(
        resultat(stdout=sortie(command="echo-double", raw="OK", error=""))
    )
    adapt = VClientCli(CONFIG, runner, invocation=double)
    r = adapt.write("setNiveauM1", 2.0)
    assert double.appels == [("setNiveauM1", 2.0)]
    assert runner.appels[0][0] == ["faux", "--x"]
    assert r.status is TransportStatus.OK


def test_une_fabrique_sans_echo_n_invente_aucune_verification() -> None:
    double = FabriqueDouble(Invocation(args=["faux"], echo=""))
    runner = FauxRunner(resultat(stdout=sortie(command="n'importe quoi")))
    adapt = VClientCli(CONFIG, runner, invocation=double)
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.OK


@pytest.mark.parametrize(
    "valeur,attendu", [(2.0, "2"), (-13.0, "-13"), (40.0, "40"), (0.0, "0"), (-0.0, "0")]
)
def test_le_rendu_entier_est_celui_caracterise(valeur: float, attendu: str) -> None:
    assert VclientWriteInvocation.render(valeur) == attendu


def test_le_rendu_est_deterministe() -> None:
    """W4-A §15 : deux appels de meme valeur donnent la meme ligne."""
    fab = VclientWriteInvocation(CONFIG)
    assert fab.build("setNiveauM1", 2.0) == fab.build("setNiveauM1", 2.0)


@pytest.mark.parametrize("valeur", [2.5, -0.5, float("nan"), float("inf")])
def test_une_valeur_non_entiere_est_refusee_et_non_devinee(valeur: float) -> None:
    """I-8 n'est pas levee : aucune forme decimale n'a jamais ete acceptee."""
    with pytest.raises(UnrenderableValue):
        VclientWriteInvocation.render(valeur)


def test_une_valeur_irrepresentable_ne_lance_aucun_processus() -> None:
    """Le refus de B devient une issue de transport, pas une exception."""
    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=VclientWriteInvocation(CONFIG)
    )
    r = adapt.write("setNiveauM1", 2.5)
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "non fabricable" in r.detail


def test_la_fabrique_ne_porte_aucune_constante_de_site() -> None:
    """Hote, port et executable viennent de la configuration, jamais du code."""
    source = pathlib.Path("src/boilerack/adapters/vclient_write.py").read_text(
        encoding="utf-8"
    )
    for interdit in ("localhost", "192.168", "/home/", ".service", ".timer", "3002"):
        assert interdit not in source, f"constante de site : {interdit}"


def test_aucun_shell_ni_concatenation_dans_la_ligne() -> None:
    """W4-A §8 : liste d'arguments, jamais de chaine assemblee."""
    fab = VclientWriteInvocation(CONFIG)
    args = fab.build("setNiveauM1", 2.0).args
    assert all(isinstance(a, str) for a in args)
    assert args.count("-c") == 1
    assert args[args.index("-c") + 1] == "setNiveauM1 2"
    assert args[1] == "-J"


# ---------------------------------------------------------------------------
# K. `detail` — arbitrage de W4-A §7.3
# ---------------------------------------------------------------------------


def test_le_diagnostic_est_borne() -> None:
    """`detail` porte un extrait, jamais la sortie entiere (W4-A §17)."""
    enorme = ("x" * 5000).encode("utf-8")
    adapt, _ = adaptateur(resultat(stdout=enorme))
    detail = adapt.write("setNiveauM1", 2.0).detail
    assert len(detail) < 600
    assert "x" in detail


def test_la_taxonomie_de_transport_n_a_pas_ete_modifiee() -> None:
    """Obligation 21 : W4-B n'ajoute aucun champ ni statut.

    L'arbitrage de §7.3 est tranche en faveur de `detail` : aucun champ `raw`
    n'est ajoute a `WriteResult`.
    """
    assert set(WriteResult.__dataclass_fields__) == {"status", "detail"}
    assert {s.name for s in TransportStatus} == {
        "OK",
        "DAEMON_UNREACHABLE",
        "UNKNOWN_COMMAND",
        "TIMEOUT",
        "UNUSABLE_OUTPUT",
        "TRANSPORT_ERROR",
    }


# ---------------------------------------------------------------------------
# L. Frontieres — W4-B livre, ne branche pas
# ---------------------------------------------------------------------------


def _modules_production() -> list[pathlib.Path]:
    racine = pathlib.Path("src/boilerack")
    return [f for f in racine.rglob("*.py") if "__pycache__" not in f.parts]





def test_l_adaptateur_ne_connait_ni_mqtt_ni_profil_ni_runtime() -> None:
    """Graphe d'import : la couche adaptateur ne remonte vers rien."""
    source = pathlib.Path("src/boilerack/adapters/vclient_write.py").read_text(
        encoding="utf-8"
    )
    cibles = []
    for noeud in ast.walk(ast.parse(source)):
        if isinstance(noeud, ast.ImportFrom) and noeud.module:
            cibles.append(noeud.module)
        elif isinstance(noeud, ast.Import):
            cibles += [a.name for a in noeud.names]
    for interdit in (
        "boilerack.core",
        "boilerack.runtime",
        "boilerack.transaction_wiring",
        "boilerack.read_surface",
        "boilerack.testing",
        "paho",
    ):
        assert not any(c.startswith(interdit) for c in cibles), interdit


# ---------------------------------------------------------------------------
# M. MAJEUR-3 — un nom porteur d'espacement interne n'est jamais emis
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "controle",
    ["setNiveauM1\t99", "setNiveauM1\n99", "setNiveauM1\x0b99", "setNiveauM1\x0c99"],
)
def test_un_espacement_de_controle_est_deja_refuse_par_l_heritage(
    controle: str,
) -> None:
    """Tabulation, saut de ligne, tabulation verticale : caracteres de CONTROLE.

    La validation heritee les refuse deja, AVANT la garde d'ecriture, et leve
    `InvalidCommandName` sans lancer aucun processus. La garde ajoutee par W4-B
    ne les voit donc jamais — et c'est bien ainsi : le trou reel etait ailleurs.
    """
    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=VclientWriteInvocation(CONFIG)
    )
    with pytest.raises(InvalidCommandName):
        adapt.write(controle, 2.0)


@pytest.mark.parametrize(
    "mauvais",
    [
        "setNiveauM1 99",
        "set NiveauM1",
        "a b c",
        "setNiveauM1\xa099",  # espace insecable : ni controle, ni ASCII
        "setNiveauM1 99",  # demi-cadratin : espace Unicode
    ],
)
def test_un_espacement_interne_n_emet_rien(mauvais: str) -> None:
    """Le danger est propre a l'ECRITURE, et il precede la reponse.

    L'argument de `-c` porte ici `"<commande> <valeur>"`. Un espace interne y
    glisse un mot de plus : `setNiveauM1 99` avec la valeur `2` emettrait
    `setNiveauM1 99 2`. Le demon rejetterait sans doute — mais l'emission
    fautive aurait deja eu lieu, et c'est cela qu'il faut empecher.

    Ces cas sont exactement ceux que la validation heritee LAISSE PASSER :
    l'espace ordinaire et les espaces Unicode ne sont pas des caracteres de
    controle. C'est la le trou reel, et c'est lui que la garde ferme.

    Le lecteur, lui, tolere ces noms sans risque : son `-c` porte le nom seul.
    Ses regles ne sont donc pas elargies ; la garde est ajoutee cote ecriture.
    """
    runner = RunnerInterdit()
    adapt = VClientCli(CONFIG, runner, invocation=VclientWriteInvocation(CONFIG))
    r = adapt.write(mauvais, 2.0)
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "non fabricable" in r.detail


def test_les_noms_a_espacement_de_bordure_restent_refuses_par_le_lecteur() -> None:
    """Les regles heritees continuent de s'appliquer AVANT la garde d'ecriture."""
    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=VclientWriteInvocation(CONFIG)
    )
    for borde in (" setNiveauM1", "setNiveauM1 "):
        with pytest.raises(InvalidCommandName):
            adapt.write(borde, 2.0)


def test_le_lecteur_n_a_pas_ete_durci_par_les_besoins_de_l_ecriture() -> None:
    """`VClientCliReader._validate_command` accepte toujours l'espace interne.

    Elargir la validation du lecteur pour resoudre un probleme d'ecriture aurait
    change un composant audite pour une raison qui ne le concerne pas.
    """
    VClientCliReader._validate_command("get Niveau M1")  # ne leve pas


def test_la_commande_normale_reste_acceptee() -> None:
    adapt, _ = adaptateur(resultat(stdout=SUCCES_REEL))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.OK


# ---------------------------------------------------------------------------
# N. MAJEUR-4 — `value` doit etre NUMERIQUE, sans que sa grandeur compte
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "non_numerique",
    ["0", "banane", None, True, False, [], [1], {}, {"a": 1}],
)
def test_un_value_non_numerique_ne_peut_jamais_donner_ok(non_numerique) -> None:
    """La signature caracterisee porte un NOMBRE a cette place.

    Une chaine, `None`, une liste ou un objet decrivent une reponse d'une AUTRE
    forme que celle observee — donc une sortie inexploitable, jamais un succes.
    `bool` est ecarte explicitement : il est sous-classe de `int`, et `True`
    passerait sinon pour un nombre.

    Ce controle porte sur le TYPE, jamais sur la grandeur.
    """
    adapt, _ = adaptateur(resultat(stdout=sortie(value=non_numerique)))
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is not TransportStatus.OK
    assert r.status is TransportStatus.UNUSABLE_OUTPUT


@pytest.mark.parametrize("numerique", [0, 0.0, 2, 2.0, 42, -1, 1e9, -0.0])
def test_toute_grandeur_numerique_donne_le_meme_verdict(numerique) -> None:
    """La grandeur reste ignoree : entier ou flottant, nul ou non, meme verdict."""
    adapt, _ = adaptateur(resultat(stdout=sortie(value=numerique)))
    assert adapt.write("setNiveauM1", 2.0).status is TransportStatus.OK


def test_la_grandeur_de_value_n_est_lue_nulle_part_dans_le_source() -> None:
    """Verrou structurel : `value` n'est compare a rien.

    Le module doit consulter `value` pour verifier son TYPE, et pour cela
    seulement. Aucune comparaison de grandeur ne doit y figurer.
    """
    source = pathlib.Path("src/boilerack/adapters/vclient_write.py").read_text(
        encoding="utf-8"
    )
    corps = source.split('"""', 2)[2]
    for interdit in ('value"] == ', 'value"] != ', "valeur == 0", "valeur != 0"):
        assert interdit not in corps, f"grandeur de value lue : {interdit}"


# ---------------------------------------------------------------------------
# O. MINEUR-1 — `detail` reellement borne, quelle que soit la source
# ---------------------------------------------------------------------------


def test_un_raw_tres_long_ne_deborde_pas_le_detail() -> None:
    adapt, _ = adaptateur(resultat(stdout=sortie(raw="R" * 5000)))
    detail = adapt.write("setNiveauM1", 2.0).detail
    assert len(detail) < 900
    assert "R" in detail


def test_un_error_tres_long_ne_deborde_pas_le_detail() -> None:
    adapt, _ = adaptateur(resultat(stdout=sortie(error="E" * 5000)))
    detail = adapt.write("setNiveauM1", 2.0).detail
    assert len(detail) < 900
    assert "E" in detail


def test_raw_error_et_flux_longs_ensemble_restent_bornes() -> None:
    """Le pire cas : toutes les sources de diagnostic saturees a la fois."""
    charge = json.dumps(
        [
            {
                "command": "setNiveauM1 2",
                "value": 0.0,
                "raw": "R" * 9000,
                "error": "E" * 9000,
            }
        ]
    ).encode("utf-8")
    adapt, _ = adaptateur(resultat(stdout=charge, stderr=b"S" * 9000))
    detail = adapt.write("setNiveauM1", 2.0).detail
    assert len(detail) < 1200


# ---------------------------------------------------------------------------
# P. MINEUR-2 — aucune exception de preparation ne fuit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mauvaise", ["deux", None, [2], {"v": 2}, True, False])
def test_une_valeur_de_type_invalide_est_refusee_sans_processus(mauvaise) -> None:
    """Aucune valeur d'appelant invalide ne remonte en exception brute."""
    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=VclientWriteInvocation(CONFIG)
    )
    r = adapt.write("setNiveauM1", mauvaise)
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "non fabricable" in r.detail


@pytest.mark.parametrize("mauvaise", ["deux", None, [2], True])
def test_le_rendu_refuse_les_types_invalides(mauvaise) -> None:
    with pytest.raises(UnrenderableValue):
        VclientWriteInvocation.render(mauvaise)


class FabriqueQuiEchoue:
    """Fabrique substituee levant une erreur d'entree ordinaire."""

    def build(self, command: str, value: float) -> Invocation:
        raise ValueError("entree non qualifiable par cette fabrique")


class FabriqueQuiCasse:
    """Fabrique substituee comportant une ERREUR DE PROGRAMMATION."""

    def build(self, command: str, value: float) -> Invocation:
        raise RuntimeError("bug interne de la fabrique")


def test_une_erreur_d_entree_de_la_fabrique_devient_une_issue() -> None:
    adapt = VClientCli(CONFIG, RunnerInterdit(), invocation=FabriqueQuiEchoue())
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "ValueError" in r.detail


def test_une_erreur_de_programmation_de_la_fabrique_remonte() -> None:
    """La frontiere reste ETROITE : on n'absorbe pas `Exception`.

    Deguiser un bug en issue de transport le rendrait invisible, et le coeur
    engagerait une relecture pour une invocation qui n'a jamais eu de sens.
    """
    adapt = VClientCli(CONFIG, RunnerInterdit(), invocation=FabriqueQuiCasse())
    with pytest.raises(RuntimeError):
        adapt.write("setNiveauM1", 2.0)


def test_un_detail_d_exception_tres_long_est_borne() -> None:
    class FabriqueBavarde:
        def build(self, command: str, value: float) -> Invocation:
            raise ValueError("Z" * 5000)

    adapt = VClientCli(CONFIG, RunnerInterdit(), invocation=FabriqueBavarde())
    detail = adapt.write("setNiveauM1", 2.0).detail
    assert len(detail) < 400


# ---------------------------------------------------------------------------
# Q. MAJEUR-1 / MAJEUR-2 — les barrieres structurelles, rendues sensibles
# ---------------------------------------------------------------------------
#
# Une barriere qui ne voit qu'`ast.Name` est une barriere trouee : un module de
# production peut composer la voie entiere par `module.Symbole(...)` ou par un
# alias d'import, sans qu'aucun test ne rougisse. Les deux resolveurs ci-dessous
# suivent donc les alias et les acces par attribut.


def _symboles_appeles(arbre: ast.AST) -> set[str]:
    """Noms d'origine des symboles APPELES dans un module, alias resolus.

    Trois formes sont suivies, et ce sont celles qu'un appelant emploierait
    naturellement :

    - `from m import S` puis `S(...)`             -> `S`
    - `from m import S as Alias` puis `Alias(...)` -> `S`
    - `import m` / `import m as a` puis `m.S(...)` -> `S`

    Le dernier cas se resout par le seul attribut : suivre le module importe
    n'ajouterait rien, un attribut `S` appele sur autre chose etant deja une
    coincidence qu'il vaut mieux signaler que taire.
    """
    alias: dict[str, str] = {}
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.ImportFrom):
            for nom in noeud.names:
                alias[nom.asname or nom.name] = nom.name

    appeles: set[str] = set()
    for noeud in ast.walk(arbre):
        if not isinstance(noeud, ast.Call):
            continue
        cible = noeud.func
        if isinstance(cible, ast.Name):
            appeles.add(alias.get(cible.id, cible.id))
        elif isinstance(cible, ast.Attribute):
            appeles.add(cible.attr)
    return appeles


#: Symboles dont un APPEL depuis un module de production ouvrirait la voie
#: ecrivable. Les definir est permis ; les appeler ne l'est pas.
_SYMBOLES_DE_COMPOSITION = {
    "VClientCli",
    "VclientWriteInvocation",
    "build_production_profile",
    "build_transaction_surface",
}


def test_aucun_module_de_production_ne_compose_la_voie_ecrivable() -> None:
    """Preuve centrale de la fermeture, depuis que celle-ci est une ABSTENTION.

    Les deux dependances existent : un module qui les assemblerait obtiendrait
    une voie fonctionnelle. Plus rien ne l'en empeche structurellement — seule
    cette preuve le detecte. Elle doit donc etre sensible aux formes qu'un tel
    module emploierait REELLEMENT, et pas seulement a la plus naive.

    Aucune exemption par nom de fichier : le module qui DEFINIT un symbole n'a
    pas plus le droit de l'appeler qu'un autre. Definir est permis, appeler ne
    l'est pas — et une definition n'est pas un `ast.Call`.
    """
    fautifs = []
    for fichier in _modules_production():
        arbre = ast.parse(fichier.read_text(encoding="utf-8"))
        for symbole in sorted(_symboles_appeles(arbre) & _SYMBOLES_DE_COMPOSITION):
            fautifs.append(f"{fichier.as_posix()} appelle {symbole}")
    assert fautifs == []


def test_la_barriere_detecte_un_appel_direct() -> None:
    """Sonde permanente : la barriere rougirait-elle vraiment ?

    Une preuve de non-detection est aussi importante que la preuve elle-meme.
    Ces trois tests soumettent au resolveur les formes exactes que l'audit a
    montrees invisibles, sans jamais ecrire dans le depot.
    """
    arbre = ast.parse(
        "from boilerack.adapters.vclient_write import VClientCli\n"
        "x = VClientCli(config, runner, invocation=inv)\n"
    )
    assert "VClientCli" in _symboles_appeles(arbre)


def test_la_barriere_detecte_un_appel_par_alias() -> None:
    arbre = ast.parse(
        "from boilerack.adapters.vclient_write import VClientCli as Writer\n"
        "from boilerack.core.production_profile import build_production_profile as P\n"
        "from boilerack.transaction_wiring import build_transaction_surface as S\n"
        "a = Writer(c, r, invocation=i)\n"
        "b = P()\n"
        "d = S(mqtt=m, clock=k, config=c, vclient=a, profile=b)\n"
    )
    trouves = _symboles_appeles(arbre)
    assert {
        "VClientCli",
        "build_production_profile",
        "build_transaction_surface",
    } <= trouves


def test_la_barriere_detecte_un_appel_par_attribut() -> None:
    arbre = ast.parse(
        "from boilerack.adapters import vclient_write\n"
        "from boilerack.core import production_profile\n"
        "import boilerack.transaction_wiring as tw\n"
        "a = vclient_write.VclientWriteInvocation(cfg)\n"
        "b = vclient_write.VClientCli(cfg, runner, invocation=a)\n"
        "c = production_profile.build_production_profile()\n"
        "d = tw.build_transaction_surface(vclient=b, profile=c)\n"
    )
    trouves = _symboles_appeles(arbre)
    assert _SYMBOLES_DE_COMPOSITION <= trouves


def test_la_barriere_ne_confond_pas_definition_et_appel() -> None:
    """Definir est permis : sans quoi la barriere interdirait sa propre cible."""
    arbre = ast.parse(
        "def build_production_profile():\n    return None\n"
        "class VClientCli:\n    pass\n"
        "from boilerack.adapters.vclient_write import VClientCli as W\n"
    )
    assert _symboles_appeles(arbre) & _SYMBOLES_DE_COMPOSITION == set()


# --- MAJEUR-2 : liste fermee des implementations de `write` ------------------


#: Seule exemption, exacte et justifiee : `transport/vclient.py` DECLARE `write`
#: dans le Protocol `VClient`. Une declaration de Protocol n'est pas une
#: implementation — son corps est `...`.
_DECLARATION_DE_PROTOCOL = "transport/vclient.py"


def test_les_implementations_de_write_forment_une_liste_fermee() -> None:
    """Balayage de TOUT `src/boilerack`, `def` et `async def` compris.

    Le scan de W3 se limitait a `adapters/` et a `ast.FunctionDef`. Deux angles
    morts en decoulaient : un ecrivain place ailleurs dans le paquet, et un
    `async def write`. Les deux sont ici couverts.

    AUCUNE EXEMPTION DE REPERTOIRE
        `testing/` n'est pas exempte, et son double figure donc dans la liste.
        L'exempter aurait ete defendable — c'est de l'infrastructure de test, et
        une autre barriere interdit deja au produit de l'importer — mais une
        liste sans exemption est plus solide qu'une liste avec une exemption
        justifiee : elle n'a pas de bord ou se glisser. Un double supplementaire
        fait rougir ce test, ce qui est l'effet recherche.

    La seule exemption porte sur la DECLARATION du Protocol, dont le corps est
    `...` — et un test voisin verifie que c'est bien le cas.
    """
    racine = pathlib.Path("src/boilerack")
    implementations = []
    for fichier in _modules_production():
        relatif = fichier.relative_to(racine).as_posix()
        if relatif == _DECLARATION_DE_PROTOCOL:
            continue
        for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
            if (
                isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef))
                and noeud.name == "write"
            ):
                implementations.append(relatif)
    assert sorted(implementations) == [
        "adapters/vclient_write.py",  # PRODUCTION — le seul ecrivain reel
        "testing/fake_vclient.py",  # DOUBLE — infrastructure de test declaree
    ]


def test_la_liste_fermee_verrait_un_write_asynchrone() -> None:
    """Sonde : un `async def write` doit compter comme une implementation."""
    arbre = ast.parse("class X:\n    async def write(self, c, v):\n        return None\n")
    trouves = [
        n.name
        for n in ast.walk(arbre)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "write"
    ]
    assert trouves == ["write"]


def test_l_exemption_du_protocol_est_exacte_et_justifiee() -> None:
    """L'unique exemption porte sur une DECLARATION, dont le corps est `...`."""
    arbre = ast.parse(
        pathlib.Path("src/boilerack/transport/vclient.py").read_text(encoding="utf-8")
    )
    corps = [
        n
        for n in ast.walk(arbre)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "write"
    ]
    assert len(corps) == 1
    (unique,) = corps
    assert all(
        isinstance(instruction, ast.Expr)
        and isinstance(instruction.value, ast.Constant)
        and instruction.value.value is Ellipsis
        for instruction in unique.body
    ), "l'exemption ne vaut que pour un corps `...`"
