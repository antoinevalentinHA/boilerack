# C10 — Interface utilisateur : configuration et point d'entree installe

Document **contractuel**, ecrit avant toute implementation. Il fixe la frontiere
publique de Boilerack pour un utilisateur : ce qu'il installe, ce qu'il ecrit,
ce qu'il lance, et ce qu'il obtient. Aucun code n'existe encore.

Ce qui est ecrit ici devient une **surface de compatibilite** au meme titre que
les topics MQTT de C7 : les noms de cles, le nom de la variable
d'environnement, les valeurs par defaut et les codes de sortie ne pourront plus
changer sans casser des installations.

## Objet

> Permettre a un utilisateur d'installer Boilerack puis de le lancer avec une
> configuration **explicite**, **validee**, et **sans aucun secret dans le
> fichier de configuration**.

Quatre choses distinctes, qu'il ne faut pas confondre :

| | Ou | Duree de vie |
|---|---|---|
| **Configuration durable** | fichier TOML | celle de l'installation |
| **Secret** | variable d'environnement | celle du processus |
| **Options de lancement** | ligne de commande | celle de la session |
| **Comportement d'execution** | ni l'un ni l'autre — il est contractuel | fixe par ce document |

## Ce que C10 n'est pas

C10 ne change **rien** au comportement du pont. Il ne touche ni la surface MQTT
de lecture (C7), ni la composition (C8), ni le cycle de vie (C9). Il ne fait
qu'ouvrir une porte d'entree devant ce qui existe deja.

## Lancement

Deux chemins publics, **strictement equivalents** :

```
boilerack --config /chemin/boilerack.toml
python -m boilerack --config /chemin/boilerack.toml
```

Les deux appellent **la meme fonction `main()`**. Le module `__main__.py` ne
porte aucune logique propre : il delegue et projette le resultat. Aucune
divergence de comportement entre les deux formes n'est admise, et un test devra
l'etablir.

Pourquoi les deux, plutot qu'un seul : la commande installee est la plus
naturelle, mais elle n'est joignable que si le `bin`/`Scripts` de
l'environnement est dans le `PATH` — ce qui n'est pas acquis sur un Raspberry
Pi avec un environnement virtuel non active. `python -m boilerack` fonctionne
alors sans rien configurer. Le cout de ce second chemin est nul des lors que
`__main__.py` ne duplique aucune logique.

## Options de ligne de commande

### `--config CHEMIN`

**Obligatoire.** Chemin du fichier TOML.

**Aucun chemin implicite n'est introduit** : ni `/etc/boilerack.toml`, ni
`~/.config/...`, ni le repertoire courant. Boilerack ne cherche pas sa
configuration, il la recoit. Une decouverte silencieuse rendrait le
comportement dependant du repertoire de lancement et du compte utilisateur,
c'est-a-dire imprevisible pour un service.

- option absente → **erreur d'usage**, code `2` ;
- fichier absent, illisible ou invalide → **erreur de configuration**, code `2`.

### `--log-level NIVEAU`

Optionnel. Defaut : `INFO`.

Valeurs acceptees, et **elles seules** :

```
DEBUG  INFO  WARNING  ERROR  CRITICAL
```

Toute autre valeur est une erreur d'usage. Le jeu est ferme deliberement :
`logging` accepte aussi des entiers arbitraires et des niveaux personnalises,
ce qui n'a aucun sens ici et n'ouvrirait qu'une surface a maintenir.

`--log-level` est **exclusivement** une option de ligne de commande :

- il n'existe **aucune** cle `log_level` dans le TOML ;
- il n'existe **aucune** variable d'environnement correspondante ;
- il n'affecte que la session en cours.

C'est un reglage de diagnostic, pas une propriete durable de l'installation.
L'exposer ailleurs creerait une precedence entre sources pour un unique
parametre — un cout sans contrepartie.

## Fichier de configuration

Format **TOML**. Trois tables, **et aucune autre** :

```toml
[mqtt]
[vclient]
[read_surface]
```

Le schema est **ferme** : toute table inconnue et toute cle inconnue sont
**refusees**. Cette strictesse est legitime parce que Boilerack possede
integralement son schema — il n'herite d'aucun format tiers et ne partage son
fichier avec personne. Elle transforme une faute de frappe silencieuse, qui
laisserait un reglage sans effet, en une erreur immediate et nommee.

TOML est retenu parce qu'il est le seul format a cumuler : disponibilite
**stdlib** sur toutes les versions supportees (`tomllib`, Python ≥ 3.11, et
`requires-python = ">=3.11"`), types natifs distincts pour entiers, flottants et
booleens, commentaires — le fichier est destine a etre edite a la main —, et
absence de toute dependance nouvelle. YAML aurait introduit la **deuxieme**
dependance d'execution du projet ; JSON n'admet pas de commentaires.

