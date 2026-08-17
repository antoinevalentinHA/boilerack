# C8 — Composition root et boucle d'exécution

## Objet

Premier lot qui **assemble** Boilerack au lieu de le décrire. Il livre un module
unique, `boilerack.runtime`, qui fait deux choses et rien d'autre :

1. `build_runtime` construit les adaptateurs concrets et les câble ;
2. `ReadSurfaceRunner` pilote le publieur de l'extérieur — `due_at`, attente,
   `run_due` — jusqu'à ce qu'un arrêt soit demandé.

Le lot est **entièrement hors production**. Aucun broker, aucun `vcontrold`,
aucune chaudière, aucun processus, aucune socket n'a été contacté. Aucune
conformité production n'est revendiquée.

## Bibliothèque contre programme

Tout ce qui précède C8 est une **bibliothèque** : des composants qui ne
construisent rien et ne décident de rien. C7-C3 a explicitement interdit au
publieur de construire ses dépendances ; cette frontière n'est pas relâchée
ici, elle est **honorée**.

| Responsabilité | Détenteur | Vérifié par |
|---|---|---|
| Construire les adaptateurs concrets | `build_runtime`, et lui seul | `test_seul_le_composition_root_construit_les_adaptateurs`, `test_le_publieur_ne_construit_aucun_adaptateur` |
| Cadence, mesures, statuts, topics, instantanés | `ReadSurfacePublisher` (C7-C3) | `test_runner_ne_porte_aucune_logique_metier` |
| Démarrer, attendre, rappeler, arrêter | `ReadSurfaceRunner` | `tests/test_runtime.py` |

Le runner ne sait ni ce qu'est une mesure, ni ce qu'est un instantané. Un test
sur l'AST du module vérifie qu'aucun nom métier — `TransportStatus`,
`record_result`, `complete_cycle`, `build_snapshot`, `format_scalar`,
`telemetry`, `heartbeat`, `bridge/`, `MqttWill` — n'y apparaît hors docstring.

## Aucun effet de bord à l'import

Importer `boilerack.runtime` ne construit rien, n'ouvre aucune connexion et ne
lance aucun processus. Le corps du module ne contient que des imports, des
déclarations et des constantes littérales — vérifié sur l'AST, pas par un
rechargement de module.

`build_runtime` est une fonction : c'est **l'appeler** qui construit. Et même
alors, rien n'est ouvert : construire un `PahoMqttClient` n'ouvre aucune socket
(seul `connect()` le ferait), construire un `VClientCliReader` ne lance aucun
processus (seule une lecture le ferait).

Précision, car « aucun effet de bord » ne veut pas dire « aucun chargement » :
importer `boilerack.runtime` **charge bien** `paho` et `subprocess`, de façon
transitive, puisque ce module nomme les adaptateurs concrets. C'est le propre
d'un composition root. L'invariant de C7 n'en est pas affecté et reste vérifié :
importer `boilerack.read_surface` ne charge **ni** `paho` **ni** `subprocess`.
Ce qui est garanti ici est plus étroit et plus utile : aucune socket n'est
ouverte, aucun processus n'est lancé, aucun objet n'est construit à l'import.

L'isolement de `boilerack.read_surface` n'est pas re-testé dans ce lot : il est
déjà verrouillé par les contrôles d'imports des suites C7-C
(`_INTERDITS` dans `test_publisher.py`, `test_state.py`, `test_snapshot.py`).

## Pourquoi il n'y a pas de `Waiter`

Le cadrage envisageait un protocole `Waiter` distinct. Il n'a **pas** été
introduit : ce serait une couture en double.

`boilerack.clock.Clock` expose déjà `monotonic()`, `now()` et **`sleep()`**, et
`VirtualClock.sleep()` avance le temps virtuel sans jamais attendre. La couture
d'attente existe donc, elle est déjà injectée partout, et elle est déjà
testable. La boucle dort via l'horloge injectée : `SystemClock` en production,
`VirtualClock` en test. Toute la suite de tests s'exécute en temps virtuel — la
mesure `sleeps == [30.0, 30.0]` est faite sur l'horloge, pas sur le mur.

## Arrêt

`StopSignal` est un `Protocol` à une seule méthode, `is_set() -> bool`. C'est
la forme de `threading.Event` : un `Event` réel satisfait donc le protocole
**structurellement**, sans que le module importe `threading` ni impose un
modèle de concurrence. Le test le démontre en faisant tourner le runner avec un
vrai `threading.Event`.

`StopSignal` n'est **pas** `runtime_checkable`. Un `isinstance` sur un protocole
n'inspecte que la présence des noms de méthodes, jamais leurs signatures : il
donnerait une assurance fausse. La conformité se prouve en utilisant l'objet.

`NeverStop` ne demande jamais l'arrêt. Il **n'est pas le défaut** de
`ReadSurfaceRunner` : une boucle sans sortie doit être demandée explicitement,
jamais obtenue par omission.

