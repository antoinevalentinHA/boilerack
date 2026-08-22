"""Tests du profil de PRODUCTION (lot W4-D).

HORS LIGNE et DETERMINISTES : aucun Pi, aucun `vclient`, aucun `vcontrold`,
aucune chaudiere, aucun broker, aucun processus. Le profil est une constante du
protocole ; le verifier n'exige rien d'autre que de le construire.

Ces tests portent sur DEUX choses, et deux seulement :

- que le profil declare exactement ce que W4-C a caracterise ;
- qu'il ne declare RIEN de ce qui appartient a une autre couche.

La seconde est la plus importante : un profil qui deborde de son role est un
defaut plus couteux qu'un profil incomplet.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from boilerack.core import build_production_profile
from boilerack.core.profile import CommandSpec, Profile, ValueType
from boilerack.core.validation import validate
from boilerack.testing import build_fake_profile

from support import START, payload, rid


# --------------------------------------------------------------------------
# A. Ce que le profil declare
# --------------------------------------------------------------------------


def test_le_profil_se_construit_et_est_valide() -> None:
    """La construction seule prouve le schema : `Profile.__post_init__` valide."""
    profile = build_production_profile()
    assert isinstance(profile, Profile)
    assert profile.name


def test_la_fabrique_ne_prend_aucun_parametre() -> None:
    """Un profil est une constante du protocole, pas une configuration de site.

    S'il prenait un parametre, il deviendrait un point d'injection de donnees
    d'installation — exactement ce que `provenance.md` exclut.
    """
    assert inspect.signature(build_production_profile).parameters == {}


def test_un_seul_role_et_c_est_celui_qui_a_ete_caracterise() -> None:
    """W4-C n'a caracterise que `setNiveauM1`. Le profil n'en expose pas d'autre.

    Liste FERMEE : un role ajoute sans campagne fait echouer ce test, ce qui est
    exactement l'effet recherche.
    """
    profile = build_production_profile()
    assert sorted(profile.commands) == ["heating_curve_shift"]


def test_les_commandes_sont_celles_de_l_autorite() -> None:
    spec = build_production_profile().get("heating_curve_shift")
    assert spec.read == "getNiveauM1"
    assert spec.write == "setNiveauM1"
    assert spec.writable is True


def test_les_contraintes_de_valeur_sont_celles_de_a5() -> None:
    """`int`, bornes [-13 ; 40], pas 1, tolerance NULLE (A5 §5.3)."""
    spec = build_production_profile().get("heating_curve_shift")
    assert spec.type is ValueType.INTEGER
    assert (spec.min, spec.max) == (-13, 40)
    assert spec.step == 1
    assert spec.confirm_tolerance == 0.0
    assert spec.idempotent is True


def test_la_provenance_des_bornes_est_citable() -> None:
    """`bounds_source` existe pour qu'aucune borne n'entre sans source.

    Les trois autorites y figurent : A5 pour les bornes, c7 §4.2 pour le role et
    la commande de lecture, W4-C pour la caracterisation de l'ecriture.
    """
    source = build_production_profile().get("heating_curve_shift").bounds_source
    assert "mqtt.md" in source
    assert "c7-mqtt-read-contract.md" in source
    assert "w4c-write-capture-protocol.md" in source


def test_le_role_reprend_le_vocabulaire_deja_en_production() -> None:
    """Le meme datapoint ne doit pas porter deux noms dans le meme depot.

    AUTORITE NORMATIVE : `c7-mqtt-read-contract.md` §4.2, dont la table associe
    `heating_curve_shift` a `getNiveauM1`.

    `V1_MEASUREMENTS` n'est PAS cette autorite : c'est une transcription pair du
    meme contrat, pour la surface de lecture. Le test la confronte au profil
    comme un controle de COHERENCE entre deux transcriptions — si l'une derive,
    il le dit — et non comme la source du nom.
    """
    from boilerack.read_surface.measurements import V1_MEASUREMENTS

    lecture = {m.read: m.role for m in V1_MEASUREMENTS}
    spec = build_production_profile().get("heating_curve_shift")
    assert lecture[spec.read] == spec.role


# --------------------------------------------------------------------------
# B. Ce que le profil ne declare PAS — la frontiere
# --------------------------------------------------------------------------


def test_le_profil_ne_porte_aucune_signature_de_succes() -> None:
    """`raw == "OK"` appartient a l'adaptateur (W4-A §9), pas au profil.

    La preuve porte sur le SOURCE du module : ni le jeton observe, ni le champ
    JSON, ni un statut de transport n'y figurent. Un profil declare des
    grandeurs ; il ne lit pas la sortie d'un processus.
    """
    from boilerack.core import production_profile

    source = inspect.getsource(production_profile)
    corps = source.split('"""', 2)[2]  # hors docstring de module
    for interdit in ('"OK"', "TransportStatus", "returncode", "stderr", "stdout"):
        assert interdit not in corps, f"le profil porte {interdit}"


def test_le_profil_ne_porte_aucune_signature_d_echec() -> None:
    """Aucun echec d'ecriture n'a ete observe : rien ne doit en etre declare.

    W4-A §11.6 et §12.3 restent en vigueur. Inventer ici une signature d'echec
    serait exactement la faute que ces clauses interdisent.
    """
    from boilerack.core import production_profile

    corps = inspect.getsource(production_profile).split('"""', 2)[2]
    for interdit in ("DAEMON_UNREACHABLE", "UNKNOWN_COMMAND", "TIMEOUT", "ERR:"):
        assert interdit not in corps, f"le profil invente {interdit}"


