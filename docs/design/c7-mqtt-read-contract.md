# C7 — Contrat MQTT de la surface de lecture

Document **normatif**. Il fixe la surface MQTT publique **en lecture seule** du
bridge, avant toute implémentation.

Conventions : **MUST** obligatoire · **MUST NOT** interdit · **SHOULD**
recommandé · *hors périmètre* explicitement exclu de la v1.

Ce contrat **ne couvre pas** l'écriture, ni les commandes, ni les
acquittements transactionnels. Voir §14.

---

## 1. Faits observés

Cette section ne contient que ce que le dépôt prouve. Elle ne décide rien.

### 1.1 Établi par C5 et C6

| Fait | Source |
|---|---|
| `vclient 0.98.12-5-g8ca4797`, forme `git describe` | fixture `version` |
| Le code retour ne discrimine ni le succès ni l'échec | `c5-vclient-contract.md` §3 |
| La forme `-J` porte `command`, `value`, `raw`, `error` ; `error` est le discriminant | fixtures `read_ok_json`, `unknown_command_json` |
| En erreur, `value` vaut `0.000000` | fixture `unknown_command_json` |
| Démon injoignable : code retour 1, **les deux flux vides** | fixture `daemon_unreachable` |
| Sortie insensible à la locale, pour `getTempKist`, cette version, cette installation | fixtures `read_ok_locale_*` |
| Lecture réelle : 2,7 à 4,0 s pour un client tiers, production active | `c5-vclient-contract.md` §9 |
| Six issues de transport typées, sans `CLIENT_UNAVAILABLE` | `transport/vclient.py` |
| Un échec de lancement local est classé `TRANSPORT_ERROR` | `c6-vclient-read-adapter.md` §1 |

### 1.2 Établi par le pont historique

Relevé dans son code, jamais supposé.

| Fait | Valeur prouvée |
|---|---|
| Mesures publiées | **neuf lectures** + **un état dérivé** = **dix publications** |
| Télémétrie | QoS 1, retain, payload scalaire textuel brut, sans unité ni horodatage |
| Présence | `boiler/bridge/online`, QoS 1, retain, plus testament MQTT |
| Battement | `boiler/bridge/heartbeat`, **QoS 0, non retenu**, JSON `{"ts":…}` |
| Statuts `vcontrold` et Optolink | QoS 1, retain, **dérivés d'une unique sonde** `getTempKist` |
| Publication conditionnelle | en cas d'échec, **rien n'est publié** ; la valeur retenue précédente subsiste |
| Cadences configurées | télémétrie 10 s, battement 30 s |
| Cadences **mesurées** | télémétrie ≈ **19-21 s**, battement ≈ **40 s** |
| État brulleur dérivé | `on` si modulation > 0, **`off` en cas d'échec de parsing** |
| Deux topics sans consommateur | `temperatures/outdoor`, `heating/reduced_reference` |

### 1.3 Établi sur le dépôt public actuel

`boilerack/command` et `boilerack/ack` sont des **valeurs par défaut
techniques**, introduites par le code sans décision documentée. Elles **ne
définissent pas** le namespace public. Ce lot ne les modifie pas.

---

## 2. Décisions C7 ratifiées

| Référence | Décision |
|---|---|
| **N3** | namespace **configurable**, défaut contractuel **`boiler`** |
| **S2** | surface v1 = télémétrie + présence + fraîcheur par mesure + état synthétique de la chaîne de lecture |
| **P3** | modèle **hybride** : scalaires retenus par mesure + un topic JSON agrégé |

Les sections suivantes en dérivent.

---

## 3. Namespace

### 3.1 Paramètre

Un paramètre **`mqtt_prefix`**, chaîne, défaut **`boiler`** — sans barre
oblique terminale.

### 3.2 Construction

Tout topic **MUST** se construire ainsi :

```
<prefix_normalise> "/" <suffixe_contractuel>
```

Les **suffixes contractuels sont invariants** : ils **MUST NOT** dépendre de la
valeur du préfixe. Un consommateur qui connaît le préfixe connaît tous les
topics.

### 3.3 Normalisation — à spécifier ici, à implémenter en C7-C

