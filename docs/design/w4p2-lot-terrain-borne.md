# `W4-P2` — second lot terrain borné : clôtures et durée de session

> **Version 14**, après réaudit. Quatre bloqueurs et une incohérence.
>
> | | Correction |
> |---|---|
> | **V14 · RB12-1** | une **ligne vide** subsistait dans le tableau du §8.1.3, entre *« Ce qui s'y fait »* et *« Ce qui ne s'y fait pas »* — les deux lignes n'étaient donc **toujours pas** dans le même tableau. Supprimée |
> | **V14 · RB12-2** | **le §7 portait encore l'ancienne règle de comptage** — *« le nombre de redémarrages du démon commandés par `M5` et `S3` »* — que le §7.1 avait corrigée en **nombre de propagations QUALIFIÉES**. La définition normative **contredisait** sa propre conduite d'évaluation. Les deux sont désormais **alignées mot pour mot** |
> | **V14 · RB12-3** | **le dernier `donc P2A-6`** subsistait dans le tableau du sort des preuves de `P2A-2` / `P2A-3`. Retiré ; **tout renvoie à la conduite unique du §7.1** |
> | **V14 · RB12-4** | **`COMPTE SUPÉRIEUR` requalifiait automatiquement en `REDÉMARRAGE NON ATTRIBUÉ`** — y compris un identifiant dont la qualification avait été **légitimement abandonnée par préemption**. Le §7.1 **trie** désormais les identifiants excédentaires, et **réserve `REDÉMARRAGE NON ATTRIBUÉ`** à ceux qui sont **réellement sans attribution hors préemption** |
> | **V14 · C-33** | l'historique de la **V8** énonçait l'ancienne règle de comptage sans marquer qu'elle a été **remplacée** |
>
> **Version 13**, après réaudit. Quatre bloqueurs et trois incohérences.
>
> | | Correction |
> |---|---|
> | **V13 · RB11-1** | la note de `C-28` était **dans** le tableau du §8.1.3, laissant la ligne *« Ce qui ne s'y fait pas »* **orpheline** après elle. Sortie du tableau, qui redevient **continu** |
> | **V13 · RB11-2** | **§7.1 ne couvrait qu'UNE des trois composantes de `R5.e`.** Le **compte**, l'**attribution** et l'**état du pont en sortie** reçoivent désormais chacun leurs verdicts — dont **compte inférieur**, **compte supérieur** et **pont non nominal**. Et le **compte attendu** est corrigé : c'est le nombre de **propagations qualifiées**, non celui des commandes, faute de quoi le cas **« zéro propagation »** admis nominalement ferait échouer `R5.e` |
> | **V13 · RB11-3** | **contradiction supprimée** : la séquence de `P2A-2` / `P2A-3` prescrivait encore `P2A-6` **automatiquement** sur un échec de `R5.e`, alors que le §7.1 en fait un **constat de sortie**. La conduite d'échec est **alignée partout** |
> | **V13 · RB11-4** | **`P5` reposait de fait sur la seule observation historique.** La **relation configurée** entre à part entière dans son verdict : `P5` = **preuve structurelle ET preuve historique**, `ÉTABLIE` **seulement si les deux concordent**. **Une observation historique seule ne suffit jamais**, et `P6` consigne la relation configurée **et son moyen de preuve** |
> | **V13 · C-30** | §8.2.1 nomme **`P6`** comme l'acte de consignation dû |
> | **V13 · C-31** | §6.1 renommé : il couvre **lecture ET consignation hors dépôt** |
> | **V13 · C-32** | §7.1 : *« en toute fin de lot »* ne valait pas pour la séquence spéciale de `P2A-2` / `P2A-3`. Reformulé |
>
> **Version 12**, après réaudit. Quatre bloqueurs et trois incohérences.
>
> | | Correction |
> |---|---|
> | **V12 · RB10-1** | **`P5` vérifiait la PRÉSENCE des quatre événements, pas leur ORDRE** — alors que `(a)` exige un ordre précis. Une installation les émettant tous, dans le désordre, aurait été déclarée `ÉTABLIE` puis aurait échoué à `(a)` **après mutation**. Le critère porte désormais **sur l'ordre** |
> | **V12 · RB10-2** | **le verdict de `P5` n'avait aucun acte pour être consigné.** Nouvel acte **`P6`**, dans la liste close : il consigne le verdict, **identifie le redémarrage historique** employé et **la fenêtre de journal** lue |
> | **V12 · RB10-3** | **l'échec de `R5.e` en sortie était un trou de procédure.** Nouveau §7.1 : trois verdicts explicites, dont celui de l'**attribution abandonnée par préemption**, qui est **légitime** et non une faute. **Aucun acte terrain nouveau, aucune nouvelle tentative** |
> | **V12 · RB10-4** | la note de `C-24` était **à l'intérieur** du tableau du §8.3.2 et le **coupait en deux**. Sortie du tableau, qui redevient **continu** |
> | **V12 · C-27** | §6.1 annonçait *« cinq lignes »* — il y en avait **six**, et **`P6` en fait sept** |
> | **V12 · C-28** | §8.1.3 énumérait `S4` à **`S9`** parmi les actes de la fenêtre — or **`S9` n'y appartient pas** : son rang est **après** la qualification. Énumération arrêtée à **`S8`** |
> | **V12 · C-29** | §8.1.2.1 affirmait *« par construction »* un comportement d'ordonnancement **qu'aucune pièce n'établit**. L'assertion est retirée et renvoyée au **verdict de `P5`** |
>
> **Version 11**, après réaudit. Quatre bloqueurs et cinq incohérences — dont
> une précondition qui **manquait entièrement** et que la V10 signalait en réserve.
>
> | | Correction |
> |---|---|
> | **V11 · RB9-1** | **`S9` et `M5 bis` / `S3 bis` étaient confondus dans leur office.** Les seconds **qualifient localement**, au moment utile ; `S9` **dénombre globalement**, à la sortie. **`S9` ne qualifie ni n'attribue rétrospectivement.** Tout redémarrage dénombré qui **n'a pas été qualifié localement** est **NON ATTRIBUÉ**, et `R5.e` **échoue** |
> | **V11 · RB9-2** | **`S9` est dû sous `P2A-2` / `P2A-3` mais ne figurait pas dans leur séquence close.** Il y est inséré, **à son rang**, et les preuves associées sont statuées |
> | **V11 · RB9-3** | **`(c)` n'était pas mesurable.** `M6` ne relevait pas l'identifiant d'invocation du démon, et **l'instant exact de la commande** de `M5` / `S3` n'était relevé nulle part. Les deux le sont désormais, et le **terme comparé** entre journal et propriétés d'unité est **nommé** |
> | **V11 · RB9-4** | **La précondition qui rend `(a)` et `(c)` praticables n'existait pas.** La V10 la portait en réserve : *« que le journal porte ces événements n'est pas établi »*. Nouvel acte de préflight **`P5`**, en **lecture seule et AVANT toute mutation** — et un **`STOP AVANT MUTATION`**, distinct d'un `ABORT` terrain, si elle n'est pas démontrable |
> | **V11 · C-22** | **`S9`** est **placé dans le temps** : après la fin de la qualification de `S3` **et** après retour du pont à nominal |
> | **V11 · C-23** | **condition 3** exprimée directement : *« exactement un identifiant nouveau **par rapport au baseline ET à ceux déjà dénombrés** »* |
> | **V11 · C-24** | **élargissement implicite d'`O2` retiré** : le **journal du pont** appartient à `M5 bis`, `S3 bis` et `S9` — **jamais à `O2`** |
> | **V11 · C-25** | **§8.1.3** nomme désormais **`M5 bis` et `S3 bis`** parmi les actes permis pendant la qualification |
> | **V11 · C-26** | **`(a)` énumère exactement les mêmes événements que sa clause de repli** |
>
> **Version 10**, après réaudit. Huit bloqueurs et quatre incohérences — dont
> une brèche que la V9 **signalait elle-même sans la fermer**.
>
> | | Correction |
> |---|---|
> | **V10 · RB8-1** | §6.3.1 disait *« à la phase 3 — et à elle seule »* alors que son contenu étendait déjà `O2` à la **phase 1**. Titre et clauses de fermeture **mis en accord** |
> | **V10 · RB8-2** | *« `O2` seulement, aucune autre lecture »* **interdisait `M6` et `S4`…`S8`** pendant la qualification — le lot se serait bloqué lui-même. Remplacé par une règle qui **autorise les actes normaux de la phase** et **n'interdit que les actes hors liste close** |
> | **V10 · RB8-3** | le cas **« zéro redémarrage du pont »** n'était pas écrit. Il l'est : **aucune qualification à conduire, aucun `ABORT`, poursuite normale** |
> | **V10 · RB8-4** | **la brèche du tiers acteur est fermée.** La V9 attribuait par **fenêtre + superviseur inactif** — deux conditions **négatives**. Le §8.1.2.1 exige désormais une **PREUVE STRUCTURELLE POSITIVE** : la transition de `<unité-démon>` doit être **strictement encadrée** par l'arrêt et le démarrage de `<unité-pont>`. **À défaut de pouvoir l'établir, la propagation demeure NON QUALIFIÉE** |
> | **V10 · RB8-5** | `R5.e` ne reposait que sur **deux fenêtres de `60 s`** et ne couvrait pas la durée du lot. Nouvel acte **`S9`** : lecture rétrospective **complète** du journal du pont en sortie |
> | **V10 · RB8-6** | *« transition »* était **ambigu**. L'unité comptée devient le **nouvel identifiant d'invocation du pont, RELATIVEMENT AU BASELINE de `P2 bis`** — jamais « tous les distincts ». §8.1.2.2 et `R5.e` alignés |
> | **V10 · RB8-7** | `R5.e` devenait **improuvable après un `ABORT`**. L'abandon de la qualification **prospective** n'interdit pas la **collecte rétrospective** : `S9` est dû **y compris** après `ABORT` ou préemption |
> | **V10 · RB8-8** | §8.3.2 disait *« journal système de la seule `<unité-superviseur>` »* — **devenu faux**. `D-1` s'appuie désormais **aussi** sur le journal du pont |
> | **V10 · C-18** | tableau `P2A-2`/`P2A-3` : statut de **`R5.e`** rendu explicite |
> | **V10 · C-19** | §9 point 4 aligné sur l'exception de redémarrage du pont **déjà arbitrée** |
> | **V10 · C-20** | en-tête V8 : renvoi **`§3.3` → `§3.0`** |
> | **V10 · C-21** | §6.2 : **`M5 bis`** replacé dans l'ordre logique, **entre `M5` et `M6`** |
>
> **Version 9**, après audit du correctif. Quatre bloqueurs — dont deux qui
> rendaient les conditions de la V8 **invérifiables avec les actes permis**.
>
> | | Correction |
> |---|---|
> | **V9 · RB7-1** | **Les cinq conditions du §8.1.2 n'avaient AUCUN acte pour les vérifier.** `O2`, à 15 s d'intervalle, ne couvre pas la fenêtre de `60 s`. Deux actes de lecture sont ajoutés à la liste close : **`M5 bis`** autour de `M5`, **`S3 bis`** après `S3` |
> | **V9 · RB7-2** | **La condition « unique » n'était pas observable.** Un échantillonnage à 15 s ne distingue pas une transition de deux. Le canal devient le **journal système du pont, lu rétrospectivement**, qui porte **toutes** les transitions et leurs **identifiants d'invocation**. **`NRestarts` cesse d'être le compteur** et devient une **corroboration**. `R5.e` est portée par des actes explicites |
> | **V9 · RB7-3** | **Un redémarrage causé par le superviseur pouvait être absorbé** comme propagation de `S3` : la V8 n'attribuait que **temporellement**. L'attribution devient **structurelle** — le superviseur **inactif de bout en bout** ne peut pas avoir commandé le redémarrage, sa commande n'existant que dans un script qui ne tourne que pendant son activité. **`<unité-superviseur>` nominal** reçoit une **définition** et une **fenêtre d'observation**. **En cas de doute, `D-1` demeure confirmateur du `STOP`** |
> | **V9 · RB7-4** | **La conduite pendant la qualification différée n'était pas écrite.** Nouveau §8.1.3 : `O2` s'y poursuit, **`D-2` / `P2A-12` demeurent préemptifs**, **aucune attente volontaire à travers les 90 s**, et une qualification **non acquise à temps ou douteuse** est un **`ABORT` avec `STOP`** |
> | **V9 · C-14** | **`NRestarts` requalifié** : *« la propagation ne l'incrémente pas »* était présenté comme une propriété ; ce n'est qu'une **observation terrain, faite deux fois** |
> | **V9 · C-15** | la phrase de **`P2A-5`** est alignée sur l'exception désormais admise |
> | **V9 · C-16** | ordre logique rétabli : **§8.1.1 avant §8.1.2**, et §9 en `1, 2, 2 bis, 3, 3 bis, 3 ter, 3 quater, 4` |
> | **V9 · C-17** | le **renvoi au §3.0** est écrit là où il manquait ; le `vcontrold` littéral du §8.1.2 devient **`<unité-démon>`** |
>
> **Version 8 — LOT CORRECTIF, après une EXÉCUTION TERRAIN ABORTÉE.**
>
> La V7 a été autorisée et exécutée. Elle s'est arrêtée **188 secondes après
> l'ouverture de la fenêtre**, sur `P2A-6` : le **pont a redémarré**, à l'instant
> exact du redémarrage du démon.
>
> | | Correction |
> |---|---|
> | **V8 · fait établi** | **`<unité-pont>` REQUIERT `<unité-démon>`, ce qui rend le redémarrage du pont INÉVITABLE.** Le fait `F-13` est ajouté au §3, et le **§3.0** en tire la conséquence : l'exclusion que la V7 se donnait — *« toute modification du pont »* — était **inatteignable par construction** avec la voie retenue. Ce n'était pas un aléa, c'était un **défaut de conception du bornage** |
> | **V8 · `P2A-6` remplacée** | le redémarrage du pont **provoqué par `M5` ou `S3`** n'est plus un `ABORT` **s'il correspond exactement à la propagation attendue**, définie par **cinq conditions cumulatives** au §8.1.2. **Tout autre redémarrage, tout redémarrage supplémentaire, toute origine inconnue, tout comportement non nominal demeurent un `ABORT`** |
> | **V8 · `D-1` qualifié** | il détectait *« le pont a été redémarré → `F-12` engagé »*. Sans qualification, il aurait déclenché `P2A-5` sur la propagation **attendue**. Il exclut désormais celle-ci, **et elle seule** |
> | **V8 · périmètre et `STOP`** | l'exclusion du §4 et la clause de `STOP` du §8.2 sont mises en accord avec l'arbitrage : la **propagation attendue** est acceptée, bornée et observée ; **toute autre atteinte au pont demeure exclue et demeure un `STOP`** |
> | **V8 · `R5.e`** | la restauration doit désormais prouver **le pont ET le démon** : le nombre de redémarrages du pont est **compté et attribué**, et doit égaler exactement le nombre de redémarrages du démon |
>
> **La piste « neutraliser temporairement la dépendance » est EXCLUE par
> arbitrage** : ce serait une modification plus profonde du dispositif historique
> pour éviter un redémarrage désormais **compris et réversible**.
>
> **Aucun autre changement de conception.** La synchronisation, les objectifs, la
> liste close, la fenêtre et toutes les autres preuves sont **inchangés**.

