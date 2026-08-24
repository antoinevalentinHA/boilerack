# W4-F1A — Régime de concurrence de `vcontrold` : cadrage

> **Lot W4-F1A — cadrage d'un sous-lot PRÉ-W4-F2. Version 3**, après audit delta
> de la V2, qui l'a validée avec deux réserves mineures. La V3 les corrige, et
> rien d'autre : les sorties et le critère `GO` héritaient d'une forme absolue
> antérieure aux trois niveaux épistémiques, et n'avaient pas été réalignées.
> Désormais le **besoin suivant** (§11.7.1) et le **statut `U-1` / `I1`**
> (§11.7.2) se **dérivent** du niveau atteint, le critère `GO` porte sur la
> **méthode** et non sur le verdict obtenu (§11.9), et le double emploi du mot
> `INDÉTERMINÉ` est réconcilié (§6.4). L'architecture V2 — §5, §6, §7, §11.5,
> §12 — est **inchangée** : l'audit l'a validée.
>
> Sous-lot **NON TERRAIN**, **SANS CODE**. Aucun accès au Pi, au réseau local, au
> broker, à `vclient`, à la chaudière, à un service systemd. Aucun déploiement,
> aucune installation, aucune instrumentation, aucune modification de
> configuration, aucune écriture.
>
> **W4-F2 reste FERMÉ.** Ce document ne demande ni n'accorde aucune autorisation
> terrain. **W4-F0 et W4-F1 restent CLOSED et intacts** : W4-F1A ne les amende
> pas, ne les rouvre pas, et ne diminue aucune de leurs garanties.

---

## 1. Pourquoi ce lot existe

La clôture de W4-F1 établit un fait qui n'était pas anticipé par W4-F0 :

> Sous le contrat V3, **aucune des trois branches de T0-B ne conduit
> actuellement à `T0 GO`.**

W4-F2 est donc bloqué **structurellement**, et non par défaut d'autorisation. Une
autorisation humaine ne le débloquerait pas.

Ce document ne contourne pas ce verrou. Il détermine **quel est le plus petit lot
suffisant** pour rendre la question tranchable un jour, sans affaiblir W4-F1.

---

## 2. La matrice exacte des trois branches

Reprise littérale de `w4f1-confirmation-window.md` §8.2.1, sans réinterprétation.

| Branche | Condition d'entrée | Sortie contractuelle | Pourquoi pas de `T0 GO` |
|---|---|---|---|
| **A** | T0-B rend `ADDITIF` | `W4-F2 NON QUALIFIABLE — STOP` | `C1` est **valide** mais **arithmétiquement inatteignable** : `seuil_C1 = 0,971 s` tandis qu'**une seule lecture** coûte 2,669 à 4,029 s. Le dépassement est structurel, pas statistique |
| **B** | T0-B rend `NON ADDITIF` | `T0 NO-GO — STOP` | `C1` additive devient **sans objet**. Son remplacement est exigé **avant T1**, et **exige un nouvel audit**. Tant qu'il n'existe pas, la barrière reste fermée |
| **C** | T0-B rend `INDÉTERMINÉ` | `W4-F2 NON QUALIFIABLE — STOP` | la **validité** de `C1` n'est pas démontrée |

**L'état actuel est la branche C**, et il n'est pas choisi : c'est la valeur que
T0-B prend faute de connaître **U-1**.

> **Les trois branches ne se ferment pas pour la même raison.** A se ferme sur une
> **arithmétique** ; B sur un **artefact documentaire manquant** ; C sur une
> **preuve manquante**. Confondre les trois conduirait à construire le mauvais
> remède.

---

## 3. Classification des verrous

| Verrou | Branche | Catégorie | Justification |
|---|---|---|---|
| **V-1** — régime de concurrence de `vcontrold` inconnu | C | **B** (preuve amont) **pour une part**, **E** (installation) **pour un résidu irréductible** — voir §7 | Le modèle de service d'un démon libre se lit dans son source, mais **il dépend aussi de la façon dont ce démon est construit et invoqué** |
| **V-2** — `C1` inatteignable si le régime est additif | A | **F** + **D** | Aucune observation ne le lèvera : il est arithmétique. Opératoire seulement si le régime est établi `ADDITIF` |
| **V-3** — contrat de remplacement de `C1` absent | B | **A** | Le manque est un **document et son audit**. Opératoire seulement si le régime est établi `NON ADDITIF` |
| **V-4** — capacité du journal `vcontrold` (M1, U-3) | toutes | **B pour une part**, **E pour le reste** — voir §12 | Ce que le source *journalise* est amont ; ce que l'installation *produit réellement* est terrain |
| **V-5** — durée d'une sonde du superviseur (M6, U-2) | toutes | **E** | Sans substitut admis (W4-F1 §8.3). Hors du chemin critique de ce lot |

