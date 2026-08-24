# W4-E1 — Composition, autorité d'activation et arbitrage de namespace

> **Lot W4-E1 — contrat.** Aucune ligne de code, aucun test modifié, aucune
> commande réelle, aucun terrain. Ce document rend **quatre décisions
> normatives** et rien d'autre : où vit la composition, ce qui l'autorise,
> comment converge le namespace, et quelles barrières remplacent celles que
> W4-E2 rendra fausses.
>
> Il existe pour que **W4-E2 soit mécanique** : son producteur ne doit avoir
> aucune décision normative à prendre.

---

## 1. Statut, portée, autorité

**Statut** — contrat de conception. Normatif pour **W4-E2** (implémentation
hors terrain), prescripteur pour **W4-F** (bascule terrain).

**Portée** — l'assemblage en production de la voie transactionnelle, l'autorité
qui l'autorise, et le namespace MQTT sous lequel elle vit. Rien d'autre.

**Ce sur quoi W4-E1 a autorité** — l'emplacement de la composition ; la forme de
l'autorité d'activation ; l'arbitrage de la dette C7 §14 ; la liste fermée des
barrières de remplacement.

**Ce sur quoi W4-E1 n'a aucune autorité** — la sémantique transactionnelle (C3),
la classification de transport (W4-A), le contenu du profil (W4-D), la forme du
payload et des ACK (W1), la surface de lecture (C7), l'activation réelle et
l'exclusivité opérationnelle (W4-F).

> **Clause de non-régression.** W4-E1 **MUST NOT** modifier une clause de C3,
> C5, C6, C7, W1, W2, W3, W4-A, W4-B ou W4-D. Il **dispose** une dette inscrite
> par C7 §14 ; il n'en réécrit pas le texte.

---

## 2. Autorités

| Réf | Document | Ce qu'il fixe, et que W4-E1 consomme sans le réécrire |
|---|---|---|
| **C3** | `c3-transactional-core.md` | verdicts, déduplication, confirmation par relecture |
| **C7** | `c7-mqtt-read-contract.md` §4.2, §11, **§14** | table des mesures, onze suffixes v1, **dette de namespace** |
| **C10** | `c10-user-interface.md` | forme de la configuration utilisateur, refus des clés inconnues |
| **W1** | `w1-mqtt-transaction-surface.md` **§8**, §22, §23 | payload, ACK, **autorité runtime du préfixe**, one-writer laissé ouvert |
| **W2/W3** | concurrence, câblage | propriétaire unique, cadence, `build_transaction_surface` |
| **W4-A** | §6, §9, §9.3, §18.4 | succès local ≠ appliqué, table fermée, statuts encore interdits |
| **W4-C** | §16 | signature de succès, inconnues non levées |
| **W4-D** | `production_profile.py` | profil réel, un seul rôle |
| **`provenance.md`** | — | aucune constante de site dans le dépôt |

---

## 3. Préconditions

W4-E1 n'est ouvrable que parce que **W4-A, W4-B, W4-C et W4-D sont fermés**.
Chacun a livré une pièce ; aucune n'est assemblée.

---

## 4. Non-objectifs

W4-E1 — et W4-E2 après lui — **ne font pas** :

1. activer réellement l'écriture chez un utilisateur ;
2. toucher le Pi, `vclient`, le pont historique, le superviseur ou systemd ;
3. trancher l'exclusivité opérationnelle entre deux écrivains ;
4. modifier `core/`, la taxonomie de transport, le profil ou l'adaptateur ;
5. exposer de nouvelles clés de transport à l'utilisateur ;
6. lever une inconnue de W4-C par raisonnement documentaire.

---

## 5. Topologie avant W4-E — état constaté

La chaîne de composition réelle, relevée dans le code et non déduite :

```
cli.main
  → load_config(chemin)            → RuntimeConfig
  → run_lifecycle(config)
  → build_runtime(config, wakeup.stop, clock=wakeup.clock)   ← `transaction` NON transmis
  → runtime.runner.run()
```

| Fait | Constat |
|---|---|
| `build_runtime` porte déjà `transaction: TransactionSurface \| None = None`, mot-clé | la couture **existe**, et sa docstring la déclare « point d'entrée prévu pour W4 » |
| `build_transaction_surface` existe | jamais appelée en production |
| `build_production_profile` existe (W4-D) | jamais appelée en production |
| `VClientCli`, `VclientWriteInvocation` existent (W4-B) | jamais construits en production |
| `lifecycle.py` est **l'unique appelant** de `build_runtime` | il n'y passe pas `transaction` |
| l'unique `PahoMqttClient` est construit **dans** `build_runtime` | il n'est exposé nulle part : `Runtime` ne porte que `publisher`, `runner`, `transaction` |

