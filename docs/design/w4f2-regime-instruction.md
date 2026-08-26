# Instruction — établissement du régime

> **Ce document est une instruction documentaire.** Il n'exécute aucun terrain, ne
> mesure rien, ne modifie aucune configuration, et **ne tranche aucun régime**.
>
> Il **ne modifie aucun contrat**. `w4f1-confirmation-window.md` en Version 5 reste
> l'autorité normative sur `C1`, et n'est pas touché ici.
>
> **Version 3**, après réaudit de la V2. Une correction obligatoire : les
> transitions 3 et 5 y étaient données **ÉTABLIES** sur la foi d'une fixture que
> C5 §1 qualifie de **transcription**, non de recapture verbatim, et dont il dit
> qu'elle **n'est vérifiable contre aucun original**. Elles passent en **ÉTABLIES
> SOUS CORROBORATION**, et sont en outre **conditionnées aux transitions 1 et 2**
> pour cette commande et ce chemin. Trois précisions accompagnent : la
> corroboration répétée apportée par `c7-mqtt-read-contract.md` (§12.3), le jeu
> de lectures historique porté à **neuf**, et le statut réel d'`A5` — **déjà
> citée et exploitée**, seule la liste restant à extraire. **Régime, résidu
> doctrinal, prochain acte et frontières sont inchangés.**
>
> **Version 2**, après audit indépendant de la V1. L'audit a rendu `À CORRIGER`
> sur deux blockers et onze majeurs. Les corrections sont portées en place ; les
> deux blockers portaient sur la même faute, et elle est la plus lourde de la V1 :
> **avoir conclu de « absent du dépôt Boilerack » à « niveaux 1 et 2 épuisés »**,
> alors que le corpus versionné nomme lui-même les sources qui portent une part de
> la réponse. Le §12 les consomme, et il en résulte deux réductions que la V1
> attribuait à tort à des actes coûteux.

## 1. Décision humaine consignée

> **Instruire l'établissement du régime `ADDITIF` / `NON ADDITIF`, sans terrain ni
> mutation de production à ce stade.**

**Ce qu'elle autorise** : un lot documentaire d'instruction · la lecture exhaustive
du corpus et des sources disponibles · l'analyse statique du code, de l'amont et de
la configuration **déjà versionnée**.

**Ce qu'elle n'autorise pas** : aucune mesure terrain · aucun changement de
configuration · aucun `debug` · aucune mutation de production · pas d'Acte B · pas
de `T0` / `T1` / `T2` · aucune écriture chaudière.

## 2. Question unique

> Que faut-il exactement établir pour faire passer le régime de `INDÉTERMINÉ` à
> `ADDITIF` ou `NON ADDITIF`, et quelle part peut être démontrée sans terrain ?

## 3. État doctrinal de départ

W4-F2 `OUVERT — FINALISATION BOILERACK` · amendement normatif `C1` V5 **intégré**,
lot `CLOSED` · `w4f1-confirmation-window.md` V5 = autorité normative sur `C1` ·
précondition 9 / §11.2 **`NON DONNÉE`** · aucun terrain, aucun `debug`, Acte B non
ouvert, aucun `T0`/`T1`/`T2` · pont historique **unique écrivain réel** · surface
transactionnelle **sans autorité**, `false`.

> **Deux états distincts, que la V1 confondait par endroits.**
>
> | | Valeur |
> |---|---|
> | **niveau épistémique** atteint par la caractérisation amont | **`PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION`**, valeur **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`** |
> | **régime opératoire**, ce que `T0-B` rendrait aujourd'hui | **`INDÉTERMINÉ`** → branche **C** → `W4-F2 NON QUALIFIABLE — STOP` |
>
> `INDÉTERMINÉ` est **explicitement écarté au niveau épistémique** :
> *« elles sont nommées, falsifiables et rattachées à un maillon, ce que le cadrage
> §11.8 distingue du cas où l'on ne sait pas même les énoncer »*. Le régime
> opératoire vaut `INDÉTERMINÉ` **faute que les hypothèses soient déchargées** —
> `w4f1a-vcontrold-concurrency.md` §2 : *« c'est la valeur que `T0-B` prend faute
> de connaître `U-1` »*.
>
> **« Établir le régime » ne signifie donc pas produire un verdict à partir de
> rien : cela signifie décharger `H1`, `H2`, `H3` et `H6`.**

---

## 4. Définition canonique des trois régimes

Reprise de `w4f1a-vcontrold-concurrency.md` §6.2 à §6.4, **sans réinterprétation et
sans sémantique nouvelle**.

### 4.1 `ADDITIF` — six maillons, tous exigés

> *« Le verdict `ADDITIF` exige une preuve explicite de **chacun** des six
> maillons. Un seul manquant donne `INDÉTERMINÉ`. »*

| # | Maillon à prouver |
|---|---|
| 1 | la sonde du superviseur emprunte bien le chemin `vclient` considéré |
| 2 | ce chemin demande la ressource Optolink pertinente |
| 3 | cette ressource est **exclusive** entre clients concurrents |
| 4 | un second client demandeur **bloque** jusqu'à libération, sans service parallèle équivalent |
| 5 | après libération, la sonde paie **son propre** coût de transaction |
| 6 | aucune part pertinente du travail ne se recouvre d'une manière qui invaliderait la composition temporelle employée par `C1` |

### 4.2 `NON ADDITIF` — preuve positive exigée

> *« `NON ADDITIF` n'est pas résiduel. Il exige une **preuve positive, sur la
> population protégée**, que la composition additive employée par `C1` ne
> s'applique pas. »*

Sont **nommément insuffisantes** : un `fork()` à l'acceptation · plusieurs sockets ·
plusieurs processus ou fils · le rejet d'une commande inconnue avant Optolink · le
comportement d'une commande hors population du superviseur · **l'absence de preuve
d'additivité**.

> *« L'absence de preuve d'additivité donne `INDÉTERMINÉ`, jamais `NON ADDITIF`. »*

### 4.3 `INDÉTERMINÉ`

> *« Toute situation qui n'est ni 6.2 ni 6.3 : maillon manquant, population non
> isolable, régime dépendant d'une commande non classifiée, hypothèses
> d'installation non énonçables. »*

§6.4 précise que ce statut est identique au niveau épistémique `INDÉTERMINÉ` du
§11.8 — *« aucun troisième sens n'existe »*. **Le cas présent n'en relève pas au
niveau épistémique** (§3) : les hypothèses sont énonçables et rattachées. Il en
relève au niveau **opératoire**, par maillon manquant.

---

## 5. État exact de `U-1`

| Élément | Valeur canonique, verbatim |
|---|---|
| caractérisation amont | **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`** |
| `U-1` | **`PART AMONT ÉTABLIE SOUS H1/H2/H3/H6, RÉSIDU D'INSTALLATION OUVERT`** |
| régime **opératoire** | **`INDÉTERMINÉ`** |

