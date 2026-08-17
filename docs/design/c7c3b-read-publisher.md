# C7-C3B — Lectures dues, publications scalaires, cadences et battement

## Objet

Second sous-lot de C7-C3. Il complète `ReadSurfacePublisher` : lecture des
mesures échues, publication des valeurs scalaires, clôture de cycle,
republication périodique de l'instantané et battement.

À l'issue de ce lot, le publieur honore la surface de lecture v1 dans son
entier — à une exception documentée près, la reprise après reconnexion.

## Sections contractuelles honorées

| Section de `c7-mqtt-read-contract.md` | Traitement |
|---|---|
| §4.4 — publication scalaire | uniquement après `OK`, QoS 1 retenu, aucune sentinelle |
| §4.5 — représentation | `format_scalar` |
| §4.6 — ordre par mesure | scalaire, puis état, puis instantané |
| §7.2 — périodes et seuils | échéance par mesure, tirée de `MeasurementSpec` |
| §7.3 — comportements de fraîcheur | issus de C7-C2, inchangés |
| §7.4 — cadence de l'instantané | republication périodique, borne vérifiée |
| §8.2 — cycle et `chain` | clôture sur l'ensemble réellement tenté |
| §9 — battement | QoS 0, non retenu, désactivable |
| §11 — surface close | seuls les onze suffixes sont publiés |

## Dépendances injectées

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
root : il possède le cycle `connect` / `disconnect` d'un client **injecté**,
rien de plus.

### Pourquoi un protocole `MeasurementReader`

Ni l'un ni l'autre des types existants ne convenait :

- **`boilerack.transport.vclient.VClient`** exige `read` **et** `write`, et C6 a
  établi que son lecteur ne doit PAS le satisfaire tant que l'écriture n'est pas
  caractérisée — un `write` bouchon conduirait le moteur à conclure `applied`
  pour une écriture jamais tentée. L'annoter ainsi serait faux ;
- **`boilerack.adapters.vclient_cli.VClientCliReader`** est une classe concrète
  d'adaptateur. L'importer ferait dépendre `read_surface` de `adapters`, et
  chargerait `subprocess` par transitivité.

Un protocole structurel a une seule méthode résout les deux : `VClientCliReader`
le satisfait **sans qu'aucun import ne les relie**.

## Définition du cycle

Un cycle est la tentative de lecture de **l'ensemble des mesures dues à cet
instant** (§8.2). Ce n'est donc pas nécessairement les huit :

- au démarrage, les huit sont dues ;
- à +30 s, seules les trois températures ;
- à +60 s, les huit de nouveau ;
- à un réveil où rien n'est dû, **il n'y a pas de cycle** : `complete_cycle`
  n'est pas appelé, `chain` reste celui du dernier cycle **terminé**.

Les lectures sont **séquentielles** : C6 n'accepte qu'une commande par
invocation, la virgule y est refusée et le groupement `-c` n'est pas
caractérisé. L'ordre est celui des specs — celui de la table §4.2 — jamais un
tri alphabétique. Un rôle est lu **au plus une fois** par appel, par
construction : la liste des dues est dérivée des specs, dont les rôles sont
uniques.

## Ordre par mesure

```
lecture OK   -> format_scalar -> publication scalaire -> record_result(OK) -> instantane
lecture non-OK ->                                        record_result(statut)
```

§4.6 n'impose l'instantané **qu'après une lecture réussie** : un échec ne
déclenche aucun instantané intermédiaire. Il apparaîtra dans celui de fin de
cycle.

## État et valeur éphémère

La valeur d'un `ReadResult` **ne traverse jamais l'état** :

```
lecture -> publication scalaire -> projection d'etat -> instantane
```

Elle reste locale à l'itération. Ni `value`, ni `raw`, ni `detail` ne sont
conservés — §6.6 interdit d'ailleurs de publier un message brut, un chemin local
ou un `stderr`. L'état est une **projection des issues**.

Le publieur détient : l'état courant, les specs (copie immuable), les échéances
par rôle, celle de l'instantané périodique, celle du battement si active, et son
drapeau de cycle de vie.

## Politique d'erreur MQTT

Les erreurs de publication sont **collectées, jamais absorbées**, puis levées en
fin d'appel dans un `ExceptionGroup`, dans l'ordre de survenue, exceptions
d'origine préservées.

