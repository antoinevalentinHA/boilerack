"""Tests de l'installateur (lots C13-B1 et C13-B2).

Ce module prouve ce que l'installateur REFUSE, que ses refus sont sans effet, et
ce qu'il POSE lorsqu'il accepte.

AUCUNE RACINE REELLE
    Toutes les racines sont des repertoires temporaires. La racine du systeme
    n'est jamais touchee : les tests substituent une racine de reference par
    l'argument nomme prevu a cet effet, qui n'est expose par aucune option de
    ligne de commande.

AUCUN ACTE SYSTEME REEL
    Ni `groupadd`, ni `useradd`, ni `chown`, ni `chmod` ne sont executes, y
    compris dans les scenarios qui exercent le mode reel : ceux-la passent par un
    double qui enregistre au lieu d'appliquer. La fonction d'application reelle
    de l'installateur n'est couverte par aucun test, et cela est declare.

CE QUE CES TESTS NE PROUVENT PAS
    Aucune conformite terrain. Le contrat range ces preuves en §20 : `useradd`
    reel, `chown` reel, modes reels, systemd, `daemon-reload`, `enable`, `start`,
    vraie racine `/` avec actes ouverts, Raspberry Pi. L'injection de version
    Python n'est PAS une execution sous un interpreteur ancien : elle exerce le
    refus, pas son declencheur reel.
"""

from __future__ import annotations

import argparse
import ast
import os
import pathlib
import subprocess
import sys
import sysconfig
import tomllib

import pytest

