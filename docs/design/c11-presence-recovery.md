# C11 — Reprise de presence apres reconnexion MQTT

Document normatif. Il etend `c7-mqtt-read-contract.md` (C7-B) §5 au cas des
connexions reussies **posterieures** au demarrage initial.

C11 ne cree aucune doctrine parallele. Il ne modifie aucune valeur, aucun topic,
aucun QoS, aucune retention, aucune periode. Il rend executoire une obligation
deja ecrite que l'implementation n'honore qu'une seule fois.

---

## 1. Objet

C7-B §5 pose, pour le suffixe `bridge/online` :

| | |
|---|---|
| QoS | 1 |
| Retain | true |
| Payload | strictement `online` ou `offline` |
| **A la connexion** | **`online`** |
| Testament MQTT | `offline`, QoS 1, retain |
| A l'arret propre | `offline` avant deconnexion |

et pour semantique : « **le processus bridge est connecte au broker MQTT** ».

L'implementation actuelle ne publie `online` qu'a `start()`. Apres une
reconnexion, le processus est connecte et le retenu affirme le contraire. C11
comble exactement cet ecart, et rien d'autre.

---

## 2. Le defaut, etabli

### 2.1 Chaine en cause

Les etapes marquees `[Boilerack]` sont observees ; celle marquee `[attendu]`
depend d'un broker et n'a pas ete observee (§2.2).

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

La chaine a ete reproduite **hors ligne**, en n'employant que les coutures
existantes du depot : `PahoMqttClient` reel, faux client Paho des tests C4
(`fire_on_connect` / `fire_on_disconnect`), `ReadSurfacePublisher` reel,
`VirtualClock`. Apres l'etape de reconnexion : **zero** publication emise par
Boilerack, trois scalaires frais publies au cycle suivant, retenu de presence
toujours `offline`.

> **Portee de cette preuve.** Elle etablit ce que **Boilerack** fait et ne fait
> pas. Elle n'etablit rien du comportement d'un broker reel : l'application du
> testament y est **simulee**, non observee. Voir §13.

### 2.3 Cause structurelle

- `bridge/online` n'est publie qu'a un seul endroit du code, dans `start()` ;
  `offline` a un seul autre, dans `stop()`. `run_due()` ne touche jamais la
  presence.
- La frontiere `boilerack.transport.mqtt.MqttClient` expose cinq methodes —
  `connect`, `disconnect`, `subscribe`, `publish`, `set_message_handler` — et
  **aucune notification de cycle de connexion**. Le publieur est donc
  structurellement aveugle a une reconnexion, quand bien meme l'adaptateur la
  connait.

C'est une lacune de **couture**, pas de logique : il n'existe aujourd'hui aucun
chemin par lequel l'information pourrait parvenir a qui doit agir.

---

## 3. Statut de C11 vis-a-vis de C7-B

C11 est une **extension normative de C7-B §5 pour le cycle de reconnexion**.

Ce qui est deja dans C7-B et n'est pas cree ici : l'obligation de publier
`online` a la connexion · le topic · le QoS 1 · la retention · les deux payloads
admis · la semantique du topic · la separation entre presence MQTT (§5) et sante
de la chaine de lecture (§8).

Ce que C11 ajoute : **quelles connexions** declenchent cette obligation apres la
premiere, **par quel chemin** l'information circule, **quand** la publication a
lieu, et **ce qui l'annule**.

C7-B n'est pas modifie. Une seule reserve, traitee sans detour en §9 : C7-B ne
fixe aucun delai, ni pour §5 ni pour aucune autre publication, et son §15 #9
qualifie les cadences de « objectifs, non des garanties ». La borne temporelle
posee par C11 est donc une **precision** de §5, pas une derogation — mais elle
doit etre ecrite, et elle l'est.

L'inconnue C7-B §15.5 — politique de retention et d'expiration de session du
broker — **reste ouverte**. C11 ne la resout pas et ne s'appuie sur aucune
hypothese a son sujet.

---

## 4. Perimetre

### 4.1 Inclus — liste fermee

Detection des transitions pertinentes de connexion MQTT · transmission de cette
information de l'adaptateur jusqu'au fil metier · republication de
`bridge/online` · idempotence et coalescence · annulation d'une reprise en
attente · ordre vis-a-vis de l'arret · discipline de fil · temporalite et borne
de latence · invariance des echeances et de la fraicheur · obligations des
doubles · inconnues a lever contre un broker reel.

### 4.2 Exclus — liste fermee

