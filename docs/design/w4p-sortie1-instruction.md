# `W4-P` — sortie 1 : instruction analytique de `(a)` et `(b)`

> **Version 2**, après audit `NO-GO`. Deux bloqueurs fermés, six réserves
> traitées.
>
> | | Correction |
> |---|---|
> | **V2 · B1** | **Citation retirée.** La V1 attribuait à `coexistence-cadrage-successeur.md` un **§7.6** qui **n'existe pas** — ce document n'a qu'un §7, « Homologation des constats produits hors corpus ». La phrase citée provient en réalité d'un document **NON INTÉGRÉ**. La pièce réelle est **`w4f2-cadrage-cloture.md` V3 §5.1**, et elle dit l'inverse : l'amputation de `T0-C` était une **erreur d'une version antérieure**, **corrigée dans le corpus** — non une proposition vivante à réfuter |
> | **V2 · B2** | **État de `U-2` corrigé.** La V1 présentait la borne déterministe comme sans moyen. **C'est faux** : le corpus **désigne un chemin** — `T0-A` / `T0-C` / `T0-D` — actuellement **non autorisé** et d'**issue non garantie**. §3.2, §3.3, §3.5, §6 et la synthèse sont repris |
> | **V2 · R-1** | la voie qui découle est énoncée pour `(a)` et `(b)`, **avec son motif**, sans arbitrer au-delà de ce que les faits imposent |
> | **V2 · R-2** | la **voie d'instrumentation `M6`** du §8.3 est nommée : *« mesure de premier choix »* si elle est possible sans modifier le dispositif historique |
> | **V2 · R-3** | la **tension** entre le chemin désigné et le cadre *« Boilerack arrêté »* de `T0` est exposée pour `U-7`, **et non tranchée** |
> | **V2 · R-4** | les **gates de `T0-C`** sont nommées : neuf préconditions du §10.3.1, `U-3`, issue non garantie |
> | **V2 · R-5** | `coexistence-cadrage-successeur.md` **§6.1** est cité et instruit sur l'autorisation de terrain |
> | **V2 · R-6** | durcissements corrigés : *« identiques »* → **« exactement cet objet »** ; *« n'existe pas »* → **« n'existe pas encore »** |
>
> **Version 1.** Instruction initiale.

> **INSTRUCTION, PAS DÉCISION.** Ce document **établit sur pièces** et
> **soumet**. Il ne produit aucun critère, ne fixe aucun seuil, ne tranche aucune
> voie, ne définit ni n'autorise aucune expérience.
>
> **Aucun terrain, aucune mesure, aucun code, aucun amendement.** Aucune constante
> de site. **`T0` demeure NON AUTORISÉ.**
>
> Il s'appuie **exclusivement** sur des documents intégrés au dépôt.

---

## 1. Objet

`coexistence-cadrage-lot-critere.md` §7 fixe la première sortie de `W4-P` :

> *« pour **(a)** et pour **(b)** séparément : ce qui est établissable, ce qui ne
> l'est pas, et la voie du §3.1 qui en découle, **avec son motif** »*

Et son §9.3 impose d'instruire, avant toute expérience touchant `U-1`, trois
questions de recouvrement avec `T0-B`.

> **Le présent document rend cette sortie 1**, et instruit **trois**
> recouvrements — celui que le cadrage nomme, et **deux** qu'il ne nomme pas.

## 2. Rappels normatifs, tous opposables

| Réf | Ce qui est posé |
|---|---|
| `w4f-write-sovereignty.md` **§10.3.3** | le critère porte **au minimum** sur **(a)** la marge du superviseur face à son budget de 5 s **et (b)** le coût observé d'une lecture en coexistence |
| `w4f1-confirmation-window.md` **§8.5** | `R` = durée totale d'invocation ; `O` = occupation. **Seule relation établie : `O ≤ R`**. Une mesure de `R` peut **majorer** `O` ; elle **MUST NOT** servir à la **minorer** |
| `w4f1` **§8.5** | *« `C1` est une borne déterministe, pas une politique probabiliste […] Seule une **borne supérieure** du coût de la sonde y entre »* |
| `w4f1` **§8.2** | **`T0` s'exécute Boilerack ARRÊTÉ** : *« `T0` ne présente donc aucun risque nouveau »* |
| `w4p-ouverture.md` **§6** | **clause de non-dérivation, adoptée et opposable** : la règle est figée **avant** le terrain qui lui fournira ses valeurs |

