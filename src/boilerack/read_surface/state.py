"""Etat durable de la surface de lecture et cloture de cycle.

Implemente le modele de mesure §6.5, la politique de fraicheur §7.3 et l'etat
synthetique de chaine §8.2 du contrat `c7-mqtt-read-contract.md`.

AUCUNE VALEUR SCALAIRE N'EST CONSERVEE
    Ce n'est pas un oubli. L'instantane §6.2 ne porte aucune valeur ; aucune
    clause n'exige de rediffuser un scalaire sans nouvelle lecture ; §7.4 ne
    prescrit la republication que de l'instantane ; le contrat ne traite pas la
    reconnexion et range la politique de retention du broker parmi les
    inconnues (§15.5). Un champ de valeur n'aurait donc aucun consommateur, et
    inviterait la republication silencieuse d'une valeur perimee que §12
    interdit de presenter comme fraiche.

    La valeur d'une lecture reussie appartient a la PORTEE DU CYCLE de son
    producteur : elle va du `ReadResult` au payload scalaire sans transiter par
    l'etat. L'etat est une PROJECTION DES ISSUES, pas un conduit de valeurs.

DEUX FONCTIONS, PAS UNE
    §4.6 impose, apres une lecture reussie, l'ordre : publier le scalaire, puis
    mettre a jour l'etat DE LA MESURE, puis publier l'instantane. Un unique
    appel en fin de cycle rendrait cette sequence par mesure impossible.
    `record_result` applique donc la transition d'une mesure — succes comme
    echec, §7.3 exigeant la mise a jour de `last_result` sur echec — et
    `complete_cycle` ne derive que `chain`, §8.2 la definissant sur le dernier
    cycle TERMINE.

Module PUR : aucune lecture, aucun MQTT, aucune publication. L'horloge est
injectee ; aucune horloge systeme n'est lue ici.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Final, Mapping, Sequence

from boilerack.clock import Clock
from boilerack.read_surface.measurements import MeasurementSpec
from boilerack.transport.vclient import TransportStatus

__all__ = [
    "ChainStatus",
    "MeasurementState",
    "ReadSurfaceState",
    "record_result",
    "complete_cycle",
]


class ChainStatus(str, Enum):
    """Etat synthetique de la chaine de lecture (§8.2). Trois etats, pas davantage."""

    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


#: Ordre de severite contractuel de `chain.cause` (§8.2), du plus grave au moins
#: grave. Place en tete ce qui affecte toute la chaine, en queue ce qui n'affecte
#: qu'une commande. Interne : aucune API externe n'en a besoin.
_SEVERITY: Final[tuple[TransportStatus, ...]] = (
    TransportStatus.DAEMON_UNREACHABLE,
    TransportStatus.TRANSPORT_ERROR,
    TransportStatus.TIMEOUT,
    TransportStatus.UNUSABLE_OUTPUT,
    TransportStatus.UNKNOWN_COMMAND,
)


def _check_status(status: object, field_name: str) -> TransportStatus:
    if not isinstance(status, TransportStatus):
        raise ValueError(
            f"{field_name} doit etre un TransportStatus, recu {type(status).__name__}"
        )
    return status


def _check_aware_utc(moment: datetime, field_name: str) -> datetime:
    """Refuse un `datetime` naif et normalise vers UTC.

    §6.4 exige un instant UTC. Un `datetime` naif serait publie avec un suffixe
    `Z` mensonger : il est refuse, jamais devine.
    """
    if not isinstance(moment, datetime):
        raise ValueError(
            f"{field_name} doit etre un datetime, recu {type(moment).__name__}"
        )
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        raise ValueError(f"{field_name} doit porter un fuseau horaire explicite")
    return moment.astimezone(timezone.utc)


def _check_finite(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"{field_name} doit etre numerique, recu {type(value).__name__}"
        )
    if not math.isfinite(value):
        raise ValueError(f"{field_name} doit etre fini : {value!r}")
    return float(value)


@dataclass(frozen=True)
class MeasurementState:
    """Etat durable d'une mesure. Trois champs, et rien d'autre.

    - `last_success_wall` : instant mural du dernier succes, UTC, publie tel
      quel dans `last_success` (§6.5) ;
    - `last_success_monotonic` : instant monotone du MEME succes. **Jamais
      publie** — §6.4 : « Une horloge monotone **MUST NOT** etre exposee ». Il
      ne sert qu'a calculer `age_s`, qui devient ainsi insensible a un reglage
      de l'horloge systeme ;
    - `last_result` : issue de la DERNIERE TENTATIVE (§6.5), succes ou echec.

    `has_value` est DERIVE, jamais stocke : l'etat incoherent
    `has_value=True / last_success=None` est ainsi structurellement impossible,
    ce qu'exige l'equivalence posee en §6.5.
    """

    last_success_wall: datetime | None = None
    last_success_monotonic: float | None = None
    last_result: TransportStatus | None = None

    def __post_init__(self) -> None:
        wall, mono = self.last_success_wall, self.last_success_monotonic
        if (wall is None) != (mono is None):
            raise ValueError(
                "les deux estampilles de succes doivent etre posees ensemble "
                "ou nulles ensemble"
            )
        if wall is not None:
            object.__setattr__(
                self, "last_success_wall", _check_aware_utc(wall, "last_success_wall")
            )
        if mono is not None:
            object.__setattr__(
                self,
                "last_success_monotonic",
                _check_finite(mono, "last_success_monotonic"),
            )
        if self.last_result is not None:
            _check_status(self.last_result, "last_result")

    @property
    def has_value(self) -> bool:
        """§6.5 : `has_value` vrai equivaut a `last_success` non nul."""
        return self.last_success_wall is not None


@dataclass(frozen=True)
class ReadSurfaceState:
    """Etat durable de l'ensemble de la surface de lecture.

    `measurements` est remplace a la construction par une vue en lecture seule
    sur une COPIE privee : un `dict` place dans une dataclass gelee resterait
    mutable de l'exterieur, ce qui viderait `frozen=True` de son sens.
    """

    measurements: Mapping[str, MeasurementState]
    chain_status: ChainStatus = ChainStatus.UNAVAILABLE
    chain_cause: TransportStatus | None = None
    cycle_completed: bool = False

    def __post_init__(self) -> None:
        prive = dict(self.measurements)
        for role, etat in prive.items():
            if not isinstance(role, str) or role == "":
                raise ValueError(f"role invalide dans l'etat : {role!r}")
            if not isinstance(etat, MeasurementState):
                raise ValueError(f"[{role}] etat attendu de type MeasurementState")
        object.__setattr__(self, "measurements", MappingProxyType(prive))

        if not isinstance(self.chain_status, ChainStatus):
            raise ValueError(f"chain_status invalide : {self.chain_status!r}")
        if self.chain_cause is not None:
            _check_status(self.chain_cause, "chain_cause")
        if self.chain_status is ChainStatus.OK and self.chain_cause is not None:
            # §8.2 : « `chain.cause` : `null` si `status` vaut `ok` ».
            raise ValueError("chain_cause doit etre nulle quand chain_status vaut ok")

    @classmethod
    def initial(cls, specs: Sequence[MeasurementSpec]) -> "ReadSurfaceState":
        """Etat de demarrage : aucune tentative, aucun cycle termine.

        §7.3 : avant la premiere lecture, chaque mesure porte `has_value: false`,
        `fresh: false`, `last_result: null`. §8.2 : avant le premier cycle
        termine, la chaine porte `unavailable` et une cause nulle — « l'absence
        de resultat n'est pas un echec ».
        """
        return cls(measurements={spec.role: MeasurementState() for spec in specs})

    def _replace_measurement(
        self, role: str, etat: MeasurementState
    ) -> "ReadSurfaceState":
        remplace = dict(self.measurements)
        remplace[role] = etat
        return ReadSurfaceState(
            measurements=remplace,
            chain_status=self.chain_status,
            chain_cause=self.chain_cause,
            cycle_completed=self.cycle_completed,
        )


def record_result(
    state: ReadSurfaceState,
    role: str,
    status: TransportStatus,
    clock: Clock,
) -> ReadSurfaceState:
    """Applique la transition d'UNE mesure et rend un nouvel etat.

    Ne recoit aucune valeur scalaire : la transition ne depend que de l'issue.

    - `OK` : les deux estampilles sont posees sur le MEME evenement logique —
      un seul appel a `now()` et un seul a `monotonic()` — et `last_result`
      devient `OK` ;
    - tout statut non-`OK` : les estampilles de succes restent INCHANGEES et
      seul `last_result` est mis a jour. §7.3 : « Echec isole → aucune
      publication scalaire ; `last_result` mis a jour ; `fresh` reste vrai tant
      que `age_s ≤ fresh_max` ». Un echec ne perime pas une valeur.

    Toute autre mesure reste inchangee. `chain` n'est pas touche : il se derive
    a la cloture du cycle (§8.2).
    """
    if role not in state.measurements:
        raise ValueError(f"role inconnu de l'etat : {role!r}")
    _check_status(status, "status")

    courant = state.measurements[role]
    if status is not TransportStatus.OK:
        return state._replace_measurement(
            role,
            MeasurementState(
                last_success_wall=courant.last_success_wall,
                last_success_monotonic=courant.last_success_monotonic,
                last_result=status,
            ),
        )

    wall = _check_aware_utc(clock.now(), "clock.now()")
    mono = _check_finite(clock.monotonic(), "clock.monotonic()")
    if (
        courant.last_success_monotonic is not None
        and mono < courant.last_success_monotonic
    ):
        # Borner a zero publierait la fraicheur MAXIMALE pour une horloge
        # cassee : le pire mensonge possible. On refuse plutot que de corriger.
        # Le controle est LOCAL a la mesure : aucune coherence globale d'horloge
        # entre mesures differentes n'est supposee.
        raise ValueError(
            f"[{role}] l'horloge monotone recule : {mono!r} < "
            f"{courant.last_success_monotonic!r}"
        )

    return state._replace_measurement(
        role,
        MeasurementState(
            last_success_wall=wall,
            last_success_monotonic=mono,
            last_result=TransportStatus.OK,
        ),
    )


def complete_cycle(
    state: ReadSurfaceState,
    results: Mapping[str, TransportStatus],
) -> ReadSurfaceState:
    """Clot un cycle et derive `chain` (§8.2). Ne touche a aucune mesure.

    Ne lit aucune horloge : la cloture est une pure derivation.

    `results` decrit les tentatives DU CYCLE. Chaque statut doit correspondre au
    `last_result` courant de sa mesure — ce controle transforme la redondance
    apparente avec `record_result` en verification de coherence.

    LIMITE ASSUMEE — les doublons ne sont PAS detectables ici. Un `Mapping`
    litteral a deja ecrase toute clef repetee avant l'appel : `complete_cycle`
    ne peut pas savoir qu'un role a ete tente deux fois. La garantie « un role
    au plus une fois par cycle » appartient au futur collecteur C7-C3, ou
    exigerait une API sequentielle distincte. Elle n'est pas revendiquee ici.

    Un ensemble VIDE est refuse. §8.2 definit un cycle comme la tentative de
    lecture « des mesures dues a cet instant » ; un ensemble vide satisferait
    vacuement « termine » et basculerait `chain` en `unavailable` — regression
    manifeste. Le refus oblige l'appelant a ne pas cloturer quand rien n'est du.
    """
    if not isinstance(results, Mapping):
        raise ValueError(
            f"results doit etre un Mapping, recu {type(results).__name__}"
        )
    if len(results) == 0:
        raise ValueError(
            "un cycle vide n'est pas un cycle : aucune mesure n'a ete tentee"
        )

    for role, status in results.items():
        if role not in state.measurements:
            raise ValueError(f"role inconnu de l'etat : {role!r}")
        _check_status(status, f"results[{role!r}]")
        courant = state.measurements[role].last_result
        if courant is not status:
            raise ValueError(
                f"[{role}] incoherence : le cycle annonce {status.value!r} "
                f"alors que last_result vaut {courant.value if courant else None!r} "
                "— record_result n'a pas ete appele pour cette tentative"
            )

    echecs = [s for s in results.values() if s is not TransportStatus.OK]
    succes = len(results) - len(echecs)

    if succes == 0:
        statut = ChainStatus.UNAVAILABLE
    elif echecs:
        statut = ChainStatus.DEGRADED
    else:
        statut = ChainStatus.OK

    cause = None if statut is ChainStatus.OK else _plus_severe(echecs)

    return ReadSurfaceState(
        measurements=dict(state.measurements),
        chain_status=statut,
        chain_cause=cause,
        cycle_completed=True,
    )


def _plus_severe(echecs: Sequence[TransportStatus]) -> TransportStatus:
    """Statut non-`OK` le plus severe du cycle, selon l'ordre §8.2."""
    for candidat in _SEVERITY:
        if candidat in echecs:
            return candidat
    # Inatteignable : `_SEVERITY` couvre les cinq valeurs non-`OK` de
    # `TransportStatus`. Un test le verifie sur l'enumeration reelle.
    raise ValueError(f"statut d'echec hors de l'ordre de severite : {echecs!r}")