Politique de reconnexion de Paho · modification du backoff · sortie du processus
sur deconnexion durable · suspension des lectures · nouvelle tentative
`vclient` · systemd · installation · Docker · Home Assistant · MQTT Discovery ·
topic de commande · ACK · ecriture chaudiere · nouveaux datapoints ·
modification des periodes de lecture · reinitialisation de la fraicheur ·
reinitialisation des echeances · second `will_set()` · champs morts
(`command_topic`, `ack_topic_prefix`, `write_timeout_s`) · `_legacy` · README ·
version ou release · CI, lint, typage, couverture · avertissement C9
`signal wakeup fd`.

---

## 5. Caracterisation Paho — constats, non obligations

Les faits ci-dessous decrivent la bibliotheque **reellement contrainte** par le
projet (`paho-mqtt>=2.1,<3`, version installee 2.1.0, Callback API `VERSION2`).
Ils justifient les clauses de C11 ; ils n'en sont pas.

| # | Constat |
|---|---|
| P1 | `on_connect` est appele pour **chaque** CONNACK : connexion initiale **et** reconnexion, sans aucune difference observable dans ses arguments |
| P2 | Signature `VERSION2` : `(client, userdata, connect_flags, reason_code, properties)`. `properties` n'est jamais `None` : un `Properties(CONNACK)` vide est substitue |
| P3 | Un succes se reconnait a `reason_code.is_failure == False`. `Success` vaut `0` ; `Not authorized` vaut `135` ; `Server unavailable` vaut `136`, tous deux en echec |
| P4 | `int(reason_code)` **leve** `TypeError` en 2.1.0. Seul le chemin `is_failure` est praticable pour un vrai `ReasonCode` |
| P5 | `connect_flags.session_present` est fourni en MQTT 3.1.1 comme en 5, mais vaut **toujours `False`** tant que `clean_session` reste a son defaut `True` — ce qui est le cas. **Inutilisable** pour distinguer une reprise |
| P6 | `on_disconnect` `VERSION2` : `(client, userdata, disconnect_flags, reason_code, properties)`. Arret volontaire -> `ReasonCode(0)`, `is_failure False`. Perte -> `ReasonCode(128)`, `is_failure True`. Keepalive expire -> `ReasonCode(141)`, `is_failure True` |
| P7 | `disconnect_flags.is_disconnect_packet_from_server` vaut **toujours `False`** en MQTT 3.1.1, protocole retenu par l'adaptateur : le broker n'y emet pas de DISCONNECT. **Inutilisable** |
| P8 | Les callbacks sont invoques depuis le **fil reseau de Paho**, cree par `loop_start()` et nomme `paho-mqtt-client-<client_id>`, jamais depuis le fil principal. Chaine : `_thread_main` -> `loop_forever` -> `_loop` -> `_packet_handle` -> `_handle_connack` -> `on_connect` |
| P9 | `suppress_exceptions` vaut `False` par defaut : une exception levee dans un callback est journalisee **puis relancee** dans la boucle reseau. Un callback qui bloque retarde keepalive, PUBACK et reception |
| P10 | La reconnexion automatique existe deja : `reconnect_on_failure` vaut `True`, backoff exponentiel de 1 s a 120 s. Un `disconnect()` volontaire met fin a la boucle — aucune reconnexion n'y succede |
| P11 | Le testament est **conserve par le client Paho** (`_will_topic`, `_will_payload`, `_will_qos`, `_will_retain`) et reempaquete par `_send_connect`, appele par `reconnect()`. Il est donc reemis dans chaque CONNECT ulterieur |
| P12 | `connect()` **n'attend aucun CONNACK** : son corps se reduit a `connect_async(...)` puis `reconnect()`, qui se termine par l'envoi du CONNECT. Le CONNACK est lu par le fil reseau, et **aucun backoff ne le retarde** — l'etat etant deja `CONNECTING`, la boucle d'amorcage sort immediatement et lit la socket. Un rappel peut donc survenir des que `loop_start()` a arme le fil, y compris **pendant** la suite du demarrage de l'appelant |
| P13 | `loop_stop()` **joint** le fil reseau avant de rendre la main. Apres un `disconnect()`, plus aucun rappel de la session close ne peut survenir |

### 5.1 Interdictions derivees

La norme Boilerack **MUST NOT** dependre de `session_present` (P5), de
`is_disconnect_packet_from_server` (P7), ni d'aucune propriete propre a MQTT 5.

La norme Boilerack **MUST NOT** ajouter, modifier ou desactiver la politique de
reconnexion native (P10) : elle en depend, elle ne la pilote pas.

---

## 6. Frontiere — capacite de cycle de connexion

### 6.1 Deux modeles compares

