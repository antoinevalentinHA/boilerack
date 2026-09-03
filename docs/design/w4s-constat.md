# Constat `W4-S` — campagne minimale de seconde écriture bornée, exécutée et close

> **Version 1.** Clôture documentaire du chantier `W4-S`. Il consigne une
> campagne d'écriture **bornée et réversible**, exécutée sur l'installation
> après **autorisation humaine explicite et distincte**, et définie par
> `w4s-campagne-minimale.md`.
>
> **Deux écritures, aucune autre.** Aucun code, aucun runtime, aucune
> modification de comportement n'accompagne ce document : **il constate, il ne
> prescrit rien**.
>
> Il suit la forme établie par `G.1` — `w4f2-g1-constat.md` — et par `G.2` —
> `w4f-g2-constat.md` : un acte borné, **proposé par un document, non autorisé
> par lui**, puis autorisé par une décision humaine séparée, exécuté sans
> élargissement, et consigné par un document distinct.
>
> **Il n'amende rien**, et en particulier **il ne modifie pas
> `w4s-campagne-minimale.md`, ni son §17.1.**

---

## 0. Convention de citation

Les citations sont reproduites **mot pour mot**. **Aucune constante de site ne
figure ici** : les unités sont désignées `<unité-boilerack>`, `<unité-pont>`,
`<unité-démon>`, `<unité-superviseur>`, `<timer-guard>`.

