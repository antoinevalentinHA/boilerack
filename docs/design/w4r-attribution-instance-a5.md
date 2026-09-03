# `W4-R` — lot borné en lecture stricte : attribution de l'instance `A-5`

> **Version 11 — après réaudit.** Aucun terrain. **`P-A5` demeure
> `NON PRONONCÉE`. `P-9` demeure `NON DONNÉE`. `G3` demeure fermé.**
>
> | | Correction |
> |---|---|
> | **V11 · 1** | **La liste `MUST` du §10 portait un test PLUS FAIBLE que le §14.1** : *« postérieure à l'audit »* au lieu de *« postérieure aux deux »*, et *« nommer `W4-R` »* sans sa **version**, sans **audit du delta**, sans **intégration**, sans **rejeu unique**. Elle porte désormais **les QUATRE conditions, mot pour mot**, et conserve ses exigences de périmètre |
> | **V11 · 2** | **La formule *« et à aucune autre »* neutralisait les garde-fous complémentaires.** Elle est **supprimée partout**. Les quatre conditions sont désormais le **NOYAU COMMUN**, et **les `MUST` comme les `MUST NOT` du §10 demeurent pleinement opposables** |
> | **V11 · 3** | **Le §14.1 citait le §8 entre guillemets dans une rédaction qu'il ne porte plus.** La **fausse citation est retirée** ; le renvoi vise le **texte actuel** du §8, sans guillemets, et **aucun retour à un test « autorisation humaine nouvelle » seul** n'est possible |
>
> **Version 10 — après réaudit du correctif de rejeu.** Aucun terrain.
>
> | | Correction |
> |---|---|
> | **V10 · B1-B4** | **Le traitement de `/var/log/wtmp.db` était incohérent.** L'objet de `L5` le couvre désormais **explicitement**, aux côtés de `/var/log/wtmp` et de ses rotations. **Aucun quatrième lecteur n'est inventé** : les trois du §5.3 demeurent seuls licites. **Deux régimes de validation sont séparés** — conteneur plat et base de données —, les critères **`a`** et **`b`** cessant d'être opposés à une base pour laquelle ils n'ont pas de sens. À défaut de lecteur licite, l'objet est **constaté PRÉSENT mais INEXPLOITABLE sous ce lot**, sans improvisation. Le §11 rend désormais ses sorties **PAR OBJET** |
> | **V10 · B5-B6** | **Le §14 se contredisait.** Il déclarait les deux prononcés sans effet **et** renvoyait leur portée à un arbitrage. Les deux prononcés sont **SANS EFFET**, **`P-A5` demeure `NON PRONONCÉE`**, et **aucune « portée à arbitrer » ne subsiste**. Les blocs périmés et dupliqués sont **fusionnés ou supprimés**, et les renvois de rejeu pointent le **§14.1** |
> | **V10 · B7-B8** | **Trois sections portaient trois tests d'admissibilité divergents.** Le **§8**, le **§10** et le **§14.1** énoncent désormais les **MÊMES quatre conditions cumulatives**, et consignent que **les DEUX autorisations du 2026-09-03 sont consommées** |
> | **V10 · B9** | **Le §6.3 avait été inséré au milieu du §6.2**, coupant deux clauses qui lui appartiennent. Il est **replacé après la fin réelle du §6.2** ; les clauses **« rang 7 »** et **« `A₁` non établi rend sans objet »** **demeurent dans le §6.2** |
>
> **Version 9 — lot CORRECTIF de REJEU, après la seconde exécution non close.**
> Aucun terrain.
>
> **Deux exécutions sont désormais NON CLOSES**, et le §14 les consigne l'une et
> l'autre. Le présent lot corrige **uniquement** les défauts qu'elles ont
> révélés.
>
> | | Correction |
> |---|---|
> | **V9 · C1** | **`/var/log/wtmp.db` entre dans le périmètre licite de `L5`**, sous la **même discipline** que les autres sources : **présence constatée**, **lecture seulement si le lot la prévoit**, **aucune extrapolation**. La seconde exécution l'a découvert et **s'est correctement abstenue** de le lire, faute d'un acte le prévoyant — §5.3, §5 |
> | **V9 · C2** | **La clôture n'était pas verrouillée.** Le rang 13 est désormais **le dernier acte, sans exception** : empreintes finales, analyse hors ligne, prononcé. **La clôture n'existe qu'après le prononcé**, et **après elle : aucune lecture de l'hôte, aucune corroboration, aucun acte supplémentaire** — §6.2, §6.3 |
> | **V9 · C3** | **`RE-4` n'appelle AUCUNE corroboration.** Elle est satisfaite **par construction**, et **cela suffit**. Toute vérification sur l'hôte à son sujet est un **acte hors liste close** — c'est ce qui a rendu la seconde exécution non close — §9 |
> | **V9 · C4** | **Historique** : la **première** exécution demeure non close (`RA-1` sur `who -b`) ; la **seconde** l'est aussi, sur **`RA-1`**, **`RA-8`** et, **subsidiairement**, **`RA-6`**. **Aucun de leurs prononcés n'est retenu**, et **`P-A5` n'est réputée prononcée en aucune branche** — §14 |
> | **V9 · C5** | **Ce qu'un nouveau rejeu exigera** est énoncé : **audit du delta**, **intégration**, **autorisation humaine propre et nouvelle**, et **rejeu UNIQUE** — §14.1 |
>
> **Version 8 — lot CORRECTIF, après réaudit.** Aucun terrain.
> **L'autorisation demeure `NON DONNÉE`. L'exécution du 2026-09-03 demeure
> `NON CLOSE`. `P-A5` n'est pas prononcée. `G3` n'est pas rouvert.**
>
> | | Correction |
> |---|---|
> | **V8 · blocage 1** | **`T` n'avait aucune source.** Le §9.2 invoquait une *« période déclarée lue par `L8` »* que **`L8` ne lisait pas**, et la notion était **ambiguë** : un `.timer` peut porter `OnBootSec`, `OnUnitActiveSec`, `OnUnitInactiveSec` ou `OnCalendar`, **dont les sémantiques diffèrent**. `L8` est **étendu nommément** aux directives temporelles de `<timer-guard>`, sa colonne `Sert` propagée vers **`RE-5b`** et **`RA-3`**, et la **condition d'activation due** est définie **par mode** — §5, §9.2 |
> | **V8 · blocage 2** | **La V7 rendait à `L5` la capacité de porter des instants de démarrage**, que la V6 lui avait retirée : sa condition (ii) admettait *« des enregistrements persistants lus par `L5` portant la séquence des démarrages »*. **Contradiction interne.** La condition (ii) **repose désormais sur `L4` SEUL**, `L4` est propagé comme **porteur potentiel de `A₁`**, et **`L5` ne porte plus aucun instant de démarrage** — §7.1.0, §7.1 |
> | **V8 · non bloquant** | **La formule `Δ ≥ T` produisait un faux positif sur un `oneshot`.** Avec `OnUnitInactiveSec`, **l'échéance repart à la FIN de l'exécution** : l'intervalle vaut `durée d'exécution + OnUnitInactiveSec`, et **la durée n'est pas dans l'objet de `L2`**. La condition est réénoncée **par mode**, et si une activation due **n'est pas établissable**, **`RE-5b` MUST NOT certifier le cycle** et **`RA-3` MUST NOT se déclencher sur ce seul motif** — §9.2, §8 |
>
> **Version 7 — lot CORRECTIF, après réaudit.** Aucun terrain.
>
> | | Correction |
> |---|---|
> | **V7 · B1-a** | **Le constat (ii) de la V6 était TAUTOLOGIQUE** : l'instant candidat étant **dérivé** du temps de fonctionnement, vérifier que celui-ci le couvre ne pouvait pas échouer. **Il est retiré.** `L0` ne rend que le **dernier** démarrage ; `A₁` n'est acquis que si ce démarrage est **rattaché de façon UNIVOQUE** au redémarrage étudié, par une source de la liste close. **Le cas de plusieurs redémarrages dans le préflight est nommé** — §7.1.0 |
> | **V7 · B1-b** | Le §6.2, rang 7, écrivait que **`A₁` était « acquis au rang 2 »**. **Le rang 2 ne rend qu'un candidat** ; la fenêtre n'existe qu'après satisfaction de la clause d'identité |
> | **V7 · B2-a** | **La « séquence chronologique cohérente » est SUPPRIMÉE comme critère.** Les enregistrements `utmp` sont **mis à jour EN PLACE** : le conteneur **n'est pas ordonné chronologiquement**, et ce critère aurait **rejeté le format réel** — §5.3 |
> | **V7 · B2-b** | **Le choix entre tailles harmoniques était ambigu**, et c'est grave : `89 600` se divise par **400 et par 800**. Deux critères le lèvent — **couverture intégrale** de chaque enregistrement élémentaire, et **minimalité** : si un diviseur propre valide aussi, **c'est lui qui est retenu**. **Un parse qui sauterait un enregistrement sur deux MUST NOT être retenu**, et **aucun constat d'absence ne MAY être fondé sur un parse partiel** |
> | **V7 · B3** | **`RE-5b` certifiait « nominal » sans que le superviseur ait cyclé.** Pour un lot couvrant **au moins une période du timer**, un **changement POSITIF de l'identifiant d'invocation** est désormais exigé ; **s'il demeure inchangé alors qu'une activation devait avoir lieu, `RA-3` se déclenche**. Les autres protections sont conservées, et **aucune cadence complète n'est prétendue** — §8, §9 |
>
> **Version 6 — lot CORRECTIF, après réaudit.** Aucun terrain.
>
> | | Correction |
> |---|---|
> | **V6 · B1** | **La V5 laissait un démarrage ULTÉRIEUR devenir silencieusement `A₁`.** L'ancrage sur l'**événement historique** du préflight `G.2` est rétabli : `L0` ne fournit qu'un **instant CANDIDAT**, et une **clause d'identité** vérifie qu'il correspond bien au redémarrage étudié. **À défaut, `A₁` demeure NON ÉTABLI** — §7.1.0 |
> | **V6 · B2** | **Le motif témoin de la V5 était circulaire** : il exigeait un `BOOT_TIME` de `L0` pour valider un format dont l'objet peut n'en porter aucun. Le témoin **MAY désormais être d'un autre type** présent dans le même objet, et la **validation structurelle du format** est **séparée** du **constat d'absence de `BOOT_TIME`/`RUN_LVL`**. **Un parse structurellement valide établit cette absence sans exiger que ces types existent** — §5.3 |
> | **V6 · B3** | **`L2` ne produisait pas les propriétés que `RE` et `RA-3` exigeaient.** Elle est **étendue nommément** — `ActiveEnterTimestamp`, `ActiveState`, `SubState`, `Result` —, **`RE-5b` est reformulée pour être décidable avec les deux prises prévues**, et **la « cadence tenue » cesse d'être exigée** : deux relevés ponctuels ne l'établissent pas — §5, §9 |
> | **V6 · B4** | **Le bornage de l'exploitation avait disparu.** Une **règle positive** est réénoncée au §5 : l'exploitation de `L5` au soutien de la règle de décision demeure **bornée autour de la date du préflight `G.2`**, et la caractérisation du §5.3 n'est autorisée **que comme instrumentation nécessaire** — elle **ne lève pas** ce bornage |
> | **V6 · propagations** | **`S3`** ne porte plus l'instant, seulement le **caractère / `A₂`** · le **rang 4** nomme **`RE-2a`**, **`RE-2b`** et **`RE-2c`** parmi les preuves qu'il conditionne |
>
> **Version 5 — lot CORRECTIF, après audit d'homologation de l'exécution du
> 2026-09-03.** Aucun terrain.
>
> **L'exécution du 2026-09-03 est NON CLOSE** — `RA-1` atteint. Le présent lot
> **ne la corrige pas** et **ne la rejoue pas** : il rend `W4-R` **réellement
> exécutable et homologable** avant toute nouvelle tentative. Voir le §14.
>
> | | Correction |
> |---|---|
> | **V5 · C1** | **`L5` était inexécutable comme écrit, et l'exécution l'a franchi.** L'instant de démarrage est **rattaché à `L0`**, qui le porte déjà ; `L5` est **strictement recentré sur les enregistrements PERSISTANTS** ; ses **lecteurs licites et son repli sont nommés** ; et la **caractérisation complète du même objet**, que le §5.1 rend nécessaire, y est **expressément autorisée**. `/var/run/utmp` et `who -b` deviennent **interdits hors acte prévu** — §4, §5, §5.3 |
> | **V5 · C2** | **`RE-2` et `RE-5` étaient défectueuses par construction** : elles exigeaient « inchangé » d'une unité **cycliquement déclenchée**. Le modèle `R2a`/`R2b` de `w4p1-lot-terrain-borne.md` V3 est **transposé** — unités invariantes, unité superviseur cyclique, timer à phases nominales —, et l'exigence de **compteur de relances est retirée pour les `.timer`**, où elle est **inapplicable** — §9 |
> | **V5 · C3** | **`RA-3` ne distinguait pas le cycle nominal d'une dérive.** Le **cycle attendu du superviseur et de son timer MUST NOT déclencher `RA-3`** ; toute variation **non expliquée par ce cycle** demeure déclencheur — §8 |
> | **V5 · C4** | **Le rejeu est borné** : une **nouvelle autorisation humaine** est exigée avant toute réexécution, et le présent lot **ne prononce pas `P-A5`**, **ne rouvre pas `G3`**, **n'ouvre aucune `P-9`** — §10, §15 |
>
> **Version 4**, après réaudit. **Quatre blocages fermés.** Aucun terrain.
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
| **S3** | **enregistrements persistants de démarrage / arrêt** | le **CARACTÈRE** du redémarrage — `A₂`. **Elle ne porte PAS l'instant** : celui-ci relève de `L0`, sous la clause d'identité du §7.1.0 | probable — fichier, indépendant du journal |
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
> - **lire `/var/run/utmp`**, ni aucune table de sessions **courante** : ce n'est
>   **pas** l'objet de `L5`, qui porte sur les enregistrements **persistants** ;
> - employer **`who`**, sous quelque forme que ce soit, **hors d'un acte qui le
>   prévoit nommément** — aucun acte de la liste close ne le prévoit ;
> - exécuter un acte **hors de la liste close du §5**.

> **Les deux interdictions ci-dessus sont ajoutées par la V5, et elles portent
> sur un franchissement réel.** L'exécution du 2026-09-03 a employé **`who -b`**
> au titre de `L5`, en le croyant lecteur du même objet. **Il ne l'est pas** :
> `who -b` lit la table **courante** — `/var/run/utmp` —, tandis que `L5` porte
> sur `/var/log/wtmp`, **fichier distinct**. **`RA-1` était dû, et il a été
> prononcé à l'homologation.** Le §14 en tire les conséquences.

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
| **`L0`** | relever la **joignabilité**, l'**horodatage de l'hôte**, l'**identifiant du démarrage courant** et le **temps de fonctionnement** — **et en dériver l'INSTANT DU DÉMARRAGE COURANT**, par soustraction du temps de fonctionnement à l'horodatage | lecture | `RE-3` — **et l'INSTANT de `A`**, §7.1 |
| **`L1`** | **empreintes de RÉFÉRENCE** des fichiers à lire, prises **avant toute lecture de contenu** : `<script-superviseur>`, les **quatre** définitions d'unité, la configuration de journalisation | lecture | **`RE-1`** |
| **`L2`** | **relevé d'état des QUATRE unités** — `<unité-superviseur>`, `<unité-pont>`, `<unité-démon>`, `<timer-guard>`. **Propriétés relevées, nommément** : **état d'activité** · **sous-état** · **résultat** · **identifiant d'invocation** · **`ActiveEnterTimestamp`** · **compteur de relances, pour les seules unités de service** — la propriété est **inapplicable à `<timer-guard>`** | lecture | **`RE-2a`**, **`RE-2b`**, **`RE-2c`**, **`RE-5a`**, **`RE-5b`**, **`RA-3`** |
| **`L3`** | lire la **configuration de journalisation du système** — le ou les fichiers qui décident de la **persistance** du journal | lecture de fichier | `S4` |
| **`L4`** | **énumérer les démarrages** connus du journal | lecture | `S4` |
| **`L5`** | lire les **enregistrements PERSISTANTS de démarrage et d'arrêt** — les **TROIS objets** du §5.3 : **`O-a`** `/var/log/wtmp` · **`O-b`** ses rotations · **`O-c`** `/var/log/wtmp.db`, **et eux seuls** —, pour en tirer le **CARACTÈRE** du redémarrage : **commandé** ou non. Objet, lecteurs, repli, régimes de validation et exploitabilité : **§5.3** | lecture | **le CARACTÈRE de `A`** — `S3` |
| **`L6`** | lire **`<script-superviseur>`**, aux seules fins de déterminer : **(i)** le **puits de journalisation** de ses chemins terminaux · **(ii)** la **forme exacte de la commande de redémarrage machine** · **(iii)** la **forme exacte de la commande de redémarrage du pont** | lecture de fichier | `S2` |
| **`L7`** | **si et seulement si `L6` établit un puits FICHIER** : **empreinte de ce puits prise AVANT de le lire**, puis lecture **bornée** à la fenêtre du §6.1 | lecture de fichier | `B`, `C` — `S2`, **`RE-1 bis`** |
| **`L8`** | lire les **définitions d'unité** des **quatre** unités — pour établir **(i)** **qui peut commander** un redémarrage machine · **(ii)** **quelles dépendances propagent** un redémarrage · **(iii)** sur `<timer-guard>`, les **DIRECTIVES TEMPORELLES** qui gouvernent son échéance : `OnBootSec`, `OnStartupSec`, `OnActiveSec`, `OnUnitActiveSec`, `OnUnitInactiveSec`, `OnCalendar`, ainsi que l'**unité déclenchée** et son **type de service** | lecture de fichier | `B`, §7.1.1 — `S5` · **`RE-5b`** et **`RA-3`**, §9.2 |
| **`L9`** | **`<journal-démon>`** : **d'abord établir la RÉTENTION** — que la source couvre effectivement la date visée —, **puis seulement** lire les événements bornés à la fenêtre du §6.1 | lecture | `A` — `S7` |
| **`L10`** | lire le **journal des démarrages survivants**, borné à la fenêtre du §6.1 | lecture | `B`, `C` — `S1` |
| **`L11`** | **inventorier et vérifier** l'artefact terrain `G.2` contre ses **trois empreintes**, puis en **lire** les pièces de préflight | lecture, **hors ligne** | `A`, `B`, `C` — `S6` |
| **`L12`** | **empreintes FINALES** — même ensemble que `L1` pour **`RE-1`**, **plus** le puits de `L7` s'il existe pour **`RE-1 bis`** | lecture | **`RE-1`** et **`RE-1 bis`** |

> **Clause — `L2` produit exactement ce que les preuves exigent, et rien de
> plus.** La liste des propriétés ci-dessus est **close**. **Aucune preuve `RE`
> et aucun critère `RA` ne MAY exiger une propriété qui n'y figure pas** : la V5
> réclamait un `ActiveEnterTimestamp` de timer que `L2` ne relevait pas, et une
> *« cadence tenue »* qu'aucune de ses deux prises ne peut établir.
>
> **`ActiveEnterTimestamp` est ajouté parce que `RE-2c` en dépend.** Il est la
> seule propriété qui distingue, pour `<timer-guard>`, une **alternance nominale**
> — timestamp inchangé — d'un **réarmement** — timestamp modifié.

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
> | 2 | **à la fin**, après la dernière lecture | établir `RE-2a`, `RE-2b`, `RE-2c`, `RE-3`, `RE-5a`, `RE-5b` |
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

### 5.4 Bornage de l'exploitation — règle positive

> **Clause — opposable à tout acte de lecture du présent lot.**
>
> **Ce qui est EXPLOITÉ au soutien de `A`, `B`, `C` ou d'une origine concurrente
> `O1` à `O4` MUST être borné** à la **fenêtre du §6.1** — l'intervalle précédant
> l'instant du redémarrage étudié, d'une étendue d'au moins `380 s` — élargie au
> plus à la **journée du préflight `G.2`** lorsque la granularité de la source
> l'impose.
>
> **Est HORS de ce bornage, et MUST NOT fonder un élément de la règle de
> décision** : tout enregistrement, toute ligne, toute pièce **datée hors de cet
> intervalle**.
>
> **Ce bornage porte sur l'EXPLOITATION, non sur la lecture technique.** Établir
> qu'une source **couvre** ou **ne couvre pas** une période, et rendre un fichier
> **lisible**, sont des actes d'**instrumentation** : ils sont régis par le §5.3,
> et ils **ne lèvent pas** la présente règle.
>
> **La distinction est la suivante, et elle est opposable :**
>
> | | Régime |
> |---|---|
> | *« ce fichier porte 224 enregistrements, du 2024-03-24 au 2026-08-27 »* | **instrumentation** — licite, §5.3 |
> | *« aucun `BOOT_TIME` n'y figure »* | **instrumentation** — licite, §5.3 |
> | *« un enregistrement du 2024-05-12 montre que… »* | **exploitation hors bornage** — **INTERDIT** |

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

### 5.3 `L5` — objet, lecteurs licites, repli, et caractérisation autorisée

> **Cette section est créée par la V5. Elle répare une clause inexécutable.**

#### L'objet, et lui seul

**`L5` porte sur TROIS objets, et sur eux seuls** — les enregistrements
**persistants** de démarrage et d'arrêt.

| | Objet | Nature |
|---|---|---|
| **O-a** | **`/var/log/wtmp`** | **conteneur plat** d'enregistrements de taille fixe |
| **O-b** | **`/var/log/wtmp.1`** et rotations ultérieures | **conteneur plat**, même nature que `O-a` |
| **O-c** | **`/var/log/wtmp.db`** | **base de données** — magasin persistant des implémentations récentes |

| | |
|---|---|
| **HORS de l'objet** | `/var/run/utmp` — table **courante** des sessions —, et tout lecteur qui l'interroge, **`who` compris** — §4 |

> **`O-c` est entré dans l'objet pour un motif de fait.** La seconde exécution
> l'a **découvert** en énumérant les rotations, et **s'est correctement abstenue
> de le lire** : aucun acte ne le prévoyait alors. **Son abstention était juste ;
> l'exclusion, elle, ne l'était pas** — ce fichier est, sur les implémentations
> qui l'emploient, **le magasin persistant des enregistrements de démarrage**,
> c'est-à-dire l'objet même que `L5` cherche.

> **Clause — discipline commune aux trois objets, sans allègement.**
>
> | | |
> |---|---|
> | **présence CONSTATÉE d'abord** | l'existence, la taille et la date de **chacun** des trois sont **constatées avant toute lecture** |
> | **lecture SEULEMENT si le lot la prévoit** | elle relève de **`L5`**, à son rang, et d'aucun autre acte. **Aucun acte nouveau n'est créé** |
> | **lecteurs** | **les TROIS du présent §5.3, et EUX SEULS.** **Aucun quatrième lecteur n'est admis**, sous quelque forme et pour quelque objet que ce soit |
> | **AUCUNE extrapolation** | ce qu'un objet ne porte pas **ne prouve rien**. **Aucune attribution ne MAY être tirée d'une absence** — §7.3 |
> | **absence de l'objet** | `L5` la **constate** et poursuit. Elle **n'est pas un manquement**, et **ne fonde aucun constat** |

#### Deux régimes de validation, selon la NATURE de l'objet

> **Les critères `a` et `b` supposent un conteneur plat d'enregistrements de
> taille fixe.** Les opposer à une base de données n'aurait **aucun sens** : une
> base ne se découpe pas en tranches égales, et sa « taille minimale
> d'enregistrement » n'existe pas.

| | **O-a / O-b** — conteneur plat | **O-c** — base de données |
|---|---|---|
| **critère `a`** couverture intégrale | **APPLICABLE** | **NON APPLICABLE** |
| **critère `b`** minimalité | **APPLICABLE** | **NON APPLICABLE** |
| **critère `c`** champ temporel | **APPLICABLE** | applicable **seulement** si un lecteur licite en rend des enregistrements |
| **critère `d`** témoin indépendant | **APPLICABLE** | **APPLICABLE**, dès lors que des enregistrements sont rendus |
| **opération 2** — constat d'absence | **séparée**, sur parse validé | **séparée**, et **conditionnée à l'exploitabilité** |

> **Clause — `O-c` PRÉSENT mais INEXPLOITABLE, et la conduite qui s'ensuit.**
>
> Si **aucun** des trois lecteurs licites — **`last`**, **`utmpdump`**, ou le
> **repli 3** — ne rend d'enregistrement à partir de `O-c`, alors :
>
> 1. `O-c` est consigné **PRÉSENT**, avec sa **taille**, sa **date** et son
>    **empreinte** ;
> 2. il est consigné **INEXPLOITABLE SOUS CE LOT** ;
> 3. **aucune improvisation** : ni lecteur ajouté, ni format supposé, ni contenu
>    inféré ;
> 4. **aucun constat, positif ou négatif, n'en est tiré** — ni sur `A₂`, ni sur
>    quoi que ce soit.
>
> **Le repli 3, tel que le présent § le définit, analyse un conteneur plat.**
> S'il ne peut pas rendre `O-c` — les critères `a` et `c` n'admettant aucune
> taille —, il **ne s'applique pas** à cet objet, et **`O-c` est inexploitable**.
> **Ce n'est pas un échec du lot : c'est sa borne.**
>
> **Ce que cette inexploitabilité laisse ouvert**, et qu'elle **ne comble pas** :
> `O-c` pourrait porter les enregistrements de démarrage que `O-a` ne porte pas.
> **Le lot ne le suppose pas**, **ne l'exclut pas**, et **n'ajoute aucun lecteur
> pour le savoir**. **Ajouter un lecteur relèverait d'un arbitrage humain et
> d'une correction du lot**, non de l'exécutant.

> **La distinction n'est pas formelle.** `who -b` lit la table **courante**, non
> le fichier persistant. Ce sont **deux fichiers différents**, et les confondre
> a coûté un `RA-1` à l'exécution du 2026-09-03.

#### Ce que `L5` établit — et ce qu'il n'établit plus

| | |
|---|---|
| **`L5` établit** | le **CARACTÈRE** du redémarrage : **commandé** — enregistrement d'arrêt ordonné —, ou **non commandé** |
| **`L5` n'établit plus l'INSTANT** | il est porté par **`L0`**, rang 2, qui lit déjà l'horodatage de l'hôte et le temps de fonctionnement. **L'instant s'en dérive par soustraction**, sans lecture supplémentaire |

> **Pourquoi ce déplacement.** La V4 faisait de `L5` le seul porteur de `A`, ce
> qui obligeait à lui faire rendre l'instant — alors que `L0` le portait déjà, et
> que la source persistante peut fort bien **ne porter aucun enregistrement de
> démarrage**. **C'est exactement ce que l'exécution a constaté**, et elle a dû
> franchir la liste close pour y suppléer.

#### Lecteurs licites, et repli

> **Clause.** `L5` **MAY** employer, dans cet ordre de préférence, **et
> exclusivement** :
>
> | | Lecteur | Condition |
> |---|---|---|
> | **1** | **`last`** — avec sélection explicite du fichier persistant | s'il est présent sur l'hôte |
> | **2** | **`utmpdump`** — sur le fichier persistant | s'il est présent |
> | **3** | **repli : figement du fichier hors installation, puis analyse hors ligne** | **si et seulement si** ni 1 ni 2 n'est disponible |
>
> **Le repli 3 est un acte de `L5`, non un acte nouveau.** Il consiste à
> **rapatrier le fichier tel quel** — l'empreinte étant relevée sur l'hôte avant
> rapatriement et vérifiée après —, puis à l'analyser **hors installation**,
> conformément au §5.1.
>
> **Aucun autre lecteur n'est licite.** En particulier, aucun lecteur
> interrogeant la table courante — §4.

#### Caractérisation complète du même objet — expressément autorisée

> **Clause.** Lorsque le repli 3 est employé, `L5` **MAY** procéder, **sur le
> fichier figé et sur lui seul**, à la **caractérisation complète nécessaire à
> son exploitation** :
>
> - **découverte du format** d'enregistrement, lorsque le format supposé est
>   **invalidé par un motif témoin** ;
> - **couverture de la source** — instant le plus ancien, instant le plus
>   récent, décompte des enregistrements et des types présents ;
> - **inventaire des types** d'enregistrement portés, ou de leur absence.
>
> **Cette caractérisation est une INSTRUMENTATION, et rien d'autre.** Elle est
> autorisée **uniquement** en tant qu'elle est **nécessaire** pour rendre le
> fichier lisible et pour établir ce qu'il porte.
>
> **Elle NE LÈVE PAS le bornage de l'exploitation du §5.4.** Ce qui est
> **exploité au soutien de `A`, `B`, `C` ou d'une origine concurrente** demeure
> borné à la fenêtre, quelle qu'ait été l'étendue de l'instrumentation.
>
> **La règle en une phrase** : on **balaie** tout le fichier pour savoir le lire
> et savoir ce qu'il contient ; on **n'exploite** que ce qui tombe dans la
> fenêtre.
>
> **Sans cette autorisation, la clause est inexécutable** : un format inconnu ne
> se déchiffre pas en ne regardant que six minutes de données.

> **Motif témoin — obligatoire, et NON circulaire.**
>
> **La V5 était circulaire** : elle exigeait de valider le format contre
> l'instant de `L0`, c'est-à-dire contre un enregistrement de démarrage — alors
> que **l'objet peut n'en porter aucun**, et que c'est précisément ce que `L5`
> doit pouvoir constater.
>
> **Deux opérations DISTINCTES, à ne jamais confondre :**
>
> | | Opération | Ce qu'elle exige |
> |---|---|---|
> | **1** | **VALIDATION STRUCTURELLE du format** | les **quatre critères cumulatifs** ci-dessous, **et eux seuls** |
> | **2** | **CONSTAT d'absence de `BOOT_TIME` / `RUN_LVL`** | **rien de plus qu'un parse structurellement validé**. Il ne présuppose **pas** que ces types existent |
>
> **Clause.** Un parse **structurellement validé** au sens de l'opération 1
> **PEUT établir l'absence** de `BOOT_TIME` et de `RUN_LVL` dans l'objet. **Cette
> absence est un constat sur la COUVERTURE de la source**, non une inférence sur
> les faits — la distinction du §7.3 demeure entière.
>
> **Clause.** Un parse dont la **validation structurelle échoue** **MUST NOT**
> fonder le moindre constat, et sa sortie **MUST** être conservée comme preuve
> qu'il a été écarté.
>
> **Les quatre critères de la validation structurelle — cumulatifs.**
>
> | | Critère |
> |---|---|
> | **a · COUVERTURE INTÉGRALE** | la taille d'enregistrement retenue **divise exactement** le conteneur, et **chaque octet appartient à un enregistrement**. Le parse **couvre chaque enregistrement élémentaire** |
> | **b · MINIMALITÉ** | **aucun diviseur propre** de la taille retenue ne satisfait également les critères **a**, **c** et **d**. **Si une taille moitié les satisfait, c'est ELLE qui est retenue** |
> | **c · CHAMP TEMPOREL** | un champ temporel **plausible** à un **offset interne constant**, sur la **quasi-totalité** des enregistrements non vides |
> | **d · TÉMOIN INDÉPENDANT** | au moins un enregistrement dont l'**instant ou le contenu** est **vérifiable par ailleurs**, de **n'importe quel type présent dans le même objet** |

> **Le critère `b` n'est pas théorique, et il est décisif.** Un conteneur de
> `n` enregistrements de taille `t` se divise **aussi** par `2t`. Un parse à
> `2t` **saute systématiquement un enregistrement sur deux** — il peut paraître
> cohérent, et **manquer la moitié du contenu**, `BOOT_TIME` compris.
>
> **Un tel parse MUST NOT être retenu.** Il est **PARTIEL**, et
> **aucun constat d'absence ne MAY être fondé sur un parse partiel** :
> l'opération 2 exige un parse satisfaisant **les quatre critères**.

> **Ce qui n'est PAS un critère de validité — et la V6 se trompait.**
>
> **La séquence chronologique est SUPPRIMÉE.** Les enregistrements `utmp` sont
> **mis à jour EN PLACE** : un emplacement de session est **réécrit** lorsque la
> session change d'état. **Le conteneur n'est donc PAS ordonné
> chronologiquement**, et exiger un ordre aurait **rejeté le format réel**.
>
> **Aucun critère d'ordre, d'aucune sorte, ne MAY être opposé au format.**

> **Ce qui MUST être rapporté** : le témoin retenu, son type, ce qui le rend
> indépendant, **les quatre critères et leur satisfaction un par un** — dont la
> **taille écartée au titre de la minimalité**, s'il y en a une — §11,
> sortie 8 quater.

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
> **L'instant du redémarrage est établi par `L0`**, au rang 2, par soustraction
> du temps de fonctionnement à l'horodatage de l'hôte — **et seulement sous la
> clause d'identité du §7.1.0**, qui vérifie qu'il s'agit bien du redémarrage
> **étudié**. Corroborable par `L9` et `L11`, jamais remplaçable par eux.
> **La V4 l'attribuait à `L5`** ; c'était une erreur de typage, `L0` le portant
> déjà. **La V5 omettait la vérification d'identité** ; c'en était une autre.
>
> **Un instant CANDIDAT ne définit aucune fenêtre.** Tant que le §7.1.0 n'a pas
> été satisfait, la fenêtre n'existe pas.
>
> **Tant qu'il n'est pas établi, aucune fenêtre n'existe**, et les actes `L7`,
> `L9` et `L10` sont **sans objet** pour ce qui est de la fenêtre.
>
> **Le CARACTÈRE du redémarrage est établi par `L5`**, au rang 7 — §5.3. Son
> absence ne supprime pas la fenêtre : elle laisse **`A` incomplet**.

### 6.2 L'ordre

| # | Acte | Sortie attendue | Si elle manque |
|---|---|---|---|
| **1** | **`L11`** — artefact `G.2`, **si accessible hors installation** | trois empreintes vérifiées ; inventaire des pièces de préflight | poursuivre ; `L11` est repris au rang 11 |
| **2** | **`L0`** | hôte joignable, horodatage, démarrage courant, temps de fonctionnement — **et un INSTANT CANDIDAT**, par soustraction. **Il ne devient `A₁` qu'après la clause d'identité du §7.1.0** | **`STOP`** — sans hôte, aucun acte. **Sans `A₁` acquis, aucune fenêtre n'existe** — §6.1 |
| **3** | **`L1`** — **empreintes de référence, avant toute lecture de contenu** | empreintes des fichiers de la liste | **`STOP`** — sans référence, `RE-1` est inatteignable |
| **4** | **`L2`** — état initial des **quatre** unités | état, sous-état, résultat, invocation, `ActiveEnterTimestamp`, relances *(unités de service seules)* | **`STOP`** — sans état initial, **`RE-2a`**, **`RE-2b`**, **`RE-2c`**, **`RE-5a`**, **`RE-5b`** et **`RA-3`** sont sans moyen |
| **5** | **`L3`** | le journal est **persistant** ou **volatil** — fait établi, non supposé | consigner *« non établi »* ; `L4` et `L10` deviennent douteux |
| **6** | **`L4`** | liste des démarrages connus | consigner ; **ne pas conclure** |
| **7** | **`L5`** | le **CARACTÈRE** du redémarrage — l'élément **`A₂`** — par les enregistrements **persistants**, selon les lecteurs et le repli du **§5.3** | **`A₂` est NON ÉTABLI**, donc **`A` est incomplet**. Consigner. **L'instruction se POURSUIT** : la fenêtre subsiste **si et seulement si `A₁` a été ACQUIS** sous la clause d'identité du §7.1.0 — **le rang 2 n'a rendu qu'un CANDIDAT**, jamais `A₁` ; **aucun rang ne devient sans objet du seul fait que `A₂` manque**, et **les rangs 12 et 13 demeurent OBLIGATOIRES**. Le prononcé a lieu au rang 13, sous le **§7.4** |
| **8** | **`L6`** | puits de journalisation · forme des deux commandes | consigner ; `L7` sans objet |
| **9** | **`L8`** — définitions des **quatre** unités | qui peut commander un redémarrage · **quelles dépendances le propagent** (**§7.1.1**) | consigner ; **`B` devient inqualifiable** — **§7.1.1** |
| **10** | **`L7`** — *si et seulement si* `L6` a établi un puits fichier | empreinte prise **avant lecture**, puis lignes de la fenêtre | `L7` sans objet |
| **11** | **`L9`**, puis **`L10`**, puis **`L11`** si non fait au rang 1 | rétention établie puis événements · lignes de la fenêtre · pièces de préflight | consigner |
| **12** | **`L2`** et **`L0`** — **répétition finale** | état et démarrage **inchangés** | un écart est **`RA-3`** ou **`RA-4`** |
| **13** | **`L12`** — empreintes finales, puis **analyse hors ligne**, puis **PRONONCÉ**. **C'est le DERNIER acte du lot, sans exception** — §6.3 | empreintes **identiques** · l'un des deux verdicts du §2.2 | un écart d'empreinte est **`RA-2`** |

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

> **Clause — ce que `A₁` non établi rend sans objet, et ce qu'il ne rend PAS
> sans objet.** La V2 se trompait ici, et l'erreur était grave.
>
> **Depuis la V5, cette clause porte sur `A₁` — l'INSTANT — et sur lui seul** :
> c'est lui qui définit la fenêtre. **`A₂` non établi ne rend aucun rang sans
> objet** ; il laisse `A` incomplet, et rien de plus.
>
> | Rang | Sort si **`A₁`** n'est pas établi | Motif |
> |---|---|---|
> | **8** — `L6` | **exécuté** | ne dépend pas de la fenêtre |
> | **9** — `L8` | **exécuté** | ne dépend pas de la fenêtre |
> | **10** — `L7` | **la LECTURE bornée devient sans objet** — faute de fenêtre. **L'empreinte du puits est prise si le puits existe** | seule la borne temporelle disparaît |
> | **11** — `L9` | **la rétention est établie** ; la **lecture bornée** devient sans objet | idem |
> | **11** — `L10` | **sans objet** | entièrement défini par la fenêtre |
> | **11** — `L11` | **exécuté** | l'artefact ne dépend pas de la fenêtre |
> | **12** — `L2` et `L0`, répétition finale | **OBLIGATOIRE, en toute hypothèse** | il porte **`RE-2a`**, **`RE-2b`**, **`RE-2c`**, **`RE-3`**, **`RE-5a`** et **`RE-5b`** |
> | **13** — `L12`, puis prononcé | **OBLIGATOIRE, en toute hypothèse** | il porte **`RE-1`**, et **le verdict** |
>
> **La V2 déclarait le rang 12 « sans objet ».** Elle privait ainsi le lot de
> **trois preuves de non-mutation sur cinq**, et rendait la restauration du §9
> **indémontrable** — alors même que le lot n'a rien muté. **Un lot qui ne peut
> pas prouver sa propre innocuité est un lot non clos.**

### 6.3 Verrou de clôture

> **La seconde exécution est devenue non close APRÈS son prononcé**, pour avoir
> lu l'hôte une fois de plus. Le lot n'interdisait pas explicitement cette
> lecture ; **il l'interdit désormais**.

> **Clause — la clôture, et ce qu'elle ferme.**
>
> **Le rang 13 comporte trois opérations, dans cet ordre, et rien d'autre :**
>
> | | Opération |
> |---|---|
> | **1** | **`L12`** — empreintes finales |
> | **2** | **analyse hors ligne**, sur la matière déjà figée |
> | **3** | **PRONONCÉ** — l'un des deux verdicts du §2.2 |
>
> **La CLÔTURE n'existe qu'après le prononcé.** Un lot arrêté avant lui est
> **non clos**, quelle qu'en soit la raison — §8.
>
> **À compter du prononcé, et sans exception :**
>
> | | |
> |---|---|
> | **aucune lecture de l'hôte** | quelle qu'en soit la nature, quelle qu'en soit la brièveté |
> | **aucune corroboration** | d'un verdict, d'une preuve `RE`, d'un critère `RA`, ni de quoi que ce soit |
> | **aucun acte supplémentaire** | y compris un acte de la liste close, qui serait alors **hors de son rang** |
>
> **Le franchissement est `RA-1`** — acte hors liste close ou hors de son rang —
> **et `RA-8`** — franchissement d'une frontière du §4. **Il rend le lot NON
> CLOS, alors même que le prononcé a eu lieu** : un prononcé suivi d'un acte
> illicite ne clôt rien.
>
> **Ce qui demeure licite après le prononcé** : l'**analyse hors ligne** de la
> matière **déjà figée**, et la **rédaction du rapport**. Ni l'une ni l'autre ne
> touche l'installation.

---

## 7. Règle de décision

### 7.1.0 `A₁` — l'ancrage sur l'ÉVÉNEMENT ÉTUDIÉ, et la clause d'identité

> **La V5 laissait un démarrage ULTÉRIEUR devenir silencieusement `A₁`.** Elle
> écrivait que l'instant *« est établi par `L0` »*, sans vérifier que le
> démarrage courant est bien **celui qui a suivi le redémarrage étudié**.
> **Sur une installation qui redémarre entre-temps, `L0` désigne un autre
> événement**, et le lot aurait attribué une instance qui n'est pas la sienne.

**L'événement étudié est fixé par le corpus, et par lui seul** — `G2-C` §6,
réserve `A-5` : le redémarrage machine survenu **pendant le préflight de la
campagne `G.2`**, *« hors campagne »*. `G2-C` §1 situe la campagne elle-même.

> **Ce que `L0` donne, et ce qu'il ne donne pas.**
>
> **`L0` ne rend QUE le DERNIER démarrage** — le démarrage **courant**. Il ne dit
> rien de ceux qui l'ont précédé, ni de leur nombre, ni de leurs instants.
>
> **Le constat (ii) de la V6 était TAUTOLOGIQUE, et il est retiré.** Il exigeait
> que le temps de fonctionnement *« couvre sans interruption l'intervalle depuis
> l'instant candidat »* — or **l'instant candidat est dérivé de ce temps de
> fonctionnement**. La vérification ne pouvait pas échouer : elle ne vérifiait
> rien.

> **Clause d'identité — `A₁` exige un rattachement UNIVOQUE.**
>
> L'instant dérivé de `L0` est un **instant candidat**. Il ne devient `A₁` que si
> le **démarrage courant** est rattaché de façon **univoque** au redémarrage
> étudié, par la conjonction des deux conditions suivantes :
>
> | | Condition |
> |---|---|
> | **(i)** | l'instant candidat tombe **avant l'ouverture de la campagne `G.2`** et **après le début de son préflight**, tels que le corpus les situe |
> | **(ii)** | une **source de la liste close** établit **POSITIVEMENT** que le démarrage courant est **celui qui a immédiatement suivi** le redémarrage étudié — c'est-à-dire qu'**aucun autre démarrage ne s'est intercalé** entre eux |
>
> **Ce qui peut satisfaire (ii) — `L4` SEUL.** Une **énumération des
> démarrages** par `L4` qui **couvre la période** allant de l'événement étudié à
> l'exécution du lot, et qui n'y montre **qu'un seul** démarrage.
>
> **`L5` NE PEUT PAS satisfaire (ii)**, et la V7 se contredisait en le
> permettant. Le §5 et la source `S3` posent que **`L5` ne porte pas l'instant du
> redémarrage** — seulement son **caractère**, `A₂`. **Lui rendre ici la capacité
> de porter une séquence de démarrages serait lui rendre l'instant**, que la V6
> lui avait retiré. **`L5` ne porte aucun instant de démarrage, en aucune
> circonstance.**
>
> **Aucun observable n'est ajouté par la présente clause.** Si `L4` ne rend pas
> cela, **(ii) n'est pas satisfaite** — et le lot **ne va pas en chercher
> ailleurs**.

> **Deux causes d'échec de (ii), par `L4`, et elles suffisent chacune :**
>
> | | Cause | Conséquence |
> |---|---|---|
> | **1** | `L4` **ne couvre pas** la période nécessaire — l'énumération commence **après** l'événement étudié | l'unicité n'est **pas établissable** |
> | **2** | `L4` couvre la période mais **n'y montre pas un démarrage unique** | l'unicité est **contredite** |
>
> **Dans l'un et l'autre cas, `A₁` demeure NON ÉTABLI.**

> **Deux cas laissent `A₁` NON ÉTABLI, et tous deux doivent être nommés :**
>
> | | Cas | Pourquoi |
> |---|---|---|
> | **1** | l'installation a **redémarré depuis** l'événement étudié | `L0` désigne alors un **autre** démarrage. L'instant candidat n'est pas celui de `A-5` |
> | **2** | **plusieurs redémarrages demeurent possibles dans le préflight** | `G2-C` §6 mentionne *« un redémarrage machine »* **sans exclure qu'il y en ait eu d'autres**. **Localiser un démarrage dans la fenêtre du préflight ne l'identifie pas à celui que `A-5` consigne** |
>
> **Dans l'un et l'autre cas, `A₁` demeure NON ÉTABLI.** L'instant candidat est
> **consigné comme candidat**, et **MUST NOT** être employé — ni comme `A₁`, ni
> pour définir la fenêtre du §6.1.
>
> **Le lot ne dispose alors d'aucune autre source pour l'instant** : `L5` ne le
> porte plus — §5, `S3` —, et `L9` comme `L11` ne font que **corroborer**.
> **Le verdict est alors `INSTANCE NON ATTRIBUABLE`**, par le §7.4.

### 7.1 Ce qui doit être établi pour `INSTANCE ATTRIBUÉE`

**Trois éléments, CUMULATIFS** — dont le premier se dédouble depuis la V5.
**L'absence d'un seul suffit à écarter le verdict.**

> **`A` est acquis si et seulement si `A₁` ET `A₂` le sont.** La V4 confondait
> les deux sous un porteur unique, et rendait `A` inatteignable dès que la source
> persistante ne portait aucun enregistrement de démarrage.
>
> **Et `A₁` n'est acquis que sous la clause d'identité du §7.1.0** : un instant
> candidat n'est pas `A₁`.

| # | Élément | Établi par | Corroborable par |
|---|---|---|---|
| **A₁** | l'**INSTANT** du redémarrage machine **étudié** — celui du préflight `G.2` | **`L0`** rend l'instant candidat, rang 2 · **`L4`** établit l'unicité, rang 6 — **les DEUX sont requis**, sous la clause d'identité du §7.1.0 | `L9` (encadrement de l'interruption) · `L11` |
| **A₂** | son **CARACTÈRE de redémarrage COMMANDÉ** — non une coupure, non un arrêt matériel | **`L5`**, rang 7 — §5.3 | `L9` · `L11` |
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

> **Clause.** Si, après les actes du §6 exécutés dans l'ordre, **`A` — c'est-à-dire
> `A₁` ET `A₂` — ou `B` n'est pas établi**, l'instruction **S'ARRÊTE** : **aucun acte supplémentaire n'est
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
| **`RA-3`** | l'**état d'une unité change** pendant le lot — `<unité-pont>`, `<unité-superviseur>`, `<unité-démon>`, `<timer-guard>` —, **hors le cycle nominal défini ci-dessous** | **`STOP`** ; le lot n'a pas à s'exécuter sur une installation qui bouge |
| **`RA-4`** | **redémarrage machine** pendant le lot, quelle qu'en soit la cause | **`STOP`** immédiat |
| **`RA-5`** | un acte exigerait d'**écrire sur l'hôte** | **`STOP`** ; l'acte n'est pas exécuté |
| **`RA-6`** | l'**autorisation humaine du §10 est absente**, dépassée, ou son périmètre serait excédé | **`STOP`** ; la demander, ou renoncer |
| **`RA-7`** | **doute de l'exploitant**, sans justification à fournir | **`STOP`** |
| **`RA-8`** | une frontière du **§4** est franchie ou sur le point de l'être | **`STOP`** immédiat |

> **Clause — le CYCLE NOMINAL ne déclenche PAS `RA-3`.** Ajoutée par la V5.
>
> `<unité-superviseur>` est **déclenchée périodiquement** par `<timer-guard>`.
> Son passage par `activating` → `active` → `inactive`/`dead`, et le changement
> de son **identifiant d'invocation** à chaque cycle, **sont le phénomène
> observé**, non une dérive. Il en va de même de l'alternance
> `running` / `waiting` de `<timer-guard>`.
>
> | | Déclenche `RA-3` ? |
> |---|---|
> | `<unité-superviseur>` change d'état ou d'identifiant d'invocation **selon sa cadence déclarée** | **NON** |
> | `<timer-guard>` alterne `running` / `waiting`, `ActiveEnterTimestamp` **inchangé** | **NON** |
> | **toute variation NON expliquée par ce cycle**, **constatée sur les propriétés que `L2` relève** — `ActiveEnterTimestamp` du timer **modifié**, compteur de relances **non nul**, `Result` **autre que succès**, `<timer-guard>` **inactif** | **OUI** |
> | **l'`InvocationID` du superviseur demeure INCHANGÉ alors qu'une activation est ÉTABLIE DUE** au sens du §9.2 — mode à échéance indépendante de la durée d'exécution, et `Δ` la dépassant | **OUI** : une activation **due** n'a pas eu lieu |
> | l'`InvocationID` demeure inchangé **sans qu'une activation soit établie due** — `OnUnitInactiveSec` seul, `OnBootSec` seul, ou mode indéterminé | **NON** — §9.2. Le déclencher serait un `STOP` injustifié |
> | **`<unité-pont>` ou `<unité-démon>` change d'identifiant d'invocation ou d'état**, à quelque titre que ce soit | **OUI** |
>
> **`RA-3` ne s'oppose que sur ce que `L2` relève.** La V5 mentionnait une
> *« cadence rompue »* : **`L2` ne la produit pas**, et un critère qu'aucun acte
> n'alimente n'est pas opposable. Les quatre déclencheurs ci-dessus sont **tous
> décidables sur les propriétés de `L2`**, aux rangs 4 et 12 — et à toute
> répétition du cas 3.
>
> **Le registre est celui de `w4p1-lot-terrain-borne.md` V3** : *« Un changement
> d'état ou de date de démarrage de `<unité-superviseur>` n'est PAS une
> divergence. C'est le phénomène observé. »*

> **Aucune seconde tentative dans la même fenêtre**, et **aucun rejeu.**
>
> **Un rejeu n'est admissible qu'aux QUATRE conditions CUMULATIVES suivantes**,
> détaillées au §14.1 :
>
> | # | Condition |
> |---|---|
> | **1** | **AUDIT INDÉPENDANT DU DELTA** |
> | **2** | **INTÉGRATION** |
> | **3** | **AUTORISATION HUMAINE PROPRE ET NOUVELLE**, **postérieure aux DEUX** — l'audit et l'intégration —, **nommant explicitement `W4-R` ET sa version** |
> | **4** | **REJEU UNIQUE** — **une exécution par autorisation**, et une seule |
>
> **Ces quatre conditions sont le NOYAU COMMUN d'admissibilité, et non la
> totalité des exigences.** Elles **ne dispensent d'AUCUNE autre obligation du
> présent document**, et les **`MUST`** comme les **`MUST NOT`** du §10 demeurent
> **pleinement opposables** — notamment l'interdiction de déduire une
> autorisation de l'audit, de l'intégration ou du merge, et l'interdiction
> d'excéder le périmètre autorisé.
>
> **Le §8, le §10 et le §14.1 portent le MÊME noyau, mot pour mot.** Aucun d'eux
> ne l'allège, et aucun n'en énonce un divergent.

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
| **`RE-2a`** | **unités INVARIANTES** — `<unité-pont>` et **`<unité-démon>`** : **identifiant d'invocation** et **compteur de relances** relevés au début et à la fin, **inchangés** | **`L2`**, répété | 4 et 12 |
| **`RE-2b`** | **`<unité-superviseur>`**, dont le **cycle périodique est nominal et attendu** : **aucun acte du lot ne l'a modifiée, démarrée, arrêtée ni redémarrée**, et son **compteur de relances demeure nul**. **Son identifiant d'invocation et son état CHANGENT à chaque cycle : ce n'est PAS une divergence** | **`L2`**, répété | 4 et 12 |
| **`RE-2c`** | **`<timer-guard>`** : **actif** au début et à la fin, **`ActiveEnterTimestamp` inchangé**, et **alternance `running` / `waiting` admise**. **Aucun compteur de relances n'est exigé** — la propriété est **inapplicable à une unité `.timer`** | **`L2`**, répété | 4 et 12 |
| **`RE-3`** | **identifiant du démarrage courant** — **inchangé** en fin de lot ; sa modification est **`RA-4`** | **`L0`**, répété | 2 et 12 |
| **`RE-4`** | **aucun fichier créé, modifié ou supprimé sur l'hôte** — les sorties sont **rapatriées et figées hors de l'installation** ; aucun acte de la liste close n'écrit. **Elle est satisfaite PAR CONSTRUCTION, et cela SUFFIT** — §9.3 | par construction — §5 | tous |
| **`RE-5a`** | **état de `<unité-pont>` et de `<unité-démon>`** en fin de lot, **identique** à celui du début | **`L2`**, répété | 4 et 12 |
| **`RE-5b`** | **régime de `<unité-superviseur>` et de `<timer-guard>` demeuré NOMINAL**, établi **avec les seules prises de `L2`** : **`Result` = succès** aux deux prises pour les deux unités · **compteur de relances nul** aux deux prises pour l'unité de service · **`<timer-guard>` actif** aux deux prises, **`ActiveEnterTimestamp` inchangé** · **et, si une activation est ÉTABLIE DUE au sens du §9.2 : `InvocationID` du superviseur CHANGÉ** ; **sinon, le cycle n'est pas certifié, et `RE-5b` le déclare**. **L'état instantané du superviseur n'est PAS comparé**, il varie par construction | **`L2`**, répété | 4 et 12 |

> **`RE-2a` et `RE-5a` couvrent `<unité-démon>`, et la V1 l'omettait.** `L2`
> porte les **quatre** unités, et non trois : le démon est celui dont un
> redémarrage **propagerait** au pont — `F-13`, §7.1.1 —, et l'omettre aurait
> laissé `O1` sans moyen de constat pendant le lot.

> **Pourquoi `RE-2` et `RE-5` ont été dédoublées — et c'est un défaut réel de la
> V4.** Elles exigeaient *« inchangés »* des **quatre** unités, alors que
> `<unité-superviseur>` est **déclenchée périodiquement** : son identifiant
> d'invocation et son état **changent par construction**, à chaque cycle.
>
> **Lues à la lettre, ces deux preuves étaient INSATISFIABLES** dès que le lot
> dure plus d'un cycle — c'est-à-dire toujours. **L'exécution du 2026-09-03 l'a
> établi sur pièces** : `<unité-superviseur>` est passée de
> `activating`/`start` à `inactive`/`dead`, identifiant d'invocation changé,
> pendant que les deux unités invariantes demeuraient identiques en tous points.
>
> **Le corpus avait déjà résolu ce cas, et la V4 ne l'avait pas repris.**
> `w4p1-lot-terrain-borne.md` V3, correction `D1`, a scindé `R2` en **`R2a`** —
> unités invariantes — et **`R2b`** — *« unité cyclique dont le cycle n'est pas
> une divergence »*. **La V5 transpose ce modèle**, et lui ajoute `RE-2c` pour le
> timer.
>
> **Et la « cadence tenue » cesse d'être exigée.** La V5 la réclamait de
> `RE-5b`. **Deux relevés ponctuels ne l'établissent pas** : une cadence se
> constate sur une **suite** d'instants de déclenchement, que `L2` ne produit
> pas. `RE-5b` est réénoncée sur ce que les **deux prises rendent réellement** —
> résultat, compteur de relances, activité du timer, `ActiveEnterTimestamp`.
>
> **Exiger d'une preuve ce que son acte ne produit pas est le même défaut que
> celui de la V1**, corrigé en `B2` : une preuve sans acte est inexécutable.

> **Et une exigence inapplicable est retirée.** `RE-2` réclamait un **compteur de
> relances** pour `<timer-guard>` : **une unité `.timer` n'en porte pas.**
> L'exécution du 2026-09-03 l'a constaté — la propriété est **absente de la
> sortie**, pour cette unité et pour elle seule. **Exiger une propriété qui
> n'existe pas est un défaut de conception**, non un manquement de l'exécutant.

> **Une limite héritée est corrigée.** `P1-H` §5 consigne que sous `W4-P1`,
> quatre fichiers avaient été lus **avant** la prise d'empreinte de référence,
> laissant un intervalle non couvert et une **réserve déclarée**. Ici, `L1` est
> au **rang 3**, avant toute lecture de contenu.

> **La séparation de `RE-1` et de `RE-1 bis` n'est pas cosmétique.** La V2
> rangeait le puits de `L7` dans `RE-1`, dont la couverture est annoncée
> *« depuis le rang 3 »* — **une promesse que le §9.1 contredisait dans le même
> document**. Les deux preuves sont désormais **distinctes**, avec des
> **couvertures distinctes**, et **le rapport ne peut plus les confondre**.

### 9.3 `RE-4` — aucune corroboration, et le motif

> **Clause — `RE-4` n'appelle AUCUN acte de vérification.**
>
> Elle est satisfaite **par construction** : **aucun acte de `L0` à `L12`
> n'écrit sur l'hôte**, et les sorties sont **rapatriées et figées hors de
> l'installation**. **Cela suffit, et rien de plus n'est requis.**
>
> **Aucune corroboration sur l'hôte ne MAY être entreprise à son sujet** — ni
> avant le rang 13, ni après.
>
> **Une telle corroboration serait un acte hors liste close**, donc **`RA-1`** ;
> conduite après le prononcé, elle serait **de surcroît `RA-8`**, par le verrou
> du §6.3.

> **C'est exactement ce qui a rendu la seconde exécution non close**, et le §14
> le consigne. **Une preuve établie par construction ne se vérifie pas : elle se
> déduit de la liste close elle-même.** Aller la constater sur l'installation,
> c'est sortir de cette liste — donc détruire la preuve qu'on croyait
> renforcer.

### 9.2 `RE-5b` — le cycle doit avoir EU LIEU, et non seulement être possible

> **La V6 certifiait « régime nominal » sans que le superviseur ait cyclé.**
> Ses quatre constats — résultat, relances, timer actif, `ActiveEnterTimestamp`
> — sont **tous compatibles avec un superviseur qui ne se déclenche plus**.
> **Un superviseur qui a cessé de cycler n'est pas nominal**, et le lot doit
> pouvoir le voir.

> **La V7 invoquait une « période déclarée » que rien ne fournissait, et dont la
> notion était ambiguë.** `L8` ne lisait pas les directives temporelles, et un
> `.timer` peut en porter plusieurs, **de sémantiques différentes**. La V8
> étend `L8` (§5) et définit la condition **par mode**.

> **Clause — l'ACTIVATION DUE, définie par mode.**
>
> Soit `Δ` l'**intervalle entre les deux prises de `L2`** — rangs 4 et 12, établi
> par les horodatages de `L0` —, et les **directives temporelles de
> `<timer-guard>`** lues par **`L8`** au rang 9.
>
> **Une activation est réputée DUE entre les deux prises si et seulement si le
> mode applicable donne une échéance INDÉPENDANTE de la durée d'exécution de
> l'unité déclenchée, et que `Δ` excède strictement l'intervalle correspondant :**
>
> | Directive lue par `L8` | Une activation est-elle établissable comme DUE ? |
> |---|---|
> | **`OnCalendar`** | **OUI**, si `Δ` couvre strictement au moins une échéance du calendrier : l'échéance est **fixe**, indépendante de toute durée d'exécution |
> | **`OnUnitActiveSec = T_a`** | **OUI**, si `Δ > T_a` : l'échéance court depuis l'**activation** précédente, non depuis sa fin |
> | **`OnUnitInactiveSec = T_i`** | **NON, JAMAIS sur ce seul fondement** — voir ci-dessous |
> | **`OnBootSec` / `OnStartupSec` seuls** | **NON** : ils ne produisent **qu'une seule échéance par démarrage**. **Aucune activation périodique n'est due** pendant le lot |
>
> **Pourquoi `OnUnitInactiveSec` ne suffit jamais.** Son échéance **repart à la
> FIN de l'exécution** de l'unité déclenchée. L'intervalle entre deux activations
> vaut donc **`durée d'exécution + T_i`** — et la **durée d'exécution n'est pas
> dans l'objet de `L2`**. **`Δ ≥ T_i` n'implique donc PAS qu'une activation était
> due**, et le conclure serait un **faux positif** sur une unité `oneshot`.
>
> **Si plusieurs directives coexistent**, la condition n'est établie que si
> **l'une au moins** de celles marquées **OUI** la satisfait à elle seule.

