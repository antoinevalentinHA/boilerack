# C12 — Contrat d'exploitation et de service

Document normatif. Il fixe la **surface d'exploitation** de Boilerack : ou vivent
le code, la configuration et le secret, sous quelle identite le pont tourne, quel
superviseur le demarre et l'arrete, et ce qu'un superviseur doit conclure de
chaque code de sortie.

C12 ne modifie **aucun comportement du programme**. Il ne redefinit ni les codes
de sortie (C10), ni les signaux (C9), ni la reconnexion (C11), ni la
configuration (C10). Il decrit ce que ces lots rendent deja possible, et le rend
opposable.

---

## 1. Objet

Boilerack est aujourd'hui un programme installable et lancable a la main. Il
n'est pas un **service**. Rien dans le depot ne dit ou sa configuration doit
vivre, sous quelle identite il doit tourner, ni ce qu'un superviseur doit faire
quand il s'arrete.

C11 §14 a explicitement renvoye ici la question restee ouverte :

> « Comportement existant conserve, **susceptible d'etre reconsidere lors du
> futur chantier d'exploitation et de service**, ou la question du redemarrage se
> posera reellement. »

C12 repond a cette question, et seulement a elle.

**C12 ne pretend pas que Boilerack est installe, ni qualifie sur le terrain.**
Aucune unite n'est activee, aucun `systemctl` n'est execute, aucune machine cible
n'est touchee. Ce qui est produit est un **contrat** et un **gabarit versionne**,
valides hors ligne.

---

## 2. Autorites et acquis

Ce que C12 **reprend sans le redefinir**, verifie dans le depot :

| # | Acquis | Origine | Preuve |
|---|---|---|---|
| A1 | Le paquet se construit et s'installe, et l'installation cree la commande `boilerack` | C10, `pyproject.toml` | installation mesuree dans un environnement jetable : code retour `0`, script present |
| A2 | La commande installee fonctionne : `--help` rend `0`, sans argument rend `2`, configuration absente rend `2` avec un message et sans trace | C10 | mesure directe sur l'installation jetable |
| A3 | Une seule dependance d'execution : `paho-mqtt` | C4 | `pip list` sur l'installation jetable |
| A4 | `--config` est **obligatoire** et **aucun emplacement par defaut n'est cherche** | C10 | contrat C10 et code du chargeur |
| A5 | Un seul secret, une seule variable : `BOILERACK_MQTT_PASSWORD` | C10 | unique lecture d'environnement de tout `src/` |
| A6 | La journalisation va sur **stderr**, horodatee, niveau reglable | C10 | `logging.basicConfig(stream=sys.stderr, ...)` |
| A7 | `SIGTERM` conduit a un arret propre et au resultat `0` ; `SIGINT` a `130` | C9 | contrat C9 |
| A8 | Codes de sortie : `0` arret propre · `130` interruption · `2` usage ou configuration · `1` panne avec trace | C10 | contrat C10 |
| A9 | Le pont **survit** a une perte MQTT et republie sa presence a la reconnexion | C11 | contrat C11 |
| A10 | **Aucune ecriture disque metier** : la seule ouverture de fichier de `src/` est la LECTURE du TOML | — | inspection du code |
| A11 | **Aucune dependance au repertoire courant** : ni `getcwd`, ni `chdir`, ni chemin relatif | — | inspection du code |

Ces acquis sont des **entrees** de C12. Les contredire serait une regression, pas
une decision d'exploitation.

---

## 3. Hors perimetre — liste fermee

Installation reelle sur une machine cible ou un Raspberry Pi · `systemctl` reel ·
activation d'un service · `systemd-analyze` sur la cible · deploiement reel ·
script d'installation · script de mise a jour · rollback · mise a jour
automatique · Docker · paquet Debian · `pipx` · release publique · changement de
version · changement du classifieur de maturite · broker MQTT reel · `vclient`
reel · `vcontrold` reel · chaudiere · Home Assistant · MQTT Discovery · commandes
MQTT · ACK · ecriture chaudiere · nouveaux datapoints · supervision externe ·
gestionnaire de secrets · modification de C9, C10 ou C11 · traitement des
reserves non bloquantes de C11 · chantier d'accentuation.

