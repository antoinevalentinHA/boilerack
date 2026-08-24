# W4-F — Souveraineté d'écriture : cadrage et décomposition

> **Lot W4-F — document d'OUVERTURE. Version 2**, après audit indépendant de la
> V1. La V2 corrige deux majeurs — la clause dominante interdisait littéralement
> le terrain de lecture qu'elle ordonne (§11), et W4-F2 n'était pas gouvernable
> sans W4-F3 (§10.3) — et quatre mineurs : le partage `timeout` / ABORT (§8.1),
> le reboot capable de recréer deux écrivains (§7.2.1), trois `MUST` inversés, et
> une analyse des budgets qui simplifiait la sémantique réelle de `_confirm`
> (§4.2). L'architecture générale est **inchangée**.
>
> Ce document n'autorise aucune écriture réelle, ne prescrit aucune campagne, et
> ne neutralise aucun service. Il établit ce que le dépôt prouve, ce qu'il ne
> prouve pas, et la décomposition minimale sûre du chantier. Il ne livre aucune
> ligne de code et ne modifie aucun test.
>
> **W4-E est clos** (PR #46, PR #47). Sa clôture rend W4-F *admissible* ; elle ne
> l'ouvre pas. Le pont historique reste **l'unique écrivain réel de production**.

---

## 1. Objet

W4-F est le lot qui doit établir la **souveraineté réelle d'écriture** de
Boilerack sur l'installation de référence.

> **Ce que W4-F n'est pas.** W4-F n'est **pas** l'action de porter
> `[transaction_surface].enabled` à `true`. Cette clé n'accorde que la
> **composition** de la voie (W4-E1 §7.2, §15). Un interrupteur fermé livré
> n'est pas un interrupteur ouvert, et un interrupteur ouvert n'est pas une
> souveraineté.

La transition à établir, dans cet ordre :

```
pont historique écrivain
      ↓  neutralisation PROUVÉE
zéro écrivain, ou écrivain explicitement maîtrisé
      ↓  autorisation humaine explicite
Boilerack autorisé
      ↓  commande MQTT supervisée
Boilerack → vclient → transport → relecture souveraine → ACK métier
```

**Invariant absolu, qui domine tout le lot :**

> À tout instant où une écriture réelle est possible : `writers_actifs <= 1`.

---

## 2. Convention — constantes de site

`provenance.md` exclut les hôtes, ports, chemins absolus et unités systemd. Ce
document reprend **à l'identique** les marqueurs de W4-C §4, afin qu'un même rôle
ne porte pas deux noms dans un même dépôt.

| Marqueur | Rôle |
|---|---|
| `<hôte>` / `<port>` | point de contact du démon `vcontrold` |
| `<unité-pont>` | unité systemd du pont historique |
| `<timer-guard>` | timer systemd du superviseur local |
| `<unité-boilerack>` | unité systemd de Boilerack, **non installée à ce jour** (§4.1) |

---

## 3. Acquis — ce que le dépôt prouve réellement

### 3.1 Le transport, caractérisé sur le terrain

W4-C a exécuté une écriture réelle supervisée le **22 août 2026**. Faits
contractuels, non rediscutables ici :

| Fait | Conséquence pour W4-F |
|---|---|
| `raw == "OK"` est un statut de **transport** | ne vaut jamais `applied` |
| `value == 0.000000` n'est **pas** la valeur écrite | ne doit jamais être consultée |
| la **relecture est souveraine** | seule source du verdict métier |
| une seule écriture nominale, **aucun réessai** | W4-F n'en introduit aucun |
| durée d'écriture mesurée : **1,045 s** | budget d'écriture de 5 s confirmé |
| le pont historique écrit par `vclient` en sous-processus (E1) | même transport ; l'expérience transfère |

### 3.2 La chaîne logicielle, déjà conforme

Le cœur transactionnel implémente **déjà** les invariants F3, F4 et F7. Vérifié
dans `src/boilerack/core/engine.py` :

- `_run_transaction` — « **Une SEULE invocation d'ecriture par transaction,
  jamais de retry.** »
- frontière typée `_PROVEN_NOT_EMITTED` : seul `DAEMON_UNREACHABLE` prouve la
  non-émission ; **tout autre statut, connu ou imprévu, déclenche une relecture**
  plutôt que de prétendre l'absence d'écriture ;
- `_confirm` — `applied` **uniquement** si une relecture confirme, sinon
  `timeout` au bout du budget.

> **Conséquence.** W4-F **n'a aucune raison** de modifier le contrat
> transactionnel. Les quatre états `accepted` / `applied` / `rejected` /
> `timeout` couvrent la campagne. Toute proposition d'état nouveau devra être
> justifiée par une impossibilité démontrée, jamais par le confort.

### 3.3 La méthode one-writer, déjà écrite et déjà éprouvée

W4-C §8, §8.1, §9 et §9.1 contiennent un protocole de neutralisation complet,
appliqué avec succès. W4-F **hérite** de cette méthode ; il ne la réinvente pas.
Les trois règles qui ont coûté le plus cher à établir :

> **Arrêter le timer ne suffit pas.** Le superviseur s'exécute dans une unité
> distincte. Un cycle déjà engagé dort 90 s avant de re-sonder et conserve
> pendant toute cette attente le pouvoir de **redémarrer la machine**.
> Neutralisé signifie **timer inactif ET unité d'exécution inactive** (W4-C
> §8.1).

