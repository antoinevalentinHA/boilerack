# C7 — Contrat MQTT de la surface de lecture

Document **normatif**. Il fixe la surface MQTT publique **en lecture seule** du
bridge, avant toute implementation.

Conventions : **MUST** obligatoire · **MUST NOT** interdit · **SHOULD**
recommande · *hors perimetre* explicitement exclu de la v1.

Ce contrat **ne couvre pas** l'ecriture, ni les commandes, ni les
acquittements transactionnels. Voir §14.

---

## 1. Faits observes

Cette section ne contient que ce que le depot prouve. Elle ne decide rien.

### 1.1 Etabli par C5 et C6

| Fait | Source |
|---|---|
| `vclient 0.98.12-5-g8ca4797`, forme `git describe` | fixture `version` |
| Le code retour ne discrimine ni le succes ni l'echec | `c5-vclient-contract.md` §3 |
| La forme `-J` porte `command`, `value`, `raw`, `error` ; `error` est le discriminant | fixtures `read_ok_json`, `unknown_command_json` |
| En erreur, `value` vaut `0.000000` | fixture `unknown_command_json` |
| Demon injoignable : code retour 1, **les deux flux vides** | fixture `daemon_unreachable` |
| Sortie insensible a la locale, pour `getTempKist`, cette version, cette installation | fixtures `read_ok_locale_*` |
| Lecture reelle : 2,7 a 4,0 s pour un client tiers, production active | `c5-vclient-contract.md` §9 |
| Six issues de transport typees, sans `CLIENT_UNAVAILABLE` | `transport/vclient.py` |
| Un echec de lancement local est classe `TRANSPORT_ERROR` | `c6-vclient-read-adapter.md` §1 |

### 1.2 Etabli par le pont historique

Releve dans son code, jamais suppose.

| Fait | Valeur prouvee |
|---|---|
| Mesures publiees | **neuf lectures** + **un etat derive** = **dix publications** |
| Telemetrie | QoS 1, retain, payload scalaire textuel brut, sans unite ni horodatage |
| Presence | `boiler/bridge/online`, QoS 1, retain, plus testament MQTT |
| Battement | `boiler/bridge/heartbeat`, **QoS 0, non retenu**, JSON `{"ts":…}` |
| Statuts `vcontrold` et Optolink | QoS 1, retain, **derives d'une unique sonde** `getTempKist` |
| Publication conditionnelle | en cas d'echec, **rien n'est publie** ; la valeur retenue precedente subsiste |
| Cadences configurees | telemetrie 10 s, battement 30 s |
| Cadences **mesurees** | telemetrie ≈ **19-21 s**, battement ≈ **40 s** |
| Etat brulleur derive | `on` si modulation > 0, **`off` en cas d'echec de parsing** |
| Deux topics sans consommateur | `temperatures/outdoor`, `heating/reduced_reference` |

### 1.3 Etabli sur le depot public actuel

`boilerack/command` et `boilerack/ack` sont des **valeurs par defaut
techniques**, introduites par le code sans decision documentee. Elles **ne
definissent pas** le namespace public. Ce lot ne les modifie pas.

---

## 2. Decisions C7 ratifiees

| Reference | Decision |
|---|---|
| **N3** | namespace **configurable**, defaut contractuel **`boiler`** |
| **S2** | surface v1 = telemetrie + presence + fraicheur par mesure + etat synthetique de la chaine de lecture |
| **P3** | modele **hybride** : scalaires retenus par mesure + un topic JSON agrege |

Les sections suivantes en derivent.

---

## 3. Namespace

### 3.1 Parametre

Un parametre **`mqtt_prefix`**, chaine, defaut **`boiler`** — sans barre
oblique terminale.

### 3.2 Construction

Tout topic **MUST** se construire ainsi :

```
<prefix_normalise> "/" <suffixe_contractuel>
```

Les **suffixes contractuels sont invariants** : ils **MUST NOT** dependre de la
valeur du prefixe. Un consommateur qui connait le prefixe connait tous les
topics.

### 3.3 Normalisation — a specifier ici, a implementer en C7-C

