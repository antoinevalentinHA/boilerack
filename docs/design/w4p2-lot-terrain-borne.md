# `W4-P2` — second lot terrain borné : clôtures et durée de session

> **Version 7**, après sixième audit. Un bloqueur : la surveillance exigée
> pendant l'attente n'était **permise par aucun acte** à ce moment-là.
>
> | | Correction |
> |---|---|
> | **V7 · RB6-1** | **`O2` était un acte de la PHASE 2 seule.** Or le §8.1.1 exige que la surveillance **se poursuive pendant l'attente d'un retour synchronisé `S1`** — laquelle appartient à la **phase 3**. La préemption par `P2A-12` y était donc **prescrite sans acte pour l'observer**. `O2` est **étendu à la phase 3**, **strictement** pour cette surveillance et sa préemption, à la **même fréquence**, et jusqu'à l'un des deux termes nommés. **Aucune autre extension de périmètre** |
> | **V7 · C-12** | la ligne vive de **`P2A-11`** au §8.1 annonçait un retour *« synchronisé »* **sans réserve**, ce que le §8.1.1 contredit pour une invocation **en cours**. Alignée |
> | **V7 · C-13** | le cas **`[5 s, 10 s)` EN COURS** ne disait pas s'il emportait le **`STOP`**. **Tranché et écrit** : la conduite de retour est **toujours** immédiate ; le `STOP` est dû **si et seulement si** le chemin d'échec est **confirmé** — et **le doute vaut confirmation** |
>
> **Version 6**, après cinquième audit. Deux bloqueurs, dont un chemin qui
> aurait fait **attendre** le lot au pire moment possible.
>
> | | Correction |
> |---|---|
> | **V6 · RB5-1** | **La précédence entre `P2A-11` et `P2A-12` n'était pas réglée.** `P2A-11`, franchi à `5,000 s`, imposait un retour **synchronisé** — c'est-à-dire une **attente**. Or, sur une invocation **encore en cours**, la durée peut continuer de croître vers le chemin d'échec : le lot aurait attendu une frontière de cycle **pendant que les 90 s s'écoulaient**. Le §8.1.1 règle la précédence, traite séparément les relevés **`[5 s, 10 s)`** et **`≥ 10 s`**, et pose la règle absolue : **aucune attente volontaire à travers les 90 s** |
> | **V6 · RB5-2** | **Une mention résiduelle de « fraction choisie » subsistait** pour `P2A-11`, héritée de la V4 et contredisant le §8.1, le §8.4 et le §9. Retirée. **`P2A-11 = 5,000 s` est DÉRIVÉ, et n'est soumis nulle part comme choix humain** |
> | **V6 · C-10** | l'ordre du §9 est rétabli : `3`, `3 bis`, `3 ter`, `3 quater` |
> | **V6 · C-11** | sous `P2A-2` / `P2A-3`, le sort de **`R3`**, **`R4`** et **`R6`** est explicité — **sans objet**, chacun avec son motif |
>
> **Version 5**, après quatrième réaudit. Trois bloqueurs, dont un qui aurait
> fait avorter le lot sur un cycle **nominal**.
>
> | | Correction |
> |---|---|
> | **V5 · RB4-1** | **`P2A-11 = 4,000 s` était SOUS le régime observé.** `W4-P1` a relevé des enveloppes d'invocation nominales allant jusqu'à **4,682 s** : le seuil aurait été franchi par des cycles **parfaitement nominaux**, et — `P2A-11` alimentant `D-2`, qui alimente `P2A-5` — un cycle nominal aurait été **interprété comme le chemin d'échec de `F-12`**. C'est la régression que `W4-P1` V3 avait déjà corrigée sous `P2A-3c`. **Les deux garde-fous sont refondus et découplés** : `P2A-11` devient un `ABORT` **ordinaire** d'allongement, au budget dérivé, **faux positif assumé** ; `P2A-12` devient la détection du **chemin d'échec**, à un seuil **choisi au-dessus du régime observé**, et **lui seul** alimente `D-2` et `P2A-5` |
> | **V5 · RB4-2** | **La structure du §6.1 était cassée** : une note explicative se trouvait **entre deux lignes du tableau**, rendant ambiguë l'appartenance de `P3` et `P4` à la liste close. `P1`, `P2`, `P2 bis`, `P3`, `P4` sont désormais **cinq lignes contiguës**, et la note est **hors du tableau** |
> | **V5 · RB4-3** | **La séquence d'`ABORT` sous `P2A-2` / `P2A-3` omettait `R2`.** L'invariance des fichiers d'origine n'était portée par aucun acte dans ce cas. La séquence devient **`S1` → `S2` → `S7` → `S4` restreint aux empreintes → `O4`** |
> | **V5 · C-8** | la formulation de `C-5` disait *« la tolérance est retirée »*, ce qui pouvait se lire comme un retrait sur l'installation. Corrigée : c'est **sa mention dans le raisonnement du §4.2** qui a été retirée |
> | **V5 · C-9** | l'**état de `<unité-démon>`** au préflight est rétabli explicitement dans `P2` — la V4 l'avait réduit à l'invocation, à l'identifiant et au compteur de relances |
>
> **Version 4**, après troisième réaudit. Trois bloqueurs, tous d'exécutabilité.
>
> | | Correction |
> |---|---|
> | **V4 · RB3-1** | **Deux seuils n'avaient aucune valeur, et se renvoyaient l'un à l'autre.** `P2A-11` disait *« une fraction, soumise au §8.4 et au §9 »* ; le §8.4 disait *« la fraction de `P2A-11` »* ; le §9 renvoyait au §8.4. **Le renvoi était circulaire et la valeur n'existait nulle part** — le lot était inexécutable. Idem pour la réserve du §8.3.4. **Les deux valeurs sont désormais écrites**, classées **choisies**, et soumises nommément |
> | **V4 · RB3-2** | **Le préflight ne relevait pas les références du pont et du superviseur.** `D-1` et `P2A-6` comparent des identifiants d'invocation et des instants de démarrage à un état antérieur — **qui n'était pas capturé**. Ils auraient donc été **inopérants au premier redémarrage de la phase 1**. `P2` les relève désormais ; `S8` demeure la mesure finale comparative |
> | **V4 · RB3-3** | **L'exception `P2A-2` / `P2A-3` était incomplète** : elle omettait la preuve d'absence `S7` et le relevé partiel `R7`. Elle est complétée, `S3` restant interdit faute de redémarrage. Et **`O4` devient explicitement admissible dans TOUTE phase** dès qu'un `ABORT` survient |
> | **V4 · C-4** | le premier bras de `D-2` — *« un instant de démarrage ancien »* — **n'était pas quantifié**. Il est remplacé par une comparaison au **seuil de `P2A-11`**, applicable à une invocation **terminée ou en cours** |
> | **V4 · C-5** | la **mention de la tolérance de 10 s** est retirée **du raisonnement du §4.2** — la tolérance demeure ce qu'elle est dans la configuration ; elle ne **portait** rien ici, la marge de ≥ 180 s tenant sans elle |
> | **V4 · C-6** | la phrase *« aucune valeur de site »* était **fausse** : le document porte des **grandeurs mesurées** sur l'installation. Elle est corrigée en ce qu'elle disait vraiment — aucun **identifiant** de site |
> | **V4 · C-7** | l'historique est remis dans l'ordre **1, 2, 3, 4** |
>
> **Version 3**, après réaudit. Quatre bloqueurs, dont un qui rendait le
> garde-fou principal aveugle une fois sur trois.
>
> | | Correction |
> |---|---|
> | **V3 · RB-1** | **Le journal du superviseur cesse d'être le canal unique de détection.** `W4-P1` a homologué que **24 invocations sur 76 ne produisent aucune ligne propre** : un échec de sonde pouvait donc survenir **sans trace lisible**. Le §8.3 fonde désormais la détection sur **trois signaux indépendants des lignes propres**, dont deux portent sur des états que systemd tient pour **toutes** les invocations. **Aucune hypothèse n'est formée sur la cause des absences de trace** |
> | **V3 · RB-2** | **La fausse borne est retirée.** *« ≤ 15 s + un délai non établi »* n'est pas une borne. La conduite est reconstruite sur les **durées réellement opposables** — les 90 s déclarées de `F-12` —, la **bascule arbitraire à 45 s est supprimée**, et la marge restante est désormais **calculée sur un observable**. La règle de sûreté est explicite : **ne jamais laisser volontairement la verbosité élevée traverser une seconde sonde** dès qu'un échec est suspecté, si une conduite plus sûre existe |
> | **V3 · RB-3** | **Chaque preuve a maintenant son acte.** `R1` — absence du répertoire de surcharge — et `R5.d` — état nominal et compteurs de relances du pont et du superviseur — n'étaient portées par **aucun acte de la liste close**. Actes **`S7`**, **`S8`** ajoutés, ainsi que **`O4`** pour le relevé partiel de `R7` |
> | **V3 · RB-4** | **§8.4 et l'autorisation rendus cohérents.** Les seuils **dérivés du corpus** cessent d'être présentés comme des choix ; seuls les seuils **choisis humainement** sont soumis. **`P2A-11` est reformulé** : sa référence ambiguë au maximum relevé par `W4-P1` — sur une population que son homologation déclare **non homogène** — est remplacée par une **fraction du budget déclaré de 5 s**, sur une population **sans ambiguïté**. **`P2A-12` reste une donnée dérivée**, jamais un choix |
>
> **Version 2**, après audit. Quatre bloqueurs fermés, trois corrections.
>
> | | Correction |
> |---|---|
> | **V2 · BL-1** | **Trois défauts liés.** La V1 fondait la marge de synchronisation sur l'**enveloppe d'invocation** relevée par `W4-P1` — ce qui la traitait en **borne de sonde**, précisément ce que son homologation interdit. La marge est refondée sur les **seules données admissibles** : la **cadence déclarée** et le **budget déclaré de 5 s**. Et les objectifs, nommés `B-O1`…`B-O5`, **entraient en collision** avec `B-O1` et `B-O2` déjà homologués sous `W4-P1` : ils deviennent **`P2-O1`…`P2-O5`** |
> | **V2 · BL-2** | **La latence de détection de `P2A-5` est bornée.** La V1 exigeait un « retour immédiat » sans dire à quelle vitesse le déclencheur serait vu, ni par quel canal. Le §8.3 fixe le **canal**, la **fréquence maximale d'observation**, et **suspend la synchronisation** pour ce cas — attendre une frontière de cycle aurait consommé le budget de 90 s qui sépare du redémarrage machine |
> | **V2 · BL-3** | **Le §E.3 du cadrage devient un RISQUE DE SÛRETÉ**, non un caveat d'observation. L'allongement des sessions rapproche la sonde de son budget déclaré, et le §5.1 en tire deux `ABORT` opposables — `P2A-11` et `P2A-12`. **Aucune qualification de `C1`, aucune borne déterministe** n'en est tirée |
> | **V2 · BL-4** | **Le quatrième constat de sortie du §F.2 est restauré INTÉGRALEMENT** : processus unique **ET détenteur du périphérique** ET servant ses clients. La V1 avait perdu la détention. Les moyens de preuve sont ceux de l'**Acte A** — deux méthodes indépendantes — et les actes correspondants sont **ajoutés à la liste close** |
> | **V2 · C-1** | `428 × 7 = 2 996` : le *« ≥ 3 000 lignes »* de la V1 était **faux**. Corrigé en valeur exacte |
> | **V2 · C-2** | nouveau §8.4 : les **seuils internes d'`ABORT`** sont distingués des **seuils produits comme résultat**. Ce lot ne produit **aucun** seuil du second genre |
> | **V2 · C-3** | les seuils de **`P2A-7`** deviennent des **choix soumis à l'autorisation**, au même titre que la fenêtre |
>
> **Version 1.** Ouverture et bornage initial.

