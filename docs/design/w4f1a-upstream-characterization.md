# W4-F1A — caractérisation amont de U-1 : rapport

> **Exécution du lot cadré par `w4f1a-vcontrold-concurrency.md`. Version 4**,
> après audit delta de la V3, rendu **GO avec réserves non bloquantes**. Le fond
> est **entièrement inchangé** : niveau, régime, jeu d'hypothèses, matrice des
> six maillons, statuts, besoin suivant et frontières sont ceux de la V3, validés.
> La V4 ne corrige que quatre incohérences documentaires, choisies pour ne pas
> intégrer de défaut connu : une limite périmée citée au §14 #15, le
> rattachement de `H6` non propagé au §9, un décompte d'événements erroné au
> §14 #5, et quatre repères de ligne imprécis (§4.2, §10.3).
>
> **NON TERRAIN, SANS CODE.** Aucun accès au Pi, au réseau local du site, au
> broker, au démon réel, à `vclient`, à la chaudière, à un service systemd.
> Aucun déploiement, aucune instrumentation, aucune modification de
> configuration, aucune écriture. Les seules consultations externes sont des
> **sources publiques amont**, énumérées au §3.
>
> **W4-F2 reste FERMÉ.** Ce document ne demande ni n'accorde aucune autorisation
> terrain. **W4-F0, W4-F1 et le cadrage W4-F1A restent CLOSED et intacts.**
>
> **Ce rapport ne rend pas le verdict de T0-B** (cadrage §5). Son résultat est
> **informatif et discriminant**, jamais opératoire.

---

## 1. Résultat

| | |
|---|---|
| **Niveau épistémique** | **`PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION`** |
| **Valeur de régime** | **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`** |
| **Statut `U-1`** | `U-1 — PART AMONT ÉTABLIE SOUS H1/H2/H3/H6, RÉSIDU D'INSTALLATION OUVERT` |
| **Statut `I1`** | `I1 PARTIELLEMENT RÉDUITE` |

Quatre hypothèses, contre cinq en V1 : `H4` et `H5` disparaissent, `H6` apparaît.

> **Ce que ce résultat ne vaut pas.** Il ne vaut pas verdict `T0-B`, ne produit
> pas `T0 GO`, n'ouvre pas W4-F2, n'autorise aucun terrain, et ne désigne ni V-2
> ni V-3 comme prochain acte (cadrage §11.7.1, cas conditionnel).

---

## 2. Autorité documentaire

| Document lu | Clauses gouvernantes retenues |
|---|---|
| `w4f1a-vcontrold-concurrency.md` — **le contrat de ce lot** | §5 · §6.1 population · §6.2 six maillons · §6.3 preuve positive · §6.4 · §7 frontière · §11.3 voie 1 · §11.4 voie 2 · §11.5 preuve rejouable · §11.7.1 et §11.7.2 · §11.8 · §11.9 · §12 |
| `w4f1-confirmation-window.md` | §8.2 précondition de T0-B · §8.5 `C1`, population et résolution · §9 U-1 |
| `w4f-write-sovereignty.md` | §10.3.4 |
| `w2-transaction-concurrency-lifecycle.md` | §15.2, §15.3, §32.1 (I1) |
| `c5-vclient-contract.md` | §1 provenance et installation · §2 version observée · §9 contention et durées |
| `w4c-write-capture-protocol.md` | §8 superviseur · §9 étape 6 · §9.1 journal |

**Population étudiée** — les **sondes du superviseur, et elles seules** (cadrage
§6.1). Exclues : toutes les commandes indistinctement, toutes les connexions,
toutes les sessions, les commandes rejetées avant Optolink, les écritures,
l'usage interactif.

---

## 3. Source amont — et l'écart de version, levé

| | |
|---|---|
| dépôt | `openv/vcontrold` |
| URL | `https://github.com/openv/vcontrold` |
| étiquette | **`v0.98.12`** |
| **commit de l'étiquette** | **`a17067d5dcffda66f63515f2415fa44c3705ac68`** |
| commit du client observé (C5 §2) | `8ca47972c9ac5b0a14a7a36393b0dbfdb165f918` |
| écart | **5 commits**, 0 en arrière |
| fichiers lus | `src/vcontrold.c` · `src/socket.c` · `src/semaphore.c` · `src/common.c` · `src/io.c` · `src/framer.c` · `CMakeLists.txt` |
| symboles examinés | `main`, `interactive`, `readCmdFile`, `listenToSocket`, `closeSocket`, `logIT`, `initLog`, `setDebugFD`, `vcontrol_seminit`, `vcontrol_semget`, `vcontrol_semrelease`, `vcontrol_semfree`, `initsem`, `framer_openDevice`, `framer_closeDevice`, `framer_open_p300`, `framer_close_p300`, `framer_send`, `setnonblock`, `setblock`, et l'ouverture du périphérique dans `io.c` |

### 3.1 Les cinq commits, énumérés

| # | commit | sujet |
|---|---|---|
| 1 | `27c16f3e08de500286ef644b1b631d1243e846d9` | *Updated my email address* |
| 2 | `7ac1c2494b671095bab06051a367633e6462ca6c` | *Fixed len for setTempWWsoll* |
| 3 | `f9fb155ea8d45dd4bb714135402db9532e6ed2b1` | *Revert « Fixed len for setTempWWsoll »* |
| 4 | `70ef62b318c2188b6ffd865f9c4d571a508b1eda` | *setTempWWsoll's length is reportedly actually 1 ;-)* |
| 5 | `8ca47972c9ac5b0a14a7a36393b0dbfdb165f918` | *Update build.yml* |

