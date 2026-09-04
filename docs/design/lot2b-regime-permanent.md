# `LOT 2B` — régime permanent et rollback

> ## `EXÉCUTÉ` — et `NON HOMOLOGUABLE STRICTEMENT`
>
> **`LOT 2B V1` a été exécuté le 2026-09-04.** Les cinq actes, la bascule, le
> rollback réel chronométré à **73 s** et la remise en régime sont
> **matériellement établis**. **Le régime permanent est en place.**
>
> **L'exécution n'est PAS homologable au regard du §10**, et elle ne le
> deviendra pas : **`§10.0`** — la `P-DEP` est absente et son antériorité est
> hors d'atteinte · **`§10.4`** — **aucun redémarrage machine APRÈS la bascule** ·
> **`§10.9`** — les critères `AB`/`FA` **n'ont pas été prononcés en fenêtre**.
>
> **Réserve NON RÉSOLUE, conservée** : dans la pièce `C-acte-5` du dossier de
> preuve, l'étiquette « toml AVANT » précède un bloc de contenu relevé **après**
> la mutation. Défaut de transcription, non de fait — mais **non corrigé**.
>
> Preuve matérielle **hors dépôt**, 21 pièces :
> `687db4d22808a7901dba58f51c3cbe7e0b5af658b281f23db3041128fc72eb1d`.
>
> **La preuve de régime est complétée — jamais régularisée — par `LOT 2B-R`,
> `lot2b-r-reboot.md`.**

---

> **Version 1 — DOCUMENT DE PRÉPARATION.** Il a été écrit **avant** toute
> bascule, pour mesurer, éprouver hors production, et **borner** les actes qui
> renversent le régime. **Il a rempli cet office, puis il a été exécuté.**
>
> ### Trois mentions de ce document sont **PÉRIMÉES**
>
> Elles étaient vraies à la rédaction. **Elles ne le sont plus, et elles sont
> remplacées ici** — le corps du document les conserve à titre historique,
> chacune signalée sur place.
>
> | Mention périmée | État réel, au 2026-09-04 |
> |---|---|
> | *« Aucun acte de souveraineté n'a été accompli »* | **`LOT 2B V1` a été EXÉCUTÉ.** Les cinq actes du §7 sont accomplis, dans l'ordre contraint : **bascule**, **rollback réel**, **remise en régime** |
> | *« L'autorisation humaine est `NON DONNÉE` »* | **DONNÉE le 2026-09-04**, en deux temps — `10:47:26Z`, puis `10:49:47Z` qui l'a rendue conforme au §12 — **puis CONSOMMÉE** |
> | *« L'acte réservé 4 demeure interdit en tout état de cause »* | **Clause LEVÉE nommément, pour cette seule campagne**, par l'autorisation, qui porte expressément les **actes réservés 2, 3 et 4** du `w4f` §11.1 |
>
> **Et cela ne rend pas l'exécution homologable** : `V1` demeure
> **`NON HOMOLOGUABLE STRICTEMENT`** — bandeau ci-dessus.

---

## 0. Convention et désignation

