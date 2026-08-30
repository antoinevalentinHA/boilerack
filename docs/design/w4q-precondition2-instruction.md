# `W4-Q` — instruction de la précondition 2 : le critère du §10.3.3 existe-t-il ?

> **Version 2**, après audit `NO-GO`. Un bloqueur fermé, quatre corrections
> locales. **La thèse est inchangée** : le critère exigé par §10.3.3 est
> matériellement absent.
>
> | | Correction |
> |---|---|
> | **V2 · B-1** | **§7.2 et §8 choix 3 rouverts.** La V1 déclarait `W4-Q` **normativement exclu** comme producteur du critère — *« **MUST NOT** »*, *« fait structurel »*, *« élimine d'emblée »*. C'était une **extension par la finalité** d'une clause qui nomme `W4-F1` et `W4-F2`, appliquée avec un standard **plus strict** que celui retenu au §7.1 pour le verrou du §10.7. Le §7.2 est reformulé **sur le modèle du §7.1**, et le choix 3 rouvre **trois** options sans en privilégier aucune |
> | **V2 · a** | **§10.2, clause `Sortie`, citée** : le critère devait être *« **écrit et figé** »*. La V1 ne citait que la question 5 |
> | **V2 · b** | **§3.3 corrigé** : `C1` porte **(a) ET (b)** — la V1 écrivait *« (a), et lui seul »*, en contradiction avec sa propre prémisse 3 du §6 |
> | **V2 · c** | **`w4f2-ouverture.md` ajouté comme TROISIÈME porteur** de la précondition 2, avec le motif de sa péremption (§5) |
> | **V2 · d** | **Réserve sur `C2` close** par la citation *« **figée avant terrain** »* du §8.5 |
>
> **Version 1.** Instruction initiale.

> **INSTRUCTION, PAS DÉCISION.** Ce document **établit sur pièces** et
> **soumet**. Il ne statue pas, ne fixe aucun seuil, n'amende aucun contrat, et
> ne requalifie aucune précondition.
>
> **Aucun code, aucune mesure, aucun terrain.** Aucune constante de site.
>
> Il s'appuie **exclusivement** sur des documents intégrés au dépôt.

---

## 1. Question posée

> **La précondition 2 du §10.3.1 — *« `W4-F1` clos, et son critère quantitatif de
> qualification disponible »* — est-elle satisfaite au sens MATÉRIEL ?**
>
> C'est-à-dire : existe-t-il aujourd'hui un critère **quantitatif**,
> **falsifiable**, **antérieur au terrain**, et **effectivement applicable** pour
> juger la coexistence ?

La question n'est pas de savoir ce que les documents **déclarent**. Elle est de
savoir ce qu'ils **contiennent encore**.

## 2. Chaîne documentaire exacte

Six maillons, tous intégrés, dans l'ordre où ils s'enchaînent.

| # | Source | Ce qu'elle pose |
|---|---|---|
| **1** | `w4f-write-sovereignty.md` **§10.2**, question 5 | `W4-F1` **MUST** répondre : *« quel **critère quantitatif falsifiable** `W4-F2` appliquera pour qualifier la coexistence (§10.3.3) »* |
| **1 bis** | `w4f-write-sovereignty.md` **§10.2**, clause **`Sortie`** | *« **Sortie** : les cinq réponses, étayées ; le **critère de §10.3.3, écrit et figé** ; et — seulement s'il a été jugé nécessaire — un réglage atteignable assorti de barrières falsifiables. »* C'est l'énoncé le plus direct de l'obligation : le critère devait être **écrit** et **figé**, non seulement défini |
| **2** | `w4f-write-sovereignty.md` **§10.3.3** | La **forme** exigée, et son producteur — voir §2.1 |
| **3** | `w4f-write-sovereignty.md` **§10.3.1**, précondition 2 | *« `W4-F1` clos, et son critère quantitatif de qualification disponible (§10.2) »* |
| **4** | `w4f-write-sovereignty.md` **§10.7** | *« `W4-F1 → W4-F2` : `W4-F2` ne peut commencer sans le critère de §10.3.3 »* |
| **5** | `w4f1-confirmation-window.md` **§8.5** | les trois critères `C1`, `C2`, `C3`, et l'état de leurs termes |
| **6** | `w4f2-ouverture.md` §2 · `w4f2-cloture.md` §6.2 · `w4f2-cadrage-cloture.md` §5.1.1 | l'état déclaré de la précondition 2, chez ses **trois** porteurs — voir §5 |

