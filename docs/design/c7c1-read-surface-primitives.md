# C7-C1 — Primitives de la surface de lecture

## Objet

Premier lot d'implementation de la surface MQTT de lecture. Il livre **deux
primitives pures** : la construction des topics et la serialisation du payload
scalaire.

Ce sont les seules parties du contrat entierement specifiees et sans aucune
dependance. Le lot ne modifie **aucun fichier existant**, n'ajoute **aucune
dependance**, ne publie rien et **ne peut rien publier**.

## Sections contractuelles honorees

| Section de `c7-mqtt-read-contract.md` | Traitement |
|---|---|
| §3.2 — construction `<prefixe>/<suffixe>` | `build_topic` |
| §3.3 — normalisation du prefixe, 9 lignes | `normalize_prefix` |
| §3.4 — suffixe invariant selon le prefixe | verrouille par test |
| §4.5 — representation du payload scalaire | `format_scalar` |
| §11 — surface exacte des onze topics | `V1_SUFFIXES` |

Aucune autre section n'est touchee. Rien n'est transpose qui ne soit ecrit dans
le contrat.

## API publique

```python
from boilerack.read_surface import (
    InvalidMqttTopic,      # unique exception, derivee de ValueError
    normalize_prefix,      # (str) -> str
    build_topic,           # (prefix: str, suffix: str) -> str
    TELEMETRY_SUFFIXES,    # tuple de 8
    BRIDGE_SUFFIXES,       # tuple de 3
    V1_SUFFIXES,           # tuple de 11, ordre stable
    format_scalar,         # (float) -> bytes
)
```

Une seule exception est definie. `InvalidPrefix` et `InvalidSuffix` distincts
n'auraient aujourd'hui aucun consommateur : le message porte deja
l'information. Les messages sont deterministes pour les tests, mais **ne sont
pas une API contractuelle**.

## Suffixe valide n'est pas suffixe de la v1

Deux notions distinctes, et c'est deliberé :

| Notion | Portee | Garde |
|---|---|---|
| **Syntaxiquement valide** | toute chaine que `build_topic` accepte d'assembler | `_validate_suffix` |
| **Appartenant a la surface v1** | l'un des **onze** de `V1_SUFFIXES` | l'enumeration et ses tests |

`build_topic` n'est volontairement pas restreint aux onze. Le respect de la
surface — §11 : « Tout autre topic **MUST NOT** etre publie » — est une
propriete du futur publieur et de ses tests de conformite, pas d'un assembleur
de chaines. Aucun mecanisme d'enregistrement, d'extension ou de greffon n'est
introduit : la surface v1 est **close**.

Ne figurent pas dans l'enumeration, et c'est voulu : `telemetry/burner/*`
(reportes, §4.3), `bridge/version` (reporte, §13), la commande et les
acquittements (surface transactionnelle, §14), `error/last` et `guard/*` (hors
perimetre, §13), un topic de capacites (hors v1, §10).

`bridge/heartbeat` **appartient** a la surface v1 tout en restant **`SHOULD`**
(§9). Cette nuance est documentaire : elle n'a pas de consommateur dans ce lot
et n'est donc encodee dans aucune structure.

## Normalisation du prefixe

Quatre normalisations, et aucune autre — §3.3 : « Aucune correction silencieuse
autre que les normalisations du tableau. »

- barre initiale retiree · barre terminale retiree · barres consecutives
  reduites · plusieurs niveaux acceptes tels quels.

Quatre refus : chaine vide · joker `+` ou `#` · caractere de controle ou `NUL`
· prefixe commencant par `$`.

Trois lectures ont ete faites, toutes signalees plutot que resolues en silence :

1. **Un prefixe qui ne contient que des barres** (`/`, `//`) se normalise en
   chaine vide. Il est refuse au meme titre que la chaine vide : le prefixe
   *effectif* serait vide, donc sans espace de noms, ce que §3.3 refuse par son
   motif meme — « eviter les collisions sur un broker partage ».
2. **Le controle du `$` porte sur le prefixe normalise**, si bien que `/$SYS`
   est refuse comme `$SYS` : le topic produit commencerait par `$`. En
   revanche `maison/$x` est **accepte** — le contrat n'interdit `$` qu'en
   **tete** de prefixe, et l'espace reserve du broker n'est alors pas atteint.
3. **`$` n'est pas refuse dans un suffixe.** §3.3 ne l'interdit qu'en tete de
   prefixe, et un suffixe n'est jamais en tete d'un topic. Aucun des onze
   suffixes n'en contient.

Le refus des jokers et des caracteres de controle **dans un suffixe** n'est pas
ecrit tel quel dans le contrat : c'est une consequence mecanique de MQTT — un
topic de publication ne peut pas porter de joker — et non une interdiction
produit nouvelle.

Enfin, ce que le contrat ne dit pas n'est pas interdit : **espaces**, y compris
de bordure, et **Unicode imprimable** sont acceptes. C'est une limite assumee,
pas un oubli ; inventer une interdiction serait un ecart doctrinal.

