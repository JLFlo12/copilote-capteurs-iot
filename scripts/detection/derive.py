"""Détection de dérive : écart avec les voisins de zone, pente sur 72 h et CUSUM.

Une dérive lente ne se voit qu'en comparant un capteur à ses 4 voisins (RT-03).
Le résidu est lissé sur 24 h, ce qui efface le cycle jour/nuit.
"""
import numpy as np
import pandas as pd

TRAMES_24H = 288
TRAMES_72H = 864
REFERENCE = pd.Timedelta(days=3)       # jours 1 à 3 : période de référence
K = 0.05                               # tolérance CUSUM (°C)
H = 20                                 # seuil CUSUM
PENTE_MIN = 0.1                        # °C par jour


def residus(df, garder, col):
    """Tableau (ts_measure x capteur) : valeur − médiane des autres capteurs de la zone."""
    d = df.loc[garder]
    piv = d.pivot_table(index="ts_measure", columns="sensor_id", values=col)
    zones = d.groupby("sensor_id").zone.first()
    res = pd.DataFrame(index=piv.index, columns=piv.columns, dtype=float)
    for _, capteurs in zones.groupby(zones):
        cols = list(capteurs.index)
        for c in cols:
            res[c] = piv[c] - piv[[x for x in cols if x != c]].median(axis=1)
    return res


def vers_trames(df, tableau):
    """Ramène un tableau (ts_measure x capteur) sur les lignes de df."""
    cle = pd.MultiIndex.from_frame(df[["ts_measure", "sensor_id"]])
    return pd.Series(tableau.stack().reindex(cle).to_numpy(), index=df.index)


def cusum(ecart):
    out = np.empty(len(ecart))
    s = 0.0
    for i, x in enumerate(ecart):
        if not np.isnan(x):
            s = max(0.0, s + x - K)
        out[i] = s
    return out


def derive(df, garder):
    """Renvoie (masque des trames en dérive, écart estimé en °C, pente en °C/jour)."""
    r24 = residus(df, garder, "temp_c").rolling(TRAMES_24H, min_periods=TRAMES_24H).mean()
    ecart = r24 - r24[r24.index < r24.index.min() + REFERENCE].mean()
    pente = (r24 - r24.shift(TRAMES_72H)) / 3
    somme = ecart.apply(lambda c: pd.Series(cusum(c.to_numpy()), index=c.index))
    # Une dérive ne disparaît pas seule : une fois détectée, elle le reste jusqu'au réétalonnage.
    alerte = ((somme > H) | (pente > PENTE_MIN)).astype(int).cummax() > 0
    masque = vers_trames(df, alerte).fillna(0).astype(bool) & garder
    return masque, vers_trames(df, ecart), vers_trames(df, pente)
