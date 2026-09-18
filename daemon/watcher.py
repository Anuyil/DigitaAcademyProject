import hashlib
import logging
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import db
from core.downloader import scarica_atto
from core.pipeline import analyze_pdf

POLL_SECONDS    = int(os.getenv("POLL_SECONDS", "8"))
LLM_CALL_DELAY  = int(os.getenv("LLM_CALL_DELAY", "15"))  # secondi tra chiamate LLM
ALBO_URL        = os.getenv("ALBO_URL", "http://localhost:8001/api/atti")
OUTPUT_DIR   = os.getenv("CORRECTED_DIR", "data/corrected")
LAST_CHECK   = Path(os.getenv("LAST_CHECK_FILE", "data/last_check.txt"))
PDF_CACHE    = Path("data/albo_fake/pdf")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [DEMONE] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("watcher")


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_last_check() -> None:
    from datetime import datetime
    LAST_CHECK.parent.mkdir(parents=True, exist_ok=True)
    LAST_CHECK.write_text(datetime.utcnow().isoformat())


def _save_report(doc_id: int, result: dict) -> None:
    db.insert_report(
        document_id       = doc_id,
        verdetto          = result["verdetto"],
        gravita_max       = result.get("gravita_max"),
        findings_json     = {
            "entities":         result.get("entities", []),
            "passaggi_critici": result.get("passaggi_critici", []),
        },
        pdf_corretto_path = result.get("pdf_corretto"),
        precedente_json   = result.get("precedente"),
    )


def _prec_id(result: dict) -> str:
    p = result.get("precedente")
    return p["id_provvedimento"] if p else "—"


def poll() -> None:
    # 1. Fetch lista atti correnti dal sito finto
    try:
        resp = requests.get(ALBO_URL, timeout=10)
        resp.raise_for_status()
        atti_correnti: list[dict] = resp.json()
    except Exception as e:
        log.error(f"Impossibile contattare {ALBO_URL}: {e}")
        return

    n_visti = len(atti_correnti)
    cnt = {"nuovi": 0, "sostituiti": 0, "rimossi": 0}

    # 2. Stato corrente nel DB
    docs_db     = {d["id_atto_albo"]: d for d in db.get_all_albo_documents()}
    id_correnti = {a["id_atto_albo"] for a in atti_correnti}
    id_in_db    = set(docs_db.keys())

    # ── Rimossi ───────────────────────────────────────────────────────────────
    for id_atto in (id_in_db - id_correnti):
        doc = docs_db[id_atto]
        db.update_document(doc["id"], stato="risolto")
        db.insert_event(doc["id"], "rimosso", "Atto non più presente sull'albo")
        log.info(f"  RIMOSSO   [{id_atto}] {doc['titolo']}")
        cnt["rimossi"] += 1

    # ── Nuovi e sostituiti ────────────────────────────────────────────────────
    for atto in atti_correnti:
        id_atto = atto["id_atto_albo"]
        url_corrente = atto["url_pdf"]

        if id_atto in id_in_db:
            doc = docs_db[id_atto]
            # URL invariata → stesso file, nessun download necessario
            if url_corrente == doc["url"]:
                continue
            # URL cambiata → il file è stato sostituito, scarica il nuovo
            pdf_path = scarica_atto(url_corrente, str(PDF_CACHE))
            if pdf_path is None:
                log.warning(f"  SKIP      [{id_atto}] download fallito")
                continue
            new_hash = _hash_file(Path(pdf_path))
            # Contenuto identico nonostante URL diversa (edge case): aggiorna solo URL
            if new_hash == doc["hash"]:
                db.update_document(doc["id"], url=url_corrente, file_path=pdf_path)
                continue
            # ── SOSTITUITO ────────────────────────────────────────────────────
            try:
                result = analyze_pdf(pdf_path, OUTPUT_DIR)
            except Exception as e:
                log.error(f"  ERRORE    [{id_atto}] analyze_pdf: {e}")
                continue
            verdetto  = result["verdetto"]
            new_stato = "risolto" if verdetto == "conforme" else "in_revisione"
            db.update_document(
                doc["id"],
                hash=new_hash, url=url_corrente,
                file_path=pdf_path, stato=new_stato,
            )
            _save_report(doc["id"], result)
            db.insert_event(doc["id"], "sostituito", f"Nuovo verdetto: {verdetto}")
            log.info(
                f"  SOSTIT.   [{id_atto}] {atto['titolo']}"
                f" → {verdetto} | precedente: {_prec_id(result)}"
            )
            cnt["sostituiti"] += 1
            if LLM_CALL_DELAY > 0:
                log.info(f"  ⏳ delay {LLM_CALL_DELAY}s (rate limit LLM)")
                time.sleep(LLM_CALL_DELAY)

        else:
            # ── NUOVO: scarica, calcola hash, analizza ────────────────────────
            pdf_path = scarica_atto(url_corrente, str(PDF_CACHE))
            if pdf_path is None:
                log.warning(f"  SKIP      [{id_atto}] download fallito")
                continue
            new_hash = _hash_file(Path(pdf_path))
            try:
                result = analyze_pdf(pdf_path, OUTPUT_DIR)
            except Exception as e:
                log.error(f"  ERRORE    [{id_atto}] analyze_pdf: {e}")
                continue
            verdetto = result["verdetto"]
            stato    = "risolto" if verdetto == "conforme" else "nuovo"
            doc_id   = db.insert_document(
                source             = "albo",
                titolo             = atto.get("titolo", ""),
                url                = url_corrente,
                id_atto_albo       = id_atto,
                file_path          = pdf_path,
                hash               = new_hash,
                data_pubblicazione = atto.get("data_pubblicazione"),
                stato              = stato,
            )
            _save_report(doc_id, result)
            db.insert_event(doc_id, "nuovo", f"Verdetto: {verdetto}")
            log.info(
                f"  NUOVO     [{id_atto}] {atto['titolo']}"
                f" → {verdetto} | precedente: {_prec_id(result)}"
            )
            cnt["nuovi"] += 1
            if LLM_CALL_DELAY > 0:
                log.info(f"  ⏳ delay {LLM_CALL_DELAY}s (rate limit LLM)")
                time.sleep(LLM_CALL_DELAY)

    # 3. Pulizia report scaduti + file su disco
    paths = db.delete_expired_reports()
    for p in paths:
        try:
            Path(p).unlink(missing_ok=True)
        except Exception:
            pass
    if paths:
        log.info(f"  CLEANUP   {len(paths)} report scaduti rimossi")

    # 4. Timestamp ultimo controllo (letto dalla dashboard)
    _write_last_check()

    # 5. Riepilogo ciclo
    log.info(
        f"── visti={n_visti} "
        f"nuovi={cnt['nuovi']} "
        f"sostituiti={cnt['sostituiti']} "
        f"rimossi={cnt['rimossi']} ──"
    )


def main() -> None:
    db.init_db()
    log.info(f"Demone avviato — polling ogni {POLL_SECONDS}s → {ALBO_URL}")
    while True:
        try:
            poll()
        except Exception as e:
            log.exception(f"Errore inatteso nel ciclo: {e}")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
