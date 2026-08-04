# C7-C3A — Testament MQTT, presence du bridge et instantane de demarrage

## Objet

Premier sous-lot de C7-C3. Il honore §5 du contrat
`c7-mqtt-read-contract.md` — testament, `online` a la connexion, `offline`
avant deconnexion propre — ainsi que l'etat de demarrage exige par §7.3
(premiere ligne) et §8.2 (etat initial de la chaine).

Il ne lit aucune mesure et ne publie aucune valeur scalaire.

## Sections contractuelles honorees

| Section | Traitement |
|---|---|
| §3.1, §3.3 | `ReadSurfaceConfig` — prefixe normalise **a la construction** |
| §5 | testament, `online`, `offline` avant deconnexion |
| §7.3 ligne 1 | instantane publie au demarrage, avant toute lecture |
| §8.2 etat initial | `chain = { unavailable, null }` |
| §11 | exactement deux topics publies, aucun autre |

## Le testament est un champ du CONNECT

En MQTT, le testament n'est pas un reglage separe : c'est un **champ du paquet
CONNECT**. La frontiere le modelise donc ainsi :

```python
def connect(self, will: MqttWill | None = None) -> None: ...
```

Trois options ont ete ecartees :

- **`set_will()` puis `connect()`** — invente une etape de cycle de vie que le
  protocole ne connait pas, et laisse un piege d'ordre : Paho documente que
  `will_set()` « must be called before connect() to have any effect ». Un
  testament pose apres la connexion serait **silencieusement** sans effet ;
- **testament dans `MqttConfig`** — le topic derive du prefixe de la surface de
  **lecture**, pas de la configuration du broker. L'y loger creerait une seconde
  autorite de prefixe et rouvrirait la dette §14 ;
- **client Paho deja configure** — le publieur ne pourrait plus garantir le
  testament, et le construire ferait de lui une composition root.

`will` reste **optionnel** pour ne pas casser les consommateurs transactionnels
existants, qui n'en posent aucun. Cette optionalite ne vaut pas permission : le
publieur de lecture en fournit **toujours** un.

`MqttWill` fait partie de l'**API publique** de `boilerack.transport`, au meme
titre que `Message`, `Publication` ou `Subscription` :

```python
from boilerack.transport import MqttWill        # reexport public
from boilerack.transport.mqtt import MqttWill   # import direct, equivalent
```

> **Limite de `runtime_checkable`.** `isinstance` ne verifie QUE la presence des
> methodes, jamais leurs signatures : une implementation dont `connect` ignorerait
> le testament satisferait encore `isinstance(..., MqttClient)`. La conformite
> reelle est donc etablie par un test de **comportement**, et un test dedie
> demontre precisement cette insuffisance.

## `will_clear()` quand le testament est absent

`connect(will=None)` signifie « aucun testament pour cette connexion », et non
« conserver le precedent ». L'adaptateur appelle donc `will_clear()` : sans
cela, un testament pose lors d'une connexion anterieure survivrait
**silencieusement** a une nouvelle connexion censee ne pas en porter — Paho
conserve le testament sur l'objet client.

Corollaire utile : le testament etant empaquete dans **chaque** CONNECT, une
reconnexion native de Paho le conserve. Aucune action n'est requise, et aucune
politique de reconnexion n'est ajoutee.

## Testament et `offline` a l'arret : deux mecanismes disjoints

Paho documente que le testament **n'est pas emis** lorsque le client se
deconnecte proprement. L'annonce explicite exigee par §5 — « `offline` avant
deconnexion » — n'est donc **pas redondante** :

| Evenement | Mecanisme |
|---|---|
| Disparition inattendue | le **broker** publie le testament |
| Arret propre | le **producteur** publie `offline`, puis se deconnecte |

Aucun des deux ne couvre le cas de l'autre.

## Propriete du cycle de connexion

Le client MQTT est **injecte**, jamais construit : `ReadSurfacePublisher` n'est
pas une composition root, ne construit aucun adaptateur et n'a ni boucle, ni
thread, ni sommeil — un test le verifie sur le source.

Il possede en revanche le cycle `connect()` / `disconnect()`, et c'est
necessaire : le testament doit etre pose **au moment** de la connexion et son
topic derive du prefixe de la surface de lecture. Confier la connexion a
l'appelant rendrait la garantie **conventionnelle** au lieu de structurelle.

| Responsabilite | Detenteur |
|---|---|
| Construction du client, de l'horloge | appelant |
| Cycle `connect` / `disconnect` | **publieur** |
| Testament | **publieur**, derive du prefixe |
| Etat de lecture C7-C2 | **publieur**, initialise a la **construction** |
| Lecture, cadences, battement | **personne** — C7-C3B |

L'etat est initialise dans `__init__`, non dans `start()` : sa duree de vie est
celle du composant, pas celle d'une connexion. Un `start()` ulterieur republie
l'etat courant sans le reinitialiser.

## Sequences

### `start()`

1. `connect(will=MqttWill(<prefix>/bridge/online, b"offline", qos=1, retain=True))` ;
2. `online` sur `<prefix>/bridge/online`, QoS 1, retenu ;
3. instantane initial sur `<prefix>/bridge/telemetry_status`, QoS 1, retenu.

Ensemble **exact** des topics publies au demarrage : ces deux-la, et aucun
autre.

### `stop()`

1. `offline` sur `<prefix>/bridge/online`, QoS 1, retenu ;
2. `disconnect()`.

## Erreurs de publication

**Au demarrage**, une publication qui leve remonte **telle quelle** : aucune
traduction, aucune taxonomie nouvelle, aucune compensation non contractee.