### Les 13 cles publiques

| Table | Cle | Type TOML | Obligatoire | Defaut |
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

**6 + 4 + 3 = 13 cles.** Deux seulement sont obligatoires : `mqtt.host` et
`vclient.executable`. Ce sont les deux valeurs de site que le depot ne peut pas
deviner, et il n'en invente aucun defaut.

Tous les defauts ci-dessus sont **exactement** ceux que portent deja les
structures internes. C10 n'en introduit aucun et n'en modifie aucun : il les
rend publics, donc contractuels.

## Table `[mqtt]`

### `host`
Broker MQTT. Chaine non vide. **Obligatoire.**

### `port`
Entier, `1..65535`. Defaut `1883`.

### `client_id`
Identite MQTT du pont. Chaine non vide. Defaut `"boilerack"`.

> **A savoir.** Deux instances de Boilerack connectees au meme broker avec le
> meme `client_id` se deconnectent mutuellement en boucle : le protocole MQTT
> impose l'unicite. Le defaut convient a une installation unique ; toute
> seconde instance **doit** en changer.

### `keepalive`
Entier strictement positif, en **secondes**. Defaut `60`.

### `username`
Chaine non vide si presente. Absente par defaut.

`username` n'est **pas** un secret : c'est un identifiant, au meme titre qu'un
nom d'hote. Il appartient donc au fichier, avec le reste de la configuration
durable. La symetrie apparente avec `password` est trompeuse et n'est pas
retenue.

`username` et le mot de passe sont **independants** : aucun des deux n'en
exige l'autre. C'est le comportement de l'adaptateur existant, qui n'appelle
`username_pw_set` que si `username` est fourni, et transmet alors le mot de
passe tel quel, y compris absent. Le contrat n'ajoute aucune contrainte croisee.

### `tls`
Booleen. Defaut `false`.

`true` active le mecanisme TLS **par defaut** du client MQTT, c'est-a-dire la
verification contre le magasin de certificats du systeme. Rien de plus :

- aucune autorite de certification personnalisee ;
- aucun certificat client ;
- aucun reglage de verification du nom d'hote ;
- **aucun nouveau reglage TLS n'est introduit par C10.**

Le contrat decrit ici exactement ce que le code fait aujourd'hui, ni plus ni
moins. Exposer davantage serait promettre ce qui n'existe pas.

### Cles explicitement refusees dans `[mqtt]`

| Cle | Motif du refus |
|---|---|
| `password` | **secret** — voir la section suivante ; jamais dans un fichier |
| `command_topic` | hors surface utilisateur C10 |
| `ack_topic_prefix` | hors surface utilisateur C10 |

Ces trois cles doivent produire une erreur **nommee**, et non le message
generique de cle inconnue : l'utilisateur qui les ecrit a une intention
precise, et merite d'apprendre pourquoi elle est refusee.

## Le secret

Un seul secret existe dans tout Boilerack : le mot de passe MQTT.

Il est fourni **exclusivement** par la variable d'environnement :

```
BOILERACK_MQTT_PASSWORD
```

### Choix du nom

Le depot ne comportait, avant ce contrat, **aucune** variable d'environnement,
aucune constante en majuscules exposee, et donc aucune convention preexistante
a respecter ou a contredire — verifie par recherche exhaustive. Le nom est donc
choisi librement, mais une seule fois.

`BOILERACK_MQTT_PASSWORD` est retenu pour trois raisons : le prefixe reprend le
**nom de distribution et de paquet** deja public (`boilerack`), ce qui evite
toute collision avec un autre logiciel sur la meme machine ; le segment
intermediaire nomme le sous-systeme, ce qui laisse la place a un eventuel futur
secret sans reorganisation ; et la forme `MAJUSCULES_AVEC_SOULIGNES` est la
convention universelle des variables d'environnement.

Ce nom devient **surface publique** des sa publication.

### Semantique

- variable absente → mot de passe `None`, connexion sans mot de passe ;
- variable presente → sa valeur est le mot de passe, telle quelle, sans
  interpretation ni decodage ;
- **fait a connaitre** : dans l'adaptateur actuel, le mot de passe n'est
  transmis au client MQTT que lorsque `mqtt.username` est defini.
  `BOILERACK_MQTT_PASSWORD` presente **sans** `mqtt.username` n'a donc aucun
  effet sur l'authentification. C10 ne transforme pas cette situation en erreur
  de configuration et n'introduit **aucune** contrainte croisee : le contrat se
  borne a l'enoncer, et une propriete de caracterisation l'epinglera ;