> **Version 7**, après sixième audit. Un bloqueur : la surveillance exigée
> pendant l'attente n'était **permise par aucun acte** à ce moment-là.
>
> | | Correction |
> |---|---|
> | **V7 · RB6-1** | **`O2` était un acte de la PHASE 2 seule.** Or le §8.1.1 exige que la surveillance **se poursuive pendant l'attente d'un retour synchronisé `S1`** — laquelle appartient à la **phase 3**. La préemption par `P2A-12` y était donc **prescrite sans acte pour l'observer**. `O2` est **étendu à la phase 3**, **strictement** pour cette surveillance et sa préemption, à la **même fréquence**, et jusqu'à l'un des deux termes nommés. **Aucune autre extension de périmètre** |
> | **V7 · C-12** | la ligne vive de **`P2A-11`** au §8.1 annonçait un retour *« synchronisé »* **sans réserve**, ce que le §8.1.1 contredit pour une invocation **en cours**. Alignée |
> | **V7 · C-13** | le cas **`[5 s, 10 s)` EN COURS** ne disait pas s'il emportait le **`STOP`**. **Tranché et écrit** : la conduite de retour est **toujours** immédiate ; le `STOP` est dû **si et seulement si** le chemin d'échec est **confirmé** — et **le doute vaut confirmation** |
>
> **Version 6**, après cinquième audit. Deux bloqueurs, dont un chemin qui
> aurait fait **attendre** le lot au pire moment possible.
>
> | | Correction |
> |---|---|
> | **V6 · RB5-1** | **La précédence entre `P2A-11` et `P2A-12` n'était pas réglée.** `P2A-11`, franchi à `5,000 s`, imposait un retour **synchronisé** — c'est-à-dire une **attente**. Or, sur une invocation **encore en cours**, la durée peut continuer de croître vers le chemin d'échec : le lot aurait attendu une frontière de cycle **pendant que les 90 s s'écoulaient**. Le §8.1.1 règle la précédence, traite séparément les relevés **`[5 s, 10 s)`** et **`≥ 10 s`**, et pose la règle absolue : **aucune attente volontaire à travers les 90 s** |
> | **V6 · RB5-2** | **Une mention résiduelle de « fraction choisie » subsistait** pour `P2A-11`, héritée de la V4 et contredisant le §8.1, le §8.4 et le §9. Retirée. **`P2A-11 = 5,000 s` est DÉRIVÉ, et n'est soumis nulle part comme choix humain** |
> | **V6 · C-10** | l'ordre du §9 est rétabli : `3`, `3 bis`, `3 ter`, `3 quater` |
> | **V6 · C-11** | sous `P2A-2` / `P2A-3`, le sort de **`R3`**, **`R4`** et **`R6`** est explicité — **sans objet**, chacun avec son motif |
>
> **Version 5**, après quatrième réaudit. Trois bloqueurs, dont un qui aurait
> fait avorter le lot sur un cycle **nominal**.
>
> | | Correction |
> |---|---|
> | **V5 · RB4-1** | **`P2A-11 = 4,000 s` était SOUS le régime observé.** `W4-P1` a relevé des enveloppes d'invocation nominales allant jusqu'à **4,682 s** : le seuil aurait été franchi par des cycles **parfaitement nominaux**, et — `P2A-11` alimentant `D-2`, qui alimente `P2A-5` — un cycle nominal aurait été **interprété comme le chemin d'échec de `F-12`**. C'est la régression que `W4-P1` V3 avait déjà corrigée sous `P2A-3c`. **Les deux garde-fous sont refondus et découplés** : `P2A-11` devient un `ABORT` **ordinaire** d'allongement, au budget dérivé, **faux positif assumé** ; `P2A-12` devient la détection du **chemin d'échec**, à un seuil **choisi au-dessus du régime observé**, et **lui seul** alimente `D-2` et `P2A-5` |
> | **V5 · RB4-2** | **La structure du §6.1 était cassée** : une note explicative se trouvait **entre deux lignes du tableau**, rendant ambiguë l'appartenance de `P3` et `P4` à la liste close. `P1`, `P2`, `P2 bis`, `P3`, `P4` sont désormais **cinq lignes contiguës**, et la note est **hors du tableau** |
> | **V5 · RB4-3** | **La séquence d'`ABORT` sous `P2A-2` / `P2A-3` omettait `R2`.** L'invariance des fichiers d'origine n'était portée par aucun acte dans ce cas. La séquence devient **`S1` → `S2` → `S7` → `S4` restreint aux empreintes → `O4`** |
> | **V5 · C-8** | la formulation de `C-5` disait *« la tolérance est retirée »*, ce qui pouvait se lire comme un retrait sur l'installation. Corrigée : c'est **sa mention dans le raisonnement du §4.2** qui a été retirée |
> | **V5 · C-9** | l'**état de `<unité-démon>`** au préflight est rétabli explicitement dans `P2` — la V4 l'avait réduit à l'invocation, à l'identifiant et au compteur de relances |
>
> **Version 4**, après troisième réaudit. Trois bloqueurs, tous d'exécutabilité.
>
> | | Correction |
> |---|---|
> | **V4 · RB3-1** | **Deux seuils n'avaient aucune valeur, et se renvoyaient l'un à l'autre.** `P2A-11` disait *« une fraction, soumise au §8.4 et au §9 »* ; le §8.4 disait *« la fraction de `P2A-11` »* ; le §9 renvoyait au §8.4. **Le renvoi était circulaire et la valeur n'existait nulle part** — le lot était inexécutable. Idem pour la réserve du §8.3.4. **Les deux valeurs sont désormais écrites**, classées **choisies**, et soumises nommément |
> | **V4 · RB3-2** | **Le préflight ne relevait pas les références du pont et du superviseur.** `D-1` et `P2A-6` comparent des identifiants d'invocation et des instants de démarrage à un état antérieur — **qui n'était pas capturé**. Ils auraient donc été **inopérants au premier redémarrage de la phase 1**. `P2` les relève désormais ; `S8` demeure la mesure finale comparative |
> | **V4 · RB3-3** | **L'exception `P2A-2` / `P2A-3` était incomplète** : elle omettait la preuve d'absence `S7` et le relevé partiel `R7`. Elle est complétée, `S3` restant interdit faute de redémarrage. Et **`O4` devient explicitement admissible dans TOUTE phase** dès qu'un `ABORT` survient |
> | **V4 · C-4** | le premier bras de `D-2` — *« un instant de démarrage ancien »* — **n'était pas quantifié**. Il est remplacé par une comparaison au **seuil de `P2A-11`**, applicable à une invocation **terminée ou en cours** |
> | **V4 · C-5** | la **mention de la tolérance de 10 s** est retirée **du raisonnement du §4.2** — la tolérance demeure ce qu'elle est dans la configuration ; elle ne **portait** rien ici, la marge de ≥ 180 s tenant sans elle |
> | **V4 · C-6** | la phrase *« aucune valeur de site »* était **fausse** : le document porte des **grandeurs mesurées** sur l'installation. Elle est corrigée en ce qu'elle disait vraiment — aucun **identifiant** de site |
> | **V4 · C-7** | l'historique est remis dans l'ordre **1, 2, 3, 4** |
>
> **Version 3**, après réaudit. Quatre bloqueurs, dont un qui rendait le
> garde-fou principal aveugle une fois sur trois.
>
> | | Correction |
> |---|---|
> | **V3 · RB-1** | **Le journal du superviseur cesse d'être le canal unique de détection.** `W4-P1` a homologué que **24 invocations sur 76 ne produisent aucune ligne propre** : un échec de sonde pouvait donc survenir **sans trace lisible**. Le §8.3 fonde désormais la détection sur **trois signaux indépendants des lignes propres**, dont deux portent sur des états que systemd tient pour **toutes** les invocations. **Aucune hypothèse n'est formée sur la cause des absences de trace** |
> | **V3 · RB-2** | **La fausse borne est retirée.** *« ≤ 15 s + un délai non établi »* n'est pas une borne. La conduite est reconstruite sur les **durées réellement opposables** — les 90 s déclarées de `F-12` —, la **bascule arbitraire à 45 s est supprimée**, et la marge restante est désormais **calculée sur un observable**. La règle de sûreté est explicite : **ne jamais laisser volontairement la verbosité élevée traverser une seconde sonde** dès qu'un échec est suspecté, si une conduite plus sûre existe |
> | **V3 · RB-3** | **Chaque preuve a maintenant son acte.** `R1` — absence du répertoire de surcharge — et `R5.d` — état nominal et compteurs de relances du pont et du superviseur — n'étaient portées par **aucun acte de la liste close**. Actes **`S7`**, **`S8`** ajoutés, ainsi que **`O4`** pour le relevé partiel de `R7` |
> | **V3 · RB-4** | **§8.4 et l'autorisation rendus cohérents.** Les seuils **dérivés du corpus** cessent d'être présentés comme des choix ; seuls les seuils **choisis humainement** sont soumis. **`P2A-11` est reformulé** : sa référence ambiguë au maximum relevé par `W4-P1` — sur une population que son homologation déclare **non homogène** — est remplacée par une **fraction du budget déclaré de 5 s**, sur une population **sans ambiguïté**. **`P2A-12` reste une donnée dérivée**, jamais un choix |
>
> **Version 2**, après audit. Quatre bloqueurs fermés, trois corrections.
>
> | | Correction |
> |---|---|
> | **V2 · BL-1** | **Trois défauts liés.** La V1 fondait la marge de synchronisation sur l'**enveloppe d'invocation** relevée par `W4-P1` — ce qui la traitait en **borne de sonde**, précisément ce que son homologation interdit. La marge est refondée sur les **seules données admissibles** : la **cadence déclarée** et le **budget déclaré de 5 s**. Et les objectifs, nommés `B-O1`…`B-O5`, **entraient en collision** avec `B-O1` et `B-O2` déjà homologués sous `W4-P1` : ils deviennent **`P2-O1`…`P2-O5`** |
> | **V2 · BL-2** | **La latence de détection de `P2A-5` est bornée.** La V1 exigeait un « retour immédiat » sans dire à quelle vitesse le déclencheur serait vu, ni par quel canal. Le §8.3 fixe le **canal**, la **fréquence maximale d'observation**, et **suspend la synchronisation** pour ce cas — attendre une frontière de cycle aurait consommé le budget de 90 s qui sépare du redémarrage machine |
> | **V2 · BL-3** | **Le §E.3 du cadrage devient un RISQUE DE SÛRETÉ**, non un caveat d'observation. L'allongement des sessions rapproche la sonde de son budget déclaré, et le §5.1 en tire deux `ABORT` opposables — `P2A-11` et `P2A-12`. **Aucune qualification de `C1`, aucune borne déterministe** n'en est tirée |
> | **V2 · BL-4** | **Le quatrième constat de sortie du §F.2 est restauré INTÉGRALEMENT** : processus unique **ET détenteur du périphérique** ET servant ses clients. La V1 avait perdu la détention. Les moyens de preuve sont ceux de l'**Acte A** — deux méthodes indépendantes — et les actes correspondants sont **ajoutés à la liste close** |
> | **V2 · C-1** | `428 × 7 = 2 996` : le *« ≥ 3 000 lignes »* de la V1 était **faux**. Corrigé en valeur exacte |
> | **V2 · C-2** | nouveau §8.4 : les **seuils internes d'`ABORT`** sont distingués des **seuils produits comme résultat**. Ce lot ne produit **aucun** seuil du second genre |
> | **V2 · C-3** | les seuils de **`P2A-7`** deviennent des **choix soumis à l'autorisation**, au même titre que la fenêtre |
>
> **Version 1.** Ouverture et bornage initial.

> **LOT BORNÉ, PAS EXÉCUTÉ.** Ce document borne une expérience
> comportant une **mutation temporaire et réversible**, et réunit les six éléments
> exigés. **L'élément 6 — autorisation propre — n'est PAS donné par ce document.**
>
> **Aucun seuil, aucun critère, aucune borne qualifiée, aucun `M6`. `C1` n'est pas
> rouverte. `T0` demeure NON AUTORISÉ, `T1` n'est pas approché.**

---

## 1. Désignation et repères

Le lot est désigné **`W4-P2`**. Désignation vérifiée libre : dix-neuf
désignations `W4` sont en usage, `W4-P1` comprise ; aucun `W4-P2` n'existait.

`W4-P2` est un **sous-lot d'expérience de `W4-P`**. Il n'est pas une phase de
`T0`, et **MUST NOT** être présenté comme en tenant lieu.

| Repère | Objet |
|---|---|
| `<unité-démon>` | l'unité de `vcontrold` |
| `<config-démon>` | le fichier de configuration déployée de `vcontrold` |
| `<journal-démon>` | le puits persistant fichier du démon |
| `<dropin-démon>` | le répertoire de surcharge systemd de `<unité-démon>` — **inexistant à ce jour** |
| `<unité-pont>` | l'unité du pont historique |
| `<timer-guard>` · `<unité-superviseur>` | le déclencheur périodique et l'unité du superviseur |

**Aucun IDENTIFIANT de site n'est écrit dans ce document** — ni chemin, ni hôte,
ni port, ni nom d'unité, ni sujet. L'invocation d'origine du démon est désignée
comme telle ; elle est relevée au préflight.

> **Ce document porte en revanche des GRANDEURS mesurées sur l'installation** —
> taille du journal, espace libre, cadence de connexion, décomptes du §3. La V3
> écrivait *« aucune valeur de site »*, ce qui était **faux** : ces grandeurs en
> sont. Elles sont conservées parce qu'elles **fondent le bornage**, et elles ne
> désignent rien.

## 2. Contexte opposable

| Source | Ce qu'elle établit |
|---|---|
| `w4p1-homologation.md` | `Command:` **ne permet pas** d'isoler les sondes du superviseur : toute sa population déclarée emploie une commande que le pont emploie aussi. **Cette piste est fermée sous le registre établi**, et `W4-P2` ne la rouvre pas |
| `w4f1a-upstream-characterization.md` §10.3 | `Closed connection (fd:%d)` **existe** dans le code, au niveau `LOG_INFO` |
| `w4a-acte-a-constat.md` §10 | `debug` effectif = **`false`** ; les types `LOG_INFO` comptent **0** occurrence |
| `w4-cadrage-activation-debug.md` **§B.3 (a)** | la voie `dbgFD` **ne peut structurellement pas** observer le trafic d'un autre client : sous `-n`, la session observatrice **bloque le service** |
| `w4-cadrage-activation-debug.md` **§D.3** | **aucune route ne dispense du redémarrage** : ni `reload`, ni `SIGHUP` ne propagent `debug` vers les puits persistants |
| `w4-cadrage-activation-debug.md` **§F.2** | l'état de sortie **MUST être constaté**, par quatre contrôles indépendants |
| `w4-cadrage-activation-debug.md` **§E.1** | le volume sous `debug` est *« une donnée manquante à établir **avant** toute activation »* ; plancher **≥ 7 lignes par session** |

> **La mutation est donc NÉCESSAIRE, et le corpus l'établit.** Les deux voies sans
> redémarrage sont fermées : `dbgFD` ne voit que sa propre session, et le
> rechargement à chaud ne propage pas `debug`. **Il n'y a pas de route douce.**

## 3. Faits établis par l'audit de bornage, en lecture seule

Conduit sur l'installation réelle, sans aucune mutation, pour combler ce que le
corpus déclarait non établi.

| # | Fait établi |
|---|---|
| **F-1** | l'option **`-g` / `--debug` existe dans le binaire déployé** — chaîne d'usage lue par `strings`, **binaire non exécuté**, méthode de l'Acte A |
| **F-2** | l'**invocation effective** du processus est celle de l'unité, sans option de journalisation ; le processus tourne sous un compte **non privilégié**, comme le §F.2 du cadrage le relevait déjà |
| **F-3** | **aucun répertoire de surcharge n'existe** pour `<unité-démon>` |
| **F-4** | **`xmllint` est ABSENT de l'hôte** — aucune validation préalable du XML n'est possible |
| **F-5** | **`systemd-analyze` est présent** — la voie surcharge est **validable avant redémarrage** |
| **F-6** | **aucune rotation** ne couvre `<journal-démon>` : aucune entrée `logrotate` ne le mentionne |
| **F-7** | `<journal-démon>` pèse **502 140 225 octets** ; sa partition offre **≈ 51 Gio libres**, occupation **9 %** |
| **F-8** | **cadence de connexion ≈ 2,105 s** — 2 991 `Client connected` sur **6 298 s** |
| **F-9** | **`FD:5` est CONSTANT** sur les 2 991 connexions relevées |
| **F-10** | les **ports source sont variables** — 2 693 valeurs distinctes — mais la ligne de **clôture ne porte que le descripteur**, non le port |
| **F-11** | trois séquences `Received SIGPIPE` / `Error writing to socket` figurent au journal sur ≈ 1 h 45 : **des sessions se terminent anormalement**, avant le lot et indépendamment de lui |
| **F-12** | le superviseur, sur échec de sonde, **redémarre le pont**, attend **90 s**, resonde — et **si la seconde sonde échoue, il redémarre la machine**. Établi par le relevé `A1` figé de `W4-P1`, registre **configuration déclarée** |

> **`F-13`** — **l'unité `<unité-pont>` porte une directive `Requires=` visant
> `<unité-démon>`.**
> Établi par la définition d'unité lue au titre de `A3` sous `W4-P1`, et
> **confirmé par l'exécution terrain de la V7**.

### 3.0 Ce que `F-13` impose, et que la V7 n'avait pas vu

**Un redémarrage de `<unité-démon>` redémarre `<unité-pont>`.** C'est le fait
`F-13`, et c'est une
propriété de la dépendance systemd, pas un incident : l'unité qui **requiert** un
service le suit lorsqu'il est relancé.

> **La V7 se donnait une exclusion inatteignable.** Son §4 excluait *« toute
> modification du pont historique […] état »*, alors que sa voie — la surcharge
> `-g`, qui **exige un redémarrage** (§D.3 du cadrage) — la rendait
> **impossible à tenir par construction**. **Ce n'était pas un aléa : c'était un
> défaut de conception du bornage**, et l'exécution terrain l'a révélé en
> 188 secondes.

**Ce que l'exécution a effectivement observé** — et qui fonde le §8.1.2 :

| | |
|---|---|
| à `M5` | démon redémarré ; **`InvocationID` du pont changé**, instant de démarrage porté à **l'instant même** du redémarrage |
| à `S3` | même propagation, le pont revenant actif **quelques dizaines de secondes** après |
| dans les deux cas | **`NRestarts` du pont est demeuré à 0** — **OBSERVATION TERRAIN, faite deux fois**, et **non une propriété démontrée** de systemd. Le §8.1.2 ne s'en sert **pas** comme compteur |
| le superviseur | **est demeuré nominal**, sans échec de sonde, sans escalade |

> **Conséquence pour la détection.** Le premier bras de la `P2A-6` de la V7 — le
> compteur de relances — **était aveugle** à cet événement. Seul le second bras,
> l'identifiant d'invocation et l'instant de démarrage, l'a vu. **Cette asymétrie
> est conservée et exploitée** au §8.1.2.
>
> **Mais elle ne fonde aucun comptage.** Deux observations ne font pas une règle :
> le §8.1.2 compte les transitions **par le journal**, et ne retient `NRestarts`
> que comme **corroboration**.

### 3.1 Ce que `F-9` et `F-10` impliquent pour l'appariement

