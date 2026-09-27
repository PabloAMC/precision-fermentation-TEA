# Review (Phase F)

Phase F sends the assumptions and results to outside experts and answers every comment
(PLAN.md). This file is the packet, the question list and the comment log.

Status (2026-09-27): human review not started. Pablo contacts the reviewers; the drafts below are
ready to send. An AI pre-review (four simulated reviewers, clearly labelled as AI) has been run so
that the obvious objections are answered before anyone's time is spent; the reviews are verbatim in
`docs/ai-review/`, and the responses and resulting changes (v2.1) are in the log at the end.

## What to send

1. `report/pf_tea_report.pdf` (the analysis, about 30 pages; the Summary and Results sections
   Q1–Q8 are the core).
2. `report/memo.pdf` (one page).
3. `docs/explorer.html` (self-contained; opens in a browser).
4. `report/pf_tea_SI.xlsx` (every parameter with its source, all result tables, a live accounting
   sheet).
5. `docs/AUDIT.md` (what the internal audit found and changed) and `docs/VALIDATION.md` (the
   calibration record).
6. Repository access (private until release; invite the reviewer on GitHub, or send a zip).

## Questions by reviewer

Each question points to where the assumption lives, so a reviewer can answer "yes / no, because".

### A. Fermentation scientist (for example GFI's fermentation science team)

1. **Production-phase stoichiometry.** No measured BLG or OVA yield on sugar exists. We derive the
   product-reaction yield (0.465 g/g, 80% of the energetic ceiling) so that the model reproduces
   Intelligen's lumped expression-phase stoichiometry, with a measured low-growth maintenance of
   0.0044 g/g/h (Rebnegger 2024). Is the production-phase glucose use of a real *K. phaffii* PF
   process closer to this (effective yield ~0.28 g/g) or to chemostat-level maintenance (~0.11 g/g)?
   Report, Methods 2.2; `data/pf/base.yaml` `strain.Y_ps_g_g`, `hosts.kphaffii.m_s_prod_g_g_h`.
2. **Secretion rate, and secretion without growth.** The base production phase follows
   Intelligen's design: 4.7 mg protein per g cells per hour while the cells barely grow. We cap
   specific productivity at 40 mg/g/h (a judgment, grade D); it binds in the best case and gates
   \$10/kg. What sustained q_p have you seen for a secreted food protein in yeast or fungi, and does
   it hold at near-zero growth (Rebnegger et al. 2024 saw it fall about fivefold)? Report, Q3–Q4.
3. **Cell density.** 107 g/L at the start of production (Intelligen's design, derived with a volume
   balance), 150 g/L maximum. Realistic for industrial *K. phaffii* on glucose?
4. **Minimum starting volume and feed concentration.** A batch may not start below 30% of the
   vessel (Intelligen's design), glucose is fed at 500 g/L (about 42 wt%, Intelligen's feed), and
   production starts at 107 g/L of cells. Together these set the base titer ceiling; a 600 g/L feed
   or fewer cells lift it (report Table "ceiling"). What starting volume (impeller submergence) and
   feed concentration do you use at scale?
5. **OVA solubility.** We dropped Intelligen's 50 g/L "practical solubility" as a limit (OVA dissolves
   at 200 g/L in water; egg white is ultrafiltered to ~110 g/L OVA). Do you know of a lower limit at
   pH 5–6 in fermentation broth?
6. **Titers.** Are the public titers in `data/titers.csv` the right ones? We know of no peer-reviewed
   BLG above 13.88 g/L (Yao 2026, ethanol-fed) or 5.14 g/L on glucose (Li 2026).

### B. Bioprocess engineer from the enzyme or dairy industry

1. **Fixed costs and factors.** Our base uses Humbird's facility factors and fixed costs of 9% of
   investment a year (maintenance 4%, insurance 5%, standing for all overheads); NREL-style design
   reports use about 2%. On the same plant the two differ by about 1.3×, most of it the fixed-cost
   rule. Which is closer to what a food PF plant costs to run? Report, Methods 2.5 and Calibration.
2. **Fermenters.** The base prices a 200 m³ fermenter from NREL's vendor quote for an enzyme-plant
   vessel (about \$1.1M in 2025 dollars); Humbird's quotes for an aseptic, ASME-BPE cell-culture
   reactor are 2.9× that (our high case). What does a 200 m³ SIP-rated food-PF fermenter cost?
