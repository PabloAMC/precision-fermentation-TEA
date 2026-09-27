# Project plan (v2, 2026-09-26)

**Purpose.** A public techno-economic analysis of precision-fermented whey (β-lactoglobulin)
and egg-white (ovalbumin) proteins, at the standard of Humbird's 2021 cultivated-meat TEA.
Audience: the alt-protein community, funders and EU policy. Deliverables: a report and
preprint, code and workbook as supplementary information, an interactive explorer, and a
one-page memo.

**The question** is fixed in [docs/SCOPE.md](docs/SCOPE.md): cost today, cost at the
physical limits, and the performance needed for price parity.

**Method.** A physics-bounded process model rather than a factored top-down one:
1. Element-balanced stoichiometry gives sugar, O₂ and heat per kg of protein.
2. Fermenter transport limits (O₂ transfer, cooling, viscosity) give the feasible
   productivity for each vessel size.
3. From those, size the plant and its schedule, the downstream train and the utilities.
4. Cost the capital bottom-up with facility-class factors, then the operating costs and
   the financing.
5. Calibrate the method against real prices before it is allowed to say anything new.

## Honesty protocol (binding for every phase)

1. **Four scenarios, never merged:**
   - `academic`: grade A/B data only;
   - `industry`: adds grade C survey data and company claims;
   - `required`: inverse, the performance frontier for $10, $20 and $50/kg;
   - `physical-limit`: the floor at physical and stoichiometric limits.

   The headline figure is `required`.
2. **Evidence grade on every parameter:** A peer-reviewed, B patent example, C company
   claim, D analogy, E guess. Tornado charts are coloured by grade.
3. **No tuning to calibration targets.** Structural parameters (cost curves, installation
   factors, labour and utility models) are fixed once. Every anchor must pass with only
   its own process inputs changed. Record failures in docs/VALIDATION.md before fixing
   them.
4. **Quotes, not numbers.** Every titers.csv row carries a verbatim quote and a locator.
   Nothing enters the base case until the quote has been checked against the full text on
   disk (`verified: yes`). Pablo audits by exception.
