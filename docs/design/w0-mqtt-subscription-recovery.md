# W0 — Persistance fonctionnelle des souscriptions MQTT

Document normatif. Il fixe ce qu'il advient d'une **souscription demandée à
`PahoMqttClient`** lorsque la connexion est rétablie.

W0 ne modifie **aucun comportement métier**. Il ne redéfinit ni la présence
(C7-B, C7-C3A, C11), ni la politique de reconnexion (C4), ni la cadence de
lecture (C7). Il comble une lacune de l'adaptateur MQTT réel : `subscribe` n'a
aujourd'hui **aucun contrat**, et rien n'établit ce qu'une souscription devient
après une reconnexion.

**W0 n'ouvre aucune voie de commande.** Aucun topic de commande n'est souscrit,
aucun acquittement n'est publié, aucun cœur transactionnel n'est instancié.

---

## 1. Objet

C4 §« Éléments reportés » a explicitement différé la **politique de
reconnexion**. C11 a ensuite traité un cas précis de ce report — la reprise de
présence — sans aborder les souscriptions : sa liste fermée d'exclusions (§4.2)
n'en dit rien, ni pour les inclure, ni pour les exclure.

Le corpus est donc **silencieux**. Or il contient déjà la prémisse du problème,
en C11 §13 :

> « le comportement réel de session (`clean_session` vaut `True`, donc une
> session neuve est attendue à chaque reconnexion — non vérifié en conditions
> réelles) »

La conséquence n'y est jamais tirée : **si la session est neuve, les
souscriptions de la session précédente n'existent plus.** W0 tire cette
conséquence et fixe ce que l'adaptateur doit en faire.

W0 est à C4 ce que C11 est à C7-B : une **extension normative** d'un contrat
antérieur, sur un cycle que celui-ci avait laissé ouvert.

---

## 2. Portée du contrat

**Clause normative.** W0 porte sur **`PahoMqttClient`** et sur son mécanisme
interne de restauration après reconnexion. Il **ne redéfinit pas** la sémantique
générale de la frontière abstraite `MqttClient`.

Cette délimitation n'est pas de confort. `FakeMqttClient.subscribe` **lève
`NotConnectedError`** lorsque le client n'est pas connecté, comportement figé et
couvert par un test existant. Étendre à toute implémentation de `MqttClient` la
règle d'enregistrement inconditionnel de §7 invaliderait cette sémantique, et
W0 n'a aucune raison de le faire : le problème qu'il corrige — la perte
silencieuse d'une souscription lors d'une reconnexion **réelle** — n'existe que
là où une reconnexion réelle existe, c'est-à-dire dans l'adaptateur Paho.

Conséquences, à énoncer clairement :

- la frontière `MqttClient` **n'acquiert aucune obligation nouvelle** ;
- les doubles de test conservent leur sémantique propre, y compris hors
  connexion ;
- un consommateur ne doit **pas** déduire de W0 qu'une implémentation
  quelconque de `MqttClient` enregistre ses souscriptions.

Cette portée reste compatible avec W1 à W3 : ceux-ci consommeront l'adaptateur
réel par la racine de composition (C8), seul endroit où il est câblé.

---

## 3. Autorités et acquis

Ce que W0 **reprend sans le redéfinir**, vérifié dans le dépôt :

