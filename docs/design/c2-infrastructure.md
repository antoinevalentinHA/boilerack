# C2 — Infrastructure de test et doubles

Document interne de conception. Il décrit les frontières techniques introduites
par le lot C2 et les décisions volontairement reportées.

> Doctrine : les doubles simulent les frontières techniques, ils ne
> réimplémentent pas le futur produit.

C2 ne contient aucun cœur transactionnel, aucun transport réel, aucun contact
avec la production. Il livre des interfaces étroites et des doubles déterministes
qui permettront, en C3, de développer le cœur sans chaudière, sans `vcontrold`
réel, sans broker, sans réseau et sans attente réelle.

## Frontières et responsabilités

| Élément | Fichier | Responsabilité exacte |
|---|---|---|
| `Clock` (protocole) | `clock.py` | Trois primitives temporelles : `now()` UTC aware, `monotonic()` pour les budgets, `sleep()`. Rien d'autre. |
| `SystemClock` | `clock.py` | Implémentation réelle (production). Délègue à la stdlib, aucune logique métier. |
| `VirtualClock` | `testing/fake_clock.py` | Horloge pilotée par le test. UTC et monotone avancent ensemble ; `sleep` n'attend jamais. |
| `VClient` (protocole) | `transport/vclient.py` | Lire / écrire une valeur via `vcontrold`. Issues typées par `TransportStatus`. |
| `ReadResult` / `WriteResult` | `transport/vclient.py` | Résultats immuables ; le « pourquoi » est toujours dans `status`, jamais absorbé dans un `None`. |
| `MqttClient` (protocole) | `transport/mqtt.py` | Frontière publier / souscrire / (de)connecter. Aucune politique. |
| `Message` / `Publication` / `PublishHandle` | `transport/mqtt.py` | Payload en octets bruts ; drapeau `dup` représenté ; publication demandée vs confirmée vs échouée. |
| `FakeVClient` | `testing/fake_vclient.py` | Double programmable et strict du transport `vcontrold`. |
| `FakeMqttClient` | `testing/fake_mqtt.py` | Double en mémoire du transport MQTT. |
| `BoundedQueue` | `bounded_queue.py` | File FIFO bornée, rejet explicite à la saturation. Structure de données, pas ordonnanceur. |

## Choix structurants

- **Les issues de transport sont des données, pas des exceptions.** Le futur
  cœur devra brancher sur `timeout`, `daemon_unreachable`, etc. pour décider
  d'une politique ; ce sont donc des valeurs (`TransportStatus`) portées par des
  résultats, pas des exceptions à rattraper dans le flux normal. Les exceptions
  sont réservées aux erreurs de programmation (appel inattendu du faux,
  publication sans connexion, file pleine).
- **Aucune sentinelle ambiguë.** `None` sur `ReadResult.value` signifie
  uniquement « pas de valeur numérique » ; la cause est dans `status`.
- **Le temps est injecté.** La latence d'un faux `vclient` fait avancer la
  `VirtualClock` ; aucun test n'attend réellement. Une opération « bloquée
  jusqu'au dépassement d'un budget » se programme en `TIMEOUT` avec une latence
  supérieure au budget.
- **`testing/` est interne.** Ce n'est pas une API publique garantie.

## Frontière, pas politique

Ces interfaces disent ce que le cœur pourra faire, pas comment. Sont
explicitement HORS de C2 :

- validation des payloads MQTT, ACK, `request_id`, déduplication ;
- profils déclaratifs, commandes réelles de chaudière ;
- reconnexion exponentielle, politique de retry, budgets concrets ;
- Paho, sous-processus, réseau, session MQTT complète.

## Décisions découvertes mais NON prises

Reportées à C3, volontairement non tranchées ici :

1. **Signature d'écriture.** `write(command, value: float)` suppose une valeur
   numérique unique. Certaines commandes pourraient exiger d'autres formes
   d'arguments ; non tranché.
2. **Typage du payload MQTT.** Choisi en `bytes` (payload brut). Le point de
   conversion texte/octets et l'encodage restent à décider avec la sérialisation
   métier, en C3.
3. **Modèle de confirmation MQTT.** `PublishHandle` distingue demandée /
   confirmée / échouée, mais la correspondance avec les QoS 0/1/2 et le PUBACK
   réel n'est pas modélisée.
4. **Sémantique de `monotonic_start`.** Fixée librement par le test ; aucune
   relation avec `now()` n'est imposée, ce qui est correct pour un compteur dont
   seuls les écarts ont un sens.
5. **Place de `BoundedQueue`.** Primitive générique posée hors de `_legacy` et de
   `testing` ; son intégration au cœur (worker, backpressure) appartient à C3.
