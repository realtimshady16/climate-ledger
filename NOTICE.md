# Upstream sources and their terms

This project recomputes numbers from upstream data. The upstream producers keep
their rights; this file records what we may redistribute and what we may only
cite.

**Rule:** if a licence forbids redistribution, the repo ships the script and the
citation, not the bytes. A Tier B entry always cites rather than copies.

| Source | Used for | Status | Licence |
|---|---|---|---|
| NASA GISTEMP v4 | warming series | in repo (`data/gistemp/`) | NASA open data; credit "NASA GISS/GISTEMP" (FAQ) |
| Global Carbon Budget 2025 workbook (ICOS, DOI 10.18160/GCP-2025) | emissions, carbon budget series | in repo (`data/gcb-workbook/`) | CC BY 4.0; cite Friedlingstein et al. 2025 |
| Global Carbon Budget 2025 paper (ESSD 18, 3211–3288) | remaining carbon budget (Tier B) | in repo (`data/gcb-paper/`) | CC BY 4.0 |
| UNEP Emissions Gap Report 2026 (*The point of return*) | policy projection (Tier B) | in repo (`data/unep-egr-2026/`) | UNEP: reproduction permitted for educational and non-profit use, in whole or in part |
| UNEP Adaptation Gap Report 2025 (*Running on Empty*) | adaptation finance (Tier B) | in repo (`data/unep-agr-2025/`) | UNEP: reproduction permitted for educational and non-profit use, in whole or in part |
| Eskom Data Portal / CSIR Energy Statistics | SA coal share | *stage 6* | To be confirmed |
| Fixture (`fixtures/smoke.csv`) | pipeline smoke test | in repo | CC0 — generated for this repo |

Attribution for each pinned snapshot is also recorded machine-readably in
`data/<claim>/<snapshot>/provenance.json`.