> **La conversion du conditionnel en opératoire passe par la décharge de `H1`,
> `H2`, `H3` et `H6`, et par rien d'autre** — la caractérisation §5 rattache chaque
> maillon à ce jeu et à lui seul (§10.1).

---

## 6. `H1` — identité du démon déployé

**Énoncé exact** (`w4f1a-upstream-characterization.md` §7.1) :

> *« Le démon réellement déployé correspond au comportement amont caractérisé,
> **sans correctif local** modifiant les chemins de concurrence étudiés : boucle
> d'acceptation, sémaphore, ouverture et fermeture du périphérique. »*

**Ce qu'Acte A a établi** : binaire = `/proc/691/exe` · version compilée
`0.98.12-5-g8ca4797` · dépôt local **propre** à ce commit exact · **six blobs
identiques** à l'amont · aucun paquet propriétaire. **Statut : `PARTIEL`**
(constat : `PARTIELLEMENT RÉDUITE`).

**Résidu, verbatim du constat** : *« le lien binaire ↔ arbre au moment de la
compilation n'est pas prouvable passivement »*.

> **Correction V2 — un absolu est retiré.** La V1 écrivait « levable par **aucune**
> lecture », « **aucune trace** n'est disponible », « la trace de l'événement
> n'existe pas ». **Ces énoncés ne sont pas soutenus par le corpus.** Acte A dit
> *« non prouvable **passivement** »* et nomme la compilation comparative comme ce
> qui **suffirait** — c'est un énoncé de **suffisance**, non de non-existence de
> trace.
>
> **Traces enregistrées par Acte A §6 et non exploitées** : l'ELF est **non
> *stripped***, avec BuildID `d3309abd6f781a72deae786123357af73a998e0c` · le dépôt
> source local est présent, propre, au commit exact · les dates concordent —
> binaire 2026-03-17, XML déployé 2026-03-17. Aucune ne **prouverait** `H1` ; mais
> le lot ne peut pas affirmer qu'aucune n'existe.
>
> **Formulation retenue : `H1` est NON PROUVÉE PASSIVEMENT EN L'ÉTAT.** Ce que ce
> lot n'a pas fait, et signale : instruire ou écarter, avec motif, chacune de ces
> traces.

## 7. `H2` — absence d'un autre ouvrant

**Énoncé exact** (§7.4, **élargi** par la caractérisation) :

> *« Aucun autre processus concurrent n'ouvre la liaison pertinente en dehors du
> mécanisme d'exclusion partagé : ni une seconde instance de `vcontrold`, ni un
> processus tiers ouvrant le périphérique directement. »*

Deux faits amont fondent cet élargissement : la clé du sémaphore vient d'un
`mkstemp()` **par processus démon**, et `open(device, O_RDWR)` est **sans**
`O_EXCL`, `TIOCEXCL`, `flock` ni `lockf`.

**Ce qu'Acte A a établi** : une instance · `/dev/ttyUSB0` détenu par le PID 691
seul, par **deux méthodes indépendantes** · liaison locale · les deux clients
connus passent par TCP 3002. **Statut : `PARTIEL`.**

**Résidu, verbatim** : *« une observation instantanée ne vaut pas absence
historique ni future »*. Et : *« **ce résidu absorbe celui de `H6`** »*.

> **Correction V2 — la sur-quantification est retirée.** La V1 écrivait
> « **négatif universel sur le temps** … ni aucune série finie de constats … **non
> fermable par une lecture** ». **Le corpus ne porte pas cette portée.**
>
> La caractérisation §7.4 assigne au contraire à `H2` un **acte minimal fini** :
> *« constater les instances en service (le `pidfile` de `-P` y aide) et l'absence
> d'autre ouvrant du périphérique désigné par `-d` »*. On ne prescrit pas un acte
> fini pour un énoncé réputé infermable. Et `H6`, qui partage ce résidu, se borne
> explicitement *« pendant la fenêtre étudiée »*.
>
> **Portée retenue : `H2` est un invariant sur la population et la fenêtre
> protégées**, non sur l'histoire universelle.
>
> **Voies structurelles non instruites, et qui bornent l'ensemble des ouvrants
> possibles au lieu de constater un instant** : mode et groupe du nœud
> `/dev/ttyUSB0` — le démon tourne `nobody` / `dialout` (Acte A §8) — composition
> du groupe `dialout`, inventaire des unités installées et des binaires liant le
> tty. Passer d'« aucun ouvrant à l'instant *t* » à « l'ensemble des processus
> capables d'ouvrir est borné et énuméré » serait un **gain structurel**. Ce lot ne
> l'instruit pas et ne le propose pas ; il cesse d'affirmer qu'il n'existe pas.

## 8. `H3` — la sonde atteint la liaison

**Énoncé exact** (§7.5, **inchangé** depuis la caractérisation) :

> *« La sonde du superviseur émet une commande qui **atteint** la liaison
> Optolink. »*

Le constat Acte A décompose le maillon 2 en **cinq transitions** (§12.2). Voici
leur état après Acte A, après la lecture XML, **et après consommation des sources
de niveau 1** (§12).