> **Ce que `RE-5b` exige, et ce qu'elle certifie :**
>
> | Cas | Exigence | Ce qui est certifié |
> |---|---|---|
> | une activation est **établie DUE** | l'**`InvocationID` de `<unité-superviseur>` MUST avoir CHANGÉ** entre les deux prises | le régime **et le cycle** |
> | une activation **n'est PAS établie due** — quelle qu'en soit la raison | **aucun changement n'est exigé** | les **quatre premiers constats seulement**. **`RE-5b` MUST NOT certifier le cycle**, et **MUST le déclarer** |
>
> **Ce que cette clause NE prétend PAS.** Elle n'établit **aucune cadence** : un
> changement d'identifiant d'invocation atteste **qu'au moins une activation a
> eu lieu**, non qu'elles se sont succédé au rythme déclaré. **Deux prises ne
> rendent pas une cadence**, et la V6 avait déjà retiré cette prétention.

> **Corollaire opposable, porté par `RA-3`, et strictement borné.**
>
> **`RA-3` se déclenche** si une activation est **établie DUE** au sens
> ci-dessus **et** que l'`InvocationID` demeure **INCHANGÉ** : une activation qui
> devait avoir lieu n'a pas eu lieu.
>
> **`RA-3` MUST NOT se déclencher sur ce seul motif** lorsque l'activation
> **n'est pas établie due** — notamment sous `OnUnitInactiveSec` seul, ou sous
> `OnBootSec` seul. **Un identifiant d'invocation inchangé n'est alors pas une
> anomalie**, et le traiter comme telle produirait un `STOP` injustifié.

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

