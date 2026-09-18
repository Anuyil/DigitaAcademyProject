"""
core/llm.py — analisi LLM del testo pseudonimizzato.

Flusso:
  pseudo_text + precedente → Groq (principale) → Gemini (riserva) → fallback detectors
  Cache su data/llm_cache.json, chiave sha256(pseudo_text).
  MAI testo originale all'LLM — solo segnaposto [PERSONA_1], [CF_1], ecc.
"""

import hashlib
import json
import logging
import os
import re
from pathlib import Path

import openai
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

_ROOT       = Path(__file__).parent.parent
_CACHE_PATH = _ROOT / os.getenv("LLM_CACHE_PATH", "data/llm_cache.json")

# ── system prompt (costante fissa, in italiano) ───────────────────────────────

_SYSTEM_PROMPT = """Sei un assistente specializzato nell'analisi di atti amministrativi \
italiani pubblicati sull'Albo Pretorio online. Valuta se il testo contiene dati personali \
eccedenti o non necessari rispetto alle finalità di trasparenza amministrativa.

NORMATIVA DI RIFERIMENTO:
- Linee guida Garante Privacy 15/05/2014: pubblicazione atti online da parte delle PA
- Art. 2-septies Codice Privacy (d.lgs. 196/2003): vietata diffusione di dati sulla salute
- Art. 26 c.4 d.lgs. 33/2013: vietati dati identificativi dei beneficiari di contributi \
economici se rivelano salute o disagio economico-sociale
- Art. 5 GDPR (UE 2016/679): minimizzazione — dati adeguati, pertinenti e limitati allo stretto necessario
- Art. 9 GDPR: tutela rafforzata per categorie particolari (salute, origine etnica, ecc.)
- Art. 10 GDPR e art. 2-octies Codice Privacy: tutela per dati su condanne penali e reati
- Tutela rafforzata dei minori in qualsiasi contesto

REGOLE OPERATIVE:
- Nomi in graduatorie di concorso ed esiti di gara sono in genere legittimi
- Numeri di protocollo, nomi di dirigenti e uffici: mantenere (dati istituzionali)
- Diagnosi, patologie, ISEE, IBAN personali, vicende giudiziarie individuali: quasi sempre eccedenti
- Se è fornito un precedente reale del Garante, citalo nella motivazione e nel campo norma
- Se non è fornito un precedente, basati solo sulle regole sopra
- Non dare mai un verdetto netto senza motivazione esplicita
- Se il contesto è ambiguo usa verdetto "da_verificare"

FORMATO RISPOSTA: rispondi SOLO con JSON valido, senza testo aggiuntivo e senza markdown."""

# ── helpers ───────────────────────────────────────────────────────────────────

_PH_RE = re.compile(
    r'\[(CF|IBAN|PERSONA|INDIRIZZO|EMAIL|TEL|TARGA|DATA_NASCITA)_(\d+)\]'
)

# Azioni prudenziali per tipo di segnaposto, usate nel fallback
_FALLBACK_AZIONE = {
    "CF":            "rimuovere",
    "IBAN":          "rimuovere",
    "DATA_NASCITA":  "rimuovere",
    "EMAIL":         "rimuovere",
    "TEL":           "rimuovere",
    "PERSONA":       "minimizzare",
    "INDIRIZZO":     "minimizzare",
    "TARGA":         "minimizzare",
}


def _cache_key(pseudo_text: str) -> str:
    return hashlib.sha256(pseudo_text.encode()).hexdigest()


def _load_cache() -> dict:
    if _CACHE_PATH.exists():
        try:
            return json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_cache(cache: dict) -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2))


def _parse_json(content: str) -> dict:
    """Estrae JSON dalla risposta LLM anche se avvolta in markdown."""
    content = content.strip()
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content).strip()
    start, end = content.find('{'), content.rfind('}')
    if start == -1 or end == -1:
        raise ValueError(f"Nessun oggetto JSON trovato nella risposta: {content[:120]}")
    return json.loads(content[start:end + 1])


def _call_provider(client: openai.OpenAI, model: str, messages: list) -> dict:
    """Chiama l'API; prova con json_object, poi senza se non supportato."""
    for kwargs in [
        {"response_format": {"type": "json_object"}},
        {},
    ]:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                **kwargs,
            )
            return _parse_json(resp.choices[0].message.content)
        except openai.BadRequestError:
            continue  # json_object non supportato, riprova senza
        except openai.NotFoundError:
            raise  # modello inesistente, inutile riprovare
    raise RuntimeError(f"Nessuna modalità di chiamata funzionante per {model}")


def _build_messages(pseudo_text: str, precedente: dict | None) -> list[dict]:
    prec_block = ""
    if precedente:
        prec_block = (
            f"\nPRECEDENTE DEL GARANTE PERTINENTE:\n"
            f"ID: {precedente.get('id_provvedimento', '')}\n"
            f"Norma violata: {precedente.get('norma_violata', '')}\n"
            f"Fatti: {precedente.get('descrizione_fatti', '')}\n"
            f"Sanzione: €{precedente.get('sanzione_euro', 'N/D')}\n"
        )

    user_msg = f"""Analizza questo atto amministrativo pubblicato sull'Albo Pretorio.
I dati identificativi reali sono stati sostituiti con segnaposto ([PERSONA_1], [CF_1], ecc.).
{prec_block}
TESTO:
---
{pseudo_text}
---

Rispondi SOLO con JSON con questa struttura:
{{
  "tipo_atto": "determina_dirigenziale|delibera|ordinanza|graduatoria|altro",
  "verdetto": "conforme|da_verificare|non_conforme",
  "decisioni": [
    {{"placeholder": "[PERSONA_1]", "azione": "mantenere|rimuovere|minimizzare",
      "motivazione": "...", "norma": "..."}}
  ],
  "passaggi_critici": [
    {{"testo": "frase esatta copiata dal testo con i segnaposto",
      "categoria": "salute|disagio_economico|minori|giudiziario|altro",
      "gravita": "alta|media|bassa", "motivazione": "...", "norma": "..."}}
  ]
}}"""

    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user",   "content": user_msg},
    ]


