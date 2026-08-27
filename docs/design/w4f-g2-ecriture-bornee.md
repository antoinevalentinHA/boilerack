# `G.2` — écriture terrain **bornée et réversible** sur `heating_curve_shift`

> **Version 6**, après réaudit. **Une seule correction** : le **prédicat** qui
> détermine `V_attendue`. Rien d'autre n'est touché.
>
> | | Correction |
> |---|---|
> | **Prédicat `V_attendue`** | La V5 indexait `V_attendue` sur des **moments** — « temps 9 », « temps 11 », « étape 1 du §11.2 ». C'était faux : un abandon survenu **avant toute écriture** conduit lui aussi à l'étape 1 du §11.2, où la table de la V5 exigeait alors **`V_canon + 1`** — une valeur que **rien n'avait écrite**. `V_attendue` dépend désormais de **deux faits objectifs**, et d'eux seuls — §12.2.1, §11.2.1 |
>
> **Inchangés, et vérifiés tels** : **`AB-8`** avant écriture · **`AB-1` transposé**
> au temps 11 · la règle propre à `G.2` — **aucune restauration de la valeur
> après `ABORT`** (§10) · la **sélection** du critère, qui reste celle de `W4-C`
> §12.3.2 · tout le reste du document.
>
> Corrections de la **Version 5**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **AB-1** | **`W4-C` écrivait à l'identique** : toute relecture y devait concorder avec `V_brut`, et `AB-1` le sanctionnait *« à n'importe quelle étape »*. **`G.2` déplace la valeur d'un pas** : au temps 11, la valeur attendue est **`V_canon + 1`**, et exiger `V_brut` y aurait fait déclencher `AB-1` **précisément quand l'écriture a réussi**. `AB-1` est donc transposé : le **terme de référence** suit la valeur attendue au moment de la relecture, et **rien d'autre ne change** — §12.2.1 |
>
> **Inchangés, et vérifiés tels** : **`AB-8`** et tous les critères **avant**
> écriture · la règle propre à `G.2` — **aucune restauration de la valeur après
> `ABORT`** (§10) · la transposition de l'étape 1 du §11.2 (§11.2.1), avec
> laquelle §12.2.1 est **délibérément aligné**.
>
> Corrections de la **Version 4**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **R1** | **Ouverture réelle de l'autorité.** Le fait porteur est **symétrique**, et la V3 ne l'appliquait qu'à la fermeture : l'autorité étant lue au démarrage du processus, persister `enabled = true` **ne compose rien** sur un processus déjà lancé. Le temps 8 comporte désormais le **démarrage manuel** de `<unité-boilerack>` et la **preuve** de la surface composée et souscrite — §9, temps 8 |
> | **R2** | **`EI-8` rendue établissable.** La preuve *one-writer* n'**attribue plus** les connexions par client : `U-3` ne le permet pas. Elle repose sur une **fenêtre muette** pendant laquelle aucun participant de `G.2` n'émet — §8.1 |
> | **R3** | **`EI-10` hors du chemin Boilerack.** Le lecteur de Boilerack est en **`-J` seul** ; la forme texte n'y existe pas. La concordance des deux formes est établie par **deux captures `vclient` nues** — §7, §9 temps 6 |
> | **R4** | **Les trois faits distincts de `W4-C` §13.1** — **A** actif · **B** sondant · **C** publiant — restaurés et nommés séparément. La V3 fusionnait **B** et **C**, ce que le §13.1 avertit expressément de ne pas faire — §11.2 |
> | **P-a** | **Restauration complète du superviseur.** `W4-C` **§13** compte **cinq étapes ordonnées**, et *« la campagne n'est close qu'après l'étape 5 »*. La V3 n'en portait que deux, et omettait l'étape 5 entière. Les cinq sont reprises — §11.2 |
> | **P-b** | **Ambiguïté des renvois `§11.1` levée.** **Trois** sections portent ce numéro dans le corpus. Une convention de citation est posée, et aucune référence n'est plus laissée nue — §0 |
>
> **Références corrigées** : les **critères détaillés** de `PR-1` / `PR-2` viennent
> de `W4-C` **§16.1** ; `W4-C` §9.1 n'en porte que l'**exigence de méthode** —
> §2.4 · la clause *« aucune restauration de la valeur après `ABORT` »* est
> présentée pour ce qu'elle est : une **restriction propre à `G.2`**, plus stricte
> que `W4-C` §12.1 — §10.
>
> **Aucun terrain dans ce lot.** Ce document n'exécute rien et n'autorise aucune
> exécution.

---

## 0. Convention de citation

Le corpus compte **trois** sections numérotées `§11.1`, et la V3 les citait sans
les distinguer. La confusion n'était pas théorique : elles portent des règles
différentes, et l'une d'elles est la clause dominante des actes réservés.

| Renvoi | Document | Objet |
|---|---|---|
| **`w4f` §11.1** | `w4f-write-sovereignty.md` | **clause dominante** — les quatre actes réservés |
| **`W4-C` §11.1** | `w4c-write-capture-protocol.md` | **garde de fraîcheur de `V_brut`** |
| **§11.1** *(nu)* | **le présent document** | **fermeture réelle de l'autorité** |

> **Règle, appliquée sans exception dans ce document.** Toute référence à un autre
> document **MUST** porter son **nom court**. Une référence **sans nom court**
> désigne **le présent document**, et rien d'autre.