| # | Transition (libellé canonique) | État | Fondement |
|---|---|---|---|
| 1 | l'unité exécute bien ce script, avec cet environnement | **NON ÉTABLIE** | fait d'exécution du superviseur ; aucun témoin |
| 2 | le script atteint `probe_mission` et substitue effectivement `$VCLIENT_CMD` **en une invocation `vclient`** | **NON ÉTABLIE** | idem |
| 3 | `vclient` transmet la commande au démon | **ÉTABLIE SOUS CORROBORATION**, pour cette commande et ce chemin, **et conditionnée aux transitions 1 et 2** | §12.2 — transcription fidèle, corroborée ; §12.3 — corroboration répétée |
| 4 | `getTempKist` **résout** dans le jeu de commandes du XML déployé pour `20CB` | **ÉTABLIE** | lecture XML — `addr 0802`, `len 2`, `unit UT`, `protocmd getaddr`, `P300` |
| 5 | exécution jusqu'à écriture et acquittement | **ÉTABLIE SOUS CORROBORATION**, pour cette commande et ce chemin, **et conditionnée aux transitions 1 et 2** | §12.2 — valeur physique restituée, corroborée ; §12.3 |

> **Correction V2 — la V1 se trompait sur les transitions 3 et 5.** Elle les
> déclarait établissables **seulement par une mutation** (`debug`), au motif que
> leurs seuls témoins sont des `LOG_INFO` écartés par la porte. **C'est faux par
> confusion entre un témoin de journal et un élément de preuve** : le §12.2 en
> produit un qui ne doit rien au journal.

> **Correction V3 — le statut « ÉTABLIE » était à son tour trop fort.** L'élément
> du §12.2 est une **transcription fidèle**, non une recapture verbatim, et C5 §1
> énonce lui-même qu'**aucune transcription n'est vérifiable contre un original**.
> Le statut retenu est donc **ÉTABLIE SOUS CORROBORATION**.

> **Et ces deux transitions sont conditionnées aux transitions 1 et 2 — y compris
> pour cette commande et ce chemin.** Ce qui est corroboré, c'est qu'une invocation
> `vclient -h localhost -p 3002 -c getTempKist` a atteint la liaison et rendu une
> valeur. Que **la sonde du superviseur** produise cette invocation reste
> exactement l'objet des transitions 1 et 2 : sans elles, 3 et 5 ne sont établies
> **d'aucune sonde**. Elles ne se lisent donc pas comme un acquis autonome, mais
> comme la partie **aval** d'une chaîne dont l'amont manque.
>
> **Ce qui subsiste : les transitions 1 et 2**, faits d'**exécution du
> superviseur** — et, par conséquent, la portée réelle de 3 et 5.

## 9. `H6` — libérations non appariées

**Énoncé exact** (§9.4) :

> *« Aucun client concurrent ne provoque, pendant la fenêtre étudiée, un chemin de
> libération non apparié élevant `semval` au-dessus de la valeur qui assure
> l'exclusivité. »*

### 9.1 Ce qui est **prouvé amont**

`vcontrol_semrelease()` **ne vérifie pas** la détention ; la branche `close` de
`interactive()` libère **sans tester `fd >= 0`** ; `framer_closeDevice()` n'a
**aucune garde**. Le sémaphore étant initialisé à **1**, `semval` peut dépasser 1.
`SEM_UNDO` ne répare qu'à la **terminaison du processus**, et sous `-n` cette borne
devient **la vie du démon**. Aucune exclusion périphérique de secours n'existe.

### 9.2 Le déclencheur, dans sa version à jour

> **Correction V2 — la V1 restituait un cadrage périmé.** Elle écrivait que
> l'activation *« dépend d'un comportement de client tiers, hors de la population
> protégée »*. C'est la formulation de la caractérisation §9.4, **corrigée depuis
> par le constat Acte A V2, §12.1(1)** :
>
> *« **Tous** les chemins de sortie de `interactive()` appellent
> `vcontrol_semrelease()` sans aucune vérification de détention … Une session close
> **sans** `quit` produit donc la même libération … la conclusion tient **a
> fortiori** — elle ne repose pas sur cette émission. »*
>
> **L'activation ne requiert donc ni tiers, ni double `close`.** Toute session qui
> se termine **sans avoir acquis** le périphérique produit une libération non
> appariée — y compris une session **de la population protégée**.

### 9.3 Résidus

| Réf | Résidu | Fermable par lecture ? |
|---|---|---|
| **(a)** | les commandes émises par le **pont** résolvent-elles toutes ? | **oui, en grande partie — et le §12.3 le fait** |
| **(b)** | un participant **extérieur** agit-il sur l'IPC System V en `0666` ? | **non** — c'est `H2`, dont le constat dit qu'il **absorbe** celui de `H6` |
| **(c)** | une session **de la population protégée** peut-elle se terminer **sans avoir acquis** le périphérique, et donc libérer sans appariement ? | **partiellement** — §12.3 ferme le cas de la non-résolution ; les autres chemins de sortie précoce restent ouverts |

**Statut : `PARTIEL`** (constat : `RÉDUITE, NON CLOSE`).

> **Ce que la lecture XML a fermé, et rien de plus.** `getTempKist` **résolvant**,
> le cas « commande rejetée avant Optolink » est écarté **pour la sonde**. Cela ne
> ferme ni **(b)**, ni les autres chemins de **(c)** — échec d'écriture vers le
> client, expiration, fin de boucle avant acquisition.

> **Borne d'instrumentation, portée par le constat §14.1.** L'état de `semval` et
> l'action d'un tiers **n'apparaissent dans aucun** des trois événements de verrou,
> **quel que soit l'état de `debug`**. Activer `debug` ne fermerait donc **pas**
> le résidu **(b)**.

---

## 10. Matrice des preuves