**L'appariement par descripteur est sans contenu** : le descripteur est constant.
Le port, qui varie, **n'apparaît pas** sur la ligne de clôture.

> **Il ne resterait donc que l'ordre.** Sous `-n`, le service est strictement
> séquentiel : ouvertures et clôtures devraient **alterner**. C'est une
> **hypothèse d'appariement**, et `F-11` montre déjà qu'elle peut être mise en
> défaut par des terminaisons anormales. **La vérifier est l'objet `P2-O2` du §5.**

### 3.2 Le volume, désormais chiffrable

`F-8` fournit la donnée que le §E.1 du cadrage exigeait. Pour une fenêtre de
**15 minutes** : **900 s / 2,105 s ≈ 428 sessions**, soit **≈ 2 996 lignes** au
plancher de sept lignes par session, et quelques multiples de ce nombre au plus.

> **Correction de la V1**, qui écrivait *« ≥ 3 000 lignes »* : `428 × 7 = 2 996`.
> Le plancher est **inférieur** à 3 000, et l'arrondi allait dans le mauvais sens.

> **Rapporté à `F-7`, le risque de saturation est négligeable pour une fenêtre
> courte** — et il ne le serait pas pour une fenêtre longue, `F-6` établissant
> qu'aucune rotation ne reprend l'espace.

## 4. Élément 1 — Périmètre

**Le lot a trois phases, et trois seulement** : préflight en lecture · fenêtre
d'observation sous verbosité élevée · retour au régime initial et constat de
sortie.

**Voie retenue : SURCHARGE SYSTEMD portant `-g`. La voie XML est ÉCARTÉE.**

| | Voie XML | **Voie surcharge, retenue** |
|---|---|---|
| Objet modifié | le fichier portant périphérique, port, journal, privilèges et jeu de commandes | **un fichier neuf**, dans un répertoire **qui n'existe pas encore** |
| Validation préalable | **impossible** — `F-4` | **possible** — `F-5`, plus l'affichage de l'invocation résultante **sans redémarrage** |
| Échec de configuration | **fatal au démarrage**, puis boucle de relance — et `F-12` mène alors au **redémarrage machine** | l'unité ne démarre pas ; même boucle, mais **surface d'une seule ligne**, validée avant |
| Fichiers d'origine | **modifiés** | **jamais touchés** — leurs empreintes prouvent l'invariance |
| Retour | ré-éditer, relancer | **supprimer le répertoire**, relancer |
| Précédence | cède devant la ligne de commande | **l'emporte** — `w4-cadrage-activation-debug.md` §D.5 |

**Le périmètre exclut, explicitement** : toute écriture chaudière · tout démarrage
de Boilerack · **toute modification du superviseur** — fichiers, unité, état ·
**toute modification du pont historique**, à **une exception nommée et à une
seule** — la **propagation attendue** du §8.1.2, acceptée par arbitrage humain,
**bornée et observée** ; **aucun fichier, aucune unité, aucune configuration du
pont n'est touché**, et **rien d'autre de son état** · toute modification de
`<config-démon>` · toute
modification du fichier d'unité lui-même · toute suppression ou rotation de
`<journal-démon>` — le §F.1 du cadrage en fait un **troisième acte**, hors lot ·
toute session cliente ouverte sur le démon par le lot · `T0`, `T1`, `T2` · les
quatre actes réservés du `w4f-write-sovereignty.md` §11.1.

### 4.1 Fenêtre et synchronisation

| | |
|---|---|
| Fenêtre sous verbosité élevée | **une seule**, continue, **bornée à 15 minutes** |
| Cycles utiles visés | **au moins 3 cycles du superviseur** — à la **cadence déclarée**, 3 × 180 s = **9 min**, d'où le plafond ci-dessus avec sa marge |
| Terminaison anticipée | **exigée dès que la matière suffit** aux objectifs du §5 |
| Les **deux** redémarrages | **synchronisés** : exécutés **immédiatement après la fin constatée d'un cycle** du superviseur |

### 4.2 Sur quoi la marge de synchronisation est fondée

**Uniquement sur des données admissibles**, et l'une d'elles est une **règle
déclarée**, non une mesure :

| Donnée | Registre | Ce qu'elle fournit |
|---|---|---|
| **cadence déclarée** du déclencheur — **3 min après inactivité** | **configuration déclarée**, `A-O4` homologué | après la fin constatée d'un cycle, **≥ 180 s** s'écoulent avant le démarrage du suivant |
| **budget déclaré de la sonde — 5 s** | **configuration déclarée**, `A-O2` homologué | une sonde qui rencontrerait le démon indisponible **échoue en 5 s au plus** |

> **Correction de fond de la V1.** Elle fondait la marge sur l'**enveloppe
> d'invocation** relevée par `W4-P1`, en la présentant comme *« l'enveloppe de
> sonde […] maximum observé 4,682 s »*. **C'était traiter cette enveloppe en
> borne de sonde** — ce que son homologation interdit expressément : elle **ne
> vaut pas `M6`**, **n'est pas une borne de sonde**, et **rien ne s'en déduit**.
> **Cette fondation est retirée.**

> **Ce que la marge de 180 s borne, et ce qu'elle ne borne pas.** Elle borne le
> **délai avant la sonde suivante**. Elle **ne borne pas la durée d'un
> redémarrage**, qui n'est établie nulle part et que ce lot **ne mesurera pas
> pour se préparer**. C'est `P2A-4` — unité active dans les **10 secondes**,
> compteur de relances stable — qui porte ce risque, et non la marge.

## 5. Élément 2 — Objectif

> **Établir des faits d'observabilité et d'appariement. Rien d'autre.**
> Ce lot **ne produit pas `M6`**, **ne qualifie aucune borne**, **ne fixe aucun
> seuil**, **ne produit aucun critère** et **ne rouvre pas `C1`**.

> **Désignations propres à `W4-P2`.** Elles sont préfixées `P2-` **parce que
> `B-O1` et `B-O2` sont déjà pris** : ce sont les objectifs de `W4-P1`, homologués
> et opposables. La V1 les réemployait, ce qui aurait rendu tout rapport
> ambigu — et aurait invité à confondre l'enveloppe d'invocation de `W4-P1` avec
> la durée de session visée ici.

| Réf | Question | Objectif | Verdicts admissibles |
|---|---|---|---|
| **`P2-O1`** | **A** | les **clôtures deviennent-elles effectivement observables** dans le puits persistant ? | `CLÔTURES OBSERVABLES` · `NON OBSERVABLES` · `INDÉTERMINÉ` |
| **`P2-O2`** | **B** | ouverture et clôture sont-elles **appariables sans ambiguïté** ? | `APPARIEMENT SANS AMBIGUÏTÉ` · `APPARIEMENT AMBIGU` · `INDÉTERMINÉ` — avec, dans tous les cas, **le critère d'appariement effectivement employé** et **le taux de séquences non appariables** |
| **`P2-O3`** | **C** | **quelle grandeur** cet appariement mesure-t-il exactement ? | **énoncé typé** de la grandeur, avec ce qu'elle **contient** et ce qu'elle **exclut** · `NON DÉTERMINABLE` |
| **`P2-O4`** | **D** | cette grandeur **apporte-t-elle** quelque chose à `U-2`, à `U-7`, ou seulement une **enveloppe différente** ? | `APPORT À U-2` · `APPORT À U-7` · **`ENVELOPPE DIFFÉRENTE UNIQUEMENT`** · `INDÉTERMINÉ` — **motivé**, jamais présumé |
| **`P2-O5`** | **E** | **quelles limites subsistent** après l'expérience ? | **énumération**, dont au minimum la **résolution** du puits et la portée des faits `F-9` à `F-11` |

> **Trois limites connues d'avance, à porter au rapport quoi qu'il advienne.**
>
> 1. **La résolution du puits demeure à la seconde** — le cadrage §B.3 (f)
>    l'établit pour les deux puits. Une durée de session s'en déduira **à cette
>    granularité**, et le §8.5 de `w4f1` interdit d'en tirer une borne.
> 2. **L'observation déforme ce qu'elle mesure** — §E.3 du cadrage : chaque ligne
>    coûte un appel d'écriture, et l'intercalation est réelle **à la réception**.
>    **La magnitude n'est établie nulle part**, et ce lot ne la fabriquera pas.
> 3. **Une durée de session n'est pas `M6`** : la population n'est pas isolée, et
>    `F-9`/`F-10` retirent tout moyen d'attribution par le puits.

### 5.1 Le §E.3 est un RISQUE DE SÛRETÉ, et pas seulement une limite

La V1 le rangeait parmi les caveats d'observation. **C'est insuffisant, et le
cadrage le dit lui-même** : *« C'est le risque le moins visible et, à mon sens,
le plus sérieux. »*

**La chaîne de conséquence, énoncée en clair :**

| | |
|---|---|
| **fait de code** | `logIT()` fait un `fprintf` **puis un `fflush` à chaque ligne**, sans tamponnage applicatif : **un appel système d'écriture par ligne** |
| **fait de code** | l'intercalation est **réelle à la réception** — horodatage pris avant, ancre déplacée après |
| **conséquence** | sous verbosité élevée, **les sessions s'allongent**. De combien : **non établi**, ni ici ni dans le cadrage |
| **conséquence de sûreté** | une sonde du superviseur est **budgétée à 5 s déclarés**. Un allongement la **rapproche de son budget** — et `F-12` établit ce qui suit un échec : **redémarrage du pont**, puis, si la seconde sonde échoue aussi, **redémarrage de la machine** |

> **Ce n'est donc pas une dégradation de la qualité de mesure : c'est un chemin
> vers l'incident de production**, et il **MUST** être gardé comme tel. Deux
> `ABORT` opposables le portent, et ils ont **deux rôles distincts** :
> **`P2A-11`** garde l'**allongement**, **`P2A-12`** détecte le **chemin
> d'échec** — et **lui seul** alimente `D-2` et `P2A-5` (§8.1, §8.3.1).

> **Ce que ce lot NE fait PAS de ce risque.** Il n'en tire **aucune qualification
> de `C1`**, **aucune borne déterministe** — il n'en existe pas —, **aucun
> seuil de critère**. Les garde-fous du §8.1 sont des **seuils internes
> d'arrêt**, et le §8.4 les distingue expressément d'un résultat.

## 6. Élément 3 — Actes permis, **liste close**

> **Liste close.** Tout acte qui n'y figure pas est **interdit**. Un doute sur
> l'appartenance vaut **interdiction** et déclenche **`P2A-1`**.

### 6.1 Phase 0 — préflight : lecture seule, et consignation hors dépôt

| # | Acte |
|---|---|
| **P1** | relever les **empreintes** — taille, date, condensat — de `<config-démon>` et du fichier d'unité de `<unité-démon>` |
| **P2** | relever, **pour `<unité-démon>`** : l'**invocation effective du processus**, son **identifiant de processus**, son **compteur de relances**, son **identifiant d'invocation**, son **instant de démarrage**, son **état** et son **sous-état** |
| **P2 bis** | relever, **pour `<unité-pont>` et pour `<unité-superviseur>`**, les **références de comparaison** : **compteur de relances**, **identifiant d'invocation**, **instant de démarrage**, **état** et **sous-état** |
| **P3** | relever la **taille** de `<journal-démon>`, le **nombre de lignes** qu'il porte, et l'**espace libre** de sa partition |
| **P4** | lire, **rétrospectivement**, le journal système de `<unité-superviseur>` sur une fenêtre courte, pour **situer le cycle courant** |
| **P5** | **établir la PRÉCONDITION D'OBSERVABILITÉ**, en lecture seule et **avant toute mutation** — voir §6.1.1 |
| **P6** | **consigner le verdict de `P5` et ses DEUX preuves** : le verdict lui-même · la **relation d'ordre et de dépendance configurée** telle que relevée, **et le moyen de preuve** par lequel elle l'a été · l'**identification précise du redémarrage historique** employé — instant et identifiant d'invocation du démon · la **fenêtre de journal** effectivement lue, bornes comprises · pour chacun des **quatre événements**, sa **présence et son rang** · et le **constat de concordance** entre les deux preuves |

> **Les SEPT lignes ci-dessus appartiennent toutes à la liste close.** La V11
> en annonçait *« cinq »* alors qu'il y en avait **six** — `P5` ayant été ajouté
> sans que le décompte suive —, et `P6` en fait **sept**. La V4
> insérait cette note **entre deux lignes du tableau**, ce qui rendait ambiguë
> l'appartenance de `P3` et `P4`. Elle est désormais **hors du tableau**.

> **`P2 bis` rend `D-1` et `P2A-6` opérants dès le premier redémarrage.** L'un et
> l'autre comparent un identifiant d'invocation ou un instant de démarrage **à un
> état antérieur**. Sans référence capturée **avant** la mutation, ils n'auraient
> rien à comparer, et seraient restés **inopérants** pendant toute la phase 1.
>
> **`S8` demeure la mesure finale comparative** : c'est le couple `P2 bis` → `S8`
> qui porte `R5.d`, et `P2 bis` qui porte `D-1` et `P2A-6` pendant la fenêtre.

> **`P2` couvre aussi `<unité-démon>`.** La V4 l'avait réduit à l'invocation, à
> l'identifiant de processus et au compteur de relances, perdant l'état que la V3
> relevait. Sans lui, `R3` et `R5.a` compareraient à une référence incomplète.

#### 6.1.1 `P5` — la précondition d'observabilité, et son `STOP` propre

**Le défaut que cela corrige.** La V10 exigeait, par `(a)` et `(c)` du §8.1.2.1,
que le journal porte certains événements **avec certains identifiants**. Elle
**portait en réserve** que rien ne l'établissait — *« `W4-P1` l'a établi pour
l'unité du superviseur, jamais pour ces deux-là »*. **Une exigence dont la
faisabilité est inconnue n'est pas une exigence : c'est un pari.**

**`P5` établit deux choses, et rien d'autre :**

| # | Ce que `P5` établit | Comment |
|---|---|---|
| **1** | la **relation d'ordre et de dépendance réellement configurée** entre `<unité-pont>` et `<unité-démon>` — ce que l'une requiert de l'autre, et dans quel ordre elles démarrent et s'arrêtent | consultation des **propriétés de dépendance et d'ordre** des deux unités |
| **2** | que les **quatre événements de cycle de vie** énumérés en `(a)` figurent au journal, **pour le pont ET pour le démon**, **avec les identifiants exigés par `(c)`**, **ET DANS L'ORDRE EXACT que `(a)` exige** | lecture **rétrospective** des journaux des deux unités sur une **fenêtre passée contenant au moins un redémarrage du démon** |

> **`P5` n'exige aucune mutation.** Le démon **a déjà été redémarré** par le passé :
> `P5` lit cette histoire, il ne la provoque pas. **Si la rétention du journal ne
> couvre aucun redémarrage passé, la précondition n'est pas établie** — et c'est
> un résultat, non un motif d'insister.

**Le verdict exige les DEUX preuves, et leur CONCORDANCE.**

> **Défaut que la V12 laissait.** Ses deux éléments étaient énumérés côte à côte,
> mais **seul le second entrait dans le critère** : une installation dont la
> relation configurée serait ignorée, mais dont un redémarrage passé aurait par
> hasard produit le bon ordre, aurait été déclarée `ÉTABLIE`. **Une observation
> historique seule ne suffit jamais** : elle atteste **ce qui s'est produit une
> fois**, non **ce que la configuration ordonne**.

| | Preuve | Ce qu'elle apporte |
|---|---|---|
| **structurelle** | la **relation d'ordre et de dépendance configurée** — élément 1 | **ce que l'installation ORDONNE**, donc ce qu'elle reproduira |
| **historique** | l'**ordre effectivement observé** sur un redémarrage passé — élément 2 | **ce qui s'est produit**, une fois au moins |

> **`ÉTABLIE` exige que les deux CONCORDENT** : l'ordre observé doit être
> **celui que la relation configurée ordonne**. Une discordance — quelle qu'en
> soit la direction — vaut **`NON ÉTABLIE`**, et le §6.1.1 ne cherche pas à
> l'expliquer.

**Le critère porte sur l'ORDRE, et pas seulement sur la présence.**

> **Défaut que cela corrige.** La V11 exigeait que les quatre événements
> *« figurent effectivement »*. **Une installation qui les émettrait tous, mais
> dans un autre ordre**, aurait été déclarée `ÉTABLIE` — puis aurait échoué à
> `(a)` **après la mutation**, c'est-à-dire au moment le plus coûteux.

| Verdict | Critère | Conséquence |
|---|---|---|
| **`PRÉCONDITION ÉTABLIE`** | **(i)** la **relation configurée** est relevée et **ordonne** l'encadrement exigé par `(a)` ; **(ii)** sur au moins un redémarrage historique du démon, les **quatre** événements figurent **et** apparaissent dans l'ordre **(1) arrêt du pont · (2) arrêt du démon · (3) démarrage du démon · (4) démarrage du pont**, **avec** l'identifiant d'invocation du démon exigé par `(c)` ; **(iii)** les deux **CONCORDENT** | la phase 1 **peut** être engagée |
| **`PRÉCONDITION NON ÉTABLIE`** | la **relation configurée** n'est pas relevable ou **n'ordonne pas** cet encadrement · un événement **manque** · l'**ordre n'est pas celui-là** · l'**identifiant** est absent · **aucun redémarrage historique** n'est couvert par la rétention · ou **les deux preuves discordent** | **`STOP AVANT MUTATION`** — §8.2.1 |

