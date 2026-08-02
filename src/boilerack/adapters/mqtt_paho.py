"""Adaptateur MQTT reel fonde sur Paho MQTT v2 (`CallbackAPIVersion.VERSION2`).

Implemente la frontiere `MqttClient` de C2 en traduisant honnetement les
callbacks Paho en objets du domaine transport. Il ne porte AUCUNE politique
metier : ni validation, ni deduplication, ni cache, ni ACK, ni retry, ni
decodage du payload.

Honnetete du `PublishHandle` (arbitrage C4-A / A2 ratifie) :

- `publish()` cree un handle DEMANDE et n'est JAMAIS considere comme confirme du
  seul fait que l'appel a rendu la main ;
- un code retour immediat non nul (p. ex. `MQTT_ERR_NO_CONN`) marque le handle
  ECHOUE (echec etabli) ;
- la CONFIRMATION ne provient que du callback `on_publish` correspondant (PUBACK
  en QoS 1) ;
- jamais de `wait_for_publish()` (aucune attente indefinie de PUBACK).

Course PUBACK / enregistrement (A2) : `on_publish` s'execute sur le thread reseau
de Paho et peut precéder l'enregistrement du handle par `publish()`. Un verrou
protege un registre `mid -> PublishHandle` et un ensemble de `mid` acquittes
AVANT enregistrement ; un rappel en double est idempotent ; un `mid` inconnu
n'est jamais faussement rattache.

QoS (A3) : `boilerack` publie ses ACK en QoS 1, ou `on_publish` vaut PUBACK et
donc confirmation reelle. En QoS 0, `on_publish` ne prouve que la remise LOCALE a
Paho, pas la reception par le broker : ne pas confondre les deux semantiques.

Reconnexion (A4) : C4 n'ajoute AUCUNE politique metier de reconnexion. Seul le
comportement natif de Paho est utilise (boucle reseau via `loop_start`). Une
deconnexion est exposee honnetement et jamais masquee en connexion saine.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Protocol

from boilerack.adapters.config import MqttConfig
from boilerack.transport.mqtt import Message, MessageHandler, Publication, PublishHandle

logger = logging.getLogger(__name__)

# `MQTT_ERR_SUCCESS` vaut 0 dans Paho. On tente d'importer la constante officielle
# pour rester fidele a l'API, sans coupler l'import de ce module a Paho : les
# tests injectent un client et n'installent aucune dependance reseau a l'import.
try:  # pragma: no cover - depend de l'installation de Paho
    from paho.mqtt.client import MQTT_ERR_SUCCESS as _MQTT_ERR_SUCCESS
except Exception:  # pragma: no cover
    _MQTT_ERR_SUCCESS = 0


class PahoLike(Protocol):
    """Sous-ensemble de l'API Paho v2 reellement utilise par l'adaptateur.

    Permet d'injecter un faux client dans les tests sans dependre de Paho.
    """

    on_connect: Any
    on_disconnect: Any
    on_publish: Any
    on_message: Any

    def connect(self, host: str, port: int, keepalive: int) -> Any: ...
    def disconnect(self) -> Any: ...
    def loop_start(self) -> Any: ...
    def loop_stop(self) -> Any: ...
    def subscribe(self, topic: str, qos: int = 0) -> Any: ...
    def publish(
        self, topic: str, payload: bytes, qos: int = 0, retain: bool = False
    ) -> Any: ...


def _reason_is_success(reason_code: object) -> bool:
    """Vrai si un `reason_code` Paho v2 (ou un entier) indique un succes."""
    if reason_code is None:
        return True
    is_failure = getattr(reason_code, "is_failure", None)
    if is_failure is not None:
        return not bool(is_failure)
    try:
        return int(reason_code) == 0  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False


class PahoMqttClient:
    """Adaptateur `MqttClient` fonde sur Paho v2.

    Le client Paho est INJECTABLE : les tests fournissent un faux client. En
    l'absence d'injection, un client Paho reel est construit paresseusement
    (import de Paho differe a `_build_client`).
    """

    def __init__(self, config: MqttConfig, *, client: PahoLike | None = None) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._pending: dict[int, PublishHandle] = {}
        self._acked_early: set[int] = set()
        self._handler: MessageHandler | None = None
        self._connected = False

        self._client: PahoLike = client if client is not None else self._build_client(config)
        # Cablage des callbacks Paho v2.
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message

    @staticmethod
    def _build_client(config: MqttConfig) -> PahoLike:
        # Import de Paho UNIQUEMENT ici : les tests injectent un client et ne
        # dependent jamais de Paho. Aucune politique de reconnexion maison n'est
        # installee : on s'en remet au comportement natif de Paho.
        from paho.mqtt.client import CallbackAPIVersion, Client

        client = Client(CallbackAPIVersion.VERSION2, client_id=config.client_id)
        if config.username is not None:
            client.username_pw_set(config.username, config.password)
        if config.tls:
            client.tls_set()
        return client

    # -- cycle de connexion --------------------------------------------------

    def connect(self) -> None:
        cfg = self._config
        self._client.connect(cfg.host, cfg.port, cfg.keepalive)
        # Boucle reseau native de Paho (thread d'arriere-plan). Aucune politique
        # de reconnexion metier ajoutee.
        self._client.loop_start()

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
        with self._lock:
            self._connected = False

    def subscribe(self, topic: str, qos: int = 0) -> None:
        self._client.subscribe(topic, qos)

    # -- publication ---------------------------------------------------------

    def publish(
        self, topic: str, payload: bytes, qos: int = 0, retain: bool = False
    ) -> PublishHandle:
        publication = Publication(topic=topic, payload=payload, qos=qos, retain=retain)
        handle = PublishHandle(publication)

        info = self._client.publish(topic, payload, qos=qos, retain=retain)
        rc = getattr(info, "rc", _MQTT_ERR_SUCCESS)
        mid = getattr(info, "mid", None)

        if rc != _MQTT_ERR_SUCCESS:
            # Echec ETABLI et immediat : le broker/transport a refuse la remise.
            handle._mark_failed()
            logger.warning(
                "publication MQTT refusee immediatement rc=%s topic=%s", rc, topic
            )
            return handle

        with self._lock:
            if mid in self._acked_early:
                # Le PUBACK a precede cet enregistrement (course A2) : on consomme
                # le marqueur et on confirme immediatement.
                self._acked_early.discard(mid)
                handle._mark_confirmed()
            else:
                self._pending[mid] = handle
        return handle

    # -- callbacks Paho ------------------------------------------------------

    def _on_publish(
        self,
        client: object,
        userdata: object,
        mid: int,
        reason_code: object = None,
        properties: object = None,
    ) -> None:
        with self._lock:
            handle = self._pending.pop(mid, None)
            if handle is None:
                # Soit le PUBACK precede l'enregistrement du handle (course),
                # soit c'est un rappel en double apres confirmation, soit un
                # `mid` inconnu. Dans tous les cas : on memorise le `mid` sans
                # rien confirmer a tort. Le `publish()` correspondant le
                # consommera une seule fois s'il existe.
                self._acked_early.add(mid)
                return
        # Hors verrou : le handle nous appartient. Confirmation idempotente.
        if not (handle.confirmed or handle.failed):
            handle._mark_confirmed()

    def _on_message(self, client: object, userdata: object, message: Any) -> None:
        handler = self._handler
        if handler is None:
            logger.warning(
                "message MQTT recu sans handler enregistre, ignore topic=%s",
                getattr(message, "topic", "?"),
            )
            return
        # Payload remis en OCTETS BRUTS : aucun decodage JSON ici. Un payload
        # binaire non UTF-8 reste des octets.
        msg = Message(
            topic=message.topic,
            payload=bytes(message.payload),
            qos=getattr(message, "qos", 0),
            retain=getattr(message, "retain", False),
            dup=getattr(message, "dup", False),
        )
        try:
            handler(msg)
        except Exception:
            # Une exception du handler ne doit jamais remonter dans la boucle
            # Paho : on la journalise, on ne la propage pas.
            logger.exception(
                "le handler de message a leve une exception topic=%s", msg.topic
            )

    def _on_connect(
        self,
        client: object,
        userdata: object,
        flags: object,
        reason_code: object,
        properties: object = None,
    ) -> None:
        if _reason_is_success(reason_code):
            with self._lock:
                self._connected = True
            logger.info("connexion MQTT etablie")
        else:
            logger.warning("echec de connexion MQTT reason=%s", reason_code)

    def _on_disconnect(
        self,
        client: object,
        userdata: object,
        disconnect_flags: object = None,
        reason_code: object = None,
        properties: object = None,
    ) -> None:
        # Une deconnexion est exposee honnetement, jamais masquee.
        with self._lock:
            self._connected = False
        logger.warning("deconnexion MQTT reason=%s", reason_code)

    # -- entree ---------------------------------------------------------------

    def set_message_handler(self, handler: MessageHandler) -> None:
        self._handler = handler

    # -- inspection ----------------------------------------------------------

    @property
    def connected(self) -> bool:
        with self._lock:
            return self._connected

    @property
    def pending_publish_count(self) -> int:
        with self._lock:
            return len(self._pending)