> **Le journal du démon ne prouve rien pour le superviseur.** Un cycle en attente
> interne n'ouvre aucune connexion : son absence du journal est exactement ce
> qu'on observerait dans le cas le plus dangereux. **PR-1 repose uniquement sur
> l'état des unités** (W4-C §9.1).

> **La sortie standard du pont ne prouve rien.** Elle est mise en tampon : des
> lignes anciennes peuvent recevoir un horodatage postérieur à l'instant
> qu'elles décrivent (W4-C §9.1).

Les deux preuves d'arrêt **PR-1** (superviseur) et **PR-2** (pont) sont reprises
telles quelles par W4-F.

---

## 4. Ce que W4-F **ne peut pas** supposer

Trois constats, tous établis par lecture du dépôt, invalident l'idée d'un W4-F en
un seul lot.

### 4.1 Boilerack n'a **jamais** été installé ni qualifié sur le terrain

C12 §30 : « **C12 ne prétend pas que Boilerack est installé, ni qualifié sur le
terrain.** » C13 : « **C13 ne prétend à aucune qualification terrain.** Aucune
machine cible n'est [touchée]. » Le `README` : « Ce qui suit décrit l'interface,
pas une mise en production validée. »

`systemd/boilerack.service` est un **gabarit versionné**, explicitement « pas une
unité installée », et `install.py` ne lance « **AUCUN `systemctl`, DANS AUCUN
MODE** ».

> **Conséquence.** La chaîne visée au §1 présuppose un Boilerack **qui tourne**
> sur la machine, connecté au broker, capable de lire par `vclient`. Rien de cela
> n'a jamais eu lieu. Ce n'est pas un détail d'exécution : c'est un lot entier,
> et il est **antérieur** à toute question de souveraineté.

### 4.2 La fenêtre de confirmation n'est pas le budget nominal — **hypothèse de concluance à mesurer**

Quatre constantes gouvernent la confirmation, et elles ne sont ni de même nature
ni également réglables.

| Constante | Valeur | Rôle | Réglable ? |
|---|---|---|---|
| `confirm_budget_s` | **5,0 s** | échéance de la boucle de relecture | **non** depuis la composition — voir ci-dessous |
| `confirm_interval_s` | 0,5 s | attente entre deux relectures | **non**, idem |
| `read_timeout_s` | **5,0 s** | **plafond par relecture**, appliqué au sous-processus | **oui** — clé publique C10, table `[vclient]` |
| coût réel d'une relecture | **2,7 à 4,0 s** sous contention | observé | — |
| délai de propagation après changement réel (I-7) | **non mesuré** | — | — |
| budget du dispositif historique | 10 s, après 1 s d'attente initiale | W4-C E4 | — |

`build_transaction_surface` **n'expose ni** `confirm_budget_s` **ni**
`confirm_interval_s` : le constructeur du cœur les accepte, la composition que
`lifecycle` réalise ne les transmet pas. Vérifié sur la signature réelle.
`read_timeout_s`, lui, est une **clé publique** et traverse déjà la
configuration.

#### 4.2.1 La sémantique réelle de `_confirm`

L'échéance est testée **après** chaque relecture, jamais avant. Trois
conséquences, toutes vérifiables dans `src/boilerack/core/engine.py` :

1. **au moins une relecture a toujours lieu**, quelle que soit sa durée ;
2. une relecture entamée avant l'échéance **va jusqu'à son terme**, et si elle
   confirme, `applied` est émis — **même après** l'échéance nominale ;
3. la fenêtre d'observation effective n'est donc pas `confirm_budget_s`, mais
   **strictement inférieure à `confirm_budget_s + confirm_interval_s +
   read_timeout_s`**, soit **10,5 s** avec les valeurs actuelles.

Le nombre de relectures dépend du régime de coût, et varie fortement :

| Coût par relecture | Relectures | Fenêtre effective |
|---|---:|---:|
| 0,3 s — sans contention | 7 | 5,1 s |
| 2,7 s — contention basse | 2 | 5,9 s |
| 4,0 s — contention haute | 2 | 8,5 s |
| 5,0 s — plafond `read_timeout_s` atteint | 1 | 5,0 s |

> **Rectification.** Il serait faux d'écrire que le budget est « trop court par
> construction ». La fenêtre effective sous contention haute — **8,5 s**, et
> jusqu'à 10,5 s en borne stricte — est du même ordre que les **10 s** que le
> dispositif historique a jugés suffisants. Ce qui est en revanche établi, c'est
> que **la fenêtre effective diffère du budget nominal**, qu'elle dépend d'un
> régime de contention non encore mesuré, et que la constante qui la borne par le
> haut n'est pas celle qu'on croirait.

> **Ce qu'il reste donc à trancher.** Non pas « le budget est-il trop court »,
> mais : quelle fenêtre effective l'installation présente réellement, face à quel
> délai de propagation. C'est une **hypothèse de concluance**, à mesurer et à
> arbitrer par **W4-F1** (§10.2), pas un fait acquis.

> **Aucun risque pour la chaudière, dans tous les cas.** Une fenêtre épuisée
> produit `timeout`, verdict terminal légitime, et F4 interdit toute seconde
> écriture. L'enjeu est **épistémique** : une campagne dont la fenêtre rend
> `applied` improbable ne prouverait pas la chaîne, seulement son expiration.

