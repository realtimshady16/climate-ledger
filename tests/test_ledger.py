"""Hermetic tests: build a throwaway tree and run the real freeze/verify code.

No network, no shared state, no reliance on the repo's own data/ or out/.
"""

from pathlib import Path

import pytest

from ledger import cli, provenance

COMPUTE = '''\
import csv, json, os
from pathlib import Path
raw = next((Path(os.environ["LEDGER_SNAPSHOT"]) / "raw").glob("*.csv"))
total = sum(float(r["v"]) for r in csv.DictReader(raw.open()))
print(json.dumps({"value": total, "unit": "count"}))
'''

CLAIMS = '''\
[[claims]]
id = "sum"
tier = "A"
question = "smoke"
unit = "count"
published = {published}
tolerance = 0.001

[claims.source]
path = "fixtures/x.csv"
'''


def build(tmp_path: Path, published: float = 3.0) -> Path:
    (tmp_path / "fixtures").mkdir()
    (tmp_path / "fixtures" / "x.csv").write_text("v\n1\n2\n")
    claim = tmp_path / "claims" / "sum"
    claim.mkdir(parents=True)
    (claim / "compute.py").write_text(COMPUTE)
    (tmp_path / "claims.toml").write_text(CLAIMS.format(published=published))
    return tmp_path


def test_sha256_is_stable():
    assert provenance.sha256_bytes(b"abc") == provenance.sha256_bytes(b"abc")
    assert provenance.sha256_bytes(b"abc") != provenance.sha256_bytes(b"abd")


def test_roundtrip_confirms(tmp_path):
    root = build(tmp_path)
    assert cli.freeze(root) == 0
    assert cli.verify(root) == 0

    import json

    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["summary"]["confirmed"] == 1
    assert payload["claims"][0]["value"] == 3.0
    assert (root / "REPORT.md").exists()


def test_drift_is_nonzero(tmp_path):
    root = build(tmp_path, published=4.0)
    assert cli.freeze(root) == 0
    assert cli.verify(root) == 1

    import json

    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["claims"][0]["verdict"] == "drifted"
    assert payload["claims"][0]["delta"] == -1.0


def test_missing_snapshot_is_nonzero(tmp_path):
    root = build(tmp_path)
    assert cli.verify(root) == 1

    import json

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

    import json

    payload = json.loads((root / "out" / "ledger.json").read_text())
    assert payload["claims"][0]["verdict"] == "error"


@pytest.mark.parametrize("command", ["freeze", "verify", "report"])
def test_cli_accepts_commands(tmp_path, command):
    root = build(tmp_path)
    cli.freeze(root)
    assert cli.main([command], root=root) == 0
