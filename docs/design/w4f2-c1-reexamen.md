# Réexamen de la barrière `C1`

> **Ce document est un cadrage d'analyse.** Il n'ouvre aucun terrain, ne modifie
> aucun contrat, ne crée aucun critère et n'autorise rien. Il instruit une
> question de modélisation que le corpus avait explicitement réservée, compare
> les voies de sortie, et propose un arbitrage à l'humain.
>
> **Il ne modifie aucun document existant.** `w4f1-confirmation-window.md` reste
> `CLOSED` et son contrat fait autorité tant qu'un amendement audité ne l'a pas
> remplacé.

## 1. Décision humaine consignée

> **POURSUIVRE W4-F2.** Orientation : **instruire d'abord la levée ou le
> remplacement de la barrière `C1`, sans terrain à ce stade.**
>
> Motif : *« L'objectif reste de terminer Boilerack. Le prochain travail doit
> porter directement sur la barrière `C1`, car c'est le verrou qui empêche
> actuellement toute trajectoire vers `T0 GO`. »*

**Portée** — cette décision autorise **un lot documentaire d'instruction de
`C1`**. Elle n'autorise **aucune** modification de production, **pas** `debug`,
**pas** l'Acte B, **pas** `T0` / `T1` / `T2`, et **ne choisit pas** encore entre
modification du contrat, modification de configuration ou correction de
modélisation.

## 2. Question centrale

> Quelle modification **minimale, démontrable et gouvernable** du contrat, de la
> configuration ou de la modélisation permettrait de rétablir une trajectoire
> réellement possible vers `T0 GO`, **sans affaiblir la sûreté que `C1` cherche à
> garantir** ?

---

## 3. La fonction de sûreté de `C1`

Avant de discuter sa forme, il faut établir ce qu'elle protège. Sept questions,
sept réponses sourcées.

### 3.1 Quel risque exact `C1` empêche-t-il ?

**Un redémarrage machine automatique**, déclenché par le superviseur historique.

`w4c-write-capture-protocol.md` §8 établit la chaîne : le superviseur sonde le
démon toutes les **3 minutes** par un appel `vclient` direct, avec un budget de
**5 s**. En cas d'échec de cette sonde, il **redémarre l'unité du pont**, attend
**90 s**, puis sonde à nouveau ; si l'échec persiste, il **redémarre la machine**.

> **« Le chemin de redémarrage machine est donc à deux échecs de sonde de
> distance. »** — `w4c-write-capture-protocol.md` §8.

`C1` empêche qu'une occupation de la liaison par Boilerack fasse expirer une
sonde, et donc engage le premier pas de cette chaîne.

### 3.2 Quelle ressource ou fenêtre temporelle protège-t-il ?

**La fenêtre de 5 s** dont dispose une sonde du superviseur pour aboutir — la
liaison Optolink partagée étant la ressource disputée.

Une seconde fenêtre existe, mais elle n'appartient **pas** à `C1` : les **90 s**
entre les deux échecs, décomposées en `T_detection + T_reaction + T_release`
(`w4f1-confirmation-window.md` §8.6.1). C'est la fenêtre de rattrapage humain,
gouvernée par les événements d'arrêt `E1`–`E8`, non par `C1`.

### 3.3 Quelle population entre dans son calcul ?

> **« La population pertinente est celle des sondes du superviseur, et elle
> seule. Pas l'ensemble des connexions au démon : le pont y domine numériquement,
> et son coût ne gouverne aucun budget que `C1` protège. »** — §8.5.

Cette restriction est **normative**, et elle est reprise par
`w4f1a-vcontrold-concurrency.md` §6.1, qui exclut explicitement six catégories et
**interdit d'extrapoler** depuis le comportement d'une autre commande.

### 3.4 Pourquoi `budget_superviseur = 5,000 s` ?

Ce n'est ni un choix de W4-F1 ni une marge de confort : c'est le **budget réel de
la sonde**, sourcé `w4c-write-capture-protocol.md` §8. Le constat Acte A le
retrouve indépendamment dans la configuration déployée du superviseur —
`VCLIENT_TIMEOUT=5` — et confirme la cadence de 3 minutes
(`OnUnitInactiveSec=3min`).

**C'est une valeur d'installation, pas une valeur de contrat.** Elle n'est pas
négociable par W4-F1 : la modifier serait modifier le superviseur, ce qui relève
d'un autre périmètre.

### 3.5 Pourquoi la borne publique C5 entre-t-elle dans `max(...)` ?

Pour garantir que **T0 ne puisse que resserrer `C1`, jamais la relâcher** :

> **« Une mesure T0 qui rendrait une borne supérieure à 4,029 s durcit le seuil ;
> une mesure qui rendrait une borne inférieure est sans effet, la valeur publiée
> l'emportant. »** — §8.5.

Le motif est explicite : sans le `max`, une population T0 dominée par le pont
abaisserait la borne et **assouplirait** `C1` « au moment précis où l'on cherche à
protéger le superviseur ». Le `max` est un **cliquet de sûreté**.

