# Albo Sicuro — Architettura e stato implementazione (P1: Demone + Sito finto)

## Cos'è implementato in questa fase

Questa documentazione copre i moduli del ciclo di sorveglianza continua (P1):
demone → sito finto → DB. È il layer di **infrastruttura** su cui si appoggerà
il motore di analisi reale (P0: detectors + LLM + redazione PDF).

---

## Flusso dati completo

```
comune_fake/main.py          daemon/watcher.py
  (porta 8001)                  (processo separato)
       │                               │
  GET /api/atti ◄────────────── ogni POLL_SECONDS
       │                               │
  lista JSON atti ──────────────►  confronto con DB
                                       │
                              ┌────────┴────────┐
                              │                 │
                           NUOVO          GIÀ VISTO
                              │                 │
                    scarica PDF      URL cambiata? ──No──► skip
                              │          │
                              │        scarica nuovo PDF
                              │          │
                         analyze_pdf() ──► verdetto + passaggi
                              │
                    ┌─────────┴────────────────────┐
                    │         core/db.py            │
                    │  INSERT documents             │
                    │  INSERT reports               │
                    │  INSERT events                │
                    └───────────────────────────────┘
```

---

## Moduli implementati

### `core/db.py`

Schema SQLite con **PRAGMA journal_mode=WAL** (necessario perché demone e
web app scrivono sullo stesso file da processi diversi).

**Tabelle:**

```sql
documents(id, source, titolo, url, id_atto_albo, file_path, hash,
          data_pubblicazione, stato, created_at)

reports(id, document_id, verdetto, gravita_max, findings_json,
        pseudo_text, llm_json, precedente_json, pdf_corretto_path,
        created_at, expires_at)

events(id, document_id, tipo, descrizione, timestamp)
```

**API pubblica:**
```python
init_db()
insert_document(source, titolo, url, id_atto_albo, file_path,
                hash, data_pubblicazione, stato) -> int
update_document(doc_id, **kwargs)
get_document_by_id(id) -> dict | None
get_document_by_atto(id_atto_albo) -> dict | None
get_all_albo_documents() -> list[dict]

insert_report(document_id, verdetto, gravita_max, findings_json,
              pseudo_text, llm_json, precedente_json,
              pdf_corretto_path) -> int
get_report_by_document(document_id) -> dict | None
delete_expired_reports() -> list[str]   # ritorna path da cancellare su disco

insert_event(document_id, tipo, descrizione) -> int
get_events_by_document(document_id) -> list[dict]
get_recent_events(limit) -> list[dict]
```

`RETENTION_DAYS` da `.env` (default 10). `expires_at = now + RETENTION_DAYS`.

---

### `core/precedents.py`

Lookup su `data/schede_provvedimenti.json`. Non è una chiamata LLM.

```python
find_precedent(categoria: str | None, tipo_atto: str | None) -> dict | None
```

**Logica:**
1. Filtra le schede per `categoria_violazione == categoria`
2. Tra i match, preferisce quello con `tipo_atto` uguale
3. Se nessun match esatto su tipo, restituisce il primo per categoria
4. Restituisce `None` se `categoria` è `None` o non c'è nessun match

**Esempi:**

| categoria | tipo_atto | risultato |
|---|---|---|
| `salute` | `determina_dirigenziale` | `ordinanza-3-2020` |
| `giudiziario` | `determina_dirigenziale` | `ordinanza-118-2020` |
| `minori` | `ordinanza` | `provv-commezzadura-2022` |
| `None` | qualsiasi | `None` |
| `inesistente` | qualsiasi | `None` |

---

### `core/pipeline.py` — STUB intelligente

> ⚠️ Questo è uno stub. Il contratto della funzione è definitivo,
> ma l'implementazione interna cambierà quando colleghiamo detectors + LLM.

```python
analyze_pdf(pdf_path: str, output_dir: str) -> dict
```

**Contratto di ritorno:**
```python
{
    "file": str,            # nome file
    "hash": str,            # SHA-256 del PDF (sempre calcolato, anche nello stub)
    "verdetto": str,        # "conforme" | "non_conforme" | "da_verificare"
    "gravita_max": str | None,
    "entities": list,       # [{"placeholder", "type", "value", "start", "end"}]
    "decisioni": list,      # [{"placeholder", "azione", "motivazione", "norma"}]
    "passaggi_critici": list, # [{"testo", "categoria", "gravita", "motivazione", "norma"}]
    "precedente": dict | None,
    "pdf_corretto": str,    # path del PDF redatto (= originale nello stub)
}
```

**Comportamento dello stub:**

| Condizione | Verdetto | Note |
|---|---|---|
| File in `labels.json`, `conforme=true` | `conforme` | passaggi=[], precedente=None |
| File in `labels.json`, `conforme=false` | `non_conforme` | passaggi da `passaggi_problematici`, precedente da `find_precedent()` |
| File NON in `labels.json` | `da_verificare` | upload del funzionario, PDF esterni |

**Nota sul prefisso `{id}_`:** il sito finto rinomina i PDF come `001_nome.pdf`.
Lo stub riconosce e toglie il prefisso numerico prima del lookup in `labels.json`.

**Pipeline reale (da implementare in P0):**
```
estrazione testo (pdf_utils)
    → pseudonymize (detectors)
    → find_precedent (già pronto)
    → llm.analyze (da scrivere)
    → redazione PDF (pdf_utils)
```

