# Ouverture de W4-F2 — chantier de finalisation

> **Ce document est une ouverture documentaire.** Il consigne une décision
> humaine de statut et en établit les conséquences. Il **n'exécute aucun
> terrain**, n'installe rien, ne mesure rien, et **ne vaut pas l'autorisation du
> §11.2**.
>
> Il **ne redéfinit pas** W4-F2. Sa définition, ses préconditions, ses critères
> `ABORT` et son verrou vers W4-F3 restent ceux de
> `w4f-write-sovereignty.md` §10.3. Son protocole `T0` / `T1` / `T2` et sa
> barrière restent ceux de `w4f1-confirmation-window.md` §8.

## 1. Décision et motif

**W4-F2 passe de `FERMÉ / NON AUTORISÉ` à `OUVERT — FINALISATION BOILERACK`.**

Motif consigné, dans les termes de la décision :

> **W4-F2 est ouvert parce que l'objectif explicite est de terminer Boilerack ;
> l'achèvement du produit constitue le travail ouvert qui consomme les réductions
> d'incertitude nécessaires.**

> **Portée de ce motif — bornée.** Il vaut **pour W4-F2 et pour la satisfaction de
> `H-4` à son endroit**. Il **n'est pas** une justification générale : il ne
> couvre par avance aucune autre mutation, aucun autre lot, et ne dispense
> d'aucune autorisation ultérieure. Invoquer « terminer Boilerack » ne suffira pas
> à ouvrir un lot suivant.

## 2. Ce que l'ouverture ne fait pas

`w4f-write-sovereignty.md` §10.3.1 exige **neuf préconditions**, dont la neuvième
est une **autorisation humaine explicite et distincte** au titre du §11.2.

> **Cette autorisation n'est pas donnée**, et la présente ouverture ne la
> constitue pas. W4-F2 est **ouvert comme chantier**, non **autorisé comme
> terrain**.

État des neuf préconditions, à la date de ce document :

| # | Précondition | État |
|---|---|---|
| 1 | W4-F0 intégré et clos | **satisfaite** |
| 2 | W4-F1 clos, critère quantitatif disponible | **satisfaite** — `C1`, `C2`, `C3` ; `seuil_C1 = 0,971 s` par défaut |
| 3 | Boilerack configuré, surface transactionnelle fermée | **non établie** — rien n'est déployé |
| 4 | preuve, sur le fichier déployé, qu'aucune écriture n'est émissible | **non établie** |
| 5 | pont et superviseur dans leur état nominal | **partiellement établie, et il faut distinguer les registres.** **Observé** : aucune campagne autorisée ne les a arrêtés, désactivés ni modifiés. **Connu par configuration** : les deux unités et leur cadence déclarée. **Non observé** : leur **exécution réelle** — le constat Acte A les qualifie « connus par configuration, non observés en train d'exécuter », et note qu'« aucun témoin d'exécution ne rattache ce mode d'accès à l'une ou l'autre unité ». Rien n'est maintenu depuis les observations autorisées |
| 6 | observabilité sur les quatre composants | **non établie**, et il faut distinguer **source disponible** de **observabilité établie**. Démon : source **disponible** — le journal existe et est lisible — mais elle ne porte que les ouvertures de connexion, sans clôture ni attribution par client ; l'observabilité au sens du §10.3.1 n'en est **pas** établie. Pont et superviseur : sources **présumées disponibles** par leur exécution sous systemd, **aucune n'a jamais été observée** ; observabilité **non établie**. Boilerack : **inexistante**, non déployé |
| 7 | rollback de déploiement lecture seule disponible | **non établi** |
| 8 | exploitant physiquement présent, plan de reprise connu | **non établi** |
| 9 | **autorisation humaine du §11.2** | **NON DONNÉE** |

## 3. Effet sur les arbitrages `H-2` et `H-4`

Les arbitrages consignés dans `w4-arbitrage-activation-debug.md` **ne sont pas
réécrits**. Ce document en constate l'effet du changement de contexte.

### 3.1 `H-4` — la règle est inchangée, son critère se décompose

**`H-4` reste `SUBORDONNÉE`.** La règle ne bouge pas : une mutation de production
destinée à réduire une incertitude doit être justifiée par un travail ouvert **qui
consomme explicitement la réduction obtenue**.

