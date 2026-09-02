# `W4-R` — lot borné en lecture stricte : attribution de l'instance `A-5`

> **Version 4**, après réaudit. **Quatre blocages fermés.** Aucun terrain.
> **L'autorisation demeure `NON DONNÉE`.**
>
> | | Correction |
> |---|---|
> | **V4 · RR1** | **`O3` était encore excluable par une absence** — le défaut même que la V3 avait corrigé sur `O1`. La **même discipline** lui est appliquée : **enregistrement POSITIF, daté dans la fenêtre** ; faute de quoi **`O3` demeure ouverte, `B` est inqualifiable, et le verdict est `INSTANCE NON ATTRIBUABLE`**. Et le motif est nommé : **le dossier `G.2` est démontrablement NON EXHAUSTIF** — `A-5` est *« hors campagne »*, `A-1` consigne une capture **écrasée** |
> | **V4 · RR2** | **Double négation supprimée au §5.2** — *« Aucune attribution […] MUST NOT être tirée »* disait le contraire de ce qu'il fallait |
> | **V4 · RR3** | **Réserve 8 alignée sur le §7.1.2** : elle raisonnait encore par absence, et ignorait que `L9` ne contribue ni à `B` ni à `C` |
> | **V4 · RR4** | **`RE-1 bis` propagée** au §5 — `L7` et `L12` — et au §11. Sa couverture demeure **depuis la découverte seulement, jamais rétroactive** |
>
> **Version 3**, après réaudit. **Sept blocages fermés.** Aucun terrain.
>
> | | Correction |
> |---|---|
> | **V3 · R1** | **La renumérotation de la V2 n'avait pas été propagée au §7.1.** `A` pointe désormais sur **`L5`** ; `B` et `C` sur les **seuls actes capables de les établir** ; **`L9` ne figure plus nulle part comme pouvant porter `B`** — il en est expressément exclu |
> | **V3 · R2** | **Le §6.2 déclarait le rang 12 « sans objet » quand `A` manque.** C'était faux et grave : ce rang porte la **répétition finale** de `L2` et `L0`, donc `RE-2`, `RE-3` et `RE-5`. **Il demeure OBLIGATOIRE en toute hypothèse** ; seuls les rangs **réellement dépendants de la fenêtre** deviennent sans objet |
> | **V3 · R3** | **`O1` était présentée comme excluable par une absence** — interdit par `W4-C` §9.1. Elle ne l'est que par un **enregistrement POSITIF** de l'état du démon. **Aucun observable n'est inventé** : si aucun n'est disponible, **`O1` demeure OUVERTE et `B` est inqualifiable** |
> | **V3 · R4** | **Décomptes corrigés** : la liste close porte **treize** actes, `L0` à `L12`, et le **§10 les autorise exactement** |
> | **V3 · R5** | Quatre renvois faux corrigés — **`§7.1.1`**, **réserve n° 10**, **autorisation §10**, et **`G3` §6.1 (a)** cité conformément à la règle de désambiguïsation du §0 |
> | **V3 · R6** | **`RE-1` promettait pour le puits de `L7` une couverture depuis le rang 3**, que le §9.1 contredisait. La table est alignée : **empreinte dédiée, couverture depuis la découverte seulement** |
> | **V3 · R7** | Deux formulations fautives remplacées par **`MUST NOT`**. **Aucune attribution ne peut être tirée d'une absence** |
>
> **Version 2**, après audit. **Six blocages fermés**, et une règle de
> désambiguïsation ajoutée. Aucun terrain.
>
> | | Correction |
> |---|---|
> | **V2 · B1** | **`<journal-démon>` manquait aux sources et à la liste close.** Il y entre comme **`S7`** et comme acte **`L9`**, avec **vérification de rétention avant exploitation**, une conclusion possible **`SOURCE NON DISCRIMINANTE`**, et l'interdiction expresse d'attribuer par absence — `U-3` demeure ouverte |
> | **V2 · B2** | **`RE-1`…`RE-5` et `RA-3` n'étaient exécutables par aucun acte.** Trois actes les portent désormais — `L1` empreintes de référence, `L2` relevé d'état des **quatre** unités, `L12` empreintes finales —, `<unité-démon>` est couverte, et les **répétitions structurées** sont **explicitement autorisées** |
> | **V2 · B3** | **Le resserrement par rapport au `G3` §6.1 (a) — `w4f-g3-seconde-ecriture-bornee.md` — n'était pas déclaré.** Il l'est : `W4-R` est **plus strict**, `B` demeure pivot obligatoire, et ce choix **peut produire `INSTANCE NON ATTRIBUABLE` alors qu'une autre voie eût théoriquement suffi** |
> | **V2 · B4** | **Les origines concurrentes du redémarrage du pont n'étaient pas instruites**, `F-13` en tête — `<unité-pont>` **requiert** `<unité-démon>`, donc un redémarrage du démon redémarre le pont. Quatre origines sont énumérées ; **`B` n'est qualifié que si toutes sont exclues par preuve**, et **jamais par proximité temporelle** |
> | **V2 · B5** | **`RE-1` ne pouvait pas couvrir le puits de journalisation, découvert seulement en cours de lot.** L'intervalle de couverture est désormais **prouvé depuis la découverte**, et **déclaré ne pas couvrir ce qui précède** |
> | **V2 · B6** | Renvois et citations corrigés : autorisation → **§10** · le rang qui établit l'instant renvoie à la **clause applicable** et **n'anticipe plus le verdict** · cadence **190,0 s** sourcée sur **`P1-H` §4** · **`W4-C` §9.1 cité mot pour mot** — *« Aucune inférence à partir d'une absence de trace »* |
>
> **Version 1.** Lot d'ouverture **et** bornage. Il définit un acte de terrain
> **en lecture stricte**, le referme, et **ne l'autorise pas**.
>
> **Aucun terrain n'est conduit par ce document. Aucune mesure, aucune commande,
> aucun accès à l'installation.** Aucune constante de site.
>
> **L'autorisation humaine est `NON DONNÉE`** — §10.

---

## 0. Convention de citation

Les unités sont désignées `<unité-superviseur>`, `<unité-pont>`, `<unité-démon>`,
`<timer-guard>`, `<script-superviseur>`, `<journal-démon>`.