> **Clause — les DEUX autorisations du 2026-09-03 sont CONSOMMÉES.**
>
> | Autorisation | Exécution qu'elle a permise | État |
> |---|---|---|
> | celle du **matin** | `07:49:10Z` → `07:59:41Z`, sous V4 | **NON CLOSE** — §14 |
> | celle de **`10:0x`** | `10:06:53Z` → `10:11:05Z`, sous V8 | **NON CLOSE** — §14 |
>
> **Ni l'une ni l'autre ne couvre une réexécution**, ni en tout ni en partie.
>
> **Toute nouvelle tentative est soumise aux QUATRE conditions CUMULATIVES
> suivantes**, détaillées au §14.1 :
>
> | # | Condition |
> |---|---|
> | **1** | **AUDIT INDÉPENDANT DU DELTA** |
> | **2** | **INTÉGRATION** |
> | **3** | **AUTORISATION HUMAINE PROPRE ET NOUVELLE**, **postérieure aux DEUX** — l'audit et l'intégration —, **nommant explicitement `W4-R` ET sa version** |
> | **4** | **REJEU UNIQUE** — **une exécution par autorisation**, et une seule |
>
> **Ces quatre conditions sont le NOYAU COMMUN d'admissibilité, et non la
> totalité des exigences.** Elles **ne dispensent d'AUCUNE autre obligation du
> présent document**, et les **`MUST`** comme les **`MUST NOT`** du §10 demeurent
> **pleinement opposables** — notamment l'interdiction de déduire une
> autorisation de l'audit, de l'intégration ou du merge, et l'interdiction
> d'excéder le périmètre autorisé.
>
> **Le §8, le §10 et le §14.1 portent le MÊME noyau, mot pour mot.**

