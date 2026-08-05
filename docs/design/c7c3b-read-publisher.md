# C7-C3B — Lectures dues, publications scalaires, cadences et battement

## Objet

Second sous-lot de C7-C3. Il complete `ReadSurfacePublisher` : lecture des
mesures echues, publication des valeurs scalaires, cloture de cycle,
republication periodique de l'instantane et battement.

A l'issue de ce lot, le publieur honore la surface de lecture v1 dans son
entier — a une exception documentee pres, la reprise apres reconnexion.

## Sections contractuelles honorees

| Section de `c7-mqtt-read-contract.md` | Traitement |
|---|---|
| §4.4 — publication scalaire | uniquement apres `OK`, QoS 1 retenu, aucune sentinelle |
| §4.5 — representation | `format_scalar` |
| §4.6 — ordre par mesure | scalaire, puis etat, puis instantane |
| §7.2 — periodes et seuils | echeance par mesure, tiree de `MeasurementSpec` |
| §7.3 — comportements de fraicheur | issus de C7-C2, inchanges |
| §7.4 — cadence de l'instantane | republication periodique, borne verifiee |
| §8.2 — cycle et `chain` | cloture sur l'ensemble reellement tente |
| §9 — battement | QoS 0, non retenu, desactivable |
| §11 — surface close | seuls les onze suffixes sont publies |

## Dependances injectees

```python
ReadSurfacePublisher(
    mqtt: MqttClient,          # C2 — frontiere, jamais Paho directement
    clock: Clock,              # C2 — murale ET monotone
    reader: MeasurementReader, # protocole etroit, voir plus bas
    specs: Sequence[MeasurementSpec] = V1_MEASUREMENTS,
    config: ReadSurfaceConfig | None = None,
)
```

Aucun adaptateur n'est construit ici. Le composant n'est pas une composition
root : il possede le cycle `connect` / `disconnect` d'un client **injecte**,
rien de plus.

### Pourquoi un protocole `MeasurementReader`

Ni l'un ni l'autre des types existants ne convenait :

- **`boilerack.transport.vclient.VClient`** exige `read` **et** `write`, et C6 a
  etabli que son lecteur ne doit PAS le satisfaire tant que l'ecriture n'est pas
  caracterisee — un `write` bouchon conduirait le moteur a conclure `applied`
  pour une ecriture jamais tentee. L'annoter ainsi serait faux ;
- **`boilerack.adapters.vclient_cli.VClientCliReader`** est une classe concrete
  d'adaptateur. L'importer ferait dependre `read_surface` de `adapters`, et
  chargerait `subprocess` par transitivite.

Un protocole structurel a une seule methode resout les deux : `VClientCliReader`
le satisfait **sans qu'aucun import ne les relie**.

## Definition du cycle

Un cycle est la tentative de lecture de **l'ensemble des mesures dues a cet
instant** (§8.2). Ce n'est donc pas necessairement les huit :

- au demarrage, les huit sont dues ;
- a +30 s, seules les trois temperatures ;
- a +60 s, les huit de nouveau ;
- a un reveil ou rien n'est du, **il n'y a pas de cycle** : `complete_cycle`
  n'est pas appele, `chain` reste celui du dernier cycle **termine**.

Les lectures sont **sequentielles** : C6 n'accepte qu'une commande par
invocation, la virgule y est refusee et le groupement `-c` n'est pas
caracterise. L'ordre est celui des specs — celui de la table §4.2 — jamais un
tri alphabetique. Un role est lu **au plus une fois** par appel, par
construction : la liste des dues est derivee des specs, dont les roles sont
uniques.

## Ordre par mesure

```
lecture OK   -> format_scalar -> publication scalaire -> record_result(OK) -> instantane
lecture non-OK ->                                        record_result(statut)
```

§4.6 n'impose l'instantane **qu'apres une lecture reussie** : un echec ne
declenche aucun instantane intermediaire. Il apparaitra dans celui de fin de
cycle.

## Etat et valeur ephemere

La valeur d'un `ReadResult` **ne traverse jamais l'etat** :

```
lecture -> publication scalaire -> projection d'etat -> instantane
```

Elle reste locale a l'iteration. Ni `value`, ni `raw`, ni `detail` ne sont
conserves — §6.6 interdit d'ailleurs de publier un message brut, un chemin local
ou un `stderr`. L'etat est une **projection des issues**.

Le publieur detient : l'etat courant, les specs (copie immuable), les echeances
par role, celle de l'instantane periodique, celle du battement si active, et son
drapeau de cycle de vie.

## Politique d'erreur MQTT

