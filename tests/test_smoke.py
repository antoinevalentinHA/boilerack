"""Test de fumee du squelette C0.

Verifie uniquement que le paquet s'importe et expose sa version.
Aucune logique metier n'existe a ce stade.
"""

import boilerack


def test_le_paquet_s_importe() -> None:
    assert boilerack.__version__ == "0.0.0"
