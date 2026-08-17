"""Installateur Boilerack — noyau de surete (lot C13-B1).

Implemente `docs/design/c13-installation-contract.md`. Ce module ne fait rien
d'autre que **refuser** ce que le contrat interdit et **classer** ce qu'il
autorise. Les effets d'installation eux-memes relevent du lot suivant.

POURQUOI CE FICHIER EST A LA RACINE DU DEPOT
    Sur la cible, il s'execute AVANT que le venv existe (contrat §21) : depuis un
    checkout nu, `src/boilerack/` n'est pas importable sans manipuler
    `sys.path`. A la racine, il se lance par `python install.py`, sans artifice.
    Il reste ainsi hors du paquet, donc hors de la wheel — `[tool.hatch.build]`
    ne prend que `src/boilerack` — et hors du graphe d'import du runtime, ce qui
    rend la propriete P14 STRUCTURELLE plutot que surveillee.

BIBLIOTHEQUE STANDARD UNIQUEMENT
    Contrainte du contrat §21, et elle n'est pas esthetique : sur la cible,
    aucune dependance n'est installable avant que ce module ait fini son travail.

CE MODULE N'EXECUTE AUCUN ACTE SYSTEME
    Ni `systemctl`, ni `useradd`, ni `groupadd`, ni `chown`, ni `chmod`. Il
    n'importe meme pas `subprocess`. Les actes systeme sont DECLARES ; les actes
    humains restants sont RESTITUES. Contrat §8.2 et §13.

`main` REND UN ENTIER
    Comme la CLI du runtime, dont ce module reprend la grille de codes sans
    importer la moindre logique metier. Nuance identique et assumee : l'analyseur
    d'arguments leve `SystemExit` depuis l'interieur de `main` pour une option
    invalide (`2`) et pour `--help` (`0`). Ces sorties traversent volontairement.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Sequence

__all__ = [
    "ACTES_HUMAINS_DESINSTALLATION",
    "ACTES_HUMAINS_INSTALLATION",
    "CHEMIN_LIEN_ACTIVATION",
    "CODE_PANNE",
    "CODE_REFUS",
    "CODE_SUCCES",
    "FICHIERS_REQUIS_DU_CHECKOUT",
    "PYTHON_MINIMAL",
    "ActeSysteme",
    "Racine",
    "RefusPrecondition",
    "Resultat",
    "build_parser",
    "classer_racine",
    "desinstaller",
    "entree_existe",
    "installer",
    "main",
]

_PROG: Final = "install.py"

#: Grille reprise de la CLI du runtime (contrat §16), pas reinventee.
CODE_SUCCES: Final = 0
CODE_PANNE: Final = 1
CODE_REFUS: Final = 2

#: PC3. Le contrat parle de l'interpreteur qui creera le venv : c'est celui qui
#: execute ce module.
PYTHON_MINIMAL: Final = (3, 11)

#: PC4, liste FERMEE. Le contrat en nomme trois, ni plus ni moins ; en exiger
#: davantage serait durcir une precondition contractee.
FICHIERS_REQUIS_DU_CHECKOUT: Final = (
    "pyproject.toml",
    "systemd/boilerack.service",
    "docs/boilerack.example.toml",
)

#: Actes humains restants, contrat §8.2 et §13.1. `daemon-reload` est PREMIER :
#: l'unite fraichement deposee doit etre relue avant toute activation.
ACTES_HUMAINS_INSTALLATION: Final = (
    "systemctl daemon-reload",
    "systemctl enable boilerack.service",
    "systemctl start boilerack.service",
)
ACTES_HUMAINS_DESINSTALLATION: Final = ("systemctl daemon-reload",)

#: Contrat §12.3. Relatif a la racine, comme tous les emplacements de §7.
CHEMIN_LIEN_ACTIVATION: Final = (
    "etc/systemd/system/multi-user.target.wants/boilerack.service"
)

#: Commande humaine a indiquer lorsque la garde de §12.3 refuse.
_COMMANDE_DESACTIVATION: Final = "systemctl disable --now boilerack.service"


class RefusPrecondition(Exception):
    """Precondition non remplie : refus AVANT TOUT EFFET.

    Une seule categorie, sans hierarchie : l'appelant n'a qu'une decision a
    prendre — presenter un message nomme et rendre `CODE_REFUS`. Elle ne doit
    jamais envelopper une panne survenue APRES le debut des effets.
    """


@dataclass(frozen=True)
class ActeSysteme:
    """Acte privilegie, execute en mode reel et DECLARE en mode synthetique.

    Trois champs, aucune hierarchie, aucun executant embarque : le contrat §8.2
    demande que ces actes soient « observables, inspectables, non executes », pas
    qu'ils sachent s'appliquer eux-memes.
    """

    genre: str
    cible: str
    valeur: str


@dataclass(frozen=True)
class Racine:
    """Racine classee, telle que la contracte §8.1bis.

    `fournie` est ce que l'operateur a ecrit ; `resolue` est ce qui a ete
    resolu ; `designe_le_systeme` est le resultat de la comparaison d'IDENTITE
    de repertoire — jamais d'une comparaison de chaines.
    """

    fournie: Path
    resolue: Path
    designe_le_systeme: bool


@dataclass(frozen=True)
class Resultat:
    """Issue d'une operation. Les deux listes du contrat §8.2 y sont restituees."""

    code: int
    racine: Racine
    actes_systeme: tuple[ActeSysteme, ...]
    actes_humains: tuple[str, ...]
    messages: tuple[str, ...]


