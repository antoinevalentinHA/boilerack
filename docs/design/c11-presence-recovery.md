# C11 — Reprise de présence après reconnexion MQTT

Document normatif. Il étend `c7-mqtt-read-contract.md` (C7-B) §5 au cas des
connexions réussies **postérieures** au démarrage initial.

C11 ne crée aucune doctrine parallèle. Il ne modifie aucune valeur, aucun topic,
aucun QoS, aucune rétention, aucune période. Il rend exécutoire une obligation
déjà écrite que l'implémentation n'honore qu'une seule fois.

---

## 1. Objet

C7-B §5 pose, pour le suffixe `bridge/online` :

| | |
|---|---|
| QoS | 1 |
| Retain | true |
| Payload | strictement `online` ou `offline` |
| **À la connexion** | **`online`** |
| Testament MQTT | `offline`, QoS 1, retain |
| À l'arrêt propre | `offline` avant déconnexion |

et pour sémantique : « **le processus bridge est connecté au broker MQTT** ».

L'implémentation actuelle ne publie `online` qu'à `start()`. Après une
reconnexion, le processus est connecté et le retenu affirme le contraire. C11
comble exactement cet écart, et rien d'autre.

---

## 2. Le défaut, établi

### 2.1 Chaîne en cause

Les étapes marquées `[Boilerack]` sont observées ; celle marquée `[attendu]`
dépend d'un broker et n'a pas été observée (§2.2).

```text
start()                                                          [Boilerack]
  -> connect(will = offline retenu)
  -> bridge/online = online, QoS 1, retenu

deconnexion inattendue
  -> le broker applique le testament                             [attendu]
  -> bridge/online = offline, retenu

reconnexion automatique de Paho, reussie
  -> PahoMqttClient sait qu'il est connecte (_on_connect, propriete `connected`)
  -> ReadSurfacePublisher n'en est pas informe
  -> aucun `online` republie

les lectures et les publications reprennent normalement
  -> telemetrie fraiche ET presence retenue encore `offline`
```

### 2.2 Reproduction

La chaîne a été reproduite **hors ligne**, en n'employant que les coutures
existantes du dépôt : `PahoMqttClient` réel, faux client Paho des tests C4
(`fire_on_connect` / `fire_on_disconnect`), `ReadSurfacePublisher` réel,
`VirtualClock`. Après l'étape de reconnexion : **zéro** publication émise par
Boilerack, trois scalaires frais publiés au cycle suivant, retenu de présence
toujours `offline`.

> **Portée de cette preuve.** Elle établit ce que **Boilerack** fait et ne fait
> pas. Elle n'établit rien du comportement d'un broker réel : l'application du
> testament y est **simulée**, non observée. Voir §13.

### 2.3 Cause structurelle

- `bridge/online` n'est publié qu'à un seul endroit du code, dans `start()` ;
  `offline` à un seul autre, dans `stop()`. `run_due()` ne touche jamais la
  présence.
- La frontière `boilerack.transport.mqtt.MqttClient` expose cinq méthodes —
  `connect`, `disconnect`, `subscribe`, `publish`, `set_message_handler` — et
  **aucune notification de cycle de connexion**. Le publieur est donc
  structurellement aveugle à une reconnexion, quand bien même l'adaptateur la
  connaît.

C'est une lacune de **couture**, pas de logique : il n'existe aujourd'hui aucun
chemin par lequel l'information pourrait parvenir à qui doit agir.

---

## 3. Statut de C11 vis-à-vis de C7-B

C11 est une **extension normative de C7-B §5 pour le cycle de reconnexion**.

Ce qui est déjà dans C7-B et n'est pas créé ici : l'obligation de publier
`online` à la connexion · le topic · le QoS 1 · la rétention · les deux payloads
admis · la sémantique du topic · la séparation entre présence MQTT (§5) et santé
de la chaîne de lecture (§8).

Ce que C11 ajoute : **quelles connexions** déclenchent cette obligation après la
première, **par quel chemin** l'information circule, **quand** la publication a
lieu, et **ce qui l'annule**.

C7-B n'est pas modifié. Une seule réserve, traitée sans détour en §9 : C7-B ne
fixe aucun délai, ni pour §5 ni pour aucune autre publication, et son §15 #9
qualifie les cadences de « objectifs, non des garanties ». La borne temporelle
posée par C11 est donc une **précision** de §5, pas une dérogation — mais elle
doit être écrite, et elle l'est.

L'inconnue C7-B §15.5 — politique de rétention et d'expiration de session du
broker — **reste ouverte**. C11 ne la résout pas et ne s'appuie sur aucune
hypothèse à son sujet.

---

## 4. Périmètre

### 4.1 Inclus — liste fermée

