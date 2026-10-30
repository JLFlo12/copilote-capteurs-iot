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
python scripts/detecter.py       # alertes dans logs/alertes.json
python evaluation/mesures.py     # résultats dans reports/mesures-j3.md
python scripts/rag.py indexer    # base du RAG (Ollama lancé)
python scripts/copilote.py --max 3   # copilote en terminal, validation humaine
python evaluation/tests_copilote.py  # 20 tests, résultats dans reports/tests-j4.md
streamlit run interface/app.py   # page web locale : http://localhost:8501
```

## Démo

La veille : régénérer les données et relancer `evaluation/tests_copilote.py` (commandes ci-dessus).

Projet dans une VM VirtualBox (NAT) avec Ollama sur l'hôte (GPU) : mettre `OLLAMA_HOST=http://10.0.2.2:11434` dans `.env`.
Streamlit n'écoute que sur `localhost` ; depuis l'hôte, passer par un tunnel SSH puis ouvrir http://localhost:8501.

```bash
streamlit run interface/app.py                           # dans la VM
ssh -N -L 8501:localhost:8501 -p 2222 <user>@127.0.0.1   # sur l'hôte (redirection NAT 2222 → 22)
```

Avant de commencer : attendre la fin de la détection (environ 15 s), puis demander l'explication d'une alerte qui ne sera pas montrée (CAPT-018) pour charger le modèle.

Déroulé (6 min) :

| Onglet | À montrer | Exigence du sujet |
|---|---|---|
| Parc | État par zone, CAPT-007 face à ses voisins | Données du terrain (simulées) |
| Alertes | CAPT-012 (valeur figée) : explication, source RT-02, **Valider** | Incident jusqu'à une action validée par un humain |
| Alertes | CAPT-007 (dérive) et CAPT-031 (clone) : **Refuser** l'une des deux | Le code décide, l'humain peut refuser |
| Alertes | Rejeu de tampon GW-B (« probablement normal ») | Fausse alerte |
| Attaque en direct | « Injection cachée dans le nom de zone », puis « Source inventée » | Injection déjouée ; le copilote dit qu'il ne sait pas |
| Décisions | Journal : validée / refusée, jamais exécutée (dry-run) | Traçabilité |
| Mesures et tests | Détection, attaques, 20 tests | Ce qu'il détecte, rate et déclenche à tort |

Si Ollama ne répond pas, la page affiche quand même la détection : relancer Ollama puis recharger la page.

## Équipe

Florian, Lallie, Mathis et Matthias. Les rôles sont dans la [note de cadrage](suivi/note-cadrage.md), section 7.
