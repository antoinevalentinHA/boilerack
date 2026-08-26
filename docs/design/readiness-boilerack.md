# Readiness Boilerack — passe finale

> **Version 2**, après audit. Le sort du `stash` W3 est consigné explicitement
> comme **acte humain déjà exécuté**, et non comme une simple absence ; les
> superlatifs qui ordonnaient les finitions sans le démontrer sont retirés. Trois
> nuances mineures accompagnent. **La conclusion générale est inchangée.**
>
> **Version 1.** Constat de readiness, établi **en lecture seule** à partir de
> `main` uniquement. Aucun développement, aucun terrain, aucun refactor, aucune
> correction. Il **constate**, il ne répare pas.

---

## 1. Objet et frontières

Ce document répond à cinq questions : reste-t-il des chantiers ou des artefacts
temporaires ; le dépôt est-il cohérent entre docs, code, tests et `README` ;
quelles dettes sont **réellement** bloquantes ; l'état de publication déclaré
est-il exact ; que reste-t-il avant de considérer Boilerack terminé proprement.

Il **ne corrige rien** de ce qu'il relève, n'amende aucun contrat, ne rouvre
aucun lot clos, et n'ouvre aucun développement.

**`W4-F2` demeure clos `NON QUALIFIABLE`** ; `W4-F3` demeure **inadmissible** ;
Précondition 9 / §11.2 demeure **`NON DONNÉE`**.

---

## 2. Le point de mesure

| | |
|---|---|
| `main` | `0fccfa5bf6a8e1220f161a2fef88566ca371a853` |
| `origin/main` | **identique** |
| Arbre | **propre** |
| Fichiers suivis | **151** |
| Modules source | 43 |
| Fichiers de test | 46, portant **1 348** fonctions |
| Documents de conception | **40** sur `main` — le présent constat, non suivi, serait le 41ᵉ |
| CI sur ce commit | **verte** — `3.11`, `3.12`, `3.13` |

---

## 3. Chantiers et artefacts — ce qui reste

### 3.1 Rien ne traîne dans le dépôt publié

| Contrôle | Résultat |
|---|---|
| `stash` | **0** — et ce zéro **résulte d'un acte**, voir §3.2 |
| Tags | **0** |
| Branches **distantes** | **une seule : `main`** |
| Fichiers non suivis | **aucun** |
| Artefacts temporaires **suivis** | **aucun** — ni `.pyc`, ni `.orig`, ni `.bak`, ni cache |
| `.gitignore` | couvre caches, build, environnements, `.env`, journaux |
| Marqueurs `TODO` / `FIXME` / `WIP` / `HACK` dans `src/` et `tests/` | **aucun** |

> **Pour un tiers qui clone, le dépôt ne présente aucun résidu.**

### 3.2 Le `stash` W3 — supprimé, et il faut le dire ainsi

> **Le zéro du tableau ci-dessus n'est pas un état de fait ancien : c'est le
> résultat d'une suppression délibérée, déjà exécutée.**

| | |
|---|---|
| Objet supprimé | `daf3ed1e4f088e01767275fc89cf01a4587c2988` |
| Preuve préalable | `docs/design/w3-stash-cadrage.md`, **intégré par la PR #64** — sept fichiers comparés à `main`, 54 lignes propres lues une à une, verdict *« intégralement subsumé par `main` »*, encore pertinent **aucun**, perdu **aucun** |
| Acte | `git stash drop stash@{0}`, exécuté **après** le merge de la PR #64, sur **arbitrage humain explicite**, et après vérification d'identité de l'objet et des préconditions |
| Portée | un `stash` est **local** : il n'a jamais été poussé, et **n'a donc jamais été un artefact publié** |

> **La distinction compte pour un lecteur.** Ce n'est pas un résidu qui aurait
> traîné dans le dépôt : c'était un objet de poste, instruit par un lot dont la
> preuve est publique, puis supprimé par une décision consignée.

### 3.3 Une réserve, strictement locale

**Huit branches locales** subsistent en plus de `main`, dont sept marquées
`[gone]` — leur distante a été supprimée. **Les huit sont fusionnées dans
`main`**, écart mesuré **zéro commit** pour chacune.

| Branche | État |
|---|---|
| `docs/w4c-terrain-closure` · `docs/w4c-terrain-qualification-erratum` · `docs/w4e-composition-activation-contract` · `docs/w4f-write-sovereignty-framing` | fusionnées, distante absente |
| `feat/w3-transaction-runtime-wiring` · `feat/w4b-vclient-write-adapter` · `feat/w4d-production-profile` · `feat/w4e2-transaction-composition` | fusionnées |

> **C'est un item d'hygiène de poste, pas de dépôt.** Ces références n'existent
> que sur la machine ; un clone n'en voit aucune. **Non bloquant.**

---

## 4. Cohérence docs / code / tests / `README`

### 4.1 Le corpus couvre le code

Les contrats `C2` à `C13` sont tous présents, ainsi que les lots `W0`, `W1`,
`W2` et la famille `W4`. Les modules qu'ils décrivent existent. Aucun document ne
décrit un composant absent ; aucun composant notable n'est sans document.

