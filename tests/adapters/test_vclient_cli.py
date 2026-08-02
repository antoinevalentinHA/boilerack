"""Tests du lecteur `vclient` en lecture seule (C6).

Entierement deterministes et hors ligne : aucun vrai processus, aucun appel a
`vclient`, aucune socket, aucun reseau, aucun shell. Le `ProcessRunner` est
remplace par un double qui rend un `ProcessResult` fabrique ou rejoue depuis
les fixtures C5, lesquelles sont lues et jamais modifiees.
"""

from __future__ import annotations

import base64
import json
import pathlib
from dataclasses import dataclass, field
from typing import Mapping

import pytest

from boilerack.adapters.config import VclientConfig
from boilerack.adapters.process_runner import ProcessResult
from boilerack.adapters.vclient_cli import InvalidCommandName, VClientCliReader
from boilerack.transport.vclient import ReadResult, TransportStatus, VClient

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "vclient"


# ----------------------------------------------------------
# Double de `ProcessRunner`
# ----------------------------------------------------------


@dataclass
class FauxRunner:
    """Rend un resultat programme et enregistre l'appel recu."""

    resultat: ProcessResult
    appels: list[tuple[list[str], float, Mapping[str, str] | None]] = field(default_factory=list)

    def run(
        self,
        args: list[str],
        timeout: float,
        env: Mapping[str, str] | None = None,
    ) -> ProcessResult:
        self.appels.append((list(args), timeout, env))
        return self.resultat


def resultat(
    *,
    returncode: int | None = 0,
    stdout: bytes = b"",
    stderr: bytes = b"",
    timed_out: bool = False,
    launch_failed: bool = False,
    launch_error: str = "",
) -> ProcessResult:
    return ProcessResult(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
        launch_failed=launch_failed,
        launch_error=launch_error,
    )


def lecteur(res: ProcessResult, **surcharges: object) -> tuple[VClientCliReader, FauxRunner]:
    params: dict[str, object] = {
        "executable": "vclient",
        "host": "localhost",
        "port": 3002,
        "read_timeout_s": 5.0,
    }
    params.update(surcharges)
    faux = FauxRunner(res)
    return VClientCliReader(VclientConfig(**params), faux), faux  # type: ignore[arg-type]


def fixture(nom: str) -> ProcessResult:
    """Rejoue une fixture C5 telle quelle, en octets."""
    f = json.loads((FIXTURES / f"{nom}.json").read_text(encoding="utf-8"))
    r = f["result"]
    return resultat(
        returncode=r["returncode"],
        stdout=base64.b64decode(r["stdout_b64"]),
        stderr=base64.b64decode(r["stderr_b64"]),
    )


def json_lecture(command: str = "getTempKist", **champs: object) -> bytes:
    objet: dict[str, object] = {
        "command": command,
        "value": 28.0,
        "raw": "28.000000 Grad Celsius",
        "error": "",
    }
    objet.update(champs)
    return (json.dumps([objet]) + "\n").encode()


# ----------------------------------------------------------
# 1-5. Construction des arguments et configuration
# ----------------------------------------------------------


def test_arguments_exacts() -> None:
    lect, faux = lecteur(fixture("read_ok_json"))
    lect.read("getTempKist")
    args, timeout, env = faux.appels[0]
    assert args == ["vclient", "-h", "localhost", "-p", "3002", "-J", "-c", "getTempKist"]
    assert timeout == 5.0
    assert env is None


def test_executable_configurable() -> None:
    lect, faux = lecteur(fixture("read_ok_json"), executable="/opt/bin/vclient")
    lect.read("getTempKist")
    assert faux.appels[0][0][0] == "/opt/bin/vclient"


def test_hote_configurable() -> None:
    lect, faux = lecteur(fixture("read_ok_json"), host="10.1.2.3")
    lect.read("getTempKist")
    assert faux.appels[0][0][1:3] == ["-h", "10.1.2.3"]


def test_port_configurable() -> None:
    lect, faux = lecteur(fixture("read_ok_json"), port=3999)
    lect.read("getTempKist")
    assert "-p" in faux.appels[0][0]
    assert faux.appels[0][0][faux.appels[0][0].index("-p") + 1] == "3999"


def test_timeout_transmis() -> None:
    lect, faux = lecteur(fixture("read_ok_json"), read_timeout_s=12.5)
    lect.read("getTempKist")
    assert faux.appels[0][1] == 12.5