| Entrée | Comportement **MUST** |
|---|---|
| `boiler` | accepté, préfixe = `boiler` |
| `boiler/` | barre terminale retirée, préfixe = `boiler` |
| `/boiler` | barre initiale retirée, préfixe = `boiler` |
| `boiler//x` | barres consécutives réduites à une seule |
| `maison/boiler` | accepté : un préfixe **MAY** comporter plusieurs niveaux |
| chaîne vide | **rejeté** — un espace de noms est obligatoire pour éviter les collisions sur un broker partagé |
| contient `+` ou `#` | **rejeté** — jokers MQTT |
| contient un caractère de contrôle ou `NUL` | **rejeté** |
| commence par `$` | **rejeté** — espace réservé du broker |

Le rejet **MUST** survenir à la construction de la configuration, avant toute
connexion. Aucune correction silencieuse autre que les normalisations du
tableau.

### 3.4 Interdictions

- **MUST NOT** publier la même donnée sous deux préfixes.
- **MUST NOT** maintenir une double publication permanente : deux autorités
  pour une même valeur constituent une dette.
- **MUST NOT** migrer implicitement les consommateurs.
- **MUST NOT** faire varier un suffixe selon le préfixe retenu.

---

## 4. Télémétrie

### 4.1 Décompte

Le pont historique publie **dix** topics de télémétrie : **neuf lectures
directes** et **un état dérivé**. Le présent contrat retient **huit topics en
v1** ; la mesure de modulation et l'état dérivé sont **tous deux reportés**
(§4.3).

### 4.2 Table normative

QoS **1**, retain **true** pour toutes les entrées. Fréquence cible = période
de publication visée, non garantie (§7).

| Rôle | Commande source | Suffixe MQTT | Type | Unité | Fréquence cible | Compatibilité | v1 |
|---|---|---|---|---|---|---|---|
| `outdoor_temperature` | `getTempA` | `telemetry/temperatures/outdoor` | decimal | °C | 30 s | identique | **oui** |
| `supply_temperature` | `getTempKist` | `telemetry/temperatures/supply` | decimal | °C | 30 s | identique | **oui** |
| `dhw_temperature` | `getTempWWist` | `telemetry/temperatures/dhw` | decimal | °C | 30 s | identique | **oui** |
| `dhw_setpoint` | `getTempWWsoll` | `telemetry/dhw/setpoint` | entier | °C | 60 s | identique | **oui** |
| `heating_setpoint` | `getTempRaumNorSollM1` | `telemetry/heating/setpoint` | entier | °C | 60 s | identique | **oui** |
| `heating_reduced_reference` | `getTempRaumRedSollM1` | `telemetry/heating/reduced_reference` | entier | °C | 60 s | identique | **oui** |
| `heating_curve_slope` | `getNeigungM1` | `telemetry/heating/curve/slope` | decimal | sans unité | 60 s | identique | **oui** |
| `heating_curve_shift` | `getNiveauM1` | `telemetry/heating/curve/shift` | entier | sans unité | 60 s | identique | **oui** |

Les deux mesures issues du brulleur — `burner_modulation` et `burner_state` —
sont **reportées hors v1** (§4.3).

**Mesures sans consommateur connu.** `outdoor` et `reduced_reference` n'ont
aucun consommateur identifié chez le consommateur d'origine.

Leur conservation a un **coût réel**, qu'il faut énoncer : chaque mesure
implique **une invocation distincte** du lecteur. C6 n'accepte **qu'une seule
commande par invocation** — la virgule y est explicitement refusée — et le
groupement multi-commandes de `-c` **n'est pas caractérisé**. C5 a par ailleurs
observé **2,7 à 4,0 secondes** pour une lecture réelle sous contention.
Conserver une mesure allonge donc la durée du cycle d'autant.

Elles sont néanmoins **retenues en v1**, pour trois raisons énoncées sans
enjolivure : la compatibilité historique est préservée ; le coût supplémentaire
est **accepté** en connaissance de cause ; les périodes cibles ne sont **pas
garanties** (§7). Cet arbitrage **SHOULD** être réévalué après les premières
mesures de durée de cycle du futur ordonnanceur.

### 4.3 REPORTÉ HORS V1 — mesures du brulleur

**`burner_modulation` et `burner_state` sont l'un et l'autre reportés.**

Motifs, tous vérifiables dans le dépôt public :

1. `getBrennerStatus` est une **commande historique observée** — le pont
   historique la lit et publie sa sortie — mais elle **n'est pas caractérisée
   par C5** : aucune fixture ne la couvre. C5 porte sur le comportement de
   transport et sur la lecture `getTempKist`.
2. Le **type** et l'**unité** de sa valeur ne sont **pas établis** par le dépôt
   public.
