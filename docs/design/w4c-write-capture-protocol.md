# W4-C — Protocole de capture de l'écriture `vclient`

> **Lot W4-C — opératoire. Version 4**, après **qualification réelle de
> l'installation**. Les V1 à V3 ont été écrites sans accès au terrain ; la
> qualification a confirmé la méthode et révélé trois points qu'un document seul
> ne pouvait pas voir : le superviseur n'est pas neutralisé par l'arrêt de son
> seul timer (§8.1) ; une lecture du datapoint retenu restitue une représentation
> **décimale** alors que son contrat exige un **entier strict**, ce qui rendait la
> consigne « verbatim » inapplicable (§11.3) ; et la comparaison de deux lectures
> demandait une définition, faute de quoi elle était structurellement impossible
> (§12.3). La **V4.1** corrige trois défauts relevés par l'audit indépendant de
> la V4 : la règle de concordance ne couvrait que les deux formes d'une même
> lecture, et non les relectures ultérieures (§12.3.2) ; le journal du démon
> était présenté à tort comme preuve de neutralisation du superviseur, alors
> qu'un cycle en attente interne n'y laisse aucune trace tout en restant armé
> (§9.1) ; et la reprise du pont était établie sans preuve qu'il **publie** de
> nouveau (§13.1). La méthode, la séquence et la cardinalité sont
> **inchangées** depuis la V1. Ce document ne livre aucune ligne de code et ne
> modifie aucun test. Il décrit une campagne de mesure à exécuter **une fois**,
> sur l'installation de référence, par l'exploitant.
>
> **La campagne a été exécutée le 22 août 2026.** Ses résultats sont au **§16**,
> qui clôt le lot. Les sections 1 à 15 restent le protocole tel qu'il a été écrit
> avant, et ne sont pas réécrites après coup. W4-C est clos ; **W4-D peut être
> ouvert, et ne l'est pas par ce document**.

---

## 1. Objet

C5 §12 pose le squelette d'un protocole de caractérisation de l'écriture,
« présenté pour mémoire, non exécuté, non demandé ». W4-A §19 énumère ce qu'une
telle campagne doit rapporter. Ce document **instancie** l'un avec l'autre, à la
lumière de faits qui n'étaient pas disponibles à la rédaction de C5 : le pont
historique dont descend Boilerack écrit sur cette chaudière depuis des mois,
**par le même transport que Boilerack** — `vclient` lancé en sous-processus.

Il en résulte une campagne beaucoup plus étroite que ce que C5 §12 laissait
craindre : il ne s'agit plus d'établir *si* une écriture est possible, ni *quel*
datapoint est sûr, mais uniquement de **regarder ce que la CLI répond** pendant
un geste déjà exécuté quotidiennement sans incident.

---

## 2. Ce que ce document ne fait pas

- Il n'autorise rien. L'exécution relève de l'exploitant, et de lui seul.
- Il ne modifie aucun contrat : ni W1, ni W2, ni W4-A. Il **ne modifie pas** non
  plus les huit éléments de C5 §12 : il en **dispositionne** un, le n° 8, par une
  note adjacente qui n'en réécrit pas le texte (C5 §12.9).
- Il n'ouvre pas la voie transactionnelle. L'activation relève de W4-E.
- Il ne consigne aucune constante de site — voir §4.
- Il ne prescrit **aucune valeur nouvelle** : la seule écriture prévue réécrit à
  l'identique la valeur déjà en place.

---

## 3. Autorités

| Réf | Document | Ce qu'il fixe |
|---|---|---|
| A1 | `c5-vclient-contract.md` §12 | squelette du protocole, critères d'abandon, retour arrière |
| A2 | `c5-vclient-contract.md` §11 | interdiction d'extrapoler de la lecture vers l'écriture |
| A3 | `w4a-vclient-write-adapter.md` §16 | inconnues I-1 à I-15 |
| A4 | `w4a-vclient-write-adapter.md` §19 | champs que W4-C **MUST** rapporter |
| A5 | `arsenal` — `00_documentation_arsenal/outils_externes/boiler_pi/mqtt.md` §5 | commandes d'écriture et de relecture, bornes, pas, tolérances |
| A6 | `boiler-bridge` — `boiler_mqtt.py` (dépôt privé) | forme d'invocation éprouvée en production |

A5 est public et citable. A6 est privé : ce document en reprend des **faits de
comportement**, jamais du code, conformément à la règle de reprise de
`provenance.md`.

---

## 4. Convention — constantes de site non consignées

`provenance.md` exclut par principe les hôtes, ports, chemins absolus, noms
d'interface et unités systemd. Ce document respecte cette règle : les éléments
propres au déploiement sont désignés par leur **rôle**, entre chevrons, et
l'exploitant leur substitue ses valeurs au moment d'exécuter.

| Marqueur | Rôle |
|---|---|
| `<hôte>` / `<port>` | point de contact du démon `vcontrold` |
| `<unité-pont>` | unité systemd du pont historique |
| `<timer-guard>` | timer systemd du superviseur local |
| `<atelier>` | répertoire de capture, créé pour l'occasion |

---

## 5. Acquis depuis W4-A — ce qui n'est plus une inconnue

W4-A a été écrit sous la contrainte de A2, qui interdit d'invoquer quoi que ce
soit d'extérieur à la campagne de lecture. L'expérience de production du pont
historique est précisément cet extérieur. Elle établit :

| Réf | Fait établi | Conséquence |
|---|---|---|
| E1 | Le pont historique écrit en lançant `vclient` en sous-processus | transport identique à celui de Boilerack ; l'expérience transfère |
| E2 | Quatre commandes d'écriture éprouvées : `setTempWWsoll`, `setTempRaumNorSollM1`, `setNiveauM1`, `setNeigungM1` | **I-2 est levée** — aucun datapoint n'est à deviner |
| E3 | Budget d'écriture de 5 s, suffisant depuis des mois | I-6 dimensionnée, à confirmer par mesure |
| E4 | Dispositif historique de confirmation : attente initiale de 1 s, sondages à 1 s, budget maximal de 10 s — il a suffi en production | **budget** de confirmation éprouvé ; **aucun délai physique de convergence n'a été mesuré** — I-7 reste entière |
| E5 | Bornes, pas et tolérances normatifs (A5 §5) | le profil réel est déterminé, hors W4-C |
| E6 | Le succès local n'est jamais conclusif : la vérité vient d'une relecture séparée | confirme la doctrine du cœur, ne la fonde pas |

**I-2 était l'inconnue la plus dangereuse de W4-A** — « écriture sur un datapoint
non vérifié ». Elle est levée par des mois d'usage, pas par un raisonnement.

---

## 6. Rendement attendu — liste fermée

Ce que la campagne lèvera, et **rien d'autre** :

| Réf | Inconnue | Levée ? |
|---|---|---|
| I-1 | syntaxe d'invocation ; `-J` produit-il une sortie exploitable en écriture | **oui** |
| I-3 | forme de `stdout` sur écriture acceptée | **oui** |
| I-4 | forme de `stderr` sur écriture | **oui** — premier flux jamais observé isolément |
| I-5 | code retour d'une écriture acceptée | **oui** |
| I-6 | durée réelle d'une écriture | **oui**, mesurée — sous la réserve d'horloge du §10 |
| I-14 | signatures de lecture réellement transposables à l'écriture | **partiellement** — voir §6.1 |

Ce qu'elle **ne lèvera pas**, et il faut le dire avant d'exécuter :

| Réf | Inconnue | Pourquoi elle résiste |
|---|---|---|
| I-7 | délai avant relecture fiable | une écriture **à l'identique** ne propage aucun changement : il n'y a rien à attendre, donc rien à chronométrer. E4 ne fournit qu'un **budget** qui a suffi, jamais un délai mesuré |
| I-8 | normalisation de la valeur | même raison, aggravée par le choix d'un datapoint entier (§7) |
| I-9 | comportement hors domaine | **jamais testé, jamais nécessaire** : Boilerack rejette avant émission, comme A5 §11 |
| I-10 | atomicité observable | non sollicitée par une écriture identique |
| I-11 | démon acceptant / chaudière appliquant autrement | indécidable sans changement de valeur |
| I-12 | signature d'un délai épuisé après émission | ne se provoque pas volontairement (§12) |
| I-13 | effet de l'expiration du budget local | idem — et propre au design de Boilerack, pas du père |
| I-15 | signature d'un démon injoignable en écriture | exigerait d'arrêter le démon : hors périmètre |