> **LOT BORNÉ, PAS EXÉCUTÉ.** Ce document borne une expérience
> comportant une **mutation temporaire et réversible**, et réunit les six éléments
> exigés. **L'élément 6 — autorisation propre — n'est PAS donné par ce document.**
>
> **Aucun seuil, aucun critère, aucune borne qualifiée, aucun `M6`. `C1` n'est pas
> rouverte. `T0` demeure NON AUTORISÉ, `T1` n'est pas approché.**

---

## 1. Désignation et repères

Le lot est désigné **`W4-P2`**. Désignation vérifiée libre : dix-neuf
désignations `W4` sont en usage, `W4-P1` comprise ; aucun `W4-P2` n'existait.

`W4-P2` est un **sous-lot d'expérience de `W4-P`**. Il n'est pas une phase de
`T0`, et **MUST NOT** être présenté comme en tenant lieu.

| Repère | Objet |
|---|---|
| `<unité-démon>` | l'unité de `vcontrold` |
| `<config-démon>` | le fichier de configuration déployée de `vcontrold` |
| `<journal-démon>` | le puits persistant fichier du démon |
| `<dropin-démon>` | le répertoire de surcharge systemd de `<unité-démon>` — **inexistant à ce jour** |
| `<unité-pont>` | l'unité du pont historique |
| `<timer-guard>` · `<unité-superviseur>` | le déclencheur périodique et l'unité du superviseur |

**Aucun IDENTIFIANT de site n'est écrit dans ce document** — ni chemin, ni hôte,
ni port, ni nom d'unité, ni sujet. L'invocation d'origine du démon est désignée
comme telle ; elle est relevée au préflight.

> **Ce document porte en revanche des GRANDEURS mesurées sur l'installation** —
> taille du journal, espace libre, cadence de connexion, décomptes du §3. La V3
> écrivait *« aucune valeur de site »*, ce qui était **faux** : ces grandeurs en
> sont. Elles sont conservées parce qu'elles **fondent le bornage**, et elles ne
> désignent rien.

## 2. Contexte opposable

| Source | Ce qu'elle établit |
|---|---|
| `w4p1-homologation.md` | `Command:` **ne permet pas** d'isoler les sondes du superviseur : toute sa population déclarée emploie une commande que le pont emploie aussi. **Cette piste est fermée sous le registre établi**, et `W4-P2` ne la rouvre pas |
| `w4f1a-upstream-characterization.md` §10.3 | `Closed connection (fd:%d)` **existe** dans le code, au niveau `LOG_INFO` |
| `w4a-acte-a-constat.md` §10 | `debug` effectif = **`false`** ; les types `LOG_INFO` comptent **0** occurrence |
| `w4-cadrage-activation-debug.md` **§B.3 (a)** | la voie `dbgFD` **ne peut structurellement pas** observer le trafic d'un autre client : sous `-n`, la session observatrice **bloque le service** |
| `w4-cadrage-activation-debug.md` **§D.3** | **aucune route ne dispense du redémarrage** : ni `reload`, ni `SIGHUP` ne propagent `debug` vers les puits persistants |
| `w4-cadrage-activation-debug.md` **§F.2** | l'état de sortie **MUST être constaté**, par quatre contrôles indépendants |
| `w4-cadrage-activation-debug.md` **§E.1** | le volume sous `debug` est *« une donnée manquante à établir **avant** toute activation »* ; plancher **≥ 7 lignes par session** |

> **La mutation est donc NÉCESSAIRE, et le corpus l'établit.** Les deux voies sans
> redémarrage sont fermées : `dbgFD` ne voit que sa propre session, et le
> rechargement à chaud ne propage pas `debug`. **Il n'y a pas de route douce.**

## 3. Faits établis par l'audit de bornage, en lecture seule

Conduit sur l'installation réelle, sans aucune mutation, pour combler ce que le
corpus déclarait non établi.

| # | Fait établi |
|---|---|
| **F-1** | l'option **`-g` / `--debug` existe dans le binaire déployé** — chaîne d'usage lue par `strings`, **binaire non exécuté**, méthode de l'Acte A |
| **F-2** | l'**invocation effective** du processus est celle de l'unité, sans option de journalisation ; le processus tourne sous un compte **non privilégié**, comme le §F.2 du cadrage le relevait déjà |
| **F-3** | **aucun répertoire de surcharge n'existe** pour `<unité-démon>` |
| **F-4** | **`xmllint` est ABSENT de l'hôte** — aucune validation préalable du XML n'est possible |
| **F-5** | **`systemd-analyze` est présent** — la voie surcharge est **validable avant redémarrage** |
| **F-6** | **aucune rotation** ne couvre `<journal-démon>` : aucune entrée `logrotate` ne le mentionne |
| **F-7** | `<journal-démon>` pèse **502 140 225 octets** ; sa partition offre **≈ 51 Gio libres**, occupation **9 %** |
| **F-8** | **cadence de connexion ≈ 2,105 s** — 2 991 `Client connected` sur **6 298 s** |
| **F-9** | **`FD:5` est CONSTANT** sur les 2 991 connexions relevées |
| **F-10** | les **ports source sont variables** — 2 693 valeurs distinctes — mais la ligne de **clôture ne porte que le descripteur**, non le port |
| **F-11** | trois séquences `Received SIGPIPE` / `Error writing to socket` figurent au journal sur ≈ 1 h 45 : **des sessions se terminent anormalement**, avant le lot et indépendamment de lui |
| **F-12** | le superviseur, sur échec de sonde, **redémarre le pont**, attend **90 s**, resonde — et **si la seconde sonde échoue, il redémarre la machine**. Établi par le relevé `A1` figé de `W4-P1`, registre **configuration déclarée** |

### 3.1 Ce que `F-9` et `F-10` impliquent pour l'appariement