> **La fermeture actuelle est une ABSTENTION, pas une impossibilité.** Les
> quatre pièces existent et sont assemblables ; rien ne les assemble. La
> garantie tient à une seule ligne — l'appel de `build_runtime` sans
> `transaction` — et aux preuves structurelles qui vérifient que personne ne la
> contourne.
>
> Le dire ainsi n'est pas une précaution de style : c'est la raison d'être de
> W4-E1. Une abstention ne se maintient pas toute seule.

---

## 6. Décision 1 — où vit la composition

> **Clause.** La **décision** de composer appartient à
> **`src/boilerack/lifecycle.py`**, et à lui seul.

Motifs, tous vérifiables :

- `lifecycle` **possède déjà la configuration complète** et est l'**unique
  appelant** de `build_runtime` ;
- `build_runtime` **expose déjà** un point d'entrée `transaction` : la couture
  n'est pas à créer de toutes pièces ;
- `runtime.py` doit **conserver sa propriété d'import léger** — un test en
  interpréteur neuf prouve que son import ne charge ni `transaction_wiring`, ni
  `core.engine`. Décider la composition dans `runtime.py` détruirait cette
  propriété, qui est précisément ce qui interdit l'activation par simple import ;
- `transaction_wiring.py` **contient déjà la fabrique** : `build_transaction_surface`
  est complète et n'a besoin de rien.

> **Clause.** W4-E2 **MUST NOT** introduire une **troisième racine de
> composition**. Les deux existantes — `build_runtime` pour les adaptateurs,
> `build_transaction_surface` pour la voie transactionnelle — suffisent.

### 6.1 Une couture bornée dans `build_runtime` — pourquoi elle est nécessaire

Le paramètre `transaction` existant attend une `TransactionSurface` **déjà
construite**. Or cette surface exige, par W1 §7.5, **la même instance
`MqttClient`** que la surface de lecture — et cette instance est construite
**dans** `build_runtime`, qui ne l'expose nulle part. `Runtime` ne porte que
`publisher`, `runner` et `transaction`.

**Conséquence : `lifecycle` ne peut pas construire la surface avant l'appel.** Il
ne dispose pas du client. Exiger un `build_runtime` littéralement inchangé
rendrait W4-E2 **irréalisable** — ou pousserait son producteur à construire un
second client MQTT, ce que W1 §7.5 interdit formellement.

Le contrat autorise donc **une extension bornée et nommée**, et rien de plus.

> **Clause.** `build_runtime` **MAY** recevoir un paramètre supplémentaire,
> **réservé aux mots-clés**, de la forme conceptuelle :
>
> ```
> transaction_factory:
>     Callable[[PresenceMqttClient, Clock], TransactionSurface] | None = None
> ```
>
> Il **MUST** valoir `None` par défaut. Lorsqu'il vaut `None`, le comportement de
> `build_runtime` est **identique à aujourd'hui**.
>
> La fabrique **MUST** être appliquée **après** la construction du client MQTT
> unique et **avant** celle du `ReadSurfaceRunner`, de sorte que la surface reçoive
> la même instance de client et la même horloge que le publieur.

> **Clause — `build_runtime` ne décide rien.** Il **MUST NOT** : décider s'il
> faut composer · choisir un namespace · construire un `Profile` · construire un
> `VClient` · connaître W4-F · construire un second client MQTT. Il **applique**
> une fabrique qu'on lui remet, ou n'en applique aucune.
>
> Exécuter une fabrique injectée **ne fait pas** de `build_runtime` une seconde
> autorité de composition : l'autorité est celle qui **décide**, et c'est
> `lifecycle`. La distinction est la même que celle déjà retenue pour l'horloge,
> injectée sans que l'injection ne transfère la décision.

**Conséquences précises pour W4-E2** : `transaction_wiring.py` **MUST** rester
inchangé · `core/` **MUST** rester inchangé · `runtime.py` change **uniquement**
pour porter `TransactionSurfaceConfig` et le membre de `RuntimeConfig` (§7), et
pour la couture ci-dessus. Le paramètre `transaction` existant **MUST** être
conservé : il reste le point d'entrée des preuves hors terrain qui fournissent
une surface déjà construite.

