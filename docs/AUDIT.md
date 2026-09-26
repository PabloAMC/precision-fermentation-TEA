# Audit log (v1 draft, 2026-09-26)

Eight independent reviewers (R1–R8) audited the v1 draft on branch `v1-draft`. Each owned one
area and worked read-only: every finding had to carry a computation, quote or code line.
This log records each finding, the decision taken and its effect. "Fix" means the code, data or
text was changed; "Document" means the behaviour is kept and stated. Effects are on the base BLG
price unless noted.

Reviewer areas:
- R1: stoichiometry and energetics
- R2: fermenter physics
- R3: plant costing
- R4: finance, scenarios and calibration
- R5: prices and benchmarks
- R6: process evidence and titers
- R7: report, memo and explorer
- R8: teaching documents

## R1 — stoichiometry and product energetics

Verified independently: formulas and molar masses of BLG and OVA (from UniProt sequences),
element balances of every reaction (residuals ≤ 5e-16), the Heijnen and Tijhuis
implementations, and the product-reaction O₂ use (71.5 mol/kg BLG at 0.28 g/g).

| ID | Finding | Decision | Effect |
|---|---|---|---|
| R1-F1 | Report states max growth yield 0.52 g/g and biomass γ ≈ 4.2. Those are Humbird's baker's-yeast values; our *K. phaffii* formula gives 0.57 g/g and γ 4.06 | Fix text (report, VALIDATION) | none on costs |
| R1-F2 | The energetic ceiling counts polymerisation (4 ATP/bond) but not the ATP cost of amino-acid synthesis. It also assumes 28 ATP/glucose, while our own evidence gives P/O 1.48 (≈21.8 ATP/glucose) | Fix: ATP per glucose from the sourced P/O ratio; call the ceiling an upper bound and state the proxy estimate of the omitted cost (−5–7%) | < 0.2% |
| R1-F3 | C-mol → g DCW ignores the 7% ash; the Heijnen yield would then overshoot measured maxima. The two effects cancel in glucose per g DCW (model 1.75 vs measured 1.71–1.84) | Document the convention and the cancellation | −1.3% if ash alone were corrected |
| R1-F4 | Heat uses dissolved-gas enthalpies without O₂-dissolution / CO₂-stripping heats | Document | −0.1% |
| R1-F5 | 460 kJ/mol O₂ is labelled "Cooney" (it is Roels); formation enthalpies give ~490 (batch) and ~505 (growth); dead constant in plant.py | Fix labels, state the gap, remove the dead code | < 0.5% |
| R1-F6–F8 | Maintenance quoted as 0.018 (is 0.0174 g/g/h); protein γ "~4.3" (is 4.24/4.18); OVA "42.8 kDa" (is 42.75) | Fix text | none |
| R1-F9 | "Post-translational modifications < 2% of mass" is wrong for glycosylated OVA (3–6%) | Fix text; mass-balance effect ≤ 0.7% | none |
| R1-F10 | compounds.yaml gives Cys/Met molar masses equal to Ala/Val (unused fields) | Fix values | none |
| R1-F11 | Sulfur is not balanced; sulfate-reduction cost omitted | Document | ceilings −1.3–1.6% |
| R1-F12 | D-formula needs γ per C-mol (say so); Heijnen formula returns a complex number for c > 6 (not triggered); PRIMER's electron ceiling 0.79 is the cellulase value | Fix text; add a guard | none |

## R5 — prices, wages, indices and incumbent prices

Verified: every price that enters the model was re-fetched from its primary source (EIA,
Eurostat, BLS, UN Comtrade, ECB, USDA MyMarketNews, EC sugar) and matches; every derivation in
base.yaml recomputes.

