import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent
_SCHEDE_PATH = _ROOT / os.getenv("SCHEDE_PATH", "data/schede_provvedimenti.json")

_schede: list[dict] | None = None


def _load() -> list[dict]:
    global _schede
    if _schede is None:
        _schede = json.loads(_SCHEDE_PATH.read_text(encoding="utf-8"))
    return _schede


def find_precedent(categoria: str | None, tipo_atto: str | None) -> dict | None:
    """
    Filtra schede_provvedimenti.json per categoria_violazione.
    Preferisce un match anche su tipo_atto; altrimenti restituisce
    il primo match sulla sola categoria.
    Ritorna None se categoria è None o non viene trovato nulla.
    """
    if not categoria:
        return None

    schede = _load()
    per_categoria = [
        s for s in schede if s.get("categoria_violazione") == categoria
    ]
    if not per_categoria:
        return None

    if tipo_atto:
        exact = [s for s in per_categoria if s.get("tipo_atto") == tipo_atto]
        if exact:
            return exact[0]

    return per_categoria[0]


# ── smoke test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cases = [
        ("salute",           "determina_dirigenziale"),
        ("salute",           "ordinanza"),
        ("disagio_economico","determina_dirigenziale"),
        ("minori",           "ordinanza"),
        ("giudiziario",      "ordinanza"),
        ("giudiziario",      "determina_dirigenziale"),
        ("dati_economici",   "determina_dirigenziale"),
        (None,               "delibera"),
        ("salute",           None),
        ("inesistente",      "delibera"),
    ]
    for cat, tipo in cases:
        result = find_precedent(cat, tipo)
        if result:
            print(
                f"  [{cat} / {tipo}] → {result['id_provvedimento']}"
                f"  (tipo={result['tipo_atto']}, cat={result['categoria_violazione']})"
            )
        else:
            print(f"  [{cat} / {tipo}] → None")