> **Chicanerie à nommer, parce qu'elle est réelle.** I-7 ne peut pas être mesurée
> *avant* la première écriture réelle, une écriture à l'identique ne propageant
> rien (W4-C §6, §16.6). La première écriture W4-F **est** la mesure de I-7. La
> campagne doit donc traiter `timeout` comme une **issue attendue et non
> fautive**, et mesurer la propagation par observation ultérieure.

### 4.3 Boilerack ajouterait un **troisième** client au démon

La surface de lecture v1 déclare **huit** mesures, une invocation `vclient`
chacune — C6 n'accepte qu'une commande par invocation — soit environ **onze
invocations par minute** (trois à 30 s, cinq à 60 s).

S'y ajoutent, sur la même liaison Optolink série :

- le pont historique, qui sonde **toutes les 10 s** (W4-C §9, étape 6) ;
- le superviseur, qui sonde **toutes les 3 minutes** avec un budget de **5 s** et
  qui, après **deux** sondes en échec, **redémarre la machine** (W4-C §8).

W4-C qualifiait déjà de « contention non maîtrisée » le simple fait de laisser le
pont tourner pendant une mesure.

> **Conséquence.** Faire tourner Boilerack *à côté* du pont historique n'est pas
> une étape neutre : c'est une modification de la charge sur un chemin qui
> commande un redémarrage machine. Elle doit être **qualifiée pour elle-même**,
> avant toute question d'écriture.

---

## 5. Les quatre autorités — distinctes, et déjà partiellement livrées

L'audit devait déterminer quelles autorités existent. Elles sont quatre, et
**trois sont déjà en place**. Aucun mécanisme nouveau n'est à créer.

| # | Autorité | Porteur | État |
|---|---|---|---|
| A1 | **composer** la voie | `[transaction_surface].enabled`, lu par `lifecycle` seul | **livrée** (W4-E2) |
| A2 | **recevoir** une commande | souscription à `<prefix>/command`, effectuée par la surface composée | **livrée** — conséquence de A1 |
| A3 | **tenter** une écriture | validation C3 : rôle connu, `writable`, bornes, pas, non expirée | **livrée** (W4-D, cœur) |
| A4 | **souveraineté one-writer** réelle | **opérationnelle** : état des unités systemd sur la machine | **absente du logiciel, et doit le rester** |

> **Clause.** A4 **MUST NOT** être implémentée en logiciel. W4-E1 §8.5 l'interdit
> déjà : « W4-E **MUST NOT** créer verrou distribué, bail, protocole de
> propriété, battement de souveraineté, ni aucun mécanisme que le pont historique
> ne respecterait pas. **Une garantie que l'autre partie ignore n'est pas une
> garantie.** » Le pont historique n'a aucune connaissance de Boilerack : toute
> exclusion logicielle serait une fiction. A4 est **prouvée par l'état des
> services**, jamais par du code.

A2 n'est pas une autorité indépendante : elle découle de A1. Créer une clé
distincte « droit de recevoir » serait un mécanisme de confort, et §5 du cahier
des charges l'interdit explicitement. **Aucun nouvel helper n'est proposé.**

---

## 6. Chaîne transactionnelle et autorité rencontrée à chaque étape

Les étapes **MUST** rester distinctes dans toute preuve W4-F. Fusionner transport
et résultat métier est la faute que W4-C a coûté cher à écarter.

| # | Étape | Autorité franchie | Observable | Verdict possible |
|---|---|---|---|---|
| 1 | commande publiée sur `<prefix>/command` | — | trace broker | — |
| 2 | reçue par la surface composée | A1, A2 | `intake` | — |
| 3 | validée | A3 | — | `rejected` (+ `Reason`) |
| 4 | admise | dédup, file bornée | ACK `accepted` | `rejected` si file pleine / expirée |
| 5 | **invocation `vclient`** — unique | A4 **opérationnelle** | capture | — |
| 6 | statut de transport | — | `TransportStatus` | `rejected/bridge_unavailable` **si et seulement si** `DAEMON_UNREACHABLE` |
| 7 | **relecture souveraine** | — | `getNiveauM1` | — |
| 8 | comparaison métier, tolérance **0** | profil W4-D | — | `applied` si égalité exacte |
| 9 | budget épuisé sans confirmation | — | — | `timeout` |
| 10 | ACK terminal publié sur `<prefix>/ack/<role>` | — | trace broker | — |

> **Trois équivalences interdites.** `accepted` ≠ écrit. Transport `OK` ≠
> `applied`. Doute ≠ succès. Un `timeout` **MUST** être rapporté comme
> `timeout` — jamais requalifié après coup par une relecture manuelle
> favorable.

Le rôle est **`heating_curve_shift`, et lui seul** : `getNiveauM1` /
`setNiveauM1`, `INTEGER`, bornes `[-13 ; 40]`, pas `1`, tolérance `0`,
idempotent. W4-F **MUST NOT** en ajouter (F10).

---

## 7. Rollback — analyse, pas prescription

W4-C a explicitement **légué** cette question :

> « Prescrire "restaurer `V_canon`" sans condition serait pire qu'inutile : face à
> une valeur qui a bougé toute seule, cela ferait **écraser un changement que la
> campagne n'a pas causé** — exactement ce que §11.1 identifie comme le signe
> d'un autre écrivain, et **que W4-F seul a autorité pour traiter**. » — W4-C
> §12.1

### 7.1 Deux rollbacks, à ne pas confondre

