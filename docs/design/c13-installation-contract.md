# C13 — Contrat d'installation et de deploiement

Document normatif. Il fixe comment passer d'un **checkout Boilerack** a un
**environnement installe et pret a etre exploite**, sans jamais demarrer
Boilerack.

C13 ne modifie **aucun comportement du programme**. Il ne redefinit ni les codes
de sortie (C10), ni les signaux (C9), ni la reconnexion (C11), ni la surface
d'exploitation (C12). Il produit l'**outil** qui construit la cible que C12 a
decrite, et l'expose a la preuve.

**C13 ne pretend a aucune qualification terrain.** Aucune machine cible n'est
touchee, aucun `systemctl` n'est execute, aucun utilisateur systeme n'est cree
par les preuves de ce lot. Ce qui est produit est un **contrat** et, au lot
suivant, un **installateur versionne** eprouve contre une racine synthetique.

---

## 1. Objet

C12 §3 a renvoye ici la question qu'il a explicitement refusee :

> « **En particulier, C12 ne livre pas l'installateur** qui cree l'environnement
> decrit en §4. Il en fixe la cible ; le produire est un chantier distinct. »

C13 est ce chantier, et seulement lui.

L'audit d'ouverture a etabli, sur pieces, qu'une seule voie d'installation existe
aujourd'hui — `pip install .` depuis un checkout, documentee au README et prouvee
par C12 — et que tout le reste est absent : creation de l'utilisateur, creation
du venv, arborescence `/etc`, pose de l'unite, reinstallation, desinstallation.
Aucun script, aucun `Makefile`, aucun paquet, aucune release, aucun tag.

C13 comble exactement ce trou.

---

## 2. Autorites et acquis

Ce que C13 **reprend sans le redefinir**, verifie dans le depot :

| # | Acquis | Origine | Preuve |
|---|---|---|---|
| B1 | Emplacements d'exploitation : venv, configuration, secret | C12 §4.1 | contrat C12 |
| B2 | Utilisateur et groupe dedies `boilerack`, non privilegies ; `root` **interdit** pour le processus | C12 §4.2 | contrat C12 |
| B3 | Aucun etat persistant : ni `StateDirectory`, ni `CacheDirectory`, ni `RuntimeDirectory` | C12 §4.3 | contrat C12 |
| B4 | Commande du service, chemin absolu, `--config` explicite | C12 §5 | gabarit versionne |
| B5 | `EnvironmentFile` sous forme **stricte** : le fichier d'environnement est **obligatoire** pour que l'unite demarre | C12 §6 | gabarit versionne |
| B6 | La **variable** `BOILERACK_MQTT_PASSWORD` reste **optionnelle** ; c'est le **fichier** qui est obligatoire | C10 et C12 §6 | contrats |
| B7 | Le fichier d'environnement n'est **pas** versionne dans ce depot | C12 §6 | contrat C12 |
| B8 | Aucun emplacement de configuration par defaut n'est cherche par le programme | C10, A4 de C12 | code du chargeur |
| B9 | Une seule dependance d'execution : `paho-mqtt` | C4 | `pyproject.toml` |
| B10 | Le paquet s'installe et produit reellement la commande `boilerack` | C10, C12 | mesure sur environnement jetable |
| B11 | `requires-python = ">=3.11"` | — | `pyproject.toml` |
| B12 | Le gabarit `systemd/boilerack.service` **n'entre pas dans la wheel** : `packages = ["src/boilerack"]` | — | `pyproject.toml` |
| B13 | `.gitignore` ignore deja `.env` et `.env.*` | — | `.gitignore` |

Ces acquis sont des **entrees** de C13. Les contredire serait une regression, pas
une decision d'installation.

**Fait mesure pendant l'instruction de ce contrat**, et non suppose : une seconde
invocation de `pip install <repertoire>` sur un checkout inchange **reconstruit la
roue, desinstalle la copie precedente et reinstalle**, malgre une version
identique (`0.0.0`). Il n'existe donc **aucune derive silencieuse du code** lors
d'une reinstallation en place. Cet argument, souvent avance en faveur d'une
recreation du venv, est **refute** et n'est pas retenu par §11.

---

## 3. Hors perimetre — liste fermee

Release publique · publication PyPI · tag · changement de version · changement du
classifieur de maturite · packaging Debian ou RPM · Docker · `pipx` · wheel
publiee · artefact publie · toute infrastructure de publication · logique fondee
sur une comparaison de numeros de version · mise a jour versionnee · mise a jour
automatique · rollback · migration automatique de configuration · gestionnaire de
secrets · supervision · durcissement systemd · installation reelle sur une
machine cible ou un Raspberry Pi · `systemctl` reel · activation d'un service ·
demarrage de Boilerack · broker MQTT reel · `vclient` reel · `vcontrold` reel ·
chaudiere · Home Assistant · MQTT Discovery · ecriture chaudiere · modification
de C9, C10, C11 ou C12 · traitement des reserves non bloquantes existantes ·
chantier d'accentuation.

**En particulier, C13 n'installe pas Python.** Un interpreteur `>=3.11` deja
present sur la cible est une **precondition**, pas un livrable.

---

## 4. Arbitrages humains rendus — normatifs

Ces cinq decisions ont ete rendues par arbitrage humain avant redaction. Elles
sont **normatives** et ne sont pas rediscutees ici.

| # | Objet | Retenu | Rejete |
|---|---|---|---|
| A | Forme de l'installateur | **Module Python versionne et testable** | `install.sh` comme autorite principale · procedure documentaire seule |
| B | Source d'installation | **Checkout Git local du depot** | release · artefact publie · paquet systeme · wheel publiee · Docker · logique de version |
| C | Portee du cycle de vie | **Installation · reinstallation idempotente · desinstallation minimale** | mise a jour versionnee |
| D | Activation et demarrage | **INSTALLER SEULEMENT** | `systemctl enable` · `systemctl start` · tout demarrage |
| E | `boilerack.env` | **Cree si absent**, gabarit commente sans valeur active ; **jamais ecrase** | ecrasement · faux secret · versionnement du fichier |

Raison retenue pour A, a conserver comme critere de conception : la logique
d'installation doit pouvoir etre exercee **reellement** sous Windows en
developpement, sous Linux en integration continue, contre une racine synthetique,
sans privilege, et sans toucher a une machine reelle.

Raison retenue pour D : **le premier demarrage reste un geste humain explicite,
apres inspection de la configuration.** L'installation peut documenter les
commandes ulterieures ; elle ne les execute pas.

---

## 5. Preconditions

L'installation est refusee, **avant tout effet**, si l'une de ces conditions
n'est pas remplie.

| # | Precondition | Verifiable hors terrain |
|---|---|---|
| PC1 | Une **racine est explicitement fournie**. Il n'existe **aucune valeur par defaut** | oui |
| PC2 | La **racine resolue** (§8.1bis) et l'autorisation des actes systeme forment une **combinaison admise** (§8.1) : soit une racine resolue **designant** la racine du systeme avec actes **ouverts**, soit une racine resolue **ne la designant pas** avec actes **fermes**. Toute combinaison hybride est refusee | oui |
| PC3 | L'interpreteur qui creera le venv satisfait `sys.version_info >= (3, 11)` | oui |
| PC4 | Le checkout designe existe et contient `pyproject.toml`, `systemd/boilerack.service` et `docs/boilerack.example.toml` | oui |
| PC5 | La racine designee existe et est inscriptible | oui |
| PC6 | En mode reel sur POSIX : l'executant possede les privileges d'administration, **`euid == 0`**. Ce critere couvre ce que le mode reel exige — ecrire dans `/opt` et `/etc`, creer l'identite, changer les proprietaires. A defaut : refus, code de §16, **avant tout effet** | **oui**, par substitution du predicat |
| PC7 | En mode reel : un index de paquets est joignable, ou un equivalent local | **non** — terrain |
| PC8 | En mode reel : un executable rendant le compte **non connectable** est resolvable sur la cible. A defaut : refus, code de §16, **avant tout effet** | **oui**, par substitution du predicat |

**PC6 est desormais exigible, et non plus seulement decrite.** Elle etait
contractee sans critere applicable : une execution reelle sans privilege
commencait ses effets, puis echouait au premier changement de proprietaire — ce
que la doctrine « refus avant effet » interdit. `euid == 0` est retenu parce
qu'il est **deterministe et verifiable** ; modeliser les capacites, un LSM,
`sudo` ou une distribution particuliere serait invérifiable hors terrain et
sortirait du perimetre. La precondition est **POSIX** : le mode reel suppose une
racine designant la racine du systeme, ce qui n'a pas de sens ailleurs.

**PC8 exprime un besoin, pas un chemin.** Le compte systeme `boilerack` cree par
l'installateur doit etre **non connectable**. Le contrat n'inscrit **aucun chemin
absolu** — ni `/usr/sbin/nologin`, ni `/sbin/nologin` — parce qu'il ne fixe
aucune distribution (voir ci-dessous). Il n'impose pas davantage de strategie de
recherche : **resoudre** l'executable sur la cible est une decision
d'implementation, sous tests. Ce que le contrat fixe est l'exigence, la necessite
de la resolution, et le refus lorsqu'elle echoue.

