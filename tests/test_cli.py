"""Tests du point d'entree C10 — `boilerack.cli` et `boilerack.__main__`.

Aucun broker, aucun `vclient`, aucun `vcontrold`, aucune chaudiere. Le cycle de
vie est remplace par un double partout ou son execution n'est pas l'objet du
test ; le seul sous-processus lance est un interpreteur Python.
"""

from __future__ import annotations

import ast
import inspect
import logging
import pathlib
import socket
import subprocess
import sys

import pytest

import boilerack.cli
from boilerack.cli import CODE_CONFIGURATION, LOG_LEVELS, build_parser, main
from boilerack.config import PASSWORD_ENV_VAR, ConfigurationError
from boilerack.runtime import RuntimeConfig

MINIMALE = """
[mqtt]
host = "broker.exemple.invalid"

[vclient]
executable = "vclient"
"""


@pytest.fixture(autouse=True)
def sans_secret(monkeypatch):
    monkeypatch.delenv(PASSWORD_ENV_VAR, raising=False)


@pytest.fixture(autouse=True)
def journalisation_restauree():
    """Rend au logger racine son etat exact apres chaque test.

    `main()` prend possession de la journalisation, et la reconfiguration forcee
    **retire et ferme** les gestionnaires existants — y compris ceux de pytest.
    Sans cette fixture, un test contaminerait les suivants.
    """
    racine = logging.getLogger()
    anciens = racine.handlers[:]
    niveau = racine.level
    yield
    for handler in racine.handlers[:]:
        racine.removeHandler(handler)
    for handler in anciens:
        racine.addHandler(handler)
    racine.setLevel(niveau)


@pytest.fixture
def config_valide(tmp_path):
    chemin = tmp_path / "boilerack.toml"
    chemin.write_text(MINIMALE, encoding="utf-8")
    return chemin


@pytest.fixture
def lifecycle_double(monkeypatch):
    """Remplace `run_lifecycle` : rien n'est jamais demarre.

    Rend un objet portant les appels recus et le resultat a produire.
    """

    class _Double:
        def __init__(self) -> None:
            self.appels: list[RuntimeConfig] = []
            self.resultat = 0
            self.action = None

        def __call__(self, config, **kwargs):
            self.appels.append(config)
            if self.action is not None:
                self.action()
            return self.resultat

    double = _Double()
    monkeypatch.setattr(boilerack.cli, "run_lifecycle", double)
    return double


# ---------------------------------------------------------------------------
# Analyseur d'arguments
# ---------------------------------------------------------------------------


def test_help_sort_en_zero(capsys) -> None:
    with pytest.raises(SystemExit) as capture:
        main(["--help"])
    assert capture.value.code == 0
    assert "--config" in capsys.readouterr().out


def test_config_absent_est_une_erreur_d_usage(capsys) -> None:
    with pytest.raises(SystemExit) as capture:
        main([])
    assert capture.value.code == CODE_CONFIGURATION
    assert "--config" in capsys.readouterr().err


def test_option_inconnue(capsys) -> None:
    with pytest.raises(SystemExit) as capture:
        main(["--config", "x", "--inconnu"])
    assert capture.value.code == CODE_CONFIGURATION
    capsys.readouterr()


def test_niveau_de_journalisation_invalide(capsys) -> None:
    with pytest.raises(SystemExit) as capture:
        main(["--config", "x", "--log-level", "TRACE"])
    assert capture.value.code == CODE_CONFIGURATION
    assert "invalid choice" in capsys.readouterr().err


def test_les_cinq_niveaux_sont_acceptes(config_valide, lifecycle_double) -> None:
    for niveau in LOG_LEVELS:
        assert main(["--config", str(config_valide), "--log-level", niveau]) == 0
    assert len(lifecycle_double.appels) == len(LOG_LEVELS)


def test_aucun_chemin_de_configuration_par_defaut() -> None:
    """`--config` n'a aucun defaut : Boilerack ne cherche pas sa configuration."""
    action = {a.dest: a for a in build_parser()._actions}["config"]
    assert action.required is True
    assert action.default is None


