# `W4-T2` — caractérisation de l'ECS, **le dernier rôle**

> ## `EXÉCUTÉ` — `W4-T2 CONFIRMÉ`, exécution `HOMOLOGUÉE`
>
> **Exécuté le 2026-09-04.** `applied`, **égalité stricte**, **régime `A`
> confirmé par l'observation — aucun démarrage de brûleur**, `R-ECS` sans effet
> parasite, **cardinalité 2**, fermeture nominale. Constat :
> **`w4t2-constat.md`**.
>
> **Les QUATRE rôles d'écriture du profil sont désormais caractérisés en
> écriture réelle. L'autorisation de ce document est CONSOMMÉE.**
>
> **`I-ECS` et le régime `B` demeurent OUVERTS.** La suite n'est plus une
> question d'écriture mais de durée : **`LOT 2B` — `lot2b-regime-permanent.md`**.

---

> **Version 1.** Ouverture **et** bornage d'une campagne **réduite à un seul
> rôle** : `dhw_setpoint` / `setTempWWsoll`, **le dernier des quatre que
> Boilerack déclare et n'a jamais émis**.
>
> **Aucun terrain n'est conduit par ce document. Aucun code n'est demandé.
> Aucune constante de site n'y figure.**
>
> **L'autorisation humaine est `NON DONNÉE`** — §14.
>
> **L'acte réservé 4 — bascule de souveraineté — demeure interdit en tout état
> de cause**, et l'autorisation de `W4-T2` **MUST NOT** le porter.

---

## 0. Convention et désignation

