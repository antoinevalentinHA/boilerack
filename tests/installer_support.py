"""Outillage des tests de l'installateur (lot C13-B1).

Trois services, et rien de plus :

- charger `install.py`, qui n'est PAS un module du paquet Boilerack ;
- photographier une arborescence pour prouver l'absence d'effet ;
- neutraliser toute fonction d'effet reel pour prouver qu'aucune n'est appelee.

AUCUNE RACINE REELLE N'EST TOUCHEE. Toutes les racines manipulees ici sont des
repertoires temporaires fournis par pytest.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import pathlib
import shutil
import sys
from types import ModuleType

RACINE_DEPOT = pathlib.Path(__file__).resolve().parents[1]
CHEMIN_INSTALLATEUR = RACINE_DEPOT / "install.py"


def charger_installateur() -> ModuleType:
    """Charge `install.py` par son chemin, sans passer par le chemin d'import.

    C'est la seule facon correcte de l'atteindre : il vit a la racine du depot,
    hors de `src/boilerack/`, precisement pour rester absent du graphe d'import
    du runtime (propriete P14). L'importer par `import install` supposerait qu'il
    soit sur `sys.path`, ce que rien ne garantit et que rien ne doit garantir.
    """
    nom = "boilerack_installateur_sous_test"
    specification = importlib.util.spec_from_file_location(nom, CHEMIN_INSTALLATEUR)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    # ENREGISTREMENT AVANT EXECUTION, et non par confort : `dataclasses` resout
    # les annotations via `sys.modules[cls.__module__]`. Sans cette ligne, la
    # premiere classe decoree echoue par `AttributeError` sur un module absent.
    sys.modules[nom] = module
    specification.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Empreinte d'arborescence
# ---------------------------------------------------------------------------


def empreinte(racine: pathlib.Path) -> tuple[tuple[str, str, int, str], ...]:
    """Photographie une arborescence, de facon a rendre tout effet detectable.

    Pour chaque entree : chemin relatif en notation POSIX, genre, taille et
    empreinte du contenu. Les liens symboliques sont decrits par leur CIBLE et
    ne sont jamais suivis — sans quoi un lien pendant serait invisible, et un
    lien reoriente passerait pour inchange.

    Le tri rend la comparaison independante de l'ordre de parcours du systeme de
    fichiers.
    """
    entrees: list[tuple[str, str, int, str]] = []
    for repertoire, sous_repertoires, fichiers in os.walk(racine, followlinks=False):
        base = pathlib.Path(repertoire)
        for nom in list(sous_repertoires) + list(fichiers):
            chemin = base / nom
            relatif = chemin.relative_to(racine).as_posix()
            if chemin.is_symlink():
                cible = os.readlink(chemin)
                entrees.append((relatif, "lien", len(cible), cible))
            elif chemin.is_dir():
                entrees.append((relatif, "repertoire", 0, ""))
            else:
                donnees = chemin.read_bytes()
                entrees.append(
                    (relatif, "fichier", len(donnees), hashlib.sha256(donnees).hexdigest())
                )
    return tuple(sorted(entrees))


# ---------------------------------------------------------------------------
# Racine systeme de reference
# ---------------------------------------------------------------------------


def racine_systeme_factice(base: pathlib.Path) -> pathlib.Path:
    """Cree une racine tenant lieu de racine du systeme pour les tests.

    Elle n'est JAMAIS `/`. Elle est passee aux fonctions de l'installateur par
    l'argument nomme prevu a cet effet, qui n'est expose par aucune option de
    ligne de commande. Le sous-repertoire `opt` sert a construire l'alias `..`.
    """
    racine = base / "racine_systeme_factice"
    (racine / "opt").mkdir(parents=True, exist_ok=True)
    return racine


# ---------------------------------------------------------------------------
# Neutralisation des effets reels
# ---------------------------------------------------------------------------

#: Fonctions capables de modifier le systeme de fichiers ou l'identite. Le lot
#: C13-B1 ne doit en appeler AUCUNE : il refuse ou il valide, il n'agit pas.
_EFFETS_REELS = (
    (os, "mkdir"),
    (os, "makedirs"),
    (os, "remove"),
    (os, "unlink"),
    (os, "rmdir"),
    (os, "rename"),
    (os, "replace"),
    (os, "symlink"),
    (os, "chmod"),
    (os, "chown"),
    (os, "system"),
    (shutil, "copy"),
    (shutil, "copy2"),
    (shutil, "copyfile"),
    (shutil, "copytree"),
    (shutil, "rmtree"),
    (shutil, "move"),
    (pathlib.Path, "mkdir"),
    (pathlib.Path, "touch"),
    (pathlib.Path, "unlink"),
    (pathlib.Path, "rmdir"),
    (pathlib.Path, "rename"),
    (pathlib.Path, "replace"),
    (pathlib.Path, "symlink_to"),
    (pathlib.Path, "write_text"),
    (pathlib.Path, "write_bytes"),
    (pathlib.Path, "chmod"),
)


def interdire_tout_effet(monkeypatch) -> None:
    """Fait echouer bruyamment toute tentative d'effet reel.

    `os.chown` n'existe pas sous Windows et `getattr` le confirme avant de tenter
    la substitution : la neutralisation couvre ce qui existe sur la plateforme
    courante, et ne pretend pas couvrir davantage.
    """
    for cible, nom in _EFFETS_REELS:
        if getattr(cible, nom, None) is None:
            continue

        def _interdit(*_args, _nom=nom, **_kwargs):
            raise AssertionError(
                f"effet reel interdit dans ce lot : {_nom} a ete appele"
            )

        monkeypatch.setattr(cible, nom, _interdit, raising=False)


def interdire_tout_sous_processus(monkeypatch) -> None:
    """Fait echouer toute tentative de lancer un processus externe.

    Complementaire de la preuve statique : celle-ci verifie que la source ne
    nomme aucun `systemctl` hors des constantes d'actes humains, celle-la verifie
    qu'aucun chemin d'execution n'en lance un par une voie detournee.
    """
    import subprocess

    def _fabriquer(nom: str):
        def _interdit(*_args, **_kwargs):
            raise AssertionError(f"sous-processus interdit dans ce lot : {nom} appele")

        return _interdit

    for nom in ("run", "call", "check_call", "check_output", "Popen"):
        monkeypatch.setattr(subprocess, nom, _fabriquer(f"subprocess.{nom}"), raising=False)
    monkeypatch.setattr(os, "system", _fabriquer("os.system"), raising=False)
    monkeypatch.setattr(os, "execv", _fabriquer("os.execv"), raising=False)


def liens_symboliques_disponibles(base: pathlib.Path) -> bool:
    """Mesure, plutot que suppose, si la plateforme permet d'en creer un.

    Sous Windows, la creation d'un lien symbolique exige un privilege que la
    machine de developpement n'accorde pas necessairement. Les tests qui en
    dependent sont alors ecartes explicitement, jamais silencieusement.
    """
    cible = base / "_sonde_cible"
    cible.mkdir(exist_ok=True)
    sonde = base / "_sonde_lien"
    try:
        os.symlink(cible, sonde, target_is_directory=True)
    except (OSError, NotImplementedError, AttributeError):
        return False
    try:
        os.remove(sonde)
    except OSError:
        os.rmdir(sonde)
    return True