**En particulier, C12 ne livre pas l'installateur** qui cree l'environnement
decrit en §4. Il en fixe la cible ; le produire est un chantier distinct.

---

## 4. Modele d'exploitation

### 4.1 Emplacements

| Role | Chemin | Proprietaire | Mode indicatif |
|---|---|---|---|
| Code installe | `/opt/boilerack/venv` | `root` | lecture pour tous |
| Commande | `/opt/boilerack/venv/bin/boilerack` | `root` | executable |
| Configuration | `/etc/boilerack/boilerack.toml` | `root:boilerack` | `0640` |
| Secret | `/etc/boilerack/boilerack.env` | `root:boilerack` | `0640` |

**Un environnement virtuel dedie**, et non une installation systeme : Boilerack
n'a qu'une dependance d'execution, et l'isoler evite tout conflit avec le Python
de la distribution. `ExecStart` vise directement le script du venv, ce qui rend
l'interpreteur utilise explicite et verifiable.

**Ces chemins appartiennent a l'exploitation, jamais au code.** Le chargeur de
configuration continue de ne chercher aucun emplacement par defaut (A4) : c'est
l'unite qui passe le chemin, explicitement.

Ce point n'est pas une precaution de style. C10 §`--config` ecrit :

> « **Aucun chemin implicite n'est introduit** : ni `/etc/boilerack.toml`, ni
> `~/.config/...`, ni le repertoire courant. Boilerack ne cherche pas sa
> configuration, il la recoit. »

C10 nomme donc **explicitement** un chemin sous `/etc` parmi ceux qui ne sont pas
cherches. La convention de §4.1 ne le contredit pas : elle designe ou l'exploitant
**place** le fichier, et l'unite le **transmet**. Inscrire ce chemin dans le
programme contredirait C10 et rendrait le comportement dependant du compte et du
repertoire de lancement.

### 4.2 Identite du service

Boilerack tourne sous un utilisateur **dedie et non privilegie**, par convention
nomme `boilerack`, membre du groupe `boilerack`.

Justification par ce que le programme fait reellement :

- il **n'ecrit rien** sur le disque (A10) — aucun repertoire d'etat n'est requis ;
- il **ne depend pas du repertoire courant** (A11) — aucun `WorkingDirectory` n'est necessaire ;
- il **lit** un fichier de configuration et un fichier d'environnement ;
- il ouvre une **socket sortante** vers le broker et **lance un sous-processus**
  `vclient`.

Aucun de ces besoins n'exige de privilege. **`root` est donc interdit.**

### 4.3 Aucun etat persistant

Boilerack ne conserve rien entre deux executions : ni cache, ni base, ni fichier
de reprise. L'etat de lecture vit en memoire et meurt avec le processus ;
l'instantane et la presence vivent **chez le broker**, en messages retenus.

Consequence contractuelle : **aucun `StateDirectory`, aucun `CacheDirectory`,
aucun `RuntimeDirectory` n'est requis**. Une unite qui en declarerait un
promettrait un besoin qui n'existe pas.

---

## 5. Commande du service

Forme normative de la commande de demarrage :

```text
/opt/boilerack/venv/bin/boilerack --config /etc/boilerack/boilerack.toml
```

Trois exigences, chacune pour une raison distincte :

1. **Le script installe**, pas `python -m boilerack`. Les deux chemins sont
   equivalents (C10), mais l'unite doit exercer l'artefact que l'installation
   produit — celui-la meme qu'un exploitant invoquera. `python -m` exigerait en
   outre de nommer un interpreteur et de maitriser le repertoire courant, alors
   que le script du venv porte deja son interpreteur.
2. **Un chemin absolu**, puisque le service ne dispose d'aucun `PATH` utile.
3. **`--config` explicite**, puisque le programme n'en cherche aucun (A4).
   L'omettre ferait echouer le demarrage avec le code `2`.

