# Instruction `vito.xml` — résolution statique des treize commandes

> **Version 3**, après réaudit. Une correction : la cellule `H6` **(a)** du §13
> ne portait qu'un seul terme, là où le §10 en avait établi **deux**. La scission
> y est propagée. **Rien d'autre ne change.**
>
> **Version 2**, après audit. Trois corrections : l'attribution des faits terrain
> — `getTempKist` / `20CB` / `P300` reviennent à
> `w4-arbitrage-activation-debug.md`, non à Acte A — ; l'acquis, déjà établi, que
> le `vcontrold.xml` déployé **diffère** de l'amont, ce qui retire toute portée à
> une comparaison d'empreinte sur ce fichier ; et le périmètre de l'acte suivant,
> resserré en conséquence. Le lot cesse en outre de prétendre que cet acte
> fermerait `H6` **(a)** intégralement. **Régime, résidu du régime, `H3`, `H1`,
> `H2`, `U-2` et `U-7` sont inchangés.**
>
> **Version 1.** Lot documentaire `W4-F2`. Il exécute **l'acte suivant établi par
> `w4f2-a5-extraction.md` §15** : instruire l'amont `vito.xml` et y confronter les
> treize commandes closes par `A5`. Aucun accès hôte, aucun terrain, aucun
> runtime, aucune mutation, aucun `vclient`, aucun `debug`, aucune chaudière.

---

## 1. Objet et frontières

Ce document **lit** l'amont `vito.xml` du commit déjà caractérisé, **établit la
règle de résolution** commande ↔ périphérique dans le code amont, **confronte**
les treize commandes au périphérique `20CB`, et **mesure** l'effet sur `H6` **(a)**
et **(c)** ainsi que sur le résidu du régime.

Il **n'infère rien** sur `H3`, `H1`, `H2`, `U-2` ni `U-7` — le §12 dit pourquoi,
hypothèse par hypothèse. Il n'amende aucun contrat, ne rouvre aucun arbitrage
clos, n'ouvre ni `Acte B`, ni `T0` / `T1` / `T2`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.**

---

## 2. Sources lues, avec leurs empreintes

Toutes proviennent de `openv/vcontrold` au commit **déjà caractérisé**
`8ca47972c9ac5b0a14a7a36393b0dbfdb165f918`, dépôt public. Chaque fichier a été
récupéré par l'API du dépôt, et **l'empreinte de blob calculée localement a été
comparée à celle que l'API déclare** — condition d'acceptation de la lecture.

| Fichier | Taille | Blob calculé = blob déclaré |
|---|---|---|
| `xml/300/vito.xml` | 56 083 o · 1 752 l | `9d8c11c87575b6540e89dbc0065ee99122db8bbe` — **concordant** ; SHA-256 `34808e1f08256ce15e7f81b6b27623866a596de562e6f7232198fa0b41b22f89` |
| `xml/300/vcontrold.xml` | 17 123 o | `173d88abda02730e90eefce93c949eeb7fddbe11` — **concordant** |
| `src/xmlconfig.c` | 48 122 o | `2aeaac07524815743acf78a2bdadc8b32b747a77` — **concordant** |
| `src/vcontrold.c` | 34 459 o | `d2adee6d9fea60aba6aa32dec563e32fa44217e7` — **concordant** |

> **`src/vcontrold.c` est l'un des six blobs qu'Acte A a comparés sur l'hôte**, et
> qu'il a trouvés **identiques à l'amont**. Le fichier lu ici est donc, pour ce
> seul fichier, celui de l'installation. **Ce n'est pas le cas de `vito.xml`** —
> §9 en fait la réserve capitale de ce lot.

Ces fichiers ont été lus dans un espace de travail hors dépôt. **Aucun n'est
versionné ici** : ce document en reprend des faits, pas du contenu.

---

## 3. Méthode

Trois opérations, dans cet ordre.

1. **Établir la règle de résolution** dans le code amont — `src/xmlconfig.c` pour
   la construction de la table par périphérique, `src/vcontrold.c` pour le test
   effectif à l'invocation. **Sans cette règle, lire le XML ne prouve rien** : la
   présence d'un nom de commande dans un fichier ne dit pas qu'il résout.
