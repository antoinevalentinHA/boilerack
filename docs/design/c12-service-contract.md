# C12 — Contrat d'exploitation et de service

Document normatif. Il fixe la **surface d'exploitation** de Boilerack : où vivent
le code, la configuration et le secret, sous quelle identité le pont tourne, quel
superviseur le démarre et l'arrête, et ce qu'un superviseur doit conclure de
chaque code de sortie.

C12 ne modifie **aucun comportement du programme**. Il ne redéfinit ni les codes
de sortie (C10), ni les signaux (C9), ni la reconnexion (C11), ni la
configuration (C10). Il décrit ce que ces lots rendent déjà possible, et le rend
opposable.

---

## 1. Objet

Boilerack est aujourd'hui un programme installable et lançable à la main. Il
n'est pas un **service**. Rien dans le dépôt ne dit où sa configuration doit
vivre, sous quelle identité il doit tourner, ni ce qu'un superviseur doit faire
quand il s'arrête.

C11 §14 a explicitement renvoyé ici la question restée ouverte :

> « Comportement existant conservé, **susceptible d'être reconsidéré lors du
> futur chantier d'exploitation et de service**, où la question du redémarrage se
> posera réellement. »

C12 répond à cette question, et seulement à elle.

**C12 ne prétend pas que Boilerack est installé, ni qualifié sur le terrain.**
Aucune unité n'est activée, aucun `systemctl` n'est exécuté, aucune machine cible
n'est touchée. Ce qui est produit est un **contrat** et un **gabarit versionné**,
valides hors ligne.

---

## 2. Autorités et acquis

Ce que C12 **reprend sans le redéfinir**, vérifié dans le dépôt :

| # | Acquis | Origine | Preuve |
|---|---|---|---|
| A1 | Le paquet se construit et s'installe, et l'installation crée la commande `boilerack` | C10, `pyproject.toml` | installation mesurée dans un environnement jetable : code retour `0`, script présent |
| A2 | La commande installée fonctionne : `--help` rend `0`, sans argument rend `2`, configuration absente rend `2` avec un message et sans trace | C10 | mesure directe sur l'installation jetable |
| A3 | Une seule dépendance d'exécution : `paho-mqtt` | C4 | `pip list` sur l'installation jetable |
| A4 | `--config` est **obligatoire** et **aucun emplacement par défaut n'est cherche** | C10 | contrat C10 et code du chargeur |
| A5 | Un seul secret, une seule variable : `BOILERACK_MQTT_PASSWORD` | C10 | unique lecture d'environnement de tout `src/` |
| A6 | La journalisation va sur **stderr**, horodatée, niveau réglable | C10 | `logging.basicConfig(stream=sys.stderr, ...)` |
| A7 | `SIGTERM` conduit à un arrêt propre et au résultat `0` ; `SIGINT` à `130` | C9 | contrat C9 |
| A8 | Codes de sortie : `0` arrêt propre · `130` interruption · `2` usage ou configuration · `1` panne avec trace | C10 | contrat C10 |
| A9 | Le pont **survit** à une perte MQTT et republie sa présence à la reconnexion | C11 | contrat C11 |
| A10 | **Aucune écriture disque métier** : la seule ouverture de fichier de `src/` est la LECTURE du TOML | — | inspection du code |
| A11 | **Aucune dépendance au répertoire courant** : ni `getcwd`, ni `chdir`, ni chemin relatif | — | inspection du code |

Ces acquis sont des **entrées** de C12. Les contredire serait une régression, pas
une décision d'exploitation.

---

## 3. Hors périmètre — liste fermée

Installation réelle sur une machine cible ou un Raspberry Pi · `systemctl` réel ·
activation d'un service · `systemd-analyze` sur la cible · déploiement réel ·
script d'installation · script de mise à jour · rollback · mise à jour
automatique · Docker · paquet Debian · `pipx` · release publique · changement de
version · changement du classifieur de maturité · broker MQTT réel · `vclient`
réel · `vcontrold` réel · chaudière · Home Assistant · MQTT Discovery · commandes
MQTT · ACK · écriture chaudière · nouveaux datapoints · supervision externe ·
gestionnaire de secrets · modification de C9, C10 ou C11 · traitement des
réserves non bloquantes de C11 · chantier d'accentuation.

