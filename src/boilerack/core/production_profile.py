"""Profil de PRODUCTION : les roles reellement inscriptibles (lot W4-D).

Pendant de `boilerack.testing.fake_profile`, mais pour la vraie chaudiere. Ce
module ne contient que des DONNEES : le schema et ses invariants restent dans
`boilerack.core.profile`, et rien n'est valide ici qui le soit deja la-bas.

POURQUOI UN SEUL ROLE
    Quatre commandes d'ecriture sont eprouvees par la production du pont
    historique, et `arsenal … boiler_pi/mqtt.md` §5 en documente les bornes. Une
    seule a ete CARACTERISEE : `setNiveauM1`, par la campagne terrain W4-C du
    22 aout 2026. Les trois autres n'ont recu aucune observation de leur reponse
    a l'ecriture.

    W4-C §15 le dit sans detour : « elle ne prouve rien au-delà de
    `setNiveauM1` ». Declarer ici les trois autres reviendrait a ouvrir des
    surfaces d'ecriture sur la foi d'une extrapolation. Le profil n'expose donc
    QUE ce qui a ete observe. L'y ajouter plus tard demandera la meme preuve,
    pas une decision d'ergonomie.

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
_BOUNDS_SOURCE: Final = (
    "arsenal — 00_documentation_arsenal/outils_externes/boiler_pi/mqtt.md §5.3 "
    "(type int, bornes [-13 ; 40], pas 1, tolerance de confirmation nulle) ; "
    "role et commande de lecture : c7-mqtt-read-contract.md §4.2 ; "
    "ecriture caracterisee par w4c-write-capture-protocol.md §16"
)


def build_production_profile() -> Profile:
    """Construit le profil de production.

    Un seul role, `heating_curve_shift` — le decalage de la courbe de chauffe du
    circuit M1 :

    - lecture `getNiveauM1`, ecriture `setNiveauM1` ;
    - entier strict, bornes [-13 ; 40], pas 1 ;
    - tolerance de confirmation NULLE : la relecture confirme par egalite
      exacte, ce que `_confirms` applique deja pour tout role entier.

    La fonction ne prend aucun parametre et ne lit aucun fichier : le profil est
    une constante du protocole, pas une configuration d'installation. Rien ici
    n'est propre a un deploiement — ni hote, ni port, ni chemin, ni topic.
    """
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
        bounds_source=_BOUNDS_SOURCE,
    )
    return Profile(
        name=PRODUCTION_PROFILE_NAME,
        commands={curve_shift.role: curve_shift},
    )
