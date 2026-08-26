# Extraction `A5` — le jeu de commandes du pont

> **Version 2**, après audit. Deux erreurs corrigées : le décompte des motifs de
> `c7` §4.3 — **cinq**, non quatre — et l'attribution de la lecture XML, qui
> revient à `w4-arbitrage-activation-debug.md`, non à `w4c` §11.3. Deux
> précisions rédactionnelles accompagnent, sans effet doctrinal. **Aucune
> conclusion ne change.**
>
> **Version 1.** Lot documentaire `W4-F2`. Il exécute **l'acte suivant établi par
> `w4f2-regime-instruction.md` §16** : consulter `A5` et en extraire la liste des
> commandes du pont. Aucun accès hôte, aucun terrain, aucun runtime, aucune
> mutation, aucun `vclient`, aucun `debug`, aucune chaudière.

---

## 1. Objet et frontières

Ce document **extrait**, d'une source de niveau 2 publique et citable, la liste
des commandes attribuées au pont historique ; il **confronte** cette liste aux
commandes déjà établies dans Boilerack ; il **recalcule** le résidu du régime.

Il ne fait rien d'autre. En particulier, il **n'amende aucun contrat**, ne rouvre
aucun arbitrage clos, n'ouvre ni `Acte B`, ni `T0` / `T1` / `T2`, et ne modifie
ni `C1`, ni `C5`, ni `C7`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.**

---

## 2. La source, identifiée par son empreinte

| | |
|---|---|
| Autorité | **`A5`**, désignée par `w4c-write-capture-protocol.md` §3 et déclarée **publique et citable** |
| Dépôt | `antoinevalentinHA/arsenal` (public) |
| Chemin | `00_documentation_arsenal/outils_externes/boiler_pi/mqtt.md` |
| Titre | *ARSENAL — Boiler Bridge · Contrat MQTT* |
| Composant déclaré | `arsenal-boiler-bridge`, **version bridge `v0.4.3`**, dernière mise à jour **2026-03-27** |
| Blob | `170feb98b7da70be3fad2991f76b7bd2d197cc3e` |
| SHA-256 | `4d1505e7dca2675610307a8f03410abb7fc6eeeb015e0d80a3df1a9522d8cb72` |
| Taille | 17 729 o · 440 lignes |
| Dernier commit touchant le fichier | `5b1af9cded2845883f811556419776495ca31f09`, 2026-06-05, *« docs: normalize markdown H1 headings »* — présent sur `origin/main` |
| État de l'arbre au moment de la lecture | **propre** pour ce fichier — aucune modification locale non versionnée |

> **Nature de la source, à ne pas confondre avec une observation.** `A5` est un
> **contrat normatif**, pas un relevé du pont en fonctionnement. Ce qu'il établit,
> c'est ce que le pont **doit** faire. La conformité du binaire déployé à ce
> contrat **n'est pas établie par `A5` lui-même** — et la correspondance entre la
> version `v0.4.3` qu'il déclare et le blob de pont identifié par `provenance.md`
> est **non établie**. Ce point est repris au §10.

---

## 3. Méthode

Lecture intégrale du document, puis extraction par sections. La mission désignait
`A5` §5 ; l'inventaire **exhaustif** des commandes exige d'y adjoindre §3
(télémétrie), §2.4 / §2.5 (sonde de santé) et §10 (`OPEN-04`), qui nomment eux
aussi des commandes `vclient`. §4, §7, §9 et §11 ont été lus et **ne nomment
aucune commande supplémentaire**.

Un relevé mécanique de toutes les occurrences de la forme `get*` / `set*` dans le
fichier a été effectué en contrôle de l'extraction manuelle. Il ne fait apparaître
**aucune commande hors des listes ci-dessous**. Deux formes supplémentaires y
figurent — `setXxx` et `getTempXxx` — mais ce sont des **métavariables** des
diagrammes ASCII de §7 et §7b, non des commandes.

