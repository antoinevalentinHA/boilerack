# boilerack

Pont MQTT transactionnel au-dessus d'un `vcontrold` existant, pour chaudières
Viessmann équipées d'une liaison Optolink.

> **État : déployé en production.** Boilerack est l'**écrivain souverain actif**
> vers la chaudière de référence depuis le 2026-09-04 (`LOT 2B`), régime
> confirmé au redémarrage machine par `LOT 2B-R` le 2026-09-05. Il a été éprouvé
> contre un broker MQTT, un `vcontrold` et une chaudière réels — pas seulement
> caractérisé sur pièces. L'ancien pont `boiler-bridge` reste installé comme
> **prédécesseur historique**, désactivé (`disabled`, `inactive`) dans le
> déploiement de référence, et sert de voie de rollback. Aucune prerelease
> n'a été diffusée, et aucun tag Git n'existe encore — voir
> [Maturité et version](#maturité-et-version).

Les contrats de construction et les lots de conception sont indexés dans
[docs/design/README.md](docs/design/README.md). La documentation d'exploitation
— installation, vérification, diagnostic, mise à jour, rollback, migration
depuis `boiler-bridge` — vit dans [docs/operations.md](docs/operations.md).

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

## Architecture

```
vcontrold (démon, Optolink) <--TCP/vclient--> Boilerack <--MQTT--> broker <--MQTT--> consommateurs
```

Boilerack lance `vclient` en sous-processus pour lire ou écrire une valeur via
`vcontrold`, et publie ce qu'il observe sur un broker MQTT. Il ne remplace ni
n'installe `vcontrold`, ne parle jamais directement à l'Optolink, et ne porte
aucune logique de confort ou de programme — ces arbitrages restent en dehors du
dépôt, côté consommateur MQTT. **Home Assistant n'est pas un composant de ce
dépôt** : Boilerack expose des topics MQTT ordinaires, sans intégration HA/HACS
ni MQTT Discovery ; brancher Home Assistant, s'il y en a un, est un choix de
l'exploitant fait entièrement côté broker.

Le déploiement de référence fait tourner Boilerack sous `systemd`, comme
écrivain unique face à l'ancien `boiler-bridge` — voir
[Migration depuis `boiler-bridge`](#migration-depuis-boiler-bridge) et
[docs/design/c12-service-contract.md](docs/design/c12-service-contract.md).

## Prérequis

- un `vcontrold` fonctionnel et joignable en TCP, avec sa propre définition de
  datapoints ;
- une liaison Optolink opérationnelle ;
- un broker MQTT accessible en réseau local ;
- Python ≥ 3.11.

## Installation et lancement

Ce qui suit décrit l'interface en ligne de commande, portable vers n'importe
quelle installation. Pour l'installation en service `systemd`, telle
qu'exercée sur le déploiement de référence — utilisateur dédié, unité,
secret séparé — voir [docs/operations.md](docs/operations.md) et
[docs/design/c12-service-contract.md](docs/design/c12-service-contract.md).

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

C'est cette même installation que le déploiement de référence exploite en
production depuis le 2026-09-04 : la caractérisation par les contrats et
l'usage réel portent donc sur la même chaudière, la même liaison Optolink et le
même `vcontrold`.

## Migration depuis `boiler-bridge`

Boilerack et `boiler-bridge` ne peuvent jamais tourner en même temps sur une
même installation : les deux unités `systemd` se déclarent mutuellement
`Conflicts=`, et démarrer l'une arrête l'autre. Sur le déploiement de
référence, cette exclusion est portée par un drop-in `systemd` posé sur la
machine (`/etc/systemd/system/boilerack.service.d/10-exclusion.conf`), pas par
le gabarit versionné de ce dépôt — voir
[docs/design/c12-service-contract.md §9.2](docs/design/c12-service-contract.md)
et [docs/operations.md](docs/operations.md#migration-depuis-boiler-bridge)
pour la procédure et son détail.

En régime nominal après bascule : `boilerack.service` est `enabled`/`active`,
`boiler_bridge.service` est `disabled`/`inactive` et reste installé comme
filet de secours.

## Vérification du bon fonctionnement

```sh
systemctl status boilerack.service        # active (running)
journalctl -u boilerack.service -f        # journal en direct, sur stderr
mosquitto_sub -t 'boiler/#' -v            # télémétrie et état publiés
```

Une installation saine publie `boiler/bridge/online` retenu à `true`, et les
dix mesures de `boiler/telemetry/...` se rafraîchissent au rythme configuré.
Détail dans [docs/operations.md](docs/operations.md#vérification).

## Diagnostic minimal

- `systemctl status boilerack.service` — état du service, code de sortie de la
  dernière exécution (voir la table des codes ci-dessus) ;
- `journalctl -u boilerack.service -n 200` — dernières lignes, avec trace en
  cas de panne (code `1`) ;
- `boiler/bridge/online` retenu à `false`, ou absent — le pont ne publie plus :
  vérifier le broker et `vcontrold` en premier.

Diagnostic détaillé, y compris les causes usuelles par code de sortie, dans
[docs/operations.md](docs/operations.md#diagnostic).

## Rollback

Le rollback vers `boiler-bridge` ne redémarre jamais la machine :

```sh
systemctl stop boilerack.service      # jusqu'à 90 s, puis SIGKILL si besoin
systemctl start boiler_bridge.service # l'exclusion mutuelle l'autorise dès lors
```

Procédure complète, temps mesurés et vérifications à faire dans
[docs/operations.md](docs/operations.md#rollback).

## Topics MQTT utiles

Préfixe par défaut `boiler/`, configurable (`[read_surface].prefix`).

| Topic | Contenu |
|---|---|
| `boiler/telemetry/...` | dix mesures de télémétrie (températures, consignes, courbe de chauffe, brûleur) |
| `boiler/bridge/online` | présence du pont, retenu |
| `boiler/bridge/telemetry_status` | état de fraîcheur de l'instantané |
| `boiler/bridge/heartbeat` | battement de compatibilité historique |

La **voie de commande** (`boilerack/command`, acquittements sur
`boilerack/ack/...`) existe dans le code mais est **fermée par défaut**
(`transaction_surface.enabled = false`) ; le déploiement de référence l'a
ouverte explicitement, en tant qu'écrivain souverain — voir
[docs/operations.md](docs/operations.md#topics-mqtt) pour le détail complet et
la source de vérité dans le code.

## Maturité et version

`__version__` vaut encore `0.0.0` et aucun tag Git n'a été publié : la
convention de version et le premier tag relèvent d'une décision de
gouvernance séparée, non de ce lot documentaire. Voir
[docs/design/readiness-boilerack.md](docs/design/readiness-boilerack.md) pour
l'état du dépôt.

## Licence

MIT — voir `LICENSE`.

## Non-affiliation

Projet indépendant. Viessmann, Vitodens et Optolink sont des marques de leurs
titulaires respectifs. Ce projet n'est ni affilié à Viessmann, ni approuvé, ni
soutenu par cette société. Ces marques ne sont citées qu'à des fins
d'identification technique.

Ce projet invoque `vcontrold` sans le redistribuer, sans en dériver et sans lui
être affilié.
