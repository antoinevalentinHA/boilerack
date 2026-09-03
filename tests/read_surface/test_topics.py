"""Tests de `boilerack.read_surface.topics` — §3.2, §3.3, §3.4 et §11 de C7-B."""

from __future__ import annotations

import ast
import pathlib

import pytest

from boilerack.read_surface import topics
from boilerack.read_surface.topics import (
    BRIDGE_SUFFIXES,
    TELEMETRY_SUFFIXES,
    V1_SUFFIXES,
    InvalidMqttTopic,
    build_topic,
    normalize_prefix,
)

# ---------------------------------------------------------------------------
# §3.3 — tableau de normalisation, ligne a ligne
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("entree", "attendu"),
    [
        ("boiler", "boiler"),  # accepte tel quel
        ("boiler/", "boiler"),  # barre terminale retiree
        ("/boiler", "boiler"),  # barre initiale retiree
        ("boiler//x", "boiler/x"),  # barres consecutives reduites
        ("maison/boiler", "maison/boiler"),  # plusieurs niveaux acceptes
    ],
)
def test_normalisation_du_tableau_contractuel(entree: str, attendu: str) -> None:
    assert normalize_prefix(entree) == attendu


def test_prefixe_par_defaut_du_contrat_est_stable() -> None:
    """§3.1 : defaut contractuel `boiler`, sans barre terminale."""
    assert normalize_prefix("boiler") == "boiler"


def test_cumul_barre_initiale_et_terminale() -> None:
    assert normalize_prefix("/boiler/") == "boiler"


def test_cumul_barres_multiples_aux_deux_extremites() -> None:
    assert normalize_prefix("//maison///boiler//") == "maison/boiler"


def test_prefixe_multi_niveaux_profond() -> None:
    assert normalize_prefix("maison/cave/boiler") == "maison/cave/boiler"


def test_normalisation_idempotente() -> None:
    once = normalize_prefix("/maison//boiler/")
    assert normalize_prefix(once) == once


# ---------------------------------------------------------------------------
# §3.3 — refus
# ---------------------------------------------------------------------------


def test_chaine_vide_rejetee() -> None:
    with pytest.raises(InvalidMqttTopic, match="espace de noms"):
        normalize_prefix("")


@pytest.mark.parametrize("entree", ["/", "//", "////"])
def test_prefixe_uniquement_compose_de_barres_rejete(entree: str) -> None:
    """Le prefixe EFFECTIF serait vide : meme refus que la chaine vide."""
    with pytest.raises(InvalidMqttTopic, match="espace de noms"):
        normalize_prefix(entree)


@pytest.mark.parametrize(
    "entree", ["boiler+", "+", "maison/+/boiler", "boiler#", "#", "maison/#"]
)
def test_jokers_mqtt_rejetes(entree: str) -> None:
    with pytest.raises(InvalidMqttTopic, match="joker"):
        normalize_prefix(entree)


@pytest.mark.parametrize(
    "entree",
    [
        "boiler\x00",  # NUL, nomme explicitement par le contrat
        "\x00",
        "boiler\x01",
        "boiler\x1f",
        "boiler\n",
        "boiler\t",
        "boiler\x7f",
        "boiler\x9f",
    ],
)
def test_caracteres_de_controle_rejetes(entree: str) -> None:
    with pytest.raises(InvalidMqttTopic, match="caractere de controle"):
        normalize_prefix(entree)


@pytest.mark.parametrize("entree", ["$SYS", "$SYS/boiler", "$"])
def test_prefixe_commencant_par_dollar_rejete(entree: str) -> None:
    with pytest.raises(InvalidMqttTopic, match=r"\$"):
        normalize_prefix(entree)


def test_dollar_apres_normalisation_rejete() -> None:
    """`/$SYS` produirait un topic commencant par `$` : meme refus."""
    with pytest.raises(InvalidMqttTopic, match=r"\$"):
        normalize_prefix("/$SYS")


def test_dollar_hors_tete_accepte() -> None:
    """Le contrat ne refuse `$` qu'en TETE de prefixe. Rien d'autre n'est invente."""
    assert normalize_prefix("maison/$x") == "maison/$x"


