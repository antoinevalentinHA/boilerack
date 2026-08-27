# `G.2` — observabilité de preuve

> **Version 3**, après réaudit. Quatre réserves résiduelles traitées, aucune
> extension de périmètre.
>
> | | Correction |
> |---|---|
> | **S-1** | **§5.1 complété** : interdiction explicite de **retenir** et de **publier** les octets bruts |
> | **S-2** | **Ellipse restituée** : la docstring de `_diagnostic` est citée **sans coupe** — §5.2 |
> | **S-3** | **Motif de R-A corrigé.** La V2 **sur-vendait** `W4-A` §14 : cette clause n'interdit **pas** un observateur injecté. L'argument décisif est `W4-A` §7.3 — §5.1 |
> | **S-4** | **Obsolescence prévue** : la docstring de `_diagnostic` **MUST** être mise à jour par l'étape 3 — §5.5 |
>
> Corrections de la **Version 2**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **R-A** | **La forme est tranchée** : le porteur est **`WriteResult`**. La voie « porteur distinct » est **abandonnée** — motif **corrigé en V3**, voir **S-3** — §5.1 |
> | **R-B** | **L'obligation 11 de `W4-A` §18 est rouverte nommément**, et l'autorité du lot pour étendre `WriteResult` est fondée sur `W4-A` §7.3 — §5.2 |
> | **R-C** | **Coût réel de la durée consigné** : injection d'une `Clock` dans `VClientCli`, 15 sites de construction, câblage en `lifecycle.py` — §5.3 |
> | **§3** | **Correction d'un fait faux.** La V1 affirmait qu'aucun compteur monotone n'existait hors de `clock.py`. **C'est faux** : `clock.monotonic()` est employé en production en six modules. Le manque porte **uniquement** sur le chemin d'écriture |
> | **§4.2** | **Interdiction explicite** de journaliser `stdout` / `stderr` **intégraux** |
> | **§7** | **Décompte de `PR-1` corrigé** — cinq sorties, non quatre |
>
> **Aucun code dans ce lot.** Il n'écrit rien, ne modifie aucun module, n'ouvre
> aucune capacité d'écriture, et **ne valide rétroactivement rien**.
>
> **Convention de citation.** Toute référence externe porte son nom court —
> `G.2` pour `w4f-g2-ecriture-bornee.md`, `W4-A` pour
> `w4a-vclient-write-adapter.md`, `W4-C` pour `w4c-write-capture-protocol.md`,
> `W1` pour `w1-mqtt-transaction-surface.md`. Une référence sans nom court
> désigne le présent document.

---

## 1. Objet et frontières

Ce document fait **une seule chose** : il cadre ce qu'il faut rendre observable
pour qu'une campagne `G.2` puisse être **close**, et il en désigne le chemin
minimal.

Il **n'amende** ni `G.2`, ni `W4-A`, ni `W4-C`. Il ne rouvre pas `W4-F2`,
n'ouvre pas `W4-F3`, ne touche pas à l'index du corpus, et **ne modifie aucune
décision métier**.

> **La campagne du 2026-08-27 reste ce qu'elle est** : une **preuve physique
> solide** — 2 → 3 → 2, relectures strictes, dispositif restauré — et une
> **campagne non close** au sens du §16 de `G.2`. Ce lot ne cherche pas à
> requalifier ce qui a eu lieu. Il prépare ce qui permettrait à une **campagne
> ultérieure** d'être close.

---

## 2. Le manque, exactement

`G.2` §16 énumère les preuves de sortie. Deux de ses items ne sont pas
productibles en l'état.

### 2.1 Item 4 — les preuves de transport

> *« l'écriture, avec sa **ligne d'invocation réelle**, `stdout` et `stderr`
> **intégralement et séparément**, **code retour** et **durée mesurée** —
> `W4-A` §19, champs 2 à 5 »*

**Aucun de ces cinq éléments n'est accessible à l'appelant.** Quatre sont
produits à l'intérieur de l'adaptateur puis **jetés** ; le cinquième — la durée
— n'est **pas mesuré** sur ce chemin.

### 2.2 Item 1 — les sorties brutes des preuves `EI`, `PR` et de la reprise

> *« les treize preuves `EI-1..EI-13`, chacune avec sa **méthode**, sa **sortie**
> et son **horodatage** »*

