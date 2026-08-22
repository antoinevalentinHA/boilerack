# Contrat réel de `vclient` — observations de lecture

Document interne de conception. Il établit, sur preuves, ce que le client
`vclient` fait réellement en **lecture** sur l'installation de référence, afin
qu'un futur adaptateur de transport soit écrit contre des faits.

> **Ce document ne couvre pas l'écriture.** Aucune commande `set…` n'a été
> exécutée. Voir la section « Limite bloquante ».

## 1. Provenance et méthode

| | |
|---|---|
| Date de collecte | 2026-08-02, 16:08 à 16:17 CEST |
| Installation | poste de référence — Debian 13, aarch64, `vcontrold` en service continu |
| Régime | **lecture seule stricte** — aucune écriture, aucun redémarrage, aucune modification de service ou de configuration, aucun `sudo` |
| Sondes | 8, exécutées une par une, avec vérification de l'état du système entre chacune |
| Placement | entre deux cycles du superviseur local, pour écarter toute contention avec lui |
| Résultat | aucune anomalie ; processus du pont et du démon inchangés ; superviseur nominal sur toute la fenêtre |

Les captures conservent **séparément** `stdout`, `stderr`, le code retour, la
durée, la locale et la ligne de commande. Elles sont versionnées en
`tests/fixtures/vclient/`, encodées en base64 pour être insensibles à toute
normalisation de fin de ligne, et couvertes par
`tests/characterization/test_vclient_fixtures.py`.

Les neuf fixtures se répartissent en **deux recaptures verbatim** et **sept
transcriptions fidèles** du rapport de collecte. Cette distinction est
probante et protégée par des tests.

Les deux recaptures — `version` et `help` — ont été refaites verbatim après la
collecte initiale, l'aide faisant 1909 octets et sa restitution ayant été
repliée à l'affichage. Ce sont des sondes purement locales, sans contact avec
le démon. Les **sept** autres sont transcrites de la collecte. **La longueur en octets de
chacune correspond exactement à la valeur attestée par la capture**, ce que les
tests vérifient — mais les répertoires de capture ayant été supprimés en fin de
collecte, **aucune transcription n'est vérifiable contre un original**. La
concordance des longueurs est une corroboration forte, pas une preuve
indépendante.

## 2. Version observée

```
vclient version 0.98.12-5-g8ca4797
```

Forme `git describe` : cinq commits après l'étiquette `v0.98.12`, empreinte
`8ca4797`. Le binaire a donc été **compilé depuis un dépôt Git, non depuis une
archive de version publiée**.

**Tout ce document vaut pour cette version et cette installation.** Aucune
signature établie ici ne doit être présumée stable sur une autre version.

## 3. Le code retour ne discrimine rien

C'est le fait le plus structurant de la collecte.

| Situation | Code retour | Nature réelle |
|---|---|---|
| `-V` | **1** | résultat normal |
| `--help` | **1** | résultat normal |
| Lecture réussie | 0 | succès |
| **Commande inconnue** | **0** | **échec** |
| Démon injoignable | 1 | échec |
| Client absent | 127 | échec avant démarrage |

`0` recouvre à la fois un succès et un échec ; `1` recouvre à la fois un
résultat normal et un échec.

> **Règle normative.** Le verdict d'une opération reposera sur le **contenu
> structure** de la réponse, jamais sur le seul code retour.

## 4. Contrat de lecture établi

### 4.1 Forme texte

```
getTempKist:
28.000000 Grad Celsius
```

Deux lignes : le nom de la commande suivi de `:`, puis la valeur et son unité.
`stderr` vide. 36 octets, code retour 0.

### 4.2 Forme JSON longue — à privilégier

```json
[{"command":"getTempKist","value":28.000000,"raw":"28.000000 Grad Celsius","error":""}]
```

Tableau d'objets, un par commande — cohérent avec `-c cmd1,cmd2`.

| Champ | Succès | Échec |
|---|---|---|
| `command` | nom demandé | nom demandé |
| `value` | nombre | **`0.000000`** |
| `raw` | valeur **et unité** | message d'erreur |
| `error` | `""` | message d'erreur |

Trois conséquences de conception :

1. **`error` est le discriminant à utiliser** — c'est le seul champ qui ait
   distingue le succès de l'échec sur les deux cas observés. Aucune règle
   universelle couvrant *toutes* les erreurs n'est démontrée à ce stade.