| Élément | Statut | Preuve disponible | Résidu | Terrain requis ? | Mutation requise ? |
|---|---|---|---|---|---|
| **`U-1`** | **`PARTIEL`** | niveau épistémique `PROUVÉ SOUS HYPOTHÈSES` ; valeur `ADDITIF — CONDITIONNEL À H1/H2/H3/H6` | décharge de `H1`, `H2`, `H3`, `H6` | selon l'hypothèse | non pour `H3` — voir §8 |
| **`H1`** | **`PARTIEL`** | binaire, version compilée, arbre propre, six blobs identiques, aucun paquet | lien binaire ↔ arbre à la compilation ; **non prouvé passivement en l'état** | oui | compilation comparative — **hors du périmètre autorisé à ce jour**, non listée au §G.4 |
| **`H2`** | **`PARTIEL`** | instance unique ; détenteur unique par deux méthodes ; pas de chemin connu vers le tty | invariant sur la fenêtre protégée, non établi dans la durée ; absorbe le résidu de `H6` | oui | non |
| **`H3`** | **`PARTIEL`** | maillon 1 **ÉTABLI** (canon) ; transition **4** établie ; transitions **3** et **5** **établies sous corroboration**, et conditionnées à 1 et 2 (§8, §12.2, §12.3) | **transitions 1 et 2** — exécution du superviseur — dont dépend aussi la portée de 3 et 5 | oui | **non** |
| **`H6`** | **`PARTIEL`** | chemin de non-résolution **fermé** pour la sonde ; commandes du pont largement couvertes (§12.3) | **(b)** = `H2` ; **(c)** chemins de sortie précoce | oui pour (c) | non |
| `H4` | **`NON APPLICABLE`** | **retirée du régime** (§7.2) — erreur de catégorie, requalifiée en limite quantitative réservée à `V-2` | — | — | — |
| `H5` | **`NON APPLICABLE`** | **supprimée** (§7.3) — tous les chemins d'échec de `vcontrol_seminit()` terminent le processus, et le démon sert effectivement | — | — | — |

> **Note de nommage.** `H4` et `H5` ci-dessus sont des **hypothèses de
> caractérisation**. `H-4`, au §14, est une **question d'arbitrage** du cadrage
> `debug`, sans rapport. Le trait d'union est le seul séparateur ; il est ici rendu
> explicite.

### 10.1 Les six maillons — affectation canonique restaurée

> **Correction V2 — la V1 défaisait deux corrections canoniques.** Elle déclarait
> le maillon **1** « manquant » et le rattachait à `H3` ; et elle retirait `H2` des
> maillons 3 et 6, `H6` des maillons 4 et 6. La caractérisation §5 porte l'inverse,
> dont un encadré intitulé **« Correction de l'affectation, aux maillons 4 et 6 »**.
> **L'affectation ci-dessous est reprise verbatim.**

| # | Statut canonique | Preuve | Hypothèse(s) |
|---|---|---|---|
| 1 | **ÉTABLI** | **dépôt** — W4-C §8 : *« il sonde le démon par un appel `vclient` **direct** »* | **aucune** |
| 2 | **NON ÉTABLI** | aucune | **`H3`** |
| 3 | **ÉTABLI** | amont | `H1`, `H2`, `H6` |
| 4 | **ÉTABLI** | amont | `H1`, `H2`, `H6` |
| 5 | **ÉTABLI** | amont | `H1` |
| 6 | **ÉTABLI** | amont | `H1`, `H2`, `H6` |

> **Un seul maillon manque : le 2.** La caractérisation le dit : *« Ici le maillon
> 2 manque, mais **par défaut d'un fait d'installation** — d'où `H3`, et un niveau
> conditionnel plutôt qu'`INDÉTERMINÉ` »*. C'est ce qui produit le niveau
> épistémique du §3, et non `INDÉTERMINÉ`.

---

## 11. Trois registres de preuve

> **Correction V2 — l'attribution était fausse.** La V1 attribuait cette
> discipline à `w4f2-c1-reexamen.md`, qui ne contient ni « registre », ni
> « conception », ni « installation nominale ». **La source réelle est le constat
> Acte A §11 — « Deux registres, à ne pas confondre » — et la
> caractérisation §8, frontière amont / installation. Ils en portent **deux** ; le
> troisième est un raffinement propre à ce lot, et il est signalé comme tel.**

| Niveau | Définition | Origine |
|---|---|---|
| **conception** | ce que le code **sait** faire | caractérisation §8, colonne « amont prouvé » |
| **installation nominale** | ce qu'un installateur ou une unité **prévoit** | **raffinement de ce lot** |
| **installation réelle** | ce que la machine **exécute** effectivement | Acte A §11, registre « observé » |

### 11.1 Ce que le dépôt contient — énumération explicite

| Source | Apport au régime |
|---|---|
| `install.py` | **aucun** — vérifié : zéro occurrence de `vcontrold`. Boilerack n'installe ni ne configure le démon |
| `systemd/boilerack.service` | **aucun** — unité de **Boilerack**, se déclarant « GABARIT, PAS UNE UNITE INSTALLEE. Aucune conformite terrain n'est revendiquee » *(citation verbatim, sans accents, comme le fichier)* |
| `docs/boilerack.example.toml` | **aucun sur le régime** — déclare comment Boilerack **joint** le démon (`host`, `port`, `executable`, `read_timeout_s`) |
| `src/boilerack/read_surface/measurements.py` | **oui** — porte la **table normative des huit commandes de lecture**, dont **`getTempKist`** (§12.3) |
| `tests/fixtures/vclient/` | **oui, décisif** — **neuf fixtures `vclient` versionnées** : **deux recaptures verbatim** et **sept transcriptions fidèles** au sens de C5 §1, dont la **transcription d'une lecture en production** (§12.2) |
| `docs/design/c5-vclient-contract.md` | **oui** — §1 provenance, méthode et **statut probant** des fixtures ; §9 durées |
| `docs/design/c7-mqtt-read-contract.md` | **oui** — §1.2 comportement du pont **relevé dans son code** ; §4.1 décompte ; §4.3 neuvième lecture (§12.3) |
| `docs/design/w4c-write-capture-protocol.md` | **oui** — §3 autorités `A5` / `A6` ; §5 fait `E2` ; §11.3 relecture (§12.3) |
| `docs/design/provenance.md` | **oui** — identifie le pont : dépôt, fichier, blob, commit, et la règle de reprise |
| `docs/design/w4f1a-*` | la caractérisation amont et son cadrage |
| code amont `openv/vcontrold` @ `8ca4797` | exploité par la caractérisation ; **`vito.xml` ne l'a pas été** (§12.4) |

> **Correction V2.** La V1 écrivait « `src/`, `tests/` : **rien** » et réduisait
> `docs/design/*` à « la caractérisation amont, déjà consommée ». **Les deux
> énoncés sont faux**, et le §12 en tire les conséquences.

---

