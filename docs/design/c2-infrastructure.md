# C2 — Infrastructure de test et doubles

Document interne de conception. Il decrit les frontieres techniques introduites
par le lot C2 et les decisions volontairement reportees.

> Doctrine : les doubles simulent les frontieres techniques, ils ne
> reimplementent pas le futur produit.

C2 ne contient aucun coeur transactionnel, aucun transport reel, aucun contact
avec la production. Il livre des interfaces etroites et des doubles deterministes
qui permettront, en C3, de developper le coeur sans chaudiere, sans `vcontrold`
reel, sans broker, sans reseau et sans attente reelle.

## Frontieres et responsabilites

| Element | Fichier | Responsabilite exacte |
|---|---|---|
| `Clock` (protocole) | `clock.py` | Trois primitives temporelles : `now()` UTC aware, `monotonic()` pour les budgets, `sleep()`. Rien d'autre. |
| `SystemClock` | `clock.py` | Implementation reelle (production). Delegue a la stdlib, aucune logique metier. |
| `VirtualClock` | `testing/fake_clock.py` | Horloge pilotee par le test. UTC et monotone avancent ensemble ; `sleep` n'attend jamais. |
| `VClient` (protocole) | `transport/vclient.py` | Lire / ecrire une valeur via `vcontrold`. Issues typees par `TransportStatus`. |
| `ReadResult` / `WriteResult` | `transport/vclient.py` | Resultats immuables ; le « pourquoi » est toujours dans `status`, jamais absorbe dans un `None`. |
| `MqttClient` (protocole) | `transport/mqtt.py` | Frontiere publier / souscrire / (de)connecter. Aucune politique. |
| `Message` / `Publication` / `PublishHandle` | `transport/mqtt.py` | Payload en octets bruts ; drapeau `dup` represente ; publication demandee vs confirmee vs echouee. |
| `FakeVClient` | `testing/fake_vclient.py` | Double programmable et strict du transport `vcontrold`. |
| `FakeMqttClient` | `testing/fake_mqtt.py` | Double en memoire du transport MQTT. |
| `BoundedQueue` | `bounded_queue.py` | File FIFO bornee, rejet explicite a la saturation. Structure de donnees, pas ordonnanceur. |

## Choix structurants

- **Les issues de transport sont des donnees, pas des exceptions.** Le futur
  coeur devra brancher sur `timeout`, `daemon_unreachable`, etc. pour decider
  d'une politique ; ce sont donc des valeurs (`TransportStatus`) portees par des
  resultats, pas des exceptions a rattraper dans le flux normal. Les exceptions
  sont reservees aux erreurs de programmation (appel inattendu du faux,
  publication sans connexion, file pleine).
- **Aucune sentinelle ambigue.** `None` sur `ReadResult.value` signifie
  uniquement « pas de valeur numerique » ; la cause est dans `status`.
- **Le temps est injecte.** La latence d'un faux `vclient` fait avancer la
  `VirtualClock` ; aucun test n'attend reellement. Une operation « bloquee
  jusqu'au depassement d'un budget » se programme en `TIMEOUT` avec une latence
  superieure au budget.
- **`testing/` est interne.** Ce n'est pas une API publique garantie.

## Frontiere, pas politique

Ces interfaces disent ce que le coeur pourra faire, pas comment. Sont
explicitement HORS de C2 :

- validation des payloads MQTT, ACK, `request_id`, deduplication ;
- profils declaratifs, commandes reelles de chaudiere ;
- reconnexion exponentielle, politique de retry, budgets concrets ;
- Paho, sous-processus, reseau, session MQTT complete.

## Decisions decouvertes mais NON prises

Reportees a C3, volontairement non tranchees ici :

1. **Signature d'ecriture.** `write(command, value: float)` suppose une valeur
   numerique unique. Certaines commandes pourraient exiger d'autres formes
   d'arguments ; non tranche.
2. **Typage du payload MQTT.** Choisi en `bytes` (payload brut). Le point de
   conversion texte/octets et l'encodage restent a decider avec la serialisation
   metier, en C3.
3. **Modele de confirmation MQTT.** `PublishHandle` distingue demandee /
   confirmee / echouee, mais la correspondance avec les QoS 0/1/2 et le PUBACK
   reel n'est pas modelisee.
4. **Semantique de `monotonic_start`.** Fixee librement par le test ; aucune
   relation avec `now()` n'est imposee, ce qui est correct pour un compteur dont
   seuls les ecarts ont un sens.
5. **Place de `BoundedQueue`.** Primitive generique posee hors de `_legacy` et de
   `testing` ; son integration au coeur (worker, backpressure) appartient a C3.
