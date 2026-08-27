# `G.2` — sortie de preuve transport

> **Version 7**, clôture de l'étape 2. Deux corrections, aucune autre.
> **Aucun changement d'architecture.**
>
> | | Correction |
> |---|---|
> | **V7 · Q-1** | **§4.1.1 recense les QUATRE adaptations de portage**, sans ellipse. La V6 en déclarait trois et **passait sous silence la quatrième** : la **suppression** de la proposition finale *« et `OBS` §4.2 n'est **pas** amendé »* — §4.1.1 |
> | **V7 · Q-2** | **§8 remis dans l'ordre** : §8.1 puis §8.2. La V6 avait inséré §8.2 **avant** §8.1 |
>
> Corrections de la **Version 6**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **V6 · P-1** | **§5.2.1 réécrite au passé** : les cinq assertions **étaient** fausses sur la base `2ae39374`, elles **sont corrigées**. Titre, constats et clauses suivent. Idem pour le décompte du schéma — §5.2.1 |
> | **V6 · P-2** | **§5.2.1 scindée** : ce qui est **FAIT à l'étape 2** et ce qui **reste à FAIRE à l'étape 3** ne sont plus mêlés — §5.2.1 |
> | **V6 · P-3** | **Le nom de la seconde variable n'est plus exigé à l'étape 2.** Il n'est pas fixé ; son choix **et** son implémentation sont **réservés à l'étape 3** — §5.2.1 |
> | **V6 · P-4** | **§7 corrigé** : il n'affirme plus que la docstring dit 3/13, ni que cela relève de l'étape 3 — §7 |
> | **V6 · P-5** | **Note de portage sortie du bloc des six conditions**, et la formule « seule différence » **bornée** à la seule qualification de `§5.4` — §4.1 |
> | **V6 · P-6** | **Les autres adaptations de portage sont documentées séparément**, et **non** présentées comme identiques au texte validé — §4.1.1 |
> | **V6 · P-7** | **Nouvelle obligation d'étape 3** : mettre à jour `test_le_module_ne_lit_qu_une_variable_d_environnement`, que la seconde variable fera échouer — §8 |
>
> Corrections de la **Version 5**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **V5 · L-1** | **Labels rendus non ambigus.** `D-1` désignait **deux corrections différentes** — l'une en V3, l'autre en V4. Chaque label porte désormais **le numéro de sa version** : `V2 · B1`, `V3 · D-1`, `V4 · D-1`… Aucun label ne se répète plus d'une version à l'autre |
> | **V5 · L-2** | **Entrée historique `V3 · C-2b` corrigée** : elle annonçait *« trois assertions »*, chiffre que la **V4** a porté à **cinq**. L'entrée le dit désormais, sans réécrire ce que la V3 avait fait |
> | **V5 · L-3** | **Préambule du §4.2 corrigé.** Il attribuait à la **V3** le fait de « nommer chaque modification » — propriété **acquise seulement en V4**, qui a ajouté la catégorie `AJOUTÉ` et corrigé le compte de quatre à cinq |
>
> Corrections de la **Version 4**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **V4 · D-1** | **Cinq** assertions d'unicité de variable d'environnement, non trois. La V3 en avait manqué **deux** — `config.py:50` et `config.py:219`. Les cinq sont recensées **avec leurs numéros de ligne réels**, et l'étape 3 doit les mettre à jour **toutes** — §5.2.1 |
> | **V4 · D-2** | **Contradiction interne levée.** Le §7 annonçait encore *« trois tables, treize clés »* pendant que le §5.2.1 disait quatre et quatorze. **Le §7 est corrigé** — §7 |
> | **V4 · C-11** | **Compte de §4.2.3 corrigé** : **cinq** fragments modifiés, non quatre |
> | **V4 · C-12** | **Catégorie AJOUTÉ créée** pour *« Le puits écrit et oublie »*, qui ne figure dans aucune version de la clause d'origine — §4.2.2 |
> | **V4 · C-13** | **§8.1 corrigé sur un fait** : la fenêtre de `C3` ne « se consomme » pas, elle **se décale**. Son budget reste **entier** — §8.1 |
> | **V4 · C-14** | Colonne « Ligne » du §5.2.1 : **numéros réels**, non des étiquettes |
>
> Corrections de la **Version 3**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **V3 · D-1** | **§4.2 réécrite.** La V2 citait `OBS` §5.1 **avec ellipses** et rédigeait un remplacement où deux puces réellement modifiées étaient annoncées « inchangées ». La clause est désormais citée **intégralement**, le remplacement **conserve mot pour mot** toute phrase inchangée, et **chaque phrase modifiée est nommée comme telle** — §4.2 |
> | **V3 · C-2b** | Les assertions d'unicité de variable d'environnement dans `config.py` sont nommées une par une et portées à l'obligation de l'étape 3 — §5.2.1. **La V3 en comptait trois ; la V4 a établi qu'il y en a cinq** (`V4 · D-1`). L'entrée est conservée pour ce qu'elle a fait, non pour son chiffre |
> | **V3 · C-8** | **Décompte du schéma TOML corrigé** : **quatre tables, quatorze clés**. La docstring en annonce trois et treize — chiffre **déjà faux** avant ce lot, depuis l'ajout de `[transaction_surface]` — §5.2.1 |
> | **V3 · C-9** | **§5.4 nomme la campagne** à laquelle les trois captures se rapportent — §5.4 |
> | **V3 · C-10** | **Étape 3 : un sink LENT est éprouvé** en plus d'un sink qui lève, verdict et `ACK` inchangés dans les deux cas — §8.1 |
>
> Corrections de la **Version 2**, conservées sans retouche :
>
> | | Correction |
> |---|---|
> | **V2 · B1** | **Revendication retirée.** La V1 affirmait que `2 × 3 = 6` **prouve directement** le nombre d'écritures et rend `U-3` inutile. **C'est faux**, et contraire à la lecture exacte de `w4f-g2` §13 : les captures prouvent **les écritures capturées**, le journal du démon demeure **falsificateur** d'une écriture **non** capturée, et `U-3` reste ouverte — §6.1 |
> | **V2 · B2** | **Amendement de `OBS` §5.1 rendu frontal et complet**, chapeau compris. La V1 ne remplaçait qu'une puce et laissait le chapeau *« rendus à l'appelant immédiat, et à lui seul »* devenir faux **par implication**. Plus aucune modification implicite — §4.2 |
> | **V2 · C-1** | `Ack` porte aussi **`reason_class`** — §1 |
> | **V2 · C-2** | La docstring de `config.py` **devient fausse** avec une seconde variable d'environnement ; sa mise à jour est **obligation de l'étape 3** — §5.2.1 |
> | **V2 · C-3** | Réserve corrigée : l'I/O du sink est **hors du budget `write_timeout_s`**, qui borne le **sous-processus**, non l'appel — §10 |
> | **V2 · C-4** | Le trajet **`config.py` → `RuntimeConfig` → fermeture `fabriquer` → composition** est nommé — §5.2.2 |
> | **V2 · C-5** | Convention de noms courts corrigée : `w4f` était employé sans être déclaré |
> | **V2 · C-6** | **Collision de nom levée** : `G.2` désigne **l'acte**, `w4f-g2` le **document** |
> | **V2 · C-7** | La condition d'extinction est **déclarative** — dit comme tel, et adossé à une **preuve persistée vérifiable avant / après** — §5.4 |
>
> **Lecture des tables ci-dessus.** Elles consignent ce que **chaque version a
> fait, au moment où elle l'a fait**, et ne sont pas réécrites après coup —
> principe posé en `V5 · L-2`. Trois entrées — `V2 · C-2`, `V3 · C-2b`,
> `V4 · D-1` — rattachent les corrections de `config.py` à **l'étape 3** :
> c'était exact quand elles ont été écrites. **`V6 · P-1` les a déplacées à
> l'étape 2, où elles sont désormais exécutées.** L'état qui fait foi est celui
> du **§5.2.1**, non celui des tables d'historique.
>
> **Aucun code dans ce lot.** Il n'écrit rien, ne modifie aucun module, n'ouvre
> aucune capacité d'écriture, et **ne valide rétroactivement rien**.
>
> **Il amende deux clauses, frontalement** : `W4-A` §17 et `OBS` §5.1 — §4.

