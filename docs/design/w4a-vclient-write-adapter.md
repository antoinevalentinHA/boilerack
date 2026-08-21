# W4-A — Contrat de l'adaptateur d'écriture `vclient`

> **Lot W4-A — documentaire.** Aucune ligne de code, aucun test modifié, aucune
> commande réelle exécutée, aucun terrain. Ce document fixe ce que l'adaptateur
> d'écriture devra garantir, et **énumère ce qu'il est encore interdit de
> savoir**. W4 reste fermé.

---

## 1. Objet

`TransactionalCore` exige un `VClient`, donc `read` **et** `write`. Or le seul
adaptateur réel du dépôt, `VClientCliReader`, n'implémente que `read`. C'est
l'une des deux dépendances manquantes qui maintiennent W4 fermé — l'autre étant
le profil réel, hors périmètre ici.

W4-A contracte l'adaptateur d'écriture que W4-B implémentera. Il répond à une
question unique :

> **Que peut-on honnêtement conclure d'une invocation locale de `vclient` en
> écriture, alors qu'aucune écriture n'a jamais été observée ?**

La réponse est délibérément étroite. Tout ce qui exige d'avoir vu une écriture
réelle est renvoyé à **W4-C**, la caractérisation terrain.

---

## 2. Statut, autorité et portée

**Statut** — contrat de conception. Normatif pour W4-B (implémentation) et
prescripteur pour W4-C (ce que le terrain devra rapporter).

**Portée** — l'invocation locale du client `vclient` pour une écriture, et la
classification de son issue en `TransportStatus`. Rien d'autre.

**Ce sur quoi W4-A a autorité :** la forme de l'invocation ; la consommation du
délai ; l'interdiction du retry ; la cartographie **fermée** des issues
distinguables hors terrain ; la liste **fermée** des inconnues.

**Ce sur quoi W4-A n'a aucune autorité :** la sémantique transactionnelle (C3),
le contenu du profil (W4-D), le choix d'un datapoint, la concurrence (W2), la
surface MQTT (W1), l'installation (C12/C13), la bascule terrain (W4-F).

**Clause de non-régression.** W4-A **MUST NOT** modifier une clause de C3, C5,
C6, W1, W2 ou W3. Si une décision paraissait l'exiger, la décision est fautive.

---

## 3. Autorités et acquis

| Autorité | Ce que W4-A consomme sans le réécrire |
| --- | --- |
| **C3** — `c3-transactional-core.md`, `core/engine.py` | Une seule invocation d'écriture par transaction, aucun retry. Frontière explicite `write_invoked`. Seul un statut **démontrant** la non-émission produit `bridge_unavailable`. `UNKNOWN_COMMAND` conclut **sans relecture**. |
| **C5** — `c5-vclient-contract.md` | Faits réels de `vclient` **en lecture** ; §3 « le code retour ne discrimine rien » ; §9 durées ; §10 faits et inconnues ; §11 limite bloquante ; §12 protocole de caractérisation d'écriture. |
| **C6** / `adapters/vclient_cli.py` | Forme d'invocation réelle, validation du nom de commande, ordre de classification « du plus certain au plus incertain », et refus de ratifier `CLIENT_UNAVAILABLE`. |
| **W1** | La surface MQTT ; W4-A n'y touche pas. |
| **W2** | Le propriétaire unique sérialise les opérations `vclient` ; l'adaptateur n'est pas l'autorité de concurrence. |
| **W3** | Le câblage existe et reste **latent**. |
| `transport/vclient.py` | `TransportStatus`, `ReadResult`, `WriteResult`, Protocol `VClient`. |
| `adapters/config.py` | `VclientConfig`, dont `write_timeout_s`. |

**Acquis repris sans redémonstration :** « écriture réussie au niveau transport »
signifie que le démon a accepté la commande, **pas** que la chaudière a confirmé
la valeur — c'est le docstring de `WriteResult` lui-même.

---

## 4. Hors périmètre — liste fermée

W4-A ne traite **aucun** des points suivants :

1. le nom réel d'une commande d'écriture, et le choix d'un datapoint ;
2. le contenu d'un `Profile` réel : bornes, pas, tolérances, `bounds_source` ;
3. l'activation de la voie transactionnelle en production ;
4. la caractérisation terrain elle-même ;
5. la bascule *one-writer* et la coexistence avec le pont historique ;
6. l'arbitrage du namespace de C7 §14 ;
7. la réserve I3 sur la cadence de `_confirm` ;
8. toute modification de `src/`, de `tests/`, de la configuration, du CLI, du
   cycle de vie, de MQTT, de systemd ou de l'installation.

---

## 5. Faits d'entrée — mesurés, non supposés

| # | Fait | Mesure |
| --- | --- | --- |
| F1 | `VClient` (Protocol) expose `read` **et** `write` | `transport/vclient.py` |
| F2 | `VClientCliReader` n'implémente que `read` | `hasattr(..., "write")` → **False** |
| F3 | `write_timeout_s` est **déclaré et validé, jamais consommé** | **2** lignes, toutes deux dans `adapters/config.py` (l. 103, l. 112) |
| F4 | `write_timeout_s` n'est **pas** une clé utilisateur | absent de `_CLES_VCLIENT` dans `config.py` |
| F5 | Aucun adaptateur d'écriture de production | **0** définition de `write` hors Protocol et hors `testing/` |
| F6 | Aucune commande d'écriture **réelle** dans le code de production | les deux seuls littéraux d'écriture du dépôt sont des noms **fictifs** de `testing/fake_profile.py`, employés par les doubles et par eux seuls |
| F7 | Aucun `Profile` de production | seul `testing/fake_profile.py` en construit un |
| F8 | C5 ne caractérise que la **lecture** | titre : « observations de lecture » |
| F9 | C5 **interdit** d'extrapoler vers l'écriture | §11 : « Toute affirmation sur l'écriture serait une extrapolation » |
| F10 | Une commande inconnue peut rendre **code retour 0** | C5 §10, fait 8 |
| F11 | Le code retour seul ne discrimine rien | C5 §3 |
| F12 | `WriteResult` porte `status` et `detail`, **pas** `raw` | `transport/vclient.py` |

