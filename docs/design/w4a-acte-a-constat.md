# ACTE A — constat terrain en lecture

> **Objet gelé, hors dépôt.** Ce document est le constat de l'Acte A du chantier
> W4-F1A. Il est autoportant : il n'exige la lecture d'aucun autre rapport.
>
> Il ne décide d'aucune intégration au dépôt, n'ouvre aucun acte suivant, et ne
> vaut aucune autorisation.

---

## 1. Autorisation

**Acte A autorisé explicitement par l'humain**, limité au constat en lecture
passive sur l'installation réelle du démon `vcontrold`.

**Opérations interdites, et non effectuées** : aucun `vclient` exécuté · aucune
commande Optolink · aucune lecture chaudière · aucune écriture chaudière · aucun
publish MQTT · aucun `restart`, `reload`, `stop` ni `start` · aucun
`daemon-reload` · aucun fichier système modifié · aucun XML, pidfile ou journal
modifié · aucun paquet installé · aucune compilation sur l'hôte · aucun
déploiement · aucune seconde instance lancée · aucun client de test · aucune
concurrence provoquée · aucun probe réseau actif · **Acte B non exécuté** · aucun
T0 préparé.

**Deux précautions de méthode.** Le binaire du démon n'a **pas** été exécuté : sa
version a été lue par `strings`, le fichier n'étant pas *stripped*. Le dépôt Git
présent sur l'hôte a été interrogé avec `--no-optional-locks`, qui interdit toute
écriture d'index.

---

## 2. État Git avant terrain

`main` @ `ef227a016bd66d21714c5a04dab616ca92adfcda` = `origin/main`, ahead 0 /
behind 0, working tree **propre**, `stash@{0}` W3 intact, 1 worktree. Les deux
documents gouvernants — le cadrage `w4f1a-vcontrold-concurrency.md` et la
caractérisation `w4f1a-upstream-characterization.md` — vérifiés à leurs
empreintes attendues.

---

## 3. Host réel

| | |
|---|---|
| hostname | `boiler-bridge` |
| OS | Debian GNU/Linux 13 (trixie) |
| architecture | `aarch64`, noyau `6.12.47+rpt-rpi-v8` |
| rôle | hôte du démon `vcontrold` et du pont historique |

**Concordance avec C5 §1** — « Debian 13, aarch64 » : l'installation examinée est
bien celle pertinente pour W4-F1A.

---

## 4. Daemon

| | |
|---|---|
| processus | **un seul** |
| PID | `691`, **PPID 1** |
| enfants | **aucun** — `TasksCurrent=1` |
| executable | `/proc/691/exe` → `/usr/sbin/vcontrold` |
| utilisateur | `nobody` |
| invocation | **`/usr/sbin/vcontrold -n -p 3002`** |
| uptime | depuis 2026-08-07, 16 j 23 h au moment du constat |

**Mode : `-n`.** Pas de `fork` par connexion. Le service est **strictement
séquentiel** : `main()` n'accepte la connexion suivante qu'après retour de
`interactive()`.

> Il n'y a **ni enfants de connexion, ni instances indépendantes** — un unique
> processus, confirmé par `TasksCurrent=1` et par `pgrep -c` = 1.

---

## 5. Service

`vcontrold.service`, unité **locale** `/etc/systemd/system/vcontrold.service`,
`enabled`, active depuis 2026-08-07.

```
ExecStart=/usr/sbin/vcontrold -n -p 3002
Restart=always
RestartSec=5
User=root
```

L'unité déclare `User=root` ; le processus tourne en `nobody` — abandon de
privilèges par le démon lui-même, conforme au XML (`<username>nobody</username>`,
`<groupname>dialout</groupname>`).

**`-n` est persisté dans l'unité** : le mode survit aux redémarrages.

**Aucune modification effectuée** — seuls `status`, `cat`, `show`, `list-units`
et `list-timers` ont été employés.

---

## 6. Provenance du binaire

