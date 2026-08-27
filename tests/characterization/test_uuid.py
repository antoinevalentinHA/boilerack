"""Caracterisation de `validate_uuid4_string` (boiler_mqtt.py L526-535).

Ces tests decrivent le comportement ACTUEL de la production. Ils ne
constituent pas le contrat du produit final : voir la classification par
marqueur sur chaque cas.
"""

import pytest

from boilerack._legacy.primitives import validate_uuid4_string

CANONIQUE = "550e8400-e29b-41d4-a716-446655440000"


@pytest.mark.reference
@pytest.mark.parametrize(
    ("valeur", "attendu", "commentaire"),
    [
        (CANONIQUE, True, "UUID v4 canonique minuscule"),
        (CANONIQUE.replace("-", ""), False, "forme sans tirets refusee"),
        ("", False, "chaine vide"),
        ("pas-un-uuid", False, "chaine quelconque"),
        (
            "550e8400-e29b-11d4-a716-446655440000",
            False,
            "UUID v1 : les bits de version sont forces, la comparaison echoue",
        ),
        (
            "00000000-0000-0000-0000-000000000000",
            False,
            "UUID nil : version forcee a 4, ne correspond plus",
        ),
        ("550e8400-e29b-41d4-a716-44665544000", False, "un caractere manquant"),
        ("550e8400-e29b-41d4-a716-4466554400000", False, "un caractere en trop"),
        (f"  {CANONIQUE}  ", False, "espaces avant/apres : aucun strip, refuse"),
        (f"{CANONIQUE}\n", False, "retour a la ligne final refuse"),
    ],
)
def test_formes_de_chaines(valeur: str, attendu: bool, commentaire: str) -> None:
    assert validate_uuid4_string(valeur) is attendu, commentaire


@pytest.mark.reference
@pytest.mark.parametrize(
    "valeur",
    [None, 42, 3.14, True, b"550e8400-e29b-41d4-a716-446655440000", ["x"], {"a": 1}, object()],
)
def test_types_non_chaines_refuses(valeur: object) -> None:
    """Le garde `isinstance(value, str)` precede toute tentative de parsing."""
    assert validate_uuid4_string(valeur) is False


@pytest.mark.accident
def test_majuscules_acceptees_malgre_la_documentation() -> None:
    """La forme MAJUSCULE est ACCEPTEE.

    La comparaison finale est `str(parsed) == value.lower()` : elle abaisse la
    casse de l'entree, si bien qu'un UUID entierement en majuscules passe.

    Le contrat du consommateur d'origine decrit pourtant une "forme canonique lowercase, validee
    strictement". La documentation et l'implementation divergent ; c'est
    l'implementation qui a raison ici, et ce test le prouve.

    Classe ACCIDENT : a trancher explicitement en C3. Accepter les majuscules
    est defendable, mais doit alors etre ecrit dans le contrat public.
    """
    assert validate_uuid4_string(CANONIQUE.upper()) is True


@pytest.mark.accident
def test_forme_urn_et_accolades_refusees() -> None:
    """`uuid.UUID` accepte ces formes au parsing, mais la comparaison les rejette.

    Le rejet est donc obtenu par effet de bord de la comparaison, non par une
    validation explicite de forme.
    """
    assert validate_uuid4_string(f"urn:uuid:{CANONIQUE}") is False
    assert validate_uuid4_string("{" + CANONIQUE + "}") is False