| # | Acquis | Origine | Preuve |
|---|---|---|---|
| A1 | Aucune politique métier de reconnexion n'est ajoutée : ni boucle maison, ni retry métier ; la reconnexion relève du comportement natif de Paho | C4 §« Connexion / reconnexion » | contrat C4 |
| A2 | `on_connect` est appelé pour **chaque** CONNACK — connexion initiale **et** reconnexion — sans différence observable dans ses arguments | C11 P1 | contrat C11 |
| A3 | Un CONNACK en échec n'est **jamais** une connexion établie | C11 §8 | `_on_connect` de l'adaptateur |
| A4 | La reconnexion automatique de Paho existe déjà ; un `disconnect()` volontaire met fin à la boucle et **aucune reconnexion n'y succède** | C11 P10 | contrat C11 |
| A5 | Un rappel peut survenir **pendant** la suite du démarrage de l'appelant : `connect()` n'attend aucun CONNACK | C11 P12 | contrat C11 |
| A6 | **Aucun rappel externe n'est appelé sous verrou** — invariant du module, énoncé pour les rappels | `mqtt_paho`, commentaire de `_on_connect` | code de l'adaptateur |
| A7 | Une exception d'un rappel est **capturée et journalisée**, jamais propagée dans la boucle Paho | C4 §« Entrée des messages » | contrat C4 |
| A8 | `clean_session` vaut `True` : une session neuve est attendue à chaque reconnexion, **non vérifié en conditions réelles** | C11 §13 | contrat C11 |
| A9 | Le testament est conservé par le client Paho et réémis dans chaque CONNECT ; aucune action n'est requise | C11 P11 | contrat C11 |
| A10 | Le type `Subscription` existe déjà : `topic` et `qos`, documenté « souscription demandée » | `transport/mqtt.py` | code |

**Faits constatés dans le code, et non supposés** : `MqttClient.subscribe` est
déclaré sans aucune documentation — son corps de protocole se réduit à `...` —
et `PahoMqttClient.subscribe` se réduit à un relais vers Paho dont la valeur de
retour est **ignorée**. Aucun registre de souscriptions n'existe, et
`_on_connect` n'en restaure aucune.

---

## 4. Hors périmètre — liste fermée

Topic de commande · souscription au topic de commande · acquittements ·
`command_topic` · `ack_topic_prefix` · `write_timeout_s` · `TransactionalCore`
en runtime · `VClient.write` · profil réel · `process_next` · politique de
reconnexion de Paho · modification du backoff · session persistante côté broker
(`clean_session=False`) · sortie du processus sur déconnexion durable ·
supervision métier d'un réabonnement en échec · **surface d'erreur de
`subscribe` rendue à l'appelant** · `unsubscribe` · **corrélation SUBACK** ·
**rappel `on_subscribe`** · **registre de `mid` de souscription** · **preuve
d'acceptation par le broker** · découverte MQTT · Home Assistant · systemd ·
installation · terrain · modification de C4, C7, C7-C3A, C7-C3B, C8, C9, C10,
C11, C12 ou C13.

**En particulier, W0 ne câble aucune voie entrante.** Il rend une primitive
robuste ; il ne s'en sert pas.

**Et W0 ne garantit que la RÉÉMISSION d'un SUBSCRIBE**, jamais qu'une
souscription soit devenue active côté broker : sans corrélation SUBACK, cette
acceptation n'est ni observée, ni observable hors terrain.

---

## 5. Le défaut, énoncé sans atténuation

Aujourd'hui, une souscription demandée est transmise à Paho une fois, et rien
ne la redemande. Après une reconnexion — que la session soit neuve (A8) ou que
le broker l'ait oubliée pour toute autre raison — l'adaptateur **ne réémet aucun
SUBSCRIBE**.

Le processus resterait vivant, la boucle de lecture continuerait de publier sa
télémétrie, et C11 republierait `online`. Rien ne signalerait que plus aucun
message entrant n'arrive.

C'est la nature de ce défaut qui le rend bloquant, et non sa probabilité : la
perte de présence que C11 a corrigée était **observable chez le broker** ; une
souscription perdue est **silencieuse**. Un pont de commande qui cesse d'obéir
sans le dire est plus dangereux qu'un pont qui s'arrête.

---

## 6. Souscription logique

**Définition normative.** Une **souscription logique** est un couple
`(topic, qos)` que l'appelant a demandé à l'adaptateur par `subscribe`.

Elle correspond exactement au type `Subscription` déjà présent dans
`transport/mqtt.py` — mêmes champs, même sens documenté, « souscription
demandée » (A10). W0 **ne crée aucun type nouveau** ; il rend normatif ce que ce
type désignait déjà.

Elle est une **déclaration d'intention de l'appelant**, distincte de la
souscription MQTT effective détenue par le broker. W0 ne fait aucune
affirmation sur la seconde : il garantit seulement que la première est
**réémise**.