## 12. Ce que les niveaux 1 et 2 établissent

> **Cette section est la correction du blocker de la V1.** Elle consomme les
> sources que la V1 déclarait épuisées, dans l'ordre prescrit par
> `w4f1a-vcontrold-concurrency.md` §10 — *« preuve déjà dans le dépôt ? »* puis
> *« preuve amont documentée ? »*.

### 12.1 Statut des deux niveaux

**Niveau 1 — dépôt : PARTIELLEMENT CONSOMMÉ par ce lot.** Il porte deux acquis
décisifs, §12.2 et §12.3.

**Niveau 2 — sources externes nommées par le corpus : NON CONSOMMÉ.** Le corpus les
nomme et les qualifie ; ce lot ne les a pas consultées, et ne les consulte pas
(§12.4).

### 12.2 La transcription de production — transitions 3 et 5

`tests/fixtures/vclient/read_ok_locale_production.json` est une **transcription
fidèle, versionnée**, d'une invocation `vclient` réelle du rapport de collecte
C5 :

| Champ | Valeur |
|---|---|
| `argv` | `["vclient","-h","localhost","-p","3002","-c","getTempKist"]` |
| `client_version` | **`0.98.12-5-g8ca4797`** — la version déployée |
| `collected_at` | `2026-08-02T16:16:20+02:00` |
| `returncode` | **0** |
| `duration_ms` | **2669** |
| `stdout` décodé | **`getTempKist:` / `28.000000 Grad Celsius`** |
| `stderr` | vide |

`c5-vclient-contract.md` §1 établit que la collecte a été faite sur le **poste de
référence** — *« Debian 13, aarch64, `vcontrold` en service continu »* — en
**lecture seule stricte**, et que les captures sont **versionnées** dans ce dépôt
et couvertes par des tests.

> **Statut probant exact — précisé en V3, et il faut le porter.** C5 §1 classe ses
> neuf fixtures en **deux recaptures verbatim** et **sept transcriptions fidèles**.
> Celle-ci est **une des sept**. Le même §1 poursuit : *« les répertoires de capture
> ayant été supprimés en fin de collecte, **aucune transcription n'est vérifiable
> contre un original**. La concordance des longueurs est une **corroboration forte,
> pas une preuve indépendante**. »*
>
> Ce qui est **corroboré**, et non prouvé de façon indépendante : la commande
> **`getTempKist`**, envoyée par **`vclient -h localhost -p 3002`** sur
> l'installation de référence, **a atteint la liaison Optolink et rendu une
> grandeur physique** — 28,000000 °C — en 2 669 ms, soit exactement le minimum de
> la plage `2 669 à 4 029 ms` que C5 §9 publie. Une valeur physique ne revient pas
> d'une transaction qui n'a pas abouti — **si la transcription est fidèle**, ce que
> la concordance des longueurs corrobore sans l'établir.
>
> Ce sont, pour **cette commande et ce chemin**, les transitions **3** et **5**, au
> statut **ÉTABLIES SOUS CORROBORATION**.

> **Ce que cette transcription n'établit pas.** Elle n'a pas été émise par le
> superviseur : la population de `C1` reste **les sondes du superviseur, et elles
> seules**. Elle ne dit donc rien des transitions **1** et **2** — **dont dépend
> pourtant la portée de 3 et 5 pour la population protégée**. Et C5 §1 précise
> qu'elle fut placée *« entre deux cycles du superviseur local, pour écarter toute
> contention avec lui »* — elle ne porte donc aucune information sur le
> comportement **sous contention**, ce que `H3` ne demande d'ailleurs pas.

> **Ce n'est pas l'inférence que la caractérisation interdit.** §7.5 écarte comme
> *« une inférence, pas une preuve »* le raisonnement tirant de la **durée** du
> budget que la sonde ferait une lecture réelle. Ici il ne s'agit pas d'une durée,
> mais d'une **transcription fidèle, corroborée**, de l'exécution et de son
> résultat. C'est d'un autre ordre que l'inférence écartée — **sans être pour
> autant une preuve indépendante**.

### 12.3 Les commandes du pont — résidu (a) de `H6`

Trois sources de niveau 1 le couvrent largement.

| Source | Apport |
|---|---|
| `w4c-write-capture-protocol.md` §5, fait **`E2`** | **« Quatre commandes d'écriture éprouvées : `setTempWWsoll`, `setTempRaumNorSollM1`, `setNiveauM1`, `setNeigungM1` »**, avec **`I-2` levée** — et le document précise qu'elles le sont *« par des mois d'usage, pas par un raisonnement »* |
| `w4c-write-capture-protocol.md` §11.3 | emploie **`getNiveauM1`** comme lecture réelle du protocole sur cette installation |
| `src/boilerack/read_surface/measurements.py` | table normative des **huit** commandes de lecture : `getTempA`, **`getTempKist`**, `getTempWWist`, `getTempWWsoll`, `getTempRaumNorSollM1`, `getTempRaumRedSollM1`, `getNeigungM1`, `getNiveauM1` |

> **Ce que cela établit.** Des commandes **éprouvées par des mois de production**
> sur cette installation **résolvent nécessairement** dans le jeu de commandes du
> XML déployé : une commande qui ne résout pas est rejetée avant Optolink et
> n'écrit rien. Le résidu **(a)** est donc **largement fermé au niveau 1**, pour
> les commandes nommées.

> **Corroboration répétée — ajoutée en V3.** `c7-mqtt-read-contract.md` §1.2
> établit le comportement du pont **« relevé dans son code, jamais supposé »** :
> **neuf lectures** publiées plus un état dérivé, soit **dix publications** (§4.1) ;
> les statuts `vcontrold` et Optolink **« dérivés d'une unique sonde
> `getTempKist` »** ; une publication **conditionnelle** — *« en cas d'échec,
> **rien n'est publié** »* ; et une **cadence mesurée** de télémétrie de
> **≈ 19-21 s**, pour 10 s configurées.
>
> **Ce que cette conjonction apporte.** Une publication qui n'a lieu qu'en cas de
> succès, et qui est **mesurée** à une cadence soutenue, corrobore de façon
> **répétée** que les commandes de lecture du pont **résolvent et atteignent la
> liaison** — `getTempKist` compris. C'est une corroboration **d'un autre type** que
> celle du §12.2 : non plus une transcription unique et datée, mais un régime
> observé dans la durée. **Elle reste une corroboration**, et ne porte que sur la
> population **du pont**, non sur celle du superviseur.
>
> Le jeu de lectures historique est donc de **neuf**, et non des huit de la table
> normative de Boilerack : `c7` §4.3 nomme la neuvième, **`getBrennerStatus`** —
> *« une commande historique observée — le pont historique la lit et publie sa
> sortie »* — reportée hors v1 faute de caractérisation, non faute d'existence.

