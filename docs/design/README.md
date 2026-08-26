# Corpus de conception — index

Ce répertoire porte **42 documents**. Ils ne sont pas de même nature, et ils ne se
lisent pas dans l'ordre alphabétique. Cet index dit ce qu'ils sont, par où entrer,
et ce qui pourrait induire en erreur.

> **État du projet.** Boilerack est **en construction**. Rien n'est publiable ni
> utilisable à ce stade, et rien n'a été éprouvé contre un broker, un `vcontrold`
> ou une chaudière réels. Voir le [`README`](../../README.md) racine.

---

## Les quatre familles

| Préfixe | Nature | Nombre |
|---|---|---|
| `c*` | **contrats de construction** — ce que le code doit faire, arrêté avant de l'écrire | 16 |
| `w0`–`w3` | **lots de travail** sur la surface transactionnelle | 4 |
| `w4*` | **famille W4** — écriture réelle, souveraineté, coexistence avec le pont historique | 19 |
| — | **hors série** — provenance, readiness, finitions | 3 |

---

## Par où entrer

**Pour comprendre ce que fait le programme**, dans cet ordre :

| # | Document | Pourquoi ici |
|---|---|---|
| 1 | [`c3-transactional-core.md`](c3-transactional-core.md) | le cœur transactionnel et le profil déclaratif |
| 2 | [`c7-mqtt-read-contract.md`](c7-mqtt-read-contract.md) | la surface de lecture MQTT |
| 3 | [`c8-composition-root.md`](c8-composition-root.md) | où tout est câblé, et nulle part ailleurs |
| 4 | [`c9-process-lifecycle.md`](c9-process-lifecycle.md) | cycle de vie et arrêt sur signal |
| 5 | [`c10-user-interface.md`](c10-user-interface.md) | configuration et point d'entrée installé |

**Pour comprendre l'état du projet et pourquoi il s'arrête là** :

| # | Document | Pourquoi ici |
|---|---|---|
| 1 | [`w4f-write-sovereignty.md`](w4f-write-sovereignty.md) | le cadrage d'ensemble de W4-F |
| 2 | [`w4f1-confirmation-window.md`](w4f1-confirmation-window.md) | le critère `C1` et ses conditions |
| 3 | [`w4f2-cloture.md`](w4f2-cloture.md) | **l'état terminal**, et ce qui reste ouvert |
| 4 | [`readiness-boilerack.md`](readiness-boilerack.md) | l'état du dépôt lui-même |

**Pour savoir d'où vient le code caractérisé** :
[`provenance.md`](provenance.md).

---

## Glossaire minimal

| Signe | Ce qu'il désigne |
|---|---|
| **`C`** *(majuscule)* | un **critère** normatif — `C1`, `C2`, `C3` — porté par [`w4f1-confirmation-window.md`](w4f1-confirmation-window.md) |
| **`c*`** *(minuscule, nom de fichier)* | un **contrat de construction** — `c5`, `c7`, etc. |
| **`W`** | un **lot de travail** — `W0` à `W4`, avec leurs sous-lots `W4-A`, `W4-F1`, `W4-F2`… |
| **`T0`** | l'étape de **préparation terrain** de `W4-F2` : caractériser les sources et décider de la calculabilité. `T0-A`, `T0-C`, `T0-D` en sont les actes ; **`T0` n'est pas ouvert** |
| **`T1` / `T2`** | les phases de **terrain** qui suivraient `T0`. **Aucune n'est atteinte** |
| **`H`** | une **hypothèse d'installation** — `H1`, `H2`, `H3`, `H6` — dont dépend le régime de concurrence |
| **`U`** | une **inconnue** — `U-1`, `U-2`, `U-3`, `U-7` — chacune avec son statut de preuve |
| **`G.1`** | un **régime d'engagement** : lecture bornée sur l'installation, sans mutation |

---

## Trois pièges de nommage

Ils sont constatés, non supposés. Les connaître évite trois contresens.

### 1. `C1` n'est pas un fichier `c1-*.md`

