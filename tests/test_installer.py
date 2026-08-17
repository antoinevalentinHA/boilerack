"""Tests du noyau de surete de l'installateur (lot C13-B1).

Ce module prouve ce que l'installateur REFUSE, et que ses refus sont sans effet.
Il ne prouve aucune installation : les effets relevent du lot suivant.

AUCUNE RACINE REELLE
    Toutes les racines sont des repertoires temporaires. La racine du systeme
    n'est jamais touchee : les tests substituent une racine de reference par
    l'argument nomme prevu a cet effet, qui n'est expose par aucune option de
    ligne de commande.

CE QUE CES TESTS NE PROUVENT PAS
    Aucun `useradd`, `chown`, `chmod` ni systemd reel n'est exerce ; aucune
    conformite terrain n'est revendiquee. Le contrat range ces preuves en §20.
    En particulier, l'injection de version de §« Python » n'est PAS une execution
    sous un interpreteur ancien : elle exerce le refus, pas son declencheur reel.

PROPRIETE DE LOT, NON CONTRACTUELLE
    Dans C13-B1, une combinaison ADMISE ne produit elle non plus aucun effet,
    puisque les etapes 2 a 10 du contrat ne sont pas implementees. Les tests le
    disent la ou ils s'en servent : cette absence d'effet disparaitra en B2, et
    ne doit pas etre lue comme une propriete du contrat.
"""

from __future__ import annotations

import argparse
import ast
import os
import pathlib
import sys
import tomllib

import pytest

from tests.installer_support import (
    CHEMIN_INSTALLATEUR,
    RACINE_DEPOT,
    charger_installateur,
    empreinte,
    interdire_tout_effet,
    interdire_tout_sous_processus,
    liens_symboliques_disponibles,
    racine_systeme_factice,
)

install = charger_installateur()


# ---------------------------------------------------------------------------
# Montage commun
# ---------------------------------------------------------------------------


@pytest.fixture
def systeme(tmp_path: pathlib.Path) -> pathlib.Path:
    """Racine tenant lieu de racine du systeme. N'est jamais `/`."""
    return racine_systeme_factice(tmp_path)


@pytest.fixture
def synthetique(tmp_path: pathlib.Path) -> pathlib.Path:
    """Racine synthetique ordinaire, distincte de la racine de reference."""
    racine = tmp_path / "racine_synthetique"
    racine.mkdir()
    return racine


@pytest.fixture
def checkout(tmp_path: pathlib.Path) -> pathlib.Path:
    """Checkout minimal conforme a PC4 : les trois fichiers requis, et rien d'autre."""
    base = tmp_path / "checkout"
    for nom in install.FICHIERS_REQUIS_DU_CHECKOUT:
        chemin = base / nom
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(b"contenu factice\n")
    return base


def _peupler(racine: pathlib.Path) -> None:
    """Depose de quoi rendre visible le moindre effet parasite sur la racine."""
    (racine / "temoin").mkdir(exist_ok=True)
    (racine / "temoin" / "fichier.txt").write_bytes(b"temoin\n")


# ---------------------------------------------------------------------------
# Classification de racine — contrat §8.1bis
# ---------------------------------------------------------------------------


def test_racine_de_reference_est_classee_reelle(systeme: pathlib.Path) -> None:
    assert install.classer_racine(systeme, systeme).designe_le_systeme is True


def test_racine_synthetique_est_classee_synthetique(
    systeme: pathlib.Path, synthetique: pathlib.Path
) -> None:
    assert install.classer_racine(synthetique, systeme).designe_le_systeme is False


def test_alias_point_designe_la_racine_du_systeme(systeme: pathlib.Path) -> None:
    """M23 : `<racine>/.` s'ecrit autrement et designe la meme chose."""
    assert install.classer_racine(systeme / ".", systeme).designe_le_systeme is True


def test_alias_point_point_designe_la_racine_du_systeme(systeme: pathlib.Path) -> None:
    """M23 : `<racine>/opt/..` remonte sur la racine du systeme."""
    alias = systeme / "opt" / ".."
    assert install.classer_racine(alias, systeme).designe_le_systeme is True