| | Rollback **de souveraineté** | Rollback **de valeur** |
|---|---|---|
| objet | retirer à Boilerack la capacité d'écrire, rendre le pont écrivain | ramener le datapoint à sa valeur d'avant |
| moyen | `enabled = false` + arrêt de `<unité-boilerack>` ; puis `<unité-pont>` et `<timer-guard>` rétablis | **une seconde écriture réelle** |
| obligatoire ? | **oui**, toujours | **non** — voir §7.3 |
| preuve de sortie | pont redevenu **unique** écrivain, et **publiant** de nouveau | relecture concordante |

Les confondre serait grave : le premier est un retour à l'état nominal, le second
est **une écriture chaudière de plus**, soumise aux mêmes contraintes que la
première — one-writer, chaîne complète, aucun réessai.

### 7.2 Le rollback de souveraineté ne dépend pas de Boilerack

Point à vérifier explicitement pendant la conception du protocole : le retour au
pont historique **MUST** rester possible même si Boilerack est en échec, figé, ou
injoignable. Les dépendances identifiées à ce stade sont toutes **externes au
logiciel** — état des unités systemd, et le recours physique que W4-C §9 étape 3
décrit déjà : « les unités concernées étant activées au démarrage, un redémarrage
de la machine restaure l'état nominal des services ».

Ce recours est un **filet connu d'avance**, jamais une étape du protocole.

#### 7.2.1 Le reboot peut **recréer** deux écrivains — risque nommé

Ce filet, tel que W4-C l'énonce, restaure l'état nominal **de tous les services
activés au démarrage**. Après W4-F2, Boilerack en fera partie. Si son unité est
activée au boot **et** que la configuration persistée porte encore
`[transaction_surface].enabled = true`, alors un reboot de rollback relance
**simultanément** le pont historique et un Boilerack **capable d'écrire**.

Le filet censé rétablir l'unicité produirait exactement ce qu'il doit empêcher.

> **Règle normative.** Un redémarrage machine **MUST NOT** être considéré comme
> un mécanisme de rollback de souveraineté tant qu'il n'est pas **prouvé** qu'au
> redémarrage le pont historique peut revenir **sans que Boilerack retrouve
> simultanément une capacité d'écriture**.

W4-F3 **MUST** figer une garde satisfaisant cette règle. Au moins l'une des
familles suivantes, sans qu'aucune commande de site ne soit choisie ici :

| Famille | Principe |
|---|---|
| **G-a** | `<unité-boilerack>` **non activée au démarrage** pendant toute la campagne d'écriture |
| **G-b** | configuration **persistée** avec `[transaction_surface].enabled = false` **avant** tout recours au reboot |
| **G-c** | mécanisme opérationnel équivalent, **prouvé avant le terrain** |

> **G-b appelle une vigilance particulière.** L'autorité est lue au démarrage du
> processus (W4-E2) : une valeur persistée à `false` suffit donc à fermer la
> voie au reboot. Mais elle ne vaut que si le fichier a **réellement** été
> réécrit, et non seulement l'autorité levée en mémoire. La preuve porte sur le
> **contenu persisté**, jamais sur l'état courant du processus.

Le choix entre G-a, G-b et G-c, et les commandes qui l'appliquent, sont
**`PREUVE TERRAIN / SOURCE EXTERNE REQUISE`** (§12.1).

### 7.3 Faut-il restaurer la valeur ? Analyse

Ne pas supposer que oui. Trois cas, et ils ne se traitent pas de la même façon.

| Cas | Analyse | Proposition |
|---|---|---|
| l'écriture n'a **pas** eu lieu | rien à restaurer ; restaurer serait écrire sans avoir caractérisé | **aucune écriture**, comme W4-C §12.1 |
| l'écriture a eu lieu, relecture **concordante** avec la cible — verdict `applied` | l'installation est dans un état **connu, borné, conforme au rôle** | restauration **facultative** — décision humaine, pas automatisme |
| l'écriture a eu lieu, **fenêtre de confirmation épuisée sans autre information** — verdict `timeout` **nominal** | l'état est **indéterminé**, ce qui n'est pas la même chose que non maîtrisé | **aucune écriture supplémentaire** ; établir l'état par observation, puis §8.1 |
| l'écriture a eu lieu, relecture ultérieure **explicitement discordante**, ou état changeant, ou autre critère `FA` déclenché | état **non maîtrisé** | **ABORT** (§8.2), aucune écriture supplémentaire, décision humaine |

> **Distinction portante, et elle n'est pas verbale.** *Indéterminé* signifie
> « la fenêtre n'a pas suffi à conclure » ; *non maîtrisé* signifie « une
> observation contredit ce qui était attendu ». Le premier est un manque
> d'information, le second une information défavorable. Les confondre ferait
> déclencher un ABORT sur l'issue la plus probable de la campagne (§4.2), ou
> — bien pire — ferait traiter une discordance réelle comme une simple attente
> trop courte. Le partage est fixé au **§8.1**.

> **Pourquoi la restauration n'est pas due dans le cas nominal.**
> `heating_curve_shift` est un décalage de courbe de chauffe, entier, borné et
> `idempotent`. Une valeur voisine, dans les bornes, choisie réversible (F9),
> laisse l'installation dans un état sûr. Restaurer serait une **seconde
> écriture réelle** — donc un risque supplémentaire — pour un bénéfice de
> confort. L'arbitrage appartient à l'humain, et le protocole terrain devra
> l'exposer comme tel plutôt que le trancher d'avance.