> **V-2 et V-3 sont mutuellement exclusifs.** Le régime est additif ou il ne l'est
> pas. **Construire l'un avant de savoir lequel, c'est avoir une chance sur deux
> de construire le mauvais.**

---

## 4. Ce que le dépôt sait de U-1, et ce qu'il ignore

### 4.1 Deux inconnues voisines, et elles ne sont pas égales

| Réf | Document | Portée |
|---|---|---|
| **I1** | `w2-transaction-concurrency-lifecycle.md` §32.1 | « Comportement réel de `vcontrold` sous accès concurrent » — propriétaire déclaré **Terrain / W4** |
| **U-1** | `w4f1-confirmation-window.md` §9 | « régime de concurrence de `vcontrold` — additif, entrelacé, ou autre » — **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`** |

> **`I1 ⊃ U-1`, et l'inclusion est stricte.** La V1 les disait « la même
> inconnue » : c'était faux. **I1** couvre tout comportement sous accès
> concurrent — robustesse, erreurs, refus, corruptions, signatures d'échec.
> **U-1** ne porte que sur la **composante temporelle** utile à `C1` : la façon
> dont les durées se composent lorsque deux clients se présentent.
>
> **W4-F1A ne peut donc fermer que U-1**, et seulement sur la population du §6.1
> — et encore, seulement si son niveau épistémique le permet. Sa sortie
> **MUST NOT** être écrite `I1 CLOSED`, dans aucun cas. Les trois formules
> admissibles, et le choix entre elles, sont fixés par la table du **§11.7.2** :
> le statut se **dérive** du niveau atteint, il ne se choisit pas.
>
> Restent ouverts dans I1, sauf preuve spécifique qui n'est pas demandée ici :
> robustesse sous concurrence, erreurs, refus, corruptions éventuelles,
> signatures d'échec, et tout comportement non nécessaire à `C1`.

W4-F1 est la formulation la plus ouverte des deux : elle admet explicitement une
**source externe** là où W2 ne voyait que du terrain. C'est cette alternative que
W4-F1A explore — sans corriger W2, qui reste tel qu'il est.

### 4.2 Ce qui est prouvé par le dépôt

| Fait | Source |
|---|---|
| version du **client** : `vclient 0.98.12-5-g8ca4797`, forme `git describe`, compilée depuis un dépôt Git | **C5 §2**, « Version observée » |
| installation de référence, `vcontrold` en service continu | **C5 §1**, « Provenance et méthode » |
| une lecture réelle « production active » coûte **2 669 à 4 029 ms** | C5 §9, « Contention et durées » |
| le pont sonde le démon toutes les 10 s ; le superviseur toutes les 3 min | W4-C §8, §9 |
| **Boilerack** ne fait jamais deux appels `vclient` simultanés | W2 §15.2 — **règle Boilerack**, structurelle |
| le journal du démon **horodate chaque connexion cliente** | W4-C §9.1 |

### 4.3 Ce que la version du client ne prouve pas

> **`vclient` n'est pas `vcontrold`.** La V1 traitait la chaîne de version du
> **client** comme si elle désignait le **démon**. Elle ne le fait pas.

Prémisses à poser explicitement, et à établir plutôt qu'à supposer :

1. `vclient` et `vcontrold` proviennent du même amont, `openv/vcontrold` ;
2. l'étiquette ou le commit amont correspondant est identifiable ;
3. **mais l'identité du démon réellement déployé doit être établie séparément** :
   sa provenance, son commit ou son paquet, et l'absence de correctif local.

À défaut de ces trois, toute conclusion reste **conditionnelle** (§7.3).

### 4.4 Ce qui n'est pas prouvé

Sept questions, aucune tranchée par le dépôt : `vcontrold` sérialise-t-il les
clients · peut-il entrelacer · existe-t-il une file interne · les connexions
sont-elles multi-fils ou multi-processus · le protocole série impose-t-il
lui-même une exclusion en aval · le journal distingue-t-il ouverture / fermeture
/ client · une preuve amont suffirait-elle sans terrain.

> **Le dépôt ne contient ni source `vcontrold`, ni URL amont, ni copie vendue.**
> Vérifié : aucun fichier, aucune référence. La seule amarre est la chaîne de
> version du client. Le mot `vcontrold` apparaît sur **59 lignes de
> `docs/design/`** — hors le présent document — toutes descriptives de son rôle,
> de sa version ou de durées observées, **aucune** de son traitement des clients
> concurrents.

> **W2 §15.3 dit exactement la bonne chose, et il faut la conserver.** La
> sérialisation interne de Boilerack « porte sur **Boilerack**, jamais sur
> `vcontrold` ». Elle ne renseigne en rien U-1, et ce lot ne l'y emploiera pas.

---

## 5. Ce que W4-F1A **ne fait pas** : rendre le verdict de T0-B

C'est la correction la plus importante de cette version.

W4-F1 §8.2 subordonne T0-B à une précondition, dans ces termes :

> « **Si, et seulement si**, T0-A montre que le journal porte ouverture **et**
> clôture **et** distinction des clients, T0-B examine leurs recouvrements et en
> déduit le régime de concurrence de `vcontrold` — U-1, sans exposer Boilerack.
> Si les données ne le portent pas, T0-B rend **`INDÉTERMINÉ`**. »

> **Clause.** **W4-F1A ne rend pas le verdict de T0-B.** Il ne peut pas s'y
> substituer, et il ne le tente pas.

Ce que W4-F1A peut faire, et rien de plus :

1. **fermer U-1** au sens de W4-F1 §9, ou constater qu'il ne le peut pas ;
2. produire une **caractérisation externe** du régime pertinent ;
3. préparer une preuve **utilisable ultérieurement**.

> **Conséquence sur la condition 4 de `T0 GO`.** Cette condition — *T0-B a rendu
> un régime compatible avec le contrat `C1` actuellement figé* — porte sur
> **T0-B**, non sur U-1. Tant que W4-F1 reste inchangé, T0-B demeure gouverné par
> T0-A : **une preuve amont ne remplace pas la précondition journal**, et la
> condition 4 ne peut pas être satisfaite par simple substitution.
>
> L'usage contractuel d'une conclusion W4-F1A dans T0-B exigerait **soit** que
> T0-A fournisse effectivement les données prévues par W4-F1, **soit** un
> amendement explicite et audité de W4-F1 §8.2.
>
> **W4-F1 est CLOSED et n'est pas amendé par ce lot.** W4-F1A assume donc que son
> résultat est **informatif et discriminant**, non directement opératoire sur
> T0-B.

C'est suffisant pour justifier le lot : le discriminant a de la valeur même sans
être opératoire (§14).

---

## 6. Règle de décision — population, verdicts, preuves minimales

La V1 changeait la nature de la preuve — de l'observation de recouvrements vers
la lecture de source — sans dire sur quelle population, ni selon quelle règle.
Cette section comble ce manque.

### 6.1 Population pertinente

> **Les sondes du superviseur, et elles seules**, conformément à W4-F1 §8.5, qui
> fonde `C1` sur cette population et sur aucune autre.

Sont **exclues** : toutes les commandes indistinctement · toutes les connexions ·
toutes les sessions · les commandes invalides ou rejetées avant Optolink · les
écritures · l'usage interactif général du démon.

> **Un régime peut dépendre de la commande.** Le lot **MUST** classifier la seule
> population du superviseur et **MUST NOT** extrapoler depuis le comportement
> d'une autre commande. Une commande rejetée avant d'atteindre la liaison ne dit
> rien du régime d'une commande qui l'atteint.

### 6.2 `ADDITIF` — chaîne causale minimale

Le verdict `ADDITIF` exige une preuve explicite de **chacun** des six maillons.
Un seul manquant donne `INDÉTERMINÉ`.

| # | Maillon à prouver |
|---|---|
| 1 | la sonde du superviseur emprunte bien le chemin `vclient` considéré |
| 2 | ce chemin demande la ressource Optolink pertinente |
| 3 | cette ressource est **exclusive** entre clients concurrents |
| 4 | un second client demandeur **bloque** jusqu'à libération, sans service parallèle équivalent |
| 5 | après libération, la sonde paie **son propre** coût de transaction |
| 6 | aucune part pertinente du travail ne se recouvre d'une manière qui invaliderait la composition temporelle employée par `C1` |

### 6.3 `NON ADDITIF` — preuve positive exigée

> **`NON ADDITIF` n'est pas résiduel.** Il exige une **preuve positive, sur la
> population protégée**, que la composition additive employée par `C1` ne
> s'applique pas.

Preuves **insuffisantes**, nommées pour qu'elles ne soient pas invoquées :

- un `fork()` à l'acceptation des connexions ;
- l'existence de plusieurs sockets ;
- l'existence de plusieurs processus ou fils ;
- le rejet d'une commande inconnue avant Optolink ;
- le comportement d'une commande n'appartenant pas à la population du
  superviseur ;
- **l'absence de preuve d'additivité**.

> **L'absence de preuve d'additivité donne `INDÉTERMINÉ`, jamais `NON ADDITIF`.**
> C'est le glissement que cette section existe pour empêcher : conclure à
> l'innocuité parce qu'on n'a pas trouvé la nocivité.

### 6.4 `INDÉTERMINÉ`

Toute situation qui n'est ni 6.2 ni 6.3 : maillon manquant, population non
isolable, régime dépendant d'une commande non classifiée, hypothèses
d'installation non énonçables.

> **Un seul `INDÉTERMINÉ`, vu sous deux angles.** Le mot apparaît ici comme issue
> de la **règle de décision**, et au §11.8 comme **niveau épistémique**. Ce n'est
> pas une homonymie : c'est le même état.
>
> | | |
> |---|---|
> | ici, §6.4 | la règle de décision **n'attribue aucune valeur de régime** |
> | §11.8 | le niveau épistémique est **`INDÉTERMINÉ`** |
>
> Les deux énoncés sont **équivalents et simultanés** : lorsque §6.4 s'applique,
> aucune valeur `ADDITIF` ni `NON ADDITIF` n'est émise, et le niveau épistémique
> **MUST** être `INDÉTERMINÉ`. Réciproquement, un niveau `INDÉTERMINÉ` signifie
> que §6.4 s'est appliqué. Aucun troisième sens n'existe.

---

## 7. Frontière amont / installation — un résidu irréductible

La V1 traitait la part installation comme un « dernier recours ». **C'est faux :
elle est obligatoire.** Le source seul ne détermine pas toujours le modèle.

> **Preuve d'existence, fournie par l'audit indépendant.** Dans l'amont, le
> modèle de traitement des clients dépend de la manière dont le démon est
> **invoqué** : un mode existerait où la création d'un processus par connexion
> n'a pas lieu, selon les arguments passés. **Ce document ne reprend pas ce fait
> à son compte** — le vérifier appartient au futur lot. Il l'emploie uniquement
> comme démonstration qu'**un même source peut produire deux comportements
> différents**, ce qui suffit à rendre la part installation obligatoire.

### 7.1 Faits amont — établissables par lecture de source

Boucle d'acceptation des connexions · présence ou absence de verrou, sémaphore ou
autre exclusion · **granularité** de cette exclusion — connexion, commande,
transaction · comportement selon les configurations connues · ce que le source
journalise (§12).

### 7.2 Faits d'installation — non établissables par lecture de source

Binaire réellement déployé · sa provenance · correctifs locaux éventuels ·
**options de compilation** · **arguments d'invocation** · configuration
d'exécution · plateforme · comportement effectif des primitives système
mobilisées, notamment les mécanismes d'exclusion inter-processus.

> **Portée à ne pas dépasser.** Le lot n'a pas à prouver des propriétés de
> plateforme sans rapport avec `C1`. Il doit identifier **les seuls paramètres
> susceptibles de changer** : l'acceptation, la création de processus,
> l'exclusion, l'attente et le réveil.

### 7.3 Verdict conditionnel

Si les faits du §7.2 ne sont pas disponibles dans un lot hors terrain — ce qui
est le cas attendu — alors le verdict **MUST** être conditionnel, et écrit comme
tel :

```
ADDITIF SOUS HYPOTHÈSES H1..Hn
NON ADDITIF SOUS HYPOTHÈSES H1..Hn
```

> **Un verdict conditionnel n'est pas un verdict.** Il **MUST NOT** être assimilé
> à un `ADDITIF` ou `NON ADDITIF` inconditionnel, ni employé comme tel par
> W4-F1. Si les hypothèses nécessaires ne peuvent pas être établies — ou même
> seulement énoncées — le verdict est **`INDÉTERMINÉ`**.
>
> Lorsque des hypothèses subsistent, W4-F1A **MUST** désigner **quel acte futur
> devra les établir**, sans l'ouvrir.

---

## 8. Observabilité — la plus petite capacité manquante

| Métrique | Disponible | Direct / proxy | Résolution | Suffit pour T0 ? | Suffit pour T1 ? |
|---|---|---|---|---|---|
| **M1** — horodatage des connexions au démon | à établir en T0-A | direct pour l'ouverture | **inconnue** | **non démontré** — la règle `r < 0,485 s` peut ne pas être tenue | idem |
| **M2** — publication du pont vue d'aval | oui | **proxy** — sensibilité non établie (U-4) | cadence du pont | oui pour `C2` et `E3` | oui |
| **M3** — état des unités | oui | direct | à établir en T0-D | oui | oui, si `cadence_max` tenue |
| **M4** — temps de fonctionnement | oui | direct | grossière, suffisante | oui | oui |
| **M5** — instantané Boilerack | oui | direct | cadence de publication | oui pour `C3` | oui |
| **M6** — durée d'une sonde du superviseur | **non** | — | — | **non** | **non** |

**La plus petite capacité manquante n'est aucune de ces six** : c'est le **régime
de concurrence** lui-même. Les métriques mesurent des **grandeurs** ; U-1 est une
**propriété de comportement**. On peut mesurer parfaitement des durées sans savoir
si deux clients se sérialisent.

> **C'est pourquoi ce lot n'est pas un lot d'observabilité.** Il aurait été plus
> facile d'écrire « il manque de l'instrumentation ». Ç'aurait été faux.

---

## 9. C1 / C2 / C3 — la chaîne causale

| Critère | Calculable à T0 ? | Calculable à T1 ? | Source requise | Branche qui le bloque |
|---|---|---|---|---|
| **C1** | **non démontré** | non démontré | M1, à résolution `< 0,485 s` | **C** (validité) **et A** (satisfaisabilité) |
| **C2** | oui, si M2 et ≥ 100 intervalles | oui | M2 + référence T0-C | aucune |
| **C3** | oui | oui | M5 | aucune |

```
U-1 inconnue
   → T0-B = INDÉTERMINÉ
      → condition 4 de T0 GO non satisfaite
         → branche C
            → W4-F2 NON QUALIFIABLE