**En particulier, C12 ne livre pas l'installateur** qui crée l'environnement
décrit en §4. Il en fixe la cible ; le produire est un chantier distinct.

---

## 4. Modèle d'exploitation

### 4.1 Emplacements

| Rôle | Chemin | Propriétaire | Mode indicatif |
|---|---|---|---|
| Code installé | `/opt/boilerack/venv` | `root` | lecture pour tous |
| Commande | `/opt/boilerack/venv/bin/boilerack` | `root` | exécutable |
| Configuration | `/etc/boilerack/boilerack.toml` | `root:boilerack` | `0640` |
| Secret | `/etc/boilerack/boilerack.env` | `root:boilerack` | `0640` |

**Un environnement virtuel dédié**, et non une installation système : Boilerack
n'a qu'une dépendance d'exécution, et l'isoler évite tout conflit avec le Python
de la distribution. `ExecStart` vise directement le script du venv, ce qui rend
l'interpréteur utilisé explicite et vérifiable.

**Ces chemins appartiennent à l'exploitation, jamais au code.** Le chargeur de
configuration continue de ne chercher aucun emplacement par défaut (A4) : c'est
l'unité qui passe le chemin, explicitement.

Ce point n'est pas une précaution de style. C10 §`--config` écrit :

> « **Aucun chemin implicite n'est introduit** : ni `/etc/boilerack.toml`, ni
> `~/.config/...`, ni le répertoire courant. Boilerack ne cherche pas sa
> configuration, il la reçoit. »

C10 nomme donc **explicitement** un chemin sous `/etc` parmi ceux qui ne sont pas
cherchés. La convention de §4.1 ne le contredit pas : elle désigne où l'exploitant
**place** le fichier, et l'unité le **transmet**. Inscrire ce chemin dans le
programme contredirait C10 et rendrait le comportement dépendant du compte et du
répertoire de lancement.

### 4.2 Identité du service

Boilerack tourne sous un utilisateur **dédié et non privilégié**, par convention
nommé `boilerack`, membre du groupe `boilerack`.

Justification par ce que le programme fait réellement :

- il **n'écrit rien** sur le disque (A10) — aucun répertoire d'état n'est requis ;
- il **ne dépend pas du répertoire courant** (A11) — aucun `WorkingDirectory` n'est nécessaire ;
- il **lit** un fichier de configuration et un fichier d'environnement ;
- il ouvre une **socket sortante** vers le broker et **lance un sous-processus**
  `vclient`.

Aucun de ces besoins n'exige de privilège. **`root` est donc interdit.**

### 4.3 Aucun état persistant

Boilerack ne conserve rien entre deux exécutions : ni cache, ni base, ni fichier
de reprise. L'état de lecture vit en mémoire et meurt avec le processus ;
l'instantané et la présence vivent **chez le broker**, en messages retenus.

Conséquence contractuelle : **aucun `StateDirectory`, aucun `CacheDirectory`,
aucun `RuntimeDirectory` n'est requis**. Une unité qui en déclarerait un
promettrait un besoin qui n'existe pas.

---

## 5. Commande du service

Forme normative de la commande de démarrage :

```text
/opt/boilerack/venv/bin/boilerack --config /etc/boilerack/boilerack.toml
```

Trois exigences, chacune pour une raison distincte :

1. **Le script installé**, pas `python -m boilerack`. Les deux chemins sont
   équivalents (C10), mais l'unité doit exercer l'artefact que l'installation
   produit — celui-la même qu'un exploitant invoquera. `python -m` exigerait en
   outre de nommer un interpréteur et de maîtriser le répertoire courant, alors
   que le script du venv porte déjà son interpréteur.
2. **Un chemin absolu**, puisque le service ne dispose d'aucun `PATH` utile.
3. **`--config` explicite**, puisque le programme n'en cherche aucun (A4).
   L'omettre ferait échouer le démarrage avec le code `2`.