---

## 7. Décision 2 — l'autorité d'activation

### 7.1 Ce qui existe, et ce qui n'existe pas

Le dépôt ne possède **aucun** mécanisme de mode, de drapeau de fonctionnalité,
de registre de surfaces ou de rôle d'écrivain. Inventer un mécanisme là où il
n'y en a pas serait ajouter une couche sans autorité.

Il possède en revanche une autorité de configuration **stricte** : `load_config`
**refuse toute clé et toute table inconnues**. Une clé d'activation ne peut donc
ni apparaître par faute de frappe, ni être ignorée en silence.

### 7.2 La clause

> **Clause.** L'autorité d'activation est une **clé de configuration
> booléenne**, dans une **table dédiée** :
>
> ```toml
> [transaction_surface]
> enabled = false
> ```
>
> - **table** : `transaction_surface` — le nom reprend celui de la classe
>   `TransactionSurface` et fait pendant à `read_surface`. Aucun vocabulaire
>   nouveau n'est introduit ;
> - **clé** : `enabled`, booléenne stricte ;
> - **défaut** : `false` ;
> - **table absente** : équivaut à `enabled = false` ;
> - **clé absente** : équivaut à `false` ;
> - **valeur non booléenne** : `ConfigurationError`, jamais une coercition ;
> - **clé ou table inconnue** : `ConfigurationError`, comme toute autre.

**Emplacement de la structure** — `TransactionSurfaceConfig` **MUST** être
déclarée dans **`src/boilerack/runtime.py`**, auprès de `RuntimeConfig`.

Deux logements étaient recevables ; celui-ci est retenu pour deux raisons.
D'abord `adapters/config.py` s'annonce comme portant les « modèles de
configuration technique des **adaptateurs réels** (C4) » — or une autorité de
composition n'est pas une configuration d'adaptateur, et l'y placer aurait exigé
d'amender cette docstring pour un type qui n'y a pas sa place. Ensuite le
couplage est **nul** : `config.py` importe déjà `RuntimeConfig` depuis
`runtime`, si bien qu'aucune arête d'import n'est créée, et `adapters/config.py`
n'a pas à changer du tout.

**Aucun module nouveau** n'est créé pour ce seul type.

### 7.3 Ce que l'autorité signifie — et ce qu'elle ne signifie pas

> **Clause.** `enabled = true` signifie **exactement** : « la configuration
> autorise la composition de la voie transactionnelle ». Cela **ne signifie
> pas** que Boilerack est l'écrivain souverain de l'installation, ni qu'une
> écriture est légitime, ni que le pont historique a été neutralisé.
>
> Cette distinction est la frontière W4-E / W4-F, et le nom de la clé la porte :
> elle active une **surface**, pas une écriture.

### 7.4 Ce que l'autorité doit garantir

| # | Exigence | Comment elle est tenue |
|---|---|---|
| 1 | explicite | clé nommée, refusée si mal orthographiée |
| 2 | **défaut fermé** | `False` ; un fichier existant reste valide **et fermé** |
| 3 | testable hors ligne | `RuntimeConfig` se construit à la main, sans TOML ni broker |
| 4 | transférable | valeur de déploiement, non de site |
| 5 | aucune donnée de site | un booléen |
| 6 | **pas d'activation par import** | la composition est un **appel** dans `lifecycle` ; `runtime` reste léger (§6) |
| 7 | **pas d'activation par présence du profil** | la fabrique n'est appelée que dans la branche autorisée |
| 8 | **pas d'activation par présence de l'adaptateur** | idem |
| 9 | pas d'activation par section partielle | `[transaction_surface]` sans `enabled` reste fermée |
| 10 | compatible W4-F | l'interrupteur est **livré fermé** ; le tourner appartient à W4-F |

---

## 8. Décision 3 — arbitrage de la dette C7 §14

### 8.1 La dette, citée

C7 §14 enregistre, sans la trancher :

> « Le code actuel publie sous `boilerack/command` et `boilerack/ack`, alors que
> la surface de lecture aura pour défaut `boiler`. Cette incohérence de
> namespace entre les deux surfaces est **réelle** et devra être arbitrée. […]
> **Avant toute composition root publique**, le projet devra arbitrer la
> convergence des namespaces transactionnel et de lecture. C7-B **n'autorise
> pas** une coexistence permanente sans décision. »