| ID | Finding | Decision | Effect |
|---|---|---|---|
| R5-1 | Incumbent price bands are nominal, compared with 2025$ costs | Fix: deflate each year with CPI-U to 2025$ | whey band $6.8–17.8 → $8.7–17.8; egg $8.2–20.1 → $10.1–22.1 (before R5-10) |
| R5-2 | EU glucose used an unsourced "75% dry solids" conversion | Fix: rebuild the EU value from sourced proxies and report the gap's sensitivity | EU gap ±$0.5/kg |
| R5-3 | Physical-limit sugar ($0.25) and tornado low ends are 2018–19$ values used as 2025$ | Fix: escalate with CPI-U | floors +2–4% |
| R5-4 | Price ranges are US-only; an EU Monte Carlo would silently draw US prices | Fix: location-keyed ranges | latent |
| R5-5 | Light-capital fermenter quotes escalated with PPI-chemicals, not CEPCI | Fix | light prices −1.3–1.6% |
| R5-6 | Steam "Humbird ratio" pairs two unrelated workbook cells | Fix: physics-based fuel ratio | negligible |
| R5-7 | EU electricity is NL, EU gas is EU27 | Fix: NL for both | +0.4% EU |
| R5-8 | EU wastewater priced as US; NL levy is per kg COD, effluent COD unknown | Document as a limitation | +0.8–5.4% EU |
| R5-9 | EU salary escalated only to 2024 | Fix: escalate to 2025 | +0.2% EU |
| R5-10 | Egg-white powder protein fraction 0.78 (grade B); USDA FoodData Central gives 0.811 (grade A) | Fix | egg band −3.8% |
| R5-11 | US electricity is the all-customer average; large users pay less | Document | US–EU gap understated |
| R5-12–14 | Values actually used (NL band IF, band I4) live only in notes; minor field and grade inconsistencies; NREL anchor uses a few non-NREL prices | Fix | ≤ 1.2 pts on the NREL anchor |

## R3 — plant: downstream, scale, capital, labour, operating costs

Verified: an independent rebuild with coefficients typed from Humbird's workbook reproduces the
base case exactly. Checked: TCI $843.13M, effective Lang factor 5.10, 113.4 staff and MSP
$29.1767. Every equipment coefficient, building cost, facility class and the 4FB capital chain
match Humbird's sheets; every 2018$ item is escalated exactly once; the operating-cost units
are right.

| ID | Finding | Decision | Effect |
|---|---|---|---|
| R3-F1 | Two-stage centrifugation (Intelligen) re-dilutes the paste with wash water, which the liquid balance omitted; membrane area was half of what the cited design needs | Fix: add the stage-2 wash to the clarified volume, process water and wastewater | +8.1% BLG, +7.4% OVA |
| R3-F2 | Diafiltration sized at the 30 L/m²/h concentration flux; the only diafiltration flux on file is 5 ± 2 L/m²/h (EVERY, OVA at 50 g/L) | Fix: separate concentration and diafiltration fluxes; diafilter at the sourced condition | +3.1% BLG, +8.4% OVA |
| R3-F3 | Fermenter cost beyond 196 m³ extrapolated with exponent 0.998, not the documented 0.89; Humbird's own fit is 0.69. "Vessel size matters little" was an artifact | Fix: graded exponent parameter above the quote table (0.69), in the tornado; revise report and memo | floors −4 to −7%; vessel swing $0.6 → ~$2/kg |
| R3-F4 | Isolate dryer fed the UF retentate volume instead of the ~20%-solids precipitate cake | Fix | OVA isolate −7.3%; Intelligen anchor +9.9% → ~+2% |
| R3-F5 | Spray-dryer cost ($2.5M at 2 t/h, exponent 0.6) hard-coded without source | Fix: parameter with grade and range; sourcing requested | ±3% BLG, ±8% OVA |
| R3-F6 | MF and dryer recoveries double-count losses already inside the 0.97 (which itself is a teaching number; see R8-m2) | Fix: physics-based paste-liquid recovery from sourced paste liquid fraction | ~−2 to −3% |
| R3-F7 | Supervisor salary factor 1.4 unused | Fix | +0.2% |
| R3-F8 | Capital costed for 30.06 fermenters, report says 31 | Fix: whole vessels | +1.5% |
| R3-F9 | Chillers sized at peak density × final volume instead of peak total heat | Fix | −1.4% |
| R3-F10–F12 | Crude branch books non-existent diafiltration water and power; wastewater double-counts dilution water; salts applied to final rather than initial medium | Fix | ≤ 0.5% each |
| R3-F13 | Hard-coded factors (wash 6 volumes, office ×1.5, staff trains N/12, peaking ×3/×2, compressor building area); light convention keeps Humbird buildings and missing capital; unused parameters; membrane price not escalated | Fix or document each | small |
| R3-open | Dryer fed 6–15% solids with no evaporator (dairy plants pre-concentrate to ~36–50%) | Sourcing requested (MVR evaporator); decide after evidence | OVA up to ~8% |

