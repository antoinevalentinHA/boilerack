"""Double du transport MQTT.

Implemente la frontiere `boilerack.transport.mqtt.MqttClient` en memoire, sans
Paho, sans broker et sans reseau. Il enregistre fidelement ce qui a ete demande
et permet au test de piloter les issues.

Enregistre, dans l'ordre :

- les publications (topic, payload brut, QoS, retain), avec leur etat
  demandee / confirmee / echouee ;
- les souscriptions demandees ;
- les evenements de connexion et de deconnexion ;
- le testament pose lors du dernier `connect()` (`connected_will`).

Pilotage par le test :

- `program_publish_failure()` fait echouer les prochaines publications ;
- `confirm_pending()` confirme les publications demandees encore en attente ;
- `deliver()` injecte un message entrant (avec drapeau `dup` eventuel) ;
- `fire_connected()` / `fire_disconnected()` declenchent une transition du
  cycle de connexion (C11).

Ce double ne SIMULE PAS Paho : il expose la meme semantique de capacite — un
booleen d'etat resultant — et rien de son mecanisme. Aucune transition n'est
declenchee automatiquement par `connect()` ou `disconnect()` : c'est le test qui
les choisit, faute de quoi les scenarios deviendraient ambigus.
"""

from __future__ import annotations

from typing import Callable

from boilerack.transport.mqtt import (
    Message,
    MqttWill,
    NotConnectedError,
    Publication,
    PublishHandle,
    Subscription,
)


class FakeMqttClient:
    """Client MQTT factice conforme au protocole `MqttClient`."""

    def __init__(self) -> None:
        self._connected = False
        self._publications: list[PublishHandle] = []
        self._subscriptions: list[Subscription] = []
        self._connection_events: list[str] = []
        self._inbox: list[Message] = []
        self._pending_failures = 0
        self._connected_will: MqttWill | None = None
        self._on_message: Callable[[Message], None] | None = None
        self._on_connection: Callable[[bool], None] | None = None

    # ------------------------------------------------------------------
    # Protocole MqttClient
    # ------------------------------------------------------------------

    def connect(self, will: MqttWill | None = None) -> None:
        """Enregistre le testament de la connexion courante.

        `will=None` EFFACE un testament precedemment enregistre : c'est la
        semantique de la frontiere, « aucun testament pour cette connexion ».

        Aucune emission automatique n'est simulee : un double de connexion
        n'invente pas une deconnexion brutale que le test n'a pas demandee.
        """
        self._connected = True
        self._connected_will = will
        self._connection_events.append("connect")

    def disconnect(self) -> None:
        self._connected = False
        self._connection_events.append("disconnect")

    def subscribe(self, topic: str, qos: int = 0) -> None:
        if not self._connected:
            raise NotConnectedError("souscription impossible : client non connecte")
        self._subscriptions.append(Subscription(topic=topic, qos=qos))

    def publish(
        self, topic: str, payload: bytes, qos: int = 0, retain: bool = False
    ) -> PublishHandle:
        if not self._connected:
            raise NotConnectedError("publication impossible : client non connecte")
        handle = PublishHandle(
            Publication(topic=topic, payload=payload, qos=qos, retain=retain)
        )
        if self._pending_failures > 0:
            self._pending_failures -= 1
            handle._mark_failed()
        self._publications.append(handle)
        return handle

    # ------------------------------------------------------------------
    # Pilotage par le test
    # ------------------------------------------------------------------

    def program_publish_failure(self, count: int = 1) -> None:
        """Fait echouer les `count` prochaines publications (des la demande)."""
        if count < 1:
            raise ValueError(f"count doit valoir au moins 1 : {count!r}")
        self._pending_failures += count

    def confirm_pending(self) -> None:
        """Confirme toutes les publications demandees qui ne sont ni confirmees ni echouees."""
        for handle in self._publications:
            if not handle.confirmed and not handle.failed:
                handle._mark_confirmed()

    def set_message_handler(self, handler: Callable[[Message], None]) -> None:
        """Enregistre un rappel appele a chaque message entrant."""
        self._on_message = handler

    def set_connection_handler(self, handler: Callable[[bool], None]) -> None:
        """Enregistre le rappel de cycle de connexion (C11). Aucun effet de bord."""
        self._on_connection = handler

    def deliver(self, message: Message) -> None:
        """Injecte un message entrant et notifie le rappel eventuel."""
        self._inbox.append(message)
        if self._on_message is not None:
            self._on_message(message)

    def fire_connected(self) -> None:
        """Notifie une connexion etablie. Declenchee par le TEST, jamais seule."""
        self._fire_connection(True)

    def fire_disconnected(self) -> None:
        """Notifie une connexion perdue ou non etablie. Declenchee par le TEST."""
        self._fire_connection(False)

    def _fire_connection(self, connected: bool) -> None:
        if self._on_connection is None:
            raise RuntimeError(
                "aucun handler de connexion enregistre : "
                "set_connection_handler() n'a pas ete appele"
            )
        self._on_connection(connected)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def connected_will(self) -> MqttWill | None:
        """Testament pose lors du dernier `connect()`, ou `None`."""
        return self._connected_will

    @property
    def publications(self) -> tuple[PublishHandle, ...]:
        """Publications demandees, dans l'ordre."""
        return tuple(self._publications)

    @property
    def subscriptions(self) -> tuple[Subscription, ...]:
        return tuple(self._subscriptions)

    @property
    def connection_events(self) -> tuple[str, ...]:
        """Suite des `connect` / `disconnect`, dans l'ordre."""
        return tuple(self._connection_events)

    @property
    def inbox(self) -> tuple[Message, ...]:
        """Messages entrants injectes, dans l'ordre."""
        return tuple(self._inbox)