Détection des transitions pertinentes de connexion MQTT · transmission de cette
information de l'adaptateur jusqu'au fil métier · republication de
`bridge/online` · idempotence et coalescence · annulation d'une reprise en
attente · ordre vis-à-vis de l'arrêt · discipline de fil · temporalité et borne
de latence · invariance des échéances et de la fraîcheur · obligations des
doubles · inconnues à lever contre un broker réel.

### 4.2 Exclus — liste fermée

Politique de reconnexion de Paho · modification du backoff · sortie du processus
sur déconnexion durable · suspension des lectures · nouvelle tentative
`vclient` · systemd · installation · Docker · Home Assistant · MQTT Discovery ·
topic de commande · ACK · écriture chaudière · nouveaux datapoints ·
modification des périodes de lecture · réinitialisation de la fraîcheur ·
réinitialisation des échéances · second `will_set()` · champs morts
(`command_topic`, `ack_topic_prefix`, `write_timeout_s`) · `_legacy` · README ·
version ou release · CI, lint, typage, couverture · avertissement C9
`signal wakeup fd`.

---

## 5. Caractérisation Paho — constats, non obligations

Les faits ci-dessous décrivent la bibliothèque **réellement contrainte** par le
projet (`paho-mqtt>=2.1,<3`, version installée 2.1.0, Callback API `VERSION2`).
Ils justifient les clauses de C11 ; ils n'en sont pas.

| # | Constat |
|---|---|
| P1 | `on_connect` est appelé pour **chaque** CONNACK : connexion initiale **et** reconnexion, sans aucune différence observable dans ses arguments |
| P2 | Signature `VERSION2` : `(client, userdata, connect_flags, reason_code, properties)`. `properties` n'est jamais `None` : un `Properties(CONNACK)` vide est substitué |
| P3 | Un succès se reconnaît à `reason_code.is_failure == False`. `Success` vaut `0` ; `Not authorized` vaut `135` ; `Server unavailable` vaut `136`, tous deux en échec |
| P4 | `int(reason_code)` **lève** `TypeError` en 2.1.0. Seul le chemin `is_failure` est praticable pour un vrai `ReasonCode` |
| P5 | `connect_flags.session_present` est fourni en MQTT 3.1.1 comme en 5, mais vaut **toujours `False`** tant que `clean_session` reste à son défaut `True` — ce qui est le cas. **Inutilisable** pour distinguer une reprise |
| P6 | `on_disconnect` `VERSION2` : `(client, userdata, disconnect_flags, reason_code, properties)`. Arrêt volontaire -> `ReasonCode(0)`, `is_failure False`. Perte -> `ReasonCode(128)`, `is_failure True`. Keepalive expiré -> `ReasonCode(141)`, `is_failure True` |
| P7 | `disconnect_flags.is_disconnect_packet_from_server` vaut **toujours `False`** en MQTT 3.1.1, protocole retenu par l'adaptateur : le broker n'y émet pas de DISCONNECT. **Inutilisable** |
| P8 | Les callbacks sont invoqués depuis le **fil réseau de Paho**, créé par `loop_start()` et nommé `paho-mqtt-client-<client_id>`, jamais depuis le fil principal. Chaîne : `_thread_main` -> `loop_forever` -> `_loop` -> `_packet_handle` -> `_handle_connack` -> `on_connect` |
| P9 | `suppress_exceptions` vaut `False` par défaut : une exception levée dans un callback est journalisée **puis relancée** dans la boucle réseau. Un callback qui bloque retarde keepalive, PUBACK et réception |
| P10 | La reconnexion automatique existe déjà : `reconnect_on_failure` vaut `True`, backoff exponentiel de 1 s à 120 s. Un `disconnect()` volontaire met fin à la boucle — aucune reconnexion n'y succède |
| P11 | Le testament est **conservé par le client Paho** (`_will_topic`, `_will_payload`, `_will_qos`, `_will_retain`) et réempaqueté par `_send_connect`, appelé par `reconnect()`. Il est donc réémis dans chaque CONNECT ultérieur |
| P12 | `connect()` **n'attend aucun CONNACK** : son corps se réduit à `connect_async(...)` puis `reconnect()`, qui se termine par l'envoi du CONNECT. Le CONNACK est lu par le fil réseau, et **aucun backoff ne le retarde** — l'état étant déjà `CONNECTING`, la boucle d'amorçage sort immédiatement et lit la socket. Un rappel peut donc survenir dès que `loop_start()` a armé le fil, y compris **pendant** la suite du démarrage de l'appelant |
| P13 | `loop_stop()` **joint** le fil réseau avant de rendre la main. Après un `disconnect()`, plus aucun rappel de la session close ne peut survenir |

### 5.1 Interdictions dérivées