`--log-level` n'est pas contracte dans la commande : son defaut `INFO` convient a
un service, et le rendre obligatoire figerait une politique que l'exploitant doit
pouvoir changer.

---

## 6. Configuration et secret

**Deux fichiers, deux natures.**

`/etc/boilerack/boilerack.toml` porte toute la configuration durable — 13 cles,
aucune secrete (C10). Il est **versionnable** par l'exploitant.

`/etc/boilerack/boilerack.env` porte l'unique secret, sous la forme deja
contractee :

```text
BOILERACK_MQTT_PASSWORD=...
```

Il est charge par `EnvironmentFile=`, ce qui laisse l'unite **versionnable sans
secret**.

### Forme STRICTE, sans prefixe

```text
EnvironmentFile=/etc/boilerack/boilerack.env
```

La forme tolerante — `EnvironmentFile=-/etc/...`, qui fait ignorer un fichier
manquant — est **REJETEE**. Avec elle, un chemin errone ou un fichier supprime
ferait disparaitre le secret **en silence** : le pont tenterait alors une
connexion sans mot de passe, et l'exploitant ne l'apprendrait qu'au refus du
broker, voire jamais. La forme stricte transforme cette faute en **echec de
demarrage immediat et lisible**, ce qui est la doctrine constante du projet.

### VARIABLE optionnelle, FICHIER obligatoire — la distinction

Ces deux propositions ne se contredisent pas, et il faut les tenir ensemble :

| Niveau | Regle | Autorite |
|---|---|---|
| **Programme** | `BOILERACK_MQTT_PASSWORD` est **optionnelle** : absente, le chargement reussit et le mot de passe vaut `None` | C10, **inchange** |
| **Exploitation** | `/etc/boilerack/boilerack.env` est **attendu par l'unite** : absent, le service ne demarre pas | C12 |

Consequence pratique, a documenter pour l'exploitant : une installation **sans
authentification MQTT** cree tout de meme ce fichier, **eventuellement vide**. Le
fichier peut donc exister sans definir la variable — C10 n'est ni durci, ni
contredit : C12 ne parle que du fichier, C10 ne parle que de la variable.

Clauses normatives :

- **le fichier d'unite versionne ne contient AUCUN secret**, ni reel, ni factice,
  ni exemple ressemblant a un secret. Un faux mot de passe versionne finit par
  etre copie ;
- le fichier d'environnement n'est **pas** versionne dans ce depot ;
- ses permissions restreignent la lecture au service et a l'administrateur ;
- aucune autre variable d'environnement n'est requise : le programme n'en lit
  qu'une (A5).

`Environment=` inline est **rejete** : il inscrirait le mot de passe dans un
fichier d'unite lisible par tous.

---

## 7. Signaux et codes de sortie

C12 **ne redefinit rien** ; il fixe ce qu'un superviseur doit en conclure.

| Code | Origine | Sens | Attendu du superviseur |
|---|---|---|---|
| `0` | C9/C10 | arret propre, notamment sur `SIGTERM` | **succes** — aucun redemarrage |
| `130` | C9/C10 | interruption (`SIGINT`) | **aucun redemarrage**, et **aucune requalification en succes** : l'interruption reste un echec visible (§8.1) |
| `2` | C10 | usage ou configuration invalide | **echec permanent** — aucun redemarrage (§8) |
| `1` | C10 | panne, avec trace | **echec transitoire possible** — redemarrage (§8) |

`SIGTERM` est le signal d'arret de `systemctl stop`, et C9 en fait un arret
propre rendant `0`. La correspondance est donc **native**, sans adaptation.

**`KillSignal=SIGTERM` est contracte explicitement**, bien que ce soit deja le
defaut de systemd. Tout le cycle de vie C9 repose sur ce signal : s'en remettre a
un defaut que rien n'oblige a rester stable reviendrait a fonder une garantie sur
une hypothese non ecrite.

---

## 8. Politique de redemarrage

### 8.1 Regle