Cette distinction n'est pas verbale. Elle est la raison pour laquelle W0 peut
être entièrement prouvé hors ligne : ce qui est vérifiable sans broker est ce
que l'adaptateur **demande**, jamais ce que le broker **retient**.

---

## 7. Enregistrement

**Clause normative.** Tout appel à `PahoMqttClient.subscribe(topic, qos)`
enregistre la souscription logique correspondante, **puis** la transmet au
client Paho.

L'enregistrement précède la transmission, et il a lieu **inconditionnellement** :
il ne dépend ni de l'état de la connexion, ni de l'issue de la transmission.

Motif : l'enregistrement traduit l'intention de l'appelant, qui ne change pas
selon l'état du réseau. Le conditionner ferait dépendre une déclaration d'un
fait de transport, et rouvrirait le défaut de §5 par un autre chemin.

### 7.1 Irrétractabilité — conséquence explicite

Trois clauses se combinent : l'enregistrement est inconditionnel (§7), aucun
`unsubscribe` n'existe (§12), et le registre vit aussi longtemps que l'objet
client (§13).

**Il en résulte une conséquence que ce contrat énonce plutôt que de la laisser
déduire :**

> Si la transmission directe d'un `subscribe` échoue, **l'intention locale reste
> enregistrée**, et elle sera réémise au prochain CONNACK réussi. L'appelant ne
> dispose d'**aucun mécanisme de retrait**.

Autrement dit, une souscription demandée une fois, même sans succès immédiat,
engage l'adaptateur jusqu'à la fin de vie de l'objet. C'est un effet voulu — il
est la contrepartie exacte de la persistance recherchée — mais il doit être
connu de l'appelant avant qu'il n'appelle.

Si un besoin de retrait apparaît, il fera l'objet d'une clause propre, jamais
d'un ajout opportuniste (§12).

---

## 8. Restauration après CONNACK réussi

**Clause normative.** À chaque CONNACK **réussi**, l'adaptateur réémet
**toutes** les souscriptions logiques enregistrées.

- Un CONNACK **en échec** ne réémet **rien** (A3) : une connexion non établie
  n'a aucune souscription à restaurer.
- La restauration porte sur **toutes** les souscriptions, jamais sur un
  sous-ensemble.
- Chaque souscription est réémise avec **exactement** le `topic` et le `qos`
  enregistrés.

**Connexion initiale et reconnexion ne sont pas distinguées**, et ne doivent pas
l'être. A2 établit que `on_connect` ne permet pas de les distinguer ; fabriquer
un compteur de connexions pour y parvenir introduirait un état que rien
n'exige. La règle est donc uniforme, et son effet sur la connexion initiale est
nul par construction : à ce moment le registre est vide, sauf si l'appelant a
déjà souscrit — auquel cas réémettre est précisément ce qu'il faut faire.

**Conséquence assumée** : si l'appelant souscrit alors que le CONNACK est déjà
arrivé, un même `(topic, qos)` peut être **émis** deux fois — une fois par
`subscribe`, une fois par la restauration d'un CONNACK ultérieur. Le registre,
lui, n'en contient qu'une entrée (§10). **W0 ne dit rien de l'effet de cette
seconde émission chez le broker** : ce serait affirmer un comportement non
observé.

---

## 9. Ordre

**Clause normative.** La restauration réémet les souscriptions dans **l'ordre où
elles ont été enregistrées la première fois**.

Motif : c'est le seul ordre **déterministe** que le registre porte déjà. Tout
autre — tri par topic, tri par QoS, ordre de dernière déclaration — serait une
décision arbitraire, et un ordre non spécifié rendrait la propriété intestable.

**Clause normative sur l'ordre vis-à-vis de C11.** Dans le traitement d'un
CONNACK, la **mise à jour de l'état de connexion et la notification de présence
précèdent la restauration des souscriptions**.

