"""Frontiere de transport vers un demon `vcontrold`.

Interface ETROITE : uniquement ce dont le futur bridge aura besoin pour lire et
ecrire une valeur, et pour distinguer les issues possibles d'une operation.

Le transport ignore deliberement MQTT, les ACK, le profil de chaudiere, Home
Assistant et toute politique de retry. Il ne decide de rien : il rend compte.

Les issues sont TYPEES par un `enum` et portees par des `dataclass` de resultat.
Aucune cause n'est absorbee dans un `None` : `None` sur `value` signifie
seulement « pas de valeur numerique », et le pourquoi est toujours dans `status`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable


class TransportStatus(Enum):
    """Issue d'une operation de transport, independante de tout metier."""

    OK = "ok"
    """Lecture ou ecriture reussie au niveau transport."""

    DAEMON_UNREACHABLE = "daemon_unreachable"
    """Le demon `vcontrold` n'est pas joignable."""

    UNKNOWN_COMMAND = "unknown_command"
    """La commande est inconnue du demon ou refusee par lui."""

    TIMEOUT = "timeout"
    """Aucune reponse dans le delai imparti."""

    UNUSABLE_OUTPUT = "unusable_output"
    """Le demon a repondu, mais la sortie est inexploitable (vide, non numerique)."""

    TRANSPORT_ERROR = "transport_error"
    """Toute autre erreur de transport, non couverte par les cas ci-dessus."""


@dataclass(frozen=True)
class ReadResult:
    """Resultat d'une lecture.

    Invariant DURCI (C3) : le statut et la valeur ne peuvent jamais se
    contredire.

    - `status is OK` implique une `value` presente ET finie (jamais `None`,
      jamais `NaN`, jamais infinie) : un succes de transport porte toujours un
      nombre exploitable ;
    - `status is not OK` implique `value is None` : aucune valeur numerique
      n'accompagne un echec, et le « pourquoi » reste dans `status`.

    `raw` porte la sortie brute du transport quand elle existe, y compris dans
    le cas `UNUSABLE_OUTPUT`, pour permettre un diagnostic.
    """

    status: TransportStatus
    value: float | None = None
    raw: str | None = None
    detail: str = ""

    def __post_init__(self) -> None:
        if self.status is TransportStatus.OK:
            if self.value is None:
                raise ValueError("ReadResult OK exige une value non nulle.")
            if not math.isfinite(self.value):
                raise ValueError(
                    f"ReadResult OK exige une value finie : {self.value!r}"
                )
        elif self.value is not None:
            raise ValueError(
                f"ReadResult non-OK ({self.status.value}) exige value is None, "
                f"recu {self.value!r}"
            )

    @property
    def ok(self) -> bool:
        return self.status is TransportStatus.OK


@dataclass(frozen=True)
class WriteObservation:
    """Signature BRUTE d'une invocation d'ecriture, rendue a l'appelant.

    POURQUOI CE PORTEUR EXISTE
        `g2-observabilite-preuve.md` rouvre l'obligation 11 de W4-A §18. W4-B
        avait tranche « `detail` suffit » parce que le seul besoin de sortie
        INTEGRALE, la capture de W4-C, etait satisfait HORS du code : l'exploitant
        lancait `vclient` lui-meme. `G.2` inverse ce modele — c'est Boilerack qui
        lance —, et l'exploitant n'a plus acces aux octets. Le besoin est donc
        revenu, avec un consommateur : `G.2` §16, item 4.

    CE N'EST PAS UNE ENTREE DE DECISION
        Le coeur transactionnel MUST NOT fonder le moindre comportement sur cette
        observation, et MUST NOT modifier la signature de `VClient.write` pour la
        recuperer. C'est la forme exacte de la clause W1 §11.4 sur `submit`. La
        confirmation metier reste une RELECTURE SEPAREE, et W4-C §16.4 interdit
        deja d'interpreter le champ `value` d'une reponse d'ecriture.

    A QUI ELLE EST REMISE — OBS §5.1, amende
        L'observation est rendue a l'APPELANT IMMEDIAT et, SI ET SEULEMENT SI un
        puits de preuve est injecte au titre de l'exception bornee de W4-A §17,
        REMISE A CE PUITS. A personne d'autre.

        Sans puits injecte — cas de toute exploitation ordinaire — elle voyage
        dans la valeur de retour et disparait avec elle.

    NI RETENTION, NI PUBLICATION
        Personne ne la conserve, PAS MEME LE PUITS : W4-A §14 pose l'adaptateur
        « sans etat au-dela de sa configuration », et le puits ecrit et oublie.
        Elle n'est publiee sur AUCUN topic MQTT, sous aucune forme, ni entiere
        ni extraite. Elle ne cree ni metrique ni compteur.

    FICHIER : SEULEMENT SOUS L'EXCEPTION BORNEE
        W4-A §17 interdit a l'adaptateur de creer un systeme d'observabilite
        nouveau, fichier compris. Son EXCEPTION BORNEE admet qu'un puits injecte
        depose cette observation dans les fichiers de preuve d'une campagne :
        opt-in, inerte par defaut, hors de l'adaptateur, ecriture seulement, et
        sans effet sur un verdict. HORS CAMPAGNE, l'interdiction demeure
        entiere : sans puits, aucun fichier n'existe.

    JAMAIS JOURNALISEE INTEGRALEMENT
        W4-A §17 n'admet `stdout` et `stderr` au journal que BORNES. `detail`
        continue de les borner ; ce porteur ne passe pas par le journal.

    - `args` : la ligne d'invocation REELLE, telle qu'executee ;
    - `stdout` / `stderr` : octets bruts, INTEGRAUX et SEPARES, jamais fusionnes ;
    - `returncode` : code retour, ou `None` si le processus n'a pas conclu ;
    - `duration_s` : duree mesuree autour de la SEULE invocation, par
      `clock.monotonic()`. INDICATIVE : W4-C §10 maintient sa reserve d'horloge.
    """

    args: tuple[str, ...]
    stdout: bytes
    stderr: bytes
    returncode: int | None
    duration_s: float


