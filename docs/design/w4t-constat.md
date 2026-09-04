# `W4-T` — constat des exécutions

> **Ce document CONSIGNE. Il n'interprète pas, ne protocole rien, n'autorise
> rien.**
>
> **Deux exécutions ont eu lieu sous `W4-T`. Les deux sont ABANDONNÉES.** Leurs
> autorisations sont **consommées**, et **aucun rejeu ne peut s'en réclamer**.
>
> Il est écrit **après** les faits et **à partir des pièces gelées**. Là où une
> pièce manque, il l'écrit.

---

## 0. Convention

| Nom court | Document |
|---|---|
| `W4-T` | `w4t-trois-ecritures.md` — le protocole, V1 puis V2 |
| `W4-C` | `w4c-write-capture-protocol.md` |
| `w4f` | `w4f-write-sovereignty.md` |

**Aucune constante de site.** Les empreintes et les horodatages sont ceux des
pièces ; les lignes d'invocation sont reproduites avec leur hôte **élidé**.

---

## 1. Les deux exécutions, en une ligne chacune

| | Date | Rang atteint | Écritures chaudière | Issue |
|---|---|---|---|---|
| **V1** | 2026-09-03 | **1** | **0** | `rejected` / `unsupported_role` |
| **V2** | 2026-09-04 | **2** | **2** | `VALEUR NON APPLIQUÉE` sur la pente |

---

## 2. V1 — abandon au rang 1, **zéro écriture**

L'`ACK` du rang 1 a conclu **`rejected` / `unsupported_role`**. Le **build
déployé** ne déclarait **qu'un rôle sur quatre** — `heating_curve_shift` — quand
le dépôt en déclarait quatre depuis le Lot 1.

> **Aucune précondition n'exigeait que le service qui allait tourner portât le
> profil audité.** `P-1` demandait Boilerack *« déployé et fonctionnel en
> lecture »*, ce qu'il était, **sans exiger qu'il fût à jour**.

**49 pièces**, conservées intactes. **La V2 a fermé ce trou par `P-DEP`, et rien
d'autre.**

---

## 3. V2 — les préconditions, avant le temps 1

`05:19:17Z` → `05:36Z`.

| | |
|---|---|
| **`P-DEP`** | `b072c409…`, prise `05:19:17.53Z` · **4 rôles** exposés par le service **installé** · les **3 rôles `W4-T` présents, aucun manquant** · **trois empreintes installées identiques à celles du dépôt** — base `main 92c78a5` |
| **`P-UFS`** | `c8fd8d4c…`, prise `05:19:49.95Z` · les trois unités historiques **`enabled`** |
| **Antériorité** | temps 1 à `05:20:47.38Z` — les deux pièces le précèdent, et l'atelier **ne contenait qu'elles** au constat `EI-4` |

> **La précondition ajoutée par la V2 a fonctionné : elle aurait bloqué la V1.**

---

## 4. V2, rôle 1 — `heating_setpoint` : **CONFIRMÉ**

| | |
|---|---|
| `V_initiale` | `15.000000` · cible **`16`** (`≤ 30`) · fraîcheur concordante |
| Écriture | `05:25:39.63Z` · `accepted` `05:25:40.67Z` → **`applied` `05:25:44.87Z`** |
| Relecture | **`16.000000`** — **égalité stricte** |
| Restauration | `accepted` → **`applied` `05:26:52.19Z`** · relecture **`15.000000` = `V_brut`** |

**Preuves de transport, produites automatiquement :**

```
rang 1 : vclient -J -h … -c "setTempRaumNorSollM1 16"   code 0   durée 2,092 s   .err vide
rang 2 : vclient -J -h … -c "setTempRaumNorSollM1 15"   code 0   durée 2,099 s   .err vide
```

> **`setTempRaumNorSollM1` est caractérisée.** C'est **le seul acquis terrain**
> des deux exécutions.

---

## 5. V2, rôle 2 — `heating_curve_slope` : **VALEUR NON APPLIQUÉE**

| | |
|---|---|
| `V_initiale` | `1.800000` · cible **`1.9`** (`≤ 3.5`) · fraîcheur concordante |
| `ACK` | `accepted` `05:28:03.55Z` → **`timeout` `05:28:09.86Z`** |
| **Relecture nue** | **`1.800000`** — écart `0.1`, soit **un cran entier** |
| Départage `W4-T` §4 | binaire `≤ 1e-9` : **non** · **métier `< 0.05` : non** → **`VALEUR NON APPLIQUÉE`** |
| **Puits** | **aucun rang pour ce rôle** — **aucune invocation d'écriture n'a eu lieu** |
| Restauration | **NON DUE** — la valeur n'a pas bougé |

### 5.1 La cause, trouvée dans le code, non déduite

`adapters/vclient_write.py`, `render()`, tel qu'il était alors :

```python
if not nombre.is_integer():
    raise UnrenderableValue("seule la forme entiere est caracterisee (W4-C)")
```