> **Trois objets à ne jamais confondre**, et c'est le fil de tout ce qui suit :
>
> | | Objet | Ce qu'il est |
> |---|---|---|
> | **valeur empirique** | ce qu'une mesure rend | un relevé, sur un échantillon fini |
> | **borne déterministe** | ce que `§8.5` exige | une **majoration démontrée**, valable au-delà de l'échantillon |
> | **règle normative** | ce que `§10.3.3` exige | l'énoncé qui **juge** une valeur, figé avant elle |
>
> **Une mesure de durée ne vaut pas démonstration d'une borne.** Le corpus l'a
> déjà tranché en écartant `4,029 s` : *« c'est un **maximum empirique** d'un
> petit jeu de mesures, **et non une borne supérieure démontrée** »*.

## 3. Objet `(a)` — la marge du superviseur face à son budget de 5 s

### 3.1 Ce qui est établissable aujourd'hui

**Un seul terme** : `budget_superviseur = 5,000 s`, que `w4f1` §8.5 donne comme
**fait d'installation**.

La **marge** est la différence entre ce budget et le coût propre de la sonde.
**Ce coût n'est pas établi.**

### 3.2 Par quel moyen le reste serait établissable

`w4f1` §9 décrit `U-2` comme **deux choses** :

> *« durée réelle d'une sonde du superviseur (`M6`), **et borne supérieure
> déterministe de cette durée, qualifiée sur la population des sondes** »* —
> `PREUVE TERRAIN / SOURCE EXTERNE REQUISE`, ***« aucun substitut admis »***.

> **Le corpus DÉSIGNE un chemin pour les deux moitiés.**
> `w4f2-cadrage-cloture.md` **§5.1** — *« Le chemin existe, il est désigné, et il
> n'est pas ouvert »* — l'établit en trois actes de `T0` :

| Acte | Ce qu'il fait, cité |
|---|---|
| **`T0-A`** | *« caractérise les sources et **désigne celle qui servira à `C1`** »*. Il porte **`U-3`**, dont la table des inconnues dit qu'elle *« **conditionne la calculabilité de `C1`** »* |
| **`T0-C`** | établit *« **en outre**, et **seulement si la population des sondes du superviseur est réellement isolable** »* par `T0-A`, **une borne supérieure de leur coût** — *« jamais une borne tirée d'un mélange pont/superviseur »* |
| **`T0-D`** | *« calculabilité, résolution et temps de réaction — c'est lui qui décide si `C1` et `C2` sont calculables »* |

> **Une seconde voie est nommée par le corpus, et elle est de premier choix.**
> `w4f1` §8.3 : *« **Si l'exploitant peut instrumenter `M6` sans modifier le
> dispositif historique, il SHOULD le faire : c'est la mesure de premier
> choix.** Sinon, elle reste manquante, et le protocole en tient compte plutôt
> que de la simuler. »*

### 3.2.1 Les gates qui s'appliquent à ce chemin

| Gate | État |
|---|---|
| **`T0` non autorisé** | `w4f2-cloture.md` §1 : *« L'ouverture de `T0` n'est pas autorisée »* ; aucun acte postérieur ne l'a autorisée |
| **Les neuf préconditions du §10.3.1** | *« Toutes exigibles avant la première intervention. Aucune n'est facultative »* — et `w4f2-cadrage-cloture.md` V3 rappelle que **sept ne sont pas satisfaites** : une partielle, cinq non établies, une `NON DONNÉE` |
| **`U-3`** | préalable **interne** : sans capacité du journal établie par `T0-A`, `T0-D` ne peut conclure |
| **Issue non garantie** | `w4f2-cadrage-cloture.md` §5.1 : *« même ouvert, `T0-A` peut ne pas isoler la population — et alors `borne_sonde` reste vide »* |

