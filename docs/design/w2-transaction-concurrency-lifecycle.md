# W2 — Contrat de concurrence et de cycle de vie de la voie transactionnelle

> **Lot W2 — documentaire.** Aucune ligne de code, aucun test modifié, aucune
> voie runtime ouverte. Ce document fixe le **modèle d'exécution** dans lequel la
> future voie de commande pourra être câblée, et rien d'autre.
>
> **Version 2**, après audit indépendant de la V1 (verdict *À REVOIR* : 0
> bloquant, 3 majeurs, 11 mineurs). Le modèle général de la V1 est conservé ;
> §35 récapitule ce que la V2 corrige.
>
> **Erratum, postérieur au merge (PR #36).** §19.3.2 imposait au propriétaire de
> **consulter l'arrêt** entre l'admission et `process_next()`. Cette obligation
> était **sans effet observable** — la clause qui l'accompagnait prescrit
> l'exécution dans les deux cas — et donc invérifiable. Elle est **retirée**. La
> règle de comportement, elle, est **conservée intégralement** : une commande
> admise dans l'itération y est exécutée. Aucune autre clause n'est touchée.

---

## 1. Objet

W1 a contracté la **frontière MQTT** de la voie transactionnelle : quel topic,
quel QoS, quels ACK, quelle déduplication. Il a explicitement refusé de trancher
la **concurrence**, et en a dressé une liste fermée de onze invariants délégués
(W1 §20).

W2 traite cette liste, et elle seule. Il répond à une question unique, posée sous
plusieurs angles :

> **Dans quel contexte d'exécution la voie transactionnelle a-t-elle le droit de
> s'exécuter, à quelle cadence, et que devient-elle quand le processus démarre ou
> s'arrête ?**

W2 ne câble rien, ne crée aucune classe, ne nomme aucun module futur, et n'ouvre
aucune voie de commande.

---

## 2. Statut, autorité et portée

**Statut** — contrat de conception. Normatif pour W3 (câblage) sur les seuls
points de concurrence et de cycle de vie.

**Portée** — le modèle d'exécution de la composition future
`MQTT → admission → exécution → ACK`, tel qu'il devra s'insérer dans la boucle
déjà existante de C8/C9.

**Ce sur quoi W2 a autorité :**

- le contexte d'exécution autorisé pour chaque opération du cœur ;
- la couture entre le contexte de rappel MQTT et ce contexte, et sa capacité ;
- **la cadence d'admission et la place exacte de l'admission dans l'itération** ;
- la sérialisation des opérations `vclient` **au niveau de Boilerack** ;
- ce qui est admissible au démarrage et à l'arrêt.

**Ce sur quoi W2 n'a aucune autorité :** la surface MQTT (W1), la sémantique des
verdicts (C3), la cadence de lecture (C7-C3), l'unité systemd (C12/C13),
l'écriture réelle et le profil réel (W4).

**Clause de non-régression.** W2 **MUST NOT** modifier une clause de W0, W1, C3,
C7, C8, C9, C11, C12 ou C13. Si une décision de W2 paraissait l'exiger, la
décision est fautive, pas le contrat amont.

---

## 3. Autorités et acquis

| Autorité | Ce qu'elle fixe, et que W2 consomme sans le réécrire |
| --- | --- |
| **C3** — `c3-transactional-core.md` | Admission/exécution en deux temps ; taxonomie fermée `AckStatus` × `Reason` ; conclusion garantie **sur exception**, `accepted` avant le verdict terminal, cache avant publication. |
| **C6** | Une commande de lecture par invocation ; aucune issue de transport ne lève. |
| **C7-C3** — `c7c3b-read-publisher.md` | Le publieur ne boucle pas : l'appelant interroge `due_at()` puis appelle `run_due()`. |
| **C8** — `c8-composition-root.md` | `ReadSurfaceRunner` : `start()` → boucle → `stop()`. Un `run_due()` engagé n'est pas tronqué. |
| **C9** — `c9-process-lifecycle.md` | `SIGINT`/`SIGTERM` → arrêt propre par descripteur de réveil. **Aucune borne** sur la durée totale de sortie. |
| **C11** — `c11-presence-recovery.md` | `ConnectionState` : écriture depuis n'importe quel fil, consommation par **un seul**. |
| **C12** §10 | `TimeoutStopSec=90`, plancher de lecture `8 × 5,0 s = 40 s`, marge nominale 50 s. Inconnue I2 conservée. |
| **W0** | Registre interne de souscriptions, réémission après CONNACK réussi, aucune promesse de SUBACK. |
| **W1** | Topic de commande, QoS 1 entrant, préfixe d'ACK, `request_id` seule autorité de rejeu, instance MQTT unique, §14.2 (`expires_at` contre l'ancienneté), §20 (liste déléguée), §21 (obligations W3). |

**Acquis repris sans redémonstration :** `online` ≠ souscription active (W0 §11.2,
W1 §7.4) ; un verdict métier reste vrai même si l'ACK n'est pas livré (W1 §16) ;
une commande publiée pendant une coupure est perdue silencieusement (W1 §17.3) ;
une seule instance `MqttClient` en runtime (W1 §7.5) ; W3 **MUST NOT** modifier
`boilerack/core/` (W1 §21, MUST NOT n° 16).

---

## 4. Hors périmètre — liste fermée

W2 ne traite **aucun** des points suivants :

1. la syntaxe réelle d'une écriture `vclient`, et l'existence d'un adaptateur
   d'écriture (W4) ;
2. le profil réel, ses bornes et ses tolérances (W4) ;
3. la bascule terrain, son critère et son interrupteur (W4, porte terrain) ;
4. toute caractérisation du comportement de `vcontrold` ou de la chaudière ;
5. la coexistence avec l'ancien pont de production ;
6. le nom des modules, classes ou fonctions que W3 écrira ;
7. toute clause de W1 (topic, QoS, retain, ACK, dédup, SUBACK) ;
8. la modification de l'unité systemd ou de l'installeur ;
9. la création d'un statut, d'une `Reason`, ou d'un indicateur de santé.

---

## 5. Cartographie d'exécution — état mesuré du dépôt

Établie par lecture du code à la base `786e199`. Colonne « active » = appelée
aujourd'hui par du code de **production** (`src/`), hors tests.

| Opération | Appelant actuel | Contexte | Bloquante ? | État partagé ? | Active ? | Autorité |
| --- | --- | --- | --- | --- | --- | --- |
| `PahoMqttClient._on_message` | Paho, en ligne | **fil réseau Paho** | NON | `_handler` (lu sans verrou) | **NON** — aucun handler enregistré en production | C4, W1 §11 |
| `set_message_handler` | tests (`test_mqtt_paho.py`, `test_integration_offline.py`, `test_observability.py`) | quelconque | NON | `_handler` (écrit sans verrou) | **NON** | C4, W1 §20.10 |
| `TransactionalCore.attach` | **tests uniquement** — `tests/core/test_reserves_c2.py:68` et `:78` | celui de l'appelant | NON | `_handler` du client | **NON** | C3, W1 §11.4 |
| `TransactionalCore.submit` | tests seulement | celui du rappel | **PARTIEL** — publie `accepted` (E/S réseau), n'attend aucun PUBACK | file, `in_flight`, cache terminal, MQTT | **NON** | C3 |
| admission interne `_admit` | `submit` | idem | PARTIEL | idem | NON | C3 |
| `process_next` | tests seulement | celui de l'appelant | **OUI** — écriture + boucle de confirmation avec `clock.sleep` | file, `in_flight`, cache, `vclient`, MQTT | **NON** | C3 |
| `drain` | tests seulement (`tests/core/test_queue.py`) | idem | **OUI** ; bornée en nombre, non en durée (§8.2) | idem | **NON** | C3 |
| `_run_transaction` / `_confirm` | `process_next` | idem | **OUI** | `vclient`, horloge | NON | C3 |
| publication `accepted` | `_admit` | celui du rappel | PARTIEL | client MQTT | NON | W1 §12 |
| publication terminale | `_conclude` | celui de `process_next` | PARTIEL | client MQTT | NON | W1 §12 |
| lecture `vclient` (télémétrie) | `ReadSurfacePublisher.run_due` | **fil principal** | **OUI** — `subprocess.run(timeout=read_timeout_s)` | aucun verrou | **OUI** | C6, C7-C3 |
| `run_due()` | `ReadSurfaceRunner._boucler` | **fil principal** | **OUI** | état du publieur, `ConnectionState` | **OUI** | C7-C3, C8 |
| reconnexion MQTT (`_on_connect`) | Paho, en ligne | **fil réseau Paho** | NON | `ConnectionState` (verrouillé), registre W0 (verrouillé) | **OUI** | C11, W0 |
| démarrage (`publisher.start`) | `runner.run` | fil principal | OUI | — | OUI | C7-C3A, C8 |
| arrêt (`publisher.stop`) | `runner.run` | fil principal | OUI | — | OUI | C8 |
| `SIGTERM` / `SIGINT` | noyau → `set_wakeup_fd` | **niveau C**, puis drainage sur le fil qui interroge | NON | descripteur de réveil | **OUI** | C9 |

### 5.1 Preuve que le cœur n'a aucune instance en production

La V1 annonçait un `grep` qui **ne produit pas** le résultat annoncé : la
définition s'écrit `class TransactionalCore:`, sans parenthèse, donc
`grep -rn "TransactionalCore(" src/` ne renvoie **rien du tout**. Preuve
corrigée, par recherche du **nom seul** dans tout `src/` :

```
src/boilerack/core/engine.py:97      class TransactionalCore:
src/boilerack/core/__init__.py:29    from boilerack.core.engine import TransactionalCore
src/boilerack/core/__init__.py:43        "TransactionalCore",
```

Trois occurrences : **une définition et deux ré-exports**. Aucune
**instanciation** nulle part dans `src/`. La voie est entièrement latente — la
conclusion de la V1 tient, sa preuve était fautive.

### 5.2 Trois faits saillants