2. **Appliquer cette règle** aux treize commandes, pour le périphérique `20CB`.
3. **Confronter** le résultat aux faits terrain déjà acquis, sans en produire de
   nouveaux.

> **Le dépouillement du XML a été fait par un lecteur XML, non par motif
> textuel** — la structure comporte des surcharges imbriquées qu'un `grep` lit
> mal. Ce lecteur **transcrit la règle du code C** établie au §5 ; il n'en est pas
> une autorité indépendante, et ne vaut que dans l'exacte mesure où cette
> transcription est fidèle. Les deux branches de la règle sont vérifiées
> séparément au §5.

---

## 4. Le périphérique `20CB` dans l'amont

`vito.xml` déclare quatre périphériques :

| ID | Nom | Protocole |
|---|---|---|
| `2098` | `V200KW2` | `KW2` |
| `2053` | `GWG_VBEM` | `GWG` |
| **`20CB`** | **`VScotHO1`** | **`P300`** |
| `2094` | `V200KW1` | `KW2` |

`20CB` est donc **défini dans l'amont**, et son protocole y est **`P300`**.

> **Attribution, corrigée en V2.** Sur l'installation, l'identifiant de
> périphérique **`20CB`** a été relevé par **Acte A** §8, dans sa lecture de la
> configuration chargée. En revanche le **protocole `P300`**, comme la résolution
> de `getTempKist` et ses attributs, proviennent de
> **`w4-arbitrage-activation-debug.md`** — *« Fait acquis qui fonde
> l'arbitrage »* — et **non d'Acte A**, dont le §12.3 dit expressément que la
> transition 4 fut **« non rapportée »** et qualifie cette omission de *« lacune
> de la campagne »*.

Le fichier définit **209 commandes**, dont **25 portent une surcharge explicite
pour `20CB`**.

---

## 5. La règle de résolution, établie dans le code amont

Elle a **deux branches**, et il faut les tenir ensemble.

### 5.1 Construction — le défaut est copié à tous les périphériques

`src/xmlconfig.c`, après l'analyse du document, lignes 1428-1452 :

> *« For all commands that have default definitions, we roam all devices and add
> the particular commands. »* — puis, pour chaque périphérique ne possédant pas
> déjà un nœud de ce nom : `logIT(LOG_INFO, "Copying command %s to device %s", …)`
> et recopie de `name`, `pcmd`, `addr`, `unit`, `bit`, `errStr`, `precmd`,
> `description`, `len`.

Et lorsqu'une commande porte un bloc `<device ID="…">`, `parseCommand` (lignes
904 et suivantes) construit un nœud **propre à ce périphérique** et l'attache à
sa liste — la garde `if (! getCommandNode(dPtr->cmdPtr, cPtr->name))` de la boucle
de recopie fait alors que **la surcharge l'emporte sur le défaut**.

**Conséquence, littérale :** une commande définie au niveau supérieur de
`<commands>` est présente pour **tous** les périphériques ; un bloc
`<device ID="20CB">` **remplace** cette définition pour `20CB` seul.

### 5.2 Invocation — la présence ne suffit pas, il faut une adresse

`src/vcontrold.c` ligne 352 :

```
} else if ((cPtr = getCommandNode(cfgPtr->devPtr->cmdPtr, cmd)) && (cPtr->addr)) {
```

La recherche porte sur `cfgPtr->devPtr->cmdPtr` — **la liste du périphérique
configuré**, non une liste globale — et la condition est **double** : le nœud
doit exister **et** porter une adresse. À défaut, l'exécution ne prend pas cette
branche.

> **Le XML dispose d'un moyen de retirer une commande à un périphérique**, et il
> s'en sert : `setNiveauM1` et `setNeigungM1` portent l'élément **vide**
> `<device ID="2053"/>`. Le nœud est alors créé pour `2053` sans adresse, et la
> garde `&& (cPtr->addr)` le rejette. C'est le mécanisme de non-résolution, **lu
> dans le fichier même**, et non supposé.