La norme Boilerack **MUST NOT** dépendre de `session_present` (P5), de
`is_disconnect_packet_from_server` (P7), ni d'aucune propriété propre à MQTT 5.

La norme Boilerack **MUST NOT** ajouter, modifier ou désactiver la politique de
reconnexion native (P10) : elle en dépend, elle ne la pilote pas.

---

## 6. Frontière — capacité de cycle de connexion

### 6.1 Deux modèles comparés

**Modèle A — enrichir `MqttClient`.** Ajouter la notification au port MQTT
générique. Tout implémenteur du port doit alors la fournir, y compris ceux qui
ne servent qu'au chemin transactionnel : `TransactionalCore` consomme
`MqttClient` pour publier des ACK et n'a aucun besoin de présence. Le port se
décrit lui-même comme « frontière MQTT minimale, sans politique » ; y loger une
capacité dont un consommateur sur deux n'a que faire l'élargit au-delà de son
objet.

**Modèle B — capacité distincte, requise par la composition C11.** Le port MQTT
générique reste inchangé. Une capacité séparée porte la notification de cycle de
connexion. La surface de lecture, qui doit honorer §5, **exige les deux** ; le
coeur transactionnel n'exige que le port.

### 6.2 Modèle retenu — B

Motif : ségrégation d'interface. La capacité est requise **là où l'obligation
existe**, et nulle part ailleurs. Le port générique conserve la portée que son
propre texte lui donne.

Ce choix n'est **pas** motivé par le nombre de doubles à mettre à jour. Il se
trouve qu'il en touche moins, mais ce n'est pas l'argument.

### 6.3 Rien d'optionnel

Une précédente analyse avait envisagé une méthode « optionnelle » sur
`MqttClient`. **Cette formule est rejetée.**

Un membre déclaré dans un `Protocol` Python n'est pas optionnel au sens
structurel : un implémenteur qui l'omet ne satisfait plus le protocole, et
`runtime_checkable` ne vérifie de toute façon que la présence des noms, jamais
les signatures. Surtout, la conséquence serait fausse : **un client incapable de
signaler ses reconnexions rend le respect de C7-B §5 impossible**. Le tolérer
reviendrait à livrer une surface qui prétend honorer §5 sans le pouvoir.

Sont donc **INTERDITS** :

- `hasattr()` ou toute détection de capacité servant de repli silencieux ;
- l'absence de collaborateur tolérée, la reprise étant alors simplement
  désactivée ;
- toute construction de la surface de lecture avec un client MQTT dépourvu de la
  capacité.

La capacité est **REQUISE**. Une composition qui ne peut pas la fournir doit
échouer, visiblement, à la construction.

### 6.4 Forme

Trois éléments, et rien de plus.

**a) Une capacité côté client.** Un protocole distinct portant une seule
méthode, d'enregistrement, symétrique de `set_message_handler` :

```text
set_connection_handler(handler) -> None
```

Le rappel reçoit **l'état résultant**, un booléen : `True` pour « connexion
établie », `False` pour « non connectée ». Il ne reçoit ni code de raison, ni
drapeaux, ni propriétés : C11 n'en consomme aucun, et les exposer créerait une
surface de compatibilité sans consommateur.

**b) Une primitive d'état de connexion.** Un objet dédié qui reçoit les
transitions depuis n'importe quel fil et qu'un seul fil consomme. Sa
responsabilité est entière et unique : répondre à « une reprise est-elle due
maintenant ? ». Elle est le pendant exact de `SignalStop` en C9 — même rôle,
même discipline, même injection depuis la racine de composition.

**c) Un collaborateur requis de la surface de lecture.** Le publieur reçoit
cette primitive à la construction. Elle **n'est pas optionnelle**.

La racine de composition crée la primitive, l'enregistre auprès du client et la
remet au publieur. Aucune autre partie du programme ne les relie.

### 6.5 Obligations de l'émetteur

Un implémenteur de la capacité **MUST** :

- appeler le rappel avec `True` à **chaque** CONNACK de succès (`is_failure`
  faux) ;
- appeler le rappel avec `False` à **chaque** `on_disconnect`, quelle qu'en soit
  la raison ;
- appeler le rappel avec `False` à **chaque** CONNACK d'échec — la connexion
  n'est pas établie, et le dire est le seul moyen de ne pas laisser un état
  supposé survivre à un fait contraire ;
- ne **jamais** invoquer deux rappels concurremment ;
- ne **jamais** laisser une exception du rappel remonter vers Paho (P9).

Un implémenteur **MUST NOT** interpréter, filtrer ni retarder les transitions :
la décision appartient au fil métier, jamais à l'adaptateur.

---

## 7. Discipline de fil

### 7.1 Invariant central

> **Aucune publication métier, aucune mutation de `ReadSurfacePublisher` ne doit
> avoir lieu depuis le fil réseau de Paho.**