W4-E **est** cette composition root publique. La dette est donc sur son chemin,
et lui seul peut la lever.

### 8.2 Ce que le code dit réellement

La surface de lecture publie sous **un préfixe configurable**, dont `boiler`
n'est que le **défaut** :

```
<prefix>/telemetry/…      8 suffixes
<prefix>/bridge/…         3 suffixes
```

`V1_SUFFIXES` énumère ces onze suffixes et **exclut explicitement** la commande
et les acquittements, en renvoyant à C7 §14. La structure anticipe donc des
sous-arbres frères sous une même racine.

Côté transactionnel, `MqttConfig` porte `command_topic = "boilerack/command"` et
`ack_topic_prefix = "boilerack/ack"`. Ces deux valeurs sont **absentes des clés
utilisateur** : `load_config` les refuserait. **Aucune n'a jamais été publiée** —
il n'existe aucun écrivain actif.

### 8.3 Options examinées

| # | Option | Compatibilité C7 §14 | Coût de migration | Stabilité API | Verdict |
|---|---|---|---|---|---|
| **A** | **Racine unique configurable, sous-arbres `telemetry/`, `bridge/`, `command`, `ack/`** | convergence pleine | change deux **défauts jamais publiés** | surface de lecture **intacte** | **RETENUE** |
| B | Tout sous `boilerack/…`, migration de la lecture | convergence pleine | change le défaut d'une surface **livrée et documentée** (C7 §11, C10, TOML d'exemple) | **rupture publique** | rejetée |
| C | Deux racines, coexistence contractualisée | satisfait la lettre — une décision est rendue | nul | deux racines pour une installation : ACL, découverte et abonnements dédoublés | rejetée |
| D | Racine transactionnelle propre, configurable séparément | ne converge pas | nul | ajoute une clé publique et un second porteur de racine | rejetée |

L'option **A** est retenue parce qu'elle est la seule qui **converge réellement**
en ne coûtant que des défauts que rien n'a jamais employés. L'option B
converge aussi, mais en cassant une surface livrée ; l'écart de coût est décisif.

### 8.4 La clause

> **Clause normative.** Une installation Boilerack possède **une seule racine de
> topics**. Les surfaces en sont des **sous-arbres** :
>
> | Sous-arbre | Surface | Autorité |
> |---|---|---|
> | `<racine>/telemetry/…` | lecture | C7 §4.2, §11 |
> | `<racine>/bridge/…` | lecture, service | C7 §11 |
> | `<racine>/command` | transactionnelle, entrant | W1 |
> | `<racine>/ack/<role>` | transactionnelle, sortant | W1 §8, C3 |
>
> **La racine est celle déjà configurée pour la surface de lecture.** Aucune
> nouvelle clé n'est créée : la convergence se fait en **dérivant** les topics
> transactionnels de la racine existante, non en ajoutant un second réglage.

> **Clause.** À la composition, W4-E2 **MUST** dériver `command_topic` et
> `ack_topic_prefix` de la racine, avec **la même validation** que la surface de
> lecture (`normalize_prefix`, `build_topic`), et les transmettre
> **explicitement** — ce que W1 §8.3 exige déjà du préfixe d'ACK.
>
> Les valeurs `"boilerack/command"` et `"boilerack/ack"` deviennent des **défauts
> de bibliothèque**, exactement au sens où W1 §8.3 a qualifié
> `DEFAULT_ACK_TOPIC_PREFIX` : légitimes pour un test qui construit une
> configuration sans composition, **jamais** l'autorité runtime.

**Pas de troisième porteur.** W1 §8.3 interdit d'introduire un troisième porteur
du préfixe d'ACK. La dérivation n'en crée aucun : la racine porte la **racine**,
`MqttConfig.ack_topic_prefix` reste le **seul** porteur du préfixe d'ACK, et la
dérivation est une fonction, pas une copie.

#### Le `MqttConfig` dérivé et W1 §7.5 — tension disposée

`build_transaction_surface` prend un `MqttConfig` complet. Pour lui transmettre
les topics dérivés, W4-E2 devra donc produire un `MqttConfig` **dérivé** de
celui de la configuration. Or W1 §7.5 écrit littéralement que le lot de câblage
« **MUST NOT** dériver un second `MqttConfig` ». La tension est réelle et doit
être disposée ici, pas laissée au producteur.

