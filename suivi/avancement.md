# Avancement du projet

Mis à jour à chaque séance. Le détail des choix est dans le [journal de décisions](journal-decisions.md).

Membres et rôles : [note de cadrage](note-cadrage.md), section 7.

## Vue d'ensemble

| Jalon | Contenu | État |
|---|---|---|
| J1 | Cadrage : terrain, parc, incidents, fausse alerte, risques | Fait (29/10) — rôles et réponses de l'enseignant à compléter |
| J2 | Simulateur, pseudonymisation, base documentaire, tests, dataset | Fait (30/10) |
| J3 | Détection : règles, dérive, Isolation Forest + mesures | Fait (30/10) |
| J4 | RAG + LLM + validation humaine + évaluation complète | À faire |
| Interface | Page web locale de la démo | Commencée (30/10) : Parc, Alertes, Mesures |
| Final | Rapport, démo de 5 min | À faire |

## Exigences du sujet

| Exigence | Où | État |
|---|---|---|
| Base documentaire (≥ 5 fichiers) | `docs_rt/` (RT-01 à RT-07) | Fait |
| Données propres et anonymisées | `simulateur/`, `scripts/pseudo.py` | Fait |
| Dataset JSONL | `datasets/instructions-copilote.jsonl` (12 exemples) | Fait |
| Grille de tests (≥ 8) | `evaluation/cas-tests.jsonl` (20 cas) | Écrite, pas encore exécutée |
| Détection simple | `scripts/detecter.py`, `scripts/detection/` | Fait |
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

Voir la section « Démarrage » du [README](../README.fr.md).

## J3 — ce qui est fait (30/10, Florian)

Résultats complets : [reports/mesures-j3.md](../reports/mesures-j3.md).

| Type | Précision | Rappel |
|---|---|---|
| Défaillant | 100 % | 100 % (+ silence de CAPT-036 signalé) |
| Dérive | 100 % | 81 % (détectée 1,8 à 1,9 jour après son début) |
| Clone | 100 % | 100 % |
| Rejeu de tampon (info) | 100 % | 100 % ; 0 classé en incident |

- 0 trame normale classée en incident. 19 alertes au total, dont 11 « inhabituel » (niveau mineur) venant de l'Isolation Forest.
- Attaques déjouées : fausse coupure (5/5 classées clone), rejeu malveillant (12/12).
- Limite à dire dans le rapport : la dérive n'est vue qu'après environ 2 jours, le temps que l'écart dépasse le bruit.

## Prochaine étape : J4

Le copilote : RAG sur `docs_rt/`, explication par le LLM local, contrôle des sources et de la liste blanche, validation humaine, puis exécution des 20 cas de test. Détail : [guide technique](../guides/guide-technique.md), étapes 3 à 7.

## Interface web et démo

`interface/app.py` (Streamlit, locale) : onglets **Parc**, **Alertes** et **Mesures et tests** faits. En J4, on ajoute l'explication du LLM avec ses sources, les boutons Valider / Refuser (dry-run), un onglet **Décisions** et un onglet **Attaque en direct**.

Déroulé prévu de la démo (5 min) : capteur figé → dérive → clone → rejeu de tampon (« probablement normal ») → attaque refusée → mesures et limite (dérive vue après 2 jours).

Vérification finale, la veille, sur la machine de la démo : régénérer les données, lancer `verifier_j2.py` et `mesures.py`, puis les 20 tests du copilote ; répétition chronométrée ; « réchauffer » le LLM avant de commencer ; plan B : enregistrement vidéo et résultats déjà dans `reports/`.

## En attente

- Répartition des 4 rôles entre les membres ([note-cadrage.md](note-cadrage.md), section 7).
- Réponses de l'enseignant aux questions du point jalon ([journal-decisions.md](journal-decisions.md)).