| Entree | Comportement **MUST** |
|---|---|
| `boiler` | accepte, prefixe = `boiler` |
| `boiler/` | barre terminale retiree, prefixe = `boiler` |
| `/boiler` | barre initiale retiree, prefixe = `boiler` |
| `boiler//x` | barres consecutives reduites a une seule |
| `maison/boiler` | accepte : un prefixe **MAY** comporter plusieurs niveaux |
| chaine vide | **rejete** — un espace de noms est obligatoire pour eviter les collisions sur un broker partage |
| contient `+` ou `#` | **rejete** — jokers MQTT |
| contient un caractere de controle ou `NUL` | **rejete** |
| commence par `$` | **rejete** — espace reserve du broker |

Le rejet **MUST** survenir a la construction de la configuration, avant toute
connexion. Aucune correction silencieuse autre que les normalisations du
tableau.

### 3.4 Interdictions

- **MUST NOT** publier la meme donnee sous deux prefixes.
- **MUST NOT** maintenir une double publication permanente : deux autorites
  pour une meme valeur constituent une dette.
- **MUST NOT** migrer implicitement les consommateurs.
- **MUST NOT** faire varier un suffixe selon le prefixe retenu.

---

## 4. Telemetrie

### 4.1 Decompte

Le pont historique publie **dix** topics de telemetrie : **neuf lectures
directes** et **un etat derive**. Le present contrat retient **huit topics en
v1** ; la mesure de modulation et l'etat derive sont **tous deux reportes**
(§4.3).

### 4.2 Table normative

QoS **1**, retain **true** pour toutes les entrees. Fréquence cible = periode
de publication visee, non garantie (§7).

| Role | Commande source | Suffixe MQTT | Type | Unite | Fréquence cible | Compatibilite | v1 |
|---|---|---|---|---|---|---|---|
| `outdoor_temperature` | `getTempA` | `telemetry/temperatures/outdoor` | decimal | °C | 30 s | identique | **oui** |
| `supply_temperature` | `getTempKist` | `telemetry/temperatures/supply` | decimal | °C | 30 s | identique | **oui** |
| `dhw_temperature` | `getTempWWist` | `telemetry/temperatures/dhw` | decimal | °C | 30 s | identique | **oui** |
| `dhw_setpoint` | `getTempWWsoll` | `telemetry/dhw/setpoint` | entier | °C | 60 s | identique | **oui** |
| `heating_setpoint` | `getTempRaumNorSollM1` | `telemetry/heating/setpoint` | entier | °C | 60 s | identique | **oui** |
| `heating_reduced_reference` | `getTempRaumRedSollM1` | `telemetry/heating/reduced_reference` | entier | °C | 60 s | identique | **oui** |
| `heating_curve_slope` | `getNeigungM1` | `telemetry/heating/curve/slope` | decimal | sans unite | 60 s | identique | **oui** |
| `heating_curve_shift` | `getNiveauM1` | `telemetry/heating/curve/shift` | entier | sans unite | 60 s | identique | **oui** |

Les deux mesures issues du brulleur — `burner_modulation` et `burner_state` —
sont **reportees hors v1** (§4.3).

**Mesures sans consommateur connu.** `outdoor` et `reduced_reference` n'ont
aucun consommateur identifie chez le consommateur d'origine.

Leur conservation a un **cout reel**, qu'il faut enoncer : chaque mesure
implique **une invocation distincte** du lecteur. C6 n'accepte **qu'une seule
commande par invocation** — la virgule y est explicitement refusee — et le
groupement multi-commandes de `-c` **n'est pas caracterise**. C5 a par ailleurs
observe **2,7 a 4,0 secondes** pour une lecture reelle sous contention.
Conserver une mesure allonge donc la duree du cycle d'autant.

Elles sont neanmoins **retenues en v1**, pour trois raisons enoncees sans
enjolivure : la compatibilite historique est preservee ; le cout supplementaire
est **accepte** en connaissance de cause ; les periodes cibles ne sont **pas
garanties** (§7). Cet arbitrage **SHOULD** etre reevalue apres les premieres
mesures de duree de cycle du futur ordonnanceur.

### 4.3 REPORTE HORS V1 — mesures du brulleur

**`burner_modulation` et `burner_state` sont l'un et l'autre reportes.**

Motifs, tous verifiables dans le depot public :