`--log-level` n'est pas contracté dans la commande : son défaut `INFO` convient à
un service, et le rendre obligatoire figerait une politique que l'exploitant doit
pouvoir changer.

---

## 6. Configuration et secret

**Deux fichiers, deux natures.**

`/etc/boilerack/boilerack.toml` porte toute la configuration durable — 13 clés,
aucune secrète (C10). Il est **versionnable** par l'exploitant.

`/etc/boilerack/boilerack.env` porte l'unique secret, sous la forme déjà
contractée :

```text
BOILERACK_MQTT_PASSWORD=...
```

Il est chargé par `EnvironmentFile=`, ce qui laisse l'unité **versionnable sans
secret**.

### Forme STRICTE, sans préfixe

```text
EnvironmentFile=/etc/boilerack/boilerack.env
```

La forme tolérante — `EnvironmentFile=-/etc/...`, qui fait ignorer un fichier
manquant — est **REJETÉE**. Avec elle, un chemin erroné ou un fichier supprimé
ferait disparaître le secret **en silence** : le pont tenterait alors une
connexion sans mot de passe, et l'exploitant ne l'apprendrait qu'au refus du
broker, voire jamais. La forme stricte transforme cette faute en **échec de
démarrage immédiat et lisible**, ce qui est la doctrine constante du projet.

### VARIABLE optionnelle, FICHIER obligatoire — la distinction

Ces deux propositions ne se contredisent pas, et il faut les tenir ensemble :

| Niveau | Règle | Autorité |
|---|---|---|
| **Programme** | `BOILERACK_MQTT_PASSWORD` est **optionnelle** : absente, le chargement réussit et le mot de passe vaut `None` | C10, **inchangé** |
| **Exploitation** | `/etc/boilerack/boilerack.env` est **attendu par l'unité** : absent, le service ne démarre pas | C12 |

Conséquence pratique, à documenter pour l'exploitant : une installation **sans
authentification MQTT** crée tout de même ce fichier, **éventuellement vide**. Le
fichier peut donc exister sans définir la variable — C10 n'est ni durci, ni
contredit : C12 ne parle que du fichier, C10 ne parle que de la variable.

Clauses normatives :

- **le fichier d'unité versionné ne contient AUCUN secret**, ni réel, ni factice,
  ni exemple ressemblant à un secret. Un faux mot de passe versionné finit par
  être copié ;
- le fichier d'environnement n'est **pas** versionné dans ce dépôt ;
- ses permissions restreignent la lecture au service et à l'administrateur ;
- aucune autre variable d'environnement n'est requise : le programme n'en lit
  qu'une (A5).

`Environment=` inline est **rejeté** : il inscrirait le mot de passe dans un
fichier d'unité lisible par tous.

---

## 7. Signaux et codes de sortie

C12 **ne redéfinit rien** ; il fixe ce qu'un superviseur doit en conclure.

| Code | Origine | Sens | Attendu du superviseur |
|---|---|---|---|
| `0` | C9/C10 | arrêt propre, notamment sur `SIGTERM` | **succès** — aucun redémarrage |
| `130` | C9/C10 | interruption (`SIGINT`) | **aucun redémarrage**, et **aucune requalification en succès** : l'interruption reste un échec visible (§8.1) |
| `2` | C10 | usage ou configuration invalide | **échec permanent** — aucun redémarrage (§8) |
| `1` | C10 | panne, avec trace | **échec transitoire possible** — redémarrage (§8) |

`SIGTERM` est le signal d'arrêt de `systemctl stop`, et C9 en fait un arrêt
propre rendant `0`. La correspondance est donc **native**, sans adaptation.

**`KillSignal=SIGTERM` est contracté explicitement**, bien que ce soit déjà le
défaut de systemd. Tout le cycle de vie C9 repose sur ce signal : s'en remettre à
un défaut que rien n'oblige à rester stable reviendrait à fonder une garantie sur
une hypothèse non écrite.

---

## 8. Politique de redémarrage

### 8.1 Règle

