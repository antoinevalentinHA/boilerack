# C7-C2 — Declaration, etat de lecture, cycles et instantane

## Objet

Deuxieme lot d'implementation de la surface MQTT de lecture. Il livre la
**declaration des huit mesures**, l'**etat durable** de lecture, la **cloture de
cycle** et la construction de l'**instantane** `bridge/telemetry_status`.

Tout y est pur : aucune lecture `vclient`, aucun client MQTT, aucune
publication, aucun testament, aucun ordonnanceur, aucune boucle, aucun thread.
L'horloge est toujours injectee ; aucune horloge systeme n'est lue.

## Sections contractuelles honorees

| Section de `c7-mqtt-read-contract.md` | Traitement |
|---|---|
| §4.2 — table normative des mesures | `V1_MEASUREMENTS` |
| §6.2 — forme de l'instantane | `build_snapshot`, `snapshot_to_json` |
| §6.3 — `schema` | constante interne, version 1 |
| §6.4 — `ts` RFC 3339 UTC, monotone jamais expose | formateur interne |
| §6.5 — champs orthogonaux et invariants | `MeasurementState` |
| §6.6 — taxonomie publique | `PublicResult` et correspondance explicite |
| §7.2 — `fresh_max` par defaut `3 × P`, invariant strict | `default_fresh_max`, `MeasurementSpec` |
| §7.3 — comportements de fraicheur | `record_result`, calcul de `fresh` |
| §8.2 — cycle, `chain.status`, `chain.cause` | `complete_cycle` |

Aucune autre section n'est touchee.

## Declaration v1

`MeasurementSpec` porte cinq champs : `role`, `read`, `suffix`, `period_s`,
`fresh_max_s`. **Rien d'autre** — ni unite, ni type metier, ni forme scalaire,
ni valeur, ni bornes, ni tolerance, ni source de bornes.

`boilerack.core.profile.CommandSpec` n'est pas reutilise : il exige `min`,
`max`, `step`, `confirm_tolerance` et surtout `bounds_source`, dont **aucune**
n'existe pour ces huit mesures. Les remplir reviendrait a inventer une
provenance, ce que le projet s'interdit.

`read` et `suffix` n'ont **aucun consommateur d'execution dans ce lot** : la
transition d'etat ne depend que du statut, et l'instantane s'indexe par role.
Ils sont declares parce que cette structure transcrit la table normative §4.2
dans son entier — comme `V1_SUFFIXES` transcrit §11 en C7-C1 — et parce que
C7-C3 les consommera sans avoir a modifier une structure deja livree. La
distinction est enoncee plutot que masquee.

`fresh_max_s` passe par `default_fresh_max(period_s)` dans la declaration :
la regle `3 × P` reste visible, et le champ demeure stocké parce que §7.2 permet
de le configurer par mesure.

### Trois couches d'invariants, jamais confondues

| Couche | Contenu | Ou |
|---|---|---|
| **Mesure generique** | chaines non vides · entiers stricts, booleens refuses · `fresh_max_s > period_s` (§7.2, **MUST** contractuel) | `MeasurementSpec.__post_init__` |
| **Collection** | unicite des roles · unicite des suffixes | `_check_collection` |
| **Conformite v1** | exactement huit · roles, commandes, suffixes, periodes et seuils exacts · egalite ordonnee avec `TELEMETRY_SUFFIXES` | **tests** |

Aucune classe generique n'impose le nombre huit. L'unicite des `read` n'est pas
imposee non plus : le contrat n'interdit nulle part que deux roles partagent une
commande. Les huit de la v1 sont distincts, ce que les tests **constatent** sans
en faire une regle.

## Etat durable

```
MeasurementState (gelee)
    last_success_wall      : datetime | None    UTC, publie dans `last_success`
    last_success_monotonic : float | None       JAMAIS publie
    last_result            : TransportStatus | None
    has_value              : propriete derivee
```

`has_value` est **derive**, jamais stocke : l'etat incoherent
`has_value=True / last_success=None` devient structurellement impossible, ce
qu'exige l'equivalence de §6.5.

Les deux estampilles sont **solidaires** : posees ensemble sur le meme succes,
ou nulles ensemble. Un `datetime` naif est refuse — il serait publie avec un
suffixe `Z` mensonger ; un instant porteur d'un autre fuseau est converti,
jamais reinterprete.

```
ReadSurfaceState (gelee)
    measurements    : Mapping[str, MeasurementState]   vue en lecture seule
    chain_status    : ChainStatus                       initial UNAVAILABLE
    chain_cause     : TransportStatus | None            initial None
    cycle_completed : bool                              initial False
```