Le drapeau de cycle de vie est pose **des que la connexion est etablie**, avant
les publications. Consequence a connaitre : si `online` ou l'instantane echoue,
`start()` ne rend pas la main et rien ne pretend qu'il a reussi, mais le client
**est** reellement connecte — le drapeau reflete donc la realite, et `stop()`
reste appelable pour refermer proprement.

**A l'arret**, `disconnect()` est **toujours** tente. Quatre issues :

| annonce `offline` | deconnexion | ce qui remonte |
|---|---|---|
| OK | OK | rien |
| KO | OK | l'erreur de publication, inchangee |
| OK | KO | l'erreur de deconnexion, inchangee |
| **KO** | **KO** | un **`ExceptionGroup`** portant les **deux**, annonce d'abord |

Le dernier cas justifie de ne pas s'en remettre a un `finally` seul : sa
semantique ferait masquer l'erreur d'annonce par celle de deconnexion, et une
information reelle serait perdue. Les exceptions d'origine sont conservees
telles quelles — aucune conversion, aucune taxonomie metier nouvelle, aucune
tentative supplementaire. Le drapeau de cycle de vie est remis a l'etat arrete
dans les quatre cas, si bien qu'un `start()` reste toujours possible.

**Preserver les deux erreurs ne dit rien de la livraison** : qu'aucune exception
ne remonte signifie seulement que les appels ont ete acceptes, jamais que le
message `offline` a ete recu par le broker. Aucune garantie de livraison n'en
est deduite.

> Ce choix **diverge volontairement** du precedent `engine._publish_terminal`,
> qui absorbe toute erreur de publication. La situation differe : le moteur
> protege un verdict deja en cache, qu'une publication ratee ne doit ni perdre
> ni remonter au demandeur. Ici il n'y a aucun verdict a proteger, et taire
> l'echec laisserait croire que le depart a ete annonce.

## Aucune confirmation de livraison

Le `PublishHandle` est **deliberement ignore**. §4.6 pose que les publications
ne sont pas transactionnelles, et l'adaptateur reel n'attend jamais de PUBACK
(C4 : « jamais de `wait_for_publish()` »). Pretendre confirmer une livraison
serait promettre une garantie que la frontiere ne fournit pas. Un test verifie
que `wait_for_publish`, `.confirmed` et `.failed` n'apparaissent pas dans le
module.

## Limitation de reconnexion, assumee

Aucune politique de reconnexion n'est implementee, et le contrat n'en definit
aucune : le mot « reconnexion » **n'apparait pas** dans C7-B, et §15.5 range la
politique de retention et d'expiration de session du broker parmi les
**inconnues**.

> **Consequence a connaitre.** Apres une deconnexion **inattendue**, le broker
> publie le testament et le retenu `bridge/online` passe a `offline`. Si Paho se
> reconnecte de lui-meme, ce composant ne le voit pas — la frontiere
> `MqttClient` n'expose aucun rappel de connexion etablie — et le retenu restera
> `offline` alors que le bridge est vivant, **jusqu'au prochain `start()`**.

Combler ce trou exigerait un rappel de connexion sur la frontiere **et** une
clause contractuelle sur la reprise. Les deux sont hors du perimetre de ce lot.

## Ce lot n'est pas encore un producteur conforme

Il ne lit aucune mesure, ne publie aucune valeur scalaire, ne porte aucune
cadence, aucun battement, aucun ordonnancement et aucune reconnexion. Un test
fige cette limite pour qu'elle ne puisse pas etre prise pour un oubli, et il
devra changer de facon **visible** le jour ou C7-C3B etendra le composant.

## Configuration

```python
@dataclass(frozen=True)
class ReadSurfaceConfig:
    prefix: str = "boiler"
```

Un seul champ. `snapshot_period_s` et `heartbeat_period_s` n'auraient **aucun
consommateur** dans ce lot, qui ne publie ni sur cadence ni de battement : ils
seront introduits en C7-C3B avec l'ordonnancement qui les utilise.

Le prefixe est normalise a la construction et **seule** la forme normalisee est
conservee — §3.3 : « Le rejet **MUST** survenir a la construction de la
configuration, avant toute connexion ». Aucun topic complet n'est stocke : tout
topic se derive du prefixe et d'un suffixe contractuel via `build_topic` (§3.2).

`boilerack.adapters.config.MqttConfig` n'est **ni modifie ni reutilise** : y
loger le prefixe de lecture creerait une seconde autorite et rouvrirait la dette
§14.

## Frontieres

Non modifies : `read_surface/topics.py`, `payload.py`, `measurements.py`,
`state.py`, `snapshot.py`, `adapters/config.py`, `core/`, `_legacy/`,
`pyproject.toml`, `.github/`. Aucune dependance ajoutee.

Le module `publisher` n'importe ni `paho`, ni `socket`, ni `subprocess`, ni
`threading`, ni `asyncio`, ni `ssl`, ni `time`, et n'appelle jamais
`datetime.now()`, `utcnow()`, `time.monotonic()` ni `time.time()` : l'horloge
est toujours injectee.

## Reports vers C7-C3B

| Element | Report |
|---|---|
| Lecture des mesures dues (`VClientCliReader`) | C7-C3B |
| Publication des valeurs scalaires (§4.4, §4.5) | C7-C3B |
| Ordre par mesure et cycles (§4.6, §8.2) | C7-C3B |
| Cadences, echeances, regle sans rattrapage (§7.4) | C7-C3B |
| Battement (§9) | C7-C3B |
| `snapshot_period_s`, `heartbeat_period_s` | C7-C3B |
| Rappel de connexion et reprise apres reconnexion | hors C7-C3, exige une clause contractuelle |
