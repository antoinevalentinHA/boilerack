# `W4-P1` — homologation finale

> **Version 1. HOMOLOGATION, PAS RÉCIT.** Ce document consigne l'arbitrage humain
> final rendu sur `W4-P1`, ses corrections factuelles, ses résultats et leur
> portée. **Il ne réécrit pas le rapport terrain**, ne traite aucune réserve
> rédactionnelle du bornage, et **n'ouvre aucun lot**.
>
> **Aucun terrain, aucune mesure, aucune modification de l'installation, aucun
> `T0` / `T1` / `T2`.**

---

## 1. Statut

> ### `W4-P1 — VALIDÉ AVEC DÉVIATION HOMOLOGUÉE`

Le lot est celui borné par `w4p1-lot-terrain-borne.md`, **Version 3**, exécuté
après autorisation humaine explicite au titre de son **élément 6**.

> **Aucun rejeu terrain n'est requis** — décision humaine.

## 2. La déviation, consignée et non effacée

**Trois actes ont été exécutés hors de la liste close du §6** du document de
bornage : relevé de joignabilité, d'horodatage, d'identifiant de démarrage et de
temps de fonctionnement · listage des unités et des déclencheurs · listage du
répertoire portant `<config-démon>`. Tous en **lecture stricte**, aucun sur un
objet du périmètre.

**Ce qui demeure opposable, et que rien n'atténue :**

| # | |
|---|---|
| 1 | **trois actes hors liste ont été exécutés** |
| 2 | **`P1A-1` était dû et n'a pas été pris** |
| 3 | **le manquement est consigné comme tel** |
| 4 | **la liste close n'est PAS modifiée a posteriori** |
| 5 | **aucun précédent d'extension rétroactive n'est créé** |

> **L'homologation porte sur la déviation, non sur les actes.** Elle ne les
> autorise pas rétroactivement, ne les ajoute à aucune liste, et **ne peut être
> invoquée pour en couvrir d'autres**.

**Deux écarts de forme, moindres et également conservés** : `A3` a précédé la
prise d'empreintes de référence — conséquence traitée au §5 — et le relevé de
`A6`(ii) a ramené des lignes hors périmètre — traitées au §6.

## 3. Corrections factuelles retenues

**Seules ces quatre corrections sont intégrées.** Le reste du rapport terrain est
inchangé.

| Affirmation initiale | Version retenue |
|---|---|
| *« a cyclé **quatre** fois »* | **`<unité-superviseur>` a cyclé DEUX fois** pendant le lot. **Erreur réelle**, non une convention de comptage : deux cycles produisent six lignes de journal, non quatre |
| `R1` **satisfaite, 7 fichiers** | **partage 3 / 4** — §5 |
| fenêtre `B1` *« 3 h 58 min »* | **3 h 57 min 33 s**, soit **14 253,167 360 s**. Marge sous le plafond de 4 heures : **146,833 s** |
| démarrage machine sans fuseau | **heure locale**, comme tous les horodatages de journal ; les instants de relevé sont en `Z`. Écart au début du lot : **4 j 21 h 40 min 53 s** |

## 4. `R2b` — régime du superviseur pendant le lot

| | |
|---|---|
| Fenêtre du lot | **392 s** |
| Démarrages dans la fenêtre | **2** |
| Cadence tenue | **190,0 s** sur les deux intervalles ; contrôle indépendant par l'écart des instants de démarrage, **380 s = 2 × 190 s** |
| Premier cycle | **`NOMINAL`** — qualifié par la ligne propre de l'unité, couverte par `B1` |
| Second cycle | **non qualifié par la capture `B1`**, qui lui est antérieure — mais **terminé par le chemin de succès du gestionnaire de services** |

> **Aucune cessation de régime nominal n'est établie. `P1A-3a` NON DUE.**
>
> Base de la constatation, sur les relevés figés : cadence tenue · état terminal
> de succès, jamais d'échec · compteur de redémarrages nul sur les quatre unités ·
> déclencheur actif et en attente de bout en bout · et, sur toute la fenêtre
> `B1`, **76 terminaisons en succès, 76 achèvements, 0 échec**.
>
> **Registre** : la nominalité est établie par le **chemin de succès** et par la
> **cadence**, non par la ligne propre de chaque invocation.

## 5. `R1` — statut retenu

| Portée | Fichiers | Statut |
|---|---|---|
| l'empreinte de référence **précède** la lecture | `<script-superviseur>`, `<source-pont>`, `<config-démon>` | **SATISFAITE** |
| lus par `A3` **avant** la prise de référence | les **quatre** fichiers de définition d'unité | **SATISFAITE SOUS RÉSERVE DÉCLARÉE** |

**Contenu de la réserve** : pour ces quatre fichiers, la preuve couvre l'intervalle
postérieur à la prise de référence, **et non** celui qui contient `A3`.

> **Aucune preuve rétroactive n'est fabriquée.** La réserve ne suggère aucune
> modification : elle constate qu'aucune empreinte ne couvre cet intervalle.

