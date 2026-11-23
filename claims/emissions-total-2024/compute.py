"""2024 total anthropogenic CO2: fossil plus land-use change, from the same sheet."""

import csv
import json
import os
from pathlib import Path

YEAR = 2024
GTC_TO_GTCO2 = 3.664

snapshot = Path(os.environ["LEDGER_SNAPSHOT"])
derived = next((snapshot / "derived").glob("*.csv"))

lines = derived.read_text().splitlines()
start = next(i for i, line in enumerate(lines) if line.startswith("Year,"))
rows = list(csv.DictReader(lines[start:]))
row = next(r for r in rows if int(float(r["Year"])) == YEAR)

fossil = (
    float(row["fossil emissions excluding carbonation"])
    - float(row["cement carbonation sink"])
)
land_use = float(row["land-use change emissions"])
value = (fossil + land_use) * GTC_TO_GTCO2

print(
    json.dumps(
        {
            "value": round(value, 3),
            "unit": "GtCO2",
            "detail": (
                f"{YEAR}: fossil {fossil:.4f} + land-use {land_use:.4f} "
                f"= {fossil + land_use:.4f} GtC x 3.664 = {value:.2f} GtCO2"
            ),
        }
    )
)
