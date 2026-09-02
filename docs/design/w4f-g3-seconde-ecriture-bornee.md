# `G.3` — seconde écriture terrain **bornée et réversible** sur `heating_curve_shift`

> **Version 4**, après réaudit. **Un blocage résiduel fermé.** Aucun terrain.
>
> | | Correction |
> |---|---|
> | **V4 · C5** | **L'extension du puits n'était subordonnée à rien.** Rédigée à l'indicatif, elle devenait opposable **par la seule intégration du document** — alors que la levée du `w4f` §11.2, au §6.3, exige d'être *« comprise dans l'autorisation humaine et portée nommément par elle »*. **L'asymétrie est supprimée** : l'extension est **subordonnée dans les mêmes termes** (§6.5), l'autorisation la **porte nommément** (`P-9`, §13 item 7), et **le geste de réarmement devient un acte de la campagne, au temps 8** — il ne peut donc plus être accompli avant que l'autorisation existe. `P-SPT` est ramenée à la **préparation** et à la capture *« avant »*, qui exige la variable **ABSENTE** |
>
> **Version 3**, après réaudit. **Quatre blocages résiduels fermés.** Aucun
> terrain.
>
> | | Correction |
> |---|---|
> | **V3 · C1** | **L'extension du puits ne visait qu'une clause sur trois.** Elle est refondue en **extension NOMINALE** visant les **deux clauses opposables** — `SPT` §5.4 et la **condition 2** portée dans `W4-A` §17 — et **ferme** l'encadré du `SPT` §8. `G.2` n'en redevient pas réutilisable, et **aucune campagne après `G.3`** ne s'en autorise — §6.5 |
> | **V3 · C2** | **Les six réserves du `SPT` §10 n'étaient pas reprises.** Elles le sont, une par une. Les réserves **2** — volume d'atelier **non borné** — et **3** — I/O du puits **hors** `write_timeout_s`, **invisible** dans `duration_s`, **décalant** la relecture — sont traitées, et il est dit expressément que **ni `AB-4`, ni `AB-7`, ni `I-7` ne les couvrent** — §6.5.1 |
> | **V3 · C3** | **`P-R` était contradictoire** — « non bloquante » **et** ligne du tableau des préconditions. L'identification de `R-2`…`R-6` aux réserves 2 à 6 du `SPT` §10 est **instruite sur pièces et ÉCARTÉE** : la PR #81 porte ses propres `R-*`. `P-R` **sort du tableau** et devient une **réserve avec obligation de rapport** — §6.6 (ii) |
> | **V3 · C4** | **La portée était incohérente.** La levée ponctuelle du `w4f` §11.2 et le réarmement du puits **manquaient** au tableau *« ce que `G.3` lève »*, et le réarmement figurait dans *« ce qu'il ne lève pas »*. Corrigé, et **aligné sur le §13** — §11 |
>
> **Version 2**, après audit. **Six blocages fermés.** Aucun terrain.
>
> | | Correction |
> |---|---|
> | **V2 · B1** | **`P-A5` était mal posée.** Elle présentait la *« condition déclenchante »* comme inconnue, alors que le **mécanisme `F-12` est ÉTABLI** — registre **configuration déclarée**. Le reliquat réel est l'**attribution de l'instance** observée, en **exécution observée**. `P-A5` est reformulée sur ce reliquat, à **deux branches**, dont l'une **bloque** `G.3` — §6.1 |
> | **V2 · B2** | **Le puits de preuve transport était supposé disponible : il ne l'est pas.** `SPT` §5.4 le borne à la campagne `G.2` *« et aucune autre »*, et `G2-C` §7 le déclare désarmé. Une **clause de réarmement bornée à `G.3`** est créée, avec **précondition** et **preuve de retrait en sortie** — §6.5 |
> | **V2 · B3** | **Les preuves de sortie manquaient entièrement.** Le `G2-P` §16 est repris **sans allègement**, trois preuves propres à `G.3` s'y ajoutent, et les verdicts **`G.3 CONFIRMÉ`** / **`G.3 ABORT`** sont définis — §9 |
> | **V2 · B4** | **La V1 se trompait sur le `w4f` §11.2.** Démarrer, arrêter et retirer `<unité-boilerack>` **ne figurent dans AUCUN des quatre actes réservés** — `w4f` §11.1 le dit en toutes lettres. Une **levée ponctuelle et bornée** du §11.2 est créée pour les **quatre gestes** du protocole, **sans requalifier son statut général** — §6.3 |
> | **V2 · B5** | **Les réserves de `G2-C` §6 n'étaient pas inventoriées.** Les **dix-neuf** sont recensées, et `A-2`, `A-3`, `A-4` **deviennent des règles de `G.3`**. Le fait que le contenu de `R-2` à `R-6` **ne soit pas dans le dépôt** est constaté, et une précondition l'exige — §6.6 |
> | **V2 · B6** | **Le §4.1 rouvrait `G.2` par sa rédaction** — *« en admettent une chacune »*, au présent. Réécrit : `G.2` **exception passée, consommée, non réutilisable** ; `G.3` **seule exception ouverte** |
>
> **Version 1.** Lot d'ouverture **et** cadrage du régime d'engagement `G.3`,
> successeur de `G.2`.
>
> **Il propose. Il n'autorise rien.** Sur le modèle établi par `G.1` puis `G.2` :
> un acte **borné**, **proposé par un document, non autorisé par lui**, puis
> autorisé — ou non — par une **décision humaine explicite et distincte**,
> postérieure à l'audit du présent document.
>
> **Aucun terrain, aucune mesure, aucune exécution, aucun code.** Aucune
> constante de site. **`T0`, `T1`, `T2` demeurent non ouverts** ; `C1`, la
> coexistence, `W4-P` et `W4-Q` **ne sont pas touchés**.

---

## 0. Convention de citation

Les citations sont reproduites **mot pour mot**. Les unités sont désignées
`<unité-boilerack>`, `<unité-pont>`, `<unité-superviseur>`, `<timer-guard>`,
`<script-superviseur>`.

| Nom court | Document |
|---|---|
| `w4f` | `w4f-write-sovereignty.md` |
| `G2-P` | `w4f-g2-ecriture-bornee.md` — le **protocole** de `G.2` |
| `G2-C` | `w4f-g2-constat.md` — le **constat** de clôture de `G.2` |
| `SPT` | `g2-sortie-preuve-transport.md` — la sortie de preuve transport |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `W4-A` | `w4a-vclient-write-adapter.md` |
| `A5x` | `w4f2-a5-extraction.md` |
| `A5` | `arsenal … boiler_pi/mqtt.md` — contrat MQTT du pont historique, source de `A5x` |

**Règle reprise de `G2-P` §0, sans allègement** : toute référence à un autre
document **MUST** porter son **nom court** ; une référence **sans nom court**
désigne **le présent document**, et rien d'autre.

> **Collision de nom, levée d'emblée.** Le corpus emploie déjà `G.1` et `G.2`
> comme **régimes d'engagement**, et `w4-cadrage-activation-debug.md` porte, dans
> son annexe `G.`, **quatre libellés de section** — `G.1`, `G.2`, `G.3`, `G.4` —
> qui n'ont aucun rapport avec eux. La collision **préexiste** pour `G.1` et
> `G.2`, et `G.3` l'étend d'un cran.
>
> **Règle de citation, opposable.** `G.3` **sans qualificatif** désigne le
> **régime d'engagement** défini par le présent document. Le libellé de section
> se cite **toujours** avec son porteur : *« `w4-cadrage-activation-debug.md`
> §G.3 »*. Le précédent est établi : `SPT` a levé la même ambiguïté entre l'acte
> `G.2` et le document `w4f-g2`.

---

## 1. Désignation, et ce que l'ouverture fait

> **Le régime successeur de `G.2` est désigné `G.3`.**

La série des régimes d'engagement est continuée sans rupture : `G.1` lecture
bornée sans mutation, `G.2` écriture bornée et réversible, `G.3` **seconde**
écriture bornée et réversible.

| | |
|---|---|
| Elle **nomme** un régime distinct, citable sans ambiguïté | oui |
| Elle en fait un **sous-lot de `W4-F`** | **non.** `G.3` n'est pas `W4-F3`, ne s'insère pas dans la table du `w4f` §10.7, et n'hérite d'aucune position contractuelle |
| Elle **rouvre** `G.2` | **non.** `G.2` demeure **exécutée, close et non réutilisable** — `G2-C` §7 |
| Elle **réutilise** l'autorisation de `G.2` | **non, et c'est le point cardinal** — §3 |
| Elle **requalifie** `W4-F2`, ou ouvre `W4-F3` | **non.** `W4-F2` reste `NON QUALIFIABLE` hors exception ; `W4-F3` reste **inadmissible** |

---

## 2. Autorité amont

| Document | Rôle | État |
|---|---|---|
| **`G2-C` §7** | établit que `G.2` est **consommée**, et que *« une nouvelle écriture exige une **nouvelle autorisation normative, appuyée sur un document qui la définit**, puis une **décision humaine explicite et distincte** »* | **intégré, en vigueur** — c'est le **fondement de l'existence** du présent lot |
| **`G2-P`** | porte la **forme éprouvée** : préconditions, `EI-1..EI-13`, preuve *one-writer*, protocole en quatorze temps, restauration, gardes, référentiel `ABORT` | intégré, en vigueur |
| **`G2-C` §6** | consigne les réserves **conservées et non corrigées**, dont **`A-1`** et **`A-5`** | intégré, en vigueur |
| `w4f` §11.1, §11.3 | la clause dominante des quatre actes réservés, et la table des phases | intégré, en vigueur |
| `SPT` | le puits de preuve transport, et sa numérotation déterministe | intégré, en vigueur |

---

## 3. Ce qui se reprend, et ce qui ne se reprend pas

> **La FORME se reprend. L'AUTORISATION ne se reprend pas.** C'est la distinction
> portante du présent document, et rien de ce qui suit ne l'atténue.

| Objet | Sort |
|---|---|
| **le protocole de `G2-P`** — §7 à §16 : `EI-1..EI-13`, `EI-8` *one-writer*, les quatorze temps, la conduite de restauration de valeur, l'extinction, les cinq étapes, `G-a`/`G-b`, `FA-1..FA-12`, `AB-1..AB-9`, le prédicat de `V_attendue` | **REPRIS INTÉGRALEMENT, SANS ALLÈGEMENT**, par renvoi nommé — §8 pour le protocole, §9 pour les preuves de sortie |
| **la dérogation du `G2-P` §3** | **ÉTEINTE.** *« La dérogation s'éteint à l'achèvement de `G.2` […] Elle ne se reconduit pas […] aucune seconde campagne ne s'en autorise »* |
| **l'autorisation humaine de `G.2`** | **CONSOMMÉE** — `G2-C` §7. Elle **MUST NOT** être invoquée, ni en tout ni en partie |
| **le constat `G.2 TERRAIN VALIDÉ`** | **acquis de fait, non transposable en droit.** Il établit que la chaîne a fonctionné une fois ; il n'autorise rien |

