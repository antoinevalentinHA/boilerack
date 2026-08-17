# C7-C3A — Testament MQTT, présence du bridge et instantané de démarrage

## Objet

Premier sous-lot de C7-C3. Il honore §5 du contrat
`c7-mqtt-read-contract.md` — testament, `online` à la connexion, `offline`
avant déconnexion propre — ainsi que l'état de démarrage exigé par §7.3
(première ligne) et §8.2 (état initial de la chaîne).

Il ne lit aucune mesure et ne publie aucune valeur scalaire.

## Sections contractuelles honorées

| Section | Traitement |
|---|---|
| §3.1, §3.3 | `ReadSurfaceConfig` — préfixe normalisé **à la construction** |
| §5 | testament, `online`, `offline` avant déconnexion |
| §7.3 ligne 1 | instantané publié au démarrage, avant toute lecture |
| §8.2 état initial | `chain = { unavailable, null }` |
| §11 | exactement deux topics publiés, aucun autre |

## Le testament est un champ du CONNECT

En MQTT, le testament n'est pas un réglage séparé : c'est un **champ du paquet
CONNECT**. La frontière le modélise donc ainsi :

```python
def connect(self, will: MqttWill | None = None) -> None: ...
```

Trois options ont été écartées :

- **`set_will()` puis `connect()`** — invente une étape de cycle de vie que le
  protocole ne connaît pas, et laisse un piège d'ordre : Paho documente que
  `will_set()` « must be called before connect() to have any effect ». Un
  testament posé après la connexion serait **silencieusement** sans effet ;
- **testament dans `MqttConfig`** — le topic dérive du préfixe de la surface de
  **lecture**, pas de la configuration du broker. L'y loger créerait une seconde
  autorité de préfixe et rouvrirait la dette §14 ;
- **client Paho déjà configuré** — le publieur ne pourrait plus garantir le
  testament, et le construire ferait de lui une composition root.

`will` reste **optionnel** pour ne pas casser les consommateurs transactionnels
existants, qui n'en posent aucun. Cette optionalité ne vaut pas permission : le
publieur de lecture en fournit **toujours** un.

`MqttWill` fait partie de l'**API publique** de `boilerack.transport`, au même
titre que `Message`, `Publication` ou `Subscription` :

```python
from boilerack.transport import MqttWill        # reexport public
from boilerack.transport.mqtt import MqttWill   # import direct, equivalent
```

> **Limite de `runtime_checkable`.** `isinstance` ne vérifie QUE la présence des
> méthodes, jamais leurs signatures : une implémentation dont `connect` ignorerait
> le testament satisferait encore `isinstance(..., MqttClient)`. La conformité
> réelle est donc établie par un test de **comportement**, et un test dédié
> démontre précisément cette insuffisance.

## `will_clear()` quand le testament est absent

`connect(will=None)` signifie « aucun testament pour cette connexion », et non
« conserver le précédent ». L'adaptateur appelle donc `will_clear()` : sans
cela, un testament posé lors d'une connexion antérieure survivrait
**silencieusement** à une nouvelle connexion censée ne pas en porter — Paho
conserve le testament sur l'objet client.

Corollaire utile : le testament étant empaqueté dans **chaque** CONNECT, une
reconnexion native de Paho le conserve. Aucune action n'est requise, et aucune
politique de reconnexion n'est ajoutée.

## Testament et `offline` à l'arrêt : deux mécanismes disjoints

Paho documente que le testament **n'est pas émis** lorsque le client se
déconnecte proprement. L'annonce explicite exigée par §5 — « `offline` avant
deconnexion » — n'est donc **pas redondante** :

| Événement | Mécanisme |
|---|---|
| Disparition inattendue | le **broker** publie le testament |
| Arrêt propre | le **producteur** publie `offline`, puis se déconnecte |

Aucun des deux ne couvre le cas de l'autre.

## Propriété du cycle de connexion

Le client MQTT est **injecté**, jamais construit : `ReadSurfacePublisher` n'est
pas une composition root, ne construit aucun adaptateur et n'a ni boucle, ni
thread, ni sommeil — un test le vérifie sur le source.

Il possède en revanche le cycle `connect()` / `disconnect()`, et c'est
nécessaire : le testament doit être posé **au moment** de la connexion et son
topic dérive du préfixe de la surface de lecture. Confier la connexion à
l'appelant rendrait la garantie **conventionnelle** au lieu de structurelle.

| Responsabilité | Détenteur |
|---|---|
| Construction du client, de l'horloge | appelant |
| Cycle `connect` / `disconnect` | **publieur** |
| Testament | **publieur**, dérivé du préfixe |
| État de lecture C7-C2 | **publieur**, initialisé à la **construction** |
| Lecture, cadences, battement | **personne** — C7-C3B |

L'état est initialisé dans `__init__`, non dans `start()` : sa durée de vie est
celle du composant, pas celle d'une connexion. Un `start()` ultérieur republie
l'état courant sans le réinitialiser.

## Séquences

### `start()`

1. `connect(will=MqttWill(<prefix>/bridge/online, b"offline", qos=1, retain=True))` ;
2. `online` sur `<prefix>/bridge/online`, QoS 1, retenu ;
3. instantané initial sur `<prefix>/bridge/telemetry_status`, QoS 1, retenu.

Ensemble **exact** des topics publiés au démarrage : ces deux-là, et aucun
autre.

### `stop()`

1. `offline` sur `<prefix>/bridge/online`, QoS 1, retenu ;
2. `disconnect()`.

## Erreurs de publication

**Au démarrage**, une publication qui lève remonte **telle quelle** : aucune
traduction, aucune taxonomie nouvelle, aucune compensation non contractée.

