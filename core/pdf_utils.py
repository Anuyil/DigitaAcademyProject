"""
core/pdf_utils.py — estrazione testo e redazione fisica del PDF.

Redazione:
  "rimuovere"   → testo sostituito con "OMISSIS" (rettangolo bianco + testo)
  "minimizzare" → nomi sostituiti con iniziali (es. "M.R.")
  "mantenere"   → nessuna modifica

Strategia di ricerca (due passate):
  1. Per ogni decisione "rimuovere"/"minimizzare": cerca il VALORE REALE
     nel PDF (page.search_for) e oscura ogni occorrenza.
  2. Per ogni passaggio_critico: ricostruisce il testo reale (sostituendo
     i segnaposto con i valori veri) e oscura la frase intera se trovata.
"""

import logging
from pathlib import Path

import pymupdf

log = logging.getLogger(__name__)

_FILL_WHITE = (1, 1, 1)
_FILL_BLACK = (0, 0, 0)


# ── helpers ───────────────────────────────────────────────────────────────────

def _initials(name: str) -> str:
    """Mario Rossi → M.R.  |  RSSMRA80A01F839X → R."""
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "***"
    return ".".join(p[0].upper() for p in parts) + "."


def _deplaceholder(text: str, mapping: dict) -> str:
    """Sostituisce i segnaposto con i valori reali per la ricerca nel PDF."""
    for ph, val in mapping.items():
        text = text.replace(ph, val)
    return text


def _redact_value(page: pymupdf.Page, value: str, replacement: str) -> int:
    """
    Cerca value nella pagina e aggiunge redaction annotation su ogni occorrenza.
    Ritorna il numero di occorrenze trovate.
    """
    found = 0
    instances = page.search_for(value)
    for rect in instances:
        page.add_redact_annot(
            rect,
            text=replacement,
            fontname="helv",
            fontsize=8,
            align=pymupdf.TEXT_ALIGN_CENTER,
            fill=_FILL_WHITE,
            text_color=_FILL_BLACK,
        )
        found += 1
    return found


# ── API pubblica ──────────────────────────────────────────────────────────────

def extract_text(pdf_path: str) -> str:
    """Estrae il testo grezzo da tutte le pagine del PDF."""
    doc = pymupdf.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def redact_pdf(
    pdf_path: str,
    output_path: str,
    mapping: dict,
    decisioni: list,
    passaggi_critici: list | None = None,
) -> str:
    """
    Applica le decisioni dell'LLM al PDF e salva il file redatto.

    Args:
        pdf_path:        path del PDF originale
        output_path:     path dove salvare il PDF redatto
        mapping:         {"[PERSONA_1]": "Mario Rossi", ...}  (da pseudonymize)
        decisioni:       [{"placeholder", "azione", ...}]     (da llm.analyze)
        passaggi_critici:[{"testo", ...}]                      (da llm.analyze, opzionale)

    Returns:
        output_path se almeno una redazione è applicata, pdf_path originale altrimenti.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Costruisce mappa placeholder → (valore_reale, replacement_text)
    redactions: list[tuple[str, str]] = []  # (valore_da_cercare, testo_sostituzione)

    for dec in decisioni:
        azione = dec.get("azione", "mantenere")
        if azione == "mantenere":
            continue
        ph    = dec.get("placeholder", "")
        value = mapping.get(ph, "")
        if not value:
            continue
        replacement = "OMISSIS" if azione == "rimuovere" else _initials(value)
        redactions.append((value, replacement))

    # Passaggi critici → cerca la frase intera ricostruita
    frase_redactions: list[str] = []
    for p in (passaggi_critici or []):
        testo_ph = p.get("testo", "")
        testo_reale = _deplaceholder(testo_ph, mapping).strip()
        if testo_reale:
            frase_redactions.append(testo_reale)

    if not redactions and not frase_redactions:
        log.info(f"Nessuna redazione necessaria per {Path(pdf_path).name}")
        return pdf_path

    doc = pymupdf.open(pdf_path)
    total = 0

    for page in doc:
        # Passata 1: valori singoli (entità)
        for value, replacement in redactions:
            n = _redact_value(page, value, replacement)
            if n:
                log.debug(f"  [{page.number}] '{value[:30]}' → '{replacement}' ({n}x)")
            total += n

        # Passata 2: frasi critiche intere (OMISSIS)
        for frase in frase_redactions:
            n = _redact_value(page, frase, "OMISSIS")
            if n:
                log.debug(f"  [{page.number}] frase critica trovata e oscurata ({n}x)")
            total += n

        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE)

    if total > 0:
        doc.save(output_path, garbage=4, deflate=True)
        log.info(f"PDF redatto: {total} occorrenze oscurate → {Path(output_path).name}")
    else:
        log.warning(f"Nessuna occorrenza trovata nel PDF — salvato senza modifiche")
        doc.save(output_path, garbage=4, deflate=True)

    doc.close()
    return output_path


# ── smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    PDF_IN  = "data/01_determina_spese_legali_salute_iban.pdf"
    PDF_OUT = "data/corrected/test_redatto.pdf"

    # 1. Estrai testo
    testo = extract_text(PDF_IN)
    print(f"✓ Testo estratto: {len(testo)} caratteri")
    print(f"  Anteprima: {testo[:120].strip()}...")

    # 2. Pseudonimizza
    from core.detectors import pseudonymize
    result = pseudonymize(testo)
    print(f"\n✓ Pseudonimizzazione: {len(result['entities'])} entità")
    for e in result["entities"][:6]:
        from core.detectors import mask
        print(f"  {e['placeholder']:20} {e['type']:15} {mask(e['value'])}")

    # 3. Simula decisioni LLM: rimuovi CF e IBAN, minimizza persone
    decisioni_test = []
    for e in result["entities"]:
        if e["type"] in ("CF", "IBAN", "DATA_NASCITA", "EMAIL", "TEL"):
            azione = "rimuovere"
        elif e["type"] == "PER":
            azione = "minimizzare"
        else:
            azione = "mantenere"
        decisioni_test.append({"placeholder": e["placeholder"], "azione": azione})

    # 4. Redigi il PDF
    out = redact_pdf(
        pdf_path         = PDF_IN,
        output_path      = PDF_OUT,
        mapping          = result["mapping"],
        decisioni        = decisioni_test,
        passaggi_critici = [],
    )
    print(f"\n✓ PDF redatto salvato: {out}")

    # 5. Verifica: i valori redatti non appaiono nel testo del PDF redatto
    testo_redatto = extract_text(out)
    print("\n✓ Verifica: valori sensibili assenti nel PDF redatto")
    tutti_ok = True
    for e in result["entities"]:
        if e["type"] in ("CF", "IBAN"):
            if e["value"] in testo_redatto:
                print(f"  ✗ TROVATO nel redatto: {mask(e['value'])}")
                tutti_ok = False
            else:
                print(f"  ✓ rimosso: {mask(e['value'])}")

    if tutti_ok:
        print(f"\n✓ Tutti i controlli passati — apri {PDF_OUT} per verificare visivamente")
    else:
        print("\n✗ Alcuni valori ancora presenti nel PDF")
        sys.exit(1)