## R8 — teaching documents (PRIMER, READING, exercise A1, LITERATURE, SCOPE)

Verified: every PRIMER number reproduces (`primer_numbers.py`), ~25 page locators and the
offsets (NREL +10, Humbird +5, Intelligen +1) check out, and the A1 answer key and workbook
reproduce exactly.

| ID | Finding | Decision |
|---|---|---|
| R8-M1 | A1 Part 3 ("doubling titer does not halve cost"; floor set by yield and downstream chemistry, not scale; bridge magnitudes) contradicts the final model | Fix: scope those lessons to Intelligen's accounting at 1 kt/yr, point to the report |
| R8-m1 | A1's heat argument uses batch-average O₂ uptake; the phase-resolved growth uptake is what breaks the limit | Fix |
| R8-m2 | "Remaining 3% lost in clarification" is within rounding, and the 0.97 entered base.yaml (teaching number in the model) | Fix (see R3-F6) |
| R8-m3 | "No public BLG/OVA yield exists" should read "no measured yield"; design values exist (Behm 0.223, Intelligen 0.28, Järviö-derived 0.39) | Fix |
| R8-m4 | SCOPE's scenario definitions differ from what runs (physical limit ≠ maximum yield; academic keeps B/D/E analogues); not logged in PLAN | Fix SCOPE and log in PLAN |
| R8-m5–m7 | PRIMER ceiling assumptions, A1 per-kg-powder vs per-kg-protein bridge ($37.21, 9.8×), capital-convention framing (">10%" is really 1.7×; NREL Lang 3.1) | Fix |
| R8-m8–m13 | A1 exit criterion cannot fail on maintenance/glucose; one wrong locator; stale `data/assumptions.yaml` references; outdated status lines; LITERATURE inaccuracies; locator precision | Fix |
| R8-open | Priors and outputs were committed together, so git cannot prove the priors came first; prior 3 and the superseded prior may be mis-scored; Aro's 2 g/L OVA includes a clipped form | Fix wording and scoring; state the git limitation |

## R7 — report, memo, explorer, SI workbook, figures and top-level docs

Verified:
- **Rebuild:** fresh compiles and a full rerun reproduce the report, the figures and
  `analyses.json` (29 differences, all ≤ 1e-5 relative).
- **Numbers:** every computed number reads the right result key, and every typed number checks
  out except 0.52 (R1-F1).
- **Explorer:** its lookups match direct model runs at 8 points.
- **SI workbook:** the sheets match the results.

