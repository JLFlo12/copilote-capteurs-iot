"""Configuration : lue dans l'environnement, sinon dans le .env du dépôt (jamais commité)."""
import os
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def _lire_fichier():
    valeurs = {}
    env = RACINE / ".env"
    if env.exists():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#") and "=" in ligne:
                cle, valeur = ligne.split("=", 1)
                valeurs[cle.strip()] = valeur.strip()
    return valeurs


_FICHIER = _lire_fichier()


def lire(nom, defaut=None):
    return os.environ.get(nom, _FICHIER.get(nom, defaut))


OLLAMA_HOST = lire("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = lire("OLLAMA_MODEL", "llama3.2:3b")
EMBED_MODEL = lire("EMBED_MODEL", "nomic-embed-text")
DRY_RUN = lire("DRY_RUN", "true").lower() != "false"
