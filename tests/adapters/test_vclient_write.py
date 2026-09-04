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
import logging
import pathlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
from boilerack.testing.fake_clock import VirtualClock
from boilerack.transport.vclient import (
    EvidenceSink,
    TransportStatus,
    VClient,
    WriteObservation,
    WriteResult,
)

#: Racine des modules de production, resolue depuis CE FICHIER.
#:
#: La resolution etait relative au repertoire courant jusqu'a W4-E2. Lance
#: depuis ailleurs, `rglob` ne rendait alors AUCUN fichier et les barrieres de
#: ce module passaient au vert sans rien avoir examine. Une barriere vacante est
#: pire qu'une barriere absente : elle rassure.
_SRC = pathlib.Path(__file__).resolve().parents[2] / "src" / "boilerack"

def _horloge() -> VirtualClock:
    """Horloge INJECTEE dans chaque adaptateur d'ecriture.

    Elle ne sert qu'a la mesure de duree de `g2-observabilite-preuve.md`.
    Figee, elle rend cette mesure DETERMINISTE — duree nulle — et n'influence
    aucun verdict : la classification est calculee avant qu'elle n'intervienne.
    """
    return VirtualClock(datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc))


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
    return VClientCli(
        config, runner, invocation=VclientWriteInvocation(config), clock=_horloge()
    ), runner


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
    """Aucune VALEUR METIER ne sort de l'adaptateur — intention INCHANGEE.

    Le verrou porte sur `value`, pas sur le nombre de champs. Il est ici
    ETENDU : `WriteObservation`, ajoutee par `g2-observabilite-preuve.md`, est
    soumise au meme interdit. Elle porte la signature BRUTE du transport, jamais
    une valeur de datapoint — W4-C §16.4 interdit d'ailleurs d'interpreter le
    champ `value` d'une reponse d'ecriture.
    """
    champs = set(WriteResult.__dataclass_fields__)
    assert champs == {"status", "detail", "observation"}
    assert "value" not in champs

    observes = set(WriteObservation.__dataclass_fields__)
    assert observes == {"args", "stdout", "stderr", "returncode", "duration_s"}
    assert "value" not in observes


def test_l_adaptateur_ne_prononce_aucun_verdict_metier() -> None:
    """`applied`, `accepted`, `rejected` : vocabulaire du coeur, pas du transport."""
    source = (_SRC / "adapters" / "vclient_write.py").read_text(encoding="utf-8")
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
    source = (_SRC / "adapters" / "vclient_write.py").read_text(encoding="utf-8")
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
    source = (_SRC / "adapters" / "vclient_write.py").read_text(
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
        CONFIG,
        RunnerInterdit(),
        invocation=VclientWriteInvocation(CONFIG),
        clock=_horloge(),
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
    adapt = VClientCli(CONFIG, runner, invocation=double, clock=_horloge())
    r = adapt.write("setNiveauM1", 2.0)
    assert double.appels == [("setNiveauM1", 2.0)]
    assert runner.appels[0][0] == ["faux", "--x"]
    assert r.status is TransportStatus.OK


def test_une_fabrique_sans_echo_n_invente_aucune_verification() -> None:
    double = FabriqueDouble(Invocation(args=["faux"], echo=""))
    runner = FauxRunner(resultat(stdout=sortie(command="n'importe quoi")))
    adapt = VClientCli(CONFIG, runner, invocation=double, clock=_horloge())
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


@pytest.mark.parametrize("valeur", [float("nan"), float("inf"), float("-inf")])
def test_une_valeur_non_finie_est_refusee_et_non_devinee(valeur: float) -> None:
    """Le refus des non-finies est INCHANGE : aucune forme ne les represente."""
    with pytest.raises(UnrenderableValue):
        VclientWriteInvocation.render(valeur)


# ---------------------------------------------------------------------------
# I-8 — la forme DECIMALE, et ce qui la fonde
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "valeur,attendu",
    [(1.9, "1.9"), (0.2, "0.2"), (3.5, "3.5"), (2.5, "2.5"), (-0.5, "-0.5")],
)
def test_le_rendu_decimal_est_positionnel_et_pointe(
    valeur: float, attendu: str
) -> None:
    """La forme est celle que le demon parse par `atof` et que le pont emet."""
    assert VclientWriteInvocation.render(valeur) == attendu