```

**`C1` n'est pas bloquée par une source manquante : elle l'est en amont, au
niveau de sa validité.** Rendre M1 calculable ne débloquerait rien tant que U-1
reste inconnue. Inversement, caractériser U-1 ne rend pas `C1` calculable : V-4
subsiste, et T0-A le traite.

---

## 10. Recherche d'une sortie sans code — dans l'ordre prescrit

1. **Preuve déjà dans le dépôt ?** Non. Les 59 lignes de `docs/design/`
   mentionnant `vcontrold` décrivent son rôle, sa version, ses durées observées —
   **jamais** son traitement des clients concurrents.
2. **Preuve amont documentée ?** **Partiellement, et non consultée depuis cette
   session.** `PREUVE EXTERNE REQUISE` pour la part amont ; le résidu
   d'installation reste hors de portée d'un lot documentaire (§7).
3. **Mesure dérivable d'une source existante ?** Non (§8).
4. **Analyse locale hors terrain ?** Oui, en subsidiaire encadré (§11.4).
5. **Instrumentation ?** **Non justifiée.** Elle mesurerait des durées sans
   répondre à la question posée.

> On n'ajoute pas de code pour mesurer ce qu'une preuve existante permet
> d'établir — et encore moins pour mesurer ce qu'aucune mesure ne peut établir.

---

## 11. Le lot proposé

### 11.1 Identité et objectif

> **W4-F1A — caractérisation de la composante amont de U-1.**

**Pré-W4-F2**, et le restant : W4-F2 conserve intégralement sa définition —
terrain en lecture seule, autorisation humaine distincte, T0/T1/T2 selon W4-F1.

**Objectif, énoncé exactement :**

> caractériser, **sans terrain**, la composante amont de **U-1** sur la
> **population des sondes du superviseur**, en **séparant** les faits amont des
> dépendances d'installation, afin de déterminer **quel prochain besoin doit être
> instruit** avant toute possibilité de `T0 GO`.

L'objectif n'est **pas** de « rendre la valeur que T0-B doit produire » : le §5
l'interdit.

### 11.2 Entrées

Chaîne de version du client (C5 §2) et contexte d'installation (C5 §1) · W2
§15.2, §15.3, §32.1 (I1) · W4-F1 §6.5, §8.2, §8.2.1, §8.5, §9 (U-1) · W4-C §8,
§9.1 · la règle de décision du §6 · la frontière du §7.

### 11.3 Voie 1 — amont, principale

Lecture du source de `vcontrold` à la version amont identifiée : boucle
d'acceptation, création de processus ou de fils, exclusion et sa **granularité**,
file éventuelle, exclusion en aval vers la liaison série, et **dépendance de ce
modèle aux options de construction et aux arguments d'invocation** (§7.2).

### 11.4 Voie 2 — subsidiaire, et strictement encadrée

> **Le « démon factice » de la V1 est retiré.** C5 avait déjà écarté la
> simulation qui fabrique elle-même le fait recherché ; un simulateur dont la
> logique encode la conclusion ne prouve rien.

| | |
|---|---|
| **Interdit comme preuve** | simulateur conçu pour reproduire un comportement supposé · double dont la logique encode la conclusion |
| **Autorisé** | **le source amont réel, compilé localement**, hors terrain · un environnement local · un adaptateur minimal destiné uniquement à rendre l'amont exécutable · un harnais jetable qui **observe** l'amont sans définir le résultat |

Conditions cumulatives : compiler un logiciel tiers est permis **comme outil
d'analyse hors dépôt** · **aucun code Boilerack** · **aucun artefact livré** ·
**aucun changement du dépôt** · procédure documentée · nettoyage complet · valeur
probatoire **limitée aux seules propriétés réellement exercées**.

Si ce niveau de reproduction n'est pas nécessaire, la voie 2 reste **non
utilisée**.

### 11.5 Exigence normative de preuve rejouable

> **Clause.** Le rapport de W4-F1A **MUST** porter les dix-sept éléments
> suivants. Ce n'est pas une recommandation de présentation : une preuve qu'un
> auditeur ne peut pas rejouer n'est pas une preuve.

| # | Élément |
|---|---|
| 1 | amont exact |
| 2 | URL |
| 3 | étiquette ou commit **complet** |
| 4 | fichiers |
| 5 | lignes ou symboles |
| 6 | options de construction pertinentes |
| 7 | options d'exécution et d'invocation |
| 8 | plateforme, ou hypothèses de plateforme |
| 9 | population étudiée |
| 10 | chaîne causale, **maillon par maillon** (§6.2) |
| 11 | faits amont **séparés** des hypothèses d'installation |
| 12 | procédure de toute reproduction locale |
| 13 | artefacts employés |
| 14 | résultats |
| 15 | limites |
| 16 | verdict, **conditionnel ou inconditionnel** |
| 17 | ce qui reste inconnu |

### 11.6 Hors périmètre — explicitement

Terrain sous toutes ses formes · Pi · réseau local · broker · `vclient` réel ·
chaudière · Optolink · service systemd · déploiement · installation ·
instrumentation · modification de l'ordonnanceur · exposition de paramètres ·
**toute modification de W4-F0 ou W4-F1** · toute autorisation W4-F2 · T0, T1, T2 ·
V-5, et la part installation de V-4, qui restent du terrain.

**Et, tant que le régime n'est pas caractérisé** : ni le remède de V-2, ni celui
de V-3.

### 11.7 Sorties attendues

Six sorties, dont deux — la **4** et la **5** — **dépendent du niveau épistémique
atteint** (§11.8) et ne s'écrivent pas de la même façon selon les cas.

1. la **valeur de régime** si elle est établie — `ADDITIF` ou `NON ADDITIF` —
   avec son **niveau de preuve** (§11.8) ;
2. la **preuve rejouable** au sens du §11.5 ;
3. la liste des **hypothèses d'installation** subsistantes, et **quel acte futur
   devra les établir** ;
4. la désignation du **besoin suivant**, **selon le §11.7.1** — jamais autrement,
   et **sans jamais l'ouvrir** ;
5. la **note de statut** `U-1` / `I1`, **selon le §11.7.2** ;
6. le rappel explicite que **rien de tout cela ne vaut verdict T0-B** (§5).

#### 11.7.1 Le besoin suivant dépend du niveau atteint

> **Clause.** Désigner V-2 ou V-3 comme prochain acte n'est légitime **que** si le
> régime est prouvé **inconditionnellement**. Dans les deux autres cas, le
> prochain acte porte sur ce qui manque, non sur le remède.

| Niveau atteint | Besoin suivant à désigner |
|---|---|
| **`PROUVÉ INCONDITIONNELLEMENT`** | **V-2** si `ADDITIF` · **V-3** si `NON ADDITIF` — sans l'ouvrir, sans modifier W4-F1, sans effet sur T0-B |
| **`PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION`** | **l'acte minimal nécessaire pour établir ou réfuter `H1..Hn`** |
| **`INDÉTERMINÉ`** | **la preuve supplémentaire minimale** susceptible de réduire l'indétermination, **si une telle preuve est identifiable** |

> **Cas conditionnel — ne pas désigner V-2 ou V-3 comme prochain acte.** Le lot
> **PEUT** rappeler quel remède s'ensuivrait **si** les hypothèses étaient
> ultérieurement établies, mais uniquement comme **conséquence conditionnelle**.
> L'écrire comme prochain acte reviendrait à traiter un verdict conditionnel
> comme un verdict — ce que le §7.3 interdit.

> **Cas `INDÉTERMINÉ` sans preuve hors terrain disponible.** Si aucune preuve
> supplémentaire n'est identifiable sans terrain, alors : le lot reste un **GO
> documentaire** (§11.9) · le résultat reste **`INDÉTERMINÉ`** · **aucune suite
> terrain n'en découle automatiquement** · et la décision d'engager quoi que ce
> soit reste **un acte humain séparé**.

#### 11.7.2 Le statut `U-1` / `I1` se dérive, il ne se choisit pas

> **Clause.** La note de statut **MUST** être déduite du niveau épistémique par la
> table ci-dessous. Elle **MUST NOT** être formulée librement.

| Niveau atteint | Statut `U-1` | Statut `I1` |
|---|---|---|
| **`PROUVÉ INCONDITIONNELLEMENT`** | `U-1 CLOSED` | `I1 PARTIELLEMENT RÉDUITE` |
| **`PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION`** | `U-1 — PART AMONT ÉTABLIE SOUS H1..Hn, RÉSIDU D'INSTALLATION OUVERT` | `I1 PARTIELLEMENT RÉDUITE` |
| **`INDÉTERMINÉ`** | `U-1 OUVERTE` | `I1 OUVERTE` |