**Modele A — enrichir `MqttClient`.** Ajouter la notification au port MQTT
generique. Tout implementeur du port doit alors la fournir, y compris ceux qui
ne servent qu'au chemin transactionnel : `TransactionalCore` consomme
`MqttClient` pour publier des ACK et n'a aucun besoin de presence. Le port se
decrit lui-meme comme « frontiere MQTT minimale, sans politique » ; y loger une
capacite dont un consommateur sur deux n'a que faire l'elargit au-dela de son
objet.

**Modele B — capacite distincte, requise par la composition C11.** Le port MQTT
generique reste inchange. Une capacite separee porte la notification de cycle de
connexion. La surface de lecture, qui doit honorer §5, **exige les deux** ; le
coeur transactionnel n'exige que le port.

### 6.2 Modele retenu — B

Motif : segregation d'interface. La capacite est requise **la ou l'obligation
existe**, et nulle part ailleurs. Le port generique conserve la portee que son
propre texte lui donne.

Ce choix n'est **pas** motive par le nombre de doubles a mettre a jour. Il se
trouve qu'il en touche moins, mais ce n'est pas l'argument.

### 6.3 Rien d'optionnel

Une precedente analyse avait envisage une methode « optionnelle » sur
`MqttClient`. **Cette formule est rejetee.**

Un membre declare dans un `Protocol` Python n'est pas optionnel au sens
structurel : un implementeur qui l'omet ne satisfait plus le protocole, et
`runtime_checkable` ne verifie de toute facon que la presence des noms, jamais
les signatures. Surtout, la consequence serait fausse : **un client incapable de
signaler ses reconnexions rend le respect de C7-B §5 impossible**. Le tolerer
reviendrait a livrer une surface qui pretend honorer §5 sans le pouvoir.

Sont donc **INTERDITS** :

- `hasattr()` ou toute detection de capacite servant de repli silencieux ;
- l'absence de collaborateur toleree, la reprise etant alors simplement
  desactivee ;
- toute construction de la surface de lecture avec un client MQTT depourvu de la
  capacite.

La capacite est **REQUISE**. Une composition qui ne peut pas la fournir doit
echouer, visiblement, a la construction.

### 6.4 Forme

Trois elements, et rien de plus.

**a) Une capacite cote client.** Un protocole distinct portant une seule
methode, d'enregistrement, symetrique de `set_message_handler` :

```text
set_connection_handler(handler) -> None
```

Le rappel recoit **l'etat resultant**, un booleen : `True` pour « connexion
etablie », `False` pour « non connectee ». Il ne recoit ni code de raison, ni
drapeaux, ni proprietes : C11 n'en consomme aucun, et les exposer creerait une
surface de compatibilite sans consommateur.

**b) Une primitive d'etat de connexion.** Un objet dedie qui recoit les
transitions depuis n'importe quel fil et qu'un seul fil consomme. Sa
responsabilite est entiere et unique : repondre a « une reprise est-elle due
maintenant ? ». Elle est le pendant exact de `SignalStop` en C9 — meme role,
meme discipline, meme injection depuis la racine de composition.

**c) Un collaborateur requis de la surface de lecture.** Le publieur recoit
cette primitive a la construction. Elle **n'est pas optionnelle**.

La racine de composition cree la primitive, l'enregistre aupres du client et la
remet au publieur. Aucune autre partie du programme ne les relie.

### 6.5 Obligations de l'emetteur

Un implementeur de la capacite **MUST** :

- appeler le rappel avec `True` a **chaque** CONNACK de succes (`is_failure`
  faux) ;
- appeler le rappel avec `False` a **chaque** `on_disconnect`, quelle qu'en soit
  la raison ;
- appeler le rappel avec `False` a **chaque** CONNACK d'echec — la connexion
  n'est pas etablie, et le dire est le seul moyen de ne pas laisser un etat
  suppose survivre a un fait contraire ;
- ne **jamais** invoquer deux rappels concurremment ;
- ne **jamais** laisser une exception du rappel remonter vers Paho (P9).

Un implementeur **MUST NOT** interpreter, filtrer ni retarder les transitions :
la decision appartient au fil metier, jamais a l'adaptateur.

---

## 7. Discipline de fil

### 7.1 Invariant central

> **Aucune publication metier, aucune mutation de `ReadSurfacePublisher` ne doit
> avoir lieu depuis le fil reseau de Paho.**

Motif, etabli et non suppose : le publieur ne detient aucun verrou, mute
`_next_due`, `_state` et `_started` sans protection, et C7-C3B verrouille par
test qu'il n'importe ni `threading` ni `asyncio`. Publier depuis le fil reseau
introduirait des courses sur l'etat, un entrelacement de publications d'ordre
indefini, et exposerait la boucle reseau a une exception relancee (P9).