Ces deux preconditions sont **verifiables hors terrain par substitution du
predicat**, exactement comme la moitie « inscriptible » de PC5. Cette
verification prouve le **refus et son absence d'effet** ; elle ne prouve rien du
comportement d'un `useradd` reel, qui reste terrain (§20).

PC1 et PC2 sont evaluees **en premier** : sans elles, aucune des suivantes n'a de
sens, puisque la racine determine ou porteraient les effets. Elles sont la
traduction en preconditions de la regle de surete de §8.1.

**Cible d'exploitation : Linux.** Aucune distribution particuliere n'est fixee :
rien dans le corpus ne l'exige, et le fixer inventerait une contrainte. Les seuls
pre-requis de plateforme sont un systemd et les emplacements de C12 §4.1.

**Ce que C13 ne fait pas en precondition** : il ne configure ni le broker, ni
`vclient`, ni `vcontrold`, ni la chaudiere, ni Home Assistant. Il ne verifie pas
leur presence, et n'a pas a le faire : le programme n'en a besoin qu'au
demarrage, que C13 ne provoque jamais (arbitrage D).

> **Inconnue conservee.** Si l'interpreteur de la cible est anterieur a 3.11, la
> lecture meme du code de l'installateur pourrait echouer avant que PC3 ne soit
> evaluee, selon la syntaxe employee. Aucune preuve n'est possible dans une suite
> qui ne s'execute que sur `>=3.11`. Le message d'echec de PC3 est donc contracte
> pour le cas ou il est atteint, sans garantie qu'il le soit toujours.

---

## 6. Quatre etapes distinctes — a ne jamais confondre

| # | Etape | Qui | Portee C13 |
|---|---|---|---|
| 1 | **Preparation et installabilite** — le paquet se construit et s'installe | deja acquis (B10) | entree |
| 2 | **Installation** — fichiers, identite, environnement, unite deposee | **l'installateur C13** | **objet du lot** |
| 3 | **Prise en compte, activation, demarrage** — `daemon-reload`, `enable`, `start` | **l'humain**, apres inspection | documente, **jamais execute** (§13) |
| 4 | **Qualification terrain** — le service demarre, lit, publie, s'arrete | chantier ulterieur | **hors C13** (§20) |

La confusion de ces quatre etapes est le risque principal du lot. Un rapport, un
message ou une documentation qui laisserait entendre que l'etape 2 produit un
service qui fonctionne serait une **violation** de ce contrat.

---

## 7. Emplacements et proprietes

### 7.1 Consommes de C12, sans modification

| Role | Chemin | Proprietaire | Mode indicatif |
|---|---|---|---|
| Code installe | `/opt/boilerack/venv` | `root` | lecture pour tous |
| Commande | `/opt/boilerack/venv/bin/boilerack` | `root` | executable |
| Configuration | `/etc/boilerack/boilerack.toml` | `root:boilerack` | `0640` |
| Secret | `/etc/boilerack/boilerack.env` | `root:boilerack` | `0640` |

**La colonne porte l'intitulé exact de C12 §4.1 : « Mode indicatif ».** C12 y
décrit un besoin fonctionnel, non une valeur opposable. Deux de ces lignes le
formulent en toutes lettres — « lecture pour tous » et « executable » — et ne
peuvent donc pas être appliquées telles quelles à un système de fichiers.

C12 §12 énonce ce besoin sans ambiguïté : le service doit pouvoir **exécuter**
`/opt/boilerack/venv/bin/boilerack`, et n'a besoin d'**aucune écriture**.
Traduire ce besoin en une valeur Unix concrète est une **décision
d'installation** : elle revient donc à C13, et figure en §7.2. Les deux lignes
`0640` sont déjà numériques et sont reprises sans changement.

### 7.2 Ajouts de C13, derives et signales comme tels

C12 n'a fixe ni le mode des repertoires, ni celui du fichier d'unite. Les laisser
au `umask` rendrait l'installation **non deterministe** : le resultat dependrait
du shell de l'administrateur. C13 les fixe donc, et les justifie.

| Role | Chemin | Proprietaire | Mode | Justification |
|---|---|---|---|---|
| Racine du code | `/opt/boilerack` | `root:root` | `0755` | code non secret, lisible par tous, conforme a C12 §4.1 |
| Repertoire de configuration | `/etc/boilerack` | `root:boilerack` | `0750` | le service doit **traverser** ce repertoire pour lire les deux fichiers `0640` du groupe ; `0750` accorde exactement cela et ne divulgue pas le contenu du repertoire aux autres comptes |
| Unite systemd | `/etc/systemd/system/boilerack.service` | `root:root` | `0644` | fichier d'unite sans secret (C12 §6) ; convention systemd |
| Code installe | `/opt/boilerack/venv` | `root` | `0755` | traduction numerique du « lecture pour tous » de C12 §4.1 — voir ci-dessous |
| Commande | `/opt/boilerack/venv/bin/boilerack` | `root` | `0755` | traduction numerique du « executable » de C12 §4.1 — voir ci-dessous |

Ces cinq lignes sont des **ajouts C13**, pas des donnees C12. Elles sont
attaquables comme telles ; elles ne contredisent aucune clause de C12.

**Le groupe des deux dernieres lignes n'est pas fixe**, et ne doit pas l'etre :
C12 §4.1 nomme `root` seul pour ces deux emplacements, sans groupe. Le service
n'y accede pas par le groupe (voir ci-dessous) ; inventer un `root:boilerack`
ajouterait une regle que le corpus ne porte pas.

#### Pourquoi `0755` pour les deux emplacements du venv

Le raisonnement est fonctionnel, et il part de C12 §12, non d'un usage Unix.

Le service tourne sous l'identite `boilerack` : il n'est **ni `root`, ni membre
du groupe `root`**. Ce sont donc les bits **« autres »** qui gouvernent son
acces. C12 §12 exige qu'il puisse **exécuter**
`/opt/boilerack/venv/bin/boilerack` — ce qui suppose aussi de **traverser** le
repertoire du venv et d'y **lire** — et precise qu'**aucune ecriture** ne lui est
requise ni accordee.

| Candidate | Autres | Consequence |
|---|---|---|
| `0750` ou `0550` en `root:root` | `---` | **Incompatible** : le service ne peut ni traverser, ni lire, ni executer. Contredit une exigence ecrite de C12 §12 |
| `0555` | `r-x` | Fonctionne, mais n'apporte **aucune protection reelle** : `root` — le seul compte a posseder le bit d'ecriture retire — contourne de toute facon les controles de permission. Le gain est symbolique, et le mode gene la reinstallation |
| **`0755`** | `r-x` | **Retenu** : donne aux autres exactement la lecture et la traversee ou l'execution requises, et conserve a `root` la capacite d'administrer sans lutter contre le mode |

Aucune valeur n'est retenue parce qu'elle serait courante : `0750` et `0550` sont
**eliminees par contradiction** avec C12 §12, et `0755` l'emporte sur `0555` par
absence de benefice reel de cette derniere.

### 7.3 Quand chaque metadonnee est posee — deux groupes

Les proprietaires et les modes ci-dessus ne sont pas tous applicables au meme
moment de l'installation. §8.3 en fixe l'ordre ; la repartition est fixee ici.

| Groupe | Emplacements | Pose |
|---|---|---|
| **A — hors venv** | `/opt/boilerack` · `/etc/boilerack` · `/etc/boilerack/boilerack.toml` · `/etc/boilerack/boilerack.env` · `/etc/systemd/system/boilerack.service` | **avant** l'etape venv, une fois ces emplacements crees ou constates presents |
| **B — venv** | `/opt/boilerack/venv` · `/opt/boilerack/venv/bin/boilerack` | **apres** la creation reussie du venv |

Raison, developpee en §8.3 : les emplacements du groupe B n'existent pas encore
lors d'une premiere installation, et sont detruits puis recrees lors d'une
reinstallation. Leur poser des metadonnees avant l'etape venv ne porterait sur
rien, ou serait annule aussitot.

`/opt/boilerack` appartient au groupe **A** bien qu'il contienne le venv : il
n'est jamais detruit par l'etape venv, qui ne supprime que `/opt/boilerack/venv`.

#### Aucune normalisation recursive

**Clause normative.** La pose des metadonnees porte **exclusivement sur les
emplacements nommes** en §7.1 et §7.2. Le `0755` des deux emplacements du groupe
B ne signifie **pas** un `chmod` recursif de l'arbre du venv.

Les modes internes du venv restent gouvernes par `venv` et par `pip`, sous le
`umask` que §8.3ter fixe pendant leur execution. Les ecraser recursivement
imposerait une politique etrangere aux outils qui ont fabrique cet arbre : selon
la valeur appliquee, cela rendrait executables des fichiers ordinaires, ou
retirerait le bit d'execution a des scripts qui en ont besoin.

Un `chmod` recursif de l'arbre du venv est donc une **violation** de ce contrat.

---

## 8. Modele d'installation — effets observables

L'installateur est un **module Python versionne** (arbitrage A). Ce contrat ne
fixe **ni son nom de module, ni son API interne** : ce sont des choix
d'implementation. Il fixe ses **effets metier observables**, son **ordre**, ses
**refus** et ses **codes de sortie**.

### 8.1 Entrees

