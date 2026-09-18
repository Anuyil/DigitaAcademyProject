"""
core/pipeline.py — motore di analisi PDF.

Catena:
  extract_text → pseudonymize → _guess_categoria+tipo → find_precedent
  → llm.analyze → redact_pdf → ritorna risultato strutturato

Usato sia dall'upload (web/main.py) che dal demone (daemon/watcher.py).
"""

import hashlib
import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

# ── euristiche per stimare categoria e tipo_atto prima della chiamata LLM ────
# (servono a find_precedent che va chiamato PRIMA dell'LLM)

_CATEGORIA_KEYWORDS: list[tuple[str, list[str]]] = [
    ("salute",           ["patolog", "malattia", "diagnosi", "infermit", "invalidi",
                          "disabilit", "medic", "oncolog", "cardiopatia", "terapia",
                          "handicap", "L. 104", "TSO"]),
    ("minori",           ["minore", "bambino", "figlio", "affidamento", "adozione",
                          "tutela", "Tribunale per i Minorenni", "nucleo familiare"]),
    ("giudiziario",      ["penale", "reato", "indagat", "procedimento penale",
                          "Procura", "G.I.P.", "misura cautelare", "sequestro",
                          "peculato", "querela", "sospensione dal", "interdittiva"]),
    ("disagio_economico",["ISEE", "sussidio", "buono spesa", "morosit", "poverta",
                          "disagio", "disoccupazione", "indigenza", "sfratto"]),
    ("dati_economici",   ["IBAN", "compenso", "parcella", "liquidazione", "pignoramento",
                          "rimborso spese", "coordinate bancarie"]),
]

_TIPO_KEYWORDS: list[tuple[str, list[str]]] = [
    ("determina_dirigenziale", ["determin", "determinazione dirigenziale"]),
    ("delibera",               ["delibera", "deliberazione"]),
    ("ordinanza",              ["ordinanza", "sindacale"]),
    ("graduatoria",            ["graduatoria", "concorso"]),
]

_GRAVITA_ORDER = {"alta": 2, "media": 1, "bassa": 0}


def _guess_categoria(testo: str) -> str | None:
    testo_lower = testo.lower()
    for categoria, keywords in _CATEGORIA_KEYWORDS:
        if any(k.lower() in testo_lower for k in keywords):
            return categoria
    return None


def _guess_tipo_atto(testo: str) -> str:
    testo_lower = testo.lower()
    for tipo, keywords in _TIPO_KEYWORDS:
        if any(k.lower() in testo_lower for k in keywords):
            return tipo
    return "altro"


def _gravita_max(passaggi: list[dict]) -> str | None:
    if not passaggi:
        return None
    return max(passaggi, key=lambda p: _GRAVITA_ORDER.get(p.get("gravita", "bassa"), 0))["gravita"]


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ── pipeline principale ───────────────────────────────────────────────────────

