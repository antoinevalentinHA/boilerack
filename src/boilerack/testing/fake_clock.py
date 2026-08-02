"""Horloge virtuelle deterministe pour les tests.

Implemente le protocole `boilerack.clock.Clock` sans jamais toucher a l'horloge
systeme ni attendre reellement. L'UTC mural et le compteur monotone avancent
ENSEMBLE, uniquement lorsque le test (ou un double) le decide.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from boilerack.clock import check_duration


class VirtualClock:
    """Horloge entierement pilotee par le test.

    - l'instant initial est fixe a la construction ;
    - `advance()` fait progresser UTC et monotone du meme increment ;
    - `sleep()` n'attend pas : il enregistre la duree puis avance le temps ;
    - toute duree negative, `NaN` ou infinie (avance ou sommeil) est refusee.
    """

    def __init__(self, start: datetime, *, monotonic_start: float = 0.0) -> None:
        if start.tzinfo is None:
            raise ValueError("VirtualClock exige un datetime aware (UTC).")
        origin = float(monotonic_start)
        if not math.isfinite(origin):
            raise ValueError(
                f"monotonic_start doit etre fini : {monotonic_start!r}"
            )
        self._now = start.astimezone(timezone.utc)
        self._monotonic = origin
        self._sleeps: list[float] = []

    def now(self) -> datetime:
        return self._now

    def monotonic(self) -> float:
        return self._monotonic

    def advance(self, seconds: float) -> None:
        """Fait avancer UTC et monotone de `seconds`.

        Refuse une valeur negative, `NaN` ou infinie : le temps virtuel ne peut
        ni reculer, ni sauter vers un etat indefini.
        """
        delta = check_duration(seconds, op="advance()")
        self._now = self._now + timedelta(seconds=delta)
        self._monotonic += delta

    def sleep(self, seconds: float) -> None:
        """Simule un sommeil : enregistre la duree et avance le temps, sans attendre."""
        delta = check_duration(seconds, op="sleep()")
        self._sleeps.append(delta)
        self.advance(delta)

    @property
    def sleeps(self) -> tuple[float, ...]:
        """Historique, dans l'ordre, des durees passees a `sleep()`."""
        return tuple(self._sleeps)