| Nom court | Document |
|---|---|
| `w4f` | `w4f-write-sovereignty.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `W4-A` | `w4a-vclient-write-adapter.md` |
| `w4f1` | `w4f1-confirmation-window.md` |
| `W1` | `w1-mqtt-transaction-surface.md` |
| `cloture` | `w4f2-cloture.md` |
| `ouverture` | `w4f2-ouverture.md` |
| `A5x` | `w4f2-a5-extraction.md` |
| `A5` | `arsenal … boiler_pi/mqtt.md` — contrat MQTT du pont historique, source de `A5x` |
| `C5`, `C6`, `c7`, `W4-E2` | contrats homonymes du corpus |

La même précaution vaut pour `§11.2` et `§11.3`, qui existent eux aussi dans
`w4f` **et** dans le présent document.

---

## 1. Objet et frontières

Ce document fait **une seule chose** : il crée l'exception `G.2` et l'enferme.

Il **n'amende pas** `C1`, `C2`, `C3` dans leur énoncé, ni `w4f1`, ni `cloture`,
ni aucun des seize contrats `c*`. Il ne rouvre ni `T0`, ni `T1`, ni `T2`, ni
l'`Acte B`. Il ne requalifie pas `W4-F2`. Il n'ouvre pas `W4-F3`. **Il ne modifie
pas l'index du corpus.**

> **`W4-F2` demeure `NON QUALIFIABLE` hors `G.2`**, et **`W4-F3` demeure
> inadmissible hors `G.2`.** L'exception ne les touche pas : elle passe à côté
> d'eux, sur un périmètre qui leur est étranger.

---

## 2. Ce que l'amendement doit lever, et pourquoi

### 2.1 Les clauses en vigueur

`w4f` **§11.1** — *clause dominante* — réserve **quatre actes** à une
autorisation *« explicite, distincte, **postérieure à l'audit de W4-F3**, et
portant sur cette campagne-là »* :

1. toute **écriture réelle** sur la chaudière ;
2. toute **ouverture de l'autorité transactionnelle** —
   `[transaction_surface].enabled = true` ;
3. toute **neutralisation du dispositif historique** — `<unité-pont>` ou
   `<timer-guard>` ;
4. toute **bascule de souveraineté**.

`w4f` §10.3.4 : *« W4-F3 n'est admissible que si les trois conditions sont
réunies : W4-F2 est clos ; la coexistence a été qualifiée ; le critère de §10.3.3
est satisfait. »* La deuxième n'est pas tenue — `cloture` §7.

`w4f` **§11.3**, table des phases : *« **W4-F4 est le seul sous-lot où une
écriture réelle est possible.** »*

### 2.2 Le verrou est de séquencement, non de sûreté

L'autorisation de `w4f` §11.1 est **exigée après un audit de `W4-F3`**, et
`W4-F3` est lui-même inadmissible tant que la coexistence n'est pas qualifiée. La
qualification bute sur `borne_sonde` (**`U-2`**), sans valeur admissible —
`w4f1` §8.5 — d'où `seuil_C1` non calculable, d'où `C1` non calculable.

**Le blocage est circulaire, et son objet n'est pas l'acte visé ici.**

### 2.3 Il n'existe aucun mécanisme *one-writer*

`W4-A` **§20** :

> *« **W4-A ne résout pas le *one-writer* et n'en conçoit aucun mécanisme.** »*

**Conséquence directe** : aucun verrou logiciel, aucune élection, aucun arbitrage
ne garantit qu'un second écrivain n'agira pas sur `setNiveauM1` pendant `G.2`. La
seule garantie disponible est **l'absence établie par preuve** — §8.

### 2.4 `PR-1` et `PR-2` — l'exigence de méthode, et les critères

Deux textes distincts, et la V3 les confondait.

**L'exigence de méthode** est portée par `W4-C` **§9.1**. Elle impose, avant
toute écriture caractérisée, deux preuves non facultatives — `PR-1` sur
`<timer-guard>` **et son unité d'exécution**, `PR-2` sur `<unité-pont>` — chacune
avec *« la méthode employée […], leurs sorties, et l'horodatage »*. Le même §9.1
ferme la voie facile : *« Aucun raisonnement par absence de trace »*, et le
journal du démon *« ne prouve rien pour `PR-1` »* — `PR-1` *« repose directement,
et uniquement, sur l'état des unités »*.

**Les critères détaillés** — ce qu'« inactif » veut dire concrètement — viennent
de `W4-C` **§16.1**, *« Conditions réunies, et comment elles ont été établies »* :

| Réf | Objet | Critère — `W4-C` **§16.1** |
|---|---|---|
| **`PR-1`** | `<timer-guard>` **et son unité d'exécution** | timer `inactive`/`dead` avec **prochain tir vide** ; unité d'exécution `inactive`/`dead`, **sortie constatée** ; **aucun processus du superviseur vivant** |
| **`PR-2`** | `<unité-pont>` | unité `inactive`/`dead`, `Result=success`, **aucun redémarrage automatique** ; **cadence de connexions au démon interrompue — zéro nouvelle connexion en 25 s** |

> **Pourquoi la distinction compte.** `W4-C` §9.1 exige *qu'*une méthode soit
> produite et consignée ; `W4-C` §16.1 dit **laquelle** a effectivement établi
> l'arrêt. `G.2` reprend la seconde sans l'alléger, et cite la première pour ce
> qu'elle impose.

**`W4-C` §8.1 fonde `PR-1`**, et sa raison est opératoire : *« Arrêter le timer
empêche les déclenchements futurs et **n'interrompt pas** une exécution déjà en
cours »* ; *« un cycle qui a franchi son test de mission attend **90 s** avant de
re-sonder, et conserve pendant toute cette attente le pouvoir de redémarrer la
machine »*. D'où la règle : *« “Timer inactif” n'équivaut **jamais** à
“superviseur neutralisé”. »*

### 2.5 Conséquence assumée — `G.2` lève aussi l'acte réservé 3

Satisfaire `PR-1` et `PR-2` **est** la neutralisation du dispositif historique,
c'est-à-dire l'acte réservé **3** de `w4f` §11.1. Il n'y a pas de troisième voie.

`lifecycle.py` lie d'ailleurs déjà les deux :

> *« cette question relève de W4-F, qui **seul peut neutraliser l'écrivain
> historique ET autoriser une écriture réelle** »* — docstring de
> `_composer_transaction`.

`G.2` étant un acte de W4-F, lever conjointement les actes 1, 2 et 3 est
cohérent avec ce que le module déclare.

> **Ce que cela coûte, et qui est accepté.** Pendant `G.2`, le pont ne publie
> plus et la télémétrie s'interrompt. C'est une **interruption de service
> visible**, bornée, et **suivie d'une restauration vérifiée en cinq étapes**
> (§11.2). L'acte reste intégralement réversible.

---

## 3. Clause `G.2` — amendement du séquencement de `w4f` §11.1

> **Clause d'exception — bornée, non générale.**
>
> Par dérogation au séquencement de `w4f` §11.1, les actes réservés **1**, **2**
> et **3** de cette clause peuvent être autorisés **une fois**, pour la seule
> campagne `G.2` définie au §9 du présent document, **sans que `W4-F3` soit
> ouvert ni audité**, et **sans que la coexistence ait été qualifiée** au sens de
> `w4f` §10.3.3.
>
> La levée de l'acte **3** est **strictement instrumentale** : elle n'autorise
> que ce qu'exigent `PR-1`, `PR-2` et la preuve *one-writer* du §8, pour la seule
> durée de la campagne, et **impose** la restauration vérifiée du dispositif
> historique selon les **cinq étapes** de `W4-C` §13 (§11.2).
>
> L'acte réservé **4** — **bascule de souveraineté** — demeure **intégralement
> interdit**. **Aucune bascule permanente de souveraineté n'est créée, ni
> préparée, ni rendue plus proche.**
>
> Cette dérogation **MUST** faire l'objet d'une **autorisation humaine explicite
> et distincte**, postérieure à l'audit du présent document, et **portant
> nommément sur `G.2`**.
>
> Elle **MUST NOT** être déduite : ni de l'audit de ce document, ni de son
> intégration, ni de la clôture d'un lot quelconque, ni du fait que
> `[transaction_surface].enabled` **puisse** valoir `true`.
>
> **La dérogation s'éteint à l'achèvement de `G.2`**, quel qu'en soit le
> résultat, `ABORT` compris. Elle ne se reconduit pas, **ne crée aucune autorité
> permanente**, et **aucune seconde campagne ne s'en autorise**.

### 3.1 Amendement de `w4f` §11.3

> **Clause.** La phrase de `w4f` §11.3 — *« W4-F4 est le seul sous-lot où une
> écriture réelle est possible »* — est amendée comme suit, et uniquement comme
> suit :
>
> *« W4-F4 est le seul **sous-lot** où une écriture réelle est possible.
> La campagne `G.2`, qui n'est pas un sous-lot mais une **exception bornée**
> définie par `w4f-g2-ecriture-bornee.md`, en admet **une**, sous les conditions
> de ce document. »*
>
> Aucune autre ligne de la table des phases n'est modifiée. `W4-F3`, `W4-F4` et
> `W4-F5` demeurent non ouverts.

### 3.2 Pourquoi l'acte réservé 2

Le chemin d'écriture de Boilerack **ne passe que par la surface
transactionnelle** : `lifecycle.py` ne compose l'écrivain que si
`config.transaction_surface.enabled` est vrai. Autoriser l'acte 1 sans l'acte 2
produirait une autorisation **inexécutable**.

---

## 4. `C1` et `E8` — traitement explicite, sans substitution

### 4.1 Ce qui est retiré

Toute idée de **substituer une surveillance à `C1`** est retirée. Le corpus
l'interdit :

> *« **E8 n'est pas un laissez-passer.** Il serait tentant de raisonner ainsi :
> le régime est indéterminé, mais E8 arrêtera tout si `C1` est dépassée, donc on
> peut essayer. **Non.** E8 est une défense **pendant** une exposition dont la
> **précondition logique est établie** ; **il ne remplace pas cette
> précondition.** Une exposition dont on ne sait pas si le critère qui la garde a
> un sens n'est pas une exposition gardée. »*
> — `w4f1` §8.2.1

### 4.2 Pourquoi la question ne se pose plus sur la fenêtre

`C1` borne l'occupation cumulée de la liaison **face au budget de 5 s du
superviseur** (`w4f1` §8.5). C'est une contrainte de **coexistence**.

Or `PR-1` neutralise le superviseur, `PR-2` arrête le pont, et le §8 exige une
fenêtre sans aucune ouverture de connexion au démon.

> **Pendant `G.2`, il n'y a plus de sonde du superviseur à protéger.** Le budget
> de 5 s n'est pas *tenu* : il est **sans objet**, faute de sonde pour le
> consommer.

**`C1` demeure en vigueur, non satisfaite, non violée, et non applicable à la
fenêtre de `G.2`.**

> **Clause.** `G.2` **MUST NOT** être invoqué pour affirmer que `C1` serait
> satisfaite, calculable, ou dispensable ailleurs. Hors la fenêtre où les §7 et
> §8 sont établis, `C1` reprend pleinement son empire.

**`AB-4` conserve néanmoins son office** : une invocation dépassant nettement le
budget de 5 s connu (`E3`) est un abandon, que le superviseur soit neutralisé ou
non. La disparition de la sonde ne rend pas les durées inintéressantes.

---

## 5. Portée exacte

### 5.1 Ce que `G.2` lève, une fois

- une **écriture réelle**, sur un rôle unique, une valeur unique ;
- l'**ouverture temporaire** de `[transaction_surface].enabled`, **effective**
  au sens du §9 temps 8, et éteinte au sens du §11.1 ;
- la **neutralisation temporaire** du dispositif historique, bornée à `PR-1`,
  `PR-2` et au §8, suivie de la restauration en **cinq étapes** du §11.2 ;
- **au plus une seconde écriture** — la restauration de la valeur — dans le seul
  cas nominal, et sur décision humaine (§10).

### 5.2 Ce que `G.2` ne lève pas

| Objet | État |
|---|---|
| bascule de souveraineté | **interdite** — `w4f` §11.1 acte 4 |
| toute écriture sur un **second rôle** | **interdite** — §6 |
| toute commande **ECS** — `setTempWWsoll` | **interdite** — §6.2 |
| toute **modification** du pont, du superviseur ou de leurs unités | **interdite** — seuls l'arrêt et la remise en marche sont admis |
| toute **activation au démarrage** de `<unité-boilerack>` | **interdite** — `G-a`, §11.3 |
| toute **instrumentation nouvelle**, en particulier vers la levée de `U-3` | **hors périmètre** — §8.1 |
| toute **seconde campagne** | **interdite** — §3, extinction |
| `W4-F3`, `W4-F4`, `W4-F5` | **non ouverts** |
| `T0`, `T1`, `T2`, `Acte B` | **non ouverts** |
| autorité permanente d'écriture | **aucune n'est créée** |

> **Le pont historique demeure l'unique écrivain réel de production**, hors la
> fenêtre de `G.2`, pendant laquelle il est **arrêté** et où **personne d'autre
> que Boilerack n'écrit**, au sens borné du §8.1.

---

## 6. Le rôle unique

### 6.1 `heating_curve_shift`, et lui seul

| | |
|---|---|
| Rôle | `heating_curve_shift` |
| Lecture | `getNiveauM1` |
| Écriture | `setNiveauM1` |
| Type | entier |
| Bornes | `[-13 ; 40]` |
| Pas | `1` |
| Tolérance de confirmation | **`0`** — égalité stricte |

Sources : `core/production_profile.py`, seul rôle inscriptible déclaré ; `A5x`
**§4**, qui extrait le §5.3 de `arsenal … boiler_pi/mqtt.md` pour les bornes et
le pas ; `c7` §4.2 pour le vocabulaire du rôle.

`W4-C` §12.3.2 rappelle que ce datapoint est **à égalité stricte** — `A5` §5.3.

### 6.2 Pourquoi ce rôle, et pourquoi pas l'ECS

> *« Une seule a été **CARACTÉRISÉE** : `setNiveauM1`, par la campagne terrain
> W4-C du 22 août 2026. Les trois autres n'ont reçu aucune observation de leur
> réponse à l'écriture. […] Déclarer ici les trois autres reviendrait à ouvrir
> des surfaces d'écriture sur la foi d'une extrapolation. »*
> — `core/production_profile.py`

`setTempWWsoll` **n'est pas déclaré au profil de production**.

### 6.3 Une différence avec `W4-C`, qu'il faut nommer

`W4-C` a écrit **à l'identique** — *« `V_canon` désigne la même valeur que
`V_brut`, la campagne ne déplace rien »* (`W4-C` §14, champ 7). **`G.2` déplace
la valeur d'un pas.**

Ce déplacement est **prévu** par `w4f` §7.3 — *« une valeur voisine, dans les
bornes, choisie réversible »* — mais il **retire à `G.2` une part de la sûreté de
`W4-C`** : une écriture à l'identique ne propage rien, tandis qu'un déplacement
d'un pas modifie réellement une consigne de chauffe. C'est pourquoi `EI-1` —
circuit au repos — n'est pas décoratif.

**Conséquence directe sur la restauration** : `W4-C` §13 étape 1 fait confirmer
que la valeur en place **concorde avec `V_brut`**, ce qui va de soi pour une
écriture à l'identique. Sous `G.2`, cette concordance n'est attendue **que si la
restauration a été exécutée**. L'étape est donc **transposée**, non allégée —
§11.2.

---

## 7. État initial sûr — les treize preuves `EI-1..EI-13`

`W4-C` §9 énonce huit étapes de préparation, *« dans l'ordre. Aucune étape n'est
facultative. »* Elles sont reprises **sans allègement**, et complétées des
preuves propres à Boilerack, que `W4-C` n'avait pas à produire puisqu'il
n'employait pas Boilerack.

> **La numérotation `EI-1..EI-13` est propre à `G.2`.** Elle ne prétend pas
> exister ailleurs : chaque ligne porte sa source, et aucune n'est inventée.

| Réf | Preuve exigée | Source |
|---|---|---|
| **`EI-1`** | **circuit au repos, hors saison de chauffe** — état analogue à celui constaté en `W4-C` §16.1 : **brûleur à `0,0 %`**, M1 au repos ; relevé et consigné **avant** l'acte | `W4-C` §9 (1), `C5` §12.1, `W4-C` §16.1 |
| **`EI-2`** | **exploitant physiquement devant la machine**, du début à la fin. *« “Joignable à distance” ne satisfait pas cette condition, et une session distante encore moins »* | `W4-C` §9 (2) |
| **`EI-3`** | **plan de reprise physique connu et accepté** — la campagne neutralise le superviseur, *« donc aussi la remise en état automatique dont il est porteur »* | `W4-C` §9 (3) |
| **`EI-4`** | **atelier** créé, vide, sur stockage persistant, **hors de tout dépôt versionné** | `W4-C` §9 (4), §16.1 |
| **`EI-5`** | **`PR-1`** — superviseur neutralisé, aux critères de `W4-C` §16.1 rappelés au §2.4 | `W4-C` §9 (5), §8.1, §9.1, §16.1 |
| **`EI-6`** | **`PR-2`** — pont arrêté, aux critères de `W4-C` §16.1 rappelés au §2.4 | `W4-C` §9 (6), §9.1, §16.1 |
| **`EI-7`** | **démon `vcontrold` actif et jamais touché** — `active`/`running`, confirmé par une **lecture nue de code retour `0`** avant d'aller plus loin | `W4-C` §9 (7), §16.1 |
| **`EI-8`** | **preuve *one-writer*, dans la forme établissable du §8.1** — inventaire des unités inscriptibles toutes inactives · aucune session `G.2` ouverte · **fenêtre muette de 12 s sans aucune ouverture au journal du démon** | `W4-C` §16.1 — forme et limites au **§8** |
| **`EI-9`** | **retour arrière armé avant toute écriture** — valeur relevée, forme canonique dérivée, commande **écrite d'avance** | `W4-C` §9 (8), §12 ; `w4f` §7.3 |
| **`EI-10`** | **concordance des deux formes d'une même lecture** — **forme texte** *et* **forme `-J`**, capturées par **`vclient` nu, hors du chemin Boilerack** ; concordance **brute** *et* **sémantique** ; `V_canon` dérivable de `V_brut` **sans perte** | `W4-C` §11.3, §12.3.1 (`AB-2`), `AB-9` |
| **`EI-11`** | **autorité constatée sur le fichier persisté** après `enabled = true` — jamais sur l'état courant du processus | `w4f` §7.2.1, encadré `G-b` |
| **`EI-12`** | **surface transactionnelle réellement composée et souscrite**, **après le démarrage manuel** de `<unité-boilerack>` — établie par une **trace côté broker**, jamais par l'état interne de Boilerack | `W1` `A15` / `A16` ; `W4-E2` |
| **`EI-13`** | **observabilité disponible et relevée sur les trois plans** — invocations Boilerack, **journal du démon**, **trace broker** | `FA-9` ; `w4f` §10.3.1 précondition 6 |

> **`EI-10` ne peut pas passer par Boilerack, et c'est le code qui le dit.**
> `W4-C` §12.3.1 compare **la forme texte et la forme `-J`** d'une même lecture,
> à deux niveaux — *« concordance brute »* et *« concordance sémantique »* —,
> tous deux requis. `W4-C` §12.3.2 précise que les étapes 01 et 02 produisent
> *« ensemble, trois formes : le texte, le champ `raw` et le champ numérique »*.
>
> Or `VClientCliReader` construit `[…, "-J", "-c", command]` et sa docstring le
> déclare : *« `-J` (JSON long) est la seule option de sortie utilisée »*.
> **La forme texte n'existe pas dans le chemin de lecture de Boilerack.**
>
> `EI-10` est donc établie par **deux captures `vclient` nues** — une en texte,
> une en `-J` —, hors du chemin Boilerack, exactement comme les étapes 01 et 02
> de `W4-C`. **Ce sont des lectures : elles n'ajoutent aucune écriture**, et ne
> modifient donc pas la cardinalité du §9.

> **`EI-12` n'est pas une formalité, et c'est `W1` qui l'impose.**
> `A15` : *« W0 garantit la **réémission** d'un SUBSCRIBE, **jamais son
> acceptation** par le broker : aucune corrélation SUBACK n'existe. »*
> `A16` : *« `online` **ne signifie pas** “souscriptions restaurées”. »*
>
> Boilerack **ne peut donc pas prouver depuis lui-même** qu'il est souscrit. Une
> commande publiée sur un topic non souscrit ne serait jamais reçue, et l'absence
> d'`ACK` serait indiscernable d'un échec d'écriture. **La preuve est côté
> broker, ou elle n'existe pas.**

> **Aucune preuve `EI` n'est facultative.** L'échec de l'une quelconque relève du
> §12 — `FA-1`, `FA-2`, `FA-3`, `FA-4`, `FA-9`, `AB-2`, `AB-9` selon le cas — et
> **interdit d'engager l'écriture**.

---

## 8. *One-writer* — la preuve établissable, et ce qu'elle ne couvre pas

### 8.1 La preuve de `W4-C`, et sa transposition honnête

`W4-C` §16.1 établit le *one-writer* par **trois constats cumulatifs**, et non
par `PR-1` et `PR-2` seuls :

> *« **one-writer** — trois unités inscriptibles inactives, une seule session
> ouverte, **zéro connexion tierce au démon en 12 s**. »*

**Les deux premiers termes se transposent tels quels.** Le troisième, non — et il
faut dire pourquoi plutôt que de le recopier.

> **Pourquoi « zéro connexion *tierce* » ne se transpose pas littéralement.**
> Qualifier une connexion de *tierce* suppose de l'**attribuer à un client**. Or
> `cloture` §5 laisse **`U-3`** — *« capacité du journal `vcontrold` : clôture,
> durée, **attribution par client** »* — en
> `PREUVE TERRAIN / SOURCE EXTERNE REQUISE`, et `ouverture` §2 le constate sans
> détour : le journal *« ne porte que les ouvertures de connexion, **sans clôture
> ni attribution par client** »*.
>
> `W4-C` n'a pas rencontré la difficulté : **Boilerack n'était pas installé**, et
> aucun client légitime n'ouvrait de connexion pendant sa fenêtre. Sous `G.2`,
> `P-1` suppose Boilerack déployé, et `w4f` §4.3 chiffre sa charge : *« environ
> **onze invocations par minute** (trois à 30 s, cinq à 60 s) »*. Compter des
> ouvertures ne dirait alors pas **de qui** elles viennent.

> **Clause — forme établissable de `EI-8`, et elle seule.**
>
> La preuve *one-writer* de `G.2` est constituée de **trois constats
> cumulatifs**, tous relevés **au temps 5** :
>
> 1. **inventaire des unités inscriptibles** — dressé au titre de `P-5`, et
>    **chacune** constatée inactive. `PR-1` et `PR-2` n'en couvrent que deux ;
> 2. **aucune session `G.2` ouverte** — `<unité-boilerack>` **arrêtée**, et
>    aucune invocation `vclient` de l'exploitant en cours ;
> 3. **fenêtre muette de 12 s** — sur douze secondes consécutives, le journal du
>    démon **ne porte aucune ouverture de connexion**.
>
> **Aucune attribution n'est revendiquée.** Le constat 2 rend le constat 3
> concluant sans elle : si aucun participant de `G.2` n'émet, **toute** ouverture
> observée serait nécessairement tierce, et **zéro ouverture** vaut donc **zéro
> connexion tierce**. C'est la seule forme que les moyens réellement disponibles
> permettent d'opposer, et elle n'exige du journal que ce qu'il porte —
> l'horodatage des **ouvertures**.

> **Ce que cette forme coûte, et qui est assumé.** La fenêtre muette impose que
> `<unité-boilerack>` soit **arrêtée jusqu'au temps 8**. C'est sans conséquence
> pour la campagne : la surface de lecture n'est requise par aucun temps
> antérieur, et `EI-7` comme `EI-10` passent par `vclient` **nu**.
>
> **La preuve porte sur douze secondes, pas sur la campagne.** Elle établit
> l'absence d'ouverture tierce **au moment où elle est prise**, jamais sur toute
> la fenêtre. Ce qui couvre la suite n'est pas une preuve mais une **détection** :
> **`FA-3`** et **`AB-8`** — §8.2.

> **L'autre voie, et pourquoi elle n'est pas prise ici.** Établir le même terme
> **avec Boilerack en marche** exigerait d'attribuer les connexions par client,
> donc de lever **`U-3`** — `PREUVE TERRAIN / SOURCE EXTERNE REQUISE`. Ce serait
> une mesure d'instrumentation, hors du périmètre de `G.2`, et le présent
> document **ne la demande pas, ne la prépare pas, et ne s'en autorise pas**.

### 8.2 `H2` et `H6` **(b)** — ce que la preuve ne ferme pas

`cloture` **§5** :

> **`H2`** — *« `PARTIEL` — invariant sur la fenêtre protégée non établi dans la
> durée ; voies structurelles non instruites »*
>
> **`H6` (b)** — *« **OUVERT** — un participant extérieur agissant sur l'IPC
> System V ; **c'est `H2`**, qui l'absorbe »*

La preuve du §8.1 compte des **ouvertures de connexion au démon**. Un participant
agissant **directement sur l'IPC System V en `0666`** n'ouvre aucune connexion au
démon : **il n'apparaîtrait dans aucun des trois constats.**

> **Conséquence assumée, et elle est sérieuse.** La preuve *one-writer* de `G.2`
> est **bornée aux clients du démon**, et **bornée à douze secondes**. `H2` et
> `H6` **(b)** demeurent **OUVERTES**, et `G.2` **ne les ferme pas, ne les réduit
> pas, et ne s'en autorise pas**.
>
> Ce qui reste pour les couvrir n'est pas une preuve mais une **détection** :
> **`FA-3`** — *« preuve **ou suspicion** d'un second écrivain — **toute valeur
> qui bouge sans commande émise** »* — et la garde de fraîcheur **`AB-8`**. Une
> détection n'est pas une garantie, et le présent document ne la présente pas
> comme telle.

---

## 9. Protocole — la campagne, dans cet ordre

| Temps | Acte | Preuve |
|---|---|---|
| **1** | établir **`EI-1` à `EI-4`** — repos, présence, plan de reprise, atelier | §7 |
| **2** | établir **`PR-1`** (`EI-5`), de préférence juste après un cycle nominal | §7 ; `W4-C` §8.1 |
| **3** | établir **`PR-2`** (`EI-6`) | §7 |
| **4** | établir **`EI-7`** — démon actif, **lecture nue code retour `0`** | §7 |
| **5** | **`<unité-boilerack>` arrêtée**, puis établir **`EI-8`** — inventaire, aucune session `G.2`, **fenêtre muette de 12 s** | §8.1 |
| **6** | **lire** `getNiveauM1` par **deux captures `vclient` nues** — **texte** puis **`-J`** — constituer `V_brut`, en dériver `V_canon`, établir **`EI-10`** | §7 ; `W4-C` §12.3.1 |
| **7** | **armer** la restauration — `EI-9` : commande écrite d'avance, **non exécutée** | §10 |
| **8** | **persister** `enabled = true` et établir **`EI-11`** ; **démarrer `<unité-boilerack>` à la main** ; établir **`EI-12`** puis **`EI-13`** | encadré ci-dessous |
| **9** | **relire** `getNiveauM1` — **garde de fraîcheur**, en **`-J` seul** : concordance avec `V_brut` exigée, sinon **`AB-8`** | `W4-C` §11.1, §12.3.2 |
| **10** | **écrire** `V_canon + 1`, si et seulement si `V_canon + 1 ≤ 40` — **une seule écriture** | §15 |
| **11** | **relire** — **égalité stricte** exigée avec `V_canon + 1`, sinon **`AB-1` transposé** | §6.1 ; §12.2.1 |
| **12** | **conduite de restauration de la valeur** selon le §10 | §10 |
| **13** | **éteindre toute capacité d'écriture** selon le §11.1 | §11.1 |
| **14** | **restaurer le dispositif historique** — **les cinq étapes de `W4-C` §13** | §11.2 |

**Au plus deux écritures. Aucune autre commande, aucun autre rôle, aucune
répétition, aucune rafale.**

> **La cardinalité des écritures est explicite**, sur le modèle de `W4-C` §11.2 :
> **une** au temps 10, **au plus une** au temps 12, **zéro** partout ailleurs.
> Les lectures des temps 4, 6, 9, 11 et de l'étape 1 du §11.2 n'entrent pas dans
> ce décompte : ce sont des lectures.

> **Clause — ouverture réelle de l'autorité, temps 8.**
>
> Le fait porteur du §11.1 est **symétrique**, et la V3 ne l'appliquait qu'à la
> fermeture : l'autorité étant **lue au démarrage du processus** (`W4-E2`),
> persister `enabled = true` **n'ouvre rien** sur un processus déjà lancé, de la
> même façon que persister `false` n'y ferme rien. `lifecycle.py` compose la
> surface **une fois**, à l'assemblage, en passant `_composer_transaction(config)`
> à `build_runtime` ; **aucun rechargement n'existe** dans le module.
>
> Le temps 8 comporte donc **trois actes, dans cet ordre** :
>
> 1. **persister** `enabled = true`, et le **prouver sur le contenu du fichier
>    déployé** — `EI-11` ;
> 2. **démarrer `<unité-boilerack>` à la main**, puisqu'elle est arrêtée depuis
>    le temps 5 et **non activée au démarrage** (`G-a`) ;
> 3. **prouver la surface réellement composée et souscrite** par une **trace côté
>    broker** — `EI-12` —, jamais par l'état interne de Boilerack.
>
> **`G-a` est préservée : démarrer n'est pas activer au démarrage.** Un démarrage
> manuel ne rend pas l'unité active au boot, et l'état de non-activation
> **MUST** rester constaté sur toute la fenêtre (§11.3). Sans l'acte 2, `EI-12`
> serait insatisfiable et l'écriture du temps 10 **inexécutable** — l'autorisation
> serait précisément celle que le §3.2 qualifie d'inexécutable.

> **Pourquoi le temps 9 reste en `-J` seul.** `W4-C` §12.3.2 l'admet
> explicitement : *« **L'absence d'une forme n'est pas une divergence.** Une
> capture en `-J` seul ne porte pas de ligne de texte : on compare son `raw` et
> son champ numérique, et c'est tout. »* La garde de fraîcheur peut donc passer
> par le chemin de lecture de Boilerack, qui est en `-J`. **Seule `EI-10`, qui
> compare les deux formes entre elles, exige la capture texte** — d'où le
> temps 6.

### 9.1 Forme de l'invocation

Forme caractérisée par `W4-C` le 22 août 2026, **seule observée**, telle que
`adapters/vclient_write.py` la construit :

```
<executable> -J [-h <hôte>] [-p <port>] -c "setNiveauM1 <entier>"
```

La valeur est rendue **sous forme entière**, seule forme caractérisée. Aucune
constante de site ne figure dans le dépôt.

---

## 10. Restauration de la valeur — conduite conforme à `w4f` §7.3

`w4f` §7.3 distingue quatre cas et **interdit l'écriture supplémentaire dans
trois d'entre eux**.

| Cas au temps 11 | Conduite `G.2` | Fondement |
|---|---|---|
| l'écriture **n'a pas eu lieu** | **aucune écriture.** Restaurer serait écrire sans avoir caractérisé | `w4f` §7.3 cas 1 ; `W4-C` §12.1 |
| relecture **concordante** — `applied` | restauration **admise**, et **seulement** si l'autorisation humaine de `G.2` l'a explicitement pré-décidée. À défaut : aucune écriture | `w4f` §7.3 cas 2 — *« décision humaine, pas automatisme »* |
| **fenêtre épuisée sans autre information** — `timeout` nominal | **aucune écriture supplémentaire.** État *indéterminé* : l'établir par observation | `w4f` §7.3 cas 3 |
| relecture **discordante**, état changeant, ou critère `FA` / `AB` déclenché | **`ABORT`. Aucune écriture supplémentaire.** Décision humaine | `w4f` §7.3 cas 4 |

> **Clause propre à `G.2` — aucune restauration de la valeur après `ABORT`.**
>
> Cette restriction est **choisie par `G.2`**, et il faut le dire exactement :
> elle n'est **imposée par aucun texte amont**. `W4-C` §12.1 est plus permissif —
> l'étape d'écriture ayant été exécutée, il admet *« **0** écriture s'il
> **concorde** avec `V_brut` au sens de §12.3.2, **au plus 1** sinon »*. `G.2`
> **ne s'en prévaut pas** et retient la règle la plus stricte.
>
> Elle est **compatible avec `w4f` §7.3**, dont les cas 3 et 4 interdisent déjà
> l'écriture supplémentaire, et elle **étend cette interdiction au cas 2 dès lors
> qu'un `ABORT` est prononcé**. Motif : écrire dans un état que le corpus
> qualifie d'*indéterminé* ou de *non maîtrisé* ajoute un risque à un moment où
> l'on a précisément cessé de comprendre l'installation.
>
> **Ce que `W4-C` §12.1 impose et qui est repris tel quel** : le critère est le
> **fait objectif** que l'écriture ait eu lieu, *« jamais le critère d'abandon qui
> a été déclenché »* ; et le corollaire — *« `ecritures_nominales == 0`
> **implique** `ecritures_restauration == 0` »*.
>
> **Ce que `W4-C` §12.4 impose et qui est repris tel quel** : l'**ordre** de la
> conduite d'abandon — *« appliquer §12.1 […], rétablir §13, **puis** rapporter.
> **Aucune seconde tentative dans la même fenêtre.** »* Cet ordre est celui du
> §12.3.

> **Ce qui est dû en toute hypothèse** : la commande de restauration **MUST** être
> **armée et écrite par avance** (`EI-9`), *« et recopiée le moment venu plutôt
> que reconstruite sous pression »*. **Armer n'est pas exécuter.**

> **Distinction portante.** *Indéterminé* signifie « la fenêtre n'a pas suffi à
> conclure » ; *non maîtrisé* signifie « une observation contredit ce qui était
> attendu ». Les confondre ferait traiter une discordance réelle comme une
> attente trop courte.

---

## 11. Extinction de la capacité d'écriture, restauration, garde anti-reboot

### 11.1 Fermeture réelle de l'autorité — trois actes, dans cet ordre

Fermer l'autorité **n'est pas** basculer une clé. Deux faits du corpus
l'imposent :

- l'autorité est **lue au démarrage du processus** (`W4-E2`) : la lever en
  mémoire ne ferme rien sur un processus déjà lancé — et, symétriquement, la
  poser n'y ouvre rien (§9, temps 8) ;
- **`W1` `A17`** : *« Une souscription logique est **irrétractable** : aucun
  `unsubscribe` n'existe, et un `disconnect()` ne vide pas le registre. »* Le
  topic de commande reste souscrit tant que le processus vit.

> **Clause — extinction complète, avant toute restauration du pont.**
>
> 1. **persister** `[transaction_surface].enabled = false` dans le fichier de
>    configuration, et **le prouver sur le contenu persisté** — jamais sur
>    l'état courant du processus (`w4f` §7.2.1, encadré `G-b`) ;
> 2. **arrêter effectivement** `<unité-boilerack>`, et **constater l'arrêt** —
>    unité `inactive`/`dead` ;
> 3. **attendre et constater la libération effective de la liaison**, `T_release`
>    étant bornée par un cycle complet (§12.3).
>
> Ces trois actes **MUST** être achevés et prouvés **avant** le temps 14.
> Remettre le pont pendant qu'un Boilerack écrivain vit encore **recréerait
> exactement les deux écrivains** que `PR-1`, `PR-2` et le §8 avaient éliminés.

### 11.2 Restauration de l'état normal — les cinq étapes de `W4-C` §13

`W4-C` §13 — *« Restauration de l'état normal »* — prescrit **cinq étapes**,
*« dans cet ordre, et vérifié à chaque étape »*, et conclut : *« **La campagne
n'est close qu'après l'étape 5.** »*

> **La V3 n'en portait que deux, et omettait l'étape 5 entière.** C'était le
> défaut le plus grave de cette version : elle déclarait la restauration acquise
> alors que le superviseur n'avait pas été constaté revenu à son fonctionnement
> normal.

| Étape | Acte | Preuve exigée |
|---|---|---|
| **1** | **confirmer par une lecture nue** la valeur en place, et la comparer à `V_brut` au sens de `W4-C` §12.3.2 | lecture consignée — **transposition au §11.2.1** |
| **2** | **redémarrer `<unité-pont>`** | commande consignée |
| **3** | **constater sa reprise effective, en amont ET en aval** — les **trois faits distincts** de `W4-C` §13.1. *« Une trentaine de secondes suffit à lever le doute. »* | **A**, **B**, **C** ci-dessous |
| **4** | **redémarrer `<timer-guard>`** | commande consignée |
| **5** | **confirmer que le superviseur repasse un cycle nominal sans action corrective, ET que son unité d'exécution retrouve son alternance normale** (`W4-C` §8.1) | cycle observé de bout en bout |

> **L'étape 3 interdit une source, nommément.** *« La sortie standard du pont
> **MUST NOT** servir ici : elle est mise en tampon »* (`W4-C` §13, étape 3,
> renvoyant à `W4-C` §9.1).

**Les trois faits distincts de l'étape 3** — `W4-C` §13.1 :

| | Fait | Constaté par |
|---|---|---|
| **A** | le pont est **actif** | l'unité `<unité-pont>` redevenue active |
| **B** | le pont **sonde** le démon | la **cadence de connexions repartie dans le journal du démon** (`W4-C` §9.1) |
| **C** | le pont **publie** | la **télémétrie effectivement observée depuis un consommateur aval** |

> **Pourquoi les trois, et pourquoi la V3 avait tort de n'en nommer que deux.**
> `W4-C` §13.1 : *« Aucun des trois ne remplace les autres. A sans B décrirait un
> processus qui tourne sans travailler. **B sans C est précisément le piège** :
> la cadence côté démon prouve que le pont *interroge la chaudière*, jamais qu'il
> *diffuse ce qu'il lit*. »*
>
> La V3 écrivait *« reprise de la **cadence de publication** constatée »* — une
> formule qui **fusionne B et C**, exactement la confusion contre laquelle le
> §13.1 met en garde. `W4-C` §13 qualifie l'issue correspondante de **pire
> possible** : *« un pont qu'on croit redémarré et qui ne publie plus serait la
> pire issue possible de cette campagne — pire que n'importe quel résultat
> négatif »*.
>
> *« L'observation aval **MUST** donc être faite, et consignée. Elle est ici une
> preuve **requise**, non un complément. »*

> **L'étape 5 a une durée, et elle n'est pas nulle.** Le superviseur *« sonde
> toutes les 3 minutes »* (`w4f` §4.3). Observer *« un cycle nominal sans action
> corrective »* suppose donc d'attendre au moins un cycle complet. La campagne
> reste ouverte jusque-là.

> **`PR-1` et `PR-2` sont redoublées ici.** `W4-C` §13 : *« le rapport porte non
> seulement comment l'arrêt a été établi, mais **comment la reprise l'a été**.
> Redoublées, non interchangeables — elles ne reposent pas sur les mêmes moyens,
> et §9.1 dit lesquels. »*

> L'impossibilité de prouver **l'une quelconque** des cinq étapes — `A`, `B` ou
> `C` comprises — est **`FA-11`**, *« impossibilité de prouver le rollback de
> souveraineté »*, et déclenche `ABORT`.

#### 11.2.1 Transposition de l'étape 1, et pourquoi elle est nécessaire

`W4-C` écrivait **à l'identique** : la valeur en place devait donc concorder avec
`V_brut`, et l'étape 1 le vérifiait sans réserve. **`G.2` déplace la valeur d'un
pas** (§6.3), et la valeur légitimement en place à cette étape dépend de ce qui
a **effectivement été exécuté**, non de l'endroit où la campagne s'est arrêtée.

> **Clause.** L'étape 1 est **exécutée dans tous les cas** — c'est une lecture
> nue, elle n'écrit rien —, et son résultat est **consigné**. La valeur à
> laquelle elle est comparée est **`V_attendue`**, au sens du **prédicat unique
> du §12.2.1**, et d'aucun autre.
>
> En particulier : si l'écriture du temps 10 **n'a pas été exécutée** — abandon
> antérieur, quelle qu'en soit la cause —, `V_attendue` vaut **`V_brut`**, et
> **`V_canon + 1` n'est pas attendue**. Si l'écriture a été exécutée sans que la
> restauration le soit, `V_attendue` vaut **`V_canon + 1`**. Si la restauration a
> été exécutée, elle vaut de nouveau **`V_brut`**.
>
> **Une valeur qui ne concorde avec aucune des deux références** n'est pas un
> détail de transposition : c'est une **valeur qui a bougé sans commande émise**,
> donc **`FA-3`**.
>
> Cette transposition **n'allège rien** : elle conserve la lecture, la
> comparaison et la consignation, et ajoute un cas d'abandon là où `W4-C` n'en
> avait pas besoin.

### 11.3 Garde anti-reboot — `w4f` §7.2.1 intégré

`w4f` §7.2.1 nomme le risque :

> *« Si son unité est activée au boot **et** que la configuration persistée porte
> encore `[transaction_surface].enabled = true`, alors un reboot de rollback
> relance **simultanément** le pont historique et un Boilerack **capable
> d'écrire**. Le filet censé rétablir l'unicité produirait exactement ce qu'il
> doit empêcher. »*
>
> **Règle normative.** *« Un redémarrage machine **MUST NOT** être considéré
> comme un mécanisme de rollback de souveraineté tant qu'il n'est pas **prouvé**
> qu'au redémarrage le pont historique peut revenir **sans que Boilerack retrouve
> simultanément une capacité d'écriture**. »*

`w4f` §7.2.1 offre trois familles — `G-a` unité non activée au démarrage, `G-b`
configuration persistée à `false`, `G-c` équivalent prouvé.

> **Clause — `G.2` retient `G-a` ET `G-b`, cumulées.**
>
> - **`G-a`** : `<unité-boilerack>` **MUST NOT** être activée au démarrage
>   pendant toute la fenêtre de `G.2`, et cet état **MUST** être prouvé **avant**
>   le temps 8, puis **reconstaté après le démarrage manuel** de ce même temps.
>   **Démarrer une unité n'est pas l'activer au démarrage** : l'acte 2 du temps 8
>   ne touche pas `G-a` ;
> - **`G-b`** : hors les temps 8 à 13, la configuration **persistée** **MUST**
>   porter `enabled = false`, prouvé **sur le contenu du fichier**.
>
> Le cumul est délibéré : `G-a` protège pendant que l'autorité est ouverte,
> `G-b` protège dès qu'elle est refermée. **Aucune des deux ne suffit seule sur
> toute la fenêtre.**
>
> **`EI-3` reste un recours, jamais une étape.** `W4-C` §9 (3) : le redémarrage
> machine *« n'est pas une étape du protocole : c'est un recours, connu d'avance,
> qu'aucune étape ne prescrit »*. `G.2` ne le prescrit pas davantage, et **MUST
> NOT** l'employer comme rollback tant que `G-a` et `G-b` ne sont pas l'une et
> l'autre prouvées.

---

## 12. `ABORT` — référentiel d'une campagne d'écriture

### 12.1 Le référentiel applicable

`w4f` §10.3.2 réserve `F2A-1..F2A-8` à `W4-F2`, terrain de lecture seule, et
précise que les critères `FA` *« supposent une campagne d'écriture et un
dispositif historique neutralisé »*. **C'est exactement la situation de `G.2`.**

`G.2` adopte donc **`FA-1..FA-12`** et **`AB-1..AB-9`**, **intégralement et sans
retrait**.

### 12.2 Les deux tables

**`FA` — niveau campagne** *(`w4f` §8)*

| Réf | Déclencheur | Portée dans `G.2` |
|---|---|---|
| **`FA-1`** | impossibilité de prouver la neutralisation du superviseur (`PR-1`) | `EI-5` |
| **`FA-2`** | impossibilité de prouver l'arrêt du pont (`PR-2`) | `EI-6` |
| **`FA-3`** | **preuve ou suspicion d'un second écrivain — toute valeur qui bouge sans commande émise** | **seul recours face à `H2` / `H6` (b)**, au-delà des 12 s de `EI-8` — §8 ; et §11.2.1 |
| **`FA-4`** | démon `vcontrold` injoignable ou changeant d'état | `EI-7` |
| **`FA-5`** | réponse de transport anormale ou non caractérisée | temps 10 |
| **`FA-6`** | relecture absente | temps 11 |
| **`FA-7`** | relecture discordante après écriture | temps 11 ; `w4f` §7.3 cas 4 |
| **`FA-8`** | redémarrage inattendu d'un service ou de la machine | toute la fenêtre |
| **`FA-9`** | **perte de la connectivité utile à l'observation** | `EI-13` — invocations, journal démon, **trace broker** |
| **`FA-10`** | **`ACK` incohérent avec l'observation directe** | l'`ACK` publié par Boilerack **MUST** être confronté à la relecture ; leur divergence est un abandon, non un détail |
| **`FA-11`** | impossibilité de prouver le rollback de souveraineté | §11.2 — **l'une quelconque des cinq étapes**, `A`/`B`/`C` comprises —, §11.3 |
| **`FA-12`** | doute de l'exploitant, sans justification à fournir | toute la fenêtre |

**`AB` — niveau capture** *(`W4-C` §12.4)*

| Réf | Déclencheur | Portée dans `G.2` |
|---|---|---|
| **`AB-1`** | une relecture ne concorde pas avec `V_brut` au sens de `W4-C` §12.3.2, à n'importe quelle étape | **transposé — §12.2.1.** Le terme de référence suit la **valeur attendue** ; tout le reste du critère est inchangé |
| **`AB-2`** | la concordance des **deux formes d'une même lecture** échoue, avant l'écriture | `EI-10` — temps 6 |
| **`AB-3`** | le démon change d'état, ou devient injoignable | `EI-7` |
| **`AB-4`** | une invocation dépasse nettement le budget de 5 s connu (`E3`) | **conservé** — §4.2 |
| **`AB-5`** | un service redémarre, ou la machine redémarre, pour quelque cause | toute la fenêtre |
| **`AB-6`** | tout doute de l'exploitant, sans justification à fournir | toute la fenêtre |
| **`AB-7`** | durée mesurée négative, nulle ou manifestement absurde — l'horloge a bougé | *« la mesure et les suivantes ne valent plus rien »* |
| **`AB-8`** | la **garde de fraîcheur** de `W4-C` §11.1 échoue : avant l'écriture, la relecture ne concorde pas avec `V_brut` | temps 9 — **détection d'un second écrivain** |
| **`AB-9`** | `V_canon` n'est pas dérivable de `V_brut` **sans perte** | `EI-10` |

> **Interdiction reprise telle quelle.** *« Ne **jamais** provoquer délibérément
> un dépassement de budget ni un démon injoignable »* pour capturer une
> signature. *« Ces signatures se recueillent si elles surviennent, elles ne se
> fabriquent pas sur une installation en service. »* — `W4-C` §12.4

#### 12.2.1 Transposition de `AB-1` — le terme de référence, et lui seul

`AB-1` sanctionne une relecture *« qui ne concorde pas avec `V_brut` au sens de
`W4-C` §12.3.2, **à n'importe quelle étape** »*. Cette rédaction est juste pour
`W4-C`, qui écrivait **à l'identique** : la valeur en place y restait `V_brut`
d'un bout à l'autre.

> **`G.2` déplace la valeur d'un pas** (§6.3). Repris à la lettre, `AB-1` ferait
> donc déclencher un abandon au temps 11 **exactement lorsque l'écriture a
> réussi** — la relecture y valant `V_canon + 1`, et non `V_brut`. Le critère
> arrêterait la campagne sur son **succès nominal**.

> **Clause — transposition minimale.** Sous `G.2`, `AB-1` compare la relecture à
> `V_attendue`, et **rien d'autre du critère n'est modifié** : le sens de la
> comparaison reste celui de `W4-C` §12.3.2 — forme par forme parmi celles
> effectivement capturées, retrait déterministe du préfixe, neutralisation des
> espaces de bordure — et le datapoint reste **à égalité stricte** (`A5` §5.3).
>
> **La sélection du critère n'est pas transposée du tout.** Elle reste celle de
> `W4-C` §12.3.2 : *« **AB-8 avant l'étape 03, AB-1 à toute autre étape** »*.
> Seul le **terme de référence** change.

> **Clause — prédicat de `V_attendue`, et il est le seul du document.**
>
> `V_attendue` ne dépend **pas** du moment où la campagne se trouve, mais de
> **deux faits objectifs**, dans cet ordre :
>
> 1. **l'écriture du temps 10 a-t-elle été exécutée ?**
> 2. si oui, **la restauration du temps 12 a-t-elle été exécutée ?**
>
> | Fait objectif | `V_attendue` |
> |---|---|
> | écriture **non exécutée** | **`V_brut`** |
> | écriture exécutée, restauration **non exécutée** | **`V_canon + 1`** |
> | restauration **exécutée** | **`V_brut`** |
>
> **Ce prédicat vaut à toute étape**, y compris à l'étape 1 du §11.2 et après un
> `ABORT`, quelle qu'en soit la cause et quel qu'en soit le moment.
>
> **Ce que le prédicat interdit, et que la V5 permettait.** Une campagne
> interrompue **avant** le temps 10 tombe dans la première ligne : `V_attendue`
> y vaut **`V_brut`**. **`V_canon + 1` n'est jamais attendue tant que rien ne
> l'a écrite**, et `V_canon` n'est **référencé dans aucun cas antérieur à sa
> dérivation** au temps 6.
>
> **Le fait objectif se constate, il ne se suppose pas.** `W4-C` §12.2 en donne
> la méthode — *« aucun état nouveau n'est nécessaire : les captures du §10
> suffisent »* — et tranche le cas ambigu **dans le sens prudent** : une
> invocation lancée dont `.meta` est absent, *« dont on ignore l'issue est
> traitée comme une écriture ayant pu avoir lieu »*. Sous `G.2`, **« exécutée »
> s'entend en ce sens prudent**, pour la restauration comme pour l'écriture.
>
> **Conséquence assumée du sens prudent.** Une écriture lancée mais restée sans
> effet laisse la valeur à `V_brut` alors que `V_attendue` vaut `V_canon + 1` :
> la relecture diverge, et la campagne s'arrête. C'est **conservateur, non
> permissif**, et cohérent avec `w4f` §7.3 cas 3, qui traite déjà cet état comme
> *indéterminé* et interdit toute écriture supplémentaire.
>
> **Une valeur ne concordant avec aucune des deux références** — ni `V_brut`, ni
> `V_canon + 1` — est une **valeur qui a bougé sans commande émise** : c'est
> **`FA-3`**, et non un simple écart de relecture.

> **Ce que la transposition n'allonge pas, et ne relâche pas.**
>
> - **`AB-8` n'est pas touché.** Il porte sur la garde de fraîcheur de
>   `W4-C` §11.1, **avant** l'écriture, où `V_attendue` **est** `V_brut`. Sa
>   rédaction et son déclenchement sont identiques à ceux de la V4.
> - **Aucun critère antérieur à l'écriture n'est modifié** — `AB-2`, `AB-9`,
>   `EI-10` et le temps 9 restent tels quels.
> - **Aucune tolérance n'est introduite.** `W4-C` §12.3.2 : *« sans qu'aucune
>   tolérance supplémentaire ne soit introduite : le datapoint retenu est à
>   égalité stricte »*. La transposition change **le terme comparé**, jamais la
>   **rigueur** de la comparaison.
> - **La règle propre à `G.2` du §10 est intacte** : un `AB-1` transposé qui
>   déclenche au temps 11 est un `ABORT`, donc **aucune restauration de la
>   valeur** — la conduite est celle du §12.3.

> **Cohérence avec le §11.2.1.** Le prédicat ci-dessus est **le seul** du
> document : le §11.2.1 ne le redéfinit pas, il **y renvoie**. Les deux clauses
> portent sur des objets différents — `AB-1` pour les relectures de la campagne,
> l'étape 1 du §11.2 pour la lecture de restauration — et tirent leur
> `V_attendue` de la **même source unique**. C'est précisément ce qui était rompu
> en V5, où chacune portait sa propre table.

---

### 12.3 Conduite d'abandon

Ordre imposé par `W4-C` §12.4, **sans écriture supplémentaire** hors le cas
nominal du §10 :

1. **ne pas écrire** — la conduite de restauration de la valeur est celle du §10,
   *« qui peut ne prescrire **aucune** écriture »*, et dont la clause propre à
   `G.2` interdit toute restauration après `ABORT` ;
2. **éteindre la capacité d'écriture** selon le §11.1 — persister `false`,
   arrêter l'unité, **constater la libération de la liaison** ;
3. **rétablir** l'état normal selon le §11.2 — **les cinq étapes**, `A`, `B`,
   `C` compris ;
4. **rapporter**.

> **Aucune seconde tentative dans la même fenêtre.**

> **`T_release` — commander l'arrêt ne libère pas la liaison.**
> `w4f1` §8.6.1 : *« Un `run_due()` déjà engagé va jusqu'à son point de retour :
> le runner ne teste `stop.is_set()` qu'entre deux cycles, jamais à
> l'intérieur. »*
>
> ```
> T_release  ≤  8 × (R + ε)   ≈  32,2 s  au maximum publié C5 (4,029 s), hors ε
> ```
>
> **Conséquence opposable** : l'exploitant **MUST** attendre la libération
> effective avant le temps 14, et **MUST NOT** engager la restauration du pont
> avant elle.

> **Le budget de 90 s ne court pas pendant la fenêtre.** La contrainte
> `T_detection + T_reaction + T_release < 90 s` de `w4f1` §8.6.1 protège contre
> le redémarrage machine par le superviseur. Le superviseur étant neutralisé par
> `PR-1`, **cette horloge n'est pas armée** entre le temps 2 et l'étape 4 du
> §11.2. Elle reprend à ce réarmement, et la liaison **MUST** être libérée avant.

---

## 13. Bornage opposable

Chaque borne est **vérifiable sur un artefact**, indépendamment de la bonne
volonté de qui l'exécute.

| Borne | Opposable par | Ce qui la rendrait fausse |
|---|---|---|
| **un seul rôle inscriptible** | `core/production_profile.py` ne déclare qu'un `CommandSpec` avec `write` non nul | l'ajout d'un second rôle — visible en revue |
| **aucune commande ECS** | `setTempWWsoll` **absent** du profil | une commande ECS supposerait une modification du profil, donc un lot distinct |
| **égalité stricte à la relecture** | `confirm_tolerance = 0.0`, appliqué par le cœur ; `A5` §5.3 | toute tolérance non nulle serait une modification de code |
| **autorité fermée hors la fenêtre** | **contenu persisté** du fichier, **et** arrêt constaté de l'unité (§11.1) | une autorité levée en mémoire seule, ou une unité encore vivante |
| **autorité réellement ouverte pendant la fenêtre** | **trace côté broker** de la souscription au topic de commande (`EI-12`) | une souscription supposée depuis l'état interne de Boilerack — `W1` `A15`, `A16` l'interdisent |
| **unité non activée au démarrage** | état d'activation de `<unité-boilerack>`, relevé avant le temps 8 **et reconstaté après le démarrage manuel** (`G-a`) | une unité activée au boot, ou un `enable` glissé dans le démarrage manuel |
| **`PR-1` / `PR-2` établis** | **état des unités**, et zéro nouvelle connexion au démon en 25 s | *« Aucun raisonnement par absence de trace »* |
| **one-writer, au sens borné du §8.1** | inventaire des **unités inscriptibles**, `<unité-boilerack>` arrêtée, **fenêtre muette de 12 s sans aucune ouverture** au journal | une unité inscriptible omise de l'inventaire, ou une fenêtre prise pendant que Boilerack émet |
| **au plus deux écritures** | le **jeu de captures** — chaque invocation portant sa ligne réelle, `stdout` et `stderr` séparés, code retour et durée (`W4-A` §19, champs 2 à 5) — et les **échos consignés** : deux captures d'écriture, pas trois | une écriture non capturée, que le **décompte des ouvertures** du journal ferait apparaître **en excès** de ce que les captures expliquent |
| **état normal rétabli** | les **cinq étapes** du §11.2, `A` unité active · `B` cadence de connexions repartie · `C` télémétrie observée **depuis un consommateur aval** · étape 5 **cycle nominal du superviseur sans action corrective** | une restauration commandée, non vérifiée — ou **B pris pour C** — ou une campagne close avant l'étape 5 |

> **Le décompte du journal ne vaut pas attribution.** Il ne dit pas *qui* a
> ouvert une connexion — `U-3` reste ouverte — et il ne peut donc pas, à lui
> seul, prouver que `G.2` n'a écrit que deux fois. Il sert **par excès** : un
> nombre d'ouvertures supérieur à ce que les captures expliquent signale qu'un
> autre a émis, ce qui relève de **`FA-3`**, non d'un décompte d'écritures.

> **Ce que cette table ne prétend pas.** Elle rend les bornes **constatables**,
> non **infranchissables**. `W4-A` **§20** rappelle qu'aucun *one-writer*
> n'existe : le bornage est opposable **par preuve**, il n'est pas auto-appliqué.
> Et il ne couvre pas un participant agissant hors du démon — §8.2.

---

## 14. Préconditions de la campagne

| # | Précondition | Nature |
|---|---|---|
| **`P-1`** | Boilerack **déployé** et fonctionnel en lecture sur l'installation, son unité **arrêtée** jusqu'au temps 8 | action réversible |
| **`P-2`** | pont historique et superviseur dans leur **état nominal avant l'acte** | lecture |
| **`P-3`** | **rollback disponible** — arrêter et retirer `<unité-boilerack>` sans dépendre de Boilerack | action réversible, éprouvée |
| **`P-4`** | **procédure de remise en marche** du pont et du superviseur écrite et **éprouvée avant** le temps 2, **couvrant les cinq étapes** du §11.2 | préparation |
| **`P-5`** | **inventaire des unités inscriptibles** dressé et vérifié — condition de `EI-8` | préparation |
| **`P-6`** | **trace côté broker** disponible et lisible — condition de `EI-12` | préparation |
| **`P-7`** | **consommateur aval** disponible pour observer la télémétrie — condition du fait **C** (§11.2) | préparation |
| **`P-8`** | exploitant **physiquement présent**, plan de reprise physique connu | déclaration |
| **`P-9`** | **autorisation humaine explicite et distincte**, nommant `G.2`, et **disant si la restauration de la valeur est pré-décidée** (§10) | décision |
| **`P-10`** | le présent document **audité et intégré** | procédure |
| **`P-11`** | les treize preuves `EI` établies, dans l'ordre du §9 | §7 |

> **`P-1` n'est pas acquise à ce jour.** `ouverture` §2 constate l'observabilité
> Boilerack *« inexistante, non déployé »*. Le déploiement en lecture seule
> relève de `w4f` **§11.2**, distinct de `G.2` et non touché par lui.

---

## 15. Bornes de valeur, et cas d'inexécution

> **Clause.** Si `V_canon + 1 > 40`, la campagne `G.2` **MUST NOT** être exécutée.

Aucun repli n'est prévu, et **`V_canon − 1` n'est pas admis** : substituer un
autre sens de variation serait une décision non arbitrée. Le cas relève d'un
**arbitrage humain** distinct.

La campagne **MUST NOT** être exécutée si `V_brut` est hors de `[-13 ; 40]`, si
les deux formes du temps 6 ne concordent pas (`AB-2`), si `V_canon` n'est pas
dérivable sans perte (`AB-9`), ou si la garde de fraîcheur du temps 9 échoue
(`AB-8`).

---

## 16. Preuves de sortie

Sur le modèle de `W4-C` **§16.1** — *« Conditions réunies, et comment elles ont
été établies »* —, `G.2` est clos sur production de :

1. les **treize preuves `EI-1..EI-13`**, chacune avec sa **méthode**, sa sortie
   et son horodatage — *« une assertion d'arrêt ne vaut donc rien sans sa
   méthode »* (`W4-C` §9.1) ;
2. pour **`EI-8`**, la fenêtre de 12 s horodatée, l'état arrêté de
   `<unité-boilerack>` sur cette fenêtre, et l'extrait de journal montrant
   **aucune ouverture** — sans revendication d'attribution ;
3. les lectures horodatées : les **deux captures nues** du temps 6, texte **et**
   `-J`, avec `V_brut` et `V_canon` ; la garde de fraîcheur en `-J` (temps 9) ;
   la relecture de confirmation (temps 11) ; la relecture de restauration si elle
   a eu lieu ; et la **lecture nue de l'étape 1** du §11.2 ;
4. l'écriture, avec sa **ligne d'invocation réelle**, `stdout` et `stderr`
   **intégralement et séparément**, **code retour** et **durée mesurée** —
   `W4-A` §19, champs 2 à 5 ;
5. l'**`ACK` publié**, et sa confrontation à l'observation directe (`FA-10`) ;
6. les preuves d'**ouverture réelle** de l'autorité — contenu persisté, démarrage
   manuel de l'unité, **trace broker de la souscription** (§9, temps 8) — et
   d'**extinction** — contenu persisté, arrêt de l'unité, libération de la
   liaison (§11.1) ;
7. les preuves de **restauration**, **les cinq étapes nommées séparément**, dont
   les trois faits distincts de l'étape 3 — **A** unité active, **B** cadence de
   connexions au démon repartie, **C** télémétrie observée **depuis un
   consommateur aval** — et l'**étape 5**, cycle nominal du superviseur sans
   action corrective **et** alternance normale de son unité d'exécution ;
8. les preuves `PR-1` et `PR-2` **redoublées** — comment l'arrêt a été établi, et
   **comment la reprise l'a été** (`W4-C` §13) ;
9. l'état de **`G-a`** et **`G-b`** sur toute la fenêtre, `G-a` **reconstatée
   après le démarrage manuel** du temps 8 (§11.3) ;
10. le verdict : `G.2 CONFIRMÉ` ou `G.2 ABORT`, avec le critère `FA` ou `AB`
    déclencheur.

> **La campagne n'est close qu'après l'étape 5 du §11.2**, `W4-C` §13 l'exigeant
> en toutes lettres. Un rapport produit avant cette étape décrit une campagne
> **non close**.

> **Ce que `G.2` établira, et rien de plus** : que Boilerack a émis une écriture
> réelle, confirmée par relecture stricte, dispositif historique arrêté et
> *one-writer* établi **au sens borné du §8.1** — clients du démon, sur douze
> secondes. Il **n'établira pas** que la coexistence est qualifiée, ni que `C1`
> est satisfaite ou calculable, ni que Boilerack peut écrire **en coexistence**,
> ni de façon soutenue, ni que `H2`, `H6` **(b)** ou `U-3` seraient closes.

---

## 17. Préservations explicites

| Objet | État, inchangé |
|---|---|
| **`W4-F2`** | **`NON QUALIFIABLE`** hors `G.2` |
| **`W4-F3`** | **inadmissible** hors cette exception bornée |
| **Précondition 9 / `w4f` §11.2** | **`NON DONNÉE`** |
| **Pont historique** | **unique écrivain réel de production**, hors la fenêtre où il est **arrêté** |
| **Surface transactionnelle** | **sans autorité**, `false` — hors les temps 8 à 13 |
| **Autorité permanente** | **aucune n'est créée** |
| **Bascule de souveraineté** | **acte 4 de `w4f` §11.1 interdit** ; aucune bascule permanente |
| **Activation au démarrage** | `<unité-boilerack>` **jamais activée au boot** — `G-a` |
| **Rôle** | **un seul**, `heating_curve_shift` |
| **Campagne** | **une seule**, bornée, non reconductible |
| **Capacité d'écriture** | **éteinte et prouvée éteinte** avant toute restauration du pont |
| **État normal** | rétabli selon les **cinq étapes** de `W4-C` §13, campagne close après l'étape 5 |
| `C1`, `C2`, `C3` | **en vigueur, inchangés** ; `C1` **non applicable** à la fenêtre (§4.2), et non satisfaite |
| `U-1` à `U-7`, `H1`, `H2`, `H3`, `H6` | **ouvertes, inchangées** — `U-3` et `H6` **(b)** en particulier, §8 |
| `w4f` §11.3 | amendé **nommément et uniquement** par le §3.1 |
| Index du corpus | **non touché** |

---

## 18. Ce que ce document ne fait pas

Il n'exécute rien · il n'autorise aucune exécution · il ne déploie pas Boilerack ·
il ne touche ni la chaudière, ni le Pi, ni le pont, ni le superviseur, ni
`vcontrold` · il n'ouvre ni `W4-F3`, ni `W4-F4`, ni `T0` / `T1` / `T2`, ni
l'`Acte B` · il ne requalifie pas `W4-F2` · il n'amende ni `C1`, ni `C2`, ni
`C3` · il ne déclare aucun second rôle · **il ne demande aucune instrumentation
nouvelle et ne prépare pas la levée de `U-3`** · il ne modifie pas l'index du
corpus.

---

## 19. Réserves conservées

1. **`H2` et `H6` (b) demeurent OUVERTES** (§8.2). La preuve *one-writer* est
   **bornée aux clients du démon** ; un participant agissant sur l'IPC System V
   y échapperait. Seule `FA-3` en offre une **détection**, non une garantie.
2. **`U-3` demeure OUVERTE**, et `EI-8` est construite pour ne pas en dépendre.
   La contrepartie est que la preuve vaut sur une **fenêtre de douze secondes**,
   non sur la campagne : au-delà, il n'y a que `FA-3` et `AB-8`.
3. **`H6` (c) demeure OUVERTE** — `cloture` **§5** : *« sorties précoces autres
   que la non-résolution : échec d'écriture vers le client, expiration, fin de
   boucle avant acquisition »*. Les invocations de `G.2` peuvent elles-mêmes
   emprunter ces chemins ; c'est un motif d'abandon (`FA-5`, `AB-1`), non de
   poursuite.
4. **`U-2` et `U-7` demeurent ouvertes.** `G.2` ne les réduit pas ; le §4.2
   explique seulement pourquoi la question de `C1` est **sans objet sur la
   fenêtre**, non pourquoi elle serait résolue.
5. **`G.2` déplace la valeur d'un pas**, là où `W4-C` écrivait à l'identique
   (§6.3). Une part de la sûreté de `W4-C` n'est donc pas héritée, et l'étape 1
   du §11.2 doit être transposée (§11.2.1).
6. **La restriction du §10 est un choix de `G.2`**, plus strict que `W4-C` §12.1.
   Un auditeur peut légitimement juger qu'elle laisse l'installation sur une
   valeur déplacée après un `ABORT` postérieur à l'écriture. C'est assumé :
   `EI-1` borne la conséquence, et `w4f` §7.3 cas 4 la fonde.
7. **L'étape 5 du §11.2 allonge la fenêtre** d'au moins un cycle du superviseur,
   soit trois minutes (`w4f` §4.3), pendant lesquelles la campagne n'est pas
   close.
8. **`P-1` n'est pas acquise** — Boilerack n'est pas déployé.
9. **L'interruption de service est réelle** — bornée et réversible, non nulle.
10. **Le bornage est opposable, non auto-appliqué** (§13, dernier encadré).

---

## 20. Précédent invoqué

L'acte **`G.1`** — `w4f2-g1-constat.md` — a établi la forme : un acte **borné**,
**proposé par un document, non autorisé par lui**, puis autorisé par une
**décision humaine explicite et distincte**, exécuté sans élargissement, et
consigné par un document séparé.

`G.2` reprend cette forme, à une différence près, et elle est majeure : `G.1`
était en **lecture seule** et ne touchait à rien. `G.2` écrit, et **arrête
temporairement un dispositif de production**. C'est pourquoi il exige un
amendement là où `G.1` n'en exigeait aucun, et pourquoi ses preuves de sortie
comportent des preuves d'**ouverture**, d'**extinction** et de **restauration en
cinq étapes** que `G.1` n'avait pas à produire.