| Entree | Role | Defaut |
|---|---|---|
| **checkout** | repertoire source, au sens de l'arbitrage B | **AUCUN** — explicite |
| **racine** | prefixe sous lequel tous les chemins de §7 sont deposes | **AUCUN** — explicite |
| **execution des actes systeme** | autorise ou non l'execution reelle des actes privilegies | **non autorise** |

Le checkout est **explicite et sans defaut**. Le deduire de l'emplacement du
code introduirait une recherche implicite de chemin, exactement ce que C10 refuse
pour la configuration ; la coherence de doctrine l'emporte sur la commodite.

**La racine est explicite et sans defaut**, pour une raison de surete et non de
style. Un defaut a `/` ne protegerait rien : le bouton des actes systeme ne
retient que l'identite, les proprietaires et les modes. Il ne retient **ni
l'ecriture dans `/etc`, ni l'ecriture dans `/opt`, ni la suppression du venv**.
Une invocation portant une racine implicite `/` et des actes systeme fermes
ecrirait donc reellement dans le systeme et **detruirait
`/opt/boilerack/venv`** — sans qu'aucune decision explicite ne l'ait demande.

Exiger une racine explicite ferme l'acces **par omission** au systeme hote :
aucune invocation ne peut plus y porter faute d'avoir nomme sa cible. Cela ne
suffit pas : encore faut-il que la cible nommee soit classee pour ce qu'elle
**designe**, et non pour la facon dont elle est **ecrite**. C'est l'objet de
§8.1bis.

### 8.1bis Racine resolue — la classification porte sur ce qui est designe

**Clause normative.** La classification d'une racine en **reelle** ou
**synthetique** porte sur la **racine resolue**, jamais sur sa representation
textuelle brute.

Avant toute classification et avant tout effet, l'installateur **resout** la
racine fournie, au sens du systeme de fichiers : elimination des composantes
`.` et `..`, et traversee des liens symboliques.

- Si la racine resolue **designe la racine du systeme de fichiers**, la racine
  est classee **REELLE**.
- Sinon, elle peut etre classee **SYNTHETIQUE**.

**Aucune representation alternative, aucune composante `..`, aucune syntaxe
equivalente et aucun lien symbolique ne doit permettre de contourner cette
classification.**

#### Le critere est l'identite du repertoire designe

Le test est **« la racine resolue designe-t-elle la racine du systeme ? »**, et
**non** « la racine resolue est-elle egale a la chaine `/` ? ». La distinction
n'est pas theorique : certaines representations survivent a une canonicalisation
sous une forme textuelle differente tout en designant le meme repertoire. Une
comparaison de chaines les classerait **synthetiques**, et rouvrirait exactement
le defaut que cette clause ferme.

Une comparaison d'**identite de repertoire** — au sens de « ces deux chemins
designent-ils le meme repertoire » — satisfait le critere. Le contrat ne
prescrit **aucune API** : `Path.resolve()` et une comparaison d'identite de
repertoire sont des realisations possibles, citees a titre d'exemple et non
comme norme.

#### Ce que cette clause ne promet pas

**Clause d'honnetete, sans attenuation.** La resolution de chemin traite les
alias **de chemin**. Elle ne traite pas les alias **de montage ou de
configuration systeme** : un `bind mount`, un espace de noms de montage, un
`chroot`, ou tout mecanisme noyau equivalent peut faire qu'un chemin resolu
distinct de la racine donne neanmoins acces au systeme reel. Aucune
canonicalisation portable ne le detecte.

| Classe d'alias | Traitee par §8.1bis |
|---|---|
| Composantes `.` et `..` | **oui** |
| Liens symboliques sur le chemin de la racine | **oui** |
| Representations equivalentes de la racine | **oui**, par identite du repertoire designe |
| `bind mount`, espace de noms, `chroot`, equivalents noyau | **NON** — limite terrain (§20) |

C13 **ne pretend pas** fermer la seconde classe. Elle reste une limite portee au
§20, au meme titre que les autres proprietes qui ne sont pas prouvables hors
terrain. Promettre l'inverse serait exactement la faute que cette correction
repare.

#### Deux modes, et deux seulement

| Mode | Racine **resolue** | Actes systeme | Effets systeme de fichiers | Actes systeme differes | `systemctl` |
|---|---|---|---|---|---|
| **Synthetique** | explicite, **ne designant pas** la racine du systeme | **FERMES** | reels, sous la racine | **declares**, jamais executes | **jamais** |
| **Reel** | explicite, **designant** la racine du systeme | **OUVERTS** | reels, sur le systeme | **executes** | **jamais** |

#### Combinaisons interdites — refus avant tout effet

| Racine **resolue** | Actes systeme | Issue |
|---|---|---|
| absente | quelconque | **REFUS** — PC1 |
| **designe** la racine du systeme | **fermes** | **REFUS** — PC2 |
| **ne designe pas** la racine du systeme | **ouverts** | **REFUS** — PC2 |

**Aucune combinaison hybride n'existe.** Le refus intervient **avant tout effet**,
au titre de PC1 et PC2, et au code de sortie de §16.

Emprunter le chemin reel, seul chemin destructeur, exige donc **deux decisions
explicites et coherentes** : designer la racine du systeme **et** ouvrir les
actes systeme. Une seule des deux ne suffit jamais, et **aucune ecriture de la
racine ne permet de designer le systeme tout en etant classee synthetique**
(§8.1bis).

Ce dispositif n'est **pas** un moteur de modes : il n'y a ni etat, ni strategie,
ni extension possible. Deux combinaisons sont admises, trois sont refusees, et le
contrat les enumere en entier.

### 8.2 Deux categories d'actes, a ne pas melanger

**Actes systeme differes** — executes en mode reel, **declares** en mode
synthetique :

- creation du groupe `boilerack` s'il est absent ;
- creation de l'utilisateur `boilerack` s'il est absent, non privilegie ;
- changement de proprietaire de chaque emplacement de §7, **en deux groupes** (§7.3) ;
- changement de mode de chaque emplacement de §7, **en deux groupes** (§7.3).

Le **mode** figure dans cette liste, bien qu'il soit techniquement applicable sans
privilege sur POSIX. Raison : sous Windows, `chmod` n'a pratiquement pas d'effet,
et une regle qui appliquerait les modes sur une plateforme et pas sur l'autre
rendrait la preuve dependante de la plateforme — ce que l'arbitrage A cherche
precisement a eviter. La regle uniforme « en mode synthetique, tout acte systeme
est declare et aucun n'est execute » est verifiable a l'identique partout.

**Actes humains restants** — **jamais executes, dans aucun mode** :

```text
systemctl daemon-reload
systemctl enable boilerack.service
systemctl start boilerack.service
```

Voir §13 pour la justification, `daemon-reload` compris.

Ces deux listes sont **restituees a l'appelant** et **rendues dans la sortie** de
l'installateur. C'est le mecanisme unique qui rend « observable, inspectable, non
execute » ce qui ne peut pas etre execute hors terrain.

### 8.3 Ordre normatif des effets

L'ordre est **contracte**, pas laisse a l'implementation, parce qu'il determine
ce qui subsiste apres un echec.

```text
1.  Preconditions PC1 a PC5, et PC6 et PC8 en mode reel — aucun effet
2.  Groupe et utilisateur boilerack, si absents
3.  Repertoires HORS VENV : /opt/boilerack, /etc/boilerack, /etc/systemd/system
4.  /etc/boilerack/boilerack.toml — CONTENU depose SI ABSENT SEULEMENT
5.  /etc/boilerack/boilerack.env  — CONTENU depose SI ABSENT SEULEMENT
6.  /etc/systemd/system/boilerack.service — toujours depose
7.  METADONNEES, premier groupe : proprietaires et modes des emplacements
    HORS VENV, tous crees ou presents a ce stade (§7.3, groupe A)
8.  VENV — SEULE ETAPE DESTRUCTIVE, sous `umask` fixe (§8.3ter) et sous garde
    destructive (§8.3quater) : suppression si present, creation, installation du
    paquet depuis le checkout
9.  METADONNEES, second groupe : proprietaires et modes des emplacements
    DU VENV, apres creation reussie de celui-ci (§7.3, groupe B)
10. Restitution des actes systeme differes et des actes humains restants
```

### Pourquoi les metadonnees sont posees en deux temps

Un seul groupe de metadonnees place avant l'etape 8 serait **normativement
faux**. A ce moment, `/opt/boilerack/venv` et `/opt/boilerack/venv/bin/boilerack`
**n'existent pas encore** lors d'une premiere installation ; et lors d'une
reinstallation, ils sont **detruits juste apres** par l'etape 8. Leur appliquer un
proprietaire et un mode a ce moment-la ne porterait sur rien, ou serait annule
dans la seconde qui suit.

Les metadonnees d'un emplacement sont donc posees **apres** que cet emplacement
existe dans sa forme definitive, et pas avant. §7.3 fixe l'appartenance de chaque
emplacement a l'un des deux groupes.

### Clause normative de destruction

**L'etape 8 est la seule etape destructive, et elle est la DERNIERE ETAPE
DESTRUCTIVE.** Elle n'est pas la derniere operation absolue : les etapes 9 et 10
la suivent.

Cette precision n'est pas verbale. **Les etapes 9 et 10 ne detruisent rien** :
poser un proprietaire et un mode sur un venv qui vient d'etre cree, puis restituer
deux listes, ne peut faire perdre ni configuration, ni secret, ni unite, ni code
installe. La garantie recherchee — *tout ce qui peut etre perdu l'est au plus tard
a l'etape 8* — est donc integralement conservee.

