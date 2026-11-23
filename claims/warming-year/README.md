# warming-year — 2024, on the 1850–1900 baseline

**Tier:** A · **Dataset:** `gistemp` · **Published:** 1.55 °C · **Tolerance:** 0.06 °C

## Claim

2024 was the warmest calendar year in the GISTEMP record, and its global mean was
≈1.55 °C above the 1850–1900 pre-industrial average.

## Method

1. Parse `GLB.Ts+dSST.csv` (GISTEMP v4), annual means in `J-D`. Incomplete years
   (`***`) are dropped.
2. Build the baseline offset from the pinned series itself: the 1880–1899 mean
   anomaly is subtracted (re-basing to 1880–1899), then **+0.038 °C** is added to
   reach 1850–1900, the value NASA's FAQ quotes for that step.
3. Take the warmest year and convert it once.

`offset = -mean(1880–1899) + 0.038 = 0.2245 + 0.038 = 0.2625 °C`

2024 = 1.28 °C vs 1951–1980 → **1.54 °C vs 1850–1900**.

## The finding: NASA's FAQ does not reconcile with NASA's data

The FAQ says the correction "is equivalent (as of Jan 2025), of adding ~0.19 °C."
The published series contradicts that: the 1880–1899 mean is **−0.2245 °C**
relative to 1951–1980, so the conversion must be ≈**0.26 °C**.

Using 0.19 would put 2024 at 1.47 °C, **0.08 °C below** the WMO headline and
outside this claim's tolerance. The tolerance is what discriminates between the
two offsets; it is not decoration.

This is a documentation discrepancy, not a data one — the file agrees with WMO's
1.55 to within 0.01 °C once the recomputed offset is used. Recorded here rather
than silently resolved, because "which offset" is exactly the step where a
plausible wrong number enters.

## Caveat: this is one dataset

WMO's 1.55 °C is an average across several datasets (HadCRUT5, NOAAGlobalTemp,
GISTEMP, Berkeley Earth, ERA5). GISTEMP alone is not the headline; it reproduces
it. A difference of a few hundredths between datasets is expected and is not a
disagreement about the physics.

## Receipts

- Snapshot: `data/gistemp/<snapshot>/` (origin URL + SHA-256 in `provenance.json`)
- Series: `out/warming-year.csv`
- Offset constant: `constants.toml` → `[warming] sibling_offset_c`
- NASA FAQ: https://data.giss.nasa.gov/gistemp/faq/
