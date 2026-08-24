# W4-F1 — Fenêtre de confirmation et critère de coexistence

> **Sous-lot W4-F1 — analyse et critère. Version 3**, après audit delta de la V2.
> Quatre majeurs corrigés : `C1` reposait sur un **quantile** là où la garantie est
> une **borne** (§8.5) ; la cadence de 30 s ignorait la **latence de libération**
> de la liaison (§8.6.1, §8.6.2) ; `E7` avait perdu sa conséquence d'arrêt
> immédiat (§8.6.3) ; et la barrière T0 pouvait autoriser T1 alors que l'analyse
> concluait STOP (§8.2.1). Deux mineurs : `C2` est requalifiée en **politique**
> assumée (§8.5), et la résolution de la source de `C1` devient une exigence
> normative (§8.5). Le modèle temporel des §3 à §5 et l'analyse des rafales du §6
> sont **inchangés** : l'audit les a validés.
>
> Sous-lot **NON TERRAIN**. Aucun accès au Pi, au broker, à `vclient` ou à la
> chaudière. Aucun service touché, aucun déploiement, aucune écriture. Ce
> document ne livre **aucune ligne de code** et ne modifie aucun test.
>
> Autorité amont : `w4f-write-sovereignty.md` §10.2 (mission) et §10.3.3 (forme
> du critère attendu). **W4-F2 reste fermé.** Aucune autorisation terrain n'est
> demandée ni accordée ici.

W4-F0 confie à ce sous-lot deux livrables : répondre aux cinq questions sur la
fenêtre de confirmation, et **figer le critère quantitatif falsifiable** que
W4-F2 appliquera. La règle qui l'impose est celle-ci — *celui qui mesure ne doit
pas fixer après coup le seuil qui le juge*.

---

## 1. Convention

Les marqueurs de site sont ceux de W4-C §4 et de W4-F0 §2, sans ajout :
`<hôte>`, `<port>`, `<unité-pont>`, `<timer-guard>`, `<unité-boilerack>`.

Notation employée dans les formules :

| Symbole | Sens |
|---|---|
| `D` | `confirm_budget_s` — échéance de la boucle |
| `I` | `confirm_interval_s` — attente **maximale** entre deux relectures |
| `R` | durée réelle d'une relecture, bornée par `read_timeout_s + ε` |
| `N` | nombre de relectures effectuées |
| `W` | fenêtre d'observation effective |

---

## 2. Sources de vérité

| Sujet | Source réelle | Fait établi |
|---|---|---|
| `confirm_budget_s` | `core/engine.py` — `DEFAULT_CONFIRM_BUDGET_SECONDS` | `5.0` |
| `confirm_interval_s` | `core/engine.py` — `DEFAULT_CONFIRM_INTERVAL_SECONDS` | `0.5` |
| ce que la composition transmet | `transaction_wiring.py`, appel `TransactionalCore(...)` | **seuls** `queue_capacity` et `ack_topic_prefix` ; les budgets retombent sur leurs défauts |
| `read_timeout_s` | `adapters/config.py` ; `config.py` `_CLES_VCLIENT` ; C10 table `[vclient]` | `5.0`, **clé publique**, réglable par l'utilisateur |
| sémantique de `_confirm` | `core/engine.py` | échéance testée **après** chaque relecture |
| horloge de production | `lifecycle.py` — `WakeupClock.sleep` | attente **interruptible par tout signal** |
| plafond de sous-processus | `adapters/process_runner.py` → `subprocess.run(timeout=…)` | sur `TimeoutExpired` : `kill()` puis `wait()` |
| coût d'une lecture réelle | C5 §9, « Contention et durées » | **2 669 à 4 029 ms**, production active |
| budget du dispositif historique | W4-C E4 | 1 s d'attente, sondages 1 s, budget 10 s |
| cadence du pont | W4-C §9 étape 6 | sonde le démon toutes les 10 s |
| superviseur | W4-C §8 | cycle 3 min, budget 5 s, **deux échecs ⇒ redémarrage machine** |
| surface de lecture | `read_surface/measurements.py`, `publisher.py` | 8 mesures, 3 à 30 s et 5 à 60 s, **une invocation par mesure** |
| amorçage des échéances | `publisher.py`, `start()` | `self._next_due = {role: maintenant …}` — **les 8 sont dues ensemble** |
| avancement des échéances | `publisher.py`, `run_due()` | `monotonic() + period_s` — **sans rattrapage**, repart de la fin |
| observabilité Boilerack | `read_surface/snapshot.py` | `age_s`, `fresh`, `has_value`, `last_result`, `chain.status`, `chain.cause` |
| trace tierce | W4-C §9.1 | le journal du démon `vcontrold` **horodate chaque connexion cliente** — et **rien de plus n'est établi** (§8.3) |
| preuve de santé du pont | W4-C §13.1 | trois niveaux **A** processus vivant · **B** sonde le démon · **C** **publie** |
| interdiction d'inférence sur le superviseur | W4-C §9.1 | l'absence de connexion du superviseur au journal est **exactement** ce qu'on observerait dans le cas le plus dangereux |

---

## 3. Q1 — Les constantes qui gouvernent réellement la fenêtre

W4-F0 en nommait trois. Le code en révèle **cinq**.

| # | Paramètre | Origine | Consommé par | Valeur |
|---|---|---|---|---|
| 1 | `confirm_budget_s` | défaut du cœur | `_confirm`, échéance | `5.0` |
| 2 | `confirm_interval_s` | défaut du cœur | `_confirm`, attente | `0.5` |
| 3 | `read_timeout_s` | `VclientConfig`, clé publique | `SubprocessRunner.run` | `5.0` |
| 4 | **sémantique de `Clock.sleep`** | `WakeupClock`, composé par `lifecycle` | `_confirm`, attente | interruptible |
| 5 | **coût hors plafond `ε`** | `subprocess.run` — amont et aval du délai | plafond réel d'une relecture | non borné formellement |

Les deux dernières n'étaient pas nommées, et elles ont un effet réel.

**#4 — l'attente n'est pas fixe.** En production, l'horloge remise à
`build_runtime` est `WakeupClock`, dont `sleep()` « rend la main à l'expiration de
la durée demandée, **ou dès qu'un octet est disponible** » sur le descripteur de
réveil — y compris pour un **signal étranger**, cas que sa propre docstring
prévoit. `confirm_interval_s` est donc un **majorant**, non une constante :
`ι ∈ [0, I]`.

> **Conséquence.** Sous rafale de signaux, la boucle enchaîne les relectures sans
> attente. Cela **augmente** le nombre de relectures dans le budget et **réduit**
> la fenêtre — l'inverse d'un danger pour la concluance, mais une **charge accrue
> sur la liaison** au pire moment. Aucune écriture supplémentaire n'en découle :
> la cardinalité d'écriture est fixée hors de la boucle.

**#5 — `read_timeout_s` n'est pas exactement le plafond.** Le plafond réel d'une
relecture est `read_timeout_s + ε`, et `ε` a **deux composantes**, l'une avant le
compte à rebours et l'autre après.

| Composante | Moment | Contenu | Bornée ? |
|---|---|---|---|
| `ε_amont` | **avant** l'armement du délai | résolution de l'exécutable, création du processus, `fork`/`exec` ou équivalent, mise en place des tubes de capture | non mesurée ici |
| `ε_aval` | **après** expiration | `process.kill()` puis, hors Windows, `process.wait()` | **non bornée par le code** |

