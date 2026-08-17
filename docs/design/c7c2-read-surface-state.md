# C7-C2 — Déclaration, état de lecture, cycles et instantané

## Objet

Deuxième lot d'implémentation de la surface MQTT de lecture. Il livre la
**déclaration des huit mesures**, l'**état durable** de lecture, la **clôture de
cycle** et la construction de l'**instantané** `bridge/telemetry_status`.

Tout y est pur : aucune lecture `vclient`, aucun client MQTT, aucune
publication, aucun testament, aucun ordonnanceur, aucune boucle, aucun thread.
L'horloge est toujours injectée ; aucune horloge système n'est lue.

## Sections contractuelles honorées

| Section de `c7-mqtt-read-contract.md` | Traitement |
|---|---|
| §4.2 — table normative des mesures | `V1_MEASUREMENTS` |
| §6.2 — forme de l'instantané | `build_snapshot`, `snapshot_to_json` |
| §6.3 — `schema` | constante interne, version 1 |
| §6.4 — `ts` RFC 3339 UTC, monotone jamais exposé | formateur interne |
| §6.5 — champs orthogonaux et invariants | `MeasurementState` |
| §6.6 — taxonomie publique | `PublicResult` et correspondance explicite |
| §7.2 — `fresh_max` par défaut `3 × P`, invariant strict | `default_fresh_max`, `MeasurementSpec` |
| §7.3 — comportements de fraîcheur | `record_result`, calcul de `fresh` |
| §8.2 — cycle, `chain.status`, `chain.cause` | `complete_cycle` |

Aucune autre section n'est touchée.

## Déclaration v1

`MeasurementSpec` porte cinq champs : `role`, `read`, `suffix`, `period_s`,
`fresh_max_s`. **Rien d'autre** — ni unité, ni type métier, ni forme scalaire,
ni valeur, ni bornes, ni tolérance, ni source de bornes.

`boilerack.core.profile.CommandSpec` n'est pas réutilisé : il exige `min`,
`max`, `step`, `confirm_tolerance` et surtout `bounds_source`, dont **aucune**
n'existe pour ces huit mesures. Les remplir reviendrait à inventer une
provenance, ce que le projet s'interdit.

`read` et `suffix` n'ont **aucun consommateur d'exécution dans ce lot** : la
transition d'état ne dépend que du statut, et l'instantané s'indexe par rôle.
Ils sont déclarés parce que cette structure transcrit la table normative §4.2
dans son entier — comme `V1_SUFFIXES` transcrit §11 en C7-C1 — et parce que
C7-C3 les consommera sans avoir à modifier une structure déjà livrée. La
distinction est énoncée plutôt que masquée.

`fresh_max_s` passe par `default_fresh_max(period_s)` dans la déclaration :
la règle `3 × P` reste visible, et le champ demeure stocké parce que §7.2 permet
de le configurer par mesure.

### Trois couches d'invariants, jamais confondues

| Couche | Contenu | Où |
|---|---|---|
| **Mesure générique** | chaînes non vides · entiers stricts, booléens refusés · `fresh_max_s > period_s` (§7.2, **MUST** contractuel) | `MeasurementSpec.__post_init__` |
| **Collection** | unicité des rôles · unicité des suffixes | `_check_collection` |
| **Conformité v1** | exactement huit · rôles, commandes, suffixes, périodes et seuils exacts · égalité ordonnée avec `TELEMETRY_SUFFIXES` | **tests** |

Aucune classe générique n'impose le nombre huit. L'unicité des `read` n'est pas
imposée non plus : le contrat n'interdit nulle part que deux rôles partagent une
commande. Les huit de la v1 sont distincts, ce que les tests **constatent** sans
en faire une règle.

## État durable

```
MeasurementState (gelee)
    last_success_wall      : datetime | None    UTC, publie dans `last_success`
    last_success_monotonic : float | None       JAMAIS publie
    last_result            : TransportStatus | None
    has_value              : propriete derivee
```

`has_value` est **dérivé**, jamais stocké : l'état incohérent
`has_value=True / last_success=None` devient structurellement impossible, ce
qu'exige l'équivalence de §6.5.

Les deux estampilles sont **solidaires** : posées ensemble sur le même succès,
ou nulles ensemble. Un `datetime` naïf est refusé — il serait publié avec un
suffixe `Z` mensonger ; un instant porteur d'un autre fuseau est converti,
jamais réinterprété.

```
ReadSurfaceState (gelee)
    measurements    : Mapping[str, MeasurementState]   vue en lecture seule
    chain_status    : ChainStatus                       initial UNAVAILABLE
    chain_cause     : TransportStatus | None            initial None
    cycle_completed : bool                              initial False
```

`measurements` est remplacé à la construction par un `MappingProxyType` sur une
**copie privée** : un `dict` placé dans une dataclass gelée resterait mutable de
l'extérieur, ce qui viderait `frozen=True` de son sens. Deux tests le
verrouillent — mutation directe refusée, et mutation du dictionnaire source sans
effet sur l'état construit.