| ID | Finding | Decision |
|---|---|---|
| R7-C1 | "Yield and vessel size matter little" is wrong for yield. At fixed titer yield barely moves cost, but it sets the O₂ wall: 72 h ceiling 35 / 54 / 91 g/L at Y 0.20 / 0.28 / 0.40, and the BLG floor is +39% at Y 0.28. The vessel-size result was the R3-F3 extrapolation artefact | Fix: rewrite both claims; add ceiling-versus-yield to the results |
| R7-C2 | Physical-limit optima sit on grid edges; a finer search gives BLG $6.22 (−8%), light $3.27, OVA $10.95. The q_p ≤ 40 mg/g/h cap (grade D) binds at the true optimum | Fix: refined search to X_max and shorter times; report the binding constraints and a q_p-cap sensitivity |
| R7-M1 | Tornado text quotes costs of infeasible designs (titer 60 g/L, 48 h, 150 g/L cells) | Fix: truncate infeasible ends at the feasibility boundary; rank on feasible swings |
| R7-M2 | "Physics caps the titer at 54 g/L": the binding limit is Humbird's 150 mol/m³/h design cap (van 't Riet physics allows ~314; the heat cap gives 186) | Fix wording everywhere; §5.5 says 150, not 200 |
| R7-M3 | The OVA 50 g/L solubility is enforced only in the physical-limit search; the Onego 120 g/L claim shows as reachable | Fix: solubility is a hard limit in every analysis; say the claim contradicts the assumption |
| R7-M4 | Claims table breaks the report's own q_p cap (48 mg/g/h) and starts batches at 4–16% fill | Fix: apply the q_p cap and a sourced minimum initial fill |
| R7-M5 | Monte Carlo for academic OVA samples K. phaffii parameters and clips T. reesei cells to 40 g/L; deterministic values sit at the 0.5th–16th percentile; "whole distribution above $183" is false (p10) | Fix: host-specific uncertain parameters and ranges; report where each base value sits in its distribution |
| R7-M6 | Calibration agreement overstated: Intelligen glucose −28%, electricity −58%; NREL electricity −38%; the Voutilainen sugar match is by construction; costs are recorded misses | Fix wording: consistency checks, not calibration fits |
| R7-M7 | The same 42 g/L gets two costs ($22.8 industry scenario vs $18.5 claims row); the GFI 42 g/L is Hawkwood's average over private models of unspecified proteins; industry Y 0.30 is unsourced | Fix: describe GFI correctly; reconcile or unify; source or drop Y 0.30 |
| R7-M8 | Memo: light capital "undercuts whey at mid-range prices" is false (only 4 of 21 annual observations exceed $13.3) | Fix |
| R7-M9 | EU and funder claims go beyond the model (fermenters are 63% of equipment cost; capital beats siting only at 4%/20 yr; conversions not modelled) | Fix wording |
| R7-M10 | The pre-registered priors are the assistant's, cannot be verified from git, and the superseded prior is mis-scored | Fix: state who wrote them and the git limitation; re-score |
| R7-m1–m17 | Wording and number slips, grades mislabelled in text, missing references (Roels, Knoll, EVERY patent, Petrides, Carnicer and others), explorer ceiling chip ignoring yield, flag-2 points drawn as achievable, SI Accounting sheet with fixed maintenance/insurance, Liberation Labs unreferenced, the 0.15 judgment shown as the author's | Fix each |
| R7-Q6 | Does one baker's-yeast check with an assumed 33% margin justify "price-anchored"? | Keep the agreed name, but state the basis and its weakness where it is defined |

## R4 — finance, parameters, scenarios, calibration, tests

Verified:
- **Finance:** an independent DCF reproduces NREL App. B exactly ($2.1500/gal). The capital
  recovery factor, MACRS-7, the construction schedule, start-up and loss carry-forward all match.
  The unlevered MSP_DCF is within 0.2% of the independent DCF.
- **Cached results:** every cached result recomputed exactly: base, scenarios, policy, scale,
  bridge, physical limit, ceilings, required titers, claims, tornado and Monte Carlo.
- **Required titers:** each gives MSP within ±0.5% of its target and is feasible.

