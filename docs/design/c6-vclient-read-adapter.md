# C6 — Lecteur `vclient` en lecture seule

## Objet

`VClientCliReader` (`src/boilerack/adapters/vclient_cli.py`) exécute une lecture
`vclient -J` et traduit son issue en `ReadResult`. C'est le premier composant
concret à parler le dialecte `vclient` — volet **lecture uniquement**.

Il lève le blocage nommé par C4 : *« l'adaptateur `vclient` concret est
délibérément absent tant que son contrat réel n'est pas caractérisé »*. C5 a
caractérisé la lecture ; C6 l'implémente. L'écriture reste bloquée.

## Dépendances

| Provenance | Élément |
|---|---|
| **C4** | `ProcessRunner` (frontière de sous-processus injectable), `VclientConfig` (executable, hôte, port, budgets) |
| **C5** | signatures observées et 9 fixtures versionnées — voir `c5-vclient-contract.md` |
| **C3** | `TransportStatus`, `ReadResult` — **inchangés** |

Aucune dépendance nouvelle. Aucun système de configuration nouveau : `VclientConfig`
existait déjà et suffit.

## Invocation

```
<executable> [-h <host>] [-p <port>] -J -c <command>
```

Liste d'arguments, jamais de shell, jamais de concaténation, jamais de fichier
temporaire, une seule commande par invocation. `-J` est la seule option de
sortie : C5 a établi que `error` y est le discriminant et que `raw` porte la
valeur et son unité sans analyse lexicale.

`-h` et `-p` sont omis si la configuration ne les fixe pas.

### Validation du nom de commande

Le projet ne définit **aucune grammaire** de nom de commande : `CommandSpec`
exige seulement une chaîne non vide, et les noms sont explicitement « opaques
pour le transport ». C6 ne l'invente pas et se limite à ce qui empêche un nom
de changer le sens de la ligne d'arguments :

| Refus | Motif |
|---|---|
| chaîne vide ou non textuelle | rien à exécuter |
| espaces de bordure | ambiguïté d'argument |
| caractère de contrôle | injection dans la sortie |
| virgule | `-c` accepte une **liste** : une virgule ferait exécuter plusieurs commandes |
| début par `-` | ambiguïté avec une option |

Aucune liste blanche de datapoints : elle appartient au profil, pas au transport.
Un nom refusé lève `InvalidCommandName` **avant toute invocation de processus**.

## Ordre de classification

Du plus certain au plus incertain. Ce qui n'est pas prouvé ne devient jamais `OK`.

| # | Condition | Statut |
|---|---|---|
| 1 | `launch_failed` | `TRANSPORT_ERROR` |
| 2 | `timed_out` | `TIMEOUT` |
| 3 | `returncode == 1` **et** `stdout == b""` **et** `stderr == b""` | `DAEMON_UNREACHABLE` |
| 4 | `stdout` non décodable en UTF-8 | `UNUSABLE_OUTPUT` |
| 5 | structure JSON non conforme | `UNUSABLE_OUTPUT` |
| 6 | `error == "ERR: command unknown"` | `UNKNOWN_COMMAND` |
| 7 | `error` non vide, autre valeur | `TRANSPORT_ERROR` |
| 8 | `error == ""` et `value` numérique finie | `OK` |

### Précisions

**Étape 1 — pas de `CLIENT_UNAVAILABLE`.** C6 **ne ratifie pas** la septième
valeur proposée en C5. Un échec de lancement est classé prudemment en
`TRANSPORT_ERROR`. La cause est conservée dans `detail` sous la forme du **nom
de la classe d'exception** déjà fourni par `ProcessResult.launch_error` — jamais
un chemin ni un message brut.

> Note d'implémentation : le cadrage suggérait `launch_error is not None`. Le
> champ est un `str` valant `""` par défaut, et `ProcessResult` porte un drapeau
> typé dédié, `launch_failed`. C'est lui qui est utilisé.

**Étape 2 — aucune exploitation d'une sortie partielle.** Un budget épuisé rend
`TIMEOUT` même si `stdout` contient un JSON complet.

**Étape 3 — aucune généralisation.** La signature du démon injoignable est
reconnue **exactement** telle qu'observée. Tout autre code retour non nul, ou
tout flux non vide, ne la déclenche pas.

**Étape 4 — décodage strict et séparé.** `stdout` et `stderr` ne sont **jamais**
fusionnés. Un `stdout` non décodable est une sortie inexploitable, jamais une
substitution silencieuse de caractères. `stderr` est décodé pour le seul
diagnostic ; s'il est lui-même indécodable, cela n'empêche pas le verdict.

**Étape 6 — un seul signal.** `UNKNOWN_COMMAND` n'est produit que sur la valeur
**exacte** observée. Ne sont jamais utilisés : le code retour seul, toute valeur
d'`error` non vide, un `raw` commençant par `ERR:`, une ligne de `stderr`, la
chaîne `server error`.

