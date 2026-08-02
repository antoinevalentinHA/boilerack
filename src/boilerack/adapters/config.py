"""Modeles de configuration technique des adaptateurs reels (C4).

Objets IMMUABLES et MINIMAUX, valides a la construction. Ils decrivent la
surface de configuration dont les adaptateurs ont besoin ; ils ne chargent
RIEN (pas de YAML, TOML ni variables d'environnement en C4) et ne contiennent
aucun secret.

`MqttConfig` ne divulgue jamais le mot de passe : sa representation le masque,
afin qu'un `repr()` ou un log accidentel ne le fasse pas fuir.

`VclientConfig` porte les champs de configuration du futur adaptateur `vclient`.
Il ne definit AUCUN format de commande ni cartographie de sortie : l'adaptateur
`vclient` concret reste bloque tant que son contrat reel n'est pas caracterise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

_MIN_PORT = 1
_MAX_PORT = 65535


def _check_port(port: int, field: str) -> None:
    if not isinstance(port, int) or isinstance(port, bool):
        raise ValueError(f"{field} doit etre un entier : {port!r}")
    if not (_MIN_PORT <= port <= _MAX_PORT):
        raise ValueError(f"{field} hors plage 1..65535 : {port!r}")


def _check_positive_finite(value: float, field: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field} doit etre numerique : {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"{field} doit etre fini : {value!r}")
    if value <= 0:
        raise ValueError(f"{field} doit etre strictement positif : {value!r}")


def _check_non_empty(value: str, field: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(f"{field} doit etre une chaine non vide : {value!r}")


@dataclass(frozen=True, repr=False)
class MqttConfig:
    """Configuration minimale de l'adaptateur MQTT.

    Le mot de passe, s'il est fourni, n'est JAMAIS inclus dans `repr()`.
    Aucun secret ne doit etre code en dur dans le depot : `username` et
    `password` restent optionnels et fournis par l'appelant.
    """

    host: str
    port: int = 1883
    client_id: str = "boilerack"
    keepalive: int = 60
    username: str | None = None
    password: str | None = None
    tls: bool = False
    command_topic: str = "boilerack/command"
    ack_topic_prefix: str = "boilerack/ack"

    def __post_init__(self) -> None:
        _check_non_empty(self.host, "host")
        _check_port(self.port, "port")
        _check_non_empty(self.client_id, "client_id")
        if not isinstance(self.keepalive, int) or isinstance(self.keepalive, bool):
            raise ValueError(f"keepalive doit etre un entier : {self.keepalive!r}")
        if self.keepalive <= 0:
            raise ValueError(f"keepalive doit etre strictement positif : {self.keepalive!r}")
        _check_non_empty(self.command_topic, "command_topic")
        _check_non_empty(self.ack_topic_prefix, "ack_topic_prefix")

    def __repr__(self) -> str:
        # Masque explicitement le mot de passe : seule sa PRESENCE est exposee,
        # jamais sa valeur.
        secret = "***" if self.password is not None else None
        return (
            f"MqttConfig(host={self.host!r}, port={self.port!r}, "
            f"client_id={self.client_id!r}, keepalive={self.keepalive!r}, "
            f"username={self.username!r}, password={secret!r}, tls={self.tls!r}, "
            f"command_topic={self.command_topic!r}, "
            f"ack_topic_prefix={self.ack_topic_prefix!r})"
        )


@dataclass(frozen=True)
class VclientConfig:
    """Configuration minimale du futur adaptateur `vclient`.

    Porte uniquement des champs de configuration (chemin de l'executable, hote
    et port optionnels du demon, budgets de temps). Ne definit AUCUNE commande
    ni traduction de sortie : cela releve du contrat reel de `vclient`, non
    encore caracterise (voir docs/design/c4-real-adapters.md).
    """

    executable: str
    host: str | None = None
    port: int | None = None
    read_timeout_s: float = 5.0
    write_timeout_s: float = 5.0

    def __post_init__(self) -> None:
        _check_non_empty(self.executable, "executable")
        if self.host is not None:
            _check_non_empty(self.host, "host")
        if self.port is not None:
            _check_port(self.port, "port")
        _check_positive_finite(self.read_timeout_s, "read_timeout_s")
        _check_positive_finite(self.write_timeout_s, "write_timeout_s")