| Nom court | Document |
|---|---|
| `W4-T` | `w4t-trois-ecritures.md` — **CLOS** |
| `W4-TC` | `w4t-constat.md` |
| `W4-T1` | `w4t1-rejeu-pente.md` — le rejeu de la pente |
| `W4-T1C` | `w4t1-constat.md` — son constat, **exécution homologuée** |
| `W4-S` | `w4s-campagne-minimale.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `G2-P` | `w4f-g2-ecriture-bornee.md` |
| `w4f` | `w4f-write-sovereignty.md` |
| `C7` | `c7-mqtt-read-contract.md` |

**Désignation** : `W4-T2`, **sous-lot de `W4-T`**, dans l'usage de `W4-P1` /
`W4-P2` et de `W4-T1`. **Vérifiée libre.** La série `G.n` **MUST NOT** être
prolongée.

Unités désignées `<unité-boilerack>`, `<unité-pont>`, `<unité-démon>`,
`<unité-superviseur>`, `<timer-guard>`. **Aucune constante de site.**

> **`W4-T2` NE REMPLACE NI `W4-T` NI `W4-T1`.** Tout ce qu'ils établissent et qui
> n'est pas **explicitement restreint ici** demeure **opposable en l'état**.
> **Le présent document RÉDUIT ; il n'allège pas.**

---

## 1. Objet

> **Objet unique : caractériser `dhw_setpoint` / `setTempWWsoll`, en écrivant UNE
> seule fois `V_initiale + 1 °C`, en confirmant par ÉGALITÉ STRICTE, et en
> restaurant `V_initiale` si — et seulement si — la valeur a bougé.**

### 1.1 Ce que `W4-T2` établira, et rien de plus

La **réponse de transport**, la **forme de l'acquittement**, la **confirmation
par relecture**, et **l'effet physique réellement observé**.

> **Il n'établira pas** : que la coexistence est qualifiée · que `C1` est
> satisfaite · que `H2`, `H6 (b)`, `U-2` ou `U-3` seraient closes · **aucune
> capacité de production**. **Le régime permanent, le superviseur et la
> souveraineté demeurent HORS PÉRIMÈTRE.**

### 1.2 L'état des quatre rôles, et pourquoi il n'en reste qu'un

| Rôle | Commande | État |
|---|---|---|
| `heating_curve_shift` | `setNiveauM1` | **caractérisé** — `W4-C`, confirmé par `G.2` et `W4-S` |
| `heating_setpoint` | `setTempRaumNorSollM1` | **caractérisé** — `W4-T V2`, `W4-TC` §4 |
| `heating_curve_slope` | `setNeigungM1` | **caractérisé** — `W4-T1 V1`, `W4-T1C`, **forme décimale confirmée en vol** |
| **`dhw_setpoint`** | **`setTempWWsoll`** | **NON CARACTÉRISÉ. Jamais engagé.** |

> **C'est le dernier, et c'est aussi le seul dont l'effet soit RESSENTI.** Les
> trois autres ont été caractérisés hors saison de chauffe, **sans effet
> observable**. Celui-ci n'offre pas cette facilité : il agit sur l'eau chaude
> sanitaire, et le §4 lui est entièrement consacré.

---

## 2. Périmètre

> **`W4-T2` MUST NOT :**
>
> - écrire sur **un autre rôle** que `dhw_setpoint` — les trois autres
>   **compris** ;
> - émettre plus que la **cardinalité du §6** ;
> - **réémettre**, sous quelque forme et pour quelque motif que ce soit ;
> - **corriger** une valeur hors borne ou hors grille : **REJECT, jamais clamp** ;
> - **modifier** le profil, les bornes, `confirm_tolerance`, ou **aucun code** ;
> - **modifier** le pont, le superviseur, le démon, leurs unités, ou leur état
>   d'activation au démarrage ;
> - **modifier Arsenal**, en quoi que ce soit — **y compris le message retenu du
>   §5** ;
> - **basculer la souveraineté** — acte réservé **4**.

> **Le pont historique demeure l'unique écrivain réel de production**, hors la
> fenêtre de `W4-T2`, pendant laquelle il est **arrêté**.

---

## 3. La cible

| | |
|---|---|
| `V_initiale` | **relue le jour J**, par deux captures nues. **Jamais reprise d'un relevé antérieur** |
| Cible | **`V_initiale + 1 °C`** — le pas de la grille `[10 ; 60]` |
| Si la cible dépasse `60` | **le rôle n'est pas écrit, et la campagne se clôt.** Aucune valeur de repli, et le pas n'est **jamais** retranché |

**Le rôle est ENTIER** : la cible se calcule sur la grille entière, exactement, et
se rend par la forme entière — `11`, jamais `11.0`.

> **La discipline du `W4-T1` §3.1 demeure, même si le piège ne s'applique pas
> ici** : la cible est portée **comme le littéral du cran**, et **jamais**
> obtenue par une addition dont la représentation serait à démontrer. **Ce qui
> était une nécessité pour la pente est une hygiène pour l'ECS**, et elle ne
> coûte rien.

**`confirm_tolerance` vaut `0.0` pour ce rôle** : la confirmation est une
**ÉGALITÉ STRICTE**. Il n'y a **pas** de départage de tolérance — le cas à trois
issues du `W4-T1` §5 **ne s'applique pas**, et l'invoquer serait une erreur.

---

## 4. L'effet physique — le cas neuf, et il faut le traiter à part

> **C'est le premier rôle que Boilerack écrira dont l'effet soit RESSENTI.**

### 4.1 L'effet n'est pas constant : il dépend d'où se trouve `V_initiale`

La consigne ECS n'agit qu'en **comparaison** de la température réelle du
ballon. Deux régimes, et ils ne se confondent pas :

| Régime | Condition | Effet attendu de `+1 °C` |
|---|---|---|
| **A — consigne très en dessous du ballon** | `V_initiale + 1` demeure **nettement inférieure** à la température du ballon relevée | **aucune demande**, aucun démarrage de brûleur, **aucun effet observable** |
| **B — consigne au voisinage du ballon** | `V_initiale + 1` **approche ou dépasse** la température du ballon | **un cycle ECS peut être provoqué** : brûleur, gaz consommé, eau portée au plus `1 °C` plus haut |

> **`I-ECS` — INCONNUE NOMMÉE.** *« L'hystérésis de la demande ECS de cette
> installation n'est pas établie. »* On ne sait donc **pas** à quelle distance
> exacte de la température du ballon la demande s'enclenche.
>
> **Conséquence opposable : le régime B MUST être tenu pour POSSIBLE dès que
> l'écart n'est pas manifestement large.** La campagne **ne suppose jamais** que
> l'effet sera nul : elle **relève**, **prédit**, puis **observe**.

### 4.2 Ce que le protocole exige, en conséquence

| # | Exigence |
|---|---|
| **1** | **relever la température du ballon** au temps 1, par la surface de lecture aval, **avant** tout acte |
| **2** | **consigner l'écart** `température du ballon − (V_initiale + 1)`, **en clair** |
| **3** | **prononcer le régime attendu**, `A` ou `B`, **avant** l'écriture, et le porter à l'autorisation |
| **4** | **observer le brûleur** — modulation et état — **avant, pendant et après** la fenêtre, et consigner **tout démarrage** |
| **5** | **attribuer** tout démarrage observé : provoqué par l'écriture, ou **cycle propre de l'installation** sans rapport |

> **L'exigence 5 n'est pas rhétorique.** `W4-T V2` a vu le brûleur démarrer en
> fenêtre — **c'était le cycle ECS normal du matin**, et sa consigne n'avait pas
> été touchée. **Un démarrage observé n'est pas une preuve de causalité**, et le
> constat devra le dire.

### 4.3 Ce qui borne le risque, et ce qui ne le borne pas

**Ce qui le borne** : `+1 °C` est **le plus petit écart que la grille permette**
— *« il n'existe pas de variation ECS plus petite »* · la restauration est
**pré-décidée** et suit immédiatement · l'exploitant est **physiquement
présent** · la borne haute `60` est celle du profil audité, et le protocole ne
la franchit jamais.

**Ce qui ne le borne pas, et qu'il faut dire** : si `V_initiale` est déjà haute,
`+1 °C` produit de l'eau **plus chaude d'un degré** pendant quelques minutes.
**Aucune clause ne peut supprimer cet effet** — elle peut seulement le rendre
**minimal, prévu, observé et réversible**, ce que ce document fait.

---

## 5. `R-ECS` — le message RETENU sur la surface historique

> **Risque matériel propre à ce rôle, découvert lors de `W4-T1`.**

Le courtier porte un message **retenu** sur le topic de commande **du pont
historique**, portant une consigne ECS. Il a été **observé**, non modifié.

**Conséquence, à déclarer avant le terrain :** un client MQTT reçoit les messages
retenus **à la souscription**. **Au redémarrage du pont, en fin de campagne, ce
message peut lui être redélivré, et le pont peut alors écrire la valeur qu'il
porte** — sans que la campagne l'ait demandé.

| Cas | Effet |
|---|---|
| valeur retenue **égale** à `V_initiale` | l'écriture éventuelle du pont est **sans effet de valeur** |
| valeur retenue **différente** de `V_initiale` | **le pont peut déplacer la consigne après la campagne**, et ce mouvement **n'est pas imputable à Boilerack** |

**Exigences :**

1. **relever la valeur retenue au temps 1**, et la consigner ;
2. **la comparer à `V_initiale`**, et **prononcer le cas** avant l'écriture ;
3. prendre la lecture de l'étape 1 du temps 14 **AVANT** le redémarrage du pont,
   **et une seconde lecture APRÈS**, les consigner **toutes les deux**, et
   **attribuer** tout écart entre elles ;
4. **ne pas supprimer, ni réécrire, ni vider le message retenu** — ce serait
   **modifier Arsenal**, hors périmètre.

> **Un écart entre les deux lectures du temps 14 n'est PAS `FA-3`** s'il est
> **expliqué par `R-ECS`** et que la valeur atteinte est **celle du message
> retenu**. Il est `FA-3` dans **tout autre cas**.

---

## 6. Cardinalité — deux rangs au plus

| | Écriture de cible | Restauration | Ailleurs |
|---|---|---|---|
| `dhw_setpoint` | **1** | **au plus 1** | **0** |

> **DEUX écritures au maximum, et pas une de plus.** Le puits doit porter **au
> plus deux rangs**, `01` et `02`. **Un troisième rang est une violation.**
>
> **Zéro ou un rang est NORMAL.** Le décompte attendu se déduit de l'issue,
> jamais l'inverse.
>
> Les **lectures** n'entrent pas dans ce décompte. **Une écriture éventuelle du
> pont historique au titre de `R-ECS` n'y entre pas non plus** — elle n'est pas
> le fait de Boilerack, et le puits ne l'enregistre pas. **Elle est consignée à
> part.**

---

## 7. La restauration — due exactement quand la valeur a bougé

| Situation | Restauration |
|---|---|
| `applied` | **DUE** |
| `timeout`, **relecture nue** montrant la cible | **DUE** |
| `timeout`, **valeur inchangée** | **NON DUE** |
| `rejected` | **NON DUE** — aucune écriture n'a eu lieu |

> **Restaurer une valeur qui n'a pas bougé serait écrire sans avoir
> caractérisé** — `w4f` §7.3, cas 1.

**La restauration est PRÉ-DÉCIDÉE par l'autorisation, armée avant l'écriture, et
elle ramène à `V_initiale` — jamais ailleurs.** **Aucune seconde tentative.**

---

## 8. Séquence — dix actes

| # | Acte | Preuve |
|---|---|---|
| **1** | **lire l'état initial** par **deux captures nues** — texte et `-J`, hors chemin Boilerack. Constituer `V_brut`, dériver `V_initiale` **sans perte** | concordance brute **et** sémantique |
| **2** | **relever la température du ballon et l'état du brûleur**, et **la valeur retenue** du §5 | §4.2, §5 |
| **3** | **calculer la cible** `V_initiale + 1`. **Si elle dépasse `60` : le rôle n'est pas écrit** | cible consignée, **avec son littéral** |
| **4** | **prononcer le régime `A` ou `B`** et le **cas `R-ECS`** | §4.1, §5 |
| **5** | **armer la restauration** — commande écrite d'avance, **non exécutée** | fichier d'armement |
| **6** | **garde de fraîcheur** — relecture, concordance avec `V_brut` exigée | sinon **arrêt** |
| **7** | **ÉCRIRE la cible** — **une seule publication** | `ACK` + preuve de transport |
| **8** | **attendre l'`ACK` terminal** — `applied`, `rejected` ou `timeout` | capture d'`ACK` |
| **9** | **relire nûment**, et **observer le brûleur** | **égalité stricte** ; §4.2 exigences 4 et 5 |
| **10** | **RESTAURER** vers `V_initiale` **si et seulement si** le §7 la rend due, puis **relire** | `ACK` + transport + relecture |

### 8.1 Acquittements

`accepted` puis **l'un des trois terminaux**.

| Terminal | Conduite |
|---|---|
| **`applied`** | **nominal.** Restauration due |
| **`rejected`** | **aucune écriture.** Restauration **NON due**. **Arrêt** : un rejet sur une cible calculée par le protocole est un **défaut du protocole** |
| **`timeout`** | **état indéterminé.** L'établir par **lecture nue**, puis §7. **Aucune seconde tentative** |

> **`accepted` n'est jamais un succès.** Seul `applied` **corrélé au même
> `request_id`** vaut confirmation.

---

## 9. Arrêt de campagne

**Le référentiel du `W4-T` §7 s'applique intégralement**, et **les référentiels
`AB` et `FA` de `G2-P` §12 avec lui**, sans retrait.

**S'y ajoute, propre à ce rôle :**

| Déclencheur | Effet |
|---|---|
| **la température du ballon monte de plus de `1 °C` au-dessus de son relevé initial** | **arrêt**, après restauration due |
| **un démarrage de brûleur non attribuable** — ni à l'écriture, ni à un cycle propre identifié | **arrêt**, après restauration due |

> **Il n'y a qu'un rôle : tout arrêt est la fin de la campagne.** La restauration
> due s'exécute **toujours avant** l'arrêt.

---

## 10. État initial sûr, préconditions

**Repris de `W4-S`, `W4-T` et `W4-T1` sans allègement** :

- les **treize preuves `EI-1` à `EI-13`**, dans l'ordre ;
- **`PR-1`** superviseur neutralisé, **`PR-2`** pont arrêté, **redoublées** ;
- **`P-UFS`** — quatre `UnitFileState` en **pièce dédiée**, **avant le temps 1** ;
- **`G-a`** et **`G-b`**, cumulées ;
- **`P-A1`** dépôt en écriture unique, **`P-SPT`** réarmement du puits ;
- **`P-DEP` étendue**, **`P-RND`**, **`P-VI`** — §10.1 ;
- la **restauration en trois volets** — §10.3.

### 10.1 Les quatre pièces prévol — acquis de `W4-T1`

**Avant le temps 1**, et **produites par LECTURE de l'installation** :

| Pièce | Ce qu'elle MUST porter |
|---|---|
| **`P-DEP`** étendue | les **QUATRE rôles** exposés par le service **installé**, **`dhw_setpoint` nommément** avec bornes et pas · la **concordance d'empreinte installée / dépôt intégré**, **chaîne de rendu incluse** |
| **`P-UFS`** | les quatre `UnitFileState` |
| **`P-VI`** | les deux captures nues, `V_brut`, `V_initiale`, la cible, **et le calcul qui la produit** · **la température du ballon**, **l'état du brûleur** et **la valeur retenue** du §5 |
| **`P-RND`** | les **octets exacts** que la cible produira, **par le code installé**, **hors ligne** — ni courtier, ni démon, ni chaudière |

> **`P-RND` demeure exigée alors même que la forme entière est déjà
> caractérisée.** Elle ne coûte rien, et elle prouve **ce que ce build-là rendra
> pour cette cible-là**. `W4-T V1` a montré ce que coûte une précondition
> absente ; `W4-T1` a montré ce que vaut une précondition présente. **On ne la
> retire pas parce qu'on se croit sûr.**

**Chacune est satisfaite ou la campagne MUST NOT être engagée.** **Aucune
reconstruction depuis le dépôt n'est admise.**

### 10.2 Le déploiement est un acte **antérieur** et **hors périmètre**

`P-DEP` et `P-RND` **constatent** ; elles n'accomplissent pas, et **n'autorisent
aucun déploiement**.

### 10.3 Restauration — de la valeur, de l'installation, des fichiers

| | |
|---|---|
| **1. la valeur** | vers `V_initiale`, **si et seulement si** le §7 la rend due |
| **2. l'installation** | les **cinq étapes**, faits **`A`**, **`B`**, **`C`** établis séparément, **cycle nominal** du superviseur |
| **3. les fichiers persistés** | **retour byte à byte**, prouvé par empreintes **avant et après** |

**S'y ajoute** : les **deux lectures** du §5 exigence 3, avant **et** après le
redémarrage du pont.

### 10.4 Conséquence sur Arsenal — déclarée avant, non découverte après

Pendant toute la fenêtre le pont est **arrêté** : les commandes d'Arsenal **ne
seront ni reçues ni acquittées**, ses capteurs de transaction conclueront en
**délai dépassé**, et ses mécanismes de reprise pourront s'activer. **Le présent
lot n'y touche pas.** **La fenêtre doit être COURTE.**

### 10.5 Les trois réserves de `W4-T1`, intégrées

| | Réserve | Ce que `W4-T2` en fait |
|---|---|---|
| **1** | l'incident `printf` | **toute écriture de pièce se fait par `tee -a`**, jamais par une construction de format |
| **2** | le puits absent du manifeste | **le répertoire brut du puits est inclus au manifeste**, tel quel, et non par copies |
| **3** | la présence humaine | **c'est une DÉCLARATION de l'opérateur.** La session distante la **rapporte** ; **elle ne l'établit pas**, et le rapport doit l'écrire ainsi |

---

## 11. Preuves exigées en sortie

| # | Sortie |
|---|---|
| **0** | **`P-DEP` étendue**, **`P-RND`**, **`P-VI`**, **`P-UFS`** — horodatages **antérieurs au temps 1** |
| **1** | les **treize `EI`**, dans l'ordre, `PR-1` et `PR-2` **redoublées** |
| **2** | `V_brut`, `V_initiale`, la cible, **son littéral**, et le calcul |
| **3** | **la température du ballon**, **l'écart en clair**, et le **régime `A` ou `B` prononcé avant l'écriture** |
| **4** | **la valeur retenue du §5** et le **cas `R-ECS` prononcé avant l'écriture** |
| **5** | la publication émise, son `request_id`, et l'**`ACK` terminal** |
| **6** | la **preuve de transport** — ligne d'invocation réelle, sorties standard et d'erreur **intégralement et séparément**, code retour, **durée mesurée** |
| **7** | la relecture nue, l'**égalité stricte** constatée ou non |
| **8** | **l'observation du brûleur avant, pendant et après**, et **l'attribution** de tout démarrage |
| **9** | la restauration — **son caractère dû ou non dû, motivé** — puis la relecture |
| **10** | la **cardinalité effective**, rang par rang |
| **11** | les **cinq étapes**, faits `A`/`B`/`C` séparés, cycle nominal |
| **12** | **les deux lectures du temps 14**, avant et après redémarrage du pont, et **l'attribution de tout écart** |
| **13** | les **fichiers persistés**, empreintes **avant et après** |
| **14** | **`G-a`** avant et après démarrage manuel · **`G-b`** hors la fenêtre d'autorité |
| **15** | tout critère **`AB`** ou **`FA`** atteint, **prononcé ou non** |
| **16** | ce qui **demeure non établi** |

**Toutes les pièces sont hachées et portées à un manifeste — le répertoire brut
du puits COMPRIS** (§10.5). Le rapport est **gelé hors dépôt**.

---

## 12. Critère de succès

> **`W4-T2 CONFIRMÉ`** — et il n'y a pas de demi-succès.

1. **`P-DEP` étendue**, **`P-RND`**, **`P-VI`** et **`P-UFS`** prouvées, antérieures ;
2. les **treize `EI`** établies ;
3. le rôle écrit **une fois**, **`applied`**, confirmé par **égalité stricte** ;
4. la restauration **exécutée**, ramenant la valeur à `V_brut` ;
5. **cardinalité exactement deux** ;
6. **tout démarrage de brûleur attribué**, et la température du ballon revenue
   dans sa plage initiale ;
7. les **cinq étapes** achevées, **les deux lectures du §5** consignées, et les
   **fichiers persistés revenus byte à byte** ;
8. **aucun `AB`, aucun `FA`**.

**Tout autre cas est `W4-T2 ABANDONNÉ`**, avec le motif.

> **Un abandon n'est pas un échec du lot.** *« Ce que le lot n'a pas le droit de
> faire, c'est de réessayer pour obtenir une issue plus flatteuse. »*

---

## 13. Ce qu'un auditeur doit pouvoir trancher AVANT le terrain

| | Question | Où |
|---|---|---|
| **0** | le service qui va tourner porte-t-il le profil **et** la chaîne de rendu audités, prouvés **depuis l'installation** ? | §10.1 |
| **1** | la forme qui partira est-elle prouvée **avant** la fenêtre, sans rien émettre ? | §10.1, `P-RND` |
| **2** | l'**effet physique** est-il prédit **avant** l'écriture, et non découvert après ? | §4.1, §4.2 |
| **3** | l'inconnue d'hystérésis est-elle **nommée** plutôt que supposée nulle ? | §4.1, `I-ECS` |
| **4** | le **message retenu** est-il traité comme un risque, sans être modifié ? | §5, `R-ECS` |
| **5** | la confirmation est-elle une **égalité stricte**, sans départage de tolérance emprunté au cas flottant ? | §3 |
| **6** | la **cardinalité** est-elle close, et une écriture du pont au titre de `R-ECS` exclue du décompte **et consignée** ? | §6 |
| **7** | la **restauration** est-elle due exactement quand la valeur a bougé ? | §7 |
| **8** | tout **démarrage de brûleur** doit-il être **attribué**, et non seulement constaté ? | §4.2 exigence 5 |
| **9** | les trois réserves de `W4-T1` sont-elles **intégrées**, et non seulement citées ? | §10.5 |
| **10** | l'autorisation **exclut-elle** l'acte réservé 4 et le régime permanent ? | §14 |

---

## 14. L'autorisation humaine

> ### `NON DONNÉE`

**L'autorisation, si elle est donnée, MUST :**

| # | |
|---|---|
| **1** | être précédée d'un **AUDIT INDÉPENDANT** du présent document, et de son **INTÉGRATION** |
| **2** | **nommer `W4-T2` ET sa version**, être explicite, distincte, et postérieure aux deux |
| **3** | **nommer `dhw_setpoint`, et lui seul** |
| **4** | **qualifier la publication de PREMIÈRE** au sens de `W4-C` — **première émission de ce rôle**, quand bien même la forme entière est déjà caractérisée |
| **5** | **accepter explicitement l'effet physique** du §4, **régime `B` compris** |
| **6** | **dire que la restauration est PRÉ-DÉCIDÉE**, et **conditionnelle** au §7 |
| **7** | porter les **actes réservés 1, 2 et 3** du `w4f` §11.1 |
| **8** | porter la **levée ponctuelle du `w4f` §11.2**, bornée aux gestes nécessaires |
| **9** | porter l'**extension nominale du puits**, bornée à cette campagne |
| **10** | valoir pour **une exécution, et une seule** |

**Elle MUST NOT :**

- être **déduite** de l'audit, de l'intégration, ou du merge du présent document ;
- se réclamer de l'autorisation d'un autre lot — **`W4-T` V1 et V2, `W4-T1`,
  `G.2`, `G.3`, `W4-S` et le Lot 1 sont étrangers à celle-ci, et toutes leurs
  autorisations sont CONSOMMÉES** ;
- porter l'**acte réservé 4** — **interdit en tout état de cause** ;
- valoir autorisation du **régime permanent**, du **re-pointage du
  superviseur**, ni d'aucune **modification d'Arsenal** ;
- valoir autorisation de `W4-F3`, `W4-F4`, `W4-F5`, `T0`, `T1` ou `T2`.

---

## 15. Ce que ce document ne fait pas

Il **n'exécute rien** · **n'autorise rien** · ne conduit aucun terrain · ne
demande **aucun code** · **ne modifie ni le profil, ni les bornes, ni
`confirm_tolerance`** · **ne modifie ni le pont, ni le superviseur, ni leurs
unités, ni leur activation au démarrage** · **ne modifie pas Arsenal, ni le
message retenu du §5** · **ne touche pas à l'acte réservé 4** · n'ouvre pas le
régime permanent · ne rapproche pas la bascule · **n'autorise aucun
déploiement** · ne lève pas `I-ECS`.

**Il borne une campagne d'un seul rôle, la referme, et s'arrête là.**

---

## 16. Réserves conservées

1. **`setTempWWsoll` n'est pas caractérisée**, et ne le sera pas par ce
   document : **seule une exécution autorisée pourra l'établir**.
2. **`I-ECS` demeure ouverte.** L'hystérésis de la demande ECS **n'est pas
   établie**, et la campagne ne la lève pas : elle **relève l'écart et observe**.
3. **`R-ECS` n'est pas neutralisée**, elle est **déclarée**. La neutraliser
   supposerait de toucher au message retenu, donc à Arsenal — **hors périmètre**.
4. **L'effet ressenti ne peut pas être supprimé**, seulement rendu minimal,
   prévu, observé et réversible.
5. **La caractérisation des quatre rôles ne vaut PAS capacité de production.**
   Quand bien même `W4-T2` réussirait, **`C1`, la coexistence, `U-2`, `U-3`,
   `H2` et `H6 (b)` demeureraient entières**, et la bascule aussi éloignée.
6. **`P-DEP`, même étendue, ne couvre pas tout le code déployé** ni les
   dépendances du service.
7. **L'unité de `getBrennerStatus` demeure non établie** — `C7` §4.3. **Elle
   n'est pas sans rapport ici** : l'observation du brûleur du §4.2 s'appuie sur
   `burner_modulation` et `burner_state`, et **leur unité est celle-là même qui
   n'est pas établie**. L'observation demeure **relative** — un passage de `0` à
   non-`0` — et **le rapport devra le dire**.
8. **Le régime permanent, le re-pointage du superviseur et la bascule demeurent
   entiers**, et relèvent des sous-objectifs 2 et 3 du Lot 2.