**Étape 8 — succès.** Exige un JSON valide, une commande correspondante, `error`
vide, et une `value` numérique **finie**. Les booléens sont refusés explicitement
(`isinstance(True, int)` vaut `True` en Python). `raw` est conservé tel quel,
sans reparsing de l'unité.

## Frontière `UNUSABLE_OUTPUT` / `TRANSPORT_ERROR`

La règle tient en une phrase :

> `UNUSABLE_OUTPUT` quand **le démon a répondu et que sa réponse est
> inexploitable** ; `TRANSPORT_ERROR` quand **l'échange lui-même a échoué, ou
> que le démon signale une erreur qui n'est pas caractérisée**.

| Cas | Statut | Pourquoi |
|---|---|---|
| décodage impossible | `UNUSABLE_OUTPUT` | une réponse existe, elle est illisible |
| JSON invalide, racine non liste, liste vide, plusieurs objets, élément non objet | `UNUSABLE_OUTPUT` | structure |
| champ manquant, `command` différente, types incompatibles | `UNUSABLE_OUTPUT` | structure |
| `value` non numérique, booléenne, `NaN`, `±Inf` | `UNUSABLE_OUTPUT` | contenu structurellement inexploitable |
| échec de lancement | `TRANSPORT_ERROR` | aucun échange |
| `error` non vide et non caractérisé | `TRANSPORT_ERROR` | le démon a répondu, mais la cause n'est pas prouvée |

Le critère est donc **la nature du défaut**, pas sa gravité : une réponse bien
formée portant une erreur inconnue reste un problème de transport ; une réponse
mal formée reste un problème de structure, même si elle est arrivée.

Toute combinaison non couverte avec certitude tombe dans l'un de ces deux
statuts, jamais dans `OK`.

## Le code retour ne conclut jamais seul

C5 a établi qu'il ne discrimine dans aucun des deux sens : `-V` et `--help`
rendent `1` pour un résultat normal, une commande inconnue rend `0`.

Ce lecteur ne l'utilise donc qu'à **un seul endroit** : la signature exacte du
démon injoignable, conjointement à deux flux vides. Un code retour non nul
accompagné d'un JSON valide reste exploité ; un code retour nul accompagné
d'une erreur structurée reste une erreur.

## Absence volontaire de `write()`

`VClientCliReader` n'a **pas** de méthode `write` et ne satisfait donc **pas**
le protocole `VClient`, qui exige les deux méthodes et est `runtime_checkable`.
Il **ne peut pas** être branché au moteur transactionnel C3, et c'est voulu.

La raison n'est pas un périmètre arbitraire, mais une propriété du moteur :

```python
write_invoked = True                      # pose AVANT l'appel
write = self._vclient.write(command, value)
```

Le moteur traite tout statut ambigu ou imprévu — et toute exception levée à
partir de l'invocation — en « potentiellement émis », donc en tentant une
relecture de confirmation. Une méthode `write` bouchon, quelle que soit sa
forme, provoquerait cette relecture ; **si la valeur courante de la chaudière se
trouvait égale à la cible, le moteur conclurait `applied` pour une écriture
jamais tentée**. Le seul statut qui l'éviterait, `DAEMON_UNREACHABLE`, serait un
mensonge typé.

Une méthode absente est honnête. Une méthode bouchon serait dangereuse.

Deux tests figent cette décision : l'un vérifie l'absence de `write`, l'autre la
non-conformité à `VClient`. Le second **échouera** le jour où `write` sera
ajoutée — c'est voulu : la conformité doit s'acquérir par une caractérisation
réelle, jamais par inadvertance.

## Limite bloquante

Le contrat d'une commande `set…` n'est **toujours pas caractérisé**. Restent
donc hors d'atteinte : le chemin d'écriture, la définition d'un succès local
d'écriture, la forme JSON d'une réponse d'écriture, et la cartographie complète
des résultats d'écriture. Voir `c5-vclient-contract.md` §11 et §12.

## Périmètre et innocuité

Aucun contact avec une installation réelle. Le composant délègue au
`ProcessRunner` qu'on lui injecte ; les tests fournissent un double.

Non modifiés par ce lot : `transport/vclient.py` — `TransportStatus` conserve ses
**six** valeurs —, `core/`, `_legacy/`, `adapters/mqtt_paho.py`,
`tests/fixtures/vclient/` (lues seulement), `pyproject.toml`. Aucune dépendance
ajoutée. Ni `boiler-bridge`, ni Arsenal, ni le Pi, ni `vcontrold`, ni la
chaudière n'ont été approchés.

## Tests

69 tests, tous déterministes et hors ligne. Un test neutralise `subprocess.run`,
`subprocess.Popen` et `socket.socket` pour prouver qu'aucun processus ni socket
n'est sollicité. Les fixtures C5 sont rejouées telles quelles à travers un faux
`ProcessRunner`, sans être recopiées ni modifiées.
