# boilerack

Pont MQTT transactionnel au-dessus d'un `vcontrold` existant, pour chaudières
Viessmann équipées d'une liaison Optolink.

> **État : en construction. Rien n'est publiable ni utilisable à ce stade.**
> Aucune prerelease n'a été diffusée.

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

## Compatibilité

Vérifié sur **une seule installation** : régulation `VScotHO1` (`20CB`),
protocole `P300`, circuit `M1` et eau chaude sanitaire, sur une Vitodens 200-W
B2HB. Aucune compatibilité n'est revendiquée au-delà.

## Licence

MIT — voir `LICENSE`.

## Non-affiliation

Projet indépendant. Viessmann, Vitodens et Optolink sont des marques de leurs
titulaires respectifs. Ce projet n'est ni affilié à Viessmann, ni approuvé, ni
soutenu par cette société. Ces marques ne sont citées qu'à des fins
d'identification technique.

Ce projet invoque `vcontrold` sans le redistribuer, sans en dériver et sans lui
être affilié.