def test_hote_et_port_omis_quand_non_configures() -> None:
    lect, faux = lecteur(fixture("read_ok_json"), host=None, port=None)
    lect.read("getTempKist")
    assert faux.appels[0][0] == ["vclient", "-J", "-c", "getTempKist"]


def test_une_seule_commande_par_invocation() -> None:
    lect, faux = lecteur(fixture("read_ok_json"))
    lect.read("getTempKist")
    args = faux.appels[0][0]
    assert args.count("-c") == 1
    assert "," not in args[args.index("-c") + 1]


# ----------------------------------------------------------
# Validation du nom de commande
# ----------------------------------------------------------


@pytest.mark.parametrize(
    ("nom", "motif"),
    [
        ("", "non vide"),
        (" getTempKist", "espaces"),
        ("getTempKist ", "espaces"),
        ("getTemp\nKist", "controle"),
        ("getTemp\x00Kist", "controle"),
        ("getTempKist,getTempA", "virgule"),
        ("-J", "option"),
    ],
)
def test_noms_de_commande_refuses_avant_toute_invocation(nom: str, motif: str) -> None:
    lect, faux = lecteur(fixture("read_ok_json"))
    with pytest.raises(InvalidCommandName, match=motif):
        lect.read(nom)
    assert faux.appels == [], "aucun processus ne doit avoir ete sollicite"


def test_nom_de_commande_quelconque_accepte() -> None:
    """Aucune liste blanche de datapoints : les noms sont opaques au transport."""
    lect, faux = lecteur(fixture("read_ok_json"))
    assert lect.build_args("uneCommandeInconnueDuProjet")[-1] == "uneCommandeInconnueDuProjet"
    assert faux.appels == []


# ----------------------------------------------------------
# 6. Lecture reussie, depuis la fixture C5
# ----------------------------------------------------------


def test_lecture_reussie_depuis_la_fixture_c5() -> None:
    lect, _ = lecteur(fixture("read_ok_json"))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.OK
    assert r.value == pytest.approx(28.0)
    assert "28.000000 Grad Celsius" in (r.raw or "")


def test_la_valeur_provient_du_champ_value_et_non_de_raw() -> None:
    lect, _ = lecteur(resultat(stdout=json_lecture(value=31.5, raw="99.9 Grad Celsius")))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.OK
    assert r.value == pytest.approx(31.5)


# ----------------------------------------------------------
# 7. Commande inconnue
# ----------------------------------------------------------


def test_commande_inconnue_depuis_la_fixture_c5() -> None:
    """La fixture JSON est la forme reellement utilisee par l'adaptateur (`-J`)."""
    nom = "boilerack_c5_commande_inexistante_20260802"
    lect, _ = lecteur(fixture("unknown_command_json"))
    r = lect.read(nom)
    assert r.status is TransportStatus.UNKNOWN_COMMAND
    assert r.value is None


def test_la_forme_texte_n_est_pas_exploitee_par_l_adaptateur() -> None:
    """L'adaptateur n'emet que `-J` ; une sortie texte est structurellement invalide."""
    nom = "boilerack_c5_commande_inexistante_20260802"
    lect, _ = lecteur(fixture("unknown_command_text"))
    r = lect.read(nom)
    assert r.status is TransportStatus.UNUSABLE_OUTPUT


@pytest.mark.parametrize(
    "erreur",
    ["ERR: something else", "ERR:", "erreur", "server error", "ERR: command unknown "],
)
def test_seul_le_signal_exact_donne_commande_inconnue(erreur: str) -> None:
    lect, _ = lecteur(resultat(stdout=json_lecture(error=erreur)))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert r.status is not TransportStatus.UNKNOWN_COMMAND


def test_stderr_seul_ne_classe_jamais_en_commande_inconnue() -> None:
    """`stderr` peut porter le message alors que `stdout` est un succes bien forme."""
    lect, _ = lecteur(resultat(stdout=json_lecture(), stderr=b"SRV ERR: command unknown\n"))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.OK


# ----------------------------------------------------------
# 8-10. Echecs de transport
# ----------------------------------------------------------


def test_demon_injoignable_depuis_la_fixture_c5() -> None:
    lect, _ = lecteur(fixture("daemon_unreachable"))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.DAEMON_UNREACHABLE
    assert r.value is None