`subprocess.run` n'arme son délai que sur `communicate()` : tout ce qui précède
échappe au plafond. Et `wait()` après `kill()` n'a **aucun délai** : `SIGKILL` le
rend bref en pratique, mais le code ne le borne pas.

> **Portée exacte, et elle dépasse la boucle de confirmation.** `_confirm` ne
> s'exécute pas pendant W4-F2, donc `ε` n'y est pas un obstacle. Mais la
> **surface de lecture emploie le même `SubprocessRunner`** : chacune de ses huit
> invocations porte le même `ε`. C'est à ce titre, et non par la boucle de
> confirmation, que `ε` intervient dans l'analyse des rafales (§6).

> **Rectification de W4-F0 §4.2.1.** La borne y est écrite
> « strictement inférieure à `confirm_budget_s + confirm_interval_s +
> read_timeout_s` », soit 10,5 s. Elle omet `ε`. La borne exacte est
> **`D + I + read_timeout_s + ε`**. L'écart est de l'ordre de la milliseconde et
> ne change aucune conclusion ; il est consigné parce qu'une borne annoncée
> stricte doit l'être.

**Aucun autre paramètre n'intervient.** `terminal_ttl_s` (60 s) gouverne le cache
terminal, `queue_capacity` la file : ni l'un ni l'autre n'entre dans la fenêtre.
Vérifié sur la signature complète de `TransactionalCore.__init__`.

---

## 4. Q2 — Modèle temporel

### 4.1 Séquence exacte

Relevée dans `core/engine.py`, sans interprétation :

```
D_abs ← monotonic() + confirm_budget_s        # échéance posée UNE fois
boucle :
    relecture         (durée R, plafonnée par read_timeout_s + ε)
    comparaison métier (tolérance 0 pour un rôle entier : égalité exacte)
    si confirmée              → applied            ← SORTIE, sans test d'échéance
    si monotonic() ≥ D_abs    → timeout            ← test APRÈS la relecture
    attente ι ∈ [0, confirm_interval_s]
```

Trois propriétés en découlent, et elles sont structurelles :

1. **au moins une relecture a toujours lieu** — l'échéance n'est jamais testée
   avant ;
2. **une relecture entamée va à son terme** — rien ne l'interrompt ;
3. **`applied` peut être émis après l'échéance nominale** — la confirmation est
   testée avant l'échéance.

### 4.2 Formule

À coût de relecture constant `R` et attente pleine `ι = I`, la relecture `k` se
termine à `e_k = k·R + (k−1)·I`. La boucle s'arrête à la première relecture qui
confirme, ou à la première dont la fin atteint l'échéance :

```
N = ⌈ (D + I) / (R + I) ⌉          nombre de relectures si aucune ne confirme
W = N·R + (N−1)·I                   fenêtre d'observation effective
```

Bornes : `N ≥ 1` toujours, et `W < D + I + read_timeout_s + ε`.

### 4.3 Vérification — sonde jetable sur le moteur réel

Sonde entièrement hors ligne : `TransactionalCore` **réel**, profil de production
**réel**, `VirtualClock`, `FakeMqttClient`, et un `VClient` double dont chaque
relecture consomme du temps virtuel. Aucun réseau, aucun sous-processus, aucun
fichier du dépôt touché. Sonde supprimée après usage.

| `R` | `N` prédit | `N` mesuré | `W` prédite | `W` mesurée | écritures |
|---:|---:|---:|---:|---:|---:|
| 0,3 s | 7 | **7** | 5,1 s | **5,1 s** | 1 |
| 2,7 s | 2 | **2** | 5,9 s | **5,9 s** | 1 |
| 4,0 s | 2 | **2** | 8,5 s | **8,5 s** | 1 |
| 5,0 s | 1 | **1** | 5,0 s | **5,0 s** | 1 |

La formule concorde sur les quatre régimes. **Une seule écriture dans tous les
cas**, y compris lorsque la confirmation échoue : l'absence de réessai est
vérifiée sur le moteur réel, pas seulement lue dans une docstring.

### 4.4 Le fait qui compte, et que la durée masquait

W4-F0 comparait la fenêtre (8,5 s) au budget historique (10 s) et concluait
qu'ils étaient « du même ordre ». C'est vrai de la **durée**, et trompeur sur ce
qui décide.

| | Dispositif historique (E4) | Boilerack sous contention |
|---|---|---|
| fenêtre | ~10 s | 5,9 à 8,5 s |
| **occasions d'échantillonnage** | **~10** | **2** |

Le dispositif historique attendait 1 s puis sondait toutes les secondes : une
dizaine d'occasions de voir la valeur apparaître. Boilerack, sous contention, en
a **deux**. À budget comparable, la capacité de détection d'une propagation
tardive est cinq fois moindre.

> **Ce que cela n'est pas.** Ce n'est pas un danger : une fenêtre épuisée produit
> `timeout`, verdict terminal légitime, et aucune seconde écriture. C'est un
> risque de **concluance**, et il ne peut pas être levé ici : le délai de
> propagation `I-7` n'est mesurable qu'*au moment* de la première écriture
> réelle, qui appartient à W4-F4. **La circularité est réelle et doit être
> assumée, pas dissimulée par un réglage arbitraire.**

---

## 5. Q3 — `read_timeout_s`, exactement

| Aspect | Fait |
|---|---|
| nature | plafond passé à `subprocess.run(timeout=…)` **par invocation** |
| portée | **une relecture**, jamais la boucle |
| expiration | `ProcessResult(timed_out=True, returncode=None)` — issue **ambiguë**, jamais un échec de lancement |
| coût de sortie | `kill()` puis `wait()` — `ε` non borné formellement |
| effet métier | une lecture non `OK` **ne confirme rien** ; la boucle continue si l'échéance le permet |
| effet sur la sécurité | **aucun** — il ne gouverne aucune écriture ; le budget d'écriture est `write_timeout_s`, distinct |
| effet sur la concluance | **direct** — il fixe `R_max`, donc `N` par la formule §4.2 |
| réglabilité | **clé publique** `[vclient].read_timeout_s` |

> **Ne jamais confondre.** `read_timeout_s` borne **une relecture** ;
> `confirm_budget_s` borne **la boucle**. Les deux valent `5.0` aujourd'hui, et
> cette coïncidence numérique est le piège : elle rend `N = 1` dès que le coût
> atteint le plafond, alors qu'un plafond plus haut donnerait `N = 2`.

**Levier disponible, et son sens contre-intuitif.** *Augmenter* `read_timeout_s`
n'augmente pas `N` — la formule ne dépend du plafond que par `R`. *Diminuer*
`read_timeout_s` tronque les relectures coûteuses : sous contention à 2,7–4,0 s,
un plafond de 2 s ferait échouer **toutes** les lectures. Le seul réglage public
disponible ne peut donc pas améliorer la concluance ; il peut la détruire.

---

## 6. Découverte — la rafale de lecture, et le risque qu'elle fait peser

Cette section n'était pas prévue par W4-F0. Elle est apparue en instruisant
« coût réel de relecture », et elle change l'appréciation du risque de W4-F2.

### 6.1 Le mécanisme, lu dans l'ordonnanceur

Trois faits de `read_surface/publisher.py`, et rien d'autre :