> **Reprendre un texte technique n'est pas se prévaloir d'une autorisation
> épuisée.** `G2-P` demeure un document **intégré et en vigueur** : ce qu'il
> décrit — comment on prouve un arrêt, comment on établit `EI-8`, dans quel ordre
> on restaure — reste vrai indépendamment du fait que sa dérogation soit
> consommée. **C'est la clause d'exception du §3 de `G2-P` qui est morte, pas son
> protocole.**
>
> **Le présent document doit donc créer sa PROPRE clause d'exception** — §4 —, et
> il ne peut pas se contenter de renvoyer à celle de `G.2`.

---

## 4. Clause `G.3` — amendement du séquencement de `w4f` §11.1

`w4f` **§11.1** réserve **quatre actes** à une autorisation *« explicite,
distincte, **postérieure à l'audit de W4-F3**, et portant sur cette
campagne-là »*. `W4-F3` est **inadmissible** — `w4f` §10.3.4, deuxième condition
non tenue. Le verrou est **de séquencement**, et son objet n'est pas l'acte visé
ici : `G2-P` §2.2 l'a établi, et rien ne l'a infirmé.

> **Clause d'exception — bornée, non générale, et distincte de celle de `G.2`.**
>
> Par dérogation au séquencement de `w4f` §11.1, les actes réservés **1**, **2**
> et **3** de cette clause peuvent être autorisés **une fois**, pour la seule
> campagne `G.3` définie au §8 du présent document, **sans que `W4-F3` soit
> ouvert ni audité**, et **sans que la coexistence ait été qualifiée** au sens de
> `w4f` §10.3.3.
>
> La levée de l'acte **3** est **strictement instrumentale** : elle n'autorise
> que ce qu'exigent `PR-1`, `PR-2` et la preuve *one-writer* de `G2-P` §8.1, pour
> la seule durée de la campagne, et **impose** la restauration vérifiée du
> dispositif historique selon les **cinq étapes** de `W4-C` §13, reprises au
> `G2-P` §11.2.
>
> L'acte réservé **4** — **bascule de souveraineté** — demeure **intégralement
> interdit**. **Aucune bascule permanente de souveraineté n'est créée, ni
> préparée, ni rendue plus proche.**
>
> Cette dérogation **MUST** faire l'objet d'une **autorisation humaine explicite
> et distincte**, postérieure à l'audit du présent document, et **portant
> nommément sur `G.3`**.
>
> Elle **MUST NOT** être déduite : ni de l'audit de ce document, ni de son
> intégration, ni de la clôture d'un lot quelconque, ni du succès de `G.2`, ni de
> l'autorisation qui a permis `G.2`, ni du fait que
> `[transaction_surface].enabled` **puisse** valoir `true`.
>
> **La dérogation s'éteint à l'achèvement de `G.3`**, quel qu'en soit le
> résultat, `ABORT` compris. Elle ne se reconduit pas, **ne crée aucune autorité
> permanente**, et **aucune campagne ultérieure ne s'en autorise**.

### 4.1 Amendement de `w4f` §11.3

Le `G2-P` §3.1 a déjà amendé la phrase *« W4-F4 est le seul sous-lot où une
écriture réelle est possible »*, **nommément et uniquement**, pour y admettre
`G.2`. **Cette admission est aujourd'hui ÉPUISÉE** : `G2-C` §7 établit que `G.2`
est *« exécutée et close »*, que son autorisation est *« consommée »*, et que
*« `G.2` ne se rejoue pas »*.

> **Clause.** La phrase de `w4f` §11.3, telle qu'amendée par `G2-P` §3.1, est
> amendée de nouveau comme suit, et uniquement comme suit :
>
> *« W4-F4 est le seul **sous-lot** où une écriture réelle est possible.*
>
> *La campagne `G.2`, définie par `w4f-g2-ecriture-bornee.md`, en a admis une.*
> ***Elle est exécutée, close et non réutilisable***, *et sa dérogation est*
> ***éteinte*** *—* `w4f-g2-constat.md` *§7.* ***Elle n'en admet plus aucune.***
>
> *La campagne `G.3`, définie par `w4f-g3-seconde-ecriture-bornee.md`, en admet*
> ***une***, *sous les conditions de ce document.* ***C'est la seule exception
> ouverte à ce jour.*** *»*
>
> Aucune autre ligne de la table des phases n'est modifiée. `W4-F3`, `W4-F4` et
> `W4-F5` demeurent **non ouverts**.

> **La rédaction est délibérée, et celle de la V1 était fautive.** Elle écrivait
> que les campagnes `G.2` et `G.3` *« en admettent une chacune »* — **un présent
> qui rouvrait `G.2`**, en la présentant comme admettant encore une écriture.
> **Ce n'est pas le cas** : `G.2` a admis la sienne, elle l'a **consommée**, et
> **rien ne la rend de nouveau disponible**.
>
> **Aucune formulation du présent document ne peut être lue comme rendant `G.2`
> de nouveau disponible.** Toute lecture en ce sens est **fautive**, et la
> présente clause la contredit expressément.

> **Ce que cet amendement ne crée pas.** Il n'établit **aucune règle de
> reconduction**. Une troisième exception exigerait un troisième document et une
> troisième autorisation, exactement comme celle-ci — et le nombre d'exceptions
> **ouvertes** à un instant donné demeure **au plus une**.

### 4.2 Pourquoi l'acte réservé 2 demeure nécessaire

Inchangé depuis `G2-P` §3.2 : `lifecycle.py` ne compose l'écrivain que si
`config.transaction_surface.enabled` est vrai. Autoriser l'acte 1 sans l'acte 2
produirait une autorisation **inexécutable**.

---

## 5. Le rôle — examiné, et maintenu

> **`heating_curve_shift` / `setNiveauM1`, et lui seul.**

L'instruction d'ouverture demandait de maintenir ce rôle **sauf raison technique
opposable**. La question a été instruite : **aucune raison opposable n'existe, et
c'est l'inverse qui est établi.**

| Fait | Source | Conséquence |
|---|---|---|
| `core/production_profile.py` déclare **un seul** `CommandSpec` avec `write` non nul | lecture du dépôt | **aucun autre rôle n'est inscriptible** sans modifier le profil, ce qui serait un **lot distinct** |
| `setNiveauM1` est la **seule** commande d'écriture **caractérisée** sur le terrain | `G2-P` §6.2 | changer de rôle écrirait une commande **non caractérisée** |
| Le datapoint est à **égalité stricte** — `confirm_tolerance = 0.0` | `A5` §5.3 ; `W4-C` §12.3.2 | la relecture de confirmation reste **binaire**, sans tolérance |
| Toute commande **ECS** — `setTempWWsoll` — est **absente du profil** | `G2-P` §13 | elle demeure **interdite**, et le resterait par construction |

| | |
|---|---|
| Rôle | `heating_curve_shift` |
| Lecture | `getNiveauM1` |
| Écriture | `setNiveauM1` |
| Type | entier · **bornes `[-13 ; 40]`** · pas `1` · tolérance **`0`** |

> **Aucun second rôle. Aucune commande ECS. Aucune rafale. Aucune répétition.**

---

## 6. Les six corrections propres à `G.3`

**C'est ce qui distingue `G.3` de `G.2`, et rien d'autre ne l'en distingue.**
Le protocole est repris sans allègement ; les six points ci-dessous s'y
**ajoutent**.

### 6.1 `A-5` — le reliquat réel, et la précondition qu'il commande

`G2-C` §6 consigne, en réserve **non établie et ouverte** :

> *« un **redémarrage machine commandé par le superviseur** est survenu pendant
> le **préflight**, hors campagne. **Cause non établie** — le journal du boot
> précédent n'a pas survécu. `G-a` et `G-b` ont tenu à travers lui »*

> **La V1 lisait cette réserve trop largement, et il faut le redresser.** Elle
> présentait la *« condition déclenchante »* comme **inconnue**, laissant croire
> que le mécanisme lui-même était à découvrir. **Il ne l'est pas.** Le corpus le
> porte, et le crédit lui revient avant que l'on dise ce qui manque.

#### Le mécanisme est ÉTABLI — registre : configuration déclarée

`w4p2-lot-terrain-borne.md` §3, fait **`F-12`** :

> *« le superviseur, sur échec de sonde, **redémarre le pont**, attend **90 s**,
> resonde — et **si la seconde sonde échoue, il redémarre la machine**. Établi
> par le relevé `A1` figé de `W4-P1`, registre **configuration déclarée** »*

**Le superviseur dispose donc d'un chemin déclaré vers le redémarrage machine**,
et ce chemin est **nommé, sourcé, et borné dans sa durée** — 90 s entre les deux
sondes.

#### Ce qui manque est l'ATTRIBUTION DE L'INSTANCE — registre : exécution observée

`w4p1-lot-terrain-borne.md` §5.1.1 pose la distinction, et elle est opposable :
**une lecture de configuration n'est pas une preuve d'exécution.**

| Objet | Registre | État |
|---|---|---|
| **le mécanisme** — `F-12` | **configuration déclarée** | **ÉTABLI** |
| **qui** a commandé le redémarrage du préflight de `G.2` | exécution observée | **établi** — `<unité-superviseur>` |
| **que CETTE instance soit le chemin de `F-12`** | **exécution observée** | **NON ATTRIBUÉE** — le journal du boot précédent n'a pas survécu |

> **C'est le reliquat, et il est étroit.** Il ne s'agit pas de découvrir un
> mécanisme inconnu : il s'agit de **rattacher, ou non, une instance observée à
> un mécanisme déjà établi**.
>
> **La cohérence n'est pas l'attribution.** Le redémarrage est survenu pendant le
> **préflight**, donc **avant `PR-1`**, à un moment où le superviseur était
> vivant et où le chemin de `F-12` pouvait s'engager. **Cette cohérence est
> réelle, et elle ne vaut pas preuve** : aucun autre chemin de redémarrage n'est
> exclu, et `W4-C` §9.1 tient — *« Aucun raisonnement par absence de trace. »*

> **Clause — `P-A5`, et elle est bloquante.**
>
> Avant l'autorisation de `G.3`, **l'une des deux branches suivantes MUST être
> prononcée**, et consignée :
>
> | Branche | Contenu | Effet |
> |---|---|---|
> | **(a) `INSTANCE ATTRIBUÉE`** | il est établi, **en exécution observée**, que le redémarrage machine du préflight de `G.2` **est** le chemin de `F-12` — par la trace du redémarrage du pont qui le précède, par celle de la seconde sonde, ou par tout autre observable rattachant l'instance au mécanisme | `G.3` **peut** être autorisée : le risque est **connu et borné au mécanisme `F-12`** |
> | **(b) `INSTANCE NON ATTRIBUABLE`** | l'attribution est **impossible** à établir, et cette impossibilité est **déclarée explicitement** | **`G.3` MUST NOT être exécutée** — **`STOP AVANT AUTORISATION`** |
>
> **Aucune troisième branche.** Le silence, le report, ou une attribution
> qualifiée de *« probable »*, *« vraisemblable »* ou *« cohérente »* valent
> **(b)**.
>
> **Ce que la branche (a) apporte, et rien de plus.** Elle borne le risque au
> chemin de `F-12`, **dont `PR-1` neutralise l'origine** : le `G2-P` §12.3
> établit que l'horloge de 90 s *« n'est pas armée »* entre le temps 2 et
> l'étape 4 du `G2-P` §11.2, le superviseur étant neutralisé. **Le risque
> résiduel se déplace alors hors fenêtre** — préflight et après-restauration.
> **Il ne disparaît pas**, et aucun critère `FA` ou `AB` n'en est allégé — §10.

