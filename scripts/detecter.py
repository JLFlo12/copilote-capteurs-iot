"""Détection (J3) : lance les détecteurs, fusionne leurs verdicts et produit les alertes.

Le score est calculé ici, par le code. Le LLM ne fera qu'expliquer ces alertes (J4).
Sortie : logs/alertes.json.
Usage : python scripts/detecter.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "simulateur"))
from generer_parc import lire_trames  # noqa: E402

from detection.derive import derive  # noqa: E402
from detection.iforest import iforest  # noqa: E402
from detection.regles import clone_et_rejeu, fige, hors_plage, identite_attendue, silences  # noqa: E402

ENTREE = RACINE / "logs" / "trames.csv"
SORTIE = RACINE / "logs" / "alertes.json"
UNE_HEURE = pd.Timedelta(hours=1)

# Ordre de priorité quand plusieurs détecteurs marquent la même trame : le dernier gagne.
PRIORITE = ["inhabituel", "derive", "replay_tampon", "defaillant", "clone"]
NIVEAU = {"clone": "critique", "defaillant": "majeur", "derive": "mineur",
          "inhabituel": "mineur", "replay_tampon": "info"}
ACTIONS = {"clone": ["donnees_non_fiables", "alerte_securite"], "defaillant": ["ticket_inspection"],
           "derive": ["reetalonnage_planifie"], "inhabituel": ["aucune_action"],
           "replay_tampon": ["aucune_action"]}
SOURCES = {"clone": ["RT-06"], "defaillant": ["RT-02"], "derive": ["RT-03", "RT-04"],
           "inhabituel": ["RT-01"], "replay_tampon": ["RT-05"]}


def detecter(df, avec_iforest=True):
    """Renvoie (verdict par trame, détails des détecteurs). Ne lit jamais `label`."""
    df = df.drop(columns="label", errors="ignore")
    identite = identite_attendue(df)
    clone, rejeu, deja_vu, coupures = clone_et_rejeu(df, identite)
    legitime = ~clone
    plage = hors_plage(df)
    figee = fige(df, legitime & ~plage)
    defaillant = plage | figee
    der, ecart, pente = derive(df, legitime & ~defaillant)
    masques = {"derive": der, "replay_tampon": rejeu, "defaillant": defaillant, "clone": clone}
    score_if = inhabituel = None
    if avec_iforest:
        inhabituel, score_if = iforest(df, legitime)
        masques["inhabituel"] = inhabituel
    verdict = pd.Series("normal", index=df.index)
    for nom in PRIORITE:
        if nom in masques:
            verdict[masques[nom]] = nom
    details = {"identite": identite, "deja_vu": deja_vu, "coupures": coupures, "plage": plage,
               "figee": figee, "ecart": ecart, "pente": pente, "score_if": score_if, "if_seul": inhabituel,
               "silences": silences(df, legitime, identite)}
    return verdict, details


def blocs(df, masque, cle, trou=UNE_HEURE):
    """Découpe les trames marquées en épisodes : même clé, moins de `trou` entre deux trames."""
    d = df.loc[masque].sort_values([cle, "ts_measure"])
    for k, g in d.groupby(cle):
        for _, b in g.groupby((g.ts_measure.diff() > trou).cumsum()):
            yield k, b


def alerte(type_, cible, debut, fin, nb, score, preuves, zone=None):
    return {"type": type_, "niveau": NIVEAU[type_], "cible": cible, "zone": zone,
            "debut": str(debut), "fin": str(fin) if fin is not None else None, "nb_trames": int(nb),
            "score": round(float(score), 2), "preuves": preuves,
            "actions_proposees": ACTIONS[type_], "sources": SOURCES[type_]}


def construire_alertes(df, verdict, d):
    zone = df.groupby("sensor_id").zone.first()
    sortie = []
    # Des pics isolés dans la même journée forment un seul incident : on regroupe sur 12 h.
    for sid, b in blocs(df, verdict == "defaillant", "sensor_id", pd.Timedelta(hours=12)):
        nb_plage, nb_fige = int(d["plage"][b.index].sum()), int(d["figee"][b.index].sum())
        preuves = []
        if nb_plage:
            preuves.append(f"{nb_plage} valeur(s) hors plage (température de {b.temp_c.min()} à {b.temp_c.max()} °C)")
        if nb_fige:
            preuves.append(f"valeur figée sur {nb_fige} trames ({nb_fige * 5 / 60:.1f} h), voisins de zone variables")
        sortie.append(alerte("defaillant", sid, b.ts_measure.min(), b.ts_measure.max(), len(b),
                             1.0 if nb_plage else 0.9, preuves, zone[sid]))
    for s in d["silences"]:
        sortie.append(alerte("defaillant", s["capteur"], s["debut"], s["fin"], 0, 0.8,
                             [f"aucune trame depuis {s['debut']}, alors que {s['voisins_emis']} trames "
                              f"des voisins de {s['passerelle']} sont arrivées"], zone[s["capteur"]]))
    for sid, b in blocs(df, verdict == "clone", "sensor_id"):
        fenetre = df[(df.sensor_id == sid) & df.ts_measure.between(b.ts_measure.min(), b.ts_measure.max())]
        preuves = [f"{fenetre.hw_fingerprint.nunique()} empreintes matérielles pour un même identifiant",
                   f"{int(d['deja_vu'][b.index].sum())} seq déjà reçus",
                   f"passerelles : {', '.join(sorted(fenetre.gateway_id.unique()))} "
                   f"(attendue : {d['identite'].at[sid, 'gateway_id']})"]
        sortie.append(alerte("clone", sid, b.ts_measure.min(), b.ts_measure.max(), len(b), 1.0, preuves, zone[sid]))
    for sid, b in blocs(df, verdict == "derive", "sensor_id"):
        e, p = d["ecart"][b.index], d["pente"][b.index]
        sortie.append(alerte("derive", sid, b.ts_measure.min(), b.ts_measure.max(), len(b),
                             min(1.0, e.max() / 0.5),
                             [f"écart avec la médiane des voisins : +{e.max():.2f} °C",
                              f"pente sur 72 h : {p.max():+.2f} °C/jour"], zone[sid]))
    for c in d["coupures"]:
        if c["valides"]:
            sortie.append(alerte("replay_tampon", c["passerelle"], c["debut"], c["fin"], c["valides"], 0.1,
                                 [f"aucune trame de {c['passerelle']} pendant {c['duree_min']} min",
                                  f"{c['valides']} trames en retard, seq à la suite, mêmes empreintes",
                                  "probablement normal : rejeu de tampon après coupure"]))
    if d["score_if"] is not None:
        for sid, b in blocs(df, verdict == "inhabituel", "sensor_id"):
            sortie.append(alerte("inhabituel", sid, b.ts_measure.min(), b.ts_measure.max(), len(b),
                                 min(1.0, d["score_if"][b.index].max()),
                                 ["trame inhabituelle selon l'Isolation Forest, aucune règle ne s'applique"],
                                 zone[sid]))
    ordre = {"critique": 0, "majeur": 1, "mineur": 2, "info": 3}
    return sorted(sortie, key=lambda a: (ordre[a["niveau"]], a["debut"]))


def main():
    df = lire_trames(ENTREE)
    verdict, details = detecter(df)
    alertes = construire_alertes(df, verdict, details)
    SORTIE.write_text(json.dumps(alertes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(pd.Series([a["type"] for a in alertes]).value_counts().to_string())
    print(f"{len(alertes)} alertes -> {SORTIE}")


if __name__ == "__main__":
    main()
