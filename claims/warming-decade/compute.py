"""The observed 2015-2024 decade mean, on the same 1850-1900 baseline."""

import json
import os
from pathlib import Path

import tomllib

from ledger.warming import baseline_offset, mean_between, parse_annual, to_preindustrial

root = Path(os.environ["LEDGER_ROOT"])
snapshot = Path(os.environ["LEDGER_SNAPSHOT"])

constants = tomllib.loads((root / "constants.toml").read_text())["warming"]
raw = next((snapshot / "raw").glob("*.csv"))
annual = parse_annual(raw.read_text())

offset = baseline_offset(
    annual,
    constants["preindustrial_start"],
    constants["preindustrial_end"],
    constants["sibling_offset_c"],
)
start, end = constants["decade_start"], constants["decade_end"]
observed = mean_between(annual, start, end)
converted = to_preindustrial(observed, offset)

print(
    json.dumps(
        {
            "value": round(converted, 4),
            "unit": "degC",
            "detail": (
                f"{start}-{end} mean = {observed:+.3f} vs 1951-1980; "
                f"offset = {offset:.4f} degC; "
                f"this is the OBSERVED decadal mean, not human-induced warming"
            ),
            "series": [
                {
                    "year": y,
                    "decadal_mean_1850_1900": round(
                        to_preindustrial(
                            mean_between(annual, max(min(annual), y - 9), y), offset
                        ),
                        4,
                    ),
                }
                for y in sorted(annual)
                if y - 9 >= min(annual)
            ],
        }
    )
)