**Fichiers touchés sur l'ensemble de l'écart**, exhaustivement :
`.github/workflows/build.yml` · `CMakeLists.txt` · `cmake/GitDescription.cmake` ·
`cmake/UpdateVersion.cmake` · `doc/man/CMakeLists.txt` · `src/version.h.in` ·
`xml/300/vito.xml`. Toutes ces modifications valent **+1 / −1** ligne, hormis le
workflow.

**Aucun des fichiers de concurrence n'apparaît.**

### 3.2 Empreintes de blob aux deux extrémités

| chemin | à `a17067d5…` | à `8ca47972…` | |
|---|---|---|---|
| `src/vcontrold.c` | `d2adee6d9fea60aba6aa32dec563e32fa44217e7` | `d2adee6d9fea60aba6aa32dec563e32fa44217e7` | **identique** |
| `src/socket.c` | `ac97fa0d6f72c6708fc946406ac111173815fa99` | `ac97fa0d6f72c6708fc946406ac111173815fa99` | **identique** |
| `src/semaphore.c` | `33d8ffd7b67747d4b34f2435894e43b1316e189a` | `33d8ffd7b67747d4b34f2435894e43b1316e189a` | **identique** |
| `src/common.c` | `00b87df7421bbdec846295111abad8b882c79e82` | `00b87df7421bbdec846295111abad8b882c79e82` | **identique** |
| `src/io.c` | `29e698bb361a8dd001faeada0815bc3e8012f0aa` | `29e698bb361a8dd001faeada0815bc3e8012f0aa` | **identique** |
| `src/framer.c` | `31c4f880ccbe5fd0c6d943bf696cbbf21d28fbf7` | `31c4f880ccbe5fd0c6d943bf696cbbf21d28fbf7` | **identique** |
| `CMakeLists.txt` | `578579aa1987330d49ae0d7786dcbd08c80e2403` | `576b248ac2142f72420cf41c37b11f96d42ddd9b` | diffère — **+1/−1**, machinerie de version (§4.1) |

> **Conclusion, écrite explicitement :** **la preuve conduite sur `v0.98.12` est
> transférable au commit `8ca47972c9ac5b0a14a7a36393b0dbfdb165f918` pour la
> question W4-F1A.** Les six fichiers portant la concurrence, l'exclusion,
> l'acceptation, l'accès au périphérique et la journalisation sont **le même
> objet Git** aux deux extrémités. Cet écart **ne figure plus dans `H1`**.

> **Identité de la source ≠ identité du binaire déployé.** Ce qui précède
> caractérise **l'amont**. Ce que le site exécute réellement demeure `H1`.

---

## 4. Construction, plateforme, invocation

### 4.1 Système de construction — `CMakeLists.txt` à `v0.98.12`

| Élément | Valeur | Effet sur le modèle de concurrence |
|---|---|---|
| `add_definitions(-D_XOPEN_SOURCE=700)` | définition globale | expose le jeu POSIX.1-2008 ; **ne modifie** ni le `fork`, ni le sémaphore, ni l'acceptation |
| `option(MANPAGES … ON)` | page de manuel | **aucun** |
| `option(VCLIENT … ON)` | construit le client | **aucun** sur le démon |
| `option(VSIM … OFF)` | construit un simulateur | **aucun** sur le démon |
| `if (APPLE)` → `-D_DARWIN_C_SOURCE` | seul conditionnel de plateforme du CMake | **sans objet** sur Debian 13 / aarch64 (C5 §1) |
| liaison `${CMAKE_THREAD_LIBS_INIT}` | typiquement `-pthread` | **lier `pthread` n'est pas s'en servir** : aucun fil n'est créé sur le chemin étudié, qui procède par `fork` |

**Le seul écart de `CMakeLists.txt` sur les cinq commits** est de +1/−1 ligne,
dans le groupe des fichiers de version (`cmake/GitDescription.cmake`,
`cmake/UpdateVersion.cmake`, `src/version.h.in`). Aucune option de compilation
n'y change.

### 4.2 Conditionnels de compilation dans les sources lues

> **Rectification de la V2.** La V2 déclarait `__APPLE__` et `__FreeBSD__`
> **absents** des fichiers lus. **C'était faux** : cette affirmation généralisait
> une recherche qui n'avait porté que sur deux fichiers. Les deux macros
> existent. L'inventaire ci-dessous est repris sur l'ensemble des fichiers
> déclarés lus au §3, emplacement par emplacement.

| Conditionnel | Fichier | Emplacement | Ce qu'il gouverne | Impact sur la concurrence — Debian 13 / aarch64 |
|---|---|---|---|---|
| `#ifdef __CYGWIN__` | `src/vcontrold.c` | ~40 | `#define XMLFILE`, `#define INIOUTFILE` — chemins par défaut | **aucun** ; branche non prise |
| `#ifdef __CYGWIN__` | `src/vcontrold.c` | ~193 | gabarit du fichier temporaire : `vitotmp-XXXXXX` contre `/tmp/vitotmp-XXXXXX` | **aucun** sur le mécanisme ; déplace seulement le fichier servant à `ftok` ; branche non prise |
| `#if defined (__FreeBSD__) \|\| defined(__APPLE__)` | `src/socket.c` | 25–27 | `#include <netinet/in.h>` | **aucun** ; une inclusion d'en-tête ; branche non prise |
| `#ifdef __CYGWIN__` | `src/socket.c` | 283–293 | contournement de `read()` dans `readn()`, Cygwin lisant plus que `count` | **aucun** ; branche non prise |
| `#if !defined(__APPLE__)` | `src/semaphore.c` | ~21–26 | définition de `union semun`, évitée sur macOS où elle existe déjà | **aucun** — déclaration de **type** ; ne touche ni le blocage, ni la clé, ni la valeur initiale. Branche **prise** sur Debian, et sans effet sémantique |
| `#ifdef __CYGWIN__` | `src/io.c` | 28–31 | `#define NCC NCCS`, `NCC` n'étant pas défini sous Cygwin | **aucun** ; branche non prise |
| `#ifdef NCC` | `src/io.c` | ~89 | boucle de remise à zéro des caractères de contrôle du terminal | **aucun** sur l'exclusion ; réglage local du tty |
| `#if defined(O_NONBLOCK)` | `src/io.c` | ~185, ~202 | `setnonblock()` / `setblock()` : `fcntl(F_SETFL)` sur le descripteur | **aucun** sur l'exclusion — appliqué **après** `open()`, il gouverne les lectures et `select`, jamais l'ouverture ni le sémaphore |