---

### `core/downloader.py`

```python
scarica_atto(url_pdf: str, dest_dir: str) -> str | None
```

Download sincrono via `requests`. Nessuna eccezione propagata: ritorna `None`
in caso di errore (404, timeout, host irraggiungibile) con log ERROR.
Non usa streaming per compatibilità con uvicorn.

---

### `comune_fake/main.py` — Sito finto (porta 8001)

Simula l'Albo Pretorio del "Comune di Borgo Vesuviano".

**Endpoints:**

| Metodo | Path | Descrizione |
|---|---|---|
| `GET` | `/albo` | Pagina HTML con tabella atti e scadenza 15gg |
| `GET` | `/api/atti` | Lista JSON per il demone |
| `GET` | `/albo_fake/{filename}` | Serve PDF statici |
| `POST` | `/admin/pubblica` | Pubblica atto (dropdown dataset o upload) |
| `POST` | `/admin/rimuovi/{id}` | Rimuove atto dall'albo |
| `GET` | `/admin` | Pannello HTML admin |

**Seed automatico all'avvio** (solo se `atti.json` è vuoto):
```
graduatoria_concorso_01.pdf        → conforme
determina_contributo_salute_03.pdf → non_conforme / salute
determina_sussidio_disagio_04.pdf  → non_conforme / disagio_economico
atto_vicenda_giudiziaria_07.pdf    → non_conforme / giudiziario
```

**Struttura file:**
```
data/albo_fake/
  atti.json          ← lista atti correnti
  pdf/               ← PDF pubblicati (copiati da data/)
```

---

### `daemon/watcher.py`

Ciclo ogni `POLL_SECONDS` (default 8, da `.env`).

**Logica per ciclo:**

```
1. GET /api/atti → lista atti correnti
2. Per ogni atto rimosso (in DB ma non nella lista):
     UPDATE documents SET stato='risolto'
     INSERT event tipo='rimosso'
3. Per ogni atto corrente:
     - URL invariata rispetto al DB → skip (zero download)
     - URL cambiata O mai visto:
         scarica PDF → calcola hash
         se hash invariato → aggiorna solo URL, skip analisi
         altrimenti → analyze_pdf() → insert/update documents + reports + events
4. DELETE FROM reports WHERE expires_at < now  (+  rm file su disco)
5. WRITE data/last_check.txt  (timestamp UTC per la dashboard)
6. Log riepilogo ciclo
```

**Stati `documents.stato`:**

| Evento | Stato risultante |
|---|---|
| Nuovo, verdetto conforme | `risolto` |
| Nuovo, verdetto non_conforme/da_verificare | `nuovo` |
| Sostituito, ora conforme | `risolto` |
| Sostituito, ancora non_conforme | `in_revisione` |
| Rimosso dall'albo | `risolto` |

---

## Cosa NON è ancora implementato (P0)

| Modulo | Funzione | Priorità |
|---|---|---|
| `core/detectors.py` | `pseudonymize()` — regex + spaCy | P0 |
| `core/llm.py` | `analyze()` — Groq/Gemini | P0 |
| `core/pdf_utils.py` | estrazione testo + redazione | P0 |
| `web/main.py` | dashboard + `/upload` | P0/P1 |
| `scripts/seed.py` | popola DB da `data/dataset/` | P2 |

Quando `detectors.py`, `llm.py` e `pdf_utils.py` saranno pronti,
**`pipeline.py` è l'unico file da aggiornare** — tutto il resto
(daemon, db, comune_fake) rimane invariato.

---

## Come avviare in sviluppo

```bash
# Crea .env da .env.example e compila le API key se disponibili
cp .env.example .env

# Installa dipendenze
.venv/bin/pip install -r requirements.txt
python -m spacy download it_core_news_sm  # per detectors (P0)

# Terminale 1 — sito finto
.venv/bin/uvicorn comune_fake.main:app --port 8001 --reload

# Terminale 2 — demone
.venv/bin/python daemon/watcher.py

# Terminale 3 — app principale (quando web/main.py sarà pronto)
.venv/bin/uvicorn web.main:app --port 8000 --reload
```

## Test automatico

```bash
bash test_pipeline.sh
```

Testa: smoke test moduli core → seed albo finto → 3 cicli demone
(nuovo / invariato / rimosso) → pubblica 2 atti via admin → verifica
incrociata DB ↔ labels.json ↔ schede_provvedimenti.json.

## Query SQLite utili

```bash
# Tutti i report con verdetto e precedente
sqlite3 -column -header data/albo_sicuro.db "
SELECT d.id_atto_albo, d.titolo, r.verdetto, r.gravita_max,
       json_extract(r.precedente_json,'$.id_provvedimento') AS precedente,
       json_extract(r.precedente_json,'$.categoria_violazione') AS categoria
FROM reports r JOIN documents d ON r.document_id=d.id
ORDER BY d.id;"

# Cronologia eventi
sqlite3 -column -header data/albo_sicuro.db "
SELECT e.timestamp, d.titolo, e.tipo, e.descrizione
FROM events e JOIN documents d ON e.document_id=d.id
ORDER BY e.timestamp DESC LIMIT 20;"

# Verifica WAL
sqlite3 data/albo_sicuro.db "PRAGMA journal_mode;"
```
