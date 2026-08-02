"""File FIFO bornee et deterministe.

Primitive minimale dont le futur coeur aura besoin pour borner le travail en
attente. Elle ne connait NI `request_id`, NI deduplication, NI priorite metier,
NI worker : c'est une structure de donnees, pas un ordonnanceur.

Le rejet a la saturation est explicite (`QueueFull`) et l'extraction a vide l'est
aussi (`QueueEmpty`) : aucune valeur sentinelle ambigue n'est renvoyee.
"""

from __future__ import annotations

from collections import deque
from typing import Generic, TypeVar

T = TypeVar("T")


class QueueFull(Exception):
    """Levee quand `put` est appele sur une file pleine."""


class QueueEmpty(Exception):
    """Levee quand `get` est appele sur une file vide."""


class BoundedQueue(Generic[T]):
    """File FIFO a capacite fixe.

    Suit la profondeur courante et le maximum atteint depuis la creation, ce qui
    permettra plus tard d'observer la pression sans instrumenter le coeur.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError(f"la capacite doit etre strictement positive : {capacity!r}")
        self._capacity = capacity
        self._items: deque[T] = deque()
        self._max_depth_observed = 0

    def put(self, item: T) -> None:
        """Admet un element, ou leve `QueueFull` si la file est pleine."""
        if len(self._items) >= self._capacity:
            raise QueueFull(f"file pleine (capacite={self._capacity})")
        self._items.append(item)
        if len(self._items) > self._max_depth_observed:
            self._max_depth_observed = len(self._items)

    def get(self) -> T:
        """Retire et renvoie l'element le plus ancien, ou leve `QueueEmpty`."""
        if not self._items:
            raise QueueEmpty("file vide")
        return self._items.popleft()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def depth(self) -> int:
        """Nombre d'elements actuellement en file."""
        return len(self._items)

    @property
    def max_depth_observed(self) -> int:
        """Profondeur maximale atteinte depuis la creation."""
        return self._max_depth_observed

    def __len__(self) -> int:
        return len(self._items)