2. **`value` vaut `0.0` en erreur** — valeur parfaitement plausible pour une
   température. Lire `value` sans vérifier `error` est un piège silencieux.
3. **`raw` porte l'unité**, ce que la forme texte oblige à extraire par
   analyse lexicale.

L'adaptateur privilégiera donc `-J`, en analysant `command`, `value`, `raw` et
`error`.

## 5. Cartographie sur l'énumération existante

`TransportStatus` existe déjà, en `src/boilerack/transport/vclient.py`, avec
**six** valeurs : `OK`, `DAEMON_UNREACHABLE`, `UNKNOWN_COMMAND`, `TIMEOUT`,
`UNUSABLE_OUTPUT`, `TRANSPORT_ERROR`.

Ce lot **ne la modifie pas**. Il lui adosse les signatures réellement
observées, et propose séparément une septième valeur en §6.

Le tableau ci-dessous rattache chaque signature collectée à une valeur
existante ; la ligne `CLIENT_UNAVAILABLE` est la seule qui ne corresponde à
aucune valeur actuelle.

| Statut | Signature | Preuve |
|---|---|---|
| `OK` | processus lancé · JSON valide · objet correspondant à la commande demandée · `error == ""` · `value` numérique finie · structure non ambiguë | `read_ok_json` |
| `UNKNOWN_COMMAND` | `error == "ERR: command unknown"` — **code retour 0** | `unknown_command_json`, `unknown_command_text` |
| `DAEMON_UNREACHABLE` | processus lancé · code retour 1 · `stdout` **et** `stderr` vides · échec immédiat | `daemon_unreachable` |
| `CLIENT_UNAVAILABLE` | le client n'a pas pu être lancé ; aucune commande n'a été remise au démon | `client_absent` — **valeur inexistante à ce jour**, proposée en §6 |
| `TIMEOUT` | budget externe du lanceur de processus épuisé | **non caractérisé — reporté délibérément** |
| `UNUSABLE_OUTPUT` | JSON invalide · structure inattendue · commande absente de la réponse · `error` vide mais valeur absente, non numérique ou non finie · réponse contradictoire | non observé |
| `TRANSPORT_ERROR` | toute autre erreur **après lancement** non identifiée avec certitude : erreur structurée autre que `command unknown`, sortie ou code retour incompatibles avec les signatures ci-dessus, communication interrompue, résultat ambigu | cas prudent par défaut |

Deux précautions inscrites au contrat :

- `UNKNOWN_COMMAND` ne se déduit **jamais** d'un code retour ni d'une erreur
  générique : seule la valeur exacte du champ `error` la caractérise.
- La signature de `DAEMON_UNREACHABLE` — deux flux vides — est **liée à la
  version caractérisée** et **ne doit pas absorber une erreur locale de
  lancement**, qui relève de `CLIENT_UNAVAILABLE`.

## 6. `CLIENT_UNAVAILABLE` — proposition et impact

### 6.1 Sémantique

> Le client local n'a pas pu être lancé ; **aucune commande n'a été remise au
> démon**.

Cas couverts au niveau du lanceur de processus : exécutable absent, permission
refusée, format exécutable invalide, tout autre échec système survenant avant
le démarrage du processus.

**Le signal existe déjà.** `ProcessResult`, en
`src/boilerack/adapters/process_runner.py`, distingue ces cas : toute `OSError`
levée au lancement — `FileNotFoundError`, `PermissionError` et apparentées —
produit `returncode is None` et renseigne `launch_error` avec le nom de la
classe d'exception. La condition d'un futur `CLIENT_UNAVAILABLE` s'écrit donc
sans invention : `launch_error != ""`.

Aucun consommateur n'est affecté aujourd'hui, l'adaptateur qui traduirait un
`ProcessResult` en `TransportStatus` n'existant pas encore.

> **Deux niveaux d'observation à ne pas confondre.**
>
> La sonde de l'exécutable absent a été lancée sous l'utilitaire GNU
> `timeout`. Ce qu'elle observe est donc le comportement de **`timeout`**, qui
> rend `127` et produit son propre message
> (`timeout: failed to run command … : No such file or directory`).
>
> **Elle ne prouve pas directement le comportement de `subprocess.run()`.** Ce
> cas est caractérisé **séparément en C4**, par les exceptions Python que
> `SubprocessRunner` intercepte : `FileNotFoundError`, `PermissionError` et
> autres `OSError`, qui produisent `returncode is None` et renseignent
> `launch_error`.
>
> La conclusion **commune aux deux niveaux**, et la seule qui soit établie,
> est : *le processus `vclient` n'a pas démarré et aucune commande n'a pu
> atteindre le démon.*