> **Conséquence à assumer.** I-9 restera inconnue **définitivement**, et c'est un
> choix, pas un manque. A5 §11 documente pourquoi une valeur hors bornes n'a
> jamais été émise : « bruit ACK non maîtrisé, comportement silencieux selon
> firmware ». Boilerack valide dans son cœur avant d'émettre. L'inconnue n'est
> pas à lever, elle est **contournée par construction** — ce qui est plus solide
> qu'une observation isolée.

### 6.1 I-14 — la frontière exacte, et ce qu'elle coûte

I-14 demande **quelles signatures observées en lecture sont réellement
transposables à l'écriture**. C'est l'inconnue qui fonde les deux interdictions
temporaires de W4-A §11.6 et W4-A §12.3. La campagne l'éclaire, mais ne la referme
pas — et la part qu'elle laisse ouverte a une conséquence directe qu'il faut
énoncer **avant** d'exécuter, pas découvrir au dépouillement.

La campagne produit **une seule** signature d'écriture : celle d'une écriture
**acceptée**. Elle rend donc comparables, entre lecture et écriture :

| Devient comparable | Contre quelle référence de lecture |
|---|---|
| structure de `stdout` en `-J` sur succès | fixture `read_ok_json` de C5 |
| présence ou absence d'un champ d'erreur en `-J` sur succès | idem |
| contenu de `stderr` sur succès | C5, flux séparés |
| code retour sur succès | C5 §3 |

Restent **non démontrées**, faute d'avoir été provoquées — et elles ne le seront
pas, §12 l'interdit :

- la signature d'un **démon injoignable** en écriture (I-15) ;
- la signature d'une commande **inconnue ou refusée** en écriture.

> **Conséquence, à porter au rapport.** W4-A §19 annonce que W4-C lève les
> interdictions de **W4-A** §9.1, §11.4 et §12.3 — les renvois de ce paragraphe
> désignent tous des sections de **W4-A**, jamais du présent document, qui porte
> par ailleurs des sections de mêmes numéros. **La campagne décrite ici ne les
> lève pas toutes.** Elle établit une signature de **succès local**, donc elle
> lève **W4-A §9.1** — l'interdiction de rendre `TransportStatus.OK`. Elle
> n'observe aucune défaillance d'écriture, donc :
>
> - **W4-A §11.6** — l'interdiction de `DAEMON_UNREACHABLE` — **reste en
>   vigueur**, sa levée exigeant explicitement « la même signature observée sur
>   une invocation d'écriture » ;
> - **W4-A §12.3** — l'interdiction de `UNKNOWN_COMMAND` — **reste en vigueur**.
>
> Ce n'est pas une lacune du protocole : lever ces deux-là supposerait de
> provoquer une panne ou d'émettre une commande invalide sur une installation en
> service. W4-D héritera donc de **deux statuts encore interdits**, et devra le
> constater plutôt que l'inférer.

---

## 7. Choix du datapoint

C5 §12.2 demande « le moins conséquent du profil, sur un paramètre dont une
variation transitoire serait sans effet ressenti ». Parmi les quatre rôles
inscriptibles établis par E2 :

| Rôle | Effet ressenti si divergence | Verdict de relecture |
|---|---|---|
| `setTempWWsoll` | eau chaude sanitaire — **actif toute l'année** | entier |
| `setTempRaumNorSollM1` | confort ambiant — ressenti immédiat | entier |
| `setNeigungM1` | courbe de chauffe — nul hors saison | flottant, tolérance ± 0,01 |
| `setNiveauM1` | courbe de chauffe — nul hors saison | **entier, égalité stricte** |

> **Datapoint retenu : `setNiveauM1`** (décalage de courbe).

Trois raisons, dans cet ordre :

1. **Hors saison de chauffe** (C5 §12.1), les paramètres de courbe du circuit M1
   n'ont aucun effet ressenti — contrairement à l'ECS, active toute l'année.
2. Son **contrat métier** est un **entier à égalité stricte** (A5 §5.3, tolérance
   de confirmation nulle). Le verdict de relecture est donc binaire : la valeur
   relue désigne le même entier, ou elle ne le désigne pas.
3. Choisir la pente aurait mêlé la question posée — *que répond la CLI ?* — à une
   question de sérialisation flottante (I-8) que la campagne ne peut de toute
   façon pas trancher. Un datapoint dont le **domaine** est entier **isole** la
   mesure.

> **Ce que « entier » ne veut pas dire.** Le contrat du datapoint est entier ;
> **sa restitution par la CLI ne l'est pas** — la qualification terrain a établi
> que la lecture rend une représentation **décimale**. Les deux faits coexistent
> sans se contredire : l'un décrit le domaine de valeurs, l'autre la forme d'un
> affichage. Ce qui en découle pour l'écriture — que la valeur émise soit
> l'entier, et non la chaîne lue — est tranché en **§11.3**, et le point 2
> ci-dessus doit se lire à cette lumière : le domaine est binaire, la
> représentation demande une règle, et cette règle existe.

---

## 8. Danger opératoire — le superviseur local

**Section sans équivalent dans C5 §12, qui ne pouvait pas la prévoir : sa
campagne était en lecture seule stricte.**

Le superviseur local s'exécute **toutes les 3 minutes**. À chaque cycle il sonde
le démon par un appel `vclient` **direct**, avec un budget de 5 s. En cas
d'échec de cette sonde :

1. il **redémarre l'unité du pont**, puis attend 90 s ;
2. il sonde à nouveau ; si l'échec persiste, il **redémarre la machine**.

Le chemin de redémarrage machine est donc à **deux échecs de sonde** de distance.
Une écriture qui mobiliserait la liaison Optolink assez longtemps pour faire
expirer deux sondes consécutives déclencherait un `reboot` **au milieu de la
campagne** — perdant la capture, et laissant la chaudière dans un état non
observé.

La probabilité est faible ; la conséquence ne l'est pas.

> **Obligation.** Le superviseur **MUST** être neutralisé pour toute la durée de
> la campagne, et rétabli à la fin (§13). Neutralisé signifie **deux** conditions,
> pas une : son timer arrêté **et** son unité d'exécution constatée inactive
> (§8.1). Ce n'est pas une précaution de confort : c'est la suppression d'un
> chemin de redémarrage automatique, et arrêter le seul timer ne la supprime pas.

### 8.1 Arrêter le timer ne suffit pas

Le superviseur est déclenché par un timer, mais il **s'exécute** dans une unité
distincte, à usage unique. Arrêter le timer empêche les déclenchements **futurs**
et **n'interrompt pas** une exécution déjà en cours.

C'est décisif ici : un cycle qui a franchi son test de mission attend **90 s**
avant de re-sonder, et conserve pendant toute cette attente le pouvoir de
redémarrer la machine. Un exploitant qui arrête le timer et enchaîne aussitôt
travaillerait donc, sans le savoir, à côté d'un cycle armé.

> **Règle.** Le superviseur n'est réputé neutralisé que lorsque **le timer ET
> l'unité d'exécution** sont l'un et l'autre constatés inactifs. « Timer inactif »
> n'équivaut **jamais** à « superviseur neutralisé ».

En pratique, engager la séquence **juste après un cycle nominal** réduit la
probabilité de tomber sur une exécution en cours. Cela ne dispense de rien : la
preuve d'inactivité de l'unité d'exécution reste obligatoire (PR-1, §9.1).

Point rassurant, vérifié : la sonde du superviseur interroge `vclient`
**directement**, et non le pont. Arrêter le pont ne la fait donc **pas** échouer,
et ne déclenche à lui seul aucune action du superviseur.

---

## 9. Préparation

Dans l'ordre. Aucune étape n'est facultative.

1. **Saison** — hors saison de chauffe (C5 §12.1).
2. **Présence physique** — l'exploitant est **devant la machine**, du début à la
   fin. « Joignable à distance » ne satisfait pas cette condition, et une session
   distante encore moins : voir l'étape 3.
