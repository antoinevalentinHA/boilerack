"""Installateur Boilerack (lots C13-B1 et C13-B2).

Implemente `docs/design/c13-installation-contract.md` : le noyau de surete
— preconditions, classification de racine, refus avant tout effet — et les
effets contractes de l'installation et de la desinstallation.

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

AUCUN `systemctl`, DANS AUCUN MODE
    `subprocess` est importe pour une seule raison : lancer le `pip` DU VENV que
    l'installateur vient de creer. Aucune autre commande n'est lancee. Les
    commandes systemd sont des DONNEES restituees a l'humain, jamais executees.
    Contrat §13.

DEUX COUTURES, ET DEUX SEULEMENT
    `construire_venv` et `appliquer_actes` sont injectables. Ce ne sont pas des
    abstractions de confort : la premiere isole la seule etape couteuse et
    dependante d'un index de paquets, la seconde isole les seuls actes exigeant
    de vrais privileges. Sans elles, la suite ne pourrait ni s'executer hors
    ligne, ni prouver le mode reel sans creer d'utilisateur sur la machine de
    developpement. Elles n'ont ni hierarchie, ni registre, ni strategie.

`main` REND UN ENTIER
    Comme la CLI du runtime, dont ce module reprend la grille de codes sans
    importer la moindre logique metier. Nuances identiques et assumees :
    l'analyseur d'arguments leve `SystemExit` pour une option invalide (`2`) et
    pour `--help` (`0`) ; et une panne SURVENUE APRES les preconditions n'est pas
    traduite — elle remonte avec sa trace, et Python en fait un `1`.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import venv as _venv_stdlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final, Sequence

__all__ = [
    "ACTES_HUMAINS_DESINSTALLATION",
    "ACTES_HUMAINS_INSTALLATION",
    "CHEMIN_COMMANDE",
    "CHEMIN_CONFIG",
    "CHEMIN_ETC",
    "CHEMIN_LIEN_ACTIVATION",
    "CHEMIN_OPT",
    "CHEMIN_REPERTOIRE_UNITES",
    "CHEMIN_SECRET",
    "CHEMIN_UNITE",
    "CHEMIN_VENV",
    "CODE_PANNE",
    "CODE_REFUS",
    "CODE_SUCCES",
    "FICHIERS_REQUIS_DU_CHECKOUT",
    "GROUPE",
    "METADONNEES_GROUPE_A",
    "METADONNEES_GROUPE_B",
    "MODELE_ENVIRONNEMENT",
    "PYTHON_MINIMAL",
    "REPERTOIRES_HORS_VENV",
    "SOURCE_CONFIG",
    "SOURCE_UNITE",
    "UTILISATEUR",
    "ActeSysteme",
    "Racine",
    "RefusPrecondition",
    "Resultat",
    "build_parser",
    "classer_racine",
    "construire_venv_reel",
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

#: Sources de copie dans le checkout (contrat §8.4).
SOURCE_UNITE: Final = "systemd/boilerack.service"
SOURCE_CONFIG: Final = "docs/boilerack.example.toml"

#: Emplacements du contrat §7, RELATIFS a la racine. Les chemins absolus de C12
#: sont obtenus en prenant la racine `/`.
CHEMIN_OPT: Final = "opt/boilerack"
CHEMIN_VENV: Final = "opt/boilerack/venv"
CHEMIN_COMMANDE: Final = "opt/boilerack/venv/bin/boilerack"
CHEMIN_ETC: Final = "etc/boilerack"
CHEMIN_CONFIG: Final = "etc/boilerack/boilerack.toml"
CHEMIN_SECRET: Final = "etc/boilerack/boilerack.env"
CHEMIN_REPERTOIRE_UNITES: Final = "etc/systemd/system"
CHEMIN_UNITE: Final = "etc/systemd/system/boilerack.service"

#: Contrat §8.3 etape 3. Le venv n'y figure pas : il est cree a l'etape 8.
REPERTOIRES_HORS_VENV: Final = (CHEMIN_OPT, CHEMIN_ETC, CHEMIN_REPERTOIRE_UNITES)

#: Identite dediee et non privilegiee (C12 §4.2, contrat §8.2).
UTILISATEUR: Final = "boilerack"
GROUPE: Final = "boilerack"

#: Contrat §7.3, groupe A : pose AVANT l'etape venv.
METADONNEES_GROUPE_A: Final = (
    (CHEMIN_OPT, "root:root", "0755"),
    (CHEMIN_ETC, "root:boilerack", "0750"),
    (CHEMIN_CONFIG, "root:boilerack", "0640"),
    (CHEMIN_SECRET, "root:boilerack", "0640"),
    (CHEMIN_UNITE, "root:root", "0644"),
)

#: Contrat §7.3, groupe B : pose APRES la creation reussie du venv.
#:
#: LES MODES SONT REPRIS TELS QUE LE CONTRAT LES ECRIT, en toutes lettres. C12
#: §4.1 dit « lecture pour tous » et « executable » ; ni C12 ni C13 ne fixent de
#: valeur numerique pour ces deux emplacements. En inventer une ici serait
#: fabriquer une regle que le corpus ne porte pas. La consequence est assumee et
#: visible : `_appliquer_actes_reels` REFUSE un mode non numerique, de sorte que
#: le manque se signale au lieu de se combler tout seul.
METADONNEES_GROUPE_B: Final = (
    (CHEMIN_VENV, "root", "lecture pour tous"),
    (CHEMIN_COMMANDE, "root", "executable"),
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

#: Modele du fichier d'environnement, INLINE et non versionne (contrat §10.1,
#: clause 6). Il ne definit AUCUNE variable : la seule ligne qui nomme le secret
#: est un commentaire, sans valeur. Contrat §10.1, clauses 2, 3 et 4.
MODELE_ENVIRONNEMENT: Final = """\
# Environnement d'exploitation Boilerack.
#
# Ce fichier est ATTENDU par l'unite systemd : son absence empeche le
# demarrage (voir docs/design/c12-service-contract.md, §6).
#
# Il ne definit AUCUNE variable par defaut, et son CONTENU n'est JAMAIS
# ecrase par une reinstallation.
#
# Si le broker MQTT exige un mot de passe, decommentez la ligne suivante et
# renseignez-la. Sinon, laissez-la telle quelle : la variable est
# optionnelle, c'est le fichier qui est obligatoire.
#
# BOILERACK_MQTT_PASSWORD=
"""


class RefusPrecondition(Exception):
    """Precondition non remplie : refus AVANT TOUT EFFET.

    Une seule categorie, sans hierarchie : l'appelant n'a qu'une decision a
    prendre — presenter un message nomme et rendre `CODE_REFUS`. Elle ne doit
    jamais envelopper une panne survenue APRES le debut des effets ; une telle
    panne remonte telle quelle et devient un `1`.
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


