# C8 — Composition root et boucle d'execution

## Objet

Premier lot qui **assemble** Boilerack au lieu de le decrire. Il livre un module
unique, `boilerack.runtime`, qui fait deux choses et rien d'autre :

1. `build_runtime` construit les adaptateurs concrets et les cable ;
2. `ReadSurfaceRunner` pilote le publieur de l'exterieur — `due_at`, attente,
   `run_due` — jusqu'a ce qu'un arret soit demande.

Le lot est **entierement hors production**. Aucun broker, aucun `vcontrold`,
aucune chaudiere, aucun processus, aucune socket n'a ete contacte. Aucune
conformite production n'est revendiquee.

## Bibliotheque contre programme

Tout ce qui precede C8 est une **bibliotheque** : des composants qui ne
construisent rien et ne decident de rien. C7-C3 a explicitement interdit au
publieur de construire ses dependances ; cette frontiere n'est pas relachee
ici, elle est **honoree**.

| Responsabilite | Detenteur | Verifie par |
|---|---|---|
| Construire les adaptateurs concrets | `build_runtime`, et lui seul | `test_seul_le_composition_root_construit_les_adaptateurs`, `test_le_publieur_ne_construit_aucun_adaptateur` |
| Cadence, mesures, statuts, topics, instantanes | `ReadSurfacePublisher` (C7-C3) | `test_runner_ne_porte_aucune_logique_metier` |
| Demarrer, attendre, rappeler, arreter | `ReadSurfaceRunner` | `tests/test_runtime.py` |

Le runner ne sait ni ce qu'est une mesure, ni ce qu'est un instantane. Un test
sur l'AST du module verifie qu'aucun nom metier — `TransportStatus`,
`record_result`, `complete_cycle`, `build_snapshot`, `format_scalar`,
`telemetry`, `heartbeat`, `bridge/`, `MqttWill` — n'y apparait hors docstring.

## Aucun effet de bord a l'import

Importer `boilerack.runtime` ne construit rien, n'ouvre aucune connexion et ne
lance aucun processus. Le corps du module ne contient que des imports, des
declarations et des constantes litterales — verifie sur l'AST, pas par un
rechargement de module.

`build_runtime` est une fonction : c'est **l'appeler** qui construit. Et meme
alors, rien n'est ouvert : construire un `PahoMqttClient` n'ouvre aucune socket
(seul `connect()` le ferait), construire un `VClientCliReader` ne lance aucun
processus (seule une lecture le ferait).

Precision, car « aucun effet de bord » ne veut pas dire « aucun chargement » :
importer `boilerack.runtime` **charge bien** `paho` et `subprocess`, de facon
transitive, puisque ce module nomme les adaptateurs concrets. C'est le propre
d'un composition root. L'invariant de C7 n'en est pas affecte et reste verifie :
importer `boilerack.read_surface` ne charge **ni** `paho` **ni** `subprocess`.
Ce qui est garanti ici est plus etroit et plus utile : aucune socket n'est
ouverte, aucun processus n'est lance, aucun objet n'est construit a l'import.

L'isolement de `boilerack.read_surface` n'est pas re-teste dans ce lot : il est
deja verrouille par les controles d'imports des suites C7-C
(`_INTERDITS` dans `test_publisher.py`, `test_state.py`, `test_snapshot.py`).

## Pourquoi il n'y a pas de `Waiter`

Le cadrage envisageait un protocole `Waiter` distinct. Il n'a **pas** ete
introduit : ce serait une couture en double.

`boilerack.clock.Clock` expose deja `monotonic()`, `now()` et **`sleep()`**, et
`VirtualClock.sleep()` avance le temps virtuel sans jamais attendre. La couture
d'attente existe donc, elle est deja injectee partout, et elle est deja
testable. La boucle dort via l'horloge injectee : `SystemClock` en production,
`VirtualClock` en test. Toute la suite de tests s'execute en temps virtuel — la
mesure `sleeps == [30.0, 30.0]` est faite sur l'horloge, pas sur le mur.

## Arret

`StopSignal` est un `Protocol` a une seule methode, `is_set() -> bool`. C'est
la forme de `threading.Event` : un `Event` reel satisfait donc le protocole
**structurellement**, sans que le module importe `threading` ni impose un
modele de concurrence. Le test le demontre en faisant tourner le runner avec un
vrai `threading.Event`.

`StopSignal` n'est **pas** `runtime_checkable`. Un `isinstance` sur un protocole
n'inspecte que la presence des noms de methodes, jamais leurs signatures : il
donnerait une assurance fausse. La conformite se prouve en utilisant l'objet.

`NeverStop` ne demande jamais l'arret. Il **n'est pas le defaut** de
`ReadSurfaceRunner` : une boucle sans sortie doit etre demandee explicitement,
jamais obtenue par omission.

La demande est consultee a deux moments par cycle : a l'entree de la boucle, et
**apres l'attente**, avant tout travail. Un arret demande pendant une attente
n'est donc pas vu immediatement, mais il n'entraine aucun cycle superflu.

