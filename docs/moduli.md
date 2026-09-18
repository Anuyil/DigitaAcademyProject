# Albo Sicuro — Cosa fa ogni modulo e stato di funzionamento

> Verificato il 2026-09-18 con test reale end-to-end (LLM Groq attivo).

---

## Mappa del sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                     FLUSSO PRINCIPALE                           │
│                                                                 │
│  comune_fake/main.py          daemon/watcher.py                 │
│    (porta 8001)                  (processo separato)            │
│         │                               │                       │
│    GET /api/atti ◄──────────── ogni POLL_SECONDS                │
│         │                               │                       │
│    lista atti JSON ──────────► confronto con DB                 │
│                                         │                       │
│                               ┌─────────┴──────────┐           │
│                            NUOVO               GIÀ VISTO        │
│                               │                     │           │
│                        scarica PDF          URL uguale? → skip  │
│                               │                     │           │
│                         core/pipeline.analyze_pdf()             │
│                               │                                 │
│           ┌───────────────────┼──────────────────────┐          │
│           │                   │                      │          │
│    extract_text          pseudonymize           find_precedent  │
│    (pdf_utils)           (detectors)            (precedents)    │
│           │                   │                      │          │
│           └───────────────────┴──────────────────────┘          │
│                               │                                 │
│                         llm.analyze()                           │
│                    (Groq → Gemini → fallback)                   │
│                               │                                 │
│                         redact_pdf()                            │
│                          (pdf_utils)                            │
│                               │                                 │
│              INSERT documents + reports + events                │
│                          (core/db)                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Moduli — dettaglio e stato

### `core/db.py` ✅ Funziona

**Cosa fa:** gestisce il database SQLite con WAL attivo.

**Tabelle:**
- `documents` — ogni PDF mai visto (source, titolo, url, hash, stato)
- `reports` — risultato analisi per ogni documento (verdetto, passaggi, precedente, path PDF redatto, scadenza)
- `events` — log degli eventi (nuovo/sostituito/rimosso)

**Funzioni principali:**
```python
init_db()                          # crea le tabelle se non esistono
insert_document(source, ...)  → int   # ritorna l'id del documento inserito
update_document(doc_id, **kwargs)     # aggiorna campi arbitrari
get_document_by_atto(id_atto_albo) → dict | None
get_all_albo_documents() → list[dict] # tutti gli atti source='albo'
insert_report(document_id, verdetto, ...) → int
delete_expired_reports() → list[str]  # elimina scaduti, ritorna path da cancellare
insert_event(document_id, tipo, descrizione) → int
```

**Dettagli tecnici:**
- `PRAGMA journal_mode=WAL` attivato su ogni connessione (demone e web app scrivono in parallelo)
- `PRAGMA foreign_keys=ON`
- `expires_at = now + RETENTION_DAYS` (default 10, da `.env`)
- I valori nelle entities salvate nel DB sono **sempre mascherati** (`RSS***39D`), mai in chiaro

**Verifica:** `python -m core.db`

---

### `core/precedents.py` ✅ Funziona

**Cosa fa:** cerca il precedente del Garante Privacy più pertinente in `data/schede_provvedimenti.json`. Non chiama nessuna API.

```python
find_precedent(categoria: str | None, tipo_atto: str | None) → dict | None
```

**Logica:**
1. Filtra le schede per `categoria_violazione == categoria`
2. Tra i match preferisce quello con `tipo_atto` uguale
3. Altrimenti restituisce il primo della categoria
4. Restituisce `None` se `categoria` è `None` o non c'è nessun match

**Esempi verificati:**
| categoria | tipo_atto | risultato |
|---|---|---|
| `salute` | `determina_dirigenziale` | `ordinanza-3-2020` ✅ |
| `giudiziario` | `determina_dirigenziale` | `ordinanza-118-2020` ✅ |
| `minori` | `ordinanza` | `provv-commezzadura-2022` ✅ |
| `None` | qualsiasi | `None` ✅ |

**Verifica:** `python -m core.precedents`

---

### `core/detectors.py` ✅ Funziona

**Cosa fa:** pseudonimizza il testo — sostituisce i dati sensibili con segnaposto coerenti prima di mandare qualsiasi cosa all'LLM.

```python
pseudonymize(text: str) → {
    "pseudo_text": str,              # testo con [PERSONA_1], [CF_1], ecc.
    "mapping":  {"[CF_1]": "RSSMRA80A01F839X", ...},  # resta solo locale
    "entities": [{"placeholder", "type", "value", "start", "end"}]
}
mask(value: str) → str               # "RSS***39X" per log/DB
```

**Entità rilevate (in ordine di priorità):**
| Tipo | Metodo | Validazione | Placeholder |
|---|---|---|---|
| CF | regex 16 char | `stdnum.it.codicefiscale.is_valid` | `[CF_N]` |
| IBAN | regex 27 char | `stdnum.iban.is_valid` | `[IBAN_N]` |
| EMAIL | regex | — | `[EMAIL_N]` |
| TARGA | regex | — | `[TARGA_N]` |
| TEL | regex (fisso/mobile IT) | — | `[TEL_N]` |
| DATA_NASCITA | regex contestuale "nato/nata il" | — | `[DATA_NASCITA_N]` |
| PERSONA | spaCy PER + euristiche sig./dott./avv. | — | `[PERSONA_N]` |
| INDIRIZZO | spaCy LOC | — | `[INDIRIZZO_N]` |

