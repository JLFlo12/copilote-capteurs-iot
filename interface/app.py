"""Interface web du copilote : parc, alertes, mesures (100 % locale).

Usage : streamlit run interface/app.py   (après simulateur/injecter_incidents.py)
Les onglets « Décisions » et « Attaque en direct » arrivent avec le copilote (J4).
"""
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

RACINE = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RACINE / "scripts"), str(RACINE / "simulateur")]
from detecter import construire_alertes, detecter  # noqa: E402
from detection.derive import residus  # noqa: E402
from generer_parc import lire_trames  # noqa: E402

TRAMES = RACINE / "logs" / "trames.csv"
MESURES = RACINE / "reports" / "mesures-j3.md"
DOCS = RACINE / "docs_rt"
TESTS = RACINE / "evaluation" / "cas-tests.jsonl"

NIVEAUX = ["critique", "majeur", "mineur", "info"]
COULEUR = {"critique": "red", "majeur": "orange", "mineur": "blue", "info": "gray"}
LIBELLE = {"clone": "Capteur cloné", "defaillant": "Capteur défaillant", "derive": "Dérive",
           "replay_tampon": "Rejeu de tampon (probablement normal)", "inhabituel": "Trame inhabituelle"}


@st.cache_data(show_spinner="Détection en cours (environ 15 s)…")
def charger():
    df = lire_trames(TRAMES)
    verdict, details = detecter(df)
    alertes = construire_alertes(df, verdict, details)
    temp = residus(df, ~details["deja_vu"], "temp_c")
    return df.drop(columns="label"), verdict, alertes, temp


def etat_capteurs(df, alertes):
    capteurs = df.groupby("sensor_id").agg(zone=("zone", "first"), passerelle=("gateway_id", "first"),
                                           derniere_trame=("ts_measure", "max"))
    capteurs["etat"] = "normal"
    rang = {n: i for i, n in enumerate(NIVEAUX)}
    for a in sorted(alertes, key=lambda a: -rang[a["niveau"]]):     # le plus grave écrit en dernier
        if a["cible"] in capteurs.index:
            capteurs.loc[a["cible"], "etat"] = LIBELLE[a["type"]]
    return capteurs


def onglet_parc(df, alertes, residu):
    capteurs = etat_capteurs(df, alertes)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capteurs", len(capteurs))
    c2.metric("Trames", f"{len(df):,}".replace(",", " "))
    c3.metric("Capteurs en alerte", int((capteurs.etat != "normal").sum()))
    c4.metric("Coupures de passerelle", sum(a["type"] == "replay_tampon" for a in alertes))

    st.subheader("État par zone")
    for zone, groupe in capteurs.groupby("zone"):
        cols = st.columns([1.2] + [1] * len(groupe))
        cols[0].markdown(f"**{zone}**  \n{groupe.passerelle.iloc[0]}")
        for col, (sid, c) in zip(cols[1:], groupe.iterrows()):
            if c.etat == "normal":
                col.markdown(f"{sid}  \n:green[normal]")
            else:
                col.markdown(f"**{sid}**  \n:red[{c.etat}]")

    st.subheader("Un capteur face à ses voisins")
    sid = st.selectbox("Capteur", capteurs.index, index=list(capteurs.index).index("CAPT-007"))
    d = df[(df.sensor_id == sid)].drop_duplicates("ts_measure").set_index("ts_measure").sort_index()
    voisins = df[(df.zone == capteurs.at[sid, "zone"]) & (df.sensor_id != sid)]
    courbes = pd.DataFrame({
        sid: d.temp_c.resample("1h").mean(),
        "médiane des voisins": voisins.groupby("ts_measure").temp_c.median().resample("1h").mean(),
    })
    st.line_chart(courbes, y_label="Température (°C)")
    st.caption("Moyennes horaires. L'écart lissé sur 24 h avec les voisins sert à détecter une dérive.")
    st.line_chart(residu[sid].resample("1h").mean().rolling(24).mean().rename("écart lissé (°C)"),
                  y_label="Écart avec les voisins (°C)")


def onglet_alertes(alertes):
    c1, c2 = st.columns(2)
    niveaux = c1.multiselect("Niveau", NIVEAUX, default=["critique", "majeur", "mineur", "info"])
    types = c2.multiselect("Type", list(LIBELLE), default=[t for t in LIBELLE if t != "inhabituel"],
                           format_func=LIBELLE.get)
    choix = [a for a in alertes if a["niveau"] in niveaux and a["type"] in types]
    st.caption(f"{len(choix)} alerte(s) sur {len(alertes)}. Les scores sont calculés par le code, pas par le LLM.")
    for a in choix:
        titre = f":{COULEUR[a['niveau']]}[{a['niveau'].upper()}] {LIBELLE[a['type']]} — {a['cible']}"
        with st.expander(titre):
            st.markdown(f"**Période** : {a['debut'][:16]} → {(a['fin'] or 'en cours')[:16]}  ·  "
                        f"**Zone** : {a['zone'] or '—'}  ·  **Trames** : {a['nb_trames']}  ·  **Score** : {a['score']}")
            st.markdown("**Preuves**\n" + "\n".join(f"- {p}" for p in a["preuves"]))
            st.markdown("**Action proposée** : " + ", ".join(f"`{x}`" for x in a["actions_proposees"]))
            st.info("Explication du LLM et boutons Valider / Refuser : au jalon J4.")
            for src in a["sources"]:
                doc = next(DOCS.glob(f"{src}-*.md"), None)
                if doc:
                    with st.popover(f"Source {src}"):
                        st.markdown(doc.read_text(encoding="utf-8"))


def onglet_mesures():
    if MESURES.exists():
        texte = MESURES.read_text(encoding="utf-8")
        st.markdown(texte.split("\n", 1)[1])          # sans le titre, déjà affiché par l'onglet
    else:
        st.warning("Lancer `python evaluation/mesures.py` pour produire les mesures.")
    st.subheader("Cas de test du copilote")
    tests = pd.DataFrame([json.loads(l) for l in TESTS.read_text(encoding="utf-8").splitlines() if l.strip()])
    st.caption("Exécutés au jalon J4, une fois le copilote branché sur le LLM.")
    st.dataframe(tests[["id", "category", "question", "expected", "forbidden"]], hide_index=True, width="stretch")


def main():
    st.set_page_config(page_title="Copilote IoT", layout="wide")
    st.title("Copilote d'exploitation — parc de capteurs IoT")
    st.caption("L'IA propose, l'humain décide. Tout tourne en local, sur des données simulées.")
    if not TRAMES.exists():
        st.error("Pas de données : lancer `python simulateur/generer_parc.py` puis `python simulateur/injecter_incidents.py`.")
        st.stop()
    df, _, alertes, residu = charger()
    parc, liste, mesures = st.tabs(["Parc", "Alertes", "Mesures et tests"])
    with parc:
        onglet_parc(df, alertes, residu)
    with liste:
        onglet_alertes(alertes)
    with mesures:
        onglet_mesures()


main()
