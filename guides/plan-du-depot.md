# Plan du dépôt — à quoi sert chaque fichier

Ce guide présente le dépôt fichier par fichier. Pour savoir où en est le projet, ouvrir [suivi/avancement.md](../suivi/avancement.md).

Les fichiers marqués *(à venir)* sont prévus mais pas encore écrits. Les fichiers marqués *(généré)* sont produits par un script et ne sont pas commités : on les recrée avec les commandes du README.

## Racine

| Fichier | Utilité |
|---|---|
| `README.md` / `README.fr.md` | Présentation du projet (anglais / français) : but, règles, chaîne, démarrage. |
| `requirements.txt` | Bibliothèques Python à installer (`pip install -r requirements.txt`). |
| `.env.example` | Modèle de configuration : clé de pseudonymisation, modèle Ollama, `DRY_RUN`. À copier en `.env`. |
| `.env` | La vraie configuration, avec la clé secrète. **Jamais commité** (ignoré par Git). |
| `.gitignore` | Ce que Git ignore : `.env`, `.venv/`, les CSV générés, les caches Python. |

## `suivi/` — le pilotage du projet

| Fichier | Utilité |
|---|---|
| `avancement.md` | **À ouvrir en premier.** État de chaque jalon, exigences du sujet, prochaine étape, points en attente. |
| `note-cadrage.md` | Livrable J1 : terrain, parc simulé, incidents, fausse alerte, choix d'IA, risques, rôles. La référence pour les chiffres du parc. |
| `journal-decisions.md` | Chaque décision avec sa date, sa raison et ce qu'on a écarté. Questions pour l'enseignant en bas. |

## `guides/` — l'aide pour travailler

| Fichier | Utilité |
|---|---|
| `guide-technique.md` | Les 8 étapes à coder, dans l'ordre, avec les outils et les fichiers de chaque étape. |
| `guide-seance-1-cadrage.md` | Déroulé de la séance J1 (cadrage). Utile pour comprendre comment la note de cadrage a été construite. |
| `plan-du-depot.md` | Ce fichier. |

## `simulateur/` — fabriquer les données

| Fichier | Utilité |
|---|---|
| `generer_parc.py` | Génère le parc **normal** : 40 capteurs, 14 jours, une trame toutes les 5 min, graine fixe. Sortie : `logs/trames_normales.csv`. |
| `injecter_incidents.py` | Ajoute les incidents (défaillant, dérive, clone) et la fausse alerte (rejeu de tampon), avec la colonne `label`. Sortie : `logs/trames.csv`. |

## `interface/` — la page web de la démo

| Fichier | Utilité |
|---|---|
| `app.py` | Page web locale (Streamlit), le support de la démo. Onglets : **Parc** (état des capteurs, courbe face aux voisins), **Alertes** (preuves, sources, explication du copilote, Valider / Refuser), **Décisions** (journal), **Attaque en direct** (tenter une injection et voir les parades), **Mesures et tests**. Lancement : `streamlit run interface/app.py`. |

## `logs/` — les données produites

| Fichier | Utilité |
|---|---|
| `trames_normales.csv` *(généré)* | Le parc sans aucune anomalie. Étape intermédiaire. |
| `trames.csv` *(généré)* | Les trames complètes, incidents compris (≈ 161 000 lignes). C'est l'entrée de la détection. |
| `alertes.json` *(généré)* | Les alertes produites par la détection. C'est l'entrée du copilote (J4). |
| `decisions.jsonl` *(généré)* | Une ligne par validation ou refus de l'opérateur. |

## `scripts/` — le copilote

| Fichier | Utilité |
|---|---|
| `config.py` | Lit la configuration (`.env` ou variables d'environnement) : modèle Ollama, `DRY_RUN`, clé. |
| `pseudo.py` | Remplace les vrais identifiants (`CAPT-012`, `GW-B`, `BAT-A-E3`) par des pseudonymes avant tout envoi au LLM. |
| `detecter.py` | Lance les 3 détecteurs, fusionne leurs verdicts et écrit les alertes dans `logs/alertes.json`. |
| `detection/regles.py` | Règles : capteur figé, hors plage, silencieux ; clone ; rejeu de tampon (les 5 critères de RT-05). |
| `detection/derive.py` | Repère une dérive en comparant chaque capteur à ses voisins de zone. |
| `detection/iforest.py` | Isolation Forest : repère les trames inhabituelles qu'aucune règle ne couvre. |
| `rag.py` | Découpe `docs_rt/` en passages, calcule les embeddings (`rag.py indexer`) et retrouve les 3 passages les plus proches (`rag.py chercher "…"`). |
| `expliquer.py` | Demande au LLM d'expliquer une alerte ou de répondre à une question, puis le code contrôle : sources existantes (une source inventée bloque la réponse), actions de la liste blanche, injection. |
| `copilote.py` | La chaîne complète en terminal : chaque alerte est expliquée, l'opérateur valide ou refuse, la décision est journalisée et un rapport d'incident de 6 lignes est écrit. |

## `docs_rt/` — la base documentaire du RAG

Le copilote lit ces documents pour justifier ses réponses et les cite (RT-01, RT-02…). Ce sont des données du copilote, pas de la documentation du projet.

| Fichier | Utilité |
|---|---|
| `RT-01-fiche-terrain.md` | Description du parc : passerelles, zones, valeurs normales, identité d'un capteur. |
| `RT-02-runbook-defaillant.md` | Capteur figé, hors plage ou silencieux : diagnostic et action. |
| `RT-03-runbook-derive.md` | Dérive lente : comment la reconnaître, quoi faire. |
| `RT-04-procedure-reetalonnage.md` | Étapes du réétalonnage après une dérive. |
| `RT-05-runbook-rejeu-tampon.md` | La fausse alerte : les 5 critères d'un rejeu de tampon normal. |
| `RT-06-procedure-clone.md` | Capteur cloné ou rejeu malveillant : conduite à tenir. |
| `RT-07-liste-blanche-actions.md` | Les 5 seules actions que le copilote peut proposer, et ce qui est interdit. |
| `RT-08-regles-usage.md` | Rafales d'alertes, données interdites dans un dataset ou un prompt, validation humaine. |

## `datasets/` — les exemples de réponses

| Fichier | Utilité |
|---|---|
| `instructions-copilote.jsonl` | 12 exemples `instruction` / `input` / `output` (pseudonymisés) : le style de réponse attendu du copilote. Livrable du sujet. |

## `evaluation/` — vérifier que tout marche

| Fichier | Utilité |
|---|---|
| `verifier_j2.py` | 21 contrôles automatiques sur les données, la pseudonymisation, les documents, les tests et le dataset. |
| `cas-tests.jsonl` | 20 questions de test avec les mots attendus et interdits (diagnostic, fausse alerte, attaques). |
| `mesures.py` | Précision et rappel de la détection par type, objectifs, deux scénarios d'attaque. Écrit `reports/mesures-j3.md`. |
| `tests_copilote.py` | Lance les 20 cas sur le copilote, note automatiquement les réponses et écrit `reports/tests-j4.md` et `.csv` (colonne de note humaine à remplir). |

## Autres dossiers

| Dossier | Utilité |
|---|---|
| `rag/` | `embeddings.json` : les passages de `docs_rt/` et leurs embeddings *(généré)*. |
| `models/` | `iforest.joblib`, le modèle entraîné *(généré)*. |
| `reports/` | `mesures-j3.md` (détection), `tests-j4.md` et `.csv` (copilote), `incidents/` (rapports d'incident, générés) ; plus tard, le rapport final. |
