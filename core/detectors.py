"""
core/detectors.py — pseudonimizzazione del testo prima dell'invio all'LLM.

Entità rilevate (priorità decrescente per la gestione degli overlap):
  CF           regex + stdnum validation
  IBAN         regex + stdnum validation
  EMAIL        regex
  TARGA        regex
  TEL          regex (numeri italiani)
  DATA_NASCITA regex contestuale (nato/nata il ...)
  PERSONA      spaCy PER + euristiche sig./dott./avv.
  INDIRIZZO    spaCy LOC

Principio: l'LLM vede [PERSONA_1], [CF_1] ecc., MAI i valori reali.
La mappa placeholder→valore reale resta solo in DB/memoria locale.
"""

import re

# Carica spaCy una volta sola; degrada gracefully se non disponibile
try:
    import spacy as _spacy
    _NLP = _spacy.load("it_core_news_sm")
except (ImportError, OSError):
    _NLP = None

# Prova la validazione con stdnum; degrada se non installato
try:
    from stdnum.it import codicefiscale as _cf_lib
    from stdnum import iban as _iban_lib
    _HAS_STDNUM = True
except ImportError:
    _HAS_STDNUM = False


# ── termini istituzionali che spaCy non deve mai taggare come entità ─────────
# (tipi di atto, istituzioni, mesi, ruoli — mai dati personali)
_SPACY_SKIP: set[str] = {
    # tipi di atto
    "ordinanza", "delibera", "determina", "determinazione", "decreto",
    "legge", "articolo", "comma", "lettera", "allegato", "protocollo",
    "provvedimento", "circolare", "nota", "verbale", "atto",
    # istituzioni e uffici
    "comune", "provincia", "regione", "stato", "governo", "nazione",
    "tribunale", "procura", "questura", "prefettura", "corte", "gip",
    "ministero", "agenzia", "ente", "istituto", "ufficio", "settore",
    "consiglio", "giunta", "commissione", "dipartimento", "direzione",
    "polizia", "carabinieri", "guardia", "municipio",
    # ruoli
    "sindaco", "assessore", "dirigente", "funzionario", "responsabile",
    "segretario", "presidente", "vicepresidente", "consigliere",
    "cittadino", "dipendente", "beneficiario", "richiedente",
    "trasgressore", "indagato", "imputato", "destinatario",
    "istruttore", "istruttori", "amministrativo", "amministrativi",
    "candidato", "candidati", "vincitore", "idoneo",
    # incipit tipici degli atti amministrativi (participi/verbi che spaCy
    # confonde con nomi propri quando iniziano una frase)
    "visto", "vista", "visti", "viste", "considerato", "considerata",
    "considerati", "considerate", "accertato", "accertata",
    "richiamato", "richiamata", "premesso", "premessa", "rilevato",
    "rilevata", "ritenuto", "ritenuta", "atteso", "attesa", "dato",
    "sentito", "sentita", "preso", "presa", "acquisito", "acquisita",
    # etichette di modulo/tabella e titoli, mai dati personali
    "registro", "trasparenza", "pubblicazione", "pubblicazioni",
    "posizione", "punteggio", "titoli", "prove", "totale", "esito",
    "cognome", "nome", "buoni", "spesa", "sostegno", "locazione",
    # abbreviazioni di titolo isolate (senza il nome che segue): spaCy a
    # volte le tagga da sole come LOC — non portano nessuna informazione
    "dott", "sig", "avv", "geom", "arch", "prof", "dr",
    # mesi (spacy li confonde con nomi propri in italiano)
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
    # città italiane — appaiono sia in contesti personali sia istituzionali
    # ("nato a Napoli" MA ANCHE "Tribunale di Napoli") → non oscurare mai
    "napoli", "roma", "milano", "torino", "firenze", "venezia", "bologna",
    "palermo", "genova", "catania", "bari", "messina", "padova", "trieste",
    "brescia", "parma", "modena", "livorno", "cagliari", "foggia", "salerno",
    "ferrara", "rimini", "ravenna", "siracusa", "pescara", "bergamo", "verona",
    "nola", "avellino", "caserta", "benevento", "ottaviano", "portici",
    "ercolano", "castellammare", "pozzuoli", "giugliano", "aversa",
    "italia", "campania", "lazio", "sicilia", "lombardia", "puglia",
}