> **Ce contrôle est une heuristique lexicale, et rien de plus.** Il ne détecte que
> ce qui porte le préfixe `get` ou `set` **en clair dans le fichier**. Une commande
> `vclient` désignée sous une autre forme lexicale, construite dynamiquement, ou
> simplement **absente du contrat**, lui échapperait. Il **corrobore** la lecture
> intégrale ; il ne la remplace pas, et ne démontre pas à lui seul l'exhaustivité.

---

## 4. Extraction — §5, commandes d'écriture et de relecture

`A5` §5 décrit quatre commandes, chacune sous forme d'un couple **écriture +
relecture de confirmation**.

| § | Écriture | Relecture | Bornes | Pas | Tolérance de confirmation |
|---|---|---|---|---|---|
| 5.1 | `setTempWWsoll <value>` | `getTempWWsoll` | [10 ; 60] °C | — (int) | — |
| 5.2 | `setTempRaumNorSollM1 <value>` | `getTempRaumNorSollM1` | [5 ; 30] °C | — (int) | — |
| 5.3 | `setNiveauM1 <value>` | `getNiveauM1` | [-13 ; 40] | 1 (entier strict) | **0** — égalité stricte |
| 5.4 | `setNeigungM1 <value>` | `getNeigungM1` | [0.2 ; 3.5] | 0.1 | **± 0,01** |

> **La relecture est constitutive du statut `applied`.** `A5` §4.2 définit
> `applied` comme *« Écriture confirmée par **relecture vclient** »*, et §4.4
> précise la boucle : *« Après écriture vclient, le bridge relit la valeur pour
> confirmation. Délai maximum : **10 secondes**, sondage toutes les **1
> seconde**. »* Un ACK `applied` implique donc qu'une écriture **et** une
> relecture ont abouti.

---

## 5. Extraction — §3, commandes de lecture télémétrique

| Suffixe de topic | Commande |
|---|---|
| `telemetry/temperatures/outdoor` | `getTempA` |
| `telemetry/temperatures/supply` | `getTempKist` |
| `telemetry/temperatures/dhw` | `getTempWWist` |
| `telemetry/dhw/setpoint` | `getTempWWsoll` |
| `telemetry/heating/setpoint` | `getTempRaumNorSollM1` |
| `telemetry/heating/reduced_reference` | `getTempRaumRedSollM1` |
| `telemetry/heating/curve/slope` | `getNeigungM1` |
| `telemetry/heating/curve/shift` | `getNiveauM1` |
| `telemetry/burner/modulation` | `getBrennerStatus` |
| `telemetry/burner/state` | **`—`** — état dérivé, **aucune commande** |

**Neuf commandes, dix topics.** `A5` §3 énonce en outre la règle de publication :
*« Un topic absent signifie que la lecture vclient a échoué »*, et *« En cas
d'échec de lecture vclient, le bridge n'émet pas de nouvelle valeur pour le topic
concerné »*.

---

## 6. Extraction — §2.4 / §2.5 / §10, la sonde de santé

`A5` §2.5 porte une note explicite : *« `vcontrold_status` et `optolink_status`
sont dérivés d'un **unique probe vclient** (`getTempKist`). Ils constituent deux
projections métier d'un même test de santé global et ne permettent pas de
distinguer finement une panne Optolink d'une panne vcontrold. Période de
publication : **30 secondes**. »*

§10 la reprend comme dette normative ouverte, `OPEN-04`, de criticité moyenne.

**Aucune commande nouvelle** : la sonde de santé réemploie `getTempKist`.

---

## 7. Le jeu complet, dédupliqué

| Classe | Cardinal | Commandes |
|---|---|---|
| Lecture | **9** | `getTempA` · `getTempKist` · `getTempWWist` · `getTempWWsoll` · `getTempRaumNorSollM1` · `getTempRaumRedSollM1` · `getNeigungM1` · `getNiveauM1` · `getBrennerStatus` |
| Écriture | **4** | `setTempWWsoll` · `setTempRaumNorSollM1` · `setNiveauM1` · `setNeigungM1` |
| **Total distinct** | **13** | |

