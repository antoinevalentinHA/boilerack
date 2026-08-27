"""Caracterisation du contrat reel de `vclient`, a partir de fixtures verbatim.

Les fixtures de `tests/fixtures/vclient/` sont des captures reelles effectuees
le 2026-08-02 sur l'installation de reference, en lecture seule. Elles
conservent separement `stdout`, `stderr`, le code retour, la duree, la locale
et la ligne de commande exacte.

Ces tests sont PURS : ils ne lancent aucun processus, n'ouvrent aucune socket
et ne touchent aucune installation. Ils figent ce que la version
`0.98.12-5-g8ca4797` fait reellement, afin qu'un futur adaptateur soit ecrit
contre des faits et non contre des suppositions.
"""

import base64
import json
import pathlib

import pytest

from boilerack.transport.vclient import TransportStatus

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures" / "vclient"

CHAMPS_COLLECTE = {"collected_at", "client_version", "argv", "env", "external_timeout_s", "origin"}
CHAMPS_RESULTAT = {
    "returncode",
    "duration_ms",
    "stdout_len",
    "stderr_len",
    "stdout_b64",
    "stderr_b64",
}

#: Les deux seules fixtures rejouables a l'identique sur le binaire. Les autres
#: sont des transcriptions fideles du rapport de collecte : leur longueur en
#: octets corrobore la transcription, mais aucun artefact brut originel n'a ete
#: conserve. La distinction est probante et doit le rester.
RECAPTUREES = {"version", "help"}


def charger(nom: str) -> dict:
    return json.loads((FIXTURES / f"{nom}.json").read_text(encoding="utf-8"))


def flux(fixture: dict, nom: str) -> bytes:
    return base64.b64decode(fixture["result"][f"{nom}_b64"])


TOUTES = sorted(p.stem for p in FIXTURES.glob("*.json"))


# ----------------------------------------------------------
# Integrite des fixtures
# ----------------------------------------------------------


def test_les_fixtures_attendues_sont_presentes() -> None:
    assert TOUTES == [
        "client_absent",
        "daemon_unreachable",
        "help",
        "read_ok_json",
        "read_ok_locale_c",
        "read_ok_locale_production",
        "unknown_command_json",
        "unknown_command_text",
        "version",
    ]


@pytest.mark.parametrize("nom", TOUTES)
def test_schema_et_longueurs_coherentes(nom: str) -> None:
    """Chaque fixture porte son schema complet et ses longueurs declarees sont exactes."""
    f = charger(nom)
    assert CHAMPS_COLLECTE <= set(f["collection"])
    assert CHAMPS_RESULTAT <= set(f["result"])
    assert len(flux(f, "stdout")) == f["result"]["stdout_len"]
    assert len(flux(f, "stderr")) == f["result"]["stderr_len"]


@pytest.mark.parametrize("nom", TOUTES)
def test_aucune_donnee_sensible(nom: str) -> None:
    """Aucun identifiant, mot de passe ni adresse de reseau prive dans les fixtures."""
    brut = (FIXTURES / f"{nom}.json").read_text(encoding="utf-8").lower()
    for interdit in ("password", "passwd", "mqtt_pass", "192.168.", "10.0.", "secret", "token"):
        assert interdit not in brut


@pytest.mark.parametrize("nom", TOUTES)
def test_version_du_client_uniforme(nom: str) -> None:
    assert charger(nom)["collection"]["client_version"] == "0.98.12-5-g8ca4797"


# ----------------------------------------------------------
# Provenance : recapture verbatim contre transcription fidele
# ----------------------------------------------------------


