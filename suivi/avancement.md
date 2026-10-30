# Avancement du projet

Mis à jour à chaque séance. Le détail des choix est dans le [journal de décisions](journal-decisions.md).

Membres et rôles : [note de cadrage](note-cadrage.md), section 7.

## Vue d'ensemble

| Jalon | Contenu | État |
|---|---|---|
| J1 | Cadrage : terrain, parc, incidents, fausse alerte, risques | Fait (29/10) — rôles et réponses de l'enseignant à compléter |
| J2 | Simulateur, pseudonymisation, base documentaire, tests, dataset | Fait (30/10) |
| J3 | Détection : règles, dérive, Isolation Forest + mesures | Fait (30/10) |
| J4 | RAG + LLM + validation humaine + évaluation complète | Fait (30/10) — note humaine des tests à faire |
| Interface | Page web locale de la démo | Faite (30/10) |
| Final | Rapport, démo de 5 min | À faire |

## Exigences du sujet

| Exigence | Où | État |
|---|---|---|
| Base documentaire (≥ 5 fichiers) | `docs_rt/` (RT-01 à RT-08) | Fait |
| Données propres et anonymisées | `simulateur/`, `scripts/pseudo.py` | Fait |
| Dataset JSONL | `datasets/instructions-copilote.jsonl` (12 exemples) | Fait |
| Grille de tests (≥ 8) | `evaluation/cas-tests.jsonl` (20 cas) | Exécutée : 14/20 (score auto), note humaine à faire |
| Détection simple | `scripts/detecter.py`, `scripts/detection/` | Fait |
| Recherche / RAG | `scripts/rag.py`, `rag/` | Fait |
| Prompt système sécurisé, réponses sourcées, refus | `scripts/expliquer.py` | Fait |
| Rapport d'incident court | `scripts/copilote.py` → `reports/incidents/` | Fait |
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

## J4 — ce qui est fait (30/10, Florian)

Résultats : [reports/tests-j4.md](../reports/tests-j4.md). LLM `llama3.2:3b` sur le PC de Florian, environ 5 s par réponse.

- **RAG** : 8 documents découpés en 20 passages ; le bon runbook est retrouvé en tête dans 4 requêtes de test sur 5.
- **Contrôles par le code** : source inventée → réponse bloquée ; action hors liste blanche → ignorée et notée dans le journal ; données des capteurs entre balises ; passages et questions pseudonymisés (0 identifiant réel envoyé au LLM).
- **Chaîne** : `copilote.py` explique chaque alerte, l'opérateur valide ou refuse, tout va dans `logs/decisions.jsonl`, rapport de 6 lignes dans `reports/incidents/`.
- **Tests** : 14/20 au score automatique. À la relecture, le score se trompe dans les deux sens : BAT-01 est un bon refus compté en échec ; DEF-01 et DEF-02 sont comptés réussis mais le modèle se trompe sur les nombres.
- **Limite à mettre dans le rapport** : le modèle 3B raisonne mal sur les chiffres et confond parfois défaillant et dérive. C'est pour ça que le code fixe le type et l'action, et que le LLM ne fait qu'expliquer.

## Interface web et démo

`interface/app.py` (Streamlit, locale) : onglets **Parc**, **Alertes** (avec explication du copilote et boutons Valider / Refuser, en dry-run), **Décisions**, **Attaque en direct** et **Mesures et tests**.

Déroulé prévu de la démo (5 min) : capteur figé → dérive → clone → rejeu de tampon (« probablement normal ») → attaque refusée → mesures et limite (dérive vue après 2 jours).

## Tâches restantes, par rôle

Qui tient quel rôle : [note de cadrage](note-cadrage.md), section 7. Chacun relit le code et les résultats de son rôle pour savoir les expliquer à l'oral ; personne n'a à les réécrire.

| Rôle | Tâches | Partie du rapport | Dans la démo |
|---|---|---|---|
| Intégration | Installer et tester le projet sur la VM du TP0 ; remesurer la latence (passer à `llama3.2:1b` si la VM manque de mémoire) ; noter les réponses de l'enseignant dans le journal ; vérification finale la veille | Architecture, chaîne complète, installation | Pilote la page web |
| Données | Relire le simulateur (`simulateur/`) ; faire le schéma du parc (bâtiments, zones, passerelles) | Problème et terrain : parc simulé, incidents, rejeu de tampon | Parc et capteur figé |
| Modèles | Relire la détection (`scripts/detection/`) et [mesures-j3.md](../reports/mesures-j3.md) ; savoir justifier règles, CUSUM et Isolation Forest | Choix et justification des modèles, résultats de la détection, limites | Dérive et clone |
| Sécurité & évaluation | Note humaine des 20 réponses (colonne `note_humaine_20` de `reports/tests-j4.csv`), dont au moins 5 justifiées : 2 bonnes, 2 insuffisantes, 1 dangereuse ou ambiguë (à partager à 5 tests chacun si besoin) ; relire les 5 règles et leurs parades | Sécurité, tests du copilote, limites du LLM 3B | Rejeu de tampon et attaque en direct |

**Ensemble** :

- Répartir les rôles et poser les questions du point jalon à l'enseignant ([journal-decisions.md](journal-decisions.md)).
- Relire le rapport (4 à 6 pages) : chacun relit les parties des autres.
- Répéter la démo, chronomètre en main (environ 1 min 15 par personne) ; enregistrer une vidéo comme plan B.
- La veille, sur la machine de la démo : régénérer les données, lancer `verifier_j2.py`, `mesures.py` et `tests_copilote.py`, vérifier que GitHub est à jour, « réchauffer » le LLM.

**Ordre conseillé** : rôles et questions à l'enseignant → VM et note humaine en parallèle → rapport → répétition et vérification finale.