| Nom court | Document |
|---|---|
| `w4f` | `w4f-write-sovereignty.md` |
| `G3` | `w4f-g3-seconde-ecriture-bornee.md` |
| `G2-P` | `w4f-g2-ecriture-bornee.md` |
| `G2-C` | `w4f-g2-constat.md` |
| `P1-B` | `w4p1-lot-terrain-borne.md` |
| `P1-H` | `w4p1-homologation.md` |
| `P2-B` | `w4p2-lot-terrain-borne.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `debug` | `w4-cadrage-activation-debug.md` |
| `ouverture` | `w4f2-ouverture.md` |

Une référence **sans nom court** désigne le présent document.

> **Règle de désambiguïsation `G.n` — opposable dans tout le présent
> document.**
>
> Le corpus emploie les mêmes étiquettes pour **deux objets différents**. La
> règle qui suit tranche, **pour `W4-R` et pour lui seul** :
>
> | Forme | Désigne |
> |---|---|
> | **`G.1`, `G.2`, `G.3` sans qualificatif** | l'**acte / la campagne** de ce nom — `w4f2-g1-constat.md`, `G2-P`, `G3` |
> | **`debug` §G.1 … §G.4**, ou toute forme **portant son document** | la **classe de régime d'engagement** définie par l'annexe `G.` de `debug`, reprise par `w4f2-regime-instruction.md` §13.2 |
>
> **Une classe de régime ne se cite JAMAIS sans son porteur.** Toute occurrence
> nue dans le présent document désigne l'acte, et rien d'autre.
>
> **Cette règle ne vaut que pour `W4-R`.** Elle n'amende ni `debug`, ni `G3`, ni
> `w4f2-regime-instruction.md` — voir la **réserve 10** du §13.

---

## 1. Désignation, et pourquoi elle n'est pas un `G.n`

> **Le lot est désigné `W4-R`** — *reliquat d'attribution*.

**La série `G.n` a été écartée délibérément, et le motif doit être dit.**

`debug` **§G** définit une **échelle normative de régimes d'engagement**, et
`w4f2-regime-instruction.md` **§13.2** la reprend comme telle :

| Classe | Contenu |
|---|---|
| **`debug` §G.1** | **lecture** — *« configuration déployée, invocation effective, du journal, de l'état des processus »* · *« aucune mutation, aucune interruption »* |
| **`debug` §G.2** | mutation de configuration — réversible |
| **`debug` §G.3** | **interruption de service** — *« le seuil qualitatif »* |
| **`debug` §G.4** | **hors périmètre, absolument** — écriture chaudière, `set*`, changement de writer |

Ajouter un `G.5` ou réemployer une de ces étiquettes **aggraverait une ambiguïté
déjà présente** dans le corpus. `W4-R` est **vérifiée libre** : les désignations `W4`
en usage sont `W4-A`…`W4-F`, `W4-F0`…`W4-F6`, `W4-F1A`, `W4-E1`, `W4-E2`,
`W4-P`, `W4-P1`, `W4-P2`, `W4-Q`. **Aucun `W4-R` n'existait.**

> **Ce que `W4-R` est, dans l'échelle de `debug` §G : la classe `debug` §G.1, et
> elle seule.** *« Aucune mutation, aucune interruption. »* C'est le régime le
> moins engageant du corpus, et le lot n'en sort à aucun acte.

**Ce que la désignation ne fait pas** : elle n'insère `W4-R` ni dans `W4-F`, ni
dans `W4-P`, ni dans `G3` ; elle ne lui donne aucune position contractuelle
héritée ; elle n'ouvre ni ne rapproche `G3`.

---

## 2. Objet, et les deux verdicts

> **Objet unique : déterminer si le redémarrage machine observé pendant le
> préflight de la campagne `G.2` est attribuable au mécanisme `F-12`.**

**Rien d'autre.** Le lot ne cherche ni la cause générale des redémarrages, ni le
comportement du superviseur, ni une caractérisation du chemin correctif.

### 2.1 L'état de la question, et il est étroit

**Le mécanisme est ÉTABLI** — `P2-B` §3, fait **`F-12`**, registre
**configuration déclarée** :

> *« le superviseur, sur échec de sonde, **redémarre le pont**, attend **90 s**,
> resonde — et **si la seconde sonde échoue, il redémarre la machine**. Établi
> par le relevé `A1` figé de `W4-P1` »*

**L'instance ne l'est pas** — `G2-C` §6, réserve `A-5` :

> *« un **redémarrage machine commandé par le superviseur** est survenu pendant
> le **préflight**, hors campagne. **Cause non établie** — le journal du boot
> précédent n'a pas survécu. `G-a` et `G-b` ont tenu à travers lui »*

`P1-B` **§5.1.1** tient : **une lecture de configuration n'est pas une preuve
d'exécution.** Le reliquat est donc de **rattacher une instance observée à un
mécanisme déjà établi**, et de rien d'autre.

### 2.2 Les deux verdicts — exclusifs, et il n'y en a pas d'autre

| Verdict | Conditions |
|---|---|
| **`INSTANCE ATTRIBUÉE`** | la règle de décision du §7 est satisfaite **intégralement** |
| **`INSTANCE NON ATTRIBUABLE`** | **tout autre cas**, y compris l'absence de source, la matière insuffisante, et l'attribution seulement plausible |

> **Aucun troisième verdict, aucun verdict nuancé, aucun verdict par défaut
> favorable.** *« Probable »*, *« vraisemblable »*, *« cohérent »* et
> *« compatible avec »* valent **`INSTANCE NON ATTRIBUABLE`**.

> **Ce qu'`INSTANCE NON ATTRIBUABLE` signifie, et ne signifie pas.** Il dit que
> **le rattachement n'est pas prouvé**. Il ne dit **pas** que le redémarrage
> aurait une autre cause, ni que `F-12` serait hors de cause. **Il ne conclut
> rien sur le mécanisme.**

### 2.3 Ce que le verdict emporte pour `G3`

`G3` §6.1 rend `P-A5` **bloquante** : sur **(a)** la campagne peut être
autorisée, sur **(b)** elle **MUST NOT** être exécutée — **`STOP AVANT
AUTORISATION`**.

> **`W4-R` prononce la branche. Il n'autorise ni ne refuse `G3`** : c'est
> l'autorisation humaine du `G3` §13 qui en tire la conséquence.

---

## 3. Les sources, et leur survie — l'inventaire honnête

**La difficulté centrale est nommée d'avance** : la source principale est
déclarée perdue.

| # | Source | Ce qu'elle porterait | Survie |
|---|---|---|---|
| **S1** | **journal systemd du boot précédant le redémarrage** | la chaîne `F-12` entière | **DÉCLARÉE NON SURVIVANTE** — `G2-C` §6 |
| **S2** | **puits de journalisation propre de `<script-superviseur>`**, s'il écrit **hors** journald | la ligne du chemin correctif | **À ÉTABLIR** — `W4-P1` a lu le script, mais **son puits n'est pas consigné** |
| **S3** | **enregistrements persistants de démarrage / arrêt** | l'**instant** du redémarrage et son **type** | probable — fichier, indépendant du journal |
| **S4** | **énumération des démarrages** connus du journal | quels boots subsistent | **conditionnée à la persistance du journal**, à établir |
| **S5** | **définitions d'unité** déjà lues sous `W4-P1` | **qui** peut commander un redémarrage machine | acquise, à reconstater |
| **S6** | **artefact terrain `G.2`** — rapport, bundle de 56 pièces, manifeste | des captures de préflight **encadrant** le redémarrage | **existe** (`G2-C` §4), **localisation à établir** — §3.1 |
| **S7** | **`<journal-démon>`** | les **ouvertures de connexion** de part et d'autre de l'instant du redémarrage | **probablement survivante** — §3.2 |

### 3.1 L'artefact `G.2` — statut exact

`G2-C` §4 : *« Le rapport et ses pièces sont conservés **hors du dépôt**, et
transmis manuellement à l'auditeur. »* Empreintes au dépôt :
`RAPPORT-TERRAIN-G2.md` `5b921453…2612d7` · `g2-terrain-20260828.tar.gz`
`dee4a8e1…1ead2d` · `MANIFESTE-SHA256.txt` `5cf55ec5…687648`.

> **Sa localisation n'est pas établie**, et le présent document ne la suppose
> pas. **Deux cas, et ils ne se confondent pas :**
>
> | Cas | Conséquence |
> |---|---|
> | l'artefact est accessible **hors du réseau de l'installation** | l'acte **`L11`** est exécutable **sans accès à l'installation**, et **avant** tout autre acte — rang 1 du §6.2 |
> | il ne l'est pas | **`L11`** devient **conditionné au même accès** que le reste, et se joue au rang 11 |
>
> **Dans les deux cas, son intégrité MUST être vérifiée contre les trois
> empreintes ci-dessus avant toute exploitation.** Une pièce dont l'empreinte ne
> concorde pas **MUST NOT** être exploitée.

### 3.2 `<journal-démon>` — pourquoi il entre, et ce qu'il ne pourra pas dire

**Il entre parce qu'il survit.** `P2-B` §3, fait **`F-6`** : *« **aucune
rotation** ne couvre `<journal-démon>` : aucune entrée `logrotate` ne le
mentionne »*. C'est la **seule** source du présent inventaire dont la survie ait
un fondement structurel, et non une espérance.

**Mais il n'attribuera rien à un client, et il faut le dire avant de le lire.**
`ouverture` §2, précondition 6, établit que le journal du démon *« ne porte que
les ouvertures de connexion, **sans clôture ni attribution par client** »*.
**`U-3` demeure ouverte**, et le présent lot **ne la réduit pas**.

**Et `W4-C` §9.1 décrit exactement ce que ce journal montrerait du chemin de
`F-12`** :

> *« Un cycle dont le test de mission a échoué a déjà redémarré le pont et **dort
> 90 s** avant de re-sonder : pendant toute cette attente il n'ouvre **aucune**
> connexion au démon, et il reste pourtant **armé pour redémarrer la machine**.
> L'absence de connexion du superviseur dans le journal est donc exactement ce
> qu'on observerait dans le cas le plus dangereux. »*

> **Conséquence, portée d'avance.** Un **creux** dans la cadence de connexions —
> `P2-B` §3, fait `F-8` : **≈ 2,105 s** en régime nominal — est **compatible**
> avec le chemin de `F-12`. **Il ne l'établit pas** : rien ne dit **de qui**
> viennent les connexions présentes, ni **à qui** manquent celles qui sont
> absentes.
>
> **Ce que `S7` peut rendre**, au mieux : l'**instant du dernier événement avant
> le redémarrage** et du **premier après** — donc un **encadrement de
> l'interruption**, corroborant `A`.
>
> **Ce qu'il ne peut pas rendre** : `B`, ni aucune part de `B`.

> **Verdict propre à l'acte.** L'acte qui lit `S7` **PEUT** conclure
> **`SOURCE NON DISCRIMINANTE`**, et ce constat est une **sortie normale**, non
> un échec. **Une attribution MUST NOT être tirée d'une absence** dans cette
> source, sous quelque forme que ce soit — §7.3.

---

## 4. Périmètre — lecture stricte, et rien d'autre

> **`W4-R` MUST NOT :**
>
> - **redémarrer** quoi que ce soit — machine, service, timer, démon, pont ;
> - **modifier** un service, un timer, le pont, le démon, une unité, une
>   configuration, un fichier, une variable d'environnement ;
> - **écrire** quoi que ce soit sur l'hôte — y compris un fichier temporaire,
>   y compris dans un répertoire de travail ;
> - **écrire sur la chaudière**, ni exécuter, préparer ou tester une commande
>   `set*` ;
> - ouvrir **`T0`**, **`T1`** ou **`T2`**, ni conduire un acte qui en relèverait ;
> - **« rejouer » `F-12` pour voir** — ni provoquer un échec de sonde, ni
>   simuler une indisponibilité, ni fabriquer la condition qu'il observe ;
> - **extrapoler** : conclure au-delà de ce que les pièces portent, dans un sens
>   ou dans l'autre ;
> - exécuter un acte **hors de la liste close du §5**.

> **Le franchissement de l'une quelconque de ces frontières est un motif de
> `STOP` immédiat** — §8.

> **La sixième interdiction est celle qui coûte, et elle est délibérée.**
> Reproduire le chemin de `F-12` serait le moyen le plus direct d'en observer la
> signature. **Il est interdit sans réserve** : ce serait **fabriquer le mode de
> défaillance** — exactement ce que `debug` §G.4 proscrit —, et l'escalade
> aboutit à un **redémarrage machine**. Le lot renonce à cette voie, et le
> renoncement est **définitif dans son périmètre**.

---

## 5. Liste close des actes permis

**TREIZE actes — `L0` à `L12` —, et aucun autre.** Ils sont tous en **lecture**.
L'ordre du §6 est opposable.

**Trois d'entre eux ne servent qu'à prouver la non-mutation** — `L1`, `L2`,
`L12`. **La V1 exigeait ces preuves sans donner l'acte qui les produit** : elles
étaient hors liste close, donc inexécutables sans `RA-1`.

| Réf | Acte | Nature | Sert |
|---|---|---|---|
| **`L0`** | relever la **joignabilité**, l'**horodatage de l'hôte**, l'**identifiant du démarrage courant** et le **temps de fonctionnement** | lecture | `RE-3` |
| **`L1`** | **empreintes de RÉFÉRENCE** des fichiers à lire, prises **avant toute lecture de contenu** : `<script-superviseur>`, les **quatre** définitions d'unité, la configuration de journalisation | lecture | **`RE-1`** |
| **`L2`** | **relevé d'état des QUATRE unités** — `<unité-superviseur>`, `<unité-pont>`, `<unité-démon>`, `<timer-guard>` : **état**, **identifiant d'invocation**, **compteur de relances** | lecture | **`RE-2`**, **`RE-5`**, **`RA-3`** |
| **`L3`** | lire la **configuration de journalisation du système** — le ou les fichiers qui décident de la **persistance** du journal | lecture de fichier | `S4` |
| **`L4`** | **énumérer les démarrages** connus du journal | lecture | `S4` |
| **`L5`** | lire les **enregistrements persistants de démarrage et d'arrêt**, bornés aux entrées encadrant la date du préflight `G.2` | lecture | **`A`** — `S3` |
| **`L6`** | lire **`<script-superviseur>`**, aux seules fins de déterminer : **(i)** le **puits de journalisation** de ses chemins terminaux · **(ii)** la **forme exacte de la commande de redémarrage machine** · **(iii)** la **forme exacte de la commande de redémarrage du pont** | lecture de fichier | `S2` |
| **`L7`** | **si et seulement si `L6` établit un puits FICHIER** : **empreinte de ce puits prise AVANT de le lire**, puis lecture **bornée** à la fenêtre du §6.1 | lecture de fichier | `B`, `C` — `S2`, **`RE-1 bis`** |
| **`L8`** | lire les **définitions d'unité** des **quatre** unités — pour établir **qui peut commander** un redémarrage machine, **et quelles dépendances propagent un redémarrage** | lecture de fichier | `B`, §7.1.1 — `S5` |
| **`L9`** | **`<journal-démon>`** : **d'abord établir la RÉTENTION** — que la source couvre effectivement la date visée —, **puis seulement** lire les événements bornés à la fenêtre du §6.1 | lecture | `A` — `S7` |
| **`L10`** | lire le **journal des démarrages survivants**, borné à la fenêtre du §6.1 | lecture | `B`, `C` — `S1` |
| **`L11`** | **inventorier et vérifier** l'artefact terrain `G.2` contre ses **trois empreintes**, puis en **lire** les pièces de préflight | lecture, **hors ligne** | `A`, `B`, `C` — `S6` |
| **`L12`** | **empreintes FINALES** — même ensemble que `L1` pour **`RE-1`**, **plus** le puits de `L7` s'il existe pour **`RE-1 bis`** | lecture | **`RE-1`** et **`RE-1 bis`** |

> **`L0` figure dans la liste close, et c'est délibéré.** `P1-H` §2 consigne que
> ce relevé exact a été exécuté **hors liste close** sous `W4-P1`, et que
> **`P1A-1` était dû et n'a pas été pris**. L'erreur n'est pas répétée : l'acte
> est **prévu**, donc licite.

> **Clause — répétitions structurées, explicitement autorisées.**
>
> Les actes **`L0`** et **`L2`** **MAY** être répétés, **à l'identique dans leur
> forme**, aux moments suivants — et à ceux-là seulement :
>
> | | Quand | Pourquoi |
> |---|---|---|
> | 1 | **au début**, avant toute lecture de contenu | établir l'état initial |
> | 2 | **à la fin**, après la dernière lecture | établir `RE-2`, `RE-3`, `RE-5` |
> | 3 | **entre deux actes de lecture**, si l'exploitant conçoit un doute sur la stabilité de l'installation | rendre **`RA-3`** et **`RA-4`** détectables **pendant** le lot, et non seulement après |
>
> **Chaque répétition est consignée avec son horodatage.** Une répétition n'est
> **pas** un acte hors liste close ; **un acte répété sous une forme différente
> en est un** — `RA-1`.
>
> **Sans le cas 3, `RA-3` et `RA-4` seraient des critères sans moyen** : rien
> n'aurait permis de constater un changement d'état **avant la fin du lot**.

> **Aucun acte ne produit de fichier sur l'hôte.** Les sorties sont **rapatriées
> et figées hors de l'installation** ; l'hôte n'en garde rien.

### 5.1 Règle de méthode — analyse hors ligne obligatoire

> **Clause, reprise de la règle `A-2` du `G3` §6.6.**
>
> Tout constat portant sur la **table des processus** **MUST** être établi sur un
> **instantané figé, analysé hors ligne**, avec **motif témoin**. Un filtrage
> exécuté en direct **MUST NOT** fonder un constat : *« il se compte lui-même »*,
> y compris par son **libellé d'affichage**.
>
> **La même discipline vaut pour toute l'analyse du présent lot** : les actes
> `L0` à `L12` **figent** de la matière ; **le raisonnement se fait hors ligne**,
> sur cette matière figée.

### 5.2 `L9` — conduite propre, et ses deux verrous

> **Verrou 1 — la rétention se vérifie AVANT d'exploiter.** `L9` établit d'abord
> que `<journal-démon>` **couvre effectivement** la date visée. `P2-B` §3, fait
> `F-6`, donne à cette couverture un fondement structurel — *« aucune rotation ne
> couvre `<journal-démon>` »* —, **mais un fondement n'est pas un constat.** Tant
> que la couverture n'est pas **constatée**, aucune ligne n'est exploitée.
>
> **Verrou 2 — la conclusion `SOURCE NON DISCRIMINANTE` est licite et normale.**
> Elle est **la conclusion attendue** dès lors que ce que l'on cherche est
> l'origine d'une connexion : `ouverture` §2, précondition 6, l'exclut. **`U-3`
> demeure ouverte, et `L9` ne la réduit pas.**
>
> **Interdiction expresse.** **Une attribution MUST NOT être tirée d'une absence
> d'événement dans cette source** — ni à `F-12`, ni à un client, ni à quiconque.
> Voir §7.3.

---

## 6. Ordre d'exécution, et la fenêtre d'analyse

### 6.1 La fenêtre

> **Elle est définie par le mécanisme, non choisie.** `F-12` déclare **90 s**
> entre la première et la seconde sonde. La fenêtre d'analyse retenue est
> **l'intervalle précédant l'instant du redémarrage**, d'une **étendue au moins
> égale à deux cadences du superviseur** — **`P1-H` §4** relève une *« cadence
> tenue »* de **`190,0 s`** sur les deux intervalles, avec *« contrôle
> indépendant par l'écart des instants de démarrage, 380 s = 2 × 190 s »* —,
> soit **au moins 380 s**.
>
> **L'instant du redémarrage est établi par `L5`**, et par lui seul —
> corroborable par `L9` et `L11`, jamais remplaçable par eux. **Tant qu'il n'est
> pas établi, aucune fenêtre n'existe**, et les actes `L7`, `L9` et `L10` sont
> **sans objet** pour ce qui est de la fenêtre.

### 6.2 L'ordre

| # | Acte | Sortie attendue | Si elle manque |
|---|---|---|---|
| **1** | **`L11`** — artefact `G.2`, **si accessible hors installation** | trois empreintes vérifiées ; inventaire des pièces de préflight | poursuivre ; `L11` est repris au rang 11 |
| **2** | **`L0`** | hôte joignable, horodatage, démarrage courant, temps de fonctionnement | **`STOP`** — sans hôte, aucun acte |
| **3** | **`L1`** — **empreintes de référence, avant toute lecture de contenu** | empreintes des fichiers de la liste | **`STOP`** — sans référence, `RE-1` est inatteignable |
| **4** | **`L2`** — état initial des **quatre** unités | état, invocation, relances | **`STOP`** — sans état initial, `RA-3` et `RE-5` sont sans moyen |
| **5** | **`L3`** | le journal est **persistant** ou **volatil** — fait établi, non supposé | consigner *« non établi »* ; `L4` et `L10` deviennent douteux |
| **6** | **`L4`** | liste des démarrages connus | consigner ; **ne pas conclure** |
| **7** | **`L5`** | **instant** du redémarrage et son **type** — l'élément **`A`** | **`A` est NON ÉTABLI.** Consigner. **L'instruction se POURSUIT** — voir la clause ci-dessous : seuls les actes **réellement dépendants de la fenêtre** deviennent sans objet, et **les rangs 12 et 13 demeurent OBLIGATOIRES**. Le prononcé a lieu au rang 13, sous le **§7.4** |
| **8** | **`L6`** | puits de journalisation · forme des deux commandes | consigner ; `L7` sans objet |
| **9** | **`L8`** — définitions des **quatre** unités | qui peut commander un redémarrage · **quelles dépendances le propagent** (**§7.1.1**) | consigner ; **`B` devient inqualifiable** — **§7.1.1** |
| **10** | **`L7`** — *si et seulement si* `L6` a établi un puits fichier | empreinte prise **avant lecture**, puis lignes de la fenêtre | `L7` sans objet |
| **11** | **`L9`**, puis **`L10`**, puis **`L11`** si non fait au rang 1 | rétention établie puis événements · lignes de la fenêtre · pièces de préflight | consigner |
| **12** | **`L2`** et **`L0`** — **répétition finale** | état et démarrage **inchangés** | un écart est **`RA-3`** ou **`RA-4`** |
| **13** | **`L12`** — empreintes finales, puis **analyse hors ligne** et **prononcé** | empreintes **identiques** · l'un des deux verdicts du §2.2 | un écart d'empreinte est **`RA-2`** |

> **Un acte ne se déplace pas.** Un acte exécuté hors de son rang est un acte
> hors liste close — **`RA-1`**.
>
> **Mais `L0` et `L2` se répètent**, aux trois moments que le §5 autorise, et
> **une répétition n'est pas un déplacement**. Le rang 12 est la répétition
> **obligatoire** ; celles du cas 3 sont **facultatives et consignées**.

> **Le rang 7 n'anticipe plus le verdict, et c'est la correction de la V1.**
> Celle-ci prononçait `INSTANCE NON ATTRIBUABLE` **au rang 5**, alors que six
> rangs restaient à exécuter — dont ceux qui produisent les preuves de
> non-mutation. **Un verdict rendu là aurait laissé le lot ouvert.** Le prononcé
> a lieu **au rang 13, et nulle part ailleurs**.

> **Clause — ce que `A` non établi rend sans objet, et ce qu'il ne rend PAS sans
> objet.** La V2 se trompait ici, et l'erreur était grave.
>
> | Rang | Sort si `A` n'est pas établi | Motif |
> |---|---|---|
> | **8** — `L6` | **exécuté** | ne dépend pas de la fenêtre |
> | **9** — `L8` | **exécuté** | ne dépend pas de la fenêtre |
> | **10** — `L7` | **la LECTURE bornée devient sans objet** — faute de fenêtre. **L'empreinte du puits est prise si le puits existe** | seule la borne temporelle disparaît |
> | **11** — `L9` | **la rétention est établie** ; la **lecture bornée** devient sans objet | idem |
> | **11** — `L10` | **sans objet** | entièrement défini par la fenêtre |
> | **11** — `L11` | **exécuté** | l'artefact ne dépend pas de la fenêtre |
> | **12** — `L2` et `L0`, répétition finale | **OBLIGATOIRE, en toute hypothèse** | il porte **`RE-2`**, **`RE-3`** et **`RE-5`** |
> | **13** — `L12`, puis prononcé | **OBLIGATOIRE, en toute hypothèse** | il porte **`RE-1`**, et **le verdict** |
>
> **La V2 déclarait le rang 12 « sans objet ».** Elle privait ainsi le lot de
> **trois preuves de non-mutation sur cinq**, et rendait la restauration du §9
> **indémontrable** — alors même que le lot n'a rien muté. **Un lot qui ne peut
> pas prouver sa propre innocuité est un lot non clos.**

---

## 7. Règle de décision

### 7.1 Ce qui doit être établi pour `INSTANCE ATTRIBUÉE`

**Trois éléments, CUMULATIFS.** L'absence d'un seul suffit à écarter le verdict.

| # | Élément | Établi par | Corroborable par |
|---|---|---|---|
| **A** | l'**instant** du redémarrage machine, et son caractère de **redémarrage commandé** — non une coupure, non un arrêt matériel | **`L5`**, et par lui seul | `L9` (encadrement de l'interruption) · `L11` |
| **B** | un **redémarrage de `<unité-pont>` commandé par le superviseur**, **dans la fenêtre** précédant cet instant | **`L7`** *(puits du superviseur, s'il existe)* · **`L10`** *(journal survivant)* · **`L11`** *(pièces du préflight)* | — |
| **C** | **au moins un** corroborant : l'**intervalle d'environ 90 s** entre `B` et le redémarrage · **ou** la trace d'une **seconde sonde** dans cet intervalle · **ou** une **ligne propre du superviseur** nommant son chemin correctif | **`L7`** · **`L10`** · **`L11`** | — |

> **`L9` ne porte NI `B` NI `C`, et il en est expressément exclu.**
> `<journal-démon>` ne porte **aucune attribution par client** — `ouverture` §2,
> précondition 6, §3.2 du présent document. Il ne peut donc dire ni **qui** a
> redémarré le pont, ni **qui** a sondé. **Sa seule contribution licite est de
> corroborer `A`**, en encadrant l'interruption par le dernier événement qui la
> précède et le premier qui la suit.
>
> **Toute mention de `L9` au soutien de `B` serait une erreur du présent
> document**, et la V2 en portait une.

> **`B` est le pivot, et il n'est pas remplaçable.** Le redémarrage du pont est
> le **premier acte** du chemin de `F-12`, et le seul qui distingue ce chemin
> d'un redémarrage machine d'une autre origine. **Sans `B`, il n'y a pas
> d'attribution**, quels que soient `A` et `C`.

#### `W4-R` est PLUS STRICT que `G3` §6.1 (a), et c'est un choix

**La différence doit être vue, non découverte après coup.**

`G3` §6.1, branche **(a)**, admet l'attribution *« par la trace du redémarrage du
pont qui le précède, par celle de la seconde sonde, **ou par tout autre
observable rattachant l'instance au mécanisme** »*.

> **`W4-R` retire la troisième voie.** Il exige **`B`** — le redémarrage du pont
> commandé par le superviseur — **en tout état de cause**, là où `G3` se
> contenterait d'un observable quelconque.

| | `G3` §6.1 (a) | `W4-R` §7.1 |
|---|---|---|
| trace du redémarrage du pont | suffisante | **obligatoire** |
| trace de la seconde sonde | **suffisante seule** | corroborant `C` seulement |
| tout autre observable rattachant | **suffisant seul** | **non admis seul** |

> **Conséquence assumée, et elle n'est pas mince.** `W4-R` **peut prononcer
> `INSTANCE NON ATTRIBUABLE` alors qu'une voie théoriquement suffisante au sens
> de `G3` §6.1 (a) aurait été disponible.** Le lot le sait, et le choisit.
>
> **Motif.** `G3` §6.1 laisse la troisième voie **ouverte et non qualifiée** :
> *« tout autre observable »* n'énonce aucun critère, et rendrait l'attribution
> **appréciative**. Un verdict qui **bloque ou débloque une campagne d'écriture**
> ne peut pas reposer sur une clause dont le contenu se décide au moment de
> l'appliquer.
>
> **Ce resserrement n'amende pas `G3`.** Il **borne `W4-R`**, et lui seul.
> Si l'humain juge le resserrement excessif, il lui appartient de **ne pas
> retenir `W4-R`** comme instrument de `P-A5`, ou d'en autoriser un autre — le
> présent document **ne s'impose pas** comme la seule voie vers la branche.

### 7.1.1 Qualifier `B` — les origines concurrentes du redémarrage du pont

> **Un redémarrage de `<unité-pont>` n'est PAS, en soi, un acte du superviseur.**
> C'est l'erreur que la V1 laissait passer.

**`F-13` l'établit** — `P2-B` §3 : *« l'unité `<unité-pont>` porte une directive
`Requires=` visant `<unité-démon>` »*, et `P2-B` §3.0 en tire la conséquence :
*« **Un redémarrage de `<unité-démon>` redémarre `<unité-pont>`.** C'est […] une
propriété de la dépendance systemd, pas un incident. »*

**Quatre origines, et elles doivent toutes être écartées :**

| # | Origine concurrente | Écartée par |
|---|---|---|
| **O1** | **propagation `F-13`** — `<unité-démon>` redémarre, `<unité-pont>` suit | **un enregistrement POSITIF de l'état de `<unité-démon>` dans la fenêtre**, montrant qu'il **n'a pas redémarré** — §7.1.2 |
| **O2** | **redémarrage automatique** par le gestionnaire de services — politique de relance de l'unité | la **lecture de la définition d'unité** (`L8`) : si l'unité porte une politique de relance, l'origine reste ouverte |
| **O3** | **redémarrage commandé par l'exploitant** pendant le préflight | **un enregistrement POSITIF, daté dans la fenêtre**, portant l'état de l'installation ou les commandes de l'exploitant — §7.1.3 |
| **O4** | **redémarrage consécutif au démarrage de la machine** — l'unité démarre parce que le système démarre | la **position temporelle** relativement à l'instant `A` : un démarrage postérieur au redémarrage machine n'est pas dans la fenêtre |

> **Clause — `B` n'est qualifié que si les QUATRE origines sont exclues PAR
> PREUVE.**
>
> **Une origine qui demeure ouverte suffit à laisser `B` inqualifié**, et le
> verdict est alors **`INSTANCE NON ATTRIBUABLE`**.
>
> **La proximité temporelle ne qualifie rien.** Qu'un redémarrage du pont
> précède le redémarrage machine de quelques dizaines de secondes est
> **compatible** avec `F-12` — et tout autant avec `O1`, `O2`, `O3` et `O4`.
> **Une coïncidence n'est pas une attribution**, et le présent lot ne la traite
> jamais comme telle.
>
> **Si `L8` n'a pas été obtenu, `B` est inqualifiable de plein droit** : `O2` ne
> peut pas être écartée sans la définition d'unité.

#### 7.1.2 `O1` — pourquoi son exclusion est difficile, et ce qui est refusé

> **La V2 proposait de l'écarter par une ABSENCE**, et c'était interdit.
> Elle écrivait : *« l'absence, dans la fenêtre, de tout redémarrage de
> `<unité-démon>` »*. **`W4-C` §9.1 l'exclut** — *« Aucune inférence à partir
> d'une absence de trace. »*

**Ce qui pourrait écarter `O1`, et rien d'autre : un enregistrement POSITIF.**

| Voie | Ce qu'elle exigerait |
|---|---|
| **`L10`** — journal survivant | une trace **explicite** de l'état de `<unité-démon>` dans la fenêtre, montrant qu'il **est demeuré en fonctionnement**. Or ce journal est **déclaré non survivant** — `S1` |
| **`L11`** — pièces du préflight `G.2` | une capture de préflight **datée dans la fenêtre** portant l'état du démon. **Son existence est une question de fait**, que `L11` établit ou non — elle n'est **pas présumée ici** |

> **Aucun observable n'est inventé.** Le présent document **ne prescrit pas** de
> chercher un observable qui n'est pas déjà nommé, et **n'affirme pas** qu'il en
> existe un.

> **Clause — conduite si aucune voie licite n'aboutit.**
>
> Si **ni `L10` ni `L11`** ne fournit d'enregistrement **positif** de l'état de
> `<unité-démon>` dans la fenêtre, alors :
>
> 1. **`O1` DEMEURE OUVERTE**, et le rapport le consigne **en ces termes** ;
> 2. **`B` est INQUALIFIABLE** — §7.1.1, clause des quatre origines ;
> 3. le verdict est **`INSTANCE NON ATTRIBUABLE`**.
>
> **Aucune atténuation n'est admise** : ni *« aucun redémarrage n'apparaît »*,
> ni *« rien n'indique que le démon ait redémarré »*, ni *« l'hypothèse est peu
> probable »*. **Ces formules sont des inférences d'absence**, et elles sont
> **interdites**.

> **Conséquence lucide, et il faut la porter.** `S1` étant déclarée non
> survivante, **l'exclusion de `O1` repose en pratique sur la seule `L11`**.
> Si les pièces du préflight ne portent pas l'état du démon dans la fenêtre,
> **`W4-R` prononcera `INSTANCE NON ATTRIBUABLE`**, et ce sera l'issue correcte.

#### 7.1.3 `O3` — même discipline, et le dossier `G.2` n'est pas exhaustif

> **La V3 laissait subsister sur `O3` le défaut qu'elle venait de corriger sur
> `O1`.** Elle écrivait : *« la campagne consigne ses actes, et un redémarrage
> commandé y figurerait »*. **C'est une inférence d'absence** — si l'acte n'y
> figure pas, il n'a pas eu lieu —, et `W4-C` §9.1 l'interdit au même titre.

**Et l'inférence est ici doublement fautive, car le dossier est DÉMONTRABLEMENT
NON EXHAUSTIF.** Deux pièces du corpus l'établissent, et elles sont dans
`G2-C` §6 :

| | Ce que la réserve établit | Conséquence sur l'exhaustivité |
|---|---|---|
| **`A-5`** | le redémarrage est survenu *« pendant le **préflight**, **hors campagne** »* | **la fenêtre visée précède l'ouverture de la campagne** : ce qui s'y est passé n'était **pas encore** couvert par le protocole de consignation de `G.2` |
| **`A-1`** | *« un nom de fichier réutilisé entre deux publications a **écrasé** la capture de l'`ACK` rejeté […] **aucune capture n'a été recréée après coup** »* | **une pièce du dossier a été perdue en cours de campagne**, et le dossier le consigne lui-même. **Un dossier qui a perdu une pièce ne prouve aucune absence** |

> **Clause — `O3` s'exclut par un enregistrement POSITIF, et par rien d'autre.**
>
> Écarter `O3` exige une **pièce datée dans la fenêtre** portant **l'état de
> l'installation ou les commandes effectivement passées par l'exploitant**, et
> montrant qu'**aucune commande de redémarrage n'a été émise par lui**.
>
> **Le silence du dossier ne vaut pas cette preuve.** *« Aucun redémarrage n'est
> consigné »*, *« la campagne n'en mentionne pas »*, *« l'exploitant n'a rien
> noté »* sont des **inférences d'absence**, et elles sont **interdites**.
>
> **Faute de preuve positive :**
>
> 1. **`O3` DEMEURE OUVERTE**, et le rapport le consigne **en ces termes** ;
> 2. **`B` est INQUALIFIABLE** — §7.1.1 ;
> 3. le verdict est **`INSTANCE NON ATTRIBUABLE`**.

> **Ce que cette exigence rend probable, et qui est assumé.** La fenêtre est
> **antérieure à l'ouverture de la campagne**. Il est donc **peu vraisemblable**
> qu'une pièce datée y porte l'état de l'installation ou les commandes de
> l'exploitant. **`O3` a de fortes chances de demeurer ouverte**, et `W4-R` de
> prononcer **`INSTANCE NON ATTRIBUABLE`** pour ce seul motif.
>
> **Le lot ne s'en écarte pas pour autant.** Un verdict qui **débloque une
> campagne d'écriture** ne se rend pas sur un dossier dont on sait qu'il est
> incomplet.

### 7.2 Ce qui interdit `INSTANCE ATTRIBUÉE`, même si `A`, `B` et `C` sont réunis

> **Clause d'exclusion concurrente.** Si les pièces recueillies rendent une
> **autre origine du redémarrage également soutenable** — redémarrage commandé
> par l'exploitant pendant le préflight, mise à jour automatique, chien de garde
> matériel, coupure d'alimentation —, **et que rien ne la départage**, le verdict
> est **`INSTANCE NON ATTRIBUABLE`**.
>
> **L'attribution est exclusive ou elle n'est pas.**

### 7.3 Le piège de l'absence, nommé et neutralisé

> **`W4-C` §9.1 s'applique intégralement**, et sa formule est reproduite **mot
> pour mot** : *« Aucune inférence à partir d'une absence de trace. »*
>
> **La V1 en donnait une paraphrase entre guillemets** — *« Aucun raisonnement
> par absence de trace »*. Le sens était juste, la citation ne l'était pas.

Et le corpus porte, sur **cette source précise**, un fait qui l'aggrave.
`P1-H` §7 consigne :

> *« `<script-superviseur>` déclare un appel de journalisation sur **chacun** de
> ses chemins terminaux, et pourtant **un tiers** des invocations n'en produit
> aucun tout en se terminant en succès. **Aucune hypothèse n'est formée.** »*

> **Conséquence opposable, et elle vaut dans les deux sens.**
>
> | | |
> |---|---|
> | l'**absence** d'une ligne du superviseur | **ne prouve pas** que le chemin correctif n'a pas été emprunté |
> | elle **ne fonde pas** `INSTANCE NON ATTRIBUABLE` **comme un constat positif** | ce verdict est **le défaut**, jamais une démonstration |
> | la **présence** d'une ligne | vaut ce que vaut son contenu, et rien de plus |
>
> **`INSTANCE NON ATTRIBUABLE` ne dit jamais que `F-12` est hors de cause.** Il
> dit que **le rattachement n'est pas prouvé**, et le rapport **MUST** le
> formuler ainsi.

> **La règle vaut identiquement pour `<journal-démon>`** — §3.2. Un **creux**
> dans la cadence de connexions **n'attribue rien**, ni au superviseur, ni à
> quiconque : `ouverture` §2, précondition 6, exclut toute attribution par
> client, et **`U-3` demeure ouverte**. Une absence d'événement dans cette source
> **MUST NOT** fonder `B`, ni `C`, ni aucune part de l'attribution.

### 7.4 Matière insuffisante — conduite exacte

> **Clause.** Si, après les actes du §6 exécutés dans l'ordre, **`A` ou `B` n'est
> pas établi**, l'instruction **S'ARRÊTE** : **aucun acte supplémentaire n'est
> improvisé**, aucune source nouvelle n'est cherchée, aucune extrapolation n'est
> tentée.
>
> **Le lot prononce alors `INSTANCE NON ATTRIBUABLE`, et se clôt.**
>
> **Ce n'est pas un `STOP` au sens du §8** : le lot a fait ce qu'il devait, et il
> rend le verdict que les faits permettent. **Un lot qui prononce (b) a réussi**,
> au même titre qu'un lot qui prononce (a). Ce qu'il n'a pas le droit de faire,
> c'est **d'aller chercher ailleurs** pour éviter (b).

---

## 8. `ABORT` / `STOP`

> **Un `STOP` n'est pas un verdict.** Un lot arrêté sans verdict prononcé est
> **non clos**, et le dire est préférable à laisser croire qu'il l'est.

| Réf | Déclencheur | Conduite |
|---|---|---|
| **`RA-1`** | un acte **hors liste close** du §5, ou hors de son rang au §6 | **`STOP`** immédiat ; consigner le fait, sans l'effacer ni l'ajouter à la liste |
| **`RA-2`** | une **mutation** est constatée, commandée, ou sur le point de l'être — service, timer, unité, configuration, fichier | **`STOP`** immédiat |
| **`RA-3`** | l'**état d'une unité change** pendant le lot — `<unité-pont>`, `<unité-superviseur>`, `<unité-démon>`, `<timer-guard>` | **`STOP`** ; le lot n'a pas à s'exécuter sur une installation qui bouge |
| **`RA-4`** | **redémarrage machine** pendant le lot, quelle qu'en soit la cause | **`STOP`** immédiat |
| **`RA-5`** | un acte exigerait d'**écrire sur l'hôte** | **`STOP`** ; l'acte n'est pas exécuté |
| **`RA-6`** | l'**autorisation humaine du §10 est absente**, dépassée, ou son périmètre serait excédé | **`STOP`** ; la demander, ou renoncer |
| **`RA-7`** | **doute de l'exploitant**, sans justification à fournir | **`STOP`** |
| **`RA-8`** | une frontière du **§4** est franchie ou sur le point de l'être | **`STOP`** immédiat |

> **Aucune seconde tentative dans la même fenêtre**, et **aucun rejeu** : le lot
> ne se rejoue pas après un `STOP` sans une **autorisation humaine nouvelle**.

---

## 9. Restauration

> **Elle est NULLE, et c'est un fait à prouver, non à déclarer.**

Le lot **n'écrit rien, ne modifie rien, ne redémarre rien**. Il n'y a donc rien à
restaurer. **Mais l'absence de mutation se démontre**, et le lot en porte la
charge.

**Chaque preuve est adossée à un acte de la liste close**, et à un rang du §6.2.
**La V1 les exigeait sans donner l'acte qui les produit** : elles étaient
inexécutables sans franchir `RA-1`.

| Réf | Preuve exigée en sortie | Produite par | Rangs |
|---|---|---|---|
| **`RE-1`** | **empreintes des fichiers de la liste de référence**, relevées **avant** la première lecture de contenu et **après** la dernière — `<script-superviseur>`, les **quatre** définitions d'unité, la configuration de journalisation. **Identiques**. **Le puits de `L7` n'en fait PAS partie** : il relève de `RE-1 bis` | **`L1`** et **`L12`** | 3 et 13 |
| **`RE-1 bis`** | **empreinte du puits de journalisation**, **si et seulement si `L6` en a établi un** : prise **au rang 10, avant d'en lire une ligne**, reprise au rang 13. **Identiques**. **La couverture court de la DÉCOUVERTE à la fin du lot**, et **pas avant** — la réserve est **déclarée** au §9.1 | **`L7`** et **`L12`** | 10 et 13 |
| **`RE-2`** | **identifiant d'invocation** et **compteur de relances** des **quatre** unités — `<unité-superviseur>`, `<unité-pont>`, **`<unité-démon>`**, `<timer-guard>` —, relevés au début et à la fin : **inchangés** | **`L2`**, répété | 4 et 12 |
| **`RE-3`** | **identifiant du démarrage courant** — **inchangé** en fin de lot ; sa modification est **`RA-4`** | **`L0`**, répété | 2 et 12 |
| **`RE-4`** | **aucun fichier créé, modifié ou supprimé sur l'hôte** — les sorties sont **rapatriées et figées hors de l'installation** ; aucun acte de la liste close n'écrit | par construction — §5 | tous |
| **`RE-5`** | **état des quatre unités** en fin de lot, **identique** à celui du début | **`L2`**, répété | 4 et 12 |

> **`RE-2` et `RE-5` couvrent `<unité-démon>`, et la V1 l'omettait.** `L2` porte
> les **quatre** unités, et non trois : le démon est celui dont un redémarrage
> **propagerait** au pont — `F-13`, §7.1.1 —, et l'omettre aurait laissé `O1`
> sans moyen de constat pendant le lot.

> **Une limite héritée est corrigée.** `P1-H` §5 consigne que sous `W4-P1`,
> quatre fichiers avaient été lus **avant** la prise d'empreinte de référence,
> laissant un intervalle non couvert et une **réserve déclarée**. Ici, `L1` est
> au **rang 3**, avant toute lecture de contenu.

> **La séparation de `RE-1` et de `RE-1 bis` n'est pas cosmétique.** La V2
> rangeait le puits de `L7` dans `RE-1`, dont la couverture est annoncée
> *« depuis le rang 3 »* — **une promesse que le §9.1 contredisait dans le même
> document**. Les deux preuves sont désormais **distinctes**, avec des
> **couvertures distinctes**, et **le rapport ne peut plus les confondre**.

### 9.1 Le puits de `L7` — couverture partielle, déclarée

> **Il ne peut pas figurer dans les empreintes de référence, et le nier serait
> faux.** L'existence et l'emplacement du puits ne sont connus qu'**après `L6`**,
> au rang 8 — soit **cinq rangs après** `L1`.
>
> **Conduite retenue — couverture prouvée depuis la découverte.**
>
> | | |
> |---|---|
> | **empreinte prise** | **au rang 10**, par `L7`, **avant d'en lire une ligne** |
> | **empreinte reprise** | **au rang 13**, par `L12` |
> | **intervalle couvert** | de la **découverte** à la **fin du lot** |
> | **intervalle NON couvert** | **du début du lot à la découverte** — et il est **déclaré comme tel** |
>
> **Ce que cette conduite établit** : que **`W4-R` n'a pas modifié ce fichier
> après l'avoir découvert**.
>
> **Ce qu'elle n'établit pas, et qui MUST être écrit dans le rapport** : elle ne
> couvre **pas** l'intervalle qui précède la découverte. **Aucune preuve
> rétroactive n'est fabriquée**, et la réserve est **déclarée**, sur le modèle
> exact de `P1-H` §5.
>
> **Le rapport MUST porter cette réserve nommément.** Une couverture partielle
> présentée comme complète serait un défaut plus grave que la couverture
> partielle elle-même.

> **Clause de non-rétroactivité — opposable, et sans exception.**
>
> **`RE-1 bis` ne couvre JAMAIS rétroactivement.** Sa couverture commence à
> l'instant de la **prise d'empreinte du rang 10**, et **pas une seconde avant**.
>
> **Aucun raisonnement ne MAY l'étendre en arrière** : ni *« le fichier n'avait
> aucune raison de changer »*, ni *« le lot ne l'a pas touché avant de le
> découvrir »*, ni *« son horodatage est antérieur »*. **Aucune preuve
> rétroactive n'est fabriquée** — `P1-H` §5.

---

## 10. Autorisation humaine

> ### `NON DONNÉE`

**Le présent document ne l'accorde pas, ne la sollicite pas implicitement, et
n'en préjuge pas.**

**L'autorisation, si elle est donnée, MUST :**

| # | |
|---|---|
| **1** | être **explicite, distincte et postérieure à l'audit** du présent document |
| **2** | **nommer `W4-R`** |
| **3** | ne porter que sur les **TREIZE actes** de la liste close du §5 — **`L0` à `L12`** —, **dans l'ordre du §6**, et sur aucun autre |
| **4** | **ne porter aucune mutation**, d'aucune nature |

**Elle MUST NOT :**

- être déduite de l'audit, de l'intégration, ou du merge du présent document ;
- se réclamer de l'autorisation d'un autre lot — **`W4-P1`, `W4-P2`, `G.2` et
  `G.3` sont étrangers à celle-ci** ;
- valoir autorisation de `G3`, ni la rapprocher ;
- valoir autorisation du `w4f` §11.2, ni d'un acte réservé du `w4f` §11.1 ;
- valoir autorisation de `T0`, `T1` ou `T2`.

> **Le lot ne rapproche `G3` d'aucune façon.** Il peut, au contraire, **le
> fermer** : la branche **(b)** interdit son exécution — `G3` §6.1.

---

## 11. Sorties exigées

| # | Sortie |
|---|---|
| **1** | l'**état initial** relevé, et les **empreintes de référence** de `RE-1` |
| **2** | les **actes réellement exécutés, dans l'ordre**, avec leur horodatage |
| **3** | pour chaque source **`S1` à `S7`** : **survivante**, **absente**, ou **non établie** — jamais supposée. Pour **`S7`**, la **rétention constatée** avant toute exploitation, et le cas échéant le constat **`SOURCE NON DISCRIMINANTE`** |
| **4** | l'**instant du redémarrage** et son **type**, ou le constat qu'ils ne sont pas établis |
| **5** | l'état de **`A`**, **`B`** et **`C`** du §7.1, **un par un** |
| **5 bis** | pour **`B`** : l'examen des **quatre origines concurrentes** `O1` à `O4` du §7.1.1, **une par une**, avec ce qui a écarté chacune — ou le constat qu'elle demeure ouverte |
| **6** | l'examen de la **clause d'exclusion concurrente** du §7.2 |
| **7** | le **verdict** — `INSTANCE ATTRIBUÉE` ou `INSTANCE NON ATTRIBUABLE` — avec ce qui l'a établi |
| **8** | les preuves **`RE-1`**, **`RE-1 bis`**, **`RE-2`**, **`RE-3`**, **`RE-4`** et **`RE-5`**, avec l'acte et le rang qui les ont produites |
| **8 ter** | pour **`RE-1 bis`** : l'état du puits — **découvert** ou **inexistant**. S'il a été découvert, les **deux empreintes** (rangs 10 et 13) **et la réserve de couverture partielle du §9.1, nommément** : la couverture court **de la découverte à la fin du lot**, et **jamais rétroactivement** |
| **8 bis** | la liste des **répétitions structurées** de `L0` et `L2` effectivement exécutées, avec leur horodatage et leur motif |
| **9** | tout **`RA`** atteint, **prononcé ou non**, et le fait qu'il l'ait été ou non |
| **10** | ce qui **demeure non établi** |

> **Aucune donnée de site ne figure au dépôt.** Le rapport est **gelé hors
> dépôt** ; le dépôt n'en portera que les empreintes, sur le modèle de
> `G2-C` §4.

---

## 12. Ce que ce document ne fait pas

Il **n'exécute rien** · **n'autorise rien** · ne conduit aucun terrain · ne lit
aucune installation · ne redémarre rien · ne modifie ni service, ni timer, ni
pont, ni démon, ni configuration · n'écrit pas sur la chaudière · n'ouvre ni
`T0`, ni `T1`, ni `T2` · **ne rejoue pas `F-12`** · ne tranche pas `P-A5` ·
n'autorise pas `G3` et ne le rapproche pas · n'amende aucun contrat · ne lève
aucune inconnue · ne modifie pas l'index du corpus.

Il borne un acte de lecture, le referme, et s'arrête là.

---

## 13. Réserves conservées

1. **La source principale est déclarée perdue.** `G2-C` §6 : le journal du boot
   précédent n'a pas survécu. **La probabilité d'aboutir à `INSTANCE ATTRIBUÉE`
   est faible**, et le lot est conçu pour que **(b)** soit une issue **normale**,
   non un échec.
2. **`S2` est une conjecture de structure, non un fait.** Que
   `<script-superviseur>` dispose d'un puits de journalisation **hors journald**
   n'est **pas établi** ; **`L6`** a précisément pour objet de le déterminer, et
   il peut conclure qu'il n'y en a pas.
3. **La localisation de l'artefact `G.2` n'est pas établie** (§3.1). Si elle
   suppose l'accès au réseau de l'installation, **`L11` est aussi contraint que
   le reste**, et l'avantage attendu du rang 1 disparaît.
4. **Le renoncement à reproduire `F-12` a un coût**, et il est assumé : c'est la
   voie la plus directe vers la signature recherchée, et elle est **interdite
   sans réserve** (§4).
5. **Le lot ne réduit aucune inconnue.** `U-1`, `U-2`, `U-3`, `U-7`, `H1`, `H2`,
   `H3`, `H6` demeurent **ouvertes** ; `C1` demeure non satisfaite et non
   calculable ; la coexistence demeure **non qualifiée**.
6. **`W4-R` est PLUS STRICT que `G3` §6.1 (a)**, et le §7.1 le déclare. Il
   **peut prononcer `INSTANCE NON ATTRIBUABLE` alors qu'une voie théoriquement
   suffisante au sens de `G3` aurait existé** — la troisième, *« tout autre
   observable »*, que `W4-R` n'admet pas seule. **Le resserrement est volontaire
   et motivé** ; il n'amende pas `G3`, et **l'humain peut ne pas retenir `W4-R`**
   comme instrument de `P-A5`.
7. **`<journal-démon>` n'attribuera rien à un client**, et le lot le sait avant
   de le lire. `ouverture` §2, précondition 6 ; **`U-3` demeure ouverte** et
   n'est **pas réduite**. Le constat **`SOURCE NON DISCRIMINANTE`** est une
   sortie **normale** de `L9`.
8. **L'exclusion de `O1` repose sur une seule voie praticable, et elle est
   incertaine** — §7.1.2. Quatre faits, dans cet ordre : **`O1` ne s'exclut que
   par un constat POSITIF** de l'état de `<unité-démon>` dans la fenêtre, jamais
   par une absence ; **`L9` n'y contribue pas**, ne portant ni `B` ni `C`
   (§7.1, §3.2) ; **`L10` dépend de `S1`, déclarée non survivante** ; **seule
   `L11` peut donc potentiellement fermer `O1`**, et seulement si les pièces du
   préflight portent effectivement cet état, ce qui **n'est pas présumé**.
   **À défaut, `O1` demeure ouverte et `B` est inqualifiable.**
8 bis. **`O3` est dans la même situation, et pour un motif propre** — §7.1.3.
   Le dossier `G.2` est **démontrablement non exhaustif** : la fenêtre est
   *« hors campagne »* (`A-5`), et une pièce a été **écrasée** en cours de
   campagne (`A-1`). **Le silence du dossier ne prouve donc rien**, et `O3` a de
   **fortes chances de demeurer ouverte**.
9. **La couverture d'empreinte du puits de `L7` est partielle**, et déclarée
   telle (§9.1). L'intervalle antérieur à sa découverte **n'est pas couvert**, et
   **aucune preuve rétroactive n'est fabriquée**.
10. **Une ambiguïté du corpus est signalée, et non traitée ici.** `debug` §G
   définit **quatre classes normatives** — `debug` §G.1 à `debug` §G.4 —,
   reprises par `w4f2-regime-instruction.md` §13.2, tandis que `G.1`, `G.2` et
   `G.3` désignent aussi des **actes** : `w4f2-g1-constat.md`, `G2-P`, `G3`.
   **`G3` traverse précisément la classe `debug` §G.3**, *« interruption de
   service — le seuil qualitatif »*, en arrêtant le pont et le démon.
   **Le §0 de `G3` traite cette collision comme lexicale ; elle est aussi
   sémantique.**
   Le présent lot **s'en écarte** par sa désignation (§1), **pose une règle de
   citation locale** (§0) — et **ne corrige rien au-delà**. Le traitement de
   l'ambiguïté dans `G3`, `debug` et `w4f2-regime-instruction.md` relève d'un
   **arbitrage humain et d'un lot distinct**, que le présent document n'ouvre
   pas.

---

## 14. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture et bornage de `W4-R`, lot en **lecture stricte** instruisant la précondition `P-A5` de `G3`. Périmètre, deux verdicts exclusifs, liste close de neuf actes, ordre opposable, règle de décision à trois éléments cumulatifs avec clause d'exclusion concurrente, neutralisation du piège de l'absence, conduite en matière insuffisante, huit critères d'arrêt, restauration nulle prouvée par cinq preuves, autorisation **`NON DONNÉE`**. Aucun terrain, aucune exécution, aucune autorisation. |
| **2** | Après audit. Six blocages fermés et une règle de désambiguïsation ajoutée, sans terrain. `B1` : **`<journal-démon>`** entre comme source **`S7`** (§3.2) et comme acte **`L9`**, avec **rétention vérifiée avant exploitation**, conclusion **`SOURCE NON DISCRIMINANTE`** licite, et **interdiction d'attribuer par absence** — `U-3` demeure ouverte. `B2` : les preuves de non-mutation deviennent **exécutables** — trois actes les portent (`L1` empreintes de référence, `L2` état des **quatre** unités dont `<unité-démon>`, `L12` empreintes finales), et les **répétitions structurées** de `L0` et `L2` sont **explicitement autorisées**, sans quoi `RA-3` et `RA-4` étaient des critères sans moyen. `B3` : le **resserrement volontaire** par rapport à `G3` §6.1 (a) est **déclaré** — `B` demeure pivot obligatoire, et ce choix **peut produire `INSTANCE NON ATTRIBUABLE`** malgré une voie théoriquement suffisante. `B4` : nouveau **§7.1.1** — quatre origines concurrentes du redémarrage du pont, `F-13` en tête ; **`B` n'est qualifié que si les quatre sont exclues par preuve**, et **jamais par proximité temporelle**. `B5` : nouveau **§9.1** — la couverture d'empreinte du puits est **prouvée depuis sa découverte** et **déclarée ne pas couvrir ce qui précède**. `B6` : renvois et citations corrigés — autorisation **§10**, rang de l'instant **sans anticipation du verdict**, cadence sourcée sur **`P1-H` §4**, `W4-C` §9.1 **cité mot pour mot**. **Désambiguïsation `G.n`** posée au §0 et appliquée. **Autorisation toujours `NON DONNÉE`.** |
| **3** | Après réaudit. Sept blocages fermés, sans terrain. `R1` : la renumérotation de la V2 est **propagée au §7.1** — `A` sur **`L5`**, `B` et `C` sur **`L7`, `L10`, `L11`** seuls, et **`L9` expressément exclu** de `B` et de `C`, sa seule contribution licite étant de corroborer `A`. `R2` : le §6.2 déclarait le **rang 12 « sans objet »** quand `A` manque — **faux et grave**, ce rang portant `RE-2`, `RE-3` et `RE-5` ; une clause distingue désormais ce que l absence de fenêtre rend sans objet de ce qui **demeure obligatoire**, rangs **12 et 13** compris. `R3` : nouveau **§7.1.2** — `O1` ne s exclut **que par un enregistrement POSITIF** de l état de `<unité-démon>` ; **aucun observable n est inventé** ; si aucune voie licite n aboutit, **`O1` demeure ouverte, `B` est inqualifiable, le verdict est `INSTANCE NON ATTRIBUABLE`**, et les formules d atténuation sont nommément interdites. `R4` : décomptes corrigés — **treize actes `L0` à `L12`**, et le §10 les autorise **exactement**. `R5` : quatre renvois faux corrigés — **§7.1.1** (deux occurrences), **réserve n° 10**, **autorisation §10**, et **`G3` §6.1 (a)** cité avec son document. `R6` : **`RE-1 bis`** créée — le puits de `L7` sort de `RE-1`, avec sa **propre empreinte** et une **couverture depuis la découverte seulement**, alignée sur le §9.1. `R7` : les deux formulations fautives passent en **`MUST NOT`**. **Autorisation toujours `NON DONNÉE`.** |
| **4** | Après réaudit. Quatre blocages fermés, sans terrain. `RR1` : **`O3` était encore excluable par une absence** — le défaut que la V3 venait de corriger sur `O1`. Nouveau **§7.1.3** : `O3` ne s exclut que par un **enregistrement POSITIF daté dans la fenêtre**, portant l état de l installation ou les commandes de l exploitant ; à défaut **`O3` demeure ouverte, `B` est inqualifiable, le verdict est `INSTANCE NON ATTRIBUABLE`**. Le motif est sourcé : le dossier `G.2` est **démontrablement non exhaustif** — `A-5` place la fenêtre *hors campagne*, `A-1` consigne une **capture écrasée et non recréée** ; **un dossier qui a perdu une pièce ne prouve aucune absence**. `RR2` : **double négation supprimée au §5.2** — la formule disait le contraire de ce qu il fallait. `RR3` : **réserve 8 alignée sur le §7.1.2** — constat positif seul, `L9` sans contribution à `B`/`C`, `L10` adossée à une source non survivante, **seule `L11` peut potentiellement fermer `O1`** ; réserve **8 bis** ajoutée pour `O3`. `RR4` : **`RE-1 bis` propagée** — `L7`, `L12`, et sortie **8 ter** au §11 ; **clause de non-rétroactivité** ajoutée au §9.1, sans exception. **Autorisation toujours `NON DONNÉE`.** |