Les erreurs de publication sont **collectees, jamais absorbees**, puis levees en
fin d'appel dans un `ExceptionGroup`, dans l'ordre de survenue, exceptions
d'origine preservees.

| Ce qui echoue | Consequence |
|---|---|
| publication scalaire | l'etat enregistre quand meme `OK` — §4.6 : « `last_result` porte l'issue de la **lecture**, jamais celle de la publication MQTT » |
| instantane intermediaire | collecte, cycle poursuivi |
| instantane de fin de cycle | collecte ; §4.6 renvoie a la republication periodique (§7.4), qui retablira l'etat courant **si le broker est redevenu joignable** — une tentative echouee repousse l'echeance comme une reussite, si bien que l'intervalle borne est celui des TENTATIVES, non celui des publications effectives |
| battement | collecte |

Une erreur de publication ne **transforme jamais** un statut, n'influence pas
`chain`, ne supprime aucun resultat de lecture et n'arrete pas le cycle. Aucune
taxonomie metier n'est creee — §4.6 : « Aucune taxonomie d'erreur de publication
MQTT n'est definie en v1 ».

Seules les `Exception` sont interceptees. `KeyboardInterrupt`, `SystemExit` et
`GeneratorExit` remontent immediatement et inchangees, jamais groupees.

Ce choix — collecter puis lever — s'aligne sur le traitement du double echec de
`stop()` : rien n'est tu, rien n'est converti.

## Exception inattendue du lecteur

C6 garantit qu'aucune issue de transport ne leve : toute exception du lecteur
signale donc un **defaut**, non un incident de transport. La convertir en
`TransportStatus` le maquillerait.

Elle **remonte telle quelle, immediatement**. Consequences, toutes assumees :

- le cycle **n'est pas cloture** — aucun `chain` n'est fabrique sur un cycle
  incomplet ;
- les mesures deja traitees restent **projetees et replanifiees** ;
- les mesures non traitees restent **dues** ;
- les erreurs de publication deja collectees sont **perdues** : les grouper avec
  un defaut le noierait.

## Echeances monotones et absence de rattrapage

Toutes les echeances sont **monotones** — un reglage de l'horloge systeme ne les
fausse pas — et aucune valeur monotone n'est jamais publiee (§6.4).

Apres chaque tentative :

```
next_due[role]      = monotonic_apres_la_tentative + spec.period_s
next_snapshot_due   = monotonic_apres_la_tentative + snapshot_period_s
next_heartbeat_due  = monotonic_apres_la_tentative + heartbeat_period_s
```

**Aucun rattrapage.** Un reveil tardif ne declenche jamais de rafale : dix
periodes manquees produisent **une** lecture, pas dix, et la prochaine echeance
repart de la fin de la tentative — jamais de l'echeance theorique manquee.

C'est une **decision d'implementation, pas une clause normative**. §7 pose deja
que les periodes cibles ne sont pas garanties, et §15.9 range les cadences
reellement atteignables parmi les inconnues. L'inscrire au contrat
sur-contraindrait tout producteur conforme.

Rappel du chiffrage C5 : une lecture reelle coute 2,7 a 4,0 s, soit 21,6 a
32,0 s pour un cycle de huit — au-dela de la periode cible de 30 s des
temperatures. Le facteur 3 de `fresh_max` (90 s) absorbe ce depassement.

### Echeances initiales

Au `start()`, apres l'instantane initial, **toutes les mesures deviennent
immediatement dues**. Le contrat ne dit pas quand la premiere lecture doit avoir
lieu ; c'est la lecture la plus fidele : §7.3 exige que l'instantane initial
precede toute lecture — ce qui est le cas — et rien n'impose d'attendre une
periode entiere avant la premiere donnee. Le demarrage est le premier reveil.

L'instantane et le battement, eux, sont planifies a `+ periode`. **Aucun
battement n'est publie dans `start()`** : §9 ne l'exige pas, et le publier
laisserait croire a une vitalite que rien n'a encore etablie.

## Instantane : trois declencheurs

| Declencheur | Clause |
|---|---|
| apres chaque lecture **reussie** | §4.6 etape 3, **MUST** |
| a la **cloture** du cycle | non impose ; c'est l'instant ou `chain` change, et il est publie meme si toutes les lectures ont echoue |
| **periodiquement** | §7.4, **MUST** — « meme si rien n'a change », avec un `ts` a jour |

Toute publication **tentee** de l'instantane repousse l'echeance periodique :
§7.4 borne un intervalle **maximal**, publier plus souvent reste conforme, et
republier deux fois le meme etat dans un seul appel n'apporterait rien. Un
`run_due()` ne publie donc jamais deux instantanes consecutifs identiques.