1. `getBrennerStatus` est une **commande historique observee** — le pont
   historique la lit et publie sa sortie — mais elle **n'est pas caracterisee
   par C5** : aucune fixture ne la couvre. C5 porte sur le comportement de
   transport et sur la lecture `getTempKist`.
2. Le **type** et l'**unite** de sa valeur ne sont **pas etablis** par le depot
   public.
3. `CommandSpec` **ne porte aucun champ d'unite** : le profil ne peut donc pas,
   en l'etat, porter cette information.
4. Une dependance de la semantique a la regulation a ete **alleguee a partir du
   pont historique**, mais elle n'est **pas prouvee** dans le depot public. Elle
   figure a ce titre parmi les inconnues (§15).
5. Conserver le meme topic avec une semantique incertaine creerait un **risque
   silencieux** : rien ne casserait visiblement, et un consommateur continuerait
   d'interpreter la valeur selon son hypothese anterieure.

> **Regle.** Aucun topic de brulleur ne doit etre publie avant caracterisation
> de la commande **et** existence d'une source de verite contractuelle pour son
> type et son unite.

Le present contrat **ne fixe ni type, ni unite, ni plage** pour ces mesures :
ce serait decider sans preuve.

Par ailleurs, le repli `off` en cas d'echec de parsing pratique par le pont
historique ne doit pas etre reproduit, quel que soit le sort futur de ces
mesures.

**Cout de compatibilite, assume et signale** : un consommateur historique perd
deux entites, dont un capteur binaire de brulleur. Aucun contournement n'est
propose ici — le proposer supposerait la semantique que ce contrat refuse
precisement d'affirmer.

### 4.4 Publication scalaire

- **MUST** publier en QoS 1, retain `true`.
- **MUST** publier **uniquement** apres une lecture dont le statut est `OK`.
- **MUST NOT** publier quoi que ce soit en cas d'echec de lecture.
- **MUST NOT** substituer une valeur sentinelle : ni `0`, ni `false`, ni chaine
  vide, ni `unknown`, ni `null`, ni aucune autre.
- La derniere valeur retenue **MAY** subsister cote broker apres un echec.

> **Regle normative.** Une valeur retenue est **la derniere valeur connue, pas
> necessairement une valeur actuelle**. Un consommateur **MUST** consulter le
> topic de fraicheur (§6) pour en connaitre la validite temporelle.

### 4.5 Representation

Le payload **MUST** etre une **chaine numerique decimale sans unite, utilisant
le point comme separateur et analysable comme un nombre fini**, encodee UTF-8.

Regles fermees pour la v1, afin que deux producteurs conformes ne puissent pas
emettre des formes incompatibles :

| Regle | Decision |
|---|---|
| Separateur decimal | le point **MUST** ; la virgule **MUST NOT** |
| Notation exponentielle | **MUST NOT** — ni `2.8e1`, ni `2.8E1` |
| Espaces, y compris de bordure | **MUST NOT** |
| Guillemets | **MUST NOT** — le payload n'est pas du JSON |
| `NaN`, `Infinity`, `-Infinity` | **MUST NOT** — une valeur non finie n'est pas un succes de lecture et ne donne lieu a aucune publication |
| Zero negatif | une valeur negative nulle **MUST** etre serialisee **sans signe negatif** : `-0` s'ecrit `0`, `-0.0` s'ecrit `0.0`. La regle porte sur le **seul signe** ; elle ne fixe pas la precision |
| Forme entiere ou decimale | **toutes deux autorisees** : `28` et `28.0` sont conformes |
| Signe negatif | autorise pour les mesures dont le domaine l'admet |
| Precision decimale | **non normative** : `28.0` et `28.000000` sont l'un et l'autre conformes |

Un consommateur **MUST** analyser la valeur comme un nombre decimal fini et
**MUST NOT** s'appuyer sur le nombre de chiffres.

Cette forme est compatible avec l'historique, qui emet `28.000000`, et
directement exploitable par un consommateur domotique sans transformation.

### 4.6 Ordre de publication

Apres une lecture reussie, le producteur **MUST** proceder dans cet ordre :

