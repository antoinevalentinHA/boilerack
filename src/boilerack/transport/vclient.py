"""Frontiere de transport vers un demon `vcontrold`.

Interface ETROITE : uniquement ce dont le futur bridge aura besoin pour lire et
ecrire une valeur, et pour distinguer les issues possibles d'une operation.

Le transport ignore deliberement MQTT, les ACK, le profil de chaudiere, Home
Assistant et toute politique de retry. Il ne decide de rien : il rend compte.

Les issues sont TYPEES par un `enum` et portees par des `dataclass` de resultat.
Aucune cause n'est absorbee dans un `None` : `None` sur `value` signifie
seulement « pas de valeur numerique », et le pourquoi est toujours dans `status`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable


class TransportStatus(Enum):
    """Issue d'une operation de transport, independante de tout metier."""

    OK = "ok"
    """Lecture ou ecriture reussie au niveau transport."""

    DAEMON_UNREACHABLE = "daemon_unreachable"
    """Le demon `vcontrold` n'est pas joignable."""

    UNKNOWN_COMMAND = "unknown_command"
    """La commande est inconnue du demon ou refusee par lui."""

    TIMEOUT = "timeout"
    """Aucune reponse dans le delai imparti."""

    UNUSABLE_OUTPUT = "unusable_output"
    """Le demon a repondu, mais la sortie est inexploitable (vide, non numerique)."""

    TRANSPORT_ERROR = "transport_error"
    """Toute autre erreur de transport, non couverte par les cas ci-dessus."""


@dataclass(frozen=True)
class ReadResult:
    """Resultat d'une lecture.

    Invariant DURCI (C3) : le statut et la valeur ne peuvent jamais se
    contredire.

    - `status is OK` implique une `value` presente ET finie (jamais `None`,
      jamais `NaN`, jamais infinie) : un succes de transport porte toujours un
      nombre exploitable ;
    - `status is not OK` implique `value is None` : aucune valeur numerique
      n'accompagne un echec, et le « pourquoi » reste dans `status`.

    `raw` porte la sortie brute du transport quand elle existe, y compris dans
    le cas `UNUSABLE_OUTPUT`, pour permettre un diagnostic.
    """

    status: TransportStatus
    value: float | None = None
    raw: str | None = None
    detail: str = ""

    def __post_init__(self) -> None:
        if self.status is TransportStatus.OK:
            if self.value is None:
                raise ValueError("ReadResult OK exige une value non nulle.")
            if not math.isfinite(self.value):
                raise ValueError(
                    f"ReadResult OK exige une value finie : {self.value!r}"
                )
        elif self.value is not None:
            raise ValueError(
                f"ReadResult non-OK ({self.status.value}) exige value is None, "
                f"recu {self.value!r}"
            )

    @property
    def ok(self) -> bool:
        return self.status is TransportStatus.OK


@dataclass(frozen=True)
class WriteResult:
    """Resultat d'une ecriture au niveau transport.

    « Ecriture reussie au niveau transport » signifie que le demon a accepte la
    commande, PAS que la chaudiere a confirme la valeur par relecture : cette
    confirmation releve du coeur, en C3, pas du transport.
    """

    status: TransportStatus
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status is TransportStatus.OK


@runtime_checkable
class VClient(Protocol):
    """Transport minimal : lire une valeur, ecrire une valeur.

    Les noms de commandes sont des chaines opaques pour le transport. Aucun
    datapoint de production n'est cable ici.
    """

    def read(self, command: str) -> ReadResult:
        ...

    def write(self, command: str, value: float) -> WriteResult:
        ...