- **aucune** valeur TOML concurrente : `[mqtt].password` est refuse ;
- **aucune** precedence a arbitrer, puisqu'il n'y a qu'une source ;
- **aucun** equivalent en ligne de commande — un mot de passe en argument
  serait visible dans la table des processus et dans l'historique du shell ;
- sa valeur n'est **jamais** affichee, ni journalisee, ni incluse dans un
  message d'erreur ;
- le masquage existant dans la representation des objets de configuration est
  preserve, et reste transitif.

### Ce que C10 ne lit pas dans l'environnement

Boilerack lit **une** variable, celle qu'il possede explicitement. Il ne traite
pas l'environnement du processus comme un document de configuration :

- aucun balayage des variables ;
- aucun refus de variable inconnue — l'environnement ne lui appartient pas ;
- aucun espace de noms de configuration general ;
- aucune possibilite pour l'environnement de surcharger une cle TOML ;
- aucun chargeur de fichier `.env`. Le processus herite de son environnement
  par les moyens habituels du systeme.

Les deux sources sont donc **disjointes** : le fichier porte tout sauf le
secret, l'environnement porte le secret et rien d'autre. Il n'y a aucune
cascade, et donc aucune question « qui gagne ? » a laquelle repondre.

## Table `[vclient]`

### `executable`
Chemin ou nom de l'executable `vclient`. Chaine non vide. **Obligatoire.**

Son existence sur le disque n'est **pas** verifiee pendant la validation : ce
serait une verification d'infrastructure, et elle echouerait pour de mauvaises
raisons (montage non encore disponible, `PATH` different au lancement du
service).

### `host`
Hote du demon `vcontrold`. Chaine non vide si presente. Absente par defaut.

### `port`
Entier `1..65535`. Absent par defaut.

`host` et `port` sont **independants** : ni l'un ni l'autre n'exige l'autre.
C'est le comportement de l'adaptateur, qui ajoute `-h` et `-p` a la ligne de
commande separement, chacun seulement s'il est fourni. Omettre les deux laisse
`vclient` employer ses propres defauts. Le contrat n'ajoute aucune contrainte
que le code n'impose pas.

### `read_timeout_s`
Duree en **secondes**, finie et strictement positive. Defaut `5.0`.

Le type TOML accepte est **integer ou float** : `5` et `5.0` sont tous deux
valides et signifient la meme chose. La valeur est convertie en `float`. Cette
tolerance est justifiee — un utilisateur ecrira naturellement `10` plutot que
`10.0` pour une duree ronde — et sans ambiguite, TOML distinguant les deux
types a la lecture.

### Cle non exposee

`write_timeout_s` n'est pas exposee : elle n'a **aucun consommateur** dans le
code. Voir la section « Champs non exposes ».

## Table `[read_surface]`

### `prefix`
Racine de tous les topics MQTT de lecture. Defaut `"boiler"`. Valide selon les
regles de topic deja etablies par C7 §3.3 — validation existante, non
redefinie ici.

> **Contrat important.** Modifier cette valeur modifie **l'ensemble des topics
> publics** que Boilerack publie. Ce n'est pas un reglage cosmetique : tout
> consommateur en aval — tableau de bord, automatisation, enregistreur — doit
> etre mis a jour en consequence.

### `snapshot_period_s`
Entier strictement positif, en **secondes**. Defaut `30`.

Une contrainte supplementaire existe deja et n'est pas relaxee : la periode
doit rester **inferieure ou egale au plus petit `fresh_max_s`** des mesures
declarees. Cette borne est **dynamique** : elle depend des mesures reellement
injectees, et vaut 90 s avec la surface v1 **d'aujourd'hui**.

Ce nombre est une **observation**, pas une constante du contrat. C10 ne doit ni
le recopier, ni recalculer `min(fresh_max_s)` pour son propre compte : ce serait
dupliquer une regle metier dont l'autorite est ailleurs, et la faire diverger au
premier changement de la surface de lecture. Voir « Frontiere de la validation
dynamique ».

### `heartbeat_period_s`
Entier strictement positif, en **secondes**. Defaut `30`.

**`0` desactive le battement.**

#### Pourquoi cette convention, et pas une autre

Le probleme est reel et nait du passage de Python a TOML : le runtime represente
la desactivation par `None`, or **TOML n'a pas de valeur nulle**. Il faut donc
une convention explicite. Quatre options ont ete examinees.

| Option | Verdict |
|---|---|
| **`0` signifie desactive** | **retenue** |
| Omettre la cle | insuffisant : l'absence vaut deja « defaut 30 », elle ne peut pas aussi vouloir dire « desactive » |
| Cle booleenne separee (`heartbeat_enabled`) | rejetee : deux cles pour un concept, et un etat contradictoire possible — `enabled = false` avec `period = 30` |
| Type mixte (`false` ou un entier) | rejetee : melanger booleen et entier sur une meme cle contredit le typage strict retenu par ailleurs |

