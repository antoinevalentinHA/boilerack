"""Caracterisation de `sanitize_curve_slope` (boiler_mqtt.py L386-426).

Domaine : [0.2 ; 3.5], pas 0.1, tolerance de representation 1e-9.

Point d'attention sur l'ORDRE des controles : normalisation, puis bornes,
puis pas. Une valeur hors bornes ET hors pas rend donc
`invalid_value_out_of_range`, jamais `invalid_step`.
"""

import pytest

from boilerack._legacy.primitives import sanitize_curve_slope


@pytest.mark.reference
@pytest.mark.parametrize(
    ("entree", "normalisee"),
    [(0.2, 0.2), (0.3, 0.3), (1.8, 1.8), (2.4, 2.4), (3.5, 3.5), (1, 1.0), (3, 3.0)],
)
def test_valeurs_exactes_acceptees(entree: float, normalisee: float) -> None:
    assert sanitize_curve_slope(entree) == (True, None, normalisee)


@pytest.mark.reference
@pytest.mark.parametrize(
    ("entree", "normalisee"),
    [
        (0.30000000000000004, 0.3),
        (2.4000000000000004, 2.4),
        (1.7999999999999998, 1.8),
        (0.1 + 0.2, 0.3),
    ],
)
def test_erreurs_flottantes_usuelles_absorbees(entree: float, normalisee: float) -> None:
    """C'est le coeur de la regle : normaliser la REPRESENTATION, pas la VALEUR.

    L'ecart entre 0.30000000000000004 et 0.3 vaut 5.5e-17, tres en dessous de
    la tolerance de 1e-9 : la valeur est acceptee sans etre modifiee.
    """
    assert sanitize_curve_slope(entree) == (True, None, normalisee)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [0.25, 2.37, 1.83, 0.21, 3.44])
def test_valeurs_intermediaires_refusees_sans_arrondi(entree: float) -> None:
    """0.25 n'est pas rapproche de 0.2 : il est refuse.

    C'est la difference decisive avec le chemin des consignes, qui arrondit.
    """
    assert sanitize_curve_slope(entree) == (False, "invalid_step", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [0.1, 0.0, -1.0, 0.14])
def test_hors_borne_basse(entree: float) -> None:
    assert sanitize_curve_slope(entree) == (False, "invalid_value_out_of_range", None)


@pytest.mark.reference
def test_une_valeur_sous_la_borne_peut_etre_refusee_pour_le_pas() -> None:
    """0.19 est sous la borne basse de 0.2, mais se normalise EN 0.2.

    Le controle de bornes porte sur la valeur NORMALISEE : 0.2 y satisfait.
    Le rejet survient donc au controle suivant, pour le pas, et la raison
    rendue est `invalid_step` et non `invalid_value_out_of_range`.

    Une valeur trop basse peut ainsi produire un diagnostic de granularite.
    Comportement reel et non evident, decouvert par ce test.
    """
    assert sanitize_curve_slope(0.19) == (False, "invalid_step", None)
    assert sanitize_curve_slope(0.14) == (False, "invalid_value_out_of_range", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [3.6, 4.0, 20.0, 100])
def test_hors_borne_haute(entree: float) -> None:
    """20.0 est ici refuse pour depassement, non pour le pas."""
    assert sanitize_curve_slope(entree) == (False, "invalid_value_out_of_range", None)


@pytest.mark.unknown
def test_l_ordre_des_controles_est_bornes_puis_pas() -> None:
    """3.54 se normalise en 3.5, donc dans les bornes, puis echoue sur le pas.

    3.94 se normalise en 3.9, hors bornes : la raison rendue est le
    depassement, alors que le pas est egalement invalide. L'ordre des
    controles est donc observable de l'exterieur.

    Classe UNKNOWN et non REFERENCE : le diagnostic rendu quand une valeur
    viole a la fois les bornes ET le pas n'est pas un comportement a conserver,
    mais un artefact de l'ordre des controles, a unifier en C3. Le rejet des
    valeurs simplement hors bornes reste, lui, couvert par les tests REFERENCE
    dedies (test_hors_borne_haute).
    """
    assert sanitize_curve_slope(3.54) == (False, "invalid_step", None)
    assert sanitize_curve_slope(3.94) == (False, "invalid_value_out_of_range", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [True, False])
def test_booleen_refuse(entree: bool) -> None:
    assert sanitize_curve_slope(entree) == (False, "invalid_type", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", ["1.8", None, [1.8], {"v": 1.8}, b"1.8", object()])
def test_types_non_numeriques_refuses(entree: object) -> None:
    assert sanitize_curve_slope(entree) == (False, "invalid_type", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [float("nan"), float("inf"), float("-inf")])
def test_nan_et_infini_refuses_proprement(entree: float) -> None:
    """Contrairement au chemin des consignes, NaN et l'infini sont ici geres."""
    assert sanitize_curve_slope(entree) == (False, "invalid_type", None)


@pytest.mark.accident
def test_la_fonction_ecrit_sur_la_sortie_standard(capsys: pytest.CaptureFixture[str]) -> None:
    """La fonction n'est pas pure : elle appelle `print` sur tous ses chemins.

    Cela empeche de l'utiliser comme fonction de validation dans une
    bibliotheque, pollue la sortie et contourne la journalisation.

    Classe ACCIDENT : le produit public devra journaliser via `logging`, la
    decision restant rendue par une fonction pure.
    """
    sanitize_curve_slope(1.8)
    succes = capsys.readouterr().out
    assert "[INFO] curve_slope" in succes

    sanitize_curve_slope(9.9)
    depassement = capsys.readouterr().out
    assert "[WARN] curve_slope out of range" in depassement

    sanitize_curve_slope("x")
    mauvais_type = capsys.readouterr().out
    assert "[ERROR] curve_slope invalid_type" in mauvais_type
