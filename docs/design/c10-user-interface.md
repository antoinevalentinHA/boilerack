# C10 — Interface utilisateur : configuration et point d'entrée installé

Document **contractuel**, écrit avant toute implémentation. Il fixe la frontière
publique de Boilerack pour un utilisateur : ce qu'il installe, ce qu'il écrit,
ce qu'il lance, et ce qu'il obtient. Aucun code n'existe encore.

Ce qui est écrit ici devient une **surface de compatibilité** au même titre que
les topics MQTT de C7 : les noms de clés, le nom de la variable
d'environnement, les valeurs par défaut et les codes de sortie ne pourront plus
changer sans casser des installations.

## Objet

> Permettre à un utilisateur d'installer Boilerack puis de le lancer avec une
> configuration **explicite**, **validée**, et **sans aucun secret dans le
> fichier de configuration**.

Quatre choses distinctes, qu'il ne faut pas confondre :

| | Où | Durée de vie |
|---|---|---|
| **Configuration durable** | fichier TOML | celle de l'installation |
| **Secret** | variable d'environnement | celle du processus |
| **Options de lancement** | ligne de commande | celle de la session |
| **Comportement d'exécution** | ni l'un ni l'autre — il est contractuel | fixé par ce document |

## Ce que C10 n'est pas

C10 ne change **rien** au comportement du pont. Il ne touche ni la surface MQTT
de lecture (C7), ni la composition (C8), ni le cycle de vie (C9). Il ne fait
qu'ouvrir une porte d'entrée devant ce qui existe déjà.

## Lancement

Deux chemins publics, **strictement équivalents** :

```
boilerack --config /chemin/boilerack.toml
python -m boilerack --config /chemin/boilerack.toml
```

Les deux appellent **la même fonction `main()`**. Le module `__main__.py` ne
porte aucune logique propre : il délègue et projette le résultat. Aucune
divergence de comportement entre les deux formes n'est admise, et un test devra
l'établir.

Pourquoi les deux, plutôt qu'un seul : la commande installée est la plus
naturelle, mais elle n'est joignable que si le `bin`/`Scripts` de
l'environnement est dans le `PATH` — ce qui n'est pas acquis sur un Raspberry
Pi avec un environnement virtuel non activé. `python -m boilerack` fonctionne
alors sans rien configurer. Le coût de ce second chemin est nul dès lors que
`__main__.py` ne duplique aucune logique.

## Options de ligne de commande

### `--config CHEMIN`

**Obligatoire.** Chemin du fichier TOML.

**Aucun chemin implicite n'est introduit** : ni `/etc/boilerack.toml`, ni
`~/.config/...`, ni le répertoire courant. Boilerack ne cherche pas sa
configuration, il la reçoit. Une découverte silencieuse rendrait le
comportement dépendant du répertoire de lancement et du compte utilisateur,
c'est-à-dire imprévisible pour un service.

- option absente → **erreur d'usage**, code `2` ;
- fichier absent, illisible ou invalide → **erreur de configuration**, code `2`.

### `--log-level NIVEAU`

Optionnel. Défaut : `INFO`.

Valeurs acceptées, et **elles seules** :

```
DEBUG  INFO  WARNING  ERROR  CRITICAL
```

Toute autre valeur est une erreur d'usage. Le jeu est fermé délibérément :
`logging` accepte aussi des entiers arbitraires et des niveaux personnalisés,
ce qui n'a aucun sens ici et n'ouvrirait qu'une surface à maintenir.

`--log-level` est **exclusivement** une option de ligne de commande :

- il n'existe **aucune** clé `log_level` dans le TOML ;
- il n'existe **aucune** variable d'environnement correspondante ;
- il n'affecte que la session en cours.

C'est un réglage de diagnostic, pas une propriété durable de l'installation.
L'exposer ailleurs créerait une précédence entre sources pour un unique
paramètre — un coût sans contrepartie.

## Fichier de configuration

Format **TOML**. Trois tables, **et aucune autre** :

```toml
[mqtt]
[vclient]
[read_surface]
```

Le schéma est **fermé** : toute table inconnue et toute clé inconnue sont
**refusées**. Cette strictesse est légitime parce que Boilerack possède
intégralement son schéma — il n'hérite d'aucun format tiers et ne partage son
fichier avec personne. Elle transforme une faute de frappe silencieuse, qui
laisserait un réglage sans effet, en une erreur immédiate et nommée.

TOML est retenu parce qu'il est le seul format à cumuler : disponibilité
**stdlib** sur toutes les versions supportées (`tomllib`, Python ≥ 3.11, et
`requires-python = ">=3.11"`), types natifs distincts pour entiers, flottants et
booléens, commentaires — le fichier est destiné à être édité à la main —, et
absence de toute dépendance nouvelle. YAML aurait introduit la **deuxième**
dépendance d'exécution du projet ; JSON n'admet pas de commentaires.

