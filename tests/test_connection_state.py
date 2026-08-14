"""Tests de `boilerack.connection_state` — etat de connexion partage (C11).

Aucun MQTT, aucun Paho, aucun reseau : la primitive est pure et se teste seule.
Un seul test emploie un vrai fil, et c'est pour PROUVER — non supposer — qu'une
transition posee depuis un autre fil est bien vue par le fil consommateur.
"""

from __future__ import annotations

import ast
import pathlib
import threading

from boilerack.connection_state import ConnectionState
from boilerack import connection_state as module


# ---------------------------------------------------------------------------
# Etat initial
# ---------------------------------------------------------------------------


def test_etat_initial_non_connecte_sans_reprise() -> None:
    etat = ConnectionState()
    assert etat.connected is False
    assert etat.consume_recovery() is False


# ---------------------------------------------------------------------------
# Transitions
# ---------------------------------------------------------------------------


def test_transition_vers_connecte_arme_une_reprise() -> None:
    """`False -> True` : la seule transition qui arme."""
    etat = ConnectionState()
    etat.notify(True)
    assert etat.connected is True
    assert etat.consume_recovery() is True


def test_connexion_repetee_n_arme_pas_deux_fois() -> None:
    """`True -> True` n'est pas une transition : aucun armement supplementaire."""
    etat = ConnectionState()
    etat.notify(True)
    etat.notify(True)
    assert etat.consume_recovery() is True
    assert etat.consume_recovery() is False


def test_deconnexion_avant_consommation_annule_la_reprise() -> None:
    """Le coeur de §8.2 : un marqueur monotone publierait `online` hors ligne."""
    etat = ConnectionState()
    etat.notify(True)
    etat.notify(False)
    assert etat.connected is False
    assert etat.consume_recovery() is False


def test_reconnexion_apres_deconnexion_arme_de_nouveau() -> None:
    etat = ConnectionState()
    etat.notify(True)
    etat.notify(False)
    etat.notify(True)
    assert etat.consume_recovery() is True


def test_etat_final_deconnecte_n_arme_rien() -> None:
    """`connect / disc / connect / disc` : l'etat final decide, pas l'historique."""
    etat = ConnectionState()
    for connecte in (True, False, True, False):
        etat.notify(connecte)
    assert etat.connected is False
    assert etat.consume_recovery() is False


def test_consommation_rend_vrai_une_seule_fois() -> None:
    etat = ConnectionState()
    etat.notify(True)
    assert [etat.consume_recovery() for _ in range(4)] == [True, False, False, False]


# ---------------------------------------------------------------------------
# Base optimiste et desarmement
# ---------------------------------------------------------------------------


def test_base_optimiste_connecte_sans_armer() -> None:
    etat = ConnectionState()
    etat.mark_connected()
    assert etat.connected is True
    assert etat.consume_recovery() is False


def test_base_optimiste_suivie_d_un_succes_n_arme_rien() -> None:
    """Le CONNACK initial reussi ne doit provoquer aucune republication."""
    etat = ConnectionState()
    etat.mark_connected()
    etat.notify(True)
    assert etat.consume_recovery() is False


def test_un_echec_a_autorite_sur_la_base_optimiste() -> None:
    """§8.3 : le fait observe l'emporte sur l'hypothese posee par `start()`."""
    etat = ConnectionState()
    etat.mark_connected()
    etat.notify(False)
    assert etat.connected is False
    assert etat.consume_recovery() is False


def test_echec_puis_reussite_arme_exactement_une_reprise() -> None:
    """La sequence que l'ancien placement de la base faisait perdre."""
    etat = ConnectionState()
    etat.mark_connected()
    etat.notify(False)
    etat.notify(True)
    assert [etat.consume_recovery() for _ in range(3)] == [True, False, False]


def test_base_optimiste_efface_une_reprise_en_attente() -> None:
    """Un `start()` reprend a zero : rien de la session precedente ne survit."""
    etat = ConnectionState()
    etat.notify(True)
    etat.mark_connected()
    assert etat.consume_recovery() is False


def test_desarmement_laisse_l_etat_de_connexion_intact() -> None:
    etat = ConnectionState()
    etat.notify(True)
    etat.disarm()
    assert etat.connected is True
    assert etat.consume_recovery() is False


# ---------------------------------------------------------------------------
# Fil
# ---------------------------------------------------------------------------


def test_transition_posee_depuis_un_autre_fil_est_vue_par_le_consommateur() -> None:
    """PROUVE, non suppose : le fil emetteur n'est pas celui qui consomme."""
    etat = ConnectionState()
    fils: list[str] = []

    def emetteur() -> None:
        fils.append(threading.current_thread().name)
        etat.notify(True)

    fil = threading.Thread(target=emetteur, name="emetteur-c11")
    fil.start()
    fil.join()

    assert fils == ["emetteur-c11"]
    assert threading.current_thread().name != "emetteur-c11"
    assert etat.consume_recovery() is True


def test_rafale_concurrente_ne_produit_jamais_deux_reprises() -> None:
    """Huit fils notifient une connexion : au plus UNE reprise en decoule."""
    etat = ConnectionState()
    depart = threading.Barrier(8)

    def notifier() -> None:
        depart.wait()
        etat.notify(True)

    fils = [threading.Thread(target=notifier) for _ in range(8)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()

    reprises = sum(etat.consume_recovery() for _ in range(8))
    assert reprises == 1


# ---------------------------------------------------------------------------
# Frontieres du module
# ---------------------------------------------------------------------------


def test_module_pur_sans_horloge_ni_reseau_ni_file() -> None:
    """Un seul verrou, aucune horloge, aucune file, aucun transport."""
    source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
    arbre = ast.parse(source)
    importes = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            importes.update(a.name.split(".")[0] for a in noeud.names)
        elif isinstance(noeud, ast.ImportFrom) and noeud.module:
            importes.add(noeud.module.split(".")[0])
    assert importes == {"__future__", "threading"}
    code = ast.unparse(arbre)
    for interdit in ("Queue", "deque", "time.", "datetime", "socket", "paho"):
        assert interdit not in code
    assert code.count("threading.Lock()") == 1
