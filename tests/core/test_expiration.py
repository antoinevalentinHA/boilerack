"""Tests de la semantique d'expiration.

Une commande est expiree lorsque `now >= expires_at`. L'expiration est verifiee
a l'admission ET de nouveau immediatement avant l'ecriture, via `Clock`, jamais
via l'horloge systeme.
"""

from __future__ import annotations

from boilerack.core import Reason
from boilerack.core.ack import AckStatus
from support import Harness, message, payload, rid


def test_avant_echeance_admise() -> None:
    h = Harness()
    ack = h.core.submit(message(payload(rid(1), "mode", 1, ttl_seconds=60)))
    assert ack.status is AckStatus.ACCEPTED


def test_egalite_est_expiree() -> None:
    h = Harness()
    ack = h.core.submit(message(payload(rid(1), "mode", 1, ttl_seconds=0)))
    assert ack.status is AckStatus.REJECTED
    assert ack.reason is Reason.EXPIRED


def test_apres_echeance_expiree() -> None:
    h = Harness()
    ack = h.core.submit(message(payload(rid(1), "mode", 1, ttl_seconds=-1)))
    assert ack.status is AckStatus.REJECTED
    assert ack.reason is Reason.EXPIRED


def test_expiration_pendant_l_attente_en_file() -> None:
    # Admise valide, puis le temps avance au-dela de l'echeance PENDANT l'attente.
    h = Harness()
    accepted = h.core.submit(message(payload(rid(1), "mode", 1, ttl_seconds=10)))
    assert accepted.status is AckStatus.ACCEPTED
    assert h.core.queue_depth == 1

    h.clock.advance(20)  # depasse expires_at
    verdict = h.core.process_next()

    assert verdict.status is AckStatus.REJECTED
    assert verdict.reason is Reason.EXPIRED
    # Aucune ecriture ne doit avoir eu lieu.
    assert h.write_calls() == []
    h.vclient.assert_all_consumed()


def test_expiration_juste_avant_l_ecriture() -> None:
    # Valide a l'admission ; expire exactement a l'instant du traitement.
    h = Harness()
    h.core.submit(message(payload(rid(1), "mode", 1, ttl_seconds=5)))
    h.clock.advance(5)  # now == expires_at -> expiree
    verdict = h.core.process_next()
    assert verdict.reason is Reason.EXPIRED
    assert h.write_calls() == []