| Ce qui échoue | Conséquence |
|---|---|
| publication scalaire | l'état enregistre quand même `OK` — §4.6 : « `last_result` porte l'issue de la **lecture**, jamais celle de la publication MQTT » |
| instantané intermédiaire | collecte, cycle poursuivi |
| instantané de fin de cycle | collecte ; §4.6 renvoie à la republication périodique (§7.4), qui rétablira l'état courant **si le broker est redevenu joignable** — une tentative échouée repousse l'échéance comme une réussite, si bien que l'intervalle borné est celui des TENTATIVES, non celui des publications effectives |
| battement | collecte |

Une erreur de publication ne **transforme jamais** un statut, n'influence pas
`chain`, ne supprime aucun résultat de lecture et n'arrête pas le cycle. Aucune
taxonomie métier n'est créée — §4.6 : « Aucune taxonomie d'erreur de publication
MQTT n'est définie en v1 ».

Seules les `Exception` sont interceptées. `KeyboardInterrupt`, `SystemExit` et
`GeneratorExit` remontent immédiatement et inchangées, jamais groupées.

Ce choix — collecter puis lever — s'aligne sur le traitement du double échec de
`stop()` : rien n'est tu, rien n'est converti.

## Exception inattendue du lecteur

C6 garantit qu'aucune issue de transport ne lève : toute exception du lecteur
signale donc un **défaut**, non un incident de transport. La convertir en
`TransportStatus` le maquillerait.

Elle **remonte telle quelle, immédiatement**. Conséquences, toutes assumées :

- le cycle **n'est pas clôturé** — aucun `chain` n'est fabriqué sur un cycle
  incomplet ;
- les mesures déjà traitées restent **projetées et replanifiées** ;
- les mesures non traitées restent **dues** ;
- les erreurs de publication déjà collectées sont **perdues** : les grouper avec
  un défaut le noierait.

## Échéances monotones et absence de rattrapage

Toutes les échéances sont **monotones** — un réglage de l'horloge système ne les
fausse pas — et aucune valeur monotone n'est jamais publiée (§6.4).

Après chaque tentative :

```
next_due[role]      = monotonic_apres_la_tentative + spec.period_s
next_snapshot_due   = monotonic_apres_la_tentative + snapshot_period_s
next_heartbeat_due  = monotonic_apres_la_tentative + heartbeat_period_s
```

**Aucun rattrapage.** Un réveil tardif ne déclenche jamais de rafale : dix
périodes manquées produisent **une** lecture, pas dix, et la prochaine échéance
repart de la fin de la tentative — jamais de l'échéance théorique manquée.

C'est une **décision d'implémentation, pas une clause normative**. §7 pose déjà
que les périodes cibles ne sont pas garanties, et §15.9 range les cadences
réellement atteignables parmi les inconnues. L'inscrire au contrat
sur-contraindrait tout producteur conforme.

Rappel du chiffrage C5 : une lecture réelle coûte 2,7 à 4,0 s, soit 21,6 à
32,0 s pour un cycle de huit — au-delà de la période cible de 30 s des
températures. Le facteur 3 de `fresh_max` (90 s) absorbe ce dépassement.

### Échéances initiales

Au `start()`, après l'instantané initial, **toutes les mesures deviennent
immédiatement dues**. Le contrat ne dit pas quand la première lecture doit avoir
lieu ; c'est la lecture la plus fidèle : §7.3 exige que l'instantané initial
précède toute lecture — ce qui est le cas — et rien n'impose d'attendre une
période entière avant la première donnée. Le démarrage est le premier réveil.

L'instantané et le battement, eux, sont planifiés à `+ periode`. **Aucun
battement n'est publié dans `start()`** : §9 ne l'exige pas, et le publier
laisserait croire à une vitalité que rien n'a encore établie.

## Instantané : trois déclencheurs

| Déclencheur | Clause |
|---|---|
| après chaque lecture **réussie** | §4.6 étape 3, **MUST** |
| à la **clôture** du cycle | non impose ; c'est l'instant où `chain` change, et il est publié même si toutes les lectures ont échoué |
| **périodiquement** | §7.4, **MUST** — « même si rien n'a changé », avec un `ts` à jour |

Toute publication **tentée** de l'instantané repousse l'échéance périodique :
§7.4 borne un intervalle **maximal**, publier plus souvent reste conforme, et
republier deux fois le même état dans un seul appel n'apporterait rien. Un
`run_due()` ne publie donc jamais deux instantanés consecutifs identiques.

Coût assumé de la conformité littérale à §4.6 : jusqu'à huit instantanés par
cycle complet. Substituer la lecture économique reviendrait à remplacer un MUST
par une préférence.

## Battement