Motif, et il est dérivé : la notification de présence est une écriture en
mémoire qui n'échoue pas, tandis que la restauration sollicite le réseau et
peut échouer. Placer la première en tête garantit que **C11 n'est jamais dégradé
par une défaillance de W0**. L'ordre inverse ferait dépendre la reprise de
présence — déjà contractée et éprouvée — d'un mécanisme ajouté après elle.

**Clause normative complémentaire** : la notification de présence **MUST NOT**
être conditionnée à l'issue de la restauration. Elle a lieu que la restauration
réussisse, échoue, ou n'ait rien à faire.

---

## 10. Doublons et QoS

| Cas | Règle | Motif |
|---|---|---|
| Même `topic`, même `qos`, deux fois | Le registre n'en conserve **qu'une entrée**. Le second appel est **transmis** à Paho comme le premier | L'appelant a demandé deux fois ; l'adaptateur n'a pas à taire une demande. Le registre, lui, décrit un état, pas un journal |
| Même `topic`, `qos` différent | Le registre conserve **le dernier `qos` déclaré** | Restaurer un `qos` que l'appelant a depuis remplacé rétablirait une intention périmée. Le dernier appel est le seul qui exprime l'intention courante |
| Topics différents | Chacun est enregistré ; **tous** sont restaurés | §8 |

**Aucune multiplication interne.** Le registre est indexé par `topic` : quel que
soit le nombre d'appels et de reconnexions, il ne contient jamais deux entrées
pour un même topic. Une croissance du registre au fil des reconnexions serait
une **violation**.

Ces règles portent **exclusivement sur le registre local**. W0 ne contractualise
aucun comportement du broker face à des SUBSCRIBE répétés sur un même filtre.

---

## 11. Échec de la restauration

**Clause normative.** Un échec de réémission :

1. **MUST** être rendu **observable** par journalisation, avec le topic
   concerné ;
2. **MUST NOT** être propagé dans la boucle Paho — par analogie directe avec
   A7, qui l'impose déjà pour une exception de rappel ;
3. **MUST NOT** retirer la souscription du registre : elle reste déclarée, et
   sera réémise au CONNACK suivant ;
4. **MUST NOT** être présenté comme un succès, ni faire croire que la
   souscription est rétablie.

**Aucune politique de supervision n'est créée par W0.** L'adaptateur rend le
défaut visible ; décider ce qu'un superviseur en fait — dégrader un état de
santé, sortir du processus, alerter — appartient à un lot ultérieur, et exige
une clause contractuelle propre.

### 11.1 Ce que W0 ne définit pas : la surface d'erreur de `subscribe`

W0 **ne définit aucune nouvelle forme de retour** pour un appel direct à
`subscribe` : ni exception, ni booléen, ni code de retour, ni aucun autre
mécanisme rendu à l'appelant.

Motif : cela sort de l'objet du lot — la persistance et la réémission des
intentions — et la forme d'un échec côté Paho n'est pas éprouvée. En faire une
obligation contractuelle reviendrait à inventer une API sur une base non
observée.

**Fait, non garantie** : l'adaptateur ignore aujourd'hui la valeur de retour de
`subscribe` côté Paho. W0 ne change pas ce fait et n'en fait pas une promesse.
Une éventuelle surface d'erreur relèvera d'un lot dédié.

### 11.2 `online` ne signifie pas « souscriptions restaurées »

**Limitation explicite, et non un risque à découvrir plus loin.**

La présence `online` publiée par C11 atteste **une connexion MQTT établie**,
rien de plus. Elle **ne signifie pas** que les souscriptions ont été restaurées,
ni qu'elles l'ont été avec succès.

Un échec de restauration peut donc **coexister** avec un état de présence
`online` parfaitement à jour. C'est une conséquence directe de §9 — la présence
précède la restauration et ne dépend pas de son issue — et c'est voulu : lier
les deux ferait de la présence un indicateur composite dont C7-B §5 a
explicitement séparé les significations.

**W0 ne crée aucun nouvel indicateur de santé.**

---

## 12. Absence de retrait

`MqttClient` **n'expose pas** `unsubscribe`, et W0 **ne l'ajoute pas** : aucun
appelant n'en a besoin, et l'ajouter créerait une surface sans consommateur.

