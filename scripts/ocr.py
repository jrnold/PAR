"""Stage `ocr`: send the reports to LlamaParse. Frozen, because it costs money."""

from par.ocr import run_ocr

if __name__ == "__main__":
    run_ocr()