3. `CommandSpec` **ne porte aucun champ d'unité** : le profil ne peut donc pas,
   en l'état, porter cette information.
4. Une dépendance de la sémantique à la régulation a été **alléguée à partir du
   pont historique**, mais elle n'est **pas prouvée** dans le dépôt public. Elle
   figure à ce titre parmi les inconnues (§15).
5. Conserver le même topic avec une sémantique incertaine créerait un **risque
   silencieux** : rien ne casserait visiblement, et un consommateur continuerait
   d'interpréter la valeur selon son hypothèse antérieure.

> **Règle.** Aucun topic de brulleur ne doit être publié avant caractérisation
> de la commande **et** existence d'une source de vérité contractuelle pour son
> type et son unité.

Le présent contrat **ne fixe ni type, ni unité, ni plage** pour ces mesures :
ce serait décider sans preuve.

Par ailleurs, le repli `off` en cas d'échec de parsing pratique par le pont
historique ne doit pas être reproduit, quel que soit le sort futur de ces
mesures.

**Coût de compatibilité, assumé et signalé** : un consommateur historique perd
deux entités, dont un capteur binaire de brulleur. Aucun contournement n'est
proposé ici — le proposer supposerait la sémantique que ce contrat refuse
précisément d'affirmer.

### 4.4 Publication scalaire

- **MUST** publier en QoS 1, retain `true`.
- **MUST** publier **uniquement** après une lecture dont le statut est `OK`.
- **MUST NOT** publier quoi que ce soit en cas d'échec de lecture.
- **MUST NOT** substituer une valeur sentinelle : ni `0`, ni `false`, ni chaîne
  vide, ni `unknown`, ni `null`, ni aucune autre.
- La dernière valeur retenue **MAY** subsister côté broker après un échec.

> **Règle normative.** Une valeur retenue est **la dernière valeur connue, pas
> nécessairement une valeur actuelle**. Un consommateur **MUST** consulter le
> topic de fraîcheur (§6) pour en connaître la validité temporelle.

### 4.5 Représentation

Le payload **MUST** être une **chaîne numérique décimale sans unité, utilisant
le point comme séparateur et analysable comme un nombre fini**, encodée UTF-8.

Règles fermées pour la v1, afin que deux producteurs conformes ne puissent pas
émettre des formes incompatibles :

| Règle | Décision |
|---|---|
| Séparateur decimal | le point **MUST** ; la virgule **MUST NOT** |
| Notation exponentielle | **MUST NOT** — ni `2.8e1`, ni `2.8E1` |
| Espaces, y compris de bordure | **MUST NOT** |
| Guillemets | **MUST NOT** — le payload n'est pas du JSON |
| `NaN`, `Infinity`, `-Infinity` | **MUST NOT** — une valeur non finie n'est pas un succès de lecture et ne donne lieu à aucune publication |
| Zéro négatif | une valeur négative nulle **MUST** être sérialisée **sans signe négatif** : `-0` s'écrit `0`, `-0.0` s'écrit `0.0`. La règle porte sur le **seul signe** ; elle ne fixe pas la précision |
| Forme entière ou décimale | **toutes deux autorisées** : `28` et `28.0` sont conformes |
| Signe négatif | autorise pour les mesures dont le domaine l'admet |
| Précision décimale | **non normative** : `28.0` et `28.000000` sont l'un et l'autre conformes |

Un consommateur **MUST** analyser la valeur comme un nombre decimal fini et
**MUST NOT** s'appuyer sur le nombre de chiffres.

Cette forme est compatible avec l'historique, qui émet `28.000000`, et
directement exploitable par un consommateur domotique sans transformation.

### 4.6 Ordre de publication

Après une lecture réussie, le producteur **MUST** procéder dans cet ordre :

1. publier la nouvelle valeur scalaire ;
2. mettre à jour l'état interne de la mesure ;
3. publier l'instantané `bridge/telemetry_status`.

**Les deux publications ne sont pas transactionnelles.** Le contrat l'énonce
plutôt que de le masquer :

- l'instantané décrit **l'état de lecture**, non la garantie de livraison du
  scalaire ; `last_result` porte l'issue de la **lecture**, jamais celle de la
  publication MQTT ;
- si la publication scalaire échoue, **aucune compensation ni aucun retour
  arrière n'est exigé** — et la valeur ne doit pas être présentée comme publiée,
  ce que l'instantané ne prétend de toute façon pas ;