> **Ce que cela ne ferme pas.** La **liste complète** des commandes du pont n'est
> pas dans ce dépôt. `provenance.md` identifie le pont — dépôt
> `antoinevalentinHA/boiler-bridge` **(privé)**, fichier `boiler_mqtt.py`, blob
> `992f9efa5d063dee7b0ccdec17351739b7371a1b`, commit
> `f14ba5c8498d3fc1706a4634ef5512a2af095bda` — et note que *« les commits
> ultérieurs du dépôt portent sur le guard, le déploiement et la sauvegarde »*.
> **`boiler_guard.sh` y est donc versionné.**

### 12.4 Niveau 2 — nommé par le corpus, non consommé ici

| Autorité | Ce qu'elle porte | Statut de reprise |
|---|---|---|
| **`A5`** — `arsenal` — `00_documentation_arsenal/outils_externes/boiler_pi/mqtt.md` §5 | *« commandes d'écriture **et de relecture**, bornes, pas, tolérances »* | **`A5` est public et citable** — `w4c` §3 |
| **`A6`** — `boiler-bridge` — `boiler_mqtt.py` | *« forme d'invocation éprouvée en production »* | **privé** — `w4c` §3 : *« ce document en reprend des **faits de comportement**, jamais du code, conformément à la règle de reprise de `provenance.md` »* |
| **amont `vito.xml`** | le jeu de commandes livré par `openv/vcontrold` @ `8ca4797`, dont `w4-arbitrage-activation-debug.md` établit qu'il est inclus par **XInclude** dans le XML déployé | fichier amont, déjà identifié ; **jamais lu** |

> **`A5` porte littéralement la liste que la V1 proposait d'aller chercher sur
> l'hôte.** Elle est **publique et citable**, et **n'exige aucun accès à
> l'installation**.
>
> **Précision V3 — `A5` n'est pas une source ignorée.** Elle est **déjà citée et
> exploitée** par le corpus : `w4c` s'y appuie pour les bornes, pas et tolérances
> (fait `E5`), pour le contrat métier d'un datapoint (§5.3, invoqué à trois
> reprises) et pour le comportement hors domaine (§11, inconnue `I-9`). **Ce qui
> reste à faire n'est donc pas de la découvrir, mais d'en extraire la liste des
> commandes** — un travail d'extraction sur une autorité déjà admise.

> **`A6` ne s'ouvre pas librement** : la règle de reprise n'autorise que des
> **faits de comportement**, jamais du code. Toute exploitation devrait s'y
> conformer.

---

## 13. Classification des actes

> **Correction V2 — la hiérarchie à sept niveaux de la V1 n'était pas canonique.**
> Elle était présentée comme « la hiérarchie des actes » ; **elle n'existe nulle
> part dans le corpus**. Elle est retirée. La classification ci-dessous emploie les
> **régimes du cadrage `debug` §G** et **l'ordre prescrit** de
> `w4f1a-vcontrold-concurrency.md` §10.

### 13.1 L'ordre prescrit de recherche — §10

| Étape | Question | État pour ce lot |
|---|---|---|
| 1 | preuve déjà dans le dépôt ? | **oui, et elle n'était pas consommée** — §12.2, §12.3 |
| 2 | preuve amont documentée ? | **oui, nommée, non consultée** — §12.4 |
| 3 | mesure dérivable d'une source existante ? | non |
| 4 | analyse locale hors terrain ? | épuisée par la caractérisation |
| 5 | instrumentation ? | non justifiée pour `U-1` |

### 13.2 Les régimes d'engagement — cadrage `debug` §G

| Régime | Contenu | Note |
|---|---|---|
| **`G.1`** — lecture | *« Lecture de la configuration déployée, de l'invocation effective, **du journal**, de **l'état des processus et des descripteurs**. Aucune mutation, aucune interruption. »* | **un seul régime** : lire un fichier et lire un journal y sont **au même rang**. La V1 les séparait en deux « niveaux », à tort |
| **`G.2`** — mutation de configuration | persistante, réversible, sans effet tant que le processus n'est pas relancé | — |
| **`G.3`** — interruption de service | le seuil qualitatif | — |
| **`G.4`** — hors périmètre, absolument | écriture chaudière · `set*` · changement de writer · surface transactionnelle · modification du pont ou du superviseur · second ouvrant du périphérique | **la compilation comparative n'y figure pas** |

### 13.3 Quatre catégories, à ne jamais confondre

> **Correction V2.** La V1 rangeait sous le seul mot « aucun niveau **autorisé** »
> des situations logiquement distinctes, et qualifiait `H1` d'**« interdit par le
> corpus »**. **C'est faux** : la classe d'interdiction absolue est `G.4`, et la
> compilation comparative n'y figure pas. Sa seule mention comme « interdite » est
> Acte A §1, dans la liste **« Opérations interdites, et non effectuées »** — une
> borne de **périmètre d'acte**, de même rang que « aucun `vclient` exécuté » et
> « aucun `restart` », qui ne sont évidemment pas des interdits permanents.

| Catégorie | Sens | Cas |
|---|---|---|
| **non autorisé dans ce lot** | l'acte existe, il n'est pas couvert par la décision du §1 | toute lecture sur l'hôte (`G.1`) |
| **hors du périmètre autorisé à ce jour** | l'acte n'a été autorisé par aucune décision, et n'est pas listé au `G.4` | compilation comparative — `H1` |
| **interdit par gouvernance** | listé au `G.4`, à aucun titre et sous aucune formulation | second ouvrant, `set*`, écriture chaudière |
| **non prouvé en l'état** | aucune source disponible ne l'établit ; rien ne dit qu'aucune n'existe | transitions 1 et 2 ; `H2` dans la durée |

