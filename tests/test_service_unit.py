"""Tests du gabarit d'unite systemd et du script console installe (lot C12).

Aucun `systemctl`, aucun `systemd-analyze`, aucune machine cible : ce module
prouve le CONTENU du gabarit par analyse deterministe, et le comportement du
script console REELLEMENT installe dans un environnement jetable.

CE QUE CES TESTS NE PROUVENT PAS
    Qu'une unite reelle se charge, demarre ou s'arrete sur la cible ; que
    `journald` capture ; que `TimeoutStopSec` suffise en pratique ; que
    `RestartSec` evite la limite de demarrage de la distribution. C12 §14 range
    ces points en qualification terrain, et rien ici ne les revendique.

RESEAU
    La preuve du script console installe **peut necessiter un acces a l'index
    des paquets** : l'isolation de build PEP 517 y recupere le backend declare.
    Voir la fixture `boilerack_installe`, qui le documente precisement.
"""

from __future__ import annotations

import configparser
import pathlib
import re
import subprocess
import sysconfig
import venv

import pytest

import boilerack.cli
from boilerack.adapters.config import VclientConfig
from boilerack.cli import CODE_CONFIGURATION
from boilerack.read_surface.measurements import V1_MEASUREMENTS

_RACINE = pathlib.Path(boilerack.cli.__file__).parents[2]
_UNITE = _RACINE / "systemd" / "boilerack.service"

#: Valeurs contractees par C12. Repetees ici PARCE QUE le test doit tomber si le
#: gabarit derive, pas se contenter de relire le gabarit.
_EXEC = "/opt/boilerack/venv/bin/boilerack"
_TOML = "/etc/boilerack/boilerack.toml"
_ENV = "/etc/boilerack/boilerack.env"
_CIBLE_RESEAU = "network-online.target"

#: Jeu FERME des directives autorisees, par section. Toute clause absente de ce
#: jeu est un ajout hors contrat — notamment le durcissement que C12 §12 a
#: explicitement refuse de promettre faute de pouvoir l'eprouver.
_AUTORISEES = {
    "Unit": {"Description", "Documentation", "Wants", "After"},
    "Service": {
        "Type", "User", "Group", "ExecStart", "EnvironmentFile",
        "Restart", "RestartPreventExitStatus", "RestartSec",
        "KillSignal", "TimeoutStopSec",
    },
    "Install": {"WantedBy"},
}


def _analyser(texte: str) -> configparser.ConfigParser:
    """Analyse un texte d'unite comme un fichier de type INI.

    `interpolation=None` est indispensable : `%` est un caractere de specificateur
    systemd, que `configparser` tenterait sinon d'interpreter. `optionxform=str`
    preserve la casse des directives, qui est significative.

    MODE STRICT — volontaire, et non un defaut laisse en place. En mode tolerant,
    une directive repetee est acceptee et **la derniere gagne** : un
    `EnvironmentFile=` ou un `ExecStart=` errone glisse AVANT le bon passerait
    alors totalement inapercu, alors que systemd, lui, en tiendrait compte.
    Le mode strict transforme toute repetition en echec d'analyse, donc en test
    rouge.

    Consequence assumee : le gabarit ne peut porter aucune directive repetee.
    Aucune clause de C12 §9 n'en demande, et une repetition future devrait etre
    une decision explicite, pas un accident silencieux.
    """
    parseur = configparser.ConfigParser(interpolation=None, delimiters=("=",))
    parseur.optionxform = str  # type: ignore[method-assign]
    parseur.read_string(texte)
    return parseur


def _unite() -> configparser.ConfigParser:
    return _analyser(_UNITE.read_text(encoding="utf-8"))


def _duree_en_secondes(valeur: str) -> float:
    """Convertit une duree systemd simple en secondes.

    Couvre les seules formes que le gabarit contracte : un nombre nu, ou un
    nombre suffixe de `s`, `min` ou `h`. Toute autre forme est refusee plutot
    qu'interpretee au jugé.
    """
    texte = valeur.strip()
    for suffixe, facteur in (("min", 60.0), ("h", 3600.0), ("s", 1.0)):
        if texte.endswith(suffixe):
            return float(texte[: -len(suffixe)]) * facteur
    return float(texte)


def _plancher_arret_s() -> float:
    """Plancher d'arret de C12 §10, calcule sur le CODE et non recopie.

    Un cycle deja commence n'est jamais tronque, et chaque lecture est bornee par
    le budget du sous-processus : le pire cas de la phase de lecture vaut donc
    `nombre de COMMANDES DISTINCTES x read_timeout_s`. Distinctes, et non
    nombre de mesures : le publieur memoise la lecture par cycle, donc deux
    mesures partageant une commande (§4.3, le brulleur) n'en coutent qu'une. Si
    la surface grandit ou si le budget par defaut augmente, ce plancher suit —
    et le test avec lui.
    """
    distinctes = {spec.read for spec in V1_MEASUREMENTS}
    return len(distinctes) * VclientConfig(executable="x").read_timeout_s