1. **Rien de transactionnel n'est actif en production** (§5.1).
2. **Deux contextes existent déjà** et sont réellement actifs : le fil principal
   (boucle du runner, lectures `vclient`) et le fil réseau de Paho (rappels de
   connexion, W0). Ils se rencontrent aujourd'hui en **un seul point**, protégé :
   `ConnectionState`.
3. **La seule opération bloquante active** est la lecture `vclient`, bornée par
   `subprocess.run(timeout=…)` et exécutée **séquentiellement** sur le fil
   principal.

---

## 6. Le callback Paho — faits mesurés

W1 §11.5 constate que `submit` s'exécuterait « sur le fil réseau de Paho » sans
en tirer de clause. W2 fonde cette affirmation avant de décider.

**Fait 1 — le mode utilisé est le mode threadé.** `PahoMqttClient.connect()`
appelle `self._client.loop_start()` après `client.connect(...)`.

**Fait 2 — `loop_start()` crée un fil.** Mesuré sur la dépendance réellement
installée (`paho-mqtt 2.1.0`, déclarée `paho-mqtt>=2.1,<3`) :

```python
self._thread = threading.Thread(target=self._thread_main,
                                name=f"paho-mqtt-client-{...}")
self._thread.daemon = True
self._thread.start()
```

**Fait 3 — un seul fil, aucune file de rappels.** Dans tout
`paho.mqtt.client`, une seule construction `threading.Thread` existe, et les
motifs `callback_queue`, `Queue(`, `callback_thread`, `ThreadPool` ont **zéro**
occurrence. `_handle_on_message` invoque le rappel utilisateur **en ligne**, sous
`_in_callback_mutex`.

**Fait 4 — publier depuis un rappel ne s'auto-bloque pas en mode threadé.**
`Client.publish` ne prend que `_out_message_mutex`. Le seul point où
`_packet_queue` touche `_in_callback_mutex` est gardé par `if self._thread is
None`, donc **inatteignable** en mode `loop_start()`, et l'acquisition y est de
toute façon non bloquante. Publier `accepted` depuis `on_message` est donc
**techniquement permis** : ce qui est possible n'est pas ce qui est souhaitable
(§12).

**Fait 5 — un rappel bloquant gèle le keepalive.** Chaîne mesurée :
`_thread_main` → `loop_forever` → `_loop` → `loop_misc()` → `_check_keepalive()`
→ `_send_pingreq()`. Les rappels étant invoqués **en ligne** dans `_loop`
(fait 3), un rappel qui n'en finit pas empêche `loop_misc()` d'être atteint : le
PINGREQ n'est plus émis et le broker déconnecte à l'expiration du keepalive. Ce
mécanisme fonde §13 et l'écartement de l'option A-1(c) en §11.1.

**Fait 6 — `loop_stop()` ne garantit pas l'émission des paquets en attente.** Sa
documentation l'écrit : « This don't guarantee that publish packet are sent ». Or
`PahoMqttClient.disconnect()` appelle `loop_stop()` **puis** `disconnect()`.
Conséquence en §22.4.

---

## 7. `submit()` — ce qui est synchrone avant le retour