## 14. `H-4` reste applicable

**Verbatim de la règle arbitrée** :

> *« Une mutation de production destinée **uniquement** à réduire une incertitude
> doit être justifiée par un travail ouvert qui consomme **explicitement** la
> réduction obtenue. »*

Le présent lot **établit un besoin** ; il **n'autorise pas** la mutation.

> **Correction V2 — une mutation n'est plus le sujet.** La V1 construisait une
> démonstration de nécessité de la mutation pour les transitions 3 et 5. **Cette
> démonstration tombe** : le §12.2 les établit **sous corroboration**, pour la
> commande et le chemin, au niveau 1, sans aucune mutation. **Aucun résidu
> identifié par ce lot n'appelle aujourd'hui une mutation.**

> **Et la V1 taisait une voie que son propre corpus nomme.** Acte A §9 porte une
> réserve d'inventaire : *« `debug on` **en session** arme `setDebugFD(socketfd)`,
> et l'émission se fait **en amont de la porte**, vers la socket du **client
> demandeur**, préfixée `DEBUG:` »*. Le programme **émet** donc ces événements sans
> mutation de configuration. Que cette voie ne capte vraisemblablement pas la
> session **du superviseur** — sous `-n` les sessions sont sérialisées et le
> descripteur est remis à `-1` à chaque fin de session — est un argument recevable ;
> **c'est celui qu'il fallait faire**, et non affirmer que le programme n'émet pas.

## 15. Résidu minimal, recalculé

> **Correction V2 — la liste de la V1 comptait deux fois le même fait.** Elle
> portait « maillon 1 — le superviseur exécute effectivement ce chemin » **et**
> « transition 1 — l'unité exécute bien ce script » comme deux entrées de natures
> différentes. Le maillon 1 est de surcroît **ÉTABLI** au canon.

**Formulation minimale, en maillons — la grammaire du corpus :**

| Résidu | Nature | Ce qui le fermerait |
|---|---|---|
| **maillon 2 non prouvé** — transitions **1** et **2** | faits d'**exécution du superviseur** | une preuve d'exécution ; aucune source de niveau 1 ou 2 ne l'apporte |
| **maillons 3, 4, 6 conditionnels à `H1`, `H2`, `H6`** | hypothèses d'installation | décharge de `H1`, `H2`, `H6` |
| **maillon 5 conditionnel à `H1`** | idem | décharge de `H1` |

**Et, à l'intérieur des hypothèses :**

| Hypothèse | Résidu exact |
|---|---|
| `H1` | lien binaire ↔ arbre à la compilation — **non prouvé passivement en l'état** ; traces non instruites au §6 |
| `H2` | invariant sur la fenêtre protégée, non établi dans la durée ; voies structurelles non instruites au §7 |
| `H6` | **(b)** = `H2` · **(c)** chemins de sortie précoce autres que la non-résolution |

> **Le résidu n'est pas réductible à un seul acte**, et il ne l'était pas
> davantage dans la V1 — mais il est **plus petit qu'elle ne le disait** : les
> transitions 3 et 5 en sortent, et le résidu **(a)** de `H6` en sort largement.

## 16. Le plus petit acte suivant, recalculé

> **Correction V2 — l'acte proposé par la V1 n'était pas le plus petit, et son
> rendement était sur-promis.** Elle proposait trois lectures **sur l'hôte** et
> annonçait qu'elles **établiraient** la transition 2 — ce que sa propre taxonomie
> interdit, une lecture ne produisant qu'une preuve **nominale** là où la
> transition est un fait d'**exécution**.

> **Le plus petit acte suivant n'exige aucun accès à l'hôte.**

**Acte : consulter `A5`** — le document `arsenal` désigné par `w4c` §3,
`00_documentation_arsenal/outils_externes/boiler_pi/mqtt.md` §5, **déclaré
publique et citable**.

| | |
|---|---|
| **régime** | **niveau 2** de l'ordre prescrit — source externe documentée. **Aucun régime `G` n'est engagé** : ce n'est pas un acte sur l'installation |
| **preuve attendue** | la liste des commandes d'écriture **et de relecture** du pont, à confronter au jeu de commandes déployé. **Il s'agit d'une extraction**, non d'une découverte : `A5` est **déjà une autorité admise et exploitée** (§12.4) |
| **ce qu'il fermerait** | le résidu **(a)** de `H6`, dans son intégralité et non plus « largement » |
| **ce qu'il ne fermerait pas** | transitions 1 et 2 · `H1` · `H2` · `H6` **(b)** et **(c)** |
| **autorisation requise** | **aucune au titre du terrain.** L'ordre prescrit du §10 en fait au contraire une **étape due avant tout acte supérieur** |

**Ensuite seulement, et dans cet ordre** : lire l'amont `vito.xml` (§12.4), qui
réduirait la part hôte de la vérification du jeu de commandes à une **comparaison
d'intégrité** — méthode déjà employée par Acte A sur les six blobs.

**Et seulement après** viendrait un acte `G.1` sur l'hôte, pour les transitions 1
et 2. Il **n'est pas proposé ici**, et le §16.1 dit pourquoi.

### 16.1 Ce qu'un acte `G.1` pourrait et ne pourrait pas

| | |
|---|---|
| **pourrait** | verser des éléments d'**installation nominale** — contenu du script, unité, environnement — et des éléments d'**exécution** : historique d'invocation de `boiler-guard.service` |
| **ne pourrait pas** | établir à lui seul les transitions 1 et 2 par la seule lecture d'un fichier : *« une lecture établit ce que le script **dirait** »*. Seule la part **journal** de `G.1` porte sur l'exécution |
| **réserve** | que le journal du superviseur contienne quoi que ce soit d'exploitable **n'est pas établi** |