Une entree non textuelle leve `InvalidMqttTopic`, par coherence avec
`InvalidCommandName` (C6), qui traite de meme une entree non textuelle.

## Serialisation

Strategie : **`Decimal(repr(value))` puis formatage positionnel `f`**.

- `repr` donne la representation la plus **courte** qui reconstruit exactement
  le flottant : aucune decimale parasite. `Decimal(value)` exposerait au
  contraire l'expansion binaire complete — `0.1` deviendrait 55 chiffres ;
- le format `f` de `Decimal` est **positionnel** et **insensible a la locale**
  (seul le format `n` est localise). Il n'emet jamais de notation
  exponentielle, ce que `repr` seul ne garantit pas : `repr(1e-05)` vaut
  `'1e-05'`.

Le zero negatif est ramene au zero positif **avant** formatage : §4.5 exige
qu'une valeur negative nulle soit serialisee sans signe negatif. La regle porte
sur le **seul signe** — `-0.0` rend donc `0.0`, pas `0`, la precision restant
non normative.

`ValueError` est levee sur une valeur non finie, non numerique, booleenne, ou
sur un entier trop grand pour un flottant. Ce chemin n'est pas atteignable
depuis un `ReadResult` en statut `OK`, dont l'invariant durci garantit une
valeur presente et finie : c'est une garde contre une erreur de programmation,
jamais une issue de transport.

### Pas de forme declaree

Aucun `ValueForm` n'est introduit, et c'est une decision. §4.5 declare les deux
formes conformes — « `28` et `28.0` sont conformes » — et §11 declare le payload
`decimal` pour **les huit** mesures, y compris les quatre que §4.2 range dans le
type `entier`. Ces deux sections ne sont coherentes qu'a une lecture : la
colonne `Type` de §4.2 decrit le **domaine de la mesure**, la colonne `Payload`
de §11 decrit la **forme sur le fil**. Un champ de forme pilotant la
serialisation contredirait §11.

La primitive ne connait donc pas la mesure qu'elle serialise : elle n'arrondit
pas, ne tronque pas, et ne verifie pas qu'une mesure historiquement entiere
recoit une valeur entiere. Ce controle releverait d'une couche de conformite
qui n'existe pas et n'a pas de consommateur.

### Bornes de representation

Le contrat ne fixe aucune longueur maximale de payload, et `ReadResult` accepte
tout flottant fini. La longueur produite a donc ete **mesuree**, pas supposee.

| Valeur | Longueur |
|---|---:|
| `0.0`, `-0.0` | 3 |
| `1e-05` | 7 |
| `1e30` | 31 |
| `sys.float_info.max` | **309** (forme entiere, aucun point) |
| `5e-324` (plus petit subnormal) | 326 |
| `-5e-324` | **327** |

Borne : **327 caracteres**, atteinte par le subnormal negatif — 1 signe + `0.` +
307 zeros + 17 chiffres significatifs, `repr` n'excedant jamais 17 chiffres
significatifs. Verifiee par balayage systematique de 6 328 valeurs couvrant les
exposants −330 a +308, signes compris : aucune sortie exponentielle, aucune
longueur superieure a 327.

Rien n'est tronque, arrondi, limite artificiellement, ni rendu dependant de la
locale. **Aucune limite non prevue par le contrat n'est introduite.**

## Frontieres

Les deux modules sont **purs**. Ils n'importent ni `paho`, ni `socket`, ni
`subprocess`, ni `threading`, ni `asyncio`, ni `time`, ni `datetime`, ni
`locale`, et **aucune autre partie de `boilerack`**. Aucune lecture de fichier,
de variable d'environnement, de reseau ni d'horloge. Des tests structurels
figent ces deux proprietes par analyse du code source.

Ce lot ne contient : aucun client MQTT, aucun testament, aucun etat, aucun
instantane, aucune fraicheur, aucun publieur, aucun ordonnancement, aucune
configuration, aucune declaration de mesure, aucun chemin d'ecriture, aucun
contact avec une installation reelle.

Non modifies : `transport/`, `adapters/`, `core/`, `testing/`, `_legacy/`,
`pyproject.toml`, `.github/`.

## Reports

| Vers | Contenu |
|---|---|
| **C7-C2** | declaration des mesures (`role`, `read`, `suffix`, `period_s`, `fresh_max_s`), etat par mesure, politique de fraicheur (§7), instantane `bridge/telemetry_status` (§6), etat de chaine (§8) — dont le traitement d'un ensemble du **vide** |
| **C7-C3** | testament MQTT et presence (§5), publieur et ordre de publication (§4.4, §4.6), battement (§9), cadences (§7.4), ordonnancement sequentiel — seul lot qui modifiera des fichiers existants |

## Tests

**326 cas**, issus de **66 fonctions** — l'ecart vient du parametrage, le plus
large etant l'invariance du suffixe verifiee sur 4 prefixes x 11 suffixes.

Tous deterministes, hors ligne, sans marqueur pytest. Aucun processus, aucun
socket, aucun broker, aucune attente reelle.