- si la publication de l'instantané échoue, aucune compensation n'est exigée :
  la republication périodique (§7.4) rétablira l'état courant.

Aucune taxonomie d'erreur de publication MQTT n'est définie en v1 : la surface
de lecture ne la porte pas.

---

## 5. Présence du bridge

Suffixe : **`bridge/online`**.

| | |
|---|---|
| QoS | **1** |
| Retain | **true** |
| Payload | strictement `online` ou `offline` |
| À la connexion | `online` |
| Testament MQTT | `offline`, QoS 1, retain |
| À l'arrêt propre | `offline` avant déconnexion |

### Sémantique, énoncée sans exagération

> **Le processus bridge est connecté au broker MQTT.**

Ce topic **ne prouve pas** : que `vclient` est lançable · que `vcontrold`
répond · que la liaison Optolink répond · que les mesures sont fraîches · que
la chaudière est joignable.

Un consommateur **MUST NOT** en déduire la disponibilité de la chaîne de
lecture ; celle-ci est portée par §8.

---

## 6. Fraîcheur agrégée

### 6.1 Choix du topic

Suffixe retenu : **`bridge/telemetry_status`**.

Argumentation, la décision devant être figée : `telemetry/status` aurait place
un objet JSON de métadonnées au milieu de valeurs scalaires. L'invariant
**« tout ce qui se trouve sous `telemetry/` est une valeur de mesure
scalaire »** a une valeur pratique : il rend sur un abonnement générique
`telemetry/#` toute entrée directement exploitable, sans exception à traiter.
Placer les métadonnées sous `bridge/` — où se trouvent déjà présence et
version — préserve cet invariant. Ce choix rejoint par ailleurs la
spécification antérieure du projet.

| | |
|---|---|
| QoS | **1** |
| Retain | **true** |

### 6.2 Forme

```json
{
  "schema": 1,
  "ts": "2026-08-02T20:00:00Z",
  "chain": { "status": "ok", "cause": null },
  "measurements": {
    "supply_temperature": {
      "has_value": true,
      "fresh": true,
      "last_success": "2026-08-02T19:59:58Z",
      "age_s": 2,
      "last_result": "ok"
    },
    "outdoor_temperature": {
      "has_value": true,
      "fresh": false,
      "last_success": "2026-08-02T19:52:10Z",
      "age_s": 470,
      "last_result": "timeout"
    }
  }
}
```

JSON compact, UTF-8, `allow_nan` interdit.

### 6.3 `schema`

Entier, version initiale **`1`**. Une évolution **compatible** — ajout de champ
optionnel, ajout d'une entrée de mesure — **MUST NOT** incrémenter `schema`. Un
retrait de champ, un changement de type ou de sémantique **MUST**
l'incrémenter. Un consommateur **MUST** ignorer les champs qu'il ne connaît pas
et **MUST** refuser un `schema` majeur inconnu.

### 6.4 `ts`

Instant de construction de l'instantané. **MUST** être en **UTC**, au format
**RFC 3339** avec suffixe `Z`. Une horloge monotone **MUST NOT** être exposée :
elle n'a de sens que dans le processus.

### 6.5 Modèle de mesure — deux dimensions, jamais fusionnées

Deux modèles ont été comparés.

| | Énuméré unique `ok` / `stale` / `error` / `never` | Champs orthogonaux |
|---|---|---|
| Mesure ancienne **et** dernière tentative en erreur | **impossible à exprimer** : il faut choisir | exprime : `fresh: false` + `last_result: "timeout"` |
| Lisibilité immédiate | meilleure | demande une lecture de trois champs |
| Extension | ajouter un état casse les consommateurs | ajouter un champ ne casse rien |

Ces deux dimensions — **ai-je une valeur, est-elle fraîche** d'une part, **qu'a
donne la dernière tentative** d'autre part — sont indépendantes et doivent le
rester. Le modèle énuméré unique les écrase.

> **Décision : modèle à champs orthogonaux.** Aucun champ `status` par mesure
> n'est défini : il réintroduirait l'écrasement qu'on cherche à éviter. Le
> signal synthétique existe au niveau de la chaîne (§8), pas de la mesure.