Ces **onze** faits F1 à F11 couvrent les dix faits d'entrée exigés à l'ouverture
du lot — F3 et F4 en détaillent un seul. **F12** est un constat supplémentaire,
traité en §7.3.

---

## 6. La frontière fondamentale — succès local ≠ écriture appliquée

> **Clause.** L'adaptateur d'écriture rapporte **l'issue de l'invocation locale**
> de `vclient`. Il **MUST NOT** conclure, ni suggérer, qu'une valeur a été
> appliquée par la chaudière.

La vérité métier appartient à C3, et à lui seul : écriture → relecture →
confirmation → verdict. `TransportStatus.OK` sur une écriture signifie au plus
*« le client a rendu une issue que rien ne permet de classer comme une erreur
locale »*. Ce n'est ni `applied`, ni une promesse, ni une présomption.

Trois conséquences directes :

1. l'adaptateur **MUST NOT** produire, retourner ou journaliser un verdict de la
   taxonomie C3 (`accepted`, `applied`, `rejected`, `timeout`, une `Reason`) ;
2. l'adaptateur **MUST NOT** faire de relecture lui-même : la confirmation est
   une étape du cœur, avec son propre budget ;
3. une invocation qui paraît réussie **n'est pas** une preuve d'application, et
   le contrat ne l'autorise à aucun moment à s'y substituer.

---

## 7. Interface `write()`

### 7.1 Ce que le Protocol impose déjà

```python
def write(self, command: str, value: float) -> WriteResult: ...
```

`command` est une **chaîne opaque** — le transport ne l'interprète pas et ne
décide jamais quel datapoint écrire ; elle provient de `CommandSpec.write`, dont
l'autorité est le profil. `value` est un flottant, déjà validé par C3.

### 7.2 Politique d'exception — symétrique de `read()`

> **Clause.** `write()` **MUST NOT** lever pour une **issue de transport** :
> toute cause est portée par `WriteResult.status`. Il **MAY** lever
> `InvalidCommandName` pour un nom de commande invalide, **avant toute
> invocation de processus**, exactement comme `read()`.

**Conséquence à connaître, et assumée.** `core/engine.py` pose
`write_invoked = True` **avant** d'appeler `vclient.write`. Une exception levée
depuis `write()` est donc traitée comme « potentiellement émise » : le cœur
engage la **boucle de confirmation**, qui relit jusqu'à conclusion ou épuisement
de son budget. Pour un nom invalide — rejeté localement, sans processus — cette
classification ne prétend jamais la non-émission, ce qui est le point important.
Elle expose en revanche au faux positif d'application décrit en **§11.4**, et
pour la même raison. W4-A retient la symétrie avec `read()` plutôt qu'une
exception à la règle, et enregistre la conséquence plutôt que de la masquer.

### 7.3 Insuffisance signalée de `WriteResult` — conséquence W4-B

`ReadResult` porte `raw`, qui conserve la sortie observée ; `WriteResult` ne le
porte pas. Or W4-C devra capturer `stdout` et `stderr` d'une écriture réelle, et
un adaptateur qui n'a nulle part où les déposer ne peut pas les rendre à un
appelant.

> **W4-A ne modifie pas le Protocol.** Le manque est **signalé** comme
> conséquence à trancher en W4-B : soit `detail` suffit pour le diagnostic, soit
> W4-B propose l'ajout d'un champ, ce qui **MUST** faire l'objet d'un arbitrage
> explicite et non d'un ajout opportuniste.

---

## 8. Contrat d'invocation

> **Clause.** Un appel à `write()` déclenche **au plus une** invocation de
> processus `vclient`, sans shell, sans concaténation de chaîne, avec les
> arguments passés en liste.

L'adaptateur **MUST** :

- valider le nom de commande **avant** toute invocation, selon les mêmes règles
  que `VClientCliReader._validate_command` — chaîne non vide, sans espaces
  d'encadrement, sans caractère de contrôle, sans virgule, ne commençant pas par
  `-`. Ces règles protègent la **ligne d'arguments**, elles ne constituent
  aucune grammaire de datapoint ;
- consommer `write_timeout_s` (§10) ;
- capturer séparément `stdout`, `stderr` et le code retour ;
- traiter un échec de lancement comme une issue, non comme une exception ;
- décoder strictement, sans substitution silencieuse.

L'adaptateur **MUST NOT** : réessayer (§13) ; enchaîner deux commandes ; se
rabattre sur une autre syntaxe ; interpréter la sortie au-delà des faits établis ;
décider quel datapoint écrire.

> **La forme exacte de la ligne d'arguments d'écriture n'est pas contractée
> ici.** Celle de la lecture — `<exécutable> [-h host] [-p port] -J -c <commande>`
> — est établie par observation ; rien ne prouve qu'une écriture s'invoque de la
> même manière, ni que `-J` produise une sortie exploitable pour elle. C'est
> l'inconnue **I-1** (§16).