### Les 13 clés publiques

| Table | Clé | Type TOML | Obligatoire | Défaut |
|---|---|---|---|---|
| `[mqtt]` | `host` | string | **oui** | — |
| | `port` | integer | non | `1883` |
| | `client_id` | string | non | `"boilerack"` |
| | `keepalive` | integer | non | `60` |
| | `username` | string | non | absent |
| | `tls` | boolean | non | `false` |
| `[vclient]` | `executable` | string | **oui** | — |
| | `host` | string | non | absent |
| | `port` | integer | non | absent |
| | `read_timeout_s` | integer ou float | non | `5.0` |
| `[read_surface]` | `prefix` | string | non | `"boiler"` |
| | `snapshot_period_s` | integer | non | `30` |
| | `heartbeat_period_s` | integer | non | `30` |

**6 + 4 + 3 = 13 clés.** Deux seulement sont obligatoires : `mqtt.host` et
`vclient.executable`. Ce sont les deux valeurs de site que le dépôt ne peut pas
deviner, et il n'en invente aucun défaut.

Tous les défauts ci-dessus sont **exactement** ceux que portent déjà les
structures internes. C10 n'en introduit aucun et n'en modifie aucun : il les
rend publics, donc contractuels.

## Table `[mqtt]`

### `host`
Broker MQTT. Chaîne non vide. **Obligatoire.**

### `port`
Entier, `1..65535`. Défaut `1883`.

### `client_id`
Identité MQTT du pont. Chaîne non vide. Défaut `"boilerack"`.

> **À savoir.** Deux instances de Boilerack connectées au même broker avec le
> même `client_id` se déconnectent mutuellement en boucle : le protocole MQTT
> impose l'unicité. Le défaut convient à une installation unique ; toute
> seconde instance **doit** en changer.

### `keepalive`
Entier strictement positif, en **secondes**. Défaut `60`.

### `username`
Chaîne non vide si présente. Absente par défaut.

`username` n'est **pas** un secret : c'est un identifiant, au même titre qu'un
nom d'hôte. Il appartient donc au fichier, avec le reste de la configuration
durable. La symétrie apparente avec `password` est trompeuse et n'est pas
retenue.

`username` et le mot de passe sont **indépendants** : aucun des deux n'en
exige l'autre. C'est le comportement de l'adaptateur existant, qui n'appelle
`username_pw_set` que si `username` est fourni, et transmet alors le mot de
passe tel quel, y compris absent. Le contrat n'ajoute aucune contrainte croisée.

### `tls`
Booléen. Défaut `false`.

`true` active le mécanisme TLS **par défaut** du client MQTT, c'est-à-dire la
vérification contre le magasin de certificats du système. Rien de plus :

- aucune autorité de certification personnalisée ;
- aucun certificat client ;
- aucun réglage de vérification du nom d'hôte ;
- **aucun nouveau réglage TLS n'est introduit par C10.**

Le contrat décrit ici exactement ce que le code fait aujourd'hui, ni plus ni
moins. Exposer davantage serait promettre ce qui n'existe pas.

### Clés explicitement refusées dans `[mqtt]`

| Clé | Motif du refus |
|---|---|
| `password` | **secret** — voir la section suivante ; jamais dans un fichier |
| `command_topic` | hors surface utilisateur C10 |
| `ack_topic_prefix` | hors surface utilisateur C10 |

Ces trois clés doivent produire une erreur **nommée**, et non le message
générique de clé inconnue : l'utilisateur qui les écrit a une intention
précise, et mérite d'apprendre pourquoi elle est refusée.

## Le secret

Un seul secret existe dans tout Boilerack : le mot de passe MQTT.

Il est fourni **exclusivement** par la variable d'environnement :

```
BOILERACK_MQTT_PASSWORD
```

### Choix du nom

Le dépôt ne comportait, avant ce contrat, **aucune** variable d'environnement,
aucune constante en majuscules exposée, et donc aucune convention préexistante
à respecter ou à contredire — vérifié par recherche exhaustive. Le nom est donc
choisi librement, mais une seule fois.

`BOILERACK_MQTT_PASSWORD` est retenu pour trois raisons : le préfixe reprend le
**nom de distribution et de paquet** déjà public (`boilerack`), ce qui évite
toute collision avec un autre logiciel sur la même machine ; le segment
intermédiaire nomme le sous-système, ce qui laisse la place à un éventuel futur
secret sans réorganisation ; et la forme `MAJUSCULES_AVEC_SOULIGNES` est la
convention universelle des variables d'environnement.

Ce nom devient **surface publique** dès sa publication.

### Sémantique

- variable absente → mot de passe `None`, connexion sans mot de passe ;
- variable présente → sa valeur est le mot de passe, telle quelle, sans
  interprétation ni décodage ;