### 7.2 Ce que le rappel a le droit de faire

Le rappel **MUST** etre non bloquant, sur de l'acces concurrent, et ne **MUST
NOT** jamais lever. Il ne fait qu'enregistrer une transition dans la primitive
d'etat. Rien d'autre.

### 7.3 Ce que le publieur reste

Le module du publieur **MUST NOT** importer `paho`, `threading`, `asyncio`, ni
lire une horloge non injectee. C'est precisement pourquoi la primitive d'etat
est un **collaborateur injecte** et non un attribut interne : elle peut, elle,
employer un verrou.

Le traitement metier — decider, puis publier — reste integralement sur le fil du
runner.

---

## 8. Semantique des transitions

### 8.1 Le probleme d'un drapeau monotone

Un simple marqueur « une connexion est survenue », arme et jamais desarme avant
consommation, est **INTERDIT**. Il produirait ceci :

```text
connexion reussie        -> reprise en attente
deconnexion inattendue   -> le marqueur reste arme
consommation par le runner -> `online` publie alors que le pont est deconnecte
```

soit exactement le mensonge que C11 vient corriger, retourne.

### 8.2 Regle

La primitive conserve **l'etat courant** — connecte ou non — et un **marqueur de
transition**. Elle applique :

| Evenement | Effet sur l'etat | Effet sur le marqueur |
|---|---|---|
| Notification `True`, etat courant **non connecte** | devient connecte | **arme** |
| Notification `True`, etat courant **deja connecte** | inchange | inchange |
| Notification `False` | devient non connecte | **desarme** |
| Consommation, marqueur arme **et** etat connecte | inchange | desarme, la reprise est due |
| Consommation, tout autre cas | inchange | inchange, aucune reprise |

Invariant qui en decoule, et qui est la clause normative :

> **Au moment ou le fil metier consomme une reprise, la derniere transition MQTT
> observee doit encore etre une connexion reussie. Toute deconnexion posterieure
> a l'armement annule la reprise en attente.**

Une seule valeur booleenne suffit a porter le marqueur ; aucune file n'est
requise, et aucune ne doit etre introduite : la seule information utile est
« une reprise est-elle due », qui est idempotente et sans historique.

### 8.3 Etat initial et demarrage

`start()` ouvre la connexion, puis publie `online` — comportement etabli par
C7-C3A, inchange. La primitive doit donc partir d'une base coherente avec cette
annonce, faute de quoi le CONNACK initial armerait une reprise et ferait
republier `online` au premier cycle, pour rien.

**Aucun ordre entre le CONNACK et la suite de `start()` ne peut etre suppose.**
P12 l'etablit : l'ouverture n'attend pas le CONNACK, le fil reseau le lit des
son arrivee et aucun backoff ne le retarde. Un rappel peut donc survenir
**pendant** `start()`. Une redaction anterieure de cette clause posait la base
*apres* la publication de `online` et raisonnait sur « le CONNACK qui suit » :
cette relation d'ordre n'existe pas, et le raisonnement qu'elle portait etait
faux.

**Le danger n'est pas la republication redondante.** Un succes recu tot serait
de toute facon desarme par la pose de la base. Le danger est l'inverse, et il
est plus grave : **une base posee tard ecrase un echec reellement observe**.
L'etat redeviendrait « connecte » alors que la connexion a echoue ; la reussite
suivante ne serait plus une transition ; aucune reprise ne serait armee — et le
defaut que C11 corrige reapparaitrait entier, sur le chemin meme que cette
clause etait censee couvrir.

Clause : **`start()` place la primitive dans l'etat connecte et desarme tout
marqueur AVANT d'ouvrir la connexion**, c'est-a-dire avant l'appel qui rend un
rappel possible.

Cette place est sure **par construction, non par chronometrie** : les rappels ne
sont emis que par le fil reseau, ce fil n'existe pas avant `loop_start()` (P8),
et `loop_start()` est interne a l'ouverture de la connexion. Aucun rappel ne
peut donc preceder la base.

Il en decoule, sans qu'aucun ordre temporel ne soit suppose :

| Evenement | Etat | Reprise |
|---|---|---|
| Base posee par `start()` | connecte | desarmee |
| Premier CONNACK **reussi** | reste connecte — aucune transition | aucune |
| Premier CONNACK **en echec** (§6.5) | passe non connecte — **le fait observe a autorite sur la base** | aucune |
| Reussite **ulterieure**, apres un echec | transition non connecte -> connecte | **exactement une** |

La base reste optimiste : au moment ou elle est posee, aucun CONNACK n'a ete
recu. Elle l'est **exactement autant** que la publication de `online` qui la
suit, deja contractee ainsi. La difference tient a ceci : toute notification
reelle a desormais **autorite** sur elle, quel que soit l'instant ou elle
survient.