`0` est une valeur speciale, ce qui n'est jamais elegant, mais c'est la seule
option qui reste dans un type unique, sans cle supplementaire et sans etat
contradictoire. Elle est **sans ambiguite** : `0` seconde n'a aucune
interpretation utile comme periode, et la structure interne le refuse deja
explicitement.

**Mecanique exacte, a ne pas confondre.** La projection `0 → None` appartient au
chargeur de configuration de C10. La structure interne, elle, continue de
refuser `0` : elle ne recoit jamais cette valeur, elle recoit `None`. Aucune
regle existante n'est modifiee.

**Ordre imperatif des deux etapes.** Le type est valide **d'abord**, la valeur
est interpretee **ensuite**. Seul un **entier TOML exact** `0` est projete vers
`None`.

Consequence directe :

```toml
heartbeat_period_s = false
```

est **refuse** comme erreur de type. Il n'est **jamais** interprete comme une
desactivation.

Le piege est reel et tient a Python, pas a TOML : `bool` y est une sous-classe
de `int`, et `False == 0` est vrai. Une projection ecrite comme
`if valeur == 0: valeur = None` **avant** la validation de type accepterait donc
silencieusement `false` et desactiverait le battement sans que l'utilisateur
l'ait demande. La comparaison a zero ne doit jamais preceder la verification du
type.

## Champs non exposes

| Champ | Motif |
|---|---|
| `MqttConfig.command_topic` | **mort** — aucun consommateur dans le code |
| `MqttConfig.ack_topic_prefix` | **mort dans le chemin d'execution** — le noyau transactionnel a son propre parametre, jamais alimente par cette valeur, et il n'est pas cable |
| `VclientConfig.write_timeout_s` | **mort** — aucun consommateur |
| `RuntimeConfig.specs` | **surface interne fermee** — la table des huit mesures est un contrat C7, pas un reglage |

Leur presence dans une structure interne **ne constitue pas** un engagement
d'interface publique. Exposer un champ parce qu'il existe reviendrait a
publier des boutons qui ne font rien, et a s'engager a les maintenir.

**C10 ne les supprime pas.** Retirer un champ mort toucherait les lots C3 et C4
et anticiperait la surface d'ecriture ; c'est une dette identifiee, datee, et
laissee a un lot ulterieur.

## Validation

C10 valide la **configuration**, jamais l'infrastructure.

### Ce qui est verifie, avant tout demarrage

1. le fichier existe ;
2. le fichier est lisible ;
3. le TOML est syntaxiquement valide ;
4. les tables sont connues ;
5. les cles sont connues, dans chaque table ;
6. les types sont exacts, au sens TOML ;
7. les cles obligatoires sont presentes ;
8. les contraintes de valeur sont respectees ;
9. aucun secret n'est present dans le fichier ;
10. `RuntimeConfig` se construit — ce qui declenche les validations portees par
    les structures de configuration elles-memes ;
11. les validations **dependant de la surface de lecture** passent, notamment la
    borne dynamique de `snapshot_period_s` — voir ci-dessous.

### Ce qui n'est jamais fait pour valider

- ouvrir une connexion MQTT ;
- resoudre activement le nom d'hote du broker ;
- lancer `vclient` ;
- interroger `vcontrold` ;
- toucher a la chaudiere ;
- verifier l'existence de l'executable sur le disque.

Ce n'est pas une precaution de style : c'est la preservation d'un invariant
etabli et teste par C8 — construire n'ouvre aucune socket et ne lance aucun
processus. Melanger validation de saisie et test de connectivite rendrait le
demarrage dependant du reseau et confondrait une faute de frappe avec une panne
d'infrastructure.

### Ou survient chaque validation

Trois etages, qu'il faut distinguer parce que le message et le moment different :

| Etage | Ce qu'il verifie | Quand |
|---|---|---|
| Chargeur C10 | forme du fichier, tables, cles, types TOML, cles interdites | a la lecture |
| Structures de configuration | valeurs : ports, durees, chaines non vides, topic valide | a la construction |
| Autorite de la surface de lecture | borne dynamique de `snapshot_period_s`, contre les mesures reellement declarees | avant l'entree dans `run_lifecycle()` |

Les trois surviennent **avant que quoi que ce soit ne demarre**, et les trois
produisent une erreur de configuration lisible : code `2`, sans traceback, avec
la table et la cle fautives nommees. Le chargeur est responsable de cette mise
en contexte, y compris lorsque l'erreur remonte des deux etages suivants.

