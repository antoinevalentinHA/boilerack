# Cadrage des finitions post-readiness

> **Version 3**, après réaudit. Le §5.1 exposait une **reconstruction** du
> mécanisme ayant produit le chiffre erroné de la V1. Cette reconstruction est
> **retirée** : seuls les faits établis subsistent. **Rien d'autre ne change.**
>
> **Version 2**, après audit. Une correction de fait : les fonctions annotées en
> retour sont **315 sur 318**, non 318. Les trois fonctions concernées sont
> nommées. Deux formulations sont adoucies.
>
> **Version 1.** Cadrage établi **à partir de `main` seul**. Pour chacune des
> quatre finitions relevées par `readiness-boilerack.md` : l'état exact, le
> traitement minimal, et la distinction entre ce qui est **purement
> documentaire** et ce qui **pourrait toucher au code**. **Rien n'est exécuté.**

---

## 1. Objet et frontières

Ce document **instruit** quatre finitions. Il n'en traite aucune : ni index, ni
`README`, ni outillage, ni branche n'est modifié.

Il **ne rouvre aucun lot clos**, et en particulier **aucun lot `W4`**. Là où il
cite `W4-F2`, c'est pour rappeler un état terminal, jamais pour le discuter.

**`W4-F2` demeure clos `NON QUALIFIABLE`** ; `W4-F3` demeure **inadmissible** ;
Précondition 9 / §11.2 demeure **`NON DONNÉE`**.

---

## 2. Point de mesure

| | |
|---|---|
| `main` | `40763c771f6f84a3ac90085b73728ccd3c97df82` |
| `origin/main` | **identique** · arbre **propre** |
| Documents de conception | **41** |
| Modules source | **43** |
| Branches distantes | **une seule : `main`** |

---

## 3. Finition 1 — index du corpus documentaire

### 3.1 État exact

**41 documents**, répartis en quatre familles :

| Famille | Nombre |
|---|---|
| Contrats `c*` | **16** |
| Lots `w0` à `w3` | **4** |
| Famille `w4` | **19** |
| Hors série — `provenance.md`, `readiness-boilerack.md` | **2** |

**Aucun index n'existe** : ni `docs/README.md`, ni `docs/design/README.md`. Le
`README` racine ne cite **qu'un seul** de ces documents.

### 3.2 Trois pièges de nommage, constatés

Un index n'a pas seulement à lister : il doit désamorcer ce qui induit en erreur.

| Piège | Fait constaté |
|---|---|
| **`C1` n'est pas `c1-*.md`** | **aucun fichier `c1-*` n'existe.** `C1` est un **critère** porté par `w4f1-confirmation-window.md`, à ne pas confondre avec les contrats `c5`, `c7`, etc. — confusion déjà signalée par `w4f2-cadrage-cloture.md` |
| **deux documents `w4a-*` distincts** | `w4a-acte-a-constat.md` et `w4a-vclient-write-adapter.md` — même préfixe, objets sans rapport |
| **`w3-stash-cadrage.md` n'est pas un contrat `W3`** | il traite du sort d'un `stash` ; **il n'existe pas de contrat de lot `W3` autonome**, comme l'établit `readiness-boilerack.md` §4.1 |

### 3.3 Traitement minimal proposé

**Un fichier d'index, et un lien depuis le `README` racine.** Il porterait :

1. les **quatre familles** et ce que chacune est ;
2. un **ordre de lecture** — par où entrer, et dans quel sens ;
3. un **glossaire minimal** : `C`, `W`, `T0`, `H`, `U` ;
4. les **trois pièges** du §3.2 ;
5. l'**état terminal de `W4-F2`**, avec le renvoi vers son lot de clôture.

> **Ce qu'il ne faut surtout pas faire, et il faut le dire pour l'écarter** :
> renommer ou réorganiser les documents. Les renvois croisés sont nombreux et
> internes au corpus, et **les lots clos ne se retouchent pas**. Un index ajoute
> une porte ; il ne redessine pas le bâtiment.

| Nature | **purement documentaire** — un fichier ajouté, un lien ajouté |
|---|---|
| Code touché | **aucun** |
| Contrats touchés | **aucun** |

---

## 4. Finition 2 — l'ambiguïté du `README`

### 4.1 État exact — trois énoncés, tous vrais

| Emplacement | Énoncé |
|---|---|
| Bannière, l. 6-7 | *« **État : en construction. Rien n'est publiable ni utilisable à ce stade.** Aucune prerelease n'a été diffusée. »* |
| §Installation, l. 34 | *« Rien n'a été éprouvé contre un broker, un `vcontrold` ou une chaudière réels. »* |
| §Compatibilité, l. 82 | *« **Vérifié** sur une seule installation : régulation `VScotHO1` (`20CB`), protocole `P300` … »* |

**Aucun des trois n'est faux.** Le troisième décrit ce que la **caractérisation**
a couvert — la chaudière réellement observée par le corpus — et non un essai de
Boilerack. Mais « vérifié », lu vite et à quarante-huit lignes du second énoncé,
peut s'entendre comme « essayé ».

