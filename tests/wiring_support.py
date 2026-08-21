"""Doubles hors ligne pour le cablage transactionnel W3.

Tous les tests W3 sont HORS LIGNE et DETERMINISTES : aucun broker, aucun Pi,
aucun `vcontrold`, aucune chaudiere, aucun processus, aucune attente reelle.

POURQUOI DES DOUBLES PROPRES A CE LOT
    `tests/adapters/adapter_support.py` n'est importable que depuis
    `tests/adapters/`, ou pytest insere ce repertoire dans `sys.path`. W3 est un
    lot de cablage runtime, dont la place est a la racine des tests, aux cotes de
    `test_runtime.py` et `test_lifecycle.py`. Ce module suit donc la convention
    deja etablie par `tests/installer_support.py` et `tests/core/support.py`.

    Ces doubles portent en outre deux instrumentations que les doubles existants
    n'ont pas, et dont W3 a besoin :

    - `PahoDouble` capture l'ETAT DE L'ADAPTATEUR AU MOMENT PRECIS de `connect()`,
      seule facon deterministe de prouver « gestionnaire installe AVANT connect »
      sans chronometrie ;
    - `VClientEnregistreur` detecte un RECOUVREMENT d'appels `vclient`, ce qui
      rend la propriete « aucune operation simultanee » falsifiable.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from boilerack.transport.vclient import ReadResult, TransportStatus, WriteResult


@dataclass
class FakeMessageInfo:
    """Reproduit `MQTTMessageInfo` : code retour immediat et `mid`."""

    rc: int
    mid: int


@dataclass
class PahoMessage:
    """Message Paho entrant, tel que l'adaptateur le recoit."""

    topic: str
    payload: bytes
    qos: int = 0
    retain: bool = False
    dup: bool = False


@dataclass
class PahoDouble:
    """Faux client Paho, deterministe, avec journal d'ordre.

    Satisfait la surface `PahoLike` reellement utilisee par `PahoMqttClient`.
    Les rappels sont declenches EXPLICITEMENT par le test : rien n'est
    asynchrone, aucun fil n'est cree, aucun `sleep` n'est employe.
    """

    #: Adaptateur observe. Renseigne par le test pour permettre a `connect()`
    #: d'inspecter l'etat interne AU MOMENT PRECIS de l'appel.
    adaptateur: Any = None
    publish_rc: int = 0

    # -- journaux ------------------------------------------------------------
    #: Ordre d'appel de toutes les operations, pour les preuves de sequence.
    ordre: list = field(default_factory=list)
    subscriptions: list = field(default_factory=list)
    published: list = field(default_factory=list)
    connected_args: tuple | None = None
    loop_started: int = 0
    loop_stopped: int = 0
    disconnected: int = 0
    #: Etat capture a l'instant du `connect()`.
    handler_present_au_connect: bool | None = None
    souscriptions_au_connect: tuple = ()

    next_mid: int = 1

    # -- rappels cables par l'adaptateur -------------------------------------
    on_connect: Any = None
    on_disconnect: Any = None
    on_publish: Any = None
    on_message: Any = None

    # -- surface PahoLike ----------------------------------------------------

    def connect(self, host, port, keepalive):
        self.connected_args = (host, port, keepalive)
        if self.adaptateur is not None:
            # Preuve d'ordre : le gestionnaire etait-il DEJA enregistre ?
            self.handler_present_au_connect = self.adaptateur._handler is not None
        self.souscriptions_au_connect = tuple(self.subscriptions)
        self.ordre.append(("connect", host, port))

    def disconnect(self):
        self.disconnected += 1
        self.ordre.append(("disconnect",))

    def loop_start(self):
        self.loop_started += 1
        self.ordre.append(("loop_start",))

    def loop_stop(self):
        self.loop_stopped += 1
        self.ordre.append(("loop_stop",))

    def subscribe(self, topic, qos=0):
        self.subscriptions.append((topic, qos))
        self.ordre.append(("subscribe", topic, qos))

    def will_set(self, topic, payload=None, qos=0, retain=False):
        self.ordre.append(("will_set", topic))

    def will_clear(self):
        self.ordre.append(("will_clear",))

    def publish(self, topic, payload, qos=0, retain=False):
        mid = self.next_mid
        self.next_mid += 1
        self.published.append(
            {"topic": topic, "payload": payload, "qos": qos, "retain": retain, "mid": mid}
        )
        self.ordre.append(("publish", topic))
        return FakeMessageInfo(rc=self.publish_rc, mid=mid)

    # -- declencheurs, cote test ---------------------------------------------

    def fire_on_connect(self, *, success: bool = True) -> None:
        self.on_connect(self, None, {}, 0 if success else 1, None)

    def fire_on_disconnect(self, *, reason: int = 0) -> None:
        self.on_disconnect(self, None, None, reason, None)

    def fire_on_message(self, message: PahoMessage) -> None:
        self.on_message(self, None, message)

    # -- inspection ----------------------------------------------------------

    @property
    def topics_publies(self) -> tuple:
        return tuple(p["topic"] for p in self.published)