# ---------------------------------------------------------------------------
# Primitives de systeme de fichiers
# ---------------------------------------------------------------------------


def entree_existe(chemin: Path | str) -> bool:
    """Vrai si une entree existe a ce chemin, LIEN SYMBOLIQUE PENDANT COMPRIS.

    `Path.exists()` suit le lien et rend `False` sur un lien pendant. La garde
    du contrat §12.3 laisserait alors passer exactement le cas qu'elle doit
    arreter : un lien d'activation dont la cible a deja disparu reste une entree
    que systemd lira au prochain amorcage.
    """
    return os.path.lexists(chemin)


def _racine_systeme_par_defaut() -> Path:
    """Racine du systeme de fichiers de la machine courante.

    COUTURE PRIVEE : les tests peuvent substituer une racine de reference pour
    prouver la classification sans jamais toucher a la vraie. Elle n'est
    accessible par AUCUNE option de ligne de commande, AUCUNE variable
    d'environnement et AUCUNE cle de configuration — voir `build_parser`.
    """
    return Path(os.sep)


def classer_racine(racine: Path | str, racine_systeme: Path | None = None) -> Racine:
    """Classe une racine selon le contrat §8.1bis.

    Resolution d'abord — composantes `.` et `..` eliminees, liens symboliques
    traverses —, puis comparaison d'IDENTITE du repertoire designe. Une
    comparaison de chaines classerait « synthetiques » des representations qui
    designent pourtant la racine du systeme, et rouvrirait le defaut que cette
    clause ferme.

    Une racine INEXISTANTE ne designe pas la racine du systeme : celle-ci existe
    toujours. Ce n'est pas un repli silencieux mais la seule reponse vraie ; la
    precondition PC5 refusera ensuite cette racine pour son inexistence.
    """
    if racine_systeme is None:
        racine_systeme = _racine_systeme_par_defaut()
    fournie = Path(racine)
    resolue = fournie.resolve()
    try:
        designe = os.path.samefile(resolue, racine_systeme)
    except OSError:
        designe = False
    return Racine(fournie=fournie, resolue=resolue, designe_le_systeme=designe)


# ---------------------------------------------------------------------------
# Preconditions — contrat §5, evaluees AVANT TOUT EFFET
# ---------------------------------------------------------------------------


def _verifier_version_python(version: tuple[int, ...] | None = None) -> None:
    """PC3.

    `version` est injectable UNIQUEMENT pour que la suite puisse exercer le refus
    depuis un interpreteur qui, par construction, satisfait deja la borne.
    **Cela ne prouve rien d'une execution reelle sous un interpreteur ancien** —
    le contrat conserve cette inconnue en §5, et rien ici ne la leve.
    """
    courante = tuple(sys.version_info[:2]) if version is None else tuple(version[:2])
    if courante < PYTHON_MINIMAL:
        attendue = ".".join(str(n) for n in PYTHON_MINIMAL)
        trouvee = ".".join(str(n) for n in courante)
        raise RefusPrecondition(
            f"PC3 : Python {attendue} ou superieur est requis, trouve {trouvee}"
        )