**Aucun fichier `c1-*` n'existe.** `C1` est un **critère** — la fenêtre de
confirmation — porté par [`w4f1-confirmation-window.md`](w4f1-confirmation-window.md)
et amendé par [`w4f2-c1-amendement.md`](w4f2-c1-amendement.md). Il ne faut pas le
confondre avec les **contrats** `c5`, `c7` et les autres, qui sont d'un tout autre
ordre.

### 2. Deux documents `w4a-*` sans rapport entre eux

| Fichier | Objet |
|---|---|
| [`w4a-vclient-write-adapter.md`](w4a-vclient-write-adapter.md) | le **contrat W4-A** de l'adaptateur d'écriture |
| [`w4a-acte-a-constat.md`](w4a-acte-a-constat.md) | le constat de l'**Acte A**, une observation terrain en lecture |

Même préfixe, objets distincts.

### 3. `w3-stash-cadrage.md` n'est pas un contrat `W3`

**Il n'existe pas de contrat de lot `W3` autonome.** Ce fichier traite du sort
d'un `stash`. Le câblage dit « W3 » est couvert par
[`w1-mqtt-transaction-surface.md`](w1-mqtt-transaction-surface.md),
[`w2-transaction-concurrency-lifecycle.md`](w2-transaction-concurrency-lifecycle.md),
[`w4a-vclient-write-adapter.md`](w4a-vclient-write-adapter.md) et
[`w4e-composition-activation.md`](w4e-composition-activation.md).

---

## État terminal de `W4-F2`

> **`W4-F2` est clos `NON QUALIFIABLE` au plafond de preuve actuel.**

Ce n'est ni un échec, ni un abandon : c'est la **sortie contractuelle** prévue.
En conséquence, et sans changement :

- **`W4-F3` demeure inadmissible** ;
- la **précondition d'autorisation humaine demeure `NON DONNÉE`** ;
- le **pont historique demeure l'unique écrivain réel** de production ;
- la **surface transactionnelle demeure sans autorité**, `false` par défaut.

Le détail, les dix inconnues laissées ouvertes et le chemin de reprise figurent
dans [`w4f2-cloture.md`](w4f2-cloture.md).

---

## Inventaire complet

### Contrats de construction

| Document | Objet |
|---|---|
| [`c2-infrastructure.md`](c2-infrastructure.md) | infrastructure de test et doubles |
| [`c3-transactional-core.md`](c3-transactional-core.md) | cœur transactionnel générique et profil déclaratif |
| [`c4-real-adapters.md`](c4-real-adapters.md) | adaptateurs réels MQTT et frontière de processus |
| [`c5-vclient-contract.md`](c5-vclient-contract.md) | contrat réel de `vclient` — observations de lecture |
| [`c6-vclient-read-adapter.md`](c6-vclient-read-adapter.md) | lecteur `vclient` en lecture seule |
| [`c7-mqtt-read-contract.md`](c7-mqtt-read-contract.md) | contrat MQTT de la surface de lecture |
| [`c7c1-read-surface-primitives.md`](c7c1-read-surface-primitives.md) | primitives de la surface de lecture |
| [`c7c2-read-surface-state.md`](c7c2-read-surface-state.md) | déclaration, état de lecture, cycles et instantané |
| [`c7c3a-mqtt-presence.md`](c7c3a-mqtt-presence.md) | testament MQTT, présence et instantané de démarrage |
| [`c7c3b-read-publisher.md`](c7c3b-read-publisher.md) | lectures dues, publications, cadences et battement |
| [`c8-composition-root.md`](c8-composition-root.md) | composition root et boucle d'exécution |
| [`c9-process-lifecycle.md`](c9-process-lifecycle.md) | cycle de vie du processus et arrêt sur signal |
| [`c10-user-interface.md`](c10-user-interface.md) | configuration et point d'entrée installé |
| [`c11-presence-recovery.md`](c11-presence-recovery.md) | reprise de présence après reconnexion MQTT |
| [`c12-service-contract.md`](c12-service-contract.md) | contrat d'exploitation et de service |
| [`c13-installation-contract.md`](c13-installation-contract.md) | contrat d'installation et de déploiement |

### Lots `W0` à `W3`

