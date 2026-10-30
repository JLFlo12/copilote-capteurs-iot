"""Injecte les incidents et la fausse alerte dans le parc normal (J2).

Plan d'injection (voir suivi/NOTE_CADRAGE.md, section 3) :
- derive          : CAPT-007 et CAPT-023, +0,15 °C/jour à partir de la fin du jour 4
- clone           : CAPT-031, second émetteur via GW-C pendant le jour 8
- replay_tampon   : coupure GW-B 30 min (jour 6, 14 h) et GW-C 45 min (jour 10, 3 h)
- defaillant      : CAPT-012 figé 6 h (jour 9), CAPT-018 18 pics (jour 11),
                    CAPT-036 silence définitif (jour 12, 10 h, aucune trame)
Sortie : logs/trames.csv, triée par ts_received (ordre d'arrivée).
Usage : python simulateur/injecter_incidents.py [--graine 2026]
"""
import argparse

import numpy as np
import pandas as pd

from generer_parc import DEBUT, GRAINE, SORTIE as ENTREE, empreinte, generer, lire_trames

SORTIE = ENTREE.with_name("trames.csv")


def jour(n, heure=0):
    """Début du jour n (1..14) + heure."""
    return DEBUT + pd.Timedelta(days=n - 1, hours=heure)


def injecter_derive(df, sid, debut, pente_par_jour=0.15):
    m = (df.sensor_id == sid) & (df.ts_measure >= debut)
    jours = (df.loc[m, "ts_measure"] - debut).dt.total_seconds() / 86400
    df.loc[m, "temp_c"] = (df.loc[m, "temp_c"] + pente_par_jour * jours).round(2)
    df.loc[m, "label"] = "derive"


def injecter_clone(df, sid, debut, passerelle, rng):
    """Second émetteur : même ID et mêmes seq, autre empreinte, autre passerelle."""
    m = (df.sensor_id == sid) & (df.ts_measure >= debut) & (df.ts_measure < debut + pd.Timedelta(days=1))
    faux = df.loc[m].copy()
    faux["hw_fingerprint"] = empreinte(sid + "-clone", 0)
    faux["gateway_id"] = passerelle
    faux["temp_c"] = (faux["temp_c"] + rng.normal(1.5, 0.5, len(faux))).round(2)
    faux["hum_pct"] = (faux["hum_pct"] + rng.normal(-3, 1, len(faux))).round(1)
    faux["rssi_dbm"] = rng.normal(-55, 2, len(faux)).round().astype(int)
    decalage = pd.to_timedelta(rng.uniform(30, 120, len(faux)), unit="s")
    faux["ts_measure"] += decalage
    faux["ts_received"] += decalage
    faux["label"] = "clone"
    return pd.concat([df, faux], ignore_index=True)


def injecter_rejeu(df, passerelle, debut, duree_min, rng):
    """Coupure de passerelle : les trames sont gardées puis envoyées en rafale."""
    fin = debut + pd.Timedelta(minutes=duree_min)
    m = (df.gateway_id == passerelle) & (df.ts_measure >= debut) & (df.ts_measure < fin)
    rafale = pd.to_timedelta(rng.uniform(5, 60, m.sum()), unit="s")
    df.loc[m, "ts_received"] = fin + rafale
    df.loc[m, "label"] = "replay_tampon"


def injecter_defaillants(df, rng):
    # Valeur figée pendant 6 h (72 trames).
    debut = jour(9, 8)
    m = (df.sensor_id == "CAPT-012") & (df.ts_measure >= debut) & (df.ts_measure < debut + pd.Timedelta(hours=6))
    premiere = df.loc[m].iloc[0]
    df.loc[m, ["temp_c", "hum_pct"]] = premiere[["temp_c", "hum_pct"]].values
    df.loc[m, "label"] = "defaillant"

    # 18 pics hors plage dans la journée 11.
    m = (df.sensor_id == "CAPT-018") & (df.ts_measure >= jour(11)) & (df.ts_measure < jour(12))
    idx = rng.choice(df.index[m], 18, replace=False)
    df.loc[idx, "temp_c"] = rng.choice([-40.0, 85.0], 18)
    df.loc[idx, "label"] = "defaillant"

    # Silence définitif : plus aucune trame (rien à étiqueter).
    m = (df.sensor_id == "CAPT-036") & (df.ts_measure >= jour(12, 10))
    return df.drop(df.index[m])


def injecter(df, graine=GRAINE):
    rng = np.random.default_rng(graine + 1)
    injecter_derive(df, "CAPT-007", jour(5))
    injecter_derive(df, "CAPT-023", jour(5))
    injecter_rejeu(df, "GW-B", jour(6, 14), 30, rng)
    injecter_rejeu(df, "GW-C", jour(10, 3), 45, rng)
    df = injecter_defaillants(df, rng)
    df = injecter_clone(df, "CAPT-031", jour(8), "GW-C", rng)
    return df.sort_values("ts_received", ignore_index=True)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--graine", type=int, default=GRAINE)
    args = p.parse_args()
    if ENTREE.exists():
        df = lire_trames(ENTREE)
    else:
        df = generer(args.graine)
    df = injecter(df, args.graine)
    df.to_csv(SORTIE, index=False, date_format="%Y-%m-%d %H:%M:%S.%f")
    compte = df.label.value_counts()
    print(compte.to_string())
    print(f"{len(df)} trames, {1 - compte['normal'] / len(df):.1%} anormales -> {SORTIE}")


if __name__ == "__main__":
    main()
