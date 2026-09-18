import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import db
from core.pipeline import analyze_pdf

_ROOT        = Path(__file__).parent.parent
_UPLOAD_DIR  = _ROOT / "data" / "uploads"
_CORRECT_DIR = _ROOT / "data" / "corrected"
_LAST_CHECK  = _ROOT / "data" / "last_check.txt"

app = FastAPI(title="Albo Sicuro")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_findings(row: dict) -> tuple[list, list, list]:
    """Estrae entities, passaggi_critici, decisioni dal findings_json."""
    raw = row.get("findings_json") or "{}"
    if isinstance(raw, str):
        data = json.loads(raw)
    else:
        data = raw or {}
    return (
        data.get("entities", []),
        data.get("passaggi_critici", []),
        data.get("decisioni", []),
    )


def _parse_precedente(row: dict) -> dict | None:
    raw = row.get("precedente_json")
    if not raw:
        return None
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


# ── dashboard ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    db.init_db()
    documents = db.get_all_documents()
    stats     = db.get_stats()
    last_check = _LAST_CHECK.read_text().strip()[:19] if _LAST_CHECK.exists() else None
    return templates.TemplateResponse(request, "dashboard.html", {
        "documents":  documents,
        "stats":      stats,
        "last_check": last_check,
    })


@app.get("/api/stato")
def api_stato():
    db.init_db()
    last_check = _LAST_CHECK.read_text().strip() if _LAST_CHECK.exists() else None
    return {"last_check": last_check, "stats": db.get_stats()}


# ── upload ────────────────────────────────────────────────────────────────────

@app.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request):
    return templates.TemplateResponse(request, "upload.html", {})


@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    titolo: str = Form(""),
):
    db.init_db()
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    _CORRECT_DIR.mkdir(parents=True, exist_ok=True)

    # Salva il file
    safe_name = Path(file.filename).name
    uid       = str(uuid.uuid4())[:8]
    dest      = _UPLOAD_DIR / f"{uid}_{safe_name}"
    dest.write_bytes(await file.read())

    # Analisi
    try:
        result = analyze_pdf(str(dest), str(_CORRECT_DIR))
    except Exception as e:
        return templates.TemplateResponse(request, "upload.html", {
            "error": f"Errore durante l'analisi: {e}",
        }, status_code=500)

    # Salva nel DB
    titolo_finale = titolo.strip() or Path(safe_name).stem.replace("_", " ").title()
    doc_id = db.insert_document(
        source    = "upload",
        titolo    = titolo_finale,
        file_path = str(dest),
        hash      = result["hash"],
        stato     = "risolto" if result["verdetto"] == "conforme" else "nuovo",
    )
    db.insert_report(
        document_id       = doc_id,
        verdetto          = result["verdetto"],
        gravita_max       = result.get("gravita_max"),
        findings_json     = {
            "entities":         result.get("entities", []),
            "passaggi_critici": result.get("passaggi_critici", []),
            "decisioni":        result.get("decisioni", []),
        },
        pdf_corretto_path = result.get("pdf_corretto"),
        precedente_json   = result.get("precedente"),
    )
    db.insert_event(doc_id, "upload", f"Caricato manualmente — verdetto: {result['verdetto']}")

    return RedirectResponse(f"/report/{doc_id}", status_code=303)


# ── report dettaglio ──────────────────────────────────────────────────────────

@app.get("/report/{doc_id}", response_class=HTMLResponse)
def report_detail(request: Request, doc_id: int):
    db.init_db()
    row = db.get_document_with_report(doc_id)
    if not row:
        raise HTTPException(404, "Documento non trovato")

    entities, passaggi, decisioni = _parse_findings(row)
    precedente = _parse_precedente(row)

    return templates.TemplateResponse(request, "report.html", {
        "doc":        row,
        "entities":   entities,
        "passaggi":   passaggi,
        "decisioni":  decisioni,
        "precedente": precedente,
        "has_original":  bool(row.get("file_path") and Path(row["file_path"]).exists()),
        "has_oscurato":  bool(row.get("pdf_corretto_path") and Path(row["pdf_corretto_path"]).exists()),
    })


# ── serve PDF ─────────────────────────────────────────────────────────────────

@app.get("/pdf/originale/{doc_id}")
def serve_original(doc_id: int):
    db.init_db()
    doc = db.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(404)
    path = Path(doc["file_path"] or "")
    if not path.exists():
        raise HTTPException(404, "File originale non trovato")
    return FileResponse(str(path), media_type="application/pdf",
                        headers={"Content-Disposition": "inline"})


@app.get("/pdf/oscurato/{doc_id}")
def serve_oscurato(doc_id: int):
    db.init_db()
    row = db.get_report_by_document(doc_id)
    if not row:
        raise HTTPException(404)
    path = Path(row.get("pdf_corretto_path") or "")
    if not path.exists():
        raise HTTPException(404, "PDF oscurato non trovato")
    return FileResponse(str(path), media_type="application/pdf",
                        headers={"Content-Disposition": "inline"})
