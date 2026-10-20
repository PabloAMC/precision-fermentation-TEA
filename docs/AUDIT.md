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

## Batch 3 (2026-09-27): milk and egg equivalents; lactoferrin contrast case

Both were requested after the audit (Pablo, 2026-09-26).

**Milk and egg equivalents** (`benchmarks.equivalents`, report section on equivalents;
evidence in `data/evidence/milk_egg.yaml`): a litre of milk holds 3.3 g BLG and 33.7 g of
protein; a large egg holds 1.96 g ovalbumin and 3.64 g of egg-white protein. Milk and egg
prices (US farm, EU raw milk, US retail; US wholesale and retail eggs) are converted per unit
and deflated to 2025$ like the incumbent bands. Dividing a unit's price by its protein gives
the price at which PF protein would cost as much as the natural source per gram of protein:
US farm milk $14–19/kg protein (2015–2025), eggs $26–85/kg egg-white protein (wholesale). These
are upper bounds on the protein's value, because fat, lactose and yolk carry part of the price,
and whey is a by-product.

**Lactoferrin** (`data/pf/scenarios/lactoferrin.yaml`, evidence `data/evidence/lactoferrin.yaml`):
bovine lactoferrin in K. phaffii without methanol (FDA GRN 1219, 1284), 250 t/yr, 90% LF powder,
MF → cation exchange → UF/DF → spray dryer. New model step: cation-exchange capture (plant.py
block c'), with binding capacity, buffers, salt and ethanol from the EVERY patent (B), resin
price (Petrides, B) and industrial lactoferrin resin life (>1,000 cycles, A). Two new
guesses (E): cycle time (sets resin volume only) and column hardware per litre of resin.
Salt and ethanol prices from Comext 2025 (A). Results at 10 g/L (Intelligen's design titer):
$216/kg with price-anchored capital, $134/kg with design-report capital, against dairy
lactoferrin at $200–1,500/kg (grade C, 2013–2025). At the best public methanol-free titer
(2.8 g/L, porcine LF, Yen 2024) $531/$283. Resin life is the largest downstream lever (125 cycles:
$364/kg).

## Finding during the v2 rebuild (2026-09-27): what sets the titer ceiling

With the minimum starting volume added (R2-Q1) and the production stoichiometry corrected, the base
titer ceiling is no longer set by O₂ transfer: at every production time the limit that fails just
above it is the minimum starting volume. A higher titer needs more sugar feed; with a 50 wt%
feed and a broth that must end at 80% of the vessel, the batch would have to start below 30%.
Ceilings at 36/72/120 h: 81/74/65 g/L (they fall with time because maintenance keeps consuming
feed). Relaxing either design choice (20% start, or a 65% feed) lifts the 72 h ceiling to ~125 g/L,
where the secretion ceiling or O₂ (on Humbird's cell-free basis) binds. Decision: report the
ceiling as a volume ceiling set by design choices, with these sensitivities (`ceiling_limits` in
`results/analyses.json`, report Table 7); v1's "O₂ wall" wording is withdrawn everywhere. The
teaching documents were updated to v2 results.


## Phase F AI pre-review (2026-09-27): what changed in v2.1

Four simulated expert reviewers (AI) read v2 (commit 5cbf9bc); their reviews are verbatim in
`docs/ai-review/` and every comment is answered in `docs/REVIEW.md`. Each comment was re-checked
against the code, the data or the source before acting. Model and data changes, in order of effect
on the base BLG price (29.37 → 21.17 \$/kg):

| Change | Why (review) | Evidence |
|---|---|---|
| Fermenters priced from NREL 2011's vendor quote (industrial enzyme fermenter, internal coils, agitator) in both conventions; Humbird's aseptic ACCE curve kept as a structural high case (`capital.fermenter_quote`) | BE-1, HM-2, SC-3: the aseptic cell-culture reactor (ASME BPE, 316L, full vacuum; Humbird text Table 3.3) is 2.9× the vendor quote and 3.2× the bubble column of the yeast anchor ($779k per 199 m³, 2018$) | Humbird p.37 and Table 3.3; A.1 Equip!BT6; NREL 2011 App. A; with it our capital matches Voutilainen's FCI (+1.8%) and Intelligen's cost (−3.5%) |
| Missing-equipment allowance 10% → 20% (range 10–20%) | BE-4: the list omits CIP and feed tanks, filter housings, sugar storage, inactivation, packing and effluent pretreatment | Humbird A.1 uses 20% on its abbreviated list |
| O₂ cap 150 per m³ of broth → 200 per m³ of cell-free liquid (range 150–250) | HM-3, BE-7: 150 is Humbird's bubble-column limit; his air-sparged STR value is ~200, on the cell-free basis of his Eq. 4.2 | Humbird p.28, p.49, p.91; 129 per m³ of broth at 107 g/L cells |
| Chillers and compressors sized on the coincident peak of staggered batches | BE-6: v2 summed every fermenter's peak (72.6 MW against a coincident 27.3 MW) | model arithmetic; `plant._coincident_peak`, tested |
| CIP chemicals not charged again under Humbird's rule | HM-8, BE-3 | Humbird p.46: maintenance "is assumed to include CIP chemicals" |
| Membrane skid price treated as installed (backed out to a purchase cost) | BE-8 | Mercier-Bouchard 2017 row "Installation capital investment"; our P-1 note "probably installed" |
| Spent-cell disposal fees converted at the model's 15% paste solids (US $458, EU $211 per t dry) | BE-9 | the paste model (30% dry wet cells × 50% extracellular liquid) |
| Feed concentrations in g/L: glucose 500 g/L (not "50 wt%"; range 500–600), ammonia 268 g/L | FS-1, BE-2, HM-1 | Intelligen p.6; Shemesh 2024 "60% (w/v)"; GESTIS density of 30% ammonia |
| Energetic ceiling adds amino-acid synthesis (0.29 ATP/residue) and sulfate assimilation (3 ATP + 8 e⁻ per S); physical-limit yield 0.55 → 0.535 | FS-2, SC-2 | Stouthamer 1973 as recomputed by Martin et al. 2025 (PMC7617979) |
| Physical-limit case uses a 600 g/L feed; shown at secretion ceilings 5–120 mg/g/h; secretion-ceiling range 5–40 | FS-3, SC-2, HM-1 | Intelligen's design rate 4.75 mg/g/h is the low end |
| Inoculum 5 → 3 g/L (5% of a 60 g/L seed), then 0.88 g/L (5% of 17.6 g/L seed broth) | FS-11, follow-up L | Intelligen's lactoferrin flowsheet; the growth phase is then 37 h against Intelligen's 36 h |
| CEX cycle time computed from load and buffer column volumes (2.1 h, was 3.5 h), at 20 column volumes per hour | BE-12, follow-up L | load CVs = capacity / feed concentration; flow from Intelligen's design (500 cm/h, 25 cm bed) |
| Lactoferrin price band deflated to 2025$; Intelligen's own costs shown as costs of production ($299 UF/DF only, $441 with cation exchange, 2025$) against ours ($113, $159) and reconciled by category | SC-6, follow-up L | Intelligen report Tables 2–5; the $292 GFI cites is case a per kg lactoferrin |
| Monte Carlo: failure reasons, input means and all-draw percentiles recorded; academic BLG cells 40–60 g/L; industry titer 24–54 g/L, grade C | SC-8 | GFI 2025 Table 2 and text |
| Claims priced at their own production time; the shortest-time cost kept as a labelled best case | SC-7 | Behm 2022: 120 h |
| New analyses: cheapest design at base biology by secretion ceiling; required titers with implied q_p; ceiling rows for 35/40/50% starts, 80 g/L cells and a 600 g/L feed; convention gap decomposed; base sensitivities; A.1 under other capital stacks | SC-1, SC-4, SC-3, BE-3, BE-5 | `results/analyses.json` |

Text changes (report, memo, explorer, README, REVIEW): the feed label, the ceiling's causes (SC-4),
secretion as the gate for $10/kg (SC-1), "best case" instead of "floor" (SC-2), what the yeast anchor
supports (SC-3, HM-2), the published-cost ratios (SC-5, BE-13), the milk-and-egg bias (SC-10), the
whey-egg comparison (SC-9), the bridge's infeasible first steps (SC-11), the priors' scoring (SC-12),
heat per mol O₂ (FS-10, HM-9), the compressor effect (HM-7), and the directions of the model's
simplifications (FS-6, FS-12, HM-4).

**New evidence found while checking FS-4.** Rebnegger et al. 2024, the source of the production-phase
maintenance, measured secretion falling as growth slowed and settling "roughly fivefold lower" than
the chemostat trend (0.019 mg/g/h at doubling times of two months), which the authors partly
attribute to the promoter. The base production phase (Intelligen's design: 4.7 mg/g/h at near-zero
growth) therefore assumes secretion decoupled from growth, which no public BLG or OVA data test. It is
now the report's lead caveat and the first question for funders. The v2 evidence note said secretion
"collapses" and that decoupling "does NOT work"; that overstated the paper and was corrected.

**Follow-up reading, same day** (details in REVIEW.md). Compressor: the PF model now uses the
textbook adiabatic formula; Humbird's workbook formula puts k = 1.4 where (k−1)/k belongs and is kept
only in the A.1 port (+$0.02/kg). The aeration search no longer fails at high DO setpoints (a
latent bug; no base result changed). Seed density 17.6 g/L and inoculum 0.88 g/L from Intelligen's
lactoferrin flowsheet. Cation-exchange flow 20 column volumes per hour (Intelligen) instead of a
guess. New evidence entries for Heyland 2010 (an intracellular product: never cite it for secretion),
Looser 2015, Humbird 2017 and 2021 aeration and the Intelligen lactoferrin report; three lactoferrin
evidence notes corrected against that report; a malformed YAML entry (Prielhofer) found and fixed, and
a data-integrity test added (`tests/test_data.py`); a misattributed heat-per-O₂ citation corrected
(von Stockar → Maskow et al. 2010).

**Corrections to earlier audit statements.** R3's "the 4FB capital chain match Humbird's sheets"
needs a qualification (HM-5): the model applies the ISBL installation factor to the fermenters,
whereas Humbird's chain enters bioreactors at their installed ACCE cost (Table14 bioreactor install
factor 1). With the aseptic quote the two agree within about 10% ($7.5M against his $6.8M per 200 m³,
2018$); with vendor-quote vessels the factor is the right treatment. R6-M2's feed fix was only
"documented"; the report still said "50 wt%" (FS-1).

**Not changed, with reasons** (details in REVIEW.md): the 9% fixed-cost rule (Humbird's; his yeast
workbook needs it to reach the market band), the diafiltration flux (the reviewer's 10–20 L/m²/h needs
a source not on disk), a titer-dependent k_La (no source), a wider T. reesei maintenance range (no
measured value), start-up, working capital and failed batches (not in the anchored method; listed as
exclusions), and the base feed (Intelligen's 500 g/L kept; 600 g/L is the sensitivity).

## v3 audit (2026-10-01/02, night): ovomucoid, β-casein and five products on an equal footing

Three independent AI reviewers audited v3 read-only on a working copy, under the same rule (every
finding backed by a computation, quote or code line): R9 the β-casein product and its `acid`
route; R10 the five products' data, scenarios and benchmarks; R11 the report, memo, figures,
explorer and SI workbook. Full reviews were kept with the session; this log records each finding
of substance and the decision. Effects are on the base β-casein MSP unless noted.

Verified independently: the ovomucoid and β-casein formulas (C840H1306N240O292S20, 20,080 Da;
C1080H1692N268O310S6, 23,583 Da), the acid-dose arithmetic (49.4 mol H+/m3 → 5.69 kg 85% H3PO4,
base.yaml rounds to 5.65), the heater steam, the water balance to the dryer, the recovery chain,
the casein per-lb price conversion ($10.13/kg protein in 2025), the ovomucoid purity derivation
(0.72–0.81 dry, mean 0.76), every titer marker against titers.csv, every results key the report
reads for all five products, and the explorer's JavaScript in node for every product and unit.

| ID | Finding | Decision | Effect |
|---|---|---|---|
| R9-1 | Precipitation recovery fixed at 0.95 whatever the casein concentration; the permeate is 9.7 g/L at base and 0.3–0.85 g/L in the academic cases, against 26 g/L in milk | Fix: the permeate is ultrafiltered (no diafiltration) to skim milk's casein concentration before precipitating (`dsp.acid_precip_feed_g_L`, D), so the dairy recovery and wash data apply; acid and heat now scale with the smaller feed | −2.9% ($22.71 → $22.05); academic −5% |
| R9-2 | Acid dose per m3 of diluted permeate at milk's buffer capacity; source claimed ammonia buffers and a pH 5.5 start | Fix with R9-1 (dose per m3 of the concentrated feed); source corrected (pH 6.8 start; protein takes 14–17 H+ per molecule; ammonia does not buffer at pH 4–7) | in R9-1 |
| R9-3 | H3PO4 costs several times more per mol H+ than H2SO4/HCl, and adds phosphorus to the effluent | Document (no sulfuric/hydrochloric acid price on file); stated as a lever in the source and limitations | −$0.45–0.50/kg if switched (reviewer's estimate) |
| R9-4 | "Acidify at ~82 °C" is an OCR misreading (the text then heats to 40–45 °C) | Fix: low bound 45 °C, note in base.yaml | −$0.02 |
| R9-5, R9-6 | Report said Formo needed heat for full precipitation and called pH 4 the isoelectric point | Fix text: only Standing Ovation heated; pH 4 is below the recombinant pI (~5.5) | none |
| R9-7 | Dairy-practice values applied to PF casein graded A | Fix: graded C, as the dairy values for BLG | none |
| R9-8, R9-13 | Wash high bound is one concurrent wash; value at the bottom of 11–15 L/kg | Fix: value 13 L/kg; note on the high bound | +0.2% |
| R9-11 | 90% heat recovery on a 90 °C slurry optimistic | Fix: low bound 0.50 (E) | range only |
| R9-12 | The model makes sodium caseinate; Formo sells acid casein | Document as a design choice | −1.6% if dried as acid casein |
| R9-14 | Purity 0.90 below GRN 1312's batches and spec minimum on a dry basis | Fix: 0.925 (0.91–0.94), derived from the batches | −0.7% |
| R10-1 | Academic production times subtracted ~23–30 h of growth; the model's growth phase is now 37–38 h, so batches ran longer than their sources | Fix: OVA 110 → 95 h, lactoferrin 114 → 107 h, lactoferrin base 90 → 83 h, ovomucoid patent 103 h; convention stated in academic.yaml | academic OVA −7.5%, academic LF −2.6%, base LF −0.1% |
| R10-2 | Ovomucoid dryer-feed range used EVERY's 5% feed as its low end, OVA's does not; P-8 misdescribed | Fix: range 0.20–0.30 as OVA's; EVERY's 5% feed stated as for OVA | ovomucoid tornado bar −90% |
| R10-3 | SCOPE.md defines `academic` as peer-reviewed full-text titers; the ovomucoid and casein academic cases were patent examples | Fix: academic ovomucoid = Kim 2025 (0.93 g/L, abstract only, flagged), academic casein = Choi 1996 (1.0 g/L, intracellular, flagged); the patent examples become variants `ovd_patent` and `cas_patent` | academic ovd $24 → $613; academic cas $198 → $590 |
| R10-4 | "Methanol co-feed" stated for EVERY's Example 9; the source does not say | Fix: removed | none |
| R10-5 | The Eden Brew UF/DF variant keeps a 6% purity that is physically impossible at 30 g/L (hundreds of g/L of non-protein solids) | Fix text: the comparison with precipitation holds only at low titer; the variant is an upper bound | none on base |
| R10-6 | Academic Monte Carlo keeps the wide cell-density range for ovd, cas and lf (feasible shares 0.40–0.65), BLG's was narrowed on evidence | Document: no product-specific cell-density data | none |
| R10-7 | Kim 2025 called "BEST VERIFIED" though abstract-only | Fix wording | none |
| R10-8 | Physical-limit yield is 0.89 of ovomucoid's ceiling, not stated | Fix comment | none |
| R10-9 | The milk equivalent's casein target was all casein, not β-casein | Fix: 9.2 g/L β-casein | target-per-litre only |
| R11-1 | Report did not compile (MKT used before definition) | Fix | none |
| R11-2, R11-7, R11-8 | Three comparison claims did not hold: the casein levers "move the base little" (recovery moves it up to +38%); ovomucoid "the exception" (still 1.1–2.4× its band); "the route matters most for casein" (lactoferrin's route effect is as large) | Fix text | none |
| R11-3, R11-4, R11-5 | Ovomucoid is not "the second" egg-white protein; GRN 1219 is ≥80% protein; Choi labels stale | Fix | none |
| R11-6 | Semicolons after inserted values swallowed by Typst in six sentences | Fix (`\;`) | none |
| R11-9 to R11-11 | Explorer: one base point (30 g/L, 72 h) for every product; no grid/product check; missing reference rows | Fix: per-product base point (lactoferrin 10 g/L, 83 h; the grid includes every product's base point), a hard check, the missing rows | none |
| R11-12, R11-13, R11-14 | SI workbook BLG-only sheets and old title; ovomucoid evidence missing; ~19 references missing | Fix | none |
| R11-15, R11-16 | Ovomucoid left out of several passages; Fig. 11 labels overlapped | Fix | none |
| R11-30 | `--only physical_limit` deleted the demonstrated-secretion entries | Fix | none |

Not changed (documented): the decanters pooled across duties (R9-9, +0.65%), uncosted small heat
duties (R9-10, < +$0.05), Beck's untraceable 3.2 g/L ovomucoid row kept at grade B as a
secondary report (R10-15), and the minor equal-footing gaps of R10-18 (no ovomucoid bridge
variant: the bridge varies base.yaml directly, so it could not carry ovomucoid's own purity).

### Follow-up (2026-10-02 morning): full texts of Chezan 2026 and Kim 2025, and fixes found unapplied

- Chezan et al. 2026 (full text): recombinant β-casein is least soluble at pH 4.5, like milk β-casein
  (22.45% vs 20.67% left dissolved in a dilute unheated assay); at pH 4 half stays dissolved. Decision:
  the route targets pH 4.5; `dsp.acid_precip_recovery` keeps 0.95 (now better supported: at pH 4.5 the
  recombinant protein precipitates as the native one does), with the assay's 0.78 as the low end
  (was a derived 0.67). The abstract-based entry is marked superseded in casein.yaml.
- Kim et al. 2025 (full text): 0.929 g/L after 60 h in a methanol-free glycerol fed-batch (2.5 L,
  176 g/L cells). Decision: the academic ovomucoid case is now verified (no abstract-only exception);
  production time 23 h (60 h less the model's growth phase).
- Found while checking: the report's casein methods text still carried R9-5/R9-6 (Formo "needed heat",
  "no membrane concentration") and R9-16/R9-17 (viscosity threshold, phosphorylation wording), logged
  as fixed above but not yet applied to that passage. Now applied.

## v4 (2026-10-02): independent review of the method against the state of the art

Pablo asked whether this is "the best possible model for this ... no artificial complexity, but SOTA or
close". An AI reviewer read the code, data and report and the published PF, recombinant-protein and
cultivated-meat TEAs (Humbird 2021, BioSTEAM-based work, Intelligen SuperPro models, GFI Europe/ADL 2025,
Voutilainen, Järviö, NREL). Its report: [`docs/ai-review/sota_review.md`](ai-review/sota_review.md). Verdict: at or
above the published state of the art for a public multi-protein screening TEA (its P ~0.85 that no
structural change moves the commodity base cases by >10%); conventions (design-report capital −22%,
aseptic vessels +46% on BLG) and strain data dominate. Each gap and the decision:

| # | Gap (reviewer) | Decision | Effect |
|---|---|---|---|
| G1 | Methanol costed but missing from the O2 and heat balance; matters for albumin (all high titers methanol-induced) | **Done.** Production phase blends glucose and methanol reactions (`strain.methanol_frac_prod`); methanol anabolism takes no CO2 (all carbon from methanol, surplus electrons to O2: Heijnen; a first implementation that fixed CO2 gave a >1 g/g ceiling and was corrected before any result used it); yield on methanol = the glucose yield's share of the energetic ceiling with 2 x P/O ATP per methanol (D); maintenance on methanol from Dietzsch 2011 (0.016, A) scaled to near-zero growth (0.0050, D), matching Tomas-Gamisans 2018's NGAM converted at 2.96 ATP/methanol (0.0048). Tests: carbon and electron balances at f = 0, 0.5, 1; no CO2 fixation | Base cases unchanged (f = 0). BLG base with methanol induction +12%. Methanol-induced academic cases (lactoferrin Lv 2023, beta-casein Choi 1996, albumin) now costed on methanol |
| G2 | Vessel size fixed at 200 m3 even for small plants (whole vessels) | **Done.** `scenarios.size_fermenter`: cheapest feasible of 50/100/150/200 m3 up to the 200 m3 cap, on each product's base case; scale curve re-sizes per output; explorer grid keeps the base plant | Commodity plants unchanged (200 m3; 500 m3 would be ~5% cheaper, kept as a sensitivity because 200 m3 is near PF practice). Lactoferrin 100 m3 (as Intelligen), $177.7 -> $167.8/kg base |
| G3 | Secretion decoupled from growth (q_p = beta) | **Not done.** An optional alpha defaulting to 0 changes no result; the growth dependence is stated in the report (Rebnegger 2024, Looser 2015, Prielhofer 2018) | — |
| G4 | No global sensitivity measure | **Done.** Spearman rank correlations over feasible Monte Carlo draws (report table, SI sheet MonteCarlo_rank) | Titer leads (rho -0.80 for industry BLG); sum of rho^2 ~1, as expected for independent inputs |
| G5 | First-of-a-kind penalty promised in SCOPE but not implemented | **Scope corrected.** No sourced premium on file (RAND blocks scripted downloads; GFI Europe 2025 gives none). SCOPE and PLAN now exclude it until RAND R-2569 is read (DOWNLOADS P7) | — |
| G6 | Chromatography is one column | **Superseded by R12-H1:** albumin's base now has a capture column plus an anion-exchange polish (`dsp.polish_columns`); capture-only is the optimistic variant | — |
| — | "Not worth it": mechanistic chromatography, CFD/viscosity-corrected kLa, genome-scale models, continuous operation, Sobol indices, rebuilding in SuperPro/BioSTEAM | Agreed | — |

Albumin evidence pass (AI research agent; main session spot-checked identity, formula, column data,
prices and specs; formula C2936H4590N786O889S41 reproduced independently): `data/evidence/albumin.yaml`
(52 entries), 9 titer rows. Reference titles in the report were checked against the evidence files and
Crossref after the first draft had some from memory (Zhu 2021, Delta patents: corrected).

### R12 (2026-10-02): AI audit of the v4 model changes and the albumin data

Independent reviewer, read-only, with computations (report: [`docs/ai-review/audit_R12.md`](ai-review/audit_R12.md)). Methanol physics
checked and fine (balances close, no CO2 fixed, maintenance conversion dimensionally right, heat signs, blend
only in production, Y_ps on methanol below both ceilings); sizing side effects and cache fine; every albumin
source value matches its source (Comtrade and 1.13 g/L recomputed). Findings and decisions:

| # | Finding | Decision |
|---|---|---|
| H1 | One CEX capture reaching >=96% has no support (the >96% Pichia results used dye affinity; the patent's affinity step removes the 45 kDa fragment, antigens and pigment) | **Fixed.** Base = the patent's minimal claimed train, CEX then AEX polish (US 6,638,740: AEX loaded 30 +/- 10 g/L, "approximately 110%" monomer yield -> recovery 1.0), via `dsp.polish_columns` on the existing column arithmetic. Albumin base $143 -> ~$216/kg; capture-only kept as `alb_capture_only` (optimistic) |
| H2 | Resin life 1,000 cycles (whey lactoferrin) is the favourable end for pigmented yeast broth | **Stated, not changed** (no albumin-specific lifetime exists; the base keeps the one industrial measurement, as for lactoferrin). Report shows the 125-cycle case beside the base and calls the base the favourable end |
| M1 | Vessel tornado bar is one-sided where sizing chose 100 m3 | **Fixed.** `scenarios.design_choices` skips it in the tornado |
| M2 | Methanol uptake about 2x low; the x0.31 near-zero scaling (D) | **Kept**, with the independent check (Tomas-Gamisans NGAM -> 0.0048 g/g/h) and the Zhu 2021 comparison stated in the report (model's methanol per kg made well below the 58 g/g fed) |
| M3 | Protease loss during the pH-4.5 hold not modelled | **Limitation**; recovery low end 0.40 covers it |
| M4 | Intelligen OVA anchor silently lost its methanol inducer cost | **Fixed.** `media.methanol_inducer_kg_per_kg_product` (cost only, as in v3) |
| L1 | Methanol yield ceiling leaves out the ATP of methanol assimilation (~+$0.7) | Limitation (stated) |
| L2 | Neat methanol in the volume balance by volume | Not changed (consistent with the feed convention; ~+$0.7) |
| L3 | Acetate note wrong by 30x | **Fixed** note (~$1/kg at the NaCl price) |
| L4 | Patent step volumes are maxima; eluate 6.5 not 8.5 CV | Limitation (conservative) |
| L5 | Load-conductivity limit not checked (~$2-3) | Limitation |
| L6 | Spearman rho is noise for constant inputs | **Fixed** (None when an input does not vary) |
| L7 | Base-case variants re-size the vessel | **Documented** in the sizing note |
| L8 | Recovery and step tables from different patent examples | Limitation |

Also on 2026-10-02 (Pablo's downloads): Zhu 2021 full text (the 17.47 g/L is per litre of supernatant; whole
broth 8.74 g/L is now the academic titer; membranes alone bounded at 77% albumin; capture recovery high end
0.86 measured) and RAND R-2569 (OCR'd; pioneer capital 1/0.78 = 1.28x as a separate sensitivity, never in the
base; start-up performance 72% recorded, not modelled).

### R13 (2026-10-02): AI audit of the compiled v4 report and memo

More than 60 numbers checked against results/analyses.json: all match (albumin, pioneer, methanol, Spearman,
tornado, scale; all 21 cells of the per-kg-cultivated-meat table); prose claims that follow numbers hold.
Fixes applied: albumin's two-column route in every caption and sentence (H2); three semicolons swallowed by
Typst after a function call, in the report and memo (H3); the missing evidence entry for the polish column,
hsa_delta_aex_polish, and the products.yaml route note (H4); Zhu titer markers placed on the whole-broth basis
(H1, `factor` in benchmarks titer markers); resin life for albumin graded D (borrowed from whey lactoferrin)
and the polish inputs sampled in the Monte Carlo (M2, M6); the pioneer factor stated as the reciprocal of
RAND's mean ratio, with the mean overrun ~1.36 beside it, 'conservative' dropped, resin first fill noted (M4);
the methanol-maintenance check reworded (M5); 'favourable end' limited to resin life and purification (M1);
scale-section clarifications (M3); Spearman noise floor stated (M6); route-figure labels and rounding (M7);
references sorted; low-severity wording. Report: [`docs/ai-review/audit_R13.md`](ai-review/audit_R13.md).

### R14 (2026-10-02): AI audit of the α-lactalbumin, rennet-cheese casein and heme data and logic

Read-only audit of the additions (formulas, evidence, scenario values, s_cheese/s_heme, titers.csv rows). Verified:
the four formulas and sequences, and every number the main session relies on against the local full texts. Fixes:
- H1: κ-casein alone on the pH-4.5 acid route was unsupported by its own evidence entry. Now two cases bracket its
  unknown recovery: co-precipitated with α-s1 (acid route, 78%, E) and its own cation-exchange column on lactoferrin's
  column data (D); the report shows both.
- H2: GFI Europe's α-lac prices ($15, $123) are per kg of ingredient at 60% and 95% α-lac (their p.33 arithmetic):
  restated per kg of α-lac, $25–129 (derived); FMI's $31–86 (basis unknown) dropped from the band; targets 25/60/130.
- M1: κ share 0.19 (0.167–0.25, grade B, New Culture's recombinant blends); Antuma's plateau is 19–26% κ, not 15–19%.
- M2: the 4.14 mg/L κ point sat below the model's secretion search floor (it simulated 7.4 mg/L): removed from the grid
  and quoted; infeasible points are filtered before interpolation.
- M3: scenarios.blend_titer_needed checks that cost falls with titer (tested); α-s1 baseline per κ share; the
  industry titer read from industry.yaml.
- M4: supernatant titers (α-lac Wang 2025; LegH Chen 2025, Shao 2022) converted to whole broth with the model's cell
  volume (×0.643 at 107 g/L dry cells, D), as albumin's were in R12.
- M5: the Impossible Burger retail price (no verifiable quote) removed from the heme scenario.
- M6: the heme note is an estimate, not a bound; the signs of its omissions are stated.
- Low: α-lac purity derivation (0.855 at the spec minimum, 0.90 typical); LegH purity 0.43 (batch mean); hemin coverage
  "at most" 41%; unused_paths no longer hides cas1's own dryer leaf (tested); cas1.yaml evidence pointer; marker label.
  Not changed: four evidence quotes over 40 words (L9) and scale_L conventions in the new titers.csv rows (L10).
Report: [`docs/ai-review/audit_R14_data.md`](ai-review/audit_R14_data.md).

### R15 (2026-10-03): AI audit of the compiled report's new content (α-lac, rennet-cheese casein, heme)

58 numbers checked against results/analyses.json: all match; every new citation has a matching reference entry; no
Typst defects. No HIGH findings. Fixes: GFI Europe's two α-lac market sizes are one $462 M market priced two ways, in
tonnes of ingredient, so the physical-limit cap is ~19 kt/yr of α-lac (31.8 kt at ~60%), not 31.8 kt (M1); the κ
requirement now names its route everywhere (co-precipitated: ~α-s1's design titer; own column: none up to 42 g/L) (M2);
"about four orders of magnitude" (M3); α-lac solubility stated consistently (calcium-bound form soluble pH 2–9; unfolds
in culture below pH 5.5) (M4); a stale limitation on the old $15 price (M5); the Q6 α-lac scale sentence (M6); the heme
conclusion stated as $/kg of analogue ex works and % of retail beef, not "a small part" (M7); α-lac titer basis
(supernatant vs broth) consistent (M8); low-severity fixes to figure footnotes and labels, the Wang 2021 reference (title,
DOI), a Panchanawaporn 2026 evidence entry, Chen 2025's author list, and ten clarity rewrites. Report:
[`docs/ai-review/audit_R15.md`](ai-review/audit_R15.md).

### R16 (2026-10-05): AI audit of the metabolic floor and the animals' feed bill

Read-only audit of floor.py, benchmarks.feed_bills, data/evidence/feed.yaml (every derived chain recomputed; quotes matched
against the saved texts and the Eurostat JSON), kinetic.yaml's review note, s_floor, Fig. 13 (fig12_feed_vs_floor.png), the SI
sheet, the report section, its Answers and Limitations bullets and the memo bullet. Every new number matched
results/analyses.json. No HIGH findings. Fixes:
- M1: "PF spends no more on feedstock than the animals" holds only with all the feed charged to protein; milk's and eggs' feed
  also makes fat and lactose. The report, Answers, memo and figure now say so; the robust part (glucose is 19% of PF's cost) leads.
  An energy- or value-allocated column is not built (no sourced composition prices).
- M2: whiskers paired extremes that never co-occur. Farm-cost ranges now hold the feed share at its central value, and US milk
  uses year-paired ERS costs ($14.1-17.6, was $9.7-20.9). The US broiler delivered-feed premium is now an adder (~$53/t,
  2015-2017), not a ratio paired with other years' prices: US broiler feed $6.57 (5.27-10.48), was $6.68 (4.62-11.42).
- M3: "no cell can do better" is now "no K. phaffii process": the floor rests on the host's P/O (1.48, a model value).
- M4: the 13 kg/m3/h vessel bound is set beside what cells could make (q_p,max x X_max = 6) and the physical-limit case (1.3);
  the capital floor is set by the cells (secretion and O2 for maintenance), not by the vessel. Cooling-range bounds computed.
- M5: the Limitations bullet names each pricing basis. M6: EU hens convert feed slightly worse than US hens (2.00 vs 1.96).
- Low: non-feed farm costs may be understated (EIC 2023: $4.2/kg egg protein vs our $2.1) (L1); milk credited by milk/(milk +
  cattle), 0.903, not milk/gross value (L2); grade A of the ERS feed share documented (L3); EU bills stated in 2024 dollars (L4);
  "2-3 cents per MJ" for broiler feed (L5); kinetic.yaml's derivation corrected to its own review note (L6); "the highest we
  found published" (L7); figure whiskers above the bars, beta-casein and alpha-lactalbumin labels, axis format, footnote (L8);
  food proteins from an explicit list, feed_bills.food_products (L9); molar masses from thermo (L10); floor.py docstring heat
  per O2 (L11); SI sheet ranges, keys and grades (L12); feed.yaml header and the 17-week pullet scope (L13); the 10% downstream
  loss named (L14).
Also: titer check. 43 of 134 titers.csv rows are unverified; none is used in a base case or headline scenario. Four uses (the
alb_zhu2018 variant and three Fig. 3 markers: Liu 2026, Hu 2025, Zhu 2018) rest on paywalled papers, now labelled "abstract
only" and listed first in references/DOWNLOADS.md. Report: [`docs/ai-review/audit_R16.md`](ai-review/audit_R16.md).

### R17 (2026-10-06): AI cold read of the whole v4.1 report and memo

A sceptical reader went through the whole report and memo, not one section. About 120 numbers were checked against
results/analyses.json; all matched. No HIGH findings. Fixes:
- M1: the vessel bound over the cooling range is capped by O2 transfer (8-17 kg/m3/h, not 8-21; floor.p_max_range_kg_m3_h).
- M2: the industry case (42 g/L in a 72 h production phase) now states the secretion it needs, ~7 mg/g/h, about three times
  the best demonstrated, in the summary, results, answers, funders section and memo.
- M3: the secretion-ceiling evidence reconciled: "below 1" is K. phaffii only; 15-16 mg/g/h is the highest *measured*
  rate; cellulase processes imply 5-20 at assumed cell densities.
- M4: the Q2 answer says the column, not productivity, leads for lactoferrin and albumin.
- M5: lactoferrin's 10 g/L is Intelligen's methanol-induced design, costed on glucose; a methanol variant (lf_methanol,
  $177 vs $168/kg) and the best methanol-free titer ($413) are now quoted; "the size of its market" corrected.
- Low: nine results, not eight (L1); version labels v4.1, question table, priors header, memo caveat, SCOPE alpha-lac plant
  (L2); the Intelligen comparison's sign (L3); summary point 9 in dollars (L4); albumin resin arithmetic read from the
  parameters (L6); the routes figure's stars captioned as costs of production (L7); bridge title to one decimal (L8);
  uncited references removed and the two Wang 2025 papers told apart (L11); a glossary box for policy readers (L12);
  typos (L13). Not changed: the unquoted spent-cells sensitivity (L5), marker-label overlaps in the cost-vs-titer figure
  (L9) and typed reference numbers in make_figures.py labels (L10). Report: [`docs/ai-review/audit_R17.md`](ai-review/audit_R17.md).