**Le critère de résolution statique retenu dans ce lot est donc exactement
celui-là** : pour `20CB`, un nœud de ce nom existe **et** porte une adresse
effective.

---

## 6. Les treize commandes confrontées à `20CB`

| Commande | `protocmd` | `addr` | `len` | `unit` | Origine de la définition pour `20CB` |
|---|---|---|---|---|---|
| `getTempA` | `getaddr` | `0800` | 2 | `UT` | défaut, recopié à tous les périphériques |
| `getTempKist` | `getaddr` | `0802` | 2 | `UT` | défaut, recopié à tous les périphériques |
| `getTempWWist` | `getaddr` | `0804` | 2 | `UT` | défaut, recopié à tous les périphériques |
| `getTempWWsoll` | `getaddr` | `6300` | 1 | `UTI` | défaut, recopié à tous les périphériques |
| `getTempRaumNorSollM1` | `getaddr` | `2306` | 1 | `UTI` | défaut, recopié à tous les périphériques |
| `getTempRaumRedSollM1` | `getaddr` | `2307` | 1 | `UTI` | défaut, recopié à tous les périphériques |
| `getNeigungM1` | `getaddr` | `27D3` | 1 | `UN` | **surcharge `<device ID="20CB">`** |
| `getNiveauM1` | `getaddr` | `27D4` | 1 | `ST` | **surcharge `<device ID="20CB">`** |
| `getBrennerStatus` | `getaddr` | `55D3` | 1 | `PR1` | **surcharge `<device ID="20CB">`** |
| `setTempWWsoll` | `setaddr` | `6300` | 1 | `UTI` | défaut, recopié à tous les périphériques |
| `setTempRaumNorSollM1` | `setaddr` | `2306` | 1 | `UTI` | défaut, recopié à tous les périphériques |
| `setNiveauM1` | `setaddr` | `27D4` | 1 | `ST` | **surcharge `<device ID="20CB">`** |
| `setNeigungM1` | `setaddr` | `27D3` | 1 | `UN` | **surcharge `<device ID="20CB">`** |

**Aucun élément `<device ID="20CB"/>` vide n'existe dans le fichier** — zéro
occurrence, sur les 209 commandes. Le mécanisme de retrait du §5.2 n'est employé
pour `20CB` **nulle part**.

---

## 7. Verdict de résolution statique

> **Les treize commandes résolvent pour `20CB` sur l'amont
> `8ca47972…` — toutes les treize, sans exception.**

Huit par recopie du défaut, cinq par surcharge explicite. Chacune porte une
adresse effective non vide, ce qui satisfait **les deux branches** du critère du
§5.

Il faut nommer ce qui est établi avec exactitude : **c'est un fait sur un fichier
amont, pas sur une installation**. Le §9 en tire la conséquence.

---

## 8. Trois concordances avec le terrain déjà acquis

Elles ne produisent aucun fait nouveau sur l'installation ; elles rapprochent des
faits déjà consignés.

1. **`getTempKist` — définition effective identique.**
   **`w4-arbitrage-activation-debug.md`** porte le fait terrain, issu d'une
   observation en lecture seule explicitement autorisée : *« `getTempKist` résout
   pour `20CB` — `addr 0802`, `len 2`, `unit UT`, `protocmd getaddr`, protocole
   `P300` »*. L'amont donne, pour `20CB` : `addr 0802`, `len 2`, `unit UT`,
   `protocmd getaddr`, périphérique `20CB` en `P300`. **Les cinq attributs
   coïncident.**
2. **Le périphérique et son protocole.** L'identifiant **`20CB`** est relevé par
   **Acte A** §8 ; le protocole **`P300`** l'est par
   **`w4-arbitrage-activation-debug.md`**. L'un et l'autre sont déclarés à
   l'identique dans l'amont — où `xml/300/vcontrold.xml` désigne d'ailleurs
   **`<device ID="20CB"/>`** comme périphérique par défaut.