3. **O₂ transfer.** We cap transfer at Humbird's air-sparged stirred-tank value, 200 mol O₂/m³/h per
   m³ of cell-free liquid (about 130 per m³ of broth at our base cell density, 100 at 150 g/L). In
   the base the vessel volume, not O₂, sets the titer ceiling. Which basis, and which number, would
   you design to with air? Report, Methods 2.3 and Results Q3.
4. **Diafiltration.** One patent value (5 L/m²/h at 50 g/L protein) sizes most of our membrane area.
   What diafiltration and final-concentration fluxes do whey or enzyme plants achieve?
5. **Dryer feed.** We feed the dryer at 30% solids (BLG) and 23% (OVA), concentrated by membranes,
   following dairy practice for >60%-protein concentrates. Right?
6. **Heat removal.** 25 kW/m³ (grade D); the vendor-quote vessel has internal coils; external loops
   for 400 m³ vessels are not costed. Reasonable?
7. **Labour, cleaning and spent cells.** Humbird's attention model gives ~120 operators and
   supervisors for 10 kt/yr; cleaning 7.3 kg solution per kg product; spent cells landfilled at
   $458/t dry (US). Any of these off by a large factor?

### C. A sceptic of PF cost claims

1. Is the "physical limit" best case (now shown against the secretion rate it assumes) meaningful,
   or does it still overstate what is achievable?
2. Is whey the right benchmark for BLG? We argue it is the right *price* benchmark and the wrong
   *impact* benchmark (report, section 1 and Results Q7).
3. Where does the analysis overclaim? The internal audit removed several overclaims (AUDIT R7);
   which remain?
4. The calibration anchors are models, not plants. What real cost data could test the model?

### D. Optionally, David Humbird (author of the method)

1. Does the port of the baker's-yeast workbook and its extension to a secreted protein respect the
   method? (Report sections 2–3; `src/pftea/humbird_yeast.py` reproduces A.1 to 0.004%.)
2. We now apply your air-sparged stirred-tank value (200 mol/m³/h) per m³ of cell-free liquid, as
   your Eq. 4.2 does. Is that what you intended for high-density microbial fermenters?
3. The compressor formula in A.1 (exponent 1.4) and the broth-volume update signs (VALIDATION.md,
   anchor 1 findings 1 and 3): are these intended?

## Email drafts (for Pablo to send; placeholders in brackets)

**To a fermentation scientist**

> Subject: Request for a critical read: open cost model of precision-fermented BLG and OVA
>
> Dear [Name],
>
> I have built an open techno-economic model of food-grade β-lactoglobulin and ovalbumin made by
> precision fermentation, following Humbird's 2021 method, with every input sourced and graded. Its
> weakest point is the strain physiology: no measured product yield on sugar exists, so I derive it
> from Intelligen's design with a measured low-growth maintenance, the production phase assumes
> secretion at near-zero growth, and I cap secretion at 40 mg/g/h. Would you be willing to spend an
> hour telling me where the fermentation assumptions are
> wrong? The six questions are on one page (attached, section A); the report and an interactive
> explorer are attached too. Everything is public data; I will credit reviewers who wish it and
> answer every comment in the repository.
>
> Best regards, Pablo Antonio Moreno Casares

**To a bioprocess engineer**