> **Interdiction de requalification, et elle porte l'essentiel.**
>
> Le fait que **`G-a` et `G-b` aient tenu à travers ce redémarrage** est un
> **constat favorable**, et il est vrai. Il **MUST NOT** être requalifié en
> établissement de la cause, ni en garantie que le prochain redémarrage sera
> également inoffensif.
>
> **L'absence de dommage n'est pas la démonstration d'une absence de risque.**
> Le corpus a déjà eu à poser cette garde ailleurs, et le motif est le même :
> une absence dûment constatée ne doit pas être relue, plus tard, comme un
> constat positif.

> **Ce que `P-A5` exige, et où cela se fait.**
>
> Attribuer l'instance suppose de **lire l'installation** — au minimum
> `<script-superviseur>`, dont `W4-P1` a établi qu'il *« déclare un appel de
> journalisation sur chacun de ses chemins terminaux »*, et ce qui subsiste du
> journal autour de l'instance. **Ce document ne conduit aucun terrain**, et n'en
> autorise aucun.
>
> Cette lecture relève d'un **lot borné distinct**, en **lecture stricte**,
> disposant des **six éléments** exigés de toute expérience — lot borné,
> objectif, actes permis, critères d'`ABORT`/`STOP`, restauration, autorisation
> propre. **Aucun de ces six éléments n'existe aujourd'hui**, et le présent
> document **ne les fournit pas**.

> **Une voie prospective existe, et elle n'est PAS ouverte ici.** Rendre le
> journal système persistant permettrait d'attribuer un redémarrage **ultérieur**
> — jamais celui de `G.2`, dont la trace est perdue.
> **C'est une mutation de configuration de l'installation**, donc un acte qui
> exige son propre bornage et sa propre autorisation. Le présent document
> **la nomme pour qu'elle ne soit pas glissée dans un préflight**, et
> **ne la demande pas**.

> **Pourquoi cette précondition est dure, et non une simple vigilance.** Un
> redémarrage machine pendant la fenêtre est déjà `AB-5` et `FA-8` — donc un
> abandon. Mais un abandon **subi à un instant qu'aucun mécanisme connu
> n'explique** n'est pas équivalent à un risque **rattaché et borné** : la
> campagne peut se trouver
> interrompue **après** l'écriture du temps 10 et **avant** la restauration, et
> la clause propre au §10 de `G2-P` interdit alors toute restauration de la
> valeur. **L'installation resterait sur une valeur déplacée.** `EI-1` en borne
> la conséquence ; elle ne l'annule pas.

### 6.2 `A-1` — aucune capture d'`ACK` écrasable

`G2-C` §6 consigne, en défaut d'outillage :

> *« un nom de fichier réutilisé entre deux publications a **écrasé** la capture
> de l'`ACK` rejeté. Le texte de cet `ACK` n'existe que dans le transcript de
> session, et **aucune capture n'a été recréée après coup** »*

**Le défaut est situé exactement.** Il **ne porte pas** sur le puits de preuve
transport : `SPT` §5.3 numérote les captures d'écriture par un **compteur
monotone propre à la campagne**, *« jamais dérivé d'une horloge »*, et **ne peut
pas collisionner**. Le défaut porte sur les captures d'`ACK`, prises par la
**procédure opératoire**, hors du puits.

> **Clause — dépôt en écriture unique, opposable.**
>
> 1. **Tout nom de fichier de capture est UNIQUE dans l'atelier de la campagne**,
>    et **MUST NOT** être réutilisé, quelle que soit l'issue de ce qu'il capture ;
> 2. **le dépôt est en écriture unique** : rencontrer un nom existant est une
>    **erreur**, jamais un écrasement. La procédure **MUST** échouer plutôt que
>    remplacer ;
> 3. **les captures d'`ACK` sont numérotées par un compteur monotone propre à la
>    campagne**, commençant à `01`, incrémenté **à chaque `ACK` reçu** — la règle
>    de `SPT` §5.3, étendue à ce plan ;
> 4. **un `ACK` REJETÉ est une capture comme une autre.** Il est déposé, numéroté
>    et conservé. Un rejet de forme n'est pas un non-événement : `G2-C` §5 a dû
>    reconstituer le sien depuis un transcript de session ;
> 5. **une capture qui n'a pas pu être prise est DÉCLARÉE MANQUANTE**, et
>    **MUST NOT** être recréée après coup. La conduite tenue sous `G.2` était
>    juste ; elle devient une règle.

> **Cette correction est de PROCÉDURE, et n'appelle aucune modification de
> code.** Le puits est déjà déterministe. Ajouter du code ici serait une
> finition étrangère au lot, et le présent document n'en demande aucune.

> **Opposabilité.** La règle est vérifiable sur l'**atelier lui-même** : deux
> captures ne peuvent pas porter le même nom, et le compteur d'`ACK` doit être
> **continu**. Un trou dans la numérotation est une capture manquante, qui
> **MUST** alors être déclarée.

### 6.3 L'autorisation du `w4f` §11.2 — nécessaire, levée ponctuellement, non requalifiée

> **La V1 se trompait, et il faut le dire frontalement.** Elle affirmait que le
> démarrage manuel du temps 8 était *« instrumental à la dérogation »*, et en
> déduisait que `G.3` n'avait *« pas besoin »* de l'autorisation du `w4f` §11.2.
> **Le `w4f` §11.1 dit l'inverse, en toutes lettres.**

> *« **Ce que cette clause ne vise pas.** Elle ne porte **pas** sur
> l'exploitation de `<unité-boilerack>` en lecture seule, **qui relève du
> §11.2**. Installer Boilerack, démarrer son unité, l'arrêter ou la retirer **ne
> figure dans aucun des quatre actes réservés** : ces gestes ne touchent ni la
> chaudière, ni l'autorité, ni le dispositif historique, ni la souveraineté. »*

**Conséquence exacte.** Les actes réservés **1**, **2** et **3** **ne couvrent
pas** les gestes sur `<unité-boilerack>`. **Les lever ne suffit donc pas à rendre
`G.3` exécutable** : il y manque une autorisation d'une autre nature.

**Or le protocole en exige quatre :**

| Temps | Geste sur `<unité-boilerack>` | Pourquoi il est indispensable |
|---|---|---|
| **5** | **arrêtée** | condition de `EI-8` — la fenêtre muette exige qu'aucune session `G.3` ne soit ouverte |
| **8** | **démarrée à la main** | sans elle, `EI-12` est insatisfiable et l'écriture **inexécutable** — `G2-P` §9 |
| **13** | **arrêtée**, arrêt constaté | acte 2 de l'extinction de l'autorité — `G2-P` §11.1 |
| *rollback* | **retirée** | `P-3` |

**Et l'autorisation qui les couvre n'est pas donnée** : `G2-P` §17 porte
*« Précondition 9 / `w4f` §11.2 : **NON DONNÉE** »*, et rien ne l'a donnée depuis.

> **Clause — levée ponctuelle et bornée du `w4f` §11.2.**
>
> Par dérogation à l'exigence d'autorisation du `w4f` §11.2, les gestes suivants
> sur `<unité-boilerack>` peuvent être autorisés **une fois**, pour la seule
> campagne `G.3`, **et exclusivement aux temps que le protocole leur assigne** :
> **arrêter** au temps 5 · **démarrer à la main** au temps 8 · **arrêter** au
> temps 13 · **retirer** au titre du rollback `P-3`.
>
> **Cette levée n'autorise RIEN D'AUTRE** de ce que le `w4f` §11.2 énumère : ni
> *« le faire fonctionner **en lecture seule** »* hors des temps ci-dessus, ni
> *« mesurer la coexistence et la contention »*, ni aucune exploitation continue.
> **`<unité-boilerack>` n'est vivante qu'entre les temps 8 et 13.**
>
> Elle **MUST** être **comprise dans l'autorisation humaine de `G.3`** et
> **portée nommément par elle** : elle ne s'y ajoute pas d'elle-même — §13.
>
> Elle **s'éteint** à l'achèvement de `G.3`, quel qu'en soit le résultat, et
> **ne se reconduit pas**.

> **Ce qui n'est PAS requalifié.**
>
> **Le statut général de l'autorisation du `w4f` §11.2 est INCHANGÉ : elle reste
> `NON DONNÉE`.** La levée ci-dessus est **ponctuelle**, bornée à **quatre
> gestes** et à **leurs temps**, et **ne vaut pas** autorisation du terrain de
> lecture seule. **`W4-F2` n'en est ni rouvert, ni requalifié.**
>
> **Le présent document ne répute donc la précondition 9 ni satisfaite, ni
> dispensée, ni sans objet.** Il constate qu'elle manque, et crée l'exception
> **étroite** sans laquelle `G.3` serait inexécutable — exactement comme le §4
> le fait pour le séquencement du `w4f` §11.1.

**La dissymétrie de fait, qui demeure entière :**

| Fait | Source |
|---|---|
| l'**autorisation `w4f` §11.2** — terrain de lecture seule — demeure **`NON DONNÉE`** | `G2-P` §17, préservations explicites |
| **Boilerack est néanmoins DÉPLOYÉ** sur l'installation, unité **`disabled`** et **`inactive`** hors tests | `G2-C` §6 — la réserve 8 est *« levée par le fait »* |
| le déploiement a été accompli **par le préflight de `G.2`**, dont la précondition `P-1` l'exigeait | `G2-P` §14, `P-1` |

> **`P-1` n'est plus un acte à accomplir, mais un état à CONSTATER.** Boilerack
> est déployé ; `G.3` le **vérifie**, il ne le **déploie pas**. C'est le seul des
> trois motifs de la V1 qui tenait, et il est conservé.

> **La dissymétrie subsiste, et elle est nommée** : une installation porte un
> logiciel dont l'autorisation de déploiement en lecture seule n'a jamais été
> donnée, parce qu'il y a été porté au titre d'une **autre** autorisation, plus
> étroite et désormais consommée. **Statuer sur cette dissymétrie est une
> décision de gouvernance**, elle appartient à l'humain, et **ce document ne la
> prend pas** : un cadrage ne requalifie pas une précondition d'un autre lot.
>
> **Conséquence pratique, dite sans l'adoucir** : si l'humain juge que le
> déploiement de fait doit être régularisé ou défait **avant** toute nouvelle
> campagne, `G.3` en dépend. Le présent document **le signale**, et ne préjuge
> pas du sens.

### 6.4 Réétablissement terrain le jour de l'acte

