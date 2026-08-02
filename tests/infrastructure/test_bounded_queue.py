"""Tests de la file bornee deterministe."""

import pytest

from boilerack.bounded_queue import BoundedQueue, QueueEmpty, QueueFull


def test_capacite_doit_etre_positive() -> None:
    with pytest.raises(ValueError):
        BoundedQueue(0)
    with pytest.raises(ValueError):
        BoundedQueue(-1)


def test_fifo() -> None:
    q: BoundedQueue[int] = BoundedQueue(3)
    q.put(1)
    q.put(2)
    q.put(3)
    assert q.get() == 1
    assert q.get() == 2
    assert q.get() == 3


def test_rejet_si_pleine() -> None:
    q: BoundedQueue[str] = BoundedQueue(2)
    q.put("a")
    q.put("b")
    with pytest.raises(QueueFull, match="capacite=2"):
        q.put("c")


def test_extraction_a_vide_leve() -> None:
    q: BoundedQueue[int] = BoundedQueue(1)
    with pytest.raises(QueueEmpty):
        q.get()


def test_profondeur_courante() -> None:
    q: BoundedQueue[int] = BoundedQueue(5)
    assert q.depth == 0
    q.put(1)
    q.put(2)
    assert q.depth == 2
    q.get()
    assert q.depth == 1


def test_profondeur_maximale_observee() -> None:
    q: BoundedQueue[int] = BoundedQueue(5)
    q.put(1)
    q.put(2)
    q.put(3)  # pic a 3
    q.get()
    q.get()
    assert q.depth == 1
    assert q.max_depth_observed == 3  # le maximum reste memorise


def test_retour_a_zero_apres_extraction() -> None:
    q: BoundedQueue[int] = BoundedQueue(2)
    q.put(1)
    q.put(2)
    q.get()
    q.get()
    assert q.depth == 0
    assert len(q) == 0
    # la file redevient utilisable apres avoir ete videe
    q.put(9)
    assert q.get() == 9


def test_place_liberee_apres_extraction() -> None:
    q: BoundedQueue[int] = BoundedQueue(1)
    q.put(1)
    with pytest.raises(QueueFull):
        q.put(2)
    assert q.get() == 1
    q.put(2)  # la place s'est liberee
    assert q.get() == 2


def test_capacite_exposee() -> None:
    assert BoundedQueue(7).capacity == 7
