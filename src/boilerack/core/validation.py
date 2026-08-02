"""Validation generique pilotee par le profil.

Applique, dans un ORDRE explicite et teste, les etapes de validation d'une
commande. La premiere cause rencontree emporte le verdict : il n'y a pas de
cumul de raisons.

Ordre (cf. doctrine C3) :

1. forme du payload (structure, UUID, dates aware, valeur numerique finie) ;
2. type (booleen refuse, non nombre refuse) ;
3. finitude (`NaN` / `Inf` refuses) ;
4. borne (`min` <= value <= `max`) ;
5. pas (value sur la grille definie par `step`) ;
6. expiration (`now >= expires_at`).

Les etapes 1 a 3 sont portees par `boilerack.core.command.parse_command`. Les
etapes 4 a 6 sont pilotees par le profil. La resolution du role (role inconnu,
role en lecture seule) precede les bornes : sans surface d'ecriture, borne et
pas n'ont pas de sens.

Doctrine RATIFIEE :

- REJECT, jamais clamp : une valeur hors borne ou hors pas est rejetee, jamais
  ramenee dans la plage ni arrondie ;
- normalisation de REPRESENTATION seulement : `20.0` peut representer l'entier
  `20` ; `20.4` n'est jamais arrondi et, hors grille, est rejete ;
- la comparaison de pas est ROBUSTE (pas de modulo flottant naif).

Priorite borne / pas : la borne (etape 4) est verifiee AVANT le pas (etape 5).
Une valeur a la fois hors borne et hors pas est donc rejetee pour hors borne.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime

from boilerack.core.ack import Reason
from boilerack.core.command import Command, CommandFormError, parse_command
from boilerack.core.profile import CommandSpec, Profile, ValueType

# Tolerance de comparaison pour la grille de pas. Absolue et relative, pour
# absorber les artefacts de representation flottante SANS jamais accepter une
# valeur reellement hors grille (ex. 20.4 avec un pas de 0.5).
_GRID_ABS_TOL = 1e-9
_GRID_REL_TOL = 1e-9


@dataclass(frozen=True)
class ValidatedCommand:
    """Commande admise, resolue contre le profil.

    `target` est la valeur NORMALISEE a ecrire puis a confirmer : `int` pour un
    role entier (ex. `20.0` -> `20`), `float` pour un role flottant.
    """

    command: Command
    spec: CommandSpec
    target: int | float


@dataclass(frozen=True)
class Rejection:
    """Rejet de validation, porteur d'une raison typee et d'un detail."""

    reason: Reason
    detail: str = ""


def _on_grid(value: float, minimum: float, step: float) -> bool:
    """Vrai si `value` appartient a la grille `minimum + k*step` (k entier >= 0).

    Utilise l'indice de grille le plus proche puis une comparaison robuste, au
    lieu d'un modulo flottant naif qui echouerait sur des valeurs comme 20.4.
    """
    index = round((value - minimum) / step)
    reconstructed = minimum + index * step
    return math.isclose(
        reconstructed, value, rel_tol=_GRID_REL_TOL, abs_tol=_GRID_ABS_TOL
    )


def _normalize_target(value: float, spec: CommandSpec) -> int | float:
    if spec.type is ValueType.INTEGER:
        # `value` est deja sur la grille entiere (verifie par le pas) : la
        # conversion est exacte, sans arrondi silencieux d'une valeur hors grille.
        return int(round(value))
    return float(value)


def validate(payload: bytes, profile: Profile, now: datetime) -> ValidatedCommand | Rejection:
    """Valide une commande brute contre un profil, a l'instant `now`.

    Renvoie `ValidatedCommand` si admise, `Rejection` sinon. Ne leve jamais pour
    une entree simplement invalide : les erreurs de forme sont converties en
    `Rejection` typees.
    """
    # Etapes 1-3 : forme, type, finitude.
    try:
        command = parse_command(payload)
    except CommandFormError as exc:
        return Rejection(exc.reason, exc.detail)

    # Resolution du role (avant bornes/pas : pas de surface -> pas de sens).
    spec = profile.get(command.role)
    if spec is None:
        return Rejection(
            Reason.INVALID_PAYLOAD, f"role inconnu du profil : {command.role!r}"
        )
    if not spec.writable:
        return Rejection(
            Reason.INVALID_PAYLOAD,
            f"role en lecture seule, aucune surface d'ecriture : {command.role!r}",
        )

    value = float(command.value)

    # Etape 4 : borne (inclusive).
    if value < spec.min or value > spec.max:
        return Rejection(
            Reason.INVALID_VALUE_OUT_OF_RANGE,
            f"value {command.value!r} hors [{spec.min}, {spec.max}]",
        )

    # Etape 5 : pas (grille). Jamais d'arrondi de la valeur : hors grille = rejet.
    if not _on_grid(value, spec.min, spec.step):
        return Rejection(
            Reason.INVALID_STEP,
            f"value {command.value!r} hors grille (min={spec.min}, step={spec.step})",
        )

    # Etape 6 : expiration.
    if now >= command.expires_at:
        return Rejection(
            Reason.EXPIRED, f"commande expiree : now={now} >= {command.expires_at}"
        )

    return ValidatedCommand(
        command=command,
        spec=spec,
        target=_normalize_target(value, spec),
    )