**Conséquence à énoncer clairement** : une souscription logique, une fois
déclarée, l'est pour toute la durée de vie de l'objet client. Il n'existe aucun
chemin pour la retirer — voir §7.1, qui en tire l'effet complet.

---

## 13. Déconnexion volontaire

**Clause normative.** `disconnect()` ne vide **pas** le registre.

Motif : le registre porte des **déclarations de l'appelant** (§6), et une
déconnexion ne retire aucune déclaration — d'autant qu'aucun chemin de retrait
n'existe (§12). Si le même objet client était reconnecté par un `connect()`
explicite, ses souscriptions seraient donc restaurées au CONNACK, exactement
comme après une reconnexion automatique.

**Ce cas n'est pas atteignable dans le runtime actuel** : A4 établit qu'aucune
reconnexion ne succède à un `disconnect()` volontaire, et C9 arrête le processus
après l'arrêt du publieur. La règle est néanmoins fixée, parce qu'un
comportement indéterminé sur un chemin inatteignable devient un piège dès que le
chemin s'ouvre.

---

## 14. Concurrence

**Le scénario de course est réel, et il est démontré par le corpus, non
supposé.** C11 P12 établit qu'un rappel peut survenir **pendant** la suite du
démarrage de l'appelant. Un appelant qui souscrirait juste après `connect()`
écrirait donc dans le registre pendant que le fil réseau de Paho pourrait le
lire dans `_on_connect`.

**Clause normative** : l'accès au registre — écriture par `subscribe`, lecture
par la restauration — **MUST** être protégé, et la restauration **MUST** opérer
sur un **instantané** du registre plutôt que sur la structure vivante, afin
qu'un appel concurrent ne la modifie pas en cours de parcours.

**Clause normative, exigence propre à W0** : aucune émission vers le client Paho
**ne doit avoir lieu sous verrou**.

Cette règle est **dérivée** du modèle de verrouillage existant du module, non
reprise telle quelle : A6 énonce que les *rappels externes* ne sont pas appelés
sous verrou, et le module pratique déjà la même retenue autour de
`client.publish()`. W0 étend explicitement cette discipline à l'émission des
SUBSCRIBE, et l'assume comme une exigence nouvelle plutôt que comme la citation
d'un acquis.

Aucune primitive nouvelle n'est requise : le module possède déjà un verrou.
W0 ne crée ni fil, ni file, ni machine à états.

---

## 15. Ce que W0 ne prétend pas

À écrire tel quel, sans atténuation :

- W0 **n'affirme pas** que le broker retient les souscriptions, ni qu'il les
  oublie : il garantit seulement que l'adaptateur les **redemande** ;
- W0 **n'affirme rien** de l'effet d'un SUBSCRIBE répété sur un même filtre ;
- W0 **ne prouve pas** qu'un SUBSCRIBE réémis est **accepté** : sans corrélation
  SUBACK, l'acceptation n'est ni observée ni observable hors terrain ;
- W0 **n'introduit pas** de session persistante. `clean_session` reste `True`,
  et l'inconnue de C11 §13 reste entière ;
- W0 **ne garantit aucune fenêtre** pendant laquelle aucun message ne serait
  perdu. Entre la coupure et la réémission, des messages publiés par un tiers
  peuvent être perdus, et rien ici ne l'empêche ;
- W0 **ne rend pas** la voie de commande fiable : il en supprime un obstacle ;
- W0 **ne donne à `online` aucun sens nouveau** (§11.2).

---

## 16. Propriétés à verrouiller

Le lot d'implémentation devra prouver, au minimum, les propriétés suivantes.
Chacune porte **une seule** obligation ; les noms de tests ne sont pas fixés ici.