### 4.2 Traitement minimal proposé

**Une incise au §Compatibilité**, précisant ce que « vérifié » qualifie : la
caractérisation de l'installation, non un essai de Boilerack — avec le renvoi
vers l'énoncé de §Installation, qui reste inchangé.

> **Une variante existe, et l'arbitrage revient à l'humain** : remplacer le mot
> « Vérifié » par un terme qui ne peut pas être mal lu. C'est plus radical et
> touche une formulation publique en place. **L'incise est proposée comme
> minimale** ; le remplacement n'est pas exclu.

| Nature | **purement documentaire** — une phrase dans le `README` |
|---|---|
| Code touché | **aucun** |
| Corpus touché | **aucun** — l'incise ne cite aucun lot et n'en rouvre aucun |

---

## 5. Finition 3 — outillage lint et types

C'est la seule des quatre qui demande d'être instruite avant d'être chiffrée.

### 5.1 État exact, mesuré statiquement

| Mesure | Valeur |
|---|---|
| Fonctions dans `src/` | **318** |
| Fonctions **annotées en retour** | **315** — soit **99,1 %** |
| Fonctions **sans** annotation de retour | **3**, nommées ci-dessous |
| Modules portant `from __future__ import annotations` | **40** sur 43 |
| `# type: ignore[…]` présents | **3** |
| **`py.typed`** | **ABSENT** |
| Lignes source > 88 caractères | **36** |
| Lignes source > 100 caractères | **2** |
| Sections `[tool.*]` dans `pyproject.toml` | `hatch.version`, `hatch.build`, `pytest` — **aucun outil de qualité** |
| Extra `dev` | `pytest>=8` **seul** |

**Les trois fonctions sans annotation de retour**, relevées par lecture de
l'arbre syntaxique :

| Fonction | Emplacement |
|---|---|
| `_construire` | `src/boilerack/config.py`, l. 197 |
| `_composer_transaction` | `src/boilerack/lifecycle.py`, l. 428 |
| `fabriquer` | `src/boilerack/lifecycle.py`, l. 457 |

> **Correction, énoncée comme un fait et rien de plus.** La **V1 annonçait
> `318/318`**. Le **comptage par parcours de l'arbre syntaxique donne `315/318`**,
> et **trois fonctions sont sans annotation de retour** — celles nommées
> ci-dessus. Ce qui a produit le chiffre de la V1 **n'est pas reconstitué ici**.

> **Principe général, retenu pour la suite.** Une **égalité de totaux n'établit
> aucune correspondance** : compter des déclarations d'un côté et des marques de
> l'autre ne dit rien de leur appariement. Seul un parcours qui **associe chaque
> fonction à son annotation** y répond. Le principe vaut indépendamment de ce lot
> et **n'est attribué à aucune méthode particulière**.

### 5.2 Deux constats qui orientent le traitement

> **Le code parle déjà le dialecte de `mypy`.** Les trois `# type: ignore` portent
> un **code d'erreur entre crochets** — `[arg-type]`, `[arg-type]`, `[operator]`
> — qui est la syntaxe de `mypy`. Le choix de l'outil est donc **fortement
> suggéré par le code**, sans être imposé : un autre vérificateur resterait
> possible, mais rendrait ces trois annotations inertes ou à réécrire.

> **Le paquet ne se déclare pas typé.** `py.typed` étant absent, **un
> consommateur ne voit aucune de ces 315 annotations**. C'est un écart entre
> l'effort consenti et ce qui en sort du paquet.

### 5.3 Traitement minimal proposé — **trois pas séparables**

| Pas | Contenu | Code touché |
|---|---|---|
| **A** | ajouter **`py.typed`** au paquet, et s'assurer qu'il est bien embarqué dans la distribution | **aucun** — un fichier marqueur, vide ; **ce cadrage ne préjuge pas** de ce que la configuration de construction exige en plus, s'il faut quoi que ce soit |
| **B** | brancher un **linter**, longueur de ligne à **100** : **2 lignes** concernées | **potentiellement 1 ligne** — voir la réserve ci-dessous |
| **C** | brancher **`mypy`** | **ampleur non évaluable sans l'exécuter** |

**Sur le pas B.** À 100 caractères, deux lignes sont hors norme :
`src/boilerack/adapters/process_runner.py:93` et
`src/boilerack/_legacy/primitives.py:139`. À 88, il y en aurait **36** —
l'arbitrage entre les deux seuils appartient à l'humain.

> **Réserve, et elle est contractuelle.** `src/boilerack/_legacy/primitives.py`
> est sous **interdiction explicite de retouche** : *« Ne rien "améliorer" ici :
> toute correction souhaitée est une divergence à traiter en C3, pas une retouche
> silencieuse. »* **Toute règle de lint ou de types doit donc l'exclure**, sous
> peine d'entrer en conflit avec ce que le module prescrit. C'est vrai des pas
> **B** et **C**.

