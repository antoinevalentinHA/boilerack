# Cadrage — activation de `debug` sur le démon `vcontrold` de production

> **Ce document est un cadrage. Il n'autorise aucun terrain.**
>
> Aucune autorisation d'exécution n'a été donnée. Il ne contient aucun mode
> opératoire, aucune commande prête à l'emploi, aucune séquence exécutable. Il
> décrit **ce qu'il faudrait établir et sous quelles contraintes** — pas comment
> le faire.
>
> Il n'ouvre aucun acte, ne prépare aucun acte, et ne porte aucune désignation de
> lot ni de phase : leur attribution appartient à l'humain.

**Sources.** Tout ce que ce cadrage dit de l'installation vient du constat
`docs/design/w4a-acte-a-constat.md` intégré à `main`
(SHA-256 `8ba4ff0f7bf7df9a680400316699e8d18a11fd84895a1f0e09554d81f048fb6a`), et
de rien d'autre. Tout ce qu'il dit du programme vient de la relecture du code
amont `openv/vcontrold` au commit `8ca47972c9ac5b0a14a7a36393b0dbfdb165f918` et
des deux pièces `docs/design/w4f1a-upstream-characterization.md` et
`docs/design/w4f1a-vcontrold-concurrency.md`. **Aucun fait de terrain nouveau.**

---

## 0. La limite à porter en tête

**Une part du résidu de `H6` restera invisible quoi qu'il arrive.**

Le constat établit que l'état de `semval`, et l'action d'un participant
**extérieur au démon** sur un ensemble de sémaphores System V en mode `0666`,
n'apparaissent dans **aucun** des trois événements de verrou —
`tries to aquire`, `got lock`, `released lock` — **quel que soit l'état de
`debug`**. Le démon ne journalise pas ce qu'un tiers fait à son sémaphore.

Cette limite n'est pas une réserve de bas de page : elle borne d'avance le
rendement maximal de toute activation. **Aucun réglage de journalisation ne la
lève.** Ce qui suit s'apprécie sous cette borne.

Une seconde limite du même ordre : sous `-n`, tous les événements portent le PID
du démon unique, la discrimination par PID est annulée. Elle est toutefois
**compensable** — voir §A.3.

---

## A. Objet et rendement attendu

### A.1 Le mécanisme, relu

`logIT()` (`common.c:56-120`) écarte l'événement avant tout puits persistant :

```
if (! debug && (class > LOG_NOTICE)) { free(print_buffer); return; }
```

`LOG_NOTICE` vaut 5. Passent donc **inconditionnellement** `LOG_ERR` (3),
`LOG_WARNING` (4) et `LOG_NOTICE` (5) ; sont **écartés sans `debug`** `LOG_INFO`
(6) et `LOG_DEBUG` (7). Activer `debug` ouvre la porte **aux deux niveaux à la
fois** — `LOG_INFO` et `LOG_DEBUG`, indistinctement : il n'existe **aucun réglage
de granularité**, aucun filtre par module, aucun niveau intermédiaire. C'est un
interrupteur binaire, tout ou rien.

Deux puits sont derrière la porte, et un seul est actif sur le site :

| Puits | Condition | État sur le site |
|---|---|---|
| syslog | `syslogger`, depuis `-s` ou `<syslog>` | **inactif** — `<syslog>n</syslog>` |
| fichier | `logFD`, depuis `-l` ou `<file>` | **actif** — `/home/pi/vcontrold.log` |
| `stderr` | `isatty(2)` (`common.c:115`) | **inactif** — fd 2 est une socket journald |

Un troisième chemin existe **en amont de la porte** (`common.c:93-96`) : si
`dbgFD >= 0`, tout événement est écrit d'abord sur ce descripteur, préfixé
`DEBUG:`. Il est armé par `debug on` **en session** (`vcontrold.c:298`), pointe
vers la socket du **client demandeur**, et est remis à `-1` en fin de session
(`vcontrold.c:965`). **Il n'atteint ni le fichier ni syslog, et n'écrit pas la
variable `debug`.** Le constat le porte déjà comme réserve d'inventaire.

### A.2 Ce qui franchirait la porte

Les douze événements inventoriés par `w4f1a-upstream-characterization.md`
(§10.3), dont onze à `LOG_INFO`.
Rapportés au site — un seul processus, pas de `fork` :

| Événement | Origine | Statut sur le site sous `debug` |
|---|---|---|
| `Client connected …` | `socket.c:145`, `LOG_NOTICE` | **déjà visible**, ne change pas |
| `Child process started with pid %d` | `socket.c:153` | **jamais émis** — `makeChild` faux sous `-n` |
| `Child process with PID %d terminated` | `vcontrold.c:967` | **jamais émis** — sous `if (makeDaemon)` |
| `Process %d tries to aquire lock` | `semaphore.c:139` | **apparaîtrait** |
| `Process %d got lock` | `semaphore.c:150` | **apparaîtrait** |
| `Process %d released lock` | `semaphore.c:158` | **apparaîtrait** |
| `>FRAMER: open device %s ProtocolID %02X` | `framer.c:491` | **apparaîtrait** |
| `>FRAMER: opened` | `framer.c:217` | **apparaîtrait** |
| `>FRAMER: closed` | `framer.c:169` | **apparaîtrait** |
| `Command: %s` | `vcontrold.c:277` | **apparaîtrait** — porte la commande émise |
| `>FRAMER: Command send` | `framer.c:300` | **apparaîtrait** — écriture puis acquittement |
| `Closed connection (fd:%d)` | `socket.c:162` | **apparaîtrait** |

Deux des douze sont donc **structurellement inatteignables** sur cette
installation : ils sont conditionnés au mode `fork`, que `-n` exclut.

L'inventaire de `w4f1a-upstream-characterization.md` est celui de la question du
verrou. La relecture du code en fait apparaître **beaucoup d'autres**, hors de ce
périmètre et pourtant sur le même interrupteur — et ce sont eux qui dominent le
volume :

- `io.c:130` — `">SENT: %02X"` dans `my_send()`, **une ligne par octet émis** ;
- `io.c:287` — `"<RECV: len=%zd %02X (%0.1f ms)"` dans `receive_nb()`. **C'est le
  site de réception du chemin de la session TCP** : `framer_receive()`
  (`parser.c:238`) descend vers `receive_nb()` (`framer.c:351`, `:370`, `:393`),
  et `framer.c:351` **précède** le test `framer_pid != P300_LEADIN` de
  `framer.c:360` (`:359` étant `return FRAMER_READ_TIMEOUT;`) —
  le chemin est donc emprunté quel que soit le protocole déployé. Le décompte
  n'est **pas** d'une ligne par octet : voir §E.1 ;
- `io.c:299` — ligne de vidage `<RECV: received …`, émise **à chaque réception
  complète** (`io.c:296-299`, sortie normale de `receive_nb()`). La **même ligne**
  figure à `io.c:255`, `:264`, `:272` et `:281`, mais **sur des chemins d'erreur**
  — délai de `select()` (`io.c:252`), erreur de `select()` (`:257`), fin de flux
  (`:269`), erreur de `read()` (`:274`). **Ces quatre-là ne comptent pas dans le
  régime nominal** ;
- `io.c:170` — `"<RECV: %02X (%0.1f ms)"` dans `receive()`, **une ligne par octet
  reçu**. `receive()` (`io.c:141`) n'est atteinte que par `waitfor()` (`io.c:329`,
  `:340`) et par `execCmd()` (`parser.c:376`). **Ce site reste atteignable depuis
  une session TCP, par deux chemins distincts** :
  - `waitfor()`, depuis `framer_waitfor()` (`framer.c:483`) sur l'opération `WAIT`
    du bytecode (`parser.c:183`) — **la présence de telles opérations dans le jeu
    de commandes déployé n'est pas établie** ;
  - `execCmd()`, depuis `readCmdFile()` (`vcontrold.c:136`), dont les **deux**
    sites d'appel sont `vcontrold.c:979` — le fichier de commandes de démarrage,
    hors session — et `vcontrold.c:224`, **à l'intérieur de `rawModus()`**
    (`vcontrold.c:186`), qu'`interactive()` atteint sur la commande `raw`
    (`vcontrold.c:321`). **Ce second chemin est bien celui d'une session TCP.**

  > **Portée exacte, à ne pas sur-borner.** Le chemin de lecture **ordinaire** —
  > `execByteCode()` → `framer_receive()` → `receive_nb()` — passe par `io.c:287`
  > et non par `io.c:170`. Mais le mode `raw` conduit bien à `io.c:170`, et donc à
  > **une ligne par octet reçu**. **Que le superviseur ou le pont emploient ce
  > mode n'est pas établi** : le constat ne le dit pas, et rien ici ne le suppose.

- `io.c:323` — `"Waiting for %s"`, dans `waitfor()` (`io.c:309`). `waitfor()` a
  **deux appelants** : `framer_waitfor()` (`framer.c:483`), qui dépend de
  l'opération `WAIT` du bytecode déployé, **et `execCmd()` (`parser.c:359`,
  `case WAIT:`)**, donc le chemin `raw` ci-dessus — **qui ne dépend pas du jeu de
  commandes déployé**. La réserve `WAIT` ne couvre donc pas ce site à elle seule ;