**Ce que §7.5 vise.** Sa motivation entière porte sur l'**identité de
connexion** : deux instances partageant un `client_id` « se déconnectent
mutuellement en boucle », et le registre de souscriptions de W0 est **par objet
client**. Sa propre clause de portée le dit : « Cette clause dit qu'il existe
**un seul objet client** en runtime. » L'interdiction protège l'unicité du
client, non l'unicité de la valeur des topics.

> **Clause.** Le `MqttConfig` transmis à `build_transaction_surface` **MUST**
> être dérivé de celui de la configuration, et **MUST** ne différer que par
> **deux champs** :
>
> - `command_topic`
> - `ack_topic_prefix`
>
> Il **MUST** préserver à l'identique **`host`, `port`, `client_id`, `keepalive`,
> `username`, `password` et `tls`** — c'est-à-dire toute propriété de connexion.
>
> Il **MUST NOT** produire : un second client MQTT, un second `client_id`, une
> seconde identité de connexion.

> **Disposition.** Un `MqttConfig` dérivé qui ne diffère que par ces deux topics
> **n'est pas une seconde connexion**, et ne relève donc pas de ce que W1 §7.5
> interdit. L'invariant que §7.5 protège — **une seule instance de client**, la
> même pour les deux surfaces — est intégralement tenu, et §12 en fait une
> barrière falsifiable.
>
> W4-E2 n'a **aucune** décision à prendre sur ce point.

**Une verrue conservée, et nommée.** La racine s'appelle aujourd'hui
`read_surface.prefix`, nom hérité du temps où la lecture était la seule surface.
Après cet arbitrage, elle gouverne les deux.

> **Clause — le renommage est HORS périmètre.** La clé `[read_surface].prefix`
> est **conservée volontairement**, pour compatibilité. Sa **sémantique est
> étendue** ; elle n'est **pas renommée**. Renommer une clé publique pour une
> raison cosmétique coûterait une rupture à tous les déploiements existants.

#### La décision porte sur C7 **et** C10

W1 §19 énumère les options de convergence et qualifie celle qui est retenue ici
— sa variante **N1** — de « **décision C7 + C10** ». La dette n'appartient donc
pas au seul contrat de lecture.

C10 décrit aujourd'hui `[read_surface].prefix` comme la racine des topics **de
lecture**. Après W4-E2, cette description serait **incomplète** : la clé
gouvernerait quatre sous-arbres. W1 §19 relève d'ailleurs la même chose dans le
fichier d'exemple, qui annonce « racine de **TOUS** les topics publiés » — phrase
que l'option retenue rend **vraie**, là où une coexistence à deux racines
l'aurait rendue fausse.

> **Clause.** W4-E2 **MUST** amender `docs/design/c10-user-interface.md` pour que
> l'entrée `[read_surface].prefix` énonce qu'elle gouverne la **racine commune**
> des quatre sous-arbres :
>
> ```
> <prefix>/telemetry/…
> <prefix>/bridge/…
> <prefix>/command
> <prefix>/ack/<role>
> ```
>
> L'amendement **MUST** être une extension de sémantique, sans renommage, sans
> nouvelle clé, et sans réécriture de l'historique de C10.

### 8.5 Namespace ≠ one-writer

> **Clause.** Un namespace, quel qu'il soit, **ne garantit en rien** qu'un seul
> écrivain agisse sur la chaudière. Deux processus peuvent publier sous le même
> topic, ou écrire par des chemins entièrement disjoints — c'est précisément le
> cas aujourd'hui, le pont historique n'utilisant pas MQTT pour écrire mais
> `vclient` en direct.
>
> W4-E **MUST NOT** créer : verrou distribué, bail, protocole de propriété,
> battement de souveraineté, ni aucun mécanisme que le pont historique ne
> respecterait pas. Une garantie que l'autre partie ignore n'est pas une
> garantie.
>
> **La seule garantie de W4-E** : autorité fermée ⇒ Boilerack ne compose pas sa
> voie d'écriture, donc n'est pas un second écrivain. L'exclusivité réelle est
> **opérationnelle** et appartient à **W4-F**.

---

## 9. Surface transactionnelle — rappel, pas conception

W4-E n'invente aucun topic et aucun champ. Tout est déjà contracté :

**Payload de commande** (W1 A1, C3) — six champs exacts : `request_id`, `ts`,
`expires_at`, `source`, `role`, `value`. Aucun champ supplémentaire n'est
interprété ; tout champ inconnu est refusé.

