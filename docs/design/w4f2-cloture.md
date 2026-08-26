# Clôture de `W4-F2` — `NON QUALIFIABLE` au plafond de preuve

> **Version 1.** Lot de clôture. Il consigne un **arbitrage humain** et l'état
> terminal de `W4-F2`. Il n'établit aucun fait, n'en requalifie aucun, et ne
> désigne aucune suite. Aucun hôte, aucun runtime, aucun terrain, aucun `debug`,
> aucune mutation.

---

## 1. L'arbitrage, consigné

> **`W4-F2` est clos comme `NON QUALIFIABLE` au plafond de preuve actuel.**
>
> **L'ouverture de `T0` n'est pas autorisée dans le cadre de `W4-F2`.**

C'est une **décision de gouvernance**, prise par l'humain. `w4f2-ouverture.md`
§5.2 l'avait nommée *« disponible dès maintenant »*, en précisant qu'elle *« ne
fabrique pas `T0 GO`, ne lève aucune branche »*. **Elle n'en lève aucune ici non
plus.**

Elle porte sur la **conduite du chantier**, non sur les faits. Aucun fait n'est
modifié par ce document.

---

## 2. Ce que « clos » veut dire, et ce qu'il ne veut pas dire

`w4f-write-sovereignty.md` §10.3.4 pose trois conditions **distinctes** à
l'admissibilité de `W4-F3` : *« `W4-F2` est **clos** ; la coexistence a été
**qualifiée** ; le critère de §10.3.3 est satisfait »*. Le corpus sépare donc
`clos` et `qualifié` ; ce document ne fait que se ranger à cette séparation.

| Terme | Ce qui est prononcé |
|---|---|
| **`NON QUALIFIABLE`** | la sortie contractuelle de la branche **C**, telle que la fixe `w4f1-confirmation-window.md` §8.2.1 |
| **`NON QUALIFIÉ`** | **n'est pas prononcé.** Ce n'est pas le terme du contrat, et ce document n'en introduit aucun |
| **abandon** | **n'est pas prononcé.** Les huit lots du §3 sont intégrés, audités et opposables |
| **échec** | **n'est pas prononcé.** Le régime `INDÉTERMINÉ` *« n'est pas choisi : c'est la valeur que `T0-B` prend »* (`w4f1a-vcontrold-concurrency.md` §2) |

---

## 3. Ce que le chantier a produit

Huit lots, tous intégrés à `main` après audit indépendant et merge humain.

| PR | Merge | Lot |
|---|---|---|
| #55 | `3fd7e93` | ouverture de `W4-F2` |
| #56 | `cdd4b93` | réexamen de la barrière `C1` |
| #57 | `60b78ad` | **amendement normatif de `C1`** — Version 4 puis 5 de `w4f1-confirmation-window.md` |
| #58 | `954b088` | instruction de l'établissement du régime |
| #59 | `e6b098f` | extraction `A5` — le jeu de commandes du pont |
| #60 | `030d7a0` | instruction `vito.xml` — résolution statique des treize commandes |
| #61 | `dde5750` | constat `G.1` — empreinte du fichier de commandes déployé |
| #62 | `5ec0068` | cadrage du plus court chemin de clôture |

Ces documents **restent en vigueur**. La clôture ne les rétracte pas.

---

## 4. État terminal — les faits, tels qu'ils sont

Repris **sans requalification**.

| Objet | État |
|---|---|
| **Régime opératoire** | **`INDÉTERMINÉ`** → branche **C** → **`W4-F2 NON QUALIFIABLE — STOP`** |
| Niveau épistémique | `PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION` — valeur `ADDITIF — CONDITIONNEL À H1/H2/H3/H6` |
| `H1` | `PARTIEL` |
| `H2` | `PARTIEL` — absorbe le résidu **(b)** de `H6` |
| `H3` | `PARTIEL` — maillon 1 `ÉTABLI` ; transition 4 `ÉTABLIE` ; transitions 3 et 5 **`ÉTABLIES SOUS CORROBORATION`**, conditionnées à 1 et 2 ; transitions 1 et 2 **ouvertes** |
| `H6` | `PARTIEL` — `RÉDUITE, NON CLOSE` |
| `H6` **(a)** terme 1 | **FERMÉ** — les treize commandes du pont résolvent pour `20CB` sur l'installation |
| `H6` **(a)** terme 2 | **OUVERT** |
| `H6` **(c)**, cas « commande non résolue » | **ÉCARTÉ sur l'installation** |
| `C1` | **non calculable** — `U-2` et `U-7`. Le critère demeure **en vigueur** dans sa forme amendée |
| Conditions de `T0 GO` | **1, 2 et 4 bloquantes** (`w4f2-c1-amendement.md` §6, Q5) |
| **Précondition 9 / §11.2** | **`NON DONNÉE`** |