| | |
|---|---|
| chemin | `/usr/sbin/vcontrold` |
| SHA-256 | `1341e240a3b07abdcfb0aee51d8a4e2e7815d82e6a1634321a03d1127d0d7e91` |
| identique au binaire en cours | **oui** — `sha256sum /proc/691/exe` rend la même valeur |
| taille / date | 149 040 o, 2026-03-17 |
| type | ELF 64 PIE aarch64, **non *stripped***, BuildID `d3309abd6f781a72deae786123357af73a998e0c` |
| paquet Debian | **aucun** — `dpkg -S` ne trouve aucun paquet propriétaire : installation locale |
| version compilée | **`0.98.12-5-g8ca4797`**, lue par `strings`, **sans exécuter le binaire** |

**Dépôt source local** `/home/pi/vcontrold` :

| | |
|---|---|
| HEAD | **`8ca47972c9ac5b0a14a7a36393b0dbfdb165f918`** |
| `describe --tags --dirty` | `v0.98.12-5-g8ca4797` — **sans suffixe `-dirty`** |
| `status --porcelain` | **vide** — arbre propre |

**Blobs des six fichiers portant le comportement caractérisé**, comparés aux
empreintes amont relevées lors de la caractérisation :

| fichier | blob local | amont | |
|---|---|---|---|
| `src/vcontrold.c` | `d2adee6d…` | `d2adee6d…` | **identique** |
| `src/socket.c` | `ac97fa0d…` | `ac97fa0d…` | **identique** |
| `src/semaphore.c` | `33d8ffd7…` | `33d8ffd7…` | **identique** |
| `src/common.c` | `00b87df7…` | `00b87df7…` | **identique** |
| `src/io.c` | `29e698bb…` | `29e698bb…` | **identique** |
| `src/framer.c` | `31c4f880…` | `31c4f880…` | **identique** |

**Éléments en faveur** : version compilée = commit caractérisé · arbre local
propre à ce commit exact · six blobs identiques à l'amont · aucune option de
construction ne pouvant altérer le modèle de concurrence.

**Limite, et elle est réelle** : rien ne prouve **passivement** que le binaire de
mars ait été compilé depuis *cet* arbre dans *cet* état. Un arbre sale au moment
de la compilation, nettoyé depuis, rendrait la même chaîne de version. Le lever
exigerait une compilation comparative sur l'hôte — **interdite**.

---

## 7. Invocation effective

| Option | Valeur effective | Preuve | Impact |
|---|---|---|---|
| `-n` | **présente** | ligne de commande et `ExecStart` | **service séquentiel**, pas de `fork` |
| `-g` / `--debug` | **absente** | ligne de commande | n'active pas `debug` |
| `-s` | **absente** | ligne de commande | destination non forcée en syslog |
| `-l` | **absente** | ligne de commande | fichier de journal non forcé par la ligne de commande |
| `-x` | **absente** | ligne de commande | XML par défaut `/etc/vcontrold/vcontrold.xml`, **présent** |
| `-d` | **absente** | ligne de commande | device pris du XML |
| `-P` | **absente** | ligne de commande | **aucun pidfile** |

`-p 3002` est présente : port d'écoute TCP du démon.

---

## 8. Configuration effective

Fichier réellement référencé : `/etc/vcontrold/vcontrold.xml` (17 132 o,
2026-03-17), **confirmé effectif** par l'absence de `-x` et par la concordance de
tous ses paramètres avec l'état observé.

| Élément | Valeur |
|---|---|
| device | `<serial><tty>/dev/ttyUSB0</tty></serial>` — **liaison locale, non TCP** |
| port | `<net><port>3002</port></net>` |
| journal | `<logging><file>/home/pi/vcontrold.log</file>` |
| syslog | `<syslog>n</syslog>` |
| **debug** | **`<debug>n</debug>`** |
| privilèges | `nobody` / `dialout` |
| device ID | `20CB` |

**Corroboré par les descripteurs ouverts du PID 691** : fd 3 →
`/home/pi/vcontrold.log` (écriture seule) · fd 6 → `/dev/ttyUSB0`
(lecture-écriture) · fd 4 → socket d'écoute · fd 1 et 2 → socket journald.

---

## 9. Debug

| Route | Valeur | Preuve |
|---|---|---|
| ligne de commande | **non activé** | `-g` / `--debug` absentes de `ExecStart` et de la ligne de commande |
| XML | **`n`** | `<logging><debug>n</debug></logging>` |