### Frontiere de la validation dynamique

Le troisieme etage merite d'etre specifie, parce qu'il est le seul dont
l'autorite ne reside pas dans le chargeur.

**Exigence normative.** Toute validation dependant de la construction statique
de la surface de lecture — au premier rang, la borne dynamique de
`snapshot_period_s` — a lieu **avant l'entree dans `run_lifecycle()`**, et
repose sur **la meme autorite metier que celle appliquee par le publieur**. Une
configuration qui echoue a ce stade reste une **erreur de configuration
utilisateur** : code `2`, aucun traceback, `[read_surface].snapshot_period_s`
identifiable.

**Interdits.** Aucun des quatre contournements suivants n'est admis :

- recopier la valeur `90` dans le chargeur ;
- recalculer `min(fresh_max_s)` pour le compte de C10 ;
- intercepter globalement les `ValueError` remontant de `run_lifecycle()` ;
- transformer une panne d'execution en code `2`.

Les deux premiers dupliqueraient une regle metier et la feraient diverger ; les
deux suivants confondraient une saisie fautive avec une panne.

**Ce que le contrat ne fixe pas.** Il fixe la **propriete** — validation avant
`run_lifecycle()`, autorite unique — et **non la mecanique**. En particulier, il
n'impose **pas** de construire le runtime deux fois. La caracterisation C10
devra determiner la couture minimale, en comparant au moins :

1. l'extraction ou la reutilisation d'une validation **pure** partagee avec le
   publieur ;
2. une autre couture deja existante offrant la meme autorite ;
3. la preconstruction du runtime, **uniquement** si aucune solution plus sobre
   n'existe.

Cette comparaison appartient a l'etape suivante, pas a ce contrat.

### Types stricts

Les types annonces sont ceux de **TOML**, pas ceux de l'heritage Python.

Point d'attention, deja traite ailleurs dans le depot : en Python, `bool` est
une sous-classe de `int`. Une verification naive par `isinstance(valeur, int)`
accepterait donc `true` comme numero de port ou comme periode.

**Une cle declaree entiere refuse un booleen.** Meme rigueur pour les
flottants. Le depot applique deja cette regle dans ses structures de
configuration ; le chargeur C10 doit l'appliquer au meme titre, et un test doit
la verrouiller pour **chaque** cle numerique.

## Erreurs de configuration

Une seule categorie d'erreur utilisateur. Aucune hierarchie d'exceptions :
elle n'aurait aucun consommateur, et le point d'entree est le seul appelant.

Un message d'erreur de configuration :

- est **lisible** — il s'adresse a une personne qui edite un fichier, pas a un
  developpeur qui lit une pile d'appels ;
- nomme le **fichier** lorsque c'est pertinent ;
- nomme la **table et la cle** fautives ;
- ne contient **jamais** le mot de passe ;
- ne produit **aucun traceback** : la faute est dans le fichier, une pile
  d'appels designerait le code et n'apprendrait rien.

Forme visee, a titre indicatif — le contrat fixe la substance, pas la
ponctuation :

```
boilerack: configuration invalide: [mqtt].host est obligatoire
boilerack: configuration invalide: cle inconnue [mqtt].hots
boilerack: configuration invalide: [mqtt].password est interdit, utilisez BOILERACK_MQTT_PASSWORD
```

Code de sortie : **`2`**.

## Erreurs d'execution

Une fois `RuntimeConfig` construit et le runtime lance, une exception n'est plus
une erreur de l'utilisateur : c'est une panne du programme ou de son
environnement. Elle est traitee comme telle.

- **aucune interception globale** d'`Exception` au point d'entree ;
- le **traceback natif** est conserve — c'est le meilleur outil de diagnostic
  disponible, et l'affichage des groupes d'exceptions par Python est deja
  excellent ;
- le code de sortie est celui de Python, soit **`1`**.

Embellir cette sortie ferait perdre de l'information sans rien apporter.

## Codes de sortie

| Code | Situation |
|---|---|
| `0` | arret normal, ou arret demande par `SIGTERM` |
| `130` | arret demande par `SIGINT` (Ctrl-C) |
| `2` | erreur d'usage de la ligne de commande, ou erreur de configuration |
| `1` | panne d'execution non interceptee, comportement natif de Python |

**Repartition des responsabilites, a ne pas confondre.** C9 produit un
**resultat logique** — un entier rendu par une fonction, `0` ou `130`. C10 est
le seul responsable de sa **projection en code de sortie de processus**. C9 ne
sort jamais du processus ; C10 ne decide jamais de la semantique de l'arret.