> **Un fait qui pèse sur `U-3`, sans la trancher.** `w4f2-ouverture.md` §2,
> précondition 6, établit que le journal du démon *« ne porte que les ouvertures
> de connexion, **sans clôture ni attribution par client** »*. Ce constat porte
> sur **cette source-là** ; il ne dit pas qu'aucune autre ne pourrait servir, et
> **c'est `T0-A` qui a mandat de caractériser les sources**.

### 3.3 Ce qui n'est pas établi aujourd'hui

**La borne supérieure déterministe** — et, avec elle, la marge.

> **« Non établi » n'est pas « non établissable ».** Le chemin du §3.2 existe et
> est désigné. Ce qui manque n'est pas un moyen : c'est **l'autorisation de
> l'emprunter**, et la certitude qu'il aboutisse.

### 3.4 Pourquoi — deux obstacles, et une vigilance

**Obstacle 1 — le chemin n'est pas autorisé.** `T0` demeure non autorisé, et sept
des neuf préconditions du §10.3.1 ne sont pas satisfaites (§3.2.1).

**Obstacle 2 — l'issue n'est pas garantie.** `w4f2-cadrage-cloture.md` §5.1 le
dit sans détour : *« même ouvert, `T0-A` peut ne pas isoler la population — et
alors `borne_sonde` reste vide »*. Le §8.5 ajoute que *« le repli de secours a
été **retiré** »* : il n'existe pas de valeur de rattrapage.

> **Vigilance — et elle n'est pas un obstacle de plus.** Le §8.5 a écarté
> `4,029 s` comme *« maximum empirique […] **et non une borne supérieure
> démontrée** »*, et interdit le quantile. **Une durée relevée n'est donc pas, en
> soi, une borne.**
>
> **Mais ce n'est pas au présent document de dire ce que `T0-C` produirait.** Le
> corpus lui assigne d'établir *« une borne supérieure de leur coût »*, et
> désigne **`T0-D`** comme l'organe qui *« décide si `C1` et `C2` sont
> calculables »*. **La qualification de ce qui sortirait de `T0-C` appartient à
> `T0-D`, qui n'a pas eu lieu.**

> **Une piste SUPPLÉMENTAIRE, ni écartée ni instruite : une borne dérivée d'un
> MÉCANISME.** Elle serait déterministe par construction. **L'instruire exigerait
> de lire la configuration de l'installation** — un constat de terrain qui devrait
> être **homologué** avant d'être opposable. Ce n'est pas fait ici. Elle vient
> **en plus** du chemin désigné, non à sa place.

### 3.5 Quelle voie en découlerait — sans la trancher

| Voie | Ce que `(a)` exigerait d'elle |
|---|---|
| **maintenir** | il faudrait parcourir le chemin désigné — `T0-A` puis `T0-C`, sous `T0-D` — ou instrumenter `M6` au sens du §8.3. **Cette voie n'est pas fermée** ; elle est **conditionnée** à une autorisation qui n'existe pas et à une isolabilité qui n'est pas acquise |
| **reformuler** | il faudrait exprimer la marge en termes d'une grandeur établissable sans déplacer ce que le critère rejette — et le moyen de vérifier ce non-déplacement **n'existe pas encore** (cadrage §3.2) |
| **amender** | il faudrait modifier ce que le §10.3.3 exige de **(a)**. Gouvernance la plus lourde, et la seule où rien n'est déplacé en silence |

> **La voie qui découle des faits, pour `(a)` : AUCUNE n'est imposée, et ce
> constat est lui-même le résultat.**
>
> Les faits n'excluent aucune des trois. Ce qu'ils imposent est **un ordre** : le
> choix dépend de **l'isolabilité de la population des sondes**, que seul `T0-A`
> peut établir. **Tant qu'elle est inconnue, choisir une voie serait choisir sans
> le fait dont elle dépend.**
>
> Le cadrage §3.3 pose que la voie **découle** de ce qui est établissable. Ici,
> ce qui est établissable dépend d'un acte non autorisé — **et c'est cela, la
> réponse**.

