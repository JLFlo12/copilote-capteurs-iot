"""Détecteurs à règles : capteur défaillant, clone, rejeu de tampon.

Seuils repris de la note de cadrage (section 3) et de RT-05 (les 5 critères).
"""
import numpy as np
import pandas as pd

PLAGE_TEMP = (-20, 60)
PLAGE_HUM = (0, 100)
FENETRE_FIGE = 12                      # trames, soit 1 h
SILENCE = pd.Timedelta(minutes=15)
RETARD = pd.Timedelta(minutes=5)
COUPURE = pd.Timedelta(minutes=15)
ECART_RAFALE = pd.Timedelta(minutes=10)


def identite_attendue(df):
    """Empreinte et passerelle habituelles de chaque capteur (les plus fréquentes)."""
    return df.groupby("sensor_id")[["hw_fingerprint", "gateway_id"]].agg(lambda s: s.mode().iloc[0])


def hors_plage(df):
    return ~df.temp_c.between(*PLAGE_TEMP) | ~df.hum_pct.between(*PLAGE_HUM)


def fige(df, garder):
    """Trames comprises dans une fenêtre de 12 trames où température et humidité ne bougent pas."""
    d = df.loc[garder, ["sensor_id", "ts_measure", "temp_c", "hum_pct"]].sort_values(["sensor_id", "ts_measure"])
    g = d.groupby("sensor_id")

    def etendue(col):
        return g[col].transform(lambda s: s.rolling(FENETRE_FIGE).max() - s.rolling(FENETRE_FIGE).min())

    fin = ((etendue("temp_c") == 0) & (etendue("hum_pct") == 0)).astype(float)
    # La fenêtre se termine sur `fin` : on propage le marquage aux 11 trames qui précèdent.
    inverse = fin.iloc[::-1]
    couvre = inverse.groupby(d.sensor_id.iloc[::-1]).transform(
        lambda s: s.rolling(FENETRE_FIGE, min_periods=1).max()).iloc[::-1] > 0
    return couvre.reindex(df.index, fill_value=False)


def silences(df, garder, identite):
    """Alertes de silence : un capteur se tait alors que ses voisins de passerelle émettent.

    On regarde les trous de `ts_measure` : une coupure de passerelle ne crée pas de trou,
    car les mesures sont gardées en tampon puis renvoyées.
    """
    d = df.loc[garder].sort_values("ts_measure")
    fin_parc = d.ts_measure.max()
    alertes = []
    for sid, s in d.groupby("sensor_id"):
        ts = s.ts_measure.reset_index(drop=True)
        gw = identite.at[sid, "gateway_id"]
        autres = d.ts_measure[(d.gateway_id == gw) & (d.sensor_id != sid)]
        nb_autres = d.sensor_id[d.gateway_id == gw].nunique() - 1
        trous = [(ts[i - 1], ts[i]) for i in np.flatnonzero(ts.diff() > SILENCE)]
        if fin_parc - ts.iloc[-1] > SILENCE:
            trous.append((ts.iloc[-1], None))
        for debut, fin in trous:
            emis = autres.between(debut, fin if fin is not None else fin_parc, inclusive="neither").sum()
            if emis >= nb_autres:          # au moins un cycle complet des voisins
                alertes.append({"capteur": sid, "passerelle": gw, "debut": debut, "fin": fin,
                                "voisins_emis": int(emis)})
    return alertes


def clone_et_rejeu(df, identite):
    """Sépare les rafales légitimes (rejeu de tampon) des trames usurpées ou rejouées.

    Renvoie (clone, rejeu, deja_vu, coupures) : deux masques de trames, le masque des
    `seq` déjà reçus, et la liste des coupures de passerelle trouvées.
    """
    usurpe = ((df.hw_fingerprint != df.sensor_id.map(identite.hw_fingerprint))
              | (df.gateway_id != df.sensor_id.map(identite.gateway_id)))
    retard = (df.ts_received - df.ts_measure) > RETARD
    deja_vu = df.sort_values("ts_received").duplicated(["sensor_id", "seq"]).reindex(df.index)

    a_l_heure = df[~retard & ~usurpe]
    candidats = df[retard & ~usurpe].sort_values("ts_received")
    rejeu = pd.Series(False, index=df.index)
    coupures = []
    for gw, c in candidats.groupby("gateway_id"):
        gw_a_l_heure = a_l_heure[a_l_heure.gateway_id == gw]
        for _, rafale in c.groupby((c.ts_received.diff() > ECART_RAFALE).cumsum()):
            t0 = rafale.ts_received.min()
            debut_mes, fin_mes = rafale.ts_measure.min(), rafale.ts_measure.max()
            avant = gw_a_l_heure.ts_received[gw_a_l_heure.ts_measure < debut_mes]
            if avant.empty:
                continue
            dernier = avant.max()                                       # dernière réception avant le trou
            # Critère 1 : aucune trame de la passerelle n'est arrivée à l'heure pendant la période mesurée.
            muette = not gw_a_l_heure.ts_measure.between(debut_mes, fin_mes).any()
            coupure = muette and t0 - dernier >= COUPURE                # critères 1 et 2
            comble = debut_mes - dernier <= ECART_RAFALE                # critère 4
            valides = rafale.index[~deja_vu[rafale.index]]              # critère 3 ; 5 = non usurpé
            if coupure and comble:
                rejeu[valides] = True
            coupures.append({"passerelle": gw, "debut": dernier, "fin": t0,
                             "duree_min": round((t0 - dernier).total_seconds() / 60),
                             "trames": len(rafale), "valides": int(coupure and comble) * len(valides)})
    clone = usurpe | deja_vu | (retard & ~rejeu)
    return clone, rejeu, deja_vu, coupures
