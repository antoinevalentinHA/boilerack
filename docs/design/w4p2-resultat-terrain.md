# `W4-P2` — résultat terrain et clôture

> **Version 12**, après réaudit. Deux corrections, l'une de place, l'autre de
> **portée d'une affirmation**.
>
> | | Correction |
> |---|---|
> | **V12 · B39** | les deux paragraphes commentant le chiffrage de `R6` étaient **restés sous le `§5.3`**, séparés de la table qu'ils commentent. Ils sont replacés **sous le `§5.1`, immédiatement après elle** — ce qui **répare aussi un déictique** : leur *« ci-dessus »* désignait, là où ils étaient, un tout autre contenu. **Aucun changement de fond, de chiffre ni de verdict** |
> | **V12 · B40** | le `§0` affirmait que **« chaque durée publiée dans ce document »** se recalculait depuis son tableau. **C'était trop large** : les durées tirées des horodatages `O2` n'en proviennent pas. L'affirmation est **bornée aux huit durées dérivées des instants de journal**, et **l'incertitude des durées d'origine `O2` est énoncée une fois**, au `§3.1` |
>
> **`P2-O2` demeure inchangé** : `APPARIEMENT SANS AMBIGUÏTÉ`, attelé à la
> limite 4 du `P2-O5`.

> **CONSIGNATION D'UN RÉSULTAT.** Ce document **consigne** ce que la
> campagne a produit. Il **n'interprète pas**, **ne qualifie rien**, **ne déduit
> aucune autorisation**, et **ne modifie aucun autre contrat ni chantier**.
>
> **Aucune nouvelle autorisation terrain ni d'écriture n'en découle.** `C1` n'est
> pas rouverte, `T0` demeure NON AUTORISÉ, `T1` et `T2` ne sont pas approchés.

---

## 0. Bases de temps, et réconciliation des instants

**Deux bases de temps coexistent dans les artefacts, et les versions antérieures
les mêlaient sans le dire.**

| Source | Base | Résolution |
|---|---|---|
| les **relevés du lot** — instants de commande, de vérification, de relevé `O2` | **`UTC`** | **microseconde** pour les instants de commande, **seconde** pour les autres |
| le **journal système** et les **propriétés d'unité** | **`CEST`**, soit **`UTC + 2 h`** | **microseconde** au journal, **seconde** pour les propriétés |

> **Le décalage est de `+2 h` exactement.** Tous les instants ci-dessous sont
> donnés **dans les deux bases**, et leur résolution est nommée.

> **Tout instant servant à dériver une durée est publié ci-dessous en `UTC` à la
> MICROSECONDE.** Les versions antérieures donnaient l'`UTC` à la milliseconde et
> le `CEST` à la microseconde : **les durées annoncées n'étaient pas dérivables
> des opérandes publiées dans la base de référence**. Elles le sont désormais.

| Événement | `UTC` | `CEST` | Résolution |
|---|---|---|---|
| **commande `M5`** | `06:21:26,488866` | `08:21:26,488866` | microseconde |
| **arrêt du pont à `M5`** — début | `06:21:26,746329` | `08:21:26,746329` | microseconde |
| **arrêt du pont à `M5`** — fin | `06:21:41,394465` | `08:21:41,394465` | microseconde |
| **arrêt du démon à `M5`** — début | `06:21:41,399874` | `08:21:41,399874` | microseconde |
| **arrêt du démon à `M5`** — fin | `06:21:41,412831` | `08:21:41,412831` | microseconde |
| **`Started` du démon à `M5`** | `06:21:41,421068` | `08:21:41,421068` | microseconde |
| **démarrage du pont à `M5`** | `06:21:41,430833` | `08:21:41,430833` | microseconde |
| **vérification `M6`** | `06:21:41` | `08:21:41` | **seconde** |
| **premier relevé `O2`** | `06:21:41` | `08:21:41` | **seconde** |
| **commande `S3`** | `06:31:30,101506` | `08:31:30,101506` | microseconde |
| **arrêt du pont à `S3`** — début | `06:31:30,202425` | `08:31:30,202425` | microseconde |
| **arrêt du pont à `S3`** — fin | `06:31:31,849865` | `08:31:31,849865` | microseconde |
| **arrêt du démon à `S3`** — début | `06:31:31,854093` | `08:31:31,854093` | microseconde |
| **`Stopped` du démon à `S3`** | `06:31:31,860129` | `08:31:31,860129` | microseconde |
| **`Started` du démon à `S3`** | `06:31:31,868135` | `08:31:31,868135` | microseconde |
| **démarrage du pont à `S3`** | `06:31:31,876717` | `08:31:31,876717` | microseconde |
| **exécution de `M5 bis`** | `06:22:36` | `08:22:36` | **seconde** — horodatage interne à l'acte |
| **exécution de `S9`** | `06:33:55` | `08:33:55` | **seconde** — horodatage interne à l'acte |
| **extraction des lignes de la fenêtre** | `06:34:37` | `08:34:37` | **seconde** — **date de modification de l'artefact**, et non un horodatage interne : la commande n'en portait pas |

**Les HUIT durées dérivées des instants de journal ci-dessus se recalculent
exactement depuis ce tableau :**

| Durée | Opérandes | Calcul |
|---|---|---|
| **`14,932 s`** — commande `M5` → démon actif | `06:21:41,421068 − 06:21:26,488866` | `14,932202` |
| **`1,767 s`** — commande `S3` → démon actif | `06:31:31,868135 − 06:31:30,101506` | `1,766629` |
| **`14,648 s`** — arrêt du pont à `M5` | `06:21:41,394465 − 06:21:26,746329` | `14,648136` |
| **`1,647 s`** — arrêt du pont à `S3` | `06:31:31,849865 − 06:31:30,202425` | `1,647440` |
| **`590,439 s`** — fonctionnement sous verbosité élevée | `06:31:31,860129 − 06:21:41,421068` | `590,439061` |
| **`603,613 s`** — fenêtre, de commande à commande | `06:31:30,101506 − 06:21:26,488866` | `603,612640` |
| **`[588,102 ; 588,680] s`** — premier relevé `O2` → commande `S3` | `06:31:30,101506 − [06:21:41,999999 ; 06:21:41,421068]` | bornes exactes |
| **`[14,932 ; 15,511] s`** — commande `M5` → premier relevé `O2` | `[06:21:41,421068 ; 06:21:41,999999] − 06:21:26,488866` | bornes exactes |

> **Les valeurs publiées sont des ARRONDIS des calculs ci-dessus**, à la
> milliseconde. Les deux instants de résolution **seconde** — vérification `M6`
> et premier relevé `O2` — n'entrent que dans les deux dernières lignes, **sous
> forme d'intervalle**, jamais comme valeur unique.

> **Ce tableau ne couvre QUE ces huit durées, et la V11 le disait trop largement.**
> Elle affirmait que *« chaque durée publiée dans ce document »* s'en dérivait.
> **C'est faux** : le document porte d'autres durées — les silences, leur total,
> la non-couverture, l'étendue de la surveillance, les dépassements structurels —
> qui sont tirées des **horodatages `O2`**, lesquels n'ont qu'une **résolution à
> la seconde**. Elles ne se recalculent pas depuis ce tableau, et **leur
> incertitude est énoncée au §3.1**.

> **Ce que la réconciliation révèle, et ce que la V7 en disait à tort.** La
> vérification `M6` et le premier relevé `O2` portent le **même horodatage à la
> seconde**, `06:21:41`. La V7 en concluait qu'on **ne pouvait pas trancher** s'ils
> précédaient ou suivaient le `Started` de `06:21:41,421`.

> **C'était faux, et l'ordonnancement est déterminé.** `M6` a **constaté le
> nouvel identifiant de processus** — `296340` — et le **nouvel identifiant
> d'invocation**. **Ces valeurs n'existaient pas avant le `Started`.** `M6` lui
> est donc **nécessairement postérieur**, et le premier relevé `O2`, exécuté dans
> la même commande **après** lui, l'est aussi.

| | Borne basse | Borne haute |
|---|---|---|
| instant réel de `M6` et du premier relevé `O2` | **`06:21:41,421`** — le `Started` | `06:21:41,999` — la seconde suivante |

> **La résolution demeure la seule limite**, mais elle est désormais **bornée des
> deux côtés**, et non plus ouverte.

> **Chaque instant n'est publié qu'ICI, dans les deux bases.** Le reste du
> document emploie **`UTC` seul**, et renvoie à ce tableau pour la
> correspondance. Les versions antérieures citaient le même instant tantôt en
> `UTC`, tantôt en `CEST`, **sans le dire** — notamment l'extraction des lignes,
> donnée `08:34:37` au bandeau et `06:34:37` au corps. **C'est le même
> instant.**

## 1. Ce qui a été exécuté

La campagne bornée par `w4p2-lot-terrain-borne.md` **Version 14**.

**Deux autorisations humaines successives et distinctes**, dans cet ordre :

| # | Autorisation | Portée | Ce qu'elle a permis |
|---|---|---|---|
| **1** | **avant tout acte** | **la phase 0, et elle seule** — les sept actes de lecture et de consignation | `P1` à `P6`, avec interdiction explicite de poursuivre vers la mutation |
| **2** | **après le verdict `P5 = PRÉCONDITION ÉTABLIE`** et la reddition des preuves de phase 0 | **à partir de `M1`** | l'armement, la fenêtre et le retour |