## 4. Objet `(b)` — le coût observé d'une lecture en coexistence

### 4.1 Ce qui est établissable aujourd'hui

**Une seule relation** : **`O ≤ R`**, que `w4f1` §8.5 donne comme *« seule
relation établie »*, en précisant que *« leur différence est inconnue, leur
égalité éventuelle aussi »*.

### 4.2 Par quel moyen le reste serait établissable

`R`, temps mural d'une invocation, est mesurable **en principe** — mais mesurer
`R` **de Boilerack** exige de faire tourner Boilerack **en coexistence** (§5.3).

> **Et `R` ne donne pas la grandeur du contrat.** `w4f1` §9 décrit `U-7` comme
> l'occupation `O` *« pour une lecture **et pour une rafale** »*, et `§8.5` définit
> `occupation_max` comme l'occupation **cumulée vue par une sonde**. Un `R`
> par invocation majore l'occupation **d'une** invocation ; il ne majore pas un
> **cumul**.

### 4.3 Ce qui n'est pas établissable

**`occupation_max`** — l'occupation cumulée vue par une sonde, rafale comprise.

### 4.4 Pourquoi — trois motifs distincts

**Motif 1 — la rafale n'est bornée par aucun facteur constant.** `w4f1` §6.3 :
*« **Aucun facteur constant ne borne la rafale** ; au-delà de `30/7`, elle n'est
bornée que par la saturation. »* Un plafond par invocation ne borne donc pas le
cumul.

**Motif 2 — une réserve du corpus porte sur l'atteignabilité même.**
`w4f2-cloture.md` §5 consigne que `w4f2-c1-amendement.md` §9(4) *« note qu'elle
pourrait être non seulement non mesurée, mais **non bornable de façon
déterministe dans la configuration actuelle** »* — **point non établi et non
tranché**.

> **Cette réserve est portée ici explicitement, et elle n'est pas mineure.** Si
> elle se confirmait, elle porterait sur l'**atteignabilité** d'un terme du
> contrat, non sur sa mesure — et **aucune campagne ne la lèverait**. Elle doit
> être instruite, dans un sens ou dans l'autre, avant qu'une expérience visant
> `(b)` puisse être dite utile.

**Motif 3 — la mesure exige une exposition.** Voir §5.3.

### 4.5 Quelle voie en découlerait — sans la trancher

| Voie | Ce que `(b)` exigerait d'elle |
|---|---|
| **maintenir** | il faudrait borner l'occupation **cumulée** — alors que le motif 1 écarte tout facteur constant, et que le motif 2 met en doute qu'elle soit bornable |
| **reformuler** | même difficulté qu'en `(a)` : le moyen de vérifier le non-déplacement **n'existe pas encore** |
| **amender** | il faudrait modifier ce que le §10.3.3 exige de **(b)** |

> **La voie qui découle des faits, pour `(b)` : AUCUNE n'est imposée non plus —
> mais l'ordre y est différent de `(a)`.**
>
> Pour `(a)`, le préalable est l'**isolabilité**. Pour `(b)`, il est la
> **réserve du motif 2** : si l'occupation cumulée n'était pas bornable de façon
> déterministe, la voie *maintenir* tomberait — non par manque de mesure, mais
> par impossibilité de l'objet. **Cette réserve est non établie et non tranchée**,
> et elle doit l'être avant que la voie puisse être choisie.
>
> S'y ajoute la tension du §5.3, qui porte sur la possibilité même de mesurer.

## 5. Les trois recouvrements

### 5.1 `U-1` / `T0-B` — les trois questions du cadrage

**Question 1 — l'objet visé est-il réellement distinct de `T0-B` ?**

