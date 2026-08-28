# Ouverture de `W4-Q` — chantier successeur de qualification de la coexistence

> **Version 2**, après intégration du cadrage. Le `NO-GO` précédent portait sur
> le **séquencement**, non sur la conception : le lot ouvrait un chantier sous un
> cadrage qui n'était pas encore dans le dépôt. **Le cadrage y est désormais**,
> et le présent lot est rebasé sur lui.
>
> | | Correction |
> |---|---|
> | **V2 · a** | **État réel du cadrage rétabli** : il est **intégré et opposable**, et non plus « absent ». Le §2 le dit, et le **référence par son chemin dans le dépôt** |
> | **V2 · b** | **Empreinte et base de l'artefact gelé retirées** : elles servaient à rendre vérifiable un document hors dépôt. Il y est |
> | **V2 · c** | **Mention d'un audit externe retirée** — elle n'est pas opposable au dépôt |
> | **V2 · d** | **Décision « intégrer, ou non, le cadrage » retirée du §7.1** : elle est **prise**, et une décision prise n'est plus une décision ouverte |
>
> **Le contenu fonctionnel est conservé sans autre changement** : désignation,
> objet, frontières négatives, non-autorisation de `T0`, décisions et inconnues
> restantes, `STOP` et issues terminales sont inchangés.
>
> **Version 1.** Ouverture initiale, sous cadrage non encore intégré.

> **Lot d'ouverture.** Il **ouvre** un chantier et **consigne
> l'arbitrage humain** qui l'autorise. Il n'exécute aucune phase, ne mesure
> rien, et ne tranche aucune question de fond.
>
> Aucun code, aucun terrain, aucune mesure, aucune valeur locale, aucun
> amendement normatif. **Aucune clôture existante n'est modifiée.**
>
> **`T0` demeure NON AUTORISÉ.**

---

## 1. Désignation

> **Le chantier successeur est désigné `W4-Q`** — *qualification de la
> coexistence.*

La désignation est **introduite ici**. Elle est vérifiée libre dans le corpus :
la famille `W4` emploie `W4-A` à `W4-F`, et leurs sous-lots `W4-F0` à `W4-F5` ;
aucun `W4-Q` n'existait.

**Ce que cette désignation fait, et ce qu'elle ne fait pas :**

| | |
|---|---|
| Elle **nomme** un chantier distinct, pour qu'il puisse être cité sans ambiguïté | oui |
| Elle en fait un **sous-lot de `W4-F`** | **non.** `W4-Q` n'est pas `W4-F6`, ne s'insère pas dans l'énumération du §10.7, et n'hérite d'aucune position contractuelle de ce fait |
| Elle lui donne la **position contractuelle de `W4-F2`** | **non.** `W4-F2` est clos, et sa clôture n'est pas modifiée |
| Elle fixe sa **place dans l'enchaînement** | **partiellement, et par son objet seul** : `W4-Q` est le chantier dont dépendrait la **condition 2** du §10.3.4 — *« la coexistence a été qualifiée »* — s'il aboutissait. Rien d'autre n'est présumé |

## 2. Autorité amont

| Document | Rôle | État |
|---|---|---|
| **Cadrage du chantier successeur** — `docs/design/coexistence-cadrage-successeur.md` | définit `W4-Q` : objet, corpus hérité, inconnues, décisions, conditions préalables, homologation, issues | **intégré, en vigueur** |
| **`w4f2-a0-succession.md`** | consigne l'arbitrage retenant la forme du **chantier successeur** | intégré, en vigueur |
| **`w4f2-cloture.md`** | clôture de `W4-F2`, `NON QUALIFIABLE`, et chemin de reprise conservé | intégré, en vigueur |

> **Le cadrage est dans le dépôt**, à
> `docs/design/coexistence-cadrage-successeur.md`. Il est **opposable**, et le
> présent lot **le désigne comme autorité amont**.
>
> Le lot **reprend au §4, §5, §6 et §8 ce qui est nécessaire pour que l'ouverture
> se comprenne seule**. Il ne le résume pas, ne s'y substitue pas, et **n'en
> importe aucune substance non reprise ici** : sur tout ce qu'il ne reprend pas,
> **c'est le cadrage qui fait foi**.

## 3. L'arbitrage d'ouverture, consigné

> **Décision humaine : ouvrir le chantier successeur sous le cadrage Version 2.**

C'est une **décision de gouvernance**, prise par l'humain. Elle **ouvre** un
chantier ; elle n'autorise aucune phase, aucun terrain, aucun amendement.

