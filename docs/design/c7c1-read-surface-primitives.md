# C7-C1 — Primitives de la surface de lecture

## Objet

Premier lot d'implémentation de la surface MQTT de lecture. Il livre **deux
primitives pures** : la construction des topics et la sérialisation du payload
scalaire.

Ce sont les seules parties du contrat entièrement spécifiées et sans aucune
dépendance. Le lot ne modifie **aucun fichier existant**, n'ajoute **aucune
dépendance**, ne publie rien et **ne peut rien publier**.

## Sections contractuelles honorées

| Section de `c7-mqtt-read-contract.md` | Traitement |
|---|---|
| §3.2 — construction `<prefixe>/<suffixe>` | `build_topic` |
| §3.3 — normalisation du préfixe, 9 lignes | `normalize_prefix` |
| §3.4 — suffixe invariant selon le préfixe | verrouillé par test |
| §4.5 — représentation du payload scalaire | `format_scalar` |
| §11 — surface exacte des onze topics | `V1_SUFFIXES` |

Aucune autre section n'est touchée. Rien n'est transposé qui ne soit écrit dans
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

Une seule exception est définie. `InvalidPrefix` et `InvalidSuffix` distincts
n'auraient aujourd'hui aucun consommateur : le message porte déjà
l'information. Les messages sont déterministes pour les tests, mais **ne sont
pas une API contractuelle**.

## Suffixe valide n'est pas suffixe de la v1

Deux notions distinctes, et c'est délibéré :

| Notion | Portée | Garde |
|---|---|---|
| **Syntaxiquement valide** | toute chaîne que `build_topic` accepte d'assembler | `_validate_suffix` |
| **Appartenant à la surface v1** | l'un des **onze** de `V1_SUFFIXES` | l'énumération et ses tests |

`build_topic` n'est volontairement pas restreint aux onze. Le respect de la
surface — §11 : « Tout autre topic **MUST NOT** être publié » — est une
propriété du futur publieur et de ses tests de conformité, pas d'un assembleur
de chaînes. Aucun mécanisme d'enregistrement, d'extension ou de greffon n'est
introduit : la surface v1 est **close**.

Ne figurent pas dans l'énumération, et c'est voulu : `telemetry/burner/*`
(reportés, §4.3), `bridge/version` (reporté, §13), la commande et les
acquittements (surface transactionnelle, §14), `error/last` et `guard/*` (hors
périmètre, §13), un topic de capacités (hors v1, §10).

`bridge/heartbeat` **appartient** à la surface v1 tout en restant **`SHOULD`**
(§9). Cette nuance est documentaire : elle n'a pas de consommateur dans ce lot
et n'est donc encodée dans aucune structure.

## Normalisation du préfixe

Quatre normalisations, et aucune autre — §3.3 : « Aucune correction silencieuse
autre que les normalisations du tableau. »

- barre initiale retirée · barre terminale retirée · barres consécutives
  réduites · plusieurs niveaux acceptés tels quels.

Quatre refus : chaîne vide · joker `+` ou `#` · caractère de contrôle ou `NUL`
· préfixe commençant par `$`.

Trois lectures ont été faites, toutes signalées plutôt que résolues en silence :

1. **Un préfixe qui ne contient que des barres** (`/`, `//`) se normalise en
   chaîne vide. Il est refusé au même titre que la chaîne vide : le préfixe
   *effectif* serait vide, donc sans espace de noms, ce que §3.3 refuse par son
   motif même — « éviter les collisions sur un broker partagé ».
2. **Le contrôle du `$` porte sur le préfixe normalisé**, si bien que `/$SYS`
   est refusé comme `$SYS` : le topic produit commencerait par `$`. En
   revanche `maison/$x` est **accepté** — le contrat n'interdit `$` qu'en
   **tête** de préfixe, et l'espace réservé du broker n'est alors pas atteint.
3. **`$` n'est pas refusé dans un suffixe.** §3.3 ne l'interdit qu'en tête de
   préfixe, et un suffixe n'est jamais en tête d'un topic. Aucun des onze
   suffixes n'en contient.

Le refus des jokers et des caractères de contrôle **dans un suffixe** n'est pas
écrit tel quel dans le contrat : c'est une conséquence mécanique de MQTT — un
topic de publication ne peut pas porter de joker — et non une interdiction
produit nouvelle.

Enfin, ce que le contrat ne dit pas n'est pas interdit : **espaces**, y compris
de bordure, et **Unicode imprimable** sont acceptés. C'est une limite assumée,
pas un oubli ; inventer une interdiction serait un écart doctrinal.

Une entrée non textuelle lève `InvalidMqttTopic`, par cohérence avec
`InvalidCommandName` (C6), qui traite de même une entrée non textuelle.

## Sérialisation

Stratégie : **`Decimal(repr(value))` puis formatage positionnel `f`**.

