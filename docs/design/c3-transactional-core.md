# C3 — Cœur transactionnel générique et profil déclaratif

Document interne de conception. Il décrit le cœur métier générique introduit par
le lot C3, entièrement testable au travers des interfaces et doubles de C2.

> Doctrine : « Le cœur ne suppose jamais qu'une commande a réussi. Seule une
> relecture conforme permet d'émettre `applied`. »

C3 n'ajoute **aucun transport réel** : ni Paho, ni socket, ni sous-processus, ni
accès fichier, ni réseau. Le cœur ne parle qu'aux frontières C2 (`Clock`,
`VClient`, `MqttClient`). Aucune dépendance d'exécution n'est ajoutée.

## Architecture

Modules à responsabilité unique, sous `boilerack.core` :

| Module | Responsabilité |
|---|---|
| `command.py` | Décodage du payload brut + validation de FORME → `Command` immuable. |
| `ack.py` | Modèle d'ACK, statuts et raisons fermés, sérialisation JSON déterministe. |
| `profile.py` | Schéma déclaratif des rôles de commande (aucune donnée propriétaire). |
| `validation.py` | Validation générique pilotée par le profil, dans un ordre explicite. |
| `dedup.py` | `InFlightRegistry` (volatil) + `TerminalCache` (TTL monotone). |
| `engine.py` | `TransactionalCore` : orchestration admission → exécution → verdict. |

Le profil factice de test vit dans `boilerack.testing.fake_profile`.

## Modèle de commande

Séparation stricte : **décodage** → **validation de forme** → **validation
métier (profil)** → **exécution**. Le cœur ne reçoit jamais un dictionnaire non
validé dans sa partie d'exécution ; il ne manipule que des `Command` /
`ValidatedCommand` immuables.

Contraintes de forme (`parse_command`) : `request_id` UUID v4 canonique
minuscule ; `ts` / `expires_at` timezone-aware ; `source` / `role` non vides ;
`value` numérique **finie** ; booléen refusé ; `NaN` / `±Inf` refusés ; aucun
champ supplémentaire interprété.

## Modèle d'ACK

Statuts fermés : `accepted` (non terminal), `applied`, `rejected`, `timeout`
(terminaux). Classes de raison : `permanent`, `temporal`, `transient`.

| Raison | Classe | Origine |
|---|---|---|
| `invalid_payload` | permanent | forme / structure / rôle inconnu / rôle lecture seule |
| `invalid_type` | permanent | booléen, non nombre, ou non fini |
| `invalid_value_out_of_range` | permanent | hors `[min, max]` |
| `invalid_step` | permanent | hors grille `step` |
| `expired` | temporal | `now >= expires_at` |
| `bridge_unavailable` | transient | aucune écriture émise (démon injoignable) |
| `queue_full` | transient | file bornée saturée |
| `unsupported_command` | permanent | commande d'écriture non reconnue par le transport (C3, arbitrage 1.b) |

`reason` / `reason_class` ne sont présents **que** pour `rejected`. Chaque raison
a une classe **fixe** : on ne peut jamais construire un couple contradictoire.
Sérialisation JSON compacte, UTF-8, déterministe (clefs triées), `allow_nan=False`.

## Profil déclaratif

`CommandSpec` par rôle : `read`, `write` (ou `None` = lecture seule), `type`
(`integer`/`float`), `min`, `max`, `step`, `confirm_tolerance`, `idempotent`
(obligatoirement `True` en v1), `bounds_source` (provenance obligatoire des
bornes et du pas). **Aucune** adresse Optolink, longueur, ni code d'unité. Les
noms `read` / `write` sont des chaînes opaques transmises au transport.

## Ordre de validation

Ordre explicite et testé ; la **première** cause rencontrée emporte le verdict :

1. **forme** du payload (structure, UUID, dates aware) ;
2. **type** (booléen refusé, non nombre refusé) ;
3. **finitude** (`NaN` / `Inf` refusés) — étapes 1–3 portées par `parse_command` ;
4. **borne** (`min <= value <= max`) ;
5. **pas** (grille `min + k·step`) ;
6. **expiration** (`now >= expires_at`).

La **résolution du rôle** (rôle inconnu, rôle en lecture seule) précède les
bornes. **Priorité borne avant pas** (étape 4 < 5) : une valeur à la fois hors
borne et hors grille est rejetée pour `invalid_value_out_of_range`.

