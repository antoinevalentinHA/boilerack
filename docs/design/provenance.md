# Provenance du code caracterise

Document interne de conception. Il etablit la tracabilite entre les primitives
reprises dans `src/boilerack/_legacy/` et l'implementation de production dont
elles proviennent.

## Pourquoi ce document

`boilerack` ne reecrit pas un produit theorique. Il descend d'une
implementation qui tourne en production et dont le comportement a ete audite.
La demarche est :

> etablir d'abord, par des tests executables, ce que l'implementation de
> production garantit reellement, puis extraire et factoriser sous ce filet
> de securite.

Ce document rend cette filiation verifiable. La licence MIT couvre le code
publie par son auteur ; la provenance technique reste explicite pour montrer
que le produit descend bien de l'implementation eprouvee, et non d'une
reconstruction de memoire.

## Source

| | |
|---|---|
| Depot | `antoinevalentinHA/boiler-bridge` (prive) |
| Fichier | `boiler_mqtt.py` |
| Blob | `992f9efa5d063dee7b0ccdec17351739b7371a1b` |
| Dernier commit l'ayant modifie | `f14ba5c8498d3fc1706a4634ef5512a2af095bda` — *feat: enforce strict curve validation and final ACK dedup*, 2026-03-27 |
| `origin/main` au moment de la reprise | `12138249643888de930538796addf70c60dc33fa` |
| Version declaree par le composant | `v0.5` |

Le fichier n'a pas ete modifie depuis le 27 mars 2026. Les commits ulterieurs
du depot portent sur le guard, le deploiement et la sauvegarde.

## Regle de reprise

Aucun secret, chemin local, identifiant reseau ni constante de site n'est
repris. Sont exclus par principe : les variables d'environnement propres au
deploiement d'origine, l'identifiant client MQTT, les hotes et ports, les
chemins absolus du systeme de fichiers, les noms de topics, les unites
systemd, et toute logique de transport, de sous-processus ou de reseau.

## Matrice des fonctions auditees

Quatre decisions possibles : **copie litterale** · **adaptation mecanique**
(corps reproduit, enveloppe nouvelle) · **non importe** · **inexistant**
(candidat pressenti qui ne correspond a aucune fonction reelle).

| Nom d'origine | Lignes | Pure | Entrees | Sorties | Sentinelle / exception | Effets de bord | Decision |
|---|---|---|---|---|---|---|---|
| `utc_now` | 111-112 | non — horloge | aucune | `datetime` aware UTC | aucune | lecture de l'horloge | **copie litterale** |
| `utc_now_iso` | 115-117 | non — horloge | aucune | `str` `…Z` | aucune | idem | **copie litterale** |
| `parse_iso8601` | 120-131 | oui | `str` | `datetime` UTC | `ValueError` | aucun | **copie litterale** |
| `json_dumps` | 134-135 | oui | `dict` | `str` compact | `TypeError` si non serialisable | aucun | **copie litterale** |
| `validate_uuid4_string` | 526-535 | oui | `Any` | `bool` | aucune — `except Exception` absorbe tout | aucun | **copie litterale** |
| `sanitize_curve_slope` | 386-426 | **non** — `print` | `Any` | `(bool, str\|None, float\|None)` | aucune | **ecrit sur stdout** | **copie litterale**, defaut inclus |
| `sanitize_curve_shift` | 429-469 | **non** — `print` | `Any` | `(bool, str\|None, int\|None)` | aucune | **ecrit sur stdout** | **copie litterale**, defaut inclus |
| Constantes de domaine | 63-64, 76-77, 83-89 | — | — | — | — | — | **copie litterale**, destinees au profil en C3 |
| Condition d'expiration | 569, 625, 681, 730 | oui | 2 `datetime` | `bool` | aucune | aucun | **adaptation mecanique** → `legacy_is_expired` |
| Validation de valeur des consignes | 572-581, 628-637 | oui | `Any`, bornes | `(bool, str\|None, int\|None)` | **`ValueError` / `OverflowError` non gerees** | aucun | **adaptation mecanique** → `legacy_setpoint_value` |
| Corps de `publish_ack` | 335-343 | oui | 4 `str` | `dict` | aucune | aucun | **adaptation mecanique** → `legacy_build_ack_payload` |
| Corps de `publish_error` | 356-363 | oui | 6 champs | `dict` | aucune | aucun | **adaptation mecanique** → `legacy_build_error_payload` |
| `publish_ack` / `publish_error` entiers | 328-366 | non | + client MQTT | `dict` | aucune | **publication MQTT** | **non importe** — transport |
| `validate_*_payload` × 4 | 538-745 | oui | `Any` | tuple | aucune | aucun | **non importe** — a factoriser en C3, hors perimetre C1 |
| `run_vclient`, `get_value`, `get_float_value` | 142-189 | non | — | — | `None` absorbant toute cause | **sous-processus** | **non importe** |
| `set_*` / `confirm_*` × 8 | 202-295 | non | — | — | — | **sous-processus, sommeil** | **non importe** |
| `handle_*_command` × 4 | 752-1234 | non | — | — | — | **MQTT, ecriture chaudiere** | **non importe** |
| Cache de deduplication | 476-519 | non | — | — | — | **etat global, verrou** | **non importe** — modele revu en C3 |
| Callbacks MQTT, `main`, telemetrie | 1241-1403 | non | — | — | — | **reseau, threads** | **non importe** |
| « Fonction pure de construction d'ACK » | — | — | — | — | — | — | **inexistant** — la construction est inline dans `publish_ack`, d'ou l'adaptation mecanique |
| « Fonction de logique de pas » | — | — | — | — | — | — | **inexistant** — le controle de pas est inline dans chaque assainisseur, il n'a pas d'existence autonome |