**L'autorisation, si elle est donnée, MUST :**

**Les quatre premières lignes sont le noyau commun du §8 et du §14.1, mot pour
mot. Les deux dernières sont les exigences de périmètre propres au présent §.**

| # | |
|---|---|
| **1** | être précédée d'un **AUDIT INDÉPENDANT DU DELTA** |
| **2** | être précédée de l'**INTÉGRATION** de la version auditée |
| **3** | être **explicite, distincte**, **postérieure aux DEUX** — l'audit et l'intégration —, et **nommer explicitement `W4-R` ET sa version** |
| **4** | ne permettre qu'un **REJEU UNIQUE** — **une exécution par autorisation**, et une seule |
| **5** | ne porter que sur les **TREIZE actes** de la liste close du §5 — **`L0` à `L12`** —, **dans l'ordre du §6**, et sur aucun autre |
| **6** | **ne porter aucune mutation**, d'aucune nature |

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
| **8** | les preuves **`RE-1`**, **`RE-1 bis`**, **`RE-2a`**, **`RE-2b`**, **`RE-2c`**, **`RE-3`**, **`RE-4`**, **`RE-5a`** et **`RE-5b`**, avec l'acte et le rang qui les ont produites |
| **8 ter** | pour **`RE-1 bis`** : l'état du puits — **découvert** ou **inexistant**. S'il a été découvert, les **deux empreintes** (rangs 10 et 13) **et la réserve de couverture partielle du §9.1, nommément** : la couverture court **de la découverte à la fin du lot**, et **jamais rétroactivement** |
| **8 bis** | la liste des **répétitions structurées** de `L0` et `L2` effectivement exécutées, avec leur horodatage et leur motif |
| **8 quater** | pour **`L5`**, et **OBJET PAR OBJET** — `O-a`, `O-b`, `O-c` — : **présence ou absence** · **taille, date et empreinte** si présent · **lecteur réellement employé** parmi les trois du §5.3, ou le constat qu'**aucun n'a rendu d'enregistrement** · le **motif** du repli s'il a été employé · la **concordance d'empreinte** avant et après rapatriement · la **validation applicable à sa nature** — quatre critères pour un conteneur plat, `c` et `d` seuls pour une base —, **satisfaite un par un**, dont la **taille écartée au titre de la minimalité** s'il y en a une · le **témoin retenu, son type, ce qui le rend indépendant** · et enfin **EXPLOITABLE ou INEXPLOITABLE sous ce lot**. **La validation de format et le constat d'absence de `BOOT_TIME`/`RUN_LVL` sont rapportés SÉPARÉMENT, pour chaque objet** |
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