| Nom court | Document |
|---|---|
| `W4-S` | `w4s-campagne-minimale.md` — le **protocole**, intégré par la PR #100 |
| `G2-P` | `w4f-g2-ecriture-bornee.md` |
| `G2-C` | `w4f-g2-constat.md` |
| `w4f` | `w4f-write-sovereignty.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `W1` | `w1-mqtt-transaction-surface.md` |

---

## 1. Verdict

> # `W4-S HOMOLOGUÉE`

**Deux prononcés distincts, et ils ne se confondent pas.**

| | Prononcé | Par qui | Sur quoi |
|---|---|---|---|
| **`W4-S CONFIRMÉ`** | verdict **de terrain**, au sens du §16 du protocole | **l'exécutant**, en fin de campagne | les treize `EI` établies, l'écriture émise, la relecture strictement égale, la restauration conduite, les cinq étapes achevées, **aucun `AB`, aucun `FA`** |
| **`W4-S HOMOLOGUÉE`** | **homologation** | **audit indépendant**, sur les pièces | la conformité de l'exécution au protocole intégré, vérifiée sur l'artefact gelé |

> **Le premier ne vaut pas le second, et ne l'a jamais valu.** La première
> exécution avait prononcé `W4-S CONFIRMÉ` et n'a **pas** été homologuée — §2.
> **Nul n'homologue ce qu'il a produit.**

---

## 2. Les DEUX exécutions du 2026-09-03 — distinguées par leur fenêtre

> **Le protocole porte un §17.1 intitulé *« Statut de l'exécution du
> 2026-09-03 »*, et les deux exécutions ont eu lieu ce jour-là.** Le présent §
> lève l'ambiguïté **en nommant les fenêtres horaires**. Il **n'amende pas** le
> §17.1, qui vise la **première**.

| Fenêtre `UTC` | Sous | Statut |
|---|---|---|
| **`16:15:15Z` → `16:49:38Z`** | `W4-S` V1, PR #99 | **NON HOMOLOGUÉE** |
| **`18:46:07Z` → `19:14:56Z`** | `W4-S` corrigé, **PR #100** | **HOMOLOGUÉE** |

### 2.1 La première — non homologuée, et le motif

**Aucune des 80 pièces figées ne prouvait `P-UFS`.** Les quatre occurrences
d'état d'activation qu'elles portaient concernaient toutes `<unité-boilerack>`,
servaient **`G-a`**, et étaient **postérieures au temps 1**.

**La cause était structurelle** : `P-UFS` se prend **avant le temps 1**, alors
que l'atelier n'était créé **qu'au temps 1** — il n'existait aucun endroit où
déposer la pièce. **Le correctif intégré par la PR #100 traite cette cause.**

> **La preuve manquante n'a PAS été reconstruite**, ni alors, ni depuis.
> **L'exécution demeure non homologuée**, et ses pièces demeurent au dossier.

### 2.2 La seconde — homologuée

**`P-UFS` est prouvée par une pièce dédiée**, prise à `18:46:07.390622995Z`,
soit **8 min 6 s avant le temps 1** (`18:54:13.073111396Z`), **antériorité
démontrée par la pièce elle-même**. Elle fut la **première et unique** pièce de
l'atelier jusqu'au temps 1, et **l'atelier a été constaté ne contenir qu'elle**
avant tout autre dépôt.

Les **quatre** états d'activation y figurent : `<unité-pont>`, `<unité-démon>` et
`<timer-guard>` **`enabled`** ; `<unité-superviseur>` relevée, **aucune valeur
exigée** — elle est déclenchée par le timer.

---

## 3. Ce que `W4-S` établit — et rien de plus

**Deux choses, et le protocole les avait annoncées d'avance au §2.1.**

### 3.1 La RÉPÉTABILITÉ

**Les quatre `.out` et `.err` des preuves transport sont BYTE À BYTE identiques
à ceux de `G.2`**, publiés au dépôt dans `G2-C` §4.1 depuis le **2026-08-28** :

| Fichier | SHA-256 | `G.2` | `W4-S` |
|---|---|---|---|
| `01-ecriture.out` | `77ecdb7db66264f3e6ed3777c91f3c62c7a3c639a4decd4e2ce8c4614723ebc8` | ✔ | **✔** |
| `01-ecriture.err` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | ✔ | **✔** |
| `02-ecriture.out` | `a52cd85aaacdbadcf73da2447d9d89e5c395ec1d115aa33ae41aecd00dbf9d26` | ✔ | **✔** |
| `02-ecriture.err` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | ✔ | **✔** |

**Seuls les `.meta` diffèrent**, et ils **devaient** différer : ils portent
l'horodatage et la **durée mesurée**, propres à chaque exécution.

> **Une écriture réussie n'était pas un coup unique.** Le résultat est
> **vérifiable par quiconque contre le dépôt public**, sans accès à
> l'installation.

### 3.2 L'ASSAINISSEMENT de l'instrumentation

Le **puits de preuve transport** a été **réarmé** et a produit la preuve n° 4 du
`G2-P` §16 — **ligne d'invocation réelle, sorties standard et d'erreur
intégralement et séparément, code retour, durée mesurée** — **automatiquement**,
sans geste manuel. Les deux sorties d'erreur sont **vides** et **jamais
fusionnées** avec les sorties standard.

---

## 4. Ce qui demeure OUVERT

| Objet | État |
|---|---|
| **`C1`** | **OUVERTE.** Non satisfaite, et toujours **non calculable** |
| **`U-2`** | **OUVERTE.** Aucune valeur admissible |
| **Coexistence** | **NON QUALIFIÉE.** La campagne s'est déroulée **dispositif historique arrêté**. Elle ne dit rien d'une écriture en coexistence |
| **`H2`** | **OUVERTE.** La preuve *one-writer* est bornée aux **clients du démon** |
| **`H6` (b)** | **OUVERTE**, pour le même motif |
| **`U-3`** | **OUVERTE.** Le compte des captures prouve les écritures **de Boilerack**, non le total tous écrivains confondus |
| **Écriture soutenue** | **NON ÉTABLIE** |
| **Capacité de production** | **AUCUNE.** La souveraineté demeure **interdite** — `w4f` §11.1, acte réservé **4** |

> **Aucune inconnue n'a été réduite par cette campagne**, et le protocole
> l'avait dit avant de commencer.

---

## 5. La campagne homologuée, telle qu'exécutée

| | Valeur | Établie par |
|---|---|---|
| Initiale `V_brut` | **`2.000000 `** *(espace final inclus)* | `EI-10`, deux captures nues concordantes |
| `V_canon` | **`2`** | dérivation entière **sans perte** — pas d'`AB-9` |
| Cible | **`3`** = `V_canon + 1` | `3 ≤ 40` : admissible au §5 du protocole |
| Restaurée | **`2`** | restauration **pré-décidée** par l'autorisation — `w4f` §7.3, cas 2 |

**Rôle unique : `heating_curve_shift` / `setNiveauM1`.** Actes réservés
autorisés : **1, 2 et 3**. **L'acte réservé 4 est resté interdit, et n'a pas été
employé.**

**Cardinalité respectée** : **une** écriture au temps 10, **une** au temps 12,
**zéro** partout ailleurs. Le puits porte **exactement deux rangs**. Les lectures
des temps 4, 6, 9, 11 et de l'étape 1 de la restauration n'entrent pas dans ce
décompte : ce sont des lectures.

**Acquittements** : `accepted` puis **`applied`** pour chacune des deux
commandes, sur le topic d'acquittement du rôle, avec le même identifiant de
requête que la commande.

### 5.1 Les preuves d'état initial

Les treize preuves **`EI-1` à `EI-13`** ont été établies **dans l'ordre du §9**,
**sans allègement** :

- **`EI-5` / `PR-1`** — superviseur neutralisé : timer inactif **avec prochain
  tir vide**, unité d'exécution inactive **avec sortie constatée**, **aucun
  processus du superviseur vivant**, établi sur un **instantané figé de la table
  des processus analysé HORS LIGNE**, avec **motif témoin** ;
- **`EI-6` / `PR-2`** — pont arrêté, **aucun redémarrage automatique**, **zéro
  nouvelle ouverture** au journal du démon sur la fenêtre ;
- **`EI-8`** — inventaire des unités inscriptibles **toutes inactives**, aucune
  autre session, **fenêtre muette sans aucune ouverture** ;
- **`EI-10`** — **concordance brute et sémantique** des deux formes d'une même
  lecture, par captures nues **hors du chemin Boilerack** ;
- **`EI-11`** — autorité constatée **sur le fichier persisté**, jamais sur l'état
  courant du processus ;
- **`EI-12`** — **journal du différentiel horodaté côté broker**, un seul abonné
  maintenu sur toute la fenêtre, baseline stable, puis **exactement un
  abonnement et un client supplémentaires** au démarrage manuel — **la valeur
  que `W1` §7.2 prédit** ;
- **`EI-13`** — observabilité relevée **sur les trois plans**.

> **Une auto-correspondance a été rencontrée à `EI-5`, et écartée.**
> L'instantané figé portait une ligne appariant le superviseur : **la ligne de
> commande de la session d'exploitation elle-même**, identifiée et **exclue
> nommément**. Un filtrage en direct n'aurait pas permis de la voir — c'est le
> défaut que `G2-C` §6 consigne sous `A-2`.

### 5.2 Les gardes

- **`G-a`** : `<unité-boilerack>` **non activée au démarrage**, prouvé **avant**
  le temps 8 **et reconstaté après le démarrage manuel**. **Démarrer n'est pas
  activer.**
- **`G-b`** : configuration **persistée** fermée **hors les temps 8 à 13**,
  prouvé **sur le contenu du fichier**.

**`EI-3` est demeurée un recours, jamais une étape** : aucun redémarrage machine
n'a été employé, ni comme rollback ni autrement.

### 5.3 La restauration

Les **cinq étapes** de `W4-C` §13 ont été exécutées et prouvées, dont les **trois
faits distincts `A`, `B` et `C`** de l'étape 3, établis **séparément** — la
sortie standard du pont **n'a pas servi** au fait `B` —, et l'**étape 5**, cycle
nominal du superviseur **sans action corrective**, observé de bout en bout.

**`PR-1` et `PR-2` ont été redoublées** : le rapport porte **comment l'arrêt a
été établi, et comment la reprise l'a été**.

---

## 6. Artefacts terrain gelés — empreintes seules

Les rapports et leurs pièces sont conservés **hors du dépôt**, et transmis
manuellement à l'auditeur. **Le dépôt n'en porte que les empreintes**, sur le
modèle de `G2-C` §4.

### 6.1 Exécution HOMOLOGUÉE — `18:46:07Z` → `19:14:56Z`

| Pièce | SHA-256 |
|---|---|
| `w4s-resultat-terrain-rejeu-20260903.md` | `25b815bfd3a18d4cd3a49f02de0b059a50469a3c10c141039186596ec99fbd16` |
| `MANIFESTE-SHA256.txt` *(83 pièces)* | `358c9eaff2178b5ede67e83025b429d67765373318e3fceea1bccb875449ab52` |
| `w4s-rejeu-homologation-20260903.tar.gz` | `91017b55bf94c890296f192bfe406aa0d96572409ec8e291d676a429076d7385` |

### 6.2 Exécution NON HOMOLOGUÉE — `16:15:15Z` → `16:49:38Z`

**Conservée au dossier, et ses empreintes publiées au même titre.** Une
exécution non homologuée ne s'efface pas.

| Pièce | SHA-256 |
|---|---|
| `w4s-resultat-terrain-20260903.md` | `47431773a8a7dff3e51670008512741a4e5be1263deb8d09dfcb8d2ff8928683` |
| `MANIFESTE-SHA256.txt` *(80 pièces)* | `fba698b853acaa147baacca336a52549f4c07c030f004477b4b907900b2d004a` |
| `w4s-homologation-20260903.tar.gz` | `d2e3166ff27ee427a33cdad931f8f12da169599b6e024ba00817cb35de66c9c8` |

> **Aucune constante de site ne figure dans le présent document.** Le secret
> employé pour le transport ne figure **dans aucun artefact**, ni en clair ni
> par empreinte de sa valeur.

---

## 7. Réserves conservées — non corrigées

> **Aucune n'est requalifiée en conformité.** Elles sont consignées telles que
> l'audit les a qualifiées.

### 7.1 Écart `P-A1` — non-conformité formelle, **non bloquante**

La règle du §6.3 du protocole, n° 3, exige un compteur de captures
d'acquittement **« incrémenté à chaque `ACK` reçu »**. **Quatre acquittements
ont été reçus, et déposés dans deux fichiers — un par commande.**

| | |
|---|---|
| **satisfait en substance** | aucune capture **perdue**, aucune **écrasée** — le dépôt était en écriture unique —, numérotation **continue**, aucune capture à déclarer manquante |
| **non satisfait** | **la lettre de la règle.** Un compteur par acquittement aurait produit **quatre** fichiers |

**L'audit a qualifié cet écart NON BLOQUANT et demandé qu'il soit conservé. Il
l'est.** Le correctif intégré par la PR #100 **ne l'a pas corrigé**, et le
présent constat **ne le corrige pas davantage**.

### 7.2 Geste préparatoire — limite déclarée, **non bloquante**

Avant la campagne homologuée, les deux répertoires de l'exécution non homologuée
occupaient les chemins canoniques. Ils ont été **renommés, sans suppression ni
écrasement**, et leur intégrité vérifiée par empreinte agrégée avant et après.

> **La limite, énoncée sans atténuation** : ce geste est **affirmé et vérifié en
> session**, mais **il n'est adossé à aucune des 83 pièces**. Il est
> **antérieur à la création de l'atelier**, et **hors des sorties exigées par le
> §16** du protocole. **Il n'est donc pas prouvé par l'artefact.**
>
> **L'audit l'a qualifié NON BLOQUANT.** Le présent constat le consigne **comme
> une limite**, et non comme une preuve.

### 7.3 Les réserves déjà ouvertes

**Les réserves du protocole demeurent intégralement**, la campagne n'en ayant
levé aucune : `R-1` redémarrage machine d'origine non établie · `R-2`
*one-writer* borné · `R-3` puits · le fait que le lot **n'ouvre aucune capacité
de production** · et toutes celles que `G2-C` §6 conserve.

---

## 8. Régime de `W4-S` — exécutée, close, non réutilisable

> **Clause.** `W4-S` est **exécutée et close**. L'autorisation qui l'a permise
> était **unique, explicite et distincte**, et elle est **CONSOMMÉE**.

**Quatre conséquences, opposables :**

1. **`W4-S` ne se rejoue pas.** L'autorisation valait *« une exécution, et une
   seule »* ; cette exécution a eu lieu. **Le présent constat ne rouvre rien** ;
2. **aucune écriture ultérieure ne peut s'en réclamer** — ni sur le même rôle,
   ni sur un autre, ni « dans les mêmes conditions ». Une nouvelle écriture
   exige une **nouvelle autorisation normative**, appuyée sur **un document qui
   la définit**, puis une **décision humaine explicite et distincte** ;
3. **l'amendement de séquencement du §4 et l'extension nominale du puits du
   §6.3 sont ÉTEINTS.** Aucune campagne postérieure ne s'en autorise, ni de
   `W4-S`, ni du fait qu'ils aient servi ;
4. **le bornage reste opposable, non auto-appliqué.** Rien dans le code
   n'empêche une écriture hors campagne ; **c'est la discipline qui l'empêche**,
   et ce constat en fait partie.

**L'instrumentation est DÉSARMÉE.** La variable d'atelier a été retirée du
fichier d'environnement persisté, l'autorité d'écriture est refermée sur le
fichier persisté, et `<unité-boilerack>` est non activée au démarrage et
inactive.

> **Les deux fichiers persistés sont revenus BYTE À BYTE à leur état
> d'avant-campagne**, empreintes vérifiées de part et d'autre. Le secret de
> transport est demeuré **présent et intact** tout du long.

**L'installation a été rendue nominale** : pont, démon et timer du superviseur
actifs et activés au démarrage, superviseur repassé par un cycle nominal sans
action corrective, valeur de la chaudière égale à `V_brut`.

---

## 9. Ce que ce document ne fait pas

Il **n'exécute rien** · **n'autorise rien** · **n'amende aucun contrat** — en
particulier **il ne modifie pas `w4s-campagne-minimale.md`, ni son §17.1** ·
ne conduit aucun terrain · ne demande aucun code · **ne rouvre ni `P-A5`, ni
`G.3`, ni l'acte réservé 4** · **n'ouvre aucune `P-9`** · ne touche ni `C1`, ni
la coexistence · **n'ouvre ni `W4-F3`, ni `W4-F4`, ni `W4-F5`, ni `T0`, ni
`T1`, ni `T2`** · ne corrige aucune réserve · ne lève aucune inconnue.

**Il constate une campagne homologuée, la referme, et s'arrête là.**