def analyze_pdf(pdf_path: str, output_dir: str) -> dict:
    """
    Analizza un PDF e ritorna il risultato strutturato.

    Returns:
        {
          "file": str, "hash": str,
          "verdetto": "conforme"|"non_conforme"|"da_verificare",
          "gravita_max": str | None,
          "entities": [{"placeholder","type","value"(mascherato),"start","end"}],
          "decisioni": [{"placeholder","azione","motivazione","norma"}],
          "passaggi_critici": [{"testo","categoria","gravita","motivazione","norma"}],
          "precedente": dict | None,
          "pdf_corretto": str,
        }
    """
    from core.detectors import pseudonymize, mask as mask_value
    from core.precedents import find_precedent
    from core.pdf_utils import extract_text, redact_pdf
    from core import llm

    pdf_path = Path(pdf_path)
    file_name = pdf_path.name
    file_hash = _hash_file(pdf_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log.info(f"Analisi: {file_name}")

    # 1. Estrazione testo
    try:
        testo = extract_text(str(pdf_path))
    except Exception as e:
        log.error(f"Estrazione testo fallita: {e}")
        return _error_result(file_name, file_hash, str(pdf_path), str(e))

    # 2. Pseudonimizzazione
    pseudo = pseudonymize(testo)
    pseudo_text = pseudo["pseudo_text"]
    mapping     = pseudo["mapping"]          # {[PERSONA_1]: "Mario Rossi", ...}
    entities_raw = pseudo["entities"]

    # Maschera i valori reali nelle entità prima di salvarle nel DB
    entities = [
        {**e, "value": mask_value(e["value"])}
        for e in entities_raw
    ]

    log.info(f"  Entità trovate: {len(entities)} — "
             f"CF:{sum(1 for e in entities_raw if e['type']=='CF')} "
             f"IBAN:{sum(1 for e in entities_raw if e['type']=='IBAN')} "
             f"PER:{sum(1 for e in entities_raw if e['type']=='PER')}")

    # 3. Stima categoria e tipo per find_precedent (pre-LLM)
    categoria_guess = _guess_categoria(testo)
    tipo_guess      = _guess_tipo_atto(testo)
    precedente      = find_precedent(categoria_guess, tipo_guess)

    if precedente:
        log.info(f"  Precedente trovato: {precedente['id_provvedimento']}")
    else:
        log.info("  Nessun precedente trovato")

    # 4. Analisi LLM (pseudo_text + precedente — MAI testo originale)
    llm_result = llm.analyze(pseudo_text, precedente=precedente)

    verdetto        = llm_result.get("verdetto", "da_verificare")
    decisioni       = llm_result.get("decisioni", [])
    passaggi        = llm_result.get("passaggi_critici", [])
    tipo_atto_llm   = llm_result.get("tipo_atto", tipo_guess)

    # Aggiorna il precedente con tipo_atto reale se l'LLM ha classificato diversamente
    if tipo_atto_llm != tipo_guess:
        precedente_aggiornato = find_precedent(categoria_guess, tipo_atto_llm)
        if precedente_aggiornato:
            precedente = precedente_aggiornato

    log.info(f"  LLM → verdetto={verdetto} | tipo={tipo_atto_llm} | "
             f"passaggi={len(passaggi)} | decisioni={len(decisioni)}")

    # 5. Redazione PDF — bande nere solo sui dati flaggati dall'LLM
    output_path = str(Path(output_dir) / f"oscurato_{file_name}")
    try:
        pdf_corretto_path = redact_pdf(
            pdf_path         = str(pdf_path),
            output_path      = output_path,
            mapping          = mapping,
            decisioni        = decisioni,
            passaggi_critici = passaggi,
        )
    except Exception as e:
        log.error(f"Redazione fallita: {e}")
        pdf_corretto_path = str(pdf_path)  # fallback: path originale

    return {
        "file":             file_name,
        "hash":             file_hash,
        "verdetto":         verdetto,
        "gravita_max":      _gravita_max(passaggi),
        "entities":         entities,
        "decisioni":        decisioni,
        "passaggi_critici": passaggi,
        "precedente":       precedente,
        "pdf_corretto":     pdf_corretto_path,
    }


def _error_result(file_name: str, file_hash: str, pdf_path: str, msg: str) -> dict:
    return {
        "file": file_name, "hash": file_hash,
        "verdetto": "da_verificare", "gravita_max": None,
        "entities": [], "decisioni": [],
        "passaggi_critici": [{"testo": f"Errore: {msg}", "categoria": "altro",
                               "gravita": "bassa", "motivazione": "", "norma": ""}],
        "precedente": None, "pdf_corretto": pdf_path,
    }


# ── smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    _ROOT   = Path(__file__).parent.parent
    out_dir = str(_ROOT / "data" / "corrected")

    tests = [
        ("data/graduatoria_concorso_01.pdf",                    "conforme",      "graduatoria conforme"),
        ("data/01_determina_spese_legali_salute_iban.pdf",       "non_conforme",  "salute+iban"),
        ("data/03_determina_sospensione_procedimento_penale.pdf","non_conforme",  "giudiziario"),
    ]

    print("═" * 60)
    print("  Pipeline reale — smoke test")
    print("═" * 60)

    for pdf_rel, expected, note in tests:
        pdf_path = _ROOT / pdf_rel
        if not pdf_path.exists():
            print(f"  SKIP (mancante): {pdf_rel}")
            continue

        print(f"\n▶ {pdf_path.name}  [{note}]")
        result = analyze_pdf(str(pdf_path), out_dir)

        icon = "✓" if result["verdetto"] == expected else "✗"
        prec = (result["precedente"] or {}).get("id_provvedimento", "—")
        print(f"  {icon} verdetto={result['verdetto']} (atteso={expected})")
        print(f"    hash={result['hash'][:16]}...")
        print(f"    entità={len(result['entities'])} | passaggi={len(result['passaggi_critici'])}")
        print(f"    precedente={prec}")
        print(f"    gravita_max={result['gravita_max']}")
        print(f"    pdf_corretto={Path(result['pdf_corretto']).name}")
        for p in result["passaggi_critici"][:2]:
            print(f"    [{p.get('gravita','?')}] {p['testo'][:65]}…")

    print("\n" + "═" * 30)