> **Conclusion, conservée parce qu'elle reste prouvée** : aucun de ces
> conditionnels ne modifie le modèle de concurrence sur Debian 13 / aarch64. Les
> branches Cygwin, FreeBSD et Apple ne sont pas prises ; celle de `semaphore.c`
> l'est, mais elle ne déclare qu'un type ; `NCC` et `O_NONBLOCK` règlent le
> terminal et le mode des lectures, en aval de toute exclusion.

> **Ce que cette rectification ne change pas.** L'inventaire était faux, la
> **conclusion** ne l'était pas : `B-1` portait sur la neutralité du build, qui
> reste établie. `N-1` portait sur la **preuve**, et c'est elle qui est refaite
> ici.

> **Fait amont, énoncé comme tel :** **aucune option de construction pertinente
> ne modifie le modèle de concurrence sur Debian 13 / aarch64.** Cette question
> **ne figure plus dans `H1`**.

### 4.3 Options d'invocation

Jeu complet relevé : `"c:d:gil:P:U:G:np:L:sx:vV46h"`. Seules les options ayant
un effet sur la question sont retenues.

| Option | Rôle | Effet | Valeur connue ? |
|---|---|---|---|
| `-n` / `--nodaemon` | `makeDaemon = 0` | **concurrence** — supprime le `fork` par connexion ; le service devient strictement séquentiel (§5, maillon 4) | **non** — fait d'installation, mais **sans conséquence** : les deux modes sont additifs |
| `-g` / `--debug` | `debug = 1` | **journal** — lève la suppression programmée des événements au-dessus de `LOG_NOTICE` (§10.1). **Décisif pour V-4**. Ce n'est **pas la seule route** : la configuration XML peut aussi l'activer (§10.1) | **non** — fait d'installation critique |
| `-s` / `--syslog` | `useSyslog = 1` | **journal** — destination : `syslog` plutôt qu'un fichier ; change la résolution d'horodatage (§10.4) | **non** — fait d'installation |
| `-l` / `--logfile` | fichier de journal | **journal** — destination fichier, format `[pid] ctime : message` | **non** — fait d'installation |
| `-x` / `--xmlfile` | jeu de commandes | **H3** — détermine quelles commandes existent, donc lesquelles atteignent Optolink | **non** — fait d'installation |
| `-d` / `--device` | périphérique | **H2** — désigne la liaison protégée | **non** — fait d'installation |
| `-P` / `--pidfile` | fichier de PID | **H2** — permet de constater l'instance en service | **non** — fait d'installation |

Les autres options — `-c`, `-i`, `-U`, `-G`, `-p`, `-L`, `-v`, `-V`, `-4`,
`-6`, `-h`, `--vsim` — sont sans effet sur la question et ne sont pas détaillées.

---

## 5. Chaîne causale `ADDITIF`

| # | Maillon | Preuve | Hypothèse | Statut |
|---|---|---|---|---|
| **1** | la sonde du superviseur emprunte le chemin `vclient` considéré | **dépôt** — W4-C §8 : « il sonde le démon par un appel `vclient` **direct** », et « la sonde du superviseur interroge `vclient` **directement**, et non le pont » | — | **ÉTABLI** |
| **2** | ce chemin demande la ressource Optolink pertinente | **aucune** — le dépôt ne nomme jamais la commande émise par la sonde | **H3** | **NON ÉTABLI → H3** |
| **3** | la ressource est **exclusive** entre clients concurrents | **amont** — `vcontrol_seminit()` appelé une fois dans `main()` **avant** la boucle d'acceptation ; sémaphore System V initialisé à `1` ; enfants de `fork()` héritant du `semid` ; accès au périphérique encadré par `semget`/`semrelease` | **H1, H2, H6** | **ÉTABLI** |
| **4** | un second demandeur **bloque** jusqu'à libération, sans service parallèle équivalent | **amont** — `sem_op = -1`, `SEM_UNDO`, **sans `IPC_NOWAIT`** ⇒ `semop` bloque. En mode `-n`, `main()` n'accepte le client suivant qu'après le retour de `interactive()` : l'attente est dans le backlog | **H1, H2, H6** | **ÉTABLI** |
| **5** | après libération, la sonde paie **son propre** coût | **amont** — le demandeur débloqué poursuit sur `framer_openDevice` puis l'exécution du bytecode sur le descripteur du périphérique | **H1** | **ÉTABLI** |
| **6** | aucun recouvrement pertinent n'invalide la composition temporelle de `C1` | **amont** — l'exclusion couvre toute l'utilisation du périphérique ; aucun service parallèle du périphérique n'existe | **H1, H2, H6** | **ÉTABLI** |