La demande est consultée à deux moments par cycle : à l'entrée de la boucle, et
**après l'attente**, avant tout travail. Un arrêt demandé pendant une attente
n'est donc pas vu immédiatement, mais il n'entraîne aucun cycle superflu.

### Latence d'arrêt — limite connue

Deux grandeurs distinctes, à ne pas confondre.

**Latence d'attente** — le délai entre la demande d'arrêt et le moment où elle
est vue. Elle est bornée par la prochaine échéance, soit au plus la plus petite
période de la surface : **≤ 30 s** avec `V1_MEASUREMENTS`. C'est la seule des
deux qui admette une borne connue.

**Latence totale d'arrêt** — le délai entre la demande et le retour de `run()`.
Elle vaut :

```
latence d'attente
  + le travail deja engage (un run_due() commence n'est PAS interrompu)
  + la duree de stop()
```

Les deux derniers termes n'ont **aucune borne établie** : ils dépendent du
publieur, du réseau et du broker, qu'aucun contrat ne borne. Le seul fait
garanti ici est étroit : **le runner ne tronque pas un `run_due()` déjà
engagé** pour répondre au signal d'arrêt ; il attend son retour, et l'arrêt
est pris en compte entre les cycles. Énoncé autrement : `≤ 30 s` borne le
réveil, pas la sortie.

Cela ne dit **rien** de l'issue des publications de ce cycle. C7 reste
best-effort et non transactionnel : une publication peut échouer isolément, et
un cycle mené à son terme ne garantit donc ni le tout-ou-rien, ni la cohérence
de la surface MQTT à l'arrêt. Le runner ne fait ici qu'une chose : il
n'interrompt pas au milieu.

Aucune tranche d'attente maximale n'a été introduite pour réduire la première.
Ce serait une politique, et rien dans les contrats ne l'exige. Le découpage du
sommeil, ou une attente interruptible, relèverait d'un lot ultérieur avec une
exigence écrite.

> Ce lot ultérieur existe désormais : voir `c9-process-lifecycle.md`, qui
> introduit une attente interruptible et un réveil sur signal. Les grandeurs
> décrites ci-dessus restent celles de C8 seul, où aucun réveil n'existe.

## Attente

Fondée sur le temps **monotone**, jamais sur l'heure murale : le module
n'appelle ni `datetime.now`, ni `utcnow`, ni `time.sleep`, ni `time.monotonic`
directement — vérifié par test.

Une échéance déjà atteinte ou dépassée ne provoque **aucune** attente : `sleep`
n'est alors pas appelé du tout, et jamais avec une durée négative.

Le runner n'introduit **aucune dérive** propre : il dort exactement jusqu'à
l'échéance demandée par le publieur, sans marge et sans rattrapage. La politique
de non-rattrapage appartient au publieur (C7-C3B : `next_due` recalculé après
chaque tentative).

## Politique d'erreur

Rien n'est masqué, rien n'est traduit, aucune taxonomie nouvelle n'est créée.

| Situation | Comportement |
|---|---|
| `start()` échoue, `started` faux | Remonte tel quel. Aucun arrêt de secours : rien n'a été ouvert. Aucune boucle. |
| `start()` échoue, `started` vrai | Arrêt de secours tenté — la connexion n'est pas fuitée —, puis l'erreur d'origine remonte. |
| `start()` puis arrêt de secours échouent | `ExceptionGroup` des deux, dans cet ordre. |
| `due_at()`, attente ou `run_due()` échoue | La boucle s'arrête. `stop()` est néanmoins tenté. L'erreur remonte **telle quelle**, identité préservée. |
| Erreur de boucle **et** `stop()` échouent | `ExceptionGroup` des deux : erreur de boucle d'abord, erreur d'arrêt ensuite. |
| `stop()` échoue seul | Remonte tel quel, sans groupe. |

Le cas « `start()` échoue alors que `started` est vrai » n'est pas théorique :
C7-C3A documente que la connexion peut être ouverte alors qu'une publication
initiale a échoué. Ce lot donne à `started` son premier consommateur hors test.

Le runner ne décide d'**aucune politique de reprise**. Une erreur de cycle
arrête la boucle. Réessayer, temporiser, dégrader — ce serait inventer une
résilience que rien n'établit, et masquer une panne que l'exploitant doit voir.

Seules les `Exception` sont interceptées. `KeyboardInterrupt`, `SystemExit` et
`GeneratorExit` traversent immédiatement : ce sont des contrôles de flux, pas
des pannes. **Conséquence assumée et testée** : une interruption clavier ne
déclenche pas d'arrêt propre, donc pas d'annonce `offline`. La brancher à un
arrêt gracieux relève de la gestion de signaux, reportée ci-dessous.

## Configuration

`RuntimeConfig` **contient** les trois configurations existantes et n'en
redéclare aucun champ :

```
RuntimeConfig(mqtt: MqttConfig, vclient: VclientConfig,
              read_surface: ReadSurfaceConfig = ReadSurfaceConfig(),
              specs: Sequence[MeasurementSpec] = V1_MEASUREMENTS)
```

