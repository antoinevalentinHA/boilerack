# Arbitrage — activation de `debug` sur le démon `vcontrold`

> **Ce document consigne deux décisions humaines.** Il ne produit aucune analyse
> nouvelle, n'ouvre aucun travail et n'autorise aucune opération.
>
> Il **ne modifie pas** le cadrage `w4-cadrage-activation-debug.md`, qui est gelé
> à l'empreinte SHA-256
> `d09b6bf40c979918140afb41d9c604b620e79565550db899968376b4f8087f75` et dont les
> termes d'intégration réservent toute modification à une version numérotée
> distincte. Les questions `H-1` à `H-12` restent lisibles là-bas, dans leur
> rédaction d'origine.

## Objet

Le cadrage soumet **douze questions d'arbitrage** à l'humain. Deux ont été
tranchées : **`H-2`** et **`H-4`**. Ce document en porte le résultat et les
conséquences, et rien d'autre.

## Fait acquis qui fonde l'arbitrage

Une observation terrain **en lecture seule**, explicitement autorisée, a établi la
configuration réellement chargée par le démon — `/etc/vcontrold/vcontrold.xml`,
avec inclusion XInclude de `vito.xml` — et la définition effective de la commande
sondée pour le périphérique déployé `20CB` :

> **`getTempKist` résout pour `20CB`** — `addr 0802`, `len 2`, `unit UT`,
> `protocmd getaddr`, protocole `P300` ; `UT` est de type `short` avec conversion
> de lecture `V/10`, soit une résolution numérique de **0,1 °C**.

Aucune écriture, aucun rechargement, aucun redémarrage, aucune commande chaudière.

---

## `H-2` — Suffisance : **CLOSE**

**La question de l'activation de `debug` est close pour l'état actuel.**

La lecture a produit le résultat `getTempKist résout pour 20CB`. Ce résultat
**ferme une branche de risque** — celle où la sonde du superviseur aurait été
rejetée avant Optolink faute de résolution, produisant une libération de verrou
non appariée à chaque cycle. Cette branche est écartée.

**Il ne ferme ni `H3` ni `H6`.**

- La **transition 4** du maillon 2 de `H3` est désormais **ÉTABLIE**.
- Les transitions **1, 2, 3 et 5** demeurent **NON ÉTABLIES**.
- **`H3` reste `PARTIELLEMENT RÉDUITE`** ; le maillon 2 reste **NON ÉTABLI**.
- **`H6` reste `RÉDUITE, NON CLOSE`**.
- Un rejet pour un motif **en aval** de la résolution reste **NON ÉTABLI**.
- **`r < 0,485 s` reste `NON PROUVÉ`.**

**Les inconnues résiduelles restent documentées sans déclencher d'instrumentation
supplémentaire.** Elles ne constituent pas, à elles seules, un besoin
d'instrumentation de production.

> **Réouverture.** La question pourra être reposée **uniquement si un contexte
> futur change matériellement les conditions qui ont fondé cet arbitrage**. Le
> présent document ne préjuge pas d'un tel contexte et n'en prépare aucun.

---

## `H-4` — Consommateur : **SUBORDONNÉE**

**Une mutation de production destinée uniquement à réduire une incertitude doit
être justifiée par un travail ouvert qui consomme explicitement la réduction
obtenue.**

**Aucun travail de ce type n'est actuellement ouvert** : `W4-F2` est fermé et non
autorisé, aucun `T0` / `T1` / `T2` n'est ouvert, l'Acte B n'est pas ouvert.

> **Donc aucune activation de `debug` n'est justifiée aujourd'hui.**

Cette subordination est une **règle de justification**, non un jugement sur la
valeur technique de l'instrumentation : elle porte sur ce qui autorise à engager
la production, pas sur ce que l'observation apprendrait.

---

## Conséquences consignées

Pour l'**état courant**, et à ce titre seulement :

| | |
|---|---|
| `H-3` à `H-11` | **NON ARBITRÉES / SANS OBJET À CE STADE** |
| `H-12` | **NON POURSUIVIE** |
| activation de `debug` | **aucune** |
| observation supplémentaire | **aucune** |
| Acte B | **NON OUVERT** |
| `W4-F2` | **FERMÉ / NON AUTORISÉ** |
| `T0` / `T1` / `T2` | **aucun** |
| modification de production | **aucune** |

> **Portée temporelle.** Ces états valent **pour l'état courant**. Ce ne sont pas
> des décisions définitives : ils décrivent ce qui est arbitré et ce qui ne l'est
> pas aujourd'hui, non ce qui le serait à jamais. `H-3` à `H-12` demeurent
> **entières et disponibles** dans le cadrage ; elles sont sans objet, non
> retirées.

---

## État de gouvernance après ces deux arbitrages

`W4-F0`, `W4-F1`, `W4-F1A` : **CLOSED** · Acte A : **CLOSED** · cadrage de
l'activation de `debug` : **CLOSED** · Acte B : **NON OUVERT** · `W4-F2` :
**FERMÉ / NON AUTORISÉ** · aucun `T0` / `T1` / `T2`.

Le **pont historique** demeure l'**unique écrivain réel de production** ; la
**surface transactionnelle** demeure **sans autorité**, `False`.

**État épistémique — inchangé, et non touché par les présents arbitrages** :
`H1`, `H2`, `H3` **PARTIELLEMENT RÉDUITES** (`H3` : maillon 2 **NON ÉTABLI**,
transition 4 exceptée) · `H6` **RÉDUITE, NON CLOSE** · **aucune hypothèse close** ·
régime **`ADDITIF — CONDITIONNEL À H1/H2/H3/H6`** · niveau **`PROUVÉ SOUS
HYPOTHÈSES D'INSTALLATION`** · `U-1` **`PART AMONT ÉTABLIE SOUS H1/H2/H3/H6,
RÉSIDU D'INSTALLATION OUVERT`**, `H3` incluse · `I1` **PARTIELLEMENT RÉDUITE** ·
`r < 0,485 s` **NON PROUVÉ**.

---

## Ce que ce document ne fait pas

Il ne modifie pas le cadrage gelé · il ne clôt ni `H3`, ni `H6`, ni aucune
hypothèse · il ne retire aucune des dix questions non arbitrées · il n'ouvre ni
Acte B, ni `W4-F2`, ni `T0` / `T1` / `T2` · il n'autorise aucune observation,
aucune mutation, aucun redémarrage · il ne prépare aucun travail suivant.