# parole che segnalano un vero indirizzo (via, numero civico, ecc.) — usate
# per capire se un'entità "LOC" di spaCy è davvero un luogo o un nome di
# persona mal etichettato (vedi punto 8 di pseudonymize)
_ADDRESS_KEYWORDS: set[str] = {
    "via", "viale", "piazza", "piazzale", "corso", "largo", "vicolo",
    "strada", "frazione", "contrada", "traversa", "vico", "rione",
    "borgo", "località", "localita", "c", "so", "p",
}


# ── pattern regex ─────────────────────────────────────────────────────────────

# CF: 6 lettere + 2 alfanumerici + 1 lettera mese + 2 cifre + 1 lettera + 3 alfanumerici + 1 lettera
_CF_RE = re.compile(
    r'\b([A-Z]{6}[0-9LMNPQRSTUV]{2}[ABCDEHLMPRST][0-9LMNPQRSTUV]{2}'
    r'[A-Z][0-9LMNPQRSTUV]{3}[A-Z])\b',
    re.IGNORECASE,
)

# IBAN italiano senza spazi (IT + 2 check + 23 BBAN = 27 car)
_IBAN_RE = re.compile(
    r'\b(IT\d{2}[A-Z][A-Z0-9]{22})\b',
    re.IGNORECASE,
)

_EMAIL_RE = re.compile(
    r'\b([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})\b'
)

# Targhe italiane: 2 lettere + 3 cifre + 2 lettere (formato post-1994)
_TARGA_RE = re.compile(r'\b([A-Z]{2}\d{3}[A-Z]{2})\b', re.IGNORECASE)

# Telefoni italiani: fisso (0...) o mobile (3...)
_TEL_RE = re.compile(
    r'\b(\+?39[\s\-]?)?'
    r'((?:0\d{1,4}[\s\-]?\d{3,8}|3[0-9]{2}[\s\-]?[0-9]{6,7}))\b'
)

# Data di nascita in contesto "nato[/a] [a Città] [il] GG/MM/AAAA"
_DATA_NASCITA_RE = re.compile(
    r'\b(?:nato|nata|n\.)\b[^,;\n]{0,40}?'
    r'(\d{1,2}[/\.\-]\d{1,2}[/\.\-]\d{4})',
    re.IGNORECASE,
)

# Euristiche titoli: cattura il NOME dopo il titolo (sig., avv., dott. …)
# NB: l'IGNORECASE va applicato SOLO al prefisso del titolo — se si applica a
# tutto il pattern, la classe [A-Z] nel gruppo del nome perde il vincolo di
# maiuscola e il match "ingoia" qualsiasi parola minuscola successiva, anche
# oltre l'a-capo (es. "Dott.ssa Valeria Moretti" + tutto il testo seguente).
# Il separatore è limitato a spazio/tab (mai \n) per non unire righe diverse,
# e il numero di parole del nome è limitato per evitare match a valanga.
_TITOLO_RE = re.compile(
    r'\b(?:(?i:sig\.(?:ra)?|dott(?:\.ssa)?|avv\.|ing\.|geom\.|arch\.|prof\.(?:ssa)?|dr\.?))[ \t]+'
    r'([A-ZÀÈÉÌÒÙÜ][a-zàèéìòùü]+(?:[ \t]+[A-ZÀÈÉÌÒÙÜ][a-zàèéìòùü]+){0,2})'
)

# Priorità per la risoluzione degli overlap (più basso = più prioritario)
_PRIORITY = {
    "CF": 0, "IBAN": 1, "EMAIL": 2, "TARGA": 3,
    "TEL": 4, "DATA_NASCITA": 5, "PER": 6, "LOC": 7,
}

# Mappa tipo → prefisso del placeholder
_PREFIX = {
    "CF": "CF", "IBAN": "IBAN", "EMAIL": "EMAIL",
    "TARGA": "TARGA", "TEL": "TEL", "DATA_NASCITA": "DATA_NASCITA",
    "PER": "PERSONA", "LOC": "INDIRIZZO",
}


# ── funzioni pubbliche ────────────────────────────────────────────────────────