Précédence amont : `if (! debug) { debug = cfgPtr->debug; }` — la ligne de
commande n'ayant rien activé, la valeur XML s'applique.

> **`debug` effectif = `false`.**

C'est la sortie majeure de l'Acte A : **pour le fichier de journal et pour
syslog**, le programme lui-même écarte tout événement au-dessus de `LOG_NOTICE`
— aucun réglage de collecte en aval ne peut le récupérer, l'événement n'étant pas
produit vers ces puits.

> **Réserve d'inventaire, sans incidence sur ce résultat.** Une voie distincte
> existe vers les mêmes événements : `debug on` **en session** arme
> `setDebugFD(socketfd)`, et l'émission se fait **en amont de la porte**, vers la
> socket du **client demandeur**, préfixée `DEBUG:`. Elle n'écrit pas la variable
> `debug`, n'atteint **ni le fichier ni syslog**, et est remise à zéro à chaque
> session. Elle ne change donc rien à « `debug` effectif = `false` » ni au constat
> du §10.

---

## 10. Journal

| | |
|---|---|
| destination | **fichier**, `/home/pi/vcontrold.log` — pas syslog |
| existence | oui, 477 848 600 o (≈ 456 Mio), écrit à l'instant du constat |
| accessibilité | `-rw-rw-r-- nobody:dialout` — lisible |
| format | `[691] Mon Aug 24 19:25:02 2026 : Client connected 127.0.0.1:48426 (FD:5)` |
| résolution d'horodatage | **la seconde** — `ctime()`, aucune sous-seconde |
| **`LOG_INFO` produits ?** | **NON** |

**Vérification d'existence** — recherche de simple présence sur les 200 000
dernières lignes, **sans aucune analyse de séquence** :

| événement | niveau amont | occurrences |
|---|---|---|
| `Client connected` | `LOG_NOTICE` | **199 628** |
| `got lock` | `LOG_INFO` | **0** |
| `tries to aquire` | `LOG_INFO` | **0** |
| `released lock` | `LOG_INFO` | **0** |
| `Command:` | `LOG_INFO` | **0** |
| `Closed connection` | `LOG_INFO` | **0** |
| `FRAMER` | mixte | 2 — nécessairement les variantes `LOG_ERR` |

**Le terrain confirme exactement la prédiction amont** : ouvertures de connexion
seules, **aucune fermeture**, aucune séquence de verrou, aucune commande. La
résolution à la seconde confirme par ailleurs que la contrainte `r < 0,485 s`
**ne peut pas** être satisfaite par ce puits.

> **Acte B techniquement possible : NON.** **Aucune analyse Acte B n'a été
> conduite.** Le sondage de queue a servi au format et à l'existence des types
> d'événements. Il a incidemment rendu visible une cadence de connexions de
> quelques secondes ; elle **n'est ni exploitée ni interprétée** — cela relèverait
> de l'Acte B.

---

## 11. Instance et autres ouvrants

| | |
|---|---|
| instances `vcontrold` | **une** — PID 691, PPID 1, unité systemd unique |
| enfants vs instances | **aucun enfant** ; `TasksCurrent=1` ; `-n` exclut le `fork` par connexion |
| device réel | **`/dev/ttyUSB0`**, tty local — **pas** `host:port` |
| détenteurs du device | **PID 691 seul**, établi par **deux méthodes indépendantes** : `fuser -v` et balayage `/proc/*/fd` |
| clients connus | `boiler_bridge.service` (pont) et `boiler-guard.timer` → `boiler-guard.service` (superviseur, `OnUnitInactiveSec=3min`) — **connus par configuration**, non observés en train d'exécuter |
| mode d'accès déclaré | `vclient` → **TCP 127.0.0.1:3002** pour l'un et pour l'autre, jamais le tty directement. **Témoin : la configuration lue** — `boiler_guard.sh` pour le superviseur, le source du pont pour le pont. **Aucun témoin d'exécution** ne rattache ce mode d'accès à l'une ou l'autre unité |
| connexion active au constat | `vclient` pid 911617 ↔ `vcontrold` pid 691 — une seule paire. **Commanditaire non établi** : cette paire n'est rattachée à aucune des deux unités |