> Subject: Capital and downstream assumptions for a precision-fermentation cost model
>
> Dear [Name],
>
> I am checking an open cost model of precision-fermented whey and egg proteins against people who
> build and run such plants. Its largest cost uncertainties are the fermenter price (an enzyme-plant
> vendor quote against an aseptic cell-culture specification, 2.9× apart) and the fixed-cost rule
> (Humbird's 9% of investment a year against about 2% in NREL-style reports). The seven questions in
> section B of the attached page (fermenter costs, O₂ transfer design basis, diafiltration flux,
> dryer feed, heat removal, labour) are where your experience would change the answer most. Could
> you spare an hour? I will credit you if you wish and answer every comment publicly.
>
> Best regards, Pablo Antonio Moreno Casares

**To a sceptic**

> Subject: Please try to break this precision-fermentation cost analysis
>
> Dear [Name],
>
> I have written an open analysis of what precision-fermented BLG and OVA cost, and I would value a
> hostile read before it is public. It concludes that whey is hard to beat on price, that cheap
> protein needs faster secretion more than higher titers, and that at a design titer lactoferrin
> costs less than most reported dairy prices. An AI pre-review has already been answered in the
> repository. Where is it still wrong or overclaimed? The questions in section C and the report are attached; the full audit log
> of what has already been corrected is in the repository.
>
> Best regards, Pablo Antonio Moreno Casares

## Comment log

| # | Reviewer | Comment | Response | Change |
|---|---|---|---|---|
| — | — | Human review not started | — | — |

AI pre-review (simulated reviewers; not a substitute for the human review above): see below.

## AI pre-review (Phase F) <a id="ai-pre-review-phase-f"></a>

Four simulated reviewers (Claude, an AI model, each instructed to review as one expert) read v2 on
2026-09-27 (commit 5cbf9bc): a fermentation scientist (FS), a bioprocess engineer from the enzyme or
dairy industry (BE), a sceptic of PF cost claims (SC), and the perspective of the method's author
(HM; not David Humbird's opinion). Each was told to verify every comment against the code, the data
or a model run, and to give a checkable source for domain judgments. Their reviews are kept verbatim
(local file paths redacted) in [docs/ai-review/](ai-review/). **They are not human expert reviews**;
the human review above is still to come.

Every comment was re-checked before acting on it (verdicts below: *confirmed*, *partly*, *not
confirmed*). Where a reviewer's number was a judgment without a source on disk, it was not put into
the model; it appears as a caveat or an exclusion instead.

**Effect on the headline numbers** (BLG, 10 kt/yr, US, price-anchored capital unless noted):

| | v2 | v2.1 |
|---|---|---|
| Base case, \$/kg | 29.37 | 21.17 |
| Base case, design-report accounting | 16.06 | 16.42 |
| Base case with v2's aseptic cell-culture fermenters | (the v2 base) | 30.95 |
| Total capital investment | \$848M | $490M |
| Industry benchmark (42 g/L) | 21.91 | 15.84 |
| Titer ceiling at 72 h, 500 g/L feed (v2 said "50 wt%") | 74 g/L | 70 g/L |
| Titer ceiling at 72 h, 600 g/L feed | not shown | 105 g/L |
| Physical-limit case (40 mg/g/h secretion) | 6.11 | 4.10 |
| Physical-limit case at 10 / 5 mg/g/h | not shown | 8.09 / 12.11 |
| Cheapest design at base biology, 40 / 10 mg/g/h | not shown | 7.06 / 12.05 |
| Lactoferrin, 10 g/L (price-anchored / design-report) | 216 / 134 | 178 / 136 |

The largest change (BE-1, HM-2, SC-3): v2 priced fermenters with Humbird's quotes for the aseptic
cell-culture reactor he designed for cultured meat (ASME BPE, 316L, full vacuum; his text Table
3.3). The yeast workbook that anchors his method uses a bubble column at a third of that price, and
Intelligen's food-PF design and NREL's enzyme-plant vendor quote agree with the lower price. v2.1
prices fermenters from the vendor quote and keeps the aseptic curve as a named high case. With it,
our capital for Voutilainen's plant is within +1.8% of theirs and Intelligen's cost within
−3.5% of ours; the remaining gap to NREL-style designs is the fixed-cost rule.

### Fermentation scientist (FS)

| # | Comment (short) | Checked | Response | Change |
|---|---|---|---|---|
| FS-1 | "50 wt%" feed is really 500 g/L (≈42 wt%); the ceiling and "$10/kg not reachable" depend on it; 600–700 g/L is common | Confirmed (base.yaml; Shemesh 2024 feeds "60% (w/v)"; Aro 2023 "55 % glucose") | Accepted | Feed now in g/L everywhere (`fermenter.feed_glucose_g_L` 500, range 500–600); 600 g/L sensitivity replaces "65 wt%"; the physical-limit case uses 600 g/L; the ceiling and the $10/kg statement are given per feed (report, Q3) |
| FS-2 | The energetic ceiling counts only peptide bonds; the physical-limit yield 0.55 may exceed a fuller bound; Heijnen applied to protein gives ~0.50 | Partly: amino-acid synthesis from glucose + NH4+ costs 0.28–0.29 ATP per residue on Stouthamer's accounting as recomputed by Martin et al. 2025 (the reviewer's 1–2 is closer to the unweighted 1.2); sulfate assimilation adds ~0.5 ATP-eq per residue; Heijnen-for-protein reproduced (0.501 BLG) | Accepted with the sourced costs | Ceiling = peptide bond + amino-acid synthesis + sulfate assimilation: BLG 0.582 → 0.564, OVA 0.590 → 0.570; physical-limit yield 0.55 → 0.535 (0.95 × ceiling); the Heijnen estimate is reported as a non-bounding alternative |
| FS-3 | The floor is set by the 40 mg/g/h secretion ceiling, ~10× anything measured in K. phaffii; show it at today's rates | Confirmed (the ceiling binds; base design 4.7; Yao 2026 ≈1; Ellilä 2017 productivities) | Accepted | Case shown at 5/10/20/40/120 mg/g/h (report, Q4); range of the ceiling 5–40 (low = Intelligen's design rate); summary and memo call it a best case conditional on secretion |
| FS-4 | The Y_ps inversion is unstable in m_s; production-phase glucose uptake (0.017 g/g/h) is below what holds a secreting culture; real effective yield 0.08–0.19 | Confirmed arithmetic; new evidence found in our own file: Rebnegger 2024 (our maintenance source) saw secretion fall as growth slowed and settle ~5× below the chemostat trend | Accepted as text and as the lead caveat; the 0.08–0.19 is the reviewer's judgment (not modelled) | Report §2.2 gives the inversion's sensitivity, the implied uptake (0.016 g/g/h) and the secretion-without-growth caveat; funders' first question |
| FS-5 | "Effective yield 0.276, close to Intelligen" holds only at 30 g/L | Confirmed | Accepted | Report gives it at base, industry and physical limit |
| FS-6 | kLa is water-like at ~12% protein and >100 g/L cells; 40 kW/m³ in 400 m³ is 16 MW per vessel | Confirmed | Accepted as caveats (no source for a titer-dependent kLa) | §2.3 "What the fermenter model leaves out"; §4.5 on external loops |
| FS-7 | Ethanol-fed academic BLG understates O2 and heat; the modelled batch ends at 88 g/L cells vs ~122 | Confirmed (quote verified in Yao 2026) | Accepted | §2.7 flags both |
| FS-8 | T. reesei OVA: the 2 g/L is mostly clipped protein | Confirmed (Aro 2023: purified TrOVA "a major band of approximately 36 kDa with an estimated purity of 80 %") | Accepted | 1 g/L intact-OVA variant (judgment, D): $489/kg vs $246/kg at 2 g/L |
| FS-9 | T. reesei maintenance uses the yeast correlation | Confirmed | Answered: no measured T. reesei value on file to widen the range with | Stated as a lower bound on its sugar use |
| FS-10 | The heat screen uses 460 kJ/mol O2 while the batch computes 480–510 | Not confirmed as an error: the batch slows growth to the heat limit with its own heat and every design's peak is checked against the ceiling; 460 only screens the O2 cap | Answered; text corrected (product reaction 520–570, HM-9) | §2.2 |
| FS-11 | X0 = 5 g/L contradicts the 60 g/L seed | Confirmed | Accepted | X0 = 3 g/L (5% × 60); then 0.88 g/L, 5% of the 17.6 g/L seed broth read in Intelligen's lactoferrin flowsheet (follow-up L), which gives a 37 h growth phase against Intelligen's 36 h |
| FS-12 | State the direction of constant q_p and no product in growth | Confirmed | Accepted | Limitations list the direction of each simplification |
| Titers | Lv 2023 lacto-protein 5.4 g/L; Yang 2009 quail OVA | Resolved from the primary paper (Lv 2023, Green Chem 25:5460): the 5.4 g/L is human lactoferrin, not BLG, methanol-induced in a 3 L fermenter and measured by ELISA only; the CO2-derived-methanol result is 56 mg/L in a shake flask | Accepted | `data/titers.csv`: the secondary row replaced by three primary rows with quality flags |