Ce critère porte **deux conditions**, et il faut les tenir séparées.

| Condition | État |
|---|---|
| **Existence d'un travail ouvert** | **SATISFAITE** — W4-F2 est désormais un travail ouvert |
| **Consommation effective de la réduction** | **NON SATISFAITE À CE STADE, SOUS `C1` FIGÉ** |

**Pourquoi la seconde ne l'est pas.** Le §4 l'établit sur les documents canoniques
eux-mêmes : sous `C1` figé, la branche **C** rend `NON QUALIFIABLE`, la branche
**A** rend `NON QUALIFIABLE` également, et **aucune réduction de `H3` ou de `H6`
ne produit `T0 GO`**. La réduction que l'activation de `debug` permettrait n'a donc
**aucun effet consommable sur la qualifiabilité de W4-F2** dans l'état actuel.

> **Conséquence, et elle est nette.** `H-4` reste `SUBORDONNÉE` ; **son critère
> complet n'est pas encore satisfait** ; et **l'ouverture de W4-F2 ne fonde pas, à
> elle seule, une activation de `debug`**.

> **Ce n'est pas une fermeture de W4-F2.** W4-F2 demeure
> **`OUVERT — FINALISATION BOILERACK`** — mais sans terrain autorisé, et sans
> justification actuelle pour `debug`.

### 3.2 `H-2` — valide pour son état, reposée par le contexte

**`H-2` n'est pas annulée.** Elle reste une **décision valide pour l'état où elle
a été prise**, et son fondement propre était celui-ci, et non celui de `H-4` :

- `getTempKist` **résout** pour `20CB` — le résultat de la lecture a fermé une
  branche de risque ;
- les inconnues résiduelles ne constituaient pas, **à elles seules**, un besoin
  d'instrumentation de production.

**L'ouverture de W4-F2 est un changement matériel de contexte.** Elle **permet de
reposer la question**, parce qu'un élément nouveau — un travail ouvert — s'ajoute
désormais aux inconnues résiduelles, lesquelles n'ont pas changé.

> **Mais reposer n'est pas fonder.** `H-4` continue d'interdire d'utiliser cette
> seule ouverture comme justification d'une mutation **tant qu'aucune consommation
> effective n'existe sous `C1` figé** (§3.1).

**`H-3` redevient la question d'arbitrage humain pertinente sur `debug`** — sans
être pour autant le prochain arbitrage utile : le §5 établit ce qui la précède.

> **`H-3` n'est pas tranchée ici**, ni préjugée. Le §5 établit seulement ce qui la
> conditionne et ce qu'elle ne suffira pas à débloquer.

## 4. La barrière `T0` — ce que les documents canoniques imposent

C'est le point que l'ouverture de W4-F2 rend immédiatement opérant, et il doit
être énoncé sans atténuation.

`w4f1-confirmation-window.md` §8.2.1, repris littéralement par
`w4f1a-vcontrold-concurrency.md` §2, fixe **trois branches exclusives** :

| Branche | `T0-B` rend | Sortie contractuelle | Motif |
|---|---|---|---|
| **A** | `ADDITIF` | **`W4-F2 NON QUALIFIABLE — STOP`**, aucun `T1` | `C1` est **valide** mais **arithmétiquement inatteignable** : `seuil_C1 = 0,971 s` quand **une seule lecture** coûte 2,669 à 4,029 s. Dépassement **structurel**, non statistique |
| **B** | `NON ADDITIF` | **`T0 NO-GO — STOP`** | `C1` additive devient sans objet ; son remplacement est exigé **avant `T1`** et **exige un nouvel audit** |
| **C** | `INDÉTERMINÉ` | **`W4-F2 NON QUALIFIABLE — STOP`**, aucun `T1` | la **validité** de `C1` n'est pas démontrée |

> **`w4f1a-vcontrold-concurrency.md` §2 : « L'état actuel est la branche C, et il
> n'est pas choisi : c'est la valeur que `T0-B` prend faute de connaître `U-1`. »**

**Aucune des trois branches ne rend `T0 GO`** sous le contrat `C1` actuellement
figé. `T0 GO` exige en outre, par le §8.2.1, que **la résolution de la source de
`C1` satisfasse la règle du §8.5** — soit `r < 0,485 s`, **NON PROUVÉ** à ce jour,
et hors d'atteinte du puits fichier dont l'horodatage est à la seconde.