@pytest.mark.parametrize("nom", TOUTES)
def test_la_provenance_est_qualifiee_sans_ambiguite(nom: str) -> None:
    """Chaque fixture declare laquelle des deux natures elle possede.

    Une transcription ne doit jamais pouvoir se presenter comme un artefact
    brut originel conserve depuis la sonde : les repertoires de capture ont
    ete supprimes en fin de collecte, et aucune transcription n'est donc
    verifiable contre un original.
    """
    origine = charger(nom)["collection"]["origin"]
    attendu = "recaptur" if nom in RECAPTUREES else "transcrit"
    assert attendu in origine, f"{nom} : provenance attendue '{attendu}', lue {origine!r}"

    interdits = ("capture brute originelle", "artefact brut", "fichier brut conserve")
    for mot in interdits:
        assert mot not in origine.lower(), f"{nom} : qualification trompeuse — {mot!r}"


def test_exactement_deux_recaptures_et_sept_transcriptions() -> None:
    natures = {
        n: (
            "recapture"
            if "recaptur" in charger(n)["collection"]["origin"]
            else "transcription"
        )
        for n in TOUTES
    }
    assert sorted(n for n, v in natures.items() if v == "recapture") == ["help", "version"]
    assert len([n for n, v in natures.items() if v == "transcription"]) == 7


# ----------------------------------------------------------
# CLIENT_UNAVAILABLE reste une proposition
# ----------------------------------------------------------


def test_client_unavailable_n_appartient_pas_a_l_enumeration() -> None:
    """La valeur proposee ne doit pas avoir ete ajoutee subrepticement."""
    assert "CLIENT_UNAVAILABLE" not in {membre.name for membre in TransportStatus}


def test_l_enumeration_n_est_pas_modifiee_par_ce_lot() -> None:
    """Toute evolution de `TransportStatus` doit etre un acte conscient.

    Ce lot documente une septieme valeur candidate ; il ne l'introduit pas.
    Si l'arbitrage aboutit, ce test devra etre mis a jour explicitement.
    """
    assert {membre.name for membre in TransportStatus} == {
        "OK",
        "DAEMON_UNREACHABLE",
        "UNKNOWN_COMMAND",
        "TIMEOUT",
        "UNUSABLE_OUTPUT",
        "TRANSPORT_ERROR",
    }


def test_la_fixture_du_client_absent_declare_un_statut_candidat() -> None:
    """Elle porte `candidate_status`, jamais `expected_status`."""
    f = charger("client_absent")
    assert f["status_is_proposed"] is True
    assert f["candidate_status"] == "CLIENT_UNAVAILABLE"
    assert "expected_status" not in f
    assert f["proposal_reference"].startswith("docs/design/c5-vclient-contract.md")


@pytest.mark.parametrize("nom", sorted(set(TOUTES) - {"client_absent"}))
def test_les_autres_fixtures_ne_portent_aucun_statut_propose(nom: str) -> None:
    f = charger(nom)
    assert f["status_is_proposed"] is False
    statut = f["expected_status"]
    assert statut == "n/a" or statut in {membre.name for membre in TransportStatus}


def test_la_sonde_du_client_absent_caracterise_timeout_et_non_subprocess() -> None:
    """La distinction des deux niveaux doit rester inscrite dans la fixture.

    Le message provient de l'utilitaire GNU `timeout`, qui rend 127. Le
    comportement de `subprocess.run()` est caracterise separement en C4, par
    les exceptions Python.
    """
    notes = charger("client_absent")["notes"].lower()
    assert "timeout" in notes
    assert "exec direct" in notes or "sans shell" in notes


# ----------------------------------------------------------
# Le code retour ne discrimine rien
# ----------------------------------------------------------


def test_un_resultat_normal_peut_rendre_un_code_retour_non_nul() -> None:
    """`-V` et `--help` aboutissent normalement mais rendent 1."""
    assert charger("version")["result"]["returncode"] == 1
    assert charger("help")["result"]["returncode"] == 1
    assert b"vclient version 0.98.12-5-g8ca4797" in flux(charger("version"), "stdout")


def test_un_echec_peut_rendre_un_code_retour_nul() -> None:
    """Une commande inconnue rend 0, dans les deux formes de sortie."""
    assert charger("unknown_command_text")["result"]["returncode"] == 0
    assert charger("unknown_command_json")["result"]["returncode"] == 0


