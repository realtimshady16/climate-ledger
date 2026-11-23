"""Command line: freeze | verify | report.

Paths are resolved from an explicit root so the tests can build a throwaway tree
and run the real code against it, with no network and no shared state.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from . import provenance

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load(root: Path, key: str) -> list[dict]:
    with (root / "claims.toml").open("rb") as handle:
        return tomllib.load(handle).get(key, [])


def load_datasets(root: Path) -> list[dict]:
    return _load(root, "datasets")


def load_claims(root: Path) -> list[dict]:
    return _load(root, "claims")


def run_compute(root: Path, claim: dict, snapshot: Path) -> dict:
    script = root / "claims" / claim["id"] / "compute.py"
    if not script.exists():
        raise RuntimeError(f"{claim['id']}: no compute.py")
    env = dict(
        os.environ,
        LEDGER_SNAPSHOT=str(snapshot),
        LEDGER_CLAIM_ID=claim["id"],
        LEDGER_ROOT=str(root),
        PYTHONPATH=os.pathsep.join(
            p for p in (str(root), os.environ.get("PYTHONPATH", "")) if p
        ),
    )
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        env=env,
        cwd=root,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{claim['id']}: compute.py failed\n{proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{claim['id']}: compute.py printed non-JSON: {exc}") from exc


def freeze(root: Path) -> int:
    count = 0
    for dataset in load_datasets(root):
        snapshot = provenance.freeze_dataset(root, dataset)
        prov = json.loads((snapshot / "provenance.json").read_text())
        print(
            f"froze {dataset['id']}: {snapshot.relative_to(root)}  "
            f"{prov['bytes']} bytes  sha256={prov['sha256'][:12]}…"
        )
        count += 1
    print(f"{count} dataset(s) frozen")
    return 0


def transcribed_row(root: Path, claim: dict) -> dict:
    readme = root / "claims" / claim["id"] / "README.md"
    if not readme.exists():
        return {"verdict": "error", "detail": "tier B entry has no README.md"}
    text = readme.read_text()
    missing = [key for key in ("quoted:", "page:", "checked_by:") if key not in text]
    if missing:
        return {"verdict": "error", "detail": f"README missing {missing}"}
    return {"verdict": "transcribed", "detail": "quoted passage present; no recompute"}


def verify(root: Path) -> int:
    rows: list[dict] = []
    for claim in load_claims(root):
        dataset = claim.get("dataset")
        snapshot = provenance.latest_snapshot(root, dataset) if dataset else None
        row: dict = {
            "id": claim["id"],
            "dataset": dataset,
            "tier": claim["tier"],
            "question": claim["question"],
            "unit": claim.get("unit"),
            "published": claim.get("published"),
            "tolerance": claim.get("tolerance"),
            "snapshot": snapshot.name if snapshot else None,
            "checked_at": now(),
        }

        if snapshot is None:
            row |= {"verdict": "missing-snapshot", "detail": "run `make freeze`"}
            rows.append(row)
            continue

        if claim["tier"] == "B":
            row |= transcribed_row(root, claim)
            rows.append(row)
            continue

        try:
            result = run_compute(root, claim, snapshot)
        except RuntimeError as exc:
            row |= {"verdict": "error", "detail": str(exc)}
            rows.append(row)
            continue

        value = float(result["value"])
        published = float(claim["published"])
        delta = value - published
        within = abs(delta) <= float(claim["tolerance"])
        row |= {
            "value": value,
            "delta": round(delta, 6),
            "detail": result.get("detail"),
            "verdict": "confirmed" if within else "drifted",
        }
        if result.get("series"):
            write_series(root, claim["id"], result["series"])
        rows.append(row)

    write_outputs(root, rows)
    return 0 if all(r["verdict"] in ("confirmed", "transcribed") for r in rows) else 1


def write_series(root: Path, claim_id: str, series: list[dict]) -> None:
    import csv

    out = root / "out"
    out.mkdir(exist_ok=True)
    with (out / f"{claim_id}.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(series[0].keys()))
        writer.writeheader()
        writer.writerows(series)


def write_outputs(root: Path, rows: list[dict]) -> None:
    out = root / "out"
    out.mkdir(exist_ok=True)
    payload = {
        "generated_at": now(),
        "tool": provenance.FETCHER,
        "claims": rows,
        "summary": {
            "total": len(rows),
            "confirmed": sum(r["verdict"] == "confirmed" for r in rows),
            "transcribed": sum(r["verdict"] == "transcribed" for r in rows),
            "drifted": sum(r["verdict"] == "drifted" for r in rows),
            "failed": sum(
                r["verdict"] not in ("confirmed", "transcribed") for r in rows
            ),
        },
    }
    (out / "ledger.json").write_text(json.dumps(payload, indent=2) + "\n")
    (root / "REPORT.md").write_text(render_report(payload))


def render_report(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Climate ledger — report",
        "",
        f"Generated {payload['generated_at']} by `{payload['tool']}`.",
        "",
        f"{summary['confirmed']} confirmed · {summary['transcribed']} transcribed · "
        f"{summary['drifted']} drifted · {summary['failed']} failed "
        f"of {summary['total']}.",
        "",
        "| Claim | Dataset | Tier | Published | Recomputed | Δ | Verdict | Checked |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in payload["claims"]:
        recomputed = "" if row.get("value") is None else f"{row['value']:g}"
        delta = "" if row.get("delta") is None else f"{row['delta']:+g}"
        lines.append(
            f"| `{row['id']}` | `{row.get('dataset') or '—'}` | {row['tier']} "
            f"| {row['published']} | {recomputed} | {delta} "
            f"| {row['verdict']} | {row['checked_at'][:10]} |"
        )
    lines += [
        "",
        "Recomputed values come from pinned raw bytes; see "
        "`data/<dataset>/<snapshot>/provenance.json`.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    root = root or PACKAGE_ROOT
    parser = argparse.ArgumentParser(prog="climate-ledger")
    parser.add_argument("command", choices=["freeze", "verify", "report"])
    args = parser.parse_args(argv)

    if args.command == "freeze":
        return freeze(root)
    if args.command == "verify":
        code = verify(root)
        payload = json.loads((root / "out" / "ledger.json").read_text())
        print(json.dumps(payload["summary"]))
        return code
    if not (root / "out" / "ledger.json").exists():
        verify(root)
    print((root / "REPORT.md").read_text())
    return 0
