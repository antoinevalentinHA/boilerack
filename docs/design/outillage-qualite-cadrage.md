# Cadrage — outillage qualité post-readiness

> **Version 2**, après audit. Quatre corrections, dont une **contradiction
> assumée d'un finding** : la mesure à 79 occurrences **ne dépend pas de
> `--preview`, et cela a été vérifié** (§3.1). **Aucune mesure porteuse
> — `B1`, `B2`, `C1`, `C2` — n'est modifiée.**
>
> **Version 1.** Audit et cadrage des deux pas d'outillage laissés en suspens par
> `finitions-post-readiness.md` : **linter** et **`mypy`**. L'impact réel est
> **mesuré**, non estimé. **Rien n'est configuré, rien n'est corrigé, le dépôt
> n'est pas modifié.**

---

## 1. Objet et frontières

`finitions-post-readiness.md` §5.3 avait retenu trois pas, dont deux restaient
non exécutés : **B**, brancher un linter à 100 caractères en excluant
`_legacy/primitives.py` ; **C**, brancher `mypy`, dont il déclarait l'ampleur
*« non évaluable sans l'exécuter »*.

**Ce document l'évalue.** Il ne décide rien, ne configure rien, ne corrige rien.

Il **ne rouvre aucun lot clos**, et en particulier aucun lot `W4`. `W4-F2`
demeure clos `NON QUALIFIABLE` ; `W4-F3` demeure **inadmissible** ; la
précondition d'autorisation humaine demeure **`NON DONNÉE`**.

---

## 2. Méthode et point de mesure

| | |
|---|---|
| `main` | `977a794903264af77dab7d1bea817a0a796f3e07` — arbre propre |
| Environnement de mesure | **venv jetable, hors dépôt**, détruit après mesure |
| Outils | **`ruff` 0.16.4**, **`mypy` 2.3.1** |
| Environnement système | **inchangé** — `ruff` et `mypy` y restent absents, vérifié après coup |
| Dépôt | **aucune configuration ajoutée** ; tous les réglages passés en ligne de commande |

> **Deux précautions de mesure, apprises à leurs dépens.**
>
> **La première porte sur le comptage.** La sortie d'un linter mêle les
> occurrences et les lignes de résumé — *« Found N errors »*, *« [*] N
> fixable »*. Les compter ensemble **gonfle le total**. Toutes les valeurs de ce
> document ne comptent que les lignes de la forme `chemin:ligne:colonne: CODE`.
>
> **La seconde porte sur l'isolement.** Lancer `ruff` avec `--isolated` lui fait
> **ignorer `pyproject.toml`**, donc `requires-python = ">=3.11"`. Sous ce
> régime, il signalait **7 `F821`** sur `ExceptionGroup` et `BaseExceptionGroup`,
> en suggérant lui-même de déclarer la version cible. **Ces sept occurrences sont
> des artefacts** : lu normalement, `ruff` ne les rapporte plus — *« All checks
> passed »*. Toutes les mesures ci-dessous sont prises **sans** `--isolated`.
>
> **Correction V2 — la V1 ajoutait qu'`--isolated` activerait « tout le
> catalogue ». C'est faux.** Le dépôt ne déclarant aucune section `[tool.ruff]`,
> `--isolated` ne change **rien** à la sélection : les familles de règles
> rapportées sont **identiques** avec et sans — `BLE`, `F`, `I`, `PLR`, `RUF`,
> `TRY`, `UP`. La seule différence est bien la perte de `requires-python`, et
> avec elle les sept `F821`.

---

## 3. Volet 1 — le linter

### 3.1 État mesuré

`_legacy/primitives.py` exclu, limite de ligne **100** :

| Jeu de règles | `src` | `tests` |
|---|---|---|
| **`E4,E7,E9,F`** — jeu minimal classique | **1** | **17** |
| **`E4,E7,E9,F` + `E501`** | **2** | **38** |
| **sélection intégrée de `ruff` 0.16.4**, sans aucune section `[tool.ruff]` | **79** | **148** |

