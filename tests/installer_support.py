"""Outillage des tests de l'installateur (lots C13-B1 et C13-B2).

Quatre services, et rien de plus :

- charger `install.py`, qui n'est PAS un module du paquet Boilerack ;
- photographier une arborescence, METADONNEES COMPRISES, pour prouver l'absence
  d'effet et la pose des permissions ;
- doubler les deux coutures de l'installateur — construction du venv et
  application des actes systeme ;
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
# Empreinte d'arborescence — contenu ET metadonnees
# ---------------------------------------------------------------------------


def empreinte(racine: pathlib.Path) -> tuple[tuple[str, str, str, int, str], ...]:
    """Photographie une arborescence, de facon a rendre tout effet detectable.

    Pour chaque entree : chemin relatif en notation POSIX, genre, **mode**,
    taille et empreinte du contenu.

    LE MODE EST INCLUS DEPUIS C13-B2. Sans lui, un `chmod` execute en mode
    synthetique — la mutation M8 — passerait inapercu sur les plateformes ou il
    a un effet. Sa lecture reste indicative sous Windows, ou les permissions ne
    se modelisent pas en bits POSIX ; la comparaison avant/apres reste valide
    puisqu'elle porte sur la meme plateforme.

    Les liens symboliques sont decrits par leur CIBLE et ne sont jamais suivis —
    sans quoi un lien pendant serait invisible, et un lien reoriente passerait
    pour inchange.
    """
    entrees: list[tuple[str, str, str, int, str]] = []
    for repertoire, sous_repertoires, fichiers in os.walk(racine, followlinks=False):
        base = pathlib.Path(repertoire)
        for nom in list(sous_repertoires) + list(fichiers):
            chemin = base / nom
            relatif = chemin.relative_to(racine).as_posix()
            if chemin.is_symlink():
                cible = os.readlink(chemin)
                entrees.append((relatif, "lien", "-", len(cible), cible))
                continue
            mode = oct(chemin.stat().st_mode & 0o7777)
            if chemin.is_dir():
                entrees.append((relatif, "repertoire", mode, 0, ""))
            else:
                donnees = chemin.read_bytes()
                entrees.append(
                    (relatif, "fichier", mode, len(donnees),
                     hashlib.sha256(donnees).hexdigest())
                )
    return tuple(sorted(entrees))


def contenus(racine: pathlib.Path) -> dict[str, str]:
    """Empreintes des seuls CONTENUS, sans metadonnee ni genre.

    Utile la ou le contrat distingue explicitement les deux : le contenu de la
    configuration et du secret est souverain, leurs metadonnees ne le sont pas.
    """
    return {
        entree[0]: entree[4] for entree in empreinte(racine) if entree[1] == "fichier"
    }


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
# Double de la couture de construction du venv
# ---------------------------------------------------------------------------


class DoubleVenv:
    """Remplace la construction reelle du venv, et photographie l'instant.

    Il n'imite pas `venv.create` : il enregistre ce qui lui a ete demande,
    PHOTOGRAPHIE la racine au moment precis de son appel — ce qui est la seule
    facon de prouver l'ordre des effets du contrat §8.3 —, puis depose un
    squelette minimal correspondant aux emplacements du groupe B.

    `echouer=True` simule un echec de l'etape 8, pour eprouver l'etat residuel
    contracte en §11.2.
    """

    def __init__(
        self,
        racine: pathlib.Path,
        echouer: bool = False,
        squelette: bool = True,
    ) -> None:
        self.racine = racine
        self.echouer = echouer
        self.squelette = squelette
        self.appels: list[tuple[pathlib.Path, pathlib.Path]] = []
        self.empreinte_a_l_appel: tuple | None = None
        self.contenus_a_l_appel: dict[str, str] | None = None

    def __call__(self, venv: pathlib.Path, checkout: pathlib.Path) -> None:
        self.appels.append((venv, checkout))
        self.empreinte_a_l_appel = empreinte(self.racine)
        self.contenus_a_l_appel = contenus(self.racine)
        if self.echouer:
            raise RuntimeError("construction du venv en echec (simulee)")
        if self.squelette:
            (venv / "bin").mkdir(parents=True, exist_ok=True)
            (venv / "bin" / "boilerack").write_bytes(b"#!squelette\n")
            (venv / "pyvenv.cfg").write_bytes(b"squelette = oui\n")

    @property
    def appele(self) -> bool:
        return bool(self.appels)


class DoubleActes:
    """Remplace l'application reelle des actes systeme. N'execute rien.

    Le mode reel du contrat exige `groupadd`, `useradd`, `chown` et `chmod`.
    Aucun test ne doit les declencher sur la machine de developpement : ce double
    enregistre ce qui aurait ete applique, et dans quel ordre.
    """

    def __init__(self) -> None:
        self.lots: list[tuple[object, ...]] = []

    def __call__(self, actes, racine: pathlib.Path) -> None:
        self.lots.append(tuple(actes))

    @property
    def appliques(self) -> tuple:
        return tuple(acte for lot in self.lots for acte in lot)


# ---------------------------------------------------------------------------
# Neutralisation des effets reels
# ---------------------------------------------------------------------------

#: Actes systeme que le mode synthetique ne doit JAMAIS executer, et primitives
#: d'execution de processus. Contrairement au lot B1, les primitives d'ecriture
#: ordinaires ne figurent plus ici : C13-B2 ecrit legitimement sous la racine
#: synthetique.
_ACTES_SYSTEME_INTERDITS = (
    (os, "chmod"),
    (os, "chown"),
    (os, "lchown"),
    (shutil, "chown"),
)


def interdire_les_actes_systeme(monkeypatch) -> None:
    """Fait echouer bruyamment tout `chmod`/`chown` reel.

    `os.chown` n'existe pas sous Windows et `getattr` le confirme avant de tenter
    la substitution : la neutralisation couvre ce qui existe sur la plateforme
    courante, et ne pretend pas couvrir davantage.
    """
    for cible, nom in _ACTES_SYSTEME_INTERDITS:
        if getattr(cible, nom, None) is None:
            continue

        def _interdit(*_args, _nom=nom, **_kwargs):
            raise AssertionError(
                f"acte systeme interdit en mode synthetique : {_nom} a ete appele"
            )

        monkeypatch.setattr(cible, nom, _interdit, raising=False)


def interdire_toute_ecriture(monkeypatch) -> None:
    """Fait echouer toute tentative d'ecriture. Reserve aux chemins de REFUS.

    Utilise la ou le contrat exige qu'aucun effet ne soit produit : un refus de
    precondition ne doit atteindre aucune de ces primitives.
    """
    for cible, nom in (
        (os, "mkdir"), (os, "makedirs"), (os, "remove"), (os, "unlink"),
        (os, "rmdir"), (os, "rename"), (os, "replace"), (os, "symlink"),
        (os, "chmod"), (os, "chown"),
        (shutil, "copy"), (shutil, "copy2"), (shutil, "copyfile"),
        (shutil, "copytree"), (shutil, "rmtree"), (shutil, "move"), (shutil, "chown"),
        (pathlib.Path, "mkdir"), (pathlib.Path, "touch"), (pathlib.Path, "unlink"),
        (pathlib.Path, "rmdir"), (pathlib.Path, "rename"), (pathlib.Path, "replace"),
        (pathlib.Path, "symlink_to"), (pathlib.Path, "write_text"),
        (pathlib.Path, "write_bytes"), (pathlib.Path, "chmod"),
    ):
        if getattr(cible, nom, None) is None:
            continue

        def _interdit(*_args, _nom=nom, **_kwargs):
            raise AssertionError(f"effet reel interdit sur ce chemin : {_nom} appele")

        monkeypatch.setattr(cible, nom, _interdit, raising=False)


class EspionProcessus:
    """Enregistre tout lancement de processus au lieu de l'executer."""

    def __init__(self) -> None:
        self.commandes: list[list[str]] = []

    def run(self, args, *_reste, **_kwargs):
        self.commandes.append([str(a) for a in args])

        class _Termine:
            returncode = 0
            stdout = b""
            stderr = b""

        return _Termine()

    @property
    def executables(self) -> set[str]:
        return {commande[0] for commande in self.commandes if commande}


def espionner_les_processus(monkeypatch) -> EspionProcessus:
    """Substitue un espion a toute primitive capable de lancer un processus."""
    espion = EspionProcessus()
    monkeypatch.setattr(subprocess_module(), "run", espion.run, raising=False)

    def _interdit(*_args, **_kwargs):
        raise AssertionError("primitive de lancement de processus interdite")

    for nom in ("call", "check_call", "check_output", "Popen"):
        monkeypatch.setattr(subprocess_module(), nom, _interdit, raising=False)
    monkeypatch.setattr(os, "system", _interdit, raising=False)
    return espion


def subprocess_module():
    import subprocess

    return subprocess


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
