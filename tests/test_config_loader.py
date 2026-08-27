"""Tests du chargeur de configuration C10 — `boilerack.config`.

Aucun broker, aucun `vclient`, aucun `vcontrold`, aucune chaudiere. Les seuls
acces sont un fichier temporaire et la variable d'environnement du secret.
"""

from __future__ import annotations

import os
import socket
import subprocess

import pytest

from boilerack.config import PASSWORD_ENV_VAR, ConfigurationError, load_config
from boilerack.read_surface.measurements import (
    V1_MEASUREMENTS,
    MeasurementSpec,
    check_snapshot_period,
)
from boilerack.runtime import RuntimeConfig

#: Configuration minimale valide : les deux seules cles obligatoires.
MINIMALE = """
[mqtt]
host = "broker.exemple.invalid"

[vclient]
executable = "vclient"
"""


@pytest.fixture(autouse=True)
def sans_secret(monkeypatch):
    """Aucun test ne doit dependre de l'environnement de la machine."""
    monkeypatch.delenv(PASSWORD_ENV_VAR, raising=False)


@pytest.fixture
def ecrire(tmp_path):
    """Ecrit un TOML temporaire et rend son chemin."""

    def _ecrire(contenu: str, nom: str = "boilerack.toml"):
        chemin = tmp_path / nom
        chemin.write_text(contenu, encoding="utf-8")
        return chemin

    return _ecrire


# ---------------------------------------------------------------------------
# Chargement et schema
# ---------------------------------------------------------------------------


def test_configuration_minimale_valide(ecrire) -> None:
    config = load_config(ecrire(MINIMALE))
    assert isinstance(config, RuntimeConfig)
    assert config.mqtt.host == "broker.exemple.invalid"
    assert config.vclient.executable == "vclient"


def test_fichier_absent(tmp_path) -> None:
    with pytest.raises(ConfigurationError, match="introuvable"):
        load_config(tmp_path / "nexiste.pas")


def test_repertoire_au_lieu_d_un_fichier(tmp_path) -> None:
    """Portable : un repertoire existe partout, contrairement a un fichier
    rendu illisible, dont la mecanique differe selon la plateforme."""
    with pytest.raises(ConfigurationError):
        load_config(tmp_path)


def test_toml_malforme(ecrire) -> None:
    with pytest.raises(ConfigurationError, match="TOML invalide"):
        load_config(ecrire("[mqtt\nhost = 1\n"))


def test_table_inconnue_refusee(ecrire) -> None:
    with pytest.raises(ConfigurationError, match=r"table inconnue.*\[divers\]"):
        load_config(ecrire(MINIMALE + '\n[divers]\nx = 1\n'))


@pytest.mark.parametrize(
    ("table", "contenu"),
    [
        ("mqtt", '[mqtt]\nhost = "b"\nhots = "x"\n[vclient]\nexecutable = "v"\n'),
        ("vclient", '[mqtt]\nhost = "b"\n[vclient]\nexecutable = "v"\nexecutible = "x"\n'),
        ("read_surface", MINIMALE + '\n[read_surface]\nprefixe = "x"\n'),
    ],
)
def test_cle_inconnue_refusee_dans_chaque_table(ecrire, table, contenu) -> None:
    with pytest.raises(ConfigurationError, match=rf"cle inconnue : \[{table}\]"):
        load_config(ecrire(contenu))


def test_table_qui_n_en_est_pas_une(ecrire) -> None:
    with pytest.raises(ConfigurationError, match=r"\[mqtt\] doit etre une table"):
        load_config(ecrire('mqtt = 1\n[vclient]\nexecutable = "v"\n'))


@pytest.mark.parametrize(
    ("cle", "contenu"),
    [
        ("[mqtt].host", '[mqtt]\nport = 1883\n[vclient]\nexecutable = "v"\n'),
        ("[vclient].executable", '[mqtt]\nhost = "b"\n[vclient]\nport = 3002\n'),
    ],
)
def test_cle_obligatoire_absente(ecrire, cle, contenu) -> None:
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(contenu))
    assert cle in str(capture.value)
    assert "obligatoire" in str(capture.value)


