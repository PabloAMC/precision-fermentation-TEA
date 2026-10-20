# Audit R16: the metabolic floor and the animals' feed bill (content added 2026-10-05)

Scope: only the three commits of 2026-10-05 (97e59df, 0821824, 4e7ad27; `git diff 90f2908..HEAD`):
- src/pftea/floor.py
- benchmarks.feed_bills and benchmarks.yaml `feed_bills`
- data/evidence/feed.yaml (58 entries) and kinetic.yaml (header, REVIEW NOTE)
- the q_p_max source text in base.yaml
- run_analyses.s_floor, the Fig. 12 block of make_figures.py (Figure 13 in the report) and the SI sheet Floor_vs_feed
- report §4.10 "Feedstock against feed" (sec-floor), the "Feedstock" answer bullet, and the two changed Limitations bullets
- the memo bullet "Sugar is not the problem"

Mode: read-only. No tracked file was touched, and run_analyses, explorer_grid and the build scripts were not run.

What I did run:
- scratch model calls (`floor.metabolic_floor` with parameter overrides)
- the three new tests (`pytest -k "floor or feed_bills"`: 3 passed)
- `pdftotext` of the memo

Scratch files: .preview/r16_check.py (it recomputes the arithmetic) and .preview/r16_head_analyses.json (HEAD copy, for comparison).

Note: during the audit the working tree showed uncommitted edits by another session to benchmarks.yaml (titer-marker
labels), fig1, references/DOWNLOADS.md and results/analyses.json. These are outside scope. The `floor` section of
analyses.json is identical to HEAD's, so every check below holds for the committed state.

References:
- "rep NNNN" = line of `.preview/rep.txt`
- "typ NNNN" = line of `report/pf_tea_report.typ`
- "memo NN" = line of `.preview/memo.txt`

## Numbers checked (all match)

**Floor (analyses.json `floor.products.blg.us_midwest.floor`; report rep 1636–1648)**
- Y* = 0.5635 g/g. Substrate 1.7747 kg → "1.77". NH3 0.192 → "0.19". O2 11.70 mol → "11.7". Heat 6.79 MJ → "6.8".
- Cost: glucose 0.710 + NH3 0.117 + power 0.049 = $0.876 → "$0.88" ("$0.71 of it glucose"). EU $1.282 → "$1.28".
- "Within a few per cent": the other food proteins' input cost runs 0.844 (ovd) to 0.882 (cas), within −3.7%/+0.7% of BLG. ✓
- P_O2 = 17.1, P_heat = 13.25 → "at most 13", "cooling binds first". ✓
- Base case productivity: 30.0 g/L / 109.1 h = 0.275 → "0.27". ✓
- Base glucose 10.28 kg (5.79× the floor), cells 3.50 kg, glucose $4.112 = 19.4% of $21.17. ✓
- Physical-limit case: 2.72 kg glucose ($0.842), 1.53× the floor. ✓
- s_floor's msp equals R.base / R.base_eu for all 7 products and both locations (e.g. BLG 21.174 / 24.323). ✓
- Mass balance: substrate = 1/Y* (tested), NH3 = 0.192 kg ≈ 16% N × 17/14. ✓
- Electron balance closes (tested). O2 agrees with my hand electron balance (≈11.4 mol at γ_p ≈ 4.27). ✓

**Animals (analyses.json `floor.animals`; rep 1653–1691)**
- 21.5 kg feed/kg protein → "22". 19.9 → "20".
- Feed bills: US $6.68/$4.69/$5.80 (milk 6.62 × 0.876) → "$6.7, $4.7, $5.8". ✓
- Ratios to $0.710: 6.6–9.4 → "7–9×". 18.0 kg glucose-equivalent vs 1.8. ✓
- Premium 1.2335 → "23%". 1 − 0.876 → "12%". Shares 0.742/0.695/0.42 → "74%, 70%, 42%". ✓
- Farm-gate cost: 9.003/6.748/13.807 → "$9.0, $6.7, $13.8". ✓
- EU: €31.1 vs €24.1. €39.62 → "€39.6". FCR 1.63 vs 1.83. Feed $8.87/$7.88. Totals $12.91/$11.59. Milk $4.88. ✓
- Glucose $0.61 vs $0.40. Floor $1.083 → "$1.08". Base glucose $6.27 → "$6.3". ✓
- "Other": $17.06, 17.18, 17.25, 17.84, 29.70 → "$17.1, $17.2, $17.3, $17.8, $29.7". Farm $2.06–8.01 → "$2–$8". ✓
- Answers bullet (rep 1845–1847) and memo bullet (memo 18–19): 1.8 kg, $0.71, $4.7–$6.7, $4.1, $17, $2–$8. ✓
- PLAN.md entry: 1.77 kg, $0.88, $0.71, $1.28, ~13, 0.27, $4.1, $4.7–6.7, $7.9–8.9, $17 vs $2–8, 7–9×. ✓