```text
Restart=on-failure
RestartPreventExitStatus=2 130
```

`on-failure` plutot que `always` : un arret propre (`0`) est un arret **voulu**,
et le relancer contrarierait `systemctl stop`.

**Le code `2` est soustrait au redemarrage.** Sans cela, un TOML invalide
produirait une boucle : echec immediat, redemarrage, echec immediat. L'exploitant
verrait un service qui s'agite au lieu d'un service **arrete et visible**, avec sa
cause dans le journal. C'est l'objectif normatif : **une erreur de configuration
reste arretee et lisible ; elle ne boucle jamais.**

**Le code `130` l'est aussi.** Sous `Restart=on-failure`, un `130` serait sinon
relance : une interruption **demandee** deviendrait un redemarrage subi. Ce code
ne peut naitre d'aucune action de systemd lui-meme — `systemctl stop` envoie
`SIGTERM` (§7), et un service n'a pas de terminal —, mais il reste atteignable
par une action deliberee d'administrateur, typiquement
`systemctl kill --signal=SIGINT`. La clause couvre ce cas plutot que de s'en
remettre a son improbabilite.

**`SuccessExitStatus=130` est REJETE.** Ce serait l'autre facon d'empecher le
redemarrage, et elle est refusee : elle requalifierait l'interruption en
**succes**, alors que C9 a choisi `130` precisement pour dire **qui** a demande
l'arret. La distinction serait effacee au niveau du superviseur, et l'unite
paraitrait s'etre arretee normalement.

Consequence assumee, a connaitre : apres un `SIGINT` administratif explicite,
l'unite reste en etat d'**echec** — visible dans `systemctl status` — sans etre
relancee. C'est le comportement voulu : **absence de redemarrage automatique
ET visibilite de l'interruption**, plutot qu'une requalification de confort.

Le chemin normal d'arret reste inchange : `systemctl stop` envoie `SIGTERM`,
Boilerack rend `0`, et l'unite s'arrete proprement sans redemarrage.

### 8.2 Le cas du code `1`, mesure

Fait etabli hors ligne, et non suppose : lorsque le broker est injoignable au
demarrage, l'ouverture de la connexion leve, l'exception remonte inchangee
jusqu'a l'interpreteur, et **le processus sort avec le code `1`**, trace incluse.
C'est le comportement contracte par C10 pour une panne.

Consequence : un broker indisponible **au demarrage** produit un `1`, donc un
redemarrage. C'est le comportement voulu — le service retentera.

### 8.3 Cadence de redemarrage — clause derivee

Cette consequence en impose une autre, decouverte en instruisant §8.2 : avec le
delai de redemarrage par defaut, un broker durablement injoignable au demarrage
produirait plusieurs echecs par seconde, et le compteur de demarrages de systemd
mettrait rapidement l'unite en etat d'echec — soit **l'inverse** de la resilience
recherchee.

`RestartSec` doit donc satisfaire :

```text
RestartSec >= StartLimitIntervalSec / StartLimitBurst
```

Avec les valeurs par defaut de systemd — fenetre de 10 s, 5 demarrages — le
plancher vaut **2 s**. Le gabarit retient **10 s**, qui laisse une marge de
facteur cinq et se situe dans le meme ordre de grandeur que le delai minimal de
reconnexion natif de Paho (1 s, C11 P10) : le service ne retente pas plus vite
que la bibliotheque qu'il pilote.

> **Inconnue conservee.** `StartLimitIntervalSec` et `StartLimitBurst` sont des
> defauts de systemd qu'une distribution peut modifier. La relation ci-dessus est
> contractee ; la valeur du plancher depend d'un reglage exterieur et ne peut
> etre verifiee hors terrain.

### 8.4 Perte MQTT durable

**C12 ne rouvre pas C11.** Le comportement reste celui que C11 §14 a conserve :

- Paho conserve sa politique native de reconnexion, backoff compris ;
- le processus **ne sort pas** parce que MQTT est durablement indisponible ;
- aucun delai maximal, aucun compteur d'echecs, aucune horloge n'est ajoute ;
- les lectures ne sont pas suspendues.