> **Le Lot 1 a déclaré `heating_curve_slope` en flottant ; l'adaptateur
> d'écriture ne savait pas rendre un flottant.**

L'exception était levée **avant tout lancement de processus** : d'où **l'absence
de rang au puits**, **la valeur intacte**, et le **`timeout`**.

**Profil et adaptateur étaient incohérents.** `I-8` — *« normalisation de la
valeur par le démon ou la chaudière »*, `W4-A` §16 — est une inconnue **nommée
du corpus**, délibérément écartée par `W4-C`. **Le Lot 1 a déclaré le rôle sans
la lever.**

---

## 6. V2, rôle 3 — `dhw_setpoint` : **NON ENGAGÉ**

Par le `W4-T` §7, l'arrêt intervient **entre deux rôles**. **L'ECS, seul rôle à
effet physique, n'a jamais été touchée** — exactement ce que l'ordre du §3.1
visait.

---

## 7. Cardinalité effective — **2**, conforme

| Rôle | Cible | Restauration |
|---|---|---|
| `heating_setpoint` | **1** | **1** |
| `heating_curve_slope` | **0** | **0** *(non due)* |
| `dhw_setpoint` | **0** | **0** |

**Le puits porte exactement deux rangs.** **Aucun `AB`, aucun `FA`** — un
`timeout` suivi d'une valeur inchangée est une **issue prévue** du `W4-T` §4, non
un critère d'abandon. **Aucune réémission.**

---

## 8. État final — nominal

```
<unite-pont> / <unite-demon> / <timer-guard>   active     enabled
<unite-boilerack>                             inactive   disabled   (G-a intacte)
autorite persistee                            enabled = false
```

**Valeurs chaudière** : `heating_setpoint 15.000000` · `heating_curve_slope
1.800000` · `dhw_setpoint 10.000000` · `heating_curve_shift 2.000000` —
**toutes à leur valeur initiale**.

**Fichiers persistés revenus byte à byte à l'origine** : TOML `5bda5337…`, env
`e9b4ccc1…`, secret ancré, **puits désarmé**.

**Cinq étapes achevées** : lecture nue · pont redémarré · **fait A** actif ·
**fait B** `23` ouvertures en `25 s` · **fait C** télémétrie observée · timer
relancé · **cycle nominal**.

> Le brûleur a démarré pendant la fenêtre — départ `64,5 °C`, ECS `52,6 °C`.
> **C'est le cycle ECS normal du matin**, sans rapport avec la campagne : sa
> consigne **n'a jamais été touchée**.

---

## 9. Artefacts

**65 pièces**, `sha256sum -c` : **65 / 65**. Manifeste
`74ac6e1f65ea6e911825a6e7d9bcab008111dea1c5c51dd07162cc99ad40e4c0`. Les **49
pièces de la V1** sont conservées intactes, sous un puits distinct.

**Le dépôt ne porte que ces empreintes.** Les pièces sont **hors dépôt**.

---

## 10. Ce que les deux exécutions ont établi — et ce qu'elles n'ont pas établi

**Établi :**

1. **`setTempRaumNorSollM1` est caractérisée** — réponse de transport, `ACK`,
   confirmation par relecture, restauration confirmée.
2. **`P-DEP` est efficace** : elle a constaté ce que la V1 avait appris par un
   rejet.
3. **Un défaut réel a été découvert avant la production** — le profil déclarait
   un rôle que l'adaptateur ne pouvait pas écrire — **sans toucher la chaudière**
   et **sans toucher l'ECS**.

**Non établi, et il faut le dire :**

| | |
|---|---|
| **`setNeigungM1`** | **AUCUNE caractérisation terrain.** Aucune invocation n'a atteint le démon |
| **`setTempWWsoll`** | **AUCUNE caractérisation terrain.** Rôle jamais engagé |
| **La forme décimale en vol** | **jamais émise**, donc **jamais observée** |
| **`C1`, la coexistence, `U-2`, `U-3`, `H2`, `H6 (b)`** | **entières** |

---

## 11. Suite donnée

**`I-8` a été levée sur pièces et sur code**, sans terrain — PR **#105**, mergée,
`main` `7f09cb9`. L'adaptateur rend désormais un non-entier par la forme
décimale positionnelle à point, et le rendu entier est **inchangé**.

> **Lever `I-8` n'est pas caractériser `setNeigungM1`.** La forme **n'a jamais
> quitté la machine**. **La prochaine émission décimale demeure une PREMIÈRE au
> sens de `W4-C`**, et exige une **autorisation nouvelle** : celle de la V2 est
> **consommée**.

Le rejeu est porté par **`W4-T1`** — `w4t1-rejeu-pente.md` — et **par lui seul**.

---

## 12. Réserve du présent constat

**Ce document est écrit par la session qui a conduit la campagne.** Il consigne
des faits horodatés et hachés, vérifiables sur les pièces gelées ; **il ne les
homologue pas**. **L'homologation appartient à un tiers**, et **nul n'homologue
ce qu'il a produit**.