3. **La structure d'inclusion.** `w4-arbitrage-activation-debug.md` avait établi
   sur l'hôte que la configuration chargée inclut `vito.xml` par **XInclude**.
   L'amont `xml/300/vcontrold.xml` porte littéralement, ligne 449 :
   `<xi:include href="vito.xml" parse="xml"/>`. **La forme d'assemblage observée
   est celle de l'amont.**

> **Ces trois concordances sont des points d'intégrité, pas une preuve
> d'intégrité.** Elles portent sur **une commande sur treize**, sur une
> déclaration de périphérique et sur une directive d'inclusion. Elles rendent la
> divergence moins vraisemblable ; elles ne l'excluent pas.

---

## 9. La réserve capitale — l'amont n'est pas le déployé

> **`vito.xml` n'a jamais été comparé entre l'installation et l'amont.**

Acte A a comparé **six blobs**, et il faut les nommer : `src/vcontrold.c`,
`src/socket.c`, `src/semaphore.c`, `src/common.c`, `src/io.c`, `src/framer.c`.
**Six fichiers source. Aucun fichier XML.** Le fichier de commandes déployé —
inclus par la configuration chargée — **n'est couvert par aucune comparaison
d'intégrité**.

Trois écarts se posent, et leurs statuts diffèrent — l'un est établi, un autre
est écarté, le troisième demeure ouvert :

| Écart | Statut |
|---|---|
| le `vito.xml` déployé diffère de l'amont `8ca47972…` | **non écarté** — aucune comparaison n'a été faite |
| le `vcontrold.xml` déployé diffère de l'amont | **ÉTABLI — il diffère** (voir ci-dessous) |
| le périphérique configuré sur l'installation n'est pas `20CB` | **écarté** — Acte A §8 l'a relevé en lecture directe |

> **La divergence de `vcontrold.xml` n'est pas une conjecture : elle est acquise,
> et il faut en tirer la conséquence.** Acte A §8 a relevé sur l'installation le
> périphérique série effectif et le chemin du fichier de journal ; l'amont
> `xml/300/vcontrold.xml` porte, pour ces deux éléments, des valeurs **autres** —
> un périphérique série différent et un chemin de journal relatif. **Le fichier
> déployé n'est donc pas l'amont**, et ce n'est pas un défaut : c'est un fichier
> de configuration, fait pour porter des valeurs d'installation.
>
> **Conséquence directe, et la V1 s'y trompait.** Proposer une **comparaison
> d'empreinte** sur `vcontrold.xml` serait proposer un contrôle dont on connaît
> déjà le résultat — il échouerait, sans rien apprendre. Ce qui est requis de ce
> fichier n'est pas son identité, mais **deux éléments précis** : quel fichier de
> commandes il inclut, et quel périphérique il désigne. Le §15 s'y tient.

**Ce que ce lot établit se lit donc ainsi**, et pas autrement : *si* le fichier de
commandes déployé est celui de l'amont caractérisé, *alors* les treize commandes
résolvent. La prémisse est **une comparaison d'intégrité, non faite**.

---

## 10. Effet sur `H6` **(a)**

Le résidu **(a)** — *« les commandes émises par le pont résolvent-elles
toutes ? »* — avait été scindé par `w4f2-a5-extraction.md` §9 en deux parts.

| Part | Avant ce lot | Après ce lot |
|---|---|---|
| **énumération** | close au niveau du contrat `A5` v0.4.3 | **inchangée** — ce lot n'y touche pas |
| **résolution** | couverte pour les treize, par des éléments de **force inégale** — preuve directe pour deux commandes, preuve d'usage pour quatre, corroboration répétée pour sept | **établie sur l'amont pour les treize, uniformément, par lecture du fichier et de la règle** — et **subordonnée**, pour l'installation, à une comparaison d'intégrité non faite |

> **Le gain est réel et il est d'une autre nature que les précédents.** Jusqu'ici,
> la résolution reposait sur des **corroborations de comportement** — la
> publication n'a lieu qu'en cas de succès, l'écriture est éprouvée par des mois
> d'usage. Elle repose désormais sur une **lecture de la définition et de la règle
> qui la consomme**. C'est un déplacement du comportemental vers le structurel.

