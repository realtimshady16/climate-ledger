"""2024 in GISTEMP, converted to the 1850-1900 baseline used by the headlines."""

import json
import os
from pathlib import Path

import tomllib

from ledger.warming import baseline_offset, parse_annual, to_preindustrial, warmest

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
year, value = warmest(annual)
converted = to_preindustrial(annual[2024], offset)

series = [
    {
        "year": y,
        "anomaly_1951_1980": annual[y],
        "anomaly_1850_1900": round(to_preindustrial(annual[y], offset), 4),
    }
    for y in sorted(annual)
]

print(
    json.dumps(
        {
            "value": round(converted, 4),
            "unit": "degC",
            "detail": (
                f"2024 = {annual[2024]:+.2f} vs 1951-1980; "
                f"offset = {offset:.4f} degC (1880-1899 mean + "
                f"{constants['sibling_offset_c']} degC); "
                f"warmest year = {year} ({value:+.2f} vs 1951-1980)"
            ),
            "series": series,
        }
    )
)