- **fait à connaître** : dans l'adaptateur actuel, le mot de passe n'est
  transmis au client MQTT que lorsque `mqtt.username` est défini.
  `BOILERACK_MQTT_PASSWORD` présente **sans** `mqtt.username` n'a donc aucun
  effet sur l'authentification. C10 ne transforme pas cette situation en erreur
  de configuration et n'introduit **aucune** contrainte croisée : le contrat se
  borne à l'énoncer, et une propriété de caractérisation l'épinglera ;
- **aucune** valeur TOML concurrente : `[mqtt].password` est refusé ;
- **aucune** précédence à arbitrer, puisqu'il n'y a qu'une source ;
- **aucun** équivalent en ligne de commande — un mot de passe en argument
  serait visible dans la table des processus et dans l'historique du shell ;
- sa valeur n'est **jamais** affichée, ni journalisée, ni incluse dans un
  message d'erreur ;
- le masquage existant dans la représentation des objets de configuration est
  préservé, et reste transitif.

### Ce que C10 ne lit pas dans l'environnement

Boilerack lit **une** variable, celle qu'il possède explicitement. Il ne traite
pas l'environnement du processus comme un document de configuration :

- aucun balayage des variables ;
- aucun refus de variable inconnue — l'environnement ne lui appartient pas ;
- aucun espace de noms de configuration général ;
- aucune possibilité pour l'environnement de surcharger une clé TOML ;
- aucun chargeur de fichier `.env`. Le processus hérite de son environnement
  par les moyens habituels du système.

Les deux sources sont donc **disjointes** : le fichier porte tout sauf le
secret, l'environnement porte le secret et rien d'autre. Il n'y a aucune
cascade, et donc aucune question « qui gagne ? » à laquelle répondre.

## Table `[vclient]`

### `executable`
Chemin ou nom de l'exécutable `vclient`. Chaîne non vide. **Obligatoire.**

Son existence sur le disque n'est **pas** vérifiée pendant la validation : ce
serait une vérification d'infrastructure, et elle échouerait pour de mauvaises
raisons (montage non encore disponible, `PATH` différent au lancement du
service).

### `host`
Hôte du démon `vcontrold`. Chaîne non vide si présente. Absente par défaut.

### `port`
Entier `1..65535`. Absent par défaut.

`host` et `port` sont **indépendants** : ni l'un ni l'autre n'exige l'autre.
C'est le comportement de l'adaptateur, qui ajoute `-h` et `-p` à la ligne de
commande séparément, chacun seulement s'il est fourni. Omettre les deux laisse
`vclient` employer ses propres défauts. Le contrat n'ajoute aucune contrainte
que le code n'impose pas.

### `read_timeout_s`
Durée en **secondes**, finie et strictement positive. Défaut `5.0`.

Le type TOML accepté est **integer ou float** : `5` et `5.0` sont tous deux
valides et signifient la même chose. La valeur est convertie en `float`. Cette
tolérance est justifiée — un utilisateur écrira naturellement `10` plutôt que
`10.0` pour une durée ronde — et sans ambiguïté, TOML distinguant les deux
types à la lecture.

### Clé non exposée

`write_timeout_s` n'est pas exposée : elle n'a **aucun consommateur** dans le
code. Voir la section « Champs non exposés ».

## Table `[read_surface]`

### `prefix`
Racine de tous les topics MQTT de lecture. Défaut `"boiler"`. Validé selon les
règles de topic déjà établies par C7 §3.3 — validation existante, non
redéfinie ici.

> **Contrat important.** Modifier cette valeur modifie **l'ensemble des topics
> publics** que Boilerack publie. Ce n'est pas un réglage cosmétique : tout
> consommateur en aval — tableau de bord, automatisation, enregistreur — doit
> être mis à jour en conséquence.

### `snapshot_period_s`
Entier strictement positif, en **secondes**. Défaut `30`.

Une contrainte supplémentaire existe déjà et n'est pas relaxée : la période
doit rester **inférieure ou égale au plus petit `fresh_max_s`** des mesures
déclarées. Cette borne est **dynamique** : elle dépend des mesures réellement
injectées, et vaut 90 s avec la surface v1 **d'aujourd'hui**.

Ce nombre est une **observation**, pas une constante du contrat. C10 ne doit ni
le recopier, ni recalculer `min(fresh_max_s)` pour son propre compte : ce serait
dupliquer une règle métier dont l'autorité est ailleurs, et la faire diverger au
premier changement de la surface de lecture. Voir « Frontière de la validation
dynamique ».

### `heartbeat_period_s`
Entier strictement positif, en **secondes**. Défaut `30`.

**`0` désactive le battement.**

#### Pourquoi cette convention, et pas une autre

