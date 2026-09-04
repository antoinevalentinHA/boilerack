# `W4-T1 V1` — constat d'exécution

> **`W4-T1 CONFIRMÉ`, exécution `HOMOLOGUÉE`.**
>
> **Ce document CONSIGNE. Il n'interprète pas, ne protocole rien, n'autorise
> rien.** L'autorisation du 2026-09-04 est **CONSOMMÉE**.
>
> Écrit **après** les faits, **à partir des pièces gelées**. Le dépôt n'en porte
> que les empreintes ; les pièces sont **hors dépôt**.

---

## 0. Convention

| Nom court | Document |
|---|---|
| `W4-T1` | `w4t1-rejeu-pente.md` — le protocole |
| `W4-TC` | `w4t-constat.md` — les deux exécutions `W4-T` |
| `W4-S` | `w4s-campagne-minimale.md` |
| `W4-C` | `w4c-write-capture-protocol.md` |

**Aucune constante de site.** Les lignes d'invocation sont celles du puits, avec
leur **hôte et leur port élidés** ; la commande et la valeur sont intactes.

---

## 1. En une ligne

**2026-09-04, `07:33:52Z` → `07:52:20Z`.** La **première forme non entière**
jamais émise par Boilerack est passée sur le fil, la chaudière l'a **appliquée**,
et la valeur est **revenue**.

---

## 2. Un acte préalable, hors périmètre — le redéploiement

Le service installé était **antérieur à la PR #105** : `decimal_form.py`
**absent**, et `render(1.9)` levant `UnrenderableValue`. **Le défaut qui a fait
échouer `W4-T V2` a donc été constaté en direct, sur l'installation, avant
d'être corrigé.**

Roue construite depuis un **export propre de `main` `7160e8c`**, empreinte
`cc860658e52039bf…`, installée **sans dépendances** : `paho-mqtt==2.1.0`
inchangé, **seul `boilerack` a bougé**. `<unité-boilerack>` n'a **pas** été
démarrée par cet acte.

> **Cet acte est ANTÉRIEUR à la campagne et lui est étranger** — `W4-T1` §10.3.

---

## 3. Préconditions — quatre pièces, avant le temps 1

Atelier créé **vide** à `07:33:52.570Z`, sur stockage persistant, **hors de tout
dépôt versionné**. Helper de capture déposé **hors atelier**.

| Pièce | Empreinte | Ce qu'elle établit |
|---|---|---|
| **`P-DEP`** étendue | `c6314537adb38719…` | **4 rôles** exposés par le service **installé** · `heating_curve_slope` `FLOAT [0.2 ; 3.5]` pas `0.1` tol `1e-09` · **8 fichiers de la chaîne de rendu, 8 concordants** avec le dépôt |
| **`P-UFS`** | `b453a7b8d130c61a…` | pont, démon, timer `enabled` · `<unité-boilerack>` **`disabled`** |
| **`P-VI`** | `d2381e198e4d58b7…` | `V_brut` `'1.800000'`, `V_initiale` `1.8`, cible **`1.9`** par arithmétique **décimale**, cran `k = 17`, `≤ 3.5` |
| **`P-RND`** | `71bb5b1c9df59bc9…` | par le code **installé**, hors ligne : `'1.9'` → **`[49, 46, 57]`**, hex `31 2e 39`, **3 octets**, sans exposant ni zéro superflu · les 34 crans `fb7d6840…` |

---

## 4. Les treize preuves d'état initial