> **Pourquoi trois états et non deux.** La V2 n'en proposait que deux —
> `U-1 CLOSED` ou U-1 maintenue — et aucun ne convenait au cas conditionnel : le
> premier **sur-ferme**, puisqu'un résidu d'installation subsiste ; le second
> **sous-estime** un travail amont réellement acquis. Le libellé intermédiaire
> porte les trois faits qu'il doit porter : **ce qui est acquis**, **ce qui reste
> ouvert**, et que **`I1` demeure plus large** (§4.1).

> **`U-1 CLOSED` ne s'écrit jamais sous hypothèses.** C'est la conséquence
> directe du §7.3 : un verdict conditionnel n'est pas un verdict, et une
> fermeture conditionnelle n'est pas une fermeture.

> **`I1` n'est jamais déclarée fermée.** Aucune ligne de la table ne le permet.
> Robustesse, erreurs, refus, corruptions éventuelles et signatures d'échec
> restent ouverts, sauf preuve spécifique qui n'est pas demandée à ce lot (§4.1).

### 11.8 Deux niveaux de sortie, à ne pas confondre

**Niveau épistémique** — ce que le lot hors terrain a pu établir :

| Niveau | Sens |
|---|---|
| `PROUVÉ INCONDITIONNELLEMENT` | aucune hypothèse d'installation nécessaire |
| `PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION` | conclusion valide sous `H1..Hn`, énoncées |
| `INDÉTERMINÉ` | ni l'un ni l'autre — c'est-à-dire, exactement, le §6.4 |

