# Come testare ogni pezzo — Albo Sicuro

## Comandi utili prima di tutto

```bash
# Uccidi processi su porte usate dal progetto
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null

# Verifica che le porte siano libere
lsof -i:8000 -i:8001
```

---

## Pezzo 1 — `core/db.py`

Schema SQLite (documents, reports, events) + PRAGMA WAL.

```bash
# Smoke test: insert + read su tutte e 3 le tabelle
.venv/bin/python -m core.db
```

Output atteso: stampa document, report ed event inseriti, poi li rilegge.

```bash
# Verifica schema e WAL direttamente
sqlite3 data/albo_sicuro.db "PRAGMA journal_mode;"
# → wal

sqlite3 data/albo_sicuro.db ".schema"
# → mostra CREATE TABLE documents / reports / events

sqlite3 data/albo_sicuro.db "SELECT * FROM documents;"
sqlite3 data/albo_sicuro.db "SELECT * FROM reports;"
sqlite3 data/albo_sicuro.db "SELECT * FROM events;"
```

---

## Pezzo 2 — `core/precedents.py`

Lookup su `data/schede_provvedimenti.json`.

```bash
.venv/bin/python -m core.precedents
```

Output atteso (ogni riga mostra categoria/tipo → id_provvedimento trovato):
- `[salute / determina_dirigenziale]` → `ordinanza-3-2020`
- `[giudiziario / determina_dirigenziale]` → `ordinanza-118-2020`
- `[None / delibera]` → `None`
- `[inesistente / delibera]` → `None`

---

## Pezzo 3 — `core/pipeline.py`

Stub intelligente: legge labels.json, apre il PDF con fitz, calcola hash.

```bash
.venv/bin/python -m core.pipeline
```

Output atteso:
```
✓ graduatoria_concorso_01.pdf     → conforme, precedente=None, passaggi=0
✓ 03_determina_sospensione...pdf  → non_conforme, precedente=ordinanza-118-2020
✓ atto_vicenda_giudiziaria_07.pdf → non_conforme, precedente=provv-afragola-2022
✓ determina_contributo_salute_03  → non_conforme, precedente=ordinanza-3-2020
✓ PDF non in labels               → da_verificare
```

---

## Pezzo 4 — `comune_fake/main.py` (porta 8001)

Sito finto del Comune.

```bash
# Avvio (con auto-reload per sviluppo)
.venv/bin/uvicorn comune_fake.main:app --port 8001 --reload

# Se la porta è occupata, prima:
lsof -ti:8001 | xargs kill -9
```

### Endpoint da verificare

```bash
# 4 atti seed in JSON (mix conforme + salute + disagio + giudiziario)
curl http://localhost:8001/api/atti | python3 -m json.tool

# Pagina HTML pubblica
open http://localhost:8001/albo

# PDF statico (sostituisci il nome con quello reale in atti.json)
curl -I http://localhost:8001/albo_fake/001_graduatoria_concorso_01.pdf
# → HTTP/1.1 200 OK

# Pannello admin
open http://localhost:8001/admin
```

### Test admin via curl

```bash
# Pubblica un nuovo atto scegliendo dal dataset
curl -X POST http://localhost:8001/admin/pubblica \
  -F "titolo=Test atto giudiziario" \
  -F "tipo_atto=determina_dirigenziale" \
  -F "pdf_dataset=03_determina_sospensione_procedimento_penale.pdf"

# Verifica che l'atto sia apparso
curl http://localhost:8001/api/atti | python3 -m json.tool

# Rimuovi l'atto appena creato (sostituisci 005 con l'id reale)
curl -X POST http://localhost:8001/admin/rimuovi/005

# Verifica rimozione
curl http://localhost:8001/api/atti | python3 -m json.tool
```

### Reset del sito finto (riparte da zero)

```bash
rm data/albo_fake/atti.json
rm data/albo_fake/pdf/*.pdf
# Poi riavvia uvicorn → ri-publica i 4 atti seed automaticamente
```

---

## Pezzo 5 — `core/downloader.py`

Richiede il sito finto attivo su :8001.

```bash
.venv/bin/uvicorn comune_fake.main:app --port 8001 --log-level warning &
sleep 2
.venv/bin/python -m core.downloader
```

Output atteso:
```
✓ Download riuscito: 001_graduatoria_concorso_01.pdf (75461 byte)
✓ URL inesistente → None (nessun crash)
✓ Host irraggiungibile → None (nessun crash)
```

---

