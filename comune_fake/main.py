import json
import os
import shutil
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

load_dotenv()

_ROOT        = Path(__file__).parent.parent
_ALBO_DIR    = _ROOT / "data" / "albo_fake"
_PDF_DIR     = _ALBO_DIR / "pdf"
_ATTI_JSON   = _ALBO_DIR / "atti.json"
_DATA_DIR    = _ROOT / "data"
_LABELS_PATH = _ROOT / os.getenv("LABELS_PATH", "data/labels.json")

HOST = "http://localhost:8001"

# Atti pubblicati automaticamente all'avvio (mix conforme + 2 categorie diverse)
_SEED = [
    "graduatoria_concorso_01.pdf",        # conforme
    "determina_contributo_salute_03.pdf", # non_conforme / salute
    "determina_sussidio_disagio_04.pdf",  # non_conforme / disagio_economico
    "atto_vicenda_giudiziaria_07.pdf",    # non_conforme / giudiziario
]


# ── helpers ──────────────────────────────────────────────────────────────────

def _load_atti() -> list[dict]:
    if not _ATTI_JSON.exists():
        return []
    return json.loads(_ATTI_JSON.read_text(encoding="utf-8"))


def _save_atti(atti: list[dict]) -> None:
    _ALBO_DIR.mkdir(parents=True, exist_ok=True)
    _ATTI_JSON.write_text(json.dumps(atti, indent=2, ensure_ascii=False))


def _next_id(atti: list[dict]) -> str:
    nums = []
    for a in atti:
        try:
            nums.append(int(a["id_atto_albo"]))
        except (ValueError, KeyError):
            pass
    return str(max(nums, default=0) + 1).zfill(3)


def _fname_to_titolo(fname: str) -> str:
    return Path(fname).stem.replace("_", " ").title()


def _dataset_pdfs() -> list[str]:
    return sorted(p.name for p in _DATA_DIR.glob("*.pdf"))


def _seed() -> None:
    """Pubblica atti iniziali solo se atti.json è vuoto/assente."""
    atti = _load_atti()
    if atti:
        return

    _PDF_DIR.mkdir(parents=True, exist_ok=True)
    labels_map: dict[str, dict] = {}
    if _LABELS_PATH.exists():
        for e in json.loads(_LABELS_PATH.read_text(encoding="utf-8")):
            labels_map[e["file"]] = e

    for fname in _SEED:
        src = _DATA_DIR / fname
        if not src.exists():
            print(f"[comune_fake] seed: file mancante {src}, skip")
            continue
        id_atto   = _next_id(atti)
        dest_name = f"{id_atto}_{fname}"
        shutil.copy2(str(src), str(_PDF_DIR / dest_name))
        label = labels_map.get(fname, {})
        atti.append({
            "id_atto_albo":      id_atto,
            "titolo":            _fname_to_titolo(fname),
            "tipo_atto":         label.get("tipo_atto", "altro"),
            "url_pdf":           f"{HOST}/albo_fake/{dest_name}",
            "data_pubblicazione": date.today().isoformat(),
        })

    _save_atti(atti)
    print(f"[comune_fake] seed: {len(atti)} atti pubblicati")


# ── lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    _seed()
    yield


app = FastAPI(title="Comune di Borgo Vesuviano — Albo Pretorio", lifespan=lifespan)


# ── pagina HTML pubblica ─────────────────────────────────────────────────────