- `vcontrold.c:444` — le tampon reçu, journalisé tel quel ;
- `framer.c:99`, `:105`, `:124` — trois `LOG_DEBUG` de suivi d'adresse ;
- `unit.c` — **onze** `LOG_INFO`, dont quatre dans `procGetUnit()` (`unit.c:327`,
  journalisant à `:451`, `:453`, `:464`, `:471`). **Sur le chemin de lecture** :
  `procGetUnit()` est appelée depuis `execByteCode()` (`parser.c:275`) ;
- `parser.c` — **onze** `LOG_INFO` vivantes — `:502` est commentée — dont `:297`
  dans `execByteCode()`, et six sur le chemin de `compileCommand()`
  (`parser.c:653`), **à des granularités différentes qu'il faut distinguer** :
  `:479`, `:536` et `:568` sont dans `expand()` (`parser.c:437-577`), qui récurse
  **par commande** (`parser.c:443-444`) ; `:615` est émise **une fois par
  commande** dans `buildByteCode()` (`parser.c:578-651`) ; `:629` est dans la
  boucle `do…while` de cette même fonction (`parser.c:617-647`) et est donc émise
  **par jeton** ; `:662` est dans `compileCommand()`, qui récurse **par
  périphérique** (`parser.c:658-659`), et est donc émise **par périphérique** ;
- `xmlconfig.c` — **quarante-sept** `LOG_INFO` sur le chemin d'analyse du XML.

> **Les deux derniers postes se cumulent à chaque chargement de configuration.**
> `reloadConfig()` (`vcontrold.c:87-97`) appelle `parseXMLFile()` **puis**
> `compileCommand()` : les quarante-sept lignes de `xmlconfig.c` et les six sites
> de `parser.c` — **quatre par commande, un par jeton, un par périphérique** —
> sont émis **ensemble**, au démarrage (`vcontrold.c:823`) comme à chaque
> rechargement (`vcontrold.c:90`).

### A.3 Ce que cela réduirait

**`H3`, maillon 2.** Le constat énumère cinq transitions non observées entre la
valeur configurée `getTempKist` et l'atteinte effective de la liaison. Deux
d'entre elles ont un témoin, et ce témoin est à `LOG_INFO` :

| Transition | Témoin | Sous `debug` |
|---|---|---|
| 3 — `vclient` transmet la commande au démon | `Command: %s` | **observable** |
| 5 — exécution jusqu'à écriture et acquittement | `>FRAMER: Command send` | **observable** |

Les transitions **1**, **2** et **4** n'ont **aucun témoin direct dans le démon**.
Pour les transitions **1** et **2**, `debug` ne les atteint pas du tout. Pour la
**transition 4** — la résolution de `getTempKist` dans le jeu de commandes
déployé — il n'existe pas davantage de témoin direct, **mais une signature
indirecte existe sous `debug`**, décrite au §C.2 (a) : il serait donc inexact de
dire que `debug` ne l'atteint pas. Les autres moyens d'atteindre ce fait sont
traités au §C.

> **Rendement sur `H3` : partiel.** Deux transitions sur cinq. Le maillon 2 ne
> serait pas établi pour autant, sauf à ce que les transitions 1, 2 et 4 le
> soient par ailleurs.

**`H6`, part interne.** La séquence `tries to aquire` → `got lock` →
`released lock` deviendrait lisible, et avec elle l'appariement des acquisitions
et des libérations **à l'intérieur du démon**. La perte de discrimination par PID
sous `-n` **n'empêche pas cette lecture** : le service étant strictement
séquentiel, les sessions ne s'entrelacent pas, et l'appariement se lit dans
l'ordre d'apparition. C'est le rendement le plus net de l'activation.

**Ce qu'elle ne réduirait pas, et il faut l'énoncer :**

- **la part extérieure du résidu de `H6`** — §0, invisible par construction ;
- **`H1`** — le lien entre le binaire déployé et l'arbre source au moment de la
  compilation ne se journalise pas ;
- **`H2`** — un ouvrant du périphérique **extérieur au démon** n'apparaît dans
  aucun événement du démon ;
- **`I1`** — robustesse sous concurrence, erreurs, refus, signatures d'échec :
  rien de ce que `debug` ouvre ne les caractérise ;
- **la contrainte `r < 0,485 s`**. Ce point est décisif et souvent mal lu :
  activer `debug` **ne change pas la résolution d'horodatage**. Le puits fichier
  écrit une chaîne produite par `ctime()` (`common.c:63`) et rendue au format de
  journal à `common.c:110` — donc **à la seconde**. Il échoue la contrainte
  **par construction**, avec ou sans `debug`. Ouvrir la porte ne fait que
  produire davantage de lignes à la même résolution insuffisante. Seul le puits
  syslog pourrait la satisfaire — mais il est inactif sur le site, sa résolution
  est un fait d'installation non établi, et l'activer serait **une mutation
  supplémentaire**, distincte de celle qui est ici cadrée.

> **Synthèse du rendement.** Activer `debug` réduirait **la part interne de
> `H6`**, et **deux transitions sur cinq de `H3`**. Cela ne clôt ni l'une ni
> l'autre, ne touche ni `H1`, ni `H2`, ni `I1`, et ne lève pas `r < 0,485 s`.

---

## B. La voie `dbgFD` — ce qui est déjà observable sans mutation

Le §A.1 a relevé cette voie et n'en a tiré qu'une conséquence : elle n'atteint pas
les puits persistants. C'était insuffisant. Elle porte **le même flux
d'événements** que celui dont l'activation est censée être le rendement, et elle
doit donc entrer dans la comparaison — faute de quoi le §C opposerait deux voies
là où il y en a trois, et le §H-3 mettrait deux interruptions en balance avec un
rendement dont une part serait déjà accessible autrement.

### B.1 Deux natures de puits, à séparer

| | Puits **persistants** | Voie `dbgFD` |
|---|---|---|
| Destination | fichier, syslog | la **socket du client demandeur** |
| Position vis-à-vis de la porte | **après** (`common.c:98`) | **avant** (`common.c:93-96`) |
| Conditionnée à `debug` | **oui** | **non** |
| Armement | configuration **et** redémarrage | commande `debug on` en session |
| Persistance | fichier sur disque | **aucune** — flux vers un client |
| Portée | tout ce que le démon émet | voir §B.3 |

### B.2 Ce qu'elle rend déjà observable — établi sur code

`common.c:93-96` précède `common.c:98`. Tout événement passé à `logIT()` est donc
écrit sur `dbgFD` **avant** que la porte n'écarte quoi que ce soit : `LOG_INFO`
**et** `LOG_DEBUG` compris, `debug` actif ou non.

Il en résulte que, `dbgFD` armé, la session voit passer :

- la séquence de verrou complète — `tries to aquire`, `got lock`,
  `released lock` ;
- `Command: %s` ;
- `>FRAMER: open device …`, `>FRAMER: opened`, `>FRAMER: Command send`,
  `>FRAMER: closed` ;
- les lignes d'émission et de réception de `io.c`, et les `LOG_DEBUG` de
  `framer.c`.

C'est-à-dire **exactement la matière que le §A.3 compte comme rendement de
l'activation** — sans toucher au XML, sans toucher à l'unité systemd, et sans
redémarrer le démon.

### B.3 Ce qu'elle ne rend pas observable — établi sur code

**a) Rien qui sorte de la session observatrice.** `dbgFD` est un descripteur
global unique (`common.c:26`), armé par `setDebugFD(socketfd)` sur la socket du
demandeur (`vcontrold.c:298`). Sous `-n`, le service est **strictement
séquentiel** : `main()` n'accepte la connexion suivante qu'après retour
d'`interactive()` (`vcontrold.c:955-963`). Tant que la session observatrice est
ouverte, **aucune autre session n'est servie**. Il est donc **structurellement
impossible** d'observer par cette voie le trafic d'un autre client : on n'observe
que **sa propre session**.

**b) Rien avant la session — mais le rechargement, lui, n'est pas hors de
portée.** `setDebugFD(-1)` est exécuté à la fin de chaque session
(`vcontrold.c:965`), et l'armement ne survit pas : les événements du **démarrage**
échappent entièrement à cette voie. Le **chargement de configuration**, en
revanche, n'y échappe pas : `reload` est une **commande de session**
(`vcontrold.c:305-306`) qui appelle `reloadConfig()` (`vcontrold.c:87-97`)
**pendant** la session, `dbgFD` armé — les quarante-sept `LOG_INFO` de
`xmlconfig.c` et les lignes par commande de `parser.c` partiraient alors sur
`dbgFD`. Un `SIGHUP` reçu pendant une session (`vcontrold.c:594-598`) produirait
le même effet, le démon étant un processus unique sous `-n`.