| Champ | Type | Sémantique |
|---|---|---|
| `has_value` | booléen | une valeur scalaire a été publiée au moins une fois depuis le démarrage |
| `fresh` | booléen | `age_s` est inférieur ou égal au seuil de fraîcheur de la mesure (§7) |
| `last_success` | RFC 3339 UTC, ou `null` | instant de la dernière lecture réussie |
| `age_s` | entier ≥ 0, ou `null` | ancienneté de `last_success` à l'instant `ts` |
| `last_result` | énuméré (§6.6) ou `null` | issue de la **dernière tentative**, `null` si aucune tentative |

Invariants **MUST** : `has_value` vrai équivaut à `last_success` non nul ·
`age_s` nul si et seulement si `last_success` est nul · `fresh` vrai implique
`has_value` vrai · une mesure jamais lue avec succès porte
`has_value: false`, `fresh: false`, `last_success: null`, `age_s: null`.

**Aucun champ `last_attempt` n'est défini en v1.** Conséquence, énoncée
franchement :

> La distinction entre une valeur ancienne sans tentative récente et une valeur
> ancienne après plusieurs échecs récents n'est pas exposée en v1 ; elle relève
> d'une éventuelle surface de santé détaillée ultérieure.

Seuls `last_success`, `age_s` et `last_result` sont portés.

### 6.6 Taxonomie publique de `last_result`

Valeurs **stables et contractuelles** :

```
ok · timeout · daemon_unreachable · unusable_output ·
unsupported_command · transport_error
```

Correspondance **actuelle** avec les issues internes — elle **MAY** évoluer,
les valeurs publiques restant stables :

| Interne | Public |
|---|---|
| `OK` | `ok` |
| `TIMEOUT` | `timeout` |
| `DAEMON_UNREACHABLE` | `daemon_unreachable` |
| `UNUSABLE_OUTPUT` | `unusable_output` |
| `UNKNOWN_COMMAND` | `unsupported_command` |
| `TRANSPORT_ERROR` | `transport_error` |

> **Limite honnête.** Un échec de lancement du client local est aujourd'hui
> classé `TRANSPORT_ERROR` — `CLIENT_UNAVAILABLE` n'étant pas ratifié. La
> taxonomie publique **ne distingue donc pas** « client non lançable » de
> « autre erreur de transport ». Aucune valeur publique n'est définie pour
> cette distinction tant qu'elle n'est pas représentable.

Interdictions : **MUST NOT** publier un message système brut, un chemin local,
un `stderr` complet, un nom d'exception, ni tout détail susceptible de varier
selon la version du client ou du système.

---

## 7. Politique de fraîcheur

### 7.1 Pourquoi les seuils ne sont pas repris de l'historique

Les cadences **configurées** du pont historique (10 s et 30 s) ne correspondent
pas aux cadences **mesurées** (≈ 19-21 s et ≈ 40 s) : la durée du cycle de
lecture allonge la boucle. Un seuil de 60 s, hérité de l'historique, ne
tolérait donc **qu'un seul** cycle manque au lieu des deux escomptés.

Le contrat **MUST NOT** figer un seuil absolu par inertie. Il le définit
**relativement à la période**.

### 7.2 Définitions

Pour chaque mesure de période cible `P` :

| Paramètre | Règle |
|---|---|
| `fresh_max` | seuil de fraîcheur, en secondes. Défaut **`3 × P`** |
| Invariant | `fresh_max` **MUST** être strictement supérieur à `P` |
| Configurabilité | `fresh_max` **MAY** être configuré par mesure ou globalement |
| Unité | secondes, entier positif |

Le facteur **3** est retenu, et non 2, parce que la durée d'une lecture réelle
observée — 2,7 à 4,0 s — est du même ordre que certaines périodes : un facteur
2 laisserait une marge d'un seul cycle.

### 7.3 Comportements

| Situation | Comportement **MUST** |
|---|---|
| Après démarrage, avant la première lecture | aucune publication scalaire ; instantané publié avec `has_value: false`, `fresh: false`, `last_result: null` |
| Échec isolé | aucune publication scalaire ; `last_result` mis à jour ; `fresh` reste vrai tant que `age_s ≤ fresh_max` |
| Échecs répétés jusqu'au dépassement | `fresh` devient faux ; le scalaire retenu subsiste ; l'instantané porte la cause |
| Reprise après échec | publication scalaire, `last_success` et `age_s` remis à jour, `last_result` à `ok`, `fresh` à vrai |

### 7.4 Cadence de l'instantané

L'instantané **MUST** être republie à intervalle régulier **même si rien n'a
change**, avec un `ts` à jour. Sans cette règle, un consommateur ne pourrait
pas distinguer un bridge figé d'un bridge dont rien n'a bouge.