### 3.6 Pourquoi T0 ne peut-il que resserrer `C1` ?

Même raison, énoncée comme propriété : le sens de variation est **unilatéral** et
il va vers la sûreté. C'est une propriété **structurelle** du `max`, pas une
politique révisable au cas par cas.

### 3.7 L'invariant proposé par ce lot

**Aucune pièce du corpus ne porte d'invariant sous cette forme.** Ce qui suit est
une **construction du présent lot**, déduite des sources citées aux §3.1 à §3.6 et
formulée indépendamment de la formule actuelle. **Elle n'a aucun statut
contractuel** et ne peut en acquérir un que par un amendement audité :

> **INVARIANT DE SÛRETÉ — PROPOSÉ PAR CE LOT.** L'exposition de Boilerack **ne
> doit jamais** pouvoir faire échouer une sonde du superviseur historique —
> c'est-à-dire ne jamais pouvoir porter la durée totale d'une sonde au-delà de
> son budget de 5 s — car
> un tel échec engage le premier pas d'une chaîne à deux échecs qui aboutit à un
> **redémarrage machine automatique**.

Trois propriétés accompagnent l'invariant et doivent lui survivre :

1. **Population** : la garantie porte sur les **sondes du superviseur**, et sur
   elles seules (§3.3).
2. **Nature de la garantie** : une **borne déterministe**, jamais un quantile —
   §8.5 a explicitement retiré `q95` de `C1`, avec un contre-exemple chiffré.
3. **Sens unilatéral** : toute mesure ultérieure ne peut que **durcir** le
   critère (§3.5, §3.6).

> **Ce que l'invariant ne dit pas.** Il ne prescrit **aucune** forme algébrique,
> **aucune** valeur de seuil, et **aucune** grandeur particulière à mesurer. Il
> dit quel événement doit rester impossible. C'est à ce niveau que toute révision
> doit être jugée.

---

## 4. Reconstruction de `C1`

### 4.1 La formule canonique, verbatim

`w4f1-confirmation-window.md` §8.5 :

```
borne_effective  =  max( borne_publique_C5 , borne_T0_superviseur )
seuil_C1         =  budget_superviseur  −  borne_effective
rafale_max(T1) ≤ seuil_C1      et      rafale_max(T2) ≤ seuil_C1
```

### 4.2 Variables, unités, provenance

| Terme | Valeur | Unité | Provenance | Nature |
|---|---:|---|---|---|
| `budget_superviseur` | **5,000 s** | durée | `w4c-write-capture-protocol.md` §8 ; corroboré par le constat Acte A (`VCLIENT_TIMEOUT=5`) | **fait d'installation** |
| `borne_publique_C5` | **4,029 s** | durée | `c5-vclient-contract.md` §9, maximum publié de « Lecture Optolink réelle, production active : 2 669 à 4 029 ms » | **mesure publiée** |
| `borne_T0_superviseur` | — | durée | T0-C, **seulement si** T0-A isole la population des sondes | **non existante à ce jour** |
| `borne_effective` | **4,029 s** | durée | `max(4,029 ; ∅)` | dérivée |
| **`seuil_C1`** | **0,971 s** | durée | `5,000 − 4,029` | dérivée |
| `rafale_max` | — | durée | mesuré en T1/T2 sur la source retenue en T0-D | non mesuré |
| `r` (résolution exigée) | **< 0,485 s** | durée | `seuil_C1 / 2 = 0,4855`, arrondi vers le bas | **dérivée du seuil** |

### 4.3 Le raisonnement, reconstruit

§8.5 le donne en une phrase : *« Sous le régime additif (§6.5), une transaction
concurrente paie l'attente puis son propre coût. Pour que la somme reste sous le
budget, l'attente doit rester sous `budget − coût`. »*

Soit, en grandeurs nommées :

```
attente_imposée_à_la_sonde  +  coût_propre_de_la_sonde  ≤  budget_superviseur
```

`C1` identifie `attente_imposée_à_la_sonde` à `rafale_max`, et
`coût_propre_de_la_sonde` à `borne_effective`.

### 4.4 Les grandeurs, distinguées

Le corpus les mélange dans une seule mesure agrégée. Les séparer est le préalable
de toute analyse.

| Grandeur | Définition | Statut dans le corpus |
|---|---|---|
| **coût de sonde historique** | durée totale d'un appel `vclient` du superviseur, de l'invocation au résultat | agrégée dans C5 §9 ; **jamais mesurée sur la population du superviseur** |
| **temps de service** | durée pendant laquelle le démon traite effectivement une session, liaison tenue | **non isolé** |
| **occupation du lien** | durée pendant laquelle un client **détient** la liaison et en exclut les autres | **non isolée** |
| **délai marginal ajouté par Boilerack** | supplément de durée qu'une sonde subit **du fait de l'existence de Boilerack** | **jamais défini ni mesuré** |
| **intervalle entre requêtes** | 3 min pour le superviseur ; **10 s pour le pont** selon `w4f1a-vcontrold-concurrency.md` §4.2 (sourcé W4-C §8-§9), valeur **non réétablie** par le constat Acte A | partiellement établi |
| **rafale** | occupation cumulée vue par une sonde arrivant pendant une séquence de lectures Boilerack | définie, non mesurée |
| **délai de réaction superviseur** | 90 s entre les deux échecs, décomposés en `T_detection + T_reaction + T_release` | §8.6.1, **hors `C1`** |