### 2.1 La forme exigée, mot pour mot

`w4f-write-sovereignty.md` §10.3.3 :

> **Clause.** *« Le résultat de W4-F2 **MUST NOT** être « marge mesurée ». Il
> **MUST** être « **marge mesurée, et déclarée conforme à un critère falsifiable
> fixé avant le terrain** ».*
>
> *Ce critère est **produit par W4-F1** (§10.2), pas par W4-F2 : **celui qui
> mesure ne doit pas fixer après coup le seuil qui le juge**. »*

Et, sur le contenu :

> *« Ce que W4-F0 impose, c'est la **forme** du critère : **falsifiable,
> quantitatif, antérieur au terrain, et portant au minimum sur la marge du
> superviseur face à son budget de 5 s et sur le coût observé d'une lecture en
> coexistence**. »*

**Deux objets minimaux** sont donc exigés, et ils sont nommés :

| | Objet minimal |
|---|---|
| **(a)** | la **marge du superviseur face à son budget de 5 s** |
| **(b)** | le **coût observé d'une lecture en coexistence** |

## 3. Ce qui existe matériellement, et qui est opposable

Trois critères sont nommés par la précondition telle que les clôtures la
renseignent — *« satisfaite — `C1`, `C2`, `C3` »*. Ils ne sont pas dans le même
état.

### 3.1 `C2` — **existe, complet, applicable en la forme**

`w4f1-confirmation-window.md` §8.5 :

```
p95(intervalle_publication, T2)  ≤  p95(T0)  +  ( p95(T0) − p50(T0) )
```

**Formule entière**, sans terme manquant. Le document assume ses trois choix de
politique — *« `p95` comme statistique de comparaison ; `p50` comme référence
basse de la dispersion ; et le coefficient **1** appliqué à l'écart »* —, et
pose un plancher de validité : chaque fenêtre **MUST** contenir au moins **100**
intervalles.

**Réserve d'applicabilité, non d'existence** : si `p95(T0) − p50(T0)` est du même
ordre que `p95(T0)`, *« **T0-D déclare alors `C2` non exploitable** »*. C'est une
condition d'exploitation, pas une absence de critère.

> **Objet couvert : la dégradation du pont historique.** Ni **(a)**, ni **(b)**.

### 3.2 `C3` — **existe, complet, applicable**

```
aucune mesure ne dépasse son fresh_max_s à aucun relevé de T2
et  chain.status reste nominal sur toute la fenêtre
et  chacun des huit rôles a produit au moins une lecture réussie
```

**Aucune constante libre** : *« `fresh_max_s` est déclaré par mesure dans C7 ; il
n'est pas inventé ici. »* Le document borne lui-même sa portée : *« **`C3` ne
protège pas le dispositif historique** et n'y prétend pas. Elle garantit
seulement que `C1` et `C2` n'ont pas été satisfaites par l'inaction. »*

> **Objet couvert : l'inaction de Boilerack.** Ni **(a)**, ni **(b)**.

### 3.3 `C1` — **la formule existe ; ses termes n'ont pas de valeur**

```
borne_sonde        =  max( bornes supérieures déterministes disponibles,
                           qualifiées sur la population des sondes du superviseur )
seuil_C1           =  budget_superviseur  −  borne_sonde
occupation_max(T1) ≤ seuil_C1      et      occupation_max(T2) ≤ seuil_C1
```

