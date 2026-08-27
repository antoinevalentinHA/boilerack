"""`FileEvidenceSink` — le puits de preuve de `g2-sortie-preuve-transport.md`.

Ce fichier eprouve le puits SEUL. Son cablage dans l'adaptateur, et le fait
qu'un puits fautif ou lent ne change aucun verdict, sont eprouves dans
`test_vclient_write.py`, section Z bis.
"""

from __future__ import annotations

import pathlib
from datetime import datetime, timezone

import pytest

from boilerack.adapters.evidence_sink import FileEvidenceSink
from boilerack.testing.fake_clock import VirtualClock
from boilerack.transport.vclient import EvidenceSink, WriteObservation

# La signature REELLE d'une ecriture acceptee, W4-C §16.3, a l'octet pres.
SUCCES_REEL = b'[{"command":"setNiveauM1 2","value":0.000000,"raw":"OK","error":""}]'


def _horloge() -> VirtualClock:
    return VirtualClock(datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc))


def _observation(**champs: object) -> WriteObservation:
    base: dict[str, object] = {
        "args": ("/usr/bin/vclient", "-J", "-c", "setNiveauM1 3"),
        "stdout": SUCCES_REEL,
        "stderr": b"",
        "returncode": 0,
        "duration_s": 1.045,
    }
    base.update(champs)
    return WriteObservation(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# A. Les trois fichiers, et les cinq champs
# ---------------------------------------------------------------------------


def test_une_ecriture_depose_exactement_trois_fichiers(tmp_path: pathlib.Path) -> None:
    FileEvidenceSink(tmp_path, clock=_horloge()).record(_observation())

    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "01-ecriture.err",
        "01-ecriture.meta",
        "01-ecriture.out",
    ]


def test_stdout_et_stderr_sont_bruts_integraux_et_separes(
    tmp_path: pathlib.Path,
) -> None:
    """`W4-A` §18, obligation 5 : separement, et jamais fusionnes."""
    out, err = b"\x00\xff" + b"o" * 5000, b"e" * 5000
    FileEvidenceSink(tmp_path, clock=_horloge()).record(
        _observation(stdout=out, stderr=err)
    )

    assert (tmp_path / "01-ecriture.out").read_bytes() == out
    assert (tmp_path / "01-ecriture.err").read_bytes() == err


def test_le_meta_porte_args_returncode_et_duree(tmp_path: pathlib.Path) -> None:
    """Les trois champs que `.out` et `.err` ne portent pas."""
    FileEvidenceSink(tmp_path, clock=_horloge()).record(_observation())

    meta = (tmp_path / "01-ecriture.meta").read_text(encoding="utf-8")
    assert "returncode: 0" in meta
    assert "duration_s: 1.045" in meta
    for argument in ("/usr/bin/vclient", "-J", "-c", "setNiveauM1 3"):
        assert f"  {argument}" in meta


def test_la_ligne_d_invocation_est_verbatim(tmp_path: pathlib.Path) -> None:
    """Un argument portant un espace n'est ni cite, ni echappe, ni recompose."""
    FileEvidenceSink(tmp_path, clock=_horloge()).record(
        _observation(args=("/usr/bin/vclient", "-c", "setNiveauM1 3"))
    )
    meta = (tmp_path / "01-ecriture.meta").read_text(encoding="utf-8")
    assert "  setNiveauM1 3" in meta