> **Une précision, pour ne pas induire en erreur : il n'existe pas de contrat de
> lot `W3` autonome.** Le seul fichier `w3-*` est `w3-stash-cadrage.md`, qui
> traite du sort d'un `stash` — ce n'est pas un contrat de lot. Le câblage dit
> « W3 » est **couvert par d'autres documents** qui le nomment : `W1`, `W2`,
> `w4a-vclient-write-adapter.md` et `w4e-composition-activation.md`. **Ce n'est
> pas une lacune constatée ici**, mais une numérotation qu'un lecteur pourrait
> lire comme un trou.

### 4.2 Références pendantes — recherche systématique, **aucune**

Toutes les chaînes de la forme `"…​.py"` des tests et tous les noms de documents
cités dans `docs/design/` et le `README` ont été confrontés au dépôt. **Deux
candidats sont ressortis, tous deux faux positifs :**

| Candidat | Nature réelle |
|---|---|
| `intrus.py` | **clé d'un dictionnaire en mémoire** passé à un helper de test, jamais un chemin |
| `mqtt.md` | **`A5`**, document du dépôt `arsenal`, cité avec son chemin externe complet |

**Aucune référence pendante n'a été trouvée.**

> **Une réserve de méthode, à ne pas taire.** Un audit antérieur a mentionné un
> « constat incident sur une référence pendante dans `test_transaction_wiring.py` ».
> **Ce constat ne m'a jamais été transmis**, et rien de ce que ce contrôle a
> examiné n'y correspond. Il n'est donc **ni confirmé, ni infirmé** : il reste à
> produire par qui l'a relevé.

### 4.3 Le `README` — exact, avec une ambiguïté

Tout ce que le `README` référence existe : `docs/boilerack.example.toml`,
`docs/design/c10-user-interface.md`, `LICENSE`. Les codes de sortie, les clés de
configuration et la règle du mot de passe par variable d'environnement
correspondent au code.

> **Une phrase peut être mal lue, et il faut le dire.** Le `README` énonce en
> §Installation : *« Rien n'a été éprouvé contre un broker, un `vcontrold` ou une
> chaudière réels »* — et en §Compatibilité : *« **Vérifié** sur une seule
> installation : régulation `VScotHO1` (`20CB`), protocole `P300` … »*.
>
> Les deux sont vrais et ne se contredisent pas : le second décrit ce que la
> **caractérisation** a couvert, non un essai de Boilerack. Mais un lecteur
> pressé peut lire « vérifié » comme « essayé ». **L'ambiguïté est réelle et se
> lève d'une incise** ; ce document ne la lève pas.

---

## 5. Dettes — ce qui est bloquant, et ce qui ne l'est pas

### 5.1 Non bloquantes, parce que nommées, bornées et gardées

| Dette | Pourquoi elle ne bloque pas |
|---|---|
| `src/boilerack/_legacy/primitives.py`, déclaré **PROVISOIRE** | extrait du pont historique, conservé pour caractérisation, et le module distingue lui-même **deux régimes** : une première section *« copiée LITTÉRALEMENT, y compris ses défauts et ses effets de bord »*, et une seconde d'**extractions mécaniques** — *« le corps est reproduit à l'identique ; seule l'enveloppe … est nouvelle »*. **Aucun module de `src/` ne l'importe** — seuls les tests de `tests/characterization/`. Un test garde explicitement sa non-réutilisation dans le code de production |
| Dettes contractuelles déclarées — `c7` §4.3 report hors v1 des mesures brûleur, et celles de `c10`, `c7c3a`, `w1`, `w2`, `w4a`, `w4e` | **toutes consignées** dans leur contrat, avec leur motif |
| Les dix inconnues de `W4-F2` — maillon 2, `H1`, `H2`, `H6` (a) t2 / (b) / (c), `U-2`, `U-3`, `U-7`, `A6` | **listées dans le lot de clôture**, `W4-F2` étant clos `NON QUALIFIABLE` |

### 5.2 Un manque d'outillage, non bloquant mais notable

La CI **ne lance que `pytest`**, et l'extra `dev` ne déclare que `pytest>=8` :
**aucun linter, aucun vérificateur de types**. Or le code porte des
constructions écrites *pour* un vérificateur — `if TYPE_CHECKING:` avec le
commentaire *« réservé à la vérification de types »*.

> **L'intention est là, l'outil n'y est pas.** Ce n'est pas un défaut de
> correction — 1 348 tests couvrent le comportement — mais une **asymétrie**
> entre ce que le code annonce et ce que la chaîne vérifie.

### 5.3 Le corpus est indécouvrable

**40 documents** sous `docs/design/` sur `main`, nommés `c2-…`, `w4f2-…`. Le
`README` en cite **un seul**. **Il n'existe aucun index** — ni `docs/README.md`, ni
`docs/design/README.md`.

Conséquence pour un tiers : il voit quarante fichiers sans ordre de lecture, sans
savoir ce que sont `C`, `W`, `T0` ou `H3`, **et sans jamais apprendre que `W4-F2`
est clos** ni pourquoi. Le travail le plus considérable du dépôt est celui qu'on
ne peut pas aborder.

