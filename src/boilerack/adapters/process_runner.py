"""Frontiere ETROITE autour d'un sous-processus, generique et injectable.

Ce module ne connait NI `vclient`, NI `vcontrold`, NI aucun dialecte de
commande : il execute une liste d'arguments deja construite et rend compte de
l'issue de facon typee. La construction des arguments et la traduction de la
sortie en statut de transport appartiennent a un futur adaptateur `vclient`,
bloque tant que son contrat reel n'est pas caracterise.

Garanties de securite de lancement :

- liste d'arguments uniquement, jamais `shell=True`, aucun assemblage shell ;
- timeout obligatoire, fini et strictement positif ;
- capture bornee de stdout/stderr en OCTETS bruts (aucun decodage ici :
  l'encodage explicite releve de l'adaptateur qui interprete la sortie) ;
- aucune dependance au repertoire courant : l'appelant fournit un chemin
  d'executable, ce module ne fixe pas de `cwd` implicite ;
- l'echec de LANCEMENT (executable absent, non executable, permission refusee)
  et le TIMEOUT sont distingues explicitement du deroulement normal.

L'implementation reelle `SubprocessRunner` accepte un `runner` injectable
(par defaut `subprocess.run`) : tous les tests injectent un faux runner et
n'executent JAMAIS de processus reel.
"""

from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol, runtime_checkable


@dataclass(frozen=True)
class ProcessResult:
    """Issue TYPEE d'une invocation de sous-processus.

    - `returncode` : code retour du processus, ou `None` s'il n'a pas conclu
      normalement (timeout, ou echec de lancement) ;
    - `stdout` / `stderr` : sortie brute en octets (jamais decodee ici) ;
    - `timed_out` : le processus a depasse le budget de temps ;
    - `launch_failed` : le processus n'a pas pu etre lance (donc AUCUNE commande
      n'a ete transmise) ;
    - `launch_error` : nom de la classe d'exception de lancement, a titre de
      diagnostic (jamais de message brut, pour ne divulguer ni chemin ni secret).

    `timed_out` et `launch_failed` sont mutuellement exclusifs et impliquent
    tous deux `returncode is None`.
    """

    returncode: int | None
    stdout: bytes
    stderr: bytes
    timed_out: bool = False
    launch_failed: bool = False
    launch_error: str = ""


@runtime_checkable
class ProcessRunner(Protocol):
    """Frontiere minimale d'execution de sous-processus."""

    def run(
        self,
        args: list[str],
        timeout: float,
        env: Mapping[str, str] | None = None,
    ) -> ProcessResult:
        ...


def _as_bytes(value: object) -> bytes:
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, str):
        # Defense : si un runner injecte renvoie du texte, on le fige en octets
        # UTF-8 explicitement (le runner reel capture deja des octets).
        return value.encode("utf-8", "surrogatepass")
    raise TypeError(f"sortie de processus inattendue : {type(value).__name__}")


class SubprocessRunner:
    """`ProcessRunner` reel, fonde sur `subprocess.run`, sans shell.

    Le callable sous-jacent est INJECTABLE (`runner`) pour permettre des tests
    entierement hors ligne : par defaut `subprocess.run`, jamais appele dans la
    suite de tests.
    """

    def __init__(self, *, runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> None:
        self._runner = runner

    def run(
        self,
        args: list[str],
        timeout: float,
        env: Mapping[str, str] | None = None,
    ) -> ProcessResult:
        if not isinstance(args, (list, tuple)) or len(args) == 0:
            raise ValueError("args doit etre une liste non vide d'arguments")
        arg_list = list(args)
        if not all(isinstance(a, str) for a in arg_list):
            raise ValueError("tous les arguments doivent etre des chaines")
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool):
            raise ValueError(f"timeout doit etre numerique : {timeout!r}")
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError(f"timeout doit etre fini et strictement positif : {timeout!r}")

        try:
            completed = self._runner(
                arg_list,
                capture_output=True,
                timeout=timeout,
                shell=False,  # explicite : jamais de shell, jamais d'assemblage shell
                env=env,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            # Le processus a ete lance mais n'a pas repondu dans le budget : issue
            # AMBIGUE (une commande a pu etre transmise). Ce n'est pas un echec de
            # lancement.
            return ProcessResult(
                returncode=None,
                stdout=_as_bytes(exc.stdout),
                stderr=_as_bytes(exc.stderr),
                timed_out=True,
            )
        except OSError as exc:
            # `FileNotFoundError`, `PermissionError` et autres `OSError` a la
            # tentative de lancement : le processus N'A PAS demarre, donc aucune
            # commande n'a ete transmise. On expose uniquement le NOM de la classe
            # d'exception (aucun message, aucun chemin, aucun secret).
            return ProcessResult(
                returncode=None,
                stdout=b"",
                stderr=b"",
                launch_failed=True,
                launch_error=type(exc).__name__,
            )

        return ProcessResult(
            returncode=completed.returncode,
            stdout=_as_bytes(completed.stdout),
            stderr=_as_bytes(completed.stderr),
        )