### 8.1 Deux parties de nature différente, à ne pas confondre

Un adaptateur d'écriture réunit deux choses que W4-A sépare explicitement :

| | Partie | Dépend du terrain ? |
| --- | --- | --- |
| **A** | **Mécanique de transport** — validation locale du nom, budget de temps, lancement du processus, capture des flux, décodage, classification, absence de retry | **non** |
| **B** | **Fabrication de l'invocation réelle** — ligne d'arguments d'écriture et représentation textuelle de la valeur | **oui** — inconnues I-1 et I-8 |

> **Clause.** W4-B **MUST** séparer A de B. La partie **B MUST** être un
> collaborateur **injecté ou paramétré**, substituable par un double en test, et
> **MUST NOT** être résolue en production avant W4-C.

W4-A ne nomme volontairement ni classe ni module pour la partie B : le contrat
fixe la **propriété** — une frontière substituable — et laisse l'architecture à
W4-B, à charge pour lui de ne pas la surdimensionner.

---

## 9. Cartographie `TransportStatus` — liste fermée

Cartographie des issues **distinguables hors terrain**. L'ordre est celui du
plus certain au plus incertain, repris de `VClientCliReader._classify`.

| # | Situation observable | Statut | Fondement |
| --- | --- | --- | --- |
| 1 | Le processus n'a pas pu être lancé (`launch_failed`) | `TRANSPORT_ERROR` | Précédent exact du chemin de lecture ; C6 ne ratifie pas `CLIENT_UNAVAILABLE`. Voir §11.3 à §11.5 |
| 2 | Le délai est épuisé (`timed_out`) | `TIMEOUT` | §10 |
| 3 | Sortie non décodable en UTF-8 | `UNUSABLE_OUTPUT` | précédent de lecture |
| 4 | Sortie décodable mais de forme inattendue | `UNUSABLE_OUTPUT` | précédent de lecture |
| 5 | **Tout le reste**, y compris code retour nul | `TRANSPORT_ERROR` | §9.2 |

### 9.1 Ce que cette table ne contient pas, et pourquoi

**`OK` n'y figure pas.** Aucune signature de succès d'écriture n'a été observée.
Un adaptateur qui rendrait `OK` avant W4-C affirmerait un fait qu'il ne possède
pas ; et comme le cœur traite tout statut non prouvé non émis par une relecture,
rendre `TRANSPORT_ERROR` au lieu de `OK` **ne perd rien** : la relecture décide
dans les deux cas, et elle seule.

> **Clause.** Avant W4-C, l'adaptateur d'écriture **MUST NOT** rendre
> `TransportStatus.OK`. Cette interdiction est **temporaire** et lève dès que
> W4-C aura établi une signature de succès local.

**`DAEMON_UNREACHABLE` n'y figure pas** — §11.6. **`UNKNOWN_COMMAND` n'y figure
pas** — §12.

### 9.2 Pourquoi un code retour nul ne suffit jamais

C5 §3 établit que le code retour ne discrimine rien, et C5 §10 fait 8 qu'une
commande inconnue rend **0**. Le chemin de lecture ne s'appuie donc pas sur lui,
mais sur le champ `error` de la sortie JSON.

> **Clause.** L'adaptateur **MUST NOT** dériver une issue du seul code retour.
> En particulier, `returncode == 0` **MUST NOT** produire un statut favorable.

---

## 10. Délai d'écriture

> **Clause.** `write()` **MUST** consommer `VclientConfig.write_timeout_s` comme
> budget de l'invocation, de la même façon que `read()` consomme
> `read_timeout_s`.

Trois choses distinctes, à ne pas confondre :

| | |
| --- | --- |
| **Mécanisme** | contracté ici : un budget passé au lanceur de processus, fini et strictement positif, déjà validé par `VclientConfig` |
| **Valeur actuelle** | `5.0` s par défaut, **non exposée à l'utilisateur** (F4). Ce n'est pas une valeur qualifiée : c'est une valeur d'attente |
| **Qualification** | **INCONNUE**. C5 §9 mesure une **lecture** réelle entre 2 669 et 4 029 ms sous contention, et avertit qu'un budget de trois secondes « peut être trop court ». Aucune mesure d'écriture n'existe |

### 10.1 Ce qu'un délai épuisé permet de conclure

> **Rien sur l'émission.** Le délai expire **après** le lancement du processus.
> Une commande a donc pu partir, être reçue, voire être appliquée. `TIMEOUT` est
> un état d'**incertitude**, jamais une preuve d'échec avant émission.

C'est exactement ainsi que le cœur le traite : `TIMEOUT` n'appartient pas à
`_PROVEN_NOT_EMITTED`, donc il déclenche la boucle de confirmation. La chaîne est
cohérente, et W4-A ne la modifie pas.

> **Ce que l'expiration fait au processus, en revanche, n'est pas caractérisé.**
> Le mécanisme repose sur `subprocess.run(timeout=…)`, qui **termine l'enfant**.
> Ce qu'une telle interruption produit sur une transaction Optolink déjà engagée
> — poursuite côté démon, interruption, application partielle — est l'inconnue
> **I-13** (§16). W4-A n'en propose aucune réponse.

---

## 11. `_PROVEN_NOT_EMITTED` — ce qui prouve vraiment la non-émission

### 11.1 Ce que la frontière signifie

`core/engine.py` définit `_PROVEN_NOT_EMITTED = frozenset({DAEMON_UNREACHABLE})`
et n'en tire `bridge_unavailable` que là. Son commentaire est sans ambiguïté :
« Seul un statut EXPLICITEMENT démontré *non émis* peut produire
`bridge_unavailable` ».

