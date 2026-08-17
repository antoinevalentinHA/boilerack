# Provenance du code caractérisé

Document interne de conception. Il établit la traçabilité entre les primitives
reprises dans `src/boilerack/_legacy/` et l'implémentation de production dont
elles proviennent.

## Pourquoi ce document

`boilerack` ne réécrit pas un produit théorique. Il descend d'une
implémentation qui tourne en production et dont le comportement a été audité.
La démarche est :

> établir d'abord, par des tests exécutables, ce que l'implémentation de
> production garantit réellement, puis extraire et factoriser sous ce filet
> de sécurité.

Ce document rend cette filiation vérifiable. La licence MIT couvre le code
publié par son auteur ; la provenance technique reste explicite pour montrer
que le produit descend bien de l'implémentation éprouvée, et non d'une
reconstruction de mémoire.

## Source

| | |
|---|---|
| Dépôt | `antoinevalentinHA/boiler-bridge` (privé) |
| Fichier | `boiler_mqtt.py` |
| Blob | `992f9efa5d063dee7b0ccdec17351739b7371a1b` |
| Dernier commit l'ayant modifié | `f14ba5c8498d3fc1706a4634ef5512a2af095bda` — *feat: enforce strict curve validation and final ACK dedup*, 2026-03-27 |
| `origin/main` au moment de la reprise | `12138249643888de930538796addf70c60dc33fa` |
| Version déclarée par le composant | `v0.5` |

Le fichier n'a pas été modifié depuis le 27 mars 2026. Les commits ultérieurs
du dépôt portent sur le guard, le déploiement et la sauvegarde.

## Règle de reprise

Aucun secret, chemin local, identifiant réseau ni constante de site n'est
repris. Sont exclus par principe : les variables d'environnement propres au
déploiement d'origine, l'identifiant client MQTT, les hôtes et ports, les
chemins absolus du système de fichiers, les noms de topics, les unités
systemd, et toute logique de transport, de sous-processus ou de réseau.

## Matrice des fonctions auditées

Quatre décisions possibles : **copie littérale** · **adaptation mécanique**
(corps reproduit, enveloppe nouvelle) · **non importé** · **inexistant**
(candidat pressenti qui ne correspond à aucune fonction réelle).

| Nom d'origine | Lignes | Pure | Entrées | Sorties | Sentinelle / exception | Effets de bord | Décision |
|---|---|---|---|---|---|---|---|
| `utc_now` | 111-112 | non — horloge | aucune | `datetime` aware UTC | aucune | lecture de l'horloge | **copie littérale** |
| `utc_now_iso` | 115-117 | non — horloge | aucune | `str` `…Z` | aucune | idem | **copie littérale** |
| `parse_iso8601` | 120-131 | oui | `str` | `datetime` UTC | `ValueError` | aucun | **copie littérale** |
| `json_dumps` | 134-135 | oui | `dict` | `str` compact | `TypeError` si non sérialisable | aucun | **copie littérale** |
| `validate_uuid4_string` | 526-535 | oui | `Any` | `bool` | aucune — `except Exception` absorbe tout | aucun | **copie littérale** |
| `sanitize_curve_slope` | 386-426 | **non** — `print` | `Any` | `(bool, str\|None, float\|None)` | aucune | **écrit sur stdout** | **copie littérale**, défaut inclus |
| `sanitize_curve_shift` | 429-469 | **non** — `print` | `Any` | `(bool, str\|None, int\|None)` | aucune | **écrit sur stdout** | **copie littérale**, défaut inclus |
| Constantes de domaine | 63-64, 76-77, 83-89 | — | — | — | — | — | **copie littérale**, destinées au profil en C3 |
| Condition d'expiration | 569, 625, 681, 730 | oui | 2 `datetime` | `bool` | aucune | aucun | **adaptation mécanique** → `legacy_is_expired` |
| Validation de valeur des consignes | 572-581, 628-637 | oui | `Any`, bornes | `(bool, str\|None, int\|None)` | **`ValueError` / `OverflowError` non gérées** | aucun | **adaptation mécanique** → `legacy_setpoint_value` |
| Corps de `publish_ack` | 335-343 | oui | 4 `str` | `dict` | aucune | aucun | **adaptation mécanique** → `legacy_build_ack_payload` |
| Corps de `publish_error` | 356-363 | oui | 6 champs | `dict` | aucune | aucun | **adaptation mécanique** → `legacy_build_error_payload` |
| `publish_ack` / `publish_error` entiers | 328-366 | non | + client MQTT | `dict` | aucune | **publication MQTT** | **non importé** — transport |
| `validate_*_payload` × 4 | 538-745 | oui | `Any` | tuple | aucune | aucun | **non importé** — à factoriser en C3, hors périmètre C1 |
| `run_vclient`, `get_value`, `get_float_value` | 142-189 | non | — | — | `None` absorbant toute cause | **sous-processus** | **non importé** |
| `set_*` / `confirm_*` × 8 | 202-295 | non | — | — | — | **sous-processus, sommeil** | **non importé** |
| `handle_*_command` × 4 | 752-1234 | non | — | — | — | **MQTT, écriture chaudière** | **non importé** |
| Cache de deduplication | 476-519 | non | — | — | — | **état global, verrou** | **non importé** — modèle revu en C3 |
| Callbacks MQTT, `main`, télémétrie | 1241-1403 | non | — | — | — | **réseau, threads** | **non importé** |
| « Fonction pure de construction d'ACK » | — | — | — | — | — | — | **inexistant** — la construction est inline dans `publish_ack`, d'où l'adaptation mécanique |
| « Fonction de logique de pas » | — | — | — | — | — | — | **inexistant** — le contrôle de pas est inline dans chaque assainisseur, il n'a pas d'existence autonome |

