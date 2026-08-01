"""Primitives historiques du bridge de production, isolees pour caracterisation.

PROVENANCE
    Depot  : antoinevalentinHA/boiler-bridge (prive)
    Fichier: boiler_mqtt.py
    Blob   : 992f9efa5d063dee7b0ccdec17351739b7371a1b
    Commit : f14ba5c8498d3fc1706a4634ef5512a2af095bda
             "feat: enforce strict curve validation and final ACK dedup"

STATUT
    Module interne et PROVISOIRE. Ce n'est pas l'API publique de boilerack.
    Il existe pour qu'une suite de tests etablisse ce que l'implementation
    de production garantit reellement, AVANT toute factorisation.

    Le code de la premiere section est copie LITTERALEMENT, y compris ses
    defauts et ses effets de bord (appels a print). Ne rien "ameliorer" ici :
    toute correction souhaitee est une divergence a traiter en C3, pas une
    retouche silencieuse.

    La seconde section contient des EXTRACTIONS MECANIQUES : du code qui,
    dans l'original, est inline dans une fonction plus grande et ne peut donc
    pas etre copie tel quel. Le corps est reproduit a l'identique ; seule
    l'enveloppe (signature, parametres de bornes) est nouvelle.

Voir docs/design/provenance.md pour la matrice complete.
"""

from __future__ import annotations

import json
import math
import uuid
from datetime import datetime, timezone
from typing import Any

# ==========================================================
# CONSTANTES DE DOMAINE — copie litterale
# boiler_mqtt.py L63-64, L76-77, L83-89
# Destinees a migrer vers le profil declaratif en C3.
# ==========================================================

DHW_SETPOINT_MIN = 10
DHW_SETPOINT_MAX = 60

HEATING_TEMPERATURE_MIN = 5
HEATING_TEMPERATURE_MAX = 30

CURVE_SHIFT_MIN = -13
CURVE_SHIFT_MAX = 40
CURVE_SHIFT_STEP = 1  # entier strict

CURVE_SLOPE_MIN = 0.2
CURVE_SLOPE_MAX = 3.5
CURVE_SLOPE_STEP = 0.1  # flottant discret, tolérance représentation ±1e-9


# ==========================================================
# SECTION 1 — COPIE LITTERALE
# ==========================================================


def utc_now() -> datetime:
    """boiler_mqtt.py L111-112 — copie litterale."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """boiler_mqtt.py L115-117 — copie litterale."""
    now = utc_now()
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso8601(value: str) -> datetime:
    """boiler_mqtt.py L120-131 — copie litterale."""
    normalized = value.strip()

    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    parsed = datetime.fromisoformat(normalized)

    if parsed.tzinfo is None:
        raise ValueError("timezone missing")

    return parsed.astimezone(timezone.utc)


def json_dumps(payload: dict[str, Any]) -> str:
    """boiler_mqtt.py L134-135 — copie litterale."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def validate_uuid4_string(value: Any) -> bool:
    """boiler_mqtt.py L526-535 — copie litterale."""
    if not isinstance(value, str):
        return False

    try:
        parsed = uuid.UUID(value, version=4)
    except Exception:
        return False

    return str(parsed) == value.lower()


def sanitize_curve_slope(value: Any) -> tuple[bool, str | None, float | None]:
    """boiler_mqtt.py L386-426 — copie litterale, appels print inclus.

    Valide et normalise une valeur de pente de courbe.

    Bornes physiques : [0.2 ; 3.5], pas 0.1
    Normalisation de représentation : round(value, 1) pour absorber
    les imprécisions flottantes (ex. 2.4000000000000004 → 2.4).
    Aucune correction de valeur : 2.37 est rejeté, pas arrondi à 2.4.
    """
    if isinstance(value, bool):
        print(f"[ERROR] curve_slope invalid_type: bool is not accepted")
        return False, "invalid_type", None

    if not isinstance(value, (int, float)):
        print(f"[ERROR] curve_slope invalid_type: {type(value).__name__}")
        return False, "invalid_type", None

    if math.isnan(value) or math.isinf(value):
        print(f"[ERROR] curve_slope invalid_type: NaN or Inf")
        return False, "invalid_type", None

    # Normalisation de représentation uniquement (pas de correction de valeur)
    normalized = round(float(value), 1)

    if normalized < CURVE_SLOPE_MIN or normalized > CURVE_SLOPE_MAX:
        print(f"[WARN] curve_slope out of range: input={value} normalized={normalized} "
              f"bounds=[{CURVE_SLOPE_MIN};{CURVE_SLOPE_MAX}]")
        return False, "invalid_value_out_of_range", None

    # Validation du pas : la valeur normalisée doit être multiple de 0.1
    # On vérifie que round(v, 1) == v à la précision de représentation
    if abs(normalized - float(value)) > 1e-9:
        print(f"[WARN] curve_slope invalid_step: input={value} → would normalize to {normalized}, rejected")
        return False, "invalid_step", None

    print(f"[INFO] curve_slope: input={value} → normalized={normalized}")
    return True, None, normalized