> **L'écart entre la deuxième et la troisième ligne est le fait marquant.** Ce
> que « brancher un linter » coûte ne dépend pas de l'outil : **il dépend
> entièrement du jeu de règles retenu.** Avec un jeu minimal, l'impact est de
> **2 occurrences** dans `src`. Avec ce que `ruff` 0.16.4 applique **de
> lui-même**, il est de **79**.

> **Qualification exacte de cette troisième ligne, précisée en V2.** Elle mesure
> ce que rapporte `ruff` **0.16.4** lorsqu'aucune section `[tool.ruff]` n'existe.
> Les familles alors actives — `BLE`, `F`, `I`, `PLR`, `RUF`, `TRY`, `UP` —
> **débordent largement** le `E4,E7,E9,F` historique. **Ce chiffre est donc lié à
> cette version de l'outil** et n'a pas vocation à être reporté tel quel sur une
> autre : c'est une raison de plus de **déclarer explicitement** le jeu retenu
> plutôt que de s'en remettre à celui de l'outil.

> **Contradiction assumée d'un finding d'audit.** Il a été avancé que ce chiffre
> serait lié au mode `--preview`. **Vérification faite, ce n'est pas le cas** :
> `ruff check` rapporte **79 occurrences avec `--preview` comme sans**, et
> `--show-settings` indique `linter.preview = disabled`. Le mode `preview` change
> seulement l'**affichage** — il imprime le nom des règles, `type-check-without-
> type-error`, là où le mode normal imprime leur code, `TRY004`. **La correction
> demandée n'a donc pas été appliquée telle quelle** : la qualification exacte
> est celle de l'encadré précédent.

**Longueur de ligne seule**, selon la limite :

| Cible | limite 100 | limite 88 |
|---|---|---|
| `src` *(hors `_legacy`)* | **1** | **32** |
| `tests` | **21** | **194** |

La limite **100** retenue par le cadrage précédent est confirmée comme le choix
le moins coûteux : **une seule ligne** dans `src`.

### 3.2 Les deux occurrences de `src`, nommées

| Occurrence | Nature | Vérification |
|---|---|---|
| `src/boilerack/core/engine.py:45` — `F401`, `datetime.datetime` importé non utilisé | **auto-corrigible** | le mot `datetime` n'apparaît **qu'une fois** dans le fichier, à l'import lui-même : il est réellement inutilisé, et le retirer ne touche aucune annotation |
| `src/boilerack/adapters/process_runner.py:93` — `E501`, **103** caractères | réenroulement | c'est une signature de constructeur ; la couper ne change aucun comportement |

Sur l'ensemble `src` + `tests` en jeu minimal + `E501@100` — **40 occurrences** —
**12 sont corrigibles automatiquement**.

### 3.3 L'exclusion de `_legacy/primitives.py` est **nécessaire**, et mesurée

Analysé seul, en jeu minimal + `E501@100`, ce fichier produit **5 occurrences** :
quatre `F541` — *f-string sans aucun champ* — et une `E501` de 108 caractères.

> **Ce sont exactement les défauts que le module ordonne de ne pas corriger.** Sa
> propre docstring : *« Le code de la première section est copié LITTÉRALEMENT, y
> compris ses défauts et ses effets de bord … Ne rien "améliorer" ici. »*
> **Sans exclusion, le linter demanderait de violer un contrat.** L'exclusion
> n'est donc pas un confort : c'est une condition de compatibilité.

### 3.4 Changements minimaux, et impact

| Élément | Ce qu'il faudrait |
|---|---|
| `pyproject.toml` | une section `[tool.ruff]` : `line-length = 100`, le jeu de règles retenu, et l'exclusion de `_legacy/primitives.py` |
| Extra `dev` | ajouter `ruff` — **une dépendance, sans dépendance transitive** |
| `ci.yml` | une étape `ruff check` avant les tests |
| Code | **2 occurrences** dans `src`, dont **1 auto-corrigible** ; **38** dans `tests` si `tests` est inclus dans le périmètre |

---

## 4. Volet 2 — `mypy`

### 4.1 État mesuré

Sur `src/boilerack`, `_legacy` exclu, `--python-version 3.11` — la version
plancher que la CI teste :

| Réglage | Erreurs | Fichiers touchés | Fichiers analysés |
|---|---|---|---|
| **par défaut** | **6** | **3** | 41 |
| **`--strict`** | **22** | **7** | 41 |

> **C'est l'information que le cadrage précédent déclarait non évaluable, et elle
> est nettement plus favorable qu'on ne pouvait le craindre.** Six erreurs en
> réglage par défaut sur quarante et un modules, pour un code qui n'a jamais été
> vérifié : le paquet est déjà largement cohérent.

**Répartition en `--strict`**, par code d'erreur :

| Code | Nombre |
|---|---|
| `no-any-return` | 6 |
| `no-untyped-def` | 5 |
| `type-arg` | 3 |
| `arg-type`, `assignment`, `attr-defined`, `call-overload`, `exit-return`, `index`, `return`, `unused-ignore` | 1 chacun |

### 4.2 Les six erreurs du réglage par défaut

Elles se concentrent sur **trois fichiers** :

| Fichier | Erreurs |
|---|---|
| `core/engine.py` | 1 — `arg-type` sur un gestionnaire de message |
| `adapters/mqtt_paho.py` | 3 — `assignment`, `call-overload`, `index` |
| `lifecycle.py` | 2 — `exit-return`, `return` |

### 4.3 Un `# type: ignore` mal codé, découvert au passage