Motif, établi et non supposé : le publieur ne détient aucun verrou, mute
`_next_due`, `_state` et `_started` sans protection, et C7-C3B verrouille par
test qu'il n'importe ni `threading` ni `asyncio`. Publier depuis le fil réseau
introduirait des courses sur l'état, un entrelacement de publications d'ordre
indéfini, et exposerait la boucle réseau à une exception relancée (P9).

### 7.2 Ce que le rappel à le droit de faire

Le rappel **MUST** être non bloquant, sur de l'accès concurrent, et ne **MUST
NOT** jamais lever. Il ne fait qu'enregistrer une transition dans la primitive
d'état. Rien d'autre.

### 7.3 Ce que le publieur reste

Le module du publieur **MUST NOT** importer `paho`, `threading`, `asyncio`, ni
lire une horloge non injectée. C'est précisément pourquoi la primitive d'état
est un **collaborateur injecté** et non un attribut interne : elle peut, elle,
employer un verrou.

Le traitement métier — décider, puis publier — reste intégralement sur le fil du
runner.

---

## 8. Sémantique des transitions

### 8.1 Le problème d'un drapeau monotone

Un simple marqueur « une connexion est survenue », armé et jamais désarmé avant
consommation, est **INTERDIT**. Il produirait ceci :

```text
connexion reussie        -> reprise en attente
deconnexion inattendue   -> le marqueur reste arme
consommation par le runner -> `online` publie alors que le pont est deconnecte
```

soit exactement le mensonge que C11 vient corriger, retourné.

### 8.2 Règle

La primitive conserve **l'état courant** — connecté ou non — et un **marqueur de
transition**. Elle applique :

| Événement | Effet sur l'état | Effet sur le marqueur |
|---|---|---|
| Notification `True`, état courant **non connecté** | devient connecté | **armé** |
| Notification `True`, état courant **déjà connecté** | inchangé | inchangé |
| Notification `False` | devient non connecté | **désarmé** |
| Consommation, marqueur armé **et** état connecté | inchangé | désarmé, la reprise est due |
| Consommation, tout autre cas | inchangé | inchangé, aucune reprise |

Invariant qui en découle, et qui est la clause normative :

> **Au moment où le fil métier consomme une reprise, la dernière transition MQTT
> observée doit encore être une connexion réussie. Toute déconnexion postérieure
> à l'armement annule la reprise en attente.**

Une seule valeur booléenne suffit à porter le marqueur ; aucune file n'est
requise, et aucune ne doit être introduite : la seule information utile est
« une reprise est-elle due », qui est idempotente et sans historique.

### 8.3 État initial et démarrage

`start()` ouvre la connexion, puis publie `online` — comportement établi par
C7-C3A, inchangé. La primitive doit donc partir d'une base cohérente avec cette
annonce, faute de quoi le CONNACK initial armerait une reprise et ferait
republier `online` au premier cycle, pour rien.

**Aucun ordre entre le CONNACK et la suite de `start()` ne peut être supposé.**
P12 l'établit : l'ouverture n'attend pas le CONNACK, le fil réseau le lit des
son arrivée et aucun backoff ne le retarde. Un rappel peut donc survenir
**pendant** `start()`. Une rédaction antérieure de cette clause posait la base
*après* la publication de `online` et raisonnait sur « le CONNACK qui suit » :
cette relation d'ordre n'existe pas, et le raisonnement qu'elle portait était
faux.

**Le danger n'est pas la republication redondante.** Un succès reçu tôt serait
de toute façon désarmé par la pose de la base. Le danger est l'inverse, et il
est plus grave : **une base posée tard écrase un échec réellement observé**.
L'état redeviendrait « connecté » alors que la connexion a échoué ; la réussite
suivante ne serait plus une transition ; aucune reprise ne serait armée — et le
défaut que C11 corrige réapparaîtrait entier, sur le chemin même que cette
clause était censée couvrir.

Clause : **`start()` place la primitive dans l'état connecté et désarme tout
marqueur AVANT d'ouvrir la connexion**, c'est-à-dire avant l'appel qui rend un
rappel possible.

Cette place est sûre **par construction, non par chronométrie** : les rappels ne
sont émis que par le fil réseau, ce fil n'existe pas avant `loop_start()` (P8),
et `loop_start()` est interne à l'ouverture de la connexion. Aucun rappel ne
peut donc précéder la base.

Il en découle, sans qu'aucun ordre temporel ne soit supposé :

| Événement | État | Reprise |
|---|---|---|
| Base posée par `start()` | connecté | désarmée |
| Premier CONNACK **réussi** | reste connecté — aucune transition | aucune |
| Premier CONNACK **en échec** (§6.5) | passe non connecté — **le fait observé a autorité sur la base** | aucune |
| Réussite **ultérieure**, après un échec | transition non connecté -> connecté | **exactement une** |