> **Ne jamais confondre « aucune preuve d'application » et « preuve que rien n'a
> été émis ».** Le premier énoncé est le cas ordinaire ; le second est une
> affirmation forte, et c'est la seule dont l'erreur soit dangereuse dans le
> sens grave : déclarer qu'aucune écriture n'a eu lieu alors qu'une valeur a pu
> partir.

### 11.2 Examen des candidats

| Candidat | Prouve la non-émission ? | Décision W4-A |
| --- | --- | --- |
| Exécutable absent, échec **avant** création du processus | **Oui, structurellement** — aucun processus n'a existé, donc aucun octet n'a pu partir. Cette preuve est **logique**, elle ne dépend d'aucune observation de `vclient` | mais voir §11.3 |
| Nom de commande invalide, rejeté avant invocation | Oui, même raison | levée d'exception (§7.2) ; le cœur restera pessimiste |
| Délai épuisé après lancement | **Non** — §10.1 | `TIMEOUT` |
| Code retour non nul | **Non** — il peut suivre une émission | `TRANSPORT_ERROR` |
| Diagnostic serveur sur `stderr` | **Non** — non caractérisé en écriture | `TRANSPORT_ERROR` |
| Démon injoignable, signature « rc = 1 et deux flux vides » | **Non démontré en écriture** — §11.4 | `TRANSPORT_ERROR` |

### 11.3 Le seul cas structurellement prouvé n'est pas exprimable

Un échec **avant création du processus** prouve la non-émission. Mais le cœur ne
reconnaît la non-émission qu'à travers `DAEMON_UNREACHABLE`, dont la sémantique
déclarée est une **cause** — « le démon `vcontrold` n'est pas joignable » — et non
une **preuve**. Employer ce statut pour un binaire introuvable serait, selon les
termes mêmes de `adapters/vclient_cli.py`, « un mensonge typé ».

> **Clause.** W4-B **MUST** classer un échec de lancement en `TRANSPORT_ERROR`,
> comme le fait déjà le chemin de lecture. C'est le choix conservateur correct
> avec la taxonomie actuelle : il ne prétend **jamais** la non-émission.

### 11.4 Ce que ce choix conservateur ne protège pas

**Il protège l'émission, pas le verdict.** Une fois `TRANSPORT_ERROR` rendu, le
cœur engage la boucle de confirmation. Si une relecture y trouve la valeur
courante conforme à la cible, `_confirm` rend **`applied`** — alors qu'**aucun
processus n'a été lancé** et qu'aucune écriture n'a eu lieu.

Ce n'est pas une hypothèse d'école : `adapters/vclient_cli.py` documente déjà ce
mécanisme, et c'est précisément pour cela que ce module n'expose délibérément
aucune méthode `write` —

> « […] si la valeur courante de la chaudière se trouvait égale à la cible, le
> moteur conclurait `applied` pour une écriture **JAMAIS TENTÉE**. »

Le cas est **d'autant plus atteignable en W4-C** que C5 §12.3 prescrit
précisément de **réécrire la valeur courante à l'identique** : la relecture y
sera conforme par construction.

Nature exacte du défaut, à ne pas confondre :

- ce n'est **pas** une émission réelle passée inaperçue ;
- c'est un **faux positif d'application**, dû à une **perte d'information de
  taxonomie** : l'adaptateur sait que rien n'a été émis, et n'a aucun moyen de le
  dire ;
- la classification reste donc **conservatrice sur l'émission** — elle ne
  prétend jamais que rien n'est parti — mais elle n'est **pas exacte sur le
  verdict `applied`**.

> **Clause.** `DAEMON_UNREACHABLE` **MUST NOT** être employé pour masquer ce
> défaut. Sa sémantique désigne une autre cause, et il conclut **sans
> relecture** : l'erreur deviendrait définitive au lieu d'être seulement
> imprécise. Le défaut est enregistré comme risque (§24) et transmis tel quel à
> W4-B et à W4-C.

### 11.5 `CLIENT_UNAVAILABLE` — spécifié, non ratifié

W4-A ne prétend pas qu'un statut de non-émission « resterait à concevoir ».
L'état exact est le suivant :

- **C5 §6 le spécifie déjà** : sémantique — « le client local n'a pas pu être
  lancé ; **aucune commande n'a été remise au démon** » —, condition d'émission
  fondée sur un signal qui existe (`launch_failed`, porté par `ProcessResult`),
  impact sur C3 (§6.3) et sur les acquittements (§6.4) ;
- **C6 ne le ratifie pas** : « C6 **ne ratifie pas** la septième valeur proposée
  en C5. Un échec de lancement est classé prudemment en `TRANSPORT_ERROR` » ;
- **la taxonomie active ne l'expose donc pas** : `TransportStatus` compte six
  valeurs, et `CLIENT_UNAVAILABLE` n'apparaît dans le code qu'en commentaire ;
- **son adoption exigerait un arbitrage contractuel séparé**, portant au moins
  sur C6, sur la cartographie C3 et sur les acquittements.

> **W4-A ne fait pas cet arbitrage et ne le prépare pas.** Il enregistre que la
> réponse au défaut de §11.4 existe déjà à l'état de proposition, et que la
> retenir relève d'un lot dédié.

### 11.6 Pourquoi la signature du démon injoignable n'est pas transposée