> **Et la borne est tout aussi réelle.** Ce déplacement s'accompagne d'une
> **prémisse nouvelle** — l'identité du fichier déployé — qui n'existait pas dans
> les corroborations de comportement, lesquelles portaient, elles, sur
> l'installation réelle. **Les deux ordres de preuve ne se remplacent pas : ils
> se complètent.** Les corroborations antérieures **subsistent intégralement**, et
> ce lot ne les retire pas.

**Résidu de (a) après ce lot, énoncé exactement.** Il comporte **deux termes**, et
les confondre serait promettre une clôture qui n'aura pas lieu :

| Terme | Ce qu'il exige |
|---|---|
| **résolution sur l'installation** | une **comparaison d'intégrité** entre le `vito.xml` déployé et l'amont `8ca47972…`, plus la vérification que la configuration chargée inclut bien **ce** fichier. Acte de **lecture sur l'hôte**, de la nature de ce qu'Acte A a pratiqué sur six blobs source |
| **conformité du pont déployé au contrat `A5`** | **ouverte, et ce lot ne l'approche pas.** L'énumération des treize commandes est close **au niveau du contrat `A5` v0.4.3** ; que le pont **effectivement déployé** n'émette que celles-là n'est **pas établi** — `w4f2-a5-extraction.md` §2 et §10 le disaient déjà, et rien ici ne le change |

> **Aucun acte proposé par ce lot ne fermerait donc `H6` (a) intégralement.** Le
> premier terme est à portée d'une lecture bornée ; le second demanderait une
> autorité sur le pont déployé que le corpus n'a pas.

---

## 11. Effet sur `H6` **(c)**

Le résidu **(c)** — *« une session de la population protégée peut-elle se
terminer sans avoir acquis le périphérique ? »* — comportait le cas **« commande
non résolue »**.

| État | Avant ce lot | Après ce lot |
|---|---|---|
| cas « commande non résolue » | traité pour tout le jeu attribué au pont par le contrat, sur des corroborations de comportement | **écarté sur l'amont** : les treize résolvent, et le mécanisme de retrait existe mais n'est employé pour `20CB` nulle part — **sous la même réserve d'intégrité** |
| autres chemins de sortie précoce | ouverts | **inchangés** — échec d'écriture vers le client, expiration, fin de boucle avant acquisition |

**Statut de `H6` : `PARTIEL`, inchangé.** Le constat `RÉDUITE, NON CLOSE` demeure
exact, et pour la même raison qu'avant : **(b)** est absorbé par `H2`, que rien
ici ne touche.

---

## 12. Ce sur quoi ce lot n'infère rien

Cinq objets sont **explicitement hors de portée**, et il faut dire pourquoi
plutôt que de se contenter de les écarter.

| Objet | Pourquoi ce lot ne dit rien |
|---|---|
| **`H3`** | les transitions **1** et **2** sont des faits d'**exécution du superviseur**. Un fichier de définitions ne dit pas qu'une machine exécute. **Aucun mouvement.** |
| **`H1`** | porte sur le lien **binaire ↔ arbre au moment de la compilation**. `vito.xml` n'est **pas compilé** : c'est une donnée lue à l'exécution. Le lot ne l'effleure pas |
| **`H2`** | porte sur l'existence d'un **autre ouvreur de la liaison**. Rien dans un fichier de commandes n'en parle. **Aucun mouvement**, et donc aucun sur `H6` **(b)** |
| **`U-2`** | `borne_sonde` reste **non calculable** ; ce lot ne mesure aucune durée et n'en déduit aucune |
| **`U-7`** | `occupation_max` n'est pas approché ; `seuil_C1` demeure **non calculable** |

> **Une inférence serait tentante et il faut la nommer pour l'écarter.** De ce que
> les treize commandes résolvent, on serait tenté de conclure que la sonde du
> superviseur résout. **Non.** Aucune source n'attribue de commande à la sonde du
> superviseur — c'est le constat de `w4f2-a5-extraction.md` §11, et il tient. Les
> treize commandes sont celles **du pont**.

---

## 13. Résidu du régime, recalculé

