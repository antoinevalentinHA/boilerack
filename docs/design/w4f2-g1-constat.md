# Constat `G.1` — empreinte du fichier de commandes déployé

> **Version 2**, après audit. Une correction, au §3 : l'ordre d'exécution des
> lectures y était attribué à une exigence du §15 de
> `w4f2-vito-xml-instruction.md`, **qui n'en porte aucune** — sa liste énonce
> même les deux lectures dans l'ordre inverse. L'ordre réellement exécuté est
> conservé, et fondé pour ce qu'il est : un **choix de méthode**, appuyé sur le
> §10, terme 1. **Aucun autre changement de fond.**
>
> **Version 1.** Lot documentaire `W4-F2`. Il consigne un acte `G.1` **borné**,
> exécuté sur l'installation après **autorisation humaine explicite**, et défini
> par `w4f2-vito-xml-instruction.md` §15. Quatre lectures, aucune autre. Aucun
> runtime, aucun `vclient`, aucun service, aucune mutation, aucune commande
> chaudière.

---

## 1. Objet et frontières

Ce document consigne **ce qui a été lu et ce que cela établit**, et rien de plus.
Il n'élargit pas l'acte, n'en propose pas d'autre, n'amende aucun contrat, ne
rouvre aucun arbitrage clos, et n'ouvre ni `Acte B`, ni `T0` / `T1` / `T2`.

**Précondition 9 / §11.2 demeure `NON DONNÉE`.**

---

## 2. Autorisation et bornes de l'acte

L'acte proposé par `w4f2-vito-xml-instruction.md` §15 — **proposé, non autorisé**
à la clôture de ce lot — a fait l'objet d'une **autorisation humaine explicite**
et **bornée à ces seules lectures**.

**Ce que l'acte ne comportait pas**, et n'a pas comporté : aucune lecture
intégrale du fichier de configuration · aucun journal · aucun descripteur, `ps`
ni `/proc` · aucun `systemctl`, `restart` ni `reload` · aucun `vclient` · aucune
écriture · aucun `debug` · aucune commande chaudière.

---

## 3. Les quatre lectures, telles qu'exécutées

Dans cet ordre — lecture de l'inclusion **avant** l'empreinte.

> **Cet ordre est un choix de méthode, non une prescription reçue.** Le §15 de
> `w4f2-vito-xml-instruction.md` n'impose **aucun ordre** : il énumère même les
> deux lectures dans l'ordre inverse, l'empreinte en **(i)** et la lecture ciblée
> en **(ii)**. Ce constat ne lui attribue donc rien.
>
> **Ce qui le fonde est le §10, terme 1**, qui exige *« une comparaison
> d'intégrité entre le `vito.xml` déployé et l'amont …, **plus la vérification que
> la configuration chargée inclut bien ce fichier** »*. Les deux lectures étant
> requises l'une et l'autre, les faire dans cet ordre évite de relever une
> empreinte avant de savoir sur quel fichier elle doit porter. **C'est une
> commodité de méthode ; le résultat ne dépend pas de l'ordre**, les quatre
> lectures étant sans effet l'une sur l'autre.

| # | Lecture | Résultat |
|---|---|---|
| 1 | élément d'inclusion du `vcontrold.xml` déployé | ligne **449** : `<xi:include href="vito.xml" parse="xml"/>` |
| 2 | élément de périphérique par défaut du même fichier | ligne **24** : `<device ID="20CB"/>` |
| 3 | présence et taille du fichier de commandes désigné | présent au chemin résolu · **56 083 o** |
| 4 | empreinte de ce fichier | SHA-256 **`34808e1f08256ce15e7f81b6b27623866a596de562e6f7232198fa0b41b22f89`** |

**Aucune autre lecture n'a été faite**, sur ce fichier comme sur l'installation.

---

## 4. Résolution du chemin réellement inclus

`href="vito.xml"` est un chemin **relatif**. Il se résout depuis le répertoire du
document incluant — `/etc/vcontrold/` — soit `/etc/vcontrold/vito.xml`.

**Cette résolution n'a pas été supposée** : la lecture 3 a constaté la présence
du fichier au chemin résolu, et les lectures 3 et 4 portent sur lui.

---

## 5. Comparaison à l'amont `8ca47972…`

