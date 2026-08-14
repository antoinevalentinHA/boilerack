"""Publieur de la surface MQTT de lecture (lots C7-C3A et C7-C3B).

Implemente :

- **§5** — testament, `online` a la connexion, `offline` avant deconnexion
  propre (C7-C3A) ;
- **§7.3 ligne 1** et **§8.2** — etat et instantane de demarrage (C7-C3A) ;
- **§4.4, §4.5, §4.6** — lecture des mesures dues, publication scalaire apres
  succes, ordre par mesure (C7-C3B) ;
- **§7.2, §7.4** — echeances par mesure, republication periodique de
  l'instantane (C7-C3B) ;
- **§8.2** — cloture de cycle et derivation de `chain` (C7-C3B) ;
- **§9** — battement, en `SHOULD`, desactivable (C7-C3B).

PROPRIETE DU CYCLE DE CONNEXION
    Le client MQTT et le lecteur sont **injectes**, jamais construits ici : ce
    composant n'est pas une composition root. Il possede en revanche le cycle
    `connect()` / `disconnect()`, et c'est necessaire : le testament doit etre
    pose AU MOMENT de la connexion, et son topic derive du prefixe de la
    surface de lecture. Confier la connexion a l'appelant rendrait la garantie
    conventionnelle au lieu de structurelle.

AUCUNE BOUCLE, AUCUN THREAD, AUCUN SOMMEIL
    L'appelant pilote : il interroge `due_at()` pour savoir quand revenir, puis
    appelle `run_due()`. Il n'existe ni `run_forever()`, ni ordonnanceur
    interne, ni signal, ni composition root — tout cela suppose des decisions de
    deploiement que ce lot n'a pas a prendre.

LA VALEUR SCALAIRE EST EPHEMERE
    Elle va du `ReadResult` au payload sans jamais entrer dans l'etat :

        lecture -> publication scalaire -> projection d'etat -> instantane

    L'etat est une PROJECTION DES ISSUES. Ni `value`, ni `raw`, ni `detail` ne
    sont conserves.

LIMITE DE RECONNEXION, ASSUMEE
    Aucune politique de reconnexion n'est implementee, et le contrat n'en
    definit aucune — le mot « reconnexion » n'y figure pas, et §15.5 range la
    politique de session du broker parmi les inconnues. Consequence a connaitre :
    apres une deconnexion INATTENDUE, le broker publie le testament et le topic
    retenu `bridge/online` passe a `offline` ; si Paho se reconnecte de
    lui-meme, ce composant ne le voit pas — la frontiere `MqttClient` n'expose
    aucun rappel de connexion — et le retenu restera `offline` alors que le
    bridge est vivant, jusqu'au prochain `start()`.

AUCUNE CONFORMITE PRODUCTION N'EST REVENDIQUEE : rien n'a ete eprouve contre un
broker, un demon `vcontrold` ou une chaudiere reels.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Final, Protocol, Sequence

from boilerack.clock import Clock
from boilerack.read_surface.config import ReadSurfaceConfig
from boilerack.read_surface.measurements import (
    V1_MEASUREMENTS,
    MeasurementSpec,
    check_snapshot_period,
)
from boilerack.read_surface.payload import format_scalar
from boilerack.read_surface.snapshot import build_snapshot, snapshot_to_json
from boilerack.read_surface.state import ReadSurfaceState, complete_cycle, record_result
from boilerack.read_surface.topics import build_topic
from boilerack.connection_state import ConnectionState
from boilerack.transport.mqtt import MqttWill, PresenceMqttClient
from boilerack.transport.vclient import ReadResult, TransportStatus

__all__ = ["MeasurementReader", "ReadSurfacePublisher"]

#: Suffixes contractuels employes ici (§11). Un test verifie qu'ils
#: appartiennent bien a l'autorite close `V1_SUFFIXES`, ce qui interdit toute
#: derive entre ces chaines et la surface ratifiee.
_ONLINE_SUFFIX: Final = "bridge/online"
_STATUS_SUFFIX: Final = "bridge/telemetry_status"
_HEARTBEAT_SUFFIX: Final = "bridge/heartbeat"

#: §4.4, §5 et §6.1 : presence, telemetrie et instantane en QoS 1, retenus.
_QOS: Final = 1
_RETAIN: Final = True

#: §9 : le battement, lui, est en QoS 0 et **non retenu**.
_HEARTBEAT_QOS: Final = 0
_HEARTBEAT_RETAIN: Final = False

_ONLINE: Final = b"online"
_OFFLINE: Final = b"offline"

#: Forme RFC 3339 UTC suffixee `Z`, identique a celle de l'instantane (§6.4).
#: Un test verifie que le battement et l'instantane produisent le meme `ts` a
#: instant egal, ce qui interdit toute derive entre les deux formateurs.
_TS_FORMAT: Final = "%Y-%m-%dT%H:%M:%SZ"

#: Messages des groupes d'erreurs. Non contractuels : seule importe la
#: preservation des exceptions d'origine.
_ARRET_ECHOUE: Final = "echec de l'arret propre MQTT"
_CYCLE_ECHOUE: Final = "echecs de publication MQTT pendant le cycle"


class MeasurementReader(Protocol):
    """Frontiere de LECTURE dont le publieur a besoin — et rien de plus.

    Pourquoi un protocole etroit plutot qu'un type existant :

    - `boilerack.transport.vclient.VClient` exige `read` **et** `write`, et C6 a
      etabli que son lecteur ne doit PAS le satisfaire tant que l'ecriture n'est
      pas caracterisee. L'annoter ainsi serait faux ;
    - `boilerack.adapters.vclient_cli.VClientCliReader` est une classe concrete
      d'adaptateur. L'importer ferait dependre `read_surface` de `adapters`, et
      chargerait `subprocess` par transitivite.

    Le typage structurel resout les deux : `VClientCliReader` satisfait ce
    protocole sans qu'aucun import ne les relie.
    """

    def read(self, command: str) -> ReadResult:
        ...


class ReadSurfacePublisher:
    """Presence, lecture des mesures dues et publications de la surface v1.

    Ne publie que des suffixes de la surface v1 (§11) : les huit mesures,
    `bridge/online`, `bridge/telemetry_status` et, si active,
    `bridge/heartbeat`. Tout autre topic serait interdit.
    """

    def __init__(
        self,
        mqtt: PresenceMqttClient,
        clock: Clock,
        connection: ConnectionState,
        reader: MeasurementReader | None = None,
        specs: Sequence[MeasurementSpec] = V1_MEASUREMENTS,
        config: ReadSurfaceConfig | None = None,
    ) -> None:
        # `config=None` puis construction interne, plutot qu'une instance en
        # valeur par defaut : la dataclass est gelee, donc sans risque de
        # partage, mais la construire ici evite tout travail a l'import du
        # module et rend explicite le cas « aucune configuration fournie ».
        self._mqtt = mqtt
        self._clock = clock
        self._connection = connection
        self._reader = reader
        self._specs: tuple[MeasurementSpec, ...] = tuple(specs)
        self._config = config if config is not None else ReadSurfaceConfig()

        # §7.4 : la republication ne doit pas depasser la fraicheur. Ce controle
        # depend des specs REELLEMENT injectees, il ne peut donc pas vivre dans
        # la configuration seule. La regle est DELEGUEE a `check_snapshot_period`
        # pour qu'elle n'existe qu'a un seul endroit : un appelant qui valide
        # une configuration avant construction appelle la meme autorite.
        check_snapshot_period(self._specs, self._config.snapshot_period_s)

        self._online_topic = build_topic(self._config.prefix, _ONLINE_SUFFIX)
        self._status_topic = build_topic(self._config.prefix, _STATUS_SUFFIX)
        self._heartbeat_topic = build_topic(self._config.prefix, _HEARTBEAT_SUFFIX)
        self._scalar_topics = {
            spec.role: build_topic(self._config.prefix, spec.suffix)
            for spec in self._specs
        }

        # L'etat est initialise A LA CONSTRUCTION, pas dans `start()` : sa duree
        # de vie est celle du composant, pas celle d'une connexion. Un `start()`
        # ulterieur republie l'etat courant sans le reinitialiser.
        self._state = ReadSurfaceState.initial(self._specs)
        self._started = False

        # Echeances monotones, posees a `start()`.
        self._next_due: dict[str, float] = {}
        self._next_snapshot_due: float | None = None
        self._next_heartbeat_due: float | None = None

        # C11 : la capacite de notification est REQUISE, jamais sondee. L'appel
        # est direct — un client qui ne la porte pas fait echouer la
        # construction, visiblement. Aucun `hasattr`, aucun repli : tolerer
        # l'absence reviendrait a livrer une surface qui pretend honorer C7-B §5
        # sans le pouvoir. Enregistrement PUR : aucune entree-sortie ici, et
        # place APRES la validation, pour ne pas laisser un rappel branche sur
        # un publieur dont la construction echoue.
        self._mqtt.set_connection_handler(self._connection.notify)

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
    def heartbeat_topic(self) -> str:
        return self._heartbeat_topic

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
           `has_value: false`, `fresh: false`, `last_result: null` » ;
        4. **echeances posees** : toutes les mesures deviennent immediatement
           dues, l'instantane et le battement sont replanifies a `+ periode`.

        ECHEANCES INITIALES — decision d'implementation, pas une clause. Le
        contrat ne dit pas quand la premiere lecture doit avoir lieu. Rendre les
        mesures immediatement dues est la lecture la plus fidele : §7.3 exige
        que l'instantane initial precede toute lecture — ce qui est le cas —, et
        rien n'impose d'attendre une periode entiere avant la premiere donnee.
        Le demarrage est le premier reveil.

        Aucun battement n'est publie ici : §9 ne l'exige pas, et le publier
        laisserait croire a une vitalite que rien n'a encore etablie.

        HONNETETE EN CAS D'ECHEC : si une publication leve, l'exception remonte
        telle quelle — aucune traduction, aucune taxonomie nouvelle, aucune
        compensation non contractee. Le drapeau de cycle de vie est pose des que
        la connexion est etablie, AVANT les publications : le client est alors
        reellement connecte, et `stop()` reste appelable pour le refermer
        proprement. Les echeances ne sont posees qu'apres les publications : un
        `start()` interrompu ne laisse donc pas d'echeances a demi-armees.
        """
        if self._started:
            raise RuntimeError("start() a deja ete appele : cycle de vie incoherent")

        # C11 §8.3 — BASE AVANT L'OUVERTURE, et non apres les publications.
        # A cet instant aucun appel n'a encore ete fait au transport, donc aucun
        # rappel n'est possible : la place est sure par CONSTRUCTION, non par
        # chronometrie. Poser la base plus tard ecraserait un echec de CONNACK
        # deja observe, et la reussite suivante ne serait plus une transition :
        # la reprise serait perdue.
        self._connection.mark_connected()

        self._mqtt.connect(will=self.will())
        # Le client est connecte : l'etat de cycle de vie reflete la realite,
        # meme si une publication echoue juste apres.
        self._started = True

        self._publish(self._online_topic, _ONLINE)
        self._publish(self._status_topic, self._snapshot_bytes())

        maintenant = self._clock.monotonic()
        self._next_due = {spec.role: maintenant for spec in self._specs}
        self._next_snapshot_due = maintenant + self._config.snapshot_period_s
        self._next_heartbeat_due = (
            maintenant + self._config.heartbeat_period_s
            if self._config.heartbeat_period_s is not None
            else None
        )

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

        Les echeances sont oubliees : elles appartiennent a une session, pas au
        composant. L'etat de lecture, lui, survit — un `start()` ulterieur le
        republie sans le reinitialiser.
        """
        if not self._started:
            raise RuntimeError("stop() appele sans start() prealable")

        self._started = False
        self._next_due = {}
        self._next_snapshot_due = None
        self._next_heartbeat_due = None
        # C11 : aucune reprise en attente ne survit a l'arret. Desarmement
        # EXPLICITE, et non deduit d'une notification de deconnexion : le
        # transport n'est pas tenu d'en emettre une pour un `disconnect()`
        # volontaire, et la surete de l'arret ne doit dependre d'aucun rappel.
        self._connection.disarm()

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

    # -- echeances -----------------------------------------------------------

    def due_at(self) -> float:
        """Instant monotone de la prochaine echeance, toutes categories confondues.

        Ne lit pas l'horloge murale, ne modifie aucun etat, ne publie rien.
        L'appelant s'en sert pour savoir quand rappeler `run_due()`.

        Leve avant `start()` : aucune echeance n'existe tant que la session n'a
        pas commence.
        """
        self._exiger_demarre("due_at()")
        echeances = list(self._next_due.values())
        if self._next_snapshot_due is not None:
            echeances.append(self._next_snapshot_due)
        if self._next_heartbeat_due is not None:
            echeances.append(self._next_heartbeat_due)
        if not echeances:
            # Inatteignable avec une surface non vide : l'instantane a toujours
            # une echeance des `start()`.
            raise RuntimeError("aucune echeance : la surface est vide")
        return min(echeances)

    def due_measurements(self) -> tuple[MeasurementSpec, ...]:
        """Mesures echues a cet instant, dans l'ordre des specs.

        Aucun tri alphabetique : §4.2 fixe un ordre, et `run_due` le suit.
        """
        self._exiger_demarre("due_measurements()")
        maintenant = self._clock.monotonic()
        return tuple(
            spec for spec in self._specs if self._next_due[spec.role] <= maintenant
        )

    # -- cycle ---------------------------------------------------------------

    def run_due(self) -> None:
        """Traite tout ce qui est du a cet instant. Ne boucle jamais.

        Ordre, fige au debut de l'appel :

        0. reprise de presence, si une connexion a ete retablie depuis la
           derniere consommation (C11) — republication de `online`, et rien
           d'autre : ni echeance touchee, ni etat de lecture modifie ;
        1. instant monotone captute UNE fois — l'ensemble des taches dues ne
           change plus pendant l'appel, meme si les lectures prennent du temps ;
        2. mesures dues, dans l'ordre des specs, lues **sequentiellement** — C6
           n'accepte qu'une commande par invocation ;
        3. cloture du cycle, **uniquement** si au moins une mesure etait due ;
        4. instantane de fin de cycle ;
        5. instantane periodique, **seulement** s'il n'a pas deja ete publie
           dans cet appel ;
        6. battement du, si active ;
        7. `ExceptionGroup` des erreurs de publication collectees, s'il y en a.

        ERREURS DE PUBLICATION — collectees, jamais absorbees. Une publication
        qui echoue n'interrompt pas le cycle : les lectures dues restent
        traitees, l'etat reste fonde sur les LECTURES (§4.6 : « `last_result`
        porte l'issue de la lecture, jamais celle de la publication MQTT »), et
        aucune erreur n'est tue. Elles remontent groupees a la fin, dans l'ordre
        de survenue, exceptions d'origine preservees.

        EXCEPTION INATTENDUE DU LECTEUR — remonte telle quelle, immediatement.
        C6 garantit qu'aucune issue de transport ne leve : une exception signale
        donc un DEFAUT, que la convertir en `TransportStatus` maquillerait. Le
        cycle n'est pas cloture, `chain` n'est pas fabrique sur un cycle
        incomplet, les mesures deja traitees restent projetees et replanifiees,
        les autres restent dues. Consequence assumee : les erreurs de
        publication deja collectees sont alors perdues — les grouper avec un
        defaut le noierait.
        """
        self._exiger_demarre("run_due()")
        maintenant = self._clock.monotonic()

        dues = tuple(
            spec for spec in self._specs if self._next_due[spec.role] <= maintenant
        )
        snapshot_du = (
            self._next_snapshot_due is not None and self._next_snapshot_due <= maintenant
        )
        heartbeat_du = (
            self._next_heartbeat_due is not None
            and self._next_heartbeat_due <= maintenant
        )

        erreurs: list[Exception] = []
        resultats: dict[str, TransportStatus] = {}
        snapshot_publie = False

        # C11 — etape 0 : reprise de presence. Placee ici, elle herite de deux
        # garanties sans ecrire une ligne d'ordonnancement : la verification de
        # demarrage l'a precedee, et le runner a deja consulte l'arret avant
        # d'appeler cette methode. L'arret prime donc toujours sur une reprise.
        # `_tenter` applique le QoS et la retention contractuels, et une erreur
        # de publication rejoint le groupe du cycle, comme toutes les autres.
        if self._connection.consume_recovery():
            self._tenter(erreurs, self._online_topic, _ONLINE)

        for spec in dues:
            # Une exception inattendue du lecteur remonte ici, sans cloture.
            resultat = self._reader_or_raise().read(spec.read)

            if resultat.status is TransportStatus.OK:
                # §4.6 : scalaire, PUIS etat, PUIS instantane.
                assert resultat.value is not None  # invariant durci de ReadResult
                self._tenter(
                    erreurs,
                    self._scalar_topics[spec.role],
                    format_scalar(resultat.value),
                )
                self._state = record_result(
                    self._state, spec.role, TransportStatus.OK, self._clock
                )
                self._tenter(erreurs, self._status_topic, self._snapshot_bytes())
                snapshot_publie = True
            else:
                # §4.4 : rien n'est publie sur un echec, aucune sentinelle.
                self._state = record_result(
                    self._state, spec.role, resultat.status, self._clock
                )

            resultats[spec.role] = resultat.status
            # Sans rattrapage : la prochaine echeance repart de la FIN de la
            # tentative, jamais de l'echeance theorique manquee.
            self._next_due[spec.role] = self._clock.monotonic() + spec.period_s

        if resultats:
            self._state = complete_cycle(self._state, resultats)
            # Publie meme si toutes les lectures ont echoue : c'est precisement
            # la que `chain` change.
            self._tenter(erreurs, self._status_topic, self._snapshot_bytes())
            snapshot_publie = True

        if snapshot_du and not snapshot_publie:
            self._tenter(erreurs, self._status_topic, self._snapshot_bytes())
            snapshot_publie = True

        if snapshot_publie:
            # Toute publication TENTEE de l'instantane repousse l'echeance
            # periodique : §7.4 borne l'intervalle maximal, publier plus souvent
            # reste conforme, et republier deux fois de suite le meme etat dans
            # un seul appel n'apporterait rien.
            self._next_snapshot_due = (
                self._clock.monotonic() + self._config.snapshot_period_s
            )

        if heartbeat_du:
            self._tenter(
                erreurs,
                self._heartbeat_topic,
                self._heartbeat_bytes(),
                qos=_HEARTBEAT_QOS,
                retain=_HEARTBEAT_RETAIN,
            )
            self._next_heartbeat_due = (
                self._clock.monotonic() + self._config.heartbeat_period_s  # type: ignore[operator]
            )

        if erreurs:
            raise ExceptionGroup(_CYCLE_ECHOUE, erreurs)

    # -- interne -------------------------------------------------------------

    def _exiger_demarre(self, quoi: str) -> None:
        if not self._started:
            raise RuntimeError(f"{quoi} appele sans start() prealable")

    def _reader_or_raise(self) -> MeasurementReader:
        if self._reader is None:
            raise RuntimeError("aucun lecteur injecte : aucune mesure ne peut etre lue")
        return self._reader

    def _tenter(
        self,
        erreurs: list[Exception],
        topic: str,
        payload: bytes,
        *,
        qos: int = _QOS,
        retain: bool = _RETAIN,
    ) -> None:
        """Publie et COLLECTE une erreur ordinaire, sans jamais l'absorber."""
        try:
            self._publish(topic, payload, qos=qos, retain=retain)
        except Exception as exc:  # large mais non aveugle : conservee, regroupee
            erreurs.append(exc)

    def _publish(
        self, topic: str, payload: bytes, *, qos: int = _QOS, retain: bool = _RETAIN
    ) -> None:
        """Publie, sans jamais attendre de confirmation.

        Le `PublishHandle` est DELIBEREMENT ignore : §4.6 pose que les
        publications ne sont pas transactionnelles, et l'adaptateur reel
        n'attend jamais de PUBACK. Pretendre confirmer une livraison serait
        promettre une garantie que la frontiere ne fournit pas.
        """
        self._mqtt.publish(topic, payload, qos=qos, retain=retain)

    def _snapshot_bytes(self) -> bytes:
        return snapshot_to_json(build_snapshot(self._state, self._specs, self._clock))

    def _heartbeat_bytes(self) -> bytes:
        """§9 : `{"ts":"…"}` compact, RFC 3339 UTC, aucun champ supplementaire.

        Le battement n'atteste QUE de l'activite du processus. Aucune sante de
        la chaudiere, ni de la chaine de lecture, ne doit en etre deduite.
        """
        return json.dumps(
            {"ts": self._maintenant_iso()},
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

    def _maintenant_iso(self) -> str:
        """Instant mural en RFC 3339 UTC, meme forme que l'instantane (§6.4)."""
        moment = self._clock.now()
        if not isinstance(moment, datetime):
            raise ValueError(f"instant attendu, recu {type(moment).__name__}")
        if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
            raise ValueError("un instant sans fuseau horaire ne peut pas etre publie")
        return moment.astimezone(timezone.utc).strftime(_TS_FORMAT)