**feed.yaml arithmetic, recomputed independently (.preview/r16_check.py)**

Broiler, US:
- Feed per kg live: 1.830 / 1.653 / 1.923.
- Edible protein per kg live: 0.0777 / 0.0922 / mean 0.0849 / 0.0957.
- Feed per kg protein: 21.54 / 17.27 / 24.75.
- NASS proxy: 2025 228.8 USD/st = 0.2522 $/kg; 2024 0.2511; 2022 0.3685; 2020 0.2701.
- USD per kg protein: 5.42 / 4.34 / 9.15.
- Delivered: 6.683 / 4.616 / 11.421.

Premium:
- 2017 proxy 222.1 USD/t vs 270.6 delivered → 1.218.
- 2013: 355.5 vs 377.9 → 1.063.
- 2015: 234.6 vs 292.8 → 1.248.
- Mean of 2015 and 2017 → 1.2335.

Layer, US:
- 2.204 / 2.112 / 2.297 kg/kg. EIC 2.324 kg/kg.
- 19.95 / 19.12 / 21.31 kg/kg protein.
- USD (EIC formula): 4.691 (2025), 4.354 (2020), 6.99 (2022).

Dairy, US:
- ERS 9.82 → 6.621; DMC 10.03 → 6.762; DMC 8.87 → 5.98; DMC 14.83 → 9.998.
- Allocation 21.02/23.99 = 0.876.
- F·a/s = 13.81, equal to ERS's direct costs listed × 0.876 = 13.80, a good consistency check.

EU:
- Broiler: FCR mean 1.585, live weight 2.433, 1.755 kg/kg live (low FR 1.707, high ES 1.810); 20.67 kg/kg protein; USD 8.864 / 6.248 / 11.571.
- Eurostat means: 39.62 / 31.30 / 47.16.
- Layer: 2.228 / 2.171 / 2.378 kg/kg; USD 7.884 / 6.300 / 10.362; Eurostat mean 36.12.
- Milk: 5.637 / 6.296 / 4.262; beef allocation 0.865.

Feed shares:
- EU broiler by country: NL 0.676, DE 0.672, FR 0.640, IT 0.713, ES 0.708, PL 0.713; mean 0.687.
- US broiler 0.742. US layer 0.695. EU layer 0.680.
- Breeder males: 453/15,220 = 0.0298; 566/15,220 = 0.0372.

Price per MJ:
- US delivered broiler feed 2.39 c/MJ; glucose 2.57.
- EU feed 3.30; EU glucose 3.92.

**Sources against the saved texts**
- WUR 2018-116 Tables 3.4/3.5 (USA: feed 24.1 €/100 kg, FCR 1.83, live weight 2,700 g, feed 44.1 and total 64.5 c/kg live). ✓
- WUR 2023-006 Tables 4.1/4.2 (EU/USA feed 30.0/24.8, FCR 2.00/1.96, 400/430 eggs, 61.9/60.0 g, feed 60.1/48.5, total 98.5/77.6). ✓
- WUR ECC memo (NL feed 56.5, total 92.4). ✓
- EMB 2024 (13.77, 3.26, −7.56; milk price 48.42). ✓
- ERS milk.csv 2025 (feed 9.82, operating 13.75, costs listed 23.36, gross value 23.99, milk 21.02, cattle 2.25, other income 0.72). ✓
- Eurostat JSON (DE/FR/NL broiler 2024 42.0/38.07/38.8; NL 2022 50.3; FR 2019 29.61; layer DE/NL 2024 36.85/31.65, ES sacks 39.85; NL 2019 25.57). ✓
- ECB 2019/2022/2023/2024 rates (prices.yaml). ✓
- NCC 2020/2025 rows. ✓
- Ross PS 36.7 kg / 152.2 chicks and the male-feed footnote. ✓
- Hutjens Table 2, 7 CFR 1430.411, Withers and Swift abstracts (16.0, 15.0). ✓