## 14. Statut des exécutions du 2026-09-03 — **DEUX, toutes deux NON CLOSES**

> **Aucune des deux n'a valablement prononcé.** Leurs verdicts respectifs **ne
> sont pas retenus**, et **`P-A5` demeure `NON PRONONCÉE`** — ni en branche
> **(a)**, ni en branche **(b)**.

### Première exécution — `07:49:10Z` → `07:59:41Z`, sous `W4-R` V4

> **NON CLOSE.** `RA-1` **atteint et prononcé à l'homologation** : **`who -b`** a
> été employé au titre de `L5`, alors qu'il lit `/var/run/utmp` — la table
> **courante** — et non `/var/log/wtmp`. **Ce sont deux objets distincts**, et
> l'acte était donc **hors liste close**.

### Seconde exécution — `10:06:53Z` → `10:11:05Z`, sous `W4-R` V8

> **NON CLOSE.** Un **acte de lecture sur l'hôte a été exécuté APRÈS le rang 13**
> — une énumération des fichiers récemment modifiés, destinée à **corroborer
> `RE-4`**. **Aucun acte de `L0` à `L12` ne la prévoit**, le §9 produisant `RE-4`
> **par construction**.

**Trois critères sont consignés à ce titre, dans cet ordre :**

| Réf | Qualification | Motif |
|---|---|---|
| **`RA-1`** | **atteint** | *« un acte **hors liste close** du §5, ou hors de son rang au §6 »*. L'acte n'est prescrit par aucun des treize |
| **`RA-8`** | **atteint** | *« une frontière du §4 est franchie »* — le §4 interdit d'*« exécuter un acte **hors de la liste close du §5** »* |
| **`RA-6`** | **atteint, à titre SUBSIDIAIRE** | *« son périmètre serait excédé »*. L'autorisation portait *« exactement les actes `L0…L12` »* et *« aucun acte supplémentaire »*. Subsidiaire : il n'ajoute rien à `RA-1` et `RA-8`, mais il est **dû**, et l'omettre serait incomplet |