def test_le_profil_n_a_aucune_notion_de_valeur_appliquee() -> None:
    """`value == 0.000000` n'est pas une valeur metier — le profil l'ignore.

    Le champ `value` d'une reponse d'ECRITURE vaut `0.000000` alors que le
    datapoint vaut autre chose (W4-C §16.4). Le profil ne connait pas ce champ,
    et `CommandSpec` n'expose aucun attribut qui pourrait le recevoir.
    """
    champs = {f for f in CommandSpec.__dataclass_fields__}
    for interdit in ("value", "applied", "raw", "success", "ok"):
        assert interdit not in champs


def test_la_confirmation_reste_une_relecture_du_coeur() -> None:
    """Le profil fournit la tolerance ; le coeur decide.

    Un role entier est confirme par EGALITE EXACTE, quelle que soit la
    tolerance : c'est `_confirms` qui l'applique, dans le coeur, et le profil ne
    fait que declarer `read` pour que cette relecture soit possible.
    """
    from boilerack.core.engine import _confirms

    spec = build_production_profile().get("heating_curve_shift")
    assert spec.read  # la relecture est possible : une commande existe
    assert _confirms(2, 2, spec.confirm_tolerance, spec) is True
    assert _confirms(3, 2, spec.confirm_tolerance, spec) is False
    # Meme avec une tolerance large, un entier n'est jamais confirme "a peu pres".
    assert _confirms(3, 2, 10.0, spec) is False


def test_aucune_donnee_de_site_dans_le_module() -> None:
    """Le profil decrit le protocole, pas l'installation (`provenance.md`)."""
    from boilerack.core import production_profile

    source = inspect.getsource(production_profile)
    for interdit in ("localhost", "192.168", "/home/", ".service", ".timer", "3002"):
        assert interdit not in source, f"donnee de site : {interdit}"


# --------------------------------------------------------------------------
# C. Le profil est reellement utilisable par le coeur
# --------------------------------------------------------------------------


@pytest.mark.parametrize("valeur", [-13, 0, 2, 40])
def test_une_valeur_du_domaine_est_admise(valeur: int) -> None:
    resultat = validate(
        payload(rid(1), "heating_curve_shift", valeur),
        build_production_profile(),
        START,
    )
    assert getattr(resultat, "reason", None) is None
    assert resultat.target == valeur
    assert isinstance(resultat.target, int)


@pytest.mark.parametrize("valeur", [-14, 41])
def test_une_valeur_hors_bornes_est_rejetee(valeur: int) -> None:
    resultat = validate(
        payload(rid(1), "heating_curve_shift", valeur),
        build_production_profile(),
        START,
    )
    assert resultat.reason.value == "invalid_value_out_of_range"


def test_une_valeur_hors_grille_est_rejetee_sans_arrondi() -> None:
    """Le pas est 1 : `2.5` est refuse, jamais arrondi silencieusement."""
    resultat = validate(
        payload(rid(1), "heating_curve_shift", 2.5),
        build_production_profile(),
        START,
    )
    assert resultat.reason.value == "invalid_step"


def test_un_role_inconnu_du_profil_est_rejete() -> None:
    """La liste des roles etant fermee, tout le reste est `unsupported_role`."""
    resultat = validate(
        payload(rid(1), "heating_curve_slope", 1.8),
        build_production_profile(),
        START,
    )
    assert resultat.reason.value == "unsupported_role"


# --------------------------------------------------------------------------
# D. Non-regression : le profil factice reste intact et distinct
# --------------------------------------------------------------------------


def test_le_profil_factice_est_inchange_et_distinct() -> None:
    """W4-D n'a pas touche au double : les tests du coeur en dependent."""
    fake = build_fake_profile()
    assert fake.name == "fake-c3"
    assert sorted(fake.commands) == ["mode", "sonde", "temp_consigne"]
    assert set(fake.commands) & set(build_production_profile().commands) == set()


def test_le_profil_de_production_n_est_construit_nulle_part_en_production() -> None:
    """W4-D livre le profil ; il ne le branche pas. La composition est W4-E.

    Barriere symetrique de celles de W3 : la fabrique existe, et aucun module de
    production ne l'appelle. Un appel apparaissant ici fait echouer ce test.

    AUCUNE EXCLUSION, ET C'EST LE POINT
        Le balayage couvre **tous** les modules de `src/boilerack`, y compris
        chaque `__init__.py`. Exempter un nom de fichier — meme celui qui declare
        la fabrique, meme un paquet — creerait un angle mort ou un appel
        passerait inapercu, et la preuve affirmerait alors plus qu'elle ne
        montre.

        Aucune exemption n'est necessaire : la recherche porte sur un `ast.Call`.
        Ni l'`ImportFrom` de `core/__init__.py`, ni le `FunctionDef` de
        `production_profile.py` n'en sont un. Seul un APPEL est releve.
    """
    racine = pathlib.Path(__file__).resolve().parents[2] / "src" / "boilerack"
    modules = [f for f in racine.rglob("*.py") if "__pycache__" not in f.parts]
    assert any(f.name == "__init__.py" for f in modules), "les paquets sont balayes"

    appelants = []
    for fichier in modules:
        for noeud in ast.walk(ast.parse(fichier.read_text(encoding="utf-8"))):
            if (
                isinstance(noeud, ast.Call)
                and isinstance(noeud.func, ast.Name)
                and noeud.func.id == "build_production_profile"
            ):
                appelants.append(fichier.relative_to(racine).as_posix())
    assert appelants == []
