"""Coal's share of South African electricity, from Ember's yearly generation data.

Ember is CC BY 4.0 and machine-readable, which is why this claim is Tier A: the
number can be recomputed rather than transcribed. The CSIR report gives the same
story for utility-scale generation; the README carries the comparison.
"""

import csv
import json
import os
from pathlib import Path

AREA = "South Africa"
YEAR = 2025

snapshot = Path(os.environ["LEDGER_SNAPSHOT"])
raw = next((snapshot / "raw").glob("*.csv"))


def share(year: int) -> tuple[float, float, float] | None:
    rows = [
        row
        for row in csv.DictReader(raw.open())
        if row["Area"] == AREA and int(row["Year"]) == year
    ]
    if not rows:
        return None
    by_source = {row["Electricity source"]: row for row in rows}
    try:
        coal = float(by_source["Coal"]["Generation (TWh)"])
        total = float(by_source["Total generation"]["Generation (TWh)"])
    except (KeyError, ValueError):
        return None
    return coal, total, coal / total * 100


current = share(YEAR)
if current is None:
    raise SystemExit(f"no {AREA} row for {YEAR} in the pinned Ember file")
coal, total, value = current

series = []
for year in range(2000, YEAR + 1):
    row = share(year)
    if row:
        series.append(
            {
                "year": year,
                "coal_twh": round(row[0], 3),
                "total_twh": round(row[1], 3),
                "coal_share_pct": round(row[2], 3),
            }
        )

print(
    json.dumps(
        {
            "value": round(value, 3),
            "unit": "%",
            "detail": (
                f"{AREA} {YEAR}: coal {coal:.3f} of {total:.3f} TWh "
                f"= {value:.2f}%"
            ),
            "series": series,
        }
    )
)
