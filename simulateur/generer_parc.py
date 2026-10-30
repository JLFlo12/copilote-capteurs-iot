"""Génère les trames normales du parc de capteurs (J2).

40 capteurs, 4 passerelles, 8 zones, 1 trame toutes les 5 min pendant 14 jours.
Sortie : logs/trames_normales.csv (aucune anomalie, label = "normal").
Usage : python simulateur/generer_parc.py [--graine 2026]
"""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

GRAINE = 2026
NB_CAPTEURS = 40
CAPTEURS_PAR_ZONE = 5
PERIODE_MIN = 5
NB_JOURS = 14
DEBUT = pd.Timestamp("2026-11-02 00:00:00")
SORTIE = Path(__file__).resolve().parent.parent / "logs" / "trames_normales.csv"


def zone_de(i):
    """Capteur i (0..39) -> zone BAT-x-Ey : 2 bâtiments x 4 étages."""
    z = i // CAPTEURS_PAR_ZONE
    return f"BAT-{'AB'[z // 4]}-E{z % 4 + 1}"


def passerelle_de(i):
    """2 zones (10 capteurs) par passerelle."""
    return f"GW-{'ABCD'[i // 10]}"


def empreinte(sensor_id, graine):
    """Empreinte matérielle stable, propre à chaque capteur physique."""
    return hashlib.sha256(f"{sensor_id}-{graine}".encode()).hexdigest()[:12]


def lire_trames(chemin):
    """Relit un CSV de trames avec des horodatages en datetime64[ns]."""
    df = pd.read_csv(chemin)
    for col in ("ts_measure", "ts_received"):
        df[col] = pd.to_datetime(df[col], format="ISO8601").astype("datetime64[ns]")
    return df


def generer(graine=GRAINE):
    rng = np.random.default_rng(graine)
    nb_pas = NB_JOURS * 24 * 60 // PERIODE_MIN
    ts = DEBUT + pd.to_timedelta(np.arange(nb_pas) * PERIODE_MIN, unit="min")
    heure = ts.hour + ts.minute / 60
    # Cycle jour/nuit : minimum vers 3 h, maximum vers 15 h.
    cycle = -np.cos(2 * np.pi * (heure - 3) / 24)

    blocs = []
    for i in range(NB_CAPTEURS):
        sid = f"CAPT-{i + 1:03d}"
        biais_t = rng.normal(0, 0.3)
        temp = 21 + biais_t + 1.6 * cycle + rng.normal(0, 0.2, nb_pas)
        hum = 47.5 - 4 * cycle + rng.normal(0, 1.0, nb_pas)
        batterie = rng.uniform(3000, 3100) - np.arange(nb_pas) * 0.005 + rng.normal(0, 3, nb_pas)
        rssi = rng.normal(rng.uniform(-85, -60), 2, nb_pas)
        latence_s = rng.uniform(1, 5, nb_pas)
        blocs.append(pd.DataFrame({
            "sensor_id": sid,
            "hw_fingerprint": empreinte(sid, graine),
            "gateway_id": passerelle_de(i),
            "zone": zone_de(i),
            "seq": rng.integers(0, 50_000) + np.arange(nb_pas),
            "ts_measure": ts,
            "ts_received": ts + pd.to_timedelta(latence_s, unit="s"),
            "temp_c": np.clip(temp, 19, 23).round(2),
            "hum_pct": np.clip(hum, 40, 55).round(1),
            "battery_mv": batterie.round().astype(int),
            "rssi_dbm": rssi.round().astype(int),
            "label": "normal",
        }))
    return pd.concat(blocs, ignore_index=True)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--graine", type=int, default=GRAINE)
    args = p.parse_args()
    df = generer(args.graine)
    SORTIE.parent.mkdir(exist_ok=True)
    df.to_csv(SORTIE, index=False, date_format="%Y-%m-%d %H:%M:%S.%f")
    print(f"{len(df)} trames normales -> {SORTIE}")


if __name__ == "__main__":
    main()