@pytest.mark.parametrize(
    ("rc", "out", "err"),
    [
        (1, b"du texte\n", b""),
        (1, b"", b"un message\n"),
        (2, b"", b""),
        (127, b"", b""),
        (0, b"", b""),
    ],
)
def test_la_signature_du_demon_injoignable_n_est_pas_generalisee(
    rc: int, out: bytes, err: bytes
) -> None:
    lect, _ = lecteur(resultat(returncode=rc, stdout=out, stderr=err))
    r = lect.read("getTempKist")
    assert r.status is not TransportStatus.DAEMON_UNREACHABLE


def test_client_absent_donne_transport_error() -> None:
    """C6 ne ratifie pas `CLIENT_UNAVAILABLE` : on reste prudent."""
    lect, _ = lecteur(
        resultat(returncode=None, launch_failed=True, launch_error="FileNotFoundError")
    )
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "FileNotFoundError" in r.detail


def test_permission_refusee_donne_aussi_transport_error() -> None:
    lect, _ = lecteur(
        resultat(returncode=None, launch_failed=True, launch_error="PermissionError")
    )
    assert lect.read("getTempKist").status is TransportStatus.TRANSPORT_ERROR


def test_timeout_externe() -> None:
    lect, _ = lecteur(resultat(returncode=None, timed_out=True))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.TIMEOUT


def test_une_sortie_partielle_en_timeout_n_est_jamais_exploitee() -> None:
    lect, _ = lecteur(resultat(returncode=None, timed_out=True, stdout=json_lecture()))
    assert lect.read("getTempKist").status is TransportStatus.TIMEOUT


# ----------------------------------------------------------
# 11-21. Structure JSON inexploitable
# ----------------------------------------------------------


@pytest.mark.parametrize(
    ("charge", "motif"),
    [
        (b"pas du json\n", "JSON invalide"),
        (b"", "JSON invalide"),
        (b'{"command":"getTempKist"}\n', "racine JSON non liste"),
        (b'"une chaine"\n', "racine JSON non liste"),
        (b"[]\n", "liste JSON vide"),
        (b'[{"command":"a","value":1,"raw":"","error":""},'
         b'{"command":"b","value":2,"raw":"","error":""}]\n', "ambigue"),
        (b'["pas un objet"]\n', "non objet"),
    ],
)
def test_structures_inexploitables(charge: bytes, motif: str) -> None:
    lect, _ = lecteur(resultat(stdout=charge))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.UNUSABLE_OUTPUT
    assert motif in r.detail


def test_commande_differente_de_celle_demandee() -> None:
    lect, _ = lecteur(resultat(stdout=json_lecture(command="getTempA")))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.UNUSABLE_OUTPUT
    assert "commande inattendue" in r.detail


@pytest.mark.parametrize("absent", ["command", "value", "raw", "error"])
def test_champ_manquant(absent: str) -> None:
    objet = {"command": "getTempKist", "value": 28.0, "raw": "x", "error": ""}
    del objet[absent]
    lect, _ = lecteur(resultat(stdout=(json.dumps([objet]) + "\n").encode()))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.UNUSABLE_OUTPUT
    assert absent in r.detail


@pytest.mark.parametrize("valeur", ["28.0", None, [28.0], {"v": 28.0}])
def test_value_non_numerique(valeur: object) -> None:
    lect, _ = lecteur(resultat(stdout=json_lecture(value=valeur)))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.UNUSABLE_OUTPUT
    assert "non numerique" in r.detail


@pytest.mark.parametrize("valeur", [True, False])
def test_value_booleenne_refusee(valeur: bool) -> None:
    """`isinstance(True, int)` vaut True en Python : la garde doit etre explicite."""
    lect, _ = lecteur(resultat(stdout=json_lecture(value=valeur)))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.UNUSABLE_OUTPUT
    assert "non numerique" in r.detail


@pytest.mark.parametrize("litteral", ["NaN", "Infinity", "-Infinity"])
def test_value_non_finie(litteral: str) -> None:
    charge = (
        '[{"command":"getTempKist","value":' + litteral + ',"raw":"x","error":""}]\n'
    ).encode()
    lect, _ = lecteur(resultat(stdout=charge))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.UNUSABLE_OUTPUT
    assert "non finie" in r.detail


def test_command_non_textuel() -> None:
    lect, _ = lecteur(resultat(stdout=json_lecture(command=42)))
    assert lect.read("getTempKist").status is TransportStatus.UNUSABLE_OUTPUT


def test_error_non_textuel() -> None:
    lect, _ = lecteur(resultat(stdout=json_lecture(error=1)))
    assert lect.read("getTempKist").status is TransportStatus.UNUSABLE_OUTPUT


# ----------------------------------------------------------
# 23-26. Decodage, flux separes, codes retour
# ----------------------------------------------------------