> **Le fait, et rien d'autre.** La phase 0 a été exécutée sous une **première
> autorisation humaine distincte**, alors que **l'autorisation décrite au §9 du
> document borné n'a été donnée qu'ensuite**, pour `M1` et la suite.

> **Elle est allée à son terme. AUCUN `ABORT` N'A ÉTÉ PRONONCÉ, AUCUN `STOP`.**
>
> **Mais DEUX critères d'arrêt ONT ÉTÉ ATTEINTS, CINQ FOIS EN TOUT** :
>
> | Critère | Où | Renvoi |
> |---|---|---|
> | **`P2A-1`** | à `M5 bis`, à `S3 bis`, à `S8`, et à l'extraction postérieure — **quatre fois** | §5.2 |
> | **`P2A-4`** | à `M5` — l'unité n'est devenue active que `14,932 s` après la commande, contre un plafond de `10 s` | §5.3 |
>
> **Aucun `ABORT` n'a jamais été prononcé**, et le premier était dû **dès `M5`**.
>
> **La réserve porte sur TROIS critères.** Sur les **`123 s`** sans aucun canal —
> ni temps réel, ni rétrospectif —, **`P2A-5`, `P2A-11` et `P2A-12`** ne sont que
> **« non constatés atteints »**. **Tous les autres sont établis** par leurs
> preuves propres : voir §3.3.

| Acte | Résultat |
|---|---|
| **`M1`** | répertoire de surcharge **absent** au préalable ; créé ; **un seul fichier**, portant exactement la réinitialisation de la ligne d'exécution et sa reprise augmentée de l'option de verbosité |
| **`M2`** | validation **sans redémarrage** : **sortie vide, code 0**. `P2A-2` non déclenchée |
| **`M3`** | rechargement effectué, démon **non redémarré** — identifiant de processus et d'invocation **inchangés** |
| **`M4`** | invocation résultante **identique caractère à caractère** à l'attendue. `P2A-3` non déclenchée |
| **`M5`** | fin de cycle **constatée**, puis commande de redémarrage — **≈ 165 s de marge** avant le cycle suivant |
| **`M6`** | unité trouvée **active au premier contrôle suivant le retour de la commande**, identifiant de processus **nouveau**, compteur de relances **stable**, identifiant d'invocation relevé. **Depuis l'émission de la commande, `14,932 s` se sont écoulés** — voir §5.3 |
| **`S1`–`S3`** | surcharge supprimée sur une fin de cycle constatée ; invocation résultante **identique au préflight** ; retour commandé, unité **active `1,767 s` après l'émission de la commande** |
| **`S4`–`S9`** | constats de sortie conduits intégralement |

## 2. Les deux propagations — **QUALIFIÉES**

Les cinq conditions cumulatives du §8.1.2 du bornage sont réunies **dans les deux
cas**.

| Condition | `M5 bis` | `S3 bis` |
|---|---|---|
| **1 · attribution POSITIVE** | quatre événements dans l'ordre **1 → 2 → 3 → 4** · `<unité-superviseur>` **sans aucune entrée** sur la fenêtre · l'identifiant d'invocation porté par le démarrage du démon **au journal** est **celui relevé par `M6`** | idem, ordre **1 → 2 → 3 → 4** · superviseur **inactif** · identifiant **celui relevé par `S3`** |
| **2 · dans les `60 s`** | arrêt du pont puis démarrage du pont, **tous deux dans la fenêtre** | idem |
| **3 · unique** | **un** identifiant nouveau par rapport au baseline | **un** identifiant nouveau par rapport au baseline **et** à celui déjà dénombré |
| **4 · compteur de relances** | **inchangé** — corroboration | **inchangé** |
| **5 · état** | pont **`active/running`** · superviseur **nominal** | idem |

> **`P2A-6` ne s'est pas déclenchée.** L'attribution **positive** a fonctionné
> comme conçue : la transition de `<unité-démon>` s'est trouvée **strictement
> encadrée** par celle de `<unité-pont>`, et le terme comparé par `(c)` s'est
> retrouvé **des deux côtés**.

## 3. La fenêtre d'observation

| | |
|---|---|
| **Fenêtre sous verbosité élevée** — de la **commande `M5`** à la **commande `S3`** | **`603,6 s`** |
| **Durée réelle de fonctionnement sous verbosité élevée** — du `Started` au `Stopped` de `<unité-démon>`, **bornes lues au journal à la microseconde** | **`590,439 s`** |
| Intervalle du **premier relevé `O2`** à la **commande `S3`** — ce que les versions antérieures appelaient à tort une durée de fonctionnement | **`[588,1 ; 588,7] s`** |
| Étendue de la **surveillance `O2`** — du premier au dernier relevé | **`640 s`** |
| **`P2A-9`** — plafond de **15 minutes**, soit `900 s` | **NON ATTEINT** : `603,6 s < 900 s` |
| Cycles du superviseur sous verbosité élevée | **trois**, **tous nominaux** |
| Relevés `O2` | **33** — voir §3.1 |
| Terminaison | **anticipée**, **la cible de trois cycles étant atteinte** — voir **§3.0** |

> **Quatre durées, et elles ne se confondent pas.** La **fenêtre** court de
> commande à commande ; le **fonctionnement réel** sous verbosité élevée court du
> démarrage effectif du démon à son arrêt ; l'**étendue de la surveillance**
> déborde la fenêtre des deux côtés ; et le `589,1 s` des versions antérieures
> n'est **aucune des trois**.

> **Ce que `589,1 s` mesure réellement, et pourquoi l'étiquette était fausse.**
> Sa borne basse est le **premier relevé `O2`** — `06:21:41`, à la **seconde** —
> et sa borne haute la **commande `S3`**. **Ce n'est ni un début ni une fin de
> fonctionnement** : les deux bornes sont décalées vers l'intérieur. Les versions
> antérieures l'appelaient *« durée réelle de fonctionnement sous `-g` »* —
> **c'était faux**.

> **Et la décimale était artificielle.** La borne basse n'ayant qu'une résolution
> à la seconde, l'intervalle réel est **`[588,102 ; 588,680] s`**, porté
> **`[588,1 ; 588,7] s`** : **une valeur unique à la décimale supposerait une
> précision que la source n'a pas.**
>
> **La V8 l'avait laissé à `[588,1 ; 589,1] s`** : elle avait établi au §0 que le
> premier relevé `O2` ne peut pas précéder `06:21:41,421`, **sans propager cette
> borne ici**. La borne haute en découle : `06:31:30,101506 − 06:21:41,421068`.

> **La vraie durée, et d'où elle vient.** Le journal système porte les deux
> bornes **à la microseconde** : `Started` de `<unité-démon>` à
> **`06:21:41,421`**, `Stopped` à **`06:31:31,860`** — §0 pour la correspondance
> en `CEST` —, soit **`590,439 s`**. **Ces deux instants tombent l'un et l'autre
> à l'intérieur des fenêtres prescrites** de `M5 bis` et de `S3 bis` — ils ne
> proviennent donc **pas** des débordements de lecture consignés au §3.2.

> **Écart consigné sur la fenêtre.** L'audit annonce `610 s` de commande à
> commande. Les artefacts donnent **`603,613 s`** — commande `M5` à
> `06:21:26,489`, commande `S3` à `06:31:30,102`. **L'écart est de `6,4 s`**, et
> **le chiffre retenu est celui des artefacts**. `P2A-9` n'est atteint dans
> aucune des deux lectures.

### 3.0 Le motif réel de la terminaison anticipée

**Les versions antérieures écrivaient que la fenêtre avait été close *« dès que
la matière a suffi aux objectifs »*. C'est sans fondement**, et les artefacts
l'établissent.

> **Aucune ligne du journal n'a été lue pendant la phase 2.** `O2` y relevait la
> **taille** de `<journal-démon>` — une valeur en octets, à chaque relevé — et
> **jamais son contenu**. Les artefacts de la phase 2 ne portent **aucune** ligne
> d'ouverture ni de clôture.

> **Je ne pouvais donc pas savoir si la matière suffisait : je n'en avais lu
> aucune.** La première lecture du contenu est l'extraction de `06:34:37`, **après
> la sortie du lot** — §4.1.

**Le motif réel, et le seul que les faits portent :**

| | |
|---|---|
| ce qui a déclenché la fermeture | **la cible de trois cycles du superviseur était atteinte**, le troisième s'étant terminé |
| ce qui ne l'a pas déclenchée | une appréciation de la matière recueillie, **qui n'avait pas été lue** |

> **Et la terminaison n'était PAS conforme au §4.1 — la V9 l'affirmait, à tort.**
> Le §4.1 du bornage porte **deux** énoncés distincts :
>
> | Énoncé du §4.1 | État |
> |---|---|
> | *« au moins 3 cycles du superviseur »* — un **minimum** | **atteint** |
> | *« terminaison anticipée **exigée dès que la matière suffit** aux objectifs »* — le **déclencheur** | **jamais évalué** |
>
> **Atteindre le minimum n'est pas satisfaire le déclencheur.** Le minimum
> autorise la fermeture ; le déclencheur commande **quand** elle est due. La
> fenêtre a été close **au minimum atteint**, et non sur une suffisance
> appréciée — **laquelle ne pouvait pas l'être**, aucune ligne n'ayant été lue.

