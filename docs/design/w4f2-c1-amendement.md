# Amendement normatif de `C1`

> **Ce document est le lot d'amendement.** Il consigne la décision humaine, donne
> la matrice qui en fixe le périmètre, décrit exactement ce qui a été modifié dans
> `w4f1-confirmation-window.md`, et reconstruit la logique `T0` sur le texte
> amendé.
>
> **L'objet normatif est le contrat lui-même**, passé en **Version 5** — Version 4
> pour l'amendement, Version 5 pour la correction delta rendue après audit
> indépendant. Ce document ne le double pas : il l'accompagne et le rend auditable.
>
> **Il n'autorise aucun terrain**, ne fixe aucun seuil, n'établit aucun régime, et
> **ne rend l'amendement opératoire en rien**.

## 1. Décision humaine consignée

> **Rédiger l'amendement normatif de `C1` avant l'établissement du régime.**

Cette décision tranche l'arbitrage laissé ouvert par `w4f2-c1-reexamen.md` §12.

**Ce qu'elle autorise** : la rédaction d'un lot normatif documentaire.

**Ce qu'elle n'établit pas, et qu'elle ne prétend pas établir** : ni le régime
`ADDITIF`, ni le régime `NON ADDITIF`. Elle **ne rend pas l'amendement
opératoire**. Elle n'autorise ni terrain, ni configuration, ni `debug`, ni
l'Acte B, ni `T0` / `T1` / `T2`, ni aucune écriture chaudière.

### 1.1 La réserve de séquencement, assumée

`w4f1a-vcontrold-concurrency.md` §13 réserve l'ouverture de cette question à un
régime `ADDITIF` établi, et son §3 avertit que `V-2` et `V-3` sont mutuellement
exclusifs — *« construire l'un avant de savoir lequel, c'est avoir une chance sur
deux de construire le mauvais »*.

> **Cette réserve n'est pas levée : elle est assumée.** L'amendement en tient
> compte de deux manières.
>
> **Il ne construit pas `V-2`.** `V-2` est le verrou *« `C1` inatteignable si le
> régime est additif »*. L'amendement ne construit rien de tel : il **retire** une
> inférence non établie et **re-type** deux termes. Il serait tout aussi nécessaire
> sous `NON ADDITIF`, la confusion `R` / `O` qu'il corrige étant indépendante du
> régime.
>
> **Il ne devient pas opératoire pour autant.** `C1` amendée n'a de sens que sous
> un régime `ADDITIF` établi — le contrat le dit déjà, et l'amendement ne le change
> pas.

## 2. Question centrale

> Quel amendement **minimal** du contrat W4-F1 permet de conserver les usages
> légitimes de `R`, de remplacer par `O` les usages où la contention est réellement
> la grandeur pertinente, de supprimer l'inférence non établie
> `rafale_max ≥ 2,669 s`, et de **préserver la sûreté** de `C1` sans fabriquer de
> seuil ni de régime ?

---

## 3. Les deux grandeurs

| Symbole | Grandeur | Emploi légitime |
|---|---|---|
| **`R`** | **durée totale d'invocation** — temps mural, de l'appel au résultat | ordonnancement, chaînage des cycles, seuil de réalimentation, `T_release`, `cadence_max` |
| **`O`** | **occupation** — durée pendant laquelle un client détient la liaison partagée et en exclut les autres | contention : la grandeur que `C1` borne |

**Seule relation établie : `O ≤ R`.** Son fondement, porté au contrat en V5 : sous
`-n` le service est **strictement séquentiel** — fait établi par le constat
Acte A — donc une invocation se décompose en *attente éventuelle avant session*
puis *durée de session*, et l'occupation vaut au plus la seconde. **Aucune attente
non nulle, aucune inégalité stricte, aucune valeur** n'en découle.

