"""Construction et serialisation de l'instantane `bridge/telemetry_status`.

Implemente la forme §6.2, le modele de mesure §6.5, la taxonomie publique §6.6
et la politique de fraicheur §7.2 du contrat `c7-mqtt-read-contract.md`.

DEUX FONCTIONS SEPAREES, comme `ack_to_dict` / `ack_to_json` en C3 : la
construction rend un dictionnaire, testable champ par champ sans analyser du
JSON ; la serialisation applique l'idiome strict du projet.

Module PUR : aucun MQTT, aucune lecture, aucune publication. L'horloge est
injectee ; aucune horloge systeme n'est lue ici.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Final, Mapping, Sequence

from boilerack.clock import Clock
from boilerack.read_surface.measurements import MeasurementSpec
from boilerack.read_surface.state import MeasurementState, ReadSurfaceState
from boilerack.transport.vclient import TransportStatus

__all__ = ["PublicResult", "build_snapshot", "snapshot_to_json"]

#: Version du schema de l'instantane (§6.3). Un ajout de champ optionnel ou
#: d'entree de mesure **MUST NOT** l'incrementer ; un retrait, un changement de
#: type ou de semantique **MUST** l'incrementer.
_SCHEMA: Final = 1

#: Forme RFC 3339 UTC avec suffixe `Z`, telle que §6.4 l'exige et telle que
#: l'exemple §6.2 la montre — precision a la seconde.
_TS_FORMAT: Final = "%Y-%m-%dT%H:%M:%SZ"


class PublicResult(str, Enum):
    """Taxonomie publique de `last_result` (§6.6). Valeurs stables et contractuelles."""

    OK = "ok"
    TIMEOUT = "timeout"
    DAEMON_UNREACHABLE = "daemon_unreachable"
    UNUSABLE_OUTPUT = "unusable_output"
    UNSUPPORTED_COMMAND = "unsupported_command"
    TRANSPORT_ERROR = "transport_error"


#: Correspondance EXPLICITE des six issues internes vers la taxonomie publique.
#:
#: `status.value` ne peut PAS servir : `TransportStatus.UNKNOWN_COMMAND.value`
#: vaut `"unknown_command"`, alors que la valeur publique est
#: `"unsupported_command"`. §6.6 precise d'ailleurs que cette correspondance
#: **MAY** evoluer, les valeurs publiques restant stables — raison de plus pour
#: qu'elle soit une table, et non une propriete de l'enumeration interne.
#:
#: Interne : aucune API externe n'en a besoin.
_PUBLIC: Final[Mapping[TransportStatus, PublicResult]] = {
    TransportStatus.OK: PublicResult.OK,
    TransportStatus.TIMEOUT: PublicResult.TIMEOUT,
    TransportStatus.DAEMON_UNREACHABLE: PublicResult.DAEMON_UNREACHABLE,
    TransportStatus.UNUSABLE_OUTPUT: PublicResult.UNUSABLE_OUTPUT,
    TransportStatus.UNKNOWN_COMMAND: PublicResult.UNSUPPORTED_COMMAND,
    TransportStatus.TRANSPORT_ERROR: PublicResult.TRANSPORT_ERROR,
}


def _public(status: TransportStatus | None) -> str | None:
    if status is None:
        return None
    try:
        return _PUBLIC[status].value
    except KeyError as exc:  # pragma: no cover - garde contre un statut ajoute
        raise ValueError(f"statut sans correspondance publique : {status!r}") from exc


def _format_ts(moment: datetime) -> str:
    """Rend un instant en RFC 3339 UTC suffixe `Z`.

    Un `datetime` naif est refuse : le suffixe `Z` serait mensonger. Un instant
    porteur d'un autre fuseau est converti, jamais reinterprete.
    """
    if not isinstance(moment, datetime):
        raise ValueError(f"instant attendu, recu {type(moment).__name__}")
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        raise ValueError("un instant sans fuseau horaire ne peut pas etre publie")
    return moment.astimezone(timezone.utc).strftime(_TS_FORMAT)


def _age_s(etat: MeasurementState, monotonic_now: float, role: str) -> int | None:
    """Anciennete du dernier succes, en secondes entieres.

    `None` avant tout succes — §6.5 : « `age_s` nul si et seulement si
    `last_success` est nul ».

    Mesuree sur l'horloge MONOTONE, jamais par difference d'horodatages muraux :
    un reglage de l'horloge systeme ne doit pas fausser une anciennete. La
    valeur monotone elle-meme n'est jamais publiee (§6.4).

    Troncature a la seconde inferieure (`floor`) : c'est le nombre de secondes
    ENTIERES ecoulees, lecture conventionnelle d'un age. §6.5 impose le type
    « entier ≥ 0 ». Consequence assumee : a la frontiere de fraicheur, l'age
    rapporte peut etre optimiste de moins d'une seconde.
    """
    if etat.last_success_monotonic is None:
        return None
    delta = monotonic_now - etat.last_success_monotonic
    if delta < 0:
        raise ValueError(
            f"[{role}] l'horloge monotone recule : {monotonic_now!r} < "
            f"{etat.last_success_monotonic!r}"
        )
    return math.floor(delta)


def _fresh(age: int | None, fresh_max_s: int) -> bool:
    """§6.5 : `age_s` inferieur ou EGAL au seuil — la borne est inclusive.

    Faux avant tout succes, ce qui satisfait « `fresh` vrai implique
    `has_value` vrai ». La comparaison porte sur `age_s`, l'entier publie, et
    non sur le delta flottant : le consommateur doit pouvoir refaire le calcul a
    partir de ce qu'il lit.
    """
    return age is not None and age <= fresh_max_s


def build_snapshot(
    state: ReadSurfaceState,
    specs: Sequence[MeasurementSpec],
    clock: Clock,
) -> dict[str, Any]:
    """Construit l'instantane §6.2 a partir de l'etat durable.

    Quatre clefs globales — `schema`, `ts`, `chain`, `measurements` — et cinq
    par mesure : `has_value`, `fresh`, `last_success`, `age_s`, `last_result`.
    **Aucune autre.** En particulier aucune valeur scalaire : celle-ci vit sur
    son propre topic, et l'instantane decrit l'ETAT DE LECTURE.

    Les mesures apparaissent dans l'ordre de `specs`. Un role inconnu de l'etat
    ou repete dans `specs` est refuse.
    """
    ts = _format_ts(clock.now())
    monotonic_now = clock.monotonic()
    if isinstance(monotonic_now, bool) or not isinstance(monotonic_now, (int, float)):
        raise ValueError(
            f"clock.monotonic() doit etre numerique, recu {type(monotonic_now).__name__}"
        )
    if not math.isfinite(monotonic_now):
        raise ValueError(f"clock.monotonic() doit etre fini : {monotonic_now!r}")

    mesures: dict[str, Any] = {}
    for spec in specs:
        if spec.role not in state.measurements:
            raise ValueError(f"role absent de l'etat : {spec.role!r}")
        if spec.role in mesures:
            raise ValueError(f"role repete dans specs : {spec.role!r}")
        etat = state.measurements[spec.role]
        age = _age_s(etat, float(monotonic_now), spec.role)
        mesures[spec.role] = {
            "has_value": etat.has_value,
            "fresh": _fresh(age, spec.fresh_max_s),
            "last_success": (
                _format_ts(etat.last_success_wall)
                if etat.last_success_wall is not None
                else None
            ),
            "age_s": age,
            "last_result": _public(etat.last_result),
        }

    return {
        "schema": _SCHEMA,
        "ts": ts,
        "chain": {
            "status": state.chain_status.value,
            "cause": _public(state.chain_cause),
        },
        "measurements": mesures,
    }


def snapshot_to_json(snapshot: Mapping[str, Any]) -> bytes:
    """Serialise l'instantane en JSON compact, UTF-8, deterministe.

    Meme idiome que `boilerack.core.ack.ack_to_json` :

    - compact : `separators=(",", ":")` ;
    - deterministe : `sort_keys=True`. L'ordre des clefs devient independant de
      l'ordre d'insertion. L'ordre montre par l'exemple §6.2 est illustratif :
      le contrat ne le declare pas normatif ;
    - strict : **`allow_nan=False`** — §6.2 : « `allow_nan` interdit » ;
    - UTF-8 : `ensure_ascii=False` puis encodage explicite.

    `boilerack._legacy.primitives.json_dumps` n'est PAS reutilise : il ne passe
    pas `allow_nan=False` et emet donc `NaN` et `Infinity`, qui ne sont pas du
    JSON valide — comportement classe accident dans `provenance.md`.
    """
    text = json.dumps(
        snapshot,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    return text.encode("utf-8")