Les méthodes ont été employées et leurs résultats rapportés, mais **les sorties
brutes n'ont pas été capturées en fichiers**. Elles n'existent que dans le
transcript de la session, ce qui n'est pas un artefact transmissible au sens de
`W4-C` §10.

**Ce second manque n'est pas un défaut de code.** C'est une **discipline de
capture** absente — §7.

---

## 3. Ce que le code produit, et ce qu'il jette

Faits relevés dans l'arbre à `8010c51f`, non supposés.

| Élément | Où il existe | Ce qu'il devient |
|---|---|---|
| **ligne d'invocation réelle** | `Invocation.args`, construite dans `VclientWriteInvocation.build` | reste locale à `write()` |
| **`stdout` intégral** | `ProcessResult.stdout`, **octets bruts** | lu pour classer, puis **jeté** |
| **`stderr` intégral** | `ProcessResult.stderr`, **octets bruts** | idem |
| **code retour** | `ProcessResult.returncode` | idem |
| **durée mesurée** | **n'existe pas sur ce chemin** | — |

```python
@dataclass(frozen=True)
class WriteResult:
    status: TransportStatus
    detail: str = ""
```

`WriteResult` — `transport/vclient.py` — ne porte que deux champs. Tout le reste
est perdu au retour de `_classify_write`.

### 3.1 Correction d'un fait affirmé à tort en V1

> **La V1 écrivait** : *« aucun appel à un compteur monotone n'existe hors de
> `clock.py` »*. **C'est faux, et l'audit a raison de le relever.**

`clock.monotonic()` est employé **en production**, en six modules :
`core/dedup.py`, `core/engine.py`, `read_surface/publisher.py`,
`read_surface/snapshot.py`, `read_surface/state.py`, `runtime.py`.

> **Le manque est donc étroit, et c'est une bonne nouvelle.** La mesure de durée
> n'est ni à concevoir, ni à introduire dans le corpus : elle y est **établie,
> injectée par `Clock`, doublée en test par `VirtualClock`**. Elle **manque
> uniquement sur le chemin d'écriture**, qui ne reçoit aucune horloge.

### 3.2 L'asymétrie était déjà nommée par `W4-A`

`W4-A` **§7.3 « Insuffisance signalée de `WriteResult` »** l'avait constatée
avant ce lot, et il faut le lui rendre :

> *« `ReadResult` porte `raw`, qui conserve la sortie observée ; `WriteResult` ne
> le porte pas. Or W4-C devra capturer `stdout` et `stderr` d'une écriture
> réelle, et un adaptateur qui n'a nulle part où les déposer **ne peut pas les
> rendre à un appelant**. »*

Le présent lot ne découvre rien : il constate que la conséquence annoncée s'est
produite, et sur un consommateur que `W4-A` n'avait pas prévu.

---

## 4. Ce que `W4-A` §17 autorise, interdit, et laisse en tension

`W4-A` **§17 « Journalisation »** :

> **Clause.** L'adaptateur **MAY** journaliser : le nom logique de la commande,
> la valeur transportée, **le code retour**, **la durée observée** et un extrait
> de diagnostic **borné**. Il **MUST NOT** journaliser un secret de
> configuration, et **MUST NOT** créer de système d'observabilité nouveau : **ni
> métrique, ni compteur, ni fichier.**

Et, juste après :

> *« `stdout` et `stderr` **MAY** être journalisés bornés, et **MUST** être
> capturés intégralement pour W4-C — ce sont deux besoins distincts. »*

`W4-A` §18, obligation **5** : l'adaptateur **MUST** *« capturer `stdout`,
`stderr` et le code retour séparément »*. Il le fait — et ne les rend pas.

### 4.1 La tension, nommée

Le partage de §17 — *« journalisés bornés »* d'un côté, *« capturés
intégralement pour W4-C »* de l'autre — **suppose le modèle de `W4-C`**, où
**l'exploitant lance lui-même `vclient`** et redirige ses sorties.

**`G.2` inverse ce modèle** : c'est **Boilerack** qui lance l'invocation.
L'exploitant n'a plus accès aux octets bruts, et **seul l'adaptateur les
détient**.

> **Conséquence.** Sous `G.2`, la capture intégrale exigée par §16 item 4 **ne
> peut venir que de l'adaptateur** — or §17 lui interdit de créer un fichier, et
> ne lui accorde qu'une journalisation **bornée** de `stdout` et `stderr`.
>
> Ce n'est pas une contradiction rédactionnelle : c'est une **frontière que
> `W4-A` n'avait pas à franchir**, parce qu'aucune campagne n'écrivait alors
> **par** Boilerack.