### 4.5 Ce que la mesure C5 §9 est réellement

C5 §9 mesure **« Lecture Optolink réelle, production active : 2 669 à 4 029 ms »**.

Trois propriétés de cette mesure, toutes établies par sa propre source :

1. elle est **agrégée** — c'est une **durée totale d'invocation**, qui ne distingue
   ni service, ni attente, ni occupation ;
2. elle est prise **« production active »** : elle **ne permet donc pas d'exclure**
   une composante d'attente. **Elle n'établit pas non plus qu'il y en ait une.**
   Deux faits bornent ce point, et ils vont dans des sens différents —
   `w4f1-confirmation-window.md` §6.5 dit que la mesure **« suggère »** une
   ressource disputée et que **« cela ne l'établit pas »** ; et
   `c5-vclient-contract.md` place expressément sa campagne **« entre deux cycles du
   superviseur local, pour écarter toute contention avec lui »**. Une contention
   avec le **pont** n'est ni établie ni exclue ;
3. elle porte sur **« une lecture »**, sans qualification de population : rien n'y
   rattache spécifiquement la sonde du superviseur.

C5 §9 le dit lui-même : *« Aucun budget de production n'est arrêté dans ce lot… Le
dimensionnement relève d'un arbitrage ultérieur, appuyé sur des mesures
dédiées. »*

---

## 5. La question de modélisation — instruite, non tranchée

### 5.1 La réserve, verbatim

`w4f1a-vcontrold-concurrency.md` §13 l'a consignée et **délibérément non
instruite** :

> *« L'intervalle `2 669 – 4 029 ms` de C5 est mesuré "production active",
> c'est-à-dire déjà sous contention avec le pont. W4-F1 §8.5 l'emploie à deux
> titres dans la même soustraction : comme occupation de Boilerack et comme coût
> propre de la sonde du superviseur. Savoir si ces deux emplois sont légitimes, ou
> si la grandeur pertinente est le délai marginal ajouté par Boilerack, est une
> question ouverte. »*

> **Sur les mots « déjà sous contention ».** Ils appartiennent à la réserve citée,
> et sont reproduits tels quels. Le présent document **ne les reprend pas à son
> compte** : §4.5 établit que la contention est **suggérée, non établie**, et le
> raisonnement du §5.3 est construit pour ne rien lui devoir.

> **Tension de gouvernance, à porter.** Le même §13 réserve cette question à la
> branche A — *« à n'ouvrir que si le régime est `ADDITIF` »* — au motif que
> rouvrir un contrat clos avant de savoir si la branche s'applique « serait
> l'inverse de la méthode suivie ». La décision humaine du §1 ouvre l'instruction
> **documentaire** de cette question. **Instruire n'est pas construire V-2** : le
> §12 traite de l'opérativité, qui reste conditionnée.

### 5.2 Le double emploi — établi

Les deux emplois de l'intervalle C5 §9 dans la même inégalité sont **factuellement
avérés** :

| Emploi | Où | Grandeur que la formule lui prête |
|---|---|---|
| **1** | `borne_effective = max(4,029 ; …)` (§8.5) | le **coût propre de la sonde du superviseur** |
| **2** | *« une lecture unique coûte 2,669 à 4,029 s, donc `rafale_max ≥ 2,669 s` par construction »* (§8.5) | l'**occupation imposée par Boilerack** |

**Ce sont deux grandeurs différentes**, mesurées par un seul et même nombre
agrégé. Le constat est vérifiable ligne à ligne ; il ne repose sur aucune
interprétation.

### 5.3 Ce que chaque emploi vaut, examiné séparément

Les deux emplois sont défectueux, **mais pas du même défaut**, et il faut les
juger séparément.

#### 5.3.1 Emploi 2 — un défaut logique, établi dans sa forme négative

Le raisonnement qui suit **ne suppose aucune attente**. Il est purement
d'inclusion.

Sous `-n`, établi par le constat Acte A, le service est **strictement
séquentiel** : `main()` n'accepte la connexion suivante qu'après retour de la
session en cours. La durée d'une invocation `vclient` se décompose donc ainsi :

```
durée_invocation  =  attente éventuelle avant session  +  durée_session
```

L'occupation — la part pendant laquelle Boilerack **détient** la liaison et en
exclut un autre client — est au plus la `durée_session`. D'où, sans hypothèse
aucune sur la valeur du premier terme :

```
occupation  ≤  durée_invocation
```

> **La durée totale d'invocation peut donc MAJORER l'occupation. Elle ne peut
> pas, sur cette seule base, la MINORER.**