def _inscriptible(chemin: Path) -> bool:
    """Couture minimale : les tests substituent ce predicat.

    `os.access` ne rend pas un verdict fiable sous Windows, ou les droits ne se
    modelisent pas comme un bit d'ecriture POSIX. Fabriquer un repertoire
    reellement non inscriptible pour eprouver PC5 serait donc soit impossible,
    soit une simulation deguisee. Substituer ce PREDICAT expose exactement ce que
    le test veut eprouver — le refus et son absence d'effet — sans pretendre
    reproduire une permission POSIX.
    """
    return os.access(chemin, os.W_OK)


def _verifier_racine_utilisable(racine: Racine) -> None:
    """PC5. La racine designee existe et est inscriptible."""
    if not racine.resolue.is_dir():
        raise RefusPrecondition(f"PC5 : racine introuvable : {racine.resolue}")
    if not _inscriptible(racine.resolue):
        raise RefusPrecondition(f"PC5 : racine non inscriptible : {racine.resolue}")


# ---------------------------------------------------------------------------
# Coutures : construction du venv, application des actes systeme
# ---------------------------------------------------------------------------


def construire_venv_reel(venv: Path, checkout: Path) -> None:
    """Cree le venv puis y installe Boilerack depuis le checkout.

    **CETTE ETAPE N'EST PAS HORS LIGNE.** `pip` recupere le moteur de
    construction declare — `hatchling` — et la dependance d'execution depuis un
    index si elle ne sont pas deja disponibles. Le contrat le dit en §15.2, et
    la fixture C12 avait deja mesure ce fait.

    Le seul processus lance est le `python` DU VENV que cette fonction vient de
    creer. Aucun `systemctl`, aucun `useradd`, aucune autre commande.
    """
    _venv_stdlib.create(venv, with_pip=True, clear=True)
    binaire = "Scripts" if os.name == "nt" else "bin"
    python = venv / binaire / ("python.exe" if os.name == "nt" else "python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", str(checkout)],
        check=True,
        capture_output=True,
        timeout=900,
    )


