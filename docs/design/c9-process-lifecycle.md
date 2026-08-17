# C9 — Cycle de vie du processus et arrêt sur signal

Document d'architecture, écrit **avant** l'implémentation puis complété par
elle. Il fixe la frontière du lot, les décisions arbitrées, les invariants que
le code préserve, les preuves exécutées, et l'API effectivement livrée.

## Objectif normatif

> C9 permet à du code Python appelant de lancer un `Runtime` assemblé et de
> transformer `SIGINT` ou `SIGTERM` en **demande d'arrêt propre**. La demande
> réveille l'attente du runner afin qu'elle soit prise en compte à son prochain
> point de contrôle. C9 ne promet **aucune borne** sur la durée totale de sortie
> lorsqu'un travail est déjà engagé ou lorsque `stop()` est en cours.

Une seule propriété sera bornée et démontrée : la **latence de réveil** de
l'attente interruptible, sous les conditions effectivement testées. Voir
« Latences » plus bas.

## Ce que C9 n'est pas

C9 **n'est pas** le point d'entrée du programme. Il ne fournit ni commande, ni
lecture de configuration, ni nom de clé publique. Il offre une **fonction Python
de cycle de vie**, appelée par un programme qui, lui, viendra plus tard (C10).

Cette distinction n'est pas cosmétique : elle détermine plusieurs décisions du
présent document, notamment le refus de configurer la journalisation.

## Point de départ — ce que C8 fournit déjà

```
build_runtime(config: RuntimeConfig, stop: StopSignal) -> Runtime
Runtime(publisher: ReadSurfacePublisher, runner: ReadSurfaceRunner)
ReadSurfaceRunner(publisher, clock: Clock, stop: StopSignal).run() -> None
StopSignal : Protocol, is_set() -> bool
```

Le runner consulte la demande d'arrêt à deux moments par cycle : à l'entrée de
la boucle, et **après l'attente**, avant tout travail. Ce second point de
contrôle existe déjà, il est testé, et C9 s'appuie dessus sans le modifier.

C8 garantit par ailleurs : `start()` une fois ; ordre
`is_set → due_at → attente → is_set → run_due` ; jamais de sommeil négatif ;
aucun rattrapage ; `stop()` toujours tenté sur le chemin `Exception` ; identités
d'exception préservées ; `ExceptionGroup` en cas de double échec.

## Le problème établi

`SystemClock.sleep()` délègue à `time.sleep()`. Or CPython, depuis PEP 475,
**reprend** `time.sleep()` après l'exécution d'un gestionnaire de signal qui ne
lève pas d'exception.

Conséquence, mesurée lors du cadrage : un gestionnaire qui se contente d'armer
un drapeau **ne réveille pas** l'attente. Le processus continuerait de dormir
jusqu'à l'échéance prévue.

| Mécanisme | Durée demandée | Durée observée | Réveil |
|---|---|---|---|
| `time.sleep` + gestionnaire pose-drapeau | 3.00 s | 3.00 s | **non** |
| `time.sleep` + gestionnaire par défaut (lève `KeyboardInterrupt`) | 3.00 s | 0.50 s | oui, par exception |
| attente sur état + armement depuis un autre fil | 3.00 s | 0.50 s | **oui** |
| attente sur état + gestionnaire `SIGINT` pose-drapeau | 2.00 s | 0.50 s | **oui** |

Mesures faites sur Windows / CPython 3.14, hors dépôt. Elles établissent le
mécanisme ; elles ne valent **pas** preuve du comportement sur la plateforme
cible. Voir « Preuve POSIX ».

Les deux dernières lignes montrent qu'une attente sur état **peut** être
réveillée. Elles ne suffisent pourtant pas à retenir cette solution : la section
suivante expose pourquoi armer l'état depuis le gestionnaire a été rejeté.

C9 a donc besoin d'une **couture d'attente interruptible**. Ce n'est pas un
confort : sans elle, armer un drapeau depuis un gestionnaire de signal serait un
geste sans effet observable avant la prochaine échéance.

## Faits établis par la caractérisation

Ces faits sont mesurés, pas supposés. Ils ont été établis **avant** tout code
de production, et restent verrouillés par `tests/test_lifecycle.py`.

Une première caractérisation avait retenu `threading.Event`, armé depuis le
gestionnaire de signal. Une contre-caractérisation ciblée l'a **invalidée**. Le
mécanisme retenu est donc différent, et la section qui suit expose d'abord
pourquoi.

### Pourquoi `threading.Event` armé depuis le gestionnaire est rejeté

`Event.__init__` construit `Condition(Lock())` : un verrou **non réentrant**.
`set()` le prend ; `is_set()` ne prend **aucun** verrou. Si un second signal,
de numéro différent, survient pendant l'exécution de `set()` et rappelle
`set()` sur le même fil, celui-ci se bloque **définitivement**.