**Conclusion, et elle est négative.** L'inférence *« une lecture unique coûte
2 669 à 4 029 ms, donc `rafale_max ≥ 2,669 s` par construction »* **n'est pas
soutenue par la mesure invoquée** : elle utilise une majoration comme si c'était
une minoration. **La minoration tombe.**

> **Ce que ce résultat n'affirme pas.** Il n'affirme **pas** que l'occupation soit
> inférieure à 2,669 s, ni qu'une attente existe, ni que la coexistence soit
> possible. Il affirme seulement que **la certitude d'échec de la branche A n'est
> pas établie par cette mesure**. Les deux termes de la décomposition ci-dessus
> sont inconnus, et leur égalité éventuelle l'est aussi.

#### 5.3.2 Emploi 1 — un défaut distinct : la qualification de la borne

`C1` exige une **borne supérieure déterministe** du coût propre de la sonde —
§8.5 a explicitement retiré le quantile de `C1` pour cette raison. La question
n'est donc pas *« 4,029 est-il grand ou petit »*, mais *« 4,029 est-il une borne
supérieure déterministe sur la bonne population »*.

**Deux effets s'opposent, et aucun n'est établi.**

| Sens | Mécanisme | Statut |
|---|---|---|
| **potentiellement conservateur** | si la mesure contient de l'attente, l'employer comme coût propre **surestime** ce coût et **réduit** le seuil | l'attente non nulle **n'est pas établie** (§4.5) |
| **potentiellement anti-conservateur** | `4,029` est un **maximum empirique** d'un petit jeu de mesures, sur une population **non qualifiée** comme celle des sondes du superviseur, prises **entre deux cycles du superviseur** pour écarter sa contention, et C5 §9 déclare lui-même n'arrêter **aucun budget de production** | un maximum empirique peut **sous-estimer** la vraie borne supérieure |

> **Sur la population, un élément de contexte et sa provenance exacte.** La
> commande qu'exécute la sonde du superviseur est `getTempKist` — fait établi par
> le constat Acte A, qui l'a lue dans la configuration du superviseur. Sa
> **définition déployée** — `addr 0802`, `len 2`, `unit UT`, `protocmd getaddr`,
> protocole `P300` — ne vient **pas** du constat Acte A, qui laissait ce point
> **non établi** : elle est portée par **`w4-arbitrage-activation-debug.md`**. Rien
> n'établit pour autant que le coût d'une telle lecture soit celui que C5 §9 a
> mesuré : la comparaison n'a pas été faite, et ce document ne la fait pas.

> **Précision de lecture sur « par défaut ».** §8.5 qualifie de « par défaut » le
> **`seuil_C1`** — la valeur `0,971 s` — et **non** `4,029 s`, qui y est nommée
> `borne_publique_C5`. Confondre les deux reviendrait à prêter à §8.5 une réserve
> sur la borne qu'il ne formule pas.

> **Solde : `INDÉTERMINÉ`.** L'emploi 1 ne peut pas être qualifié de
> « conservateur », ni d'anti-conservateur. Son défaut est **d'un autre ordre que
> celui de l'emploi 2** : ce n'est pas une inférence invalide, c'est une
> **qualification non établie** — une valeur employée comme borne déterministe sans
> que sa nature de borne, ni sa population, ne soient démontrées.

> **Ce constat n'appelle ici ni valeur nouvelle, ni campagne de mesure.** Il
> qualifie un défaut ; il ne le corrige pas.

### 5.4 Ce qui est établi, ce qui reste hypothèse

**Établi :**

- le double emploi existe et porte sur deux grandeurs distinctes (§5.2) ;
- **emploi 2** : la minoration `rafale_max ≥ 2,669 s` n'est pas soutenue par la
  mesure invoquée — résultat **purement logique**, indépendant de toute
  hypothèse sur l'attente (§5.3.1) ;
- **emploi 1** : la qualification de `4,029 s` comme borne supérieure déterministe
  sur la population des sondes n'est pas établie, et le sens de l'écart est
  **indéterminé** (§5.3.2) ;
- sous `-n`, `occupation ≤ durée_invocation`.

**Non établi, et non établissable par ce lot :**

- l'existence, la valeur ou la nullité de l'attente dans la mesure C5 §9 ;
- la décomposition de l'intervalle 2 669 – 4 029 ms. **Aucune source du dépôt ne la
  porte** ;
- le coût propre d'une sonde du superviseur, sur sa population ;
- le délai marginal réellement ajouté par Boilerack ;
- le régime `U-1`, qui reste **`INDÉTERMINÉ`** — branche C.

### 5.5 Le couplage avec la condition de résolution

Fait arithmétique, à porter parce qu'il change la portée de tout amendement :

```
r  <  seuil_C1 / 2
```

La condition de résolution — condition **2** de `T0 GO` — est une **fonction du
seuil**. Toute re-dérivation du seuil s'y propage mécaniquement. Un amendement de
`C1` ne toucherait donc pas une condition de `T0 GO`, mais **deux**.

