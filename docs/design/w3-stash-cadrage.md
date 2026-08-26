# Cadrage — le sort du `stash` W3

> **Version 2**, après audit. Deux corrections d'attribution et de renvoi, sans
> effet sur les constats : les **deux barrières** du §4.3 sont l'absence
> d'adaptateur d'écriture réel et l'absence de `Profile` réel, levées
> respectivement par **`W4-B`** et **`W4-D`** — `W4-E1` n'en lève aucune, il
> compose sous autorité ; et le renvoi du §4.2 désigne l'**erratum `W2` §19.3.2**,
> non un §7. **La conclusion est inchangée.**
>
> **Version 1.** Lot documentaire, **hors `W4-F2`**. Il identifie le contenu du
> `stash@{0}`, le compare à `main`, vérifie son lien avec l'erratum `W2` §19.3.2
> et propose son sort minimal. **Le stash n'est ni appliqué, ni dépilé, ni
> modifié, ni supprimé par ce lot.** Aucun code, aucun hôte, aucun runtime,
> aucune mutation.

---

## 1. Objet et frontières

Le lot de clôture de `W4-F2` a signalé, en §8, une réserve **non bloquante et
hors périmètre** : un `stash` subsistait comme unique porteur d'un état. Ce
document l'instruit, et rien d'autre.

Il **ne modifie aucun code**, n'amende aucun contrat, ne rouvre aucun arbitrage
clos, et **n'exécute pas** le sort qu'il propose. La suppression d'un `stash`
étant irréversible en pratique, elle relève d'une décision humaine, prise sur
une preuve — que ce document produit.

---

## 2. Identité de l'objet

| | |
|---|---|
| Référence | `stash@{0}` |
| Objet | **`daf3ed1e4f088e01767275fc89cf01a4587c2988`** |
| Auteur | `Antoine <antoine.valentin@gmail.com>` |
| Date | **2026-08-19 16:31:25 +0200** |
| Message | *« On `feat/w3-transaction-runtime-wiring`: W3 gelé (`af3be310`) — mis à l'abri pour l'erratum W2 §19.3.2 »* |

**C'est un `stash` à trois parents**, ce qui n'est pas le cas ordinaire :

| Parent | Objet | Rôle |
|---|---|---|
| 1 | `3290e71ec382bbe58e02b62650e6aca06cb6f5fb` | **base** — merge de la PR #36, `W2` concurrence et cycle de vie, 2026-08-19 15:08 |
| 2 | `217ae18b335b8ba67debce6ebe19f24342ce2667` | index au moment du `stash` — **vide par rapport à la base** |
| 3 | `ee469e8a2c6b34b90b710371b4f37c6421469906` | **fichiers non suivis**, présents parce que le `stash` a été pris avec `-u` |

> **Le troisième parent change le décompte, et il faut le dire d'emblée.** Le
> `stash` ne porte pas **trois** fichiers, comme le laissait croire
> `git stash show --stat`, mais **sept** : trois modifications de fichiers
> suivis, et **quatre fichiers alors non suivis**.

**La base est ancêtre de `main`**, avec **56 commits** d'écart. Le `stash` date
du 2026-08-19 ; `main` est au 2026-08-26.

---

## 3. Les sept fichiers, comparés à `main`

Comparaison d'empreintes de blob. Aucun fichier n'a été extrait ni écrit.

### 3.1 Les trois fichiers suivis

| Fichier | base | `stash` | `main` | Constat |
|---|---|---|---|---|
| `src/boilerack/runtime.py` | `39e97d9c` | `fcd01045` | `a22645b8` | les trois diffèrent |
| `tests/adapters/test_mqtt_paho.py` | `af178745` | `5a688061` | **`5a688061`** | **`stash` = `main`** — intégré verbatim |
| `tests/test_lifecycle.py` | `e6ab0784` | `5ae63540` | `fe4a6128` | les trois diffèrent |

### 3.2 Les quatre fichiers alors non suivis

| Fichier | `stash` | `main` | Constat |
|---|---|---|---|
| `src/boilerack/command_intake.py` | `cd094b26` | **`cd094b26`** | **identique à `main`** |
| `src/boilerack/transaction_wiring.py` | `9af77923` | `2ba115d6` | diffère |
| `tests/test_transaction_wiring.py` | `fd27d687` | `bb874f10` | diffère |
| `tests/wiring_support.py` | `2e555f83` | `9b249417` | diffère |

**Les sept fichiers existent tous dans `main`.** Aucun n'a disparu.

---

## 4. Ce que porte le `stash` et qui n'est pas dans `main`

La question n'est pas « les fichiers diffèrent-ils » — ils diffèrent, 56 commits
plus tard — mais **« le `stash` porte-t-il quelque chose que `main` n'a pas »**.

Méthode : pour chaque fichier, l'ensemble des lignes non vides du `stash`,
normalisées, moins celui de `main`.

