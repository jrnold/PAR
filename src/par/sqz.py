"""Decode the diskette's `.WQ!` spreadsheets to CSV with the `sqz` command."""

import shutil
import subprocess
from pathlib import Path

from par.tables import RAW_DIR, SHEET_DIR


def decode_sheets(raw_dir: Path = RAW_DIR, out_dir: Path = SHEET_DIR) -> None:
    """Write one CSV per `.WQ!` file, failing if `sqz` is missing or can't read a file."""
    sqz = shutil.which("sqz")
    if sqz is None:
        raise RuntimeError("sqz not found. Install it with: cargo install quattro-sqz --locked")
    sheets = sorted(raw_dir.glob("*.WQ!"))
    if not sheets:
        raise FileNotFoundError(f"no .WQ! files in {raw_dir}")
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    for sheet in sheets:
        out = out_dir / f"{sheet.name.removesuffix('.WQ!')}.csv"
        subprocess.run([sqz, "decode", str(sheet), str(out)], check=True)  # noqa: S603