Consequence pour le superviseur, a ecrire noir sur blanc : **systemd ne redemarre
pas Boilerack du seul fait d'une indisponibilite durable du broker**, puisque le
processus reste vivant. La reprise est assuree par C11, pas par le superviseur.

La dissymetrie avec §8.2 est voulue et doit etre comprise : une indisponibilite
**au demarrage** fait sortir en `1` — la connexion initiale est synchrone —, une
indisponibilite **en cours de route** ne fait pas sortir. C12 constate cette
dissymetrie ; il ne la corrige pas, car la corriger reviendrait a modifier C11.

---

## 9. Unite systemd

Le lot d'implementation versionnera **un gabarit**, non une unite installee.
Clauses attendues et leur justification :

| Clause | Valeur | Justification |
|---|---|---|
| `Type` | `simple` | Le processus ne se dedouble pas, ne se detache pas, et n'implemente aucun protocole de disponibilite. `notify` exigerait `sd_notify`, que Boilerack ne fournit pas — l'ajouter serait hors perimetre |
| `ExecStart` | §5 | script installe, chemin absolu, `--config` explicite |
| `User` / `Group` | `boilerack` | §4.2, moindre privilege |
| `EnvironmentFile` | `/etc/boilerack/boilerack.env`, **sans prefixe `-`** | §6, secret hors unite, absence du fichier bloquante |
| `Restart` | `on-failure` | §8.1 |
| `RestartPreventExitStatus` | `2 130` | §8.1 — configuration et interruption, ni l'une ni l'autre relancee |
| `SuccessExitStatus` | **absente** | §8.1 — `130` n'est pas requalifie en succes |
| `RestartSec` | `10` | §8.3, derive |
| `KillSignal` | `SIGTERM` | §7, socle de C9 rendu explicite |
| `TimeoutStopSec` | §10 | derive d'une borne partielle |
| `After` / `Wants` | §9.1 | ordonnancement, pas disponibilite |
| `WantedBy` | `multi-user.target` | service systeme sans interface graphique |
| `StandardOutput` / `StandardError` | non declares | §11 : le defaut va deja au journal |
| `StateDirectory` et apparentes | **absents** | §4.3 : rien n'est ecrit |

### 9.1 Dependances reseau — ce qui est promis et ce qui ne l'est pas

```text
Wants=network-online.target
After=network-online.target
```

Cette clause ordonne le demarrage apres que **la pile reseau locale** est
configuree. Elle ne dit **rien** de la disponibilite du broker MQTT, qui est un
service applicatif distant, possiblement sur une autre machine, et dont aucun
`target` systemd ne connait l'etat.

Il est **INTERDIT** d'ecrire ou de laisser entendre que cette clause garantit que
le broker est joignable. Si le broker n'est pas la, le demarrage echoue en `1`
(§8.2) et la politique de redemarrage s'applique : c'est ainsi que la
disponibilite applicative est traitee, pas par un ordonnancement.

---

## 10. `TimeoutStopSec`

### 10.1 Ce qui est bornable, et ce qui ne l'est pas

C9 est explicite : la latence totale de sortie **n'a aucune borne contractuelle**,
et « aucune formulation de ce projet ne doit laisser entendre que `SIGINT` ou
`SIGTERM` garantit un arret du processus complet en moins de X secondes ». C12 ne
contredit pas cette clause et n'en fabrique aucune.

Une borne **partielle** est cependant deductible, et elle suffit a fonder un
plancher. Trois faits du depot :

1. le signal est vu vite : l'attente du runner est interrompue par le signal (C9) ;
2. un cycle **deja commence n'est jamais tronque** : le runner ne coupe pas un
   `run_due()` en cours (C9) ;
3. chaque lecture est bornee par `subprocess.run(timeout=read_timeout_s)`, et les
   mesures dues sont lues **sequentiellement**.

Il en decoule un pire cas pour la seule phase de lecture :