> **Les quatre relectures de §5 n'ajoutent aucune commande.** `getTempWWsoll`,
> `getTempRaumNorSollM1`, `getNiveauM1` et `getNeigungM1` appartiennent déjà, les
> quatre, au jeu de lecture télémétrique de §3. Le pont **relit par les mêmes
> commandes qu'il publie**. L'intersection est exacte, et c'est un fait
> d'extraction, non une interprétation.

> **La sonde de santé n'en ajoute pas davantage** : `getTempKist` est la deuxième
> entrée du tableau de lecture.

**Le jeu est donc clos à treize commandes — au niveau du contrat `A5` v0.4.3**,
auxquelles s'ajoute un dixième topic qui n'en consomme aucune : `burner/state`,
état dérivé par la règle *« `on` si modulation > 0, sinon `off` »*.

---

## 8. Confrontation aux sources Boilerack

| Commande | `A5` | `c7` §4.2 / §4.3 | `measurements.py` | Autres sources Boilerack |
|---|---|---|---|---|
| `getTempA` | §3.1 | table normative, **v1** | oui | — |
| `getTempKist` | §3.1, §2.5 | table normative, **v1** | oui | **`w4-arbitrage-activation-debug.md`** — lecture du XML déployé : *« `getTempKist` résout pour `20CB` »* ; repris par `w4f2-regime-instruction.md` |
| `getTempWWist` | §3.1 | table normative, **v1** | oui | — |
| `getTempWWsoll` | §3.2, §5.1 | table normative, **v1** | oui | — |
| `getTempRaumNorSollM1` | §3.2, §5.2 | table normative, **v1** | oui | — |
| `getTempRaumRedSollM1` | §3.2 | table normative, **v1** | oui | — |
| `getNeigungM1` | §3.3, §5.4 | table normative, **v1** | oui | — |
| `getNiveauM1` | §3.3, §5.3 | table normative, **v1** | oui | `w4c` §11.3 |
| `getBrennerStatus` | §3.4 | **§4.3, reporté hors v1** | **non** | — |
| `setTempWWsoll` | §5.1 | — | — | `w4c` §5, fait `E2` |
| `setTempRaumNorSollM1` | §5.2 | — | — | `w4c` §5, fait `E2` |
| `setNiveauM1` | §5.3 | — | — | `w4c` §5, fait `E2` |
| `setNeigungM1` | §5.4 | — | — | `w4c` §5, fait `E2` |

### 8.1 Trois concordances, et aucune divergence

1. **Le décompte de `c7` est confirmé par une source indépendante.** `c7` §1.2
   déclare **neuf lectures** plus **un état dérivé**, soit **dix publications**,
   et le déclare *« relevé dans son **code**, jamais supposé »*. `A5` §3 donne
   **exactement** neuf commandes et un état dérivé. Les deux sources sont
   d'origines distinctes — l'une lue dans le code du pont, l'autre écrite comme
   contrat normatif — et **concordent au nom de commande près et au suffixe de
   topic près**. La concordance porte sur les dix lignes.
2. **La sonde unique est confirmée par une source indépendante.** `c7` §1.2 :
   statuts *« dérivés d'une unique sonde `getTempKist` »*. `A5` §2.5 et `OPEN-04`
   disent la même chose, dans les mêmes termes.
3. **Les quatre écritures de `w4c` §5 `E2` sont exactement celles de `A5` §5.**
   Aucune écriture supplémentaire, aucune manquante. `A5` fournit en outre les
   bornes, pas et tolérances que `w4c` §3 lui attribuait.

**Aucune divergence n'a été relevée.** Ni commande présente dans une source et
absente de l'autre, ni attribution contradictoire.

### 8.2 Le seul écart, déjà connu et déjà motivé

`measurements.py` porte **huit** commandes, `A5` et `c7` en portent **neuf**. La
neuvième est `getBrennerStatus`, et `c7` §4.3 avait déjà énoncé l'écart et ses
**cinq** motifs. **L'extraction ne le rouvre pas.**

---

## 9. Ce que l'extraction ferme

> **Le résidu `(a)` de `H6` — « les commandes émises par le pont résolvent-elles
> toutes ? » — change de nature.**

Ce résidu comportait deux parts, qu'il faut distinguer pour ne pas surévaluer ce
qui vient d'être obtenu :