**Principio chiave:** la stessa entità produce sempre lo stesso segnaposto nello stesso documento (`[PERSONA_1]` appare tutte le volte che appare "Mario Rossi"). La mappa reale resta in memoria locale e non esce mai verso l'LLM.

**Risultato su PDF reale (`01_determina_spese_legali_salute_iban.pdf`):**
- 34 entità totali: CF×1, IBAN×1, PERSONA×13 — tutti rimossi dal pseudo_text ✅

**Dipendenze:** `spacy it_core_news_sm`, `python-stdnum`. Degrada gracefully se non installate (solo regex).

**Verifica:** `python -m core.detectors`

---

### `core/llm.py` ✅ Funziona (con Groq)

**Cosa fa:** manda il testo pseudonimizzato all'LLM e riceve il verdetto.

```python
analyze(pseudo_text: str, precedente: dict | None = None) → {
    "tipo_atto": str,
    "verdetto": "conforme" | "da_verificare" | "non_conforme",
    "decisioni": [{"placeholder", "azione", "motivazione", "norma"}],
    "passaggi_critici": [{"testo", "categoria", "gravita", "motivazione", "norma"}]
}
```

**Flusso:**
1. Calcola `sha256(pseudo_text)` → controlla `data/llm_cache.json`
2. **Cache hit** → ritorna subito (zero API call)
3. Prova **Groq** (`groq/compound`) con `response_format=json_object`
4. Se Groq fallisce → prova **Gemini** (riserva, opzionale)
5. Se entrambi falliscono → **fallback deterministico**: `verdetto=da_verificare`, azioni prudenziali per ogni segnaposto, nessun crash

**Cosa manda all'LLM:**
- System prompt fisso con norme GDPR/Garante (Linee guida 15/05/2014, art. 2-septies, art. 26 c.4, art. 5 GDPR, art. 9-10 GDPR)
- Pseudo_text con segnaposto (MAI il testo originale)
- Precedente Garante pertinente nel messaggio utente (non nel system prompt)

**Configurazione `.env`:**
```
GROQ_API_KEY=...
GROQ_MODEL=groq/compound
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

**Limiti Groq noti:** piano gratuito = 30.000 token/minuto. Documenti grandi (>3000 token) saturano il limite in sequenza rapida → usare `LLM_CALL_DELAY=15` nel demone.

**Verifica:** `python -m core.llm`

---

### `core/pdf_utils.py` ✅ Funziona

**Cosa fa:** estrae il testo dai PDF e applica la redazione fisica.

```python
extract_text(pdf_path: str) → str        # testo grezzo da tutte le pagine

