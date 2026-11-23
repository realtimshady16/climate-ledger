# emissions-total-2024 — total anthropogenic CO2, 2024

**Tier:** A · **Dataset:** `gcb-workbook` · **Published:** 42.4 GtCO2 · **Tolerance:** 0.3

## Claim

Total anthropogenic CO₂ emissions — fossil plus land-use change — were
**42.4 GtCO₂** in 2024.

## Method

Same sheet, same carbonation correction as `emissions-fossil-2024`:

```
(10.3102 fossil + 1.2515 land-use) × 3.664 = 42.38 GtCO2
```

## What this number is and is not

| Figure | What it covers | 2024 |
|---|---|---|
| Fossil CO₂ | coal, oil, gas, cement, flaring | 37.8 Gt |
| Land-use CO₂ | deforestation minus regrowth | 4.6 Gt |
| **Total CO₂** | **this claim** | **42.4 Gt** |
| Total greenhouse gases | CO₂ + CH₄ + N₂O + F-gases, CO₂e | ~58 GtCO₂e |

The last row is the UNEP Emissions Gap Report's basis and is roughly 37 % larger.
The gap between 42 and 58 is mostly methane — which is why methane policy is not
a rounding error.

## Land-use is the soft number

`ELUC` carries ±0.7 GtC (±2.6 GtCO₂), the largest relative uncertainty in the
budget, because it is the average of three bookkeeping models. The 2025 edition
also introduced corrections to `ELUC`, the ocean and land sinks, so this series
is not directly comparable with editions before it.

## Receipts

- Snapshot: `data/gcb-workbook/<snapshot>/`
- Paper: `data/gcb-paper/<snapshot>/essd-18-3211-2026.pdf`, p. 3215