A mechanical quote match against references/text/feed/ flags nine entries. All nine are records (JSON, CSV, XML) or
composites of table rows, and each is present in layout form.

**Data-file hygiene**
- All 58 feed.yaml and 39 kinetic.yaml entries carry a source and a grade.
- Every `Derived (mine)` entry is graded D.
- benchmarks.yaml reads every number by key; there are no literals.
- base.yaml bracket check: 0.25 × 74 = 18.5 and 0.25 × 163 = 40.7 → "~18–41" ✓; 40/16 = 2.5 ✓; Withers 16.0 and Swift 15.0 → "15–16" ✓.

## HIGH

None. Nothing here changes a headline conclusion. Glucose stays about a fifth of the base cost, and the plant
dominates under every reading below.

## MEDIUM

### M1. "PF already spends no more on feedstock than the animals" holds only if the whole feed bill is charged to protein. For milk and eggs, any physical or value allocation reverses it.

**Where:**
- §4.10 "What it means": rep 1683–1684, typ 2034–2035.
- Answers "Feedstock": rep 1846–1847, typ 2225–2226.
- Memo "Sugar is not the problem": memo 18–19, memo.typ 77.
- PLAN.md result line.

**Evidence:**
- The animal bills charge 100% of the feed to the protein. Milk's feed also makes its fat and lactose, and the egg's
  feed also makes its yolk fat.
- On energy content (my estimate from textbook energy factors, unsourced; not for the data files):
  - Milk is about 3.3% protein, 3.9–4.3% fat and 4.8% lactose (milk_egg.yaml l.74 gives 3.9/3.4/4.8). Protein is
    about 20% of milk's energy.
  - A whole egg (12.6% protein, ~9.5% fat) puts protein at about 35–40% of its energy.
- Charged that way, milk protein's feed is about $1.2–2.5/kg (US, after the beef credit) and egg protein's about
  $1.7–1.9/kg. Both are below PF's $4.1 of glucose. Only chicken meat (lean, ~3% fat) stays above.
- The report's first caution ("its protein comes in a whole food with fat and other value") names the issue. It does
  not say that the feedstock comparison depends on it, and the memo and the Answers bullet carry no qualifier.

**Fix:**
- §4.10, old: "At the base case PF already spends no more on feedstock than the animals: $4.1 of glucose per kg of BLG
  against $4.7–$6.7 of feed."
  New: "Charging the animal's whole feed bill to its protein, PF at the base case spends no more on feedstock than the
  animals: $4.1 of glucose per kg of BLG against $4.7–$6.7 of feed. Milk's and eggs' feed also makes their fat and
  lactose. Charged by energy content, their protein's share would fall below PF's glucose. Only chicken meat, which is
  nearly all protein, stays above."
- Answers: "The base case already spends no more on glucose ($4.1) than the animals spend on feed when all of it is
  charged to protein; …"
- Memo: "Base-case glucose ($4.1/kg BLG) is about a fifth of its cost and comparable to animal feed per kg of protein
  ($4.7–$6.7 with all the feed charged to protein, US 2025, our derivation); the gap is the plant ($17/kg against $2–$8
  of non-feed cost at the farm gate)." This keeps the robust half of the claim ("about a fifth"; $0.71 floor).
- Optional: add an allocated column (by energy or component value) to feed_bills. That needs sourced composition and
  component-price entries; do not use my numbers.

### M2. The whiskers in Figure 13 pair extremes that never occur together. For US milk the shown range is about 2.5× the observed one.

**Where:**
- benchmarks.feed_bills (`total_low = flo·a/shi`, `total_high = fhi·a/slo`).
- feed.yaml `derived_us_broiler_delivered_feed_usd_per_edible_protein` low/high.
- Fig. 12 code and the figure's footnote.