| | |
|---|---|
| **`EI-1`** | brûleur `modulation 0.000000`, `state off` · extérieur `32,6 °C` · relevé **avant** tout acte, depuis un consommateur aval |
| **`EI-2`** | présence physique **déclarée par écrit** dans l'autorisation |
| **`EI-3`** | plan de reprise physique connu — **recours, jamais étape** |
| **`EI-4`** | atelier — §7, écart déclaré |
| **`EI-5` / `PR-1`** | timer `inactive`/`dead`, **`NextElapse` vide** · unité d'exécution `inactive`/`dead`, `Result=success`, **sortie constatée** `09:36:31`, `MainPID=0` · **aucun processus superviseur vivant** |
| **`EI-6` / `PR-2`** | pont `inactive`/`dead`, `Result=success`, `MainPID=0`, **`NRestarts=0` malgré `Restart=always`** · **zéro connexion au démon en 25 s** |
| **`EI-7`** | démon `active`/`running`, **lecture nue code retour `0`**, `.err` vide |
| **`EI-8`** | quatre unités inscriptibles **inactives** · `0` `vclient`, `0` pont, `0` Boilerack · **fenêtre muette de 12 s** · **limite bornée déclarée** |
| **`EI-9`** | restauration **armée, non exécutée** — voie nominale **et** voie de secours |
| **`EI-10`** | deux captures nues, concordance **brute et sémantique** — `V_brut` **identique au préflight** |
| **`EI-11`** | `enabled = true` prouvé **sur le contenu du fichier persisté** (`e442dd0f…`) |
| **`EI-12`** | **trace côté broker** : souscriptions `221 → 222`, clients `3 → 4` |
| **`EI-13`** | trois plans — journal systemd, cadence du démon, télémétrie `boilerack/#` |

**Temps 8, quatre actes dans l'ordre** : puits réarmé → autorité persistée →
**démarrage manuel** → trace broker. **`G-a` reconstatée après démarrage :
`disabled`.**

**Temps 9** — garde de fraîcheur en `-J` seul : `raw` `'1.800000 '`,
**concordante**.

---

## 5. Temps 10 — la PREMIÈRE

`request_id` `e57cdd37-bcda-45f4-ba87-807548cb7a90` · publication **unique**,
`<racine>/command`, QoS 1, `07:43:47.090Z` · **littéral publié `1.9`**, jamais
`1.8 + 0.1`.

| ACK | |
|---|---|
| `accepted` | `07:43:51.671Z` |
| **`applied`** | **`07:43:55.872Z`** — même `request_id` |

**Puits, rang 01 :**

```
args : vclient -J -h … -p … -c "setNeigungM1 1.9"
returncode : 0     duration_s : 2.0923871010309085     .err : 0 octet
.out : [{"command":"setNeigungM1 1.9","value":0.000000,"raw":"OK","error":""}]
```

> **Les trois octets que `P-RND` avait prédits sont exactement ceux qui ont
> atteint le démon.** `I-8` n'est plus seulement levée sur pièces : **elle est
> confirmée en vol.**

---

## 6. Temps 11 à 14

**Départage** — relecture nue, deux formes, concordance brute **OUI** :

| | |
|---|---|
| cible | `1.9` |
| relu | `1.9` |
| **`abs(relu − cible)`** | **`0.0`** |

**Issue : `applied`.** La tolérance déclarée de `1e-9` **suffit**. *« L'écart est
exactement nul, il n'y avait rien à interpréter. »*

**Restauration DUE** — la valeur avait bougé `1.800000 → 1.900000`.
`request_id` `96dd823c-cdff-4dfa-bc61-2852481851cc`, **`applied`
`07:45:30.335Z`**, puits rang 02 — `vclient -J -h … -c "setNeigungM1 1.8"`, code `0`, **`2.1028 s`**,
`.err` vide. **Relecture : `1.800000` = `V_brut`.**

**Cardinalité effective : exactement 2 rangs.** Aucune réémission, aucune seconde
tentative, aucun autre rôle touché.

**Fermeture de l'autorité, trois actes** : `enabled = false` persisté et prouvé
sur le contenu · **puits désarmé** · unité arrêtée, `Result=success`,
`MainPID=0` · **liaison libérée**, `0` connexion sur 25 s puis fenêtre de
contrôle de 12 s à `0`.

**Les deux fichiers persistés sont revenus BYTE À BYTE** : TOML `5bda5337…`, env
`e9b4ccc1…`.

**Les cinq étapes** : lecture nue `= V_attendue` (`V_brut`) · pont redémarré ·
**`A`** actif `NRestarts=0`, **`B`** 10 connexions au démon, **`C`** télémétrie
observée **depuis le broker** · timer redémarré · **cycle nominal complet
observé** `07:48:12Z → 07:51:21Z`, `status nominal`, **`last_action none`**.

