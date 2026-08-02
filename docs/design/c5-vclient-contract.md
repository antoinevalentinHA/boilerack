# Contrat reel de `vclient` — observations de lecture

Document interne de conception. Il etablit, sur preuves, ce que le client
`vclient` fait reellement en **lecture** sur l'installation de reference, afin
qu'un futur adaptateur de transport soit ecrit contre des faits.

> **Ce document ne couvre pas l'ecriture.** Aucune commande `set…` n'a ete
> executee. Voir la section « Limite bloquante ».

## 1. Provenance et methode

| | |
|---|---|
| Date de collecte | 2026-08-02, 16:08 a 16:17 CEST |
| Installation | poste de reference — Debian 13, aarch64, `vcontrold` en service continu |
| Regime | **lecture seule stricte** — aucune ecriture, aucun redemarrage, aucune modification de service ou de configuration, aucun `sudo` |
| Sondes | 8, executees une par une, avec verification de l'etat du systeme entre chacune |
| Placement | entre deux cycles du superviseur local, pour ecarter toute contention avec lui |
| Resultat | aucune anomalie ; processus du pont et du demon inchanges ; superviseur nominal sur toute la fenetre |

Les captures conservent **separement** `stdout`, `stderr`, le code retour, la
duree, la locale et la ligne de commande. Elles sont versionnees en
`tests/fixtures/vclient/`, encodees en base64 pour etre insensibles a toute
normalisation de fin de ligne, et couvertes par
`tests/characterization/test_vclient_fixtures.py`.

Deux fixtures — `version` et `help` — ont ete **recapturees verbatim** apres la
collecte initiale, l'aide faisant 1909 octets et sa restitution ayant ete
repliee a l'affichage. Ce sont des sondes purement locales, sans contact avec
le demon. Les six autres sont transcrites de la collecte ; **la longueur en
octets de chacune correspond exactement a la valeur attestee par la capture**,
ce que les tests verifient.

## 2. Version observee

```
vclient version 0.98.12-5-g8ca4797
```

Forme `git describe` : cinq commits apres l'etiquette `v0.98.12`, empreinte
`8ca4797`. Le binaire a donc ete **compile depuis un depot Git, non depuis une
archive de version publiee**.

**Tout ce document vaut pour cette version et cette installation.** Aucune
signature etablie ici ne doit etre presumee stable sur une autre version.

## 3. Le code retour ne discrimine rien

C'est le fait le plus structurant de la collecte.

| Situation | Code retour | Nature reelle |
|---|---|---|
| `-V` | **1** | resultat normal |
| `--help` | **1** | resultat normal |
| Lecture reussie | 0 | succes |
| **Commande inconnue** | **0** | **echec** |
| Demon injoignable | 1 | echec |
| Client absent | 127 | echec avant demarrage |

`0` recouvre a la fois un succes et un echec ; `1` recouvre a la fois un
resultat normal et un echec.

> **Regle normative.** Le verdict d'une operation reposera sur le **contenu
> structure** de la reponse, jamais sur le seul code retour.

## 4. Contrat de lecture etabli

### 4.1 Forme texte

```
getTempKist:
28.000000 Grad Celsius
```

Deux lignes : le nom de la commande suivi de `:`, puis la valeur et son unite.
`stderr` vide. 36 octets, code retour 0.

### 4.2 Forme JSON longue — a privilegier

```json
[{"command":"getTempKist","value":28.000000,"raw":"28.000000 Grad Celsius","error":""}]
```

Tableau d'objets, un par commande — coherent avec `-c cmd1,cmd2`.

| Champ | Succes | Echec |
|---|---|---|
| `command` | nom demande | nom demande |
| `value` | nombre | **`0.000000`** |
| `raw` | valeur **et unite** | message d'erreur |
| `error` | `""` | message d'erreur |

Trois consequences de conception :

1. **`error` est le seul discriminant fiable.**
2. **`value` vaut `0.0` en erreur** — valeur parfaitement plausible pour une
   temperature. Lire `value` sans verifier `error` est un piege silencieux.
3. **`raw` porte l'unite**, ce que la forme texte oblige a extraire par
   analyse lexicale.

L'adaptateur privilegiera donc `-J`, en analysant `command`, `value`, `raw` et
`error`.

## 5. Cartographie des statuts de transport

**Proposition documentaire.** Aucun type ni enumeration n'est cree dans ce
lot. Les noms sont ceux du vocabulaire normatif retenu.

| Statut | Signature | Preuve |
|---|---|---|
| `OK` | processus lance · JSON valide · objet correspondant a la commande demandee · `error == ""` · `value` numerique finie · structure non ambigue | `read_ok_json` |
| `UNKNOWN_COMMAND` | `error == "ERR: command unknown"` — **code retour 0** | `unknown_command_json`, `unknown_command_text` |
| `DAEMON_UNREACHABLE` | processus lance · code retour 1 · `stdout` **et** `stderr` vides · echec immediat | `daemon_unreachable` |
| `CLIENT_UNAVAILABLE` | le client n'a pas pu etre lance ; aucune commande n'a ete remise au demon | `client_absent` |
| `TIMEOUT` | budget externe du lanceur de processus epuise | **non caracterise — reporte deliberement** |
| `UNUSABLE_OUTPUT` | JSON invalide · structure inattendue · commande absente de la reponse · `error` vide mais valeur absente, non numerique ou non finie · reponse contradictoire | non observe |
| `TRANSPORT_ERROR` | toute autre erreur **apres lancement** non identifiee avec certitude : erreur structuree autre que `command unknown`, sortie ou code retour incompatibles avec les signatures ci-dessus, communication interrompue, resultat ambigu | cas prudent par defaut |

