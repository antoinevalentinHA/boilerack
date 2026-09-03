# `W4-T` — caractérisation groupée des trois écritures non caractérisées

> **Version 1.** Ouverture **et** bornage. Le document définit **une seule
> campagne** couvrant les **trois rôles** que Boilerack déclare depuis le Lot 1
> mais n'a **jamais émis**, la referme, et **ne l'autorise pas**.
>
> **Aucun terrain n'est conduit par ce document. Aucun code n'est demandé.
> Aucune constante de site n'y figure.**
>
> **L'autorisation humaine est `NON DONNÉE`** — §11.
>
> **L'acte réservé 4 — bascule de souveraineté — demeure interdit**, et
> l'autorisation de `W4-T` **MUST NOT** le porter.

---

## 0. Convention

| Nom court | Document |
|---|---|
| `w4f` | `w4f-write-sovereignty.md` |
| `G2-P` | `w4f-g2-ecriture-bornee.md` — le protocole |
| `G2-C` | `w4f-g2-constat.md` |
| `W4-S` | `w4s-campagne-minimale.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `C7` | `c7-mqtt-read-contract.md` |

Unités désignées `<unité-boilerack>`, `<unité-pont>`, `<unité-démon>`,
`<unité-superviseur>`, `<timer-guard>`. **Aucune constante de site.**

**Désignation** : `W4-T` — *trois écritures*. Vérifiée libre. La série `G.n`
**MUST NOT** être prolongée : `debug` §G.4 nomme déjà *« ce qui touche à
l'écrivain réel — hors périmètre, absolument »*.

---

## 1. Objet

> **Objet unique : caractériser, en UNE campagne, les trois écritures que le
> Lot 1 a déclarées sans jamais les émettre.**

| Rôle | Commande | Type | Bornes | Pas |
|---|---|---|---|---|
| `heating_setpoint` | `setTempRaumNorSollM1` | entier | `[5 ; 30]` | `1` |
| `heating_curve_slope` | `setNeigungM1` | **flottant** | `[0.2 ; 3.5]` | `0.1` |
| `dhw_setpoint` | `setTempWWsoll` | entier | `[10 ; 60]` | `1` |

**`heating_curve_shift` n'en fait PAS partie** : il est caractérisé depuis
`W4-C`, confirmé par `G.2` et `W4-S`. **Le réémettre n'apprendrait rien.**

### 1.1 Ce que `W4-T` établira, et rien de plus

Pour chacun des trois rôles : **la réponse de transport à l'écriture**, la
**forme de l'acquittement**, la **confirmation par relecture**, et — pour la
pente seule — **si la tolérance de confirmation déclarée est suffisante**.

> **Il n'établira pas** : que la coexistence est qualifiée · que `C1` est
> satisfaite · que Boilerack peut écrire en coexistence ou de façon soutenue ·
> que `H2`, `H6 (b)` ou `U-3` seraient closes · **aucune capacité de
> production**. **Le régime permanent, le superviseur et la souveraineté sont
> HORS PÉRIMÈTRE**, et relèvent des sous-objectifs 2 et 3 du Lot 2.

### 1.2 Pourquoi une seule campagne, et non trois

Les trois rôles partagent **la même chaîne** — même profil, même surface
transactionnelle, même adaptateur, même transport. Trois campagnes séparées
répéteraient **trois fois** les mêmes treize preuves d'état initial, la même
neutralisation et la même restauration, pour **trois fois le risque
d'exposition**. Une campagne les caractérise **dans une seule fenêtre
neutralisée**.

---

## 2. Périmètre

> **`W4-T` MUST NOT :**
>
> - écrire sur un **autre rôle** que les trois ci-dessus — `heating_curve_shift`
>   compris ;
> - émettre plus que la **cardinalité du §5** ;
> - **modifier** le pont, le superviseur, le démon, leurs unités, ou leur état
>   d'activation au démarrage ;
> - **modifier Arsenal**, en quoi que ce soit ;
> - **basculer la souveraineté** — acte réservé **4**, interdit en tout état de
>   cause ;
> - **réessayer** une écriture, sous quelque forme que ce soit ;
> - **corriger** une valeur hors borne ou hors grille : **REJECT, jamais clamp**.

> **Le pont historique demeure l'unique écrivain réel de production**, hors la
> fenêtre de `W4-T`, pendant laquelle il est **arrêté** et où **personne d'autre
> que Boilerack n'écrit**.

---

## 3. Les trois rôles — cible, restauration, motif

> **Règle commune.** La cible est **`V_initiale + 1 pas`**, et **rien d'autre** :
> le plus petit écart que la grille autorise. La restauration ramène à
> **`V_initiale`**, et elle est **PRÉ-DÉCIDÉE** par l'autorisation.
>
> **Si `V_initiale + 1 pas` dépasse la borne haute, la campagne se clôt sans
> écrire ce rôle** — aucune valeur de repli n'est improvisée, et le pas n'est
> jamais retranché pour « faire quand même ».

### 3.1 Ordre d'exécution — et son motif de sûreté

| # | Rôle | Effet physique attendu | Motif de la place |
|---|---|---|---|
| **1** | `heating_setpoint` | **aucun** — hors saison de chauffe | **entier**, forme déjà caractérisée sur un autre rôle. On éprouve la chaîne connue d'abord |
| **2** | `heating_curve_slope` | **aucun** — hors saison de chauffe | **flottant**, forme NEUVE. On l'éprouve quand la chaîne entière vient d'être vue fonctionner |
| **3** | `dhw_setpoint` | **le seul réel** — consigne d'eau chaude | **en dernier**, pour qu'un défaut rencontré aux rangs 1 ou 2 **arrête la campagne avant** de toucher la seule grandeur qui produise un effet ressenti |

### 3.2 Bornes utiles et effet

| Rôle | `V_initiale` *(à relire le jour J)* | Cible | Effet |
|---|---|---|---|
| `heating_setpoint` | consigne de confort du circuit M1 | `+1 °C` | nul hors saison |
| `heating_curve_slope` | pente de courbe | `+0,1` | nul hors saison |
| `dhw_setpoint` | consigne ECS | `+1 °C` | **eau chaude 1 °C plus haut, quelques minutes** |

> **`EI-1` exige le circuit au repos, hors saison de chauffe.** Les deux
> premiers rôles n'ont alors **aucun effet observable** : c'est délibéré, et
> c'est ce qui rend leur caractérisation peu coûteuse.
>
> **`dhw_setpoint` est le seul dont l'effet est réel.** `+1 °C` sur quelques
> minutes, restauré aussitôt, est le plus petit écart que la grille permette.
> **Il n'existe pas de variation ECS plus petite.**

---

## 4. La pente — le cas neuf, et il faut le traiter à part

> **C'est le premier rôle FLOTTANT que Boilerack écrira.** Sa confirmation ne
> passe pas par une égalité exacte mais par
> `abs(relu − cible) <= confirm_tolerance`, avec `confirm_tolerance = 1e-9`.

**La tolérance déclarée est une tolérance de REPRÉSENTATION, pas de valeur.**
`0.1` n'est pas représentable exactement en binaire ; exiger l'égalité stricte
rejetterait des relectures pourtant justes. `1e-9` est **cent millions de fois
plus petit** qu'un cran de pente.

> **Clause — ne JAMAIS confondre égalité binaire et égalité métier.**
>
> Trois issues distinctes, et elles ne se confondent pas :
>
> | Issue | Constat | Ce qu'elle signifie |
> |---|---|---|
> | **`applied`** | `abs(relu − cible) <= 1e-9` | la tolérance déclarée **suffit**. Rien à corriger |
> | **`TOLÉRANCE INSUFFISANTE`** | l'`ACK` conclut `timeout`, **et** la relecture nue montre une valeur **métier égale** — même cran de `0.1`, écart `< 0.05` | **la chaudière a appliqué la valeur ; c'est `confirm_tolerance` qui est trop serrée.** Ce n'est **PAS** un défaut de la chaudière, **PAS** un second écrivain, **PAS** une raison d'abandonner la campagne |
> | **`VALEUR NON APPLIQUÉE`** | la relecture nue montre une valeur **métier différente** — autre cran, ou `V_initiale` | l'écriture n'a **pas pris**. **Défaut réel**, et la campagne s'arrête |
>
> **Le départage se fait sur une lecture nue, hors chemin Boilerack**, et sur
> elle seule. Le critère métier est : **`abs(relu − cible) < 0.05`**, soit un
> demi-cran — il n'existe aucune valeur licite entre deux crans.

> **Conduite sur `TOLÉRANCE INSUFFISANTE`.** La valeur **est** appliquée : la
> **restauration est donc DUE**, et elle s'exécute. Puis **la campagne
> s'arrête** — non par danger, mais parce que la caractérisation a produit son
> résultat : **`confirm_tolerance` doit être révisée avant tout usage
> ultérieur de ce rôle**, et poursuivre sur `dhw_setpoint` n'apprendrait rien de
> plus. **Le rang 3 n'est pas exécuté.**
>
> **Aucune valeur de tolérance n'est décidée ici.** La révision relèvera d'un lot
> distinct, instruit par la mesure que cette campagne aura produite.

---

## 5. Cardinalité — exacte, et vérifiable sur le puits

| Rôle | Écriture de cible | Restauration | Ailleurs |
|---|---|---|---|
| `heating_setpoint` | **1** | **1** | **0** |
| `heating_curve_slope` | **1** | **1** | **0** |
| `dhw_setpoint` | **1** | **1** | **0** |

> **SIX écritures au maximum, et pas une de plus.** Le puits de preuve doit
> porter **au plus six rangs**, dans l'ordre `01` à `06`. Un septième rang est
> une violation, quelle qu'en soit la cause.
>
> **Moins de six est NORMAL** : un arrêt au rang 1 ou 2 en laisse deux ou
> quatre. Le décompte attendu se déduit du rang atteint, jamais l'inverse.
>
> Les **lectures** — état initial, garde de fraîcheur, relecture de
> confirmation, relecture nue de départage — **n'entrent pas** dans ce décompte.

---

## 6. Séquence par rôle — identique pour les trois

**Pour chaque rôle, dans l'ordre du §3.1 :**

| # | Acte | Preuve |
|---|---|---|
| **1** | **lire l'état initial** par **deux captures nues** — forme texte et forme `-J`, hors chemin Boilerack. Constituer `V_brut`, en dériver `V_initiale` **sans perte** | concordance brute **et** sémantique |
| **2** | **calculer la cible** `V_initiale + 1 pas`. **Si elle dépasse la borne haute : le rôle n'est pas écrit**, et la campagne passe au suivant | cible consignée |
| **3** | **armer la restauration** — commande écrite d'avance, **non exécutée** | fichier d'armement |
| **4** | **garde de fraîcheur** — relecture, concordance avec `V_brut` exigée | sinon **arrêt** |
| **5** | **ÉCRIRE la cible** — **une seule publication** | `ACK` + preuve transport |
| **6** | **attendre l'`ACK` terminal** — `applied`, `rejected` ou `timeout` | capture d'`ACK` |
| **7** | **relire** — confirmation selon le type du rôle | égalité stricte, ou §4 |
| **8** | **RESTAURER** vers `V_initiale` — **pré-décidée** | `ACK` + preuve transport |
| **9** | **relire** — la valeur doit être revenue à `V_brut` | relecture consignée |

> **La restauration est due dès que la valeur a bougé**, que l'`ACK` ait conclu
> `applied` ou que la relecture ait montré la cible sans `ACK` terminal. **Elle
> n'est PAS due si la valeur n'a pas bougé** : restaurer serait alors écrire sans
> avoir caractérisé — `w4f` §7.3, cas 1.

### 6.1 Acquittements — la séquence attendue

`accepted` puis **l'un des trois terminaux** : `applied`, `rejected`, `timeout`.

| Terminal | Signification | Conduite |
|---|---|---|
| **`applied`** | relecture concordante dans la fenêtre | **nominal**. Restauration due |
| **`rejected`** | refus **avant** écriture — forme, borne, grille, expiration | **aucune écriture n'a eu lieu.** Restauration **NON due**. La campagne **s'arrête** : un rejet sur une cible calculée par le protocole est un **défaut du protocole**, et il doit être compris avant d'aller plus loin |
| **`timeout`** | fenêtre épuisée sans confirmation | **état indéterminé.** Établir par **lecture nue** ce que porte réellement la chaudière, puis §4 pour la pente, ou **arrêt** pour les rôles entiers |

> **`accepted` n'est jamais un succès.** Seul `applied` **corrélé au même
> `request_id`** vaut confirmation.

---

## 7. Arrêt de campagne — et ce qui le déclenche

> **Règle.** Un arrêt intervient **entre deux rôles, jamais au milieu d'un
> rôle** : la restauration due d'un rôle engagé s'exécute **toujours** avant
> l'arrêt.

| Déclencheur | Effet |
|---|---|
| une preuve d'état initial impossible à établir | **la campagne n'est pas engagée** |
| `rejected` sur une cible calculée par le protocole | **arrêt** après le rôle |
| `timeout` avec valeur **métier différente** de la cible — `VALEUR NON APPLIQUÉE` | **arrêt** |
| relecture discordante après restauration | **arrêt** |
| valeur qui bouge **sans commande émise** | **arrêt** — signe d'un second écrivain |
| redémarrage d'un service ou de la machine | **arrêt** |
| `TOLÉRANCE INSUFFISANTE` sur la pente | **arrêt**, après restauration — §4 |
| doute de l'exploitant, sans justification à fournir | **arrêt** |

**Les référentiels `AB` et `FA` de `G2-P` §12 s'appliquent intégralement**, sans
retrait ni allègement.

---

## 8. État initial sûr, gardes, restauration

**Repris de `W4-S` sans allègement** — le présent document n'en réécrit pas le
détail, il les rend opposables :

- les **treize preuves `EI-1` à `EI-13`**, dans l'ordre ;
- **`PR-1`** superviseur neutralisé, **`PR-2`** pont arrêté ;
- **`P-UFS`** — `UnitFileState` des **quatre** unités en **pièce dédiée**,
  déposée **avant le temps 1**, antériorité prouvée par la pièce elle-même ;
- **`G-a`** et **`G-b`**, cumulées ;
- la **restauration du dispositif historique en cinq étapes**, avec les **trois
  faits `A`, `B`, `C` établis séparément** et le **cycle nominal** du
  superviseur ;
- **`P-A1`** dépôt en écriture unique, **`P-SPT`** réarmement du puits.

> **Une seule différence avec `W4-S`, et elle est de cardinalité** : le puits
> portera **jusqu'à six rangs** au lieu de deux.

### 8.1 Une conséquence à déclarer avant le terrain

**Arsenal pilote les trois rôles en production.** Pendant toute la fenêtre, le
pont historique est **arrêté** : les commandes qu'Arsenal publie sur sa propre
surface **ne seront ni reçues ni acquittées**.

> **Conséquence attendue, et normale** : les capteurs de transaction d'Arsenal
> conclueront en **délai dépassé**, et ses mécanismes de reprise pourront
> s'activer. **Rien ne l'empêche, et le présent lot n'y touche pas** — modifier
> Arsenal est hors périmètre.
>
> **L'exploitant en est informé avant d'autoriser**, et il lui appartient de
> décider s'il suspend ou non ses automatismes — par un geste qui **ne relève
> pas de ce document**.
>
> **La fenêtre doit donc être COURTE**, et c'est un motif de plus pour grouper
> les trois rôles en une seule campagne.

---

## 9. Preuves exigées en sortie

| # | Sortie |
|---|---|
| **1** | **`P-UFS`** — pièce dédiée, quatre `UnitFileState`, horodatage antérieur au temps 1 |
| **2** | les **treize `EI`**, dans l'ordre, avec `PR-1` et `PR-2` **redoublées** |
| **3** | **par rôle** : `V_brut`, `V_initiale`, cible, et le calcul qui la produit |
| **4** | **par rôle** : la publication émise, son `request_id`, et l'**`ACK` terminal** |
| **5** | **par rôle** : la **preuve de transport** du puits — ligne d'invocation réelle, sorties standard et d'erreur **intégralement et séparément**, code retour, **durée mesurée** |
| **6** | **par rôle** : la relecture de confirmation, puis la relecture après restauration |
| **7** | **pour la pente** : l'écart `abs(relu − cible)` **en clair**, et laquelle des trois issues du §4 est retenue |
| **8** | la **cardinalité effective**, rang par rang, et le décompte du puits |
| **9** | les **cinq étapes** de restauration, faits `A`/`B`/`C` séparés, cycle nominal |
| **10** | **`G-a`** avant et après démarrage manuel · **`G-b`** hors la fenêtre d'autorité |
| **11** | tout critère **`AB`** ou **`FA`** atteint, **prononcé ou non** |
| **12** | ce qui **demeure non établi** |

**Toutes les pièces sont hachées et portées à un manifeste**, et le rapport est
**gelé hors dépôt** — le dépôt n'en portera que les empreintes.

---

## 10. Critère de succès global

> **`W4-T CONFIRMÉ`** — et il n'y a pas de demi-succès.

**Exige, cumulativement :**

1. les **treize `EI`** établies, `P-UFS` prouvée par pièce dédiée ;
2. les **trois rôles** écrits, chacun **`applied`** et **confirmé par
   relecture** ;
3. les **trois restaurations** exécutées, chacune ramenant la valeur à
   `V_brut` ;
4. **cardinalité exactement six**, et le puits portant six rangs ;
5. les **cinq étapes** de restauration achevées, cycle nominal compris ;
6. **aucun `AB`, aucun `FA`**.

**Tout autre cas est `W4-T ABANDONNÉ`**, avec le rang atteint et le motif.

> **Un abandon n'est pas un échec du lot.** Trois issues sont **utiles** :
> `W4-T CONFIRMÉ` · `TOLÉRANCE INSUFFISANTE` sur la pente, qui **produit
> précisément la mesure que ce rôle appelait** · `VALEUR NON APPLIQUÉE`, qui
> révèle un défaut réel **avant** qu'il n'atteigne la production.
>
> **Ce que le lot n'a pas le droit de faire, c'est de réessayer pour obtenir une
> issue plus flatteuse.**

---

## 11. L'autorisation humaine

> ### `NON DONNÉE`

**L'autorisation, si elle est donnée, MUST :**

| # | |
|---|---|
| **1** | être précédée d'un **AUDIT INDÉPENDANT** du présent document, et de son **INTÉGRATION** |
| **2** | **nommer `W4-T` ET sa version**, être explicite, distincte, et postérieure aux deux |
| **3** | **nommer les TROIS rôles**, et eux seuls |
| **4** | **dire que la restauration est PRÉ-DÉCIDÉE** pour les trois |
| **5** | porter les **actes réservés 1, 2 et 3** du `w4f` §11.1 |
| **6** | porter la **levée ponctuelle du `w4f` §11.2**, bornée aux quatre gestes |
| **7** | porter l'**extension nominale du puits**, bornée à cette campagne |
| **8** | valoir pour **une exécution, et une seule** |

**Elle MUST NOT :**

- être **déduite** de l'audit, de l'intégration, ou du merge ;
- se réclamer de l'autorisation d'un autre lot — **`G.2`, `G.3`, `W4-S` et le
  Lot 1 sont étrangers à celle-ci** ;
- porter l'**acte réservé 4** — **interdit en tout état de cause** ;
- valoir autorisation du **régime permanent**, du **re-pointage du
  superviseur**, ni d'aucune **modification d'Arsenal** ;
- valoir autorisation de `W4-F3`, `W4-F4`, `W4-F5`, `T0`, `T1` ou `T2`.

---

## 12. Ce qu'un auditeur doit pouvoir trancher AVANT le terrain

| | Question | Où elle se tranche |
|---|---|---|
| **1** | les **cibles** sont-elles minimales, bornées, et calculées sans arbitraire ? | §3, règle `V_initiale + 1 pas` |
| **2** | l'**ordre** des trois rôles est-il justifié par la sûreté ? | §3.1 |
| **3** | la **cardinalité** est-elle close et vérifiable sur un artefact ? | §5, six rangs du puits |
| **4** | le cas **flottant** distingue-t-il égalité binaire et égalité métier ? | §4, trois issues |
| **5** | un **rejet** ou un **timeout** conduit-il à un arrêt, jamais à un réessai ? | §6.1, §7 |
| **6** | la **restauration** est-elle due exactement quand la valeur a bougé ? | §6 |
| **7** | l'effet sur **Arsenal** est-il déclaré avant, et non découvert après ? | §8.1 |
| **8** | le **succès global** est-il défini sans demi-mesure ? | §10 |
| **9** | l'autorisation **exclut-elle** l'acte réservé 4 et le régime permanent ? | §11 |

---

## 13. Ce que ce document ne fait pas

Il **n'exécute rien** · **n'autorise rien** · ne conduit aucun terrain · ne
demande **aucun code** · **ne modifie ni le pont, ni le superviseur, ni leurs
unités, ni leur activation au démarrage** · **ne modifie pas Arsenal** · **ne
touche pas à l'acte réservé 4** · n'ouvre pas le régime permanent · ne rapproche
pas la bascule · ne révise **aucune tolérance** · ne lève aucune inconnue.

**Il borne une campagne de caractérisation, la referme, et s'arrête là.**

---

## 14. Réserves conservées

1. **Les trois écritures n'ont jamais été observées sous protocole.** Le pont
   historique les exerce quotidiennement, mais **exercer n'est pas
   caractériser**.
2. **La tolérance de la pente peut se révéler insuffisante.** C'est une issue
   **prévue**, non un incident — §4.
3. **`C1`, la coexistence, `U-2`, `U-3`, `H2`, `H6 (b)` demeurent ouvertes**, et
   la campagne n'en réduit aucune.
4. **L'unité de `getBrennerStatus` demeure non établie** — `C7` §4.3. Sans
   rapport avec la présente campagne, mais toujours ouverte.
5. **Arsenal subira une fenêtre sans acquittement**, et ses mécanismes de
   reprise pourront s'activer — §8.1. **Aucun contournement n'est proposé** : en
   proposer un supposerait de modifier Arsenal.
6. **Le régime permanent, le re-pointage du superviseur et la bascule demeurent
   entiers**, et relèvent des sous-objectifs 2 et 3 du Lot 2.
