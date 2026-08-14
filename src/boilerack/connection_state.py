"""Etat de connexion MQTT partage entre le fil de rappel et le fil metier (lot C11).

Pendant exact de `SignalStop` en C9 : un objet dedie qui recoit des transitions
depuis n'importe quel fil et qu'UN SEUL fil consomme. Sa responsabilite est
entiere et unique — repondre a « une reprise de presence est-elle due
maintenant ? ».

POURQUOI UN MODULE A PART
    Le publieur ne peut pas heberger cette primitive : un test verrouille qu'il
    n'importe ni `threading` ni `asyncio`, et il ne detient aucun verrou. La
    frontiere `boilerack.transport.mqtt` est une declaration pure — Protocols et
    dataclasses — ou une classe concurrente n'a pas sa place. La racine de
    composition, elle, assemble et ne porte pas de mecanique. Ce module feuille
    reprend donc le placement de `clock.py` et `bounded_queue.py`.

POURQUOI UN SEUL VERROU SUFFIT
    Les quatre methodes publiques sont des sections critiques courtes : aucune
    n'appelle une autre, aucune n'invoque de code fourni par l'appelant, aucune
    ne fait d'entree-sortie. Ni imbrication, ni reentrance ne sont possibles.

CE QUE CETTE PRIMITIVE N'EST PAS
    Ni une file — la seule information utile est « une reprise est-elle due »,
    qui est idempotente et sans historique. Ni une horloge. Ni une machine
    d'etat : deux booleens suffisent, et rien de plus n'est ajoute.
"""

from __future__ import annotations

import threading

__all__ = ["ConnectionState"]


class ConnectionState:
    """Etat courant de la connexion, plus un marqueur de reprise annulable.

    Table de transitions (contrat C11 §8.2) :

    | Evenement                          | Etat            | Marqueur   |
    |------------------------------------|-----------------|------------|
    | `notify(True)`, etat non connecte  | devient connecte| **arme**   |
    | `notify(True)`, etat deja connecte | inchange        | inchange   |
    | `notify(False)`                    | non connecte    | **desarme**|
    | `mark_connected()`                 | connecte        | desarme    |
    | `disarm()`                         | inchange        | desarme    |

    L'invariant normatif qui en decoule :

        Au moment ou le fil metier consomme une reprise, la derniere transition
        observee doit ENCORE etre une connexion reussie. Toute deconnexion
        posterieure a l'armement annule la reprise en attente.

    C'est la raison pour laquelle un simple marqueur monotone est interdit : il
    ferait annoncer `online` alors que le pont est deconnecte.
    """

    def __init__(self) -> None:
        self._verrou = threading.Lock()
        self._connected = False
        self._recovery_pending = False

    # -- ecriture depuis n'importe quel fil ----------------------------------

    def notify(self, connected: bool) -> None:
        """Enregistre une transition REELLEMENT observee.

        Appele depuis le contexte de rappel du transport, donc potentiellement
        depuis un autre fil que celui du runner. Ne bloque pas, ne leve pas.

        Un armement n'a lieu que sur une transition non connecte -> connecte :
        deux notifications de connexion successives ne produisent donc qu'une
        seule reprise.
        """
        with self._verrou:
            if connected:
                if not self._connected:
                    self._connected = True
                    self._recovery_pending = True
            else:
                self._connected = False
                self._recovery_pending = False

    # -- ecriture depuis le fil metier ---------------------------------------

    def mark_connected(self) -> None:
        """Pose la base optimiste : connecte, sans reprise en attente.

        Appelee par `start()` **avant d'ouvrir la connexion**, donc avant tout
        appel susceptible de rendre un rappel possible. Cette place est sure par
        construction et non par chronometrie : aucune notification ne peut la
        preceder.

        La base est optimiste — aucune confirmation n'a encore ete recue — mais
        toute notification reelle a ensuite AUTORITE sur elle, quel que soit
        l'instant ou elle survient. Un echec d'etablissement fait donc retomber
        l'etat, et une reussite ulterieure constitue bien une transition.
        """
        with self._verrou:
            self._connected = True
            self._recovery_pending = False

    def disarm(self) -> None:
        """Annule toute reprise en attente, sans toucher a l'etat de connexion.

        Appelee par `stop()`. Volontairement independante de toute notification
        de deconnexion : la surete de l'arret ne doit dependre d'aucun rappel
        que le transport n'est pas tenu d'emettre.
        """
        with self._verrou:
            self._recovery_pending = False

    # -- consommation, fil metier uniquement ---------------------------------

    def consume_recovery(self) -> bool:
        """Rend `True` AU PLUS UNE FOIS par transition, et desarme.

        Rend `True` si et seulement si une reprise est armee **et** que l'etat
        courant est toujours connecte. Dans tout autre cas, rend `False` sans
        rien modifier.
        """
        with self._verrou:
            if self._recovery_pending and self._connected:
                self._recovery_pending = False
                return True
            return False

    # -- inspection ----------------------------------------------------------

    @property
    def connected(self) -> bool:
        """Dernier etat observe. Pour l'observabilite et les tests UNIQUEMENT.

        Aucun code de production ne lit cette propriete : la reprise se decide
        par `consume_recovery()`, jamais par interrogation repetee d'un etat.
        """
        with self._verrou:
            return self._connected