# ---------------------------------------------------------------------------
# Presence et forme
# ---------------------------------------------------------------------------


def test_le_gabarit_est_versionne() -> None:
    assert _UNITE.is_file()


def test_le_gabarit_est_analysable_et_ses_sections_sont_celles_attendues() -> None:
    assert set(_unite().sections()) == {"Unit", "Service", "Install"}


def test_aucune_directive_hors_contrat() -> None:
    """C12 §12 refuse de promettre un durcissement qu'il ne peut pas eprouver."""
    parseur = _unite()
    for section, autorisees in _AUTORISEES.items():
        surnumeraires = set(parseur[section]) - autorisees
        assert surnumeraires == set(), f"[{section}] : {sorted(surnumeraires)}"


def test_une_directive_dupliquee_fait_echouer_l_analyse() -> None:
    """MAJ-1 : en mode tolerant, un doublon place AVANT le bon survivait.

    `configparser` tolerant accepte la repetition et retient la DERNIERE valeur ;
    un `EnvironmentFile=` errone glisse avant le bon serait donc invisible au
    test, alors que systemd en tiendrait compte. Le mode strict le refuse.
    """
    texte = _UNITE.read_text(encoding="utf-8")
    for directive, faux in (
        ("EnvironmentFile=", "EnvironmentFile=/etc/mauvais.env\n"),
        ("ExecStart=", "ExecStart=/usr/bin/false\n"),
    ):
        sabote = texte.replace(directive, faux + directive, 1)
        with pytest.raises(configparser.DuplicateOptionError):
            _analyser(sabote)


def test_les_formes_systemd_legitimes_restent_acceptees() -> None:
    """Le mode strict ne doit pas transformer le parseur en faux positif.

    Quatre variantes que systemd accepte et que C12 n'interdit pas : l'ordre
    inverse des codes, une duree en entier nu, un specificateur `%`, et une
    directive hors contrat mentionnee en simple commentaire.

    Ce test construit ses variantes A PARTIR de la forme canonique du gabarit :
    il exige donc que celle-ci soit en place. Une campagne de mutation qui
    appliquerait deja l'une de ces variantes au fichier le ferait echouer sur sa
    precondition — ce n'est alors pas une regression du parseur, et les tests de
    conformite, eux, continuent de passer.
    """
    texte = _UNITE.read_text(encoding="utf-8")
    variantes = {
        "ordre des codes inverse": ("RestartPreventExitStatus=2 130",
                                    "RestartPreventExitStatus=130 2"),
        "duree en entier nu": ("TimeoutStopSec=90s", "TimeoutStopSec=90"),
        "specificateur systemd": ("Description=Boilerack",
                                  "Description=Boilerack %i"),
        "hardening en commentaire": (
            "[Install]", "# ProtectSystem=strict serait a evaluer\n[Install]"),
    }
    for nom, (avant, apres) in variantes.items():
        assert texte.count(avant) == 1, nom
        parseur = _analyser(texte.replace(avant, apres, 1))
        assert set(parseur.sections()) == {"Unit", "Service", "Install"}, nom

    # Les deux premieres variantes doivent en outre rester CONFORMES au contrat.
    inverse = _analyser(texte.replace("RestartPreventExitStatus=2 130",
                                      "RestartPreventExitStatus=130 2", 1))
    assert set(inverse["Service"]["RestartPreventExitStatus"].split()) == {"2", "130"}
    nu = _analyser(texte.replace("TimeoutStopSec=90s", "TimeoutStopSec=90", 1))
    assert _duree_en_secondes(nu["Service"]["TimeoutStopSec"]) == 90.0

    # La derniere ne doit pas etre prise pour une directive.
    commente = _analyser(texte.replace(
        "[Install]", "# ProtectSystem=strict serait a evaluer\n[Install]", 1))
    assert "ProtectSystem" not in commente["Service"]


def test_aucun_repertoire_d_etat_declare() -> None:
    """C12 §4.3 : rien n'est ecrit, donc rien n'est a declarer."""
    texte = _UNITE.read_text(encoding="utf-8")
    for interdit in ("StateDirectory", "CacheDirectory", "RuntimeDirectory",
                     "LogsDirectory", "WorkingDirectory"):
        assert interdit not in texte


def test_aucun_chemin_de_machine_de_developpement() -> None:
    texte = _UNITE.read_text(encoding="utf-8")
    for interdit in ("C:\\", "c:/", "/c/dev", "site-packages", ".venv", "src/boilerack"):
        assert interdit not in texte