1. publier la nouvelle valeur scalaire ;
2. mettre a jour l'etat interne de la mesure ;
3. publier l'instantane `bridge/telemetry_status`.

**Les deux publications ne sont pas transactionnelles.** Le contrat l'enonce
plutot que de le masquer :

- l'instantane decrit **l'etat de lecture**, non la garantie de livraison du
  scalaire ; `last_result` porte l'issue de la **lecture**, jamais celle de la
  publication MQTT ;
- si la publication scalaire echoue, **aucune compensation ni aucun retour
  arriere n'est exige** — et la valeur ne doit pas etre presentee comme publiee,
  ce que l'instantane ne pretend de toute facon pas ;
- si la publication de l'instantane echoue, aucune compensation n'est exigee :
  la republication periodique (§7.4) retablira l'etat courant.

Aucune taxonomie d'erreur de publication MQTT n'est definie en v1 : la surface
de lecture ne la porte pas.

---

## 5. Presence du bridge

Suffixe : **`bridge/online`**.

| | |
|---|---|
| QoS | **1** |
| Retain | **true** |
| Payload | strictement `online` ou `offline` |
| A la connexion | `online` |
| Testament MQTT | `offline`, QoS 1, retain |
| A l'arret propre | `offline` avant deconnexion |

### Semantique, enoncee sans exageration

> **Le processus bridge est connecte au broker MQTT.**

Ce topic **ne prouve pas** : que `vclient` est lancable · que `vcontrold`
repond · que la liaison Optolink repond · que les mesures sont fraiches · que
la chaudiere est joignable.

Un consommateur **MUST NOT** en deduire la disponibilite de la chaine de
lecture ; celle-ci est portee par §8.

---

## 6. Fraicheur agregee

### 6.1 Choix du topic

Suffixe retenu : **`bridge/telemetry_status`**.

Argumentation, la decision devant etre figee : `telemetry/status` aurait place
un objet JSON de metadonnees au milieu de valeurs scalaires. L'invariant
**« tout ce qui se trouve sous `telemetry/` est une valeur de mesure
scalaire »** a une valeur pratique : il rend sur un abonnement generique
`telemetry/#` toute entree directement exploitable, sans exception a traiter.
Placer les metadonnees sous `bridge/` — ou se trouvent deja presence et
version — preserve cet invariant. Ce choix rejoint par ailleurs la
specification anterieure du projet.

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

Entier, version initiale **`1`**. Une evolution **compatible** — ajout de champ
optionnel, ajout d'une entree de mesure — **MUST NOT** incrementer `schema`. Un
retrait de champ, un changement de type ou de semantique **MUST**
l'incrementer. Un consommateur **MUST** ignorer les champs qu'il ne connait pas
et **MUST** refuser un `schema` majeur inconnu.

### 6.4 `ts`

Instant de construction de l'instantane. **MUST** etre en **UTC**, au format
**RFC 3339** avec suffixe `Z`. Une horloge monotone **MUST NOT** etre exposee :
elle n'a de sens que dans le processus.

### 6.5 Modele de mesure — deux dimensions, jamais fusionnees

Deux modeles ont ete compares.

| | Enumere unique `ok` / `stale` / `error` / `never` | Champs orthogonaux |
|---|---|---|
| Mesure ancienne **et** derniere tentative en erreur | **impossible a exprimer** : il faut choisir | exprime : `fresh: false` + `last_result: "timeout"` |
| Lisibilite immediate | meilleure | demande une lecture de trois champs |
| Extension | ajouter un etat casse les consommateurs | ajouter un champ ne casse rien |

Ces deux dimensions — **ai-je une valeur, est-elle fraiche** d'une part, **qu'a
donne la derniere tentative** d'autre part — sont independantes et doivent le
rester. Le modele enumere unique les ecrase.

> **Decision : modele a champs orthogonaux.** Aucun champ `status` par mesure
> n'est defini : il reintroduirait l'ecrasement qu'on cherche a eviter. Le
> signal synthetique existe au niveau de la chaine (§8), pas de la mesure.

