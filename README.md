# Copilote IoT — AI operations copilot for a sensor fleet

🇬🇧 English · [🇫🇷 Français](README.fr.md)

![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local%20LLM-000000?logo=ollama&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-anomaly%20detection-F7931E?logo=scikitlearn&logoColor=white)

A 100 % local operations copilot that triages alerts from a **simulated IoT sensor fleet**. It flags faulty, drifting and cloned sensors, and recognises a sensor that replays its buffer after an outage as probably normal.

Rule set by management: **the AI proposes, the human decides.**

BUT3 R&T project, module R5.IA.13 (applied AI), based on the [Kodetis "Copilote d'exploitation IA" project](https://formation.kodetis.com/formation/ia/projet-copilote/).

## What it detects

| Case | Signature | Proposed action |
|---|---|---|
| Faulty sensor | Stuck value, out-of-range value, silence | Open an on-site inspection ticket |
| Drift | Growing gap with the median of neighbouring sensors | Schedule a recalibration |
| Cloned sensor | Duplicate `seq` with different values, two hardware fingerprints | Mark data as unreliable, open a security alert |
| **False alarm:** buffer replay | Consecutive `seq`, `ts_measure` filling the reception gap, same fingerprint | None (info level); the outage is logged as an operations event |

## Non-negotiable rules

1. No real data: the whole fleet is simulated.
2. No secrets in the repo, prompts or data: use environment variables (`.env`).
3. No cloud API for inference.
4. No destructive action proposed or executed by the AI.
5. Dry-run by default: nothing runs without human approval.

## Pipeline

Simulated frames → features → detection (rules + Isolation Forest) → false-alarm triage → pseudonymisation → local LLM + RAG → output check (JSON, sources, allow-list) → **human validation** → JSONL decision log.

## Repository layout

```text
copilote-capteurs-iot/
├── suivi/        # progress, scoping note, decision log — in French
├── guides/       # project guides (technical, sessions) — in French
├── simulateur/   # fleet simulator (fixed seed)
├── logs/         # generated frames (not committed) and operator validations
├── docs_rt/      # RAG documents: field sheet, runbooks, allowed actions
├── datasets/     # instruction/response JSONL
├── rag/          # chunks and embeddings (generated)
├── models/       # Ollama Modelfile, trained Isolation Forest model
├── scripts/      # detection, pipeline, validation
├── evaluation/   # test cases (JSONL) and scoring grid
└── reports/      # incident reports and test results (generated)
```

## Documentation (in French)

- [Repository map](guides/plan-du-depot.md): what each file is for.
- [Technical guide in brief](guides/guide-technique.md): the 8 steps to build, tools and files.
- [Session 1 guide](guides/guide-seance-1-cadrage.md): J1 scoping, minute-by-minute plan.
- **[Progress](suivi/avancement.md)**: where the project stands, open it first.
- [Scoping note](suivi/note-cadrage.md) and [decision log](suivi/journal-decisions.md).

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set PSEUDO_KEY
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Generate the data and check J2:

```bash
python simulateur/generer_parc.py
python simulateur/injecter_incidents.py
python evaluation/verifier_j2.py
```

Detection and demo commands will be added in the next milestones.

## Team

Florian, Lallie, Mathis and Matthias. Roles are in the [scoping note](suivi/note-cadrage.md), section 7.