**Valeur du régime**, si un niveau prouvant est atteint : `ADDITIF` ou
`NON ADDITIF`. Au niveau `INDÉTERMINÉ`, **aucune valeur de régime n'est émise**.

Une sortie s'écrit donc, par exemple : **`ADDITIF — CONDITIONNEL À H1/H2/H3`**.

> **Ce qu'une telle sortie vaut, et ne vaut pas.** Elle ferme éventuellement la
> **part amont** de U-1. Elle **ne vaut pas** verdict T0-B, **ne vaut pas**
> `T0 GO`, et **ne vaut pas** autorisation W4-F2.

### 11.9 GO / NO-GO

> **Le critère porte sur la méthode, jamais sur le verdict obtenu.** Un lot dont
> l'issue honnête est `INDÉTERMINÉ` a rempli sa mission s'il l'a établi
> proprement : il a produit ce qu'on lui demandait — **savoir où l'on en est**.
> Exiger `ADDITIF` ou `NON ADDITIF` reviendrait à récompenser la conclusion
> plutôt que la rigueur, et donc à encourager la conclusion de trop.

> **`GO W4-F1A`** si et seulement si **toutes** ces conditions sont réunies :
>
> 1. la **population** est correctement fixée (§6.1) ;
> 2. la **source** est correctement caractérisée ;
> 3. la **règle de décision** du §6 est **réellement appliquée** ;
> 4. le **niveau épistémique** est correctement attribué (§11.8) ;
> 5. les **hypothèses d'installation** sont listées ;
> 6. les **limites** sont explicites ;
> 7. le **statut `U-1` / `I1`** est rendu conformément au §11.7.2 ;
> 8. le **besoin suivant** est désigné **selon le niveau atteint** (§11.7.1) ;
> 9. **aucun glissement vers T0-B** n'a eu lieu (§5).
>
> Aucune de ces neuf conditions n'exige un `ADDITIF` ou un `NON ADDITIF`
> inconditionnel. **Les trois niveaux du §11.8 sont compatibles avec un `GO`.**