> **Principe cardinal : `R` n'est pas remplacé globalement.** Là où le contrat
> raisonne en temps mural, `R` est la bonne variable et **reste**. Seuls sont
> amendés les emplois où `R` tient lieu de `O`.

---

## 4. Matrice du périmètre — occurrences examinées

Établie sur §2, §6.2, §6.5, §7.2, §8.2, §8.2.1, §8.5, §8.6, §8.6.1, §8.7 et §9 du
contrat en Version 3. **Elle est la seule vérité chiffrée de ce lot**, et tout
décompte y renvoie.

| # | Occurrence | Grandeur actuelle | Grandeur requise | `R` légitime ? | `O` requis ? | Modification ? | Motif |
|---|---|---|---|---|---|---|---|
| 1 | §2, citation C5 « 2 669 à 4 029 ms » | `R` | `R` | oui | non | **non** | citation d'une source, sans emploi normatif |
| 2 | §6.2, `R + 30 ≤ 8R ⟺ R ≥ 30/7` | `R` | `R` | oui | non | **non** | chaînage d'ordonnanceur : temps mural pur |
| 3 | §6.2, colonne « Coût par lecture » | `R` | `R` | oui | non | **oui — nommage V5** | typée explicitement `R` pour lever toute ambiguïté |
| 4 | §6.2, colonnes « Occupation » / « Rafale max » | `R` | `R` pour l'ordonnancement | oui, sous réserve de nommage | oui, si lues par `C1` | **oui — qualification V4, renommage V5** | collision de vocabulaire avec `occupation_max` |
| 5 | §6.2, proximité 4,029 / 4,286 | `R` vs `R` | `R` | oui | non | **non** | comparaison homogène |
| 6 | §6.5, définition du régime additif | conceptuelle | conceptuelle | — | — | **non** | l'énoncé est correct |
| 7 | §6.5, lignes « attente tolérable » et conclusion « une seule lecture dépasse déjà » | `R` employé comme `O` | `O` | **non** | **oui** | **oui — retrait V4** | inférence invalide |
| 8 | §6.5, encadré « ce constat n'est pas une conclusion terrain » | conclusion « arithmétiquement impossible » | aucune conclusion | — | — | **oui — réécriture V5** | **survivance** de l'inférence retirée |
| 9 | §7.2, verdict et condition suspensive | — | — | — | — | **non** | indépendant des deux grandeurs |
| 10 | §8.2, `T0-A` / `T0-B` | — | — | — | — | **non** | caractérisation de sources et de régime |
| 11 | §8.2.1, branche A | motif arithmétique | motif à refonder | — | — | **oui — motif V4** | l'arithmétique tombe avec l'inférence |
| 12 | §8.2.1, encadré `NON QUALIFIABLE` / `NON QUALIFIÉ` | désignait la suite | ne désigne rien | — | — | **oui — V4** | la désignation reposait sur l'arithmétique retirée |
| 13 | §8.2.1, condition 4 de `T0 GO` | « exclut les trois branches » | portée par branche | — | — | **oui — V5** | inexact : sous A, la condition 4 serait tenue |
| 14 | §8.2.1, branches B et C | — | — | — | — | **non** | indépendantes de la distinction |
| 15 | §8.5, `borne_effective` / `borne_publique_C5` | `R`, population non qualifiée | borne déterministe qualifiée | **non** | non | **oui — requalification V4, portée V5** | maximum empirique, population non qualifiée |
| 16 | §8.5, `rafale_max` | `R` | **`O`** | **non** | **oui** | **oui — re-typage V4** | grandeur de contention |
| 17 | §8.5, `seuil_C1 = 0,971 s` | dérivée d'une donnée non qualifiée | dérivée d'une borne qualifiée | — | — | **oui — retrait V4** | tombe avec la donnée dont elle dérivait |
| 18 | §8.5, encadré `max` / cliquet | correct | correct | — | — | **oui — précision V4** | le `max` ne porte que sur des bornes qualifiées |
| 19 | §8.5, repli « si T0-A n'isole pas ⇒ `0,971 s` » | repli sur donnée non qualifiée | — | — | — | **oui — retrait V4** | contredisait son propre voisinage |
| 20 | §8.5, justification historique du seuil V1 de 2,5 s | s'appuyait sur « attente tolérable » | motif propre | — | — | **oui — V5** | la notion invoquée a été supprimée par la V4 |
| 21 | §8.5, `r < seuil_C1 / 2 = 0,4855 s` | dérivée du seuil | dérivée du seuil | — | — | **oui — conséquence V4, règle d'admissibilité V5** | la règle survit, sa valeur tombe |
| 22 | §8.5, encadré « `C1` vraisemblablement inatteignable » | `R` employé comme `O` | `O` | **non** | **oui** | **oui — retrait V4** | même inférence invalide qu'au §6.5 |
| 23 | §8.5, `C2` et `C3` | — | — | — | — | **non** | indépendants des deux grandeurs |
| 24 | §8.6, événements `E1`–`E8` | — | — | — | — | **non** | états et seuils propres |
| 25 | §8.6.1, `T_release ≤ 8 × (R + ε)` | `R` | `R` | **oui** | non | **non** | délai avant libération : somme de temps muraux |
| 26 | §8.6.1 / §8.6.2, `cadence_max` | dérivée de `T_release` | idem | **oui** | non | **non** | hérite du typage correct |
| 27 | §8.7, condition 2 de `T1 GO` | renvoie à `C1` | idem | — | — | **non** | `C1` est amendée en place |
| 28 | §9, libellé de `U-2` | durée réelle | **borne** déterministe qualifiée | — | — | **oui — V5** | `borne_sonde` exige plus qu'une durée |
| 29 | §9, tableau des inconnues | `O` absente | `O` nommée | — | **oui** | **oui — ajout `U-7` V4** | le contrat nomme un terme sans source |

