# W4-C — Protocole de capture de l'écriture `vclient`

> **Lot W4-C — opératoire. Version 2**, après audit indépendant de la V1
> (verdict *À REVOIR* : 0 bloquant, 2 majeurs, 5 mineurs, 3 informations). Les
> deux majeurs portaient sur la **complétude de listes fermées** — le champ 11 de
> W4-A §19 et l'inconnue I-14 — et non sur la méthode, qui est conservée telle
> quelle. Ce document ne livre aucune ligne de code et ne
> modifie aucun test. Il décrit une campagne de mesure à exécuter **une fois**,
> sur l'installation de référence, par l'exploitant. Tant qu'elle n'a pas été
> exécutée et rapportée, W4-D reste fermé et aucune ligne d'arguments d'écriture
> réelle n'entre dans le produit.

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
- Il ne modifie aucun contrat : ni C5, ni W1, ni W2, ni W4-A.
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
temporaires de W4-A §11.6 et §12.3. La campagne l'éclaire, mais ne la referme
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
> interdictions de §9.1, §11.4 et §12.3. **La campagne décrite ici ne les lève
> pas toutes.** Elle établit une signature de **succès local**, donc elle lève
> §9.1 — l'interdiction de rendre `TransportStatus.OK`. Elle n'observe aucune
> défaillance d'écriture, donc :
>
> - §11.6 — l'interdiction de `DAEMON_UNREACHABLE` — **reste en vigueur**, sa
>   levée exigeant explicitement « la même signature observée sur une invocation
>   d'écriture » ;
> - §12.3 — l'interdiction de `UNKNOWN_COMMAND` — **reste en vigueur**.
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
2. C'est un **entier à égalité stricte** (A5 §5.3, tolérance de confirmation
   nulle). Le verdict de relecture est binaire : aucune question de
   représentation flottante ne peut brouiller la lecture des résultats.
3. Choisir la pente aurait mêlé la question posée — *que répond la CLI ?* — à une
   question de sérialisation flottante (I-8) que la campagne ne peut de toute
   façon pas trancher. Un datapoint entier **isole** la mesure.

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

> **Obligation.** Le timer du superviseur **MUST** être arrêté pour toute la
> durée de la campagne, et rétabli à la fin (§13). Ce n'est pas une précaution
> de confort : c'est la suppression d'un chemin de redémarrage automatique.

Point rassurant, vérifié : la sonde du superviseur interroge `vclient`
**directement**, et non le pont. Arrêter le pont ne la fait donc **pas** échouer,
et ne déclenche à lui seul aucune action du superviseur.

---

## 9. Préparation

Dans l'ordre. Aucune étape n'est facultative.

1. **Saison** — hors saison de chauffe (C5 §12.1).
2. **Présence** — l'exploitant est devant la machine, du début à la fin.
3. **Atelier** — créer `<atelier>`, vide, hors de tout dépôt versionné.
4. **Arrêter le superviseur, et le prouver** — arrêter `<timer-guard>` (§8),
   puis établir son inactivité et **consigner comment** (PR-1 ci-dessous).
5. **Arrêter le pont, et le prouver** — arrêter `<unité-pont>`, puis établir son
   arrêt effectif et **consigner comment** (PR-2). Il sonde le démon toutes les
   10 s ; le laisser tourner introduirait une contention non maîtrisée pendant la
   mesure. Son unité déclare `Restart=always`, mais un arrêt explicite n'est pas
   suivi de redémarrage automatique : c'est bien un arrêt — ce qui **reste à
   constater**, non à supposer.
6. **Vérifier le démon** — le démon `vcontrold`, lui, **reste actif**. Confirmer
   par une lecture nue avant d'aller plus loin.
7. **Armer le retour arrière** — §12, avant toute écriture.

### 9.1 Preuves d'arrêt — symétriques et consignées

W4-A §19 n° 10 exige l'état du pont pendant l'essai **« et comment cela a été
établi »**. Une assertion d'arrêt ne vaut donc rien sans sa méthode. Les deux
arrêts sont traités à la même exigence.