@runtime_checkable
class EvidenceSink(Protocol):
    """Puits de PREUVE : recoit la signature brute d'une ecriture, et l'oublie.

    Port de sortie de l'adaptateur d'ecriture, au titre de l'exception bornee
    de W4-A §17. Il est TOUJOURS optionnel : sans puits injecte, aucun appel
    n'a lieu et aucun fichier n'existe.

    CE N'EST PAS UN CHEMIN DE DECISION
        `record` ne rend rien, et l'adaptateur n'attend rien de lui. Aucun
        verdict, aucun `ACK`, aucune duree mesuree ne depend de ce qu'il fait
        ni du temps qu'il y met.

    IL PEUT LEVER
        L'adaptateur intercepte et journalise borne. Un puits en echec ne
        change aucune issue : l'absence de fichier vaut constat.

    CE QU'IL NE FAIT PAS
        Il ne publie sur aucun topic, ne retient aucune observation, et n'est
        jamais cable sur le chemin de LECTURE.
    """

    def record(self, observation: WriteObservation) -> None:
        """Consigne `observation`. Ne rend rien, et rien n'attend son retour."""


@dataclass(frozen=True)
class WriteResult:
    """Resultat d'une ecriture au niveau transport.

    « Ecriture reussie au niveau transport » signifie que le demon a accepte la
    commande, PAS que la chaudiere a confirme la valeur par relecture : cette
    confirmation releve du coeur, en C3, pas du transport.

    `observation` porte la signature brute de l'invocation. Voir
    `WriteObservation` : ce champ est une TRACE, jamais une entree de decision.
    La taxonomie `TransportStatus` n'est pas touchee — obligation 21 de
    W4-A §18.

    QUAND ELLE EST PRESENTE, ET QUAND ELLE NE L'EST PAS
        Le critere est l'INVOCATION TENTEE, non le processus effectivement ne.

        - **presente** des lors que le lanceur a ete appele — y compris quand le
          lancement a ECHOUE (`launch_failed`), cas ou aucun processus n'existe
          mais ou la tentative, elle, a bien eu lieu : la ligne d'arguments et la
          duree en temoignent, et c'est precisement ce qu'une preuve doit
          consigner ;
        - **`None`** dans le seul cas ou le lanceur n'a JAMAIS ete appele : la
          ligne d'invocation n'a pas pu etre fabriquee (`UnrenderableValue`, ou
          une entree que la fabrique n'a pas su qualifier). Il n'y a alors rien a
          observer, et on ne l'invente pas.

        Un nom de commande invalide leve avant tout : il ne produit aucun
        `WriteResult`, donc aucune observation.
    """

    status: TransportStatus
    detail: str = ""
    observation: WriteObservation | None = None

    @property
    def ok(self) -> bool:
        return self.status is TransportStatus.OK


@runtime_checkable
class VClient(Protocol):
    """Transport minimal : lire une valeur, ecrire une valeur.

    Les noms de commandes sont des chaines opaques pour le transport. Aucun
    datapoint de production n'est cable ici.
    """

    def read(self, command: str) -> ReadResult:
        ...

    def write(self, command: str, value: float) -> WriteResult:
        ...