> **Décompte unique, recalculé sur cette matrice : 29 occurrences examinées —
> 17 amendées, 12 laissées intactes.**
>
> Les chiffres annoncés par la V4 du présent document — « 9 / 15 » puis « vingt sur
> trente » — étaient **faux et mutuellement incohérents**. Ils sont retirés. Toute
> mention chiffrée du périmètre renvoie désormais à cette seule ligne.

**Ajouts normatifs de la V4, qui ne sont pas des occurrences préexistantes** et ne
figurent donc pas dans le décompte : la **clause d'invariant de sûreté** (§8.5,
précisée en V5) et la **clause `R` / `O`** (§8.5, fondée en V5).

---

## 5. Ce que l'amendement change, point par point

### 5.1 En-tête — Versions 4 puis 5

La convention du dépôt porte l'historique dans un **bloc d'en-tête versionné**,
sans changelog séparé. Le bloc **V5** décrit la correction delta ; le bloc **V4**
et le bloc **V3** sont **conservés tels quels** dessous. Les mentions « W4-F2 reste
fermé » qu'ils contiennent sont signalées comme **états datés de la V3**.

**Le statut du contrat n'est pas touché** : `w4f1-confirmation-window.md` demeure
`CLOSED`, la convention n'en prévoyant pas d'autre pour amender.

### 5.2 §6.2 — qualification et nommage

Une clause précise que les colonnes du tableau sont dérivées de **`R`** et
décrivent du **temps mural**, que c'est l'emploi légitime de `R`, et que le
« Regroupement max » **MUST NOT** être lu comme l'`occupation_max` du §8.5.

**Les colonnes sont renommées en V5** — « Coût par lecture (`R`) », « Temps actif
simulé », « Regroupement max » — parce que « Occupation » et « Rafale max »
entraient en collision directe avec le vocabulaire normatif introduit au §8.5.
**Aucune valeur du tableau n'est touchée**, ni le raisonnement, ni `R ≥ 30/7`.