def sanitize_curve_shift(value: Any) -> tuple[bool, str | None, int | None]:
    """boiler_mqtt.py L429-469 — copie litterale, appels print inclus.

    Valide et normalise une valeur de parallèle de courbe.

    Bornes physiques : [-13 ; 40], pas 1 (entier strict)
    Aucune correction de valeur : 7.2 est rejeté, pas arrondi à 7.
    """
    if isinstance(value, bool):
        print(f"[ERROR] curve_shift invalid_type: bool is not accepted")
        return False, "invalid_type", None

    if not isinstance(value, (int, float)):
        print(f"[ERROR] curve_shift invalid_type: {type(value).__name__}")
        return False, "invalid_type", None

    if math.isnan(value) or math.isinf(value):
        print(f"[ERROR] curve_shift invalid_type: NaN or Inf")
        return False, "invalid_type", None

    # Validation du pas : doit être un entier strict.
    # Tolérance 1e-9 pour les artefacts de représentation flottante
    # (cohérence avec sanitize_curve_slope).
    # 7.0 → accepté, 7.0000000001 → accepté, 7.2 → rejeté
    rounded = round(float(value))
    if abs(float(value) - rounded) > 1e-9:
        print(f"[WARN] curve_shift invalid_step: input={value} is not an integer")
        return False, "invalid_step", None

    normalized = int(rounded)

    if normalized < CURVE_SHIFT_MIN or normalized > CURVE_SHIFT_MAX:
        print(f"[WARN] curve_shift out of range: input={value} normalized={normalized} "
              f"bounds=[{CURVE_SHIFT_MIN};{CURVE_SHIFT_MAX}]")
        return False, "invalid_value_out_of_range", None

    print(f"[INFO] curve_shift: input={value} → normalized={normalized}")
    return True, None, normalized


# ==========================================================
# SECTION 2 — EXTRACTIONS MECANIQUES
# ----------------------------------------------------------
# Code inline dans l'original, non copiable tel quel. Le CORPS est
# reproduit a l'identique ; seule l'enveloppe est nouvelle.
# ==========================================================


def legacy_is_expired(now: datetime, expires_at: datetime) -> bool:
    """Extraction de la condition d'expiration.

    Source : boiler_mqtt.py L569, L625, L681, L730 — quatre occurrences
    identiques de `if utc_now() > expires_at_dt:`.

    Comparateur STRICT reproduit tel quel : a l'instant exact d'expiration,
    la commande n'est PAS consideree expiree. La divergence D-8 alignera ce
    comportement sur `now >= expires_at` en C3.
    """
    return now > expires_at


def legacy_setpoint_value(
    value: Any, minimum: int, maximum: int
) -> tuple[bool, str | None, int | None]:
    """Extraction de la validation de valeur des commandes de consigne.

    Source : boiler_mqtt.py L572-581 (dhw/set_setpoint) et L628-637
    (heating/set_temperature) — deux blocs identiques.

    Reproduit le comportement d'ARRONDI de l'original : contrairement aux
    fonctions de courbe, une valeur non entiere est arrondie et acceptee.
    La divergence D-1 (P-02) supprimera cet arrondi en C3.

    Aucune protection contre NaN ni Inf dans l'original : ces valeurs
    remontent donc une exception. Comportement reproduit tel quel.
    """
    if isinstance(value, bool):
        return False, "invalid_value", None

    if not isinstance(value, (int, float)):
        return False, "invalid_value", None

    normalized_value = int(round(float(value)))

    if normalized_value < minimum or normalized_value > maximum:
        return False, "invalid_value", None

    return True, None, normalized_value


def legacy_build_ack_payload(
    request_id: str, status: str, ts: str, reason: str | None = None
) -> dict[str, Any]:
    """Extraction de la construction du payload d'ACK.

    Source : boiler_mqtt.py L335-343, corps de `publish_ack`, dont la
    publication MQTT est retiree. L'ordre d'insertion des cles est conserve.
    """
    payload: dict[str, Any] = {
        "request_id": request_id,
        "status": status,
        "ts": ts,
    }

    if reason is not None:
        payload["reason"] = reason

    return payload


def legacy_build_error_payload(
    request_id: str | None,
    domain: str,
    action: str,
    reason: str,
    details: str,
    ts: str,
) -> dict[str, Any]:
    """Extraction de la construction du payload d'erreur.

    Source : boiler_mqtt.py L356-363, corps de `publish_error`, dont la
    publication MQTT est retiree.
    """
    return {
        "request_id": request_id,
        "domain": domain,
        "action": action,
        "reason": reason,
        "details": details,
        "ts": ts,
    }