5. **Public data only.** No private disclosures, and no citing the model's own outputs.
6. **Pre-registered priors** (docs/SCOPE.md) are scored at release and never used to tune.
7. **Agreement with another model is consistency, not validation.** Only real market
   prices (baker's yeast, enzymes) anchor the method to reality. Say which kind of check
   each one is.

## Phases

| Phase | Weeks | Deliverables | Exit criterion |
|---|---|---|---|
| **A. Frame and learn** | 2 | docs/SCOPE.md, docs/PRIMER.md, docs/READING.md, exercise A1 | Pablo signs off SCOPE; reading and primer self-check done; A1 unit cost within 20% of $38.99/kg |
| **B. Evidence** (parallel with A) | 2–3 | Remaining P1 items fetched; 31 titer rows verified; Intelligen inputs extracted to `data/validation/`; price series for whey, egg white, dextrose and energy (US + EU); sources for OTR ceilings, maximum vessel size and heat per O₂ | Every parameter sourced and graded; fewer than 3 base-case guesses |
| **C. Process model** | ~8 | C1: port Humbird's yeast simulator (SI sheets A.1–A.3, Equip, RawUtil, Phys) and reproduce it. C2: product-formation reactions for both hosts and the maximum yield. C3: cooling and viscosity limits, giving feasible productivity vs vessel size. C4: downstream train sized from fluxes and capacities. C5: plant integration, schedule, utilities, waste; finance as capital charge and DCF. | Every module tested with its equations in the docstring; Humbird's baker's-yeast result reproduced within 1% (software check) |
| **D. Calibration** (overlaps C) | 2 | Frozen structure run on four anchors; docs/VALIDATION.md | Baker's yeast within ±25% of the market-implied cost (reality check); NREL cellulase ±20%; Intelligen OVA ±30%; Voutilainen ±30%. Misses explained, not tuned away. |
| **E. Results** | 3 | Four scenarios; Monte Carlo with correlated inputs; the SCOPE figures (cost map, cost bridge, frontier, floor, tornado, scale and siting) | All figures regenerate from one command. Sanity: industry-benchmark inputs outside $10–200/kg means look for an accounting error first. |
| **F. Review** | ~4, mostly waiting | Assumptions and figures sent to a GFI fermentation scientist, an enzyme-industry bioprocess engineer and a known sceptic (optionally Humbird); docs/REVIEW.md | Every comment answered or fixed |
| **G. Release** | 2 | Report plus engrXiv preprint, SI (code, YAML, exported workbook), explorer (cultivated-meat pattern), one-page memo, scored priors | Public |

**Status (2026-09-27, evening).** v2.1: the v2 draft was pre-reviewed by four simulated expert
reviewers (AI; `docs/ai-review/`), every comment answered in `docs/REVIEW.md`, and the resulting
changes made (`docs/AUDIT.md`, Phase F section), then checked against five further sources (decisions
log below). The human review (Phase F proper) waits on Pablo's
emails; the release (Phase G) waits on his go-ahead (`docs/RELEASE.md`).

**Status (2026-09-27).** v1 was audited (docs/AUDIT.md) and v2 implements the findings; phases
F (review packet) and G (release files) are being prepared. Earlier status, kept for the record:

**Status (2026-09-26, end of day).** A v1 draft of phases B–E and G is built and awaits
Pablo's review.
- **B:** four evidence files, 369 graded entries: hosts, downstream, engineering, prices.
- **C:** the process model, with Humbird's baker's yeast reproduced to 0.004%.
- **D:** the calibration record, with misses recorded (`docs/VALIDATION.md`).
- **E:** all analyses and figures, from one command.
- **G drafts:** report, memo, SI workbook and explorer.

Phase F (external review) has not started. Open items:
- 15 titer rows are not yet verified in full text.
- Pablo's SCOPE sign-off and the Phase A reading are pending.
- 9 parameters are still grade E (listed in the report's limitations).

## Decisions log

- **2026-09-27, follow-up reading after the pre-review (Claude; for Pablo's review):**
  - Five sources Pablo downloaded were read (Humbird 2017 aeration; Heyland 2010 and Looser 2015
    physiology; Intelligen's lactoferrin report; Lv 2023), three of them by AI reading passes
    whose findings were checked against the texts, table images and workbook cells.
  - Corrected: the compressor formula (Humbird's workbook puts k where (k−1)/k belongs; the PF
    model now uses the textbook form, the A.1 port keeps his); a latent failure of the aeration
    search at high DO; the lactoferrin comparison (Intelligen's figures are costs of production,
    $292 is its UF/DF-only case; now reconciled by category); the cation-exchange flow (Intelligen's
    20 CV/h replaces a guess); seed density and inoculum (Intelligen's flowsheet, 17.6 and 0.88 g/L).
  - Kept, with reasons (REVIEW.md, follow-up section): the 40 mg/g/h secretion ceiling of the
    best case, the production-maintenance range, our lactoferrin design and prices.
  - Added: `tests/test_data.py` (every data file parses; evidence schema and unique keys), after
    a malformed evidence entry was found.

- **2026-09-27, Phase F AI pre-review (Claude, under the "no mistakes" mandate; for Pablo's review):**
  - Four simulated reviewers (fermentation scientist, bioprocess engineer, sceptic, method author's
    perspective) reviewed v2; each comment was re-checked before acting (`docs/REVIEW.md`).
  - Fermenters are now priced from NREL's industrial vendor quote in both conventions; Humbird's
    aseptic cell-culture vessel prices, used in v2, are a named high case. This moves the base BLG
    from $29.4 to about $21/kg; see AUDIT.md for the evidence.
  - Humbird's air-sparged STR O₂ value (200 mol/m³/h per m³ of cell-free liquid) replaces the
    bubble-column 150 per m³ of broth; missing-equipment allowance 20% (his A.1 value).
  - The physical-limit scenario is presented as a best case conditional on an assumed secretion
    rate; "secretion without growth" is the report's lead caveat.
  - Kept, with reasons: Humbird's 9% fixed-cost rule, Intelligen's 500 g/L feed as the base, and the
    exclusion of start-up, working capital and failed batches.

- **2026-09-26/27, audit and v2 (Claude, at Pablo's request "make sure there are no mistakes",
  then "close the gaps"; for Pablo's review):**
  - Eight independent reviewers (R1–R8) audited v1; every finding, decision and effect is in
    `docs/AUDIT.md`, implemented in three commits on branch `audit-fixes`.
  - A research pass sourced the grade-E placeholders (P-1 to P-13); six guesses remain, four of them
    formerly hidden constants in the code.
  - Production-phase stoichiometry: the product yield is derived from Intelligen's Eq. 2 with a
    measured production-phase maintenance (AUDIT, decision on R2-Q2/R6-C2).
  - OVA's 50 g/L "practical solubility" is no longer a limit (P-8); it is a sensitivity.
  - Capital conventions renamed: "price-anchored capital (Humbird method)" and "design-report
    capital (NREL-style)" (Pablo, 2026-09-26).
  - Added at Pablo's request: milk and egg equivalents; a lactoferrin contrast case.
  - SCOPE's scenario definitions rewritten to match what runs (R8-m4).

- **2026-09-26, working mode:** Pablo reviews the finished v1 rather than gating each phase.
  Claude builds B through G as a complete draft. Gates that need Pablo move to that review:
  the SCOPE sign-off, the Phase A reading, and auditing the verified quotes by exception.
  The honesty protocol is unchanged.
- **2026-09-26** (defaults accepted by Pablo):
  - Products: BLG + OVA in v1; casein in v2.
  - Hosts: *K. phaffii* base, *T. reesei* variant.
  - Plant: nth-of-a-kind, 10 kt/yr base, swept 1–100 kt/yr; US Midwest base plus an EU
    variant.
  - Output: report + preprint. This replaces v1's "not a paper".
  - `openpyxl` added as a dev dependency.
  - Product specs: the GRN 1056-style concentrate is the base; the isolate is a variant.
- **2026-09-26, v1 build (Claude; for Pablo's review):**
  - *Escalation 2018→2025:* 1.33 (CEPCI and the BLS machinery PPI), replacing the placeholder 1.25.
    Humbird's own index (PPI chemicals, 1.23) is the low end; pumps and compressors (1.52) the
    high end. For consistency, the NREL anchor is deflated to 2007 with CEPCI (0.871), NREL's
    own index. This moved the recorded misses (see VALIDATION, record of changes).
  - *Cost bridge:* one change per step, ending exactly at the base case (asserted in code).
    OVA concentrate and isolate are shown as variants from the base.
  - *Feasibility:* designs past the O₂ or heat limit are never costed as if they worked.
    Required titers are searched only below the feasible ceiling. Tornado and Monte Carlo
    mark infeasible draws.
  - *OVA:* its practical solubility of 50 g/L (Intelligen's assumption) caps its titer and
    floor. A sensitivity with the cap lifted is reported next to the base.
  - *EU variant:* NL electricity (Eurostat band IF), EU gas (band I4), EU glucose proxies (C),
    NL wages (derived, B). Construction costs are the same as the US: no sourced location
    factor is on disk.
- **2026-09-26:** Calibration anchors changed:
  - add baker's yeast (reality check), NREL 2011 cellulase and Intelligen OVA 2025;
  - Voutilainen 2021 moves from anchor 1 to anchor 4;
  - Intelligen lactoferrin 2024 becomes an optional downstream check (not on disk).

  `tests/test_validation.py` is updated in Phase D.
- **2026-09-18:** Honesty protocol points 1–5 (then called amendments).

## What not to do

- No point estimate without its titer, rate and yield stated next to it.
- No more than two products in v1.
- No BioSTEAM or SuperPro as the core model. BioSTEAM may cross-check capital costs; the
  SuperPro trial may only be used to read Intelligen's example file.
- No claim that cannot be traced to a row in data/pf/base.yaml or data/evidence/.
- No first-of-a-kind penalty mixed into the base case; it is shown separately.
- No teaching numbers (docs/PRIMER.md, exercises) copied into the model; they are
  illustrative.

## History

v1 (2026-09-18) had phases 0–5. They map to v2 as follows:
- 0 (learn) → A
- 1 (data) → B
- 2 (deterministic model) → C + D
- 3 (uncertainty) → E
- 4 (review) → F
- 5 (release) → G

v1's "model additions queued for Phase 2" (O₂ feasibility test, per-unit downstream
sizing, labour scaled with fermenter count, correlated titer and batch-time sampling) are
now part of C3–C5 and E.