> **Non — le corpus assigne à `T0-B` exactement cet objet.** `w4f1` §8.2 :
> *« examine leurs recouvrements et **en déduit le régime de concurrence de
> `vcontrold` — `U-1`**, sans exposer Boilerack »*. Le **chevauchement est donc
> substantiel**, et le cadrage §9.3 le qualifiait déjà ainsi.
>
> Cela ne dit pas que toute expérience concevable sur `U-1` **serait** `T0-B` :
> une expérience de méthode différente pourrait viser le même objet autrement.
> **Mais l'objet, lui, est celui de `T0-B`.**

**Cette réponse est établie sur pièces.** Les deux suivantes ne le sont pas.

**Question 2 — quelle autorisation est requise ?**

Trois lectures, **aucune retenue** :

| | Lecture | Ce qu'elle suppose |
|---|---|---|
| **i** | l'autorisation de `T0` s'applique | qu'un acte identique ne change pas de nature en changeant de chantier |
| **ii** | une autorisation propre à `W4-P` suffit | qu'il faut alors **dire pourquoi** le même acte échappe aux conditions de `T0` |
| **iii** | les deux sont requises | position la plus conservatrice |

**Question 3 — le résultat vaudrait-il `T0-B` pour `W4-Q` ?**

| Si | Alors |
|---|---|
| **oui** | `W4-P` aurait exécuté une phase de `T0` — ce que le cadrage §9.3 interdit d'obtenir par renommage |
| **non** | le travail devrait être **rejoué** sous les conditions de `T0`, et l'expérience de `W4-P` n'aurait servi qu'à elle-même |

> **Dans les deux branches, trancher avant d'agir est nécessaire** — et le
> cadrage le pose déjà : *« Tant que ces trois questions ne sont pas tranchées,
> aucune expérience touchant `U-1` ne peut être bornée valablement. »*

### 5.2 `M6` / `T0-C` — recouvrement substantiel, non traité par le cadrage

`w4f1` §8.2 assigne à **`T0-C`**, outre la référence statistique :

> *« T0-C établit **en outre**, et **seulement si la population des sondes du
> superviseur est réellement isolable** (T0-A), **une borne supérieure de leur
> coût** — jamais une borne tirée d'un mélange pont/superviseur. »*

> **Le recouvrement est substantiel.** Mesurer `M6` pour établir le coût de la
> sonde recouvre le second volet de `T0-C`, y compris sa condition
> d'isolabilité.

**Ce volet est bien en vigueur, et le corpus a corrigé une erreur qui l'avait
retiré.** `w4f2-cadrage-cloture.md`, bandeau de la **Version 3**, consigne parmi
ses deux corrections : *« le §5.1 **amputait `T0-C` de sa fonction de borne
supérieure de coût**, ainsi que du **repli du §8.5** qui s'applique si `T0-A`
n'isole pas la population »*.

> **C'était une erreur d'une version antérieure, et elle a été corrigée.** Ce
> n'est **pas** une proposition vivante qu'il faudrait réfuter. Le **§5.1 de
> `w4f2-cadrage-cloture.md`**, dans sa version en vigueur, rétablit `T0-C` dans
> sa fonction — et c'est cette version qui fait foi.

**Gates applicables** : celles du §3.2.1 — `T0` **non autorisé**, les **neuf**
préconditions du §10.3.1 dont sept ne sont pas satisfaites, **`U-3`**, et une
**issue non garantie**.

> **Le cadrage n'avait pas nommé ce recouvrement.** Il est nommé ici, et il
> appelle le même traitement que celui du §5.1 : **trois questions de même
> forme**, à instruire avant qu'une expérience visant `M6` puisse être bornée.
>
> **Et il faut ajouter la voie du §8.3** : si `M6` est instrumentable **sans
> modifier le dispositif historique**, le corpus la donne pour *« la mesure de
> premier choix »*. Que cette voie relève ou non de `T0-C` — et donc de ses
> gates — **fait partie des questions à instruire**.

### 5.3 `U-7` / `T1` — au-delà de `T0`, et circulaire