> **Il n'y a pas de troisième verdict**, et **l'ordre non établi vaut NON
> ÉTABLIE** : un ordre différent ne rendrait pas `(a)` *un peu moins* vérifiable,
> il le rendrait **faux**.

> **`STOP AVANT MUTATION` n'est PAS un `ABORT` terrain**, et la distinction
> importe : **rien n'a été muté**, il n'y a **rien à restaurer**, et la phase 1
> **n'est jamais engagée**. Le lot s'arrête **avant** d'avoir touché à quoi que ce
> soit. Voir §8.2.1 pour ce qui est dû dans ce cas.

### 6.2 Phase 1 — armement

| # | Acte |
|---|---|
| **M1** | créer `<dropin-démon>` et **un seul** fichier de surcharge, portant **exclusivement** la réinitialisation de la ligne d'exécution et sa reprise **à l'identique augmentée de `-g`** |
| **M2** | **valider l'unité résultante** par `systemd-analyze verify` — **sans redémarrage** |
| **M3** | **recharger la configuration systemd** — cet acte **ne redémarre pas** le service |
| **M4** | **afficher l'invocation résultante** et la **comparer caractère à caractère** à l'attendu — **avant** tout redémarrage |
| **M5** | **attendre la fin constatée d'un cycle** du superviseur, puis **redémarrer `<unité-démon>`**, et **relever l'INSTANT EXACT de la commande** |
| **M5 bis** | **qualifier la propagation attendue** de `M5`, en **lecture seule**, selon le §8.1.2 : lire **rétrospectivement** le **journal système de `<unité-pont>`**, celui de `<unité-démon>` et celui de `<unité-superviseur>` sur la fenêtre de qualification, et relever pour le pont son **état, sous-état, identifiant d'invocation, instant de démarrage et compteur de relances** |
| **M6** | **vérifier dans les 10 secondes** : unité active, identifiant de processus **nouveau**, compteur de relances **stable**, et **relever l'IDENTIFIANT D'INVOCATION de `<unité-démon>`** — c'est le terme que `(c)` compare |

### 6.3 Phase 2 — observation

| # | Acte |
|---|---|
| **O1** | relever la **position de fin** de `<journal-démon>` avant la fenêtre, puis lire **exclusivement les lignes produites après cette position** |
| **O2** | surveiller, **par lecture seule**, selon les canaux et la fréquence du §8.3 : l'**état, le sous-état, l'instant de démarrage, l'identifiant d'invocation et le compteur de relances** des trois unités du périmètre · la croissance de `<journal-démon>` · l'espace libre · et, **quand elles existent**, les lignes propres de `<unité-superviseur>`. **Voir l'extension du §6.3.1** |
| **O3** | **figer** les relevés dans des fichiers **hors dépôt** |
| **O4** | **en cas d'`ABORT`, dans QUELLE QUE SOIT la phase** — 0, 1, 2 ou 3 —, **consigner l'état exact du relevé partiel** : ce qui a été figé, ce qui ne l'a pas été, et l'**instant de l'arrêt** — porte `R7`. **Hors ce cas, `O4` n'est pas permis** |

#### 6.3.1 Extension de `O2` aux phases 1 et 3 — dans deux cas nommés

**`O2` est un acte de la phase 2.** Le §8.1.1 exige pourtant que la surveillance
**se poursuive pendant l'attente d'un retour synchronisé `S1`**, laquelle
appartient à la **phase 3**. Sans cette extension, la **préemption** que le
§8.1.1 prescrit serait **prescrite sans acte permettant de l'observer**.

| | |
|---|---|
| **Ce qui est étendu** | `O2`, **et lui seul**, **inchangé dans son contenu et sa fréquence** |
| **Quand** | **deux cas, et deux seulement** : **(i)** pendant toute **attente d'un retour synchronisé `S1`**, en phase 3 ; **(ii)** pendant toute **qualification différée** du §8.1.3, en phase 1 comme en phase 3 |
| **Pour quoi faire** | **uniquement** maintenir la surveillance et la **préemption** définies au §8.1.1 et au §8.1.3 |
| **Jusqu'à quand** | jusqu'à l'un des **termes** nommés, et à aucun autre : pour **(i)**, l'**exécution effective du retour** — `S1` engagé — ou la **préemption par `P2A-12`** ; pour **(ii)**, la **qualification acquise**, son **échec**, ou la **préemption par `P2A-12`** |

> **Correction de la V9.** Son titre disait *« à la phase 3 — et à elle seule »*
> alors que son contenu étendait déjà `O2` à la **qualification différée**, qui
> survient **aussi en phase 1** — autour de `M5`. Le titre et les clauses de
> fermeture disent désormais **ce que le contenu fait**.

> **Aucune autre extension de périmètre.** `O2` demeure **inchangé dans son
> contenu, ses canaux et sa fréquence**. Il **ne devient pas** un acte de la
> phase 0. Il **n'est permis hors de la phase 2 que dans les deux cas nommés
> ci-dessus** — attente d'un `S1` synchronisé, qualification différée — et
> **jamais autrement**.
>
> **`O2` appartient à la liste close** dans ces deux cas comme dans la phase 2 :
> son appartenance n'est **pas** ambiguë, et aucune lecture nouvelle n'est
> introduite par l'extension.

### 6.4 Phase 3 — retour et constat de sortie

| # | Acte |
|---|---|
| **S1** | **attendre la fin constatée d'un cycle** du superviseur, puis **supprimer le fichier de surcharge et le répertoire `<dropin-démon>`** |
| **S2** | **recharger la configuration systemd**, puis **afficher l'invocation résultante** et vérifier qu'elle est **identique à celle du préflight** |
| **S3** | **redémarrer `<unité-démon>`**, **relever l'INSTANT EXACT de la commande**, puis **vérifier dans les 10 secondes** et **relever l'IDENTIFIANT D'INVOCATION** du démon — mêmes relevés qu'à `M5` et `M6`, pour que `(c)` soit mesurable des deux côtés |
| **S3 bis** | **qualifier la propagation attendue** de `S3`, en **lecture seule**, par les **mêmes lectures que `M5 bis`** et sur la même fenêtre |
| **S4** | relever l'**invocation effective** du processus, son identifiant, son compteur de relances, et les empreintes de `<config-démon>` et du fichier d'unité |
| **S5** | lire les lignes de `<journal-démon>` **produites après** le redémarrage de retour, et y vérifier l'**absence des types `LOG_INFO`** visés — puis la **reprise des lignes d'ouverture**, qui atteste que le démon **sert ses clients** sans que le lot ouvre lui-même de session |
| **S6** | établir que le démon est un **processus unique** et le **détenteur du périphérique**, par les **deux méthodes indépendantes de l'Acte A** : `fuser -v` sur le périphérique, **et** balayage des descripteurs sous `/proc` |
| **S7** | **constater l'absence** de `<dropin-démon>` et de son fichier — porte `R1` |
| **S8** | relever, pour `<unité-pont>` et `<unité-superviseur>` : **état, sous-état, compteur de relances, identifiant d'invocation et instant de démarrage** ; et relever la **taille finale** de `<journal-démon>` ainsi que l'**espace libre** — porte `R5.d` et `R6` |
| **S9** | lire **rétrospectivement et EN ENTIER** le **journal système de `<unité-pont>`** sur **toute la durée du lot** — du préflight à la sortie —, et y **DÉNOMBRER** les identifiants d'invocation **nouveaux par rapport au baseline de `P2 bis`** — porte `R5.e`. **`S9` DÉNOMBRE ; il ne QUALIFIE PAS** |

> **Deux offices distincts, que la V10 confondait.**
>
> | | **`M5 bis` / `S3 bis`** | **`S9`** |
> |---|---|---|
> | Office | **QUALIFIER localement** un redémarrage, au **moment utile** | **DÉNOMBRER globalement**, à la sortie |
> | Fenêtre | les `60 s` de leur qualification | **toute la durée du lot** |
> | Peut attribuer ? | **oui** — c'est leur objet | **NON, jamais** |
>
> **`S9` n'attribue rien rétrospectivement.** Un redémarrage qu'il dénombre et qui
> **n'a pas été qualifié au moment utile** est **NON ATTRIBUÉ** — et le demeure.
> **Aucune attribution après coup n'est possible** : les éléments `(a)`, `(b)` et
> `(c)` portent sur une fenêtre qui est passée, et le lot **ne reconstitue pas**.

> **Conséquence, et elle est dure : tout redémarrage dénombré non qualifié
> localement fait ÉCHOUER `R5.e`.** C'est voulu — la preuve de sortie ne se
> satisfait pas d'un compte : elle exige que **chaque** redémarrage soit
> **attribué**.

> **Rang de `S9` dans le temps.** Il est conduit **après la fin de la
> qualification de `S3`** — issue prononcée, quelle qu'elle soit — **et après le
> retour de `<unité-pont>` à `active/running`**. Avant, son dénombrement serait
> incomplet ; il compterait un redémarrage en cours comme absent.

> **`S9` est dû dans TOUS les cas de sortie**, y compris après un `ABORT` et
> **y compris après une préemption**. L'abandon d'une qualification
> **prospective** — §8.1.3 — **n'interdit pas** la collecte **rétrospective**
> nécessaire aux preuves de sortie : ce sont deux choses différentes, et la V9 les
> confondait au détriment de `R5.e`.

> **Pourquoi `S9` NE REMPLACE PAS `M5 bis` / `S3 bis`.** Ces deux-là ne couvrent
> que **leurs fenêtres de `60 s`** — un redémarrage survenu **entre** elles leur
> échapperait —, mais **eux seuls qualifient**. `S9` couvre la durée du lot, **et
> ne qualifie rien**. **Les deux sont nécessaires, et aucun ne supplée l'autre.**

**Tout le reste est interdit** — et nommément : aucune édition de `<config-démon>`
ni du fichier d'unité · aucune session cliente ouverte par le lot · aucune
commande envoyée au démon · aucun `reload` applicatif, aucun signal · aucune
action sur `<unité-pont>`, `<timer-guard>` ni `<unité-superviseur>` · aucune
suppression, troncature ni rotation de `<journal-démon>` · aucune publication
externe d'un élément du lot.

## 7. Élément 5 — Restauration définie et vérifiable

**Le lot mute. La restauration est donc réelle, et elle doit être ÉTABLIE, pas
supposée** — `w4-cadrage-activation-debug.md` §F.2.

| # | Preuve exigée |
|---|---|
| **R1** | **`<dropin-démon>` n'existe plus**, ni son fichier |
| **R2** | `<config-démon>` et le fichier d'unité : **taille, date et condensat identiques** au préflight — **ils n'auront jamais été touchés** |
| **R3** | l'**invocation effective du processus** est identique à celle du préflight, **sans `-g`** — le contrôle porte sur le **processus**, non sur le fichier |
| **R4** | sur les lignes **produites après** le retour : **absence des types `LOG_INFO`** visés. Seul contrôle portant sur le **comportement observable** |
| **R5** | **quatrième constat du §F.2, restauré intégralement** — le démon est revenu à l'état d'**un processus unique**, **détenteur du périphérique**, **servant ses clients** : |
| `R5.a` | **processus unique** — une seule instance, sans enfant |
| `R5.b` | **détenteur du périphérique** — établi par **deux méthodes indépendantes**, celles de l'Acte A : `fuser -v` et balayage des descripteurs sous `/proc` |
| `R5.c` | **sert ses clients** — les lignes d'ouverture reparaissent dans `<journal-démon>` après le retour, **sans que le lot ouvre de session** |
| `R5.d` | `<unité-pont>` et `<unité-superviseur>` sont **nominaux**, compteurs de relances **inchangés** |
| `R5.e` | **restauration du pont, prouvée et COMPTÉE AU JOURNAL SUR TOUTE LA DURÉE DU LOT** : le nombre d'**identifiants d'invocation de `<unité-pont>` NOUVEAUX relativement au baseline de `P2 bis`** — l'unité de compte du §8.1.2.2 — **égale exactement le NOMBRE DE PROPAGATIONS QUALIFIÉES** au sens du §8.1.2, **et non le nombre de commandes de `M5` et `S3`** ; **chacune est attribuée** à sa commande au sens du §8.1.2.1 ; et le pont est **`active/running`** en sortie. **Le cas « zéro propagation » du §8.1.3 est SATISFAISANT** : zéro identifiant nouveau pour zéro propagation qualifiée, l'égalité tient. **Portée par QUATRE actes, dont aucun ne supplée les autres** : `P2 bis` — le baseline — · **`M5 bis`** et **`S3 bis`** — l'**attribution**, au moment utile — · **`S9`** — le **dénombrement** rétrospectif complet — · `S8` — l'état final. **`R5.e` ÉCHOUE si `S9` dénombre un redémarrage que `M5 bis` ou `S3 bis` n'a pas qualifié** — sous réserve du cas de **préemption**, §7.1 : le compte seul ne prouve rien, et **rien ne s'attribue après coup**. **Les verdicts d'échec, leurs trois composantes et la conduite qui s'ensuit sont au §7.1, et là seulement.** **`O2` n'y est pas invoqué**, son échantillonnage ne comptant rien |
| **R6** | le **volume ajouté** à `<journal-démon>` est relevé et consigné |
| **R7** | en cas d'`ABORT` : le **relevé partiel** est conservé **tel quel**, avec l'instant de l'arrêt, et **MUST NOT** être complété, reconstitué ni présenté comme complet |

> **Ce que la restauration ne rend pas.** L'espace consommé dans
> `<journal-démon>` **reste consommé** : `F-6` établit qu'aucune rotation ne le
> reprendra. Son retrait serait un **troisième acte**, **hors de ce lot**, et
> `R6` se borne à le **chiffrer**.

> **Une divergence sur `R1`, `R2`, `R3` ou `R4` est un `ABORT`**, et **MUST** être
> consignée telle quelle, sans correction ni réinterprétation.

### 7.1 Conduite si `R5.e` échoue en sortie

**Le défaut que cela corrige.** La V11 posait que `R5.e` **échoue** si un
redémarrage dénombré n'a pas été qualifié — **sans dire ce qui se passe alors**.
C'était un **trou de procédure** : le lot arrivait en sortie avec une preuve
manquante et aucune conduite écrite.

> **`R5.e` s'évalue APRÈS `S9`, quel que soit le chemin de sortie** — déroulement
> complet, `ABORT` ordinaire, ou séquence spéciale de `P2A-2` / `P2A-3`, où `S9`
> occupe le rang 5. Ce n'est pas un
> déclencheur d'`ABORT` : à ce stade, le retour est **déjà conduit**, la
> restauration **déjà établie** par `R1` à `R5.d`. **`R5.e` est un CONSTAT DE
> SORTIE**, et son échec se **rapporte**, il ne se **répare** pas.

**`R5.e` a TROIS composantes, et chacune reçoit ses verdicts.** La V12 n'en
couvrait qu'une.

| # | Composante | Portée par |
|---|---|---|
| **1** | le **compte** des identifiants d'invocation nouveaux du pont | `S9` |
| **2** | l'**attribution** de chacun | `M5 bis` / `S3 bis` |
| **3** | le pont **`active/running` en sortie** | `S8` |

> **Le COMPTE ATTENDU, corrigé.** Ce n'est **pas** le nombre de commandes de
> redémarrage du démon : c'est le **nombre de propagations QUALIFIÉES**. Le
> §8.1.3 admet en effet le cas **« zéro redémarrage du pont »** comme **nominal** ;
> un redémarrage du démon peut donc légitimement n'en produire **aucune**.
> **Compter les commandes ferait échouer `R5.e` sur un déroulement parfaitement
> normal** — c'est ce que la V12 prescrivait.

**Les verdicts, composante par composante :**

| Verdict | Composante | Quand | Ce qui est dû |
|---|---|---|---|
| **`R5.e SATISFAITE`** | les trois | le compte **égale** le nombre de propagations qualifiées · **chacune** est attribuée · le pont est **`active/running`** | rien de plus |
| **`R5.e ÉCHOUE — COMPTE SUPÉRIEUR`** | 1 | `S9` dénombre **plus** d'identifiants nouveaux qu'il n'y a de propagations qualifiées | **nommer chaque identifiant excédentaire** — instant compris — **puis le TRIER** selon le §7.1.1, qui décide lequel des deux verdicts de composante 2 lui revient |
| **`R5.e ÉCHOUE — COMPTE INFÉRIEUR`** | 1 | `S9` en dénombre **moins** : une propagation **qualifiée localement** n'apparaît **pas** au dénombrement global | **rapporter la contradiction telle quelle** — quelle propagation, quel acte l'a qualifiée, et pourquoi elle est absente du dénombrement. **Le lot N'ARBITRE PAS** lequel des deux relevés a raison |
| **`R5.e ÉCHOUE — REDÉMARRAGE NON ATTRIBUÉ`** | 2 | un identifiant dénombré n'a été qualifié **ni par `M5 bis` ni par `S3 bis`**, **et aucune préemption ne l'explique** — §7.1.1 | **rapporter explicitement** le redémarrage : **identifiant d'invocation**, **instant**, et le fait qu'**aucune attribution n'existe** pour lui |
| **`R5.e ÉCHOUE — ATTRIBUTION ABANDONNÉE PAR PRÉEMPTION`** | 2 | la qualification qui **aurait couvert cet identifiant** a été **abandonnée** en cours, par la préemption du §8.1.3 | **rapporter l'abandon**, l'instant de la préemption, et **le redémarrage demeuré sans attribution de ce fait** |
| **`R5.e ÉCHOUE — PONT NON NOMINAL EN SORTIE`** | 3 | `S8` ne rend **pas** `<unité-pont>` en `active/running` | **rapporter l'état effectif**, son sous-état et son instant de relevé. **Ce verdict se cumule** avec ceux des composantes 1 et 2, il ne les remplace pas |