```text
Restart=on-failure
RestartPreventExitStatus=2 130
```

`on-failure` plutôt que `always` : un arrêt propre (`0`) est un arrêt **voulu**,
et le relancer contrarierait `systemctl stop`.

**Le code `2` est soustrait au redémarrage.** Sans cela, un TOML invalide
produirait une boucle : échec immédiat, redémarrage, échec immédiat. L'exploitant
verrait un service qui s'agite au lieu d'un service **arrêté et visible**, avec sa
cause dans le journal. C'est l'objectif normatif : **une erreur de configuration
reste arrêtée et lisible ; elle ne boucle jamais.**

**Le code `130` l'est aussi.** Sous `Restart=on-failure`, un `130` serait sinon
relancé : une interruption **demandée** deviendrait un redémarrage subi. Ce code
ne peut naître d'aucune action de systemd lui-même — `systemctl stop` envoie
`SIGTERM` (§7), et un service n'a pas de terminal —, mais il reste atteignable
par une action délibérée d'administrateur, typiquement
`systemctl kill --signal=SIGINT`. La clause couvre ce cas plutôt que de s'en
remettre à son improbabilité.

**`SuccessExitStatus=130` est REJETÉ.** Ce serait l'autre façon d'empêcher le
redémarrage, et elle est refusée : elle requalifierait l'interruption en
**succès**, alors que C9 a choisi `130` précisément pour dire **qui** a demandé
l'arrêt. La distinction serait effacée au niveau du superviseur, et l'unité
paraîtrait s'être arrêtée normalement.

Conséquence assumée, à connaître : après un `SIGINT` administratif explicite,
l'unité reste en état d'**échec** — visible dans `systemctl status` — sans être
relancée. C'est le comportement voulu : **absence de redémarrage automatique
ET visibilité de l'interruption**, plutôt qu'une requalification de confort.

Le chemin normal d'arrêt reste inchangé : `systemctl stop` envoie `SIGTERM`,
Boilerack rend `0`, et l'unité s'arrête proprement sans redémarrage.

### 8.2 Le cas du code `1`, mesure

Fait établi hors ligne, et non supposé : lorsque le broker est injoignable au
démarrage, l'ouverture de la connexion lève, l'exception remonte inchangée
jusqu'à l'interpréteur, et **le processus sort avec le code `1`**, trace incluse.
C'est le comportement contracté par C10 pour une panne.

Conséquence : un broker indisponible **au démarrage** produit un `1`, donc un
redémarrage. C'est le comportement voulu — le service retentera.

### 8.3 Cadence de redémarrage — clause dérivée

Cette conséquence en impose une autre, découverte en instruisant §8.2 : avec le
délai de redémarrage par défaut, un broker durablement injoignable au démarrage
produirait plusieurs échecs par seconde, et le compteur de démarrages de systemd
mettrait rapidement l'unité en état d'échec — soit **l'inverse** de la résilience
recherchée.

`RestartSec` doit donc satisfaire :

```text
RestartSec >= StartLimitIntervalSec / StartLimitBurst
```

Avec les valeurs par défaut de systemd — fenêtre de 10 s, 5 démarrages — le
plancher vaut **2 s**. Le gabarit retient **10 s**, qui laisse une marge de
facteur cinq et se situe dans le même ordre de grandeur que le délai minimal de
reconnexion natif de Paho (1 s, C11 P10) : le service ne retente pas plus vite
que la bibliothèque qu'il pilote.

> **Inconnue conservée.** `StartLimitIntervalSec` et `StartLimitBurst` sont des
> défauts de systemd qu'une distribution peut modifier. La relation ci-dessus est
> contractée ; la valeur du plancher dépend d'un réglage extérieur et ne peut
> être vérifiée hors terrain.

### 8.4 Perte MQTT durable

**C12 ne rouvre pas C11.** Le comportement reste celui que C11 §14 a conservé :

- Paho conserve sa politique native de reconnexion, backoff compris ;
- le processus **ne sort pas** parce que MQTT est durablement indisponible ;
- aucun délai maximal, aucun compteur d'échecs, aucune horloge n'est ajouté ;
- les lectures ne sont pas suspendues.