**L'appariement par descripteur est sans contenu** : le descripteur est constant.
Le port, qui varie, **n'apparaît pas** sur la ligne de clôture.

> **Il ne resterait donc que l'ordre.** Sous `-n`, le service est strictement
> séquentiel : ouvertures et clôtures devraient **alterner**. C'est une
> **hypothèse d'appariement**, et `F-11` montre déjà qu'elle peut être mise en
> défaut par des terminaisons anormales. **La vérifier est l'objet `P2-O2` du §5.**

### 3.2 Le volume, désormais chiffrable

`F-8` fournit la donnée que le §E.1 du cadrage exigeait. Pour une fenêtre de
**15 minutes** : **900 s / 2,105 s ≈ 428 sessions**, soit **≈ 2 996 lignes** au
plancher de sept lignes par session, et quelques multiples de ce nombre au plus.

> **Correction de la V1**, qui écrivait *« ≥ 3 000 lignes »* : `428 × 7 = 2 996`.
> Le plancher est **inférieur** à 3 000, et l'arrondi allait dans le mauvais sens.

> **Rapporté à `F-7`, le risque de saturation est négligeable pour une fenêtre
> courte** — et il ne le serait pas pour une fenêtre longue, `F-6` établissant
> qu'aucune rotation ne reprend l'espace.

## 4. Élément 1 — Périmètre

**Le lot a trois phases, et trois seulement** : préflight en lecture · fenêtre
d'observation sous verbosité élevée · retour au régime initial et constat de
sortie.

**Voie retenue : SURCHARGE SYSTEMD portant `-g`. La voie XML est ÉCARTÉE.**

| | Voie XML | **Voie surcharge, retenue** |
|---|---|---|
| Objet modifié | le fichier portant périphérique, port, journal, privilèges et jeu de commandes | **un fichier neuf**, dans un répertoire **qui n'existe pas encore** |
| Validation préalable | **impossible** — `F-4` | **possible** — `F-5`, plus l'affichage de l'invocation résultante **sans redémarrage** |
| Échec de configuration | **fatal au démarrage**, puis boucle de relance — et `F-12` mène alors au **redémarrage machine** | l'unité ne démarre pas ; même boucle, mais **surface d'une seule ligne**, validée avant |
| Fichiers d'origine | **modifiés** | **jamais touchés** — leurs empreintes prouvent l'invariance |
| Retour | ré-éditer, relancer | **supprimer le répertoire**, relancer |
| Précédence | cède devant la ligne de commande | **l'emporte** — `w4-cadrage-activation-debug.md` §D.5 |

**Le périmètre exclut, explicitement** : toute écriture chaudière · tout démarrage
de Boilerack · **toute modification du pont historique ou du superviseur** —
fichiers, unités, état · toute modification de `<config-démon>` · toute
modification du fichier d'unité lui-même · toute suppression ou rotation de
`<journal-démon>` — le §F.1 du cadrage en fait un **troisième acte**, hors lot ·
toute session cliente ouverte sur le démon par le lot · `T0`, `T1`, `T2` · les
quatre actes réservés du `w4f-write-sovereignty.md` §11.1.

### 4.1 Fenêtre et synchronisation

| | |
|---|---|
| Fenêtre sous verbosité élevée | **une seule**, continue, **bornée à 15 minutes** |
| Cycles utiles visés | **au moins 3 cycles du superviseur** — à la **cadence déclarée**, 3 × 180 s = **9 min**, d'où le plafond ci-dessus avec sa marge |
| Terminaison anticipée | **exigée dès que la matière suffit** aux objectifs du §5 |
| Les **deux** redémarrages | **synchronisés** : exécutés **immédiatement après la fin constatée d'un cycle** du superviseur |

### 4.2 Sur quoi la marge de synchronisation est fondée

**Uniquement sur des données admissibles**, et l'une d'elles est une **règle
déclarée**, non une mesure :

| Donnée | Registre | Ce qu'elle fournit |
|---|---|---|
| **cadence déclarée** du déclencheur — **3 min après inactivité** | **configuration déclarée**, `A-O4` homologué | après la fin constatée d'un cycle, **≥ 180 s** s'écoulent avant le démarrage du suivant |
| **budget déclaré de la sonde — 5 s** | **configuration déclarée**, `A-O2` homologué | une sonde qui rencontrerait le démon indisponible **échoue en 5 s au plus** |

> **Correction de fond de la V1.** Elle fondait la marge sur l'**enveloppe
> d'invocation** relevée par `W4-P1`, en la présentant comme *« l'enveloppe de
> sonde […] maximum observé 4,682 s »*. **C'était traiter cette enveloppe en
> borne de sonde** — ce que son homologation interdit expressément : elle **ne
> vaut pas `M6`**, **n'est pas une borne de sonde**, et **rien ne s'en déduit**.
> **Cette fondation est retirée.**

> **Ce que la marge de 180 s borne, et ce qu'elle ne borne pas.** Elle borne le
> **délai avant la sonde suivante**. Elle **ne borne pas la durée d'un
> redémarrage**, qui n'est établie nulle part et que ce lot **ne mesurera pas
> pour se préparer**. C'est `P2A-4` — unité active dans les **10 secondes**,
> compteur de relances stable — qui porte ce risque, et non la marge.

## 5. Élément 2 — Objectif

> **Établir des faits d'observabilité et d'appariement. Rien d'autre.**
> Ce lot **ne produit pas `M6`**, **ne qualifie aucune borne**, **ne fixe aucun
> seuil**, **ne produit aucun critère** et **ne rouvre pas `C1`**.

> **Désignations propres à `W4-P2`.** Elles sont préfixées `P2-` **parce que
> `B-O1` et `B-O2` sont déjà pris** : ce sont les objectifs de `W4-P1`, homologués
> et opposables. La V1 les réemployait, ce qui aurait rendu tout rapport
> ambigu — et aurait invité à confondre l'enveloppe d'invocation de `W4-P1` avec
> la durée de session visée ici.

| Réf | Question | Objectif | Verdicts admissibles |
|---|---|---|---|
| **`P2-O1`** | **A** | les **clôtures deviennent-elles effectivement observables** dans le puits persistant ? | `CLÔTURES OBSERVABLES` · `NON OBSERVABLES` · `INDÉTERMINÉ` |
| **`P2-O2`** | **B** | ouverture et clôture sont-elles **appariables sans ambiguïté** ? | `APPARIEMENT SANS AMBIGUÏTÉ` · `APPARIEMENT AMBIGU` · `INDÉTERMINÉ` — avec, dans tous les cas, **le critère d'appariement effectivement employé** et **le taux de séquences non appariables** |
| **`P2-O3`** | **C** | **quelle grandeur** cet appariement mesure-t-il exactement ? | **énoncé typé** de la grandeur, avec ce qu'elle **contient** et ce qu'elle **exclut** · `NON DÉTERMINABLE` |
| **`P2-O4`** | **D** | cette grandeur **apporte-t-elle** quelque chose à `U-2`, à `U-7`, ou seulement une **enveloppe différente** ? | `APPORT À U-2` · `APPORT À U-7` · **`ENVELOPPE DIFFÉRENTE UNIQUEMENT`** · `INDÉTERMINÉ` — **motivé**, jamais présumé |
| **`P2-O5`** | **E** | **quelles limites subsistent** après l'expérience ? | **énumération**, dont au minimum la **résolution** du puits et la portée des faits `F-9` à `F-11` |

> **Trois limites connues d'avance, à porter au rapport quoi qu'il advienne.**
>
> 1. **La résolution du puits demeure à la seconde** — le cadrage §B.3 (f)
>    l'établit pour les deux puits. Une durée de session s'en déduira **à cette
>    granularité**, et le §8.5 de `w4f1` interdit d'en tirer une borne.
> 2. **L'observation déforme ce qu'elle mesure** — §E.3 du cadrage : chaque ligne
>    coûte un appel d'écriture, et l'intercalation est réelle **à la réception**.
>    **La magnitude n'est établie nulle part**, et ce lot ne la fabriquera pas.
> 3. **Une durée de session n'est pas `M6`** : la population n'est pas isolée, et
>    `F-9`/`F-10` retirent tout moyen d'attribution par le puits.

### 5.1 Le §E.3 est un RISQUE DE SÛRETÉ, et pas seulement une limite

La V1 le rangeait parmi les caveats d'observation. **C'est insuffisant, et le
cadrage le dit lui-même** : *« C'est le risque le moins visible et, à mon sens,
le plus sérieux. »*

**La chaîne de conséquence, énoncée en clair :**

| | |
|---|---|
| **fait de code** | `logIT()` fait un `fprintf` **puis un `fflush` à chaque ligne**, sans tamponnage applicatif : **un appel système d'écriture par ligne** |
| **fait de code** | l'intercalation est **réelle à la réception** — horodatage pris avant, ancre déplacée après |
| **conséquence** | sous verbosité élevée, **les sessions s'allongent**. De combien : **non établi**, ni ici ni dans le cadrage |
| **conséquence de sûreté** | une sonde du superviseur est **budgétée à 5 s déclarés**. Un allongement la **rapproche de son budget** — et `F-12` établit ce qui suit un échec : **redémarrage du pont**, puis, si la seconde sonde échoue aussi, **redémarrage de la machine** |