> **Clause — rien n'est reporté de `G.2`.**
>
> 1. **Les treize preuves `EI-1..EI-13` sont RÉÉTABLIES intégralement**, dans
>    l'ordre du protocole, **le jour de l'acte**. Aucune n'est réputée acquise
>    par le fait qu'elle l'ait été le 2026-08-28 ;
> 2. **`V_brut` est RELU le jour de l'acte**, par les **deux captures `vclient`
>    nues** du temps 6 — **texte** *et* **`-J`** —, hors du chemin Boilerack.
>    `G.2` a restauré la valeur à `2` : **ce chiffre n'est pas reporté**, il ne
>    fonde rien, et il **MUST NOT** servir de référence ;
> 3. **les bornes du `G2-P` §15 sont RÉÉVALUÉES sur le `V_brut` du jour** : la
>    campagne **MUST NOT** être exécutée si `V_canon + 1 > 40`, si `V_brut` est
>    hors de `[-13 ; 40]`, si les deux formes du temps 6 ne concordent pas
>    (`AB-2`), si `V_canon` n'est pas dérivable sans perte (`AB-9`), ou si la
>    garde de fraîcheur du temps 9 échoue (`AB-8`) ;
> 4. **`V_canon − 1` demeure NON ADMIS.** Substituer un autre sens de variation
>    serait une décision non arbitrée — `G2-P` §15. Le cas relève d'un
>    **arbitrage humain distinct**, et `G.3` **s'arrête** plutôt que de le
>    trancher ;
> 5. **`P-A5` est vérifiée avant le temps 1**, et son échec est un **`STOP AVANT
>    AUTORISATION`**, non un `ABORT` — §6.1.

> **Pourquoi ce réétablissement n'est pas une formalité.** `w4f` §12.1 range
> l'**état réel courant de `heating_curve_shift`** parmi les éléments en
> `PREUVE TERRAIN / SOURCE EXTERNE REQUISE`. Une valeur relevée cinq jours plus
> tôt est une **donnée périmée**, et la traiter autrement serait exactement le
> raisonnement documentaire que `w4f` §12.2 interdit : *« Composer, déployer ou
> rédiger n'observe rien. »*

### 6.5 Le puits de preuve transport — épuisé, et à réarmer

> **La V1 supposait le puits disponible. Il ne l'est pas**, et la preuve n°4 des
> sorties en dépend.

**TROIS clauses le bornent à `G.2`, et la V2 n'en visait qu'une.** Les trois
sont reproduites, et l'extension du présent document les vise **nominalement**.

> **Clause opposable n° 1 — `W4-A` §17, exception bornée, condition 2**, telle
> qu'elle est **intégrée et en vigueur** :
>
> *« 2. il n'est actif que pour la **durée d'une campagne** au sens de `G.2` —
> condition **déclarative**, adossée à la preuve du §5.4 de
> `g2-sortie-preuve-transport.md` ; »*

> **Clause opposable n° 2 — `SPT` §5.4**, qui définit *« la campagne »* :
>
> *« **La campagne visée est celle-là même dont les trois captures encadrent le
> déroulement** : la campagne `G.2` instrumentée que l'étape 4 du §8 désigne, **et
> aucune autre**. »*

> **Clause opposable n° 3 — `SPT` §8**, encadré de l'étape 4 :
>
> *« L'étape 4 n'est ni ouverte, ni préparée, ni rendue plus proche. La
> dérogation `G.2` s'est éteinte à l'achèvement de la campagne du 27 août 2026,
> et **aucune seconde campagne ne s'en autorise** — `w4f-g2` §3. »*

> **Ce que la troisième clause dit, et ce qu'elle ne dit pas.** Elle ferme la
> réutilisation **de la dérogation `G.2`** — ce que le §4.1 du présent document
> confirme et n'entame pas. **Elle n'interdit pas qu'une autre exception, créée
> par un autre document, désigne sa propre campagne** : c'est exactement ce que
> le §4 fait pour le séquencement du `w4f` §11.1, et ce que le présent § fait
> pour le puits.
>
> **La distinction est celle du §3 : la forme se reprend, l'autorisation ne se
> reprend pas.** `G.3` ne s'autorise **pas** de `G.2` ; elle crée sa propre
> désignation.

**Deux faits en découlent, et ils sont distincts :**

| | Fait | Source |
|---|---|---|
| **en droit** | l'autorisation d'usage du puits est **ÉPUISÉE** — elle visait `G.2`, *« et aucune autre »* | `SPT` §5.4 |
| **en fait** | l'instrumentation est **DÉSARMÉE** — *« la variable d'atelier a été retirée du fichier d'environnement persisté »* | `G2-C` §7 |

> **Clause — extension NOMINALE, bornée à `G.3`, et à elle seule.**
>
> **La désignation *« au sens de `G.2` »* de la condition 2 portée dans
> `W4-A` §17, et la désignation *« et aucune autre »* du `SPT` §5.4, sont
> étendues à la campagne `G.3`** — **et à aucune autre campagne**.
>
> **Les deux clauses sont visées nommément**, et la seconde parce qu'elle définit
> ce que la première appelle *« la campagne »* : étendre l'une sans l'autre ne
> produirait rien.
>
> La **durée de la campagne `G.3`** se définit **exactement comme le `SPT` §5.4
> définit celle de `G.2`** : *« avant »* signifie **avant le temps 1** ;
> *« pendant »*, **entre les temps 8 et 13** ; *« après »*, **une fois l'étape 5
> achevée**.
>
> **Ce que cette extension NE fait PAS, et il faut le dire nettement :**
>
> | | |
> |---|---|
> | elle **ne rend pas `G.2` réutilisable** | la dérogation de `G.2` demeure **éteinte** — `G2-P` §3, `G2-C` §7, et le §4.1 du présent document. **`G.3` ne s'autorise pas de `G.2`** : elle ajoute **sa propre désignation** à côté d'une désignation épuisée |
> | elle **ne rouvre pas l'étape 4 du `SPT` §8** | cet encadré ferme la réutilisation **de la dérogation `G.2`**. Il n'est **pas** entamé : rien ici ne s'en réclame |
> | elle **n'allège aucune des six conditions** du `SPT` §4.1 | opt-in et **inerte par défaut** · durée d'une campagne · implémentation **hors de l'adaptateur** · **ni métrique ni compteur** · signature d'une **écriture** seulement, **jamais d'une lecture** · **aucune influence sur un verdict**, aucune levée dans le chemin d'écriture |
> | elle **ne crée aucune autorisation permanente** | l'extension **s'éteint** à l'achèvement de `G.3`, quel qu'en soit le résultat, `ABORT` compris |
>
> **Fermeture, symétrique de celle du `SPT` §8.** **Aucune campagne postérieure à
> `G.3` ne s'autorise de la présente extension**, ni de la campagne `G.3`, ni du
> fait que le puits ait servi deux fois. Un usage ultérieur exigerait une
> **nouvelle extension nominale**, portée par un **nouveau document**, et une
> **nouvelle autorisation humaine**.
>
> **Aucune modification de code n'est demandée.** Le puits est **déjà
> implémenté** et son opt-in est une **variable d'environnement persistée** :
> réarmer, c'est **reposer cette variable**, non écrire du code.
>
> **Subordination — dans les mêmes termes que la levée du §6.3.**
>
> **La présente extension ne s'applique PAS par l'intégration du présent
> document.** Elle **MUST** être **comprise dans l'autorisation humaine de `G.3`**
> et **portée nommément par elle** : **elle ne s'y ajoute pas d'elle-même** —
> §13, item 7.
>
> **Tant que cette autorisation n'est pas donnée, l'extension n'existe pas**, et
> les trois clauses opposables ci-dessus gardent leur plein effet : le puits
> demeure borné à `G.2`, *« et aucune autre »*.
>
> Elle **s'éteint** à l'achèvement de `G.3`, quel qu'en soit le résultat, et
> **ne se reconduit pas**.

> **Clause — le réarmement est un ACTE DE LA CAMPAGNE, et il se situe au
> temps 8.**
>
> **La V3 laissait un chemin opérationnel ouvert.** Elle portait le réarmement
> par `P-SPT`, c'est-à-dire par une **précondition** — or les préconditions
> peuvent être satisfaites **dans n'importe quel ordre**, et rien n'imposait que
> `P-9` le fût d'abord. **La variable pouvait donc être reposée avant que
> l'autorisation existe.**
>
> **Elle ne le peut plus.** Le geste de **reposer la variable persistée** est un
> **acte de la campagne**, situé au **temps 8**, **avant l'acte 2** — le
> démarrage manuel de `<unité-boilerack>` —, puisque l'opt-in du puits est lu
> **au démarrage du processus**.
>
> Le temps 8 comporte donc, sous `G.3`, **quatre actes dans cet ordre** :
>
> | | Acte | Preuve |
> |---|---|---|
> | **1** | **persister** `[transaction_surface].enabled = true` | `EI-11` |
> | **1 bis** | **reposer la variable d'atelier persistée** — le réarmement du puits | capture *« pendant »*, §6.5 |
> | **2** | **démarrer `<unité-boilerack>` à la main** | `G-a` reconstatée |
> | **3** | **prouver la surface composée et souscrite**, par une trace côté broker | `EI-12`, puis `EI-13` |
>
> **La campagne ne commence pas sans `P-9`.** Un acte situé au temps 8 est donc
> **structurellement postérieur** à l'autorisation, et **aucun chemin
> opérationnel ne permet plus de réarmer le puits avant elle**.
>
> **Ce que cet ordre ne change pas** : les trois actes du `G2-P` §9, temps 8,
> demeurent **inchangés dans leur contenu et dans leur ordre relatif**. L'acte
> **1 bis** s'insère entre le premier et le deuxième ; **il n'en déplace aucun**,
> et le §8 du présent document reprend le temps 8 sans autre modification.

> **Précondition, extinction et preuve — les trois captures du `SPT` §5.4, sans
> allègement.**
>
> | Moment | Attendu | Sous `G.3` |
> |---|---|---|
> | **avant** le temps 1 | variable **ABSENTE** | à capturer — **c'est l'état actuel**, `G2-C` §7, et **`P-SPT` l'exige tel quel** |
> | **pendant**, unité démarrée | variable **présente** | à capturer — **c'est l'acte 1 bis du temps 8**, postérieur à l'autorisation |
> | **après** l'extinction | variable **absente** | à capturer — **c'est le retrait**, acte de sortie exigible |

> **La capture *« avant »* est elle-même un verrou.** Elle exige la variable
> **ABSENTE** avant le temps 1. Une variable trouvée **présente** à cet instant
> établirait qu'elle a été reposée **hors campagne** — donc **hors
> autorisation** —, et `P-SPT` ne serait **pas** satisfaite.
>
> *« **Sans les trois captures, l'extinction n'est pas établie**, et la campagne
> n'est pas close sur ce point. »* — `SPT` §5.4
>
> **Le retrait est un acte de sortie EXIGIBLE**, au même titre que la persistance
> de `enabled = false` : la variable **MUST** être retirée du fichier
> d'environnement persisté, et le retrait **prouvé**, avant que `G.3` soit
> déclarée close.

#### 6.5.1 Les six réserves du `SPT` §10 — reprises une par une

**La V2 n'en portait qu'une.** Les six sont reprises ; aucune n'est levée.