| Part | Avant | Après |
|---|---|---|
| **énumération** — sait-on quelles commandes le pont émet ? | **ouverte** : `w4f2-regime-instruction.md` §12.3 constatait que *« la liste complète des commandes du pont n'est pas dans ce dépôt »* | **fermée au niveau du contrat `A5` v0.4.3** — treize commandes, source publique et citable |
| **résolution** — chacune résout-elle dans la configuration déployée ? | établie ou corroborée **pour les commandes nommées**, indéterminée pour d'éventuelles autres | **couverte pour les treize**, par des éléments de **force inégale** (§10) |

> **La conséquence la plus nette porte sur `(c)`.** Le résidu `(c)` de `H6` — une
> session de la population protégée peut-elle se terminer sans avoir acquis le
> périphérique — comportait le cas **« commande non résolue »**.
> `w4f2-regime-instruction.md` §9.3 le donnait fermé *« pour la sonde »*
> seulement, et §12.3 *« pour les commandes nommées »*. **L'énumération étant
> close au niveau du contrat, ce cas est désormais traité pour l'intégralité du
> jeu de commandes que le contrat attribue au pont** : **aucune commande non
> inventoriée au contrat** ne peut plus être invoquée. Les **autres** chemins de
> sortie précoce de `(c)` restent ouverts, sans changement.

---

## 10. Ce que l'extraction ne ferme pas

> **La part « résolution » est couverte, non prouvée uniformément.** Il faut dire
> commande par commande sur quoi elle repose, sans niveler.

| Commandes | Sur quoi repose la résolution | Force |
|---|---|---|
| `getTempKist` | lecture du XML déployé — la commande **résout** pour `20CB` | **preuve directe** |
| `getNiveauM1` | `w4c` §11.3 l'emploie comme lecture réelle du protocole sur cette installation | **preuve directe** |
| `setTempWWsoll`, `setTempRaumNorSollM1`, `setNiveauM1`, `setNeigungM1` | `w4c` §5 `E2`, *« éprouvées par des mois d'usage, pas par un raisonnement »*, `I-2` levée — une commande qui ne résout pas est rejetée avant Optolink et n'écrit rien | **preuve d'usage** |
| `getTempA`, `getTempWWist`, `getTempWWsoll`, `getTempRaumNorSollM1`, `getTempRaumRedSollM1`, `getNeigungM1` | publication **conditionnelle** au succès (`c7` §1.2, `A5` §3), à **cadence mesurée** ≈ 19-21 s | **corroboration répétée** |
| `getBrennerStatus` | même mécanisme de publication conditionnelle ; observée publiée par le pont historique (`c7` §1.2 et §4.3) | **corroboration répétée** |

> **Aucune de ces lignes n'est une extrapolation d'`A5`.** `A5` fournit
> l'énumération ; la résolution reste établie par les sources antérieures. **Ce
> lot n'a rien ajouté à la part résolution, et ne prétend pas l'avoir fait.**

Restent également ouverts, **sans le moindre changement** :

- les **transitions 1 et 2** du maillon 2 — faits d'exécution du superviseur ;
- `H1` en entier ;
- `H2` en entier, et donc `H6` **(b)** qui en est absorbé ;
- les chemins de sortie précoce de `H6` **(c)** autres que la non-résolution ;
- la conformité du pont **déployé** au contrat `A5` — la version `v0.4.3`
  déclarée par `A5` et le blob de pont identifié par `provenance.md` **ne sont
  pas rapprochés**, et rien dans le dépôt public ne permet de le faire.

---

## 11. Effet sur `H3` — aucun

> **`A5` documente le pont. `C1` protège les sondes du superviseur.**

Ce sont deux populations distinctes : `w4c` §8 décrit le superviseur comme un
processus qui sonde toutes les 3 minutes sous un budget de 5 secondes, et qui
**redémarre le pont** en cas d'échec. Le pont est son objet, non lui-même.

**`A5` ne dit rien du superviseur** — ni de son existence, ni de sa commande de
sonde, ni de sa cadence. Il ne peut donc rien établir sur les **transitions 1 et
2**, qui sont des faits d'exécution du superviseur.