La base reste optimiste : au moment où elle est posée, aucun CONNACK n'a été
reçu. Elle l'est **exactement autant** que la publication de `online` qui la
suit, déjà contractée ainsi. La différence tient à ceci : toute notification
réelle a désormais **autorité** sur elle, quel que soit l'instant où elle
survient.

**Redémarrage.** `stop()` désarme le marqueur, et la déconnexion met fin à la
boucle réseau en joignant le fil (P13) : aucun rappel de la session close ne
peut survivre. Un `start()` ultérieur repose donc la base dans les mêmes
conditions de sûreté.

**Échec de l'ouverture.** Si l'ouverture lève, `start()` propage l'exception
telle quelle : la politique d'erreur existante n'est pas modifiée, et le
publieur reste non démarré. La primitive conserve alors une base « connecté,
désarmée » qui ne correspond à rien — mais cet état est **fonctionnellement
inobservable** : une reprise n'est consommée qu'après la vérification de
démarrage, et un `start()` ultérieur repose la base. Aucun `try/except` ne doit
être ajouté pour « nettoyer » cet état : ce serait modifier une politique
d'erreur pour un état que personne ne peut lire.

### 8.4 Connexions échouées

Un CONNACK dont `reason_code.is_failure` est vrai n'est **jamais** une connexion
réussie. Il n'arme aucune reprise, ne fait publier aucun `online`, et ne modifie
aucune échéance. Il fait uniquement passer l'état à « non connecté » (§6.5).

---

## 9. Temporalité

### 9.1 Tension à résoudre

C7-B §5 dit « **à la connexion** : `online` ». Traiter la reprise sur le fil du
runner introduit un délai. Cette tension doit être tranchée, pas contournée.

### 9.2 Options

**T1 — consommation au prochain réveil naturel du runner.** Aucune nouvelle
couture inter-fil ; modèle mono-fil métier de C8/C9 intégralement préservé ; la
reprise devient une tâche due parmi les autres. Coût : la présence peut rester
`offline` jusqu'à la prochaine échéance.

**T2 — réveil immédiat dédié.** Rapproche la publication de l'événement. Coût :
une couture inter-fil supplémentaire, et le risque de la confondre avec le
mécanisme de signaux de C9.

### 9.3 Décision — T1

**T1 est retenu.**

**Borne normative.** La latence de reprise est bornée par la prochaine échéance
du publieur, soit :

```text
latence_max = min(plus petite periode de mesure,
                  snapshot_period_s,
                  heartbeat_period_s si le battement est actif)
```

Avec la surface v1 et les valeurs par défaut — périodes 30 s et 60 s,
`snapshot_period_s = 30`, `heartbeat_period_s = 30` — cette borne vaut
**30 secondes**.

**Pourquoi c'est une lecture honnête de C7-B §5.** §5 prescrit **ce qui** doit
être publié à la connexion ; il ne fixe **aucun** délai, et C7-B n'en fixe nulle
part : son §15 #9 range explicitement les cadences parmi les « objectifs, non
des garanties ». Une reprise bornée et annoncée satisfait donc §5. Ce qui le
violerait serait de ne jamais republier — le défaut d'aujourd'hui — ou de
republier sans borne connue.

**Ce qui ne doit pas être écrit.** Il est **INTERDIT** de présenter la reprise
comme immédiate, instantanée ou synchrone de l'événement de connexion. Elle ne
l'est pas, et la documentation utilisateur ne doit pas le laisser croire.

### 9.4 Interdiction explicite

Le socket de réveil de C9 **MUST NOT** servir de canal à C11.

Il a été caractérisé qu'un octet ne correspondant à aucun signal surveillé
réveille `WakeupClock` sans armer l'arrêt, et se retrouve dans
`signaux_ignores`. **C'est une caractérisation, pas une interface.** Ce
descripteur est celui de `signal.set_wakeup_fd`, il appartient à la gestion des
signaux, et y faire transiter un événement métier mélangerait deux natures
d'événements et polluerait un journal d'observabilité dédié aux signaux
étrangers.

Si un besoin de reprise plus rapide était un jour démontré, T2 devrait être
instruit comme une frontière propre, avec sa propre couture. C11 ne l'ouvre pas.

---

## 10. Publication de reprise

### 10.1 Contenu

Après une reprise due, le publieur publie **exactement un message** :

| | |
|---|---|
| Topic | `<prefix>/bridge/online`, dérivé par l'autorité existante `build_topic` |
| Payload | `online` |
| QoS | **1** |
| Retain | **true** |

Aucun autre topic n'est publié : ni scalaire, ni `bridge/telemetry_status`, ni
`bridge/heartbeat`, ni instantané.