**c) Aucune portée temporelle.** Il n'y a pas de flux qu'on laisse tourner : la
fenêtre d'observation est exactement la durée de la session, et cette session
**bloque le service** pendant tout ce temps.

**d) Aucune persistance *du côté du démon*.** Le flux part vers une socket
(`common.c:95`) : le démon n'en écrit rien et n'en conserve rien. **Ce que le
destinataire en fait est hors du code**, et ce cadrage n'a rien pour le trancher.
Il ne prétend donc pas que le flux ne puisse être ni relu ni compté — seulement
que **le démon n'y pourvoit pas**, là où le puits fichier y pourvoit.

**e) Aucun PID.** Le format est `"DEBUG:%s: %s\n"` (`common.c:95`) : il ne porte
pas le PID, là où la sortie fichier le porte (`common.c:110`). Sous `-n` la
discrimination par PID est de toute façon annulée, mais cette voie en porte encore
moins.

**f) Aucune amélioration de résolution.** `common.c:95` emploie la **même** chaîne
`tPtr`, issue de `ctime()` (`common.c:63`). La résolution reste **à la seconde** :
`r < 0,485 s` n'est pas davantage atteignable par cette voie que par le fichier.

**g) Elle exige d'exécuter un client.** Armer `dbgFD` suppose d'ouvrir une session
sur le démon de production et d'y émettre une commande. Ce n'est ni une mutation
ni un redémarrage — mais ce n'est pas non plus une observation passive : c'est une
**exécution sur l'hôte**, qui occupe le service séquentiel. **Ce cadrage ne la
propose pas, ne la prépare pas et ne l'autorise pas** ; elle est décrite ici parce
que la comparaison de rendement l'exige.

**h) Elle déforme ce qu'elle montre — et sans condition.** `common.c:93-96` est
**dans** `logIT()`, avant la porte. Chaque `LOG_INFO` de la boucle de réception —
`io.c:287` — y déclenche donc un `dprintf` (`common.c:95`) **dans le même appel de
`logIT()`** que celui où le puits fichier ferait son `fflush()` (`common.c:111`) —
seize lignes plus bas, mais **à l'intérieur du même intervalle**, celui que
`io.c:286-288` rapporte : horodatage pris avant, ancre déplacée après. L'effet
d'observation que le §E.3 tient pour le risque le plus sérieux de l'activation
**est de même nature et de même inconditionnalité** pour `dbgFD`, cette voie
n'étant pas soumise à la porte. **Sa magnitude, en revanche, n'est établie nulle
part** — ni pour l'un ni pour l'autre puits — et rien ici ne permet de les
comparer en grandeur.

> **Cette limite coupe dans l'autre sens que les sept précédentes.** Celles-ci
> bornent ce que `dbgFD` **ne montre pas** ; celle-ci entame la qualité de ce
> qu'elle **montre**. Le seul avantage que le §B.5 lui reconnaît — voir la
> **forme** sans mutation — en sort diminué : la forme est vue, mais **altérée par
> l'observation elle-même**.

### B.4 Le rendement réellement supplémentaire de l'activation

La comparaison se joue sur la **population observée**, et c'est elle qui tranche.

La caractérisation amont fixe cette population : **les sondes du superviseur, et
elles seules**. Le maillon 2 de `H3` porte sur la commande **que le superviseur
émet**. La part interne de `H6` porte sur l'appariement des verrous **tel que le
produisent les clients réels**, dans la durée.

| Objet | Voie `dbgFD` | Activation sur puits persistants |
|---|---|---|
| Voir la **forme** de la séquence d'événements | **oui, mais déformée** — §B.3 h) | oui, et déformée de même — §E.3 |
| Voir la séquence produite par **le superviseur** — population de l'étude | **non** — §B.3 a) | **oui, sous réserve (1)** ci-dessous |
| Voir la séquence produite par **le pont** — **hors population** | **non** — §B.3 a) | oui, sous réserve (1), mais **hors périmètre** — réserve (2) |
| Observer **dans la durée**, sur plusieurs cycles | **non** — §B.3 c) | **oui** |
| Conserver de quoi relire, compter, recouper | **non du côté du démon** — §B.3 d) | **oui**, le journal y pourvoit |
| Atteindre `r < 0,485 s` | non | non |
| Atteindre la part extérieure du résidu de `H6` | non | non |

> **Deux réserves grèvent la colonne « activation », et elles doivent être lues
> avec le tableau.**
>
> **(1) Registre.** Que le superviseur et le pont atteignent le démon par TCP
> `3002` est **connu par configuration, non observé** — le constat les qualifie
> « connus par configuration, non observés en train d'exécuter » et précise
> qu'« aucun témoin d'exécution ne rattache ce mode d'accès à l'une ou l'autre
> unité » (§D.4). Si l'un d'eux n'atteignait pas le démon par cette voie,
> **l'activation n'en montrerait rien**. Les « oui » de cette colonne sont donc
> **conditionnels au même fait non observé**, et l'encadré « Quatre registres » du
> §D.4 s'applique ici au même titre qu'il s'y applique.
>
> **(2) Population.** `w4f1a-vcontrold-concurrency.md` §6.1 fixe la population aux
> **sondes du superviseur, et elles seules**, et exclut explicitement **six**
> catégories : « toutes les commandes indistinctement · toutes les connexions ·
> toutes les sessions · les commandes invalides ou rejetées avant Optolink · les
> écritures · l'usage interactif général du démon ». Il **interdit d'extrapoler**
> depuis le comportement d'une autre commande. La ligne « le pont » ne peut donc
> **pas** être portée au crédit du rendement visé : elle décrit un supplément
> d'observation **hors du périmètre d'étude**.

> **Le rendement supplémentaire de l'activation n'est pas marginal : il est
> presque entier.** `dbgFD` montre ce que le démon **sait** émettre — ce que la
> caractérisation amont établissait déjà par la seule lecture du code. Elle ne
> montre **pas** ce que les clients réels produisent, et c'est là que se trouve
> l'intégralité du rendement décrit au §A.3.

### B.5 Ce que cela change à la balance

Deux effets, de sens opposés, et ils ne se compensent pas.

1. **Contre l'activation** — il existe un moyen de voir la **forme** du flux sans
   aucune mutation ni redémarrage. Un besoin qui se satisferait de la forme n'a
   pas à payer une mutation de production.

2. **Pour l'activation** — ce moyen **ne couvre pas la population** sur laquelle
   portent `H3` et `H6`. L'idée que l'activation serait largement redondante avec
   `dbgFD` **ne tient pas** : les deux voies n'observent pas la même chose.

> **Le second effet neutralise le premier ; il ne crée aucun crédit.** Rapportée à
> la balance **effective** de ce cadrage — qui n'avait, à aucun moment, crédité
> `dbgFD` d'une quelconque redondance — la présente section a un solde **nul**, et
> non positif. Ce qu'elle écarte est une **objection de redondance** qui aurait pu
> naître, **et non un coût** : aucun terme de cette section ne touche au coût, le
> §E étant inchangé.
>
> **Et le §B.3 h) ajoute un troisième terme, contre `dbgFD`** : la forme qu'elle
> montre est déformée par l'observation. Le premier effet ci-dessus en sort
> lui-même diminué.
>
> **La conclusion du §I n'est donc pas déplacée par cette section.** Les deux
> raisons qui la portent — l'ordre des opérations et l'absence de travail ouvert
> qui consomme la réduction — n'y sont pas touchées, et la première ne coûte
> toujours rien.

### B.6 La question tranchée

> **Une fois `dbgFD` correctement intégré à la comparaison de rendement, l'ordre
> recommandé — lecture du XML avant toute activation — reste-t-il soutenu, et
> pourquoi ?**
>
> **Oui. Et pour trois raisons qu'aucune propriété de `dbgFD` ne touche.**

1. **La lecture du XML est la seule des trois voies comparées qui ne touche pas au
   démon** — ni mutation, ni redémarrage, ni occupation du service séquentiel, ni
   octet écrit, ni fenêtre d'exposition. **Aucun événement du journal** ne
   *témoigne* de la résolution de `getTempKist` — c'est un fait de
   **configuration**, pas un fait d'exécution. Mais les deux nuances du §C.2
   restent entières, et il faut les porter ici : sous `debug`, une **signature
   indirecte** existe, plus forte que ce document ne l'admettait — `Command:` puis
   `released lock` sans acquisition ; et le **protocole de session** porte le fait
   par un **quatrième moyen**, hors des trois voies comparées. Ce qui distingue la
   lecture n'est donc **pas** d'être seule à atteindre le fait : c'est d'être seule
   à l'atteindre **sans toucher au démon**.

   > **Et elle n'est pas hors de la porte d'autorisation.** Elle s'exécute sur
   > l'hôte de production ; le §G.1 la range dans le régime de lecture **à
   > autoriser**, et **elle n'est pas autorisée**.
2. **Elle ne coûte rien.** Ni mutation, ni redémarrage, ni session, ni octet écrit,
   ni fenêtre d'exposition. `dbgFD` coûte une session bloquante ; l'activation
   coûte deux interruptions.
