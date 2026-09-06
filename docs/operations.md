# Documentation opérateur

Guide court, pour qui exploite Boilerack sans avoir à lire le corpus de
conception. Il décrit le déploiement de référence : Boilerack en service
`systemd`, coexistant avec l'ancien `boiler-bridge` par exclusion mutuelle.

Pour le détail contractuel et les preuves, chaque section renvoie vers le
document de conception qui l'établit. Rien ici n'introduit de comportement que
ces contrats ne couvrent pas déjà.

---

## Prérequis

- un `vcontrold` fonctionnel, joignable en TCP, avec sa propre définition de
  datapoints ;
- une liaison Optolink opérationnelle vers la chaudière ;
- un broker MQTT accessible en réseau local ;
- Python ≥ 3.11 sur la machine cible ;
- privilèges d'administration (`root`) pour l'installation en service.

## Installation

Deux voies existent, pour deux usages différents.

**Interface en ligne de commande seule**, portable, sans privilèges :

```sh
pip install .
```

Voir [`README.md`](../README.md#installation-et-lancement) pour la
configuration minimale et le lancement direct.

**Installation en service**, avec utilisateur dédié, `venv` isolé et unité
`systemd` — celle du déploiement de référence :

```sh
python install.py install --checkout /chemin/du/checkout --root / --allow-system-acts
```

Ce script, `install.py` à la racine du dépôt, ne démarre jamais le service et
n'exécute jamais `systemctl` lui-même : il crée l'utilisateur `boilerack`
(non privilégié), le `venv` sous `/opt/boilerack`, dépose la configuration
d'exemple et l'unité sous `/etc/boilerack` et `/etc/systemd/system` **si
elles sont absentes**, puis affiche les commandes `systemctl` restantes à
exécuter soi-même. Contrat complet :
[`design/c13-installation-contract.md`](design/c13-installation-contract.md).

Une réinstallation (même commande, rejouée) **préserve** la configuration et
le secret déjà en place — ils ne sont déposés que s'ils sont absents — et
**redépose** l'unité à l'identique du gabarit versionné. Elle ne touche
jamais un éventuel drop-in `systemd` posé à la main : voir
[Migration depuis `boiler-bridge`](#migration-depuis-boiler-bridge).

## Configuration

Deux fichiers, sous `/etc/boilerack/` :

| Fichier | Contenu | Mode |
|---|---|---|
| `boilerack.toml` | toute la configuration durable — hôte MQTT, `vclient`, préfixe des topics, cadences | `0640 root:boilerack`, versionnable |
| `boilerack.env` | le seul secret, `BOILERACK_MQTT_PASSWORD=...` | `0640 root:boilerack`, **jamais** versionné |

Le mot de passe MQTT ne se met **jamais** dans le fichier TOML. Le fichier
`boilerack.env` est **attendu** par l'unité : son absence empêche le
démarrage, même sans authentification MQTT — dans ce cas, il existe mais reste
vide.

Référence complète des clés : [`design/c10-user-interface.md`](design/c10-user-interface.md)
et [`boilerack.example.toml`](boilerack.example.toml).

## Démarrage

Actes humains restants après `install.py` (jamais exécutés à votre place) :

```sh
systemctl daemon-reload
systemctl enable boilerack.service
systemctl start boilerack.service
```

## Vérification

```sh
systemctl status boilerack.service
```

Attendu : `active (running)`, sans redémarrage récent inexpliqué
(`NRestarts`).

```sh
journalctl -u boilerack.service -f
```

Le journal (stderr, capturé nativement par `systemd`) montre les cycles de
lecture au niveau `INFO` par défaut.

```sh
mosquitto_sub -h <broker> -t 'boiler/#' -v
```

Attendu : `boiler/bridge/online` retenu à `true`, et les dix mesures de
`boiler/telemetry/...` (voir [Topics MQTT](#topics-mqtt)) se rafraîchissant
au rythme de `snapshot_period_s` (30 s par défaut).

## Diagnostic

| Symptôme | Piste |
|---|---|
| `systemctl status` montre `code=exited, status=2` | configuration invalide ou absente — le message est dans `journalctl`, sans trace ; le service reste arrêté et **ne redémarre pas** (c'est voulu) |
| `status=1`, avec trace | panne — broker injoignable au démarrage en est la cause la plus fréquente ; le service **redémarre** (`Restart=on-failure`, `RestartSec=10s`) |
| `status=130` | interruption `SIGINT` délibérée — ne redémarre pas non plus, et reste visible en échec |
| `boiler/bridge/online` absent ou retenu à `false` | le pont ne publie plus : vérifier d'abord la connectivité au broker, puis `vclient`/`vcontrold` |
| aucune commande n'est acquittée | normal si la voie de commande est fermée — voir [Topics MQTT](#topics-mqtt) |

Détail des codes de sortie et de la politique de redémarrage :
[`design/c12-service-contract.md` §7-8](design/c12-service-contract.md).

## Mise à jour

Rejouer l'installation avec un checkout à jour :

```sh
python install.py install --checkout /chemin/du/checkout/à-jour --root / --allow-system-acts
systemctl restart boilerack.service
```

Le `venv` est reconstruit à neuf ; la configuration, le secret et le drop-in
d'exclusion terrain (s'il existe) sont préservés. Le redémarrage n'est pas
automatique : il est délibérément laissé à l'exploitant.

## Rollback

Vers l'ancien `boiler-bridge`, **sans redémarrage machine** :

```sh
systemctl stop boilerack.service       # jusqu'à 90 s, puis SIGKILL si le processus ne répond pas
systemctl start boiler_bridge.service  # l'exclusion mutuelle l'autorise dès que boilerack.service est arrêté
```

Puis vérifier que le pont historique publie de nouveau, et que Boilerack ne
tourne plus (`systemctl status boilerack.service` → `inactive`).

Sur le déploiement de référence, ce geste a été mesuré à `LOT 2B` :
arrêt (borné à 90 s), démarrage du pont, confirmation de la reprise —
`≈ 130 s` au pire cas, décrit en détail dans
[`design/lot2b-regime-permanent.md` §6](design/lot2b-regime-permanent.md).

## Migration depuis `boiler-bridge`

Boilerack et `boiler-bridge` déclarent une exclusion mutuelle `Conflicts=` :
démarrer l'un arrête l'autre, dans les deux sens, et `systemd` l'applique
lui-même — il n'existe pas de fenêtre où les deux tournent en même temps.

**Ce que le dépôt versionne, et ce qu'il ne versionne pas.** Le gabarit
[`systemd/boilerack.service`](../systemd/boilerack.service) ne porte **aucune**
directive `Conflicts=`. Sur le déploiement de référence, l'exclusion est
posée par un drop-in `systemd` distinct, extérieur à ce dépôt :

```text
/etc/systemd/system/boilerack.service.d/10-exclusion.conf
```

C'est un acte de migration posé à la main sur la machine, pas quelque chose
qu'`install.py` crée, lit ou supprime — une réinstallation normale le laisse
intact. Le détail normatif de ce constat est dans
[`design/c12-service-contract.md` §9.2](design/c12-service-contract.md).

**Procédure de bascule**, dans l'ordre (déjà exécutée sur le déploiement de
référence le 2026-09-04) :

1. poser le drop-in d'exclusion mutuelle ;
2. activer `boilerack.service` au démarrage (`enable`) ;
3. désactiver `boiler_bridge.service` (`disable`) ;
4. démarrer `boilerack.service` — l'exclusion arrête `boiler_bridge.service`
   s'il tournait encore ;
5. ouvrir l'autorité d'écriture dans `boilerack.toml`
   (`[transaction_surface] enabled = true`) — **fermée par défaut**, cette clé
   fait de Boilerack l'écrivain souverain.

**Vérifier que la migration a pris** :

```sh
systemctl is-enabled boilerack.service boiler_bridge.service
systemctl is-active  boilerack.service boiler_bridge.service
```

Attendu après bascule : `boilerack.service` → `enabled`/`active`,
`boiler_bridge.service` → `disabled`/`inactive`. Un redémarrage machine
confirme que ce régime revient seul au boot (constaté sur le déploiement de
référence par `LOT 2B-R`,
[`design/lot2b-r-constat.md`](design/lot2b-r-constat.md)).

## Frontière avec Home Assistant

**Boilerack n'intègre pas Home Assistant.** Il n'implémente ni MQTT
Discovery, ni aucun composant HACS, et ce dépôt n'en dépend pas. Ce qu'il
expose est une surface MQTT ordinaire — voir [Topics MQTT](#topics-mqtt) —
que n'importe quel consommateur MQTT peut lire, Home Assistant compris s'il
est configuré côté broker pour le faire (capteurs MQTT génériques,
`configuration.yaml`, ou tout autre outil). Cette configuration, si elle
existe, vit entièrement hors de ce dépôt.

## Topics MQTT

Tous les topics sont préfixés par `[read_surface].prefix`, `boiler` par
défaut. Source de vérité dans le code :
[`src/boilerack/read_surface/topics.py`](../src/boilerack/read_surface/topics.py)
et [`design/c7-mqtt-read-contract.md`](design/c7-mqtt-read-contract.md).

### Télémétrie (`boiler/telemetry/...`)

Dix mesures, publiées en retenu (`retain`), republiées à `snapshot_period_s`
(30 s par défaut) ou dès qu'une valeur change de plus que sa tolérance :

| Topic |
|---|
| `telemetry/temperatures/outdoor` |
| `telemetry/temperatures/supply` |
| `telemetry/temperatures/dhw` |
| `telemetry/dhw/setpoint` |
| `telemetry/heating/setpoint` |
| `telemetry/heating/reduced_reference` |
| `telemetry/heating/curve/slope` |
| `telemetry/heating/curve/shift` |
| `telemetry/burner/modulation` |
| `telemetry/burner/state` |

### État de service (`boiler/bridge/...`)

| Topic | Rôle |
|---|---|
| `bridge/online` | présence du pont, message testament MQTT (`retain`) |
| `bridge/telemetry_status` | fraîcheur de l'instantané de télémétrie |
| `bridge/heartbeat` | battement périodique, conservé pour compatibilité avec le consommateur historique |

### Disponibilité / diagnostic

`bridge/online` **est** le topic de disponibilité : retenu à `true` tant que
le pont est connecté, testament MQTT le faisant passer à `false` si le
processus disparaît sans prévenir. Il n'existe pas d'autre topic
d'auto-diagnostic dans la surface v1 ; le diagnostic opérationnel se fait par
`journalctl` et `systemctl status`, voir [Diagnostic](#diagnostic).

### Surface de commande, si activée

Une voie de commande existe dans le code — souscription sur
`boilerack/command` (topic fixe, non reconfigurable), acquittements sous
`boilerack/ack/...` — mais **elle est fermée par défaut** :
`[transaction_surface].enabled = false`. Aucune commande n'est acceptée tant
que cette clé n'est pas explicitement mise à `true` dans `boilerack.toml`.

Le déploiement de référence l'a ouverte, en cohérence avec son rôle
d'écrivain souverain — voir
[Migration depuis `boiler-bridge`](#migration-depuis-boiler-bridge). Une
installation qui ne doit **que** lire n'a rien à faire : le défaut suffit.