@app.get("/albo", response_class=HTMLResponse)
def albo_html():
    atti = _load_atti()
    rows = ""
    for i, a in enumerate(atti, 1):
        scadenza = ""
        try:
            from datetime import datetime, timedelta
            pub = datetime.fromisoformat(a["data_pubblicazione"])
            scadenza = (pub + timedelta(days=15)).date().isoformat()
        except Exception:
            pass
        rows += (
            f"<tr>"
            f"<td>{i}</td>"
            f"<td>{a['titolo']}</td>"
            f"<td>{a['tipo_atto']}</td>"
            f"<td>{a['data_pubblicazione']}</td>"
            f"<td>{scadenza}</td>"
            f"<td><a href=\"{a['url_pdf']}\">PDF</a></td>"
            f"</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Albo Pretorio — Comune di Borgo Vesuviano</title>
  <style>
    body {{ font-family: Georgia, serif; margin: 0; background: #f5f5f0; color: #222; }}
    header {{ background: #003366; color: white; padding: 1rem 2rem; }}
    header h1 {{ margin: 0; font-size: 1.3rem; }}
    header p  {{ margin: .2rem 0 0; font-size: .85rem; opacity: .8; }}
    main  {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
    table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 4px #0002; }}
    th    {{ background: #003366; color: white; padding: .6rem .8rem; text-align: left; font-size: .85rem; }}
    td    {{ padding: .55rem .8rem; border-bottom: 1px solid #ddd; font-size: .9rem; }}
    tr:hover td {{ background: #f0f4ff; }}
    a     {{ color: #003366; }}
    footer {{ text-align: center; font-size: .75rem; color: #888; margin: 2rem 0; }}
  </style>
</head>
<body>
<header>
  <h1>Comune di Borgo Vesuviano</h1>
  <p>Albo Pretorio Online — Pubblicazioni correnti</p>
</header>
<main>
  <h2 style="font-size:1.1rem;margin-bottom:.8rem">Atti pubblicati ({len(atti)})</h2>
  <table>
    <thead>
      <tr>
        <th>#</th><th>Oggetto</th><th>Tipo</th>
        <th>Data pubbl.</th><th>Scadenza</th><th>PDF</th>
      </tr>
    </thead>
    <tbody>{rows if rows else '<tr><td colspan="6" style="text-align:center;color:#888">Nessun atto pubblicato</td></tr>'}</tbody>
  </table>
</main>
<footer>Simulazione a scopo dimostrativo — nessun dato reale</footer>
</body>
</html>"""


# ── API JSON per il demone ────────────────────────────────────────────────────

@app.get("/api/atti")
def api_atti():
    return _load_atti()


# ── serve PDF statici ─────────────────────────────────────────────────────────

@app.get("/albo_fake/{filename}")
def serve_pdf(filename: str):
    path = _PDF_DIR / filename
    if not path.exists():
        raise HTTPException(404, f"File non trovato: {filename}")
    return FileResponse(str(path), media_type="application/pdf")


# ── admin ─────────────────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    atti   = _load_atti()
    pdfs   = _dataset_pdfs()

    righe_atti = ""
    for a in atti:
        righe_atti += (
            f"<tr>"
            f"<td>{a['id_atto_albo']}</td>"
            f"<td>{a['titolo']}</td>"
            f"<td>{a['tipo_atto']}</td>"
            f"<td>{a['data_pubblicazione']}</td>"
            f"<td>"
            f"<form method='post' action='/admin/rimuovi/{a['id_atto_albo']}' style='display:inline'>"
            f"<button style='color:red;background:none;border:none;cursor:pointer;font-size:.9rem'>✕ Rimuovi</button>"
            f"</form>"
            f"</td>"
            f"</tr>"
        )

    opts_pdf = "".join(f"<option value='{p}'>{p}</option>" for p in pdfs)
    opts_tipo = "".join(
        f"<option value='{t}'>{t}</option>"
        for t in ["determina_dirigenziale","delibera","ordinanza","graduatoria","altro"]
    )

    return f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Admin — Comune di Borgo Vesuviano</title>
  <style>
    body  {{ font-family: sans-serif; margin: 2rem; background: #fafafa; }}
    h1    {{ color: #003366; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
    th    {{ background: #003366; color: white; padding: .5rem .8rem; text-align:left; }}
    td    {{ padding: .45rem .8rem; border-bottom: 1px solid #ddd; }}
    fieldset {{ border: 1px solid #ccc; padding: 1rem; margin-bottom: 1rem; max-width: 520px; }}
    label {{ display:block; margin:.4rem 0 .1rem; font-size:.9rem; }}
    input,select {{ width:100%; padding:.35rem; box-sizing:border-box; }}
    button[type=submit] {{ margin-top:.8rem; padding:.45rem 1.2rem;
                           background:#003366; color:white; border:none;
                           cursor:pointer; border-radius:3px; }}
  </style>
</head>
<body>
<h1>Admin — Albo Pretorio</h1>

<h2>Atti correnti</h2>
<table>
  <thead><tr><th>ID</th><th>Titolo</th><th>Tipo</th><th>Data</th><th></th></tr></thead>
  <tbody>{righe_atti if righe_atti else '<tr><td colspan="5">Nessun atto</td></tr>'}</tbody>
</table>

<h2>Pubblica nuovo atto</h2>
<form method="post" action="/admin/pubblica" enctype="multipart/form-data">
  <fieldset>
    <legend>Seleziona sorgente PDF</legend>
    <label>PDF dal dataset (dropdown)
      <select name="pdf_dataset">{opts_pdf}</select>
    </label>
    <label style="margin-top:.6rem">— oppure upload libero (sovrascrive la selezione sopra)
      <input type="file" name="pdf_upload" accept=".pdf">
    </label>
  </fieldset>
  <fieldset>
    <legend>Metadati</legend>
    <label>Titolo <input type="text" name="titolo" required></label>
    <label>Tipo atto <select name="tipo_atto">{opts_tipo}</select></label>
  </fieldset>
  <button type="submit">Pubblica</button>
</form>
</body>
</html>"""


@app.post("/admin/pubblica", response_class=HTMLResponse)
async def admin_pubblica(
    titolo: str       = Form(...),
    tipo_atto: str    = Form("altro"),
    pdf_dataset: str  = Form(""),
    pdf_upload: UploadFile | None = File(None),
):
    _PDF_DIR.mkdir(parents=True, exist_ok=True)
    atti = _load_atti()
    id_atto = _next_id(atti)

    # Determina sorgente: upload > dropdown
    if pdf_upload and pdf_upload.filename:
        content = await pdf_upload.read()
        fname   = f"{id_atto}_{pdf_upload.filename}"
        (_PDF_DIR / fname).write_bytes(content)
    elif pdf_dataset:
        src   = _DATA_DIR / pdf_dataset
        if not src.exists():
            raise HTTPException(400, f"File non trovato nel dataset: {pdf_dataset}")
        fname = f"{id_atto}_{pdf_dataset}"
        shutil.copy2(str(src), str(_PDF_DIR / fname))
    else:
        raise HTTPException(400, "Nessun PDF selezionato")

    atti.append({
        "id_atto_albo":      id_atto,
        "titolo":            titolo,
        "tipo_atto":         tipo_atto,
        "url_pdf":           f"{HOST}/albo_fake/{fname}",
        "data_pubblicazione": date.today().isoformat(),
    })
    _save_atti(atti)

    return f"""<html><body>
<p>✓ Atto <strong>{id_atto}</strong> pubblicato.</p>
<p><a href="/admin">← Torna all'admin</a> &nbsp;|&nbsp; <a href="/albo">Vedi albo</a></p>
</body></html>"""


@app.post("/admin/rimuovi/{id_atto_albo}", response_class=HTMLResponse)
def admin_rimuovi(id_atto_albo: str):
    atti     = _load_atti()
    new_atti = [a for a in atti if a["id_atto_albo"] != id_atto_albo]
    if len(new_atti) == len(atti):
        raise HTTPException(404, f"Atto {id_atto_albo} non trovato")
    _save_atti(new_atti)
    return f"""<html><body>
<p>✓ Atto <strong>{id_atto_albo}</strong> rimosso.</p>
<p><a href="/admin">← Torna all'admin</a></p>
</body></html>"""