3. **Son résultat peut requalifier ce qu'il faut instrumenter.** Si la sonde était
   rejetée avant Optolink, la question ne serait plus de mieux observer la
   séquence, mais d'expliquer une libération non appariée toutes les trois
   minutes.

> **`dbgFD` renforce cet ordre plutôt qu'il ne l'affaiblit.** Il établit que le
> rendement des deux voies coûteuses est **conditionné à la population observée**,
> tandis que la lecture du XML porte sur un fait dont **aucun événement du journal
> ne témoigne** et qu'elle seule atteint **sans toucher au démon** — l'autorisation
> qu'elle requiert, elle, restant entière.

---

## C. L'alternative moins coûteuse, à peser d'abord

Le constat consigne une transition **non relevée alors qu'elle était à portée
d'un constat en lecture** : la résolution de `getTempKist` dans le jeu de
commandes du XML déployé pour le device `20CB`. C'est la **transition 4** du
maillon 2.

### C.1 Ce qu'elle coûte

**Rien de ce que coûte l'activation.** C'est une lecture du même fichier de
configuration que le constat a déjà lu pour `debug`, le device et le journal.
Aucune mutation, aucun redémarrage, aucune interruption de service, aucun octet
écrit, aucune exposition dans le temps, aucun volume de journal, aucun retour
arrière à organiser. **Elle ne touche pas au démon.**

> **Ce qu'elle coûte tout de même, et qu'il faut nommer.** Elle s'exécute **sur
> l'hôte de production**, comme le constat s'y est exécuté. Elle relève donc du
> régime de lecture du §G.1 — **le moins engageant du périmètre, mais dans le
> périmètre**. « Gratuite » se dit ici **par rapport au démon et à la production**,
> non par rapport à la porte d'autorisation : **cette lecture n'est pas
> autorisée**.

### C.2 Ce qu'elle réduirait

**La transition 4, entièrement** — et c'est la seule des cinq dont **aucun
événement du journal ne porte témoignage**, sous `debug` comme sans lui. Le
maillon 2 passerait de cinq transitions non établies à quatre.

> **Deux nuances, et il faut les porter : « aucun témoin » n'est pas « aucun
> moyen ».**
>
> **(a) Une signature indirecte existe sous `debug`, et elle est plus forte que ce
> que ce cadrage admettait.** `Command: %s` (`vcontrold.c:277`) est émise **avant**
> la résolution du nom (`vcontrold.c:352`). Un nom qui ne résout pas retombe à
> `vcontrold.c:565-572`, branche qui n'émet **aucun** `logIT` — et n'atteint donc
> ni `vcontrol_semget()` (`vcontrold.c:396`), ni `framer_openDevice()`
> (`vcontrold.c:398`), ni `>FRAMER: Command send`. **Mais la session finit
> néanmoins par libérer** : toutes les sorties d'`interactive()`
> (`vcontrold.c:295`, `:324`, `:569`, `:577`, `:584`) appellent
> `vcontrol_semrelease()`, dont la **première instruction** est
> `logIT(LOG_INFO, "Process %d released lock", …)` (`semaphore.c:158`), sans
> aucune garde.
>
> La signature n'est donc pas seulement « `Command:` sans séquence aval » : c'est
> **`Command:` puis `released lock`, sans `tries to aquire` ni `got lock`** — un
> motif nettement plus discriminant, et qui est précisément le mode de défaillance
> que `H6` surveille.
>
> **Cet écart joue contre la thèse de ce cadrage, et il est porté comme tel** : la
> voie `debug` atteint la transition 4 **mieux** que ce document ne l'admettait, ce
> qui érode davantage l'exclusivité déjà retirée à la lecture du XML.
>
> **(b) Le protocole de session porte le fait, sans `debug` ni `dbgFD`.**
> `vcontrold.c:478` résout un nom contre le jeu déployé et répond sur la socket
> (`vcontrold.c:562`) ; `vcontrold.c:328-336` énumère ce jeu. **Ce sont des faits
> de code, portés ici comme tels : ce cadrage n'en décrit ni n'en prépare aucun
> usage.**
>
> Ce que la lecture du XML conserve en propre, et que ces nuances ne lui retirent
> pas : elle est **la seule voie qui ne touche pas au démon** — ni mutation, ni
> redémarrage, ni occupation du service séquentiel, ni octet écrit, ni fenêtre
> d'exposition.
>
> **Ce qu'elle ne conserve pas, et qu'il ne faut pas lui prêter.** Elle n'est pas
> « sans exécution sur l'hôte » : lire un fichier sur la machine de production
> suppose d'y agir. Le §G.1 la range explicitement dans le régime de lecture
> **à autoriser**, et le constat lui-même a été conduit sur l'hôte sous
> autorisation. **La lecture du XML est dans le périmètre à autoriser, et elle
> n'est pas autorisée.**
>
> **Et « les trois voies » n'énumère plus les moyens d'atteindre ce fait.** La
> nuance (b) ci-dessus en établit un **quatrième**, qui ne passe ni par `debug`,
> ni par `dbgFD`, ni par une mutation. L'expression « trois voies » désigne
> désormais les trois voies **comparées** dans ce cadrage — lecture, `dbgFD`,
> activation — et non l'ensemble des moyens existants.

Mais son rendement réel est **asymétrique**, et c'est ce qui la rend
disproportionnellement intéressante :

| Résultat | Conséquence |
|---|---|
| `getTempKist` **résout** pour `20CB` | la transition 4 tombe ; `H3` reste ouverte sur 1, 2, 3, 5 ; le couplage `H3`/`H6` du constat se relâche |
| `getTempKist` **ne résout pas** | résultat **majeur**. La sonde du superviseur serait rejetée avant Optolink. Or le constat établit que ce cas produit, à lui seul, une libération non appariée — **toutes les trois minutes, sans réparation sous `-n`**. `H3` et `H6` basculeraient ensemble, et le résidu prendrait une forme entièrement différente |

Autrement dit : **une lecture gratuite peut rendre un résultat qui change la
nature du problème**, y compris la question de savoir si `debug` mérite d'être
activé.

### C.3 L'ordre rationnel

> **Oui, et sans atténuation : cette lecture doit précéder toute activation de
> `debug`.**

Trois raisons, dont la troisième suffirait seule :

1. **Elle est gratuite** au regard de tout ce que le §E instruit — et elle est la
   **seule voie qui ne touche pas au démon**. Elle n'est pas pour autant « sans
   exécution sur l'hôte » : le §G.1 la range dans le régime de lecture **à
   autoriser**, et elle **n'est pas autorisée**.
2. **Elle atteint sans témoin ni signature ce dont `debug` ne donne qu'une
   signature indirecte** — la transition 4 n'a **aucun témoin direct** dans le
   journal du démon, mais elle y laisse un motif discriminant (§C.2 (a)), et le
   protocole de session la porte par un quatrième moyen (§C.2 (b)). **Ce n'est
   donc plus une exclusivité**, seulement une différence de nature et de coût.
3. **Elle peut rendre la question de `debug` sans objet, ou la transformer.** Si
   la sonde est rejetée avant Optolink, l'observation à instrumenter n'est plus
   la même. Activer `debug` d'abord, ce serait payer une mutation de production
   pour instrumenter une hypothèse qu'une lecture pouvait requalifier.

Faire l'inverse n'a pas de justification technique. Le seul argument
contraire — regrouper les deux en une seule intervention — ne tient pas : la
lecture n'exige **aucune intervention sur le démon**, là où l'activation en exige
deux (§D, §F). Elle exige en revanche, comme toute opération de ce périmètre,
**une autorisation** : voir le §G.1.

> **Trois voies comparées, et un quatrième moyen hors comparaison.** Le §B
> introduit un troisième terme — l'observation en session par `dbgFD`. Sa
> comparaison complète est conduite au §B.4, et sa conséquence sur l'ordre exposé
> ici est tranchée au §B.6 : elle le **renforce**. Le §C.2 (b) établit par
> ailleurs un **quatrième moyen** d'atteindre la transition 4, que ce cadrage
> porte comme fait de code et ne compare pas, faute d'en décrire aucun usage.

---

## D. Voies d'activation et leurs conséquences

### D.1 Route ligne de commande — `-g` / `--debug`

`vcontrold.c:641` et `:700` ; positionne la variable de `main()`, transmise à
`initLog()`.

Sur le site, l'invocation vient d'`ExecStart` dans l'unité systemd locale
`/etc/systemd/system/vcontrold.service`, qui porte `/usr/sbin/vcontrold -n -p 3002`.

- **À modifier** : l'unité systemd elle-même.
- **Persistance** : **permanente**, exactement comme `-n` l'est aujourd'hui. Elle
  survit aux redémarrages du démon **et de la machine**, jusqu'à retrait explicite.
- **Redémarrage** : **nécessaire**. Une unité modifiée n'agit que sur un processus
  relancé, après rechargement de la configuration systemd.