Le problème est réel et naît du passage de Python à TOML : le runtime représente
la désactivation par `None`, or **TOML n'a pas de valeur nulle**. Il faut donc
une convention explicite. Quatre options ont été examinées.

| Option | Verdict |
|---|---|
| **`0` signifie désactivé** | **retenue** |
| Omettre la clé | insuffisant : l'absence vaut déjà « défaut 30 », elle ne peut pas aussi vouloir dire « désactivé » |
| Clé booléenne séparée (`heartbeat_enabled`) | rejetée : deux clés pour un concept, et un état contradictoire possible — `enabled = false` avec `period = 30` |
| Type mixte (`false` ou un entier) | rejetée : mélanger booléen et entier sur une même clé contredit le typage strict retenu par ailleurs |

`0` est une valeur spéciale, ce qui n'est jamais élégant, mais c'est la seule
option qui reste dans un type unique, sans clé supplémentaire et sans état
contradictoire. Elle est **sans ambiguïté** : `0` seconde n'a aucune
interprétation utile comme période, et la structure interne le refuse déjà
explicitement.

**Mécanique exacte, à ne pas confondre.** La projection `0 → None` appartient au
chargeur de configuration de C10. La structure interne, elle, continue de
refuser `0` : elle ne reçoit jamais cette valeur, elle reçoit `None`. Aucune
règle existante n'est modifiée.

**Ordre impératif des deux étapes.** Le type est validé **d'abord**, la valeur
est interprétée **ensuite**. Seul un **entier TOML exact** `0` est projeté vers
`None`.

Conséquence directe :

```toml
heartbeat_period_s = false
```

est **refusé** comme erreur de type. Il n'est **jamais** interprété comme une
désactivation.

Le piège est réel et tient à Python, pas à TOML : `bool` y est une sous-classe
de `int`, et `False == 0` est vrai. Une projection écrite comme
`if valeur == 0: valeur = None` **avant** la validation de type accepterait donc
silencieusement `false` et désactiverait le battement sans que l'utilisateur
l'ait demandé. La comparaison à zéro ne doit jamais précéder la vérification du
type.

## Champs non exposés

| Champ | Motif |
|---|---|
| `MqttConfig.command_topic` | **mort** — aucun consommateur dans le code |
| `MqttConfig.ack_topic_prefix` | **mort dans le chemin d'exécution** — le noyau transactionnel a son propre paramètre, jamais alimenté par cette valeur, et il n'est pas câblé |
| `VclientConfig.write_timeout_s` | **mort** — aucun consommateur |
| `RuntimeConfig.specs` | **surface interne fermée** — la table des huit mesures est un contrat C7, pas un réglage |

Leur présence dans une structure interne **ne constitue pas** un engagement
d'interface publique. Exposer un champ parce qu'il existe reviendrait à
publier des boutons qui ne font rien, et à s'engager à les maintenir.

**C10 ne les supprime pas.** Retirer un champ mort toucherait les lots C3 et C4
et anticiperait la surface d'écriture ; c'est une dette identifiée, datée, et
laissée à un lot ultérieur.

## Validation

C10 valide la **configuration**, jamais l'infrastructure.

### Ce qui est vérifié, avant tout démarrage

1. le fichier existe ;
2. le fichier est lisible ;
3. le TOML est syntaxiquement valide ;
4. les tables sont connues ;
5. les clés sont connues, dans chaque table ;
6. les types sont exacts, au sens TOML ;
7. les clés obligatoires sont présentes ;
8. les contraintes de valeur sont respectées ;
9. aucun secret n'est présent dans le fichier ;
10. `RuntimeConfig` se construit — ce qui déclenche les validations portées par
    les structures de configuration elles-mêmes ;
11. les validations **dépendant de la surface de lecture** passent, notamment la
    borne dynamique de `snapshot_period_s` — voir ci-dessous.

### Ce qui n'est jamais fait pour valider

- ouvrir une connexion MQTT ;
- résoudre activement le nom d'hôte du broker ;
- lancer `vclient` ;
- interroger `vcontrold` ;
- toucher à la chaudière ;
- vérifier l'existence de l'exécutable sur le disque.

Ce n'est pas une précaution de style : c'est la préservation d'un invariant
établi et testé par C8 — construire n'ouvre aucune socket et ne lance aucun
processus. Mélanger validation de saisie et test de connectivité rendrait le
démarrage dépendant du réseau et confondrait une faute de frappe avec une panne
d'infrastructure.

### Où survient chaque validation

Trois étages, qu'il faut distinguer parce que le message et le moment diffèrent :

| Étage | Ce qu'il vérifie | Quand |
|---|---|---|
| Chargeur C10 | forme du fichier, tables, clés, types TOML, clés interdites | à la lecture |
| Structures de configuration | valeurs : ports, durées, chaînes non vides, topic valide | à la construction |
| Autorité de la surface de lecture | borne dynamique de `snapshot_period_s`, contre les mesures réellement déclarées | avant l'entrée dans `run_lifecycle()` |