def _appliquer_actes_reels(actes: Sequence[ActeSysteme], racine: Path) -> None:
    """Applique les actes systeme. MODE REEL UNIQUEMENT — jamais exerce ici.

    Fonction volontairement mince : elle n'est couverte par aucun test, et cela
    est declare plutot que masque. C'est la raison de la garder inspectable et
    sans branche superflue. Contrat §20 : `useradd`, `chown` et les modes reels
    appartiennent a la qualification terrain.

    Elle REFUSE un mode non numerique. Les deux emplacements du groupe B portent
    un mode ecrit en toutes lettres, faute de valeur numerique dans le corpus
    (voir `METADONNEES_GROUPE_B`) : le manque se signale ici au lieu d'etre
    comble par une valeur inventee.
    """
    for acte in actes:  # pragma: no cover - mode reel, jamais exerce hors terrain
        if acte.genre == "groupe":
            subprocess.run(["groupadd", "--system", acte.cible], check=False)
        elif acte.genre == "utilisateur":
            subprocess.run(
                ["useradd", "--system", "--no-create-home", "--shell",
                 "/usr/sbin/nologin", "--gid", GROUPE, acte.cible],
                check=False,
            )
        elif acte.genre == "proprietaire":
            shutil.chown(racine / acte.cible, *_proprietaire(acte.valeur))
        elif acte.genre == "mode":
            if not acte.valeur.isdigit():
                raise NotImplementedError(
                    f"mode non numerique pour {acte.cible} : {acte.valeur!r}. "
                    "Ni C12 ni C13 n'en fixent la valeur ; elle doit etre "
                    "arbitree avant toute application reelle."
                )
            os.chmod(racine / acte.cible, int(acte.valeur, 8))
        else:
            raise ValueError(f"genre d'acte inconnu : {acte.genre!r}")


def _proprietaire(valeur: str) -> tuple[str, str | None]:  # pragma: no cover
    """Decoupe `user` ou `user:group`."""
    if ":" in valeur:
        utilisateur, groupe = valeur.split(":", 1)
        return utilisateur, groupe
    return valeur, None


# ---------------------------------------------------------------------------
# Effets
# ---------------------------------------------------------------------------


def _actes_de_metadonnees(table: Sequence[tuple[str, str, str]]) -> list[ActeSysteme]:
    """Traduit une table de §7 en actes, proprietaire d'abord puis mode."""
    actes: list[ActeSysteme] = []
    for cible, proprietaire, mode in table:
        actes.append(ActeSysteme(genre="proprietaire", cible=cible, valeur=proprietaire))
        actes.append(ActeSysteme(genre="mode", cible=cible, valeur=mode))
    return actes