- **Réversibilité** : rétablir l'unité et relancer — **une seconde interruption**.
- **Effet de bord** : cette route touche le **fichier d'unité**, c'est-à-dire la
  définition du service, et non seulement le comportement du programme.

### D.2 Route XML — `<logging><debug>`

`xmlconfig.c:624-626` renseigne `cfgPtr->debug` ; `vcontrold.c:785-786` ne
l'applique que **si la ligne de commande n'a rien activé**, puis `initLog()`
(`vcontrold.c:790`) l'écrit dans la variable qui commande la porte.

Sur le site : `/etc/vcontrold/vcontrold.xml`, `<debug>n</debug>`, effectif faute
de `-x` sur la ligne de commande.

- **À modifier** : la valeur `n` dans le XML de configuration.
- **Persistance** : **permanente** jusqu'à retrait.
- **Redémarrage** : **nécessaire**, et le point mérite d'être établi précisément
  parce qu'il est contre-intuitif — voir §D.3.
- **Réversibilité** : rétablir la valeur et relancer — **une seconde
  interruption**.
- **Effet de bord** : le XML porte aussi le device, le port, le journal, les
  privilèges et le jeu de commandes. Toute erreur d'édition dans ce fichier
  affecte la totalité du service, pas seulement la journalisation. Et une
  configuration invalide au démarrage est **fatale** — `vcontrold.c:754-757`
  termine le processus, que `Restart=always` fera alors reboucler.

### D.3 Aucune route ne dispense du redémarrage — établi sur le code

Le démon expose un rechargement de configuration : commande `reload` en session
(`vcontrold.c:305-308`) et `SIGHUP` (`vcontrold.c:594-598`), tous deux vers
`reloadConfig()` (`vcontrold.c:87-97`).

**Ni l'un ni l'autre n'active `debug`.** `reloadConfig()` ré-analyse le XML et
recompile les commandes — donc `cfgPtr->debug` prend bien la nouvelle valeur —
**mais rien ne la propage**. La variable qui commande la porte n'est écrite qu'en
un seul endroit, `initLog()` (`common.c:50`), appelé exclusivement depuis
`main()` (`vcontrold.c:750` et `:790`). La fusion
`if (! debug) { debug = cfgPtr->debug; }` n'existe que dans `main()`, et
`reloadConfig()` n'appelle pas `initLog()`.

> **Conséquence : les deux routes exigent un redémarrage du processus.** Il
> n'existe **aucun basculement à chaud** de `debug` vers les puits persistants.
> La seule bascule sans redémarrage est `debug on` en session — et elle n'écrit
> ni le fichier ni syslog, et disparaît avec la session.

### D.4 Ce qu'un redémarrage interrompt, et pourquoi cela n'est pas anodin

Le constat établit une configuration où le redémarrage n'est pas une formalité :

- **un seul démon**, PID unique, `PPID 1`, sans enfant ;
- **détenteur exclusif** de `/dev/ttyUSB0` au moment du constat, établi par deux
  méthodes indépendantes ;
- **mode d'accès des deux clients connus** : le pont historique et le superviseur
  atteignent la chaudière par TCP `3002` et non par le tty — mais c'est un fait de
  **configuration lue**, non d'observation. Le constat les qualifie « connus par
  configuration, non observés en train d'exécuter », et précise qu'**aucun témoin
  d'exécution ne rattache ce mode d'accès à l'une ou l'autre unité** ;
- le **pont historique est l'unique écrivain réel de production**.

> **Quatre registres, à ne pas confondre dans ce qui précède.** L'instance unique
> et la détention du périphérique sont **observées**. Le mode d'accès des deux
> clients est **connu par configuration**. L'absence de chemin de repli est une
> **inférence** tirée de l'architecture, non un constat. Ce que le superviseur et
> le pont font d'une indisponibilité est **non établi**. Le cadrage tient ces
> quatre registres séparés, ici comme partout où ils sont en jeu.

> **Interrompre le démon, c'est interrompre l'écrivain réel de production.** Il
> n'y a pas de chemin de repli : aucun autre processus ne peut servir la liaison
> pendant l'arrêt, et la conception l'interdit — un second ouvrant serait
> précisément le mode de défaillance que `H2` surveille.

Trois conséquences à instruire avant toute autorisation :

1. **`Restart=always` / `RestartSec=5`** relance automatiquement le démon. C'est
   une protection contre l'arrêt durable — mais aussi un mécanisme qui **masque**
   une configuration cassée derrière une boucle de redémarrage, et qui rend
   l'observation de l'état réel moins immédiate.
2. **Le superviseur sonde toutes les trois minutes**, avec un délai de garde de
   5 secondes. Une indisponibilité, même brève, tombera dans une fenêtre de sonde
   avec une probabilité non négligeable. Ce que le superviseur **fait** d'un échec
   de sonde n'est **pas établi** par le constat — c'est un point à instruire, et
   non à supposer.
3. **Le pont** subit la même indisponibilité. Son comportement en cas d'échec
   n'est pas davantage établi ici.

### D.5 Comparaison des deux routes

| | Unité systemd (`-g`) | XML (`<debug>`) |
|---|---|---|
| Objet modifié | définition du service | configuration applicative |
| Surface d'erreur | ligne d'invocation | fichier portant device, port, journal, privilèges, commandes |
| Échec de configuration | invocation invalide | **terminaison au démarrage**, puis boucle `Restart=always` |
| Précédence | **l'emporte** sur le XML | **cède** devant la ligne de commande |
| Persistance | permanente | permanente |
| Redémarrage | nécessaire | nécessaire |
| Retour arrière | seconde interruption | seconde interruption |

Un point d'asymétrie mérite d'être relevé : la route XML **cède** devant la ligne
de commande. Si un jour `-g` figurait dans l'unité, une valeur `n` dans le XML ne
désactiverait rien. Inversement, la route ligne de commande est
**inconditionnelle** — ce qui la rend plus prévisible, au prix de toucher à la
définition du service.

---

## E. Coûts et risques

### E.1 Volume de journal

**Fait.** Le puits est un fichier unique, `/home/pi/vcontrold.log`, de
**477 848 600 octets** au moment du constat, ne portant que des `LOG_NOTICE`.
Le format est établi par un échantillon relevé :
`[691] Mon Aug 24 19:25:02 2026 : Client connected 127.0.0.1:48426 (FD:5)`.
Sur les 200 000 dernières lignes, 199 628 sont des `Client connected` et **cinq**
types `LOG_INFO` recherchés sont à **zéro** ; une sixième ligne recherchée,
`FRAMER`, de niveau **mixte**, compte **2** occurrences — nécessairement des
variantes `LOG_ERR`.

**Fait.** Le régime actuel est donc, en pratique, **d'environ une ligne par
connexion**.

**Estimation — et elle est marquée comme telle.** Sous `debug`, une session qui
ouvre le périphérique et exécute une commande produirait :

- une **partie dite fixe**, qui ne l'est pas tout à fait : sa composition **varie
  selon la commande et selon le jeu déployé**. Elle se sépare en deux :
  - **dues à toute session qui ouvre le périphérique et exécute une commande** :
    les trois lignes de verrou, `Command:` (`vcontrold.c:277`),
    `>FRAMER: open device` (`framer.c:491`), `>FRAMER: opened` (`framer.c:217`),
    `>FRAMER: Command send` (`framer.c:300`), `>FRAMER: closed` (`framer.c:169`),
    `Closed connection` (`socket.c:162`), **une ligne de préréglage par
    réception** — `framer.c:134` **ou** `:138`, l'une des deux étant émise à
    chaque appel de `framer_preset_result()` depuis `framer_receive()`
    (`framer.c:345`) — et jusqu'à trois `LOG_DEBUG` de suivi d'adresse ;
  - **conditionnelles, et il faut les compter comme telles** : `Waiting for`
    (`io.c:323`) ne vient que par `waitfor()`, donc sous la réserve `WAIT` du
    §A.2 **pour le seul chemin ordinaire** — sur le chemin `raw`, `waitfor()` est
    atteinte par `execCmd()` (`parser.c:359`) sans dépendre du jeu déployé ; le
    tampon reçu (`vcontrold.c:444`) n'est émis que sur la branche **unité
    convertie** (`vcontrold.c:442-444`) ;
- une **partie proportionnelle**, et elle est **asymétrique entre les deux
  sens** :
  - **à l'émission**, le décompte est exact : `my_send()` boucle sur le tampon
    (`io.c:128-131`) et émet **une ligne par octet envoyé** ;
  - **à la réception, non.** `io.c:287` est émise **une fois par retour de
    `read()`** (`io.c:268`), pour les `len` octets de ce lot, et ne journalise que
    `r_buf[i]` — le **premier octet du lot**. Le nombre de lignes est donc
    **majoré** par le nombre d'octets reçus, sans lui être égal. **La taille réelle
    des lots est un fait d'exécution non établi** : elle dépend de l'arrivée des
    octets sur la liaison, et rien ici ne l'établit ;
  - s'ajoute **une ligne de vidage** par réception complète (`io.c:299`).

  > **Une réserve sur cette asymétrie.** Elle vaut pour le chemin de lecture
  > **ordinaire**, qui passe par `receive_nb()`. Sur le chemin du mode `raw`
  > (§A.2), la réception passe par `receive()` et redevient **d'une ligne par
  > octet reçu** (`io.c:170`). **Que ce mode soit employé sur le site n'est pas
  > établi** ; s'il l'était, la majoration ci-dessous serait atteinte de plus
  > près.

