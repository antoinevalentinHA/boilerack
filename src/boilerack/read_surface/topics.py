"""Construction des topics de la surface MQTT de lecture.

Implemente §3.2 (construction), §3.3 (normalisation du prefixe) et §11
(surface exacte de la v1) du contrat `c7-mqtt-read-contract.md`.

Deux notions sont **distinctes** et ne doivent jamais etre confondues :

- un suffixe **syntaxiquement valide** : toute chaine que `build_topic` accepte
  d'assembler derriere un prefixe ;
- un suffixe **de la surface v1** : l'un des ONZE de `V1_SUFFIXES`, seule
  enumeration faisant autorite. §11 est formel : « Tout autre topic **MUST NOT**
  etre publie par la surface de lecture. »

`build_topic` n'est volontairement PAS restreint aux onze : le respect de la
surface est une propriete du futur publieur et de ses tests de conformite, pas
une propriete d'un assembleur de chaines. Ce module n'expose aucun mecanisme
d'enregistrement, d'extension ou de greffon : la surface v1 est close.

Module PUR : aucune horloge, aucun reseau, aucun processus, aucun etat.
"""

from __future__ import annotations

import re
from typing import Final

__all__ = [
    "InvalidMqttTopic",
    "normalize_prefix",
    "build_topic",
    "TELEMETRY_SUFFIXES",
    "BRIDGE_SUFFIXES",
    "V1_SUFFIXES",
]


#: Jokers MQTT. §3.3 les refuse dans un prefixe ; un topic de PUBLICATION ne
#: peut de toute facon pas en porter, ce qui vaut donc aussi pour un suffixe.
_WILDCARDS: Final = ("+", "#")

#: Caracteres de controle Unicode, categorie `Cc` : U+0000 (dont `NUL`) a
#: U+001F et U+007F a U+009F. C'est la definition de « caractere de controle »
#: visee par §3.3, pas une interdiction supplementaire.
_CONTROL_CHARS: Final = re.compile(r"[\x00-\x1f\x7f-\x9f]")


class InvalidMqttTopic(ValueError):
    """Prefixe ou suffixe refuse.

    Exception UNIQUE du module. Aucune sous-classe n'est definie : distinguer
    « prefixe invalide » de « suffixe invalide » n'aurait aujourd'hui aucun
    consommateur, le message portant deja l'information.

    Les messages sont deterministes pour faciliter les tests, mais ne sont pas
    une API publique contractuelle : ils peuvent changer sans preavis.
    """


# -- Surface v1 -------------------------------------------------------------

#: Les HUIT mesures retenues en v1, dans l'ordre de la table normative §4.2.
TELEMETRY_SUFFIXES: Final[tuple[str, ...]] = (
    "telemetry/temperatures/outdoor",
    "telemetry/temperatures/supply",
    "telemetry/temperatures/dhw",
    "telemetry/dhw/setpoint",
    "telemetry/heating/setpoint",
    "telemetry/heating/reduced_reference",
    "telemetry/heating/curve/slope",
    "telemetry/heating/curve/shift",
)

#: Les TROIS topics de service, dans l'ordre du recapitulatif §11.
#:
#: `bridge/heartbeat` appartient bien a la surface v1, mais §9 le conserve en
#: **SHOULD** — au seul titre de la compatibilite historique — quand les dix
#: autres sont requis. Cette nuance est documentaire : elle n'a pas de
#: consommateur dans ce lot et n'est donc pas encodee dans une structure.
BRIDGE_SUFFIXES: Final[tuple[str, ...]] = (
    "bridge/online",
    "bridge/telemetry_status",
    "bridge/heartbeat",
)

#: Les ONZE suffixes de la surface v1 (§11), dans un ordre stable. Aucune autre
#: valeur n'est publiable par la surface de lecture. Ne figurent donc pas ici,
#: et c'est voulu : les topics de brulleur (reportes, §4.3), `bridge/version`
#: (reporte, §13), la commande et les acquittements (surface transactionnelle,
#: §14), `error/last` et `guard/*` (hors perimetre, §13), et un eventuel topic
#: de capacites (hors v1, §10).
V1_SUFFIXES: Final[tuple[str, ...]] = TELEMETRY_SUFFIXES + BRIDGE_SUFFIXES


# -- Prefixe ----------------------------------------------------------------