| Fichier | Lignes uniques absentes de `main` |
|---|---|
| `tests/adapters/test_mqtt_paho.py` | **0** sur 532 |
| `src/boilerack/command_intake.py` | **0** sur 85 |
| `tests/wiring_support.py` | **0** sur 182 |
| `tests/test_lifecycle.py` | 7 sur 1 145 |
| `src/boilerack/transaction_wiring.py` | 8 sur 168 |
| `src/boilerack/runtime.py` | 12 sur 276 |
| `tests/test_transaction_wiring.py` | 27 sur 502 |

**Les 54 lignes concernées ont été lues une à une.** Elles se répartissent en
**trois catégories, et trois seulement**.

### 4.1 Résidu de refonte — aucun contenu normatif

Ligne d'`import`, nom d'auxiliaire de test, signature d'un faux constructeur
`def faux(config, stop, *, clock=None)` que `main` a fait évoluer en y ajoutant
le paramètre transactionnel. **Rien qui porte une règle.**

### 4.2 Commentaires que l'erratum a précisément retirés

Le `stash` porte, dans `runtime.py` :

> *« Le contrat place ici un quatrième contrôle d'arrêt ; sa propre réserve m-E
> constate qu'il ne peut changer aucun comportement … Il n'est donc pas
> matérialisé en appel mort : c'est le COMPORTEMENT normatif qui est
> implémenté. »*

`main` porte, au même endroit :

> *« W2 §19.3.2 : une commande admise dans cette itération MUST être exécutée
> dans cette MÊME itération … W2 §13.3 énonce par ailleurs qu'**aucune
> consultation d'arrêt supplémentaire n'est requise** entre l'admission et
> `process_next()` : le contrat prescrit le comportement, et lui seul. »*

**C'est exactement la substitution que prescrit l'erratum `W2` §19.3.2**,
consigné dans le **bloc de versions en tête** de
`w2-transaction-concurrency-lifecycle.md` : *« §19.3.2 imposait au propriétaire de
**consulter l'arrêt** entre l'admission et `process_next()`. Cette obligation
était **sans effet observable** … Elle est **retirée**. La règle de comportement,
elle, est **conservée intégralement**. »* Le §6 le vérifie clause par clause.

### 4.3 Descriptions d'une barrière que `W4` a remplacée

Le `stash` décrit une barrière **de type** : *« la voie reste fermée en
production tant que W4 n'a pas livré ces deux dépendances »*, *« ce n'est pas un
interrupteur qu'on pourrait laisser ouvert par mégarde, mais l'absence de deux
dépendances obligatoires »*.

Le `stash` nommait lui-même ces deux dépendances : *« `build_transaction_surface`
exige un `VClient` — donc `read` **ET** `write` — et un `Profile` ; or
`VClientCliReader` n'implémente que `read`, et aucun `Profile` réel n'existe dans
ce dépôt »*.

**Les deux ont été levées depuis**, chacune par son lot :

| Barrière | Ce qui manquait | Levée par |
|---|---|---|
| **n° 1** | un **adaptateur d'écriture réel** — aucun `VClient` satisfaisant `write` | **`W4-B`** — `c603549`, *production vclient write adapter* : `VClientCli` étend `VClientCliReader` et implémente `write` |
| **n° 2** | un **`Profile` réel** — le seul constructeur était un double de test | **`W4-D`** — `f0d0076`, *W4-D production profile* |

> **`W4-E1` ne lève aucune de ces deux barrières, et il ne faut pas le lui
> attribuer.** `71b543d`, *compose transaction surface under configuration
> authority*, fait autre chose : les deux dépendances étant désormais
> disponibles, il **compose** la surface et pose l'**autorité d'activation** qui
> décide si cette composition est autorisée.

La barrière a donc changé de nature : elle n'est plus **de type** — l'absence de
deux dépendances — mais **de configuration** : `TransactionSurfaceConfig`,
`enabled: bool = False`, défaut fermé. Et `src/boilerack/lifecycle.py`
**construit** effectivement la surface sous cette autorité.

> **La description du `stash` n'est pas perdue : elle est devenue fausse.**

---

## 5. Les deux tests du `stash` absents de `main`

C'est le seul point qui méritait une vérification nominale. Le `stash` porte
**50** fonctions de test dans `tests/test_transaction_wiring.py`, `main` en porte
**56**. Deux noms du `stash` n'existent pas dans `main` :

| Test du `stash` | Statut | Pourquoi |
|---|---|---|
| `test_la_surface_n_est_construite_nulle_part_en_production` | **obsolète par décision intégrée** | l'assertion est devenue **fausse** : `lifecycle.py` construit la surface sous l'autorité `enabled`. `main` porte l'invariant survivant, plus étroit et toujours vrai : **`test_la_racine_de_composition_ne_construit_aucune_voie`** |
| `test_aucun_profil_reel_dans_le_code_de_production` | **obsolète par décision intégrée** | l'assertion est devenue **fausse** : `src/boilerack/core/production_profile.py` existe, livré par `W4-D`. `main` porte l'invariant adapté : **`test_les_constructeurs_de_profil_sont_une_liste_fermee`** |

> **Aucun des deux n'a été perdu par inadvertance.** L'un et l'autre affirmaient
> un fait que des lots ultérieurs, audités et mergés, ont délibérément changé —
> et `main` porte, pour chacun, un invariant de remplacement.

---