Le drapeau de cycle de vie est posé **dès que la connexion est établie**, avant
les publications. Conséquence à connaître : si `online` ou l'instantané échoue,
`start()` ne rend pas la main et rien ne prétend qu'il a réussi, mais le client
**est** réellement connecté — le drapeau reflète donc la réalité, et `stop()`
reste appelable pour refermer proprement.

**À l'arrêt**, `disconnect()` est **toujours** tenté. Quatre issues :

| annonce `offline` | déconnexion | ce qui remonte |
|---|---|---|
| OK | OK | rien |
| KO | OK | l'erreur de publication, inchangée |
| OK | KO | l'erreur de déconnexion, inchangée |
| **KO** | **KO** | un **`ExceptionGroup`** portant les **deux**, annonce d'abord |

Le dernier cas justifie de ne pas s'en remettre à un `finally` seul : sa
sémantique ferait masquer l'erreur d'annonce par celle de déconnexion, et une
information réelle serait perdue. Les exceptions d'origine sont conservées
telles quelles — aucune conversion, aucune taxonomie métier nouvelle, aucune
tentative supplémentaire. Le drapeau de cycle de vie est remis à l'état arrêté
dans les quatre cas, si bien qu'un `start()` reste toujours possible.

**Préserver les deux erreurs ne dit rien de la livraison** : qu'aucune exception
ne remonte signifie seulement que les appels ont été acceptés, jamais que le
message `offline` a été reçu par le broker. Aucune garantie de livraison n'en
est déduite.

> Ce choix **diverge volontairement** du précédent `engine._publish_terminal`,
> qui absorbe toute erreur de publication. La situation diffère : le moteur
> protège un verdict déjà en cache, qu'une publication ratée ne doit ni perdre
> ni remonter au demandeur. Ici il n'y a aucun verdict à protéger, et taire
> l'échec laisserait croire que le départ a été annoncé.

## Aucune confirmation de livraison

Le `PublishHandle` est **délibérément ignoré**. §4.6 pose que les publications
ne sont pas transactionnelles, et l'adaptateur réel n'attend jamais de PUBACK
(C4 : « jamais de `wait_for_publish()` »). Prétendre confirmer une livraison
serait promettre une garantie que la frontière ne fournit pas. Un test vérifie
que `wait_for_publish`, `.confirmed` et `.failed` n'apparaissent pas dans le
module.

## Limitation de reconnexion, assumée

Aucune politique de reconnexion n'est implémentée, et le contrat n'en définit
aucune : le mot « reconnexion » **n'apparaît pas** dans C7-B, et §15.5 range la
politique de rétention et d'expiration de session du broker parmi les
**inconnues**.

> **Conséquence à connaître.** Après une déconnexion **inattendue**, le broker
> publie le testament et le retenu `bridge/online` passe à `offline`. Si Paho se
> reconnecte de lui-même, ce composant ne le voit pas — la frontière
> `MqttClient` n'expose aucun rappel de connexion établie — et le retenu restera
> `offline` alors que le bridge est vivant, **jusqu'au prochain `start()`**.

Combler ce trou exigerait un rappel de connexion sur la frontière **et** une
clause contractuelle sur la reprise. Les deux sont hors du périmètre de ce lot.

## Ce lot n'est pas encore un producteur conforme

Il ne lit aucune mesure, ne publie aucune valeur scalaire, ne porte aucune
cadence, aucun battement, aucun ordonnancement et aucune reconnexion. Un test
fige cette limite pour qu'elle ne puisse pas être prise pour un oubli, et il
devra changer de façon **visible** le jour où C7-C3B étendra le composant.

## Configuration

```python
@dataclass(frozen=True)
class ReadSurfaceConfig:
    prefix: str = "boiler"
```

Un seul champ. `snapshot_period_s` et `heartbeat_period_s` n'auraient **aucun
consommateur** dans ce lot, qui ne publie ni sur cadence ni de battement : ils
seront introduits en C7-C3B avec l'ordonnancement qui les utilise.

Le préfixe est normalisé à la construction et **seule** la forme normalisée est
conservée — §3.3 : « Le rejet **MUST** survenir a la construction de la
configuration, avant toute connexion ». Aucun topic complet n'est stocké : tout
topic se dérive du préfixe et d'un suffixe contractuel via `build_topic` (§3.2).

`boilerack.adapters.config.MqttConfig` n'est **ni modifié ni réutilisé** : y
loger le préfixe de lecture créerait une seconde autorité et rouvrirait la dette
§14.

## Frontières

Non modifiés : `read_surface/topics.py`, `payload.py`, `measurements.py`,
`state.py`, `snapshot.py`, `adapters/config.py`, `core/`, `_legacy/`,
`pyproject.toml`, `.github/`. Aucune dépendance ajoutée.

Le module `publisher` n'importe ni `paho`, ni `socket`, ni `subprocess`, ni
`threading`, ni `asyncio`, ni `ssl`, ni `time`, et n'appelle jamais
`datetime.now()`, `utcnow()`, `time.monotonic()` ni `time.time()` : l'horloge
est toujours injectée.

## Reports vers C7-C3B

| Élément | Report |
|---|---|
| Lecture des mesures dues (`VClientCliReader`) | C7-C3B |
| Publication des valeurs scalaires (§4.4, §4.5) | C7-C3B |
| Ordre par mesure et cycles (§4.6, §8.2) | C7-C3B |
| Cadences, échéances, règle sans rattrapage (§7.4) | C7-C3B |
| Battement (§9) | C7-C3B |
| `snapshot_period_s`, `heartbeat_period_s` | C7-C3B |
| Rappel de connexion et reprise après reconnexion | hors C7-C3, exige une clause contractuelle |