### Bioprocess engineer (BE)

| # | Comment (short) | Checked | Response | Change |
|---|---|---|---|---|
| BE-1 | "Price-anchored" does not cover the fermenter price: the base uses Humbird's STRFERM at 3.2× the anchor's vessel | Confirmed (Equip sheet; Humbird text Table 3.3: aseptic, ASME BPE; A.1 bubble column $779k) | Accepted | Vendor-quote fermenters in both conventions (`capital.fermenter_quote`); aseptic curve as high case (+$9.8/kg) |
| BE-2 | Feed mislabelled; ammonia at 1 kg/L | Confirmed (GESTIS: 30% NH3 ≈ 0.895 kg/L) | Accepted | See FS-1; ammonia at 268 g/L |
| BE-3 | 9% fixed costs are high, unranged and hidden in the convention bar; CIP chemicals double counted | Partly: 9% is Humbird's rule, and his yeast workbook needs it to reach the market band (NREL-like fixed costs give $1.62/kg; the full NREL-like set $1.37/kg, below the $1.47–$2.11 band) | Kept as the base convention; the double count removed; the gap decomposed | CIP chemicals inside Humbird's 4% (HM-8); report §2.5 splits the convention gap: fixed-cost rule $3.32, factors $1.43 |
| BE-4 | Equipment list short; 10% allowance low | Confirmed (CIP/feed tanks, filter housings, sugar storage, inactivation, packing, effluent) | Accepted | Missing allowance 20% (Humbird A.1 for an abbreviated list), range 10–20% |
| BE-5 | Vessels escalated with composite CEPCI; the tank PPI rose 1.92× | Confirmed (prices.yaml) | Partly: one index kept for all equipment | Sensitivity: fermenters at the tank PPI +$2.28/kg |
| BE-6 | Chillers sized as if all fermenters peaked at once; no heat-transfer hardware | Confirmed | Accepted | Chillers and compressors sized on the coincident plant peak (27.3 MW vs 72.6 MW); the vendor quote includes internal coils; external loops for 400 m³ not costed (stated) |
| BE-7 | Design to 100–120 mol/m³/h with air; "376" is not a physical limit | Confirmed (Humbird: kLa ~800 h⁻¹; STR ~200) | Accepted | Cap = Humbird's STR value on his cell-free basis: 129 per m³ broth at 107 g/L; "376" labelled an extrapolation. Aeration power checked (follow-up H1): the model reproduces Humbird's 2021 aeration sheet (0.50 vs 0.50 kWh/kg O₂ with his compressor formula); Humbird 2017 implies about twice that |
| BE-8 | DF flux applied beyond its evidence; skid cost installed twice; no CIP downtime; dryer high end low | Partly: the skid double count confirmed (our evidence note: "probably installed") | Skid treated as installed; DF flux kept (the 10–20 LMH needs Cheryan, not on disk) and called probably conservative; downtime and dryer noted | `dsp.membrane_skid_usd_m2` backed out to a purchase cost |
| BE-9 | Disposal fee at 20% solids vs the model's 15% paste; landfill unlikely central | Confirmed | Accepted the solids; route kept (sourced), outlet credit as the low end | US $458, EU $211 per t dry |
| BE-10 | No salaried staff, QC or packaging | Confirmed | Answered: the 9% fixed-cost rule stands for overheads (no double count); QC and packaging listed as exclusions | Report §2.1 and §6 |
| BE-11 | Start-up, working capital and failed batches missing (~+$1.6/kg) | Confirmed | Answered: not in Humbird's anchored method; listed as exclusions next to the headline | Report §2.1 |
| BE-12 | CEX cycle 3.5 h ignores ~26 CV of dilute load | Confirmed | Accepted | Cycle computed from load + buffer CVs: 2.1 h at Intelligen's 20 column volumes per hour (follow-up L; the draft guessed 5) |
| BE-13 | Convention ratios mixed up (1.8× vs 2.4–2.5×; Lang 5.1/5.2/5.15) | Confirmed | Accepted | Ratios from JSON; REVIEW questions rewritten |
| B1–B7 | Answers to section B | — | Logged; they informed BE-1 to BE-12 | — |

