# Avancement du projet

Mis à jour à chaque séance. Le détail des choix est dans [JOURNAL_DECISIONS.md](JOURNAL_DECISIONS.md).

## Vue d'ensemble

| Jalon | Contenu | État |
|---|---|---|
| J1 | Cadrage : terrain, parc, incidents, fausse alerte, risques | Fait (29/10) — rôles et réponses de l'enseignant à compléter |
| J2 | Simulateur, pseudonymisation, base documentaire, tests, dataset | Fait (30/10) |
| J3 | Détection : règles, dérive, Isolation Forest + mesures | À faire |
| J4 | RAG + LLM + validation humaine + évaluation complète | À faire |
| Final | Rapport, démo de 5 min | À faire |

## Exigences du sujet

| Exigence | Où | État |
|---|---|---|
| Base documentaire (≥ 5 fichiers) | `docs_rt/` (RT-01 à RT-07) | Fait |
| Données propres et anonymisées | `simulateur/`, `scripts/pseudo.py` | Fait |
| Dataset JSONL | `datasets/rt_instructions.jsonl` (12 exemples) | Fait |
| Grille de tests (≥ 8) | `evaluation/cas_tests.jsonl` (20 cas) | Écrite, pas encore exécutée |
| Détection simple | `scripts/detection/` | J3 |
| Recherche / RAG | `scripts/rag_*.py`, `rag/` | J4 |
| Prompt système sécurisé, réponses sourcées, refus | `scripts/expliquer.py` | J4 |
| Rapport d'incident court | `scripts/copilote.py` | J4 |
| Rapport technique, démo | `reports/` | Final |

## J2 — ce qui est fait (30/10, Florian)

- **Simulateur** : `generer_parc.py` (parc normal) puis `injecter_incidents.py` (incidents). 160 824 trames, 3,9 % anormales : dérive 5 751, clone 288, rejeu de tampon 150, défaillant 90.
- **Pseudonymisation** : HMAC avec `PSEUDO_KEY` (`.env`, non commité). `CAPT-012` → `CAPTEUR_xxxxxx`.
- **docs_rt** : fiche terrain, runbooks défaillant / dérive / rejeu de tampon, procédures réétalonnage / clone, liste blanche des actions.
- **Tests** : 20 cas (diagnostic, fausse alerte, injection, empoisonnement du RAG, hallucination, fuite…).
- **Vérification** : `evaluation/verifier_j2.py`, 21 contrôles, tous OK. Il a révélé un bug de format de date dans le CSV, corrigé.

## Reproduire

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Linux : .venv/bin/
cp .env.example .env        # puis mettre une vraie PSEUDO_KEY
python simulateur/generer_parc.py
python simulateur/injecter_incidents.py
python evaluation/verifier_j2.py
```

## Prochaine étape : J3

1. `scripts/detection/regles.py` : défaillant (figé, hors plage, silence), clone, rejeu de tampon (5 critères).
2. `scripts/detection/derive.py` : résidu par rapport aux voisins de zone, pente sur 72 h + CUSUM.
3. `scripts/detection/iforest.py` : Isolation Forest entraîné sur les jours 1 à 3.
4. `evaluation/mesures.py` : précision et rappel par incident ; 0 incident sur les rejeux de tampon.

## En attente

- Rôles de Mathis et Matthias (NOTE_CADRAGE.md, section 7).
- Réponses de l'enseignant aux questions du point jalon (JOURNAL_DECISIONS.md).
