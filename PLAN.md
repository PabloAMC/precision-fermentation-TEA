# Project plan

Purpose: calibrated, verifiable cost estimates for PF whey and egg proteins, for
the alt-protein community and impact investors. Not a paper. A public benchmark.

## Phase 0 — Learn the accounting (3 weeks, ~15 h)
Read in the order given in docs/READING.md. Exit criterion: you can rebuild
Voutilainen 2021's cost table by hand in a spreadsheet within 20%.

## Phase 1 — Data table (2 weeks)
Fill data/titers.csv with every public titer, yield and secretion figure for
BLG and ovalbumin (papers, patents, company disclosures). Fill
data/assumptions.yaml with base/low/high and a source for every line.
Exit criterion: fewer than 3 parameters with source "guess".

## Phase 2 — Deterministic model (4–6 weeks)
Implement upstream -> downstream -> capex -> opex -> economics.
Exit criterion: tests/test_validation.py passes (Voutilainen within 20%,
Intelligen lactoferrin within 30%).

## Phase 3 — Uncertainty (2 weeks)
Monte Carlo over titer, yield, DSP recovery, sugar price, CapEx factor.
Tornado chart. Cost-vs-titer curve per product.
Exit criterion: industry-benchmark inputs (42 g/L, 10,000 t/yr) land in the
$20–200/kg band; if not, find the accounting error.

## Phase 4 — Review (2–3 weeks, mostly waiting)
Send assumptions.yaml and the three figures to one GFI fermentation scientist
and one bioprocess engineer. Fix what they flag. Record their comments in
docs/REVIEW.md.

## Phase 5 — Release
Interactive page (reuse the cultivated-meat page pattern), short write-up,
one-page memo. Headline framing: "what must be true for PF dairy/egg proteins
to reach $X/kg".

## What not to do
- No point estimate without a titer stated next to it.
- No more than two products.
- No BioSTEAM as the core model; use it only to cross-check CapEx.
- No claim that cannot be traced to a row in assumptions.yaml.

## Amendments (2026-09-18, after first review of the scaffold)

Honesty protocol — these are binding for every phase.
1. **Three scenarios, never merged.** `academic` (grade A/B data only), `industry`
   (adds grade C survey/company claims), `required` (inverse: the titer/yield/recovery
   frontier needed to hit $10, $20, $50/kg). The headline figure is `required`.
2. **Evidence grade on every parameter** (A peer-reviewed, B patent example,
   C company claim, D analogy, E guess). Tornado charts are coloured by grade.
3. **No tuning to validation targets.** Structural parameters (cost curves, Lang
   factor, labour and utility models) are fixed once; both validation tests must
   pass with only the papers' own process inputs changed. Record failures in
   docs/VALIDATION.md before fixing them.
4. **Quotes, not numbers.** Every titers.csv row carries a verbatim quote and
   locator; nothing enters the base case until the quote is checked against the full
   text on disk (`verified: yes`). Pablo audits by exception, not row by row.
5. **Public data only.** No private disclosures, no citing the model's own outputs.

Model additions queued for Phase 2.
- Oxygen-transfer feasibility test: titer/(yield*batch_time) implies an O2 demand;
  reject parameter sets above the OTR ceiling of large aerobic vessels
  (order 150-250 mmol/L/h; source to be fixed in Phase 1).
- Per-unit DSP sizing (filtration, optional chromatography with resin cost, drying)
  replacing dsp_capex_multiplier; "no chromatography" is a named scenario.
- Labour scaled with fermenter count; correlated sampling of titer and batch time.
- Validation anchor candidates to add: NREL 2011 on-site enzyme section;
  Klein-Marcuschamer 2012 cellulase cost. Decide after reading (Phase 0).

Phase 4 addition: a third reviewer who is a known skeptic of PF economics.

Layout addition: `references/` (INDEX.md committed; PDFs and text dumps ignored),
`docs/LITERATURE.md` (what exists, what does not), `docs/VALIDATION.md`.