> **La sortie brute de l'acte litigieux est MANQUANTE** — elle n'a pas été figée.
> **Elle n'est pas recréée** : la recréer exigerait une nouvelle lecture de
> l'hôte.

> **Le prononcé de cette seconde exécution n'est PAS retenu.** Un `STOP` n'est
> pas un verdict — §8 —, et **un prononcé suivi d'un acte illicite ne clôt rien**
> — §6.3. **Le verdict n'est réécrit ni en branche (a), ni en branche (b) : il
> est SANS EFFET.**

### Portée des deux prononcés — **SANS EFFET**, sans réserve

> **Les deux prononcés sont SANS EFFET.** Un `STOP` n'est pas un verdict — §8 —,
> et un prononcé suivi d'un acte illicite ne clôt rien — §6.3. **Une exécution
> non close n'a pas prononcé valablement.**
>
> **`P-A5` demeure `NON PRONONCÉE`** — ni en branche **(a)**, ni en branche
> **(b)**.
>
> **Aucune « portée à arbitrer » ne subsiste.** Les versions antérieures
> renvoyaient la portée de ces verdicts à un arbitrage humain : **cette réserve
> est retirée**, car elle contredisait le constat d'absence d'effet. **Un verdict
> sans effet n'a pas de portée à arbitrer.**