> **Ce n'est donc pas une dégradation de la qualité de mesure : c'est un chemin
> vers l'incident de production**, et il **MUST** être gardé comme tel. Deux
> `ABORT` opposables le portent, et ils ont **deux rôles distincts** :
> **`P2A-11`** garde l'**allongement**, **`P2A-12`** détecte le **chemin
> d'échec** — et **lui seul** alimente `D-2` et `P2A-5` (§8.1, §8.3.1).

> **Ce que ce lot NE fait PAS de ce risque.** Il n'en tire **aucune qualification
> de `C1`**, **aucune borne déterministe** — il n'en existe pas —, **aucun
> seuil de critère**. Les garde-fous du §8.1 sont des **seuils internes
> d'arrêt**, et le §8.4 les distingue expressément d'un résultat.

## 6. Élément 3 — Actes permis, **liste close**

> **Liste close.** Tout acte qui n'y figure pas est **interdit**. Un doute sur
> l'appartenance vaut **interdiction** et déclenche **`P2A-1`**.

### 6.1 Phase 0 — préflight, en lecture seule

| # | Acte |
|---|---|
| **P1** | relever les **empreintes** — taille, date, condensat — de `<config-démon>` et du fichier d'unité de `<unité-démon>` |
| **P2** | relever, **pour `<unité-démon>`** : l'**invocation effective du processus**, son **identifiant de processus**, son **compteur de relances**, son **identifiant d'invocation**, son **instant de démarrage**, son **état** et son **sous-état** |
| **P2 bis** | relever, **pour `<unité-pont>` et pour `<unité-superviseur>`**, les **références de comparaison** : **compteur de relances**, **identifiant d'invocation**, **instant de démarrage**, **état** et **sous-état** |
| **P3** | relever la **taille** de `<journal-démon>`, le **nombre de lignes** qu'il porte, et l'**espace libre** de sa partition |
| **P4** | lire, **rétrospectivement**, le journal système de `<unité-superviseur>` sur une fenêtre courte, pour **situer le cycle courant** |

> **Les cinq lignes ci-dessus appartiennent toutes à la liste close.** La V4
> insérait cette note **entre deux lignes du tableau**, ce qui rendait ambiguë
> l'appartenance de `P3` et `P4`. Elle est désormais **hors du tableau**.

> **`P2 bis` rend `D-1` et `P2A-6` opérants dès le premier redémarrage.** L'un et
> l'autre comparent un identifiant d'invocation ou un instant de démarrage **à un
> état antérieur**. Sans référence capturée **avant** la mutation, ils n'auraient
> rien à comparer, et seraient restés **inopérants** pendant toute la phase 1.
>
> **`S8` demeure la mesure finale comparative** : c'est le couple `P2 bis` → `S8`
> qui porte `R5.d`, et `P2 bis` qui porte `D-1` et `P2A-6` pendant la fenêtre.

> **`P2` couvre aussi `<unité-démon>`.** La V4 l'avait réduit à l'invocation, à
> l'identifiant de processus et au compteur de relances, perdant l'état que la V3
> relevait. Sans lui, `R3` et `R5.a` compareraient à une référence incomplète.

### 6.2 Phase 1 — armement

| # | Acte |
|---|---|
| **M1** | créer `<dropin-démon>` et **un seul** fichier de surcharge, portant **exclusivement** la réinitialisation de la ligne d'exécution et sa reprise **à l'identique augmentée de `-g`** |
| **M2** | **valider l'unité résultante** par `systemd-analyze verify` — **sans redémarrage** |
| **M3** | **recharger la configuration systemd** — cet acte **ne redémarre pas** le service |
| **M4** | **afficher l'invocation résultante** et la **comparer caractère à caractère** à l'attendu — **avant** tout redémarrage |
| **M5** | **attendre la fin constatée d'un cycle** du superviseur, puis **redémarrer `<unité-démon>`** |
| **M6** | **vérifier dans les 10 secondes** : unité active, identifiant de processus **nouveau**, compteur de relances **stable** |

### 6.3 Phase 2 — observation

| # | Acte |
|---|---|
| **O1** | relever la **position de fin** de `<journal-démon>` avant la fenêtre, puis lire **exclusivement les lignes produites après cette position** |
| **O2** | surveiller, **par lecture seule**, selon les canaux et la fréquence du §8.3 : l'**état, le sous-état, l'instant de démarrage, l'identifiant d'invocation et le compteur de relances** des trois unités du périmètre · la croissance de `<journal-démon>` · l'espace libre · et, **quand elles existent**, les lignes propres de `<unité-superviseur>`. **Voir l'extension du §6.3.1** |
| **O3** | **figer** les relevés dans des fichiers **hors dépôt** |
| **O4** | **en cas d'`ABORT`, dans QUELLE QUE SOIT la phase** — 0, 1, 2 ou 3 —, **consigner l'état exact du relevé partiel** : ce qui a été figé, ce qui ne l'a pas été, et l'**instant de l'arrêt** — porte `R7`. **Hors ce cas, `O4` n'est pas permis** |

#### 6.3.1 Extension de `O2` à la phase 3 — et à elle seule

**`O2` est un acte de la phase 2.** Le §8.1.1 exige pourtant que la surveillance
**se poursuive pendant l'attente d'un retour synchronisé `S1`**, laquelle
appartient à la **phase 3**. Sans cette extension, la **préemption** que le
§8.1.1 prescrit serait **prescrite sans acte permettant de l'observer**.

| | |
|---|---|
| **Ce qui est étendu** | `O2`, **et lui seul**, **inchangé dans son contenu et sa fréquence** |
| **Quand** | pendant toute **attente d'un retour synchronisé `S1`**, en phase 3 |
| **Pour quoi faire** | **uniquement** maintenir la surveillance et la **préemption** définies au §8.1.1 |
| **Jusqu'à quand** | jusqu'à l'un des **deux termes**, et à aucun autre : **(a)** l'**exécution effective du retour** — `S1` engagé ; **(b)** la **préemption par `P2A-12`**, qui bascule sur la conduite du §8.3.4 |

> **Aucune autre extension de périmètre.** `O2` ne devient pas un acte des phases
> 0 ou 1 ; il ne s'étend à aucun autre objet, aucune autre fréquence, aucun autre
> canal. **Hors attente d'un `S1` synchronisé, `O2` demeure un acte de la seule
> phase 2.**

### 6.4 Phase 3 — retour et constat de sortie

| # | Acte |
|---|---|
| **S1** | **attendre la fin constatée d'un cycle** du superviseur, puis **supprimer le fichier de surcharge et le répertoire `<dropin-démon>`** |
| **S2** | **recharger la configuration systemd**, puis **afficher l'invocation résultante** et vérifier qu'elle est **identique à celle du préflight** |
| **S3** | **redémarrer `<unité-démon>`** |
| **S4** | relever l'**invocation effective** du processus, son identifiant, son compteur de relances, et les empreintes de `<config-démon>` et du fichier d'unité |
| **S5** | lire les lignes de `<journal-démon>` **produites après** le redémarrage de retour, et y vérifier l'**absence des types `LOG_INFO`** visés — puis la **reprise des lignes d'ouverture**, qui atteste que le démon **sert ses clients** sans que le lot ouvre lui-même de session |
| **S6** | établir que le démon est un **processus unique** et le **détenteur du périphérique**, par les **deux méthodes indépendantes de l'Acte A** : `fuser -v` sur le périphérique, **et** balayage des descripteurs sous `/proc` |
| **S7** | **constater l'absence** de `<dropin-démon>` et de son fichier — porte `R1` |
| **S8** | relever, pour `<unité-pont>` et `<unité-superviseur>` : **état, sous-état, compteur de relances, identifiant d'invocation et instant de démarrage** ; et relever la **taille finale** de `<journal-démon>` ainsi que l'**espace libre** — porte `R5.d` et `R6` |

**Tout le reste est interdit** — et nommément : aucune édition de `<config-démon>`
ni du fichier d'unité · aucune session cliente ouverte par le lot · aucune
commande envoyée au démon · aucun `reload` applicatif, aucun signal · aucune
action sur `<unité-pont>`, `<timer-guard>` ni `<unité-superviseur>` · aucune
suppression, troncature ni rotation de `<journal-démon>` · aucune publication
externe d'un élément du lot.

## 7. Élément 5 — Restauration définie et vérifiable

**Le lot mute. La restauration est donc réelle, et elle doit être ÉTABLIE, pas
supposée** — `w4-cadrage-activation-debug.md` §F.2.