3. **Plan de reprise physique connu et accepté** — la campagne neutralise le
   superviseur, donc aussi la remise en état automatique dont il est porteur. Si
   l'accès distant se perd pendant la fenêtre, l'exploitant doit **déjà savoir**
   comment reprendre la main sur place. Les unités concernées étant activées au
   démarrage, un redémarrage de la machine restaure l'état nominal des services.
   Ce n'est **pas** une étape du protocole : c'est un recours, connu d'avance,
   qu'aucune étape ne prescrit.
4. **Atelier** — créer `<atelier>`, vide, hors de tout dépôt versionné.
5. **Neutraliser le superviseur, et le prouver** — arrêter `<timer-guard>`, puis
   établir l'inactivité **du timer et de l'unité d'exécution** (§8.1) et
   **consigner comment** (PR-1 ci-dessous). Engager de préférence juste après un
   cycle nominal.
6. **Arrêter le pont, et le prouver** — arrêter `<unité-pont>`, puis établir son
   arrêt effectif et **consigner comment** (PR-2). Il sonde le démon toutes les
   10 s ; le laisser tourner introduirait une contention non maîtrisée pendant la
   mesure. Son unité déclare `Restart=always`, mais un arrêt explicite n'est pas
   suivi de redémarrage automatique : c'est bien un arrêt — ce qui **reste à
   constater**, non à supposer.
7. **Vérifier le démon** — le démon `vcontrold`, lui, **reste actif**. Confirmer
   par une lecture nue avant d'aller plus loin.
8. **Armer le retour arrière** — §12, avant toute écriture.

### 9.1 Preuves d'arrêt — symétriques et consignées

W4-A §19 n° 10 exige l'état du pont pendant l'essai **« et comment cela a été
établi »**. Une assertion d'arrêt ne vaut donc rien sans sa méthode. Les deux
arrêts sont traités à la même exigence.

| Réf | Objet | Ce que le rapport **MUST** porter |
|---|---|---|
| **PR-1** | `<timer-guard>` **et son unité d'exécution** | la méthode employée pour établir l'inactivité **des deux**, leurs sorties, et l'horodatage |
| **PR-2** | `<unité-pont>` | la méthode employée pour établir l'arrêt, sa sortie, et l'horodatage |

Deux preuves indépendantes valent mieux qu'une : l'état déclaré par le
superviseur de services **et** un constat d'absence d'activité observable. Ni
l'une ni l'autre n'est nommée ici : ce sont des constantes de site (§4).

> **Ce qui ne peut pas servir de preuve.** La sortie standard du pont **MUST
> NOT** être employée comme preuve d'arrêt ni de reprise. Elle est mise en
> tampon : des lignes produites longtemps avant peuvent n'être vidées qu'à la
> terminaison du processus, et recevoir alors un horodatage de journal
> **postérieur** à l'instant qu'elles décrivent. Une preuve d'arrêt fondée sur
> elle affirmerait le contraire de ce qu'elle observe.
>
> **Ce qui peut servir — pour PR-2 seulement.** Le **journal du démon**
> `vcontrold` horodate chaque connexion cliente. Le pont s'y inscrit à cadence
> soutenue tant qu'il tourne ; son arrêt fait **cesser cette cadence**, et sa
> reprise la fait repartir. C'est une trace écrite par un tiers — ni le pont, ni
> Boilerack, ni l'exploitant — ce qui en fait la preuve indépendante recherchée
> **pour le pont**.
>
> Une observation MQTT reste admise **en complément**, jamais comme unique
> preuve.

> **Ce journal ne prouve rien pour PR-1.** Il serait tentant de raisonner
> symétriquement — superviseur neutralisé, donc ses connexions périodiques
> cessent. **C'est faux, et dangereusement faux.** Un cycle dont le test de
> mission a échoué a déjà redémarré le pont et **dort 90 s** avant de re-sonder :
> pendant toute cette attente il n'ouvre **aucune** connexion au démon, et il
> reste pourtant **armé pour redémarrer la machine**. L'absence de connexion du
> superviseur dans le journal est donc exactement ce qu'on observerait dans le
> cas le plus dangereux.
>
> **PR-1 repose directement, et uniquement, sur l'état des unités** : timer
> inactif **et** unité d'exécution inactive (§8.1). Aucune inférence à partir
> d'une absence de trace.

Ces deux preuves sont relevées **avant** l'étape 01 de §11, et rappelées à la
restauration (§13).

---

## 10. Instrumentation de capture

W4-A exige `stdout`, `stderr`, code retour et durée **séparément**. Le pont
historique fusionne les deux flux depuis toujours : c'est précisément la raison
pour laquelle I-4 n'a jamais été observée. La capture **MUST NOT** passer par le
pont ni par Boilerack — elle invoque `vclient` nu.

À exécuter sous **bash** — `printf %q` est une fonctionnalité bash, et elle est
ici indispensable (voir plus bas).

```bash
capture() {
    local nom="$1"; shift
    local debut fin rc ms
    debut=$(date +%s%N)
    "$@" > "$nom.out" 2> "$nom.err"
    rc=$?
    fin=$(date +%s%N)
    ms=$(( (fin - debut) / 1000000 ))
    {
        printf 'commande='; printf '%q ' "$@"; printf '\n'
        printf 'code_retour=%s\n' "$rc"
        printf 'duree_s=%d.%03d\n' "$((ms / 1000))" "$((ms % 1000))"
        printf 'horloge=CLOCK_REALTIME (date +%%s%%N, GNU coreutils)\n'
        printf 'locale=%s\n' "${LC_ALL:-${LANG:-non-definie}}"
        printf 'fin_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$nom.meta"
    return 0
}
```

Trois fichiers par invocation, jamais fusionnés : `.out`, `.err`, `.meta`.

Trois choix de forme, chacun pour une raison :

- **`printf %q` plutôt que `"$*"`.** W4-A §19.2 exige « la ligne d'invocation
  réelle, **telle qu'exécutée** ». `"$*"` aplatit les arguments et perd les
  guillemets : `-c "setNiveauM1 5"` y devient indiscernable de deux arguments
  séparés. `%q` conserve la frontière — la ligne consignée est reproductible
  telle quelle.
- **Nanosecondes entières plutôt que `bc`.** L'arithmétique est faite par le
  shell : `bc` n'est pas garanti présent sur une installation minimale, et la
  campagne ne doit rien installer sur la machine de production.
- **Locale consignée.** C5 a montré qu'elle change la forme des nombres en
  lecture ; rien ne dit qu'elle est sans effet en écriture.
- **`local` sur toutes les variables.** Le helper est appelé plusieurs fois de
  suite dans le même shell ; sans `local`, `rc` ou `debut` survivraient d'une
  invocation à l'autre et une erreur de frappe se lirait comme une mesure.