def installer(
    checkout: Path | str,
    racine: Path | str,
    actes_ouverts: bool = False,
    racine_systeme: Path | None = None,
    construire_venv: Callable[[Path, Path], None] = construire_venv_reel,
    appliquer_actes: Callable[[Sequence[ActeSysteme], Path], None] | None = None,
    version_python: tuple[int, ...] | None = None,
) -> Resultat:
    """Installe Boilerack sous `racine`, dans l'ordre exact du contrat §8.3.

    Toutes les preconditions passent AVANT le moindre effet. Ensuite seulement,
    et dans cet ordre : identite, repertoires hors venv, configuration si
    absente, secret si absent, unite, metadonnees du groupe A, **venv detruit
    puis recree**, metadonnees du groupe B, restitution.

    L'etape venv est la SEULE etape destructive, et la DERNIERE : seules la pose
    des metadonnees du groupe B et la restitution la suivent, et ni l'une ni
    l'autre ne detruit quoi que ce soit.

    Aucune exception survenue apres les preconditions n'est traduite : elle
    remonte avec sa trace, et l'appelant en fait un `1` (contrat §16). Il n'y a
    ni rollback, ni transaction : le contrat n'en demande aucun, et §11.2 assume
    explicitement l'etat residuel d'un echec tardif.
    """
    # --- Preconditions : aucun effet ---------------------------------------
    racine_classee = classer_racine(racine, racine_systeme)
    _verifier_combinaison(racine_classee, actes_ouverts)
    _verifier_version_python(version_python)
    checkout = Path(checkout)
    _verifier_checkout(checkout)
    _verifier_racine_utilisable(racine_classee)

    # --- FRONTIERE : les effets commencent ici -----------------------------
    base = racine_classee.resolue
    if appliquer_actes is None:
        appliquer_actes = _appliquer_actes_reels
    messages: list[str] = []

    # 2. Identite. En mode synthetique elle est DECLAREE, jamais creee.
    actes: list[ActeSysteme] = [
        ActeSysteme(genre="groupe", cible=GROUPE, valeur="cree si absent"),
        ActeSysteme(genre="utilisateur", cible=UTILISATEUR, valeur="cree si absent"),
    ]

    # 3. Repertoires hors venv.
    for relatif in REPERTOIRES_HORS_VENV:
        (base / relatif).mkdir(parents=True, exist_ok=True)

    # 4 et 5. Contenus de l'exploitant : deposes SI ABSENTS SEULEMENT.
    messages.append(
        _deposer_si_absent(
            base / CHEMIN_CONFIG, (checkout / SOURCE_CONFIG).read_bytes(), "configuration"
        )
    )
    messages.append(
        _deposer_si_absent(
            base / CHEMIN_SECRET, MODELE_ENVIRONNEMENT.encode("utf-8"), "environnement"
        )
    )

    # 6. Unite : TOUJOURS redeposee, copie octet pour octet du checkout.
    (base / CHEMIN_UNITE).write_bytes((checkout / SOURCE_UNITE).read_bytes())

    # 7. Metadonnees du groupe A.
    actes.extend(_actes_de_metadonnees(METADONNEES_GROUPE_A))
    if actes_ouverts:
        appliquer_actes(tuple(actes), base)

    # 8. SEULE ETAPE DESTRUCTIVE : le venv est detruit puis recree.
    venv = base / CHEMIN_VENV
    if venv.exists():
        shutil.rmtree(venv)
    construire_venv(venv, checkout)

    # 9. Metadonnees du groupe B, apres creation reussie du venv.
    actes_b = _actes_de_metadonnees(METADONNEES_GROUPE_B)
    actes.extend(actes_b)
    if actes_ouverts:
        appliquer_actes(tuple(actes_b), base)

    # 10. Restitution.
    messages.append(
        "la configuration deposee est un EXEMPLE : relisez-la avant tout demarrage"
    )
    return Resultat(
        code=CODE_SUCCES,
        racine=racine_classee,
        actes_systeme=tuple(actes),
        actes_humains=ACTES_HUMAINS_INSTALLATION,
        messages=tuple(messages),
    )