> **Il serait tentant, et faux, d'écrire que la sonde du superviseur est
> `getTempKist` parce que celle du pont l'est.** `A5` §2.5 attribue cette sonde au
> **pont**. Aucune source consultée n'attribue de commande à la sonde du
> superviseur. **Non établi.**

Le statut de `H3` est donc **inchangé** : `PARTIEL`, maillon 1 `ÉTABLI`,
transition 4 `ÉTABLIE`, transitions 3 et 5 `ÉTABLIES SOUS CORROBORATION` et
conditionnées à 1 et 2, transitions 1 et 2 **ouvertes**.

---

## 12. Effet sur `H6` — réduction réelle, bornée

| Résidu | Avant | Après |
|---|---|---|
| **(a)** | *« largement fermé au niveau 1, pour les commandes nommées »* | **énumération close au niveau du contrat `A5` v0.4.3** ; résolution **couverte pour les treize commandes**, par des éléments de force inégale |
| **(b)** | `= H2` | **inchangé** — `A5` ne dit rien de l'IPC System V |
| **(c)** | non-résolution fermée *« pour la sonde »*, autres chemins ouverts | non-résolution **traitée pour tout le jeu attribué au pont par le contrat** ; **autres chemins inchangés** |

**Statut de `H6` : `PARTIEL`, inchangé** — le constat `RÉDUITE, NON CLOSE`
demeure exact, et il le demeure pour la même raison qu'avant : **(b)** est
absorbé par `H2`, que rien ici ne touche.

> **La réduction est réelle mais elle ne change pas de statut.** Un résidu dont
> une part se ferme ne fait pas basculer l'hypothèse tant qu'une autre part
> demeure. C'est le cas.

---

## 13. Résidu du régime, recalculé

| Résidu | Nature | Mouvement dû à ce lot |
|---|---|---|
| **maillon 2 non prouvé** — transitions **1** et **2** | faits d'exécution du superviseur | **aucun** |
| **maillons 3, 4, 6 conditionnels à `H1`, `H2`, `H6`** | hypothèses d'installation | **aucun** — `H6` est réduit, non déchargé |
| **maillon 5 conditionnel à `H1`** | idem | **aucun** |
| `H1` | lien binaire ↔ arbre ; traces non instruites | **aucun** |
| `H2` | invariant sur la fenêtre protégée ; voies structurelles non instruites | **aucun** |
| `H6` **(a)** | commandes du pont | **fermé quant à l'énumération, au niveau du contrat `A5` v0.4.3** |
| `H6` **(b)** | `= H2` | **aucun** |
| `H6` **(c)** | chemins de sortie précoce | non-résolution **traitée pour tout le jeu** ; autres chemins **aucun** |

> **Le résidu du régime est identique à celui de la veille.** Ce qui a bougé est
> **interne à `H6`**, et `H6` reste `PARTIEL`. Le maillon 2 — seul maillon
> manquant — n'est pas touché.

---

## 14. Régime — `INDÉTERMINÉ`, inchangé

| | |
|---|---|
| Niveau épistémique | `PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION` — valeur `ADDITIF — CONDITIONNEL À H1/H2/H3/H6` |
| **Régime opératoire** | **`INDÉTERMINÉ`** → branche **C** → **`W4-F2 NON QUALIFIABLE — STOP`** |

`ADDITIF` exige la preuve explicite de **chacun** des six maillons — *« un seul
manquant donne `INDÉTERMINÉ` »*. Le maillon 2 manque. `NON ADDITIF` exige une
**preuve positive sur la population protégée** ; ce lot n'en apporte aucune, et
n'en cherchait pas.

**Aucune conclusion par défaut n'est émise.**

---

## 15. Le plus petit acte suivant

L'ordre prescrit par `w4f1a-vcontrold-concurrency.md` §10, et repris par
`w4f2-regime-instruction.md` §16, désigne l'étape suivante : **l'amont
`vito.xml`**.