### 5.3 §6.5 — retrait de l'inférence, et de sa survivance

Les deux lignes « attente tolérable » et la conclusion « une seule lecture en cours
dépasse déjà l'attente tolérable » sont **retirées** (V4). Le tableau restant est
typé : les deux durées de C5 y sont marquées **`R`**.

**L'encadré final est réécrit en V5.** Il concluait encore que *« si le régime est
additif, alors la coexistence est arithmétiquement impossible aux coûts
documentés »* — c'est-à-dire exactement l'inférence que la V4 venait de retirer,
et que l'en-tête V4 comme le §8.2.1 déclaraient retirée. Le texte ne conclut plus
dans **aucun** sens : la valeur de `O` n'est établie par aucune source, **y compris
sous régime additif** ; établir le régime reste le travail de `T0` ; et **cette
absence de connaissance n'autorise rien**, `C1` restant non calculable.

### 5.4 §8.2.1 — motif de la branche A, et condition 4

**Sortie normative inchangée** — `W4-F2 NON QUALIFIABLE — STOP`, aucun `T1`.
**Motif changé** : « valide mais **non calculable** ». L'encadré explicatif est
corrigé, et la désignation de la suite comme « un lot qui changerait la
configuration » est **retirée** avec l'arithmétique qui la portait.

**Condition 4 de `T0 GO`, corrigée en V5.** Elle disait « exclut les trois branches
ci-dessus ». C'est inexact : **B** et **C** échouent bien à cette condition, mais
en branche **A** elle serait **tenue** si `ADDITIF` était établi — ce sont alors
les conditions **1** et **2** qui bloquent. **Aucun statut de branche n'est
modifié.**

### 5.5 §8.5 — le cœur de l'amendement

**(a) L'invariant de sûreté devient une clause normative.** Il était une
proposition de cadrage ; il est désormais **dans le contrat**, avec la règle que
toute formule prétendant remplacer `C1` **est jugée à ce niveau**. **C'est un
renforcement, et il est explicite.**

Sa **troisième propriété est précisée en V5** : le cliquet joue **entre bornes
qualifiées**, et le **premier** établissement d'une borne ne « durcit » aucun
niveau antérieur — il **fixe** le premier niveau.

**(b) La distinction `R` / `O` est introduite normativement**, avec `O ≤ R` comme
seule relation établie, l'interdiction d'employer `R` pour **minorer** `O`, et —
**ajouté en V5** — le **fondement** de `O ≤ R` : séquentialité stricte sous `-n`,
établie par le constat Acte A.

**(c) La formule est re-typée**, sa forme étant conservée :

```
borne_sonde        =  max( bornes supérieures déterministes disponibles,
                           qualifiées sur la population des sondes du superviseur )
seuil_C1           =  budget_superviseur  −  borne_sonde
occupation_max(T1) ≤ seuil_C1      et      occupation_max(T2) ≤ seuil_C1
```

`borne_publique_C5` est **requalifiée en donnée de référence non qualifiée**, avec
trois motifs cumulatifs, et **MUST NOT** servir de `borne_sonde`. Le repli de la V3
sur `seuil_C1 = 0,971 s` est **retiré**. Le `max` ne porte que sur des bornes
**qualifiées**. Le tableau des termes renvoie désormais explicitement
`borne_sonde` → **`U-2`** et `occupation_max` → **`U-7`**.

> **Portée de l'interdiction, précisée en V5.** Elle vise l'emploi de
> `borne_publique_C5` **comme `borne_sonde`**. Ses emplois explicitement typés
> **`R`** demeurent **licites** — comparaison au seuil de réalimentation (§6.2),
> calcul de `T_release` et de `cadence_max` (§8.6.1).

> **Conséquence assumée : `borne_sonde` sans valeur admissible ⇒ `seuil_C1` non
> calculable ⇒ `C1` non calculable.**

