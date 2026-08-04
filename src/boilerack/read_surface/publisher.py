"""Presence du bridge sur la surface MQTT de lecture (lot C7-C3A).

Implemente §5 du contrat `c7-mqtt-read-contract.md` — testament, `online` a la
connexion, `offline` avant deconnexion propre — ainsi que l'etat de demarrage
exige par §7.3 (premiere ligne) et §8.2 (etat initial de la chaine).

CE COMPOSANT N'EST PAS ENCORE UN PRODUCTEUR CONFORME
    Il ne lit aucune mesure, ne publie aucune valeur scalaire, ne porte aucune
    cadence, aucun battement et aucun ordonnancement. La telemetrie relevera de
    C7-C3B. Un test fige cette limite pour qu'elle ne puisse pas etre prise
    pour un oubli.

PROPRIETE DU CYCLE DE CONNEXION
    Le client MQTT est **injecte**, jamais construit ici : ce composant n'est
    pas une composition root. Il possede en revanche le cycle
    `connect()` / `disconnect()`, et c'est necessaire : le testament doit etre
    pose AU MOMENT de la connexion, et son topic derive du prefixe de la
    surface de lecture. Confier la connexion a l'appelant rendrait la garantie
    conventionnelle au lieu de structurelle.

LIMITE DE RECONNEXION, ASSUMEE
    Aucune politique de reconnexion n'est implementee, et le contrat n'en
    definit aucune — le mot « reconnexion » n'y figure pas, et §15.5 range la
    politique de session du broker parmi les inconnues. Consequence a connaitre :
    apres une deconnexion INATTENDUE, le broker publie le testament et le topic
    retenu `bridge/online` passe a `offline` ; si Paho se reconnecte de
    lui-meme, ce composant ne le voit pas — la frontiere `MqttClient` n'expose
    aucun rappel de connexion — et le retenu restera `offline` alors que le
    bridge est vivant, jusqu'au prochain `start()`.

Aucune boucle, aucun thread, aucun sommeil : l'appelant pilote.
"""

from __future__ import annotations

from typing import Final, Sequence

from boilerack.clock import Clock
from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.measurements import V1_MEASUREMENTS, MeasurementSpec
from boilerack.read_surface.snapshot import build_snapshot, snapshot_to_json
from boilerack.read_surface.state import ReadSurfaceState
from boilerack.read_surface.topics import build_topic
from boilerack.transport.mqtt import MqttClient, MqttWill

__all__ = ["ReadSurfacePublisher"]

#: Suffixes contractuels employes par ce lot (§11). Un test verifie qu'ils
#: appartiennent bien a l'autorite close `V1_SUFFIXES`, ce qui interdit toute
#: derive entre cette chaine et la surface ratifiee.
_ONLINE_SUFFIX: Final = "bridge/online"
_STATUS_SUFFIX: Final = "bridge/telemetry_status"

#: §5 et §6.1 : les deux topics sont publies en QoS 1, retenus.
_QOS: Final = 1
_RETAIN: Final = True

_ONLINE: Final = b"online"
_OFFLINE: Final = b"offline"

#: Message du groupe leve quand l'annonce `offline` ET la deconnexion echouent.
#: Le texte n'est pas contractuel : seul importe que les deux exceptions
#: d'origine soient preservees, dans cet ordre.
_ARRET_ECHOUE: Final = "echec de l'arret propre MQTT"


