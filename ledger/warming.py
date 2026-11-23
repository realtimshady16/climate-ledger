"""Temperature-series arithmetic, kept out of the scripts so it can be tested.

The baseline conversion is the dangerous part: apply it twice and every number
is ~0.26 degC too high, which is also roughly the size of the signal the project
is checking. `baseline_offset` is therefore defined once and tested.
"""

from __future__ import annotations

import csv


def parse_annual(csv_text: str) -> dict[int, float]:
    """Parse GISTEMP's GLB.Ts+dSST.csv into {year: annual mean anomaly}.

    The file begins with a title line, then a header row. Annual means are in
    the `J-D` column; incomplete years carry `***` and are dropped.
    """
    lines = csv_text.splitlines()
    if len(lines) < 2:
        raise ValueError("expected a title line and a header row")
    out: dict[int, float] = {}
    for row in csv.DictReader(lines[1:]):
        year, value = row.get("Year"), row.get("J-D")
        if not year or value is None or value.strip() in ("***", ""):
            continue
        out[int(year)] = float(value)
    return out


def baseline_offset(
    annual: dict[int, float],
    start: int = 1880,
    end: int = 1899,
    sibling_offset: float = 0.038,
) -> float:
    """Offset that converts a 1951-1980 anomaly to a 1850-1900 anomaly.

    Anomalies are relative to 1951-1980, so the window's mean is how much
    colder it was; subtracting it re-bases the series. The sibling offset then
    carries the window to 1850-1900.
    """
    window = [annual[year] for year in range(start, end + 1)]
    if not window:
        raise ValueError(f"no data in {start}-{end}")
    return -sum(window) / len(window) + sibling_offset


def to_preindustrial(anomaly: float, offset: float) -> float:
    """Apply the baseline conversion exactly once."""
    return anomaly + offset


def warmest(annual: dict[int, float]) -> tuple[int, float]:
    year = max(annual, key=lambda y: annual[y])
    return year, annual[year]


def mean_between(annual: dict[int, float], start: int, end: int) -> float:
    window = [annual[year] for year in range(start, end + 1)]
    if not window:
        raise ValueError(f"no data in {start}-{end}")
    return sum(window) / len(window)