### Sceptic (SC)

| # | Comment (short) | Checked | Response | Change |
|---|---|---|---|---|
| SC-1 | "$10/kg needs every lever" is wrong: fewer cells and higher titer suffice; the gate is q_p | Confirmed | Accepted | New analysis: cheapest design at base biology by secretion ceiling (report, Q3); q_p given for every required titer |
| SC-2 | The "physical-limit floor" is set by a judgment; not a floor | Confirmed | Accepted | Called a best case; curve over 5–120 mg/g/h; every lever listed; memo reworded |
| SC-3 | Price-anchoring cannot separate the conventions; half the gap is fixed costs; Intelligen matches the lighter capital | Confirmed | Accepted (with BE-1) | Anchor text rewritten (what it supports and what not); "the only convention tied to a real price" and "conservative" dropped |
| SC-4 | Relaxed ceilings are still set by the starting volume; sensitivity one-sided | Confirmed | Accepted | Ceiling table adds 35/40/50% starts and 80 g/L cells; text corrected |
| SC-5 | "2.4–2.5× lower" and "most published PF studies" overgeneralise | Confirmed | Accepted | Numbers from JSON; "NREL-style design reports"; Intelligen stated |
| SC-6 | Lactoferrin: Intelligen's own $292/kg omitted; band nominal; interested-party source | Confirmed (GFI 2025 p.28 quote) | Accepted, then corrected from the primary report (follow-up L): $292 is Intelligen's UF/DF-only case per kg lactoferrin and a cost of production | Both Intelligen cases shown as costs of production, $299 and $441 (2025$), against ours, $113 and $159, and reconciled by category; band deflated ($250–$1,585); summary says "at a design titer" |
| SC-7 | Claims priced at the shortest time, where q_p hits the ceiling; labels | Confirmed | Accepted | Claims at their own time and, labelled, at the shortest; labels fixed |
| SC-8 | MC infeasibility explained wrongly; feasible-only percentiles; academic X range; titer range grade | Confirmed | Accepted | Reasons and input means recorded; all-draw percentiles; academic BLG cells 40–60; industry titer 24–54, grade C |
| SC-9 | Whey protein fraction; egg white not always dearer; "spike years" | Confirmed | Accepted | Band at 88% protein shown; egg-vs-whey years computed; wording |
| SC-10 | Explorer states the equivalents bias backwards; egg bound loose; whey share mixes years | Confirmed | Accepted | "This flatters PF"; dried egg white per egg ($0.035–$0.077 per egg); year-matched whey share (11%–21%) |
| SC-11 | The cost bridge costs infeasible designs | Confirmed (q_p 118 > 40) | Accepted | Marked † in the figure and text |
| SC-12 | Prior 2 scored against a later judgment, twice | Confirmed | Accepted | Scored once, conditionally |
| SC-13 | Nine wording items | Confirmed | Accepted | All fixed |
| C1–C4 | Answers to section C | — | Logged; C4's list of real-cost data is in the funders' section | — |

