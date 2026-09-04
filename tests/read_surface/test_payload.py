"""Tests de `boilerack.read_surface.payload` — §4.5 de C7-B.

Les assertions portent sur les PROPRIETES exigees par le contrat, non sur une
forme textuelle unique : §4.5 declare la precision decimale « non normative »
et admet les formes entiere et decimale. Ne sont figees exactement que les
regles que le contrat ferme lui-meme, au premier rang desquelles le signe du
zero.
"""

from __future__ import annotations

import ast
import math
import pathlib
import sys

import pytest

from boilerack.read_surface import payload as payload_module
from boilerack.read_surface.payload import format_scalar

#: Echantillon couvrant l'amplitude des flottants finis, signes compris.
_ECHANTILLON = [
    0.0,
    -0.0,
    1.0,
    28.0,
    -12.5,
    0.1,
    2.8,
    1 / 3,
    1e-05,
    1e5,
    1e30,
    1e-30,
    1e300,
    1e-300,
    sys.float_info.min,
    sys.float_info.max,
    -sys.float_info.max,
    5e-324,
    -5e-324,
    sys.float_info.epsilon,
]


def _texte(value: float) -> str:
    return format_scalar(value).decode("utf-8")


# ---------------------------------------------------------------------------
# Type de sortie
# ---------------------------------------------------------------------------


def test_sortie_en_octets() -> None:
    assert isinstance(format_scalar(28.0), bytes)


def test_sortie_encodee_utf8_et_purement_ascii() -> None:
    brut = format_scalar(-12.5)
    assert brut.decode("utf-8") == brut.decode("ascii")


# ---------------------------------------------------------------------------
# §4.5 — forme du payload
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_aucune_notation_exponentielle(valeur: float) -> None:
    texte = _texte(valeur)
    assert "e" not in texte and "E" not in texte


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_aucun_espace(valeur: float) -> None:
    texte = _texte(valeur)
    assert texte == texte.strip()
    assert " " not in texte


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_aucun_guillemet(valeur: float) -> None:
    assert '"' not in _texte(valeur) and "'" not in _texte(valeur)


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_aucune_virgule_le_point_est_le_separateur(valeur: float) -> None:
    assert "," not in _texte(valeur)


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_aucune_unite_ni_caractere_etranger(valeur: float) -> None:
    """Seuls chiffres, point et signe negatif de tete sont admis."""
    texte = _texte(valeur)
    corps = texte[1:] if texte.startswith("-") else texte
    assert set(corps) <= set("0123456789.")


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_payload_analysable_comme_un_nombre_fini(valeur: float) -> None:
    """« analysable comme un nombre fini » : le tour est exact, sans perte."""
    relu = float(_texte(valeur))
    assert math.isfinite(relu)
    assert relu == valeur


# ---------------------------------------------------------------------------
# §4.5 — cas nommes par le contrat
# ---------------------------------------------------------------------------


def test_entier_positif() -> None:
    assert float(_texte(28.0)) == 28.0


def test_decimal_positif() -> None:
    assert float(_texte(2.8)) == 2.8


def test_valeur_negative() -> None:
    texte = _texte(-12.5)
    assert texte.startswith("-")
    assert float(texte) == -12.5


def test_zero_positif() -> None:
    assert float(_texte(0.0)) == 0.0
    assert not _texte(0.0).startswith("-")


def test_zero_negatif_serialise_sans_signe() -> None:
    """§4.5 : « une valeur negative nulle **MUST** etre serialisee sans signe negatif »."""
    texte = _texte(-0.0)
    assert not texte.startswith("-")
    assert float(texte) == 0.0


def test_zero_negatif_conserve_une_forme_decimale() -> None:
    """La regle porte sur le SEUL signe ; elle ne fixe pas la precision."""
    assert _texte(-0.0) == _texte(0.0)


def test_forme_entiere_et_forme_decimale_sont_toutes_deux_admises() -> None:
    """§4.5 : `28` et `28.0` sont conformes. Aucune n'est imposee."""
    for candidat in ("28", "28.0", "28.000000"):
        assert float(candidat) == 28.0


def test_meme_fonction_pour_les_mesures_declarees_entieres() -> None:
    """§11 declare le payload `decimal` pour les HUIT mesures.

    Une valeur non entiere sur une mesure rangee en type `entier` par §4.2 est
    serialisee telle quelle : cette primitive n'arrondit pas, ne tronque pas et
    ne connait pas la mesure.
    """
    assert float(_texte(18.5)) == 18.5


# ---------------------------------------------------------------------------
# §6.1 du cadrage — bornes de representation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "valeur",
    [1e-05, 1e-30, 1e30, 1e300, 5e-324, sys.float_info.min, sys.float_info.max],
)
def test_valeurs_rendues_en_exponentielle_par_repr_restent_positionnelles(
    valeur: float,
) -> None:
    assert "e" in repr(valeur)  # `repr` seul ne suffirait pas
    assert "e" not in _texte(valeur)