def test_stdout_non_decodable() -> None:
    lect, _ = lecteur(resultat(stdout=b"\xff\xfe\x00 pas de l'utf-8"))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.UNUSABLE_OUTPUT
    assert "non decodable" in r.detail


def test_stderr_non_decodable_n_empeche_pas_le_verdict() -> None:
    lect, _ = lecteur(resultat(stdout=json_lecture(), stderr=b"\xff\xfe"))
    assert lect.read("getTempKist").status is TransportStatus.OK


def test_stderr_est_conserve_pour_diagnostic_sans_porter_le_verdict() -> None:
    lect, _ = lecteur(
        resultat(stdout=json_lecture(error="ERR: something else"), stderr=b"SRV ERR: autre\n")
    )
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.TRANSPORT_ERROR
    assert "stderr:" in r.detail


def test_les_flux_ne_sont_jamais_fusionnes() -> None:
    """Un JSON valide sur stdout reste exploitable quel que soit le bruit sur stderr."""
    lect, _ = lecteur(resultat(stdout=json_lecture(), stderr=b"[{\"command\":\"x\"}]\n"))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.OK
    assert r.value == pytest.approx(28.0)


def test_code_retour_non_nul_avec_json_valide_reste_exploite() -> None:
    """Le code retour seul ne prouve rien : C5 l'a etabli dans les deux sens."""
    lect, _ = lecteur(resultat(returncode=3, stdout=json_lecture()))
    r = lect.read("getTempKist")
    assert r.status is TransportStatus.OK


def test_code_retour_nul_avec_erreur_structuree_reste_une_erreur() -> None:
    lect, _ = lecteur(resultat(returncode=0, stdout=json_lecture(error="ERR: command unknown")))
    assert lect.read("getTempKist").status is TransportStatus.UNKNOWN_COMMAND


# ----------------------------------------------------------
# 27-28. Absence d'ecriture, non-conformite assumee
# ----------------------------------------------------------


def test_le_lecteur_n_a_aucune_methode_write() -> None:
    """Une methode `write` bouchon exposerait a un faux `applied` (cf. module)."""
    assert not hasattr(VClientCliReader, "write")
    lect, _ = lecteur(fixture("read_ok_json"))
    assert not hasattr(lect, "write")


def test_le_lecteur_ne_satisfait_pas_le_protocole_vclient() -> None:
    """Non-conformite INTENTIONNELLE : `VClient` exige `read` ET `write`.

    Ce test echouera le jour ou une methode `write` sera ajoutee — ce qui est
    voulu : la conformite ne doit pas s'acquerir par inadvertance, mais par une
    caracterisation reelle du chemin d'ecriture.
    """
    lect, _ = lecteur(fixture("read_ok_json"))
    assert not isinstance(lect, VClient)


def test_le_lecteur_expose_bien_read() -> None:
    lect, _ = lecteur(fixture("read_ok_json"))
    assert callable(lect.read)
    assert isinstance(lect.read("getTempKist"), ReadResult)


def test_aucun_statut_hors_enumeration_n_est_produit() -> None:
    """Balayage : toutes les issues produites appartiennent aux six valeurs."""
    cas = [
        fixture("read_ok_json"),
        fixture("unknown_command_json"),
        fixture("daemon_unreachable"),
        resultat(returncode=None, launch_failed=True, launch_error="OSError"),
        resultat(returncode=None, timed_out=True),
        resultat(stdout=b"pas du json"),
        resultat(stdout=json_lecture(error="ERR: autre")),
    ]
    for res in cas:
        lect, _ = lecteur(res)
        r = lect.read("boilerack_c5_commande_inexistante_20260802")
        assert r.status in set(TransportStatus)


# ----------------------------------------------------------
# Preuve d'absence de processus et de reseau
# ----------------------------------------------------------


def test_aucun_sous_processus_ni_socket_n_est_utilise(monkeypatch: pytest.MonkeyPatch) -> None:
    """Toute tentative de lancer un processus ou d'ouvrir une socket echoue le test."""
    import socket
    import subprocess

    def interdit(*_a: object, **_k: object) -> None:
        raise AssertionError("appel systeme interdit dans les tests C6")

    monkeypatch.setattr(subprocess, "run", interdit)
    monkeypatch.setattr(subprocess, "Popen", interdit)
    monkeypatch.setattr(socket, "socket", interdit)

    lect, _ = lecteur(fixture("read_ok_json"))
    assert lect.read("getTempKist").status is TransportStatus.OK