**Evidence:**
- Feed price and feed share move together: a dear-feed year has a high share. Pairing the lowest feed bill (DMC 2020,
  $5.98) with the highest share (2022, 0.54), and the reverse, gives a US milk farm cost of $9.7–20.9.
- ERS's own total costs listed for 2020–2025, × 0.876 per kg protein, give $13.1–16.1 (2020 13.13, 2022 16.14, 2025
  13.80). Pairing year by year is possible, and for milk the total can be read directly.
- US broiler feed has the same problem. The low case (4.62) multiplies a 2024 feed price by the 2013 premium (1.063).
  2013 was a drought year: dear ingredients and a thin premium. The high case (11.42) multiplies a 2022 price by the
  2015 premium (1.248, a cheap-ingredient year). The premium behaves like a roughly fixed adder ($22–58/t), not a
  ratio. As an adder (~$50/t) the 2022 bill would be about 24.8 × 0.419 ≈ 10.4, not 11.4.
- The footnote "whiskers: other years' feed prices and the feed-share range" also omits that the broiler whisker spans
  FCR (Ross target vs NCC 2020), edible yield (meat + skin vs old dissection) and premium years.

**Fix:**
- Dairy: compute total by year (ERS costs listed × milk share) and take the min and max.
- Poultry: pair each feed year with its own share where one exists. Otherwise hold the share at its central value and
  report the share range separately.
- Premium: either apply a USD/t adder (mean 2015/2017 delivered − proxy) or pair premium years with matching price
  years.
- Footnote, new: "whiskers: the range over feed-price years, feed conversion, edible yield and feed share, each taken
  at its own year where available".

### M3. "No cell or fermenter can do better" overstates the floor. It is a ceiling for the assumed host P/O ratio and textbook biosynthetic costs, not for any cell.

**Where:**
- rep 1640–1641, typ 1986–1987.
- Answers "PF's least possible feedstock" (rep 1845).
- Fig. 13 footnote: "the least glucose, ammonia and aeration power any process needs".
- floor.py docstring line 1 ("that any process needs").

**Evidence:**
- Y* pays ATP at K. phaffii's P/O = 1.48. That figure is a genome-scale-model constraint (base.yaml l.52, "no measured
  P/O found"), not a physical limit.
- My scratch runs:
  - At P/O 2.5 the floor falls from 1.775 to 1.659 kg glucose (−6.5%).
  - With Stouthamer's amino-acid cost at its low end (0) it is 1.753.
  - With both, 1.645 (−7.3%).
  - At the high end (1.2 ATP per residue) it is 1.841.
- So a host with a better P/O could beat the stated floor by about 7%. The excluded items (transport, secretion,
  turnover) only push the other way, so "lower bound on use" is true for this host's energetics, not for any cell.

**Fix:**
- §4.10, old: "No cell or fermenter can do better, because the floor leaves out transport, secretion, folding and
  protein turnover, all of which only add to it."
  New: "No K. phaffii process can do better: the floor leaves out transport, secretion, folding and protein turnover,
  all of which only add to it. A host that made more ATP per O2 than the P/O we assume (1.48) could beat it by up to
  about 7%."
- Answers: "PF's least feedstock (at the energetic ceiling) is 1.8 kg …".
- Footnote: "the least glucose, ammonia and aeration power at the energetic ceiling".
- floor.py docstring: "that a process needs at the host's energetic ceiling".

### M4. "13 kg/m³/h … the capital floor is not physical but biological, set by how fast cells secrete" mixes two bounds. The model's own ceilings give a tighter physical-plus-catalyst bound, and at the best case O₂ transfer does bind.

**Where:** rep 1643–1645, typ 1988–1991.

**Evidence:**
- P_max assumes product without catalyst. With the model's own ceilings, q_p ≤ 40 mg/g/h and X ≤ X_max = 150 g/L
  (base.yaml l.28). The cells needed for 13 kg/m³/h (≥ 330 g/L at 40 mg/g/h) cannot exist. Cells alone cap production
  at 0.040 × 150 = 6 kg/m³/h, before their own maintenance O₂.