Toutes les operations bon marche et sures precedent l'unique operation qui detruit
et qui depend du reseau. Un echec en 8 laisse la configuration, le secret,
l'unite, l'identite et **les metadonnees hors venv** en place, et une seconde
invocation reprend sans rien perdre.

L'inversion de cet ordre est une **violation**, sous ses deux formes : deplacer
le venv **avant** le depot de la configuration et du secret (mute en §18, M13),
et poser les metadonnees du venv **avant** que le venv existe (mute en §18, M18).

### 8.3bis Identite avant appropriation

**Clause normative.** Les actes d'**identite** — creation ou constat du groupe et
de l'utilisateur `boilerack` — precedent **tout acte d'appropriation qui
reference cette identite**.

La raison est mecanique : un changement de proprietaire vers `root:boilerack`
echoue si le groupe `boilerack` n'existe pas encore. L'etape 2 de §8.3 place donc
l'identite avant l'etape 7, et cet ordre est **normatif**, non un effet de
l'ordre de redaction du code.

Invariants de l'identite, en mode reel :

- le groupe n'est cree que s'il est **absent** ; sinon il est constate ;
- l'utilisateur n'est cree que s'il est **absent** ; sinon il est constate ;
- une creation **necessaire** qui echoue est une **panne explicite**, jamais
  ignoree : la faire disparaitre ferait resurgir l'echec plus tard, sous la forme
  moins lisible d'un changement de proprietaire impossible ;
- l'utilisateur cree est **non connectable** (PC8) ;
- la desinstallation ne supprime **ni le groupe, ni l'utilisateur** (§12.2,
  inchange).

Ce contrat ne prescrit **aucune API** pour constater l'existence ou pour creer :
c'est une decision d'implementation, sous tests.

### 8.3ter `umask` de l'etape venv

**Clause normative.** L'etape 8 s'execute sous un `umask` **fixe a `0022`**.
L'installateur sauvegarde le `umask` courant avant l'etape, l'applique pour la
**seule** duree de la creation du venv et de l'installation du paquet, puis le
**restaure — succes ou echec**.

Sa portee est **strictement** cette etape. Aucune autre etape n'est concernee.

Justification, et elle n'est pas empruntee a un usage : §7.2 refuse deja de
laisser au `umask` le mode des repertoires qu'il cree, au motif que « le resultat
dependrait du shell de l'administrateur ». Le meme raisonnement s'applique a
l'arbre que l'etape 8 fait produire par `venv` et par `pip`.

Sans cette clause, une installation pourrait **reussir**, poser exactement les
modes de §7.2, et produire malgre tout un service **incapable de demarrer** : un
`umask` restrictif rendrait les repertoires intermediaires du venv inaccessibles
aux « autres », c'est-a-dire a l'identite sous laquelle le service tourne. Aucune
preuve hors ligne ne detecterait cette situation.

`0022` est la valeur qui laisse `venv` et `pip` produire un arbre traversable et
lisible par tous, sans qu'aucun `chmod` recursif ne soit necessaire (§7.3).

### 8.3quater Garde destructive

**Clause normative.** Avant **toute suppression** contractee, le chemin **resolu**
de la cible doit rester **sous la racine resolue**. Sinon : **refus**, code de
§16, et **aucune suppression**.

La resolution est celle de §8.1bis — composantes `.` et `..` eliminees, liens
symboliques traverses — et la comparaison porte sur l'appartenance au sous-arbre,
non sur la ressemblance des chaines.

« Rester sous la racine resolue » signifie ici : **la cible resolue est un
descendant STRICT de la racine resolue**. L'egalite est exclue : aucune cible
destructive contractee n'est la racine elle-meme, et l'admettre autoriserait la
suppression de la racine.

Cibles concernees — celles que le contrat supprime effectivement :

| Operation | Cible |
|---|---|
| Installation, etape 8 | `/opt/boilerack/venv` |
| Desinstallation | `/opt/boilerack` |
| Desinstallation | `/etc/systemd/system/boilerack.service` |

Le risque ferme est concret : si `<racine>/opt/boilerack` est un **lien
symbolique** vers l'exterieur, l'etape 8 supprimerait `<cible>/venv` **hors de la
racine**, sans que rien ne le signale. Que l'auteur du lien ait deja du pouvoir
ecrire sous la racine n'attenue pas le dommage : une suppression **hors** de la
racine est d'une autre nature qu'une suppression dedans.

Cette garde n'est **pas** un bac a sable : elle ne restreint aucun acces, ne
surveille aucune ouverture de fichier et ne couvre pas les cibles non
destructives. Elle est une resolution suivie d'une preuve d'appartenance.

### 8.4 Contenus deposes

| Cible | Source | Regle |
|---|---|---|
| `/etc/systemd/system/boilerack.service` | `systemd/boilerack.service` du checkout | **copie octet pour octet**, sans substitution |
| `/etc/boilerack/boilerack.toml` | `docs/boilerack.example.toml` du checkout | **copie octet pour octet**, si absent seulement |
| `/etc/boilerack/boilerack.env` | modele **inline** dans l'installateur (§10) | si absent seulement |

**Aucune substitution de gabarit.** Les chemins inscrits dans l'unite sont des
constantes absolues fixees par C12 §4.1 : il n'y a **rien** a substituer. La
copie octet pour octet est donc a la fois la regle la plus simple, la plus
deterministe et la seule qui rende opposable la validation statique de C12 §13 —
si le fichier depose differait du gabarit valide, cette validation ne prouverait
plus rien sur ce qui est reellement installe.

**Consequence a enoncer sans attenuation** : sous une racine synthetique, l'unite
deposee continue de designer `/opt/boilerack/venv/bin/boilerack`, qui n'existe pas
sous cette racine. C'est voulu. Le mode synthetique prouve le **placement** et le
**contenu**, jamais la coherence des chemins avec le systeme hote.

**Consequence a documenter pour l'exploitant** : la configuration initiale copiee
depuis l'exemple porte `host = "broker.exemple.invalid"` et
`executable = "vclient"`. Elle est **valide syntaxiquement et inutilisable en
l'etat**. L'installateur ne doit jamais laisser entendre qu'elle est prete ; c'est
precisement ce que l'inspection humaine exigee par l'arbitrage D vient corriger.

---

## 9. Politique de non-ecrasement — propriete critique

C'est la propriete dont la violation cause le plus grand dommage : perdre la
configuration ou le secret d'une installation en service.

| Fichier | Absent | Present |
|---|---|---|
| `/etc/boilerack/boilerack.toml` | **contenu** cree depuis l'exemple versionne | **CONTENU PRESERVE — jamais ecrase, jamais modifie, jamais fusionne** |
| `/etc/boilerack/boilerack.env` | **contenu** cree depuis le modele de §10 | **CONTENU PRESERVE — jamais ecrase, jamais modifie, jamais fusionne** |

### 9.1 Ce que « non-ecrasement » signifie exactement

La souverainete de l'exploitant porte sur le **CONTENU**. Elle ne porte pas sur
les metadonnees du systeme de fichiers.

| Aspect | Regle | Portee |
|---|---|---|
| **Contenu** | **byte-identique** avant et apres. Aucune fusion, aucune correction automatique, aucune reinitialisation, aucun secret remplace | **exploitant** |
| **Proprietaire, groupe, mode** | **reappliques** a chaque installation et reinstallation, selon §7 et §7.3 | **contrat d'installation** |

**Clause normative.** Dans tout ce contrat, « non-ecrasement » et
« non-modification » designent le **contenu, octet pour octet**. Ces termes ne
designent **pas** la conservation des proprietaires et des modes anterieurs.

Consequence a documenter pour l'exploitant : **un exploitant qui a modifie a la
main le proprietaire, le groupe ou le mode de l'un de ces deux fichiers doit
s'attendre a leur normalisation lors d'une reinstallation.** Cette normalisation
n'est **pas** une modification du contenu, et n'est donc **pas** une violation :
c'est le comportement contracte.

Raison : les metadonnees de ces fichiers sont une propriete de **surete** —
`0640 root:boilerack` est ce qui empeche un compte quelconque de lire le secret.
Les laisser deriver au fil des interventions manuelles ferait de la
reinstallation un moyen de conserver une faiblesse plutot que de la corriger.

**Il n'existe aucun mode « preserve metadata ».** Ni option, ni variable, ni
combinaison d'entrees ne permet de sauter la reapplication.

### 9.2 L'ecrasement de contenu est une violation

**Clause normative.** L'ecrasement silencieux du **contenu** de l'un de ces deux
fichiers est une **violation du contrat**, y compris lors d'une reinstallation, y
compris si le contenu present est juge invalide, et y compris s'il est vide.
L'installateur n'a **aucun mode** qui autorise cet ecrasement : il n'existe ni
option, ni variable, ni combinaison d'entrees qui le rende possible. Ajouter une
telle option serait une violation.

Preserver n'est **pas une erreur** : une installation qui trouve ces fichiers en
place et laisse leur contenu intact **reussit** et rend `0`. Elle le **signale**
dans sa sortie, afin que l'exploitant sache que sa configuration n'a pas ete
rafraichie.