class ReadSurfacePublisher:
    """Presence du bridge et instantane de demarrage.

    Ne publie que deux topics : `<prefix>/bridge/online` et
    `<prefix>/bridge/telemetry_status`. Tout autre topic serait interdit par
    §11.
    """

    def __init__(
        self,
        mqtt: MqttClient,
        clock: Clock,
        specs: Sequence[MeasurementSpec] = V1_MEASUREMENTS,
        config: ReadSurfaceConfig | None = None,
    ) -> None:
        # `config=None` puis construction interne, plutot qu'une instance en
        # valeur par defaut : la dataclass est gelee, donc sans risque de
        # partage, mais la construire ici evite tout travail a l'import du
        # module et rend explicite le cas « aucune configuration fournie ».
        self._mqtt = mqtt
        self._clock = clock
        self._specs = tuple(specs)
        self._config = config if config is not None else ReadSurfaceConfig()
        self._online_topic = build_topic(self._config.prefix, _ONLINE_SUFFIX)
        self._status_topic = build_topic(self._config.prefix, _STATUS_SUFFIX)
        # L'etat est initialise A LA CONSTRUCTION, pas dans `start()` : sa duree
        # de vie est celle du composant, pas celle d'une connexion. Un `start()`
        # ulterieur republie l'etat courant sans le reinitialiser.
        self._state = ReadSurfaceState.initial(self._specs)
        self._started = False

    # -- inspection ----------------------------------------------------------

    @property
    def state(self) -> ReadSurfaceState:
        """Etat de lecture courant (C7-C2)."""
        return self._state

    @property
    def online_topic(self) -> str:
        return self._online_topic

    @property
    def status_topic(self) -> str:
        return self._status_topic

    @property
    def started(self) -> bool:
        return self._started

    # -- cycle de vie --------------------------------------------------------

    def will(self) -> MqttWill:
        """Testament de la session : `offline` retenu sur le topic de presence (§5)."""
        return MqttWill(
            topic=self._online_topic, payload=_OFFLINE, qos=_QOS, retain=_RETAIN
        )

    def start(self) -> None:
        """Connecte avec testament, annonce la presence, publie l'instantane initial.

        Sequence, dans cet ordre exact :

        1. `connect(will=…)` — le testament est pose AVANT l'ouverture ;
        2. `online` sur `<prefix>/bridge/online`, QoS 1, retenu (§5) ;
        3. instantane initial sur `<prefix>/bridge/telemetry_status`, QoS 1,
           retenu — §7.3 : « Apres demarrage, avant la premiere lecture :
           aucune publication scalaire ; instantane publie avec
           `has_value: false`, `fresh: false`, `last_result: null` ».

        HONNETETE EN CAS D'ECHEC : si une publication leve, l'exception remonte
        telle quelle — aucune traduction, aucune taxonomie nouvelle, aucune
        compensation non contractee. Le drapeau de cycle de vie est pose des que
        la connexion est etablie, AVANT les publications : le client est alors
        reellement connecte, et `stop()` reste appelable pour le refermer
        proprement. `start()` n'aura pas rendu la main, mais rien ne pretendra
        qu'il a reussi.
        """
        if self._started:
            raise RuntimeError("start() a deja ete appele : cycle de vie incoherent")

        self._mqtt.connect(will=self.will())
        # Le client est connecte : l'etat de cycle de vie reflete la realite,
        # meme si une publication echoue juste apres.
        self._started = True

        self._publish(self._online_topic, _ONLINE)
        self._publish(self._status_topic, self._snapshot_bytes())

    def stop(self) -> None:
        """Annonce l'absence puis ferme la connexion (§5).

        L'annonce explicite n'est PAS redondante avec le testament : le
        protocole MQTT ne fait pas emettre le testament lors d'une deconnexion
        propre. Les deux mecanismes couvrent des cas disjoints.

        `disconnect()` est TOUJOURS tente, meme si l'annonce echoue.

        Quatre issues, toutes explicites :

        | annonce | deconnexion | ce qui remonte |
        |---|---|---|
        | OK | OK | rien |
        | KO | OK | l'erreur de publication, inchangee |
        | OK | KO | l'erreur de deconnexion, inchangee |
        | KO | KO | un `ExceptionGroup` portant **les deux**, dans cet ordre |

        Le dernier cas justifie de ne PAS s'en remettre au `finally` seul : la
        semantique de Python y ferait masquer l'erreur d'annonce par celle de
        deconnexion, et une information reelle serait perdue. Les exceptions
        d'origine sont conservees telles quelles — aucune conversion, aucune
        taxonomie metier nouvelle, aucune tentative supplementaire.

        Seules les `Exception` sont interceptees, jamais les `BaseException` :
        `KeyboardInterrupt`, `SystemExit` et `GeneratorExit` expriment un
        controle de flux, pas un echec d'arret. Elles remontent immediatement et
        inchangees, sans etre groupees — et sans que la deconnexion soit tentee,
        car interrompre une interruption pour faire du menage serait la trahir.

        Ce choix DIVERGE volontairement du precedent `engine._publish_terminal`,
        qui absorbe toute erreur de publication. La situation n'est pas la meme :
        le moteur protege un verdict deja en cache, qu'une publication ratee ne
        doit ni perdre ni remonter. Ici il n'y a aucun verdict a proteger, et
        taire l'echec laisserait croire que le depart a ete annonce.
        """
        if not self._started:
            raise RuntimeError("stop() appele sans start() prealable")

        self._started = False
        annonce: Exception | None = None
        try:
            self._publish(self._online_topic, _OFFLINE)
        except Exception as exc:  # large mais non aveugle : conservee, jamais absorbee
            annonce = exc

        try:
            self._mqtt.disconnect()
        except Exception as exc:
            if annonce is not None:
                raise ExceptionGroup(_ARRET_ECHOUE, [annonce, exc]) from None
            raise

        if annonce is not None:
            raise annonce

    # -- interne -------------------------------------------------------------

    def _publish(self, topic: str, payload: bytes) -> None:
        """Publie en QoS 1 retenu, sans jamais attendre de confirmation.

        Le `PublishHandle` est DELIBEREMENT ignore : §4.6 pose que les
        publications ne sont pas transactionnelles, et l'adaptateur reel
        n'attend jamais de PUBACK. Pretendre confirmer une livraison serait
        promettre une garantie que la frontiere ne fournit pas.
        """
        self._mqtt.publish(topic, payload, qos=_QOS, retain=_RETAIN)

    def _snapshot_bytes(self) -> bytes:
        return snapshot_to_json(build_snapshot(self._state, self._specs, self._clock))
