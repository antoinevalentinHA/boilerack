# Constat `G.2` — campagne d'écriture bornée, exécutée et close

> **Version 1.** Clôture documentaire du chantier `G.2`. Il consigne une
> campagne d'écriture **bornée et réversible**, exécutée sur l'installation
> après **autorisation humaine explicite et distincte**, et définie par
> `w4f-g2-ecriture-bornee.md`.
>
> **Deux écritures, aucune autre.** Aucun code, aucun runtime, aucune
> modification de comportement n'accompagne ce document : il **constate**, il
> ne prescrit rien.
>
> Il suit la forme établie par le précédent `G.1` — `w4f2-g1-constat.md` — :
> un acte borné, **proposé par un document, non autorisé par lui**, puis
> autorisé par une décision humaine séparée, exécuté sans élargissement, et
> consigné par un document distinct.

---

## 0. Convention de citation

Les citations sont reproduites **mot pour mot**. Aucune constante de site ne
figure ici : les unités sont désignées `<unité-boilerack>`, `<unité-pont>`,
`<timer-guard>`, conformément au §9.1 du protocole.

---

## 1. Verdict

> **`G.2 TERRAIN VALIDÉ`**

La campagne s'est exécutée le **2026-08-28**, de `22:05Z` à `22:27Z`, sur le
build `f27bfce95baee45bd11a23006897e44deaac1fa8`. Elle a produit le verdict
**`G.2 CONFIRMÉ`** au sens du §16, terme 10, du protocole, puis a été **validée
en audit terrain**.

**Aucun critère `AB`, aucun critère `FA` n'a été déclenché.**

## 2. Ce que le verdict établit — et rien de plus

`G.2` établit que **Boilerack a émis deux écritures réelles**, confirmées par
relecture stricte, dispositif historique arrêté, et *one-writer* établi **au
sens borné du §8.1** — clients du démon, sur la fenêtre observée.

Le protocole avait fixé cette borne d'avance, au §16 :

> *« Ce que `G.2` établira, et rien de plus : que Boilerack a émis une écriture
> réelle, confirmée par relecture stricte, dispositif historique arrêté et
> *one-writer* établi **au sens borné du §8.1** — clients du démon, sur douze
> secondes. Il **n'établira pas** que la coexistence est qualifiée, ni que `C1`
> est satisfaite ou calculable, ni que Boilerack peut écrire **en coexistence**,
> ni de façon soutenue, ni que `H2`, `H6` **(b)** ou `U-3` seraient closes. »*

**Cette borne est tenue.** Le terrain n'a rien établi au-delà.

### 2.1 Ce qui demeure OUVERT

| Objet | État |
|---|---|
| **`C1`** | **OUVERTE.** Non satisfaite, et toujours **non calculable** — `borne_sonde` (`U-2`) n'a toujours aucune valeur admissible |
| **Coexistence** | **NON QUALIFIÉE.** La campagne s'est déroulée dispositif historique **arrêté**. Elle ne dit rien d'une écriture en coexistence |
| **`H2`** | **OUVERTE.** La preuve *one-writer* est bornée aux clients du démon ; un participant agissant sur l'IPC System V y échapperait |
| **`H6` (b)** | **OUVERTE**, pour le même motif |
| **`U-3`** | **OUVERTE.** Le compte des captures prouve les écritures **de Boilerack**, non le total tous écrivains confondus |
| **Écriture soutenue** | **NON ÉTABLIE.** Deux écritures espacées ne caractérisent aucun régime soutenu |

## 3. La campagne, telle qu'exécutée

| | Valeur | Établie par |
|---|---|---|
| Initiale `V_brut` | `2.000000 ` *(espace final inclus)* | `EI-10`, deux captures nues concordantes |
| `V_canon` | **2** | dérivation entière **sans perte** — pas d'`AB-9` |
| Cible | **3** = `V_canon + 1` | `3 ≤ 40`, `V_brut ∈ [−13 ; 40]` : admissible au §15 |
| Restaurée | **2** | restauration **pré-décidée** par l'autorisation, §10 cas 2 |

Rôle unique : `heating_curve_shift` / `setNiveauM1`. Actes réservés autorisés :
**1, 2 et 3**. **L'acte réservé 4 est resté interdit, et n'a pas été employé.**

**Cardinalité respectée** : une écriture au temps 10, une au temps 12, **zéro
partout ailleurs**.

Les treize preuves `EI-1..EI-13` ont été établies **dans l'ordre du §9**, sans
allègement. `PR-1` et `PR-2` ont été **redoublées** : le rapport porte comment
l'arrêt a été établi **et comment la reprise l'a été**. Les **cinq** étapes du
§11.2 ont été exécutées et prouvées, dont les **trois faits distincts** `A`,
`B` et `C` de l'étape 3, et l'**étape 5** — cycle nominal du superviseur sans
action corrective.

Les gardes cumulées ont tenu : **`G-a`** prouvée avant le temps 8 et
**reconstatée après le démarrage manuel**, **`G-b`** persistée hors les
temps 8 à 13.