> **Réserve d'horloge — à consigner telle quelle dans le rapport.** `date +%s%N`
> lit **`CLOCK_REALTIME`**, l'horloge murale, et non une horloge monotone. Trois
> conséquences, assumées plutôt que corrigées :
>
> 1. la mesure dépend de **GNU coreutils** (`%N` n'est pas portable) ;
> 2. un ajustement d'horloge — NTP, correction manuelle — pendant l'invocation
>    **invalide la mesure**, éventuellement jusqu'au signe ;
> 3. la durée est donc une **valeur indicative**, pas un chronométrage opposable.
>
> Aucune primitive monotone n'est disponible sans ajouter une dépendance sur une
> machine de production, ce que §9 interdit. La campagne s'en accommode : I-6
> cherche l'ordre de grandeur d'une écriture face à un budget de 5 s (E3), pas
> une mesure à la milliseconde. Une durée négative ou absurde relève de AB-7.

> **Le helper rend toujours `0`, délibérément.** Un code retour non nul de la
> commande capturée est un **résultat de campagne**, pas un incident de script :
> l'interrompre ferait perdre la capture. Le vrai code retour est dans
> `<nom>.meta`, jamais dans `$?` après `capture`. L'opérateur **MUST** lire
> `.meta` — et **MUST NOT** enchaîner `capture … && …`, qui réussirait toujours.

---

## 11. Séquence d'exécution

**Une seule écriture**, en forme `-J`. C'est la lecture la plus stricte de
C5 §12.3 (« une seule fois, sans répétition automatique »), et elle vise
exactement la lacune : la forme texte est déjà éprouvée par des mois de
production du pont historique (E1), tandis que `-J` en écriture n'a **jamais**
été exercé — alors que c'est la forme qu'emploie le lecteur de Boilerack.

| # | Étape | Invocation |
|---|---|---|
| 01 | lecture avant, forme texte | `capture 01-avant-texte vclient -h <hôte> -p <port> -c "getNiveauM1"` |
| 02 | lecture avant, forme `-J` | `capture 02-avant-json vclient -J -h <hôte> -p <port> -c "getNiveauM1"` |
| — | **relever `V_brut`** dans 01 et 02, **vérifier la concordance** au sens de §12.3.1 | — |
| — | **dériver `V_canon`** selon §11.3 — c'est **elle** qui sera écrite | — |
| — | **point d'arrêt** — si la concordance échoue (AB-2) ou si `V_canon` n'est pas dérivable (AB-9), **abandonner** (§12) | — |
| 03 | **écriture à l'identique, `-J`** | `capture 03-ecriture-json vclient -J -h <hôte> -p <port> -c "setNiveauM1 V_canon"` |
| 04 | relecture immédiate (≈ 1 s après) | `capture 04-apres-1s-json vclient -J -h <hôte> -p <port> -c "getNiveauM1"` |
| 05 | relecture à +10 s | `capture 05-apres-10s-json vclient -J -h <hôte> -p <port> -c "getNiveauM1"` |
| 06 | relecture, forme texte | `capture 06-apres-texte vclient -h <hôte> -p <port> -c "getNiveauM1"` |

La valeur observée est **conservée verbatim comme preuve**, et la valeur émise
en est **dérivée** selon §11.3 : ce sont deux objets distincts, et les confondre
serait une faute. Si les deux formes de lecture ne concordent pas au sens de
§12.3.1, c'est en soi un résultat à consigner — et un motif d'arrêt avant
l'étape 03.

Aucune étape n'est automatisée en boucle. Chaque invocation est lancée à la main,
son résultat lu, avant de décider de la suivante.

### 11.1 Garde de fraîcheur de `V_brut`

C5 §12.3 prescrit de réécrire **la valeur courante**. Si `V_brut` a été relevée
puis que le temps a passé, elle n'est plus la valeur courante mais une valeur
*historique* — et l'étape 03 cesserait d'être une réécriture à l'identique pour
devenir une écriture de valeur, ce que ce protocole n'autorise pas.

> **Règle.** Au moment d'exécuter l'étape 03, `V_brut` **MUST** être encore la
> valeur courante observée, établie par la lecture qui précède **immédiatement**
> l'écriture — et `V_canon` en **MUST** rester la dérivée exacte (§11.3).

En pratique : l'étape 02 enchaîne directement sur l'étape 03. Si quoi que ce soit
s'intercale — une pause, une interruption, une hésitation, un doute levé puis
écarté — la lecture est **refaite** avant d'écrire, sous un nom de capture
incrémenté. Si la relecture **ne concorde pas** avec `V_brut` au sens de
§12.3.2, la campagne s'arrête (AB-8) : une valeur qui bouge toute seule signale
un autre écrivain, et cette question relève de W4-F, pas d'ici.

> **Et l'arrêt est sec.** L'étape 03 n'ayant pas eu lieu, §12.1 **interdit** toute
> écriture — y compris celle de `V_canon`. Réécrire ici effacerait le changement
> qu'on vient précisément de constater, et détruirait la seule preuve qu'un autre
> écrivain existe.

Cette garde est **une lecture**. Elle n'ajoute aucune écriture, et ne peut en
aucun cas être satisfaite en écrivant.

### 11.2 Cardinalité des écritures — explicite

> **WRITE NOMINAL COUNT = 1**

Une seule écriture de caractérisation, l'étape 03. Aucun réessai, quel que soit
son résultat : ni après un code retour non nul, ni après un délai épuisé, ni
« pour vérifier ». Un échec de l'étape 03 est un **résultat**, à capturer et à
rapporter tel quel.

L'écriture de restauration éventuelle du §12 **n'entre pas dans ce compte** : ce
n'est pas une seconde tentative de caractérisation, c'est un retour à l'état
initial. Elle est comptée séparément, son existence est elle-même un fait à
consigner, et elle est **subordonnée à §12.1** : sans étape 03 exécutée, elle est
impossible — `ecritures_nominales == 0` implique `ecritures_restauration == 0`.

### 11.3 Valeur observée et valeur canonique — deux objets distincts

Une lecture de `getNiveauM1` ne restitue pas un entier. Elle restitue une
représentation **décimale** — sur ce point la forme texte et la forme `-J`
s'accordent, et la forme `-J` expose en outre la chaîne brute telle que le démon
l'a produite, espace terminale comprise.

Or A5 §5.3 est catégorique pour ce datapoint : type `int`, pas de 1, **entier
strict, aucune décimale autorisée**, « toute valeur float transmise doit être
rejetée avant émission ». Et la forme d'écriture éprouvée par des mois de
production du pont historique (E1) est l'**entier**, jamais une représentation
décimale.

Réécrire « verbatim » la chaîne lue émettrait donc une forme que la
spécification du datapoint interdit et que la production n'a jamais exercée —
et transformerait l'unique écriture de la campagne en test de normalisation
flottante, c'est-à-dire en la mesure de I-8, que §6 déclare explicitement hors
d'atteinte. Le protocole tranche donc, **avant** la fenêtre, ce que l'exploitant
aurait sinon dû improviser à l'instant du seul acte irréversible.

| Objet | Ce que c'est | Usage |
|---|---|---|
| **`V_brut`** | la représentation observée, telle quelle — texte utile, `raw` du JSON, `value` du JSON | **preuve** : consignée intégralement, jamais modifiée |
| **`V_canon`** | l'entier autorisé que `V_brut` désigne exactement | **émission** : la seule valeur écrite, à l'étape 03 comme en restauration |

> **Règle de dérivation, volontairement non permissive.** `V_canon` n'est dérivée
> que si `V_brut` désigne **exactement** un entier du domaine. La dérivation
> **MUST** échouer — et la campagne s'arrêter par **AB-9** — dans chacun de ces
> cas :
>
> - la valeur observée n'est pas un entier exact (partie fractionnaire non nulle) ;
> - elle est hors des bornes du datapoint ;
> - sa représentation est ambiguë, tronquée, arrondie ou non interprétable ;
> - les observations disponibles ne concordent pas (§12.3) ;
> - l'entier ne peut pas être établi **sans perte** à partir de ce qui a été lu.
>
> En cas de doute, on n'arrondit pas : on abandonne.

> **Portée strictement locale.** Cette règle vaut pour **ce datapoint**, et
> parce que son contrat le permet : `int`, pas de 1, tolérance de confirmation
> nulle. Elle n'établit **aucune** règle générale de normalisation, ne s'applique
> à aucun autre rôle inscriptible, et ne préjuge en rien du contenu des futurs
> `Profile` — qui relèvent de W4-D.

---

## 12. Retour arrière et critères d'abandon

**Retour arrière.** Armer le retour arrière, c'est relever `V_brut`, en dériver
`V_canon` (§11.3) et **écrire à l'avance** la commande qui la restaurerait — la
**même que l'étape 03**, `V_canon` comprise. Les deux **MUST** être relevées et
notées par écrit **avant** l'étape 03.

> **Une seule valeur émise, du début à la fin.** L'étape 03 et une éventuelle
> restauration écrivent **la même** `V_canon`. Il est donc **impossible** qu'une
> restauration réintroduise la représentation décimale observée après que
> l'étape nominale a émis l'entier : la commande de restauration n'est pas
> reconstruite au moment où l'on en a besoin, elle est **recopiée** de celle qui
> a été armée avant l'étape 03.

**Armer n'est pas exécuter.** Cette commande n'est tirée que si §12.1 l'autorise,
et §12.1 l'interdit dans le cas le plus fréquent d'abandon : celui où l'étape 03
n'a pas eu lieu. Un abandon ne déclenche donc **pas** une écriture par défaut.

> **Nature de cette écriture.** Prescrite par C5 §12.5, elle est **conditionnelle
> et non nominale** : elle ne caractérise rien. Elle est donc hors du
> `WRITE NOMINAL COUNT` (§11.2), et la confondre avec un réessai serait une
> faute — le réessai est interdit, la restauration est due **lorsqu'elle est
> autorisée**. Le rapport les distingue explicitement : `ecritures_nominales`,
> `ecritures_restauration`.

### 12.1 La restauration est conditionnée à l'exécution de l'étape 03

Une campagne interrompue **avant** d'avoir écrit n'a rien à restaurer par
écriture. Prescrire « restaurer `V_canon` » sans condition serait pire
qu'inutile : face à une valeur qui a bougé toute seule, cela ferait **écraser un
changement que la campagne n'a pas causé** — exactement ce que §11.1 identifie
comme le signe d'un autre écrivain, et que W4-F seul a autorité pour traiter.

> **Règle.** Une écriture de restauration n'est autorisée **que si l'étape 03 a
> effectivement été exécutée**. Le critère est ce **fait objectif**, jamais le
> critère d'abandon qui a été déclenché.

| Étape 03 exécutée | Ce qui est autorisé |
|---|---|
| **non** | **aucune écriture, d'aucune sorte.** Ne pas écrire `V_canon`, ne pas « remettre » quoi que ce soit. Rétablir les services (§13), conserver les captures, rapporter |
| **oui** | la logique C5 §12.5 s'applique : constater l'état courant, puis **0** écriture s'il **concorde** avec `V_brut` au sens de §12.3.2, **au plus 1** sinon — et cette écriture est `V_canon` |

Cette règle couvre tous les chemins d'interruption sans qu'il soit besoin de les
énumérer : valeur devenue différente (AB-8), formes discordantes (AB-2), démon
injoignable (AB-3), redémarrage de service ou de machine (AB-5), doute de
l'exploitant (AB-6), et tout autre arrêt survenu avant l'étape 03. Une liste
fermée de cas serait fragile ; le fait objectif ne l'est pas.

> **Corollaire de compteurs.** `ecritures_nominales == 0` **implique**
> `ecritures_restauration == 0`. Un rapport portant `ecritures_nominales=0` et
> `ecritures_restauration=1` décrit une campagne qui a écrit sans avoir
> caractérisé : c'est une **violation du protocole**, pas un résultat.

### 12.2 Comment savoir si l'étape 03 a été exécutée

Aucun état nouveau n'est nécessaire : les captures du §10 suffisent, parce que
le shell crée les fichiers de redirection **au lancement** de l'invocation et
n'écrit `.meta` **qu'au retour**.

| Artefacts de `03-ecriture-json` | Lecture | Restauration |
|---|---|---|
| aucun fichier | l'invocation n'a **jamais** été lancée | **interdite** |
| `.out` et `.err` présents, `.meta` **absent** | l'invocation a été lancée puis interrompue — son issue est **inconnue**, et une écriture a **pu** partir | **autorisée**, conditionnelle |
| `.meta` présent | l'invocation est allée à son terme, quel que soit son code retour | **autorisée**, conditionnelle |

Le cas du milieu est tranché dans le sens **prudent** : une invocation lancée
dont on ignore l'issue est traitée comme une écriture ayant pu avoir lieu. C'est
précisément la situation que I-13 décrit et que §14.1 demande de rapporter.

> **À consigner.** Une divergence constatée **après** une étape 03 réussie est en
> soi une anomalie : une écriture à l'identique ne devrait déplacer aucune
> valeur. La restaurer est prescrit ; l'expliquer ne l'est pas — le rapport
> énonce le fait sans conclure entre une normalisation par le démon (I-8) et un
> autre écrivain (W4-F).

### 12.3 Ce que « concordance » veut dire

Cette section définit **la seule** règle de comparaison du protocole. Elle
s'applique à deux situations, et à elles seules :

- **entre les deux formes d'une même lecture** — étapes 01 et 02, sanctionnée
  par **AB-2** (§12.3.1) ;
- **entre une relecture ultérieure et `V_brut`** — §11.1, AB-1, AB-8, §12.1,
  §13 étape 1 (§12.3.2).

Partout où le document écrit « concorde », « ne concorde pas » ou « diverge », il
désigne **cette** règle, et rien d'autre. Aucune heuristique supplémentaire n'est
introduite ailleurs.

#### 12.3.1 Entre les deux formes d'une même lecture — AB-2

Exiger que la forme texte et la forme `-J` soient **identiques** serait
impossible à satisfaire : l'une est une ligne de texte, l'autre une structure
dont un champ est un **nombre**. Une chaîne et un nombre ne peuvent pas être
égaux, et fabriquer une divergence à partir de cette différence de nature
n'apprendrait rien. Le protocole distingue donc deux niveaux, tous deux requis.

| Niveau | Ce qui est comparé | Condition |
|---|---|---|
| **Concordance brute** | la valeur utile du texte, après retrait déterministe du préfixe de commande, et le champ `raw` du JSON | les deux portent **la même représentation brute** |
| **Concordance sémantique** | cette représentation et le champ numérique du JSON | elles désignent **la même valeur**, et cette valeur est **exactement** convertible en l'entier canonique autorisé (§11.3) |

Le retrait du préfixe est **déterministe** : la lecture textuelle nomme la
commande puis restitue la valeur ; seule la partie utile est comparée. Les
espaces de bordure ne constituent pas une divergence — ils sont conservés dans
`V_brut` comme preuve, et neutralisés pour la comparaison.

> **AB-2 déclenche si l'un des deux niveaux échoue.** Une différence réelle —
> deux valeurs numériques distinctes, deux représentations brutes distinctes —
> arrête la campagne. Une différence de **type** entre une chaîne et un nombre,
> non.

#### 12.3.2 Entre une relecture ultérieure et `V_brut`

Les étapes 01 et 02 produisent, ensemble, trois formes : le texte, le champ
`raw` et le champ numérique. Une relecture ultérieure n'en produit pas
nécessairement autant — l'étape 04 et l'étape 05 sont en `-J` seul, l'étape 06
en texte seul. Comparer ce qui n'a pas été capturé serait impossible ; en faire
une divergence serait faux.

> **Règle.** Une relecture est comparée à `V_brut` avec **les mêmes exigences de
> fond** qu'en §12.3.1, mais **uniquement sur les formes effectivement présentes
> dans cette capture**.
>
> - Chaque forme présente est comparée à **la composante correspondante** de
>   `V_brut` : le texte utile au texte utile, `raw` à `raw`, le champ numérique
>   à la valeur numérique de référence.
> - La valeur ainsi observée **MUST** désigner encore **exactement le même**
>   `V_canon` (§11.3).
> - Le retrait du préfixe et la neutralisation des espaces de bordure
>   s'appliquent à l'identique.

**L'absence d'une forme n'est pas une divergence.** Une capture en `-J` seul ne
porte pas de ligne de texte : on compare son `raw` et son champ numérique, et
c'est tout. Réciproquement pour une capture en texte seul.

**Une différence réelle sur une forme présente en est une.** Elle déclenche
l'abandon prévu par le critère applicable au moment où elle est constatée —
AB-8 avant l'étape 03, AB-1 à toute autre étape — sans qu'aucune tolérance
supplémentaire ne soit introduite : le datapoint retenu est à **égalité stricte**
(A5 §5.3).

### 12.4 Critères d'abandon

**Abandon immédiat**, sans poursuivre la séquence, si :

| Réf | Condition |
|---|---|
| AB-1 | une relecture **ne concorde pas** avec `V_brut` au sens de §12.3.2, à n'importe quelle étape |
| AB-2 | la concordance des deux formes d'une même lecture échoue au sens de §12.3.1, avant l'étape 03 |
| AB-3 | le démon `vcontrold` change d'état, ou devient injoignable |
| AB-4 | une invocation dépasse nettement le budget de 5 s connu (E3) |
| AB-5 | un service redémarre, ou la machine redémarre, pour quelque cause |
| AB-6 | tout doute de l'exploitant, sans justification à fournir |
| AB-7 | une durée mesurée négative, nulle ou manifestement absurde — l'horloge a bougé (§10), la mesure et les suivantes ne valent plus rien |
| AB-8 | la garde de fraîcheur de §11.1 échoue : avant l'étape 03, la relecture **ne concorde pas** avec `V_brut` au sens de §12.3.2 |
| AB-9 | `V_canon` n'est pas dérivable de `V_brut` sans perte, au sens de §11.3 |

Après un abandon, dans cet ordre : appliquer §12.1 — qui peut ne prescrire
**aucune** écriture —, rétablir §13, **puis** rapporter. Aucune seconde tentative
dans la même fenêtre.

> **Interdiction.** Ne **jamais** provoquer délibérément un dépassement de budget
> ni un démon injoignable pour capturer I-12, I-13 ou I-15. Ces signatures se
> recueillent si elles surviennent, elles ne se fabriquent pas sur une
> installation en service.

---

## 13. Restauration de l'état normal

Dans cet ordre, et vérifié à chaque étape :

1. confirmer par une lecture nue que la valeur en place **concorde** avec
   `V_brut` au sens de §12.3.2 ;
2. redémarrer `<unité-pont>` ;
3. **constater sa reprise effective, en amont ET en aval** — voir §13.1. Une
   trentaine de secondes suffit à lever le doute. La sortie standard du pont
   **MUST NOT** servir ici : elle est mise en tampon (§9.1) ;
4. redémarrer `<timer-guard>` ;
5. confirmer que le superviseur repasse un cycle nominal sans action corrective,
   **et** que son unité d'exécution retrouve son alternance normale (§8.1).

La campagne n'est close qu'après l'étape 5.

Les preuves **PR-1** et **PR-2** (§9.1) sont l'une et l'autre redoublées ici : le
rapport porte non seulement comment l'arrêt a été établi, mais **comment la
reprise l'a été**. Redoublées, non interchangeables — elles ne reposent pas sur
les mêmes moyens, et §9.1 dit lesquels. Un pont qu'on croit redémarré et qui ne
publie plus serait la pire issue possible de cette campagne — pire que n'importe
quel résultat négatif.

### 13.1 Reprise du pont — trois faits distincts, et pourquoi il en faut trois

« Actif », « sondant » et « publiant » ne sont pas le même fait, et le troisième
est le seul qui intéresse les consommateurs du pont. Un processus peut être actif
sans sonder ; il peut sonder sans publier — sa liaison amont fonctionnerait
pendant que sa sortie aval serait muette. La reprise n'est donc établie que par
**trois constats**, chacun sur un chemin différent :

| | Fait | Constaté par |
|---|---|---|
| **A** | le pont est **actif** | l'unité redevenue active |
| **B** | le pont **sonde** le démon | la cadence de connexions repartie dans le journal du démon (§9.1) |
| **C** | le pont **publie** | la télémétrie effectivement observée **depuis un consommateur aval** |

> **Aucun des trois ne remplace les autres.** A sans B décrirait un processus qui
> tourne sans travailler. **B sans C est précisément le piège** : la cadence côté
> démon prouve que le pont *interroge la chaudière*, jamais qu'il *diffuse ce
> qu'il lit*. C'est exactement l'issue que §13 désigne comme la pire — « un pont
> qu'on croit redémarré et qui ne publie plus » —, et la cadence amont ne la
> détecte pas.
>
> L'observation aval **MUST** donc être faite, et consignée. Elle est ici une
> preuve **requise**, non un complément : c'est le seul point du protocole où
> une observation depuis le bus est obligatoire, et cela ne fait pas d'elle
> l'unique preuve du bon fonctionnement du pont — elle vient **en plus** de A et
> de B, jamais à leur place.

---

## 14. Livrable — ce que W4-C rapporte

W4-A §19 fixe la liste. Ce protocole la couvre ainsi :

| §19 | Champ exigé | Fourni par |
|---|---|---|
| 1 | nom réel de la commande d'écriture | §7 — `setNiveauM1` |
| 2 | ligne d'invocation réelle, telle qu'exécutée | `03-ecriture-json.meta`, champ `commande=` — elle porte `V_canon`, la valeur **réellement émise** |
| 3 | `stdout` et `stderr` intégralement et **séparément** | `.out` / `.err`, jamais fusionnés (§10) |
| 4 | code retour | `.meta` |
| 5 | durée mesurée | `.meta` |
| 6 | valeur **avant** | étapes 01–02 — **`V_brut` intégrale** (texte utile, `raw`, champ numérique) **et** `V_canon` dérivée, côte à côte (§11.3) |
| 7 | écriture à l'identique | étape 03, conforme à C5 §12.3 — `V_canon` désigne la même valeur que `V_brut`, la campagne ne déplace rien |
| 8 | valeur **après**, et délai de stabilité | étapes 04–06 — **avec la réserve I-7 du §6** |
| 9 | preuve de retour arrière, armée avant l'essai | §12, armée avant l'étape 03, **`V_canon` comprise** |
| 10 | état du pont historique pendant l'essai, **et comment cela a été établi** | **arrêté** — méthode et sortie consignées en **PR-2**, jamais fondées sur sa sortie standard (§9.1) ; superviseur neutralisé **timer et unité d'exécution**, **PR-1** (§8.1, §9.1) |
| 11 | ce qu'il est possible d'établir, par une méthode sûre et autorisée, sur l'effet d'une expiration du budget local — **I-13** | §14.1 |

**11 exigences sur 11.** Deux sont livrées en retrait de ce que W4-A espérait, et
le protocole dit pourquoi avant d'exécuter plutôt qu'après :

- le **champ 8** — §6 : une écriture à l'identique ne propage rien, donc aucun
  délai de convergence n'est mesurable ;
- le **champ 11** — §14.1 ci-dessous.

Ce ne sont pas des défauts d'exécution mais des limites de la méthode, et la
méthode a été choisie parce qu'elle est sûre.

### 14.1 Champ 11 — I-13, et la seule réponse honnête

W4-A §19 n° 11 demande ce qu'une **méthode sûre et autorisée** permet d'établir
sur l'effet d'une expiration du budget local — le cas où le processus client est
terminé alors qu'une transaction Optolink est peut-être en cours.

Le protocole ne connaît qu'une méthode sûre : **ne rien provoquer**. §12 interdit
explicitement de fabriquer un dépassement de budget, et cette interdiction n'est
pas négociable sur une installation en service. Deux issues, donc, et deux
seulement :

| Cas | Ce que le rapport porte |
|---|---|
| Aucun dépassement de budget n'est survenu — **attendu** | **`INCONNU NON LEVÉ — INTERDICTION CONSERVÉE`**, verbatim |
| Un dépassement est survenu **spontanément** | les faits capturés tels quels : `.out`, `.err`, code retour, durée, valeur relue ensuite — sans en tirer de conclusion sur ce qu'a fait le démon |

> **Le champ 11 est renseigné dans les deux cas.** W4-A §19 l'écrit sans
> ambiguïté : « un lot terrain a le droit de rapporter qu'il n'a pas pu établir
> un fait ; il n'a pas le droit de le deviner. » Une case vide serait un manquement
> au livrable ; la mention `INCONNU NON LEVÉ` est, elle, une réponse complète.

### 14.2 Champs de contexte

Sobres, et utiles au dépouillement comme à la reproductibilité :

| Champ | Source |
|---|---|
| horodatage UTC de fin de chaque invocation | `fin_utc` dans `.meta` (§10) |
| début et fin de la campagne | relevés par l'exploitant, à l'ouverture et après §13 |
| `ecritures_nominales` / `ecritures_restauration` | §11.2 et §12.1 — la seconde est nulle si la première l'est |
| `V_brut` / valeur numérique interprétée / `V_canon` émise | §11.3 — les trois côte à côte, jamais l'une à la place de l'autre |
| anomalies observées, même écartées | journal libre de l'exploitant — une anomalie écartée reste un fait |
| critère d'abandon déclenché, le cas échéant | `AB-1` … `AB-9` (§12.4) |

Les captures sont versionnées dans `tests/fixtures/vclient/`, selon la convention
établie par C5 : encodage base64, flux séparés, couverture par un test de
caractérisation.

---

## 15. Ce que cette campagne ne prouvera pas

À écrire dans le rapport, en toutes lettres, pour qu'aucune lecture ultérieure ne
s'y trompe :

- elle ne prouve rien sur une écriture **qui change** une valeur ;
- elle ne prouve rien sur un refus, une valeur hors bornes, un démon injoignable
  ni un délai épuisé ;
- elle ne prouve rien au-delà de `setNiveauM1` — les trois autres commandes
  restent éprouvées par la production du père, non par cette campagne ;
- elle n'autorise pas l'activation de la voie transactionnelle, qui relève de
  W4-E ;
- elle ne lève **pas** les interdictions de W4-A §11.6 (`DAEMON_UNREACHABLE`) ni
  **W4-A** §12.3 (`UNKNOWN_COMMAND`) : aucune défaillance d'écriture n'aura été
  observée,
  et §6.1 explique pourquoi elle ne peut pas l'être ici ;
- elle ne dit rien de l'effet d'une expiration du budget local — I-13, §14.1 —
  sauf si le phénomène survient de lui-même ;
- elle ne dit **rien** de la normalisation d'une valeur par le démon ou la
  chaudière — I-8. La règle canonique du §11.3 sert précisément à **écarter**
  cette question de la campagne : elle n'émet qu'un entier exact, jamais une
  représentation décimale dont le sort resterait à interpréter.

Elle établit une chose, et une seule : **ce que `vclient -J` répond quand une
écriture aboutit.** C'est exactement ce qui manque à W4-B pour cesser d'être « non
résolu pour l'invocation réelle ».

---

## 16. Résultats — la campagne a été exécutée

**Le 22 août 2026, de 22:50:30 à 23:05:29 CEST**, sur l'installation de
référence, exploitant physiquement présent du début à la fin. Les sections 1 à 15
sont le protocole tel qu'il a été écrit **avant** ; celle-ci rapporte ce qui a été
**observé**. Aucune des deux ne réécrit l'autre : la prédiction du §6 et le
résultat du §16 se lisent ensemble.

Une seule campagne. Aucune n'est autorisée à la suivre.

### 16.1 Conditions réunies, et comment elles ont été établies

| Condition | Établie par |
|---|---|
| M1 au repos | extérieur 22,8 °C, consigne ambiante M1 15,0 °C, **brûleur 0,0 %**, consigne ECS 10,0 °C |
| présence physique | déclarée par l'exploitant, tenue sur toute la fenêtre |
| **PR-1** — superviseur neutralisé | timer `inactive`/`dead` avec prochain tir **vide** ; unité d'exécution `inactive`/`dead`, **sortie constatée** ; **aucun processus du superviseur vivant**. Aucun raisonnement par absence de trace (§9.1) |
| **PR-2** — pont arrêté | unité `inactive`/`dead`, `Result=success`, aucun redémarrage automatique ; **cadence de connexions au démon interrompue — zéro nouvelle connexion en 25 s** |
| démon actif | `active`/`running`, jamais touché, lecture nue de code retour `0` |
| one-writer | trois unités inscriptibles inactives, une seule session ouverte, **zéro connexion tierce au démon en 12 s** |
| atelier | `<atelier>` sur stockage persistant, hors dépôt versionné ; helper du §10 **repris verbatim**, empreinte vérifiée |

La neutralisation a été engagée juste après un cycle nominal, comme le §8.1 le
recommande — mais la preuve reste celle des unités, pas celle du moment choisi.

### 16.2 Valeur de campagne

| Objet | Observé |
|---|---|
| `V_brut` — texte utile | `'2.000000 '`, espace terminale comprise |
| `V_brut` — `raw` JSON | `'2.000000 '` |
| `V_brut` — champ numérique | `2.0` |
| valeur interprétée | `2.000000` en décimal exact |
| **`V_canon`** | **`2`** |

Concordance §12.3.1 vérifiée sur les deux niveaux. Dérivation §11.3 passée sous
sept contrôles — partie fractionnaire nulle, entier exact, dans les bornes, sur
le pas, représentation non ambiguë, reconversion sans perte, observations
concordantes. La garde de fraîcheur du §11.1 a été **effectivement exercée** :
une étape intermédiaire s'étant intercalée, la lecture a été refaite sous un nom
incrémenté avant d'écrire, et elle concordait.

**AB-2, AB-8 et AB-9 n'ont pas déclenché.** Aucun critère d'abandon, d'ailleurs,
n'a déclenché de toute la campagne.

### 16.3 Le fait central — signature d'une écriture acceptée

Une invocation, une seule :

```
vclient -J -h <hôte> -p <port> -c "setNiveauM1 2"
```

| Sortie | Observé |
|---|---|
| `stdout` | `[{"command":"setNiveauM1 2","value":0.000000,"raw":"OK","error":""}]` |
| `stderr` | **vide — 0 octet** |
| code retour | **0** |
| durée | **1,045 s** — valeur indicative, réserve d'horloge du §10 maintenue |

C'est ce qui manquait au dépôt depuis le premier jour : **la forme que prend une
écriture qui aboutit**, capturée une fois, sur un datapoint, dans des conditions
maîtrisées.

### 16.4 Ce que cette signature ne dit pas — `value` n'est pas une valeur

> **Interdiction.** Le champ `value` d'une réponse d'**écriture** **MUST NOT**
> être interprété comme la valeur du datapoint, ni comme une confirmation que
> quoi que ce soit a été appliqué. Sur l'écriture acceptée observée ici, il vaut
> `0.000000` alors que le datapoint valait, vaut et est resté à `2`.

`0.000000` est ici un **remplissage**, pas une mesure. Aucune conclusion sur une
normalisation par le démon ou par la chaudière n'en découle : I-8 reste entière,
et la campagne l'a délibérément écartée en n'émettant qu'un entier exact (§11.3).

La confirmation métier reste ce qu'elle a toujours été : **une relecture séparée
du datapoint**. Cette campagne ne déplace pas cette frontière — elle la confirme.

### 16.5 I-14 — étayée par comparaison directe, non close

L'inconnue demandait quelles signatures de lecture sont **réellement**
transposables à l'écriture. La réponse est maintenant adossée à des observations,
et elle est contre-intuitive. Confrontation avec les fixtures C5 :

| Champ | Lecture réussie (`read_ok_json`) | Lecture **en erreur** (`unknown_command_json`) | **Écriture acceptée (terrain)** | Transposable ? |
|---|---|---|---|---|
| code retour | `0` | `0` | `0` | **non discriminant** — confirmé une troisième fois |
| `command` | `"getTempKist"` — nom seul | le nom inconnu | **`"setNiveauM1 2"` — nom ET argument** | **non** — la forme change |
| `value` | `28.000000` — la valeur | **`0.000000`** | **`0.000000`** | **NON — et c'est le piège** |
| `raw` | `"28.000000 Grad Celsius"` | `"ERR: command unknown"` | **`"OK"`** | **non** — jeton d'état, pas une représentation |
| `error` | `""` | `"ERR: command unknown"` | `""` | **oui** — discriminant, comme C7 §1.1 l'établissait |
| `stderr` | vide | non vide | **vide** | **oui, sur le succès** |

> **Le piège, nommé.** En lecture, `value == 0.000000` **accompagne une erreur** —
> C7 §1.1 le tient de la fixture `unknown_command_json`. En écriture, la même
> valeur **accompagne un succès**. Les mêmes octets signifient l'inverse selon le
> contexte. Un adaptateur qui transposerait l'heuristique de lecture vers
> l'écriture classerait une écriture réussie en échec.
>
> Ce que la campagne établit, c'est donc moins une ressemblance qu'une
> **dissemblance mesurée**, et c'est la partie utile.

Ce qui reste **non observé**, et ne le sera pas ici : la signature d'un démon
injoignable en écriture (I-15) et celle d'une commande inconnue ou refusée en
écriture. **Aucun échec n'a été provoqué**, et une absence d'échec n'est pas la
connaissance d'une signature d'échec. I-14 demeure donc **partiellement levée** —
mais étayée, là où elle n'était qu'annoncée.

### 16.6 Invariance, et un écart de cadence à consigner

| Étape | Écart réel après l'écriture | Valeur relue |
|---|---|---|
| 04, forme `-J` | **+39 s** — cible ≈ 1 s | `2.000000` |
| 05, forme `-J` | **+77 s** — cible +10 s | `2.000000` |
| 06, forme texte | +92 s | `2.000000 ` |

Preuve la plus forte de l'invariance : les quatre lectures en forme `-J`, avant
comme après l'écriture, sont **byte-identiques** — même empreinte — et les deux
lectures en forme texte également. Rien n'a bougé, et cela se démontre par
comparaison d'octets plutôt que de valeurs affichées.

> **Écart au protocole, assumé.** Les étapes 04 et 05 n'ont pas respecté les
> cadences prévues : l'aller-retour de l'opérateur les rend inatteignables en
> pratique. L'écart ne remet pas en cause l'invariance, mais il **interdit toute
> conclusion sur un délai minimal de propagation**. I-7 n'est pas levée — elle ne
> l'aurait de toute façon pas été, une écriture à l'identique ne propageant rien
> (§6). Une campagne future qui voudrait mesurer un délai devrait automatiser la
> relecture, ce que ce protocole interdit ailleurs pour d'autres raisons.

### 16.7 Cardinalité et retour arrière

> **`WRITE NOMINAL COUNT = 1`** · **`WRITE RESTAURATION COUNT = 0`**

Preuve mécanique : une seule occurrence d'une commande d'écriture dans l'ensemble
des métadonnées de l'atelier. L'étape 03 ayant été exécutée — ses trois fichiers
sont présents, `.meta` compris (§12.2) —, la restauration était **autorisée et
conditionnelle**. L'état courant a été constaté **avant** toute écriture : il
concordait avec `V_brut` sur les trois relectures, donc **zéro écriture de
restauration**. La commande armée avant l'étape 03 n'a jamais été tirée.

### 16.8 Matrice des inconnues après terrain

| Réf | Statut | Fondement |
|---|---|---|
| I-1 | **LEVÉE** | `-J` produit une sortie JSON valide et exploitable en écriture |
| I-2 | levée avant campagne | E2 |
| I-3 | **LEVÉE** | forme de `stdout` sur écriture acceptée, capturée (§16.3) |
| I-4 | **LEVÉE** | `stderr` **vide, 0 octet** — premier flux jamais observé isolément |
| I-5 | **LEVÉE** | code retour `0` sur écriture acceptée |
| I-6 | **LEVÉE** | **1,045 s**, sous la réserve d'horloge du §10 |
| I-7 | **non levée** | rien ne se propage ; l'écart de cadence du §16.6 l'interdit doublement |
| I-8 | **non levée** | délibérément écartée par la règle canonique du §11.3 |
| I-9 | contournée par construction | inchangé |
| I-10 | **non levée** | non sollicitée par une écriture identique |
| I-11 | **non levée** | indécidable sans changement de valeur |
| I-12 | **non levée** | aucun délai épuisé n'est survenu |
| I-13 | **non levée** | **aucun dépassement de budget n'est survenu, aucun n'a été provoqué** |
| I-14 | **partiellement levée, étayée** | §16.5 |
| I-15 | **non levée** | exigerait d'arrêter le démon — hors périmètre |

**Attribution exacte du rendement.** La campagne terrain a levé **cinq**
inconnues — I-1, I-3, I-4, I-5, I-6. **I-2 était déjà levée avant elle**, par
l'expérience de production du pont (E2, §5) : la campagne ne la lève pas, elle en
hérite. **I-14 reste partielle**, étayée mais non close. I-9 demeure contournée
par construction, et **sept restent intactes** — I-7, I-8, I-10, I-11, I-12,
I-13, I-15.

C'est exactement le rendement annoncé au §6, ni plus, ni moins.

### 16.9 W4-A §19 — onze champs renseignés

| §19 | Renseigné par |
|---|---|
| 1 | `setNiveauM1` |
| 2 | ligne réellement exécutée, portant `V_canon`, consignée sous forme reproductible |
| 3 | `stdout` et `stderr` en fichiers distincts, jamais fusionnés |
| 4 | `0` |
| 5 | `1,045 s`, indicative |
| 6 | `V_brut` intégrale **et** `V_canon`, côte à côte |
| 7 | oui — `V_canon` désigne la même valeur que `V_brut` |
| 8 | valeur après : `2.000000` ; **délai de stabilité non déterminé** (§16.6) |
| 9 | armé et consigné **avant** l'étape 03 |
| 10 | pont arrêté, PR-2 ; superviseur neutralisé timer **et** unité, PR-1 |
| 11 | **`INCONNU NON LEVÉ — INTERDICTION CONSERVÉE`** |

> **Onze champs renseignés n'est pas onze inconnues levées.** Les champs 8 et 11
> portent une réponse négative, et c'est une réponse complète — W4-A §19 l'écrit :
> un lot terrain a le droit de rapporter qu'il n'a pas pu établir un fait.

### 16.10 Ce que W4-B reçoit, et ce qu'il ne doit pas en faire

Pour **la commande caractérisée**, et pour elle seule, une écriture locale
acceptée présente conjointement : processus terminé · code retour `0` · `stderr`
vide · `stdout` en JSON valide · un objet · `command` portant la commande **et**
son argument · `raw == "OK"` · `error == ""` · `value == 0.000000`.

> **Trois bornes.** Cette signature vient d'**une** observation, sur **un**
> datapoint, dans **un** succès : elle ne se généralise ni aux trois autres rôles
> inscriptibles, ni aux échecs, ni à d'autres versions du client. · Le champ
> `value` **MUST NOT** devenir un résultat métier. · Le verdict d'application
> reste au cœur, par relecture, conformément à l'architecture existante.

Aucune ligne de code n'est écrite ici. W4-B reste à ouvrir.

### 16.11 Retour à l'état nominal

Le pont a été repris et sa reprise établie sur les **trois** faits du §13.1 :
unité active · cadence de connexions au démon repartie · **télémétrie
effectivement publiée**, observée depuis un consommateur aval avec les messages
retenus exclus, portant le datapoint de la campagne à sa valeur. Le superviseur a
ensuite été rétabli et a repassé un cycle **nominal sans action corrective**, son
timer ré-armé.

État final : aucun redémarrage machine · démon jamais touché · pont redémarré une
seule fois, par l'exploitant · datapoint à `2.000000`, pente inchangée, brûleur à
l'arrêt.

### 16.12 Artefacts — écart au §14.2, assumé

Les captures — trois fichiers par invocation, plus les journaux de preuve —
résident dans `<atelier>`, sur la machine de référence. **Elles ne sont pas
versionnées dans ce dépôt.**

> **ÉCART AU §14.2, ASSUMÉ.** Le §14.2 prescrit que « les captures sont
> versionnées dans `tests/fixtures/vclient/`, selon la convention établie par
> C5 ». **Cette campagne ne l'a pas fait**, et le présent paragraphe le déclare
> plutôt que de le laisser passer sous silence. Le §14.2 n'est pas réécrit
> rétroactivement : il a été prescrit avant, il reste au dossier tel quel.

Ce que cet écart recouvre, précisément :

- les captures **existent** et sont **conservées hors dépôt**, intactes ;
- aucune n'a été copiée, transformée, encodée ni tronquée par cette clôture ;
- leur **sélection** éventuelle — toutes, certaines, aucune — et leur
  transformation en fixtures versionnées relèvent d'une **décision explicite
  ultérieure**, avec les mêmes exigences que C5 : encodage base64, flux séparés,
  couverture par un test de caractérisation ;
- **cette décision n'est pas prise ici**, et ne conditionne pas la clôture de
  W4-C.

Un relevé terrain n'entre pas dans le dépôt au seul motif qu'il existe. Le
reporter n'ouvre aucun chantier bloquant : W4-B et W4-D peuvent être ouverts sans
lui, la signature dont ils ont besoin étant consignée au §16.3.

### 16.13 Ce que cette campagne n'a toujours pas prouvé

Le §15 reste vrai, mot pour mot, et il faut le relire après coup autant qu'avant.
En particulier : rien sur une écriture **qui change** une valeur, rien sur un
refus, un démon injoignable ou un délai épuisé, rien au-delà de `setNiveauM1`, et
aucune autorisation d'activer la voie transactionnelle — qui relève de W4-E.

**W4-C est clos. W4-D peut être ouvert. Il ne l'est pas par ce document.**
