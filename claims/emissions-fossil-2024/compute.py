"""2024 fossil CO2, recomputed from the pinned Global Carbon Budget workbook.

The workbook's column is labelled "fossil emissions excluding carbonation", but
the paper's headline figure is "including the cement carbonation sink". The two
columns reconcile only when the sink is netted out, which is why the subtraction
below is explicit rather than assumed.
"""

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

gross = float(row["fossil emissions excluding carbonation"])
carbonation = float(row["cement carbonation sink"])
net_gtc = gross - carbonation
value = net_gtc * GTC_TO_GTCO2

series = [
    {
        "year": int(float(r["Year"])),
        "fossil_gtco2": round(
            (float(r["fossil emissions excluding carbonation"])
             - float(r["cement carbonation sink"])) * GTC_TO_GTCO2,
            3,
        ),
    }
    for r in rows
    if r["Year"] and r["fossil emissions excluding carbonation"]
]

print(
    json.dumps(
        {
            "value": round(value, 3),
            "unit": "GtCO2",
            "detail": (
                f"{YEAR}: gross {gross:.4f} GtC, cement carbonation "
                f"{carbonation:.4f} GtC, net {net_gtc:.4f} GtC x 3.664 = "
                f"{value:.2f} GtCO2"
            ),
            "series": series,
        }
    )
)