**Ce que le présent lot fait, et ne fait pas :**

| | |
|---|---|
| il **corrige le lot** pour les tentatives **futures** | §5.3, §6.3, §9.3, §14.1 |
| il **ne corrige aucun des deux rapports terrain** | ils demeurent la **consignation d'exécutions NON CLOSES**, et **MUST NOT** être réécrits |
| il **ne rejoue rien** | aucune réexécution n'est autorisée — §14.1 |
| il **ne prononce pas `P-A5`** | et **ne réécrit aucun des deux verdicts**, ni en branche (a), ni en branche (b) |
| il **ne rouvre pas `G3`** | et **n'ouvre aucune `P-9`** |

> **Ce que les deux exécutions ont néanmoins produit, et qui demeure au
> dossier.** Leurs pièces figées — empreintes, relevés d'état, script du
> superviseur, définitions d'unité, `wtmp` — sont **conservées telles quelles**,
> et **ne sont ni détruites ni complétées**. Ce sont elles qui ont révélé les
> défauts que les versions V5 à V10 corrigent. **Une exécution non close peut
> instruire son propre lot ; elle ne peut pas prononcer à sa place.**

### 14.1 Ce qu'un NOUVEAU REJEU exigera

> **Aucun rejeu n'est autorisé par le présent document.** Ce qui suit énonce les
> conditions, il ne les remplit pas.

| # | Condition | Portée |
|---|---|---|
| **1** | **AUDIT DU DELTA** — la présente version, et **elle seule**, doit être auditée. L'audit porte sur **ce qui change depuis la V8**, non sur l'ensemble du lot | indépendant ; **l'exécutant ne peut pas auditer ce qu'il a produit** |
| **2** | **INTÉGRATION** — la version auditée doit être **intégrée au dépôt**, sur branche dédiée, avec fidélité byte-à-byte vérifiée | le merge demeure **humain** |
| **3** | **AUTORISATION HUMAINE PROPRE ET NOUVELLE** — explicite, distincte, **postérieure aux DEUX précédentes**, c'est-à-dire à l'**audit** et à l'**intégration**, **nommant explicitement `W4-R` ET sa version** | elle **MUST NOT** être déduite des **deux autorisations consommées du 2026-09-03** — §10, ni de l'audit, ni de l'intégration, ni du merge |
| **4** | **REJEU UNIQUE** — **une exécution par autorisation**, et une seule | un `STOP` **n'ouvre pas** un essai suivant : il exige **une nouvelle boucle complète**, des conditions 1 à 4. **Deux `STOP` ont déjà eu lieu** — §14 |

> **Les deux autorisations du 2026-09-03 sont CONSOMMÉES** — le §10 les
> énumère. **Aucune ne couvre un rejeu**, ni en tout ni en partie.
>
> **Ces quatre conditions sont le NOYAU COMMUN d'admissibilité, et non la
> totalité des exigences.** Elles **ne dispensent d'AUCUNE autre obligation du
> présent document**, et les **`MUST`** comme les **`MUST NOT`** du §10 demeurent
> **pleinement opposables** — notamment l'interdiction de déduire une
> autorisation de l'audit, de l'intégration ou du merge, et l'interdiction
> d'excéder le périmètre autorisé.
>
> **Le §8 et le §10 portent ce même noyau, mot pour mot**, et **aucun des trois
> ne l'allège**.

> **L'arbitrage humain qui avait levé la clause de rejeu du §8 était borné à la
> seconde exécution**, et **il est épuisé**. La clause de rejeu du §8 **reprend
> son plein effet, dans sa rédaction ACTUELLE** — c'est-à-dire les **quatre
> conditions cumulatives** ci-dessus, et non le seul test d'une *autorisation
> humaine nouvelle*, que les versions antérieures portaient et qui **n'est plus
> le texte du §8**.
>
> **Aucun retour à ce test isolé n'est possible.** Une autorisation nouvelle,
> **seule**, ne rend aucun rejeu admissible : les conditions **1**, **2** et
> **4** demeurent exigibles.

---