| Nom court | Document |
|---|---|
| `w4f` | `w4f-write-sovereignty.md` |
| `W4-S` | `w4s-campagne-minimale.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `W4-T2` | `w4t2-ecs.md` · constat `w4t2-constat.md` |
| `W4-T1` | `w4t1-rejeu-pente.md` · constat `w4t1-constat.md` |
| `C7` | `c7-mqtt-read-contract.md` |
| `W1` | contrats de cycle de vie MQTT |

Unités désignées `<unité-boilerack>`, `<unité-pont>`, `<unité-démon>`,
`<unité-superviseur>`, `<timer-guard>`. **Aucune constante de site.**

**Désignation** : `LOT 2B`, sous-objectif 2 du Lot 2. **Vérifiée libre.**

> **On sort des campagnes de caractérisation rôle par rôle.** Les quatre rôles
> sont caractérisés — `w4t2-constat.md` §9. **Ce qui reste n'est plus une
> question d'écriture, mais de DURÉE et de RETOUR EN ARRIÈRE.**

---

## 1. Objet

> **Objet : qualifier Boilerack comme service DURABLE — revenant au boot,
> fonctionnant seul sous le superviseur, supportant les reconnexions et les
> pannes ordinaires — et établir un ROLLBACK explicite vers le pont historique,
> qui fonctionne même si Boilerack est figé ou mort.**

### 1.1 Ce que le lot établira, et rien de plus

Le **budget de sonde réel**, la **marge du superviseur**, le **comportement en
reconnexion**, le **filet de boot**, et une **procédure de rollback bornée dans
le temps et mesurée**.

> **Il n'établira pas** : que `C1` est satisfaite · que la coexistence est
> qualifiée · que `H2`, `H6 (b)`, `U-2` ou `U-3` seraient closes · **aucune
> autorisation de bascule**.

---

## 2. Périmètre

> **PÉRIMÉ — interdiction levée par l'autorisation du 2026-09-04.** Conservée
> ici telle qu'elle s'appliquait **avant** l'audit et l'autorisation.
>
> **`LOT 2B` MUST NOT**, tant que l'audit n'a pas borné les actes du §7 :
>
> - **activer `<unité-boilerack>` au démarrage** ;
> - **désactiver `<unité-pont>`** ;
> - **installer** le superviseur modifié, ni son variable d'environnement ;
> - **ouvrir l'autorité d'écriture de façon permanente** ;
> - **modifier Arsenal**, en quoi que ce soit ;
> - **basculer la souveraineté** — acte réservé **4**.

**Ce que le lot faisait, à la rédaction, et qui ne franchissait aucune de ces
bornes** : il **mesurait**, il **simulait hors production**, et il posait des
artefacts **volatils** — dans `/run`, effacés au redémarrage — pour éprouver un
mécanisme sans l'installer. **Les cinq actes ont ensuite été accomplis sous
l'autorisation du §12.**

---

## 3. Ce qui a été MESURÉ — banc du 2026-09-04

**Fenêtre `09:23:23Z` → `09:40:23Z`.** Superviseur neutralisé, pont arrêté,
Boilerack démarré **autorité FERMÉE** : **aucune écriture n'était possible**, et
aucune n'a eu lieu. Puits **désarmé** de bout en bout.

### 3.1 Budget de sonde — la prédiction confrontée à la mesure

**Prédiction, dérivée du contrat de lecture** — 9 commandes distinctes,
4 à 30 s et 5 à 60 s :

```
4 × 2/min  +  5 × 1/min  =  13 invocations/min
```

| Charge | Mesure sur le journal du démon, minutes pleines | Moyenne |
|---|---|---|
| **Boilerack seul** | **14 · 19 · 13** connexions/min | **15,3/min** |
| **Pont historique seul** | **28 · 28 · 29** connexions/min | **28,3/min** |

> **La prédiction n'est PAS confirmée, et le dire autrement serait la défendre.**
> Un échantillon sur trois atteint **19 connexions/min**, soit **≈ 46 % au-dessus
> de la prédiction de 13/min**. Les deux autres, `14` et `13`, l'encadrent de
> près. **Trois minutes ne sont pas une distribution**, et **aucune conclusion
> quantitative n'est tirée d'elles.**
>
> **Un contributeur documenté existe pour la minute à 19**, et il est vérifiable
> sur les horodatages du banc : le relevé de latence du §3.2 — **dix invocations
> de sonde** — s'est déroulé pendant cette minute-là. **La mesure est conservée
> telle quelle, à 19.** Elle n'est ni corrigée, ni écartée, ni expliquée : la
> cause probable est signalée, **le chiffre reste**.

> **Correction d'une valeur du corpus.** La figure **« 56 invocations/min pour le
> pont, soit 4,3× »** **n'est PAS confirmée par la mesure** : le pont ouvre
> **28 à 29 connexions/min**.
>
> Le rapport mesuré vaut **≈ 1,8×** sur les moyennes, et s'étale de **≈ 1,5×**
> — pire échantillon pour Boilerack, `19` contre `28` — à **≈ 2,2×** —
> meilleur, `13` contre `29`.
>
> **La seule conclusion retenue est DIRECTIONNELLE : Boilerack charge
> sensiblement moins la liaison que le pont historique.** Aucun facteur n'est
> déclaré, ni `4,3`, ni `2,2`, ni `1,8`.

### 3.2 La marge du superviseur — et c'est la découverte du lot

La sonde du superviseur est **`vclient getTempKist`**, **timeout `5 s`**.

| Charge | Moyenne | **Maximum** | **Marge sur 5 000 ms** |
|---|---|---|---|
| **Pont historique seul** — 20 invocations | 2 527 ms | **4 261 ms** | **739 ms** |
| **Boilerack seul** — 10 invocations | 2 292 ms | **3 189 ms** | **1 811 ms** |

> **Le plancher de ≈ 2,19 s est le trajet Optolink, pas la contention** : il est
> identique sous les deux charges. Ce qui varie, c'est la **queue** : sous le
> pont, trois invocations consécutives ont atteint **4,25 s**.
>
> **La marge actuelle, en production, est de 739 ms.** C'est **mince**, et ce
> n'est **pas** un défaut créé par Boilerack : **c'est l'état présent**.
> **Boilerack la porte à 1 811 ms, soit 2,4× plus.**
>
> **Ce que cela ne dit pas** : dix invocations ne sont pas une distribution.
> **Aucun seuil n'est déclaré ici**, et **`FA-9` n'est pas levée**.

### 3.3 Reconnexion et reprise — quatre épreuves, aucune régression

| Épreuve | Geste | Résultat mesuré |
|---|---|---|
| **MQTT** | courtier bloqué **35 s** par une règle de filtrage **volatile**, retirée et vérifiée retirée | service **`active`**, **`NRestarts=0`** |
| **`<unité-démon>`** | démon **arrêté 40 s** puis redémarré | service **`active`**, **`NRestarts=0`** ; lecture nue redevenue `0` après reprise |
| **Redémarrage du service** | `restart` | reprise propre, connexion MQTT rétablie en ≈ 2 s |
| **Redémarrage machine** | `reboot` **au banc, AVANT la bascule** | machine revenue en **≈ 47 s** |

**La preuve de reprise est POSITIVE, et ne repose pas sur l'absence de trace** :
après les deux pannes, l'état de chaîne **publié par Boilerack** vaut
`{"status":"ok","cause":null}`, avec **dix mesures, toutes fraîches, toutes en
`last_result=ok`**.

> **Ce que borne un blocage réel** : le sous-processus de lecture est plafonné à
> **`read_timeout_s = 5,0`** et **`write_timeout_s = 5,0`**. Un cycle ne peut
> donc pas s'immobiliser indéfiniment sur la liaison.
>
> **Aucune doctrine de cycle de vie n'est créée ici** : les contrats `W1`
> existants sont **vérifiés**, pas réécrits.

### 3.4 Le filet de boot AVANT la bascule — éprouvé par un redémarrage réel

> **Ce relevé date du banc préparatoire, et il est ANTÉRIEUR à la bascule.** Il
> décrit le filet **non inversé**. Après la bascule, ce tableau **s'inverse** —
> §8 — et **aucun redémarrage n'a été fait pour le constater** : c'est l'objet de
> **`LOT 2B-R`**.

Après redémarrage réel **du banc**, **sans aucune intervention** :

```
<unité-pont>        active    enabled
<unité-démon>       active    enabled
<timer-guard>       active    enabled
<unité-boilerack>   inactive  disabled     <- G-a, VÉRIFIÉE PAR LE FAIT
```

Le superviseur a tiré son cycle de boot et a conclu **`NOMINAL`**. L'artefact
volatil du §5 avait **disparu**, `/run` étant effacé au démarrage. L'autorité
persistée portait toujours **`enabled = false`** — **`G-b`**.

---

## 4. Le superviseur — re-pointage minimal

### 4.1 `v1.2` — **une seule ligne de LOGIQUE**

```
  # LOGIQUE — la seule ligne qui change un comportement