def test_tables_optionnelles_absentes(ecrire) -> None:
    """`[read_surface]` entiere peut manquer : tous ses defauts s'appliquent."""
    config = load_config(ecrire(MINIMALE))
    assert config.read_surface.prefix == "boiler"


# ---------------------------------------------------------------------------
# Valeurs par defaut — celles des structures, jamais recopiees
# ---------------------------------------------------------------------------


def test_defauts_exacts(ecrire) -> None:
    config = load_config(ecrire(MINIMALE))
    assert config.mqtt.port == 1883
    assert config.mqtt.client_id == "boilerack"
    assert config.mqtt.keepalive == 60
    assert config.mqtt.username is None
    assert config.mqtt.tls is False
    assert config.vclient.host is None
    assert config.vclient.port is None
    assert config.vclient.read_timeout_s == 5.0
    assert config.read_surface.prefix == "boiler"
    assert config.read_surface.snapshot_period_s == 30
    assert config.read_surface.heartbeat_period_s == 30
    assert config.specs == V1_MEASUREMENTS


def test_toutes_les_cles_publiques_sont_acceptees(ecrire) -> None:
    """Les treize cles du contrat, ensemble, dans un seul fichier."""
    config = load_config(
        ecrire(
            """
[mqtt]
host = "broker.exemple.invalid"
port = 8883
client_id = "pont-1"
keepalive = 45
username = "utilisateur"
tls = true

[vclient]
executable = "/opt/vclient"
host = "vcontrold.exemple.invalid"
port = 3002
read_timeout_s = 7.5

[read_surface]
prefix = "maison/boiler"
snapshot_period_s = 20
heartbeat_period_s = 15
"""
        )
    )
    assert (config.mqtt.port, config.mqtt.client_id, config.mqtt.keepalive) == (
        8883,
        "pont-1",
        45,
    )
    assert (config.mqtt.username, config.mqtt.tls) == ("utilisateur", True)
    assert (config.vclient.host, config.vclient.port) == ("vcontrold.exemple.invalid", 3002)
    assert config.vclient.read_timeout_s == 7.5
    assert config.read_surface.prefix == "maison/boiler"
    assert (config.read_surface.snapshot_period_s, config.read_surface.heartbeat_period_s) == (
        20,
        15,
    )


# ---------------------------------------------------------------------------
# Types TOML stricts
# ---------------------------------------------------------------------------

#: Chaque cle entiere du schema, avec un fichier complet autour.
_CLES_ENTIERES = [
    ("[mqtt].port", '[mqtt]\nhost = "b"\nport = {v}\n[vclient]\nexecutable = "v"\n'),
    ("[mqtt].keepalive", '[mqtt]\nhost = "b"\nkeepalive = {v}\n[vclient]\nexecutable = "v"\n'),
    ("[vclient].port", '[mqtt]\nhost = "b"\n[vclient]\nexecutable = "v"\nport = {v}\n'),
    (
        "[read_surface].snapshot_period_s",
        MINIMALE + "\n[read_surface]\nsnapshot_period_s = {v}\n",
    ),
    (
        "[read_surface].heartbeat_period_s",
        MINIMALE + "\n[read_surface]\nheartbeat_period_s = {v}\n",
    ),
]


@pytest.mark.parametrize(("cle", "gabarit"), _CLES_ENTIERES)
@pytest.mark.parametrize("booleen", ["true", "false"])
def test_un_booleen_est_refuse_partout_ou_un_entier_est_attendu(
    ecrire, cle, gabarit, booleen
) -> None:
    """`isinstance(True, int)` vaut `True` : la garde doit porter sur le type exact."""
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(gabarit.format(v=booleen)))
    assert cle in str(capture.value)
    assert "entier" in str(capture.value)
    assert "bool" in str(capture.value)


@pytest.mark.parametrize(("cle", "gabarit"), _CLES_ENTIERES)
def test_un_flottant_est_refuse_la_ou_un_entier_est_attendu(ecrire, cle, gabarit) -> None:
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(gabarit.format(v="30.5")))
    assert cle in str(capture.value)
    assert "entier" in str(capture.value)


