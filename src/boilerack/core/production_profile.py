"""Profil de PRODUCTION : les roles reellement inscriptibles (lot W4-D).

Pendant de `boilerack.testing.fake_profile`, mais pour la vraie chaudiere. Ce
module ne contient que des DONNEES : le schema et ses invariants restent dans
`boilerack.core.profile`, et rien n'est valide ici qui le soit deja la-bas.

LES QUATRE ROLES — PARITE DE REMPLACEMENT
    Le pont historique ecrit QUATRE roles en production, tous reellement
    utilises par ses consommateurs aval. Le profil les declare tous les quatre :
    sans eux, Boilerack ne peut pas remplacer le pont, il ne peut que
    l'accompagner.

    La borne « un seul role inscriptible » est LEVEE par arbitrage humain, au
    titre de la parite de remplacement. Elle avait un motif, et ce motif
    subsiste en partie : voir la reserve ci-dessous.

RESERVE — CARACTERISATION, ET CE QUI N'EST PAS PROUVE
    Une seule des quatre ecritures a ete CARACTERISEE au sens de W4-C : celle de
    `setNiveauM1`, par la campagne terrain du 22 aout 2026, puis confirmee par
    G.2 et W4-S. W4-C §15 le dit sans detour : « elle ne prouve rien au-delà de
    `setNiveauM1` ».

    Les trois autres sont ecrites quotidiennement par le pont historique — leur
    comportement est donc EXERCE —, mais leur reponse de transport n'a jamais
    ete observee sous protocole. La premiere ecriture reelle emise par Boilerack
    sur chacune d'elles sera une PREMIERE, au sens de W4-F, et releve du meme
    regime d'autorisation que les precedentes.

    Declarer un role ne l'ecrit pas : la surface transactionnelle demeure fermee
    tant que `[transaction_surface].enabled` n'est pas persiste a `true`.

POURQUOI AUCUN ROLE EN LECTURE SEULE
    `CommandSpec` accepte `write=None`, et le profil factice s'en sert pour
    couvrir un cas de rejet. En production, la surface de lecture ne consomme
    PAS `Profile` : elle a sa propre declaration, `read_surface/measurements.py`,
    dont le module explique pourquoi. Un role en lecture seule n'aurait donc ici
    aucun consommateur.

VOCABULAIRE DES ROLES — REPRIS, NON INVENTE
    `heating_curve_shift` n'est pas un nom cree pour l'occasion. L'autorite
    normative est `c7-mqtt-read-contract.md` §4.2, dont la table associe deja ce
    role a `getNiveauM1` — et le qualifie d'`entier`, ce que ce profil retrouve
    par une autre source, A5 §5.3.

    `read_surface/measurements.py` en est une TRANSCRIPTION, pas l'autorite : ce
    module et celui-ci transcrivent le meme contrat pour deux usages differents.
    Un test croise les deux transcriptions, non pour fonder le nom, mais pour
    detecter qu'elles divergeraient. Un second vocabulaire pour une seule
    grandeur serait une dette immediate.

CE QUE CE MODULE NE DECIDE PAS
    Ni la signature d'une invocation reussie, ni la classification d'une issue de
    transport : W4-A §9 en est l'autorite, et l'adaptateur d'ecriture — non
    encore livre — en sera le siege. Un profil declare des grandeurs ; il ne lit
    pas une sortie de processus.

    Ni le verdict metier. `confirm_tolerance` alimente la relecture du coeur
    (C3) ; elle ne dit pas qu'une valeur a ete appliquee.

FRONTIERE
    Construire ce profil n'active rien. `build_transaction_surface` exige AUSSI
    un `VClient` ecrivain, qui n'existe pas : la voie transactionnelle reste
    fermee par cette seconde dependance. La composition relève de W4-E, la
    bascule terrain de W4-F.
"""

from __future__ import annotations

from typing import Final

from boilerack.core.profile import CommandSpec, Profile, ValueType

__all__ = ["PRODUCTION_PROFILE_NAME", "build_production_profile"]

#: Nom du profil, sur le modele de `fake-c3` : usage et version, rien de plus.
PRODUCTION_PROFILE_NAME: Final = "production-v1"

#: Provenance des bornes, du pas et de la tolerance. `CommandSpec` l'exige non
#: vide precisement pour qu'aucune borne n'entre sans source citable.
#:
#: Les quatre sources citent le meme couple : la documentation arsenal du pont
#: `boiler_pi`, et le code du pont historique lui-meme — seul temoin executable
#: des bornes qu'il applique en production.
_SHIFT_BOUNDS_SOURCE: Final = (
    "arsenal — 00_documentation_arsenal/outils_externes/boiler_pi/mqtt.md §5.3 "
    "(type int, bornes [-13 ; 40], pas 1, tolerance de confirmation nulle) ; "
    "role et commande de lecture : c7-mqtt-read-contract.md §4.2 ; "
    "ecriture caracterisee par w4c-write-capture-protocol.md §16"
)

