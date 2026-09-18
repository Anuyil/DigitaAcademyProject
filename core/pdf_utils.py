"""
core/pdf_utils.py — estrazione testo e redazione fisica del PDF.

Redazione:
  Solo entità flaggate dall'LLM come "rimuovere" o "minimizzare".
  Bande nere (fill nero, nessun testo sostitutivo).
  Solo valori abbastanza specifici da oscurare safely nel PDF.
"""

import logging
from pathlib import Path

import pymupdf

log = logging.getLogger(__name__)

# ── helpers ───────────────────────────────────────────────────────────────────

def _deplaceholder(text: str, mapping: dict) -> str:
    """Sostituisce i segnaposto con i valori reali per la ricerca nel PDF."""
    for ph, val in mapping.items():
        text = text.replace(ph, val)
    return text


def _redact_value(page: pymupdf.Page, value: str) -> int:
    """
    Cerca value nella pagina e aggiunge una banda nera su ogni occorrenza.
    Ritorna il numero di occorrenze trovate.
    """
    found = 0
    instances = page.search_for(value)
    for rect in instances:
        page.add_redact_annot(
            rect,
            text=None,          # nessun testo di sostituzione
            fill=(0, 0, 0),     # banda nera
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
    passaggi_critici: list | None = None,  # non usato (rimosso per evitare over-redaction)
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

    # Raccoglie i valori reali da oscurare (tutte le entità non "mantenere")
    valori_da_oscurare: list[str] = []

    for dec in decisioni:
        azione = dec.get("azione", "mantenere")
        if azione == "mantenere":
            continue
        ph    = dec.get("placeholder", "")
        value = mapping.get(ph, "")
        if not value:
            continue
        valori_da_oscurare.append(value)

    if not valori_da_oscurare:
        log.info(f"Nessuna redazione necessaria per {Path(pdf_path).name}")
        return pdf_path

    doc = pymupdf.open(pdf_path)
    total = 0

    for page in doc:
        # Passata 1: valori singoli (entità flaggate dall'LLM)
        for value in valori_da_oscurare:
            n = _redact_value(page, value)
            if n:
                log.debug(f"  [{page.number}] oscurato '{value[:30]}' ({n}x)")
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

    # 3. Simula decisioni LLM: rimuovi CF e IBAN, tutto il resto mantenere
    decisioni_test = []
    for e in result["entities"]:
        if e["type"] in ("CF", "IBAN"):
            azione = "rimuovere"
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