### 4.2 Interdiction, posée ici et sans exception

> **Clause.** Boilerack **MUST NOT** journaliser `stdout` ni `stderr`
> **intégraux**, sous aucun niveau, dans aucun module, et quelle que soit la
> suite donnée à ce cadrage.
>
> `W4-A` §17 ne les admet au journal que **bornés**. `_diagnostic` les borne
> aujourd'hui, par `_borner`, et **MUST** continuer à le faire.
>
> **Rendre n'est pas journaliser.** L'observation intégrale est **rendue à
> l'appelant**, qui en dispose ; elle ne **passe pas** par le journal. Une
> journalisation intégrale créerait un volume non borné, exposerait la sortie du
> transport à toute destination de journal configurée, et déborderait le `MAY`
> de §17.

---

## 5. La conception, tranchée

### 5.1 R-A — le porteur est `WriteResult`

> **Décision.** L'observation est portée par un **champ optionnel de
> `WriteResult`**, absent par défaut. La voie « **porteur distinct**, remis par
> un observateur injecté » est **abandonnée**.

**Motif décisif — `W4-A` §7.3, et lui seul.** La clause qui désigne le lieu de
l'ajout le nomme :

> *« soit `detail` suffit pour le diagnostic, **soit W4-B propose l'ajout d'un
> champ** […] »*

**« Un champ »** — sur `WriteResult`. `W4-A` n'a jamais envisagé un porteur
tiers ; il a désigné le porteur existant. Retenir `WriteResult` suit la clause,
et un porteur distinct s'en écarterait.

> **Ce que la V2 sur-vendait, et qui est retiré.** Elle affirmait qu'un
> observateur injecté **exigerait un amendement de `W4-A` §14**. **C'est faux.**
> §14 interdit *« verrou, fil, file ou travailleur d'arrière-plan »* — un
> observateur n'est aucun des quatre — et pose l'adaptateur *« synchrone et sans
> état **au-delà de sa configuration** »* : un collaborateur **injecté à la
> construction** fait précisément partie de cette configuration.
>
> **§14 ne l'interdit donc pas.** Ce qu'on peut en dire honnêtement est plus
> faible : un canal d'émission latéral **consonne mal** avec un adaptateur que
> §14 veut synchrone et sans état, et il exigerait de câbler un consommateur que
> personne ne réclame. C'est un argument de **cohérence et de sobriété**, pas
> une interdiction.

**Ce que `WriteResult` reçoit** — à arrêter en contrat, non ici :

- la **ligne d'invocation** telle qu'exécutée (`Invocation.args`) ;
- **`stdout` brut** et **`stderr` brut**, séparés, non décodés ;
- le **code retour** ;
- la **durée** mesurée autour de la seule invocation.

> **Clause exigée, sur la forme exacte de `W1` §11.4.** Le cœur transactionnel
> **MUST NOT** fonder le moindre comportement sur cette observation, et
> **MUST NOT** modifier la signature de `VClient.write` pour la récupérer.
> L'observation est une **trace**, jamais une **entrée de décision**.
>
> `W1` §11.4 dit la même chose de `submit` : *« Le lot de câblage **MUST NOT**
> fonder de comportement sur la valeur rendue […]. »* Le précédent est exact, et
> il est repris tel quel.
>
> Sans cette clause, la décision serait déplacée sur une donnée que `W4-C` §16.4
> interdit déjà d'interpréter : *« Le champ `value` d'une réponse d'écriture
> **MUST NOT** être interprété comme […] une confirmation que quoi que ce soit a
> été appliqué. »* **La confirmation métier reste une relecture séparée.**