> **Aucune conclusion par défaut n'est émise**, ce que `w4f1a-vcontrold-concurrency.md`
> §6.3 interdit expressément.

---

## 5. Les inconnues qui restent ouvertes

Elles restent ouvertes **exactement dans l'état où les lots les ont laissées**.

| Inconnue | État, non requalifié |
|---|---|
| **maillon 2** — transitions **1** et **2** | **non prouvé.** Faits d'**exécution du superviseur** ; hors de portée de tout acte documentaire |
| **`H1`** | `PARTIEL` — lien binaire ↔ arbre à la compilation, non prouvable passivement en l'état ; traces non instruites |
| **`H2`** | `PARTIEL` — invariant sur la fenêtre protégée non établi dans la durée ; voies structurelles non instruites |
| **`H6` (a)** terme 2 | **OUVERT** — la conformité du **pont déployé** au contrat `A5` n'est pas établie ; l'énumération des treize commandes est close **au niveau du contrat `A5` v0.4.3**, et rien n'établit que le pont effectivement déployé n'émette que celles-là |
| **`H6` (b)** | **OUVERT** — un participant extérieur agissant sur l'IPC System V ; **c'est `H2`**, qui l'absorbe |
| **`H6` (c)** | **OUVERT pour ses autres chemins** — sorties précoces autres que la non-résolution : échec d'écriture vers le client, expiration, fin de boucle avant acquisition |
| **`U-2`** — `borne_sonde` | `PREUVE TERRAIN / SOURCE EXTERNE REQUISE` — borne supérieure déterministe, **qualifiée sur la population des sondes du superviseur** ; **aucun substitut admis** |
| **`U-3`** — capacité du journal `vcontrold` | `PREUVE TERRAIN / SOURCE EXTERNE REQUISE` — clôture, durée, attribution par client ; **conditionne la calculabilité de `C1`** ; relève de `T0-A` |
| **`U-7`** — `occupation_max` | `PREUVE TERRAIN / SOURCE EXTERNE REQUISE` — seule `O ≤ R` est établie. **Réserve** : `w4f2-c1-amendement.md` §9(4) note qu'elle *« pourrait être non seulement non mesurée, mais non bornable de façon déterministe dans la configuration actuelle »*, point **non établi** et non tranché |
| **`A6`** | source de niveau 2 **jamais consommée** — dépôt privé ; `w4c-write-capture-protocol.md` §3 n'autorise à en reprendre que des **faits de comportement, jamais du code** |

---

## 6. Le chemin de reprise, conservé

> **La clôture ne détruit pas le chemin. Elle constate qu'il n'est pas ouvert.**

C'est ce qui la distingue d'un abandon, et ce qui la rend préférable à une
suspension : l'état est déclaré **et** la reprise reste écrite.

### 6.1 Les trois actes désignés

| Acte | Ce qu'il fait |
|---|---|
| **`T0-A`** | caractérise les sources et désigne celle qui servira à `C1` ; porte **`U-3`** |
| **`T0-C`** | référence statistique ; établit **en outre**, *« et seulement si la population des sondes du superviseur est réellement isolable »* par `T0-A`, une **borne supérieure de leur coût** |
| **`T0-D`** | **calculabilité, résolution et temps de réaction** — décide si `C1` et `C2` sont calculables |

### 6.2 Les neuf préconditions du §10.3.1

*« Toutes exigibles avant la première intervention. Aucune n'est facultative. »*
État repris de `w4f2-ouverture.md` §2 et de `w4f2-cadrage-cloture.md` §5.1.1,
**sans requalification** :