> **Le sens de ce déplacement est INDÉTERMINÉ, et doit le rester.** Si un seuil
> révisé était **supérieur**, la résolution exigée se **relâcherait** ; s'il était
> **inférieur**, elle se **durcirait**. Aucune valeur révisée n'étant calculable
> (§5.4), **aucun sens ne peut être présumé** — et le défaut de l'emploi 1
> (§5.3.2) rend un durcissement tout aussi concevable qu'un relâchement.

> **Aucune valeur n'est proposée ici.** Poser un seuil sans la décomposition
> manquante reviendrait à remplacer une constante non justifiée par une autre —
> exactement ce que §8.5 reproche à la V1 et à la V2 de W4-F1.

---

## 6. Voie A — conserver la configuration, corriger la modélisation

### 6.1 Ce qu'elle propose

Remplacer, dans l'inégalité, la grandeur de l'emploi 2 par celle que l'invariant
du §3.7 désigne réellement : le **délai marginal** ajouté par Boilerack à une
sonde du superviseur.

**Forme candidate**, énoncée comme **objet d'étude** et **non comme contrat** :

```
coût_sonde_sans_Boilerack  +  délai_marginal_Boilerack  ≤  budget_superviseur
```

Elle préserve l'invariant du §3.7 point par point : somme bornée par le budget,
population restreinte aux sondes, garantie de nature déterministe. Le `max` du
§3.5 se transpose au premier terme et y conserve son sens unilatéral.

### 6.2 Le modèle à deux variables, `R` et `O`

La forme candidate n'est pas exploitable tant qu'une confusion de vocabulaire
subsiste. Le corpus emploie une seule grandeur là où il en faut deux.

| Symbole | Grandeur | Rôle légitime |
|---|---|---|
| **`R`** | **durée totale d'invocation** — temps mural, de l'appel au résultat | ordonnancement : c'est la bonne variable pour le chaînage des cycles et le seuil de réalimentation |
| **`O`** | **occupation** — durée pendant laquelle un client détient la liaison et en exclut les autres | contention : c'est la grandeur que `C1` doit borner |

Relation établie, et seule établie : **`O ≤ R`**. Leur différence est inconnue ;
leur égalité éventuelle aussi.

> **`R` reste légitime, et ne doit pas être remplacé globalement.** Là où le
> corpus raisonne en temps mural — typiquement le seuil de réalimentation
> `R ≥ 30/7 ≈ 4,286 s` de `w4f1-confirmation-window.md` §6.2, qui décrit le
> chaînage d'un ordonnanceur — `R` **est la bonne variable**. Le défaut n'apparaît
> que là où `R` est employé **comme si** c'était `O`.

### 6.3 Ce qu'il faudrait pour rendre un futur critère calculable

Quatre éléments, **aucun disponible aujourd'hui** :

1. une **borne supérieure déterministe** de `coût_sonde_sans_Boilerack`, établie
   sur la **population réelle des sondes du superviseur** — ce que §5.3.2 montre
   absent ;
2. `délai_marginal_Boilerack`, c'est-à-dire `O`, avec sa **cumulation éventuelle
   sur une rafale** ;
3. le **régime `U-1`** : une composition additive n'a de sens que sous un régime
   `ADDITIF` **établi** ;
4. le **modèle à deux variables** du §6.2, appliqué aux endroits du corpus où il
   change quelque chose.

> **Aucune de ces quatre grandeurs n'est mesurable aujourd'hui**, et ce document
> ne prétend pas le contraire.

### 6.4 Portée et limites de la voie A

| Point | État |
|---|---|
| les données existantes suffisent-elles à **établir le défaut de l'emploi 2** ? | **oui** — §5.3.1 est purement logique, sans mesure nouvelle |
| à **qualifier le défaut de l'emploi 1** ? | **oui**, comme défaut de qualification ; **non** pour en trancher le sens |
| à **calculer un seuil révisé** ? | **non** — §6.3 |
| une preuve documentaire est-elle possible ? | **oui pour les défauts** ; **non pour toute valeur** |
| une mesure nouvelle serait-elle nécessaire ? | **oui, plus tard** — §6.3 |
| l'invariant serait-il préservé ? | **oui** — §3.7 point par point |

> **Limite honnête de la voie A.** Elle ne débloque rien à elle seule. Elle
> supprime une **certitude d'échec** ; elle ne crée pas une **possibilité
> établie**. Elle **déplace** la condition 2 dans un sens **indéterminé** (§5.5),
> et laisse entières les conditions 1, 3, 4 et 5 de `T0 GO`.

### 6.5 Le périmètre d'un amendement éventuel n'est pas établi

**Ce point corrige une erreur de cadrage, et il faut le dire nettement.** Il
serait tentant de borner un futur amendement au seul emploi 2 du §8.5. **Ce
périmètre serait trop étroit.**

La même identification entre `R` et `O` intervient ailleurs dans W4-F1 :

- **§6.2**, où les colonnes **« Occupation »** et **« Rafale max »** sont dérivées
  du **coût par lecture**, c'est-à-dire de `R` ;