Le §8.5 renseigne l'état de chaque terme :

| Terme | État, cité |
|---|---|
| `budget_superviseur` | **5,000 s** — *« fait d'installation »* |
| `borne_sonde` | *« **aucune valeur admissible à ce jour** »* — inconnue `U-2` |
| `occupation_max` | *« **aucune source ne la fournit** »* — inconnue `U-7` |
| **`seuil_C1`** | **« non calculable »** — *« `borne_sonde` n'existant pas »* |

Et la conséquence est écrite dans le document lui-même :

> *« **Conséquence, assumée :** `borne_sonde` n'a **aucune valeur admissible**,
> donc **`seuil_C1` est non calculable**, donc **`C1` est non calculable**. Ce
> n'est pas un relâchement : une condition non calculable **ne peut pas être
> satisfaite**, et la condition 1 de `T0 GO` échoue. »*

> **Objets couverts : (a) ET (b).** `C1` est le seul contrat portant sur **(a)**,
> la marge du superviseur face à son budget — c'est le sens même de la
> soustraction `budget_superviseur − borne_sonde`. Et il porte **(b)**, le coût
> observé d'une lecture en coexistence, sous le nom de `occupation_max`.
>
> **`C1` porte donc, à lui seul, les deux objets minimaux du §10.3.3** — et
> aucun de ses deux termes propres n'a de valeur.

## 4. Valeurs retirées, et interdictions de substitution

Deux valeurs ont existé au dossier. **Aucune n'est employable**, et le corpus le
dit lui-même.

| Valeur | Statut | Source |
|---|---|---|
| **`seuil_C1 = 0,971 s`** | **RETIRÉE.** *« La V3 rabattait ce cas sur `seuil_C1 = 0,971 s`, valeur dérivée de la donnée non qualifiée `4,029 s`. **Ce repli est retiré** : il revenait à employer comme borne ce que le paragraphe précédent interdit précisément d'employer ainsi. »* | `w4f1` §8.5, correction V4 |
| **`borne_publique_C5 = 4,029 s`** | **REQUALIFIÉE en donnée de référence non qualifiée**, et **interdite** comme `borne_sonde` pour *« trois motifs cumulatifs »* : maximum empirique, population non qualifiée, et `C5` n'arrêtant *« aucun budget de production »* | `w4f1` §8.5 |

Le même §8.5 ferme la porte au repli :

> *« Si `T0-A` ne permet pas d'isoler les sondes du superviseur, alors aucune
> borne qualifiée n'existe, `borne_sonde` reste vide, et **`seuil_C1` demeure non
> calculable**. On ne fabrique **pas** une borne à partir d'un mélange
> pont/superviseur : une borne tirée de la mauvaise population n'est pas une
> borne conservatrice, c'est une borne fausse. »*

Et le document producteur déclare de lui-même, dans son bandeau de **Version 4** :

> *« Il **ne fixe aucun seuil**, **n'établit aucun régime**, et **ne rend `T0 GO`
> atteignable en rien** : `seuil_C1` devient **non calculable**, et la barrière
> reste fermée. »*

> **Le producteur désigné du critère déclare donc n'avoir fixé aucun seuil.**

## 5. Statut documentaire — trois porteurs, et leur dissymétrie

La précondition 2 est portée par **trois** documents intégrés, non deux. Aucun
des trois ne la requalifie.

| Document | Ce qu'il porte |
|---|---|
| **`w4f2-ouverture.md`** §2 | *« `W4-F1` clos, critère quantitatif disponible — **satisfaite** — `C1`, `C2`, `C3` ; **`seuil_C1 = 0,971 s` par défaut** »*. **C'est le porteur d'origine, et le seul qui NOMME la valeur** |
| **`w4f2-cloture.md`** §6.2 | la **même mention, sans la valeur, et sans note**. L'en-tête du tableau précise : état repris *« **sans requalification** »* |
| **`w4f2-cadrage-cloture.md`** §5.1.1 | la même mention, **sans la valeur**, **et avec** la note : *« La valeur par défaut que cette cellule citait a été **retirée** depuis, par la **Version 4 de `w4f1-confirmation-window.md`** […] ; `seuil_C1` est aujourd'hui **non calculable**. **Ce lot ne requalifie pas la précondition pour autant** »* |

