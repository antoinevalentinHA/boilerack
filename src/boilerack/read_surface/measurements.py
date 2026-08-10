"""Declaration des mesures de la surface de lecture.

Implemente la table normative §4.2 et la politique de fraicheur §7.2 du contrat
`c7-mqtt-read-contract.md`.

POURQUOI PAS `CommandSpec`
    `boilerack.core.profile.CommandSpec` exige `min`, `max`, `step`,
    `confirm_tolerance` et surtout `bounds_source` — « provenance des bornes et
    du pas ». Aucune de ces informations n'existe pour les huit mesures de
    lecture : le contrat n'en fixe ni plage ni tolerance, et aucun profil de
    production n'existe dans le depot. Les remplir reviendrait a inventer une
    provenance. `MeasurementSpec` est donc une structure distincte, strictement
    limitee a ce que la surface de lecture consomme.

CHAMPS DELIBEREMENT ABSENTS
    Ni unite, ni type metier, ni forme scalaire, ni valeur, ni bornes, ni
    tolerance, ni source de bornes. L'instantane §6.2 ne porte aucun de ces
    elements, et C7-C1 a etabli une serialisation uniforme (§4.5 declare les
    formes entiere et decimale toutes deux conformes, §11 declare le payload
    `decimal` pour les huit).

Module PUR : aucune horloge, aucun reseau, aucun processus, aucun etat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Sequence

__all__ = [
    "MeasurementSpec",
    "default_fresh_max",
    "check_snapshot_period",
    "V1_MEASUREMENTS",
]

#: Facteur contractuel du seuil de fraicheur par defaut (§7.2). Le facteur 3 est
#: retenu, et non 2, parce que la duree d'une lecture reelle observee en C5 —
#: 2,7 a 4,0 s — est du meme ordre que certaines periodes.
_FRESH_FACTOR: Final = 3


def _check_positive_int(value: int, field: str) -> int:
    """Refuse ce qui n'est pas un entier strictement positif.

    Le booleen est ecarte explicitement : `isinstance(True, int)` vaut `True`
    en Python, comme dans l'adaptateur de lecture C6.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} doit etre un entier : {value!r}")
    if value <= 0:
        raise ValueError(f"{field} doit etre strictement positif : {value!r}")
    return value


def _check_non_empty(value: str, field: str) -> str:
    if not isinstance(value, str) or value == "":
        raise ValueError(f"{field} doit etre une chaine non vide : {value!r}")
    return value


def default_fresh_max(period_s: int) -> int:
    """Seuil de fraicheur par defaut d'une periode cible : `3 × P` (§7.2)."""
    return _FRESH_FACTOR * _check_positive_int(period_s, "period_s")


@dataclass(frozen=True)
class MeasurementSpec:
    """Declaration d'une mesure de la surface de lecture.

    - `role`   : identifiant public, clef d'indexation de l'instantane (§6.2) ;
    - `read`   : commande de transport, chaine opaque, jamais interpretee ici ;
    - `suffix` : suffixe contractuel MQTT (§11) ;
    - `period_s` : periode de publication visee, non garantie (§4.2, §7) ;
    - `fresh_max_s` : seuil de fraicheur, en secondes (§7.2).

    `read` et `suffix` n'ont AUCUN consommateur d'execution dans ce lot : la
    transition d'etat ne depend que du statut, et l'instantane s'indexe par
    role. Ils sont declares parce que cette structure transcrit la table
    normative §4.2 dans son entier — comme `V1_SUFFIXES` transcrit §11 en C7-C1
    — et parce que C7-C3 les consommera sans avoir a modifier une structure
    deja livree.
    """

    role: str
    read: str
    suffix: str
    period_s: int
    fresh_max_s: int

    def __post_init__(self) -> None:
        _check_non_empty(self.role, "role")
        _check_non_empty(self.read, "read")
        _check_non_empty(self.suffix, "suffix")
        _check_positive_int(self.period_s, "period_s")
        _check_positive_int(self.fresh_max_s, "fresh_max_s")
        if self.fresh_max_s <= self.period_s:
            # §7.2 : « `fresh_max` **MUST** etre strictement superieur a `P` ».
            # Invariant contractuel, pas une prudence ajoutee ici.
            raise ValueError(
                f"[{self.role}] fresh_max_s ({self.fresh_max_s}) doit etre "
                f"strictement superieur a period_s ({self.period_s})"
            )