| # | Réserve du `SPT` §10 | Sort sous `G.3` |
|---|---|---|
| **1** | *« L'amendement de `W4-A` §17 est réel et frontal […] Un auditeur peut juger que l'exception, fût-elle bornée, **ouvre une brèche que la prochaine campagne élargira**. »* | **CONSERVÉE, et elle vise le présent document.** `G.3` **est** cette prochaine campagne. L'extension du §6.5 est **nominale et fermée aux deux extrémités** — elle ne se reconduit pas —, mais **la réserve n'est pas réfutée pour autant**, et le §16 la porte |
| **2** | **le volume de l'atelier est NON BORNÉ** ; *« une écriture au `stdout` volumineux remplirait l'atelier »* | **CONSERVÉE** — traitée ci-dessous |
| **3** | **l'I/O du puits est HORS du budget `write_timeout_s`**, et **invisible dans `duration_s`** | **CONSERVÉE** — traitée ci-dessous |
| **4** | **l'extinction est déclarative** ; les trois captures la *« constatent »*, elles ne l'*« imposent »* pas | **CONSERVÉE** — rien dans le système n'expire la variable |
| **5** | `OBS` §5.1 comportait une **erreur d'analyse**, corrigée frontalement par le `SPT` §4.2 | **CONSERVÉE** — sans effet sur le protocole de `G.3`, et conservée pour n'être pas perdue par omission |
| **6** | *« Rien n'est rétroactif. La campagne du 27 août 2026 demeure une preuve physique solide et une campagne **non close**. »* | **CONSERVÉE TELLE QUELLE.** `G.3` **ne la touche pas, ne l'interprète pas, et ne statue pas** sur cette campagne ni sur son état |

> **Réserve 2 — le volume, et ce que `G.3` peut en faire.**
>
> Aucune borne n'existe sur les octets déposés, et c'est **assumé** par le
> `SPT` §10 : *« borner tronquerait la preuve, et une preuve tronquée ne prouve
> plus l'intégralité que `w4f-g2` §16 item 4 exige »*.
>
> **Ce que `G.3` borne déjà** : la **cardinalité** — au plus **deux** écritures,
> donc au plus **deux trios**. **Ce qu'il ne borne pas** : la **taille** de
> chacun.
>
> **Clause.** `EI-4` exige déjà l'atelier *« créé, vide, sur stockage persistant,
> hors de tout dépôt versionné »*. S'y ajoute, en **sortie** : le **volume final
> de l'atelier est rapporté**, fichier par fichier. **Aucune borne n'est posée**
> — en poser une contredirait le `SPT` §10 — et **le volume est donc un
> observable, non une garantie**.

> **Réserve 3 — le décalage de la relecture, et ce qu'aucun critère ne couvre.**
>
> `SPT` §10, réserve 3 : le budget `write_timeout_s` *« borne le **sous-processus**,
> jamais l'appel `write()` »* ; le dépôt a lieu **après** le retour du
> sous-processus, **hors budget** ; *« cela ne se voit **pas** dans `duration_s`,
> mesurée autour de la seule invocation »*.
>
> `SPT` §8.1 en donne l'effet exact : le dépôt **décale le début** de la fenêtre
> de confirmation, *« il n'en consomme rien »*. **Le budget reste entier ; la
> relecture commence plus tard.**
>
> **Aucun critère du référentiel ne le couvre, et il ne faut pas prétendre le
> contraire :**
>
> | Critère | Ce qu'il mesure | Pourquoi il ne couvre PAS le dépôt |
> |---|---|---|
> | **`AB-4`** | une **invocation** dépassant nettement le budget de 5 s connu | le dépôt survient **après le retour du sous-processus** : il **n'entre pas** dans la durée mesurée |
> | **`AB-7`** | une durée **négative, nulle ou absurde** — *« l'horloge a bougé »* | il porte sur la **cohérence de l'horloge**, jamais sur un délai réel entre deux actes |
> | **`I-7`** | *« délai avant relecture **fiable** »* — `w4f` §12.2 | c'est une **inconnue portant sur l'installation**, non une borne sur l'I/O du puits. **Elle ne mesure rien**, et `w4f` §12.2 interdit de la lever par raisonnement |
>
> **Clause — le décalage est rendu OBSERVABLE, il n'est pas borné.** Les
> **instants d'horloge** du retour de l'invocation d'écriture et du **début de la
> relecture de confirmation** (temps 11) **MUST** être consignés, de sorte que
> l'écart soit **lisible après coup**.
>
> **Ce que cette clause fait, et rien de plus** : elle rend un délai **visible**.
> **Elle ne le borne pas, ne le mesure pas dans `duration_s`, et n'ajoute aucun
> critère d'abandon.** Sur un datapoint à **égalité stricte**, `SPT` §8.1 pose
> qu'un décalage *« ne fausse aucun verdict — mais il éloigne l'observation du
> geste, et cela doit être su »*. **`G.3` fait en sorte que ce soit su.**

### 6.6 Les réserves de `G2-C` §6 — inventaire complet, et sort de chacune

> **La V1 en traitait deux — `A-1` et `A-5` — et laissait les autres hors
> inventaire.** Une réserve qui disparaît par omission n'est pas conservée.

#### (i) Les neuf réserves du `G2-P` §19

`G2-C` §6 : elles sont *« conservées telles quelles »*, **à une exception près**
— la huitième, levée par le fait.

| # | Objet | Sort sous `G.3` |
|---|---|---|
| **1** | `H2` et `H6` **(b)** ouvertes — *one-writer* **borné aux clients du démon** ; seule `FA-3` en offre une **détection**, non une garantie | **conservée** |
| **2** | `U-3` ouverte ; `EI-8` vaut sur **douze secondes**, non sur la campagne | **conservée** |
| **3** | `H6` **(c)** ouverte — sorties précoces ; motif d'abandon, non de poursuite | **conservée** |
| **4** | `U-2` et `U-7` ouvertes ; `C1` **sans objet sur la fenêtre**, non résolue | **conservée** — §12 |
| **5** | la valeur est **déplacée d'un pas** ; une part de la sûreté de `W4-C` n'est pas héritée | **conservée** |
| **6** | la restriction du `G2-P` §10 laisse l'installation sur une **valeur déplacée** après un `ABORT` postérieur à l'écriture | **conservée**, et c'est elle que `A-5` aggrave — §6.1 |
| **7** | l'étape 5 **allonge la fenêtre** d'au moins un cycle du superviseur | **conservée** |
| **8** | *« `P-1` n'est pas acquise — Boilerack n'est pas déployé »* | **LEVÉE PAR LE FAIT** — `G2-C` §6 ; et c'est elle qui ouvre la dissymétrie du §6.3 |
| **9** | l'**interruption de service est réelle** — bornée, réversible, non nulle | **conservée** — elle se reproduira intégralement |
| **10** | le bornage est **opposable, non auto-appliqué** | **conservée** |

#### (ii) Les réserves du lot `sortie de preuve` — `R-2` à `R-6`

`G2-C` §6 les porte comme *« réserves du lot `sortie de preuve`, relevées à
l'audit d'implémentation et **délibérément non traitées** »*, qualifiées **non
bloquantes, conservées**.

**Une identification se présentait, et elle a été instruite sur pièces.**

**Hypothèse examinée** : `R-2` à `R-6` seraient les **réserves 2 à 6 du
`SPT` §10** — cinq items, une plage exactement coïncidente, et le même lot.

**Elle est ÉCARTÉE.** Trois pièces l'établissent :

| # | Pièce | Ce qu'elle montre |
|---|---|---|
| **1** | le corps de la **PR #81** — intégration du lot `sortie de preuve`, étape 3 — porte une section *« Réserves conservées »* : *« `R-2` à `R-6` ne sont **pas** traitées dans ce lot : elles sont conservées telles quelles, non bloquantes »* | **c'est la source directe** de la ligne de `G2-C` §6, mot pour mot, et elle appartient à **l'intégration de l'implémentation** |
| **2** | la **même PR** invoque **`R-1`** comme **contrat de deux garanties de code** — *« Création exclusive (`"xb"`) […] n'est **jamais** écrasée »* et *« Une preuve incomplète est un **constat visible**, pas un silence »* | **`R-1` porte sur l'implémentation**, non sur l'amendement de `W4-A` §17 dont traite la réserve 1 du `SPT` §10. **Les deux numérotations ne se recouvrent pas** |
| **3** | le `SPT` est en **Version 7**, et **aucun de ses labels de correction n'est un `R-*`** — ils sont `B`, `C`, `D`, `L`, `P`, `Q`. Ses réserves du §10 sont numérotées **`1` à `6`**, sans préfixe | la série `R-*` **n'appartient pas au document `SPT`** |

> **Conclusion, et elle est ferme.** `R-1` à `R-6` sont les réserves de
> **l'audit d'implémentation de la PR #81**, distinctes des six réserves du
> `SPT` §10 — lesquelles sont, elles, **intégralement reprises au §6.5.1**.
>
> **Aucune assertion d'absence n'est portée ici.** Le texte de `R-2` à `R-6`
> réside dans **l'audit d'implémentation**, qui est leur source déclarée ; le
> présent document **ne prétend pas qu'il n'existe pas**, et **n'a pas qualité
> pour dire où il se trouve**.

> **Statut, et il n'est pas contradictoire.**
>
> **`R-2` à `R-6` ne sont PAS une précondition de `G.3`.** `G2-C` §6 et la
> PR #81 les qualifient l'une et l'autre de **non bloquantes**, et le présent
> document **ne les requalifie pas**. Elles **ne figurent donc pas au tableau du
> §7** : une ligne ne peut pas être à la fois *« obligatoire »* et *« non
> bloquante »*, et la V2 les portait ainsi.
>
> **Ce qui est dû est une OBLIGATION DE RAPPORT**, et rien de plus :
>
> **Clause.** Le rapport de `G.3` **MUST NOT** déclarer ces réserves
> *« conservées »* sans dire **ce qu'il en a fait** : soit il en reproduit le
> contenu, retrouvé à sa source, soit il **constate qu'il ne l'a pas obtenu**.
>
> **Une réserve dont le rapport ne peut rien dire n'est pas conservée : elle est
> citée.** Le dire est préférable à laisser croire le contraire — et cela
> **n'empêche ni l'autorisation, ni l'exécution**.

#### (iii) `A-1` à `A-5` — les cinq réserves propres à la campagne

| Réf | Objet | Sort sous `G.3` |
|---|---|---|
| **`A-1`** | capture d'`ACK` **écrasée** par un nom de fichier réutilisé | **TRAITÉE** — dépôt en écriture unique, §6.2 |
| **`A-2`** | un **filtrage de la table des processus s'auto-correspond**, y compris par les **libellés d'affichage** ; redressé en figeant un instantané analysé hors ligne, avec **motif témoin** | **TRAITÉE — devient une règle**, ci-dessous |
| **`A-3`** | un **commentaire de configuration obsolète** laissé en place, **non corrigé en fenêtre** — *« pas de polissage sous acte »* | **TRAITÉE — devient une règle**, ci-dessous |
| **`A-4`** | la fenêtre muette de `EI-8` a couvert **bien plus** que les douze secondes exigées ; écart **favorable**, signalé pour exactitude | **TRAITÉE — devient une règle**, ci-dessous |
| **`A-5`** | redémarrage machine, **instance non attribuée** | **TRAITÉE — précondition dure `P-A5`**, §6.1 |