> **Ce qui est en revanche dû.** La commande de restauration **MUST** être
> **armée et écrite par avance**, sur le modèle de W4-C §12 : relever la valeur,
> en dériver la forme canonique, et **recopier** la commande le moment venu
> plutôt que de la reconstruire sous pression. Armer n'est pas exécuter.

---

## 8. ABORT

W4-F hérite des critères W4-C `AB-1` à `AB-9` et doit y ajouter ceux que sa
propre chaîne introduit. Liste de travail, à figer dans le protocole terrain :

| Réf | Déclencheur |
|---|---|
| **FA-1** | impossibilité de prouver la neutralisation du superviseur (**PR-1**) |
| **FA-2** | impossibilité de prouver l'arrêt du pont (**PR-2**) |
| **FA-3** | preuve **ou suspicion** d'un second écrivain — toute valeur qui bouge sans commande émise |
| **FA-4** | démon `vcontrold` injoignable ou changeant d'état |
| **FA-5** | réponse de transport anormale ou non caractérisée |
| **FA-6** | relecture absente |
| **FA-7** | relecture discordante après écriture |
| **FA-8** | redémarrage inattendu d'un service ou de la machine |
| **FA-9** | perte de la connectivité utile à l'observation |
| **FA-10** | ACK incohérent avec l'observation directe |
| **FA-11** | impossibilité de prouver le rollback de souveraineté |
| **FA-12** | doute de l'exploitant, sans justification à fournir |

### 8.1 `timeout` — le partage, tranché

Un `timeout` est un **verdict terminal de transaction**, prévu et fréquent
(§4.2). Il n'est **jamais** un ABORT de campagne par lui-même. Ce qui décide,
c'est ce que l'observation apporte **ensuite**.

| Fait observé | Qualification | Suite |
|---|---|---|
| fenêtre épuisée, **aucune information supplémentaire** | `timeout` **nominal** — état *indéterminé* | transaction terminée ; **aucune** seconde écriture ; établir l'état par observation ; la campagne peut être **close proprement**, sans ABORT |
| relecture ultérieure **concordante avec la cible** | l'écriture a bien porté ; la fenêtre était trop courte — **fait à consigner**, il mesure I-7 | pas d'ABORT ; le verdict publié **reste** `timeout` (§6) |
| relecture ultérieure **explicitement discordante** | état **non maîtrisé** | **FA-7 → ABORT** |
| état changeant, incohérent, ou tout autre `FA` déclenché | état **non maîtrisé** | **ABORT** |

> **Un `timeout` ne se requalifie jamais après coup.** Si une relecture
> ultérieure concorde, le fait est **consigné** — il vaut mesure de I-7 — mais
> l'ACK publié demeure `timeout`. Le modèle transactionnel n'est pas modifié, et
> le rapport ne réécrit pas l'histoire (§6).

### 8.2 Ce qu'un ABORT déclenche

Un ABORT interrompt la **campagne**, jamais par une écriture. Il impose, dans
cet ordre : arrêter toute nouvelle commande ; établir l'état observable ;
exécuter le **rollback de souveraineté** (§7.1), qui est toujours dû ; et
soumettre à l'humain la question du rollback de valeur, qui ne l'est jamais
d'office (§7.3).

---

## 9. État initial sûr — ce que la campagne devra établir avant toute écriture

Reprise de F8, sans allègement. Chaque ligne est une **preuve à consigner**, pas
une case à cocher.

1. rôle testé : `heating_curve_shift`, et lui seul ;
2. valeur actuelle **relue**, sous ses deux formes, concordantes ;
3. valeur cible — **non choisie par ce document** (F9, §10.4) ;
4. cible dans `[-13 ; 40]`, sur la grille de pas 1, entière ;
5. superviseur neutralisé — **PR-1**, timer **et** unité ;
6. pont historique arrêté — **PR-2** ;
7. démon `vcontrold` actif, confirmé par une lecture nue ;
8. Boilerack installé, démarré, connecté au broker, publiant sa surface de
   lecture ;
9. `[transaction_surface].enabled = true`, et la surface effectivement souscrite ;
10. commande de restauration **armée et écrite** (§7.3) ;
11. observabilité disponible : capture des invocations, journal du démon, trace
    broker ;
12. exploitant **physiquement présent**, plan de reprise physique connu et
    accepté ;
13. hors saison de chauffe.

---

## 10. Décomposition proposée

Déduite des manques réels du §4, non d'un découpage de principe.

### 10.1 W4-F0 — cadrage *(ce document)*

**Objectif** : fixer invariants, autorités, chaîne, analyse du rollback,
décomposition. **Terrain** : non. **Sortie** : ce document, audité.

### 10.2 W4-F1 — la fenêtre de confirmation : étude, arbitrage, et critère

**Objectif** : étudier **l'ensemble** de la fenêtre de confirmation — non la
seule constante `confirm_budget_s` — puis arbitrer, et produire le critère
quantitatif que W4-F2 appliquera.

W4-F1 **MUST** répondre à cinq questions, dans cet ordre :

1. **quelles constantes sont réellement réglables** aujourd'hui, et par quel
   chemin — `read_timeout_s` traverse la configuration publique,
   `confirm_budget_s` et `confirm_interval_s` sont figées par la composition
   (§4.2) ;