| # | Propriété |
|---|---|
| W-P1 | Un registre local des souscriptions logiques existe, **indexé par topic** |
| W-P2 | L'enregistrement a lieu **avant** la transmission au client |
| W-P3 | L'enregistrement est **conservé** lorsque la transmission directe échoue |
| W-P4 | Un CONNACK **réussi** réémet **toutes** les souscriptions enregistrées |
| W-P5 | Un CONNACK **en échec** ne réémet **aucune** souscription |
| W-P6 | Chaque réémission porte le **`qos` exact** enregistré |
| W-P7 | L'ordre de restauration est celui du **premier** enregistrement de chaque topic |
| W-P8 | Deux déclarations du même topic ne produisent **qu'une** entrée de registre |
| W-P9 | Un `qos` redéclaré **remplace** le précédent dans le registre |
| W-P10 | Des reconnexions successives restaurent à chaque fois **sans faire croître** le registre |
| W-P11 | `disconnect()` **conserve** le registre |
| W-P12 | La notification de présence C11 **précède** la restauration |
| W-P13 | La notification de présence C11 **n'est pas conditionnée** à l'issue de la restauration |
| W-P14 | Un échec de réémission est **journalisé**, avec le topic concerné |
| W-P15 | Un échec de réémission **n'est pas propagé** dans la boucle Paho |
| W-P16 | Un échec de réémission **ne retire pas** la souscription du registre |
| W-P17 | Aucune émission vers le client n'a lieu **sous verrou** |
| W-P18 | Aucun topic jamais déclaré n'est jamais émis |
| W-P19 | Aucun topic de commande, aucun acquittement, aucun cœur transactionnel n'est introduit |
| W-P20 | Aucune corrélation SUBACK, aucun rappel `on_subscribe`, aucun registre de `mid` de souscription n'est introduit |
| W-P21 | `clean_session` demeure inchangé : aucune session persistante n'est introduite |
| W-P22 | La sémantique hors connexion des autres implémentations de `MqttClient` est **inchangée** — `FakeMqttClient.subscribe` lève toujours `NotConnectedError` |

---

## 17. Mutations discriminantes

Aucun test n'est écrit à ce stade. **Aucune mutation n'est déclarée tuée.**
Chaque mutation ne change **qu'une seule chose**.

| # | Mutation | Propriété visée |
|---|---|---|
| W-M1 | Le registre est supprimé : `subscribe` redevient un simple relais | W-P1 |
| W-M2 | L'enregistrement est **conditionné au succès** de la transmission | W-P3 |
| W-M3 | La transmission au client a lieu **avant** l'enregistrement | W-P2 |
| W-M4 | `_on_connect` ne restaure rien | W-P4 |
| W-M5 | Seule la première souscription enregistrée est restaurée | W-P4 |
| W-M6 | La restauration réémet avec un `qos` par défaut au lieu du `qos` enregistré | W-P6 |
| W-M7 | La restauration a lieu même sur un CONNACK **en échec** | W-P5 |
| W-M8 | Le registre est vidé par `disconnect()` | W-P11 |
| W-M9 | Le registre est une liste : chaque appel ajoute une entrée, et le registre croît à chaque reconnexion | W-P8, W-P10 |
| W-M10 | Un `qos` redéclaré est ignoré : le premier l'emporte | W-P9 |
| W-M11 | La restauration suit l'ordre de **dernière** déclaration | W-P7 |
| W-M12 | La restauration précède la notification de présence | W-P12 |
| W-M13 | La notification de présence est **conditionnée au succès** de la restauration | W-P13 |
| W-M14 | Un échec de réémission est absorbé **sans aucune trace** | W-P14 |
| W-M15 | Un échec de réémission est **propagé** dans la boucle Paho | W-P15 |
| W-M16 | Un échec de réémission **retire** la souscription du registre | W-P16 |
| W-M17 | L'émission vers le client a lieu **sous verrou** | W-P17 |
| W-M18 | La restauration émet **un topic supplémentaire** jamais enregistré | W-P18 |

**W-M12 est discriminable sur le chemin NOMINAL**, et pas seulement sur un
échec : un journal d'événements ordonné — notification de connexion d'un côté,
appels `subscribe` de l'autre — suffit à observer l'inversion, sans qu'aucune
réémission ait besoin d'échouer.