Conséquence pour le superviseur, à écrire noir sur blanc : **systemd ne redémarre
pas Boilerack du seul fait d'une indisponibilité durable du broker**, puisque le
processus reste vivant. La reprise est assurée par C11, pas par le superviseur.

La dissymétrie avec §8.2 est voulue et doit être comprise : une indisponibilité
**au démarrage** fait sortir en `1` — la connexion initiale est synchrone —, une
indisponibilité **en cours de route** ne fait pas sortir. C12 constate cette
dissymétrie ; il ne la corrige pas, car la corriger reviendrait à modifier C11.

---

## 9. Unité systemd

Le lot d'implémentation versionnera **un gabarit**, non une unité installée.
Clauses attendues et leur justification :

| Clause | Valeur | Justification |
|---|---|---|
| `Type` | `simple` | Le processus ne se dédouble pas, ne se détache pas, et n'implémente aucun protocole de disponibilité. `notify` exigerait `sd_notify`, que Boilerack ne fournit pas — l'ajouter serait hors périmètre |
| `ExecStart` | §5 | script installé, chemin absolu, `--config` explicite |
| `User` / `Group` | `boilerack` | §4.2, moindre privilège |
| `EnvironmentFile` | `/etc/boilerack/boilerack.env`, **sans préfixe `-`** | §6, secret hors unité, absence du fichier bloquante |
| `Restart` | `on-failure` | §8.1 |
| `RestartPreventExitStatus` | `2 130` | §8.1 — configuration et interruption, ni l'une ni l'autre relancée |
| `SuccessExitStatus` | **absente** | §8.1 — `130` n'est pas requalifié en succès |
| `RestartSec` | `10` | §8.3, dérivé |
| `KillSignal` | `SIGTERM` | §7, socle de C9 rendu explicite |
| `TimeoutStopSec` | §10 | dérivé d'une borne partielle |
| `After` / `Wants` | §9.1 | ordonnancement, pas disponibilité |
| `WantedBy` | `multi-user.target` | service système sans interface graphique |
| `StandardOutput` / `StandardError` | non déclarés | §11 : le défaut va déjà au journal |
| `StateDirectory` et apparentés | **absents** | §4.3 : rien n'est écrit |

### 9.1 Dépendances réseau — ce qui est promis et ce qui ne l'est pas

```text
Wants=network-online.target
After=network-online.target
```

Cette clause ordonne le démarrage après que **la pile réseau locale** est
configurée. Elle ne dit **rien** de la disponibilité du broker MQTT, qui est un
service applicatif distant, possiblement sur une autre machine, et dont aucun
`target` systemd ne connaît l'état.

Il est **INTERDIT** d'écrire ou de laisser entendre que cette clause garantit que
le broker est joignable. Si le broker n'est pas la, le démarrage échoue en `1`
(§8.2) et la politique de redémarrage s'applique : c'est ainsi que la
disponibilité applicative est traitée, pas par un ordonnancement.

---

## 10. `TimeoutStopSec`

### 10.1 Ce qui est bornable, et ce qui ne l'est pas

C9 est explicite : la latence totale de sortie **n'a aucune borne contractuelle**,
et « aucune formulation de ce projet ne doit laisser entendre que `SIGINT` ou
`SIGTERM` garantit un arrêt du processus complet en moins de X secondes ». C12 ne
contredit pas cette clause et n'en fabrique aucune.

Une borne **partielle** est cependant déductible, et elle suffit à fonder un
plancher. Trois faits du dépôt :

1. le signal est vu vite : l'attente du runner est interrompue par le signal (C9) ;
2. un cycle **déjà commencé n'est jamais tronqué** : le runner ne coupe pas un
   `run_due()` en cours (C9) ;
3. chaque lecture est bornée par `subprocess.run(timeout=read_timeout_s)`, et les
   mesures dues sont lues **sequentiellement**.

Il en découle un pire cas pour la seule phase de lecture :