1. `start()` pose `self._next_due = {spec.role: maintenant …}` — **les huit
   mesures sont dues au même instant** ;
2. `run_due()` **fige l'ensemble des dues** à l'entrée, puis les lit
   **séquentiellement** ;
3. après chaque tentative, l'échéance suivante vaut `monotonic() + period_s` —
   recalculée **à la fin de la tentative**, sans rattrapage.

Le runner rappelle ensuite `_attendre(due_at())`, qui **n'attend pas** si une
échéance est déjà atteinte : `run_due()` est alors rappelé **immédiatement**.

> **Conséquence : une rafale peut se réalimenter.** Si, pendant qu'un cycle se
> déroule, une mesure déjà servie redevient due avant la fin du cycle, l'appel
> suivant enchaîne **sans relâcher la liaison**. Le regroupement n'est donc pas
> borné par le nombre de mesures.

### 6.2 Le seuil de réalimentation, dérivé puis vérifié

La première mesure à 30 s d'un cycle est servie en position 1 : elle se termine à
`R` et redevient due à `R + 30`. Le cycle de huit se termine à `8R`. La rafale se
chaîne donc dès que :

```
R + 30 ≤ 8R      ⟺      R ≥ 30/7 ≈ 4,286 s
```

**Vérification sur l'ordonnanceur réel** — sonde jetable hors ligne, horizon
30 min virtuelles :

| Coût par lecture | Occupation | Rafale max | Lectures d'affilée | Chaînage |
|---:|---:|---:|---:|:--|
| 4,000 s | 65,3 % | 32,0 s | 8 | non |
| 4,250 s | 68,9 % | 34,0 s | 8 | non |
| **4,286 s** = 30/7 | 69,3 % | **47,1 s** | **11** | **OUI** |
| 4,500 s | 71,0 % | 49,5 s | 11 | OUI |
| 5,000 s | 78,6 % | 55,0 s | 11 | OUI |
| 6,000 s | 91,0 % | 72,0 s | 12 | OUI |
| **8,000 s** | **100 %** | **1 720 s** | **215** | **saturation** |

La transition est **nette** au seuil dérivé : 8 lectures à 4,250 s, onze à
4,286 s. À 8 s, la liaison n'est **jamais relâchée** sur tout l'horizon simulé.

> **Proximité à consigner.** Le maximum documenté par C5 est **4,029 s**. Le
> seuil de réalimentation est à **0,257 s** au-dessus. Le régime de contention
> mesuré sur cette installation frôle donc le point où le comportement change de
> nature.

### 6.3 Rectification de W4-F1 V1

> **La borne « `8 × read_timeout_s` » était fausse**, et le calcul qui en
> découlait — un plafond de 0,625 s qui ramènerait la rafale sous 5 s — est
> **retiré**. La table de la V1 le contredisait déjà elle-même : elle portait
> onze lectures et 55 s au régime 5,0 s. Aucun facteur constant ne borne la
> rafale ; au-delà de `30/7`, elle n'est bornée que par la saturation.

**La conclusion sur les leviers de configuration est inchangée, et renforcée.**

- les périodes des mesures **ne sont pas exposées** — C10 classe
  `RuntimeConfig.specs` en « surface interne fermée » ;
- `snapshot_period_s` et `heartbeat_period_s` ne gouvernent aucune invocation
  `vclient` ;
- `read_timeout_s` ne borne **pas** la rafale : au-delà de `30/7` il ne fait que
  déplacer le régime, et l'abaisser sous les coûts réels ferait échouer toutes
  les lectures.

Il n'existe donc **aucun levier de configuration public**. La protection ne peut
venir que du protocole (§8).

### 6.4 Ce que ces chiffres sont, et ne sont pas

> Toutes les valeurs des §6.2 sont des **projections hors ligne** obtenues en
> pilotant l'ordonnanceur réel avec une `VirtualClock`. Elles décrivent
> exactement ce que le code fait pour un coût de lecture donné. Elles ne sont
> **pas** des observations de terrain, et elles ne disent rien du coût réel que
> présentera l'installation avec Boilerack actif.

### 6.5 L'hypothèse dont tout dépend

Le superviseur sonde le démon toutes les 3 minutes avec un budget de **5 s**, et
**deux sondes en échec conduisent à un redémarrage machine** (W4-C §8). Une
rafale ne met le superviseur en difficulté **que si** un accès de Boilerack
**retarde** un accès concurrent.

> **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE` — U-1.** Le dépôt ne contient
> **aucune** description du comportement de `vcontrold` face à des clients
> concurrents : ni sérialisation, ni file, ni entrelacement. C5 intitule sa
> section « **Contention et durées** » et mesure 2 669 à 4 029 ms « production
> active », ce qui **suggère** une ressource disputée — cela ne l'établit pas.

**Le régime additif, énoncé pour pouvoir être réfuté.** Appelons *additif* le
régime où une transaction arrivant pendant une occupation attend sa libération,
puis paie son propre coût. Sous ce régime, et sous lui seul, les seuils du §8.5
s'appliquent. Si `vcontrold` entrelace ou parallélise, ils sont sans objet.

**Ce que le régime additif impliquerait, arithmétiquement.**

| Grandeur | Valeur | Source |
|---|---:|---|
| budget du superviseur | 5,000 s | W4-C §8 |
| coût d'une transaction, minimum | 2,669 s | C5 §9 |
| coût d'une transaction, maximum | 4,029 s | C5 §9 |
| attente tolérable, cas favorable | **2,331 s** | `5,000 − 2,669` |
| attente tolérable, cas défavorable | **0,971 s** | `5,000 − 4,029` |

Une lecture de Boilerack coûte, dans la même plage, **2,669 à 4,029 s**. Sous le
régime additif, **une seule lecture en cours dépasse déjà l'attente tolérable**,
avant même qu'il soit question de rafale. Le problème des rafales est réel mais
**second** : le premier est qu'une transaction unique occupe presque tout le
budget d'une autre.

> **Ce constat n'est pas une conclusion terrain.** Il dit : *si* le régime est
> additif, *alors* la coexistence est arithmétiquement impossible aux coûts
> documentés. Établir le régime est le travail de **T0** (§8.2), et c'est
> pourquoi T0 précède toute exposition.

---

## 7. Q4 — Faut-il modifier le logiciel avant W4-F2 ?

### 7.1 Options examinées

| Option | Verdict | Motif |
|---|---|---|
| aucune modification | **retenue, sous condition** | §7.2 |
| ajuster `read_timeout_s` | rejetée | ne borne pas la rafale (§6.3) et ne peut qu'aggraver la concluance (§5) |
| exposer `confirm_budget_s` | **prématurée** | la boucle ne s'exécute pas en W4-F2 |
| exposer `confirm_interval_s` | **prématurée** | idem |
| modifier la sémantique de `_confirm` | rejetée | aucune impossibilité démontrée ; toucherait le cœur |
| échelonner les échéances de lecture | **non instruite ici** | §7.3 |

### 7.2 Verdict, et sa condition

> **AUCUN CHANGEMENT LOGICIEL N'EST ACTUELLEMENT DÉMONTRÉ NÉCESSAIRE AVANT
> W4-F2.**
>
> **Condition suspensive.** Ce verdict vaut tant que **T0** n'a pas conclu. T0
> doit établir deux choses : que les sources existantes permettent réellement de
> calculer les critères du §8.5, et quel régime de concurrence `vcontrold`
> présente. Si T0 montre que les critères ne sont **pas calculables**, ou que le
> régime est **additif**, alors W4-F2 ne progresse pas vers T1, et le besoin
> éventuel — instrumentation, ou échelonnement de l'ordonnanceur — devient un
> **lot à instruire** avant toute reprise.

Deux raisons soutiennent le verdict lui-même.

**La boucle `_confirm` ne s'exécute jamais pendant W4-F2** — la voie
transactionnelle y est fermée. Les paramètres 1, 2 et 4 du §3 sont sans effet sur
ce sous-lot. Exposer un budget qu'aucun code n'exécutera serait du confort
d'exploitation, que W4-F0 §10.2 refuse comme motif d'ouvrir du code.

**Le risque du §6 doit être mesuré avant d'être corrigé.** Il repose sur U-1, que
le dépôt ne tranche pas. Modifier l'ordonnanceur maintenant reviendrait à
corriger un défaut **supposé** — exactement la faute que la méthode proscrit.

> **Ce verdict ne promet pas qu'aucun code ne sera jamais nécessaire.** Il dit
> qu'aucun n'est **démontré** nécessaire aujourd'hui, et il désigne T0 comme
> l'étape qui peut renverser ce constat sans aucune exposition.

### 7.3 Ce que ce verdict n'autorise pas

W4-F0 décrivait W4-F2 comme un lot de qualification. Le §6 montre qu'il est
**matériellement plus risqué** : sous le régime additif, il peut conduire à un
redémarrage machine.

> **Clause.** W4-F2 **MUST NOT** être conduit comme une observation longue lancée
> puis laissée courir. Le §8 impose une progression **T0 → T1 → T2** avec deux
> barrières normatives, et une évaluation de `C1` **pendant** T1.

Un sous-lot logiciel — échelonnement des échéances de lecture — n'est **pas**
ouvert par ce document.

---

## 8. Q5 — Le protocole et le critère que W4-F2 appliquera

### 8.1 Principe

W4-F2 ajoute Boilerack à un système qui fonctionne. **Le dispositif historique
est la référence de sécurité.** Le succès n'est pas « Boilerack arrive à lire »,
mais :

> Boilerack démontre qu'il coexiste **sans dégrader le dispositif historique
> au-delà d'une limite fixée avant l'essai**.

Trois phases, deux barrières normatives, et **aucun seuil choisi après
observation** — hormis les valeurs que des formules figées ici prennent en
entrée depuis T0.

```
T0  référence, Boilerack ARRÊTÉ
    ↓  barrière T0 : GO, ou W4-F2 NON QUALIFIABLE