### Method-author perspective (HM)

| # | Comment (short) | Checked | Response | Change |
|---|---|---|---|---|
| HM-1 | Feed label (as FS-1) | Confirmed | Accepted | As FS-1 |
| HM-2 | Price-anchoring covers the factors, not the vessel; A.1 uses a flat Lang 4.5; the commodity-aerobic class is never used by Humbird | Confirmed | Accepted | As BE-1; text says so |
| HM-3 | 150 is the bubble-column cap; the STR value is ~200 on the cell-free basis (Eq. 4.2) | Confirmed (Humbird p.28, p.49, p.91) | Accepted | Base cap 200 per m³ cell-free liquid |
| HM-4 | The method stops at 2 cP; kLa has no viscosity term | Confirmed (Humbird p.92) | Accepted as caveat | §2.3 |
| HM-5 | The ISBL factor on fermenters is undocumented | Confirmed | Accepted | Documented in base.yaml and AUDIT |
| HM-6 | The derived yield absorbs the host-cell protein | Confirmed | Accepted | §2.2 |
| HM-7 | The compressor effect is about zero, not $0.1/kg | Confirmed | Accepted, then the formula corrected (follow-up H1: Humbird's workbook puts k where (k−1)/k belongs, 1.6× the power) | Textbook adiabatic compressor in the PF model (+$0.02/kg against the workbook formula, which the A.1 port keeps) |
| HM-8 | CIP chemicals counted twice | Confirmed (Humbird p.46 quote) | Accepted | Removed under Humbird's rule |
| HM-9 | Product-reaction heat is 520–570 kJ/mol O2 | Confirmed | Accepted | §2.2 |
| D1–D3 | Answers to section D (A.8 exponent 0.2 in print vs 0.7 in the workbook) | — | Logged; VALIDATION notes the exponent | — |

### Follow-up reading (2026-09-27, same day)

Papers Pablo downloaded after the pre-review were read by three further AI reading passes (H1:
Humbird, Davis & McMillan 2017 on aeration; H2: Heyland 2010 and Looser 2015 on production
physiology; L: Intelligen's lactoferrin report, February 2026), and by the assistant directly (Lv
2023, Prielhofer 2018, Rebnegger 2014, Aro 2023). Each finding was checked against the source
text, the page images of tables, or the workbook cells before acting.

| Source | Finding | Action |
|---|---|---|
| Humbird 2021 SI, Fig1.3; Humbird 2017 | The compressor formula of Humbird's workbook (copied into our model) puts k = 1.4 where (k−1)/k belongs; with it, our aeration matches his 2021 sheet (0.50 vs 0.50 kWh/kg O₂) | Textbook adiabatic compressor in the PF model (+$0.02/kg against the workbook formula); the A.1 port keeps his formula; aeration check stated in §2.3 |
| Humbird 2017 | Process simulations imply about twice the 2021 aeration energy; their DO was not controlled | Stated; sensitivities: DO at 50% of saturation +$0.26/kg, no kLa temperature term +$0.07/kg |
| Our code (H1) | The aeration search returned no solution at DO setpoints of 50% and above (it read a lean exit gas as too much air) | Fixed; the base setpoint is unaffected; test added |
| Heyland 2010 | Its 6.5 g/L is an intracellular product (pGAPZ A, crude-extract assay); densities above ~155 g/L slowed growth and are called small-scale only; a 730 g/L feed | Evidence entry; never cited for secretion; X_max and feed notes; the physical limit mentions the feed |
| Looser 2015 | Compiled secreted q_P,max 0.004–0.69 mg/g/h; glucose (GAP) entries peak at µ 0.15–0.20 and are growth-coupled; maintenance 0.009–0.032 g/g/h on methanol and glycerol only | Lead caveat and §2.2; the production-maintenance bound computed (0.0062 g/g/h at the energetic ceiling); q_p_max kept at 40 as a stated best-case judgment |
| Intelligen LF report (2026) | $262.43/kg powder (case a, UF/DF only) and $406.95 (case b, cation exchange) are unit production costs; six 100 m³ fermenters; CEX at 20 CV/h; seed broth 17.4–17.8 g/L | Comparators corrected to cost of production and reconciled by category (report, lactoferrin reconciliation table); CEX flow 20 CV/h (B) replaces the guess; seed density and inoculum from the flowsheet; three evidence entries corrected |
| Lv 2023 | The 5.4 g/L is human lactoferrin (not BLG), methanol-induced, ELISA only | Titer rows replaced (see "Titers" above) |
| Prielhofer 2018; Rebnegger 2014 | Best glucose fed-batch secretion 2.1 mg/g/h near µ 0.1; secretion rises with µ | "Best demonstrated" case (q_P 2.1) in the best-design and physical-limit tables |

The reading reports are kept verbatim in [docs/ai-review/](ai-review/) (H1, H2, L).

Adopted from them besides the table: the growth-rate range of the host (µ_max 0.15–0.28/h, Heyland's
producing strain and its non-producing parent), Intelligen's buffer volumes and 97% step recovery as
the high ends of the cation-exchange ranges, a 10% dryer feed as the low end for lactoferrin, and
source notes on the titer, cell-density, feed and secretion-ceiling parameters.

Not adopted, with reasons: a secretion ceiling of 5 mg/g/h as the base (the physical-limit case is
defined as a best case at assumed limits and is shown from 2.1 to 120 mg/g/h); a production-maintenance
high of 0.032 (Looser's values are Pirt fits from growing cultures on other substrates, and maintenance
falls at near-zero growth); a production growth-rate high of 0.0047/h (H2 called 0.02 an impossible
corner, but the model already stops growth at the maximum cell density, so that end is a plateau); a
730 g/L feed as the high end (a 2.6 L laboratory value; noted); Intelligen's 100 m³ vessels and SuperPro
unit prices for our lactoferrin case (our design and sourced prices are kept; the reconciliation shows
their effect); a QC line (listed as not costed).
