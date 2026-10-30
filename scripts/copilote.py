"""Chaîne complète : alertes → pseudonymisation → explication → validation humaine → journal.

Le code décide du type, du score et de l'action ; le LLM explique ; l'opérateur valide ou refuse.
Rien n'est jamais exécuté : DRY_RUN=true est imposé par config.py (règle n° 5). Chaque décision va dans logs/decisions.jsonl,
et chaque incident validé produit un rapport court dans reports/incidents/.
Usage : python scripts/copilote.py [--max 5]
"""
import argparse
import json
from datetime import datetime

from config import RACINE
from expliquer import LISTE_BLANCHE, expliquer_alerte
from pseudo import Pseudonymiseur

ALERTES = RACINE / "logs" / "alertes.json"
DECISIONS = RACINE / "logs" / "decisions.jsonl"
INCIDENTS = RACINE / "reports" / "incidents"


def action_finale(alerte, explication):
    """L'action vient du code. Si le LLM en propose une autre, on le signale sans la suivre."""
    proposees = explication["controles"]["actions_valides"]
    ecart = sorted(set(proposees) - set(alerte["actions_proposees"]))
    actions = [a for a in alerte["actions_proposees"] if a in LISTE_BLANCHE]
    return actions, ecart


def rapport_incident(alerte, explication, pseudo, operateur_ok):
    """Rapport d'incident en 6 lignes, rempli par le code (les faits ne viennent pas du LLM)."""
    r = explication["reponse"]
    resume = pseudo.reveler(str(r.get("reponse", ""))).strip().replace("\n", " ")
    return "\n".join([
        f"1. Incident : {alerte['type']} ({alerte['niveau']}) sur {alerte['cible']}"
        + (f", zone {alerte['zone']}" if alerte["zone"] else ""),
        f"2. Période : {alerte['debut'][:16]} → {(alerte['fin'] or 'en cours')[:16]}",
        f"3. Constat (calculé par le code) : {' ; '.join(alerte['preuves'])}",
        f"4. Explication du copilote : {resume}",
        f"5. Action : {', '.join(alerte['actions_proposees'])} — "
        f"{'validée' if operateur_ok else 'refusée'} par l'opérateur (dry-run, non exécutée)",
        f"6. Sources : {', '.join(explication['controles']['sources_valides']) or 'aucune'}",
    ])


def traiter(alerte, pseudo, decision, explication=None, operateur="operateur"):
    """Applique la décision (True/False) sur une alerte expliquée et la journalise."""
    explication = explication or expliquer_alerte(alerte, pseudo)
    actions, ecart = action_finale(alerte, explication)
    entree = {
        "horodatage": datetime.now().isoformat(timespec="seconds"), "operateur": operateur,
        "alerte": {k: alerte[k] for k in ("type", "niveau", "cible", "debut", "score")},
        "actions": actions, "decision": "validee" if decision else "refusee",
        "executee": False, "ecart_llm": ecart,     # aucun exécuteur : dry-run imposé
        "sources": explication["controles"]["sources_valides"],
        "sources_inventees": explication["controles"]["sources_inventees"],
        "latence_s": explication["latence_s"],
    }
    DECISIONS.parent.mkdir(exist_ok=True)
    with DECISIONS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")
    if decision and alerte["type"] != "replay_tampon":
        INCIDENTS.mkdir(parents=True, exist_ok=True)
        nom = f"{alerte['debut'][:10]}-{alerte['type']}-{alerte['cible']}.md"
        (INCIDENTS / nom).write_text(rapport_incident(alerte, explication, pseudo, True) + "\n", encoding="utf-8")
    return entree, explication


def afficher(alerte, explication, pseudo):
    r, c = explication["reponse"], explication["controles"]
    print(f"\n=== [{alerte['niveau'].upper()}] {alerte['type']} — {alerte['cible']} (score {alerte['score']})")
    for p in alerte["preuves"]:
        print(f"  preuve : {p}")
    print(f"\n  {pseudo.reveler(str(r.get('reponse', '')))}")
    print(f"\n  Action proposée par le code : {', '.join(alerte['actions_proposees'])}")
    print(f"  Sources : {', '.join(c['sources_valides']) or 'aucune'}"
          + (f"  |  sources inventées rejetées : {', '.join(c['sources_inventees'])}" if c["sources_inventees"] else ""))
    if r.get("refus"):
        print(f"  Refus du copilote : {r['refus']}")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--max", type=int, default=None, help="nombre d'alertes à traiter")
    args = p.parse_args()
    if not ALERTES.exists():
        raise SystemExit("Pas d'alertes : lancer d'abord python scripts/detecter.py")
    alertes = [a for a in json.loads(ALERTES.read_text(encoding="utf-8")) if a["type"] != "inhabituel"][:args.max]
    pseudo = Pseudonymiseur()
    print(f"{len(alertes)} alertes. Mode DRY-RUN : aucune action n'est exécutée.")
    for a in alertes:
        explication = expliquer_alerte(a, pseudo)
        afficher(a, explication, pseudo)
        ok = input("\n  Valider l'action ? [o/n] ").strip().lower() == "o"
        entree, _ = traiter(a, pseudo, ok, explication)
        print(f"  -> {entree['decision']}" + (" (dry-run)" if ok else ""))
    print(f"\nDécisions journalisées dans {DECISIONS}")


if __name__ == "__main__":
    main()