Les trois surviennent **avant que quoi que ce soit ne démarre**, et les trois
produisent une erreur de configuration lisible : code `2`, sans traceback, avec
la table et la clé fautives nommées. Le chargeur est responsable de cette mise
en contexte, y compris lorsque l'erreur remonte des deux étages suivants.

### Frontière de la validation dynamique

Le troisième étage mérite d'être spécifié, parce qu'il est le seul dont
l'autorité ne réside pas dans le chargeur.

**Exigence normative.** Toute validation dépendant de la construction statique
de la surface de lecture — au premier rang, la borne dynamique de
`snapshot_period_s` — à lieu **avant l'entrée dans `run_lifecycle()`**, et
repose sur **la même autorité métier que celle appliquée par le publieur**. Une
configuration qui échoue à ce stade reste une **erreur de configuration
utilisateur** : code `2`, aucun traceback, `[read_surface].snapshot_period_s`
identifiable.

**Interdits.** Aucun des quatre contournements suivants n'est admis :

- recopier la valeur `90` dans le chargeur ;
- recalculer `min(fresh_max_s)` pour le compte de C10 ;
- intercepter globalement les `ValueError` remontant de `run_lifecycle()` ;
- transformer une panne d'exécution en code `2`.

Les deux premiers dupliqueraient une règle métier et la feraient diverger ; les
deux suivants confondraient une saisie fautive avec une panne.

**Ce que le contrat ne fixe pas.** Il fixe la **propriété** — validation avant
`run_lifecycle()`, autorité unique — et **non la mécanique**. En particulier, il
n'impose **pas** de construire le runtime deux fois. La caractérisation C10
devra déterminer la couture minimale, en comparant au moins :

1. l'extraction ou la réutilisation d'une validation **pure** partagée avec le
   publieur ;
2. une autre couture déjà existante offrant la même autorité ;
3. la préconstruction du runtime, **uniquement** si aucune solution plus sobre
   n'existe.

Cette comparaison appartient à l'étape suivante, pas à ce contrat.

### Types stricts

Les types annoncés sont ceux de **TOML**, pas ceux de l'héritage Python.

Point d'attention, déjà traité ailleurs dans le dépôt : en Python, `bool` est
une sous-classe de `int`. Une vérification naïve par `isinstance(valeur, int)`
accepterait donc `true` comme numéro de port ou comme période.

**Une clé déclarée entière refuse un booléen.** Même rigueur pour les
flottants. Le dépôt applique déjà cette règle dans ses structures de
configuration ; le chargeur C10 doit l'appliquer au même titre, et un test doit
la verrouiller pour **chaque** clé numérique.

## Erreurs de configuration

Une seule catégorie d'erreur utilisateur. Aucune hiérarchie d'exceptions :
elle n'aurait aucun consommateur, et le point d'entrée est le seul appelant.

Un message d'erreur de configuration :

- est **lisible** — il s'adresse à une personne qui édite un fichier, pas à un
  développeur qui lit une pile d'appels ;
- nomme le **fichier** lorsque c'est pertinent ;
- nomme la **table et la clé** fautives ;
- ne contient **jamais** le mot de passe ;
- ne produit **aucun traceback** : la faute est dans le fichier, une pile
  d'appels désignerait le code et n'apprendrait rien.

Forme visée, à titre indicatif — le contrat fixe la substance, pas la
ponctuation :

```
boilerack: configuration invalide: [mqtt].host est obligatoire
boilerack: configuration invalide: cle inconnue [mqtt].hots
boilerack: configuration invalide: [mqtt].password est interdit, utilisez BOILERACK_MQTT_PASSWORD
```

Code de sortie : **`2`**.

## Erreurs d'exécution

Une fois `RuntimeConfig` construit et le runtime lancé, une exception n'est plus
une erreur de l'utilisateur : c'est une panne du programme ou de son
environnement. Elle est traitée comme telle.

- **aucune interception globale** d'`Exception` au point d'entrée ;
- le **traceback natif** est conservé — c'est le meilleur outil de diagnostic
  disponible, et l'affichage des groupes d'exceptions par Python est déjà
  excellent ;
- le code de sortie est celui de Python, soit **`1`**.

Embellir cette sortie ferait perdre de l'information sans rien apporter.

## Codes de sortie

| Code | Situation |
|---|---|
| `0` | arrêt normal, ou arrêt demandé par `SIGTERM` |
| `130` | arrêt demandé par `SIGINT` (Ctrl-C) |
| `2` | erreur d'usage de la ligne de commande, ou erreur de configuration |
| `1` | panne d'exécution non interceptée, comportement natif de Python |