**(d) La condition de résolution est conservée symboliquement.** `r < seuil_C1 / 2`
demeure normative ; la valeur `0,485 s` **tombe avec le seuil dont elle dérivait**,
et **aucune valeur ne la remplace**. Le sens d'un futur déplacement est
**indéterminé** et **MUST NOT** être présumé.

**Règle d'admissibilité ajoutée en V5** : *l'admissibilité d'une source **MUST**
être réétablie depuis un `seuil_C1` calculé sur une borne qualifiée ; elle n'est
présumée dans **aucun** sens.* L'exclusion nommée de la résolution à la seconde
tombe avec la dérivation qui la portait — **et n'est remplacée par aucune
admission**.

**(e)** L'encadré « `C1` est vraisemblablement inatteignable » est **retiré**, avec
son inférence. **(f)** La justification historique du seuil V1 de 2,5 s est
**réécrite en V5** : elle s'appuyait sur l'« attente tolérable », notion supprimée
par la V4. Le motif retenu est propre — c'était **une fraction choisie**, non la
soustraction que le régime impose — et le retrait du seuil reste justifié.

### 5.6 §9 — `U-2` et `U-7`

**`U-7` — occupation `O`** est ajoutée au tableau des inconnues, avec le statut
`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`. Ce n'est **pas** une inconnue nouvelle
du système : c'est celle que la V3 masquait en employant `R` à la place de `O`.

**`U-2` est mise à niveau en V5** : `borne_sonde` n'exige pas seulement la durée
réelle d'une sonde, mais une **borne supérieure déterministe qualifiée sur la
population des sondes**. `M6` est inchangée, et « aucun substitut admis » reste
vrai.

Ensemble, `U-2` et `U-7` expliquent pourquoi les **deux** termes de `C1` sont sans
source.

---

## 6. Reconstruction de la logique `T0` sur le texte amendé

### Q1 — Sous régime `ADDITIF`, quelles données manquent pour calculer `C1` ?

**Deux, et ce sont exactement les deux termes :**

1. **`borne_sonde`** — borne supérieure **déterministe**, **qualifiée sur la
   population des sondes du superviseur**, de la durée totale d'une sonde hors
   exposition Boilerack. Inconnue **`U-2`** (`M6`), **sans substitut admis**.
2. **`occupation_max`** — l'occupation cumulée `O` imposée à une sonde. Inconnue
   **`U-7`**.

S'y ajoute en dépendance : la **source** de mesure de `occupation_max` et sa
**résolution**, soumise à `r < seuil_C1 / 2` — non évaluable tant que le seuil ne
l'est pas.

### Q2 — Sous régime `ADDITIF`, la branche A ?

> **`W4-F2 NON QUALIFIABLE — STOP`. Aucun `T1`.**

**Statut inchangé, motif changé** : d'une impossibilité arithmétique à une
**insuffisance de données**. Aucune sémantique nouvelle n'est introduite.

### Q3 — Sous régime `INDÉTERMINÉ` ?

> **`W4-F2 NON QUALIFIABLE — STOP`. Aucun `T1`.** Inchangé.

La branche C repose sur la **validité** de `C1`, non sur sa calculabilité.
**C'est l'état actuel.**

### Q4 — Sous régime `NON ADDITIF` ?

**Oui, `C1` reste sans objet, sans changement.** La branche B impose son
remplacement **avant `T1`**, avec **un nouvel audit**. **L'amendement ne s'y
substitue pas.**

### Q5 — Conditions de `T0 GO` indépendamment bloquantes