Période de republication : **MUST** être inférieure ou égale au plus petit
`fresh_max` de la surface. **SHOULD** valoir la plus petite période cible.

---

## 8. État synthétique de la chaîne de lecture

### 8.1 Ce que ce contrat refuse de reproduire

Le pont historique publie `vcontrold_status` et `optolink_status` dérivés
**d'une seule sonde**. Deux topics, une seule vérité. Le contrat **MUST NOT**
reproduire cette projection.

Il **MUST NOT** non plus affirmer une distinction entre « démon joignable » et
« Optolink fonctionnel » : C5 et C6 permettent de distinguer *démon injoignable*
de *réponse inexploitable*, mais **ne permettent pas** d'attribuer une réponse
inexploitable à la liaison plutôt qu'à la chaudière.

### 8.2 Signal unique

Un seul signal, dans l'instantané agrégé, sous `chain`.

**Définition — cycle de lecture.** Une **tentative planifiée de lecture de
l'ensemble des mesures v1 dues à cet instant**. Un cycle est **terminé** lorsque
chacune de ces tentatives a rendu une issue, quelle qu'elle soit.

| `status` | Condition |
|---|---|
| `ok` | au moins une mesure lue avec succès lors du dernier cycle terminé, **et** aucune tentative en échec lors de ce cycle |
| `degraded` | au moins une réussite **et** au moins un échec lors du dernier cycle terminé |
| `unavailable` | aucune lecture réussie lors du dernier cycle terminé, **ou** aucun cycle terminé à ce jour |

**Avant le premier cycle terminé**, l'instantané **MUST** porter :

```json
{ "status": "unavailable", "cause": null }
```

Sémantique exacte de cet état initial : **aucune conclusion sur la chaudière**,
aucune lecture encore achevée, la chaîne de lecture n'a simplement pas encore
produit de résultat. `cause` est `null` parce qu'aucun échec n'a été observé —
l'absence de résultat n'est pas un échec.

**Transition.** Des la fin du premier cycle, `status` prend la valeur dérivée
du tableau ci-dessus, et `cause` celle de la règle ci-dessous.

Trois états, pas davantage : ils recouvrent les cas actionnables sans en
inventer.

`chain.cause` : `null` si `status` vaut `ok` ; sinon la valeur de
`last_result` la plus sévère observée au dernier cycle, selon l'ordre

```
daemon_unreachable > transport_error > timeout > unusable_output > unsupported_command
```

Cet ordre place en tête ce qui affecte toute la chaîne, et en queue ce qui
n'affecte qu'une commande.

> `chain` est **dérivé de l'ensemble des mesures réellement tentées**, jamais
> d'une sonde dédiée. C'est ce qui le distingue du modèle historique.

### 8.3 Aucun topic scalaire de santé

`bridge/vcontrold_status` et `bridge/optolink_status` **MUST NOT** être
publiés. Voir la matrice §13 pour le coût de compatibilité.

---

## 9. Battement

Suffixe historique : `bridge/heartbeat`, QoS 0, non retenu, payload
`{"ts":…}`.

**Analyse.** Dans le modèle retenu, la présence est portée par le testament et
le topic retenu, et la vitalité du processus par la republication périodique de
l'instantané (§7.4), qui porte déjà un `ts`. Le battement est donc
**techniquement redondant**.

Il conserve néanmoins un **consommateur prouvé** : le consommateur d'origine en
dérive un état dégradé par l'âge du dernier battement. Le supprimer romprait ce
consommateur, alors même que le défaut `boiler` a été retenu pour préserver la
compatibilité.

> **Décision : conservé en `SHOULD`, pour compatibilité historique uniquement.**
> QoS 0, non retenu, payload `{"ts":"…"}` en RFC 3339 UTC.

Conditions de cette conservation, toutes explicites :

- il est conservé **au titre de la compatibilité historique**, pas de son
  utilité propre ;
- sa **redondance** avec le testament et l'instantané est **assumée** ;
- il **ne porte aucune autorité fonctionnelle** : aucune décision ne doit en
  dépendre ;
- il est **candidat à la dépréciation** dès lors que l'instantané sera consommé ;
- **aucune santé de la chaudière ne doit en être déduite** : il n'atteste que de
  l'activité du processus.

Un producteur **MAY** l'omettre s'il documente la rupture. Ce topic **n'est pas
indispensable**.