Doctrine ratifiée : **REJECT, jamais clamp** ; normalisation de représentation
seulement (`20.0` peut représenter l'entier `20`) ; `20.4` n'est **jamais**
arrondi et, hors grille, est rejeté. La comparaison de pas est **robuste**
(indice de grille le plus proche + `math.isclose`), jamais un modulo flottant naïf.

## Expiration

Vérifiée **à l'admission** puis **de nouveau immédiatement avant l'écriture**,
toujours via `Clock`, jamais via l'horloge système. Une commande qui expire
pendant son attente en file n'est **pas** écrite : verdict
`rejected / expired / temporal`.

## `in_flight` et cache terminal

Deux structures **distinctes**, **volatiles**, non persistantes :

- **`in_flight`** réserve les `request_id` admis, empêche un second travail dans
  la vie du processus, et est vidé d'un identifiant **uniquement** à la
  production de son verdict terminal ;
- **`TerminalCache`** associe `request_id → verdict terminal`, TTL **monotone**
  (défaut 60 s), purge déterministe (paresseuse à l'accès + `purge()` explicite),
  rejoue le verdict **sans réexécution**, et ne contient **jamais** `accepted`.

Doublons : identifiant en cache terminal → rejeu ; en `in_flight` → aucun second
travail, pas de nouveau `accepted` ; inconnu → admission normale. La dédup ne
s'applique qu'aux `request_id` canoniques (sans identité stable, pas de dédup).
Aucune mémoire n'est garantie après TTL ou redémarrage.

## File bornée

`BoundedQueue` est le **premier consommateur réel**. Admission : si une place
existe → réserver `request_id`, mettre en file, publier `accepted` ; si pleine →
**ne pas** réserver, publier `rejected / queue_full / transient`. FIFO à
l'exécution, profondeur et maximum observés exposés, aucun `accepted` pour une
commande refusée par saturation.

## Frontière écriture tentée / potentiellement émise (arbitrages 1.a / 1.b)

La décision repose sur le **statut typé** de `WriteResult`, jamais sur une
supposition :

| `WriteResult.status` | Émise ? | Verdict |
|---|---|---|
| `OK` | oui (acceptée) | relecture → `applied` / `timeout` |
| `TIMEOUT` | peut-être | relecture → `applied` / `timeout` |
| `UNUSABLE_OUTPUT` | peut-être | relecture → `applied` / `timeout` |
| `TRANSPORT_ERROR` | peut-être (prudence) | relecture → `applied` / `timeout` |
| `DAEMON_UNREACHABLE` | non | `rejected / bridge_unavailable / transient` |
| `UNKNOWN_COMMAND` | non (refus du démon) | `rejected / unsupported_command / permanent` |

On ne prétend jamais « non émise » sauf preuve typée (`DAEMON_UNREACHABLE`).
`unsupported_command` est un défaut **permanent** de profil / configuration /
compatibilité, distinct de `invalid_payload`.

## Confirmation par relecture

Générique. Entier : `read == target`. Flottant :
`abs(read - target) <= confirm_tolerance`. Valeur relue finie (garantie par le
`ReadResult` durci) ; aucune valeur par défaut, aucun clamp ; une lecture
invalide (non `OK`, y compris sortie `NaN`/inexploitable) ne confirme rien. Les
tentatives sont bornées par un **budget** monotone (défaut 5 s), séparées par un
**intervalle** (défaut 0,5 s) via `Clock.sleep` (jamais d'attente réelle).
Première relecture évaluée immédiatement ; budget épuisé → `timeout`. **Une seule
invocation d'écriture par transaction ; aucun retry d'écriture.**

## Publication des ACK (arbitrage 2, fail-closed)

Topic dérivé du rôle : `boilerack/ack/<role>`. QoS 1, non retained, payload JSON
compact. Ordre garanti : `accepted` **avant** le verdict terminal.

- **Échec établi de `accepted` avant l'écriture** (`PublishHandle.failed`) →
  **fail-closed** : la commande n'est **pas** exécutée, l'identifiant est retiré
  de `in_flight`, le verdict `rejected / bridge_unavailable / transient` est mis
  en cache puis publié (meilleur effort). Un handle simplement **demandé** (ni
  confirmé ni échoué) n'est **pas** un échec : l'écriture n'attend pas le PUBACK.
- Le verdict est décidé par le **fait physique** (relecture). Un échec de
  publication (accepted ou terminal) ne transforme jamais une commande en
  succès et n'est **pas** retenté : livraison MQTT et résultat physique sont deux
  faits distincts.

## Voie d'entrée MQTT

`MqttClient.set_message_handler(handler)` : couture minimale par laquelle le
transport remet chaque `Message` entrant (topic, payload brut, QoS, `dup`).
`TransactionalCore.attach()` y branche `submit`. Aucune session complète, aucun
Paho. Le pilotage de l'exécution (`process_next`) reste explicite ; le drapeau
`dup` est représenté mais n'altère pas la logique (la dédup se fait par
`request_id`).

## Réserves C2 traitées

1. **`ReadResult` durci** : `status is OK` ⟹ `value` présente et finie ;
   `status is not OK` ⟹ `value is None`. Rend un état contradictoire impossible.
2. **Entrée MQTT** : `set_message_handler` ajouté au protocole `MqttClient`,
   couvert par `FakeMqttClient`.
3. **Horloge** : gardes explicites `NaN` / `+Inf` / `-Inf` (et durée négative)
   centralisées, testées, sur horloge réelle et virtuelle.
4. **`boilerack.testing`** : conservé, **non** renommé ; reste interne et non
   stable. Décision définitive reportée avant toute prerelease.
5. **`TransportStatus`** : reste à **six** cas. Aucun statut ajouté pour
   atteindre un nombre ; `unsupported_command` est une **raison d'ACK**, pas un
   statut de transport.

## Décisions découvertes, surfacées pour ratification

- **Rôle inconnu** et **rôle en lecture seule** sont rejetés en
  `invalid_payload / permanent` (requête non recevable contre le profil, pré-
  transport). Une raison dédiée (`unknown_role` / `role_not_writable`) pourrait
  être introduite ultérieurement si une sémantique plus fine est souhaitée, sur
  le modèle de `unsupported_command`.
- **Valeur non finie** (`NaN` / `±Inf`) est rejetée en `invalid_type` (étape de
  finitude), le jeu de raisons ne comportant pas de raison de finitude dédiée.

## Hors périmètre C3

Aucun transport réel, aucun broker, aucun `subprocess`, aucun `vclient` réel,
aucun réseau, aucun systemd, aucune CLI, aucun Home Assistant, aucune découverte
MQTT, aucun profil de production complet, aucune publication PyPI.