Actif par défaut, **désactivable** — §9 : « Un producteur **MAY** l'omettre s'il
documente la rupture ». `heartbeat_period_s = None` supprime l'échéance, la
publication et le topic.

```
topic   : <prefix>/bridge/heartbeat
payload : {"ts":"2026-08-05T12:00:00Z"}
QoS     : 0        retain : false
```

Aucun champ supplémentaire. L'horodatage emploie exactement la même forme
RFC 3339 UTC que l'instantané ; un test compare les deux à instant égal, ce qui
interdit toute dérive entre les formateurs.

Le battement **n'atteste que de l'activité du processus**. §9 : il ne porte
aucune autorité fonctionnelle, aucune santé de la chaudière ne doit en être
déduite, et il reste candidat à la dépréciation.

## Configuration

```python
ReadSurfaceConfig(
    prefix: str = "boiler",
    snapshot_period_s: int = 30,
    heartbeat_period_s: int | None = 30,
)
```

`prefix` est normalisé à la construction (§3.3), inchangé depuis C7-C3A.

`snapshot_period_s` et `heartbeat_period_s` sont des entiers stricts,
strictement positifs, booléens refusés. La borne haute de §7.4 — « inférieure ou
égale au plus petit `fresh_max` de la surface » — **dépend des specs
réellement injectées**, que la configuration ne connaît pas : elle est donc
vérifiée dans `ReadSurfacePublisher.__init__`, contre les specs reçues et non
contre une constante globale. Avec `V1_MEASUREMENTS`, le plafond est **90 s**.

> Depuis C10, le publieur applique toujours cette règle au même endroit, mais
> il la **délègue** à `check_snapshot_period` — désormais l'autorité unique,
> partagée avec la validation de configuration qui doit refuser une valeur hors
> borne avant tout démarrage. Le comportement observable est inchangé.

Aucun topic complet n'est stocké ; `MqttConfig` n'est ni modifié ni réutilisé.

## API publique

```
start()   stop()   due_at()   run_due()   state   will()
```

Plus, en lecture seule : `online_topic`, `status_topic`, `heartbeat_topic`,
`started`, `due_measurements()`.

`due_at()` rend l'instant monotone de la prochaine échéance, toutes catégories
confondues. Il ne lit pas l'horloge murale, ne modifie aucun état, ne publie
rien, et **lève avant `start()`**.

Ne sont **pas** exposés, faute de consommateur : `publish_snapshot()`,
`publish_heartbeat()`, `read_cycle()`, un type `CycleResult`, un ordonnanceur.
Aucun module séparé n'a été créé.

## Ordre dans `run_due()`

1. instant monotone capture **une seule fois** — l'ensemble des tâches dues ne
   change plus pendant l'appel, même si les lectures durent ;
2. mesures dues, dans l'ordre des specs, lues séquentiellement ;
3. clôture du cycle, **uniquement** si au moins une mesure était due ;
4. instantané de fin de cycle ;
5. instantané périodique, **seulement** s'il n'a pas déjà été publié ;
6. battement dû ;
7. `ExceptionGroup` des erreurs collectées.

L'horloge est relue **après chaque tentative**, mais uniquement pour recalculer
une échéance — jamais pour rendre une tâche due en cours d'appel.

## Aucune boucle interne

Il n'existe ni `run_forever()`, ni thread, ni `asyncio`, ni sommeil, ni signal.
L'appelant interroge `due_at()` puis appelle `run_due()`. Tout ordonnancement
réel suppose des décisions de déploiement — service, supervision, arrêt
gracieux — que ce lot n'a pas à prendre.

## Reports et limitations

| Élément | État |
|---|---|
| Composition root, CLI, service systemd, installation | **hors périmètre** |
| Boucle, thread, signaux OS | **hors périmètre** |
| Politique de reconnexion | **hors périmètre**, et non contractée : le mot « reconnexion » ne figure pas dans C7-B, §15.5 range la session du broker parmi les inconnues |
| Reprise du retenu `bridge/online` après reconnexion | **limitation connue** : après une déconnexion inattendue suivie d'une reconnexion native de Paho, le retenu peut rester `offline` jusqu'au prochain `start()`. La frontière n'expose aucun rappel de connexion |
| Écriture, chemin transactionnel | **hors périmètre** |
| Migration du pont historique | **hors périmètre** |

**AUCUNE CONFORMITÉ PRODUCTION N'EST REVENDIQUÉE.** Rien n'a été éprouvé contre
un broker, un démon `vcontrold` ou une chaudière réels. Tous les tests sont hors
ligne, sur doubles déterministes.