T1  exposition courte, bornée
    ↓  barrière T1 : GO, ou W4-F2 NON QUALIFIÉ
T2  observation longue
    ↓  QUALIFIÉ / NON QUALIFIÉ
```

### 8.2 T0 — référence et caractérisation, sans aucune exposition

Boilerack est **arrêté**. T0 ne présente donc **aucun risque nouveau**, et c'est
ce qui permet de lui confier tout ce qui peut s'apprendre sans exposer
l'installation.

**T0-A — caractériser les sources.** Le dépôt établit seulement que le journal
`vcontrold` **horodate chaque connexion cliente** (W4-C §9.1). Il n'établit ni
clôture de connexion, ni durée, ni attribution par client. T0-A doit donc
déterminer, sur le journal réel :

1. son format et sa résolution temporelle ;
2. la présence ou l'absence d'un événement d'**ouverture** et d'un événement de
   **clôture** ;
3. la présence ou l'absence d'un attribut permettant de **distinguer les
   clients** ;
4. la cadence et la résolution réellement atteignables sur M2, M3, M4, M5 ;
5. la liste des métriques **effectivement calculables** qui en résulte.

> **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`.** Tant que T0-A n'a pas conclu, la
> calculabilité de `C1` est **inconnue**. Elle n'est pas supposée.

**T0-A désigne aussi les sources retenues** : celle qui servira à `C1`, celle qui
servira à `C2`, et celles qui serviront aux événements E1–E6 et E8. Les noms
`M1`…`M5` du §8.3 sont des étiquettes de travail ; c'est T0-A qui dit quelle
source réelle joue chaque rôle, et la règle de résolution du §8.5 porte sur la
source **effectivement retenue**, non sur l'étiquette.

**T0-B — la concurrence déjà présente.** Le pont et le superviseur coexistent
depuis des mois. Si, et seulement si, T0-A montre que le journal porte ouverture
**et** clôture **et** distinction des clients, T0-B examine leurs recouvrements
et en déduit le régime de concurrence de `vcontrold` — U-1, sans exposer
Boilerack. Si les données ne le portent pas, T0-B rend **`INDÉTERMINÉ`** :
aucune inférence n'est tirée d'une donnée absente, et l'absence de conclusion est
elle-même une conclusion consignée.

**T0-B rend un verdict, jamais un silence.** Son résultat **MUST** être l'une des
trois valeurs suivantes, explicitement écrite :

| Verdict T0-B | Sens |
|---|---|
| **`ADDITIF`** | une transaction concurrente attend la libération, puis paie son propre coût |
| **`NON ADDITIF`** | `vcontrold` entrelace, parallélise, ou présente un autre régime |
| **`INDÉTERMINÉ`** | les sources ne permettent pas de conclure |

Aucune valeur par défaut. Ne pas conclure **est** `INDÉTERMINÉ`, et cela se
consigne.

**T0-C — référence statistique.** Distribution des intervalles de publication du
pont vue d'aval (M2), sur une fenêtre de durée `Δ`. Les quantiles `p50(T0)` et
`p95(T0)` en sont extraits ; ils alimentent `C2` (§8.5) et `E3` (§8.6). T0-C
établit en outre, **et seulement si la population des sondes du superviseur est
réellement isolable** (T0-A), une borne supérieure de leur coût — jamais une
borne tirée d'un mélange pont/superviseur.

**T0-D — calculabilité, résolution, et temps de réaction.** Décider
explicitement, avant toute exposition :

1. `C1` est-elle calculable, et la **résolution** de sa source satisfait-elle la
   règle du §8.5 ?
2. `C2` est-elle calculable, et la dispersion de T0-C permet-elle une politique
   crédible (§8.5) ?
3. `C3` est-elle calculable ?
4. les événements E1–E8 sont-ils détectables **à la cadence** exigée (§8.6) ?
5. la **latence de libération** est-elle bornée, et le budget de 90 s du §8.6
   laisse-t-il un temps de réaction humaine que l'exploitant déclare tenable ?

### 8.2.1 Barrière T0 — trois branches exclusives

La barrière ne porte pas seulement sur la calculabilité : elle porte aussi sur la
**validité du contrat `C1` lui-même**, qui n'a de sens que sous un régime donné.

| Branche | T0-B | Conséquence normative |
|---|---|---|
| **A** | `ADDITIF` | `C1` est valide **et** arithmétiquement inatteignable aux coûts documentés (§6.5). **`W4-F2 NON QUALIFIABLE — STOP`. Aucun T1.** |
| **B** | `NON ADDITIF` | `C1` additive **n'est pas applicable**. Elle doit être remplacée par un contrat documentaire adapté, **avant T1**, et ce remplacement **exige un nouvel audit**. Tant qu'il n'existe pas : **`T0 NO-GO — STOP`.** |
| **C** | `INDÉTERMINÉ` | la validité de `C1` n'est **pas démontrée**. **`W4-F2 NON QUALIFIABLE — STOP`. Aucun T1.** |

