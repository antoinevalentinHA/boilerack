# `W4-T2 V1` — constat d'exécution

> **`W4-T2 CONFIRMÉ`, exécution `HOMOLOGUÉE`.**
>
> **Ce document CONSIGNE. Il n'interprète pas, ne protocole rien, n'autorise
> rien.** L'autorisation du 2026-09-04 est **CONSOMMÉE**.
>
> **Les quatre rôles d'écriture du profil sont désormais caractérisés en écriture
> réelle, au moins une fois chacun.**

---

## 0. Convention

| Nom court | Document |
|---|---|
| `W4-T2` | `w4t2-ecs.md` — le protocole |
| `W4-T1C` | `w4t1-constat.md` |
| `W4-TC` | `w4t-constat.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |

**Aucune constante de site.** Les lignes d'invocation sont celles du puits, avec
leur **hôte et leur port élidés**.

---

## 1. En une ligne

**2026-09-04, `08:36:11Z` → `08:52:01Z`.** Le **dernier des quatre rôles** est
caractérisé. **Aucun brûleur n'a démarré.**

---

## 2. Préconditions — cinq pièces prévol, avant le temps 1

Atelier créé **vide** à `08:36:11.353Z`, stockage persistant, **hors de tout
dépôt versionné**. Helpers déposés **hors atelier**.

| Pièce | Empreinte | Ce qu'elle établit |
|---|---|---|
| **`P-DEP`** étendue | `22ba9348233fcb6b…` | **4 rôles** exposés par le service **installé** · `dhw_setpoint` `INTEGER [10 ; 60]` pas `1` **tol `0.0`** · **8 fichiers de la chaîne de rendu, 8 concordants** avec le dépôt |
| **`P-UFS`** | `9da684a18c794485…` | pont, démon, timer `enabled` · `<unité-boilerack>` **`disabled`** |
| **`P-VI`** | `eb04510259fc95eb…` | `V_brut` `'10.000000 Grad Celsius'`, `V_initiale` `10` · **ballon `39,099998 °C`** · brûleur `0.000000 %` · **retenu `{"value": 10}`** · cible `11` · écart `28,099998 °C` · **régime `A` prononcé** |
| **`P-RND`** | `8c779438b7ef96f0…` | par le code **installé**, hors ligne : `'11'` → **`[49, 49]`**, hex `31 31`, **2 octets** · domaine `[10 ; 60]` **sans un seul point décimal** |
| **`R-ECS-avant`** | `08dbf8a1cf3b5513…` | le message retenu, **observé seulement** |

---

## 3. Les treize preuves d'état initial

| | |
|---|---|
| **`EI-1`** | brûleur `0.000000` / `off` · ballon `39,1 °C` · relevé **avant** tout acte, depuis un consommateur aval |
| **`EI-2`** | **DÉCLARATION de l'opérateur**, portée par l'autorisation. La session distante la **rapporte** ; elle ne la constate pas |
| **`EI-3`** | plan de reprise physique — **recours, jamais étape** |
| **`EI-4`** | atelier — §7 |
| **`EI-5` / `PR-1`** | timer `inactive`/`dead`, **`NextElapse` vide** · unité d'exécution `Result=success`, **sortie constatée**, `MainPID=0` · **aucun processus superviseur vivant** |
| **`EI-6` / `PR-2`** | pont `inactive`/`dead`, `Result=success`, `MainPID=0`, **`NRestarts=0` malgré `Restart=always`** · **zéro connexion au démon en 25 s** |
| **`EI-7`** | démon `active`/`running`, **lecture nue code retour `0`** |
| **`EI-8`** | quatre unités inscriptibles **inactives** · `0` `vclient`, `0` pont, `0` Boilerack · **fenêtre muette de 12 s** · limite bornée **déclarée** |
| **`EI-9`** | restauration **armée, non exécutée** |
| **`EI-10`** | deux captures nues, concordance **brute et sémantique** |
| **`EI-11`** | `enabled = true` prouvé **sur le contenu du fichier persisté** (`e442dd0f…`) |
| **`EI-12`** | **trace côté broker** : souscriptions `221 → 222`, clients `3 → 4` |
| **`EI-13`** | trois plans — journal systemd, cadence du démon, télémétrie |

**Temps 8, quatre actes dans l'ordre** ; **`G-a` reconstatée après démarrage :
`disabled`**. **Garde de fraîcheur** concordante.

---

## 4. Actes 3 et 4 — prononcés **avant** l'écriture

```
cible                : 10 + 1 = 11        borne haute 60 : ADMISE
littéral publié      : 11                 identique au prévol
écart ballon − cible : 28,200001 °C
RÉGIME PRONONCÉ      : A — aucune demande ECS attendue
R-ECS                : retenu 10, V_initiale 10 -> ÉGALES
                       une écriture du pont au redémarrage serait SANS EFFET DE VALEUR