## 15. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture et bornage de `W4-R`, lot en **lecture stricte** instruisant la précondition `P-A5` de `G3`. Périmètre, deux verdicts exclusifs, liste close de neuf actes, ordre opposable, règle de décision à trois éléments cumulatifs avec clause d'exclusion concurrente, neutralisation du piège de l'absence, conduite en matière insuffisante, huit critères d'arrêt, restauration nulle prouvée par cinq preuves, autorisation **`NON DONNÉE`**. Aucun terrain, aucune exécution, aucune autorisation. |
| **2** | Après audit. Six blocages fermés et une règle de désambiguïsation ajoutée, sans terrain. `B1` : **`<journal-démon>`** entre comme source **`S7`** (§3.2) et comme acte **`L9`**, avec **rétention vérifiée avant exploitation**, conclusion **`SOURCE NON DISCRIMINANTE`** licite, et **interdiction d'attribuer par absence** — `U-3` demeure ouverte. `B2` : les preuves de non-mutation deviennent **exécutables** — trois actes les portent (`L1` empreintes de référence, `L2` état des **quatre** unités dont `<unité-démon>`, `L12` empreintes finales), et les **répétitions structurées** de `L0` et `L2` sont **explicitement autorisées**, sans quoi `RA-3` et `RA-4` étaient des critères sans moyen. `B3` : le **resserrement volontaire** par rapport à `G3` §6.1 (a) est **déclaré** — `B` demeure pivot obligatoire, et ce choix **peut produire `INSTANCE NON ATTRIBUABLE`** malgré une voie théoriquement suffisante. `B4` : nouveau **§7.1.1** — quatre origines concurrentes du redémarrage du pont, `F-13` en tête ; **`B` n'est qualifié que si les quatre sont exclues par preuve**, et **jamais par proximité temporelle**. `B5` : nouveau **§9.1** — la couverture d'empreinte du puits est **prouvée depuis sa découverte** et **déclarée ne pas couvrir ce qui précède**. `B6` : renvois et citations corrigés — autorisation **§10**, rang de l'instant **sans anticipation du verdict**, cadence sourcée sur **`P1-H` §4**, `W4-C` §9.1 **cité mot pour mot**. **Désambiguïsation `G.n`** posée au §0 et appliquée. **Autorisation toujours `NON DONNÉE`.** |
| **3** | Après réaudit. Sept blocages fermés, sans terrain. `R1` : la renumérotation de la V2 est **propagée au §7.1** — `A` sur **`L5`**, `B` et `C` sur **`L7`, `L10`, `L11`** seuls, et **`L9` expressément exclu** de `B` et de `C`, sa seule contribution licite étant de corroborer `A`. `R2` : le §6.2 déclarait le **rang 12 « sans objet »** quand `A` manque — **faux et grave**, ce rang portant `RE-2`, `RE-3` et `RE-5` ; une clause distingue désormais ce que l absence de fenêtre rend sans objet de ce qui **demeure obligatoire**, rangs **12 et 13** compris. `R3` : nouveau **§7.1.2** — `O1` ne s exclut **que par un enregistrement POSITIF** de l état de `<unité-démon>` ; **aucun observable n est inventé** ; si aucune voie licite n aboutit, **`O1` demeure ouverte, `B` est inqualifiable, le verdict est `INSTANCE NON ATTRIBUABLE`**, et les formules d atténuation sont nommément interdites. `R4` : décomptes corrigés — **treize actes `L0` à `L12`**, et le §10 les autorise **exactement**. `R5` : quatre renvois faux corrigés — **§7.1.1** (deux occurrences), **réserve n° 10**, **autorisation §10**, et **`G3` §6.1 (a)** cité avec son document. `R6` : **`RE-1 bis`** créée — le puits de `L7` sort de `RE-1`, avec sa **propre empreinte** et une **couverture depuis la découverte seulement**, alignée sur le §9.1. `R7` : les deux formulations fautives passent en **`MUST NOT`**. **Autorisation toujours `NON DONNÉE`.** |
| **4** | Après réaudit. Quatre blocages fermés, sans terrain. `RR1` : **`O3` était encore excluable par une absence** — le défaut que la V3 venait de corriger sur `O1`. Nouveau **§7.1.3** : `O3` ne s exclut que par un **enregistrement POSITIF daté dans la fenêtre**, portant l état de l installation ou les commandes de l exploitant ; à défaut **`O3` demeure ouverte, `B` est inqualifiable, le verdict est `INSTANCE NON ATTRIBUABLE`**. Le motif est sourcé : le dossier `G.2` est **démontrablement non exhaustif** — `A-5` place la fenêtre *hors campagne*, `A-1` consigne une **capture écrasée et non recréée** ; **un dossier qui a perdu une pièce ne prouve aucune absence**. `RR2` : **double négation supprimée au §5.2** — la formule disait le contraire de ce qu il fallait. `RR3` : **réserve 8 alignée sur le §7.1.2** — constat positif seul, `L9` sans contribution à `B`/`C`, `L10` adossée à une source non survivante, **seule `L11` peut potentiellement fermer `O1`** ; réserve **8 bis** ajoutée pour `O3`. `RR4` : **`RE-1 bis` propagée** — `L7`, `L12`, et sortie **8 ter** au §11 ; **clause de non-rétroactivité** ajoutée au §9.1, sans exception. **Autorisation toujours `NON DONNÉE`.** |
| **5** | **Lot CORRECTIF**, après audit d'homologation de l'exécution du 2026-09-03 — laquelle est **NON CLOSE**, `RA-1` atteint. Aucun terrain. `C1` : **`L5` était inexécutable comme écrit** ; l'**instant** est rattaché à **`L0`** — dédoublement de `A` en **`A₁`** instant et **`A₂`** caractère —, `L5` est recentré sur les enregistrements **persistants** et sur eux seuls, ses **lecteurs licites** et son **repli** sont nommés au nouveau **§5.3**, la **caractérisation complète du même objet** y est expressément autorisée avec **motif témoin obligatoire**, et `/var/run/utmp` comme `who` deviennent **interdits hors acte prévu** (§4). `C2` : **`RE-2` et `RE-5` étaient insatisfiables par construction** ; le modèle `R2a`/`R2b` de `w4p1-lot-terrain-borne.md` V3 est **transposé** en **`RE-2a`/`RE-2b`/`RE-2c`** et **`RE-5a`/`RE-5b`**, et l'exigence de **compteur de relances est retirée pour `<timer-guard>`**, où elle est **inapplicable**. `C3` : **`RA-3`** exclut désormais le **cycle nominal** du superviseur et de son timer, **toute variation non expliquée par ce cycle demeurant déclencheur**. `C4` : l'autorisation du 2026-09-03 est déclarée **CONSOMMÉE**, une **autorisation nouvelle** est exigée avant toute réexécution, et le nouveau **§14** consigne le statut de l'exécution passée **sans la réécrire**. **`P-A5` n'est pas prononcée. `G3` n'est pas rouvert. Aucune `P-9`.** |
| **6** | Après réaudit du correctif. Aucun terrain. `B1` : **la V5 laissait un démarrage ultérieur devenir silencieusement `A₁`** — nouveau **§7.1.0** : `L0` ne rend qu'un **instant candidat**, et une **clause d'identité à deux constats** vérifie qu'il correspond au redémarrage **étudié** du préflight `G.2` ; le constat (ii) est **positif**, fondé sur la continuité du temps de fonctionnement ; **à défaut, `A₁` demeure non établi** et **ne définit aucune fenêtre**. `B2` : **le motif témoin était circulaire** — il exigeait un `BOOT_TIME` pour valider un format dont l'objet peut n'en porter aucun ; le témoin **MAY être d'un autre type du même objet**, et la **validation structurelle** est **séparée** du **constat d'absence de `BOOT_TIME`/`RUN_LVL`**, qu'un parse structurellement validé **peut établir sans présupposer** que ces types existent. `B3` : **`L2` est étendue nommément** — état, sous-état, résultat, invocation, **`ActiveEnterTimestamp`**, relances pour les seules unités de service —, **`RE-5b` est réénoncée sur ce que les deux prises rendent réellement**, la **« cadence tenue » cesse d'être exigée**, et **`RA-3` ne s'oppose plus que sur les propriétés que `L2` relève**. `B4` : nouveau **§5.4** — **règle positive de bornage de l'exploitation** autour de la date du préflight, la caractérisation du §5.3 n'étant autorisée **que comme instrumentation** et **ne levant pas** ce bornage. **Propagations** : **`S3`** ne porte plus l'instant, seulement le **caractère / `A₂`** ; le **rang 4** nomme `RE-2a`, `RE-2b` et `RE-2c`. **Autorisation toujours `NON DONNÉE`. Exécution du 2026-09-03 toujours `NON CLOSE`. `P-A5` non prononcée. `G3` non rouvert.** |
| **7** | Après réaudit du correctif. Aucun terrain. `B1-a` : **le constat (ii) de la V6 était TAUTOLOGIQUE** — l'instant candidat étant dérivé du temps de fonctionnement, la vérification ne pouvait pas échouer ; **retiré**. Il est reconnu que **`L0` ne rend que le dernier démarrage**, et `A₁` n'est acquis que si celui-ci est rattaché **de façon univoque** au redémarrage étudié, par **`L4` ou `L5`** et **par aucune source ajoutée** ; **deux cas laissant `A₁` non établi sont nommés**, dont celui de **plusieurs redémarrages possibles dans le préflight**. `B1-b` : le §6.2, rang 7, **n'écrit plus que `A₁` est acquis au rang 2** — le rang 2 ne rend qu'un **candidat**, et la fenêtre n'existe qu'après la clause d'identité. `B2-a` : la **« séquence chronologique cohérente » est SUPPRIMÉE** comme critère — les enregistrements `utmp` étant **mis à jour en place**, le conteneur n'est pas ordonné, et ce critère aurait **rejeté le format réel** ; **aucun critère d'ordre n'est opposable**. `B2-b` : la validation structurelle repose sur **quatre critères cumulatifs** — **couverture intégrale**, **minimalité**, champ temporel, témoin indépendant — ; **un parse sautant un enregistrement sur deux MUST NOT être retenu**, et **aucun constat d'absence ne peut être fondé sur un parse partiel**. `B3` : nouveau **§9.2** — pour un lot couvrant **au moins une période du timer**, `RE-5b` exige un **changement positif de l'`InvocationID`** du superviseur ; **à défaut, `RA-3` se déclenche** ; les autres protections sont conservées et **aucune cadence n'est prétendue**. **`B4` non touché. Autorisation toujours `NON DONNÉE`. Exécution du 2026-09-03 toujours `NON CLOSE`. `P-A5` non prononcée. `G3` non rouvert.** |
| **8** | Après réaudit du correctif. Aucun terrain. **Blocage 1** : **`T` n'avait aucune source** — le §9.2 invoquait une *« période déclarée lue par `L8` »* que **`L8` ne lisait pas**, et la notion était **ambiguë**. **`L8` est étendu nommément** aux directives temporelles de `<timer-guard>` — `OnBootSec`, `OnStartupSec`, `OnActiveSec`, `OnUnitActiveSec`, `OnUnitInactiveSec`, `OnCalendar`, unité déclenchée et type de service —, sa colonne `Sert` propagée vers **`RE-5b`** et **`RA-3`**, et la **condition d'activation due est définie PAR MODE**. **Blocage 2** : **la V7 rendait à `L5` la capacité de porter des instants de démarrage**, que la V6 lui avait retirée — **contradiction interne** ; la condition (ii) du §7.1.0 **repose désormais sur `L4` SEUL**, ses **deux causes d'échec** sont nommées, **`L4` est propagé comme porteur de l'unicité de `A₁`**, et **`L5` ne porte aucun instant de démarrage, en aucune circonstance**. **Non bloquant** : la formule `Δ ≥ T` produisait un **faux positif sur un `oneshot`** — sous `OnUnitInactiveSec`, **l'échéance repart à la fin de l'exécution**, l'intervalle valant `durée + T_i` et la durée n'étant **pas dans l'objet de `L2`** ; la condition est réénoncée par mode, et **si une activation n'est pas établie due, `RE-5b` MUST NOT certifier le cycle et `RA-3` MUST NOT se déclencher sur ce seul motif**. **Autorisation toujours `NON DONNÉE`. Exécution du 2026-09-03 toujours `NON CLOSE`. `P-A5` non prononcée. `G3` non rouvert.** |
| **9** | **Lot correctif de REJEU**, après la **seconde exécution non close**. Aucun terrain. `C1` : **`/var/log/wtmp.db` entre dans le périmètre licite de `L5`**, sous la **même discipline** que les autres sources — présence **constatée** d'abord, lecture **seulement si le lot la prévoit** et **au seul titre de `L5`**, quatre critères et opération 2 séparée, **aucune extrapolation**, et son **absence ne fonde aucun constat**. La seconde exécution l'avait découvert et **s'était correctement abstenue** de le lire : **son abstention était juste, l'exclusion ne l'était pas**. `C2` : nouveau **§6.3, verrou de clôture** — le rang 13 comporte **trois opérations** et **c'est le dernier acte, sans exception** ; **la clôture n'existe qu'après le prononcé** ; **après elle, aucune lecture de l'hôte, aucune corroboration, aucun acte supplémentaire**, sous peine de **`RA-1` et `RA-8`** ; seules demeurent licites l'**analyse hors ligne** de la matière figée et la **rédaction du rapport**. `C3` : nouveau **§9.3** — **`RE-4` est satisfaite par construction, et cela SUFFIT** ; **aucune corroboration sur l'hôte** ne peut être entreprise à son sujet, *« une preuve établie par construction ne se vérifie pas »*. `C4` : le **§14 consigne DEUX exécutions non closes** — la première sur **`RA-1`** (`who -b`), la seconde sur **`RA-1`**, **`RA-8`** et, **subsidiairement**, **`RA-6`** ; **aucun de leurs prononcés n'est retenu**, et **leurs verdicts ne sont réécrits ni en branche (a) ni en branche (b)**. `C5` : nouveau **§14.1** — un rejeu exigera **audit du delta**, **intégration**, **autorisation humaine propre et nouvelle**, et **rejeu UNIQUE** ; les deux autorisations du 2026-09-03 sont **consommées**, et **l'arbitrage qui avait levé la clause de rejeu est épuisé**. **`P-A5` demeure `NON PRONONCÉE`. `P-9` demeure `NON DONNÉE`. `G3` demeure fermé.** |
| **10** | Après réaudit du correctif de rejeu. Aucun terrain. `B1-B4` : **le traitement de `/var/log/wtmp.db` était incohérent**. L'objet de `L5` est réénoncé en **trois objets nommés** — **`O-a`** `/var/log/wtmp`, **`O-b`** ses rotations, **`O-c`** `/var/log/wtmp.db` — sous une **discipline commune**, avec **les TROIS lecteurs du §5.3 et eux seuls** : **aucun quatrième lecteur n'est admis**. **Deux régimes de validation sont séparés** selon la **nature** de l'objet — les critères **`a`** et **`b`** sont **NON APPLICABLES** à une base de données, où ils n'ont pas de sens. À défaut de lecteur licite rendant des enregistrements, `O-c` est consigné **PRÉSENT mais INEXPLOITABLE SOUS CE LOT**, **sans improvisation**, et **aucun constat n'en est tiré** ; ce que cela laisse ouvert est **nommé sans être comblé**. Le **§11, sortie 8 quater**, rend désormais **OBJET PAR OBJET** : présence ou absence, taille, date, empreinte, **lecteur réellement employé**, validation applicable à la nature, et **EXPLOITABLE ou INEXPLOITABLE**. `B5-B6` : le **§14 se contredisait** — il déclarait les prononcés sans effet **et** renvoyait leur portée à un arbitrage ; les **deux prononcés sont SANS EFFET**, **`P-A5` demeure `NON PRONONCÉE`**, **aucune « portée à arbitrer » ne subsiste**, et les blocs **périmés et dupliqués sont fusionnés ou supprimés**. `B7-B8` : le **§8**, le **§10** et le **§14.1** portent désormais **le MÊME test d'admissibilité** — les **quatre conditions cumulatives** —, et les **DEUX autorisations du 2026-09-03 sont énumérées comme consommées**. `B9` : le **§6.3 est replacé après la fin réelle du §6.2**, les clauses **« rang 7 »** et **« `A₁` non établi rend sans objet »** y demeurant. **`P-A5` = `NON PRONONCÉE`. `P-9` = `NON DONNÉE`. `G3` inchangé.** |
| **11** | Après réaudit. Aucun terrain. **Trois blocages résiduels sur l'alignement du régime de rejeu.** **1** : la liste `MUST` du **§10** portait un test **plus faible** que le §14.1 — *« postérieure à l'audit »* au lieu de *« postérieure aux deux »*, *« nommer `W4-R` »* **sans sa version**, et **ni audit du delta, ni intégration, ni rejeu unique** ; elle porte désormais **les quatre conditions mot pour mot**, suivies de ses **deux exigences de périmètre**. **2** : la formule **« et à aucune autre »** neutralisait les garde-fous complémentaires ; elle est **supprimée partout**, les quatre conditions devenant le **NOYAU COMMUN** qui **ne dispense d'aucune autre obligation**, les **`MUST` et `MUST NOT` du §10 demeurant pleinement opposables** — notamment l'interdiction de déduire une autorisation de l'audit, de l'intégration ou du merge, et celle d'excéder le périmètre. **3** : le **§14.1 citait le §8 entre guillemets dans une rédaction qu'il ne porte plus** ; la **fausse citation est retirée**, le renvoi vise le **texte actuel**, et il est dit expressément qu'**aucun retour au test isolé de la seule « autorisation humaine nouvelle » n'est possible**. **Le §8, le §10 et le §14.1 portent désormais le même noyau, mot pour mot. `P-A5` = `NON PRONONCÉE`. `P-9` = `NON DONNÉE`. `G3` inchangé.** |