> **Pourquoi la branche A conduit à `NON QUALIFIABLE` et non à `NON QUALIFIÉ`.**
> Les deux termes ne disent pas la même chose. `NON QUALIFIÉ` signifie *la
> coexistence a été éprouvée et elle échoue* ; `NON QUALIFIABLE` signifie *elle
> ne peut pas être jugée en l'état*. En branche A, rien n'a été éprouvé : c'est
> l'arithmétique, avant toute exposition, qui montre que la configuration
> actuelle ne peut pas satisfaire `C1`. Le mot juste est donc
> `NON QUALIFIABLE` — et la suite appartient à un lot qui changerait la
> configuration, non à une mesure.

> **`T0 GO`** si et seulement si **toutes** ces conditions sont réunies :
>
> 1. `C1`, `C2` et `C3` sont calculables avec les sources existantes ;
> 2. la résolution de la source de `C1` satisfait la règle du §8.5 ;
> 3. les cadences et le budget de réaction du §8.6 sont atteignables ;
> 4. **T0-B a rendu un régime compatible avec le contrat `C1` actuellement
>    figé** — ce qui, aujourd'hui, exclut les trois branches ci-dessus ;
> 5. aucune inconnue structurante ne rend le critère invalide.
>
> Sinon : **`STOP`**, selon la branche. On ne « mesure pas quand même ». Le
> besoin — instrumentation, ou nouveau contrat — devient un lot à instruire, et
> **aucune instrumentation n'est créée par le présent document**.

> **E8 n'est pas un laissez-passer.** Il serait tentant de raisonner ainsi : *le
> régime est indéterminé, mais E8 arrêtera tout si `C1` est dépassée, donc on
> peut essayer*. **Non.** E8 est une défense **pendant** une exposition dont la
> précondition logique est établie ; il ne remplace pas cette précondition. Une
> exposition dont on ne sait pas si le critère qui la garde a un sens n'est pas
> une exposition gardée.

### 8.3 Métriques

| Réf | Grandeur | Source | Statut |
|---|---|---|---|
| **M1** | horodatage des connexions clientes au démon | journal `vcontrold` | **capacité réelle à établir en T0-A** — le dépôt ne prouve que l'horodatage d'ouverture |
| **M2** | intervalle de publication du **pont**, vu d'aval | consommateur MQTT (W4-C §13.1, niveau **C**) | disponible ; **sensibilité à caractériser** (§8.4) |
| **M3** | état de `<unité-pont>`, de `<timer-guard>` et de `vcontrold` | superviseur de services | disponible |
| **M4** | temps de fonctionnement de la machine | système | disponible |
| **M5** | `age_s`, `fresh`, `last_result`, `chain.status` par mesure | instantané publié par Boilerack | disponible |
| **M6** | **durée d'une sonde du superviseur** | — | **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`** |

> **M6 n'a aucun substitut, et M1 n'en est surtout pas un.** Il serait tentant de
> lire dans le journal un écart entre connexions du superviseur et d'y voir un
> retard. **W4-C §9.1 l'interdit explicitement** : un cycle dont la sonde a
> échoué a déjà redémarré le pont, **dort 90 s**, n'ouvre aucune connexion — et
> reste armé pour redémarrer la machine. L'absence de connexion est donc
> *exactement* la signature du cas le plus dangereux. Aucune inférence de santé
> du superviseur ne sera tirée de M1.

> **Le premier étage observable du chemin dangereux est le redémarrage non
> commandé du pont.** C'est la première action du superviseur en échec, et elle
> précède le redémarrage machine de **90 s** (W4-C §8.1). C'est sur M3 — et non
> sur M1 — que repose la détection précoce, et c'est ce qui fixe la cadence du
> §8.6.

Si l'exploitant peut instrumenter M6 sans modifier le dispositif historique, il
**SHOULD** le faire : c'est la mesure de premier choix. Sinon, elle reste
manquante, et le protocole en tient compte plutôt que de la simuler.

### 8.4 Ce que M2 prouve, et ce qu'il ne prouve pas

M2 observe que le pont **publie**. C'est le niveau **C** de W4-C §13.1, le seul
des trois qui atteste la fonction plutôt que le processus.