| | |
|---|---|
| **acte** | lire l'amont `vito.xml` documenté, **niveau 2** |
| **régime** | aucun régime `G` engagé — ce n'est pas un acte sur l'installation |
| **rendement, désormais précisé** | la comparaison porte sur un jeu **énuméré de treize commandes, clos au niveau du contrat `A5` v0.4.3**, ce qui n'était pas le cas avant ce lot. Elle réduirait la part hôte à une **comparaison d'intégrité**, méthode déjà employée par Acte A sur les six blobs |
| **ce qu'il ne fermerait pas** | transitions 1 et 2 · `H1` · `H2` · `H6` **(b)** et **(c)** |

**Et seulement après** viendrait un acte `G.1` sur l'hôte pour les transitions 1
et 2. Il **n'est pas proposé ici**.

---

## 16. Constats collatéraux, relevés et non consommés

Trois faits extraits de `A5` sortent du périmètre de ce lot. Ils sont consignés
**sans être exploités**, et **n'amendent aucun contrat**.

1. **Type de `getBrennerStatus`.** `A5` §3.4 donne *« Valeur brute de modulation
   (ex. `"75%"`) »* et la règle de dérivation *« `on` si modulation > 0, sinon
   `off` »*. `c7` §4.3 motif 2 tenait le type et l'unité pour **non établis par
   le dépôt public**. `A5` **informe** ce motif — il ne le lève pas : la mention
   est un **exemple**, non une déclaration normative de type. Les **quatre autres
   motifs** de `c7` §4.3 — qui en compte **cinq** — demeurent intacts : **1**
   l'absence de caractérisation par C5, **3** l'absence de champ d'unité dans
   `CommandSpec`, **4** la dépendance alléguée à la régulation, non prouvée, et
   **5** le **risque silencieux** d'un topic conservé sous sémantique incertaine.
   **Le report hors v1 n'est pas rouvert.**
2. **Paramètres internes du pont.** `A5` §9 déclare `TELEMETRY_PERIOD_SECONDS`
   10 s, `HEARTBEAT_PERIOD_SECONDS` 30 s, `BRIDGE_STATUS_PERIOD_SECONDS` 30 s,
   `COMMAND_CONFIRM_TIMEOUT_SECONDS` 10 s, `COMMAND_CONFIRM_POLL_SECONDS` 1 s.
   Les deux premiers concordent avec les cadences **configurées** relevées par
   `c7` §1.2. Les deux derniers décrivent une boucle de confirmation pouvant
   émettre **jusqu'à dix relectures en dix secondes** après une écriture.
3. **Portée du point 2.** Cette boucle est un fait d'**occupation du pont**. Elle
   n'est **pas consommée ici** : `borne_sonde`, `occupation_max`, `U-2` et `U-7`
   sont hors périmètre de ce lot par décision explicite, et `C1` protège la
   population du **superviseur**, non celle du pont. Le fait est consigné pour un
   lot ultérieur, sans conclusion.

---

## 17. Ce que ce document ne fait pas

Il ne tranche aucun régime · il n'émet aucune conclusion par défaut · il ne crée
aucune hypothèse, aucun seuil, aucune constante · il ne modifie aucun contrat ·
il ne rouvre ni `c7` §4.3, ni `C1`, ni `C5` · il n'ouvre ni Acte B, ni `T0` /
`T1` / `T2` · il n'autorise aucun terrain, aucune lecture sur l'hôte, aucune
inspection de journal, aucune mutation, aucun `debug` · il ne consulte ni `A6`,
ni `vito.xml`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.** Le pont historique demeure
l'unique écrivain réel de production ; la surface transactionnelle demeure sans
autorité, `false`.

---

## 18. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Extraction initiale de `A5`. Exécute l'acte désigné par `w4f2-regime-instruction.md` §16 |
| **2** | Audit : décompte des motifs de `c7` §4.3 porté à **cinq** (§8.2, §16) ; lecture XML réattribuée à `w4-arbitrage-activation-debug.md` (§8). Bornage du contrôle lexical (§3) et des formulations de clôture, rapportées au **contrat `A5` v0.4.3**. Aucune conclusion modifiée |