`w4f1` §8.2 définit le cadre de `T0` : *« Boilerack est **arrêté**. `T0` ne
présente donc aucun risque nouveau. »* Et §8.7 définit `T1` : *« **exposition
courte** »*, douze minutes, quatre cycles du superviseur.

> **Mesurer l'occupation de Boilerack en coexistence exige de le faire tourner en
> coexistence.** Ce n'est donc **pas** une activité de `T0` — c'est,
> substantiellement, **une exposition au sens de `T1`**.

**Et la circularité doit être dite.** `w4f1` §8.7 pose que `T1 GO` exige, entre
autres, que ***« `C1` est satisfaite » sur la totalité de `T1`***. Or `C1` est
précisément ce qui manque.

> **Une expérience visant `(b)` ne peut donc pas être conduite *comme* `T1`** :
> la barrière de `T1` exige le critère que l'expérience doit aider à produire.
> Et la conduire **sous un autre nom** serait exactement le renommage que le
> cadrage interdit.

### 5.3.1 Une tension du corpus, exposée et non tranchée

`w4f2-cadrage-cloture.md` §5.1 désigne **`T0-A` / `T0-C` / `T0-D`** comme le
chemin qui lèverait **`U-2` ET `U-7`**.

Or `w4f1` §8.2 pose que **`T0` s'exécute Boilerack arrêté**, et `U-7` est
l'occupation **de Boilerack**.

> **La tension est réelle, et le présent document ne la résout pas.** Deux
> lectures se présentent, et aucune n'est retenue :
>
> | | Lecture | Ce qu'elle suppose |
> |---|---|---|
> | **i** | `T0` établit ce qu'il peut de `U-7` **sans exposer** — par exemple la caractérisation des sources qui la mesureraient plus tard | que `U-7` soit « levée » au sens de *rendue mesurable*, non de *mesurée* |
> | **ii** | le chemin désigné vise `U-2`, et `U-7` n'y figure que par extension | que la désignation soit moins large que sa lettre |
>
> **Trancher entre les deux n'appartient pas à ce lot** : il faudrait dire ce que
> le corpus a voulu, et cela relève de l'arbitrage. **La tension est signalée pour
> qu'elle ne soit pas franchie sans être vue.**

### 5.3.2 Une exposition hors `T1` — et l'autorisation qu'elle supposerait

L'ouverture du terrain en principe contemple des expériences pour `W4-P`. Une
exposition conduite **hors du cadre de `T1`**, sur une base explicitement
distincte et avec ses garanties propres, est donc **concevable** — mais elle
devrait être **déclarée comme telle**, avec les six éléments exigés, et **ne
jamais être présentée comme un `T1`**, ni comme en tenant lieu.

> **Et la question de l'autorisation reste ouverte, le corpus le dit déjà.**
> `coexistence-cadrage-successeur.md` **§6.1** — *« L'autorisation de terrain —
> une question ouverte, non un héritage »* — établit que le §11.2 est intitulé
> *« Autorisation `W4-F2` »*, qu'il *« se borne lui-même »* — *« **propre à
> `W4-F2`** […] **uniquement dans le cadre de `W4-F2`** »* —, et conclut :
> *« **`§11.2` n'est donc pas transposable** […] Ce qui est acquis est seulement
> ceci : **la question existe**, elle est **préalable**, et une autorisation de
> terrain **ne peut pas être réputée acquise par héritage**. »*
>
> Le §6.1 pose trois lectures — extension explicite du §11.2, autorisation neuve,
> ou précondition 9 sans objet — et **n'en retient aucune**. **Elles valent pour
> `W4-P` comme pour le chantier successeur**, et le présent document ne les
> tranche pas davantage.

## 6. Ce que cette instruction établit, en synthèse

