"""Adaptateur `vclient` d'ECRITURE (lot W4-B).

Complete `VClientCliReader` : le lecteur n'expose que `read` et ne satisfait donc
pas `VClient`, qui exige les deux. `VClientCli`, ici, ajoute `write` et devient
le seul type du depot a satisfaire ce Protocol.

POURQUOI CE MODULE ET PAS `vclient_cli.py`
    Le lecteur est un composant audite et stable, dont la docstring explique en
    detail pourquoi il n'ecrit pas. L'ecriture est un ajout d'un autre lot, fonde
    sur d'autres faits — la campagne terrain W4-C. Les separer garde chaque
    raisonnement lisible et laisse le lecteur intact.

DEUX PARTIES DE NATURE DIFFERENTE — W4-A §8.1
    A. **Mecanique de transport** — validation du nom, budget, lancement,
       capture, decodage, classification, absence de retry. Ne depend pas du
       terrain : c'est `VClientCli`.
    B. **Fabrication de l'invocation** — ligne d'arguments et representation
       textuelle de la valeur. Depend du terrain : c'est `WriteInvocation`, un
       collaborateur INJECTE, substituable par un double.

    W4-A §8.1 exigeait que B ne soit pas « resolue en production **avant
    W4-C** », et l'obligation 20 de §18 interdisait de livrer une fabrique
    resolue « **avant W4-C** ». **W4-C a eu lieu** : ces deux conditions sont
    echues, et `VclientWriteInvocation` est la resolution que la campagne
    autorise. B reste neanmoins injectee, sans valeur par defaut — livrer une
    piece n'est pas la brancher.

CE QUE CET ADAPTATEUR NE FAIT PAS
    Il ne decide jamais qu'une valeur a ete APPLIQUEE. W4-A §6 : succes local
    n'est pas ecriture appliquee. La confirmation est une relecture, et elle
    appartient au coeur (C3). Cet adaptateur ne relit rien, ne reessaie rien, ne
    valide aucune borne metier, ne connait ni MQTT ni profil.

Ce module ne contacte aucun systeme reel : il delegue au `ProcessRunner` qu'on
lui injecte, comme le lecteur.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Final, Protocol, runtime_checkable

from boilerack.adapters.config import VclientConfig
from boilerack.adapters.process_runner import ProcessResult, ProcessRunner
from boilerack.adapters.vclient_cli import VClientCliReader
from boilerack.transport.vclient import TransportStatus, WriteResult

__all__ = [
    "Invocation",
    "UnrenderableValue",
    "VClientCli",
    "VclientWriteInvocation",
    "WriteInvocation",
]


#: Jeton EXACT observe dans le champ `raw` d'une ecriture acceptee, lors de la
#: campagne W4-C du 22 aout 2026 (`w4c-write-capture-protocol.md` §16.3). W4-A
#: §9.3 borne la levee de `OK` a cette chaine et a elle seule : « `raw` portant
#: une AUTRE chaine — quelle qu'elle soit, et quelque "positive" qu'elle
#: paraisse — n'est PAS cette signature ».
_RAW_SUCCES: Final = "OK"

#: Longueur maximale d'un extrait de diagnostic place dans `detail`. W4-A §17
#: autorise un extrait BORNE, jamais la sortie entiere.
_EXTRAIT_MAX: Final = 200


class UnrenderableValue(ValueError):
    """La valeur ne possede aucune representation textuelle caracterisee.

    Levee par la partie B, jamais propagee hors de `write()` : l'adaptateur la
    convertit en issue de transport, conformement a W4-A §7.2 qui interdit de
    lever pour une issue de transport.
    """


@dataclass(frozen=True)
class Invocation:
    """Ce que la partie B remet a la partie A.

    - `args` : la ligne d'arguments complete, deja construite, sans shell ;
    - `echo` : la chaine que la reponse est censee renvoyer dans son champ
      `command`. La partie A ne peut pas la deduire : elle ne connait pas la
      forme du fil, qui appartient a B. B la declare donc explicitement plutot
      que A ne la devine.

    `echo` vide signifie « je ne declare aucun echo » : la verification est alors
    omise, sans etre remplacee par une supposition.
    """

    args: list[str]
    echo: str = ""


@runtime_checkable
class WriteInvocation(Protocol):
    """Partie B de W4-A §8.1 — fabrication de l'invocation d'ecriture.

    Rend une `Invocation` complete, sans shell ni concatenation. Leve
    `UnrenderableValue` si la valeur n'a pas de forme textuelle caracterisee :
    inventer une forme reviendrait a repondre a l'inconnue I-8, que W4-C n'a pas
    levee.
    """

    def build(self, command: str, value: float) -> Invocation:
        ...


class VclientWriteInvocation:
    """Fabrique RESOLUE, telle que la campagne W4-C l'a caracterisee.

    Forme observee le 22 aout 2026, et la seule :

        <executable> [-h <host>] [-p <port>] -J -c "<commande> <valeur>"

    L'argument de `-c` porte la commande ET sa valeur, en un seul mot du shell —
    c'est ce que `03-ecriture-json.meta` a consigne, et c'est aussi ce que le
    champ `command` de la reponse renvoie en echo.

    Hote, port et executable viennent de `VclientConfig`, comme pour la lecture.
    Aucune constante de site n'est ecrite ici.
    """

    def __init__(self, config: VclientConfig) -> None:
        self._config = config

    def build(self, command: str, value: float) -> Invocation:
        self._refuser_espace_interne(command)
        argument = f"{command} {self.render(value)}"
        # Ordre repris de la ligne REELLEMENT executee le 22 aout 2026, consignee
        # dans `03-ecriture-json.meta` : `-J` precede `-h` et `-p`. Le lecteur
        # place `-J` en dernier ; les deux ordres sont equivalents pour un
        # analyseur d'options, mais seul celui-ci a ete observe en ECRITURE, et
        # c'est le seul motif de ce choix.
        args = [self._config.executable, "-J"]
        if self._config.host is not None:
            args += ["-h", self._config.host]
        if self._config.port is not None:
            args += ["-p", str(self._config.port)]
        args += ["-c", argument]
        # L'echo attendu est l'argument de `-c` lui-meme : c'est ce que W4-C a
        # observe dans le champ `command` de la reponse.
        return Invocation(args=args, echo=argument)

    @staticmethod
    def _refuser_espace_interne(command: str) -> None:
        """Refuse un nom porteur d'espacement INTERNE — garde propre a l'ecriture.

        Le lecteur autorise les espaces internes, et il le peut : son `-c` porte
        le nom SEUL, si bien qu'un nom fantaisiste ne produit qu'une commande
        inconnue. Ici, `-c` porte `"<commande> <valeur>"` : un espace interne y
        insere un mot supplementaire, et `setNiveauM1 99` avec la valeur `2`
        emettrait `setNiveauM1 99 2`.

        La reponse serait probablement rejetee — mais l'emission fautive aurait
        deja eu lieu, et c'est precisement ce qu'il faut empecher.

        Cette garde COMPLETE la validation heritee, elle ne la reecrit pas :
        `VClientCliReader._validate_command` reste inchange, les besoins de
        l'ecriture n'ayant pas a elargir les regles de la lecture.
        """
        if any(caractere.isspace() for caractere in command):
            raise UnrenderableValue(
                "un nom de commande porteur d'espacement interne inserait un mot "
                f"supplementaire dans l'argument de -c : {command!r}"
            )

    @staticmethod
    def render(value: float) -> str:
        """Rend la valeur sous sa forme ENTIERE, seule forme caracterisee.

        W4-C n'a observe qu'une ecriture, `setNiveauM1 2`, sur un datapoint dont
        le contrat est `int` a pas 1 : la forme entiere est donc la seule dont on
        sache qu'elle est acceptee. La representation d'un non-entier releve de
        l'inconnue **I-8**, que la campagne a deliberement ecartee — elle n'a
        emis qu'un entier exact, precisement pour ne pas avoir a l'interpreter.

        Le rendu est DETERMINISTE et insensible a la locale (W4-A §15) : deux
        appels de meme valeur produisent le meme texte.

        `UnrenderableValue` est levee plutot qu'un format devine. Refuser est un
        fait ; inventer serait une hypothese.
        """
        # `bool` est une sous-classe de `int` : l'ecarter explicitement evite que
        # `True` ne se rende silencieusement en `"1"`.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise UnrenderableValue(
                f"valeur non numerique ({type(value).__name__}) : {value!r}"
            )
        nombre = float(value)
        if not math.isfinite(nombre):
            raise UnrenderableValue(f"valeur non finie : {value!r}")
        if not nombre.is_integer():
            raise UnrenderableValue(
                f"seule la forme entiere est caracterisee (W4-C) : {value!r}"
            )
        return str(int(nombre))


class VClientCli(VClientCliReader):
    """Adaptateur `vclient` COMPLET : lecture heritee, ecriture ajoutee.

    Seul type du depot a satisfaire le Protocol `VClient`. Il herite du lecteur
    plutot que de le dupliquer : W4-A §8 exige que le nom de commande soit valide
    « selon les memes regles que `VClientCliReader._validate_command` », et
    heriter rend cette identite litterale au lieu de la recopier.

    LIVRER N'EST PAS BRANCHER
        Aucun module de production ne construit cette classe. La voie
        transactionnelle reste fermee parce que rien ne la compose — et non plus
        parce qu'une dependance manquerait. C'est W4-E qui composera, pas W4-B.
    """

    def __init__(
        self,
        config: VclientConfig,
        runner: ProcessRunner,
        *,
        invocation: WriteInvocation,
    ) -> None:
        super().__init__(config, runner)
        self._invocation = invocation

    # -- Ecriture ------------------------------------------------------------

    def write(self, command: str, value: float) -> WriteResult:
        """Execute AU PLUS UNE invocation d'ecriture, et classe son issue.

        Ne leve jamais pour une issue de transport (W4-A §7.2) : toute cause est
        portee par `WriteResult.status`. Seul un nom de commande invalide leve
        `InvalidCommandName`, avant toute invocation de processus, exactement
        comme `read()`.

        Aucun reessai, sous aucune forme (W4-A §13) : un echec est une issue, pas
        une invitation a recommencer.
        """
        self._validate_command(command)
        try:
            invocation = self._invocation.build(command, value)
        except UnrenderableValue as exc:
            # Aucun processus n'a ete lance. Le repli est celui de la ligne 1 de
            # W4-A §9 — meme raisonnement que `launch_failed` : rien ne prouve la
            # non-emission au sens de la taxonomie active, donc on reste prudent
            # et le coeur tranchera par relecture.
            return WriteResult(
                status=TransportStatus.TRANSPORT_ERROR,
                detail=f"invocation non fabricable ({self._borner(str(exc))})",
            )
        except (TypeError, ValueError) as exc:
            # Une entree que la fabrique n'a pas su qualifier — type inattendu,
            # conversion refusee. La frontiere reste ETROITE : seules ces deux
            # familles sont absorbees, et pas `Exception`. Une erreur de
            # programmation dans une fabrique substituee doit remonter, pas se
            # deguiser en issue de transport.
            return WriteResult(
                status=TransportStatus.TRANSPORT_ERROR,
                detail=(
                    f"invocation non fabricable ({type(exc).__name__}: "
                    f"{self._borner(str(exc))})"
                ),
            )

        result = self._runner.run(
            invocation.args, timeout=self._config.write_timeout_s
        )
        return self._classify_write(invocation.echo, result)

    # -- Classification -------------------------------------------------------

    def _classify_write(self, echo_attendu: str, result: ProcessResult) -> WriteResult:
        """Table FERMEE de W4-A §9, augmentee de la seule levee de §9.3.

        Ordre du plus certain au plus incertain, repris du chemin de lecture.
        Deux statuts n'apparaissent nulle part et c'est deliberé :
        `DAEMON_UNREACHABLE` (§11.6) et `UNKNOWN_COMMAND` (§12.3) restent
        interdits — aucune signature d'echec d'ecriture n'a jamais ete observee,
        et une absence d'echec n'est pas la connaissance d'une signature d'echec.
        """
        # 1. Echec de lancement local : aucune commande n'a atteint le demon.
        if result.launch_failed:
            return WriteResult(
                status=TransportStatus.TRANSPORT_ERROR,
                detail=f"lancement impossible ({result.launch_error or 'cause inconnue'})",
            )

        # 2. Budget epuise. W4-A §10.1 : n'affirme RIEN sur l'emission.
        if result.timed_out:
            return WriteResult(
                status=TransportStatus.TIMEOUT, detail="budget de temps epuise"
            )

        # 3. Decodage STRICT et separe, sans substitution silencieuse.
        try:
            stdout = result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            return WriteResult(
                status=TransportStatus.UNUSABLE_OUTPUT,
                detail="stdout non decodable en UTF-8",
            )
        try:
            stderr_texte = result.stderr.decode("utf-8")
        except UnicodeDecodeError:
            stderr_texte = "<stderr non decodable>"

        # 4. Structure. Un echo qui ne correspond pas est une sortie
        #    inexploitable, pas un echec typé : on ne saurait pas de quelle
        #    invocation elle parle.
        objet, echec = self._extract_write_object(echo_attendu, stdout)
        if echec is not None:
            return WriteResult(
                status=TransportStatus.UNUSABLE_OUTPUT,
                detail=self._diagnostic(echec, stdout, stderr_texte),
            )
        assert objet is not None

        # 5. LA signature de succes, litteralement (W4-A §9.3). Quatre conditions
        #    conjointes, et rien d'autre.
        #
        #    `value` n'en fait PAS partie, alors meme que §9.3 le mentionne comme
        #    observe : la clause qui suit sa mention interdit d'en « deriver quoi
        #    que ce soit ». Le consulter — fut-ce pour exiger `0.0` — serait en
        #    deriver quelque chose. Il est donc ignore, sciemment.
        if (
            result.returncode == 0
            and result.stderr == b""
            and objet["error"] == ""
            and objet["raw"] == _RAW_SUCCES
        ):
            return WriteResult(
                status=TransportStatus.OK,
                detail="signature de succes local caracterisee par W4-C",
            )

        # 6. Tout le reste (W4-A §9, ligne 5), y compris un code retour nul.
        #    Un `error` non vide n'est pas classe : la seule erreur structuree
        #    caracterisee l'a ete en LECTURE, et §12.3 interdit de la transposer.
        return WriteResult(
            status=TransportStatus.TRANSPORT_ERROR,
            detail=self._diagnostic(
                f"signature non caracterisee (rc={result.returncode}, "
                f"raw={self._borner(repr(objet['raw']))}, "
                f"error={self._borner(repr(objet['error']))})",
                stdout,
                stderr_texte,
            ),
        )

    # -- Extraction structuree -------------------------------------------------

    @staticmethod
    def _extract_write_object(
        echo_attendu: str, stdout: str
    ) -> tuple[dict[str, Any] | None, str | None]:
        """Rend l'objet utile, ou la raison pour laquelle la sortie est inexploitable.

        Meme exigence de structure que le chemin de lecture : une liste d'un seul
        objet, les quatre clefs presentes, `command` et `error` textuels.

        UNE DIFFERENCE, ETABLIE PAR W4-C
            En lecture, `command` renvoie le nom seul. En ECRITURE, il renvoie la
            commande ET son argument — `"setNiveauM1 2"`. L'echo attendu est donc
            l'invocation complete, pas le nom.
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
            return None, f"reponse ambigue : {len(charge)} objets pour une ecriture unique"

        objet = charge[0]
        if not isinstance(objet, dict):
            return None, f"element JSON non objet ({type(objet).__name__})"

        manquants = [c for c in ("command", "value", "raw", "error") if c not in objet]
        if manquants:
            return None, f"champs manquants : {', '.join(manquants)}"

        if not isinstance(objet["command"], str):
            return None, "champ command non textuel"
        if echo_attendu and objet["command"] != echo_attendu:
            return None, (
                f"echo inattendu : {objet['command']!r} au lieu de {echo_attendu!r}"
            )
        if not isinstance(objet["error"], str):
            return None, "champ error non textuel"

        # `value` doit etre NUMERIQUE. Ce n'est pas une lecture de sa grandeur :
        # la signature caracterisee porte un nombre, et une chaine, `None`, une
        # liste ou un objet a cette place decrivent une reponse d'une autre forme
        # que celle qui a ete observee. `bool` est ecarte explicitement, etant
        # une sous-classe de `int`.
        #
        # La grandeur, elle, reste ignoree — voir la classification.
        valeur = objet["value"]
        if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
            return None, f"champ value non numerique ({type(valeur).__name__})"

        return objet, None

    # -- Diagnostic -------------------------------------------------------------

    @staticmethod
    def _diagnostic(message: str, stdout: str, stderr: str) -> str:
        """Assemble un diagnostic BORNE dans `detail`.

        ARBITRAGE DE W4-A §7.3, OBLIGATION 11 — `WriteResult` ne porte pas de
        champ `raw`, contrairement a `ReadResult`. W4-A demandait de trancher :
        soit `detail` suffit, soit W4-B propose un champ.

        **`detail` suffit, et aucun champ n'est ajoute.** Le seul besoin qui
        exigeait la sortie INTEGRALE d'une ecriture etait la capture de W4-C —
        or W4-C a eu lieu, et l'a capturee hors du code, dans des fichiers
        dedies. Ce qui reste utile a l'execution est un diagnostic, et un
        diagnostic se borne. Ajouter un champ a la taxonomie de transport pour un
        besoin desormais satisfait ailleurs serait un elargissement sans
        consommateur — et l'obligation 21 interdit par ailleurs a W4-B de
        modifier la taxonomie.
        """
        morceaux = [message]
        extrait_out = stdout.strip()
        if extrait_out:
            morceaux.append(f"stdout: {VClientCli._borner(extrait_out)}")
        extrait_err = stderr.strip()
        if extrait_err:
            morceaux.append(f"stderr: {VClientCli._borner(extrait_err)}")
        return " | ".join(morceaux)

    @staticmethod
    def _borner(fragment: str) -> str:
        """Tronque un fragment de diagnostic a la borne contractuelle.

        UNE SEULE politique de bornage, appliquee a TOUT fragment de provenance
        externe : les flux, mais aussi `raw` et `error`, qui viennent du demon et
        peuvent etre arbitrairement longs. Les borner separement puis les
        composer dans un message est ce qui rend `detail` reellement borne, et
        non seulement borne par endroits.
        """
        if len(fragment) <= _EXTRAIT_MAX:
            return fragment
        return fragment[:_EXTRAIT_MAX] + "…"
