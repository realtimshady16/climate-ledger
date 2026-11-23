"""Stage-1 smoke claim: sum the fixture column, print the ledger record.

Any compute.py receives the frozen snapshot directory in LEDGER_SNAPSHOT and
prints one JSON object on stdout: {"value": <float>, "unit": <str>,
"detail": <str>, "series": [{"x": ..., "y": ...}, ...] optional}.
"""

import csv
import json
import os
from pathlib import Path

snapshot = Path(os.environ["LEDGER_SNAPSHOT"])
raw = next((snapshot / "raw").glob("*.csv"))
rows = list(csv.DictReader(raw.open()))
total = sum(float(row["value"]) for row in rows)

print(
    json.dumps(
        {
            "value": total,
            "unit": "count",
            "detail": f"sum of {len(rows)} rows in {raw.name}",
        }
    )
)