def test_plus_petit_subnormal_positif() -> None:
    texte = _texte(5e-324)
    assert texte.startswith("0.00000")
    assert float(texte) == 5e-324


def test_plus_grande_valeur_finie() -> None:
    """Rendue en forme ENTIERE (309 chiffres, aucun point) — §4.5 l'autorise."""
    texte = _texte(sys.float_info.max)
    assert "." not in texte
    assert len(texte) == 309
    assert float(texte) == sys.float_info.max


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_longueur_bornee(valeur: float) -> None:
    """Borne mesuree : 327 caracteres, atteinte par le subnormal negatif.

    1 signe + `0.` + 307 zeros + 17 chiffres significatifs. Aucune limite
    artificielle n'est imposee : le contrat n'en fixe aucune.
    """
    assert len(format_scalar(valeur)) <= 327


def test_borne_atteinte_par_le_subnormal_negatif() -> None:
    assert len(format_scalar(-5e-324)) == 327


# ---------------------------------------------------------------------------
# §4.5 — refus
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "valeur", [float("nan"), float("inf"), float("-inf"), -float("nan")]
)
def test_valeurs_non_finies_refusees(valeur: float) -> None:
    with pytest.raises(ValueError, match="non finie"):
        format_scalar(valeur)


@pytest.mark.parametrize("valeur", [None, "28.0", b"28.0", [28.0], {"v": 1}])
def test_valeurs_non_numeriques_refusees(valeur: object) -> None:
    with pytest.raises(ValueError, match="attend un nombre"):
        format_scalar(valeur)  # type: ignore[arg-type]


@pytest.mark.parametrize("valeur", [True, False])
def test_booleens_refuses(valeur: bool) -> None:
    """`isinstance(True, int)` vaut `True` : le booleen est ecarte explicitement."""
    with pytest.raises(ValueError, match="attend un nombre"):
        format_scalar(valeur)  # type: ignore[arg-type]


def test_entier_trop_grand_pour_un_flottant_refuse() -> None:
    with pytest.raises(ValueError, match="non representable"):
        format_scalar(10**400)  # type: ignore[arg-type]


def test_entier_python_accepte() -> None:
    assert float(_texte(28)) == 28.0  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Determinisme et absence d'effet de bord
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("valeur", _ECHANTILLON)
def test_deterministe(valeur: float) -> None:
    assert format_scalar(valeur) == format_scalar(valeur)


_INTERDITS = {
    "paho",
    "socket",
    "subprocess",
    "threading",
    "asyncio",
    "time",
    "datetime",
    "os",
    "pathlib",
    "locale",
}


def _modules_importes(module: object) -> set[str]:
    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")  # type: ignore[arg-type]
    noms: set[str] = set()
    for noeud in ast.walk(ast.parse(source)):
        if isinstance(noeud, ast.Import):
            noms.update(alias.name.split(".")[0] for alias in noeud.names)
        elif isinstance(noeud, ast.ImportFrom) and noeud.module:
            noms.add(noeud.module.split(".")[0])
    return noms


def test_module_sans_dependance_technique() -> None:
    """Ni MQTT, ni `vclient`, ni horloge, ni processus, ni socket, ni locale."""
    assert _modules_importes(payload_module) & _INTERDITS == set()


def test_module_ne_depend_que_du_siege_neutre_de_la_forme() -> None:
    """La PURETE est conservee, elle a seulement change de siege.

    `format_scalar` vit desormais dans `boilerack.decimal_form`, module neutre
    de premier niveau, parce que la couche adaptateur en a besoin et n'a pas le
    droit de remonter vers `read_surface`. Ce module le REEXPORTE : §4.5 demeure
    l'autorite contractuelle de la forme.

    L'invariant reste donc entier, et il est verifie AUX DEUX endroits : ce
    module n'importe rien d'autre du projet, et le siege n'importe rien du tout.
    """
    complets = {
        noeud.module
        for noeud in ast.walk(
            ast.parse(
                pathlib.Path(payload_module.__file__).read_text(encoding="utf-8")
            )
        )
        if isinstance(noeud, ast.ImportFrom) and noeud.module
    }
    assert {m for m in complets if m.startswith("boilerack")} == {
        "boilerack.decimal_form"
    }


def test_le_siege_neutre_ne_depend_d_aucune_partie_du_projet() -> None:
    """`decimal_form` est sous tout le monde : il n'importe rien de `boilerack`."""
    from boilerack import decimal_form as siege

    assert "boilerack" not in _modules_importes(siege)