Le nombre d'octets d'un échange P300 n'est **pas établi** par le constat ; l'ordre
de grandeur d'un télégramme de lecture se compte en dizaines d'octets, les deux
sens confondus.

> **Ce qu'on peut dire du facteur, et rien de plus.** Il est **majoré** par la
> partie décrite ci-dessus augmentée du nombre total d'octets échangés, soit un
> ordre de grandeur de **quelques dizaines**.
>
> Il a **une borne basse, mais plus basse que la sous-liste ne le laisse croire, et
> conditionnée au protocole**. Quatre lignes de cette sous-liste tombent si le
> périphérique n'est pas ouvert en P300 : `framer_open_p300()` n'est pas appelée
> (`framer.c:497-498`), donc pas de `>FRAMER: opened` ; `framer_send()` retourne
> par `my_send()` dès `framer.c:262-263`, donc pas de `>FRAMER: Command send` ;
> `framer_close_p300()` n'est pas appelée (`framer.c:510-511`), donc pas de
> `>FRAMER: closed` ; et `framer_preset_result()` tombe systématiquement à
> `framer.c:138`, son test `:131` exigeant `P300_LEADIN`. **Le protocole
> réellement déployé n'est pas établi par le constat.**
>
> **Ce qui demeure quel que soit le protocole**, pour une session qui ouvre le
> périphérique et exécute une commande qui résout : les **trois lignes de verrou**
> (`semaphore.c:139`, `:150`, `:158`), `Command:` (`vcontrold.c:277`),
> `>FRAMER: open device` (`framer.c:491`, émise **avant** tout test de protocole),
> **une ligne de préréglage par réception** (`framer.c:134` **ou** `:138`), et
> `Closed connection` (`socket.c:162`) — soit **au moins sept lignes**. Sous P300,
> les trois lignes de `framer` citées plus haut s'y ajoutent.
>
> **La borne haute reste une majoration, pas une estimation centrale ; il n'existe
> pas ici d'estimation centrale, et ce cadrage n'en fabrique aucune.** L'écart
> entre les deux bornes dépend de faits d'exécution non établis — taille des lots
> reçus, protocole réellement ouvert, composition conditionnelle du reste — et
> **ce cadrage ne les comble pas par une hypothèse**.

**Ce qui manque pour convertir ce facteur en volume par jour.** La cadence réelle
de connexions n'est **pas établie** : le constat relève une cadence de quelques
secondes lors du sondage de queue, mais **refuse explicitement de l'exploiter** —
cela relèverait d'une analyse qu'il n'a pas conduite. Le seul ancrage temporel que
le constat établisse est le superviseur : un déclenchement toutes les trois
minutes, soit **au plus 480 sessions par jour**. Ce que ce nombre borne, c'est le
**compte de sessions** — pas un volume : le convertir en lignes exigerait une
valeur centrale du facteur, que l'encadré précédent vient précisément de refuser.
**Ce cadrage ne la fabrique pas ici pour la reprendre ailleurs.**

> **Une valeur de cadence existe ailleurs, et ce cadrage ne la reprend pas — voici
> pourquoi.** `w4f1a-vcontrold-concurrency.md` §4.2 porte « le pont sonde le démon
> toutes les 10 s ; le superviseur toutes les 3 min », sourcé W4-C §8 et §9. Ce
> cadrage ne s'appuie pas dessus, et ce n'est **pas un oubli** : sa règle de
> sourçage est que **tout ce qu'il dit de l'installation vient du constat Acte A,
> et de rien d'autre**. Le constat n'a pas relevé la cadence du pont ; la valeur de
> §4.2 provient d'une campagne antérieure et n'a pas été réétablie depuis. Elle
> n'est donc **ni « établie » au sens de ce cadrage, ni inexistante** : elle est
> **connue d'une autre source, non réétablie ici**. **H-6 doit être arbitrée en le
> sachant**, et non en croyant qu'aucun chiffre n'existe.

> **Conséquence de méthode : le volume par unité de temps sous `debug` ne peut
> pas être estimé de façon défendable en l'état.** C'est une donnée manquante à
> établir **avant** toute activation, et non une inconnue à découvrir pendant.

### E.2 Espace disque

**Non établi.** Le constat ne relève **ni l'espace libre du système de fichiers,
ni l'existence d'une rotation** du journal. La pièce range explicitement rotation
et conservation parmi les faits d'installation non établis.

Deux observations de fait pèsent néanmoins :

- le fichier est **unique et de 456 Mio**, ce qui n'est pas la signature d'une
  rotation agressive ;
- le descripteur 3 du démon l'ouvre en **écriture seule**, et une rotation par
  renommage sans signal laisserait le démon écrire dans un fichier délié — le
  journal cesserait de croître visiblement tout en consommant l'espace.

> **Risque : saturation du système de fichiers.** Sur un hôte qui porte l'unique
> écrivain de production, une partition pleine n'est pas un incident de
> journalisation — c'est un incident de production, dont les effets dépassent
> largement le démon.

### E.3 Effet de la journalisation sur le comportement du démon

C'est le risque le moins visible et, à mon sens, le plus sérieux.

**Fait de code.** `logIT()` écrit puis **vide le tampon à chaque ligne** :
`fprintf(logFD, …); fflush(logFD);` (`common.c:110-111`). Il n'y a pas de
tamponnage applicatif — `setvbuf()` n'apparaît nulle part dans les sources. Chaque
ligne coûte donc **un appel système d'écriture**. En revanche, rien n'établit une
écriture **durable** par ligne : ni `fsync()`, ni `O_SYNC`, ni `O_DSYNC`
n'apparaissent dans les sources. L'écriture va au cache de pages du noyau ; sa
descente sur le support n'est pas commandée par le programme.

**Fait de code — et il faut le borner exactement.** Ces écritures ne sont **pas**
intercalées entre les octets **émis** : `my_send()` écrit le tampon entier par
`writen()` (`io.c:127`), **puis** journalise dans une boucle (`io.c:128-131`).
L'émission est terminée quand la journalisation commence. **L'intercalation est
réelle à la réception, et là seulement.**

Elle y procède d'une structure identique aux deux sites de mesure — `receive_nb()`
(`io.c:285-288`) et `receive()` (`io.c:168-171`) : l'horodatage courant est pris
**avant** la journalisation, et l'ancre est déplacée **après**.

    mid = times(&tms_t);          // horodatage pris AVANT
    logIT(LOG_INFO, "... (%0.1f ms)", ..., (mid - mid1) ...);
    mid1 = mid;                   // ancre déplacée APRÈS

L'intervalle rapporté au tour suivant part donc d'un instant **antérieur** à
l'exécution du `logIT()` du tour précédent : **il englobe cette exécution,
`fflush()` compris**.

Une correction d'attribution s'impose au passage : `receive_nb()`, qui est le site
de la session TCP, **n'arme aucune alarme**. Elle emploie `select()` avec
`tv.tv_sec = TIMEOUT` (`io.c:246-251`). L'alarme par octet (`io.c:159`) appartient
à `receive()`, hors du chemin de la session.

Trois conséquences :

1. **Allongement de la durée de session.** Chaque ligne coûte un appel système
   d'écriture. Sur une liaison série lente ce surcoût peut rester marginal ; sur
   un support lent ou une partition chargée, il ne l'est pas nécessairement.
   **Non quantifié — et non quantifiable sans mesure.**
2. **Effet d'observation direct, et démontré par la structure ci-dessus.** La
   grandeur rapportée à `io.c:287` n'est pas le seul écart entre deux arrivées :
   elle **inclut** le temps de journalisation du tour précédent. Les temps
   journalisés sous `debug` ne sont donc pas ceux du régime sans `debug`, et
   l'écart n'est pas un biais constant qu'on pourrait retrancher.
3. **Propagation à la file d'attente.** Sous `-n`, le service est strictement
   séquentiel : toute session allongée retarde la suivante. Le superviseur borne
   sa sonde à **5 secondes**. Un allongement des sessions rapproche l'ensemble du
   système de ce seuil, et un dépassement produirait un échec de sonde dont les
   conséquences ne sont pas établies.

> **Activer `debug` n'est pas une observation passive du système.** C'est une
> modification de son comportement temporel, sur le chemin même de l'écrivain
> réel de production.

### E.4 Durée d'exposition

Les séquences visées sont **répétitives** : le superviseur sonde toutes les trois
minutes, et la cadence du pont — **non réétablie par le constat, mais portée par
une autre source, cf. §E.1** — est vraisemblablement plus élevée.
La partie **répétitive** du rendement — appariement des verrous, présence de
`Command:` et de `>FRAMER: Command send` — devrait donc être visible **très
rapidement**, en quelques dizaines de minutes tout au plus.