@pytest.mark.parametrize(("cle", "gabarit"), _CLES_ENTIERES)
def test_une_chaine_est_refusee_la_ou_un_entier_est_attendu(ecrire, cle, gabarit) -> None:
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(gabarit.format(v='"30"')))
    assert cle in str(capture.value)


@pytest.mark.parametrize(
    ("cle", "contenu"),
    [
        ("[mqtt].host", "[mqtt]\nhost = 1\n[vclient]\nexecutable = \"v\"\n"),
        ("[mqtt].client_id", '[mqtt]\nhost = "b"\nclient_id = 1\n[vclient]\nexecutable = "v"\n'),
        ("[mqtt].username", '[mqtt]\nhost = "b"\nusername = 1\n[vclient]\nexecutable = "v"\n'),
        ("[vclient].executable", '[mqtt]\nhost = "b"\n[vclient]\nexecutable = 1\n'),
        ("[vclient].host", '[mqtt]\nhost = "b"\n[vclient]\nexecutable = "v"\nhost = 1\n'),
        ("[read_surface].prefix", MINIMALE + "\n[read_surface]\nprefix = 1\n"),
    ],
)
def test_type_errone_la_ou_une_chaine_est_attendue(ecrire, cle, contenu) -> None:
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(contenu))
    assert cle in str(capture.value)
    assert "chaine" in str(capture.value)


@pytest.mark.parametrize("valeur", ["1", '"true"', "1.0"])
def test_tls_refuse_ce_qui_n_est_pas_un_booleen(ecrire, valeur) -> None:
    with pytest.raises(ConfigurationError, match=r"\[mqtt\].tls doit etre un booleen"):
        load_config(ecrire(f'[mqtt]\nhost = "b"\ntls = {valeur}\n[vclient]\nexecutable = "v"\n'))


@pytest.mark.parametrize(("ecrit", "attendu"), [("5", 5.0), ("7.5", 7.5), ("10", 10.0)])
def test_read_timeout_accepte_entier_et_flottant(ecrire, ecrit, attendu) -> None:
    config = load_config(
        ecrire(f'[mqtt]\nhost = "b"\n[vclient]\nexecutable = "v"\nread_timeout_s = {ecrit}\n')
    )
    assert config.vclient.read_timeout_s == attendu
    assert isinstance(config.vclient.read_timeout_s, float)


@pytest.mark.parametrize("valeur", ["true", "false", '"5"'])
def test_read_timeout_refuse_booleen_et_chaine(ecrire, valeur) -> None:
    with pytest.raises(ConfigurationError, match=r"\[vclient\].read_timeout_s doit etre un nombre"):
        load_config(
            ecrire(f'[mqtt]\nhost = "b"\n[vclient]\nexecutable = "v"\nread_timeout_s = {valeur}\n')
        )


# ---------------------------------------------------------------------------
# Valeurs : les structures existantes restent seules autorites
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("contenu", "attendu"),
    [
        ('[mqtt]\nhost = ""\n[vclient]\nexecutable = "v"\n', "mqtt"),
        ('[mqtt]\nhost = "b"\nport = 70000\n[vclient]\nexecutable = "v"\n', "mqtt"),
        ('[mqtt]\nhost = "b"\nkeepalive = 0\n[vclient]\nexecutable = "v"\n', "mqtt"),
        ('[mqtt]\nhost = "b"\n[vclient]\nexecutable = ""\n', "vclient"),
        (
            '[mqtt]\nhost = "b"\n[vclient]\nexecutable = "v"\nread_timeout_s = 0\n',
            "vclient",
        ),
        (MINIMALE + "\n[read_surface]\nsnapshot_period_s = 0\n", "read_surface"),
        (MINIMALE + "\n[read_surface]\nheartbeat_period_s = -1\n", "read_surface"),
    ],
)
def test_valeur_hors_domaine_refusee_avec_sa_table(ecrire, contenu, attendu) -> None:
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(contenu))
    assert f"[{attendu}]" in str(capture.value)


def test_prefixe_invalide_refuse(ecrire) -> None:
    with pytest.raises(ConfigurationError, match=r"\[read_surface\]"):
        load_config(ecrire(MINIMALE + '\n[read_surface]\nprefix = "boiler+"\n'))


