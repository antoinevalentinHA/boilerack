"""Point d'entree utilisateur de Boilerack (lot C10).

Deux chemins publics, **strictement equivalents**, servis par la meme fonction :

    boilerack --config /chemin/boilerack.toml
    python -m boilerack --config /chemin/boilerack.toml

Le module `__main__` ne porte aucune logique propre : il delegue a `main` et
projette son resultat.

CE MODULE EST LA RACINE DU PROCESSUS
    C'est a ce titre, et a ce titre seul, qu'il configure la journalisation. Une
    bibliotheque ne doit jamais imposer sa politique de journaux a son
    appelant ; C9 l'a explicitement refuse. Importer ce module ne touche a rien :
    seul l'appel de `main` prend possession du processus.

`main` REND UN ENTIER
    Elle ne quitte jamais le processus. Le script installe execute
    `sys.exit(main())` — c'est le gabarit standard de l'ecosysteme —, `__main__`
    fait de meme, et un test peut ecrire `assert main([...]) == 0` sans capturer
    d'exception.

    Nuance assumee : l'analyseur d'arguments leve `SystemExit` depuis l'interieur
    de `main` pour une option invalide (`2`) et pour `--help` (`0`). Ces sorties
    traversent volontairement. Les intercepter pour uniformiser obligerait a
    traiter `--help` comme une erreur.

FRONTIERE CONFIGURATION / EXECUTION
    Tout ce qui precede `run_lifecycle` peut devenir une erreur de configuration,
    presentee sans trace d'appels et rendue en `2`. A partir de `run_lifecycle`,
    aucune exception n'est traduite : une panne garde sa trace et son code natif.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Final, Sequence

from boilerack.config import ConfigurationError, load_config
from boilerack.lifecycle import run_lifecycle

__all__ = ["LOG_LEVELS", "CODE_CONFIGURATION", "build_parser", "main"]

#: Jeu FERME de niveaux acceptes. `logging` en accepterait bien d'autres —
#: entiers arbitraires, niveaux personnalises — sans qu'aucun ait de sens ici.
LOG_LEVELS: Final = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

#: Convention Unix pour une erreur d'usage. C'est aussi le code que l'analyseur
#: d'arguments rend deja de lui-meme : en retenir un autre pour le fichier de
#: configuration creerait une incoherence avec « mauvaise option ».
CODE_CONFIGURATION: Final = 2

#: Horodatage, niveau, logger, message. Aucune couleur, aucune dependance. Un
#: pont qui tourne en continu produit des lignes qu'il faut pouvoir situer, et
#: un lancement manuel n'ajoute aucun horodatage de lui-meme.
_LOG_FORMAT: Final = "%(asctime)s %(levelname)s %(name)s %(message)s"

_PROG: Final = "boilerack"


def build_parser() -> argparse.ArgumentParser:
    """Analyseur d'arguments. Aucun effet de bord."""
    parser = argparse.ArgumentParser(
        prog=_PROG,
        description="Pont MQTT de lecture pour chaudieres Viessmann via vcontrold.",
    )
    parser.add_argument(
        "--config",
        required=True,
        metavar="CHEMIN",
        help=(
            "chemin du fichier de configuration TOML (obligatoire ; aucun "
            "emplacement par defaut n'est cherche)"
        ),
    )
    parser.add_argument(
        "--log-level",
        choices=LOG_LEVELS,
        default="INFO",
        help="niveau de journalisation de cette execution (defaut : INFO)",
    )
    return parser


def _configurer_journalisation(niveau: str) -> None:
    """Prend possession de la journalisation du processus.

    `force` est indispensable : sans lui, la configuration simplifiee de la
    bibliotheque standard **ne fait rien** lorsque la racine possede deja un
    gestionnaire. Deux invocations successives avec des niveaux differents
    laisseraient alors le premier en place, silencieusement.

    Consequence a connaitre : les gestionnaires existants sont retires **et
    fermes**. C'est legitime ici — cette fonction est la racine du processus —
    mais cela impose aux tests de restaurer l'etat du logger racine.
    """
    logging.basicConfig(
        level=getattr(logging, niveau),
        stream=sys.stderr,
        format=_LOG_FORMAT,
        force=True,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Analyse, configure, charge, puis execute. Rend le resultat logique.

    Sequence :

        analyse des arguments
        configuration de la journalisation
        chargement et validation de la configuration
        ================= FRONTIERE =================
        run_lifecycle(config)

    Resultats : `0` pour un arret normal ou demande par `SIGTERM`, `130` pour un
    arret demande par `SIGINT`, `2` pour une faute d'usage ou de configuration.
    Une panne n'est pas rendue : elle remonte, avec sa trace, et Python en fait
    un `1`.
    """
    arguments = build_parser().parse_args(argv)
    _configurer_journalisation(arguments.log_level)

    try:
        config = load_config(arguments.config)
    except ConfigurationError as erreur:
        # Pas de trace d'appels : la faute est dans le fichier, une pile
        # designerait le code et n'apprendrait rien a qui edite un TOML.
        print(f"{_PROG}: configuration invalide: {erreur}", file=sys.stderr)
        return CODE_CONFIGURATION

    # A partir d'ici, plus rien n'est traduit : toute exception est une panne du
    # programme ou de son environnement, et garde sa trace et son code natif.
    return run_lifecycle(config)