**Répartition des responsabilités, à ne pas confondre.** C9 produit un
**résultat logique** — un entier rendu par une fonction, `0` ou `130`. C10 est
le seul responsable de sa **projection en code de sortie de processus**. C9 ne
sort jamais du processus ; C10 ne décide jamais de la sémantique de l'arrêt.

`2` est retenu pour les erreurs d'usage et de configuration parce que c'est la
convention Unix, et surtout parce que l'analyseur d'arguments de la
bibliothèque standard sort **déjà** en `2` : retenir autre chose créerait une
incohérence entre « mauvaise option » et « mauvais fichier ».

## Convention de `main()`

```
main(argv: Sequence[str] | None = None) -> int
```

`main` **rend** un entier ; elle ne quitte pas le processus.

Ce choix n'est pas arbitraire, il découle du mécanisme réel de chacun des trois
appelants — vérifié, non supposé :

| Appelant | Ce qu'il fait |
|---|---|
| Commande installée | le script généré exécute `sys.exit(main())` — c'est le gabarit standard de l'écosystème |
| `python -m boilerack` | `__main__.py` doit projeter lui-même : `raise SystemExit(main())` |
| Tests | `assert main([...]) == 0` — direct, sans capture d'exception |

Une convention ou `main()` lèverait elle-même `SystemExit` fonctionnerait pour
les deux premiers, mais imposerait `pytest.raises(SystemExit)` à chaque test, ce
qui rend l'assertion sur le code plus indirecte. La convention « rendre un
entier » sert les trois appelants sans concession.

Le paramètre `argv` optionnel permet de tester sans manipuler `sys.argv`. Absent,
il vaut `sys.argv[1:]`.

**Nuance honnête à documenter, plutôt qu'à masquer.** L'analyseur d'arguments de
la bibliothèque standard lève `SystemExit(2)` depuis l'intérieur de `main()`
pour une option invalide, et `SystemExit(0)` pour `--help`. `main()` a donc deux
issues : un entier rendu dans le cas normal, et un `SystemExit` qui la traverse
pour l'usage et l'aide. Les deux produisent le même code de processus par les
deux chemins de lancement. Intercepter ces `SystemExit` pour uniformiser
obligerait à traiter `--help` comme une erreur : le remède serait pire.

Un test devra couvrir explicitement les deux issues.

## Journalisation

C10 est le **propriétaire** de la configuration de journalisation du processus,
et le seul. C9 l'a explicitement refusée, parce qu'une fonction appelée
programmatiquement n'a pas à imposer sa politique au processus hôte.

- **aucune configuration à l'import** — importer un module de Boilerack, y
  compris celui de la ligne de commande, ne touche à rien ;
- **chaque invocation de `main()` configure la journalisation du processus
  qu'elle possède**, conformément au `--log-level` de cette invocation ;
- canal : **`stderr`** — c'est le canal des diagnostics ; `stdout` reste libre ;
- niveau par défaut : **`INFO`**, piloté par `--log-level` ;
- chaque ligne porte un **horodatage**, un **niveau**, le **nom du logger** et
  le **message** ;
- **aucune couleur, aucune dépendance, aucun format structuré.**

L'horodatage n'est pas décoratif : un pont qui tourne en continu produit des
lignes qu'il faut pouvoir situer, et un lancement manuel n'en ajoute aucun.

**Sémantique sur appels répétés.** « Une seule fois » serait ambigu, et pire :
faux avec la mécanique par défaut de la bibliothèque standard, dont la
configuration simplifiée **ne fait rien** si la racine possède déjà un
gestionnaire. Deux appels successifs de `main()` avec des niveaux différents
laisseraient alors le premier niveau en place — silencieusement.

Le contrat exige donc l'inverse : **le niveau demandé est effectivement
appliqué à chaque invocation**. `main()` prend possession de la configuration de
journalisation du processus ; c'est légitime, puisqu'elle en est la racine. Une
implémentation forçant la reconfiguration est **autorisée et probablement
adaptée**, mais le contrat fixe la propriété observable, pas la ligne de code :
toute solution équivalente de la bibliothèque standard convient.

Conséquences, toutes vérifiables :

- importer le module de ligne de commande ne touche jamais à la journalisation ;
- appeler `main()` en prend possession ;
- deux appels successifs avec des niveaux différents reflètent le **second**.

Le contrat fixe la **sémantique** du format — quelles informations, dans quel
ordre — et non une chaîne de format caractère par caractère : figer celle-ci
n'apporterait rien et interdirait tout ajustement de lisibilité.

État actuel, pour mémoire : deux modules journalisent, pour douze appels — dix
avertissements, une information, une exception. Sans configuration, seuls les
avertissements sont visibles et la confirmation de connexion ne l'est pas. Le
défaut `INFO` la rend visible, sans bavardage.

## Fichier d'exemple

C10 livrera un exemple de configuration, **sans aucun secret**.