## La valeur scalaire est volontairement absente

Aucun champ de valeur n'existe, à aucun niveau. Ce n'est pas un oubli :

- l'instantané §6.2 ne porte **aucune valeur** — cinq champs par mesure, listés
  en §6.5, et la valeur n'en fait pas partie ;
- **aucune clause** n'exige de rediffuser un scalaire sans nouvelle lecture.
  §7.4 ne prescrit la republication périodique que de l'**instantané** ;
- le contrat **ne traite pas la reconnexion** — le mot n'y figure pas — et range
  la politique de rétention et d'expiration de session du broker parmi les
  **inconnues** (§15.5) ;
- §12 interdit de « présenter une valeur retenue comme fraîche sans le topic de
  fraîcheur ». Un champ de valeur stocké inviterait précisément la republication
  silencieuse d'une valeur périmée.

Le retain du broker n'est **pas** la mémoire métier du bridge : §4.4 dit qu'une
valeur retenue **MAY** subsister côté broker, et §15.5 déclare la politique de
rétention non déductible. La raison de ne rien stocker n'est donc pas une
délégation au broker, mais l'**absence de consommateur contractuel**.

## Flux futur

```
lecture → publication scalaire + projection d'etat → instantane
```

La formule `lecture → etat → livraison` serait trompeuse : elle laisserait croire
que la valeur transite par l'état. Elle n'y transite pas.

```
pour chaque mesure due :
    r = reader.read(spec.read)                       ReadResult, portee du cycle
    si r.status is OK :
        publier format_scalar(r.value)               §4.6 etape 1
    state = record_result(state, role, r.status, clock)   §4.6 etape 2
    [publication eventuelle de l'instantane]         §4.6 etape 3

fin de cycle :
    state = complete_cycle(state, {role: r.status ...})
    publier snapshot_to_json(build_snapshot(state, V1_MEASUREMENTS, clock))
```

La valeur va du `ReadResult` au payload **sans traverser l'état**. L'état est une
**projection des issues**. `raw` et `detail` ne quittent jamais le lecteur :
§6.6 interdit de publier un message système brut, un chemin local, un `stderr`
complet ou un nom d'exception.

## `record_result` et `complete_cycle`

Deux fonctions, et non une seule, parce que §4.6 impose — après une lecture
réussie — l'ordre : publier le scalaire, puis mettre à jour l'état **de la
mesure**, puis publier l'instantané. Un unique appel en fin de cycle rendrait
cette séquence par mesure impossible. La granularité fine sert les **deux**
lectures possibles de §4.6 sans préjuger : c'est C7-C3 qui choisira la cadence
de publication de l'instantané.

| Fonction | Fait | Ne fait pas |
|---|---|---|
| `record_result(state, role, status, clock)` | transition d'une mesure, succès **et** échec | ne touche pas `chain` ; ne reçoit aucune valeur |
| `complete_cycle(state, results)` | dérive `chain_status`, `chain_cause`, `cycle_completed` | ne lit aucune horloge ; ne modifie aucune mesure |

Un échec **ne périme pas** la dernière valeur connue : les estampilles restent
inchangées, seul `last_result` bouge (§7.3).

### Refus

`record_result` refuse un rôle inconnu, un statut qui n'est pas un
`TransportStatus`, une horloge murale naïve, un monotone non fini, et un **recul
monotone détectable par rapport au dernier succès de cette mesure**. Le contrôle
est **local** : aucune cohérence globale d'horloge entre mesures différentes
n'est supposée.

`complete_cycle` refuse un ensemble **vide**, un rôle inconnu, un statut
invalide, et une **incohérence** entre le statut annoncé et le `last_result`
courant — ce dernier contrôle transforme la redondance apparente en vérification
que `record_result` a bien été appelé.

Le refus du cycle vide est délibéré : §8.2 définit un cycle comme la tentative
de lecture « des mesures **dues à cet instant** ». Un ensemble vide satisferait
vacuement « terminé » et basculerait `chain` en `unavailable` — régression
manifeste. Le refus oblige l'appelant à ne pas clôturer quand rien n'est dû.

### Limite assumée — les doublons ne sont pas détectables

`complete_cycle` reçoit un `Mapping`. Un dictionnaire littéral a **déjà écrasé**
toute clef répétée avant l'appel : la fonction ne peut pas savoir qu'un rôle a
été tenté deux fois dans le cycle. Cette garantie n'est donc **pas revendiquée**.
Elle appartiendra au futur collecteur C7-C3, ou exigerait une API séquentielle
distincte. Aucun test ne prétend le contraire.

## Horloges murale et monotone

`Clock` (C2) suffit : aucune abstraction nouvelle n'est introduite.

| Usage | Horloge | Publié ? |
|---|---|---|
| `ts` de l'instantané, `last_success` | murale, UTC | **oui** |
| `age_s` | **monotone** | jamais la valeur brute |