# ---------------------------------------------------------------------------
# Battement
# ---------------------------------------------------------------------------


def test_heartbeat_zero_desactive(ecrire) -> None:
    config = load_config(ecrire(MINIMALE + "\n[read_surface]\nheartbeat_period_s = 0\n"))
    assert config.read_surface.heartbeat_period_s is None
    assert config.read_surface.heartbeat_enabled is False


def test_heartbeat_absent_vaut_trente(ecrire) -> None:
    config = load_config(ecrire(MINIMALE))
    assert config.read_surface.heartbeat_period_s == 30
    assert config.read_surface.heartbeat_enabled is True


def test_heartbeat_positif_conserve(ecrire) -> None:
    config = load_config(ecrire(MINIMALE + "\n[read_surface]\nheartbeat_period_s = 5\n"))
    assert config.read_surface.heartbeat_period_s == 5


def test_heartbeat_false_est_une_erreur_de_type(ecrire) -> None:
    """`False == 0` : une projection avant la validation de type desactiverait.

    Le battement doit rester ACTIF au defaut, et `false` doit etre refuse.
    """
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(MINIMALE + "\n[read_surface]\nheartbeat_period_s = false\n"))
    message = str(capture.value)
    assert "[read_surface].heartbeat_period_s" in message
    assert "entier" in message and "bool" in message


def test_heartbeat_negatif_refuse(ecrire) -> None:
    with pytest.raises(ConfigurationError):
        load_config(ecrire(MINIMALE + "\n[read_surface]\nheartbeat_period_s = -5\n"))


# ---------------------------------------------------------------------------
# Secret
# ---------------------------------------------------------------------------


def test_password_dans_le_toml_est_refuse(ecrire) -> None:
    """Le message doit NOMMER la variable d'environnement a utiliser."""
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire('[mqtt]\nhost = "b"\npassword = "x"\n[vclient]\nexecutable = "v"\n'))
    message = str(capture.value)
    assert "[mqtt].password" in message
    assert PASSWORD_ENV_VAR in message


@pytest.mark.parametrize("cle", ["command_topic", "ack_topic_prefix"])
def test_cles_hors_surface_refusees_nommement(ecrire, cle) -> None:
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(f'[mqtt]\nhost = "b"\n{cle} = "x"\n[vclient]\nexecutable = "v"\n'))
    assert f"[mqtt].{cle}" in str(capture.value)
    assert "interdit" in str(capture.value)


def test_secret_absent_donne_none(ecrire) -> None:
    config = load_config(ecrire(MINIMALE))
    assert config.mqtt.password is None


def test_secret_present_est_utilise(ecrire, monkeypatch) -> None:
    monkeypatch.setenv(PASSWORD_ENV_VAR, "mot-de-passe-de-test")
    config = load_config(ecrire(MINIMALE))
    assert config.mqtt.password == "mot-de-passe-de-test"


def test_secret_jamais_divulgue(ecrire, monkeypatch) -> None:
    """Ni dans les representations, ni dans un message d'erreur."""
    secret = "mot-de-passe-de-test"
    monkeypatch.setenv(PASSWORD_ENV_VAR, secret)
    config = load_config(ecrire(MINIMALE))
    assert secret not in repr(config)
    assert secret not in str(config)
    assert secret not in repr(config.mqtt)

    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire('[mqtt]\nhost = ""\n[vclient]\nexecutable = "v"\n'))
    assert secret not in str(capture.value)


def test_aucune_autre_variable_d_environnement_n_est_lue(ecrire, monkeypatch) -> None:
    """Boilerack lit UNE variable, pas l'environnement du processus."""
    for parasite in ("BOILERACK_MQTT_HOST", "BOILERACK_CONFIG", "MQTT_HOST", "BOILERACK_PORT"):
        monkeypatch.setenv(parasite, "valeur-parasite")
    config = load_config(ecrire(MINIMALE))
    assert config.mqtt.host == "broker.exemple.invalid"
    assert config.mqtt.port == 1883


