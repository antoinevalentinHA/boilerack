# Cadrage — le plus court chemin de clôture de `W4-F2`

> **Version 5**, après réaudit. Une seule correction : au §10, un « six » avait
> survécu à la correction de décompte de la V4, la substitution ayant porté sur la
> ligne suivante. **Rien d'autre ne change.**
>
> **Version 4**, après réaudit. Quatre corrections de précision : le décompte des
> préconditions, qui confondait « non établie » et « `NON DONNÉE` » ; le retrait
> de toute idée d'ordre entre elles ; l'attribution du retrait de la valeur par
> défaut ; et l'ordre de l'historique. **Aucune autre modification.**
>
> **Version 3**, après réaudit. Deux corrections. La V2 réduisait l'ouverture de
> `T0` à la seule **Précondition 9**, alors que `w4f-write-sovereignty.md` §10.3.1
> en exige **neuf, toutes exigibles, aucune facultative** — et que **sept** ne sont
> pas satisfaites : une partielle, cinq non établies, une `NON DONNÉE`. Et le §5.1
> amputait `T0-C` de sa fonction de **borne supérieure de coût**, ainsi que du
> **repli du §8.5** qui s'applique si `T0-A` n'isole pas la population.
> **Thèse centrale inchangée.**
>
> **Version 2**, après audit. La correction principale porte sur le §5 : le lot
> y généralisait à tout le corpus une négation que
> `w4f2-c1-amendement.md` §9(5) borne expressément **« par ce lot »**. Le chemin
> vers `U-2` et `U-7` **est** désigné — c'est `T0-A` / `T0-C` / `T0-D` — mais il
> **n'est pas autorisé**, Précondition 9 / §11.2 étant `NON DONNÉE`, et il est
> **conditionné à `U-3`**. La correction est propagée aux §6 et §10. Cinq
> corrections mineures suivent. **La thèse centrale est inchangée : `W4-F2` est
> clôturable `NON QUALIFIABLE` au plafond actuel, et `W4-F3` reste
> inadmissible.**
>
> **Version 1.** Lot de cadrage documentaire. Il détermine, **à partir du corpus
> seul**, ce qui empêche encore la qualification, ce qui serait strictement
> nécessaire pour la lever, et si `W4-F2` peut être clos proprement comme
> **`NON QUALIFIABLE`** au plafond de preuve actuel. Aucun acte de preuve n'est
> exécuté. Aucun hôte, aucun runtime, aucun terrain, aucun `debug`, aucune
> mutation.

---

## 1. Objet et frontières

Ce document **n'établit aucun fait nouveau**. Il relit le corpus déjà intégré et
en tire ce qui s'y trouve déjà, mais dispersé : la structure exacte du blocage.

Il **ne prend aucune décision**. La clôture d'un chantier est un acte de
gouvernance ; le §9 dit à qui il revient. Il n'amende aucun contrat, ne rouvre
aucun arbitrage clos, n'ouvre ni `Acte B`, ni `T0` / `T1` / `T2`, et **ne propose
aucune instrumentation**.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.**

---

## 2. Ce qui empêche la qualification — trois conditions, pas une

`w4f2-c1-amendement.md` §6, Q5, énumère les cinq conditions de `T0 GO` et leur
état après amendement. **Trois bloquent aujourd'hui.**

| # | Condition | État | Bloquante |
|---|---|---|---|
| 1 | `C1`, `C2`, `C3` calculables | **`C1` non calculable** — `U-2` et `U-7` | **oui** |
| 2 | résolution de la source de `C1` | **non évaluable** — le seuil ne l'est pas | **oui** |
| 3 | cadences et budget du §8.6 | inchangé | non |
| 4 | régime compatible avec `C1` | **`INDÉTERMINÉ`** | **oui** |
| 5 | aucune inconnue structurante | inchangée | non |

Le même §6 tire lui-même la conséquence, et elle est le pivot de tout ce lot :