```text
plancher = nombre de mesures dues x read_timeout_s
```

Avec la surface v1 — **8** mesures — et le défaut `read_timeout_s = 5.0`, le
plancher vaut **40 s**.

### 10.2 Clause

`TimeoutStopSec` **MUST** être strictement supérieur à ce plancher. En dessous,
systemd enverrait `SIGKILL` au milieu d'un cycle : l'annonce `offline` ne serait
jamais publiée, et le retenu de présence resterait `online` alors que le pont est
mort — soit exactement le mensonge inverse de celui que C11 a corrigé.

Le gabarit retient **`TimeoutStopSec=90`** : strictement supérieur au plancher de
40 s, avec une marge de 50 s pour la fermeture MQTT, et égal au défaut historique
de systemd, ce qui n'introduit aucune surprise pour un exploitant.

**Clause d'exploitation** : `read_timeout_s` est réglable par l'utilisateur (C10).
Si l'exploitant l'augmente, le plancher augmente proportionnellement et
`TimeoutStopSec` **doit être revu**. Cette dépendance doit figurer dans la
documentation d'exploitation.

> **Inconnue conservée.** La marge au-delà du plancher n'est pas démontrée : la
> fermeture MQTT et la durée de `stop()` ne sont bornées par aucun contrat (C9).
> `90` est un choix **dérivé et justifié**, non une garantie. Seule une
> qualification terrain pourrait l'étayer.

---

## 11. Journalisation

Boilerack écrit sur **stderr** (A6). Sous systemd, la sortie standard et la
sortie d'erreur d'un service sont capturées par le journal sans qu'aucune clause
ne soit nécessaire.

Clauses normatives :

- **aucun fichier de journal n'est ajouté** à Boilerack — ce serait rouvrir A10
  et exiger un répertoire inscriptible qui n'existe pas ;
- aucune rotation, aucun `syslog`, aucune destination alternative ;
- le niveau reste réglé par `--log-level`, défaut `INFO` ;
- `StandardOutput` et `StandardError` ne sont pas déclarés dans le gabarit : les
  déclarer figerait un comportement que le défaut assure déjà.

---

## 12. Permissions — moindre privilège

Principe : Boilerack ne reçoit que ce que son comportement observé exige.

**Requis** : lire `/etc/boilerack/boilerack.toml` · lire
`/etc/boilerack/boilerack.env` · exécuter `/opt/boilerack/venv/bin/boilerack` ·
ouvrir une connexion sortante vers le broker · exécuter le binaire `vclient`
désigné par la configuration.

**Non requis, donc non accordé** : `root` · toute écriture disque (A10) · tout
répertoire d'état (§4.3) · tout port en écoute · toute capacité particulière.

Les directives de durcissement supplémentaires de systemd — restriction du
système de fichiers, des espaces de noms, des appels système — **ne sont pas
contractées ici**. Elles se justifient, mais chacune peut casser l'exécution d'un
sous-processus `vclient` de façon qui n'est pas vérifiable hors terrain. Les
ajouter sans pouvoir les éprouver serait promettre une sûreté non démontrée.
Elles relèvent du chantier de qualification terrain (§17).

---

## 13. Validation hors ligne — ce qui doit être prouvé

Toutes ces preuves sont réalisables sans machine cible, sans `systemctl`, sans
broker et sans chaudière.

**Sur l'artefact installé** — dans un environnement jetable, créé puis détruit :
l'installation du paquet produit réellement la commande `boilerack` ; cette
commande s'exécute et rend `0` sur `--help`, `2` sans argument, `2` sur une
configuration inexistante avec un message et sans trace.

**Sur le gabarit** — analysé comme un fichier de type INI : sections attendues,
aucune clé inconnue, valeurs conformes aux clauses de §9 ; `ExecStart` désigne le
script installé et non une invocation `python -m` ni un chemin de développement ;
`--config` présent avec le chemin de §4.1 ; aucun secret ; aucun chemin local à
une machine de développement ; `User` différent de `root`.