@pytest.mark.parametrize("entree", [None, 42, 3.5, b"boiler", ["boiler"], True])
def test_entree_non_textuelle_rejetee(entree: object) -> None:
    with pytest.raises(InvalidMqttTopic, match="doit etre une chaine"):
        normalize_prefix(entree)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# §3.3 — ce que le contrat ne dit pas n'est pas interdit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entree", ["mon boiler", " boiler ", "chaudiere-été", "böiler"])
def test_espaces_et_unicode_imprimable_acceptes(entree: str) -> None:
    """Limite assumee : §3.3 ne les mentionne pas, aucune interdiction n'est inventee."""
    assert normalize_prefix(entree) == entree


# ---------------------------------------------------------------------------
# §3.2 — construction et invariance du suffixe
# ---------------------------------------------------------------------------


def test_construction_conforme_au_contrat() -> None:
    assert build_topic("boiler", "bridge/online") == "boiler/bridge/online"


def test_construction_normalise_le_prefixe() -> None:
    assert build_topic("/maison//boiler/", "bridge/online") == "maison/boiler/bridge/online"


@pytest.mark.parametrize("prefixe", ["boiler", "maison/boiler", "/a/", "x//y"])
@pytest.mark.parametrize("suffixe", V1_SUFFIXES)
def test_suffixe_invariant_quel_que_soit_le_prefixe(prefixe: str, suffixe: str) -> None:
    """§3.2 : un suffixe **MUST NOT** dependre de la valeur du prefixe."""
    topic = build_topic(prefixe, suffixe)
    prefixe_normalise = normalize_prefix(prefixe)
    assert topic == f"{prefixe_normalise}/{suffixe}"
    assert topic[len(prefixe_normalise) + 1 :] == suffixe


def test_prefixe_invalide_empeche_toute_construction() -> None:
    with pytest.raises(InvalidMqttTopic):
        build_topic("", "bridge/online")


# ---------------------------------------------------------------------------
# Validite syntaxique d'un suffixe
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "suffixe",
    ["a", "bridge/online", "telemetry/heating/curve/slope", "un suffixe", "$x", "a/$b"],
)
def test_suffixes_syntaxiquement_valides(suffixe: str) -> None:
    """`$` n'est pas refuse dans un suffixe : il n'est jamais en tete du topic."""
    assert build_topic("boiler", suffixe) == f"boiler/{suffixe}"


@pytest.mark.parametrize(
    ("suffixe", "motif"),
    [
        ("", "vide"),
        ("/bridge/online", "bordure"),
        ("bridge/online/", "bordure"),
        ("/bridge/online/", "bordure"),
        ("bridge//online", "consecutives"),
        ("bridge/+/online", "joker"),
        ("bridge/#", "joker"),
        ("bridge/on\x00line", "caractere de controle"),
        ("bridge/on\x1fline", "caractere de controle"),
    ],
)
def test_suffixes_syntaxiquement_invalides(suffixe: str, motif: str) -> None:
    with pytest.raises(InvalidMqttTopic, match=motif):
        build_topic("boiler", suffixe)


@pytest.mark.parametrize("suffixe", [None, 7, b"bridge/online"])
def test_suffixe_non_textuel_rejete(suffixe: object) -> None:
    with pytest.raises(InvalidMqttTopic, match="doit etre une chaine"):
        build_topic("boiler", suffixe)  # type: ignore[arg-type]


def test_suffixe_jamais_normalise() -> None:
    """Un suffixe mal forme est REFUSE, jamais corrige en silence."""
    with pytest.raises(InvalidMqttTopic):
        build_topic("boiler", "bridge//online")


# ---------------------------------------------------------------------------
# §11 — surface exacte de la v1
# ---------------------------------------------------------------------------


def test_treize_suffixes_exactement() -> None:
    assert len(V1_SUFFIXES) == 13


def test_dix_mesures_de_telemetrie() -> None:
    assert len(TELEMETRY_SUFFIXES) == 10
    assert all(s.startswith("telemetry/") for s in TELEMETRY_SUFFIXES)


def test_trois_topics_de_service() -> None:
    assert len(BRIDGE_SUFFIXES) == 3
    assert all(s.startswith("bridge/") for s in BRIDGE_SUFFIXES)