> **Règle `A-2` — aucun constat d'absence par filtrage auto-correspondant.**
>
> `PR-1` exige de constater *« **aucun processus du superviseur vivant** »*
> — `W4-C` §16.1. Ce constat passe par un filtrage de la table des processus, et
> **un filtrage naïf se compte lui-même**, y compris par son **libellé
> d'affichage**.
>
> **Clause.** Tout constat d'absence portant sur la table des processus **MUST**
> être établi sur un **instantané figé, analysé hors ligne**, avec **motif
> témoin** — la méthode même qui a redressé `A-2`. Un filtrage exécuté en direct
> **MUST NOT** fonder un constat d'absence.
>
> **Le piège s'est présenté deux fois** : `G2-C` §6 range `A-2` dans la **même
> famille** que le `pgrep` auto-correspondant de `P-4`. **Une règle vaut mieux
> qu'une vigilance.**

> **Règle `A-3` — aucun polissage sous acte.**
>
> **Clause.** Pendant la fenêtre de `G.3`, **aucune correction cosmétique** —
> commentaire, mise en forme, nommage — **MUST NOT** être entreprise sur un
> fichier de l'installation. Ce qui est constaté obsolète est **consigné**, et
> corrigé **hors campagne**.
>
> La conduite tenue sous `G.2` était **juste** ; elle devient une **règle**.

> **Règle `A-4` — la fenêtre muette se rapporte telle qu'elle a été.**
>
> **Clause.** L'étendue **réelle** de la fenêtre de `EI-8` **MUST** être
> rapportée, et **MUST NOT** être présentée comme valant exactement douze
> secondes lorsqu'elle a couvert davantage.
>
> **Un écart favorable reste un écart**, et l'exactitude du rapport ne se négocie
> pas contre le sens de l'écart.

---

## 7. Préconditions de la campagne

Reprises de `G2-P` §14, **avec l'état réel du jour** et les **trois**
préconditions propres à `G.3` — `P-A5`, `P-A1`, `P-SPT`.

| # | Précondition | État |
|---|---|---|
| **`P-1`** | Boilerack **déployé** et fonctionnel en lecture, unité **arrêtée** jusqu'au temps 8 | **acquise en fait** — `G2-C` §6 ; **à constater**, non à accomplir — §6.3 |
| **`P-2`** | pont historique et superviseur dans leur **état nominal avant l'acte** | à établir le jour |
| **`P-3`** | **rollback disponible** — arrêter et retirer `<unité-boilerack>` sans dépendre de Boilerack | éprouvé sous `G.2` ; **à reconstater** |
| **`P-4`** | **procédure de remise en marche** du pont et du superviseur, écrite et **éprouvée avant le temps 2**, couvrant les **cinq étapes** | éprouvée sous `G.2` ; **à reconstater** |
| **`P-5`** | **inventaire des unités inscriptibles** dressé et vérifié — condition de `EI-8` | à dresser le jour |
| **`P-6`** | **trace côté broker** disponible et lisible — condition de `EI-12` | à établir le jour |
| **`P-7`** | **consommateur aval** disponible pour observer la télémétrie — condition du fait **C** | à établir le jour |
| **`P-8`** | exploitant **physiquement présent**, plan de reprise physique connu | déclaration |
| **`P-9`** | **autorisation humaine explicite et distincte**, nommant **`G.3`**, **disant si la restauration de la valeur est pré-décidée**, **portant la levée ponctuelle du `w4f` §11.2**, et **portant l'extension d'usage du puits de preuve — le réarmement pour `G.3`** | **NON DONNÉE** — §13 |
| **`P-10`** | le présent document **audité et intégré** | **non acquise** |
| **`P-11`** | les treize preuves `EI` établies, dans l'ordre du protocole | à établir le jour — §6.4 |
| **`P-A5`** | **branche prononcée** sur l'attribution de l'instance du redémarrage machine au mécanisme `F-12` — **(a) `INSTANCE ATTRIBUÉE`** ou **(b) `INSTANCE NON ATTRIBUABLE`** | **NON PRONONCÉE — BLOQUANTE** ; la branche **(b)** interdit l'exécution — §6.1 |
| **`P-A1`** | **procédure de capture en écriture unique** en place, compteur d'`ACK` armé | **à mettre en place avant la campagne** — §6.2 |
| **`P-SPT`** | **réarmement du puits PRÉPARÉ, non accompli** : procédure écrite, et capture *« avant »* prise **avant le temps 1**, **montrant la variable ABSENTE** | **à faire** — §6.5. **La variable MUST NOT être reposée au titre de cette précondition** : ce geste est l'**acte 1 bis du temps 8**, postérieur à `P-9` |

> **Aucune précondition n'est facultative.** L'échec de l'une quelconque
> **interdit d'engager la campagne.** C'est pourquoi **rien de non bloquant ne
> figure dans ce tableau** : la V2 y avait porté `P-R`, qualifiée dans le même
> mouvement de *« non bloquante »*. **La contradiction est levée** — `R-2` à
> `R-6` relèvent d'une **obligation de rapport**, au §6.6 (ii), et non d'une
> précondition.

---

## 8. Protocole — repris de `G2-P`, sans allègement

> **Clause de reprise.** `G.3` adopte **intégralement et sans retrait** les
> sections suivantes de `G2-P`, qui demeurent en vigueur comme texte technique
> indépendamment de l'extinction de la dérogation de son §3 :
>
> | Section reprise | Objet |
> |---|---|
> | **§7** | les treize preuves `EI-1..EI-13`, chacune avec sa source |
> | **§8** | la preuve *one-writer* — trois constats cumulatifs, fenêtre muette de **12 s** — et ses limites : `H2` et `H6` **(b)** demeurent **OUVERTES** |
> | **§9**, temps **1** à **14** | le déroulé, dans cet ordre, y compris les trois actes du temps 8 — **auxquels le §6.5 insère l'acte 1 bis**, le réarmement du puits, **sans en déplacer aucun** |
> | **§9.1** | la forme de l'invocation, **seule forme caractérisée** |
> | **§10** | la conduite de restauration de la valeur, et la clause propre : **aucune restauration après `ABORT`** |
> | **§11.1** | l'extinction de l'autorité — trois actes, **avant** toute restauration du pont |
> | **§11.2** et **§11.2.1** | les **cinq étapes** de `W4-C` §13, les **trois faits distincts** `A`/`B`/`C`, la transposition de l'étape 1 |
> | **§11.3** | la garde anti-reboot — **`G-a` ET `G-b` cumulées** |
> | **§12** | le référentiel `ABORT` — `FA-1..FA-12` et `AB-1..AB-9`, la transposition de `AB-1`, le **prédicat unique de `V_attendue`**, la conduite d'abandon et `T_release` |
> | **§13** | le bornage opposable |
>
> **Toute divergence entre le présent document et une section reprise est une
> erreur du présent document**, sauf là où il énonce explicitement un ajout —
> §6, §9 et §10.

**Cardinalité, inchangée et opposable** : **une** écriture au temps 10, **au plus
une** au temps 12, **zéro** partout ailleurs. Les lectures des temps 4, 6, 9, 11
et de l'étape 1 n'entrent pas dans ce décompte.

> **La campagne n'est close qu'après l'étape 5**, `W4-C` §13 l'exigeant en toutes
> lettres. Un rapport produit avant cette étape décrit une campagne **non close**.

---

## 9. Preuves de sortie, et verdict

> **Clause de reprise.** `G.3` reprend les **dix preuves de sortie du `G2-P`
> §16, intégralement et sans allègement**, en substituant `G.3` à `G.2` partout
> où la campagne y est nommée.

| # | Preuve exigée — `G2-P` §16 |
|---|---|
| **1** | les **treize preuves `EI-1..EI-13`**, chacune avec sa **méthode**, sa sortie et son **horodatage** — *« une assertion d'arrêt ne vaut donc rien sans sa méthode »*, `W4-C` §9.1 |
| **2** | pour **`EI-8`** : la fenêtre horodatée, l'état **arrêté** de `<unité-boilerack>` sur cette fenêtre, et l'extrait de journal montrant **aucune ouverture** — **sans revendication d'attribution**. Son étendue réelle est rapportée telle qu'elle a été — règle `A-4`, §6.6 |
| **3** | les **lectures horodatées** : les **deux captures nues** du temps 6, **texte et `-J`**, avec `V_brut` et `V_canon` · la garde de fraîcheur en `-J` (temps 9) · la relecture de confirmation (temps 11) · la relecture de restauration si elle a eu lieu · la **lecture nue de l'étape 1** |
| **4** | l'écriture, avec sa **ligne d'invocation réelle**, son **`stdout` et son `stderr` intégralement et SÉPARÉMENT**, son **code retour** et sa **durée mesurée** — `W4-A` §19, champs 2 à 5 |
| **5** | l'**`ACK` publié**, et sa **confrontation à l'observation directe** — `FA-10` |
| **6** | les preuves d'**ouverture réelle** de l'autorité — contenu **persisté**, démarrage manuel de l'unité, **trace côté broker** de la souscription — et d'**extinction** — contenu persisté, arrêt de l'unité, **libération de la liaison** |
| **7** | les preuves de **restauration**, **les cinq étapes nommées séparément**, dont les **trois faits distincts** de l'étape 3 — **A** unité active, **B** cadence de connexions repartie, **C** télémétrie observée **depuis un consommateur aval** — et l'**étape 5** |
| **8** | `PR-1` et `PR-2` **redoublées** — comment l'arrêt a été établi, **et comment la reprise l'a été** |
| **9** | l'état de **`G-a`** et **`G-b`** sur toute la fenêtre, **`G-a` reconstatée après le démarrage manuel** du temps 8 |
| **10** | le **verdict**, avec le critère `FA` ou `AB` déclencheur — §9.1 |

**Cinq preuves s'y ajoutent, propres à `G.3` :**

| # | Preuve | Renvoi |
|---|---|---|
| **11** | la **branche de `P-A5` prononcée** — **(a)** avec ce qui a établi l'attribution de l'instance au mécanisme `F-12`, ou **(b)** avec ce qui l'a rendue impossible | §6.1 |
| **12** | les **trois captures d'environnement** du puits de preuve — *« avant »*, *« pendant »*, *« après »* — et la **preuve du retrait** de la variable persistée | §6.5 |
| **13** | l'**atelier complet**, avec le **compteur d'`ACK` continu**, tout `ACK` **rejeté** déposé comme les autres, et **toute capture manquante déclarée** | §6.2 |
| **14** | le **volume final de l'atelier**, fichier par fichier — **observable, non borné** | §6.5.1, réserve 2 |
| **15** | les **instants d'horloge** du retour de l'invocation d'écriture et du **début de la relecture** du temps 11, rendant **lisible** le décalage introduit par le dépôt — **sans le borner** | §6.5.1, réserve 3 |

> **La preuve n°4 dépend du puits.** Sans réarmement, la signature de
> l'invocation n'est pas déposée automatiquement, et la preuve n°4 retomberait
> sur une capture manuelle — c'est-à-dire sur ce que `A-1` a précisément fait
> échouer. **Ni `P-SPT` ni l'acte 1 bis ne sont donc un confort.**
>
> **Et l'ordre est opposable** : `P-SPT` **prépare** et capture l'état
> *« avant »*, variable **absente** ; l'**acte 1 bis du temps 8** repose la
> variable, **après** que `P-9` a porté nommément l'extension — §6.5.

### 9.1 Le verdict