**Sur le pas C.** Brancher `mypy` sur 43 modules fait remonter un état initial
dont le traitement **n'est pas borné d'avance**. Il peut appeler des annotations
supplémentaires, des `Protocol` précisés, ou de nouveaux `# type: ignore`.
**Ce cadrage ne l'évalue pas** : le mesurer exigerait d'installer et d'exécuter
l'outil, ce que ce lot s'interdit.

> **C'est le seul des quatre chantiers susceptible d'entraîner des
> modifications de code**, et il faut le dire sans l'atténuer. Les pas **A** et
> **B** sont séparables et peuvent être menés sans lui.

---

## 6. Finition 4 — branches locales fusionnées

### 6.1 État exact

**Huit branches** en plus de `main`, **toutes fusionnées**, écart **zéro commit**
pour chacune.

| Branche | Sommet | Configuration d'`upstream` |
|---|---|---|
| `docs/w4c-terrain-closure` | `4a4da0a` | pointe vers une distante **supprimée** |
| `docs/w4c-terrain-qualification-erratum` | `4c32c75` | idem |
| `docs/w4e-composition-activation-contract` | `10066a0` | idem |
| `docs/w4f-write-sovereignty-framing` | `0ae9b4d` | idem |
| `feat/w4b-vclient-write-adapter` | `c603549` | idem |
| `feat/w4d-production-profile` | `f0d0076` | idem |
| `feat/w4e2-transaction-composition` | `71b543d` | idem |
| `feat/w3-transaction-runtime-wiring` | `3290e71` | **aucune** |

### 6.2 Traitement minimal proposé

**`git branch -d` sur chacune**, jamais `-D` : la suppression n'est possible que
parce qu'elles sont fusionnées, et `-d` **refuse** de supprimer ce qui ne l'est
pas. C'est la garantie, et elle doit rester le mécanisme.

> **Rien n'est perdu, et c'est vérifiable** : chaque sommet est un commit
> **atteignable depuis `main`**. La suppression ne retire qu'une étiquette
> locale. **Aucun rapport avec la suppression d'un `stash`**, qui rendait un
> objet inatteignable.

| Nature | **purement locale** |
|---|---|
| Code touché | **aucun** |
| Dépôt publié | **aucun effet** — le distant ne porte déjà que `main` |

---

## 7. Synthèse — ce qui touche au code, et ce qui n'y touche pas

| # | Finition | Nature | Peut toucher au code |
|---|---|---|---|
| 1 | index du corpus | documentaire | **non** |
| 2 | ambiguïté du `README` | documentaire | **non** |
| 3-A | `py.typed` | packaging déclaratif | **non** |
| 3-B | linter | outillage | **au plus une ligne**, hors `_legacy` exclu |
| 3-C | `mypy` | outillage | **oui — ampleur non évaluée** |
| 4 | branches locales | hygiène de poste | **non** |

> **Cinq des six pas ne touchent pas au code.** Le sixième — brancher `mypy` — est
> le seul qui puisse en entraîner, et **il est séparable des cinq autres**.

**Aucun des six ne rouvre un lot clos, ne demande de terrain, ni ne modifie un
contrat.** L'unique interaction contractuelle relevée est une **exclusion à
respecter** : `_legacy/primitives.py`, qui interdit sa propre retouche.

---

## 8. Ce que ce document ne fait pas

Il n'écrit aucun index · il ne touche pas au `README` · il n'ajoute ni `py.typed`,
ni linter, ni vérificateur de types · il ne supprime aucune branche · il ne
modifie aucun code, aucun contrat, aucun test · il n'évalue pas l'ampleur du pas
**3-C**, qui exigerait d'exécuter l'outil · il ne rouvre aucun lot clos, et
**aucun lot `W4`** · il n'ouvre ni `T0`, ni `T1` / `T2` · il n'autorise aucun
terrain, aucun runtime, aucune mutation.

**`W4-F2` demeure clos `NON QUALIFIABLE`** ; `W4-F3` demeure **inadmissible** ;
Précondition 9 / §11.2 demeure **`NON DONNÉE`** ; le pont historique demeure
l'unique écrivain réel ; la surface transactionnelle demeure sans autorité,
`false`.

---

## 9. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Cadrage initial des quatre finitions, sur `main` `40763c77` |
| **2** | Audit. §5.1 : les fonctions annotées en retour passent de **318 à 315 sur 318**, soit **99,1 %**, et les trois exceptions sont nommées. §5.2 : reprise du faux 318 corrigée ; `mypy` est dit **fortement suggéré par le code**, non imposé ; le pas **A** ne préjuge plus de ce que la construction exige. **Aucun autre changement de fond** |
| **3** | Réaudit. §5.1 : retrait de la **reconstruction** du mécanisme ayant produit le chiffre de la V1 ; seuls subsistent les faits — la V1 annonçait `318/318`, le comptage par AST donne `315/318`, trois fonctions sont sans annotation de retour. Le principe « une égalité de totaux n'établit aucune correspondance » est conservé comme **principe général**, sans attribution. **Aucun autre changement** |
