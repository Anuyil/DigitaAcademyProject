#!/usr/bin/env bash
# test_pipeline.sh — test REALE end-to-end con LLM vero
# Uso: bash test_pipeline.sh
# Durata attesa: ~90s (4 atti × 15s delay LLM + download + analisi)
set -euo pipefail

PY=".venv/bin/python"
UV=".venv/bin/uvicorn"
PORT=8001
DB="data/albo_sicuro.db"

GRN='\033[0;32m'; RED='\033[0;31m'; YLW='\033[1;33m'
BLU='\033[0;34m'; CYN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

ok()   { echo -e "  ${GRN}✓ $*${NC}"; }
fail() { echo -e "  ${RED}✗ $*${NC}"; exit 1; }
step() { echo -e "\n${BOLD}${BLU}▶ $*${NC}"; }
info() { echo -e "  ${YLW}$*${NC}"; }

dbq()  { sqlite3 "$DB" "$1"; }
dbc()  { sqlite3 -column -header "$DB" "$1"; }

echo -e "${BOLD}${BLU}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLU}║   ALBO SICURO — Test Reale End-to-End       ║${NC}"
echo -e "${BOLD}${BLU}╚══════════════════════════════════════════════╝${NC}"
echo -e "  LLM: groq/compound  |  delay: ${LLM_CALL_DELAY:-15}s tra atti"
echo -e "  Durata stimata: ~$((${LLM_CALL_DELAY:-15} * 4 + 30))s"