_DHW_BOUNDS_SOURCE: Final = (
    "pont historique boiler_mqtt.py v0.5, DHW_SETPOINT_MIN/MAX = [10 ; 60], "
    "normalisation entiere ; role et commande de lecture : "
    "c7-mqtt-read-contract.md §4.2 ; ecriture NON caracterisee au sens de W4-C"
)

_HEATING_BOUNDS_SOURCE: Final = (
    "pont historique boiler_mqtt.py v0.5, HEATING_TEMPERATURE_MIN/MAX = "
    "[5 ; 30], normalisation entiere ; role et commande de lecture : "
    "c7-mqtt-read-contract.md §4.2 ; ecriture NON caracterisee au sens de W4-C"
)

_SLOPE_BOUNDS_SOURCE: Final = (
    "pont historique boiler_mqtt.py v0.5, CURVE_SLOPE_MIN/MAX = [0.2 ; 3.5], "
    "CURVE_SLOPE_STEP = 0.1, tolerance de representation 1e-9 ; role et "
    "commande de lecture : c7-mqtt-read-contract.md §4.2 ; ecriture NON "
    "caracterisee au sens de W4-C"
)


def build_production_profile() -> Profile:
    """Construit le profil de production.

    QUATRE roles, exactement ceux que le pont historique ecrit en production :

    - `dhw_setpoint`         — consigne ECS, `getTempWWsoll` / `setTempWWsoll`,
      entier, [10 ; 60], pas 1 ;
    - `heating_setpoint`     — consigne de chauffage du circuit M1,
      `getTempRaumNorSollM1` / `setTempRaumNorSollM1`, entier, [5 ; 30], pas 1 ;
    - `heating_curve_shift`  — decalage parallele de la courbe, `getNiveauM1` /
      `setNiveauM1`, entier, [-13 ; 40], pas 1 ;
    - `heating_curve_slope`  — pente de la courbe, `getNeigungM1` /
      `setNeigungM1`, FLOTTANT, [0.2 ; 3.5], pas 0.1.

    TOLERANCE DE CONFIRMATION
        Nulle pour les trois roles entiers : la relecture confirme par egalite
        exacte, ce que `_confirms` applique deja pour tout role entier.

        Pour la pente, seule grandeur flottante, la tolerance vaut `1e-9` — une
        tolerance de REPRESENTATION, non de valeur. Le pont historique retient
        le meme ordre de grandeur pour la meme raison : `0.1` n'est pas
        representable exactement en binaire, et exiger l'egalite stricte
        rejetterait des relectures pourtant justes. Elle ne tolere aucun ecart
        metier : deux crans de pente sont distants de `0.1`, soit cent millions
        de fois cette tolerance.

    DIFFERENCE ASSUMEE AVEC LE PONT HISTORIQUE
        Le pont historique ARRONDIT la valeur recue avant de borner
        (`int(round(float(value)))`, `round(float(value), 1)`). Boilerack
        REJETTE : une valeur hors grille est refusee, jamais ramenee. La
        doctrine « REJECT, jamais clamp » de `core/validation.py` prevaut, et
        elle est plus stricte — un consommateur qui envoyait `20.4` en consigne
        recevait un `20` silencieux ; il recevra desormais un rejet explicite.

    La fonction ne prend aucun parametre et ne lit aucun fichier : le profil est
    une constante du protocole, pas une configuration d'installation. Rien ici
    n'est propre a un deploiement — ni hote, ni port, ni chemin, ni topic.
    """
    dhw_setpoint = CommandSpec(
        role="dhw_setpoint",
        read="getTempWWsoll",
        write="setTempWWsoll",
        type=ValueType.INTEGER,
        min=10,
        max=60,
        step=1,
        confirm_tolerance=0.0,
        idempotent=True,
        bounds_source=_DHW_BOUNDS_SOURCE,
    )
    heating_setpoint = CommandSpec(
        role="heating_setpoint",
        read="getTempRaumNorSollM1",
        write="setTempRaumNorSollM1",
        type=ValueType.INTEGER,
        min=5,
        max=30,
        step=1,
        confirm_tolerance=0.0,
        idempotent=True,
        bounds_source=_HEATING_BOUNDS_SOURCE,
    )
    curve_shift = CommandSpec(
        role="heating_curve_shift",
        read="getNiveauM1",
        write="setNiveauM1",
        type=ValueType.INTEGER,
        min=-13,
        max=40,
        step=1,
        confirm_tolerance=0.0,
        idempotent=True,
        bounds_source=_SHIFT_BOUNDS_SOURCE,
    )
    curve_slope = CommandSpec(
        role="heating_curve_slope",
        read="getNeigungM1",
        write="setNeigungM1",
        type=ValueType.FLOAT,
        min=0.2,
        max=3.5,
        step=0.1,
        confirm_tolerance=1e-9,
        idempotent=True,
        bounds_source=_SLOPE_BOUNDS_SOURCE,
    )
    roles = (dhw_setpoint, heating_setpoint, curve_shift, curve_slope)
    return Profile(
        name=PRODUCTION_PROFILE_NAME,
        commands={spec.role: spec for spec in roles},
    )
