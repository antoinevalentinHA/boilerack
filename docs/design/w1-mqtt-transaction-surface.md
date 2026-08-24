# W1 — Contrat de la surface transactionnelle MQTT

Document **normatif**. Il fixe **comment MQTT transporte la surface
transactionnelle** : quel topic porte une commande, comment un message entrant
atteint le cœur, sous quels topics et avec quels réglages ses acquittements
repartent.

Il ne fixe **pas** comment le cœur décide. Cette question est déjà contractée
par C3, et W1 s'interdit de la rejouer.

**W1 ne câble rien.** Aucun abonnement runtime, aucun gestionnaire de message,
aucun `TransactionalCore` instancié, aucune pompe d'exécution, aucune écriture.
W1 est un contrat de **frontière et de composition**, écrit avant le lot qui
l'appliquera.

Conventions : **MUST** obligatoire · **MUST NOT** interdit · *reporté*
explicitement renvoyé à un lot ultérieur. Aucun `SHOULD` n'est employé : ce
contrat n'énonce que des obligations et des interdictions, et n'a aucune
recommandation à formuler.

---

## 1. Objet

Le dépôt contient, depuis C3 et C4, **toutes les pièces** d'une voie de
commande MQTT : un décodeur de payload, une validation ordonnée, un moteur
transactionnel, un modèle d'acquittement, une couture d'entrée
(`set_message_handler`), un adaptateur Paho réel, et — depuis W0 — des
souscriptions qui survivent à une reconnexion.

Aucune de ces pièces n'est reliée aux autres dans le runtime. Il ne manque pas
un composant : il manque une **décision de frontière**. Personne n'a écrit quel
topic est souscrit, avec quel QoS, par quelle autorité, ni quelle valeur
alimente le préfixe d'acquittement — alors que **deux** champs prétendent
aujourd'hui le porter.

W1 comble ce vide contractuel, et lui seul. Il est à C3 ce que W0 est à C4 :
une **extension de frontière** d'un contrat antérieur, sur une jonction que
celui-ci a laissée ouverte parce qu'elle ne relevait pas de lui.

La chaîne visée, dont W1 ne décrit que les deux extrémités MQTT :

```
commande MQTT → décodage / validation → TransactionalCore → exécution → ACK MQTT
    ^^^^^^^^^^                                                            ^^^^^^^
    W1                                   C3 (inchangé)                    W1
```

---

## 2. Statut, autorité et portée

**Autorité.** W1 est normatif sur la **frontière MQTT de la voie de commande** :
topic souscrit, QoS de souscription, remise du message au cœur, autorité des
champs de configuration qui alimentent cette composition, et topics
d'acquittement effectivement employés en runtime.

**Non-autorité.** W1 n'est normatif ni sur le format du payload, ni sur les
états, ni sur les raisons, ni sur la validation, ni sur la déduplication, ni sur
l'expiration, ni sur la confirmation par relecture : **C3 les possède**, et W1
les cite sans les redéfinir. Une divergence entre W1 et C3 sur l'un de ces
points serait une **faute de W1**, jamais une modification de C3.

**Portée d'implémentation.** Les clauses de W1 s'adressent à la **racine de
composition** (C8) et au lot qui y ouvrira la voie de commande (W3). Elles ne
créent aucune obligation nouvelle pour la frontière abstraite `MqttClient`, ni
pour les doubles de test, ni pour `PahoMqttClient` au-delà de ce que W0 a déjà
contracté.

**Périmètre du présent lot.** W1 ne produit qu'un document. Aucun module de
`src/`, aucun test, aucun autre contrat n'est modifié.

---

## 3. Autorités et acquis

Ce que W1 **reprend sans le redéfinir**, chaque ligne vérifiée dans le dépôt à
la base `e9306de`.