| Champ | Type | Semantique |
|---|---|---|
| `has_value` | booleen | une valeur scalaire a ete publiee au moins une fois depuis le demarrage |
| `fresh` | booleen | `age_s` est inferieur ou egal au seuil de fraicheur de la mesure (§7) |
| `last_success` | RFC 3339 UTC, ou `null` | instant de la derniere lecture reussie |
| `age_s` | entier ≥ 0, ou `null` | anciennete de `last_success` a l'instant `ts` |
| `last_result` | enumere (§6.6) ou `null` | issue de la **derniere tentative**, `null` si aucune tentative |

Invariants **MUST** : `has_value` vrai equivaut a `last_success` non nul ·
`age_s` nul si et seulement si `last_success` est nul · `fresh` vrai implique
`has_value` vrai · une mesure jamais lue avec succes porte
`has_value: false`, `fresh: false`, `last_success: null`, `age_s: null`.

**Aucun champ `last_attempt` n'est defini en v1.** Consequence, enoncee
franchement :

> La distinction entre une valeur ancienne sans tentative recente et une valeur
> ancienne apres plusieurs echecs recents n'est pas exposee en v1 ; elle releve
> d'une eventuelle surface de sante detaillee ulterieure.

Seuls `last_success`, `age_s` et `last_result` sont portes.

### 6.6 Taxonomie publique de `last_result`

Valeurs **stables et contractuelles** :

```
ok · timeout · daemon_unreachable · unusable_output ·
unsupported_command · transport_error
```

Correspondance **actuelle** avec les issues internes — elle **MAY** evoluer,
les valeurs publiques restant stables :

| Interne | Public |
|---|---|
| `OK` | `ok` |
| `TIMEOUT` | `timeout` |
| `DAEMON_UNREACHABLE` | `daemon_unreachable` |
| `UNUSABLE_OUTPUT` | `unusable_output` |
| `UNKNOWN_COMMAND` | `unsupported_command` |
| `TRANSPORT_ERROR` | `transport_error` |

> **Limite honnete.** Un echec de lancement du client local est aujourd'hui
> classe `TRANSPORT_ERROR` — `CLIENT_UNAVAILABLE` n'etant pas ratifie. La
> taxonomie publique **ne distingue donc pas** « client non lancable » de
> « autre erreur de transport ». Aucune valeur publique n'est definie pour
> cette distinction tant qu'elle n'est pas representable.

Interdictions : **MUST NOT** publier un message systeme brut, un chemin local,
un `stderr` complet, un nom d'exception, ni tout detail susceptible de varier
selon la version du client ou du systeme.

---

## 7. Politique de fraicheur

### 7.1 Pourquoi les seuils ne sont pas repris de l'historique

Les cadences **configurees** du pont historique (10 s et 30 s) ne correspondent
pas aux cadences **mesurees** (≈ 19-21 s et ≈ 40 s) : la duree du cycle de
lecture allonge la boucle. Un seuil de 60 s, herite de l'historique, ne
tolerait donc **qu'un seul** cycle manque au lieu des deux escomptes.

Le contrat **MUST NOT** figer un seuil absolu par inertie. Il le definit
**relativement a la periode**.

### 7.2 Definitions

Pour chaque mesure de periode cible `P` :

| Parametre | Regle |
|---|---|
| `fresh_max` | seuil de fraicheur, en secondes. Defaut **`3 × P`** |
| Invariant | `fresh_max` **MUST** etre strictement superieur a `P` |
| Configurabilite | `fresh_max` **MAY** etre configure par mesure ou globalement |
| Unite | secondes, entier positif |

Le facteur **3** est retenu, et non 2, parce que la duree d'une lecture reelle
observee — 2,7 a 4,0 s — est du meme ordre que certaines periodes : un facteur
2 laisserait une marge d'un seul cycle.

### 7.3 Comportements

| Situation | Comportement **MUST** |
|---|---|
| Apres demarrage, avant la premiere lecture | aucune publication scalaire ; instantane publie avec `has_value: false`, `fresh: false`, `last_result: null` |
| Echec isole | aucune publication scalaire ; `last_result` mis a jour ; `fresh` reste vrai tant que `age_s ≤ fresh_max` |
| Echecs repetes jusqu'au depassement | `fresh` devient faux ; le scalaire retenu subsiste ; l'instantane porte la cause |
| Reprise apres echec | publication scalaire, `last_success` et `age_s` remis a jour, `last_result` a `ok`, `fresh` a vrai |