| # | Condition | État après amendement | Bloquante ? |
|---|---|---|---|
| 1 | `C1`, `C2`, `C3` calculables | **`C1` non calculable** — `U-2` et `U-7` | **oui** |
| 2 | résolution de la source de `C1` | **non évaluable** — le seuil ne l'est pas | **oui** |
| 3 | cadences et budget du §8.6 | inchangé — dépend de `T_release`, typé `R` | non touchée |
| 4 | régime compatible avec `C1` | **`INDÉTERMINÉ`** aujourd'hui → bloque ; **serait tenue** sous `ADDITIF` établi | **oui, dans l'état actuel** |
| 5 | aucune inconnue structurante | inchangée | non touchée |

> **Trois conditions bloquent aujourd'hui : 1, 2 et 4.** Sous un `ADDITIF` établi,
> la 4 tomberait et **1 et 2 subsisteraient**. **L'amendement ne débloque `T0 GO`
> en rien**, et ne le prétend pas.

---

## 7. Sûreté — ce qui est préservé

| Question d'audit | Réponse |
|---|---|
| une sûreté a-t-elle été affaiblie ? | **non.** Avant : seuil existant + `C1` inatteignable ⇒ `STOP`. Après : `C1` non calculable ⇒ `STOP`. **Même arrêt**, aucune exposition rendue possible |
| une constante a-t-elle été inventée ? | **non.** Aucune valeur créée ; **deux retirées** — `0,971 s`, `0,485 s` — sans remplaçante |
| une branche est-elle devenue implicitement `GO` ? | **non.** A et C ⇒ `NON QUALIFIABLE — STOP` ; B ⇒ `T0 NO-GO — STOP` |
| le régime est-il toujours séparé ? | **oui** |
| chaque suppression est-elle compensée ? | **oui** — table ci-dessous |
| chaque modification est-elle nécessaire ? | **oui** — la matrice du §4 borne le périmètre : **12 occurrences sur 29 sont laissées intactes** |

| Supprimé | Compensé par |
|---|---|
| l'inférence `rafale_max ≥ 2,669 s` (§6.5, §8.5) | la relation typée `O ≤ R`, son fondement, et l'interdiction d'employer `R` pour minorer `O` |
| la survivance « arithmétiquement impossible » (§6.5) | un énoncé qui ne conclut dans aucun sens, et rappelle que l'ignorance n'autorise rien |
| `seuil_C1 = 0,971 s` | l'exigence de **borne qualifiée** et le constat de non-calculabilité |
| le repli « si T0-A n'isole pas ⇒ `0,971 s` » | « aucune borne qualifiée ⇒ `seuil_C1` non calculable » |
| la valeur `r < 0,485 s` | la règle symbolique conservée **et** la règle d'admissibilité de la V5 |
| le motif arithmétique de la branche A | le motif d'insuffisance de données, **à sortie identique** |
| « attente tolérable » comme argument actif | le motif propre du seuil V1 : une fraction choisie |
| la désignation de la suite | **rien** — le contrat ne désigne plus aucune suite |

> **Un renforcement explicite** : l'invariant de sûreté entre au contrat.

---

## 8. Corpus historique — statut daté

Plusieurs lots **clos** continuent de porter `seuil_C1 = 0,971 s`, `r < 0,485 s`,
« `C1` arithmétiquement inatteignable » ou des énoncés équivalents :

`w4f2-ouverture.md` · `w4f1a-vcontrold-concurrency.md` ·
`w4f1a-upstream-characterization.md` · `w4-arbitrage-activation-debug.md` ·
`w4-cadrage-activation-debug.md` · `w4a-acte-a-constat.md`.

> **Aucun de ces documents n'est modifié, et aucun ne doit l'être.** Ce sont des
> **traces datées** de l'état doctrinal au moment de leur rédaction, et les
> réécrire détruirait la chaîne d'audit qui fait leur valeur.

**Statut déclaré ici :**

1. leurs énoncés numériques et leurs conclusions portant sur `C1` deviennent
   **datés** par les Versions 4 et 5 de `w4f1-confirmation-window.md` ;
2. ils **ne doivent plus être lus comme autorité normative actuelle sur `C1`** —
   **seul le contrat en vigueur l'est** ;