- **§8.2.1**, où la **branche A** fonde son `STOP` sur la même arithmétique ;
- et potentiellement toute autre expression dépendant de `R` qu'il faudrait
  distinguer de celles dépendant réellement de `O`.

> **Conclusion de périmètre.** Tout amendement éventuel devrait **d'abord établir
> son périmètre exact dans W4-F1** — notamment §6.2 et §8.2.1 branche A — afin de
> séparer les usages **légitimes** de `R` comme temps mural des usages où la
> grandeur pertinente devrait être `O`.
>
> **Ce lot ne rédige aucun amendement normatif et n'en fixe pas le périmètre.**

---

## 7. Voie B — conserver `C1`, changer la configuration

**Ce que le corpus nomme.** `w4f1-confirmation-window.md` §7.2 nomme deux classes,
et deux seulement : **« instrumentation, ou échelonnement de l'ordonnanceur »**,
qualifiées de « lot à instruire ».

| Option | Portée par le corpus ? | Ce qu'elle change | Pourquoi elle pourrait aider |
|---|---|---|---|
| **échelonnement de l'ordonnanceur Boilerack** | **oui** — §7.2 | le profil temporel des lectures de Boilerack | réduit l'occupation **cumulée** vue par une sonde ; ne réduit pas celle d'**une** lecture |
| **instrumentation** | **oui** — §7.2 | ajoute des sources de mesure | ne change **aucune** durée ; agit sur la **calculabilité**, non sur la satisfaisabilité |
| déphasage de sonde, changement de cadence, sérialisation différente | **non portés** | — | **hors corpus actuel** |

> **Sur l'instrumentation — deux périmètres à ne pas confondre.**
> `w4f1a-vcontrold-concurrency.md` §10 la juge **« non justifiée »**, mais cette
> conclusion porte sur son emploi pour **caractériser `U-1`** : *« elle mesurerait
> des durées sans répondre à la question posée »*. Pour la **calculabilité de
> `C1`**, `w4f1-confirmation-window.md` §7.2 la cite au contraire comme classe
> possible. Les deux énoncés ne se contredisent pas : ils ne portent pas sur le
> même objet.

> **Sur le déphasage et la cadence — le motif exact.** Ils sont écartés parce
> qu'ils sont **hors du corpus actuel** : §7.2 ne nomme que l'instrumentation et
> l'échelonnement, et aucune pièce ne porte ces classes. `w4f-write-sovereignty.md`
> §11.1 intervient en **garde secondaire** — il réserve la **neutralisation** du
> dispositif historique à une autorisation postérieure à l'audit de W4-F3 — mais
> il ne s'énonce pas comme une interdiction explicite de tout changement de
> cadence.

**Analyse de l'option principale — échelonnement.**

| | |
|---|---|
| ce qu'elle change | le profil temporel des lectures, dans le **code de Boilerack seul** |
| coût / complexité | modification de runtime : **un lot de code**, avec audit |
| besoin de terrain | **non** pour l'écrire ; **oui** pour en constater l'effet |
| impact pont / superviseur | **nul par construction** |
| réversibilité | **bonne** — Boilerack seul |
| nouveau risque | allongement de la fenêtre de fraîcheur ; interaction avec `C3`, qui interdit de réussir par inaction |

> **Deux dépendances, et elles sont cumulatives.** L'échelonnement agit sur
> l'occupation **cumulée**. Or §6.5 de `w4f1-confirmation-window.md` établit que,
> **sous la formule actuelle**, la transaction **unitaire** dominerait déjà le
> seuil. La voie B n'a donc de sens **qu'après clarification de la voie A** — pour
> savoir sur quelle grandeur elle agit — et, pour être **opératoire**, elle
> suppose en outre un **régime établi**.

---

## 8. Voie C — remplacer `C1` si le régime est `NON ADDITIF`

**Pourquoi elle dépend d'un régime établi.** `w4f1a-vcontrold-concurrency.md` §3
classe **V-3** — « contrat de remplacement de `C1` absent » — comme **opératoire
seulement si le régime est établi `NON ADDITIF`**. La branche B du §8.2.1 exige ce
remplacement « avant `T1` », et il **exige un nouvel audit**.

**Ce qui deviendrait invalide.** §8.5 le dit : *« `C1` n'a de sens que sous le
régime additif. Si T0-B rend `NON ADDITIF` ou `INDÉTERMINÉ`, … `C1` n'est alors ni
satisfaite ni violée, elle est sans objet. »* C'est la **composition additive**
elle-même qui tombe.

**Ce qu'un remplaçant devrait protéger.** Exactement l'invariant du §3.7 —
inchangé, car il ne dépend d'aucun régime. Seule la **forme** changerait.

**Pourquoi un nouvel audit.** Parce qu'un critère est un contrat, et que §8.5
qualifie ce remplacement d'**« amendement documentaire, pas un choix
d'exploitant »**.

