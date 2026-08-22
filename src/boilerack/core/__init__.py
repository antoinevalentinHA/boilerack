"""Coeur transactionnel generique de `boilerack`.

Ce paquet contient la logique metier du bridge, entierement testable au travers
des interfaces et des doubles introduits en C2 (horloge, transport `vcontrold`,
transport MQTT). Il ne contient AUCUN transport reel : ni Paho, ni socket, ni
sous-processus, ni acces fichier.

Responsabilites, separees en modules a responsabilite unique :

- `command`  : modele immuable d'une commande admise ;
- `ack`      : modele d'acquittement, statuts fermes, raisons et serialisation ;
- `profile`  : schema declaratif des roles de commande ;
- `validation` : validation generique pilotee par le profil ;
- `dedup`    : registre `in_flight` (volatil) et cache terminal (TTL monotone) ;
- `engine`   : moteur transactionnel qui orchestre le tout.
"""

from __future__ import annotations

from boilerack.core.ack import (
    Ack,
    AckStatus,
    Reason,
    ReasonClass,
    ack_to_json,
)
from boilerack.core.command import Command, CommandFormError
from boilerack.core.dedup import InFlightRegistry, TerminalCache
from boilerack.core.engine import TransactionalCore
from boilerack.core.production_profile import (
    PRODUCTION_PROFILE_NAME,
    build_production_profile,
)
from boilerack.core.profile import CommandSpec, Profile, ProfileError, ValueType
from boilerack.core.validation import Rejection, ValidatedCommand, validate

__all__ = [
    "Ack",
    "AckStatus",
    "Reason",
    "ReasonClass",
    "ack_to_json",
    "Command",
    "CommandFormError",
    "InFlightRegistry",
    "TerminalCache",
    "TransactionalCore",
    "CommandSpec",
    "Profile",
    "ProfileError",
    "ValueType",
    "PRODUCTION_PROFILE_NAME",
    "build_production_profile",
    "Rejection",
    "ValidatedCommand",
    "validate",
]
