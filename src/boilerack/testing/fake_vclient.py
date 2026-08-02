"""Double programmable du transport `vcontrold`.

Un test declare a l'avance la SEQUENCE exacte d'interactions attendues (lectures
et ecritures), avec pour chacune le resultat a renvoyer et une latence virtuelle
optionnelle. A l'execution, le double :

- verifie que chaque appel correspond a l'interaction attendue (operation,
  commande, et valeur pour les ecritures) ;
- enregistre tous les appels dans leur ordre exact ;
- fait echouer immediatement tout appel inattendu ou mal argumente ;
- simule la latence en faisant avancer une `VirtualClock`, sans attente reelle ;
- signale les interactions programmees mais jamais consommees.

Le double ne devine jamais : il ne renvoie aucune valeur par defaut et ne tolere
aucun appel non prevu. Une operation « bloquee jusqu'au depassement d'un budget »
se programme simplement comme un resultat `TIMEOUT` assorti d'une latence
superieure au budget du test.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from boilerack.testing.fake_clock import VirtualClock
from boilerack.transport.vclient import (
    ReadResult,
    TransportStatus,
    WriteResult,
)


class FakeVClientError(Exception):
    """Erreur d'utilisation du double : le test a ete mal ecrit ou l'objet teste
    n'a pas respecte la sequence attendue."""


class UnexpectedCall(FakeVClientError):
    """Appel non prevu : operation, commande ou valeur inattendue, ou sequence epuisee."""


class UnconsumedExpectations(FakeVClientError):
    """Des interactions programmees n'ont pas ete consommees a la fin du test."""


@dataclass(frozen=True)
class RecordedCall:
    """Trace d'un appel effectivement recu, dans l'ordre."""

    op: str  # "read" ou "write"
    command: str
    value: float | None  # renseigne uniquement pour les ecritures


@dataclass(frozen=True)
class _Expectation:
    op: str
    command: str
    value: float | None
    result: ReadResult | WriteResult
    latency: float


class FakeVClient:
    """Transport factice conforme au protocole `VClient`.

    Requiert une `VirtualClock` : toute latence programmee la fait avancer, ce
    qui garde les tests deterministes et sans attente reelle.
    """

    def __init__(self, clock: VirtualClock) -> None:
        self._clock = clock
        self._expectations: deque[_Expectation] = deque()
        self._calls: list[RecordedCall] = []

    # ------------------------------------------------------------------
    # Programmation
    # ------------------------------------------------------------------

    def expect_read(
        self,
        command: str,
        *,
        returns: float | None = None,
        result: ReadResult | None = None,
        latency: float = 0.0,
    ) -> None:
        """Programme une lecture attendue.

        Fournir SOIT `returns` (valeur numerique d'une lecture reussie), SOIT
        `result` (un `ReadResult` explicite, notamment pour les cas d'erreur).
        """
        if (returns is None) == (result is None):
            raise FakeVClientError(
                "expect_read attend exactement l'un de `returns` ou `result`."
            )
        if latency < 0:
            raise FakeVClientError(f"latence negative interdite : {latency!r}")
        if result is None:
            result = ReadResult(status=TransportStatus.OK, value=returns)
        self._expectations.append(
            _Expectation("read", command, None, result, latency)
        )

    def expect_write(
        self,
        command: str,
        value: float,
        *,
        result: WriteResult | None = None,
        latency: float = 0.0,
    ) -> None:
        """Programme une ecriture attendue.

        Par defaut, l'ecriture reussit au niveau transport. Fournir `result`
        pour programmer un echec (`DAEMON_UNREACHABLE`, `TIMEOUT`, ...).
        """
        if latency < 0:
            raise FakeVClientError(f"latence negative interdite : {latency!r}")
        if result is None:
            result = WriteResult(status=TransportStatus.OK)
        self._expectations.append(
            _Expectation("write", command, value, result, latency)
        )

    # ------------------------------------------------------------------
    # Protocole VClient
    # ------------------------------------------------------------------

    def read(self, command: str) -> ReadResult:
        expectation = self._pop_expectation("read", command, None)
        self._calls.append(RecordedCall("read", command, None))
        self._apply_latency(expectation.latency)
        assert isinstance(expectation.result, ReadResult)
        return expectation.result

    def write(self, command: str, value: float) -> WriteResult:
        expectation = self._pop_expectation("write", command, value)
        self._calls.append(RecordedCall("write", command, value))
        self._apply_latency(expectation.latency)
        assert isinstance(expectation.result, WriteResult)
        return expectation.result

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    @property
    def calls(self) -> tuple[RecordedCall, ...]:
        """Tous les appels recus, dans l'ordre exact."""
        return tuple(self._calls)

    def unconsumed(self) -> tuple[_Expectation, ...]:
        """Interactions programmees mais jamais consommees."""
        return tuple(self._expectations)

    def assert_all_consumed(self) -> None:
        """Echoue si des interactions programmees restent inutilisees."""
        if self._expectations:
            restantes = ", ".join(
                f"{e.op} {e.command}" for e in self._expectations
            )
            raise UnconsumedExpectations(
                f"{len(self._expectations)} interaction(s) non consommee(s) : {restantes}"
            )

    # ------------------------------------------------------------------
    # Interne
    # ------------------------------------------------------------------

    def _pop_expectation(
        self, op: str, command: str, value: float | None
    ) -> _Expectation:
        if not self._expectations:
            raise UnexpectedCall(
                f"appel inattendu {op} {command!r} : plus aucune interaction programmee"
            )
        expectation = self._expectations[0]
        if expectation.op != op or expectation.command != command:
            raise UnexpectedCall(
                f"appel inattendu {op} {command!r} ; "
                f"attendu {expectation.op} {expectation.command!r}"
            )
        if op == "write" and expectation.value != value:
            raise UnexpectedCall(
                f"argument inattendu pour {command!r} : recu {value!r}, "
                f"attendu {expectation.value!r}"
            )
        self._expectations.popleft()
        return expectation

    def _apply_latency(self, latency: float) -> None:
        if latency:
            self._clock.advance(latency)