**Redemarrage.** `stop()` desarme le marqueur, et la deconnexion met fin a la
boucle reseau en joignant le fil (P13) : aucun rappel de la session close ne
peut survivre. Un `start()` ulterieur repose donc la base dans les memes
conditions de surete.

**Echec de l'ouverture.** Si l'ouverture leve, `start()` propage l'exception
telle quelle : la politique d'erreur existante n'est pas modifiee, et le
publieur reste non demarre. La primitive conserve alors une base « connecte,
desarmee » qui ne correspond a rien — mais cet etat est **fonctionnellement
inobservable** : une reprise n'est consommee qu'apres la verification de
demarrage, et un `start()` ulterieur repose la base. Aucun `try/except` ne doit
etre ajoute pour « nettoyer » cet etat : ce serait modifier une politique
d'erreur pour un etat que personne ne peut lire.

### 8.4 Connexions echouees

Un CONNACK dont `reason_code.is_failure` est vrai n'est **jamais** une connexion
reussie. Il n'arme aucune reprise, ne fait publier aucun `online`, et ne modifie
aucune echeance. Il fait uniquement passer l'etat a « non connecte » (§6.5).

---

## 9. Temporalite

### 9.1 Tension a resoudre

C7-B §5 dit « **a la connexion** : `online` ». Traiter la reprise sur le fil du
runner introduit un delai. Cette tension doit etre tranchee, pas contournee.

### 9.2 Options

**T1 — consommation au prochain reveil naturel du runner.** Aucune nouvelle
couture inter-fil ; modele mono-fil metier de C8/C9 integralement preserve ; la
reprise devient une tache due parmi les autres. Cout : la presence peut rester
`offline` jusqu'a la prochaine echeance.

**T2 — reveil immediat dedie.** Rapproche la publication de l'evenement. Cout :
une couture inter-fil supplementaire, et le risque de la confondre avec le
mecanisme de signaux de C9.

### 9.3 Decision — T1

**T1 est retenu.**

**Borne normative.** La latence de reprise est bornee par la prochaine echeance
du publieur, soit :

```text
latence_max = min(plus petite periode de mesure,
                  snapshot_period_s,
                  heartbeat_period_s si le battement est actif)
```

Avec la surface v1 et les valeurs par defaut — periodes 30 s et 60 s,
`snapshot_period_s = 30`, `heartbeat_period_s = 30` — cette borne vaut
**30 secondes**.

**Pourquoi c'est une lecture honnete de C7-B §5.** §5 prescrit **ce qui** doit
etre publie a la connexion ; il ne fixe **aucun** delai, et C7-B n'en fixe nulle
part : son §15 #9 range explicitement les cadences parmi les « objectifs, non
des garanties ». Une reprise bornee et annoncee satisfait donc §5. Ce qui le
violerait serait de ne jamais republier — le defaut d'aujourd'hui — ou de
republier sans borne connue.

**Ce qui ne doit pas etre ecrit.** Il est **INTERDIT** de presenter la reprise
comme immediate, instantanee ou synchrone de l'evenement de connexion. Elle ne
l'est pas, et la documentation utilisateur ne doit pas le laisser croire.

### 9.4 Interdiction explicite

Le socket de reveil de C9 **MUST NOT** servir de canal a C11.

Il a ete caracterise qu'un octet ne correspondant a aucun signal surveille
reveille `WakeupClock` sans armer l'arret, et se retrouve dans
`signaux_ignores`. **C'est une caracterisation, pas une interface.** Ce
descripteur est celui de `signal.set_wakeup_fd`, il appartient a la gestion des
signaux, et y faire transiter un evenement metier melangerait deux natures
d'evenements et polluerait un journal d'observabilite dedie aux signaux
etrangers.

Si un besoin de reprise plus rapide etait un jour demontre, T2 devrait etre
instruit comme une frontiere propre, avec sa propre couture. C11 ne l'ouvre pas.

---

## 10. Publication de reprise

### 10.1 Contenu

Apres une reprise due, le publieur publie **exactement un message** :

| | |
|---|---|
| Topic | `<prefix>/bridge/online`, derive par l'autorite existante `build_topic` |
| Payload | `online` |
| QoS | **1** |
| Retain | **true** |

Aucun autre topic n'est publie : ni scalaire, ni `bridge/telemetry_status`, ni
`bridge/heartbeat`, ni instantane.

### 10.2 Motifs

- Seul le retenu de presence a ete altere : le testament ne porte que sur
  `bridge/online`.