| Réf | Objet | Ce que le rapport **MUST** porter |
|---|---|---|
| **PR-1** | `<timer-guard>` | la méthode employée pour établir l'inactivité, sa sortie, et l'horodatage |
| **PR-2** | `<unité-pont>` | la méthode employée pour établir l'arrêt, sa sortie, et l'horodatage |

Deux preuves indépendantes valent mieux qu'une : l'état déclaré par le
superviseur de services **et** un constat d'absence d'activité observable —
typiquement, l'arrêt de la télémétrie que le pont publiait toutes les 10 s. Ni
l'une ni l'autre n'est nommée ici : ce sont des constantes de site (§4).

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
| — | **relever la valeur `V`** issue de 01 et 02, et vérifier qu'elles concordent | — |
| — | **point d'arrêt** — si 01 et 02 divergent, **abandonner** (§12) | — |
| 03 | **écriture à l'identique, `-J`** | `capture 03-ecriture-json vclient -J -h <hôte> -p <port> -c "setNiveauM1 V"` |
| 04 | relecture immédiate (≈ 1 s après) | `capture 04-apres-1s-json vclient -J -h <hôte> -p <port> -c "getNiveauM1"` |
| 05 | relecture à +10 s | `capture 05-apres-10s-json vclient -J -h <hôte> -p <port> -c "getNiveauM1"` |
| 06 | relecture, forme texte | `capture 06-apres-texte vclient -h <hôte> -p <port> -c "getNiveauM1"` |

`V` est reprise **verbatim** de la lecture, sans reformatage. Si la forme texte
et la forme `-J` ne restituent pas `V` de façon identique, c'est en soi un
résultat à consigner — et un motif d'arrêt avant l'étape 03.

Aucune étape n'est automatisée en boucle. Chaque invocation est lancée à la main,
son résultat lu, avant de décider de la suivante.

### 11.1 Garde de fraîcheur de `V`

C5 §12.3 prescrit de réécrire **la valeur courante**. Si `V` a été relevée puis
que le temps a passé, `V` n'est plus la valeur courante mais une valeur
*historique* — et l'étape 03 cesserait d'être une réécriture à l'identique pour
devenir une écriture de valeur, ce que ce protocole n'autorise pas.

> **Règle.** Au moment d'exécuter l'étape 03, `V` **MUST** être encore la valeur
> courante observée, établie par la lecture qui précède **immédiatement**
> l'écriture.

En pratique : l'étape 02 enchaîne directement sur l'étape 03. Si quoi que ce soit
s'intercale — une pause, une interruption, une hésitation, un doute levé puis
écarté — la lecture est **refaite** avant d'écrire, sous un nom de capture
incrémenté. Si la valeur relue diffère de `V`, la campagne s'arrête (AB-8) : une
valeur qui bouge toute seule signale un autre écrivain, et cette question relève
de W4-F, pas d'ici.

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
initial. Elle est comptée séparément, et son existence est elle-même un fait à
consigner.

---

## 12. Retour arrière et critères d'abandon

**Retour arrière.** L'écriture étant à l'identique, la restauration consiste à
réécrire `V` — la même commande que l'étape 03. La valeur `V` **MUST** être
relevée et notée par écrit **avant** l'étape 03, et la commande de restauration
écrite en toutes lettres avant d'être éventuellement nécessaire.

> **Nature de cette écriture.** Prescrite par C5 §12.5, elle est **conditionnelle
> et non nominale** : elle n'a lieu que si l'état constaté n'est plus `V`, et
> elle ne caractérise rien. Elle est donc hors du `WRITE NOMINAL COUNT` (§11.2),
> et la confondre avec un réessai serait une faute — le réessai est interdit, la
> restauration est due. Le rapport les distingue explicitement :
> `ecritures_nominales=1`, `ecritures_restauration=0 ou 1`.

**Abandon immédiat**, sans poursuivre la séquence, si :

