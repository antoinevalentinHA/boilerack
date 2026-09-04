"""Forme decimale DETERMINISTE d'une valeur numerique.

Module NEUTRE, de premier niveau : il ne connait ni la surface de lecture, ni la
couche adaptateur, ni le coeur. Les deux couches qui en ont besoin l'importent
d'ici, et il n'existe donc qu'UNE autorite pour cette forme.

POURQUOI ICI, ET NON DANS `read_surface`
    La surface de lecture l'a introduit la premiere ; l'adaptateur d'ecriture en
    a besoin depuis la levee de I-8. Or le graphe d'import interdit a la couche
    adaptateur de remonter vers `boilerack.read_surface`, et un test le verifie.

    Deux issues existaient : dupliquer la primitive, ou l'extraire. Dupliquer
    aurait cree une SECONDE autorite pour une seule forme, donc une dette
    immediate. Elle est extraite, et `read_surface.payload` la REEXPORTE : aucun
    de ses consommateurs ne change.

Module PUR : aucune horloge, aucun reseau, aucun processus, aucun etat, aucune
dependance a la locale.
"""

from __future__ import annotations

import math
from decimal import Decimal

__all__ = ["format_scalar"]


def format_scalar(value: float) -> bytes:
    """Serialise une valeur de mesure en payload MQTT (§4.5).

    Strategie : `Decimal(repr(value))` puis formatage positionnel `f`.

    - `repr` donne la representation la plus COURTE qui reconstruit exactement
      le flottant : aucune decimale parasite n'est introduite. `Decimal(value)`
      exposerait au contraire l'expansion binaire complete (`0.1` deviendrait
      55 chiffres) ;
    - le format `f` de `Decimal` est **positionnel** et **insensible a la
      locale** — seul le format `n` est localise. Il n'emet donc jamais de
      notation exponentielle, quelle que soit l'amplitude, ce que `repr` seul ne
      garantit pas (`repr(1e-05)` vaut `'1e-05'`).

    Le zero negatif est ramene au zero positif AVANT formatage : §4.5 exige
    qu'« une valeur negative nulle **MUST** etre serialisee sans signe negatif ».
    La regle porte sur le seul signe ; la precision reste non normative, si bien
    que `-0.0` rend `0.0` et non `0`.

    Leve `ValueError` sur une valeur non finie ou non numerique. Ce chemin n'est
    pas atteignable depuis un `ReadResult` en statut `OK`, dont l'invariant
    durci garantit une valeur presente et finie : c'est une garde contre une
    erreur de programmation, jamais une issue de transport.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        # `isinstance(True, int)` vaut `True` en Python : le booleen est ecarte
        # explicitement, comme dans l'adaptateur de lecture C6.
        raise ValueError(
            f"format_scalar attend un nombre, recu {type(value).__name__}"
        )
    try:
        number = float(value)
    except OverflowError as exc:  # entier trop grand pour un flottant
        raise ValueError(f"valeur non representable en flottant : {value!r}") from exc

    if not math.isfinite(number):
        raise ValueError(f"une valeur non finie n'est pas serialisable : {number!r}")

    if number == 0:
        # Couvre `-0.0` ; `0.0 == -0.0` est vrai, l'affectation retire le signe.
        number = 0.0

    return format(Decimal(repr(number)), "f").encode("utf-8")