| ID | Finding | Decision | Effect |
|---|---|---|---|
| R4-1 | Physical-limit search grid too coarse; optima on grid edges (same as R7-C2) | Fix: refined search to X_max | floors −1 to −8% |
| R4-2 | OVA solubility is a hard limit only in the physical-limit search (same as R7-M3) | Fix: hard limit everywhere | Onego claim not reachable |
| R4-3 | NREL's $4.24/kg is per kg produced (Aspen ~580 kg/h), not per kg delivered; the anchor applied a 0.909 delivered fraction | Fix: delivered fraction 1 | NREL miss +174% → ~+149%; light +43% → ~+30% |
| R4-4 | Academic OVA Monte Carlo draws K. phaffii cell densities (mode clamped to 40 g/L) and K. phaffii maintenance (same as R7-M5) | Fix: host-specific ranges and paths; sample() refuses out-of-range modes | median $619 → ~$518 |
| R4-5 | Levered DCF omits interest during construction (NREL draws the loan over construction and pays interest) | Fix | NREL anchor +~12 points |
| R4-6 | Voutilainen "their DCF" misses their price and opex escalation and full start-up year | Fix: reproduce their conventions for that anchor (reconstruction gives 9,012 vs their 9,007 €/t) | anchor −7% |
| R4-7 | Voutilainen light row charges 1.5% maintenance on ISBL installed cost, not FCI | Fix | +4 points on that row |
| R4-8 | NREL glucose comparison mixes per-kg-delivered and per-kg-produced | Fix (with R4-3): 3.87 vs 4.17 kg/kg, −7% | wording |
| R4-9 | "Mass and energy balances agree with all three designs" overstated (electricity −38/−58%, Intelligen glucose −28%) | Fix wording | — |
| R4-10 | Monte Carlo drops draws that raise errors instead of counting them infeasible | Fix | feasible fraction −1 point |
| R4-11 | params.override depends on key order for location-keyed leaves | Fix: resolve location before applying overrides | latent |
| R4-12 | EU values outside US ranges (same as R5-4) | Fix: location-keyed ranges | latent |
| R4-13 | Finance parameters depreciation_years, construction_years, equity_frac are never read | Fix: wire or remove | — |
| R4-14 | VALIDATION says the capital convention appears in the tornado; it does not | Fix: add a capital-convention bar | — |
| R4-15 | PLAN promises correlated Monte Carlo inputs; draws are independent | Document honestly (no data to set correlations); keep the feasibility filter as the physical coupling | — |
| R4-16 | Tornado text uses infeasible ends (same as R7-M1); SI calibration sheet compares a light-convention cost with a Humbird-convention target | Fix | — |
| R4-17 | Light-capital fermenter price round-trips through two indices ($1.10M vs NREL's own $0.99M in 2007$) | Fix (with R5-5) | light −3 points |
| R4-18 | No unit tests for finance, params, scenarios; calibration bands wide enough to miss R4-3/5/8; referenced tests/test_validation.py does not exist | Fix: add unit tests, including NREL's $2.15/gal DCF | — |

## New full texts (Li 2026, Yao 2026, Aro 2023, Järviö 2021, Nielsen 2026, Shukla 2026)

Every quote was checked against a raw re-extraction: 11 of 12 match verbatim, and 1 was
reconstructed across a hyphenated line break.

| ID | Finding | Decision |
|---|---|---|
| NP-1 | Li 2026: 5.14 g/L BLG on glucose, 5 L, 24 h batch + 108 h fed-batch; cells ~112 g/L DCW (read from Fig. 6B at a 4:1 wet:dry ratio) | Academic BLG: t_prod 108 h, X_prod ~112 g/L (derived, grade D) |
| NP-2 | Yao 2026: 13.88 g/L BLG, but the production phase runs on ethanol (489 g/L wet cells) | Show as a marker and an upper variant; not costed on glucose (the model has one carbon source) |
| NP-3 | Aro 2023: OVA 2 g/L is two bands combined (full-length plus a 36 kDa clipped form); no biomass or yield in the paper | Keep 2 g/L and say it is an upper bound for full-length OVA |
| NP-4 | Järviö 2021's 2.54 kg glucose/kg protein (0.39 g/g) fails a carbon balance; it is not a strain yield | Mark the titers.csv row unusable as a yield |
| NP-5 | Nielsen 2026's ">70% carbon yield" is a relative improvement (Table 2: 100 → 173), not an absolute yield | Fix the hosts.yaml entry and every text that cites it |
| NP-6 | No public measured BLG/OVA yield on sugar exists; the academic scenario pairs academic titers with a design yield | State it; the cell density carries most of the sugar use anyway |

## R2 — fermenter transport physics and the fed-batch simulation

Verified: an independent first-principles model (RK4) reproduces the base batch within 0.6%
(W0, q_p, growth time, O₂, glucose), and a hand check of the titer ceiling gives 54 g/L at
72 h. The following all match or are correct: kLa correlation and units (Humbird Fig1.3), the
log-mean driving force with gas depletion (hand check within 1.6% of Humbird's aeration power),
the aeration objective and constraints, the liquid mass balance (glucose closes exactly), and the
production-phase integration.

| ID | Finding | Decision | Effect |
|---|---|---|---|
| R2-1 | Humbird's A.1 applies its 150 mol/m³/h cap per m³ of **cell-free liquid** (OUR = −qO₂/(W(1−φ))), about 110 per m³ of broth at 80 g/L cells; the model applies 150 per m³ of broth and cites A.1 | Fix: state the basis (per m³ of broth, the usual industrial basis, supported by Takors' >120 and Humbird's "200 about as high as it gets"); re-cite; show ceilings on A.1's basis as a sensitivity | 72 h ceiling 54 g/L (broth basis) vs ~24 g/L (A.1 basis) |
| R2-2 | New heat-throttle secant can return µ = 0 when the first step lands just past the root (one verified false failure in 60 stress draws; none in current outputs) | Fix: Illinois false position | none on current outputs |
| R2-3 | Report arithmetic: 241 mol O₂/kg is per kg delivered (218 per kg made); 7.2 kmol/m³ mixes bases (6.5); the time-averaged OUR is ~105, not 79; the wall is the production-phase q_p·X_prod at the start of production (~14.9 mg/g/h); "Intelligen 83 g/L" is derived (source says 92 at harvest) | Fix text | — |
| R2-4 | Air-rate search stops up to 1.5× short of the gas-velocity limit; the physical-limit 250 cap is silently 249 | Fix: solve the velocity limit exactly | ~0.4% on the physical limit |
| R2-5 | Aeration power taken from a max-fill table; at partial fill it is ~9% higher | Document (+0.1% MSP) | +$0.03/kg |
| R2-6 | Time-step bias (growth overshoots X_prod by ~1.2%; midpoint µ throttle) makes costs ~0.3% conservative and adds step noise | Fix: land the last growth step on X_prod | −0.3% |
| R2-7 | Draws whose growth plateaus below X_prod are dropped from the Monte Carlo (same as R4-10) | Fix | — |
| R2-8 | Hard-coded NH₃ feed strength (0.25), duplicated 460 kJ/mol literals, dead agitator code and a docstring describing an unused power model | Fix: parameters (NH₃ 30% w/w per Intelligen), one heat-per-O₂ parameter, remove dead code | −0.05% |
| R2-Q1 | No minimum working volume: batches start at 4–30% fill | Fix: sourced minimum-fill feasibility limit (sourcing requested) | ceilings at long times fall sharply |
| R2-Q2 | Intelligen's 0.28 g/g (Eq. 2) is a lumped production-phase yield with no maintenance term and 8% biomass; the model uses 0.28 for the product reaction alone and adds Tijhuis maintenance and growth. Production O₂ is 186 mol/kg vs Intelligen's 60 | Decide with the maintenance evidence: state the definition, derive the product-reaction yield consistently, use measured producing-strain maintenance | first-order for the O₂ wall |
| R2-Q3 | No product during growth, although the base (methanol-free) promoter is constitutive | Document as a simplification | — |

## R6 — process evidence, titers, parameters against evidence

Verified: 118/118 local quotes found (77 contiguous, 41 across two-column interleaving, each read by
hand); 14/14 Humbird workbook cells; 97 online entries re-fetched, 93 verbatim, 3 non-verbatim with
correct numbers, 1 misread (R6-M3); the engineering quotes gathered with a paraphrasing fetch tool
held up (33/34 verbatim). All 46 verified titer rows match their full texts. All 62 parameters in
strain, hosts, fermenter, media and dsp checked against their sources; page citations resolve.

| ID | Finding | Decision | Effect |
|---|---|---|---|
| R6-C1 | Yao 2026 (13.88 g/L BLG, K. phaffii, peer-reviewed) is the best public titer, 2.7× the Li 2026 value used | Fix: academic BLG uses Yao (ethanol-induced production costed as glucose-equivalent, flagged; per electron the two feeds cost about the same); Li 2026 (on glucose) shown alongside | academic BLG ~$188 → ~$71–81/kg |
| R6-C2 | Production-phase stoichiometry adds growth (0.01/h) and Tijhuis maintenance on top of Intelligen's lumped 0.28 g/g; the effective production-phase yield is 0.11 g/g (same as R2-Q2) | Decide with the producing-strain maintenance evidence: product-reaction yield derived from Intelligen Eq. 2, Intelligen's growth rate, measured maintenance; report the effective yield | up to −10% MSP; 72 h ceiling 54 → up to 72 g/L |
| R6-C3 | Diafiltration at the concentration flux (same as R3-F2) | Fix | +3–8% |
| R6-C4 | Academic OVA (T. reesei) grows cells at 0.01/h for 120 h, harvesting 77 g/L against the cited 20–50 g/L and ≥120 h total | Fix: no production-phase growth for that case; total batch ~133 h (Aro's sampling) | −9 to −20% |
| R6-M1 | MF flux 10 L/m²/h is a final bioburden filtration (EVERY Table 9), not primary clarification | Fix: 20 L/m²/h grade D, range 10–50 | −3 to −4% |
| R6-M2 | Glucose feed 0.5 w/w cited as a 500 g/L solution (0.42 w/w) | Document: the model tracks volume at 1 kg/L, so 0.5 gives the right feed volume for a 500 g/L solution (as R2 found); only feed mass is off, negligibly | none |
| R6-M3 | Nielsen's "carbon yield above 70%" is a relative improvement (+73% vs centre point) | Fix the evidence entry (value null) and every text citing it | none on costs |
| R6-m1 | Salts on final broth (38 kg/m³); Intelligen Table 3 implies 22.3 kg/m³ of final broth | Fix | −0.3 to −0.6% |
| R6-m2–m13 | Isolate purity 0.97 vs Intelligen's 99%; "lowest measured maintenance" is 0.0023 not 0.0035; physical_limit.yaml cites the model's own 118 mg/g/h as NREL's (honesty rule 5); NREL P/V per liquid is 2,500 W/m³; us_max has no evidence entry; several unsourced range ends; harvest densities cited for a start-of-production parameter; X0 rationale; one wrong DOI and wrong authors in hosts.yaml; 4 non-verbatim quotes; NREL page slips and an unsourced salts price; MF recovery double count | Fix each | small |

## Research pass on the placeholders (P-1 to P-13; `data/evidence/placeholders.yaml`)

A sourcing pass (57 entries, every quote read from raw text) covered the v1 grade-E
placeholders and the audit's open sourcing requests.

| ID | Parameter | Decision | Effect (base BLG unless noted) |
|---|---|---|---|
| P-1 | Membrane skid | $1,200/m² (E) → $263/m² (B: Mercier-Bouchard 2017, spiral-wound dairy MF), range 85–526. Membranes $150 → $45/m² (dairy spiral-wound elements), high 272 | the v1 values would add +16.6% now that diafiltration is costed at 5 L/m²/h |
| P-2 | Downstream building area | No source; stays E (0.5). Check: the model's buildings are 0.34 × equipment cost, against Petrides' 0.45 for enzyme plants (range 0.1–3.0) | none |
| P-3 | Laboratory area | 400 m², E → D (Humbird's 6.8 kt/yr cultured-meat plant has 441 m²) | none |
| P-4 | Antifoam | 0.5 (E) → 0.2 kg/m³ (B: Behm 2022; patent practice 0.02–0.2) | <0.1% |
| P-5 | Spent-cell disposal | $0 (E) → US $343/t dry (landfill tipping fee at 20% solids), EU $158/t (anaerobic digestion gate fee), grade C; low 0 (feed or fertiliser outlet) | +$1.20/kg (+4.1%) |
| P-6 | Construction location factor | New: EU 1.09 × US Midwest (B: IEAGHG 2018, same plants costed in NL and the US Midwest), on TCI | EU +$1.80/kg |
| P-7 | Heat removal ceiling | Stays 25 kW/m³ (D), now bracketed by sources (8–30 kW/m³ in 200–300 m³ SCP fermenters; 17 kW/m³ with coils alone; 42 claimed at pilot scale) | none |
| P-8 | OVA solubility | Intelligen's "50 g/L practical solubility" is unsourced and matches vendor QC concentrations (Sigma 40, Interchim 50 mg/mL); OVA dissolves at 200 g/L (Wang 2025), egg white is ultrafiltered to ~110 g/L OVA (Tsai 1977). No longer a hard limit; 50 g/L is kept as a sensitivity. Caveat: no data at pH 5 (the fermentation pH, near the pI) | OVA concentrate −6% (dryer feed); the OVA ceiling and physical limit are no longer capped at 50 g/L |
| P-9 | Spray dryer | $2.5M at 2 t/h, exponent 0.6 (unsourced) → $924k at 790 kg/h, exponent 0.62 (B: Yver 2012, supplier-based); range from BioSTEAM (low) and Watson Dairy Consulting (high) | −0.6% |
| P-10/11 | Evaporator and dryer feed solids | Dairy practice concentrates >60%-protein streams by membranes, not evaporators. Dryer feed: BLG 0.30 (WPC80/WPI 27–37% DM), OVA 0.23 (egg white UF), both C; the final concentration is costed at the DF flux | −0.9% BLG, −6% OVA |
| P-12 | Minimum initial fill | New feasibility limit 0.30 of vessel volume (B: Intelligen starts at 30.5%; NREL 50%) | base unaffected (39%); long, high-titer designs become infeasible |
| P-13 | Production-phase maintenance | Measured 0.00437 g/g/h (A: Rebnegger 2024, VHH-secreting K. phaffii at low growth); range 0.0023–0.0161 | see R2-Q2 below |

## Decision on R2-Q2 / R6-C2: production-phase stoichiometry

Intelligen's Eq. 2 is a lumped expression-phase stoichiometry (100 g glucose → 28 g rOVA +
8 g cells + 4 g host proteins, maintenance included). v1 used its 0.28 as the yield of the
product reaction alone and then added Tijhuis maintenance (0.0174 g/g/h) and growth at
0.01/h on top, an effective production-phase yield of 0.11. With chemostat-level maintenance
Eq. 2 is impossible: maintenance alone would use all of its glucose.

Decision (consistent with the evidence at near-zero growth, where maintenance falls about
threefold; Rebnegger 2016):
- production-phase maintenance = measured 0.00437 g/g/h (P-13); growth phase keeps Tijhuis;
- growth in production = Intelligen's own: 917 kg of cells on 8,927 kg in 72 h, 0.0014/h;
- product-reaction yield derived so the model reproduces Eq. 2: 1/Y = 100/28 − (8/28)/0.5705
  − 0.00437/0.00475 → **Y_ps = 0.465** (0.80 of the energetic ceiling); tested in
  `tests/test_model.py`;
- cell density at the start of production re-derived with Intelligen's volume balance
  (8,927 kg in ~83 m³): **107 g/L**, not the 80–83 g/L read from harvest (R6-m). The model's
  harvest density is then 94 g/L (Intelligen 92) and q_p 4.65 mg/g/h (Intelligen 4.75).

Effect: the production-phase effective yield is 0.276 (Intelligen 0.28). Base BLG moves little
(+0.1% against the v1 set, because more cells at the start of production offset the cheaper
stoichiometry), but O₂ per kg falls from 241 to 147 mol and the titer ceiling rises (see the
results). The v1 reading (Y_ps 0.28) is the low end of the yield range.

## Batch 2 implementation (2026-09-27)

Implemented: every "Fix" decision in R1–R6 that touches the model or data, P-1 to P-13 and
R2-Q2/R6-C2. The report and memo text (R7, and the report parts of R1, R2 and R4) follow in
the rebuild.

Base results, v1 → batch 2 (price-anchored capital, US Midwest, 10 kt/yr):

| Case | v1 | Batch 2 |
|---|---|---|
| BLG concentrate, MSP_CCF $/kg protein | 29.18 | 29.37 |
| OVA concentrate | 31.60 | 29.45 |
| OVA isolate | 37.80 | 35.12 |
| BLG, EU (NL) | 33.56 | 33.52 (now with the 1.09 construction factor) |
| Academic BLG | 187.7 (Li 5.14 g/L) | 64.2 (Yao 13.88 g/L, ethanol-induced, flagged); Li 5.14 g/L 164.1 |
| Academic OVA (T. reesei, 2 g/L) | 467.3 | 389.8 |
| Industry BLG (42 g/L) | 22.81 | 21.91 |

One-at-a-time effects on base BLG of reverting a batch-2 decision: membranes to v1 prices
+16.6%; no spent-cell disposal −4.1%; diafiltration at 30 L/m²/h −2.7%; v1 production
stoichiometry alone +2.3%; no centrifuge paste loss −1.9%; MF at 10 L/m²/h +1.1%; dryer feed
at 15% solids +0.9%; v1 dryer basis +0.6%; no CIP −0.7%; salts at 38 kg/m³ +0.4%.

Code and data changes: `pf_ferm` (production-phase maintenance, production-phase glucose),
`plant` (paste-model centrifugation, MF/UF/DF, dryer feed solids, whole fermenters, chillers,
supervisors, CIP, location factor, P/O-based ceiling, q_p ceiling, crude branch), `params`
(location-keyed ranges, order-independent overrides, strict sampling), `scenarios` (feasibility
limits, tornado truncation and capital bar, host-specific Monte Carlo counting errors as
infeasible, refined physical-limit search with binding constraints), calibration cases (R4-3,
R4-6, R4-7, R4-17, R6-m12), evidence corrections (R6-m10/m11, NP-5), titers.csv (new full
texts), and 22 new model tests.