**Sur la cohérence** — le gabarit, le contrat et la documentation d'exploitation
ne se contredisent pas sur les chemins, les codes de sortie et la politique de
redémarrage.

**Sur la non-régression** — le chargeur de configuration ne gagne aucun
emplacement par défaut ; aucune dépendance au répertoire courant n'apparaît ;
aucune écriture disque n'est introduite.

---

## 14. Validation terrain différée — ce qui ne peut pas être prouvé ici

À écrire tel quel, sans atténuation :

- qu'une unité réelle s'analyse, se charge et démarre ;
- que `systemctl stop` obtienne effectivement le code `0` et l'annonce `offline` ;
- que `TimeoutStopSec` suffise réellement dans le pire cas ;
- que `journald` capture correctement les lignes émises ;
- que `RestartPreventExitStatus` empêche effectivement le redémarrage sur `2`
  et sur `130` ;
- qu'un fichier d'environnement absent empêche effectivement le démarrage ;
- que les valeurs de `StartLimitIntervalSec` et `StartLimitBurst` de la
  distribution cible rendent `RestartSec=10` suffisant ;
- que l'utilisateur `boilerack` dispose des droits nécessaires pour exécuter
  `vclient` et joindre le broker ;
- l'ensemble du comportement contre un broker, un `vcontrold` et une chaudière
  réels.

**Aucune conformité systemd réelle n'est revendiquée par C12.** Un gabarit
valide statiquement n'est pas une unité qui fonctionne.

---

## 15. Propriétés à verrouiller

Le lot d'implémentation devra prouver, au minimum, les propriétés suivantes. Les
noms de tests ne sont pas fixés ici ; les propriétés le sont.

### Artefact installé

1. L'installation du paquet dans un environnement jetable produit réellement la
   commande `boilerack` — présence vérifiée, non déduite des métadonnées.
2. La commande installée est **exécutée** et rend `0` sur `--help`.
3. La commande installée rend le code contracté lorsqu'aucune configuration n'est
   fournie.
4. La commande installée rend le code contracté lorsque la configuration
   n'existe pas, avec un message et **sans trace**.

### Gabarit

5. `ExecStart` désigne le **script installé**, jamais `python -m boilerack`.
6. `ExecStart` fournit explicitement `--config`.
7. Le chemin de configuration est exactement `/etc/boilerack/boilerack.toml`.
8. Le gabarit **ne contient aucun secret**, ni réel ni factice.
9. Le gabarit référence `/etc/boilerack/boilerack.env` par `EnvironmentFile`,
   **sous la forme stricte**, sans préfixe `-`.
10. `User` est renseigné et **différent de `root`**.
11. `Restart=on-failure` est présent, et `RestartPreventExitStatus` porte
    **`2` ET `130`**.
11bis. `SuccessExitStatus` est **absente** : `130` n'est pas requalifié en succès.
12. `KillSignal=SIGTERM` est présent.
13. `TimeoutStopSec` est strictement supérieur au plancher de §10.
14. Le gabarit ne contient **aucun chemin local à une machine de développement**.
15. Le gabarit s'analyse comme un fichier INI valide, sans clé inconnue.
16. Le gabarit ne déclare **aucun répertoire d'état**.

### Non-régression

17. Le chargeur de configuration ne cherche **toujours aucun** emplacement par
    défaut.
18. Aucune dépendance au répertoire courant n'est introduite.
19. Aucune écriture disque métier n'est introduite : journaliser n'exige rien.
20. La sémantique C9 de `SIGTERM` est inchangée.
21. La sémantique C11 de la perte MQTT est inchangée — le processus reste vivant.

### Documentation

22. Le contrat distingue explicitement validation hors ligne et conformité
    terrain, et ne revendique nulle part la seconde.

---

## 16. Mutations discriminantes

Aucun test n'est écrit à ce stade. **Aucune mutation n'est déclarée tuée.**

