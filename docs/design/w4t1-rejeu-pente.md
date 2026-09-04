# `W4-T1` — rejeu minimal, **la pente et rien d'autre**

> **Version 1.** Ouverture **et** bornage d'un rejeu **réduit à un seul rôle** :
> `heating_curve_slope` / `setNeigungM1`, le seul que `W4-T` a laissé
> **non caractérisé et engageable**.
>
> **Aucun terrain n'est conduit par ce document. Aucun code n'est demandé.
> Aucune constante de site n'y figure.**
>
> **L'autorisation humaine est `NON DONNÉE`** — §13. Elle **MUST NOT** être
> déduite du merge de la PR **#105**, ni de l'audit, ni de l'intégration du
> présent document.
>
> **L'acte réservé 4 — bascule de souveraineté — demeure interdit en tout état
> de cause**, et l'autorisation de `W4-T1` **MUST NOT** le porter.

---

## 0. Convention et désignation

| Nom court | Document |
|---|---|
| `W4-T` | `w4t-trois-ecritures.md` — le protocole des trois écritures, V1 puis V2 |
| `W4-TC` | `w4t-constat.md` — le constat des deux exécutions |
| `W4-S` | `w4s-campagne-minimale.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `G2-P` | `w4f-g2-ecriture-bornee.md` — le protocole |
| `w4f` | `w4f-write-sovereignty.md` |

**Désignation** : `W4-T1`, **sous-lot de `W4-T`**, dans l'usage établi par
`W4-P1`, `W4-F1` et `W4-E1`. **Vérifiée libre.** La série `G.n` **MUST NOT**
être prolongée — `debug` §G.4 nomme déjà *« ce qui touche à l'écrivain réel —
hors périmètre, absolument »*.

Unités désignées `<unité-boilerack>`, `<unité-pont>`, `<unité-démon>`,
`<unité-superviseur>`, `<timer-guard>`. **Aucune constante de site.**

> **`W4-T1` NE REMPLACE PAS `W4-T`.** Tout ce que `W4-T` établit et qui n'est
> pas **explicitement restreint ici** demeure **opposable en l'état** :
> périmètre, gardes, arrêts, référentiels `AB` et `FA`, restauration. **Le
> présent document RÉDUIT ; il n'allège pas.**

---

## 1. Objet

> **Objet unique : caractériser `heating_curve_slope` / `setNeigungM1`, en
> écrivant UNE seule fois `V_initiale + 1 cran`, en confirmant strictement, et en
> restaurant `V_initiale` si — et seulement si — la valeur a bougé.**

### 1.1 Ce que `W4-T1` établira, et rien de plus

La **réponse de transport** à l'écriture d'un flottant, la **forme de
l'acquittement**, la **confirmation par relecture**, et **si la tolérance de
confirmation déclarée suffit**.

> **Il n'établira pas** : que `dhw_setpoint` est caractérisée · que la
> coexistence est qualifiée · que `C1` est satisfaite · que `H2`, `H6 (b)`,
> `U-2` ou `U-3` seraient closes · **aucune capacité de production**. **Le régime
> permanent, le superviseur et la souveraineté demeurent HORS PÉRIMÈTRE.**

### 1.2 Pourquoi un seul rôle, et pourquoi les deux autres ne sont pas rejoués

| Rôle | État | Décision |
|---|---|---|
| `heating_setpoint` | **caractérisé** — `W4-TC` §4 : `15 → 16 → 15`, deux `applied`, preuves de transport, relectures concordantes | **NON REJOUÉ.** Le réémettre n'apprendrait **rien** |
| `heating_curve_slope` | **non caractérisé** — `W4-TC` §5 : aucune invocation n'a atteint le démon | **SEUL RÔLE DU LOT** |
| `dhw_setpoint` | **non caractérisé**, jamais engagé | **NON REJOUÉ ICI.** C'est le **seul rôle à effet physique ressenti** ; le joindre à une PREMIÈRE de forme mêlerait deux inconnues dans une même fenêtre |
| `heating_curve_shift` | caractérisé depuis `W4-C` | **NON REJOUÉ** |

> **Le groupement du `W4-T` §1.2 ne s'applique plus** : il valait pour **trois**
> rôles non caractérisés. **Il en reste deux, et ils ne sont pas de même
> nature** — l'un est une **forme neuve sans effet**, l'autre un **effet réel
> sous forme connue**. **Les séparer réduit la fenêtre et isole l'inconnue.**
>
> **`dhw_setpoint` demeure ouvert**, et relèvera d'un lot propre, **postérieur**.

---

## 2. Périmètre

> **`W4-T1` MUST NOT :**
>
> - écrire sur **un autre rôle** que `heating_curve_slope` — `heating_setpoint`,
>   `dhw_setpoint` et `heating_curve_shift` **compris** ;
> - émettre plus que la **cardinalité du §7** ;
> - **réémettre**, sous quelque forme et pour quelque motif que ce soit ;
> - **corriger** une valeur hors borne ou hors grille : **REJECT, jamais clamp** ;
> - **modifier** le profil, les bornes, `confirm_tolerance`, ou **aucun code** ;
> - **modifier** le pont, le superviseur, le démon, leurs unités, ou leur état
>   d'activation au démarrage ;
> - **modifier Arsenal**, en quoi que ce soit ;
> - **basculer la souveraineté** — acte réservé **4**, interdit en tout état de
>   cause.

> **Le pont historique demeure l'unique écrivain réel de production**, hors la
> fenêtre de `W4-T1`, pendant laquelle il est **arrêté** et où **personne d'autre
> que Boilerack n'écrit**.

---

## 3. La cible — **un cran, et un seul**

| | |
|---|---|
| `V_initiale` | **relue le jour J**, par deux captures nues — jamais reprise de `W4-TC` |
| Cible | **`V_initiale + 0,1`** — un cran de la grille `[0,2 ; 3,5]` |
| Effet physique attendu | **aucun** — circuit au repos, hors saison de chauffe, exigé par `EI-1` |
| Si la cible dépasse `3,5` | **le rôle n'est pas écrit, et la campagne se clôt** — aucune valeur de repli n'est improvisée, et le cran n'est **jamais** retranché pour « faire quand même » |

> **La valeur relevée à la V2 était `1.800000`, cible `1.9`.** Elle est citée
> **à titre historique**. **Elle n'est pas la cible du rejeu** : `V_initiale`
> est **relue**, et la cible **recalculée**.

### 3.1 La cible est écrite **comme un cran**, non calculée en binaire

> **Clause NEUVE, et elle est décisive.** La cible **MUST** être portée par la
> commande sous la forme du **littéral décimal à une décimale** du cran visé.
> Elle **MUST NOT** être obtenue en ajoutant `0,1` à la valeur relue **en
> arithmétique flottante binaire**.

**Motif, vérifié sur le code intégré et non supposé :**

| Chemin | Ce qui part sur le fil |
|---|---|
| littéral `1.9` | **`1.9`** |
| `1.8 + 0.1` en binaire | **`1.9000000000000001`** |

`0,1` n'est pas représentable en binaire ; la somme vaut `1.9000000000000001`, et
la forme décimale intégrée par `I-8` rend **la représentation la plus courte qui
reconstruit exactement ce flottant** — donc **dix-sept chiffres significatifs**.

> **Ni la borne ni la grille ne l'arrêteraient** : le contrôle de grille est
> tolérant, et la valeur passerait. **Elle partirait telle quelle.**
>
> **Sur une PREMIÈRE de forme, ce serait exactement l'inverse du but** :
> caractériser une forme **choisie**, et non une forme **subie**. La clause
> ferme ce chemin **avant** la fenêtre, et non après.

---

## 4. La PREMIÈRE — qualifiée, et sans équivoque

> ### **La publication du §8 acte 5 est une PREMIÈRE au sens de `W4-C`.**

**Ce qui est neuf, et qui ne l'a jamais été :**

| | |
|---|---|
| **Le rôle** | `setNeigungM1` n'a **jamais** été écrite par Boilerack. Aucune invocation ne l'a jamais atteint |
| **La forme** | **aucune valeur non entière n'a jamais quitté la machine** par la chaîne d'écriture Boilerack |
| **La normalisation** | `I-8` est levée **sur pièces et sur code** — définition du démon, `atof`, précédent de production, coïncidence exacte de la troncature et de l'arrondi sur les 34 crans. **Aucune écriture réelle ne l'a confirmée en vol** |

> **Lever `I-8` n'est pas caractériser `setNeigungM1`.** La levée a établi ce que
> le code **rend** ; elle n'a rien établi de ce que la chaudière **reçoit**.
> **L'écart entre les deux est précisément l'objet de ce lot.**

**Conséquence opposable** : l'autorisation **MUST** nommer cette publication
comme **PREMIÈRE**, et les actes réservés du `w4f` §11.1 s'appliquent **sans
allègement**.

---

## 5. La confirmation — **stricte**

> **« Strictement » signifie : la règle déclarée, appliquée telle quelle, sans
> relaxation, sans clamp, sans réémission, et sans lecture favorable d'un
> résultat ambigu.**

**La règle déclarée est celle du profil intégré, et le présent lot ne la modifie
pas :**

```
confirmation  <=>  abs(relu - cible) <= confirm_tolerance,  confirm_tolerance = 1e-9
```

> **`confirm_tolerance` n'est ni révisée, ni discutée, ni contournée ici.** La
> réviser serait décider avant de mesurer — et c'est la mesure que ce lot
> produit.

**Les trois issues du `W4-T` §4 sont reprises intégralement**, et **elles ne se
confondent pas** :

| Issue | Constat | Ce qu'elle signifie | Conduite |
|---|---|---|---|
| **`applied`** | `abs(relu − cible) <= 1e-9` | la tolérance déclarée **suffit** | **nominal.** Restauration **DUE** |
| **`TOLÉRANCE INSUFFISANTE`** | `ACK` `timeout`, **et** relecture nue **métier égale** — `abs(relu − cible) < 0,05`, soit un demi-cran | **la chaudière a appliqué la valeur ; c'est la tolérance qui est trop serrée.** Ni défaut de la chaudière, ni second écrivain | restauration **DUE**, puis **arrêt** : la caractérisation a produit son résultat |
| **`VALEUR NON APPLIQUÉE`** | relecture nue **métier différente** — autre cran, ou `V_initiale` | l'écriture **n'a pas pris**. **Défaut réel** | restauration **NON DUE**, **arrêt** |

> **Le départage se fait sur une lecture nue, hors chemin Boilerack, et sur elle
> seule.** Il n'existe **aucune valeur licite entre deux crans** : le seuil
> métier de `0,05` est un **demi-cran**, et il ne recouvre rien d'autre.

---

## 6. La restauration — due exactement quand la valeur a bougé

| Situation | Restauration |
|---|---|
| `applied` | **DUE** |
| `timeout`, valeur **métier égale** à la cible | **DUE** |
| `timeout`, **valeur inchangée** | **NON DUE** |
| `rejected` | **NON DUE** — aucune écriture n'a eu lieu |

> **Restaurer une valeur qui n'a pas bougé serait écrire sans avoir
> caractérisé** — `w4f` §7.3, cas 1. **C'est interdit.**

**La restauration est PRÉ-DÉCIDÉE par l'autorisation, armée avant l'écriture, et
elle ramène à `V_initiale` — jamais ailleurs.**

---

## 7. Cardinalité — **deux rangs au plus**

| | Écriture de cible | Restauration | Ailleurs |
|---|---|---|---|
| `heating_curve_slope` | **1** | **au plus 1** | **0** |

> **DEUX écritures au maximum, et pas une de plus.** Le puits de preuve doit
> porter **au plus deux rangs**, `01` et `02`. **Un troisième rang est une
> violation, quelle qu'en soit la cause.**
>
> **Zéro ou un rang est NORMAL** : zéro si la cible dépasse la borne ou si
> l'écriture n'atteint pas le démon ; un si la restauration n'est pas due. **Le
> décompte attendu se déduit de l'issue, jamais l'inverse.**
>
> Les **lectures** — état initial, garde de fraîcheur, relecture de
> confirmation, relecture nue de départage, relecture après restauration —
> **n'entrent pas** dans ce décompte.

---

## 8. Séquence — neuf actes, et aucun autre

| # | Acte | Preuve |
|---|---|---|
| **1** | **lire l'état initial** par **deux captures nues** — forme texte et forme `-J`, hors chemin Boilerack. Constituer `V_brut`, en dériver `V_initiale` **sans perte** | concordance brute **et** sémantique |
| **2** | **calculer la cible** `V_initiale + 1 cran`, **écrite comme un cran** — §3.1. **Si elle dépasse `3,5` : le rôle n'est pas écrit**, et la campagne se clôt | cible consignée, **avec son littéral** |
| **3** | **armer la restauration** — commande écrite d'avance, **non exécutée** | fichier d'armement |
| **4** | **garde de fraîcheur** — relecture, concordance avec `V_brut` exigée | sinon **arrêt** |
| **5** | **ÉCRIRE la cible** — **une seule publication**. **C'est la PREMIÈRE du §4** | `ACK` + preuve de transport |
| **6** | **attendre l'`ACK` terminal** — `applied`, `rejected` ou `timeout` | capture d'`ACK` |
| **7** | **relire nûment**, hors chemin Boilerack, et **départager** par le §5 | écart `abs(relu − cible)` **en clair** |
| **8** | **RESTAURER** vers `V_initiale` **si et seulement si** le §6 la rend due | `ACK` + preuve de transport |
| **9** | **relire** — la valeur doit être revenue à `V_brut` | relecture consignée |

### 8.1 Acquittements — la séquence attendue

`accepted` puis **l'un des trois terminaux** : `applied`, `rejected`, `timeout`.

| Terminal | Conduite |
|---|---|
| **`applied`** | **nominal.** Restauration due |
| **`rejected`** | **aucune écriture n'a eu lieu.** Restauration **NON due**. **Arrêt** : un rejet sur une cible calculée par le protocole est un **défaut du protocole**, et il doit être compris avant d'aller plus loin |
| **`timeout`** | **état indéterminé.** Établir par **lecture nue** ce que porte réellement la chaudière, puis §5 |

> **`accepted` n'est jamais un succès.** Seul `applied` **corrélé au même
> `request_id`** vaut confirmation.

---

## 9. Arrêt de campagne

**Le référentiel du `W4-T` §7 s'applique intégralement**, sans retrait, et **les
référentiels `AB` et `FA` de `G2-P` §12 avec lui**.

> **Il n'y a qu'un rôle : tout arrêt est donc la fin de la campagne.** La
> restauration due, si elle l'est, **s'exécute avant l'arrêt** — toujours.

---

## 10. État initial sûr, préconditions, restauration

**Repris de `W4-S` et de `W4-T` sans allègement** :

- les **treize preuves `EI-1` à `EI-13`**, dans l'ordre ;
- **`PR-1`** superviseur neutralisé, **`PR-2`** pont arrêté, **redoublées** ;
- **`P-UFS`** — `UnitFileState` des **quatre** unités en **pièce dédiée**,
  déposée **avant le temps 1**, antériorité prouvée par la pièce elle-même ;
- **`G-a`** et **`G-b`**, cumulées ;
- **`P-A1`** dépôt en écriture unique, **`P-SPT`** réarmement du puits ;
- **`P-DEP`**, **étendue** — §10.1 ;
- **`P-RND`**, **neuve** — §10.2 ;
- la **restauration complète** — §10.5.

> **Une seule différence de cardinalité avec `W4-T`** : le puits portera **au
> plus deux rangs** au lieu de six.

### 10.1 `P-DEP` — **étendue à la chaîne de rendu**

> **La `P-DEP` de `W4-T` n'aurait PAS arrêté la V2.** Sa réserve 7 le disait
> déjà : *« `P-DEP` ne couvre que le profil et la surface de lecture »*. Or le
> défaut qui a fait échouer la V2 était **dans l'adaptateur d'écriture**, que
> `P-DEP` **ne regardait pas**.

**Clause.** Avant le temps 1, la pièce dédiée `P-DEP` **MUST** établir, **par
lecture du service installé** :

| | |
|---|---|
| **1** | les **QUATRE rôles** du profil de production exposés par le service **installé**, avec pour chacun sa commande de lecture, sa commande d'écriture, ses bornes et son pas |
| **2** | **explicitement, `heating_curve_slope`**, son type **flottant**, ses bornes et son pas |
| **3** | l'**identité du code déployé** : empreintes des fichiers **installés** confrontées aux mêmes fichiers **au dépôt intégré**, et leur **concordance** |
| **4** | **NEUF — la chaîne de rendu en fait partie** : les fichiers qui décident de la **forme émise** sont **inclus** dans le point 3, au même titre que le profil et la surface de lecture |

> **Le point 4 n'est pas une commodité : c'est la leçon de la V2.** Une `P-DEP`
> qui prouve le profil mais ignore l'adaptateur prouve **ce que le service
> promet**, non **ce qu'il sait faire**.

**La précondition est satisfaite si et seulement si les quatre points le sont.**
À défaut, **la campagne MUST NOT être engagée**, et **aucun acte du §8 ne MAY
être entrepris** — pas même l'acte 1.

**Aucune reconstruction n'est admise.** Une pièce produite **après** l'acte 1, ou
dérivée du dépôt plutôt que de l'installation, **MUST NOT** être présentée comme
satisfaisant la précondition.

### 10.2 `P-RND` — la forme, prouvée **hors ligne**, avant la fenêtre

> **Précondition NEUVE, et son motif est le coût de la V2** : la forme émise a
> été apprise **au prix d'une fenêtre**, alors qu'elle était connaissable
> **sans terrain**.

**Clause.** Avant le temps 1, une **pièce dédiée** `P-RND` **MUST** porter le
**rendu effectif de la cible par le code INSTALLÉ** :

| | |
|---|---|
| **1** | la cible du §3, telle qu'elle sera publiée |
| **2** | les **octets exacts** que la chaîne d'écriture **installée** produirait pour cette cible |
| **3** | le constat que ces octets sont la **forme décimale positionnelle à point du cran visé**, **sans exposant, sans chiffre parasite** |

> **`P-RND` est l'analogue exact du point 1 de `P-DEP`, appliqué à la forme.**
> L'empreinte prouve que **le fichier est le bon fichier** ; `P-RND` prouve que
> **la forme qui partira est la forme voulue**. Ce sont **deux choses
> différentes**, et la V1 comme la V2 ont échoué sur cette différence.

> **`P-RND` est PURE.** Elle **n'émet rien**, **ne publie rien**, **ne contacte
> ni le démon ni le courtier**, **ne lance aucun processus d'écriture** et
> **n'atteint jamais la chaudière**. Elle appelle une fonction de rendu et
> observe des octets. **Elle n'est en aucun cas une écriture**, et elle
> **n'entre pas** dans la cardinalité du §7.

**Si `P-RND` ne rend pas la forme attendue, la campagne MUST NOT être engagée** —
et le défaut est alors connu **au prix de rien**.

### 10.3 Le déploiement est un acte **antérieur** et **hors périmètre**

**Le service installé sur la machine est antérieur à la PR #105** : il **ne
porte pas** la levée de `I-8`. **Il devra donc être redéployé avant la
campagne.**

> **`W4-T1` n'autorise ce déploiement ni ne le décrit.** Mettre le service à
> jour est un acte **propre**, **antérieur** à la campagne, relevant d'une
> décision distincte. **`P-DEP` et `P-RND` CONSTATENT ; elles n'accomplissent
> pas.**

### 10.4 Conséquence sur Arsenal — déclarée avant, non découverte après

**Arsenal pilote ce rôle en production.** Pendant toute la fenêtre, le pont
historique est **arrêté** : les commandes qu'Arsenal publie sur sa propre surface
**ne seront ni reçues ni acquittées**.

> **Conséquence attendue et normale** : les capteurs de transaction d'Arsenal
> conclueront en **délai dépassé**, et ses mécanismes de reprise pourront
> s'activer. **Rien ne l'empêche, et le présent lot n'y touche pas** — modifier
> Arsenal est **hors périmètre**.
>
> **L'exploitant en est informé avant d'autoriser.** **La fenêtre doit être
> COURTE** — et elle l'est plus qu'en `W4-T`, puisqu'un seul rôle est engagé.

### 10.5 Restauration — de la valeur, **et de l'installation**

**Trois restaurations distinctes, et aucune ne dispense des autres :**

| | |
|---|---|
| **1. la valeur** | vers `V_initiale`, **si et seulement si** le §6 la rend due |
| **2. l'installation** | les **cinq étapes** de `W4-S`, avec les **trois faits `A`, `B`, `C` établis séparément** et le **cycle nominal** du superviseur |
| **3. les fichiers persistés** | **retour byte à byte** à leur état d'origine — configuration, environnement, secret ancré, **puits désarmé** — **prouvé par empreintes avant et après** |

> **La V2 a établi les trois.** Le rejeu **MUST** les établir de même : une
> campagne qui laisse la machine dans un état autre que celui qu'elle a trouvé
> **n'est pas achevée**, quel qu'ait été son résultat.

---

## 11. Preuves exigées en sortie

| # | Sortie |
|---|---|
| **0** | **`P-DEP` étendue** — quatre rôles exposés par le service installé, `heating_curve_slope` nommément, **concordance d'empreinte incluant la chaîne de rendu**. Horodatage **antérieur au temps 1** |
| **1** | **`P-RND`** — cible, **octets rendus par le code installé**, constat de forme. Horodatage **antérieur au temps 1** |
| **2** | **`P-UFS`** — pièce dédiée, quatre `UnitFileState`, horodatage antérieur au temps 1 |
| **3** | les **treize `EI`**, dans l'ordre, avec `PR-1` et `PR-2` **redoublées** |
| **4** | `V_brut`, `V_initiale`, la cible, **son littéral**, et le calcul qui la produit |
| **5** | la publication émise, son `request_id`, et l'**`ACK` terminal** |
| **6** | la **preuve de transport** du puits — ligne d'invocation réelle, sorties standard et d'erreur **intégralement et séparément**, code retour, **durée mesurée** |
| **7** | la **relecture nue** de départage, l'écart `abs(relu − cible)` **en clair**, et **laquelle des trois issues du §5** est retenue |
| **8** | la restauration — **son caractère dû ou non dû, motivé** — puis la relecture après restauration |
| **9** | la **cardinalité effective**, rang par rang, et le décompte du puits |
| **10** | les **cinq étapes** de restauration, faits `A`/`B`/`C` séparés, cycle nominal |
| **11** | les **fichiers persistés**, empreintes **avant et après**, et leur égalité |
| **12** | **`G-a`** avant et après démarrage manuel · **`G-b`** hors la fenêtre d'autorité |
| **13** | tout critère **`AB`** ou **`FA`** atteint, **prononcé ou non** |
| **14** | ce qui **demeure non établi** |

**Toutes les pièces sont hachées et portées à un manifeste**, et le rapport est
**gelé hors dépôt** — **le dépôt n'en portera que les empreintes**.

---

## 12. Critère de succès

> **`W4-T1 CONFIRMÉ`** — et il n'y a pas de demi-succès.

**Exige, cumulativement :**

1. **`P-DEP` étendue**, **`P-RND`** et **`P-UFS`** prouvées par pièces dédiées et
   antérieures ;
2. les **treize `EI`** établies ;
3. le rôle écrit **une fois**, **`applied`**, et **confirmé par relecture** ;
4. la restauration **exécutée**, ramenant la valeur à `V_brut` ;
5. **cardinalité exactement deux**, et le puits portant deux rangs ;
6. les **cinq étapes** de restauration achevées, cycle nominal compris, et les
   **fichiers persistés revenus byte à byte** ;
7. **aucun `AB`, aucun `FA`**.

**Tout autre cas est `W4-T1 ABANDONNÉ`**, avec le motif.

> **Un abandon n'est pas un échec du lot.** Trois issues sont **utiles** :
> `W4-T1 CONFIRMÉ` · `TOLÉRANCE INSUFFISANTE`, qui **produit précisément la
> mesure que ce rôle appelait** · `VALEUR NON APPLIQUÉE`, qui révèle un défaut
> réel **avant** qu'il n'atteigne la production.
>
> **Ce que le lot n'a pas le droit de faire, c'est de réessayer pour obtenir une
> issue plus flatteuse.**

---

## 13. L'autorisation humaine

> ### `NON DONNÉE`

**L'autorisation, si elle est donnée, MUST :**

| # | |
|---|---|
| **1** | être précédée d'un **AUDIT INDÉPENDANT** du présent document, et de son **INTÉGRATION** |
| **2** | **nommer `W4-T1` ET sa version**, être explicite, distincte, et postérieure aux deux |
| **3** | **nommer `heating_curve_slope`, et lui seul** |
| **4** | **qualifier la publication de PREMIÈRE** au sens de `W4-C` — §4 |
| **5** | **dire que la restauration est PRÉ-DÉCIDÉE**, et **conditionnelle** au §6 |
| **6** | porter les **actes réservés 1, 2 et 3** du `w4f` §11.1 |
| **7** | porter la **levée ponctuelle du `w4f` §11.2**, bornée aux gestes nécessaires |
| **8** | porter l'**extension nominale du puits**, bornée à cette campagne |
| **9** | valoir pour **une exécution, et une seule** |

**Elle MUST NOT :**

- être **déduite** de l'audit, de l'intégration, du merge du présent document,
  **ni du merge de la PR #105** ;
- se réclamer de l'autorisation d'un autre lot — **`W4-T` V1 et V2, `G.2`,
  `G.3`, `W4-S` et le Lot 1 sont étrangers à celle-ci, et les deux autorisations
  de `W4-T` sont CONSOMMÉES** ;
- porter l'**acte réservé 4** — **interdit en tout état de cause** ;
- valoir autorisation de `dhw_setpoint`, du **régime permanent**, du
  **re-pointage du superviseur**, ni d'aucune **modification d'Arsenal** ;
- valoir autorisation de `W4-F3`, `W4-F4`, `W4-F5`, `T0`, `T1` ou `T2`.

---

## 14. Ce qu'un auditeur doit pouvoir trancher AVANT le terrain

| | Question | Où elle se tranche |
|---|---|---|
| **0** | le **service qui va tourner** porte-t-il le profil audité **et la chaîne de rendu auditée**, prouvés depuis l'installation ? | §10.1, `P-DEP` étendue |
| **1** | la **forme qui partira** est-elle prouvée **avant** la fenêtre, et sans rien émettre ? | §10.2, `P-RND` |
| **2** | la **cible** est-elle un **cran**, écrite comme un cran, et non une somme binaire ? | §3.1 |
| **3** | la **PREMIÈRE** est-elle qualifiée comme telle, sans que la levée de `I-8` en tienne lieu ? | §4 |
| **4** | la **confirmation** est-elle celle du code, appliquée sans relaxation ? | §5 |
| **5** | la **cardinalité** est-elle close et vérifiable sur un artefact ? | §7, deux rangs |
| **6** | la **restauration** est-elle due **exactement** quand la valeur a bougé ? | §6 |
| **7** | l'**installation et les fichiers persistés** reviennent-ils prouvablement à l'état trouvé ? | §10.5 |
| **8** | l'effet sur **Arsenal** est-il déclaré avant, et non découvert après ? | §10.4 |
| **9** | l'exclusion de `dhw_setpoint` est-elle **motivée**, et non commode ? | §1.2 |
| **10** | l'autorisation **exclut-elle** l'acte réservé 4 et le régime permanent ? | §13 |

---

## 15. Ce que ce document ne fait pas

Il **n'exécute rien** · **n'autorise rien** · ne conduit aucun terrain · ne
demande **aucun code** · **ne modifie ni le profil, ni les bornes, ni
`confirm_tolerance`** · **ne modifie ni le pont, ni le superviseur, ni leurs
unités, ni leur activation au démarrage** · **ne modifie pas Arsenal** · **ne
touche pas à l'acte réservé 4** · n'ouvre pas le régime permanent · ne rapproche
pas la bascule · **n'autorise aucun déploiement** · ne révise **aucune
tolérance** · **ne caractérise `dhw_setpoint` en rien**.

**Il borne un rejeu d'un seul rôle, le referme, et s'arrête là.**

---

## 16. Réserves conservées

1. **`setNeigungM1` n'est pas caractérisée**, et ne le sera pas par ce document :
   **seule une exécution autorisée pourra l'établir**.
2. **La forme décimale n'a jamais été émise.** `I-8` est levée **sur pièces**, et
   **la prochaine émission demeure une PREMIÈRE**.
3. **La tolérance de la pente peut se révéler insuffisante.** C'est une issue
   **prévue**, non un incident — §5. **Aucune valeur de remplacement n'est
   décidée ici.**
4. **`dhw_setpoint` demeure non caractérisée**, et son lot reste à ouvrir.
5. **`P-DEP`, même étendue, ne couvre pas tout le code déployé** ni les
   dépendances du service. **Elle ferme le trou du profil et celui du rendu, et
   pas davantage** — l'étendre serait une autre décision.
6. **`P-RND` prouve le rendu, non la réception.** Ce que la chaudière fait de la
   forme demeure **exactement l'inconnue** que la campagne doit lever.
7. **`C1`, la coexistence, `U-2`, `U-3`, `H2`, `H6 (b)` demeurent ouvertes**, et
   la campagne n'en réduit aucune.
8. **L'unité de `getBrennerStatus` demeure non établie** — `C7` §4.3. Sans
   rapport avec la présente campagne, mais toujours ouverte.
9. **Arsenal subira une fenêtre sans acquittement**, et ses mécanismes de reprise
   pourront s'activer — §10.4. **Aucun contournement n'est proposé** : en
   proposer un supposerait de modifier Arsenal.
10. **Le régime permanent, le re-pointage du superviseur et la bascule demeurent
    entiers**, et relèvent des sous-objectifs 2 et 3 du Lot 2.
11. **Les deux autorisations de `W4-T` sont consommées.** Le présent lot **ne
    s'en réclame pas**, et **aucune autorisation ne peut être déduite** de son
    audit, de son intégration ou de son merge.