def _fallback(pseudo_text: str) -> dict:
    """
    Risposta conservativa quando entrambe le API sono irraggiungibili.
    Suggerisce azioni prudenziali per ogni segnaposto trovato nel testo.
    """
    seen: dict[str, dict] = {}
    for m in _PH_RE.finditer(pseudo_text):
        ph = m.group(0)
        if ph not in seen:
            tipo = m.group(1)
            seen[ph] = {
                "placeholder": ph,
                "azione":      _FALLBACK_AZIONE.get(tipo, "rimuovere"),
                "motivazione": "API LLM non raggiungibile — verifica manuale necessaria.",
                "norma":       "",
            }
    return {
        "tipo_atto":        "altro",
        "verdetto":         "da_verificare",
        "decisioni":        list(seen.values()),
        "passaggi_critici": [],
    }


# ── API pubblica ──────────────────────────────────────────────────────────────

def analyze(pseudo_text: str, precedente: dict | None = None) -> dict:
    """
    Analizza pseudo_text con l'LLM e restituisce verdetto + decisioni + passaggi_critici.
    Usa la cache; se entrambi i provider falliscono restituisce il fallback (da_verificare).
    MAI inviare testo originale — solo segnaposto.
    """
    # Cache
    key   = _cache_key(pseudo_text)
    cache = _load_cache()
    if key in cache:
        log.info("LLM cache hit")
        return cache[key]

    messages = _build_messages(pseudo_text, precedente)

    # Provider principale: Groq
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_key:
        try:
            client = openai.OpenAI(
                api_key  = groq_key,
                base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            )
            model  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            result = _call_provider(client, model, messages)
            log.info(f"LLM Groq OK — verdetto={result.get('verdetto')}")
            cache[key] = result
            _save_cache(cache)
            return result
        except Exception as e:
            log.warning(f"Groq fallita: {e}")

    # Riserva: Gemini
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            client = openai.OpenAI(
                api_key  = gemini_key,
                base_url = os.getenv(
                    "GEMINI_BASE_URL",
                    "https://generativelanguage.googleapis.com/v1beta/openai/",
                ),
            )
            model  = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            result = _call_provider(client, model, messages)
            log.info(f"LLM Gemini OK — verdetto={result.get('verdetto')}")
            cache[key] = result
            _save_cache(cache)
            return result
        except Exception as e:
            log.warning(f"Gemini fallita: {e}")

    # Fallback: nessuna API disponibile
    log.error("Entrambi i provider LLM non disponibili — uso fallback da_verificare")
    return _fallback(pseudo_text)


# ── smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    PSEUDO = (
        "Determinazione dirigenziale relativa a [PERSONA_1], nato il [DATA_NASCITA_1], "
        "C.F. [CF_1], affetto da patologia oncologica invalidante al 100%. "
        "Liquidazione parcella all'[PERSONA_2] (C.F. [CF_2]) sul conto [IBAN_1]. "
        "Prot. n. 9921/2023 — Dirigente: dott. Verdi."
    )

    PREC = {
        "id_provvedimento": "ordinanza-3-2020",
        "norma_violata":    "art. 2-septies c.8 Codice privacy; art. 9 GDPR; art. 5.1.c GDPR",
        "descrizione_fatti": (
            "Determina con patologia del dipendente e IBAN del legale pubblicati sull'albo."
        ),
        "sanzione_euro": 10000,
    }

    print("=== Test analyze() ===")
    result = analyze(PSEUDO, precedente=PREC)
    print(f"  tipo_atto:  {result.get('tipo_atto')}")
    print(f"  verdetto:   {result.get('verdetto')}")
    print(f"  decisioni:  {len(result.get('decisioni', []))}")
    print(f"  passaggi:   {len(result.get('passaggi_critici', []))}")
    for d in result.get("decisioni", []):
        print(f"    {d['placeholder']:20} → {d['azione']:12} | {d.get('norma','')[:50]}")
    for p in result.get("passaggi_critici", []):
        print(f"    [{p.get('gravita','?')}] {p['testo'][:70]}")

    print("\n=== Test cache (secondo call = cache hit) ===")
    result2 = analyze(PSEUDO, precedente=PREC)
    assert result2 == result, "Cache non funziona!"
    print("  ✓ cache hit confermato")

    print("\n=== Test fallback (pseudo_text senza API key) ===")
    old_groq, old_gem = os.environ.pop("GROQ_API_KEY", ""), os.environ.pop("GEMINI_API_KEY", "")
    # Usa un testo diverso per evitare cache hit
    fb = analyze("[PERSONA_1] ha ricevuto contributo. C.F. [CF_1] e [IBAN_1].")
    assert fb["verdetto"] == "da_verificare"
    assert any(d["placeholder"] == "[PERSONA_1]" for d in fb["decisioni"])
    print(f"  ✓ fallback: verdetto={fb['verdetto']}, decisioni={len(fb['decisioni'])}")
    for d in fb["decisioni"]:
        print(f"    {d['placeholder']:20} → {d['azione']}")
    if old_groq:
        os.environ["GROQ_API_KEY"] = old_groq
    if old_gem:
        os.environ["GEMINI_API_KEY"] = old_gem

    print("\n✓ Tutti i test completati")
