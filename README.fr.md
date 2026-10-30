# Copilote IoT — copilote d'exploitation IA pour un parc de capteurs

[🇬🇧 English](README.md) · 🇫🇷 Français

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-LLM%20local-000000?logo=ollama&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-d%C3%A9tection%20d'anomalies-F7931E?logo=scikitlearn&logoColor=white)

Un copilote d'exploitation 100 % local qui trie les alertes d'un **parc de capteurs IoT simulé**. Il signale les capteurs défaillants, en dérive ou clonés, et reconnaît comme probablement normal un capteur qui rejoue son tampon après une coupure.

Règle de la direction : **l'IA propose, l'humain décide.**

Projet BUT3 R&T, ressource R5.IA.13 (IA appliquée), d'après le [projet « Copilote d'exploitation IA » de Kodetis](https://formation.kodetis.com/formation/ia/projet-copilote/).

## Ce qu'il détecte

| Cas | Signature | Action proposée |
|---|---|---|
| Capteur défaillant | Valeur figée, hors plage, silence | Ticket d'inspection sur site |
| Dérive | Écart croissant avec la médiane des voisins | Planifier un réétalonnage |
| Capteur cloné | `seq` en double avec des valeurs différentes, deux empreintes matérielles | Marquer les données non fiables, alerte sécurité |
| **Fausse alerte :** rejeu de tampon | `seq` consécutifs, `ts_measure` qui comblent le trou de réception, même empreinte | Aucune (niveau info) ; la coupure est notée comme événement d'exploitation |

## Règles non négociables

1. Aucune donnée réelle : tout le parc est simulé.
2. Aucun secret dans le dépôt, les prompts ou les données : variables d'environnement (`.env`).
3. Aucune API cloud pour l'inférence.
4. Aucune action destructive proposée ou exécutée par l'IA.
5. Dry-run par défaut : rien ne s'exécute sans validation humaine.

## Chaîne

Trames simulées → variables → détection (règles + Isolation Forest) → tri des fausses alertes → pseudonymisation → LLM local + RAG → contrôle de sortie (JSON, sources, liste blanche) → **validation humaine** → journal JSONL des décisions.

## Arborescence

```text
copilote-capteurs-iot/
├── suivi/        # avancement, note de cadrage, journal de décisions
├── guides/       # guides du projet (technique, séances)
├── simulateur/   # simulateur du parc (graine fixée)
├── logs/         # trames générées (non commitées) et validations de l'opérateur
├── docs_rt/      # documents du RAG : fiche terrain, runbooks, actions autorisées
├── datasets/     # JSONL instruction/réponse
├── rag/          # chunks et embeddings (générés)
├── models/       # Modelfile Ollama, modèle Isolation Forest entraîné
├── scripts/      # détection, chaîne, validation
├── evaluation/   # cas de test (JSONL) et grille de notation
└── reports/      # rapports d'incident et résultats des tests (générés)
```

## Documentation

- [Plan du dépôt](guides/plan-du-depot.md) : à quoi sert chaque fichier.
- [Guide technique en bref](guides/guide-technique.md) : les 8 étapes à coder, outils et fichiers.
- [Guide de la séance 1](guides/guide-seance-1-cadrage.md) : cadrage J1, déroulé minute par minute.
- **[Avancement](suivi/avancement.md)** : où en est le projet, à ouvrir en premier.
- [Note de cadrage](suivi/note-cadrage.md) et [journal de décisions](suivi/journal-decisions.md).

## Démarrage

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # puis renseigner PSEUDO_KEY
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Générer les données et vérifier J2 :

```bash
python simulateur/generer_parc.py
python simulateur/injecter_incidents.py
python evaluation/verifier_j2.py
```

Les commandes de détection et de démo seront ajoutées aux jalons suivants.

## Équipe

Florian, Lallie, Mathis et Matthias. Les rôles sont dans la [note de cadrage](suivi/note-cadrage.md), section 7.
