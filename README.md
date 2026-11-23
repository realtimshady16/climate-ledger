# climate-ledger

A public, one-off verification of the climate numbers everyone cites.

Each entry answers one question — *claim → source → method → recomputed value →
verdict → date* — from raw, pinned source bytes rather than from a web page's
summary.

Live: <https://realtimshady16.github.io/climate-ledger/>

**Status:** stage 5. Eight claims; all computed sources reproduce their published
headlines, and the Tier B entries are transcribed with page references. See
`plans/` in the origin workspace.

## Claims

| Claim | Tier | What it checks | Recomputed |
|---|---|---|---|
| `warming-year` | A | 2024 ≈ 1.55 °C above 1850–1900, warmest on record | 1.5425 |
| `warming-decade` | A | observed 2015–2024 mean | 1.2475 |
| `emissions-fossil-2024` | A | 2024 fossil CO₂ | 37.777 Gt |
| `emissions-total-2024` | A | 2024 fossil + land-use CO₂ | 42.362 Gt |
| `budget-1.5` | B | 170 GtCO₂ left ≈ 4 years | transcribed |
| `projection-policies` | B | 2.8 °C under current policies | transcribed |
| `finance-adaptation` | B | $26bn delivered vs $310bn/yr needed | transcribed |
| `smoke` | A | the pipeline itself | 10 |

## The two commands that matter

```bash
make freeze    # fetch each source once, pin bytes + sha256 + provenance
make verify    # recompute offline from the pinned bytes; non-zero on drift
```

`freeze` and `verify` are deliberately separate:

- `freeze` touches the network. It never overwrites — each run creates a new
  timestamped snapshot under `data/<dataset>/<snapshot>/`. Spreadsheets are also
  converted to derived CSVs here, so the spreadsheet dependency stays on this
  side of the line.
- `verify` never touches the network and needs only the standard library. It
  recomputes from the frozen bytes and exits non-zero if a value has moved
  outside its stated tolerance.

That split is what makes a one-off artefact safe: the result is reproducible
forever, and a later refresh is just a new freeze plus a diff against the old
snapshot.

## Layout

```
claims.toml              dataset + claim registries
constants.toml           named constants, each with a source
claims/<id>/README.md    public entry: claim, verdict, receipts
claims/<id>/compute.py   tier A only: reads LEDGER_SNAPSHOT, prints JSON
data/<dataset>/<snap>/   pinned raw bytes + provenance.json + SHA256SUMS
data/<dataset>/LATEST    pointer to the snapshot verify uses
out/ledger.json          machine-readable result of the last verify
REPORT.md                human-readable report, generated
```

## Tiers

- **A — computed.** The source is machine-readable; `compute.py` derives the
  value and the drift test compares it with the published headline.
- **B — transcribed.** The number exists only in a document. The README carries
  the quoted passage, the page, and who read it. No parser pretends otherwise.

Datasets are frozen, not claims: two claims reading the same source must never
end up on two different vintages of it.

Tier B never redistributes restricted documents; it cites them.

## Quick start

```bash
make freeze              # fetch every dataset; or: python -m ledger freeze <id> …
make verify              # stdlib only, offline; writes out/ledger.json + REPORT.md
make test                # hermetic, no network
```

Requires Python ≥ 3.11 and nothing else — no third-party runtime dependencies.

## Licence

Code MIT (`LICENSE`). Prose and derived data CC BY 4.0 (`LICENSE-CONTENT`).
Upstream sources and their terms: `NOTICE.md`.