- Les scalaires sont publies **retenus**. Un message retenu appartient au broker
  et survit a la deconnexion du client qui l'a publie : il n'y a rien a
  restaurer.
- Boilerack **ne conserve aucune valeur scalaire en memoire**. `MeasurementState`
  porte trois champs — `last_success_wall`, `last_success_monotonic`,
  `last_result` — et aucune valeur. Republier des scalaires exigerait de stocker
  les valeurs, decision metier nouvelle, hors de cette frontiere.
- Aucun besoin de rafraichissement metier n'est demontre. Republier
  `telemetry_status` serait une redite : le testament ne l'a pas ecrase, et son
  contenu se recalculerait a l'identique.

### 10.3 Ordre dans la boucle

Le fil du runner consulte dans cet ordre :

```text
1. arret demande ?          -> si oui, sortir. Rien d'autre n'est fait.
2. reprise de presence due ? -> si oui, publier `online`.
3. travail periodique du.
```

Invariant : **l'arret prime toujours sur une reprise.** Il en decoule qu'aucun
`online` n'est publie apres le debut d'un arret, ni apres un `offline`.

L'obligation porte sur **l'ordre**, non sur son lieu d'ecriture. La realisation
la plus econome place l'etape 2 en tete de `run_due()`, ou la verification de
demarrage existe deja et ou l'etape 1 a necessairement precede : le runner reste
alors inchange. Une realisation dans la boucle du runner est admissible si elle
respecte le meme ordre.

---

## 11. Arret

L'autorite d'etat existante — le booleen `_started`, expose par la propriete
`started` — **suffit**. Aucune machine d'etat n'est creee : les etats « jamais
demarre » et « arrete » sont indiscernables par ce booleen, et **aucune decision
de C11 n'en depend** — dans les deux cas, rien n'est republie.

Clauses :

- `started == False` -> **aucune reprise**, en toute circonstance ;
- `stop()` rend le publieur non demarre **avant** de publier `offline` : une
  reprise consommee pendant un arret en cours trouve donc deja `started` faux ;
- un `disconnect()` volontaire ne genere aucune reprise. Il fait passer l'etat a
  « non connecte » (§6.5), ce qui desarme, et met fin a la boucle reseau de Paho
  (P10) : aucune notification de connexion ne peut plus survenir.

---

## 12. Echeances et fraicheur — invariance

Une reconnexion MQTT **MUST NOT** modifier :

`_next_due` de quelque mesure que ce soit · `_next_snapshot_due` ·
`_next_heartbeat_due` · `last_success_wall` · `last_success_monotonic` ·
`last_result` · l'etat de fraicheur (`age_s`, `fresh`) · `chain_status` ·
`chain_cause`.

Motif : **une reconnexion MQTT n'est pas une lecture de chaudiere.** La cadence
de lecture ne depend pas du broker ; `vclient` et la chaudiere etaient joignables
ou non pendant la coupure, independamment de MQTT. La fraicheur mesure l'age
d'une **lecture**, jamais celui d'une publication. Et C7-B §5 pose explicitement
qu'un consommateur **MUST NOT** deduire de la presence la disponibilite de la
chaine de lecture, portee par §8 : lier l'une a l'autre confondrait deux santes
que le contrat separe.

Toute autre option — forcer une lecture, forcer un instantane, reinitialiser —
serait une decision metier nouvelle, non derivable des invariants existants.
Aucune n'est prise.

---

## 13. Testament

**Contracte** :

- le testament est configure **une seule fois, avant la connexion initiale**,
  par `connect(will=...)` ;
- **aucun second `will_set()`** n'est emis, ni apres connexion, ni apres
  reconnexion. Il serait sans effet sur la session en cours et redondant pour
  les suivantes ;
- Paho transporte le testament dans ses CONNECT ulterieurs (P11) : la
  reconnexion le conserve sans qu'aucune action ne soit requise.

**NON DEMONTRE hors ligne** — a ne jamais presenter autrement :

- que le broker applique effectivement le testament sur coupure brutale ;
- qu'il conserve le retenu, et selon quelle politique ;
- le comportement reel de session (`clean_session` vaut `True`, donc une session
  neuve est attendue a chaque reconnexion — non verifie en conditions reelles) ;
- le replay a un abonne tardif ;
- le delai entre la coupure et l'emission du testament, lie au keepalive du
  broker ;
- **l'ordre reel entre le `offline` du testament et le `online` de reprise.**

Ce dernier point est le risque residuel principal du lot. Si un broker emettait
le testament tardivement, il pourrait ecraser un `online` deja republie. C11
**n'affirme pas** qu'un `online` de reprise l'emporte necessairement sur un
testament tardif. Aucune clause ne repose sur cette hypothese, et aucune ne doit
en reposer avant une validation contre un broker reel.