```text
plancher = nombre de mesures dues x read_timeout_s
```

Avec la surface v1 — **8** mesures — et le defaut `read_timeout_s = 5.0`, le
plancher vaut **40 s**.

### 10.2 Clause

`TimeoutStopSec` **MUST** etre strictement superieur a ce plancher. En dessous,
systemd enverrait `SIGKILL` au milieu d'un cycle : l'annonce `offline` ne serait
jamais publiee, et le retenu de presence resterait `online` alors que le pont est
mort — soit exactement le mensonge inverse de celui que C11 a corrige.

Le gabarit retient **`TimeoutStopSec=90`** : strictement superieur au plancher de
40 s, avec une marge de 50 s pour la fermeture MQTT, et egal au defaut historique
de systemd, ce qui n'introduit aucune surprise pour un exploitant.

**Clause d'exploitation** : `read_timeout_s` est reglable par l'utilisateur (C10).
Si l'exploitant l'augmente, le plancher augmente proportionnellement et
`TimeoutStopSec` **doit etre revu**. Cette dependance doit figurer dans la
documentation d'exploitation.

> **Inconnue conservee.** La marge au-dela du plancher n'est pas demontree : la
> fermeture MQTT et la duree de `stop()` ne sont bornees par aucun contrat (C9).
> `90` est un choix **derive et justifie**, non une garantie. Seule une
> qualification terrain pourrait l'etayer.

---

## 11. Journalisation

Boilerack ecrit sur **stderr** (A6). Sous systemd, la sortie standard et la
sortie d'erreur d'un service sont capturees par le journal sans qu'aucune clause
ne soit necessaire.

Clauses normatives :

- **aucun fichier de journal n'est ajoute** a Boilerack — ce serait rouvrir A10
  et exiger un repertoire inscriptible qui n'existe pas ;
- aucune rotation, aucun `syslog`, aucune destination alternative ;
- le niveau reste regle par `--log-level`, defaut `INFO` ;
- `StandardOutput` et `StandardError` ne sont pas declares dans le gabarit : les
  declarer figerait un comportement que le defaut assure deja.

---

## 12. Permissions — moindre privilege

Principe : Boilerack ne recoit que ce que son comportement observe exige.

**Requis** : lire `/etc/boilerack/boilerack.toml` · lire
`/etc/boilerack/boilerack.env` · executer `/opt/boilerack/venv/bin/boilerack` ·
ouvrir une connexion sortante vers le broker · executer le binaire `vclient`
designe par la configuration.

**Non requis, donc non accorde** : `root` · toute ecriture disque (A10) · tout
repertoire d'etat (§4.3) · tout port en ecoute · toute capacite particuliere.

Les directives de durcissement supplementaires de systemd — restriction du
systeme de fichiers, des espaces de noms, des appels systeme — **ne sont pas
contractees ici**. Elles se justifient, mais chacune peut casser l'execution d'un
sous-processus `vclient` de facon qui n'est pas verifiable hors terrain. Les
ajouter sans pouvoir les eprouver serait promettre une surete non demontree.
Elles relevent du chantier de qualification terrain (§17).

---

## 13. Validation hors ligne — ce qui doit etre prouve

Toutes ces preuves sont realisables sans machine cible, sans `systemctl`, sans
broker et sans chaudiere.

**Sur l'artefact installe** — dans un environnement jetable, cree puis detruit :
l'installation du paquet produit reellement la commande `boilerack` ; cette
commande s'execute et rend `0` sur `--help`, `2` sans argument, `2` sur une
configuration inexistante avec un message et sans trace.

**Sur le gabarit** — analyse comme un fichier de type INI : sections attendues,
aucune cle inconnue, valeurs conformes aux clauses de §9 ; `ExecStart` designe le
script installe et non une invocation `python -m` ni un chemin de developpement ;
`--config` present avec le chemin de §4.1 ; aucun secret ; aucun chemin local a
une machine de developpement ; `User` different de `root`.

**Sur la coherence** — le gabarit, le contrat et la documentation d'exploitation
ne se contredisent pas sur les chemins, les codes de sortie et la politique de
redemarrage.