`MqttConfig`, `VclientConfig` et `ReadSurfaceConfig` restent **seules autorités**
de ce qu'elles portent et de leurs invariants. Il n'y a pas de seconde autorité :
aucun champ n'est copié, aucun invariant n'est revalidé. `RuntimeConfig` ne
vérifie que les types de ce qu'on lui donne, et gèle `specs` en tuple.

Aucun défaut n'est fourni pour l'hôte du broker ni pour l'exécutable `vclient` :
ce sont des **valeurs de site**, et le dépôt n'en porte aucune. Un test vérifie
qu'aucune adresse IP, aucun `localhost`, aucun chemin absolu et aucun terme de
secret n'apparaît dans le module.

## Point d'entrée — reporté

**Aucun point d'entrée n'est livré.** `pyproject.toml` ne déclare toujours pas
de `[project.scripts]`, et il n'existe ni `main()`, ni `__main__`, ni service.

Ce report est délibéré. Livrer une commande exigerait de trancher, sans
exigence écrite pour arbitrer :

- la **source** de la configuration — variables d'environnement, fichier TOML
  ou YAML, arguments de ligne de commande, ou combinaison ordonnée ;
- le **nom** et la **forme** des clés publiques, qui deviendraient une surface
  de compatibilité au même titre que les topics ;
- la gestion des **signaux** (`SIGTERM`, `SIGINT`) et son branchement sur le
  `StopSignal` ;
- la **journalisation** : format, niveau, destination ;
- le **mode de déploiement** — unité systemd, conteneur, ou lancement manuel.

Chacun de ces choix est une décision structurelle, donc arbitrable par l'humain
et non par le code. `build_runtime` est la brique sur laquelle un tel point
d'entrée se posera sans rien réécrire : il ne manque que ces arbitrages.

> Ces arbitrages ont depuis été répartis sur deux lots. La gestion des signaux
> et son branchement sur le `StopSignal` reviennent à C9
> (`c9-process-lifecycle.md`). La source de configuration, les noms des clés
> publiques, la journalisation, le mode de déploiement et le point d'entrée
> installé lui-même reviennent à C10, non encore ouvert.

## Surface publique du lot

| Symbole | Rôle |
|---|---|
| `StopSignal` | Protocole d'arrêt, `is_set() -> bool` |
| `NeverStop` | Signal qui ne demande jamais l'arrêt |
| `RuntimeConfig` | Configuration d'assemblage |
| `Runtime` | Assemblage prêt à tourner : `publisher`, `runner` |
| `ReadSurfaceRunner` | Boucle extérieure : `run()`, `publisher` |
| `build_runtime(config, stop) -> Runtime` | Construction et câblage |

`Runtime` expose `publisher` en plus de `runner` pour permettre d'inspecter
l'état sans passer par la boucle.

## Vérification

45 tests dans `tests/test_runtime.py`, dont :

- **intégration hors production** — vrai `ReadSurfacePublisher` et vrai runner,
  faux MQTT, faux lecteur, horloge virtuelle, arrêt virtuel. Le parcours
  `start → lectures initiales → cycle 30 s → battement → instantane → stop` est
  vérifié au comptage exact : 19 lectures (8 puis 3 puis 8), 2 sommeils de 30 s,
  une publication scalaire par lecture réussie, `online` en tête et `offline` en
  queue, aucun topic hors de la surface v1, `chain.status = ok` à la fin ;
- **`build_runtime`** — la frontière Paho est remplacée par un double via
  `monkeypatch` de `PahoMqttClient._build_client` ; `socket.socket`,
  `subprocess.run` et `subprocess.Popen` sont remplacés par des échecs
  immédiats, ce qui **prouve** que la construction n'ouvre ni socket ni
  processus.

Aucun adaptateur réel n'est jamais exercé contre une ressource réelle.

**Mutation testing** — 7 mutations appliquées à `runtime.py`, 7 tuées, aucune
survivante : attente d'une échéance passée, absence de reconsultation de l'arrêt
après l'attente, arrêt de secours indu, perte de l'erreur de boucle en cas de
double échec, absorption silencieuse de l'erreur de boucle, interception de
`BaseException`, perte de l'erreur d'arrêt de secours au démarrage. Le fichier a
été restauré à l'octet près (SHA-256 vérifié).

## Ce que ce lot ne fait pas

- Aucun point d'entrée, aucune commande, aucun service, aucune unité systemd ;
- aucune gestion de signaux ;
- aucune journalisation ;
- aucun thread, aucun `asyncio`, aucun modèle de concurrence imposé ;
- aucune écriture chaudière — le noyau transactionnel de C3 n'est pas câblé ;
- aucune politique de reprise, de nouvelle tentative ou de reconnexion ;
- aucune réduction de la latence d'arrêt ;
- aucune valeur de site, aucun secret.

La limite déjà connue de C7-C3A reste entière : après une déconnexion
inattendue suivie d'une reconnexion automatique de Paho, `bridge/online` retenu
peut rester à `offline` jusqu'au prochain `start()`. La frontière n'expose aucun
rappel de connexion et C7-B ne couvre pas la reconnexion.