> **Clause — ni rétention, ni publication.** Les octets bruts sont **rendus à
> l'appelant immédiat, et à lui seul**.
>
> - **Aucune rétention.** Ni l'adaptateur, ni le cœur, ni la surface
>   transactionnelle **MUST NOT** conserver l'observation au-delà de l'appel qui
>   l'a produite : pas de champ d'instance, pas de liste, pas de cache, pas de
>   dernier-résultat. `W4-A` §14 pose l'adaptateur *« sans état au-delà de sa
>   configuration »*, et une observation retenue serait de l'état.
> - **Aucune publication.** L'observation **MUST NOT** être publiée sur MQTT,
>   sous aucun topic, sous aucune forme, ni entière ni extraite. Les topics
>   d'`ACK` gardent exactement le contenu que `W1` leur donne.
> - **Aucun fichier.** `W4-A` §17 l'interdit, et ce lot ne le demande pas.
>
> **Ce que « rendre » veut dire, exactement** : l'observation voyage **dans la
> valeur de retour**, l'appelant en fait ce que son propre contrat lui permet, et
> elle disparaît avec elle. Sous `G.2`, cet appelant est **l'exploitant de la
> campagne**, qui la consigne dans son atelier — §7.

### 5.2 R-B — l'obligation 11 est rouverte, et l'autorité est fondée

`W4-A` §18, obligation **11** : *« trancher explicitement la question de
`WriteResult.raw` (§7.3) »*.

**W4-B l'a tranchée**, et son arbitrage est consigné **dans le code**, à
`adapters/vclient_write.py`, docstring de `_diagnostic` :

> *« **`detail` suffit, et aucun champ n'est ajouté.** Le seul besoin qui
> exigeait la sortie INTÉGRALE d'une écriture était la capture de W4-C — or W4-C
> a eu lieu, et l'a capturée **hors du code**, dans des fichiers dédiés. **Ce qui
> reste utile à l'exécution est un diagnostic, et un diagnostic se borne.**
> Ajouter un champ à la taxonomie de transport pour un besoin **désormais
> satisfait ailleurs** serait un **élargissement sans consommateur** — et
> l'obligation 21 interdit par ailleurs à W4-B de modifier la taxonomie. »*

> **L'ellipse de la V2 masquait la meilleure phrase de cet arbitrage**, et il
> faut la restituer : *« Ce qui reste utile à l'exécution est un diagnostic, et
> un diagnostic se borne. »* **Elle reste vraie, et ce lot ne la contredit pas.**
> `detail` demeure **borné**, à l'exécution, pour le diagnostic. L'observation
> intégrale répond à un **autre besoin** — la preuve d'une campagne — et c'est
> pourquoi elle ne passe ni par `detail`, ni par le journal.

> **Les deux prémisses de cet arbitrage sont tombées, et c'est `G.2` qui les a
> fait tomber.**
>
> 1. *« capturée hors du code »* — **impossible sous `G.2`** : l'invocation est
>    lancée **par Boilerack**, et l'exploitant n'a aucun accès aux octets bruts ;
> 2. *« élargissement sans consommateur »* — **le consommateur existe** : c'est
>    `G.2` §16 item 4, qui exige `stdout` et `stderr` **intégralement et
>    séparément**.
>
> L'arbitrage de W4-B **était juste au moment où il a été rendu**. Il ne l'est
> plus, parce que le monde qu'il décrivait a changé. Ce lot ne le corrige pas :
> il constate que sa condition d'application a disparu.

**L'autorité du lot** vient de `W4-A` §7.3 lui-même :

> *« soit `detail` suffit pour le diagnostic, **soit W4-B propose l'ajout d'un
> champ**, ce qui **MUST** faire l'objet d'un **arbitrage explicite** et non d'un
> ajout opportuniste. »*

**Le présent lot est cet arbitrage explicite**, rendu à découvert, avec son
motif, et soumis à audit avant tout code. Il n'est ni opportuniste, ni
silencieux.

> **Ce qui n'est pas touché.** L'obligation **21** interdit de modifier *« `core/`,
> C3, C5 ou **la taxonomie** »*. La taxonomie est le jeu **fermé** de
> `TransportStatus`, arrêté par la table de `W4-A` §9. **Aucun statut n'est
> ajouté, retiré ni redéfini.** Un champ optionnel sur `WriteResult` ne modifie
> pas la taxonomie des issues.

### 5.3 R-C — le coût réel de la durée

La V1 le passait sous silence. Le voici, mesuré.

| Élément | Coût |
|---|---|
| `VClientCli.__init__(config, runner, *, invocation)` | reçoit **`clock: Clock`** en argument nommé |
| `VClientCli(VClientCliReader)` | la classe sert **lecture et écriture** ; **seule `write()`** emploierait l'horloge |
| sites de construction | **15**, dont **14 en tests** — tous à mettre à jour |
| câblage de production | **`lifecycle.py:481`**, dans `fabriquer(mqtt, clock)` — **l'horloge y est déjà en portée**, l'appel gagne un argument |
| test | `VirtualClock` fournit `monotonic()` et `advance()` ; la mesure devient **déterministe** |