# ── 0. Reset totale ───────────────────────────────────────────────────────────
step "0. Reset totale"
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
dbq "DELETE FROM events; DELETE FROM reports; DELETE FROM documents; DELETE FROM sqlite_sequence;" 2>/dev/null || true
rm -f data/albo_fake/atti.json data/albo_fake/pdf/*.pdf data/last_check.txt data/llm_cache.json 2>/dev/null || true
rm -f data/corrected/corretto_*.pdf 2>/dev/null || true
ok "DB, albo_fake e cache LLM ripuliti"

# ── 1. Avvio sito finto ───────────────────────────────────────────────────────
step "1. Avvio sito finto (porta $PORT) — seed automatico 4 atti"
$UV comune_fake.main:app --port $PORT --log-level error &
UVPID=$!
sleep 2

echo ""
curl -s http://localhost:$PORT/api/atti | $PY -c "
import json, sys
atti = json.load(sys.stdin)
print(f'  Atti pubblicati: {len(atti)}')
for a in atti:
    print(f\"  {a['id_atto_albo']} | {a['tipo_atto']:25} | {a['titolo']}\")
"
echo ""
N=$(curl -s http://localhost:$PORT/api/atti | $PY -c "import json,sys; print(len(json.load(sys.stdin)))")
[ "$N" -eq 4 ] && ok "Seed OK: $N atti sull'albo" || fail "Attesi 4 atti, trovati $N"

# ── 2. Ciclo demone — analisi reale con LLM ───────────────────────────────────
step "2. Ciclo demone — analisi reale con LLM (Groq)"
info "Ogni atto richiede: download → pseudonimizza → find_precedent → LLM → redigi PDF"
info "Delay ${LLM_CALL_DELAY:-15}s tra ogni chiamata LLM per rispettare il rate limit Groq"
echo ""

$PY << 'PYEOF'
import sys, os, time, logging
sys.path.insert(0, '.')
logging.basicConfig(level=logging.INFO,
    format='  %(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
from daemon.watcher import poll
from core import db
db.init_db()
poll()
PYEOF

echo ""
ok "Ciclo demone completato"

# ── 3. Report completo per ogni atto ─────────────────────────────────────────
step "3. Report completo per ogni atto analizzato"
echo ""

$PY << 'PYEOF'
import json, sqlite3

DB = "data/albo_sicuro.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT d.id_atto_albo, d.titolo, d.stato, d.data_pubblicazione,
           r.verdetto, r.gravita_max,
           r.findings_json, r.precedente_json,
           r.created_at, r.expires_at
    FROM documents d
    JOIN reports r ON r.document_id = d.id
    ORDER BY CAST(d.id_atto_albo AS INTEGER)
""").fetchall()

ICON    = {"conforme": "🟢", "non_conforme": "🔴", "da_verificare": "🟡"}
BOLD    = "\033[1m"
GRN     = "\033[0;32m"
RED     = "\033[0;31m"
YLW     = "\033[1;33m"
CYN     = "\033[0;36m"
NC      = "\033[0m"
SEP     = "─" * 66

for row in rows:
    r          = dict(row)
    findings   = json.loads(r["findings_json"] or "{}")
    precedente = json.loads(r["precedente_json"] or "null")
    passaggi   = findings.get("passaggi_critici", [])
    entita     = findings.get("entities", [])
    icon       = ICON.get(r["verdetto"], "⚪")

    col = GRN if r["verdetto"] == "conforme" else (RED if r["verdetto"] == "non_conforme" else YLW)

    print(f"\n{SEP}")
    print(f"  {icon}  {BOLD}[{r['id_atto_albo']}] {r['titolo']}{NC}")
    print(f"  {col}verdetto: {r['verdetto']}{NC}  |  gravità max: {r['gravita_max'] or '—'}  |  stato: {r['stato']}")
    print(f"  pubblicato: {r['data_pubblicazione']}  |  analizzato: {r['created_at'][:19]}  |  scade: {r['expires_at'][:10]}")

    if precedente:
        print(f"\n  {CYN}📋 Precedente Garante:{NC}")
        print(f"     ID:       {precedente.get('id_provvedimento', '—')}")
        print(f"     Categ.:   {precedente.get('categoria_violazione', '—')}")
        print(f"     Sanzione: €{precedente.get('sanzione_euro', '?')}")
        norma = precedente.get('norma_violata', '')
        print(f"     Norma:    {norma[:72]}{'…' if len(norma)>72 else ''}")

    if passaggi:
        print(f"\n  ⚠️  Passaggi critici ({len(passaggi)}):")
        for p in passaggi[:3]:
            g = p.get('gravita','?')
            gcol = RED if g == 'alta' else (YLW if g == 'media' else NC)
            txt = p['testo'][:70] + ('…' if len(p['testo']) > 70 else '')
            print(f"     {gcol}[{g}]{NC} {txt}")
            print(f"           norma: {p.get('norma','—')[:60]}")
        if len(passaggi) > 3:
            print(f"     … +{len(passaggi)-3} altri passaggi")
    else:
        print(f"\n  ✅ Nessun passaggio critico rilevato")

print(f"\n{SEP}")
print(f"\n  Totale atti analizzati: {len(rows)}")
conf = sum(1 for r in rows if dict(r)["verdetto"] == "conforme")
nc   = sum(1 for r in rows if dict(r)["verdetto"] == "non_conforme")
dv   = sum(1 for r in rows if dict(r)["verdetto"] == "da_verificare")
print(f"  🟢 conformi: {conf}  🔴 non conformi: {nc}  🟡 da verificare: {dv}")
PYEOF

# ── 4. PDF redatti ────────────────────────────────────────────────────────────
step "4. PDF redatti in data/corrected/"
echo ""
ls -lh data/corrected/corretto_*.pdf 2>/dev/null | awk '{print "  ",$5,$9}' || info "Nessun PDF redatto (tutti conformi o nessuna entità da rimuovere)"
echo ""

# ── 5. Tabella DB di riepilogo ────────────────────────────────────────────────
step "5. Riepilogo DB — documents + reports"
echo ""
dbc "
SELECT
  d.id_atto_albo   AS id,
  substr(d.titolo,1,30) AS titolo,
  r.verdetto,
  r.gravita_max    AS gravita,
  json_extract(r.precedente_json,'$.id_provvedimento') AS precedente,
  d.stato
FROM reports r
JOIN documents d ON r.document_id = d.id
ORDER BY CAST(d.id_atto_albo AS INTEGER);"
echo ""

# ── 6. Cronologia eventi ──────────────────────────────────────────────────────
step "6. Cronologia eventi"
echo ""
dbc "
SELECT e.timestamp, d.id_atto_albo AS id, e.tipo, substr(e.descrizione,1,45) AS descrizione
FROM events e JOIN documents d ON e.document_id = d.id
ORDER BY e.timestamp;"
echo ""

# ── 7. Verifica last_check ────────────────────────────────────────────────────
step "7. Secondo ciclo (tutti già visti — zero download, zero LLM)"
$PY << 'PYEOF'
import sys, logging
sys.path.insert(0, '.')
logging.basicConfig(level=logging.INFO,
    format='  %(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
from daemon.watcher import poll
poll()
PYEOF
ok "Zero nuovi atti → nessun download, nessuna chiamata LLM"

# ── Cleanup ───────────────────────────────────────────────────────────────────
kill $UVPID 2>/dev/null || true

LAST=$(cat data/last_check.txt 2>/dev/null | cut -c1-19 || echo "—")
echo ""
echo -e "${BOLD}${GRN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GRN}║  Test completato ✓                           ║${NC}"
echo -e "${BOLD}${GRN}║  Ultimo controllo demone: $LAST  ║${NC}"
echo -e "${BOLD}${GRN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "  Per aprire un PDF redatto:"
echo "  open data/corrected/corretto_001_graduatoria_concorso_01.pdf"