## Convention de citation

| Nom court | Désigne |
|---|---|
| **`G.2`** | **l'acte** — la campagne d'écriture bornée elle-même |
| **`w4f-g2`** | le **document** `w4f-g2-ecriture-bornee.md`, qui définit cet acte |
| `OBS` | `g2-observabilite-preuve.md` |
| `W4-A` | `w4a-vclient-write-adapter.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `W1` | `w1-mqtt-transaction-surface.md` |
| `w4f` | `w4f-write-sovereignty.md` |
| `C10` | `c10-user-interface.md` |

Une référence **sans nom court** désigne le présent document.

> **La collision que la V1 laissait passer** : elle employait `G.2` pour l'acte
> **et** pour le document, alors que deux fichiers portent désormais le préfixe
> `g2-`. Les deux sont maintenant distincts, et `w4f` — employé au §5.1 — est
> enfin déclaré.

---

## 1. Le constat, et ce qu'il ferme

`OBS` a rendu la signature brute d'une écriture **disponible à la frontière de
transport** : `WriteObservation` porte `args`, `stdout`, `stderr`, `returncode`
et `duration_s`, et `WriteResult.observation` la transporte.

**Personne ne la consomme.** Relevé dans l'arbre à `2ae39374`, non supposé :

| Point | Constat |
|---|---|
| `core/engine.py` reçoit le `WriteResult` | il lit **`.status`**, et rien d'autre |
| `observation` lu ailleurs dans `src/` | **nulle part** |
| journalisation dans `adapters/vclient_write.py` | **zéro** occurrence de `logging` ou `logger` |
| `Ack` | `request_id`, `status`, `reason`, **`reason_class`** — et rien de plus |

> **`OBS` §5.1 écrivait** : *« Sous `G.2`, cet appelant est **l'exploitant de la
> campagne**, qui la consigne dans son atelier. »* **C'est faux.** L'appelant est
> le **cœur**, dont le contrat lui interdit précisément d'en faire quoi que ce
> soit. Le présent lot corrige cette erreur d'analyse autant qu'il complète
> l'architecture.

**Conséquence** : `w4f-g2` §16 item 4 — ligne d'invocation réelle, `stdout` et
`stderr` intégraux, code retour, durée — demeure **inproduisible pour
l'exploitant**, et une campagne conduite en l'état resterait **non close** sur
le même item.

---

## 2. Les quatre voies, confrontées aux clauses

| Voie | Ce qu'elle heurte | Amendements |
|---|---|---|
| **A — journal dédié** | `W4-A` §17 n'admet `stdout`/`stderr` au journal que **bornés** · `OBS` §4.2 les interdit **intégraux** *« sous aucun niveau, dans aucun module, et quelle que soit la suite donnée à ce cadrage »* | **deux** |
| **B — fichier écrit par l'adaptateur** | `W4-A` §17 *« ni métrique, ni compteur, ni fichier »* · `OBS` §5.1 *« Aucun fichier »* · place une I/O dans un adaptateur que `W4-A` §14 veut **synchrone** | **deux** |
| **C — `EvidenceSink` injecté** | l'adaptateur ne crée rien ; le sink, lui, écrit | **deux**, mais **bornés** |
| **D — plus simple** | **aucune** : MQTT interdit d'emblée · écrire sur les flux du processus revient à **A**, l'unité les envoyant au journal · un point d'entrée de campagne serait une **capacité d'écriture nouvelle**, interdite | — |

> **Aucune voie ne mène à l'exploitant sans amender une clause.** C'est
> **structurel**, et non un défaut de conception : `W4-A` §17 et `OBS` §4.2
> verrouillent conjointement **toute** sortie d'octets bruts. Le verrou a été
> posé délibérément ; il est ici desserré délibérément, et sous bornes.

---

## 3. Voie retenue — **C**, et pourquoi

**`EvidenceSink` injecté**, pour trois raisons cumulatives :

1. **elle n'amende pas `OBS` §4.2.** Les octets bruts ne passent **jamais** par
   le journal. Les voies A et B l'exigeraient, avec un volume non borné diffusé
   vers toute destination de journal configurée ;
2. **elle laisse l'adaptateur pur.** Aucune I/O n'y entre : il appelle un
   collaborateur **injecté à la construction**, donc partie de sa configuration,
   ce que `W4-A` §14 permet — comme `OBS` **S-3** l'a établi en corrigeant une
   affirmation contraire de sa propre V2 ;
3. **elle est inerte par défaut**, au sens fort : sans sink, **aucun appel n'a
   lieu**.

> **Ce n'est pas un contournement, et le document refuse de le présenter ainsi.**
> Le sink écrit un fichier ; **Boilerack écrit donc un fichier**. La distinction
> « l'adaptateur ne crée rien » respecte la lettre de §17 mais **n'en épuise pas
> l'esprit**. C'est pourquoi le §4 amende §17 **frontalement**, plutôt que de
> s'abriter derrière l'injection.

---

## 4. Les deux amendements

### 4.1 Amendement de `W4-A` §17 — frontal et borné

**Clause en vigueur** :

> **Clause.** L'adaptateur **MAY** journaliser : le nom logique de la commande,
> la valeur transportée, le code retour, la durée observée et un extrait de
> diagnostic **borné**. Il **MUST NOT** journaliser un secret de configuration,
> et **MUST NOT** créer de système d'observabilité nouveau : ni métrique, ni
> compteur, ni fichier.

> **Amendement.** À la clause ci-dessus est ajouté, et **uniquement** :
>
> *« **Exception bornée — capture de preuve de campagne.** Un **puits de preuve**
> (`EvidenceSink`) **MAY** être injecté dans l'adaptateur d'écriture, et
> **MAY** déposer sur disque la signature brute d'une invocation d'écriture,
> aux conditions **cumulatives** suivantes :*
>
> *1. il est **opt-in** et **inerte par défaut** : à défaut d'injection, aucun
>    appel n'a lieu et aucun fichier n'existe ;*
> *2. il n'est actif que pour la **durée d'une campagne** au sens de `G.2` —
>    condition **déclarative**, adossée à la preuve du §5.4 ;*
> *3. son implémentation vit **hors de l'adaptateur** ;*
> *4. il ne crée **ni métrique, ni compteur** — l'interdiction demeure entière
>    sur ces deux-là ;*
> *5. il ne dépose **que** la signature d'une **écriture**, jamais d'une
>    lecture ;*
> *6. il **MUST NOT** influencer un verdict, ni lever dans le chemin
>    d'écriture. »*
>
> **Ce que l'amendement ne fait pas.** Il n'autorise **aucun** système
> d'observabilité **permanent** — c'est ce que §17 protégeait, et cela reste
> protégé. Il n'assouplit rien sur la journalisation : `stdout` et `stderr`
> demeurent **bornés au journal**, et `OBS` §4.2 n'est **pas** amendé.

#### 4.1.1 Les adaptations du portage, déclarées une par une

Le texte porté dans `W4-A` §17 **n'est pas mot pour mot** celui du §4.1.
**Quatre** adaptations ont été faites, et aucune n'est laissée implicite — la
V6 n'en déclarait que trois.

| # | Adaptation | Motif |
|---|---|---|
| **1** | *« adossée à la preuve du §5.4 »* devient *« adossée à la preuve du **§5.4 de `g2-sortie-preuve-transport.md`** »* | **la seule qui touche une condition.** « §5.4 » est **relatif au présent document** ; transplanté tel quel, il désignerait la §5.4 **de `W4-A`**. Sans cette qualification, la condition renverrait à la mauvaise section |
| **2** | une ligne de **provenance** est ajoutée en tête : *« Amendement porté par `g2-sortie-preuve-transport.md` §4.1 »* | **éditoriale.** Une clause amendée doit dire d'où vient son amendement ; elle n'existe pas dans le §4.1, qui est lui-même cette provenance |
| **3** | *« Ce que **l'amendement** ne fait pas »* devient *« Ce que **cette exception** ne fait pas »*, et *« c'est ce que **§17** protégeait »* devient *« c'est ce que **la clause ci-dessus** protégeait »* | **éditoriale.** Dans `W4-A`, « §17 » désignerait la section qui contient le texte, et « l'amendement » n'a plus de référent une fois porté |
| **4** | la proposition finale *« **, et `OBS` §4.2 n'est pas amendé** »* est **SUPPRIMÉE** du texte porté | **suppression**, et non reformulation — voir ci-dessous |

##### La quatrième adaptation est une suppression, et elle se déclare

La phrase du §4.1 se termine ainsi :

> *« […] `stdout` et `stderr` demeurent **bornés au journal**, et `OBS` §4.2
> n'est **pas** amendé. »*

Le texte porté dans `W4-A` s'arrête à *« bornés au journal. »* **La dernière
proposition a été retirée.**

> **Elle est éditorialement défendable.** `W4-A` ne gouverne pas `OBS` : y écrire
> qu'un autre document n'est pas amendé serait une affirmation **hors de son
> autorité**, et sa présence inviterait à croire que `W4-A` statue sur `OBS`.
>
> **Mais une suppression n'est pas une reformulation**, et la V6 l'a laissée
> passer en silence tout en affirmant n'avoir fait que trois adaptations. **Une
> proposition retirée doit être déclarée comme retirée** — c'est exactement la
> règle que le §4.2 applique à `OBS` §5.1, et elle vaut ici aussi.
>
> **Ce que la suppression ne change pas** : `OBS` §4.2 demeure **entière et sans
> exception**. Le fait subsiste ; seul son **énoncé dans `W4-A`** a disparu, et
> il reste écrit **ici**, au §4.1, ainsi qu'au §7.

> **Une seule adaptation touche le contenu normatif : la 1.** Elle ne change ni
> la condition, ni sa portée — elle en rend la référence **absolue** au lieu de
> relative. Les adaptations **2** et **3** relèvent de la **provenance** et de la
> **désignation**. L'adaptation **4** retire une proposition qui n'avait pas sa
> place hors de ce document, sans rien retirer au fait qu'elle énonce.
>
> **Les six conditions elles-mêmes sont identiques**, mot pour mot, une fois
> l'adaptation 1 appliquée — vérifié par comparaison automatique.

### 4.2 Amendement de `OBS` §5.1 — frontal, intégral, phrase par phrase

> **Deux versions se sont trompées ici, et il faut le dire.**
>
> La **V1** ne remplaçait qu'une puce, et laissait le chapeau devenir faux **par
> implication**. La **V2** a corrigé cela, mais a commis deux fautes de méthode :
> elle **citait la clause avec des ellipses** — `[…]` sur deux puces entières —
> et son remplacement annonçait « **Inchangée** » deux puces qu'elle
> **modifiait** en réalité.
>
> **Une clause ne se remplace pas sur une citation tronquée**, et **une phrase
> modifiée ne s'annonce pas comme inchangée.**
>
> **La V3 a rétabli la citation intégrale** et la conservation littérale. **Elle
> n'a pas achevé l'énumération** : son compte annonçait quatre fragments modifiés
> là où il y en a cinq, et elle n'avait pas de catégorie pour une phrase
> **ajoutée**. **C'est la V4 qui l'a complétée** — `V4 · C-11` et `V4 · C-12`.
> L'état ci-dessous est donc l'oeuvre des deux, et non de la seule V3.

#### 4.2.1 La clause en vigueur — citée **intégralement, sans ellipse**

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

#### 4.2.2 Ce qui est modifié, et ce qui ne l'est pas

| Fragment | Sort |
|---|---|
| **chapeau** — *« et à lui seul »* | **MODIFIÉ** — un second destinataire existe, sous condition |
| **Aucune rétention**, première phrase — *« Ni l'adaptateur, ni le cœur, ni la surface transactionnelle **MUST NOT** conserver […] »* | **MODIFIÉ** — le **puits** est ajouté à l'énumération |
| **Aucune rétention**, *« pas de champ d'instance, pas de liste, pas de cache, pas de dernier-résultat »* | **CONSERVÉ mot pour mot** |
| **Aucune rétention**, le fondement — *« `W4-A` §14 pose l'adaptateur « sans état au-delà de sa configuration », et une observation retenue serait de l'état »* | **CONSERVÉ mot pour mot** |
| **Aucune publication**, en entier | **CONSERVÉE mot pour mot**, y compris *« Les topics d'`ACK` gardent exactement le contenu que `W1` leur donne »* |
| **Aucun fichier** | **MODIFIÉ** — c'est l'objet de l'exception |
| ***Ce que « rendre » veut dire***, première phrase | **MODIFIÉ** — la valeur de retour n'est plus l'unique chemin |
| ***Ce que « rendre » veut dire***, dernière phrase — *« Sous `G.2`, cet appelant est l'exploitant de la campagne »* | **MODIFIÉ** — **erreur de fait** : l'appelant est le cœur |
| **Aucune rétention**, *« **Le puits écrit et oublie.** »* | **AJOUTÉ** — cette phrase ne figure dans **aucune** version de la clause d'origine. Elle étend l'interdiction de rétention au destinataire nouveau |

#### 4.2.3 La clause de remplacement

> **Amendement.** La clause **entière** du §4.2.1 est remplacée par :
>
> *« **Clause — ni rétention, ni publication.** Les octets bruts sont **rendus à
> l'appelant immédiat** et, **si et seulement si** un puits de preuve est injecté
> au titre de l'exception bornée de `W4-A` §17, **remis à ce puits**. À personne
> d'autre.*
>
> *- **Aucune rétention.** Ni l'adaptateur, ni le cœur, ni la surface
>   transactionnelle, **ni le puits**, **MUST NOT** conserver l'observation
>   au-delà de l'appel qui l'a produite : **pas de champ d'instance, pas de
>   liste, pas de cache, pas de dernier-résultat**. `W4-A` §14 pose l'adaptateur
>   « sans état au-delà de sa configuration », et une observation retenue serait
>   de l'état. **Le puits écrit et oublie.***
> *- **Aucune publication.** L'observation **MUST NOT** être publiée sur MQTT,
>   sous aucun topic, sous aucune forme, ni entière ni extraite. **Les topics
>   d'`ACK` gardent exactement le contenu que `W1` leur donne.***
> *- **Aucun fichier, hors l'exception bornée de `W4-A` §17.** Le lot
>   `g2-sortie-preuve-transport.md` y ouvre une exception **opt-in, inerte par
>   défaut**, portée par un `EvidenceSink` injecté. **Hors campagne,
>   l'interdiction demeure entière.***
>
> ***Ce que « rendre » veut dire, exactement*** : *l'observation voyage **dans la
> valeur de retour**, et le cas échéant **jusqu'au puits**. L'appelant en fait ce
> que son propre contrat lui permet, et elle disparaît avec elle. Sous `G.2`, cet
> appelant est **le cœur** — non l'exploitant, comme la rédaction d'origine le
> disait à tort — et son contrat lui interdit d'en rien faire. C'est le **puits**,
> et lui seul, qui la porte jusqu'à l'atelier de l'exploitant. »*

> **Portée de l'amendement.** Il touche **`OBS` §5.1, et rien d'autre**. **`OBS`
> §4.2 — aucune journalisation intégrale — demeure entière et sans exception.**
>
> **Le compte exact** — la V3 annonçait quatre modifiés, il y en a **cinq** :
>
> | | Nombre |
> |---|---:|
> | fragments **MODIFIÉS** | **5** |
> | fragments **CONSERVÉS mot pour mot** | **3** |
> | fragment **AJOUTÉ** | **1** |
> | fragments **supprimés** | **0** |

---

## 5. L'architecture

```
EvidenceSink (Protocol)      record(observation: WriteObservation) -> None