| # | Mutation | Propriété visée |
|---|---|---|
| 1 | `ExecStart` en `python -m boilerack` | 5 |
| 2 | Suppression de `--config` dans `ExecStart` | 6 |
| 3 | Chemin de configuration erroné | 7 |
| 4 | Secret inscrit directement dans l'unité | 8 |
| 5 | `EnvironmentFile` erroné ou absent | 9 |
| 5bis | `EnvironmentFile` sous forme **tolérante** (`-`) | 9 |
| 6 | `User=root` | 10 |
| 7 | Suppression de `RestartPreventExitStatus` | 11 |
| 7bis | Suppression du seul `130`, en gardant `2` | 11 |
| 7ter | Ajout de `SuccessExitStatus=130` | 11bis |
| 8 | `Restart=always` | 11 |
| 9 | `KillSignal` différent de `SIGTERM` | 12 |
| 10 | `TimeoutStopSec` inférieur au plancher | 13 |
| 11 | Chemin de checkout local dans le gabarit | 14 |
| 12 | Gabarit syntaxiquement invalide | 15 |
| 13 | Déclaration d'un `StateDirectory` | 16 |
| 14 | **Preuve du script installé remplacée par une simple lecture de métadonnées, sans exécution** | 1, 2 |
| 15 | Ajout d'un emplacement de configuration par défaut dans le chargeur | 17 |

La mutation 14 est la plus importante : c'est exactement le défaut que le dépôt
porte aujourd'hui, où `[project.scripts]` est vérifié statiquement mais où le
script installé n'est jamais exécuté.

---

## 17. Risques et inconnues

| # | Inconnue ou risque | Portée |
|---|---|---|
| I1 | Comportement réel de systemd : analyse, démarrage, arrêt, redémarrage | Tout §14 reste non valide |
| I2 | Suffisance réelle de `TimeoutStopSec=90` : la marge au-delà du plancher n'est pas démontrée | §10 |
| I3 | `StartLimitIntervalSec` et `StartLimitBurst` réels de la distribution cible | §8.3 |
| I4 | Droits réels de l'utilisateur `boilerack` sur `vclient` et sur le réseau | §12 |
| I5 | Directives de durcissement non contractées, potentiellement incompatibles avec un sous-processus | §12 |
| I6 | La dissymétrie « broker absent au démarrage » (sortie `1`) contre « broker perdu en route » (aucune sortie) peut surprendre un exploitant | §8.4 — constatée, non corrigée |
| R1 | **Illusion de conformité** : un gabarit valide statiquement n'est pas une unité qui fonctionne. Risque principal du lot | §14 |
| R2 | Dérive vers l'installation et le déploiement, adjacents et tentants | §3 |
| R3 | Tentation d'inscrire un emplacement par défaut dans le chargeur, ce qui contredirait C10 | Propriété 17 |
| R4 | Tentation de rouvrir C11 pour ajouter un délai MQTT fatal | §8.4 |

---

## 18. Ce que C12 ne fait pas

Aucun changement de code, de CLI, de runtime, de signaux, de configuration ou de
dépendance · aucune unité installée, activée ou exécutée · aucun installateur ·
aucun déploiement · aucune release, aucun tag, aucun changement de version ·
aucune modification de C9, C10 ou C11.

**AUCUNE CONFORMITÉ TERRAIN N'EST REVENDIQUÉE.** Rien n'a été éprouvé contre un
système cible, un broker, un démon `vcontrold` ou une chaudière réels. Toutes les
preuves prévues sont hors ligne : environnement jetable et analyse statique.

---

## 19. Renvois

`c8-composition-root.md` — racine de composition, et report explicite du « mode de
déploiement » · `c9-process-lifecycle.md` — signaux, codes `0` et `130`, absence
de borne sur la latence totale de sortie · `c10-user-interface.md` — commande
installée, `--config` obligatoire sans emplacement par défaut, secret par
variable d'environnement, journalisation sur stderr, codes `2` et `1` ·
`c11-presence-recovery.md` — survie à la perte MQTT, reprise de présence, et §14
qui renvoie ici la question du redémarrage.

**Chantier futur, hors C12** : qualification terrain — installation réelle,
activation du service, mesure de l'arrêt propre, durcissement systemd, et
validation contre un broker, un `vcontrold` et une chaudière réels.