2. **quel est le comportement réel** de la boucle `_confirm` face à
   `read_timeout_s`, l'échéance étant testée **après** chaque relecture
   (§4.2.1) ;
3. **quelle fenêtre effective** en résulte selon le régime de contention, et
   comment elle se compare aux 10 s du dispositif historique (E4) ;
4. **une modification logicielle est-elle nécessaire** — exposer
   `confirm_budget_s` et `confirm_interval_s` depuis la composition — **ou le
   réglage déjà public de `read_timeout_s` suffit-il** ;
5. **quel critère quantitatif falsifiable** W4-F2 appliquera pour qualifier la
   coexistence (§10.3.3).

**Périmètre**, si et seulement si la question 4 conclut par l'affirmative :
`transaction_wiring.py`, éventuellement `lifecycle.py` et la forme de
configuration. **Aucune modification du cœur**, aucun réessai, aucun état
nouveau, aucune nouvelle autorité.

**Préconditions** : W4-F0 audité. **Interdits** : terrain, nouveau rôle, nouvelle
sémantique d'ACK, choix d'une valeur cible d'écriture.

**Sortie** : les cinq réponses, étayées ; le **critère de §10.3.3, écrit et
figé** ; et — seulement s'il a été jugé nécessaire — un réglage atteignable
assorti de barrières falsifiables.

> **Ce sous-lot est-il indispensable ?** Il ne l'est pas pour la *sécurité* : une
> fenêtre épuisée produit `timeout`, pas un danger. Il l'est pour deux autres
> raisons. D'abord la **concluance** : sans lui, la campagne risque de ne prouver
> que sa propre expiration. Ensuite parce que W4-F2 a besoin de son **critère**,
> et que le mesureur ne peut pas fixer son propre seuil après coup.

> **Il peut se conclure sans une ligne de code.** Si l'étude montre que la
> fenêtre effective est suffisante, ou que `read_timeout_s` suffit à la régler,
> W4-F1 se clôt sur un arbitrage documenté. **W4-F0 ne préjuge pas de l'issue**,
> et n'autorise aucune modification logicielle par anticipation.

### 10.3 W4-F2 — déploiement et qualification en **lecture seule**

**Objectif** : installer Boilerack sur la machine de référence, le démarrer,
prouver qu'il lit et publie, **avec l'autorité transactionnelle fermée**, et
**qualifier la coexistence** contre le critère que W4-F1 aura fixé.

**Terrain** : **oui — terrain de lecture seule** (§11.2). C'est le sous-lot que
le §4.1 rend inévitable, et le seul qui puisse mesurer la contention avant
qu'elle ne compte.

W4-F2 est le **premier** contact avec l'installation. Il ne peut donc pas
attendre W4-F3 pour être gouverné : son protocole minimal est fixé ici.

#### 10.3.1 Préconditions W4-F2

Toutes exigibles avant la première intervention. Aucune n'est facultative.

1. **W4-F0 intégré et clos** ;
2. **W4-F1 clos**, et son critère quantitatif de qualification disponible
   (§10.2) ;
3. Boilerack configuré, **surface transactionnelle fermée** ;
4. **preuve que cette configuration ne peut émettre aucune écriture** — la
   configuration effectivement déployée est relue et montre l'autorité absente ou
   `false` ; la preuve porte sur le **fichier déployé**, pas sur une intention ;
5. pont historique et superviseur **laissés dans leur état nominal** — ni
   arrêtés, ni désactivés, ni modifiés ;
6. **observabilité disponible** sur les quatre : pont, superviseur, `vcontrold`,
   Boilerack ;
7. **rollback de déploiement lecture seule disponible** — savoir arrêter et
   retirer `<unité-boilerack>` et revenir à l'état d'avant, sans dépendre de
   Boilerack lui-même ;
8. exploitant **physiquement présent**, plan de reprise physique connu ;
9. **autorisation humaine explicite du §11.2**, distincte, et qui ne vaut
   autorisation d'écriture ni de neutralisation.

#### 10.3.2 Critères ABORT propres à W4-F2

Les critères `FA-1..FA-12` du §8 supposent une campagne d'écriture et un
dispositif historique neutralisé : ils ne s'appliquent pas ici. W4-F2 a les
siens, et ils portent tous sur la **coexistence**.

| Réf | Déclencheur |
|---|---|
| **F2A-1** | `vcontrold` devient indisponible, instable, ou change d'état |
| **F2A-2** | le superviseur historique signale une dégradation, ou son cycle cesse d'être nominal |
| **F2A-3** | redémarrage machine inattendu |
| **F2A-4** | redémarrage inattendu du pont, du superviseur, du démon ou de Boilerack |
| **F2A-5** | perte de l'observabilité sur l'un des quatre composants |
| **F2A-6** | comportement de contention non maîtrisé — durées erratiques, ou dépassant le critère de §10.3.3 |
| **F2A-7** | le pont historique cesse de publier, ou sa cadence se dégrade |
| **F2A-8** | doute de l'exploitant, sans justification à fournir |

> **L'ABORT de W4-F2 est simple, et c'est sa force** : arrêter et retirer
> `<unité-boilerack>`. Rien d'autre n'a été touché — ni la chaudière, ni
> l'autorité, ni le dispositif historique — donc rien d'autre n'est à défaire.

#### 10.3.3 Critère de qualification de la coexistence