Deux precautions inscrites au contrat :

- `UNKNOWN_COMMAND` ne se deduit **jamais** d'un code retour ni d'une erreur
  generique : seule la valeur exacte du champ `error` la caracterise.
- La signature de `DAEMON_UNREACHABLE` — deux flux vides — est **liee a la
  version caracterisee** et **ne doit pas absorber une erreur locale de
  lancement**, qui releve de `CLIENT_UNAVAILABLE`.

## 6. `CLIENT_UNAVAILABLE` — proposition et impact

### 6.1 Semantique

> Le client local n'a pas pu etre lance ; **aucune commande n'a ete remise au
> demon**.

Cas couverts au niveau du lanceur de processus : executable absent, permission
refusee, format executable invalide, tout autre echec systeme survenant avant
le demarrage du processus.

### 6.2 Distinction des voisins

| | Le client a demarre | Une commande a pu partir | Une ecriture a pu atteindre la chaudiere |
|---|---|---|---|
| `CLIENT_UNAVAILABLE` | **non** | non | **non** |
| `DAEMON_UNREACHABLE` | oui | non | **non** |
| `TRANSPORT_ERROR` | oui | **peut-etre** | **peut-etre** |
| `TIMEOUT` (apres invocation d'ecriture) | oui | oui | **peut-etre** |

C'est cette colonne de droite, et elle seule, qui determine le verdict d'une
commande.

### 6.3 Impact sur C3

Le coeur transactionnel traduit un resultat de transport en verdict. La
frontiere retenue est celle de l'invocation de l'operation d'ecriture :

| Statut | Verdict de commande | Raison | Classe |
|---|---|---|---|
| `CLIENT_UNAVAILABLE` | `rejected` | `bridge_unavailable` | transitoire |
| `DAEMON_UNREACHABLE` | `rejected` | `bridge_unavailable` | transitoire |
| `UNKNOWN_COMMAND` | `rejected` | `bridge_unavailable` | transitoire — signale une **incoherence de profil**, a journaliser comme telle |
| `UNUSABLE_OUTPUT` avant invocation | `rejected` | `bridge_unavailable` | transitoire |
| `TIMEOUT` **apres** invocation d'ecriture | `timeout` | — | — |
| `TRANSPORT_ERROR` **apres** invocation d'ecriture | `timeout` | — | — |

`CLIENT_UNAVAILABLE` et `DAEMON_UNREACHABLE` **prouvent qu'aucune ecriture n'a
eu lieu** : ils autorisent un verdict `rejected`, plus informatif qu'un
`timeout`. C'est leur seul interet pratique, et il est reel.

### 6.4 Impact sur les acquittements

Aucun changement du schema d'ACK ni de la machine a quatre etats. Le statut de
transport n'apparait pas dans l'acquittement : il alimente la **raison** et le
diagnostic. Trois consequences seulement :

- la distinction `vcontrold_status` / `optolink_status` devient calculable —
  `DAEMON_UNREACHABLE` donne `stopped`, tandis qu'un demon joignable dont la
  lecture echoue donne `running` + `disconnected` ;
- les causes du topic d'etat de telemetrie se derivent directement des
  statuts ;
- aucune raison de rejet nouvelle n'est requise.

### 6.5 Ce que ce lot ne fait pas

Aucune enumeration, aucun type, aucun adaptateur, aucun lanceur de processus
n'est cree ou modifie ici. La proposition ci-dessus attend un arbitrage.

## 7. Locale

Les sorties sous la locale reelle du service et sous `LC_ALL=C` sont
**identiques octet pour octet**.

L'adaptateur pourra neanmoins fixer un environnement deterministe par
precaution, mais le document doit indiquer que **cette precaution n'est pas
necessaire a la lecture observee**. Corollaire : la substitution de virgule
decimale presente dans le pont historique est defensive et sans objet ici.

## 8. Defaut latent du pont historique

Constat historique, consigne pour ne pas etre reproduit. **Aucune modification
de la production n'a ete faite ni n'est proposee.**

Le pont historique fusionne `stdout` et `stderr`, puis filtre les lignes
commencant par `ERR`. Or le message reel commence par `SRV `. Combine a un code
retour nul — qui empeche la levee d'exception — une commande inconnue produit
la chaine **`SRV`** en guise de valeur.

Consequences : `SRV` publie comme valeur de telemetrie, et surtout une **sante
rendue faussement nominale**, la valeur n'etant pas nulle.

**Le defaut est latent** : le jeu de commandes est fige et les definitions sont
intactes. Il deviendrait actif si la configuration des commandes divergeait.
Il est demontre sur la capture reelle par
`test_le_filtre_historique_rend_SRV_sur_une_commande_inconnue`.

## 9. Contention et durees

| Operation | Duree observee |
|---|---|
| Erreur avant connexion — port ferme, client absent | **~10 ms** |
| Rejet local d'une commande inconnue | **~111 ms** |
| **Lecture Optolink reelle**, production active | **2 669 a 4 029 ms** |

Deux ordres de grandeur separent un rejet local d'une transaction reelle : la
duree est un signal exploitable, jamais un verdict.

> **Aucun budget de production n'est arrete dans ce lot.** Les mesures
> demontrent seulement qu'un budget de trois secondes **peut etre trop court
> sous contention**. Le dimensionnement releve d'un arbitrage ulterieur,
> appuye sur des mesures dediees.

## 10. Faits etablis et inconnues

### Etabli

| # | Fait |
|---|---|
| 1 | Version `0.98.12-5-g8ca4797`, compilee depuis un depot Git |
| 2 | `-V` et `--help` rendent un code retour `1` avec sortie sur `stdout` |
| 3 | Une lecture reussie rend `0`, deux lignes sur `stdout`, `stderr` vide |
| 4 | `-j` et `-J` sont supportes ; `-4`, `-6`, `--help` egalement |
| 5 | La forme JSON longue est un tableau d'objets a quatre champs |
| 6 | `error == ""` marque le succes ; une valeur non vide marque l'echec |
| 7 | En erreur, `value` vaut `0.000000` |
| 8 | Une commande inconnue rend `0`, message `SRV ERR: command unknown` sur `stderr` |
| 9 | Une commande inconnue est rejetee localement, sans transaction Optolink |
| 10 | Un demon injoignable rend `1` avec les deux flux vides |
| 11 | La sortie est insensible a la locale |
| 12 | Une lecture reelle coute 2,7 a 4,0 s pour un client tiers, production active |

### Inconnu

| # | Inconnue | Consequence |
|---|---|---|
| 1 | **Comportement d'une ecriture `set…`** — code retour, forme texte, forme JSON, signal de succes | **bloquant** — voir §11 |
| 2 | Comportement d'expiration reelle du client | reporte deliberement ; sera caracterise par doubles de test |
| 3 | Forme d'une reponse a plusieurs commandes (`-c a,b,c`) | la structure en tableau la suggere, non verifiee |
| 4 | Forme `-j` (JSON court) | non collectee |
| 5 | Comportement en cas d'erreur Optolink reelle — chaudiere muette, liaison coupee | non provoquable sans risque |
| 6 | Signature d'une valeur hors domaine rendue par le demon | non observee |
| 7 | Stabilite des signatures sur une autre version de `vclient` | inconnue par construction |
| 8 | Comportement en cas de permission refusee sur le binaire | non teste — sous-cas de `CLIENT_UNAVAILABLE` |

## 11. Limite bloquante — l'ecriture n'est pas caracterisee

Le comportement reel d'une commande `set…` **n'a pas ete observe**. En
consequence, ce lot **ne permet pas** :

- d'implementer le chemin d'ecriture de l'adaptateur ;
- de decider ce qui constitue un succes local d'ecriture ;
- d'etablir la forme JSON d'une reponse d'ecriture ;
- de finaliser la cartographie des resultats d'ecriture.

Toute affirmation sur l'ecriture serait une extrapolation depuis la lecture.
Elle n'a pas sa place ici.

## 12. Protocole minimal pour une caracterisation ulterieure d'ecriture

**Presente pour memoire. Non execute. Non demande.** Une ecriture, meme
identique a la valeur courante, reste une ecriture : elle releve d'un chantier
separe, avec plan d'action prealable et autorisation explicite.

Elements qu'un tel protocole devrait comporter :

1. **Fenetre** — hors saison de chauffe, en presence de l'exploitant.
2. **Datapoint** — le moins consequent du profil, sur un parametre dont une
   variation transitoire serait sans effet ressenti.
3. **Sequence** — lire la valeur courante ; la reecrire a l'identique ; relire ;
   verifier l'invariance. Une seule fois, sans repetition automatique.
4. **Capture** — code retour, `stdout`, `stderr`, duree, formes texte **et**
   JSON, chacune separement.
5. **Retour arriere arme** — la valeur d'origine relevee avant toute action, et
   la procedure de restauration ecrite avant de commencer.
6. **Criteres d'abandon** — toute divergence de la valeur relue, tout echec du
   superviseur local, tout changement d'etat des services.
7. **Coordination** — le superviseur local sonde periodiquement avec un budget
   contraint ; la fenetre doit etre choisie entre deux cycles.
8. **Alternative a etudier d'abord** — une instance de demon dediee, hors
   production, adossee a un simulateur de liaison. Elle supprimerait le risque,
   au prix d'un travail de simulation qui n'existe pas aujourd'hui.

Aucun de ces elements ne constitue une demande.