Il doit : contenir les trois tables ; distinguer visiblement les deux clés
obligatoires des onze optionnelles ; montrer ou commenter les valeurs par
défaut ; expliquer que le mot de passe se fournit par `BOILERACK_MQTT_PASSWORD`
et **nulle part ailleurs**.

Il ne doit **jamais** présenter une clé `password` — même commentée, même avec
une valeur manifestement fictive. Une ligne commentée se décommente ; l'exemple
ne doit pas contenir le geste dangereux, il doit contenir son alternative.

Nom proposé : `docs/boilerack.example.toml`. Le placer sous `docs/` plutôt qu'à
la racine évite qu'il soit pris pour une configuration active du dépôt.

## README

Le lot devra rendre le chemin utilisateur compréhensible depuis le README, en
cinq étapes : installation ; création du fichier TOML ; fourniture éventuelle du
mot de passe ; lancement ; signification des codes de sortie.

Le README **renvoie** au présent contrat, il ne le duplique pas. Deux copies
d'une même spécification divergent toujours.

## Packaging

### Commande installée

```toml
[project.scripts]
boilerack = "boilerack.cli:main"
```

Forme correcte pour le système de construction en place. Ce sera la
**première** modification de `pyproject.toml` depuis le lot des adaptateurs
réels, et elle n'ajoute **aucune dépendance**.

### Module exécutable

`src/boilerack/__main__.py`, réduit à la délégation :

```
from boilerack.cli import main
raise SystemExit(main())
```

Aucune logique propre, aucune duplication. Un test devra vérifier que ce fichier
ne contient rien d'autre.

## Absence d'entrées-sorties d'infrastructure

Le chargement et la validation **peuvent** : ouvrir et lire le fichier TOML ;
lire la variable d'environnement du mot de passe.

Ils ne **peuvent pas** : ouvrir une socket ; se connecter à un broker ; lancer
un sous-processus ; exécuter `vclient`.

La construction de `RuntimeConfig` reste hors de toute entrée-sortie
d'infrastructure. Un test devra le prouver par sabotage, comme les lots C8 et C9
l'ont fait pour la construction du runtime.

## Hors périmètre

Confirmés hors C10, aucune nécessité démontrée :

unité systemd · Docker · installateur · module complémentaire Home Assistant ·
HACS · supervision externe · reprise ou reconnexion · nouvelle tentative
`vclient` · écriture chaudière · configuration métier des commandes ·
découverte automatique · assistant interactif · interface web · migration de
configuration · gestionnaire de secrets · paquet Debian · **tout nouveau
réglage TLS** · **suppression des champs morts**.

## Propriétés à verrouiller

Le lot d'implémentation devra prouver, au minimum, les propriétés suivantes.
Les noms de tests ne sont pas fixés ici ; les propriétés le sont.

### Chargement et schéma

- une configuration minimale — les deux clés obligatoires seules — produit un
  `RuntimeConfig` valide ;
- chaque valeur par défaut non fournie vaut **exactement** celle annoncée ;
- table inconnue refusée ; clé inconnue refusée, dans chacune des trois tables ;
- TOML malformé refusé ; fichier absent refusé ; fichier illisible refusé ;
- chaque clé obligatoire absente est refusée, en nommant la clé.

### Types

- pour **chaque** clé entière, un booléen est refusé ;
- pour **chaque** clé entière, un flottant est refusé ;
- `read_timeout_s` accepte un entier **et** un flottant, refuse un booléen ;
- `tls` refuse tout ce qui n'est pas un booléen ;
- chaque clé chaîne refuse les autres types.

### Secret

- `[mqtt].password` dans le fichier est refusé, avec un message qui **nomme**
  la variable d'environnement à utiliser ;
- variable présente → le mot de passe est celui-là ;
- variable absente → mot de passe `None`, et le chargement réussit ;
- **aucune fuite** : le secret n'apparaît dans aucun message d'erreur, dans
  aucune représentation d'objet, dans aucune ligne journalisée ;
- aucune autre variable d'environnement n'est lue ;
- **caractérisation** : variable présente **sans** `mqtt.username` — le
  chargement réussit, aucune erreur n'est levée, et le mot de passe n'atteint
  pas le client MQTT. Cette propriété épingle le comportement de l'adaptateur ;
  elle ne promet rien de plus et n'impose aucune contrainte croisée.

### Battement

- `heartbeat_period_s = 0` désactive le battement ;
- `heartbeat_period_s` absent vaut `30`, battement actif ;
- une valeur négative est refusée ;
- la structure interne ne reçoit **jamais** `0` ;
- **`heartbeat_period_s = false` est refusé comme erreur de type**, et n'est en
  aucun cas interprété comme une désactivation.

### Surface de lecture