---

## 14. Deconnexion durable

C11 **conserve le comportement existant** et ne contracte aucune politique
definitive :

- le runtime peut rester vivant pendant une perte MQTT ;
- Paho conserve sa politique native de reconnexion, backoff compris (P10) ;
- C11 n'ajoute **aucun** delai maximal, aucun compteur d'echecs, aucune horloge ;
- C11 ne suspend **aucune** lecture ;
- C11 ne provoque **aucune** sortie de processus.

> **Comportement existant conserve, susceptible d'etre reconsidere lors du futur
> chantier d'exploitation et de service**, ou la question du redemarrage se
> posera reellement.

Ce statu quo ne contredit pas la reprise : celle-ci n'a de sens que parce que le
pont survit a la coupure.

---

## 15. Compatibilite protocolaire

L'adaptateur emploie **MQTT 3.1.1**, valeur par defaut de Paho, avec
`clean_session = True`. Aucun reglage MQTT 5 n'est pose.

Paho v2 normalise la surface des rappels entre les deux protocoles : le code de
raison est un `ReasonCode` dans les deux cas, les proprietes sont un objet vide
plutot que `None`, et les drapeaux existent dans les deux cas.

La couture definie ici ne depend d'aucune propriete propre a MQTT 5, ni de
`session_present` (P5), ni de `is_disconnect_packet_from_server` (P7). **Aucune
nouvelle promesse de compatibilite n'est formulee.**

---

## 16. Proprietes a verrouiller

Le lot d'implementation devra prouver, au minimum, les proprietes suivantes. Les
noms de tests ne sont pas fixes ici ; les proprietes le sont. Toutes sont
etablissables hors ligne, sur doubles deterministes et horloge injectee.

### Defaut corrige

1. `start()` puis deconnexion inattendue puis reconnexion reussie : le retenu
   `bridge/online` vaut `online`. **Ce test doit echouer sur le code
   d'aujourd'hui** — c'est la seule preuve que le lot corrige un fait reel.

### Transitions

2. CONNACK d'echec : aucune reprise, aucun `online`, aucune echeance modifiee.
3. Deux notifications de connexion successives sans deconnexion intermediaire :
   **une seule** reprise au plus.
4. Connexion puis deconnexion **avant** consommation : **aucun** `online`.
5. Connexion, deconnexion, connexion : une reprise, l'etat final etant connecte.
6. Connexion, deconnexion, connexion, deconnexion : **aucune** reprise.
7. Apres `start()`, la notification du CONNACK initial ne provoque **aucune**
   republication.

### Arret

8. Aucune reprise lorsque `started` est faux.
9. L'arret prime : une reprise en attente au moment ou l'arret est demande ne
   produit aucun `online`.

### Forme de la publication

10. QoS **1**.
11. Retain **true**.
12. Topic exactement `<prefix>/bridge/online`, derive par l'autorite existante.
13. **Aucun** autre topic republie a l'occasion d'une reprise.

### Invariance

14. Echeances (`_next_due`, snapshot, battement) inchangees par une reconnexion.
15. Fraicheur, `last_result` et statut de chaine inchanges par une reconnexion.

### Fil

16. Le rappel de connexion est exercable depuis un fil distinct du fil
    principal, et le test doit le **prouver**, non le supposer.
17. Le rappel ne bloque pas et ne laisse echapper aucune exception.
18. Aucune publication ni mutation du publieur n'a lieu depuis le fil du rappel.
19. Le module du publieur n'importe ni `paho`, ni `threading`, ni `asyncio`, et
    ne lit aucune horloge non injectee — verification par inspection, comme les
    lots precedents.

### Doubles

20. Le double MQTT de `boilerack.testing` reproduit fidelement la capacite : il
    permet de declencher connexion et deconnexion, faute de quoi les tests du
    publieur resteraient aveugles a l'evenement.
21. Une composition de la surface de lecture avec un client depourvu de la
    capacite **echoue visiblement**.

### Course du premier CONNACK

Ces proprietes verrouillent §8.3. Les proprietes 24 et 26 portent sur une
**emission**, jamais sur une valeur retenue finale : c'est la seule facon de
distinguer « republie » de « n'a jamais eu besoin de l'etre ».

22. Premier CONNACK **reussi** recu **pendant** `start()`, avant sa fin : aucune
    reprise, et aucune emission de `bridge/online` au-dela de celle de `start()`.
23. Premier CONNACK **en echec** recu pendant `start()` : l'etat final de la
    primitive est **non connecte** — la base ne l'a pas ecrase.