from installer_support import (
    CHEMIN_INSTALLATEUR,
    RACINE_DEPOT,
    DoubleActes,
    DoubleVenv,
    charger_installateur,
    contenus,
    empreinte,
    espionner_les_processus,
    interdire_les_actes_systeme,
    interdire_toute_ecriture,
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
    """Checkout minimal conforme a PC4, avec des sources de copie identifiables."""
    base = tmp_path / "checkout"
    (base / "systemd").mkdir(parents=True)
    (base / "docs").mkdir(parents=True)
    (base / "pyproject.toml").write_bytes(b"[project]\nname = 'factice'\n")
    (base / "systemd" / "boilerack.service").write_bytes(
        b"[Unit]\nDescription=unite factice\n"
    )
    (base / "docs" / "boilerack.example.toml").write_bytes(
        b"[mqtt]\nhost = \"broker.exemple.invalid\"\n"
    )
    return base


def _peupler(racine: pathlib.Path) -> None:
    """Depose de quoi rendre visible le moindre effet parasite sur la racine."""
    (racine / "temoin").mkdir(exist_ok=True)
    (racine / "temoin" / "fichier.txt").write_bytes(b"temoin\n")


def _installer(checkout, racine, systeme, **kwargs):
    """Installe avec les deux coutures doublees. Rend (resultat, venv, actes)."""
    double_venv = kwargs.pop("double_venv", None) or DoubleVenv(racine)
    double_actes = kwargs.pop("double_actes", None) or DoubleActes()
    resultat = install.installer(
        checkout=checkout,
        racine=racine,
        racine_systeme=systeme,
        construire_venv=double_venv,
        appliquer_actes=double_actes,
        **kwargs,
    )
    return resultat, double_venv, double_actes


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
# Racine systeme par defaut — reserve R2 de l'audit B1
# ---------------------------------------------------------------------------


def test_la_racine_systeme_par_defaut_est_celle_du_systeme() -> None:
    """Le chemin de PRODUCTION vise bien la vraie racine, sans jamais y toucher."""
    assert install._racine_systeme_par_defaut() == pathlib.Path(os.sep)


def test_sans_argument_la_classification_utilise_la_vraie_racine(
    tmp_path: pathlib.Path,
) -> None:
    """Aucune couture n'est active par defaut : un tempdir n'est pas la racine."""
    assert install.classer_racine(tmp_path).designe_le_systeme is False


def test_aucune_variable_d_environnement_ne_redefinit_la_racine_systeme(
    monkeypatch, tmp_path: pathlib.Path
) -> None:
    """La couture n'est ni une option, ni une variable, ni une cle de configuration."""
    for nom in ("BOILERACK_SYSTEM_ROOT", "BOILERACK_ROOT", "SYSTEM_ROOT", "ROOT"):
        monkeypatch.setenv(nom, str(tmp_path))
    assert install.classer_racine(tmp_path).designe_le_systeme is False

    # Preuve structurelle : l'installateur ne lit AUCUNE variable d'environnement.
    # Une recherche textuelle heurterait le mot « environnement », qui figure
    # legitimement dans le modele de `boilerack.env`.
    arbre = ast.parse(CHEMIN_INSTALLATEUR.read_text(encoding="utf-8"))
    lectures = {
        noeud.attr
        for noeud in ast.walk(arbre)
        if isinstance(noeud, ast.Attribute)
        and isinstance(noeud.value, ast.Name)
        and noeud.value.id == "os"
    }
    assert lectures & {"environ", "getenv", "environb"} == set()


# ---------------------------------------------------------------------------
# Combinaisons admises et refusees — contrat §8.1, PC2
# ---------------------------------------------------------------------------


def test_synthetique_avec_actes_fermes_est_admise(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    resultat, _, _ = _installer(checkout, synthetique, systeme)
    assert resultat.code == install.CODE_SUCCES
    assert resultat.racine.designe_le_systeme is False


def test_reference_avec_actes_ouverts_est_admise(
    checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """La seconde combinaison admise, exercee sur la racine de REFERENCE, jamais `/`.

    Les actes systeme passent par un double : aucun `useradd` ni `chown` reel.
    """
    resultat, _, actes = _installer(checkout, systeme, systeme, actes_ouverts=True)
    assert resultat.code == install.CODE_SUCCES
    assert resultat.racine.designe_le_systeme is True
    assert actes.appliques, "le mode reel doit appliquer les actes declares"


def test_reference_avec_actes_fermes_est_refusee(
    monkeypatch, checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M21 : c'est le vecteur destructeur exact ferme par la correction N1."""
    _peupler(systeme)
    avant = empreinte(systeme)
    interdire_toute_ecriture(monkeypatch)
    with pytest.raises(install.RefusPrecondition) as refus:
        _installer(checkout, systeme, systeme, actes_ouverts=False)
    assert "PC2" in str(refus.value)
    assert empreinte(systeme) == avant


def test_synthetique_avec_actes_ouverts_est_refusee(
    monkeypatch, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """M22 : ouvrir les actes systeme sur une racine synthetique ruinerait P8."""
    _peupler(synthetique)
    avant = empreinte(synthetique)
    interdire_toute_ecriture(monkeypatch)
    with pytest.raises(install.RefusPrecondition) as refus:
        _installer(checkout, synthetique, systeme, actes_ouverts=True)
    assert "PC2" in str(refus.value)
    assert empreinte(synthetique) == avant


def test_alias_de_la_racine_de_reference_avec_actes_fermes_est_refuse(
    monkeypatch, checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M23 par le refus : une ecriture alternative ne contourne pas PC2."""
    _peupler(systeme)
    avant = empreinte(systeme)
    interdire_toute_ecriture(monkeypatch)
    for alias in (systeme / ".", systeme / "opt" / ".."):
        with pytest.raises(install.RefusPrecondition) as refus:
            _installer(checkout, alias, systeme, actes_ouverts=False)
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
                _installer(checkout, racine, systeme, actes_ouverts=ouverts)
                obtenu[(reelle, ouverts)] = "admise"
            except install.RefusPrecondition:
                obtenu[(reelle, ouverts)] = "refusee"
    assert obtenu == attendu


# ---------------------------------------------------------------------------
# Preconditions — PC3, PC4, PC5
# ---------------------------------------------------------------------------


def test_python_trop_ancien_est_refuse() -> None:
    """L'injection exerce le REFUS, pas son declencheur reel (contrat §5, I2)."""
    with pytest.raises(install.RefusPrecondition) as refus:
        install._verifier_version_python((3, 9))
    assert "PC3" in str(refus.value)


def test_python_courant_est_accepte() -> None:
    assert sys.version_info[:2] >= install.PYTHON_MINIMAL
    install._verifier_version_python()


def test_python_trop_ancien_ne_produit_aucun_effet(
    monkeypatch, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """M7 dans sa forme reelle — reserve R8 de l'audit B1.

    B2 produit de vrais effets : le controle de version doit donc les preceder
    tous. Toute mutation le deplacant apres la creation des repertoires laisse
    une trace que l'empreinte revele.
    """
    _peupler(synthetique)
    avant = empreinte(synthetique)
    interdire_toute_ecriture(monkeypatch)
    with pytest.raises(install.RefusPrecondition) as refus:
        _installer(checkout, synthetique, systeme, version_python=(3, 9))
    assert "PC3" in str(refus.value)
    assert empreinte(synthetique) == avant


def test_checkout_absent_est_refuse_sans_effet(
    monkeypatch, tmp_path: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    _peupler(synthetique)
    avant = empreinte(synthetique)
    interdire_toute_ecriture(monkeypatch)
    with pytest.raises(install.RefusPrecondition) as refus:
        _installer(tmp_path / "nexiste_pas", synthetique, systeme)
    assert "PC4" in str(refus.value)
    assert empreinte(synthetique) == avant


@pytest.mark.parametrize(
    "manquant",
    ["pyproject.toml", "systemd/boilerack.service", "docs/boilerack.example.toml"],
)
def test_checkout_incomplet_est_refuse_sans_effet(
    monkeypatch, manquant: str, checkout: pathlib.Path,
    synthetique: pathlib.Path, systeme: pathlib.Path,
) -> None:
    """M14 : chacun des trois fichiers de PC4 est individuellement necessaire."""
    (checkout / manquant).unlink()
    _peupler(synthetique)
    avant = empreinte(synthetique)
    interdire_toute_ecriture(monkeypatch)
    with pytest.raises(install.RefusPrecondition) as refus:
        _installer(checkout, synthetique, systeme)
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
        _installer(checkout, tmp_path / "nexiste" / "pas", systeme)
    assert "PC5" in str(refus.value)


def test_racine_non_inscriptible_est_refusee_sans_effet(
    monkeypatch, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """PC5, moitie « inscriptible » — reserve R4 de l'audit B1.

    Le PREDICAT d'accessibilite est substitue, et non une permission POSIX
    fabriquee : sous Windows les droits ne se modelisent pas en bits d'ecriture,
    et un repertoire rendu « non inscriptible » y serait une simulation deguisee.
    Ce qui est eprouve est ce que le contrat exige — le refus et son absence
    d'effet —, pas le mecanisme de permission de la plateforme.
    """
    _peupler(synthetique)
    avant = empreinte(synthetique)
    monkeypatch.setattr(install, "_inscriptible", lambda _chemin: False)
    interdire_toute_ecriture(monkeypatch)
    with pytest.raises(install.RefusPrecondition) as refus:
        _installer(checkout, synthetique, systeme)
    assert "PC5" in str(refus.value)
    assert "inscriptible" in str(refus.value)
    assert empreinte(synthetique) == avant


def test_les_preconditions_precedent_tout_effet(
    monkeypatch, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """R5 : PC1/PC2 sont evaluees avant le moindre effet.

    Toute primitive d'ecriture est rendue explosive : un refus qui en atteindrait
    une echouerait bruyamment au lieu de passer.
    """
    interdire_toute_ecriture(monkeypatch)
    for racine, ouverts in ((systeme, False), (synthetique, True)):
        with pytest.raises(install.RefusPrecondition):
            _installer(checkout, racine, systeme, actes_ouverts=ouverts)


# ---------------------------------------------------------------------------
# Arborescence — propriete P1
# ---------------------------------------------------------------------------


def test_installation_dans_une_racine_vide_produit_l_arborescence(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """P1 : les emplacements de §7.1 et les repertoires de §7.2."""
    _installer(checkout, synthetique, systeme)
    for relatif in (
        install.CHEMIN_OPT,
        install.CHEMIN_ETC,
        install.CHEMIN_REPERTOIRE_UNITES,
        install.CHEMIN_VENV,
    ):
        assert (synthetique / relatif).is_dir(), relatif
    for relatif in (
        install.CHEMIN_CONFIG,
        install.CHEMIN_SECRET,
        install.CHEMIN_UNITE,
        install.CHEMIN_COMMANDE,
    ):
        assert (synthetique / relatif).is_file(), relatif


def test_les_chemins_relatifs_correspondent_aux_chemins_absolus_du_contrat() -> None:
    """Sous la racine `/`, les emplacements sont exactement ceux de C12 §4.1."""
    assert "/" + install.CHEMIN_VENV == "/opt/boilerack/venv"
    assert "/" + install.CHEMIN_COMMANDE == "/opt/boilerack/venv/bin/boilerack"
    assert "/" + install.CHEMIN_CONFIG == "/etc/boilerack/boilerack.toml"
    assert "/" + install.CHEMIN_SECRET == "/etc/boilerack/boilerack.env"
    assert "/" + install.CHEMIN_UNITE == "/etc/systemd/system/boilerack.service"


def test_aucun_chemin_hors_contrat_n_est_cree(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M1 : rien de plus que ce que le contrat nomme, au niveau superieur."""
    _installer(checkout, synthetique, systeme)
    assert {enfant.name for enfant in synthetique.iterdir()} == {"opt", "etc"}


# ---------------------------------------------------------------------------
# Configuration — proprietes P2 et P6
# ---------------------------------------------------------------------------


def test_configuration_absente_est_copiee_octet_pour_octet(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """P6 : copie byte-identique de l'exemple versionne du checkout."""
    _installer(checkout, synthetique, systeme)
    source = (checkout / install.SOURCE_CONFIG).read_bytes()
    assert (synthetique / install.CHEMIN_CONFIG).read_bytes() == source


def test_configuration_existante_n_est_jamais_ecrasee(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """P2 : le CONTENU est souverain, y compris lors d'une reinstallation."""
    cible = synthetique / install.CHEMIN_CONFIG
    cible.parent.mkdir(parents=True)
    mien = b"[mqtt]\nhost = \"broker.local\"\n# reglages de l'exploitant\n"
    cible.write_bytes(mien)

    _installer(checkout, synthetique, systeme)
    assert cible.read_bytes() == mien
    _installer(checkout, synthetique, systeme)
    assert cible.read_bytes() == mien


def test_preserver_la_configuration_est_un_succes_signale(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M17 : preserver n'est pas echouer (contrat §9.2)."""
    cible = synthetique / install.CHEMIN_CONFIG
    cible.parent.mkdir(parents=True)
    cible.write_bytes(b"a moi\n")
    resultat, _, _ = _installer(checkout, synthetique, systeme)
    assert resultat.code == install.CODE_SUCCES
    assert any("preservee" in message for message in resultat.messages)


# ---------------------------------------------------------------------------
# Secret — proprietes P3 et P4
# ---------------------------------------------------------------------------


def test_environnement_absent_est_cree_depuis_le_modele(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    _installer(checkout, synthetique, systeme)
    contenu = (synthetique / install.CHEMIN_SECRET).read_text(encoding="utf-8")
    assert contenu == install.MODELE_ENVIRONNEMENT


def test_le_modele_ne_definit_aucune_variable() -> None:
    """P4 : aucune affectation active, et la variable citee en commentaire.

    Analyse comme systemd lirait un `EnvironmentFile` : commentaires et lignes
    vides ignores, le reste devant etre `CLE=valeur`.
    """
    actives = [
        ligne
        for ligne in install.MODELE_ENVIRONNEMENT.splitlines()
        if ligne.strip() and not ligne.lstrip().startswith("#")
    ]
    assert actives == []
    assert "BOILERACK_MQTT_PASSWORD" in install.MODELE_ENVIRONNEMENT


def test_le_modele_ne_contient_aucune_valeur_ressemblant_a_un_secret() -> None:
    """Contrat §10.1, clause 4 : ni secret reel, ni factice, ni exemple."""
    for ligne in install.MODELE_ENVIRONNEMENT.splitlines():
        if "BOILERACK_MQTT_PASSWORD" in ligne:
            assert ligne.rstrip().endswith("=")


def test_le_modele_correspond_a_la_variable_du_runtime() -> None:
    """Le nom cite doit etre celui que le programme lit reellement."""
    from boilerack.config import PASSWORD_ENV_VAR

    assert PASSWORD_ENV_VAR in install.MODELE_ENVIRONNEMENT


@pytest.mark.parametrize(
    "existant",
    [b"", b"BOILERACK_MQTT_PASSWORD=deja-actif\n", b"# vide de valeur\n", b"n'importe\n"],
)
def test_environnement_existant_n_est_jamais_ecrase(
    existant: bytes, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """P3 : y compris vide, y compris deja actif, y compris arbitraire."""
    cible = synthetique / install.CHEMIN_SECRET
    cible.parent.mkdir(parents=True)
    cible.write_bytes(existant)

    _installer(checkout, synthetique, systeme)
    assert cible.read_bytes() == existant
    _installer(checkout, synthetique, systeme)
    assert cible.read_bytes() == existant


def test_le_modele_d_environnement_n_est_pas_versionne() -> None:
    """Contrat §10.1, clause 6 : le modele vit INLINE, pas en fichier du depot."""
    assert install.MODELE_ENVIRONNEMENT
    for chemin in RACINE_DEPOT.rglob("boilerack.env*"):
        pytest.fail(f"fichier d'environnement versionne : {chemin}")


# ---------------------------------------------------------------------------
# Unite systemd — propriete P6
# ---------------------------------------------------------------------------


def test_unite_deposee_octet_pour_octet(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M6 : sans quoi la validation statique de C12 §13 ne prouverait plus rien."""
    _installer(checkout, synthetique, systeme)
    source = (checkout / install.SOURCE_UNITE).read_bytes()
    assert (synthetique / install.CHEMIN_UNITE).read_bytes() == source


def test_unite_toujours_redeposee_meme_si_modifiee(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """L'unite appartient au programme, pas a l'exploitant (contrat §9.2)."""
    cible = synthetique / install.CHEMIN_UNITE
    cible.parent.mkdir(parents=True)
    cible.write_bytes(b"[Unit]\nDescription=bricolage local\n")
    _installer(checkout, synthetique, systeme)
    assert cible.read_bytes() == (checkout / install.SOURCE_UNITE).read_bytes()


def test_le_gabarit_reel_du_depot_est_copie_tel_quel(
    synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Exerce la source REELLE du depot, et pas seulement un checkout factice."""
    _installer(RACINE_DEPOT, synthetique, systeme)
    assert (synthetique / install.CHEMIN_UNITE).read_bytes() == (
        RACINE_DEPOT / install.SOURCE_UNITE
    ).read_bytes()
    assert (synthetique / install.CHEMIN_CONFIG).read_bytes() == (
        RACINE_DEPOT / install.SOURCE_CONFIG
    ).read_bytes()


# ---------------------------------------------------------------------------
# Metadonnees — proprietes P8 et P12, mutations M8 et M19
# ---------------------------------------------------------------------------


def _actes(resultat, genre: str) -> dict[str, str]:
    return {a.cible: a.valeur for a in resultat.actes_systeme if a.genre == genre}


def test_les_metadonnees_contractees_sont_declarees(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M8 : chaque emplacement de §7 recoit un proprietaire et un mode."""
    resultat, _, _ = _installer(checkout, synthetique, systeme)
    proprietaires = _actes(resultat, "proprietaire")
    modes = _actes(resultat, "mode")
    attendu = dict(
        (cible, (prop, mode))
        for cible, prop, mode in install.METADONNEES_GROUPE_A + install.METADONNEES_GROUPE_B
    )
    for cible, (prop, mode) in attendu.items():
        assert proprietaires[cible] == prop, cible
        assert modes[cible] == mode, cible


def test_l_identite_est_declaree(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    resultat, _, _ = _installer(checkout, synthetique, systeme)
    assert _actes(resultat, "groupe") == {install.GROUPE: "cree si absent"}
    assert _actes(resultat, "utilisateur") == {install.UTILISATEUR: "cree si absent"}


def test_le_mode_synthetique_n_execute_aucun_acte_systeme(
    monkeypatch, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """P8 : ils sont DECLARES, jamais appliques."""
    interdire_les_actes_systeme(monkeypatch)
    double_actes = DoubleActes()
    resultat, _, _ = _installer(
        checkout, synthetique, systeme, double_actes=double_actes
    )
    assert resultat.actes_systeme
    assert double_actes.lots == [], "aucun acte ne doit etre applique en synthetique"


def test_le_mode_reel_applique_les_actes_declares(
    checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Le double enregistre ; rien n'est execute sur la machine de developpement."""
    resultat, _, double_actes = _installer(
        checkout, systeme, systeme, actes_ouverts=True
    )
    assert {a.cible for a in double_actes.appliques} == {
        a.cible for a in resultat.actes_systeme
    }


def test_les_metadonnees_sont_reappliquees_aux_fichiers_existants(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M19, mutation miroir de M2 et M3.

    Le CONTENU est preserve, les METADONNEES sont reappliquees. Sans cette
    preuve, un installateur qui n'en reappliquerait aucune passerait P2 et P3.
    """
    for relatif, contenu in (
        (install.CHEMIN_CONFIG, b"a moi\n"),
        (install.CHEMIN_SECRET, b"a moi aussi\n"),
    ):
        cible = synthetique / relatif
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_bytes(contenu)

    avant = contenus(synthetique)
    resultat, _, _ = _installer(checkout, synthetique, systeme)

    for relatif in (install.CHEMIN_CONFIG, install.CHEMIN_SECRET):
        assert contenus(synthetique)[relatif] == avant[relatif], "contenu preserve"
        assert _actes(resultat, "proprietaire")[relatif] == "root:boilerack"
        assert _actes(resultat, "mode")[relatif] == "0640"


def test_le_groupe_b_reprend_les_modes_du_contrat_en_toutes_lettres() -> None:
    """Ni C12 ni C13 ne fixent de valeur numerique pour les emplacements du venv.

    En inventer une serait fabriquer une regle absente du corpus. Le manque est
    donc porte tel quel, et `_appliquer_actes_reels` refuse un mode non numerique.
    """
    modes = {cible: mode for cible, _prop, mode in install.METADONNEES_GROUPE_B}
    assert modes == {
        install.CHEMIN_VENV: "lecture pour tous",
        install.CHEMIN_COMMANDE: "executable",
    }
    assert not any(mode.isdigit() for mode in modes.values())


# ---------------------------------------------------------------------------
# Ordre des effets — contrat §8.3, mutations M13 et M18
# ---------------------------------------------------------------------------


def test_au_moment_de_l_etape_venv_tout_le_groupe_a_est_deja_pose(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M13 et M18 : la photographie prise par le double fait foi."""
    double = DoubleVenv(synthetique)
    _installer(checkout, synthetique, systeme, double_venv=double)
    assert double.appele
    presents = {entree[0] for entree in double.empreinte_a_l_appel}
    for relatif in (
        install.CHEMIN_OPT, install.CHEMIN_ETC, install.CHEMIN_REPERTOIRE_UNITES,
        install.CHEMIN_CONFIG, install.CHEMIN_SECRET, install.CHEMIN_UNITE,
    ):
        assert relatif in presents, relatif
    assert install.CHEMIN_VENV not in presents, "le venv ne doit pas exister encore"


def test_les_metadonnees_du_groupe_b_ne_sont_posees_qu_apres_le_venv(
    checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M18 : le groupe B ne peut pas porter sur un venv qui n'existe pas."""
    double_actes = DoubleActes()
    _installer(
        checkout, systeme, systeme, actes_ouverts=True, double_actes=double_actes
    )
    assert len(double_actes.lots) == 2, "deux poses distinctes, pas une seule"
    premier = {a.cible for a in double_actes.lots[0]}
    second = {a.cible for a in double_actes.lots[1]}
    assert install.CHEMIN_VENV not in premier
    assert second == {install.CHEMIN_VENV, install.CHEMIN_COMMANDE}


def test_l_ancien_venv_est_detruit_avant_l_appel_de_construction(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """La destruction precede la construction, et elle est reelle."""
    venv = synthetique / install.CHEMIN_VENV
    venv.mkdir(parents=True)
    (venv / "MARQUEUR_ETRANGER").write_bytes(b"x\n")
    double = DoubleVenv(synthetique)
    _installer(checkout, synthetique, systeme, double_venv=double)
    presents = {entree[0] for entree in double.empreinte_a_l_appel}
    assert not any(chemin.startswith(install.CHEMIN_VENV) for chemin in presents)


# ---------------------------------------------------------------------------
# Venv — proprietes P5 et P12, mutation M5
# ---------------------------------------------------------------------------


def test_le_venv_est_detruit_puis_recree(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M5 : un marqueur etranger ne survit pas a une reinstallation."""
    _installer(checkout, synthetique, systeme)
    marqueur = synthetique / install.CHEMIN_VENV / "MARQUEUR_ETRANGER"
    marqueur.write_bytes(b"survivrai-je ?\n")
    assert marqueur.exists()

    _installer(checkout, synthetique, systeme)
    assert not marqueur.exists()
    assert (synthetique / install.CHEMIN_COMMANDE).is_file()


def test_l_echec_de_l_etape_venv_laisse_le_reste_en_place(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """P12 : configuration, secret et unite subsistent (contrat §11.2)."""
    with pytest.raises(RuntimeError):
        _installer(
            checkout, synthetique, systeme,
            double_venv=DoubleVenv(synthetique, echouer=True),
        )
    assert (synthetique / install.CHEMIN_CONFIG).is_file()
    assert (synthetique / install.CHEMIN_SECRET).is_file()
    assert (synthetique / install.CHEMIN_UNITE).is_file()


def test_aucun_acte_du_groupe_b_si_le_venv_echoue(
    checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Le groupe B suit la creation REUSSIE du venv, jamais son echec."""
    double_actes = DoubleActes()
    with pytest.raises(RuntimeError):
        _installer(
            checkout, systeme, systeme, actes_ouverts=True,
            double_venv=DoubleVenv(systeme, echouer=True),
            double_actes=double_actes,
        )
    assert len(double_actes.lots) == 1
    assert install.CHEMIN_VENV not in {a.cible for a in double_actes.appliques}


def test_une_relance_apres_echec_du_venv_reussit(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Pas de rollback : la reprise se fait par une seconde invocation."""
    with pytest.raises(RuntimeError):
        _installer(
            checkout, synthetique, systeme,
            double_venv=DoubleVenv(synthetique, echouer=True),
        )
    resultat, _, _ = _installer(checkout, synthetique, systeme)
    assert resultat.code == install.CODE_SUCCES
    assert (synthetique / install.CHEMIN_COMMANDE).is_file()


# ---------------------------------------------------------------------------
# Idempotence — propriete P5
# ---------------------------------------------------------------------------


def test_seconde_installation_idempotente(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Contenus preserves, unite remise a la source, venv recree, code 0."""
    premier, _, _ = _installer(checkout, synthetique, systeme)
    empreinte_1 = empreinte(synthetique)

    second, _, _ = _installer(checkout, synthetique, systeme)
    assert second.code == install.CODE_SUCCES
    assert empreinte(synthetique) == empreinte_1
    assert second.actes_systeme == premier.actes_systeme


def test_troisieme_installation_reste_stable(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    _installer(checkout, synthetique, systeme)
    _installer(checkout, synthetique, systeme)
    reference = empreinte(synthetique)
    _installer(checkout, synthetique, systeme)
    assert empreinte(synthetique) == reference


# ---------------------------------------------------------------------------
# Desinstallation — proprietes P10 et P11
# ---------------------------------------------------------------------------


def test_desinstallation_supprime_le_programme_et_preserve_l_exploitant(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M10 et M11 : le contenu de l'exploitant et l'identite survivent."""
    _installer(checkout, synthetique, systeme)
    config = (synthetique / install.CHEMIN_CONFIG).read_bytes()
    secret = (synthetique / install.CHEMIN_SECRET).read_bytes()

    resultat = install.desinstaller(racine=synthetique, racine_systeme=systeme)

    assert resultat.code == install.CODE_SUCCES
    assert not (synthetique / install.CHEMIN_OPT).exists()
    assert not (synthetique / install.CHEMIN_UNITE).exists()
    assert (synthetique / install.CHEMIN_ETC).is_dir()
    assert (synthetique / install.CHEMIN_CONFIG).read_bytes() == config
    assert (synthetique / install.CHEMIN_SECRET).read_bytes() == secret
    assert resultat.actes_systeme == (), "aucune suppression d'identite"


def test_desinstallation_idempotente(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    _installer(checkout, synthetique, systeme)
    install.desinstaller(racine=synthetique, racine_systeme=systeme)
    apres = empreinte(synthetique)
    second = install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert second.code == install.CODE_SUCCES
    assert empreinte(synthetique) == apres


def test_desinstallation_sur_racine_vierge_reussit(
    synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    resultat = install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert resultat.code == install.CODE_SUCCES


def test_desinstallation_refuse_si_un_fichier_occupe_le_chemin_d_activation(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """M12, cas du fichier ordinaire — refus AVANT toute suppression."""
    _installer(checkout, synthetique, systeme)
    lien = synthetique / install.CHEMIN_LIEN_ACTIVATION
    lien.parent.mkdir(parents=True, exist_ok=True)
    lien.write_bytes(b"")
    avant = empreinte(synthetique)

    with pytest.raises(install.RefusPrecondition) as refus:
        install.desinstaller(racine=synthetique, racine_systeme=systeme)

    assert "systemctl disable" in str(refus.value)
    assert empreinte(synthetique) == avant
    assert (synthetique / install.CHEMIN_OPT).is_dir(), "rien ne doit avoir ete supprime"


def test_desinstallation_refuse_sur_un_lien_symbolique_pendant(
    tmp_path: pathlib.Path, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """La garde doit voir une entree PENDANTE : `Path.exists()` rendrait `False`."""
    if not liens_symboliques_disponibles(tmp_path):
        pytest.skip("creation de lien symbolique indisponible sur cette plateforme")
    _installer(checkout, synthetique, systeme)
    lien = synthetique / install.CHEMIN_LIEN_ACTIVATION
    lien.parent.mkdir(parents=True, exist_ok=True)
    lien.symlink_to(synthetique / "cible" / "absente.service")

    assert lien.exists() is False, "la cible doit bien etre absente"
    assert install.entree_existe(lien) is True

    avant = empreinte(synthetique)
    with pytest.raises(install.RefusPrecondition):
        install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert empreinte(synthetique) == avant


def test_la_garde_n_utilise_pas_une_primitive_qui_suit_les_liens() -> None:
    """Aide statique seulement : la preuve comportementale Linux fait autorite."""
    source = CHEMIN_INSTALLATEUR.read_text(encoding="utf-8")
    assert "os.path.lexists" in source


# ---------------------------------------------------------------------------
# Aucun `systemctl` — contrat §13, propriete P9
# ---------------------------------------------------------------------------


def test_systemctl_ne_figure_que_dans_des_valeurs_restituees() -> None:
    """M9, sur les VALEURS du module plutot que sur son texte."""
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


def test_aucun_processus_n_est_lance_en_mode_synthetique(
    monkeypatch, checkout: pathlib.Path, synthetique: pathlib.Path,
    systeme: pathlib.Path,
) -> None:
    """M9, preuve dynamique sur l'installation ET la desinstallation.

    Le seul processus que l'installateur puisse legitimement lancer est le `pip`
    du venv qu'il vient de creer — et cette etape passe ici par un double.
    """
    espion = espionner_les_processus(monkeypatch)
    _installer(checkout, synthetique, systeme)
    install.desinstaller(racine=synthetique, racine_systeme=systeme)
    assert espion.commandes == []


def test_le_seul_executable_lance_appartient_au_venv() -> None:
    """La couture reelle ne lance que le `python` du venv, pour `pip`."""
    source = ast.parse(CHEMIN_INSTALLATEUR.read_text(encoding="utf-8"))
    appels_os: set[str] = set()
    for noeud in ast.walk(source):
        if isinstance(noeud, ast.Attribute) and isinstance(noeud.value, ast.Name):
            if noeud.value.id == "os":
                appels_os.add(noeud.attr)
    interdits = {
        "system", "popen", "execv", "execve", "execvp", "execvpe", "execl",
        "spawnl", "spawnv", "spawnve", "posix_spawn", "fork", "forkpty",
    }
    assert appels_os & interdits == set()


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
# Interface en ligne de commande
# ---------------------------------------------------------------------------


def _sous_commandes() -> argparse._SubParsersAction:
    parser = install.build_parser()
    return [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ][0]


def _options(nom: str) -> set[str]:
    chaines: set[str] = set()
    for action in _sous_commandes().choices[nom]._actions:
        chaines.update(action.option_strings)
    return chaines


def test_options_de_install() -> None:
    assert _options("install") == {
        "-h", "--help", "--checkout", "--root", "--allow-system-acts"
    }


def test_options_de_uninstall() -> None:
    assert _options("uninstall") == {"-h", "--help", "--root", "--allow-system-acts"}


def test_aucune_option_n_expose_la_racine_systeme_de_reference() -> None:
    """La couture de test ne doit exister dans AUCUNE surface publique."""
    toutes = _options("install") | _options("uninstall")
    for interdite in (
        "--system-root", "--fake-root", "--reference-root", "--racine-systeme",
        "--test-root",
    ):
        assert interdite not in toutes
    assert not any("system-root" in option or "fake" in option for option in toutes)


def test_aucune_option_n_expose_les_coutures() -> None:
    """Ni le constructeur de venv, ni l'applicateur d'actes ne sont exposes."""
    toutes = _options("install") | _options("uninstall")
    assert not any("venv" in option or "acts-impl" in option for option in toutes)


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
    sous = _sous_commandes()
    for nom in ("install", "uninstall"):
        racine = {a.dest: a for a in sous.choices[nom]._actions}["root"]
        assert racine.required is True
        assert racine.default is None


def test_allow_system_acts_est_ferme_par_defaut(
    checkout: pathlib.Path, synthetique: pathlib.Path
) -> None:
    arguments = install.build_parser().parse_args(
        ["install", "--checkout", str(checkout), "--root", str(synthetique)]
    )
    assert arguments.allow_system_acts is False


def test_allow_system_acts_present_est_lu(
    checkout: pathlib.Path, synthetique: pathlib.Path
) -> None:
    arguments = install.build_parser().parse_args(
        ["install", "--checkout", str(checkout), "--root", str(synthetique),
         "--allow-system-acts"]
    )
    assert arguments.allow_system_acts is True


def test_main_installe_de_bout_en_bout(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    code = install.main(
        ["install", "--checkout", str(checkout), "--root", str(synthetique)],
        racine_systeme=systeme,
        construire_venv=DoubleVenv(synthetique),
        appliquer_actes=DoubleActes(),
    )
    assert code == install.CODE_SUCCES
    assert (synthetique / install.CHEMIN_UNITE).is_file()


def test_main_desinstalle_de_bout_en_bout(
    capsys, checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """R3 : la branche `uninstall` de `main()` est exercee reellement."""
    _installer(checkout, synthetique, systeme)
    capsys.readouterr()

    code = install.main(
        ["uninstall", "--root", str(synthetique)], racine_systeme=systeme
    )

    assert code == install.CODE_SUCCES
    assert not (synthetique / install.CHEMIN_OPT).exists()
    assert (synthetique / install.CHEMIN_CONFIG).is_file()
    assert "systemctl daemon-reload" in capsys.readouterr().out


def test_main_uninstall_refuse_la_combinaison_interdite(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    _installer(checkout, synthetique, systeme)
    avant = empreinte(synthetique)
    code = install.main(
        ["uninstall", "--root", str(synthetique), "--allow-system-acts"],
        racine_systeme=systeme,
    )
    assert code == install.CODE_REFUS
    assert empreinte(synthetique) == avant


def test_main_uninstall_refuse_sur_activation(
    capsys, checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    _installer(checkout, synthetique, systeme)
    lien = synthetique / install.CHEMIN_LIEN_ACTIVATION
    lien.parent.mkdir(parents=True, exist_ok=True)
    lien.write_bytes(b"")
    avant = empreinte(synthetique)
    capsys.readouterr()

    code = install.main(
        ["uninstall", "--root", str(synthetique)], racine_systeme=systeme
    )

    assert code == install.CODE_REFUS
    assert empreinte(synthetique) == avant
    assert "systemctl disable" in capsys.readouterr().err


def test_main_rend_deux_et_n_affiche_pas_de_trace(
    capsys, checkout: pathlib.Path, systeme: pathlib.Path
) -> None:
    code = install.main(
        ["install", "--checkout", str(checkout), "--root", str(systeme)],
        racine_systeme=systeme,
        construire_venv=DoubleVenv(systeme),
        appliquer_actes=DoubleActes(),
    )
    assert code == install.CODE_REFUS
    capture = capsys.readouterr()
    assert "refus" in capture.err
    assert "Traceback" not in capture.err


def test_main_restitue_les_actes(
    capsys, checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    install.main(
        ["install", "--checkout", str(checkout), "--root", str(synthetique)],
        racine_systeme=systeme,
        construire_venv=DoubleVenv(synthetique),
        appliquer_actes=DoubleActes(),
    )
    sortie = capsys.readouterr().out
    for commande in install.ACTES_HUMAINS_INSTALLATION:
        assert commande in sortie
    assert "declares, non executes" in sortie
    assert install.CHEMIN_CONFIG in sortie


def test_main_ne_pretend_pas_que_la_configuration_est_prete(
    capsys, checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Contrat §8.4 : l'exemple depose est inutilisable en l'etat."""
    install.main(
        ["install", "--checkout", str(checkout), "--root", str(synthetique)],
        racine_systeme=systeme,
        construire_venv=DoubleVenv(synthetique),
        appliquer_actes=DoubleActes(),
    )
    assert "relisez-la avant tout demarrage" in capsys.readouterr().out


def test_la_grille_de_codes_est_celle_du_contrat() -> None:
    assert (install.CODE_SUCCES, install.CODE_PANNE, install.CODE_REFUS) == (0, 1, 2)


def test_une_panne_apres_les_preconditions_n_est_pas_traduite(
    checkout: pathlib.Path, synthetique: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Contrat §16 : elle remonte avec sa trace, et Python en fait un `1`."""
    with pytest.raises(RuntimeError):
        install.main(
            ["install", "--checkout", str(checkout), "--root", str(synthetique)],
            racine_systeme=systeme,
            construire_venv=DoubleVenv(synthetique, echouer=True),
            appliquer_actes=DoubleActes(),
        )


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


# ---------------------------------------------------------------------------
# Bout en bout REEL — venv veritable, pip veritable. N'EST PAS HORS LIGNE.
# ---------------------------------------------------------------------------


def test_installation_reelle_du_venv_sous_racine_synthetique(
    tmp_path: pathlib.Path, systeme: pathlib.Path
) -> None:
    """Unique test qui construit un vrai venv et y installe vraiment Boilerack.

    **CE TEST N'EST PAS HORS LIGNE** : l'isolation de build PEP 517 recupere le
    moteur declare depuis l'index des paquets, comme la fixture C12 l'avait deja
    mesure. Un echec reseau reste un ECHEC ; il n'est pas requalifie en skip.

    Aucun systeme reel n'est touche : la racine est un repertoire temporaire, et
    l'unite deposee designe des chemins absolus qui n'y existent pas — c'est
    voulu (contrat §8.4).
    """
    racine = tmp_path / "racine_reelle"
    racine.mkdir()

    resultat = install.installer(
        checkout=RACINE_DEPOT,
        racine=racine,
        racine_systeme=systeme,
        appliquer_actes=DoubleActes(),
    )
    assert resultat.code == install.CODE_SUCCES

    venv = racine / install.CHEMIN_VENV
    assert (venv / "pyvenv.cfg").is_file()
    binaire = "Scripts" if sysconfig.get_platform().startswith("win") else "bin"
    script = venv / binaire / ("boilerack.exe" if binaire == "Scripts" else "boilerack")
    assert script.is_file(), f"le script console n'a pas ete cree : {script}"

    proc = subprocess.run(
        [str(script), "--help"], capture_output=True, text=True, timeout=180
    )
    assert proc.returncode == 0
    assert "--config" in proc.stdout

    etranger = venv / "MARQUEUR_ETRANGER"
    etranger.write_bytes(b"je ne dois pas survivre\n")
    install.installer(
        checkout=RACINE_DEPOT,
        racine=racine,
        racine_systeme=systeme,
        appliquer_actes=DoubleActes(),
    )
    assert not etranger.exists(), "la recreation du venv doit tout emporter"
    assert script.is_file()