> **Conséquence, et elle est structurante.** Ouvrir W4-F2 ne le rend **pas**
> qualifiable. Réduire encore `H3` ou `H6` — ce que l'activation de `debug`
> permettrait — ferait au mieux passer l'état de la **branche C** à la **branche
> A**. La branche A est **également** `NON QUALIFIABLE`, et elle l'est sur une
> **arithmétique**, que **aucune observation ne modifie**.
>
> Le §8.2.1 le dit lui-même : en branche A, « c'est l'arithmétique, avant toute
> exposition, qui montre que la configuration actuelle ne peut pas satisfaire
> `C1` », et « **la suite appartient à un lot qui changerait la configuration, non
> à une mesure** ».

## 5. Prochain point décisionnel

L'ouverture de W4-F2 fait apparaître **deux points de décision distincts**, dont
un seul était nommé.

**Point 1 — `H-3`, opportunité de l'activation de `debug`.** Redevenue pertinente
(§3.2). Elle gouverne la possibilité d'un Acte B, lequel **caractérise les
possibilités réelles de `T0-A`** — sans en être la précondition, ni en découler.
Et **l'Acte B n'est envisageable que si les conditions qui le rendent utile et
possible sont réunies** : le §4 établit qu'à ce jour l'utilité fait défaut, et le
constat Acte A que la possibilité fait défaut avec le journal actuel.

**Point 2 — le contrat `C1` lui-même.** Il n'est pas nommé dans les questions
`H-1` à `H-12`, et il **domine le point 1** : quelle que soit la réponse à `H-3`,
et quel que soit le résultat d'un Acte B, `T0 GO` demeure inatteignable tant que
`C1` reste figé dans sa forme actuelle.

Le corpus laisse ouvertes des issues de **deux natures différentes**, et les
confondre serait une erreur.

#### 5.1 Voies techniques — toutes **conditionnelles**, aucune opératoire aujourd'hui

| # | Voie | Condition d'opérativité |
|---|---|---|
| 1 | **remplacement de `C1`** | opératoire **seulement si le régime `NON ADDITIF` est établi** — c'est la branche B, qui exige le remplacement « avant `T1` » et **un nouvel audit** |
| 2 | **lot changeant la configuration** | opératoire **seulement si le régime `ADDITIF` est établi** — c'est la suite que le §8.2.1 désigne pour la branche A |
| 3 | **réexamen par W4-F1** | déclencheur canonique = **critère effectivement échoué** (`w4f-write-sovereignty.md` §10.3.4). **Cet état n'est pas atteint aujourd'hui** : aucun critère n'a échoué, aucune mesure n'a eu lieu |

**Aucune des trois n'est opératoire dans l'état présent** : les voies 1 et 2
attendent qu'un régime soit **établi**, et l'état actuel est la branche **C**,
c'est-à-dire précisément l'absence de régime établi ; la voie 3 attend un échec
qui ne s'est pas produit.

#### 5.2 Voie de gouvernance — **disponible maintenant**

| # | Voie | Nature |
|---|---|---|
| 4 | **arbitrage humain sur la poursuite du chantier** | **décision de gouvernance**, non solution technique |

`w4f-write-sovereignty.md` §10.3.4 nomme cette voie à côté du réexamen par
W4-F1, et l'y rattache au même déclencheur — l'échec du critère. Mais un arbitrage
sur la poursuite d'un chantier est un **acte de gouvernance** : il appartient à
l'humain et ne requiert aucune habilitation canonique. Il est donc **disponible
dès maintenant**.

> **Ce qu'elle permet, et ce qu'elle ne permet pas.** Elle permet de décider
> **poursuivre, suspendre ou abandonner**. Elle **ne fabrique pas `T0 GO`**, ne
> lève aucune branche, et ne remplace aucune des trois voies techniques.

> **Ce document ne choisit aucune de ces quatre voies et n'en prépare aucune.**
> Il constate leur nature respective, et que le point 2 doit être arbitré
> **avant** que l'effort du point 1 puisse produire un effet sur W4-F2.

#### 5.3 Le prochain arbitrage humain utile

De ce qui précède, une seule conclusion se tire, et elle ne préjuge d'aucune
réponse :