- The best case actually reached (physical limit, BLG) makes 140 g/L in 109 h = 1.3 kg/m³/h. Its binding constraints
  include "O2 transfer" (analyses.json `physical_limit.blg/humbird`). The vessel limit does bind, through the O₂ the
  cells burn.
- "Set by how fast cells secrete" is right for the base case (q_p 4.7 mg/g/h). It is not the whole story at the best
  case.
- P_max also scales with the grade-D cooling limit (25 kW/m³; range 15–40 gives 7.9–17.1 kg/m³/h).

**Fix:**
- Old: "…could make at most 13 kg of protein per m³ per hour (cooling binds first). The base case makes 0.27 kg/m³/h
  over its batch: the capital floor is not physical but biological, set by how fast cells secrete."
- New: "…could make at most 13 kg of protein per m³ per hour (cooling binds first; 8–17 over our cooling range). Real
  cells cannot approach it: at our secretion ceiling (40 mg/g/h) and packing limit (150 g/L) they would make at most
  6, and their own respiration takes most of the O₂. The physical-limit case reaches 1.3 kg/m³/h, the base case 0.27.
  So the capital floor is set by the cells, how fast they secrete and how much O₂ they burn staying alive, not by the
  vessel."
- Typst: P_heat at the heat bounds needs either an s_floor output or two extra fields from floor.py. Do not type the
  numbers.

### M5. The feed-comparison Limitations bullet says the bills are "priced as corn and soybean meal". That holds for one of the five.

**Where:** rep 2003–2007, typ 2397–2400.

**Evidence:** Only the US broiler bill is a corn + soybean proxy (× premium). The other four are priced differently:
- US eggs: the EIC delivered-layer-feed formula (corn, SBM, calcium, other, milling, transport).
- US milk: ERS total feed costs (purchased + home-grown + grazed, mostly forage).
- EU broilers and layers: Eurostat complete-feed prices.
- EU milk: bought-in feed + fodder inputs.

**Fix:**
- Old: "…and Wageningen costings, priced as corn and soybean meal (broilers raised by a delivered-feed premium), with
  milk credited for its beef only;"
- New: "…and Wageningen costings: US broiler feed as corn and soybeans raised by a delivered-feed premium, US layer
  feed by the Egg Industry Center's delivered-feed formula, EU poultry feed at Eurostat complete-feed prices, and milk
  at USDA and EU farm-account feed costs; milk is credited for its beef, all of the feed is charged to protein (M1),"

### M6. "EU birds and hens convert feed as well as or better than US ones" is wrong for hens.

**Where:** rep 1659–1660, typ 2023–2025.

**Evidence:**
- eu_layer_cost_wur_2021 gives FCR 2.00 for the EU and 1.96 for the US (kg feed per kg eggs). The US also gets more
  eggs per hen (430 vs 400).
- In 2017 the figures were 2.02 and 1.98 (eu_layer_cost_wur_2017).
- Per kg of protein the EU layer feed is 20.2 kg vs US 19.9 (Hy-Line basis).
- The broiler comparison (1.63 vs 1.83) is confounded by weight, as the text says. Per kg protein the derived values
  are EU 20.7 vs US 21.5 kg, i.e. similar.

**Fix:** "EU broilers convert feed about as well as US ones (1.63 against 1.83 kg per kg live weight in 2017, at a
lighter bird); EU hens slightly worse (2.00 against 1.96 kg per kg of eggs, Wageningen 2021). So the EU bills are higher
mainly because the feed is dearer: …"

## LOW

**L1. The farm "other" cost (and so the "$2–$8") is low at its bottom end because of the F/s method.**
- Non-feed costs do not scale with feed prices, but C = F/s makes them do so.
- US eggs: EIC's own 2023 survey gives non-feed (incl. pullet non-feed) 85.98 − 52.77 = 33.2 c/dozen = $4.2/kg protein,
  against the model's $2.06.
- US broilers: WUR 2017 non-feed 16.7 € c/kg live = $2.2/kg protein in 2017 dollars, roughly $2.8–2.9 in 2025 with
  US CPI (my estimate), against $2.32.
- The conclusion ($17 vs a few dollars) stands.
- Fix: cross-check "other" against an absolute non-feed cost (WUR/EIC, inflated) and state "$2–$8 (the method may
  understate the low end)", or compute other = absolute non-feed cost.

