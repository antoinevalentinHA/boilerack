# C6 — Lecteur `vclient` en lecture seule

## Objet

`VClientCliReader` (`src/boilerack/adapters/vclient_cli.py`) execute une lecture
`vclient -J` et traduit son issue en `ReadResult`. C'est le premier composant
concret a parler le dialecte `vclient` — volet **lecture uniquement**.

Il leve le blocage nomme par C4 : *« l'adaptateur `vclient` concret est
deliberement absent tant que son contrat reel n'est pas caracterise »*. C5 a
caracterise la lecture ; C6 l'implemente. L'ecriture reste bloquee.

## Dependances

| Provenance | Element |
|---|---|
| **C4** | `ProcessRunner` (frontiere de sous-processus injectable), `VclientConfig` (executable, hote, port, budgets) |
| **C5** | signatures observees et 9 fixtures versionnees — voir `c5-vclient-contract.md` |
| **C3** | `TransportStatus`, `ReadResult` — **inchanges** |

Aucune dependance nouvelle. Aucun systeme de configuration nouveau : `VclientConfig`
existait deja et suffit.

## Invocation

```
<executable> [-h <host>] [-p <port>] -J -c <command>
```

Liste d'arguments, jamais de shell, jamais de concatenation, jamais de fichier
temporaire, une seule commande par invocation. `-J` est la seule option de
sortie : C5 a etabli que `error` y est le discriminant et que `raw` porte la
valeur et son unite sans analyse lexicale.

`-h` et `-p` sont omis si la configuration ne les fixe pas.

### Validation du nom de commande

Le projet ne definit **aucune grammaire** de nom de commande : `CommandSpec`
exige seulement une chaine non vide, et les noms sont explicitement « opaques
pour le transport ». C6 ne l'invente pas et se limite a ce qui empeche un nom
de changer le sens de la ligne d'arguments :

| Refus | Motif |
|---|---|
| chaine vide ou non textuelle | rien a executer |
| espaces de bordure | ambiguite d'argument |
| caractere de controle | injection dans la sortie |
| virgule | `-c` accepte une **liste** : une virgule ferait executer plusieurs commandes |
| debut par `-` | ambiguite avec une option |

Aucune liste blanche de datapoints : elle appartient au profil, pas au transport.
Un nom refuse leve `InvalidCommandName` **avant toute invocation de processus**.

## Ordre de classification

Du plus certain au plus incertain. Ce qui n'est pas prouve ne devient jamais `OK`.

| # | Condition | Statut |
|---|---|---|
| 1 | `launch_failed` | `TRANSPORT_ERROR` |
| 2 | `timed_out` | `TIMEOUT` |
| 3 | `returncode == 1` **et** `stdout == b""` **et** `stderr == b""` | `DAEMON_UNREACHABLE` |
| 4 | `stdout` non decodable en UTF-8 | `UNUSABLE_OUTPUT` |
| 5 | structure JSON non conforme | `UNUSABLE_OUTPUT` |
| 6 | `error == "ERR: command unknown"` | `UNKNOWN_COMMAND` |
| 7 | `error` non vide, autre valeur | `TRANSPORT_ERROR` |
| 8 | `error == ""` et `value` numerique finie | `OK` |

### Precisions

**Etape 1 — pas de `CLIENT_UNAVAILABLE`.** C6 **ne ratifie pas** la septieme
valeur proposee en C5. Un echec de lancement est classe prudemment en
`TRANSPORT_ERROR`. La cause est conservee dans `detail` sous la forme du **nom
de la classe d'exception** deja fourni par `ProcessResult.launch_error` — jamais
un chemin ni un message brut.

> Note d'implementation : le cadrage suggerait `launch_error is not None`. Le
> champ est un `str` valant `""` par defaut, et `ProcessResult` porte un drapeau
> typé dedie, `launch_failed`. C'est lui qui est utilise.

**Etape 2 — aucune exploitation d'une sortie partielle.** Un budget epuise rend
`TIMEOUT` meme si `stdout` contient un JSON complet.

**Etape 3 — aucune generalisation.** La signature du demon injoignable est
reconnue **exactement** telle qu'observee. Tout autre code retour non nul, ou
tout flux non vide, ne la declenche pas.

**Etape 4 — decodage strict et separe.** `stdout` et `stderr` ne sont **jamais**
fusionnes. Un `stdout` non decodable est une sortie inexploitable, jamais une
substitution silencieuse de caracteres. `stderr` est decode pour le seul
diagnostic ; s'il est lui-meme indecodable, cela n'empeche pas le verdict.

**Etape 6 — un seul signal.** `UNKNOWN_COMMAND` n'est produit que sur la valeur
**exacte** observee. Ne sont jamais utilises : le code retour seul, toute valeur
d'`error` non vide, un `raw` commencant par `ERR:`, une ligne de `stderr`, la
chaine `server error`.

