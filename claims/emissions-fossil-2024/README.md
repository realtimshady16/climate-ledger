# emissions-fossil-2024 — fossil CO2, 2024

**Tier:** A · **Dataset:** `gcb-workbook` · **Published:** 37.8 GtCO2 · **Tolerance:** 0.2

## Claim

Global fossil CO₂ emissions were **37.8 GtCO₂** in 2024 — the highest annual
figure on record at the time of publication.

## Method

From the "Global Carbon Budget" sheet of the pinned workbook:

```
net (GtC) = fossil emissions excluding carbonation − cement carbonation sink
net CO2   = net (GtC) × 3.664
```

2024: `10.5345 − 0.2243 = 10.3102 GtC` → **37.78 GtCO₂**.

### Why the subtraction is not optional

The workbook column says *excluding* carbonation; the paper's headline says
*including* the cement carbonation sink (0.2 GtC). Read literally, the column
would give **38.60 GtCO₂** — 0.8 Gt above the published figure and outside the
tolerance. The paper's own arithmetic resolves it: 10.31 + 1.25 land-use = 11.56
GtC = 42.4 GtCO₂, which is exactly the total it reports.

A reader taking the column heading at face value gets a plausible wrong number.
The README records the resolution rather than leaving it implicit in a script.

## Caveat: this is CO₂, not all greenhouse gases

37.8 GtCO₂ is carbon dioxide from fossil fuels and industry. It is **not** the
~58 GtCO₂e figure used for total greenhouse gases (which adds methane, nitrous
oxide and F-gases). Quoting one as the other is a common and large error.

## Receipts

- Snapshot: `data/gcb-workbook/<snapshot>/` (xlsx + `derived/Global_Carbon_Budget.csv`)
- Series: `out/emissions-fossil-2024.csv` (1859–2024)
- Paper: `data/gcb-paper/<snapshot>/essd-18-3211-2026.pdf`, p. 3215