**Portée exacte** : ces observations sont **instantanées**. Elles n'établissent
pas qu'aucun autre processus n'ouvre jamais la liaison — seulement qu'aucun ne la
tenait à cet instant.

**Deux registres, à ne pas confondre.** L'instance unique, les détenteurs du
device et la paire `vclient` ↔ `vcontrold` relèvent de l'**observation**. Le
mode d'accès des deux clients connus relève de la **configuration lue** : aucun
témoin n'établit qu'une de ces deux unités ait exécuté `vclient` pendant le
constat. C'est exactement le registre sur lequel les transitions 1 et 2 du §12.2
sont cotées « non observée », et il est traité ici de la même manière.

---

## 12. Hypothèses après Acte A

| Hyp. | Avant | Faits Acte A | Après | Justification |
|---|---|---|---|---|
| **H1** | OUVERTE | binaire = `/proc/691/exe`, version compilée `0.98.12-5-g8ca4797` ; dépôt local **propre** à ce commit exact ; **six blobs identiques** à l'amont ; aucun paquet propriétaire | **PARTIELLEMENT RÉDUITE** | l'arbre déployé est exempt de correctif sur les six fichiers portants. Résidu : le lien binaire ↔ arbre au moment de la compilation n'est pas prouvable passivement |
| **H2** | OUVERTE | une instance ; `/dev/ttyUSB0` détenu par PID 691 seul, deux méthodes ; liaison **locale** ; les deux clients connus passent par TCP 3002 | **PARTIELLEMENT RÉDUITE** | aucun autre ouvrant à cet instant, et aucun chemin connu vers le tty. Résidu : une observation instantanée ne vaut pas absence historique ni future. **Ce résidu absorbe celui de H6** |
| **H3** | OUVERTE | `VCLIENT_CMD="getTempKist"`, `VCLIENT_HOST="localhost"`, `VCLIENT_PORT="3002"`, `VCLIENT_TIMEOUT=5`, lus dans `/home/pi/boiler-bridge/boiler_guard.sh` ; la sonde exige une valeur numérique dans 0–100 | **PARTIELLEMENT RÉDUITE** | **Établi** : la commande **configurée** est `getTempKist`, et le contrôle de plage montre que la sonde *attend* une grandeur physique. **Non établi** : que `getTempKist` **résolve** dans le jeu de commandes du XML **déployé** pour le device `20CB` ; et qu'elle **atteigne** la liaison. **Maillon 2 : NON ÉTABLI** |
| **H6** | OUVERTE | `-n` persisté dans l'unité ; instance unique ; sérialisation confirmée pour **tous** les clients TCP du démon, connus ou non ; les deux clients invoquent `vclient` en one-shot ; le pont sérialise en outre par un verrou interne | **RÉDUITE, NON CLOSE** | `-n` **masque la conséquence** — deux clients du démon ne peuvent être servis simultanément — mais **n'établit pas le contenu** de H6. Voir ci-dessous |

### 12.1 Pourquoi `H6` n'est pas close

`-n` décharge légitimement le maillon 4, et le maillon 3 est acquis pour les
clients du démon. Trois faits interdisent d'aller plus loin.

1. **Le chemin de libération non appariée reste ouvert, et il ne dépend pas de
   `quit`.** **Tous** les chemins de sortie de `interactive()` appellent
   `vcontrol_semrelease()` sans aucune vérification de détention : la branche
   `quit`, les échecs d'écriture vers le client, et la sortie de boucle en fin de
   fonction. Une session close **sans** `quit` produit donc la même libération.
   Le cas qui illustre le chemin — un `vclient` one-shot dont la commande est
   rejetée avant Optolink — passe effectivement par `quit` : le serveur répond
   `ERR: command unknown`, chaîne fixe et sans substitution, puis le prompt ; le
   client enregistre l'erreur et poursuit jusqu'à un retour non nul, si bien que
   `disconnectServer()`, seul émetteur de `quit`, est atteint. Mais la conclusion tient **a fortiori** —
   elle ne repose pas sur cette émission.
