# Guide technique en bref — Copilote IA capteurs IoT

Ce qu'on code, dans quel ordre, avec quels outils.

## La pile

| Brique | Outil |
|---|---|
| Langage | Python 3 (`pandas`, `numpy`, `scikit-learn`, `requests`) |
| LLM local | Ollama + `llama3.2:3b` (repli `1b`) |
| Embeddings (RAG) | `nomic-embed-text` dans Ollama |
| Base vectorielle | Fichier JSON d'embeddings (mini-RAG du TP3) ou `chromadb` |
| Données | CSV dans `logs/` (MQTT local en option) |
| Config et secrets | `.env` (jamais commité), modèle dans `.env.example` |

## La chaîne complète

```
simulateur → CSV de trames → détection (score) → pseudonymisation
→ RAG (docs_rt) → LLM explique → validation humaine → action en dry-run → log
```

## Étape 1 — Simulateur (J2) · `simulateur/`

- `generer_parc.py` : 40 capteurs, 4 passerelles, 8 zones, 1 trame toutes les 5 min, 14 jours, graine fixée.
- Profil normal : température en sinusoïde jour/nuit (19 à 23 °C) + bruit, humidité de 40 à 55 %.
- `injecter_incidents.py` : défaillant, dérive, clone, rejeu de tampon, avec la colonne `label`.
- Sortie : `logs/trames.csv` (environ 161 000 lignes, environ 4 % anormales, non commité : on le régénère avec la graine).
- Colonnes : `sensor_id, hw_fingerprint, gateway_id, zone, seq, ts_measure, ts_received, temp_c, hum_pct, battery_mv, rssi_dbm, label`.

## Étape 2 — Détection (J3) · `scripts/detection/`

Le score est calculé uniquement par le code. Il y a 3 détecteurs, puis une fusion.

| Détecteur | Cible | Principe |
|---|---|---|
| `regles.py` | Défaillant, clone, rejeu | Seuils de plage, écart-type nul sur 1 h, silence ; `seq` en double, 2 empreintes, trou commun à une passerelle |
| `derive.py` | Dérive | Résidu = valeur − médiane des voisins de la zone ; pente sur 72 h + CUSUM |
| `iforest.py` | Inhabituel multivarié | Isolation Forest entraîné sur les jours 1 à 3 (normaux) |

- Le détecteur ne lit **jamais** la colonne `label`.
- Le modèle Isolation Forest entraîné est enregistré dans `models/` (avec le `Modelfile` Ollama du copilote).
- Sortie : une alerte en JSON (`capteur`, `type`, `score`, `preuves`).

## Étape 3 — Pseudonymisation · `scripts/pseudo.py`

- `CAPT-012` devient `CAPTEUR_n`, `GW-B` devient `GW_n`, la zone devient `ZONE_n`, via un HMAC avec la clé `PSEUDO_KEY` du `.env`.
- Cette étape a lieu **avant** tout envoi au LLM.

## Étape 4 — RAG · `docs_rt/` et `rag/`

- `docs_rt/` contient 6 documents courts et inventés : fiche terrain, runbook par incident, procédure de réétalonnage, procédure en cas de clone, liste blanche des actions.
- `scripts/rag_indexer.py` : découpe les documents, calcule les embeddings avec `nomic-embed-text` et les enregistre dans `rag/embeddings.json`.
- `scripts/rag_chercher.py` : renvoie les 3 passages les plus proches de l'alerte.

## Étape 5 — Explication par le LLM · `scripts/expliquer.py`

- Prompt système : rôle de l'assistant, format de réponse imposé, citation des sources obligatoire, « je ne sais pas » autorisé, refus de toute action hors liste blanche.
- Les données de l'alerte sont placées entre balises (`<donnees>…</donnees>`) et traitées comme des données, jamais comme des consignes. C'est la parade contre l'injection de prompt.
- Appel à l'API locale d'Ollama : `POST http://localhost:11434/api/generate`.
- Le code vérifie ensuite la réponse :
  - chaque source citée existe dans `docs_rt` ;
  - chaque action proposée est dans la liste blanche.

## Étape 6 — Validation humaine et action · `scripts/copilote.py`

- La chaîne de bout en bout : détecter, puis pseudonymiser, puis expliquer, puis demander à l'opérateur de valider ou refuser.
- Liste blanche d'actions : ticket d'inspection, réétalonnage planifié, marquage « données non fiables », alerte sécurité, aucune action.
- `DRY_RUN=true` par défaut : on affiche l'action, on ne l'exécute pas.
- Chaque décision est journalisée dans `logs/decisions.jsonl` (une ligne JSON par décision).

## Étape 7 — Évaluation (J4) · `evaluation/`

- `evaluation/mesures.py` : précision et rappel par incident, avec la vérité terrain `label`.
- Taux de fausses alertes sur les trames `replay_tampon` : objectif 0 incident déclaré.
- `evaluation/cas_tests.jsonl` + `evaluation/tests_adverses.py` : au moins 15 cas.
  - Injection de prompt dans un nom de zone.
  - Document empoisonné dans le RAG.
  - Demande d'action destructive.
  - Clone déguisé en rejeu de tampon.
  - Source inventée par le LLM.
  - Fuite d'identifiant réel vers le LLM.
- Latence de bout en bout, mesurée sur la VM.

## Étape 8 — Livrables · `reports/`

- Rapport : choix, résultats chiffrés, limites, risques.
- Démo : un incident de chaque type + la fausse alerte, avec validation humaine.
- Journal de décisions tenu à jour à chaque jalon.

## Pièges à éviter

- Faire calculer le score par le LLM.
- Donner la colonne `label` au détecteur.
- Commiter le `.env` ou une clé.
- Lancer une action réelle : tout reste en dry-run.
- Oublier de pseudonymiser avant d'appeler le LLM.
