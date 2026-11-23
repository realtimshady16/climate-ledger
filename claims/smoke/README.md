# smoke — pipeline check

**Tier:** A · **Published:** 10 · **Unit:** count · **Tolerance:** 0.001

## Claim

The fixture `fixtures/smoke.csv` sums to 10.

## Why it exists

It is not a climate claim. It exercises the full path — freeze, pin with a
SHA-256, recompute offline, compare against a published value, report a delta —
so that stages 2–6 add sources rather than plumbing.

## Method

`claims/smoke/compute.py` reads the only CSV in the snapshot's `raw/` directory
and sums its `value` column.

## Verdict

`confirmed` when `make verify` recomputes 10.0 from the pinned bytes.

## Receipts

- Snapshot: `data/smoke/<snapshot>/`
- Provenance: `data/smoke/<snapshot>/provenance.json`
- Source: generated fixture, CC0