> **Cette voie n'est pas activable.** Le régime n'est pas établi. Et
> `w4f1a-vcontrold-concurrency.md` §3 avertit : *« V-2 et V-3 sont mutuellement
> exclusifs… Construire l'un avant de savoir lequel, c'est avoir une chance sur
> deux de construire le mauvais. »*
>
> **Éléments de contexte, sans conclusion de régime.** La caractérisation amont a
> rendu **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`** ; §6.3 exige une **preuve
> positive** pour `NON ADDITIF`, qu'aucune source n'apporte ; et le régime demeure
> néanmoins **`INDÉTERMINÉ`**. Ces éléments peuvent **pencher** vers l'hypothèse
> additive **sans l'établir**. Ce document n'en tire **aucune conclusion de
> régime**.

---

## 9. Voie D — réexamen W4-F1 / arbitrage de modèle

**Ce que le contrat exige littéralement.** `w4f-write-sovereignty.md` §10.3.4 ne
nomme le réexamen par W4-F1 — et l'arbitrage humain sur la poursuite du
chantier — qu'**en cas d'échec du critère**. **Cet état n'est pas atteint** :
aucun critère n'a échoué, aucune mesure n'a eu lieu.

**Ce que la gouvernance peut décider.** Un arbitrage sur la poursuite ou la
direction d'un chantier est un **acte de gouvernance** : il appartient à l'humain
et ne requiert aucune habilitation canonique. La décision du §1 en est un.

**Quatre actes à ne pas confondre :**

| Acte | Nature | Ce qu'il exige | État |
|---|---|---|---|
| **arbitrage de gouvernance** | poursuite / suspension / abandon | rien de canonique | **déjà pris** au §1 |
| **cadrage d'amendement** | analyse sans effet normatif — *le présent document* | un audit du cadrage | **en cours** |
| **rédaction d'un amendement normatif** | correction d'un contrat clos, à invariant inchangé | un périmètre établi (§6.5), un lot dédié, **et un nouvel audit** | **non autorisée — arbitrage humain distinct, non rendu** |
| **réouverture de W4-F1** | remise en cause du lot et de ses conclusions | l'échec d'un critère, ou un arbitrage humain explicite | non justifiée |

> **Ce que le présent constat justifie, et ce qu'il ne justifie pas.** Le §5
> établit un défaut logique **fondé** sur l'emploi 2, et un défaut de
> qualification sur l'emploi 1. Cela justifie le **cadrage d'amendement** — ce
> document. Cela ne justifie **pas** une réouverture de W4-F1 : le lot n'est pas
> en cause, deux grandeurs le sont. **Et cela ne décide pas s'il faut rédiger
> l'amendement maintenant** : c'est l'objet du §12.

---

## 10. Comparaison des voies

| Voie | Change contrat ? | Change configuration ? | Terrain requis ? | Données manquantes | Préserve invariant ? | Peut rendre `T0 GO` possible ? | Dépendance préalable | Complexité |
|---|---|---|---|---|---|---|---|---|
| **A** — corriger la modélisation | **oui, par amendement** — forme changée, invariant conservé | non | **non** pour établir les défauts ; **oui** pour toute valeur | les quatre grandeurs du §6.3 | **oui**, §3.7 point par point | **partiellement** : retire la certitude d'échec de la branche A et **déplace** la condition 2 dans un sens **indéterminé** ; ne lève ni la condition 4, ni le régime | périmètre à établir (§6.5) ; régime `ADDITIF` pour être **opératoire** | **faible** en cadrage ; moyenne pour l'amendement et son audit |
| **B** — changer la configuration | non | **oui**, code ou réglage de **Boilerack seul** | **oui** pour constater l'effet | effet réel de l'échelonnement sur `O` | oui — n'affaiblit rien | **non seule** : agit sur l'occupation cumulée, alors que la transaction unitaire domine sous la formule actuelle | **clarification de A**, puis régime établi | moyenne à élevée — lot de code |
| **C** — remplacer `C1` | **oui, remplacement complet** | non | non pour l'écrire | **le régime lui-même** | oui, si le remplaçant vise §3.7 | oui, **mais seulement sous `NON ADDITIF`** | régime établi `NON ADDITIF` — **non disponible** | élevée — nouveau contrat + audit |
| **D** — gouvernance | selon l'acte choisi | non | non | aucune pour l'arbitrage | **oui** — ne touche à rien par soi-même | **non** — elle décide, elle ne débloque pas | aucune pour l'arbitrage | faible |

---

## 11. Réponses aux cinq questions

### Q1 — Une faiblesse de modélisation assez établie pour justifier un
amendement documentaire maintenant ?

**Deux défauts distincts, et une réponse qui ne porte pas sur le même plan.**

- **Emploi 2 : OUI, établie — dans sa forme négative.** L'inférence
  `rafale_max ≥ 2,669 s` n'est pas soutenue par la mesure invoquée (§5.3.1). Le
  résultat est logique et ne suppose aucune attente.
- **Emploi 1 : un défaut distinct**, de **qualification de la borne** — la nature
  de `4,029 s` comme borne supérieure déterministe sur la population des sondes
  n'est pas établie, et l'effet global est **`INDÉTERMINÉ`** (§5.3.2).

> **Ce que cela ne décide pas.** Que ces défauts justifient un **cadrage** est
> acquis — c'est ce document. Qu'ils justifient de **rédiger maintenant** un
> amendement normatif est une **autre question**, réservée à l'humain (§12), et sur
> laquelle pèse la réserve de séquencement de `w4f1a-vcontrold-concurrency.md`
> §13.

### Q2 — Peut-on définir un critère de remplacement plus juste avec les
données déjà acquises ?

**Sa forme conceptuelle, oui. Sa valeur, non. Son périmètre, pas encore.**

La forme du §6.1 est recevable comme **piste** et préserve l'invariant. Mais les
quatre grandeurs du §6.3 manquent, et le **périmètre exact** d'un amendement
reste à instruire dans W4-F1 (§6.5).

### Q3 — Une modification de configuration est-elle nécessaire dans tous les cas ?

**Non — elle n'est ni nécessaire dans tous les cas, ni opportune maintenant.**

Elle est **prématurée** : la voie B dépend logiquement de la clarification de la
voie A — pour savoir sur quelle grandeur elle agit — et, pour être **opératoire**,
d'un **régime établi**. Elle n'est jamais la première action.

### Q4 — La plus petite prochaine action capable de faire progresser réellement
W4-F2 ?

> **Après intégration du présent cadrage : un arbitrage humain sur le MOMENT de
> rédaction de l'amendement normatif — maintenant, ou après établissement du
> régime.**

Ce n'est **pas** « rédiger l'amendement maintenant ». La réserve de séquencement
du §13 de `w4f1a-vcontrold-concurrency.md` et l'exclusion mutuelle V-2 / V-3 font
de ce moment une **question ouverte**, que ce document n'a ni qualité ni matière
pour trancher.

### Q5 — Nature de cette action ?

> **Un arbitrage de gouvernance humain, sans terrain.**

Si l'humain choisit ensuite de faire rédiger l'amendement, **ce lot futur sera
documentaire** — et devra commencer par établir son périmètre (§6.5).

---

## 12. Chemin minimal

**Ce que ce lot établit :**

1. le **défaut logique de l'emploi 2** est établi, dans sa forme négative ;
2. l'**emploi 1** porte un problème **distinct**, de qualification de borne, dont
   l'effet global est **indéterminé** ;
3. la forme candidate `coût_sonde + délai_marginal ≤ budget` est **recevable comme
   piste**, non comme contrat ;
4. elle exige un modèle distinguant **`R`** et **`O`** (§6.2), et son **périmètre
   dans W4-F1 reste à établir** (§6.5) ;
5. **aucun seuil n'est calculable aujourd'hui** ;
6. **aucun amendement normatif n'est autorisé par ce cadrage**.

**L'ordre de la suite :**

| # | Étape | Nature | État |
|---|---|---|---|
| 1 | intégrer le présent cadrage après audit | documentaire | proposé |
| 2 | **arbitrage humain** : rédiger maintenant l'amendement normatif, ou attendre l'établissement du régime | **gouvernance** | **non rendu** |
| 3 | si « rédiger maintenant » : ouvrir un lot d'amendement distinct, commençant par son périmètre (§6.5) | documentaire | conditionnel |
| 4 | sinon : **aucun amendement à ce stade** | — | conditionnel |

**Les termes de l'arbitrage 2, exposés sans être tranchés :**

- **pour rédiger maintenant** — le défaut de l'emploi 2 est établi et ne dépend
  d'aucun régime ; le travail est documentaire et sans coût de production ; et il
  conditionne toute suite, y compris la voie B ;
- **pour attendre** — `w4f1a-vcontrold-concurrency.md` §13 réserve l'ouverture de
  cette question à un régime `ADDITIF`, et §3 avertit que V-2 et V-3 sont
  mutuellement exclusifs : rédiger la correction avant de connaître le régime peut
  revenir à construire le mauvais verrou.

> **Ce document ne choisit pas.** Il s'arrête **avant** cet arbitrage, qui
> appartient à l'humain.

> **Ce que ce chemin ne prétend pas.** Il ne dit pas que `T0 GO` deviendra
> atteignable. Il dit quel est le prochain acte qui **coûte zéro en production**
> et dont tous les autres dépendent.

---

## 13. Ce que ce document ne fait pas

Il ne modifie aucun contrat · il ne crée aucun critère et ne propose aucune valeur
de seuil · il ne tranche pas la question de modélisation, il l'instruit · il
n'ouvre aucun lot, il en propose un · il ne rouvre pas W4-F1 · il ne modifie aucun
statut d'hypothèse, ni le régime, ni `U-1`, ni `I1` · il n'autorise ni terrain, ni
`debug`, ni Acte B, ni `T0` / `T1` / `T2` · il ne touche ni au code, ni au runtime,
ni à une configuration · **précondition 9 / §11.2 demeure `NON DONNÉE`** · le pont
historique demeure l'unique écrivain réel de production et la surface
transactionnelle demeure sans autorité, `false`.
