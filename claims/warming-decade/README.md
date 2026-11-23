# warming-decade — the observed 2015–2024 mean

**Tier:** A · **Dataset:** `gistemp` · **Published:** 1.25 °C · **Tolerance:** 0.05 °C

## Claim

The observed global mean for 2015–2024 was ≈**1.25 °C** above 1850–1900.

## Method

Same parse and same offset as `warming-year` — identical pipeline, so a bug in
the conversion moves both numbers and the disagreement shows up twice:

`mean(2015–2024) = 0.985 °C vs 1951–1980` → `+ 0.2625` → **1.2475 °C**.

## The distinction this claim exists to keep

**Observed decadal mean ≠ human-induced warming.** They are quoted
interchangeably and are not the same number:

| Quantity | What it is | Rough value now |
|---|---|---|
| Observed decadal mean | what the thermometers averaged | **≈1.25 °C** |
| Human-induced warming | the trend attributable to us, natural variability removed | **≈1.3–1.4 °C** |

The second comes from attribution studies (Indicators of Global Climate Change),
not from a raw series. A grounding note written before this project conflated the
two and quoted 1.3–1.4 °C as the decadal average; the recomputation says 1.25.

The observed mean sits *below* human-induced warming at the moment because the
last few years have been pulled down by La Niña relative to the underlying trend
— which is also why a single hot year (2024, 2026) is not evidence of a step
change, and a single cool year is not evidence of a pause.

## What would falsify this

A revision that moves the 2015–2024 mean by more than 0.05 °C, or a change in
the baseline offset. Both are visible in `make verify`; neither is visible in a
news article.

## Receipts

- Snapshot: `data/gistemp/<snapshot>/`
- Series: `out/warming-decade.csv` (10-year running mean, converted)
- Offset: `constants.toml` → `[warming]`
