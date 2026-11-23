# Upstream sources and their terms

This project recomputes numbers from upstream data. The upstream producers keep
their rights; this file records what we may redistribute and what we may only
cite.

**Rule:** if a licence forbids redistribution, the repo ships the script and the
citation, not the bytes. A Tier B entry always cites rather than copies.

| Source | Used for | Status | Licence |
|---|---|---|---|
| NASA GISTEMP v4 | warming series | *stage 2* | Open (NASA), to be confirmed |
| Global Carbon Budget (Global Carbon Project) | emissions, remaining carbon budget | *stage 3* | To be confirmed before redistribution |
| UNEP Emissions Gap Report 2026 | policy projection (Tier B) | *stage 4* | Likely CC BY-NC-SA IGO — cite only, do not redistribute tables |
| UNEP Adaptation Gap Report | adaptation finance (Tier B) | *stage 4* | Likely CC BY-NC-SA IGO — cite only |
| Eskom Data Portal / CSIR Energy Statistics | SA coal share | *stage 6* | To be confirmed |
| Fixture (`fixtures/smoke.csv`) | pipeline smoke test | in repo | CC0 — generated for this repo |

Attribution for each pinned snapshot is also recorded machine-readably in
`data/<claim>/<snapshot>/provenance.json`.