redact_pdf(pdf_path, output_path, mapping, decisioni, passaggi_critici) → str
```

**Redazione:**
- `"rimuovere"` → cerca il valore reale nel PDF (`page.search_for`), sostituisce con **OMISSIS** (rettangolo bianco + testo)
- `"minimizzare"` → sostituisce con **iniziali** (Mario Rossi → M.R.)
- `"mantenere"` → nessuna modifica

**Due passate:**
1. Entità singole: cerca il valore reale di ogni `[PERSONA_N]`, `[CF_N]`, ecc. e oscura tutte le occorrenze
2. Frasi critiche: ricostruisce il testo reale dai passaggi (ri-sostituisce i segnaposto con valori veri) e oscura la frase intera se trovata

**Risultato su PDF reale:** 14 occorrenze oscurate su `01_determina_spese_legali_salute_iban.pdf` ✅

**Tecnologia:** PyMuPDF (`pymupdf`), `page.add_redact_annot` + `page.apply_redactions`

**Verifica:** `python -m core.pdf_utils` → apri `data/corrected/test_redatto.pdf`

---

### `core/pipeline.py` ✅ Funziona (motore completo)

**Cosa fa:** collega tutti i moduli nella catena completa.

```python
analyze_pdf(pdf_path: str, output_dir: str) → {
    "file": str, "hash": str,
    "verdetto": "conforme"|"non_conforme"|"da_verificare",
    "gravita_max": str | None,
    "entities": [...],        # valori MASCHERATI, sicuri per il DB
    "decisioni": [...],
    "passaggi_critici": [...],
    "precedente": dict | None,
    "pdf_corretto": str       # path del PDF redatto
}
```

**Catena interna:**
```
1. extract_text(pdf_path)          → testo grezzo
2. pseudonymize(testo)             → pseudo_text + mapping + entities
3. _guess_categoria(testo)         → stima categoria con keyword matching
4. find_precedent(categoria, tipo) → precedente Garante pertinente
5. llm.analyze(pseudo_text, prec)  → verdetto + decisioni + passaggi
6. redact_pdf(...)                 → PDF fisicamente redatto
7. return risultato strutturato
```

**Stima categoria (pre-LLM):** analisi keyword sul testo originale per trovare categoria probabile e tipo_atto — serve a passare il precedente all'LLM prima che risponda.

**Verifica:** `python -m core.pipeline`

---

### `core/downloader.py` ✅ Funziona

**Cosa fa:** scarica un PDF da URL e lo salva su disco.

```python
scarica_atto(url_pdf: str, dest_dir: str) → str | None
```

Ritorna il path del file scaricato, `None` in caso di qualsiasi errore (404, timeout, host irraggiungibile). Non lancia eccezioni.

**Verifica:** `python -m core.downloader` (richiede sito finto attivo)

---

### `comune_fake/main.py` ✅ Funziona (porta 8001)

**Cosa fa:** simula l'Albo Pretorio del "Comune di Borgo Vesuviano".

| Endpoint | Descrizione |
|---|---|
| `GET /albo` | Pagina HTML con tabella atti e scadenza 15gg |
| `GET /api/atti` | Lista JSON per il demone |
| `GET /albo_fake/{filename}` | Serve i PDF come file statici |
| `GET /admin` | Pannello HTML per gestire gli atti |
| `POST /admin/pubblica` | Pubblica atto (scegli PDF dal dataset o upload) |
| `POST /admin/rimuovi/{id}` | Rimuove atto dall'albo |

**Seed automatico all'avvio** (solo se `atti.json` vuoto):
- `001` — Graduatoria Concorso 01 (conforme)
- `002` — Determina Contributo Salute 03 (non_conforme / salute)
- `003` — Determina Sussidio Disagio 04 (non_conforme / disagio_economico)
- `004` — Atto Vicenda Giudiziaria 07 (non_conforme / giudiziario)

**Avvio:** `uvicorn comune_fake.main:app --port 8001 --reload`

---

### `daemon/watcher.py` ✅ Funziona

**Cosa fa:** ciclo di monitoraggio che scarica e analizza ogni atto nuovo o modificato sull'albo.

**Ciclo ogni `POLL_SECONDS` (default 8):**
1. `GET /api/atti` → lista atti correnti
2. Confronto con DB:
   - **URL invariata** → skip (zero download, zero LLM)
   - **Nuovo id** → scarica PDF → `analyze_pdf` → INSERT documents+reports+events
   - **URL cambiata** → scarica nuovo PDF → confronta hash → se diverso → rianalizza
   - **Rimosso** → UPDATE stato=risolto + evento
3. Cancella report scaduti + file su disco
4. Scrive `data/last_check.txt` (timestamp UTC, letto dalla dashboard)

**Delay LLM:** `LLM_CALL_DELAY=15` secondi tra ogni chiamata LLM (evita 429 rate limit Groq piano gratuito).

**Avvio:** `python daemon/watcher.py`

---

## Test end-to-end verificato

```bash
bash test_pipeline.sh
```

Output reale dell'ultimo test:

| Atto | Tipo | Verdetto LLM | Precedente | PDF redatto |
|---|---|---|---|---|
| 001 Graduatoria | graduatoria | **conforme** | — | no (nessuna modifica) |
| 002 Contributo Salute | determina | **non_conforme** | ordinanza-3-2020 | sì (14 occorrenze) |
| 003 Sussidio Disagio | determina | **da_verificare** | provv-tricase-2021 | sì (1 occorrenza) |
| 004 Vicenda Giudiziaria | ordinanza | **da_verificare** | ordinanza-118-2020 | sì (9 occorrenze) |

Secondo ciclo: 0 download, 0 chiamate LLM (URL invariate).

---

## Cosa NON è ancora implementato

| Modulo | Funzione | Note |
|---|---|---|
| `web/main.py` | Dashboard + `/upload` | P0/P1 — prossimo passo |
| `scripts/seed.py` | Popola DB da `data/dataset/` | P2 |

---

## Setup da zero

```bash
# 1. Dipendenze
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m spacy download it_core_news_sm

# 2. Configurazione
cp .env.example .env
# Modifica .env: GROQ_API_KEY=...

# 3. Avvia i processi (3 terminali separati)
.venv/bin/uvicorn comune_fake.main:app --port 8001      # sito finto
.venv/bin/python daemon/watcher.py                      # demone
# .venv/bin/uvicorn web.main:app --port 8000             # app (da fare)

# 4. Test completo
bash test_pipeline.sh
```

---

## Variabili `.env` rilevanti

| Variabile | Default | Descrizione |
|---|---|---|
| `DB_PATH` | `data/albo_sicuro.db` | Path del database SQLite |
| `RETENTION_DAYS` | `10` | Giorni prima che un report scada |
| `POLL_SECONDS` | `8` | Intervallo ciclo demone |
| `LLM_CALL_DELAY` | `15` | Secondi di pausa tra chiamate LLM |
| `ALBO_URL` | `http://localhost:8001/api/atti` | URL API sito finto |
| `GROQ_API_KEY` | — | API key Groq (obbligatoria) |
| `GROQ_MODEL` | `groq/compound` | Modello Groq da usare |
| `LABELS_PATH` | `data/labels.json` | Dataset di test etichettato |
| `SCHEDE_PATH` | `data/schede_provvedimenti.json` | Precedenti Garante |