### Nature exacte des adaptations

Aucun changement de comportement n'a ete introduit. Les quatre adaptations sont
strictement enveloppantes :

| Adaptation | Ce qui change | Ce qui ne change pas |
|---|---|---|
| `legacy_is_expired` | l'horloge devient un parametre au lieu d'un appel a `utc_now()` | le comparateur strict `>` |
| `legacy_setpoint_value` | les bornes deviennent des parametres au lieu de constantes globales | l'arrondi, l'ordre des gardes, les codes de retour, l'absence de garde NaN/Inf |
| `legacy_build_ack_payload` | la publication MQTT est retiree | l'ordre d'insertion des cles, l'omission de `reason` |
| `legacy_build_error_payload` | idem | l'ordre des cles, `request_id` a `null` |

Aucun renommage de champ, aucune valeur modifiee, aucun controle ajoute ni
retire.

## Classification des comportements caracterises

| Classe | Sens | Nombre de tests |
|---|---|---|
| `REFERENCE` | comportement eprouve, a conserver | 135 |
| `ACCIDENT` | comportement actuel non souhaite, caracterise sans devenir normatif | 9 |
| `DIVERGENCE_RATIFIED` | comportement qui changera selon D-1 a D-10 | 6 |
| `UNKNOWN` | comportement observe dont le sens n'est pas demontre | 1 |

Les marqueurs `pytest` correspondants sont declares dans `pyproject.toml` et
`--strict-markers` est actif : un marqueur mal orthographie fait echouer la
suite.

### Accidents releves

1. **`validate_uuid4_string` accepte les majuscules.** La comparaison finale
   abaisse la casse de l'entree. Le contrat du consommateur d'origine decrit pourtant une forme
   canonique minuscule « validee strictement ». A trancher en C3.
2. **Les formes URN et entre accolades sont rejetees par effet de bord** de la
   comparaison, non par une validation de forme.
3. **`sanitize_curve_slope` et `sanitize_curve_shift` ecrivent sur la sortie
   standard** sur tous leurs chemins. Elles ne sont donc pas des fonctions
   pures et ne peuvent pas etre utilisees telles quelles dans une
   bibliotheque.
4. **NaN et l'infini ne sont pas geres sur le chemin des consignes.**
   `int(round(float('nan')))` leve `ValueError`, l'infini leve
   `OverflowError`. L'exception remonte au gestionnaire de commande, qui
   publie `bridge_exception` puis un ACK `rejected` / `bridge_unavailable` —
   soit une raison **transitoire** pour une erreur **permanente**. Les
   fonctions de courbe, elles, rendent proprement `invalid_type`.
5. **`legacy_build_ack_payload` n'exerce aucun controle** sur le statut ni sur
   la raison : toute chaine passe.
6. **`json_dumps` emet `NaN` et `Infinity`**, qui ne sont pas du JSON valide.
   Non atteignable aujourd'hui, aucun payload ne portant de flottant.

### Divergences deja ratifiees, caracterisees ici

| Test | Comportement actuel | Divergence |
|---|---|---|
| expiration a l'instant exact | non expire (`>`) | **D-8** — alignement sur `>=` |
| valeur de consigne non entiere | arrondie et acceptee | **D-1 / P-02** — rejet strict |

Ces tests figent le comportement **reel**. Lorsque C3 appliquera les
divergences, ils devront etre inverses de facon visible et tracee — jamais par
une correction silencieuse.

### Point non demontre

Le decalage de courbe accepte la valeur `0`, qui appartient a l'intervalle
`[-13 ; 40]`. Aucune source consultee n'etablit son sens physique. Classe
`UNKNOWN`.

## Observations d'ordre de controle

Deux comportements decouverts par les tests, non documentes jusqu'ici :

1. **L'ordre des controles differe entre les deux assainisseurs.** La pente
   verifie les bornes puis le pas ; le decalage verifie le pas puis les
   bornes. Une valeur a la fois hors bornes et hors pas rend donc des
   diagnostics differents selon la commande. A unifier en C3.
2. **Une valeur sous la borne basse de pente peut etre rejetee pour le pas.**
   `0.19` se normalise en `0.2`, qui satisfait les bornes ; le rejet survient
   au controle suivant avec la raison `invalid_step`. Le controle de bornes
   porte sur la valeur normalisee, pas sur l'entree.

## Perimetre de C1

Ce lot ne produit ni coeur transactionnel generique, ni profil declaratif, ni
transport MQTT, ni ordonnanceur, ni faux `vclient`, ni CLI. Le paquet
`_legacy` est interne et provisoire : son contenu sera factorise en C3, apres
quoi il disparaitra.
