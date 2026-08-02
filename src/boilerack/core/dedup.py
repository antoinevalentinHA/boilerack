"""Deduplication VOLATILE : registre `in_flight` et cache terminal.

Deux structures DISTINCTES, aux roles opposes :

- `InFlightRegistry` reserve les `request_id` en cours de traitement, pour
  empecher un second travail dans la meme vie du processus. Un identifiant y
  reste jusqu'a la PRODUCTION de son verdict terminal, puis en est retire.
- `TerminalCache` associe un `request_id` a son verdict terminal, avec un TTL
  MONOTONE, pour rejouer ce verdict sans reexecution.

Doctrine (v1) : cette memoire est VOLATILE. Elle empeche les doubles travaux
pendant la vie du processus mais ne pretend AUCUNE persistance apres redemarrage
ni apres expiration du TTL. Le cache ne contient JAMAIS `accepted` (non
terminal).
"""

from __future__ import annotations

from boilerack.clock import Clock
from boilerack.core.ack import Ack

DEFAULT_TERMINAL_TTL_SECONDS = 60.0


class InFlightRegistry:
    """Ensemble des `request_id` admis et non encore conclus."""

    def __init__(self) -> None:
        self._ids: set[str] = set()

    def reserve(self, request_id: str) -> bool:
        """Reserve un identifiant. Renvoie `False` s'il etait deja present."""
        if request_id in self._ids:
            return False
        self._ids.add(request_id)
        return True

    def contains(self, request_id: str) -> bool:
        return request_id in self._ids

    def release(self, request_id: str) -> None:
        """Retire un identifiant (a la production du verdict terminal)."""
        self._ids.discard(request_id)

    def __len__(self) -> int:
        return len(self._ids)


class TerminalCache:
    """Cache `request_id -> verdict terminal`, borne par un TTL monotone."""

    def __init__(
        self, clock: Clock, ttl_seconds: float = DEFAULT_TERMINAL_TTL_SECONDS
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError(f"le TTL doit etre strictement positif : {ttl_seconds!r}")
        self._clock = clock
        self._ttl = float(ttl_seconds)
        self._entries: dict[str, tuple[Ack, float]] = {}

    def put(self, request_id: str, ack: Ack) -> None:
        """Enregistre un verdict TERMINAL. Refuse tout ACK non terminal."""
        if not ack.is_terminal:
            raise ValueError(
                f"le cache terminal refuse un ACK non terminal : {ack.status.value}"
            )
        deadline = self._clock.monotonic() + self._ttl
        self._entries[request_id] = (ack, deadline)

    def get(self, request_id: str) -> Ack | None:
        """Renvoie le verdict si present ET non expire, sinon `None`.

        Une entree expiree est purgee a l'acces (purge paresseuse deterministe).
        """
        entry = self._entries.get(request_id)
        if entry is None:
            return None
        ack, deadline = entry
        if self._clock.monotonic() >= deadline:
            del self._entries[request_id]
            return None
        return ack

    def purge(self) -> int:
        """Purge toutes les entrees expirees. Renvoie le nombre purge."""
        now = self._clock.monotonic()
        expired = [rid for rid, (_, deadline) in self._entries.items() if now >= deadline]
        for rid in expired:
            del self._entries[rid]
        return len(expired)

    def __len__(self) -> int:
        return len(self._entries)
