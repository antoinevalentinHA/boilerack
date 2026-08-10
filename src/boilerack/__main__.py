"""Permet `python -m boilerack`. Aucune logique propre.

Le script installe par le paquet execute `sys.exit(main())` de lui-meme ; ici,
c'est a ce module de projeter le resultat en code de sortie. Les deux chemins
appellent la meme fonction et doivent rester indiscernables.
"""

from boilerack.cli import main

raise SystemExit(main())