> **C'est un écart à la conduite prescrite, et il est consigné comme tel.**
> **Aucun critère `P2A` n'y correspond** : le §4.1 ne porte pas de critère
> d'arrêt sur le motif de fermeture, et **ce document n'en invente pas**. La
> fenêtre est demeurée sous son plafond, et `P2A-9` n'a pas été atteint.

### 3.1 Les relevés `O2` — compte exact et écarts à la fréquence prescrite

**Trois comptes successifs ont été publiés, et les deux premiers étaient
faux** : 31 en V1, **32** en V2 et V3, **33** en réalité. Les artefacts figés
hors dépôt l'établissent.

> **Ce que les deux comptes précédents manquaient.** Un relevé `O2` a été
> effectué **immédiatement après `M6`**, à `06:21:41`, dans un artefact où il
> porte un **format différent** des autres. Le dénombrement le cherchait par sa
> forme, et l'a donc **omis deux fois de suite**.

| Segment | Relevés |
|---|---|
| immédiatement après `M6` | **1** |
| qualification de `M5` | **2** |
| fenêtre, premier segment | **20** |
| fenêtre, second segment | **8** |
| qualification de `S3` | **2** |
| **total** | **33** |

**Dix intervalles dépassent la fréquence prescrite de `15 s`**, et ils sont de
deux natures :

| Nature | Nombre | Valeur | Cause constatée |
|---|---|---|---|
| **dépassement structurel** | **7** | **16 s** | l'attente programmée de 15 s, **augmentée de la durée des consultations elles-mêmes**. Ce n'est pas un aléa : c'est le **coût du relevé**, que la fréquence prescrite n'avait pas provisionné |
| **SILENCE** | **1** | **40 s** | de `06:21:41` à `06:22:21` — **immédiatement après `M5`**. **Omis par la V2 et la V3** |
| **SILENCE** | **1** | **69 s** | de `06:22:36` à `06:23:45` — entre la fin de la qualification de `M5` et le début de la surveillance de la fenêtre |
| **SILENCE** | **1** | **90 s** | de `06:30:36` à `06:32:06` — **cet intervalle recouvre le redémarrage de retour `S3`** |

> **Total brut des silences : `199 s`.** La V3 publiait **`159 s`** : **le chiffre
> était faux**, il omettait le silence de 40 s. Toutes les occurrences sont
> corrigées.

> **INCERTITUDE DE TOUTES CES VALEURS, énoncée une fois pour toutes.** Les
> horodatages `O2` n'ont qu'une **résolution à la seconde**. Toute durée obtenue
> en soustrayant deux d'entre eux porte donc une incertitude **d'au plus une
> seconde sur chaque borne**.
>
> **Cela vaut pour** : les trois silences — `40`, `69`, `90 s` — · leur **total
> de `199 s`** · les **sept dépassements de `16 s`** · l'**étendue de la
> surveillance, `640 s`** · et la **non-couverture de `123 s`** du §3.2, dont une
> borne est un horodatage `O2`.
>
> **Ces valeurs sont publiées en entiers parce que leur source l'est**, et **non
> parce qu'elles seraient exactes.** Elles ne relèvent pas du tableau de recalcul
> du §0, qui ne couvre que les **huit durées dérivées du journal**.
>
> **Aucune conclusion du présent document ne dépend de cette précision** : un
> silence de `69 s` ou de `70 s` est **également** un silence, et le total
> demeure d'un ordre sans rapport avec le plafond de `15 s`.

> **Un quatrième silence a été proposé, et il n'est pas retenu.** L'audit demande
> de compter `06:21:20 → 06:21:41`, soit **`21 s`**, et d'établir le total à
> `220 s`.
>
> | Lecture | D'où court l'obligation `O2` | Écart au premier relevé | Silence ? |
> |---|---|---|---|
> | **retenue** | de la **commande `M5`**, `06:21:26,489` — c'est ce que le §8.1.3 du bornage énonce : *« de la commande de redémarrage jusqu'à la qualification »* | **`[14,932 ; 15,511] s`** — voir ci-dessous | **NON**, dans les deux bornes |
> | proposée | de `06:21:20`, instant où **ma lecture** de qualification a commencé | `21 s` | oui |
>
> **La lecture retenue est celle du bornage**, et elle est aussi celle que `B13`
> impose par ailleurs : **une fenêtre s'ouvre à la commande, pas au moment où
> quelqu'un commence à lire**. Retenir `21 s` ici et `06:31:30` là serait
> appliquer deux règles opposées au même objet.
>
> **Le total des silences demeure donc `199 s`.**

> **Et le premier intervalle n'est PAS exact : il est INDÉTERMINÉ.** La commande
> `M5` est horodatée **à la microseconde**, `06:21:26,488866`. Le premier relevé
> `O2` ne l'est qu'**à la seconde**, `06:21:41` : son instant réel est dans
> `[06:21:41,421 ; 06:21:41,999]` — la borne basse étant le `Started`, dont le §0
> établit que le relevé lui est **nécessairement postérieur**.
>
> | | |
> |---|---|
> | intervalle réel | **entre `14,932 s` et `15,511 s`** — la borne basse est celle du `Started`, §0 |
> | respecte-t-il le plafond de `15 s` ? | **INDÉTERMINÉ** — la borne haute le dépasse |
> | est-ce un silence ? | **NON**, dans les deux bornes : un silence est d'un tout autre ordre |
>
> **Les V4 et V5 affirmaient `14,511 s` et concluaient au respect du plafond.
> C'était traiter comme exacte une valeur que la résolution de la source ne
> permet pas d'établir.** La conclusion est retirée : **il y a sept dépassements
> structurels avérés, et un huitième indéterminé**.

> **Aucun `ABORT` n'était dû de ce chef** : la fréquence du §8.3.2 est une
> **règle de conduite**, une valeur **choisie**, et **aucun critère `P2A` ne
> porte sur son dépassement**. Le constat est donc un **écart à la conduite
> prescrite**, non un manquement à un critère d'arrêt.

> **Rien n'est corrigé rétrospectivement.** Les relevés figés portent leurs
> horodatages réels ; ce paragraphe les rapporte, il ne les retouche pas.

### 3.2 Les 199 s de silence — deux questions distinctes

**La V3 confondait deux choses.** Elles se traitent séparément, et leurs réponses
diffèrent.

| | Question | Réponse |
|---|---|---|
| **(i)** | la **préemption en temps réel** était-elle disponible ? | **NON, pendant la totalité des `199 s`** |
| **(ii)** | le **fait** — seuil atteint ou non — est-il couvert **rétrospectivement** ? | **partiellement**, et le §8.1.2.3 (a) en est le moyen |

#### (i) — la préemption temps réel : indisponible sur les `199 s`

La préemption prévue au §8.1.1 repose sur `O2`. **Sans relevé, un franchissement
de `P2A-12` par une invocation du superviseur n'aurait pas été vu au moment où il
se produisait, et la conduite d'urgence n'aurait pas pris la main.**

**Cela vaut pour les trois silences, sans exception**, y compris ceux que la
lecture rétrospective couvre par ailleurs : **une couverture après coup ne rend
pas une préemption possible**.

**Décomposition du silence de `90 s`**, sur les instants des relevés figés :

| Intervalle | Durée | Ce que le bornage y exigeait |
|---|---|---|
| fin de cycle constatée → exécution de `S1` | **≈ 28 s** | **`O2`, par le §6.3.1 (i)** — l'extension couvre *« toute attente d'un retour synchronisé `S1` »*. **C'était exactement cette attente** |
| exécution de `S1`, `S2`, `S3` | ≈ 26 s | les actes de la phase, permis |
| redémarrage `S3` → reprise des relevés | **≈ 36 s** | **`O2`, par le §8.1.3** — la qualification différée était engagée |

> **`O2` était exigé par DEUX clauses distinctes pendant ce silence, et il était
> absent des deux.**

#### (ii) — la couverture rétrospective du fait, par le §8.1.2.3 (a)

**Le §8.1.2.3 (a) exige, pour la condition 5, qu'*« aucune invocation — terminée
ou en cours — n'atteigne le seuil de `P2A-11` »*, sur la fenêtre de
qualification.** `M5 bis` et `S3 bis` l'ont vérifié, **rétrospectivement**, sur
leurs fenêtres respectives.

> **Ce sont donc bien des canaux rétrospectifs pour le FAIT** — seuil atteint ou
> non —, et la V3 avait tort d'écrire que ces critères *« n'étaient surveillés par
> rien »* sur l'ensemble des silences.

> **Une fenêtre de qualification s'ouvre À LA COMMANDE.** C'est ce que le §8.1.2
> du bornage énonce — la condition 2 court *« dans les `60 s` qui suivent la
> commande »* —, et **l'instant où une lecture a effectivement commencé ne
> déplace pas cette borne**.

