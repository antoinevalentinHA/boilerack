"""Lecteur `vclient` en ligne de commande — LECTURE SEULE.

Traduit une invocation `vclient -J` en `ReadResult`, en s'appuyant
exclusivement sur :

- `ProcessRunner` et `VclientConfig`, livres en C4 ;
- les signatures reellement observees et versionnees en C5
  (`docs/design/c5-vclient-contract.md`, `tests/fixtures/vclient/`) ;
- les six valeurs actuelles de `TransportStatus`, inchangees.

ABSENCE VOLONTAIRE D'ECRITURE
    Ce composant expose `read` et **rien d'autre**. Il ne possede pas de
    methode `write` et ne satisfait donc PAS le protocole `VClient`, qui exige
    les deux. Ce n'est pas un oubli : c'est la conclusion d'une analyse du
    moteur transactionnel.

    Le moteur pose `write_invoked = True` AVANT d'appeler `write`, et traite
    tout statut ambigu ou imprevu — comme toute exception levee a partir de
    l'invocation — en « potentiellement emis », donc en tentant une relecture
    de confirmation. Une methode `write` bouchon, quelle que soit sa forme,
    conduirait donc a une relecture ; si la valeur courante de la chaudiere se
    trouvait egale a la cible, le moteur conclurait `applied` pour une ecriture
    JAMAIS TENTEE. Le seul statut qui l'eviterait est `DAEMON_UNREACHABLE`,
    qui serait un mensonge typé.

    Une methode absente est honnete ; une methode bouchon serait dangereuse.
    La conformite `VClient` attendait la caracterisation reelle de l'ecriture.

    ELLE A EU LIEU. La campagne W4-C a observe une ecriture acceptee, et W4-B en
    a tire `adapters.vclient_write.VClientCli`, qui ETEND cette classe et ajoute
    `write`. Ce lecteur-ci reste volontairement en lecture seule : le
    raisonnement ci-dessus vaut toujours pour lui, et l'ecriture est ailleurs.

Ce module ne contacte aucun systeme reel par lui-meme : il delegue au
`ProcessRunner` qu'on lui injecte.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any, Final

from boilerack.adapters.config import VclientConfig
from boilerack.adapters.process_runner import ProcessResult, ProcessRunner
from boilerack.transport.vclient import ReadResult, TransportStatus

__all__ = ["VClientCliReader", "InvalidCommandName"]


#: Unique signal d'erreur structuree reellement observe en C5. Toute autre
#: valeur non vide de `error` releve de `TRANSPORT_ERROR` : rien d'autre n'a
#: ete caracterise, et deviner serait inventer.
_UNKNOWN_COMMAND_ERROR: Final = "ERR: command unknown"

#: Nom de commande : au moins un caractere, aucun caractere de controle, et
#: aucune virgule — `-c` accepte une LISTE separee par des virgules, si bien
#: qu'une virgule permettrait de faire executer plusieurs commandes.
_CONTROL_CHARS: Final = re.compile(r"[\x00-\x1f\x7f]")


class InvalidCommandName(ValueError):
    """Nom de commande refuse avant toute invocation de processus."""


class VClientCliReader:
    """Lecteur `vclient -J`, en LECTURE SEULE.

    N'expose que `read`. Voir la docstring du module pour la raison, qui tient
    a la surete du moteur transactionnel et non a un perimetre arbitraire.
    """

    def __init__(self, config: VclientConfig, runner: ProcessRunner) -> None:
        self._config = config
        self._runner = runner

    # -- Construction d'arguments ------------------------------------------

    def build_args(self, command: str) -> list[str]:
        """Construit la ligne d'arguments, sans shell ni concatenation.

        Forme retenue, identique a celle observee en production :
            <executable> [-h <host>] [-p <port>] -J -c <command>

        `-J` (JSON long) est la seule option de sortie utilisee : C5 a etabli
        que le champ `error` y est le discriminant, et que `raw` porte la
        valeur et son unite sans analyse lexicale.
        """
        self._validate_command(command)
        args = [self._config.executable]
        if self._config.host is not None:
            args += ["-h", self._config.host]
        if self._config.port is not None:
            args += ["-p", str(self._config.port)]
        args += ["-J", "-c", command]
        return args

    @staticmethod
    def _validate_command(command: str) -> None:
        """Protection minimale, sans grammaire propre a une chaudiere.

        Le projet ne definit aucune grammaire de nom de commande : `CommandSpec`
        exige seulement une chaine non vide, et les noms sont explicitement
        « opaques pour le transport ». On se limite donc au strict necessaire
        pour qu'un nom ne puisse pas changer le sens de la ligne d'arguments.

        Aucune liste blanche de datapoints n'est definie ici : elle appartient
        au profil, pas au transport.
        """
        if not isinstance(command, str) or command == "":
            raise InvalidCommandName("le nom de commande doit etre une chaine non vide")
        if command.strip() != command:
            raise InvalidCommandName("le nom de commande ne doit pas etre entoure d'espaces")
        if _CONTROL_CHARS.search(command):
            raise InvalidCommandName("le nom de commande contient un caractere de controle")
        if "," in command:
            raise InvalidCommandName(
                "la virgule permettrait de passer plusieurs commandes a -c"
            )
        if command.startswith("-"):
            raise InvalidCommandName(
                "un nom commencant par '-' serait ambigu avec une option"
            )

    # -- Lecture ------------------------------------------------------------

    def read(self, command: str) -> ReadResult:
        """Execute une lecture et classe son issue.

        Ne leve jamais pour une issue de transport : toute cause est portee par
        `ReadResult.status`. Seul un nom de commande invalide leve
        `InvalidCommandName`, avant toute invocation de processus.
        """
        args = self.build_args(command)
        result = self._runner.run(args, timeout=self._config.read_timeout_s)
        return self._classify(command, result)

    # -- Classification -----------------------------------------------------

    def _classify(self, command: str, result: ProcessResult) -> ReadResult:
        """Ordre de decision, du plus certain au plus incertain.

        Chaque etape n'utilise que des signaux etablis en C5. Ce qui n'est pas
        prouve tombe dans un statut prudent, jamais dans `OK`.
        """
        # 1. Echec de lancement local : aucune commande n'a atteint le demon.
        #    C6 ne ratifie PAS `CLIENT_UNAVAILABLE` : on reste prudent.
        #    On s'appuie sur le drapeau typé `launch_failed` plutot que sur la
        #    chaine `launch_error`, qui vaut "" par defaut et non `None`.
        if result.launch_failed:
            return ReadResult(
                status=TransportStatus.TRANSPORT_ERROR,
                detail=f"lancement impossible ({result.launch_error or 'cause inconnue'})",
            )

        # 2. Budget de temps epuise : on ne tente PAS d'exploiter une sortie
        #    partielle comme un succes.
        if result.timed_out:
            return ReadResult(status=TransportStatus.TIMEOUT, detail="budget de temps epuise")

        # 3. Demon injoignable : signature EXACTE observee en C5. Aucune
        #    generalisation a tout code retour non nul.
        if result.returncode == 1 and result.stdout == b"" and result.stderr == b"":
            return ReadResult(
                status=TransportStatus.DAEMON_UNREACHABLE,
                detail="code retour 1, aucune sortie sur les deux flux",
            )

        # 4. Decodage STRICT et separe. Aucune substitution silencieuse.
        try:
            stdout = result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            return ReadResult(
                status=TransportStatus.UNUSABLE_OUTPUT, detail="stdout non decodable en UTF-8"
            )
        try:
            # `stderr` est decode pour le diagnostic uniquement. Il ne participe
            # JAMAIS a la classification : C5 a montre qu'un message d'erreur y
            # figure alors que `stdout` reste formellement bien forme.
            stderr = result.stderr.decode("utf-8")
        except UnicodeDecodeError:
            stderr = "<stderr non decodable>"

        # 5. Structure JSON attendue.
        objet, echec = self._extract_object(command, stdout)
        if echec is not None:
            return ReadResult(
                status=TransportStatus.UNUSABLE_OUTPUT, raw=stdout, detail=echec
            )
        assert objet is not None

        erreur = objet["error"]
        if erreur != "":
            # 6. Commande inconnue : UNIQUEMENT le signal exact observe.
            if erreur == _UNKNOWN_COMMAND_ERROR:
                return ReadResult(
                    status=TransportStatus.UNKNOWN_COMMAND,
                    raw=stdout,
                    detail=self._avec_stderr("commande inconnue", stderr),
                )
            # 7. Autre erreur structuree : aucune classification nouvelle.
            return ReadResult(
                status=TransportStatus.TRANSPORT_ERROR,
                raw=stdout,
                detail=self._avec_stderr(f"erreur structuree : {erreur}", stderr),
            )

        # 8. Succes : uniquement si la valeur est un nombre fini.
        valeur = objet["value"]
        if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
            return ReadResult(
                status=TransportStatus.UNUSABLE_OUTPUT,
                raw=stdout,
                detail=f"value non numerique ({type(valeur).__name__})",
            )
        if not math.isfinite(valeur):
            return ReadResult(
                status=TransportStatus.UNUSABLE_OUTPUT,
                raw=stdout,
                detail=f"value non finie ({valeur!r})",
            )

        # `raw` conserve la sortie observee, sans reparsing de l'unite.
        return ReadResult(status=TransportStatus.OK, value=float(valeur), raw=stdout)

    # -- Extraction structuree ---------------------------------------------

    @staticmethod
    def _extract_object(command: str, stdout: str) -> tuple[dict[str, Any] | None, str | None]:
        """Rend l'objet utile, ou la raison pour laquelle la sortie est inexploitable.

        Toute ambiguite de structure est un echec : on n'accepte jamais
        silencieusement le premier objet d'une reponse a plusieurs elements.
        """
        try:
            charge = json.loads(stdout)
        except (json.JSONDecodeError, ValueError):
            return None, "JSON invalide"

        if not isinstance(charge, list):
            return None, f"racine JSON non liste ({type(charge).__name__})"
        if len(charge) == 0:
            return None, "liste JSON vide"
        if len(charge) > 1:
            return None, f"reponse ambigue : {len(charge)} objets pour une lecture unique"

        objet = charge[0]
        if not isinstance(objet, dict):
            return None, f"element JSON non objet ({type(objet).__name__})"

        manquants = [c for c in ("command", "value", "raw", "error") if c not in objet]
        if manquants:
            return None, f"champs manquants : {', '.join(manquants)}"

        if not isinstance(objet["command"], str):
            return None, "champ command non textuel"
        if objet["command"] != command:
            return None, f"commande inattendue : {objet['command']!r} au lieu de {command!r}"
        if not isinstance(objet["error"], str):
            return None, "champ error non textuel"

        return objet, None

    @staticmethod
    def _avec_stderr(message: str, stderr: str) -> str:
        """Joint `stderr` au diagnostic, sans jamais lui faire porter le verdict."""
        extrait = stderr.strip()
        if not extrait:
            return message
        return f"{message} | stderr: {extrait[:200]}"
