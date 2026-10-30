"""Pseudonymisation des identifiants avant tout envoi au LLM.

CAPT-012 -> CAPTEUR_xxxxxx, GW-B -> GW_xxxxxx, BAT-A-E1 -> ZONE_xxxxxx,
où xxxxxx = HMAC-SHA256(PSEUDO_KEY, identifiant) tronqué. Sans la clé, on ne
peut pas retrouver l'identifiant réel ; avec la clé, le pseudonyme est stable.
La table inverse reste côté code (affichage opérateur), jamais envoyée au LLM.
Usage : python scripts/pseudo.py '{"capteur": "CAPT-012", "zone": "BAT-A-E1"}'
"""
import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path

MOTIFS = {
    "CAPTEUR": re.compile(r"\bCAPT-\d{3}\b"),
    "GW": re.compile(r"\bGW-[A-Z]\b"),
    "ZONE": re.compile(r"\bBAT-[A-Z]-E\d\b"),
}


def charger_cle():
    """Lit PSEUDO_KEY dans l'environnement, sinon dans le .env du dépôt."""
    cle = os.environ.get("PSEUDO_KEY")
    env = Path(__file__).resolve().parent.parent / ".env"
    if not cle and env.exists():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("PSEUDO_KEY="):
                cle = ligne.split("=", 1)[1].strip()
    if not cle or cle == "change-me":
        raise SystemExit("PSEUDO_KEY absente ou par défaut : la définir dans .env")
    return cle.encode()


class Pseudonymiseur:
    def __init__(self, cle=None):
        self.cle = cle or charger_cle()
        self.inverse = {}

    def pseudo(self, prefixe, ident):
        h = hmac.new(self.cle, ident.encode(), hashlib.sha256).hexdigest()[:6]
        p = f"{prefixe}_{h}"
        self.inverse[p] = ident
        return p

    def texte(self, s):
        """Remplace tous les identifiants trouvés dans une chaîne."""
        for prefixe, motif in MOTIFS.items():
            s = motif.sub(lambda m, p=prefixe: self.pseudo(p, m.group()), s)
        return s

    def objet(self, o):
        """Parcourt dict / liste / chaîne (une alerte JSON par exemple)."""
        if isinstance(o, dict):
            return {k: self.objet(v) for k, v in o.items()}
        if isinstance(o, list):
            return [self.objet(v) for v in o]
        if isinstance(o, str):
            return self.texte(o)
        return o

    def reveler(self, s):
        """Remet les vrais identifiants (pour l'affichage opérateur)."""
        for p, ident in self.inverse.items():
            s = s.replace(p, ident)
        return s


if __name__ == "__main__":
    alerte = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "capteur": "CAPT-012", "passerelle": "GW-B", "zone": "BAT-A-E3",
        "preuves": ["CAPT-012 figé depuis 6 h, voisins de BAT-A-E3 normaux"],
    }
    print(json.dumps(Pseudonymiseur().objet(alerte), ensure_ascii=False, indent=2))