def test_secret_sans_username_reste_valide(ecrire, monkeypatch) -> None:
    """Caracterisation : l'adaptateur ne transmet le mot de passe que si
    `username` est defini. C10 n'en fait pas une erreur et n'ajoute aucune
    contrainte croisee — le contrat se borne a l'enoncer."""
    monkeypatch.setenv(PASSWORD_ENV_VAR, "mot-de-passe-de-test")
    config = load_config(ecrire(MINIMALE))
    assert config.mqtt.username is None
    assert config.mqtt.password == "mot-de-passe-de-test"

    import inspect

    from boilerack.adapters.mqtt_paho import PahoMqttClient

    source = inspect.getsource(PahoMqttClient._build_client)
    assert "if config.username is not None:" in source


def test_username_seul_reste_valide(ecrire) -> None:
    config = load_config(
        ecrire('[mqtt]\nhost = "b"\nusername = "u"\n[vclient]\nexecutable = "v"\n')
    )
    assert config.mqtt.username == "u"
    assert config.mqtt.password is None


# ---------------------------------------------------------------------------
# Borne dynamique de la surface de lecture
# ---------------------------------------------------------------------------

#: Surface artificielle a borne BASSE. Une implementation codant `90` en dur
#: accepterait 41 a tort.
_SURFACE_BASSE = (
    MeasurementSpec(role="x", read="getX", suffix="telemetry/x", period_s=10, fresh_max_s=40),
)

#: Surface artificielle a borne HAUTE. Une implementation codant `90` en dur
#: refuserait 120 a tort.
_SURFACE_HAUTE = (
    MeasurementSpec(role="y", read="getY", suffix="telemetry/y", period_s=60, fresh_max_s=200),
)


def test_snapshot_hors_borne_v1_refuse_avant_le_runtime(ecrire) -> None:
    with pytest.raises(ConfigurationError) as capture:
        load_config(ecrire(MINIMALE + "\n[read_surface]\nsnapshot_period_s = 91\n"))
    assert "[read_surface].snapshot_period_s" in str(capture.value)


def test_snapshot_a_la_borne_v1_accepte(ecrire) -> None:
    config = load_config(ecrire(MINIMALE + "\n[read_surface]\nsnapshot_period_s = 90\n"))
    assert config.read_surface.snapshot_period_s == 90


def test_l_autorite_est_partagee_avec_le_publieur() -> None:
    """Le chargeur n'a pas sa propre regle : il appelle la meme fonction.

    Verifie sur la source, faute de quoi une copie silencieuse passerait
    inapercue tant que les deux resteraient d'accord.
    """
    import boilerack.config as module_config

    code = _code_sans_docstrings(module_config)
    assert "check_snapshot_period" in code
    assert "fresh_max_s" not in code, "le chargeur ne doit pas recalculer la borne"
    assert "90" not in code, "aucune borne codee en dur"


@pytest.mark.parametrize(
    ("specs", "periode", "accepte"),
    [
        (_SURFACE_BASSE, 40, True),
        (_SURFACE_BASSE, 41, False),
        (_SURFACE_HAUTE, 120, True),
        (_SURFACE_HAUTE, 201, False),
        (V1_MEASUREMENTS, 90, True),
        (V1_MEASUREMENTS, 91, False),
        ((), 10_000, True),
    ],
)
def test_l_autorite_suit_la_surface_et_non_une_constante(specs, periode, accepte) -> None:
    """Preuve anti-duplication, dans les DEUX sens.

    Une borne codee en dur a `90` accepterait 41 sur la surface basse et
    refuserait 120 sur la surface haute : chacun des deux sens la trahit.

    Le test interroge **l'autorite elle-meme**, il ne reproduit pas son calcul.
    """
    if accepte:
        assert check_snapshot_period(specs, periode) is None
    else:
        with pytest.raises(ValueError):
            check_snapshot_period(specs, periode)


def test_surface_vide_ne_borne_rien() -> None:
    """Comportement etabli par C7-C3B, conserve a l'identique par l'extraction."""
    assert check_snapshot_period((), 10_000) is None