**Etape 8 — succes.** Exige un JSON valide, une commande correspondante, `error`
vide, et une `value` numerique **finie**. Les booleens sont refuses explicitement
(`isinstance(True, int)` vaut `True` en Python). `raw` est conserve tel quel,
sans reparsing de l'unite.

## Frontiere `UNUSABLE_OUTPUT` / `TRANSPORT_ERROR`

La regle tient en une phrase :

> `UNUSABLE_OUTPUT` quand **le demon a repondu et que sa reponse est
> inexploitable** ; `TRANSPORT_ERROR` quand **l'echange lui-meme a echoue, ou
> que le demon signale une erreur qui n'est pas caracterisee**.

| Cas | Statut | Pourquoi |
|---|---|---|
| decodage impossible | `UNUSABLE_OUTPUT` | une reponse existe, elle est illisible |
| JSON invalide, racine non liste, liste vide, plusieurs objets, element non objet | `UNUSABLE_OUTPUT` | structure |
| champ manquant, `command` differente, types incompatibles | `UNUSABLE_OUTPUT` | structure |
| `value` non numerique, booleenne, `NaN`, `±Inf` | `UNUSABLE_OUTPUT` | contenu structurellement inexploitable |
| echec de lancement | `TRANSPORT_ERROR` | aucun echange |
| `error` non vide et non caracterise | `TRANSPORT_ERROR` | le demon a repondu, mais la cause n'est pas prouvee |

Le critere est donc **la nature du defaut**, pas sa gravite : une reponse bien
formee portant une erreur inconnue reste un probleme de transport ; une reponse
mal formee reste un probleme de structure, meme si elle est arrivee.

Toute combinaison non couverte avec certitude tombe dans l'un de ces deux
statuts, jamais dans `OK`.

## Le code retour ne conclut jamais seul

C5 a etabli qu'il ne discrimine dans aucun des deux sens : `-V` et `--help`
rendent `1` pour un resultat normal, une commande inconnue rend `0`.

Ce lecteur ne l'utilise donc qu'a **un seul endroit** : la signature exacte du
demon injoignable, conjointement a deux flux vides. Un code retour non nul
accompagne d'un JSON valide reste exploite ; un code retour nul accompagne
d'une erreur structuree reste une erreur.

## Absence volontaire de `write()`

`VClientCliReader` n'a **pas** de methode `write` et ne satisfait donc **pas**
le protocole `VClient`, qui exige les deux methodes et est `runtime_checkable`.
Il **ne peut pas** etre branche au moteur transactionnel C3, et c'est voulu.

La raison n'est pas un perimetre arbitraire, mais une propriete du moteur :

```python
write_invoked = True                      # pose AVANT l'appel
write = self._vclient.write(command, value)
```

Le moteur traite tout statut ambigu ou imprevu — et toute exception levee a
partir de l'invocation — en « potentiellement emis », donc en tentant une
relecture de confirmation. Une methode `write` bouchon, quelle que soit sa
forme, provoquerait cette relecture ; **si la valeur courante de la chaudiere se
trouvait egale a la cible, le moteur conclurait `applied` pour une ecriture
jamais tentee**. Le seul statut qui l'eviterait, `DAEMON_UNREACHABLE`, serait un
mensonge typé.

Une methode absente est honnete. Une methode bouchon serait dangereuse.

Deux tests figent cette decision : l'un verifie l'absence de `write`, l'autre la
non-conformite a `VClient`. Le second **echouera** le jour ou `write` sera
ajoutee — c'est voulu : la conformite doit s'acquerir par une caracterisation
reelle, jamais par inadvertance.

## Limite bloquante

Le contrat d'une commande `set…` n'est **toujours pas caracterise**. Restent
donc hors d'atteinte : le chemin d'ecriture, la definition d'un succes local
d'ecriture, la forme JSON d'une reponse d'ecriture, et la cartographie complete
des resultats d'ecriture. Voir `c5-vclient-contract.md` §11 et §12.

## Perimetre et innocuite

Aucun contact avec une installation reelle. Le composant delegue au
`ProcessRunner` qu'on lui injecte ; les tests fournissent un double.

Non modifies par ce lot : `transport/vclient.py` — `TransportStatus` conserve ses
**six** valeurs —, `core/`, `_legacy/`, `adapters/mqtt_paho.py`,
`tests/fixtures/vclient/` (lues seulement), `pyproject.toml`. Aucune dependance
ajoutee. Ni `boiler-bridge`, ni Arsenal, ni le Pi, ni `vcontrold`, ni la
chaudiere n'ont ete approches.

## Tests

69 tests, tous deterministes et hors ligne. Un test neutralise `subprocess.run`,
`subprocess.Popen` et `socket.socket` pour prouver qu'aucun processus ni socket
n'est sollicite. Les fixtures C5 sont rejouees telles quelles a travers un faux
`ProcessRunner`, sans etre recopiees ni modifiees.