> **Assertions retirées en V2.** La V1 affirmait qu'Acte A n'avait lu de
> `boiler_guard.sh` que « les lignes 9 à 12 et la ligne 69 », citait
> « `boiler_mqtt.py`, ligne 145 » et donnait `boiler-guard.service` pour
> `Type=oneshot`. **Aucune de ces trois précisions n'est portée par le corpus
> gelé** ; elles sont retirées. Ce que le corpus atteste : `boiler_guard.sh` **a
> bien été lu pendant Acte A** (constat §18), quatre variables en ont été tirées
> (§12), et le superviseur est déclenché par `boiler-guard.timer` →
> `boiler-guard.service`, `OnUnitInactiveSec=3min` (§11).

## 17. Aucun glissement vers `U-2` / `U-7`

Ce lot porte sur le **régime**, et sur lui seul. Ni `borne_sonde` / `U-2`, ni
`occupation_max` / `U-7` ne sont nécessaires pour **définir** le régime.

> **Même si `ADDITIF` était établi, `T0` resterait bloqué par `U-2` et `U-7`**
> (conditions 1 et 2 de `T0 GO`). **Les deux problèmes sont distincts et ne se
> compensent pas.**

## 18. Réponses

### Q1 — `ADDITIF` établissable depuis le corpus et les sources statiques ?

> **Non.**

Le maillon **2** manque, et son résidu — transitions **1** et **2** — porte sur
l'**exécution du superviseur** : aucun corpus statique ne peut établir qu'une
machine exécute. Les maillons 3 à 6 restent conditionnels à `H1`, `H2`, `H6`, dont
les résidus ne sont pas statiquement fermables.

> **Mais la V1 sous-estimait ce que le statique donne déjà** : la transition **4**
> est **établie**, les transitions **3** et **5** le sont **sous corroboration** —
> et conditionnées à 1 et 2 —, et le maillon 1 l'était déjà au canon.

### Q2 — `NON ADDITIF` établissable depuis le corpus et les sources statiques ?

> **Non.**

Il exige une **preuve positive sur la population protégée**. Aucune source n'en
fournit. Le seul candidat — le chemin de libération non appariée — est un **risque
conditionnel, non un verdict**, et §6.3 range *« l'absence de preuve
d'additivité »* parmi les preuves insuffisantes.

### Q3 — Résidu minimal exact

Voir §15 : **maillon 2** (transitions 1 et 2) · **maillons 3, 4, 6** conditionnels
à `H1`, `H2`, `H6` · **maillon 5** conditionnel à `H1`.

### Q4 — Ce que le résidu exige

| Résidu | Acte |
|---|---|
| `H6` **(a)** | **niveau 2** — `A5`, publique et citable. **Aucun accès hôte** |
| transitions 1 et 2 | **`G.1`**, part **journal** — non autorisé dans ce lot |
| `H1` | **hors du périmètre autorisé à ce jour**, non listé au `G.4` |
| `H2`, `H6` **(b)** | non prouvés en l'état ; voies structurelles `G.1` non instruites (§7) |
| `H6` **(c)** | `G.1` ou analyse amont complémentaire |

### Q5 — Plus petit acte suivant

Voir §16 : **consulter `A5`**, source de **niveau 2, publique et citable, sans
accès à l'installation**.

> **Aucun acte identifié par ce lot ne tranche le régime** — et l'énoncé est
> borné : il vaut pour les actes que ce lot a identifiés, non pour l'ensemble des actes
> concevables.

## 19. Statut final du régime

> **Niveau épistémique : `PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION`, valeur
> `ADDITIF — CONDITIONNEL À H1/H2/H3/H6`.**
>
> **Régime opératoire : `INDÉTERMINÉ`** → branche **C** →
> **`W4-F2 NON QUALIFIABLE — STOP`**. **Inchangé.**

Aucune conclusion par défaut n'est émise : §6.3 l'interdit pour `NON ADDITIF`, et
§6.2 exige les six maillons pour `ADDITIF`.

## 20. Risques et points non résolus

1. **Le niveau 2 n'est pas consommé.** `A6` et l'amont `vito.xml` sont nommés par
   le corpus et restent à consulter. Pour **`A5`, la formulation exacte est autre** :
   elle est **déjà une autorité admise et exploitée** par le corpus (§12.4) — **il
   reste à en extraire la liste des commandes**, ce qui est un travail
   d'extraction, non de découverte. **L'ordre prescrit du §10 fait du niveau 2 une
   étape due avant tout acte supérieur**, et ce lot ne l'a pas franchie.
2. **`H1` et `H2` restent les verrous durables.** Ce lot cesse d'affirmer qu'ils
   sont infermables ; il constate qu'**aucune voie qu'il a identifiée** ne les
   ferme, et il nomme au §6 et §7 des voies non instruites.
3. **Conséquence pour l'arbitrage** : si `H1` et `H2` demeurent `PARTIEL`, la
   branche **C** est stable — mais **cette stabilité n'est pas démontrée**, elle
   est constatée sur l'état actuel des preuves.
4. **La transcription de production est datée** — 2026-08-02. Elle corrobore qu'une
   lecture a abouti ce jour-là, non qu'elle aboutit toujours. Elle n'est toutefois
   **pas isolée** : §12.3 lui adjoint une **corroboration répétée** — publication
   conditionnelle du pont à cadence mesurée — d'un autre type et sur une autre
   population. Le résidu tient donc à la **nature corroborante** de ces éléments,
   non à leur nombre.
5. **`H6` (c) est un résidu nouveau**, dégagé par la correction du §9.2 : les
   chemins de sortie précoce autres que la non-résolution n'ont pas été inventoriés.
6. **La part `G.1`-journal reste incertaine dans son rendement** : que le journal du
   superviseur porte quoi que ce soit d'exploitable n'est pas établi.

## 21. Ce que ce document ne fait pas

Il ne tranche aucun régime · il n'émet aucune conclusion par défaut · il ne crée
aucune hypothèse, aucun seuil, aucune constante, aucune hiérarchie normative,
aucun protocole terrain, aucune commande de production · il ne modifie aucun
contrat · il n'ouvre ni Acte B, ni `T0` / `T1` / `T2` · il n'autorise aucun terrain,
aucune lecture sur l'hôte, aucune inspection de journal, aucune mutation · il ne
relance pas Acte A · il ne consulte ni `A5`, ni `A6`, ni `vito.xml`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.** Le pont historique demeure
l'unique écrivain réel de production ; la surface transactionnelle demeure sans
autorité, `false`.
