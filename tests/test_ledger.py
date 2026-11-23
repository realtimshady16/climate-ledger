"""Hermetic tests: build a throwaway tree and run the real freeze/verify code.

No network and no shared state. One optional test reads the repo's own frozen
GISTEMP snapshot when it exists, so the real data is exercised after `make freeze`.
"""

import csv
import json
from pathlib import Path

import pytest

from ledger import cli, provenance, warming

COMPUTE = '''\
import csv, json, os
from pathlib import Path
raw = next((Path(os.environ["LEDGER_SNAPSHOT"]) / "raw").glob("*.csv"))
total = sum(float(r["v"]) for r in csv.DictReader(raw.open()))
print(json.dumps({"value": total, "unit": "count"}))
'''

DATASETS = '''\
[[datasets]]
id = "sum"
version = "fixture-1"

[datasets.source]
path = "fixtures/x.csv"
'''

CLAIMS = '''\
[[claims]]
id = "sum"
dataset = "sum"
tier = "A"
question = "smoke"
unit = "count"
published = {published}
tolerance = 0.001
'''

ROOT = Path(__file__).resolve().parents[1]


def build(tmp_path: Path, published: float = 3.0) -> Path:
    (tmp_path / "fixtures").mkdir()
    (tmp_path / "fixtures" / "x.csv").write_text("v\n1\n2\n")
    claim = tmp_path / "claims" / "sum"
    claim.mkdir(parents=True)
    (claim / "compute.py").write_text(COMPUTE)
    (tmp_path / "claims.toml").write_text(
        DATASETS + "\n" + CLAIMS.format(published=published)
    )
    return tmp_path


def gistemp_text(annual: dict[int, float]) -> str:
    header = "Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D"
    lines = ["Land-Ocean: Global Means", header]
    for year, value in annual.items():
        lines.append(f"{year}," + ",".join(["***"] * 12) + f",{value}")
    return "\n".join(lines) + "\n"


# --- the pipeline -----------------------------------------------------------


def test_sha256_is_stable():
    assert provenance.sha256_bytes(b"abc") == provenance.sha256_bytes(b"abc")
    assert provenance.sha256_bytes(b"abc") != provenance.sha256_bytes(b"abd")


def test_roundtrip_confirms(tmp_path):
    root = build(tmp_path)
    assert cli.freeze(root) == 0
    assert cli.verify(root) == 0

    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["summary"]["confirmed"] == 1
    assert payload["claims"][0]["value"] == 3.0
    assert (root / "REPORT.md").exists()


def test_drift_is_nonzero(tmp_path):
    root = build(tmp_path, published=4.0)
    assert cli.freeze(root) == 0
    assert cli.verify(root) == 1

    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["claims"][0]["verdict"] == "drifted"
    assert payload["claims"][0]["delta"] == -1.0


def test_missing_snapshot_is_nonzero(tmp_path):
    root = build(tmp_path)
    assert cli.verify(root) == 1

    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["claims"][0]["verdict"] == "missing-snapshot"


def test_snapshot_is_immutable(tmp_path):
    root = build(tmp_path)
    assert cli.freeze(root) == 0
    first = provenance.latest_snapshot(root, "sum")
    assert cli.freeze(root) == 0
    second = provenance.latest_snapshot(root, "sum")
    assert first != second
    assert first.is_dir(), "freezing again must not delete or rewrite the old snapshot"


def test_compute_failure_is_reported(tmp_path):
    root = build(tmp_path)
    (root / "claims" / "sum" / "compute.py").write_text("raise SystemExit(2)\n")
    assert cli.freeze(root) == 0
    assert cli.verify(root) == 1

    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["claims"][0]["verdict"] == "error"


def test_two_claims_share_one_snapshot(tmp_path):
    """Both claims must read the same frozen vintage, not two downloads."""
    root = build(tmp_path)
    (root / "claims" / "other").mkdir()
    (root / "claims" / "other" / "compute.py").write_text(COMPUTE)
    text = (root / "claims.toml").read_text()
    text += "\n" + CLAIMS.format(published=3.0).replace('id = "sum"', 'id = "other"')
    (root / "claims.toml").write_text(text)

    assert cli.freeze(root) == 0
    assert len(list((root / "data" / "sum").glob("*/provenance.json"))) == 1
    assert cli.verify(root) == 0


# --- warming arithmetic -----------------------------------------------------


def test_parse_annual_drops_incomplete_years():
    text = gistemp_text({2023: 1.17, 2024: 1.28})
    text += "2026," + ",".join(["***"] * 12) + ",***\n"
    annual = warming.parse_annual(text)
    assert annual == {2023: 1.17, 2024: 1.28}


def test_baseline_offset_direction():
    annual = {year: -0.2 for year in range(1880, 1900)}
    offset = warming.baseline_offset(annual, 1880, 1899, 0.038)
    assert offset == pytest.approx(0.238)


def test_offset_is_applied_exactly_once():
    """The regression that matters: a double conversion adds ~0.52 degC."""
    raw, offset = 1.28, 0.2625
    converted = warming.to_preindustrial(raw, offset)
    assert converted == pytest.approx(1.5425)
    assert converted != pytest.approx(raw + 2 * offset)


def test_warmest_year():
    assert warming.warmest({2023: 1.17, 2024: 1.28, 2016: 1.01}) == (2024, 1.28)


def test_mean_between():
    assert warming.mean_between({2019: 1.0, 2020: 2.0}, 2019, 2020) == 1.5


@pytest.mark.skipif(
    not any((ROOT / "data" / "gistemp").glob("*/raw/*.csv")),
    reason="no frozen GISTEMP snapshot in this checkout",
)
def test_real_gistemp_2024_is_warmest():
    raw = next((ROOT / "data" / "gistemp").glob("*/raw/*.csv"))
    annual = warming.parse_annual(raw.read_text())
    assert warming.warmest(annual)[0] == 2024
    offset = warming.baseline_offset(annual, 1880, 1899, 0.038)
    assert 0.24 < offset < 0.28