### 6.2 Distinction des voisins

| | Le client a démarré | Une commande a pu partir | Une écriture a pu atteindre la chaudière |
|---|---|---|---|
| `CLIENT_UNAVAILABLE` | **non** | non | **non** |
| `DAEMON_UNREACHABLE` | oui | non | **non** |
| `TRANSPORT_ERROR` | oui | **peut-être** | **peut-être** |
| `TIMEOUT` (après invocation d'écriture) | oui | oui | **peut-être** |

C'est cette colonne de droite, et elle seule, qui détermine le verdict d'une
commande.

### 6.3 Impact sur C3

Le cœur transactionnel traduit un résultat de transport en verdict. La
frontière retenue est celle de l'invocation de l'opération d'écriture :

| Statut | Verdict de commande | Raison | Classe |
|---|---|---|---|
| `CLIENT_UNAVAILABLE` | `rejected` | `bridge_unavailable` | transitoire |
| `DAEMON_UNREACHABLE` | `rejected` | `bridge_unavailable` | transitoire |
| `UNKNOWN_COMMAND` | `rejected` | **`unsupported_command`** | **permanent** — déjà ratifié en C3 |
| `UNUSABLE_OUTPUT` avant invocation | `rejected` | `bridge_unavailable` | transitoire |
| `TIMEOUT` **après** invocation d'écriture | `timeout` | — | — |
| `TRANSPORT_ERROR` **après** invocation d'écriture | `timeout` | — | — |

`CLIENT_UNAVAILABLE` et `DAEMON_UNREACHABLE` **prouvent qu'aucune écriture n'a
eu lieu** : ils autorisent un verdict `rejected`, plus informatif qu'un
`timeout`. C'est leur seul intérêt pratique, et il est réel.

> **Correction.** Une rédaction antérieure de ce tableau rattachait
> `UNKNOWN_COMMAND` à `bridge_unavailable` / transitoire. C'était faux à deux
> titres : une commande inconnue est une condition **permanente** — la rejouer
> donnera le même résultat — et la question était **déjà tranchée en C3**, où
> `unsupported_command` / `permanent` est ratifié et implémente
> (`docs/design/c3-transactional-core.md` §1.b). Le tableau ci-dessus reprend
> la décision existante ; il ne la rouvre pas.

**Portée du signal.** `UNKNOWN_COMMAND` repose strictement sur
`error == "ERR: command unknown"`, pour la version et l'installation
caractérisées. Cette classification n'est étendue **ni** à toute valeur
d'`error` non vide, **ni** à tout `raw` commençant par `ERR:`, **ni** à la
ligne `server error` observée sur `stderr`.

### 6.4 Impact sur les acquittements

Aucun changement du schéma d'ACK ni de la machine à quatre états. Le statut de
transport n'apparaît pas dans l'acquittement : il alimente la **raison** et le
diagnostic. Trois conséquences seulement :

- la distinction `vcontrold_status` / `optolink_status` devient calculable —
  `DAEMON_UNREACHABLE` donne `stopped`, tandis qu'un démon joignable dont la
  lecture échoue donne `running` + `disconnected` ;
- les causes du topic d'état de télémétrie se dérivent directement des
  statuts ;
- aucune raison de rejet nouvelle n'est requise.

### 6.5 Ce que ce lot ne fait pas

`TransportStatus` **n'est pas modifiée** : la septième valeur reste une
proposition en attente d'arbitrage. Aucun type, aucun adaptateur, aucun lanceur
de processus n'est créé ni modifié.

L'adaptateur `vclient` — qui traduira un `ProcessResult` en `ReadResult` ou
`WriteResult` — **n'existe pas encore**. Ce document en est l'entrée : il
fournit les signatures que cet adaptateur devra reconnaître, et rappelle en §11
celles qui lui manquent encore.

## 7. Locale

Pour **la seule commande `getTempKist`**, sur **cette version**
(`0.98.12-5-g8ca4797`) et **cette installation**, les sorties sous la locale
réelle du service (`LANG=en_GB.UTF-8`, `LC_ALL` non défini) et sous `LC_ALL=C`
sont **identiques octet pour octet**.

Rien n'est établi au-delà : ni pour les autres commandes, ni pour d'autres
locales, ni pour une autre version. En particulier, ce lot **n'affirme pas**
que `vclient` serait insensible à la locale en général, ni que `LC_ALL=C`
serait inutile partout.

L'adaptateur pourra néanmoins fixer un environnement déterministe par
précaution, mais le document doit indiquer que **cette précaution n'est pas
nécessaire à la lecture observée**. Corollaire : la substitution de virgule
décimale présente dans le pont historique est défensive et sans objet ici.

## 8. Défaut latent du pont historique

Constat historique, consigné pour ne pas être reproduit. **Aucune modification
de la production n'a été faite ni n'est proposée.**

Le pont historique fusionne `stdout` et `stderr`, puis filtre les lignes
commençant par `ERR`. Or le message réel commence par `SRV `. Combiné à un code
retour nul — qui empêche la levée d'exception — une commande inconnue produit
la chaîne **`SRV`** en guise de valeur.

Conséquences : `SRV` publié comme valeur de télémétrie, et surtout une **santé
rendue faussement nominale**, la valeur n'étant pas nulle.

Nuance importante : sur les chemins **numériques**, la dégradation reste
prudente — `float("SRV")` échoue et la valeur devient `None`. Le défaut ne se
manifeste donc que sur les chemins qui consomment la chaîne telle quelle :
publication de télémétrie et dérivation de la santé.

**Le défaut est latent** : le jeu de commandes est figé et les définitions sont
intactes. Il deviendrait actif si la configuration des commandes divergeait.
Il est démontré sur la capture réelle par
`test_le_filtre_historique_rend_SRV_sur_une_commande_inconnue`.

> **Portée du constat.** Le code du pont historique démontre **son propre
> comportement**, non le contrat général de `vclient`. Ce qui est établi ici,
> c'est la rencontre entre une sortie réelle du client et un filtre particulier
> — pas une propriété du client.

## 9. Contention et durées

| Opération | Durée observée |
|---|---|
| Erreur avant connexion — port fermé, client absent | **~10 ms** |
| Rejet local d'une commande inconnue | **~111 ms** |
| **Lecture Optolink réelle**, production active | **2 669 à 4 029 ms** |

Deux ordres de grandeur séparent un rejet local d'une transaction réelle : la
durée est un signal exploitable, jamais un verdict.

> **Aucun budget de production n'est arrêté dans ce lot.** Les mesures
> démontrent seulement qu'un budget de trois secondes **peut être trop court
> sous contention**. Le dimensionnement relève d'un arbitrage ultérieur,
> appuyé sur des mesures dédiées.

## 10. Faits établis et inconnues

### Établi

| # | Fait |
|---|---|
| 1 | Version `0.98.12-5-g8ca4797`, compilée depuis un dépôt Git |
| 2 | `-V` et `--help` rendent un code retour `1` avec sortie sur `stdout` |
| 3 | Une lecture réussie rend `0`, deux lignes sur `stdout`, `stderr` vide |
| 4 | L'aide **déclare** `-j`, `-J`, `-4`, `-6`, `--help` ; seul **`-J` a été exercé** |
| 5 | La forme JSON longue est un tableau d'objets à quatre champs |
| 6 | `error == ""` **observé sur la lecture réussie** ; `error == "ERR: command unknown"` **observé sur la commande inexistante**. Aucune règle universelle couvrant toutes les erreurs n'est démontrée |
| 7 | En erreur, `value` vaut `0.000000` |
| 8 | Une commande inconnue rend `0`, message `SRV ERR: command unknown` sur `stderr` |
| 9 | Une commande inconnue est rejetée localement, sans transaction Optolink |
| 10 | Un démon injoignable rend `1` avec les deux flux vides |
| 11 | Pour `getTempKist`, sur cette version et cette installation, la sortie est identique entre `en_GB.UTF-8` et `LC_ALL=C` |
| 12 | Une lecture réelle coûte 2,7 à 4,0 s pour un client tiers, production active |

### Inconnu

| # | Inconnue | Conséquence |
|---|---|---|
| 1 | **Comportement d'une écriture `set…`** — code retour, forme texte, forme JSON, signal de succès | **bloquant** — voir §11 |
| 2 | Comportement d'expiration réelle du client | reporté délibérément ; sera caractérisé par doubles de test |
| 3 | Forme d'une réponse à plusieurs commandes (`-c a,b,c`) | la structure en tableau la suggère, non vérifiée |
| 4 | Forme `-j` (JSON court) | non collectée |
| 5 | Comportement en cas d'erreur Optolink réelle — chaudière muette, liaison coupée | non provoquable sans risque |
| 6 | Signature d'une valeur hors domaine rendue par le démon | non observée |
| 7 | Stabilité des signatures sur une autre version de `vclient` | inconnue par construction |
| 8 | Comportement en cas de permission refusée sur le binaire | non testé — sous-cas de `CLIENT_UNAVAILABLE` |

## 11. Limite bloquante — l'écriture n'est pas caractérisée

Le comportement réel d'une commande `set…` **n'a pas été observé**. En
conséquence, ce lot **ne permet pas** :

- d'implémenter le chemin d'écriture de l'adaptateur ;
- de décider ce qui constitue un succès local d'écriture ;
- d'établir la forme JSON d'une réponse d'écriture ;
- de finaliser la cartographie des résultats d'écriture.

Toute affirmation sur l'écriture serait une extrapolation depuis la lecture.
Elle n'a pas sa place ici.

## 12. Protocole minimal pour une caractérisation ultérieure d'écriture

**Présenté pour mémoire. Non exécuté. Non demandé.** Une écriture, même
identique à la valeur courante, reste une écriture : elle relève d'un chantier
séparé, avec plan d'action préalable et autorisation explicite.

Éléments qu'un tel protocole devrait comporter :

1. **Fenêtre** — hors saison de chauffe, en présence de l'exploitant.
2. **Datapoint** — le moins conséquent du profil, sur un paramètre dont une
   variation transitoire serait sans effet ressenti.
3. **Séquence** — lire la valeur courante ; la réécrire à l'identique ; relire ;
   vérifier l'invariance. Une seule fois, sans répétition automatique.
4. **Capture** — code retour, `stdout`, `stderr`, durée, formes texte **et**
   JSON, chacune séparément.
5. **Retour arrière armé** — la valeur d'origine relevée avant toute action, et
   la procédure de restauration écrite avant de commencer.
6. **Critères d'abandon** — toute divergence de la valeur relue, tout échec du
   superviseur local, tout changement d'état des services.
7. **Coordination** — le superviseur local sonde périodiquement avec un budget
   contraint ; la fenêtre doit être choisie entre deux cycles.
8. **Alternative à étudier d'abord** — une instance de démon dédiée, hors
   production, adossée à un simulateur de liaison. Elle supprimerait le risque,
   au prix d'un travail de simulation qui n'existe pas aujourd'hui.

Aucun de ces éléments ne constitue une demande.

### 12.9 Disposition du n° 8 — alternative étudiée, puis écartée

*Note ajoutée après coup. Elle ne modifie aucun des huit éléments ci-dessus :
elle consigne l'issue de l'étude que le n° 8 réclamait.*

L'alternative a été étudiée par le lot **W4-C**, qui instancie ce protocole.
Verdict : **écartée**.

Un démon dédié adossé à un simulateur de liaison ne dispose ni d'une vraie
liaison Optolink, ni d'une vraie chaudière. Il ne peut donc **pas** produire les
signatures réelles d'une écriture acceptée — code retour, forme de `stdout`,
forme de `stderr`, durée — qui sont exactement ce que la caractérisation doit
mesurer. Le simulateur **fabriquerait les faits recherchés** : il rendrait ce
qu'on lui aurait fait rendre, et l'on prendrait pour une observation ce qui
serait une hypothèse écrite deux fois.

La proposition n'était pas absurde, et elle devait être étudiée : elle supprime
effectivement le risque opératoire. Mais elle le supprime **en supprimant aussi
l'objet de la mesure**, ce qui la rend inapte à cette fin précise.

Par ailleurs, le besoin auquel un tel banc répondrait par ailleurs — éprouver la
mécanique hors terrain — est **déjà couvert** : le dépôt dispose de doubles et de
fixtures de caractérisation, et c'est sur eux que reposent les lots hors terrain.

> **Conséquence.** L'alternative est écartée pour cette fin. Une caractérisation
> **terrain** reste donc nécessaire, et c'est le rôle de W4-C. Rien d'autre dans
> §12 n'est modifié.