**Sur la non-regression** — le chargeur de configuration ne gagne aucun
emplacement par defaut ; aucune dependance au repertoire courant n'apparait ;
aucune ecriture disque n'est introduite.

---

## 14. Validation terrain differee — ce qui ne peut pas etre prouve ici

A ecrire tel quel, sans attenuation :

- qu'une unite reelle s'analyse, se charge et demarre ;
- que `systemctl stop` obtienne effectivement le code `0` et l'annonce `offline` ;
- que `TimeoutStopSec` suffise reellement dans le pire cas ;
- que `journald` capture correctement les lignes emises ;
- que `RestartPreventExitStatus` empeche effectivement le redemarrage sur `2`
  et sur `130` ;
- qu'un fichier d'environnement absent empeche effectivement le demarrage ;
- que les valeurs de `StartLimitIntervalSec` et `StartLimitBurst` de la
  distribution cible rendent `RestartSec=10` suffisant ;
- que l'utilisateur `boilerack` dispose des droits necessaires pour executer
  `vclient` et joindre le broker ;
- l'ensemble du comportement contre un broker, un `vcontrold` et une chaudiere
  reels.

**Aucune conformite systemd reelle n'est revendiquee par C12.** Un gabarit
valide statiquement n'est pas une unite qui fonctionne.

---

## 15. Proprietes a verrouiller

Le lot d'implementation devra prouver, au minimum, les proprietes suivantes. Les
noms de tests ne sont pas fixes ici ; les proprietes le sont.

### Artefact installe

1. L'installation du paquet dans un environnement jetable produit reellement la
   commande `boilerack` — presence verifiee, non deduite des metadonnees.
2. La commande installee est **executee** et rend `0` sur `--help`.
3. La commande installee rend le code contracte lorsqu'aucune configuration n'est
   fournie.
4. La commande installee rend le code contracte lorsque la configuration
   n'existe pas, avec un message et **sans trace**.

### Gabarit

5. `ExecStart` designe le **script installe**, jamais `python -m boilerack`.
6. `ExecStart` fournit explicitement `--config`.
7. Le chemin de configuration est exactement `/etc/boilerack/boilerack.toml`.
8. Le gabarit **ne contient aucun secret**, ni reel ni factice.
9. Le gabarit reference `/etc/boilerack/boilerack.env` par `EnvironmentFile`,
   **sous la forme stricte**, sans prefixe `-`.
10. `User` est renseigne et **different de `root`**.
11. `Restart=on-failure` est present, et `RestartPreventExitStatus` porte
    **`2` ET `130`**.
11bis. `SuccessExitStatus` est **absente** : `130` n'est pas requalifie en succes.
12. `KillSignal=SIGTERM` est present.
13. `TimeoutStopSec` est strictement superieur au plancher de §10.
14. Le gabarit ne contient **aucun chemin local a une machine de developpement**.
15. Le gabarit s'analyse comme un fichier INI valide, sans cle inconnue.
16. Le gabarit ne declare **aucun repertoire d'etat**.

### Non-regression

17. Le chargeur de configuration ne cherche **toujours aucun** emplacement par
    defaut.
18. Aucune dependance au repertoire courant n'est introduite.
19. Aucune ecriture disque metier n'est introduite : journaliser n'exige rien.
20. La semantique C9 de `SIGTERM` est inchangee.
21. La semantique C11 de la perte MQTT est inchangee — le processus reste vivant.

### Documentation

22. Le contrat distingue explicitement validation hors ligne et conformite
    terrain, et ne revendique nulle part la seconde.

---

## 16. Mutations discriminantes

Aucun test n'est ecrit a ce stade. **Aucune mutation n'est declaree tuee.**