> **Le câblage touche la racine de composition**, qui relève de `W4-E`. Le
> changement est d'une ligne et n'introduit aucune dépendance nouvelle — la
> `Clock` est **déjà** celle que `build_transaction_surface` reçoit — mais il
> **doit être dit**, et non glissé.

> **Ce que la durée n'est pas.** Elle est **indicative**. `W4-C` §10 maintient sa
> réserve d'horloge, et `AB-7` sanctionne déjà une durée absurde. **Mesurer n'est
> pas garantir.**

### 5.5 La docstring de `_diagnostic` devient obsolète

L'arbitrage de W4-B est consigné **dans le code**, et le présent lot le rouvre.
Laisser la docstring en l'état ferait mentir le module.

> **Clause.** L'étape 3 **MUST** mettre à jour la docstring de `_diagnostic`
> dans `adapters/vclient_write.py`, pour :
>
> 1. **conserver** l'arbitrage d'origine et son motif — il était juste quand il a
>    été rendu, et l'effacer réécrirait l'histoire ;
> 2. **dater sa réouverture** et en nommer la cause : `G.2` fait de Boilerack
>    l'exécutant de l'invocation, ce que W4-B ne pouvait pas prévoir ;
> 3. **redire ce que `detail` reste** — un diagnostic **borné**, inchangé — et
>    **où** l'observation intégrale se trouve désormais.
>
> Aucune autre docstring du module n'est touchée.

### 5.4 Ce qui reste à trancher, et qui n'est pas tranché ici

1. **Le chemin de lecture** reçoit-il la même durée ? `VClientCliReader` n'a
   aucune horloge ; lui en donner une élargirait le lot au-delà de `G.2`.
2. **Une borne de volume** s'impose-t-elle sur les octets rendus ? Voir la
   réserve 3.
3. **Le nom et le type exact** du champ, et s'il porte les octets bruts ou une
   structure dédiée.

---

## 6. Ce qui **MUST NOT** changer

| Objet | État |
|---|---|
| **décision métier** | inchangée — aucune classification, aucun verdict, aucune relecture n'est touchée |
| **autorité** | inchangée — `transaction_surface.enabled` garde son sens et son défaut fermé |
| **absence de réessai** | inchangée — `W4-A` §13 : *« un échec est une issue, pas une invitation à recommencer »* |
| **budget de temps** | inchangé — `write_timeout_s` conserve sa valeur et son effet |
| **sémantique d'`ACK`** | inchangée — `accepted`, `applied`, `rejected` gardent leur sens |
| **capacité d'écriture** | **aucune nouvelle** — aucun rôle, aucune commande, aucun chemin |
| **taxonomie `TransportStatus`** | **inchangée** — table fermée de `W4-A` §9 |
| **`VClient` Protocol** | signature de `write` **inchangée** |
| **fichier, métrique, compteur** | **aucun n'est créé** — `W4-A` §17 |
| **journal** | `stdout` / `stderr` **jamais intégraux** — §4.2 |

---

## 7. Objectif opératoire — la discipline de capture

Le second manque — §16 item 1 — ne se corrige par aucun code. Il se corrige par
une **discipline**, sur le modèle de `W4-C` §10.

> **Règle.** Pendant une campagne `G.2`, **toute** commande dont une preuve `EI`,
> `PR` ou de reprise dépend **MUST** être exécutée avec ses trois sorties
> redirigées dans l'atelier :
>
> ```
> <NN>-<nom>.out    sortie standard, intégrale
> <NN>-<nom>.err    sortie d'erreur, intégrale, JAMAIS fusionnée
> <NN>-<nom>.meta   commande exécutée, code retour, horodatage
> ```

**Couverture exigée**, une capture par preuve :

| Preuves | Ce qui doit être capturé |
|---|---|
| `EI-1` | relevé de l'état de repos |
| `EI-4` | création de l'atelier et son contrôle hors dépôt |
| **`EI-5` / `PR-1`** | **cinq sorties** — voir §7.1 |
| **`EI-6` / `PR-2`** | état de l'unité **et** décompte des ouvertures sur la fenêtre |
| `EI-7` | état du démon **et** code retour de la lecture nue |
| `EI-8` | inventaire des unités, absence de session, **fenêtre muette** |
| `EI-10` | déjà capturé — deux formes |
| `EI-11` | contenu **persisté**, avant et après |
| `EI-12` | journal du différentiel `$SYS`, horodaté |
| `EI-13` | extraits des trois plans |
| **reprise** | les **cinq étapes**, faits **A**, **B**, **C** séparés |