**Instrumentation.** La campagne est la première à produire la preuve n°4 du
§16 — *ligne d'invocation réelle, `stdout` et `stderr` intégralement et
séparément, code retour et durée mesurée* — **automatiquement**, par le puits
de preuve introduit par `g2-sortie-preuve-transport.md`. Six fichiers,
rangs `01` et `02`.

## 4. Artefact terrain gelé

Le rapport et ses pièces sont conservés **hors du dépôt**, et transmis
manuellement à l'auditeur. Le dépôt n'en porte que les empreintes.

| Pièce | SHA-256 |
|---|---|
| `RAPPORT-TERRAIN-G2.md` | `5b92145398e266f71c6dece1920e9c3201c9a4b58b332e4f31e54120cc2612d7` |
| `g2-terrain-20260828.tar.gz` *(bundle, 57 fichiers)* | `dee4a8e1ea6d0433222e445a9aaed722eb3be7a4aa819f7a8ccb313cca1ead2d` |
| `MANIFESTE-SHA256.txt` | `5cf55ec5985f9f750cf777bd0a0d84089fe6e0ea66192b002056d75ea1687648` |

Le bundle contient **56 pièces** portées au manifeste : 2 documents d'analyse,
**6 preuves transport**, et **48 captures de terrain** — dont huit trios
`.out`/`.err`/`.meta` à la forme de `W4-C` §10. Le manifeste a été vérifié sur
le contenu **extrait** : 56/56 conformes.

**Le secret MQTT n'est pas dans l'artefact.** Le fichier d'environnement n'y
figure que par son empreinte.

### 4.1 Les six preuves transport

| Fichier | SHA-256 |
|---|---|
| `01-ecriture.meta` | `a50a08f14f5e9e1cb7c6ec7fbee45e51ddd6f71fa4c0f80e82dfd90a2833ed1e` |
| `01-ecriture.out` | `77ecdb7db66264f3e6ed3777c91f3c62c7a3c639a4decd4e2ce8c4614723ebc8` |
| `01-ecriture.err` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `02-ecriture.meta` | `a3b7c1e76492ee0ae026d92ef320207b2f64f7573ac947e75b6cf84d7974e449` |
| `02-ecriture.out` | `a52cd85aaacdbadcf73da2447d9d89e5c395ec1d115aa33ae41aecd00dbf9d26` |
| `02-ecriture.err` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Les deux `.err` portent la même empreinte parce qu'ils sont **vides** :
`e3b0c442…b855` est le SHA-256 de la chaîne vide. Ils ne sont **jamais**
fusionnés avec `.out` — `W4-A` §18, obligation 5.

## 5. `A-1` — publication MQTT rejetée, distincte de toute écriture

Consigné ici **exactement comme audité**.

Une publication a précédé la première écriture et a été **rejetée en forme** :
`invalid_payload`, `reason_class: permanent`. La charge utile émise portait
**quatre** champs là où le décodeur en exige **six** — `ts` et `expires_at`
manquaient. Erreur de construction de l'opérateur de session ; aucune cause
côté chaudière, transport ou programme.

### 5.1 Une publication rejetée n'est pas une invocation transport

| | Publication MQTT rejetée | Écriture transport réelle |
|---|---|---|
| Objet compté | une **publication** sur le topic de commande | une **invocation** de `vclient` par l'adaptateur d'écriture |
| Où elle s'arrête | validation de **forme**, **en amont du cœur** | atteint le démon et l'Optolink |
| Trace produite | un `ACK` `rejected` | `accepted` puis `applied`, **et** un trio de fichiers |
| Effet sur l'installation | **aucun** | l'état change, et la relecture stricte le confirme |
| Comptée par la cardinalité du §9 | **non** | **oui** |

La cardinalité du §9 porte sur les **invocations**, non sur les publications.
Le décompte de la campagne est donc : **trois publications** — une rejetée,
deux acceptées — pour **deux écritures transport** et **deux écritures sur
l'installation**.

### 5.2 Aucune écriture n'a eu lieu

Quatre éléments, dont trois sont des captures de terrain conservées :

1. **l'atelier de preuve est resté à zéro entrée**, constaté immédiatement après
   le rejet. Le puits dépose sur **toute** invocation, **y compris en échec** —
   un atelier vide est donc la preuve **positive** que l'adaptateur n'a pas été
   appelé ;
2. **l'atelier final ne porte que deux trios**, rangs `01` et `02`, le premier
   créé **près de trois minutes après** le rejet. Aucun trio, aucun fragment de
   trio n'est attribuable à la publication rejetée ;
3. **l'état lu après le rejet valait `2.000000`**, identique à `V_brut` ;
4. **le processus n'a pas bronché** — même `MainPID`, `NRestarts = 0`, vie
   continue au journal.

### 5.3 Republication autorisée humainement, avant l'acte