- `repr` donne la représentation la plus **courte** qui reconstruit exactement
  le flottant : aucune décimale parasite. `Decimal(value)` exposerait au
  contraire l'expansion binaire complète — `0.1` deviendrait 55 chiffres ;
- le format `f` de `Decimal` est **positionnel** et **insensible à la locale**
  (seul le format `n` est localisé). Il n'émet jamais de notation
  exponentielle, ce que `repr` seul ne garantit pas : `repr(1e-05)` vaut
  `'1e-05'`.

Le zéro négatif est ramené au zéro positif **avant** formatage : §4.5 exige
qu'une valeur négative nulle soit sérialisée sans signe négatif. La règle porte
sur le **seul signe** — `-0.0` rend donc `0.0`, pas `0`, la précision restant
non normative.

`ValueError` est levée sur une valeur non finie, non numérique, booléenne, ou
sur un entier trop grand pour un flottant. Ce chemin n'est pas atteignable
depuis un `ReadResult` en statut `OK`, dont l'invariant durci garantit une
valeur présente et finie : c'est une garde contre une erreur de programmation,
jamais une issue de transport.

### Pas de forme déclarée

Aucun `ValueForm` n'est introduit, et c'est une décision. §4.5 déclare les deux
formes conformes — « `28` et `28.0` sont conformes » — et §11 déclare le payload
`decimal` pour **les huit** mesures, y compris les quatre que §4.2 range dans le
type `entier`. Ces deux sections ne sont cohérentes qu'à une lecture : la
colonne `Type` de §4.2 décrit le **domaine de la mesure**, la colonne `Payload`
de §11 décrit la **forme sur le fil**. Un champ de forme pilotant la
sérialisation contredirait §11.

La primitive ne connaît donc pas la mesure qu'elle sérialise : elle n'arrondit
pas, ne tronque pas, et ne vérifie pas qu'une mesure historiquement entière
reçoit une valeur entière. Ce contrôle relèverait d'une couche de conformité
qui n'existe pas et n'a pas de consommateur.

### Bornes de représentation

Le contrat ne fixe aucune longueur maximale de payload, et `ReadResult` accepte
tout flottant fini. La longueur produite a donc été **mesurée**, pas supposée.

| Valeur | Longueur |
|---|---:|
| `0.0`, `-0.0` | 3 |
| `1e-05` | 7 |
| `1e30` | 31 |
| `sys.float_info.max` | **309** (forme entière, aucun point) |
| `5e-324` (plus petit subnormal) | 326 |
| `-5e-324` | **327** |

Borne : **327 caractères**, atteinte par le subnormal négatif — 1 signe + `0.` +
307 zéros + 17 chiffres significatifs, `repr` n'excédant jamais 17 chiffres
significatifs. Vérifiée par balayage systématique de 6 328 valeurs couvrant les
exposants −330 à +308, signes compris : aucune sortie exponentielle, aucune
longueur supérieure à 327.

Rien n'est tronqué, arrondi, limité artificiellement, ni rendu dépendant de la
locale. **Aucune limite non prévue par le contrat n'est introduite.**

## Frontières

Les deux modules sont **purs**. Ils n'importent ni `paho`, ni `socket`, ni
`subprocess`, ni `threading`, ni `asyncio`, ni `time`, ni `datetime`, ni
`locale`, et **aucune autre partie de `boilerack`**. Aucune lecture de fichier,
de variable d'environnement, de réseau ni d'horloge. Des tests structurels
figent ces deux propriétés par analyse du code source.

Ce lot ne contient : aucun client MQTT, aucun testament, aucun état, aucun
instantané, aucune fraîcheur, aucun publieur, aucun ordonnancement, aucune
configuration, aucune déclaration de mesure, aucun chemin d'écriture, aucun
contact avec une installation réelle.

Non modifiés : `transport/`, `adapters/`, `core/`, `testing/`, `_legacy/`,
`pyproject.toml`, `.github/`.

## Reports

| Vers | Contenu |
|---|---|
| **C7-C2** | déclaration des mesures (`role`, `read`, `suffix`, `period_s`, `fresh_max_s`), état par mesure, politique de fraîcheur (§7), instantané `bridge/telemetry_status` (§6), état de chaîne (§8) — dont le traitement d'un ensemble du **vide** |
| **C7-C3** | testament MQTT et présence (§5), publieur et ordre de publication (§4.4, §4.6), battement (§9), cadences (§7.4), ordonnancement séquentiel — seul lot qui modifiera des fichiers existants |

## Tests

**326 cas**, issus de **66 fonctions** — l'écart vient du paramétrage, le plus
large étant l'invariance du suffixe vérifiée sur 4 préfixes x 11 suffixes.

Tous déterministes, hors ligne, sans marqueur pytest. Aucun processus, aucun
socket, aucun broker, aucune attente réelle.