`2` est retenu pour les erreurs d'usage et de configuration parce que c'est la
convention Unix, et surtout parce que l'analyseur d'arguments de la
bibliotheque standard sort **deja** en `2` : retenir autre chose creerait une
incoherence entre « mauvaise option » et « mauvais fichier ».

## Convention de `main()`

```
main(argv: Sequence[str] | None = None) -> int
```

`main` **rend** un entier ; elle ne quitte pas le processus.

Ce choix n'est pas arbitraire, il decoule du mecanisme reel de chacun des trois
appelants — verifie, non suppose :

| Appelant | Ce qu'il fait |
|---|---|
| Commande installee | le script genere execute `sys.exit(main())` — c'est le gabarit standard de l'ecosysteme |
| `python -m boilerack` | `__main__.py` doit projeter lui-meme : `raise SystemExit(main())` |
| Tests | `assert main([...]) == 0` — direct, sans capture d'exception |

Une convention ou `main()` leverait elle-meme `SystemExit` fonctionnerait pour
les deux premiers, mais imposerait `pytest.raises(SystemExit)` a chaque test, ce
qui rend l'assertion sur le code plus indirecte. La convention « rendre un
entier » sert les trois appelants sans concession.

Le parametre `argv` optionnel permet de tester sans manipuler `sys.argv`. Absent,
il vaut `sys.argv[1:]`.

**Nuance honnete a documenter, plutot qu'a masquer.** L'analyseur d'arguments de
la bibliotheque standard leve `SystemExit(2)` depuis l'interieur de `main()`
pour une option invalide, et `SystemExit(0)` pour `--help`. `main()` a donc deux
issues : un entier rendu dans le cas normal, et un `SystemExit` qui la traverse
pour l'usage et l'aide. Les deux produisent le meme code de processus par les
deux chemins de lancement. Intercepter ces `SystemExit` pour uniformiser
obligerait a traiter `--help` comme une erreur : le remede serait pire.

Un test devra couvrir explicitement les deux issues.

## Journalisation

C10 est le **proprietaire** de la configuration de journalisation du processus,
et le seul. C9 l'a explicitement refusee, parce qu'une fonction appelee
programmatiquement n'a pas a imposer sa politique au processus hote.

- **aucune configuration a l'import** — importer un module de Boilerack, y
  compris celui de la ligne de commande, ne touche a rien ;
- **chaque invocation de `main()` configure la journalisation du processus
  qu'elle possede**, conformement au `--log-level` de cette invocation ;
- canal : **`stderr`** — c'est le canal des diagnostics ; `stdout` reste libre ;
- niveau par defaut : **`INFO`**, pilote par `--log-level` ;
- chaque ligne porte un **horodatage**, un **niveau**, le **nom du logger** et
  le **message** ;
- **aucune couleur, aucune dependance, aucun format structure.**

L'horodatage n'est pas decoratif : un pont qui tourne en continu produit des
lignes qu'il faut pouvoir situer, et un lancement manuel n'en ajoute aucun.

**Semantique sur appels repetes.** « Une seule fois » serait ambigu, et pire :
faux avec la mecanique par defaut de la bibliotheque standard, dont la
configuration simplifiee **ne fait rien** si la racine possede deja un
gestionnaire. Deux appels successifs de `main()` avec des niveaux differents
laisseraient alors le premier niveau en place — silencieusement.

Le contrat exige donc l'inverse : **le niveau demande est effectivement
applique a chaque invocation**. `main()` prend possession de la configuration de
journalisation du processus ; c'est legitime, puisqu'elle en est la racine. Une
implementation forcant la reconfiguration est **autorisee et probablement
adaptee**, mais le contrat fixe la propriete observable, pas la ligne de code :
toute solution equivalente de la bibliotheque standard convient.

Consequences, toutes verifiables :

- importer le module de ligne de commande ne touche jamais a la journalisation ;
- appeler `main()` en prend possession ;
- deux appels successifs avec des niveaux differents refletent le **second**.

Le contrat fixe la **semantique** du format — quelles informations, dans quel
ordre — et non une chaine de format caractere par caractere : figer celle-ci
n'apporterait rien et interdirait tout ajustement de lisibilite.

Etat actuel, pour memoire : deux modules journalisent, pour douze appels — dix
avertissements, une information, une exception. Sans configuration, seuls les
avertissements sont visibles et la confirmation de connexion ne l'est pas. Le
defaut `INFO` la rend visible, sans bavardage.

## Fichier d'exemple

C10 livrera un exemple de configuration, **sans aucun secret**.

Il doit : contenir les trois tables ; distinguer visiblement les deux cles
obligatoires des onze optionnelles ; montrer ou commenter les valeurs par
defaut ; expliquer que le mot de passe se fournit par `BOILERACK_MQTT_PASSWORD`
et **nulle part ailleurs**.