### 10.2 Motifs

- Seul le retenu de présence a été altéré : le testament ne porte que sur
  `bridge/online`.
- Les scalaires sont publiés **retenus**. Un message retenu appartient au broker
  et survit à la déconnexion du client qui l'a publié : il n'y a rien à
  restaurer.
- Boilerack **ne conserve aucune valeur scalaire en mémoire**. `MeasurementState`
  porte trois champs — `last_success_wall`, `last_success_monotonic`,
  `last_result` — et aucune valeur. Republier des scalaires exigerait de stocker
  les valeurs, décision métier nouvelle, hors de cette frontière.
- Aucun besoin de rafraîchissement métier n'est démontré. Republier
  `telemetry_status` serait une redite : le testament ne l'a pas écrasé, et son
  contenu se recalculerait à l'identique.

### 10.3 Ordre dans la boucle

Le fil du runner consulte dans cet ordre :

```text
1. arret demande ?          -> si oui, sortir. Rien d'autre n'est fait.
2. reprise de presence due ? -> si oui, publier `online`.
3. travail periodique du.
```

Invariant : **l'arrêt prime toujours sur une reprise.** Il en découle qu'aucun
`online` n'est publié après le début d'un arrêt, ni après un `offline`.

L'obligation porte sur **l'ordre**, non sur son lieu d'écriture. La réalisation
la plus économe place l'étape 2 en tête de `run_due()`, où la vérification de
démarrage existe déjà et où l'étape 1 a nécessairement précédé : le runner reste
alors inchangé. Une réalisation dans la boucle du runner est admissible si elle
respecte le même ordre.

---

## 11. Arrêt

L'autorité d'état existante — le booléen `_started`, exposé par la propriété
`started` — **suffit**. Aucune machine d'état n'est créée : les états « jamais
démarré » et « arrêté » sont indiscernables par ce booléen, et **aucune décision
de C11 n'en dépend** — dans les deux cas, rien n'est republié.

Clauses :

- `started == False` -> **aucune reprise**, en toute circonstance ;
- `stop()` rend le publieur non démarré **avant** de publier `offline` : une
  reprise consommée pendant un arrêt en cours trouve donc déjà `started` faux ;
- un `disconnect()` volontaire ne génère aucune reprise. Il fait passer l'état à
  « non connecté » (§6.5), ce qui désarme, et met fin à la boucle réseau de Paho
  (P10) : aucune notification de connexion ne peut plus survenir.

---

## 12. Échéances et fraîcheur — invariance

Une reconnexion MQTT **MUST NOT** modifier :

`_next_due` de quelque mesure que ce soit · `_next_snapshot_due` ·
`_next_heartbeat_due` · `last_success_wall` · `last_success_monotonic` ·
`last_result` · l'état de fraîcheur (`age_s`, `fresh`) · `chain_status` ·
`chain_cause`.

Motif : **une reconnexion MQTT n'est pas une lecture de chaudière.** La cadence
de lecture ne dépend pas du broker ; `vclient` et la chaudière étaient joignables
ou non pendant la coupure, indépendamment de MQTT. La fraîcheur mesure l'âge
d'une **lecture**, jamais celui d'une publication. Et C7-B §5 pose explicitement
qu'un consommateur **MUST NOT** déduire de la présence la disponibilité de la
chaîne de lecture, portée par §8 : lier l'une à l'autre confondrait deux santés
que le contrat sépare.

Toute autre option — forcer une lecture, forcer un instantané, réinitialiser —
serait une décision métier nouvelle, non dérivable des invariants existants.
Aucune n'est prise.

---

## 13. Testament

**Contracté** :

- le testament est configuré **une seule fois, avant la connexion initiale**,
  par `connect(will=...)` ;
- **aucun second `will_set()`** n'est émis, ni après connexion, ni après
  reconnexion. Il serait sans effet sur la session en cours et redondant pour
  les suivantes ;
- Paho transporte le testament dans ses CONNECT ultérieurs (P11) : la
  reconnexion le conserve sans qu'aucune action ne soit requise.

**NON DÉMONTRÉ hors ligne** — à ne jamais présenter autrement :

- que le broker applique effectivement le testament sur coupure brutale ;
- qu'il conserve le retenu, et selon quelle politique ;
- le comportement réel de session (`clean_session` vaut `True`, donc une session
  neuve est attendue à chaque reconnexion — non vérifié en conditions réelles) ;
- le replay à un abonné tardif ;
- le délai entre la coupure et l'émission du testament, lié au keepalive du
  broker ;
- **l'ordre réel entre le `offline` du testament et le `online` de reprise.**