| # | Preuve exigée |
|---|---|
| **R1** | **`<dropin-démon>` n'existe plus**, ni son fichier |
| **R2** | `<config-démon>` et le fichier d'unité : **taille, date et condensat identiques** au préflight — **ils n'auront jamais été touchés** |
| **R3** | l'**invocation effective du processus** est identique à celle du préflight, **sans `-g`** — le contrôle porte sur le **processus**, non sur le fichier |
| **R4** | sur les lignes **produites après** le retour : **absence des types `LOG_INFO`** visés. Seul contrôle portant sur le **comportement observable** |
| **R5** | **quatrième constat du §F.2, restauré intégralement** — le démon est revenu à l'état d'**un processus unique**, **détenteur du périphérique**, **servant ses clients** : |
| `R5.a` | **processus unique** — une seule instance, sans enfant |
| `R5.b` | **détenteur du périphérique** — établi par **deux méthodes indépendantes**, celles de l'Acte A : `fuser -v` et balayage des descripteurs sous `/proc` |
| `R5.c` | **sert ses clients** — les lignes d'ouverture reparaissent dans `<journal-démon>` après le retour, **sans que le lot ouvre de session** |
| `R5.d` | `<unité-pont>` et `<unité-superviseur>` sont **nominaux**, compteurs de relances **inchangés** |
| **R6** | le **volume ajouté** à `<journal-démon>` est relevé et consigné |
| **R7** | en cas d'`ABORT` : le **relevé partiel** est conservé **tel quel**, avec l'instant de l'arrêt, et **MUST NOT** être complété, reconstitué ni présenté comme complet |

> **Ce que la restauration ne rend pas.** L'espace consommé dans
> `<journal-démon>` **reste consommé** : `F-6` établit qu'aucune rotation ne le
> reprendra. Son retrait serait un **troisième acte**, **hors de ce lot**, et
> `R6` se borne à le **chiffrer**.

> **Une divergence sur `R1`, `R2`, `R3` ou `R4` est un `ABORT`**, et **MUST** être
> consignée telle quelle, sans correction ni réinterprétation.

## 8. Élément 4 — `ABORT` et `STOP`

### 8.1 `ABORT` — arrêt immédiat, suivi du retour de la phase 3

| Réf | Déclencheur |
|---|---|
| **`P2A-1`** | un acte hors de la liste close est envisagé, ou son appartenance est douteuse |
| **`P2A-2`** | la validation `M2` signale quoi que ce soit — **ne pas redémarrer**, retirer la surcharge |
| **`P2A-3`** | l'invocation résultante affichée en `M4` **diffère** de l'attendu, en quoi que ce soit — **ne pas redémarrer**, retirer la surcharge |
| **`P2A-4`** | après un redémarrage, l'unité n'est pas active dans les **10 secondes**, ou son compteur de relances **s'incrémente** — signature d'une boucle |
| **`P2A-5`** | l'un des **trois détecteurs du §8.3** signale que le chemin d'échec de `F-12` est **engagé ou suspecté**. **Retour selon le §8.3, puis `STOP` pour arbitrage** : le pont aurait été redémarré, ce que le lot s'interdit |
| **`P2A-6`** | `<unité-pont>` redémarre, ou son compteur de relances bouge |
| **`P2A-7`** | l'espace libre de la partition passe **sous 10 %**, ou `<journal-démon>` croît de plus de **100 Mio** pendant la fenêtre. **Seuils internes, soumis à l'autorisation** — §8.4, §9 |
| **`P2A-8`** | redémarrage machine |
| **`P2A-9`** | la fenêtre du §4.1 serait dépassée |
| **`P2A-10`** | **doute de l'exploitant, sans justification à fournir** |
| **`P2A-11`** — *allongement* | la durée d'une invocation **quelconque** de `<unité-superviseur>` — terminée ou en cours — atteint **`5,000 s`**, le **budget déclaré**. `ABORT`, dont **la conduite dépend de l'état de l'invocation** : **terminée** → retour **synchronisé** ; **EN COURS** → retour **NON synchronisé**, §8.1.1. **Valeur DÉRIVÉE**, jamais un choix. **N'alimente NI `D-2` NI `P2A-5`** |
| **`P2A-12`** — *chemin d'échec* | la durée d'une invocation **quelconque** de `<unité-superviseur>` — terminée ou en cours — atteint **`10 s`**. `ABORT` **D'URGENCE** : alimente `D-2`, donc `P2A-5`, donc la conduite du §8.3.4. **Valeur CHOISIE**, soumise au §9 |

> **Correction de fond de la V4, et elle était grave.** `P2A-11` y valait
> **`4,000 s`** — **SOUS le régime observé**. `W4-P1` a relevé des enveloppes
> d'invocation **nominales** allant jusqu'à **4,682 s** : le seuil aurait été
> franchi par des cycles **parfaitement normaux**. Et comme `P2A-11` alimentait
> `D-2`, qui alimente `P2A-5`, **un cycle nominal aurait été interprété comme le
> chemin d'échec de `F-12`**, déclenchant la conduite d'urgence et un `STOP`.
>
> **C'est exactement la régression que `W4-P1` V3 avait corrigée sous `P2A-3c`** :
> prendre le comportement nominal pour une défaillance.

> **Ce que la V5 fait, et ce qu'elle se refuse à faire.**
>
> | | |
> |---|---|
> | **elle ne dérive aucune borne de `W4-P1`** | la valeur `4,682 s` n'est employée **ni comme borne, ni comme seuil, ni comme base de calcul**. Elle sert **uniquement** à constater que `4,000 s` était sous le régime observé, et à vérifier qu'un seuil choisi se situe au-dessus |
> | **elle choisit un seuil humain au-dessus du régime observé** | **`10 s`** pour `P2A-12` : plus du **double** de tout ce qui a été observé sans verbosité élevée, **au-dessus** du budget dérivé de 5 s, et **neuf fois sous** la signature déclarée du chemin d'échec, qui court à ≥ 90 s |
> | **elle assume explicitement le faux positif** | `P2A-11` à `5,000 s` ne laisse que **≈ 318 ms** au-dessus du maximum observé. **Il peut donc se déclencher sur un cycle nominal** — et c'est assumé : son effet est un `ABORT` **ordinaire**, qui met fin au lot **sans rien conclure** |
> | **elle découple** | **`P2A-11` n'alimente ni `D-2` ni `P2A-5`.** Un franchissement du budget **n'est pas** une interprétation du chemin `F-12` : seul **`P2A-12`** l'est |
>
> **Le garde-fou est donc opérant sans qu'un cycle nominal soit jamais interprété
> comme le chemin de `F-12`.**

> **Reformulation de `P2A-11`, et pourquoi.** La V2 le référait au *« maximum
> relevé par `W4-P1` »*. **Cette référence était ambiguë sur deux plans** : la
> valeur n'était pas nommée, et la population dont elle sortait est déclarée
> **non homogène** par l'homologation elle-même — 52 invocations qualifiées, 24
> non qualifiées. **Un seuil d'arrêt ne peut pas reposer là-dessus.** `P2A-11`
> repose désormais sur une **valeur dérivée du corpus** — le **budget déclaré**,
> `5,000 s` — **et sur rien d'autre**.
>
> **Aucune fraction n'intervient.** La V4 en introduisait une ; la V5 l'a retirée
> du seuil sans nettoyer cette phrase, qui la mentionnait encore. **`P2A-11` est
> dérivé de bout en bout**, et n'est soumis à l'autorisation **à aucun titre** —
> §8.4, §9 point 3 quater.

> **La population est désormais sans ambiguïté** : **toute** invocation de
> `<unité-superviseur>` observée pendant la fenêtre, **qualifiée ou non**. Ce
> choix découle de `RB-1` : conditionner le garde-fou à la présence d'une ligne
> propre l'aurait rendu **aveugle** sur les invocations qui n'en produisent pas.

#### 8.1.1 Précédence entre `P2A-11` et `P2A-12`

> **RÈGLE ABSOLUE, qui domine tout ce paragraphe.** **Le lot n'attend jamais
> volontairement à travers les 90 s du chemin de `F-12`.** Aucune conduite, aucun
> `ABORT`, aucune synchronisation ne peut avoir pour effet une attente pendant
> que cet intervalle s'écoule.

> **RÈGLE DE PRÉCÉDENCE.** **`P2A-12` prévaut TOUJOURS sur `P2A-11`** dès qu'il
> est atteint. Lorsque les deux sont satisfaits, la conduite est **celle de
> `P2A-12`**, sans exception et sans délibération.

**Le défaut que cela corrige.** `P2A-11` prescrivait un retour **synchronisé** —
donc une **attente**. Sur une invocation **encore en cours**, la durée **peut
continuer de croître** : le lot aurait attendu une frontière de cycle **alors
même que le chemin d'échec se déroulait**. La durée seule ne suffit donc pas à
choisir la conduite : **il faut savoir si l'invocation est terminée.**

