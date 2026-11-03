"""OCR the PAR reports with LlamaParse."""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from llama_cloud import LlamaCloud

PDFS = [Path("docs/sources/ADA279069.pdf"), Path("docs/sources/ADA294527.pdf")]
JSON_DIR = Path("data/interim/ocr")
MARKDOWN_DIR = Path("docs/ocr")

PROMPT = """\
This is a scanned, typewritten 1990s US Army Concepts Analysis Agency research report, with
tables of casualty data, data-file layouts, and bibliographic entries.
- Transcribe the text faithfully, keeping the original spelling, abbreviations and numbers.
  Do not modernize or correct.
- Reproduce tables as markdown tables, keeping every number exactly; use '-' for dashes.
- Write mathematics as LaTeX ($...$ inline, $$...$$ display).
- Keep identifiers such as AD-A183 255 and dataset names such as AHART-1993 exactly.
- Mark illegible text as [illegible] rather than guessing.
- Describe figures briefly as [figure: ...], transcribing titles, axis labels and legends.
- Keep printed page numbers and report numbers in headers and footers.
"""


def parse_pdf(client: LlamaCloud, pdf: Path, tier: str = "agentic") -> None:
    """OCR one PDF and write the raw API result as JSON."""
    result = client.parsing.parse(
        tier=tier,
        version="latest",
        upload_file=pdf,
        agentic_options={"custom_prompt": PROMPT},
        expand=["markdown"],
    )
    (JSON_DIR / f"{pdf.stem}.json").write_text(result.model_dump_json(indent=2))


def run_ocr() -> None:
    """OCR every report. Reads LLAMAINDEX_API_KEY from the environment."""
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    client = LlamaCloud(api_key=os.environ["LLAMAINDEX_API_KEY"])
    with ThreadPoolExecutor(len(PDFS)) as pool:
        for future in [pool.submit(parse_pdf, client, pdf) for pdf in PDFS]:
            future.result()


def write_markdown() -> None:
    """Write one markdown file per report, with a comment marking each page."""
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    for pdf in PDFS:
        result = json.loads((JSON_DIR / f"{pdf.stem}.json").read_text())
        pages = result["markdown"]["pages"]
        body = "\n\n".join(
            f"<!-- page {number} -->\n\n{page.get('markdown', '').strip()}"
            for number, page in enumerate(pages, 1)
        )
        (MARKDOWN_DIR / f"{pdf.stem}.md").write_text(body + "\n", encoding="utf-8")