Cout assume de la conformite litterale a §4.6 : jusqu'a huit instantanes par
cycle complet. Substituer la lecture economique reviendrait a remplacer un MUST
par une preference.

## Battement

Actif par defaut, **desactivable** — §9 : « Un producteur **MAY** l'omettre s'il
documente la rupture ». `heartbeat_period_s = None` supprime l'echeance, la
publication et le topic.

```
topic   : <prefix>/bridge/heartbeat
payload : {"ts":"2026-08-05T12:00:00Z"}
QoS     : 0        retain : false
```

Aucun champ supplementaire. L'horodatage emploie exactement la meme forme
RFC 3339 UTC que l'instantane ; un test compare les deux a instant egal, ce qui
interdit toute derive entre les formateurs.

Le battement **n'atteste que de l'activite du processus**. §9 : il ne porte
aucune autorite fonctionnelle, aucune sante de la chaudiere ne doit en etre
deduite, et il reste candidat a la depreciation.

## Configuration

```python
ReadSurfaceConfig(
    prefix: str = "boiler",
    snapshot_period_s: int = 30,
    heartbeat_period_s: int | None = 30,
)
```

`prefix` est normalise a la construction (§3.3), inchange depuis C7-C3A.

`snapshot_period_s` et `heartbeat_period_s` sont des entiers stricts,
strictement positifs, booleens refuses. La borne haute de §7.4 — « inferieure ou
egale au plus petit `fresh_max` de la surface » — **depend des specs
reellement injectees**, que la configuration ne connait pas : elle est donc
verifiee dans `ReadSurfacePublisher.__init__`, contre les specs recues et non
contre une constante globale. Avec `V1_MEASUREMENTS`, le plafond est **90 s**.

Aucun topic complet n'est stocke ; `MqttConfig` n'est ni modifie ni reutilise.

## API publique

```
start()   stop()   due_at()   run_due()   state   will()
```

Plus, en lecture seule : `online_topic`, `status_topic`, `heartbeat_topic`,
`started`, `due_measurements()`.

`due_at()` rend l'instant monotone de la prochaine echeance, toutes categories
confondues. Il ne lit pas l'horloge murale, ne modifie aucun etat, ne publie
rien, et **leve avant `start()`**.

Ne sont **pas** exposes, faute de consommateur : `publish_snapshot()`,
`publish_heartbeat()`, `read_cycle()`, un type `CycleResult`, un ordonnanceur.
Aucun module separe n'a ete cree.

## Ordre dans `run_due()`

1. instant monotone capture **une seule fois** — l'ensemble des taches dues ne
   change plus pendant l'appel, meme si les lectures durent ;
2. mesures dues, dans l'ordre des specs, lues sequentiellement ;
3. cloture du cycle, **uniquement** si au moins une mesure etait due ;
4. instantane de fin de cycle ;
5. instantane periodique, **seulement** s'il n'a pas deja ete publie ;
6. battement du ;
7. `ExceptionGroup` des erreurs collectees.

L'horloge est relue **apres chaque tentative**, mais uniquement pour recalculer
une echeance — jamais pour rendre une tache due en cours d'appel.

## Aucune boucle interne

Il n'existe ni `run_forever()`, ni thread, ni `asyncio`, ni sommeil, ni signal.
L'appelant interroge `due_at()` puis appelle `run_due()`. Tout ordonnancement
reel suppose des decisions de deploiement — service, supervision, arret
gracieux — que ce lot n'a pas a prendre.

## Reports et limitations

| Element | Etat |
|---|---|
| Composition root, CLI, service systemd, installation | **hors perimetre** |
| Boucle, thread, signaux OS | **hors perimetre** |
| Politique de reconnexion | **hors perimetre**, et non contractee : le mot « reconnexion » ne figure pas dans C7-B, §15.5 range la session du broker parmi les inconnues |
| Reprise du retenu `bridge/online` apres reconnexion | **limitation connue** : apres une deconnexion inattendue suivie d'une reconnexion native de Paho, le retenu peut rester `offline` jusqu'au prochain `start()`. La frontiere n'expose aucun rappel de connexion |
| Ecriture, chemin transactionnel | **hors perimetre** |
| Migration du pont historique | **hors perimetre** |

**AUCUNE CONFORMITE PRODUCTION N'EST REVENDIQUEE.** Rien n'a ete eprouve contre
un broker, un demon `vcontrold` ou une chaudiere reels. Tous les tests sont hors
ligne, sur doubles deterministes.