> *« Sous un `ADDITIF` établi, la 4 tomberait et **1 et 2 subsisteraient**. »*

---

## 3. La démonstration décisive — aucune branche ne rend `T0 GO`

`w4f1-confirmation-window.md` §8.2.1, repris par `w4f1a-vcontrold-concurrency.md`
§2 et reconstruit sur le texte amendé par `w4f2-c1-amendement.md` §6 :

| Branche | `T0-B` rend | Sortie contractuelle |
|---|---|---|
| **A** | `ADDITIF` | **`W4-F2 NON QUALIFIABLE — STOP`**, aucun `T1` |
| **B** | `NON ADDITIF` | **`T0 NO-GO — STOP`** |
| **C** | `INDÉTERMINÉ` | **`W4-F2 NON QUALIFIABLE — STOP`**, aucun `T1` — **état actuel** |

> **Les trois branches s'arrêtent. Aucune ne rend `T0 GO`.**

Et l'amendement précise que la branche **A** n'a pas seulement conservé sa sortie
en changeant de motif — *« d'une impossibilité arithmétique à une insuffisance de
données »* (Q2) — mais qu'elle **ne désigne plus aucune suite** : l'encadré qui la
désignait a été retiré en V4, *« la désignation reposait sur l'arithmétique
retirée »* (§4, ligne 12 de la matrice).

---

## 4. Ce qui n'est **pas** nécessaire — et le corpus le dit déjà

> **Établir le régime ne change pas le résultat de `W4-F2`.**

C'est une conséquence directe du §3 : `Q2` et `Q3` rendent **la même sortie**.
Passer de la branche **C** à la branche **A** — ce que l'obtention du **maillon
2** permettrait au mieux — fait changer le **motif**, pas la **sortie**.

`w4f2-ouverture.md` §4 l'avait déjà écrit sans détour :

> *« Réduire encore `H3` ou `H6` … ferait au mieux passer l'état de la branche C
> à la branche A. La branche A est **également** `NON QUALIFIABLE` … »*

**Sont donc des réductions d'incertitude, non des nécessités :**

| Objet | Ce que sa levée changerait |
|---|---|
| **maillon 2** — transitions 1 et 2 | ferait tomber la condition 4 ; **1 et 2 subsisteraient** |
| `H1` | idem — contribue au régime, rien de plus |
| `H2`, et donc `H6` **(b)** | idem |
| `H6` **(c)**, chemins restants | idem |
| `H6` **(a)** terme 2 — conformité du pont à `A5` | idem |

> **Aucune de ces cinq levées ne touche les conditions 1 et 2.** Elles portent
> toutes sur le **régime** ; les conditions 1 et 2 portent sur la
> **calculabilité de `C1`**. Ce sont deux ordres distincts, et c'est pourquoi
> aucune instrumentation ne peut qualifier `W4-F2`.

**Conséquence pratique, à énoncer sans détour :** un Acte B, une activation de
`debug`, une mesure sur l'hôte — tout cela serait du **travail réel sur `H3` et
`H6`**, et **sans effet sur la qualifiabilité**. `w4f2-ouverture.md` §5.3 le
disait déjà ; les **six** lots intégrés depuis n'ont fait que le confirmer.

---

## 5. Ce qui serait strictement nécessaire — et ce n'est pas **un** fait

Les conditions **1** et **2** subsistent sous tout régime, et la **2 dérive de la
1** : elle n'est pas évaluable tant que `seuil_C1` ne l'est pas. La nécessité se
réduit donc à la condition **1** — mais elle ne se réduit pas à **un fait**.

| Inconnue | Ce qu'elle exige | Statut |
|---|---|---|
| **`U-2`** — `borne_sonde` | borne supérieure **déterministe**, **qualifiée sur la population des sondes du superviseur**, hors exposition Boilerack | `PREUVE TERRAIN / SOURCE EXTERNE REQUISE` · **sans substitut admis** |
| **`U-7`** — `occupation_max` | l'occupation cumulée `O` imposée à une sonde | `PREUVE TERRAIN / SOURCE EXTERNE REQUISE` |