### 7.4 Cadence de l'instantane

L'instantane **MUST** etre republie a intervalle regulier **meme si rien n'a
change**, avec un `ts` a jour. Sans cette regle, un consommateur ne pourrait
pas distinguer un bridge fige d'un bridge dont rien n'a bouge.

Periode de republication : **MUST** etre inferieure ou egale au plus petit
`fresh_max` de la surface. **SHOULD** valoir la plus petite periode cible.

---

## 8. Etat synthetique de la chaine de lecture

### 8.1 Ce que ce contrat refuse de reproduire

Le pont historique publie `vcontrold_status` et `optolink_status` derives
**d'une seule sonde**. Deux topics, une seule verite. Le contrat **MUST NOT**
reproduire cette projection.

Il **MUST NOT** non plus affirmer une distinction entre « demon joignable » et
« Optolink fonctionnel » : C5 et C6 permettent de distinguer *demon injoignable*
de *reponse inexploitable*, mais **ne permettent pas** d'attribuer une reponse
inexploitable a la liaison plutot qu'a la chaudiere.

### 8.2 Signal unique

Un seul signal, dans l'instantane agrege, sous `chain`.

**Definition — cycle de lecture.** Une **tentative planifiee de lecture de
l'ensemble des mesures v1 dues a cet instant**. Un cycle est **termine** lorsque
chacune de ces tentatives a rendu une issue, quelle qu'elle soit.

| `status` | Condition |
|---|---|
| `ok` | au moins une mesure lue avec succes lors du dernier cycle termine, **et** aucune tentative en echec lors de ce cycle |
| `degraded` | au moins une reussite **et** au moins un echec lors du dernier cycle termine |
| `unavailable` | aucune lecture reussie lors du dernier cycle termine, **ou** aucun cycle termine a ce jour |

**Avant le premier cycle termine**, l'instantane **MUST** porter :

```json
{ "status": "unavailable", "cause": null }
```

Semantique exacte de cet etat initial : **aucune conclusion sur la chaudiere**,
aucune lecture encore achevee, la chaine de lecture n'a simplement pas encore
produit de resultat. `cause` est `null` parce qu'aucun echec n'a ete observe —
l'absence de resultat n'est pas un echec.

**Transition.** Des la fin du premier cycle, `status` prend la valeur derivee
du tableau ci-dessus, et `cause` celle de la regle ci-dessous.

Trois etats, pas davantage : ils recouvrent les cas actionnables sans en
inventer.

`chain.cause` : `null` si `status` vaut `ok` ; sinon la valeur de
`last_result` la plus severe observee au dernier cycle, selon l'ordre

```
daemon_unreachable > transport_error > timeout > unusable_output > unsupported_command
```

Cet ordre place en tete ce qui affecte toute la chaine, et en queue ce qui
n'affecte qu'une commande.

> `chain` est **derive de l'ensemble des mesures reellement tentees**, jamais
> d'une sonde dediee. C'est ce qui le distingue du modele historique.

### 8.3 Aucun topic scalaire de sante

`bridge/vcontrold_status` et `bridge/optolink_status` **MUST NOT** etre
publies. Voir la matrice §13 pour le cout de compatibilite.

---

## 9. Battement

Suffixe historique : `bridge/heartbeat`, QoS 0, non retenu, payload
`{"ts":…}`.

**Analyse.** Dans le modele retenu, la presence est portee par le testament et
le topic retenu, et la vitalite du processus par la republication periodique de
l'instantane (§7.4), qui porte deja un `ts`. Le battement est donc
**techniquement redondant**.

Il conserve neanmoins un **consommateur prouve** : le consommateur d'origine en
derive un etat degrade par l'age du dernier battement. Le supprimer romprait ce
consommateur, alors meme que le defaut `boiler` a ete retenu pour preserver la
compatibilite.

> **Decision : conserve en `SHOULD`, pour compatibilite historique uniquement.**
> QoS 0, non retenu, payload `{"ts":"…"}` en RFC 3339 UTC.

Conditions de cette conservation, toutes explicites :

- il est conserve **au titre de la compatibilite historique**, pas de son
  utilite propre ;