**Les deux relevés, traités séparément :**

| Relevé | État de l'invocation | Conduite, et son motif |
|---|---|---|
| **`[5 s, 10 s)`** | **TERMINÉE** | la durée est **définitive et ne croîtra plus**. De plus, la signature déclarée du chemin d'échec court à **≥ 90 s** : une invocation close en deçà de 10 s **n'y est pas engagée**. → **`P2A-11` ordinaire, retour SYNCHRONISÉ permis** |
| **`[5 s, 10 s)`** | **EN COURS** | la durée **peut encore croître** vers `P2A-12`. **Aucune attente volontaire n'est permise.** → **conduite du §8.3.4**, exactement comme si `P2A-12` était atteint. **Pour le `STOP`, voir la règle ci-dessous** |
| **`≥ 10 s`** | terminée **ou** en cours | **`P2A-12` prévaut** → **conduite du §8.3.4**, `STOP` pour arbitrage dû |

> **Il n'y a donc qu'un seul chemin où une attente est permise** : une invocation
> **close** entre 5 s et 10 s. Partout ailleurs, la conduite est **non
> synchronisée**.

> **Et l'attente permise reste sous surveillance.** Pendant qu'un retour
> synchronisé est en cours d'attente, la surveillance du §8.3.2 **se poursuit à
> sa fréquence** — l'acte qui la permet en phase 3 est l'**extension du §6.3.1**.
> Si une invocation ultérieure atteint `P2A-12`, la conduite d'urgence du §8.3.4
> **préempte** le retour synchronisé en attente, sans délibération.

> **Le `STOP` dans le cas `[5 s, 10 s)` EN COURS — tranché, et écrit.** La V6
> laissait l'ambiguïté : la conduite renvoyait au §8.3.4, dont les deux branches
> déclarent le `STOP` dû, alors que le chemin d'échec n'est ici que **suspecté**.
>
> | | |
> |---|---|
> | **la conduite de retour** | **toujours immédiate et non synchronisée** — elle **ne dépend d'aucune confirmation**, et n'attend rien |
> | **le `STOP` pour arbitrage** | dû **si et seulement si** le chemin d'échec est **CONFIRMÉ** — par **`D-1`**, le pont ayant redémarré ; ou par la durée atteignant **`P2A-12`** ; ou par **`D-3`** |
> | **à défaut de confirmation** | le lot se clôt sur un **`ABORT` ordinaire**, et le rapport **MUST** consigner la **suspicion** et sa **non-confirmation** |
> | **en cas de doute** | **le doute vaut confirmation** : le `STOP` est dû. En particulier, si `D-1` **ne peut pas être évalué**, le `STOP` **est dû** |
>
> **Motif de la règle, et il n'est pas de commodité.** Le `STOP` de `P2A-5` a pour
> objet le fait que *« le pont aurait été redémarré, ce que le lot s'interdit »*.
> **Si le pont n'a pas été redémarré, ce motif est absent** — et `D-1` l'établit
> directement. **La sûreté, elle, n'est pas conditionnée** : le retour part
> immédiatement dans tous les cas.

> **Ce sont des garde-fous, pas des mesures.** L'enveloppe **n'est ni `M6` ni une
> borne** — `w4p1-homologation.md` §7 —, et la comparer à un seuil d'arrêt **ne
> la requalifie pas**. Elle **contient** la ou les sondes de l'invocation : une
> enveloppe sous le seuil **suffit** à établir qu'aucune sonde ne l'a franchi, ce
> qui fait du garde-fou un majorant **conservateur** — et **rien de plus**.

> **L'`ABORT` de `W4-P2` a quelque chose à défaire**, contrairement à celui de
> `W4-P1` : la phase 3 **MUST** être conduite intégralement, et les preuves du §7
> produites, **y compris après un `ABORT`**.
>
> **Exception, et une seule** : sous `P2A-2` et `P2A-3`, **aucun redémarrage n'a
> eu lieu**. Le retour se réduit alors à la séquence suivante, **et à elle
> seule** :
>
> | Ordre | Acte | Pourquoi |
> |---|---|---|
> | 1 | **`S1`** | supprimer le fichier et le répertoire de surcharge |
> | 2 | **`S2`** | recharger la configuration systemd et vérifier que l'invocation résultante est **identique à celle du préflight** |
> | 3 | **`S7`** | **constater l'absence** du répertoire et du fichier — la preuve `R1` est due **aussi dans ce cas** |
> | 4 | **`S4`, RESTREINT AUX EMPREINTES** | relever les empreintes de `<config-démon>` et du fichier d'unité, et les comparer au préflight — la preuve **`R2`** est due, et la V4 l'avait **omise** |
> | 5 | **`O4`** | **consigner le relevé partiel** — la preuve `R7` est due |
>
> **`S4` est ici limité à la preuve d'invariance des fichiers d'origine.** Son
> volet « invocation effective du processus » est **sans objet** : le processus
> n'a pas été redémarré, et le relire n'apprendrait rien. **Aucune lecture
> inutile, aucun processus interrogé sans nécessité.**
>
> **Le reste, par nature :**
>
> | | |
> |---|---|
> | **`S3`** | **INTERDIT** — redémarrer ici **introduirait** l'interruption que l'`ABORT` vient précisément d'éviter |
> | **`S5`** | **sans objet** — il porte sur les lignes produites **après un redémarrage de retour** qui n'a pas lieu |
> | **`S6`** | **sans objet** — le processus n'a pas été touché, sa qualité de détenteur unique n'a pas été mise en cause |
> | **`S8`** | **sans objet** — `R5.d` compare un état **après redémarrage** ; sans redémarrage, la référence du préflight fait foi |
>
> **Et le sort de chaque preuve, explicitement :**
>
> | Preuve | Sort | Motif |
> |---|---|---|
> | **`R1`** | **DUE** — portée par `S7` | le répertoire de surcharge a bien été créé, puis supprimé |
> | **`R2`** | **DUE** — portée par `S4` restreint | les fichiers d'origine doivent être prouvés invariants |
> | **`R3`** | **SANS OBJET** | elle compare l'**invocation effective du processus** ; le processus **n'a pas été redémarré**, son invocation ne peut donc pas avoir changé. `S2` a par ailleurs vérifié l'invocation **résultante** de l'unité |
> | **`R4`** | **SANS OBJET** | elle porte sur les lignes **produites après le redémarrage de retour** — lequel n'a pas lieu |
> | **`R5.a` à `R5.d`** | **SANS OBJET** | `S5`, `S6` et `S8` le sont, et pour les mêmes motifs |
> | **`R6`** | **SANS OBJET** | elle chiffre le **volume ajouté sous verbosité élevée** ; la fenêtre n'a **jamais été ouverte**, et le lot n'a **rien ajouté** au journal |
> | **`R7`** | **DUE** — portée par `O4` | un `ABORT` a eu lieu |

> **`O4` est admissible dans TOUTE phase**, dès qu'un `ABORT` survient — phase 0,
> 1, 2 ou 3 — et **jamais** en dehors de ce cas. La V3 le rangeait dans la seule
> phase 2, ce qui laissait `R7` sans acte pour les `ABORT` des autres phases.

### 8.2 `STOP`

Les quatre cas du `w4p-ouverture.md` §10.1 s'appliquent sans allègement. S'y
ajoute, **propre à ce lot** : **toute nécessité de modifier le pont historique**
— même transitoirement, même pour réparer — est un **`STOP` pour nouvel
arbitrage humain**, et **jamais** une décision du lot.

> **Un `STOP` n'est pas une issue**, et les verdicts du §5 **ne sont pas** l'issue
> de `W4-P`.

### 8.3 Détection du chemin d'échec, et conduite du retour

**Le budget est celui de `F-12`, et il est déclaré : 90 s.** Le superviseur, sur
échec de sonde, **redémarre le pont**, **attend 90 s**, puis resonde. **Si cette
seconde sonde échoue, il redémarre la machine.** Tout ce qui suit tient dans cet
intervalle, ou ne s'y engage pas.

#### 8.3.1 Trois détecteurs, dont deux indépendants des lignes propres

> **Correction de fond de la V2.** Elle faisait du journal du superviseur le
> **canal unique**. Or `w4p1-homologation.md` §7 homologue que **24 invocations
> sur 76 ne produisent aucune ligne propre**. Un échec de sonde pouvait donc
> survenir **sans trace lisible**, et le garde-fou serait resté muet.
>
> **Aucune hypothèse n'est formée sur la cause de ces absences.** Le fait suffit :
> **on ne peut pas compter dessus**, et la détection est refondée sans elles.