def test_le_jeu_de_niveaux_est_ferme() -> None:
    action = {a.dest: a for a in build_parser()._actions}["log_level"]
    assert tuple(action.choices) == LOG_LEVELS
    assert action.default == "INFO"


# ---------------------------------------------------------------------------
# Configuration et resultats
# ---------------------------------------------------------------------------


def test_configuration_valide_appelle_le_cycle_de_vie(config_valide, lifecycle_double) -> None:
    assert main(["--config", str(config_valide)]) == 0
    assert len(lifecycle_double.appels) == 1
    assert isinstance(lifecycle_double.appels[0], RuntimeConfig)
    assert lifecycle_double.appels[0].mqtt.host == "broker.exemple.invalid"


def test_resultat_zero_projete(config_valide, lifecycle_double) -> None:
    lifecycle_double.resultat = 0
    assert main(["--config", str(config_valide)]) == 0


def test_resultat_130_projete(config_valide, lifecycle_double) -> None:
    """`SIGINT` : le resultat logique de C9 traverse sans etre traduit."""
    lifecycle_double.resultat = 130
    assert main(["--config", str(config_valide)]) == 130


def test_erreur_de_configuration_rend_deux_sans_trace(tmp_path, capsys) -> None:
    mauvais = tmp_path / "mauvais.toml"
    mauvais.write_text('[mqtt]\nhost = "b"\nhots = 1\n[vclient]\nexecutable = "v"\n', encoding="utf-8")
    code = main(["--config", str(mauvais)])
    capture = capsys.readouterr()
    assert code == CODE_CONFIGURATION
    assert "configuration invalide" in capture.err
    assert "[mqtt].hots" in capture.err
    assert "Traceback" not in capture.err
    assert capture.out == ""


def test_fichier_absent_rend_deux(tmp_path, capsys) -> None:
    code = main(["--config", str(tmp_path / "nexiste.pas")])
    assert code == CODE_CONFIGURATION
    assert "introuvable" in capsys.readouterr().err


def test_le_secret_n_apparait_dans_aucun_message(tmp_path, capsys, monkeypatch) -> None:
    secret = "mot-de-passe-de-test"
    monkeypatch.setenv(PASSWORD_ENV_VAR, secret)
    mauvais = tmp_path / "mauvais.toml"
    mauvais.write_text('[mqtt]\nhost = ""\n[vclient]\nexecutable = "v"\n', encoding="utf-8")
    main(["--config", str(mauvais)])
    capture = capsys.readouterr()
    assert secret not in capture.err
    assert secret not in capture.out


def test_une_panne_du_cycle_de_vie_n_est_pas_convertie(
    config_valide, lifecycle_double, capsys
) -> None:
    """Une exception d'execution garde son identite et n'est jamais un code 2."""
    origine = OSError("broker injoignable")

    def lever():
        raise origine

    lifecycle_double.action = lever
    with pytest.raises(OSError) as capture:
        main(["--config", str(config_valide)])
    assert capture.value is origine
    assert "configuration invalide" not in capsys.readouterr().err


def test_un_exception_group_traverse_intact(config_valide, lifecycle_double) -> None:
    groupe = ExceptionGroup("echecs", [OSError("a"), RuntimeError("b")])

    def lever():
        raise groupe

    lifecycle_double.action = lever
    with pytest.raises(ExceptionGroup) as capture:
        main(["--config", str(config_valide)])
    assert capture.value is groupe


def test_le_cycle_de_vie_n_est_pas_entoure_d_un_gestionnaire() -> None:
    """Verifie sur l'AST : aucun `try` n'enveloppe l'appel au cycle de vie."""
    arbre = ast.parse(inspect.getsource(main))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Try):
            interieur = ast.unparse(noeud)
            assert "run_lifecycle" not in interieur, (
                "run_lifecycle ne doit jamais etre enveloppe : une panne serait "
                "traduite en erreur de configuration"
            )