- sa **redondance** avec le testament et l'instantane est **assumee** ;
- il **ne porte aucune autorite fonctionnelle** : aucune decision ne doit en
  dependre ;
- il est **candidat a la depreciation** des lors que l'instantane sera consomme ;
- **aucune sante de la chaudiere ne doit en etre deduite** : il n'atteste que de
  l'activite du processus.

Un producteur **MAY** l'omettre s'il documente la rupture. Ce topic **n'est pas
indispensable**.

---

## 10. Capacites — hors v1

Aucun topic `capabilities` n'est defini par ce contrat. Aucun
consommateur reel n'a ete identifie, et le pont historique n'en publie pas.
Le sujet est reporte sans prejuger de sa valeur future.

---

## 11. Recapitulatif des topics v1

Suffixes contractuels, prefixe omis.

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
| `bridge/heartbeat` | 0 | ✖ | JSON `{"ts":…}` — `SHOULD`, compatibilite |

**Onze topics** au total, dont **huit mesures**. Ils ne sont pas tous
obligatoires : **dix topics requis** (**MUST**) et **un topic recommande**
(**SHOULD**), `bridge/heartbeat`, conserve au seul titre de la compatibilite
historique et omissible par un producteur qui documente la rupture (§9).

Tout autre topic **MUST NOT** etre publie par la surface de lecture.

---

## 12. Interdictions transverses

Le contrat **MUST NOT** :

- assimiler « valeur absente », « valeur inconnue » et « valeur fausse » ;
- publier `0` ou toute sentinelle a la place d'une erreur ;
- presenter une valeur retenue comme fraiche sans le topic de fraicheur ;
- faire dependre un etat de sante d'une seule valeur metier sans l'expliciter ;
- deduire une capacite d'ecriture de la seule presence d'une commande ;
- annoncer `online` alors que seule la connexion MQTT est etablie **et** laisser
  croire que la chaine de lecture fonctionne — d'ou §5 et §8 ;
- melanger acquittements transactionnels et telemetrie ;
- introduire un chemin d'ecriture.

---

## 13. Matrice de compatibilite

| Topic historique | Identique | Nouvelle semantique | Remplace | Reporte | Justification |
|---|:-:|:-:|:-:|:-:|---|
| `telemetry/temperatures/outdoor` | ✔ | | | | nom, QoS, retain, payload conserves |
| `telemetry/temperatures/supply` | ✔ | | | | idem |
| `telemetry/temperatures/dhw` | ✔ | | | | idem |
| `telemetry/dhw/setpoint` | ✔ | | | | idem |
| `telemetry/heating/setpoint` | ✔ | | | | idem |
| `telemetry/heating/reduced_reference` | ✔ | | | | idem |
| `telemetry/heating/curve/slope` | ✔ | | | | idem |
| `telemetry/heating/curve/shift` | ✔ | | | | idem |
| `telemetry/burner/modulation` | | | | **✔** | commande non caracterisee ; type et unite non etablis — **perte d'entite** cote consommateur |
| `telemetry/burner/state` | | | | **✔** | derive d'une mesure elle-meme reportee ; repli `off` refuse — **perte d'entite** cote consommateur |
| `bridge/online` | ✔ | | | | nom, QoS, retain, testament, payload conserves |
| `bridge/heartbeat` | ✔ | | | | conserve en `SHOULD`, declare redondant |
| `bridge/version` | | | | **✔** | non retenu en v1 : information de diagnostic sans consommateur decisionnel |
| `bridge/vcontrold_status` | | | **✔** | | remplace par `chain` dans l'instantane — **rupture** : le topic disparait |
| `bridge/optolink_status` | | | **✔** | | idem |
| `error/last` | | | | **✔** | lie au chemin d'ecriture, hors surface de lecture |
| `guard/*` | | | | **✔** | supervision correctrice hors perimetre du produit |