C5 fait 10 établit, **en lecture**, qu'un démon injoignable rend `1` avec les
deux flux vides. Cette défaillance survient avant que la commande n'atteigne le
démon, ce qui rend la transposition à l'écriture *plausible*. Mais C5 §11
interdit explicitement de conclure d'une observation de lecture vers l'écriture,
et l'erreur porterait ici sur le **seul** statut qui affirme la non-émission.

> **Clause.** Avant W4-C, l'adaptateur d'écriture **MUST NOT** rendre
> `DAEMON_UNREACHABLE`. Interdiction **temporaire**, levable par W4-C si la même
> signature est observée sur une invocation d'écriture.

---

## 12. `UNKNOWN_COMMAND` — non transposable, et pourquoi c'est grave

### 12.1 Ce que le cœur en fait

```python
if status is TransportStatus.UNKNOWN_COMMAND:
    return Ack.rejected(request_id, Reason.UNSUPPORTED_COMMAND)
```

Ce statut **court-circuite la relecture**. C'est le seul, avec
`DAEMON_UNREACHABLE`, à conclure sans vérifier le fait physique — au motif qu'un
défaut permanent de déclaration ne se vérifie pas par observation.

### 12.2 Ce qui est réellement établi

Le chemin de lecture ne reconnaît **pas** la chaîne `SRV ERR: command unknown`
vue sur `stderr` : il teste l'égalité exacte du champ **`error` de la sortie
JSON** avec `"ERR: command unknown"`, et son commentaire précise « UNIQUEMENT le
signal exact observé ». `stderr` est décodé pour le diagnostic et **ne participe
jamais** à la classification.

### 12.3 Ce qui n'est pas établi

Que `-J` produise une sortie JSON pour une écriture ; que le champ `error` y
existe ; qu'une commande d'écriture inconnue y porte la même chaîne ; qu'un
**refus** — commande connue mais valeur ou contexte inacceptable — ne s'y exprime
pas de la même manière. Le libellé du statut couvre d'ailleurs les deux :
« inconnue du démon **ou refusée par lui** ». Confondre les deux ferait rejeter
une commande valide en `unsupported_command`, **sans relecture**, alors qu'une
écriture a pu partir.

> **Clause.** Avant W4-C, l'adaptateur d'écriture **MUST NOT** rendre
> `UNKNOWN_COMMAND`. Une commande d'écriture inconnue sera classée
> `TRANSPORT_ERROR`, ce qui déclenche une relecture : verdict moins spécifique,
> jamais faussement définitif. Interdiction **temporaire**, levable par W4-C.

---

## 13. Aucun retry

> **Clause.** Un appel à `write()` **MUST** correspondre à **au plus une**
> invocation de processus d'écriture.

Sont interdits, sans exception : réessai après délai épuisé ; réessai sur code
retour non nul ; réessai sur diagnostic d'erreur ; repli vers une autre syntaxe ;
seconde invocation « de vérification ». C3 contracte déjà « une SEULE invocation
d'écriture par transaction, jamais de retry » ; W4-A l'étend à l'intérieur de
l'adaptateur, où le cœur ne voit rien.

---

## 14. Concurrence — rappel, pas de redéfinition

W2 a tranché : un **propriétaire unique** exécute toutes les opérations
`vclient`, et deux opérations ne sont jamais simultanées. L'adaptateur n'est pas
l'autorité de concurrence.

> **Clause.** W4-B **MUST NOT** introduire de verrou, de fil, de file ou de
> travailleur d'arrière-plan. L'adaptateur est **synchrone et sans état**
> au-delà de sa configuration.

---

## 15. Valeur d'écriture et sérialisation

`CommandSpec` porte `type`, `min`, `max`, `step`, `confirm_tolerance` et
`idempotent` ; `core/validation.py` les applique **avant** toute admission.

> **Clause.** L'adaptateur **MUST NOT** revalider les bornes métier — ni `min`,
> ni `max`, ni `step`, ni la tolérance, ni l'idempotence. Il transporte.

Ce qu'il **doit** en revanche garantir : une **sérialisation déterministe** de la
valeur, c'est-à-dire que deux appels portant la même valeur produisent la même
ligne d'arguments, sans dépendance à la locale. C5 §7 mesure que, pour la lecture
observée, la sortie est identique entre `en_GB.UTF-8` et `LC_ALL=C` ; la
symétrie n'est pas démontrée pour l'entrée.

> **La forme textuelle exacte de la valeur n'est pas contractée ici** — nombre de
> décimales, séparateur, notation d'un entier. C'est l'inconnue **I-8** (§16).

Ces deux exigences ne vivent pas au même endroit : le **déterminisme** appartient
à la partie A de §8.1 et se teste hors terrain ; la **forme réellement acceptée**
appartient à la partie B, qui devra combiner syntaxe d'invocation (I-1) et
représentation de la valeur (I-8) à partir des faits de W4-C. Aucune forme
concrète n'est arrêtée aujourd'hui.

---

## 16. Inconnues terrain — liste fermée

Chacune est **INCONNUE**, et aucune ne doit être comblée par intuition. Toutes
relèvent de **W4-C**, dont le protocole est déjà écrit en **C5 §12** — W4-A ne le
répète pas.