**W-M13 est distincte de W-M12** : elle conserve l'ordre contracté et ne
défaille que lorsque la restauration échoue. Les deux facettes de §9 exigent
donc deux mutants, non un seul.

**W-P4 et W-P18 se tiennent ensemble** : la première exige que toutes les
souscriptions enregistrées soient réémises, la seconde qu'aucune autre ne le
soit. Ensemble elles fixent l'ensemble émis exactement ; W-M5 attaque la
première, W-M18 la seconde.

**Quatre propriétés n'ont volontairement aucune mutation dédiée** : W-P19 à
W-P22 sont des propriétés de **portée et de non-régression** — l'absence de voie
de commande, l'absence de corrélation SUBACK, l'invariance de `clean_session`,
l'invariance de la sémantique des doubles. Leur « mutation » consisterait à
introduire le composant qu'elles interdisent, ce qui n'éprouverait rien du code
de W0. Les vérifier par constat direct est plus honnête que gonfler la table.

---

## 18. Risques et inconnues

| # | Risque ou inconnue | Portée |
|---|---|---|
| W-R1 | **Illusion de fiabilité** : réémettre un SUBSCRIBE n'est pas la preuve qu'un broker l'honore, ni même qu'il l'accepte. Risque principal du lot | §15 |
| W-R2 | **Dérive vers une gestion de session** : `clean_session=False`, identifiants de session, files persistantes. Explicitement hors périmètre | §4 |
| W-R3 | **Dérive vers une supervision** : transformer un échec de réabonnement en politique de santé ou en sortie de processus | §11 |
| W-R4 | Tentation d'ouvrir la voie de commande « puisque `subscribe` marche enfin » | §4 |
| W-R5 | **Irrétractabilité** : une souscription demandée une fois engage l'objet jusqu'à sa fin de vie, sans recours pour l'appelant | §7.1 |
| W-I1 | Forme exacte d'un échec de `subscribe` côté Paho — code de retour, exception — non éprouvée. W0 ne la contractualise pas | §11.1 |
| W-I2 | Comportement réel de session du broker : `clean_session` vaut `True`, mais rien n'est vérifié en conditions réelles | A8, C11 §13 |
| W-I3 | Messages publiés pendant la fenêtre de coupure : perte possible, non traitée | §15 |
| W-I4 | Ordre réel des paquets SUBSCRIBE réémis et des messages entrants, côté broker | terrain |
| W-I5 | Acceptation effective d'un SUBSCRIBE réémis, faute de corrélation SUBACK | §4, §15 |

---

## 19. Ce que W0 ne fait pas

Aucun changement du cœur, du runtime, du lifecycle, de la surface de lecture,
de la configuration utilisateur ou du packaging · aucune souscription au topic
de commande · aucun acquittement · aucun `TransactionalCore` instancié · aucune
écriture · aucun profil réel · aucune modification d'un contrat existant ·
aucune modification de la sémantique des doubles de test.

**AUCUNE CONFORMITÉ TERRAIN N'EST REVENDIQUÉE.** Rien n'a été éprouvé contre un
broker réel. Toutes les preuves prévues sont hors ligne : faux client Paho,
rappels déclenchés explicitement, aucun réseau.

---

## 20. Renvois

`c4-real-adapters.md` — **autorité amont directe** : adaptateur MQTT, entrée des
messages, connexion et reconnexion, et report explicite de la politique de
reconnexion · `c7-mqtt-read-contract.md` — surface de lecture, séparée des
commandes · `c7c3a-mqtt-presence.md` — présence et testament, limitation de
reconnexion assumée · `c11-presence-recovery.md` — reprise de présence après
reconnexion, `on_connect` pour chaque CONNACK, session neuve attendue ·
`c9-process-lifecycle.md` — arrêt du processus · `c8-composition-root.md` —
racine de composition, seul endroit où les adaptateurs sont câblés.

**Chantiers futurs, hors W0** : contrat de la surface transactionnelle MQTT ·
contrat de concurrence et de cycle de vie · câblage runtime de la voie de
commande · surface d'erreur de `subscribe` · adaptateur d'écriture et profil
réel · qualification terrain.