def test_lien_symbolique_vers_la_racine_du_systeme_est_classe_reel(
    tmp_path: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M23, variante lien symbolique. Ecartee explicitement si la plateforme la refuse."""
    if not liens_symboliques_disponibles(tmp_path):
        pytest.skip("creation de lien symbolique indisponible sur cette plateforme")
    lien = tmp_path / "lien_vers_systeme"
    lien.symlink_to(systeme, target_is_directory=True)
    assert install.classer_racine(lien, systeme).designe_le_systeme is True


def test_la_classification_n_est_pas_une_comparaison_de_chaines(
    systeme: pathlib.Path,
) -> None:
    """Des ecritures textuellement differentes designent la meme racine.

    Fait mesure, et non suppose : `pathlib` elimine une composante `.` DES LA
    CONSTRUCTION du chemin, si bien que cet alias-la n'atteint jamais la
    resolution. `..` en revanche subsiste, parce qu'il ne peut pas etre elimine
    lexicalement en presence de liens symboliques : lui exige une resolution
    reelle. Les deux sont testes, mais seul `..` eprouve la resolution.
    """
    ecrites = [str(systeme), f"{systeme}{os.sep}.", f"{systeme}{os.sep}opt{os.sep}.."]
    assert len(set(ecrites)) == 3, "les trois ecritures doivent bien differer"

    assert str(pathlib.Path(ecrites[1])) == str(systeme), "pathlib absorbe le point"
    assert str(pathlib.Path(ecrites[2])) != str(systeme), "le double point subsiste"

    assert all(install.classer_racine(e, systeme).designe_le_systeme for e in ecrites)


def test_racine_inexistante_ne_designe_pas_la_racine_du_systeme(
    tmp_path: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Une racine absente ne peut pas etre la racine du systeme, qui existe toujours."""
    absente = tmp_path / "nexiste" / "pas"
    assert install.classer_racine(absente, systeme).designe_le_systeme is False


def test_la_source_ne_compare_pas_la_racine_a_une_chaine() -> None:
    """M23 / M24 : aucune comparaison textuelle a la racine dans le code."""
    source = CHEMIN_INSTALLATEUR.read_text(encoding="utf-8")
    for motif in ('== "/"', "== '/'", '!= "/"', "!= '/'", 'startswith("/")'):
        assert motif not in source, f"comparaison textuelle de racine : {motif}"


# ---------------------------------------------------------------------------
# Combinaisons admises et refusees — contrat §8.1, PC2
# ---------------------------------------------------------------------------


def test_synthetique_avec_actes_fermes_est_admise(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    resultat = install.installer(
        checkout=checkout,
        racine=synthetique,
        actes_ouverts=False,
        racine_systeme=systeme,
    )
    assert resultat.code == install.CODE_SUCCES
    assert resultat.racine.designe_le_systeme is False


def test_reference_avec_actes_ouverts_est_admise(
    checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """La seconde combinaison admise, exercee sur la racine de REFERENCE, jamais `/`."""
    resultat = install.installer(
        checkout=checkout, racine=systeme, actes_ouverts=True, racine_systeme=systeme
    )
    assert resultat.code == install.CODE_SUCCES
    assert resultat.racine.designe_le_systeme is True


def test_reference_avec_actes_fermes_est_refusee(
    checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M21 : c'est le vecteur destructeur exact ferme par la correction N1."""
    _peupler(systeme)
    avant = empreinte(systeme)
    with pytest.raises(install.RefusPrecondition) as refus:
        install.installer(
            checkout=checkout, racine=systeme, actes_ouverts=False, racine_systeme=systeme
        )
    assert "PC2" in str(refus.value)
    assert empreinte(systeme) == avant


def test_synthetique_avec_actes_ouverts_est_refusee(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M22 : ouvrir les actes systeme sur une racine synthetique ruinerait P8."""
    _peupler(synthetique)
    avant = empreinte(synthetique)
    with pytest.raises(install.RefusPrecondition) as refus:
        install.installer(
            checkout=checkout,
            racine=synthetique,
            actes_ouverts=True,
            racine_systeme=systeme,
        )
    assert "PC2" in str(refus.value)
    assert empreinte(synthetique) == avant


def test_alias_de_la_racine_de_reference_avec_actes_fermes_est_refuse(
    checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M23 par le refus : une ecriture alternative ne contourne pas PC2."""
    _peupler(systeme)
    avant = empreinte(systeme)
    for alias in (systeme / ".", systeme / "opt" / ".."):
        with pytest.raises(install.RefusPrecondition) as refus:
            install.installer(
                checkout=checkout,
                racine=alias,
                actes_ouverts=False,
                racine_systeme=systeme,
            )
        assert "PC2" in str(refus.value)
    assert empreinte(systeme) == avant


def test_les_quatre_combinaisons_sont_traitees_sans_exception(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Enumeration close : deux admises, deux refusees, aucune issue tierce."""
    attendu = {
        (True, True): "admise",
        (True, False): "refusee",
        (False, True): "refusee",
        (False, False): "admise",
    }
    obtenu = {}
    for reelle, racine in ((True, systeme), (False, synthetique)):
        for ouverts in (True, False):
            try:
                install.installer(
                    checkout=checkout,
                    racine=racine,
                    actes_ouverts=ouverts,
                    racine_systeme=systeme,
                )
                obtenu[(reelle, ouverts)] = "admise"
            except install.RefusPrecondition:
                obtenu[(reelle, ouverts)] = "refusee"
    assert obtenu == attendu


# ---------------------------------------------------------------------------
# Preconditions restantes — PC3, PC4, PC5
# ---------------------------------------------------------------------------


def test_python_trop_ancien_est_refuse() -> None:
    """M7, part prouvable.

    L'injection exerce le REFUS. Elle ne prouve PAS une execution sous un
    interpreteur ancien : la suite ne s'execute que sur `>= 3.11`, et le contrat
    conserve cette inconnue en §5.
    """
    with pytest.raises(install.RefusPrecondition) as refus:
        install._verifier_version_python((3, 9))
    assert "PC3" in str(refus.value)


def test_python_courant_est_accepte() -> None:
    assert sys.version_info[:2] >= install.PYTHON_MINIMAL
    install._verifier_version_python()


def test_checkout_absent_est_refuse_sans_effet(
    tmp_path: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    _peupler(synthetique)
    avant = empreinte(synthetique)
    with pytest.raises(install.RefusPrecondition) as refus:
        install.installer(
            checkout=tmp_path / "nexiste_pas",
            racine=synthetique,
            racine_systeme=systeme,
        )
    assert "PC4" in str(refus.value)
    assert empreinte(synthetique) == avant


@pytest.mark.parametrize("manquant", ["pyproject.toml", "systemd/boilerack.service",
                                      "docs/boilerack.example.toml"])
def test_checkout_incomplet_est_refuse_sans_effet(
    manquant: str,
    checkout: pathlib.Path,
    synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """M14 : chacun des trois fichiers de PC4 est individuellement necessaire."""
    (checkout / manquant).unlink()
    _peupler(synthetique)
    avant = empreinte(synthetique)
    with pytest.raises(install.RefusPrecondition) as refus:
        install.installer(
            checkout=checkout, racine=synthetique, racine_systeme=systeme
        )
    assert "PC4" in str(refus.value)
    assert manquant in str(refus.value)
    assert empreinte(synthetique) == avant


def test_pc4_n_exige_pas_plus_que_le_contrat() -> None:
    """Le contrat en nomme trois. En exiger davantage durcirait une precondition."""
    assert install.FICHIERS_REQUIS_DU_CHECKOUT == (
        "pyproject.toml",
        "systemd/boilerack.service",
        "docs/boilerack.example.toml",
    )


def test_le_depot_lui_meme_satisfait_pc4() -> None:
    """Garde-fou : la precondition doit accepter le checkout reel de Boilerack."""
    install._verifier_checkout(RACINE_DEPOT)


def test_racine_inexistante_est_refusee(
    checkout: pathlib.Path, tmp_path: pathlib.Path, systeme: pathlib.Path
) -> None:
    with pytest.raises(install.RefusPrecondition) as refus:
        install.installer(
            checkout=checkout,
            racine=tmp_path / "nexiste" / "pas",
            racine_systeme=systeme,
        )
    assert "PC5" in str(refus.value)


# ---------------------------------------------------------------------------
# Refus AVANT TOUT EFFET — contrat §5 et §8.3 etape 1
# ---------------------------------------------------------------------------


def test_aucun_effet_reel_n_est_invoque_sur_les_chemins_de_ce_lot(
    monkeypatch,
    checkout: pathlib.Path,
    synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """Toute fonction capable de modifier le disque est rendue explosive.

    Couvre les chemins admis comme les chemins refuses : dans ce lot, aucun ne
    doit atteindre la moindre ecriture.
    """
    _peupler(synthetique)
    interdire_tout_effet(monkeypatch)
    interdire_tout_sous_processus(monkeypatch)

    install.installer(checkout=checkout, racine=synthetique, racine_systeme=systeme)
    install.desinstaller(racine=synthetique, racine_systeme=systeme)
    with pytest.raises(install.RefusPrecondition):
        install.installer(
            checkout=checkout,
            racine=synthetique,
            actes_ouverts=True,
            racine_systeme=systeme,
        )
    with pytest.raises(install.RefusPrecondition):
        install.installer(
            checkout=checkout, racine=systeme, actes_ouverts=False, racine_systeme=systeme
        )


def test_une_combinaison_admise_ne_produit_pas_encore_d_effet(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """PROPRIETE DE LOT, NON CONTRACTUELLE : elle disparaitra en C13-B2."""
    _peupler(synthetique)
    avant = empreinte(synthetique)
    resultat = install.installer(
        checkout=checkout, racine=synthetique, racine_systeme=systeme
    )
    assert resultat.code == install.CODE_SUCCES
    assert empreinte(synthetique) == avant


def test_le_resultat_ne_pretend_pas_avoir_installe(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Pas de mensonge d'etat : un succes de lot n'est pas une installation."""
    resultat = install.installer(
        checkout=checkout, racine=synthetique, racine_systeme=systeme
    )
    assert resultat.actes_systeme == ()
    assert any("aucun effet" in message for message in resultat.messages)


# ---------------------------------------------------------------------------
# Garde d'activation — contrat §12.3
# ---------------------------------------------------------------------------


def test_desinstallation_refuse_si_un_fichier_occupe_le_chemin_d_activation(
    synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M12, cas du fichier ordinaire."""
    lien = synthetique / install.CHEMIN_LIEN_ACTIVATION
    lien.parent.mkdir(parents=True)
    lien.write_bytes(b"")
    avant = empreinte(synthetique)
    with pytest.raises(install.RefusPrecondition) as refus:
        install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert "systemctl disable" in str(refus.value)
    assert empreinte(synthetique) == avant


def test_desinstallation_refuse_sur_un_lien_symbolique_pendant(
    tmp_path: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """La garde doit voir une entree PENDANTE : `Path.exists()` rendrait `False`."""
    if not liens_symboliques_disponibles(tmp_path):
        pytest.skip("creation de lien symbolique indisponible sur cette plateforme")
    lien = synthetique / install.CHEMIN_LIEN_ACTIVATION
    lien.parent.mkdir(parents=True)
    lien.symlink_to(synthetique / "cible" / "absente.service")

    assert lien.exists() is False, "la cible doit bien etre absente"
    assert install.entree_existe(lien) is True

    avant = empreinte(synthetique)
    with pytest.raises(install.RefusPrecondition):
        install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert empreinte(synthetique) == avant


def test_desinstallation_admise_sans_lien_d_activation(
    synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    resultat = install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert resultat.code == install.CODE_SUCCES


def test_la_garde_n_utilise_pas_une_primitive_qui_suit_les_liens() -> None:
    """Verrouille le choix de primitive : `lexists`, jamais `exists`."""
    source = CHEMIN_INSTALLATEUR.read_text(encoding="utf-8")
    assert "os.path.lexists" in source


# ---------------------------------------------------------------------------
# Actes systeme et actes humains — contrat §8.2
# ---------------------------------------------------------------------------


def test_les_actes_humains_de_l_installation_sont_les_trois_du_contrat() -> None:
    """M16 : `daemon-reload` est PREMIER, et les trois sont restitues."""
    assert install.ACTES_HUMAINS_INSTALLATION == (
        "systemctl daemon-reload",
        "systemctl enable boilerack.service",
        "systemctl start boilerack.service",
    )


def test_les_actes_humains_de_la_desinstallation(
    synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    resultat = install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert resultat.actes_humains == ("systemctl daemon-reload",)


def test_le_modele_d_acte_reste_minimal() -> None:
    """Ni hierarchie, ni moteur d'execution : trois champs et rien d'autre."""
    acte = install.ActeSysteme(genre="mode", cible="/etc/boilerack", valeur="0750")
    assert (acte.genre, acte.cible, acte.valeur) == ("mode", "/etc/boilerack", "0750")
    assert install.ActeSysteme.__mro__[1:] == (object,)


# ---------------------------------------------------------------------------
# Aucun `systemctl` execute — contrat §13, propriete P9
# ---------------------------------------------------------------------------


def test_systemctl_ne_figure_que_dans_des_valeurs_restituees() -> None:
    """M9, sur les VALEURS du module plutot que sur son texte.

    Une recherche textuelle heurterait les commentaires et les docstrings, qui
    nomment legitimement `systemctl` pour dire qu'il n'est jamais execute. Ce
    test porte sur ce que le module contient reellement a l'execution.
    """
    valeurs: set[str] = set()
    for nom, valeur in vars(install).items():
        if nom.startswith("__"):
            continue
        if isinstance(valeur, str):
            valeurs.add(valeur)
        elif isinstance(valeur, tuple):
            valeurs.update(v for v in valeur if isinstance(v, str))

    porteuses = {v for v in valeurs if "systemctl" in v}
    assert porteuses == set(install.ACTES_HUMAINS_INSTALLATION) | {
        "systemctl disable --now boilerack.service"
    }


def test_l_installateur_ne_peut_lancer_aucun_processus() -> None:
    """M9, preuve STRUCTURELLE : la capacite d'executer n'existe pas.

    Ni `subprocess` importe, ni aucune primitive d'execution de `os` appelee. Un
    module qui n'a pas ces moyens ne peut pas invoquer `systemctl`, quelle que
    soit la chaine qu'il manipule.
    """
    arbre = ast.parse(CHEMIN_INSTALLATEUR.read_text(encoding="utf-8"))

    importes: set[str] = set()
    appels_os: set[str] = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            importes.update(alias.name.split(".")[0] for alias in noeud.names)
        elif isinstance(noeud, ast.ImportFrom) and noeud.level == 0 and noeud.module:
            importes.add(noeud.module.split(".")[0])
        elif isinstance(noeud, ast.Attribute) and isinstance(noeud.value, ast.Name):
            if noeud.value.id == "os":
                appels_os.add(noeud.attr)

    assert "subprocess" not in importes
    interdits = {
        "system", "popen", "execv", "execve", "execvp", "execvpe", "execl",
        "spawnl", "spawnv", "spawnve", "posix_spawn", "fork", "forkpty",
    }
    assert appels_os & interdits == set()


# ---------------------------------------------------------------------------
# Interface en ligne de commande
# ---------------------------------------------------------------------------


def _options(nom_sous_commande: str) -> set[str]:
    parser = install.build_parser()
    sous = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ][0]
    cible = sous.choices[nom_sous_commande]
    chaines: set[str] = set()
    for action in cible._actions:
        chaines.update(action.option_strings)
    return chaines


def test_options_de_install() -> None:
    assert _options("install") == {"-h", "--help", "--checkout", "--root",
                                   "--allow-system-acts"}


def test_options_de_uninstall() -> None:
    assert _options("uninstall") == {"-h", "--help", "--root", "--allow-system-acts"}


def test_aucune_option_n_expose_la_racine_systeme_de_reference() -> None:
    """La couture de test ne doit exister dans AUCUNE surface publique."""
    toutes = _options("install") | _options("uninstall")
    for interdite in (
        "--system-root",
        "--fake-root",
        "--reference-root",
        "--racine-systeme",
        "--test-root",
    ):
        assert interdite not in toutes
    assert not any("system-root" in option or "fake" in option for option in toutes)


def test_install_sans_root_est_refuse() -> None:
    """M20 : aucune valeur par defaut, donc aucune invocation par omission."""
    with pytest.raises(SystemExit) as sortie:
        install.main(["install", "--checkout", "."])
    assert sortie.value.code == install.CODE_REFUS


def test_uninstall_sans_root_est_refuse() -> None:
    with pytest.raises(SystemExit) as sortie:
        install.main(["uninstall"])
    assert sortie.value.code == install.CODE_REFUS


def test_install_sans_checkout_est_refuse(synthetique: pathlib.Path) -> None:
    with pytest.raises(SystemExit) as sortie:
        install.main(["install", "--root", str(synthetique)])
    assert sortie.value.code == install.CODE_REFUS


def test_commande_inconnue_est_refusee() -> None:
    with pytest.raises(SystemExit) as sortie:
        install.main(["deploy", "--root", "/tmp"])
    assert sortie.value.code == install.CODE_REFUS


def test_aucune_commande_est_refusee() -> None:
    with pytest.raises(SystemExit) as sortie:
        install.main([])
    assert sortie.value.code == install.CODE_REFUS


def test_la_racine_n_a_aucune_valeur_par_defaut() -> None:
    """M20, preuve directe sur l'analyseur plutot que sur son comportement."""
    parser = install.build_parser()
    sous = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ][0]
    for nom in ("install", "uninstall"):
        racine = {a.dest: a for a in sous.choices[nom]._actions}["root"]
        assert racine.required is True
        assert racine.default is None


def test_allow_system_acts_est_ferme_par_defaut(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    parser = install.build_parser()
    arguments = parser.parse_args(
        ["install", "--checkout", str(checkout), "--root", str(synthetique)]
    )
    assert arguments.allow_system_acts is False


def test_allow_system_acts_present_est_lu(
    checkout: pathlib.Path, synthetique: pathlib.Path
) -> None:
    parser = install.build_parser()
    arguments = parser.parse_args(
        [
            "install",
            "--checkout",
            str(checkout),
            "--root",
            str(synthetique),
            "--allow-system-acts",
        ]
    )
    assert arguments.allow_system_acts is True


def test_main_rend_zero_sur_combinaison_admise(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    code = install.main(
        ["install", "--checkout", str(checkout), "--root", str(synthetique)],
        racine_systeme=systeme,
    )
    assert code == install.CODE_SUCCES


def test_main_rend_deux_et_n_affiche_pas_de_trace(
    capsys, checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    code = install.main(
        ["install", "--checkout", str(checkout), "--root", str(systeme)],
        racine_systeme=systeme,
    )
    assert code == install.CODE_REFUS
    capture = capsys.readouterr()
    assert "refus" in capture.err
    assert "Traceback" not in capture.err


def test_main_restitue_les_actes_humains(
    capsys, checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    install.main(
        ["install", "--checkout", str(checkout), "--root", str(synthetique)],
        racine_systeme=systeme,
    )
    sortie = capsys.readouterr().out
    for commande in install.ACTES_HUMAINS_INSTALLATION:
        assert commande in sortie


def test_la_grille_de_codes_est_celle_du_contrat() -> None:
    assert (install.CODE_SUCCES, install.CODE_PANNE, install.CODE_REFUS) == (0, 1, 2)


# ---------------------------------------------------------------------------
# Separation runtime / installateur — propriete P14
# ---------------------------------------------------------------------------


def test_l_installateur_n_est_pas_dans_le_paquet() -> None:
    assert CHEMIN_INSTALLATEUR.parent == RACINE_DEPOT
    assert not (RACINE_DEPOT / "src" / "boilerack" / "install.py").exists()


def test_aucun_module_runtime_n_importe_l_installateur() -> None:
    """M15 : le service n'embarque pas la logique qui ecrit sur le disque."""
    for module in (RACINE_DEPOT / "src" / "boilerack").rglob("*.py"):
        source = module.read_text(encoding="utf-8")
        assert "import install" not in source, module
        assert "install.py" not in source, module


def test_le_packaging_exclut_l_installateur_de_la_wheel() -> None:
    """Preuve statique sur `pyproject.toml`, sans le modifier ni construire de roue."""
    document = tomllib.loads(
        (RACINE_DEPOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    paquets = document["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    assert paquets == ["src/boilerack"]


def test_l_installateur_n_utilise_que_la_bibliotheque_standard() -> None:
    """Contrat §21 : sur la cible, il s'execute avant qu'une dependance existe."""
    arbre = ast.parse(CHEMIN_INSTALLATEUR.read_text(encoding="utf-8"))
    racines: set[str] = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            racines.update(alias.name.split(".")[0] for alias in noeud.names)
        elif isinstance(noeud, ast.ImportFrom) and noeud.level == 0 and noeud.module:
            racines.add(noeud.module.split(".")[0])
    assert racines <= set(sys.stdlib_module_names)
    assert "boilerack" not in racines