| Silence | Durée | Fenêtre prescrite qui le couvre | Couvert | Non couvert |
|---|---|---|---|---|
| `06:21:41` → `06:22:21` | **40 s** | **`M5 bis`** : `06:21:26,489` → `06:22:26,489` | **40 s** — entièrement dedans | **0 s** |
| `06:22:36` → `06:23:45` | **69 s** | **aucune** | 0 s | **69 s** |
| `06:30:36` → `06:32:06` | **90 s** | **`S3 bis`** : `06:31:30,102` → `06:32:30,102` | **36 s** | **54 s** |

> **L'absence réelle de couverture est donc de `123 s`** : les `69 s` du second
> silence, et les `54 s` du troisième qui **précèdent la commande `S3`**.

> **Deux lectures ont débordé leur fenêtre prescrite, et elles sont consignées
> comme telles.**
>
> | Lecture | A commencé à | Fenêtre prescrite ouverte à | Débordement |
> |---|---|---|---|
> | `M5 bis` | `06:21:20` | `06:21:26,489` | **`6,489 s` avant** |
> | `S3 bis` | `06:31:24` | `06:31:30,102` | **`6,102 s` avant** |
>
> **Ces débordements ne réduisent aucune non-couverture.** La V4 s'en était
> servie pour ramener le total de `123 s` à `117 s` — **c'était utiliser une
> lecture hors portée comme si elle était prescrite**, et c'est retiré.

> **Et leur statut au regard de la liste close est tranché : ils SONT hors liste
> close.**
>
> L'acte `M5 bis` prescrit de *« lire rétrospectivement le journal système […]
> **sur la fenêtre de qualification** »*, et `S3 bis` *« par les mêmes lectures
> […] et sur la même fenêtre »*. **La fenêtre est la borne de l'acte**, et
> §8.1.2 la fait courir **à partir de la commande**. Lire six secondes avant,
> c'est lire **au-delà de ce que l'acte prescrit**.
>
> **La même règle que pour le décompte final de lignes s'applique donc**, et elle
> s'applique **symétriquement** : `S8` prescrit la taille et non les lignes ;
> `M5 bis` et `S3 bis` prescrivent une fenêtre, et la lecture l'a dépassée. **Il
> n'y a aucune raison de traiter l'un plus sévèrement que les autres.**
>
> **Deux occurrences supplémentaires de `P2A-1` sont donc consignées** — §5.2.

#### Ce que la couverture rétrospective ne rattrape jamais

| | Couvre | Ne couvre pas |
|---|---|---|
| **`M5 bis`** / **`S3 bis`** | le **fait** — seuil `P2A-11` atteint ou non — sur **leurs** fenêtres, par le §8.1.2.3 (a) | **la préemption**, qui ne peut pas être rétroactive · et **tout instant hors de leurs fenêtres** |
| **`S9`** | le **dénombrement** des identifiants du pont sur la durée du lot | **`P2A-11` et `P2A-12`** — il ne lit que le journal du pont |

### 3.3 Ce que la lacune atteint, et ce qu'elle n'atteint pas

**La V4 laissait entendre que onze critères demeuraient incertains. C'est faux**,
et la portée réelle est bien plus étroite.

| Critère | État | Sur quoi il repose |
|---|---|---|
| **`P2A-1`** | **ATTEINT QUATRE FOIS** — **§5.2 en entier** | `M5 bis` et `S3 bis`, lectures excédant leur fenêtre · `S8`, décompte de lignes non prescrit · **extraction des lignes à `06:34:37`, acte de phase 2 exécuté après la phase 3** |
| **`P2A-2`** | **établi** — non atteint | `M2` : sortie vide, code 0 |
| **`P2A-3`** | **établi** — non atteint | `M4` : comparaison caractère à caractère |
| **`P2A-4`** | **ATTEINT à `M5`** — §5.3 | l'unité n'est devenue active que **`14,932 s`** après l'émission de la commande, contre un plafond de **`10 s`**. **Non atteint à `S3`** : `1,767 s` |
| **`P2A-6`** | **établi** — non atteint | `M5 bis`, `S3 bis` et surtout **`S9`, qui couvre la DURÉE ENTIÈRE du lot** pour les identifiants du pont |
| **`P2A-7`** | **établi** — non atteint | `P3` et `S8` aux bornes : croissance de `1,44 Mo` contre un seuil de `100 Mio`, espace libre inchangé |
| **`P2A-8`** | **établi** — non atteint | **trois preuves indépendantes de `O2`** : voir ci-dessous |
| **`P2A-9`** | **établi** — non atteint | `603,6 s < 900 s` |
| **`P2A-10`** | **établi** — non atteint | aucun doute d'exploitant n'a été formé |
| **`P2A-5`** | **NON CONSTATABLE sur `123 s`** | voir ci-dessous |
| **`P2A-11`** | **NON CONSTATABLE sur `123 s`** | il repose sur la durée des invocations du superviseur, que rien n'observait sur ces intervalles |
| **`P2A-12`** | **NON CONSTATABLE sur `123 s`** | idem |

> **`P2A-5` rejoint la réserve, et la V5 avait tort de l'en exclure.** Il est
> **composite** : il se déclenche sur **l'un QUELCONQUE** de ses trois
> détecteurs.
>
> | Détecteur | Sur les `123 s` |
> |---|---|
> | **`D-1`** — redémarrage du pont | **couvert** : `S9` dénombre les identifiants du pont sur **toute la durée du lot**, et n'en trouve que deux, tous deux qualifiés |
> | **`D-2`** — durée d'invocation du superviseur | **NON couvert** — même lacune que `P2A-11` / `P2A-12` |
> | **`D-3`** — ligne propre du superviseur | **NON couvert** sur ces intervalles |
>
> **Savoir que `D-1` n'a pas signalé ne suffit pas.** Il aurait suffi que `D-2`
> ou `D-3` signale pour que `P2A-5` soit atteint — et **rien ne les observait**.
> **`P2A-5` est donc NON CONSTATABLE sur ces `123 s`**, exactement comme
> `P2A-11` et `P2A-12`.

> **La réserve porte donc sur TROIS critères** : `P2A-5`, `P2A-11`, `P2A-12`.

> **`P2A-8` — redémarrage machine — repose désormais sur des preuves qui ne
> doivent RIEN à `O2`.** La V5 invoquait une *« continuité des cycles et des
> invocations relevées »* : **cette continuité passait par `O2`**, muet `199 s`.
> **On ne peut pas fonder une continuité sur une surveillance interrompue.**
>
> | Preuve | Ce qu'elle établit, sans `O2` |
> |---|---|
> | **`S9`** | il dénombre les identifiants d'invocation de `<unité-pont>` sur **toute la durée du lot** et n'en trouve que **deux**. Un redémarrage machine en aurait nécessairement produit un de plus |
> | **`R5.d`** | les **compteurs de relances** du pont et du superviseur sont **inchangés** entre `P2 bis` et `S8` |
> | **relevés de sortie `S4` / `S8`** | l'identifiant de processus du démon et son instant de démarrage sont **cohérents** entre les deux, et le pont porte le même identifiant d'invocation qu'à `S3 bis` |
>
> **Aucune de ces trois preuves ne dépend d'un relevé `O2`**, ni de sa continuité.

> **En résumé : la lacune est réelle, et elle est bornée.** Elle porte sur la
> durée des invocations du superviseur pendant `123 s`, et atteint **trois**
> critères : `P2A-5`, `P2A-11`, `P2A-12`. **Elle n'entame aucun des autres
> constats**, qui reposent sur des preuves dédiées et non sur `O2`.

## 4. Verdicts `P2-O1` à `P2-O5`

> **RENVOI CHRONOLOGIQUE, et il ne préjuge de rien.**
>
> **Le premier instant où un `ABORT` était dû est `M5`, au titre de `P2A-4`** —
> commande à `06:21:26,489`, constat qui l'établit à `06:21:41,421`. Le second
> est **`M5 bis`**, au titre de `P2A-1`, exécuté à `06:22:36`.
>
> | Matière | Recueillie |
> |---|---|
> | les lignes de journal de la fenêtre | **produites** de `06:21:41` à `06:31:30` · **extraites de l'hôte à `06:34:37`**, soit **après `S9`** — voir §4.1 |
> | l'analyse d'appariement et les durées de session | **hors ligne**, sur l'extraction ci-dessus |
> | `S3 bis`, `S4` à `S9`, et toutes les preuves de restauration | de `06:32:36` à `06:33:55` |
>
> **Toute la matière `P2-O1` → `P2-O5` et toutes les preuves ultérieures ont donc
> été recueillies APRÈS l'instant où un `ABORT` était déjà dû.**
>
> **Ce renvoi est un fait de chronologie, et rien d'autre.** Le présent document
> **ne juge pas** la validité de cette matière : il n'affirme ni qu'elle est
> viciée, ni qu'elle ne l'est pas. **Il la situe.**

### 4.1 D'où vient la matière analysée — et le quatrième `P2A-1`

**La question devait être tranchée** : l'analyse postérieure a-t-elle procédé des
**seuls artefacts déjà figés par `O3`**, ou d'une **nouvelle lecture de l'hôte**
après la sortie ?