> **Clause.** Le résultat de W4-F2 **MUST NOT** être « marge mesurée ». Il
> **MUST** être « **marge mesurée, et déclarée conforme à un critère falsifiable
> fixé avant le terrain** ».
>
> Ce critère est **produit par W4-F1** (§10.2), pas par W4-F2 : celui qui mesure
> ne doit pas fixer après coup le seuil qui le juge.

Ce document **ne choisit aucune valeur numérique** : elle relève de W4-F1, qui
seul aura étudié la fenêtre de confirmation et le coût réel des relectures
(§4.2). Ce que W4-F0 impose, c'est la **forme** du critère : falsifiable,
quantitatif, antérieur au terrain, et portant au minimum sur la marge du
superviseur face à son budget de 5 s et sur le coût observé d'une lecture en
coexistence.

**Preuve de sortie** : Boilerack actif en lecture et publiant ; pont historique
**toujours écrivain et toujours nominal** ; mesures de coexistence relevées ;
**critère de W4-F1 déclaré satisfait, ou non**.

#### 10.3.4 Verrou vers W4-F3

> **Clause.** W4-F3 n'est admissible que si **les trois** conditions sont
> réunies : W4-F2 est clos ; la coexistence a été qualifiée ; le critère de
> §10.3.3 est **satisfait**.
>
> Si le critère **échoue**, W4-F3 est **NO-GO**. L'échec n'ouvre ni dérogation ni
> révision du seuil après coup : il renvoie à W4-F1 pour réexamen, ou à un
> arbitrage humain sur la poursuite du chantier.

### 10.4 W4-F3 — protocole one-writer, valeur de test et rollback

**Objectif** : transposer la méthode W4-C §8/§9.1/§12/§13 à la chaîne Boilerack,
figer `FA-1..FA-12`, définir la règle de choix de la valeur cible **sur état
réel observé** — delta minimal, réversible, conforme au rôle — la procédure
de rollback des deux natures (§7.1), et **la garde anti-double-écrivain du §7.2.1**,
sans laquelle aucun reboot ne peut servir de filet.

**Préconditions** : W4-F2 clos, **coexistence qualifiée et critère satisfait**
(§10.3.4). **Interdits** : toute écriture ; tout choix de
valeur *a priori*. **Sortie** : protocole opératoire complet, auditable, avec ses
preuves nommées. **Terrain** : non.

### 10.5 W4-F4 — campagne terrain : première commande réelle

**Objectif** : exécuter **une** commande, une seule fois, selon W4-F3.

**Préconditions** : W4-F3 audité **et autorisation humaine explicite et
distincte**. **Interdits** : réessai, seconde commande, élargissement de rôle,
automatisation de la relecture. **Sortie** : chaîne de preuve complète du §6,
étape par étape, `applied` **ou** `timeout` rapporté tel quel. **Terrain** :
**oui**, écriture réelle.

### 10.6 W4-F5 — clôture

**Objectif** : consigner les résultats, lever ou maintenir I-7, I-10, I-11,
statuer sur la souveraineté durable, rétablir ou confirmer l'état des services.
**Terrain** : non. **Sortie** : W4-F clos, ou renvoi à un lot ultérieur.

### 10.7 Table de synthèse

| Sous-lot | Objectif | Terrain ? | Preuve de sortie |
|---|---|---|---|
| **W4-F0** | cadrage, invariants, décomposition | non | ce document, audité |
| **W4-F1** | fenêtre de confirmation : étude, arbitrage, **critère** | non | cinq réponses étayées ; critère de §10.3.3 figé ; aucun réessai introduit |
| **W4-F2** | Boilerack déployé et qualifié en coexistence | **oui — lecture seule** | lit et publie ; pont nominal ; **critère de W4-F1 déclaré satisfait, ou non** |
| **W4-F3** | protocole one-writer, valeur, rollback, garde anti-reboot | non | protocole complet ; `FA-1..FA-12` figés ; garde §7.2.1 choisie |
| **W4-F4** | une commande réelle, une seule | **oui — écriture** | chaîne §6 étape par étape ; verdict rapporté tel quel |
| **W4-F5** | clôture et inconnues | non | I-7 / I-10 / I-11 statuées |

**Deux verrous conditionnent l'enchaînement**, et ils ne se contournent pas :

- **W4-F1 → W4-F2** : W4-F2 ne peut commencer sans le critère de §10.3.3.
- **W4-F2 → W4-F3** : critère non satisfait ⇒ **W4-F3 NO-GO** (§10.3.4).

---

## 11. Interdit d'écriture réelle sans autorisation humaine ultérieure

Deux terrains existent dans W4-F, et **une seule** interdiction ne peut pas les
gouverner tous les deux. W4-F2 exploite `<unité-boilerack>` en lecture seule ;
W4-F4 écrit sur la chaudière. Les deux exigent une autorisation humaine, mais
**pas la même**, et l'une ne vaut jamais l'autre.

### 11.1 Clause dominante — les quatre actes réservés