- BRIDGE_SERVICE="<unité-pont>"
+ BRIDGE_SERVICE="${BRIDGE_SERVICE:-<unité-pont>}"

  # IDENTIFICATION — le script s'annonce pour ce qu'il est
- # arsenal-boiler-guard — v1.1        -> v1.2
- publication de « boiler/guard/version » : v1.1  -> v1.2
```

> **Le défaut est inchangé.** Sans variable d'environnement, `v1.2` **se comporte
> exactement comme** `v1.1` — **à ceci près qu'il s'annonce `v1.2`**, ce qui est
> le but des deux lignes d'identification. Avec la variable, la cible se déplace
> **sans toucher au script**.
>
> **Conséquence directe sur le rollback** : revenir en arrière, c'est **retirer
> une ligne d'environnement**. Le script n'a **jamais** à être ré-édité, et il
> n'existe donc **aucune fenêtre** où il serait à moitié modifié.

### 4.2 Le banc — **neuf cas, hors production**

Le script sous test n'a **rien touché** : `systemctl`, `reboot`, `ip`, `ping`,
`logger`, le client MQTT et `vclient` étaient **interceptés** et journalisaient
leurs appels.

| Cas | Situation | Appel système observé |
|---|---|---|
| **1** | nominal, **aucune variable** | **aucun** |
| **2** | nominal, cible re-pointée | **aucun** |
| **3** | sonde KO puis OK, re-pointée | `restart <unité-boilerack>` |
| **4** | sonde KO **deux fois**, re-pointée | `restart <unité-boilerack>` **puis `reboot`** |
| **5** | réseau KO — AXE 2 | interface cyclée **puis `reboot`** · **le pont n'est PAS redémarré** |
| **6** | sonde KO/OK, **aucune variable** | `restart <unité-pont>` |
| **7** | **le même cas sur `v1.1` installé** | `restart <unité-pont>` |
| **8** | sonde **hors bornes** (code 3) | `restart <unité-boilerack>` |
| **9** | sonde **non numérique** (code 2) | `restart <unité-boilerack>` |

> **Non-régression établie par comparaison de traces** : les cas **6** et **7**
> produisent des traces **identiques**. **`v1.2` sans variable se comporte
> exactement comme `v1.1`.**

### 4.3 Ce que le re-pointage **NE répare PAS**

> **La sonde teste `<unité-démon>` directement, jamais le pont.** Le remède —
> redémarrer un service de pont — **ne peut pas réparer le démon**.
>
> **Le re-pointage ne change donc pas la nature du remède : il change seulement
> QUEL service est redémarré inutilement.** Il **MUST NOT** être présenté comme
> une réparation de `<unité-démon>`, ni comme une amélioration de la couverture
> du superviseur. **C'est une mise en cohérence de la cible, et rien d'autre.**

### 4.4 L'escalade demeure, et **elle reboote**

Le cas **4** l'établit sur le banc : deux échecs de sonde → redémarrage du
service → `sleep 90` → seconde sonde → **`reboot`**.

> **En régime permanent, une panne de `<unité-démon>` conduit donc à : redémarrer
> Boilerack — sans effet sur la cause — puis à REDÉMARRER LA MACHINE.**
>
> **Ce mécanisme n'est ni corrigé ni atténué par le présent lot.** Il est
> **nommé**, et il devra être arbitré séparément : le corriger touche à
> l'escalade, ce qui excède le re-pointage minimal demandé.

---

## 5. L'exclusion mutuelle des deux écrivains

**Exigence** : *aucun état où les deux écrivains sont simultanément souverains.*

**Mécanisme retenu, et ÉPROUVÉ** — une déclaration `Conflicts=` portée par
`<unité-boilerack>` vers `<unité-pont>`, posée en **drop-in VOLATILE** dans
`/run` pour le banc :

| Geste | Résultat mesuré |
|---|---|
| état initial | pont **actif**, Boilerack **inactif** |
| démarrer Boilerack | pont **arrêté**, Boilerack **actif** |
| démarrer le pont | pont **actif**, Boilerack **arrêté** |

> **L'exclusion joue dans LES DEUX SENS**, et systemd l'applique lui-même : il
> n'existe pas de fenêtre où les deux tournent. Le drop-in a été **retiré**, et
> le redémarrage machine du §3.4 l'a **effacé de toute façon**.
>
> **Il n'est PAS installé de façon persistante** : cet acte relève du §7.

---

## 6. Le rollback — explicite, sans redémarrage

### 6.1 `SIGSTOP` n'est **pas** un gel — la correction

**Premier essai** : le processus a été suspendu par `SIGSTOP`, puis le service
arrêté. **L'arrêt a pris `0 s`.**

> **Ce n'est pas une bonne nouvelle : c'est une épreuve INVALIDE.** systemd envoie
> **`SIGCONT` avec `SIGTERM`**. Le processus suspendu est **dégelé**, reçoit son
> `SIGTERM` et se termine normalement.
>
> **`SIGSTOP` ne modélise donc pas un Boilerack figé**, et le pire cas **n'avait
> pas été éprouvé**. L'essai est consigné tel quel, **et non présenté comme un
> succès**.

### 6.2 Le pire cas, **mesuré** sur une doublure

Une unité **doublure**, volatile, dont le programme **ignore `SIGTERM`**, portant
le **même `TimeoutStopSec = 90 s`** :

```
arrêt demandé  09:32:05.131Z
arrêt obtenu   09:33:35.222Z
DURÉE RÉELLE : 90 s      Result=timeout      ActiveState=failed
journal : Killing process … with signal SIGKILL / code=killed, status=9/KILL
```

> **Le pire cas n'est pas une estimation : il est mesuré, et il vaut exactement
> 90 secondes.** Au terme, `SIGKILL` **termine le processus**, et l'unité est
> bien **arrêtée**.

### 6.3 La procédure — cinq gestes, aucune n'est un redémarrage machine

| # | Geste | Borne mesurée |
|---|---|---|
| **1** | **arrêter `<unité-boilerack>`** | **≤ 90 s** — immédiat si le processus répond, `90 s` puis `SIGKILL` s'il ne répond pas |
| **2** | **constater la libération de la liaison** | `0` connexion au démon **15 s** après l'arrêt |
| **3** | **démarrer `<unité-pont>`** | — |
| **4** | **établir les trois faits `A`, `B`, `C`** | pont actif · **12 connexions** au démon en 25 s · **télémétrie observée depuis le courtier** |
| **5** | **remettre `<timer-guard>`**, et attendre un **cycle nominal** | cycle observé, `status nominal`, `last_action none` |

> **Rollback complet, pire cas : ≈ 130 s.** `90 + 15 + 25`, plus l'attente d'un
> cycle du superviseur. **Aucun redémarrage machine n'y figure**, et
> **`EI-3` demeure un recours, jamais une étape**.

### 6.4 Ce dont la procédure **ne dépend pas**

> **Elle ne dépend pas de `Result=success`.** Un arrêt forcé laisse l'unité en
> **`failed` / `timeout`** — c'est **l'issue nominale du pire cas**, et une
> procédure qui exigerait `success` **échouerait précisément quand elle est le
> plus nécessaire**.
>
> Elle ne dépend pas non plus de la **coopération** de Boilerack, de son
> **journal**, ni de sa **connexion au courtier** : les trois faits `A`, `B`, `C`
> sont établis **depuis l'extérieur**, et le fait `C` **depuis un consommateur
> aval**, jamais depuis la sortie standard du pont.

---

## 7. LA BORNE — les cinq actes qui renversent le régime

> **PÉRIMÉ.** À la rédaction, aucun n'avait été accompli. **Ils l'ont tous été
> le 2026-09-04, dans l'ordre contraint ci-dessous**, sous l'autorisation du §12.
> Le texte d'origine suit.
>
> **Aucun n'a été accompli. Ils forment ensemble la bascule, et ils sont
> indissociables.**

| # | Acte | Pourquoi il ne peut pas être isolé |
|---|---|---|
| **1** | **activer `<unité-boilerack>` au démarrage** | seul, il crée un boot à **deux écrivains** |
| **2** | **désactiver `<unité-pont>`** | seul, il laisse l'installation **sans écrivain** au boot |
| **3** | **installer le `Conflicts=` de façon persistante** | c'est la **garde** qui rend 1 et 2 sûrs ; sans elle, l'exclusion repose sur la discipline |
| **4** | **installer le superviseur `v1.2` + la variable de cible** | sans lui, le superviseur redémarre un service **arrêté et désactivé** |
| **5** | **ouvrir l'autorité d'écriture de façon permanente** | sans elle, Boilerack tourne sans pouvoir écrire ; avec elle **avant** 1 à 4, deux écrivains deviennent possibles |

> **L'ordre importe, et il est contraint** : **3 avant 1**, **4 avant 2**,
> **5 en dernier**. Toute autre séquence ouvre une fenêtre à deux souverains ou
> une fenêtre sans souverain.
>
> **C'est ici que l'audit indépendant s'interpose**, et **nulle part ailleurs**
> dans ce lot.

---

## 8. Le filet de boot **s'inverse**

**Aujourd'hui, mesuré** : un redémarrage ramène le pont, le démon et le
superviseur ; **Boilerack ne revient pas**.

**Après les cinq actes** : un redémarrage ramènera **Boilerack**, et **pas le
pont**.

> **Le redémarrage cesse alors d'être un rollback.** Il en devient l'inverse :
> il **restaure la nouvelle souveraineté**. C'est précisément pourquoi le
> rollback du §6 doit être une **procédure explicite** — et pourquoi
> **`EI-3` ne peut plus servir de secours** une fois la bascule faite.

---

## 9. Arsenal — **non recâblé**

> **Arsenal n'est pas recâblé, et ne le sera pas par ce lot.** Le recâblage
> demeure **ATOMIQUE AVEC LA BASCULE** : le faire avant aveuglerait des capteurs
> vivants, le faire après laisserait Arsenal parler à un pont arrêté.
>
> **Le message retenu de la surface historique n'est ni supprimé, ni réécrit, ni
> vidé** — `W4-T2` §5.

---

## 10. Preuves exigées à l'exécution des actes du §7

| # | Sortie |
|---|---|
| **0** | **`P-DEP` étendue**, **`P-UFS`**, antérieures au premier acte |
| **1** | l'état **avant** : `UnitFileState` des quatre unités, autorité persistée, empreintes des fichiers persistés |
| **2** | **les cinq actes, dans l'ordre du §7**, chacun horodaté et constaté |
| **3** | **la preuve qu'à aucun instant les deux écrivains n'ont été actifs ensemble** |
| **4** | un **redémarrage machine réel**, et le **filet de boot inversé** constaté — **NON PRODUIT par `V1`**, et il faut être exact : un redémarrage réel **a bien eu lieu au banc, AVANT la bascule** (§3.4), et il a constaté le filet **NON inversé** ; **aucun redémarrage n'a eu lieu APRÈS la bascule, en régime permanent**. **C'est cette preuve-là, et elle seule, que `LOT 2B-R` doit établir** |
| **5** | un **cycle nominal du superviseur** re-pointé, sans action corrective |
| **6** | le **budget de sonde** et la **marge** re-mesurés en régime permanent |
| **7** | **un rollback réel exécuté de bout en bout**, chronométré, puis le retour au régime permanent |
| **8** | les **fichiers persistés**, empreintes **avant et après** |
| **9** | tout critère **`AB`** ou **`FA`** atteint, **prononcé ou non** |
| **10** | ce qui **demeure non établi** |

**Toutes les pièces sont hachées et portées à un manifeste — répertoire brut du
puits compris, et le manifeste s'exclut de son propre inventaire**
(`w4t2-constat.md` §7).

---

## 11. Critère de succès

> **`LOT 2B CONFIRMÉ`** — et il n'y a pas de demi-succès.

1. les **cinq actes** accomplis **dans l'ordre**, chacun constaté ;
2. **aucun instant à deux écrivains actifs**, prouvé ;
3. **filet de boot inversé**, constaté sur un redémarrage réel **postérieur à la
   bascule** — le redémarrage du banc, antérieur, ne peut pas y suppléer ;
4. **cycle nominal** du superviseur re-pointé ;
5. **rollback réel exécuté**, chronométré, **sans redémarrage machine** ;
6. **retour au régime permanent** après le rollback ;
7. **aucun `AB`, aucun `FA`**.

**Tout autre cas est `LOT 2B ABANDONNÉ`**, avec le motif.

---

## 12. L'autorisation humaine

> ### `DONNÉE le 2026-09-04, puis CONSOMMÉE`
>
> **PÉRIMÉ : `NON DONNÉE`.** L'autorisation a été donnée en deux temps —
> `10:47:26Z`, puis `10:49:47Z` qui en a porté les points 2 et 6 et l'a rendue
> conforme. Elle a été **CONSOMMÉE** par l'exécution du même jour, et **ne peut
> plus fonder aucun acte**.
>
> Les exigences ci-dessous sont conservées **comme mémoire de ce qui était
> requis**, et elles ont été servies.

**L'autorisation, si elle est donnée, MUST :**

| # | |
|---|---|
| **1** | être précédée d'un **AUDIT INDÉPENDANT** du présent document, et de son **INTÉGRATION** |
| **2** | **nommer `LOT 2B` ET sa version**, être explicite, distincte, postérieure aux deux |
| **3** | **nommer les CINQ actes du §7**, et **accepter leur ordre** |
| **4** | **reconnaître que le filet de boot s'inverse** — §8 |
| **5** | **reconnaître que l'escalade du superviseur reboote toujours** en cas de panne du démon — §4.4 |
| **6** | porter les **actes réservés** du `w4f` §11.1 nécessaires, et **eux seuls** |
| **7** | **pré-décider le rollback** du §6, et son déclenchement |
| **8** | valoir pour **une exécution, et une seule** |

**Elle MUST NOT :**

- être **déduite** de l'audit, de l'intégration ou du merge du présent document ;
- se réclamer d'une autorisation antérieure — **toutes sont CONSOMMÉES** ;
- valoir autorisation de **modifier Arsenal**, ni de **recâbler** quoi que ce
  soit ;
- valoir autorisation de **corriger l'escalade** du superviseur ;
- porter l'**acte réservé 4** au-delà de ce que les cinq actes du §7 impliquent
  **strictement**.

---

## 13. Ce qu'un auditeur doit pouvoir trancher AVANT les actes du §7

| | Question | Où |
|---|---|---|
| **0** | le **budget de sonde** est-il mesuré, et la prédiction confrontée plutôt qu'affirmée ? | §3.1 |
| **1** | la **marge du superviseur** est-elle établie sous les DEUX charges ? | §3.2 |
| **2** | une figure du corpus est-elle **corrigée** plutôt que défendue ? | §3.1, les 56/min |
| **3** | la reprise est-elle prouvée **positivement**, et non par absence de trace ? | §3.3 |
| **4** | le re-pointage est-il **une seule ligne**, et sa non-régression prouvée par **traces identiques** ? | §4.1, §4.2 |
| **5** | le document **s'abstient-il** de prétendre que le re-pointage répare le démon ? | §4.3 |
| **6** | l'**escalade qui reboote** est-elle nommée plutôt que tue ? | §4.4 |
| **7** | l'exclusion mutuelle est-elle **éprouvée dans les deux sens**, et **non installée** ? | §5 |
| **8** | l'épreuve `SIGSTOP` **invalide** est-elle consignée comme telle ? | §6.1 |
| **9** | le **pire cas de 90 s** est-il **mesuré**, et la procédure indépendante de `Result=success` ? | §6.2, §6.4 |
| **10** | les **cinq actes** sont-ils indissociables, ordonnés, et **non accomplis** ? | §7 |
| **11** | l'**inversion du filet de boot** est-elle déclarée avant, et non découverte après ? | §8 |
| **12** | **Arsenal** est-il laissé intact, recâblage **atomique avec la bascule** ? | §9 |

---

## 14. Ce que ce document ne faisait pas

> **PÉRIMÉ pour ses deux premières mentions.** Le document n'exécutait ni
> n'autorisait rien **par lui-même** — et il ne le fait toujours pas : ce sont
> **l'autorisation du §12** et l'exécution du 2026-09-04 qui ont accompli les
> cinq actes et installé le superviseur, le drop-in et la variable. **Le reste
> de la liste demeure vrai.**

Il **n'exécutait aucun des cinq actes du §7** · **n'autorisait rien** ·
**n'installait rien** — ni superviseur, ni drop-in, ni variable · **ne modifie
pas Arsenal** · **ne corrige pas l'escalade** du superviseur · **ne révise
aucune tolérance** · **ne lève ni `I-ECS`, ni `C1`, ni `U-2`, ni `U-3`, ni `H2`,
ni `H6 (b)`** · **ne crée aucune doctrine de cycle de vie** : il vérifie les
contrats existants.

**Il a mesuré, éprouvé hors production, borné — et l'exécution est venue
ensuite, sous autorisation.**

---

## 15. Réserves conservées

1. **La marge de sonde de `739 ms` sous le pont historique est mince**, et elle
   est **antérieure à Boilerack**. **Aucun seuil n'est déclaré**, et dix
   invocations ne sont pas une distribution.
2. **L'escalade du superviseur reboote la machine** sur une panne prolongée du
   démon, et **le re-pointage n'y change rien**. Arbitrage **différé**, nommé.
3. **Le remède du superviseur ne correspond pas au défaut qu'il diagnostique.**
   Constat ancien, **ni corrigé ni aggravé ici**.
4. **Le budget de sonde n'est PAS établi quantitativement.** La prédiction de
   `13/min` n'est pas confirmée — un échantillon monte à `19/min` — et la
   correction de la figure « 56 invocations/min » vaut pour les mesures faites
   ce jour, sur cette installation, dans ces conditions. **Seule la conclusion
   directionnelle du §3.1 est retenue**, et **elle ne prétend pas à une loi**.
   Établir un budget exigerait une campagne de mesure propre, sur une durée
   longue et **sans instrumentation concurrente** — elle reste à ouvrir.
5. **`SIGSTOP` ne modélise pas un gel** — §6.1. Le pire cas a été établi sur une
   **doublure**, non sur Boilerack : **on a mesuré le mécanisme de systemd, pas
   la propension de Boilerack à se figer**, qui demeure **non caractérisée**.
6. **Le blocage réel est borné par les délais du sous-processus** (`5,0 s` en
   lecture comme en écriture), **mais aucun blocage réel n'a été observé**.
7. **`I-ECS` et le régime `B`**, **l'unité de `getBrennerStatus`**, **`C1`**, la
   **coexistence**, **`U-2`**, **`U-3`**, **`H2`**, **`H6 (b)`** demeurent
   **entières**.
8. **Les écarts d'audit antérieurs sont CONSERVÉS**, non corrigés : l'atelier à
   plusieurs pièces prévol, l'auto-inclusion du manifeste, et les **connexions
   résiduelles** de la fenêtre de libération.
9. **Arsenal n'est pas recâblé**, et son recâblage demeure **atomique avec la
   bascule**.
