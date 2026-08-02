"""Caracterisation du temps et de l'expiration.

Sources : `parse_iso8601` (L120-131), `utc_now` / `utc_now_iso` (L111-117),
condition d'expiration inline (L569, L625, L681, L730).
"""

from datetime import datetime, timedelta, timezone

import pytest

from boilerack._legacy.primitives import (
    legacy_is_expired,
    parse_iso8601,
    utc_now,
    utc_now_iso,
)

INSTANT = datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)


@pytest.mark.reference
@pytest.mark.parametrize(
    ("valeur", "attendu", "commentaire"),
    [
        ("2026-08-01T10:00:00Z", INSTANT, "UTC en Z"),
        ("2026-08-01T10:00:00+00:00", INSTANT, "decalage explicite nul"),
        ("2026-08-01T12:00:00+02:00", INSTANT, "fuseau explicite, converti en UTC"),
        ("2026-08-01T05:00:00-05:00", INSTANT, "fuseau negatif"),
        ("  2026-08-01T10:00:00Z  ", INSTANT, "espaces : strip applique"),
        ("2026-08-01T10:00:00.500Z", INSTANT + timedelta(milliseconds=500), "fraction de seconde acceptee"),
    ],
)
def test_formes_acceptees(valeur: str, attendu: datetime, commentaire: str) -> None:
    assert parse_iso8601(valeur) == attendu, commentaire


@pytest.mark.reference
def test_absence_de_fuseau_refusee() -> None:
    """Le fuseau est obligatoire : c'est une garantie forte de l'implementation."""
    with pytest.raises(ValueError, match="timezone missing"):
        parse_iso8601("2026-08-01T10:00:00")


@pytest.mark.reference
@pytest.mark.parametrize("valeur", ["", "pas une date", "2026-13-01T10:00:00Z", "2026-08-01"])
def test_valeurs_invalides(valeur: str) -> None:
    """Une date invalide leve ValueError.

    Note : "2026-08-01" est une date valide au sens ISO mais sans fuseau,
    elle echoue donc aussi, sur la seconde garde.
    """
    with pytest.raises(ValueError):
        parse_iso8601(valeur)


@pytest.mark.reference
def test_utc_now_est_bien_offset_aware() -> None:
    maintenant = utc_now()
    assert maintenant.tzinfo is not None
    assert maintenant.utcoffset() == timedelta(0)


@pytest.mark.reference
def test_utc_now_iso_tronque_a_la_seconde() -> None:
    """Le format ne porte ni fraction de seconde ni decalage numerique."""
    rendu = utc_now_iso()
    assert rendu.endswith("Z")
    assert len(rendu) == 20
    assert parse_iso8601(rendu).microsecond == 0


# ----------------------------------------------------------
# Expiration
# ----------------------------------------------------------


@pytest.mark.reference
def test_avant_expiration_non_expire() -> None:
    assert legacy_is_expired(INSTANT - timedelta(seconds=1), INSTANT) is False


@pytest.mark.reference
def test_apres_expiration_expire() -> None:
    assert legacy_is_expired(INSTANT + timedelta(seconds=1), INSTANT) is True


@pytest.mark.divergence_ratified
def test_instant_exact_non_expire_dans_l_implementation_actuelle() -> None:
    """A l'instant exact d'expiration, la commande n'est PAS expiree.

    L'implementation utilise un comparateur strict `now > expires_at`, alors
    que le contrat du consommateur d'origine ecrit `now >= expires_at`. Le texte et le code
    divergent depuis l'origine.

    Ce test fige le comportement REEL. La divergence D-8 alignera le produit
    public sur `now >= expires_at` en C3 : ce test devra alors etre inverse,
    de facon visible et tracee, jamais par une correction silencieuse.
    """
    assert legacy_is_expired(INSTANT, INSTANT) is False