> **Le prochain arbitrage humain utile porte d'abord sur la poursuite et la
> direction de W4-F2 face à la barrière `C1`** — et **non** sur l'activation
> immédiate de `debug`.

Motifs, tous établis au §4 et au §5.1 : sous `C1` figé, **aucune branche `T0-B`
ne permet `T0 GO`** ; **réduire `H3` ou `H6` ne change pas la qualifiabilité** ; et
un **Acte B serait aujourd'hui du travail réel sur `H3` et `H6`, mais sans effet
sur la qualifiabilité de W4-F2**.

**Cet arbitrage n'est pas pris ici.** Le présent document ne dit ni de poursuivre,
ni de suspendre, ni d'abandonner : il établit seulement que c'est la question qui
vient en premier.

## 6. Ce qui reste conditionnel

- **`H-5` à `H-11`** — ne deviennent pertinentes que si `H-3` conclut à une
  activation. Elles portent toutes sur l'exécution de cette activation : route,
  préalables de volume, durée, effet d'observation, comportement des clients,
  constats de sortie, journal résiduel.
- **`H-12`** — examinable dès que la question `debug` est reposée, indépendamment
  de `H-3`, `dbgFD` n'étant pas une mutation.
- **Acte B** — demeure **NON OUVERT**. Il **caractérise les possibilités réelles
  de `T0-A`** ; ce n'est ni sa précondition, ni sa conséquence. Il **n'est
  envisageable que si les conditions qui le rendent utile et possible sont
  réunies** — or son impossibilité avec le journal actuel est un constat déjà
  établi, que rien ici ne modifie, et le §4 établit qu'il serait aujourd'hui du
  **travail réel sur `H3` et `H6` sans effet sur la qualifiabilité de W4-F2**. La
  présente ouverture ne change ni l'un ni l'autre de ces deux points.
- **`T0`, `T1`, `T2`** — demeurent **fermés**. `T0` ne peut être ni exécuté ni
  préparé : sa barrière est close par les trois branches, et sa précondition de
  résolution n'est pas satisfaite.

## 7. État après ouverture

**W4-F2 : `OUVERT — FINALISATION BOILERACK`**, sans autorisation terrain (§2).

W4-F0, W4-F1, W4-F1A : **CLOSED** · Acte A : **CLOSED** · cadrage de l'activation
de `debug` : **CLOSED** · arbitrages `H-2` / `H-4` : **CLOSED** · Acte B : **NON
OUVERT** · `T0` / `T1` / `T2` : **aucun, et fermés**.

**Le pont historique demeure l'unique écrivain réel de production.** La **surface
transactionnelle demeure sans autorité**, `false` — l'ouverture de W4-F2 ne la
touche pas. L'**interdiction** d'ouvrir cette autorité relève du **§11.1**, clause
dominante dont c'est le deuxième acte réservé ; le **§11.2**, lui, ne l'interdit
pas : il **ne l'autorise pas**, ce qui n'est pas la même chose et suffit ici.

**État épistémique — inchangé, non touché par cette ouverture** : régime
**`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`** · `H1`, `H2`, `H3` **PARTIELLEMENT
RÉDUITES** (`H3` : transition 4 du maillon 2 **ÉTABLIE**, transitions 1, 2, 3 et 5
**NON ÉTABLIES**) · `H6` **RÉDUITE, NON CLOSE** · `U-1` **PART AMONT ÉTABLIE SOUS
H1/H2/H3/H6, RÉSIDU D'INSTALLATION OUVERT** · `I1` **PARTIELLEMENT RÉDUITE** ·
`r < 0,485 s` **NON PROUVÉ**.

## 8. Ce que ce document ne fait pas

Il n'autorise aucun terrain · il ne vaut pas l'autorisation du §11.2 · il
n'installe, ne démarre, ne mesure et ne déploie rien · il ne tranche pas `H-3` ·
il ne rouvre ni ne réécrit `H-2` et `H-4` · il n'ouvre pas l'Acte B · il n'ouvre
ni ne prépare `T0`, `T1`, `T2` · il ne modifie ni `C1`, ni `C2`, ni `C3`, ni aucun
statut d'hypothèse · il ne touche ni au code, ni au runtime, ni à un service · il
ne redéfinit pas W4-F2.
