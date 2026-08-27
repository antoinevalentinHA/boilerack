"""Chargement et validation de la configuration utilisateur (lot C10).

Traduit un fichier TOML et une variable d'environnement en un `RuntimeConfig`
pret a etre execute, ou refuse en nommant la faute. Implemente le contrat
`docs/design/c10-user-interface.md`.

DEUX SOURCES DISJOINTES
    Le fichier porte **toute** la configuration durable ; l'environnement porte
    **le seul secret**, et rien d'autre. Il n'y a donc aucune precedence a
    arbitrer : une cle ne peut pas venir des deux endroits. Boilerack ne balaie
    pas l'environnement, n'y refuse aucune variable inconnue, et ne lit aucun
    fichier `.env` : l'environnement du processus ne lui appartient pas.

SCHEMA FERME
    Trois tables, treize cles, et rien d'autre. Toute table ou cle inconnue est
    refusee. Cette strictesse est legitime parce que Boilerack possede
    integralement son schema : elle transforme une faute de frappe silencieuse,
    qui laisserait un reglage sans effet, en une erreur immediate et nommee.

TYPES TOML, PAS TYPES PYTHON
    TOML distingue nativement entier, flottant, booleen et chaine. Les
    verifications portent donc sur le type **exact** : `type(v) is int`, et non
    `isinstance`, parce que `bool` est une sous-classe de `int` en Python et que
    `False == 0` est vrai. Sans cette rigueur, `port = true` passerait pour un
    entier et `heartbeat_period_s = false` desactiverait silencieusement le
    battement.

AUCUNE ENTREE-SORTIE D'INFRASTRUCTURE
    Ce module lit un fichier et une variable d'environnement. Il n'ouvre aucune
    socket, ne resout aucun nom d'hote, ne lance aucun processus et ne verifie
    pas l'existence de l'executable `vclient` : ce sont des verifications
    d'infrastructure, et elles echoueraient pour de mauvaises raisons. Il ne
    lance jamais le runtime.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any, Callable, Final, Mapping, TypeVar

from boilerack.adapters.config import MqttConfig, VclientConfig
from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.measurements import check_snapshot_period
from boilerack.runtime import RuntimeConfig, TransactionSurfaceConfig

__all__ = ["ConfigurationError", "PASSWORD_ENV_VAR", "load_config"]

#: Unique variable d'environnement lue par Boilerack. Le prefixe reprend le nom
#: de distribution, ce qui evite toute collision sur une machine partagee ; le
#: segment intermediaire nomme le sous-systeme. Nom PUBLIC : il ne changera plus.
PASSWORD_ENV_VAR: Final = "BOILERACK_MQTT_PASSWORD"

#: Les quatre tables du schema, et aucune autre.
_TABLES: Final = ("mqtt", "vclient", "read_surface", "transaction_surface")

#: Les quatorze cles publiques, par table.
_CLES_MQTT: Final = ("host", "port", "client_id", "keepalive", "username", "tls")
_CLES_VCLIENT: Final = ("executable", "host", "port", "read_timeout_s")
_CLES_READ_SURFACE: Final = ("prefix", "snapshot_period_s", "heartbeat_period_s")
_CLES_TRANSACTION_SURFACE: Final = ("enabled",)

#: Cles refusees NOMMEMENT dans `[mqtt]`, avec leur motif. Un message dedie vaut
#: mieux qu'un « cle inconnue » generique : celui qui les ecrit a une intention
#: precise et merite d'apprendre pourquoi elle est refusee.
_REFUS_MQTT: Final = {
    "password": (
        f"le mot de passe ne se met jamais dans un fichier ; utilisez la "
        f"variable d'environnement {PASSWORD_ENV_VAR}"
    ),
    "command_topic": "hors surface utilisateur : cette cle n'est pas configurable",
    "ack_topic_prefix": "hors surface utilisateur : cette cle n'est pas configurable",
}

#: Valeur entiere signifiant « battement desactive ». TOML n'a pas de valeur
#: nulle ; il faut donc une convention, et celle-ci est sans ambiguite : zero
#: seconde n'a aucune interpretation utile comme periode.
_HEARTBEAT_DESACTIVE: Final = 0


class ConfigurationError(Exception):
    """Faute de l'utilisateur dans sa configuration, jamais une panne.

    Une seule categorie, sans hierarchie : le point d'entree est son unique
    consommateur, et il n'a qu'une decision a prendre — presenter un message
    lisible et rendre le code d'usage.

    Elle est levee par ce module uniquement, et ne doit jamais etre employee
    pour envelopper une exception survenue APRES le demarrage du runtime.
    """


# ---------------------------------------------------------------------------
# Verificateurs de type — types TOML, pas types Python
# ---------------------------------------------------------------------------


def _ou(table: str, cle: str) -> str:
    return f"[{table}].{cle}"


def _exiger_str(table: str, cle: str, valeur: Any) -> str:
    if type(valeur) is not str:
        raise ConfigurationError(
            f"{_ou(table, cle)} doit etre une chaine, pas {type(valeur).__name__}"
        )
    return valeur


def _exiger_int(table: str, cle: str, valeur: Any) -> int:
    """Refuse le booleen : `isinstance(True, int)` vaut `True` en Python."""
    if type(valeur) is not int:
        raise ConfigurationError(
            f"{_ou(table, cle)} doit etre un entier, pas {type(valeur).__name__}"
        )
    return valeur


def _exiger_bool(table: str, cle: str, valeur: Any) -> bool:
    if type(valeur) is not bool:
        raise ConfigurationError(
            f"{_ou(table, cle)} doit etre un booleen, pas {type(valeur).__name__}"
        )
    return valeur


def _exiger_nombre(table: str, cle: str, valeur: Any) -> float:
    """Accepte un entier ou un flottant TOML, refuse le booleen.

    Ecrire `10` pour une duree ronde est naturel ; TOML distingue les deux types
    a la lecture, donc la tolerance ne cree aucune ambiguite.
    """
    if type(valeur) is int or type(valeur) is float:
        return float(valeur)
    raise ConfigurationError(
        f"{_ou(table, cle)} doit etre un nombre, pas {type(valeur).__name__}"
    )


# ---------------------------------------------------------------------------
# Lecture du fichier et controle du schema
# ---------------------------------------------------------------------------


def _lire_toml(chemin: Path) -> Mapping[str, Any]:
    try:
        with chemin.open("rb") as fichier:
            return tomllib.load(fichier)
    except FileNotFoundError:
        raise ConfigurationError(f"fichier introuvable : {chemin}") from None
    except IsADirectoryError:
        raise ConfigurationError(f"n'est pas un fichier : {chemin}") from None
    except PermissionError:
        raise ConfigurationError(f"fichier illisible : {chemin}") from None
    except tomllib.TOMLDecodeError as erreur:
        raise ConfigurationError(f"TOML invalide dans {chemin} : {erreur}") from None
    except OSError as erreur:
        raise ConfigurationError(f"lecture impossible de {chemin} : {erreur}") from None


def _table(document: Mapping[str, Any], nom: str) -> Mapping[str, Any]:
    """Rend la table demandee, ou une table vide si elle est absente."""
    valeur = document.get(nom, {})
    if not isinstance(valeur, dict):
        raise ConfigurationError(f"[{nom}] doit etre une table")
    return valeur


def _verifier_tables(document: Mapping[str, Any]) -> None:
    inconnues = sorted(set(document) - set(_TABLES))
    if inconnues:
        raise ConfigurationError(
            f"table inconnue : {', '.join('[' + n + ']' for n in inconnues)}"
        )


def _verifier_cles(table: str, contenu: Mapping[str, Any], connues: tuple[str, ...]) -> None:
    for cle in sorted(contenu):
        motif = _REFUS_MQTT.get(cle) if table == "mqtt" else None
        if motif is not None:
            raise ConfigurationError(f"{_ou(table, cle)} est interdit : {motif}")
        if cle not in connues:
            raise ConfigurationError(f"cle inconnue : {_ou(table, cle)}")


def _exiger_presence(table: str, contenu: Mapping[str, Any], cle: str) -> None:
    if cle not in contenu:
        raise ConfigurationError(f"{_ou(table, cle)} est obligatoire")


# ---------------------------------------------------------------------------
# Construction des structures existantes
# ---------------------------------------------------------------------------


#: Le type rendu par la fabrique passee a `_construire`. Sans lui, la fonction
#: rendrait `Any`, et chaque appelant declarant un type concret le dissimulerait.
_T = TypeVar("_T")


def _construire(
    table: str, fabrique: Callable[..., _T], arguments: dict[str, Any]
) -> _T:
    """Delegue la validation des valeurs aux structures existantes.

    Leurs `__post_init__` restent **seules autorites** des plages, des chaines
    non vides et du format de prefixe : les revalider ici dupliquerait des
    regles et les ferait diverger. Seul le contexte de table est ajoute ; le
    message d'origine nomme deja le champ fautif.
    """
    try:
        return fabrique(**arguments)
    except ValueError as erreur:
        raise ConfigurationError(f"[{table}] : {erreur}") from None


def _lire_secret() -> str | None:
    """Lit l'unique variable d'environnement, une seule fois.

    Absente : aucun mot de passe. Presente : sa valeur, telle quelle, sans
    interpretation ni decodage. Elle n'est ni journalisee, ni incluse dans un
    message : le masquage de `MqttConfig.__repr__` reste la seule representation
    possible du champ.
    """
    return os.environ.get(PASSWORD_ENV_VAR)


def _mqtt(contenu: Mapping[str, Any]) -> MqttConfig:
    _verifier_cles("mqtt", contenu, _CLES_MQTT)
    _exiger_presence("mqtt", contenu, "host")

    arguments: dict[str, Any] = {"host": _exiger_str("mqtt", "host", contenu["host"])}
    # Seules les cles PRESENTES sont transmises : les absentes laissent jouer le
    # defaut de la structure, qui reste l'unique endroit ou il est ecrit.
    if "port" in contenu:
        arguments["port"] = _exiger_int("mqtt", "port", contenu["port"])
    if "client_id" in contenu:
        arguments["client_id"] = _exiger_str("mqtt", "client_id", contenu["client_id"])
    if "keepalive" in contenu:
        arguments["keepalive"] = _exiger_int("mqtt", "keepalive", contenu["keepalive"])
    if "username" in contenu:
        arguments["username"] = _exiger_str("mqtt", "username", contenu["username"])
    if "tls" in contenu:
        arguments["tls"] = _exiger_bool("mqtt", "tls", contenu["tls"])
    arguments["password"] = _lire_secret()

    return _construire("mqtt", MqttConfig, arguments)


def _vclient(contenu: Mapping[str, Any]) -> VclientConfig:
    _verifier_cles("vclient", contenu, _CLES_VCLIENT)
    _exiger_presence("vclient", contenu, "executable")

    arguments: dict[str, Any] = {
        "executable": _exiger_str("vclient", "executable", contenu["executable"])
    }
    if "host" in contenu:
        arguments["host"] = _exiger_str("vclient", "host", contenu["host"])
    if "port" in contenu:
        arguments["port"] = _exiger_int("vclient", "port", contenu["port"])
    if "read_timeout_s" in contenu:
        arguments["read_timeout_s"] = _exiger_nombre(
            "vclient", "read_timeout_s", contenu["read_timeout_s"]
        )

    return _construire("vclient", VclientConfig, arguments)


def _read_surface(contenu: Mapping[str, Any]) -> ReadSurfaceConfig:
    _verifier_cles("read_surface", contenu, _CLES_READ_SURFACE)

    arguments: dict[str, Any] = {}
    if "prefix" in contenu:
        arguments["prefix"] = _exiger_str("read_surface", "prefix", contenu["prefix"])
    if "snapshot_period_s" in contenu:
        arguments["snapshot_period_s"] = _exiger_int(
            "read_surface", "snapshot_period_s", contenu["snapshot_period_s"]
        )
    if "heartbeat_period_s" in contenu:
        # ORDRE IMPERATIF : le type d'abord, la valeur ensuite. Comparer a zero
        # avant de verifier le type accepterait `false`, puisque `False == 0`,
        # et desactiverait le battement sans que l'utilisateur l'ait demande.
        periode = _exiger_int(
            "read_surface", "heartbeat_period_s", contenu["heartbeat_period_s"]
        )
        arguments["heartbeat_period_s"] = (
            None if periode == _HEARTBEAT_DESACTIVE else periode
        )

    try:
        return ReadSurfaceConfig(**arguments)
    except ValueError as erreur:
        raise ConfigurationError(f"[read_surface] : {erreur}") from None


# ---------------------------------------------------------------------------
# Point d'entree du module
# ---------------------------------------------------------------------------


def _transaction_surface(contenu: Mapping[str, Any]) -> TransactionSurfaceConfig:
    """Autorite d'activation (W4-E1 §7.2, §14). FERMEE par defaut.

    Trois absences valent fermeture, et aucune ne produit d'erreur : table
    absente, table vide, cle absente. Un fichier ecrit avant ce lot reste donc
    valide, et reste ferme.

    Aucune coercition : `_exiger_bool` refuse `"true"`, `1` et `0` comme il
    refuse le reste. Une autorite d'ecriture ne s'accorde pas par inadvertance
    de typage.
    """
    _verifier_cles("transaction_surface", contenu, _CLES_TRANSACTION_SURFACE)

    arguments: dict[str, Any] = {}
    if "enabled" in contenu:
        arguments["enabled"] = _exiger_bool(
            "transaction_surface", "enabled", contenu["enabled"]
        )
    return _construire("transaction_surface", TransactionSurfaceConfig, arguments)


def load_config(chemin: str | os.PathLike[str]) -> RuntimeConfig:
    """Lit, valide et assemble la configuration. Ne lance jamais le runtime.

    Sequence, entierement anterieure a tout demarrage :

        lecture du fichier -> tables connues -> cles connues -> types exacts
        -> cles obligatoires -> valeurs (structures existantes) -> secret
        -> RuntimeConfig -> borne dynamique de la surface de lecture

    Toute faute rencontree leve `ConfigurationError`, en nommant la table et la
    cle. Aucune autre exception n'est prevue ; celles des structures existantes
    sont enveloppees la ou la cle concernee est connue.
    """
    chemin = Path(chemin)
    document = _lire_toml(chemin)
    _verifier_tables(document)

    config = RuntimeConfig(
        mqtt=_mqtt(_table(document, "mqtt")),
        vclient=_vclient(_table(document, "vclient")),
        read_surface=_read_surface(_table(document, "read_surface")),
        transaction_surface=_transaction_surface(
            _table(document, "transaction_surface")
        ),
    )
    _verifier_surface(config)
    return config


def _verifier_surface(config: RuntimeConfig) -> None:
    """Borne dynamique de §7.4, AVANT toute construction de runtime.

    La regle n'est pas recopiee ici : elle est demandee a
    `check_snapshot_period`, la meme autorite que celle appliquee par le
    publieur. Sans cela, une valeur hors borne ne serait refusee qu'a la
    construction du runtime, sous forme de panne, alors que c'est une faute de
    saisie.
    """
    try:
        check_snapshot_period(config.specs, config.read_surface.snapshot_period_s)
    except ValueError as erreur:
        raise ConfigurationError(
            f"{_ou('read_surface', 'snapshot_period_s')} : {erreur}"
        ) from None