### Latence d'arret — limite connue

Deux grandeurs distinctes, a ne pas confondre.

**Latence d'attente** — le delai entre la demande d'arret et le moment ou elle
est vue. Elle est bornee par la prochaine echeance, soit au plus la plus petite
periode de la surface : **≤ 30 s** avec `V1_MEASUREMENTS`. C'est la seule des
deux qui admette une borne connue.

**Latence totale d'arret** — le delai entre la demande et le retour de `run()`.
Elle vaut :

```
latence d'attente
  + le travail deja engage (un run_due() commence n'est PAS interrompu)
  + la duree de stop()
```

Les deux derniers termes n'ont **aucune borne etablie** : ils dependent du
publieur, du reseau et du broker, qu'aucun contrat ne borne. Le seul fait
garanti ici est etroit : **le runner ne tronque pas un `run_due()` deja
engage** pour repondre au signal d'arret ; il attend son retour, et l'arret
est pris en compte entre les cycles. Enonce autrement : `≤ 30 s` borne le
reveil, pas la sortie.

Cela ne dit **rien** de l'issue des publications de ce cycle. C7 reste
best-effort et non transactionnel : une publication peut echouer isolement, et
un cycle mene a son terme ne garantit donc ni le tout-ou-rien, ni la coherence
de la surface MQTT a l'arret. Le runner ne fait ici qu'une chose : il
n'interrompt pas au milieu.

Aucune tranche d'attente maximale n'a ete introduite pour reduire la premiere.
Ce serait une politique, et rien dans les contrats ne l'exige. Le decoupage du
sommeil, ou une attente interruptible, releverait d'un lot ulterieur avec une
exigence ecrite.

> Ce lot ulterieur existe desormais : voir `c9-process-lifecycle.md`, qui
> introduit une attente interruptible et un reveil sur signal. Les grandeurs
> decrites ci-dessus restent celles de C8 seul, ou aucun reveil n'existe.

## Attente

Fondee sur le temps **monotone**, jamais sur l'heure murale : le module
n'appelle ni `datetime.now`, ni `utcnow`, ni `time.sleep`, ni `time.monotonic`
directement — verifie par test.

Une echeance deja atteinte ou depassee ne provoque **aucune** attente : `sleep`
n'est alors pas appele du tout, et jamais avec une duree negative.

Le runner n'introduit **aucune derive** propre : il dort exactement jusqu'a
l'echeance demandee par le publieur, sans marge et sans rattrapage. La politique
de non-rattrapage appartient au publieur (C7-C3B : `next_due` recalcule apres
chaque tentative).

## Politique d'erreur

Rien n'est masque, rien n'est traduit, aucune taxonomie nouvelle n'est creee.

| Situation | Comportement |
|---|---|
| `start()` echoue, `started` faux | Remonte tel quel. Aucun arret de secours : rien n'a ete ouvert. Aucune boucle. |
| `start()` echoue, `started` vrai | Arret de secours tente — la connexion n'est pas fuitee —, puis l'erreur d'origine remonte. |
| `start()` puis arret de secours echouent | `ExceptionGroup` des deux, dans cet ordre. |
| `due_at()`, attente ou `run_due()` echoue | La boucle s'arrete. `stop()` est neanmoins tente. L'erreur remonte **telle quelle**, identite preservee. |
| Erreur de boucle **et** `stop()` echouent | `ExceptionGroup` des deux : erreur de boucle d'abord, erreur d'arret ensuite. |
| `stop()` echoue seul | Remonte tel quel, sans groupe. |

Le cas « `start()` echoue alors que `started` est vrai » n'est pas theorique :
C7-C3A documente que la connexion peut etre ouverte alors qu'une publication
initiale a echoue. Ce lot donne a `started` son premier consommateur hors test.

Le runner ne decide d'**aucune politique de reprise**. Une erreur de cycle
arrete la boucle. Reessayer, temporiser, degrader — ce serait inventer une
resilience que rien n'etablit, et masquer une panne que l'exploitant doit voir.

Seules les `Exception` sont interceptees. `KeyboardInterrupt`, `SystemExit` et
`GeneratorExit` traversent immediatement : ce sont des controles de flux, pas
des pannes. **Consequence assumee et testee** : une interruption clavier ne
declenche pas d'arret propre, donc pas d'annonce `offline`. La brancher a un
arret gracieux releve de la gestion de signaux, reportee ci-dessous.

## Configuration

`RuntimeConfig` **contient** les trois configurations existantes et n'en
redeclare aucun champ :

```
RuntimeConfig(mqtt: MqttConfig, vclient: VclientConfig,
              read_surface: ReadSurfaceConfig = ReadSurfaceConfig(),
              specs: Sequence[MeasurementSpec] = V1_MEASUREMENTS)
```

