"""RAG : découpe docs_rt/, calcule les embeddings et retrouve les passages utiles.

Usage : python scripts/rag.py indexer
        python scripts/rag.py chercher "CAPT-012 figé depuis 6 h"
"""
import json
import sys

import numpy as np
import requests

from config import EMBED_MODEL, OLLAMA_HOST, RACINE

DOCS = RACINE / "docs_rt"
INDEX = RACINE / "rag" / "embeddings.json"
TAILLE_MAX = 700
NB_PASSAGES = 3
_cache = None


def decouper(texte):
    """Une section « ## » par passage ; une section trop longue est coupée par paragraphes."""
    titre, *sections = texte.split("\n## ")
    titre = titre.splitlines()[0].lstrip("# ").strip()
    intro = "\n".join(texte.split("\n## ")[0].splitlines()[1:]).strip()
    morceaux = [intro] if intro else []
    for s in sections:
        s = "## " + s.strip()
        if len(s) <= TAILLE_MAX:
            morceaux.append(s)
            continue
        courant = ""
        for para in s.split("\n\n"):
            if courant and len(courant) + len(para) > TAILLE_MAX:
                morceaux.append(courant)
                courant = ""
            courant = f"{courant}\n\n{para}" if courant else para
        morceaux.append(courant)
    return titre, morceaux


def embed(textes):
    r = requests.post(f"{OLLAMA_HOST}/api/embed", json={"model": EMBED_MODEL, "input": textes}, timeout=300)
    r.raise_for_status()
    return r.json()["embeddings"]


def indexer():
    passages = []
    for doc in sorted(DOCS.glob("RT-*.md")):
        titre, morceaux = decouper(doc.read_text(encoding="utf-8"))
        for i, m in enumerate(morceaux, 1):
            passages.append({"id": f"{doc.name[:5]}-{i}", "source": doc.name[:5], "titre": titre, "texte": m})
    # nomic-embed-text attend un préfixe qui distingue documents et questions.
    vecteurs = embed([f"search_document: {p['titre']}\n{p['texte']}" for p in passages])
    for p, v in zip(passages, vecteurs):
        p["embedding"] = v
    INDEX.parent.mkdir(exist_ok=True)
    INDEX.write_text(json.dumps(passages, ensure_ascii=False), encoding="utf-8")
    return passages


def chercher(question, k=NB_PASSAGES):
    """Renvoie les k passages les plus proches : liste de (similarité cosinus, passage)."""
    global _cache
    if _cache is None:
        if not INDEX.exists():
            indexer()
        passages = json.loads(INDEX.read_text(encoding="utf-8"))
        m = np.array([p["embedding"] for p in passages])
        _cache = passages, m / np.linalg.norm(m, axis=1, keepdims=True)
    passages, m = _cache
    q = np.array(embed([f"search_query: {question}"])[0])
    scores = m @ (q / np.linalg.norm(q))
    return [(float(scores[i]), passages[i]) for i in np.argsort(-scores)[:k]]


if __name__ == "__main__":
    if sys.argv[1:2] == ["indexer"]:
        p = indexer()
        print(f"{len(p)} passages indexés depuis {len(set(x['source'] for x in p))} documents -> {INDEX}")
    elif sys.argv[1:2] == ["chercher"] and len(sys.argv) > 2:
        for score, p in chercher(" ".join(sys.argv[2:])):
            print(f"{score:.3f}  {p['id']}  {p['titre']}\n       {p['texte'][:120]!r}")
    else:
        print(__doc__)