VClientCli.__init__(..., evidence: EvidenceSink | None = None)

write():   … obs construite …
           if self._evidence is not None:
               self._evidence.record(obs)      # jamais dans le chemin de decision
           return verdict                       # inchange
```

### 5.1 Les six clauses de l'usage

1. **Inerte par défaut.** `evidence is None` → **aucun appel**, aucun fichier,
   aucune branche prise. Le comportement de production est **identique** à
   celui d'aujourd'hui.
2. **L'adaptateur n'écrit rien.** `FileEvidenceSink` vit **hors de
   l'adaptateur**, dans son propre module, câblé à la composition.
3. **Échec sans effet sur le verdict.** Le sink **MUST NOT** lever dans le
   chemin d'écriture. Ses exceptions sont **interceptées** et journalisées
   **bornées** — ce que §17 autorise, `type(exc).__name__` et rien de plus.
   **L'absence de fichier vaut alors constat** : une preuve manquante se voit.
4. **Ni rétention, ni publication.** Le sink **écrit et oublie** : aucune liste,
   aucun cache, aucun dernier-résultat. Aucune publication MQTT, **jamais**.
5. **Le cœur ne le voit pas.** Aucun consommateur du sink dans `core/`. La
   clause de non-décision de `OBS` §5.1 demeure entière : le cœur **MUST NOT**
   fonder le moindre comportement sur cette observation.
6. **Écriture uniquement.** Le sink **MUST NOT** être câblé sur le chemin de
   **lecture**. `w4f-g2` §16 item 4 ne porte que sur l'écriture, et la surface de
   lecture émet environ **onze invocations par minute** (`w4f` §4.3) : l'y
   brancher inonderait l'atelier sans servir aucune preuve.

### 5.2 Opt-in — **variable d'environnement**, tranché

> **Décision.** L'opt-in est une **variable d'environnement**, **et non une clé
> TOML**.

Trois motifs : **précédent exact** — `config.py` est le seul module qui lit
l'environnement, pour `BOILERACK_MQTT_PASSWORD` · **zéro surface de configuration
ajoutée** au fichier déployé, que `EI-11` relit inchangé dans sa forme ·
**extinction plus simple** — une clé TOML persisterait et demanderait un acte de
retrait, donc une preuve de plus.

**Contrepartie assumée** : une variable d'environnement est **moins découvrable**
qu'une clé de configuration. C'est accepté — la découvrabilité n'est pas une
qualité recherchée pour un dispositif qui doit rester **inerte et exceptionnel**.

#### 5.2.1 La docstring de `config.py` — **corrigée à l'étape 2**

**Cinq assertions d'unicité étaient fausses**, ou le seraient devenues.
**La V3 n'en recensait que trois** et manquait les deux dernières, qui sont les
plus explicites de toutes. Les voici **toutes**, à leur **numéro de ligne** dans
`src/boilerack/config.py` **tel qu'il était sur la base `2ae39374`** :

| # | Ligne | Assertion |
|---|---:|---|
| **1** | **3** | *« Traduit **un** fichier TOML **et une** variable d'environnement en un `RuntimeConfig` »* |
| **2** | **8–9** | *« Le fichier porte **toute** la configuration durable ; l'environnement porte **le seul secret**, et rien d'autre. »* |
| **3** | **29** | *« Ce module lit un fichier **et une** variable d'environnement. »* |
| **4** | **50** | *« **Unique** variable d'environnement lue par Boilerack. »* |
| **5** | **219** | *« Lit **l'unique** variable d'environnement, une seule fois. »* |

> **Les deux que la V3 avait manquées étaient les plus frontales.** La 4
> qualifiait la constante `PASSWORD_ENV_VAR` d'**unique**, et la 5 le redisait
> dans la docstring de la fonction qui lit. Ce n'étaient pas des tournures de
> présentation : c'étaient des **affirmations d'unicité**, au plus près du code
> qu'elles décrivaient.
>
> **Une seconde variable les aurait rendues fausses.** Elle n'est ni un secret,
> ni de la configuration durable : c'est un **interrupteur de campagne**.
>
> **Les numéros de ligne valent pour la base `2ae39374`**, avant correction. Ils
> localisent ; ils ne se substituent pas à la lecture du module.

> **Le décompte du schéma fermé était faux lui aussi, et il l'était avant ce
> lot.** La docstring annonçait *« Trois tables, treize clés »* là où le module
> en déclare **quatre** — `mqtt`, `vclient`, `read_surface`,
> `transaction_surface` — et **quatorze** clés : **6 + 4 + 3 + 1**. L'écart
> datait de l'ajout de `[transaction_surface]` par W4-E ; **ce lot ne l'a pas
> créé, il l'a constaté puis corrigé**.

##### Ce qui est **FAIT**, à l'étape 2

Corrections **documentaires**, sans le moindre effet sur le comportement —
établi par comparaison des **AST, docstrings retirées** :

| | Fait |
|---|---|
| **1** | les **cinq** assertions ne portent plus d'affirmation d'**unicité permanente** |
| **2** | le module énonce l'état **courant** — *« À ce jour, une seule variable est lue : le SECRET MQTT »* — et le donne pour **non permanent** |
| **3** | la seconde variable est annoncée comme **contractée par le présent design, non encore implémentée** |
| **4** | la règle *« Boilerack ne balaie pas l'environnement »* est **conservée**, car elle demeure vraie |
| **5** | le décompte est porté à **quatre tables, quatorze clés**, avec le détail par table |

##### Ce qui **RESTE À FAIRE**, à l'étape 3

> **Clause.** L'étape 3 **MUST**, et l'étape 2 **MUST NOT** :
>
> 1. **fixer le nom** de la seconde variable d'environnement. **Ce nom n'est pas
>    arrêté**, et le présent document **ne le fixe pas** : le poser en docstring
>    avant qu'il n'existe reviendrait à documenter une chose absente ;
> 2. **l'implémenter** — sa lecture dans `config.py`, son transport dans
>    `RuntimeConfig`, son câblage jusqu'à la construction (§5.2.2) ;
> 3. **nommer cette variable dans les docstrings** une fois son nom fixé, en
>    remplacement de la mention générique posée à l'étape 2.
>
> **Pourquoi ce partage.** L'étape 2 pouvait retirer une affirmation devenue
> intenable et un chiffre faux : cela ne suppose aucun nom. Elle ne pouvait pas
> annoncer un identifiant qui n'existe pas.

#### 5.2.2 Le trajet, nommé de bout en bout

```
config.py            lit l'environnement, resout l'opt-in           <- seul lecteur
   |