Le fichier d'unite, lui, est **toujours redepose** : il n'appartient pas a
l'exploitant, il appartient au programme, et il est reconstructible octet pour
octet depuis le checkout. Aucun contenu utilisateur n'y vit — C12 §6 interdit
explicitement qu'un secret y figure.

---

## 10. Contenu initial de `boilerack.env`

### 10.1 Clauses normatives

Le fichier cree, lorsqu'il est absent :

1. est **valide comme `EnvironmentFile` systemd** — commentaires `#`, lignes
   vides et affectations `CLE=valeur` ;
2. **ne definit aucune variable** : il ne contient **aucune affectation active** ;
3. **cite `BOILERACK_MQTT_PASSWORD`** en commentaire, afin que l'exploitant sache
   quoi renseigner ;
4. **ne contient aucun secret**, ni reel, ni factice, ni exemple ressemblant a un
   secret — la clause de C12 §6 s'applique ici mot pour mot ;
5. rend possible une installation **sans authentification MQTT** : le fichier
   existe, donc l'unite peut demarrer (B5) ; la variable est absente, donc le mot
   de passe vaut `None` (B6) ;
6. n'est **pas versionne** dans le depot.

La clause 6 impose que le modele soit **inline dans le code de l'installateur**,
et non un fichier d'exemple versionne. Deux raisons, dont une factuelle : la
premiere est C12 §6, la seconde est que `.gitignore` ignore deja `.env` et
`.env.*` (B13), de sorte qu'un tel fichier ne pourrait etre ajoute sans creer une
exception a une regle de protection.

### 10.2 Modele — illustratif, non fige au caractere pres

Les clauses 1 a 6 sont normatives ; le texte ci-dessous en est une realisation
conforme. Les tests verifieront les **proprietes**, non ces octets.

```text
# Environnement d'exploitation Boilerack.
#
# Ce fichier est ATTENDU par l'unite systemd : son absence empeche le
# demarrage (voir docs/design/c12-service-contract.md, §6).
#
# Il ne definit AUCUNE variable par defaut, et son CONTENU n'est JAMAIS
# ecrase par une reinstallation.
#
# Si le broker MQTT exige un mot de passe, decommentez la ligne suivante et
# renseignez-la. Sinon, laissez-la telle quelle : la variable est
# optionnelle, c'est le fichier qui est obligatoire.
#
# BOILERACK_MQTT_PASSWORD=
```

**C13 n'est pas un gestionnaire de secrets.** Il ne genere aucun mot de passe, ne
lit aucun coffre, ne chiffre rien, ne valide aucune valeur. Il cree un fichier
vide de valeur active, aux bonnes permissions, et s'arrete la.

---

## 11. Reinstallation et idempotence

### 11.1 Ce qui est preserve, ce qui est refait

| Element | Seconde installation |
|---|---|
| Groupe et utilisateur `boilerack` | **retrouves** s'ils existent ; jamais recrees, jamais modifies |
| `/opt/boilerack`, `/etc/boilerack` | **retrouves** s'ils existent |
| `/etc/boilerack/boilerack.toml` | **CONTENU PRESERVE** (§9.1) ; **metadonnees reappliquees** (§7, §9.1) |
| `/etc/boilerack/boilerack.env` | **CONTENU PRESERVE** (§9.1) ; **metadonnees reappliquees** (§7, §9.1) |
| `/etc/systemd/system/boilerack.service` | **redepose**, octet pour octet |
| Proprietaires et modes | **reappliques**, en **deux temps** : groupe A avant l'etape venv, groupe B apres (§7.3, §8.3) |
| `/opt/boilerack/venv` | **detruit puis recree**, voir §11.2 ; ses metadonnees sont posees **apres** sa recreation |

### 11.2 Politique du venv — decision derivee, et son instruction complete

Deux politiques raisonnables existaient. Elles ont ete instruites avant d'etre
departagees, et l'argument le plus souvent avance a ete **refute par la mesure**.

**Ce qui a ete refute.** L'argument selon lequel une mise a jour en place
laisserait subsister l'ancien code — pip considerant la version `0.0.0` deja
satisfaite — est **faux**. La mesure figure en §2 : pip reconstruit la roue,
desinstalle la copie precedente et reinstalle. Une mise a jour en place rafraichit
donc bien le code. Cet argument n'est **pas** retenu.

**Ce qui a ete elimine.** Construire un venv a cote puis permuter les repertoires
est ecarte pour deux raisons. La premiere est §21 : cela introduit un mecanisme
transactionnel que la sobriete du lot exclut. La seconde est que les scripts de
console d'un venv POSIX portent un interpreteur en chemin absolu, ce qui rend un
venv non relogeable — **propriete non mesuree depuis la machine de
developpement**, et donc citee comme motif secondaire seulement.

**Ce qui departage.** L'arbitrage C emploie le mot **idempotente**. Une
reinstallation idempotente produit le meme etat final quel que soit l'etat
anterieur. Or une mise a jour en place **ne l'est pas** : le contenu final du venv
depend de son histoire — un paquet installe manuellement y demeure, une dependance
retiree de `pyproject.toml` y demeure, une version de dependance obtenue lors
d'une installation anterieure y demeure. La recreation, elle, est idempotente par
construction : le contenu du venv ne depend que du checkout et de l'index.

**Decision : le venv est detruit puis recree a chaque installation.**

**Risque assume, enonce sans attenuation.** Entre la destruction et la fin de
l'installation du paquet, la cible n'a **pas** de programme installe. Si l'etape
echoue — index injoignable, disque plein, interruption — l'installation precedente
est perdue et le service ne peut plus demarrer. Ce risque est **mitige par
construction, pas supprime** : §8.3 place cette etape **apres toutes les
verifications et tous les depots surs**, en **derniere position destructive**, de
sorte que l'echec soit tardif, visible, et rattrapable par une simple seconde
invocation. Seule la pose des metadonnees du venv la suit, et elle ne detruit
rien. Aucun rollback n'est fourni (§21).

**Consequence a documenter** : une reinstallation pendant que le service tourne
n'est pas coordonnee par C13 (arbitrage D : ni arret, ni demarrage). Le processus
en cours survit a la destruction de ses fichiers — il tient ses inodes ouverts —
mais tout redemarrage survenant pendant l'operation echoue. **La reinstallation
d'un service en fonctionnement est un geste a encadrer par l'exploitant.**

---

## 12. Desinstallation minimale

### 12.1 Principe

**Supprimer ce qui appartient au programme. Preserver ce qui appartient a
l'exploitant.**

| Element | Sort | Justification |
|---|---|---|
| `/opt/boilerack/venv` | **SUPPRIME** | code, reconstructible depuis le checkout |
| `/opt/boilerack` | **SUPPRIME** | ne contient que le venv ; cree par C13 |
| `/etc/systemd/system/boilerack.service` | **SUPPRIME** | artefact du programme, reconstructible octet pour octet, sans contenu utilisateur |
| `/etc/boilerack/boilerack.toml` | **PRESERVE** | configuration de l'exploitant |
| `/etc/boilerack/boilerack.env` | **PRESERVE** | secret de l'exploitant |
| `/etc/boilerack/` | **PRESERVE** | contient les deux precedents ; sa suppression n'apporte rien et sa conservation est visible et sans nuisance |
| Utilisateur `boilerack` | **PRESERVE** | voir §12.2 |
| Groupe `boilerack` | **PRESERVE** | voir §12.2 |

Une seule regle pour `/etc/boilerack/` : il n'est **jamais** supprime, meme s'il
se trouve vide. Une regle conditionnelle « supprimer si vide » ajouterait une
branche et un cas limite pour un benefice nul.

### 12.2 Pourquoi l'identite n'est pas supprimee

Trois raisons, dont la troisieme est decisive.

1. La suppression d'un compte systeme a une **portee systeme**, au-dela de
   Boilerack : l'administrateur a pu creer ce compte, ou l'utiliser ailleurs.
   C13 ne peut pas le savoir et n'a pas a le presumer.
2. Elle laisserait des fichiers orphelins ailleurs sur la machine, hors de la
   connaissance de C13.
3. **Les fichiers preserves restent detenus par le groupe `boilerack`.** Supprimer
   le groupe laisserait `/etc/boilerack/boilerack.env` — le **secret** — detenu
   par un identifiant numerique libere, qu'un groupe ulterieur et sans rapport
   pourrait recevoir, heritant ainsi du droit de lecture. Supprimer le groupe
   serait donc une **regression de securite**.

### 12.3 Refus de securite

L'unite peut avoir ete activee. La supprimer sans la desactiver laisserait un lien
d'activation pointant vers un fichier absent, et systemd echouerait au demarrage
suivant.

**Clause normative** : si le lien d'activation existe sous la racine —
typiquement `/etc/systemd/system/multi-user.target.wants/boilerack.service` — la
desinstallation **refuse**, ne supprime **rien**, et indique la commande humaine
requise :

```text
systemctl disable --now boilerack.service
```

Ce controle est un examen du **systeme de fichiers**, pas un appel a `systemctl`.
Il est donc exercable en mode synthetique, ce qui est la raison pour laquelle il
est contracte plutot que laisse a la documentation.

La **garde destructive de §8.3quater** s'applique en outre aux deux suppressions de
cette section : `/opt/boilerack` et l'unite. Une cible dont le chemin resolu ne
serait pas un descendant strict de la racine resolue est refusee, et rien n'est
supprime.