> **Le maillon 6 ne dépend plus de `H4`.** La V1 y attachait la brièveté des
> sessions tierces. C'était une confusion, corrigée au §7.2 : la durée d'une
> session ne conditionne pas l'**additivité**, seulement sa **bornabilité**.

> **Correction de l'affectation, aux maillons 4 et 6.** La V2 n'y portait pas
> `H2`. C'était une omission : `H2` énonce qu'aucun autre processus n'ouvre la
> liaison hors du mécanisme partagé (§7.4). Or un tel ouvrant **fournirait un
> service parallèle équivalent** — ce que le maillon 4 exclut — et **produirait un
> recouvrement** — ce que le maillon 6 exclut. Le maillon 6 acquiert pour la même
> raison `H6` : une exclusivité perdue par `semval > 1` (§9) est, elle aussi, un
> recouvrement. L'affectation par maillon devient donc : **1** aucune · **2**
> `H3` · **3** `H1/H2/H6` · **4** `H1/H2/H6` · **5** `H1` · **6** `H1/H2/H6`.
> **Le jeu global `H1/H2/H3/H6` est inchangé.**

> **Un seul maillon manquant suffirait à `INDÉTERMINÉ`** (cadrage §6.2). Ici le
> maillon 2 manque, mais **par défaut d'un fait d'installation** — d'où `H3`, et
> un niveau conditionnel plutôt qu'`INDÉTERMINÉ`.

---

## 6. Portée exacte de l'exclusion

La V1 disait « acquise jusqu'à la fin de session ». C'est trop grossier. La
portée réelle, lue dans `interactive()` :

| Moment | Code | Effet |
|---|---|---|
| **acquisition** | `if (fd < 0) { vcontrol_semget(); … framer_openDevice(…) }` | au **premier besoin** du périphérique, non à l'ouverture de session |
| **maintien** | tant que `fd >= 0` | l'exclusion couvre toutes les commandes suivantes de la session, sans réacquisition |
| **libération sur `close`** | `framer_closeDevice(fd); vcontrol_semrelease(); … fd = -1;` | **la session continue** ; l'exclusion est rendue |
| **réacquisition** | même test `if (fd < 0)` à la commande suivante nécessitant le périphérique | une session ayant fait `close` **réacquiert** si elle a de nouveau besoin de la liaison |
| **libération sur `quit`** | `framer_closeDevice(fd); vcontrol_semrelease(); return 1;` | fin de session |
| **libération sur erreur** | notamment échec d'ouverture, échec d'écriture socket | fin de session |
| **libération en fin de session** | `framer_closeDevice(fd); vcontrol_semrelease(); return 0;` | fin de session |

Le même schéma existe dans `readCmdFile()`, avec acquisition avant ouverture et
libération après fermeture.

> **Cette description est indissociable du §9 :** c'est précisément parce que la
> libération est possible **en cours de session**, et sans garde, que `H6`
> existe.

---

## 7. Hypothèses — ce qui entre, ce qui sort

### 7.1 `H1`, réduite à son résidu réel

> **`H1`** — le démon réellement déployé correspond au comportement amont
> caractérisé, **sans correctif local** modifiant les chemins de concurrence
> étudiés : boucle d'acceptation, sémaphore, ouverture et fermeture du
> périphérique.

Ne figurent **plus** dans `H1`, ayant été levés hors terrain : l'écart des cinq
commits (§3), les options de construction (§4.1), et les conditionnels de
plateforme (§4.2).

**Acte minimal** — constater la provenance du binaire déployé : paquet, dépôt de
compilation ou source, et l'absence de correctif sur les six fichiers dont les
empreintes sont données au §3.2.

### 7.2 `H4` — retirée du régime

La V1 en faisait une hypothèse de classification. C'était une erreur de
catégorie, que cette version corrige en nommant la distinction :

| | |
|---|---|
| **additivité structurelle** | les travaux se composent **séquentiellement**, par somme : un demandeur attend, puis paie son propre coût |
| **bornabilité quantitative** | cette somme admet une **borne assez basse** pour satisfaire `C1` |

Une session tierce longue mais **sérialisée** ne détruit pas l'additivité : elle
allonge l'attente, sans jamais la faire cesser d'être une attente. Elle peut en
revanche rendre le seuil de `C1` inatteignable.

> **La durée des sessions tierces n'est donc pas une hypothèse de régime.** Elle
> est une **limite quantitative**, consignée ici et **réservée au dimensionnement
> futur de V-2**, si celui-ci devient un jour pertinent. **V-2 n'est pas ouvert.**

La V2 cesse d'affirmer que des sessions brèves seraient nécessaires à la
classification `ADDITIF`.

### 7.3 `H5` — supprimée

Réinspection de `vcontrol_seminit()` : **tous** ses chemins d'échec terminent le
processus — `mkstemp` → `perror("mkstemp"); exit(1)` · `ftok` →
`perror("ftok"); exit(1)` · `initsem` → `perror("initsem"); exit(1)`. **Aucun
mode dégradé n'existe.** L'appel précède la boucle d'acceptation.

`vcontrol_semget()` et `vcontrol_semrelease()` terminent également le processus
sur échec de `semop`.

C5 §1 établit `vcontrold` **en service continu** sur l'installation de
référence.

> **Conséquence :** un démon qui **sert effectivement** a nécessairement franchi
> `seminit`. La disponibilité des sémaphores System V n'est donc plus un fait
> terrain à vérifier, et `H5` est **supprimée**. Les questions de robustesse du
> sémaphore hors du chemin étudié restent, s'il y a lieu, dans **`I1`**.

### 7.4 `H2` — élargie

La V1 la formulait « une seule instance de `vcontrold` ». Trop étroit : deux
faits amont montrent que l'invariant réel est plus large.