| # | Inconnue | Conséquence si devinée |
| --- | --- | --- |
| **I-1** | Syntaxe exacte d'invocation d'une écriture ; `-J` produit-il une sortie exploitable | invocation muette ou mal formée |
| **I-2** | Nom réel de la première commande d'écriture | **écriture sur un datapoint non vérifié** |
| **I-3** | Forme de `stdout` sur une écriture acceptée | faux `OK` |
| **I-4** | Forme de `stderr` sur une écriture | classification fondée sur le mauvais flux |
| **I-5** | Code retour d'une écriture, acceptée ou refusée | reproduction du piège de C5 §3 |
| **I-6** | Durée réelle d'une écriture | `write_timeout_s` mal dimensionné |
| **I-7** | Délai avant qu'une relecture soit fiable | `timeout` alors que la valeur a été appliquée |
| **I-8** | Normalisation de la valeur par le démon ou la chaudière | confirmation impossible malgré une écriture réussie |
| **I-9** | Comportement hors domaine (C5, inconnu 6) | refus pris pour un succès, ou l'inverse |
| **I-10** | Atomicité observable d'une écriture | conclusions erronées sur un état intermédiaire |
| **I-11** | Démon acceptant, chaudière appliquant autrement | `applied` fondé sur une relecture trompeuse |
| **I-12** | Signature d'un délai épuisé **après** émission | `TIMEOUT` interprété comme non-émission |
| **I-13** | **Effet de l'expiration du budget local sur une écriture en cours.** Le mécanisme repose sur `subprocess.run(timeout=…)`, qui **termine le processus enfant** à l'expiration. Restent inconnus : si la commande avait déjà été transmise au démon ; si le démon poursuit ou interrompt la transaction Optolink après disparition du client ; si l'état a été appliqué, partiellement appliqué ou pas du tout ; l'effet d'une interruption sur le protocole lui-même ; et si une relecture ultérieure permet de désambiguïser | interprétation fausse d'un `TIMEOUT` — dans les deux sens |
| **I-14** | Signatures de lecture réellement transposables à l'écriture | fondement de §11.6 et §12.3 |
| **I-15** | Signature d'un démon injoignable en écriture | faux `bridge_unavailable` — l'erreur la plus grave |

---

## 17. Journalisation

Convention existante du cœur : journaliser `request_id`, rôle, étape et **type**
d'exception, jamais la charge utile complète.

> **Clause.** L'adaptateur **MAY** journaliser : le nom logique de la commande,
> la valeur transportée, le code retour, la durée observée et un extrait de
> diagnostic **borné**. Il **MUST NOT** journaliser un secret de configuration,
> et **MUST NOT** créer de système d'observabilité nouveau : ni métrique, ni
> compteur, ni fichier.

La valeur écrite est une consigne de chauffage, pas un secret ; la journaliser
est nécessaire pour reconstituer une transaction. `stdout` et `stderr` **MAY**
être journalisés bornés, et **MUST** être capturés intégralement pour W4-C — ce
sont deux besoins distincts.

---

## 18. Obligations de W4-B — checklist falsifiable

**W4-B MUST :**

1. implémenter `write(command, value) -> WriteResult` satisfaisant le Protocol
   `VClient`, de sorte que l'adaptateur réel satisfasse enfin `VClient` ;
2. valider le nom de commande **avant** toute invocation, selon les règles de
   §8 ;
3. consommer `write_timeout_s` ;
4. n'effectuer **au plus qu'une** invocation de processus par appel ;
5. capturer `stdout`, `stderr` et le code retour séparément ;
6. classer selon la table **fermée** de §9, et elle seule ;
7. ne jamais lever pour une issue de transport ;
8. être développable et testable **entièrement contre doubles**, sans terrain ;
9. **séparer la mécanique de transport de la fabrication de l'invocation**
   (§8.1) ;
10. rendre la fabrication de l'invocation **injectée ou paramétrée**,
    substituable par un double, et **non résolue en production** ;
11. trancher explicitement la question de `WriteResult.raw` (§7.3) ;
12. laisser la production **fermée** : aucun appel à
    `build_transaction_surface`, aucun `Profile` réel, aucun nom de commande en
    dur.

**W4-B MUST NOT :**

13. rendre `OK`, `DAEMON_UNREACHABLE` ou `UNKNOWN_COMMAND` (§9.1, §11.6, §12.3) ;
14. dériver une issue du seul code retour ;
15. réessayer, sous quelque forme que ce soit ;
16. relire pour confirmer ;
17. valider une borne métier ;
18. introduire verrou, fil ou travailleur ;
19. inventer un nom de commande, une syntaxe ou une valeur de délai qualifiée ;
20. livrer une fabrique d'invocation d'écriture **résolue** — c'est-à-dire
    produisant une ligne d'arguments concrète — avant W4-C ;
21. modifier `core/`, C3, C5 ou la taxonomie.

### 18.1 Ce que W4-B livrera, et ce qu'il ne livrera pas

W4-B **peut** être développé et éprouvé **entièrement hors terrain**, à quatre
conditions : la mécanique de transport (partie A) est complète ; une fabrique
d'invocation est **injectée** dans les tests ; aucune fabrique réelle n'existe en
production ; aucune ligne d'arguments d'écriture concrète n'est inventée.

> **Formulation exacte de ce que W4-B livre.** Un adaptateur **structurellement
> complet, mais NON RÉSOLU POUR L'INVOCATION RÉELLE**. Il **MUST NOT** être
> présenté comme utilisable sur une chaudière.

Ne peuvent honnêtement pas être codées avant W4-C : la reconnaissance d'un succès
local, celle d'une commande inconnue, celle d'un démon injoignable en écriture,
la forme textuelle de la valeur, et la ligne d'arguments elle-même.

### 18.2 Frontière de production après W4-B

Aujourd'hui, deux dépendances absentes ferment la production : l'adaptateur
d'écriture et le profil réel. **Après W4-B, la première ne sera plus absente au
sens structurel** — un adaptateur existera.

