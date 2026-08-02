"""Horloge virtuelle deterministe pour les tests.

Implemente le protocole `boilerack.clock.Clock` sans jamais toucher a l'horloge
systeme ni attendre reellement. L'UTC mural et le compteur monotone avancent
ENSEMBLE, uniquement lorsque le test (ou un double) le decide.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


class VirtualClock:
    """Horloge entierement pilotee par le test.

    - l'instant initial est fixe a la construction ;
    - `advance()` fait progresser UTC et monotone du meme increment ;
    - `sleep()` n'attend pas : il enregistre la duree puis avance le temps ;
    - toute duree negative (avance ou sommeil) est refusee.
    """

    def __init__(self, start: datetime, *, monotonic_start: float = 0.0) -> None:
        if start.tzinfo is None:
            raise ValueError("VirtualClock exige un datetime aware (UTC).")
        self._now = start.astimezone(timezone.utc)
        self._monotonic = float(monotonic_start)
        self._sleeps: list[float] = []

    def now(self) -> datetime:
        return self._now

    def monotonic(self) -> float:
        return self._monotonic

    def advance(self, seconds: float) -> None:
        """Fait avancer UTC et monotone de `seconds`. Refuse une valeur negative."""
        if seconds < 0:
            raise ValueError(f"advance() n'accepte pas une duree negative : {seconds!r}")
        self._now = self._now + timedelta(seconds=seconds)
        self._monotonic += seconds

    def sleep(self, seconds: float) -> None:
        """Simule un sommeil : enregistre la duree et avance le temps, sans attendre."""
        if seconds < 0:
            raise ValueError(f"sleep() n'accepte pas une duree negative : {seconds!r}")
        self._sleeps.append(seconds)
        self.advance(seconds)

    @property
    def sleeps(self) -> tuple[float, ...]:
        """Historique, dans l'ordre, des durees passees a `sleep()`."""
        return tuple(self._sleeps)