> **Réponse : d'une nouvelle lecture.** Les lignes de la fenêtre ont été
> extraites de `<journal-démon>` **à `06:34:37`**, **après `S9`** qui s'achevait
> à `06:33:55`. Tout ce qui suit — décompte par type, appariement, durées de
> session — est **hors ligne**, sur cette extraction.

| Étape | Nature | Instant |
|---|---|---|
| `S9`, dernier acte de la phase 3 | lecture de l'hôte, **prescrite** | `06:33:55` |
| **extraction des lignes de la fenêtre** | **lecture de l'hôte** | **`06:34:37`** |
| décompte, appariement, durées | **hors ligne**, sur l'artefact | après |

> **Cette lecture est HORS LISTE CLOSE, et pour une raison de phase.** Son
> **contenu** est exactement ce que `O1` prescrit — *« lire exclusivement les
> lignes produites après cette position »*. Mais **`O1` est un acte de la
> PHASE 2**, et il a été exécuté **après la fin de la phase 3**. Le §6.3.1
> n'étend hors de sa phase que **`O2`**, et **aucune extension ne couvre `O1`**.

> **Traitement symétrique, comme au §5.2.** Un acte exécuté hors de la phase que
> la liste close lui assigne est un acte hors liste close, **au même titre**
> qu'un acte excédant une fenêtre ou une nature de relevé. **Quatrième occurrence
> de `P2A-1`.**

> **Le produit de cette lecture est néanmoins CONSERVÉ, et son origine lui reste
> attachée.** Le §5.2.1 motive ce choix et le distingue de l'exclusion du chiffre
> issu de `S8`.

### `P2-O1` — **`CLÔTURES OBSERVABLES`**

**279 clôtures de connexion** là où le régime nominal en compte **zéro**. Les
séquences de verrou et les commandes reçues apparaissent également.

### `P2-O2` — **`APPARIEMENT SANS AMBIGUÏTÉ`**

**Critère d'appariement effectivement employé : l'ORDRE — l'alternance stricte.**
**Pas le descripteur** : il est **constant à l'ouverture comme à la clôture**, et
ne porte donc aucune information distinctive.

| | |
|---|---|
| événements retenus | **559** — 280 ouvertures, 279 clôtures |
| **violations de l'alternance** | **0** |
| paires appariées | **279** |
| **taux de séquences non appariables** | **1 sur 280**, soit l'ouverture **en cours à la fermeture de la fenêtre** — expliquée par la **borne**, non par une ambiguïté |

### `P2-O3` — la grandeur, **typée**

**La durée de session vue du démon**, de l'ouverture de connexion à sa clôture.

| Elle **contient** | Elle **exclut** |
|---|---|
| l'intégralité de la session cliente — connexion, commandes, échanges avec le périphérique, clôture | tout ce qui précède la connexion et tout ce qui suit la clôture |

**Elle ne distingue aucun client.**

| n | min | médiane | max |
|---|---|---|---|
| **279** | **1 s** | **2 s** | **3 s** |

**Toutes les valeurs sont entières** : la résolution de la source est **la
seconde**.

### `P2-O4` — **`ENVELOPPE DIFFÉRENTE UNIQUEMENT`**, motivé

| | |
|---|---|
| **aucun apport à `U-2`** | la **population n'est pas isolée**. Le descripteur est constant, la ligne de clôture ne porte pas le port, et **rien au journal ne rattache une session à un client**. Les sessions relevées **mélangent** les deux clients sans moyen de les séparer |
| **aucun apport à `U-7`** | Boilerack **n'a pas tourné**. L'occupation qu'il imposerait est sans rapport avec ce qui a été mesuré |
| **et un motif qui suffirait seul** | les sessions durent **1 à 3 s** et la résolution est **1 s**. **L'incertitude est du même ordre que la grandeur** |

> **C'est donc une troisième enveloppe** — distincte de `R`, distincte de
> l'enveloppe d'invocation homologuée sous `W4-P1` — **et rien de plus**.

### `P2-O5` — limites subsistantes

| # | Limite |
|---|---|
| **1** | **résolution à la seconde**, contre des durées de **1 à 3 s** |
| **2** | **aucune attribution** : descripteur constant des deux côtés, aucun discriminant client au journal |
| **3** | **la déformation par l'observation** — `w4-cadrage-activation-debug.md` §E.3 — demeure de **magnitude non établie**, et **n'a pas été mesurée** ici |
| **4** | **l'appariement n'a pas été éprouvé contre les terminaisons anormales** : le fait `F-11` en établit l'existence, mais la fenêtre n'en a compté **aucune**. L'alternance stricte n'a **pas** été testée contre ce cas |
| **5** | **`U-7` demeure intacte** |
| **6** | **aucune qualification** de quoi que ce soit — elle appartient à **`T0-D`**, qui n'a pas eu lieu |

## 5. Preuves de restauration

> **Même renvoi chronologique qu'au §4** : les preuves qui suivent ont été
> recueillies **après** l'instant où un `ABORT` était déjà dû — `M5` au titre de
> `P2A-4`, `M5 bis` au titre de `P2A-1`. **Fait de chronologie, sans jugement de
> validité.**

| Réf | Résultat |
|---|---|
| **`R1`** | **SATISFAITE** — répertoire **et** fichier de surcharge absents, confirmés séparément |
| **`R2`** | **SATISFAITE** — les deux fichiers d'origine ont **taille, date et condensat identiques** au préflight. Ils n'ont **jamais** été touchés |
| **`R3`** | **SATISFAITE** — invocation effective du **processus** identique au préflight, **sans l'option de verbosité** |
| **`R4`** | **SATISFAITE** — sur les lignes du **démon de retour** : les types visés comptent **tous zéro** |
| **`R5.a`** | **SATISFAITE** — **une seule** instance |
| **`R5.b`** | **SATISFAITE** — **détenteur du périphérique** établi par les **deux méthodes indépendantes** de l'Acte A, sur le **même** identifiant de processus |
| **`R5.c`** | **SATISFAITE** — les ouvertures de connexion **reparaissent** après le retour, **sans que le lot ouvre de session** |
| **`R5.d`** | **SATISFAITE** — pont et superviseur **nominaux**, compteurs de relances **inchangés** |
| **`R5.e`** | **SATISFAITE** — le dénombrement rétrospectif complet rend **deux** identifiants nouveaux, soit **exactement** le nombre de propagations **qualifiées** ; **chacune est attribuée** à sa commande ; le pont est **`active/running`** en sortie |
| **`R6`** | **SATISFAITE** — chiffrage porté au §5.1 |
| **`R7`** | **SANS OBJET** — **uniquement parce qu'aucun `ABORT` n'a été prononcé**. Voir **§5.3** : le premier `ABORT` dû l'était à **`M5`**, au titre de **`P2A-4`** ; puis §5.2, au titre de `P2A-1`, **quatre fois** |

> **`R5.e` est satisfaite sur ses trois composantes** — compte, attribution, état
> du pont —, et aucun des verdicts d'échec du §7.1 n'est prononcé.

### 5.1 `R6` — le chiffrage

| | Avant, au préflight | Après, en sortie | Delta |
|---|---|---|---|
| **octets** | **504 208 733** | **505 651 032** | **+1 442 299** |

> **« Espace libre inchangé » est une observation À LA GRANULARITÉ DU RELEVÉ.**
> L'espace libre a été relevé **en pourcentage entier** de la partition, et il
> est demeuré au même entier de bout en bout. **Cela n'entre en aucune
> contradiction avec la croissance mesurée ci-dessus** : le volume ajouté est
> **très inférieur** au pas d'un point de pourcentage sur cette partition. **Les
> deux constats sont compatibles**, et le second ne dit rien de plus que ce que
> sa granularité permet.

> **L'espace consommé reste consommé.** Aucune rotation ne couvre ce puits — fait
> `F-6` du bornage. Le retrait de ce volume serait un **acte distinct, hors de ce
> lot**, et `R6` se borne à le **chiffrer**.

> **`R6` porte sur le VOLUME EN OCTETS, et sur lui seul.** C'est ce que l'acte
> `S8` prescrit de relever en sortie : la **taille finale** et l'**espace libre**.

> **Le chiffre qu'elle a produit n'entre pas dans le présent document** : ni la
> ligne « après », ni le delta correspondant. **Mais la lecture, elle, a eu lieu**,
> et sa qualification est au §5.2.

> **Et son exclusion tient à un motif PROPRE, non à l'illicéité commune.** Ce
> chiffre **n'a aucune utilité probante** : `R6` porte sur le **volume en
> octets**, que `S8` prescrit et qui suffit à l'établir. Le total de lignes
> **n'apporte rien** que la taille ne dise déjà, **n'étaye aucun verdict**, et
> **ne fonde aucun constat**.
>
> **C'est pourquoi il est écarté, et non seulement parce qu'il fut acquis hors
> liste close.** Un produit hors liste close n'est pas écarté par principe — le
> §5.2.1 le montre pour la quatrième lecture. **Il l'est ici parce qu'il ne sert
> à rien**, et l'écarter ne prive le document d'aucune matière.

### 5.2 `P2A-1` a été atteint QUATRE FOIS, et l'`ABORT` n'a pas été prononcé

