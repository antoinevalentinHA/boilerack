# C9 — Cycle de vie du processus et arret sur signal

Document d'architecture, ecrit **avant** l'implementation puis complete par
elle. Il fixe la frontiere du lot, les decisions arbitrees, les invariants que
le code preserve, les preuves executees, et l'API effectivement livree.

## Objectif normatif

> C9 permet a du code Python appelant de lancer un `Runtime` assemble et de
> transformer `SIGINT` ou `SIGTERM` en **demande d'arret propre**. La demande
> reveille l'attente du runner afin qu'elle soit prise en compte a son prochain
> point de controle. C9 ne promet **aucune borne** sur la duree totale de sortie
> lorsqu'un travail est deja engage ou lorsque `stop()` est en cours.

Une seule propriete sera bornee et demontree : la **latence de reveil** de
l'attente interruptible, sous les conditions effectivement testees. Voir
« Latences » plus bas.

## Ce que C9 n'est pas

C9 **n'est pas** le point d'entree du programme. Il ne fournit ni commande, ni
lecture de configuration, ni nom de cle publique. Il offre une **fonction Python
de cycle de vie**, appelee par un programme qui, lui, viendra plus tard (C10).

Cette distinction n'est pas cosmetique : elle determine plusieurs decisions du
present document, notamment le refus de configurer la journalisation.

## Point de depart — ce que C8 fournit deja

```
build_runtime(config: RuntimeConfig, stop: StopSignal) -> Runtime
Runtime(publisher: ReadSurfacePublisher, runner: ReadSurfaceRunner)
ReadSurfaceRunner(publisher, clock: Clock, stop: StopSignal).run() -> None
StopSignal : Protocol, is_set() -> bool
```

Le runner consulte la demande d'arret a deux moments par cycle : a l'entree de
la boucle, et **apres l'attente**, avant tout travail. Ce second point de
controle existe deja, il est teste, et C9 s'appuie dessus sans le modifier.

C8 garantit par ailleurs : `start()` une fois ; ordre
`is_set → due_at → attente → is_set → run_due` ; jamais de sommeil negatif ;
aucun rattrapage ; `stop()` toujours tente sur le chemin `Exception` ; identites
d'exception preservees ; `ExceptionGroup` en cas de double echec.

## Le probleme etabli

`SystemClock.sleep()` delegue a `time.sleep()`. Or CPython, depuis PEP 475,
**reprend** `time.sleep()` apres l'execution d'un gestionnaire de signal qui ne
leve pas d'exception.

Consequence, mesuree lors du cadrage : un gestionnaire qui se contente d'armer
un drapeau **ne reveille pas** l'attente. Le processus continuerait de dormir
jusqu'a l'echeance prevue.

| Mecanisme | Duree demandee | Duree observee | Reveil |
|---|---|---|---|
| `time.sleep` + gestionnaire pose-drapeau | 3.00 s | 3.00 s | **non** |
| `time.sleep` + gestionnaire par defaut (leve `KeyboardInterrupt`) | 3.00 s | 0.50 s | oui, par exception |
| attente sur etat + armement depuis un autre fil | 3.00 s | 0.50 s | **oui** |
| attente sur etat + gestionnaire `SIGINT` pose-drapeau | 2.00 s | 0.50 s | **oui** |

Mesures faites sur Windows / CPython 3.14, hors depot. Elles etablissent le
mecanisme ; elles ne valent **pas** preuve du comportement sur la plateforme
cible. Voir « Preuve POSIX ».

Les deux dernieres lignes montrent qu'une attente sur etat **peut** etre
reveillee. Elles ne suffisent pourtant pas a retenir cette solution : la section
suivante expose pourquoi armer l'etat depuis le gestionnaire a ete rejete.

C9 a donc besoin d'une **couture d'attente interruptible**. Ce n'est pas un
confort : sans elle, armer un drapeau depuis un gestionnaire de signal serait un
geste sans effet observable avant la prochaine echeance.

## Faits etablis par la caracterisation

Ces faits sont mesures, pas supposes. Ils ont ete etablis **avant** tout code
de production, et restent verrouilles par `tests/test_lifecycle.py`.

Une premiere caracterisation avait retenu `threading.Event`, arme depuis le
gestionnaire de signal. Une contre-caracterisation ciblee l'a **invalidee**. Le
mecanisme retenu est donc different, et la section qui suit expose d'abord
pourquoi.

### Pourquoi `threading.Event` arme depuis le gestionnaire est rejete

`Event.__init__` construit `Condition(Lock())` : un verrou **non reentrant**.
`set()` le prend ; `is_set()` ne prend **aucun** verrou. Si un second signal,
de numero different, survient pendant l'execution de `set()` et rappelle
`set()` sur le meme fil, celui-ci se bloque **definitivement**.

Ce defaut n'est pas theorique. Il a ete **reproduit de facon deterministe**,
avec deux vrais gestionnaires et sans aucun verrou pris a la main : un `Event`
instrumente delivre le second signal a l'interieur meme de `set()`, entre
l'acquisition du verrou et la pose du drapeau. Le processus ne rend jamais la
main ; seul un delai dur permet de le constater.