Le dépôt porte **trois** `# type: ignore`, tous avec un code entre crochets.
**L'un d'eux ne désigne pas la bonne erreur** :

`src/boilerack/adapters/mqtt_paho.py:112` porte `# type: ignore[arg-type]`, et
`mypy` répond deux choses cohérentes entre elles :

- en réglage par défaut — *« Error code `call-overload` not covered by
  `type: ignore[arg-type]` comment »* : l'erreur réelle n'est pas celle
  déclarée, donc **l'ignore ne couvre rien** ;
- en `--strict` — *« Unused `type: ignore` comment »* `[unused-ignore]`.

> **Le code annonce un dialecte qu'il ne parle pas tout à fait.** Ce n'est pas un
> défaut de comportement — les tests passent — mais une annotation qui ne fait
> pas ce qu'elle prétend, et que personne ne pouvait détecter sans lancer
> l'outil.

### 4.4 Les cinq `no-untyped-def`

| Emplacement | Ce qui manque |
|---|---|
| `config.py:197` | annotation de retour **et** de paramètre |
| `core/engine.py:452` | annotation d'un ou plusieurs paramètres |
| `lifecycle.py:428` | annotation de retour |
| `lifecycle.py:457` | annotation de retour et de paramètres |

Les cinq erreurs portent sur **quatre fonctions**. Les **trois** sans annotation
de **retour** recensées par `finitions-post-readiness.md` §5.1 — `config.py:197`,
`lifecycle.py:428`, `lifecycle.py:457` — s'y retrouvent toutes ; **une seule
fonction s'y ajoute**, `core/engine.py:452`, dont ce sont uniquement les
**paramètres** qui manquent. Deux des quatre cumulent les deux manques, d'où cinq
erreurs pour quatre fonctions.

### 4.5 `_legacy` n'a **pas** besoin d'être exclu de `mypy`

Analysé seul : **`Success: no issues found in 2 source files`**.