def test_le_code_retour_seul_ne_permet_aucune_conclusion() -> None:
    """Demonstration d'ensemble : 0 et 1 recouvrent chacun succes et echec.

    Les statuts cites ici sont ceux de l'enumeration existante. La fixture du
    client absent porte un statut CANDIDAT et est donc traitee a part.
    """
    par_code: dict[int, set[str]] = {}
    for nom in TOUTES:
        f = charger(nom)
        if f["status_is_proposed"]:
            continue
        par_code.setdefault(f["result"]["returncode"], set()).add(f["expected_status"])

    assert par_code[0] == {"OK", "UNKNOWN_COMMAND"}
    assert par_code[1] == {"n/a", "DAEMON_UNREACHABLE"}
    assert 127 not in par_code, "aucun statut existant ne couvre l'echec de lancement"


# ----------------------------------------------------------
# Lecture reussie
# ----------------------------------------------------------


def test_forme_texte_d_une_lecture_reussie() -> None:
    f = charger("read_ok_locale_production")
    assert f["result"]["returncode"] == 0
    assert flux(f, "stdout") == b"getTempKist:\n28.000000 Grad Celsius\n"
    assert flux(f, "stderr") == b""


def test_la_valeur_et_l_unite_sont_sur_la_seconde_ligne() -> None:
    lignes = flux(charger("read_ok_locale_production"), "stdout").decode().splitlines()
    assert lignes[0] == "getTempKist:"
    assert lignes[1].split() == ["28.000000", "Grad", "Celsius"]


def test_la_sortie_est_insensible_a_la_locale() -> None:
    """Locale de production et LC_ALL=C produisent des octets identiques.

    Consequence : la substitution de virgule decimale presente dans le bridge
    historique est defensive et sans objet sur cette installation.
    """
    prod = charger("read_ok_locale_production")
    forcee = charger("read_ok_locale_c")
    assert prod["collection"]["env"]["LC_ALL"] is None
    assert forcee["collection"]["env"]["LC_ALL"] == "C"
    assert flux(prod, "stdout") == flux(forcee, "stdout")
    assert b"," not in flux(prod, "stdout")


# ----------------------------------------------------------
# Forme JSON
# ----------------------------------------------------------


def test_json_succes() -> None:
    charge = json.loads(flux(charger("read_ok_json"), "stdout").decode())
    assert isinstance(charge, list) and len(charge) == 1
    objet = charge[0]
    assert set(objet) == {"command", "value", "raw", "error"}
    assert objet["command"] == "getTempKist"
    assert objet["error"] == ""
    assert objet["value"] == pytest.approx(28.0)
    assert objet["raw"] == "28.000000 Grad Celsius"


def test_json_echec_le_champ_error_est_le_discriminant() -> None:
    charge = json.loads(flux(charger("unknown_command_json"), "stdout").decode())
    objet = charge[0]
    assert objet["error"] == "ERR: command unknown"
    assert objet["raw"] == "ERR: command unknown"


def test_json_echec_la_valeur_vaut_zero_et_constitue_un_piege() -> None:
    """En erreur, `value` vaut 0.0 — une valeur plausible pour une temperature.

    Un consommateur qui lirait `value` sans verifier `error` obtiendrait
    0,0 degre pour une commande inexistante.
    """
    objet = json.loads(flux(charger("unknown_command_json"), "stdout").decode())[0]
    assert objet["value"] == 0.0
    assert objet["error"] != ""


# ----------------------------------------------------------
# Erreurs
# ----------------------------------------------------------


def test_commande_inconnue_forme_texte() -> None:
    f = charger("unknown_command_text")
    assert flux(f, "stdout") == b"boilerack_c5_commande_inexistante_20260802:\n"
    assert flux(f, "stderr") == b"SRV ERR: command unknown\nserver error\n"