> **`NO-GO W4-F1A`** si l'une de ces situations se présente : l'amont est ambigu ·
> le démon n'est pas identifiable · la population n'est pas isolable · la
> causalité n'est pas démontrable · source et exécution ne peuvent pas être
> séparées · la conclusion dépend d'hypothèses qu'on ne sait pas même énoncer.

> **`INDÉTERMINÉ` n'est pas un `NO-GO`, et les deux ne se confondent pas.**
> `INDÉTERMINÉ` est un **résultat** rendu par une méthode correctement conduite ;
> `NO-GO` est un **défaut de méthode**. Un lot peut donc être `GO` en rendant
> `INDÉTERMINÉ`, et `NO-GO` en rendant `ADDITIF` mal étayé. Rendre `INDÉTERMINÉ`
> laisse simplement U-1 au terrain, d'où W2 l'avait classée, pour un coût nul :
> aucune exposition, aucun code.

### 11.10 Besoin de code, besoin de terrain

| | |
|---|---|
| **code de production** | **NON** |
| **test de production** | **NON** |
| **configuration** | **NON** |
| **instrumentation** | **NON** |
| **terrain** | **NON** |
| accès à une source externe | **oui**, hors terrain |
| compilation d'un tiers hors dépôt | possible en voie 2, encadrée par §11.4 |

