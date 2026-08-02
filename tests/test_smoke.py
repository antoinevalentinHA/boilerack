"""Tests de fumee du squelette.

Verifient que le paquet s'importe et que la version a une source unique.
Aucune logique metier n'existe a ce stade.
"""

from importlib.metadata import version as distribution_version

import boilerack


def test_le_paquet_s_importe() -> None:
    assert boilerack.__version__ == "0.0.0"


def test_source_unique_de_version() -> None:
    """La version de la distribution est lue depuis __init__.py par Hatchling.

    Une divergence signalerait la reapparition de deux sources independantes.
    """
    assert distribution_version("boilerack") == boilerack.__version__
