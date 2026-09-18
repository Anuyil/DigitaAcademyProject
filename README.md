# DigitaAcademyProject

# Albo Sicuro — Contesto di progetto

## Cos'è
Hackathon "Campionato Universitario AI", traccia PRIVACY. 3 persone, 3 ore.
Albo Sicuro aiuta i Comuni a non pubblicare dati personali non necessari sull'Albo
Pretorio online. Due funzioni:
1. Il funzionario carica un PDF prima della pubblicazione: l'app dice se è conforme,
   evidenzia i problemi e genera un PDF corretto.
2. Un demone controlla gli atti già pubblicati (cartella data/albo_inbox/) e mostra
   le non conformità in una dashboard.

## Principio chiave: "l'IA vede il contesto, mai l'identità"
Prima si sostituiscono gli identificativi con segnaposto coerenti ([PERSONA_1], [CF_1],
[INDIRIZZO_1], [IBAN_1], [EMAIL_1], [TEL_1], [TARGA_1], [DATA_NASCITA_1]).
La stessa entità ha sempre lo stesso segnaposto. L'LLM locale riceve solo il testo
pseudonimizzato. La mappa segnaposto→valore resta in memoria e serve per applicare
le decisioni sul PDF originale.

## Stack (non cambiarlo)
Python 3.11, Streamlit, PyMuPDF (fitz), spaCy it_core_news_lg (o _sm se lento),
python-stdnum (validazione CF e IBAN), Ollama con qwen2.5:7b (fallback qwen2.5:3b),
SQLite. Nessun servizio cloud per l'analisi. Codice semplice, niente astrazioni inutili.

## Interfacce (CONTRATTI — non modificarle senza avvisare il team)

core/detectors.py
  pseudonymize(text: str) -> dict
    {"pseudo_text": str,
     "mapping": {"[CF_1]": "RSSMRA80A01F839X", ...},
     "entities": [{"placeholder": "[CF_1]", "type": "CF", "value": "...",
                   "start": int, "end": int}]}

core/llm.py
  analyze(pseudo_text: str) -> dict
    {"tipo_atto": str,
     "verdetto": "conforme" | "da_verificare" | "non_conforme",
     "decisioni": [{"placeholder": "[PERSONA_1]",
                    "azione": "mantenere" | "rimuovere" | "minimizzare",
                    "motivazione": str, "norma": str}],
     "passaggi_critici": [{"testo": str,   # frase ESATTA copiata dal testo
                           "categoria": "salute" | "disagio_economico" | "minori"
                                        | "giudiziario" | "altro",
                           "gravita": "alta" | "media" | "bassa",
                           "motivazione": str, "norma": str}]}
  Ollama con format="json" e temperature=0.

core/precedents.py
  find_precedent(categoria: str, tipo_atto: str) -> dict | None   # una scheda

core/pipeline.py
  analyze_pdf(pdf_path: str, output_dir: str) -> dict
    {"file": str, "verdetto": str, "gravita_max": str,
     "entities": [...], "decisioni": [...], "passaggi_critici": [...],
     "precedente": dict | None, "pdf_corretto": str}
  Redazione con page.add_redact_annot + apply_redactions (redazione vera, non
  rettangoli sovrapposti). "rimuovere" -> "omissis"; "minimizzare" -> iniziali.
  I passaggi_critici si oscurano cercandone il testo nel PDF.

Tabella SQLite "reports": id, file, hash, verdetto, gravita_max,
  data_pubblicazione, data_analisi, report_json.

## Formato dati
data/schede_provvedimenti.json: lista di
  {"id_provvedimento", "ente", "tipo_atto", "dati_esposti": [..],
   "categoria_violazione", "norma_violata", "giorni_esposizione",
   "sanzione_euro", "descrizione_fatti"}
data/dataset/labels.json: lista di
  {"file", "conforme": bool, "categoria_violazione", "tipo_atto",
   "id_provvedimento_origine", "passaggi_problematici": [str]}
Tutti i dati personali nel dataset sono INVENTATI. CF finti ma con carattere di
controllo valido.

## Regole normative da applicare
- Linee guida Garante 15/05/2014 su pubblicazione dati da parte delle PA per trasparenza
- Art. 2-septies Codice privacy: vietata la diffusione di dati relativi alla salute
- Art. 26 c.4 d.lgs. 33/2013: vietato pubblicare i dati identificativi dei beneficiari
  di contributi se rivelano salute o disagio economico-sociale