L'attenuation envisagee — garder le gestionnaire par `if not etat.is_set()` —
a ete testee et **ne supprime pas le blocage**. La raison est simple, et elle
avait ete manquee : le drapeau n'est pose qu'**apres** l'acquisition du verrou,
donc la garde laisse passer precisement dans la fenetre qu'elle etait censee
fermer. Les deux variantes, avec et sans garde, se bloquent.

Le critere de decision est ici sans ambiguite : un blocage connu **dans le
chemin d'arret lui-meme** contredit l'objet du lot. Aucune probabilite faible
ne rachete cela.

`threading.Event` conserve par ailleurs toutes ses qualites — armement
idempotent, attente passive (moins de 1 ms de CPU pour 1 s d'attente), reveil
anticipe — et reste parfaitement utilisable **tant qu'aucun gestionnaire de
signal n'appelle `set()`**. C'est l'usage depuis le gestionnaire qui est
rejete, pas la primitive.

### Mecanisme retenu — reveil par descripteur

`signal.set_wakeup_fd` fait ecrire, **par le niveau C de CPython**, un octet
egal au numero du signal dans un descripteur choisi. Le gestionnaire Python n'y
participe pas : il peut etre entierement **vide**. Aucun verrou n'est donc pris
dans le chemin de signal, et la course de reentrance devient structurellement
impossible.

Caracteristiques etablies par la mesure :

| Point | Constat |
|---|---|
| Fil principal | requis, `ValueError` sinon — meme contrainte que `signal.signal`, aucune nouvelle |
| Valeur de retour | le descripteur precedent, ou `-1` si aucun ; c'est ce qui permet une restauration exacte |
| Restauration | `set_wakeup_fd(precedent)` restitue l'etat anterieur |
| Contenu ecrit | un octet, egal au numero du signal (`2` pour `SIGINT`, `15` pour `SIGTERM`) |
| Ordre | preserve : `SIGINT` puis `SIGTERM` donne `[2, 15]`, l'inverse donne `[15, 2]` |
| Gestionnaire Python | **indispensable** : sous `SIG_IGN`, aucun octet n'est ecrit |
| Descripteur bloquant | accepte sans erreur, non verifie — a la charge de l'appelant |
| Memorisation | le descripteur reste lisible jusqu'au drainage ; une attente ouverte apres coup rend la main immediatement |

**MECANISME C9 RETENU : WAKEUP_FD.**

### Transport — paire de sockets locales

`os.pipe()` et `socket.socketpair()` sont tous deux acceptes par
`set_wakeup_fd`, et tous deux fonctionnent : l'octet est bien ecrit dans l'un
comme dans l'autre. Le tri se fait sur l'**attente**, pas sur l'ecriture.

Hors POSIX, un tube est *enregistrable* aupres d'un selecteur sans erreur, mais
l'attente elle-meme echoue — `select` n'y connait que les sockets. Une paire de
sockets locales est donc le seul transport valable sur les deux familles de
plateformes, et c'est celui qui est retenu.

**Ce n'est pas une connexion reseau.** `socket.socketpair()` cree deux
extremites locales appariees, jamais publiees, jamais accessibles depuis
l'exterieur. L'invariant C8 — `build_runtime()` n'ouvre aucune socket — porte
sur la construction de l'assemblage et reste intact : cette paire est creee par
la couche de cycle de vie, pendant son execution, et refermee a sa sortie.
Confondre les deux reviendrait a confondre un tuyau interne avec un port
ouvert.

### Premiere cause conservee

L'ordre des octets suffit : **le premier octet consomme est la premiere cause**.
Verifie dans les deux sens. Aucune priorite n'est inventee, aucun verrou n'est
requis, et les octets suivants sont draines sans modifier la cause retenue.

`dict.setdefault` reste utilisable pour materialiser « la premiere ecriture
gagne » du cote du lecteur, mais ce n'est plus qu'un detail d'implementation :
la garantie vient de la file d'octets elle-meme.

### Le drainage doit avoir lieu dans `is_set()`

Point decouvert en confrontant la couture au runner C8 reel, et **decisif**.

Si seul `sleep()` drainait le descripteur, l'arret ne serait pas vu lorsque C8
n'appelle pas `sleep()` — ce qui arrive quand l'echeance suivante est deja
depassee, comportement normal et deja teste de C8. Mesure : **trois cycles
executes au lieu d'un seul**, et une boucle sans fin si l'echeance reste
indefiniment depassee.

Avec un drainage dans `is_set()`, le meme scenario sort apres **un seul**
cycle. C'est donc `is_set()` qui doit drainer : il devient le point unique ou
l'etat d'arret est rafraichi, quel que soit le chemin emprunte par le runner.

Consequence a assumer : `is_set()` n'est plus une simple lecture, il consomme
le descripteur. C'est acceptable parce qu'il n'est appele que sur le fil
principal, par le runner, et que la lecture est non bloquante.

### Saturation

Lorsque le tampon du descripteur est plein, CPython **abandonne** les octets
excedentaires ; aucune exception n'est levee cote emetteur, et
`warn_on_full_buffer` ne gouverne qu'un avertissement.

La saturation n'a **pas pu etre atteinte** experimentalement sur la machine de
developpement, meme avec des tampons volontairement reduits a 1 Kio et 400 000
signaux emis. Ce point reste donc etabli par le contrat de l'API, non par la
mesure.

Son effet serait de toute facon benin ici : le descripteur reste lisible tant
qu'un seul octet subsiste, donc **le reveil n'est jamais perdu** ; seules des
causes surnumeraires le seraient, et la politique de C9 ne retient que la
premiere — celle qui est ecrite en tete, donc la moins exposee a un abandon qui
ne survient que sur un tampon deja rempli.

Compare a la course de verrou de l'architecture precedente, le risque est d'un
autre ordre : perdre une cause redondante contre bloquer le processus.

### Granularite d'horloge

Une attente peut rendre la main quelques millisecondes **avant** la duree
demandee, mesuree sur `time.monotonic()` : les deux ne derivent pas de la meme
source. Avance maximale observee sur la machine de developpement : 7,2 ms sur
60 mesures. Aucun test de C9 ne doit donc exiger `ecoule >= duree` au sens
strict.

### Compatibilite avec le runner C8, verifiee

Le `ReadSurfaceRunner` de C8, **sans aucune modification**, honore un arret
arme pendant son attente : il sort par `start → due_at → stop`, sans executer
de cycle superflu. La couture est donc compatible avec l'existant, et le seul
manque reste l'injection d'horloge dans `build_runtime`.

### Un signal pendant `run_due()` ne tronque pas le cycle

Verifie contre le runner reel : le signal survient au milieu de `run_due()`, le
gestionnaire vide n'y touche pas, l'octet est memorise, le cycle s'acheve
entierement, et l'arret est honore au point de controle suivant — journal
`start → due_at → run_due → stop`, un seul cycle.

Cette architecture **renforce** l'invariant C8 plutot que de l'affaiblir : le
signal ne peut pas interrompre un cycle, puisque rien dans le chemin de signal
ne touche a l'etat ; il est simplement mis en attente dans le descripteur.

## Decision arbitree — `SIGTERM`

`SIGTERM` doit :

1. armer la demande d'arret ;
2. reveiller l'attente interruptible ;
3. laisser le runner emprunter son **chemin normal** d'arret ;
4. permettre la fermeture MQTT et la publication `offline`, selon les garanties
   existantes de C7-C3A et C8 — ni plus, ni moins ;
5. etre classe comme **arret demande normal**.

Resultat logique du lanceur : **`0`**, si le cycle d'arret s'acheve normalement.

## Decision arbitree — `SIGINT`

`SIGINT` (Ctrl-C) doit produire exactement le meme comportement interne :
armement, reveil, chemin d'arret propre, fermeture et `offline`.

Sa semantique externe reste toutefois **identifiable comme interruption
utilisateur**. Resultat logique du lanceur : **`130`**, si l'arret propre
s'acheve normalement.

Cette decision **change deliberement** le comportement herite de C8. Jusqu'ici,
`Ctrl-C` levait `KeyboardInterrupt`, qui traversait `run()` sans declencher
`stop()` : ni `offline`, ni deconnexion propre. C9 remplace ce chemin brutal par
un arret gracieux, tout en conservant la convention `130` pour dire **qui** a
demande l'arret.

Ce que l'on gagne : la surface MQTT est refermee proprement sur Ctrl-C.
Ce que l'on paie : Ctrl-C n'est plus instantane — il devient une demande, honoree
au prochain point de controle. L'arbitrage est rendu, et il est assume.

## Panne

Une panne **n'est jamais** convertie en arret demande.

Les exceptions remontees par C8 traversent la couche de cycle de vie sans etre
masquees, traduites ni regroupees autrement que C8 ne l'a deja fait. Aucune
taxonomie nouvelle n'est creee. Le langage distingue deja ce qui doit l'etre :

| Situation | Resultat logique |
|---|---|
| Retour normal, sans signal | `0` |
| `SIGTERM` puis arret propre acheve | `0` |
| `SIGINT` puis arret propre acheve | `130` |
| Panne | l'exception remonte, non masquee |

`0`, `1` (exception non capturee, par le comportement natif de Python) et `130`
suffisent. Aucun code intermediaire n'est invente : aucun consommateur n'existe
dans le perimetre, et un code sans consommateur est un contrat gratuit a honorer
ensuite.

## Representation interne de l'etat d'arret

C9 a besoin de conserver deux choses, et rien de plus :

1. **l'etat** — l'arret est-il demande ;
2. **la cause**, lorsqu'elle provient d'un signal — `SIGINT` ou `SIGTERM`.

La cause est necessaire, et uniquement, parce que le resultat logique en depend
(`0` contre `130`). Elle n'est justifiee par aucun autre besoin.

C'est la plus petite representation suffisante. En particulier, C9 **ne**
construit **pas** : machine a etats generale, historique des transitions,
horodatage des demandes, priorites entre causes, ni file de signaux propre — la
file d'octets du descripteur joue ce role, et c'est elle qui garantit
naturellement que la premiere cause reste la cause.

L'etat et la cause ne sont ecrits **que sur le fil principal**, au moment du
drainage. Aucune synchronisation n'est donc requise entre le gestionnaire et le
reste : le gestionnaire n'ecrit rien.

Cette representation **n'est pas une API utilisateur publique**. Elle sert la
couche de cycle de vie et le calcul du resultat logique ; sa forme peut evoluer
sans engagement de compatibilite.

Contrainte de compatibilite avec C8 : l'objet doit satisfaire `StopSignal`,
c'est-a-dire exposer `is_set() -> bool`. C8 n'exige rien d'autre, et rien
d'autre ne doit lui etre impose.

## Attente interruptible

Un **meme descripteur** est ecrit par le niveau C au moment du signal et
surveille par l'horloge. C'est ce partage qui transforme un signal en reveil, et
pas seulement en intention. Le gestionnaire Python, lui, ne participe a rien.

L'horloge de C9 satisfait le protocole `Clock` — `now()`, `monotonic()`,
`sleep()` — et son `sleep(duration)` rend la main :

- soit a l'expiration de la duree demandee ;
- soit des que le descripteur devient lisible, c'est-a-dire des qu'un signal a
  ete recu — y compris **avant** l'entree dans l'attente, puisque l'octet y est
  memorise.

Le drainage arme l'etat d'arret et enregistre la cause. Il a lieu dans
`sleep()` **et** dans `is_set()` : la mesure a montre que le second est
indispensable, faute de quoi un arret passe inapercu lorsque C8 n'appelle pas
`sleep()`. Apres le reveil, C8 reconsulte deja le `StopSignal` : aucun mecanisme
supplementaire n'est requis, et le runner reste inchange.

Contraintes fermes :

- `SystemClock` **n'est pas modifiee** ;
- `ReadSurfaceRunner` **n'est pas modifie** ;
- les invariants de duree de `Clock` sont preserves a l'identique : les durees
  non finies et negatives restent refusees exactement comme le fait
  `boilerack.clock.check_duration`, afin que l'horloge reelle, l'horloge
  virtuelle et l'horloge interruptible refusent les memes entrees.

## Injection d'horloge dans `build_runtime`

`build_runtime()` construit aujourd'hui `SystemClock()` en dur et n'expose aucun
moyen de fournir une autre horloge. C9 leve cette limitation — c'est la
**seule** evolution de code C8 que l'analyse ait demontree necessaire.

Contraintes :

- **comportement historique inchange sans injection** ; le defaut reste
  `SystemClock` ;
- publisher et runner recoivent **exactement la meme instance**, injectee ou par
  defaut (invariant deja verrouille par C8) ;
- construire reste **sans connexion, sans socket et sans subprocess** ;
- **aucun autre refactor** de `runtime.py` : ni renommage, ni reorganisation, ni
  changement de signature au-dela de ce parametre.

## Gestionnaires de signaux

Invariants a preserver :

- les gestionnaires appartiennent a la **couche de cycle de vie**, jamais aux
  composants metier ; aucun module de `read_surface`, `adapters`, `transport`
  ou `core` n'installe quoi que ce soit ;
- **aucune installation a l'import** — importer un module de C9 ne doit rien
  poser ;
- installation **uniquement pendant l'execution controlee**, dans une portee
  explicite ;
- **restauration exacte** des gestionnaires precedents a la sortie, y compris
  lorsque le corps leve ;
- execution requise **depuis le fil principal** : `signal.signal` **et**
  `signal.set_wakeup_fd` echouent ailleurs, avec la meme `ValueError`, et
  l'echec doit rester explicite plutot que silencieux ;
- **aucun gestionnaire laisse en place** dans un processus hote apres la sortie ;
- le **descripteur de reveil** obeit aux memes regles que les gestionnaires :
  installe dans la portee, restaure a l'ancienne valeur rendue par
  `set_wakeup_fd`, et la paire de sockets refermee — y compris lorsque le corps
  leve. Aucun descripteur residuel ;
- les gestionnaires sont **vides**. Ils n'arment rien, n'ecrivent rien,
  n'acquierent aucun verrou. Leur seule raison d'etre est que le niveau C de
  CPython n'ecrit l'octet que si un gestionnaire Python existe : sous `SIG_IGN`,
  rien n'est ecrit.

Le processus est deja multi-fils avant meme que C9 n'intervienne :
`PahoMqttClient.connect()` appelle `loop_start()`, qui demarre un fil reseau. Le
fil principal reste celui qui execute la boucle et recoit les signaux ; la
contrainte ci-dessus n'est donc pas theorique.

### Double signal

C9 **n'implemente aucune** politique de « second Ctrl-C force la sortie ».

Un second signal reste **idempotent** vis-a-vis de l'etat d'arret : il n'ajoute
rien, ne reinitialise rien, ne change pas la cause deja enregistree. Toute
politique d'escalade forcee est hors perimetre tant qu'un besoin reel n'est pas
demontre.

Consequence a connaitre : si un `stop()` est long, un utilisateur impatient ne
disposera d'aucun moyen d'accelerer la sortie autre que ceux de son systeme.
C'est un manque assume, pas un oubli.

## Journalisation

C9 **n'appelle pas** `logging.basicConfig()` et ne configure la journalisation
d'aucune maniere.

Motif : C9 ne possede pas le point d'entree du programme. Une fonction appelee
programmatiquement qui configurerait globalement la journalisation du processus
hote imposerait sa politique a un appelant qui n'a rien demande.

Les composants existants continuent d'utiliser leurs journaux inchanges —
`boilerack.adapters.mqtt_paho` et `boilerack.core.engine` declarent chacun un
`logging.getLogger(__name__)`, pour douze sites d'appel au total, sans
gestionnaire configure. Le `lastResort` de la bibliotheque standard affiche donc
les avertissements sur `stderr`, et les messages `info` restent invisibles.
C'est le comportement actuel ; C9 ne le change pas.

La configuration de la journalisation appartient a C10, avec le vrai point
d'entree utilisateur. Aucun fichier de journalisation n'est modifie par C9.

## Latences

Deux grandeurs distinctes, a ne jamais confondre.

### Latence de reveil

Temps ecoule entre l'armement de l'arret et le retour de l'attente
interruptible.

C'est la **seule** propriete que C9 cherche a rendre courte et demontrable, et
la seule sur laquelle il produira une mesure.

Encore faut-il distinguer deux choses que l'on confond aisement :

- **la preuve fonctionnelle** — une attente demandee pour une duree longue est
  effectivement interrompue **avant son echeance normale**. C'est binaire, c'est
  stable, et c'est cela que les tests affirment ;
- **la mesure informative** — la latence observee, rapportee en millisecondes.
  Elle renseigne, elle n'engage pas. Aucun seuil numerique contractuel n'est
  fixe : il dependrait de la charge de la machine d'integration, et une
  promesse en millisecondes tenue par GitHub Actions ne serait pas une promesse.

Les bornes temporelles qui apparaissent dans les tests sont des **garde-fous**
destines a ne jamais bloquer une execution. Elles ne sont pas des bornes
normatives, et ne doivent jamais etre lues comme telles.

### Latence totale de sortie

Temps ecoule entre la reception du signal et le retour de la fonction de cycle
de vie. Elle inclut potentiellement :

- la latence de reveil ;
- le travail deja engage, dont un `run_due()` **deja commence**, que le runner
  ne tronque pas ;
- l'arret du publisher et la fermeture MQTT ;
- toute duree de `stop()`.

**C9 ne lui attribue aucune borne**, faute de preuve. Ces durees dependent du
publisher, du reseau et du broker, qu'aucun contrat ne borne.

Aucune formulation de ce projet ne doit laisser entendre que `SIGINT` ou
`SIGTERM` garantit « un arret du processus complet en moins de X secondes ».
Ce qui est vise est plus modeste et verifiable : le signal est **vu vite**, et
il emprunte ensuite le chemin d'arret que C8 garantit deja.

## API livree

Un module unique : `src/boilerack/lifecycle.py`. Rien n'a ete disperse.

| Symbole | Role |
|---|---|
| `SIGNALS_SURVEILLES` | `(SIGINT, SIGTERM)` — les deux seuls signaux traduits en demande d'arret |
| `CODE_ARRET_NORMAL` / `CODE_INTERRUPTION` | `0` et `130`, resultats **logiques**, pas des codes de sortie de processus |
| `SignalStop` | Etat d'arret. `is_set()` **draine puis repond** ; `cause` rend la premiere cause ; `signaux_ignores` expose les octets etrangers |
| `WakeupClock` | Horloge satisfaisant `Clock`. `now()` / `monotonic()` delegues a une horloge de base ; `sleep()` attend sur le descripteur |
| `Wakeup` | Paire gelee `(stop, clock)`, construite depuis **le meme** descripteur |
| `SignalScope` | Portee : installe et retire integralement gestionnaires, descripteur de reveil et sockets |
| `resultat_logique(cause)` | `130` si `SIGINT`, `0` sinon |
| `run_lifecycle(config, *, surveilles=…)` | Assemble, execute, rend le resultat logique |

`SignalStop` et `WakeupClock` sont construits ensemble par la portee, a partir du
meme descripteur : il est **structurellement impossible** qu'ils en surveillent
deux differents. Ce n'est pas un invariant a tester, c'est un invariant a ne pas
pouvoir violer.

### `is_set()` draine — et c'est ecrit dans le code

La docstring de `SignalStop.is_set` le dit sans detour : ce n'est pas une
lecture passive, elle consomme le descripteur avant de repondre. Le motif y est
rappele — sans cela, un arret passerait inapercu lorsque C8 n'appelle pas
`sleep()`, ce qui arrive quand l'echeance suivante est deja depassee.

### Signaux etrangers

`signal.set_wakeup_fd` est **global au processus** : un gestionnaire pose par
l'hote pour un autre signal ecrit lui aussi dans notre descripteur. Le
comportement retenu, explicite et teste : ces octets sont **draines et
ignores** — ils n'arment pas l'arret et ne fournissent aucune cause. Ils sont
seulement recenses dans `signaux_ignores`, pour l'observabilite.

Consequence assumee : un tel signal **reveille** neanmoins l'attente. Le runner
reconsulte l'etat, ne trouve pas d'arret, et rappelle `run_due()`, qui ne trouve
alors rien de du. Aucune reprise d'attente n'est tentee : ce serait une
politique, et rien ne l'exige.

### Drainage ultime

`run_lifecycle` draine une derniere fois **apres** le retour du runner, avant de
conclure. Sans cela, le resultat logique dependrait du nombre d'interrogations
faites par le runner, et un signal recu pendant `stop()` serait perdu. Ce defaut
a ete introduit puis attrape par un test avant d'etre corrige ; la mutation
correspondante figure au tableau plus bas.

### Politique d'erreurs de la portee

Alignee sur celle de C8, et non inventee :

| Situation | Comportement |
|---|---|
| Corps normal, restauration normale | rien de particulier |
| Corps en echec, restauration reussie | l'exception du corps poursuit sa route, **identite preservee** |
| Corps normal, restauration en echec | l'erreur de restauration remonte telle quelle |
| Les deux en echec | un **groupe** portant **[corps, restauration]**, dans cet ordre |

La propriete tenue est semantique, non typologique : **le corps et la
restauration sont tous deux preserves, dans cet ordre, via le type de groupe
approprie aux exceptions contenues.**

Le groupe est construit avec `BaseExceptionGroup`, jamais avec
`ExceptionGroup`. Motif etabli par l'audit puis reproduit : un corps peut sortir
sur une `BaseException` — `SystemExit`, par exemple —, et `ExceptionGroup`
refuse alors de l'imbriquer en levant `TypeError: Cannot nest BaseExceptions in
an ExceptionGroup`. L'exception d'origine serait **perdue**, remplacee par une
erreur de typage sans rapport.

Le cas courant reste inchange, et cela a ete verifie plutot que suppose :
lorsque tous les membres sont des `Exception`, `BaseExceptionGroup` **rend un
`ExceptionGroup`**. Le type observe est donc `ExceptionGroup` pour deux erreurs
ordinaires, et `BaseExceptionGroup` seulement lorsqu'un membre l'exige. Un
`except ExceptionGroup` continue d'attraper le premier cas, et ne peut pas
attraper le second — ce qui est correct : une `BaseException` ne doit pas etre
capturee par inadvertance.

La restauration tente **toutes** ses etapes — selecteur, gestionnaires,
descripteur, sockets — meme si l'une echoue, et ne groupe qu'ensuite. Un echec
partiel ne doit pas laisser le reste installe.

La meme politique gouverne l'**entree**, et pas seulement la sortie :

| Situation a l'entree | Comportement |
|---|---|
| Echec partiel, nettoyage reussi | l'erreur d'entree remonte **telle quelle**, sans groupe |
| Echec partiel, nettoyage en echec | un **groupe** portant **[entree, nettoyage]**, dans cet ordre |

Si la pose d'un gestionnaire echoue alors que le descripteur de reveil est deja
installe, `__enter__` retire tout ce qui a ete pose avant de laisser l'erreur
remonter. Et si ce nettoyage echoue a son tour, les deux erreurs sont
conservees — comme a la sortie, et par le meme mecanisme.

Le comportement anterieur a ete **reproduit avant d'etre corrige** : l'erreur de
nettoyage devenait l'exception principale, et l'erreur d'entree ne survivait que
dans `__context__`. C'etait vrai aussi bien pour une `OSError` que pour un
`SystemExit`. Des tests d'injection de panne verrouillent desormais les quatre
combinaisons.

### Fil principal

`SignalScope.__enter__` verifie le fil principal **avant toute allocation** et
leve une `RuntimeError` explicite. La contrainte n'est pas contournee : elle est
seulement annoncee plus tot et plus clairement que la `ValueError` que
`signal.signal` aurait fini par lever, et rien n'est alloue en cas de refus.

## Architecture retenue

```
couche de cycle de vie (C9)
+------------------------------------------------------+
| portee de signaux                                    | installe SIGINT/SIGTERM
|   gestionnaire Python : VIDE                         | + wakeup fd,
|   niveau C de CPython --> ecrit 1 octet (n_signal)   | restaure tout a la
|                            dans le descripteur       | sortie, meme sur levee
|                                    |                 |
|   paire de sockets locales <-------+                 | jamais publiee,
|        |            |                                | refermee a la sortie
|        |            +--> drainage --> etat arme      |
|        |                             + 1re cause     |
|   horloge : sleep(d) = attente sur le descripteur    | rend la main des que
|                                    |                 | l'octet est present
|   etat.is_set() draine aussi       |                 | (meme si sleep() n'a
|                                    |                 |  pas ete appele)
|   build_runtime(config, stop, clock=...)             |
|                                    |                 |
|   runtime.runner.run()   bloquant  |                 |
|                                    |                 |
|   retour normal            --> 0                     |
|   premiere cause = SIGINT  --> 130                   |
|   exception                --> remontee, non masquee |
+------------------------------------------------------+
                             |
                    C8 inchange en dessous
               (hors le parametre d'horloge)
```

Rien, dans le chemin parcouru par un signal, n'acquiert de verrou : le
gestionnaire Python ne fait rien, et l'ecriture de l'octet appartient au niveau
C. C'est ce qui distingue cette architecture de celle qui a ete rejetee.

Flux de controle : la fonction de cycle de vie ouvre la portee de signaux,
construit le runtime avec l'etat d'arret et l'horloge interruptible partagee,
appelle `run()`, puis calcule le resultat logique a partir de la cause
enregistree. La portee de signaux restaure les gestionnaires precedents en
sortant, que `run()` ait rendu la main normalement ou leve.

## Inclus — liste fermee

1. Un etat d'arret concret, arme par drainage du descripteur, compatible avec
   `StopSignal`.
2. La conservation minimale de la cause `SIGINT` / `SIGTERM`, tiree du premier
   octet consomme.
3. Une attente / horloge interruptible compatible avec `Clock`, fondee sur une
   paire de sockets locales et un selecteur.
4. L'injection optionnelle de l'horloge dans `build_runtime`.
5. L'installation et la restauration controlees des gestionnaires `SIGINT` /
   `SIGTERM` **et** du descripteur de reveil, ainsi que la creation et la
   fermeture de la paire de sockets locales.
6. Une fonction Python de cycle de vie prenant un `RuntimeConfig` **deja
   construit**.
7. L'arret gracieux par le chemin C8 existant.
8. Le resultat logique : normal ou `SIGTERM` propre → `0` ; `SIGINT` propre →
   `130`.
9. La preservation des exceptions en cas de panne.
10. La documentation des limites et de la preuve POSIX.

## Exclus — liste fermee

CLI · `argparse`, Click, Typer ou equivalent · `[project.scripts]` ·
`__main__.py` · lecture de variables d'environnement · fichier TOML / YAML /
JSON de configuration · noms publics de configuration · configuration globale de
la journalisation · reconnexion MQTT · strategie reseau · systemd · packaging
final · installation · deploiement · Pi reel · broker reel · `vclient` reel ·
`vcontrold` reel · chaudiere · Home Assistant · ecriture chaudiere · traitement
des trois champs de configuration morts (`command_topic`, `ack_topic_prefix`,
`write_timeout_s`) · politique de second signal force · refactor large de C8.

## Preuves a produire

### Etat d'arret

- initialement non arme ;
- armement **idempotent** : plusieurs signaux laissent le meme etat et la meme
  cause — la premiere ;
- `is_set()` compatible avec ce que C8 consomme, et **drainant** ;
- la cause utile au resultat final est conservee, et elle seule ;
- la premiere cause est verifiee dans les **deux** ordres d'arrivee.

### Attente interruptible

- duree normale respectee lorsque aucun signal n'est survenu ;
- reveil anticipe lorsqu'un signal survient pendant l'attente ;
- reveil **immediat** lorsqu'un signal est survenu AVANT l'entree dans
  l'attente : l'octet memorise doit suffire ;
- **meme descripteur partage** entre l'etat d'arret et l'attente — deux
  descripteurs distincts doivent etre detectes comme un defaut ;
- durees invalides traitees selon les invariants de `Clock` : non finies et
  negatives refusees ;
- `now()` et `monotonic()` restent conformes au protocole.

### Chemin de signal

- le gestionnaire installe est **vide** : il n'arme rien et n'acquiert aucun
  verrou. Un gestionnaire qui appellerait une primitive de synchronisation doit
  etre detecte comme un defaut ;
- sous `SIG_IGN`, aucun octet n'est ecrit : le gestionnaire vide est donc
  necessaire, et son absence doit etre detectee ;
- un signal recu **pendant** `run_due()` ne tronque pas le cycle et est honore
  au point de controle suivant, sans cycle superflu.

### `build_runtime`

- sans injection, l'horloge par defaut reste `SystemClock` — le test C8 existant
  doit rester vert sans modification de son intention ;
- avec injection, l'horloge fournie est bien celle utilisee ;
- **la meme instance** est partagee par le publisher et le runner, dans les deux
  cas ;
- construire n'ouvre toujours ni socket ni processus.

### Signaux

- les gestionnaires sont installes dans la portee ;
- les gestionnaires precedents sont **restaures exactement**, y compris lorsque
  le corps de la portee leve ;
- `SIGINT` arme l'etat avec la cause `SIGINT` ;
- `SIGTERM` arme l'etat avec la cause `SIGTERM` ;
- l'installation hors fil principal **echoue explicitement** ;
- **aucun effet de bord a l'import** du module.

### Cycle de vie

- retour normal sans signal → `0` ;
- `SIGTERM` puis arret propre → `0` ;
- `SIGINT` puis arret propre → `130` ;
- panne → l'exception remonte, non masquee, identite preservee ;
- erreur pendant `stop()` → la politique C8 est preservee telle quelle, y compris
  le regroupement lors d'un double echec, `BaseException` comprise.

### Preuve POSIX

Une preuve reelle, en sous-processus, sur Linux — donc en integration continue,
ou le depot execute deja Python 3.11, 3.12 et 3.13 sur `ubuntu-latest` :

- lancement d'un processus Python qui exerce les composants de **production** —
  `SignalScope`, `WakeupClock`, `SignalStop`, `resultat_logique` ;
- envoi d'un `SIGTERM` reel ;
- constatation du reveil ;
- constatation de l'arret ;
- verification du code de sortie ;
- mesure de la **latence de reveil**, et d'elle seule.

**Limite de plateforme, assumee.** La machine de developpement est sous Windows.
Il y a ete mesure que `SIGTERM` n'interrompt pas une attente sur etat quand le
fil principal y est bloque, alors que `SIGINT` le fait. Windows ne permet donc
pas de demontrer ce que la cible garantit. La preuve `SIGTERM` est conditionnee
a POSIX et ne sera reellement exercee qu'en integration continue. Ce document ne
pretend rien de plus.

Ce que la caracterisation a **deja** pu etablir localement, et ce qu'elle n'a
pas pu etablir, precisement :

| Etabli localement | Non etabli localement |
|---|---|
| le script enfant compile, demarre et annonce sa disponibilite | la delivrance reelle de `SIGTERM` |
| le harnais — sous-processus, fil lecteur, file, delais durs — fonctionne | le reveil par `SIGTERM` |
| `SIGINT` arme l'etat et ecourte une attente, en processus | — |
| `time.sleep` n'est PAS ecourte par un gestionnaire pose-drapeau | — |

Le saut de plateforme est rendu **visible et verifiable** par un test dedie qui
constate le motif du saut, plutot que par un simple `skipif` silencieux. Aucune
preuve POSIX n'est simulee.

### Mutations discriminantes

Au minimum, les mutations suivantes doivent etre tuees :

Campagne executee : **15 mutations, 15 tuees, aucune survivante**, fichiers de
production restaures a l'octet pres (SHA-256 verifie). Le detail figure au
rapport du lot.

| # | Mutation | Ce qu'elle casse |
|---|---|---|
| 1 | Aucun gestionnaire installe, ou `SIG_IGN` | aucun octet n'est ecrit : le signal devient sans effet |
| 2 | Descripteur different entre le wakeup fd et l'attente | l'octet est ecrit, mais rien ne reveille |
| 3 | Attente non interruptible (retour a `time.sleep`) | reproduit exactement le piege PEP 475 |
| 4 | Gestionnaires non restaures a la sortie | contamination du processus hote |
| 4 bis | Wakeup fd ou paire de sockets non restaures / non fermes | descripteur residuel, contamination du processus hote |
| 5 | `SIGINT` classe en succes `0` | perte de la semantique d'interruption |
| 6 | `SIGTERM` classe `130` | arret normal presente comme une interruption |
| 7 | Panne convertie en succes | une panne passerait pour un arret demande |
| 8 | Horloges differentes pour publisher et runner | rupture de l'invariant C8 |
| 9 | `is_set()` ne draine pas | arret manque quand l'echeance est deja depassee : cycles superflus, voire boucle sans fin |
| 10 | Le dernier octet consomme ecrase la cause | resultat logique non deterministe entre `0` et `130` |
| 11 | Le gestionnaire arme l'etat lui-meme (retour a l'architecture rejetee) | reintroduit le blocage par reentrance de verrou |
| 12 | Pas de drainage ultime dans `run_lifecycle` | un signal recu apres le dernier point de controle est perdu ; le resultat depend du nombre d'interrogations du runner |
| 13 | Le refus hors fil principal disparait | echec tardif et obscur au lieu d'un refus clair |
| 14 | Les signaux etrangers arment l'arret | un signal de l'hote arreterait le pont |
| 15 | Retour a `ExceptionGroup` pour le double echec | `TypeError` sur un corps `BaseException` : l'origine est perdue |
| 16 | Suppression du nettoyage dans `__enter__` | une entree echouant a mi-chemin laisserait descripteur, gestionnaire et sockets installes |
| 17 | A l'entree, le nettoyage en echec remplace l'erreur d'origine | l'erreur d'entree n'est plus conservee que dans `__context__` |
| 18 | Ordre inverse dans le groupe d'entree | l'erreur de nettoyage passerait pour la cause premiere |

## Fichiers

**Nouveaux** — `src/boilerack/lifecycle.py` ; `tests/test_lifecycle.py` ; le
present document.

**Modifies** — `src/boilerack/runtime.py`, pour le seul parametre d'horloge
optionnel, reserve aux mots-cles et de defaut inchange ;
`tests/test_runtime.py`, pour le couvrir ; `docs/design/c8-composition-root.md`,
pour deux renvois documentaires.

**Non modifies** — `pyproject.toml`, `clock.py`, `read_surface/`, `adapters/`,
`transport/`, `core/`, `README.md`, et les contrats C4, C5 et C7.

Aucune dependance n'est ajoutee : la bibliotheque standard suffit — `signal`,
`socket`, `selectors`, et rien de plus.

## Renvois

- La section « Latence d'arret » de `c8-composition-root.md` decrit l'etat de C8
  seul, ou aucun reveil n'existe. Elle reste exacte pour ce qu'elle decrit.
- Le point d'entree installe, la source de configuration et la configuration de
  la journalisation relevent de C10.
