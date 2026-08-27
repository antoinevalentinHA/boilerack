"""Caracterisation du traitement des valeurs numeriques des commandes de consigne.

Source : `legacy_setpoint_value`, extraction de boiler_mqtt.py L572-581
(dhw/set_setpoint) et L628-637 (heating/set_temperature).

Ce chemin est celui des DEUX commandes de consigne. Il se comporte de facon
tres differente du chemin des courbes : il ARRONDIT au lieu de rejeter, et il
ne se protege ni de NaN ni de l'infini.
"""

import pytest

from boilerack._legacy.primitives import (
    DHW_SETPOINT_MAX,
    DHW_SETPOINT_MIN,
    HEATING_TEMPERATURE_MAX,
    HEATING_TEMPERATURE_MIN,
    legacy_setpoint_value,
)


@pytest.mark.reference
@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [(10, 10), (55, 55), (60, 60), (42, 42)],
)
def test_entiers_dans_les_bornes(valeur: int, attendu: int) -> None:
    resultat = legacy_setpoint_value(valeur, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX)
    assert resultat == (True, None, attendu)


@pytest.mark.reference
def test_flottant_exact_representant_un_entier_accepte() -> None:
    """20.0 designe 20 : acceptation conforme a la regle de normalisation P-02."""
    assert legacy_setpoint_value(20.0, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX) == (True, None, 20)


@pytest.mark.reference
@pytest.mark.parametrize("valeur", [9, 61, -5, 1000, 4, 100])
def test_hors_bornes_refuse(valeur: int) -> None:
    assert legacy_setpoint_value(valeur, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX) == (
        False,
        "invalid_value",
        None,
    )


@pytest.mark.reference
@pytest.mark.parametrize("valeur", [True, False])
def test_booleen_refuse_avant_le_test_numerique(valeur: bool) -> None:
    """`isinstance(True, int)` vaut True en Python : la garde explicite est donc
    indispensable, et elle est bien presente."""
    assert legacy_setpoint_value(valeur, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX) == (
        False,
        "invalid_value",
        None,
    )


@pytest.mark.reference
@pytest.mark.parametrize("valeur", ["55", None, [55], {"v": 55}, b"55", object()])
def test_types_non_numeriques_refuses(valeur: object) -> None:
    """Une chaine numerique est refusee : aucune coercition implicite."""
    assert legacy_setpoint_value(valeur, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX) == (
        False,
        "invalid_value",
        None,
    )


@pytest.mark.divergence_ratified
@pytest.mark.parametrize(
    ("entree", "resultat_arrondi"),
    [(20.4, 20), (20.6, 21), (55.49, 55), (55.5, 56), (20.5, 20)],
)
def test_valeur_non_entiere_arrondie_et_acceptee(entree: float, resultat_arrondi: int) -> None:
    """Le chemin des consignes ARRONDIT au lieu de rejeter.

    20.4 est accepte et 20 est ecrit dans la chaudiere. Le demandeur n'en sait
    rien : il recoit `applied`.

    Note : 20.5 donne 20 et non 21 — `round` applique l'arrondi bancaire.

    Classe DIVERGENCE_RATIFIED : la divergence D-1 (arbitrage P-02) supprimera
    cet arrondi, le produit public devant rejeter toute valeur non conforme au
    pas. Ce test devra alors etre inverse de facon tracee.
    """
    assert legacy_setpoint_value(entree, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX) == (
        True,
        None,
        resultat_arrondi,
    )


@pytest.mark.accident
def test_nan_leve_une_exception_au_lieu_d_etre_refuse() -> None:
    """NaN n'est PAS gere sur le chemin des consignes.

    `int(round(float('nan')))` leve ValueError. L'exception remonte jusqu'au
    gestionnaire de commande, qui publie `bridge_exception` sur error/last et
    un ACK `rejected` / `bridge_unavailable` — c'est-a-dire une raison
    TRANSITOIRE pour une erreur de saisie PERMANENTE.

    Les fonctions de courbe, elles, refusent proprement NaN par `invalid_type`.
    L'asymetrie est un defaut reel, non un choix.

    Classe ACCIDENT : le produit public devra rendre `invalid_type`.
    """
    with pytest.raises(ValueError):
        legacy_setpoint_value(float("nan"), DHW_SETPOINT_MIN, DHW_SETPOINT_MAX)


@pytest.mark.accident
@pytest.mark.parametrize("valeur", [float("inf"), float("-inf")])
def test_infini_leve_une_exception_au_lieu_d_etre_refuse(valeur: float) -> None:
    """Meme defaut que pour NaN, avec OverflowError."""
    with pytest.raises(OverflowError):
        legacy_setpoint_value(valeur, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX)


@pytest.mark.reference
def test_les_bornes_sont_bien_appliquees_par_domaine() -> None:
    """Les memes regles servent deux domaines aux bornes differentes."""
    assert legacy_setpoint_value(21, HEATING_TEMPERATURE_MIN, HEATING_TEMPERATURE_MAX)[0] is True
    assert legacy_setpoint_value(55, HEATING_TEMPERATURE_MIN, HEATING_TEMPERATURE_MAX)[0] is False
    assert legacy_setpoint_value(55, DHW_SETPOINT_MIN, DHW_SETPOINT_MAX)[0] is True