def test_le_rendu_entier_ne_devient_pas_decimal() -> None:
    """NON-REGRESSION : les roles a conversion identite recoivent `16`, pas `16.0`.

    C'est l'invariant que la forme decimale ne doit surtout pas emporter avec
    elle : trois des quatre roles du profil de production sont entiers.
    """
    for valeur in (16.0, 15.0, 11.0, 10.0, 2.0, -13.0, 40.0, 0.0, -0.0):
        rendu = VclientWriteInvocation.render(valeur)
        assert "." not in rendu, valeur
        assert rendu == str(int(valeur))


_CRANS_DE_PENTE = [round(k / 10, 1) for k in range(2, 36)]


def test_les_trente_quatre_crans_de_pente_sont_rendus_sans_ambiguite() -> None:
    """I-8 : la NORMALISATION du demon est sans ambiguite sur tout le domaine.

    Le demon parse par `atof` puis applique `calc set="V*10"` vers un `short`.
    Si le produit tombait entre deux entiers, troncature et arrondi
    divergeraient et l'ecriture serait fausse d'un cran, SILENCIEUSEMENT.

    Ce test le verifie cran par cran plutot que de l'affirmer : pour chacun des
    34 crans de [0.2 ; 3.5], `float(rendu) * 10` tombe EXACTEMENT sur l'entier
    attendu, et troncature comme arrondi donnent le meme resultat.
    """
    assert len(_CRANS_DE_PENTE) == 34
    assert _CRANS_DE_PENTE[0] == 0.2
    assert _CRANS_DE_PENTE[-1] == 3.5

    for k, cran in enumerate(_CRANS_DE_PENTE, start=2):
        rendu = VclientWriteInvocation.render(cran)
        produit = float(rendu) * 10
        assert produit == float(k), (cran, rendu, produit)
        assert int(produit) == round(produit) == k, (cran, rendu, produit)


@pytest.mark.parametrize("cran", _CRANS_DE_PENTE)
def test_chaque_cran_est_positionnel_sans_exposant_ni_zero_superflu(
    cran: float,
) -> None:
    """Forme exigee : `.` pour separateur, aucun `e`, aucun zero de queue.

    TROIS crans du domaine sont ENTIERS — 1.0, 2.0, 3.0 — et prennent donc la
    forme entiere, sans point. Ce n'est pas une exception a la regle : c'est la
    regle elle-meme, qui rend la forme entiere quand la valeur est entiere. Le
    demon les parse par `atof` de la meme facon, et `float("2") * 10` vaut 20.
    """
    rendu = VclientWriteInvocation.render(cran)
    assert "e" not in rendu.lower()
    assert "," not in rendu
    assert float(rendu) == cran

    if float(cran).is_integer():
        assert "." not in rendu
        assert rendu == str(int(cran))
    else:
        assert rendu.count(".") == 1
        assert not rendu.endswith("0")


def test_le_rendu_decimal_est_deterministe() -> None:
    """W4-A §15, pour la forme decimale comme pour l'entiere."""
    fab = VclientWriteInvocation(CONFIG)
    assert fab.build("setNeigungM1", 1.9) == fab.build("setNeigungM1", 1.9)
    assert VclientWriteInvocation.render(1.9) == VclientWriteInvocation.render(1.9)


def test_une_valeur_irrepresentable_ne_lance_aucun_processus() -> None:
    """Le refus de B devient une issue de transport, pas une exception."""
    adapt = VClientCli(
        CONFIG,
        RunnerInterdit(),
        invocation=VclientWriteInvocation(CONFIG),
        clock=_horloge(),
    )
    r = adapt.write("setNiveauM1", float("nan"))
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "non fabricable" in r.detail