**État final** : pont, démon, timer `active`/`enabled` · `<unité-boilerack>`
`inactive`/`disabled` (`G-a`) · autorité persistée `false` (`G-b`) · valeurs
chaudière `1.800000` · `15.000000` · `10.000000` · `2.000000`, **toutes
initiales** · **aucun redémarrage machine**.

---

## 7. Écart déclaré, non minimisé

**L'atelier contenait QUATRE pièces prévol**, et leurs captures, là où `W4-S`
`EI-4` exige *« un atelier ne contenant QUE la pièce `P-UFS` »*.

> `W4-T` l'avait déjà porté à deux en ajoutant `P-DEP` ; `W4-T1` à quatre en
> ajoutant `P-RND` et `P-VI`. **L'exigence réellement servie est l'absence de
> contamination antérieure**, et elle est tenue : atelier **créé vide**, **seules
> les pièces exigées par l'autorisation** y ont été déposées, **avant le temps
> 1**. **L'écart est consigné, non converti en conformité.**

**Un incident d'instrumentation, sans effet sur les preuves** : un `printf` du
script de capture a échoué sur une option (`--`) en écrivant une pièce de
transcription ; **la pièce a été régénérée complète**, et **le contenu du puits
n'a jamais été touché**.

**Une observation, sans rapport avec la campagne** : le courtier porte un message
**retenu** sur le topic de commande **historique**, portant la consigne ECS à sa
valeur en place. **Signalée, non modifiée** — Arsenal est hors périmètre.

---

## 8. Artefacts

**70 pièces**, `sha256sum -c` : **70 / 70**. Manifeste
`601dfb8c46d8d0ceda860ca1fcbe13231ebd9aafd8b7cd56370e18c8a1ed9c93`.

Les pièces de `G.2`, `W4-S` et `W4-T` demeurent **intactes** sous leurs puits
distincts.

---

## 9. Ce que l'exécution établit — et ce qu'elle n'établit pas

**Établi, et à ne pas rouvrir :**

1. **`setNeigungM1` est caractérisée en écriture réelle** — transport, `ACK`,
   confirmation, restauration.
2. **La forme décimale non entière `1.9` est confirmée EN VOL.**
3. **`confirm_tolerance = 1e-9` suffit** pour ce cas — **mesuré**, non supposé.
4. **Cardinalité 2, propre.**
5. **Restauration complète** — valeur, installation, fichiers persistés.
6. **Fermeture nominale.**
7. **Aucune incidence sur les autres rôles.**

**Non établi :**

| | |
|---|---|
| **`setTempWWsoll`** | **AUCUNE caractérisation terrain.** Rôle jamais engagé |
| **`C1`, coexistence, `U-2`, `U-3`, `H2`, `H6 (b)`** | **entières** |
| **Régime permanent, re-pointage du superviseur, bascule** | **intacts** |
| **Unité de `getBrennerStatus`** | ouverte — `C7` §4.3 |

---

## 10. Réserves non bloquantes, conservées pour les campagnes suivantes

1. **Éviter l'incident `printf`** : employer directement `tee -a` pour toute
   écriture de pièce.
2. **Inclure le répertoire brut `transport/` dans le manifeste**, et non
   seulement des copies de ses fichiers.
3. **La présence humaine est une DÉCLARATION de l'opérateur, jamais un constat
   distant.** Une session à distance la **rapporte** ; elle ne l'établit pas.

> **Ces trois réserves sont CONSERVÉES, non corrigées ici** : elles s'imposent
> aux campagnes suivantes, à commencer par **`W4-T2`**.

---

## 11. Réserve du présent constat

**Écrit par la session qui a conduit la campagne.** Il consigne des faits
horodatés et hachés, vérifiables sur les pièces gelées ; **il ne les homologue
pas**. **L'homologation a été prononcée séparément**, et **nul n'homologue ce
qu'il a produit**.