---

## 10. Capacités — hors v1

Aucun topic `capabilities` n'est défini par ce contrat. Aucun
consommateur réel n'a été identifié, et le pont historique n'en publie pas.
Le sujet est reporté sans préjuger de sa valeur future.

---

## 11. Récapitulatif des topics v1

Suffixes contractuels, préfixe omis.

| Suffixe | QoS | Retain | Payload |
|---|---:|---:|---|
| `telemetry/temperatures/outdoor` | 1 | ✔ | decimal |
| `telemetry/temperatures/supply` | 1 | ✔ | decimal |
| `telemetry/temperatures/dhw` | 1 | ✔ | decimal |
| `telemetry/dhw/setpoint` | 1 | ✔ | decimal |
| `telemetry/heating/setpoint` | 1 | ✔ | decimal |
| `telemetry/heating/reduced_reference` | 1 | ✔ | decimal |
| `telemetry/heating/curve/slope` | 1 | ✔ | decimal |
| `telemetry/heating/curve/shift` | 1 | ✔ | decimal |
| `bridge/online` | 1 | ✔ | `online` / `offline` |
| `bridge/telemetry_status` | 1 | ✔ | JSON, schema 1 |
| `bridge/heartbeat` | 0 | ✖ | JSON `{"ts":…}` — `SHOULD`, compatibilité |

**Onze topics** au total, dont **huit mesures**. Ils ne sont pas tous
obligatoires : **dix topics requis** (**MUST**) et **un topic recommandé**
(**SHOULD**), `bridge/heartbeat`, conservé au seul titre de la compatibilité
historique et omissible par un producteur qui documente la rupture (§9).

Tout autre topic **MUST NOT** être publié par la surface de lecture.

---

## 12. Interdictions transverses

Le contrat **MUST NOT** :

- assimiler « valeur absente », « valeur inconnue » et « valeur fausse » ;
- publier `0` ou toute sentinelle à la place d'une erreur ;
- présenter une valeur retenue comme fraîche sans le topic de fraîcheur ;
- faire dépendre un état de santé d'une seule valeur métier sans l'expliciter ;
- déduire une capacité d'écriture de la seule présence d'une commande ;
- annoncer `online` alors que seule la connexion MQTT est établie **et** laisser
  croire que la chaîne de lecture fonctionne — d'où §5 et §8 ;
- mélanger acquittements transactionnels et télémétrie ;
- introduire un chemin d'écriture.

---

## 13. Matrice de compatibilité

| Topic historique | Identique | Nouvelle sémantique | Remplacé | Reporté | Justification |
|---|:-:|:-:|:-:|:-:|---|
| `telemetry/temperatures/outdoor` | ✔ | | | | nom, QoS, retain, payload conservés |
| `telemetry/temperatures/supply` | ✔ | | | | idem |
| `telemetry/temperatures/dhw` | ✔ | | | | idem |
| `telemetry/dhw/setpoint` | ✔ | | | | idem |
| `telemetry/heating/setpoint` | ✔ | | | | idem |
| `telemetry/heating/reduced_reference` | ✔ | | | | idem |
| `telemetry/heating/curve/slope` | ✔ | | | | idem |
| `telemetry/heating/curve/shift` | ✔ | | | | idem |
| `telemetry/burner/modulation` | | | | **✔** | commande non caractérisée ; type et unité non établis — **perte d'entité** côté consommateur |
| `telemetry/burner/state` | | | | **✔** | dérivé d'une mesure elle-même reportée ; repli `off` refusé — **perte d'entité** côté consommateur |
| `bridge/online` | ✔ | | | | nom, QoS, retain, testament, payload conservés |
| `bridge/heartbeat` | ✔ | | | | conservé en `SHOULD`, déclaré redondant |
| `bridge/version` | | | | **✔** | non retenu en v1 : information de diagnostic sans consommateur décisionnel |
| `bridge/vcontrold_status` | | | **✔** | | remplacé par `chain` dans l'instantané — **rupture** : le topic disparait |
| `bridge/optolink_status` | | | **✔** | | idem |
| `error/last` | | | | **✔** | lié au chemin d'écriture, hors surface de lecture |
| `guard/*` | | | | **✔** | supervision correctrice hors périmètre du produit |