| # | Mutation | Propriete visee |
|---|---|---|
| 1 | `ExecStart` en `python -m boilerack` | 5 |
| 2 | Suppression de `--config` dans `ExecStart` | 6 |
| 3 | Chemin de configuration errone | 7 |
| 4 | Secret inscrit directement dans l'unite | 8 |
| 5 | `EnvironmentFile` errone ou absent | 9 |
| 5bis | `EnvironmentFile` sous forme **tolerante** (`-`) | 9 |
| 6 | `User=root` | 10 |
| 7 | Suppression de `RestartPreventExitStatus` | 11 |
| 7bis | Suppression du seul `130`, en gardant `2` | 11 |
| 7ter | Ajout de `SuccessExitStatus=130` | 11bis |
| 8 | `Restart=always` | 11 |
| 9 | `KillSignal` different de `SIGTERM` | 12 |
| 10 | `TimeoutStopSec` inferieur au plancher | 13 |
| 11 | Chemin de checkout local dans le gabarit | 14 |
| 12 | Gabarit syntaxiquement invalide | 15 |
| 13 | Declaration d'un `StateDirectory` | 16 |
| 14 | **Preuve du script installe remplacee par une simple lecture de metadonnees, sans execution** | 1, 2 |
| 15 | Ajout d'un emplacement de configuration par defaut dans le chargeur | 17 |

La mutation 14 est la plus importante : c'est exactement le defaut que le depot
porte aujourd'hui, ou `[project.scripts]` est verifie statiquement mais ou le
script installe n'est jamais execute.

---

## 17. Risques et inconnues

| # | Inconnue ou risque | Portee |
|---|---|---|
| I1 | Comportement reel de systemd : analyse, demarrage, arret, redemarrage | Tout §14 reste non valide |
| I2 | Suffisance reelle de `TimeoutStopSec=90` : la marge au-dela du plancher n'est pas demontree | §10 |
| I3 | `StartLimitIntervalSec` et `StartLimitBurst` reels de la distribution cible | §8.3 |
| I4 | Droits reels de l'utilisateur `boilerack` sur `vclient` et sur le reseau | §12 |
| I5 | Directives de durcissement non contractees, potentiellement incompatibles avec un sous-processus | §12 |
| I6 | La dissymetrie « broker absent au demarrage » (sortie `1`) contre « broker perdu en route » (aucune sortie) peut surprendre un exploitant | §8.4 — constatee, non corrigee |
| R1 | **Illusion de conformite** : un gabarit valide statiquement n'est pas une unite qui fonctionne. Risque principal du lot | §14 |
| R2 | Derive vers l'installation et le deploiement, adjacents et tentants | §3 |
| R3 | Tentation d'inscrire un emplacement par defaut dans le chargeur, ce qui contredirait C10 | Propriete 17 |
| R4 | Tentation de rouvrir C11 pour ajouter un delai MQTT fatal | §8.4 |

---

## 18. Ce que C12 ne fait pas

Aucun changement de code, de CLI, de runtime, de signaux, de configuration ou de
dependance · aucune unite installee, activee ou executee · aucun installateur ·
aucun deploiement · aucune release, aucun tag, aucun changement de version ·
aucune modification de C9, C10 ou C11.

**AUCUNE CONFORMITE TERRAIN N'EST REVENDIQUEE.** Rien n'a ete eprouve contre un
systeme cible, un broker, un demon `vcontrold` ou une chaudiere reels. Toutes les
preuves prevues sont hors ligne : environnement jetable et analyse statique.

---

## 19. Renvois

`c8-composition-root.md` — racine de composition, et report explicite du « mode de
deploiement » · `c9-process-lifecycle.md` — signaux, codes `0` et `130`, absence
de borne sur la latence totale de sortie · `c10-user-interface.md` — commande
installee, `--config` obligatoire sans emplacement par defaut, secret par
variable d'environnement, journalisation sur stderr, codes `2` et `1` ·
`c11-presence-recovery.md` — survie a la perte MQTT, reprise de presence, et §14
qui renvoie ici la question du redemarrage.

**Chantier futur, hors C12** : qualification terrain — installation reelle,
activation du service, mesure de l'arret propre, durcissement systemd, et
validation contre un broker, un `vcontrold` et une chaudiere reels.
