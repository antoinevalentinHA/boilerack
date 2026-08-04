"""Frontiere de publication / souscription MQTT.

Definit la FRONTIERE dont le futur coeur aura besoin, sans dependre de Paho, ni
ouvrir de session MQTT reelle, ni faire de reseau, ni serialiser des ACK.

Le payload est traite comme des octets bruts : le transport n'interprete jamais
le contenu (la serialisation metier appartiendra au coeur, en C3).

Une publication est modelisee en deux temps distincts : DEMANDEE (l'appel
`publish` a rendu un `PublishHandle`) puis, separement, CONFIRMEE ou ECHOUEE.
Cela permettra plus tard de distinguer « envoye » de « accuse ».

Le TESTAMENT (`MqttWill`) est porte par `connect`, et non par un reglage
separe : en MQTT, le testament est un CHAMP DU PAQUET CONNECT. Le lier a la
connexion supprime tout piege d'ordre — un testament pose apres la connexion
serait silencieusement sans effet.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Final, Protocol, runtime_checkable

MessageHandler = Callable[["Message"], None]
"""Rappel invoque pour chaque `Message` entrant remis par le transport."""

#: Jokers MQTT : un topic de PUBLICATION ne peut pas en porter.
_WILDCARDS: Final = ("+", "#")

#: Caracteres de controle Unicode, categorie `Cc`.
_CONTROL_CHARS: Final = re.compile(r"[\x00-\x1f\x7f-\x9f]")


class NotConnectedError(Exception):
    """Levee si l'on publie ou souscrit sans connexion active."""


@dataclass(frozen=True)
class MqttWill:
    """Testament MQTT : message publie par le BROKER si le client disparait.

    Valide a la construction, parce que la frontiere ne doit pas deleguer sa
    propre validite a l'adaptateur : un testament mal forme ne doit jamais
    atteindre une connexion.

    ATTENTION, propriete du protocole MQTT, pas de ce projet : le testament
    n'est PAS emis lorsque le client se deconnecte proprement. Un producteur
    qui doit annoncer son depart doit donc publier explicitement avant de se
    deconnecter ; le testament ne couvre que la disparition inattendue.
    """

    topic: str
    payload: bytes
    qos: int
    retain: bool

    def __post_init__(self) -> None:
        if not isinstance(self.topic, str) or self.topic == "":
            raise ValueError(f"topic doit etre une chaine non vide : {self.topic!r}")
        for wildcard in _WILDCARDS:
            if wildcard in self.topic:
                raise ValueError(
                    f"le topic d'un testament ne doit pas contenir le joker "
                    f"MQTT {wildcard!r}"
                )
        if _CONTROL_CHARS.search(self.topic):
            raise ValueError("le topic d'un testament contient un caractere de controle")
        if not isinstance(self.payload, bytes):
            raise ValueError(
                f"payload doit etre des octets, recu {type(self.payload).__name__}"
            )
        if isinstance(self.qos, bool) or not isinstance(self.qos, int):
            raise ValueError(f"qos doit etre un entier : {self.qos!r}")
        if self.qos not in (0, 1, 2):
            raise ValueError(f"qos doit valoir 0, 1 ou 2 : {self.qos!r}")
        if not isinstance(self.retain, bool):
            raise ValueError(
                f"retain doit etre un booleen, recu {type(self.retain).__name__}"
            )


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

    La voie d'ENTREE est reduite au strict minimum : `set_message_handler`
    enregistre un rappel que le transport appellera pour chaque `Message`
    entrant (topic, payload brut, QoS, `dup`). Cela n'introduit ni Paho ni
    session complete : c'est la seule couture dont le coeur a besoin pour
    recevoir des commandes.

    LIMITE DE `runtime_checkable` : `isinstance` ne verifie QUE la presence des
    methodes, jamais leurs signatures. Une implementation dont `connect`
    ignorerait le testament satisferait donc encore `isinstance(..., MqttClient)`.
    La conformite reelle au testament doit etre etablie par un test de
    COMPORTEMENT, jamais par cette seule verification.
    """

    def connect(self, will: MqttWill | None = None) -> None:
        """Ouvre la connexion, en posant `will` comme testament de la session.

        `will` est OPTIONNEL pour ne pas casser les consommateurs
        transactionnels existants, qui n'en posent aucun. Cette optionalite ne
        vaut PAS permission : un producteur soumis a une exigence de testament
        doit toujours en fournir un.

        `will=None` signifie « aucun testament pour cette connexion », et non
        « conserver le precedent » : une implementation doit effacer un
        testament anterieur.
        """
        ...

    def disconnect(self) -> None:
        ...

    def subscribe(self, topic: str, qos: int = 0) -> None:
        ...

    def publish(
        self, topic: str, payload: bytes, qos: int = 0, retain: bool = False
    ) -> PublishHandle:
        ...

    def set_message_handler(self, handler: MessageHandler) -> None:
        ...