1. la clé du sémaphore provient d'un `mkstemp()` **par processus démon** — deux
   instances obtiennent donc des sémaphores **distincts**, sans exclusion
   mutuelle ;
2. l'ouverture du périphérique est `open(device, O_RDWR)`, **sans** `O_EXCL`,
   **sans** `ioctl(TIOCEXCL)`, **sans** `flock` ni `lockf` — **aucune exclusion
   périphérique secondaire n'existe**.

> **`H2`** — aucun autre processus concurrent n'ouvre la liaison pertinente en
> dehors du mécanisme d'exclusion partagé : ni une seconde instance de
> `vcontrold`, ni un processus tiers ouvrant le périphérique directement.

*Précision non normative :* la liaison protégée peut être locale ou TCP selon ce
que désigne `-d`. La formulation de `H2` est agnostique et couvre les deux cas
sans modification.

**Acte minimal** — constater les instances en service (le `pidfile` de `-P` y
aide) et l'absence d'autre ouvrant du périphérique désigné par `-d`.

### 7.5 `H3` — inchangée

> **`H3`** — la sonde du superviseur émet une commande qui **atteint** la liaison
> Optolink.

**Acte minimal** — lire la commande émise par le superviseur. *Indice non
probant :* son budget de 5 s est de l'ordre d'une lecture réelle (C5 §9 :
2 669–4 029 ms) et non d'un rejet local (~111 ms) — **c'est une inférence, pas
une preuve**, et le cadrage §6.1 interdit d'extrapoler.

---

## 8. Tableau de frontière amont / installation

| Fait | Amont prouvé | Installation prouvée | Hypothèse |
|---|---|---|---|
| exclusion System V bloquante, valeur initiale 1 | **oui** | non | H1 |
| `seminit` avant `fork`, `semid` hérité, sans mode dégradé | **oui** | non | H1 |
| additivité dans les deux modes d'invocation | **oui** | non | — |
| portée exacte de l'exclusion, réacquisition après `close` | **oui** | non | — |
| **libérations non appariées possibles** | **oui** | non | **H6** |
| **absence d'exclusion périphérique secondaire** | **oui** | non | H2, H6 |
| transférabilité `v0.98.12` → `8ca47972…` | **oui** | — | — |
| neutralité des options de construction sur Debian/aarch64 | **oui** | — | — |
| identité du démon déployé, absence de correctif | non | **non** | **H1** |
| absence d'un autre ouvrant de la liaison | non | **non** | **H2** |
| commande émise par la sonde | non | **non** | **H3** |
| absence de client provoquant une libération non appariée | non | **non** | **H6** |

---

## 9. Libérations non appariées — `H6`

### 9.1 Le fait, lu dans le code

`vcontrol_semrelease()` **ne vérifie pas** que le sémaphore était détenu :

```c
int vcontrol_semrelease()
{
    struct sembuf sb;
    logIT(LOG_INFO, "Process %d released lock", getpid());
    sb.sem_num = 0;
    sb.sem_op = 1;
    sb.sem_flg = SEM_UNDO;
    if (semop(semid, &sb, 1) == -1) { perror("semop"); exit(1); }
    return 1;
}
```

Et la branche `close` de `interactive()` libère **sans tester `fd >= 0`** :

```c
} else if (strstr(readBuf, "close") == readBuf) {
    framer_closeDevice(fd);
    vcontrol_semrelease();
    …
    fd = -1;
```

`framer_closeDevice()` ne comporte **aucune garde** `if (fd < 0)`. Deux commandes
`close` consécutives, sans commande périphérique intercalée, produisent donc
**deux incréments pour une seule acquisition**. Le chemin de fin de session
libère lui aussi inconditionnellement.

Le sémaphore étant initialisé à **1**, `semval` peut alors dépasser 1, et **deux
clients peuvent acquérir simultanément**.

### 9.2 Ce que `SEM_UNDO` répare, et ce qu'il ne répare pas

`SEM_UNDO` fait tenir au noyau un ajustement par processus, appliqué **à la
terminaison du processus**. Un enfant ayant libéré une fois de trop voit donc son
excédent défait — **mais seulement quand il se termine**.

> **La fenêtre reste ouverte entre la libération excédentaire et la fin du
> processus.** En mode `fork`, cette fenêtre est la fin de la session fautive.
> Pendant tout cet intervalle, l'exclusivité peut être perdue.

### 9.3 Aucune exclusion de secours

`open(device, O_RDWR)` sans `O_EXCL`, sans `TIOCEXCL`, sans `flock` : si
l'exclusivité du sémaphore est perdue, **rien d'autre ne bloque** l'accès
concurrent au périphérique.

### 9.4 Pourquoi ce n'est **pas** un verdict `NON ADDITIF`

| | |
|---|---|
| **le fait** | le code **contient** une possibilité de perdre l'exclusivité si `semval` est gonflé par des libérations non appariées |
| **mais** | son activation dépend d'un **comportement de client tiers**, hors de la population protégée |
| **or** | la population étudiée — `vclient` invoqué avec une commande, puis terminaison — **ne produit pas** ce chemin : elle n'envoie pas deux `close` |

> Au sens du cadrage §6.3, il n'existe donc **aucune preuve positive de
> `NON ADDITIF` sur les sondes du superviseur elles-mêmes**. Un **risque
> conditionnel n'est pas un verdict**. La conséquence correcte est que `ADDITIF`
> reste **conditionnel à `H6`**.

> **`H6`** — aucun client concurrent ne provoque, pendant la fenêtre étudiée, un
> chemin de libération non apparié élevant `semval` au-dessus de la valeur qui
> assure l'exclusivité.