À la réception du rejet, la session **a interrompu la campagne** et n'a rien
republié de sa propre initiative. Le motif était un **doute de portée** : la
question de savoir si republier après un rejet de forme entrait dans
l'interdiction « aucune seconde tentative » **n'était pas à la session de la
trancher**.

La question a été posée avec les faits — rejet de forme, aucune écriture,
atelier à zéro fichier, valeur inchangée — et **l'humain a autorisé la
republication**. Celle-ci a eu lieu **après** cette autorisation, avec un
`request_id` neuf et une charge utile complète.

### 5.4 Aucune violation de « aucune seconde tentative »

L'interdiction porte sur les **écritures**, et le §12.3 la formule sous la
conduite d'abandon : *« Aucune seconde tentative dans la même fenêtre. »*
Aucun `ABORT` n'a été prononcé, et **aucune écriture n'avait eu lieu** au
moment de la republication. La règle n'a donc pas été enfreinte — et elle n'a
pas été interprétée par la session, mais **soumise à l'humain**.

## 6. Réserves conservées

Les dix réserves du **§19** de `w4f-g2-ecriture-bornee.md` sont **conservées
telles quelles**, à une exception près :

- la réserve **8** — *« `P-1` n'est pas acquise — Boilerack n'est pas
  déployé »* — est **levée par le fait** : le préflight a déployé le build,
  unité **`disabled`** et **`inactive`** hors tests. Les neuf autres demeurent
  intégralement.

Y sont ajoutées, **conservées et non corrigées** :

| | Réserve | Nature |
|---|---|---|
| **`R-2` … `R-6`** | réserves du lot `sortie de preuve`, relevées à l'audit d'implémentation et **délibérément non traitées** | non bloquantes, conservées |
| **`A-1`** | protocole de capture : un nom de fichier réutilisé entre deux publications a **écrasé** la capture de l'`ACK` rejeté. Le texte de cet `ACK` n'existe que dans le transcript de session, et **aucune capture n'a été recréée après coup** | défaut d'outillage, non de programme |
| **`A-2`** | un filtrage de la table des processus **s'auto-correspond**, y compris par les **libellés d'affichage**. Redressé en figeant un instantané analysé hors ligne, avec motif témoin. Même famille que le `pgrep` auto-correspondant de `P-4` | méthode |
| **`A-3`** | un commentaire du fichier de configuration est resté obsolète pendant l'ouverture de l'autorité. **Non corrigé en fenêtre** — pas de polissage sous acte | cosmétique |
| **`A-4`** | la fenêtre muette de `EI-8` a couvert bien plus que les douze secondes exigées. Écart **favorable**, signalé pour exactitude | exactitude |
| **`A-5`** | un **redémarrage machine commandé par le superviseur** est survenu pendant le **préflight**, hors campagne. **Cause non établie** — le journal du boot précédent n'a pas survécu. `G-a` et `G-b` ont tenu à travers lui | **non établie, ouverte** |

**Aucune de ces réserves n'a été corrigée sur les artefacts produits.** Les
fichiers de terrain restent tels que la campagne les a laissés.

## 7. Régime de `G.2` — exécutée, close, non réutilisable

> **Clause.** `G.2` est **exécutée et close**. L'autorisation qui l'a permise
> était **unique, explicite et distincte**, et elle est **consommée**.

Trois conséquences, opposables :

1. **`G.2` ne se rejoue pas.** Le §5.1 du protocole ne lève ses clauses
   **qu'une fois** ; cette fois a eu lieu. Le présent constat ne rouvre rien ;
2. **aucune écriture ultérieure ne peut s'en réclamer** — ni sur le même rôle,
   ni sur un autre, ni « dans les mêmes conditions ». Une nouvelle écriture
   exige une **nouvelle autorisation normative**, appuyée sur un document qui
   la définit, puis une **décision humaine explicite et distincte** ;
3. **le bornage reste opposable, non auto-appliqué** (§13). Rien dans le code
   n'empêche une écriture hors campagne ; c'est la discipline qui l'empêche,
   et ce constat en fait partie.

L'instrumentation est **désarmée** : la variable d'atelier a été retirée du
fichier d'environnement persisté, l'autorité d'écriture est refermée sur le
fichier persisté, et `<unité-boilerack>` est `disabled` et `inactive`. Les
empreintes des fichiers persistés sont **identiques à l'avant-campagne**.

## 8. Ce que ce document ne fait pas

Il **n'amende** aucune clause, **ne lève** aucune interdiction, **n'autorise**
aucun acte, et **ne modifie** aucun comportement. Il ne rouvre ni `C1`, ni la
coexistence, ni `H2`, ni `H6` **(b)**, ni `U-3`. Il ne qualifie pas la surface
d'écriture pour l'exploitation, et n'ouvre aucune voie vers `W4-F3`, qui
demeure **inadmissible**.

Il consigne un acte passé, et le referme.

## 9. Historique de révision

| Version | Objet |
|---|---|
| **1** | Constat initial. Clôture du chantier `G.2` après validation terrain. |