> **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`.** Le dépôt n'établit **pas** qu'un
> retard de la sonde interne du pont se traduise par un retard de publication
> aval. Le pont peut tamponner, publier sur une cadence propre, ou republier une
> valeur ancienne.
>
> **M2 prouve** que le pont continue de remplir sa fonction visible, et **détecte
> une interruption**. **M2 ne prouve pas** l'absence de dégradation interne.
>
> T0-A caractérise cette sensibilité si les données le permettent. À défaut, `C2`
> reste un critère de **fonction préservée**, non de **latence interne
> préservée**, et le document ne prétend pas davantage.

### 8.5 Les trois critères

**C1 — l'occupation ne doit pas pouvoir faire dépasser le budget du
superviseur.**

Formule figée ici :

```
borne_effective  =  max( borne_publique_C5 , borne_T0_superviseur )
seuil_C1         =  budget_superviseur  −  borne_effective
rafale_max(T1) ≤ seuil_C1      et      rafale_max(T2) ≤ seuil_C1
```

**La population pertinente est celle des sondes du superviseur**, et elle seule.
Pas l'ensemble des connexions au démon : le pont y domine numériquement, et son
coût ne gouverne aucun budget que `C1` protège.

| Terme | Valeur | Provenance |
|---|---:|---|
| `budget_superviseur` | 5,000 s | W4-C §8 |
| `borne_publique_C5` | **4,029 s** | C5 §9, maximum publié |
| `borne_T0_superviseur` | — | T0-C, **uniquement si** T0-A montre que la population des sondes du superviseur est **isolable** |
| **`seuil_C1` par défaut** | **0,971 s** | `5,000 − 4,029` |

*Justification.* Sous le régime additif (§6.5), une transaction concurrente paie
l'attente **puis** son propre coût. Pour que la somme reste sous le budget,
l'attente doit rester sous `budget − coût`. Ce n'est pas une fraction choisie :
c'est la soustraction que le régime impose.

> **`C1` est une borne déterministe, pas une politique probabiliste.** La V2
> employait un **quantile** — `q95` — là où la garantie revendiquée est une
> **borne**. Un `q95` laisse par construction une part de la queue haute
> au-dessus : avec `q95 = 3,7 s`, le seuil vaudrait `1,3 s`, et une sonde réelle
> à `4,0 s` donnerait `1,3 + 4,0 = 5,3 s > 5,0 s` **alors même que `C1` serait
> satisfaite**. Le quantile est **retiré de `C1`**. Seule une **borne
> supérieure** du coût de la sonde y entre.

> **T0 ne peut que resserrer `C1`, jamais la relâcher.** C'est le rôle du `max`
> dans `borne_effective`. Une mesure T0 qui rendrait une borne **supérieure** à
> 4,029 s durcit le seuil ; une mesure qui rendrait une borne **inférieure** est
> sans effet, la valeur publiée l'emportant. Le sens de la variation est donc
> unilatéral, et il va vers la sûreté.
>
> *Pourquoi cette précaution.* Sans le `max`, une population T0 dominée par le
> pont — dont les transactions peuvent être plus courtes que celles du
> superviseur — abaisserait la borne et **assouplirait** `C1` au moment précis où
> l'on cherche à protéger le superviseur. Le seuil deviendrait plus permissif
> parce qu'on aurait mesuré la mauvaise population.

> **Si T0-A ne permet pas d'isoler les sondes du superviseur**, alors
> `borne_T0_superviseur` **n'existe pas** et `seuil_C1 = 0,971 s`. On ne fabrique
> **pas** une borne à partir d'un mélange pont/superviseur : une borne tirée de
> la mauvaise population n'est pas une borne conservatrice, c'est une borne
> fausse.

> **Portée de la garantie.** `C1` n'a de sens que sous le régime **additif**. Si
> T0-B rend `NON ADDITIF` ou `INDÉTERMINÉ`, la barrière du §8.2.1 s'applique et
> il n'y a pas de T1 : `C1` n'est alors ni satisfaite ni violée, elle est **sans
> objet**.

Le seuil de 2,5 s de la V1, présenté comme « moitié du budget », était **faux** —
il dépassait déjà l'attente tolérable sur toute la plage C5, et il est retiré.

> **Résolution exigée de la source.** `C1` compare une durée à un seuil qui vaut
> **0,971 s** par défaut. La source retenue en T0-D pour mesurer `rafale_max` —
> M1, ou toute autre source qu'aura désignée T0-A — **MUST** avoir une résolution
> temporelle permettant de **décider sans ambiguïté** du dépassement.
>
> Une mesure de résolution `r` porte une incertitude de quantification d'au plus
> `r` sur une durée, et l'écart entre deux instants relevés en porte jusqu'à
> `2r`. Pour que la comparaison au seuil reste tranchée sur toute la plage
> utile, il faut donc `2r < seuil_C1`, soit :
>
> ```
> r  <  seuil_C1 / 2      =  0,4855 s  au seuil par défaut
> ```
>
> Soit, arrondi **dans le sens sûr**, `r < 0,485 s`. Arrondir à 0,486 s
> relâcherait la condition d'un millième : sur une règle conservatrice, on
> arrondit vers le bas.
>
> Une résolution à la seconde — cas courant d'un journal système — **ne
> satisfait pas** cette condition. Si aucune source disponible ne l'atteint :
> **`C1` non calculable ⇒ `T0 GO` impossible ⇒ `W4-F2 NON QUALIFIABLE — STOP`.**

> **Hypothèse revendiquée, et sa portée.** `C1` n'a de sens que sous le régime
> additif, dont le statut est **U-1**. Si T0-B établit un régime non additif,
> `C1` doit être **remplacée avant T1** par une formule adaptée à ce régime — et
> ce remplacement relève d'un amendement documentaire, pas d'un choix
> d'exploitant.

> **`C1` est vraisemblablement inatteignable.** Une lecture unique coûte 2,669 à
> 4,029 s, donc `rafale_max ≥ 2,669 s > 0,971 s` **par construction**. C'est un
> résultat, non un défaut du critère : sous le régime additif, la coexistence est
> arithmétiquement impossible aux coûts documentés. `C1` est la forme falsifiable
> de cet énoncé, et c'est pourquoi elle est évaluée **dès T1** (§8.7).

**C2 — le pont historique ne doit pas être dégradé.**

Comparaison de **quantiles homologues**, sur des fenêtres de **même durée `Δ`** :

```
p95(intervalle_publication, T2)  ≤  p95(T0)  +  ( p95(T0) − p50(T0) )
```

> **`C2` est une politique conservatrice site-relative, figée avant terrain — et
> non une dérivation.** La V2 affirmait « aucune constante libre » : c'était
> excessif. Trois choix de **politique** y sont faits, et ils sont assumés comme
> tels : `p95` comme statistique de comparaison ; `p50` comme référence basse de
> la dispersion ; et le coefficient **1** appliqué à l'écart `p95 − p50`. Aucun
> contrat amont ne les impose.
>
> **Ce que la règle vise.** Limiter la dégradation *visible* du pont à une
> amplitude comparable à sa **propre dispersion de référence**. Un site déjà
> irrégulier tolère un peu plus qu'un site régulier — non par indulgence, mais
> parce qu'exiger de lui une stabilité qu'il n'a jamais eue produirait un échec
> sans rapport avec Boilerack.
>
> **Ce que la règle ne fait pas.** Elle ne borne pas les événements extrêmes :
> **E3** s'en charge, en événement d'arrêt dur et non en statistique.

**Cas d'un T0 anormalement dispersé.** Si `p95(T0) − p50(T0)` est du même ordre
que `p95(T0)` lui-même, la tolérance devient si large que `C2` ne discrimine plus
rien : elle serait satisfaite par une dégradation majeure. **T0-D déclare alors
`C2` non exploitable**, `T0 GO` devient impossible, et **T1 est interdit**. Aucun
plafond absolu n'est posé ici : en inventer un remplacerait une constante non
justifiée par une autre.

*Pourquoi plus de `max`.* La V1 comparait `max(T2)` à `p95(T0)`. Deux
statistiques hétérogènes, et `max` croît avec la taille de l'échantillon : le
verdict pouvait basculer pour la seule raison qu'on avait observé plus
longtemps. Un quantile est **stable en durée** ; c'est ce qui le rend
contractuel. Le contrôle des événements extrêmes est assuré séparément par **E3**
(§8.6), qui est un événement d'arrêt et non une statistique.

*Validité du quantile.* Chaque fenêtre **MUST** contenir au moins **100**
intervalles de publication, afin que `p95` repose sur au moins cinq observations
de queue (`5 / 0,05 = 100`). Ce plancher est une exigence de validité, non un
réglage.

**C3 — Boilerack ne réussit pas par inaction.**

```
aucune mesure ne dépasse son fresh_max_s à aucun relevé de T2
et  chain.status reste nominal sur toute la fenêtre
et  chacun des huit rôles a produit au moins une lecture réussie
```

`fresh_max_s` est déclaré par mesure dans C7 ; il n'est pas inventé ici. La
troisième clause remplace le taux d'échec de 1 % de la V1, qui n'avait **aucune
provenance** : elle exprime la même intention — écarter une coexistence obtenue
en ne lisant rien — sans introduire de constante.

> **`C3` ne protège pas le dispositif historique** et n'y prétend pas. Elle
> garantit seulement que `C1` et `C2` n'ont pas été satisfaites par l'inaction.

### 8.6 Événements d'arrêt et cadence de surveillance

Un « arrêt immédiat » n'a de sens que si l'on dit à quelle cadence on regarde.

| Réf | Événement observable | Source | Cadence exigée | `F2A` |
|---|---|---|---|---|
| **E1** | redémarrage machine | M4 | ≤ `cadence_max` (§8.6.2) | F2A-3 |
| **E2** | redémarrage de `<unité-pont>` non commandé | M3 | ≤ `cadence_max` (§8.6.2) | F2A-4 |
| **E3** | publication du pont interrompue ≥ 2 × `p95(T0)` | M2 | continue | F2A-7 |
| **E4** | changement d'état de `vcontrold` | M3 | ≤ `cadence_max` (§8.6.2) | F2A-1 |
| **E5** | sortie du superviseur de son cycle nominal | M3 | ≤ `cadence_max` (§8.6.2) | F2A-2 |
| **E6** | perte de l'une des sources retenues | sources retenues en T0-D | continue | F2A-5 |
| **E7** | **doute de l'exploitant** | l'exploitant | permanente, par nature | F2A-8 |
| **E8** | **`C1` dépassée, à tout instant de T1 ou T2** | source de `C1` retenue en T0-D | continue | **F2A-6** |

#### 8.6.1 Le budget de 90 secondes, décomposé

Le superviseur en échec **redémarre le pont, puis attend 90 s** avant de
re-sonder ; c'est seulement au second échec qu'il redémarre la machine (W4-C §8).
Ces 90 s sont la fenêtre pendant laquelle un arrêt de Boilerack peut encore
éviter le redémarrage machine. Elle se consomme en **trois** termes, non en un :

```
T_detection  +  T_reaction  +  T_release   <   90 s
```

| Terme | Sens | Statut |
|---|---|---|
| `T_detection` | délai maximal avant qu'un événement E1/E2/E4/E5 soit vu | = cadence de relevé |
| `T_reaction` | temps humain entre la détection et la commande d'arrêt | **non borné par un contrat** |
| `T_release` | délai entre la commande d'arrêt et la **libération effective** de la liaison | mesuré ci-dessous |

> **Commander l'arrêt de `<unité-boilerack>` ne libère pas la liaison.** Un
> `run_due()` déjà engagé va jusqu'à son point de retour : le runner ne teste
> `stop.is_set()` **qu'entre** deux cycles, jamais à l'intérieur. Les lectures
> restantes du cycle en cours s'exécutent toutes.

**Mesure de `T_release`** — sonde jetable hors ligne pilotant le **vrai**
`ReadSurfaceRunner`, arrêt armé pendant une rafale :

| Coût par lecture | Arrêt armé à la lecture n° | Lectures restantes | `T_release` |
|---:|---:|---:|---:|
| 2,7 s | 1 | 7 | **18,9 s** |
| 2,7 s | 4 | 4 | 10,8 s |
| 4,0 s | 1 | 7 | **28,0 s** |
| 4,0 s | 4 | 4 | 16,0 s |
| 5,0 s | 1 | 7 | **35,0 s** |
| 5,0 s | 8 | 0 | 0,0 s |

**Borne.** `T_release` est bornée par **un** cycle `run_due()`, soit au plus les
huit mesures — et non par la rafale chaînée du §6.2, puisque le runner reteste
l'arrêt entre deux cycles :

```
T_release  ≤  8 × (R + ε)      ≈ 32,2 s  au maximum publié C5 (4,029 s), hors ε
```

#### 8.6.2 Cadence — ce qui est contractualisable, et ce qui ne l'est pas

La cadence n'est pas un chiffre à choisir mais un reste à calculer :

```
cadence_max  =  90 s  −  T_release_max  −  T_reaction_retenu
```

Au maximum publié C5, `T_release_max ≈ 32,2 s` (hors `ε`). Si l'exploitant
retient `T_reaction = 30 s`, alors `cadence_max ≈ 27,8 s`.

> **La cadence de 30 s de la V2 était insuffisante.** Elle se dérivait de
> `90 / 3 = 30`, un découpage qui ne comptait que la détection et **ignorait
> `T_release`**. Avec `T_release ≈ 32 s`, un relevé toutes les 30 s ne laisse
> qu'environ 28 s à l'humain — et la V2 ne le disait pas.

> **Aucune cadence ne fournit une garantie déterministe, et il faut le dire.**
> Deux termes de l'inégalité échappent à toute borne contractuelle : `ε_aval`
> n'est pas borné par le code (§3), et `T_reaction` est un temps **humain**, qui
> ne se contractualise pas. La cadence **réduit le risque** ; elle ne le supprime
> pas. Prétendre le contraire serait la même faute que le seuil de 2,5 s de la
> V1 — une garantie affichée que l'arithmétique ne soutient pas.

**Conséquence sur la barrière T0**, et c'est là que la garantie se rétablit :

> **Clause.** T0-D **MUST** établir, avant tout T1 :
>
> 1. une **borne** de `T_release` sur cette installation — à défaut de mesure, la
>    borne analytique `8 × (R_max + ε)` avec le `R_max` retenu ;
> 2. la **cadence de relevé réellement atteignable** sur M3 et M4 ;
> 3. le `T_reaction` que l'exploitant **déclare tenable**, écrit avant l'essai ;
> 4. que la somme des trois reste **strictement inférieure à 90 s**, avec la
>    marge que l'exploitant assume.
>
> Si la somme ne tient pas, ou si `T_release` ne peut pas être bornée :
> **`T0 GO` impossible ⇒ `W4-F2 NON QUALIFIABLE — STOP`.** L'exposition est alors
> refusée non parce qu'elle échouerait, mais parce qu'on ne pourrait pas
> l'interrompre à temps.

> **Un arrêt automatique n'est pas créé ici.** Si T0 démontre que la réaction
> humaine ne peut pas tenir dans le budget, alors un déclenchement automatisé sur
> E2 deviendrait un **besoin logiciel à instruire** dans un lot dédié. Ce serait
> du code, et V3 n'en écrit pas.

#### 8.6.3 Conséquence commune, et tolérance

> **Tout événement E1 à E8, `E7` compris, impose :**
>
> 1. l'**arrêt immédiat** de `<unité-boilerack>` ;
> 2. le verdict **`NON QUALIFIÉ`** pour W4-F2 ;
> 3. l'**interdiction de toute poursuite** — pas de reprise, pas de passage à T2.

**E7 n'est pas d'une autre nature que les autres.** Le doute de l'exploitant
**suffit**, et **aucune justification n'est requise**. La V2 l'avait exclu de la
phrase d'arrêt immédiat en ne nommant que « E1 à E6 et E8 » : c'était une
régression, et elle est corrigée. Le principe *l'humain arbitre* est opératoire,
non décoratif : celui qui est devant la machine peut interrompre sans avoir à
argumenter.

**La tolérance est une notion distincte, et elle ne s'applique pas à E7.**

| Événements | Tolérance |
|---|---|
| E1–E6, E8 | **numérique nulle** — une occurrence suffit |
| **E7** | **sans objet** — le doute n'est pas une grandeur, il ne se compte pas |

> Il ne doit jamais être écrit, ni laissé entendre, qu'**E7 peut être toléré**.
> Une tolérance nulle et une tolérance sans objet produisent le même effet
> — l'arrêt — mais pour des raisons différentes, et la confusion des deux
> rouvrirait la porte à un arbitrage sur le doute.

**E8 comble le manque signalé en V1.** `F2A-6` — l'arrêt prédictif de contention
— n'y était réalisé par aucun événement, et `C1` n'était évaluée qu'après coup.
Le contrat permettait donc d'observer une rafale excessive pendant T1 puis de
passer à T2. **E8 le rend impossible.** La couverture est désormais complète :
E1→F2A-3, E2→F2A-4, E3→F2A-7, E4→F2A-1, E5→F2A-2, E6→F2A-5, E7→F2A-8,
**E8→F2A-6**.

### 8.7 T1 — exposition courte, et sa barrière

**Rôle de T1, énoncé sans emphase :** borner l'exposition, rendre décidables les
grandeurs qui le sont vite, et **arrêter avant T2** si une barrière échoue. Rien
de plus.

**Durée : 12 minutes**, soit quatre cycles du superviseur (3 min), puis arrêt de
`<unité-boilerack>`.

> **T1 n'exerce pas le pire alignement, et ne prétend pas le faire.** La phase du
> superviseur au démarrage de Boilerack est **inconnue** — M6 n'est pas
> observable (§8.3) — et elle n'est pas **contrôlable**. Selon la phase de
> départ, une paire de sondes consécutives affectées peut survenir dans T1,
> survenir plus tard, ou ne pas survenir du tout.
>
> **Un T1 silencieux ne prouve donc rien** : ni l'absence de sérialisation, ni la
> qualification de la coexistence. Il prouve seulement qu'aucun événement d'arrêt
> ne s'est manifesté sur douze minutes.

> **Pourquoi ne pas répéter T1 à plusieurs phases.** L'idée serait juste si la
> phase était observable ou pilotable. Elle n'est ni l'une ni l'autre : on ne
> saurait pas quelles phases ont été exercées, ni combien il en reste. Une
> répétition donnerait une **impression** de couverture sans preuve falsifiable,
> et multiplierait l'exposition pour un gain non démontrable. Elle est donc
> **écartée**, et la raison est consignée plutôt que le résultat.

> **L'arrêt commandé n'est pas un arrêt effectif.** Le protocole humain de T1
> **MUST** tenir compte de `T_release` (§8.6.1) : entre la commande d'arrêt et la
> libération de la liaison, jusqu'à un cycle complet de lectures s'exécute encore.
> L'exploitant qui déclenche un arrêt ne doit pas conclure de l'exécution de sa
> commande que la contention a cessé.

> **Barrière T1 — normative, jamais discrétionnaire.**
>
> **`T1 GO`** si et seulement si **toutes** ces conditions sont réunies :
>
> 1. aucun événement **E1–E8** n'est survenu ;
> 2. **`C1` est satisfaite** sur la totalité de T1 — évaluée **pendant** T1, en
>    continu, et non après ;
> 3. les sources retenues par T0-D sont restées disponibles sans interruption ;
> 4. aucune situation n'a été classée non maîtrisée par l'exploitant.
>
> **`W4-F2 NON QUALIFIÉ — STOP`** sinon, **sans passage à T2**. L'absence
> d'incident ne suffit pas : la condition 2 est **positive et mesurée**.

### 8.8 T2 — observation longue

**Durée `Δ` ≥ 2 heures**, égale à celle de la fenêtre T0-C.

> **Ce que cette durée est.** Une **politique conservatrice d'observation**, et
> rien d'autre. Elle est justifiée par : un effectif d'intervalles du pont de
> plusieurs centaines, largement au-dessus du plancher de validité de 100 (§8.5) ;
> la couverture de plusieurs dizaines de cycles du superviseur ; et la capacité à
> observer une dérive durable plutôt qu'un transitoire.

> **Ce que cette durée n'est pas.** La V1 affirmait que deux heures garantissaient
> un **balayage complet des phases**, en s'appuyant sur deux points de simulation
> (11 min à 4,0 s, 109 min à 2,7 s). **Cette affirmation est retirée.** La
> fonction est résonante, et deux points ne bornent pas le domaine : la même
> sonde donne **153 min à 2,75 s**, et à **3,75 s** deux des dix-huit tranches de
> phase ne sont **jamais** couvertes en quatre heures. Ces deux coûts sont
> intérieurs à l'intervalle C5. Aucune durée finie ne garantit donc la couverture
> de phase, et `≥ 2 h` est assumée comme politique, non comme preuve.

### 8.9 Règle de conclusion

> **`QUALIFIÉ`** si et seulement si : `T0 GO` ; `T1 GO` ; aucun événement
> **E1–E8** sur T2 ; **C1**, **C2** et **C3** toutes satisfaites sur T2 ; et
> toutes les sources retenues disponibles sans interruption sur T1 et T2.
>
> **`NON QUALIFIÉ`** dans tous les autres cas, **y compris** si une source a
> manqué. Une mesure incomplète n'est pas un succès.
>
> **`NON QUALIFIABLE`** si la barrière T0 n'est pas franchie — branches **A** et
> **C** du §8.2.1, source de `C1` de résolution insuffisante, `C2` non
> exploitable, ou budget de réaction du §8.6.2 intenable. Ce n'est pas un échec
> de la coexistence : c'est l'impossibilité de la juger.
>
> **`T0 NO-GO`** en branche **B** : le régime est établi non additif, `C1`
> additive est sans objet, et son remplacement exige un nouvel audit avant tout
> T1.

`NON QUALIFIÉ`, `NON QUALIFIABLE` et `T0 NO-GO` entraînent tous trois, par W4-F0
§10.3.4, **W4-F3 NO-GO**. Aucun seuil ne se révise après coup : il se conteste avant la mesure, ou
il s'applique.

### 8.10 Ce que W4-F2 devra rapporter

Le résultat de T0-A, T0-B, T0-C et T0-D avec la décision de barrière ; pour C1,
C2 et C3, leur valeur sur T1 le cas échéant et sur T2, avec les entrées T0 des
formules ; la liste des événements E1–E8 survenus, ou l'attestation qu'aucun ne
l'est ; la disponibilité de chaque source ; **et le régime de concurrence observé
de `vcontrold`** (§6.5), qui est la donnée la plus utile que W4-F2 puisse
rapporter au reste du chantier.

---

## 9. Inconnues qui conditionnent W4-F2

| Réf | Inconnue | Statut |
|---|---|---|
| **U-1** | régime de concurrence de `vcontrold` — additif, entrelacé, ou autre | **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`** — conditionne §6.5 et la validité même de `C1` ; **T0-B** peut le trancher sans exposition si les sources le permettent |
| **U-2** | durée réelle d'une sonde du superviseur (M6) | **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`** — **aucun substitut admis** (§8.3) |
| **U-3** | capacité réelle du journal `vcontrold` : clôture, durée, attribution par client | **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`** — **T0-A** ; conditionne la calculabilité de `C1` |
| **U-4** | sensibilité de M2 à un retard interne du pont | **`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`** — §8.4 ; borne ce que `C2` démontre |
| **U-5** | phase du superviseur au démarrage de Boilerack | **non observable et non contrôlable** — fonde le §8.7 |
| **U-6** | référence T0 du pont sur cette installation | mesurable **par W4-F2**, phase T0-C |
| **I-7** | délai de propagation après changement réel | **non levable avant W4-F4** — circularité assumée (§4.4) |

`I-7` n'obstrue pas W4-F2, qui n'écrit pas. Elle figure ici parce que le §4.4 en
fait le seul point où la fenêtre de confirmation pourrait se révéler
insuffisante, et que W4-F1 ne peut pas le trancher.

---

## 10. Ce que ce document ne fait pas

- il ne modifie **aucun** code, test ni configuration ;
- il n'ouvre **aucun** sous-lot logiciel ;
- il ne demande ni n'accorde **aucune** autorisation terrain ;
- il ne choisit **aucune** valeur chaudière, aucune unité systemd, aucune
  constante de site ;
- il ne crée **aucune** instrumentation ;
- il ne conduit **aucune** mesure sur l'installation.

**W4-F2 reste fermé. Le pont historique reste l'unique écrivain réel de
production.**