def mask(value: str) -> str:
    """Maschera un valore per log/DB: RSS***39X, IT60***456."""
    v = value.replace(" ", "")
    if len(v) <= 6:
        return v[:1] + "***" if v else "***"
    return v[:3] + "***" + v[-3:]


def pseudonymize(text: str) -> dict:
    """
    Sostituisce entità sensibili con segnaposto coerenti.

    Ritorna:
      {
        "pseudo_text": str,
        "mapping": {"[CF_1]": "RSSMRA80A01F839X", ...},
        "entities": [{"placeholder", "type", "value", "start", "end"}]
      }
    """
    raw_spans: list[tuple[int, int, str, str]] = []  # (start, end, type, value)

    # 1. CF
    for m in _CF_RE.finditer(text):
        val = m.group(1).upper()
        if _HAS_STDNUM:
            if not _cf_lib.is_valid(val):
                continue
        raw_spans.append((m.start(1), m.end(1), "CF", val))

    # 2. IBAN
    for m in _IBAN_RE.finditer(text):
        val = m.group(1).upper().replace(" ", "")
        if _HAS_STDNUM:
            if not _iban_lib.is_valid(val):
                continue
        raw_spans.append((m.start(1), m.end(1), "IBAN", val))

    # 3. Email
    for m in _EMAIL_RE.finditer(text):
        raw_spans.append((m.start(1), m.end(1), "EMAIL", m.group(1)))

    # 4. Targa
    for m in _TARGA_RE.finditer(text):
        raw_spans.append((m.start(1), m.end(1), "TARGA", m.group(1).upper()))

    # 5. Telefono (solo il numero, senza il prefisso +39 opzionale)
    for m in _TEL_RE.finditer(text):
        num_grp = m.group(2)
        if num_grp:
            s = text.index(num_grp, m.start())
            raw_spans.append((s, s + len(num_grp), "TEL", num_grp))

    # 6. Data di nascita (solo la data, non il contesto "nato a Città il")
    for m in _DATA_NASCITA_RE.finditer(text):
        s, e = m.start(1), m.end(1)
        raw_spans.append((s, e, "DATA_NASCITA", m.group(1)))

    # 7. Euristiche titoli: cattura solo il nome
    for m in _TITOLO_RE.finditer(text):
        nome = m.group(1)
        s = m.start(1)
        raw_spans.append((s, s + len(nome), "PER", nome))

    # 8. spaCy PER e LOC — con filtro per falsi positivi istituzionali
    if _NLP is not None:
        doc = _NLP(text)
        for ent in doc.ents:
            if ent.label_ not in ("PER", "LOC"):
                continue
            val = ent.text.strip()
            if len(val) < 3:
                continue
            # span che attraversa un a-capo: quasi sempre un artefatto di
            # estrazione testo (intestazioni/tabelle), mai un nome reale
            if "\n" in val:
                continue
            # scarta l'intera entità se una qualsiasi delle sue parole è un
            # termine istituzionale/di modulo — mai un dato personale
            words = re.findall(r"[\wàèéìòù]+", val.lower())
            if any(w in _SPACY_SKIP for w in words):
                continue
            # spaCy scambia spesso PER/LOC su nomi di persona in elenchi e
            # firme: un "LOC" senza numero e senza una parola tipica di
            # indirizzo non è un luogo — è quasi certamente un nome mal
            # etichettato, da trattare come PERSONA (mai perso, mai un
            # "indirizzo" fittizio che confonde l'LLM sull'azione da fare)
            label = ent.label_
            if label == "LOC" and not any(c.isdigit() for c in val) \
                    and not any(w in _ADDRESS_KEYWORDS for w in words):
                label = "PER"
            raw_spans.append((ent.start_char, ent.end_char, label, val))

    # 9. Risoluzione overlap: priorità prima di tutto (CF/IBAN/... vincono
    # sempre su una entità spaCy che li racchiude per intero, es. "Codice
    # Fiscale RSSMRA..." non deve far perdere lo span esatto del CF), poi
    # start per l'ordine tra span di pari priorità.
    raw_spans.sort(key=lambda x: (_PRIORITY.get(x[2], 99), x[0]))
    accepted: list[tuple[int, int, str, str]] = []
    covered: list[tuple[int, int]] = []

    for span in raw_spans:
        s, e, t, v = span
        if any(not (e <= cs or s >= ce) for cs, ce in covered):
            continue  # overlap con span già accettato
        accepted.append(span)
        covered.append((s, e))

    # 10. Assegna placeholder coerenti (stessa entità → stesso segnaposto)
    counters: dict[str, int] = {}
    val_to_ph: dict[tuple[str, str], str] = {}
    entities: list[dict] = []

    for s, e, t, v in sorted(accepted, key=lambda x: x[0]):
        norm_key = (t, v.upper().replace(" ", ""))
        if norm_key not in val_to_ph:
            prefix = _PREFIX.get(t, t)
            n = counters.get(prefix, 0) + 1
            counters[prefix] = n
            ph = f"[{prefix}_{n}]"
            val_to_ph[norm_key] = ph
        else:
            ph = val_to_ph[norm_key]
        entities.append({"placeholder": ph, "type": t, "value": v,
                         "start": s, "end": e})

    # 11. Costruisci pseudo_text sostituendo da destra a sinistra
    chars = list(text)
    for ent in reversed(entities):
        chars[ent["start"]:ent["end"]] = list(ent["placeholder"])
    pseudo_text = "".join(chars)

    mapping = {e["placeholder"]: e["value"] for e in entities}
    return {"pseudo_text": pseudo_text, "mapping": mapping, "entities": entities}


# ── smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")

    SAMPLE = (
        "Si comunica che il sig. Gennaro Esposito, nato a Napoli il 12/03/1971, "
        "C.F. SPSGNR71C12F839D, residente in Via Roma 48, ha presentato istanza. "
        "L'Avv. Carla Russo (C.F. RSSCRL80S45F839Z) riceverà il pagamento "
        "sul conto IBAN IT37H0503439960000000457812. "
        "Contatto: avv.russo@legale.it  —  tel. 081 123 4567."
    )

    result = pseudonymize(SAMPLE)

    print("── Entità rilevate ─────────────────────────────────────────")
    for e in result["entities"]:
        print(f"  {e['placeholder']:20} {e['type']:15} {mask(e['value'])}")

    print("\n── Mapping (placeholder → valore reale) ────────────────────")
    for ph, val in result["mapping"].items():
        print(f"  {ph:20} → {val}")

    print("\n── Pseudo-text ─────────────────────────────────────────────")
    print(" ", result["pseudo_text"])

    # Verifica: nessun dato originale nel pseudo_text
    sensibili = ["SPSGNR71C12F839D", "RSSCRL80S45F839Z",
                 "IT37H0503439960000000457812", "12/03/1971",
                 "avv.russo@legale.it"]
    print("\n── Verifica: dati originali assenti nel pseudo_text ────────")
    tutti_ok = True
    for dato in sensibili:
        if dato in result["pseudo_text"]:
            print(f"  ✗ TROVATO in pseudo_text: {dato}")
            tutti_ok = False
        else:
            print(f"  ✓ rimosso: {mask(dato)}")

    # Test su PDF reale
    print("\n── Test su PDF reale (01_determina_spese_legali...) ────────")
    import pymupdf
    doc = pymupdf.open("data/01_determina_spese_legali_salute_iban.pdf")
    testo = "\n".join(p.get_text() for p in doc)
    doc.close()
    res2 = pseudonymize(testo)
    cf_count    = sum(1 for e in res2["entities"] if e["type"] == "CF")
    iban_count  = sum(1 for e in res2["entities"] if e["type"] == "IBAN")
    per_count   = sum(1 for e in res2["entities"] if e["type"] == "PER")
    print(f"  CF trovati:    {cf_count}")
    print(f"  IBAN trovati:  {iban_count}")
    print(f"  PERSONA trovati: {per_count}")
    print(f"  Totale entità: {len(res2['entities'])}")
    spacy_status = "✓ attivo" if _NLP else "✗ non disponibile (solo regex)"
    print(f"  spaCy:         {spacy_status}")
    stdnum_status = "✓ attivo" if _HAS_STDNUM else "✗ non disponibile (no validation)"
    print(f"  stdnum:        {stdnum_status}")

    if tutti_ok:
        print("\n✓ Tutti i controlli passati")
    else:
        print("\n✗ Alcuni controlli falliti")
        sys.exit(1)