> **Lecture de la matrice.** La colonne « Reporté » recouvre **deux cas
> distincts**, détaillés plus bas : *reporté faute de preuve* — le topic pourrait
> revenir — et *hors périmètre* — il n'a jamais relève de ce contrat.
>
> Sur les **16** topics historiques **individuels** hors guard :
> **10** conservés à l'identique · **2** remplacés · **3** reportés faute de
> preuve (`telemetry/burner/modulation`, `telemetry/burner/state`,
> `bridge/version`) · **1** hors périmètre (`error/last`).
>
> La dix-septième ligne, `guard/*`, est une **ligne groupée supplémentaire**,
> elle aussi hors périmètre, et **n'entre pas** dans le décompte de 16.

**Compatibilité de nom** : sur les **16** topics historiques hors guard,
**10** conservent leur nom, **tous à l'identique** — aucun topic n'est conservé
avec une sémantique modifiée. **Compatibilité de QoS et de retain** : conservée
sur ces 10 topics. **Compatibilité de payload** : conservée sur les 8 mesures
retenues.
**Compatibilité sémantique** : conservée sur **tous** les topics retenus.
Aucun topic n'est conservé avec une sémantique modifiée — c'est précisément ce
qu'a permis le report des mesures de brulleur.

Trois catégories distinctes, à ne pas confondre :

| Catégorie | Topics | Sens |
|---|---|---|
| **Rupture de la surface de lecture** | `vcontrold_status`, `optolink_status` | le topic disparait ; l'information est portée autrement, par `chain` |
| **Reporté faute de preuve** | `burner/modulation`, `burner/state`, `bridge/version` | le topic pourrait revenir ; rien n'est décide contre lui |
| **Hors périmètre de la surface de lecture** | `error/last`, `guard/*` | jamais du ressort de ce contrat |

`bridge/version` figure parmi les reports et non parmi les ruptures : rien ne
s'oppose à sa publication, il n'a simplement aucun consommateur décisionnel
identifié à ce jour.

---

## 14. Interaction avec la surface transactionnelle

- La surface de lecture est **séparée** des commandes et des acquittements.
- Un topic de lecture **MUST NOT** déclencher d'action.
- Aucun statut de lecture ne vaut acquittement.
- Aucune absence de mesure ne produit de commande.
- Ce contrat **ne modifie ni C3 ni C4**.

**Divergence enregistrée, non tranchée ici.** Le code actuel publie sous
`boilerack/command` et `boilerack/ack`, alors que la surface de lecture aura
pour défaut `boiler`. Cette incohérence de namespace entre les deux surfaces
est **réelle** et devra être arbitrée. Elle **MUST NOT** l'être dans ce contrat
de lecture, qui porterait alors sur l'écriture.

> **Dette enregistrée.** Avant toute composition root publique, le projet devra
> arbitrer la convergence des namespaces transactionnel et de lecture. C7-B
> **n'autorise pas** une coexistence permanente sans décision.

---

## 15. Inconnues restantes

| # | Inconnue | Conséquence |
|---|---|---|
| 1 | **Comportement d'une écriture `set…`** | bloque tout le chemin d'écriture |
| 2 | Distinction chaudière / liaison Optolink | `chain` ne peut pas l'exprimer |
| 3 | Distinction « client non lançable » / autre erreur de transport | absente de la taxonomie publique |
| 4 | Sémantique des signatures sur une autre version du client | contrat valable pour la version caractérisée |
| 5 | Politique de rétention et expiration de session du broker | non déductible du code |
| 6 | Consommateurs exacts de `outdoor` et `reduced_reference` | aucun identifié ; conservés par prudence |
| 7 | Valeur réelle d'un topic de capacités | reporté |
| 8 | **Sémantique, type et unité de `getBrennerStatus`** — commande observée dans le pont historique, **non caractérisée par C5** ; la dépendance à la régulation est **alléguée** à partir du pont historique, non prouvée dans le dépôt public | bloque `burner_modulation` **et** `burner_state` |
| 9 | Cadences réelles atteignables par le futur publieur | les périodes cibles sont des objectifs, non des garanties |

---

## 16. Périmètre

Ce document est **documentaire**. Il ne crée aucun topic, ne publie rien,
n'implémente aucune validation. La normalisation du préfixe (§3.3), la
publication (§4.4), l'instantané (§6) et la politique de fraîcheur (§7) seront
implémentés en C7-C, hors ligne, sur doubles et fixtures.

Aucun accès production n'a été effectué pour rédiger ce contrat : il est
intégralement dérivé du dépôt public et du dépôt historique, lus en lecture
seule.