| # | Acquis | Origine | Preuve |
|---|---|---|---|
| A1 | Payload de commande : objet JSON UTF-8, **six champs exacts** — `request_id`, `ts`, `expires_at`, `source`, `role`, `value` — aucun champ supplémentaire interprété, tout champ inconnu refusé | C3 § « Modèle de commande » | `core/command.py` `REQUIRED_FIELDS`, `parse_command` |
| A2 | `request_id` : UUID v4 **canonique minuscule** ; toute autre forme est `invalid_payload` | C3 | `is_canonical_uuid4` |
| A3 | Statuts fermés : `accepted` non terminal ; `applied`, `rejected`, `timeout` terminaux | C3 § « Modèle d'ACK » | `core/ack.py` |
| A4 | Dix raisons fermées, chacune de **classe fixe** ; `reason` / `reason_class` **uniquement** sur `rejected` | C3 | `REASON_CLASS`, `Ack.__post_init__` |
| A5 | Sérialisation d'ACK : JSON compact, clefs triées, UTF-8, `allow_nan=False` | C3 | `ack_to_json` |
| A6 | Topic d'ACK **dérivé du rôle**, sous le préfixe transactionnel. C3 l'écrit littéralement `boilerack/ack/<role>` ; le code implémente ce préfixe comme **paramètre** (`ack_topic_prefix`), la valeur de C3 en étant le défaut. Ce que W1 décide n'est pas le schéma — il est acquis — mais **quelle autorité runtime alimente ce paramètre** (§8) | C3 § « Publication des ACK » (schéma) ; code (paramétrage) | `TransactionalCore._publish_ack`, `DEFAULT_ACK_TOPIC_PREFIX` |
| A7 | ACK publiés en **QoS 1, non retenus** | C3 ; C4 § « QoS » | `_ACK_QOS = 1`, `_ACK_RETAIN = False` |
| A8 | Ordre : `accepted` **avant** le verdict terminal ; le verdict terminal est **mis en cache avant** toute publication | C3 | `_admit`, `_conclude` |
| A9 | Une publication d'ACK qui échoue ou lève **ne perd jamais** le verdict, n'est **pas retentée**, et ne remonte pas. Deux mécanismes distincts : `_publish_terminal` intercepte et journalise les **exceptions** ; un **échec établi** (`rc` non nul) ne lève pas, n'est pas observé par le cœur — qui ignore le handle rendu — et n'est journalisé que par `PahoMqttClient.publish` | C3 (clause) ; C4 (journalisation de l'échec établi) | `_publish_terminal` ; `PahoMqttClient.publish` |
| A10 | La déduplication repose **exclusivement** sur `request_id` ; le drapeau `dup` est représenté mais **n'altère pas** la logique | C3 § « Voie d'entrée MQTT » | `submit`, `test_message_dup_est_admis_par_request_id` |
| A11 | Expiration vérifiée **à l'admission** puis **de nouveau avant l'écriture**, toujours via `Clock` | C3 § « Expiration » | `validate`, `_run_transaction` |
| A12 | `set_message_handler` est la **seule** couture d'entrée ; `TransactionalCore.attach()` y branche `submit` | C3 § « Voie d'entrée MQTT » | `transport/mqtt.py`, `engine.attach` |
| A13 | `on_message` construit `Message(topic, payload octets bruts, qos, retain, dup)` ; **aucun décodage JSON dans l'adaptateur** ; une exception du handler est journalisée, jamais propagée dans la boucle Paho | C4 § « Entrée des messages » | `PahoMqttClient._on_message` |
| A14 | Une souscription demandée à `PahoMqttClient` est **enregistrée puis réémise après chaque CONNACK réussi** | W0 §7, §8 | `_souscriptions`, `_restaurer_souscriptions` |
| A15 | W0 garantit la **réémission** d'un SUBSCRIBE, **jamais son acceptation** par le broker : aucune corrélation SUBACK n'existe | W0 §4, §15 | contrat W0 |
| A16 | `online` **ne signifie pas** « souscriptions restaurées » | W0 §11.2 | contrat W0 |
| A17 | Une souscription logique est **irrétractable** : aucun `unsubscribe` n'existe, et un `disconnect()` ne vide pas le registre | W0 §7.1, §12, §13 | contrat W0 |
| A18 | Une redéclaration du même topic avec un autre QoS **remplace** le QoS enregistré | W0 §10 | contrat W0 |
| A19 | Surface de lecture et surface transactionnelle sont **séparées** ; un topic de lecture ne déclenche aucune action ; mélanger acquittements et télémétrie est interdit | C7 §12, §14 | contrat C7 |
| A20 | `[mqtt].command_topic` et `[mqtt].ack_topic_prefix` sont **refusées nommément** dans le fichier utilisateur | C10 § « Clés explicitement refusées » | `config.py` `_REFUS_MQTT` |
| A21 | Ces mêmes champs sont documentés **morts** ou **morts dans le chemin d'exécution**, et **non supprimés** | C10 § « Champs non exposés » ; C9 § « Exclus » | contrats C10, C9 |
| A22 | Un topic de **publication** ne peut porter de joker — conséquence mécanique de MQTT, déjà appliquée au testament et déjà relevée pour la surface de lecture | frontière transport ; C7-C1 § « refus » | `MqttWill.__post_init__`, `_WILDCARDS` ; `c7c1-read-surface-primitives.md` |
| A23 | La divergence de namespace entre `boilerack/*` (transactionnel) et `boiler` (lecture) est **enregistrée comme dette**, et **explicitement non tranchée** par C7 | C7 §1.3, §14 | contrat C7 |

**Faits constatés, non supposés.** `MqttConfig.command_topic` vaut
`"boilerack/command"` et **aucun module de `src/` ne le lit** hors validation et
`__repr__`. `MqttConfig.ack_topic_prefix` vaut `"boilerack/ack"` et n'est lu par
personne. `TransactionalCore` porte son **propre** paramètre
`ack_topic_prefix`, de défaut `DEFAULT_ACK_TOPIC_PREFIX = "boilerack/ack"` :
deux littéraux identiques, dans deux modules distincts, sans lien. Ni
`runtime.py`, ni `lifecycle.py`, ni `cli.py` n'appellent `subscribe`,
`set_message_handler` ou `TransactionalCore` — un test l'exige déjà
(`test_aucune_voie_de_commande_ouverte`). `submit()` ne lit **que**
`message.payload` : le topic entrant est ignoré. `source` est exigé non vide et
**n'est employé nulle part ailleurs**.

---

## 4. Hors périmètre — liste fermée

Câblage runtime de la voie de commande · `subscribe(command_topic)` réel ·
`set_message_handler` réel · instanciation de `TransactionalCore` en runtime ·
pompe `process_next` · `drain` · choix du fil d'exécution de `submit` ·
verrouillage du cœur · file inter-fils · ordre vis-à-vis de `run_due()` ·
comportement d'une transaction en vol pendant `SIGTERM` · `TimeoutStopSec` ·
`VClient.write` · adaptateur d'écriture concret · dialecte `vclient` ·
`write_timeout_s` · profil de production · bornes réelles · tolérances réelles ·
noms de commandes chaudière · `unsubscribe` · corrélation SUBACK · rappel
`on_subscribe` · session persistante (`clean_session=False`) · file persistante
côté broker · politique de reconnexion · retry de publication · nouveau timeout
métier · nouvelle raison d'ACK · nouveau statut · nouvelle clé TOML · TLS,
ACL, authentification ou chiffrement nouveaux · découverte MQTT · Home
Assistant · systemd · installation · terrain · **modification de C2, C3, C4,
C7, C8, C9, C10, C11, C12, C13 ou W0**.

**En particulier, W1 n'ouvre aucune voie entrante.** Il décide de sa forme ; il
ne s'en sert pas.

---

## 5. Ce qui est déjà normatif — et que W1 ne réécrit pas

W1 serait nuisible s'il reformulait C3 : deux énoncés d'une même règle finissent
par diverger. Les points suivants sont **déjà contractés**, et W1 s'y réfère
sans les reprendre.

| Domaine | Autorité | W1 en dit |
|---|---|---|
| Forme et champs du payload | C3 (A1, A2) | rien de plus |
| Ordre de validation, priorité borne/pas | C3 | rien |
| Statuts, raisons, classes | C3 (A3, A4) | **lesquels sont transportés** (§12) |
| Sérialisation d'ACK | C3 (A5) | rien |
| Schéma du topic d'ACK | C3 (A6) | **quelle valeur alimente le préfixe** (§8) |
| QoS et retain des ACK | C3, C4 (A7) | **confirmation, sans redéfinition** (§10) |
| Déduplication, TTL, `in_flight` | C3 (A10) | **qu'aucune seconde autorité n'apparaît** (§13) |
| Expiration | C3 (A11) | **qu'elle est l'unique garde contre un message ancien** (§14) |
| Fail-closed sur `accepted`, cache avant publication | C3 (A8, A9) | **la conséquence côté consommateur** (§16) |
| Persistance des souscriptions | W0 (A14–A18) | **que la voie de commande la consomme** (§17) |
| Refus des clés utilisateur | C10 (A20, A21) | **qu'aucune n'est ouverte** (§18) |

---

## 6. Trous contractuels comblés par W1

Chacun est un **manque réel**, constaté, et non une préférence.

| # | Trou | Effet s'il reste ouvert |
|---|---|---|
| T1 | Aucune autorité runtime n'est désignée pour le **topic de commande** | le lot de câblage choisirait un littéral, et la configuration resterait morte |
| T2 | **Deux** autorités prétendent porter le préfixe d'ACK, aucune n'est câblée | une divergence future serait **silencieuse** : les ACK partiraient sous un préfixe que la configuration ne décrit pas |
| T3 | Aucun **QoS de souscription** n'est spécifié ; `subscribe` vaut `qos=0` par défaut | une commande pourrait être perdue **sans trace**, exactement le défaut que W0 a corrigé pour la souscription elle-même |
| T4 | Rien ne dit si le **topic entrant** porte de l'information métier | un lot ultérieur pourrait dériver le rôle du topic et créer une seconde autorité de routage |
| T5 | Rien n'interdit un **joker** dans le topic souscrit | tout message du broker deviendrait une commande candidate |
| T6 | Rien ne dit ce qu'il advient d'un message livré **retenu** | soit une règle inventée, soit une exécution surprise |
| T7 | Rien ne dit ce qu'il advient d'une commande publiée **pendant une coupure** | un consommateur pourrait croire à une file inexistante |
| T8 | Rien n'interdit une **seconde déduplication** dans le transport | deux mémoires de rejeu, aux durées de vie différentes |
| T9 | La **divergence de namespace** transactionnel / lecture reste ouverte (A23) | deux racines de topics sur un même broker, sans décision |
| T10 | Le segment de rôle du topic d'ACK est bâti sur une **chaîne non validée** du payload | un demandeur choisit le nom et la profondeur d'un sous-topic sous le préfixe d'ACK (§9.4) |

T1 à T8 sont **tranchés** par W1. T9 et T10 sont **exposés et reportés**, avec
motif : §19 et §9.4.

---

## 7. Topic de commande

### 7.1 Autorité unique

**Clause normative.** La valeur du topic de commande souscrit par le runtime
**MUST** provenir de **`MqttConfig.command_topic`**, et d'aucune autre source.

Motif : c'est le **seul** champ existant qui porte cette information (A21) ;
aucune seconde autorité n'a besoin d'être créée, et un littéral écrit dans le
lot de câblage rendrait le champ définitivement mort tout en le laissant en
place — la pire des deux situations.

**Clause normative.** Le lot de câblage **MUST NOT** écrire un topic de commande
en dur, **MUST NOT** le dériver du préfixe de la surface de lecture, et
**MUST NOT** introduire un second champ de configuration pour le porter.

Cette clause désigne une autorité ; elle **ne rend rien configurable par
l'utilisateur** (§18).

### 7.2 Unicité et absence de joker

**Clause normative.** Le runtime **MUST** souscrire à **exactement un** topic de
commande, **MUST** le souscrire **une seule fois** dans la vie du client, et ce
topic **MUST NOT** contenir de joker MQTT (`+`, `#`).

Motifs, dans l'ordre :

- **Unicité** — la pluralité n'a aucun consommateur. Le rôle visé voyage dans le
  payload (§11), jamais dans le topic : un second topic ne porterait donc aucune
  information supplémentaire, et multiplierait les chemins d'entrée d'un cœur
  qui n'en a qu'un.
- **Une seule fois** — W0 §10 établit qu'une redéclaration avec un autre QoS
  **remplace** le QoS enregistré (A18). Souscrire deux fois ouvre donc un chemin
  par lequel le QoS effectivement réémis diffère de celui contracté ici.
  L'obligation vise **l'appel de composition**, jamais les réémissions internes
  de W0 : la distinction est faite en §7.5.
- **Aucun joker** — un joker ferait de tout message du broker une commande
  candidate, et rendrait le topic entrant indéterminé alors même que W1
  l'affirme sans signification métier (§11.2). La frontière applique déjà cette
  interdiction au testament (A22) ; l'étendre à la souscription de commande est
  une exigence propre à W1, non la citation d'un acquis.

**Non contracté** : la **validité** du topic au sens du protocole (caractères de
contrôle, `$` initial, longueur) n'est vérifiée aujourd'hui que par
`_check_non_empty`. W1 **n'ajoute aucune validation** — ce serait du code — et
**ne prétend pas** qu'une valeur non vide soit un topic MQTT valide. Voir §28.

### 7.3 QoS de souscription

**Clause normative.** La souscription au topic de commande **MUST** être
demandée avec **QoS 1**, passé **explicitement**.

Motifs :

- **QoS 0 est refusé** : il autorise la perte d'une commande sans aucune trace.
  Le pont perdrait un ordre en silence — exactement la classe de défaut que W0
  §5 qualifie de bloquante *par sa nature, non par sa probabilité*.
- **QoS 2 est refusé**, et il faut dire exactement pourquoi, sans surestimer ce
  que le projet possède déjà. `request_id` procure une **déduplication
  transactionnelle bornée** : elle vaut pendant le TTL du cache terminal, et
  **disparaît au redémarrage** du processus (C3, et §13 ci-dessous). Ce n'est
  donc **pas** un « exactement une fois » de bout en bout, et QoS 2 n'en
  fournirait pas un non plus : la remise unique d'un paquet ne dit rien de
  l'idempotence d'une transaction dont la mémoire est volatile. QoS 2 ne
  **remplacerait** aucune de ces garanties métier ; il coûterait un échange en
  quatre temps et un support broker moins uniforme pour une propriété que le
  cœur ne consomme pas. Il n'est pas retenu.
- **QoS 1 est retenu** : au moins une fois, doublons possibles, doublons
  neutralisés par `request_id` **dans les limites qui viennent d'être dites**.
  Il est aussi le QoS déjà employé pour les ACK (A7) et pour la télémétrie
  retenue (C7 §11) : aucune exception à justifier.

**Explicitement** n'est pas une précaution de style : `subscribe(topic)` sans
QoS vaut **0** par signature. Un QoS obtenu par omission serait indiscernable
d'un QoS choisi, et le mutant correspondant (§26, W1-M2) serait invisible en
relecture.

### 7.4 Ce que la souscription ne prouve pas

**À énoncer sans atténuation.** Une souscription **demandée** en QoS 1 ne prouve
pas :

- qu'elle a été **acceptée** par le broker — aucune corrélation SUBACK n'existe
  (A15) ;
- que le QoS **accordé** est 1 — un broker peut accorder un QoS inférieur, et ce
  QoS accordé n'est ni observé ni observable ici ;
- que des messages arrivent — `online` ne dit rien de l'abonnement (A16).

W1 contracte donc un **QoS demandé**, jamais un QoS effectif.

---

### 7.5 Une seule instance MQTT en runtime — et ce que « une seule fois » veut dire

**Le fait, vérifié.** `build_runtime` construit **une** instance
`PahoMqttClient(config.mqtt)` et la remet au publieur de lecture. C8 énonce que
la racine de composition est le **seul** endroit où les adaptateurs sont câblés.

**Le risque, dérivé et non supposé.** Une seconde instance construite depuis le
même `MqttConfig` porterait le **même `client_id`**. C10 le documente sans
ambiguïté :

> « Deux instances de Boilerack connectées au même broker avec le même
> `client_id` se déconnectent mutuellement en boucle : le protocole MQTT impose
> l'unicité. » — C10, `client_id`

Une voie de commande qui construirait son propre client se déconnecterait donc
en boucle avec la surface de lecture. S'y ajoute une conséquence propre à W0 :
le registre de souscriptions est **par objet client** ; deux instances auraient
deux registres, et la restauration de l'une ne dirait rien de l'autre.

**Clause normative.** La surface transactionnelle **MUST** consommer **la même
instance `MqttClient`** que la surface de lecture, celle que la racine de
composition construit déjà. Le lot de câblage **MUST NOT** construire un second
client MQTT, **MUST NOT** dériver un second `MqttConfig`, et **MUST NOT**
introduire un second `client_id`.

**Pourquoi cette décision appartient à W1 et non à W2.** Elle porte sur le
**nombre d'objets assemblés par la racine**, pas sur la façon dont ils sont
exécutés. Elle se tranche par lecture de `build_runtime`, de C8 et de C10, sans
rien décider d'un fil, d'un verrou ni d'un ordre. La question voisine — savoir
si deux surfaces peuvent appeler cette instance **concurremment** — est, elle,
entièrement W2 (§20).

**Portée exacte : l'instance, pas les paquets.** Cette clause dit qu'il existe
**un seul objet client** en runtime. Elle ne dit **rien** du nombre de paquets
SUBSCRIBE émis vers le broker : W0 en réémet nécessairement à chaque CONNACK
réussi, et c'est voulu (§17.1).

**Ce que « exactement une fois » signifie en §7.2 et dans W1-P4.** L'obligation
porte sur **l'appel logique de composition à `MqttClient.subscribe`** : le
câblage le fait une fois, pour un topic, avec un QoS. Elle ne porte **pas** sur
les réémissions internes de W0, qui ne sont pas des appels du câblage et que
W1-P4 ne compte pas. Un mutant qui souscrirait à nouveau depuis un rappel de
connexion violerait W1-P4 ; la restauration W0, elle, ne la viole jamais.

---

#### 7.5.1 Le `MqttConfig` dérivé de W4-E2 — note de clôture

*Note ajoutée après coup, et **non normative**. Elle ne réécrit rien de §7.5 :
la clause a été énoncée ici, sa tension a été disposée ailleurs, et les deux
doivent rester lisibles.*

§7.5 écrit que le lot de câblage « **MUST NOT** dériver un second `MqttConfig` ».
W4-E2 en dérive pourtant un, par `replace(config.mqtt, …)`, pour transmettre à
`build_transaction_surface` les topics du sous-arbre de commande. La tension est
réelle, et elle a été **tranchée avant l'écriture du code**, non découverte
après : `w4e-composition-activation.md` §8.4 la dispose ainsi —

> Un `MqttConfig` dérivé qui ne diffère que par ces deux topics **n'est pas une
> seconde connexion**, et ne relève donc pas de ce que W1 §7.5 interdit.

**Pourquoi cette lecture, et pas la lettre.** La motivation entière de §7.5
porte sur l'**identité de connexion** : deux instances partageant un `client_id`
« se déconnectent mutuellement en boucle », et le registre de souscriptions de
W0 est **par objet client**. La clause de portée de §7.5 le dit elle-même, dans
les termes qui suivent quelques paragraphes plus haut :

> « Cette clause dit qu'il existe **un seul objet client** en runtime. »

L'interdiction protège donc l'unicité du **client**, pas l'unicité de la valeur
des topics. Un dérivé qui ne touche à aucune propriété de connexion ne crée ni
seconde instance, ni second `client_id`, ni seconde session.

**Ce que le dérivé change, exhaustivement.** Deux champs : `command_topic` et
`ack_topic_prefix`. Sont préservés à l'identique `host`, `port`, `client_id`,
`keepalive`, `username`, `password` et `tls` — c'est-à-dire toute propriété de
connexion.

**L'invariant de §7.5 reste intégralement tenu.** L'unique `PahoMqttClient`
demeure celui que `build_runtime` construit ; la surface transactionnelle le
reçoit tel quel, sans jamais en fabriquer un autre. Cet invariant n'est pas
seulement affirmé : W4-E2 en fait une **barrière falsifiable**, éprouvée par une
sonde qui construit un second client dans `lifecycle.py` et doit la faire rougir.

## 8. Préfixe d'ACK — suppression de la double autorité

### 8.1 Le constat

Deux emplacements portent aujourd'hui la même information :

| Emplacement | Valeur | Consommateur |
|---|---|---|
| `MqttConfig.ack_topic_prefix` | `"boilerack/ack"` | **aucun** |
| `TransactionalCore(ack_topic_prefix=…)`, défaut `DEFAULT_ACK_TOPIC_PREFIX` | `"boilerack/ack"` | le cœur, sur son propre défaut |

C10 l'a déjà nommé sans le résoudre : le champ de configuration est **« mort
dans le chemin d'exécution — le noyau transactionnel a son propre paramètre,
jamais alimenté par cette valeur »** (A21).

Les deux littéraux sont **égaux aujourd'hui**, et c'est précisément ce qui rend
le défaut dangereux : rien ne les lie, et une modification de l'un ne ferait
échouer aucune vérification. La divergence, le jour où elle surviendrait, serait
**silencieuse**.

### 8.2 Options examinées

| # | Option | Coût | Verdict |
|---|---|---|---|
| O1 | `MqttConfig.ack_topic_prefix` devient l'autorité runtime : la composition la **transmet explicitement** au cœur ; le défaut du cœur reste un défaut de **bibliothèque**, jamais du runtime | aucun changement de code ni de contrat dans W1 ; une obligation pour W3 | **retenue** |
| O2 | Supprimer `MqttConfig.ack_topic_prefix`, le cœur reste seul | touche C4 et un test existant ; C10 et C9 **excluent explicitement** le traitement des champs morts ; ferme définitivement toute configurabilité future | rejetée |
| O3 | Supprimer le paramètre du cœur et rendre l'argument obligatoire | modifie la signature publique de `TransactionalCore`, donc C3 ; casse les doubles et tests existants | rejetée |
| O4 | Ne rien décider | conserve exactement le défaut que W1 doit corriger | rejetée |

### 8.3 Clause

**Clause normative.** En runtime, le préfixe d'ACK employé par le cœur
**MUST** provenir de **`MqttConfig.ack_topic_prefix`**, transmis
**explicitement** à la construction de `TransactionalCore`.

**Clause normative.** Le lot de câblage **MUST NOT** s'en remettre au défaut
`DEFAULT_ACK_TOPIC_PREFIX`, **MUST NOT** écrire un préfixe en dur, et
**MUST NOT** introduire un troisième porteur de cette valeur.

**Statut de `DEFAULT_ACK_TOPIC_PREFIX` après W1** : défaut de **bibliothèque**,
légitime pour un test qui construit un cœur sans configuration, **jamais**
l'autorité d'un runtime. Il n'est ni supprimé, ni déprécié, ni modifié.

**Dette résiduelle, énoncée et non résolue** : la **duplication du littéral**
subsiste dans deux modules. O1 garantit qu'elle ne peut plus produire de
divergence **sur le chemin d'exécution**, puisqu'une seule valeur y circule ;
elle reste une dette de code, dont la résorption relèverait d'un lot dédié et
non de W1 (§28).

---

## 9. Topics d'ACK

### 9.1 Schéma — inchangé

**Clause de rappel, non de création.** Le topic d'un acquittement est
`<ack_topic_prefix>/<rôle>` (A6). W1 **ne modifie pas** ce schéma.

Le topic dépend donc **du rôle**, et de **rien d'autre**.

**Clause normative.** Le topic d'ACK **MUST NOT** dépendre du `request_id`, ni
du `source`, ni de l'instance émettrice, ni du statut, ni de la raison.

Motif : un topic par transaction créerait un espace de topics **non borné** sur
le broker, dont chaque entrée serait morte à la seconde suivante. Un topic par
statut obligerait un consommateur à s'abonner à un ensemble qu'il devrait
connaître d'avance. Le rôle est la seule dimension **fermée** — elle est celle
du profil — et c'est aussi celle qu'un consommateur suit déjà.

`request_id` reste porté **dans le payload** de chaque ACK (A5), et c'est là
qu'un consommateur corrèle.

### 9.2 Rôle inexploitable — le seau `_unknown`

**Clause de rappel.** Lorsqu'un rejet survient sur un payload dont le champ
`role` n'est pas une chaîne non vide, l'ACK est publié sous le segment
`_unknown` (`_UNKNOWN_ROLE_TOPIC`, déjà présent dans le cœur).

**Clause normative.** Le lot de câblage **MUST NOT** supprimer ce seau,
**MUST NOT** le remplacer par un silence, et **MUST NOT** rediriger un tel ACK
vers le topic de commande ou vers un topic de la surface de lecture.

Motif : un rejet de forme est **précisément** le cas où un demandeur a le plus
besoin d'une réponse, et c'est aussi celui où le rôle manque. Ne rien publier
transformerait une erreur nommée en absence indistinguable d'une panne.

### 9.3 Séparation stricte

**Clause normative :**

- un ACK **MUST NOT** être publié sur le topic de commande ;
- une commande **MUST NOT** être attendue sous le préfixe d'ACK ;
- le préfixe d'ACK et le topic de commande **MUST** rester **disjoints au sens
  des niveaux MQTT**, au sens précis défini ci-dessous ;
- un topic d'ACK **MUST NOT** porter de joker : une publication n'en admet
  pas (A22) ;
- un topic de la surface de lecture **MUST NOT** porter d'acquittement — C7
  §12 l'interdit déjà, W1 ne fait que ne pas y contrevenir.

**Définition normative — disjonction au sens des niveaux.** Soit `niveaux(x)` la
découpe de `x` sur `/`. Deux topics `A` et `B` sont **disjoints** lorsque :

1. `niveaux(A) != niveaux(B)` — ils ne sont pas égaux ; **et**
2. `niveaux(A)` n'est pas un préfixe strict de `niveaux(B)`, **ni l'inverse** —
   aucun n'est ancêtre de l'autre dans la hiérarchie MQTT.

**Ce n'est pas un `startswith()` sur les chaînes**, et la distinction est
matérielle :

| A | B | `B.startswith(A)` | Disjoints au sens des niveaux ? |
|---|---|:-:|:-:|
| `boilerack/ack` | `boilerack/ack/temp` | vrai | **non** — `A` est ancêtre de `B` |
| `boilerack/ack` | `boilerack/ackx` | **vrai** | **oui** — `ackx` est un autre niveau |
| `boilerack/ack` | `boilerack/command` | faux | **oui** |

Un test de chaîne classerait `boilerack/ackx` comme conflictuel alors qu'aucun
abonné à `boilerack/ack/#` ne le recevra jamais : ce serait interdire ce que le
protocole autorise. Inversement, la relation d'ancêtre est le seul cas où un
abonnement à l'une des deux surfaces capte l'autre — c'est **elle** que la
clause vise.

**Cette propriété est vérifiable statiquement**, sur les deux valeurs de
`MqttConfig`, sans broker et sans connexion : W3 la prouve par un test de
composition (§21, obligation 16).

### 9.4 Trou signalé — segment de rôle non validé

**Constat, non clause.** Sur le chemin de **rejet à l'admission**, le segment de
rôle du topic d'ACK est tiré du champ `role` **brut du payload**, avant toute
résolution contre le profil (`_topic_role`). Toute chaîne non vide fournie par
le demandeur devient donc un segment du topic de publication, sans qu'aucune
validation du dépôt ne s'y applique : `MqttConfig` ne contrôle que la
non-vacuité du **préfixe**, et le cœur ne contrôle rien du **segment**.

**Ce que l'adaptateur refuse réellement.** Vérifié directement contre Paho
2.1.0 — version installée et utilisée par le dépôt —, `Client.publish` ne
soumet le topic qu'à `_raise_for_invalid_topic`, dont le corps entier se réduit
à deux gardes :

| Entrée dans le segment de rôle | Issue observée |
|---|---|
| `+` | **refusé** — `ValueError: Publish topic cannot contain wildcards.` |
| `#` | **refusé** — même `ValueError` |
| topic de plus de 65 535 octets | **refusé** — `ValueError: Publish topic is too long.` |
| `/` | **accepté** |
| `NUL` (0x00) | **accepté** |
| `LF` (0x0a), `DEL` (0x7f), C1 (0x9f) | **acceptés** |
| espace | **accepté** |
| `$` en tête de segment | **accepté** |

Aucune autre garde n'existe : ni caractère de contrôle, ni `NUL`, ni espace, ni
`$`, ni nombre de niveaux. **W1 ne prétend donc à aucune validation que
l'adaptateur ne possède pas.**

**Le défaut réel, énoncé exactement.** Il ne s'agit pas d'un échec de
publication, mais de l'inverse :

> Un demandeur qui contrôle le champ `role` d'un payload par ailleurs rejeté
> contrôle, par la même occasion, **le nom et la profondeur d'un sous-topic
> publié sous `<ack_topic_prefix>/`**. Le caractère `/` étant accepté, il peut
> faire naître une arborescence arbitraire sous le préfixe d'ACK.

Deux régimes distincts, à ne pas confondre :

- **`+` ou `#`** — la publication est refusée par Paho ; la `ValueError` remonte
  de `PahoMqttClient.publish` jusqu'à `_publish_terminal`, qui l'absorbe et la
  journalise (§16). Le verdict reste en cache, **aucun ACK n'atteint le
  demandeur** ;
- **tout le reste, `/` compris** — la publication **réussit**, sur un topic
  choisi par le demandeur. Il n'y a ici ni erreur, ni trace, ni garde.

Dans les deux régimes, aucune écriture n'a lieu et aucun faux succès n'est
produit : la portée du défaut est celle de **l'espace de topics**, non celle du
verdict métier. C'est ce qui le maintient en dessous du seuil bloquant — et non
une validation qui existerait quelque part.

**W1 ne corrige rien et ne conçoit rien.** Le calcul du topic vit dans
`core/engine.py`, que W1 s'interdit de modifier (§4). Décrire ici la forme
d'une future garde — jeu de caractères admis, repli sur `_unknown`, rejet —
reviendrait à concevoir la correction dans un contrat de frontière. Le point est
**enregistré comme trou T10, et reste REPORTÉ**, assorti d'un risque (§27) et
d'un signalement (§28). Le trancher exige un lot propre, avec sa propre clause —
jamais un ajout opportuniste au lot de câblage.

---

## 10. QoS et retain

### 10.1 Table de la surface

| Sens | Topic | QoS | Retain | Autorité |
|---|---|---:|:---:|---|
| entrant | `MqttConfig.command_topic` | **1** *(demandé)* | *(non applicable — voir §14)* | **W1** §7.3 |
| sortant | `<ack_topic_prefix>/<rôle>` | **1** | **faux** | C3 / C4 (A7) — **confirmé**, non redéfini |

### 10.2 Ce que ces réglages signifient — et ne signifient pas

Quatre faits distincts, que la table ci-dessus **ne confond pas** :

| Fait | Établi par |
|---|---|
| **Émission locale** — l'appel `publish` a rendu un handle | `PublishHandle` demandé |
| **Acceptation broker** — PUBACK reçu en QoS 1 | `PublishHandle.confirmed` (C4) |
| **Livraison au consommateur** | **jamais établi** — hors de portée du pont |
| **Application à la chaudière** | **jamais** déduit d'un fait MQTT : seule une relecture conforme produit `applied` (C3) |

**Clause normative.** Aucune clause de W1, ni aucun lot qui le consomme,
**MUST NOT** présenter l'un de ces faits comme un autre. En particulier, un ACK
`applied` **publié** ne prouve pas qu'il a été **reçu**, et un ACK non publié ne
retire rien au fait physique qu'il décrivait (§16).

### 10.3 Le QoS entrant ne déduplique pas

**Clause normative.** Le QoS 1 de la souscription **MUST NOT** être présenté
comme une garantie d'unicité. Il autorise explicitement la **redélivrance**. La
neutralisation d'un doublon relève de `request_id`, et de lui seul (§13).

---

## 11. Du message MQTT au cœur

### 11.1 Messages admissibles

**Clause normative.** Est admissible tout `Message` remis par le transport dont
le `topic` est celui souscrit (§7). La frontière **MUST NOT** appliquer de
critère supplémentaire avant de remettre le message au cœur — ni taille, ni
encodage, ni forme, ni présence de champ.

Motif : chacun de ces contrôles existe déjà **dans le cœur**, avec une raison
typée à la clef (`invalid_payload`, `invalid_type`, `invalid_value_non_finite`).
Les dupliquer à la frontière produirait des rejets **sans ACK** — un demandeur
verrait sa commande disparaître au lieu d'être nommément refusée.

Conséquences explicites : un payload **vide** est admissible et sera rejeté par
le cœur ; un payload **non UTF-8** l'est aussi ; un payload de plusieurs
mégaoctets l'est également. **Aucune borne de taille n'est contractée par W1**,
et le lot de câblage **MUST NOT** en introduire une.

**Où irait une politique de taille, si elle devenait nécessaire.** Le point
n'est pas laissé sans propriétaire. Une limite posée **à la frontière** ferait
disparaître un message sans ACK — exactement le défaut que la clause ci-dessus
interdit. Une limite a besoin, pour être honnête, de produire un **rejet
transactionnel typé** : un statut, une raison fermée et sa classe, donc une
autorité qui possède `Reason`. Cette autorité est le **cœur**, et son contrat
est C3.

**Classement : REPORTÉ au contrat compétent** — celui qui possède la taxonomie
de rejet, non W1 et non le lot de câblage. W1 ne définit **aucune** taille, ne
propose aucun seuil, et **ne modifie pas C3**. Voir §27, W1-R6, et §28, S5.

### 11.2 Le topic ne porte aucune information métier

**Clause normative.** L'intégralité de l'information métier — `request_id`,
`role`, `value`, `expires_at`, `ts`, `source` — **MUST** être portée par le
**payload**. Le topic entrant **MUST NOT** être interprété, découpé, ni utilisé
pour dériver un rôle, une valeur ou une identité.

Ce n'est pas une préférence : c'est le **comportement actuel du cœur**.
`submit()` ne lit que `message.payload` ; le topic est ignoré. W1 rend
normatif ce que le code fait déjà, afin qu'un lot ultérieur ne puisse pas
introduire une seconde autorité de routage sans violer une clause écrite.

### 11.3 Le gestionnaire adapte, il ne décode pas

**Clause normative.** La couche de câblage **MUST** remettre le payload au cœur
**en octets bruts, inchangés**. Elle **MUST NOT** décoder le JSON, **MUST NOT**
valider, **MUST NOT** filtrer, **MUST NOT** journaliser le payload complet, et
**MUST NOT** construire d'ACK.

Cette clause prolonge exactement la discipline de l'adaptateur, qui ne décode
déjà rien (A13). Elle en fait une obligation pour la **couche suivante**, où
rien ne l'imposait encore.

### 11.4 Qui appelle `submit`, et ce qu'il rend

**Constat.** `TransactionalCore.attach()` enregistre `submit` comme
gestionnaire ; le transport l'appelle alors pour chaque message. `submit`
renvoie `Ack | None`, tandis que `MessageHandler` est typé
`Callable[[Message], None]` : **la valeur de retour est ignorée** par
l'adaptateur, ce qui est cohérent — l'ACK est publié, pas rendu.

Sémantique du retour, telle qu'elle existe : `accepted` si la commande est
admise ; un ACK terminal si elle est rejetée à l'admission ou si un verdict est
rejoué depuis le cache ; **`None`** pour un doublon encore en vol.

**Clause normative.** Le lot de câblage **MUST NOT** fonder de comportement sur
la valeur rendue par `submit`, et **MUST NOT** modifier la signature de
`MessageHandler` pour la récupérer. L'acquittement du demandeur passe par MQTT,
jamais par un retour d'appel.

### 11.5 Ce que W1 refuse de trancher ici

**Constat, énoncé sans le résoudre.** Tel que `attach()` existe aujourd'hui,
`submit` s'exécuterait **sur le fil réseau de Paho**, et la publication de
`accepted` aurait lieu **depuis le callback `on_message`**, sur ce même fil.

W1 le **constate** et **n'en tire aucune clause**. Savoir si c'est acceptable,
s'il faut une file inter-fils, un verrou, ou une pompe distincte, est une
question de **concurrence** : elle appartient à W2 (§20). Trancher ici, au motif
que la surface la rencontre, reviendrait à décider d'un modèle d'exécution dans
un contrat de frontière.

**Ce que W1 affirme malgré tout**, parce que cela ne dépend d'aucun modèle de
fils : l'ordre **de demande** `accepted` puis verdict terminal est garanti **par
construction**, la mise en file suivant la publication de `accepted` dans
`_admit` (A8). L'ordre de **livraison** chez le consommateur n'est, lui,
contracté par personne — et W1 ne le contracte pas.

---

## 12. `accepted` et verdicts terminaux transportés

**Clause normative.** Les quatre statuts de C3 sont transportés sur MQTT, sur le
topic d'ACK du rôle. Aucun n'est retenu localement, aucun n'est ajouté.

| Statut | Terminal | Transporté | Circonstance de surface |
|---|:-:|:-:|---|
| `accepted` | non | **oui** | admission réussie, publié **avant** la mise en file |
| `rejected` | oui | **oui** | rejet d'admission, `queue_full`, échec établi de `accepted`, expiration, verdict d'exécution |
| `applied` | oui | **oui** | relecture conforme, et rien d'autre |
| `timeout` | oui | **oui** | budget de confirmation épuisé |

**Clause normative.** W1 **MUST NOT** redéfinir la frontière entre ces statuts,
ni ajouter de statut intermédiaire (« en cours », « écrit », « en attente de
confirmation »). Aucun n'existe dans C3, et aucun consommateur n'en a besoin :
`accepted` dit que la transaction est prise en charge, le verdict terminal dit
ce qu'elle est devenue.

**Cas de surface à énoncer**, parce qu'ils décrivent ce qui **circule ou ne
circule pas** :

| Cas | Trafic MQTT produit |
|---|---|
| Doublon dont le verdict terminal est en cache | le **même** ACK est republié, sans réexécution |
| Doublon encore **en vol** | **aucune publication** — `submit` rend `None` |
| Saturation de la file | un `rejected / queue_full / transient`, **jamais** de `accepted` |
| Échec **établi** de `accepted` avant l'écriture | un `rejected / bridge_unavailable / transient` (fail-closed C3) |

Le second cas mérite d'être écrit : un demandeur qui republie sa commande pendant
qu'elle est traitée **ne reçoit rien de plus**. C'est voulu — le verdict de la
transaction initiale suffira — mais un consommateur qui l'ignore pourrait
interpréter ce silence comme une perte.

**Précision de surface sur le rejeu.** L'ACK rejoué est l'objet **mémorisé**,
donc identique au premier ; en revanche son **topic** est recalculé depuis le
payload du **message doublon**. Deux messages portant le même `request_id` mais
un `role` différent verraient donc le même verdict publié sous **deux topics
différents**. C'est le comportement actuel du cœur, énoncé ici parce qu'il
appartient à la surface ; W1 ne le modifie pas et n'en fait pas une clause.

---

## 13. Duplication et rejeu

**Clause normative.** `request_id` est l'**unique** autorité de rejeu de la voie
de commande. La couche de transport **MUST NOT** tenir de mémoire de messages
déjà vus : ni cache de `mid`, ni ensemble de `request_id`, ni empreinte de
payload, ni fenêtre temporelle.

Motifs :

- une seconde mémoire aurait sa propre durée de vie, sa propre purge, et sa
  propre définition de l'identité — trois occasions de diverger du
  `TerminalCache`, dont le TTL monotone non glissant est déjà contracté (C3) ;
- le cœur est le seul endroit qui sait **ce que rejouer** : un doublon conclu
  doit recevoir son verdict, pas un silence. Une déduplication transport
  supprimerait le message, donc l'ACK avec lui.

**Clause normative.** Le drapeau `dup` **MUST** être transmis fidèlement et
**MUST NOT** altérer aucun verdict, ni provoquer un rejet, ni déclencher une
branche particulière. C'est déjà la règle du cœur (A10) ; W1 interdit qu'elle
soit contredite à la frontière.

**Conséquence à connaître.** Une redélivrance QoS 1 d'une commande **déjà
conclue** provoque la **republication** de son verdict terminal, tant que le TTL
du cache le porte encore. Un consommateur peut donc recevoir **plusieurs fois**
le même ACK terminal, à l'identique. Ce n'est pas un défaut : c'est la
conséquence directe du rejeu sans réexécution.

Et une limite, énoncée sans atténuation : **passé le TTL du cache terminal, ou
après un redémarrage du processus, la mémoire est vide** (C3). Une commande
redélivrée alors serait admise **comme neuve**. La seule garde qui subsiste dans
ce cas est **`expires_at`** — d'où §14.

---

## 14. Message retenu

### 14.1 Ce que l'interface expose réellement

`Message` porte un champ `retain`, et `PahoMqttClient._on_message` le renseigne
depuis le message Paho (A13). L'information **est donc disponible** à la
frontière. W1 ne l'invente pas et n'a pas à créer de surface pour l'obtenir.

**Mais ce qu'elle dit est étroit**, et le contrat doit le dire avant d'en
conclure quoi que ce soit :

- le drapeau reçu signale une **livraison de message stocké**, typiquement à
  l'établissement d'une souscription ;
- il **ne dit rien** de l'intention du producteur : une publication faite avec
  `retain=true` est livrée à un abonné **déjà présent** avec le drapeau à
  **faux** ;
- il est donc **impossible** de vérifier, à la réception, qu'un producteur a
  publié sa commande sans rétention.

### 14.2 Clause

**Clause normative.** Un message livré comme retenu **MUST** suivre exactement
le même chemin qu'un message vivant : il est remis au cœur, admis ou rejeté par
les règles ordinaires, et acquitté comme tout autre.

**Clause normative.** La couche de câblage **MUST NOT** rejeter, filtrer ni
traiter spécialement un message sur la foi du drapeau `retain`.

Motifs, dans l'ordre :

1. **Le danger réel est l'ancienneté, pas la rétention** — et `expires_at` le
   traite déjà, à l'admission **et** avant l'écriture (A11). Une commande
   retenue d'hier est rejetée `expired / temporal` : nommément, avec un ACK.
2. **La règle serait incohérente** : elle refuserait la livraison stockée d'une
   commande et accepterait la livraison vivante de la même commande publiée
   avec le même drapeau.
3. **Elle fabriquerait une sécurité inapplicable** : le contrat ne peut pas
   exiger `retain=false` d'un producteur, puisqu'il ne peut pas le constater.
4. Elle exigerait une modification du cœur, hors périmètre (§4).

### 14.3 Obligation du producteur, et limite du pont

**Clause normative, adressée au producteur.** Une commande **MUST** être publiée
**non retenue**.

**Limite énoncée sans atténuation.** Le pont **ne peut pas** faire respecter
cette obligation, **ne la vérifie pas**, et **ne l'annonce pas** comme une
garantie. Il ne purge aucun message retenu laissé sur le topic de commande par
un tiers, et n'en publie aucun lui-même. Si un tel message existe, il sera livré
à chaque nouvelle souscription — et rejeté `expired` dès que sa date le
justifie, ce qui est le seul rempart que W1 revendique.

---

## 15. Erreurs — qui les décide, qui les transporte

**Clause normative.** W1 **ne crée aucune taxonomie**. `Reason` et `ReasonClass`
sont fermés et suffisants (A4). La table ci-dessous dit **où naît** chaque
défaut et **comment il repart**, jamais ce qu'il vaut.

| Défaut | Décidé par | Transporté comment |
|---|---|---|
| Payload illisible, mal formé, champ manquant ou supplémentaire | C3, `parse_command` | `rejected / invalid_payload / permanent`, sur le seau `_unknown` ou le rôle brut (§9.2) |
| Valeur non numérique | C3 | `rejected / invalid_type / permanent` |
| Valeur non finie | C3 | `rejected / invalid_value_non_finite / permanent` |
| Rôle inconnu ou en lecture seule | C3, profil | `rejected / unsupported_role / permanent` |
| Hors bornes, hors grille | C3, profil | `rejected / invalid_value_out_of_range` ou `invalid_step`, permanent |
| Commande expirée | C3, `Clock` | `rejected / expired / temporal` |
| File saturée | C3 | `rejected / queue_full / transient`, **sans** `accepted` |
| Écriture prouvée non émise | C3, statut typé | `rejected / bridge_unavailable / transient` |
| Commande d'écriture refusée par le transport | C3 | `rejected / unsupported_command / permanent` |
| Écriture potentiellement émise, non confirmée | C3, relecture | `timeout` |
| Relecture conforme | C3 | `applied` |
| **Échec de publication d'un ACK** | transport | **rien n'est transporté** — §16 |
| **Commande perdue par MQTT** | broker / réseau | **rien** — aucun ACK, aucune trace côté demandeur ; §17.3 |

Les deux dernières lignes sont les seules qui appartiennent à W1, et ce sont
précisément celles où **il n'y a rien à transporter**. C'est pour cela qu'elles
doivent être écrites : un consommateur qui attend un ACK doit savoir qu'il
existe des cas où aucun n'arrivera.

---

## 16. Échec de publication d'un ACK

**Constat vérifié, avec ses responsabilités exactes.** `_conclude` met le
verdict terminal **en cache** puis libère `in_flight`, **avant** toute tentative
de publication (A8). Ensuite, deux mécanismes distincts — que V1 confondait :

| Cas | Ce qui se passe | Qui journalise |
|---|---|---|
| La publication **lève** (p. ex. `ValueError` de Paho sur un topic à joker) | `_publish_terminal` intercepte, absorbe, **ne retente pas** | **le cœur**, `_publish_terminal` |
| **Échec établi** (`rc` non nul, handle marqué `failed`) | rien ne lève ; le cœur **ignore** le handle rendu et ne l'examine pas | **l'adaptateur**, `PahoMqttClient.publish` |

Dans les deux cas le verdict est déjà en cache et n'est ni perdu, ni modifié, ni
remonté. Mais la **trace** ne vient pas du même endroit, et sur le chemin
terminal le cœur ne **constate** même pas l'échec établi : il ne consulte pas
`PublishHandle.failed` — ce qu'il ne fait que pour `accepted`, où le fail-closed
l'exige (A8).

**Clause normative.** W1 contractualise cet état de fait, sans le modifier :

1. le **verdict métier existe** indépendamment de la publication de son ACK ;
2. la publication d'un ACK est de **meilleur effort** : elle n'est ni garantie,
   ni confirmée avant de rendre la main, ni retentée ;
3. un échec de publication **MUST NOT** provoquer de rollback métier, de
   réexécution, de seconde écriture ni de changement de verdict ;
4. un échec de publication **MUST** rester observable par journalisation — par
   le cœur pour une exception, par l'adaptateur pour un échec établi ; le lot
   de câblage **MUST NOT** supprimer l'une ou l'autre de ces traces, et
   **MUST NOT** en déduire que le cœur observe les échecs établis terminaux ;
5. un mécanisme de **retry** d'ACK **MUST NOT** être introduit par le lot de
   câblage.

**Clause normative, adressée au consommateur.** L'absence d'un ACK **ne prouve
rien** : ni que la commande a été perdue, ni qu'elle n'a pas été appliquée. La
seule voie de rattrapage est une **nouvelle** transaction, avec un **nouveau**
`request_id` — le même identifiant rejouerait le verdict mémorisé plutôt que
d'obtenir un nouveau travail (C3).

**W1 ne promet donc aucune livraison du verdict au demandeur.** Il promet que le
verdict n'est pas perdu **par le pont**, ce qui est une affirmation plus faible
et vérifiable hors ligne.

---

## 17. Reconnexion — W1 consomme W0, et rien de plus

### 17.1 Ce que devient la souscription

**Clause normative.** La souscription au topic de commande **est** une
souscription logique au sens de W0 §6. Elle en reçoit toutes les propriétés,
sans qu'aucune soit reformulée ici :

- enregistrée avant transmission, inconditionnellement (W0 §7) ;
- réémise **intégralement** après chaque CONNACK **réussi** (W0 §8) ;
- réémise avec le **QoS exact** enregistré — donc 1 (W0 §8, §10) ;
- conservée si la transmission directe échoue (W0 §7.1) ;
- conservée par `disconnect()` (W0 §13) ;
- **irrétractable** (W0 §7.1, §12).

**Clause normative.** Le lot de câblage **MUST NOT** implémenter sa propre
restauration : ni réabonnement au rappel de connexion C11, ni compteur de
reconnexions, ni souscription répétée périodiquement. W0 le fait déjà ; le
doubler créerait une seconde autorité **et** contreviendrait à §7.2 en
redéclarant le topic.

### 17.2 Ce que la reconnexion ne garantit pas

**À énoncer sans atténuation**, en reprise directe de W0 §15 :

- réémettre un SUBSCRIBE **ne prouve pas** qu'il est accepté (A15) ;
- `online` **ne signifie pas** « abonné au topic de commande » (A16) ;
- un SUBACK **MUST NOT** être introduit par W1 ;
- `clean_session` reste `True` : aucune session persistante, aucune file côté
  broker.

### 17.3 La fenêtre de coupure — conséquence propre à la voie de commande

W0 §15 énonce qu'entre la coupure et la réémission, des messages publiés par un
tiers peuvent être perdus. Pour la voie de commande, cette conséquence a un nom
qu'il faut écrire :

> **Une commande publiée pendant que le pont est déconnecté est perdue,
> silencieusement, et ne produit aucun acquittement.**

Aucune file, aucune session persistante et aucun rattrapage n'existe. Le
demandeur ne peut le distinguer d'une commande reçue dont l'ACK s'est perdu
(§16). Sa seule conduite possible est celle de §16 : réémettre sous un
**nouveau** `request_id`, et traiter l'expiration comme sa borne de sûreté.

---

## 18. Configuration et C10 — aucune ouverture

**Trois natures distinctes**, que W1 ne confond pas :

| Nature | Exemple | Statut après W1 |
|---|---|---|
| **Constante produit** | `DEFAULT_ACK_TOPIC_PREFIX` | défaut de bibliothèque, jamais autorité runtime (§8.3) |
| **Champ interne vivant** | `MqttConfig.command_topic`, `MqttConfig.ack_topic_prefix` | **deviennent vivants** dans la composition future, **sans** devenir configurables |
| **Clé utilisateur TOML** | les treize clés de C10 | **inchangées** — aucune ajoutée, aucune retirée |

**Clause normative.** W1 **MUST NOT** exposer, et le lot de câblage **MUST NOT**
exposer, de nouvelle clé de configuration utilisateur. En particulier :

- `[mqtt].command_topic` **reste refusée nommément** ;
- `[mqtt].ack_topic_prefix` **reste refusée nommément** ;
- `[vclient].write_timeout_s` **reste non exposée** et **reste morte** — aucune
  écriture n'existe avant W4 ;
- le schéma demeure à **trois tables et treize clés**.

Motif : rendre un champ vivant dans la composition et le rendre réglable par
l'utilisateur sont **deux décisions différentes**. C10 a tranché la seconde par
la négative, avec un message d'erreur dédié ; W1 ne tranche que la première, et
n'a aucun besoin de rouvrir la seconde. Un topic de commande réglable serait de
surcroît une décision de **surface publique**, indissociable de l'arbitrage de
namespace non tranché (§19).

**Conséquence documentaire signalée, non appliquée.** Le jour où le lot de
câblage transmettra ces deux champs, la colonne « motif » du tableau
« Champs non exposés » de C10 cessera d'être exacte : `command_topic` ne sera
plus « mort », et `ack_topic_prefix` ne sera plus « mort dans le chemin
d'exécution ». **W1 ne modifie pas C10** ; il signale que ce lot devra
l'accompagner d'une mise à jour **factuelle** de ce tableau, sans aucune
ouverture de clé. Voir §28.

---

## 19. Namespace — divergence enregistrée, non tranchée

**Le fait.** Les topics transactionnels par défaut sont `boilerack/command` et
`boilerack/ack`, tandis que la surface de lecture a pour préfixe `boiler`,
réglable par `[read_surface].prefix`. C7 §1.3 qualifie les premiers de
**valeurs par défaut techniques introduites sans décision documentée**, et C7
§14 enregistre la convergence comme une **dette à arbitrer**, en s'interdisant
explicitement de la trancher (A23).

**Aggravation constatée** : `docs/boilerack.example.toml` décrit `prefix` comme
« racine de **TOUS** les topics publiés ». Cette phrase est exacte tant que
seule la surface de lecture publie ; elle deviendrait **fausse** le jour où des
ACK partiraient sous `boilerack/ack`.

**Options, exposées sans choix :**

| # | Option | Conséquence |
|---|---|---|
| N1 | Converger sur le préfixe de lecture : `<prefix>/command`, `<prefix>/ack/<rôle>` | un seul espace de noms par installation ; mais étend la sémantique d'une clé C10 existante et modifie deux valeurs par défaut — **décision C7 + C10** |
| N2 | Conserver deux racines distinctes, et le déclarer | aucun changement ; mais laisse deux racines sur un broker partagé, et laisse la phrase de l'exemple fausse |
| N3 | Troisième clé dédiée, propre à la surface transactionnelle | ouvre la surface utilisateur que §18 referme ; contredit C10 |

**Clause normative.** W1 **ne tranche pas** cette question, et **retient les
valeurs actuellement démontrées par le code** — `boilerack/command`,
`boilerack/ack` — sans en modifier aucune.

**Clause normative.** Une convergence **MUST NOT** être opérée
silencieusement, par un lot de câblage ou par un défaut modifié en passant.
Elle exige une décision explicite, portant sur C7 et C10.

**La porte est celle de C7, citée telle qu'elle est écrite** — W1 n'en déplace
pas le moment :

> « Avant toute composition root publique, le projet devra arbitrer la
> convergence des namespaces transactionnel et de lecture. C7-B **n'autorise
> pas** une coexistence permanente sans décision. » — C7 §14

C7 fixe donc l'échéance à la **composition root publique**. W1 **ne traduit pas**
cette échéance en « activation terrain » : ce serait interpréter, et rien dans
C7 ne pose cette équivalence. Ce qui relève du terrain reste hors W1 (§23), et
la porte de C7 vaut par elle-même, à son propre moment, qu'une activation
terrain suive ou non.

Classement : **REPORTÉ**, avec la porte C7 telle quelle. Voir §28.

---

## 20. Invariants délégués à W2 — liste fermée

W1 rencontre ces questions ; il **n'en tranche aucune**. Elles appartiennent au
contrat de concurrence et de cycle de vie.

1. Quel fil exécute `submit` — fil réseau de Paho, fil principal, ou autre.
2. S'il faut une file inter-fils entre la réception et l'admission.
3. Si l'admission peut publier `accepted` **depuis** le callback `on_message`.
4. Quel verrouillage protège `TerminalCache`, `InFlightRegistry` et
   `BoundedQueue`, aucun n'étant aujourd'hui déclaré sûr entre fils.
5. Qui appelle `process_next` / `drain`, à quelle cadence, et depuis quel fil.
6. L'entrelacement exact avec `run_due()` et l'attente du `ReadSurfaceRunner`.
7. La sérialisation entre lectures de télémétrie et écriture transactionnelle
   sur le même `vclient`.
8. Le sort d'une transaction **en vol** pendant `SIGTERM`, et la latence qu'elle
   ajoute.
9. L'effet sur `TimeoutStopSec` et sur les latences de sortie contractées par C9.
10. Le fait que `PahoMqttClient._handler` est écrit par `set_message_handler` et
    lu par `_on_message` **sans verrou** — constaté ici, non traité.
11. L'ordre de **livraison** des ACK au consommateur lorsque `accepted` et le
    verdict terminal sont publiés depuis des fils différents (§11.5).

**Ce qui n'est PAS dans cette liste, et pourquoi.** Le **nombre d'instances
`MqttClient` assemblées par la racine** n'est pas délégué : c'est une décision de
composition, tranchée en §7.5 sur la foi de `build_runtime`, de C8 et de C10,
sans qu'aucune propriété de fil n'intervienne. Ce qui reste W2 est l'usage
**concurrent** de cette instance unique — point 4 ci-dessus.

**Clause normative.** W1 **MUST NOT** être invoqué pour justifier une décision
figurant dans cette liste, et W2 **MUST NOT** modifier les clauses de W1 pour
s'y conformer : la surface est fixée, la concurrence s'y adapte.

---

## 21. Obligations de W3 — le lot de câblage

W1 dit **ce que W3 devra respecter**, jamais comment W3 s'organise.

**W3 MUST :**

1. lire le topic de commande depuis `MqttConfig.command_topic` (§7.1) ;
2. souscrire **une fois**, à **ce seul** topic, en **QoS 1 explicite** (§7.2,
   §7.3) ;
3. transmettre `MqttConfig.ack_topic_prefix` **explicitement** à
   `TransactionalCore` (§8.3) ;
4. remettre le payload **brut** au cœur, sans décodage ni filtrage (§11.3) ;
5. laisser `request_id` seule autorité de rejeu (§13) ;
6. s'en remettre à W0 pour la restauration après reconnexion (§17.1) ;
7. n'exposer **aucune** clé de configuration nouvelle (§18) ;
8. accompagner son câblage de la mise à jour **factuelle** de C10 §« Champs non
   exposés » (§18, §28) ;
9. consommer **l'instance `MqttClient` déjà construite** par la racine de
   composition, sans en créer une seconde (§7.5) ;
10. **réviser ou remplacer le test de non-ouverture**
    `tests/adapters/test_mqtt_paho.py::test_aucune_voie_de_commande_ouverte`
    — ou l'autorité qui en tiendra lieu à ce moment-là. Ce test assère
    aujourd'hui, au niveau **source**, que `".subscribe("`,
    `"set_message_handler"`, `"TransactionalCore"` et `"command_topic"`
    n'apparaissent pas dans `runtime.py`, `lifecycle.py` ni `cli.py`. Appliquer
    W1 rendra ces assertions **volontairement fausses** : c'est l'effet
    recherché, non une régression. W3 **MUST** traiter ce test explicitement —
    le remplacer par la vérification de ce que W1 exige réellement — et
    **MUST NOT** le contourner, le désactiver sans mention, ni le supprimer en
    silence. **W1 ne le modifie pas** (§19 du présent lot : aucun test touché) ;
11. prouver, par un test de composition **statique**, que `command_topic` et
    `ack_topic_prefix` sont disjoints au sens des niveaux MQTT (§9.3).

**W3 MUST NOT :**

12. écrire un topic ou un préfixe en dur ;
13. introduire une seconde déduplication, un retry d'ACK, ou un SUBACK ;
14. rejeter un message sur la foi de `retain` ou de `dup` ;
15. dériver quoi que ce soit du topic entrant ;
16. modifier `boilerack/core/` ;
17. construire un second client MQTT ou un second `client_id` (§7.5) ;
18. revendiquer une voie de commande **fonctionnelle** en l'absence d'adaptateur
    d'écriture et de profil réel (§22) ;
19. activer quoi que ce soit sur une installation réelle (§23).

---

## 22. Frontière avec W4

W1 est **indépendant du modèle réel de chaudière**, et doit le rester. Il ne
connaît, ne nomme et ne suppose :

- aucune commande `set…` réelle ;
- aucun profil de production, aucune borne, aucun pas, aucune tolérance ;
- aucun `VClient.write` concret — le dépôt n'expose aujourd'hui qu'un lecteur,
  `VClientCliReader` ;
- aucune correspondance entre un `role` et un datapoint.

**Conséquence à énoncer.** Le `role` est, pour W1, une **chaîne opaque** qui
sélectionne un segment de topic d'ACK et une entrée de profil. Aucune valeur de
rôle n'est contractée ici, et l'ensemble des rôles reste vide tant que W4 n'a
pas fourni de profil réel.

**Conséquence pratique.** Même intégralement câblée selon W1, la voie de
commande ne pourrait produire **aucun `applied`** sans surface d'écriture. Ce
n'est pas un défaut de W1 : c'est la raison pour laquelle W1 ne câble rien.

---

## 23. One-writer et porte terrain

W1 n'effectue **aucune écriture chaudière** et n'en décrit aucune.

**Rappel, non conception.** Une voie MQTT de commande **MUST NOT** devenir
active sur une installation réelle avant la qualification correspondante. W1 ne
conçoit ni la bascule terrain, ni son critère, ni son interrupteur : les
énoncer ici reviendrait à préparer une activation que rien n'autorise encore.

**Aucune porte n'est empruntée à un autre contrat.** §19 rapporte la porte de
C7 §14, qui vise la **composition root publique** ; W1 ne la reformule pas en
condition de terrain et n'en crée aucune autre. Les deux échéances sont
distinctes, portées par des contrats distincts, et W1 n'en fusionne aucune.

---

## 24. Ce que W1 ne prétend pas

À écrire tel quel, sans atténuation :

- W1 **n'affirme pas** qu'une souscription contractée en QoS 1 est acceptée, ni
  que le QoS accordé est 1 (§7.4) ;
- W1 **ne garantit aucune livraison** d'ACK au demandeur (§16) ;
- W1 **ne garantit aucune réception** de commande : celles publiées pendant une
  coupure sont perdues (§17.3) ;
- W1 **ne crée aucune garantie broker** : ni ordre, ni rétention, ni file, ni
  session ;
- W1 **ne rend pas** la voie de commande fonctionnelle : il en fixe la forme ;
- W1 **ne prouve rien contre un broker réel** — ses clauses sont dérivées de la
  lecture du dépôt et, pour les seuls faits Paho de §9.4, d'un sondage direct de
  la bibliothèque installée. Aucun broker n'a été sollicité ;
- W1 **n'affirme aucune validation** du segment de rôle employé dans un topic
  d'ACK : hors `+`, `#` et la longueur maximale, l'adaptateur n'en refuse
  aucun, et le contrat ne prétend pas le contraire (§9.4) ;
- W1 **ne donne aucun sens nouveau** à `online`, à `dup`, à `retain` ni à
  `source` ;
- W1 **n'attribue aucune sémantique** à `source`, que le cœur exige non vide et
  n'exploite nulle part.

---

## 25. Propriétés à verrouiller

Le lot qui appliquera ce contrat devra prouver, au minimum, les propriétés
suivantes. Chacune porte **une seule** obligation ; les noms de tests ne sont
pas fixés ici. Les propriétés W1-P22 à W1-P24 portent sur le **présent lot** et
se vérifient par constat direct.

| # | Propriété |
|---|---|
| W1-P1 | Le runtime souscrit à **un seul** topic de commande, dont la valeur provient de `MqttConfig.command_topic` |
| W1-P2 | La souscription est demandée en **QoS 1**, passé explicitement |
| W1-P3 | Le topic souscrit ne contient **aucun joker** (`+`, `#`) |
| W1-P4 | Le câblage appelle `MqttClient.subscribe` **exactement une fois** pour le topic de commande — les réémissions internes de W0 après CONNACK ne sont pas des appels du câblage et ne comptent pas (§7.5) |
| W1-P5 | La restauration après reconnexion est celle de **W0** ; aucun réabonnement propre au câblage n'existe |
| W1-P6 | Le préfixe d'ACK employé en runtime provient de `MqttConfig.ack_topic_prefix`, transmis explicitement ; le défaut du cœur ne décide jamais |
| W1-P7 | Le topic d'ACK vaut exactement `<ack_topic_prefix>/<rôle>`, et ne dépend ni du `request_id`, ni du statut, ni de la raison |
| W1-P8 | Un rôle inexploitable produit le seau `_unknown`, jamais un silence |
| W1-P9 | Tout ACK est publié en **QoS 1** |
| W1-P10 | Tout ACK est publié avec **`retain` faux** |
| W1-P11 | Aucun ACK n'est publié sur le topic de commande ; aucune commande n'est attendue sous le préfixe d'ACK |
| W1-P12 | Le payload est remis au cœur **en octets bruts** ; la couche de câblage ne le décode pas |
| W1-P13 | **Aucune** information métier n'est dérivée du topic entrant |
| W1-P14 | Aucune déduplication n'existe hors du cœur : `request_id` reste l'unique autorité de rejeu |
| W1-P15 | Le drapeau `dup` n'altère aucun verdict |
| W1-P16 | Un message livré **retenu** suit exactement le même chemin qu'un message vivant |
| W1-P17 | Le `request_id` de la commande est porté **inchangé** par chacun de ses ACK |
| W1-P18 | Un doublon encore **en vol** ne produit **aucune** publication MQTT |
| W1-P19 | Un verdict terminal existe même si la publication de son ACK échoue ; aucun retry n'est introduit |
| W1-P20 | Aucune clé TOML nouvelle n'est exposée ; `command_topic` et `ack_topic_prefix` restent refusées nommément |
| W1-P21 | Aucune corrélation SUBACK n'est introduite ; `online` ne signifie toujours pas « abonné » |
| W1-P22 | **W1 n'ouvre aucune voie runtime** : ni `subscribe`, ni `set_message_handler`, ni `TransactionalCore`, ni `command_topic` dans `runtime.py`, `lifecycle.py`, `cli.py` |
| W1-P23 | **Aucun module de `boilerack/core/` n'est modifié** par W1 |
| W1-P24 | **Aucune décision de concurrence** n'est prise par W1 : la liste §20 reste entièrement déléguée |
| W1-P25 | **Une seule instance `MqttClient`** existe en runtime, partagée par la surface de lecture et la surface transactionnelle ; aucun second `client_id` n'est introduit |

---

## 26. Mutations discriminantes

Aucun test n'est écrit à ce stade. **Aucune mutation n'est déclarée tuée.**
Chaque mutation ne change **qu'une seule chose**.

| # | Mutation | Propriété visée |
|---|---|---|
| W1-M1 | Souscrire à un topic écrit **en dur**, différent de `MqttConfig.command_topic` | W1-P1 |
| W1-M2 | Appeler `subscribe(topic)` sans QoS : le défaut **0** s'applique | W1-P2 |
| W1-M3 | Souscrire à `<command_topic>/#` | W1-P3 |
| W1-M4 | Ne pas souscrire du tout | W1-P1 |
| W1-M5 | Souscrire **de nouveau** à chaque rappel de connexion, en parallèle de W0 | W1-P4, W1-P5 |
| W1-M6 | Construire `TransactionalCore` **sans** transmettre `ack_topic_prefix` | W1-P6 |
| W1-M7 | Publier les ACK sous un préfixe littéral distinct de la configuration | W1-P6 |
| W1-M8 | Publier les ACK **retenus** | W1-P10 |
| W1-M9 | Publier les ACK en **QoS 0** | W1-P9 |
| W1-M10 | Publier l'ACK sur le **topic de commande** | W1-P11 |
| W1-M11 | Décoder le JSON dans le gestionnaire et rejeter avant d'atteindre le cœur | W1-P12 |
| W1-M12 | Dériver le `role` du **topic entrant** plutôt que du payload | W1-P13 |
| W1-M13 | Mémoriser les `request_id` déjà vus **dans la couche de câblage** | W1-P14 |
| W1-M14 | Ignorer les messages portant `dup` | W1-P15 |
| W1-M15 | Rejeter les messages livrés **retenus** | W1-P16 |
| W1-M16 | Publier l'ACK sous un `request_id` régénéré | W1-P17 |
| W1-M17 | Publier un `accepted` pour un doublon **en vol** | W1-P18 |
| W1-M18 | Réessayer la publication d'un ACK en échec | W1-P19 |
| W1-M19 | Accepter `[mqtt].command_topic` dans le fichier TOML | W1-P20 |
| W1-M20 | Ouvrir la voie runtime **dans le lot documentaire** | W1-P22 |
| W1-M21 | Dériver le topic d'ACK du **`request_id`** au lieu du rôle : `<préfixe>/<request_id>` | W1-P7 |
| W1-M22 | Ne **rien publier** lorsque le rôle est inexploitable, au lieu d'employer le seau `_unknown` | W1-P8 |
| W1-M23 | Construire un **second** `PahoMqttClient` pour la voie de commande, depuis le même `MqttConfig` | W1-P25 |

**W1-M2 mérite d'exister séparément de W1-M1** : elle conserve le bon topic et
la bonne autorité, et ne dévie que par une **omission de paramètre**. C'est la
forme sous laquelle le défaut apparaîtrait réellement — personne n'écrit
`qos=0`, on oublie de l'écrire du tout.

**W1-M5 attaque deux propriétés à la fois et c'est assumé** : réabonner
soi-même viole simultanément l'unicité de la déclaration et la délégation à W0.
Les séparer produirait deux mutants indiscernables.

**W1-M21 et W1-M22 comblent une lacune de la première rédaction** : W1-P7 (le
topic dépend du rôle, et de rien d'autre) et W1-P8 (le seau `_unknown`) étaient
énoncés sans qu'aucun mutant ne les attaque. Chacune ne change qu'une décision —
la **dimension** dont dérive le topic pour W1-M21, la **présence** de l'ACK de
repli pour W1-M22 — et toutes deux sont observables sur le chemin nominal d'un
rejet de forme.

**Exactement trois propriétés n'ont volontairement aucune mutation** : **W1-P21,
W1-P23 et W1-P24**. Ce sont des propriétés de **portée et de non-régression** —
absence de SUBACK, non-modification du cœur, non-décision de concurrence. Les
muter consisterait à introduire le composant qu'elles interdisent, ce qui
n'éprouverait rien du code visé — exactement le raisonnement de W0 §17 pour
W-P19 à W-P22. Un constat direct est plus honnête qu'une table gonflée.

**W1-P22 n'est pas de celles-là** : elle possède W1-M20, qui la met réellement à
l'épreuve en ouvrant la voie runtime dans le lot documentaire. La première
rédaction l'avait rangée par erreur parmi les propriétés exemptées, alors qu'un
mutant lui était déjà attribué ; l'exemption ci-dessus est désormais exacte, et
vérifiée par recoupement mécanique de la table (§18 du protocole de contrôle).

---

## 27. Risques et inconnues

| # | Risque ou inconnue | Portée |
|---|---|---|
| W1-R1 | **Illusion de voie ouverte** : W1 décrit une surface complète et cohérente, dont **rien** n'est câblé. Le risque principal du lot est qu'un lecteur la croie active | §1, §4 |
| W1-R2 | **Tentation de câbler « puisque le contrat est écrit »**, avant W2 et sans profil réel | §20, §22 |
| W1-R3 | **Dérive vers une garantie de livraison** : ajouter un retry d'ACK, une file, une session persistante, parce que §16 et §17.3 sont inconfortables | §16, §17.3 |
| W1-R4 | **Double autorité rétablie par inadvertance** : un appel à `TransactionalCore(...)` sans `ack_topic_prefix` restaure silencieusement le défaut du cœur | §8.3, W1-M6 |
| W1-R5 | **Duplication de littéral résiduelle** : `"boilerack/ack"` existe toujours dans deux modules ; leur divergence future ne ferait échouer aucune vérification | §8.3 |
| W1-R6 | **Aucune borne de taille** de payload n'est contractée ; un message volumineux traverserait la frontière jusqu'au décodeur JSON. Le risque n'est pas sans propriétaire : une politique éventuelle est **REPORTÉE au contrat qui possède la taxonomie de rejet** (C3), jamais ajoutée à la frontière | §11.1, S5 |
| W1-R7 | **Le demandeur contrôle un segment du topic d'ACK** sur le chemin de rejet : `/` étant accepté par Paho, il peut créer une arborescence arbitraire sous le préfixe d'ACK. `+` et `#` sont seuls refusés, et ce refus supprime alors l'ACK. Aucune garde ne couvre le reste | §9.4, T10 |
| W1-R8 | **Divergence de namespace non résolue** : deux racines de topics coexistent, et l'exemple de configuration décrit `prefix` comme la racine de *tous* les topics | §19 |
| W1-I1 | Le QoS **accordé** par le broker à la souscription n'est ni observé ni observable, faute de SUBACK | §7.4 |
| W1-I2 | Le comportement réel d'un broker face à un message **retenu** laissé sur le topic de commande — délai, rétention, purge | §14.3 |
| W1-I3 | L'ordre réel de livraison, chez le consommateur, de `accepted` puis du verdict terminal | §11.5 |
| W1-I4 | La forme exacte d'un échec de `subscribe` côté Paho reste non éprouvée (W0-I1, inchangée) | W0 §11.1 |
| W1-I5 | La validité protocolaire d'une valeur de `command_topic` : seule la non-vacuité est vérifiée | §7.2 |
| W1-I6 | Le comportement d'une transaction en vol lors d'un arrêt — délégué, donc inconnu à ce stade | §20 |

---

## 28. Points signalés — décisions qui ne sont pas celles de W1

**Cinq** points sont **nommés et arrêtés ici**, sans être traités. Chacun exige
un lot ou une décision propre ; aucun ne doit être réglé par un ajout
opportuniste.

| # | Point | Qui doit trancher |
|---|---|---|
| S1 | **Convergence de namespace** transactionnel / lecture, et phrase de `docs/boilerack.example.toml` qualifiant `prefix` de racine de *tous* les topics | décision explicite touchant **C7 et C10**. Échéance : celle que C7 §14 fixe lui-même — **« avant toute composition root publique »**, citée sans être déplacée (§19) |
| S2 | **Mise à jour factuelle de C10** § « Champs non exposés » lorsque les deux champs deviendront vivants — sans ouverture de clé | **W3**, dans le lot qui câble (§18) |
| S3 | **Maîtrise du segment de rôle** du topic d'ACK sur le chemin de rejet — un demandeur choisit aujourd'hui un sous-topic sous le préfixe d'ACK (§9.4). W1 ne prescrit **aucune** forme de correction | lot dédié touchant `core/engine.py` — **jamais** le lot de câblage |
| S4 | **Déduplication du littéral** `"boilerack/ack"` entre `adapters/config.py` et `core/engine.py` | lot dédié ; sans effet sur le chemin d'exécution une fois §8.3 appliqué |
| S5 | **Politique de taille de payload** entrant, si elle devient nécessaire | le contrat qui possède `Reason` — donc **C3** — parce que seule cette autorité peut produire un rejet typé plutôt qu'une disparition (§11.1) |

**Aucun de ces points n'a été modifié par W1.** Aucun fichier autre que le
présent document n'a été touché.

---

## 29. Ce que W1 ne fait pas

Aucun changement du cœur, du transport, des adaptateurs, du runtime, du
lifecycle, de la CLI, de la surface de lecture, de la configuration, des tests
ou du packaging · aucune souscription · aucun gestionnaire de message · aucun
`TransactionalCore` instancié · aucune pompe d'exécution · aucune écriture ·
aucun profil réel · aucune clé de configuration ajoutée · aucune modification
d'un contrat existant · aucune modification de W0.

**AUCUNE CONFORMITÉ TERRAIN N'EST REVENDIQUÉE.** Rien n'a été éprouvé contre un
broker, un `vcontrold` ou une chaudière réels. Ce contrat est intégralement
dérivé du dépôt, lu en lecture seule à la base `e9306de`.

---

## 30. Renvois

`c3-transactional-core.md` — **autorité amont directe** : payload, validation,
statuts, raisons, déduplication, expiration, publication des ACK, couture
d'entrée MQTT · `c4-real-adapters.md` — adaptateur Paho, QoS, entrée des
messages, honnêteté du `PublishHandle` · `w0-mqtt-subscription-recovery.md` —
persistance et réémission des souscriptions, absence de SUBACK, irrétractabilité
· `c7-mqtt-read-contract.md` — séparation lecture / transaction, divergence de
namespace enregistrée · `c11-presence-recovery.md` — reprise de présence,
session neuve attendue · `c7c1-read-surface-primitives.md` — refus des
jokers et des caractères de contrôle dans un topic · `c8-composition-root.md` — racine de composition, seul
endroit où les adaptateurs sont câblés · `c9-process-lifecycle.md` — arrêt du
processus, champs morts exclus · `c10-user-interface.md` — schéma fermé, clés
refusées, champs non exposés · `c2-infrastructure.md` — frontières et doubles.

**Chantiers futurs, hors W1** : contrat de concurrence et de cycle de vie
transactionnel (**W2**) · câblage runtime de la voie de commande (**W3**) ·
adaptateur d'écriture, dialecte `vclient` et profil réel (**W4**) ·
convergence de namespace (S1) · validation du segment de rôle (S3) ·
qualification terrain.

---

## 31. Fermeture

W1 est **fermé** en tant que contrat. Il ne livre qu'un document, ne modifie
aucun code, aucun test et aucun autre contrat, et laisse le dépôt dans l'état
fonctionnel exact où W0 l'a laissé : **la voie de commande reste fermée**.