RuntimeConfig        porte la valeur resolue                        <- donnee, pas lecture
   |
lifecycle.py         _composer_transaction(config)
   |                    |
   |                    fermeture  fabriquer(mqtt, clock)           <- deja existante
   |                        |
   +--------------------->  VClientCli(config.vclient, runner,
                               invocation=..., clock=clock,
                               evidence=<sink ou None>)
```

> **`lifecycle.py` ne lit jamais l'environnement**, et ne le lira pas : son garde
> `test_le_module_n_importe_ni_argparse_ni_os_environ` est
> `@pytest.mark.reference`, donc **gelé**. Il reçoit la valeur **déjà résolue**,
> et la fermeture `fabriquer` — qui reçoit déjà `mqtt` et `clock` — la transmet
> à la construction. **Aucun nouveau point de lecture n'est créé.**

### 5.3 Numérotation déterministe — tranchée

> **Décision.** Les captures sont numérotées par un **compteur monotone propre à
> la campagne**, commençant à `01`, incrémenté **à chaque invocation d'écriture
> déposée**, et **jamais** dérivé d'une horloge.

```
01-ecriture.out   01-ecriture.err   01-ecriture.meta
02-ecriture.out   02-ecriture.err   02-ecriture.meta
```

**Pourquoi pas l'horodatage** : `W4-C` §10 maintient une **réserve d'horloge**, et
`AB-7` sanctionne déjà une durée absurde. Un nom dérivé d'une horloge qui a bougé
produirait un ordre faux, ou une collision. Un compteur ne ment pas sur l'ordre.

**L'horodatage figure dans le `.meta`**, où il est une **donnée**, pas une clé.

> **Le compteur est un état** — le seul du sink, et il est **borné à la
> campagne**. Il ne contredit pas la clause de non-rétention, qui porte sur
> **l'observation**, non sur un rang.

### 5.4 L'extinction est **déclarative** — et sa preuve

> **Constat, dit sans détour.** La condition 2 du §4.1 — *« il n'est actif que
> pour la durée d'une campagne »* — **n'est garantie par aucun mécanisme**. Une
> variable d'environnement peut être posée dans une unité, un profil, un
> gestionnaire de services, et **y demeurer indéfiniment**. Rien dans le code ne
> l'expire.
>
> **C'est une clause de conduite, pas une propriété du système.** La V1 la
> présentait comme un fait ; elle est une **déclaration**.

> **Clause — l'extinction se prouve, elle ne se déclare pas seule.** **La
> campagne visée est celle-là même dont les trois captures encadrent le
> déroulement** : la campagne `G.2` instrumentée que l'étape 4 du §8 désigne, et
> aucune autre. « Avant » signifie **avant son temps 1**, « pendant » **entre son
> temps 8 et son temps 13**, « après » **une fois son temps 14 achevé**. Les
> captures appartiennent au dossier de **cette** campagne, et y sont numérotées
> avec les siennes.
>
> Elle **MUST** produire, et consigner dans son atelier, **trois** captures
> persistées de l'environnement du service :
>
> | Moment | Attendu | Ce qu'il prouve |
> |---|---|---|
> | **avant** la campagne | variable **absente** | l'état de repos est bien inerte |
> | **pendant**, unité démarrée | variable **présente** | l'opt-in est effectif, et daté |
> | **après** l'extinction | variable **absente** | la campagne a bien rendu le système à son état de repos |
>
> La capture porte sur l'**environnement effectif du processus** ou sur la
> déclaration de l'unité — le moyen relève de la procédure opératoire, la
> **persistance de la preuve** relève du présent contrat.
>
> **Sans les trois captures, l'extinction n'est pas établie**, et la campagne
> n'est pas close sur ce point.

Cette forme est celle de **`EI-11`**, qui prouve l'autorité **sur le contenu
persisté** et non sur l'état courant d'un processus. Le principe est le même :
**une propriété qu'aucun mécanisme ne garantit se prouve par constat, avant et
après.**

---

## 6. Démonstration — les cinq champs atteignent l'exploitant

Une invocation d'écriture **déposée** produit **trois fichiers**, à la forme de
`W4-C` §10 :

| Fichier | Contenu | Champ source |
|---|---|---|
| `<NN>-ecriture.out` | octets **bruts, intégraux** | `observation.stdout` |
| `<NN>-ecriture.err` | octets **bruts, intégraux**, **jamais fusionnés** | `observation.stderr` |
| `<NN>-ecriture.meta` | ligne d'invocation **verbatim** · code retour · durée · horodatage | `observation.args` · `.returncode` · `.duration_s` |

**Les cinq éléments de `w4f-g2` §16 item 4 sont couverts**, et dans la forme même
de la signature qu'a établie `W4-C` §16.3 :

```
stdout   [{"command":"setNiveauM1 2","value":0.000000,"raw":"OK","error":""}]
stderr   vide — 0 octet
rc       0
duree    1,045 s
```

### 6.1 Ce que le sink prouve, et ce qu'il ne prouve pas

> **La V1 était fautive ici, et c'est le blocage B1.** Elle écrivait que
> `2 × 3 = 6` devient *« une preuve directe du nombre d'écritures, opposable sans
> `U-3` »*. **Non.** Un décompte de captures ne prouve que **les captures**.

**La lecture exacte de `w4f-g2` §13**, reprise sans la déformer :

| | |
|---|---|
| ce que **les captures** prouvent | **les écritures capturées**, et elles seules — leur ligne réelle, leurs sorties, leur code retour, leur durée |
| ce que **le journal du démon** apporte | un **falsificateur** : *« une écriture non capturée, que le décompte des ouvertures du journal ferait apparaître **en excès** de ce que les captures expliquent »* |
| ce que le journal **ne** donne **pas** | l'**attribution par client** — « Il ne dit pas *qui* a ouvert une connexion — `U-3` reste ouverte — et il ne peut donc pas, à lui seul, prouver que `G.2` n'a écrit que deux fois. » |
| ce qu'un excès **déclenche** | **`FA-3`**, « non **d'un** décompte d'écritures » |

> **`U-3` demeure ouverte, et ce lot ne la réduit en rien.**

**Ce que le sink change réellement, et c'est déjà beaucoup** : il rend
**produisible** un artefact que `w4f-g2` §16 item 4 **exigeait déjà** et que nul
ne pouvait fournir. Il ne crée pas une preuve nouvelle — **il rend exécutable une
exigence existante**. Le bornage du §13 fonctionne exactement comme avant :
captures d'un côté, journal en falsificateur de l'autre.

### 6.2 Atelier hors dépôt

> **Clause.** Le répertoire du sink **MUST** être l'**atelier** de `EI-4` :
> créé pour la campagne, **hors de tout dépôt versionné**, et vérifié comme tel
> avant l'acte.

**Aucun secret n'y transite** : `VclientConfig` porte `executable`, `host`, `port`
et deux budgets — **aucun identifiant**. La ligne d'invocation déposée ne contient
donc ni mot de passe, ni jeton.

---

## 7. Ce qui ne change pas

| Objet | État |
|---|---|
| `TransportStatus` | **inchangé**, statut pour statut |
| table fermée de `W4-A` §9 | **inchangée** |
| sémantique des `ACK`, `reason` et `reason_class` compris | **inchangée** |
| absence de réessai — `W4-A` §13 | **inchangée** |
| budget `write_timeout_s` | **inchangé** — voir la réserve 3 |
| autorité `transaction_surface.enabled` | **inchangée** |
| confirmation par relecture — `C3` | **inchangée** |
| signature de `VClient.write` | **inchangée** |
| `WriteResult`, `WriteObservation` | **inchangés**, déjà intégrés |
| schéma fermé du TOML — **quatre tables, quatorze clés** | **inchangé** — ce lot n'ajoute **aucune** clé. Le décompte de la docstring, qui était faux avant ce lot, a été **corrigé à l'étape 2** (§5.2.1) |
| `OBS` §4.2 — aucune journalisation intégrale | **inchangée, non amendée** |
| `U-3` | **ouverte, inchangée** |
| index du corpus | **non touché** |

---

## 8. Chemin, ordonné

| # | Étape | Nature |
|---|---|---|
| **1** | **audit du présent design** | documentaire |
| **2** | **intégration des deux amendements** dans `W4-A` §17 et `OBS` §5.1, **et des corrections documentaires de `config.py`** (§5.2.1) | documentaire |
| **3** | **code** — nom et implémentation de la seconde variable (§5.2.1), `EvidenceSink`, `FileEvidenceSink`, câblage, tests dont ceux du §8.1 et celui du §8.2 | code, sous contrat |
| **4** | campagne `G.2` instrumentée — **sous une autorisation humaine nouvelle** | terrain |

> **L'étape 4 n'est ni ouverte, ni préparée, ni rendue plus proche.** La
> dérogation `G.2` s'est éteinte à l'achèvement de la campagne du 27 août 2026,
> et **aucune seconde campagne ne s'en autorise** — `w4f-g2` §3.

### 8.1 Deux sinks fautifs que l'étape 3 **MUST** éprouver

Un sink peut échouer de **deux** façons, et la seconde est la plus dangereuse
parce qu'elle ne lève rien.

| Cas | Ce qui est éprouvé | Attendu |
|---|---|---|
| **sink qui lève** | l'exception est **interceptée** et journalisée **bornée** | **verdict inchangé** · **`ACK` inchangé** · l'appel rend le même `WriteResult` qu'avec `evidence=None` · **absence de fichier**, qui vaut constat |
| **sink LENT** | le dépôt consomme du temps **hors** du budget `write_timeout_s` (§10, réserve 3) | **verdict inchangé** · **`ACK` inchangé** · **`duration_s` inchangée** — elle mesure la seule invocation, jamais le dépôt |

> **Pourquoi le sink lent compte autant que celui qui lève.** Un sink lent ne
> produit **aucun signal** : il ne lève pas, il n'échoue pas, il retarde.
>
> **Ce qu'il fait exactement, et la V3 le disait mal.** Le budget de confirmation
> est calculé **à l'entrée de la confirmation**, après le retour de `write()` :
> `deadline = clock.monotonic() + confirm_budget_s`. Un dépôt lent **décale donc
> le début de la fenêtre** de `C3` — **il n'en consomme rien**. Le budget reste
> **entier**, et la fenêtre garde toute sa durée ; elle commence simplement plus
> tard.
>
> **Le risque est donc un décalage, pas une amputation** : la confirmation
> observe la chaudière **après** un délai que rien ne mesure ni ne borne. Sur un
> datapoint que `w4f-g2` §6.1 déclare à **égalité stricte**, un décalage ne
> fausse aucun verdict — mais il éloigne l'observation du geste, et cela doit
> être su.
>
> Le test doit établir que **la lenteur du dépôt ne remonte ni dans le verdict,
> ni dans l'`ACK`, ni dans `duration_s`**.
>
> **Ces deux tests ne sont pas facultatifs.** Sans eux, la clause 3 du §5.1 —
> *« échec sans effet sur le verdict »* — resterait une intention.

### 8.2 Un test que la seconde variable fera échouer

> **Clause.** L'étape 3 **MUST** mettre à jour
> `test_le_module_ne_lit_qu_une_variable_d_environnement`, dans
> `tests/test_config_loader.py`.

Ce test assère aujourd'hui, sur le code de `config.py` **docstrings retirées** :

```python
assert code.count("os.environ") == 1
assert "os.environ.get(PASSWORD_ENV_VAR)" in code
```

**Une seconde lecture d'environnement le fera échouer sur la première
assertion.** Ce n'est pas un défaut du test : il **garde** exactement ce qu'il
doit garder — que Boilerack ne balaie pas l'environnement.

> **Ce que la mise à jour doit préserver, et qui est l'essentiel.** Le compte
> passe de **1** à **2**, et **rien d'autre ne se relâche** : les interdits
> `dotenv`, `environ.items`, `environ.keys`, `environ.copy` demeurent, et la
> lecture du secret reste vérifiée nommément. Un test qui se contenterait de
> retirer l'assertion de compte **perdrait sa raison d'être**.

> **Corollaire.** Tant que l'étape 3 n'a pas eu lieu, ce test **passe** et doit
> passer : la seconde variable n'existe pas encore.
---

## 9. Ce que ce document ne fait pas

Il n'écrit aucun code · il ne modifie aucun module · il n'ouvre aucune capacité
d'écriture · il ne valide rétroactivement aucune campagne · il ne rouvre pas
`W4-F2` · il n'ouvre pas `W4-F3` · il n'amende ni `w4f-g2`, ni `W4-C`, ni `OBS`
§4.2 · il ne réduit pas `U-3` · il ne touche pas à l'index du corpus · il
n'autorise aucun terrain.

---

## 10. Réserves

1. **L'amendement de `W4-A` §17 est réel et frontal.** Il desserre une
   interdiction posée délibérément. Un auditeur peut juger que l'exception,
   fût-elle bornée, ouvre une brèche que la prochaine campagne élargira. Le
   §4.1 la borne par **six conditions cumulatives** ; elles valent ce que vaut
   leur respect.
2. **Le volume reste NON BORNÉ, et c'est conservé comme tel.** Aucune borne
   n'est posée sur la taille des octets déposés. Une écriture au `stdout`
   volumineux remplirait l'atelier. C'est **assumé** : borner tronquerait la
   preuve, et une preuve tronquée ne prouve plus l'intégralité que `w4f-g2` §16
   item 4 exige. La réserve se déplace du `WriteResult` vers le **disque de
   l'atelier**, elle ne disparaît pas.
3. **L'I/O du sink est HORS du budget `write_timeout_s`** — correction de la V1,
   qui affirmait le contraire. Ce budget est passé à `runner.run(timeout=…)` : il
   borne le **sous-processus**, jamais l'appel `write()`. Le dépôt a lieu **après**
   le retour du sous-processus, donc **hors budget**. Il allonge l'appel d'une
   durée **non bornée par aucun contrat**, et cela ne se voit **pas** dans
   `duration_s`, mesurée autour de la seule invocation. Une écriture lente à
   déposer retarderait la relecture de confirmation sans qu'aucun compteur ne le
   dise.
4. **L'extinction est déclarative** (§5.4). Les trois captures la **constatent** ;
   elles ne l'**imposent** pas. Un exploitant qui laisserait la variable en place
   produirait une capture « après » fausse ou absente — et la campagne ne serait
   pas close.
5. **`OBS` §5.1 comportait une erreur d'analyse** — l'exploitant présenté comme
   appelant de `write()`. Le §4.2 la corrige **frontalement**, chapeau compris.
6. **Rien n'est rétroactif.** La campagne du 27 août 2026 demeure une preuve
   **physique solide** et une campagne **non close**.