| Résidu | Nature | Mouvement dû à ce lot |
|---|---|---|
| **maillon 2 non prouvé** — transitions **1** et **2** | faits d'exécution du superviseur | **aucun** |
| **maillons 3, 4, 6 conditionnels à `H1`, `H2`, `H6`** | hypothèses d'installation | **aucun** — `H6` est réduit, non déchargé |
| **maillon 5 conditionnel à `H1`** | idem | **aucun** |
| `H1` | lien binaire ↔ arbre ; traces non instruites | **aucun** |
| `H2` | invariant sur la fenêtre protégée ; voies structurelles non instruites | **aucun** |
| `H6` **(a)**, terme **1** — résolution sur l'installation | commandes du pont | résolution **établie sur l'amont pour les treize** ; terme réduit à une **comparaison d'intégrité** (§10, §15) |
| `H6` **(a)**, terme **2** — conformité du pont déployé au contrat `A5` | énumération close **au niveau du contrat `A5` v0.4.3** | **aucun — le terme reste ouvert.** Ce lot ne l'approche pas, et l'acte du §15 ne le fermerait pas |
| `H6` **(b)** | `= H2` | **aucun** |
| `H6` **(c)** | chemins de sortie précoce | cas « non résolue » **écarté sur l'amont** ; autres chemins **aucun** |

> **Le résidu du régime est identique à celui de la veille.** Le mouvement est,
> une fois encore, **interne à `H6`** — et `H6` reste `PARTIEL`. Le maillon 2,
> seul maillon manquant, n'est pas touché, et **aucun acte documentaire ne le
> touchera** : c'est un fait d'exécution.

---

## 14. Régime — `INDÉTERMINÉ`, inchangé

| | |
|---|---|
| Niveau épistémique | `PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION` — valeur `ADDITIF — CONDITIONNEL À H1/H2/H3/H6` |
| **Régime opératoire** | **`INDÉTERMINÉ`** → branche **C** → **`W4-F2 NON QUALIFIABLE — STOP`** |

`ADDITIF` exige la preuve explicite de **chacun** des six maillons — *« un seul
manquant donne `INDÉTERMINÉ` »*. Le maillon 2 manque. `NON ADDITIF` exige une
**preuve positive sur la population protégée** ; ce lot n'en apporte aucune.

**Aucune conclusion par défaut n'est émise.**

---

## 15. Le plus petit acte suivant

> **Le niveau 2 est désormais épuisé pour ce qui concerne le jeu de commandes.**
> `A5` a été extraite, l'amont `vito.xml` a été lu. Il reste `A6`, **privé**, dont
> `w4c` §3 n'autorise à reprendre que des **faits de comportement, jamais du
> code** — et qui porte sur la **forme d'invocation**, non sur la résolution.

L'acte suivant est donc, pour la première fois depuis l'ouverture de `W4-F2`, un
acte **sur l'hôte**.

| | |
|---|---|
| **acte, en deux lectures et rien de plus** | **(i)** relever l'**empreinte du `vito.xml` déployé** et la comparer à l'amont `8ca47972…` ; **(ii)** faire une **lecture ciblée du `vcontrold.xml` déployé**, bornée à son élément **`<xi:include>`** — quel fichier de commandes est inclus, et depuis quel emplacement — et à l'élément de **périphérique par défaut**. **Rien d'autre de ce fichier n'est requis** |
| **régime** | un acte **`G.1`**, borné à ces deux lectures : ni journal, ni descripteurs, ni processus, ni exécution |
| **pourquoi pas d'empreinte sur `vcontrold.xml`** | parce qu'il **diffère déjà** de l'amont, et qu'on le sait (§9). Une empreinte y serait un contrôle dont le résultat est connu d'avance |
| **ce qu'il fermerait** | le **premier terme** du résidu **(a)** — la résolution sur l'installation — et le cas « commande non résolue » de **(c)**, en levant la prémisse du §9 |
| **ce qu'il ne fermerait pas** | le **second terme** de **(a)**, la **conformité du pont déployé au contrat `A5`**, qui reste **ouverte** · transitions **1** et **2** · `H1` · `H2` · `H6` **(b)** et les autres chemins de **(c)** |
| **autorisation** | **non donnée, et non demandée ici.** Ce document propose ; il n'autorise pas |
| **précédent de méthode** | Acte A a pratiqué la comparaison d'empreinte sur six blobs source, en lecture seule explicitement autorisée |