## 6. Le lien avec l'erratum `W2` §19.3.2 — vérifié

L'erratum est consigné dans l'en-tête de
`w2-transaction-concurrency-lifecycle.md` : l'obligation de **consulter l'arrêt**
entre l'admission et `process_next()` était *« sans effet observable … et donc
invérifiable. Elle est **retirée**. La règle de comportement, elle, est
**conservée intégralement** »*.

| Ce que l'erratum prescrit | État dans `main` |
|---|---|
| retirer l'obligation de consultation | **fait** — le commentaire de `runtime.py` ne parle plus d'un « quatrième contrôle d'arrêt » |
| conserver la règle de comportement | **fait** — `_pomper()` appelle `executer_un()` inconditionnellement |
| conserver §19.3.1 | **fait** — `if not self._stop.is_set(): admettre_un()` |

> **Le motif du `stash` est consommé.** Ce pour quoi il avait été mis à l'abri a
> été traité dans `main`, et dans une formulation **postérieure** à la sienne.

---

## 7. Verdict, par catégorie

| Catégorie | Contenu concerné |
|---|---|
| **déjà intégré à l'identique** | `tests/adapters/test_mqtt_paho.py`, `src/boilerack/command_intake.py`, `tests/wiring_support.py` |
| **intégré puis dépassé** | `runtime.py`, `test_lifecycle.py`, `transaction_wiring.py`, `test_transaction_wiring.py` — le comportement y est, sous une forme ultérieure |
| **obsolète** | les commentaires du §4.2, les descriptions du §4.3, les deux tests du §5 |
| **encore pertinent** | **aucun** |
| **perdu** | **aucun** |

> **Le `stash` est intégralement subsumé par `main`.** Aucune règle, aucun test,
> aucun comportement qu'il porte n'est absent du dépôt. Ce qu'il contient en
> propre est soit du résidu de refonte, soit du texte que des décisions
> intégrées ont rendu faux.

---

## 8. Sort proposé — le minimal et le propre

> **Supprimer le `stash`, après la preuve produite ci-dessus.**

C'est la seule des trois options qui laisse le dépôt dans un état exact.

| Option | Évaluation |
|---|---|
| **intégrer** | **à écarter** — il n'y a rien à intégrer. Appliquer le `stash` réintroduirait des commentaires que l'erratum a retirés et deux tests devenus faux : la CI les rejetterait, et à raison |
| **reformuler** | **à écarter** — reformuler quoi ? Le §4 montre qu'aucun contenu propre ne subsiste. Une reformulation fabriquerait une dette là où il n'y en a plus |
| **supprimer** | **retenu** — l'objet est sans objet, et sa présence fait croire à un fil pendant |

### 8.1 Ce qui rend la suppression sûre

La preuve est **versionnée dans ce document** : les sept fichiers, leurs
empreintes, les trois catégories de lignes propres, les deux tests et leurs
remplaçants, la vérification de l'erratum. **Rien de ce que le `stash` porte
n'aura besoin d'être retrouvé.**

### 8.2 Ce qu'il faut savoir avant de le faire

- `git stash drop` rend l'objet **inatteignable**, et le ramassage de mémoire
  finira par le détruire. L'opération est **irréversible en pratique**.
- Une récupération reste possible **brièvement**, par l'objet
  `daf3ed1e4f088e01767275fc89cf01a4587c2988`, que ce document consigne — mais
  **seulement tant que la mémoire n'a pas été ramassée**. Ce n'est pas une
  garantie, et il ne faut pas la présenter comme telle.
- **Aucune sauvegarde par `tag` ou branche n'est proposée** : elle publierait,
  dans un dépôt **public** et de façon permanente, des brouillons dépassés de
  fichiers dont `main` porte la version aboutie. Le remède serait pire.

### 8.3 Ce que ce lot ne fait pas

Il **n'exécute pas** la suppression. Elle demande un acte humain distinct, sur ce
constat, et hors de ce document.

---

## 9. Ce que ce document ne fait pas

Il ne modifie aucun code · il n'applique, ne dépile, ne déplace ni ne supprime le
`stash` · il n'amende aucun contrat · il ne rouvre ni `W4-F2`, ni l'erratum `W2`
· il ne rétablit aucun test retiré · il n'émet aucune conclusion par défaut · il
n'ouvre ni `T0`, ni Acte B, ni `T1` / `T2` · il n'autorise aucun terrain, aucune
mutation, aucun `debug`.

**`W4-F2` demeure clos `NON QUALIFIABLE`** ; `W4-F3` demeure **inadmissible** ;
Précondition 9 / §11.2 demeure **`NON DONNÉE`**. Ce lot leur est **étranger**.

---

## 10. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Cadrage initial du sort du `stash` W3 |
| **2** | Audit. §4.3 : attribution des deux barrières corrigée — adaptateur d'écriture réel levé par **`W4-B`**, `Profile` réel levé par **`W4-D`** ; `W4-E1` rendu à son objet, la composition sous autorité. §4.2 : renvoi « §7 » remplacé par le renvoi exact à l'erratum `W2` §19.3.2 et à son bloc de versions. **Conclusion inchangée** |
