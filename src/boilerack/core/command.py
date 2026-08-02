"""Modele immuable d'une commande admise par le coeur.

Le decodage du payload brut et la validation de forme sont STRICTEMENT separes
de l'execution : le coeur ne recoit jamais un dictionnaire non valide dans sa
partie d'execution. `parse_command` transforme des octets bruts en `Command`
immuable ou leve `CommandFormError` portant une raison typee.

Ce module ne connait NI profil, NI bornes, NI pas : il ne verifie que la FORME
(champs presents, types de base, UUID canonique, dates aware, valeur numerique
finie non booleenne). Les regles metier (borne, pas, expiration) vivent dans
`boilerack.core.validation`.
"""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass
from datetime import datetime

from boilerack.core.ack import Reason

# Champs obligatoires, exacts : aucun champ supplementaire n'est interprete, et
# tout champ inconnu fait echouer le decodage (invalid_payload).
REQUIRED_FIELDS: tuple[str, ...] = (
    "request_id",
    "ts",
    "expires_at",
    "source",
    "role",
    "value",
)


class CommandFormError(Exception):
    """Echec de decodage / validation de forme, porteur d'une raison typee.

    La `reason` est l'une des raisons permanentes de forme : `invalid_payload`
    (structure ou champ non recevable) ou `invalid_type` (valeur numerique
    inacceptable : booleen, non nombre, ou non finie).
    """

    def __init__(self, reason: Reason, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class Command:
    """Commande immuable, validee UNIQUEMENT en forme.

    - `request_id` : UUID v4 canonique, minuscule ;
    - `ts` / `expires_at` : `datetime` aware ;
    - `source` / `role` : chaines non vides ;
    - `value` : nombre fini (jamais booleen, jamais `NaN`/`Inf`). Conserve son
      type d'origine (`int` ou `float`) ; la normalisation metier (p. ex.
      `20.0` -> entier `20`) est faite plus tard, en fonction du profil.
    """

    request_id: str
    ts: datetime
    expires_at: datetime
    source: str
    role: str
    value: int | float


def is_canonical_uuid4(text: object) -> bool:
    """Vrai si `text` est un UUID v4 canonique en minuscules.

    Rejette les formes majuscules, avec accolades, ou de version differente : la
    representation doit etre exactement celle rendue par `str(uuid.UUID(...))`.
    """
    if not isinstance(text, str):
        return False
    if text != text.lower():
        return False
    try:
        parsed = uuid.UUID(text)
    except (ValueError, AttributeError, TypeError):
        return False
    return parsed.version == 4 and str(parsed) == text


def _require_aware_datetime(raw: object, field: str) -> datetime:
    if not isinstance(raw, str):
        raise CommandFormError(
            Reason.INVALID_PAYLOAD, f"{field} doit etre une chaine ISO 8601."
        )
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        raise CommandFormError(
            Reason.INVALID_PAYLOAD, f"{field} n'est pas une date ISO 8601 : {raw!r}"
        )
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CommandFormError(
            Reason.INVALID_PAYLOAD, f"{field} doit etre timezone-aware : {raw!r}"
        )
    return parsed


def _require_numeric_value(raw: object) -> int | float:
    # `bool` est une sous-classe de `int` : il faut le refuser AVANT le test
    # numerique, sinon `True`/`False` passeraient pour `1`/`0`.
    if isinstance(raw, bool):
        raise CommandFormError(
            Reason.INVALID_TYPE, "value ne peut pas etre un booleen."
        )
    if not isinstance(raw, (int, float)):
        raise CommandFormError(
            Reason.INVALID_TYPE, f"value doit etre numerique, recu {type(raw).__name__}."
        )
    # Finitude : etape distincte du type (cf. ordre de validation). `NaN`/`Inf`
    # sont des nombres mais pas des valeurs de commande exploitables.
    if not math.isfinite(raw):
        raise CommandFormError(
            Reason.INVALID_TYPE, f"value doit etre finie : {raw!r}"
        )
    return raw


def _require_non_empty_str(raw: object, field: str) -> str:
    if not isinstance(raw, str) or raw == "":
        raise CommandFormError(
            Reason.INVALID_PAYLOAD, f"{field} doit etre une chaine non vide."
        )
    return raw


def decode_payload(payload: bytes) -> dict:
    """Decode des octets bruts en objet JSON.

    N'accepte QUE des octets UTF-8 representant un objet JSON. Les constantes
    non standard (`NaN`, `Infinity`) laissees passer par la valeur seront
    rejetees a l'etape de finitude, avec une raison `invalid_type` explicite,
    plutot qu'ici : cela conserve une frontiere nette entre « payload illisible »
    et « valeur non finie ».
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise CommandFormError(
            Reason.INVALID_PAYLOAD, "payload doit etre des octets."
        )
    try:
        text = bytes(payload).decode("utf-8")
    except UnicodeDecodeError:
        raise CommandFormError(Reason.INVALID_PAYLOAD, "payload n'est pas de l'UTF-8.")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        raise CommandFormError(Reason.INVALID_PAYLOAD, "payload n'est pas du JSON valide.")
    if not isinstance(obj, dict):
        raise CommandFormError(
            Reason.INVALID_PAYLOAD, "payload doit etre un objet JSON."
        )
    return obj


def extract_request_id(payload: bytes) -> str:
    """Tente d'extraire un `request_id` a des fins de CORRELATION d'ACK.

    Renvoie la valeur brute si elle est presente et de type chaine (meme si elle
    n'est pas un UUID canonique), sinon la chaine vide. Ne valide RIEN : sert
    uniquement a etiqueter un ACK de rejet lorsque le payload est par ailleurs
    non recevable. La validite reelle du `request_id` est verifiee par
    `parse_command`.
    """
    try:
        obj = decode_payload(payload)
    except CommandFormError:
        return ""
    candidate = obj.get("request_id")
    return candidate if isinstance(candidate, str) else ""


def parse_command(payload: bytes) -> Command:
    """Decode et valide la FORME d'une commande. Leve `CommandFormError` sinon.

    Ne verifie ni borne, ni pas, ni expiration, ni existence du role dans le
    profil : uniquement la structure et les types de base.
    """
    obj = decode_payload(payload)

    keys = set(obj.keys())
    required = set(REQUIRED_FIELDS)
    missing = required - keys
    if missing:
        raise CommandFormError(
            Reason.INVALID_PAYLOAD,
            f"champ(s) obligatoire(s) manquant(s) : {sorted(missing)}",
        )
    extra = keys - required
    if extra:
        raise CommandFormError(
            Reason.INVALID_PAYLOAD, f"champ(s) non interprete(s) : {sorted(extra)}"
        )

    if not is_canonical_uuid4(obj["request_id"]):
        raise CommandFormError(
            Reason.INVALID_PAYLOAD,
            f"request_id doit etre un UUID v4 canonique minuscule : {obj['request_id']!r}",
        )

    ts = _require_aware_datetime(obj["ts"], "ts")
    expires_at = _require_aware_datetime(obj["expires_at"], "expires_at")
    source = _require_non_empty_str(obj["source"], "source")
    role = _require_non_empty_str(obj["role"], "role")
    value = _require_numeric_value(obj["value"])

    return Command(
        request_id=obj["request_id"],
        ts=ts,
        expires_at=expires_at,
        source=source,
        role=role,
        value=value,
    )
