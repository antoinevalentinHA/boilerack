"""Caracterisation de `sanitize_curve_shift` (boiler_mqtt.py L429-469).

Domaine : [-13 ; 40], pas 1 (entier strict), tolerance de representation 1e-9.

Point d'attention : l'ORDRE des controles est INVERSE de celui de la pente —
pas d'abord, bornes ensuite. Une valeur hors bornes ET non entiere rend donc
`invalid_step`, la ou la pente aurait rendu `invalid_value_out_of_range`.
"""

import pytest

from boilerack._legacy.primitives import sanitize_curve_shift


@pytest.mark.reference
@pytest.mark.parametrize("entree", [-13, -1, 0, 2, 7, 39, 40])
def test_entiers_dans_les_bornes(entree: int) -> None:
    assert sanitize_curve_shift(entree) == (True, None, entree)


@pytest.mark.reference
@pytest.mark.parametrize(("entree", "normalisee"), [(7.0, 7), (-13.0, -13), (40.0, 40), (0.0, 0)])
def test_flottant_exact_representant_un_entier_accepte(entree: float, normalisee: int) -> None:
    """7.0 designe 7 : normalisation de representation, pas correction de valeur."""
    resultat = sanitize_curve_shift(entree)
    assert resultat == (True, None, normalisee)
    assert isinstance(resultat[2], int)


@pytest.mark.reference
@pytest.mark.parametrize(("entree", "normalisee"), [(7.0000000001, 7), (6.9999999999, 7)])
def test_artefacts_de_representation_absorbes(entree: float, normalisee: int) -> None:
    """L'ecart est inferieur a la tolerance de 1e-9 : la valeur est acceptee."""
    assert sanitize_curve_shift(entree) == (True, None, normalisee)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [7.2, -0.5, 0.1, 39.9, 7.00001])
def test_flottant_non_entier_refuse_sans_arrondi(entree: float) -> None:
    """7.2 n'est pas rapproche de 7 : il est refuse."""
    assert sanitize_curve_shift(entree) == (False, "invalid_step", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [-14, -100, 41, 128, 1000])
def test_hors_bornes_refuse(entree: int) -> None:
    assert sanitize_curve_shift(entree) == (False, "invalid_value_out_of_range", None)


@pytest.mark.unknown
def test_l_ordre_des_controles_est_pas_puis_bornes() -> None:
    """100.5 est hors bornes ET non entier : la raison rendue est `invalid_step`.

    L'ordre est l'inverse de celui de la pente. Deux commandes de la meme
    famille rendent donc des diagnostics differents pour une erreur de meme
    nature.

    Classe UNKNOWN et non REFERENCE : le diagnostic rendu quand une valeur
    viole a la fois les bornes ET le pas n'est pas un comportement a conserver,
    mais un artefact de l'ordre des controles, a unifier en C3. Le rejet des
    valeurs simplement hors bornes reste, lui, couvert par les tests REFERENCE
    dedies (test_hors_bornes_refuse).
    """
    assert sanitize_curve_shift(100.5) == (False, "invalid_step", None)
    assert sanitize_curve_shift(100) == (False, "invalid_value_out_of_range", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [True, False])
def test_booleen_refuse(entree: bool) -> None:
    assert sanitize_curve_shift(entree) == (False, "invalid_type", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", ["7", None, [7], {"v": 7}, b"7", object()])
def test_types_non_numeriques_refuses(entree: object) -> None:
    assert sanitize_curve_shift(entree) == (False, "invalid_type", None)


@pytest.mark.reference
@pytest.mark.parametrize("entree", [float("nan"), float("inf"), float("-inf")])
def test_nan_et_infini_refuses_proprement(entree: float) -> None:
    assert sanitize_curve_shift(entree) == (False, "invalid_type", None)


@pytest.mark.accident
def test_la_fonction_ecrit_sur_la_sortie_standard(capsys: pytest.CaptureFixture[str]) -> None:
    """Meme defaut de purete que pour la pente. Classe ACCIDENT."""
    sanitize_curve_shift(7)
    assert "[INFO] curve_shift" in capsys.readouterr().out

    sanitize_curve_shift(7.2)
    assert "[WARN] curve_shift invalid_step" in capsys.readouterr().out

    sanitize_curve_shift("x")
    assert "[ERROR] curve_shift invalid_type" in capsys.readouterr().out


@pytest.mark.unknown
def test_valeur_zero_acceptee_alors_que_son_sens_physique_n_est_pas_documente() -> None:
    """0 est dans [-13 ; 40] et donc accepte.

    Aucune source consultee — ni le fichier de definition de l'installation, ni
    la documentation constructeur — n'etablit que 0 soit une valeur de decalage
    valide, ni ce qu'elle signifie physiquement.

    Classe UNKNOWN : comportement observe, sens non demontre.
    """
    assert sanitize_curve_shift(0) == (True, None, 0)