```

---

## 5. La PREMIÈRE ECS

`request_id` `65f21aed-0f32-44d8-8274-342793e0a4cd` · publication **unique**,
`<racine>/command`, QoS 1, `08:44:15.269Z` · charge `"value":11`.

| ACK | |
|---|---|
| `accepted` | `08:44:19.543Z` |
| **`applied`** | **`08:44:22.965Z`** — même `request_id` |

**Puits, rang 01 :**

```
args : vclient -J -h … -p … -c "setTempWWsoll 11"
returncode : 0     duration_s : 1.3166464699897915     .err : 0 octet
.out : [{"command":"setTempWWsoll 11","value":0.000000,"raw":"OK","error":""}]
```

> **Les deux octets que `P-RND` avait prédits sont exactement ceux qui ont
> atteint le démon.**

---

## 6. Confirmation, effet ECS, restauration

**Relecture nue, deux formes** : texte `'11.000000'`, `-J` `value=11.0`,
concordance brute **OUI**. **Égalité stricte** — `confirm_tolerance = 0.0`,
cible `11`, relu `11.0`. *Aucun départage flottant, aucun clamp.*

| Effet ECS | Avant | Après |
|---|---|---|
| ballon | `39,200001 °C` | `39,099998 °C` — **`−0,1`**, dérive normale |
| `getBrennerStatus` | `0.000000` | `0.000000` |

> **Aucun démarrage de brûleur, rien à attribuer.** Le **régime `A`** prononcé
> avant l'écriture est **confirmé par l'observation**.
>
> **Ceci n'établit PAS l'hystérésis.** **`I-ECS` demeure ouverte** : une
> observation unique, en régime `A`, ne dit rien du seuil. Et l'unité de
> `getBrennerStatus` n'étant pas établie — `C7` §4.3 — l'observation demeure
> **relative** : un `0` resté `0`.

**Restauration DUE** — `request_id` `8773fe35-f485-4ea0-9f8f-d1c81fe59d9b`,
**`applied` `08:45:31.618Z`**, puits rang 02 `setTempWWsoll 10`, code `0`,
**`2,0980 s`**, `.err` vide. **Relecture : `10.000000 Grad Celsius` = `V_brut`.**

**Cardinalité effective : exactement 2 rangs.** Aucune réémission.

**Fermeture** — autorité `false` persistée et prouvée sur le contenu · **puits
désarmé** · Boilerack arrêté, `Result=success`, `MainPID=0` · **liaison
libérée** · **fichiers persistés byte à byte** : TOML `5bda5337…`, env
`e9b4ccc1…`.

**Les cinq étapes** — lecture **avant** redémarrage `= V_attendue` · pont
redémarré · **`A`** actif `NRestarts=0`, **`B`** 13 connexions, **`C`**
télémétrie observée **depuis le broker** · timer redémarré · **cycle nominal**
`08:48:15Z → 08:51:20Z`, `status nominal`, `last_action none`.

**`R-ECS`, attribution** — lecture **avant** `10.000000`, lecture **après**
`10.000000` : **aucun écart à attribuer**. Message retenu **inchangé**, **ni
supprimé, ni réécrit, ni vidé**.

---

## 7. Écarts et incidents, déclarés sans minimisation — **CONSERVÉS**

1. **L'atelier contenait cinq pièces prévol** et leurs captures, là où `W4-S`
   `EI-4` exige `P-UFS` seule. **Écart consigné, non converti en conformité.**
2. **La première génération du manifeste a donné `93 / 94`.** `MANIFESTE.txt`
   **s'était inclus lui-même** : le `tee -a` du tube crée le fichier avant que
   `find` ne l'énumère, il a donc été haché **vide** puis rempli. Régénéré en
   s'excluant : **`93 / 93`**. Aucune pièce n'a été touchée.
   > **C'est un effet de bord direct de l'obligation `W4-T1` n° 2.** Règle à
   > porter aux campagnes suivantes : **le manifeste s'exclut de son propre
   > inventaire**.
3. **Deux connexions résiduelles** au démon dans la première fenêtre de
   libération, **attribuées au cycle en vol** au moment de l'arrêt ; la fenêtre
   de contrôle de 12 s est à `0`.

**Les trois obligations de `W4-T1` ont été honorées** : captures par **`tee -a`
dès la première tentative** · **`transport/` brut au manifeste** · **présence
humaine rapportée comme déclaration**.

---

## 8. Artefacts

**93 pièces**, `sha256sum -c` : **93 / 93**. Manifeste
`3acf80c116e4236d6f68a9e602bdda1b255ddf8234fd3d2ea97da7a37f6fda58` — **le
répertoire brut du puits y figure en tant que tel**, six entrées.

---

## 9. Ce que l'exécution établit — et ce qu'elle n'établit pas

**Établi, et à ne pas rouvrir :**

1. **`setTempWWsoll` est caractérisée en écriture réelle.**
2. **`dhw_setpoint` confirmé par égalité stricte.**
3. **Restauration propre**, **cardinalité 2**.
4. **Aucun effet ECS observable en régime `A`.**
5. **`R-ECS` sans effet parasite constaté.**
6. **Les QUATRE rôles d'écriture du profil sont caractérisés en écriture réelle
   au moins une fois.**

**Restent explicitement ouverts** : **`I-ECS` et le régime `B`** · **l'unité de
`getBrennerStatus`** · le **régime permanent** · le **superviseur** · le
**rollback en régime permanent** · la **souveraineté / bascule** · les autres
inconnues déjà documentées.

> **La caractérisation des quatre rôles ne vaut PAS capacité de production** —
> `W4-T2` §16.5. **`C1`, la coexistence, `U-2`, `U-3`, `H2` et `H6 (b)`
> demeurent entières.**

---

## 10. Réserve du présent constat

**Écrit par la session qui a conduit la campagne.** Il consigne des faits
horodatés et hachés ; **il ne les homologue pas**. **L'homologation a été
prononcée séparément**, et **nul n'homologue ce qu'il a produit**.