def test_la_prevalidation_utilise_les_specs_du_runtime_config() -> None:
    """Une `RuntimeConfig` a surface artificielle est bien evaluee contre elle.

    `specs` n'est pas une cle TOML : le test la fournit programmatiquement, ce
    qui est exactement le point d'injection prevu par le contrat.
    """
    from boilerack.adapters.config import MqttConfig, VclientConfig
    from boilerack.config import _verifier_surface
    from boilerack.read_surface.config import ReadSurfaceConfig

    def config(specs, periode):
        return RuntimeConfig(
            mqtt=MqttConfig(host="b.invalid"),
            vclient=VclientConfig(executable="v"),
            read_surface=ReadSurfaceConfig(snapshot_period_s=periode),
            specs=specs,
        )

    assert _verifier_surface(config(_SURFACE_BASSE, 40)) is None
    with pytest.raises(ConfigurationError, match=r"\[read_surface\].snapshot_period_s"):
        _verifier_surface(config(_SURFACE_BASSE, 41))
    assert _verifier_surface(config(_SURFACE_HAUTE, 120)) is None


# ---------------------------------------------------------------------------
# Frontieres
# ---------------------------------------------------------------------------


def test_le_chargement_n_ouvre_ni_socket_ni_processus(ecrire, monkeypatch) -> None:
    """Validation de saisie, jamais d'infrastructure.

    Le sabotage est pose juste avant l'appel et retire aussitot par
    `monkeypatch`, pour ne pas gener pytest lui-meme.
    """
    chemin = ecrire(MINIMALE)

    def interdit(*args, **kwargs):
        raise AssertionError("entree-sortie d'infrastructure pendant le chargement")

    monkeypatch.setattr(socket, "socket", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)
    monkeypatch.setattr(subprocess, "run", interdit)
    monkeypatch.setattr(subprocess, "Popen", interdit)

    config = load_config(chemin)
    assert config.mqtt.host == "broker.exemple.invalid"


def test_l_executable_n_est_pas_verifie_sur_le_disque(ecrire) -> None:
    """Ce serait une verification d'infrastructure, qui echouerait a tort."""
    config = load_config(
        ecrire('[mqtt]\nhost = "b"\n[vclient]\nexecutable = "/chemin/qui/nexiste/pas"\n')
    )
    assert config.vclient.executable == "/chemin/qui/nexiste/pas"
    assert not os.path.exists(config.vclient.executable)


def test_le_module_ne_lance_jamais_le_runtime() -> None:
    import boilerack.config as module_config

    code = _code_sans_docstrings(module_config)
    for interdit in ("run_lifecycle", "build_runtime", "SignalScope"):
        assert interdit not in code


def _code_sans_docstrings(module) -> str:
    """Source du module prive de ses docstrings.

    Les docstrings mentionnent volontiers ce que le module NE fait PAS ; une
    recherche de sous-chaine sur la source brute confondrait ces mentions
    negatives avec du code.
    """
    import ast
    import inspect

    arbre = ast.parse(inspect.getsource(module))
    for noeud in ast.walk(arbre):
        if isinstance(noeud, (ast.Module, ast.ClassDef, ast.FunctionDef)) and noeud.body:
            premier = noeud.body[0]
            if (
                isinstance(premier, ast.Expr)
                and isinstance(premier.value, ast.Constant)
                and isinstance(premier.value.value, str)
            ):
                noeud.body.pop(0)
    return ast.unparse(arbre)


def test_le_module_ne_lit_qu_une_variable_d_environnement() -> None:
    import boilerack.config as module_config

    code = _code_sans_docstrings(module_config)
    assert code.count("os.environ") == 1
    assert "os.environ.get(PASSWORD_ENV_VAR)" in code
    # « .env » n'est pas testable comme sous-chaine : `os.environ` la contient.
    # Le risque reel est le chargement d'un fichier, couvert par `dotenv`.
    for interdit in ("dotenv", "environ.items", "environ.keys", "environ.copy"):
        assert interdit not in code


def test_aucun_secret_ni_valeur_de_site_dans_le_module() -> None:
    import inspect
    import re

    import boilerack.config as module_config

    source = inspect.getsource(module_config)
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", source)
    for interdit in ("localhost", "192.168", "/home/", "passwd"):
        assert interdit not in source.lower()