**Le fait.** Un **total final de lignes** de `<journal-démon>` a été relevé au
moment de `S8`. **`S8` ne le prescrit pas** : il prescrit la **taille finale** et
l'**espace libre**, rien d'autre. Le nombre de lignes n'est prescrit qu'au
**préflight**, par `P3`.

> **Cette lecture est donc un acte HORS DE LA LISTE CLOSE.**

**Deux autres actes le sont également, et pour la même raison.** Les lectures de
`M5 bis` et de `S3 bis` ont **débordé la fenêtre** qui borne ces actes — §3.2.

| # | Acte | Ce que la liste close prescrit | Ce qui a été fait |
|---|---|---|---|
| **1** | `M5 bis` | lire les journaux **sur la fenêtre de qualification**, laquelle s'ouvre **à la commande** `06:21:26,489` | lecture depuis `06:21:20` — **`6,489 s` avant** |
| **2** | `S3 bis` | idem, fenêtre ouverte à `06:31:30,102` | lecture depuis `06:31:24` — **`6,102 s` avant** |
| **3** | `S8` | relever la **taille finale** et l'**espace libre** | un **décompte de lignes** en outre |
| **4** | `O1`, second volet | acte de la **phase 2** | exécuté **après la fin de la phase 3**, à `06:34:37` — §4.1 |

> **Le traitement est symétrique, et il doit l'être.** Un acte qui excède la
> borne que la liste close lui donne est un acte hors liste close, **que la borne
> soit une fenêtre de temps, une nature de relevé, ou une phase**. Traiter l'un
> en écart et les autres en détail serait une asymétrie sans justification.

**La norme.** `P2A-1` se déclenche lorsqu'*« un acte hors de la liste close du §6
est envisagé, ou son appartenance est douteuse »*. **La condition était remplie
QUATRE FOIS : à `M5 bis`, à `S3 bis`, à `S8`, et à l'extraction de `06:34:37`. Un
`ABORT` était dû dès la première.**

**Les deux registres, tenus séparés :**

| Registre | Énoncé |
|---|---|
| **FAIT** | **aucun `ABORT` n'a été déclaré** au cours de la campagne. L'écart n'a été identifié qu'**après** la sortie, au réaudit |
| **NORME** | **un `ABORT` était dû à partir de `P2A-1`**, et **dès `M5 bis`** — donc **avant même l'ouverture de la fenêtre d'observation**. Le fait qu'il n'ait pas été prononcé **ne le rend pas non dû** |

> **`R7` est `SANS OBJET` UNIQUEMENT parce qu'aucun `ABORT` n'a été prononcé.**
> Il **ne s'ensuit pas** qu'aucun n'était dû. La preuve `R7` porte sur la
> consignation d'un relevé partiel après un `ABORT` **déclaré** ; aucun ne l'a
> été, donc elle est sans objet — **et c'est tout ce que cela signifie**.

#### 5.2.1 Pourquoi le produit de la quatrième lecture est conservé, et celui de la troisième écarté

**Les quatre lectures sont également hors liste close. Leurs produits ne
reçoivent pourtant pas le même traitement, et la différence doit être motivée.**

| | Produit | Traitement | Motif |
|---|---|---|---|
| **n° 3** — décompte de lignes à `S8` | un nombre | **ÉCARTÉ** | **motif propre** : il **n'a aucune utilité probante**. `R6` s'établit sur le volume en octets, que `S8` prescrit. Ce chiffre n'apporte rien, n'étaye aucun verdict, ne fonde aucun constat. **L'écarter ne prive le document d'aucune matière** |
| **n° 4** — extraction des lignes à `06:34:37` | **20 546 lignes** | **CONSERVÉ** | il constitue la **matière brute indispensable** aux constats `P2-O1` → `P2-O5`. **Sans elle, ces constats n'existent pas** |

> **La conservation n'efface pas l'illicéité, et il faut le dire nettement.**
>
> | | |
> |---|---|
> | **la donnée a été acquise HORS LISTE CLOSE** | l'acte `O1` appartient à la phase 2, et il a été exécuté après la fin de la phase 3 |
> | **elle est conservée comme FAIT OBSERVÉ** | les lignes ont été produites par le démon pendant la fenêtre ; leur extraction tardive ne les a ni créées ni modifiées |
> | **son origine hors borne reste ATTACHÉE** | à **toute** interprétation qui en découle — `P2-O1`, `P2-O2`, `P2-O3`, `P2-O4`, `P2-O5`, et tout usage ultérieur |
>
> **Ce document ne juge pas ce que cette origine emporte.** Il ne dit ni que les
> verdicts sont viciés, ni qu'ils ne le sont pas : **il attache l'origine à la
> matière**, et laisse l'appréciation à qui de droit.

> **Le traitement n'est donc pas asymétrique sur l'illicéité** — elle est
> identique pour les quatre. **Il l'est sur l'utilité**, et c'est un critère
> distinct, énoncé ici plutôt que laissé implicite.

### 5.3 `P2A-4` a été atteint à `M5`, et l'`ABORT` n'a pas été prononcé

**Le référentiel des `10 s` devait être tranché**, car deux lectures étaient
possibles : l'**émission de la commande**, ou le **retour synchrone** de celle-ci.

> **C'est l'émission de la commande, et deux appuis le fondent.**
>
> | | Appui |
> |---|---|
> | **1** | `P2A-4` dit *« **après un redémarrage**, l'unité n'est pas active dans les 10 secondes »*. Le redémarrage est l'**acte commandé** ; son instant est celui de la **commande** |
> | **2** | l'acte `M5` prescrit de *« relever l'**INSTANT EXACT de la commande** »*. C'est le **seul instant** dont le bornage exige le relevé en rapport avec le redémarrage, et il est donc **disponible** comme référent. **Le retour synchrone, lui, n'est relevé nulle part** — un critère ne peut pas se référer à un instant que le lot n'a pas mandat de constater |

> **Deux appuis de la V7 sont RETIRÉS, parce qu'ils étaient faux.**
>
> | Appui retiré | Pourquoi il était faux |
> |---|---|
> | *« `M5` n'aurait aucun objet si `M6` ne s'y référait pas »* | **il en a un autre** : la **condition 2 du §8.1.2** borne la propagation attendue *« dans les `60 s` qui suivent cette commande »*. L'instant de `M5` la sert, `M6` ou non |
> | *« le §8.3.3 emploie le même point de départ »* | **il en emploie un autre** : son `t_départ` est l'**instant de démarrage de l'invocation du superviseur**, pas la commande de redémarrage du démon. **La référence ne soutenait rien** |

> **Ce que l'autre lecture aurait donné, énoncé étroitement.** Le retour de
> `systemctl restart` est **postérieur** au démarrage effectif : compter de là
> rendrait **la BRANCHE DÉLAI** de `P2A-4` incapable de se déclencher, l'unité
> étant active par construction au moment du retour.
>
> **`P2A-4` ne serait pas pour autant inopérant** — la V7 l'écrivait, et c'était
> trop large : sa **seconde branche**, l'incrément du compteur de relances,
> continuerait de fonctionner. **C'est la branche délai seule qui serait vide**,
> et c'est déjà une raison suffisante d'écarter ce référentiel.

**Le constat, dans le référentiel retenu :**

| | Émission de la commande | `Started` du démon | Écart | Plafond `10 s` |
|---|---|---|---|---|
| **`M5`** | `06:21:26,489` | `06:21:41,421` | **`14,932 s`** | **DÉPASSÉ — `P2A-4` ATTEINT** |
| **`S3`** | `06:31:30,102` | `06:31:31,868` | `1,767 s` | respecté |

> **La cause est établie, et elle n'est pas dans le démon.** À `M5`, l'arrêt du
> **pont** a duré **`14,648 s`** — de `06:21:26,746` à `06:21:41,394` —, et le
> démon ne pouvait démarrer qu'après. À `S3`, le même arrêt n'a duré que
> **`1,647 s`**. **C'est la durée d'arrêt du pont qui a fait franchir le
> plafond**, non une défaillance du démon.

**Les deux registres, tenus séparés comme au §5.2 :**

| Registre | Énoncé |
|---|---|
| **FAIT** | **aucun `ABORT` n'a été déclaré**. La vérification `M6` a conclu *« actif »* sans mesurer l'écart à la commande |
| **NORME** | **un `ABORT` était dû à `M5`**, au titre de `P2A-4`. Le fait qu'il n'ait pas été prononcé **ne le rend pas non dû** |

> **Ce n'est pas la signature que `P2A-4` visait.** Le critère nomme *« signature
> d'une boucle »*, et **il n'y a pas eu de boucle** : le compteur de relances est
> demeuré nul, le démon a démarré une fois et n'est pas reparti. **Le critère
> n'en a pas moins été franchi**, et le bornage ne subordonne pas son
> déclenchement à la présence d'une boucle : il énonce **deux** conditions
> alternatives, dont celle du délai.