> **Cet acte ne ferme pas `H6` (a).** Il en ferme **un terme sur deux**. Le dire
> autrement — comme le faisait la V1 — promettrait une clôture que la
> conformité non établie du pont déployé au contrat `A5` interdit.

**Et le maillon 2 ne sera pas fermé par là.** Les transitions 1 et 2 exigent une
preuve d'**exécution**, que ni une empreinte ni un fichier ne produisent.

---

## 16. Constats collatéraux, relevés et non consommés

Deux faits sortent du périmètre. Ils sont consignés **sans être exploités**, et
**n'amendent aucun contrat**.

1. **Unité de `getBrennerStatus` pour `20CB`.** L'amont donne `unit PR1`, et
   `xml/300/vcontrold.xml` définit `PR1` comme *« Prozent 1 Byte ganzzahlig »* :
   `type uchar`, `entity %`, `calc get="V"`. Cela converge avec l'exemple `"75%"`
   de `A5` §3.4. `c7` §4.3 motif 2 tenait le type et l'unité pour *« non établis
   par le dépôt public »* — au sens du **dépôt Boilerack**. Une source publique
   amont les porte. **Ce lot ne rouvre pas le report hors v1** : les motifs 1, 3,
   4 et 5 de `c7` §4.3 demeurent intacts. **Et la réserve y est ici plus forte
   qu'ailleurs** : `PR1` est défini dans `vcontrold.xml`, **dont le §9 établit que
   l'exemplaire déployé diffère de l'amont**. Que la définition déployée de `PR1`
   soit celle de l'amont n'est donc **pas établi**, et l'acte du §15 ne le
   vérifierait pas — il ne lit de ce fichier que l'inclusion et le
   périphérique.
2. **Héritage de `len` dans une surcharge.** `parseCommand` recopie explicitement
   `unit` et `pcmd` du parent lorsque la surcharge les omet ; le sort de `len`
   dans ce cas **n'a pas été instruit**. La question est **sans effet ici** : les
   cinq surcharges `20CB` des treize commandes portent toutes un `len` explicite.

---

## 17. Ce que ce document ne fait pas

Il ne tranche aucun régime · il n'émet aucune conclusion par défaut · il ne crée
aucune hypothèse, aucun seuil, aucune constante · il ne modifie aucun contrat ·
il ne rouvre ni `c7` §4.3, ni `C1`, ni `C5` · il n'ouvre ni Acte B, ni `T0` /
`T1` / `T2` · il n'autorise aucun terrain, aucune lecture sur l'hôte, aucune
inspection de journal, aucune mutation, aucun `debug` · il ne consulte pas `A6` ·
il ne verse aucun fichier amont dans ce dépôt.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.** Le pont historique demeure
l'unique écrivain réel de production ; la surface transactionnelle demeure sans
autorité, `false`.

---

## 18. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Instruction initiale de `vito.xml`. Exécute l'acte désigné par `w4f2-a5-extraction.md` §15 |
| **3** | Réaudit. Scission du résidu **(a)** en deux termes, établie au §10, **propagée à la table du §13**. En-tête : « résidu doctrinal » → « résidu du régime », pour lever une ambiguïté. Aucune conclusion modifiée |
| **2** | Audit. Attribution des faits terrain corrigée (§4, §8.1) : `P300` et la résolution de `getTempKist` reviennent à `w4-arbitrage-activation-debug.md`, l'identifiant `20CB` à Acte A §8. Divergence acquise du `vcontrold.xml` déployé actée (§9), comparaison d'empreinte sur ce fichier retirée. Acte suivant resserré en deux lectures bornées (§15). Résidu **(a)** scindé en deux termes, la conformité du pont au contrat `A5` restant ouverte (§10, §15). Réserve renforcée sur `PR1` (§16). Aucune conclusion doctrinale modifiée |
