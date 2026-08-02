"""Profil declaratif : schema minimal des roles de commande.

Un profil associe des ROLES generiques a des specifications techniques etroites.
Il ne contient AUCUNE donnee proprietaire : ni adresse Optolink, ni longueur, ni
code d'unite. Les noms de commandes `read` / `write` sont des chaines opaques
transmises telles quelles au transport.

Chaque specification porte la provenance de ses bornes et de son pas
(`bounds_source`), pour qu'aucune borne ne soit introduite sans source.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class ValueType(str, Enum):
    """Type numerique d'une valeur de commande."""

    INTEGER = "integer"
    FLOAT = "float"


class ProfileError(Exception):
    """Schema de profil invalide (defaut de declaration, pas d'execution)."""


def _check_finite(value: float, field: str, role: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ProfileError(f"[{role}] {field} doit etre fini : {value!r}")
    return number


@dataclass(frozen=True)
class CommandSpec:
    """Specification d'un role de commande.

    - `read`  : commande de transport pour relire la valeur (obligatoire) ;
    - `write` : commande de transport pour ecrire ; `None` => role en lecture
      seule, sans aucune surface d'ecriture ;
    - `type`  : `integer` ou `float` ;
    - `min` / `max` : bornes inclusives ;
    - `step`  : pas de la grille de valeurs admissibles (> 0) ;
    - `confirm_tolerance` : tolerance de confirmation par relecture (>= 0) ;
    - `idempotent` : la v1 n'expose QUE des commandes idempotentes (doit etre
      `True`) ;
    - `bounds_source` : provenance des bornes et du pas (chaine non vide).
    """

    role: str
    read: str
    write: str | None
    type: ValueType
    min: float
    max: float
    step: float
    confirm_tolerance: float
    idempotent: bool
    bounds_source: str

    def __post_init__(self) -> None:
        role = self.role
        if not role:
            raise ProfileError("un role doit avoir un identifiant non vide.")
        if not self.read:
            raise ProfileError(f"[{role}] read doit etre une commande non vide.")
        if self.write is not None and self.write == "":
            raise ProfileError(f"[{role}] write vide : utiliser None pour lecture seule.")
        if not isinstance(self.type, ValueType):
            raise ProfileError(f"[{role}] type inconnu : {self.type!r}")
        if not self.idempotent:
            raise ProfileError(
                f"[{role}] la v1 n'expose que des commandes idempotentes."
            )
        if not self.bounds_source:
            raise ProfileError(
                f"[{role}] bounds_source obligatoire : provenance des bornes et du pas."
            )

        low = _check_finite(self.min, "min", role)
        high = _check_finite(self.max, "max", role)
        step = _check_finite(self.step, "step", role)
        tol = _check_finite(self.confirm_tolerance, "confirm_tolerance", role)
        if low > high:
            raise ProfileError(f"[{role}] min ({low}) doit etre <= max ({high}).")
        if step <= 0:
            raise ProfileError(f"[{role}] step doit etre strictement positif : {step!r}")
        if tol < 0:
            raise ProfileError(f"[{role}] confirm_tolerance doit etre >= 0 : {tol!r}")

        if self.type is ValueType.INTEGER:
            for name, number in (("min", low), ("max", high), ("step", step)):
                if not float(number).is_integer():
                    raise ProfileError(
                        f"[{role}] type integer exige un {name} entier : {number!r}"
                    )

    @property
    def writable(self) -> bool:
        """Vrai si le role expose une surface d'ecriture."""
        return self.write is not None


@dataclass(frozen=True)
class Profile:
    """Ensemble de roles de commande, indexes par identifiant de role."""

    name: str
    commands: dict[str, CommandSpec]

    def __post_init__(self) -> None:
        if not self.name:
            raise ProfileError("un profil doit avoir un nom non vide.")
        for role, spec in self.commands.items():
            if spec.role != role:
                raise ProfileError(
                    f"cle de role {role!r} != CommandSpec.role {spec.role!r}."
                )

    def get(self, role: str) -> CommandSpec | None:
        """Specification du role, ou `None` s'il est inconnu du profil."""
        return self.commands.get(role)