2. **Le mécanisme d'exclusion n'est pas interne au processus.** C'est un ensemble
   de sémaphores **System V**, objet IPC du noyau, en mode `0666`, dont la clé
   est dérivée par `ftok()` sur un fichier `/tmp` jamais délié. Un participant
   **extérieur au démon** peut donc agir sur `semval`, indépendamment de `-n`.
3. **Sous `-n`, la réparation par `SEM_UNDO` change de borne.** `SEM_UNDO` est un
   ajustement par processus, appliqué à la **terminaison du processus**. Sans
   enfant, le processus qui libère en trop est le démon lui-même : la fenêtre
   cesse d'être bornée par la session et devient bornée par **la vie du démon**.

Le maillon 6 garde en conséquence une voie ouverte vers le recouvrement : un
**second ouvrant du périphérique**, `open(device, O_RDWR)` étant sans `O_EXCL`,
`TIOCEXCL` ni `flock`. Cette voie est exactement **H2**, qui demeure ouverte.
Le **résidu de H6 est donc absorbé dans celui de H2**.

> **Sur le verrou interne du pont.** Le fait est **exact et observé** — le pont
> sérialise ses propres appels `vclient` par un verrou interne. Il est cependant
> **non porteur** pour la réduction de H6 : sous `-n`, le démon sérialise déjà
> tous ses clients, et le résidu qui subsiste vient d'un participant extérieur au
> démon, que ce verrou ne gouverne pas. Il est conservé ici comme constat, non
> comme argument.

### 12.2 Le maillon 2, transition par transition

Cinq transitions séparent la valeur configurée de l'atteinte effective de la
liaison. **Aucune n'est observée.**

| # | Transition | Témoin | État |
|---|---|---|---|
| 1 | l'unité exécute bien ce script, avec cet environnement | — | non observée |
| 2 | le script atteint `probe_mission` et substitue effectivement `$VCLIENT_CMD` en une invocation `vclient` | — | non observée |
| 3 | `vclient` transmet la commande au démon | `"Command: %s"`, `LOG_INFO` | **muet** sous `debug=false` |
| 4 | `getTempKist` **résout** dans le jeu de commandes du XML déployé pour le device `20CB` | — | **non rapportée** — voir §12.3 |
| 5 | exécution jusqu'à écriture et acquittement | `">FRAMER: Command send"`, `LOG_INFO` | **muet** sous `debug=false` |

> **Trois des cinq transitions n'ont aucun témoin ; les deux qui en portent un
> l'ont en `LOG_INFO`, donc muet dans les deux sens** : l'absence de ces deux
> événements du journal ne prouve rien, ni que la commande passe, ni qu'elle
> échoue.

> **Couplage à ne pas perdre de vue.** Si `getTempKist` était rejetée avant
> Optolink, la session `vclient` se terminerait néanmoins par `quit` →
> libération sans acquisition — c'est exactement le chemin décrit au §12.1,
> **toutes les trois minutes, sans réparation sous `-n`**. `H3` et `H6` ne
> peuvent donc pas se soutenir l'une l'autre : elles partagent le même point non
> observé.

### 12.3 Un fait statique à portée de l'Acte A, non relevé

La **transition 4** — la présence ou l'absence de `getTempKist` dans le jeu de
commandes du XML déployé pour le device `20CB` — est un constat en lecture, du
même ordre que ceux conduits aux §8 et §9. Il n'a pas été fait : le XML a été lu
pour `debug`, le device et le journal, sans que sa table de commandes soit
examinée. **C'est une lacune de la campagne, non une limite du terrain.**

Elle ne peut pas être comblée ici : **l'Acte A est terminé et aucune autorisation
nouvelle n'a été donnée.** L'opportunité d'un constat complémentaire relève d'un
**arbitrage humain**.

> **Aucune hypothèse n'est déclarée CLOSED.** Les quatre subsistent, réduites à
> des degrés divers, et leurs résidus sont nommés — non minimisés.

---

## 13. `U-1` / `I1`

`U-1` progresse : **aucune des quatre hypothèses n'est close**, mais toutes se
réduisent — `H1` et `H2` fortement, `H3` et `H6` partiellement. Le statut
canonique **reste intégralement en vigueur, `H3` incluse** :