def _verifier_combinaison(racine: Racine, actes_ouverts: bool) -> None:
    """PC2. Deux combinaisons admises, toutes les autres refusees."""
    if racine.designe_le_systeme and not actes_ouverts:
        raise RefusPrecondition(
            "PC2 : la racine designe la racine du systeme ; les actes systeme "
            "doivent alors etre explicitement autorises (--allow-system-acts)"
        )
    if not racine.designe_le_systeme and actes_ouverts:
        raise RefusPrecondition(
            "PC2 : la racine ne designe pas la racine du systeme ; les actes "
            "systeme ne peuvent pas etre autorises sur une racine synthetique"
        )


def _verifier_checkout(checkout: Path) -> None:
    """PC4. Les trois fichiers du contrat, ni plus ni moins."""
    if not checkout.is_dir():
        raise RefusPrecondition(f"PC4 : checkout introuvable : {checkout}")
    manquants = [
        nom for nom in FICHIERS_REQUIS_DU_CHECKOUT if not (checkout / nom).is_file()
    ]
    if manquants:
        raise RefusPrecondition(
            f"PC4 : checkout incomplet, fichier(s) absent(s) : {', '.join(manquants)}"
        )


def _verifier_racine_utilisable(racine: Racine) -> None:
    """PC5. La racine designee existe et est inscriptible."""
    if not racine.resolue.is_dir():
        raise RefusPrecondition(f"PC5 : racine introuvable : {racine.resolue}")
    if not os.access(racine.resolue, os.W_OK):
        raise RefusPrecondition(f"PC5 : racine non inscriptible : {racine.resolue}")


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def installer(
    checkout: Path | str,
    racine: Path | str,
    actes_ouverts: bool = False,
    racine_systeme: Path | None = None,
) -> Resultat:
    """Valide les preconditions de l'installation. NE PRODUIT AUCUN EFFET.

    Ordre imperatif du contrat §8.3, etape 1 : PC1 a PC5, PC6 en mode reel.
    PC1 est assuree en amont par l'analyseur d'arguments, qui rend `--root`
    obligatoire et sans defaut.

    LOT C13-B1 : les etapes 2 a 10 du contrat ne sont pas implementees. Cette
    fonction ne cree rien, ne copie rien, ne detruit rien. Le resultat le dit
    explicitement plutot que de laisser croire a une installation.
    """
    racine_classee = classer_racine(racine, racine_systeme)
    _verifier_combinaison(racine_classee, actes_ouverts)
    _verifier_version_python()
    _verifier_checkout(Path(checkout))
    _verifier_racine_utilisable(racine_classee)

    return Resultat(
        code=CODE_SUCCES,
        racine=racine_classee,
        actes_systeme=(),
        actes_humains=ACTES_HUMAINS_INSTALLATION,
        messages=(
            "preconditions satisfaites ; aucun effet n'a ete produit",
            "les effets d'installation relevent du lot suivant (contrat §8.3, "
            "etapes 2 a 10)",
        ),
    )