**Rattachement** : maillons **3**, **4** et **6** (§5). **Acte minimal** — constater le
comportement des clients tiers, ou observer les séquences
`tries to aquire / got lock / released lock` du journal, si celui-ci existe
(§10).

---

## 10. Journal — V-4, refait

### 10.1 La porte `debug` — le fait décisif

`src/common.c`, dans `logIT()` :

```c
if (! debug && (class  > LOG_NOTICE)) {
    free(print_buffer);
    return;
}
```

avec, dans le même fichier :

```c
int debug = 0;
```

et, dans `initLog()` : `debug = debugSwitch;`.

> **Ce n'est pas un filtre `syslog` externe.** C'est le **programme** qui écarte
> l'événement : lorsque `debug` vaut 0, une entrée `LOG_INFO` **n'est jamais
> émise**, ni vers `syslog`, ni vers un fichier. Aucun réglage de collecte en
> aval ne peut la récupérer, parce qu'elle n'a pas été produite.

**Deux routes mènent à `debug`, et la V2 n'en nommait qu'une.**

| Route | Code | Précédence |
|---|---|---|
| ligne de commande | `-g` / `--debug` → `debug = 1` ; la table `long_options` porte aussi `{"debug", no_argument, &debug, 1}` | appliquée en premier |
| **configuration XML** | `src/vcontrold.c`, ~781–786 : `if (! debug) { debug = cfgPtr->debug; }`, suivi immédiatement de `initLog(useSyslog, logfile, debug)` | **n'agit que si la ligne de commande n'a pas déjà activé** `debug` |

`debug` **vaut 0 par défaut**, et sa valeur effective peut donc provenir de l'une
ou l'autre route selon la configuration du site. C'est pourquoi l'acte A (§13)
demande de lire **l'invocation *et* la configuration**, non l'une seule.

### 10.2 Le PID — la V1 avait tort

| Destination | Forme | PID ? |
|---|---|---|
| `syslog` | `openlog("vito", LOG_PID, LOG_LOCAL0)` | **oui**, par `LOG_PID` |
| fichier | `fprintf(logFD, "[%d] %s: %s\n", pid, tPtr, print_buffer)` | **oui**, en tête entre crochets |

> **Correction explicite.** La V1 écrivait que « l'appariement ne peut se faire
> que par le descripteur ». **C'est faux** : le PID est présent dans les deux
> destinations.

**Ce que le PID permet réellement**, et ses limites :

| Mode | Ce que le PID vaut |
|---|---|
| **par défaut** (`fork` par connexion) | chaque connexion est servie par un **enfant distinct** : le PID corrèle sans ambiguïté les événements d'une même connexion et d'une même détention de verrou |
| **`-n`** | **aucun `fork`** : tous les événements portent le PID du démon unique. Le PID **ne discrimine plus rien** — mais dans ce mode il n'y a pas non plus de concurrence à démêler |

Le PID n'est pas sur-vendu : il corrèle **au sein d'un même mode**, et seulement
si les événements concernés sont émis (§10.1).

### 10.3 Inventaire des événements

| Événement | Fichier | Symbole | Niveau | Message | Éléments portés |
|---|---|---|---|---|---|
| client connecté | `socket.c` | `listenToSocket` | **`LOG_NOTICE`** | `"Client connected %s:%s (FD:%d)"` | hôte, service, FD |
| enfant démarré | `socket.c` | `listenToSocket` | `LOG_INFO` | `"Child process started with pid %d"` | PID de l'enfant |
| attente du verrou | `semaphore.c` | `vcontrol_semget` | `LOG_INFO` | `"Process %d tries to aquire lock"` | PID |
| verrou obtenu | `semaphore.c` | `vcontrol_semget` | `LOG_INFO` | `"Process %d got lock"` | PID |
| verrou relâché | `semaphore.c` | `vcontrol_semrelease` | `LOG_INFO` | `"Process %d released lock"` | PID |
| ouverture périphérique | `framer.c` | `framer_openDevice` | `LOG_INFO` | `">FRAMER: open device %s ProtocolID %02X"` | périphérique, protocole |
| périphérique ouvert | `framer.c` | `framer_open_p300` | `LOG_INFO` | `">FRAMER: opened"` | — |
| périphérique fermé | `framer.c` | `framer_close_p300` | `LOG_INFO` | `">FRAMER: closed"` | — |
| **commande reçue** | `vcontrold.c` | `interactive`, ~277 | **`LOG_INFO`** | `"Command: %s"` | **la commande émise par le client** |
| commande transmise et acquittée | `framer.c` | `framer_send`, 300 | `LOG_INFO` | `">FRAMER: Command send"` | — ; marque l'instant où la commande est **écrite au périphérique puis acquittée** |
| connexion fermée | `socket.c` | `closeSocket` | `LOG_INFO` | `"Closed connection (fd:%d)"` | FD seul |
| **fin de processus enfant** | `vcontrold.c` | `main`, ~967, **sous `if (makeDaemon)`** | **`LOG_INFO`** | `"Child process with PID %d terminated"` | **PID de l'enfant** |

> **Rectification de la V2 — `"Command: %s"`.** La V2 déclarait son niveau « non
> relevé » et affirmait que rien ne s'appuyait dessus. **Les deux points étaient
> faux.** Le niveau est **`LOG_INFO`** (`vcontrold.c` ~277), il subit donc la
> porte `debug` au même titre que les autres ; et cet événement est précisément
> **le seul du journal amont qui porte la commande émise** — c'est-à-dire la
> grandeur dont dépend `H3`, et que l'acte B du §13 vient chercher.