def _deposer_si_absent(cible: Path, contenu: bytes, quoi: str) -> str:
    """Ecrit `contenu` seulement si `cible` est absente. Rend un message.

    PRESERVER N'EST PAS ECHOUER (contrat §9.2) : trouver le fichier en place est
    une issue NORMALE, signalee et rendue avec un succes. Seules les METADONNEES
    sont ensuite reappliquees (contrat §9.1) ; le contenu, lui, n'est ni ecrase,
    ni fusionne, ni corrige.
    """
    if entree_existe(cible):
        return f"{quoi} existante preservee : {cible}"
    cible.write_bytes(contenu)
    return f"{quoi} initiale deposee : {cible}"


def desinstaller(
    racine: Path | str,
    actes_ouverts: bool = False,
    racine_systeme: Path | None = None,
) -> Resultat:
    """Desinstalle Boilerack. Supprime le programme, preserve l'exploitant.

    Supprime `/opt/boilerack` — venv compris — et l'unite. **Preserve**
    `/etc/boilerack/`, la configuration, le secret, l'utilisateur et le groupe :
    contrat §12.1 et §12.2, ou la troisieme raison est decisive — un GID libere
    pourrait etre reattribue et rendre le secret lisible.

    PC3 et PC4 ne sont pas evaluees : la desinstallation ne cree aucun venv et ne
    consomme aucun checkout. Les exiger durcirait des preconditions que le
    contrat rattache a l'installation.

    Idempotente : une seconde execution ne trouve rien a supprimer et reussit.
    """
    racine_classee = classer_racine(racine, racine_systeme)
    _verifier_combinaison(racine_classee, actes_ouverts)
    _verifier_racine_utilisable(racine_classee)

    base = racine_classee.resolue
    lien = base / CHEMIN_LIEN_ACTIVATION
    if entree_existe(lien):
        raise RefusPrecondition(
            f"l'unite parait activee : {lien} existe. Desactivez-la d'abord : "
            f"{_COMMANDE_DESACTIVATION}"
        )

    # --- FRONTIERE : les effets commencent ici -----------------------------
    messages: list[str] = []
    opt = base / CHEMIN_OPT
    if opt.exists():
        shutil.rmtree(opt)
        messages.append(f"programme supprime : {opt}")
    else:
        messages.append(f"rien a supprimer : {opt} est absent")

    unite = base / CHEMIN_UNITE
    if entree_existe(unite):
        unite.unlink()
        messages.append(f"unite supprimee : {unite}")
    else:
        messages.append(f"rien a supprimer : {unite} est absente")

    messages.append(
        f"preserves : {base / CHEMIN_ETC}, sa configuration, son secret, "
        f"l'utilisateur et le groupe {UTILISATEUR}"
    )
    return Resultat(
        code=CODE_SUCCES,
        racine=racine_classee,
        actes_systeme=(),
        actes_humains=ACTES_HUMAINS_DESINSTALLATION,
        messages=tuple(messages),
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


def main(
    argv: Sequence[str] | None = None,
    racine_systeme: Path | None = None,
    construire_venv: Callable[[Path, Path], None] = construire_venv_reel,
    appliquer_actes: Callable[[Sequence[ActeSysteme], Path], None] | None = None,
) -> int:
    """Analyse, valide, agit, rend le resultat logique. Ne quitte jamais le processus.

    `racine_systeme`, `construire_venv` et `appliquer_actes` sont les coutures
    privees decrites en tete de module. Aucune n'est atteignable depuis la ligne
    de commande.
    """
    arguments = build_parser().parse_args(argv)

    try:
        if arguments.commande == "install":
            resultat = installer(
                checkout=arguments.checkout,
                racine=arguments.root,
                actes_ouverts=arguments.allow_system_acts,
                racine_systeme=racine_systeme,
                construire_venv=construire_venv,
                appliquer_actes=appliquer_actes,
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
        etiquette = "executes" if arguments.allow_system_acts else "declares, non executes"
        print(f"{_PROG}: actes systeme {etiquette} :")
        for acte in resultat.actes_systeme:
            print(f"  {acte.genre} {acte.cible} {acte.valeur}")
    print(f"{_PROG}: actes humains restants, a executer vous-meme :")
    for commande in resultat.actes_humains:
        print(f"  {commande}")
    return resultat.code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