> **La symétrie avec le linter n'existe pas, et il faut le dire.** L'exclusion de
> `_legacy` est **nécessaire pour `ruff`** — cinq occurrences, portant sur des
> défauts que le module interdit de corriger — et **inutile pour `mypy`**, qui
> n'y trouve rien. Reprendre l'exclusion des deux côtés serait une symétrie de
> confort, non une nécessité mesurée.

### 4.6 Les tests, hors périmètre

**La mesure brute est trompeuse, et la V1 la reportait sans la qualifier.**

| Mesure | Erreurs | dont `import-not-found` |
|---|---|---|
| **brute** — paquet non installé dans l'environnement de mesure | **274** | **236**, soit **86 %** |
| **chemin résolu** — paquet installé en éditable | **198** | **39** |

Et les **39** restants sont **tous le même** : le module **`pytest`**, absent de
l'environnement de mesure. Les installer ferait encore baisser le total.

> **Ce qu'il faut en retenir.** Le chiffre de 274 mesurait pour l'essentiel une
> **carence d'environnement**, non l'état du code. Le nombre pertinent est
> **198**, et il descendrait encore avec `pytest` résolu.

> **Typer la suite de tests reste un chantier d'un autre ordre**, sans commune
> mesure avec les 6 à 22 erreurs du paquet. Ce document **ne le cadre pas**, et
> recommande de ne pas l'attacher au même pas.

### 4.7 Changements minimaux, et impact

| Élément | Ce qu'il faudrait |
|---|---|
| `pyproject.toml` | une section `[tool.mypy]` : `python_version`, périmètre `src/boilerack`, et le niveau retenu — défaut ou `strict` |
| Extra `dev` | ajouter `mypy`, qui tire **`mypy_extensions`**, **`pathspec`** et **`typing_extensions`** |
| `ci.yml` | une étape `mypy` |
| Code | **6** corrections en réglage par défaut, **22** en `--strict` — dont **1** consistant à corriger un `type: ignore` déjà présent |

---

## 5. Conflits avec les contrats et les zones gelées

Recherche menée sur l'ensemble du corpus.

| Point | Constat |
|---|---|
| **`_legacy/primitives.py`** | **seule zone opposable.** Interdiction explicite de retouche ; le linter doit l'exclure (§3.3), `mypy` n'en a pas besoin (§4.5) — **et sur ce dernier point ce cadrage diverge d'un document intégré**, voir ci-dessous |
| **`c11-presence-recovery.md`** | mentionne *« CI, lint, typage, couverture »* dans son énumération de **ce qu'il ne traite pas**. C'est une **déclaration de périmètre**, non une interdiction |
| **Autres contrats** | aucun n'impose de forme de code que le jeu minimal contrarierait. Les deux occurrences de `src` — un import mort et une ligne longue — ne portent aucune règle contractuelle |
| **Lots clos** | aucun n'est touché ; ce cadrage n'en rouvre aucun |

> **Divergence explicite avec `finitions-post-readiness.md` §5.3.** Ce document,
> intégré et clos, énonce : *« **Toute règle de lint ou de types doit donc
> l'exclure** … C'est vrai des pas **B** et **C**. »* Il plaçait donc l'exclusion
> de `_legacy` comme nécessaire **des deux côtés**.
>
> **La mesure le contredit pour `mypy`** : analysé seul, `_legacy` donne
> *« Success: no issues found »*. L'exclusion y serait **sans objet**, faute
> d'occurrence à exclure.
>
> **Cette divergence est signalée, non tranchée.** Le §5.3 raisonnait **avant**
> toute mesure, et sa prudence était fondée : il ne pouvait pas savoir. Ce
> cadrage ne le corrige pas — **les lots clos ne se retouchent pas** — et se
> borne à constater que, sur ce point précis, la mesure est plus précise que la
> précaution. **Exclure `_legacy` de `mypy` resterait sans inconvénient**, mais ce
> serait une précaution, non une nécessité.