`measurements` est remplace a la construction par un `MappingProxyType` sur une
**copie privee** : un `dict` place dans une dataclass gelee resterait mutable de
l'exterieur, ce qui viderait `frozen=True` de son sens. Deux tests le
verrouillent — mutation directe refusee, et mutation du dictionnaire source sans
effet sur l'etat construit.

## La valeur scalaire est volontairement absente

Aucun champ de valeur n'existe, a aucun niveau. Ce n'est pas un oubli :

- l'instantane §6.2 ne porte **aucune valeur** — cinq champs par mesure, listes
  en §6.5, et la valeur n'en fait pas partie ;
- **aucune clause** n'exige de rediffuser un scalaire sans nouvelle lecture.
  §7.4 ne prescrit la republication periodique que de l'**instantane** ;
- le contrat **ne traite pas la reconnexion** — le mot n'y figure pas — et range
  la politique de retention et d'expiration de session du broker parmi les
  **inconnues** (§15.5) ;
- §12 interdit de « presenter une valeur retenue comme fraiche sans le topic de
  fraicheur ». Un champ de valeur stocke inviterait precisement la republication
  silencieuse d'une valeur perimee.

Le retain du broker n'est **pas** la memoire metier du bridge : §4.4 dit qu'une
valeur retenue **MAY** subsister cote broker, et §15.5 declare la politique de
retention non deductible. La raison de ne rien stocker n'est donc pas une
delegation au broker, mais l'**absence de consommateur contractuel**.

## Flux futur

```
lecture → publication scalaire + projection d'etat → instantane
```

La formule `lecture → etat → livraison` serait trompeuse : elle laisserait croire
que la valeur transite par l'etat. Elle n'y transite pas.

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

La valeur va du `ReadResult` au payload **sans traverser l'etat**. L'etat est une
**projection des issues**. `raw` et `detail` ne quittent jamais le lecteur :
§6.6 interdit de publier un message systeme brut, un chemin local, un `stderr`
complet ou un nom d'exception.

## `record_result` et `complete_cycle`

Deux fonctions, et non une seule, parce que §4.6 impose — apres une lecture
reussie — l'ordre : publier le scalaire, puis mettre a jour l'etat **de la
mesure**, puis publier l'instantane. Un unique appel en fin de cycle rendrait
cette sequence par mesure impossible. La granularite fine sert les **deux**
lectures possibles de §4.6 sans prejuger : c'est C7-C3 qui choisira la cadence
de publication de l'instantane.

| Fonction | Fait | Ne fait pas |
|---|---|---|
| `record_result(state, role, status, clock)` | transition d'une mesure, succes **et** echec | ne touche pas `chain` ; ne recoit aucune valeur |
| `complete_cycle(state, results)` | derive `chain_status`, `chain_cause`, `cycle_completed` | ne lit aucune horloge ; ne modifie aucune mesure |

Un echec **ne perime pas** la derniere valeur connue : les estampilles restent
inchangees, seul `last_result` bouge (§7.3).

### Refus

`record_result` refuse un role inconnu, un statut qui n'est pas un
`TransportStatus`, une horloge murale naive, un monotone non fini, et un **recul
monotone detectable par rapport au dernier succes de cette mesure**. Le controle
est **local** : aucune coherence globale d'horloge entre mesures differentes
n'est supposee.

`complete_cycle` refuse un ensemble **vide**, un role inconnu, un statut
invalide, et une **incoherence** entre le statut annonce et le `last_result`
courant — ce dernier controle transforme la redondance apparente en verification
que `record_result` a bien ete appele.

Le refus du cycle vide est delibere : §8.2 definit un cycle comme la tentative
de lecture « des mesures **dues a cet instant** ». Un ensemble vide satisferait
vacuement « termine » et basculerait `chain` en `unavailable` — regression
manifeste. Le refus oblige l'appelant a ne pas cloturer quand rien n'est du.

### Limite assumee — les doublons ne sont pas detectables

`complete_cycle` recoit un `Mapping`. Un dictionnaire litteral a **deja ecrase**
toute clef repetee avant l'appel : la fonction ne peut pas savoir qu'un role a
ete tente deux fois dans le cycle. Cette garantie n'est donc **pas revendiquee**.
Elle appartiendra au futur collecteur C7-C3, ou exigerait une API sequentielle
distincte. Aucun test ne pretend le contraire.

## Horloges murale et monotone

`Clock` (C2) suffit : aucune abstraction nouvelle n'est introduite.

| Usage | Horloge | Publie ? |
|---|---|---|
| `ts` de l'instantane, `last_success` | murale, UTC | **oui** |
| `age_s` | **monotone** | jamais la valeur brute |

Le meme succes estampille les deux. §6.4 interdit d'**exposer** une horloge
monotone, pas de s'en servir : mesurer l'age sur le compteur monotone rend
`age_s` insensible a un reglage de l'horloge systeme, sans qu'aucune valeur
monotone n'apparaisse dans le payload. Un test verifie qu'une valeur monotone
distinctive n'apparait nulle part dans le JSON.