**Verdicts** (C3) — `accepted`, `applied`, `rejected`, `timeout`, publiés sous
`<racine>/ack/<role>`.

**Autorités runtime** — `command_topic` et `ack_topic_prefix` de `MqttConfig`,
transmis explicitement à la construction (W1 §8.3), désormais dérivés de la
racine (§8.4).

> **Trois états à ne jamais confondre.**
> *namespace disponible* — les topics existent contractuellement ;
> *writer actif* — la voie est composée et souscrit ;
> *writer souverain* — Boilerack est le seul à écrire sur la chaudière.
>
> W4-E1 fixe le premier. W4-E2 rend le deuxième possible **sous autorité**.
> **Seul W4-F peut établir le troisième.**

---

## 10. `applied` — inchangé, et hors périmètre

> **Clause.** `raw == "OK"` ne produit **jamais** `applied`. La chaîne reste :
> écriture locale → relecture → confirmation → verdict métier. Pour un rôle
> `INTEGER`, la confirmation est une **égalité stricte**.

Le cœur fait déjà exactement cela : `_PROVEN_NOT_EMITTED` ne contient que
`DAEMON_UNREACHABLE`, que l'adaptateur d'écriture **ne produit jamais** (W4-A
§11.6) ; tout succès local mène donc à la boucle de confirmation.

> **Clause.** W4-E2 **MUST NOT** modifier `core/`. L'obligation 21 de W4-A §18
> l'interdit déjà, et rien ne l'exigerait.

---

## 11. Barrières périmées et garanties de remplacement

W4-E2 rendra volontairement fausses des garanties aujourd'hui vraies. Chacune
**MUST** être remplacée, jamais simplement supprimée.

| Ancienne garantie | Pourquoi elle devient fausse | Garantie de remplacement |
|---|---|---|
| **zéro appel** de production à `VClientCli` | `lifecycle` le construira sous autorité | **liste fermée d'appelants** : `lifecycle.py` et lui seul |
| **zéro appel** à `VclientWriteInvocation` | idem | idem |
| **zéro appel** à `build_production_profile` | idem | idem |
| **zéro appel** à `build_transaction_surface` | idem | idem |
| `runtime.transaction is None` **inconditionnellement** | vrai seulement autorité fermée | **conditionnel** : fermée ⇒ `None` ; ouverte ⇒ surface complète |

Restent vraies **et deviennent critiques**, donc **MUST** être conservées telles
quelles :

- l'import de `runtime` ne charge ni `transaction_wiring` ni `core.engine` ;
- **une seule construction de `PahoMqttClient` dans tout `src/boilerack`**, au
  site autorisé de `runtime.py` — garantie dérivée de W1 §7.5, et devenue
  critique : c'est elle qui empêche un producteur de contourner la couture du
  §6.1 en construisant son propre client dans `lifecycle` ;
- `build_transaction_surface` exige ses deux dépendances en mot-clé sans défaut ;
- le lecteur seul n'écrit pas ;
- les implémentations de `write` forment une liste fermée.

---

## 12. Barrières normatives de W4-E2

W4-E2 **MUST** livrer des preuves falsifiables pour chacune :

| Réf | Propriété |
|---|---|
| **B1** | autorité **absente** ⇒ aucune composition, `runtime.transaction is None` |
| **B2** | autorité **`false`** ⇒ aucune composition |
| **B3** | autorité **`true`** ⇒ `lifecycle` fournit une `transaction_factory`, `build_runtime` l'applique **avec le client MQTT unique**, la surface est créée **avant** le `ReadSurfaceRunner`, et `Runtime.transaction` n'est pas `None` |
| **B4** | **liste fermée des lieux de DÉCISION** de composer : `lifecycle.py` seul. Que `build_runtime` **applique** une fabrique injectée ne l'y inscrit pas — il n'en choisit jamais l'existence |
| **B5** | un **second lieu de décision** fait échouer B4 |
| **B6** | dans un interpréteur neuf, l'import de **`boilerack.runtime`** *et* celui de **`boilerack.lifecycle`** ne construisent aucune `TransactionSurface`, aucun `VClientCli`, aucun `VclientWriteInvocation`, n'appellent ni `build_production_profile` ni `build_transaction_surface`, n'ouvrent aucune socket, ne lancent aucun processus et n'écrivent rien |
| **B7** | `build_runtime` seul ne compose rien implicitement |
| **B8** | **aucun sous-processus** au simple assemblage |
| **B9** | **aucune écriture** au démarrage |
| **B10** | **un seul** profil de production |
| **B11** | **un seul** écrivain de production |
| **B12** | **une seule** surface transactionnelle |
| **B13** | aucune seconde implémentation de `write` sans lot dédié |
| **B14** | aucun `applied` sans relecture |
| **B15** | aucun retry |
| **B16** | les topics transactionnels **dérivent de la racine** et n'emploient jamais un défaut de bibliothèque |
| **B17** | une clé ou une table inconnue reste refusée |
| **B18** | **une seule construction de `PahoMqttClient`** dans tout `src/boilerack`, au site de `runtime.py` ; la surface transactionnelle reçoit **cette instance** |
| **B19** | le `MqttConfig` transmis à la surface ne diffère de celui de la configuration **que** par `command_topic` et `ack_topic_prefix` ; toute propriété de connexion est préservée à l'identique (§8.4) |