# ---------------------------------------------------------------------------
# Commande de demarrage
# ---------------------------------------------------------------------------


def test_type_simple() -> None:
    assert _unite()["Service"]["Type"] == "simple"


def test_execstart_utilise_le_script_console_installe() -> None:
    """C12 §5 : le script installe, jamais `python -m`, et en chemin absolu."""
    argv = _unite()["Service"]["ExecStart"].split()
    assert argv[0] == _EXEC
    assert "-m" not in argv
    assert not any(a.endswith("python") or "python" in a for a in argv)


def test_execstart_fournit_explicitement_le_chemin_de_configuration() -> None:
    """C12 §5 : le programme ne cherche aucun emplacement, l'unite le transmet."""
    argv = _unite()["Service"]["ExecStart"].split()
    assert "--config" in argv
    assert argv[argv.index("--config") + 1] == _TOML


# ---------------------------------------------------------------------------
# Identite et secret
# ---------------------------------------------------------------------------


def test_le_service_ne_tourne_pas_en_root() -> None:
    service = _unite()["Service"]
    assert service["User"] == "boilerack"
    assert service["User"] != "root"
    assert service["Group"] == "boilerack"


def test_environment_file_exact_et_de_forme_STRICTE() -> None:
    """Arbitrage R2 : l'absence du fichier doit empecher le demarrage.

    La forme tolerante `-` ferait disparaitre le secret en silence si le chemin
    etait errone ou le fichier supprime. Elle est donc refusee.
    """
    valeur = _unite()["Service"]["EnvironmentFile"]
    assert valeur == _ENV
    assert not valeur.startswith("-"), "la forme tolerante est interdite par R2"


def test_aucun_secret_dans_le_gabarit() -> None:
    """C12 §6 : ni secret reel, ni factice, ni exemple qui y ressemble.

    Deux interdits distincts : `Environment=` inline, qui inscrirait le mot de
    passe dans un fichier lisible de tous, et toute AFFECTATION de la variable de
    secret. La seule mention tolerée est nominative, sans valeur.
    """
    texte = _UNITE.read_text(encoding="utf-8")
    assert "Environment=" not in texte
    assert re.search(r"BOILERACK_MQTT_PASSWORD\s*=", texte) is None


# ---------------------------------------------------------------------------
# Politique de redemarrage
# ---------------------------------------------------------------------------


def test_restart_on_failure() -> None:
    assert _unite()["Service"]["Restart"] == "on-failure"


def test_les_codes_2_et_130_sont_soustraits_au_redemarrage() -> None:
    """Arbitrage R1 : ni boucle sur `2`, ni relance sur `130`."""
    codes = set(_unite()["Service"]["RestartPreventExitStatus"].split())
    assert codes == {"2", "130"}


def test_le_code_130_n_est_pas_requalifie_en_succes() -> None:
    """Arbitrage R1 : l'interruption reste visible, elle ne devient pas un succes."""
    assert "SuccessExitStatus" not in _UNITE.read_text(encoding="utf-8")


def test_cadence_de_redemarrage_conforme() -> None:
    """C12 §8.3 : au-dessus du plancher issu de la limite de demarrage systemd."""
    secondes = _duree_en_secondes(_unite()["Service"]["RestartSec"])
    assert secondes == 10.0
    # Plancher documente : StartLimitIntervalSec / StartLimitBurst = 10 / 5.
    assert secondes >= 2.0


# ---------------------------------------------------------------------------
# Arret
# ---------------------------------------------------------------------------


def test_kill_signal_sigterm() -> None:
    """C12 §7 : tout C9 repose sur ce signal, il est rendu explicite."""
    assert _unite()["Service"]["KillSignal"] == "SIGTERM"


def test_timeout_stop_strictement_superieur_au_plancher_calcule() -> None:
    """C12 §10 : sous le plancher, `SIGKILL` couperait un cycle et `offline` ne
    serait jamais publie — le mensonge inverse de celui que C11 a corrige."""
    secondes = _duree_en_secondes(_unite()["Service"]["TimeoutStopSec"])
    assert secondes == 90.0
    assert secondes > _plancher_arret_s()


def test_le_plancher_est_bien_celui_du_contrat() -> None:
    """Verrouille le calcul : NEUF commandes distinctes x 5,0 s = 45 s.

    C12 le calculait sur huit mesures (40 s). §4.3 en ajoute deux, qui partagent
    une commande : le plancher passe donc a 45 s, non a 50 s. Il demeure sous le
    `TimeoutStopSec` de l'unite, qui n'a pas a bouger.
    """
    assert _plancher_arret_s() == 45.0


# ---------------------------------------------------------------------------
# Ordonnancement et installation
# ---------------------------------------------------------------------------