> **Clause d'interdiction — dominante sur tout le reste du document.**
>
> Les quatre actes suivants **MUST NOT** être entrepris au titre de W4-F sans une
> **autorisation humaine explicite, distincte, postérieure à l'audit de W4-F3**,
> et portant sur cette campagne-là :
>
> 1. toute **écriture réelle** sur la chaudière ;
> 2. toute **ouverture de l'autorité transactionnelle** —
>    `[transaction_surface].enabled = true` — sur l'installation de référence ;
> 3. toute **neutralisation du dispositif historique** — `<unité-pont>` ou
>    `<timer-guard>` ;
> 4. toute **bascule de souveraineté**, sous quelque forme que ce soit.
>
> Cette autorisation **MUST NOT** être déduite : ni de la clôture de W4-E, ni de
> l'audit de ce document, ni de la clôture de W4-F1, ni de celle de W4-F2, ni de
> l'autorisation W4-F2 du §11.2, ni du fait que `[transaction_surface].enabled`
> **puisse** valoir `true`.

> **Ce que cette clause ne vise pas.** Elle ne porte **pas** sur l'exploitation de
> `<unité-boilerack>` en lecture seule, qui relève du §11.2. Installer Boilerack,
> démarrer son unité, l'arrêter ou la retirer ne figure dans aucun des quatre
> actes réservés : ces gestes ne touchent ni la chaudière, ni l'autorité, ni le
> dispositif historique, ni la souveraineté.

### 11.2 Autorisation W4-F2 — terrain de **lecture seule**

> **Clause.** La première intervention sur l'installation de référence exige elle
> aussi une **autorisation humaine explicite et distincte**, propre à W4-F2.
>
> Elle **autorise**, et uniquement dans le cadre de W4-F2 : installer Boilerack ;
> créer, démarrer, arrêter et retirer `<unité-boilerack>` ; le faire fonctionner
> **en lecture seule** ; mesurer la coexistence et la contention.
>
> Elle **n'autorise pas** : `[transaction_surface].enabled = true` ; la
> neutralisation de `<unité-pont>` ; celle de `<timer-guard>` ; toute écriture
> chaudière ; toute prise de souveraineté ; ni W4-F4.
>
> Elle **MUST NOT** valoir autorisation au sens du §11.1, ni en dispenser.

### 11.3 Les phases

| Phase | Sous-lot | Terrain | Écriture possible ? |
|---|---|---|---|
| conception | F0 | non | non |
| préparation logicielle | F1 | non | non |
| **autorisation humaine — lecture seule** | — | *décision, pas exécution* | — |
| **terrain de lecture seule** | **F2** | **oui, lecture seule** | **non** |
| conception du protocole | F3 | non | non |
| **autorisation humaine — écriture** | — | *décision, pas exécution* | — |
| **terrain d'écriture** | **F4** | **oui, écriture** | **oui**, une seule fois |
| rollback / clôture | F4, F5 | selon le cas | seconde écriture **conditionnelle** (§7.3) |

> **La frontière entre les deux terrains ne se dilue pas.** W4-F2 ne touche ni à
> la chaudière, ni à l'autorité, ni au dispositif historique — il n'est un
> terrain que parce qu'il pose un logiciel sur une machine réelle et modifie la
> charge d'une liaison partagée (§4.3). W4-F4 est le **seul** sous-lot où une
> écriture réelle est possible.

---

## 12. Preuves manquantes et inconnues

### 12.1 `PREUVE TERRAIN / SOURCE EXTERNE REQUISE`

Le dépôt est **public** et exclut par principe les constantes de site. Les
éléments suivants n'y figurent pas, et **ne doivent pas y figurer** :

| Élément | Statut |
|---|---|
| nom de `<unité-pont>`, ce qui la démarre et la maintient | **PREUVE TERRAIN / SOURCE EXTERNE REQUISE** |
| nom de `<timer-guard>` et de son unité d'exécution | **PREUVE TERRAIN / SOURCE EXTERNE REQUISE** |
| commandes exactes d'arrêt, de vérification et de restauration | **PREUVE TERRAIN / SOURCE EXTERNE REQUISE** |
| existence d'un autre écrivain que le pont historique | **PREUVE TERRAIN / SOURCE EXTERNE REQUISE** |
| état réel courant de `heating_curve_shift` | **PREUVE TERRAIN / SOURCE EXTERNE REQUISE** |

Ce que le dépôt **prouve**, en revanche : la **méthode** de neutralisation, ses
deux preuves nommées, et les trois pièges qui l'ont fait échouer une première
fois (§3.3). C'est la partie transférable, et elle est acquise.

### 12.2 Inconnues techniques encore vivantes

| Réf | Inconnue | Effet sur W4-F |
|---|---|---|
| **I-7** | délai avant relecture fiable | **conditionne W4-F1 et W4-F4** ; ne peut être mesurée qu'*au moment* de la première écriture réelle |
| **I-10** | atomicité observable | pourrait apparaître lors d'un changement réel |
| **I-11** | démon acceptant / chaudière appliquant autrement | **indécidable sans changement de valeur** — W4-F4 est sa première occasion |
| **I-15** | signature d'un démon injoignable en écriture | exigerait d'arrêter le démon : **hors périmètre** |

> **Clause.** Ces inconnues **MUST NOT** être levées par raisonnement
> documentaire (W4-E §16). Composer, déployer ou rédiger n'observe rien.

---

## 13. Ce que ce document ne fait pas

- il ne choisit **aucune valeur** à écrire (F9) ;
- il ne prescrit **aucune** commande systemd ;
- il n'ouvre **aucun** sous-lot : il les décrit ;
- il n'ajoute **aucun** rôle, topic, état, ni réessai (F10) ;
- il ne modifie **aucun** contrat existant ;
- il n'accorde **aucune** souveraineté.

**W4-F0 est un cadrage. La souveraineté reste au pont historique.**