def desinstaller(
    racine: Path | str,
    actes_ouverts: bool = False,
    racine_systeme: Path | None = None,
) -> Resultat:
    """Valide les preconditions de la desinstallation. NE SUPPRIME RIEN.

    PC3 et PC4 ne sont pas evaluees : la desinstallation ne cree aucun venv et
    ne consomme aucun checkout. Les exiger durcirait des preconditions que le
    contrat rattache a l'installation.

    La garde de §12.3 est en revanche evaluee ici : c'est un refus AVANT TOUT
    EFFET, et un examen du systeme de fichiers, jamais un appel a `systemctl`.
    """
    racine_classee = classer_racine(racine, racine_systeme)
    _verifier_combinaison(racine_classee, actes_ouverts)
    _verifier_racine_utilisable(racine_classee)

    lien = racine_classee.resolue / CHEMIN_LIEN_ACTIVATION
    if entree_existe(lien):
        raise RefusPrecondition(
            f"l'unite parait activee : {lien} existe. Desactivez-la d'abord : "
            f"{_COMMANDE_DESACTIVATION}"
        )

    return Resultat(
        code=CODE_SUCCES,
        racine=racine_classee,
        actes_systeme=(),
        actes_humains=ACTES_HUMAINS_DESINSTALLATION,
        messages=(
            "preconditions satisfaites ; aucun effet n'a ete produit",
            "les effets de desinstallation relevent du lot suivant (contrat §12)",
        ),
    )


# ---------------------------------------------------------------------------
# Interface en ligne de commande
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Analyseur d'arguments. Aucun effet de bord.

    `--root` est OBLIGATOIRE et SANS DEFAUT sur les deux commandes : c'est la
    traduction de PC1, et la raison en est de surete, non de style — voir
    contrat §8.1. `--allow-system-acts` est le second bouton, ferme par defaut.

    AUCUNE OPTION N'EXPOSE LA RACINE SYSTEME DE REFERENCE. La couture qui permet
    aux tests d'en substituer une est un argument nomme des fonctions internes,
    volontairement absent de cette surface.
    """
    parser = argparse.ArgumentParser(
        prog=_PROG,
        description=(
            "Installateur Boilerack. Ne demarre jamais le service et n'execute "
            "jamais systemctl."
        ),
    )
    sous = parser.add_subparsers(dest="commande", required=True, metavar="COMMANDE")

    installation = sous.add_parser("install", help="installe Boilerack")
    installation.add_argument(
        "--checkout",
        required=True,
        metavar="CHEMIN",
        help="repertoire du checkout Boilerack (obligatoire)",
    )
    _ajouter_options_communes(installation)

    desinstallation = sous.add_parser("uninstall", help="desinstalle Boilerack")
    _ajouter_options_communes(desinstallation)

    return parser


def _ajouter_options_communes(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        required=True,
        metavar="CHEMIN",
        help=(
            "racine sous laquelle porter les effets (obligatoire ; aucune valeur "
            "par defaut, y compris vers la racine du systeme)"
        ),
    )
    parser.add_argument(
        "--allow-system-acts",
        action="store_true",
        help=(
            "autorise l'execution reelle des actes systeme privilegies ; "
            "admis uniquement lorsque la racine designe la racine du systeme"
        ),
    )


def main(argv: Sequence[str] | None = None, racine_systeme: Path | None = None) -> int:
    """Analyse, valide, rend le resultat logique. Ne quitte jamais le processus.

    `racine_systeme` est la couture privee de test decrite dans
    `_racine_systeme_par_defaut`. Elle n'est atteignable que par appel direct, et
    jamais depuis la ligne de commande.
    """
    arguments = build_parser().parse_args(argv)

    try:
        if arguments.commande == "install":
            resultat = installer(
                checkout=arguments.checkout,
                racine=arguments.root,
                actes_ouverts=arguments.allow_system_acts,
                racine_systeme=racine_systeme,
            )
        else:
            resultat = desinstaller(
                racine=arguments.root,
                actes_ouverts=arguments.allow_system_acts,
                racine_systeme=racine_systeme,
            )
    except RefusPrecondition as refus:
        # Pas de trace d'appels : la faute est dans l'invocation, une pile
        # designerait le code et n'apprendrait rien a qui tape une commande.
        print(f"{_PROG}: refus : {refus}", file=sys.stderr)
        return CODE_REFUS

    for message in resultat.messages:
        print(f"{_PROG}: {message}")
    if resultat.actes_systeme:
        print(f"{_PROG}: actes systeme declares, non executes :")
        for acte in resultat.actes_systeme:
            print(f"  {acte.genre} {acte.cible} {acte.valeur}")
    print(f"{_PROG}: actes humains restants, a executer vous-meme :")
    for commande in resultat.actes_humains:
        print(f"  {commande}")
    return resultat.code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
