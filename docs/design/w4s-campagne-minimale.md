# `W4-S` — campagne minimale de seconde écriture bornée sur `heating_curve_shift`

> **Version 1.** Ouverture **et** bornage. Le document définit une campagne
> d'écriture réelle, **bornée et réversible**, la referme, et **ne l'autorise
> pas**.
>
> **Aucun terrain n'est conduit par ce document. Aucun code n'est demandé.
> Aucune constante de site n'y figure.**
>
> **L'autorisation humaine est `NON DONNÉE`** — §15.
>
> **Il ne rouvre ni `G.3`, ni `P-A5`**, et ne s'autorise d'aucun des deux — §2.2.

---

## 0. Convention de citation

Les citations sont reproduites **mot pour mot**. Les unités sont désignées
`<unité-boilerack>`, `<unité-pont>`, `<unité-démon>`, `<unité-superviseur>`,
`<timer-guard>`, `<script-superviseur>`.

| Nom court | Document |
|---|---|
| `w4f` | `w4f-write-sovereignty.md` |
| `G2-P` | `w4f-g2-ecriture-bornee.md` — le **protocole** |
| `G2-C` | `w4f-g2-constat.md` — le **constat** |
| `G3` | `w4f-g3-seconde-ecriture-bornee.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `W4-R` | `w4r-attribution-instance-a5.md` |
| `SPT` | `g2-sortie-preuve-transport.md` |
| `W4-A` | `w4a-vclient-write-adapter.md` |
| `W1` | `w1-mqtt-transaction-surface.md` |
| `C5` | `c5-vclient-contract.md` |
| `debug` | `w4-cadrage-activation-debug.md` |

> **Règle de désambiguïsation locale.** `debug` **§G.1** à **§G.4** désignent des
> **classes normatives de régime d'engagement**. `G.1`, `G.2` et `G.3` désignent
> des **actes**. Les premières sont toujours citées **préfixées `debug`**.

---

## 1. Désignation — et pourquoi ce n'est pas un `G.n`

> **Le lot est désigné `W4-S`.**

**La série `G.n` MUST NOT être prolongée, et le motif est précis.** `debug`
**§G.4** est intitulé *« Ce qui touche à l'écrivain réel — hors périmètre,
absolument »*. Nommer `G.4` une campagne d'écriture réelle donnerait à un acte
le nom exact de la classe qui l'interdit. **La collision serait pire que
lexicale.**

`W4-S` est **vérifiée libre** : les désignations `W4` en usage sont `W4-A`…`W4-F`,
`W4-F0`…`W4-F6`, `W4-F1A`, `W4-E1`, `W4-E2`, `W4-P`, `W4-P1`, `W4-P2`, `W4-Q`,
`W4-R`. **Aucun `W4-S` n'existait.**

**Ce que la désignation ne fait pas** : elle n'insère `W4-S` ni dans `W4-F`, ni
dans la série `G.n` ; elle ne lui donne aucune position contractuelle héritée ;
**elle ne rouvre pas `G.3`**.

---

## 2. Objet, et ce que le lot ne prétend pas

> **Objet unique : répéter une écriture réelle sur `heating_curve_shift`, dans
> la forme exacte de `G.2`, dispositif historique neutralisé.**

### 2.1 Ce que `W4-S` établira, et rien de plus

**La RÉPÉTABILITÉ de l'acte, et les deux correctifs d'outillage que `G.2` a
révélés** — la capture en écriture unique, et le puits de preuve réarmé.

> **Il n'établira pas** que la coexistence est qualifiée, ni que `C1` est
> satisfaite ou calculable, ni que Boilerack peut écrire **en coexistence**, ni
> de façon soutenue, ni que `H2`, `H6` **(b)** ou `U-3` seraient closes.
>
> **La borne est celle de `G2-P` §16, reprise sans élargissement.**

> **Ce lot n'apporte presque rien de neuf, et il faut le dire d'emblée.**
> `G2-C` §2 consigne que **Boilerack a déjà émis deux écritures réelles**, le
> `2026-08-28`. Une seconde campagne identique n'ajoute **ni capacité de
> production, ni qualification de la coexistence**. Ce qu'elle ajoute est la
> **répétabilité** — qu'une écriture réussie n'était pas un coup unique — et
> l'**assainissement de l'instrumentation**. **C'est peu, c'est assumé, et le
> présent § existe pour que l'humain arbitre en le sachant.**

### 2.2 Ce que `W4-S` ne rouvre pas

| | État |
|---|---|
| **`G.3`** | **FERMÉ** par sa branche **(b)** — `G3` §6.1, `STOP AVANT AUTORISATION`. **`W4-S` ne s'en réclame d'aucune façon**, ne reprend aucune de ses six corrections, et **ne le rouvre pas** |
| **`P-A5`** | **PRONONCÉE en branche (b)** — `INSTANCE NON ATTRIBUABLE`. **Elle n'est pas transposée** — §7 — et **elle n'est pas rouverte** |
| **`W4-R`** | **exécuté, homologué, clos.** **Aucun rejeu** |
| **`C1`, la coexistence, `W4-P`, `W4-Q`** | **non touchés** — le raisonnement de `G2-P` §4.2 est inchangé : `PR-1` neutralise le superviseur, `PR-2` arrête le pont, `EI-8` exige une fenêtre sans aucune ouverture de connexion |

---

## 3. Ce qui se reprend, et ce qui ne se reprend pas

> **La FORME se reprend. L'AUTORISATION ne se reprend jamais.**

`G2-C` §7 est **opposable et sans exception** :

> *« aucune écriture ultérieure ne peut s'en réclamer — ni sur le même rôle, ni
> sur un autre, ni « dans les mêmes conditions ». Une nouvelle écriture exige
> une **nouvelle autorisation normative**, appuyée sur un document qui la
> définit, puis une **décision humaine explicite et distincte** »*

**Le présent document est ce document.** Il ne dispense d'aucune décision.

| | Se reprend | Ne se reprend pas |
|---|---|---|
| `G2-P` | **le protocole entier, sans allègement** — §8 à §12 | son **autorisation**, consommée |
| `SPT` | le **puits déjà implémenté** | son **usage**, borné à `G.2` *« et aucune autre »* — §6.3 |
| `G.2` | ses **procédures éprouvées** `P-3`, `P-4` | sa **dérogation**, éteinte |
| `G3` | **rien** | **tout** |

---

## 4. Clause `W4-S` — amendement du séquencement de `w4f` §11.1

`w4f` §11.1 réserve quatre actes à une autorisation *« explicite, distincte,
**postérieure à l'audit de W4-F3**, et portant sur cette campagne-là »*.

> **Le verrou est de SÉQUENCEMENT, non de sûreté** — `G2-P` §2.2. Il exige que
> l'autorisation vienne **après** un document qui définit la campagne. **Il
> n'exige pas que ce document soit `W4-F3`.**

> **Clause `W4-S` — amendement nominal, borné, et à extinction.**
>
> Pour la seule campagne définie par le présent document, la mention
> *« postérieure à l'audit de `W4-F3` »* du `w4f` §11.1 est lue
> **« postérieure à l'audit et à l'intégration de `W4-S` »**.
>
> **Rien d'autre du `w4f` §11.1 n'est amendé** : les quatre actes réservés
> demeurent réservés, l'autorisation demeure **explicite, distincte et portant
> sur cette campagne-là**, et **elle MUST NOT être déduite**.
>
> **L'amendement s'ÉTEINT** à l'achèvement de `W4-S`, quel qu'en soit le
> résultat, **`ABORT` compris**. **Aucune campagne postérieure ne s'en autorise**,
> ni de `W4-S`, ni du fait que l'amendement ait servi.
>
> **`W4-F3`, `W4-F4` et `W4-F5` ne sont ni ouverts, ni préparés, ni rapprochés.**

---

## 5. Le rôle unique, et la valeur

**`heating_curve_shift` / `setNiveauM1`, et rien d'autre** — `G2-P` §6.

| | |
|---|---|
| **un seul rôle inscriptible** | `core/production_profile.py` ne déclare qu'un `CommandSpec` avec `write` non nul. **Un second rôle serait visible en revue** |
| **aucune commande ECS** | `setTempWWsoll` **absent du profil**. Une commande ECS supposerait une modification du profil, donc un lot distinct |
| **une seule valeur cible** | **`V_canon + 1`**, **si et seulement si `V_canon + 1 ≤ 40`** — bornes `[−13 ; 40]`, `G2-P` §15 |
| **égalité stricte à la relecture** | `confirm_tolerance = 0.0`, appliqué par le cœur |
| **cardinalité** | **une** écriture au temps 10, **au plus une** au temps 12, **zéro** partout ailleurs |

**Forme de l'invocation**, telle que `adapters/vclient_write.py` la construit —
`G2-P` §9.1 :

```
<executable> -J [-h <hôte>] [-p <port>] -c "setNiveauM1 <entier>"
```

> **Cas d'inexécution.** Si `V_canon + 1 > 40`, **l'écriture n'a pas lieu** et la
> campagne se clôt sans écriture — `G2-P` §15. **Aucune valeur de repli n'est
> improvisée.**

---

## 6. Les trois risques matériels — et eux seuls

> **`W4-S` ne porte que ces trois-là.** Tout ce que `G.3` avait accumulé
> au-delà est **abandonné avec lui**.

### 6.1 `R-1` — redémarrage machine en fenêtre, d'origine non établie

**Le fait, tel qu'il est.** `G2-C` §6, réserve `A-5` : un redémarrage machine
est survenu pendant le préflight de `G.2`, **cause non établie**. `W4-R` a
prononcé **`INSTANCE NON ATTRIBUABLE`**, et **n'a pas même pu établir le
caractère commandé** du redémarrage.

**Ce que le protocole fait déjà de ce risque, et qui n'est pas allégé :** un
redémarrage machine en fenêtre déclenche **`AB-5`** *(niveau capture)* et
**`FA-8`** *(niveau campagne)*. **La campagne s'arrête.** Le présent § ne
traite donc pas de la poursuite — elle est exclue —, mais de **l'état laissé
derrière**.

> **La question utile n'est pas « qu'est-ce qui a causé le redémarrage du
> préflight ». Elle est « dans quel état un redémarrage laisserait
> l'installation ».** La première est indécidable — `W4-R` l'a établi sur
> pièces. **La seconde se constate en un relevé.**

> **Clause — `P-UFS`, précondition BLOQUANTE.**
>
> **Avant le temps 1**, l'**état d'activation au démarrage** — `UnitFileState`
> — **MUST** être relevé et consigné pour les **trois unités historiques** :
> **`<unité-pont>`**, **`<unité-démon>`**, **`<timer-guard>`**.
>
> **La précondition est satisfaite si et seulement si les TROIS sont
> `enabled`.** À défaut, **la campagne MUST NOT être engagée**.
>
> **`<unité-superviseur>` est relevée aussi, et son état ne conditionne rien** :
> elle est déclenchée par `<timer-guard>`, et n'a pas à être activée au
> démarrage. **Exiger d'elle `enabled` serait exiger une propriété que son mode
> de déclenchement ne comporte pas.**

> **Ce que `P-UFS` établit**, et c'est tout ce qu'elle prétend : **un
> redémarrage machine en fenêtre RAMÈNE le dispositif historique en service par
> lui-même** — démon, pont et timer reviennent —, tandis que **`G-a` maintient
> `<unité-boilerack>` hors service**. **L'état d'arrivée est nominal, non
> dangereux.**
>
> **Ce qu'elle n'établit pas** : que le redémarrage n'aura pas lieu · qu'il
> serait sans conséquence sur la valeur · qu'il constituerait un rollback.
> **`w4f` §7.2.1 l'interdit expressément**, et `G2-P` §11.3 le rappelle :
> *« un redémarrage machine MUST NOT être considéré comme un mécanisme de
> rollback de souveraineté »*. **`EI-3` reste un recours, jamais une étape.**

**Conséquence matérielle résiduelle, énoncée sans atténuation :** si un
redémarrage survient entre le temps 10 et le temps 12, **la valeur demeure à
`V_canon + 1`** jusqu'à restauration manuelle. C'est un décalage de **un pas**
de courbe de chauffe, **dans les bornes du constructeur**, sur une installation
**hors saison de chauffe** (`EI-1`), avec **l'exploitant physiquement présent**
(`EI-2`) et **le plan de reprise connu** (`EI-3`).

> **Ce n'est pas une conjecture.** `G2-C` §6 consigne que, lors du redémarrage
> réel du préflight, **`G-a` et `G-b` ont tenu à travers lui**.
>
> **Et ce constat MUST NOT être requalifié** — la garde de `G3` §6.1 est
> reprise ici, car elle est juste : *« L'absence de dommage n'est pas la
> démonstration d'une absence de risque. »* Il établit que **les gardes ont
> tenu une fois**, non qu'un prochain redémarrage serait inoffensif.

### 6.2 `R-2` — le *one-writer* n'est prouvé qu'au sens borné

**`H2` et `H6` (b) demeurent OUVERTES** — `G2-C` §2.1 : la preuve *one-writer*
est bornée aux **clients du démon** ; **un participant agissant sur l'IPC
System V y échapperait**.

> **Clause — `EI-8` est conservée intégralement**, dans la forme du `G2-P` §8.1 :
> **inventaire des unités inscriptibles, toutes inactives** · **aucune session
> `W4-S` ouverte** · **fenêtre muette de 12 s sans aucune ouverture au journal
> du démon**.
>
> **Aucun allègement, aucune substitution.** Le seul recours au-delà des douze
> secondes demeure **`FA-3`** — *« toute valeur qui bouge sans commande
> émise »* —, et **`AB-8`**, la garde de fraîcheur du temps 9.
>
> **`U-3` n'est pas réduite** par le présent lot, et **aucune instrumentation
> nouvelle n'est créée** pour tenter de la réduire.

### 6.3 `R-3` — le puits de preuve est épuisé en droit, désarmé en fait

| | Fait | Source |
|---|---|---|
| **en droit** | l'autorisation d'usage est **ÉPUISÉE** — elle visait `G.2`, *« et aucune autre »* | `SPT` §5.4 |
| **en fait** | l'instrumentation est **DÉSARMÉE** — la variable d'atelier a été retirée du fichier d'environnement persisté | `G2-C` §7 |

> **Clause — extension NOMINALE, bornée à `W4-S`, et à elle seule.**
>
> La désignation *« au sens de `G.2` »* de la **condition 2 de `W4-A` §17**, et
> la désignation *« et aucune autre »* du **`SPT` §5.4**, sont **étendues à la
> campagne `W4-S`** — **et à aucune autre campagne**. **Les deux sont visées
> nommément** : étendre l'une sans l'autre ne produirait rien.
>
> La **durée de `W4-S`** se définit exactement comme le `SPT` §5.4 définit celle
> de `G.2` : *« avant »* = **avant le temps 1** · *« pendant »* = **entre les
> temps 8 et 13** · *« après »* = **une fois l'étape 5 achevée**.
>
> **Ce que l'extension ne fait pas** : elle **ne rend pas `G.2` réutilisable**,
> dont la dérogation demeure éteinte · elle **ne rouvre pas l'étape 4 du
> `SPT` §8** · elle **n'allège aucune des six conditions du `SPT` §4.1** · elle
> **ne crée aucune autorisation permanente** et **s'éteint** à l'achèvement de
> `W4-S`, `ABORT` compris.
>
> **Subordination.** L'extension **ne s'applique PAS par l'intégration du
> présent document**. Elle **MUST** être **portée nommément par l'autorisation
> humaine** — §15, item 6. **Tant qu'elle ne l'est pas, l'extension n'existe
> pas**, et les clauses ci-dessus gardent leur plein effet.
>
> **Aucune modification de code n'est demandée.** L'opt-in est une **variable
> d'environnement persistée** : réarmer, c'est **reposer cette variable**.

> **Clause — le réarmement est un ACTE de la campagne, au temps 8, avant
> l'acte 2.** L'opt-in est lu au démarrage du processus : reposer la variable
> **après** le démarrage manuel ne réarmerait rien.
>
> **`P-SPT` prépare, elle n'accomplit pas** : procédure écrite, et **capture
> *« avant »* prise avant le temps 1, montrant la variable ABSENTE**.
> **La variable MUST NOT être reposée au titre de la précondition.**

> **Clause — dépôt en écriture unique, opposable** *(reprise de `G3` §6.2, qui
> corrigeait `A-1` ; la correction est de procédure et n'appelle aucun code)* :
>
> 1. **tout nom de fichier de capture est UNIQUE dans l'atelier**, et **MUST
>    NOT** être réutilisé, quelle que soit l'issue de ce qu'il capture ;
> 2. **le dépôt est en écriture unique** : rencontrer un nom existant est une
>    **erreur**, jamais un écrasement. **La procédure MUST échouer plutôt que
>    remplacer** ;
> 3. **les captures d'`ACK` sont numérotées par un compteur monotone** propre à
>    la campagne, commençant à `01`, **incrémenté à chaque `ACK` reçu** ;
> 4. **un `ACK` REJETÉ est une capture comme une autre** — déposé, numéroté,
>    conservé ;
> 5. **une capture qui n'a pas pu être prise est DÉCLARÉE MANQUANTE**, et
>    **MUST NOT** être recréée après coup.
>
> **Opposable sur l'atelier lui-même** : deux captures ne peuvent pas porter le
> même nom, et **un trou dans la numérotation est une capture manquante**.

---

## 7. Pourquoi `P-A5` n'est PAS transposée

> **Ce n'est pas un allègement. C'est le constat que la précondition ne
> protégeait pas ce qu'on croyait.**

**Ce que `G3` §6.1 en disait, mot pour mot :**

> *« Ce que la branche (a) apporte, et rien de plus. Elle borne le risque au
> chemin de `F-12`, **dont `PR-1` neutralise l'origine** […] **Le risque
> résiduel se déplace alors hors fenêtre** — préflight et après-restauration.
> **Il ne disparaît pas** »*

**Trois faits, et ils suffisent :**

| | Fait | Source |
|---|---|---|
| **1** | **`PR-1` ne neutralise pas un chemin : il neutralise le superviseur.** Son critère exige *« aucun processus du superviseur vivant »*, timer `inactive`/`dead` **prochain tir vide**, unité d'exécution `inactive`/`dead` **sortie constatée** | `W4-C` §16.1, rappelé au `G2-P` §2.4 |
| **2** | **`<script-superviseur>` porte DEUX chemins terminaux menant au redémarrage machine**, non un seul. Constat **positif**, établi en lecture stricte et homologué | `W4-R`, acte `L6` |
| **3** | **`PR-1` les tue tous les deux**, puisqu'il tue l'unité qui les porte. **L'attribution de l'instance n'y change rien** |  |

> **Conclusion opposable.** La branche **(a)** aurait borné le risque à un
> mécanisme que `PR-1` neutralise **déjà**, et **au-delà**. **Elle n'apportait
> aucune protection supplémentaire en fenêtre**, et son absence n'en retire
> aucune.

**Ce que la non-transposition laisse ouvert, et qui est traité ailleurs :** le
risque d'un redémarrage **d'origine autre que le superviseur** — que `P-A5`
n'adressait pas davantage, `W4-R` n'ayant pas même pu établir le caractère
commandé. **Il est porté par `R-1`**, et couvert par **`P-UFS`**, **`AB-5`**,
**`FA-8`**, **`G-a`**, **`G-b`**, **`EI-2`** et **`EI-3`**.

> **`W4-S` ne rouvre pas `P-A5`, ne la conteste pas, et ne s'en réclame pas.**
> Elle demeure **prononcée en branche (b)**, et `G.3` demeure **fermé**.

**Empreintes des artefacts `W4-R`, conservés hors dépôt** — sur le modèle de
`G2-C` §4 :

| Pièce | SHA-256 |
|---|---|
| `RAPPORT-W4R-V11-EXEC3.md` | `6081f28ffa30e1fb143f7eb04090caa8e99a6750f5477c7153199b74ccb0a271` |
| `w4r-v11-exec3-homologation-20260903.tar.gz` *(20 pièces)* | `1485565990fd3e7926edee80d943d2b2640461dc0a2600499cbfaa4e8765aabb` |

---

## 8. État initial sûr — les treize preuves `EI-1..EI-13`

**Reprises du `G2-P` §7, sans allègement et sans renumérotation.**

| Réf | Preuve exigée | Source |
|---|---|---|
| **`EI-1`** | **circuit au repos, hors saison de chauffe** — **brûleur à `0,0 %`**, M1 au repos ; relevé **avant** l'acte | `W4-C` §9 (1), `C5` §12.1, `W4-C` §16.1 |
| **`EI-2`** | **exploitant physiquement devant la machine**, du début à la fin. *« “Joignable à distance” ne satisfait pas cette condition, et une session distante encore moins »* | `W4-C` §9 (2) |
| **`EI-3`** | **plan de reprise physique connu et accepté** — la campagne neutralise le superviseur, *« donc aussi la remise en état automatique dont il est porteur »* | `W4-C` §9 (3) |
| **`EI-4`** | **atelier** créé, vide, sur stockage persistant, **hors de tout dépôt versionné** | `W4-C` §9 (4), §16.1 |
| **`EI-5`** | **`PR-1`** — superviseur neutralisé : timer `inactive`/`dead` **prochain tir vide** · unité d'exécution `inactive`/`dead`, **sortie constatée** · **aucun processus du superviseur vivant** | `W4-C` §9 (5), §8.1, §16.1 |
| **`EI-6`** | **`PR-2`** — pont arrêté : unité `inactive`/`dead`, `Result=success`, **aucun redémarrage automatique** · **zéro nouvelle connexion au démon en 25 s** | `W4-C` §9 (6), §9.1, §16.1 |
| **`EI-7`** | **démon actif et jamais touché** — `active`/`running`, confirmé par une **lecture nue de code retour `0`** | `W4-C` §9 (7), §16.1 |
| **`EI-8`** | **preuve *one-writer*** — inventaire des unités inscriptibles toutes inactives · aucune session `W4-S` ouverte · **fenêtre muette de 12 s** | `W4-C` §16.1 ; forme et limites au **§6.2** |
| **`EI-9`** | **retour arrière armé avant toute écriture** — valeur relevée, forme canonique dérivée, commande **écrite d'avance** | `W4-C` §9 (8), §12 ; `w4f` §7.3 |
| **`EI-10`** | **concordance des deux formes d'une même lecture** — **texte** *et* **`-J`**, par **`vclient` nu, hors du chemin Boilerack** ; concordance **brute** *et* **sémantique** ; `V_canon` dérivable **sans perte** | `W4-C` §11.3, §12.3.1 ; `AB-2`, `AB-9` |
| **`EI-11`** | **autorité constatée sur le fichier PERSISTÉ** après `enabled = true` — **jamais** sur l'état courant du processus | `w4f` §7.2.1, encadré `G-b` |
| **`EI-12`** | **surface transactionnelle réellement composée et souscrite**, **après le démarrage manuel** — établie par une **trace côté broker**, jamais par l'état interne de Boilerack | `W1` `A15`/`A16` ; `W4-E2` |
| **`EI-13`** | **observabilité relevée sur les trois plans** — invocations Boilerack, **journal du démon**, **trace broker** | `FA-9` ; `w4f` §10.3.1 précondition 6 |

> **`EI-10` ne peut pas passer par Boilerack, et c'est le code qui le dit.**
> `VClientCliReader` construit `[…, "-J", "-c", command]` : **la forme texte
> n'existe pas dans le chemin de lecture de Boilerack.** `EI-10` est donc
> établie par **deux captures `vclient` nues**. **Ce sont des lectures** : elles
> ne modifient pas la cardinalité du §9.

> **`EI-12` n'est pas une formalité.** `W1` `A15` : *« W0 garantit la
> **réémission** d'un SUBSCRIBE, **jamais son acceptation** par le broker »* ;
> `A16` : *« `online` **ne signifie pas** “souscriptions restaurées”. »*
> **La preuve est côté broker, ou elle n'existe pas.**

> **Aucune preuve `EI` n'est facultative.** L'échec de l'une quelconque relève
> du §12 et **interdit d'engager l'écriture**.

---

## 9. Protocole — la campagne, dans cet ordre

**Repris du `G2-P` §9, sans allègement.**

| Temps | Acte | Preuve |
|---|---|---|
| **1** | établir **`EI-1` à `EI-4`** — repos, présence, plan de reprise, atelier | §8 |
| **2** | établir **`PR-1`** (`EI-5`), de préférence juste après un cycle nominal | §8 |
| **3** | établir **`PR-2`** (`EI-6`) | §8 |
| **4** | établir **`EI-7`** — démon actif, **lecture nue code retour `0`** | §8 |
| **5** | **`<unité-boilerack>` arrêtée**, puis établir **`EI-8`** — inventaire, aucune session, **fenêtre muette de 12 s** | §6.2 |
| **6** | **lire** `getNiveauM1` par **deux captures `vclient` nues** — **texte** puis **`-J`** — constituer `V_brut`, dériver `V_canon`, établir **`EI-10`** | §8 |
| **7** | **armer** la restauration — `EI-9` : commande écrite d'avance, **non exécutée** | §10 |
| **8** | **réarmer le puits** *(acte 1 bis)*, **persister `enabled = true`** et établir **`EI-11`**, **démarrer `<unité-boilerack>` à la main**, établir **`EI-12`** puis **`EI-13`** | encadré ci-dessous |
| **9** | **relire** — **garde de fraîcheur**, en **`-J` seul** : concordance avec `V_brut` exigée, sinon **`AB-8`** | `W4-C` §11.1, §12.3.2 |
| **10** | **écrire** `V_canon + 1`, **si et seulement si `V_canon + 1 ≤ 40`** — **une seule écriture** | §5 |
| **11** | **relire** — **égalité stricte** exigée avec `V_canon + 1`, sinon **`AB-1` transposé** | §12 |
| **12** | **conduite de restauration de la valeur** selon le §10 | §10 |
| **13** | **éteindre toute capacité d'écriture** selon le §11.1 | §11.1 |
| **14** | **restaurer le dispositif historique** — **les cinq étapes** | §11.2 |

**Au plus deux écritures. Aucune autre commande, aucun autre rôle, aucune
répétition, aucune rafale.** Les lectures des temps 4, 6, 9, 11 et de l'étape 1
du §11.2 **n'entrent pas dans ce décompte**.

> **Clause — le temps 8, et ses QUATRE actes dans cet ordre.**
>
> L'autorité comme l'opt-in du puits sont **lus au démarrage du processus**
> (`W4-E2`) : persister quoi que ce soit **n'ouvre rien** sur un processus déjà
> lancé. D'où :
>
> 1. **réarmer le puits** — reposer la variable persistée *(acte 1 bis, §6.3)* ;
> 2. **persister `enabled = true`**, et le **prouver sur le contenu du fichier
>    déployé** — `EI-11` ;
> 3. **démarrer `<unité-boilerack>` à la main**, puisqu'elle est arrêtée depuis
>    le temps 5 et **non activée au démarrage** (`G-a`) ;
> 4. **prouver la surface réellement composée et souscrite** par une **trace
>    côté broker** — `EI-12`.
>
> **`G-a` est préservée : démarrer n'est pas activer au démarrage.**

---

## 10. Restauration de la valeur — `w4f` §7.3

| Cas au temps 11 | Conduite | Fondement |
|---|---|---|
| l'écriture **n'a pas eu lieu** | **aucune écriture.** Restaurer serait écrire sans avoir caractérisé | `w4f` §7.3 cas 1 |
| relecture **concordante** — `applied` | restauration **admise**, et **seulement** si l'autorisation humaine l'a **explicitement pré-décidée**. À défaut : aucune écriture | `w4f` §7.3 cas 2 — *« décision humaine, pas automatisme »* |
| **fenêtre épuisée** — `timeout` nominal | **aucune écriture supplémentaire.** État *indéterminé* : l'établir par observation | `w4f` §7.3 cas 3 |
| relecture **discordante**, état changeant, ou critère `FA`/`AB` déclenché | **`ABORT`. Aucune écriture supplémentaire.** | `w4f` §7.3 cas 4 |

> **Aucune restauration de la valeur après `ABORT`** — clause reprise du
> `G2-P` §10.

---

## 11. Extinction, restauration, gardes

### 11.1 Fermeture réelle de l'autorité — trois actes, dans cet ordre

**`W1` `A17`** : *« Une souscription logique est **irrétractable** : aucun
`unsubscribe` n'existe, et un `disconnect()` ne vide pas le registre. »*

> 1. **persister `[transaction_surface].enabled = false`**, et le **prouver sur
>    le contenu persisté** — jamais sur l'état courant du processus ;
> 2. **arrêter effectivement `<unité-boilerack>`**, et **constater l'arrêt** ;
> 3. **attendre et constater la libération effective de la liaison**.
>
> **Achevés et prouvés AVANT le temps 14.** Remettre le pont pendant qu'un
> Boilerack écrivain vit encore **recréerait exactement les deux écrivains** que
> `PR-1`, `PR-2` et `EI-8` avaient éliminés.

### 11.2 Restauration de l'état normal — les cinq étapes de `W4-C` §13

*« dans cet ordre, et vérifié à chaque étape »* — *« **La campagne n'est close
qu'après l'étape 5.** »*

| Étape | Acte | Preuve exigée |
|---|---|---|
| **1** | **confirmer par une lecture nue** la valeur en place, et la comparer à **`V_attendue`** | lecture consignée — §11.2.1 |
| **2** | **redémarrer `<unité-pont>`** | commande consignée |
| **3** | **constater sa reprise, en amont ET en aval** — les **trois faits distincts** | **A**, **B**, **C** |
| **4** | **redémarrer `<timer-guard>`** | commande consignée |
| **5** | **confirmer un cycle nominal du superviseur sans action corrective**, et l'alternance normale de son unité d'exécution | cycle observé de bout en bout |

**Les trois faits distincts de l'étape 3** — `W4-C` §13.1 :

| | Fait | Constaté par |
|---|---|---|
| **A** | le pont est **actif** | l'unité redevenue active |
| **B** | le pont **sonde** le démon | **cadence de connexions repartie dans le journal du démon** |
| **C** | le pont **publie** | **télémétrie effectivement observée depuis un consommateur aval** |

> *« Aucun des trois ne remplace les autres. A sans B décrirait un processus qui
> tourne sans travailler. **B sans C est précisément le piège** »* — et
> `W4-C` §13 qualifie l'issue correspondante de **pire possible**.
>
> **L'étape 3 interdit une source, nommément** : *« La sortie standard du pont
> **MUST NOT** servir ici : elle est mise en tampon »*.
>
> **L'étape 5 a une durée** : le superviseur sonde périodiquement ; observer un
> cycle nominal suppose d'attendre **au moins un cycle complet**. **La campagne
> reste ouverte jusque-là.**
>
> **`PR-1` et `PR-2` sont redoublées** : le rapport porte **comment l'arrêt a
> été établi, ET comment la reprise l'a été**.
>
> L'impossibilité de prouver **l'une quelconque** des cinq étapes — `A`, `B`,
> `C` comprises — est **`FA-11`**.

#### 11.2.1 `V_attendue` — le terme de référence, et lui seul

| Ce qui a été exécuté | `V_attendue` |
|---|---|
| l'écriture du temps 10 **n'a pas eu lieu** | **`V_brut`** — `V_canon + 1` **n'est pas attendue** |
| écriture exécutée, **restauration non exécutée** | **`V_canon + 1`** |
| écriture **et** restauration exécutées | **`V_brut`** |

> **Une valeur qui ne concorde avec aucune des deux références est une valeur
> qui a bougé sans commande émise : `FA-3`.**

### 11.3 Gardes anti-reboot — `G-a` et `G-b`, cumulées

> - **`G-a`** : `<unité-boilerack>` **MUST NOT** être activée au démarrage
>   pendant toute la fenêtre, état **prouvé avant le temps 8** puis
>   **reconstaté après le démarrage manuel**. **Démarrer n'est pas activer.**
> - **`G-b`** : **hors les temps 8 à 13**, la configuration **persistée** MUST
>   porter `enabled = false`, **prouvé sur le contenu du fichier**.
>
> **Le cumul est délibéré** : `G-a` protège pendant que l'autorité est ouverte,
> `G-b` dès qu'elle est refermée. **Aucune ne suffit seule sur toute la
> fenêtre.**
>
> **`EI-3` reste un recours, jamais une étape** : le redémarrage machine
> **MUST NOT** être employé comme rollback tant que `G-a` et `G-b` ne sont pas
> l'une et l'autre prouvées.

---

## 12. `ABORT` — référentiel intégral, sans retrait

**`W4-S` adopte `FA-1..FA-12` et `AB-1..AB-9`, intégralement.**

**`FA` — niveau campagne**

| Réf | Déclencheur | Portée |
|---|---|---|
| **`FA-1`** | impossibilité de prouver `PR-1` | `EI-5` |
| **`FA-2`** | impossibilité de prouver `PR-2` | `EI-6` |
| **`FA-3`** | **second écrivain — toute valeur qui bouge sans commande émise** | **seul recours face à `H2`/`H6` (b)** au-delà des 12 s ; et §11.2.1 |
| **`FA-4`** | démon injoignable ou changeant d'état | `EI-7` |
| **`FA-5`** | réponse de transport anormale ou non caractérisée | temps 10 |
| **`FA-6`** | relecture absente | temps 11 |
| **`FA-7`** | relecture discordante après écriture | temps 11 |
| **`FA-8`** | **redémarrage inattendu d'un service ou de la machine** | **toute la fenêtre — `R-1`, §6.1** |
| **`FA-9`** | perte de la connectivité utile à l'observation | `EI-13` |
| **`FA-10`** | **`ACK` incohérent avec l'observation directe** | l'`ACK` **MUST** être confronté à la relecture |
| **`FA-11`** | impossibilité de prouver le rollback | §11.2, **l'une quelconque des cinq étapes** |
| **`FA-12`** | doute de l'exploitant, sans justification à fournir | toute la fenêtre |

**`AB` — niveau capture**

| Réf | Déclencheur | Portée |
|---|---|---|
| **`AB-1`** | une relecture ne concorde pas avec la valeur attendue | **transposé — §11.2.1** |
| **`AB-2`** | la concordance des **deux formes** échoue, avant l'écriture | `EI-10`, temps 6 |
| **`AB-3`** | le démon change d'état ou devient injoignable | `EI-7` |
| **`AB-4`** | une invocation dépasse nettement le budget de 5 s | conservé |
| **`AB-5`** | **un service redémarre, ou la machine redémarre, pour quelque cause** | **toute la fenêtre — `R-1`, §6.1** |
| **`AB-6`** | tout doute de l'exploitant | toute la fenêtre |
| **`AB-7`** | durée mesurée négative, nulle ou absurde | l'horloge a bougé |
| **`AB-8`** | la **garde de fraîcheur** échoue avant l'écriture | temps 9 — **détection d'un second écrivain** |
| **`AB-9`** | `V_canon` non dérivable de `V_brut` **sans perte** | `EI-10` |

> **Interdiction reprise telle quelle** : *« Ne **jamais** provoquer
> délibérément un dépassement de budget ni un démon injoignable »* pour
> capturer une signature.

---

## 13. Préconditions

| # | Précondition | État |
|---|---|---|
| **`P-1`** | Boilerack **déployé** et fonctionnel en lecture, unité **arrêtée** jusqu'au temps 8 | **à constater**, non à accomplir |
| **`P-2`** | pont, démon et superviseur dans leur **état nominal avant l'acte** | à établir le jour |
| **`P-3`** | **rollback disponible** — arrêter et retirer `<unité-boilerack>` sans dépendre de Boilerack | éprouvé sous `G.2` ; **à reconstater** |
| **`P-4`** | **procédure de remise en marche** écrite et **éprouvée avant le temps 2**, couvrant les **cinq étapes** | éprouvée sous `G.2` ; **à reconstater** |
| **`P-5`** | **inventaire des unités inscriptibles** dressé et vérifié | à dresser le jour |
| **`P-6`** | **trace côté broker** disponible et lisible | à établir le jour |
| **`P-7`** | **consommateur aval** disponible pour observer la télémétrie | à établir le jour |
| **`P-8`** | exploitant **physiquement présent**, plan de reprise physique connu | déclaration |
| **`P-UFS`** | **`UnitFileState` des TROIS unités historiques relevé, et les trois `enabled`** | **à établir avant le temps 1** — §6.1 |
| **`P-A1`** | **dépôt de captures en écriture unique** en place, **compteur d'`ACK` armé** | à mettre en place — §6.3 |
| **`P-SPT`** | **réarmement PRÉPARÉ, non accompli** : procédure écrite, capture *« avant »* **montrant la variable ABSENTE**, prise **avant le temps 1** | à faire — §6.3 |
| **`P-9`** | **autorisation humaine explicite et distincte** — §15 | **NON DONNÉE** |
| **`P-10`** | le présent document **audité et intégré** | **non acquise** |
| **`P-11`** | les treize preuves `EI` établies, **dans l'ordre** | à établir le jour |

> **Aucune précondition n'est facultative.** L'échec de l'une quelconque
> **interdit d'engager la campagne**. **Rien de non bloquant ne figure dans ce
> tableau.**

> **`P-A5` n'y figure pas, et c'est délibéré** — §7. Elle est **prononcée en
> branche (b)**, et **n'est ni transposée, ni rouverte**.

---

## 14. Ce que `W4-S` lève, et ce qu'il ne lève pas

**Ce qu'il lèverait, une fois — liste close :**

| # | Objet levé | Fondement |
|---|---|---|
| **1** | une **écriture réelle**, sur un **rôle unique** et une **valeur unique** | acte réservé **1** — §4 |
| **2** | l'**ouverture temporaire** de `[transaction_surface].enabled`, effective au temps 8, éteinte au temps 13 | acte réservé **2** — §4 |
| **3** | la **neutralisation temporaire** du dispositif historique, bornée à `PR-1`, `PR-2`, `EI-8`, suivie de la restauration en **cinq étapes** | acte réservé **3** — §4 |
| **4** | **au plus une seconde écriture** — la restauration de la valeur —, dans le **seul cas nominal** et sur décision humaine **pré-décidée** | §10 |
| **5** | **quatre gestes sur `<unité-boilerack>`** — arrêter (t. 5), **démarrer à la main** (t. 8), arrêter (t. 13), **retirer** au rollback `P-3` | **levée ponctuelle du `w4f` §11.2** |
| **6** | le **réarmement temporaire du puits** pour la durée de `W4-S` | **extension nominale** — §6.3 |

**Ce qu'il ne lève pas :**

| Objet | État |
|---|---|
| **bascule de souveraineté** | **INTERDITE — acte réservé 4 du `w4f` §11.1, strictement.** Sous aucune forme, à aucun temps, et **l'autorisation ne peut pas la porter** |
| écriture sur un **second rôle** | interdite — §5 |
| toute commande **ECS** | interdite — absente du profil |
| **modification** du pont, du superviseur, du démon ou de leurs unités | interdite — **seuls l'arrêt et la remise en marche** sont admis |
| **activation au démarrage** de `<unité-boilerack>` | interdite — `G-a` |
| **instrumentation nouvelle**, en particulier vers `U-3` | **hors périmètre.** Le réarmement n'en est pas une : le puits est **déjà implémenté** |
| exploitation de `<unité-boilerack>` **hors des quatre gestes** | **NON LEVÉE** — le `w4f` §11.2 demeure `NON DONNÉE` en général |
| usage du puits **hors de `W4-S`** | **NON LEVÉ** — l'extension **s'éteint** avec la campagne |
| toute **campagne ultérieure** | **interdite** — §4, extinction ; **aucune ne s'autorise de `W4-S`** |
| **`G.3`**, **`P-A5`** | **non rouverts** — §2.2 |
| `C1`, coexistence, `W4-P`, `W4-Q` | **non touchés** |
| `W4-F3`, `W4-F4`, `W4-F5`, `T0`, `T1`, `T2` | **non ouverts** |
| **autorité permanente d'écriture** | **aucune n'est créée** |

> **Le pont historique demeure l'unique écrivain réel de production**, hors la
> fenêtre de `W4-S`.

---

## 15. L'autorisation humaine

> ### `NON DONNÉE`

**Le présent document ne l'accorde pas, ne la sollicite pas implicitement, et
n'en préjuge pas.**

**Ce qui est demandé, si elle est donnée — liste close :**

| # | Objet |
|---|---|
| **1** | nommer **`W4-S`**, explicitement |
| **2** | être **postérieure à l'audit ET à l'intégration** du présent document |
| **3** | **dire si la restauration de la valeur est PRÉ-DÉCIDÉE** — §10, cas 2 |
| **4** | porter les **actes réservés 1, 2 et 3** du `w4f` §11.1 |
| **5** | porter la **levée ponctuelle du `w4f` §11.2**, bornée aux **quatre gestes** |
| **6** | porter l'**extension nominale du puits de preuve** — §6.3 |
| **7** | valoir pour **une exécution, et une seule** |

**Elle MUST NOT :**

- être **déduite** de l'audit, de l'intégration, ou du merge du présent document ;
- se réclamer de l'autorisation d'un **autre lot** — **`G.1`, `G.2`, `G.3`,
  `W4-P1`, `W4-P2` et `W4-R` sont étrangers à celle-ci** ;
- porter l'**acte réservé 4** — la bascule de souveraineté, **interdite en tout
  état de cause** ;
- valoir autorisation de `W4-F3`, `W4-F4`, `W4-F5`, `T0`, `T1` ou `T2` ;
- valoir **rouverture** de `G.3` ou de `P-A5`.

> **Une campagne engagée sans l'une quelconque des sept lignes ci-dessus est
> hors autorisation**, et **MUST NOT** être exécutée.

---

## 16. Preuves de sortie, et verdict

| # | Sortie |
|---|---|
| **1** | les **préconditions**, une par une, dont **`P-UFS`** avec les **quatre** `UnitFileState` relevés |
| **2** | les **treize preuves `EI`**, dans l'ordre du §9 |
| **3** | **`PR-1` et `PR-2` REDOUBLÉES** — comment l'arrêt a été établi, **et comment la reprise l'a été** |
| **4** | la **ligne d'invocation réelle**, `stdout` et `stderr` **intégralement et séparément**, **code retour** et **durée mesurée** — par le puits réarmé |
| **5** | `V_brut`, `V_canon`, la valeur cible, la valeur finale, et **`V_attendue`** à l'étape 1 |
| **6** | la **cardinalité effective** des écritures, temps par temps |
| **7** | les **cinq étapes** du §11.2, dont les **trois faits `A`, `B`, `C`** et le **cycle nominal** de l'étape 5 |
| **8** | **`G-a`** prouvée avant le temps 8 **et reconstatée après le démarrage manuel** · **`G-b`** hors les temps 8 à 13 |
| **9** | le **compteur d'`ACK`**, **continu**, et toute capture **DÉCLARÉE MANQUANTE** |
| **10** | tout critère **`AB`** ou **`FA`** atteint, **prononcé ou non** |
| **11** | ce qui **demeure non établi** |

**Verdict** — l'un des deux, et il n'y en a pas d'autre :

| | |
|---|---|
| **`W4-S CONFIRMÉ`** | les treize `EI` établies, l'écriture émise, la relecture **strictement égale**, la restauration conduite selon le §10, les **cinq étapes** achevées, **aucun `AB`, aucun `FA`** |
| **`W4-S ABANDONNÉ`** | **tout autre cas.** Un abandon **n'est pas un échec du lot** : c'est le référentiel qui fonctionne |

> **Aucune donnée de site ne figure au dépôt.** Le rapport est **gelé hors
> dépôt** ; le dépôt n'en portera que les **empreintes** — modèle `G2-C` §4.

---

## 17. Ce que ce document ne fait pas

Il **n'exécute rien** · **n'autorise rien** · ne conduit aucun terrain · ne
demande **aucun code** · ne modifie ni service, ni timer, ni pont, ni démon, ni
configuration · **ne rouvre ni `G.3` ni `P-A5`** · ne tranche aucune inconnue ·
**n'ouvre ni `T0`, ni `T1`, ni `T2`** · ne rapproche pas la bascule de
souveraineté · n'amende aucun contrat hors le séquencement nominal du §4 et
l'extension nominale du §6.3, **toutes deux à extinction**.

**Il définit une campagne, la referme, et s'arrête là.**

---

## 18. Réserves conservées

1. **Le lot n'apporte presque rien de neuf** — §2.1. Il établit la
   **répétabilité** et assainit l'instrumentation. **Il n'ouvre aucune capacité
   de production.**
2. **`H2` et `H6` (b) demeurent ouvertes** — la preuve *one-writer* est bornée
   aux **clients du démon**. Un participant sur l'**IPC System V** y
   échapperait, et **`FA-3` est le seul recours**.
3. **`U-3` demeure ouverte** et **n'est pas réduite**.
4. **`C1` demeure non satisfaite et non calculable** — `U-2` n'a **aucune
   valeur admissible**, `W4-P1` et `W4-P2` ayant fermé les deux routes.
   **La coexistence demeure non qualifiée.**
5. **`R-1` n'est pas supprimé, il est borné** — §6.1. Un redémarrage machine
   d'origine non établie **demeure possible**. `P-UFS` établit **l'état
   d'arrivée**, non l'absence d'occurrence.
6. **`P-UFS` se constate, elle ne se présume pas.** Un état d'activation relevé
   **avant** la fenêtre peut avoir changé ; c'est pourquoi le relevé est
   **exigé avant le temps 1**, et non repris d'un relevé antérieur.
7. **`EI-1` suppose l'installation hors saison de chauffe.** La campagne
   **MUST NOT** être engagée si le circuit n'est pas au repos.
8. **La restauration de la valeur n'est pas automatique** : sans pré-décision
   humaine explicite, **aucune seconde écriture n'a lieu**, et la valeur
   demeure à `V_canon + 1`.
9. **`A-2`, `A-3`, `A-4` de `G2-C` §6 ne sont pas corrigées ici** : elles
   relèvent de la méthode, du cosmétique et de l'exactitude, et **aucun
   polissage n'est conduit sous acte**.
10. **Le bornage reste opposable, non auto-appliqué.** Rien dans le code
    n'empêche une écriture hors campagne ; **c'est la discipline qui
    l'empêche**, et le présent document en fait partie.

---

## 19. Précédent invoqué

`G.1` — `w4f2-g1-constat.md` — puis `G.2` — `G2-P`, `G2-C` : **un acte borné,
proposé par un document, non autorisé par lui**, puis autorisé par une décision
humaine séparée, exécuté sans élargissement, et consigné par un document
distinct.

**`W4-S` suit cette forme exactement.** Il en tire aussi la leçon inverse :
`G.3` a suivi la même forme et **s'est fermé sur une précondition
indécidable**. **Le présent lot ne porte que des préconditions constatables.**

---

## 20. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture et bornage. Reprise intégrale de `G2-P` — `PR-1`, `PR-2`, `EI-1..EI-13`, `G-a`, `G-b`, `FA-1..FA-12`, `AB-1..AB-9`, restauration en cinq étapes. **Trois risques matériels seulement** : `R-1` redémarrage d'origine non établie, borné par la précondition **constatable** `P-UFS` · `R-2` *one-writer* borné, `EI-8` conservée · `R-3` puits épuisé, extension nominale et dépôt en écriture unique. **`P-A5` n'est pas transposée** — `PR-1` neutralise le superviseur entier, donc **les deux** chemins de redémarrage que `W4-R` a constatés, et l'attribution n'apportait aucune protection en fenêtre. **Acte réservé 4 strictement interdit.** **`G.3` et `P-A5` ne sont pas rouverts.** **Autorisation `NON DONNÉE`.** |
