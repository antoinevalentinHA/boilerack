# C4 — Adaptateurs réels MQTT et frontière de processus

Lot **C4**. Relie les frontières abstraites de C2 (`MqttClient`, `VClient`) et le
cœur transactionnel de C3 à des adaptateurs techniques réels, **sans jamais
contacter la production** : aucun broker réel, aucun démon `vcontrold`, aucune
chaudière, aucun Pi, aucun déploiement, aucune migration depuis `boiler-bridge`.

> Promesse inchangée : « Le cœur ne suppose jamais qu'une commande a réussi.
> Seule une relecture conforme permet d'émettre `applied`. » « Une erreur
> technique ne doit jamais être transformée en faux succès. » « Une écriture qui
> peut avoir été émise ne doit jamais être classée comme certainement non émise. »

## Ce que C4 livre

| Élément | Module | État |
|---|---|---|
| Modèles de configuration | `boilerack.adapters.config` | livré |
| Adaptateur MQTT Paho v2 | `boilerack.adapters.mqtt_paho` | livré |
| Frontière de sous-processus générique | `boilerack.adapters.process_runner` | livré |
| Observabilité minimale du cœur | `boilerack.core.engine` (logging) | livré |
| Adaptateur `vclient` **concret** | — | **bloqué** (voir plus bas) |

## Ce que C4 NE livre PAS (et pourquoi)

L'adaptateur `vclient` concret — la traduction d'une sortie de processus vers un
`TransportStatus` — est **délibérément absent**. La caractérisation du dépôt
public montre que `_legacy/primitives.py` (extrait littéral du privé
`boiler-bridge`) **ne contient aucun** code d'invocation `vclient`/`vcontrold` :
uniquement validation, ACK, temps, UUID. La suite de caractérisation C1 ne couvre
aucun comportement de sous-processus.

Le format réel des arguments, des sorties, des codes retour et des erreurs de
`vclient` n'est donc **prouvé nulle part** dans le périmètre public. Inventer une
cartographie sortie → statut reviendrait à donner une fausse impression de
compatibilité. Décision (arbitrage **C4-A**, option 2 ratifiée) : la frontière de
processus générique est livrée, mais **aucun dialecte `vclient` n'est écrit** tant
que son contrat réel n'est pas caractérisé à partir d'une source explicite.

## Dépendance ajoutée

Première et unique dépendance d'exécution : **`paho-mqtt>=2.1,<3`**.

- Licence `EPL-2.0 OR BSD-3-Clause` (permissive, compatible MIT du projet) ;
- pur-Python, `requires_python >=3.7` → couvre **3.11 / 3.12 / 3.13** ;
- API callbacks **`CallbackAPIVersion.VERSION2`**.

L'adaptateur de processus n'ajoute aucune dépendance : `subprocess` (stdlib).

## Adaptateur MQTT (`PahoMqttClient`)

Enveloppe un `paho.mqtt.client.Client(CallbackAPIVersion.VERSION2, …)`
**injectable** (les tests fournissent un faux client ; Paho n'est construit que
par `_build_client`, jamais dans les tests). Aucune politique métier : ni
validation, ni déduplication, ni cache, ni ACK, ni retry, ni décodage du payload.

### Cycle du `PublishHandle` (honnêteté)

- `publish()` crée un handle **DEMANDÉ** ; le simple retour de `publish()` ne
  vaut **jamais** confirmation ;
- code retour immédiat `rc != MQTT_ERR_SUCCESS` → handle **ÉCHOUÉ** (échec
  établi, p. ex. `MQTT_ERR_NO_CONN`) ;
- la **CONFIRMATION** ne provient que du callback `on_publish` correspondant
  (PUBACK en QoS 1) ;
- **jamais** de `wait_for_publish()` : aucune attente indéfinie de PUBACK.

### Course PUBACK / enregistrement (durcie C4-CORR)

`on_publish` s'exécute sur le thread réseau de Paho et peut **précéder**
l'enregistrement du handle par `publish()`. Le `mid` n'étant attribué qu'à
l'intérieur de `client.publish()`, la seule course réelle est un PUBACK arrivant
**pendant** la fenêtre où `publish()` enregistre encore ce `mid`.

Traitement : un `threading.Lock` protège un registre `mid → PublishHandle`, un
ensemble **borné** de `mid` acquittés tôt, et un compteur `_registering` des
publications en cours d'enregistrement.

- `publish()` **ouvre** la fenêtre (`_registering += 1`) **avant**
  `client.publish()` (appelé **hors** verrou), puis, sous verrou : si le `mid`
  porte déjà un crédit d'ACK précoce, le consomme et confirme ; sinon enregistre
  le handle. En `finally`, **ferme** la fenêtre ; quand plus aucune publication
  n'enregistre (`_registering == 0`), **purge** tout crédit non consommé ;
- `on_publish` (sous verrou) : si un handle est enregistré, le retire (confirmé
  **hors** verrou) ; sinon dépose un crédit **seulement si** une fenêtre est
  ouverte (`_registering > 0`), et **abandonne** l'ACK autrement.

Garanties (verrouillées par tests) :

- un PUBACK précoce **légitime** confirme la publication en cours ;
- un **double** PUBACK après confirmation ne crée **aucun** crédit futur ;
- un `mid` **inconnu / orphelin** n'est jamais mémorisé sans limite (purge à la
  quiescence → aucune croissance non bornée) ;
- la **réutilisation** ultérieure d'un `mid` ne confirme **jamais** un nouveau
  handle sans nouveau PUBACK ;
- aucun callback externe n'est appelé sous verrou ; aucune attente bloquante.

### QoS

