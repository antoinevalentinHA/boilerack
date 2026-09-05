# `LOT 2B-R V2` — constat d'exécution

> **`LOT 2B-R CONFIRMÉ`, exécution `HOMOLOGUÉE`.**
> **Régime permanent au boot : CONFIRMÉ.**
>
> **Ce document CONSIGNE. Il n'interprète pas, ne protocole rien, n'autorise
> rien.** L'autorisation du 2026-09-05 est **CONSOMMÉE**.
>
> **Il ne régularise RIEN de `LOT 2B V1`** — §8.

---

## 0. Convention

| Nom court | Document |
|---|---|
| `2B-R` | `lot2b-r-reboot.md` — le protocole |
| `2B` | `lot2b-regime-permanent.md` · sa `V1` **exécutée** et **non homologable** |
| `G2-P` | `w4f-g2-ecriture-bornee.md` — référentiel `AB` / `FA`, §12 |
| `w4f` | `w4f-write-sovereignty.md` |

**Aucune constante de site.** Unités désignées `<unité-boilerack>`,
`<unité-pont>`, `<unité-démon>`, `<timer-guard>`.

---

## 1. En une ligne

**2026-09-05, `07:01:22Z` → `07:10:28Z`.** La machine, **laissée à elle-même**,
a **ramené Boilerack** et **n'a pas ramené le pont historique**. Le filet de boot
est **effectivement inversé**.

---

## 2. Les trois pièces — dédiées, et antérieures à l'acte

Atelier créé **vide** à `07:01:22.320Z`, sur stockage persistant, **hors de tout
dépôt versionné**.

| Pièce | Empreinte | Ce qu'elle établit |
|---|---|---|
| **`P-DEP`** | `d6c5401a8f8e441b…` | les **quatre rôles** exposés par le service **installé**, bornes, pas et `confirm_tolerance` · **8 / 8 fichiers de la chaîne de rendu concordants** avec le dépôt intégré · l'**identité de l'unité** et de son drop-in d'exclusion |
| **`P-UFS`** | `afd74d447ade4853…` | `UnitFileState` **et** `ActiveState` des quatre unités, plus l'unité d'exécution du superviseur |
| **`T0`** | `998ea5fd42c18e79…` | neuf rubriques · **souveraineté CONSTATÉE, non présumée** : `<unité-boilerack>` `active`/`enabled`, `<unité-pont>` `inactive`/`disabled`, exclusion effective, autorité ouverte, superviseur `v1.2` ciblant Boilerack, chaîne `ok`, quatre valeurs relevées, empreintes persistées, `MainPID 50809` et `uptime` de référence |

> **`T0` a établi le régime attendu.** C'est à cette seule condition que la
> fenêtre pouvait s'ouvrir.

---

## 3. L'acte — un seul

```
commande     : systemctl reboot
demandé à    : 2026-09-05T07:02:54.360Z
machine revenue : 2026-09-05T07:04:14.314Z      indisponibilité ≈ 80 s
```

**Aucun autre geste.** Aucun fichier modifié, aucune unité réactivée ou
désactivée, aucune autorité touchée.

---

## 4. Les huit constats, sans aucune intervention

| # | Constat | Résultat |
|---|---|---|
| **1** | **Boilerack est revenue seule** | `active`/`running`, **`MainPID 705`** — **différent du `50809`** de `T0` · `NRestarts=0` · active depuis `09:03:18` locale |
| **2** | **le pont n'est PAS revenu** | `inactive`, `dead`, `disabled`, **zéro processus** |
| **3** | l'autorité demeure ouverte | `enabled = true`, empreinte `e442dd0f…` **identique à `T0`** |
| **4** | superviseur `v1.2`, cible Boilerack | cycle **`OnBootSec`** à `07:06:11Z` → **`NOMINAL`**, `last_action none`, **0 action corrective**, version publiée au courtier : **`v1.2`** |
| **5** | chaîne publiée | `{"status":"ok","cause":null}`, **dix mesures, toutes fraîches, toutes en `last_result` nominal** |
| **6** | quatre valeurs chaudière | **inchangées** — identiques à `T0` |
| **7** | aucun second écrivain | 0 processus pont · 1 processus Boilerack · **0 unité en échec** |
| **8** | fichiers persistés | empreintes **identiques à `T0`** |

> **Le constat 2 est le cœur du lot.** C'est lui qui établit l'inversion du filet
> de boot — la conséquence que `2B` §8 déclarait et que `2B V1` n'avait pas
> éprouvée.
>
> **Le constat 1 exige un `MainPID` différent**, et il l'est : un processus
> inchangé aurait prouvé que le redémarrage n'avait pas eu lieu.

---

## 5. Marge de sonde, re-mesurée en régime permanent — lecture seule

Dix invocations de la sonde du superviseur, **aucune écriture**.

| | Moyenne | **Maximum** | **Marge sur 5 000 ms** |
|---|---|---|---|
| **Régime permanent Boilerack, après boot** | **2 154 ms** | **2 207 ms** | **2 793 ms** |
| Banc du 2026-09-04, Boilerack seul | 2 292 ms | 3 189 ms | 1 811 ms |
| Banc du 2026-09-04, pont historique seul | 2 527 ms | 4 261 ms | **739 ms** |

**Zéro échec sur dix.** La marge est **la meilleure des trois mesures**.

> **Aucun seuil n'est déclaré, et `FA-9` n'est pas levée** : dix invocations ne
> sont pas une distribution.

---

## 6. Les vingt-et-un critères — prononcés **dans la fenêtre**

Prononcé à `07:09:59.330Z`, référentiel `G2-P` §12 adopté intégralement.