> **Le cas « zéro propagation » est SATISFAISANT sur la composante 1** : zéro
> identifiant nouveau, zéro propagation qualifiée, l'égalité tient. Il n'appelle
> **aucun** des verdicts d'échec.

#### 7.1.1 Trier les identifiants excédentaires — préemption ou absence d'attribution

**Le défaut que cela corrige.** La V13 faisait suivre `COMPTE SUPÉRIEUR` du
verdict **`REDÉMARRAGE NON ATTRIBUÉ`**, **automatiquement**. Or un identifiant
dont la qualification a été **légitimement abandonnée par préemption** apparaît
lui aussi en excédent — il n'est pas une propagation *qualifiée*. **Il aurait été
requalifié en « non attribué », c'est-à-dire traité comme une anomalie alors
qu'il résulte d'une règle de sûreté que le lot a correctement appliquée.**

**Chaque identifiant excédentaire est trié, un par un :**

| Cas | Verdict qui lui revient |
|---|---|
| une **qualification le couvrait** et a été **abandonnée par la préemption** du §8.1.3 — l'instant de la préemption et celui de l'identifiant **concordent** | **`ATTRIBUTION ABANDONNÉE PAR PRÉEMPTION`** — et **jamais** `REDÉMARRAGE NON ATTRIBUÉ` |
| **aucune préemption ne l'explique** : il survient hors de toute fenêtre de qualification, ou aucune qualification ne le couvrait | **`REDÉMARRAGE NON ATTRIBUÉ`** |

> **Le tri se fait identifiant par identifiant, jamais en bloc.** Un même lot peut
> porter un excédent **des deux natures** : les deux verdicts sont alors
> prononcés, chacun **nommant les identifiants qui lui reviennent**.

> **`REDÉMARRAGE NON ATTRIBUÉ` est réservé** aux redémarrages **réellement sans
> attribution hors préemption**. L'employer là où une préemption explique
> l'absence reviendrait à **imputer au lot une anomalie dont sa propre règle de
> sûreté est la cause**.

> **Les verdicts se CUMULENT.** `R5.e` peut échouer sur deux composantes à la
> fois — un compte supérieur **et** un pont non nominal, par exemple. **Chacun se
> prononce**, et aucun n'absorbe l'autre. **Cela vaut aussi entre les deux
> verdicts de composante 2**, lorsque le tri du §7.1.1 en désigne des deux
> natures.

> **Le verdict de préemption est LÉGITIME, et ce n'est pas une faute.** Le §8.1.3
> **prescrit** l'abandon de la qualification en cas de préemption — *« jamais
> reprise ni menée à son terme après coup »*. Que `R5.e` en pâtisse est la
> **conséquence assumée** de cette règle de sûreté, non un manquement du lot.
> **Il reçoit un verdict propre pour que cela se lise, plutôt que de se confondre
> avec une négligence.**

**Dans TOUS les cas d'échec, et sans exception :**

| | |
|---|---|
| **aucun acte terrain nouveau** | le lot est en sortie ; **rien ne se rejoue** |
| **aucune nouvelle tentative** | ni de qualification, ni de dénombrement, ni de redémarrage |
| **aucune attribution après coup** | §8.1.2 — les éléments `(a)`, `(b)` et `(c)` portent sur une fenêtre **passée** |

> **Ce constat final se distingue d'un `ABORT` qui aurait dû se déclencher plus
> tôt.** Si le redémarrage non attribué **était détectable au moment où il est
> survenu** — par `D-1`, par `O2`, par `P2A-6` —, alors **un `ABORT` était dû
> alors**, et son absence est **un manquement à consigner comme tel**, en plus de
> l'échec de `R5.e`.
>
> **S'il n'était PAS détectable à ce moment** — hors de toute fenêtre de
> qualification, entre deux relevés —, alors l'échec de `R5.e` **est précisément
> ce qui le révèle**, et le lot a fonctionné comme il devait. **Le rapport MUST
> dire lequel des deux cas s'applique**, et ne pas laisser la question ouverte.

## 8. Élément 4 — `ABORT` et `STOP`

### 8.1 `ABORT` — arrêt immédiat, suivi du retour de la phase 3

| Réf | Déclencheur |
|---|---|
| **`P2A-1`** | un acte hors de la liste close est envisagé, ou son appartenance est douteuse |
| **`P2A-2`** | la validation `M2` signale quoi que ce soit — **ne pas redémarrer**, retirer la surcharge |
| **`P2A-3`** | l'invocation résultante affichée en `M4` **diffère** de l'attendu, en quoi que ce soit — **ne pas redémarrer**, retirer la surcharge |
| **`P2A-4`** | après un redémarrage, l'unité n'est pas active dans les **10 secondes**, ou son compteur de relances **s'incrémente** — signature d'une boucle |
| **`P2A-5`** | l'un des **trois détecteurs du §8.3** signale que le chemin d'échec de `F-12` est **engagé ou suspecté**. **Retour selon le §8.3, puis `STOP` pour arbitrage** : le pont aurait été redémarré **par le superviseur** — ce que le lot s'interdit de provoquer, et qui demeure exclu **même depuis que la propagation attendue du §8.1.2 est admise**. **L'admission ne couvre que la propagation, jamais l'escalade** |
| **`P2A-6`** | `<unité-pont>` redémarre **autrement que par la propagation attendue du §8.1.2** — qualifiée selon le §8.1.3 — ou son compteur de relances bouge. **Motif au §3.0** |
| **`P2A-7`** | l'espace libre de la partition passe **sous 10 %**, ou `<journal-démon>` croît de plus de **100 Mio** pendant la fenêtre. **Seuils internes, soumis à l'autorisation** — §8.4, §9 |
| **`P2A-8`** | redémarrage machine |
| **`P2A-9`** | la fenêtre du §4.1 serait dépassée |
| **`P2A-10`** | **doute de l'exploitant, sans justification à fournir** |
| **`P2A-11`** — *allongement* | la durée d'une invocation **quelconque** de `<unité-superviseur>` — terminée ou en cours — atteint **`5,000 s`**, le **budget déclaré**. `ABORT`, dont **la conduite dépend de l'état de l'invocation** : **terminée** → retour **synchronisé** ; **EN COURS** → retour **NON synchronisé**, §8.1.1. **Valeur DÉRIVÉE**, jamais un choix. **N'alimente NI `D-2` NI `P2A-5`** |
| **`P2A-12`** — *chemin d'échec* | la durée d'une invocation **quelconque** de `<unité-superviseur>` — terminée ou en cours — atteint **`10 s`**. `ABORT` **D'URGENCE** : alimente `D-2`, donc `P2A-5`, donc la conduite du §8.3.4. **Valeur CHOISIE**, soumise au §9 |

> **Correction de fond de la V4, et elle était grave.** `P2A-11` y valait
> **`4,000 s`** — **SOUS le régime observé**. `W4-P1` a relevé des enveloppes
> d'invocation **nominales** allant jusqu'à **4,682 s** : le seuil aurait été
> franchi par des cycles **parfaitement normaux**. Et comme `P2A-11` alimentait
> `D-2`, qui alimente `P2A-5`, **un cycle nominal aurait été interprété comme le
> chemin d'échec de `F-12`**, déclenchant la conduite d'urgence et un `STOP`.
>
> **C'est exactement la régression que `W4-P1` V3 avait corrigée sous `P2A-3c`** :
> prendre le comportement nominal pour une défaillance.

> **Ce que la V5 fait, et ce qu'elle se refuse à faire.**
>
> | | |
> |---|---|
> | **elle ne dérive aucune borne de `W4-P1`** | la valeur `4,682 s` n'est employée **ni comme borne, ni comme seuil, ni comme base de calcul**. Elle sert **uniquement** à constater que `4,000 s` était sous le régime observé, et à vérifier qu'un seuil choisi se situe au-dessus |
> | **elle choisit un seuil humain au-dessus du régime observé** | **`10 s`** pour `P2A-12` : plus du **double** de tout ce qui a été observé sans verbosité élevée, **au-dessus** du budget dérivé de 5 s, et **neuf fois sous** la signature déclarée du chemin d'échec, qui court à ≥ 90 s |
> | **elle assume explicitement le faux positif** | `P2A-11` à `5,000 s` ne laisse que **≈ 318 ms** au-dessus du maximum observé. **Il peut donc se déclencher sur un cycle nominal** — et c'est assumé : son effet est un `ABORT` **ordinaire**, qui met fin au lot **sans rien conclure** |
> | **elle découple** | **`P2A-11` n'alimente ni `D-2` ni `P2A-5`.** Un franchissement du budget **n'est pas** une interprétation du chemin `F-12` : seul **`P2A-12`** l'est |
>
> **Le garde-fou est donc opérant sans qu'un cycle nominal soit jamais interprété
> comme le chemin de `F-12`.**

> **Reformulation de `P2A-11`, et pourquoi.** La V2 le référait au *« maximum
> relevé par `W4-P1` »*. **Cette référence était ambiguë sur deux plans** : la
> valeur n'était pas nommée, et la population dont elle sortait est déclarée
> **non homogène** par l'homologation elle-même — 52 invocations qualifiées, 24
> non qualifiées. **Un seuil d'arrêt ne peut pas reposer là-dessus.** `P2A-11`
> repose désormais sur une **valeur dérivée du corpus** — le **budget déclaré**,
> `5,000 s` — **et sur rien d'autre**.
>
> **Aucune fraction n'intervient.** La V4 en introduisait une ; la V5 l'a retirée
> du seuil sans nettoyer cette phrase, qui la mentionnait encore. **`P2A-11` est
> dérivé de bout en bout**, et n'est soumis à l'autorisation **à aucun titre** —
> §8.4, §9 point 3 quater.

> **La population est désormais sans ambiguïté** : **toute** invocation de
> `<unité-superviseur>` observée pendant la fenêtre, **qualifiée ou non**. Ce
> choix découle de `RB-1` : conditionner le garde-fou à la présence d'une ligne
> propre l'aurait rendu **aveugle** sur les invocations qui n'en produisent pas.

#### 8.1.1 Précédence entre `P2A-11` et `P2A-12`

> **RÈGLE ABSOLUE, qui domine tout ce paragraphe.** **Le lot n'attend jamais
> volontairement à travers les 90 s du chemin de `F-12`.** Aucune conduite, aucun
> `ABORT`, aucune synchronisation ne peut avoir pour effet une attente pendant
> que cet intervalle s'écoule.

> **RÈGLE DE PRÉCÉDENCE.** **`P2A-12` prévaut TOUJOURS sur `P2A-11`** dès qu'il
> est atteint. Lorsque les deux sont satisfaits, la conduite est **celle de
> `P2A-12`**, sans exception et sans délibération.

**Le défaut que cela corrige.** `P2A-11` prescrivait un retour **synchronisé** —
donc une **attente**. Sur une invocation **encore en cours**, la durée **peut
continuer de croître** : le lot aurait attendu une frontière de cycle **alors
même que le chemin d'échec se déroulait**. La durée seule ne suffit donc pas à
choisir la conduite : **il faut savoir si l'invocation est terminée.**

**Les deux relevés, traités séparément :**

| Relevé | État de l'invocation | Conduite, et son motif |
|---|---|---|
| **`[5 s, 10 s)`** | **TERMINÉE** | la durée est **définitive et ne croîtra plus**. De plus, la signature déclarée du chemin d'échec court à **≥ 90 s** : une invocation close en deçà de 10 s **n'y est pas engagée**. → **`P2A-11` ordinaire, retour SYNCHRONISÉ permis** |
| **`[5 s, 10 s)`** | **EN COURS** | la durée **peut encore croître** vers `P2A-12`. **Aucune attente volontaire n'est permise.** → **conduite du §8.3.4**, exactement comme si `P2A-12` était atteint. **Pour le `STOP`, voir la règle ci-dessous** |
| **`≥ 10 s`** | terminée **ou** en cours | **`P2A-12` prévaut** → **conduite du §8.3.4**, `STOP` pour arbitrage dû |

> **Il n'y a donc qu'un seul chemin où une attente est permise** : une invocation
> **close** entre 5 s et 10 s. Partout ailleurs, la conduite est **non
> synchronisée**.

> **Et l'attente permise reste sous surveillance.** Pendant qu'un retour
> synchronisé est en cours d'attente, la surveillance du §8.3.2 **se poursuit à
> sa fréquence** — l'acte qui la permet en phase 3 est l'**extension du §6.3.1**.
> Si une invocation ultérieure atteint `P2A-12`, la conduite d'urgence du §8.3.4
> **préempte** le retour synchronisé en attente, sans délibération.

> **Le `STOP` dans le cas `[5 s, 10 s)` EN COURS — tranché, et écrit.** La V6
> laissait l'ambiguïté : la conduite renvoyait au §8.3.4, dont les deux branches
> déclarent le `STOP` dû, alors que le chemin d'échec n'est ici que **suspecté**.
>
> | | |
> |---|---|
> | **la conduite de retour** | **toujours immédiate et non synchronisée** — elle **ne dépend d'aucune confirmation**, et n'attend rien |
> | **le `STOP` pour arbitrage** | dû **si et seulement si** le chemin d'échec est **CONFIRMÉ** — par **`D-1`**, le pont ayant redémarré ; ou par la durée atteignant **`P2A-12`** ; ou par **`D-3`** |
> | **à défaut de confirmation** | le lot se clôt sur un **`ABORT` ordinaire**, et le rapport **MUST** consigner la **suspicion** et sa **non-confirmation** |
> | **en cas de doute** | **le doute vaut confirmation** : le `STOP` est dû. En particulier, si `D-1` **ne peut pas être évalué**, le `STOP` **est dû** |
>
> **Motif de la règle, et il n'est pas de commodité.** Le `STOP` de `P2A-5` a pour
> objet le fait que *« le pont aurait été redémarré, ce que le lot s'interdit »*.
> **Si le pont n'a pas été redémarré, ce motif est absent** — et `D-1` l'établit
> directement. **La sûreté, elle, n'est pas conditionnée** : le retour part
> immédiatement dans tous les cas.

> **Ce sont des garde-fous, pas des mesures.** L'enveloppe **n'est ni `M6` ni une
> borne** — `w4p1-homologation.md` §7 —, et la comparer à un seuil d'arrêt **ne
> la requalifie pas**. Elle **contient** la ou les sondes de l'invocation : une
> enveloppe sous le seuil **suffit** à établir qu'aucune sonde ne l'a franchi, ce
> qui fait du garde-fou un majorant **conservateur** — et **rien de plus**.

> **L'`ABORT` de `W4-P2` a quelque chose à défaire**, contrairement à celui de
> `W4-P1` : la phase 3 **MUST** être conduite intégralement, et les preuves du §7
> produites, **y compris après un `ABORT`**.
>
> **Exception, et une seule** : sous `P2A-2` et `P2A-3`, **aucun redémarrage n'a
> eu lieu**. Le retour se réduit alors à la séquence suivante, **et à elle
> seule** :
>
> | Ordre | Acte | Pourquoi |
> |---|---|---|
> | 1 | **`S1`** | supprimer le fichier et le répertoire de surcharge |
> | 2 | **`S2`** | recharger la configuration systemd et vérifier que l'invocation résultante est **identique à celle du préflight** |
> | 3 | **`S7`** | **constater l'absence** du répertoire et du fichier — la preuve `R1` est due **aussi dans ce cas** |
> | 4 | **`S4`, RESTREINT AUX EMPREINTES** | relever les empreintes de `<config-démon>` et du fichier d'unité, et les comparer au préflight — la preuve **`R2`** est due, et la V4 l'avait **omise** |
> | 5 | **`S9`** | **dénombrer** les identifiants d'invocation nouveaux du pont sur toute la durée du lot — la preuve **`R5.e`** est due, et la V10 la déclarait due **sans l'inscrire dans cette séquence** |
> | 6 | **`O4`** | **consigner le relevé partiel** — la preuve `R7` est due |

> **`S9` vient en cinquième, et son rang est contraint.** Il suit `S4` parce que
> l'invariance des fichiers se constate d'abord, et il précède `O4` parce que le
> relevé partiel doit consigner **son résultat**.