### Nature exacte des adaptations

Aucun changement de comportement n'a été introduit. Les quatre adaptations sont
strictement enveloppantes :

| Adaptation | Ce qui change | Ce qui ne change pas |
|---|---|---|
| `legacy_is_expired` | l'horloge devient un paramètre au lieu d'un appel à `utc_now()` | le comparateur strict `>` |
| `legacy_setpoint_value` | les bornes deviennent des paramètres au lieu de constantes globales | l'arrondi, l'ordre des gardes, les codes de retour, l'absence de garde NaN/Inf |
| `legacy_build_ack_payload` | la publication MQTT est retirée | l'ordre d'insertion des clés, l'omission de `reason` |
| `legacy_build_error_payload` | idem | l'ordre des clés, `request_id` à `null` |

Aucun renommage de champ, aucune valeur modifiée, aucun contrôle ajouté ni
retiré.

## Classification des comportements caractérisés

| Classe | Sens | Nombre de tests |
|---|---|---|
| `REFERENCE` | comportement éprouvé, à conserver | 133 |
| `ACCIDENT` | comportement actuel non souhaité, caractérisé sans devenir normatif | 9 |
| `DIVERGENCE_RATIFIED` | comportement qui changera selon D-1 à D-10 | 6 |
| `UNKNOWN` | comportement observé dont le sens n'est pas démontré | 3 |

Les marqueurs `pytest` correspondants sont déclarés dans `pyproject.toml` et
`--strict-markers` est actif : un marqueur mal orthographié fait échouer la
suite.

### Accidents relevés

1. **`validate_uuid4_string` accepte les majuscules.** La comparaison finale
   abaisse la casse de l'entrée. Le contrat du consommateur d'origine décrit pourtant une forme
   canonique minuscule « validée strictement ». À trancher en C3.
2. **Les formes URN et entre accolades sont rejetées par effet de bord** de la
   comparaison, non par une validation de forme.
3. **`sanitize_curve_slope` et `sanitize_curve_shift` écrivent sur la sortie
   standard** sur tous leurs chemins. Elles ne sont donc pas des fonctions
   pures et ne peuvent pas être utilisées telles quelles dans une
   bibliothèque.
4. **NaN et l'infini ne sont pas gérés sur le chemin des consignes.**
   `int(round(float('nan')))` lève `ValueError`, l'infini lève
   `OverflowError`. L'exception remonte au gestionnaire de commande, qui
   publie `bridge_exception` puis un ACK `rejected` / `bridge_unavailable` —
   soit une raison **transitoire** pour une erreur **permanente**. Les
   fonctions de courbe, elles, rendent proprement `invalid_type`.
5. **`legacy_build_ack_payload` n'exerce aucun contrôle** sur le statut ni sur
   la raison : toute chaîne passe.
6. **`json_dumps` émet `NaN` et `Infinity`**, qui ne sont pas du JSON valide.
   Non atteignable aujourd'hui, aucun payload ne portant de flottant.

### Divergences déjà ratifiées, caractérisées ici

| Test | Comportement actuel | Divergence |
|---|---|---|
| expiration à l'instant exact | non expiré (`>`) | **D-8** — alignement sur `>=` |
| valeur de consigne non entière | arrondie et acceptée | **D-1 / P-02** — rejet strict |

Ces tests figent le comportement **réel**. Lorsque C3 appliquera les
divergences, ils devront être inversés de façon visible et tracée — jamais par
une correction silencieuse.

### Points non démontrés

Trois comportements sont classés `UNKNOWN` — observés, mais dont le sens ou le
caractère contractuel n'est pas établi :

1. Le décalage de courbe accepte la valeur `0`, qui appartient à l'intervalle
   `[-13 ; 40]`. Aucune source consultée n'établit son sens physique.
2. Le diagnostic rendu par `sanitize_curve_shift` quand une valeur viole à la
   fois les bornes ET le pas (`invalid_step`) dépend de l'ordre des contrôles,
   non d'un contrat.
3. Le diagnostic symétrique de `sanitize_curve_slope`
   (`invalid_value_out_of_range` dans le même cas de figure).

Les points 2 et 3 étaient auparavant classés `REFERENCE`. Les compter parmi les
comportements « à conserver » aurait figé un artefact d'ordre en contrat, alors
que l'unification prévue en C3 le fera changer. Le rejet des valeurs simplement
hors bornes reste, lui, couvert par des tests `REFERENCE` dédiés.

## Observations d'ordre de contrôle

Deux comportements découverts par les tests, non documentés jusqu'ici :

1. **L'ordre des contrôles diffère entre les deux assainisseurs.** La pente
   vérifie les bornes puis le pas ; le décalage vérifie le pas puis les
   bornes. Une valeur à la fois hors bornes et hors pas rend donc des
   diagnostics différents selon la commande. À unifier en C3 : les deux tests
   qui figent ce diagnostic sont classés `UNKNOWN`, pas `REFERENCE`.
2. **Une valeur sous la borne basse de pente peut être rejetée pour le pas.**
   `0.19` se normalise en `0.2`, qui satisfait les bornes ; le rejet survient
   au contrôle suivant avec la raison `invalid_step`. Le contrôle de bornes
   porte sur la valeur normalisée, pas sur l'entrée.

## Périmètre de C1

Ce lot ne produit ni coeur transactionnel générique, ni profil déclaratif, ni
transport MQTT, ni ordonnanceur, ni faux `vclient`, ni CLI. Le paquet
`_legacy` est interne et provisoire : son contenu sera factorisé en C3, après
quoi il disparaîtra.