| Mention | Nombre | Critères |
|---|---|---|
| **`ATTEINT`** | **1** | **`AB-5`** |
| **`NON ATTEINT`** | **9** | `FA-3`, `FA-4`, `FA-8`, `FA-9`, `FA-12`, `AB-3`, `AB-4`, `AB-6`, `AB-7` |
| **`SANS OBJET`** | **11** | `FA-1`, `FA-2`, `FA-5`, `FA-6`, `FA-7`, `FA-10`, `FA-11`, `AB-1`, `AB-2`, `AB-8`, `AB-9` |

> **`SANS OBJET` n'est pas une commodité.** `2B-R` n'écrit pas : les critères qui
> présupposent une écriture, une relecture d'écriture ou un `ACK` **ne sont pas
> « non atteints », ils sont hors de leur domaine** — et chacun porte son motif.

### 6.1 `AB-5` — atteint par construction, levé par l'humain

**`AB-5`** — *« un service redémarre, ou la machine redémarre, **pour quelque
cause** »* — est **`ATTEINT`**, et il l'était **avant même l'acte** : l'acte
unique du lot **est** un redémarrage machine, qui emporte aussi le redémarrage de
Boilerack et du démon.

> **Le lot ne s'est pas auto-exempté.** Il a **prononcé `ATTEINT`**, et
> l'**autorisation propriétaire du 2026-09-05 l'a écarté nommément**, pour ce
> redémarrage volontaire unique et pour lui seul.

### 6.2 `FA-4` et `AB-3` — une lecture soumise, puis arbitrée

**Le démon a bien été indisponible et a changé d'état** : il s'est arrêté et a
redémarré **avec la machine**, environ 80 secondes. **Lus à la lettre, `FA-4` —
démon injoignable ou changeant d'état — et `AB-3` seraient réalisés.**

La session a prononcé **`NON ATTEINT`** et a **déclaré sa lecture au lieu de la
taire** :

- l'indisponibilité est la conséquence **directe et entière** de l'acte autorisé ;
- le critère qui nomme exactement ce fait est **`AB-5`**, prononcé `ATTEINT` puis
  écarté par l'humain ;
- `FA-4` et `AB-3` visent une condition **anormale** du démon — injoignable hors
  acte, ou instable — alors qu'il est actif et a répondu **dix fois sur dix**.

> **L'arbitrage n'appartenait pas à la session, et elle ne se l'est pas
> accordé.** Elle a écrit que, sous la lecture littérale, ces deux critères
> exigeraient la **même exception nommée** qu'`AB-5` — que l'autorisation ne
> portait pas — et que le verdict deviendrait alors `ABANDONNÉ`.
>
> **L'audit indépendant a tranché : `FA-4` et `AB-3` sont homologués
> `NON ATTEINT`.**

---

## 7. État final

```
<unité-boilerack>   active    enabled      MainPID 705, NRestarts=0
<unité-pont>        inactive  disabled     zéro processus
<unité-démon>       active    enabled
<timer-guard>       active    enabled      NOMINAL, 0 action corrective
exclusion mutuelle  armée     autorité persistée : enabled = true
unités en échec     0
```

**Quatre valeurs chaudière inchangées.** **Zéro écriture, zéro ordre métier,
zéro modification persistante** — les quatre empreintes de fichiers persistés
sont **identiques à `T0`**.

**Artefacts** : **8 pièces**, `sha256sum -c` **8 / 8**, vérifié **après
rapatriement hors machine**. Manifeste
`ab17de8807eb4fdc538563afdc84c7d4dba8065479ea9644b623887ca3d012fd`. Les pièces
sont **hors dépôt** ; le dépôt n'en porte que les empreintes.

---

## 8. Ce que ce constat n'établit pas

> ### **`LOT 2B V1` demeure `NON HOMOLOGUABLE STRICTEMENT`.**
>
> **`2B-R` ne le régularise pas, et il ne le pourra jamais.** Sa preuve est
> **postérieure** : elle sert la **substance** du `2B` §10.4 — le filet est
> inversé — **jamais sa chronologie**. Le `§10.0 P-DEP` et le `§10.9` manquent
> définitivement à `V1`.

**Demeurent également ouverts** : l'**anomalie `C-acte-5`** de `2B V1`, **non
résolue** et non traitée ici · **`FA-9`**, non levée · l'**escalade du
superviseur**, inchangée — une panne prolongée du démon conduirait toujours à
redémarrer un service puis **la machine** · **Arsenal**, privé de la surface
historique, son recâblage demeurant **atomique avec une décision ultérieure** ·
**`I-ECS`**, le régime `B`, l'**unité de `getBrennerStatus`**, **`C1`**, la
coexistence, **`U-2`**, **`U-3`**, **`H2`**, **`H6 (b)`**.

---

## 9. Réserve conservée, non bloquante

**Le commentaire du fichier de configuration dit encore *« autorité d'écriture —
FERMÉE, explicitement »* alors que la clé porte `enabled = true`.**

Le commentaire est **historique** : il date du dépôt du fichier en régime de
lecture seule et n'a jamais été révisé. **La clé fait foi, le commentaire non**,
et toutes les pièces des campagnes l'ont relevée sur le **contenu du fichier**.

> **Il n'est PAS corrigé dans ce lot**, sur instruction. La contradiction est
> **consignée**, et elle appelle une correction dans un lot qui aura le droit de
> toucher au fichier.

---

## 10. Réserve du présent constat

**Écrit par la session qui a conduit la campagne.** Il consigne des faits
horodatés et hachés ; **il ne les homologue pas**. **L'homologation a été
prononcée séparément** — `GO — LOT 2B-R HOMOLOGUÉ : RÉGIME PERMANENT AU BOOT
CONFIRMÉ` — et **nul n'homologue ce qu'il a produit**.