`MqttConfig`, `VclientConfig` et `ReadSurfaceConfig` restent **seules autorites**
de ce qu'elles portent et de leurs invariants. Il n'y a pas de seconde autorite :
aucun champ n'est copie, aucun invariant n'est revalide. `RuntimeConfig` ne
verifie que les types de ce qu'on lui donne, et gele `specs` en tuple.

Aucun defaut n'est fourni pour l'hote du broker ni pour l'executable `vclient` :
ce sont des **valeurs de site**, et le depot n'en porte aucune. Un test verifie
qu'aucune adresse IP, aucun `localhost`, aucun chemin absolu et aucun terme de
secret n'apparait dans le module.

## Point d'entree — reporte

**Aucun point d'entree n'est livre.** `pyproject.toml` ne declare toujours pas
de `[project.scripts]`, et il n'existe ni `main()`, ni `__main__`, ni service.

Ce report est delibere. Livrer une commande exigerait de trancher, sans
exigence ecrite pour arbitrer :

- la **source** de la configuration — variables d'environnement, fichier TOML
  ou YAML, arguments de ligne de commande, ou combinaison ordonnee ;
- le **nom** et la **forme** des cles publiques, qui deviendraient une surface
  de compatibilite au meme titre que les topics ;
- la gestion des **signaux** (`SIGTERM`, `SIGINT`) et son branchement sur le
  `StopSignal` ;
- la **journalisation** : format, niveau, destination ;
- le **mode de deploiement** — unite systemd, conteneur, ou lancement manuel.

Chacun de ces choix est une decision structurelle, donc arbitrable par l'humain
et non par le code. `build_runtime` est la brique sur laquelle un tel point
d'entree se posera sans rien reecrire : il ne manque que ces arbitrages.

> Ces arbitrages ont depuis ete repartis sur deux lots. La gestion des signaux
> et son branchement sur le `StopSignal` reviennent a C9
> (`c9-process-lifecycle.md`). La source de configuration, les noms des cles
> publiques, la journalisation, le mode de deploiement et le point d'entree
> installe lui-meme reviennent a C10, non encore ouvert.

## Surface publique du lot

| Symbole | Role |
|---|---|
| `StopSignal` | Protocole d'arret, `is_set() -> bool` |
| `NeverStop` | Signal qui ne demande jamais l'arret |
| `RuntimeConfig` | Configuration d'assemblage |
| `Runtime` | Assemblage pret a tourner : `publisher`, `runner` |
| `ReadSurfaceRunner` | Boucle exterieure : `run()`, `publisher` |
| `build_runtime(config, stop) -> Runtime` | Construction et cablage |

`Runtime` expose `publisher` en plus de `runner` pour permettre d'inspecter
l'etat sans passer par la boucle.

## Verification

45 tests dans `tests/test_runtime.py`, dont :

- **integration hors production** — vrai `ReadSurfacePublisher` et vrai runner,
  faux MQTT, faux lecteur, horloge virtuelle, arret virtuel. Le parcours
  `start → lectures initiales → cycle 30 s → battement → instantane → stop` est
  verifie au comptage exact : 19 lectures (8 puis 3 puis 8), 2 sommeils de 30 s,
  une publication scalaire par lecture reussie, `online` en tete et `offline` en
  queue, aucun topic hors de la surface v1, `chain.status = ok` a la fin ;
- **`build_runtime`** — la frontiere Paho est remplacee par un double via
  `monkeypatch` de `PahoMqttClient._build_client` ; `socket.socket`,
  `subprocess.run` et `subprocess.Popen` sont remplaces par des echecs
  immediats, ce qui **prouve** que la construction n'ouvre ni socket ni
  processus.

Aucun adaptateur reel n'est jamais exerce contre une ressource reelle.

**Mutation testing** — 7 mutations appliquees a `runtime.py`, 7 tuees, aucune
survivante : attente d'une echeance passee, absence de reconsultation de l'arret
apres l'attente, arret de secours indu, perte de l'erreur de boucle en cas de
double echec, absorption silencieuse de l'erreur de boucle, interception de
`BaseException`, perte de l'erreur d'arret de secours au demarrage. Le fichier a
ete restaure a l'octet pres (SHA-256 verifie).

## Ce que ce lot ne fait pas

- Aucun point d'entree, aucune commande, aucun service, aucune unite systemd ;
- aucune gestion de signaux ;
- aucune journalisation ;
- aucun thread, aucun `asyncio`, aucun modele de concurrence impose ;
- aucune ecriture chaudiere — le noyau transactionnel de C3 n'est pas cable ;
- aucune politique de reprise, de nouvelle tentative ou de reconnexion ;
- aucune reduction de la latence d'arret ;
- aucune valeur de site, aucun secret.

La limite deja connue de C7-C3A reste entiere : apres une deconnexion
inattendue suivie d'une reconnexion automatique de Paho, `bridge/online` retenu
peut rester a `offline` jusqu'au prochain `start()`. La frontiere n'expose aucun
rappel de connexion et C7-B ne couvre pas la reconnexion.