> **Lecture de la matrice.** La colonne « Reporte » recouvre **deux cas
> distincts**, detailles plus bas : *reporte faute de preuve* — le topic pourrait
> revenir — et *hors perimetre* — il n'a jamais releve de ce contrat.
>
> Sur les **16** topics historiques **individuels** hors guard :
> **10** conserves a l'identique · **2** remplaces · **3** reportes faute de
> preuve (`telemetry/burner/modulation`, `telemetry/burner/state`,
> `bridge/version`) · **1** hors perimetre (`error/last`).
>
> La dix-septieme ligne, `guard/*`, est une **ligne groupee supplementaire**,
> elle aussi hors perimetre, et **n'entre pas** dans le decompte de 16.

**Compatibilite de nom** : sur les **16** topics historiques hors guard,
**10** conservent leur nom, **tous a l'identique** — aucun topic n'est conserve
avec une semantique modifiee. **Compatibilite de QoS et de retain** : conservee
sur ces 10 topics. **Compatibilite de payload** : conservee sur les 8 mesures
retenues.
**Compatibilite semantique** : conservee sur **tous** les topics retenus.
Aucun topic n'est conserve avec une semantique modifiee — c'est precisement ce
qu'a permis le report des mesures de brulleur.

Trois categories distinctes, a ne pas confondre :

| Categorie | Topics | Sens |
|---|---|---|
| **Rupture de la surface de lecture** | `vcontrold_status`, `optolink_status` | le topic disparait ; l'information est portee autrement, par `chain` |
| **Reporte faute de preuve** | `burner/modulation`, `burner/state`, `bridge/version` | le topic pourrait revenir ; rien n'est decide contre lui |
| **Hors perimetre de la surface de lecture** | `error/last`, `guard/*` | jamais du ressort de ce contrat |

`bridge/version` figure parmi les reports et non parmi les ruptures : rien ne
s'oppose a sa publication, il n'a simplement aucun consommateur decisionnel
identifie a ce jour.

---

## 14. Interaction avec la surface transactionnelle

- La surface de lecture est **separee** des commandes et des acquittements.
- Un topic de lecture **MUST NOT** declencher d'action.
- Aucun statut de lecture ne vaut acquittement.
- Aucune absence de mesure ne produit de commande.
- Ce contrat **ne modifie ni C3 ni C4**.

**Divergence enregistree, non tranchee ici.** Le code actuel publie sous
`boilerack/command` et `boilerack/ack`, alors que la surface de lecture aura
pour defaut `boiler`. Cette incoherence de namespace entre les deux surfaces
est **reelle** et devra etre arbitree. Elle **MUST NOT** l'etre dans ce contrat
de lecture, qui porterait alors sur l'ecriture.

> **Dette enregistree.** Avant toute composition root publique, le projet devra
> arbitrer la convergence des namespaces transactionnel et de lecture. C7-B
> **n'autorise pas** une coexistence permanente sans decision.

---

## 15. Inconnues restantes

| # | Inconnue | Consequence |
|---|---|---|
| 1 | **Comportement d'une ecriture `set…`** | bloque tout le chemin d'ecriture |
| 2 | Distinction chaudiere / liaison Optolink | `chain` ne peut pas l'exprimer |
| 3 | Distinction « client non lancable » / autre erreur de transport | absente de la taxonomie publique |
| 4 | Semantique des signatures sur une autre version du client | contrat valable pour la version caracterisee |
| 5 | Politique de retention et expiration de session du broker | non deductible du code |
| 6 | Consommateurs exacts de `outdoor` et `reduced_reference` | aucun identifie ; conserves par prudence |
| 7 | Valeur reelle d'un topic de capacites | reporte |
| 8 | **Semantique, type et unite de `getBrennerStatus`** — commande observee dans le pont historique, **non caracterisee par C5** ; la dependance a la regulation est **alleguee** a partir du pont historique, non prouvee dans le depot public | bloque `burner_modulation` **et** `burner_state` |
| 9 | Cadences reelles atteignables par le futur publieur | les periodes cibles sont des objectifs, non des garanties |

---

## 16. Perimetre

Ce document est **documentaire**. Il ne cree aucun topic, ne publie rien,
n'implemente aucune validation. La normalisation du prefixe (§3.3), la
publication (§4.4), l'instantane (§6) et la politique de fraicheur (§7) seront
implementes en C7-C, hors ligne, sur doubles et fixtures.

Aucun acces production n'a ete effectue pour rediger ce contrat : il est
integralement derive du depot public et du depot historique, lus en lecture
seule.
