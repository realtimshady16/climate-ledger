"""Turn a pinned spreadsheet into deterministic CSVs at freeze time.

The spreadsheet dependency lives here, on the network side. `verify` reads only
the derived CSVs, so recomputation stays hermetic and dependency-free — and a
parser bug is confined to a stage that can be re-run, rather than sitting inside
the check itself.
"""

from __future__ import annotations

import csv
from pathlib import Path


def xlsx_to_csv(workbook: Path, out_dir: Path, sheets: list[str]) -> list[Path]:
    from openpyxl import load_workbook  # lazy: only `make freeze` needs it

    book = load_workbook(workbook, data_only=True, read_only=True)
    missing = [name for name in sheets if name not in book.sheetnames]
    if missing:
        raise ValueError(f"sheets not in workbook: {missing}; have {book.sheetnames}")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name in sheets:
        path = out_dir / (name.replace(" ", "_").replace("/", "-") + ".csv")
        with path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            for row in book[name].iter_rows(values_only=True):
                writer.writerow(["" if cell is None else cell for cell in row])
        written.append(path)
    return written