**Les autres preuves sont inchangées** : `R2a` satisfaite — aucune unité invariante
n'a redémarré ni été reconfigurée · `R3` satisfaite sur le lot entier · `R4`
satisfaite · `R5` satisfaite, aucun fichier écrit sur l'hôte · `R6` sans objet,
aucun `ABORT`.

## 6. `A6`(ii) — rétention homologuée

**Vérification faite sur les relevés figés : les lignes hors périmètre ont
effectivement été conservées.**

| Relevé | Excédent |
|---|---|
| `07` | **28 lignes** hors périmètre — l'ouverture du bloc des unités de mesure du protocole amont, et les déclarations qu'il contient |
| `08` | le bloc de configuration lu porte aussi des éléments **au-delà** de l'élément de périphérique au sens strict |

> **HOMOLOGUÉES EN RÉTENTION.** Motifs : elles appartiennent aux **relevés figés
> servant de preuve de l'exécution réelle** · leur destruction **altérerait la
> trace du sur-relevé lui-même** · elles **n'ont servi à aucun verdict ni
> raisonnement** · elles demeurent **hors dépôt**.
>
> **Rien n'est détruit.** Et **aucune donnée nouvelle ne doit être publiée à
> partir de cet excédent** — le présent document n'en reproduit aucune.

## 7. Résultats homologués, sous leur typage exact

| Réf | Verdict |
|---|---|
| **`A-O1`** | **`RECOUVREMENT PARTIEL`** — l'intersection est `{ getTempKist }`, qui est **la totalité** de l'ensemble déclaré par le superviseur et **une partie** de celui du pont |
| **`A-O2`** | **timeout configuré / déclaré = 5**, relevé dans `<script-superviseur>` et appliqué à son unique invocation |
| **`A-O3`** | **`AUCUNE IDENTIFIÉE SUR LE PÉRIMÈTRE LU`** |
| **`A-O4`** | **cadence déclarée relevée** dans la définition du déclencheur |
| **`B-O1`** | **`ATTRIBUTION POSSIBLE`** — attribution **à l'unité** |
| **`B-O2`** | **enveloppes d'invocation uniquement** — **jamais `M6`, jamais une borne** |

**Population de `B-O2`** : **76** invocations complètes — **52 `NOMINAL`**,
**24 `INDÉTERMINÉ`**, ces dernières ne produisant aucune ligne propre.

> **La population n'est PAS homogène**, et les enveloppes **ne peuvent pas être
> comparées comme telle**. Aucune qualification de borne n'en découle, dans aucun
> sens : elle appartient au mécanisme prévu par `T0-D`.

> **Écart factuel conservé, sa cause NON établie par ce lot** :
> `<script-superviseur>` déclare un appel de journalisation sur **chacun** de ses
> chemins terminaux, et pourtant **un tiers** des invocations n'en produit aucun
> tout en se terminant en succès. **Aucune hypothèse n'est formée.**

## 8. Conséquences homologuées, à portée stricte

| # | Conséquence | Portée |
|---|---|---|
| **1** | **`Command:` ne peut pas discriminer les sondes du superviseur** | **si l'exécution suit la configuration déclarée** — le registre du §5.1.1 du bornage demeure : une lecture de configuration n'est pas une preuve d'exécution |
| **2** | **augmenter la verbosité perd cet objectif de discrimination** | mais **conserve potentiellement** celui de faire apparaître les **clôtures**. Aucun acte n'est pour autant autorisé, nommé ni proposé ici |
| **3** | **la source systemd fournit une attribution à l'unité** | **pas `M6`** — *« aucun substitut admis »*, `w4f1` §9, `U-2` |
| **4** | **aucune borne structurelle strictement inférieure à 5 s n'a été identifiée** | **SUR LE PÉRIMÈTRE LU**, et sur lui seul. **Aucune conclusion générale** sur l'absence d'une telle borne |

> **Ce que ces conséquences ne font pas.** Elles ne concluent ni sur `U-1`, ni sur
> `U-2`, ni sur `U-3`, ni sur `U-7` ; ne rendent aucun verdict `T0-A`, `T0-B`,
> `T0-C` ni `T0-D` ; **ne tranchent pas** la voie du point 1 de la sortie 1 ; et
> **n'ouvrent aucun lot**.

## 9. Ce que ce document ne fait pas

Il **ne réécrit pas le rapport terrain**, **ne rejoue aucun acte**, **ne produit
aucun critère**, **ne fixe aucun seuil**, **ne qualifie aucune borne**, **n'amende
aucun contrat**, **ne lève aucune inconnue**, **n'étend aucune liste close**,
**ne traite aucune réserve rédactionnelle** du bornage `V3`, **n'ouvre pas `T0`**,
et **n'ouvre pas le lot suivant**.

Il homologue `W4-P1`, et s'arrête là.

## 10. Historique de révision

| Version | Objet |
|---|---|
| **1** | Homologation finale de `W4-P1` sur arbitrage humain. Statut `VALIDÉ AVEC DÉVIATION HOMOLOGUÉE` ; déviation conservée sans extension rétroactive ; quatre corrections factuelles ; `P1A-3a` non due ; `R1` en partage 3 / 4 ; rétention `A6`(ii) homologuée ; résultats et portée arrêtés. Aucun terrain, aucune mesure, aucun lot ouvert. |