- avec la surface v1 **actuelle**, `snapshot_period_s = 91` est **refusé avant
  le démarrage du cycle de vie** : code `2`,
  `[read_surface].snapshot_period_s` identifiable, aucun traceback, **aucune
  connexion**, **aucun sous-processus**, et le runner n'est **jamais** entre ;
- une valeur à la borne exacte est acceptée ;
- la validation utilise l'autorité de la surface de lecture, jamais une valeur
  recopiée.

> `91` est une valeur de **caractérisation de la surface v1 d'aujourd'hui**, pas
> une constante à inscrire dans C10. Si la surface change, le test change avec
> elle ; le chargeur, lui, ne change pas.

### Ligne de commande

- `--config` absent → code `2` ;
- `--config` pointant vers un fichier absent → code `2` ;
- `--log-level` accepte les cinq valeurs, et **rien d'autre** ;
- `--log-level` absent → `INFO` ;
- `--help` sort en `0` ;
- une option inconnue sort en `2`.

### Codes de sortie et cycle de vie

- résultat logique `0` projeté en code `0` ;
- résultat logique `130` projeté en code `130` ;
- erreur de configuration → code `2`, **sans traceback** ;
- panne d'exécution → l'exception traverse, **traceback conservé**, code `1` ;
- l'identité de l'exception d'origine est préservée.

### Journalisation

- aucune configuration de journalisation lors du **seul import** ;
- `main()` configure la journalisation sur `stderr` ;
- le niveau demandé est effectivement appliqué ;
- **deux appels successifs de `main()` avec des niveaux différents reflètent le
  second niveau**, et non le premier.

### Frontières

- le chargement n'ouvre **aucune socket** et ne lance **aucun sous-processus**,
  prouvé par sabotage ;
- `__main__.py` ne contient aucune logique propre ;
- les deux chemins de lancement produisent le **même** comportement.

### Mutations discriminantes

Le lot devra tuer au minimum :

| # | Mutation | Ce qu'elle casse |
|---|---|---|
| 1 | Clé inconnue acceptée silencieusement | une faute de frappe reste sans effet et sans message |
| 2 | Table inconnue acceptée | idem, à l'échelle d'une section |
| 3 | Un défaut change de valeur | rupture de contrat invisible |
| 4 | Une clé obligatoire cesse de l'être | démarrage avec une configuration incomplète |
| 5 | Le mot de passe est lu depuis le fichier | secret versionnable |
| 6 | Le mot de passe apparaît dans un message d'erreur | fuite de secret |
| 7 | `isinstance(x, int)` sans exclusion du booléen | `true` accepté comme port |
| 8 | `heartbeat_period_s = 0` transmis tel quel | erreur interne au lieu d'une désactivation |
| 9 | Erreur de configuration rendue en `1` | indistinguable d'une panne |
| 10 | `130` projeté en `0` | un Ctrl-C passerait pour un arrêt normal |
| 11 | Interception globale d'`Exception` au point d'entrée | traceback perdu, diagnostic impossible |
| 12 | Journalisation configurée à l'import | contamination du processus hôte |
| 13 | `--log-level` accepte n'importe quelle chaîne | surface non contractuelle |
| 14 | `__main__.py` porte de la logique | divergence entre les deux chemins |
| 15 | La validation dynamique est omise : la valeur hors borne atteint `run_lifecycle()` | traceback et code `1` là où l'utilisateur attend une erreur de configuration en code `2` |
| 16 | `heartbeat_period_s = false` désactive silencieusement le battement | comparaison à zéro placée avant la validation de type ; `False == 0` |
| 17 | Le second appel de `main()` conserve le niveau du premier | `--log-level` sans effet dès la deuxième invocation dans un même processus |

## Fichiers prévisionnels

**Nouveaux** — un module de chargement de configuration ; un module de ligne de
commande ; `src/boilerack/__main__.py` ; leurs fichiers de tests ; un exemple
TOML ; le présent document.

**Modifiés** — `pyproject.toml`, pour la seule entrée `[project.scripts]` ;
`README.md`, pour le chemin utilisateur ; éventuellement un renvoi dans le
document C9.

**Non modifiés** — tout `adapters/`, `read_surface/`, `transport/`, `core/`,
`runtime.py`, `lifecycle.py`, `clock.py`. **Aucune dépendance ajoutée.**

## Ce que ce contrat n'a pas tranché

Deux points sont volontairement laissés à l'étape de caractérisation, parce
qu'ils dépendent de faits à établir plutôt que de décisions à prendre :

1. **La forme exacte du message d'erreur de configuration** — la substance est
   fixée ci-dessus ; la formulation sera arrêtée en même temps que le code, et
   les tests porteront sur la substance.
2. **Le nom des deux nouveaux modules** — la référence `boilerack.cli:main`
   ci-dessus fixe le nom du module de ligne de commande ; celui du chargeur
   reste à arrêter.
