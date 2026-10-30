"""Isolation Forest : repère les trames inhabituelles que les règles ne couvrent pas.

Non supervisé : entraîné sur toutes les trames, sans étiquette, et signale les 0,1 % les plus isolées.
On ne l'entraîne pas sur les seuls jours normaux : il ne sait pas extrapoler hors des valeurs vues
(un retard de 30 min suivrait le même chemin qu'un retard de 5 s). Avec 256 trames par arbre
(réglage par défaut), les rares anomalies sont absentes des échantillons : on en prend 8 192.
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from detection.derive import residus, vers_trames

MODELE = Path(__file__).resolve().parents[2] / "models" / "iforest.joblib"
CONTAMINATION = 0.001
ECHANTILLON = 8192


def caracteristiques(df, garder):
    X = pd.DataFrame(index=df.index)
    X["res_temp"] = vers_trames(df, residus(df, garder, "temp_c"))
    X["res_hum"] = vers_trames(df, residus(df, garder, "hum_pct"))
    X["retard_s"] = (df.ts_received - df.ts_measure).dt.total_seconds()
    # Écarts à la médiane glissante sur 24 h : la batterie baisse lentement, une médiane
    # sur toute la période ferait paraître anormale toute la fin de la simulation.
    ordre = df.sort_values(["sensor_id", "ts_measure"])
    for col, nom in [("rssi_dbm", "rssi_ecart"), ("battery_mv", "batterie_ecart")]:
        med = ordre.groupby("sensor_id")[col].transform(lambda s: s.rolling(288, min_periods=1).median())
        X[nom] = (df[col] - med.reindex(df.index))
    return X.fillna(0)


def iforest(df, garder):
    """Renvoie (masque des trames inhabituelles, score d'anomalie : plus grand = plus inhabituel)."""
    X = caracteristiques(df, garder)
    modele = IsolationForest(n_estimators=200, max_samples=ECHANTILLON,
                             contamination=CONTAMINATION, random_state=0)
    modele.fit(X[garder])
    MODELE.parent.mkdir(exist_ok=True)
    joblib.dump(modele, MODELE)
    score = pd.Series(-modele.score_samples(X), index=df.index)
    return pd.Series(modele.predict(X) == -1, index=df.index) & garder, score