def test_seule_l_erreur_de_configuration_est_attrapee() -> None:
    arbre = ast.parse(inspect.getsource(main))
    attrapes = [
        ast.unparse(gestionnaire.type)
        for noeud in ast.walk(arbre)
        if isinstance(noeud, ast.Try)
        for gestionnaire in noeud.handlers
        if gestionnaire.type is not None
    ]
    assert attrapes == ["ConfigurationError"]


# ---------------------------------------------------------------------------
# Journalisation
# ---------------------------------------------------------------------------


def test_l_import_ne_configure_rien() -> None:
    """Importer la CLI ne doit toucher a rien dans le processus hote."""
    arbre = ast.parse(pathlib.Path(boilerack.cli.__file__).read_text(encoding="utf-8"))
    for noeud in arbre.body:
        assert isinstance(
            noeud,
            (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef, ast.Assign,
             ast.AnnAssign, ast.Expr),
        ), ast.dump(noeud)
        if isinstance(noeud, ast.Expr):
            assert isinstance(noeud.value, ast.Constant)


def test_l_import_seul_n_installe_aucun_gestionnaire() -> None:
    racine = logging.getLogger()
    avant = racine.handlers[:]
    import importlib

    importlib.import_module("boilerack.cli")
    assert racine.handlers == avant


def test_main_applique_le_niveau_demande(config_valide, lifecycle_double) -> None:
    main(["--config", str(config_valide), "--log-level", "WARNING"])
    assert logging.getLogger().level == logging.WARNING


def test_un_second_appel_remplace_le_niveau(config_valide, lifecycle_double) -> None:
    """La configuration simplifiee est un no-op si la racine a deja un
    gestionnaire : sans reconfiguration forcee, le second niveau serait ignore."""
    main(["--config", str(config_valide), "--log-level", "WARNING"])
    assert logging.getLogger().level == logging.WARNING
    main(["--config", str(config_valide), "--log-level", "DEBUG"])
    assert logging.getLogger().level == logging.DEBUG


def test_le_niveau_par_defaut_est_info(config_valide, lifecycle_double) -> None:
    main(["--config", str(config_valide)])
    assert logging.getLogger().level == logging.INFO


def test_la_journalisation_va_sur_stderr(config_valide, lifecycle_double) -> None:
    main(["--config", str(config_valide)])
    handlers = logging.getLogger().handlers
    assert len(handlers) == 1
    assert getattr(handlers[0], "stream", None) is sys.stderr


def test_le_format_porte_horodatage_niveau_logger_et_message(
    config_valide, lifecycle_double
) -> None:
    main(["--config", str(config_valide)])
    gabarit = logging.getLogger().handlers[0].formatter._fmt
    for element in ("%(asctime)s", "%(levelname)s", "%(name)s", "%(message)s"):
        assert element in gabarit


def test_aucune_dependance_de_journalisation() -> None:
    source = pathlib.Path(boilerack.cli.__file__).read_text(encoding="utf-8")
    for interdit in ("colorama", "rich", "coloredlogs", "structlog", "json.dumps"):
        assert interdit not in source


# ---------------------------------------------------------------------------
# Frontieres
# ---------------------------------------------------------------------------


def test_aucune_io_infrastructure_avant_le_cycle_de_vie(
    config_valide, lifecycle_double, monkeypatch
) -> None:
    """Le double n'ouvre rien : tout ce qui precede ne doit rien ouvrir non plus."""

    def interdit(*args, **kwargs):
        raise AssertionError("entree-sortie d'infrastructure avant run_lifecycle")

    monkeypatch.setattr(socket, "socket", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)
    monkeypatch.setattr(subprocess, "run", interdit)
    monkeypatch.setattr(subprocess, "Popen", interdit)

    assert main(["--config", str(config_valide)]) == 0
    assert len(lifecycle_double.appels) == 1


