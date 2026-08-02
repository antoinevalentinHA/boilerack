"""Profil FACTICE minimal pour les tests du coeur (C3).

Aucune commande reelle de chaudiere, aucune donnee proprietaire : uniquement des
roles generiques dont les bornes sont explicitement marquees comme fictives. Le
profil reel de production est hors perimetre C3.
"""

from __future__ import annotations

from boilerack.core.profile import CommandSpec, Profile, ValueType

_FAKE_SOURCE = "profil factice C3 (test) — bornes fictives, aucune donnee de production"


def build_fake_profile() -> Profile:
    """Construit un profil factice couvrant les cas de test C3.

    Roles :

    - `temp_consigne` : flottant, [10.0, 30.0], pas 0.5, tolerance 0.2 ;
    - `mode` : entier, [0, 3], pas 1, tolerance 0.0 (comparaison exacte) ;
    - `sonde` : flottant en LECTURE SEULE (aucune surface d'ecriture).
    """
    specs = [
        CommandSpec(
            role="temp_consigne",
            read="get_temp_consigne",
            write="set_temp_consigne",
            type=ValueType.FLOAT,
            min=10.0,
            max=30.0,
            step=0.5,
            confirm_tolerance=0.2,
            idempotent=True,
            bounds_source=_FAKE_SOURCE,
        ),
        CommandSpec(
            role="mode",
            read="get_mode",
            write="set_mode",
            type=ValueType.INTEGER,
            min=0,
            max=3,
            step=1,
            confirm_tolerance=0.0,
            idempotent=True,
            bounds_source=_FAKE_SOURCE,
        ),
        CommandSpec(
            role="sonde",
            read="get_sonde",
            write=None,
            type=ValueType.FLOAT,
            min=-50.0,
            max=150.0,
            step=0.1,
            confirm_tolerance=0.1,
            idempotent=True,
            bounds_source=_FAKE_SOURCE,
        ),
    ]
    return Profile(name="fake-c3", commands={spec.role: spec for spec in specs})