# --- tiers, extraction ------------------------------------------------------


def test_tier_b_requires_a_snapshot(tmp_path):
    (tmp_path / "claims" / "b").mkdir(parents=True)
    (tmp_path / "claims" / "b" / "README.md").write_text(
        "quoted: q\npage: 1\nchecked_by: me\n"
    )
    (tmp_path / "claims.toml").write_text(
        '[[claims]]\nid = "b"\ndataset = "missing"\ntier = "B"\n'
        'question = "q"\npublished = 1\n'
    )
    assert cli.verify(tmp_path) == 1
    payload = json.loads((tmp_path / "out" / "ledger.json").read_text())
    assert payload["claims"][0]["verdict"] == "missing-snapshot"


def test_tier_b_reports_transcribed(tmp_path):
    root = build(tmp_path)
    (root / "claims" / "b").mkdir()
    (root / "claims" / "b" / "README.md").write_text(
        "quoted: q\npage: 1\nchecked_by: me\n"
    )
    text = (root / "claims.toml").read_text()
    text += '\n[[claims]]\nid = "b"\ndataset = "sum"\ntier = "B"\nquestion = "q"\npublished = 1\n'
    (root / "claims.toml").write_text(text)

    assert cli.freeze(root) == 0
    assert cli.verify(root) == 0
    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["claims"][1]["verdict"] == "transcribed"


def test_tier_b_missing_fields_is_an_error(tmp_path):
    root = build(tmp_path)
    (root / "claims" / "b").mkdir()
    (root / "claims" / "b" / "README.md").write_text("quoted: q\n")
    text = (root / "claims.toml").read_text()
    text += '\n[[claims]]\nid = "b"\ndataset = "sum"\ntier = "B"\nquestion = "q"\npublished = 1\n'
    (root / "claims.toml").write_text(text)

    assert cli.freeze(root) == 0
    assert cli.verify(root) == 1


def test_xlsx_extract_is_deterministic(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    from ledger import extract

    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Sheet One"
    sheet.append(["Year", "value"])
    sheet.append([2024, 1.5])
    path = tmp_path / "book.xlsx"
    book.save(path)

    first = extract.xlsx_to_csv(path, tmp_path / "a", ["Sheet One"])
    second = extract.xlsx_to_csv(path, tmp_path / "b", ["Sheet One"])
    assert first[0].name == "Sheet_One.csv"
    assert first[0].read_bytes() == second[0].read_bytes()
    assert "2024,1.5" in first[0].read_text()


def test_xlsx_extract_rejects_missing_sheet(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    from ledger import extract

    book = openpyxl.Workbook()
    path = tmp_path / "book.xlsx"
    book.save(path)
    with pytest.raises(ValueError):
        extract.xlsx_to_csv(path, tmp_path / "a", ["Nope"])


def test_tier_b_second_read_confirms(tmp_path):
    root = build(tmp_path)
    (root / "claims" / "b").mkdir()
    (root / "claims" / "b" / "README.md").write_text(
        "quoted: q\npage: 1\nsecond_read: yes\nchecked_by: me\n"
    )
    text = (root / "claims.toml").read_text()
    text += '\n[[claims]]\nid = "b"\ndataset = "sum"\ntier = "B"\nquestion = "q"\npublished = 1\n'
    (root / "claims.toml").write_text(text)

    assert cli.freeze(root) == 0
    assert cli.verify(root) == 0
    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["claims"][1]["verdict"] == "confirmed"


# --- diff -------------------------------------------------------------------


def _diff(tmp_path):
    assert cli.diff(tmp_path) == 0
    return json.loads((tmp_path / "out" / "diff.json").read_text())["datasets"][0]


def test_diff_single_snapshot_has_nothing_to_compare(tmp_path):
    root = build(tmp_path)
    assert cli.freeze(root) == 0
    entry = _diff(root)
    assert "note" in entry
    assert entry["claims"] == []


def test_diff_identical_snapshot_is_unchanged(tmp_path):
    root = build(tmp_path)
    assert cli.freeze(root) == 0
    assert cli.freeze(root) == 0
    entry = _diff(root)
    assert entry["raw_changed"] is False
    claim = entry["claims"][0]
    assert claim["delta"] == 0.0
    assert claim["within_tolerance"] is True


def test_diff_detects_a_revision(tmp_path):
    root = build(tmp_path)
    assert cli.freeze(root) == 0
    (root / "fixtures" / "x.csv").write_text("v\n1\n3\n")
    assert cli.freeze(root) == 0
    entry = _diff(root)
    assert entry["raw_changed"] is True
    claim = entry["claims"][0]
    assert claim["previous"] == 3.0
    assert claim["current"] == 4.0
    assert claim["delta"] == 1.0
    assert claim["within_tolerance"] is False


def test_diff_reports_tier_b_without_recomputing(tmp_path):
    root = build(tmp_path)
    (root / "claims" / "b").mkdir()
    (root / "claims" / "b" / "README.md").write_text(
        "quoted: q\npage: 1\nchecked_by: me\n"
    )
    text = (root / "claims.toml").read_text()
    text += '\n[[claims]]\nid = "b"\ndataset = "sum"\ntier = "B"\nquestion = "q"\npublished = 1\n'
    (root / "claims.toml").write_text(text)
    assert cli.freeze(root) == 0
    assert cli.freeze(root) == 0
    entry = _diff(root)
    tier_b = next(row for row in entry["claims"] if row["id"] == "b")
    assert "previous" not in tier_b
    assert "note" in tier_b