> **Clause — deux verdicts, exclusifs, et aucun par défaut.**
>
> | Verdict | Conditions, **cumulatives** |
> |---|---|
> | **`G.3 CONFIRMÉ`** | les **quinze** preuves ci-dessus sont produites · **aucun** critère `FA-1..FA-12` ni `AB-1..AB-9` n'a été déclenché · l'écriture du temps 10 a été **exécutée et confirmée par relecture stricte** · l'autorité d'écriture est **éteinte et prouvée éteinte** · la restauration est prouvée par les **cinq étapes**, **étape 5 comprise** |
> | **`G.3 ABORT`** | un critère `FA` ou `AB` a été déclenché. Le verdict **MUST nommer lequel**, et la **conduite d'abandon** du `G2-P` §12.3 s'applique intégralement — ne pas écrire, éteindre, rétablir les cinq étapes, **puis** rapporter |
>
> **Aucun verdict par silence, aucun verdict par défaut, aucun verdict partiel.**
> Une campagne interrompue sans verdict prononcé est **non close**.
>
> **La campagne n'est close qu'après l'étape 5** — `W4-C` §13. Un rapport produit
> avant elle décrit une campagne **non close**, quel que soit le verdict qu'il
> porte.

> **Un `STOP AVANT AUTORISATION` n'est ni l'un ni l'autre.** Prononcé au titre de
> la branche **(b)** de `P-A5`, il constate que **la campagne n'a pas commencé** :
> aucun verdict de campagne n'est dû, et il **MUST NOT** être rapporté comme un
> `ABORT`.

---

## 10. Ce que `G.3` ajoute au référentiel `ABORT`

`FA-1..FA-12` et `AB-1..AB-9` sont repris **intégralement**. Rien n'est retiré,
rien n'est adouci. Deux points sont **précisés**, et ils ne créent aucun critère
nouveau :

| Point | Précision |
|---|---|
| **`FA-8` / `AB-5`** — redémarrage inattendu de la machine | demeurent des abandons **quelle qu'en soit la cause**. **`P-A5` ne les remplace pas** : elle réduit l'imprévisibilité en amont, elle ne dispense d'aucun critère en fenêtre |
| **`FA-10`** — `ACK` incohérent avec l'observation directe | la confrontation exige une **capture de l'`ACK`**. Sous la clause du §6.2, un `ACK` **non capturé** rend `FA-10` invérifiable : la capture manquante **MUST** être déclarée, et l'exploitant conduit alors `AB-6` — doute — plutôt que de conclure |

> **Aucun critère `FA` ou `AB` n'est créé par `G.3`.** En créer un modifierait le
> référentiel d'une campagne d'écriture sans que rien ne l'exige.

---

## 11. Ce que `G.3` lève, et ce qu'il ne lève pas

> **Ce tableau et le §13 disent la MÊME chose.** Tout ce qui est levé ici
> **MUST** être nommé par l'autorisation humaine ; rien de ce qui n'y figure pas
> ne l'est. La V2 en omettait deux, et le §13 les portait déjà : **l'écart est
> corrigé ici.**

**Ce que `G.3` lèverait, une fois — la liste est close :**

| # | Objet levé | Fondement | Nommé au §13 |
|---|---|---|---|
| **1** | une **écriture réelle**, sur un **rôle unique** et une **valeur unique** | acte réservé **1** — §4 | item 4 |
| **2** | l'**ouverture temporaire** de `[transaction_surface].enabled`, effective au temps 8, éteinte au temps 13 | acte réservé **2** — §4 | item 4 |
| **3** | la **neutralisation temporaire** du dispositif historique, bornée à `PR-1`, `PR-2` et `EI-8`, suivie de la restauration en **cinq étapes** | acte réservé **3** — §4 | item 4 |
| **4** | **au plus une seconde écriture** — la restauration de la valeur —, dans le **seul cas nominal** et sur décision humaine **pré-décidée** | `G2-P` §10, cas 2 | item 3 |
| **5** | **quatre gestes sur `<unité-boilerack>`** — arrêter (t. 5), **démarrer à la main** (t. 8), arrêter (t. 13), **retirer** au rollback `P-3` | **levée ponctuelle du `w4f` §11.2** — §6.3 | item 5 |
| **6** | le **réarmement temporaire du puits de preuve transport** pour la durée de `G.3` | **extension nominale** du `SPT` §5.4 et de la condition 2 de `W4-A` §17 — §6.5. **Subordonnée à l'autorisation, comme l'objet 5** | item 7 |

> **Les objets 5 et 6 manquaient à la V2**, alors que le §6.3 et le §6.5 les
> créaient et que le §13 les faisait nommer. **La portée est désormais alignée
> sur l'autorisation**, et l'objet 6 **sort** du tableau ci-dessous, où la V2
> l'avait rangé à tort.

**Ce que `G.3` ne lève pas :**

| Objet | État |
|---|---|
| bascule de souveraineté | **interdite** — `w4f` §11.1 acte 4 |
| toute écriture sur un **second rôle** | **interdite** — §5 |
| toute commande **ECS** | **interdite** — absente du profil |
| toute **modification** du pont, du superviseur ou de leurs unités | **interdite** — seuls l'arrêt et la remise en marche sont admis |
| toute **activation au démarrage** de `<unité-boilerack>` | **interdite** — `G-a` |
| toute **instrumentation NOUVELLE**, en particulier vers `U-3` | **hors périmètre.** Le réarmement du §6.5 n'en est pas une : le puits est **déjà implémenté**, et son **autorisation d'usage** est étendue — **aucun dispositif n'est créé** |
| toute **exploitation de `<unité-boilerack>` hors des quatre gestes** — fonctionnement en lecture seule, mesure de coexistence ou de contention | **NON LEVÉE** — le `w4f` §11.2 n'est levé que pour les **quatre gestes** du §6.3, et son **statut général demeure `NON DONNÉE`** |
| tout **usage du puits hors de la campagne `G.3`** | **NON LEVÉ** — l'extension du §6.5 est **nominale** et **s'éteint** avec `G.3` |
| toute **campagne ultérieure** | **interdite** — §4, extinction ; et **aucune ne s'autorise de l'extension du puits** — §6.5 |
| **rendre le journal système persistant** | **hors périmètre** — §6.1 ; exige son propre lot |
| `W4-F3`, `W4-F4`, `W4-F5` | **non ouverts** |
| `T0`, `T1`, `T2` | **non ouverts** |
| `C1`, la coexistence, `W4-P`, `W4-Q` | **non touchés** — §12 |
| autorité permanente d'écriture | **aucune n'est créée** |

> **Le pont historique demeure l'unique écrivain réel de production**, hors la
> fenêtre de `G.3`, pendant laquelle il est **arrêté** et où **personne d'autre
> que Boilerack n'écrit**, au sens borné de `G2-P` §8.1.

---

## 12. `C1`, la coexistence, `W4-P`, `W4-Q` — non touchés

Repris de `G2-P` §4.2, dont le raisonnement est **inchangé** : `PR-1` neutralise
le superviseur, `PR-2` arrête le pont, et `EI-8` exige une fenêtre sans aucune
ouverture de connexion.

> **Pendant `G.3`, il n'y a plus de sonde du superviseur à protéger.** Le budget
> de 5 s n'est pas *tenu* : il est **sans objet**, faute de sonde pour le
> consommer.

**`C1` demeure en vigueur, non satisfaite, non violée, et non applicable à la
fenêtre de `G.3`.**

> **Clause.** `G.3` **MUST NOT** être invoqué pour affirmer que `C1` serait
> satisfaite, calculable, ou dispensable ailleurs. Hors la fenêtre où les
> préconditions et `EI-8` sont établies, `C1` reprend pleinement son empire.

| Objet | État, **inchangé** |
|---|---|
| **`C1`** | **non satisfaite, non calculable** |
| **`U-1`, `U-2`, `U-3`, `U-7`** | **ouvertes** — `G.3` ne les réduit pas |
| **`H1`, `H2`, `H3`, `H6`** | **ouvertes** — `H2` et `H6` **(b)** en particulier |
| **Coexistence** | **NON QUALIFIÉE** ; `W4-F2` reste **`NON QUALIFIABLE`** hors exception |
| **Critère du `w4f` §10.3.3** | **matériellement absent**, à produire par `W4-P` |
| **`W4-P`** | **ouvert**, non touché |
| **`W4-Q`** | **ouvert et bloqué** par le verrou du `w4f` §10.7, non touché |
| **`T0`** | **NON AUTORISÉ** |

> **`AB-4` conserve son office** : une invocation dépassant nettement le budget
> de 5 s connu est un abandon, que le superviseur soit neutralisé ou non.

---

## 13. L'autorisation — ce qui est demandé, et ce qui ne l'est pas

> **Le présent document ne demande AUCUNE exécution.** Il demande un **audit
> indépendant**, puis — si l'humain le décide — une **autorisation**.

> **La liste close de ce qui est levé est au §11**, et les deux disent la même
> chose : **rien n'est levé qui ne soit nommé ici, et rien n'est nommé ici qui ne
> figure au §11.**

**L'autorisation, si elle est donnée, MUST :**

| # | |
|---|---|
| **1** | être **explicite, distincte et postérieure à l'audit** du présent document |
| **2** | **nommer `G.3`** |
| **3** | **dire si la restauration de la valeur est pré-décidée** — `G2-P` §10, cas 2 : *« décision humaine, pas automatisme »* |
| **4** | ne porter que sur les actes réservés **1**, **2** et **3**, **une fois** |
| **5** | **porter nommément la levée ponctuelle du `w4f` §11.2** — les **quatre gestes** sur `<unité-boilerack>` et **leurs temps**, et rien d'autre — §6.3 |
| **6** | **constater la branche prononcée de `P-A5`** : sur **(a)**, elle peut être donnée ; sur **(b)**, elle **MUST** être refusée — §6.1 |
| **7** | **porter nommément l'extension d'usage du puits de preuve transport** — le réarmement, borné à `G.3`. **Sans cette mention, l'extension n'existe pas** et le puits demeure borné à `G.2` — §6.5 |

**Elle MUST NOT :**

- être déduite de l'audit ou de l'intégration du présent document ;
- se réclamer, en tout ou partie, de **l'autorisation consommée de `G.2`** ;
- valoir autorisation de l'acte réservé **4** ;
- valoir autorisation **générale** du `w4f` §11.2 — au-delà des quatre gestes
  bornés du §6.3 —, ni en dispenser, ni requalifier son statut ;
- valoir autorisation d'une campagne **ultérieure**, ni d'un usage ultérieur du
  puits de preuve ;
- être donnée tant que `P-A5` n'a pas été **prononcée**.

---

## 14. Ce que `G.3` établira, et rien de plus

> **La borne est fixée AVANT le terrain, et elle est opposable.**
>
> `G.3` établira que **Boilerack a émis une seconde écriture réelle**, confirmée
> par relecture stricte, **dispositif historique arrêté**, et *one-writer*
> établi **au sens borné de `G2-P` §8.1** — clients du démon, sur douze secondes.
>
> Il **n'établira pas** : que la coexistence est qualifiée · que `C1` est
> satisfaite ou calculable · que Boilerack peut écrire **en coexistence** · qu'un
> régime d'écriture **soutenu** existe — *« deux écritures espacées ne
> caractérisent aucun régime soutenu »*, `G2-C` §2.1 · que `H2`, `H6` **(b)**,
> `U-2`, `U-3` ou `U-7` seraient closes · qu'une souveraineté serait acquise,
> préparée ou rendue plus proche.