---

## 13. Exigence de sondes — héritée de W4-B

> **Clause.** Une barrière critique n'est **pas** validée parce que son test est
> vert. Elle **MUST** être prouvée par une **sonde fautive** qui la fait rougir,
> exécutée dans un **worktree jetable**, puis **intégralement supprimée**.
>
> La leçon vient de W4-B : deux barrières y étaient vertes tout en laissant
> passer une composition complète par alias et par attribut. Un test vert ne
> prouve rien s'il n'a jamais été vu échouer.

W4-E2 **MUST** sonder au minimum : un **second lieu de décision** de composer ·
composition **sans** autorité · composition avec autorité **`false`** · une
**seconde implémentation** de `write` · une **écriture au démarrage** · une
**seconde construction de `PahoMqttClient`** · une **activation par import**,
visant **`boilerack.lifecycle` autant que `boilerack.runtime`**, puisque c'est
désormais `lifecycle` qui porte la décision — et le dire si elle n'est pas
techniquement sondable.

---

## 14. Configuration — forme normative

| Élément | Décision |
|---|---|
| table | `transaction_surface` |
| clé | `enabled` |
| type | booléen strict |
| défaut | `false` |
| absente | fermé |
| valeur invalide | `ConfigurationError` |
| clé/table inconnue | `ConfigurationError` |
| structure | `TransactionSurfaceConfig` dans **`runtime.py`**, auprès de `RuntimeConfig` (§7.2) |
| membre | `RuntimeConfig.transaction_surface` |

> **Clause.** Aucun paramètre de transport que W4-A garde hors configuration
> utilisateur n'est exposé. En particulier `write_timeout_s` **MUST** rester
> absent des clés utilisateur (W4-A §5, fait F4).
>
> **Clause.** Aucune constante de site : ni hôte, ni port, ni adresse, ni
> chemin, ni unité systemd, ni topic propre à une installation.

**`docs/boilerack.example.toml`** — W4-E2 **MUST** y documenter la clé
**commentée et fermée**, sur le modèle des autres options facultatives :

```toml
# [transaction_surface]
# enabled = false      # autorise la composition de la voie de commande
```

> **Clause.** Le fichier d'exemple **MUST NOT** livrer une configuration qui
> compose la voie d'écriture. Un utilisateur qui copie l'exemple obtient une
> installation **fermée**.

---

## 15. Frontière W4-E2 / W4-F

**W4-E2 PEUT** : implémenter l'autorité · composer sous autorité · dériver les
topics de la racine · éprouver la chaîne complète sous doubles · livrer le
mécanisme **avec l'autorité fermée**.

**W4-E2 NE PEUT PAS** : activer réellement chez l'utilisateur · toucher le Pi ·
lancer `vclient` réel · arrêter le pont historique · neutraliser le superviseur ·
modifier systemd · opérer une bascule one-writer · déclarer Boilerack écrivain
souverain.

**W4-F CONSERVE** : l'activation terrain · l'exclusivité opérationnelle · la
première commande réelle passant par la nouvelle composition · l'observation et
le retour arrière terrain.

> **Test de la frontière.** Livrer un interrupteur fermé n'est pas l'ouvrir.
> Toute proposition de W4-E2 qui rendrait une installation écrivante sans
> intervention humaine explicite viole ce contrat.

---

## 16. Inconnues toujours vivantes

**Non levées, et W4-E1 n'en lève aucune** : I-7, I-8, I-10, I-11, I-12, I-13,
I-15.

