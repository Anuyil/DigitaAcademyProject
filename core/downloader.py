import logging
from pathlib import Path

import requests

log = logging.getLogger(__name__)


def scarica_atto(url_pdf: str, dest_dir: str) -> str | None:
    """
    Scarica il PDF da url_pdf nella directory dest_dir.
    Ritorna il path locale del file salvato, None in caso di errore.
    Non lancia eccezioni.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    fname = url_pdf.rstrip("/").rsplit("/", 1)[-1]
    dest  = dest_dir / fname

    try:
        resp = requests.get(url_pdf, timeout=30)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        log.info(f"Download OK: {fname} ({dest.stat().st_size} byte)")
        return str(dest)
    except requests.RequestException as e:
        log.error(f"Download fallito [{url_pdf}]: {e}")
        return None


# ── smoke test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # Test 1: URL valido (deve girare il sito finto su :8001)
    with tempfile.TemporaryDirectory() as tmp:
        url = "http://localhost:8001/albo_fake/001_graduatoria_concorso_01.pdf"
        path = scarica_atto(url, tmp)
        if path:
            size = Path(path).stat().st_size
            print(f"  ✓ Download riuscito: {Path(path).name} ({size} byte)")
        else:
            print("  ✗ Download fallito (il sito finto è avviato su :8001?)")

    # Test 2: URL inesistente → None, nessun crash
    with tempfile.TemporaryDirectory() as tmp:
        path = scarica_atto("http://localhost:8001/albo_fake/INESISTENTE.pdf", tmp)
        if path is None:
            print("  ✓ URL inesistente → None (nessun crash)")
        else:
            print("  ✗ Atteso None, ricevuto path")

    # Test 3: Host irraggiungibile → None, nessun crash
    with tempfile.TemporaryDirectory() as tmp:
        path = scarica_atto("http://localhost:19999/fake.pdf", tmp)
        if path is None:
            print("  ✓ Host irraggiungibile → None (nessun crash)")
        else:
            print("  ✗ Atteso None, ricevuto path")