def normalize_prefix(value: str) -> str:
    """Normalise un prefixe selon le tableau §3.3, ou refuse l'entree.

    Normalisations appliquees, et AUCUNE autre — §3.3 : « Aucune correction
    silencieuse autre que les normalisations du tableau. »

    - barre oblique initiale retiree ;
    - barre oblique terminale retiree ;
    - barres consecutives reduites a une seule ;
    - un prefixe a plusieurs niveaux est accepte tel quel.

    Refus : chaine vide, joker `+` ou `#`, caractere de controle ou `NUL`,
    prefixe commencant par `$`.

    Ce que ce contrat ne dit PAS, et qui n'est donc PAS interdit ici : les
    espaces, y compris de bordure, et tout caractere Unicode imprimable. Les
    accepter est le comportement conservateur ; inventer une interdiction
    produit ne l'est pas.
    """
    if not isinstance(value, str):
        # Erreur de programmation. `InvalidMqttTopic` derive de `ValueError`,
        # par coherence avec `InvalidCommandName` (C6), qui traite de meme une
        # entree non textuelle.
        raise InvalidMqttTopic(
            f"le prefixe doit etre une chaine, recu {type(value).__name__}"
        )

    _reject_forbidden(value, "prefixe")

    # Un unique passage retire les barres de bordure ET reduit les barres
    # consecutives : les segments vides sont simplement ecartes.
    normalized = "/".join(segment for segment in value.split("/") if segment != "")

    if normalized == "":
        # Couvre la chaine vide du tableau, et le cas ou l'entree ne contient
        # que des barres : le prefixe EFFECTIF serait vide, donc aucun espace
        # de noms, donc le risque de collision que §3.3 refuse explicitement.
        raise InvalidMqttTopic(
            "le prefixe ne peut pas etre vide : un espace de noms est obligatoire"
        )

    if normalized.startswith("$"):
        # Controle porte sur le prefixe NORMALISE : `/$SYS` doit etre refuse au
        # meme titre que `$SYS`, puisque le topic produit commencerait par `$`.
        raise InvalidMqttTopic(
            "un prefixe commencant par '$' vise un espace reserve du broker"
        )

    return normalized


# -- Suffixe et assemblage --------------------------------------------------


def build_topic(prefix: str, suffix: str) -> str:
    """Assemble un topic : `<prefixe_normalise>/<suffixe>` (§3.2).

    Le suffixe est transmis **tel quel**, jamais normalise : §3.2 exige que les
    suffixes contractuels soient invariants et **MUST NOT** dependre de la
    valeur du prefixe. Un suffixe mal forme est donc refuse, jamais corrige.
    """
    return f"{normalize_prefix(prefix)}/{_validate_suffix(suffix)}"


def _validate_suffix(suffix: str) -> str:
    """Valide la syntaxe d'un suffixe et le rend inchange.

    Refus : entree non textuelle, chaine vide, barre de bordure, barres
    consecutives, joker, caractere de controle.

    `$` n'est PAS refuse ici. §3.3 ne l'interdit qu'en tete de PREFIXE, et un
    suffixe n'est jamais en tete d'un topic — le prefixe le precede toujours.
    L'espace reserve du broker ne peut donc pas etre atteint par un suffixe.
    Aucun des onze suffixes de la v1 n'en contient.
    """
    if not isinstance(suffix, str):
        raise InvalidMqttTopic(
            f"le suffixe doit etre une chaine, recu {type(suffix).__name__}"
        )
    if suffix == "":
        raise InvalidMqttTopic("le suffixe ne peut pas etre vide")

    _reject_forbidden(suffix, "suffixe")

    if suffix.startswith("/") or suffix.endswith("/"):
        raise InvalidMqttTopic(
            f"le suffixe ne doit porter aucune barre de bordure : {suffix!r}"
        )
    if "//" in suffix:
        raise InvalidMqttTopic(
            f"le suffixe ne doit pas contenir de barres consecutives : {suffix!r}"
        )
    return suffix


def _reject_forbidden(value: str, kind: str) -> None:
    """Refuse les jokers MQTT et les caracteres de controle."""
    for wildcard in _WILDCARDS:
        if wildcard in value:
            raise InvalidMqttTopic(
                f"le {kind} ne doit pas contenir le joker MQTT {wildcard!r}"
            )
    if _CONTROL_CHARS.search(value):
        raise InvalidMqttTopic(f"le {kind} contient un caractere de controle")