> `U-1 — PART AMONT ÉTABLIE SOUS H1/H2/H3/H6, RÉSIDU D'INSTALLATION OUVERT`

`I1` demeure **PARTIELLEMENT RÉDUITE** : l'Acte A n'a rien apporté sur la
robustesse sous concurrence, les erreurs, les refus ou les signatures d'échec.

Le régime demeure **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`**, inchangé. Sa mise à
jour formelle appartiendrait à une phase documentaire séparée, non engagée ici —
et l'Acte A ne la motive pas, aucune hypothèse n'étant tombée.

---

## 14. Acte B

> **`ACTE B IMPOSSIBLE AVEC LE JOURNAL ACTUEL`**

**Pourquoi** : `debug = false` fait écarter par le programme lui-même, vers le
fichier de journal et vers syslog, tous les événements `LOG_INFO`. Les six types
dont l'Acte B aurait besoin sont **absents du journal, à zéro occurrence sur
200 000 lignes**. Le journal ne porte que les ouvertures de connexion, sans
fermeture, à la seconde près.

**Ce qu'il aurait pu réduire** : `H3` et `H6`, **toutes deux encore ouvertes**.
L'Acte A les a réduites sans les clore, et les témoins qui auraient pu achever
leur réduction sont précisément ceux que le journal ne porte pas —
`"Command: %s"` et `">FRAMER: Command send"` pour `H3`, les séquences
`tries to aquire` / `got lock` / `released lock` pour `H6`.

### 14.1 Ce que l'instrument `H6` ne pourrait pas montrer, même avec `debug`

Les trois événements de verrou sont bien fidèles et bien `LOG_INFO` — trois des
douze événements caractérisés. Leur rattachement à `H6` est conforme. Mais deux
bornes les limitent, et elles doivent être portées ici sous peine de reconduire,
en plus discret, la confusion que la non-clôture de `H6` vient d'écarter.

1. **Sous `-n`, la discrimination par PID est annulée.** Tous les événements
   portent le PID du démon unique. Le PID ne sépare plus les sessions ni les
   clients.
2. **La part du résidu de `H6` isolée au §12.1 n'y est pas visible.** L'état de
   `semval`, et la possibilité qu'un participant **extérieur au démon** agisse
   sur un IPC System V en `0666`, n'apparaissent dans **aucun** de ces trois
   événements, **quel que soit l'état de `debug`**. Le journal du démon ne
   journalise pas ce qu'un tiers fait à son sémaphore.

> **L'Acte B reste donc pertinent dans son objet, et impossible dans ses
> moyens** — et, pour la part extérieure du résidu de `H6`, il serait
> **insuffisant même s'il devenait possible**. Le rendre possible exigerait
> d'activer `debug`, c'est-à-dire une **modification de configuration** — hors
> périmètre, et décision humaine distincte. **Aucune exécution.**

---

## 15. Frontières

**W4-F0 CLOSED · W4-F1 CLOSED · W4-F1A CLOSED** · **Acte A exécuté sous
autorisation humaine explicite** · **Acte B NON EXÉCUTÉ** · **W4-F2 FERMÉ / NON
AUTORISÉ** · aucun T0/T1/T2 · **aucune écriture chaudière** · **aucun `vclient`
réel exécuté** · aucun publish MQTT · aucun redémarrage ni reload · **aucun
fichier système modifié** · aucun service modifié · aucun déploiement · **le pont
historique reste l'unique écrivain réel de production** · transaction surface
toujours sans autorité · **stash W3 intact**.

---

## 16. État Git après terrain

`main` @ `ef227a016bd66d21714c5a04dab616ca92adfcda` = `origin/main` · ahead 0 /
behind 0 · status **vide** · `stash@{0}` W3 intact · 1 worktree · les deux
documents gouvernants aux mêmes empreintes qu'avant la campagne.

**Confirmation : aucune modification du dépôt.**

---

## 17. Verdict

> **Réserve portée au verdict.** L'Acte A a atteint son terme dans son périmètre,
> mais **incomplètement sur un point à sa portée** : la résolution de
> `getTempKist` dans le jeu de commandes du XML déployé (§12.3). Le verdict
> ci-dessous vaut pour la campagne telle qu'elle a été conduite, et non comme
> épuisement de ce que l'Acte A pouvait établir.

**ACTE A TERMINÉ — STOP AVANT ACTE B**

---

## 18. Historique de révision

**Version 1** — première rédaction consolidée. Elle intègre en place les
corrections issues d'un audit indépendant conduit **sur pièce**, sans accès
terrain, contre le document de caractérisation `w4f1a-upstream-characterization.md`
et contre le code amont `vcontrold` au commit
`8ca47972c9ac5b0a14a7a36393b0dbfdb165f918`, cloné et lu par l'auditeur.

Six corrections par rapport à la première rédaction du constat :

| Réf | Ce qui a été corrigé | Origine |
|---|---|---|
| §9 | la clause sur la porte `debug` était énoncée comme une propriété générale du programme ; elle est restreinte aux **puits persistants** — fichier de journal et syslog — et assortie de la réserve d'inventaire sur la voie `dbgFD`. **La chaîne `debug = false` n'a pas bougé** : l'audit l'a vérifiée verbatim et jugée sans écart | audit sur pièce, réserve d'inventaire |
| §12 | `H3` était donnée **CLOSED**. Le pas `getTempKist` → « lecture de datapoint réelle » est une inférence sémantique tirée du nom, que la caractérisation §7.5 disqualifie explicitement et que le cadrage §6.1 proscrit. Ramenée à **PARTIELLEMENT RÉDUITE**, maillon 2 **NON ÉTABLI** | audit sur pièce, finding H3 |
| §12 | `H6` était donnée **CLOSED** au motif que `-n` rend le mode de défaillance impossible. `-n` masque la **conséquence** sans établir le **contenu** : le chemin de libération non appariée reste ouvert, le sémaphore est un IPC noyau en `0666` accessible de l'extérieur, et sous `-n` la réparation par `SEM_UNDO` n'est plus bornée par la session mais par la vie du démon. Ramenée à **RÉDUITE, NON CLOSE**, résidu absorbé dans celui de `H2` | audit sur pièce, finding H6 |
| §13 | « deux des quatre hypothèses tombent » et un régime réduit à `H1/H2` découlaient des deux clôtures retirées. Rétablis : aucune hypothèse close, régime **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`**, statut `U-1` intégralement en vigueur | conséquence des deux findings ci-dessus |
| §14 | la justification « les deux hypothèses visées sont tombées par voie statique » ne tenait plus. Corrigée. **Le constat factuel d'impossibilité — `debug=false`, `LOG_INFO` écartés, 0 occurrence sur 200 000 lignes — n'a pas été remis en cause et n'a pas bougé.** Ajout du §14.1 bornant l'instrument `H6` : PID non discriminant sous `-n`, et part extérieure du résidu invisible dans ces événements quel que soit `debug` | conséquence des findings, puis réaudit |
| §12.3 et §17 | la transition 4 — résolution de `getTempKist` dans le XML déployé — est un fait statique **à portée de l'Acte A** qui n'a pas été relevé. Signalé comme lacune de campagne, avec réserve portée au verdict | audit sur pièce, finding H3 |