def test_la_fabrique_ne_porte_aucune_constante_de_site() -> None:
    """Hote, port et executable viennent de la configuration, jamais du code."""
    source = (_SRC / "adapters" / "vclient_write.py").read_text(
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
    """Obligation 21 : LA TAXONOMIE est intacte — c'est elle que l'obligation vise.

    L'arbitrage de §7.3 avait ete tranche en faveur de `detail` seul. Il a ete
    ROUVERT par `g2-observabilite-preuve.md`, dont l'autorite est §7.3 lui-meme :
    l'ajout d'un champ y est admis sous reserve d'un « arbitrage explicite ».
    `observation` est cet ajout, et il est OPTIONNEL.

    Ce que l'obligation 21 interdit — modifier la taxonomie — reste tenu :
    `TransportStatus` est inchange, statut pour statut.
    """
    assert set(WriteResult.__dataclass_fields__) == {
        "status",
        "detail",
        "observation",
    }
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
    """Tous les modules de production. Le balayage ne doit JAMAIS etre vide."""
    modules = [f for f in _SRC.rglob("*.py") if "__pycache__" not in f.parts]
    assert modules, f"balayage vide : {_SRC}"
    assert any(f.name == "lifecycle.py" for f in modules), "lifecycle.py absent"
    return modules





def test_l_adaptateur_ne_connait_ni_mqtt_ni_profil_ni_runtime() -> None:
    """Graphe d'import : la couche adaptateur ne remonte vers rien."""
    source = (_SRC / "adapters" / "vclient_write.py").read_text(
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
        CONFIG,
        RunnerInterdit(),
        invocation=VclientWriteInvocation(CONFIG),
        clock=_horloge(),
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
    adapt = VClientCli(
        CONFIG, runner, invocation=VclientWriteInvocation(CONFIG), clock=_horloge()
    )
    r = adapt.write(mauvais, 2.0)
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "non fabricable" in r.detail


def test_les_noms_a_espacement_de_bordure_restent_refuses_par_le_lecteur() -> None:
    """Les regles heritees continuent de s'appliquer AVANT la garde d'ecriture."""
    adapt = VClientCli(
        CONFIG,
        RunnerInterdit(),
        invocation=VclientWriteInvocation(CONFIG),
        clock=_horloge(),
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
    source = (_SRC / "adapters" / "vclient_write.py").read_text(
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
        CONFIG,
        RunnerInterdit(),
        invocation=VclientWriteInvocation(CONFIG),
        clock=_horloge(),
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
    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=FabriqueQuiEchoue(), clock=_horloge()
    )
    r = adapt.write("setNiveauM1", 2.0)
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "ValueError" in r.detail


def test_une_erreur_de_programmation_de_la_fabrique_remonte() -> None:
    """La frontiere reste ETROITE : on n'absorbe pas `Exception`.

    Deguiser un bug en issue de transport le rendrait invisible, et le coeur
    engagerait une relecture pour une invocation qui n'a jamais eu de sens.
    """
    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=FabriqueQuiCasse(), clock=_horloge()
    )
    with pytest.raises(RuntimeError):
        adapt.write("setNiveauM1", 2.0)


def test_un_detail_d_exception_tres_long_est_borne() -> None:
    class FabriqueBavarde:
        def build(self, command: str, value: float) -> Invocation:
            raise ValueError("Z" * 5000)

    adapt = VClientCli(
        CONFIG, RunnerInterdit(), invocation=FabriqueBavarde(), clock=_horloge()
    )
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


#: Seul module de production autorise a APPELER les symboles de composition.
#: W4-E1 §6 : la decision de composer appartient a `lifecycle`, et a lui seul.
_LIEU_DE_DECISION = "lifecycle.py"


def test_seul_lifecycle_compose_la_voie_ecrivable() -> None:
    """Preuve centrale de la fermeture — liste FERMEE depuis W4-E2.

    Jusqu'a W4-E2, aucun module de production n'appelait ces symboles. La
    fermeture etait une ABSTENTION totale. W4-E1 §11 prescrit son remplacement :
    la composition existe desormais, mais **un seul lieu** a le droit de la
    decider, et un second fait rougir ce test.

    La preuve reste sensible aux formes qu'un module emploierait REELLEMENT —
    alias d'import et acces par attribut compris — et n'exempte aucun fichier
    par son nom : le module qui DEFINIT un symbole n'a pas plus le droit de
    l'appeler qu'un autre. Definir est permis, appeler ne l'est pas, et une
    definition n'est pas un `ast.Call`.

    Ce que cette barriere ne dit PAS : que la composition n'a lieu que sous
    autorite. Elle constate le LIEU, pas la CONDITION. La condition est prouvee
    par le couple
    `tests/test_lifecycle.py::test_le_cycle_de_vie_ne_transmet_aucune_fabrique_si_l_autorite_est_fermee`
    et `…::test_le_cycle_de_vie_transmet_une_fabrique_si_l_autorite_est_ouverte`,
    qui portent sur l'argument REELLEMENT transmis par `run_lifecycle`.

    Le lieu de LECTURE de l'autorite est, lui, ferme par
    `tests/test_w4e2_composition.py::test_seul_lifecycle_consulte_l_autorite_d_activation`.
    """
    fautifs = []
    for fichier in _modules_production():
        if fichier.name == _LIEU_DE_DECISION:
            continue
        arbre = ast.parse(fichier.read_text(encoding="utf-8"))
        for symbole in sorted(_symboles_appeles(arbre) & _SYMBOLES_DE_COMPOSITION):
            fautifs.append(f"{fichier.as_posix()} appelle {symbole}")
    assert fautifs == []

    # Et le lieu autorise les appelle bien tous les quatre : la barriere ne doit
    # pas rester verte parce que la composition aurait disparu.
    lifecycle = next(f for f in _modules_production() if f.name == _LIEU_DE_DECISION)
    appeles = _symboles_appeles(ast.parse(lifecycle.read_text(encoding="utf-8")))
    assert _SYMBOLES_DE_COMPOSITION <= appeles


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
    racine = _SRC
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
        (_SRC / "transport" / "vclient.py").read_text(encoding="utf-8")
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


# ---------------------------------------------------------------------------
# Z. Observabilite de preuve — `g2-observabilite-preuve.md`
# ---------------------------------------------------------------------------


class RunnerQuiConsommeDuTemps:
    """Lanceur qui fait AVANCER l'horloge, pour eprouver la mesure de duree."""

    def __init__(self, horloge: VirtualClock, res: ProcessResult, secondes: float):
        self._horloge = horloge
        self._res = res
        self._secondes = secondes

    def run(self, args, *, timeout):  # type: ignore[no-untyped-def]
        self._horloge.advance(self._secondes)
        return self._res


def test_l_observation_porte_les_cinq_elements_exiges() -> None:
    """`G.2` §16 item 4 : invocation, stdout, stderr, code retour, duree."""
    horloge = _horloge()
    res = resultat(returncode=0, stdout=SUCCES_REEL, stderr=b"")
    adapt = VClientCli(
        CONFIG,
        RunnerQuiConsommeDuTemps(horloge, res, 1.045),
        invocation=VclientWriteInvocation(CONFIG),
        clock=horloge,
    )

    obs = adapt.write("setNiveauM1", 2.0).observation

    assert obs is not None
    # La ligne REELLE, telle qu'executee : executable, drapeaux de site, puis
    # la commande et sa valeur en UN SEUL mot du shell (W4-C, 22 aout 2026).
    assert obs.args[0] == CONFIG.executable
    assert "-J" in obs.args
    assert obs.args[-2:] == ("-c", "setNiveauM1 2")
    assert obs.stdout == SUCCES_REEL
    assert obs.stderr == b""
    assert obs.returncode == 0
    assert obs.duration_s == 1.045


def test_la_duree_vient_de_l_horloge_injectee_et_de_rien_d_autre() -> None:
    """Aucun compteur de la bibliotheque standard : la mesure est DETERMINISTE."""
    horloge = _horloge()
    adapt = VClientCli(
        CONFIG,
        RunnerQuiConsommeDuTemps(horloge, resultat(stdout=SUCCES_REEL), 3.5),
        invocation=VclientWriteInvocation(CONFIG),
        clock=horloge,
    )
    obs = adapt.write("setNiveauM1", 2.0).observation
    assert obs is not None and obs.duration_s == 3.5


def test_stdout_et_stderr_sont_integraux_et_separes() -> None:
    """Ni tronques, ni fusionnes — `W4-A` §18, obligation 5."""
    long_out = b"x" * 5000
    long_err = b"y" * 5000
    adapt, _ = adaptateur(resultat(returncode=1, stdout=long_out, stderr=long_err))

    r = adapt.write("setNiveauM1", 2.0)

    assert r.observation is not None
    assert r.observation.stdout == long_out
    assert r.observation.stderr == long_err
    assert len(r.observation.stdout) == 5000
    assert len(r.observation.stderr) == 5000


def test_detail_reste_borne_meme_quand_l_observation_est_integrale() -> None:
    """« Un diagnostic se borne » — la phrase de W4-B reste vraie."""
    adapt, _ = adaptateur(resultat(returncode=1, stdout=b"z" * 5000, stderr=b""))
    r = adapt.write("setNiveauM1", 2.0)

    assert len(r.detail) < 600
    assert r.observation is not None and len(r.observation.stdout) == 5000


def test_l_observation_existe_aussi_quand_l_ecriture_echoue() -> None:
    """La preuve vaut pour TOUTE issue : un echec se consigne comme un succes."""
    adapt, _ = adaptateur(resultat(timed_out=True, returncode=None))
    r = adapt.write("setNiveauM1", 2.0)

    assert r.status is TransportStatus.TIMEOUT
    assert r.observation is not None
    assert r.observation.returncode is None


def test_aucune_observation_si_le_lanceur_n_a_jamais_ete_appele() -> None:
    """Rien n'a ete invoque : il n'y a rien a observer, et on ne l'invente pas.

    Le critere est bien l'APPEL AU LANCEUR, non l'existence d'un processus —
    voir le test suivant, ou le lancement echoue et ou l'observation existe
    pourtant.
    """
    adapt = VClientCli(
        CONFIG,
        RunnerInterdit(),
        invocation=VclientWriteInvocation(CONFIG),
        clock=_horloge(),
    )
    r = adapt.write("setNiveauM1", float("nan"))

    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert r.observation is None


def test_l_observation_existe_quand_le_lancement_echoue() -> None:
    """`launch_failed` : aucun processus n'est ne, mais la TENTATIVE a eu lieu.

    C'est le cas limite que le contrat de `WriteResult.observation` designe
    nommement. Rien n'a atteint le demon — W4-A §9, ligne 1 — et pourtant la
    preuve existe : la ligne d'arguments montre CE QUI aurait ete emis, et la
    duree montre le temps consomme par la tentative.
    """
    horloge = _horloge()
    adapt = VClientCli(
        CONFIG,
        RunnerQuiConsommeDuTemps(
            horloge,
            resultat(returncode=None, launch_failed=True, launch_error="OSError"),
            0.25,
        ),
        invocation=VclientWriteInvocation(CONFIG),
        clock=horloge,
    )

    r = adapt.write("setNiveauM1", 2.0)

    # Le verdict de transport est INCHANGE : la table fermee de W4-A §9 statue
    # sans jamais consulter l'observation.
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "lancement impossible" in r.detail

    obs = r.observation
    assert obs is not None
    assert obs.args[0] == CONFIG.executable
    assert obs.args[-2:] == ("-c", "setNiveauM1 2")
    assert obs.returncode is None
    assert obs.stdout == b""
    assert obs.stderr == b""
    assert obs.duration_s == 0.25


def test_l_observation_ne_change_aucun_verdict() -> None:
    """La classification est calculee AVANT que l'observation soit attachee."""
    for res, attendu in (
        (resultat(stdout=SUCCES_REEL), TransportStatus.OK),
        (resultat(timed_out=True, returncode=None), TransportStatus.TIMEOUT),
        (resultat(launch_failed=True, returncode=None), TransportStatus.TRANSPORT_ERROR),
        (resultat(stdout=b"\xff\xfe"), TransportStatus.UNUSABLE_OUTPUT),
    ):
        adapt, _ = adaptateur(res)
        assert adapt.write("setNiveauM1", 2.0).status is attendu


def test_l_adaptateur_ne_retient_aucune_observation() -> None:
    """Ni rétention, ni etat : `W4-A` §14 — « sans etat au-dela de sa configuration »."""
    adapt, _ = adaptateur(resultat(stdout=SUCCES_REEL))
    adapt.write("setNiveauM1", 2.0)

    porteurs = [
        nom
        for nom, valeur in vars(adapt).items()
        if isinstance(valeur, (WriteObservation, WriteResult, bytes, list, tuple))
    ]
    assert porteurs == []


def test_aucune_journalisation_integrale_de_stdout_ni_stderr(caplog) -> None:
    """`W4-A` §17 ne les admet au journal que BORNES. Rendre n'est pas journaliser."""
    long_out = b"q" * 5000
    adapt, _ = adaptateur(resultat(returncode=1, stdout=long_out, stderr=b"w" * 5000))

    with caplog.at_level(0):
        adapt.write("setNiveauM1", 2.0)

    journal = "\n".join(rec.getMessage() for rec in caplog.records)
    assert "q" * 600 not in journal
    assert "w" * 600 not in journal


def test_le_module_ne_publie_ni_n_ecrit_l_observation() -> None:
    """Aucun fichier, aucune metrique, aucun compteur, aucune publication."""
    source = (_SRC / "adapters" / "vclient_write.py").read_text(encoding="utf-8")
    corps = source.split('"""', 2)[2]
    for interdit in ("open(", "Path(", "publish", "mqtt", "Counter", "metric"):
        assert interdit not in corps, interdit


# ---------------------------------------------------------------------------
# Z bis. Le puits de preuve — `g2-sortie-preuve-transport.md`
# ---------------------------------------------------------------------------


class PuitsQuiCompte:
    """Puits minimal : retient ce qu'il a recu, pour que le test le lise."""

    def __init__(self) -> None:
        self.recus: list[WriteObservation] = []

    def record(self, observation: WriteObservation) -> None:
        self.recus.append(observation)


class PuitsQuiLeve:
    """Puits fautif : il echoue a chaque depot."""

    def __init__(self) -> None:
        self.appels = 0

    def record(self, observation: WriteObservation) -> None:
        self.appels += 1
        raise OSError("disque plein")


class PuitsLent:
    """Puits LENT : il consomme du temps sans rien signaler.

    Il fait avancer l'horloge APRES la mesure d'invocation, exactement comme
    une entree-sortie lente le ferait. C'est le cas dangereux : il ne leve pas,
    il n'echoue pas, il retarde.
    """

    def __init__(self, horloge: VirtualClock, secondes: float) -> None:
        self._horloge = horloge
        self._secondes = secondes

    def record(self, observation: WriteObservation) -> None:
        self._horloge.advance(self._secondes)


def _adaptateur_avec_puits(res: ProcessResult, puits, horloge=None):
    horloge = horloge or _horloge()
    runner = RunnerQuiConsommeDuTemps(horloge, res, 1.0)
    return VClientCli(
        CONFIG,
        runner,
        invocation=VclientWriteInvocation(CONFIG),
        clock=horloge,
        evidence=puits,
    )


def test_sans_puits_aucun_appel_n_a_lieu() -> None:
    """INERTE PAR DEFAUT — la branche de depot n'est meme pas prise."""
    adapt, _ = adaptateur(resultat(stdout=SUCCES_REEL))

    r = adapt.write("setNiveauM1", 2.0)

    assert r.status is TransportStatus.OK
    assert adapt._evidence is None


def test_le_puits_recoit_l_observation_complete() -> None:
    puits = PuitsQuiCompte()
    adapt = _adaptateur_avec_puits(resultat(stdout=SUCCES_REEL), puits)

    adapt.write("setNiveauM1", 2.0)

    assert len(puits.recus) == 1
    obs = puits.recus[0]
    assert obs.stdout == SUCCES_REEL
    assert obs.returncode == 0
    assert obs.duration_s == 1.0
    assert obs.args[-2:] == ("-c", "setNiveauM1 2")


def test_le_puits_recoit_la_meme_observation_que_le_resultat() -> None:
    """Une seule observation existe : celle rendue est celle deposee."""
    puits = PuitsQuiCompte()
    adapt = _adaptateur_avec_puits(resultat(stdout=SUCCES_REEL), puits)

    r = adapt.write("setNiveauM1", 2.0)

    assert r.observation is puits.recus[0]


def test_un_puits_qui_leve_ne_change_ni_verdict_ni_detail(caplog) -> None:
    """Clause 3 : echec sans effet sur le verdict."""
    puits = PuitsQuiLeve()
    adapt = _adaptateur_avec_puits(resultat(stdout=SUCCES_REEL), puits)

    with caplog.at_level(logging.WARNING):
        avec = adapt.write("setNiveauM1", 2.0)

    sans_adapt, _ = adaptateur(resultat(stdout=SUCCES_REEL))
    sans = sans_adapt.write("setNiveauM1", 2.0)

    assert puits.appels == 1
    assert avec.status is sans.status is TransportStatus.OK
    assert avec.detail == sans.detail
    # Journalise BORNE : le type, et rien de plus.
    journal = " ".join(rec.getMessage() for rec in caplog.records)
    assert "OSError" in journal
    assert "disque plein" not in journal


def test_un_puits_qui_leve_ne_change_pas_l_observation_rendue() -> None:
    """L'`ACK` du coeur se construit sur ce `WriteResult` : il est intact."""
    adapt = _adaptateur_avec_puits(resultat(stdout=SUCCES_REEL), PuitsQuiLeve())

    r = adapt.write("setNiveauM1", 2.0)

    assert r.observation is not None
    assert r.observation.stdout == SUCCES_REEL
    assert r.observation.duration_s == 1.0


def test_un_puits_LENT_ne_change_ni_verdict_ni_duree() -> None:
    """Le cas dangereux : aucune levee, aucun signal, seulement du retard.

    `duration_s` est mesuree autour de la SEULE invocation. Le depot a lieu
    apres, et la lenteur du puits n'y entre pas — meme quand elle depasse
    largement la duree de l'invocation elle-meme.
    """
    horloge = _horloge()
    puits = PuitsLent(horloge, 30.0)
    adapt = _adaptateur_avec_puits(resultat(stdout=SUCCES_REEL), puits, horloge)

    r = adapt.write("setNiveauM1", 2.0)

    assert r.status is TransportStatus.OK
    assert r.observation is not None
    assert r.observation.duration_s == 1.0  # l'invocation, non le depot


def test_le_puits_recoit_aussi_les_ecritures_en_echec() -> None:
    """Une preuve vaut pour toute issue, pas seulement pour les succes."""
    puits = PuitsQuiCompte()
    adapt = _adaptateur_avec_puits(
        resultat(returncode=None, launch_failed=True, launch_error="OSError"), puits
    )

    r = adapt.write("setNiveauM1", 2.0)

    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert len(puits.recus) == 1
    assert puits.recus[0].returncode is None


def test_aucun_depot_si_le_lanceur_n_a_jamais_ete_appele() -> None:
    """Rien n'a ete invoque : il n'y a rien a deposer."""
    puits = PuitsQuiCompte()
    adapt = VClientCli(
        CONFIG,
        RunnerInterdit(),
        invocation=VclientWriteInvocation(CONFIG),
        clock=_horloge(),
        evidence=puits,
    )

    r = adapt.write("setNiveauM1", float("nan"))

    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert puits.recus == []


def test_l_adaptateur_ne_retient_aucune_observation_meme_avec_un_puits() -> None:
    puits = PuitsQuiCompte()
    adapt = _adaptateur_avec_puits(resultat(stdout=SUCCES_REEL), puits)
    adapt.write("setNiveauM1", 2.0)

    porteurs = [
        nom
        for nom, valeur in vars(adapt).items()
        if isinstance(valeur, (WriteObservation, WriteResult, bytes))
    ]
    assert porteurs == []


def test_le_chemin_de_LECTURE_ne_recoit_aucun_puits() -> None:
    """Clause 6 : ecriture uniquement, jamais lecture.

    Le lecteur `VClientCliReader` n'a ni parametre `evidence`, ni attribut : la
    surface de lecture emet environ onze invocations par minute, et l'y brancher
    inonderait l'atelier sans servir aucune preuve.
    """
    import inspect

    from boilerack.adapters.vclient_cli import VClientCliReader

    signature = inspect.signature(VClientCliReader.__init__)
    assert "evidence" not in signature.parameters

    lecteur = VClientCliReader(CONFIG, RunnerInterdit())
    assert not hasattr(lecteur, "_evidence")


def test_le_puits_satisfait_le_protocole_attendu() -> None:
    assert isinstance(PuitsQuiCompte(), EvidenceSink)


def test_un_echec_partiel_de_depot_n_a_aucun_impact_metier(tmp_path, caplog) -> None:
    """Preuve incomplete, verdict intact — le puits REEL, en collision.

    C'est le cas complet de bout en bout : un atelier deja peuple, un depot qui
    echoue a mi-course, et une transaction qui n'en sait rien.
    """
    from boilerack.adapters.evidence_sink import FileEvidenceSink

    (tmp_path / "01-ecriture.err").write_bytes(b"anterieur")
    horloge = _horloge()
    adapt = _adaptateur_avec_puits(
        resultat(stdout=SUCCES_REEL), FileEvidenceSink(tmp_path, clock=horloge), horloge
    )

    with caplog.at_level(logging.WARNING):
        r = adapt.write("setNiveauM1", 2.0)

    assert r.status is TransportStatus.OK
    assert r.observation is not None and r.observation.duration_s == 1.0
    # La preuve est incomplete, et cela se voit : un fichier sur trois.
    assert (tmp_path / "01-ecriture.out").exists()
    assert not (tmp_path / "01-ecriture.meta").exists()
    assert "FileExistsError" in " ".join(r.getMessage() for r in caplog.records)