`boilerack` publie ses ACK en **QoS 1 non retained** : `on_publish` = PUBACK =
confirmation réelle. L'interface accepte QoS 0, mais alors `on_publish` ne prouve
que la **remise locale** à Paho, pas la réception par le broker. Aucun
consommateur ne doit confondre les deux sémantiques.

### Entrée des messages

`on_message` construit un `Message(topic, payload=octets bruts, qos, retain,
dup)` et le remet au handler enregistré via `set_message_handler`.

- **aucun décodage JSON** dans l'adaptateur ;
- payload binaire non UTF-8 préservé en octets ; payload vide accepté ; topic
  Unicode préservé ;
- handler absent → message ignoré et journalisé ; handler remplaçable ;
- une exception du handler est **capturée et journalisée**, jamais propagée dans
  la boucle Paho.

### Connexion / reconnexion

`connect()` appelle `client.connect(...)` puis `loop_start()` (boucle réseau
native de Paho, thread d'arrière-plan). **Aucune politique métier de reconnexion**
n'est ajoutée : ni boucle infinie maison, ni retry métier. Une déconnexion
(`on_disconnect`) est exposée honnêtement via la propriété `connected` et
**jamais masquée** en connexion saine. La reconnexion éventuelle relève du
comportement natif de Paho.

## Frontière de processus (`ProcessRunner` / `SubprocessRunner`)

Frontière **étroite et générique** autour d'un sous-processus, sans aucune
connaissance de `vclient`/`vcontrold`.

- entrées : liste d'arguments, `timeout` obligatoire (fini, > 0), `env`
  optionnel ;
- sorties (`ProcessResult`) : `returncode`, `stdout`/`stderr` en **octets bruts**,
  `timed_out`, `launch_failed`, `launch_error` (nom de classe d'exception
  uniquement) ;
- sécurité : **jamais `shell=True`**, aucun assemblage shell, liste d'arguments
  uniquement, aucune dépendance au répertoire courant, aucun `CompletedProcess`
  exposé au métier ;
- le runner **ne classe rien** : il rend compte. `timed_out` (processus lancé,
  ambigu) et `launch_failed` (processus jamais démarré, donc aucune commande
  transmise) sont distincts du déroulement normal ; la traduction en statut
  appartiendra au futur adaptateur `vclient`.

Le callable sous-jacent (`subprocess.run`) est **injectable** : tous les tests
injectent un faux et **n'exécutent jamais de processus réel**.

### `launch_failed` : besoin sémantique en attente

Un échec de lancement (exécutable absent, non exécutable, permission refusée)
**prouve qu'aucune écriture n'a été émise**, mais **ne prouve pas** que le démon
est injoignable. Il ne doit donc pas être mappé sur `DAEMON_UNREACHABLE`
(surchargerait la sémantique), ni provisoirement sur `TRANSPORT_ERROR` (forcerait
le cœur à une confirmation inutile puis un `timeout`). Ce constat justifie
peut-être un **statut de transport dédié** — par exemple `CLIENT_UNAVAILABLE`,
signifiant strictement « le client local n'a pas pu être lancé ; aucune commande
n'a été remise au démon ». Ce statut **n'est pas ajouté** dans ce lot : il exige
la caractérisation complète de la frontière `vclient`. Proposition présentée,
décision reportée.

## Observabilité minimale

Les `except Exception` conservateurs de C3 sont rendus **visibles** via `logging`
(`logging.getLogger("boilerack.core.engine")`), **sans changer aucun verdict** :
admission après réservation, exception avant/à partir de l'invocation d'écriture,
échec de lecture de confirmation, échec de publication terminale. Chaque trace
porte `request_id`, rôle, étape et **type** d'exception — **jamais** de secret ni
de payload complet. La journalisation est capturable en test (`caplog`).

Aucune métrique, OpenTelemetry, fichier de logs, rotation, serveur HTTP ni
diagnostic Home Assistant n'est ajouté.

## Robustesse de `_conclude`

La réserve théorique de la contre-vérification C3 (`terminal_cache.put()` et
`in_flight.release()` non protégés) est traitée par un **commentaire d'invariant**
uniquement : avec les implémentations mémoire actuelles, ces appels ne lèvent pas
pour un verdict terminal valide. Aucune machinerie de récupération n'est ajoutée,
afin de ne pas masquer une éventuelle corruption interne du cache.

## Tests — entièrement hors ligne

- **aucun broker, aucun démon, aucun exécutable réel, aucun réseau, aucune
  attente réelle** ;
- MQTT : faux client Paho injecté, callbacks déclenchés explicitement (y compris
  la course PUBACK) ;
- processus : `subprocess.run` remplacé par un faux runner ;
- intégration hors ligne : cœur C3 + adaptateur MQTT réel (faux client) +
  `VirtualClock` + profil factice. Le côté `vclient` utilise le double C2
  `FakeVClient` (l'adaptateur `vclient` concret restant bloqué), ce qui exerce
  malgré tout le chemin MQTT réel de bout en bout.

## Éléments reportés

- adaptateur `vclient` concret + dialecte de commande + cartographie sortie →
  `TransportStatus` (nécessitent le contrat réel de `vclient`) ;
- statut de transport dédié à l'échec de lancement (`CLIENT_UNAVAILABLE` proposé) ;
- chargement externe de la configuration (YAML/TOML/env) ;
- politique de reconnexion, démon durable, service permanent, découverte MQTT.

## Limites explicites

C4 **n'est pas validé sur une chaudière réelle** ni sur un `vcontrold` réel.
Aucun datapoint Viessmann, adresse Optolink, profil de production ni secret n'est
présent. L'adaptateur MQTT et la frontière de processus sont éprouvés uniquement
hors ligne, contre des doubles déterministes.
