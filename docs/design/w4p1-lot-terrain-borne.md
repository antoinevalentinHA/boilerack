# `W4-P1` — premier lot terrain borné, en lecture seule

> **Version 3**, après ré-audit. La V2 fermait quatre bloqueurs de fond ; le
> ré-audit portait sur l'**exécutabilité pratique** — et deux de ses constats
> auraient fait échouer le lot dès sa première heure.
>
> | | Correction |
> |---|---|
> | **V3 · D1** | **`R2` retypée.** La V2 exigeait que **toutes** les unités consultées gardent état et date de démarrage identiques — **y compris `<unité-superviseur>`, dont le cycle périodique est précisément l'objet du lot**. La preuve d'invariance aurait échoué sur un comportement **nominal**. Les deux régimes sont désormais séparés : **`R2a`** unités invariantes, **`R2b`** unité cyclique |
> | **V3 · D2** | **`P1A-3` corrigée.** Elle déclenchait `ABORT` sur *« le superviseur […] redémarre »* — c'est-à-dire **à chaque cycle nominal**. Le déclencheur distingue maintenant trois cas, et **le cycle périodique attendu n'en est pas un** |
> | **V3 · D3** | **Portée de `R1` bornée** aux **fichiers de configuration** lus. Le **journal système** lu par `B1` est **alimenté en continu** : lui imposer taille, date et condensat identiques était une exigence contradictoire avec sa nature |
> | **V3 · D4** | **Repli prospectif** doté d'une **règle d'exploitation** — attente minimale, aucune surveillance, aucune session, aucune action ; `STOP`/`ABORT` si l'attente devient inutile. **Aucun plafond nouveau, aucune durée nouvelle** |
> | **V3 · R-6** | **`A6`(iii) supprimé.** Le critère *« paramètres susceptibles de porter une borne structurelle »* était **ouvert**, donc incompatible avec une liste close. **Aucune pièce du corpus ne détermine un tel paramètre** : plutôt que d'en inventer un, `A6` est borné aux **deux éléments effectivement déterminés**, et le §5.1.3 en tire la conséquence sur le verdict |
> | **V3 · R-7** | **Précédent `w4f2-vito-xml-instruction.md` §15 : couverture exacte.** Ce qui en est **repris** et ce que **`W4-P1` ajoute** sont désormais distingués — le précédent ne couvre ni l'objet de `A-O3`, ni l'empreinte du §6.1 |
> | **V3 · R-8** | **Ancre corrigée** : *« aucun substitut admis »* est porté par **`w4f1` §9**, table `U-2` — qui renvoie au §8.3, mais n'est pas le §8.3 |
> | **V3 · R-9** | **Interprétabilité de `B-O2`** : le rapport **MUST** dire si l'invocation observée est **nominale, en échec ou indéterminée** quand la source le permet ; sinon, consigner que les durées **mélangent potentiellement des régimes** et ne forment **pas une population homogène** |
>
> **Version 2**, après audit `NO-GO`. Quatre bloqueurs fermés, cinq réserves
> traitées.
>
> | | Correction |
> |---|---|
> | **V2 · B1** | **`A-O3` avait un objectif sans acte permis.** La liste close ne portait aucune lecture capable de l'instruire. Un acte **`A6`** est ajouté — lecture **ciblée** de `<config-démon>`, bornée sur le modèle de `w4f2-vito-xml-instruction.md` §15 — et le repère correspondant au §1.1. Le verdict négatif devient **`AUCUNE IDENTIFIÉE SUR LE PÉRIMÈTRE LU`** |
> | **V2 · B2** | **Registre corrigé.** *« commande réellement émise »* → **configurée / déclarée** ; *« timeout réellement imposé »* → **configuré / déclaré**. Nouveau §5.1.1 : **une lecture de configuration n'est pas une preuve d'exécution** |
> | **V2 · B3** | **Verdict `A-O1` élargi** à quatre valeurs, dont **`RECOUVREMENT PARTIEL`**, qui exige d'indiquer **l'intersection exacte** et sa conséquence pour une discrimination par `Command:`. **Aucun cas réel n'est préjugé** |
> | **V2 · B4** | **`M6` cesse d'être le nom de ce que systemd ne mesure pas.** `B-O1` porte sur l'attribution des **invocations** de l'unité ; `B-O2` sur une **durée d'enveloppe d'invocation**, typée par cinq énoncés — elle **ne vaut pas `M6`**, n'est **pas** une borne de sonde, n'y est **pas** substituable |
> | **V2 · R-1** | mode prospectif **autorisé par arbitrage humain**, sous la seule forme *« attendre puis relire rétrospectivement »* ; contradiction du *« temps déjà écoulé »* corrigée. **Plafond de 4 heures conservé tel quel** |
> | **V2 · R-2** | rappel que **`Command:` est aujourd'hui muet** — `LOG_INFO` derrière `debug` — et qu'un `A-O1` favorable **n'est pas** une capacité d'observation actuelle |
> | **V2 · R-3** | ancre corrigée : le verbatim `VCLIENT_TIMEOUT=5` cité est celui de `w4f2-c1-reexamen.md` **§4.2**, non du §3.4 |
> | **V2 · R-4** | **`B2` et `R3` alignés** : la preuve d'absence de redémarrage du démon couvre **le lot entier**, jambes A et B comprises |
> | **V2 · R-5** | **relevé partiel en cas d'`ABORT`** traité : acte `B4` et preuve `R6` — conservé tel quel, **jamais complété ni reconstitué** |
>
> **Version 1.** Ouverture et bornage initial.