Ce défaut n'est pas théorique. Il a été **reproduit de façon déterministe**,
avec deux vrais gestionnaires et sans aucun verrou pris à la main : un `Event`
instrumenté délivre le second signal à l'intérieur même de `set()`, entre
l'acquisition du verrou et la pose du drapeau. Le processus ne rend jamais la
main ; seul un délai dur permet de le constater.

L'atténuation envisagée — garder le gestionnaire par `if not etat.is_set()` —
a été testée et **ne supprime pas le blocage**. La raison est simple, et elle
avait été manquée : le drapeau n'est posé qu'**après** l'acquisition du verrou,
donc la garde laisse passer précisément dans la fenêtre qu'elle était censée
fermer. Les deux variantes, avec et sans garde, se bloquent.

Le critère de décision est ici sans ambiguïté : un blocage connu **dans le
chemin d'arrêt lui-même** contredit l'objet du lot. Aucune probabilité faible
ne rachète cela.

`threading.Event` conserve par ailleurs toutes ses qualités — armement
idempotent, attente passive (moins de 1 ms de CPU pour 1 s d'attente), réveil
anticipé — et reste parfaitement utilisable **tant qu'aucun gestionnaire de
signal n'appelle `set()`**. C'est l'usage depuis le gestionnaire qui est
rejeté, pas la primitive.

### Mécanisme retenu — réveil par descripteur

`signal.set_wakeup_fd` fait écrire, **par le niveau C de CPython**, un octet
égal au numéro du signal dans un descripteur choisi. Le gestionnaire Python n'y
participe pas : il peut être entièrement **vide**. Aucun verrou n'est donc pris
dans le chemin de signal, et la course de réentrance devient structurellement
impossible.

Caractéristiques établies par la mesure :

| Point | Constat |
|---|---|
| Fil principal | requis, `ValueError` sinon — même contrainte que `signal.signal`, aucune nouvelle |
| Valeur de retour | le descripteur précédent, ou `-1` si aucun ; c'est ce qui permet une restauration exacte |
| Restauration | `set_wakeup_fd(precedent)` restitue l'état antérieur |
| Contenu écrit | un octet, égal au numéro du signal (`2` pour `SIGINT`, `15` pour `SIGTERM`) |
| Ordre | préserve : `SIGINT` puis `SIGTERM` donne `[2, 15]`, l'inverse donne `[15, 2]` |
| Gestionnaire Python | **indispensable** : sous `SIG_IGN`, aucun octet n'est écrit |
| Descripteur bloquant | accepté sans erreur, non vérifié — à la charge de l'appelant |
| Mémorisation | le descripteur reste lisible jusqu'au drainage ; une attente ouverte après coup rend la main immédiatement |

**MÉCANISME C9 RETENU : WAKEUP_FD.**

### Transport — paire de sockets locales

`os.pipe()` et `socket.socketpair()` sont tous deux acceptés par
`set_wakeup_fd`, et tous deux fonctionnent : l'octet est bien écrit dans l'un
comme dans l'autre. Le tri se fait sur l'**attente**, pas sur l'écriture.

Hors POSIX, un tube est *enregistrable* auprès d'un sélecteur sans erreur, mais
l'attente elle-même échoue — `select` n'y connaît que les sockets. Une paire de
sockets locales est donc le seul transport valable sur les deux familles de
plateformes, et c'est celui qui est retenu.

**Ce n'est pas une connexion réseau.** `socket.socketpair()` crée deux
extrémités locales appariées, jamais publiées, jamais accessibles depuis
l'extérieur. L'invariant C8 — `build_runtime()` n'ouvre aucune socket — porte
sur la construction de l'assemblage et reste intact : cette paire est créée par
la couche de cycle de vie, pendant son exécution, et refermée à sa sortie.
Confondre les deux reviendrait à confondre un tuyau interne avec un port
ouvert.

### Première cause conservée

L'ordre des octets suffit : **le premier octet consommé est la première cause**.
Vérifié dans les deux sens. Aucune priorité n'est inventée, aucun verrou n'est
requis, et les octets suivants sont drainés sans modifier la cause retenue.

`dict.setdefault` reste utilisable pour matérialiser « la première écriture
gagne » du côté du lecteur, mais ce n'est plus qu'un détail d'implémentation :
la garantie vient de la file d'octets elle-même.

### Le drainage doit avoir lieu dans `is_set()`

Point découvert en confrontant la couture au runner C8 réel, et **décisif**.

Si seul `sleep()` drainait le descripteur, l'arrêt ne serait pas vu lorsque C8
n'appelle pas `sleep()` — ce qui arrive quand l'échéance suivante est déjà
dépassée, comportement normal et déjà testé de C8. Mesure : **trois cycles
exécutés au lieu d'un seul**, et une boucle sans fin si l'échéance reste
indéfiniment dépassée.

Avec un drainage dans `is_set()`, le même scénario sort après **un seul**
cycle. C'est donc `is_set()` qui doit drainer : il devient le point unique où
l'état d'arrêt est rafraîchi, quel que soit le chemin emprunté par le runner.

Conséquence à assumer : `is_set()` n'est plus une simple lecture, il consomme
le descripteur. C'est acceptable parce qu'il n'est appelé que sur le fil
principal, par le runner, et que la lecture est non bloquante.

### Saturation

Lorsque le tampon du descripteur est plein, CPython **abandonne** les octets
excédentaires ; aucune exception n'est levée côté émetteur, et
`warn_on_full_buffer` ne gouverne qu'un avertissement.

La saturation n'a **pas pu être atteinte** expérimentalement sur la machine de
développement, même avec des tampons volontairement réduits à 1 Kio et 400 000
signaux émis. Ce point reste donc établi par le contrat de l'API, non par la
mesure.

Son effet serait de toute façon bénin ici : le descripteur reste lisible tant
qu'un seul octet subsiste, donc **le réveil n'est jamais perdu** ; seules des
causes surnuméraires le seraient, et la politique de C9 ne retient que la
première — celle qui est écrite en tête, donc la moins exposée à un abandon qui
ne survient que sur un tampon déjà rempli.

Comparé à la course de verrou de l'architecture précédente, le risque est d'un
autre ordre : perdre une cause redondante contre bloquer le processus.

### Granularité d'horloge

Une attente peut rendre la main quelques millisecondes **avant** la durée
demandée, mesurée sur `time.monotonic()` : les deux ne dérivent pas de la même
source. Avance maximale observée sur la machine de développement : 7,2 ms sur
60 mesures. Aucun test de C9 ne doit donc exiger `ecoule >= duree` au sens
strict.

### Compatibilité avec le runner C8, vérifiée

Le `ReadSurfaceRunner` de C8, **sans aucune modification**, honore un arrêt
armé pendant son attente : il sort par `start → due_at → stop`, sans exécuter
de cycle superflu. La couture est donc compatible avec l'existant, et le seul
manque reste l'injection d'horloge dans `build_runtime`.

### Un signal pendant `run_due()` ne tronque pas le cycle

Vérifié contre le runner réel : le signal survient au milieu de `run_due()`, le
gestionnaire vide n'y touche pas, l'octet est mémorisé, le cycle s'achève
entièrement, et l'arrêt est honoré au point de contrôle suivant — journal
`start → due_at → run_due → stop`, un seul cycle.

Cette architecture **renforce** l'invariant C8 plutôt que de l'affaiblir : le
signal ne peut pas interrompre un cycle, puisque rien dans le chemin de signal
ne touche à l'état ; il est simplement mis en attente dans le descripteur.

## Décision arbitrée — `SIGTERM`

`SIGTERM` doit :

1. armer la demande d'arrêt ;
2. réveiller l'attente interruptible ;
3. laisser le runner emprunter son **chemin normal** d'arrêt ;
4. permettre la fermeture MQTT et la publication `offline`, selon les garanties
   existantes de C7-C3A et C8 — ni plus, ni moins ;
5. être classé comme **arrêt demandé normal**.

Résultat logique du lanceur : **`0`**, si le cycle d'arrêt s'achève normalement.

## Décision arbitrée — `SIGINT`

`SIGINT` (Ctrl-C) doit produire exactement le même comportement interne :
armement, réveil, chemin d'arrêt propre, fermeture et `offline`.

Sa sémantique externe reste toutefois **identifiable comme interruption
utilisateur**. Résultat logique du lanceur : **`130`**, si l'arrêt propre
s'achève normalement.

Cette décision **change délibérément** le comportement hérité de C8. Jusqu'ici,
`Ctrl-C` levait `KeyboardInterrupt`, qui traversait `run()` sans déclencher
`stop()` : ni `offline`, ni déconnexion propre. C9 remplace ce chemin brutal par
un arrêt gracieux, tout en conservant la convention `130` pour dire **qui** a
demandé l'arrêt.

Ce que l'on gagne : la surface MQTT est refermée proprement sur Ctrl-C.
Ce que l'on paie : Ctrl-C n'est plus instantané — il devient une demande, honorée
au prochain point de contrôle. L'arbitrage est rendu, et il est assumé.

## Panne

Une panne **n'est jamais** convertie en arrêt demandé.

Les exceptions remontées par C8 traversent la couche de cycle de vie sans être
masquées, traduites ni regroupées autrement que C8 ne l'a déjà fait. Aucune
taxonomie nouvelle n'est créée. Le langage distingue déjà ce qui doit l'être :

| Situation | Résultat logique |
|---|---|
| Retour normal, sans signal | `0` |
| `SIGTERM` puis arrêt propre achevé | `0` |
| `SIGINT` puis arrêt propre achevé | `130` |
| Panne | l'exception remonte, non masquée |

`0`, `1` (exception non capturée, par le comportement natif de Python) et `130`
suffisent. Aucun code intermédiaire n'est inventé : aucun consommateur n'existe
dans le périmètre, et un code sans consommateur est un contrat gratuit à honorer
ensuite.

## Représentation interne de l'état d'arrêt

C9 a besoin de conserver deux choses, et rien de plus :

1. **l'état** — l'arrêt est-il demandé ;
2. **la cause**, lorsqu'elle provient d'un signal — `SIGINT` ou `SIGTERM`.

La cause est nécessaire, et uniquement, parce que le résultat logique en dépend
(`0` contre `130`). Elle n'est justifiée par aucun autre besoin.

C'est la plus petite représentation suffisante. En particulier, C9 **ne**
construit **pas** : machine à états générale, historique des transitions,
horodatage des demandes, priorités entre causes, ni file de signaux propre — la
file d'octets du descripteur joue ce rôle, et c'est elle qui garantit
naturellement que la première cause reste la cause.

L'état et la cause ne sont écrits **que sur le fil principal**, au moment du
drainage. Aucune synchronisation n'est donc requise entre le gestionnaire et le
reste : le gestionnaire n'écrit rien.

Cette représentation **n'est pas une API utilisateur publique**. Elle sert la
couche de cycle de vie et le calcul du résultat logique ; sa forme peut évoluer
sans engagement de compatibilité.

Contrainte de compatibilité avec C8 : l'objet doit satisfaire `StopSignal`,
c'est-à-dire exposer `is_set() -> bool`. C8 n'exige rien d'autre, et rien
d'autre ne doit lui être imposé.

## Attente interruptible

Un **même descripteur** est écrit par le niveau C au moment du signal et
surveille par l'horloge. C'est ce partage qui transforme un signal en réveil, et
pas seulement en intention. Le gestionnaire Python, lui, ne participe à rien.

L'horloge de C9 satisfait le protocole `Clock` — `now()`, `monotonic()`,
`sleep()` — et son `sleep(duration)` rend la main :

- soit à l'expiration de la durée demandée ;
- soit dès que le descripteur devient lisible, c'est-à-dire dès qu'un signal a
  été reçu — y compris **avant** l'entrée dans l'attente, puisque l'octet y est
  mémorisé.

Le drainage arme l'état d'arrêt et enregistre la cause. Il a lieu dans
`sleep()` **et** dans `is_set()` : la mesure a montré que le second est
indispensable, faute de quoi un arrêt passe inaperçu lorsque C8 n'appelle pas
`sleep()`. Après le réveil, C8 reconsulte déjà le `StopSignal` : aucun mécanisme
supplémentaire n'est requis, et le runner reste inchangé.

Contraintes fermes :

- `SystemClock` **n'est pas modifiée** ;
- `ReadSurfaceRunner` **n'est pas modifié** ;
- les invariants de durée de `Clock` sont préservés à l'identique : les durées
  non finies et négatives restent refusées exactement comme le fait
  `boilerack.clock.check_duration`, afin que l'horloge réelle, l'horloge
  virtuelle et l'horloge interruptible refusent les mêmes entrées.

## Injection d'horloge dans `build_runtime`

`build_runtime()` construit aujourd'hui `SystemClock()` en dur et n'expose aucun
moyen de fournir une autre horloge. C9 lève cette limitation — c'est la
**seule** évolution de code C8 que l'analyse ait démontrée nécessaire.

Contraintes :

- **comportement historique inchangé sans injection** ; le défaut reste
  `SystemClock` ;
- publisher et runner reçoivent **exactement la même instance**, injectée ou par
  défaut (invariant déjà verrouillé par C8) ;
- construire reste **sans connexion, sans socket et sans subprocess** ;
- **aucun autre refactor** de `runtime.py` : ni renommage, ni réorganisation, ni
  changement de signature au-delà de ce paramètre.

## Gestionnaires de signaux

Invariants à préserver :

- les gestionnaires appartiennent à la **couche de cycle de vie**, jamais aux
  composants métier ; aucun module de `read_surface`, `adapters`, `transport`
  ou `core` n'installe quoi que ce soit ;
- **aucune installation à l'import** — importer un module de C9 ne doit rien
  poser ;
- installation **uniquement pendant l'exécution contrôlée**, dans une portée
  explicite ;
- **restauration exacte** des gestionnaires précédents à la sortie, y compris
  lorsque le corps lève ;
- exécution requise **depuis le fil principal** : `signal.signal` **et**
  `signal.set_wakeup_fd` échouent ailleurs, avec la même `ValueError`, et
  l'échec doit rester explicite plutôt que silencieux ;
- **aucun gestionnaire laissé en place** dans un processus hôte après la sortie ;
- le **descripteur de réveil** obéit aux mêmes règles que les gestionnaires :
  installé dans la portée, restauré à l'ancienne valeur rendue par
  `set_wakeup_fd`, et la paire de sockets refermée — y compris lorsque le corps
  lève. Aucun descripteur résiduel ;
- les gestionnaires sont **vides**. Ils n'arment rien, n'écrivent rien,
  n'acquièrent aucun verrou. Leur seule raison d'être est que le niveau C de
  CPython n'écrit l'octet que si un gestionnaire Python existe : sous `SIG_IGN`,
  rien n'est écrit.

Le processus est déjà multi-fils avant même que C9 n'intervienne :
`PahoMqttClient.connect()` appelle `loop_start()`, qui démarre un fil réseau. Le
fil principal reste celui qui exécute la boucle et reçoit les signaux ; la
contrainte ci-dessus n'est donc pas théorique.

### Double signal

C9 **n'implémente aucune** politique de « second Ctrl-C force la sortie ».

Un second signal reste **idempotent** vis-à-vis de l'état d'arrêt : il n'ajoute
rien, ne réinitialise rien, ne change pas la cause déjà enregistrée. Toute
politique d'escalade forcée est hors périmètre tant qu'un besoin réel n'est pas
démontré.

Conséquence à connaître : si un `stop()` est long, un utilisateur impatient ne
disposera d'aucun moyen d'accélérer la sortie autre que ceux de son système.
C'est un manque assumé, pas un oubli.

## Journalisation

C9 **n'appelle pas** `logging.basicConfig()` et ne configure la journalisation
d'aucune manière.

Motif : C9 ne possède pas le point d'entrée du programme. Une fonction appelée
programmatiquement qui configurerait globalement la journalisation du processus
hôte imposerait sa politique à un appelant qui n'a rien demandé.

Les composants existants continuent d'utiliser leurs journaux inchangés —
`boilerack.adapters.mqtt_paho` et `boilerack.core.engine` déclarent chacun un
`logging.getLogger(__name__)`, pour douze sites d'appel au total, sans
gestionnaire configuré. Le `lastResort` de la bibliothèque standard affiche donc
les avertissements sur `stderr`, et les messages `info` restent invisibles.
C'est le comportement actuel ; C9 ne le change pas.

La configuration de la journalisation appartient à C10, avec le vrai point
d'entrée utilisateur. Aucun fichier de journalisation n'est modifié par C9.

## Latences

Deux grandeurs distinctes, à ne jamais confondre.

### Latence de réveil

Temps écoulé entre l'armement de l'arrêt et le retour de l'attente
interruptible.

C'est la **seule** propriété que C9 cherche à rendre courte et démontrable, et
la seule sur laquelle il produira une mesure.

Encore faut-il distinguer deux choses que l'on confond aisément :

- **la preuve fonctionnelle** — une attente demandée pour une durée longue est
  effectivement interrompue **avant son échéance normale**. C'est binaire, c'est
  stable, et c'est cela que les tests affirment ;
- **la mesure informative** — la latence observée, rapportée en millisecondes.
  Elle renseigne, elle n'engage pas. Aucun seuil numérique contractuel n'est
  fixé : il dépendrait de la charge de la machine d'intégration, et une
  promesse en millisecondes tenue par GitHub Actions ne serait pas une promesse.

Les bornes temporelles qui apparaissent dans les tests sont des **garde-fous**
destinés à ne jamais bloquer une exécution. Elles ne sont pas des bornes
normatives, et ne doivent jamais être lues comme telles.

### Latence totale de sortie

Temps écoulé entre la réception du signal et le retour de la fonction de cycle
de vie. Elle inclut potentiellement :

- la latence de réveil ;
- le travail déjà engagé, dont un `run_due()` **déjà commencé**, que le runner
  ne tronque pas ;
- l'arrêt du publisher et la fermeture MQTT ;
- toute durée de `stop()`.

**C9 ne lui attribue aucune borne**, faute de preuve. Ces durées dépendent du
publisher, du réseau et du broker, qu'aucun contrat ne borne.

Aucune formulation de ce projet ne doit laisser entendre que `SIGINT` ou
`SIGTERM` garantit « un arrêt du processus complet en moins de X secondes ».
Ce qui est visé est plus modeste et vérifiable : le signal est **vu vite**, et
il emprunte ensuite le chemin d'arrêt que C8 garantit déjà.

## API livrée

Un module unique : `src/boilerack/lifecycle.py`. Rien n'a été dispersé.

| Symbole | Rôle |
|---|---|
| `SIGNALS_SURVEILLES` | `(SIGINT, SIGTERM)` — les deux seuls signaux traduits en demande d'arrêt |
| `CODE_ARRET_NORMAL` / `CODE_INTERRUPTION` | `0` et `130`, résultats **logiques**, pas des codes de sortie de processus |
| `SignalStop` | État d'arrêt. `is_set()` **draine puis répond** ; `cause` rend la première cause ; `signaux_ignores` expose les octets étrangers |
| `WakeupClock` | Horloge satisfaisant `Clock`. `now()` / `monotonic()` délégués à une horloge de base ; `sleep()` attend sur le descripteur |
| `Wakeup` | Paire gelée `(stop, clock)`, construite depuis **le même** descripteur |
| `SignalScope` | Portée : installe et retire intégralement gestionnaires, descripteur de réveil et sockets |
| `resultat_logique(cause)` | `130` si `SIGINT`, `0` sinon |
| `run_lifecycle(config, *, surveilles=…)` | Assemble, exécute, rend le résultat logique |

`SignalStop` et `WakeupClock` sont construits ensemble par la portée, à partir du
même descripteur : il est **structurellement impossible** qu'ils en surveillent
deux différents. Ce n'est pas un invariant à tester, c'est un invariant à ne pas
pouvoir violer.

### `is_set()` draine — et c'est écrit dans le code

La docstring de `SignalStop.is_set` le dit sans détour : ce n'est pas une
lecture passive, elle consomme le descripteur avant de répondre. Le motif y est
rappelé — sans cela, un arrêt passerait inaperçu lorsque C8 n'appelle pas
`sleep()`, ce qui arrive quand l'échéance suivante est déjà dépassée.

### Signaux étrangers

`signal.set_wakeup_fd` est **global au processus** : un gestionnaire posé par
l'hôte pour un autre signal écrit lui aussi dans notre descripteur. Le
comportement retenu, explicite et testé : ces octets sont **drainés et
ignorés** — ils n'arment pas l'arrêt et ne fournissent aucune cause. Ils sont
seulement recensés dans `signaux_ignores`, pour l'observabilité.

Conséquence assumée : un tel signal **réveille** néanmoins l'attente. Le runner
reconsulte l'état, ne trouve pas d'arrêt, et rappelle `run_due()`, qui ne trouve
alors rien de dû. Aucune reprise d'attente n'est tentée : ce serait une
politique, et rien ne l'exige.

### Drainage ultime

`run_lifecycle` draine une dernière fois **après** le retour du runner, avant de
conclure. Sans cela, le résultat logique dépendrait du nombre d'interrogations
faites par le runner, et un signal reçu pendant `stop()` serait perdu. Ce défaut
a été introduit puis attrapé par un test avant d'être corrigé ; la mutation
correspondante figure au tableau plus bas.

### Politique d'erreurs de la portée

Alignée sur celle de C8, et non inventée :

| Situation | Comportement |
|---|---|
| Corps normal, restauration normale | rien de particulier |
| Corps en échec, restauration réussie | l'exception du corps poursuit sa route, **identité préservée** |
| Corps normal, restauration en échec | l'erreur de restauration remonte telle quelle |
| Les deux en échec | un **groupe** portant **[corps, restauration]**, dans cet ordre |

La propriété tenue est sémantique, non typologique : **le corps et la
restauration sont tous deux préservés, dans cet ordre, via le type de groupe
approprié aux exceptions contenues.**

Le groupe est construit avec `BaseExceptionGroup`, jamais avec
`ExceptionGroup`. Motif établi par l'audit puis reproduit : un corps peut sortir
sur une `BaseException` — `SystemExit`, par exemple —, et `ExceptionGroup`
refuse alors de l'imbriquer en levant `TypeError: Cannot nest BaseExceptions in
an ExceptionGroup`. L'exception d'origine serait **perdue**, remplacée par une
erreur de typage sans rapport.

Le cas courant reste inchangé, et cela a été vérifié plutôt que supposé :
lorsque tous les membres sont des `Exception`, `BaseExceptionGroup` **rend un
`ExceptionGroup`**. Le type observé est donc `ExceptionGroup` pour deux erreurs
ordinaires, et `BaseExceptionGroup` seulement lorsqu'un membre l'exige. Un
`except ExceptionGroup` continue d'attraper le premier cas, et ne peut pas
attraper le second — ce qui est correct : une `BaseException` ne doit pas être
capturée par inadvertance.

La restauration tente **toutes** ses étapes — sélecteur, gestionnaires,
descripteur, sockets — même si l'une échoue, et ne groupe qu'ensuite. Un échec
partiel ne doit pas laisser le reste installé.

La même politique gouverne l'**entrée**, et pas seulement la sortie :

| Situation à l'entrée | Comportement |
|---|---|
| Échec partiel, nettoyage réussi | l'erreur d'entrée remonte **telle quelle**, sans groupe |
| Échec partiel, nettoyage en échec | un **groupe** portant **[entrée, nettoyage]**, dans cet ordre |

Si la pose d'un gestionnaire échoue alors que le descripteur de réveil est déjà
installé, `__enter__` retire tout ce qui a été posé avant de laisser l'erreur
remonter. Et si ce nettoyage échoue à son tour, les deux erreurs sont
conservées — comme à la sortie, et par le même mécanisme.

Le comportement antérieur a été **reproduit avant d'être corrigé** : l'erreur de
nettoyage devenait l'exception principale, et l'erreur d'entrée ne survivait que
dans `__context__`. C'était vrai aussi bien pour une `OSError` que pour un
`SystemExit`. Des tests d'injection de panne verrouillent désormais les quatre
combinaisons.

### Fil principal

`SignalScope.__enter__` vérifie le fil principal **avant toute allocation** et
lève une `RuntimeError` explicite. La contrainte n'est pas contournée : elle est
seulement annoncée plus tôt et plus clairement que la `ValueError` que
`signal.signal` aurait fini par lever, et rien n'est alloué en cas de refus.

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
gestionnaire Python ne fait rien, et l'écriture de l'octet appartient au niveau
C. C'est ce qui distingue cette architecture de celle qui a été rejetée.

Flux de contrôle : la fonction de cycle de vie ouvre la portée de signaux,
construit le runtime avec l'état d'arrêt et l'horloge interruptible partagée,
appelle `run()`, puis calcule le résultat logique à partir de la cause
enregistrée. La portée de signaux restaure les gestionnaires précédents en
sortant, que `run()` ait rendu la main normalement ou levé.

## Inclus — liste fermée

1. Un état d'arrêt concret, armé par drainage du descripteur, compatible avec
   `StopSignal`.
2. La conservation minimale de la cause `SIGINT` / `SIGTERM`, tirée du premier
   octet consommé.
3. Une attente / horloge interruptible compatible avec `Clock`, fondée sur une
   paire de sockets locales et un sélecteur.
4. L'injection optionnelle de l'horloge dans `build_runtime`.
5. L'installation et la restauration contrôlées des gestionnaires `SIGINT` /
   `SIGTERM` **et** du descripteur de réveil, ainsi que la création et la
   fermeture de la paire de sockets locales.
6. Une fonction Python de cycle de vie prenant un `RuntimeConfig` **déjà
   construit**.
7. L'arrêt gracieux par le chemin C8 existant.
8. Le résultat logique : normal ou `SIGTERM` propre → `0` ; `SIGINT` propre →
   `130`.
9. La préservation des exceptions en cas de panne.
10. La documentation des limites et de la preuve POSIX.

## Exclus — liste fermée

CLI · `argparse`, Click, Typer ou équivalent · `[project.scripts]` ·
`__main__.py` · lecture de variables d'environnement · fichier TOML / YAML /
JSON de configuration · noms publics de configuration · configuration globale de
la journalisation · reconnexion MQTT · stratégie réseau · systemd · packaging
final · installation · déploiement · Pi réel · broker réel · `vclient` réel ·
`vcontrold` réel · chaudière · Home Assistant · écriture chaudière · traitement
des trois champs de configuration morts (`command_topic`, `ack_topic_prefix`,
`write_timeout_s`) · politique de second signal force · refactor large de C8.

## Preuves à produire

### État d'arrêt

- initialement non armé ;
- armement **idempotent** : plusieurs signaux laissent le même état et la même
  cause — la première ;
- `is_set()` compatible avec ce que C8 consomme, et **drainant** ;
- la cause utile au résultat final est conservée, et elle seule ;
- la première cause est vérifiée dans les **deux** ordres d'arrivée.

### Attente interruptible

- durée normale respectée lorsque aucun signal n'est survenu ;
- réveil anticipé lorsqu'un signal survient pendant l'attente ;
- réveil **immédiat** lorsqu'un signal est survenu AVANT l'entrée dans
  l'attente : l'octet mémorisé doit suffire ;
- **même descripteur partagé** entre l'état d'arrêt et l'attente — deux
  descripteurs distincts doivent être détectés comme un défaut ;
- durées invalides traitées selon les invariants de `Clock` : non finies et
  négatives refusées ;
- `now()` et `monotonic()` restent conformes au protocole.

### Chemin de signal

- le gestionnaire installé est **vide** : il n'arme rien et n'acquiert aucun
  verrou. Un gestionnaire qui appellerait une primitive de synchronisation doit
  être détecté comme un défaut ;
- sous `SIG_IGN`, aucun octet n'est écrit : le gestionnaire vide est donc
  nécessaire, et son absence doit être détectée ;
- un signal reçu **pendant** `run_due()` ne tronque pas le cycle et est honoré
  au point de contrôle suivant, sans cycle superflu.

### `build_runtime`

- sans injection, l'horloge par défaut reste `SystemClock` — le test C8 existant
  doit rester vert sans modification de son intention ;
- avec injection, l'horloge fournie est bien celle utilisée ;
- **la même instance** est partagée par le publisher et le runner, dans les deux
  cas ;
- construire n'ouvre toujours ni socket ni processus.

### Signaux

- les gestionnaires sont installés dans la portée ;
- les gestionnaires précédents sont **restaurés exactement**, y compris lorsque
  le corps de la portée lève ;
- `SIGINT` arme l'état avec la cause `SIGINT` ;
- `SIGTERM` arme l'état avec la cause `SIGTERM` ;
- l'installation hors fil principal **échoue explicitement** ;
- **aucun effet de bord à l'import** du module.

### Cycle de vie

- retour normal sans signal → `0` ;
- `SIGTERM` puis arrêt propre → `0` ;
- `SIGINT` puis arrêt propre → `130` ;
- panne → l'exception remonte, non masquée, identité préservée ;
- erreur pendant `stop()` → la politique C8 est préservée telle quelle, y compris
  le regroupement lors d'un double échec, `BaseException` comprise.

### Preuve POSIX

Une preuve réelle, en sous-processus, sur Linux — donc en intégration continue,
où le dépôt exécute déjà Python 3.11, 3.12 et 3.13 sur `ubuntu-latest` :

- lancement d'un processus Python qui exerce les composants de **production** —
  `SignalScope`, `WakeupClock`, `SignalStop`, `resultat_logique` ;
- envoi d'un `SIGTERM` réel ;
- constatation du réveil ;
- constatation de l'arrêt ;
- vérification du code de sortie ;
- mesure de la **latence de réveil**, et d'elle seule.

**Limite de plateforme, assumée.** La machine de développement est sous Windows.
Il y a été mesuré que `SIGTERM` n'interrompt pas une attente sur état quand le
fil principal y est bloqué, alors que `SIGINT` le fait. Windows ne permet donc
pas de démontrer ce que la cible garantit. La preuve `SIGTERM` est conditionnée
à POSIX et ne sera réellement exercée qu'en intégration continue. Ce document ne
prétend rien de plus.

Ce que la caractérisation a **déjà** pu établir localement, et ce qu'elle n'a
pas pu établir, précisément :

| Établi localement | Non établi localement |
|---|---|
| le script enfant compile, démarre et annonce sa disponibilité | la délivrance réelle de `SIGTERM` |
| le harnais — sous-processus, fil lecteur, file, délais durs — fonctionne | le réveil par `SIGTERM` |
| `SIGINT` arme l'état et écourte une attente, en processus | — |
| `time.sleep` n'est PAS écourté par un gestionnaire pose-drapeau | — |

Le saut de plateforme est rendu **visible et vérifiable** par un test dédié qui
constate le motif du saut, plutôt que par un simple `skipif` silencieux. Aucune
preuve POSIX n'est simulée.

### Mutations discriminantes

Au minimum, les mutations suivantes doivent être tuées :

Campagne exécutée : **15 mutations, 15 tuées, aucune survivante**, fichiers de
production restaurés à l'octet près (SHA-256 vérifié). Le détail figure au
rapport du lot.

| # | Mutation | Ce qu'elle casse |
|---|---|---|
| 1 | Aucun gestionnaire installé, ou `SIG_IGN` | aucun octet n'est écrit : le signal devient sans effet |
| 2 | Descripteur différent entre le wakeup fd et l'attente | l'octet est écrit, mais rien ne réveille |
| 3 | Attente non interruptible (retour à `time.sleep`) | reproduit exactement le piège PEP 475 |
| 4 | Gestionnaires non restaurés à la sortie | contamination du processus hôte |
| 4 bis | Wakeup fd ou paire de sockets non restaurés / non fermés | descripteur résiduel, contamination du processus hôte |
| 5 | `SIGINT` classé en succès `0` | perte de la sémantique d'interruption |
| 6 | `SIGTERM` classé `130` | arrêt normal présenté comme une interruption |
| 7 | Panne convertie en succès | une panne passerait pour un arrêt demandé |
| 8 | Horloges différentes pour publisher et runner | rupture de l'invariant C8 |
| 9 | `is_set()` ne draine pas | arrêt manque quand l'échéance est déjà dépassée : cycles superflus, voire boucle sans fin |
| 10 | Le dernier octet consommé écrase la cause | résultat logique non déterministe entre `0` et `130` |
| 11 | Le gestionnaire arme l'état lui-même (retour à l'architecture rejetée) | réintroduit le blocage par réentrance de verrou |
| 12 | Pas de drainage ultime dans `run_lifecycle` | un signal reçu après le dernier point de contrôle est perdu ; le résultat dépend du nombre d'interrogations du runner |
| 13 | Le refus hors fil principal disparaît | échec tardif et obscur au lieu d'un refus clair |
| 14 | Les signaux étrangers arment l'arrêt | un signal de l'hôte arrêterait le pont |
| 15 | Retour à `ExceptionGroup` pour le double échec | `TypeError` sur un corps `BaseException` : l'origine est perdue |
| 16 | Suppression du nettoyage dans `__enter__` | une entrée échouant à mi-chemin laisserait descripteur, gestionnaire et sockets installés |
| 17 | À l'entrée, le nettoyage en échec remplace l'erreur d'origine | l'erreur d'entrée n'est plus conservée que dans `__context__` |
| 18 | Ordre inverse dans le groupe d'entrée | l'erreur de nettoyage passerait pour la cause première |

## Fichiers

**Nouveaux** — `src/boilerack/lifecycle.py` ; `tests/test_lifecycle.py` ; le
présent document.

**Modifiés** — `src/boilerack/runtime.py`, pour le seul paramètre d'horloge
optionnel, réservé aux mots-clés et de défaut inchangé ;
`tests/test_runtime.py`, pour le couvrir ; `docs/design/c8-composition-root.md`,
pour deux renvois documentaires.

**Non modifiés** — `pyproject.toml`, `clock.py`, `read_surface/`, `adapters/`,
`transport/`, `core/`, `README.md`, et les contrats C4, C5 et C7.

Aucune dépendance n'est ajoutée : la bibliothèque standard suffit — `signal`,
`socket`, `selectors`, et rien de plus.

## Renvois

- La section « Latence d'arrêt » de `c8-composition-root.md` décrit l'état de C8
  seul, où aucun réveil n'existe. Elle reste exacte pour ce qu'elle décrit.
- Le point d'entrée installé, la source de configuration et la configuration de
  la journalisation relèvent de C10.