| Réf | Détecteur | Ce qu'il établit | Dépend d'une ligne propre ? |
|---|---|---|---|
| **`D-1`** | l'**identifiant d'invocation** ou l'**instant de démarrage** de `<unité-pont>` **change** | le pont **a été redémarré** — le chemin de `F-12` est **engagé** | **non** |
| **`D-2`** | la durée écoulée depuis l'instant de démarrage d'une invocation de `<unité-superviseur>` — **terminée ou EN COURS** — atteint le seuil de **`P2A-12`**, soit **`10 s`**. **`P2A-11` n'y entre PAS** | le chemin d'échec est **engagé ou suspecté** : la conduite déclarée y insère un **sommeil de 90 s**, qui allonge l'invocation d'un ordre de grandeur | **non** |
| **`D-3`** | une **ligne propre** de `<unité-superviseur>` signale autre chose qu'un cycle nominal | confirmation | **oui** — **jamais utilisé seul**, et son absence ne vaut **rien** |

> **`D-1` et `D-2` portent sur des états que systemd tient pour TOUTES les
> invocations** — `w4p1-homologation.md` l'établit : les enregistrements de cycle
> de vie étaient présents pour **76 sur 76**. **`D-3` est un bonus, jamais un
> prérequis.**

#### 8.3.2 Le canal, la fréquence, et ce qu'elles bornent réellement

| | |
|---|---|
| **Canaux** | l'**état des unités**, relevé par consultation de leurs propriétés courantes — pour `D-1` et `D-2` ; le **journal système de la seule `<unité-superviseur>`**, lu rétrospectivement — pour `D-3` |
| **Fréquence maximale** | un relevé **au plus toutes les 15 s** pendant toute la fenêtre. **Aucun suivi continu, aucune session ouverte** |
| **Ce que cette fréquence borne** | **l'intervalle entre deux observations du lot**, et **rien d'autre** |

> **Ce qu'elle ne borne PAS, et la V2 prétendait le contraire.** Elle ne borne
> **pas** la latence de détection : entre l'événement et sa visibilité s'ajoutent
> des délais **non établis**. *« ≤ 15 s + un délai inconnu »* **n'est pas une
> borne**, et cette formulation est **retirée**.
>
> **La fréquence est donc un choix de conduite, pas une garantie** — et le §8.4
> la range parmi les seuils choisis.

#### 8.3.3 La marge restante, calculée sur un observable

La V2 basculait de conduite à **45 s**, valeur **arbitraire**. Elle est
**supprimée**. Ce qui la remplace se **calcule** :

| Grandeur | Origine |
|---|---|
| `t_départ` — instant de démarrage de l'invocation en cause | **observé**, propriété de l'unité |
| **90 s** — sommeil déclaré avant la seconde sonde | **dérivé du corpus**, `F-12` |
| **5 s** — budget déclaré de la sonde | **dérivé du corpus**, `A-O2` homologué |

> **La seconde sonde ne peut pas commencer avant `t_départ + 90 s`**, la sonde en
> échec étant elle-même contenue dans l'invocation et bornée à 5 s déclarés.
> **La marge restante à l'instant `t` est donc au moins `t_départ + 90 s − t`**, et
> elle se calcule à chaque relevé.

#### 8.3.4 Conduite — et la règle de sûreté qui la commande

> **RÈGLE DE SÛRETÉ.** Dès qu'un échec est **suspecté**, la verbosité élevée
> **MUST NOT** être laissée volontairement en place pour traverser la seconde
> sonde, **si une conduite plus sûre est disponible**. La conduite plus sûre est
> le **retour immédiat**, et c'est la conduite par défaut.

| Cas | Conduite |
|---|---|
| **marge restante suffisante** — elle **excède `30 s`**, soit les **`10 s`** de vérification de `P2A-4` augmentées d'une **réserve CHOISIE de `20 s`** | **conduire le retour immédiatement**, sans attendre aucune frontière de cycle : la synchronisation du §4.1 est **suspendue** |
| **marge restante insuffisante**, ou vérification de `P2A-4` **non obtenue** dans son délai | **`STOP` immédiat et arbitrage humain.** Le lot **ne choisit pas** entre deux conduites risquées |

> **La réserve de `20 s` est ÉCRITE ici, et c'est un choix.** La V3 la renvoyait
> au §9, qui la renvoyait au §8.3.4 : **circulaire, et sans valeur nulle part**.
> Elle couvre ce que `P2A-4` ne couvre pas — le délai entre la décision et le
> lancement effectif du retour, et l'écart entre la vérification et la reprise
> réelle du service. **Rien ne la dérive d'une pièce** : elle est soumise au §9.

> **Il n'y a pas de troisième branche, et il faut le dire.** Dans le second cas,
> **aucune conduite n'est sûre** : redémarrer près de la seconde sonde peut la
> faire échouer ; ne rien faire la laisse s'exécuter sous verbosité élevée. **Le
> lot déclare l'impasse plutôt que d'arbitrer un risque qui ne lui appartient
> pas** — et c'est une raison de plus de relever fréquemment.

> **La durée d'un redémarrage n'est établie nulle part**, et ce lot ne la mesurera
> pas pour se préparer. C'est pourquoi la marge est comparée à une **vérification**
> — `P2A-4` — et non à une prédiction.

### 8.4 Trois natures de valeur, et ce lot n'en produit qu'une seule sorte

| | **Dérivée du corpus** | **Choisie humainement** | **Produite comme résultat** |
|---|---|---|---|
| Ce que c'est | une valeur **lue** dans une pièce opposable | une **règle de conduite** du lot | une **valeur opposable** qui juge un système |
| Qui la fixe | **personne** — elle est déjà là | le bornage, **sous réserve de l'autorisation** | un producteur de critère, sous le §10.3.3 |
| Soumise à l'autorisation ? | **non** — la soumettre laisserait croire qu'elle se négocie | **oui**, et le §9 les énumère | sans objet |
| Ce qu'elle vaut hors du lot | ce que sa pièce lui donne | **rien** | elle devient contractuelle |

**Les valeurs DÉRIVÉES employées ici, et leur pièce :**

| Valeur | Pièce |
|---|---|
| **5 s** — budget de la sonde ; **fixe `P2A-11`** | `A-O2` homologué, registre configuration déclarée |
| **90 s** — sommeil avant la seconde sonde ; base du calcul du §8.3.3 | `F-12`, même registre |
| **180 s** — cadence, tolérance ne pouvant que retarder ; base de la marge du §4.2 | `A-O4` homologué |
| **7 lignes par session** — plancher de volume du §3.2 | `w4-cadrage-activation-debug.md` §E.1 |

**Les valeurs CHOISIES, toutes soumises au §9 :**

| Valeur | Ce qu'elle règle |
|---|---|
| **15 min** · **3 cycles** | la fenêtre (§4.1) |
| **au plus 15 s** | l'intervalle entre deux relevés (§8.3.2) — **pas** une latence de détection |
| **10 s** *(vérification)* | le délai de vérification après un redémarrage — `P2A-4` |
| **10 %** et **100 Mio** | espace libre et croissance du journal — `P2A-7` |
| **`10 s`** *(détection)* | le seuil de `P2A-12`, **au-dessus du régime observé** et **sous la signature du chemin d'échec** |
| **`20 s`** | la réserve exigée en sus des `10 s` de vérification, d'où le **`30 s`** du §8.3.4 |

> **Les deux `10 s` ne sont pas la même valeur** et ne se déduisent pas l'une de
> l'autre : l'une borne une **vérification après redémarrage**, l'autre un
> **seuil de détection**. Leur égalité numérique est **fortuite**, et chacune est
> soumise séparément.

> **Chacune de ces valeurs est ÉCRITE à l'endroit où elle s'applique**, et
> reprise ici pour mémoire. **Aucune n'est définie par renvoi** : la V3 en
> laissait deux dans un cycle de renvois où la valeur n'existait nulle part.

> **`W4-P2` ne produit AUCUNE valeur de la troisième colonne.** Aucun de ses
> seuils — dérivé ou choisi — ne **MUST** être repris, cité ou dérivé comme valeur
> de critère, de `seuil_C1`, de `borne_sonde` ou d'`occupation_max`. **Les
> confondre serait produire par la porte de service ce que la clause de
> non-dérivation interdit.**

> **Et une valeur dérivée ne devient pas un choix parce qu'un lot s'en sert.** Le
> budget de 5 s et le sommeil de 90 s **ne figurent pas** au §9 : les soumettre
> laisserait croire qu'ils se négocient, alors qu'ils sont **des faits déclarés de
> l'installation**.

## 9. Élément 6 — Autorisation propre

> ### **NON DONNÉE.**
>
> `w4q-precondition2-arbitrage.md` décision 5 exige *« son **autorisation propre**,
> distincte de la présente »*. **Ce document ne la constitue pas.**
>
> **`W4-P2` MUST NOT être exécuté, même partiellement, avant que cette
> autorisation soit donnée.** La phase 0 elle-même, bien qu'en lecture, **attend**.