| | `(a)` | `(b)` |
|---|---|---|
| **Établi aujourd'hui** | le budget, `5,000 s` | la relation `O ≤ R` |
| **Chemin désigné** | **oui** — `T0-A` / `T0-C` / `T0-D`, `w4f2-cadrage-cloture.md` §5.1 ; **plus** l'instrumentation `M6` du §8.3, *« mesure de premier choix »* | **désigné par la même clause**, mais **en tension** avec le cadre *« Boilerack arrêté »* de `T0` — §5.3.1 |
| **État du chemin** | **non autorisé**, et **issue non garantie** | idem, **plus** la tension ci-dessus |
| **Condition interne** | **`U-3`** et l'**isolabilité** de la population des sondes | la **réserve** sur la bornabilité déterministe, **non établie et non tranchée** |
| **Recouvrement** | `M6` / `T0-C` — **substantiel** | `U-7` / `T1` — **au-delà de `T0`**, et la barrière de `T1` exige `C1` |
| **Piste supplémentaire** | une borne dérivée d'un **mécanisme**, non instruite | — |

> **Ce que cette instruction établit, et rien de plus.**
>
> **Pour les deux objets, un chemin est désigné par le corpus.** Aucun des deux
> n'est donc « sans moyen ». Ce qui manque est de même nature dans les deux cas :
> **une autorisation qui n'existe pas, et une condition interne qui n'est pas
> acquise** — l'isolabilité pour `(a)`, la bornabilité pour `(b)`.
>
> **Et pour `(b)` s'ajoute une tension du corpus** entre le chemin désigné et le
> cadre de `T0`, que ce document expose sans la résoudre.
>
> **Aucune voie n'est imposée par les faits**, et c'est le résultat de la
> sortie 1 : le choix dépend de conditions que seuls des actes non autorisés
> peuvent établir.

## 7. Ce qui est soumis à l'humain

Aucun de ces points n'est tranché ici.

| # | Point |
|---|---|
| **1** | la **voie** — maintien, reformulation, amendement — pour `(a)` et pour `(b)`. **Les faits n'en imposent aucune** ; ils imposent l'**ordre** (§3.5, §4.5) |
| **2** | les **questions 2 et 3** du recouvrement `U-1` / `T0-B` (§5.1) |
| **3** | le traitement du recouvrement **`M6` / `T0-C`**, que le cadrage n'avait pas nommé — **y compris** si la voie d'instrumentation du §8.3 en relève (§5.2) |
| **4** | la **tension** entre le chemin désigné et le cadre *« Boilerack arrêté »* de `T0`, pour `U-7` (§5.3.1) |
| **5** | le statut d'une **exposition hors `T1`** pour `(b)`, et l'**autorisation de terrain** que `coexistence-cadrage-successeur.md` §6.1 laisse expressément ouverte (§5.3.2) |
| **6** | l'**instruction de la réserve** sur la bornabilité de `U-7` — préalable à toute expérience la visant (§4.4) |
| **7** | l'opportunité d'**instruire la piste du mécanisme** pour `(a)`, qui exigerait un constat de terrain homologué (§3.4) |
| **8** | l'**ouverture de `T0`**, dont dépendent les points 1 à 3 et 6 — décision distincte, non prise |

## 8. Ce que ce document ne fait pas

Il **ne produit aucun critère**, **ne fixe aucun seuil**, **ne tranche aucune
voie**, **ne définit ni n'autorise aucune expérience**, **n'amende aucun
contrat**, **ne lève aucune inconnue**, **n'autorise pas `T0`**, et **ne prononce
aucune issue** au sens du §8 du cadrage.

Il rend la sortie 1, et s'arrête là.

## 9. Historique de révision

| Version | Objet |
|---|---|
| **1** | Instruction initiale de la sortie 1. Aucune décision prise. |
| **2** | Après audit `NO-GO`. `B1` : citation fabriquée retirée — le §7.6 invoqué n'existe pas, et la phrase venait d'un document non intégré ; la pièce réelle est `w4f2-cadrage-cloture.md` V3 §5.1, qui **corrige** l'amputation de `T0-C` comme erreur antérieure. `B2` : l'état de `U-2` est rétabli — **un chemin est désigné**, non autorisé, d'issue non garantie. `R-1` à `R-6`. **Aucune voie choisie, aucune décision prise.** |