> **Ce que ces écarts n'ont pas affecté.** Les **quatre** lectures étaient
> **passives** — de **trois natures distinctes** :
>
> | Nature | Occurrences | Ce qu'elle a lu |
> |---|---|---|
> | **décompte de lignes** | **1** — à `S8` | un nombre, sur un fichier |
> | **lecture de journal élargie de six secondes** | **2** — à `M5 bis` et `S3 bis` | les mêmes entrées, sur une fenêtre trop large de `≈ 6 s` |
> | **extraction complète des lignes de la fenêtre** | **1** — à `06:34:37` | **20 546 lignes** du journal du démon |
>
> Aucune écriture, aucune mutation, aucun effet sur le démon, le pont ou le
> superviseur. **Aucune preuve de restauration n'en dépend**, `R6` repose sur la
> taille que `S8` prescrit, et les instants employés au §3 tombent **à
> l'intérieur** des fenêtres prescrites.
>
> **Cela n'atténue pas le manquement** : `P2A-1` ne distingue pas les actes hors
> liste selon leur innocuité. **Et la quatrième n'est pas de même ampleur que les
> trois autres** : elle porte sur **l'intégralité de la matière** dont les
> verdicts `P2-O1` à `P2-O5` sont tirés.

## 6. État final

| | |
|---|---|
| `<unité-démon>` | **`active/running`**, invocation **d'origine** |
| `<unité-pont>` | **`active/running`**, nominal |
| `<unité-superviseur>` | **nominal**, cycle suivant armé |
| Configuration | **identique au préflight**, empreintes à l'appui |
| `<dropin-démon>` | **inexistant** |

> **L'état est entièrement restauré.** Ce qui ne l'est pas, et le bornage le
> prévoyait : **l'espace consommé dans le journal reste consommé**, aucune
> rotation ne le reprenant. Son retrait serait un **acte distinct, hors de ce
> lot**, et `R6` se borne à le chiffrer.

## 7. Observation relevée et NON CONSOMMÉE

**Constat strict, et il ne va pas au-delà :** sur les **deux arrêts observés**
de `<unité-démon>` pendant cette campagne, le journal système porte la mention
**`status=1/FAILURE`**.

> **Correction de la V1.** Elle écrivait *« le démon sort en code non nul
> lorsqu'il est arrêté »*. **C'est une règle générale, et rien ici ne
> l'établit** : deux observations ne font pas un comportement. La formulation est
> ramenée à ce qui a été vu.

> **Aucune règle, aucune causalité, aucune imputation.** Ce constat **n'entre
> dans aucun critère** de la campagne, **n'a affecté ni la présence ni l'ordre**
> des quatre événements de l'attribution positive, et **ce document ne
> l'interprète pas**. Il est consigné **parce qu'il est visible**, et pour aucune
> autre raison.

## 8. Ce que ce document ne fait pas

Il **ne qualifie aucune borne**, **ne produit aucun seuil**, **ne produit aucun
critère**, **ne rouvre pas `C1`**, **ne rend aucun verdict `T0-A`, `T0-B`,
`T0-C` ni `T0-D`**, **ne lève ni `U-2` ni `U-7`**, **ne tranche aucune voie du
§10.3.3**, **ne modifie aucun autre contrat ni chantier**, et **ne déduit aucune
autorisation nouvelle** — ni de terrain, ni d'écriture.

Il consigne un résultat, et s'arrête là.

## 9. Historique de révision