**Ce que l'autorisation devra dire, pour être suffisante :**

| # | Point à trancher |
|---|---|
| 1 | qu'elle **autorise `W4-P2`** tel que borné ici, **et rien d'autre** |
| 2 | qu'elle **autorise nommément la mutation** — création d'une surcharge portant `-g` — et **les deux redémarrages** de `<unité-démon>` qu'elle implique |
| 3 | si le **plafond de 15 minutes** et le **minimum de 3 cycles** sont retenus |
| 3 bis | si les **valeurs CHOISIES** sont retenues, **chacune nommée avec sa valeur** : **15 s** d'intervalle entre relevés · **10 s** de vérification après redémarrage, `P2A-4` · **10 %** d'espace libre et **100 Mio** de croissance, `P2A-7` · **`10 s`** de seuil de détection, `P2A-12` · **`20 s`** de réserve, portant le seuil du §8.3.4 à **`30 s`**. **Ce sont des choix de bornage, au même titre que la fenêtre** |
| 3 ter | **rien d'autre n'est soumis.** Les valeurs **dérivées** — budget de 5 s portant `P2A-11`, sommeil de 90 s, cadence de 180 s, plancher de 7 lignes — **ne sont pas des choix** et ne figurent pas ici. La **bascule à 45 s de la V2 est supprimée**, et rien ne la remplace : la marge se **calcule** (§8.3.3) |
| 3 quater | **`P2A-11` n'y figure pas** : il vaut **`5,000 s`**, le budget **dérivé**, et n'est donc pas un choix. **Le faux positif qu'il comporte est assumé au §8.1**, et l'autorisation vaut acceptation de cet effet — un `ABORT` ordinaire possible sur un cycle nominal |
| 4 | qu'elle **n'autorise ni `T0`, ni `T1`, ni `T2`**, aucune modification du pont ou du superviseur, aucun des quatre actes réservés |

## 10. Ce que ce document ne fait pas

Il **n'exécute rien**, **n'autorise rien**, **ne mute rien**, **ne relève aucune
mesure d'expérience**, **ne produit ni `M6`, ni borne, ni seuil, ni critère**,
**ne rouvre pas `C1`**, **ne rouvre pas la discrimination par `Command:`**,
**n'ouvre pas `T0`**, et **ne traite aucune réserve rédactionnelle de `W4-P1`**.

Il borne un lot, et s'arrête là.

## 11. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture et bornage du second lot terrain de `W4-P`, visant l'observabilité des clôtures et la dérivabilité d'une durée de session. Voie surcharge retenue sur faits d'audit, voie XML écartée. Six éléments réunis ; **élément 6 non donné**. Aucune exécution, aucune mutation, aucune autorisation. |
| **2** | Après audit. `BL-1` : marge de synchronisation refondée sur la **cadence déclarée** et le **budget déclaré de 5 s**, l'enveloppe de `W4-P1` cessant d'y servir de borne de sonde ; objectifs renommés `P2-O1`…`P2-O5` pour lever la collision avec `B-O1`/`B-O2` homologués. `BL-2` : §8.3 — canal, fréquence maximale de 15 s, latence bornée, synchronisation suspendue, et règle en deux branches pour que le retour ne provoque pas lui-même la seconde sonde en échec. `BL-3` : §5.1 — le §E.3 devient un **risque de sûreté**, avec `P2A-11` et `P2A-12` opposables, **sans qualifier `C1` ni produire de borne**. `BL-4` : quatrième constat de sortie restauré — processus unique, **détenteur du périphérique** par deux méthodes indépendantes, service des clients — avec les actes `S4` à `S6` ajoutés à la liste close. `C-1` volume corrigé à **2 996**. `C-2` §8.4, seuils internes distingués des seuils produits. `C-3` seuils de `P2A-7` soumis à l'autorisation. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **3** | Après réaudit. `RB-1` : le journal du superviseur cesse d'être le canal unique — trois détecteurs, dont deux **indépendants des lignes propres**, `W4-P1` ayant homologué que 24 invocations sur 76 n'en produisent aucune ; **aucune hypothèse sur la cause des absences**. `RB-2` : la fausse borne *« ≤ 15 s + délai inconnu »* est retirée, la **bascule arbitraire à 45 s supprimée**, la marge **calculée** sur un observable à partir des 90 s déclarées, et la règle de sûreté sur la seconde sonde énoncée avec son impasse assumée. `RB-3` : actes `S7`, `S8` et `O4` ajoutés — `R1`, `R5.d` et `R7` avaient une preuve sans acte. `RB-4` : §8.4 distingue **dérivé**, **choisi** et **produit** ; `P2A-11` cesse de référer à une population non homogène et repose sur une fraction du budget dérivé ; `P2A-12` demeure dérivé. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **4** | Après troisième réaudit. `RB3-1` : les deux seuils sans valeur — fraction de `P2A-11` et réserve du §8.3.4 — reçoivent **`0,80`**, soit **`4,000 s`**, et **`20 s`**, soit un seuil de **`30 s`** ; le **renvoi circulaire est supprimé** et chaque valeur est classée dérivée ou choisie, les choisies étant soumises nommément. `RB3-2` : `P2 bis` relève au préflight les **références du pont et du superviseur**, sans lesquelles `D-1` et `P2A-6` étaient **inopérants au premier redémarrage** ; `S8` demeure la mesure finale. `RB3-3` : l'exception `P2A-2`/`P2A-3` est complétée par `S7` et `O4`, `S3` restant interdit ; `O4` devient admissible **dans toute phase** sur `ABORT`. `C-4` premier bras de `D-2` quantifié. `C-5` tolérance de 10 s retirée. `C-6` phrase sur les valeurs de site corrigée. `C-7` ordre de l'historique rétabli. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **5** | Après quatrième réaudit. `RB4-1` : `P2A-11` valait **`4,000 s`**, **sous le régime observé de `4,682 s`** — un cycle nominal aurait été interprété comme le chemin d'échec de `F-12`, régression du type `P2A-3c`. Les deux garde-fous sont **refondus et découplés** : `P2A-11` devient un `ABORT` **ordinaire** d'allongement au budget **dérivé** de `5,000 s`, **faux positif assumé**, **sans alimenter `D-2` ni `P2A-5`** ; `P2A-12` devient la **détection du chemin d'échec** au seuil **choisi** de `10 s`, au-dessus du régime observé et neuf fois sous la signature de 90 s, et **lui seul** alimente `D-2`. **Aucune borne n'est dérivée de `W4-P1`.** `RB4-2` : le tableau du §6.1 est réparé — `P1`, `P2`, `P2 bis`, `P3`, `P4` contigus, note hors tableau. `RB4-3` : la séquence d'`ABORT` sous `P2A-2`/`P2A-3` devient `S1` → `S2` → `S7` → `S4` **restreint aux empreintes** → `O4`, `R2` ayant été omise ; `S3` interdit, `S5`, `S6`, `S8` sans objet. `C-8` formulation de `C-5` précisée. `C-9` état de `<unité-démon>` rétabli au préflight. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **6** | Après cinquième audit. `RB5-1` : la **précédence** entre `P2A-11` et `P2A-12` est réglée au §8.1.1 — `P2A-12` **prévaut toujours** dès qu'il est atteint ; les relevés **`[5 s, 10 s)`** et **`≥ 10 s`** sont traités séparément, et l'état **terminé ou en cours** de l'invocation commande la conduite. **Une seule attente demeure permise** — invocation close entre 5 et 10 s — et elle reste sous surveillance préemptable. **Règle absolue posée : aucune attente volontaire à travers les 90 s du chemin de `F-12`.** `RB5-2` : la mention résiduelle de *« fraction choisie »* pour `P2A-11` est retirée — **`5,000 s` est dérivé de bout en bout**, et n'est soumis nulle part. `C-10` ordre du §9 rétabli. `C-11` sort de `R3`, `R4` et `R6` explicité comme **sans objet** sous `P2A-2`/`P2A-3`. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **7** | Après sixième audit. `RB6-1` : `O2`, acte de la seule phase 2, est **étendu à la phase 3** pendant toute attente d'un retour synchronisé `S1` — la surveillance et la préemption du §8.1.1 étaient jusque-là **prescrites sans acte permettant de les observer**. L'extension est bornée par son objet, sa fréquence inchangée et **deux termes nommés** : exécution effective du retour, ou préemption par `P2A-12`. **Aucune autre extension de périmètre.** `C-12` : la ligne vive de `P2A-11` au §8.1 annonçait un retour synchronisé sans réserve — alignée sur le §8.1.1, invocation **en cours** valant retour **non** synchronisé. `C-13` : le cas `[5 s, 10 s)` **en cours** est tranché — retour **toujours** immédiat, `STOP` dû **si et seulement si** le chemin d'échec est confirmé, **le doute valant confirmation**. **Aucune exécution, aucune mutation, aucune autorisation.** |