Trois précisions apportées lors du réaudit du correctif :

- le fichier `/home/pi/boiler-bridge/boiler_guard.sh` **a bien été lu pendant
  l'Acte A** ; son nom avait été omis de la première rédaction, qui ne décrivait
  le superviseur que par ses unités systemd. Le fait est rétabli au §12, et sa
  conséquence assumée : la chaîne du maillon 2 se dédouble en amont, portant le
  compte des transitions non observées de quatre à **cinq** (§12.2) ;
- le verrou interne du pont est **exact et observé**, mais **non porteur** pour la
  réduction de `H6` ; il est conservé comme constat et non comme argument
  (§12.1) ;
- l'instrument `H6` du §14 est explicitement borné (§14.1).

**Aucune contestation n'a été opposée aux findings** : deux étaient opposables par
le document de caractérisation lui-même, le troisième portait sur un fait de
`SEM_UNDO` sous `-n` qui n'avait pas été instruit.

---

**Version 2** — deux corrections mineures et une précision de décompte, issues
d'un second tour d'audit indépendant conduit **sur pièce**, contre les mêmes
sources, le code amont étant relu au même commit
`8ca47972c9ac5b0a14a7a36393b0dbfdb165f918`. Sont repris **inchangés** : les
quatre statuts d'hypothèses, le régime, `U-1`, `I1`, la borne `r < 0,485 s`, le
§9, le constat d'impossibilité de l'Acte B et le verdict du §17 avec sa réserve.