**Ce que cet item a de propre**, sans le comparer aux autres : il porte sur une
**absence de point d'entrée**, là où l'ambiguïté du §4.3 porte sur la **lecture
d'une phrase présente**. Les deux se traitent par de la rédaction, sans
développement.

> **Aucun ordre de priorité n'est établi entre eux.** Ce constat n'a pas les
> éléments pour le démontrer — il faudrait connaître l'usage visé et le lecteur
> attendu — et il ne l'affirmera donc pas.

---

## 6. État de publication et d'utilisabilité — déclaré, et exact

| Ce que le dépôt déclare | Vérification |
|---|---|
| *« État : en construction. Rien n'est publiable ni utilisable à ce stade »* | **exact** |
| *« Aucune prerelease n'a été diffusée »* | **exact** — **0 tag**, version dynamique |
| *« Rien n'a été éprouvé contre un broker, un `vcontrold` ou une chaudière réels »* | **exact** — `W4-F2` clos `NON QUALIFIABLE`, aucun terrain |
| Gabarit systemd : *« GABARIT, PAS UNE UNITÉ INSTALLÉE »* | **exact**, auto-déclaré en tête |
| Surface transactionnelle **sans autorité**, `false` | **exact** — `TransactionSurfaceConfig.enabled: bool = False`, défaut fermé, gardé par des tests nommés : autorité absente, autorité fausse, autorité vraie, table absente |

> **Le dépôt ne promet rien qu'il ne tienne.** C'est le point le plus solide de
> cette passe : la posture publique et l'état réel coïncident.

---

## 7. Ce qui reste avant « terminé proprement »

Deux objectifs distincts, qu'il ne faut pas confondre.

### 7.1 Pour un dépôt exemplaire, **non déployé**

| # | Item | Nature | Bloquant |
|---|---|---|---|
| 1 | **un index du corpus** — ordre de lecture, ce que sont `C` / `W`, et l'état terminal de `W4-F2` | rédaction, **aucun code** | non — mais c'est ce qui sépare aujourd'hui un tiers du corpus (§5.3) |
| 2 | **lever l'ambiguïté « vérifié »** du `README` | une incise | non |
| 3 | **outiller lint et types** en CI | **pas seulement de la configuration** : brancher un vérificateur sur 43 modules fait remonter un état initial dont le traitement n'est pas borné d'avance, et qui peut appeler des annotations ou des ajustements. L'ampleur n'est **pas évaluée ici** | non |
| 4 | **purger les huit branches locales fusionnées** | hygiène de poste | non |

**Rien d'autre.** Aucun développement, aucun refactor, aucune correction de
comportement n'est requis par ce constat.

### 7.2 Pour un produit **utilisable**

`T0` et ses neuf préconditions, puis `T1` / `T2`, puis `W4-F3`. **Hors de portée
du dépôt**, et `W4-F2` est clos : cet objectif relèverait d'une décision de
gouvernance distincte, dont le cadrage de clôture a déjà chiffré le coût.

---

## 8. Verdict

> **Boilerack est prêt en tant que dépôt.** Le code est bâti et testé, la CI est
> verte, la posture publique est exacte, aucune référence n'est pendante, aucune
> dette n'est masquée, et rien ne traîne dans ce qui est publié.

**Quatre finitions subsistent**, énumérées au §7.1 : l'absence d'index du corpus,
l'ambiguïté du `README`, l'outillage lint et types, et les branches locales
fusionnées. **Aucune ne demande de développement, de refactor ni de correction de
comportement.** Deux relèvent de la rédaction, une de l'outillage — dont
l'ampleur n'est pas évaluée ici — et une de l'hygiène de poste.

**Ce constat ne les ordonne pas, et ne les exécute pas.**

---

## 9. Ce que ce document ne fait pas

Il ne corrige rien · il n'écrit aucun index · il ne touche ni au `README`, ni à
la CI, ni aux branches locales · il ne modifie aucun contrat ni aucun code · il
ne rouvre ni `W4-F2`, ni aucun lot clos · il n'ouvre ni `T0`, ni `T1` / `T2` · il
n'autorise aucun terrain, aucune mutation · il ne confirme ni n'infirme le
constat incident mentionné au §4.2, qui ne lui a pas été transmis.

---

## 10. Historique de révision

| Version | Contenu |
|---|---|
| **1** | Passe de readiness initiale, sur `main` `0fccfa5b` |
| **2** | Audit. **R1** : nouveau §3.2 consignant la suppression du `stash` W3 comme **acte humain exécuté** après la PR #64, et rappelant qu'un `stash` n'a jamais été un artefact publié ; l'ancien §3.2 devient §3.3. **R2** : retrait des superlatifs de §5.3 et §8, aucun ordre de priorité n'étant démontrable ici ; la colonne « bloquant » du §7.1 est rendue factuelle. Nuances : les **deux régimes** de `_legacy/primitives.py` distingués ; absence de contrat de lot `W3` autonome précisée (§4.1) ; lint et types ne sont plus réduits à de la configuration. **Conclusion générale inchangée** |