**L2. "Credited for cull cows and calves (12% of revenue)" includes 3% "other income".**
- ERS 2025: cattle 2.25 (9.4%) and other income 0.72 (3.0%) of 23.99.
- Fix: say "cattle and other income (12% of the farm's revenue)", or allocate with milk/(milk + cattle) = 0.903 and
  keep the wording.
- The feed.yaml note and the derived_us_dairy_milk_share_of_value_ers note need the same fix.

**L3. Grade of `dairy_feed_share_of_cost_ers` (A) for a computed ratio.**
- 9.82/23.36 is my arithmetic on grade-A data, and every other derived share is graded D.
- The figure's grade line shows "share A".
- Fix: grade D, or document that ratios of one A table keep A.

**L4. EUR → USD at the 2024 rate for EU feed against PF EU costs in 2025 dollars.**
- EU feed bills use 1.0824 (2024). Converted at 1.13 (2025) they would be 4% higher.
- The docstring of feed_bills says "(2025, the model's money year)".
- Fix: state "2024 USD" for the EU bills in the docstring and the figure footnote, or convert at the money-year rate.

**L5. "About two US cents per MJ for both".**
- Glucose at $0.40 is 2.6 c/MJ, and US delivered broiler feed is 2.4. In the EU the figures are 3.9 and 3.3.
- The claim "no dearer" holds. "About two cents" is generous for glucose, and the evidence covers broiler feed only,
  not dairy forage.
- Fix: "(2–3 US cents per MJ for both; broiler feed, `broiler_feed_me_ross_specs`)".

**L6. kinetic.yaml: the REVIEW NOTE is right, but the flawed text is still in the file.**
- The note correctly says 163 mg/g/h counts the r0 reserve and that the "89 at μ = 0.0014" line is unsupported.
- These still say otherwise: honesty note 2 ("~130–160 mg/g DCW/h for K. phaffii"; "~0.3x of the translational
  ceiling"), `derived_kphaffii_translational_throughput_at_mu` (value 160, its 89 line and the "~45/44/44 …
  coincidentally right where the model's 40 sits" sentence), and `recommendation_qp_max_kinetic_upper_bound` ("the
  one genuinely hard statement is that q_p can never exceed ~160").
- Honesty note 3 says "Three entries" and lists four.
- Fix: set the derived entry to value 74, high 163 (reserve recruited), delete the μ = 0.0014 line and the
  "coincidentally" sentence, and align notes 2–3.

**L7. The 15–16 mg/g/h frontier is stated as "measured for any protein" (Limitations, rep 1953–1955; base.yaml q_p_max source).**
- The evidence is a search of continuous-culture compilations, abstracts and a few fed-batches, with no industrial
  Bacillus or A. niger process data (proprietary).
- Swift 1998 is a pH auxostat, not a chemostat.
- Fix: "the highest specific secretion rate we found published for any protein (15–16 mg/g/h, A. niger glucoamylase,
  chemostat and pH auxostat)".
- In base.yaml, add "the 18–41 bracket is at μ = 0.2/h; at the production phase's near-zero growth the growth law does
  not bound q_p".

**L8. Figure 13 (fig12_feed_vs_floor.png).**
- (a) The US broiler whisker starts at $6.2, inside the feed segment ($6.7), so it reads as a feed range. Draw whiskers
  above the bar, or say in the footnote that they span the total.
- (b) "PF casein" should be "PF β-casein", and "alpha-lac" should be "α-lac" (SHORT labels; other figures share them).
- (c) The first x tick reads "$0.0" and the others "$10", "$20". Use a 0-decimal formatter.
- (d) The footnote's "any process needs" (see M3) and whisker wording (see M2).
- (e) PLAN.md and the commit message call it "Fig. 12". It is Figure 13 in the report (file fig12_…).

**L9. Typed number in figure and report code.**
- Food proteins are selected by `msp < 60` (make_figures.py Fig. 12 block, and typ `FOODP`). This is a data-dependent
  threshold: a scenario that pushed α-lac above $60 would silently drop it from Fig. 13 and from the "$17.1 … $29.7"
  list.