### 5.1 Pourquoi la valeur de `w4f2-ouverture.md` est périmée, et non autoritative

**Périmée** : la valeur qu'elle nomme, `seuil_C1 = 0,971 s`, est **exactement**
celle que `w4f1-confirmation-window.md` a **retirée** en Version 4 — *« Ce repli
est retiré : il revenait à employer comme borne ce que le paragraphe précédent
interdit précisément d'employer ainsi. »* `w4f2-ouverture.md` est **antérieur** à
ce retrait, et sa cellule n'a pas été mise à jour.

**Non autoritative** : le document se borne lui-même dans son propre en-tête —
*« Il **ne redéfinit pas** W4-F2. Sa définition, ses préconditions, ses critères
`ABORT` et son verrou vers W4-F3 restent ceux de `w4f-write-sovereignty.md`
§10.3. »* Il **rapporte** un état, il ne le **constitue** pas. La valeur qu'il
cite tirait son autorité de `w4f1`, et `w4f1` la lui a retirée.

> **Cette péremption ne se propage pas d'elle-même.** Aucun lot n'a mis à jour la
> cellule de `w4f2-ouverture.md`, et le présent document **ne la met pas à jour**
> non plus : ce serait requalifier.

### 5.2 La dissymétrie, décrite fidèlement

Elle n'oppose pas une mention pleine à une mention vidée. Les trois portent la
**même** mention *« satisfaite »*. Elles diffèrent sur ce qui l'accompagne :

| | Mention | Valeur citée | Note de retrait |
|---|---|---|---|
| `w4f2-ouverture.md` | oui | **oui**, `0,971 s` | non |
| `w4f2-cloture.md` | oui | non | **non** |
| `w4f2-cadrage-cloture.md` | oui | non | **oui** |

Les trois s'abstiennent de requalifier, et le troisième le dit expressément.

> **Aucun des trois ne prétend que le critère est matériellement disponible.**
> Ils **reprennent un état** ; l'un cite une valeur qui n'existe plus, et un
> autre signale précisément qu'elle a été retirée.

## 6. Démonstration de l'absence matérielle

L'absence porte sur **le critère au sens du §10.3.3**, non sur l'ensemble des
contrats.

**Prémisse 1.** §10.3.3 exige que le critère porte **au minimum** sur **(a)** la
marge du superviseur face à son budget de 5 s **et** sur **(b)** le coût observé
d'une lecture en coexistence. Le « au minimum » est conjonctif : les deux objets
sont requis.

**Prémisse 2.** Des trois contrats nommés, **`C2` couvre la dégradation du pont**
et **`C3` l'inaction de Boilerack**. Ni l'un ni l'autre ne porte sur **(a)** ou
**(b)** — leurs propres textes bornent leur objet, `C3` explicitement.

**Prémisse 3.** **`C1` est le seul contrat portant sur (a)**, et sa formule
contient **(b)** sous le nom de `occupation_max`. Or `seuil_C1` est déclaré **non
calculable** par le document producteur, et `occupation_max` est *« sans
source »*.

**Prémisse 4.** Aucune substitution n'est admise : le repli a été **retiré**, et
la donnée de référence est **interdite** comme borne.

> **Conclusion.** Les **deux** objets minimaux exigés par §10.3.3 reposent
> aujourd'hui sur des grandeurs **sans valeur admissible et sans source**. Le
> critère exigé par §10.3.3 **n'existe donc pas matériellement**, quand bien même
> deux des trois contrats qui devaient le composer existent et sont applicables.