> **Aucun redémarrage du démon n'ayant été commandé ici, aucune propagation n'est
> qualifiée : le compte attendu est ZÉRO.** Si `S9` rend zéro identifiant
> nouveau, **la composante 1 de `R5.e` est satisfaite**.
>
> **S'il en rend un**, le verdict est **`R5.e ÉCHOUE — REDÉMARRAGE NON
> ATTRIBUÉ`**, et la conduite est **celle du §7.1** — rapport, aucun acte terrain
> nouveau, aucune nouvelle tentative, et la question de la détectabilité tranchée
> au rapport.
>
> **`P2A-6` ne s'applique PAS automatiquement ici, et la V12 le prescrivait à
> tort.** Nous sommes **déjà** en séquence d'`ABORT`, en sortie, après `S4` : un
> `ABORT` ne peut pas s'y déclencher une seconde fois. **Ce que le §7.1 demande
> est de dire si un `ABORT` était dû PLUS TÔT** — au moment où ce redémarrage est
> survenu — et cette question-là, elle, doit être tranchée au rapport.
>
> **`S4` est ici limité à la preuve d'invariance des fichiers d'origine.** Son
> volet « invocation effective du processus » est **sans objet** : le processus
> n'a pas été redémarré, et le relire n'apprendrait rien. **Aucune lecture
> inutile, aucun processus interrogé sans nécessité.**
>
> **Le reste, par nature :**
>
> | | |
> |---|---|
> | **`S3`** | **INTERDIT** — redémarrer ici **introduirait** l'interruption que l'`ABORT` vient précisément d'éviter |
> | **`S5`** | **sans objet** — il porte sur les lignes produites **après un redémarrage de retour** qui n'a pas lieu |
> | **`S6`** | **sans objet** — le processus n'a pas été touché, sa qualité de détenteur unique n'a pas été mise en cause |
> | **`S8`** | **sans objet** — `R5.d` compare un état **après redémarrage** ; sans redémarrage, la référence du préflight fait foi |
>
> **Et le sort de chaque preuve, explicitement :**
>
> | Preuve | Sort | Motif |
> |---|---|---|
> | **`R1`** | **DUE** — portée par `S7` | le répertoire de surcharge a bien été créé, puis supprimé |
> | **`R2`** | **DUE** — portée par `S4` restreint | les fichiers d'origine doivent être prouvés invariants |
> | **`R3`** | **SANS OBJET** | elle compare l'**invocation effective du processus** ; le processus **n'a pas été redémarré**, son invocation ne peut donc pas avoir changé. `S2` a par ailleurs vérifié l'invocation **résultante** de l'unité |
> | **`R4`** | **SANS OBJET** | elle porte sur les lignes **produites après le redémarrage de retour** — lequel n'a pas lieu |
> | **`R5.a` à `R5.d`** | **SANS OBJET** | `S5`, `S6` et `S8` le sont, et pour les mêmes motifs |
> | **`R5.e`** | **DUE** — portée par **`S9`** | le démon **n'a pas été redémarré**, donc **aucune propagation n'est qualifiée** et le compte attendu est **zéro**. **`R5.e` doit l'établir, pas le présumer** : `S9` est conduit, et il **MUST** rendre **zéro identifiant nouveau**. **S'il en rend un, la conduite est celle du §7.1 — et d'aucun autre paragraphe** |
> | **`R6`** | **SANS OBJET** | elle chiffre le **volume ajouté sous verbosité élevée** ; la fenêtre n'a **jamais été ouverte**, et le lot n'a **rien ajouté** au journal |
> | **`R7`** | **DUE** — portée par `O4` | un `ABORT` a eu lieu |

> **`O4` est admissible dans TOUTE phase**, dès qu'un `ABORT` survient — phase 0,
> 1, 2 ou 3 — et **jamais** en dehors de ce cas. La V3 le rangeait dans la seule
> phase 2, ce qui laissait `R7` sans acte pour les `ABORT` des autres phases.

#### 8.1.2 La propagation attendue — cinq conditions cumulatives

> **Arbitrage humain, consigné.** Le redémarrage temporaire de `<unité-pont>`,
> **conséquence nécessaire** du redémarrage de `<unité-démon>` par `F-13`, est
> **accepté** — *« à condition qu'il soit attendu, borné et observé »*. La piste
> consistant à neutraliser la dépendance est **exclue** : ce serait une
> modification plus profonde du dispositif historique pour éviter un redémarrage
> **désormais compris et réversible**.

**Un redémarrage de `<unité-pont>` est la PROPAGATION ATTENDUE si et seulement
si les cinq conditions sont réunies. Il suffit qu'une seule manque pour que
`P2A-6` se déclenche.**

| # | Condition | **Par quel acte elle est vérifiée** |
|---|---|---|
| **1** | **attribution POSITIVE** — voir §8.1.2.1 : la transition de `<unité-démon>` est **strictement encadrée** par l'arrêt puis le démarrage de `<unité-pont>`, **et** `<unité-superviseur>` est demeuré **inactif** de bout en bout | `M5 bis` / `S3 bis` — journaux de **`<unité-pont>`**, **`<unité-démon>`** et `<unité-superviseur>`, lus rétrospectivement |
| **2** | il survient **dans les `60 s`** qui suivent la commande — **valeur CHOISIE**, soumise au §9 | `M5 bis` / `S3 bis` — horodatage des transitions au journal |
| **3** | il est **UNIQUE** : **exactement UN** identifiant d'invocation de `<unité-pont>` **nouveau par rapport au baseline de `P2 bis` ET à ceux déjà dénombrés** — voir §8.1.2.2 | `M5 bis` / `S3 bis` — **décompte au journal** |
| **4** | le **compteur de relances du pont demeure inchangé** | `M5 bis` / `S3 bis` — **corroboration seulement**, jamais compteur |
| **5** | le pont revient **`active/running`** dans la même fenêtre, et `<unité-superviseur>` est **NOMINAL** au sens du §8.1.2.3 | `M5 bis` / `S3 bis` |

#### 8.1.2.1 L'attribution est CAUSALE, pas seulement temporelle

**Le défaut que cela corrige.** La V8 n'attribuait que par la **fenêtre de temps**.
Un redémarrage du pont **commandé par le superviseur** — le premier acte du
chemin de `F-12` — qui tomberait dans les `60 s` suivant `S3` aurait été
**absorbé comme propagation attendue**. C'eût été prendre le début d'une
défaillance pour un effet du lot.

> **Le second défaut, que la V9 signalait sans le fermer.** Ses deux conditions
> étaient **négatives** — *dans la fenêtre*, et *le superviseur n'a pas pu agir*.
> **Aucune n'établissait que c'était MOI l'auteur.** Un tiers acteur redémarrant
> le pont pendant que le superviseur dort aurait satisfait les deux, et **aurait
> été absorbé**. La V9 le portait en réserve ; **la V10 le ferme**.

**Trois éléments, dont le premier est POSITIF et décisif :**

| # | Élément | Nature |
|---|---|---|
| **(a)** | **la transition de `<unité-démon>` est strictement encadrée** par celle de `<unité-pont>`, ce qui exige **quatre événements au journal, dans cet ordre** : **(1)** arrêt de `<unité-pont>` · **(2)** arrêt de `<unité-démon>` · **(3)** démarrage de `<unité-démon>` · **(4)** démarrage de `<unité-pont>` | **POSITIF** — il rattache les deux unités **l'une à l'autre** |
| **(b)** | `<unité-superviseur>` est demeuré **inactif** sur toute la fenêtre | négatif — il **écarte** l'auteur le plus probable |
| **(c)** | la transition du démon **correspond à la commande de `M5` ou de `S3`** : elle survient **après l'instant exact de la commande**, relevé par `M5` / `S3`, et l'**identifiant d'invocation de `<unité-démon>` lu au journal** est **le même** que celui relevé par `M6` / `S3` | **POSITIF** — il rattache la séquence **à mon acte** |

> **Le terme comparé par `(c)`, nommé sans ambiguïté.** C'est l'**identifiant
> d'invocation de `<unité-démon>`** — **la même valeur** des deux côtés : celle
> que rendent les propriétés de l'unité, relevée par `M6` / `S3`, et celle que
> portent les entrées de journal de cette unité. **Que le journal la porte
> effectivement est établi par `P5`**, et non supposé.

> **Pourquoi (a) est structurel et non circonstanciel.** `F-13` établit que le
> pont **requiert** le démon. **Que cette dépendance produise l'ordre exigé par
> `(a)` n'est PAS affirmé ici** : c'est **`P5` qui l'établit**, ou qui ne
> l'établit pas — §6.1.1. La V11 l'affirmait *« par construction »*, **sans
> qu'aucune pièce du corpus ne le porte**.
>
> **Ce qui demeure vrai indépendamment du verdict de `P5`** : un redémarrage du
> pont **seul** — par le superviseur, par un tiers, par quiconque — **n'encadre
> AUCUNE transition du démon**, et échoue donc à `(a)` **quel que soit l'ordre**
> que l'installation produit par ailleurs.

> **Ce que cela ferme, nommément.** Un **tiers acteur**, ou une **origine
> inconnue**, produit un arrêt et un démarrage du pont **sans transition du démon
> entre les deux**. `(a)` n'est pas satisfait ⇒ la propagation est **NON
> QUALIFIÉE** ⇒ **`P2A-6`**. La réserve que la V9 portait est **levée**.

> **ET SI `(a)` N'EST PAS DÉMONTRABLE.** Si le journal ne porte pas **les quatre
> événements énumérés ci-dessus — arrêt du pont, arrêt du démon, démarrage du
> démon, démarrage du pont — dans cet ordre**, parce qu'il ne les émet pas, parce
> qu'ils ne sont pas rattachables, ou pour toute autre raison, alors
> **l'attribution positive n'est pas établie**, et **la propagation demeure NON
> QUALIFIÉE**. `P2A-6` s'applique. **Le lot ne se rabat pas sur les conditions
> négatives seules**, et **ne présume rien** de ce que le journal devrait
> contenir.
>
> **Mais ce cas devrait être écarté AVANT la mutation**, par `P5` : c'est
> précisément ce que la précondition d'observabilité établit. **Si `P5` a conclu,
> un échec de `(a)` en cours de lot signale un changement, non une ignorance.**

> **La synchronisation la rend praticable.** Les deux redémarrages sont exécutés
> **juste après une fin de cycle constatée** (§4.1) : la fenêtre de `60 s` tombe
> alors dans l'intervalle de `≥ 180 s` où le superviseur est inactif par
> construction. **Vérifier n'est pas espérer** : la condition est constatée, non
> présumée.

> **En cas de doute, `D-1` demeure confirmateur du `STOP`.** Si l'attribution ne
> peut pas être établie — journal illisible, transition non rattachable,
> superviseur actif à un instant quelconque de la fenêtre — alors la propagation
> **n'est pas qualifiée**, `P2A-6` se déclenche, **et `D-1` vaut signal de
> `F-12`** : `P2A-5`, conduite du §8.3.4, `STOP`.

#### 8.1.2.2 Compter les transitions — le canal, et pourquoi `O2` n'y suffit pas

**`O2` échantillonne toutes les `15 s`.** Deux transitions du pont survenues à
l'intérieur d'un même intervalle seraient **indiscernables** d'une seule : la
condition 3 de la V8 était **prescrite sans moyen de l'établir**.

| | |
|---|---|
| **Canal retenu** | le **journal système de `<unité-pont>`**, lu **rétrospectivement** sur la fenêtre de qualification |
| **Pourquoi il suffit** | il porte **chaque** transition, qu'elle soit échantillonnée ou non, et chaque entrée est rattachée à un **identifiant d'invocation** |
| **L'UNITÉ COMPTÉE, définie sans ambiguïté** | **un redémarrage du pont = un identifiant d'invocation NOUVEAU**, c'est-à-dire **absent du baseline relevé par `P2 bis`** et de tous ceux déjà dénombrés. **Le mot « transition » n'est plus employé comme unité de compte** : il désignait indifféremment un arrêt, un démarrage ou le couple des deux |
| **Ce qui est compté** | le **nombre d'identifiants d'invocation nouveaux par rapport au baseline de `P2 bis` ET à ceux déjà dénombrés**. **Jamais le nombre d'identifiants distincts** : le baseline en est un, et le compter ferait apparaître un redémarrage là où il n'y en a pas. **Jamais non plus « nouveaux par rapport au baseline » seul** : après `M5`, l'identifiant issu de sa propagation est lui aussi nouveau par rapport au baseline, et le recompter à `S3` ferait apparaître deux redémarrages là où il y en a un |
| **Verdict de la condition 3** | **exactement UN** nouvel identifiant. **Deux ou plus ⇒ `P2A-6`**. **Zéro ⇒ le pont n'a pas redémarré** — cas nominal du §8.1.3, **aucune qualification à conduire** |
| **Ce que `NRestarts` y fait** | **rien, comme compteur.** Il est relevé en **corroboration** de la condition 4, et le §3.0 rappelle que son immobilité est une **observation terrain**, non une propriété |

#### 8.1.2.3 « `<unité-superviseur>` nominal » — définition et fenêtre

**Définition, et elle est close.** `<unité-superviseur>` est **nominal** si, sur
la fenêtre d'observation définie ci-dessous, **les quatre énoncés sont vrais** :

| # | |
|---|---|
| **a** | **aucune invocation** — terminée ou en cours — n'atteint le seuil de **`P2A-11`** |
| **b** | **toute invocation terminée** l'a été par le **chemin de succès** du gestionnaire de services |
| **c** | **aucun enregistrement d'échec** — échec, expiration, sortie anormale — ne figure à son journal |
| **d** | **aucune invocation n'a été active** à un instant quelconque de la fenêtre de qualification — c'est la condition d'attribution du §8.1.2.1 |

**Fenêtre d'observation** : de la **commande de redémarrage** — `M5` ou `S3` — au
**retour du pont à `active/running`**, **et en tout état de cause au moins les
`60 s`** de la fenêtre de qualification. Elle est lue **rétrospectivement** par
`M5 bis` / `S3 bis`, ce qui la couvre **en entier**, sans dépendre de la
fréquence d'échantillonnage.

> **L'énoncé `d` est plus strict que les trois autres**, et c'est voulu : il ne
> demande pas que le superviseur aille bien, mais qu'il **n'ait pas pu agir**.

> **Tout le reste demeure un `ABORT`**, sans exception : un redémarrage du pont
> **hors** de ces fenêtres · un redémarrage **supplémentaire** · un redémarrage
> d'**origine inconnue** ou non attribuable à `M5` ou `S3` · un **compteur de
> relances qui bouge** · un pont qui **ne revient pas** nominal · un superviseur
> qui **cesse** de l'être.

> **La propagation est ATTENDUE, elle n'est pas AUTORISÉE à dériver.** Cette
> clause n'ouvre rien d'autre : elle **nomme un événement précis**, le borne par
> cinq conditions vérifiables, et **laisse tout le reste sous `ABORT`**.

#### 8.1.3 Conduite pendant la qualification différée

**Les cinq conditions ne se qualifient pas toutes à l'instant du redémarrage.**
Les conditions 3 et 5 exigent la **fenêtre de `60 s`** entière. Il existe donc un
intervalle où le lot **ne sait pas encore** s'il a affaire à la propagation
attendue. **La V8 ne disait pas ce qui s'y passe. Voici la conduite.**

| | |
|---|---|
| **Durée** | de la commande de redémarrage jusqu'à la qualification, **au plus `60 s`** |
| **Ce qui s'y fait** | **l'acte de qualification lui-même** — **`M5 bis`** en phase 1, **`S3 bis`** en phase 3 — · **les actes normaux de la phase en cours** — `M6` en phase 1, **`S4` à `S8`** en phase 3 — · et **`O2` en surveillance continue**, à sa fréquence, par l'extension du §6.3.1 |
| **Ce qui ne s'y fait pas** | **aucun acte SUPPLÉMENTAIRE hors de la liste close**, et **aucune mutation** |

> **`S9` n'est PAS un acte de cette fenêtre**, et la V11 l'y rangeait à tort. Son
> rang est **après** la fin de la qualification et **après** le retour du pont à
> nominal : le conduire pendant la fenêtre produirait un dénombrement
> **incomplet**. L'énumération s'arrête donc à **`S8`**.
>
> **La V12 plaçait cette note À L'INTÉRIEUR du tableau**, ce qui détachait la
> ligne *« Ce qui ne s'y fait pas »* et la laissait **orpheline**. Elle est
> désormais **hors du tableau**.

> **Correction de la V9, et elle bloquait le lot.** Elle prescrivait *« `O2`
> seulement […] aucune autre lecture »*, ce qui **interdisait `M6`** — la
> vérification des 10 secondes, qui tombe précisément dans cette fenêtre — **et
> tous les actes de sortie `S4` à `S8`**. Le lot se serait **empêché lui-même**
> de conduire ses propres actes permis.
>
> **La règle correcte n'est pas restrictive sur la phase, elle l'est sur la liste
> close** : ce qui y figure et relève de la phase en cours reste permis ; ce qui
> n'y figure pas demeure interdit, et le doute vaut `P2A-1`.

> **RÈGLE ABSOLUE, rappelée.** **Aucune attente volontaire à travers les 90 s du
> chemin de `F-12`.** La qualification n'en est pas une : l'attribution du
> §8.1.2.1 **exige** que `<unité-superviseur>` soit demeuré inactif, donc que le
> chemin de `F-12` **ne soit pas engagé**. **Dès qu'il pourrait l'être, la
> qualification s'arrête et la conduite d'urgence prend la main.**

> **`D-2` et `P2A-12` demeurent PRÉEMPTIFS pendant toute la qualification.** Si la
> durée d'une invocation de `<unité-superviseur>` atteint le seuil de `P2A-12`,
> la conduite du §8.3.4 **préempte la qualification sans délibération** — et la
> qualification **est abandonnée**, jamais reprise ni menée à son terme après
> coup.

> **Le cas NOMINAL où il n'y a rien à qualifier.** Si, sur la fenêtre, **aucun
> nouvel identifiant d'invocation du pont n'apparaît** — **zéro redémarrage** —
> alors **il n'y a pas de propagation à qualifier** : `P2A-6` **ne se déclenche
> pas**, aucune issue du tableau ci-dessous n'est prononcée, et **le lot poursuit
> normalement**.
>
> **Ce cas n'est ni un échec ni une anomalie.** La V9 ne l'écrivait pas, et son
> silence pouvait se lire comme une qualification manquée — donc comme un `ABORT`
> sur un déroulement **parfaitement nominal**.

**Les trois issues de la qualification, lorsqu'un redémarrage a bien eu lieu, et
il n'y en a pas d'autre :**

| Issue | Conduite |
|---|---|
| **QUALIFIÉE** — les **cinq** conditions établies dans la fenêtre | la propagation est **attendue** ; `P2A-6` **ne se déclenche pas** ; le lot poursuit |
| **NON QUALIFIÉE** — une condition **manque** | **`P2A-6`** → `ABORT`. Et si le manque porte sur l'**attribution**, **`D-1` vaut signal de `F-12`** → `P2A-5` → conduite du §8.3.4 → **`STOP`** |
| **NON ACQUISE À TEMPS, ou DOUTEUSE** — la fenêtre de `60 s` s'écoule sans que les cinq soient établies, ou l'une d'elles demeure indécidable | **`ABORT` ET `STOP`**, tous deux **explicites**. Le lot **ne présume pas** de la qualification, et **ne prolonge pas** la fenêtre pour l'obtenir |

> **Le doute ne se résout pas en faveur du lot.** Une qualification incertaine est
> traitée **exactement** comme une qualification manquée.

### 8.2 `STOP`

Les quatre cas du `w4p-ouverture.md` §10.1 s'appliquent sans allègement. S'y
ajoute, **propre à ce lot** : **toute nécessité de modifier le pont historique**
— même transitoirement, même pour réparer — est un **`STOP` pour nouvel
arbitrage humain**, et **jamais** une décision du lot.

> **Une exception, nommée, et une seule** : la **propagation attendue** du
> §8.1.2, **acceptée par arbitrage humain préalable**, n'emporte **pas** de
> `STOP`. Elle est **prévue, bornée et observée** — elle n'est pas une *nécessité
> découverte en cours de route*, qui est ce que cette clause vise.
>
> **Toute autre atteinte au pont emporte le `STOP`**, y compris une propagation
> qui **cesserait** de satisfaire l'une des cinq conditions.

> **Un `STOP` n'est pas une issue**, et les verdicts du §5 **ne sont pas** l'issue
> de `W4-P`.

#### 8.2.1 `STOP AVANT MUTATION` — un arrêt d'une autre nature

**Il se prononce dans un seul cas** : `P5` rend **`PRÉCONDITION NON ÉTABLIE`**
(§6.1.1).

| | `STOP AVANT MUTATION` | `ABORT` terrain |
|---|---|---|
| Quand | **en phase 0**, avant `M1` | en phase 1, 2 ou 3 |
| Ce qui a été muté | **rien** | la surcharge existe, ou le démon a été redémarré |
| Ce qui est dû | la **consignation par `P6`** du verdict de `P5`, de ses **deux preuves** et de leur concordance ou discordance | le **retour de la phase 3** et **toutes** les preuves du §7 |
| Restauration | **sans objet — il n'y a rien à restaurer** | **due, et intégralement** |

> **La phase 1 n'est jamais engagée.** `M1` n'est pas exécuté, aucun répertoire
> n'est créé, aucun redémarrage n'est commandé. **Le lot s'arrête avant d'avoir
> touché à quoi que ce soit**, et c'est précisément ce qui distingue cet arrêt de
> tous les autres.

> **Ce n'est pas un échec du lot, c'est un résultat.** Si la précondition
> d'observabilité n'est pas établie, alors les conditions `(a)` et `(c)` du
> §8.1.2.1 **ne sont pas praticables sur cette installation** — et le dire est
> plus utile que de muter pour le découvrir.

### 8.3 Détection du chemin d'échec, et conduite du retour

**Le budget est celui de `F-12`, et il est déclaré : 90 s.** Le superviseur, sur
échec de sonde, **redémarre le pont**, **attend 90 s**, puis resonde. **Si cette
seconde sonde échoue, il redémarre la machine.** Tout ce qui suit tient dans cet
intervalle, ou ne s'y engage pas.

#### 8.3.1 Trois détecteurs, dont deux indépendants des lignes propres

> **Correction de fond de la V2.** Elle faisait du journal du superviseur le
> **canal unique**. Or `w4p1-homologation.md` §7 homologue que **24 invocations
> sur 76 ne produisent aucune ligne propre**. Un échec de sonde pouvait donc
> survenir **sans trace lisible**, et le garde-fou serait resté muet.
>
> **Aucune hypothèse n'est formée sur la cause de ces absences.** Le fait suffit :
> **on ne peut pas compter dessus**, et la détection est refondée sans elles.

| Réf | Détecteur | Ce qu'il établit | Dépend d'une ligne propre ? |
|---|---|---|---|
| **`D-1`** | l'**identifiant d'invocation** ou l'**instant de démarrage** de `<unité-pont>` **change**, **hors propagation attendue du §8.1.2** | le pont **a été redémarré par le superviseur** — le chemin de `F-12` est **engagé** | **non** |
| **`D-2`** | la durée écoulée depuis l'instant de démarrage d'une invocation de `<unité-superviseur>` — **terminée ou EN COURS** — atteint le seuil de **`P2A-12`**, soit **`10 s`**. **`P2A-11` n'y entre PAS** | le chemin d'échec est **engagé ou suspecté** : la conduite déclarée y insère un **sommeil de 90 s**, qui allonge l'invocation d'un ordre de grandeur | **non** |
| **`D-3`** | une **ligne propre** de `<unité-superviseur>` signale autre chose qu'un cycle nominal | confirmation | **oui** — **jamais utilisé seul**, et son absence ne vaut **rien** |

> **`D-1` doit exclure la propagation attendue, et elle seule.** Sans cette
> qualification, il aurait déclenché `P2A-5` — donc la conduite d'urgence et un
> `STOP` — sur un redémarrage **provoqué par le lot lui-même**, et non par le
> superviseur. **L'exclusion ne porte que sur les cinq conditions du §8.1.2** :
> un redémarrage du pont qui n'y satisfait pas **reste** un signal de `F-12`.

> **`D-1` et `D-2` portent sur des états que systemd tient pour TOUTES les
> invocations** — `w4p1-homologation.md` l'établit : les enregistrements de cycle
> de vie étaient présents pour **76 sur 76**. **`D-3` est un bonus, jamais un
> prérequis.**

#### 8.3.2 Le canal, la fréquence, et ce qu'elles bornent réellement

| | |
|---|---|
| **Canaux** | l'**état des unités**, relevé par consultation de leurs propriétés courantes — pour `D-1` et `D-2`, **et c'est ce que `O2` lit** ; le **journal système de `<unité-pont>`** — pour la part de `D-1` qui exige de distinguer la **propagation attendue** d'un redémarrage qui ne l'est pas, §8.1.2 — **lu par `M5 bis`, `S3 bis` et `S9`, JAMAIS par `O2`** ; le **journal système de `<unité-superviseur>`** — pour `D-3` |
| **Fréquence maximale** | un relevé **au plus toutes les 15 s** pendant toute la fenêtre. **Aucun suivi continu, aucune session ouverte** |
| **Ce que cette fréquence borne** | **l'intervalle entre deux observations du lot**, et **rien d'autre** |

> **`O2` ne gagne aucun canal.** Nommer le journal du pont dans ce tableau
> pourrait se lire comme un **élargissement implicite** de `O2`. Il n'en est
> rien : `O2` lit les **propriétés d'unité** et, quand elles existent, les
> **lignes propres du superviseur**. **Le journal du pont appartient à `M5 bis`,
> `S3 bis` et `S9`**, et à eux seuls.
>
> **La V11 plaçait cette note À L'INTÉRIEUR du tableau**, qu'elle coupait en
> deux : les lignes *« Fréquence maximale »* et *« Ce que cette fréquence
> borne »* s'en trouvaient détachées. Elle est désormais **hors du tableau**.

> **Correction de la V9.** Elle écrivait *« le journal système de la seule
> `<unité-superviseur>` »*, ce qui **est devenu faux** dès que `D-1` a dû exclure
> la propagation attendue : cette exclusion se lit **au journal du pont**. Le mot
> *« seule »* est retiré, et le canal est nommé.

> **Ce qu'elle ne borne PAS, et la V2 prétendait le contraire.** Elle ne borne
> **pas** la latence de détection : entre l'événement et sa visibilité s'ajoutent
> des délais **non établis**. *« ≤ 15 s + un délai inconnu »* **n'est pas une
> borne**, et cette formulation est **retirée**.
>
> **La fréquence est donc un choix de conduite, pas une garantie** — et le §8.4
> la range parmi les seuils choisis.

#### 8.3.3 La marge restante, calculée sur un observable

La V2 basculait de conduite à **45 s**, valeur **arbitraire**. Elle est
**supprimée**. Ce qui la remplace se **calcule** :

| Grandeur | Origine |
|---|---|
| `t_départ` — instant de démarrage de l'invocation en cause | **observé**, propriété de l'unité |
| **90 s** — sommeil déclaré avant la seconde sonde | **dérivé du corpus**, `F-12` |
| **5 s** — budget déclaré de la sonde | **dérivé du corpus**, `A-O2` homologué |

> **La seconde sonde ne peut pas commencer avant `t_départ + 90 s`**, la sonde en
> échec étant elle-même contenue dans l'invocation et bornée à 5 s déclarés.
> **La marge restante à l'instant `t` est donc au moins `t_départ + 90 s − t`**, et
> elle se calcule à chaque relevé.

#### 8.3.4 Conduite — et la règle de sûreté qui la commande

> **RÈGLE DE SÛRETÉ.** Dès qu'un échec est **suspecté**, la verbosité élevée
> **MUST NOT** être laissée volontairement en place pour traverser la seconde
> sonde, **si une conduite plus sûre est disponible**. La conduite plus sûre est
> le **retour immédiat**, et c'est la conduite par défaut.

| Cas | Conduite |
|---|---|
| **marge restante suffisante** — elle **excède `30 s`**, soit les **`10 s`** de vérification de `P2A-4` augmentées d'une **réserve CHOISIE de `20 s`** | **conduire le retour immédiatement**, sans attendre aucune frontière de cycle : la synchronisation du §4.1 est **suspendue** |
| **marge restante insuffisante**, ou vérification de `P2A-4` **non obtenue** dans son délai | **`STOP` immédiat et arbitrage humain.** Le lot **ne choisit pas** entre deux conduites risquées |

> **La réserve de `20 s` est ÉCRITE ici, et c'est un choix.** La V3 la renvoyait
> au §9, qui la renvoyait au §8.3.4 : **circulaire, et sans valeur nulle part**.
> Elle couvre ce que `P2A-4` ne couvre pas — le délai entre la décision et le
> lancement effectif du retour, et l'écart entre la vérification et la reprise
> réelle du service. **Rien ne la dérive d'une pièce** : elle est soumise au §9.

> **Il n'y a pas de troisième branche, et il faut le dire.** Dans le second cas,
> **aucune conduite n'est sûre** : redémarrer près de la seconde sonde peut la
> faire échouer ; ne rien faire la laisse s'exécuter sous verbosité élevée. **Le
> lot déclare l'impasse plutôt que d'arbitrer un risque qui ne lui appartient
> pas** — et c'est une raison de plus de relever fréquemment.

> **La durée d'un redémarrage n'est établie nulle part**, et ce lot ne la mesurera
> pas pour se préparer. C'est pourquoi la marge est comparée à une **vérification**
> — `P2A-4` — et non à une prédiction.

### 8.4 Trois natures de valeur, et ce lot n'en produit qu'une seule sorte

| | **Dérivée du corpus** | **Choisie humainement** | **Produite comme résultat** |
|---|---|---|---|
| Ce que c'est | une valeur **lue** dans une pièce opposable | une **règle de conduite** du lot | une **valeur opposable** qui juge un système |
| Qui la fixe | **personne** — elle est déjà là | le bornage, **sous réserve de l'autorisation** | un producteur de critère, sous le §10.3.3 |
| Soumise à l'autorisation ? | **non** — la soumettre laisserait croire qu'elle se négocie | **oui**, et le §9 les énumère | sans objet |
| Ce qu'elle vaut hors du lot | ce que sa pièce lui donne | **rien** | elle devient contractuelle |

**Les valeurs DÉRIVÉES employées ici, et leur pièce :**

| Valeur | Pièce |
|---|---|
| **5 s** — budget de la sonde ; **fixe `P2A-11`** | `A-O2` homologué, registre configuration déclarée |
| **90 s** — sommeil avant la seconde sonde ; base du calcul du §8.3.3 | `F-12`, même registre |
| **180 s** — cadence, tolérance ne pouvant que retarder ; base de la marge du §4.2 | `A-O4` homologué |
| **7 lignes par session** — plancher de volume du §3.2 | `w4-cadrage-activation-debug.md` §E.1 |

**Les valeurs CHOISIES, toutes soumises au §9 :**

| Valeur | Ce qu'elle règle |
|---|---|
| **15 min** · **3 cycles** | la fenêtre (§4.1) |
| **au plus 15 s** | l'intervalle entre deux relevés (§8.3.2) — **pas** une latence de détection |
| **10 s** *(vérification)* | le délai de vérification après un redémarrage — `P2A-4` |
| **10 %** et **100 Mio** | espace libre et croissance du journal — `P2A-7` |
| **`10 s`** *(détection)* | le seuil de `P2A-12`, **au-dessus du régime observé** et **sous la signature du chemin d'échec** |
| **`20 s`** | la réserve exigée en sus des `10 s` de vérification, d'où le **`30 s`** du §8.3.4 |
| **`60 s`** | la fenêtre de la **propagation attendue** — conditions 2 et 5 du §8.1.2 |

> **Les deux `10 s` ne sont pas la même valeur** et ne se déduisent pas l'une de
> l'autre : l'une borne une **vérification après redémarrage**, l'autre un
> **seuil de détection**. Leur égalité numérique est **fortuite**, et chacune est
> soumise séparément.

> **Chacune de ces valeurs est ÉCRITE à l'endroit où elle s'applique**, et
> reprise ici pour mémoire. **Aucune n'est définie par renvoi** : la V3 en
> laissait deux dans un cycle de renvois où la valeur n'existait nulle part.

> **`W4-P2` ne produit AUCUNE valeur de la troisième colonne.** Aucun de ses
> seuils — dérivé ou choisi — ne **MUST** être repris, cité ou dérivé comme valeur
> de critère, de `seuil_C1`, de `borne_sonde` ou d'`occupation_max`. **Les
> confondre serait produire par la porte de service ce que la clause de
> non-dérivation interdit.**

> **Et une valeur dérivée ne devient pas un choix parce qu'un lot s'en sert.** Le
> budget de 5 s et le sommeil de 90 s **ne figurent pas** au §9 : les soumettre
> laisserait croire qu'ils se négocient, alors qu'ils sont **des faits déclarés de
> l'installation**.

## 9. Élément 6 — Autorisation propre

> ### **NON DONNÉE.**
>
> `w4q-precondition2-arbitrage.md` décision 5 exige *« son **autorisation propre**,
> distincte de la présente »*. **Ce document ne la constitue pas.**
>
> **`W4-P2` MUST NOT être exécuté, même partiellement, avant que cette
> autorisation soit donnée.** La phase 0 elle-même, bien qu'en lecture, **attend**.

**Ce que l'autorisation devra dire, pour être suffisante :**

| # | Point à trancher |
|---|---|
| 1 | qu'elle **autorise `W4-P2`** tel que borné ici, **et rien d'autre** |
| 2 | qu'elle **autorise nommément la mutation** — création d'une surcharge portant `-g` — et **les deux redémarrages** de `<unité-démon>` qu'elle implique |
| 2 bis | qu'elle **accepte la PROPAGATION ATTENDUE** du §8.1.2 — le redémarrage temporaire de `<unité-pont>` comme **conséquence nécessaire** de `F-13` — et **elle seule**, sous ses **cinq conditions cumulatives** |
| 3 | si le **plafond de 15 minutes** et le **minimum de 3 cycles** sont retenus |
| 3 bis | si les **valeurs CHOISIES** sont retenues, **chacune nommée avec sa valeur** : **15 s** d'intervalle entre relevés · **10 s** de vérification après redémarrage, `P2A-4` · **10 %** d'espace libre et **100 Mio** de croissance, `P2A-7` · **`10 s`** de seuil de détection, `P2A-12` · **`20 s`** de réserve, portant le seuil du §8.3.4 à **`30 s`** · **`60 s`** de fenêtre de propagation, §8.1.2. **Ce sont des choix de bornage, au même titre que la fenêtre** |
| 3 ter | **rien d'autre n'est soumis.** Les valeurs **dérivées** — budget de 5 s portant `P2A-11`, sommeil de 90 s, cadence de 180 s, plancher de 7 lignes — **ne sont pas des choix** et ne figurent pas ici. La **bascule à 45 s de la V2 est supprimée**, et rien ne la remplace : la marge se **calcule** (§8.3.3) |
| 3 quater | **`P2A-11` n'y figure pas** : il vaut **`5,000 s`**, le budget **dérivé**, et n'est donc pas un choix. **Le faux positif qu'il comporte est assumé au §8.1**, et l'autorisation vaut acceptation de cet effet — un `ABORT` ordinaire possible sur un cycle nominal |
| 4 | qu'elle **n'autorise ni `T0`, ni `T1`, ni `T2`** · **aucune modification du superviseur** · **aucune modification du pont AUTRE que la propagation attendue** du §8.1.2, seule exception admise et déjà arbitrée au point 2 bis · **aucun des quatre actes réservés** |

## 10. Ce que ce document ne fait pas

Il **n'exécute rien**, **n'autorise rien**, **ne mute rien**, **ne relève aucune
mesure d'expérience**, **ne produit ni `M6`, ni borne, ni seuil, ni critère**,
**ne rouvre pas `C1`**, **ne rouvre pas la discrimination par `Command:`**,
**n'ouvre pas `T0`**, et **ne traite aucune réserve rédactionnelle de `W4-P1`**.

Il borne un lot, et s'arrête là.

## 11. Historique de révision

| Version | Objet |
|---|---|
| **1** | Ouverture et bornage du second lot terrain de `W4-P`, visant l'observabilité des clôtures et la dérivabilité d'une durée de session. Voie surcharge retenue sur faits d'audit, voie XML écartée. Six éléments réunis ; **élément 6 non donné**. Aucune exécution, aucune mutation, aucune autorisation. |
| **2** | Après audit. `BL-1` : marge de synchronisation refondée sur la **cadence déclarée** et le **budget déclaré de 5 s**, l'enveloppe de `W4-P1` cessant d'y servir de borne de sonde ; objectifs renommés `P2-O1`…`P2-O5` pour lever la collision avec `B-O1`/`B-O2` homologués. `BL-2` : §8.3 — canal, fréquence maximale de 15 s, latence bornée, synchronisation suspendue, et règle en deux branches pour que le retour ne provoque pas lui-même la seconde sonde en échec. `BL-3` : §5.1 — le §E.3 devient un **risque de sûreté**, avec `P2A-11` et `P2A-12` opposables, **sans qualifier `C1` ni produire de borne**. `BL-4` : quatrième constat de sortie restauré — processus unique, **détenteur du périphérique** par deux méthodes indépendantes, service des clients — avec les actes `S4` à `S6` ajoutés à la liste close. `C-1` volume corrigé à **2 996**. `C-2` §8.4, seuils internes distingués des seuils produits. `C-3` seuils de `P2A-7` soumis à l'autorisation. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **3** | Après réaudit. `RB-1` : le journal du superviseur cesse d'être le canal unique — trois détecteurs, dont deux **indépendants des lignes propres**, `W4-P1` ayant homologué que 24 invocations sur 76 n'en produisent aucune ; **aucune hypothèse sur la cause des absences**. `RB-2` : la fausse borne *« ≤ 15 s + délai inconnu »* est retirée, la **bascule arbitraire à 45 s supprimée**, la marge **calculée** sur un observable à partir des 90 s déclarées, et la règle de sûreté sur la seconde sonde énoncée avec son impasse assumée. `RB-3` : actes `S7`, `S8` et `O4` ajoutés — `R1`, `R5.d` et `R7` avaient une preuve sans acte. `RB-4` : §8.4 distingue **dérivé**, **choisi** et **produit** ; `P2A-11` cesse de référer à une population non homogène et repose sur une fraction du budget dérivé ; `P2A-12` demeure dérivé. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **4** | Après troisième réaudit. `RB3-1` : les deux seuils sans valeur — fraction de `P2A-11` et réserve du §8.3.4 — reçoivent **`0,80`**, soit **`4,000 s`**, et **`20 s`**, soit un seuil de **`30 s`** ; le **renvoi circulaire est supprimé** et chaque valeur est classée dérivée ou choisie, les choisies étant soumises nommément. `RB3-2` : `P2 bis` relève au préflight les **références du pont et du superviseur**, sans lesquelles `D-1` et `P2A-6` étaient **inopérants au premier redémarrage** ; `S8` demeure la mesure finale. `RB3-3` : l'exception `P2A-2`/`P2A-3` est complétée par `S7` et `O4`, `S3` restant interdit ; `O4` devient admissible **dans toute phase** sur `ABORT`. `C-4` premier bras de `D-2` quantifié. `C-5` tolérance de 10 s retirée. `C-6` phrase sur les valeurs de site corrigée. `C-7` ordre de l'historique rétabli. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **5** | Après quatrième réaudit. `RB4-1` : `P2A-11` valait **`4,000 s`**, **sous le régime observé de `4,682 s`** — un cycle nominal aurait été interprété comme le chemin d'échec de `F-12`, régression du type `P2A-3c`. Les deux garde-fous sont **refondus et découplés** : `P2A-11` devient un `ABORT` **ordinaire** d'allongement au budget **dérivé** de `5,000 s`, **faux positif assumé**, **sans alimenter `D-2` ni `P2A-5`** ; `P2A-12` devient la **détection du chemin d'échec** au seuil **choisi** de `10 s`, au-dessus du régime observé et neuf fois sous la signature de 90 s, et **lui seul** alimente `D-2`. **Aucune borne n'est dérivée de `W4-P1`.** `RB4-2` : le tableau du §6.1 est réparé — `P1`, `P2`, `P2 bis`, `P3`, `P4` contigus, note hors tableau. `RB4-3` : la séquence d'`ABORT` sous `P2A-2`/`P2A-3` devient `S1` → `S2` → `S7` → `S4` **restreint aux empreintes** → `O4`, `R2` ayant été omise ; `S3` interdit, `S5`, `S6`, `S8` sans objet. `C-8` formulation de `C-5` précisée. `C-9` état de `<unité-démon>` rétabli au préflight. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **6** | Après cinquième audit. `RB5-1` : la **précédence** entre `P2A-11` et `P2A-12` est réglée au §8.1.1 — `P2A-12` **prévaut toujours** dès qu'il est atteint ; les relevés **`[5 s, 10 s)`** et **`≥ 10 s`** sont traités séparément, et l'état **terminé ou en cours** de l'invocation commande la conduite. **Une seule attente demeure permise** — invocation close entre 5 et 10 s — et elle reste sous surveillance préemptable. **Règle absolue posée : aucune attente volontaire à travers les 90 s du chemin de `F-12`.** `RB5-2` : la mention résiduelle de *« fraction choisie »* pour `P2A-11` est retirée — **`5,000 s` est dérivé de bout en bout**, et n'est soumis nulle part. `C-10` ordre du §9 rétabli. `C-11` sort de `R3`, `R4` et `R6` explicité comme **sans objet** sous `P2A-2`/`P2A-3`. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **7** | Après sixième audit. `RB6-1` : `O2`, acte de la seule phase 2, est **étendu à la phase 3** pendant toute attente d'un retour synchronisé `S1` — la surveillance et la préemption du §8.1.1 étaient jusque-là **prescrites sans acte permettant de les observer**. L'extension est bornée par son objet, sa fréquence inchangée et **deux termes nommés** : exécution effective du retour, ou préemption par `P2A-12`. **Aucune autre extension de périmètre.** `C-12` : la ligne vive de `P2A-11` au §8.1 annonçait un retour synchronisé sans réserve — alignée sur le §8.1.1, invocation **en cours** valant retour **non** synchronisé. `C-13` : le cas `[5 s, 10 s)` **en cours** est tranché — retour **toujours** immédiat, `STOP` dû **si et seulement si** le chemin d'échec est confirmé, **le doute valant confirmation**. **Aucune exécution, aucune mutation, aucune autorisation.** |
| **8** | **Lot correctif, après une exécution terrain ABORTÉE.** La V7, autorisée et exécutée, s'est arrêtée à `P2A-6` **188 s après l'ouverture de la fenêtre** : le pont avait redémarré à l'instant même du redémarrage du démon. Le fait **`F-13`** — la directive `Requires=` du pont visant le démon — est ajouté, et le §3.0 consigne que l'exclusion que la V7 se donnait était **inatteignable par construction**, non par accident. **`P2A-6` est remplacée** : la propagation attendue, définie par **cinq conditions cumulatives** au §8.1.2, cesse d'être un `ABORT` ; **tout autre redémarrage, tout redémarrage supplémentaire, toute origine inconnue, tout comportement non nominal le demeurent**. **`D-1` est qualifié** pour ne pas prendre la propagation du lot pour le chemin de `F-12`. Le périmètre du §4 et le `STOP` du §8.2 sont mis en accord avec l'arbitrage. **`R5.e`** exige que les redémarrages du pont soient **comptés et attribués** — la règle de comptage qu'elle posait alors, *« autant que de redémarrages du démon commandés »*, a été **REMPLACÉE en V13/V14** par le **nombre de propagations qualifiées** (§7, §7.1), afin que le cas « zéro propagation » demeure satisfaisant. La piste de neutralisation de la dépendance est **exclue par arbitrage**. **Aucun autre changement de conception. Aucune exécution, aucune nouvelle autorisation terrain.** |
| **9** | Après audit du correctif. `RB7-1` : les cinq conditions n'avaient **aucun acte pour les vérifier** — **`M5 bis`** et **`S3 bis`** sont ajoutés à la liste close, en lecture seule. `RB7-2` : la condition « unique » n'était **pas observable** à 15 s d'échantillonnage — le canal devient le **journal du pont, lu rétrospectivement**, qui porte toutes les transitions et leurs identifiants d'invocation ; **`NRestarts` cesse d'être un compteur** ; `R5.e` est portée par des actes explicites. `RB7-3` : l'attribution devient **causale** et non plus temporelle — §8.1.2.1, par l'**inactivité constatée** du superviseur, qui rend son action **impossible** —, « nominal » reçoit une **définition close** et une **fenêtre** au §8.1.2.3, et **`D-1` demeure confirmateur du `STOP` en cas de doute**. `RB7-4` : nouveau §8.1.3 — conduite pendant la **qualification différée**, `O2` étendu, **`D-2` / `P2A-12` préemptifs**, **aucune attente à travers les 90 s**, et une qualification **non acquise ou douteuse** vaut **`ABORT` ET `STOP`**. `C-14` à `C-17` : `NRestarts` requalifié en observation terrain, `P2A-5` aligné sur l'exception admise, ordre des sous-sections et du §9 rétabli, renvois et repères corrigés. **Aucun autre changement de conception. Aucune exécution, aucune nouvelle autorisation terrain.** |
| **10** | Après réaudit. `RB8-1` : §6.3.1 disait *« phase 3 et elle seule »* alors qu'il étendait déjà `O2` à la **phase 1** — titre et clauses mis en accord, appartenance à la liste close rendue explicite. `RB8-2` : *« `O2` seulement »* **interdisait `M6` et `S4`…`S8`** — le lot se bloquait lui-même ; la règle porte désormais sur la **liste close**, non sur la phase. `RB8-3` : le cas **zéro redémarrage** est écrit — **aucune qualification, aucun `ABORT`, poursuite normale**. `RB8-4` : **la brèche du tiers acteur est fermée** — l'attribution devient **positive**, la transition du démon devant être **strictement encadrée** par celle du pont ; **à défaut de pouvoir l'établir, la propagation demeure NON QUALIFIÉE**. `RB8-5` et `RB8-7` : nouvel acte **`S9`**, lecture rétrospective **complète** du journal du pont, **due y compris après `ABORT` ou préemption**. `RB8-6` : l'unité comptée devient le **nouvel identifiant d'invocation relativement au baseline**, jamais « tous les distincts » ; §8.1.2.2 et `R5.e` alignés. `RB8-8` : §8.3.2 — `D-1` s'appuie **aussi** sur le journal du pont, le mot *« seule »* est retiré. `C-18` à `C-21` : statut de `R5.e` sous `P2A-2`/`P2A-3`, §9 point 4 aligné, renvoi `§3.0`, `M5 bis` replacé entre `M5` et `M6`. **Aucun autre changement de conception. Aucune exécution, aucune nouvelle autorisation terrain.** |
| **11** | Après réaudit. `RB9-1` : les offices de **`M5 bis` / `S3 bis`** — **qualifier localement** — et de **`S9`** — **dénombrer globalement** — sont séparés ; **`S9` n'attribue jamais rétrospectivement**, et **tout redémarrage dénombré non qualifié au moment utile fait ÉCHOUER `R5.e`**. `RB9-2` : **`S9` est inséré à son rang** dans la séquence close de `P2A-2` / `P2A-3`, avec les preuves associées. `RB9-3` : **`(c)` devient mesurable** — `M5` et `S3` relèvent l'**instant exact de la commande**, `M6` et `S3` l'**identifiant d'invocation du démon**, et le **terme comparé** entre journal et propriétés d'unité est nommé. `RB9-4` : nouvel acte de préflight **`P5`** — **précondition d'observabilité**, en lecture seule et **avant toute mutation**, établissant la relation d'ordre configurée **et** la présence effective des quatre événements avec leurs identifiants ; à défaut, **`STOP AVANT MUTATION`** (§8.2.1), qui **n'est pas un `ABORT`** puisque **rien n'a été muté**. `C-22` à `C-26` : rang temporel de `S9`, condition 3 exprimée par rapport au baseline **et aux identifiants déjà dénombrés**, **élargissement implicite d'`O2` retiré**, §8.1.3 nommant `M5 bis` et `S3 bis`, et `(a)` énumérant **exactement** les mêmes événements que sa clause de repli. **Aucun autre changement de conception. Aucune exécution, aucune nouvelle autorisation terrain.** |
| **12** | Après réaudit. `RB10-1` : **`P5` portait sur la PRÉSENCE des quatre événements, pas sur leur ORDRE** — une installation les émettant dans le désordre aurait été déclarée `ÉTABLIE` puis aurait échoué à `(a)` **après la mutation** ; le critère porte désormais sur l'ordre, et **l'ordre non établi vaut `NON ÉTABLIE`**. `RB10-2` : nouvel acte **`P6`**, dans la liste close, qui **consigne le verdict de `P5`**, identifie le **redémarrage historique** employé et la **fenêtre de journal** lue. `RB10-3` : nouveau §7.1 — **trois verdicts explicites** pour `R5.e`, dont celui de l'**attribution abandonnée par préemption**, qui est **légitime** ; **aucun acte terrain nouveau, aucune nouvelle tentative**, et le rapport **MUST** dire si un `ABORT` était dû plus tôt. `RB10-4` : la note de `C-24` sortie du tableau du §8.3.2, qui redevient **continu**. `C-27` à `C-29` : décompte du §6.1 porté à **sept**, `S9` retiré de l'énumération du §8.1.3 qui s'arrête à `S8`, et l'assertion *« par construction »* du §8.1.2.1 **retirée** au profit du verdict de `P5`. **Aucun autre changement de conception. Aucune exécution, aucune nouvelle autorisation terrain.** |
| **13** | Après réaudit. `RB11-1` : la note de `C-28` sortie du tableau du §8.1.3, qui laissait une ligne **orpheline**. `RB11-2` : **§7.1 rendu exhaustif** sur les **trois composantes** de `R5.e` — compte, attribution, état du pont —, avec les verdicts **compte supérieur**, **compte inférieur** et **pont non nominal**, et le **compte attendu corrigé** : le nombre de **propagations qualifiées**, non celui des commandes, faute de quoi le cas **« zéro propagation »** admis nominalement aurait fait échouer `R5.e` sur un déroulement normal. `RB11-3` : **contradiction supprimée** — la séquence de `P2A-2` / `P2A-3` ne prescrit plus `P2A-6` automatiquement sur un échec de `R5.e`, puisqu'on y est **déjà** en `ABORT` ; la conduite renvoie au §7.1 et à la question de la détectabilité. `RB11-4` : **`P5` exige désormais les DEUX preuves** — **structurelle**, la relation configurée, et **historique**, l'ordre observé — **et leur CONCORDANCE** ; *« une observation historique seule ne suffit jamais »* ; `P6` consigne la relation configurée **et son moyen de preuve**. `C-30` à `C-32` : §8.2.1 nomme `P6`, §6.1 renommé pour couvrir lecture **et** consignation hors dépôt, et §7.1 reformulé pour valoir aussi dans la séquence spéciale. **Aucun autre changement de conception. Aucune exécution, aucune nouvelle autorisation terrain.** |
| **14** | Après réaudit. `RB12-1` : la **ligne vide** subsistant dans le tableau du §8.1.3 est supprimée — les deux lignes de conduite sont enfin **contiguës**. `RB12-2` : le §7 portait encore l'**ancienne règle de comptage** que le §7.1 avait corrigée — la définition normative **contredisait** sa propre conduite d'évaluation ; les deux sont désormais **alignées mot pour mot**, et le cas **« zéro propagation » est explicitement satisfaisant**. `RB12-3` : le **dernier `donc P2A-6`** est retiré du tableau du sort des preuves de `P2A-2` / `P2A-3` ; **tout renvoie à la conduite unique du §7.1**. `RB12-4` : nouveau §7.1.1 — les identifiants excédentaires sont **triés un par un**, et **`REDÉMARRAGE NON ATTRIBUÉ` est réservé** à ceux que **nulle préemption n'explique** ; l'employer ailleurs *« reviendrait à imputer au lot une anomalie dont sa propre règle de sûreté est la cause »*. `C-33` : l'historique de la V8 marque désormais son ancienne règle de comptage comme **remplacée**. **Aucun autre changement de conception. Aucune exécution, aucune nouvelle autorisation terrain.** |