## Pezzo 6 — `daemon/watcher.py`

### Reset completo (riparte da zero)

```bash
lsof -ti:8001 | xargs kill -9 2>/dev/null
sqlite3 data/albo_sicuro.db \
  "DELETE FROM events; DELETE FROM reports; DELETE FROM documents; DELETE FROM sqlite_sequence;"
rm -f data/albo_fake/atti.json data/albo_fake/pdf/*.pdf data/last_check.txt
```

### Avvio in due terminali separati

```bash
# Terminale 1 — sito finto
.venv/bin/uvicorn comune_fake.main:app --port 8001 --log-level warning

# Terminale 2 — demone in loop
.venv/bin/python daemon/watcher.py
```

### Test: un ciclo singolo (senza loop)

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from daemon.watcher import poll
from core import db
db.init_db()
poll()
"
```

Output atteso (4 atti seed):
```
NUOVO [001] Graduatoria Concorso 01      → conforme      | precedente: —
NUOVO [002] Determina Contributo Salute  → non_conforme  | precedente: ordinanza-3-2020
NUOVO [003] Determina Sussidio Disagio   → non_conforme  | precedente: provv-tricase-2021
NUOVO [004] Atto Vicenda Giudiziaria     → non_conforme  | precedente: provv-afragola-2022
── visti=4 nuovi=4 sostituiti=0 rimossi=0 ──
```

Al secondo ciclo (URL invariate): `nuovi=0 sostituiti=0 rimossi=0` — **nessun download**.

### Test: pubblica atti nuovi via admin e verifica

```bash
# Pubblica conforme
curl -X POST http://localhost:8001/admin/pubblica \
  -F "titolo=Graduatoria Concorso Istruttore Tecnico" \
  -F "tipo_atto=graduatoria" \
  -F "pdf_dataset=graduatoria_concorso_01.pdf"

# Pubblica giudiziario
curl -X POST http://localhost:8001/admin/pubblica \
  -F "titolo=Determina Sospensione Procedimento Penale" \
  -F "tipo_atto=determina_dirigenziale" \
  -F "pdf_dataset=03_determina_sospensione_procedimento_penale.pdf"

# Esegui un ciclo → solo i 2 nuovi scaricati
.venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from daemon.watcher import poll; poll()
"
```

### Query SQLite di verifica finale

```bash
sqlite3 -column -header data/albo_sicuro.db "
SELECT
  d.id_atto_albo,
  r.verdetto,
  json_extract(r.precedente_json, '$.id_provvedimento') AS precedente,
  json_extract(r.precedente_json, '$.categoria_violazione') AS categoria,
  json_extract(r.precedente_json, '$.norma_violata') AS norma
FROM reports r
JOIN documents d ON r.document_id = d.id
ORDER BY d.id_atto_albo;
"
```

Risultato atteso per i 2 atti pubblicati manualmente:
- `005` → `conforme`, precedente=NULL, categoria=NULL
- `006` → `non_conforme`, precedente=`ordinanza-118-2020`, categoria=`giudiziario`

---

## Query SQLite utili (dopo che il demone gira)

```bash
# Tutti i documenti monitorati
sqlite3 data/albo_sicuro.db \
  "SELECT id, id_atto_albo, titolo, stato, hash FROM documents ORDER BY created_at DESC;"

# Tutti i report con verdetto e precedente
sqlite3 data/albo_sicuro.db \
  "SELECT r.id, d.titolo, r.verdetto, r.gravita_max,
          json_extract(r.precedente_json, '$.id_provvedimento') as precedente
   FROM reports r JOIN documents d ON r.document_id = d.id
   ORDER BY r.created_at DESC;"

# Cronologia eventi
sqlite3 data/albo_sicuro.db \
  "SELECT e.timestamp, d.titolo, e.tipo, e.descrizione
   FROM events e JOIN documents d ON e.document_id = d.id
   ORDER BY e.timestamp DESC LIMIT 20;"

# Verifica WAL attivo
sqlite3 data/albo_sicuro.db "PRAGMA journal_mode;"
```

---

## Processi in parallelo (tutti e 3 insieme)

```bash
# Terminale 1 — sito finto Comune
.venv/bin/uvicorn comune_fake.main:app --port 8001

# Terminale 2 — demone (dopo che il pezzo 6 è pronto)
.venv/bin/python daemon/watcher.py

# Terminale 3 — app principale (dopo che web/main.py è pronto)
.venv/bin/uvicorn web.main:app --port 8000
```