### 12.4 Ce que la desinstallation ne fait pas

Elle ne demarre ni n'arrete aucun service · elle n'appelle aucun `systemctl` · elle
ne touche a aucune configuration · elle ne touche a aucun secret · elle ne
desinstalle pas Python · elle ne supprime pas le checkout. Elle est **idempotente** :
une seconde execution ne trouve plus rien a supprimer et **reussit**.

Elle restitue, comme l'installation, les actes humains restants :

```text
systemctl daemon-reload
```

---

## 13. systemd — quatre actes distincts

| Acte | Effet | Qui l'execute |
|---|---|---|
| **Copie du fichier** | l'unite existe sur le disque | **l'installateur C13** |
| **Prise en compte** — `daemon-reload` | systemd lit l'unite et la connait | **l'humain** |
| **Activation** — `enable` | l'unite demarrera au prochain amorcage | **l'humain** (arbitrage D) |
| **Demarrage** — `start` | le pont s'execute, joint le broker, lance `vclient` | **l'humain** (arbitrage D) |

### 13.1 Le cas de `daemon-reload` — decision instruite

L'arbitrage D nomme explicitement `enable` et `start`. Il ne nomme **pas**
`daemon-reload`, qui ne demarre rien, n'active rien et ne change l'etat d'aucun
service. Le corpus ne tranche donc pas directement.

**Argument pour l'executer** : sans lui, l'unite deposee n'est pas connue de
systemd, et l'installation laisse un etat incomplet.

**Arguments pour ne pas l'executer**, retenus :

1. Il exige `root` **et** un systemd vivant. Il est donc **impossible a executer
   en mode synthetique** et **impossible a prouver hors terrain**. Toute la
   doctrine du projet — C12 §14 en particulier — tient les actes non prouvables
   hors du perimetre et les documente.
2. Une regle **uniforme** — « l'installateur n'execute aucun `systemctl`, jamais,
   dans aucun mode » — est plus sobre, plus lisible et plus testable qu'une regle
   comportant une exception unique. La propriete P9 devient absolue au lieu d'etre
   nuancee.
3. L'humain doit de toute facon executer `enable` et `start`. Grouper les trois
   commandes en un seul bloc a executer apres inspection est plus clair que d'en
   detacher une.

**Decision : l'installateur n'execute aucun `systemctl`, `daemon-reload` compris.**
Il le **restitue** comme **premiere** des trois commandes humaines, precisement
pour que l'unite fraichement deposee soit relue avant toute activation.

Cette decision est **derivee de la doctrine, non imposee par une clause
explicite**. Elle est signalee comme telle et reste attaquable en audit.

---

## 14. Privileges

Deux sujets distincts, que rien n'autorise a confondre.

**L'installateur**, en mode reel, a besoin de privileges : ecrire dans `/opt` et
`/etc`, creer un utilisateur et un groupe, changer des proprietaires. Ces besoins
sont reels et assumes ; ils sont **exiges de l'operateur**, pas du service.

**Le processus Boilerack** ne recoit **aucun privilege**. C12 §4.2 est
categorique : `root` est **interdit**. C13 ne l'affaiblit sur aucun point — il
cree precisement l'identite non privilegiee que C12 exige, et n'ajoute aucune
capacite, aucun droit d'ecriture, aucun repertoire d'etat (B3).

**Le mode synthetique n'exige aucun privilege.** C'est une exigence de conception,
pas une commodite : une preuve qui reclamerait `root` ne pourrait tourner ni sur
la machine de developpement, ni en integration continue, et l'arbitrage A
deviendrait sans objet.

---

## 15. Mode synthetique

### 15.1 Definition

Une **racine synthetique** est un repertoire temporaire quelconque, **fourni
explicitement**, et dont la **resolution ne designe pas la racine du systeme de
fichiers** (§8.1bis), sous lequel tous les chemins de §7 sont deposes tels quels.
Une racine dont la resolution **designe** la racine du systeme releve d'une
installation reelle, et n'est admise qu'avec les actes systeme ouverts (§8.1).

Le classement porte sur la racine **resolue**, jamais sur son ecriture : `/.`,
`/opt/..` ou un lien symbolique vers la racine designent la racine du systeme et
sont classes **reels**, quelle que soit leur apparence.

Il n'existe **aucune racine implicite** : une invocation qui n'en fournit pas est
refusee avant tout effet (PC1). Une racine synthetique accompagnee d'actes
systeme **ouverts** est egalement refusee (PC2). Le mode synthetique n'est donc
pas un reglage que l'on peut approcher a moitie : il est l'une des deux seules
combinaisons admises.

Aucun privilege n'est requis. Aucun acte systeme n'est execute (§8.2). Aucun
`systemctl` n'est execute, dans aucun mode (§13).

### 15.2 Ce qui y est exerce reellement

Creation de l'arborescence · creation des repertoires · copie de l'unite ·
copie de la configuration initiale · generation de `boilerack.env` ·
non-ecrasement du **contenu** de la configuration · non-ecrasement du **contenu**
du secret · seconde installation · ordre des effets, y compris la pose des
metadonnees en deux temps · refus des combinaisons interdites de racine et
d'actes systeme · desinstallation · refus sur lien d'activation · codes de sortie ·
messages · echecs de precondition · restitution des actes differes et des actes
humains.

La **preparation du venv** y est egalement exercable : `python -m venv` et
l'installation du paquet ne demandent aucun privilege et fonctionnent sous une
racine arbitraire.

**Clause d'honnetete, a ecrire sans attenuation** : cette etape **n'est pas hors
ligne**. Elle telecharge le moteur de construction et la dependance d'execution
depuis un index. Toute documentation ou tout commentaire qui la presenterait comme
hors ligne serait faux — c'est exactement le defaut corrige dans C12.

### 15.3 Ce qui y est seulement observable

Creation du groupe · creation de l'utilisateur · changement de proprietaire ·
changement de mode · les trois commandes `systemctl`.

Ces actes sont **declares, inspectables et non executes**. Leur declaration prouve
que l'installateur **les aurait demandes** ; elle ne prouve **rien** de leur
effet reel.

### 15.4 Ce que le mode synthetique ne prouve pas

Il ne prouve **aucune conformite terrain** (§20). Une installation validee contre
une racine synthetique n'est **pas** une installation qui fonctionne sur une
machine cible. Ce contrat ne revendique nulle part le contraire.

---

## 16. Codes de sortie et messages

C13 reprend la grille de C10 plutot que d'en inventer une.

| Code | Sens | Trace |
|---|---|---|
| `0` | succes — installation, reinstallation ou desinstallation menee a bien | — |
| `2` | precondition ou usage refuse : **racine absente**, **combinaison racine et actes systeme interdite**, Python trop ancien, checkout incomplet, racine inaccessible, **privileges insuffisants en mode reel** (PC6), **compte non connectable irresolvable en mode reel** (PC8), **cible destructive hors de la racine resolue** (§8.3quater), lien d'activation present a la desinstallation | **non**, message nomme |
| `1` | panne en cours d'operation | **oui**, avec sa trace |

**Preserver n'est pas echouer.** Une installation qui trouve `boilerack.toml` ou
`boilerack.env` deja presents les preserve, le **signale**, et rend `0`. Une
desinstallation qui ne trouve rien a supprimer rend `0`.

Les messages doivent nommer **ce qui a ete fait**, **ce qui a ete preserve** et
**ce qui reste a faire par l'humain**. Ils ne doivent jamais laisser entendre que
le service est actif, demarre ou qualifie (§6).

---

## 17. Proprietes a verrouiller

Le lot d'implementation devra prouver, au minimum, les proprietes suivantes. Les
noms de tests ne sont pas fixes ici ; les proprietes le sont.

