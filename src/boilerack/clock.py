"""Abstraction d'horloge.

Le futur coeur transactionnel ne doit jamais appeler directement l'horloge
systeme : il recoit une `Clock`. Cela rend les TTL, budgets et temporisations
testables de facon totalement deterministe.

Ce module ne contient que l'interface `Clock` et son implementation reelle
`SystemClock`. L'horloge virtuelle utilisee dans les tests vit dans
`boilerack.testing.fake_clock`, pour qu'aucun code de production ne depende du
code de test.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Frontiere temporelle minimale.

    Trois responsabilites, volontairement separees :

    - `now()` : instant mural, en UTC explicite, pour horodater et comparer des
      echeances absolues (`expires_at`) ;
    - `monotonic()` : compteur monotone, jamais affecte par un reglage d'horloge,
      pour mesurer des durees et tenir des budgets ;
    - `sleep()` : ceder la main pour une duree donnee.
    """

    def now(self) -> datetime:
        """Instant courant, `datetime` aware en UTC."""
        ...

    def monotonic(self) -> float:
        """Valeur d'un compteur monotone en secondes. Seuls les ecarts ont un sens."""
        ...

    def sleep(self, seconds: float) -> None:
        """Attendre `seconds` secondes. Une duree negative est refusee."""
        ...


class SystemClock:
    """Horloge reelle. Aucune logique metier : trois delegations a la stdlib.

    C'est l'implementation de production. Elle n'est jamais utilisee dans les
    tests d'infrastructure, qui exigent le determinisme de l'horloge virtuelle.
    """

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError(f"sleep() n'accepte pas une duree negative : {seconds!r}")
        time.sleep(seconds)