**Non caractérisés en écriture, donc toujours interdits** :
`DAEMON_UNREACHABLE` (W4-A §11.6) et `UNKNOWN_COMMAND` (§12.3).

> **Clause.** Aucune de ces inconnues **MUST** être levée par raisonnement
> documentaire. Composer une voie n'observe rien.

---

## 17. Réserves W4-B — hors périmètre

**MIN-1** — `detail` non borné sur le chemin d'écho divergent lorsque le champ
`command` de la réponse est très long.
**MINEUR-V2-1** — la docstring de `VclientWriteInvocation` porte encore l'ancien
ordre d'arguments.

> **Clause.** Ces deux réserves restent **hors W4-E1 et hors W4-E2**. W4-E n'a
> aucune raison fonctionnelle de modifier `adapters/vclient_write.py`, et les y
> embarquer serait artificiel. Elles seront reprises par un lot qui touche ce
> fichier pour un motif réel.

---

## 18. Critères de fermeture de W4-E1

W4-E1 est fermé si, et seulement si :

1. le namespace est arbitré **sans ambiguïté** — §8.4 ;
2. l'autorité d'activation est définie — §7.2 ;
3. le défaut fermé est contractualisé — §7.2, §14 ;
4. l'emplacement de la composition est fixé — §6 ;
5. les barrières de remplacement sont définies — §11, §12 ;
6. les sondes sont exigées — §13 ;
7. la frontière W4-F est explicite — §15 ;
8. **aucun code n'est modifié** ;
9. **aucune question normative nécessaire à W4-E2 ne reste ouverte** — §19.

---

## 19. Conséquences normatives pour W4-E2

Le producteur de W4-E2 doit pouvoir implémenter **sans prendre une seule
décision normative**. Voici ce qu'il sait déjà.

**Fichiers à modifier, et pourquoi :**

| Fichier | Raison |
|---|---|
| `src/boilerack/runtime.py` | déclarer `TransactionSurfaceConfig` (§7.2) ; `RuntimeConfig` porte le membre ; **couture `transaction_factory`** (§6.1) |
| `src/boilerack/config.py` | table et clé dans les listes fermées, sinon `_verifier_cles` les refuserait (§14) |
| `src/boilerack/lifecycle.py` | la **décision** de composer, la fabrique remise à `build_runtime`, la dérivation des topics (§6, §6.1, §8.4) |
| `docs/boilerack.example.toml` | documenter la clé, commentée et fermée (§14) |
| `docs/design/c10-user-interface.md` | étendre la sémantique de `[read_surface].prefix` à la racine commune (§8.4) |
| tests | barrières de remplacement **B1–B19** (§12) et chaîne complète sous doubles |

**Fichiers qui NE doivent PAS changer** : `transaction_wiring.py`, `core/`,
`core/production_profile.py`, `adapters/vclient_write.py`,
`adapters/vclient_cli.py`, `adapters/config.py`, `read_surface/`.

**Où décider** : `lifecycle.py`. **Quand** : si et seulement si
`config.transaction_surface.enabled` est vrai. **Comment** : `lifecycle`
construit une `transaction_factory` et la remet à `build_runtime` (§6.1) ; la
fabrique reçoit le **client MQTT unique** et l'horloge, et assemble
`VclientWriteInvocation(config.vclient)`, `VClientCli(config.vclient,
SubprocessRunner(), invocation=…)`, `build_production_profile()`, puis
`build_transaction_surface(…)` avec un `MqttConfig` **dérivé** dont seuls
`command_topic` et `ack_topic_prefix` changent (§8.4). **Quels topics** : §8.4.
**Quels tests remplacer** : §11. **Ce qui reste interdit** : §4, §15, §16, §17.

---

## 20. Fermeture

W4-E1 ne compose rien, n'active rien et n'observe rien. Il rend quatre décisions
et une seule dette est levée : celle que C7 §14 avait inscrite en attendant
qu'une composition root existe.

Ce qu'il change réellement, c'est la **nature de la garantie de fermeture**.
Avant W4-B et W4-D, la production était fermée par l'absence de pièces. Depuis,
elle l'est par abstention. Après W4-E2, elle le sera par **autorité explicite,
fermée par défaut, et vérifiée par des barrières sondées**.

Une abstention se perd par oubli ; une autorité se lit dans un fichier.

**W4-E2 n'est pas ouvert par ce document. W4-F reste terrain.**
