"""Frontiere de publication / souscription MQTT.

Definit la FRONTIERE dont le futur coeur aura besoin, sans dependre de Paho, ni
ouvrir de session MQTT reelle, ni faire de reseau, ni serialiser des ACK.

Le payload est traite comme des octets bruts : le transport n'interprete jamais
le contenu (la serialisation metier appartiendra au coeur, en C3).

Une publication est modelisee en deux temps distincts : DEMANDEE (l'appel
`publish` a rendu un `PublishHandle`) puis, separement, CONFIRMEE ou ECHOUEE.
Cela permettra plus tard de distinguer « envoye » de « accuse ».
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


class NotConnectedError(Exception):
    """Levee si l'on publie ou souscrit sans connexion active."""


@dataclass(frozen=True)
class Publication:
    """Description immuable d'une publication demandee."""

    topic: str
    payload: bytes
    qos: int
    retain: bool


@dataclass(frozen=True)
class Subscription:
    """Souscription demandee."""

    topic: str
    qos: int


@dataclass(frozen=True)
class Message:
    """Message entrant.

    `dup` reflete le drapeau MQTT « duplicate delivery ». Le coeur devra le
    prendre en compte pour la deduplication en C3 ; ici, on se contente de le
    representer fidelement.
    """

    topic: str
    payload: bytes
    qos: int = 0
    retain: bool = False
    dup: bool = False


class PublishHandle:
    """Suivi d'une publication : demandee, puis confirmee ou echouee.

    Renvoye par `publish`. Son etat evolue une seule fois : de « demandee »
    (`confirmed` et `failed` a False) vers « confirmee » OU « echouee ». Les
    deux ne peuvent pas etre vrais en meme temps.
    """

    def __init__(self, publication: Publication) -> None:
        self._publication = publication
        self._confirmed = False
        self._failed = False

    @property
    def publication(self) -> Publication:
        return self._publication

    @property
    def confirmed(self) -> bool:
        return self._confirmed

    @property
    def failed(self) -> bool:
        return self._failed

    def _mark_confirmed(self) -> None:
        if self._failed:
            raise RuntimeError("publication deja marquee en echec")
        self._confirmed = True

    def _mark_failed(self) -> None:
        if self._confirmed:
            raise RuntimeError("publication deja confirmee")
        self._failed = True


@runtime_checkable
class MqttClient(Protocol):
    """Frontiere MQTT minimale, sans politique.

    Definit ce que le coeur pourra faire ; ne dit rien de COMMENT (reconnexion,
    retry, session persistante) : ce sont des decisions ulterieures.
    """

    def connect(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def subscribe(self, topic: str, qos: int = 0) -> None:
        ...

    def publish(
        self, topic: str, payload: bytes, qos: int = 0, retain: bool = False
    ) -> PublishHandle:
        ...