Il ne doit **jamais** presenter une cle `password` — meme commentee, meme avec
une valeur manifestement fictive. Une ligne commentee se decommente ; l'exemple
ne doit pas contenir le geste dangereux, il doit contenir son alternative.

Nom propose : `docs/boilerack.example.toml`. Le placer sous `docs/` plutot qu'a
la racine evite qu'il soit pris pour une configuration active du depot.

## README

Le lot devra rendre le chemin utilisateur comprehensible depuis le README, en
cinq etapes : installation ; creation du fichier TOML ; fourniture eventuelle du
mot de passe ; lancement ; signification des codes de sortie.

Le README **renvoie** au present contrat, il ne le duplique pas. Deux copies
d'une meme specification divergent toujours.

## Packaging

### Commande installee

```toml
[project.scripts]
boilerack = "boilerack.cli:main"
```

Forme correcte pour le systeme de construction en place. Ce sera la
**premiere** modification de `pyproject.toml` depuis le lot des adaptateurs
reels, et elle n'ajoute **aucune dependance**.

### Module executable

`src/boilerack/__main__.py`, reduit a la delegation :

```
from boilerack.cli import main
raise SystemExit(main())
```

Aucune logique propre, aucune duplication. Un test devra verifier que ce fichier
ne contient rien d'autre.

## Absence d'entrees-sorties d'infrastructure

Le chargement et la validation **peuvent** : ouvrir et lire le fichier TOML ;
lire la variable d'environnement du mot de passe.

Ils ne **peuvent pas** : ouvrir une socket ; se connecter a un broker ; lancer
un sous-processus ; executer `vclient`.

La construction de `RuntimeConfig` reste hors de toute entree-sortie
d'infrastructure. Un test devra le prouver par sabotage, comme les lots C8 et C9
l'ont fait pour la construction du runtime.

## Hors perimetre

Confirmes hors C10, aucune necessite demontree :

unite systemd · Docker · installateur · module complementaire Home Assistant ·
HACS · supervision externe · reprise ou reconnexion · nouvelle tentative
`vclient` · ecriture chaudiere · configuration metier des commandes ·
decouverte automatique · assistant interactif · interface web · migration de
configuration · gestionnaire de secrets · paquet Debian · **tout nouveau
reglage TLS** · **suppression des champs morts**.

## Proprietes a verrouiller

Le lot d'implementation devra prouver, au minimum, les proprietes suivantes.
Les noms de tests ne sont pas fixes ici ; les proprietes le sont.

### Chargement et schema

- une configuration minimale — les deux cles obligatoires seules — produit un
  `RuntimeConfig` valide ;
- chaque valeur par defaut non fournie vaut **exactement** celle annoncee ;
- table inconnue refusee ; cle inconnue refusee, dans chacune des trois tables ;
- TOML malforme refuse ; fichier absent refuse ; fichier illisible refuse ;
- chaque cle obligatoire absente est refusee, en nommant la cle.

### Types

- pour **chaque** cle entiere, un booleen est refuse ;
- pour **chaque** cle entiere, un flottant est refuse ;
- `read_timeout_s` accepte un entier **et** un flottant, refuse un booleen ;
- `tls` refuse tout ce qui n'est pas un booleen ;
- chaque cle chaine refuse les autres types.

### Secret

- `[mqtt].password` dans le fichier est refuse, avec un message qui **nomme**
  la variable d'environnement a utiliser ;
- variable presente → le mot de passe est celui-la ;
- variable absente → mot de passe `None`, et le chargement reussit ;
- **aucune fuite** : le secret n'apparait dans aucun message d'erreur, dans
  aucune representation d'objet, dans aucune ligne journalisee ;
- aucune autre variable d'environnement n'est lue ;
- **caracterisation** : variable presente **sans** `mqtt.username` — le
  chargement reussit, aucune erreur n'est levee, et le mot de passe n'atteint
  pas le client MQTT. Cette propriete epingle le comportement de l'adaptateur ;
  elle ne promet rien de plus et n'impose aucune contrainte croisee.

### Battement

- `heartbeat_period_s = 0` desactive le battement ;
- `heartbeat_period_s` absent vaut `30`, battement actif ;
- une valeur negative est refusee ;
- la structure interne ne recoit **jamais** `0` ;
- **`heartbeat_period_s = false` est refuse comme erreur de type**, et n'est en
  aucun cas interprete comme une desactivation.

### Surface de lecture

- avec la surface v1 **actuelle**, `snapshot_period_s = 91` est **refuse avant
  le demarrage du cycle de vie** : code `2`,
  `[read_surface].snapshot_period_s` identifiable, aucun traceback, **aucune
  connexion**, **aucun sous-processus**, et le runner n'est **jamais** entre ;
