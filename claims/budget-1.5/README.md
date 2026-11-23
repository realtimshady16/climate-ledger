# budget-1.5 — what is left, and for how long

**Tier:** B (transcribed) · **Dataset:** `gcb-paper` · **Published:** 170 GtCO2

quoted: the passage under "Quoted passage" below, p. 3215
page: p. 3215 (Executive summary), Earth Syst. Sci. Data 18, 3211-3288, 2026
second_read: pdftotext -layout re-extraction, 2026-11-23; wording and page match the pinned PDF
checked_by: agent, first read 2026-11-23; independent second read pending

## Claim

As of the beginning of 2026, the remaining carbon budget for a 50 % chance of
holding warming to 1.5 °C is **~170 GtCO₂**, which is **about four years** at
2025 emission rates.

## Why this one is transcribed, not computed

The remaining carbon budget is not in the workbook. It is derived in the paper
from a TCRE (transient climate response to cumulative emissions) framework, and
it depends on choices — likelihood, non-CO₂ forcing, whether the budget is dated
from 2020 or 2026 — that are not in the spreadsheet. Recomputing it would mean
reimplementing someone's method and calling the result "the" budget. So the
figure is quoted, with its page, and the arithmetic in the sentence is checked
instead.

## Quoted passage

> "The remaining carbon budget from the beginning of 2026 for a 50 % likelihood
> to limit warming to 1.5 °C is nearly exhausted (50 GtC, 170 GtCO2 left,
> equivalent to around 4 years at the 2025 emissions levels), consistent with the
> warming of the planet attributed to human activities, which reached 1.36 °C in
> 2024. Each additional cumulative emission of about 180 GtCO2 will lead to
> approximately 0.1 °C of warming. The remaining carbon budgets to limit warming
> to 1.7 and 2 °C above the 1850–1900 level have been reduced to 145 GtC
> (525 GtCO2, 12 years) and 290 GtC (1055 GtCO2, 25 years) respectively."

## Arithmetic check

170 GtCO₂ ÷ 38.1 GtCO₂/yr (the 2025 fossil rate) = **4.5 years** — "around four
years" is the floor, because total CO₂ (42 Gt) would give 4.0. Both readings
support the sentence; neither supports a longer one.

The implied TCRE is also checkable: 180 GtCO₂ → 0.1 °C is **0.56 °C per
1000 GtCO₂**, inside the IPCC AR6 range of 0.27–0.63. So the budget and the
warming rule are internally consistent.

## What this claim refuses to do

- It does not round 170 to "200" or "a few hundred". The number is small and the
  rounding is where it gets minimised.
- It does not treat "four years" as a date. It is four years **at current
  rates**; the budget is exhausted in 2030 only if emissions do not fall.
- It does not present 170 GtCO₂ as a physical cliff. It is a 50 %-likelihood
  budget under a specific accounting choice; the 1.7 °C budget is 525 GtCO₂.

## Page reference

p. 3215 (Executive summary), *Earth Syst. Sci. Data* 18, 3211–3288, 2026,
doi:10.5194/essd-18-3211-2026.

A Tier B entry reports `transcribed` until a second pass has read the quoted
passage against the PDF, and `confirmed` after. Here the second pass was a
different extraction path (`pdftotext -layout`) by the same agent: it catches a
wrong page or drifted wording, and it is weaker than an independent reader. A
human or model re-read is still worth doing and would not change the verdict.