Ses conséquences, telles qu'énoncées avec elle :

| Objet | État |
|---|---|
| **`W4-Q`** | **ouvert** |
| **`W4-F2`** | **reste clos `NON QUALIFIABLE`** |
| Documents de clôture | **aucun n'est modifié** |
| **`T0`** | **reste NON AUTORISÉ** |
| Toute proposition nouvelle d'amendement de `C1` | **non adoptée** |
| Inconnues héritées | **aucune n'est réputée levée** |
| Autorité transactionnelle | **aucune n'est ouverte** |

## 4. Objet de `W4-Q`

> **Rendre la qualification de la coexistence *jugeable*. Pas encore la juger.**

`w4f-write-sovereignty.md` §10.3 assigne à `W4-F2` deux volets : déployer et
prouver la lecture, **et** *« **qualifier la coexistence** contre le critère que
`W4-F1` aura fixé »*. `W4-Q` reprend **le second, et lui seul**.

`W4-F2` s'étant clos sur `NON QUALIFIABLE` — *« l'impossibilité de la juger »*,
`w4f1-confirmation-window.md` §8.9 —, `W4-Q` ne peut pas commencer par juger.

**Deux étages, et `W4-Q` porte le premier :**

| Étage | Contenu | Porté par |
|---|---|---|
| **1** | franchir la barrière `T0` : établir si un jugement est possible | **`W4-Q`** |
| **2** | `T1`, `T2`, et le verdict `QUALIFIÉ` / `NON QUALIFIÉ` | **hors `W4-Q`**, soumis à des autorisations distinctes |

## 5. Frontières négatives

Reprises du cadrage. Elles valent pour toute la durée de `W4-Q`.

> **`W4-Q` MUST NOT :**
>
> - rouvrir `W4-F2`, ni modifier une clôture, ni requalifier un verdict rendu ;
> - réinstaller, redéployer, ni requalifier la lecture ;
> - toucher à l'autorité transactionnelle, qui **demeure fermée** ;
> - amender un contrat hérité — un amendement, s'il devenait nécessaire, relève
>   d'un **lot distinct, audité séparément** ;
> - réputer levée une inconnue héritée, dans un sens ou dans l'autre ;
> - se fonder sur un document non intégré au dépôt, ni sur un constat non
>   homologué ;
> - engager un acte de terrain sans l'autorisation humaine qui lui manque (§6) ;
> - entreprendre l'un des **quatre actes réservés** du §11.1, qui demeurent
>   interdits en tout état de cause.

> **Ces frontières ne sont pas des recommandations.** Leur franchissement est un
> motif de **STOP immédiat** au sens du §8.

## 6. `T0` demeure NON AUTORISÉ

> **L'ouverture de `W4-Q` n'autorise pas `T0`.**

`w4f2-cloture.md` §1 : *« L'ouverture de `T0` n'est pas autorisée dans le cadre
de `W4-F2`. »* `w4f2-a0-succession.md` ne l'autorise pas sous une autre forme.
Le cadrage ne l'autorise pas. **Le présent lot ne l'autorise pas davantage.**

Une autorisation de `T0` exigerait un **acte humain distinct**, postérieur à
celui du §3, et **elle n'est pas donnée**.

> **Une question préalable demeure entière, et le présent lot ne la tranche
> pas :** la précondition 9 du §10.3.1 renvoie à l'autorisation du §11.2, dont le
> texte se déclare *« propre à `W4-F2` »* et n'autorise *« uniquement dans le
> cadre de `W4-F2` »*. Ce qu'il faut à `W4-Q` — extension, autorisation neuve, ou
> autre — **est une décision ouverte** (§7).

## 7. Décisions et inconnues encore ouvertes

**Aucune n'est tranchée par ce lot**, et leur énumération n'en préjuge pas
l'issue. L'ordre ci-dessous n'est pas prescriptif.

### 7.1 Décisions

| Décision | Nature |
|---|---|
| **La forme de l'autorisation humaine de terrain** pour `W4-Q` (§6) | gouvernance / terrain |
| **Autoriser, ou non, `T0`** — acte distinct, non donné | terrain, lecture seule |
| **Statuer sur la précondition 2** du §10.3.1 et sur la dissymétrie documentaire que le cadrage relève | normative |
| **Trancher la réserve** que le corpus porte sur `U-7`, ou décider de la faire instruire | normative |
| **Appliquer les contrats hérités tels quels**, ou amender l'un d'eux par un lot distinct | normative |