**Ce que cette conclusion ne dit pas** : elle ne dit pas que `C2` et `C3` sont
défaillants — ils ne le sont pas. Elle ne dit pas que la précondition 2 est
« fausse » — les clôtures la portent telle qu'elles l'ont reçue, sans
requalifier. Elle dit que **le contenu que la précondition suppose disponible ne
l'est plus**, et que **personne ne l'a encore constaté dans un document
opposable**.

**Une réserve de lecture, désormais close par le corpus lui-même.** `C2` a sa
formule fixée d'avance, mais ses valeurs de référence (`p50`, `p95`) sont
relevées en `T0-C` : on pouvait se demander si un tel critère satisfait
*« antérieur au terrain »*.

`w4f1-confirmation-window.md` §8.5 tranche, et en ces termes : ***« `C2` est une
politique conservatrice site-relative, figée avant terrain — et non une
dérivation. »*** Le corpus qualifie donc lui-même `C2` de **figée avant
terrain**. La réserve est **close**, et `C2` satisfait ce point de forme.

**Cela ne déplace pas la conclusion**, qui porte sur `(a)` et `(b)` — objets que
`C2` ne couvre pas.

## 7. Conséquences exactes

### 7.1 Pour le verrou du §10.7

`w4f-write-sovereignty.md` §10.7 : *« `W4-F1 → W4-F2` : `W4-F2` ne peut commencer
sans le critère de §10.3.3. »*

`coexistence-cadrage-successeur.md` §3 rappelle que cette clause **nomme
`W4-F2`**, non un chantier successeur, et propose que `W4-Q` s'y tienne *« comme
s'il le liait »* — **règle conservatrice**, dont *« l'applicabilité formelle
relève d'une décision humaine »*.

| Lecture | Conséquence pour `W4-Q` |
|---|---|
| **Le verrou lie `W4-Q`** (règle conservatrice retenue) | **`W4-Q` ne peut pas commencer.** Le blocage est antérieur aux cinq conditions préalables à `T0` du cadrage §6 |
| **Le verrou ne lie pas `W4-Q`** (lecture littérale : il nomme `W4-F2`) | `W4-Q` peut commencer, mais **la condition 4 du cadrage §6 reste bloquante** — la dissymétrie doit être statuée —, et il ne pourrait pas **conclure** : son critère de clôture exige de statuer sur les préconditions |

> **Dans les deux lectures, `W4-Q` ne peut pas aller jusqu'à une issue terminale
> sans que la question du critère soit tranchée.** Les lectures diffèrent sur le
> moment du blocage, non sur son existence.

### 7.2 Qui peut produire le critère — une question de même nature que le §7.1

§10.3.3 : *« Ce critère est **produit par `W4-F1`**, pas par `W4-F2` : **celui qui
mesure ne doit pas fixer après coup le seuil qui le juge**. »*

**La clause nomme `W4-F1` et `W4-F2`.** Elle ne nomme pas de chantier successeur.
L'étendre à `W4-Q` serait une extension **par la finalité**, exactement de la
même nature que celle discutée au §7.1 pour le verrou du §10.7 — et elle doit
donc recevoir **le même traitement**.

| Lecture | Conséquence pour `W4-Q` |
|---|---|
| **La clause s'étend à `W4-Q`** — sa finalité, *« celui qui mesure ne doit pas fixer après coup le seuil qui le juge »*, vise un **rôle**, et `W4-Q` tiendrait ce rôle | le critère devrait venir d'un **autre** producteur que `W4-Q` |
| **La clause ne s'étend pas** — lecture littérale : elle nomme `W4-F1` et `W4-F2` | `W4-Q` pourrait produire le critère, **sous réserve d'une garantie d'indépendance restant à définir**, faute de quoi la finalité de la clause serait contournée sans avoir été écartée |

