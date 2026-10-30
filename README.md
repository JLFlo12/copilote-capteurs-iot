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
python scripts/detecter.py       # alerts in logs/alertes.json
python evaluation/mesures.py     # results in reports/mesures-j3.md
python scripts/rag.py indexer    # RAG index (Ollama running)
python scripts/copilote.py --max 3   # copilot in the terminal, human validation
python evaluation/tests_copilote.py  # 20 tests, results in reports/tests-j4.md
streamlit run interface/app.py   # local web page: http://localhost:8501
```

## Demo

The day before: regenerate the data and rerun `evaluation/tests_copilote.py` (commands above).

Project in a VirtualBox VM (NAT) with Ollama on the host (GPU): set `OLLAMA_HOST=http://10.0.2.2:11434` in `.env`.
Streamlit only listens on `localhost`; from the host, use an SSH tunnel and open http://localhost:8501.

```bash
streamlit run interface/app.py                           # in the VM
ssh -N -L 8501:localhost:8501 -p 2222 <user>@127.0.0.1   # on the host (NAT forward 2222 → 22)
```

Before starting: wait for the detection to finish (about 15 s), then ask for the explanation of an alert you will not show (CAPT-018) to load the model.

Running order (6 min):

| Tab | What to show | Project requirement |
|---|---|---|
| Parc | Status by zone, CAPT-007 against its neighbours | Field data (simulated) |
| Alertes | CAPT-012 (stuck value): explanation, source RT-02, **Valider** | Incident through to an action approved by a human |
| Alertes | CAPT-007 (drift) and CAPT-031 (clone): **Refuser** one of them | The code decides, the human can refuse |
| Alertes | Buffer replay GW-B ("probably normal") | False alarm |
| Attaque en direct | "Injection cachée dans le nom de zone", then "Source inventée" | Injection defeated; the copilot says it does not know |
| Décisions | Log: approved / refused, never executed (dry-run) | Traceability |
| Mesures et tests | Detection, attacks, 20 tests | What it detects, misses and triggers wrongly |

If Ollama does not answer, the page still shows the detection: restart Ollama and reload the page.

## Team

Florian, Lallie, Mathis and Matthias. Roles are in the [scoping note](suivi/note-cadrage.md), section 7.
