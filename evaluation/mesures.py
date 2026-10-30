"""Mesure la détection (J3) avec la vérité terrain `label`, puis teste deux attaques.

Sortie : reports/mesures-j3.md (et le résumé à l'écran).
Usage : python evaluation/mesures.py   (après simulateur/injecter_incidents.py)
"""
import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RACINE / "scripts"), str(RACINE / "simulateur")]
from detecter import construire_alertes, detecter  # noqa: E402
from generer_parc import lire_trames  # noqa: E402

SORTIE = RACINE / "reports" / "mesures-j3.md"
INCIDENTS = ["defaillant", "derive", "clone"]
TYPES = INCIDENTS + ["replay_tampon"]


def tableau_types(label, verdict):
    lignes = ["| Type | Trames réelles | Trames détectées | Correctes | Précision | Rappel |", "|---|---|---|---|---|---|"]
    for t in TYPES:
        reel, pred = label == t, verdict == t
        ok = (reel & pred).sum()
        precision = ok / pred.sum() if pred.sum() else float("nan")
        lignes.append(f"| {t} | {reel.sum()} | {pred.sum()} | {ok} | {precision:.1%} | {ok / reel.sum():.1%} |")
    return lignes


def scenario_fausse_coupure(df):
    """Pendant la coupure de GW-B, l'attaquant glisse 5 trames avec sa propre empreinte."""
    df = df.copy()
    cibles = df.index[df.label == "replay_tampon"][:5]
    df.loc[cibles, "hw_fingerprint"] = "attaquant00"
    v, _ = detecter(df, avec_iforest=False)
    return (v[cibles] == "clone").sum(), len(cibles)


def scenario_rejeu_malveillant(df):
    """Un attaquant renvoie 12 anciennes trames de CAPT-005 (jour 2) au jour 7, sans coupure."""
    anciennes = df[(df.sensor_id == "CAPT-005") & (df.ts_measure.dt.day == 3)].head(12).copy()
    retard = pd.Timestamp("2026-11-08 12:00") - anciennes.ts_received.min()
    anciennes["ts_received"] += retard
    df = pd.concat([df, anciennes], ignore_index=True)
    v, _ = detecter(df, avec_iforest=False)
    return (v.iloc[-12:] == "clone").sum(), 12


def main():
    df = lire_trames(RACINE / "logs" / "trames.csv")
    verdict, details = detecter(df)
    alertes = construire_alertes(df, verdict, details)
    label = df.label

    faux_incidents = (label == "normal") & verdict.isin(INCIDENTS)
    rejeu_en_incident = (label == "replay_tampon") & verdict.isin(INCIDENTS)
    if_seul = details["if_seul"]
    silence = [a for a in alertes if a["type"] == "defaillant" and a["nb_trames"] == 0]
    retard_derive = (df[(verdict == "derive")].groupby("sensor_id").ts_measure.min()
                     - df[label == "derive"].groupby("sensor_id").ts_measure.min())
    fc_ok, fc_n = scenario_fausse_coupure(df)
    rm_ok, rm_n = scenario_rejeu_malveillant(df)

    l = ["# Mesures de la détection (J3)", "",
         "Généré par `evaluation/mesures.py`. Les détecteurs ne lisent jamais `label` : il sert seulement ici, à mesurer.", "",
         f"Données : {len(df)} trames, graine 2026.", "",
         "## Par type de trame", ""] + tableau_types(label, verdict) + ["",
         "## Objectifs", "",
         "| Objectif | Résultat |", "|---|---|",
         f"| Trames normales classées en incident | {faux_incidents.sum()} |",
         f"| Rejeux de tampon classés en incident (objectif : 0) | {rejeu_en_incident.sum()} |",
         f"| Silence de CAPT-036 signalé | {'oui' if any(a['cible'] == 'CAPT-036' for a in silence) else 'non'} |",
         f"| Délai de détection de la dérive | {', '.join(f'{s} : {r.total_seconds() / 86400:.1f} j' for s, r in retard_derive.items())} |",
         "", "## Alertes produites", "",
         "| Type | Alertes |", "|---|---|"]
    l += [f"| {t} | {n} |" for t, n in pd.Series([a["type"] for a in alertes]).value_counts().items()]
    l += ["", "## Isolation Forest seul", "",
          "Ce que le modèle signale sans les règles (les 0,1 % de trames les plus isolées). Dans la fusion, ces trames prennent le verdict des règles quand une règle s'applique.", "",
          "| Type de trame | Trames | Signalées par l'Isolation Forest |", "|---|---|---|"]
    l += [f"| {t} | {(label == t).sum()} | {(if_seul & (label == t)).sum()} |" for t in ["normal"] + TYPES]
    l += ["", "## Attaques", "",
          "| Scénario | Attendu | Résultat |", "|---|---|---|",
          f"| Fausse coupure : 5 trames à empreinte inconnue dans une rafale de GW-B | clone | {fc_ok}/{fc_n} |",
          f"| Rejeu malveillant : 12 anciennes trames renvoyées sans coupure | clone | {rm_ok}/{rm_n} |", ""]
    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text("\n".join(l), encoding="utf-8")
    print("\n".join(l))


if __name__ == "__main__":
    main()