> **La finalité plaide fortement pour l'indépendance du seuil**, et le §10.3.3 la
> motive sans détour. **Mais l'applicabilité formelle de la clause à `W4-Q`
> relève d'un arbitrage humain**, et le présent document ne la tranche pas.
>
> **Une extension par la finalité ne peut pas être appliquée ici avec un standard
> plus strict qu'au §7.1.** La V1 le faisait — elle écrivait `MUST NOT` là où le
> §7.1 laissait deux lectures ouvertes. C'est corrigé.

### 7.3 Pour la précondition 2

Elle demeure **portée « satisfaite » dans les deux clôtures**, et **le présent
document ne la requalifie pas** : la requalifier est une décision humaine, listée
comme telle par `w4q-ouverture.md` §7.1.

Ce qui est établi ici est plus étroit, et c'est tout ce qui est établi : **le
contenu matériel qu'elle suppose disponible ne l'est pas.**

## 8. Choix normatifs soumis à l'humain

Aucun n'est tranché ici. Ils ne sont pas exclusifs entre eux, sauf indication.

| # | Choix | Ce qu'il engage |
|---|---|---|
| **1** | **Statuer sur la précondition 2** : la maintenir « satisfaite », la requalifier, ou la déclarer **partiellement satisfaite** — `C2` et `C3` disponibles, `C1` non | c'est la décision que le présent document instruit sans la prendre |
| **2** | **Décider si le verrou du §10.7 lie `W4-Q`** — règle conservatrice, ou lecture littérale | détermine si `W4-Q` peut commencer, ou seulement conclure |
| **3** | **Désigner qui produira le critère manquant.** Trois voies, **aucune privilégiée ici** : **(i)** `W4-Q` producteur, **avec une garantie d'indépendance à définir** — le §7.2 dit pourquoi elle serait nécessaire ; **(ii)** **réouverture de `W4-F1`**, producteur désigné par le §10.2 ; **(iii)** **lot distinct** producteur du critère, ni `W4-F1` ni `W4-Q`. Le choix suppose d'avoir tranché l'extension du §7.2 | gouvernance |
| **4** | **Décider du sort de l'objet (a)** — la marge du superviseur face à son budget — sachant que le contrat qui le porte n'est pas calculable et qu'aucune substitution n'est admise | c'est le nœud ; les autres choix en dépendent |
| **5** | **Décider si le contenu minimal du §10.3.3 est amendable**, et par quel lot — un amendement relève d'un **lot distinct, audité séparément** | le cadrage l'interdit à `W4-Q` |
| **6** | **Renoncer**, en prononçant l'une des issues terminales | demeure ouvert, et n'est pas un échec |

> **Ce que je ne fais pas, et ne ferai pas sans décision.** Je ne fixe aucun
> seuil, je n'emploie aucune valeur retirée ou interdite, je n'amende aucun
> contrat, et je ne requalifie aucune précondition.

## 9. Ce que ce document ne fait pas

Il **ne statue pas**, **ne requalifie pas** la précondition 2, **ne fixe aucun
seuil**, **n'amende aucun contrat**, **ne tranche pas** l'applicabilité du verrou
du §10.7, **n'ouvre aucune phase**, **n'autorise pas `T0`**, et **ne prononce
aucune issue terminale**.

Il établit sur pièces, et soumet.

## 10. Historique de révision

| Version | Objet |
|---|---|
| **1** | Instruction initiale. Aucune décision prise. |
| **2** | Après audit `NO-GO`. Bloqueur `B-1` fermé : §7.2 reformulé sur le modèle du §7.1, et choix 3 du §8 rouvert en trois voies sans préférence. Quatre corrections locales : clause `Sortie` du §10.2 citée ; `C1` porte **(a) ET (b)** ; `w4f2-ouverture.md` ajouté comme troisième porteur, avec le motif de sa péremption ; réserve sur `C2` close par *« figée avant terrain »*. **Thèse inchangée, aucune décision prise.** |