| Réf | Ce qui a été corrigé | Origine |
|---|---|---|
| §12.1, point 1 | l'argument reposait sur « `vclient` termine **toujours** sa session par `quit` ». Le « toujours » est inexact au sens strict : `disconnectServer()`, seul émetteur de `quit`, n'est atteint qu'après un retour non nul de `sendCmds()` ; sur prompt non reçu, envoi ou réception en échec, `vclient` sort par `exit(1)` sans émettre `quit`. Le point est refondé **a fortiori** — tous les chemins de sortie de `interactive()` libèrent sans garde, `quit` émis ou non — et le cas de la commande rejetée avant Optolink, qui passe bien par `quit`, redevient l'illustration et non le fondement. **`H6` reste RÉDUITE, NON CLOSE** | audit sur pièce, opposé au code amont |
| §11 | le tableau portait « clients observés » et attribuait aux deux unités un mode d'accès sur le registre de l'**observation**, sans nommer de témoin, alors que le §12.2 cote « non observée » la chaîne qui mènerait précisément à cette attribution. Le §11 distingue désormais l'observé du **connu par configuration**, nomme le témoin de chaque attribution, et cesse de rattacher implicitement à l'une des deux unités la paire `vclient` ↔ `vcontrold` relevée à l'instant du constat. **`H2` n'est pas rouverte** : statut, résidu et inventaire des ouvrants inchangés | audit sur pièce, opposition §11 / §12.2 |
| §12.2, encadré | « Deux des cinq témoins sont `LOG_INFO` » supposait cinq témoins existants. Trois des cinq transitions n'en portent **aucun** ; les deux qui en portent un l'ont en `LOG_INFO` | audit sur pièce |

**Motif du retrait initial de la clause sur le verrou interne du pont** — annoncé
lors du réaudit de la v1 et resté non porté : **économie de rédaction**, et non
disqualification du fait. La clause ayant été rétablie intégralement en v1, ce
motif ne subsiste que comme mémoire de correction ; sa place est ici, et non dans
le corps.

---

**Version 3** — une correction unique, issue d'un troisième tour d'audit
indépendant conduit **sur pièce**, le code amont étant relu au même commit
`8ca47972c9ac5b0a14a7a36393b0dbfdb165f918`.

| Réf | Ce qui a été corrigé | Origine |
|---|---|---|
| §12.1, point 1 | l'illustration citait la réponse serveur `ERR: command %s unknown`. Cette chaîne n'est pas celle du chemin décrit : elle n'est émise que dans la branche `detail`, en réponse à un `detail <commande inconnue>`. Une commande qui ne résout pas échoue au test d'existence, traverse la chaîne de `else if` et reçoit `ERR: command unknown` — chaîne fixe, sans substitution, émise depuis un autre site. La citation est corrigée et la mention de substitution levée | audit sur pièce, opposé au code amont |

**Rien d'autre n'est touché.** L'argument **a fortiori** du point 1, l'énumération
des chemins de sortie de `interactive()`, la conclusion du §12.1 et le statut
**`H6` RÉDUITE, NON CLOSE** sont inchangés : les deux chaînes commencent l'une et
l'autre par `ERR:`, le client les traite identiquement, et le point porteur — la
libération non appariée — ne dépend d'aucune des deux. Les quatre statuts
d'hypothèses, le régime, `U-1`, `I1`, la borne `r < 0,485 s`, les §9, §10, §11,
§12.2, §14.1, le constat d'impossibilité de l'Acte B et le verdict du §17 avec sa
réserve sont repris **inchangés**.