> **Une réserve, sur les jeux de règles étendus.** Ce que `ruff` 0.16.4 applique
> sans section `[tool.ruff]` comporte des règles d'opinion — `TRY004` réclame
> `TypeError` là où le code lève autre chose, `BLE001` proscrit les
> `except Exception` — qui
> **entreraient en discussion avec des choix délibérés** des contrats. Un jeu
> étendu ne devrait donc pas être adopté sans confronter chaque famille de règles
> au corpus. **Ce travail n'est pas fait ici**, et c'est une raison de plus de
> commencer par un jeu minimal.

---

## 6. Synthèse — quatre pas séparables

| Pas | Contenu | Impact code mesuré |
|---|---|---|
| **B1** | `ruff` en jeu **minimal** + `E501@100`, `_legacy` exclu, **sur `src` seul** | **2** occurrences, dont 1 auto-corrigible |
| **B2** | étendre le périmètre du linter à `tests` | **38** occurrences |
| **C1** | `mypy` en réglage **par défaut** sur `src/boilerack` | **6** erreurs, 3 fichiers |
| **C2** | passer `mypy` en **`--strict`** | **22** erreurs, 7 fichiers |

**B1 et C1 sont les deux pas les moins coûteux**, et ils sont indépendants l'un
de l'autre. **B2 et C2 sont des extensions**, chacune décidable séparément. Typer
la suite de tests n'est **pas** dans cette liste (§4.6).

> **Aucun de ces quatre pas ne demande de refactor.** Le plus lourd, `C2`, porte
> sur 22 points nommés, dont la majorité sont des annotations manquantes.

**Réserve de mesure.** Tout a été mesuré sous **Python 3.14** en local, avec
`--python-version 3.11` pour `mypy` et `requires-python` lu par `ruff`. La CI
exécute **3.11, 3.12 et 3.13**. Les résultats devraient s'y retrouver, mais
**cela n'a pas été constaté** : seule une exécution réelle en CI le confirmerait.

---

## 7. Ce que ce document ne fait pas

Il ne configure ni `ruff`, ni `mypy` · il n'ajoute aucune dépendance · il ne
touche ni à `pyproject.toml`, ni à `ci.yml`, ni à aucun fichier source · il ne
corrige aucune des occurrences relevées, y compris le `type: ignore` mal codé du
§4.3 · il ne choisit aucun jeu de règles ni aucun niveau de `mypy` · il ne cadre
pas le typage de la suite de tests · il ne rouvre aucun lot clos, et **aucun lot
`W4`** · il n'installe rien dans l'environnement système, et l'environnement de
mesure a été détruit.

**`W4-F2` demeure clos `NON QUALIFIABLE`** ; `W4-F3` demeure **inadmissible** ;
la précondition d'autorisation humaine demeure **`NON DONNÉE`** ; le pont
historique demeure l'unique écrivain réel ; la surface transactionnelle demeure
sans autorité, `false`.

---

## 8. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Cadrage initial, avec mesure réelle de `ruff` 0.16.4 et `mypy` 2.3.1 sur `main` `977a7949` |
| **2** | Audit. §2 : retrait de l'affirmation fausse selon laquelle `--isolated` activerait tout le catalogue — les familles sont identiques avec et sans. §3.1 et §5 : qualification exacte de la troisième ligne — « sélection intégrée de `ruff` 0.16.4, sans section `[tool.ruff]` » — et **contradiction assumée** du finding l'attribuant à `--preview`, vérification à l'appui. §4.4 : cinq erreurs pour **quatre** fonctions, une seule s'ajoutant aux trois déjà recensées. §4.6 : mesure brute et mesure à chemin résolu distinguées — **274 dont 236 `import-not-found`**, contre **198 dont 39**, tous sur `pytest`. §5 : divergence avec `finitions-post-readiness.md` §5.3 rendue explicite. **Mesures porteuses `B1`, `B2`, `C1`, `C2` inchangées** |