class OperationVClientSimultanee(AssertionError):
    """Levee si deux operations `vclient` se recouvrent."""


class VClientEnregistreur:
    """`VClient` de test qui enregistre l'ordre ET detecte tout recouvrement.

    Sert simultanement de `MeasurementReader` pour la surface de lecture et de
    `VClient` pour le coeur : c'est precisement ce partage qui rend observable
    la clause W2 §15.2, « deux operations `vclient` ne sont jamais simultanees ».

    Les valeurs rendues sont programmees par commande. Une commande inconnue
    rend un `ReadResult` non `OK`, ce qui ne confirme rien — jamais une valeur
    par defaut silencieuse.
    """

    def __init__(self, lectures: dict | None = None) -> None:
        self._lectures: dict = dict(lectures or {})
        self.appels: list = []
        self._en_cours = False
        self.recouvrements = 0
        #: Rappel optionnel, invoque PENDANT une operation. Sert a injecter une
        #: tentative concurrente au moment exact ou l'operation est en cours.
        self.pendant: Any = None

    # -- programmation --------------------------------------------------------

    def programmer_lecture(self, command: str, value: float) -> None:
        self._lectures[command] = value

    # -- protocole VClient / MeasurementReader --------------------------------

    def _entrer(self, quoi: str, command: str, value=None):
        if self._en_cours:
            self.recouvrements += 1
            raise OperationVClientSimultanee(
                f"operation vclient simultanee : {quoi} {command}"
            )
        self._en_cours = True
        self.appels.append((quoi, command, value))
        if self.pendant is not None:
            self.pendant(quoi, command, value)

    def read(self, command: str) -> ReadResult:
        self._entrer("read", command)
        try:
            if command in self._lectures:
                return ReadResult(status=TransportStatus.OK, value=self._lectures[command])
            return ReadResult(status=TransportStatus.UNUSABLE_OUTPUT, value=None)
        finally:
            self._en_cours = False

    def write(self, command: str, value: float) -> WriteResult:
        self._entrer("write", command, value)
        try:
            return WriteResult(status=TransportStatus.OK)
        finally:
            self._en_cours = False

    # -- inspection ----------------------------------------------------------

    @property
    def ecritures(self) -> tuple:
        return tuple(a for a in self.appels if a[0] == "write")

    @property
    def lectures(self) -> tuple:
        return tuple(a for a in self.appels if a[0] == "read")


class StopApres:
    """`StopSignal` qui demande l'arret apres `n` consultations effectives.

    Deterministe et sans horloge : la boucle du runner consulte `is_set()` a des
    points fixes, ce compteur les suit donc exactement.
    """

    def __init__(self, n: int) -> None:
        self._restant = n
        self.consultations = 0

    def is_set(self) -> bool:
        self.consultations += 1
        if self._restant <= 0:
            return True
        self._restant -= 1
        return False


class StopArme:
    """`StopSignal` que le test arme explicitement, a l'instant qu'il choisit."""

    def __init__(self, arme: bool = False) -> None:
        self.arme = arme
        self.consultations = 0

    def is_set(self) -> bool:
        self.consultations += 1
        return self.arme


def sans_bloquer(action, *, delai: float = 5.0):
    """Execute `action` sur un fil daemon et AFFIRME qu'elle rend la main.

    Sert partout ou une operation DOIT etre non bloquante — un depot sature, un
    rappel Paho. Une implementation bloquante fait alors ECHOUER le test au lieu
    de le geler : une suite qui pend ne prouve rien et immobiliserait
    l'integration continue. `daemon=True` : sous une implementation fautive, le
    fil ne se termine jamais et ne doit pas retenir l'interpreteur a la sortie.
    """
    issue: dict = {}

    def cible() -> None:
        try:
            issue["valeur"] = action()
        except BaseException as exc:  # repropagee telle quelle ci-dessous
            issue["exception"] = exc

    fil = threading.Thread(target=cible, daemon=True)
    fil.start()
    fil.join(timeout=delai)
    if "exception" in issue:
        # L'erreur reelle doit remonter a l'appelant, sans etre maquillee en
        # « operation bloquante » : les deux defauts sont distincts.
        raise issue["exception"]
    assert "valeur" in issue, "operation bloquante : aucune main rendue dans le delai"
    return issue["valeur"]
