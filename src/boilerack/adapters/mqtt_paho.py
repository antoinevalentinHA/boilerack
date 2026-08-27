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

Course PUBACK / enregistrement (A2, durci C4-CORR) : `on_publish` s'execute sur
le thread reseau de Paho et peut preceder l'enregistrement du handle par
`publish()`. Un verrou protege un registre `mid -> PublishHandle` et un ensemble
BORNE de `mid` acquittes tot. Ce dernier n'accepte un credit QUE pendant une
FENETRE DE CORRELATION ouverte (`_registering > 0`, i.e. une publication est en
train de s'enregistrer) ; des qu'aucune publication n'enregistre plus, tout
credit non consomme est PURGE. Consequences garanties :

- un PUBACK precoce legitime confirme la publication en cours ;
- un double PUBACK apres confirmation ne cree aucun credit pour une publication
  future ;
- un `mid` inconnu ou orphelin n'est jamais memorise sans limite ;
- la reutilisation ulterieure d'un `mid` ne confirme jamais un nouveau handle
  sans nouveau PUBACK ;
- un rappel en double est idempotent ; aucun callback externe n'est appele sous
  verrou ; aucune attente bloquante.

QoS (A3) : `boilerack` publie ses ACK en QoS 1, ou `on_publish` vaut PUBACK et
donc confirmation reelle. En QoS 0, `on_publish` ne prouve que la remise LOCALE a
Paho, pas la reception par le broker : ne pas confondre les deux semantiques.

Souscriptions (W0) : un registre INTERNE conserve les souscriptions logiques
demandees — `topic -> qos` — et l'adaptateur les reemet apres chaque CONNACK
reussi. Sans cela, une session neuve les perdrait SILENCIEUSEMENT et le pont
cesserait de recevoir sans que rien ne le signale. Le registre n'est ni une
politique de reconnexion, ni une session persistante : W0 garantit la REEMISSION
d'un SUBSCRIBE, jamais son acceptation par le broker. Voir
`docs/design/w0-mqtt-subscription-recovery.md`.

Reconnexion (A4) : C4 n'ajoute AUCUNE politique metier de reconnexion. Seul le
comportement natif de Paho est utilise (boucle reseau via `loop_start`). Une
deconnexion est exposee honnetement et jamais masquee en connexion saine.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Protocol

from boilerack.adapters.config import MqttConfig
from boilerack.transport.mqtt import (
    ConnectionHandler,
    Message,
    MessageHandler,
    MqttWill,
    Publication,
    PublishHandle,
)

logger = logging.getLogger(__name__)

# `MQTT_ERR_SUCCESS` vaut 0 dans Paho. On tente d'importer la constante officielle
# pour rester fidele a l'API, sans coupler l'import de ce module a Paho : les
# tests injectent un client et n'installent aucune dependance reseau a l'import.
# `MQTTErrorCode` est une enumeration d'entiers ; `int` couvre donc la constante
# importee comme le repli, et la comparaison `rc != _MQTT_ERR_SUCCESS` porte sur
# des entiers dans les deux cas.
_MQTT_ERR_SUCCESS: int
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
    def will_set(
        self, topic: str, payload: Any = None, qos: int = 0, retain: bool = False
    ) -> Any: ...
    def will_clear(self) -> Any: ...
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
        # `reason_code` est `object` : la conversion n'est tentee que sous
        # `try`, et l'echec est rattrape juste dessous. Le code d'erreur reel
        # est `call-overload`, non `arg-type`.
        return int(reason_code) == 0  # type: ignore[call-overload]
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
        # Crédits d'ACK précoces (PUBACK arrivé pendant qu'un `publish()` enregistre
        # encore son `mid`). Bornés : n'existent QUE pendant une fenêtre de
        # corrélation ouverte (`_registering > 0`) et sont purgés dès qu'aucune
        # publication n'est en cours d'enregistrement.
        self._early_acks: set[int] = set()
        # Nombre de `publish()` actuellement dans leur fenêtre d'enregistrement
        # (entre l'appel `client.publish()` et l'enregistrement du handle).
        self._registering = 0
        self._handler: MessageHandler | None = None
        # C11 : rappel de cycle de connexion. `None` est LEGITIME — un
        # consommateur qui n'a pas d'obligation de presence, comme le coeur
        # transactionnel, n'en enregistre aucun. Ce n'est pas un repli
        # silencieux : c'est l'absence d'un destinataire.
        self._connection_handler: ConnectionHandler | None = None
        self._connected = False
        # W0 : souscriptions LOGIQUES demandees par l'appelant, `topic -> qos`.
        # Un `dict` suffit et porte exactement la semantique contractee : une
        # entree par topic, ordre d'INSERTION preserve, et une redeclaration de
        # QoS met la valeur a jour SANS deplacer la cle. Aucune structure
        # dediee, aucun registre public.
        self._souscriptions: dict[str, int] = {}

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

    def connect(self, will: MqttWill | None = None) -> None:
        """Pose le testament PUIS ouvre la connexion, dans cet ordre exact.

        Paho documente que `will_set()` « must be called before connect() to
        have any effect » : le testament est empaquete dans le CONNECT. L'ordre
        est donc encapsule ici plutot que confie a l'appelant.

        `will=None` appelle `will_clear()` : sans cela, un testament pose lors
        d'une connexion anterieure survivrait SILENCIEUSEMENT a une nouvelle
        connexion censee ne pas en porter.

        Le testament reste attache au client Paho et est reemis dans chaque
        CONNECT : une reconnexion native le conserve, aucune action n'est
        requise. Aucune politique de reconnexion metier n'est ajoutee.
        """
        cfg = self._config
        if will is not None:
            self._client.will_set(
                will.topic, will.payload, qos=will.qos, retain=will.retain
            )
        else:
            self._client.will_clear()
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
        """Enregistre l'intention PUIS la transmet au client (W0 §7).

        L'enregistrement precede la transmission et a lieu INCONDITIONNELLEMENT :
        il ne depend ni de l'etat de la connexion, ni de l'issue de la
        transmission. Si `client.subscribe` leve, l'intention reste enregistree
        et sera reemise au prochain CONNACK reussi.

        CONSEQUENCE A CONNAITRE (W0 §7.1) : il n'existe aucun retrait. Une
        souscription demandee une fois engage cet objet jusqu'a sa fin de vie.

        Un second appel identique est TRANSMIS comme le premier — l'appelant a
        demande deux fois — mais ne cree pas de seconde entree.
        """
        with self._lock:
            self._souscriptions[topic] = qos
        # Hors verrou : W0 §14 interdit toute emission vers Paho sous verrou.
        self._client.subscribe(topic, qos)

    def _restaurer_souscriptions(self) -> None:
        """Reemet toutes les souscriptions enregistrees (W0 §8).

        Opere sur un INSTANTANE pris sous verrou, jamais sur la structure
        vivante : un `subscribe()` concurrent — possible, C11 P12 etablissant
        qu'un rappel peut survenir pendant le demarrage de l'appelant — ne doit
        pas modifier la collection en cours de parcours.

        Un echec est journalise avec son topic, N'EST PAS propage dans la boucle
        Paho, NE RETIRE PAS l'intention, et n'interrompt pas les suivantes.
        Aucun indicateur de sante n'est cree : `online` ne signifie pas
        « souscriptions restaurees » (W0 §11.2).
        """
        with self._lock:
            instantane = tuple(self._souscriptions.items())
        for topic, qos in instantane:
            try:
                self._client.subscribe(topic, qos)
            except Exception as exc:
                logger.warning(
                    "restauration de souscription en echec, intention conservee "
                    "topic=%s qos=%s exc=%s",
                    topic,
                    qos,
                    type(exc).__name__,
                )

    # -- publication ---------------------------------------------------------

    def publish(
        self, topic: str, payload: bytes, qos: int = 0, retain: bool = False
    ) -> PublishHandle:
        publication = Publication(topic=topic, payload=payload, qos=qos, retain=retain)
        handle = PublishHandle(publication)

        # Ouverture de la FENETRE DE CORRELATION : dès maintenant (avant même
        # `client.publish()`), un PUBACK précoce arrivant sur le thread réseau
        # sera reconnu comme légitime. On ne tient PAS le verrou pendant
        # `client.publish()` (aucun callback externe sous verrou, aucun risque
        # de réentrance).
        with self._lock:
            self._registering += 1
        confirm_now = False
        failed = False
        try:
            info = self._client.publish(topic, payload, qos=qos, retain=retain)
            rc = getattr(info, "rc", _MQTT_ERR_SUCCESS)
            mid = getattr(info, "mid", None)

            if rc != _MQTT_ERR_SUCCESS:
                # Echec ETABLI et immediat : le broker/transport a refuse la remise.
                failed = True
            else:
                with self._lock:
                    if mid in self._early_acks:
                        # Le PUBACK a précédé cet enregistrement (course A2) :
                        # crédit légitime pour CETTE publication, consommé ici.
                        self._early_acks.discard(mid)
                        confirm_now = True
                    else:
                        # `mid` vient d'un `getattr` sur l'objet rendu par
                        # Paho : l'adaptateur ne DECODE rien et le memorise
                        # tel quel. Le registre est indexe par ce que le
                        # transport a fourni, sans le reinterpreter.
                        self._pending[mid] = handle  # type: ignore[index]
        finally:
            # Fermeture de la fenêtre. Quand plus AUCUNE publication n'enregistre,
            # tout crédit d'ACK précoce non consommé est OBSOLETE : on le purge.
            # Un ACK orphelin (double PUBACK, `mid` inconnu, ou `mid` promis à une
            # réutilisation future) ne peut donc jamais survivre a la quiescence,
            # ni confirmer une publication ultérieure sans nouveau PUBACK.
            with self._lock:
                self._registering -= 1
                if self._registering == 0:
                    self._early_acks.clear()

        if failed:
            handle._mark_failed()
            logger.warning(
                "publication MQTT refusee immediatement topic=%s", topic
            )
        elif confirm_now:
            handle._mark_confirmed()
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
        confirmed_handle: PublishHandle | None = None
        with self._lock:
            handle = self._pending.pop(mid, None)
            if handle is None:
                # Aucun handle enregistré pour ce `mid`. Deux cas :
                # - une publication est en cours d'enregistrement
                #   (`_registering > 0`) : PUBACK précoce légitime -> on dépose un
                #   crédit BORNE, que ce `publish()` consommera puis que la
                #   quiescence purgera ;
                # - sinon (`_registering == 0`) : ACK orphelin (double PUBACK,
                #   `mid` inconnu ou obsolète) -> on l'ABANDONNE. Il ne crée
                #   AUCUN droit de confirmation permanent.
                if self._registering > 0:
                    self._early_acks.add(mid)
                return
            confirmed_handle = handle
        # Hors verrou : le handle nous appartient. Confirmation idempotente.
        if not (confirmed_handle.confirmed or confirmed_handle.failed):
            confirmed_handle._mark_confirmed()

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
        etabli = _reason_is_success(reason_code)
        with self._lock:
            self._connected = etabli
        if etabli:
            logger.info("connexion MQTT etablie")
        else:
            # C11 : un CONNACK en echec n'est JAMAIS une connexion etablie. Le
            # dire est le seul moyen d'empecher un etat suppose de survivre a un
            # fait contraire — sans quoi une reussite ulterieure ne serait plus
            # une transition, et la reprise de presence serait perdue.
            logger.warning("echec de connexion MQTT reason=%s", reason_code)
        # Notification HORS VERROU : aucun rappel externe n'est appele sous
        # verrou, invariant deja pose par ce module.
        self._notifier(etabli)
        if etabli:
            # W0 §9 : la restauration vient APRES la notification de presence.
            # Cet ordre est normatif — la notification n'echoue pas, la
            # restauration le peut : C11 ne doit jamais dependre de W0. Un
            # CONNACK en echec ne restaure rien (W0 §8).
            self._restaurer_souscriptions()

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
        self._notifier(False)

    def _notifier(self, connected: bool) -> None:
        """Transmet une transition au rappel enregistre, sans jamais laisser filer.

        Une exception du rappel serait relancee par Paho dans sa boucle reseau —
        `suppress_exceptions` vaut `False` par defaut — et pourrait la rompre.
        Elle est donc journalisee et absorbee ICI, a la frontiere, ou elle ne
        peut nuire a personne d'autre.
        """
        handler = self._connection_handler
        if handler is None:
            return
        try:
            handler(connected)
        except Exception:  # large mais non aveugle : journalisee, jamais relancee
            logger.exception("le handler de connexion a leve connected=%s", connected)

    # -- entree ---------------------------------------------------------------

    def set_message_handler(self, handler: MessageHandler) -> None:
        self._handler = handler

    def set_connection_handler(self, handler: ConnectionHandler) -> None:
        """Enregistre le rappel de cycle de connexion (C11). Aucun effet de bord.

        Enregistrement pur : aucune socket, aucun processus, aucune notification
        immediate. L'etat courant n'est PAS rejoue vers un rappel qui arrive
        apres coup — ce serait fabriquer une transition qui n'a pas eu lieu.
        """
        self._connection_handler = handler

    # -- inspection ----------------------------------------------------------

    @property
    def connected(self) -> bool:
        with self._lock:
            return self._connected

    @property
    def pending_publish_count(self) -> int:
        with self._lock:
            return len(self._pending)
