# Albo Sicuro — CLAUDE.md

Hackathon "Campionato Universitario AI" (Napoli, traccia PRIVACY). 3 persone, tempo
stretto. Priorità assoluta: **funziona prima, bello dopo**. Codice semplice, niente
astrazioni inutili, niente librerie in più rispetto a quelle elencate sotto.

## Cos'è il progetto

Albo Sicuro aiuta i Comuni a non pubblicare dati personali eccedenti sull'Albo
Pretorio online. Due modi d'uso, stesso motore di analisi:

1. **Controllo preventivo**: il funzionario carica un PDF su `/upload` prima di
   pubblicarlo → risposta sincrona con verdetto, problemi trovati, PDF corretto.
2. **Sorveglianza continua**: un demone osserva un sito finto che simula l'Albo
   Pretorio di un Comune, trova atti nuovi/modificati/rimossi, li analizza da solo
   e alimenta una dashboard live.

Entrambi i percorsi chiamano la STESSA funzione `pipeline.analyze_pdf()`. Non sono
due sistemi, sono due punti di ingresso allo stesso motore. Si distinguono solo nel
DB tramite `documents.source = "upload" | "albo"`.

## Principio chiave: "l'IA vede il contesto, mai l'identità"

Prima di mandare qualunque testo all'LLM, si sostituiscono gli identificativi con
segnaposto coerenti: `[PERSONA_1]`, `[CF_1]`, `[INDIRIZZO_1]`, `[IBAN_1]`,
`[EMAIL_1]`, `[TEL_1]`, `[TARGA_1]`, `[DATA_NASCITA_1]`. La stessa entità ha sempre
lo stesso segnaposto nello stesso documento. La mappa segnaposto→valore reale resta
SOLO in memoria/DB locale e non esce mai verso l'LLM. Mai dati reali nei log.

## Stack (non cambiare)

Python 3.11, FastAPI, Jinja2, Tailwind via CDN, JavaScript vanilla (polling con
`fetch`), SQLite (modulo `sqlite3`, **PRAGMA journal_mode=WAL** attivato in
`core/db.py` perché demone e web app scrivono sullo stesso file da processi
diversi), PyMuPDF (`fitz`), `python-stdnum` (validazione CF/IBAN), spaCy
`it_core_news_sm`, libreria `openai` con `base_url` configurabile (Groq come
provider principale, Gemini come riserva, entrambi OpenAI-compatible).
Configurazione in `.env` (`python-dotenv`).

## Tre processi indipendenti

1. **App principale Albo Sicuro** — porta 8000 (FastAPI)
2. **Sito finto "Comune di Borgo Vesuviano"** — porta 8001 (FastAPI, aspetto
   istituzionale semplice)
3. **Demone di monitoraggio** — processo Python separato, nessuna porta esposta

Comunicano SOLO tramite SQLite (demone/web app) e tramite HTTP (demone → sito
finto, in lettura). Nessun altro canale.

## Struttura cartelle

```
albo_sicuro/
  core/detectors.py    # regex + validazione + spaCy + pseudonimizzazione
  core/llm.py           # client API LLM con cache e fallback
  core/pdf_utils.py     # estrazione testo + redazione vera
  core/pipeline.py      # analyze_pdf()
  core/precedents.py    # find_precedent()
  core/db.py             # schema e query SQLite
  web/main.py            # FastAPI app porta 8000
  web/templates/         # dashboard, upload, reports, report_detail
  comune_fake/main.py   # sito finto porta 8001
  daemon/watcher.py
  scripts/seed.py        # popola il DB con data/dataset/
  data/
    schede_provvedimenti.json
    dataset/              # PDF di test + labels.json
    uploads/
    albo_fake/
    corrected/
    llm_cache.json
```

## Contratti dei moduli (NON modificare le firme senza avvisare il team)

### `core/detectors.py`
```python
pseudonymize(text: str) -> dict
# {"pseudo_text": str,
#  "mapping": {"[CF_1]": "RSSMRA80A01F839X", ...},
#  "entities": [{"placeholder": "[CF_1]", "type": "CF", "value": "...",
#                "start": int, "end": int}]}
```
CF con validazione carattere di controllo (`stdnum.it.codicefiscale.is_valid`),
IBAN italiano con `stdnum.iban.is_valid`, email/telefono/targa via regex, persone e
luoghi via spaCy (label PER, LOC) + euristiche "sig./sig.ra". `mask(value)` per
salvare valori mascherati nei log/DB, es. `"RSS***39X"`.