def test_ordonnancement_reseau() -> None:
    """C12 §9.1 : ordonne la pile reseau locale, ne promet aucun broker."""
    unit = _unite()["Unit"]
    assert unit["Wants"] == _CIBLE_RESEAU
    assert unit["After"] == _CIBLE_RESEAU


def test_cible_d_installation() -> None:
    assert _unite()["Install"]["WantedBy"] == "multi-user.target"


# ---------------------------------------------------------------------------
# Script console REELLEMENT installe
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def boilerack_installe(tmp_path_factory) -> pathlib.Path:
    """Installe le paquet dans un environnement jetable et rend le script console.

    **CETTE FIXTURE N'EST PAS HORS LIGNE.** L'installation passe par l'isolation
    de build PEP 517, qui recupere le backend declare — `hatchling` — depuis
    l'index des paquets s'il n'est pas deja disponible. Mesure a l'appui :
    `--no-build-isolation` echoue ici par `BackendUnavailable: Cannot import
    'hatchling.build'`, le backend n'etant ni installe ni declare en dependance
    de developpement. Un acces a l'index peut donc etre necessaire.

    `--no-deps` n'a pas pour objet de supprimer le reseau, mais d'eviter
    d'installer les dependances d'EXECUTION : les chemins exerces ici — `--help`
    et les erreurs de configuration — n'importent jamais Paho, dont l'import est
    differe a la construction du client MQTT.

    CE QUE CETTE PREUVE ETABLIT
        Que l'installation du paquet produit reellement la commande `boilerack`,
        et que cette commande INSTALLEE se comporte comme C10 le contracte. Ni
        une lecture de metadonnees, ni un `python -m`.

    CE QU'ELLE N'ETABLIT PAS
        Le comportement d'une installation complete avec ses dependances
        d'execution : Paho n'est pas installe ici, et aucun chemin qui en depend
        n'est exerce. C12 n'exige pas davantage.
    """
    racine = tmp_path_factory.mktemp("venv-c12")
    venv.create(racine, with_pip=True, clear=True)
    binaire = "Scripts" if sysconfig.get_platform().startswith("win") else "bin"
    python = racine / binaire / ("python.exe" if binaire == "Scripts" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", "--no-deps", str(_RACINE)],
        check=True, capture_output=True, timeout=600,
    )
    script = racine / binaire / ("boilerack.exe" if binaire == "Scripts" else "boilerack")
    assert script.is_file(), f"le script console n'a pas ete cree : {script}"
    return script


def test_l_installation_produit_la_commande(boilerack_installe) -> None:
    assert boilerack_installe.is_file()


def test_script_installe_aide_rend_zero(boilerack_installe) -> None:
    proc = subprocess.run(
        [str(boilerack_installe), "--help"], capture_output=True, text=True, timeout=120
    )
    assert proc.returncode == 0
    assert "--config" in proc.stdout


def test_script_installe_sans_configuration(boilerack_installe) -> None:
    proc = subprocess.run(
        [str(boilerack_installe)], capture_output=True, text=True, timeout=120
    )
    assert proc.returncode == CODE_CONFIGURATION


def test_script_installe_configuration_absente(boilerack_installe, tmp_path) -> None:
    proc = subprocess.run(
        [str(boilerack_installe), "--config", str(tmp_path / "nexiste.pas")],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == CODE_CONFIGURATION
    assert "configuration invalide" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_le_script_installe_n_est_pas_le_checkout(boilerack_installe) -> None:
    """Garde-fou : la preuve porte sur l'installation, pas sur le depot."""
    proc = subprocess.run(
        [str(boilerack_installe), "--config", "/nexiste/pas.toml"],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == CODE_CONFIGURATION
    assert str(_RACINE / "src") not in proc.stderr


# ---------------------------------------------------------------------------
# Non-regression des invariants C12
# ---------------------------------------------------------------------------


def test_aucun_emplacement_de_configuration_par_defaut() -> None:
    """C12 propriete 17 : la convention vit dans l'unite, jamais dans le code."""
    from boilerack.cli import build_parser

    action = {a.dest: a for a in build_parser()._actions}["config"]
    assert action.required is True
    assert action.default is None
    source = pathlib.Path(boilerack.cli.__file__).read_text(encoding="utf-8")
    assert "/etc/boilerack" not in source


def test_le_chargeur_ne_reference_aucun_chemin_d_exploitation() -> None:
    import boilerack.config as config_module

    source = pathlib.Path(config_module.__file__).read_text(encoding="utf-8")
    for interdit in ("/etc/", "/opt/", "boilerack.env"):
        assert interdit not in source


def test_une_seule_variable_d_environnement_reste_concernee() -> None:
    from boilerack.config import PASSWORD_ENV_VAR

    assert PASSWORD_ENV_VAR == "BOILERACK_MQTT_PASSWORD"