---

## 12. Le journal — amont et installation

`V-4` n'est pas purement terrain, contrairement à ce que la V1 laissait entendre.

| Part | Contenu | Qui l'établit |
|---|---|---|
| **amont** | ce que le source journalise · les événements prévus · le format prévu · le niveau · l'identité disponible · l'ouverture et la fermeture lorsqu'elles sont émises | **W4-F1A**, voie 1 |
| **installation** | niveau de journalisation réellement activé · format réellement produit · résolution effective · rotation · conservation · horodatage réel · possibilité effective d'attribution | **T0-A**, terrain |

> **La part installation reste décisive.** Même un source qui journalise
> ouverture, fermeture et identité ne garantit pas que l'installation les
> produise, ni à une résolution satisfaisant `r < 0,485 s` (W4-F1 §8.5). W4-F1A
> peut réduire l'incertitude ; il ne peut pas la lever.

---

## 13. Observation réservée — à n'ouvrir que si le régime est `ADDITIF`

Si la branche A devient un jour opératoire, le lot de V-2 rencontrera une
question de modélisation, consignée ici pour qu'elle ne se perde pas, et
**délibérément non instruite** :

> L'intervalle `2 669 – 4 029 ms` de C5 est mesuré « production active »,
> c'est-à-dire **déjà sous contention** avec le pont. W4-F1 §8.5 l'emploie à deux
> titres dans la même soustraction : comme **occupation de Boilerack** et comme
> **coût propre de la sonde du superviseur**. Savoir si ces deux emplois sont
> légitimes, ou si la grandeur pertinente est le **délai marginal** ajouté par
> Boilerack, est une question ouverte.