def test_le_message_d_erreur_commence_par_SRV_et_non_par_ERR() -> None:
    """Detail decisif : le prefixe reel est `SRV `, pas `ERR`."""
    premiere = flux(charger("unknown_command_text"), "stderr").decode().splitlines()[0]
    assert premiere.startswith("SRV ERR:")
    assert not premiere.startswith("ERR")


def test_demon_injoignable_les_deux_flux_sont_vides() -> None:
    f = charger("daemon_unreachable")
    assert f["result"]["returncode"] == 1
    assert flux(f, "stdout") == b""
    assert flux(f, "stderr") == b""


def test_client_absent() -> None:
    f = charger("client_absent")
    assert f["result"]["returncode"] == 127
    assert flux(f, "stdout") == b""
    assert b"No such file or directory" in flux(f, "stderr")


def test_rejet_local_sans_transaction_optolink() -> None:
    """Une commande inconnue est rejetee par le demon, sans acces a la chaudiere.

    111 ms contre 2669 a 4029 ms pour une lecture reelle : deux ordres de
    grandeur qui distinguent un rejet local d'une transaction Optolink.
    """
    inconnue = charger("unknown_command_text")["result"]["duration_ms"]
    lecture = charger("read_ok_locale_production")["result"]["duration_ms"]
    assert inconnue < 500
    assert lecture > 2000


def test_les_erreurs_avant_connexion_sont_immediates() -> None:
    assert charger("daemon_unreachable")["result"]["duration_ms"] < 100
    assert charger("client_absent")["result"]["duration_ms"] < 100


# ----------------------------------------------------------
# Defaut latent du bridge historique, demontre sur fixture reelle
# ----------------------------------------------------------


def _filtre_historique(sortie_fusionnee: str) -> str | None:
    """Transcription du filtre de `get_value`, boiler_mqtt.py L157-172.

    Reproduit tel quel, y compris son defaut. Le bridge historique fusionne
    `stdout` et `stderr` via `stderr=subprocess.STDOUT`, puis applique ce
    filtre a la sortie combinee.
    """
    for ligne in sortie_fusionnee.splitlines():
        nettoyee = ligne.strip()
        if not nettoyee:
            continue
        if nettoyee.startswith("vctrld>"):
            continue
        if nettoyee.startswith("ERR"):
            continue
        if nettoyee.endswith(":"):
            continue
        return nettoyee.split()[0]
    return None


def test_le_filtre_historique_rend_SRV_sur_une_commande_inconnue() -> None:
    """Defaut latent demontre sur la capture reelle.

    Le filtre ecarte les lignes commencant par `ERR`, mais le message reel
    commence par `SRV`. Combine a un code retour nul — qui empeche
    `check_output` de lever — une commande inconnue produit la chaine `SRV`
    en guise de valeur.

    Consequences dans le bridge historique : `SRV` publie comme valeur de
    telemetrie, et surtout une sante rendue faussement nominale, la valeur
    n'etant pas nulle.

    Non atteignable en production aujourd'hui : le jeu de commandes est fige
    et les definitions sont intactes. Le defaut est donc LATENT. Il est
    documente ici pour qu'il ne soit pas reproduit, jamais corrige a la
    volee sur la production.
    """
    f = charger("unknown_command_text")
    fusionnee = (flux(f, "stdout") + flux(f, "stderr")).decode()
    assert _filtre_historique(fusionnee) == "SRV"


def test_le_filtre_historique_fonctionne_sur_une_lecture_reussie() -> None:
    """Le meme filtre est correct dans le cas nominal — d'ou l'invisibilite du defaut."""
    f = charger("read_ok_locale_production")
    fusionnee = (flux(f, "stdout") + flux(f, "stderr")).decode()
    assert _filtre_historique(fusionnee) == "28.000000"


def test_le_filtre_historique_rend_None_si_le_demon_est_injoignable() -> None:
    """Cas correctement traite : sortie vide, donc aucune valeur."""
    f = charger("daemon_unreachable")
    fusionnee = (flux(f, "stdout") + flux(f, "stderr")).decode()
    assert _filtre_historique(fusionnee) is None