### 7.1 `PR-1` — cinq sorties, et le décompte de la V1 était faux

> **La V1 annonçait « quatre sorties » et en énumérait cinq.** Correction.

`W4-C` §16.1 pose **trois critères** pour `PR-1` — timer avec prochain tir vide ;
unité d'exécution inactive avec sortie constatée ; aucun processus vivant. Le
troisième s'établit par **trois voies indépendantes**. Cela fait **cinq sorties à
capturer** :

| # | Sortie |
|---|---|
| 1 | état du timer **et** son prochain tir |
| 2 | état de l'unité d'exécution, `Result` et `ExecMainStatus` compris |
| 3 | `ps` sur **arguments complets** |
| 4 | `MainPID` et `ControlPID` |
| 5 | **cgroup** de l'unité |

> **Sonde `PR-1`.** La forme `pgrep -af <script>` **MUST NOT** être employée :
> lancée depuis une session distante, elle **capture sa propre ligne de
> commande** et rend une correspondance fausse. Les sorties 3, 4 et 5 sont la
> forme éprouvée.

> **Ce que la campagne du 2026-08-27 a capturé** : douze fichiers, couvrant
> `EI-10`, l'écriture, les deux `ACK` et les relectures. **Rien de `PR-1`, de
> `PR-2`, de `EI-8`, ni de la reprise.** C'est le manque exact que cette
> discipline comble.

---

## 8. Chemin minimal, ordonné

| # | Étape | Nature |
|---|---|---|
| **1** | **audit du présent cadrage** | documentaire |
| **2** | **contrat** arrêtant les trois points de §5.4, les clauses d'interdiction de §5.1 et de §4.2, et l'obligation de §5.5 | documentaire |
| **3** | **code** — `Clock` injectée, champ d'observation, tests | code, sous contrat |
| **4** | **discipline de capture** §7, écrite en procédure opératoire | opératoire |
| **5** | campagne `G.2` ultérieure — **sous une autorisation humaine nouvelle** | terrain |

> **L'étape 5 n'est pas ouverte, ni préparée, ni rendue plus proche.** La
> dérogation `G.2` s'est éteinte à l'achèvement de la campagne du 2026-08-27, et
> **aucune seconde campagne ne s'en autorise** — `G.2` §3.

---

## 9. Ce que ce document ne fait pas

Il n'écrit aucun code · il ne modifie aucun module · il n'amende ni `G.2`, ni
`W4-A`, ni `W4-C` · il ne demande **aucun** amendement, d'aucune clause · il n'ouvre
aucune capacité d'écriture · il ne valide rétroactivement aucune campagne · il ne
rouvre pas `W4-F2` · il n'ouvre pas `W4-F3` · il ne modifie pas l'index du
corpus · il n'autorise aucun terrain.

---

## 10. Réserves

1. **La tension de §4.1 subsiste.** Le §5.1 tranche la **forme** du porteur, non
   la question de fond : un auditeur peut juger que rendre les octets bruts
   rapproche trop la preuve du chemin de décision, et préférer un amendement de
   `W4-A` §17. La clause de §5.1 est ce qui tient la frontière ; elle vaut ce que
   vaut son respect.
2. **La campagne du 2026-08-27 demeure non close** au sens du §16 de `G.2`, et
   ce lot ne la referme pas. Sa valeur reste **physique**, non contractuelle.
3. **Le volume des sorties brutes n'est pas borné** par ce cadrage. Une écriture
   dont `stdout` serait volumineux chargerait `WriteResult` — un objet que le
   cœur manipule. Le contrat de l'étape 2 devra dire si une borne s'impose, et
   laquelle. **C'est le seul point où le choix de `WriteResult` comme porteur
   coûte plus qu'un porteur distinct.**
4. **La durée mesurée reste indicative** — §5.3, dernier encadré.
5. **`U-3` demeure ouverte**, et aucune capture ne l'y aide : le journal du démon
   ne porte ni clôture ni attribution par client.