def test_le_module_n_importe_rien_hors_stdlib_et_boilerack() -> None:
    arbre = ast.parse(pathlib.Path(boilerack.cli.__file__).read_text(encoding="utf-8"))
    modules = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            modules |= {alias.name.split(".")[0] for alias in noeud.names}
        elif isinstance(noeud, ast.ImportFrom) and noeud.module:
            modules.add(noeud.module.split(".")[0])
    hors = sorted(m for m in modules if m not in sys.stdlib_module_names and m != "boilerack")
    assert hors == []


# ---------------------------------------------------------------------------
# `__main__` et packaging
# ---------------------------------------------------------------------------


def test_main_module_ne_porte_aucune_logique() -> None:
    """`__main__.py` delegue et projette, rien de plus."""
    import boilerack

    chemin = pathlib.Path(boilerack.__file__).with_name("__main__.py")
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    formes = [type(noeud).__name__ for noeud in arbre.body]
    assert formes == ["Expr", "ImportFrom", "Raise"], formes
    assert "main()" in ast.unparse(arbre.body[-1])
    for interdit in ("argparse", "logging", "load_config", "run_lifecycle", "if "):
        assert interdit not in chemin.read_text(encoding="utf-8")


def test_python_m_boilerack_help() -> None:
    """Le second chemin de lancement, exerce dans un vrai processus."""
    racine = pathlib.Path(boilerack.cli.__file__).parents[2]
    proc = subprocess.run(
        [sys.executable, "-m", "boilerack", "--help"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(racine),
    )
    assert proc.returncode == 0
    assert "--config" in proc.stdout
    assert "--log-level" in proc.stdout


def test_python_m_boilerack_config_absent(tmp_path) -> None:
    racine = pathlib.Path(boilerack.cli.__file__).parents[2]
    proc = subprocess.run(
        [sys.executable, "-m", "boilerack", "--config", str(tmp_path / "nexiste.pas")],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(racine),
    )
    assert proc.returncode == CODE_CONFIGURATION
    assert "configuration invalide" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_python_m_boilerack_sans_argument() -> None:
    racine = pathlib.Path(boilerack.cli.__file__).parents[2]
    proc = subprocess.run(
        [sys.executable, "-m", "boilerack"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(racine),
    )
    assert proc.returncode == CODE_CONFIGURATION


def test_le_paquet_importe_est_bien_celui_du_depot() -> None:
    """Garde-fou du test en sous-processus : sinon il pourrait viser un autre
    Boilerack installe ailleurs."""
    racine = pathlib.Path(boilerack.cli.__file__).parents[2]
    proc = subprocess.run(
        [sys.executable, "-c", "import boilerack.cli as m; print(m.__file__)"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(racine),
    )
    assert proc.returncode == 0
    assert pathlib.Path(proc.stdout.strip()) == pathlib.Path(boilerack.cli.__file__)


def test_le_script_installe_est_declare() -> None:
    """`[project.scripts]` pointe la meme `main` que `python -m`."""
    import tomllib

    racine = pathlib.Path(boilerack.cli.__file__).parents[2]
    pyproject = tomllib.loads((racine / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"]["scripts"]
    assert scripts == {"boilerack": "boilerack.cli:main"}

    module, _, fonction = scripts["boilerack"].partition(":")
    import importlib

    assert getattr(importlib.import_module(module), fonction) is main


def test_aucune_dependance_ajoutee() -> None:
    import tomllib

    racine = pathlib.Path(boilerack.cli.__file__).parents[2]
    pyproject = tomllib.loads((racine / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["dependencies"] == ["paho-mqtt>=2.1,<3"]
    # B1 : `ruff` rejoint l'extra de developpement. La garde reste une egalite
    # STRICTE — c'est elle qui interdit l'ajout silencieux d'une dependance.
    assert pyproject["project"]["optional-dependencies"] == {
        "dev": ["mypy>=2.3", "pytest>=8", "ruff>=0.16"]
    }