> **LOT BORNÉ, PAS EXÉCUTÉ.** Ce document **borne** une expérience et
> **réunit** les six éléments exigés. Il ne l'exécute pas, et il ne l'autorise
> pas : l'**élément 6 — autorisation propre — n'est PAS donné par ce document**.
>
> **Aucune mesure n'est relevée ici. Aucun seuil, aucun critère, aucune borne
> qualifiée. `T0` demeure NON AUTORISÉ. `T1` n'est pas approché.**

---

## 1. Désignation

Le lot est désigné **`W4-P1`**.

**Vérification que la désignation est libre** : dix-huit désignations `W4` sont en
usage dans le dépôt — `W4-A` à `W4-Q`, `W4-E1`, `W4-E2`, `W4-F0` à `W4-F6` et
`W4-F1A` compris. **Aucun `W4-P1` n'existait.**

**Ce que ce nom fait, et ne fait pas** : `W4-P1` est un **sous-lot d'expérience de
`W4-P`**. Il n'est pas une phase de `T0`, ne porte aucune de ses lettres, et
**MUST NOT** être présenté comme en tenant lieu.

### 1.1 Désignations locales

Le dépôt est **public**. Les objets de l'installation sont désignés par des
**repères**, résolus à l'exécution depuis la référence locale, **hors dépôt** :

| Repère | Objet |
|---|---|
| `<unité-pont>` | l'unité du pont historique |
| `<timer-guard>` | le déclencheur périodique du superviseur |
| `<unité-superviseur>` | l'unité déclenchée par `<timer-guard>` |
| `<script-superviseur>` | le script exécuté par `<unité-superviseur>` |
| `<source-pont>` | la source effective du pont |
| `<unité-démon>` | l'unité de `vcontrold` |
| `<config-démon>` | le fichier de **configuration déployée** de `vcontrold` |

**Aucune valeur de site — chemin, hôte, port, nom d'unité, sujet — n'est écrite
dans ce document ni dans aucun artefact qu'il produira au dépôt.**

## 2. Autorité amont

| Source | Ce qu'elle fournit |
|---|---|
| `w4q-precondition2-arbitrage.md` **décision 5** | *« Le terrain est ouvert **EN PRINCIPE** »* pour les expériences du lot distinct, sous **six éléments**, dont *« son **autorisation propre**, distincte de la présente »* ; et *« **`T0` demeure NON AUTORISÉ**, et cette ouverture ne le concerne pas »* |
| `w4p-ouverture.md` **§9** | *« La preuve directe n'est pas à éviter »* ; expériences nommées à ce jour : **aucune** ; ce qu'une expérience exigera : les six éléments |
| `w4p-ouverture.md` **§5** | les **frontières négatives**, opposables pour toute la durée de `W4-P` |
| `w4p-sortie1-instruction.md` **§7** | les **huit points** soumis |
| **Arbitrage humain du §3** | ce qui rend le présent lot ouvrable |

## 3. L'arbitrage humain, consigné

> **Rendu après intégration de la sortie 1. Il tranche cinq points sur huit, en
> réserve un, et en diffère deux.**

| # | Décision |
|---|---|
| **1** | **Non tranché.** Le choix entre maintien, reformulation et amendement *« dépend des faits restant à établir »* |
| **2** | Toute future expérience visant `U-1` **devra respecter les conditions applicables à `T0`**, et son résultat **devra être homologable comme résultat de `T0-B`**. **Aucun `T0-B` n'est lancé** |
| **3** | **Partage retenu** : l'acquisition et l'observation de `M6` sont **autorisables comme acte distinct au titre du §8.3** ; **toute qualification d'une borne reste réservée au mécanisme prévu par `T0-D`**. *« Une mesure ne vaut donc jamais, à elle seule, borne qualifiée »* |
| **4** | **Lecture retenue** : `T0` peut rendre `U-7` **mesurable** sans nécessairement **mesurer** `U-7`. **Aucune correction documentaire demandée** |
| **5** | **Autorisation neuve, bornée par lot.** Le premier lot **recevra sa propre autorisation explicite**. **Aucune exposition hors `T1` n'est autorisée** |
| **6** | La réserve sur la bornabilité de `U-7` sera instruite **comme sous-question du rapport du premier lot utile**. **Pas de cadrage distinct** |
| **7** | La piste du mécanisme est instruite **dans le premier lot, par lecture de configuration**. Elle **reste une piste, sans présomption d'existence** |
| **8** | **`T0` reste NON AUTORISÉ**, et n'est pas ouvert |