> **`"Child process with PID %d terminated"` complète le cycle.** Émis dans
> `main()` après le retour de `interactive()` et la fermeture de la socket, il ne
> l'est **que sous `makeDaemon`** — donc uniquement en mode `fork`. Avec le PID,
> il ferme la séquence d'un enfant : connexion, verrou, travail, libération,
> terminaison.

> **Ce que l'inventaire change.** Le journal amont sait produire la séquence
> complète **attente → obtention → travail → libération**, portée par le PID.
> C'est bien plus que ce que la V1 décrivait. Mais **tout cela est à
> `LOG_INFO`**, donc **conditionné à `debug`** : seul « client connecté » est à
> `LOG_NOTICE` et survit sans lui.

### 10.4 Faits amont, faits d'installation

**Faits amont** — ce que la source sait produire, et sous quelle condition :

- la séquence de verrou complète, avec PID, **si et seulement si `debug` est
  actif** ;
- la connexion cliente, avec hôte et service, **inconditionnellement** ;
- la fermeture de connexion, avec le FD seul, **sous `debug`** ;
- en sortie fichier, un horodatage issu de `ctime()`, donc **à la seconde**.

**Faits d'installation** — non établis, et non établissables ici :

`debug` réellement actif · destination réelle (`syslog` ou fichier) · format
réellement produit · **résolution réelle d'horodatage** · rotation ·
conservation · attribution effective.

### 10.5 La contrainte de résolution reste **non prouvée**

W4-F1 §8.5 exige, pour que `C1` soit calculable, une résolution `r < 0,485 s`.

| Destination | Résolution amont | Verdict |
|---|---|---|
| fichier | `ctime()` → **la seconde** | **échoue** la contrainte, par construction |
| `syslog` | déterminée par l'implémentation en aval, non par ce code | **inconnue** — fait d'installation |

> **`r < 0,485 s` reste NON PROUVÉ.** La sortie fichier ne peut pas la
> satisfaire ; la sortie `syslog` le pourrait selon l'implémentation, ce que ce
> lot ne peut pas établir.

> **Ce rapport ne rend ni T0-A, ni T0-B.** Il caractérise ce que la source sait
> produire ; ce que l'installation produit reste entièrement à T0-A, et T0-B
> demeure gouverné par sa précondition (W4-F1 §8.2).

---

## 11. Niveau épistémique

> **`PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION`**
>
> **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`**

`PROUVÉ INCONDITIONNELLEMENT` est exclu : quatre hypothèses d'installation
subsistent. `INDÉTERMINÉ` est écarté : elles sont **nommées, falsifiables et
rattachées à un maillon**, ce que le cadrage §11.8 distingue du cas où l'on ne
sait pas même les énoncer.

---

## 12. `U-1` / `I1`

Statuts **dérivés** de la table canonique du cadrage §11.7.2, ligne
« `PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION` » :

| | |
|---|---|
| **`U-1`** | `PART AMONT ÉTABLIE SOUS H1/H2/H3/H6, RÉSIDU D'INSTALLATION OUVERT` |
| **`I1`** | `PARTIELLEMENT RÉDUITE` |

> **`U-1 CLOSED` n'est pas écrit** : une fermeture conditionnelle n'est pas une
> fermeture. **`I1 CLOSED` ne l'est pas davantage** : l'inclusion `I1 ⊃ U-1` est
> stricte, et restent entières la robustesse sous concurrence, les erreurs, les
> refus, les corruptions éventuelles et les signatures d'échec.

---

## 13. Besoin suivant — minimal

La V1 annonçait « cinq constats, tous terrain ». Après avoir levé hors terrain
tout ce qui l'était — l'écart de version, les options de construction, la
plateforme, et `H5` — le besoin réel se réduit à **deux actes en lecture,
ordonnés**.

### Acte A — constat de l'installation du démon

Provenance du binaire et absence de correctif · invocation effective, dont `-n`,
`-g`, `-x`, `-d`, `-P` · configuration · instance(s) en service · fichier de PID
le cas échéant · valeur effective de `debug`.

**Réduit** : `H1`, `H2` — et, si l'invocation du superviseur est lisible au même
titre, `H3`. **Détermine** en outre si le journal utile **peut exister**, ce dont
dépend l'utilité de l'acte B.

### Acte B — constat des journaux réellement produits

**Seulement si** l'acte A montre que le journal utile existe. Commande du
superviseur · séquences `tries to aquire / got lock / released lock` ·
comportement des clients tiers · occupation réelle · éléments de V-4.

**Réduit** : `H3`, `H6`. **Caractérise** les possibilités réelles de T0-A.

> **Ces deux actes sont des constats en lecture sur l'installation. Ils exigent
> du terrain.** Ce rapport le **constate** et s'arrête là. Il **ne donne aucune
> commande**, **ne rédige aucun protocole d'exécution**, **ne contacte rien**,
> **ne prépare pas T0**, et **ne demande aucune autorisation** — ni
> explicitement, ni implicitement. Décider si, quand et comment ces constats
> seront faits est un acte humain distinct.

> **Ni V-2 ni V-3 n'est désigné comme prochain acte**, le cadrage §11.7.1 le
> réservant au seul niveau inconditionnel. À titre de **conséquence
> conditionnelle** : si `H1/H2/H3/H6` étaient établies, le régime serait
> `ADDITIF`, ce qui appellerait la branche **A** de W4-F1 §8.2.1 et donc **V-2**.
> Conséquence suspendue à quatre hypothèses non établies.

### 13.1 Ce qui reste fermé

`W4-F2` · `T0`, `T1`, `T2` · toute autorisation terrain · `W4-F3`, `W4-F4` ·
`V-2`, `V-3` · l'autorité de la surface transactionnelle.