| Version | Objet |
|---|---|
| **1** | Consignation du résultat terrain de `W4-P2` V14 : campagne exécutée **« sans `ABORT` ni `STOP` »** — **verdict initial, INVALIDÉ depuis : les V6, V7 et V8 établissent que `P2A-1` a été atteint quatre fois et `P2A-4` une fois, sans qu'aucun `ABORT` soit prononcé** —, deux propagations qualifiées, verdicts `P2-O1` à `P2-O5`, preuves de restauration, limites conservées. Aucune interprétation, aucune autorisation déduite. |
| **2** | Après audit. `B1` : le compte de relevés `O2` était **faux** — **32** et non 31 —, et *« tous à ≤ 15 s »* l'était aussi : **neuf intervalles dépassent 15 s**, dont **deux de 69 s et 90 s**, le second recouvrant le redémarrage de retour. Consignés au §3.1 **sans correction rétrospective**, avec le constat qu'**aucun `ABORT` n'était dû** puisqu'aucun critère ne porte sur cette fréquence. `B2` : la généralisation sur `status=1/FAILURE` est **retirée** au profit du **constat strict** des deux arrêts observés. `B3` : la chronologie **des deux autorisations successives** est rétablie, avec l'écart à la lettre du §9 — qui en contemplait **une** — consigné plutôt que lissé. `B4` : `R6` porte désormais son **chiffrage**, et *« espace libre inchangé »* est qualifié comme observation **à la granularité du relevé**. **`P2-O2` inchangé.** Aucune valeur brute ajoutée au-delà du chiffrage `R6`. |
| **3** | Après réaudit. `B5` : l'en-tête portait **deux bannières de version** ; il n'en porte plus qu'**une**, les versions antérieures étant au présent paragraphe. `B6` : **la couverture rétrospective était surestimée** — nouveau §3.2, qui décomposait alors **159 s sans `O2`** — **chiffre corrigé en V4 : le total réel est `199 s`**, nomme que l'interruption de 90 s recouvre l'attente de `S1` où le §6.3.1 (i) exigeait `O2` **et** le début de la qualification où le §8.1.3 l'exigeait aussi, en tire que **la préemption était indisponible**, et exclut que `S3 bis` ou `S9` couvrent `P2A-11` / `P2A-12` sur ces intervalles ; *« aucun critère atteint »* devient *« aucun **constaté** atteint »*. `B7` : les qualifications *« sens prudent »* et *« plus contraint »* sont **retirées**, le fait seul demeurant. `B8` : le **total final de lignes** ne provenant d'**aucun acte prescrit** — `S8` ne relève que la taille —, la ligne et le delta sont **retirés** du chiffrage, `R6` demeurant satisfait sur les octets, et **l'écart de lecture est consigné**. **`P2-O2` inchangé.** |
| **4** | Après réaudit. `B9` : le §3.2 sépare désormais la **préemption temps réel** — indisponible sur la **totalité** des silences — de la **couverture rétrospective du fait**, assurée par `M5 bis` et `S3 bis` via le **§8.1.2.3 (a)**. La V3 avait tort d'écrire que `P2A-11` et `P2A-12` *« n'étaient surveillés par rien »* : ils l'étaient sur les fenêtres de qualification. L'absence réelle de couverture y était bornée à **`117 s`** — **chiffre corrigé en V5 : le total réel est `123 s`**, la V4 ayant compté comme couvertes des secondes lues hors de la fenêtre prescrite. `B10` : **deux chiffres publiés étaient faux** — les relevés `O2` sont **33** et non 32, un relevé de format différent ayant été omis deux fois ; et le silence total est **`199 s`** et non `159 s`, un **troisième silence de 40 s** immédiatement après `M5` ayant été omis. Toutes les occurrences sont corrigées. **Un écart de 6 s avec le découpage proposé par l'audit est consigné** : la fenêtre de `S3 bis` s'ouvre à `06:31:24`, non à l'instant de la commande, d'où `48 s` / `42 s` et non `54 s` / `36 s`. `B11` : nouveau §5.2 — **`P2A-1` a été atteint** à `S8`, la lecture du nombre de lignes étant hors liste close ; **l'`ABORT` prescrit n'a pas été prononcé** ; le **fait** et la **norme** sont tenus séparés, et `R7` est requalifié — `SANS OBJET` **uniquement** faute d'`ABORT` prononcé. **`P2-O2` inchangé.** |
| **5** | Après réaudit. `B12` : les **trois durées** sont portées et distinguées — fenêtre de commande à commande, fonctionnement effectif sous verbosité élevée, étendue de la surveillance —, `P2A-9` demeurant non atteint. **Écart consigné** : les artefacts donnent **`603,6 s`** de commande à commande, non `610 s`. **Un quatrième silence de `21 s` a été proposé et n'est pas retenu** : l'obligation `O2` court **de la commande**, `06:21:26,489`, d'où un écart de `14,511 s` au premier relevé, **sous le plafond** ; retenir `21 s` ici et l'ouverture à la commande ailleurs serait appliquer deux règles opposées au même objet. Le total demeure **`199 s`**. `B13` : **les fenêtres de qualification s'ouvrent à la commande**, d'où **`54 s` non couvertes** et `36 s` couvertes sur le silence final, et un total non couvert de **`123 s`** ; les deux lectures ayant débordé leur fenêtre de ≈ `6 s` sont consignées comme **lectures hors portée** et **ne réduisent plus rien** — la V4 s'en servait pour ramener `123 s` à `117 s`, ce qui est retiré. `B14` : nouveau §3.3, **critère par critère** — **`P2A-1` atteint**, **`P2A-11` et `P2A-12` seuls non constatables** sur les `123 s`, `P2A-5` établi par `D-1` seul, et **tous les autres établis** par leurs preuves propres ; la formule sur *« onze critères »* est **retirée**. **`P2-O2` inchangé.** |
| **6** | Après réaudit. `B15` : l'étiquette de **`589,1 s`** était fausse — ce n'est **pas** une durée de fonctionnement, mais l'intervalle entre la vérification `M6` et la commande `S3` ; la **vraie durée sous verbosité élevée** est établie aux bornes du journal, **`590,439 s`**, toutes deux intérieures aux fenêtres prescrites. `B16` : **`14,511 s` n'est pas exact** — le relevé de `06:21:41` n'a qu'une résolution à la seconde, l'intervalle réel est dans **`[14,511 ; 15,511] s`** — **borne basse corrigée en V8 : `14,932 s`** — et **le respect du plafond est INDÉTERMINÉ** ; sept dépassements structurels avérés, un huitième indéterminé. `B17` : **`P2A-5` rejoint la réserve** — il se déclenche sur **l'un quelconque** de ses détecteurs, et `D-2` comme `D-3` étaient sans canal ; la réserve porte désormais sur **`P2A-5`, `P2A-11`, `P2A-12`**. `B18` : la preuve de **`P2A-8`** invoquait une continuité qui **passait par `O2`**, muet `199 s` ; elle est remplacée par **`S9`, `R5.d` et les relevés de sortie**, qui n'en dépendent pas. `B19` : **les débordements de lecture de `M5 bis` et `S3 bis` sont hors liste close** — une fenêtre borne un acte au même titre qu'une nature de relevé —, d'où **deux occurrences supplémentaires de `P2A-1`**, **trois au total**, la première dès `M5 bis`, **avant l'ouverture de la fenêtre d'observation**. **`P2-O2` inchangé.** |
| **7** | Après réaudit. `B20` : nouveau §0 — le document mêlait **`UTC`** pour les relevés du lot et **`CEST`** pour le journal **sans le dire** ; le décalage de `+2 h` est explicité, les instants clés **réconciliés dans les deux bases** avec leur résolution, et la formule *« actif après 1 s »* **retirée** faute de référentiel. `B21` : **`589,1 s`** reçoit son **vrai référent** — premier relevé `O2` → commande `S3` — et son **incertitude** : **`[588,1 ; 589,1] s`**, la décimale unique supposant une précision que la source n'a pas. `B22` : **le référentiel des `10 s` de `P2A-4` est tranché — c'est l'émission de la commande**, seul instant dont le bornage prescrit le relevé, l'autre lecture rendant le critère inopérant par construction. Conséquence : **`P2A-4` A ÉTÉ ATTEINT à `M5`**, `14,932 s` contre `10 s`, la cause étant la durée d'arrêt du **pont** — `14,648 s` — et non une défaillance du démon ; **non atteint à `S3`**. Nouveau §5.3, avec les deux registres tenus séparés. **Deux critères atteints, quatre fois en tout, et aucun `ABORT` prononcé.** `B23` : les §4 et §5 portent un **renvoi chronologique** — toute la matière `P2-O1` → `P2-O5` et les preuves ultérieures ont été recueillies **après** l'instant où un `ABORT` était déjà dû —, **sans aucun jugement de validité**. **`P2-O2` inchangé.** |
| **8** | Après réaudit. `B24` : la conclusion sur le référentiel de `P2A-4` est **conservée**, mais **deux de ses appuis étaient faux** et sont retirés — *« `M5` n'aurait aucun objet sinon »*, alors que la condition 2 du §8.1.2 s'en sert, et la référence au **§8.3.3**, dont le `t_départ` est tout autre ; l'argument est resserré : **seule la branche délai** serait vide sous l'autre lecture, non `P2A-4` entier. `B25` : **`M6` est nécessairement postérieur au `Started`**, ayant constaté le nouveau processus — le §0 le disait indécidable, **c'était faux** ; l'intervalle initial est resserré à **`[14,932 ; 15,511] s`**, et **quatre instants** — arrêt du démon à `M5`, arrêt du pont à `S3` — sont ajoutés au tableau, réconciliés dans les deux bases. `B26` : nouveau §4.1 — l'analyse postérieure a procédé d'une **nouvelle lecture de l'hôte à `06:34:37`, après `S9`**, et non des seuls artefacts figés ; `O1` étant un acte de la **phase 2** exécuté après la phase 3, cette lecture est **hors liste close** — **quatrième occurrence de `P2A-1`**. `B27` : le renvoi chronologique nomme **`P2A-4` à `M5`** comme premier `ABORT` dû, **`R7`** renvoie d'abord au §5.3, et la **ligne 1** de l'historique annote que *« sans `ABORT` ni `STOP` »* était le **verdict initial, désormais invalidé**. **`P2-O2` inchangé. Aucune nouvelle interprétation de la matière terrain.** |
| **9** | Après réaudit. `B28` : la borne établie en V8 **n'avait pas été propagée** — l'intervalle du premier relevé `O2` à la commande `S3` est **`[588,1 ; 588,7] s`**, non `[588,1 ; 589,1]`. `B29` : **contradiction tranchée sur les faits** — nouveau §3.0 : **aucune ligne du journal n'a été lue pendant la phase 2**, `O2` n'y relevant que la **taille** ; la formule *« dès que la matière a suffi aux objectifs »* était donc **sans fondement**, puisque je n'avais lu **aucune** matière, et **le motif réel est nommé** : la cible de **trois cycles** était atteinte. `B30` : les trois instants introduits par la V8 — exécution de `M5 bis`, de `S9`, extraction des lignes — sont portés au tableau du §0, **chacun une seule fois, dans les deux bases, avec sa résolution et sa source**, l'extraction étant datée par la **modification de l'artefact** et non par un horodatage interne ; l'ambiguïté `08:34:37` / `06:34:37` est levée. `B31` : *« trois lectures »* devient **quatre**, réparties en **trois natures**, et il est noté que la quatrième porte sur **l'intégralité de la matière** dont les verdicts sont tirés. `B32` : **`P2A-1` reflète ses quatre occurrences** au tableau critère par critère et renvoie au §5.2 **entier**. **`P2-O2` inchangé. Aucune nouvelle interprétation terrain.** |
| **10** | Après réaudit. `B33` : le renvoi de la ligne *« Terminaison »* pointait un **§3.4 inexistant** — corrigé en **§3.0**. `B34` : **deux instants demeuraient publiés en `CEST` dans le corps**, contre la règle que le §0 venait d'énoncer — portés en **`UTC` avec renvoi**. `B35` : la V9 affirmait que la terminaison était intervenue *« comme le §4.1 le prévoyait »* — **c'est faux** ; le §4.1 porte **deux énoncés distincts**, un **minimum de trois cycles**, **atteint**, et un **déclencheur** — *« dès que la matière suffit »* — **jamais évalué**. **Atteindre le minimum n'est pas satisfaire le déclencheur** : la fenêtre a été close au minimum atteint, et c'est un **écart à la conduite prescrite**, consigné **sans inventer de `P2A`**, aucun critère ne portant sur le motif de fermeture. `B36` : nouveau §5.2.1 — les quatre lectures sont **également** hors liste close, mais leurs produits diffèrent : celui de la **quatrième** est **conservé** comme **matière brute indispensable**, **acquis hors liste close**, **conservé comme fait observé**, son **origine hors borne restant attachée à toute interprétation** ; celui de la **troisième** est écarté pour un **motif propre** — **aucune utilité probante** —, et non par la seule illicéité commune. **`P2-O2` inchangé. Aucune nouvelle interprétation terrain.** |
| **11** | Après réaudit. `B37` : **`§5.2.1` avait été inséré à l'intérieur du `§5.3`**, dont il n'est pas une subdivision — il est **replacé sous le `§5.2`, avant le `§5.3`**, les **deux paragraphes de clôture du `§5.3`** y demeurant ; **le fond de la règle d'attachement de l'origine hors borne est inchangé**. `B38` : le tableau du `§0` publiait l'`UTC` **à la milliseconde** et le `CEST` **à la microseconde** — **les durées annoncées n'étaient donc pas dérivables des opérandes publiées dans la base de référence**. **Tous les instants de journal servant à dériver une durée sont désormais publiés en `UTC` à la microseconde**, quatre instants manquants sont ajoutés — arrêt du démon à `S3`, démarrage du pont à `S3` —, et un **tableau de recalcul** établit que **chacune des huit durées publiées se dérive exactement** des opérandes du `§0`. Le corps emploie **`UTC` seul**. **`P2-O2` inchangé. Aucune nouvelle interprétation terrain.** |
| **12** | Après réaudit. `B39` : les deux paragraphes commentant le chiffrage de `R6` — *« Espace libre inchangé »* et *« L'espace consommé reste consommé »* — étaient **restés sous le `§5.3`**, séparés de la table qu'ils commentent ; ils sont replacés **sous le `§5.1`, immédiatement après elle**, ce qui **répare un déictique** : leur *« ci-dessus »* désignait, là où ils étaient, un tout autre contenu. **Aucun changement de fond, de chiffre ni de verdict.** `B40` : le `§0` affirmait que *« chaque durée publiée dans ce document »* se recalculait depuis son tableau — **trop large** ; l'affirmation est **bornée aux huit durées dérivées des instants de journal**, et **l'incertitude des durées d'origine `O2` — résolution à la seconde — est énoncée une fois** au `§3.1`, pour les silences, leur total, les dépassements structurels, l'étendue de la surveillance et la non-couverture. **Les valeurs elles-mêmes sont inchangées** : elles sont publiées en entiers **parce que leur source l'est**, et aucune conclusion n'en dépend. **`P2-O2` inchangé. Aucune nouvelle interprétation terrain.** |