24. Premier CONNACK en echec pendant `start()`, **puis** reussite : **exactement
    une** nouvelle emission `bridge/online` = `online`.
25. Premier CONNACK reussi : **aucune** republication redondante au premier
    cycle.
26. Premier CONNACK en echec : la premiere reprise legitime **n'est pas perdue**.
27. L'ouverture de connexion qui leve : exception propagee inchangee, publieur
    non demarre, aucune reprise consommable ensuite.

---

## 17. Mutations discriminantes

Aucun test n'est ecrit a ce stade. **Aucune mutation n'est declaree tuee.**

| # | Mutation | Propriete visee |
|---|---|---|
| 1 | Supprimer toute reprise | 1 |
| 2 | Reprendre sur deconnexion au lieu de connexion | 1, 4 |
| 3 | Reprendre apres un CONNACK d'echec | 2 |
| 4 | Publier deux `online` pour une seule transition | 3 |
| 5 | Ne pas desarmer le marqueur sur deconnexion posterieure | 4, 6 |
| 6 | Ne pas desarmer a `start()` | 7 |
| 7 | Reprendre alors que `started` est faux | 8 |
| 8 | Inverser l'ordre arret / reprise dans la boucle | 9 |
| 9 | Publier avec `retain=False` | 11 |
| 10 | Publier en QoS 0 | 10 |
| 11 | Publier sur un topic voisin | 12, 13 |
| 12 | Reinitialiser une echeance a la reprise | 14 |
| 13 | Publier directement depuis le rappel Paho | 18 |
| 14 | Rendre le double incapable de declencher l'evenement | 20 |
| 15 | Emettre un second `will_set()` apres reconnexion | §13 |
| 16 | Poser la base **apres** l'ouverture de la connexion, ou apres les publications | 23, 24, 26 |
| 17 | Faire que la base ecrase une notification reelle deja recue | 23 |

---

## 18. Inconnues

Elles sont enumerees pour rester **des inconnues**. Aucune ne doit etre
transformee en hypothese normative, ni ici, ni dans l'implementation.

| # | Inconnue | Consequence |
|---|---|---|
| I1 | Comportement d'un broker reel : application du testament, conservation du retenu, politique de session | Toute la §13 reste non validee ; prolonge C7-B §15.5 |
| I2 | **Ordre reel entre un testament tardif `offline` et le `online` de reprise** | Un testament arrivant apres la reprise pourrait l'ecraser. Aucune clause ne suppose le contraire |
| I3 | Comportement de session reel avec `clean_session = True` | Non verifie hors laboratoire |
| I4 | Validation contre un broker : rien de C11 n'a ete eprouve en ligne | Chantier separe, sur autorisation explicite |
| I5 | Tolerance reelle des consommateurs a la latence de reprise retenue (§9.3) | Si elle s'averait insuffisante, T2 devrait etre instruit comme frontiere propre |
| I6 | Politique future en deconnexion durable | Volontairement non tranchee (§14) |
| I7 | Comportement de Paho apres un CONNACK refuse — la boucle retente-t-elle, et selon quel rythme | Non exerce hors ligne ; sans effet sur les clauses de C11, qui ne dependent que de la notification recue |

---

## 19. Ce que C11 ne fait pas

Aucune politique de reconnexion, de nouvelle tentative ou de reprise autre que
la presence · aucune modification du testament · aucun changement de topic, de
QoS, de retention, de payload ou de periode · aucun stockage de valeur scalaire ·
aucune reinitialisation d'echeance ou de fraicheur · aucune sortie de processus ·
aucune suspension de lecture · aucune machine d'etat · aucune file · aucun
reveil immediat · aucun acces au chemin d'ecriture.

**AUCUNE CONFORMITE PRODUCTION N'EST REVENDIQUEE.** Rien n'a ete eprouve contre
un broker, un demon `vcontrold` ou une chaudiere reels. Toutes les preuves
prevues sont hors ligne, sur doubles deterministes.

---

## 20. Renvois

`c7-mqtt-read-contract.md` — §5 presence, §8 sante de la chaine, §11 surface des
suffixes, §15.5 et §15 #9 inconnues · `c7c3a-mqtt-presence.md` — pose du
testament, publication de presence, limitation de reconnexion nommee ·
`c7c3b-read-publisher.md` — cadences, echeances, absence de rattrapage,
limitation reportee · `c4-real-adapters.md` — doctrine A4 : aucune politique
metier de reconnexion, deconnexion exposee honnetement · `c8-composition-root.md`
— racine de composition, boucle exterieure, injection des collaborateurs ·
`c9-process-lifecycle.md` — `SignalStop` et son descripteur de reveil, dont C11
n'use pas (§9.4).