- Art. 5 GDPR: minimizzazione
- I nomi in graduatorie di concorso ed esiti di gara sono in genere legittimi.
  Numeri di protocollo, nomi di dirigenti e uffici vanno mantenuti.

## Regole di lavoro
- Ogni modulo parte con uno STUB che restituisce dati finti conformi al contratto.
- Funziona prima, bello dopo. Ore 2:10: stop alle nuove funzioni.
- Nella demo non mostrare mai dati personali reali.

## Il mio ruolo
[A/B/C: incolla qui il tuo compito]


# Progetto: Albo Sicuro — demo per hackathon (traccia PRIVACY), tempo disponibile ~2.5 ore

## Obiettivo
Web app che aiuta i Comuni a non pubblicare dati personali non necessari sull'Albo
Pretorio online. Deve funzionare in una DEMO LIVE: priorità a stabilità e impatto
visivo, non a completezza. Costruisci in modo incrementale e verifica che ogni pezzo
giri prima di passare al successivo.

## Stack (non cambiarlo)
Python 3.11, FastAPI, Jinja2, Tailwind via CDN, JavaScript vanilla (polling con fetch),
SQLite (modulo sqlite3), PyMuPDF (fitz), python-stdnum, spaCy it_core_news_sm,
libreria `openai` con base_url configurabile. Configurazione in .env (python-dotenv).
Crea requirements.txt, .env.example, README con i comandi e run.sh che avvia i 3 processi.

## Tre processi
1. app principale Albo Sicuro — porta 8000
2. sito finto "Comune di Borgo Vesuviano" — porta 8001
3. demone di monitoraggio — processo Python separato

## Struttura
albo_sicuro/
  core/detectors.py    # regex + validazione + spaCy + pseudonimizzazione
  core/llm.py          # client API LLM con cache e fallback
  core/pdf_utils.py    # estrazione testo + redazione vera
  core/pipeline.py     # analyze_pdf()
  core/db.py           # schema e query SQLite
  web/main.py          # FastAPI app porta 8000
  web/templates/       # dashboard, upload, reports, report_detail
  comune_fake/main.py  # sito finto porta 8001
  daemon/watcher.py
  scripts/seed.py      # popola il DB con data/dataset/
  data/ (dataset/, uploads/, albo_fake/, corrected/, llm_cache.json)

## Motore di analisi (core/)
detectors.pseudonymize(text) -> {"pseudo_text", "mapping", "entities"}
- Codice fiscale: regex con omocodia + stdnum.it.codicefiscale.is_valid
- IBAN: regex IT + stdnum.iban.is_valid
- email, telefono italiano, targa [A-Z]{2}\d{3}[A-Z]{2}, "nato/a a ... il ..."
- persone e luoghi con spaCy (label PER, LOC) + euristiche "sig./sig.ra"
- segnaposto tipizzati e coerenti: [PERSONA_1], [CF_1], [IBAN_1], [INDIRIZZO_1]...
  (stessa entità = stesso segnaposto)
- funzione mask(value) per salvare valori mascherati: "RSS***39X"

llm.analyze(pseudo_text) -> dict con:
  tipo_atto, verdetto ("conforme"|"da_verificare"|"non_conforme"),
  decisioni: [{placeholder, azione: "mantenere"|"rimuovere"|"minimizzare",
               motivazione, norma}],
  passaggi_critici: [{testo (frase ESATTA dal testo), categoria: "salute"|
    "disagio_economico"|"minori"|"giudiziario"|"altro", gravita: "alta"|"media"|
    "bassa", motivazione, norma}]
- Provider principale Groq (OpenAI-compatible), riserva Gemini (endpoint
  OpenAI-compatible). base_url, modello e chiavi da .env.
