"""`ProcessRunner` generique : frontiere de lancement, sans processus reel.

Le runner sous-jacent (`subprocess.run`) est INJECTE par un faux : aucun test
ne lance de processus reel, n'attend, ni ne touche `vclient`/`vcontrold`.
"""

from __future__ import annotations

import subprocess

import pytest

from boilerack.adapters.process_runner import (
    ProcessResult,
    ProcessRunner,
    SubprocessRunner,
)


class _FakeCompleted:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _capturing_runner(record, *, completed=None, raises=None):
    def _run(args, **kwargs):
        record["args"] = args
        record["kwargs"] = kwargs
        if raises is not None:
            raise raises
        return completed if completed is not None else _FakeCompleted(0, b"ok\n")
    return _run


def test_est_conforme_au_protocole() -> None:
    assert isinstance(SubprocessRunner(), ProcessRunner)


def test_succes_renvoie_octets_bruts() -> None:
    rec: dict = {}
    runner = SubprocessRunner(
        runner=_capturing_runner(rec, completed=_FakeCompleted(0, b"21.5\n", b""))
    )
    res = runner.run(["/usr/bin/vclient", "-c", "getX"], timeout=5.0)
    assert isinstance(res, ProcessResult)
    assert res.returncode == 0
    assert res.stdout == b"21.5\n"
    assert res.stderr == b""
    assert res.timed_out is False
    assert res.launch_failed is False


def test_shell_false_et_timeout_transmis() -> None:
    rec: dict = {}
    runner = SubprocessRunner(runner=_capturing_runner(rec))
    runner.run(["/bin/echo", "x"], timeout=3.5)
    # Frontiere : jamais shell=True, args reste une liste, timeout transmis tel quel.
    assert rec["kwargs"]["shell"] is False
    assert rec["kwargs"]["timeout"] == 3.5
    assert rec["kwargs"]["capture_output"] is True
    assert rec["kwargs"]["check"] is False
    assert rec["args"] == ["/bin/echo", "x"]


def test_env_controle_transmis() -> None:
    rec: dict = {}
    runner = SubprocessRunner(runner=_capturing_runner(rec))
    runner.run(["/bin/echo"], timeout=1.0, env={"PATH": "/bin"})
    assert rec["kwargs"]["env"] == {"PATH": "/bin"}


def test_code_retour_non_nul_est_expose_tel_quel() -> None:
    rec: dict = {}
    runner = SubprocessRunner(
        runner=_capturing_runner(rec, completed=_FakeCompleted(3, b"", b"boom\n"))
    )
    res = runner.run(["/x"], timeout=1.0)
    # Le runner ne CLASSE rien : il rend compte. rc != 0 est expose brut.
    assert res.returncode == 3
    assert res.stderr == b"boom\n"
    assert res.launch_failed is False
    assert res.timed_out is False


def test_timeout_est_signale_sans_returncode() -> None:
    rec: dict = {}
    runner = SubprocessRunner(
        runner=_capturing_runner(
            rec,
            raises=subprocess.TimeoutExpired(
                cmd=["/x"], timeout=1.0, output=b"partiel", stderr=b""
            ),
        )
    )
    res = runner.run(["/x"], timeout=1.0)
    assert res.timed_out is True
    assert res.returncode is None
    assert res.launch_failed is False
    assert res.stdout == b"partiel"


@pytest.mark.parametrize("exc", [FileNotFoundError(), PermissionError(), OSError()])
def test_echec_de_lancement_signale_launch_failed(exc) -> None:
    rec: dict = {}
    runner = SubprocessRunner(runner=_capturing_runner(rec, raises=exc))
    res = runner.run(["/introuvable"], timeout=1.0)
    assert res.launch_failed is True
    assert res.returncode is None
    assert res.timed_out is False
    # Diagnostic = NOM de classe uniquement, aucun message/chemin/secret.
    assert res.launch_error == type(exc).__name__


@pytest.mark.parametrize(
    "args,timeout",
    [
        ([], 1.0),
        (["/x"], 0),
        (["/x"], -1.0),
        (["/x"], float("inf")),
        (["/x"], float("nan")),
        ([1, 2], 1.0),
    ],
)
def test_arguments_invalides_refuses(args, timeout) -> None:
    runner = SubprocessRunner(runner=lambda *a, **k: _FakeCompleted(0))
    with pytest.raises(ValueError):
        runner.run(args, timeout=timeout)


def test_ne_lance_jamais_de_processus_reel_par_defaut() -> None:
    # Preuve structurelle : sans injection, le runner par defaut est subprocess.run,
    # mais on ne l'invoque jamais avec une vraie commande dans la suite.
    runner = SubprocessRunner()
    assert runner._runner is subprocess.run