| # | Propriete |
|---|---|
| P1 | Une installation dans une racine vide produit l'arborescence attendue : les quatre emplacements de §7.1 et les trois repertoires de §7.2 |
| P2 | Le **contenu** d'un `boilerack.toml` existant est **byte-identique** avant et apres, y compris lors d'une reinstallation ; ses **metadonnees sont reappliquees** selon §7 |
| P3 | Le **contenu** d'un `boilerack.env` existant est **byte-identique** avant et apres, y compris lors d'une reinstallation ; ses **metadonnees sont reappliquees** selon §7 |
| P4 | Le `boilerack.env` initial ne definit **aucune** variable, cite `BOILERACK_MQTT_PASSWORD` en commentaire, et ne contient aucune valeur ressemblant a un secret |
| P5 | Une seconde installation reussit et est idempotente : venv recree, unite redeposee, **contenus** de la configuration et du secret preserves, **metadonnees reappliquees**, identite et repertoires retrouves |
| P6 | L'unite installee est **octet pour octet** identique a `systemd/boilerack.service` du checkout ; la configuration initiale est **octet pour octet** identique a `docs/boilerack.example.toml` |
| P7 | Un interpreteur anterieur a 3.11 provoque un echec explicite au code contracte, **avant tout effet** sur la racine |
| P8 | Le mode synthetique n'execute ni creation d'utilisateur, ni creation de groupe, ni changement de proprietaire, ni changement de mode : il les **declare** |
| P9 | L'installation n'execute **jamais** `systemctl`, dans aucun mode : ni `daemon-reload`, ni `enable`, ni `start`. Les trois sont **restitues** |
| P10 | La desinstallation supprime le venv, `/opt/boilerack` et l'unite, et preserve `boilerack.toml`, `boilerack.env`, `/etc/boilerack/`, l'utilisateur et le groupe |
| P11 | La desinstallation **refuse**, au code contracte et **sans rien supprimer**, si le lien d'activation existe sous la racine |
| P12 | L'etape venv est la **derniere etape destructive** : un echec de cette etape laisse la configuration, le secret, l'unite et les **metadonnees hors venv** deja en place. Les metadonnees du venv sont posees **apres** sa creation reussie, jamais avant |
| P13 | Un checkout incomplet — l'un des trois fichiers requis manquant — provoque un echec de precondition **avant tout effet** |
| P14 | **Aucun module du graphe d'import d'execution n'importe l'installateur** : le service n'embarque pas la logique qui ecrit sur le disque |
| P15 | **Aucune invocation sans racine explicite ne produit d'effet** : l'absence de racine est refusee avant tout effet (PC1) |
| P16 | **Les deux combinaisons hybrides sont refusees avant tout effet** (PC2), la classification portant sur la **racine resolue** (§8.1bis) : une racine resolue **designant** la racine du systeme avec actes systeme fermes, et une racine resolue **ne la designant pas** avec actes systeme ouverts. Une racine ecrite autrement mais **designant** la racine du systeme — `/.`, `/opt/..`, lien symbolique — est classee **reelle**, donc refusee avec actes fermes |
| P17 | Les modes contractes pour **tous** les emplacements de §7.2 sont **numeriques et interpretables** ; les deux emplacements du venv portent `0755` et le proprietaire `root` |
| P18 | **Aucune normalisation recursive** : la pose des metadonnees ne touche que les emplacements nommes, et le contenu interne du venv conserve les modes produits par `venv` et `pip` |
| P19 | L'etape venv s'execute sous `umask` `0022`, et le `umask` anterieur est **restaure**, y compris lorsque l'etape echoue |
| P20 | Les actes d'**identite** precedent tout acte d'**appropriation** qui reference cette identite ; une creation necessaire qui echoue est une panne explicite, jamais ignoree |
| P21 | En mode reel : des privileges insuffisants (PC6) et un compte non connectable irresolvable (PC8) sont refuses **avant tout effet** |
| P22 | **Aucune suppression ne porte hors de la racine resolue** (§8.3quater) : une cible dont le chemin resolu n'est pas un descendant strict de la racine resolue est refusee, et rien n'est supprime |

Les proprietes P1 a P10 correspondent, dans l'ordre, aux dix proprietes exigees
par le cadrage du lot. P11 a P16 sont des ajouts derives de l'instruction du
contrat et de son audit : refus de securite (§12.3), ordre des effets et pose des
metadonnees en deux temps (§7.3, §8.3), validation du checkout (§5), separation
entre le programme et son installateur (§14), et surete de la racine et des
combinaisons de modes (§8.1).

P17 a P22 sont les proprietes du **chantier de convergence du mode reel** : sans
elles, le chemin reel restait non convergent — modes non applicables (P17),
portee indeterminee (P18), arbre du venv dependant du `umask` de l'operateur
(P19), ordre de l'identite non garanti (P20), preconditions de privilege et de
compte non exigibles (P21), suppression pouvant porter hors de la racine (P22).

**P15 et P16 sont des proprietes de surete.** Elles ne decrivent pas ce que
l'installateur fait, mais ce qu'il **refuse de faire**, et leur violation ouvre
la voie a une destruction non demandee sur la machine hote.

---

## 18. Mutations discriminantes

Aucun test n'est ecrit a ce stade. **Aucune mutation n'est declaree tuee.**

| # | Mutation | Propriete visee |
|---|---|---|
| M1 | Un repertoire de §7 n'est pas cree | P1 |
| M2 | Le **contenu** de `boilerack.toml` est ecrit inconditionnellement | P2 |
| M3 | Le **contenu** de `boilerack.env` est ecrit inconditionnellement | P3 |
| M4 | Le modele de `boilerack.env` porte une affectation **active** de `BOILERACK_MQTT_PASSWORD` | P4 |
| M5 | La seconde installation echoue lorsque le venv existe deja | P5 |
| M6 | L'unite est deposee avec une modification — substitution, reindentation, ligne finale retiree | P6 |
| M7 | Le controle de version de Python est deplace **apres** la creation des repertoires | P7 |
| M8 | Le mode synthetique execute reellement la creation de l'utilisateur, ou un changement de proprietaire | P8 |
| M9 | L'installateur execute `systemctl enable`, ou `start`, ou `daemon-reload` | P9 |
| M10 | La desinstallation supprime `/etc/boilerack/` | P10 |
| M11 | La desinstallation supprime l'utilisateur ou le groupe `boilerack` | P10 |
| M12 | La desinstallation procede malgre la presence du lien d'activation | P11 |
| M13 | L'etape venv est deplacee **avant** le depot de la configuration et du secret | P12 |
| M14 | Les preconditions acceptent un checkout auquel il manque un des trois fichiers requis | P13 |
| M15 | Un module du graphe d'execution importe l'installateur | P14 |
| M16 | La restitution des actes humains restants omet `daemon-reload` | P9 |
| M17 | La preservation du contenu d'un fichier existant est requalifiee en **echec** au lieu d'un succes signale | P2, P3 |
| M18 | Les metadonnees du venv sont posees **avant** la creation du venv — groupes A et B fusionnes en un seul, place avant l'etape 8 | P12, P1 |
| M19 | Les metadonnees d'un `boilerack.toml` ou d'un `boilerack.env` **existant** ne sont pas reappliquees : la preservation du contenu est etendue a tort aux proprietaires et aux modes | P2, P3, P5 |
| M20 | La racine retrouve une **valeur par defaut**, `/` ou toute autre | P15 |
| M21 | Une racine **designant** la racine du systeme est acceptee avec les actes systeme **fermes** | P16 |
| M22 | Une racine **ne designant pas** la racine du systeme est acceptee avec les actes systeme **ouverts** | P16 |
| M23 | La classification porte sur la **representation textuelle** de la racine au lieu de sa **resolution** : une racine dont la resolution designe la racine du systeme — `/.`, `/opt/..`, lien symbolique vers la racine — est acceptee comme **synthetique** avec les actes systeme fermes | P16 |
| M24 | La classification compare la racine resolue a la **chaine** `/` au lieu de tester l'**identite du repertoire designe** | P16 |
| M25 | Un mode du groupe B redevient non numerique, ou prend une valeur qui prive les « autres » de lecture ou d'execution — `0750`, `0700`, `0640` | P17 |
| M26 | Les metadonnees sont posees **recursivement** sur l'arbre du venv | P18 |
| M27 | Le `umask` n'est pas fixe pendant l'etape venv, ou n'est **pas restaure** apres un echec de cette etape | P19 |
| M28 | Les actes d'identite sont deplaces **apres** les actes d'appropriation, ou l'echec d'une creation necessaire est ignore | P20 |
| M29 | PC6 ou PC8 est evaluee **apres** un premier effet, ou n'est pas evaluee du tout | P21 |
| M30 | La garde destructive est absente, ou compare des **chaines** au lieu de prouver l'appartenance au sous-arbre, ou admet l'**egalite** avec la racine | P22 |

M17 est la plus insidieuse des mutations de contenu : elle ne perd aucune donnee,
mais elle transforme une reinstallation normale en echec apparent, et pousserait
un exploitant a « reparer » en supprimant sa configuration.

**M19 est la mutation miroir de M2 et M3**, et elle est indispensable : sans elle,
un installateur qui ne reapplique jamais aucune metadonnee passerait P2 et P3.
Les tests futurs doivent donc distinguer deux cas et les opposer — **contenu
existant modifie : violation** · **metadonnees reappliquees : comportement
contracte**.

**M20 a M24 sont les mutations de surete.** Elles reintroduisent exactement les
defauts corriges en §8.1 et §8.1bis : un chemin par lequel une invocation
incomplete, incoherente ou **ecrite autrement** atteindrait le systeme hote et
detruirait `/opt/boilerack/venv`.

**M25 a M30 sont les mutations de convergence du mode reel.** Trois d'entre elles
meritent un mot. **M25** couvre le defaut d'origine — un mode inapplicable — mais
aussi le defaut symetrique et plus insidieux : un mode parfaitement numerique qui
prive le service de l'acces que C12 §12 lui garantit. **M27** doit etre eprouvee
**sur le chemin d'echec** autant que sur le chemin nominal : un `umask` restaure
seulement en cas de succes laisserait le processus dans un etat modifie apres une
panne. **M30** distingue trois defaillances : garde absente, garde textuelle, et
garde admettant l'egalite avec la racine — cette derniere autoriserait la
suppression de la racine elle-meme.

**M23 et M24 sont les mutations d'alias**, et elles sont distinctes de M21. M21
suppose une racine ecrite `/` ; M23 et M24 supposent une racine **ecrite
autrement** mais **designant** la racine du systeme. Un installateur qui
comparerait des chaines tuerait M21 en survivant a M23 et M24 : c'est precisement
l'etat que §8.1bis interdit. M24 discrimine le cas plus fin ou la resolution est
bien effectuee mais son resultat est compare comme du texte, ce qui laisse passer
les representations qui survivent a la canonicalisation.