Une exposition longue ne servirait qu'à capter des **événements rares** — refus,
erreurs, dérives — c'est-à-dire le domaine de `I1`, que le §A.3 a écarté du
rendement. **Il n'y a donc pas d'argument pour une exposition prolongée**, et il
y en a plusieurs contre : le volume croît linéairement avec elle, et la fenêtre
pendant laquelle la production tourne dans un état non nominal aussi.

### E.5 Autres risques identifiés

- **Deux interruptions**, pas une : l'activation et le retour arrière. Chacune
  frappe l'unique écrivain réel de production.
- **Dérive de l'état de sortie.** Une activation permanente qu'on oublie de
  retirer laisse la production dans un état non nominal, avec un journal dont la
  croissance est majorée par un facteur de quelques dizaines. `Restart=always` la
  reconduira indéfiniment.
- **Contenu du journal.** `Command: %s` journalise la commande émise et
  `vcontrold.c:444` le tampon reçu : le journal deviendrait beaucoup plus
  descriptif du fonctionnement du site. Le fichier est en `rw-rw-r--`, donc
  lisible au-delà de son propriétaire. Ce n'est pas un secret d'exploitation,
  mais c'est un changement de nature du contenu, à constater sciemment.
- **Erreur d'édition.** La route XML porte l'ensemble de la configuration ; une
  faute de syntaxe est fatale au démarrage et se manifesterait par une boucle de
  redémarrage plutôt que par un arrêt franc.
- **Absence de rendement sur ce qui bloque réellement.** `r < 0,485 s` reste hors
  d'atteinte, et la part extérieure du résidu de `H6` aussi. L'activation ne
  débloque **aucun** des deux verrous qui gouvernent l'exploitation en aval.

---

## F. Réversibilité et sortie

### F.1 Ce qu'il faudrait pour revenir

Rétablir la valeur ou l'option modifiée dans son état d'origine, puis relancer le
processus — le §D.3 établit qu'aucun rechargement à chaud ne suffit. **Le retour
arrière coûte donc exactement la même chose que l'aller** : une interruption de
l'unique écrivain réel de production.

Le journal produit pendant la fenêtre, lui, ne se retire pas par un retour de
configuration : l'espace consommé reste consommé jusqu'à une action distincte sur
le fichier, qui est un **troisième** acte, à cadrer séparément s'il devait être
nécessaire.

### F.2 L'état de sortie doit être **constaté**, pas supposé

> **Poser cette exigence est l'objet principal du présent paragraphe.** Une
> activation dont on croit être sorti, mais dont on ne l'a pas établi, laisse la
> production dans un état inconnu — ce qui est pire que l'état non nominal
> assumé.

Le retour à l'état d'origine devrait être établi par des constats indépendants et
convergents, chacun portant sur une chose différente :

1. **Les fichiers de configuration** — l'unité et le XML rendent la valeur
   d'origine, sans ambiguïté de précédence entre les deux routes.
2. **Le processus réellement en cours** — son invocation effective, et non
   seulement le fichier qui la définit. Ces deux choses ont divergé une fois
   déjà : l'unité déclare `User=root` et le processus tourne en `nobody`.
3. **Le journal lui-même** — sur les lignes **produites après** le retour
   arrière, l'absence des types `LOG_INFO` visés. C'est le seul constat qui porte
   sur le comportement observable, et non sur une déclaration. Il est de même
   nature que celui déjà conduit pendant la campagne autorisée.
4. **La reprise de service** — que le démon soit revenu à l'état d'un unique
   processus, détenteur du périphérique, servant ses clients.

Une empreinte relevée **avant** modification sur les deux fichiers de
configuration rendrait le contrôle 1 exact plutôt qu'approximatif. C'est une
précaution de coût nul, et elle transforme « on croit avoir remis comme avant » en
« on a établi que c'est identique ».

---

## G. Frontière du chantier proposé

Ce paragraphe décrit **ce qui serait autorisé et ce qui ne le serait pas si
l'humain autorisait l'exécution**. Il ne constitue pas cette autorisation.

### G.1 Lecture — le régime le moins engageant

Lecture de la configuration déployée, de l'invocation effective, du journal, de
l'état des processus et des descripteurs. **Aucune mutation, aucune interruption.**

C'est exactement le régime de la campagne déjà conduite, et **c'est le régime de
l'alternative du §C**, qui pourrait à elle seule constituer un périmètre complet.

### G.2 Mutation de configuration — engagement réel, réversible

Modification d'une valeur dans l'unité systemd **ou** dans le XML. Persistante,
réversible, **mais sans effet tant que le processus n'est pas relancé**.

À encadrer : une seule route à la fois, jamais les deux ; empreinte relevée avant
modification ; état d'origine établi avant de commencer.

### G.3 Interruption de service — le seuil qualitatif

Le redémarrage du démon. **C'est le franchissement qui distingue ce cadrage de
tout ce qui a précédé** : la campagne Acte A n'a jamais interrompu quoi que ce
soit.

À encadrer : interruption **aussi brève que possible**, fenêtre choisie
sciemment, comportement attendu du superviseur et du pont **instruits avant** et
non découverts pendant, et retour arrière préparé avant l'aller.

### G.4 Ce qui touche à l'écrivain réel — hors périmètre, absolument

**Rien de ce qui suit ne peut figurer dans un périmètre proposé, à aucun titre,
sous aucune formulation :**

- **aucune écriture chaudière**, sous quelque forme que ce soit ;
- **aucune commande `set*`**, ni exécutée, ni préparée, ni testée ;
- **aucun changement de writer** — le pont historique reste l'unique écrivain
  réel de production ;
- **aucune activation de la surface transactionnelle** — elle reste sans autorité,
  `False` ;
- **aucune modification du pont ni du superviseur** — ni leur code, ni leur
  configuration, ni leurs unités ;
- **aucun second ouvrant du périphérique**, ni instance de test, ni client
  concurrent : ce serait fabriquer soi-même le mode de défaillance que `H2`
  surveille.

> L'interruption du §G.3 **suspend** l'écrivain réel ; elle ne le **remplace**
> pas, ne le **double** pas, et ne s'y **substitue** à aucun moment.

---

## H. Ce que l'humain doit arbitrer

Formulé en questions tranchables. **Ce document ne prétend pas à la neutralité :
il prend position en deux endroits** — sur l'ordre des opérations au §C.3, sur la
balance au §I — et ces positions sont exposées là où elles sont argumentées. Elles
sont des **avis motivés**, non des réponses : chacune des questions ci-dessous
reste entière et appartient à l'humain.

**H-1 — Ordre.** La lecture de la résolution de `getTempKist` dans le XML déployé
(§C) doit-elle être conduite **avant** toute décision sur `debug` ? Ce qui est
écarté doit être nommé exactement : cette lecture **n'est pas la seule voie vers ce
fait** — sous `debug` une signature indirecte existe, `Command:` puis
`released lock` sans acquisition (§C.2 (a)), et le protocole de session le porte
par un quatrième moyen (§C.2 (b)). Ce qui lui reste en propre est de **ne pas
toucher au démon** — mais elle s'exécute sur l'hôte de production et **relève du
périmètre à autoriser** (§C.1, §G.1).

**H-2 — Suffisance.** Si cette lecture rendait un résultat décisif, la question de
`debug` serait-elle **close**, ou seulement **reposée** ?

**H-3 — Opportunité.** Le rendement du §A.3 — part interne de `H6`, deux
transitions sur cinq de `H3` — justifie-t-il **deux interruptions** de l'unique
écrivain réel de production ? L'arbitrage doit tenir compte de ce que ce rendement
**écarte lui-même** : il est **conditionnel** au mode d'accès des clients, connu
par configuration et **non observé** ; il est **borné à la population** des sondes
du superviseur, ce qui exclut la ligne « le pont » ; et il est **déformé par
l'observation** (§E.3). Voir les deux réserves du §B.4. À l'inverse, un terme joue
**en faveur** de l'activation et doit être compté : elle atteint la transition 4
par une signature discriminante (§C.2 (a)), ce que ce cadrage n'admettait pas.

**H-4 — Consommateur.** Quel travail ouvert consommerait cette réduction, et la
justification de la mutation doit-elle être subordonnée à l'existence d'un tel
travail ? À ce jour, `W4-F2` est fermé et non autorisé, aucun `T0`/`T1`/`T2` n'est
ouvert, et l'Acte B n'est pas ouvert.

**H-5 — Route.** Si activation il y a : unité systemd ou XML ? L'arbitrage porte
sur la surface d'erreur et la précédence (§D.5), non sur la commodité.