- temperature 0, risposta solo JSON, parsing robusto (togli ``` se presenti).
- CACHE su data/llm_cache.json con chiave sha256(pseudo_text).
- Se entrambe le API falliscono: verdetto basato solo sui detector,
  marcato "da_verificare", nessun crash.
- All'LLM va SOLO pseudo_text, mai il testo originale.
- Prompt di sistema in italiano con queste regole:
  * Linee guida Garante 15/05/2014 su trasparenza e pubblicazione online delle PA
  * art. 2-septies Codice privacy: vietata diffusione dati relativi alla salute
  * art. 26 c.4 d.lgs. 33/2013: vietati dati identificativi dei beneficiari di
    contributi se rivelano salute o disagio economico-sociale
  * art. 5 GDPR minimizzazione; tutela rafforzata dei minori
  * nomi in graduatorie di concorso ed esiti di gara: in genere legittimi;
    protocolli, dirigenti e uffici: mantenere

pipeline.analyze_pdf(pdf_path) -> report dict + genera PDF corretto:
- redazione vera con page.add_redact_annot + page.apply_redactions()
- "rimuovere" -> "omissis", "minimizzare" -> iniziali
- i passaggi_critici si oscurano cercando il testo nel PDF (page.search_for)
- aggiunge "precedente": scheda più simile da data/schede_provvedimenti.json
  (match su categoria e tipo_atto)

## Database (core/db.py)
documents(id, source "upload"|"albo", titolo, url, id_atto_albo, file_path, hash,
  data_pubblicazione, stato "nuovo"|"in_revisione"|"corretto"|"risolto"|
  "falso_positivo", created_at)
reports(id, document_id, verdetto, gravita_max, findings_json (SOLO valori
  mascherati), pseudo_text, llm_json, precedente_json, pdf_corretto_path,
  created_at, expires_at = created_at + RETENTION_DAYS)
events(id, document_id, tipo, descrizione, timestamp)   # cronologia
RETENTION_DAYS da .env, default 10.

## Sito finto del Comune (porta 8001)
Aspetto istituzionale semplice (stile sito comunale italiano).
- /albo: tabella atti (numero, oggetto, tipo, data pubblicazione, scadenza a
  15 giorni, link al PDF)
- /admin: form per pubblicare un PDF, sostituire il PDF di un atto esistente,
  rimuovere un atto. File in data/albo_fake/, elenco in un JSON.

## Demone (daemon/watcher.py)
Ogni POLL_SECONDS (default 8):
- scarica /albo del sito finto, estrae gli atti (BeautifulSoup)
- atto nuovo -> scarica PDF, analyze_pdf, salva document + report + evento
- stesso id_atto ma hash diverso -> evento "sostituito", rianalizza; se ora
  conforme -> stato "risolto"
- atto sparito dall'albo -> evento "rimosso"
- cancella report scaduti (expires_at) e i relativi file
- scrive l'orario dell'ultimo controllo (per l'indicatore "demone attivo")
Log chiari su console.

## App principale (porta 8000) — pagine
Design curato: stile dashboard moderna e pulita, colori semaforo
(verde/giallo/rosso), responsive. Nome "Albo Sicuro".

1. /  Dashboard LIVE
   - card: atti monitorati, non conformi, gravità alta aperti, report in scadenza
   - indicatore "Demone attivo — ultimo controllo Xs fa"
   - feed allarmi aggiornato con polling ogni 3s su /api/alerts; i nuovi
     allarmi compaiono in cima evidenziati con animazione e suono opzionale
   - ogni allarme mostra giorni di esposizione rimanenti sull'albo
2. /upload  Controllo prima della pubblicazione
   - drag & drop PDF -> risultato: semaforo, elenco problemi con motivazione e
     norma, card del precedente sanzionatorio (ente, importo)
   - pannello "Cosa vede l'IA": testo originale e pseudo_text affiancati
   - download PDF corretto
3. /reports  elenco con filtri (verdetto, stato, fonte), scadenza (countdown)
4. /reports/{id}  dettaglio
   - PDF originale e PDF corretto affiancati (iframe)
   - problemi trovati, precedente, cronologia eventi, countdown cancellazione
   - azioni: segna risolto / falso positivo, scarica corretto
5. endpoint API JSON corrispondenti + POST /api/demo/reset

## Seed
scripts/seed.py analizza tutti i PDF in data/dataset/ e popola il DB (source
"albo") con date di pubblicazione distribuite negli ultimi giorni.

## Priorità (in ordine; non passare alla successiva se la precedente non gira)
P0: motore + /upload funzionante end-to-end
P1: sito finto + demone + dashboard live
P2: /reports e dettaglio con PDF affiancati e cronologia
P3: retention, sostituzione atti, reset demo, rifiniture grafiche

## Regole
- Codice semplice e leggibile, niente astrazioni inutili.
- Mai dati personali reali. Mai valori in chiaro nel DB o nei log.
- Dopo ogni priorità: dimmi come avviarla e testarla.