> **Il n'y a donc pas « un unique fait supplémentaire ». Il y en a deux**, et il
> faut le dire plutôt que de forcer l'énoncé : `seuil_C1 = budget_superviseur −
> borne_sonde` et `occupation_max(T1|T2) ≤ seuil_C1` mobilisent **deux grandeurs
> indépendantes**, dont aucune n'est dérivable de l'autre.

**Et une réserve du corpus pèse sur la seconde.** `w4f2-c1-amendement.md` §9(4) :
`U-7` *« pourrait être non seulement non mesurée, mais **non bornable de façon
déterministe dans la configuration actuelle** »* — puisque `O ≤ R`, que `R` est
bornée par `read_timeout_s + ε`, et que **`ε_aval` n'est pas bornée par le code**.
Le même §9 précise que ce point **n'est pas établi** et que rien ne conclut à
l'impossibilité. **Il n'est pas tranché ici non plus.**

### 5.1 Le chemin existe, il est désigné, et il n'est pas ouvert

`w4f2-c1-amendement.md` §9(5) énonce que le chemin qui lèverait `U-2` et `U-7`
*« n'est **pas** désigné **par ce lot** »*. **La borne « par ce lot » est dans le
texte**, et elle change tout : c'est une limite de périmètre de l'amendement, non
un constat d'absence dans le corpus.

**Le corpus, lui, désigne le chemin.** `w4f1-confirmation-window.md` l'établit en
trois actes de `T0` :

| Acte | Ce qu'il fait |
|---|---|
| **`T0-A`** | caractérise les sources et **désigne celle qui servira à `C1`**. Il porte l'inconnue **`U-3`** — *« capacité réelle du journal `vcontrold` : clôture, durée, attribution par client »* — dont la table des inconnues dit qu'elle **« conditionne la calculabilité de `C1` »** |
| **`T0-C`** | référence statistique — distribution des intervalles de publication vue d'aval, dont `p50(T0)` et `p95(T0)` alimentent `C2` et `E3`. Il établit **en outre**, *« et seulement si la population des sondes du superviseur est réellement isolable »* par `T0-A`, **une borne supérieure de leur coût** — *« jamais une borne tirée d'un mélange pont/superviseur »* |
| **`T0-D`** | **calculabilité, résolution et temps de réaction** — c'est lui qui décide si `C1` et `C2` sont calculables |

> **Le chemin désigné porte sa propre condition d'échec, et il faut la dire.**
> `w4f1-confirmation-window.md` §8.5 : *« **Si `T0-A` ne permet pas d'isoler les
> sondes du superviseur**, alors aucune borne qualifiée n'existe, `borne_sonde`
> reste vide, et **`seuil_C1` demeure non calculable**. On ne fabrique **pas** une
> borne à partir d'un mélange pont/superviseur : une borne tirée de la mauvaise
> population n'est pas une borne conservatrice, c'est une borne fausse. »*
>
> Et le repli de secours a été **retiré** : la correction V4 du même §8.5 supprime
> le rabattement sur une valeur dérivée d'une donnée non qualifiée, *« il revenait
> à employer comme borne ce que le paragraphe précédent interdit précisément
> d'employer ainsi »*. **Ouvrir `T0` ne garantit donc pas d'obtenir `borne_sonde`.**

**L'état exact est donc celui-ci, et non une absence :**

| | |
|---|---|
| chemin | **désigné** — `T0-A` / `T0-C` / `T0-D` |
| ouverture | **hors d'atteinte — et pas pour une seule raison** (§5.1.1) |
| préalable interne | **conditionné à `U-3`** — sans capacité du journal établie par `T0-A`, `T0-D` ne peut conclure à la calculabilité de `C1` |
| issue non garantie | même ouvert, `T0-A` peut ne pas isoler la population — et alors `borne_sonde` reste vide |

#### 5.1.1 Ouvrir `T0` n'est pas lever une autorisation

> **La V2 réduisait l'ouverture de `T0` à la Précondition 9. C'est faux.**

`w4f-write-sovereignty.md` §10.3.1 exige **neuf préconditions**, et l'énoncé est
sans latitude : *« Toutes exigibles avant la première intervention. Aucune n'est
facultative. »* La Précondition 9 en est **une**, non le verrou unique.

État repris de `w4f2-ouverture.md` §2, **sans requalification par ce lot** :

| # | Précondition | État |
|---|---|---|
| 1 | W4-F0 intégré et clos | **satisfaite** |
| 2 | W4-F1 clos, critère quantitatif disponible | **satisfaite** — `C1`, `C2`, `C3`. *La valeur par défaut que cette cellule citait a été **retirée** depuis, par la **Version 4 de `w4f1-confirmation-window.md`**, portée par le lot `w4f2-c1-amendement.md` ; `seuil_C1` est aujourd'hui **non calculable**. Ce lot ne requalifie pas la précondition pour autant* |
| 3 | Boilerack configuré, surface transactionnelle fermée | **non établie** — rien n'est déployé |
| 4 | preuve, sur le fichier déployé, qu'aucune écriture n'est émissible | **non établie** |
| 5 | pont et superviseur dans leur état nominal | **partiellement établie** — observé : aucune campagne autorisée ne les a arrêtés ni modifiés ; **non observé** : leur exécution réelle |
| 6 | observabilité sur les quatre composants | **non établie** — source disponible n'est pas observabilité établie ; Boilerack : **inexistante** |
| 7 | rollback de déploiement lecture seule disponible | **non établi** |
| 8 | exploitant physiquement présent, plan de reprise connu | **non établi** |
| 9 | autorisation humaine du §11.2 | **`NON DONNÉE`** |

> **Deux satisfaites, une partielle, cinq non établies, une `NON DONNÉE`.**
> Ouvrir `T0` ne consiste donc pas à obtenir une signature. Il faudrait satisfaire
> **toutes** celles qui ne le sont pas : **déployer Boilerack en surface
> fermée**, **prouver la fermeture sur le fichier déployé**, **établir
> l'observabilité des quatre composants**,
> **disposer d'un rollback**, **organiser une présence physique**, **établir
> l'état nominal observé** et **obtenir l'autorisation du §11.2**. **Le §10.3.1
> n'ordonne rien entre elles** : il les exige toutes. **C'est un chantier, pas un
> acte.**

> **Ce n'est pas une nuance de forme.** Dire « aucun chemin n'existe » ferait de
> la clôture une fatalité technique. Dire « le chemin est désigné et non ouvert »
> en fait ce qu'elle est : une **décision**. Le plafond atteint est un **plafond
> au périmètre autorisé**, non un plafond du possible.

### 5.2 Appui direct du corpus

`w4f2-regime-instruction.md` §17 — *« Aucun glissement vers `U-2` / `U-7` »* —
porte déjà la discrimination du §4 dans les termes de ce lot :

> *« **Même si `ADDITIF` était établi, `T0` resterait bloqué par `U-2` et `U-7`**
> (conditions 1 et 2 de `T0 GO`). **Les deux problèmes sont distincts et ne se
> compensent pas.** »*

---

## 6. Réponse à la question posée

> **Oui. `W4-F2` peut être clos proprement comme `NON QUALIFIABLE` au plafond de
> preuve actuel, sans chercher à obtenir le maillon 2 par instrumentation.**

Trois raisons, toutes tirées du corpus et non de ce lot :

1. **`NON QUALIFIABLE` n'est pas un échec de méthode : c'est la sortie
   contractuelle** de la branche C, prononcée par `w4f1-confirmation-window.md`
   §8.2.1. L'état actuel *« n'est pas choisi : c'est la valeur que `T0-B` prend »*
   (`w4f1a` §2).
2. **L'instrumentation ne le changerait pas** (§4). Chercher le maillon 2 pour
   clore serait chercher à changer un motif, pas une sortie.
3. **Ce qui le changerait — `U-2` et `U-7` — passe par un chemin désigné mais
   hors d'atteinte** (§5.1) : `T0-A` / `T0-C` / `T0-D`, dont l'ouverture exige
   **les neuf préconditions du §10.3.1** — *« toutes exigibles … aucune n'est
   facultative »* — dont **cinq sont non établies, une partielle et une
   `NON DONNÉE`** (§5.1.1). S'y
   ajoutent le conditionnement à `U-3` et le fait que, même ouvert, `T0-A`
   pourrait ne pas isoler la population (§8.5). **Le plafond est donc celui du
   périmètre atteignable** — et il est atteint : aucun acte **autorisé** ne reste
   à mener.

> **`clos` et `qualifié` sont deux états distincts, et le corpus les distingue
> déjà.** `w4f-write-sovereignty.md` §10.3.4 pose trois conditions séparées à
> l'admissibilité de `W4-F3` : *« `W4-F2` est **clos** ; la coexistence a été
> **qualifiée** ; le critère de §10.3.3 est satisfait »*. Un chantier peut donc
> être clos sans avoir été qualifié — **et c'est exactement l'état atteignable
> aujourd'hui.**

---

## 7. Le coût de la clôture, à porter devant l'arbitre

Il serait malhonnête de présenter cette clôture comme sans conséquence.

`w4f-write-sovereignty.md` §10.3.3 fixe la **preuve de sortie** de `W4-F2` :
Boilerack actif en lecture et publiant, pont historique toujours écrivain et
nominal, mesures de coexistence relevées, critère de `W4-F1` déclaré satisfait ou
non. **Une clôture au plafond ne produit aucune de ces quatre pièces** — elles
supposent toutes le terrain que `T0 GO` conditionne.

| Conséquence | État |
|---|---|
| deuxième condition du §10.3.4 — *« la coexistence a été qualifiée »* | **non tenue** |
| **`W4-F3`** | demeure **inadmissible** |
| Précondition 9 / §11.2 | demeure **`NON DONNÉE`** |
| pont historique | demeure l'**unique écrivain réel** de production |
| surface transactionnelle | demeure **sans autorité**, `false` |

> **Aucune sûreté n'est affaiblie, et aucune exposition n'est ouverte.** La
> clôture consigne un arrêt qui est déjà en vigueur ; elle ne l'assouplit pas.
> `w4f2-c1-amendement.md` §7 le vérifiait déjà pour l'amendement : *« Même arrêt,
> aucune exposition rendue possible. »*

---

## 8. Ce qui devra rester nommé ouvert

Une clôture ne referme pas ce qui n'est pas fermé. Le lot de clôture devra
énumérer, **sans les requalifier** :

| Ouvert | État à consigner |
|---|---|
| **maillon 2** — transitions 1 et 2 | non prouvé ; fait d'**exécution**, hors de portée documentaire |
| `H1` | `PARTIEL` |
| `H2` | `PARTIEL` ; absorbe le résidu **(b)** de `H6` |
| `H6` | `PARTIEL` — `RÉDUITE, NON CLOSE` ; **(a)** terme 1 **fermé**, terme 2 **ouvert** ; **(c)** cas « non résolue » **écarté sur l'installation**, autres chemins ouverts |
| `H3` | `PARTIEL` — transitions 3 et 5 **établies sous corroboration**, 1 et 2 ouvertes |
| `U-2`, `U-7` | `PREUVE TERRAIN / SOURCE EXTERNE REQUISE` ; chemin **désigné** — `T0-A` / `T0-C` / `T0-D` — mais **hors d'atteinte** : sur les neuf préconditions du §10.3.1, **deux satisfaites, une partielle, cinq non établies, une `NON DONNÉE`** ; conditionné à `U-3` ; issue non garantie (§5.1, §5.1.1) |
| `A6` | source de niveau 2 **jamais consommée** ; privée |
| **`U-3`** | `PREUVE TERRAIN / SOURCE EXTERNE REQUISE` — `T0-A` ; conditionne la calculabilité de `C1` |

---

## 9. La séquence documentaire minimale de clôture

**Trois étapes, dont une seule est un lot à produire.** Aucune n'exige de terrain,
d'instrumentation ni de mesure.

| # | Étape | Nature | Qui |
|---|---|---|---|
| 1 | **le présent cadrage**, audité et intégré | il **constitue** le constat de plafond ; aucun lot supplémentaire n'est requis pour l'établir | chaîne documentaire |
| 2 | **arbitrage de gouvernance** — **poursuivre, suspendre ou abandonner** | **acte humain non substituable.** `w4f2-ouverture.md` §5.2 énonce ces trois options, nomme la voie *« disponible dès maintenant »* et rappelle qu'elle *« ne fabrique pas `T0 GO`, ne lève aucune branche »* | **humain seul** |
| 3 | **lot de clôture** consignant l'arbitrage, l'état terminal et la liste du §8 | un seul document | chaîne documentaire |

> **C'est le plus court chemin, et il est court parce que le travail est fait.**
> **Six lots** ont été intégrés depuis l'ouverture — réexamen de `C1`, amendement
> de `C1`, instruction du régime, extraction `A5`, instruction `vito.xml`, constat
> `G.1`. Ils ont épuisé ce que le corpus, les sources statiques et le seul acte
> hôte autorisé pouvaient donner. Il ne reste pas un acte documentaire à mener :
> il reste une **décision** à prendre, puis à consigner.

**Ce que l'étape 3 ne devra pas faire** : prononcer `NON QUALIFIÉ` là où le
contrat dit `NON QUALIFIABLE` · requalifier une hypothèse `PARTIEL` en close ·
désigner une suite, la branche A n'en désignant plus aucune (§3) · émettre une
conclusion par défaut, que `w4f1a` §6.3 interdit.

**Et il ne devra toucher à aucun des contrats, qui sont de deux ordres qu'il ne
faut pas confondre** : **`C1`** — avec `C2` et `C3` — est un **critère** de
`w4f1-confirmation-window.md`, amendé par `w4f2-c1-amendement.md` ; **`c5`** et
**`c7`** sont les **contrats** `c5-vclient-contract.md` et
`c7-mqtt-read-contract.md`, qui portent le lecteur `vclient` et la surface de
lecture MQTT. Les uns ni les autres ne doivent être modifiés par une clôture.

---

## 10. Si l'arbitrage était de **poursuivre**

Ce lot ne recommande rien, mais il doit dire ce qu'il a constaté, faute de quoi
l'arbitre déciderait sans l'information.

**La poursuite n'a pas de cible documentaire.** Les voies techniques de
`w4f2-ouverture.md` §5.1 restent toutes non opératoires : les voies 1 et 2
attendent un **régime établi** — et le §4 montre qu'il ne débloquerait pas les
conditions 1 et 2 ; la voie 3 attend un **critère effectivement échoué**, qui ne
s'est pas produit.

**La seule cible réelle est `U-2` et `U-7`** — et le §5.1 établit que leur chemin
**est désigné** : `T0-A`, `T0-C`, `T0-D`.

> **Poursuivre signifierait donc arbitrer l'ouverture de `T0`, et rien d'autre.**
> Ce ne serait pas inventer un chemin : le corpus le désigne déjà.

**Mais il ne faut pas se méprendre sur ce que « ouvrir `T0` » coûte.** Ce n'est
pas lever une signature : le §10.3.1 exige **neuf préconditions**, *« toutes
exigibles … aucune n'est facultative »*, et le §5.1.1 en montre **cinq non
établies, une partielle et une `NON DONNÉE`** — déploiement en surface fermée,
preuve de fermeture sur le fichier déployé, observabilité des quatre composants,
rollback, présence physique, état nominal observé, autorisation du §11.2. **Aucun
ordre n'est prescrit entre elles ; elles sont toutes exigibles.**

**Ce lot ne demande pas cette ouverture et ne la prépare pas.** Il constate
qu'elle est la seule forme qu'une poursuite pourrait prendre ; que `T0-A` devrait
y conclure sur **`U-3`** avant que `T0-D` puisse statuer sur la calculabilité de
`C1` ; et que **même menée, elle pourrait ne rien donner** — §8.5 prévoit
expressément le cas où `T0-A` n'isole pas la population, `borne_sonde` restant
vide. **L'arbitre décide entre poursuivre — c'est-à-dire engager l'ouverture de
`T0` —, suspendre, ou abandonner.**

---

## 11. Ce que ce document ne fait pas

Il ne tranche aucun régime · il ne clôt pas `W4-F2` · il ne prend ni ne prépare
l'arbitrage · il ne recommande ni la poursuite, ni la suspension, ni la clôture ·
il n'émet aucune conclusion par défaut · il ne crée aucune hypothèse, aucun seuil,
aucune constante · il ne modifie aucun contrat, ni `C1` / `C2` / `C3`, ni `c5` /
`c7` · il ne demande ni ne prépare l'ouverture de `T0` · il n'ouvre ni Acte B, ni
`T0` / `T1` / `T2` · il n'autorise aucune lecture nouvelle, aucun terrain, aucune
mutation, aucun `debug`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.** Le pont historique demeure
l'unique écrivain réel de production ; la surface transactionnelle demeure sans
autorité, `false`.

---

## 12. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Cadrage initial du chemin de clôture de `W4-F2` |
| **2** | Audit. §5 : rétablissement de la borne « par ce lot » de `w4f2-c1-amendement.md` §9(5), et substitution de l'état exact du chemin — désigné via `T0-A` / `T0-C` / `T0-D`, non autorisé sous Précondition 9 `NON DONNÉE`, conditionné à `U-3` — à la négation de chemin. Propagation aux §6(3) et §10 : une poursuite signifierait **arbitrer l'ouverture de `T0`**. Appui de `w4f2-regime-instruction.md` §17 ajouté. Retrait de `F-23`, hors périmètre. Décompte des lots porté à **six**. Option **abandonner** restaurée au §9. Désambiguïsation de `C1` et des contrats `c5` / `c7`. **Thèse centrale inchangée** |
| **3** | Réaudit. §5.1, §6(3), §10 : l'ouverture de `T0` cesse d'être réduite à la Précondition 9 — nouveau §5.1.1 portant l'état des **neuf** préconditions du §10.3.1 repris de `w4f2-ouverture.md` §2, **sans requalification** et **sans réintroduire la valeur par défaut retirée en V4**. §5.1 : `T0-C` complété de sa fonction de **borne supérieure de coût** sous condition d'isolement par `T0-A`, et **repli du §8.5** ajouté — à défaut d'isolement, `borne_sonde` reste vide et `seuil_C1` non calculable. **Thèse centrale inchangée** |
| **4** | Réaudit. §5.1.1, §6(3), §8 et en-tête : décompte des préconditions corrigé en **2 satisfaites / 1 partielle / 5 non établies / 1 `NON DONNÉE`**, « non établie » et « `NON DONNÉE` » cessant d'être confondues. §5.1.1 et §10 : retrait de toute idée d'ordre entre les préconditions — le §10.3.1 les exige toutes sans en ordonner aucune. Cellule 2 : le retrait de la valeur par défaut est attribué à la **Version 4 de `w4f1-confirmation-window.md`**, portée par le lot `w4f2-c1-amendement.md`. §12 remis en ordre chronologique. **Aucune autre modification** |
| **5** | Réaudit. §10 : « six non établies » → « **cinq** non établies » — occurrence restée hors de la correction V4, qui avait porté sur la ligne suivante. **Aucune autre modification** |