3. leur direction est **conservatrice ou neutre** : ils portent un seuil plus
   contraignant et une conclusion d'impossibilité, donc **ils ne créent aucune
   exposition** et ne peuvent pas autoriser ce que le contrat en vigueur interdit ;
4. une éventuelle **harmonisation documentaire** relèverait d'un **lot de
   gouvernance distinct**, qui **n'est pas ouvert ici** et que ce document ne
   prépare pas.

---

## 9. Risques et points non résolus

1. **La réserve de séquencement reste une réserve.** Sous `NON ADDITIF`, la
   branche B exigerait un contrat de remplacement que cet amendement ne fournit
   pas — il aurait néanmoins corrigé une confusion indépendante du régime (§1.1).
2. **`C1` devient non calculable là où elle avait une valeur** : gain de rigueur,
   perte de commodité. **Aucune exposition n'en devient possible** ; c'est
   l'inverse.
3. **Une source à la seconde n'est plus exclue *a priori*.** C'est le seul point
   potentiellement moins restrictif à terme. **Elle n'est pas admise pour
   autant** : son admissibilité devra être **réétablie** depuis un `seuil_C1`
   calculé sur une `borne_sonde` qualifiée, et **rien n'est présumé dans aucun
   sens**. La règle correspondante est portée au contrat (§8.5).
4. **`U-7` pourrait être non seulement non mesurée, mais non bornable de façon
   déterministe dans la configuration actuelle.** Le contrat établit que `R` est
   bornée par `read_timeout_s + ε`, et que **`ε_aval` n'est pas bornée par le
   code** (§3, tableau des composantes de `ε`). Comme `O ≤ R`, une borne
   déterministe sur `O` pourrait s'en trouver hors d'atteinte. **Ce point n'est pas
   établi**, et ce lot ne le tranche pas ; il devrait l'être avant qu'une valeur
   puisse satisfaire la norme. **Direction actuelle : conservatrice** — cela
   maintient `C1` non calculable. **Aucune mesure n'est lancée, et il n'est pas
   conclu que la configuration soit impossible.**
5. **`U-2` et `U-7` sont toutes deux `PREUVE TERRAIN / SOURCE EXTERNE REQUISE`.**
   Le chemin qui les lèverait n'est **pas** désigné par ce lot.
6. **Le périmètre est borné par la matrice du §4.** Une occurrence qui lui aurait
   échappé resterait typée `R` à tort — **l'audit est invité à la chercher**.

---

## 10. Statut du régime, exactement

Pour éviter tout raccourci : le régime n'est pas simplement « non établi ».

| Élément | État |
|---|---|
| caractérisation amont | **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`** |
| `U-1` | **part amont établie sous hypothèses** ; **résidu d'installation ouvert** |
| régime opératoire, aujourd'hui | **`INDÉTERMINÉ`** |

> **La conclusion ne change pas : `INDÉTERMINÉ`**, donc branche C, donc
> `W4-F2 NON QUALIFIABLE — STOP`.

## 11. Ce que l'amendement ne fait pas

Il **n'établit aucun régime** — la décision de rédiger maintenant n'est **pas** une
preuve de régime.
Il **ne rend l'amendement opératoire en rien**.
Il **ne fixe aucun seuil**, aucune borne, aucune durée d'occupation, aucune rafale
admissible, aucune valeur de `r`.
Il **ne débloque aucune condition de `T0 GO`**.
Il **ne remplace pas `R`** là où `R` est légitime.
Il **ne modifie aucun lot clos**.
Il **n'ouvre** ni Acte B, ni `T0` / `T1` / `T2`, ni aucun terrain.
Il **ne change pas** le statut du contrat : `w4f1-confirmation-window.md` demeure
`CLOSED`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.** Le pont historique demeure
l'unique écrivain réel de production ; la surface transactionnelle demeure sans
autorité, `false`.