| # | Précondition | État |
|---|---|---|
| 1 | W4-F0 intégré et clos | **satisfaite** |
| 2 | W4-F1 clos, critère quantitatif disponible | **satisfaite** — `C1`, `C2`, `C3` |
| 3 | Boilerack configuré, surface transactionnelle fermée | **non établie** |
| 4 | preuve, sur le fichier déployé, qu'aucune écriture n'est émissible | **non établie** |
| 5 | pont et superviseur dans leur état nominal | **partiellement établie** |
| 6 | observabilité sur les quatre composants | **non établie** |
| 7 | rollback de déploiement lecture seule disponible | **non établi** |
| 8 | exploitant physiquement présent, plan de reprise connu | **non établi** |
| 9 | autorisation humaine du §11.2 | **`NON DONNÉE`** |

**Deux satisfaites, une partielle, cinq non établies, une `NON DONNÉE`.** Le
§10.3.1 **n'ordonne rien entre elles** : il les exige toutes.

### 6.3 Ce que la reprise ne garantirait pas

Deux réserves du corpus subsistent, et elles doivent accompagner le chemin :

- **`w4f1-confirmation-window.md` §8.5** — *« Si `T0-A` ne permet pas d'isoler les
  sondes du superviseur, alors aucune borne qualifiée n'existe, `borne_sonde`
  reste vide, et `seuil_C1` demeure non calculable. »* Le repli de secours a été
  **retiré** par la Version 4 du même document.
- **`w4f2-c1-amendement.md` §9(4)** — la réserve sur `U-7`, rappelée au §5.

> **Rouvrir `T0` demanderait donc un chantier, et son issue n'est pas acquise.**
> Ce document ne le demande pas, ne le prépare pas, et ne le recommande pas.

---

## 7. Ce que la clôture ne change pas

| Objet | État, inchangé |
|---|---|
| **`W4-F3`** | **inadmissible.** `w4f-write-sovereignty.md` §10.3.4 exige trois conditions ; la deuxième — *« la coexistence a été qualifiée »* — **n'est pas tenue**, la preuve de sortie du §10.3.3 n'ayant pas été produite |
| **Précondition 9 / §11.2** | **`NON DONNÉE`** |
| **Pont historique** | **unique écrivain réel de production** |
| **Surface transactionnelle** | **sans autorité**, `false` |
| Contrats `C1`, `C2`, `C3` | **en vigueur**, inchangés |
| Contrats `c5`, `c7` | **en vigueur**, inchangés |
| Les huit lots du §3 | **en vigueur**, inchangés |

> **Aucune sûreté n'est affaiblie et aucune exposition n'est ouverte.** La
> clôture consigne un arrêt **déjà en vigueur** ; elle ne l'assouplit pas.
> `w4f2-c1-amendement.md` §7 avait vérifié la même propriété pour l'amendement :
> *« Même arrêt, aucune exposition rendue possible. »*

---

## 8. Hors périmètre, signalé et non traité

**Le `stash@{0}` du dépôt n'est pas touché par ce lot.** Il porte du travail mis
à l'abri pour l'erratum `W2` §19.3.2 — erratum lui-même **consigné** dans
l'en-tête de `w2-transaction-concurrency-lifecycle.md`. Il est **sans rapport
avec `W4-F2`**, et ce document ne le modifie, ne le déplace, ne l'applique ni ne
le supprime.

Il est mentionné ici pour une seule raison : qu'une clôture de `W4-F2` ne puisse
pas être lue comme ayant soldé une dette qu'elle n'a pas examinée.

---

## 9. Ce que ce document ne fait pas

Il ne tranche aucun régime · il n'établit ni ne requalifie aucun fait · il
n'émet aucune conclusion par défaut · il ne crée aucune hypothèse, aucun seuil,
aucune constante · il ne modifie aucun contrat · il ne désigne aucune suite, la
branche A n'en désignant plus aucune · il ne prononce ni `NON QUALIFIÉ`, ni
abandon, ni échec · il n'ouvre ni `T0`, ni Acte B, ni `T1` / `T2` · il n'autorise
aucune lecture, aucun terrain, aucune mutation, aucun `debug` · il ne touche pas
au `stash@{0}`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.** Le pont historique demeure
l'unique écrivain réel de production ; la surface transactionnelle demeure sans
autorité, `false`.

---

## 10. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Clôture initiale de `W4-F2` sur arbitrage humain |