**Ce qu'une seconde campagne apporte, dit exactement :**

| Apport | Portée |
|---|---|
| **répétabilité de la chaîne** | une chaîne qui fonctionne **deux fois** n'est plus un coup unique. **Ce n'est pas un régime soutenu** |
| **seconde occasion d'observer `I-7`, `I-10`, `I-11`** | `w4f` §12.2 : ces inconnues *« MUST NOT être levées par raisonnement documentaire »*. `G.3` en offre une observation de plus — **il ne les clôt pas** |
| **vérification des corrections `A-1` et `A-5`** | l'atelier complet et la cause connue sont eux-mêmes des sorties de la campagne |

---

## 15. Ce que ce document ne fait pas

Il n'exécute rien · **il n'autorise aucune exécution** · il ne conduit aucun
terrain · il ne déploie rien · il ne touche ni la chaudière, ni le Pi, ni le
pont, ni le superviseur, ni `vcontrold` · il n'ouvre ni `W4-F3`, ni `W4-F4`, ni
`W4-F5`, ni `T0` / `T1` / `T2` · il ne requalifie pas `W4-F2` · il n'amende ni
`C1`, ni `C2`, ni `C3` · **il ne touche ni `W4-P`, ni `W4-Q`, ni le critère du
`w4f` §10.3.3** · il ne déclare aucun second rôle · **il ne demande aucune
modification de code** · il ne demande **aucune instrumentation nouvelle** — le
réarmement du §6.5 étend l'usage d'un puits **déjà implémenté**, il n'en crée
aucun · il **ne requalifie pas le statut général** de l'autorisation du
`w4f` §11.2, qu'il lève **ponctuellement et pour quatre gestes seulement** · il
ne statue pas sur la **dissymétrie** du déploiement de fait · il ne modifie pas
l'index du corpus.

Il crée une exception bornée, l'enferme, et s'arrête là.

---

## 16. Réserves conservées

**L'inventaire complet des réserves de `G2-C` §6 — les dix-neuf — est au §6.6**,
avec le sort de chacune. Il n'est pas répété ici. S'y ajoutent les réserves
propres au présent cadrage :

1. **`P-A5` peut ne jamais être prononçable en branche (a).** La trace du boot
   précédant le redémarrage de `G.2` **est perdue**, et aucune voie prospective
   n'attribuera **cette** instance. Si l'attribution échoue, **`G.3` ne
   s'exécutera pas** — branche **(b)**. C'est une **issue légitime** du présent
   cadrage, et non un échec à contourner.
2. **La dissymétrie du déploiement de fait demeure ouverte** (§6.3). `G.3` lève
   le `w4f` §11.2 **ponctuellement**, pour quatre gestes ; il laisse **entier**
   ce qui relève de la gouvernance.
3. **La correction `A-1` est de procédure, donc non auto-appliquée.** Aucun
   mécanisme n'empêche un opérateur de réutiliser un nom de fichier. La règle est
   **opposable par constat sur l'atelier**, elle n'est pas imposée par le
   système — même nature que `SPT` §5.4 sur l'extinction déclarative. **Les
   règles `A-2`, `A-3` et `A-4` du §6.6 sont de la même nature.**
4. **Une seconde exception affaiblit l'argument de l'exception.** Un auditeur peut
   légitimement juger que deux dérogations successives au séquencement du
   `w4f` §11.1 dessinent une pratique plutôt qu'une exception. **Le §4.1 le dit
   sans l'adoucir** : aucune règle de reconduction n'est créée, et une troisième
   exigerait un troisième document et une troisième autorisation. **La réserve
   est conservée, non réfutée.**
5. **L'interruption de service est réelle** — bornée, réversible, non nulle, et
   elle se reproduira intégralement.
6. **Le bornage demeure opposable, non auto-appliqué.** `W4-A` §20 : aucun
   mécanisme *one-writer* n'existe. Rien dans le code n'empêche une écriture hors
   campagne ; c'est la discipline qui l'empêche.
7. **`R-2` à `R-6` sont conservées sans que le présent document en connaisse le
   texte** (§6.6 ii). Leur identification aux réserves du `SPT` §10 est
   **écartée sur pièces** ; leur source est **l'audit d'implémentation de la
   PR #81**. Elles restent **non bloquantes**, et ce qui est dû est une
   **obligation de rapport**, non une précondition. **Une réserve dont le rapport
   ne peut rien dire est citée, non conservée** — et cela est dit plutôt que
   masqué.
8. **Les six réserves du `SPT` §10 sont reprises et aucune n'est levée**
   (§6.5.1). Deux pèsent réellement : le **volume de l'atelier est non borné**,
   et **l'I/O du puits est hors budget, invisible dans `duration_s`, et décale la
   relecture**. **Aucun critère du référentiel ne les couvre** — ni `AB-4`, ni
   `AB-7`, ni `I-7` —, et `G.3` **les rend observables sans les borner**.
9. **La réserve 1 du `SPT` §10 vise le présent document.** Elle prévoyait *« une
   brèche que la **prochaine campagne** élargira »* : `G.3` **est** cette
   prochaine campagne. L'extension du §6.5 est nominale et fermée aux deux
   extrémités — **la réserve n'en est pas réfutée**.
10. **La réserve 6 du `SPT` §10 nomme une campagne du 27 août 2026 comme NON
    CLOSE.** `G.3` **ne la touche pas, ne l'interprète pas, et ne statue pas**
    sur elle. Elle est conservée pour n'être pas perdue par omission.

---

## 17. Précédent invoqué

`G.1` — `w4f2-g1-constat.md` — a établi la forme : un acte **borné**, **proposé
par un document, non autorisé par lui**, puis autorisé par une **décision humaine
explicite et distincte**, exécuté sans élargissement, et consigné par un document
séparé. `G.2` l'a reprise en y ajoutant l'écriture, l'amendement de séquencement,
et les preuves d'ouverture, d'extinction et de restauration en cinq étapes.

`G.3` reprend la forme de `G.2` **sans allègement**, et lui ajoute **six
corrections** tirées de ses propres réserves — §6. **Elle ne lui emprunte pas son
autorisation**, et elle ne la rend pas de nouveau disponible — §4.1.

---

## 18. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture et cadrage de `G.3`, régime successeur de `G.2`. Clause d'exception propre — actes réservés 1, 2, 3, une fois ; acte 4 interdit. Rôle maintenu, examen de l'alternative rendu. Quatre corrections : `A-5` en précondition dure et bloquante, `A-1` en dépôt à écriture unique, dissymétrie `w4f` §11.2 statuée pour `G.3` et laissée entière au-delà, réétablissement terrain complet le jour de l'acte. Protocole de `G2-P` repris sans allègement. Aucun terrain, aucune exécution, aucune autorisation. |
| **2** | Après audit. Six blocages fermés, sans terrain. `B1` : **`P-A5` reformulée sur le reliquat réel** — le mécanisme `F-12` est **établi** en configuration déclarée ; ce qui manque est l'**attribution de l'instance** en exécution observée. Deux branches, dont **(b) bloque** `G.3`. `B2` : **le puits de preuve transport était supposé disponible et ne l'est pas** — `SPT` §5.4 le borne à `G.2` *« et aucune autre »*, `G2-C` §7 le déclare désarmé ; clause de **réarmement borné à `G.3`**, précondition `P-SPT`, **retrait prouvé en sortie**, aucune autre campagne ne s'en autorise. `B3` : **preuves de sortie ajoutées** — `G2-P` §16 repris sans allègement, trois preuves propres, et verdicts **`G.3 CONFIRMÉ`** / **`G.3 ABORT`** définis. `B4` : **la V1 se trompait sur le `w4f` §11.2** — démarrer, arrêter et retirer l'unité ne figurent dans **aucun** des quatre actes réservés ; **levée ponctuelle et bornée** pour quatre gestes, **statut général inchangé**. `B5` : **les dix-neuf réserves de `G2-C` §6 inventoriées**, `A-2`, `A-3` et `A-4` devenues des **règles**, et le fait que le contenu de `R-2` à `R-6` **ne soit pas dans le dépôt** constaté avec la précondition `P-R`. `B6` : **le §4.1 rouvrait `G.2` par sa rédaction** — réécrit : `G.2` exception **passée, consommée, non réutilisable** ; `G.3` **seule exception ouverte**. **Aucun terrain, aucune exécution, aucune autorisation.** |
| **3** | Après réaudit. Quatre blocages résiduels fermés, sans terrain. `C1` : **l'extension du puits ne visait qu'une clause** ; elle devient **nominale** et vise les **deux clauses opposables** — la condition 2 portée dans `W4-A` §17 et le `SPT` §5.4 —, cite l'encadré du `SPT` §8 sans l'entamer, **ne rend pas `G.2` réutilisable**, et **ferme toute campagne postérieure à `G.3`**. `C2` : **les six réserves du `SPT` §10 reprises une par une** — la **2** (volume d'atelier non borné) et la **3** (I/O hors `write_timeout_s`, invisible dans `duration_s`, décalant la relecture) traitées, avec le constat exprès que **ni `AB-4`, ni `AB-7`, ni `I-7` ne les couvrent** ; deux preuves de sortie ajoutées, **observables et non bornantes**. `C3` : l'identification de `R-2`…`R-6` aux réserves 2 à 6 du `SPT` §10 est **instruite sur pièces et ÉCARTÉE** — la PR #81 porte ses propres `R-*` et `R-1` y est un contrat de code ; **aucune assertion d'absence n'est conservée** ; `P-R` **sort du tableau des préconditions** et devient une **obligation de rapport**, la contradiction « obligatoire et non bloquante » étant levée. `C4` : la **portée** est alignée sur le §13 — la levée ponctuelle du `w4f` §11.2 et le réarmement du puits **entrent** dans *« ce que `G.3` lève »*, le second **sort** de *« ce qu'il ne lève pas »*, et trois lignes de non-levée sont précisées. **Aucun terrain, aucune exécution, aucune autorisation.** |
| **4** | Après réaudit. Un blocage résiduel fermé, sans terrain. `C5` : **l'extension du puits n'était subordonnée à rien** — rédigée à l'indicatif, elle devenait opposable par la **seule intégration du document**, là où la levée du `w4f` §11.2 exige d'être *« comprise dans l'autorisation humaine et portée nommément par elle »*. L'asymétrie est supprimée : **subordination dans les mêmes termes** au §6.5 ; `P-9` porte désormais l'extension ; le **§13 item 7** exige la mention nominale et dit ce qu'emporte son absence ; et surtout, **le geste de réarmement cesse d'être une précondition pour devenir l'acte 1 bis du temps 8** — donc **structurellement postérieur à l'autorisation**. `P-SPT` est ramenée à la **préparation** et à la capture *« avant »*, qui exige la variable **ABSENTE** et vaut elle-même verrou. Les trois actes du `G2-P` §9, temps 8, demeurent inchangés dans leur contenu et leur ordre relatif. **Aucune nouvelle levée, aucune autorité générale, aucune réutilisation hors `G.3`. Aucun terrain, aucune exécution, aucune autorisation.** |