def test_surface_v1_est_la_concatenation_stable_des_deux_groupes() -> None:
    assert V1_SUFFIXES == TELEMETRY_SUFFIXES + BRIDGE_SUFFIXES


def test_contenu_exact_de_la_surface_v1() -> None:
    assert V1_SUFFIXES == (
        "telemetry/temperatures/outdoor",
        "telemetry/temperatures/supply",
        "telemetry/temperatures/dhw",
        "telemetry/dhw/setpoint",
        "telemetry/heating/setpoint",
        "telemetry/heating/reduced_reference",
        "telemetry/heating/curve/slope",
        "telemetry/heating/curve/shift",
        "telemetry/burner/modulation",
        "telemetry/burner/state",
        "bridge/online",
        "bridge/telemetry_status",
        "bridge/heartbeat",
    )


def test_ordre_stable_entre_deux_lectures() -> None:
    assert tuple(V1_SUFFIXES) == tuple(V1_SUFFIXES)
    assert list(V1_SUFFIXES) == list(topics.V1_SUFFIXES)


def test_aucun_doublon() -> None:
    assert len(set(V1_SUFFIXES)) == len(V1_SUFFIXES)


@pytest.mark.parametrize("collection", [V1_SUFFIXES, TELEMETRY_SUFFIXES, BRIDGE_SUFFIXES])
def test_autorite_immutable(collection: object) -> None:
    assert isinstance(collection, tuple)


def test_battement_present_mais_recommande_seulement() -> None:
    """§9 conserve `bridge/heartbeat` en **SHOULD**, pour compatibilite historique.

    Il appartient bien a la surface v1 contractuelle : ce test fige sa presence,
    et sa nature recommandee reste documentaire — aucune structure ne l'encode,
    faute de consommateur dans ce lot.
    """
    assert "bridge/heartbeat" in V1_SUFFIXES


@pytest.mark.parametrize(
    "absent",
    [
        "bridge/version",
        "error/last",
        "boilerack/command",
        "boilerack/ack",
        "capabilities",
    ],
)
def test_topics_hors_surface_absents(absent: str) -> None:
    """Reports (§4.3, §13), hors perimetre (§13) et surface transactionnelle (§14)."""
    assert absent not in V1_SUFFIXES


def test_les_deux_topics_de_brulleur_et_aucun_guard() -> None:
    """§4.3 amende : le brulleur entre. `guard/*` reste hors perimetre.

    Les topics du superviseur ne sont pas une dette de parite : ils sont publies
    par le superviseur lui-meme, pas par un pont, et lui survivront.
    """
    assert [s for s in V1_SUFFIXES if "burner" in s] == [
        "telemetry/burner/modulation",
        "telemetry/burner/state",
    ]
    assert not any(s.startswith("guard/") for s in V1_SUFFIXES)


def test_tous_les_suffixes_de_la_surface_sont_syntaxiquement_valides() -> None:
    for suffixe in V1_SUFFIXES:
        assert build_topic("boiler", suffixe) == f"boiler/{suffixe}"


# ---------------------------------------------------------------------------
# Absence d'effet de bord
# ---------------------------------------------------------------------------

_INTERDITS = {
    "paho",
    "socket",
    "subprocess",
    "threading",
    "asyncio",
    "time",
    "datetime",
    "os",
    "pathlib",
}


def _modules_importes(module: object) -> set[str]:
    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")  # type: ignore[arg-type]
    noms: set[str] = set()
    for noeud in ast.walk(ast.parse(source)):
        if isinstance(noeud, ast.Import):
            noms.update(alias.name.split(".")[0] for alias in noeud.names)
        elif isinstance(noeud, ast.ImportFrom) and noeud.module:
            noms.add(noeud.module.split(".")[0])
    return noms


def test_module_sans_dependance_technique() -> None:
    """Ni MQTT, ni `vclient`, ni horloge, ni processus, ni socket."""
    assert _modules_importes(topics) & _INTERDITS == set()


def test_module_ne_depend_d_aucune_autre_partie_du_projet() -> None:
    importes = _modules_importes(topics)
    assert not any(nom == "boilerack" for nom in importes)
