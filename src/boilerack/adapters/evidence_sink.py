"""Puits de preuve de campagne — depot sur disque, HORS de l'adaptateur.

POURQUOI CE MODULE EXISTE, ET HORS DE L'ADAPTATEUR
    `g2-sortie-preuve-transport.md` §5.1, clause 2 : « L'adaptateur n'ecrit
    rien. `FileEvidenceSink` vit HORS de l'adaptateur, dans son propre module,
    cable a la composition. » L'adaptateur d'ecriture reste synchrone et sans
    etat au-dela de sa configuration (W4-A §14) ; toute l'entree-sortie de
    capture est ici.

CE QU'IL DEPOSE, ET RIEN D'AUTRE
    Trois fichiers par invocation d'ecriture, a la forme de W4-C §10 :

        <NN>-ecriture.out    octets BRUTS et INTEGRAUX de `stdout`
        <NN>-ecriture.err    octets BRUTS et INTEGRAUX de `stderr`
        <NN>-ecriture.meta   ligne d'invocation, code retour, duree, horodatage

    `.out` et `.err` ne sont JAMAIS fusionnes : W4-A §18, obligation 5.

L'EXCEPTION QUI L'AUTORISE
    W4-A §17 interdit a l'adaptateur de creer un systeme d'observabilite
    nouveau, « ni metrique, ni compteur, ni fichier ». Le present depot n'existe
    qu'au titre de l'exception bornee qui y a ete portee : opt-in, inerte par
    defaut, bornee a la duree d'une campagne, hors de l'adaptateur, sans
    metrique ni compteur, ecriture seulement, et sans effet sur un verdict.

CE QU'IL NE FAIT PAS
    Il ne publie sur AUCUN topic MQTT. Il ne cree ni metrique ni compteur
    d'observabilite. Il ne retient AUCUNE observation : il ecrit et oublie.
    Il n'est jamais cable sur le chemin de LECTURE.

LE SEUL ETAT, ET POURQUOI IL EST ADMIS
    Un compteur monotone, borne a la campagne, qui numerote les captures. Il ne
    contredit pas la clause de non-retention : celle-ci porte sur
    l'OBSERVATION, non sur un rang. Le numero n'est JAMAIS derive d'une horloge
    — W4-C §10 maintient une reserve d'horloge, et un nom derive d'une horloge
    qui a bouge produirait un ordre faux, ou une collision.
"""

from __future__ import annotations

from pathlib import Path

from boilerack.clock import Clock
from boilerack.transport.vclient import WriteObservation

__all__ = ["FileEvidenceSink"]


class FileEvidenceSink:
    """Depose la signature brute d'une ecriture dans un repertoire d'atelier.

    `repertoire` DOIT etre l'atelier de `EI-1`..`EI-4`, hors de tout depot
    versionne — `g2-sortie-preuve-transport.md` §6.2. Ce module ne le verifie
    pas : la verification est un acte de campagne, consigne par l'exploitant,
    et l'inventer ici transformerait une preuve en controle automatique.

    `horloge` ne sert qu'a l'horodatage porte dans `.meta`, ou il est une
    DONNEE. Elle ne participe a aucun nom de fichier.
    """

    def __init__(self, repertoire: str | Path, *, clock: Clock) -> None:
        self._repertoire = Path(repertoire)
        self._clock = clock
        self._rang = 0

    def record(self, observation: WriteObservation) -> None:
        """Depose les trois fichiers de `observation`. Ne rend rien.

        Cette methode PEUT lever : l'appelant — `VClientCli.write` — intercepte
        et journalise borne, de sorte qu'aucun verdict n'en depende. Ce contrat
        est celui de `g2-sortie-preuve-transport.md` §5.1, clause 3, et il vaut
        mieux qu'un echec silencieux ici : l'absence de fichier vaut constat.
        """
        self._rang += 1
        prefixe = self._repertoire / f"{self._rang:02d}-ecriture"

        self._repertoire.mkdir(parents=True, exist_ok=True)
        # Octets BRUTS, en binaire : aucun decodage, aucune substitution, aucune
        # normalisation de fin de ligne. Ce sont les octets que le transport a
        # rendus, et la preuve porte sur eux.
        #
        # CREATION EXCLUSIVE — « x », jamais « w ». Une capture existante n'est
        # JAMAIS ecrasee : sur un atelier deja peuple, le depot ECHOUE au lieu
        # de detruire une preuve. L'echec remonte a l'adaptateur, qui
        # l'intercepte et le journalise borne ; aucun verdict n'en depend, et
        # l'absence du fichier vaut constat.
        self._ecrire_exclusif(prefixe.with_suffix(".out"), observation.stdout)
        self._ecrire_exclusif(prefixe.with_suffix(".err"), observation.stderr)

        horodatage = self._clock.now().isoformat().replace("+00:00", "Z")
        # La ligne d'invocation est ecrite VERBATIM, argument par argument, sans
        # citation ni echappement : la reconstituer serait l'interpreter.
        lignes = [
            f"rang: {self._rang}",
            f"horodatage: {horodatage}",
            f"returncode: {observation.returncode}",
            f"duration_s: {observation.duration_s}",
            "args:",
            *(f"  {argument}" for argument in observation.args),
            "",
        ]
        self._ecrire_exclusif(
            prefixe.with_suffix(".meta"), "\n".join(lignes).encode("utf-8")
        )

    @staticmethod
    def _ecrire_exclusif(chemin: Path, contenu: bytes) -> None:
        """Cree le fichier, ou leve. Ne remplace JAMAIS un fichier existant.

        `"xb"` leve `FileExistsError` si la cible existe deja. C'est le
        comportement voulu : une preuve de campagne qui en ecraserait une autre
        serait pire qu'absente, puisqu'elle serait indiscernable d'une preuve
        complete.
        """
        with open(chemin, "xb") as fichier:
            fichier.write(contenu)