> **Décision d'ouverture** : `GO — PREMIER LOT TERRAIN W4-P À BORNER ET
> EXÉCUTER`. **Borner d'abord.** L'exécution attend l'élément 6.

### 3.1 Deux points rendus à l'occasion de la V2

Ils portaient sur le bornage, non sur l'exécution.

| Point | Décision |
|---|---|
| **mode prospectif de repli** | **AUTORISÉ**, et **uniquement** sous la forme *« attendre puis relire rétrospectivement »* — **sans `follow`, sans surveillance continue, sans session ouverte** |
| **plafond de 4 heures** | **CONSERVÉ TEL QUEL** |

> **Aucune durée nouvelle n'est fabriquée par la V2.** Les seules durées du
> document sont le plafond de 4 heures, conservé, et le budget de 5 s, cité de
> son contrat.

> **Ces deux points ne sont pas l'élément 6.** Ils bornent le lot ; ils **ne
> l'autorisent pas** — §9.

---

# Les six éléments

## 4. Élément 1 — Périmètre

**Le lot a deux jambes, et deux seulement.**

| Jambe | Objet | Nature |
|---|---|---|
| **A** | lecture de configuration | **lecture de fichiers et d'unités**, aucune exécution du dispositif |
| **B** | observation du superviseur par sa propre unité | **lecture d'enregistrements**, en priorité **rétrospective** |

**Le périmètre inclut** : les deux clients connus du démon — pont et superviseur —
et le démon lui-même, **en tant qu'objets lus**.

**Le périmètre exclut, explicitement** :

- **`vcontrold`** — aucune modification, **aucun changement de verbosité**, aucune
  session `debug`, aucune connexion cliente ouverte par le lot ;
- **Boilerack** — aucun déploiement, aucun démarrage, aucune unité créée ;
- **la chaudière** — aucune écriture, aucune commande ;
- **le dispositif historique** — ni arrêté, ni désactivé, ni modifié, ni
  reconfiguré, ni redémarré ;
- **`T0`**, **`T1`**, **`T2`** — aucune phase, sous aucun nom ;
- les **quatre actes réservés** du `w4f-write-sovereignty.md` §11.1.

### 4.1 Fenêtre de la jambe B

**Mode primaire : rétrospectif.** La jambe B lit ce que le journal système
**retient déjà**. Elle n'attend rien et n'observe rien en direct.

| | |
|---|---|
| Fenêtre | **une seule**, continue, **bornée à 4 heures** de temps **couvert par le relevé** |
| Suivi continu | **interdit** — aucune session de suivi, aucun `follow`, aucune session laissée ouverte |
| Nombre d'invocations attendu | **non présumé** — il dépend de la cadence, que **la jambe A établit**. Aucune valeur n'est supposée ici |

> **Correction de la V1.** La V1 écrivait *« 4 heures de temps **déjà écoulé** »*,
> ce qui **contredisait** le repli prospectif qu'elle prévoyait par ailleurs. La
> fenêtre est désormais définie par le **temps qu'elle couvre**, et c'est le
> **moment de la lecture** qui distingue les deux modes.

### 4.2 Le repli prospectif, dans sa seule forme permise

**Autorisé par l'arbitrage du §3.1**, si et seulement si le mode rétrospectif ne
retient rien d'exploitable.

| | |
|---|---|
| Forme, et **la seule** | **attendre**, puis **relire rétrospectivement** |
| Ce que « attendre » veut dire | **ne rien faire** — aucune session, aucun processus, aucune connexion, aucune observation en cours pendant l'attente |
| Ce qui reste interdit | **`follow`**, surveillance continue, session laissée ouverte, échantillonnage périodique, déclenchement de quoi que ce soit |
| Borne | **la même**, **4 heures** de temps couvert — **inchangée**, et non cumulable avec le relevé rétrospectif |

> **Le repli ne change pas la nature de l'acte.** Après l'attente, la lecture est
> **exactement** l'acte `B1` : une lecture rétrospective, unique, non continue.
> **Il n'ajoute aucun acte à la liste close du §6.**

#### Règle d'exploitation de l'attente

**Aucun plafond nouveau n'est créé, et aucune durée n'est fabriquée.** Ce qui
suit borne la **conduite** pendant l'attente, non sa durée.

| # | Règle |
|---|---|
| 1 | **ne pas attendre au-delà de ce qui est nécessaire** pour qu'un nouvel événement exploitable existe |
| 2 | **aucune surveillance active** pendant l'attente |
| 3 | **aucune session ouverte** pendant l'attente |
| 4 | **aucune action**, d'aucune sorte, pendant l'attente |
| 5 | si l'attente **devient inutile**, ou si le **contexte change** : `STOP` ou `ABORT` **selon les règles existantes** du §7 — aucune règle nouvelle |

> **« Attendre » n'est pas un acte du lot.** C'est l'absence d'acte. Rien n'est
> lancé, rien n'est tenu ouvert, rien n'est échantillonné. La seule chose qui
> reprend après l'attente est `B1`.

## 5. Élément 2 — Objectif

> **L'objectif est d'ÉTABLIR DES FAITS, jamais de qualifier une borne.** La
> décision 3 le pose : *« une mesure ne vaut jamais, à elle seule, borne
> qualifiée »*.

### 5.1 Jambe A — objectifs et verdicts admissibles

| Réf | Objectif | Verdicts admissibles |
|---|---|---|
| **A-O1** | établir la **commande CONFIGURÉE / DÉCLARÉE** par chaque client, pour instruire **`H3`** | `COMMANDES DISJOINTES` · `COMMANDES IDENTIQUES` · **`RECOUVREMENT PARTIEL`** · `INDÉTERMINÉ` |
| **A-O2** | établir le **timeout CONFIGURÉ / DÉCLARÉ** imposé à `vclient` par le superviseur | valeur relevée, **avec sa source exacte** · `NON ÉTABLI` |
| **A-O3** | **rechercher**, sur le **seul périmètre lu par `A6`** — deux éléments, §6.1 —, l'existence d'une **borne structurelle déterministe strictement inférieure à 5 s** | `CANDIDATE IDENTIFIÉE` · **`AUCUNE IDENTIFIÉE SUR LE PÉRIMÈTRE LU`** · `INDÉTERMINÉ` |
| **A-O4** | relever la **cadence déclarée** du déclencheur, nécessaire au dimensionnement de la jambe B | valeur relevée · `NON ÉTABLI` |

### 5.1.1 Registre — une configuration n'est pas une exécution

> **Tous les objectifs de la jambe A relèvent du registre de la CONFIGURATION
> LUE, et d'aucun autre.** Le constat Acte A §11 tient déjà les deux registres
> séparés : les deux clients y sont *« **connus par configuration**, non observés
> en train d'exécuter »*, et *« **aucun témoin d'exécution** ne rattache ce mode
> d'accès à l'une ou l'autre unité »*.
>
> **`W4-P1` MUST NOT** transformer une lecture de configuration en preuve
> d'exécution, ni écrire qu'un client « émet », « impose » ou « exécute » quoi que
> ce soit sur la foi d'un fichier. Ce qu'un fichier établit est ce qu'il
> **déclare**.

### 5.1.2 `RECOUVREMENT PARTIEL` — ce que ce verdict oblige à écrire

**Aucun cas réel n'est préjugé** : les quatre verdicts sont ouverts, et rien dans
le corpus n'établit lequel se réalisera.

Si `A-O1` rend **`RECOUVREMENT PARTIEL`**, le rapport **MUST** porter :

| # | Élément exigé |
|---|---|
| 1 | l'**intersection exacte** — quelles commandes sont déclarées par **les deux** clients |
| 2 | les **différences symétriques** — ce que chacun déclare et que l'autre ne déclare pas |
| 3 | la **conséquence pour une discrimination par `Command:`** : sur quelle part du trafic elle serait **concluante**, et sur quelle part elle serait **ambiguë** |
| 4 | le constat, s'il y a lieu, que la part ambiguë **suffit à ruiner la discrimination** — ou qu'elle ne suffit pas, **avec le motif** |

> **Une discrimination partielle n'est pas une discrimination.** `w4f1` §8.2
> exige que le journal porte *« la distinction des clients »*, sans réserve de
> portée. **Le rapport constate ; il ne conclut pas à la place de `T0-A`.**

> **Pourquoi `A-O1` importe.** `w4f1` §8.2 conditionne `T0-B` à ce que le journal
> porte ouverture **et** clôture **et** distinction des clients. Sous **`-n`**,
> *« le PID ne discrimine plus rien »* — `w4f1a-upstream-characterization.md`
> §10.2, constat Acte A §14.1. La seule discrimination encore concevable dans ce
> puits passerait par l'événement `Command:`, qui porte *« la commande émise par
> le client »* (`w4f1a` §10.3). **Si les deux clients déclarent la même commande,
> cette voie est fermée aussi** — et c'est un résultat, pas un échec.

> **Et `Command:` est aujourd'hui MUET.** L'événement est `LOG_INFO`
> (`w4f1a` §10.3), et le constat Acte A §10 établit que **`debug` effectif =
> `false`** sur l'installation, avec `LOG_INFO` écarté et **0 occurrence** de
> `Command:` sur 200 000 lignes.
>
> **Conséquence, à ne pas franchir en silence : un `A-O1` favorable n'est PAS,
> en lui-même, une capacité d'observation actuelle.** Il dirait seulement qu'une
> discrimination serait **concevable si l'événement était produit** — ce qui
> exigerait un acte que `W4-P1` **s'interdit** (§4, §6.4). **`W4-P1` MUST NOT**
> présenter `A-O1` comme établissant que la discrimination est disponible.

> **`A-O3` — aucune présomption, et un candidat déjà mort.**
> `budget_superviseur = 5,000 s` est *« corroboré par le constat Acte A
> (`VCLIENT_TIMEOUT=5`) »* — `w4f2-c1-reexamen.md` **§4.2**, tableau
> « Variables, unités, provenance ». **Le timeout est le budget** : l'employer
> comme `borne_sonde` donnerait `seuil_C1 = 0`. `A-O3` cherche donc une borne
> **structurelle et strictement plus petite**, dont **rien n'établit qu'elle
> existe**.
>
> **Correction de la V1** : elle ancrait ce verbatim au §3.4. Le §3.4 énonce le
> fait autrement ; **le verbatim cité est celui du §4.2**.

### 5.1.3 Pourquoi le périmètre de `A-O3` est étroit, et assumé comme tel

**La V2 portait un critère ouvert.** `A6`(iii) permettait de lire *« les
paramètres de liaison et de protocole **susceptibles** de porter une borne
structurelle »* — un critère qui se juge **en lisant**, donc **incompatible avec
une liste close**, dont tout l'objet est d'être décidable **avant** l'acte.

**Le corpus ne permet pas de le refermer par énumération.** Les seuls éléments du
fichier déployé qu'une pièce intégrée **détermine** sont ceux que
`w4f2-vito-xml-instruction.md` §15 nomme : l'élément d'**inclusion** et
l'élément de **périphérique par défaut**. **Aucune pièce intégrée ne détermine un
paramètre de liaison ou de protocole** de ce fichier qui porterait une borne.

> **Conséquence assumée, et le choix est délibéré.** Plutôt que d'inventer une
> énumération, `A6` est **borné aux deux éléments déterminés** (§6.1). `A-O3`
> devient donc un instrument **étroit** : il peut rendre `CANDIDATE IDENTIFIÉE`
> si l'un de ces deux éléments en porte une, et **rien de plus**.

> **`AUCUNE IDENTIFIÉE SUR LE PÉRIMÈTRE LU` est dès lors le SEUL verdict négatif
> légitime.** Le rapport **MUST** énoncer **quel périmètre a été effectivement
> lu**, et **MUST NOT** écrire, sous aucune forme, qu'aucune borne structurelle
> n'existe.
>
> **Ce que ce verdict ne dit pas** : rien sur ce qui n'a pas été lu. Une borne
> portée par le **fichier de commandes inclus** serait **hors du périmètre** —
> `A6` en identifie l'**inclusion**, jamais le contenu. Une borne portée par un
> paramètre que le corpus ne détermine pas serait **hors du périmètre** aussi.
> **Étendre la lecture exigerait un lot distinct**, et `W4-P1` **MUST NOT** le
> faire.

### 5.2 Jambe B — objectifs et verdicts admissibles

> **Ce que systemd enregistre, et ce qu'il ne mesure pas.** La source systemd
> enregistre des **invocations d'unité**. Elle **ne mesure pas une sonde**.
> `w4f1` §8.3 définit **`M6`** comme *« la durée d'une **sonde** du
> superviseur »*, statut `PREUVE TERRAIN / SOURCE EXTERNE REQUISE`. Et c'est
> **`w4f1` §9**, table des inconnues, ligne **`U-2`**, qui porte la clause :
> ***« aucun substitut admis »*** — la ligne y renvoie au §8.3, mais **la clause
> est au §9**, et la V2 l'ancrait au mauvais endroit.
>
> **La V1 nommait `M6` ce que cette source ne rend pas. C'est corrigé** : la
> jambe B ne produit pas `M6`, et le présent document cesse de le laisser
> entendre.

| Réf | Objectif | Verdicts admissibles |
|---|---|---|
| **B-O1** | établir si la source systemd permet d'attribuer **sans ambiguïté les INVOCATIONS de `<unité-superviseur>`** — l'**unité**, non la sonde | `ATTRIBUTION POSSIBLE` · `ATTRIBUTION IMPOSSIBLE` · `INDÉTERMINÉ` |
| **B-O2** | relever, **si et seulement si `B-O1` est `ATTRIBUTION POSSIBLE`**, la **durée d'ENVELOPPE D'INVOCATION** observée sur la fenêtre | relevé empirique **typé enveloppe** · `NON RELEVABLE` |

> **Typage de la durée d'enveloppe d'invocation — cinq énoncés, tous exigibles au
> rapport.**
>
> 1. elle **contient potentiellement** `fork`/`exec`, le **corps du script**, des
>    **attentes**, et **éventuellement plusieurs sondes** ;
> 2. elle **ne vaut PAS `M6`** ;
> 3. elle **n'est PAS une borne de sonde** ;
> 4. elle **n'est PAS substituable à `M6`** — *« aucun substitut admis »*,
>    `w4f1` §9, `U-2` ;
> 5. **aucune qualification de borne n'en découle**, dans aucun sens.
>
> **`W4-P1` MUST NOT** présenter cette durée comme `M6`, comme une borne, comme
> une majoration de sonde, ni comme une approximation de l'une ou de l'autre.

> **Et même typée, elle resterait empirique.** `w4f1` §8.5 a écarté `4,029 s`
> comme *« maximum empirique […] et non une borne supérieure démontrée »*, et
> **interdit le quantile**. Toute qualification appartient à **`T0-D`** —
> décision 3 : *« une mesure ne vaut jamais, à elle seule, borne qualifiée »*.

#### Régime de l'invocation — exigence d'interprétabilité

**Le corpus établit que deux invocations peuvent n'avoir rien de comparable.**
`w4f1` §8.3 décrit le cycle en échec : *« un cycle dont la sonde a échoué **a
déjà redémarré le pont**, **dort 90 s**, **n'ouvre aucune connexion** — et reste
armé pour redémarrer la machine »*.

> **Une enveloppe d'invocation nominale et une enveloppe d'invocation en échec ne
> décrivent pas le même phénomène.** Les agréger sans le dire produirait une
> population **hétérogène** présentée comme homogène.

| Cas | Ce que le rapport **MUST** faire |
|---|---|
| la source **permet** de qualifier le régime | **signaler, pour chaque invocation observée**, si elle est **nominale**, **en échec**, ou **indéterminée** |
| la source **ne le permet pas** | **consigner explicitement** que les durées d'enveloppe **mélangent potentiellement des régimes**, et qu'elles **ne peuvent pas être comparées comme une population homogène** |

> **Aucune des deux branches ne change la nature de la grandeur.** Qualifiée ou
> non, l'enveloppe **n'est ni `M6`, ni une borne**, et **rien ne s'en déduit** au
> sens du §5.2.

> **Rien n'est présumé de cette source.** `w4f2-ouverture.md` §2, précondition 6,
> la donne *« présumée disponible par son exécution sous systemd, **aucune n'a
> jamais été observée** ; observabilité **non établie** »*. **Établir qu'elle ne
> porte pas l'attribution est un résultat recevable et attendu.**

### 5.3 Sous-question portée au rapport — décision 6

Le rapport de `W4-P1` **MUST** instruire, **comme sous-question et sans cadrage
distinct**, la **réserve sur la bornabilité déterministe de `U-7`** —
`w4f2-cloture.md` §5, reprenant `w4f2-c1-amendement.md` §9(4) : l'occupation
cumulée *« pourrait être non seulement non mesurée, mais **non bornable de façon
déterministe dans la configuration actuelle** »*.

> **L'instruction est analytique.** Elle **ne consomme aucun acte** de la liste
> close du §6, et **ne peut pas être tranchée par les relevés du lot**.

## 6. Élément 3 — Actes permis, **liste close**

> **Liste close.** Tout acte qui n'y figure pas est **interdit**. En cas de doute
> sur l'appartenance d'un acte à cette liste, l'acte est **interdit**, et le doute
> est un motif d'`ABORT` — `P1A-1`.

### 6.1 Jambe A

| # | Acte permis |
|---|---|
| **A1** | lire le **contenu** de `<script-superviseur>` |
| **A2** | lire le **contenu** de `<source-pont>` |
| **A3** | lire la **définition** des unités `<unité-superviseur>`, `<timer-guard>`, `<unité-pont>`, `<unité-démon>` — consultation de définition, sans action |
| **A4** | lire les **propriétés courantes** de ces mêmes unités — consultation d'état, sans action |
| **A5** | relever, **avant et après** les actes A1–A4 et A6, l'**empreinte** de chaque fichier lu : taille, date de modification, condensat |
| **A6** | faire une **lecture ciblée de `<config-démon>`**, bornée à **deux éléments, et rien d'autre** : **(i)** son ou ses éléments d'**inclusion** — quel fichier de commandes est inclus, et depuis quel emplacement — ; **(ii)** l'élément de **périphérique par défaut** |

> **Le troisième élément de la V2 est retiré.** Il visait *« les paramètres de
> liaison et de protocole **susceptibles** de porter une borne structurelle »* —
> critère qui ne se juge **qu'en lisant**, et qui rouvrait donc la liste close.
> **Aucune pièce intégrée ne détermine un tel paramètre** ; l'énumérer aurait été
> l'inventer. Conséquence sur le verdict : **§5.1.3**.

**Ce qui est REPRIS du précédent de méthode**, `w4f2-vito-xml-instruction.md`
§15 :

| | Élément repris |
|---|---|
| la **forme** de l'acte | *« **lecture ciblée du `vcontrold.xml` déployé**, bornée à son élément `<xi:include>` […] et à l'élément de **périphérique par défaut**. **Rien d'autre de ce fichier n'est requis** »* |
| le **régime** | *« ni journal, ni descripteurs, ni processus, ni exécution »* |

**Ce que `W4-P1` AJOUTE, et qui n'est pas couvert par ce précédent :**

| | Ajout, et pourquoi le précédent ne le porte pas |
|---|---|
| l'**objet** | §15 propose cet acte pour fermer un terme du résidu de `H6` **(a)** — la **résolution** d'une commande. **`A-O3` en poursuit un autre** : une borne structurelle pour `borne_sonde`. **Le précédent ne dit rien de cet objet**, et n'en préjuge rien |
| l'**empreinte avant/après** (`A5`) | §15 écarte une empreinte sur ce fichier, mais **pour une autre comparaison** — *« parce qu'il **diffère déjà de l'amont**, et qu'on le sait […] un contrôle dont le résultat est connu d'avance »*. **`A5` ne compare pas à l'amont** : elle compare **le fichier à lui-même, avant et après**, pour prouver la non-modification. **Ce n'est pas le contrôle que §15 écarte** |
| le **second acte de §15** | §15 propose **aussi** de relever l'empreinte du `vito.xml` déployé et de la comparer à l'amont. **`W4-P1` ne le reprend pas** : il est hors de son objet |
| l'**autorisation** | §15 est explicite — *« **non donnée, et non demandée ici**. Ce document propose ; il n'autorise pas »*. **Le précédent n'autorise donc rien**, et `A6` reste soumis à l'élément 6 (§9) |

> **`A6` hérite des trois limites du précédent** : **aucune modification** ·
> **aucune exploration ouverte** du système ou du fichier · **aucune lecture du
> contenu du fichier de commandes inclus** — `A6` en établit l'**inclusion**,
> jamais le contenu.

### 6.2 Jambe B

| # | Acte permis |
|---|---|
| **B1** | lire, **de façon rétrospective et non continue**, les enregistrements du journal système **de la seule `<unité-superviseur>`**, sur la fenêtre bornée du §4.1 |
| **B2** | relever le **PID** de `<unité-démon>` **au début et à la fin du LOT ENTIER**, jambes A et B comprises — et non de la seule jambe B |
| **B3** | figer les relevés dans des **fichiers hors dépôt**, sans transformation autre que la sélection prévue au §6.3 |
| **B4** | en cas d'`ABORT`, **consigner l'état exact du relevé partiel** : ce qui a été figé, ce qui ne l'a pas été, et l'**instant de l'arrêt** |

> **Correction de la V1 sur `B2`.** La V1 ne relevait le PID du démon
> qu'autour de la jambe B : un redémarrage survenu **pendant la jambe A** serait
> passé inaperçu. Le relevé encadre désormais **le lot entier**.

> **`B4` n'autorise aucune complétion.** Un relevé interrompu **MUST** être
> conservé **tel quel**. Le compléter, le reconstituer, ou le présenter comme
> complet **rendrait un artefact fabriqué indiscernable d'un artefact
> authentique** — et c'est interdit. Voir `R6` au §8.

### 6.3 Minimisation

**Ne sont relevés que les éléments strictement nécessaires** à l'attribution
(`B-O1`) et à la durée observée (`B-O2`). Tout contenu excédentaire **MUST NOT**
être extrait, conservé, ni reproduit.

### 6.4 Interdits nommés, sans préjudice de la clôture de la liste

Aucune écriture, aucune création, aucune suppression, aucun renommage · aucun
démarrage, arrêt, redémarrage, activation ni désactivation d'unité · **aucune
modification de `vcontrold`, aucun changement de verbosité, aucune session
`debug`** · aucune connexion cliente au démon ouverte par le lot · aucun
déploiement ni démarrage de Boilerack · aucune écriture chaudière · aucune
élévation de privilège au-delà de ce que la lecture exige · **aucune publication
MQTT d'aucun élément du lot**.

## 7. Élément 4 — Critères d'`ABORT` et de `STOP`

### 7.1 `ABORT` — arrêt immédiat de l'exécution

| Réf | Déclencheur |
|---|---|
| **`P1A-1`** | un acte hors de la liste close du §6 est envisagé, ou son appartenance est douteuse |
| **`P1A-2`** | `vcontrold` devient indisponible, instable, ou change d'état |
| **`P1A-3a`** | **cessation du régime nominal** du pont ou du superviseur |
| **`P1A-3b`** | **redémarrage, arrêt ou démarrage inattendu** de l'une de ces unités — ou **provoqué par le lot**, quel qu'il soit |
| **`P1A-3c`** | *(non déclencheur)* — le **cycle périodique nominal attendu** de `<unité-superviseur>` |
| **`P1A-4`** | redémarrage machine inattendu |
| **`P1A-5`** | une lecture exigerait une élévation de privilège non prévue, ou modifierait un état |
| **`P1A-6`** | une **empreinte avant/après diverge** (§8) |
| **`P1A-7`** | la fenêtre du §4.1 serait dépassée |
| **`P1A-8`** | **doute de l'exploitant, sans justification à fournir** |

> **`P1A-3c` n'est PAS un déclencheur, et la V2 en faisait un.** Elle écrivait
> *« le pont ou le superviseur cesse d'être nominal, **ou redémarre** »* — or
> `<unité-superviseur>` est déclenchée **périodiquement** par `<timer-guard>` :
> elle démarre et s'arrête **à chaque cycle**, par construction. Le lot aurait
> donc **avorté sur le comportement même qu'il vient observer**.
>
> **Le cycle périodique nominal MUST NOT être interprété comme un redémarrage
> fautif.** Ce qui déclenche est **`P1A-3a`** — le régime cesse d'être nominal —
> ou **`P1A-3b`** — une transition **inattendue**, ou **causée par le lot**.
>
> **Le repère du nominal est la cadence déclarée relevée par `A-O4`**, et aucune
> valeur n'est posée ici.

> **L'`ABORT` de `W4-P1` n'a rien à défaire.** Le lot ne modifie rien : arrêter
> les lectures **est** l'`ABORT`. Ce qui reste dû après un `ABORT` est la
> **consignation** de son déclencheur et la **preuve de non-modification** du §8.

### 7.2 `STOP`

Les quatre cas du `w4p-ouverture.md` §10.1 s'appliquent sans allègement — dont
*« une **frontière du §5** est franchie, ou sur le point de l'être »*.

> **Un `STOP` n'est pas une issue**, et **les verdicts du §9 ne sont pas l'issue
> de `W4-P`** : `W4-P1` ne prononce ni `SUCCÈS`, ni `ÉCHEC`, ni `INDÉTERMINÉ` au
> sens du `w4p-ouverture.md` §10.2.

## 8. Élément 5 — Restauration vérifiable

> **Le lot ne modifie rien. La « restauration » est donc la PREUVE qu'il n'y a
> rien à restaurer** — et cette preuve **MUST** être produite, y compris après un
> `ABORT`.

| # | Preuve exigée |
|---|---|
| **R1** | pour chaque **fichier de configuration** lu — `A1`, `A2`, `A6`, et les fichiers de définition d'unité lus par `A3` : **taille, date de modification et condensat identiques** avant et après. **`R1` ne porte PAS sur le journal système lu par `B1`** — voir ci-dessous |
| **R2a** | pour les unités devant demeurer **invariantes** — `<unité-démon>`, `<unité-pont>`, `<timer-guard>` : **aucun redémarrage, aucune reconfiguration** pendant le lot |
| **R2b** | pour **`<unité-superviseur>`**, dont le **cycle périodique est nominal et attendu** : **aucun acte du lot ne l'a modifiée, démarrée, arrêtée ni redémarrée**, et son fonctionnement demeure **conforme à son régime nominal** |
| **R3** | **PID de `<unité-démon>` identique au début et à la fin du LOT ENTIER**, jambes A et B comprises — le démon n'a redémarré **pendant aucune des deux jambes** |
| **R4** | **aucune unité créée, ni supprimée**, sur le périmètre du lot |
| **R5** | **aucun fichier écrit** hors des relevés `B3` et de la consignation `B4`, tous **hors dépôt** |
| **R6** | en cas d'`ABORT` : le **relevé partiel** est conservé **tel quel**, avec l'instant de l'arrêt, et **MUST NOT** être complété, reconstitué, ni présenté comme complet |

**Une divergence sur R1, R2a, R2b ou R3 est un `ABORT` — `P1A-6` — et MUST être
consignée telle quelle, sans correction ni réinterprétation.**

### 8.1 Pourquoi `R1` ne porte pas sur le journal système

Le journal lu par `B1` est **alimenté en continu** par le système. Sa taille, sa
date de modification et son condensat **changent nécessairement** pendant le lot,
**sans qu'aucun acte du lot n'y soit pour quoi que ce soit**.

> **Exiger leur invariance aurait été exiger l'impossible**, et aurait produit un
> `ABORT` `P1A-6` garanti. **`R1` porte sur les fichiers de configuration**, dont
> l'invariance est la propriété que le lot doit réellement prouver.
>
> Ce que `B1` doit prouver n'est pas que le journal n'a pas bougé, mais que **la
> lecture n'y a rien écrit et n'a rien déclenché** — ce que `R5` couvre, et ce que
> la nature rétrospective de `B1` garantit.

### 8.2 Pourquoi `R2` est dédoublée

**La V2 exigeait de `<unité-superviseur>` des « état et date de démarrage
identiques ».** C'était contradictoire avec l'objet même du lot : cette unité est
déclenchée **périodiquement**, et sa date de démarrage **change à chaque cycle**.

> **Un changement d'état ou de date de démarrage de `<unité-superviseur>` n'est
> PAS une divergence.** C'est le phénomène observé. La preuve attendue est celle
> de `R2b` : que **le lot n'y a pas touché**, et que le régime demeure nominal.

> **`R3` corrige la V1**, qui bornait la preuve à la jambe B et laissait la
> jambe A sans couverture.

## 9. Élément 6 — Autorisation propre

> ### **NON DONNÉE.**
>
> `w4q-precondition2-arbitrage.md` décision 5 exige *« son **autorisation propre**,
> **distincte de la présente** »*. **Ce document ne la constitue pas**, et
> l'arbitrage qui l'a demandé ne la donne pas d'avance : *« Le premier lot
> **recevra** sa propre autorisation explicite. »*
>
> **`W4-P1` MUST NOT être exécuté, même partiellement, avant que cette
> autorisation soit donnée.**

**Ce que l'autorisation devra dire, pour être suffisante :**

| # | Point | État |
|---|---|---|
| 1 | qu'elle **autorise `W4-P1`** tel que borné par le présent document, **et rien d'autre** | **à trancher** |
| 2 | qu'elle **n'autorise ni `T0`, ni `T1`, ni aucun des quatre actes réservés** du §11.1 | **à trancher** |
| 3 | le **mode prospectif de repli** | **RENDU** — autorisé, sous la seule forme du §4.2 (§3.1) |
| 4 | la **borne de 4 heures** | **RENDU** — conservée telle quelle (§3.1) |

> **Les points 3 et 4 sont rendus, et cela ne rend pas l'élément 6.** Ils bornent
> le lot. **L'autorisation d'exécuter demeure NON DONNÉE.**

## 10. Frontières négatives

Les frontières du `w4p-ouverture.md` §5 s'appliquent intégralement. Deux méritent
d'être rappelées ici, parce que ce lot les côtoie :

> **`W4-P1` MUST NOT** *« ouvrir `T0`, y toucher, ou présenter l'une de ses
> expériences comme une phase de `T0` »*.
>
> **`W4-P1` MUST NOT** *« se fonder sur un document non intégré au dépôt, ni sur
> un constat non homologué »* — ce qui vaut aussi pour **ses propres relevés**,
> qui ne deviendront opposables qu'une fois **homologués**.

> **Rappel de la décision 2.** `W4-P1` **ne vise pas `U-1`**. Si, à l'exécution,
> un acte s'avérait viser le régime de concurrence, il relèverait de `T0-B` et de
> ses conditions : **`ABORT`, et non requalification.**

## 11. Sorties attendues

| # | Sortie |
|---|---|
| 1 | les **verdicts** `A-O1` à `A-O4` et `B-O1` à `B-O2`, chacun avec sa **méthode** et sa **source exacte** |
| 2 | la **preuve de non-modification** du §8, complète |
| 3 | l'**instruction de la sous-question** du §5.3 — réserve sur la bornabilité de `U-7` |
| 4 | l'énoncé de **ce qui demeure non établi**, sans euphémisme |
| 5 | le constat, s'il y a lieu, qu'une **suite** est concevable — **sans la nommer comme autorisée** |

> **Aucun verdict par défaut, aucun verdict par silence.** `INDÉTERMINÉ` se
> prononce ; il ne se déduit pas d'une absence de conclusion.

## 12. Ce que ce document ne fait pas

Il **n'exécute rien**, **n'autorise rien**, **ne relève aucune mesure**, **ne fixe
aucun seuil**, **ne produit aucun critère**, **ne qualifie aucune borne**,
**n'amende aucun contrat**, **ne lève aucune inconnue**, **n'ouvre pas `T0`**, et
**ne tranche pas** la voie du point 1.

Il borne un lot, et s'arrête là.

## 13. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture et bornage du premier lot terrain de `W4-P`, sur arbitrage humain des huit points du §7 de la sortie 1. Six éléments réunis ; **élément 6 non donné**. Aucune exécution, aucune mesure, aucune autorisation. |
| **2** | Après audit `NO-GO`. `B1` : acte `A6` ajouté à la liste close, borné sur `w4f2-vito-xml-instruction.md` §15, avec le repère `<config-démon>` ; verdict négatif de `A-O3` borné au périmètre lu. `B2` : registre de la configuration séparé de celui de l'exécution (§5.1.1). `B3` : `A-O1` élargi à quatre verdicts, dont `RECOUVREMENT PARTIEL` et ses quatre exigences (§5.1.2). `B4` : `M6` retiré de la jambe B — invocations et **enveloppe d'invocation**, typées par cinq énoncés. `R-1` à `R-5` : repli prospectif borné (§4.2), `Command:` muet, ancre `§4.2`, `B2`/`R3` étendus au lot entier, relevé partiel `B4`/`R6`. **Aucune exécution, aucune mesure, aucune autorisation, aucune durée nouvelle.** |
| **3** | Après ré-audit portant sur l'exécutabilité pratique. `D1` : `R2` dédoublée — `R2a` unités invariantes, `R2b` unité cyclique dont le cycle n'est pas une divergence. `D2` : `P1A-3` scindée en `3a`/`3b`, avec `3c` **explicitement non déclencheur** — la V2 avortait sur le cycle nominal. `D3` : `R1` bornée aux fichiers de configuration, le journal vivant en étant exclu. `D4` : règle d'exploitation de l'attente, **sans plafond ni durée nouvelle**. `R-6` : `A6`(iii) retiré faute de pièce le déterminant ; `A6` borné à deux éléments et §5.1.3 ajouté. `R-7` : couverture exacte du précédent §15, repris et ajouts distingués. `R-8` : ancre *« aucun substitut admis »* corrigée vers `w4f1` §9. `R-9` : exigence d'interprétabilité du régime pour `B-O2`. **Aucune exécution, aucune mesure, aucune autorisation, aucune durée nouvelle.** |