**Rien de ce rapport ne satisfait la condition 4 de `T0 GO`** : elle porte sur
**T0-B**, que W4-F1 §8.2 subordonne à la précondition journal de T0-A. Une preuve
amont ne s'y substitue pas.

---

## 14. Preuve rejouable — les dix-sept exigences

| # | Exigence | Statut | Preuve |
|---|---|---|---|
| 1 | amont exact | **satisfaite** | §3 — `openv/vcontrold` |
| 2 | URL | **satisfaite** | §3 |
| 3 | étiquette **ou** commit complet | **satisfaite** | §3 — étiquette `v0.98.12` **et** son commit `a17067d5dcffda66f63515f2415fa44c3705ac68` |
| 4 | fichiers | **satisfaite** | §3 — sept fichiers |
| 5 | lignes ou symboles | **satisfaite** | §3 — vingt symboles ; extraits cités aux §4, §6, §9, §10, avec **emplacements** pour les conditionnels (§4.2) et pour les douze événements de journal (§10.3) |
| 6 | options de construction pertinentes | **satisfaite** | §4.1 et §4.2 — caractérisées, et déclarées neutres sur Debian/aarch64 |
| 7 | options d'exécution et d'invocation | **satisfaite** | §4.3 — sept options pertinentes, effets et statut |
| 8 | plateforme, ou hypothèses de plateforme | **satisfaite** | §4.2 — conditionnels inventoriés ; Debian 13 / aarch64 par C5 §1 |
| 9 | population étudiée | **satisfaite** | §2 — sondes du superviseur, et elles seules |
| 10 | chaîne causale maillon par maillon | **satisfaite** | §5 — six lignes |
| 11 | faits amont séparés des hypothèses | **satisfaite** | §8 — tableau à quatre colonnes |
| 12 | procédure de toute reproduction locale | **satisfaite** | §15 — **aucune reproduction conduite**, motif donné |
| 13 | artefacts employés | **satisfaite** | §3 — sept fichiers source et deux points d'API d'arbre ; aucune compilation |
| 14 | résultats | **satisfaite** | §1, §5, §9, §10 |
| 15 | limites | **satisfaite** | §4.1 (`pthread` lié mais inutilisé) · §7 (chaque hypothèse) · §9.2 (fenêtre laissée ouverte par `SEM_UNDO`) · §10.2 (limite du PID en `-n`) · §10.5 (`r < 0,485 s` non prouvé) |
| 16 | verdict, conditionnel ou inconditionnel | **satisfaite** | §11 — **conditionnel**, explicitement |
| 17 | ce qui reste inconnu | **satisfaite** | §7 (H1, H2, H3) · §9.4 (H6) · §10.4 (faits d'installation du journal) · §12 (résidu de `I1`) |

> **17 / 17.** Trois exigences ont été portées à satisfaction au fil des
> versions. Les points **3** et **6** l'ont été en V2 : le commit de l'étiquette
> est relevé et l'écart jusqu'au commit observé est levé (§3) ; les options de
> construction sont caractérisées et déclarées neutres (§4.1). Le point **5** l'est
> en **V3** : l'audit delta l'avait rétrogradé parce que la V2 contenait deux
> affirmations que le source contredisait — l'absence prétendue de `__APPLE__` et
> `__FreeBSD__` (§4.2), et le niveau prétendument non relevé de `"Command: %s"`
> (§10.3). Les deux sont corrigées, et l'inventaire porte désormais les
> **emplacements**, ce qui le rend vérifiable ligne à ligne.

> **Une exigence de preuve rejouable ne se déclare pas satisfaite quand le source
> contredit le document.** C'est ce qui a fait tomber le point 5 à l'audit delta,
> et c'est la raison pour laquelle la V3 refait l'inventaire plutôt que de
> corriger deux phrases.

---

## 15. Voie 2

**Non employée.**

Le cadrage §11.4 la réserve au cas où l'analyse statique amont laisse une
ambiguïté qu'une reproduction locale hors terrain peut réellement lever.
L'analyse statique a été **concluante sur tout ce qu'elle pouvait atteindre** :
l'exclusion, son caractère bloquant, son partage entre enfants, sa portée exacte,
ses libérations non appariées, l'absence d'exclusion périphérique secondaire,
l'additivité des deux modes d'invocation, la neutralité des options de
construction, et la structure complète du journal.

Les hypothèses restantes sont **toutes** des faits d'**installation** : aucune
compilation locale de l'amont ne dirait ce que le site a déployé, comment il
l'invoque, ni ce que son superviseur envoie. Employer la voie 2 aurait produit un
artefact sans valeur probatoire sur les questions restantes — et le cadrage
§11.4 interdit précisément de conclure sur une propriété que le harnais aurait
lui-même fabriquée.

**Aucun artefact temporaire n'a été créé, et rien n'est à nettoyer de ce chef.**

---

## 16. Ce que ce document ne fait pas

- il ne rend **aucun** verdict `T0-B`, ni `T0-A` ;
- il ne produit **aucun** `T0 GO` ;
- il n'ouvre **ni** W4-F2, **ni** V-2, **ni** V-3 ;
- il ne demande **aucune** autorisation terrain, ni explicitement ni
  implicitement ;
- il ne modifie **ni** W4-F0, **ni** W4-F1, **ni** le cadrage W4-F1A ;
- il ne livre **aucun** code, test, configuration ni instrumentation ;
- il ne transforme **aucune** hypothèse en fait, et ne transforme **aucun risque
  conditionnel en verdict**.

**W4-F2 reste FERMÉ. Le pont historique reste l'unique écrivain réel de
production.**