`VirtualClock` fait avancer mural et monotone **ensemble** : un double local est
utilise dans les tests pour les dissocier.

## Age et fraicheur

```
age_s = floor(monotonic_now − last_success_monotonic)      None avant tout succes
fresh = (age_s is not None) and (age_s <= fresh_max_s)
```

- `age_s` est un **entier ≥ 0**, type impose par §6.5 ; `None` si et seulement si
  `last_success` est nul, comme l'exige l'invariant ;
- troncature a la seconde inferieure : nombre de secondes **entieres** ecoulees,
  lecture conventionnelle d'un age. Consequence assumee : a la frontiere de
  fraicheur, l'age rapporte peut etre optimiste de moins d'une seconde ;
- la borne est **inclusive** — §6.5 : « `age_s` est inferieur ou **egal** au
  seuil » ;
- la comparaison porte sur `age_s`, **l'entier publie**, et non sur le delta
  flottant : le consommateur doit pouvoir refaire le calcul a partir de ce qu'il
  lit ;
- un recul du monotone **leve**. Borner a zero publierait la fraicheur maximale
  pour une horloge cassee : le pire mensonge possible.

## Correspondance publique des statuts

Une table **explicite** traduit les six issues internes en `PublicResult`.
`status.value` ne peut pas servir :

```
TransportStatus.UNKNOWN_COMMAND.value == "unknown_command"
valeur publique contractuelle          == "unsupported_command"
```

§6.6 precise d'ailleurs que cette correspondance **MAY** evoluer, les valeurs
publiques restant stables — raison de plus pour qu'elle soit une table, et non
une propriete de l'enumeration interne. La table reste **privee** : aucune API
externe n'en a besoin.

`chain_cause` est stocke en `TransportStatus` et traduit au seul moment du rendu,
ce qui garde la frontiere interne/publique en un point unique.

## Instantane

Quatre clefs globales — `schema`, `ts`, `chain`, `measurements` — et **cinq** par
mesure : `has_value`, `fresh`, `last_success`, `age_s`, `last_result`. Aucune
autre. Des tests verrouillent l'ensemble de clefs **exact**, et l'absence de
`value`, `raw`, `detail`, `last_attempt`, `status` et `unit`.

`build_snapshot` rend un dictionnaire ; `snapshot_to_json` le serialise. Meme
separation que `ack_to_dict` / `ack_to_json` en C3, et meme idiome :
`separators=(",", ":")`, `sort_keys=True`, `ensure_ascii=False`,
**`allow_nan=False`**, encodage UTF-8 explicite.

`boilerack._legacy.primitives.json_dumps` n'est **pas** reutilise : il ne passe
pas `allow_nan=False` et emet donc `NaN` et `Infinity`, comportement classe
accident dans `provenance.md`.

L'ordre des clefs du JSON est **deterministe par tri**, non contractuel :
l'ordre montre par l'exemple §6.2 est illustratif et le contrat ne le declare
nulle part normatif. Le dictionnaire rendu par `build_snapshot`, lui, suit
l'ordre de `specs`.

## Frontieres

Non modifies : `transport/`, `adapters/`, `core/`, `testing/`, `_legacy/`,
`pyproject.toml`, `.github/`, `read_surface/topics.py`,
`read_surface/payload.py`. Seul `read_surface/__init__.py` est modifie, pour
ajouter les exports. Aucune dependance ajoutee.

Les trois modules n'importent ni `paho`, ni `socket`, ni `subprocess`, ni
`threading`, ni `asyncio`, ni `time`, et n'appellent jamais `datetime.now()`,
`utcnow()`, `time.monotonic()` ni `time.time()`. Des tests structurels le figent
par analyse du code source.

## Reports vers C7-C3

| Element | Raison du report |
|---|---|
| Testament MQTT et presence `bridge/online` (§5) | exige d'etendre la frontiere `MqttClient`, qui ne porte aujourd'hui aucun testament |
| Publieur, ordre de publication (§4.4, §4.6) | seul lot qui touchera a MQTT |
| Battement (§9) | `SHOULD`, compatibilite historique |
| Cadences et republication de l'instantane (§7.4) | releve de l'ordonnancement |
| Ordonnancement sequentiel, echeances, regle sans rattrapage | non contractuel ; decision d'implementation |
| Garantie « un role au plus une fois par cycle » | appartient au collecteur |

## Tests

**204 cas**, issus de **126 fonctions** — mesures 67, etat 67, instantane 70.
Tous deterministes, hors ligne, sans marqueur pytest. Aucun processus, aucun
socket, aucun broker, aucun `vclient`, aucune attente reelle.
