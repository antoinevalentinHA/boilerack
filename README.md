# boilerack

Pont MQTT transactionnel au-dessus d'un `vcontrold` existant, pour chaudières
Viessmann équipées d'une liaison Optolink.

> **État : en construction. Rien n'est publiable ni utilisable à ce stade.**
> Aucune prerelease n'a été diffusée.

Les contrats de construction et les lots de conception sont indexés dans
[docs/design/README.md](docs/design/README.md).

## Ce que fait ce projet

Des commandes identifiées, expirables et confirmées par relecture réelle de la
chaudière, avec protection contre les doublons pendant la durée de vie du
processus — jamais de succès supposé.

## Ce que ce projet ne fait pas

- il n'installe ni ne configure `vcontrold` ;
- il ne prend en charge ni le câble, ni l'adaptateur, ni la liaison Optolink ;
- il ne porte aucune sémantique métier : pas de confort/éco, pas de programme,
  pas d'arbitrage ;
- il ne redémarre ni service ni machine ;
- il ne prétend pas être compatible avec l'ensemble des chaudières Viessmann.

## Prérequis

- un `vcontrold` fonctionnel et joignable en TCP, avec sa propre définition de
  datapoints ;
- une liaison Optolink opérationnelle ;
- un broker MQTT accessible en réseau local ;
- Python ≥ 3.11.

## Installation et lancement

> Rien n'a été éprouvé contre un broker, un `vcontrold` ou une chaudière réels.
> Ce qui suit décrit l'interface, pas une mise en production validée.

```sh
pip install .
```

Copiez `docs/boilerack.example.toml`, puis adaptez les deux valeurs
obligatoires — l'hôte du broker et le chemin de `vclient` :

```toml
[mqtt]
host = "broker.exemple.invalid"

[vclient]
executable = "vclient"
```

Le mot de passe MQTT, s'il y en a un, ne se met **jamais** dans ce fichier : il
est fourni exclusivement par la variable d'environnement
`BOILERACK_MQTT_PASSWORD`. Le fichier de configuration reste ainsi versionnable.

```sh
export BOILERACK_MQTT_PASSWORD='...'   # facultatif
boilerack --config /chemin/boilerack.toml
```

`python -m boilerack --config /chemin/boilerack.toml` est strictement
équivalent, et reste utilisable quand la commande installée n'est pas dans le
`PATH`.

`--log-level` accepte `DEBUG`, `INFO` (défaut), `WARNING`, `ERROR` ou
`CRITICAL`, pour la session en cours seulement.

Codes de sortie :

| Code | Signification |
|---|---|
| `0` | arrêt normal, ou arrêt demandé par `SIGTERM` |
| `130` | arrêt demandé par `SIGINT` (Ctrl-C) |
| `2` | erreur d'usage de la commande, ou configuration invalide |
| `1` | panne, avec sa trace d'appels |

Le détail de chaque clé, des validations et des garanties figure dans
[docs/design/c10-user-interface.md](docs/design/c10-user-interface.md).

## Compatibilité

Vérifié sur **une seule installation** : régulation `VScotHO1` (`20CB`),
protocole `P300`, circuit `M1` et eau chaude sanitaire, sur une Vitodens 200-W
B2HB. Aucune compatibilité n'est revendiquée au-delà.

**« Vérifié » qualifie ici la caractérisation de cette installation — ce que les
contrats ont établi en l'observant — et non un essai de Boilerack, qui n'a pas eu
lieu : voir la réserve de la section « Installation et lancement ».

## Licence

MIT — voir `LICENSE`.

## Non-affiliation

Projet indépendant. Viessmann, Vitodens et Optolink sont des marques de leurs
titulaires respectifs. Ce projet n'est ni affilié à Viessmann, ni approuvé, ni
soutenu par cette société. Ces marques ne sont citées qu'à des fins
d'identification technique.

Ce projet invoque `vcontrold` sans le redistribuer, sans en dériver et sans lui
être affilié.