Ce dernier point est le risque résiduel principal du lot. Si un broker émettait
le testament tardivement, il pourrait écraser un `online` déjà republié. C11
**n'affirme pas** qu'un `online` de reprise l'emporte nécessairement sur un
testament tardif. Aucune clause ne repose sur cette hypothèse, et aucune ne doit
en reposer avant une validation contre un broker réel.

---

## 14. Déconnexion durable

C11 **conserve le comportement existant** et ne contracte aucune politique
définitive :

- le runtime peut rester vivant pendant une perte MQTT ;
- Paho conserve sa politique native de reconnexion, backoff compris (P10) ;
- C11 n'ajoute **aucun** délai maximal, aucun compteur d'échecs, aucune horloge ;
- C11 ne suspend **aucune** lecture ;
- C11 ne provoque **aucune** sortie de processus.

> **Comportement existant conservé, susceptible d'être reconsidéré lors du futur
> chantier d'exploitation et de service**, où la question du redémarrage se
> posera réellement.

Ce statu quo ne contredit pas la reprise : celle-ci n'a de sens que parce que le
pont survit à la coupure.

---

## 15. Compatibilité protocolaire

L'adaptateur emploie **MQTT 3.1.1**, valeur par défaut de Paho, avec
`clean_session = True`. Aucun réglage MQTT 5 n'est posé.

Paho v2 normalise la surface des rappels entre les deux protocoles : le code de
raison est un `ReasonCode` dans les deux cas, les propriétés sont un objet vide
plutôt que `None`, et les drapeaux existent dans les deux cas.

La couture définie ici ne dépend d'aucune propriété propre à MQTT 5, ni de
`session_present` (P5), ni de `is_disconnect_packet_from_server` (P7). **Aucune
nouvelle promesse de compatibilité n'est formulée.**

---

## 16. Propriétés à verrouiller

Le lot d'implémentation devra prouver, au minimum, les propriétés suivantes. Les
noms de tests ne sont pas fixés ici ; les propriétés le sont. Toutes sont
établissables hors ligne, sur doubles déterministes et horloge injectée.

### Défaut corrigé

1. `start()` puis déconnexion inattendue puis reconnexion réussie : le retenu
   `bridge/online` vaut `online`. **Ce test doit échouer sur le code
   d'aujourd'hui** — c'est la seule preuve que le lot corrige un fait réel.

### Transitions

2. CONNACK d'échec : aucune reprise, aucun `online`, aucune échéance modifiée.
3. Deux notifications de connexion successives sans déconnexion intermédiaire :
   **une seule** reprise au plus.
4. Connexion puis déconnexion **avant** consommation : **aucun** `online`.
5. Connexion, déconnexion, connexion : une reprise, l'état final étant connecté.
6. Connexion, déconnexion, connexion, déconnexion : **aucune** reprise.
7. Après `start()`, la notification du CONNACK initial ne provoque **aucune**
   republication.

### Arrêt

8. Aucune reprise lorsque `started` est faux.
9. L'arrêt prime : une reprise en attente au moment où l'arrêt est demandé ne
   produit aucun `online`.

### Forme de la publication

10. QoS **1**.
11. Retain **true**.
12. Topic exactement `<prefix>/bridge/online`, dérivé par l'autorité existante.
13. **Aucun** autre topic republié à l'occasion d'une reprise.

### Invariance

14. Échéances (`_next_due`, snapshot, battement) inchangées par une reconnexion.
15. Fraîcheur, `last_result` et statut de chaîne inchangés par une reconnexion.

### Fil

16. Le rappel de connexion est exerçable depuis un fil distinct du fil
    principal, et le test doit le **prouver**, non le supposer.
17. Le rappel ne bloque pas et ne laisse échapper aucune exception.
18. Aucune publication ni mutation du publieur n'a lieu depuis le fil du rappel.
19. Le module du publieur n'importe ni `paho`, ni `threading`, ni `asyncio`, et
    ne lit aucune horloge non injectée — vérification par inspection, comme les
    lots précédents.

### Doubles

20. Le double MQTT de `boilerack.testing` reproduit fidèlement la capacité : il
    permet de déclencher connexion et déconnexion, faute de quoi les tests du
    publieur resteraient aveugles à l'événement.
21. Une composition de la surface de lecture avec un client dépourvu de la
    capacité **échoue visiblement**.

### Course du premier CONNACK

Ces propriétés verrouillent §8.3. Les propriétés 24 et 26 portent sur une
**émission**, jamais sur une valeur retenue finale : c'est la seule façon de
distinguer « republié » de « n'a jamais eu besoin de l'être ».

22. Premier CONNACK **réussi** reçu **pendant** `start()`, avant sa fin : aucune
    reprise, et aucune émission de `bridge/online` au-delà de celle de `start()`.
23. Premier CONNACK **en échec** reçu pendant `start()` : l'état final de la
    primitive est **non connecté** — la base ne l'a pas écrasé.