---

## 19. Validation hors ligne — ce qui doit etre prouve

Toutes ces preuves sont realisables sans machine cible, sans privilege, sans
`systemctl`, sans broker et sans chaudiere.

**Contre une racine synthetique** : l'arborescence complete de §7 · la copie octet
pour octet de l'unite et de la configuration initiale · le contenu du
`boilerack.env` initial · la preservation du **contenu** de la configuration et du
secret · la **reapplication de leurs metadonnees** · l'idempotence d'une seconde
installation · l'ordre des effets et la pose des metadonnees en deux temps · le
**refus des invocations sans racine et des combinaisons interdites** · la
desinstallation et son refus de securite · les codes de sortie et les messages ·
les echecs de precondition · le contenu des deux listes d'actes restitues ·
**le caractere numerique et la valeur des modes contractes** · **l'absence de
normalisation recursive** · **le `umask` de l'etape venv et sa restauration, y
compris apres echec** · **l'ordre identite puis appropriation** · **les refus de
PC6 et PC8 par substitution de predicat** · **le refus d'une cible destructive
hors de la racine resolue**.

**Sur le paquet** : que l'installation du paquet dans un venv produit reellement
la commande `boilerack` — deja acquis par C12, reconduit ici sous racine
synthetique. **Cette preuve n'est pas hors ligne** (§15.2).

**Sur la coherence documentaire** : le contrat, le gabarit d'unite, l'exemple de
configuration et la documentation d'exploitation ne se contredisent sur aucun
chemin, aucun mode, aucun proprietaire, aucun code de sortie.

**Sur la non-regression** : le chargeur de configuration ne gagne aucun
emplacement par defaut (B8) · aucune ecriture disque n'est introduite dans le
graphe d'execution (P14) · la suite existante passe inchangee.

---

## 20. Frontiere terrain — ce qui n'est pas prouve

A ecrire tel quel, sans attenuation. **C13, hors terrain, NE PROUVE PAS** :

- qu'un `useradd` reel cree l'utilisateur attendu, avec les droits attendus ;
- que l'executable resolu par PC8 rende effectivement le compte non connectable ;
- que `euid == 0` suffise reellement sur la cible : PC6 prouve le **refus** en
  son absence, jamais la **suffisance** des privileges en sa presence ;
- qu'un `chown` reel s'applique ;
- que les modes reels sous la cible Linux sont ceux contractes en §7 ;
- que l'arbre produit par `venv` et `pip` sous `umask` `0022` soit effectivement
  traversable et lisible par l'identite du service ;
- que `/etc/boilerack` en `0750 root:boilerack` laisse effectivement le service
  lire ses deux fichiers ;
- qu'un systemd reel charge l'unite deposee ;
- que `daemon-reload` la prenne en compte ;
- que `enable` et `start` reussissent ;
- que `journald` capture les lignes emises ;
- que l'index de paquets soit joignable depuis la cible ;
- que le venv construit sur la cible produise une commande fonctionnelle ;
- que le service demarre, lise, publie et s'arrete ;
- le comportement contre un broker, un `vclient`, un `vcontrold`, une chaudiere
  ou un Home Assistant reels ;
- **qu'une racine classee synthetique par §8.1bis ne donne effectivement pas
  acces au systeme reel** : la resolution de chemin traite les alias de chemin,
  jamais les alias de **montage** ou de **configuration systeme** — `bind mount`,
  espace de noms de montage, `chroot` et equivalents noyau restent hors de sa
  portee, et hors de toute detection portable ;
- **la qualite reelle de l'installation sur un Raspberry Pi.**

Ces preuves appartiennent a une **qualification terrain ulterieure**, distincte de
C13 et non planifiee par lui.

**Aucune conformite terrain n'est revendiquee par C13.** Un installateur valide
contre une racine synthetique n'est pas un installateur qui fonctionne.

---

## 21. Sobriete — ce que C13 ne construit pas

Architecture de plugin · abstraction multiplateforme generale · framework
d'installation · **moteur de modes** · moteur de transaction · rollback
sophistique · journal de reprise · verrou d'installation · gestion de versions
installees · comparaison de numeros de version · dependance externe
d'installation.

Les deux modes de §8.1 ne constituent pas un moteur de modes : ce sont **deux
combinaisons enumerees** d'entrees deja existantes, sans etat, sans strategie et
sans extension prevue. Trois autres combinaisons sont refusees, et la liste est
close.

**L'installateur n'utilise que la bibliotheque standard.** Cette contrainte n'est
pas esthetique : sur la cible, il s'execute **avant** que le venv existe, donc
avant que la moindre dependance puisse etre installee. Toute dependance externe
rendrait l'installateur ininstallable.

C13 reste un installateur **specifique a Boilerack**. Il n'a pas vocation a
installer autre chose, et rien dans sa forme ne doit suggerer le contraire.

---

## 22. Risques et inconnues

| # | Risque ou inconnue | Portee |
|---|---|---|
| R1 | **Illusion d'installation** : une preuve contre une racine synthetique n'est pas une installation qui marche. **Risque principal du lot** | §20 |
| R2 | **Derive vers le terrain** : `useradd`, `chown` et `systemctl` sont adjacents et tentants. La frontiere doit rester fermee et testee | §8.2, §13 |
| R3 | **Ecrasement du contenu de la configuration ou du secret** lors d'une reinstallation : le pire dommage possible | §9.2, M2, M3 |
| R4 | **Perte du venv** en cas d'echec de la derniere etape destructive : risque assume, mitige par l'ordre, non supprime | §11.2 |
| R5 | Tentation d'introduire un numero de version, un tag ou une release parce qu'une mise a jour en aurait besoin — hors perimetre par arbitrage B | §3 |
| R6 | Tentation d'ajouter une option d'ecrasement « pour reparer » : ce serait une violation de §9.2 | §9.2 |
| R7 | **Destruction non demandee sur la machine hote** : toute reintroduction d'une racine par defaut, toute tolerance d'une combinaison hybride, ou **toute classification fondee sur l'ecriture de la racine plutot que sur sa resolution**, rouvre le chemin par lequel `/opt/boilerack/venv` serait detruit sans decision explicite | §8.1, §8.1bis, P15, P16, M20 a M24 |
| R8 | Tentation d'ajouter un mode « preserve metadata » pour ne pas normaliser les permissions d'un exploitant : ce serait une violation de §9.1 | §9.1 |
| I1 | Python de la cible : rien ne garantit qu'un `>=3.11` y soit disponible. Des images encore repandues livrent un interpreteur anterieur | PC3 |
| I2 | Le message d'echec de PC3 peut ne jamais etre atteint si le code de l'installateur ne se lit pas sous l'interpreteur ancien | §5 |
| I3 | Joignabilite de l'index de paquets depuis la cible | PC7, §15.2 |
| I4 | Non-relogeabilite d'un venv POSIX : **non mesuree** depuis la machine de developpement | §11.2 |
| I5 | Le nom exact du lien d'activation depend de la cible d'installation declaree dans l'unite ; `multi-user.target.wants` est celui du gabarit actuel | §12.3 |
| I6 | Coordination d'une reinstallation avec un service en fonctionnement : hors perimetre par arbitrage D | §11.2 |
| I7 | **Alias de montage** : `bind mount`, espace de noms, `chroot` et equivalents noyau peuvent faire qu'une racine resolue distincte donne acces au systeme reel. §8.1bis **ne le detecte pas** et ne le pretend pas | §8.1bis, §20 |
| I8 | La resolution de certaines representations de la racine depend de la plateforme cible. Une representation **non mesuree depuis la machine de developpement** peut survivre a la canonicalisation sous une forme textuelle differente tout en designant la racine du systeme : c'est la raison pour laquelle §8.1bis exige un test d'**identite du repertoire designe** et non une comparaison de chaines | §8.1bis, M24 |

---

## 23. Ce que C13 ne fait pas

Aucun changement du programme, de sa CLI, de son runtime, de ses signaux, de sa
configuration ou de ses dependances d'execution · aucune unite activee ou
demarree · aucun `systemctl` execute · aucun utilisateur systeme cree par les
preuves du lot · aucun deploiement reel · aucune release, aucun tag, aucun
changement de version · aucune modification de C9, C10, C11 ou C12.

**AUCUNE CONFORMITE TERRAIN N'EST REVENDIQUEE.** Rien n'a ete eprouve contre une
machine cible, un systemd, un broker, un `vcontrold` ou une chaudiere reels.

---

## 24. Renvois

`c8-composition-root.md` — racine de composition, et report explicite du « mode de
deploiement » · `c9-process-lifecycle.md` — signaux et codes `0` et `130` ·
`c10-user-interface.md` — commande installee, `--config` obligatoire sans
emplacement par defaut, secret par variable d'environnement, codes `2` et `1` ·
`c11-presence-recovery.md` — survie a la perte MQTT · `c12-service-contract.md` —
**autorite directe de ce lot** : emplacements, identite, unite, `EnvironmentFile`
strict, permissions, et renvoi explicite de l'installateur a un chantier distinct.

**Chantiers futurs, hors C13** : qualification terrain — installation reelle sur
une cible, activation du service, mesure de l'arret propre, durcissement systemd,
et validation contre un broker, un `vcontrold` et une chaudiere reels · puis,
eventuellement, publication et versionnement.
