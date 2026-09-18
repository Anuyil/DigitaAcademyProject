import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_ROOT = Path(__file__).parent.parent
DB_PATH = _ROOT / os.getenv("DB_PATH", "data/albo_sicuro.db")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "10"))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    source           TEXT NOT NULL CHECK(source IN ('upload', 'albo')),
    titolo           TEXT,
    url              TEXT,
    id_atto_albo     TEXT,
    file_path        TEXT,
    hash             TEXT,
    data_pubblicazione TEXT,
    stato            TEXT NOT NULL DEFAULT 'nuovo'
                     CHECK(stato IN ('nuovo','in_revisione','corretto','risolto','falso_positivo')),
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reports (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id         INTEGER NOT NULL REFERENCES documents(id),
    verdetto            TEXT NOT NULL,
    gravita_max         TEXT,
    findings_json       TEXT,
    pseudo_text         TEXT,
    llm_json            TEXT,
    precedente_json     TEXT,
    pdf_corretto_path   TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    tipo        TEXT NOT NULL,
    descrizione TEXT,
    timestamp   TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)


# ── documents ────────────────────────────────────────────────────────────────

def insert_document(
    source: str,
    titolo: str = None,
    url: str = None,
    id_atto_albo: str = None,
    file_path: str = None,
    hash: str = None,
    data_pubblicazione: str = None,
    stato: str = "nuovo",
) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO documents
               (source, titolo, url, id_atto_albo, file_path, hash,
                data_pubblicazione, stato)
               VALUES (?,?,?,?,?,?,?,?)""",
            (source, titolo, url, id_atto_albo, file_path, hash,
             data_pubblicazione, stato),
        )
        return cur.lastrowid


def update_document(doc_id: int, **kwargs) -> None:
    if not kwargs:
        return
    cols = ", ".join(f"{k}=?" for k in kwargs)
    with _connect() as conn:
        conn.execute(
            f"UPDATE documents SET {cols} WHERE id=?",
            (*kwargs.values(), doc_id),
        )


def get_document_by_id(doc_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE id=?", (doc_id,)
        ).fetchone()
        return dict(row) if row else None


def get_document_by_atto(id_atto_albo: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            """SELECT * FROM documents
               WHERE id_atto_albo=? AND source='albo'
               ORDER BY id DESC LIMIT 1""",
            (id_atto_albo,),
        ).fetchone()
        return dict(row) if row else None


def get_all_albo_documents() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM documents WHERE source='albo' ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


# ── reports ──────────────────────────────────────────────────────────────────

def insert_report(
    document_id: int,
    verdetto: str,
    gravita_max: str = None,
    findings_json: dict | list | None = None,
    pseudo_text: str = None,
    llm_json: dict | None = None,
    precedente_json: dict | None = None,
    pdf_corretto_path: str = None,
) -> int:
    expires_at = (
        datetime.utcnow() + timedelta(days=RETENTION_DAYS)
    ).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO reports
               (document_id, verdetto, gravita_max, findings_json,
                pseudo_text, llm_json, precedente_json,
                pdf_corretto_path, expires_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                document_id,
                verdetto,
                gravita_max,
                json.dumps(findings_json) if findings_json is not None else None,
                pseudo_text,
                json.dumps(llm_json) if llm_json is not None else None,
                json.dumps(precedente_json) if precedente_json is not None else None,
                pdf_corretto_path,
                expires_at,
            ),
        )
        return cur.lastrowid


def get_report_by_document(document_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            """SELECT * FROM reports
               WHERE document_id=? ORDER BY id DESC LIMIT 1""",
            (document_id,),
        ).fetchone()
        return dict(row) if row else None


def delete_expired_reports() -> list[str]:
    """Elimina report scaduti; restituisce i pdf_corretto_path da cancellare."""
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT pdf_corretto_path FROM reports WHERE expires_at < ?", (now,)
        ).fetchall()
        paths = [r["pdf_corretto_path"] for r in rows if r["pdf_corretto_path"]]
        conn.execute("DELETE FROM reports WHERE expires_at < ?", (now,))
        return paths


# ── events ───────────────────────────────────────────────────────────────────

def insert_event(document_id: int, tipo: str, descrizione: str = None) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO events (document_id, tipo, descrizione) VALUES (?,?,?)",
            (document_id, tipo, descrizione),
        )
        return cur.lastrowid


def get_events_by_document(document_id: int) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM events WHERE document_id=? ORDER BY timestamp",
            (document_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_recent_events(limit: int = 50) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """SELECT e.*, d.titolo
               FROM events e JOIN documents d ON e.document_id = d.id
               ORDER BY e.timestamp DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


# ── smoke test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    print(f"DB inizializzato: {DB_PATH}")
    print(f"RETENTION_DAYS = {RETENTION_DAYS}")

    doc_id = insert_document(
        source="albo",
        titolo="Test atto",
        id_atto_albo="TEST-001",
        hash="abc123",
    )
    print(f"Inserted document id={doc_id}")

    rep_id = insert_report(
        document_id=doc_id,
        verdetto="non_conforme",
        gravita_max="alta",
        findings_json={"note": "test"},
    )
    print(f"Inserted report id={rep_id}")

    ev_id = insert_event(doc_id, "nuovo", "Atto rilevato durante test")
    print(f"Inserted event id={ev_id}")

    print("Document:", get_document_by_id(doc_id))
    print("Report:", get_report_by_document(doc_id))
    print("Events:", get_events_by_document(doc_id))