### 7.2 Inconnues héritées — aucune n'est levée

Elles restent **exactement dans l'état où les lots les ont laissées**.

| Inconnue | État |
|---|---|
| **`U-1`** — régime de concurrence | ouverte ; `w4f1` §9 : *« conditionne §6.5 et **la validité même de `C1`** »* |
| **`U-2`** — `borne_sonde` | ouverte ; *« aucun substitut admis »* |
| **`U-3`** — capacité du journal du démon | ouverte ; *« conditionne la calculabilité de `C1` »* |
| **`U-7`** — `occupation_max` | ouverte ; *« seule `O ≤ R` est établie »* |
| **`H1`**, **`H2`**, **`H6`** (a) terme 2, (b), (c) | `PARTIEL` ou **OUVERT** |
| **maillon 2**, transitions 1 et 2 | **non prouvé** |

> **Aucune de ces lignes n'est un acquis de `W4-Q`.** Elles sont l'état de départ
> qu'il devra **réétablir depuis le corpus** avant toute décision de barrière.

## 8. Conditions de `STOP`, et issues terminales

### 8.1 `STOP`

`W4-Q` **MUST** s'arrêter, immédiatement et sans poursuivre, dans chacun des cas
suivants :

| Cas | Conduite |
|---|---|
| une **frontière négative du §5** est franchie, ou sur le point de l'être | arrêt immédiat ; consigner le fait |
| un **acte de terrain** serait requis sans que l'autorisation correspondante ait été donnée | arrêt ; la demander, ou renoncer |
| une **issue terminale** du §8.2 est atteinte | arrêt ; la prononcer avec sa méthode |
| l'**humain décide l'arrêt** | arrêt ; consigner l'abandon (§8.2) |

> **Un `STOP` n'est pas une issue terminale.** Un chantier arrêté sans issue
> prononcée est **non clos**, et le dire est préférable à laisser croire qu'il
> l'est.

### 8.2 Issues terminales

Quatre, exclusives, **reprises du cadrage sans modification**. `W4-Q` est clos
lorsqu'il en a prononcé une, **avec sa méthode**, et pas avant.

| Issue | Statut | Sens |
|---|---|---|
| **`QUALIFIABLE`** | **proposée par le cadrage**, non issue du corpus antérieur | la barrière `T0` est franchie **au sens plein des cinq conditions du §8.2.1**. *La question peut désormais être posée* — ni `QUALIFIÉ`, ni « coexistence sûre », ni autorisation de `T1` |
| **`NON QUALIFIABLE`** | **héritée** — `w4f1` §8.9, branches **A** et **C** | la barrière n'est pas franchie. *« Ce n'est pas un échec de la coexistence : c'est l'impossibilité de la juger »* |
| **`T0 NO-GO`** | **héritée** — `w4f1` §8.9, branche **B** | le régime est établi **non additif** ; `C1` additive est sans objet ; son remplacement *« exige un nouvel audit avant tout `T1` »*. **Remède propre, distinct de `NON QUALIFIABLE`** |
| **Abandon humain** | **proposée par le cadrage**, non contractuelle | décision explicite de ne pas poursuivre ; referme le chemin |

> **Les sorties `QUALIFIÉ` et `NON QUALIFIÉ` n'appartiennent pas à `W4-Q`** :
> elles supposent `T1` et `T2`, qui relèvent du second étage (§4). Le présent lot
> ne les modifie pas, et n'y touche pas.

> **Aucune issue n'est présumée.** L'abandon n'est pas un échec du chantier :
> c'est l'une de ses quatre conclusions légitimes.

## 9. Ce que ce document ne fait pas

Il **n'autorise pas `T0`**, **ne conduit aucune phase**, **ne mesure rien**,
**n'adopte aucun amendement**, **ne tranche aucune inconnue**, **ne requalifie
aucune précondition**, **ne modifie aucune clôture**, et **ne prononce aucune
issue terminale**. Il **n'ouvre aucune autorité transactionnelle**.

Il ouvre un chantier, le nomme, et s'arrête là.

## 10. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture de `W4-Q`, sous un cadrage alors non intégré. Aucune phase conduite. |
| **2** | Rebase sur le cadrage **intégré**. État réel du cadrage rétabli et référencé par son chemin ; empreinte de l'artefact gelé et mention d'audit externe retirées ; la décision d'intégration sort des décisions ouvertes, étant prise. **Contenu fonctionnel inchangé.** |
