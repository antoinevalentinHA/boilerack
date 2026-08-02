"""Modele d'acquittement (ACK) et sa serialisation.

Statuts FERMES et raisons FERMEES. Regles contractuelles :

- `accepted` n'est PAS terminal ; `applied`, `rejected`, `timeout` le sont ;
- `reason` et `reason_class` ne sont presents QUE pour `rejected` ;
- aucun `applied` n'est jamais emis sans relecture conforme (garanti par le
  moteur, pas par ce modele) ;
- chaque raison a une classe FIXE (`permanent` / `temporal` / `transient`).

La serialisation JSON est compacte, UTF-8, deterministe (clefs triees) et
refuse `NaN` / `Infinity` (`allow_nan=False`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum


class AckStatus(str, Enum):
    """Issue d'une transaction, telle que publiee au demandeur."""

    ACCEPTED = "accepted"
    APPLIED = "applied"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class ReasonClass(str, Enum):
    """Nature d'un rejet, pour guider une eventuelle reaction du demandeur."""

    PERMANENT = "permanent"
    TEMPORAL = "temporal"
    TRANSIENT = "transient"


class Reason(str, Enum):
    """Raisons minimales et fermees d'un rejet."""

    INVALID_PAYLOAD = "invalid_payload"
    INVALID_TYPE = "invalid_type"
    # Valeur numeriquement typee mais NON FINIE (`NaN`, `+Inf`, `-Inf`). Le type
    # Python est bien un nombre ; c'est la VALEUR qui n'est pas finie, d'ou une
    # raison distincte de `invalid_type` (qui vise « pas un nombre du tout » :
    # booleen, chaine, objet). Defaut PERMANENT.
    INVALID_VALUE_NON_FINITE = "invalid_value_non_finite"
    INVALID_VALUE_OUT_OF_RANGE = "invalid_value_out_of_range"
    INVALID_STEP = "invalid_step"
    EXPIRED = "expired"
    BRIDGE_UNAVAILABLE = "bridge_unavailable"
    QUEUE_FULL = "queue_full"
    # Ajoutee en C3 (arbitrage 1.b) : la commande d'ecriture declaree par le
    # profil n'est pas reconnue par le transport `vcontrold` reellement
    # installe. Defaut PERMANENT de profil / configuration / compatibilite.
    # A NE PAS confondre avec `invalid_payload` (charge utile mal formee).
    UNSUPPORTED_COMMAND = "unsupported_command"
    # Le role vise par la commande n'offre pas de surface d'ecriture : soit il
    # est absent du profil, soit il y figure en LECTURE SEULE. La charge utile
    # est pourtant bien formee ; ce n'est donc PAS `invalid_payload`. Defaut
    # PERMANENT (profil / configuration). Le `detail` textuel precise le cas
    # exact (role inconnu vs role non inscriptible).
    UNSUPPORTED_ROLE = "unsupported_role"


# Classe FIXE de chaque raison. Une raison n'a qu'une seule classe possible :
# on ne laisse jamais l'appelant en choisir une contradictoire.
REASON_CLASS: dict[Reason, ReasonClass] = {
    Reason.INVALID_PAYLOAD: ReasonClass.PERMANENT,
    Reason.INVALID_TYPE: ReasonClass.PERMANENT,
    Reason.INVALID_VALUE_NON_FINITE: ReasonClass.PERMANENT,
    Reason.INVALID_VALUE_OUT_OF_RANGE: ReasonClass.PERMANENT,
    Reason.INVALID_STEP: ReasonClass.PERMANENT,
    Reason.EXPIRED: ReasonClass.TEMPORAL,
    Reason.BRIDGE_UNAVAILABLE: ReasonClass.TRANSIENT,
    Reason.QUEUE_FULL: ReasonClass.TRANSIENT,
    Reason.UNSUPPORTED_COMMAND: ReasonClass.PERMANENT,
    Reason.UNSUPPORTED_ROLE: ReasonClass.PERMANENT,
}

_TERMINAL_STATUSES = frozenset(
    {AckStatus.APPLIED, AckStatus.REJECTED, AckStatus.TIMEOUT}
)


@dataclass(frozen=True)
class Ack:
    """Acquittement immuable d'une transaction.

    Construire de preference via les fabriques `accepted`, `applied`, `timeout`,
    `rejected`, qui garantissent les invariants. Le constructeur les revalide de
    toute facon.
    """

    request_id: str
    status: AckStatus
    reason: Reason | None = None
    reason_class: ReasonClass | None = None

    def __post_init__(self) -> None:
        if self.status is AckStatus.REJECTED:
            if self.reason is None:
                raise ValueError("un ACK rejected exige une reason.")
            expected = REASON_CLASS[self.reason]
            if self.reason_class is None:
                # Deduit la classe si elle n'a pas ete fournie.
                object.__setattr__(self, "reason_class", expected)
            elif self.reason_class is not expected:
                raise ValueError(
                    f"reason {self.reason.value} impose reason_class "
                    f"{expected.value}, recu {self.reason_class.value}."
                )
        else:
            if self.reason is not None or self.reason_class is not None:
                raise ValueError(
                    f"un ACK {self.status.value} ne porte ni reason ni reason_class."
                )

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL_STATUSES

    # -- fabriques -----------------------------------------------------------

    @classmethod
    def accepted(cls, request_id: str) -> "Ack":
        return cls(request_id=request_id, status=AckStatus.ACCEPTED)

    @classmethod
    def applied(cls, request_id: str) -> "Ack":
        return cls(request_id=request_id, status=AckStatus.APPLIED)

    @classmethod
    def timeout(cls, request_id: str) -> "Ack":
        return cls(request_id=request_id, status=AckStatus.TIMEOUT)

    @classmethod
    def rejected(cls, request_id: str, reason: Reason) -> "Ack":
        return cls(
            request_id=request_id,
            status=AckStatus.REJECTED,
            reason=reason,
            reason_class=REASON_CLASS[reason],
        )


def ack_to_dict(ack: Ack) -> dict:
    """Projection minimale d'un ACK vers un dictionnaire serialisable.

    `reason` / `reason_class` n'apparaissent QUE pour un rejet.
    """
    data: dict[str, str] = {
        "request_id": ack.request_id,
        "status": ack.status.value,
    }
    if ack.status is AckStatus.REJECTED:
        assert ack.reason is not None and ack.reason_class is not None
        data["reason"] = ack.reason.value
        data["reason_class"] = ack.reason_class.value
    return data


def ack_to_json(ack: Ack) -> bytes:
    """Serialise un ACK en JSON compact, UTF-8, deterministe.

    - compact : aucun espace superflu (`separators=(",", ":")`) ;
    - deterministe : clefs triees (`sort_keys=True`) ;
    - strict : `allow_nan=False` refuse `NaN` / `Infinity` (defense en
      profondeur ; un ACK ne porte de toute facon aucun flottant) ;
    - UTF-8 : `ensure_ascii=False` puis encodage explicite.
    """
    text = json.dumps(
        ack_to_dict(ack),
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    return text.encode("utf-8")
