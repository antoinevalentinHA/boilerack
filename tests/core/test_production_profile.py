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


def test_les_quatre_roles_du_pont_historique_et_pas_un_de_plus() -> None:
    """Parite de remplacement : exactement les quatre roles que le pont ecrit.

    Liste FERMEE : un cinquieme role fait echouer ce test, ce qui est exactement
    l'effet recherche. Le pont historique `boiler_mqtt.py` v0.5 en ecrit quatre,
    tous reellement utilises par ses consommateurs aval ; en declarer moins
    interdirait le remplacement, en declarer plus ouvrirait une surface que rien
    n'appelle.
    """
    profile = build_production_profile()
    assert sorted(profile.commands) == [
        "dhw_setpoint",
        "heating_curve_shift",
        "heating_curve_slope",
        "heating_setpoint",
    ]


def test_les_quatre_roles_sont_tous_inscriptibles() -> None:
    """Aucun role du profil de production n'est en lecture seule."""
    profile = build_production_profile()
    assert all(spec.writable for spec in profile.commands.values())


def test_seule_la_pente_est_flottante() -> None:
    """Trois roles entiers a tolerance nulle, un seul flottant.

    La tolerance de la pente est une tolerance de REPRESENTATION : elle vaut
    `1e-9`, soit cent millions de fois moins qu'un cran de pente (`0.1`).
    """
    from boilerack.core.profile import ValueType

    profile = build_production_profile()
    flottants = {
        role for role, spec in profile.commands.items() if spec.type is ValueType.FLOAT
    }
    assert flottants == {"heating_curve_slope"}

    for role, spec in profile.commands.items():
        if role == "heating_curve_slope":
            assert spec.confirm_tolerance == 1e-9
            assert spec.confirm_tolerance < spec.step / 1_000_000
        else:
            assert spec.confirm_tolerance == 0.0


def test_les_bornes_sont_celles_du_pont_historique() -> None:
    """Chaque borne est celle que le pont historique applique en production."""
    profile = build_production_profile()
    attendu = {
        "dhw_setpoint": (10.0, 60.0, 1.0),
        "heating_setpoint": (5.0, 30.0, 1.0),
        "heating_curve_shift": (-13.0, 40.0, 1.0),
        "heating_curve_slope": (0.2, 3.5, 0.1),
    }
    obtenu = {
        role: (spec.min, spec.max, spec.step)
        for role, spec in profile.commands.items()
    }
    assert obtenu == attendu


def test_chaque_role_cite_sa_provenance_de_bornes() -> None:
    """`bounds_source` non vide et DISTINCTE par role : aucune borne recopiee."""
    profile = build_production_profile()
    sources = [spec.bounds_source for spec in profile.commands.values()]
    assert all(sources)
    assert len(set(sources)) == len(sources)


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
    """La liste des roles etant fermee, tout le reste est `unsupported_role`.

    Le role temoin est une grandeur que le pont historique NE publie ni n'ecrit :
    la temperature de depart, qui est une mesure et non une consigne.
    """
    resultat = validate(
        payload(rid(1), "supply_temperature", 30.0),
        build_production_profile(),
        START,
    )
    assert resultat.reason.value == "unsupported_role"


def test_la_pente_est_acceptee_sur_sa_grille_et_rejetee_hors_grille() -> None:
    """La pente accepte les crans de 0.1 et rejette ce qui tombe entre eux."""
    from boilerack.core.validation import ValidatedCommand

    profile = build_production_profile()

    accepte = validate(payload(rid(2), "heating_curve_slope", 1.8), profile, START)
    assert isinstance(accepte, ValidatedCommand)
    assert accepte.target == pytest.approx(1.8)

    hors_grille = validate(payload(rid(3), "heating_curve_slope", 1.85), profile, START)
    assert not isinstance(hors_grille, ValidatedCommand)

    hors_borne = validate(payload(rid(4), "heating_curve_slope", 3.6), profile, START)
    assert not isinstance(hors_borne, ValidatedCommand)


def test_l_ecs_est_bornee_et_ne_descend_pas_sous_dix() -> None:
    """`dhw_setpoint` refuse ce qui sort de [10 ; 60], sans jamais ramener.

    REJECT, jamais clamp : `9` ne devient pas `10`, et `61` ne devient pas `60`.
    """
    from boilerack.core.validation import ValidatedCommand

    profile = build_production_profile()

    for valeur in (10, 60):
        admise = validate(payload(rid(5), "dhw_setpoint", valeur), profile, START)
        assert isinstance(admise, ValidatedCommand)
        assert admise.target == valeur

    for valeur in (9, 61):
        refusee = validate(payload(rid(6), "dhw_setpoint", valeur), profile, START)
        assert not isinstance(refusee, ValidatedCommand)


def test_la_consigne_chauffage_est_bornee() -> None:
    """`heating_setpoint` refuse ce qui sort de [5 ; 30]."""
    from boilerack.core.validation import ValidatedCommand

    profile = build_production_profile()

    for valeur in (5, 30):
        admise = validate(payload(rid(7), "heating_setpoint", valeur), profile, START)
        assert isinstance(admise, ValidatedCommand)

    for valeur in (4, 31):
        refusee = validate(payload(rid(8), "heating_setpoint", valeur), profile, START)
        assert not isinstance(refusee, ValidatedCommand)


# --------------------------------------------------------------------------
# D. Non-regression : le profil factice reste intact et distinct
# --------------------------------------------------------------------------


def test_le_profil_factice_est_inchange_et_distinct() -> None:
    """W4-D n'a pas touche au double : les tests du coeur en dependent."""
    fake = build_fake_profile()
    assert fake.name == "fake-c3"
    assert sorted(fake.commands) == ["mode", "sonde", "temp_consigne"]
    assert set(fake.commands) & set(build_production_profile().commands) == set()


def test_le_profil_de_production_n_est_construit_que_par_lifecycle() -> None:
    """W4-D livrait le profil sans le brancher ; W4-E2 le branche, sous autorite.

    Liste FERMEE, et non plus absence : `lifecycle.py` est le seul lieu de
    DECISION (W4-E1 §6). Un second appelant fait echouer ce test.

    AUCUNE EXEMPTION DE FICHIER, ET C'EST LE POINT
        Le balayage couvre **tous** les modules de `src/boilerack`, y compris
        chaque `__init__.py`. Exempter un nom — meme celui qui declare la
        fabrique, meme un paquet — creerait un angle mort ou un appel passerait
        inapercu.

        Aucune exemption n'est necessaire : la recherche porte sur un `ast.Call`.
        Ni l'`ImportFrom` de `core/__init__.py`, ni le `FunctionDef` de
        `production_profile.py` n'en sont un. Seul un APPEL est releve, ce qui
        laisse `lifecycle.py` apparaitre nommement dans la liste plutot que par
        exemption.

    Ce que cette barriere ne dit PAS : que le profil n'est construit que sous
    autorite. Elle constate le LIEU ; la CONDITION est prouvee sur la couture
    reelle par les deux tests
    `tests/test_lifecycle.py::test_le_cycle_de_vie_*_fabrique_si_l_autorite_est_*`,
    fermee puis ouverte.
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
    assert sorted(appelants) == ["lifecycle.py"]