| Document | Objet |
|---|---|
| [`w0-mqtt-subscription-recovery.md`](w0-mqtt-subscription-recovery.md) | persistance fonctionnelle des souscriptions MQTT |
| [`w1-mqtt-transaction-surface.md`](w1-mqtt-transaction-surface.md) | contrat de la surface transactionnelle MQTT |
| [`w2-transaction-concurrency-lifecycle.md`](w2-transaction-concurrency-lifecycle.md) | concurrence et cycle de vie de la voie transactionnelle |
| [`w3-stash-cadrage.md`](w3-stash-cadrage.md) | sort du `stash` W3 — **pas un contrat de lot** |

### Famille `W4`

**Écriture et adaptateur**

| Document | Objet |
|---|---|
| [`w4a-vclient-write-adapter.md`](w4a-vclient-write-adapter.md) | contrat de l'adaptateur d'écriture `vclient` |
| [`w4c-write-capture-protocol.md`](w4c-write-capture-protocol.md) | protocole de capture de l'écriture |
| [`w4e-composition-activation.md`](w4e-composition-activation.md) | composition, autorité d'activation, namespace |

**Terrain et activation de `debug`**

| Document | Objet |
|---|---|
| [`w4-cadrage-activation-debug.md`](w4-cadrage-activation-debug.md) | cadrage de l'activation de `debug` |
| [`w4-arbitrage-activation-debug.md`](w4-arbitrage-activation-debug.md) | arbitrage correspondant |
| [`w4a-acte-a-constat.md`](w4a-acte-a-constat.md) | **Acte A** — constat terrain en lecture |

**Souveraineté d'écriture — `W4-F`**

| Document | Objet |
|---|---|
| [`w4f-write-sovereignty.md`](w4f-write-sovereignty.md) | cadrage d'ensemble et décomposition |
| [`w4f1-confirmation-window.md`](w4f1-confirmation-window.md) | **fenêtre de confirmation, critère `C1`** |
| [`w4f1a-vcontrold-concurrency.md`](w4f1a-vcontrold-concurrency.md) | régime de concurrence de `vcontrold` — cadrage |
| [`w4f1a-upstream-characterization.md`](w4f1a-upstream-characterization.md) | caractérisation amont de `U-1` — rapport |

**Finalisation — `W4-F2`**, dans l'ordre où elle s'est déroulée

| # | Document | Objet |
|---|---|---|
| 1 | [`w4f2-ouverture.md`](w4f2-ouverture.md) | ouverture du chantier |
| 2 | [`w4f2-c1-reexamen.md`](w4f2-c1-reexamen.md) | réexamen de la barrière `C1` |
| 3 | [`w4f2-c1-amendement.md`](w4f2-c1-amendement.md) | **amendement normatif de `C1`** |
| 4 | [`w4f2-regime-instruction.md`](w4f2-regime-instruction.md) | établissement du régime |
| 5 | [`w4f2-a5-extraction.md`](w4f2-a5-extraction.md) | extraction `A5` — le jeu de commandes du pont |
| 6 | [`w4f2-vito-xml-instruction.md`](w4f2-vito-xml-instruction.md) | résolution statique des treize commandes |
| 7 | [`w4f2-g1-constat.md`](w4f2-g1-constat.md) | constat `G.1` — empreinte du fichier déployé |
| 8 | [`w4f2-cadrage-cloture.md`](w4f2-cadrage-cloture.md) | le plus court chemin de clôture |
| 9 | [`w4f2-cloture.md`](w4f2-cloture.md) | **clôture — `NON QUALIFIABLE`** |

### Hors série

| Document | Objet |
|---|---|
| [`provenance.md`](provenance.md) | provenance du code caractérisé |
| [`readiness-boilerack.md`](readiness-boilerack.md) | readiness du dépôt — passe finale |
| [`finitions-post-readiness.md`](finitions-post-readiness.md) | cadrage des finitions qui en découlent |

---

## Convention de lecture

Chaque document porte, en tête, un **bloc de versions** décrivant ses révisions
successives. Ces révisions appartiennent à la chaîne de rédaction et d'audit
**antérieure à l'intégration** : seule la version finalement intégrée figure dans
l'historique du dépôt.

Les documents clos **ne sont pas retouchés**. Une correction ultérieure prend la
forme d'un nouveau document, ou d'un amendement explicite qui se nomme comme tel.