- Fix: select by an explicit list (e.g. `[p for p in PRODS if p not in ("lf", "alb")]`, or a `food_proteins` key in
  benchmarks.yaml).

**L10. floor.py hardcodes molar masses.**
- `M_NH3 = 17.031` and `M_SUBSTRATE = {...}` duplicate what thermo provides (`th.get(name).mw`, `th.ATOM`).
- The test repeats 180.156.
- These are physical constants, so they are only marginally a rule violation, but a second source of truth.
- Fix: read them from thermo.

**L11. floor.py docstring item 4.**
- "Respiration releases ~460 kJ per mol O2, so the two limits come together": the product reaction releases 581 kJ
  per mol O2 (6.79 MJ / 11.7 mol), because anabolism is exothermic as well.
- The 6.8 MJ rests on the grade-D biomass-analogy enthalpy of the protein (product.py item 2). A rough
  bomb-calorimetry check gives anything from ~5.5 to ~8.5 MJ.
- Fix: "the product reaction releases ~580 kJ per mol O2 (more than respiration's ~460, since making the protein also
  releases heat; grade D enthalpy), so cooling binds slightly before O2 transfer".

**L12. SI sheet Floor_vs_feed omits what the figure shows.**
- No total_low/high, allocation, year, grades or evidence keys, so the whiskers cannot be reproduced from the SI.
- Fix: add those columns.

**L13. Small scope gaps in feed.yaml.**
- The feed.yaml header still says "Not read by the model yet (src/pftea/floor.py computes the PF side)" and "~1.78 kg
  glucose".
- The US broiler bill uses female parent feed only (males +0.6%, stated).
- Hy-Line pullet feed runs to 17 weeks, while WUR's hen is bought at 20 weeks. Weeks 17–20 (~1.5 kg/hen, my estimate)
  are uncounted in the EU bills and both layer shares (~+3% on layer feed).
- The "parent and pullet feed included" wording in benchmarks.yaml and the figure is fine as an approximation.
- Fix: update the header, and add "to 17 weeks" to the pullet wording.

**L14. "Most of the difference is the yeast".**
- True: about 7.9 of the 8.5 kg excess goes to growth and maintenance.
- The 11% DSP loss (recovery 0.896) also adds glucose and is not named.
- Fix, optional: "…; the product is made below the ceiling yield, and 10% of it is lost downstream (@sec-stoich)".

## Checked and correct (logic)

**Floor code and physics**
- floor.py: reaction stoichiometry and per-kg scaling are right.
- O2 species lookup handles aq/g.
- E_O2 = (compressor + agitator + heat × rt_refrig)/O2 is the plant's own expression (plant.py l.382): 48.5 kWh/kmol.
  Its cost is $0.049, "a few cents" as stated. Using the base batch's heat per O2 slightly understates chilling at the
  floor (581 vs ~460–500 kJ/mol). This is immaterial.
- OTR basis: otr_cap 200 mol/m³ of cell-free liquid. The base batch's effective 128.7 = 200 × 0.643 per m³ of broth.
  With no cells, the floor's 200 per m³ of broth is the right upper bound, as the docstring says.
- The base 0.27 is per m³ of end broth over t_total (not the cycle), so it is like for like.
- P_heat ignores agitation heat, which only loosens the bound.

**feed_bills**
- Formula total = alloc × feed / share and other = total − feed are correct (tested).
- The allocation is applied to the feed before dividing, so feed, total and other are all on milk's share. Consistent.

**Scope of the shares**
- WUR's total cost includes the day-old chick (or 20-week hen) price, which already contains parent (pullet) feed.
  Adding that feed to the numerator only makes the share and the total consistent.
- Parent feed per US chick (0.397 kg × 24.1 € = 9.6 € c) is 35% of the 27 € c chick price. Plausible.
- The ERS share and allocation are both whole-enterprise. ✓

**Report text and code**
- The EU milk "lower bound, not comparable, no farm cost" logic is right and is applied in the code (no feed_share key).
- "Four cautions" are four.
- @sec-floor and @sec-stoich resolve. The section numbering shift (cheese 4.11, heme 4.12) uses labels only.
- s_floor uses the same base design point as R.base, both locations.
- The memo is still one page.