> **Clause.** Cela **ne rouvre rien**. Tant que W4-C et W4-D n'ont pas livré leurs
> faits, il n'existe **aucune ligne d'arguments d'écriture réelle**, **aucun
> `Profile` réel**, et **aucune composition transactionnelle active**. La
> fabrique d'invocation non résolue (§8.1, obligation 10) est une barrière
> supplémentaire, pas un substitut à celles-ci.
>
> L'activation elle-même relève de **W4-E**, et n'est pas traitée ici.

---

## 19. Ce que W4-C devra rapporter

Le protocole est **C5 §12** ; W4-A ne le réécrit pas. Il précise seulement les
champs que W4-C **MUST** renseigner pour permettre W4-D et lever les
interdictions temporaires de §9.1, §11.4 et §12.3 :

1. le nom réel de la commande d'écriture retenue ;
2. la ligne d'invocation réelle, telle qu'exécutée ;
3. `stdout` et `stderr` capturés **intégralement et séparément** ;
4. le code retour ;
5. la durée mesurée ;
6. la valeur **avant** l'essai ;
7. l'écriture **à l'identique**, conformément à C5 §12.3 ;
8. la valeur **après**, et le délai au bout duquel la relecture devient stable ;
9. la preuve de retour arrière, armée avant l'essai ;
10. l'**état du pont historique pendant l'essai** — actif ou arrêté, et comment
    cela a été établi ;
11. ce qu'il est possible d'établir, **par une méthode sûre et autorisée**, sur
    l'effet d'une expiration du budget local et de la terminaison du processus
    (inconnue **I-13**).

> **Clause de prudence sur la preuve 11.** « Preuve terrain demandée » ne
> signifie **jamais** « obligation de provoquer un incident ». Si aucune méthode
> sûre ne permet d'observer une interruption en cours d'écriture, la conclusion
> légitime de W4-C est :
>
> **INCONNU NON LEVÉ — INTERDICTION CONSERVÉE.**
>
> Un lot terrain a le droit de rapporter qu'il n'a pas pu établir un fait. Il n'a
> pas le droit de le deviner.

---

## 20. One-writer

> **W4-A ne résout pas le *one-writer* et n'en conçoit aucun mécanisme.**

- W4-B n'a **aucune autorité** pour détecter ou désactiver un autre écrivain, et
  **MUST NOT** en implémenter la moindre heuristique ;
- W4-C **MUST** suivre le protocole terrain de C5 §12, dont la coordination avec
  le superviseur local (§12.7) ;
- **W4-F** porte la procédure de bascule, sa preuve de retour arrière, et elle
  seule.

W2 §15.4 avait déjà séparé « un seul appel `vclient` à la fois **dans
Boilerack** » — contracté et satisfait — de « un seul système au monde autorisé à
écrire » — hors périmètre. W4-A maintient cette séparation.

---

## 21. Portes signalées, hors périmètre

| Porte | État | Propriétaire |
| --- | --- | --- |
| **Namespace** — C7 §14 et W1 §19 : `boilerack/command` et `boilerack/ack` contre `boiler` pour la lecture ; à arbitrer « avant toute composition root publique » | signalée, non tranchée | **W4-E** |
| **I3** — la cadence de `_confirm` sous une horloge interruptible par signal : un signal raccourcit au plus un intervalle, sans altérer le budget, qui repose sur le temps monotone réel | réserve **mineure**, à documenter au câblage réel | **W4-E/F** |

Aucune n'est touchée ici.

---

## 22. Propriétés à verrouiller

| # | Propriété | Ancrage |
| --- | --- | --- |
| **W4A-P1** | Un appel à `write()` déclenche **au plus une** invocation de processus — cardinalité. | §8 |
| **W4A-P2** | `write_timeout_s` est effectivement consommé comme budget de l'invocation. | §10 |
| **W4A-P3** | Un délai épuisé n'est jamais transformé en succès d'écriture. | §10.1 |
| **W4A-P4** | Un code retour nul ne suffit jamais à produire un statut favorable. | §9.2 |
| **W4A-P5** | Aucun réessai — y compris repli vers une autre syntaxe ou seconde invocation « de vérification » : P1 borne le nombre, P5 interdit le motif. | §13 |
| **W4A-P6** | L'adaptateur ne revalide aucune borne métier. | §15 |
| **W4A-P7** | L'adaptateur ne relit jamais et ne conclut jamais à l'application physique. | §6 |
| **W4A-P8** | L'adaptateur ne rend pas `OK` avant W4-C. | §9.1 |
| **W4A-P9** | L'adaptateur ne rend pas `DAEMON_UNREACHABLE` avant W4-C. | §11.6 |
| **W4A-P10** | L'adaptateur ne rend pas `UNKNOWN_COMMAND` avant W4-C. | §12.3 |
| **W4A-P11** | Le nom de commande est validé avant toute invocation. | §8 |
| **W4A-P12** | Aucune issue de transport ne remonte sous forme d'exception. | §7.2 |
| **W4A-P13** | La sérialisation de la valeur est déterministe et indépendante de la locale. | §15 |
| **W4A-P14** | L'adaptateur n'introduit ni verrou, ni fil, ni travailleur. | §14 |
| **W4A-P15** | Aucun verdict de la taxonomie C3 n'est produit par l'adaptateur. | §6 |
| **W4A-P16** | Aucun nom de commande d'écriture n'est écrit en dur. | §8, §18 n° 19 |
| **W4A-P17** | La production reste fermée : aucune voie transactionnelle activée. | §18 n° 12, §18.2 |
| **W4A-P18** | Les inconnues de §16 restent explicitement inconnues. **Invariant documentaire**, vérifiable par inspection, non par exécution. | §16 |
| **W4A-P19** | La fabrication de l'invocation d'écriture est **injectée** et **non résolue** en production. | §8.1, §18.1 |

