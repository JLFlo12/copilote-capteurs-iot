"""Vérifie les livrables de J2 (données, pseudonymisation, docs, tests, dataset).

Usage : python evaluation/verifier_j2.py   (après simulateur/injecter_incidents.py)
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "scripts"))
sys.path.insert(0, str(RACINE / "simulateur"))
from generer_parc import lire_trames  # noqa: E402
from pseudo import MOTIFS, Pseudonymiseur  # noqa: E402

echecs = 0


def verifier(nom, ok, detail=""):
    global echecs
    echecs += not ok
    print(f"[{'OK ' if ok else 'KO '}] {nom}{' : ' + detail if detail else ''}")


# --- Données simulées ---
df = lire_trames(RACINE / "logs/trames.csv")
n = df.label.value_counts()
taux = 1 - n["normal"] / len(df)
verifier("Taux d'anomalies entre 3 et 5 %", 0.03 <= taux <= 0.05, f"{taux:.1%}")
verifier("Les 5 étiquettes sont présentes",
         set(n.index) == {"normal", "derive", "clone", "replay_tampon", "defaillant"})

normal = df[df.label == "normal"]
verifier("Normal : température dans [19 ; 23] °C", normal.temp_c.between(19, 23).all())
verifier("Normal : humidité dans [40 ; 55] %", normal.hum_pct.between(40, 55).all())
lat = (normal.ts_received - normal.ts_measure).dt.total_seconds()
verifier("Normal : latence < 10 s", (lat < 10).all(), f"max {lat.max():.1f} s")

verifier("Normal : une seule empreinte par capteur",
         (normal.groupby("sensor_id").hw_fingerprint.nunique() == 1).all())

rej = df[df.label == "replay_tampon"]
retard = (rej.ts_received - rej.ts_measure).dt.total_seconds() / 60
verifier("Rejeu : retard > 5 min sauf dernière trame", (retard > 5).mean() > 0.8, f"min {retard.min():.1f} min")
verifier("Rejeu : aucun seq en double", not rej.duplicated(["sensor_id", "seq"]).any())

clo = df[df.label == "clone"]
legit = df[(df.sensor_id == "CAPT-031") & (df.label != "clone")]
verifier("Clone : empreinte différente de l'original", not clo.hw_fingerprint.isin(legit.hw_fingerprint).any())
verifier("Clone : seq en double avec l'original", clo.seq.isin(legit.seq).all())

d = df[df.label == "derive"].copy()
d["jour"] = (d.ts_measure - d.ts_measure.min()).dt.days
ecart = d.groupby("jour").temp_c.mean()
verifier("Dérive : la température monte avec le temps", ecart.iloc[-1] > ecart.iloc[0] + 1, f"+{ecart.iloc[-1] - ecart.iloc[0]:.2f} °C")

dern = df[df.sensor_id == "CAPT-036"].ts_measure.max()
verifier("Silence : CAPT-036 n'émet plus après le jour 12", dern < pd.Timestamp("2026-11-13 10:00"), str(dern))

# --- Pseudonymisation ---
p = Pseudonymiseur(b"cle-de-test")
sortie = p.texte("CAPT-012 sur GW-B en BAT-A-E3")
verifier("Pseudo : aucun identifiant réel restant", not any(m.search(sortie) for m in MOTIFS.values()), sortie)
verifier("Pseudo : stable", p.texte("CAPT-012") == p.texte("CAPT-012"))
verifier("Pseudo : réversible côté code", p.reveler(sortie) == "CAPT-012 sur GW-B en BAT-A-E3")

# --- Docs, tests, dataset ---
docs = sorted((RACINE / "docs_rt").glob("RT-*.md"))
verifier("Base documentaire : au moins 5 fichiers", len(docs) >= 5, str(len(docs)))
ids_docs = {d.name[:5] for d in docs}

tests = [json.loads(l) for l in open(RACINE / "evaluation/cas_tests.jsonl", encoding="utf-8")]
verifier("Grille : au moins 8 tests", len(tests) >= 8, str(len(tests)))
champs = {"id", "category", "question", "expected", "forbidden", "requires_sources"}
verifier("Grille : champs complets", all(champs <= t.keys() for t in tests))

data = [json.loads(l) for l in open(RACINE / "datasets/rt_instructions.jsonl", encoding="utf-8")]
verifier("Dataset : champs instruction/input/output", all({"instruction", "input", "output"} <= e.keys() for e in data))
fuite = [e["instruction"] for e in data if any(m.search(e["input"] + e["output"]) for m in MOTIFS.values())]
verifier("Dataset : aucun identifiant réel", not fuite, str(fuite))
cites = {s for e in data for s in re.findall(r"RT-\d\d", e["output"])}
verifier("Dataset : sources citées existantes", cites <= ids_docs, str(cites - ids_docs))

print(f"\n{'Tout est bon' if not echecs else f'{echecs} échec(s)'}")
sys.exit(1 if echecs else 0)
