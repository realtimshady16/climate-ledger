# sa-coal-share — coal's share of South African electricity, 2025

**Tier:** A · **Dataset:** `ember-yearly` · **Published:** 81.3 % · **Tolerance:** 0.5

## Claim

Coal supplied **81.3 %** of South Africa's electricity in 2025:
**197.5 TWh of 242.8 TWh**.

## Method

From Ember's yearly generation dataset, filter `Area == "South Africa"` and the
year, then `coal TWh ÷ total generation TWh`. Every year available is also
written to `out/sa-coal-share.csv` so the trend is checkable, not just the point.

## Why Ember rather than Eskom or CSIR

The plan named Eskom's data portal, and it does not work for this claim:

- The portal's charts are rendered client-side; the pages expose images, not data
  files. Its station build-up covers **Eskom's own** stations, which excludes the
  IPPs that are almost entirely renewables — so Eskom-only would overstate coal's
  share of national electricity.
- The CSIR report has the right numbers, but it is **copyright CSIR with no open
  licence**, so pinning the PDF in a public repo is redistribution I should not
  do for a claim I can compute instead.

Ember is CC BY 4.0, machine-readable, and covers total generation. That makes the
claim Tier A — recomputed rather than transcribed — which is the stronger form.

## The cross-check that makes it credible

**CSIR's own report says 81.1 % for H1 2025** (86.2 TWh of 106.4 TWh), from a
different compilation of utility-scale data. Two independent compilers landing
within **0.2 percentage points** is the kind of agreement that a single source
can never give you.

The two are not the same quantity, and the difference is instructive: CSIR
excludes embedded generation and municipal capacity, Ember's total is larger.
Coal's share of *utility-scale* generation can therefore sit slightly above its
share of *all* generation without either source being wrong.

## What the number does and does not say

- It does **not** say coal is finished. 81 % is four-fifths of the grid.
- It does **not** say coal is growing. 2024 was 83.5 %; 2025 is 81.3 %.
- It does **not** say the transition is on track. Renewables are displacing coal
  slowly, and the absolute coal number moves with total demand, which fell.

A share can fall for two reasons — clean generation rising, or total generation
falling faster. `out/sa-coal-share.csv` carries both absolute numbers so that
ambiguity is visible rather than resolved by the headline.

## Receipts

- Snapshot: `data/ember-yearly/<snapshot>/release_generation_yearly_global.csv`
- Series: `out/sa-coal-share.csv` (2000–2025)
- Cross-check: CSIR Energy Centre, *Utility-scale power generation statistics in
  South Africa 2025*, p. 9 — cited, not pinned (no open licence).
- Source: <https://ember-energy.org/data/yearly-electricity-data/>