---

## 23. Mutations à tuer en W4-B

| # | Mutation | Propriété tuée |
| --- | --- | --- |
| **W4A-M1** | Ignorer `write_timeout_s`. | P2 |
| **W4A-M2** | Réessayer après un délai épuisé. | P5 |
| **W4A-M3** | Rendre `OK` quand le code retour vaut zéro. | P4, P8 |
| **W4A-M4** | Invoquer `vclient` deux fois dans un seul `write()`. | P1 |
| **W4A-M5** | Transformer un délai épuisé en `DAEMON_UNREACHABLE`. | P3, P9 |
| **W4A-M6** | Rendre `UNKNOWN_COMMAND` sur un diagnostic de `stderr`. | P10 |
| **W4A-M7** | Valider `min`/`max` dans l'adaptateur. | P6 |
| **W4A-M8** | Relire pour confirmer avant de rendre le résultat. | P7 |
| **W4A-M9** | Lever une exception pour une issue de transport. | P12 |
| **W4A-M10** | Sérialiser la valeur via la locale courante. | P13 |
| **W4A-M11** | Écrire un nom de commande en dur dans l'adaptateur. | P16 |
| **W4A-M12** | Rendre un `Ack` ou une `Reason` depuis l'adaptateur. | P15 |
| **W4A-M13** | Coder la ligne d'arguments d'écriture en dur au lieu de l'injecter. | P19 |

**Quatre** propriétés n'ont pas de mutation dédiée, pour des raisons distinctes :
**P11** est une garde déjà éprouvée, telle quelle, sur le chemin de lecture ;
**P14** — ni verrou, ni fil, ni travailleur — se démontre par **inspection du
module**, comme le dépôt le fait déjà ailleurs, et un mutant introduisant un
verrou inerte ne prouverait rien de plus ; **P17** et **P18** sont des invariants
de **non-action**, vérifiables par inspection.

---

## 24. Risques

1. **Écriture sur un datapoint non vérifié** — barrière : §16 I-2, et l'absence
   de tout nom de commande dans le dépôt. Fermeture : W4-C puis W4-D.
2. **Faux `bridge_unavailable`** — le seul mensonge grave possible. Barrière :
   §11.6 et §12.3 interdisent les deux statuts concernés avant W4-C.
3. **`applied` alors qu'aucune commande n'a été émise** — un échec de lancement
   classé `TRANSPORT_ERROR` conduit à la boucle de confirmation ; si la valeur
   courante est déjà conforme à la cible, le verdict est `applied` alors
   qu'**aucun processus n'a été lancé**. **Aucune barrière** dans la taxonomie
   active : c'est une perte d'information, pas une émission. Particulièrement
   atteignable en W4-C, où C5 §12.3 prescrit une réécriture à l'identique.
   Fermeture : arbitrage contractuel sur `CLIENT_UNAVAILABLE` (§11.5), **hors
   W4-A**. Voir §11.4.
4. **Effet d'une interruption locale sur une écriture en cours** — inconnue
   **I-13** : `subprocess.run(timeout=…)` termine l'enfant, et rien n'est établi
   sur la suite côté démon. Fermeture : W4-C, **ou maintien explicite de
   l'inconnue** (§19).
5. **`write_timeout_s` mal dimensionné** — C5 §9 avertit déjà qu'un budget de
   trois secondes peut être trop court en lecture. Fermeture : W4-C.
6. **Double écrivain** — aucune barrière dans Boilerack. Fermeture : W4-F.
7. **Relecture trompeuse** — I-7, I-8, I-11. Fermeture : W4-C.

---

## 25. Renvois

- **C3** — sémantique transactionnelle, `_PROVEN_NOT_EMITTED`, absence de
  retry : **inchangée**, consommée en §11 et §13.
- **C5** — §3, §9, §10, §11, §12 : consommés ; le protocole de caractérisation
  n'est pas réécrit.
- **C6** / `vclient_cli.py` — forme d'invocation, validation du nom, ordre de
  classification : repris comme précédent en §8 et §9.
- **W1**, **W2**, **W3** — non modifiés ; W2 §15.4 rappelé en §20.
- **C7 §14** et **I3** — signalés en §21, non tranchés.

---

## 26. Fermeture

W4-A contracte ce qu'un adaptateur d'écriture peut garantir **sans avoir jamais
vu une écriture** : une invocation unique, bornée, sans retry, sans revalidation
métier, sans conclusion physique — et une classification volontairement pauvre,
qui préfère l'imprécision à l'affirmation.

Trois statuts sont **temporairement interdits** — `OK`, `DAEMON_UNREACHABLE`,
`UNKNOWN_COMMAND` — parce que chacun repose sur une signature observée en lecture
seulement, et que deux d'entre eux court-circuitent la relecture. Les lever est
précisément l'objet de W4-C.

Ce que W4-A refuse de faire compte autant que ce qu'il décide : aucun nom de
commande, aucune borne, aucune valeur de délai qualifiée, aucune syntaxe
supposée, aucune détection de concurrent, aucune bascule.

**W4 reste fermé. Aucune écriture réelle n'est autorisée par ce document.**
