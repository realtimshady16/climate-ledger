# climate-ledger

A public, one-off verification of the climate numbers everyone cites.

Each entry answers one question — *claim → source → method → recomputed value →
verdict → date* — from raw, pinned source bytes rather than from a web page's
summary.

**Status:** stage 1 (scaffold). One smoke claim; real claims land in stages 2–6.
See `plans/` in the origin workspace.

## The two commands that matter

```bash
make freeze    # fetch each source once, pin bytes + sha256 + provenance
make verify    # recompute offline from the pinned bytes; non-zero on drift
```

`freeze` and `verify` are deliberately separate:

- `freeze` touches the network. It never overwrites — each run creates a new
  timestamped snapshot under `data/<claim>/<snapshot>/`.
- `verify` never touches the network. It recomputes from the frozen bytes and
  exits non-zero if a value has moved outside its stated tolerance.

That split is what makes a one-off artefact safe: the result is reproducible
forever, and a later refresh is just a new freeze plus a diff against the old
snapshot.

## Layout

```
claims.toml              claim registry: id, tier, question, source, tolerance
claims/<id>/README.md    public entry: claim, verdict, receipts
claims/<id>/compute.py   tier A only: reads LEDGER_SNAPSHOT, prints JSON
data/<id>/<snapshot>/    pinned raw bytes + provenance.json + SHA256SUMS
data/<id>/LATEST         pointer to the snapshot verify uses
out/ledger.json          machine-readable result of the last verify
REPORT.md                human-readable report, generated
```

## Tiers

- **A — computed.** The source is machine-readable; `compute.py` derives the
  value and the drift test compares it with the published headline.
- **B — transcribed.** The number exists only in a document. The README carries
  the quoted passage, the page, and who read it. No parser pretends otherwise.

Tier B never redistributes restricted documents; it cites them.

## Quick start

```bash
python3 -m pytest -q     # hermetic tests, no network
make freeze              # creates data/smoke/...
make verify              # writes out/ledger.json, regenerates REPORT.md
```

Requires Python ≥ 3.11 and nothing else — no third-party runtime dependencies.

## Licence

Code MIT (`LICENSE`). Prose and derived data CC BY 4.0 (`LICENSE-CONTENT`).
Upstream sources and their terms: `NOTICE.md`.