- une valeur a la borne exacte est acceptee ;
- la validation utilise l'autorite de la surface de lecture, jamais une valeur
  recopiee.

> `91` est une valeur de **caracterisation de la surface v1 d'aujourd'hui**, pas
> une constante a inscrire dans C10. Si la surface change, le test change avec
> elle ; le chargeur, lui, ne change pas.

### Ligne de commande

- `--config` absent → code `2` ;
- `--config` pointant vers un fichier absent → code `2` ;
- `--log-level` accepte les cinq valeurs, et **rien d'autre** ;
- `--log-level` absent → `INFO` ;
- `--help` sort en `0` ;
- une option inconnue sort en `2`.

### Codes de sortie et cycle de vie

- resultat logique `0` projete en code `0` ;
- resultat logique `130` projete en code `130` ;
- erreur de configuration → code `2`, **sans traceback** ;
- panne d'execution → l'exception traverse, **traceback conserve**, code `1` ;
- l'identite de l'exception d'origine est preservee.

### Journalisation

- aucune configuration de journalisation lors du **seul import** ;
- `main()` configure la journalisation sur `stderr` ;
- le niveau demande est effectivement applique ;
- **deux appels successifs de `main()` avec des niveaux differents refletent le
  second niveau**, et non le premier.

### Frontieres

- le chargement n'ouvre **aucune socket** et ne lance **aucun sous-processus**,
  prouve par sabotage ;
- `__main__.py` ne contient aucune logique propre ;
- les deux chemins de lancement produisent le **meme** comportement.

### Mutations discriminantes

Le lot devra tuer au minimum :

| # | Mutation | Ce qu'elle casse |
|---|---|---|
| 1 | Cle inconnue acceptee silencieusement | une faute de frappe reste sans effet et sans message |
| 2 | Table inconnue acceptee | idem, a l'echelle d'une section |
| 3 | Un defaut change de valeur | rupture de contrat invisible |
| 4 | Une cle obligatoire cesse de l'etre | demarrage avec une configuration incomplete |
| 5 | Le mot de passe est lu depuis le fichier | secret versionnable |
| 6 | Le mot de passe apparait dans un message d'erreur | fuite de secret |
| 7 | `isinstance(x, int)` sans exclusion du booleen | `true` accepte comme port |
| 8 | `heartbeat_period_s = 0` transmis tel quel | erreur interne au lieu d'une desactivation |
| 9 | Erreur de configuration rendue en `1` | indistinguable d'une panne |
| 10 | `130` projete en `0` | un Ctrl-C passerait pour un arret normal |
| 11 | Interception globale d'`Exception` au point d'entree | traceback perdu, diagnostic impossible |
| 12 | Journalisation configuree a l'import | contamination du processus hote |
| 13 | `--log-level` accepte n'importe quelle chaine | surface non contractuelle |
| 14 | `__main__.py` porte de la logique | divergence entre les deux chemins |
| 15 | La validation dynamique est omise : la valeur hors borne atteint `run_lifecycle()` | traceback et code `1` la ou l'utilisateur attend une erreur de configuration en code `2` |
| 16 | `heartbeat_period_s = false` desactive silencieusement le battement | comparaison a zero placee avant la validation de type ; `False == 0` |
| 17 | Le second appel de `main()` conserve le niveau du premier | `--log-level` sans effet des la deuxieme invocation dans un meme processus |

## Fichiers previsionnels

**Nouveaux** — un module de chargement de configuration ; un module de ligne de
commande ; `src/boilerack/__main__.py` ; leurs fichiers de tests ; un exemple
TOML ; le present document.

**Modifies** — `pyproject.toml`, pour la seule entree `[project.scripts]` ;
`README.md`, pour le chemin utilisateur ; eventuellement un renvoi dans le
document C9.

**Non modifies** — tout `adapters/`, `read_surface/`, `transport/`, `core/`,
`runtime.py`, `lifecycle.py`, `clock.py`. **Aucune dependance ajoutee.**

## Ce que ce contrat n'a pas tranche

Deux points sont volontairement laisses a l'etape de caracterisation, parce
qu'ils dependent de faits a etablir plutot que de decisions a prendre :

1. **La forme exacte du message d'erreur de configuration** — la substance est
   fixee ci-dessus ; la formulation sera arretee en meme temps que le code, et
   les tests porteront sur la substance.
2. **Le nom des deux nouveaux modules** — la reference `boilerack.cli:main`
   ci-dessus fixe le nom du module de ligne de commande ; celui du chargeur
   reste a arreter.