### `core/llm.py`
```python
analyze(pseudo_text: str, precedente: dict | None = None) -> dict
# {"tipo_atto": str,
#  "verdetto": "conforme" | "da_verificare" | "non_conforme",
#  "decisioni": [{"placeholder": "[PERSONA_1]",
#                 "azione": "mantenere" | "rimuovere" | "minimizzare",
#                 "motivazione": str, "norma": str}],
#  "passaggi_critici": [{"testo": str,   # frase ESATTA copiata dal testo
#                        "categoria": "salute" | "disagio_economico" | "minori"
#                                     | "giudiziario" | "altro",
#                        "gravita": "alta" | "media" | "bassa",
#                        "motivazione": str, "norma": str}]}
```
- Provider principale Groq (OpenAI-compatible), riserva Gemini (endpoint
  OpenAI-compatible). `base_url`, modello e chiavi da `.env`.
- `temperature=0`, risposta solo JSON (`response_format` se supportato, altrimenti
  parsing robusto: togliere ``` se presenti).
- **Cache** su `data/llm_cache.json`, chiave `sha256(pseudo_text)` — evita chiamate
  ripetute sullo stesso documento durante i test.
- Se entrambe le API falliscono: verdetto basato solo sui `detectors`, marcato
  `"da_verificare"`, **nessun crash**.
- All'LLM va SOLO `pseudo_text` (+ eventuale `precedente`), MAI il testo originale.
- **System prompt** (costante fissa, in italiano, sempre uguale — separata dalla
  logica in una variabile dedicata):
  - Linee guida Garante 15/05/2014 su trasparenza e pubblicazione online delle PA
  - art. 2-septies Codice privacy: vietata diffusione dati relativi alla salute
  - art. 26 c.4 d.lgs. 33/2013: vietati dati identificativi dei beneficiari di
    contributi se rivelano salute o disagio economico-sociale
  - art. 5 GDPR: minimizzazione; tutela rafforzata dei minori
  - nomi in graduatorie di concorso ed esiti di gara: in genere legittimi;
    protocolli, dirigenti e uffici: mantenere
  - "se ti viene fornito un precedente reale pertinente, citalo nella motivazione
    e nel campo norma; se non è fornito nessun precedente, basati solo sulle
    regole sopra. Non dare mai un verdetto netto senza motivazione. Se il
    contesto è ambiguo, usa verdetto 'da_verificare'."
- Il `precedente` (dinamico, trovato da `find_precedent()` PRIMA di chiamare
  l'LLM) va nello **user message**, non nel system prompt.

### `core/precedents.py`
```python
find_precedent(categoria: str, tipo_atto: str) -> dict | None
```
Filtro/lookup su `data/schede_provvedimenti.json`, NON è una chiamata LLM.

### `core/pipeline.py`
```python
analyze_pdf(pdf_path: str, output_dir: str) -> dict
# {"file": str, "verdetto": str, "gravita_max": str,
#  "entities": [...], "decisioni": [...], "passaggi_critici": [...],
#  "precedente": dict | None, "pdf_corretto": str}
```
Ordine interno: estrazione testo → `pseudonymize` → `find_precedent` (in base a
categoria/tipo atto individuati o desumibili) → `llm.analyze` → redazione.
Redazione vera con `page.add_redact_annot` + `apply_redactions()` (mai rettangoli
sovrapposti al testo). `"rimuovere"` → `"omissis"`; `"minimizzare"` → iniziali. I
`passaggi_critici` si oscurano cercandone il testo esatto nel PDF
(`page.search_for`).

## Database (`core/db.py`)

```sql
documents(id, source "upload"|"albo", titolo, url, id_atto_albo, file_path, hash,
  data_pubblicazione, stato "nuovo"|"in_revisione"|"corretto"|"risolto"|
  "falso_positivo", created_at)

reports(id, document_id, verdetto, gravita_max, findings_json (SOLO valori
  mascherati), pseudo_text, llm_json, precedente_json, pdf_corretto_path,
  created_at, expires_at = created_at + RETENTION_DAYS)

events(id, document_id, tipo, descrizione, timestamp)
```
`RETENTION_DAYS` da `.env`, default 10. Attivare `PRAGMA journal_mode=WAL;` in ogni
connessione aperta da `core/db.py`.

## Sito finto del Comune (porta 8001)

Aspetto istituzionale semplice.
- `GET /albo` — pagina HTML con tabella atti (numero, oggetto, tipo, data
  pubblicazione, scadenza a 15 giorni, link al PDF)
- `GET /api/atti` — **stesso elenco in JSON strutturato**, per uso del demone (non
  fare parsing HTML fragile con BeautifulSoup): `[{"id_atto_albo", "titolo",
  "tipo_atto", "url_pdf", "data_pubblicazione"}, ...]`
- `/admin` — form per pubblicare un PDF, sostituire il PDF di un atto esistente,
  rimuovere un atto. File in `data/albo_fake/`, elenco in un JSON locale.

## Demone (`daemon/watcher.py`)

Ciclo ogni `POLL_SECONDS` (default 8, da `.env`):
1. `GET http://localhost:8001/api/atti` → lista atti correnti
2. confronto con `documents` (filtrati per `source="albo"`):
   - `id_atto_albo` mai visto → nuovo: scarica PDF, calcola hash, `analyze_pdf`,
     inserisce `documents`+`reports`+evento `"nuovo"`
   - `id_atto_albo` noto ma hash diverso → sostituito: rianalizza, evento
     `"sostituito"`; se ora conforme → `stato="risolto"`
   - `id_atto_albo` noto ma non più presente nella lista → evento `"rimosso"`,
     nessuna rianalisi
   - hash uguale e presente → nessuna azione
3. cancella `reports` con `expires_at` scaduto + relativi file su disco
4. scrive/aggiorna il timestamp "ultimo controllo" (letto dalla dashboard per
   l'indicatore "Demone attivo")
5. log chiari su console ad ogni giro (atti visti, nuovi, eventi generati)

Il demone NON espone API proprie. Non gestisce mai `/upload` — quello resta
responsabilità di `web/main.py`, che chiama `pipeline.analyze_pdf()` in modo
sincrono nello stesso processo della web app.

## Regole normative da applicare (riferimento rapido)

- Linee guida Garante 15/05/2014 su pubblicazione dati da parte delle PA per
  trasparenza
- Art. 2-septies Codice privacy: vietata la diffusione di dati relativi alla salute
- Art. 26 c.4 d.lgs. 33/2013: vietato pubblicare i dati identificativi dei
  beneficiari di contributi se rivelano salute o disagio economico-sociale
- Art. 5 GDPR: minimizzazione
- Nomi in graduatorie di concorso ed esiti di gara sono in genere legittimi.
  Numeri di protocollo, nomi di dirigenti e uffici vanno mantenuti.

## Formato dati

- `data/schede_provvedimenti.json`: lista di `{"id_provvedimento", "ente",
  "tipo_atto", "dati_esposti": [...], "categoria_violazione", "norma_violata",
  "giorni_esposizione", "sanzione_euro", "descrizione_fatti"}` — casi REALI del
  Garante, sintetizzati senza nomi/dati reali di persone.
- `data/dataset/labels.json`: lista di `{"file", "conforme": bool,
  "categoria_violazione", "tipo_atto", "id_provvedimento_origine",
  "passaggi_problematici": [str]}` — documenti di test, TUTTI inventati. CF/IBAN
  finti ma sintatticamente validi (carattere di controllo corretto).

## Priorità (in ordine — non passare alla successiva se la precedente non gira)

- **P0**: motore + `/upload` funzionante end-to-end
- **P1**: sito finto + demone + dashboard live
- **P2**: `/reports` e dettaglio con PDF affiancati e cronologia
- **P3**: retention, sostituzione atti, reset demo, rifiniture grafiche

## Regole di lavoro

- Ogni modulo parte con uno STUB che restituisce dati finti conformi al contratto,
  così i pezzi si sviluppano in parallelo senza bloccarsi a vicenda.
- Funziona prima, bello dopo.
- Mai dati personali reali, in nessun file, log, screenshot o commit. Mai valori
  in chiaro nel DB o nei log (sempre mascherati o pseudonimizzati).
- Dopo ogni priorità completata: spiegare come avviarla e testarla.
- Creare `requirements.txt`, `.env.example`, `README.md` con i comandi, e
  `run.sh` che avvia i 3 processi.