**H-6 — Préalable de volume.** Faut-il **exiger** que la cadence réelle de
connexions et l'espace libre soient établis **avant** l'activation, ou accepter
d'activer avec un volume par unité de temps non estimé (§E.1, §E.2) ? Ce qui est
écarté doit être nommé exactement : une valeur de cadence **existe** dans
`w4f1a-vcontrold-concurrency.md` §4.2, sourcée W4-C — ce cadrage ne s'en sert pas
parce qu'elle n'a pas été réétablie par le constat, non parce qu'aucun chiffre
n'existerait (§E.1). L'espace libre, lui, n'est établi **par aucune source**.

**H-7 — Durée.** Quelle fenêtre d'exposition, et **quel critère d'arrêt** ? Le
§E.4 indique que le rendement est acquis en dizaines de minutes ; l'arbitrage est
de savoir si la fenêtre est bornée **par le temps** ou **par l'obtention des
séquences visées**.

**H-8 — Effet d'observation.** Le §E.3 établit que `debug` modifie le
comportement temporel du démon sur le chemin de production. Ce risque est-il
accepté, et sous quelle réserve d'interprétation des temps journalisés ?

**H-9 — Comportement des clients.** Le comportement du superviseur et du pont
face à une indisponibilité n'est pas établi. Doit-il l'être **avant** toute
interruption, ou l'interruption est-elle jugée assez brève pour s'en dispenser ?

**H-10 — Sortie.** Les quatre constats de sortie du §F.2 sont-ils **exigés**, ou
un sous-ensemble suffit-il ?

**H-11 — Journal résiduel.** Que devient le volume produit pendant la fenêtre ?
Sa suppression ou sa réduction serait un **troisième acte**, non couvert ici.

**H-12 — Voie `dbgFD`.** Le §B établit qu'un flux équivalent **en forme** est
accessible en session, sans mutation ni redémarrage. Ce qui est écarté avec elle
doit être nommé exactement : elle n'observe que **la session observatrice**
(§B.3 a), **bloque le service** pendant sa durée (§B.3 c), n'est **pas persistée
par le démon** (§B.3 d), **n'améliore pas la résolution** (§B.3 f), exige une
**exécution sur l'hôte qui occupe le service séquentiel** (§B.3 g), et **déforme
la forme qu'elle montre** (§B.3 h) — d'un effet de **même nature et de même
inconditionnalité** que celui de l'activation, mais **de magnitude non établie**.
Elle atteint en revanche le **rechargement de configuration** en session
(§B.3 b). Cette voie doit-elle être examinée pour elle-même, ou tenue pour écartée
par le cumul de ces limites ?

---

## I. Verdict de cadrage

> **Avis de cadrage, non décision.** Il éclaire les arbitrages du §H ; il ne les
> tranche pas.

### I.1 Ce que je constate

Le rendement de l'activation est **réel mais étroit**, et il est **borné d'avance
par des limites que rien ne lève** :

- il réduit **la part interne de `H6`**, et **deux transitions sur cinq** de
  `H3` ;
- il ne clôt **aucune** des deux hypothèses ;
- il n'atteint **ni** la part extérieure du résidu de `H6`, **ni** `H1`, **ni**
  `H2`, **ni** `I1` ;
- il **ne lève pas** `r < 0,485 s`, la résolution du puits fichier étant à la
  seconde par construction, avec ou sans `debug`.

Le coût est **qualitativement supérieur** à tout ce que la campagne a engagé
jusqu'ici : **deux interruptions** de l'unique écrivain réel de production, un
volume de journal multiplié par un facteur **majoré par quelques dizaines**, dont
la borne basse est **d'au moins sept lignes par session et conditionnée au
protocole** (§E.1), et dont le débit réel **n'est pas estimable en l'état** ; un
espace libre **non établi** ; et une **modification du comportement temporel** du
démon sur le chemin même de la production, par appels système de journalisation
intercalés **dans la boucle de réception** d'un protocole série chronométré, à
l'intérieur même de l'intervalle que l'instrument rapporte.

Et il existe, non consommée, **une lecture qui atteint un fait dont aucun événement
du journal ne témoigne**, et qui est **la seule des trois voies comparées à ne pas
toucher au démon** (§C.2) — sans être pour autant hors du périmètre à autoriser
(§C.1, §G.1) — et dont l'un des deux résultats possibles changerait la nature du
problème.

### I.2 Mon appréciation

> **Non — le rendement ne justifie pas la mutation, en l'état.**

> **Ce que l'analyse de la voie `dbgFD` a déplacé, et il faut le dire.** Cette
> analyse aurait pu alléger la balance, en montrant qu'un flux équivalent était
> déjà accessible sans mutation. **Elle montre l'inverse** : le flux est
> équivalent **en forme**, pas **en population** (§B.4) — et cette forme y est
> elle-même déformée par l'observation (§B.3 h). Ce qui se trouve écarté est donc
> une **objection de redondance** qui aurait pu jouer contre l'activation : son
> rendement supplémentaire est presque entier, et **la mutation achète davantage
> que ce qu'un examen superficiel aurait laissé croire**.
>
> **Mais il faut être exact sur ce que cela déplace.** Ce n'est **pas le coût** —
> le §E est inchangé, et aucun terme du §B ne le touche. C'est une objection qui
> **n'avait jamais été portée au crédit du présent avis**. Le solde est donc
> **nul**, et **la conclusion ne change pas** : elle repose, comme avant, sur les
> raisons 1 et 2 ci-dessous, qu'aucun terme de cette analyse ne touche.

Trois raisons, par ordre de force :

1. **L'ordre est manifestement inversé.** Une lecture qui ne touche pas au démon,
   qui atteint la transition 4 sans témoin ni signature, et qui peut requalifier
   tout le problème, n'a pas été faite. Payer deux interruptions de production
   avant de l'avoir faite serait indéfendable. Cette raison seule suffit à
   différer.

   > **Cette raison a perdu une part de sa force, et il faut l'enregistrer ici, au
   > lieu même où ce document conclut.** Elle reposait, dans une rédaction
   > antérieure, sur une **exclusivité** : la transition 4 aurait été hors de
   > portée de `debug`. **Cette exclusivité est fausse et a été retirée** (§C.2).
   > Sous `debug` il existe une signature indirecte — plus forte encore que ce
   > cadrage ne l'admettait, `Command:` puis `released lock` sans acquisition
   > (§C.2 (a)) — et le protocole de session porte le fait par un quatrième moyen
   > (§C.2 (b)). Ce qui subsiste, et qui suffit encore, est **plus étroit** : la
   > lecture est la seule des trois voies comparées **à ne pas toucher au démon**,
   > et son résultat peut requalifier ce qu'il faudrait instrumenter. **La
   > conclusion est maintenue sur cette base rétrécie, et non sur celle qui a été
   > perdue.**

2. **Aucun travail ouvert n'attend cette réduction.** `W4-F2` est fermé et non
   autorisé, aucun `T0`/`T1`/`T2` n'est ouvert, l'Acte B n'est pas ouvert. Réduire
   `H3` et `H6` produirait un résultat sans destinataire actuel. Une mutation de
   production se justifie par un besoin qui la consomme ; ce besoin n'est pas
   constitué aujourd'hui.

3. **Ce qui bloque en aval resterait bloqué.** `r < 0,485 s` est hors d'atteinte
   du puits actif, et la part extérieure du résidu de `H6` est invisible par
   construction. L'activation ne débloquerait **aucun** des deux verrous. Elle
   améliorerait la connaissance de la part interne du verrou sans changer ce qui
   empêche d'avancer.

### I.3 Ce que cet avis ne dit pas

Il ne dit **pas** que l'activation serait techniquement dangereuse au point d'être
exclue : les risques du §E sont réels, ils sont instruits, et plusieurs sont
maîtrisables par un cadrage d'exécution soigneux.

Il dit que **le rapport entre ce qu'elle rendrait et ce qu'elle coûte n'est pas
favorable aujourd'hui**, principalement parce qu'une alternative gratuite n'a pas
été consommée et qu'aucun travail ouvert n'attend le résultat.

Si ces deux conditions changeaient — la lecture faite, et un travail ouvert qui
consomme la réduction — **la question devrait être reposée sur ces bases
nouvelles**, et cet avis ne la préjugerait pas. Poser une telle suite
n'appartient pas à ce cadrage.

---

## J. Frontières de ce document

Ce cadrage **n'ouvre rien** et **ne prépare rien**.

`W4-F0`, `W4-F1`, `W4-F1A` et l'Acte A demeurent `CLOSED`. L'Acte B demeure **non
ouvert**. `W4-F2` demeure **fermé / non autorisé**. Aucun `T0`, `T1` ni `T2`.

Les quatre statuts d'hypothèses, le régime `ADDITIF — CONDITIONNEL À H1/H2/H3/H6`,
`U-1`, `I1` et la borne `r < 0,485 s` sont **inchangés** : ce document les cite,
il ne les modifie pas.

Le pont historique demeure l'**unique écrivain réel de production** ; la surface
transactionnelle demeure **sans autorité**, `False`.

**Aucune opération terrain n'a été conduite, préparée ni suggérée.** La seule
vérification effectuée l'a été sur le code amont public et sur les deux pièces du
dépôt, en lecture.