def _check_collection(specs: Sequence[MeasurementSpec]) -> None:
    """Invariants d'une COLLECTION de mesures, quelle qu'elle soit.

    Rien ici n'impose un nombre d'entrees : la surface v1 en compte huit, mais
    c'est un fait de `V1_MEASUREMENTS` verifie par les tests de conformite, pas
    une propriete d'une declaration generique.

    L'unicite des `read` n'est PAS exigee : le contrat n'interdit nulle part que
    deux roles partagent une commande. Les huit de la v1 sont distincts, ce que
    les tests constatent sans en faire une regle generique.
    """
    roles = [spec.role for spec in specs]
    if len(set(roles)) != len(roles):
        raise ValueError("les roles d'une collection de mesures doivent etre uniques")
    suffixes = [spec.suffix for spec in specs]
    if len(set(suffixes)) != len(suffixes):
        raise ValueError("les suffixes d'une collection de mesures doivent etre uniques")


def check_snapshot_period(
    specs: Sequence[MeasurementSpec], snapshot_period_s: int
) -> None:
    """Verifie §7.4 : la republication ne doit pas depasser la fraicheur.

    « Periode de republication : **MUST** etre inferieure ou egale au plus
    petit `fresh_max` de la surface. » La borne est donc **dynamique** : elle
    depend des mesures reellement declarees, et non d'une constante.

    AUTORITE UNIQUE — cette fonction est le seul endroit du depot ou la regle
    est ecrite. `ReadSurfacePublisher` y delegue, et tout appelant souhaitant
    valider une configuration AVANT de construire quoi que ce soit doit
    l'appeler plutot que recalculer `min(fresh_max_s)` pour son compte : une
    seconde ecriture divergerait au premier changement de la surface.

    SURFACE VIDE — aucune borne n'existe alors, et aucune verification n'est
    faite. Comportement etabli par C7-C3B, conserve ici a l'identique.

    Module PUR : aucune horloge, aucun reseau, aucun processus.
    """
    if not specs:
        return
    plus_petit = min(spec.fresh_max_s for spec in specs)
    if snapshot_period_s > plus_petit:
        raise ValueError(
            f"snapshot_period_s ({snapshot_period_s}) doit etre inferieur ou "
            f"egal au plus petit fresh_max_s de la surface ({plus_petit})"
        )


def _v1() -> tuple[MeasurementSpec, ...]:
    """Transcription litterale de la table normative §4.2, dans son ordre.

    `fresh_max_s` passe par `default_fresh_max` plutot que par une constante
    ecrite a la main : la regle `3 × P` reste visible dans la declaration.
    """
    brut = (
        ("outdoor_temperature", "getTempA", "telemetry/temperatures/outdoor", 30),
        ("supply_temperature", "getTempKist", "telemetry/temperatures/supply", 30),
        ("dhw_temperature", "getTempWWist", "telemetry/temperatures/dhw", 30),
        ("dhw_setpoint", "getTempWWsoll", "telemetry/dhw/setpoint", 60),
        ("heating_setpoint", "getTempRaumNorSollM1", "telemetry/heating/setpoint", 60),
        (
            "heating_reduced_reference",
            "getTempRaumRedSollM1",
            "telemetry/heating/reduced_reference",
            60,
        ),
        ("heating_curve_slope", "getNeigungM1", "telemetry/heating/curve/slope", 60),
        ("heating_curve_shift", "getNiveauM1", "telemetry/heating/curve/shift", 60),
    )
    specs = tuple(
        MeasurementSpec(
            role=role,
            read=read,
            suffix=suffix,
            period_s=period,
            fresh_max_s=default_fresh_max(period),
        )
        for role, read, suffix, period in brut
    )
    _check_collection(specs)
    return specs


#: Les HUIT mesures de la v1 (§4.2), dans l'ordre de la table normative — le
#: meme que celui de `TELEMETRY_SUFFIXES` (§11), ce qu'un test croise verifie.
V1_MEASUREMENTS: Final[tuple[MeasurementSpec, ...]] = _v1()