def test_un_returncode_absent_est_consigne_tel_quel(tmp_path: pathlib.Path) -> None:
    """`launch_failed` et `timeout` rendent `None` : la preuve le dit."""
    FileEvidenceSink(tmp_path, clock=_horloge()).record(_observation(returncode=None))
    assert "returncode: None" in (tmp_path / "01-ecriture.meta").read_text(
        encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# B. La numerotation
# ---------------------------------------------------------------------------


def test_la_numerotation_est_monotone_et_deterministe(tmp_path: pathlib.Path) -> None:
    """`01`, `02`, `03` — un rang par depot, dans l'ordre des depots."""
    puits = FileEvidenceSink(tmp_path, clock=_horloge())
    for _ in range(3):
        puits.record(_observation())

    assert sorted(p.name for p in tmp_path.glob("*.meta")) == [
        "01-ecriture.meta",
        "02-ecriture.meta",
        "03-ecriture.meta",
    ]


def test_la_numerotation_ne_derive_d_aucune_horloge(tmp_path: pathlib.Path) -> None:
    """Une horloge FIGEE ne produit ni collision, ni desordre.

    C'est le motif du §5.3 : « un nom derive d'une horloge qui a bouge
    produirait un ordre faux, ou une collision. Un compteur ne ment pas sur
    l'ordre. » Ici l'horloge ne bouge pas du tout, et les trois depots restent
    distincts et ordonnes.
    """
    horloge = _horloge()
    puits = FileEvidenceSink(tmp_path, clock=horloge)
    puits.record(_observation())
    puits.record(_observation())

    assert (tmp_path / "01-ecriture.meta").exists()
    assert (tmp_path / "02-ecriture.meta").exists()
    assert "rang: 1" in (tmp_path / "01-ecriture.meta").read_text(encoding="utf-8")
    assert "rang: 2" in (tmp_path / "02-ecriture.meta").read_text(encoding="utf-8")


def test_l_horodatage_est_une_donnee_du_meta_pas_une_cle(
    tmp_path: pathlib.Path,
) -> None:
    FileEvidenceSink(tmp_path, clock=_horloge()).record(_observation())

    meta = (tmp_path / "01-ecriture.meta").read_text(encoding="utf-8")
    assert "horodatage: 2026-08-27T12:00:00Z" in meta
    # Aucun nom de fichier ne porte d'horodatage.
    assert not list(tmp_path.glob("*2026*"))


# ---------------------------------------------------------------------------
# C. Ce que le puits ne fait pas
# ---------------------------------------------------------------------------


def test_le_puits_ne_retient_aucune_observation(tmp_path: pathlib.Path) -> None:
    """« Il ecrit et oublie » — `OBS` §5.1, puce de non-retention."""
    puits = FileEvidenceSink(tmp_path, clock=_horloge())
    puits.record(_observation())

    retenus = [
        nom
        for nom, valeur in vars(puits).items()
        if isinstance(valeur, (WriteObservation, bytes, list, tuple, dict))
    ]
    assert retenus == []


def test_le_module_ne_publie_rien_et_ne_compte_rien() -> None:
    """Ni MQTT, ni metrique, ni compteur d'observabilite."""
    source = pathlib.Path(
        __import__("boilerack.adapters.evidence_sink", fromlist=["x"]).__file__ or ""
    ).read_text(encoding="utf-8")
    corps = source.split('"""', 2)[2]
    for interdit in ("publish", "mqtt", "Counter", "metric", "socket"):
        assert interdit not in corps, interdit


def test_le_puits_cree_son_repertoire_s_il_manque(tmp_path: pathlib.Path) -> None:
    atelier = tmp_path / "g2-atelier" / "captures"
    FileEvidenceSink(atelier, clock=_horloge()).record(_observation())
    assert (atelier / "01-ecriture.out").exists()


def test_le_puits_satisfait_le_protocole() -> None:
    assert isinstance(FileEvidenceSink(pathlib.Path("."), clock=_horloge()), EvidenceSink)


def test_le_puits_leve_si_le_depot_est_impossible(tmp_path: pathlib.Path) -> None:
    """Il ne masque pas son echec : c'est l'ADAPTATEUR qui l'intercepte.

    Le contrat est ainsi reparti a dessein — `g2-sortie-preuve-transport.md`
    §5.1, clause 3. Un puits qui avalerait ses propres erreurs rendrait
    indiscernables « rien a deposer » et « depot impossible ».
    """
    fichier = tmp_path / "occupe"
    fichier.write_text("je ne suis pas un repertoire", encoding="utf-8")

    with pytest.raises(OSError):
        FileEvidenceSink(fichier, clock=_horloge()).record(_observation())


# ---------------------------------------------------------------------------
# D. Jamais d'ecrasement silencieux — R-1
# ---------------------------------------------------------------------------


def test_une_capture_existante_n_est_jamais_ecrasee(tmp_path: pathlib.Path) -> None:
    """Un atelier deja peuple fait ECHOUER le depot, il ne le laisse pas detruire.

    C'est le pire cas qu'un puits de preuve puisse produire : une capture qui
    en remplace une autre serait indiscernable d'une capture complete, et la
    preuve d'une campagne anterieure disparaitrait sans trace.
    """
    ancien = b"la preuve d'une campagne anterieure"
    (tmp_path / "01-ecriture.out").write_bytes(ancien)

    with pytest.raises(FileExistsError):
        FileEvidenceSink(tmp_path, clock=_horloge()).record(_observation())

    assert (tmp_path / "01-ecriture.out").read_bytes() == ancien


def test_l_echec_de_collision_porte_sur_chacun_des_trois(
    tmp_path: pathlib.Path,
) -> None:
    """`.err` et `.meta` sont proteges comme `.out` : aucun n'est privilegie."""
    for nom in ("01-ecriture.err", "01-ecriture.meta"):
        atelier = tmp_path / f"cas-{nom}"
        atelier.mkdir()
        (atelier / nom).write_bytes(b"anterieur")
        with pytest.raises(FileExistsError):
            FileEvidenceSink(atelier, clock=_horloge()).record(_observation())
        assert (atelier / nom).read_bytes() == b"anterieur"


def test_deux_ecritures_deposent_exactement_six_fichiers(
    tmp_path: pathlib.Path,
) -> None:
    """La cardinalite d'une campagne `G.2` : deux ecritures, six fichiers.

    Ce compte ne prouve PAS le nombre total d'ecritures — `w4f-g2` §13 le dit,
    et `U-3` reste ouverte. Il prouve les ecritures CAPTUREES, et c'est ce que
    le puits doit rendre exact.
    """
    puits = FileEvidenceSink(tmp_path, clock=_horloge())
    puits.record(_observation())
    puits.record(_observation(stdout=b"restauration"))

    fichiers = sorted(p.name for p in tmp_path.iterdir())
    assert len(fichiers) == 6
    assert fichiers == [
        "01-ecriture.err",
        "01-ecriture.meta",
        "01-ecriture.out",
        "02-ecriture.err",
        "02-ecriture.meta",
        "02-ecriture.out",
    ]


def test_un_echec_partiel_laisse_une_preuve_INCOMPLETE_et_VISIBLE(
    tmp_path: pathlib.Path,
) -> None:
    """`.out` depose, `.err` en collision : il manque deux fichiers, et cela se voit.

    Une preuve incomplete est un CONSTAT, pas un silence : l'exploitant compte
    trois fichiers par ecriture, et n'en trouve qu'un.
    """
    (tmp_path / "01-ecriture.err").write_bytes(b"anterieur")

    with pytest.raises(FileExistsError):
        FileEvidenceSink(tmp_path, clock=_horloge()).record(_observation())

    assert (tmp_path / "01-ecriture.out").exists()   # depose avant l'echec
    assert not (tmp_path / "01-ecriture.meta").exists()
    assert (tmp_path / "01-ecriture.err").read_bytes() == b"anterieur"
