"""Serialisation du payload scalaire de telemetrie.

Implemente §4.5 du contrat `c7-mqtt-read-contract.md` : « une chaine numerique
decimale sans unite, utilisant le point comme separateur et analysable comme un
nombre fini », encodee UTF-8.

Une SEULE fonction sert les huit mesures. Aucune notion de forme entiere ou
decimale n'est portee ici, et c'est une decision, pas un oubli : §4.5 declare
les deux formes conformes (« `28` et `28.0` sont conformes ») et §11 declare le
payload `decimal` pour les huit, y compris celles que §4.2 range dans le type
`entier`. Un champ de forme qui pilotrait la serialisation contredirait §11.

Cette primitive ne connait pas la mesure qu'elle serialise. Elle n'arrondit
pas, ne tronque pas, et ne verifie pas qu'une mesure historiquement entiere
recoit une valeur entiere : ce controle releverait d'une couche de conformite
qui n'existe pas et n'a pas de consommateur aujourd'hui.

Module PUR : aucune horloge, aucun reseau, aucun processus, aucun etat, aucune
dependance a la locale.
"""

from __future__ import annotations

__all__ = ["format_scalar"]

# REEXPORTATION — l'implementation vit dans `boilerack.decimal_form`, module
# neutre, parce que la couche adaptateur en a besoin et n'a pas le droit de
# remonter jusqu'ici. Le nom reste importable depuis ce module : §4.5 en demeure
# l'autorite CONTRACTUELLE, `decimal_form` n'en est que le siege technique.
from boilerack.decimal_form import format_scalar

__all__ = ["format_scalar"]