Le même succès estampille les deux. §6.4 interdit d'**exposer** une horloge
monotone, pas de s'en servir : mesurer l'âge sur le compteur monotone rend
`age_s` insensible à un réglage de l'horloge système, sans qu'aucune valeur
monotone n'apparaisse dans le payload. Un test vérifie qu'une valeur monotone
distinctive n'apparaît nulle part dans le JSON.

`VirtualClock` fait avancer mural et monotone **ensemble** : un double local est
utilisé dans les tests pour les dissocier.

## Âge et fraîcheur

```
age_s = floor(monotonic_now − last_success_monotonic)      None avant tout succes
fresh = (age_s is not None) and (age_s <= fresh_max_s)
```

- `age_s` est un **entier ≥ 0**, type imposé par §6.5 ; `None` si et seulement si
  `last_success` est nul, comme l'exige l'invariant ;
- troncature à la seconde inférieure : nombre de secondes **entières** écoulées,
  lecture conventionnelle d'un âge. Conséquence assumée : à la frontière de
  fraîcheur, l'âge rapporté peut être optimiste de moins d'une seconde ;
- la borne est **inclusive** — §6.5 : « `age_s` est inférieur ou **égal** au
  seuil » ;
- la comparaison porte sur `age_s`, **l'entier publié**, et non sur le delta
  flottant : le consommateur doit pouvoir refaire le calcul à partir de ce qu'il
  lit ;
- un recul du monotone **lève**. Borner à zéro publierait la fraîcheur maximale
  pour une horloge cassée : le pire mensonge possible.

## Correspondance publique des statuts

Une table **explicite** traduit les six issues internes en `PublicResult`.
`status.value` ne peut pas servir :

```
TransportStatus.UNKNOWN_COMMAND.value == "unknown_command"
valeur publique contractuelle          == "unsupported_command"
```

§6.6 précise d'ailleurs que cette correspondance **MAY** évoluer, les valeurs
publiques restant stables — raison de plus pour qu'elle soit une table, et non
une propriété de l'énumération interne. La table reste **privée** : aucune API
externe n'en a besoin.

`chain_cause` est stocké en `TransportStatus` et traduit au seul moment du rendu,
ce qui garde la frontière interne/publique en un point unique.

## Instantané

Quatre clefs globales — `schema`, `ts`, `chain`, `measurements` — et **cinq** par
mesure : `has_value`, `fresh`, `last_success`, `age_s`, `last_result`. Aucune
autre. Des tests verrouillent l'ensemble de clefs **exact**, et l'absence de
`value`, `raw`, `detail`, `last_attempt`, `status` et `unit`.

`build_snapshot` rend un dictionnaire ; `snapshot_to_json` le sérialise. Même
séparation que `ack_to_dict` / `ack_to_json` en C3, et même idiome :
`separators=(",", ":")`, `sort_keys=True`, `ensure_ascii=False`,
**`allow_nan=False`**, encodage UTF-8 explicite.

`boilerack._legacy.primitives.json_dumps` n'est **pas** réutilisé : il ne passe
pas `allow_nan=False` et émet donc `NaN` et `Infinity`, comportement classé
accident dans `provenance.md`.

L'ordre des clefs du JSON est **déterministe par tri**, non contractuel :
l'ordre montré par l'exemple §6.2 est illustratif et le contrat ne le déclare
nulle part normatif. Le dictionnaire rendu par `build_snapshot`, lui, suit
l'ordre de `specs`.

## Frontières

Non modifiés : `transport/`, `adapters/`, `core/`, `testing/`, `_legacy/`,
`pyproject.toml`, `.github/`, `read_surface/topics.py`,
`read_surface/payload.py`. Seul `read_surface/__init__.py` est modifié, pour
ajouter les exports. Aucune dépendance ajoutée.

Les trois modules n'importent ni `paho`, ni `socket`, ni `subprocess`, ni
`threading`, ni `asyncio`, ni `time`, et n'appellent jamais `datetime.now()`,
`utcnow()`, `time.monotonic()` ni `time.time()`. Des tests structurels le figent
par analyse du code source.

## Reports vers C7-C3

| Élément | Raison du report |
|---|---|
| Testament MQTT et présence `bridge/online` (§5) | exige d'étendre la frontière `MqttClient`, qui ne porte aujourd'hui aucun testament |
| Publieur, ordre de publication (§4.4, §4.6) | seul lot qui touchera à MQTT |
| Battement (§9) | `SHOULD`, compatibilité historique |
| Cadences et republication de l'instantané (§7.4) | relève de l'ordonnancement |
| Ordonnancement séquentiel, échéances, règle sans rattrapage | non contractuel ; décision d'implémentation |
| Garantie « un rôle au plus une fois par cycle » | appartient au collecteur |

## Tests

**204 cas**, issus de **126 fonctions** — mesures 67, état 67, instantané 70.
Tous déterministes, hors ligne, sans marqueur pytest. Aucun processus, aucun
socket, aucun broker, aucun `vclient`, aucune attente réelle.