| | Amont | Déployé | |
|---|---|---|---|
| `xi:include` | `href="vito.xml" parse="xml"` | idem | **concordant** |
| Périphérique par défaut | `<device ID="20CB"/>` | idem | **concordant** |
| SHA-256 de `vito.xml` | `34808e1f…41b22f89` | `34808e1f…41b22f89` | **IDENTIQUE** |
| Taille de `vito.xml` | 56 083 o | 56 083 o | **identique** |

> **Le `vito.xml` déployé est, octet pour octet, celui de l'amont caractérisé.**
> C'est le fait central de ce constat, et il se lit sans interprétation : deux
> empreintes SHA-256 égales sur des fichiers de même taille.

---

## 6. Conséquence sur `H6`

La prémisse conditionnelle de `w4f2-vito-xml-instruction.md` §9 — *si* le fichier
de commandes déployé est celui de l'amont, *alors* les treize commandes résolvent
— **est levée**. Les treize commandes du pont **résolvent pour `20CB` sur
l'installation**.

| Résidu | État |
|---|---|
| **(a)** terme **1** — résolution sur l'installation | **FERMÉ.** La comparaison d'intégrité qu'il exigeait est faite, et concordante |
| **(a)** terme **2** — conformité du pont déployé au contrat `A5` | **OUVERT.** Cet acte ne l'approchait pas, et ne l'a pas approché |
| **(b)** — participant extérieur sur l'IPC System V | **inchangé** — c'est `H2` |
| **(c)** — cas « commande non résolue » | **ÉCARTÉ sur l'installation**, et non plus seulement sur l'amont |
| **(c)** — autres chemins de sortie précoce | **inchangés** |

> **`H6` reste `PARTIEL`** — constat `RÉDUITE, NON CLOSE`. Un terme fermé et un
> cas écarté ne déchargent pas l'hypothèse tant que **(b)** et les autres chemins
> de **(c)** demeurent.

---

## 7. Ce qui n'a pas bougé

| Objet | Pourquoi cet acte ne pouvait rien y faire |
|---|---|
| **maillon 2** — transitions **1** et **2** | faits d'**exécution du superviseur**. Une empreinte de fichier n'établit pas qu'une machine exécute. **Inchangé** |
| `H3` | son résidu **est** ce maillon 2. **Inchangé** |
| `H1` | porte sur le lien **binaire ↔ arbre à la compilation**. Un fichier lu à l'exécution n'y touche pas |
| `H2` | porte sur l'existence d'un **autre ouvreur de la liaison**. Rien n'en a été lu |
| `U-2`, `U-7` | aucune durée n'a été mesurée. `borne_sonde` et `seuil_C1` demeurent **non calculables** |

---

## 8. Régime — `INDÉTERMINÉ`, inchangé

| | |
|---|---|
| Niveau épistémique | `PROUVÉ SOUS HYPOTHÈSES D'INSTALLATION` — valeur `ADDITIF — CONDITIONNEL À H1/H2/H3/H6` |
| **Régime opératoire** | **`INDÉTERMINÉ`** → branche **C** → **`W4-F2 NON QUALIFIABLE — STOP`** |

`ADDITIF` exige la preuve explicite de **chacun** des six maillons — *« un seul
manquant donne `INDÉTERMINÉ` »*. **Le maillon 2 manque**, et cet acte ne pouvait
pas le fournir. `NON ADDITIF` exige une **preuve positive sur la population
protégée** ; il n'en a été produit aucune.

**Aucune conclusion par défaut n'est émise.**

**Précondition 9 / §11.2 demeure `NON DONNÉE`.** Le pont historique demeure
l'unique écrivain réel de production ; la surface transactionnelle demeure sans
autorité, `false`.

---

## 9. Ce que ce document ne fait pas

Il ne tranche aucun régime · il n'émet aucune conclusion par défaut · il ne crée
aucune hypothèse, aucun seuil, aucune constante · il ne modifie aucun contrat ·
il n'élargit pas l'acte autorisé et n'en propose aucun autre · il ne consigne
aucune valeur d'installation autre que celles nommées au §3 · il n'ouvre ni Acte
B, ni `T0` / `T1` / `T2` · il n'autorise aucune lecture nouvelle, aucune
inspection de journal, aucune mutation, aucun `debug`.

---

## 10. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Constat initial de l'acte `G.1` borné, autorisé et exécuté |
| **2** | Audit : §3, retrait de l'attribution d'une exigence d'ordre au §15, qui n'en porte pas. Ordre exécuté conservé et fondé comme choix de méthode sur le §10, terme 1. Aucun autre changement de fond |