| # | Étape | Effet | Peut publier ? | Peut attendre ? | Écrit la chaudière ? |
| --- | --- | --- | --- | --- | --- |
| 1 | `extract_request_id` + canonicité | pur | non | non | **non** |
| 2 | `TerminalCache.get` | **mute** le cache (purge à l'expiration) | non | non | non |
| 3 | rejeu d'un verdict en cache | — | **OUI** | non | non |
| 4 | `InFlightRegistry.contains` | lecture d'un `set` | non | non | non |
| 5 | `validate(...)` — **dont `now >= expires_at`** | pur | non | non | non |
| 6 | rejet de validation | **mute** le cache | **OUI** | non | non |
| 7 | contrôle de saturation `queue_full` | **mute** cache + `in_flight` | **OUI** | non | non |
| 8 | `in_flight.reserve` | **mute** un `set` | non | non | non |
| 9 | publication de `accepted` | — | **OUI** | non — le PUBACK n'est **pas** attendu | non |
| 10 | `queue.put` | **mute** la file | non | non | non |
| 11 | retour | `Ack \| None` | — | — | — |

**Trois constats normatifs.**

- **`submit` n'écrit jamais la chaudière.** Aucune branche n'appelle
  `vclient.write`.
- **`submit` publie, mais n'attend jamais.** Aucune branche ne bloque : le handle
  est consulté (`handle.failed`) sans attente de PUBACK. Sa durée est bornée par
  la mise en file locale du paquet MQTT.
- **`submit` mute quatre structures non protégées** : `TerminalCache` (`dict`),
  `InFlightRegistry` (`set`), `BoundedQueue` (`deque`), et l'état interne du
  client MQTT. *La V1 en annonçait cinq et n'en listait que quatre ; le compte
  exact est **quatre**.*

**W2 ne redéfinit pas C3.** Il ne change ni l'ordre, ni la sémantique, ni les
verdicts de cette séquence. Il contracte **où** et **quand** elle s'exécute.

---

## 8. `process_next()`, `drain()` et `run_due()`

### 8.1 `process_next()`

Bloquante : elle appelle `vclient.write` puis `_confirm`, qui boucle
`read` / `clock.sleep(confirm_interval_s)`. Une seule transaction par appel.
Publie le verdict terminal via `_conclude`.

**Bornes, qualifiées avec exactitude :**

| Composante | Statut | Valeur |
| --- | --- | --- |
| boucle de confirmation | **borne stricte prouvée** — le contrôle d'échéance suit la lecture, et le sommeil d'intervalle s'exécute **après** ce contrôle : une dernière lecture entière peut donc commencer au-delà de l'échéance | `confirm_budget_s + confirm_interval_s + read_timeout_s` = **10,5 s** aux défauts |
| invocation d'écriture | **NON BORNÉE** — aucun adaptateur d'écriture n'existe et `write_timeout_s` n'est **consommé nulle part** | *non démontrable* |
| **total d'une transaction** | **NON BORNÉ** | *non démontrable* |

### 8.2 `drain()`

`drain()` **existe** et appelle `process_next()` jusqu'à ce que la file soit
vide.

- **borne en NOMBRE : oui** — au plus `queue_depth ≤ queue_capacity`, soit **16**
  au défaut. Sous le modèle à propriétaire unique (§12), rien ne peut alimenter
  la file pendant le drainage, donc la boucle termine.
- **borne en DURÉE : non** — elle hérite de la non-borne de l'écriture (§8.1).

*La V1 écrivait « non borné » sans qualifier ; c'était inexact en nombre.*

### 8.3 `run_due()`

Appartient au **publieur de lecture**, jamais au cœur. Appelé par
`ReadSurfaceRunner._boucler()` sur le fil principal. Lit les mesures dues
**séquentiellement** ; ne boucle pas.

**Majorant conditionnel :** `nombre de mesures dues × read_timeout_s`, soit
`8 × 5,0 = 40 s` aux défauts (C12 §10). Conditionnel parce que `read_timeout_s`
est réglable par l'exploitant (C10).

### 8.4 Ordre relatif aujourd'hui

**Il n'existe pas.** Les deux méthodes appartiennent à deux objets qui ne se
rencontrent nulle part dans `src/`. W2 le fixe en §13.

---

## 9. Mutabilité du cœur — aucune sûreté entre fils

| Structure | Implémentation | Verrou | Sûre entre fils ? |
| --- | --- | --- | --- |
| `BoundedQueue` | `collections.deque` nu | **aucun** | **non déclarée** |
| `InFlightRegistry` | `set` nu | **aucun** | **non déclarée** |
| `TerminalCache` | `dict` nu + horloge | **aucun** | **non déclarée** |
| `Profile` | figé à la construction | — | lecture seule |
| `Clock` | injectée | — | dépend de l'implémentation |
| publieur MQTT | `PahoMqttClient` | verrou interne | oui, pour sa propre corrélation |

`TransactionalCore` n'importe pas `threading` et ne détient aucun verrou.

**Deux courses concrètes, si deux fils y accédaient :**

1. `TerminalCache.get()` exécute `if monotonic() >= deadline: del
   self._entries[request_id]`. Deux fils franchissant le test lèveraient un
   `KeyError` au second `del` — exception qui, depuis `submit`, remonterait dans
   `_on_message`, où elle serait **journalisée puis avalée**, laissant la commande
   sans admission et sans ACK.
2. La séquence `cache.get` → `in_flight.contains` → `in_flight.reserve` est un
   *check-then-act* sur trois structures indépendantes. Deux doublons concurrents
   pourraient **tous deux** réserver, et produire deux `accepted` puis deux
   écritures — ce que `request_id` est précisément censé empêcher (W1 §13).

---

## 10. Trous contractuels comblés par W2

| # W1 §20 | Question | Traitée en |
| --- | --- | --- |
| 1 | Quel fil exécute `submit` | §12 |
| 2 | Faut-il une file inter-fils | §14 |
| 3 | `accepted` peut-il être publié depuis `on_message` | §12 |
| 4 | Quel verrouillage protège cache / `in_flight` / file | §9, §11.1, §12 |
| 5 | Qui appelle `process_next` / `drain`, **à quelle cadence**, depuis quel fil | §12, **§13** |
| 6 | **Entrelacement exact** avec `run_due()` et l'attente du runner | **§13**, §17 |
| 7 | Sérialisation lectures / écriture sur le même `vclient` | §15 |
| 8 | Sort d'une transaction en vol pendant `SIGTERM` | §19, §20 |
| 9 | Effet sur `TimeoutStopSec` et les latences C9 | §22 |
| 10 | `_handler` écrit et lu sans verrou | §18.3 |
| 11 | Ordre de livraison des ACK publiés depuis des fils différents | §12.2 |

Les points **5** et **6**, laissés ouverts par la V1, sont **fermés** par la
décision de cadence et d'ordre de §13. Aucun autre trou n'est ouvert par W2.

---

## 11. Arbitrages

| # | Question | Options examinées | Décision | Fondement |
| --- | --- | --- | --- | --- |
| **A-1** | Comment protéger les mutations du cœur ? | (a) verrous **dans** le cœur ; (b) propriétaire unique ; (c) verrou de sérialisation **dans la couche de câblage**, sans toucher au cœur | **(b)** | §11.1 |
| **A-2** | Quel est le contexte propriétaire ? | (a) fil dédié nouveau ; (b) le fil principal, déjà propriétaire de la boucle | **(b)** | Le fil principal exécute déjà `run_due()` et **toutes** les opérations `vclient`. Un fil dédié recréerait la sérialisation qu'il prétend résoudre. |
| **A-3** | Couture rappel → propriétaire | (A) appel direct ; (B) dépôt inter-fils borné ; (C) primitive existante du dépôt | **(B)** | (A) viole A-1 ; (C) échoue : `ConnectionState` est un booléen idempotent sans historique, `BoundedQueue` n'est pas sûre entre fils. §14.2 |
| **A-4** | Le dépôt saturé bloque-t-il le fil Paho ? | (a) attente ; (b) rejet non bloquant | **(b)** | Bloquer le fil réseau gèlerait `_on_connect`, la reprise C11, la restauration W0 **et le keepalive** (fait 5). |
| **A-5** | Capacité du dépôt | (a) bornée, capacité arbitraire ; (b) bornée, plancher relié à `queue_capacity` ; (c) non bornée ; (d) autre couture | **(b)** | §16 |
| **A-6** | Cadence d'exécution | (a) `drain()` ; (b) **au plus une** `process_next()` par itération | **(b)** | §8.2 : `drain()` hérite d'une durée non bornée et rend le plancher d'arrêt indémontrable. |
| **A-7** | **Cadence d'admission** | (a) admettre tout le dépôt disponible ; (b) admettre au plus **K > 1** ; (c) admettre au plus **une** | **(c)** | §13.1 |
| **A-8** | **Place de l'admission** | (a) `run_due` → `process_next` → admission ; (b) admission → `run_due` → `process_next` ; (c) `run_due` → **admission** → `process_next` | **(c)** | §13.2 |
| **A-9** | Horloge du cœur | (a) horloge propre ; (b) **la même instance** que runner et publieur | **(b)** | Précédent explicite de `build_runtime` : « sans quoi le temps du runner et celui du publieur pourraient diverger ». |
| **A-10** | Commande admise non exécutée à l'arrêt | (a) drain complet ; (b) verdict de substitution ; (c) abandon, énoncé et **borné** | **(c)** | §20 |

### 11.1 A-1 — les trois options, dont celle que la V1 avait omise

**(a) Verrous dans `boilerack/core/`.** **Interdit** : W1 §21 (MUST NOT n° 16)
interdit à W3 de modifier `boilerack/core/`. L'option n'est pas jugée, elle est
inapplicable.

**(c) Verrou de sérialisation dans la couche de câblage.** *Cette option existe
et la V1 l'avait omise.* Elle est **permise** — elle ne touche pas au cœur. Elle
est néanmoins **écartée**, pour un motif mécanique et non esthétique :

> Pour protéger réellement les structures du cœur, le verrou devrait couvrir non
> seulement `submit` mais aussi `process_next`, dont la durée est **non bornée**
> (§8.1). Un rappel MQTT qui tenterait d'acquérir ce verrou pendant une
> transaction resterait bloqué **sur le fil réseau de Paho**. Or ce fil sert le
> keepalive **en ligne** (fait 5) : le PINGREQ cesserait d'être émis et le broker
> déconnecterait le pont. Un verrou de câblage transforme donc une contention
> transactionnelle en **perte de connexion MQTT**.

**(b) Propriétaire unique.** Retenue. Elle obtient la même sûreté sans verrou et
sans exposer le fil réseau à une attente.

> **Formulation exacte.** Le propriétaire unique n'est pas « la seule voie
> possible » — la V1 l'écrivait à tort, en oubliant (c). C'est **l'option la plus
> sobre, et la seule retenue**.

---

## 12. Modèle de concurrence — le propriétaire unique

### 12.1 Clause

> **Un seul contexte d'exécution — le *propriétaire* — a le droit d'appeler
> `TransactionalCore.submit`, `process_next` et `drain`, et d'accéder à
> `vclient`.** Ce propriétaire est le **fil qui exécute la boucle du runner**,
> c'est-à-dire le fil principal au sens de C9.

**Corollaires normatifs.**

1. Le contexte de rappel MQTT **MUST NOT** appeler `submit`, `process_next`,
   `drain`, ni aucune méthode mutante du cœur.
2. `TransactionalCore.attach()` **MUST NOT** être utilisé en runtime : il
   enregistre `submit` comme gestionnaire, donc l'exécuterait sur le fil de
   rappel. Il reste utilisable en test hors ligne, où un seul fil existe — c'est
   déjà son unique usage, dans `tests/core/test_reserves_c2.py` (l. 68 et 78).
   *La V1 attribuait cet usage à `test_integration_offline.py`, qui n'appelle
   jamais `attach()` : il câble directement `mqtt.set_message_handler(core.submit)`.*
3. Aucun verrou **MUST NOT** être ajouté à `boilerack/core/` — rappel de W1
   §21.16, non une clause propre à W2.

### 12.2 Ce que ce choix résout

- **W1 §20.4** — cache terminal, `in_flight` et file bornée n'ont besoin d'aucun
  verrou : un seul fil les touche.
- **W1 §20.3 et §20.11** — `accepted` et le verdict terminal sont publiés depuis
  le **même** contexte, dans l'ordre de demande déjà garanti par construction
  (W1 §11.5). La question de l'ordre de livraison entre fils **disparaît** au lieu
  d'être arbitrée.
- **W1 §20.7** — la sérialisation `vclient` devient structurelle (§15).

---

## 13. Cadence et place de l'admission — la décision centrale de la V2

La V1 laissait ces deux questions ouvertes ; l'audit a établi que les points
W1 §20.5 et §20.6 restaient de ce fait **non fermés**. La V2 les tranche.

### 13.1 Cadence — au plus une admission par itération

Trois options (A-7), évaluées sur le comportement de la profondeur de la file du
cœur, en régime nominal, avec **une** exécution par itération (A-6) :

| Option | Variation de profondeur par itération | Conséquence |
| --- | --- | --- |
| (a) admettre tout le dépôt | `+N − 1` | la file croît jusqu'à `queue_capacity` ; jusqu'à **16** `accepted` sans verdict terminal exposés à l'arrêt |
| (b) admettre au plus `K > 1` | `+K − 1` | même divergence, plus lente ; `K` serait un nombre arbitraire de plus |
| **(c) admettre au plus une** | **`+1 − 1 = 0`** | la profondeur **revient à zéro** à la fin de chaque itération |

**Décision : (c).** Le fondement n'est pas la simplicité mais la **stabilité** :
c'est la seule cadence pour laquelle l'admission n'alimente pas le cœur plus vite
que l'exécution ne le vide. Toute cadence `> 1` fait diverger la file par
construction, et l'exposition « `accepted` sans terminal » croît avec elle.

**Conséquence exacte, à énoncer plutôt qu'à taire.** Le dépôt se vide à raison
d'**un message par itération**. Une rafale s'écoule donc lentement, et une
commande peut atteindre son `expires_at` en attente. Elle sera alors rejetée
`expired` à l'admission — comportement C3 nominal, et **rempart voulu** : W1
§14.2 établit déjà que « le danger réel est l'ancienneté », et que `expires_at`
en est la garde. W2 ne fabrique aucune garde supplémentaire.

**Conséquence sur `queue_full`.** Avec une admission et une exécution par
itération, la profondeur de la file du cœur ne dépasse jamais **1**, très en
dessous de `queue_capacity = 16`.

> **Énoncé sans détour.** Sous la cadence V2, le verdict `queue_full` de C3
> devient **inatteignable en régime nominal**. La contre-pression ne se manifeste
> donc plus dans `submit()` mais au **dépôt** (§16). W2 ne prétend pas le
> contraire, et n'en tire aucune conséquence sur C3 : `queue_full` reste une
> sécurité du cœur, qui redeviendrait atteignable si un lot futur changeait la
> cadence. Il **MUST NOT** être retiré.

### 13.2 Place — `run_due()` → admission → `process_next()`

Trois options (A-8) :

**(a) `run_due` → `process_next` → admission.** La commande admise attend
l'itération **suivante** pour être exécutée. La profondeur en fin d'itération vaut
1 au lieu de 0, et le délai entre `accepted` et le verdict terminal augmente d'une
itération entière. **Écartée.**

**(b) admission → `run_due` → `process_next`.** L'admission est prompte, et son
coût pour C11 est négligeable puisque `submit` n'attend jamais (§7). Mais
`accepted` serait publié **jusqu'à un `run_due()` entier avant** toute exécution —
soit un majorant conditionnel de 40 s aux défauts — sans que la latence
d'**exécution** en soit améliorée : `run_due()` s'intercale de toute façon avant
`process_next()`. Cette option **élargit la fenêtre `accepted` → terminal sans
rien gagner**. Elle inverserait en outre la priorité donnée à la reprise de
présence C11, qui est l'étape 0 de `run_due()`. **Écartée.**

**(c) `run_due` → admission → `process_next`.** **Retenue.** Quatre raisons :

1. la reprise de présence C11 conserve la **priorité absolue** — inchangé depuis
   la V1 ;
2. admission et exécution deviennent **adjacentes** : la fenêtre entre `accepted`
   et le verdict terminal est la plus étroite des trois options, ce qui est la
   lecture honnête de `accepted` — « je m'apprête à le faire », non « je le ferai
   dans un moment indéterminé » ;
3. la profondeur de la file **revient à zéro** en fin d'itération (§13.1) ;
4. la latence d'**exécution** est identique à (b), `run_due()` précédant
   `process_next()` dans les deux cas.

### 13.3 Ordre d'itération normatif

> **Clause.** Une itération du propriétaire exécute, dans cet ordre exact :
>
> ```text
> consulter l'arrêt
> attendre jusqu'à due_at()
> consulter l'arrêt
> run_due()                        ← C11 étape 0, lectures dues
> admettre AU PLUS UN message du dépôt, s'il y en a un   ← submit()
> process_next() AU PLUS UNE FOIS                        ← exécution
> ```
>
> Cet ordre est **normatif et testable**. Les trois premières lignes sont celles
> de C8, inchangées.

**Ce que §13.3 fixe entièrement.** L'itération ne comporte que les **deux**
consultations d'arrêt héritées de C8. Aucune consultation supplémentaire n'est requise
entre l'admission et `process_next()` : §19.3.2 prescrit le **comportement** — la
commande admise est exécutée dans l'itération — sans exiger d'observation
supplémentaire.

---

## 14. La couture rappel → propriétaire

### 14.1 Clause

> Le contexte de rappel **MUST** se limiter à **déposer** le `Message` **brut**
> dans une structure de transfert, et rendre la main.

Le dépôt **MUST** : être **sûr entre fils** ; être **borné** (§16) ; **ne jamais
bloquer** le fil de rappel (A-4, fait 5) ; transporter le `Message` **tel quel**,
sans décodage ni filtrage (W1 §11.3).

Le dépôt **MUST NOT** : publier sur MQTT, lire `vclient`, toucher une structure du
cœur, ni prendre un verrou du cœur.

### 14.2 Pourquoi aucune primitive existante ne convient

- **`ConnectionState`** porte un booléen idempotent sans historique ; son propre
  docstring l'écrit : « Ni une file — la seule information utile est *une reprise
  est-elle due* ». Il ne peut pas transporter N messages distincts.
- **`SignalStop`** est le même patron sur un descripteur d'octets : il compte des
  signaux, il ne transporte pas de charge utile.
- **`BoundedQueue`** a la bonne forme mais **pas** la sûreté entre fils (§9), et
  la durcir signifierait modifier `boilerack/core/`, interdit à W3.

W2 **ne crée aucune classe** et **ne nomme aucun module**. Il note seulement, pour
écarter le soupçon d'overengineering, que la bibliothèque standard offre déjà une
file bornée et sûre entre fils : **aucune primitive nouvelle n'a à être
inventée**.

---

## 15. Sérialisation `vclient`

### 15.1 État mesuré

Un seul appelant existe : `ReadSurfacePublisher.run_due()`, qui lit
**séquentiellement**, sur le fil principal, chaque lecture bornée par
`subprocess.run(timeout=read_timeout_s)`. **Aucun verrou**, et aucun n'est
nécessaire : il n'y a qu'un fil.

Côté écriture : `VClient` (Protocol) déclare `read` **et** `write`, mais
`VClientCliReader` — le seul adaptateur réel — n'implémente que `read`. **Aucun
`write` réel n'existe.** `VclientConfig.write_timeout_s` est déclaré et validé,
mais **consommé nulle part**, et absent des clés de configuration exposées.

### 15.2 Clause

> **Deux opérations `vclient` ne sont jamais simultanées dans Boilerack.**

Sous §12 et §13.3, cette propriété est **structurelle** : lectures de télémétrie et
écriture transactionnelle appartiennent au même propriétaire et occupent des
positions distinctes de la même itération. Aucun verrou n'est requis, et aucun
**MUST NOT** être ajouté pour l'obtenir.

### 15.3 Ce que cette clause n'affirme pas

Elle porte sur **Boilerack**, jamais sur `vcontrold`, dont le comportement sous
accès concurrent est **INCONNU** (§32, I1). La sérialisation est adoptée parce
qu'elle est gratuite sous §12 et prudente en l'absence d'autorité, **non** parce
qu'une caractérisation l'imposerait.

### 15.4 One-writer — le bon niveau, et le mauvais

| | Énoncé | Statut |
| --- | --- | --- |
| **A** | Un seul appel `vclient` actif à la fois **dans Boilerack** | **Contracté** (§15.2) |
| **B** | Un seul système au monde autorisé à écrire la chaudière | **Hors périmètre** |

**B** relève de la porte terrain. W1 §23 a refusé de la concevoir ; W2 la refuse
pour la même raison. **Aucun terrain n'est touché.**

---

## 16. Capacité du dépôt et gouvernance de la saturation

L'audit a jugé la V1 « non gouvernée » sur ce point : elle imposait un dépôt
borné sans dire **par quoi** sa capacité est décidée. La V2 le tranche.

### 16.1 Les quatre options

| Option | Sûreté mémoire | À saturation | Rapport à `queue_full` | Perte silencieuse | Fil Paho | Arrêt |
| --- | --- | --- | --- | --- | --- | --- |
| **A** — bornée, capacité arbitraire | oui | rejet | aucun | **possible dès 1 message** si la capacité est mal choisie | sain | sans effet |
| **B** — bornée, plancher `≥ queue_capacity` | oui | rejet | aucun sous la cadence V2 (§13.1) | possible, mais **exceptionnelle et gouvernée** | sain | sans effet |
| **C** — non bornée | **non** — surface d'épuisement mémoire alimentée par le réseau | croissance | aucun | jamais | sain | croissance conservée |
| **D** — pas de dépôt, dernier message conservé | oui | écrasement | aucun | **systématique** — les commandes ne sont pas idempotentes | sain | sans effet |

**C est écartée** : une file alimentée par le réseau et sans borne est une surface
d'épuisement mémoire, et tout le dessin de C3 repose au contraire sur du travail
**borné** (`BoundedQueue`, `queue_capacity`). **D est écartée** : écraser une
commande par la suivante détruirait des demandes distinctes — l'idempotence de
`ConnectionState` ne se transpose pas. **A est écartée** : c'est exactement le
défaut relevé par l'audit.

### 16.2 La suggestion de l'audit, vérifiée puis nuancée

L'audit suggérait `capacité dépôt ≥ queue_capacity` afin que la saturation
« normale » se manifeste dans `submit()` comme `queue_full` plutôt que comme perte
avant admission. **Vérification faite : cela ne suffit pas, et ne peut pas
suffire.**

> Sous la cadence de §13.1, la profondeur de la file du cœur ne dépasse jamais
> **1**. `queue_full` est donc **inatteignable quelle que soit la capacité du
> dépôt**. Aucun dimensionnement ne peut faire apparaître la contre-pression dans
> `submit()`, parce que ce n'est pas la file du cœur qui se remplit.

La suggestion est donc **retenue comme plancher**, mais pour un autre motif que
celui qui la portait.

### 16.3 Clause

> **Le dépôt est borné. Sa capacité MUST être ≥ `queue_capacity` du cœur, et MUST
> être une constante nommée, exposée à la relecture, accompagnée par W3 de
> l'hypothèse de débit d'arrivée qui la justifie.**

**Fondement du plancher.** `queue_capacity` est la **seule** grandeur du dépôt
qui exprime combien de commandes en attente Boilerack est conçu à retenir.
Dimensionner le tampon de transport en dessous ferait du transport le facteur
limitant dans **toute** cadence — y compris une cadence future différente de celle
de §13.1. C'est un plancher qui **survit à un changement de cadence**, et c'est à
ce titre qu'il est retenu.

**Ce que W2 ne fait pas :** fixer un nombre. Le débit d'arrivée réel des commandes
n'est dérivable ni du dépôt ni d'aucune autorité ; inventer une capacité serait
remplacer un arbitraire par un autre. W2 contracte la **règle** et le
**plancher** ; W3 choisit la valeur **et écrit l'hypothèse** qui la justifie.

### 16.4 Débordement — ce qu'il est, et ce qu'il n'est pas

Un message rejeté à la saturation du dépôt **MUST NOT** produire d'ACK, et
**MUST** être journalisé.

> **Cette perte n'est PAS assimilable à la fenêtre de coupure de W1 §17.3.** Là,
> le pont est **déconnecté** ; ici, il est **connecté et sain**. Les assimiler
> masquerait un défaut de dimensionnement derrière une fatalité de transport.

Description exacte de la situation :

- le message a été **reçu** par le pont ;
- il n'a **pas** été admis ;
- **aucun** `request_id` n'est connu du cœur ;
- **aucun** `accepted`, **aucun** verdict terminal ;
- **aucune** promesse de C3 n'est engagée — C3 ne parle que de transactions
  **admises**.

Le demandeur ne peut pas la distinguer d'un ACK perdu (W1 §16). Sa conduite reste
la même : réémettre sous un **nouveau** `request_id`, et traiter `expires_at`
comme borne de sûreté.

> **Clause de gouvernance.** Ce débordement **MUST** rester exceptionnel. Une
> capacité qui le rendrait ordinaire — au premier plan, une capacité de 1 —
> violerait §16.3.

---

## 17. Latence d'admission — décomposition, sans borne inventée

La V1 annonçait une latence « bornée par la prochaine échéance du publieur ».
**C'était faux** : cette borne ne couvrait que l'attente, et omettait le travail
qui la précède dans l'itération.

### 17.1 Décomposition

Sous l'ordre de §13.3, l'admission d'un message déposé pendant l'itération *N−1*
est précédée de :

| # | Composante | Statut | Valeur |
| --- | --- | --- | --- |
| 1 | fin du `process_next()` de l'itération précédente | **NON BORNÉ** | hérite de la non-borne d'écriture (§8.1) |
| 2 | attente jusqu'à `due_at()` | **borné** | ≤ la plus petite période configurée de la surface de lecture (C7-C3) |
| 3 | durée de `run_due()` | **majorant conditionnel** | `mesures dues × read_timeout_s` = 40 s aux défauts ; conditionnel car `read_timeout_s` est réglable |
| 4 | l'admission elle-même | **borné** | `submit` n'attend jamais (§7) |

### 17.2 Clause

> **W2 ne revendique aucune borne de latence d'admission.** Tant que
> `VClient.write` n'a aucune borne consommée, la composante 1 est **non bornée**,
> donc la somme l'est aussi. Aucun nombre ne remplace celui, faux, de la V1.

**Énoncé conditionnel, seul énoncé possible aujourd'hui :** *en l'absence de toute
transaction en cours d'exécution*, la latence d'admission se réduit aux
composantes 2 à 4, soit un **majorant conditionnel** de « plus petite période
configurée + `mesures dues × read_timeout_s` ». Ce majorant devient une borne le
jour où une écriture bornée existera (§32, I2).

**Aucun SLO n'est créé.** W2 ne promet pas de latence, ne la mesure pas, et
n'introduit aucun indicateur pour la surveiller.

---

## 18. Cycle de vie — démarrage

### 18.1 États distingués

| État | Signification exacte | Suffit-il à admettre ? |
| --- | --- | --- |
| objet construit | `TransactionalCore(...)` existe | **non** |
| gestionnaire attaché | le transport sait où déposer | non |
| souscription **demandée** | `subscribe()` appelé ; W0 a enregistré l'intention | non — ne prouve aucune acceptation broker (W0 §11.2, W1 §7.4) |
| MQTT **connecté** | CONNACK réussi observé ; **la réception et le dépôt sont possibles** | non |
| **propriétaire en régime d'itération** | la boucle de §13.3 tourne | **OUI** |
| `vclient` utilisable | démontrable seulement à l'usage | non — jamais démontrable à l'avance |

### 18.2 Clause, et son vrai fondement

> **Aucune admission n'a lieu avant l'entrée du propriétaire dans le régime
> d'itération de §13.3.**

*La V1 qualifiait cette clause d'« auto-réalisatrice ». C'était un raisonnement
faux :* que seul le propriétaire appelle `submit` n'implique pas qu'il n'admettra
pas trop tôt — il pourrait le faire pendant `start()`, avant sa première
itération. La clause est donc une **règle réelle**, qui interdit d'admettre
ailleurs que dans la position prévue par §13.3.

**Ce qui protège une commande devenue trop ancienne** n'est pas cette règle mais
`expires_at`, revalidé **deux fois** :

1. à l'admission — `validate()` rejette `expired` si `now >= expires_at`
   (`core/validation.py`) ;
2. **immédiatement avant l'écriture** — `_run_transaction` re-teste
   `self._clock.now() >= validated.command.expires_at`.

C'est la garde que W1 §14.2 désigne déjà : « le danger réel est l'ancienneté, pas
la rétention ». **Aucun indicateur de disponibilité n'est créé**, et W2 **MUST
NOT** faire signifier à `online` que la voie de commande est prête.

### 18.3 `set_message_handler` avant `connect()`

W1 §20.10 signale que `PahoMqttClient._handler` est écrit par
`set_message_handler` et lu par `_on_message` **sans verrou**.

> **Clause.** Le gestionnaire de message **MUST** être enregistré **avant**
> `connect()`.

Aucun rappel ne peut alors précéder l'écriture, et l'absence de verrou devient
sûre **par construction, non par chronométrie** — exactement le raisonnement tenu
par C11 pour `mark_connected()`, appelé avant `connect()` dans
`ReadSurfacePublisher.start()`. Précédent, non invention. Aucun verrou n'est
ajouté.

### 18.4 Publier avant la connexion

`PahoMqttClient.publish()` **ne lève jamais** `NotConnectedError` : le terme
n'apparaît pas dans l'adaptateur. Une publication hors connexion produit un `rc`
non nul, donc un handle **`failed`**, que `_admit` traite en *fail-closed*
`bridge_unavailable`. Le comportement diverge de `FakeMqttClient`, qui **lève**.
§18.2 évite la situation sans clause supplémentaire.

---

## 19. Cycle de vie — arrêt

### 19.1 Ce qui existe

C9 traduit `SIGINT`/`SIGTERM` en demande d'arrêt via un descripteur de réveil, et
**ne promet aucune borne** sur la durée totale de sortie. C8 consulte l'arrêt à
deux moments et ne tronque jamais un `run_due()` engagé.

### 19.2 Les six états

| | État à l'instant de la demande d'arrêt | Sémantique contractée |
| --- | --- | --- |
| **A** | aucune commande admise | rien à traiter |
| **B** | message reçu, **déposé**, non encore admis | **abandonné**, sans ACK, **jamais réputé admis** — §19.4 |
| **C** | commande **admise**, `accepted` publié, en file | **abandonnée sans verdict** — §20 |
| **D** | transaction **en cours d'exécution** | **non tronquée** — menée à son verdict |
| **E** | écriture faite, confirmation en cours | **non tronquée** — c'est le cas D |
| **F** | verdict calculé, ACK non publié | verdict **en cache**, publication au mieux (W1 §16) |

### 19.3 Clauses

1. Dès que l'arrêt est demandé, le propriétaire **MUST NOT** admettre de nouveau
   message (états A, B).
2. Une commande **admise dans l'itération courante** **MUST** être exécutée par
   `process_next()` dans **cette même itération**, y compris si une demande
   d'arrêt survient entre l'admission et l'exécution. Admettre puis abandonner
   dans la même itération produirait un `accepted` immédiatement orphelin, alors
   que la transaction est déjà payée : ce serait l'exposition maximale pour un
   gain nul.

   > **Erratum.** La V2 exigeait ici, en outre, que le propriétaire **consulte**
   > l'arrêt entre les deux opérations. Cette obligation est **retirée**. Elle ne
   > pouvait avoir aucune conséquence, la phrase ci-dessus prescrivant
   > l'exécution dans les deux cas ; or une obligation normative sans effet
   > observable est **invérifiable** — aucun test ne peut distinguer la présence
   > de l'absence d'un tel appel, et l'exiger reviendrait à imposer du code mort.
   > Le contrat prescrit désormais le comportement, et lui seul.
3. Une transaction **déjà en exécution** **MUST NOT** être tronquée (états D, E).
   Transposition exacte de la règle C8 sur `run_due()`, pour la même raison : une
   écriture interrompue en cours de confirmation laisserait un fait physique sans
   verdict.
4. Le propriétaire **MUST NOT** entamer de **nouvelle** itération après la demande
   d'arrêt.
5. Un verdict déjà calculé **MUST** rester en cache même si sa publication échoue
   (état F) — comportement actuel de `_conclude`, verrouillé sans être modifié.

### 19.4 État B — verrouillé explicitement

*L'audit a constaté que cet état n'était couvert par aucune propriété ni aucun
mutant.* Il l'est désormais (P19, M18).

> Un message présent dans le dépôt et non admis à l'arrêt est **abandonné**. Il
> n'a jamais été admis, aucun `request_id` n'est connu du cœur, aucune promesse de
> C3 n'est engagée, et **aucun ACK MUST NOT** être fabriqué pour lui. Le traiter
> comme admis serait mentir sur un travail qui n'a pas eu lieu.

### 19.5 Aucun drain à l'arrêt

*L'audit a constaté que le MUST NOT correspondant n'était adossé à aucune
propriété.* Il l'est désormais (P21, M20).

> Le propriétaire **MUST NOT** appeler `drain()` à l'arrêt, ni boucler sur
> `process_next()`. Fondement en §22.2 : le coût conditionnel d'un drainage
> complet excède la marge de `TimeoutStopSec`, et sa durée absolue reste
> **non démontrable** tant que l'écriture n'est pas bornée.

Cette interdiction est **révisable** — mais seulement par une décision
contractuelle explicite accompagnée d'une révision de C12 (§32, R3), jamais par
initiative de W3.

---

## 20. `accepted` sans verdict terminal

### 20.1 Le problème, sans le maquiller

`accepted` prouve au demandeur que Boilerack a **admis** la transaction.

**Attribution exacte.** La formulation générale « toute transaction admise produit
un verdict terminal » est la **docstring de `core/engine.py` (l. 35)**, pas une
clause de C3. Ce que **C3 écrit** est plus étroit et figure sous le titre
« Conclusion garantie **sur exception** » : « une seule invocation d'écriture,
`in_flight` garanti libéré, verdict terminal mis en cache, aucune transaction
abandonnée silencieusement ». Cette garantie porte sur les **exceptions survenant
pendant** une transaction, dans le périmètre d'un appel. *La V1 attribuait à C3 la
formulation globale ; c'était inexact.*

**Ni C3 ni la docstring ne parlent de la sortie du processus.** Une commande dans
l'état **C** ne recevra donc jamais de verdict si le processus s'arrête avant de
l'exécuter — sans qu'aucune clause soit violée, et sans que la promesse implicite
de `accepted` soit tenue.

### 20.2 Pourquoi W2 ne le corrige pas

- **drainer complètement** — §19.5, §22.2 ;
- **émettre un verdict de substitution** — `rejected/bridge_unavailable` serait
  factuellement exact (aucune écriture émise) et n'inventerait aucune `Reason`.
  Mais le produire exige d'appeler `_conclude` sur une commande dépilée sans
  l'exécuter, ce qu'**aucune surface publique du cœur ne permet** :
  `process_next()` exécute, il n'abandonne pas. L'obtenir imposerait de modifier
  `boilerack/core/`, **interdit à W3** ;
- **inventer un statut** — proscrit (§4.9).

> **Clause.** W2 **MUST NOT** créer d'obligation de verdict pour une commande
> admise mais non exécutée à l'arrêt. La situation est **énoncée**, non résolue.

Trou **reporté** avec propriétaire désigné : §32, R1.

### 20.3 Ce que la V2 garantit, et ce qu'elle ne garantit pas

*L'audit demandait de réduire structurellement l'exposition sans prétendre la
supprimer.* La cadence de §13 le fait :

**Garanti :**

- la profondeur de la file du cœur **revient à zéro à la fin de chaque itération
  nominale** (§13.1) ;
- l'exposition ne **croît donc plus mécaniquement** jusqu'à `queue_capacity` par
  simple fonctionnement normal — elle passe d'un maximum de **16** sous une
  cadence non gouvernée à **au plus 1** ;
- une transaction **déjà en exécution** va toujours à son verdict (§19.3.3) ;
- une transaction admise dans l'itération courante est **exécutée dans la même
  itération**, même si l'arrêt est demandé entre les deux (§19.3.2).

**Non garanti :**

- le cas **ne disparaît pas**. Une commande admise peut rester sans verdict — par
  exemple si le processus est tué (`SIGKILL`, expiration de `TimeoutStopSec`,
  panne) entre la publication de `accepted` et la fin de `process_next()` ;
- aucune borne de temps n'est promise sur cet intervalle, l'écriture n'étant pas
  bornée (§17.2) ;
- si un lot futur modifiait la cadence de §13.1, l'exposition redeviendrait
  proportionnelle à `queue_capacity`.

---

## 21. Drain

| Régime | Usage de `drain()` |
| --- | --- |
| nominal | **interdit** — `process_next()` au plus une fois par itération (A-6) |
| arrêt | **interdit** — §19.5 |

`drain()` reste ce qu'il est : une commodité de test, utilisée par
`tests/core/test_queue.py`. W2 **ne le supprime pas**, **ne le modifie pas**, et
n'impose à W3 aucune primitive de drain nouvelle.

**Qualification exacte de ses bornes** (§8.2) : borné en **nombre** (≤
`queue_capacity` = 16), **non borné en durée**.

---

## 22. systemd et `TimeoutStopSec`

### 22.1 Autorité relue, non modifiée

C12 §10 : plancher de lecture `8 × 5,0 s = 40 s` ; `TimeoutStopSec=90` ; marge
nominale **50 s**. C12 conserve déjà l'inconnue I2 — « la marge au-delà du
plancher n'est pas démontrée ».

**W2 ne modifie ni C12, ni C13, ni aucune unité systemd.**

### 22.2 Coût conditionnel de la voie transactionnelle

| Composante | Statut | Valeur |
| --- | --- | --- |
| confirmation par relecture | **borne stricte prouvée** | **10,5 s** = `confirm_budget_s` + `confirm_interval_s` + `read_timeout_s` |
| invocation d'écriture | **NON BORNÉE** — aucun writer réel, `write_timeout_s` non consommé | *non démontrable* |
| **une transaction** | **NON BORNÉE**, minorée par 10,5 s | ≈ 15,5 s **seulement si** un writer futur honore `write_timeout_s = 5,0 s` |

| Politique d'arrêt | Coût ajouté | Tient dans la marge de 50 s ? |
| --- | --- | --- |
| terminer la transaction en cours (§19.3.3) | ≈ **15,5 s** *dans le scénario conditionnel ci-dessus* | **oui, sous condition** — pas de réponse absolue : le total réel est non démontrable |
| drainer la file pleine (16) | ≈ **248 s** *dans le même scénario conditionnel* | **non** — dépasse `TimeoutStopSec=90` à lui seul, et sa durée absolue reste non démontrable |

*La V1 répondait « oui » sans réserve à la première ligne ; c'était une borne
présentée comme acquise alors qu'elle est conditionnelle.*

### 22.3 Signalement

> **W2 signale à C12 une contrainte nouvelle, sans la trancher.** Dans le scénario
> conditionnel ci-dessus, terminer la transaction en cours consommerait environ
> 15,5 s de la marge de 50 s. L'inconnue I2 de C12 s'en trouve **aggravée, non
> résolue**, et une deuxième inconnue s'y ajoute : tant que l'écriture n'est pas
> bornée, **aucune marge ne peut être démontrée suffisante**.
>
> Ce signalement **MUST** être porté à C12 lorsqu'une voie transactionnelle
> deviendra réellement active. W2 ne change aucune valeur.

### 22.4 `loop_stop()` et les paquets en attente

Rappel du fait 6 (§6) : `disconnect()` appelle `loop_stop()` puis `disconnect()`,
et `loop_stop()` **ne garantit pas** l'émission des paquets déjà mis en file.

> **Conséquence.** Un ACK terminal publié dans les derniers instants peut ne
> jamais quitter la socket. Le verdict reste **en cache** et **reste vrai** : W1
> §16 s'applique tel quel. W2 ne crée aucun retry — W1 l'interdit — et ne modifie
> pas l'ordre de `disconnect()`.

---

## 23. Erreurs — aucune taxonomie nouvelle

Sémantique C3 existante, relue sans modification : `invalid_payload`,
`invalid_type`, `invalid_value_*`, `invalid_step`, `expired`,
`bridge_unavailable`, `queue_full`, `unsupported_command`, `unsupported_role` ;
statuts `accepted`, `applied`, `rejected`, `timeout`.

**Le cycle de vie doit-il convertir certaines situations d'arrêt en un verdict
existant ?** **Non**, et la raison est **mécanique**, non esthétique : §20.2 le
démontre — aucune surface publique du cœur ne permet de conclure une commande sans
l'exécuter, et modifier le cœur est interdit à W3. La conversion est **REPORTÉE**.

> **Clause.** W2 **MUST NOT** créer de `Reason`, de `AckStatus`, de classe de
> raison, ni de champ d'ACK. Le débordement du dépôt (§16.4) n'en crée aucun non
> plus : il n'y a **pas** d'admission, donc rien à acquitter.

---

## 24. Coupure MQTT pendant une transaction

1. **La transaction continue.** L'exécution dépend de `vclient`, jamais de MQTT.
   Une coupure ne la suspend pas et **MUST NOT** l'interrompre.
2. **Le verdict métier est inchangé.** Seule la relecture décide.
3. **Le cache terminal conserve le verdict** : `_conclude` met en cache **avant**
   de publier.
4. **Aucun retry d'ACK.** W1 l'interdit ; W2 ne l'introduit pas.
5. La publication ratée est **absorbée et journalisée** (`_publish_terminal`).

**Cas particulier de `accepted`.** Si sa publication échoue de façon **établie**
avant l'écriture, C3 applique déjà le *fail-closed* : la commande n'est pas
exécutée, verdict `bridge_unavailable`. W2 **ne touche pas** à cet arbitrage.

---

## 25. Reconnexion MQTT pendant une transaction

Chemin réel de `_on_connect`, sur le fil réseau : marquage de l'état connecté →
`_notifier(etabli)` (donc `ConnectionState.notify`, verrouillé) → si établi,
`_restaurer_souscriptions()` (registre W0, instantané sous verrou, émission hors
verrou).

**Aucune de ces étapes ne touche le cœur** : ni la file, ni `in_flight`, ni le
cache terminal, ni `vclient`.

> **Clause.** Une reconnexion MQTT **ne perturbe aucune transaction admise**, et
> W2 **MUST NOT** fabriquer de corrélation entre la reprise de connexion et l'état
> transactionnel. Aucune n'existe ; en inventer une créerait une dépendance que ni
> W0 ni C11 ne portent.

---

## 26. Instance MQTT unique

W1 §7.5 a tranché : une seule instance `MqttClient` en runtime. **W2 ne rouvre pas
la question et n'en fait pas une propriété propre** — ce serait re-verrouiller W1
et gonfler artificiellement W2. L'obligation correspondante (§28, MUST NOT 31)
renvoie à W1 comme autorité.

Le modèle de §12 y est cohérent : le propriétaire unique publie tous les ACK, et
le fil réseau unique de Paho reçoit tous les messages. **Deux fils, un client.**

---

## 27. Frontière avec W1 — rien n'est modifié

W2 ne touche à aucune de ces décisions : `command_topic`, QoS 1 entrant,
`ack_topic_prefix`, schéma des topics d'ACK, `retain`, `request_id`,
déduplication, absence de SUBACK, traitement des messages retenus, perte pendant
une coupure.

Les onze points de W1 §20 sont traités **sans** qu'aucune clause de W1 ait dû être
amendée. Les trois renvois fautifs connus de W1 restent **intacts** : les corriger
ici mêlerait deux lots.

---

## 28. Obligations de W3 — la charte complète

**W3 MUST :**

1. **Propriétaire unique** — exécuter `submit`, `process_next` et `drain`
   **exclusivement** depuis le fil de la boucle du runner (§12) ;
2. **Callback minimal** — limiter le contexte de rappel MQTT à un dépôt du
   `Message` brut, sans publication, sans lecture `vclient`, sans accès au cœur
   (§14.1) ;
3. **Dépôt inter-fils** — utiliser une structure **sûre entre fils**, **bornée** et
   **non bloquante** à saturation (§14.1, A-4) ;
4. **Capacité gouvernée** — capacité **≥ `queue_capacity`**, exprimée en constante
   nommée, **accompagnée de l'hypothèse de débit d'arrivée qui la justifie**
   (§16.3) ;
5. **Débordement** — le journaliser, ne produire **aucun** ACK, et ne pas le
   présenter comme une coupure de transport (§16.4) ;
6. **Cadence d'admission** — admettre **au plus un** message par itération
   (§13.1) ;
7. **Cadence d'exécution** — appeler `process_next()` **au plus une fois** par
   itération, et **jamais** `drain()` (§13.1, §21) ;
8. **Place exacte** — respecter l'ordre `run_due()` → admission →
   `process_next()` (§13.3) ;
9. **Latence** — énoncer la décomposition de §17.1 dans sa documentation
   d'exploitation, sans annoncer de borne (§17.2) ;
10. **Horloge** — injecter au cœur **la même instance** que celle du runner et du
    publieur (A-9) ;
11. **Sérialisation `vclient`** — n'émettre aucune opération `vclient` hors du
    propriétaire (§15.2) ;
12. **Démarrage** — enregistrer le gestionnaire de message **avant** `connect()`
    (§18.3) ;
13. **Démarrage** — n'admettre aucun message avant l'entrée en régime d'itération
    (§18.2) ;
14. **Arrêt** — cesser toute admission dès que l'arrêt est demandé (§19.3.1) ;
15. **Arrêt** — exécuter la transaction admise dans l'itération courante même si
    l'arrêt survient entre l'admission et `process_next()` (§19.3.2) ;
16. **Arrêt** — laisser une transaction en cours aller à son verdict (§19.3.3) ;
17. **Test de non-ouverture** — réviser ou remplacer explicitement
    `tests/adapters/test_mqtt_paho.py::test_aucune_voie_de_commande_ouverte` —
    obligation déjà posée par W1 §21.10, confirmée sans redéfinition ;
18. **Signalement** — porter à C12 le signalement de §22.3 si la voie devient
    active.

**W3 MUST NOT :**

19. modifier `boilerack/core/` — y compris pour y ajouter un verrou, un `RLock`
    ou un fil (autorité : **W1 §21.16** ; conséquence pour W2 : §11.1) ;
20. utiliser `TransactionalCore.attach()` en runtime (§12.1.2) ;
21. publier un ACK depuis le contexte de rappel MQTT (§12) ;
22. bloquer le fil réseau de Paho, à quelque titre que ce soit — keepalive
    (§6 fait 5, A-4) ;
23. introduire un verrou de sérialisation dans la couche de câblage pour couvrir
    `process_next` (§11.1) ;
24. admettre plus d'un message, ou exécuter plus d'une transaction, par itération
    (§13.1) ;
25. placer l'admission ailleurs que dans la position de §13.3 ;
26. drainer la file du cœur à l'arrêt sans révision contractuelle préalable de
    `TimeoutStopSec` (§19.5, §22) ;
27. fabriquer un ACK pour un message déposé mais non admis (§19.4) ;
28. créer un statut, une `Reason`, un champ d'ACK ou un indicateur de santé
    (§23) ;
29. annoncer une borne de latence d'admission (§17.2) ;
30. faire signifier à `online` que la voie de commande est prête (§18.2) ;
31. créer un second client MQTT ou une seconde boucle réseau (autorité : **W1
    §7.5**) ;
32. introduire un retry d'ACK ou une seconde déduplication (autorité : **W1**) ;
33. interrompre une transaction au seul motif que MQTT est tombé (§24) ;
34. activer quoi que ce soit sur une installation réelle.

**Ce que W2 ne choisit pas pour W3 :** aucun nom de module, de classe ni de
fonction, et **aucune valeur de capacité**. La seule primitive nommée l'est
**négativement** — `attach()` —, parce qu'elle existe déjà et qu'un contrat doit
dire quand ne pas s'en servir.

---

## 29. Frontière avec W4

W2 **ne définit pas** : la commande `set…`, la syntaxe réelle d'une écriture
`vclient`, le profil réel, les bornes, les tolérances, la première écriture, la
chaudière, la bascule terrain, la coexistence avec l'ancien pont.

**Ce que W2 se permet :** une **règle de sérialisation abstraite** (§15.2), qui ne
dit rien du contenu d'une écriture ni de sa durée. Elle contraint Boilerack,
jamais l'équipement.

**Ce que W2 se refuse :** déduire du modèle d'exécution une quelconque
**capacité** à écrire. Aucun adaptateur d'écriture n'existe, et `write_timeout_s`
n'est consommé nulle part. Une voie de commande **fonctionnelle** ne peut être
revendiquée par aucun lot avant W4.

---

## 30. Propriétés à verrouiller

| # | Propriété | Ancrage |
| --- | --- | --- |
| **W2-P1** | Le rappel `on_message` s'exécute sur le fil réseau de Paho, distinct du propriétaire. | §6 |
| **W2-P2** | Aucune opération mutante du cœur n'est exécutée depuis le contexte de rappel. | §12.1 |
| **W2-P3** | Un seul contexte appelle `submit`, `process_next` et `drain`. | §12.1 |
| **W2-P4** | Le contexte de rappel ne publie sur MQTT ni ne lit `vclient`. | §14.1 |
| **W2-P5** | Le dépôt inter-fils est borné. | §16.3 |
| **W2-P6** | La capacité du dépôt est **≥ `queue_capacity`** du cœur, et nommée. | §16.3 |
| **W2-P7** | Le dépôt ne bloque jamais le fil de rappel à saturation. | A-4, §6 fait 5 |
| **W2-P8** | Un débordement du dépôt est **journalisé** et ne produit **aucun** ACK. | §16.4 |
| **W2-P9** | La sûreté des structures du cœur découle de l'unicité du propriétaire ; **aucun verrou n'est requis** pour l'obtenir. | §9, §11.1 |
| **W2-P10** | Deux opérations `vclient` ne sont jamais simultanées. | §15.2 |
| **W2-P11** | **Au plus une admission** par itération. | §13.1 |
| **W2-P12** | **Au plus une exécution** par itération ; `drain()` n'est jamais appelé en runtime. | §13.1, §21 |
| **W2-P13** | Ordre d'itération : `run_due()` → admission → `process_next()`. | §13.3 |
| **W2-P14** | À la fin d'une itération nominale, la profondeur de la file du cœur est **nulle**. | §13.1 |
| **W2-P15** | `accepted` et le verdict terminal sont publiés depuis le même contexte. | §12.2 |
| **W2-P16** | Le cœur reçoit la même instance d'horloge que le runner et le publieur. | A-9 |
| **W2-P17** | Le gestionnaire de message est enregistré avant `connect()`. | §18.3 |
| **W2-P18** | Aucune admission avant l'entrée du propriétaire en régime d'itération. | §18.2 |
| **W2-P19** | Après la demande d'arrêt, aucune nouvelle admission. | §19.3.1 |
| **W2-P20** | Un message déposé mais non admis à l'arrêt est abandonné, sans ACK, et **jamais réputé admis**. | §19.4 |
| **W2-P21** | Une transaction admise dans l'itération courante est exécutée dans cette itération, même si l'arrêt survient entre les deux. | §19.3.2 |
| **W2-P22** | Une transaction en cours d'exécution n'est pas tronquée par l'arrêt. | §19.3.3 |
| **W2-P23** | **Aucun drain** de la file du cœur à l'arrêt. | §19.5 |
| **W2-P24** | Une coupure MQTT n'interrompt pas une transaction et ne modifie pas son verdict. | §24 |
| **W2-P25** | Une reconnexion MQTT ne touche aucun état du cœur. | §25 |
| **W2-P26** | W2 ne crée aucun statut, `Reason`, champ d'ACK ni indicateur de santé. | §23 |
| **W2-P27** | `online` ne signifie pas « voie de commande prête ». | §18.2 |
| **W2-P28** | W2 **ne revendique aucune borne** de latence d'admission. | §17.2 |
| **W2-P29** | W2 n'ouvre aucune voie runtime : les tests de non-ouverture restent verts. | §33 |

**Propriétés retirées depuis la V1, et pourquoi.** « Aucun verrou ajouté à
`boilerack/core/` » et « aucun second client MQTT » **re-verrouillaient W1**
(§21.16 et §7.5). Elles figurent désormais comme **obligations renvoyant à W1**
(§28, MUST NOT 19 et 31), non comme propriétés de W2. W2-P9 les remplace par un
énoncé qui lui appartient : la **suffisance** du propriétaire unique.

**Trois propriétés sans mutation dédiée, et la raison de ne pas en inventer.**
W2-P1 est un **fait mesuré** de la dépendance : le muter reviendrait à muter Paho.
W2-P27 énonce une **absence de signification** — qu'aucune déviation de câblage ne
peut porter seule, `online` restant vrai quoi que fasse la voie de commande.
W2-P29 est une propriété de **non-action** du présent lot, vérifiable directement
par la suite existante. Les vingt-six autres sont chacune tuée par au moins une
mutation de §31.

---

## 31. Mutations conceptuelles discriminantes

Une mutation = une déviation. Aucune n'est stylistique. Elles sont **futures** :
W2 n'écrit pas de code, donc ne les exécute pas.

| # | Mutation | Propriété tuée |
| --- | --- | --- |
| **W2-M1** | Appeler `submit` directement depuis `_on_message` (revenir à `attach()`). | P2, P3 |
| **W2-M2** | Appeler `process_next` depuis deux contextes. | P3, P10 |
| **W2-M3** | Publier `accepted` depuis le fil réseau, le verdict depuis le propriétaire. | P4, P15 |
| **W2-M4** | Rendre le dépôt non borné. | P5 |
| **W2-M5** | Donner au dépôt une capacité **< `queue_capacity`**. | P6 |
| **W2-M6** | Faire attendre le dépôt à saturation (fil Paho bloqué, keepalive gelé). | P7 |
| **W2-M7** | Laisser un débordement **silencieux**, non journalisé. | P8 |
| **W2-M8** | Produire un ACK au débordement du dépôt. | P8 |
| **W2-M9** | Introduire un verrou de câblage couvrant `process_next`. | P7, P9 |
| **W2-M10** | Permettre une lecture de télémétrie pendant une écriture transactionnelle. | P10 |
| **W2-M11** | Admettre **tous** les messages disponibles par itération. | P11, P14 |
| **W2-M12** | Exécuter `drain()` au lieu d'un seul `process_next()`. | P12, P14 |
| **W2-M13** | Placer l'admission **après** `process_next()`. | P13, P14 |
| **W2-M14** | Placer l'admission **avant** `run_due()`. | P13 |
| **W2-M15** | Injecter au cœur une horloge distincte de celle du runner. | P16 |
| **W2-M16** | Enregistrer le gestionnaire **après** `connect()`. | P17 |
| **W2-M17** | Admettre pendant `start()`, avant l'entrée en régime d'itération. | P18 |
| **W2-M18** | Continuer d'admettre après le début de l'arrêt. | P19 |
| **W2-M19** | Fabriquer un ACK pour un message déposé mais non admis à l'arrêt. | P20 |
| **W2-M20** | Abandonner, à l'arrêt, la commande admise dans l'itération courante au lieu de l'exécuter. | P21 |
| **W2-M21** | Tronquer une transaction en cours parce que l'arrêt est demandé. | P22 |
| **W2-M22** | Drainer la file du cœur à l'arrêt. | P23 |
| **W2-M23** | Interrompre une transaction au seul motif que MQTT est tombé. | P24 |
| **W2-M24** | Réinitialiser la file ou `in_flight` à la reconnexion MQTT. | P25 |
| **W2-M25** | Inventer un statut « annulé » pour les commandes abandonnées à l'arrêt. | P26 |
| **W2-M26** | Annoncer une borne de latence d'admission. | P28 |

**Mutations retirées depuis la V1.** « Ajouter un verrou dans `boilerack/core/` »
et « construire un second client MQTT » ne mutaient que des clauses de **W1** ;
elles ne discriminaient aucune décision de W2. W2-M9 les remplace par une mutation
qui, elle, discrimine réellement un arbitrage de W2 : le verrou de **câblage**,
option A-1(c), écartée pour le keepalive.

---

## 32. Risques, inconnues et reports

### 32.1 Inconnues — non dérivables du dépôt

| # | Inconnue | Propriétaire |
| --- | --- | --- |
| **I1** | Comportement réel de `vcontrold` sous accès concurrent. La sérialisation §15.2 est une règle **Boilerack**, prise par prudence, non une caractérisation. | Terrain / W4 |
| **I2** | **Borne réelle d'une écriture.** `write_timeout_s = 5,0` est déclaré et validé mais **consommé nulle part**, et aucun adaptateur d'écriture n'existe. C'est l'inconnue qui rend non bornées la latence d'admission (§17.2), la durée d'une transaction (§8.1) et la marge d'arrêt (§22.2). | W4 |
| **I3** | Durée réelle d'une confirmation par relecture sur équipement réel. | W4 |
| **I4** | Comportement de la chaudière face à une écriture. | Terrain |
| **I5** | Débit d'arrivée réel des commandes — d'où l'absence de valeur de capacité en §16.3. | W3, sur hypothèse écrite |
| **I6** | Compatibilité terrain et interaction avec l'ancien pont. | Porte terrain |

### 32.2 Risque hérité, préexistant à W2

| # | Point | État |
| --- | --- | --- |
| **H1** | Concurrence interne de Paho entre un `publish()` émis depuis le fil principal et un `subscribe()` réémis depuis le fil réseau. `publish` prend `_out_message_mutex`, `_send_subscribe` n'en prend aucun. | **Préexistant à W2**, non créé par lui : la situation existe **déjà** aujourd'hui, le publieur de lecture publiant sur le fil principal pendant que W0 réémet ses souscriptions sur le fil réseau. **Non démontré** depuis ce dépôt qu'une course existe ou non. Ne conditionne **pas** l'activation de W2. |

*La V1 présentait ce point comme une dépendance « à vérifier avant activation »,
ce qui laissait croire que W2 l'introduisait. Requalifié.*

### 32.3 Reports

| # | Point | Propriétaire |
| --- | --- | --- |
| **R1** | Verdict d'une commande admise mais non exécutée à l'arrêt. Impossible sans modifier `boilerack/core/`, interdit à W3 par W1 §21.16. Exigerait un amendement de C3. **Exposition réduite à au plus 1 par la V2** (§20.3), non supprimée. | Lot futur amendant C3 |
| **R2** | Chemin de réveil du propriétaire à l'arrivée d'une commande, si la latence de §17 devient inacceptable. W2 n'en conçoit aucun. | W3, sur décision explicite |
| **R3** | Révision de `TimeoutStopSec` si une politique de drain est un jour adoptée. | C12, sur signalement §22.3 |

### 32.4 Risques assumés

1. **Latence d'admission non bornée** (§17.2) — énoncée, non masquée, sans nombre
   de remplacement.
2. **Marge d'arrêt réduite** (§22.3) — d'environ 15,5 s sur 50 s **dans le scénario
   conditionnel** ; aucune marge n'est démontrable tant que I2 tient.
3. **`accepted` sans suite** (§20.3) — réduit à au plus 1, jamais supprimé.
4. **`queue_full` inatteignable** en régime nominal (§13.1) — la contre-pression
   se déplace au dépôt, dont le dimensionnement devient le point de vigilance.
5. **Écoulement lent du dépôt** (§13.1) — une rafale s'écoule à un message par
   itération, et une commande peut expirer en attente. Comportement C3 nominal.

---

## 33. Ce que W2 ne fait pas

- aucun code, aucun test modifié, aucun autre contrat modifié ;
- aucune souscription, aucun `set_message_handler`, aucun `TransactionalCore` en
  runtime ;
- aucune correction des trois renvois fautifs de W1 — ils restent **dette
  documentaire ouverte** ;
- aucun terrain, aucune installation, aucun accès à un broker, un Pi, un
  `vcontrold` ou une chaudière.

`test_aucune_voie_de_commande_ouverte` reste **vert** après W2 : le lot ne touche
ni `runtime.py`, ni `lifecycle.py`, ni `cli.py`.

---

## 34. Renvois

- **W1 §20** — liste fermée des invariants délégués : traitée intégralement,
  §10 ; les points **5** et **6**, restés ouverts en V1, sont fermés par §13.
- **W1 §21** — obligations de W3 : W2 en **ajoute** (§28) et n'en modifie
  **aucune**.
- **W1 §11.5** — question laissée ouverte par W1 : tranchée en §12.
- **W1 §14.2** — `expires_at` contre l'ancienneté : réutilisé en §18.2.
- **W1 §7.5, §16, §17.3** — instance unique, perte d'ACK, fenêtre de coupure :
  consommés (§26, §22.4, §16.4).
- **W0 §11.2, §14** — `online` ≠ restauré, aucune émission sous verrou :
  consommées.
- **C3** — sémantique transactionnelle : **inchangée** ; §20.1 précise ce que C3
  écrit réellement et ce qui relève de la docstring du cœur.
- **C8, C9** — boucle et arrêt : le modèle W2 s'y insère sans les modifier.
- **C11** — `ConnectionState` : précédent du patron « écriture multi-fils,
  consommation unique » (§14.2).
- **C12 §10** — `TimeoutStopSec` : **relu, signalé, non modifié** (§22).

---

## 35. Ce que la V2 corrige

| Défaut d'audit | Correction |
| --- | --- |
| **MAJEUR-1** — latence annoncée à tort comme bornée | §17 : décomposition en quatre composantes, qualifiées *borné* / *majorant conditionnel* / *non borné* ; aucune borne de remplacement ; P28, M26 ; obligation W3 n° 9 recalibrée. |
| **MAJEUR-2** — cadence et place de l'admission non décidées | §13 : au plus **une** admission par itération (A-7), position `run_due` → admission → `process_next` (A-8), ordre d'itération normatif ; ferme W1 §20.5 et §20.6 ; P11, P13, P14, M11, M13, M14. |
| **MAJEUR-3** — saturation non gouvernée | §16 : quatre options comparées, plancher `≥ queue_capacity` **avec son vrai motif**, constante nommée, hypothèse de débit exigée de W3, débordement journalisé et **dissocié** de W1 §17.3 ; P5, P6, P8, M5, M7. |
| m-1 | §5 : `attach()` est appelé — par `tests/core/test_reserves_c2.py:68` et `:78`. |
| m-2 | §12.1.2 : `test_integration_offline.py` n'appelle pas `attach()` ; il câble `set_message_handler(core.submit)`. |
| m-3 | §5.1 : preuve `grep` corrigée — la commande annoncée ne renvoyait rien ; trois occurrences du **nom**, aucune instanciation. |
| m-4 | §8.2, §21 : `drain()` borné en **nombre** (≤ 16), non en **durée**. |
| m-5 | §10 : les points 5 et 6 renvoient à §13, non à §14. |
| m-6 | §7 : **quatre** structures mutées, non cinq. |
| m-7 | §18.2 : l'argument « auto-réalisatrice » est retiré ; la règle est réelle, et `expires_at` (deux revalidations) est la vraie garde. |
| m-8 | §22.2 : la table distingue borne stricte (10,5 s) et coût conditionnel ; le « oui » devient « oui, sous condition ». |
| m-9 | §20.1 : la formulation globale est attribuée à la docstring de `engine.py`, non à C3, dont la clause est plus étroite. |
| m-10 | §19.4, §19.5 : état B et interdiction de drain verrouillés par P20/M19 et P23/M22. |
| m-11 | §30, §31 : les propriétés et mutations qui ne re-verrouillaient que W1 sont retirées ; W2-P9 et W2-M9 les remplacent par des énoncés propres à W2. |
| info D1 | §32.2 : requalifié en **risque hérité préexistant** (H1), ne conditionnant pas l'activation. |
| info verrou externe | §11.1 : troisième option reconnue, écartée par le mécanisme du keepalive ; « seule voie possible » remplacé par « la plus sobre et la seule retenue ». |

---

## 36. Fermeture

W2 tranche **dix arbitrages** et pose **vingt-neuf propriétés**, toutes dérivées de
faits mesurés dans le dépôt ou dans la dépendance réellement installée.

La décision structurante reste **le propriétaire unique** — non plus présentée
comme la seule voie possible, mais comme la plus sobre des deux options permises,
l'autre étant écartée parce qu'elle transformerait une contention transactionnelle
en perte de connexion MQTT.

La V2 y ajoute la décision que la V1 avait laissée ouverte : **une admission et une
exécution par itération, l'admission placée entre `run_due()` et
`process_next()`**. C'est elle qui stabilise la file du cœur à zéro en fin
d'itération et ramène l'exposition « `accepted` sans terminal » de seize à un.

Ce que W2 refuse de faire reste aussi important que ce qu'il décide : aucun verdict
inventé pour les commandes abandonnées, aucune primitive de drain, aucun chemin de
réveil, aucune classe nommée, aucune capacité chiffrée, et **aucune borne prétendue
là où le dépôt n'en fournit pas**.

**W2 n'ouvre aucune voie de commande. Aucun terrain n'est touché.**