| Réf | Condition |
|---|---|
| AB-1 | la valeur relue diverge de `V`, à n'importe quelle étape |
| AB-2 | les formes texte et `-J` ne concordent pas avant l'étape 03 |
| AB-3 | le démon `vcontrold` change d'état, ou devient injoignable |
| AB-4 | une invocation dépasse nettement le budget de 5 s connu (E3) |
| AB-5 | un service redémarre, ou la machine redémarre, pour quelque cause |
| AB-6 | tout doute de l'exploitant, sans justification à fournir |
| AB-7 | une durée mesurée négative, nulle ou manifestement absurde — l'horloge a bougé (§10), la mesure et les suivantes ne valent plus rien |
| AB-8 | la garde de fraîcheur de §11.1 échoue : la valeur courante n'est plus `V` avant l'étape 03 |

Après un abandon : restaurer `V`, rétablir §13, **puis** rapporter. Aucune
seconde tentative dans la même fenêtre.

> **Interdiction.** Ne **jamais** provoquer délibérément un dépassement de budget
> ni un démon injoignable pour capturer I-12, I-13 ou I-15. Ces signatures se
> recueillent si elles surviennent, elles ne se fabriquent pas sur une
> installation en service.

---

## 13. Restauration de l'état normal

Dans cet ordre, et vérifié à chaque étape :

1. confirmer par une lecture nue que la valeur en place est `V` ;
2. redémarrer `<unité-pont>` ;
3. attendre que sa télémétrie reparte (période de 10 s — une trentaine de
   secondes suffit à lever le doute) ;
4. redémarrer `<timer-guard>` ;
5. confirmer que le superviseur repasse un cycle nominal sans action corrective.

La campagne n'est close qu'après l'étape 5.

Les preuves **PR-1** et **PR-2** (§9.1) sont symétriquement redoublées ici : le
rapport porte non seulement comment l'arrêt a été établi, mais **comment la
reprise l'a été**. Un pont qu'on croit redémarré et qui ne publie plus serait la
pire issue possible de cette campagne — pire que n'importe quel résultat négatif.

---

## 14. Livrable — ce que W4-C rapporte

W4-A §19 fixe la liste. Ce protocole la couvre ainsi :

| §19 | Champ exigé | Fourni par |
|---|---|---|
| 1 | nom réel de la commande d'écriture | §7 — `setNiveauM1` |
| 2 | ligne d'invocation réelle, telle qu'exécutée | `03-ecriture-json.meta` |
| 3 | `stdout` et `stderr` intégralement et **séparément** | `.out` / `.err`, jamais fusionnés (§10) |
| 4 | code retour | `.meta` |
| 5 | durée mesurée | `.meta` |
| 6 | valeur **avant** | étapes 01–02 |
| 7 | écriture à l'identique | étape 03, conforme à C5 §12.3 |
| 8 | valeur **après**, et délai de stabilité | étapes 04–06 — **avec la réserve I-7 du §6** |
| 9 | preuve de retour arrière, armée avant l'essai | §12, armée avant l'étape 03 |
| 10 | état du pont historique pendant l'essai, **et comment cela a été établi** | **arrêté** — méthode et sortie consignées en **PR-2** ; superviseur également arrêté, **PR-1** (§9.1) |
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
| `ecritures_nominales` / `ecritures_restauration` | §11.2 et §12 |
| anomalies observées, même écartées | journal libre de l'exploitant — une anomalie écartée reste un fait |
| critère d'abandon déclenché, le cas échéant | `AB-1` … `AB-8` (§12) |

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
  §12.3 (`UNKNOWN_COMMAND`) : aucune défaillance d'écriture n'aura été observée,
  et §6.1 explique pourquoi elle ne peut pas l'être ici ;
- elle ne dit rien de l'effet d'une expiration du budget local — I-13, §14.1 —
  sauf si le phénomène survient de lui-même.

Elle établit une chose, et une seule : **ce que `vclient -J` répond quand une
écriture aboutit.** C'est exactement ce qui manque à W4-B pour cesser d'être « non
résolu pour l'invocation réelle ».