> **Elle n'est pas tranchée ici, et ce n'est pas un oubli.** W4-F1 est **CLOSED**
> et son contrat fait autorité. Rouvrir un contrat clos sur une objection de
> modélisation, avant même de savoir si la branche qui la rend pertinente
> s'applique, serait l'inverse de la méthode suivie jusqu'ici.

---

## 14. Séquencement — ce que ce lot change, et ce qu'il ne change pas

| Énoncé | Statut |
|---|---|
| U-1 est le **premier discriminant** utile | **vrai** — il décide entre V-2 et V-3, exclusifs |
| U-1 est le **premier déblocage** | **faux** — le caractériser ne produit aucun `T0 GO` |
| U-3 et V-4 dépendent de U-1 | **faux** — indépendants, et traités par T0-A |
| les conditions 1, 2, 3 et 5 de `T0 GO` dépendent de U-1 | **faux** — indépendantes |
| **après un W4-F1A réussi, W4-F2 reste FERMÉ** | **vrai**, sans exception |

> **La valeur de ce lot est de choisir la suite, pas de l'autoriser.** Il évite de
> construire V-2 ou V-3 au hasard, et il le fait sans exposition, sans code et
> sans toucher au terrain. C'est tout ce qu'il prétend faire.

---

## 15. Ce que ce document ne fait pas

- il n'ouvre **aucun** lot : il en cadre un ;
- il ne modifie **ni** W4-F0 **ni** W4-F1, qui restent **CLOSED** et intacts ;
- il ne modifie **aucun** code, test ni configuration ;
- il ne crée **aucune** instrumentation ;
- il ne demande ni n'accorde **aucune** autorisation terrain ;
- il ne conduit **aucune** mesure sur l'installation ;
- il ne rend **aucun** verdict sur U-1, ni **a fortiori** sur T0-B : il définit
  qui doit rendre quoi, et sous quelles conditions.

**W4-F2 reste FERMÉ. Le pont historique reste l'unique écrivain réel de
production.**