24. Premier CONNACK en échec pendant `start()`, **puis** réussite : **exactement
    une** nouvelle émission `bridge/online` = `online`.
25. Premier CONNACK réussi : **aucune** republication redondante au premier
    cycle.
26. Premier CONNACK en échec : la première reprise légitime **n'est pas perdue**.
27. L'ouverture de connexion qui lève : exception propagée inchangée, publieur
    non démarré, aucune reprise consommable ensuite.

---

## 17. Mutations discriminantes

Aucun test n'est écrit à ce stade. **Aucune mutation n'est déclarée tuée.**

| # | Mutation | Propriété visée |
|---|---|---|
| 1 | Supprimer toute reprise | 1 |
| 2 | Reprendre sur déconnexion au lieu de connexion | 1, 4 |
| 3 | Reprendre après un CONNACK d'échec | 2 |
| 4 | Publier deux `online` pour une seule transition | 3 |
| 5 | Ne pas désarmer le marqueur sur déconnexion postérieure | 4, 6 |
| 6 | Ne pas désarmer à `start()` | 7 |
| 7 | Reprendre alors que `started` est faux | 8 |
| 8 | Inverser l'ordre arrêt / reprise dans la boucle | 9 |
| 9 | Publier avec `retain=False` | 11 |
| 10 | Publier en QoS 0 | 10 |
| 11 | Publier sur un topic voisin | 12, 13 |
| 12 | Réinitialiser une échéance à la reprise | 14 |
| 13 | Publier directement depuis le rappel Paho | 18 |
| 14 | Rendre le double incapable de déclencher l'événement | 20 |
| 15 | Émettre un second `will_set()` après reconnexion | §13 |
| 16 | Poser la base **après** l'ouverture de la connexion, ou après les publications | 23, 24, 26 |
| 17 | Faire que la base écrase une notification réelle déjà reçue | 23 |

---

## 18. Inconnues

Elles sont énumérées pour rester **des inconnues**. Aucune ne doit être
transformée en hypothèse normative, ni ici, ni dans l'implémentation.

| # | Inconnue | Conséquence |
|---|---|---|
| I1 | Comportement d'un broker réel : application du testament, conservation du retenu, politique de session | Toute la §13 reste non validée ; prolonge C7-B §15.5 |
| I2 | **Ordre réel entre un testament tardif `offline` et le `online` de reprise** | Un testament arrivant après la reprise pourrait l'écraser. Aucune clause ne suppose le contraire |
| I3 | Comportement de session réel avec `clean_session = True` | Non vérifié hors laboratoire |
| I4 | Validation contre un broker : rien de C11 n'a été éprouvé en ligne | Chantier séparé, sur autorisation explicite |
| I5 | Tolérance réelle des consommateurs à la latence de reprise retenue (§9.3) | Si elle s'avérait insuffisante, T2 devrait être instruit comme frontière propre |
| I6 | Politique future en déconnexion durable | Volontairement non tranchée (§14) |
| I7 | Comportement de Paho après un CONNACK refusé — la boucle retente-t-elle, et selon quel rythme | Non exercé hors ligne ; sans effet sur les clauses de C11, qui ne dépendent que de la notification reçue |

---

## 19. Ce que C11 ne fait pas

Aucune politique de reconnexion, de nouvelle tentative ou de reprise autre que
la présence · aucune modification du testament · aucun changement de topic, de
QoS, de rétention, de payload ou de période · aucun stockage de valeur scalaire ·
aucune réinitialisation d'échéance ou de fraîcheur · aucune sortie de processus ·
aucune suspension de lecture · aucune machine d'état · aucune file · aucun
réveil immédiat · aucun accès au chemin d'écriture.

**AUCUNE CONFORMITÉ PRODUCTION N'EST REVENDIQUÉE.** Rien n'a été éprouvé contre
un broker, un démon `vcontrold` ou une chaudière réels. Toutes les preuves
prévues sont hors ligne, sur doubles déterministes.

---

## 20. Renvois

`c7-mqtt-read-contract.md` — §5 présence, §8 santé de la chaîne, §11 surface des
suffixes, §15.5 et §15 #9 inconnues · `c7c3a-mqtt-presence.md` — pose du
testament, publication de présence, limitation de reconnexion nommée ·
`c7c3b-read-publisher.md` — cadences, échéances, absence de rattrapage,
limitation reportée · `c4-real-adapters.md` — doctrine A4 : aucune politique
métier de reconnexion, déconnexion exposée honnêtement · `c8-composition-root.md`
— racine de composition, boucle extérieure, injection des collaborateurs ·
`c9-process-lifecycle.md` — `SignalStop` et son descripteur de réveil, dont C11
n'use pas (§9.4).
