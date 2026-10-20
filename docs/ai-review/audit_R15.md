# Audit R15: the compiled report's α-lactalbumin, rennet-cheese and heme content

Scope: only the content added in v4-continued. That covers α-lac wherever it appears, §4.10 (sec-cheese), §4.11
(sec-heme), summary points 7–8, the memo's new bullet and column, the new references, and the α-lac panels of
fig1/fig3/fig9/fig10.

Mode: read-only. No repo file was touched, and run_analyses / explorer_grid were not run. I made one scratch model
call (`sc.physical_limit("alac", {...}, fast=True)`) to size M1. It wrote no files.

References used below:
- PDF text lines are lines of `.preview/rep.txt` ("rep NNN").
- Source lines are lines of `report/pf_tea_report.typ` ("typ NNN").
- Figure numbers are the report's. Mapping: fig10_price_ladder = Figure 1, fig1_cost_vs_titer = Figure 3,
  fig3_required_titer = Figure 8, fig6_scale = Figure 10, fig9_routes = Figure 12.

## Numbers checked against results/analyses.json (58 spot checks, all match)

I found no number in the new content that disagrees with analyses.json. Every value below was checked at the
rounding the report uses.

**α-lac base case**
- Base cost $33.81 → $33.8. Design-report capital $24.98 → $25.0.
- 8 × 100 m³ vessels (W_end 80 m³). Total capital investment $89M.
- Table 5 rows:
  - capital charge 12.96, maintenance 3.56, insurance 4.45, glucose 4.11, labour 4.74, disposal 1.60, electricity 0.84.
  - media, ammonia and DSP chemicals 0.64 (0.325 + 0.314).
  - gas, steam, water and membranes 0.91 (0.28 + 0.08 + 0.55).
  - $28.91 per kg of powder.
  - 10.3 kg glucose, 9.8 kWh, 13 MJ, 3.5 kg cells, 37.8 staff per kt/yr.
- At 10 kt/yr: $21.17 → $21.2.
- Purity sweep: 0.70 → $33.97 ($34.0) and 0.96 → $33.78 ($33.8).
- Isolate route +$7.56 → +$7.6. EU siting +$3.94 → +$3.9.
- Aseptic vessels $43.68 → $43.7. Pioneer plant $39.73 → $39.7.

**α-lac scenarios**
- Academic case: $1,848 ($1,427 with design-report capital) on 650 fermenters, at a titer of 0.386 g/L.
- 1848/129 = 14.3 → "14×". 20/0.6 = 33.3 → "33×".
- Industry case: $28.22 ($20.77).
- Physical limit: $4.63 ($3.64) at 83 g/L cells, 88 h and 140 g/L. Binding limits: O2 transfer and minimum initial
  fill. The q_p 2.1 case costs $25.08.
- Required titer at 72 h: $25 needs 53.2 g/L, $60 needs 12.81 g/L and $130 needs 5.38 g/L, against a ceiling of
  69.96 g/L. Table 9 shows 53/13/5/70.
- Tornado: titer $24.2–37.4, capital convention $20.8–28.2, aseptic vessels $28.2–35.6.
- Monte Carlo: median $30.0, p10–p90 $27.0–35.4, 47% of draws feasible.
- Rank correlations: titer ρ = −0.77, production time +0.32, equipment cost index +0.29.
- "Titer first for 5 of the 7 proteins" holds.
- Scale curve: $114 at 100 t/yr, $27.8 at 1 kt/yr and $15.8 at 10 kt/yr.

**Cheese (§4.10)**
- κ share 0.19 (0.167–0.25).
- κ co-precipitated: $2,888, 724, 366, 152, 80.1, 44.0, 33.4 and 26.2.
- κ by column: $2,923, 764, 404, 187, 116, 79.7, 67.8 and 60.6.
- Blend with co-precipitated κ: $567, 156, 87.6, 47.0, 33.3, 26.4, 24.4 and 23.0.
- Blend with κ by column: $573, 163, 94.8, 53.6, 40.1, 33.2, 31.0 and 29.6.
- αs1 alone: $22.30 on 8,100 t/yr and $22.06 on 10 kt/yr. With design-report capital $17.15; at 42 g/L $17.08.
- αs1 academic case $522. αs1 patent case $237.
- 567/22.3 = 25.4 and 573/22.3 = 25.7 → "25–26×". 1 + 0.1/0.19 = 1.53.
- κ titer needed: 28.1, 29.1 and 29.2 g/L across the κ shares → "about 29 (28–29)". On its own column: none up to
  42 g/L.
- κ reagent price $1,080/g. 30/0.25 = 120 → "over 100×".

**Heme (§4.11)**
- Chen: $242.7 at 150 t/yr and $172.6 at 1 kt/yr. Shao: $372.4 and $290.2. Base design point: $91.7 and $35.4.
- Whole-broth titers: Chen 3.86 g/L (6.0 × 0.643) and Shao 2.25 g/L.
- Cost in use: 0.0045 × 242.7 = $1.09; range $0.61–1.94. 1.09/15.26 = 7.1% → "7%". 0.0045 × 35.39 = $0.16.

## HIGH

None. Nothing here changes a headline conclusion.

## MEDIUM

### M1. The two α-lac "market sizes" are one $462 M market priced two ways, and they are in kg of ingredient, not kg of α-lac.

**Where:**
- Table 1 caption: rep 156, typ 341.
- §2.1: rep 325–327, typ 468–469.
- Scenarios: rep 773, typ 982–983.
- Table 12 caption and Q4 text: rep 1340 and 1344, typ 1605–1614.
- Discussion Q4: typ 2110.
- Memo table note: memo.typ 118.
- data/pf/scenarios/physical_limit.yaml:33.

**Evidence:**
- alac.yaml:519–524 (`alac_market_price_gfieurope2025`) says GFI's two rows repeat the same $462 M value. They are
  "alternative cuts, not additive".
- alac.yaml:832 says the same. R14-H2 established that GFI's prices are per kg of ingredient at 60% and 95% α-lac.
  The tonnages come from the same rows ($462 M ÷ price), so they are ingredient tonnages too:
  - 31,828 t of a ~60% ingredient ≈ 19.1 kt of α-lac.
  - 3,740 t of a 95% ingredient ≈ 3.55 kt of α-lac.
- The report instead says "about a quarter of the high-purity α-lac market (3.7 kt/yr) and 3% of the food-grade one
  (32 kt/yr)". It caps the physical limit at "the food-grade α-lac market, 31.8 kt/yr" of α-lac.

**Effect (my scratch runs, fast search):**
- The physical limit at 31,828 t gives $4.65, which reproduces the $4.63.
- At 19,097 t it gives $5.16, about +$0.5 (+11%).
- It still sits far below the $25–129 band, so the conclusions stand. The 1 kt base becomes about 28% and 5% of the
  two volumes.

**Fix:**
- §2.1, old: "about a quarter of the high-purity α-lac market (3.7 kt/yr) and 3% of the food-grade one (32 kt/yr;
  GFI Europe 2025, C)".
  New: "small next to the α-lac market: GFI Europe (2025, C) value it at $462 M a year, which is 3.7 kt/yr of
  95%-pure isolate at the high-purity price, or 32 kt/yr of a ~60% ingredient (about 19 kt of α-lac) at the
  food-grade price. These are two readings of one market, not two markets."
- Physical limit: set physical_limit.yaml `alac: plant.annual_target_protein_t: 19097` (31,828 × 0.60, derived, C/D).
  Reword every "its food-grade market, 31.8 kt/yr" as "the whole α-lac market at the food-grade price, about 19 kt/yr
  of α-lac".
- If you keep 31.8 kt, say in each place that it is ingredient tonnage, so it overstates the α-lac volume by about
  1.7×.

### M2. "κ must reach roughly αs1's design titer" is true only for the co-precipitation route. The summary drops that qualifier.

**Where:**
- Summary point 8: rep 104–106, typ 287–288.
- Discussion "Notes": rep (Discussion) typ 2126.
- Memo bullet: memo.typ 102.

**Evidence:** `kappa_titer_for_10pct.kap_cex` is None for all three κ shares. On its own column, κ costs $60.6 even
at 42 g/L, against the 1.53 × 22.3 = $34.1 allowance. §4.10 says so ("on its own column no titer up to 42 g/L is
enough"). The summary, Discussion and memo state the requirement without saying which route it assumes.

**Fix:**
- Summary, old: "Made by its own strain, κ must reach roughly αs1's own design titer for the blend to cost within 10%
  of αs1-casein alone ($22.3/kg);"
  New: "Made by its own strain and co-precipitated with αs1, κ must reach roughly αs1's own design titer (about
  29 g/L) for the blend to cost within 10% of αs1-casein alone ($22.3/kg). On its own column, no titer up to 42 g/L
  is enough."
- Make the same change in the Discussion Notes and the memo: "…and, if it co-precipitates with αs1, κ must reach
  roughly αs1's design titer to add under 10%".

### M3. Funders item 8 says "three orders of magnitude". The numbers give about four.

**Where:** rep (§5.3 item 8), typ 2177.

**Evidence:** 30 g/L ÷ 2 mg/L = 15,000×, which is 4.2 orders. 30 g/L ÷ 4.14 mg/L = 7,250×, which is 3.9 orders.

**Fix:**
- Old: "Both are three orders of magnitude short of a commodity design point in public data (bovine α-lac 2 mg/L in
  yeast; κ-casein 4 mg/L peer-reviewed)."
- New: "In public data, both are about four orders of magnitude (roughly 10,000×) short of the 30 g/L design point
  (bovine α-lac 2 mg/L in yeast; κ-casein 4 mg/L peer-reviewed; the best patent κ, 0.25 g/L, is 120× short)."

### M4. The report gives three different accounts of α-lac's solubility against pH.

**Where:**
- §2.4: rep 572, typ 750: "α-lac is soluble from pH 2 to 9, Layman et al. 2018".
- §2.7: rep 757, typ 965: "the protein unfolds and sticks to cells below pH 5.5".
- §5.3 item 8: typ 2179: "the protein needs neutral pH to stay soluble".

**Evidence:**
- alac.yaml `alac_functional_properties_for_dsp`: Layman's claim is about the commercial holo (Ca-bound) ingredient.
  Apo α-lac at low pH is a molten globule and aggregates.
- Viaene found no soluble bovine α-lac in yeast culture below pH 5.5.
- Wang 2025 got its best human α-lac titer at pH 3.
- A reader sees "soluble from pH 2 to 9" and then "needs neutral pH" with no reconciliation.

**Fix:**
- §2.4, old: "α-lac is soluble from pH 2 to 9, Layman et al. 2018".
  New: "the commercial, calcium-bound α-lac is soluble from pH 2 to 9 (Layman et al. 2018)".
- §5.3 item 8, old: "the protein needs neutral pH to stay soluble, proteases need low pH to be suppressed."
  New: "in yeast culture bovine α-lac was lost below pH 5.5 (without its calcium it unfolds and sticks to the cells),
  while the record human α-lac run needed pH 3 to suppress proteases."

### M5. The α-lac limitation says the price band's "low end is close to whey protein's own price". That is stale after R14-H2.

**Where:** rep (§6, α-lac bullet), typ 2282.

**Evidence:** The low end is now $25 per kg of α-lac. The whey band is $8.7–17.8, so the low end is 1.4× the top of
the whey band. The sentence was true for the old $15.

**Fix:**
- Old: "and its low end is close to whey protein's own price;"
- New: "and its low end, $25 per kg of α-lac, comes from a ~60% ingredient priced not far above whey protein, converted
  by us to a per-kg-α-lac basis;"
- Alternatively, drop the clause.

### M6. The α-lac scale sentence in Q6 is inaccurate, and its 1 kt/yr figure disagrees with Table 1 without explanation.

**Where:** rep (§4.7, "α-Lac's industry benchmark follows BLG's curve shifted to smaller plants: $114 at 100 t/yr,
$27.8 at 1 kt/yr and $15.8 at 10 kt/yr"), typ 1731–1734.

**Evidence:**
- The α-lac curve *is* BLG's curve. The BLG scale curve gives $27.82 at 1 kt and $15.84 at 10 kt; α-lac gives $27.80
  and $15.83. Nothing is shifted.
- Table 1 and Table 6 give the α-lac industry benchmark at 1 kt/yr as $28.2. That figure keeps the base plant's
  100 m³ vessels, while the scale curve re-sizes them. The lactoferrin sentence explains this difference; the α-lac
  sentence does not.

**Fix:**
- New: "α-Lac's industry benchmark lies on BLG's own scale curve (same route, same titer), extended to smaller plants:
  $114 at 100 t/yr, $27.8 at 1 kt/yr (re-sized vessels; Table 1's $28.2 keeps the base plant) and $15.8 at
  10 kt/yr, the same as BLG."

### M7. "Heme is therefore a small part of a plant-based burger's cost" compares against a number the report no longer gives.

**Where:** rep (end of §4.11), typ 2074.

**Evidence:**
- R14-M5 removed the analogue retail price. The only comparator left is retail ground beef, so no burger cost appears
  in the report.
- The table's own range reaches $1.94 (Chen at 0.8%) and $2.98 (Shao at 0.8%), which is 13–20% of retail beef.
- The cost is ex-works, while the beef price is retail.

**Fix:**
- Old: "Heme is therefore a small part of a plant-based burger's cost, even made from today's best published
  secreting strains."
- New: "Even from today's best published secreting strains, heme adds about $1–2 per kg of analogue at Impossible's
  use level (ex works; 7–11% of the retail price of the ground beef it imitates), and under $0.5 at the design point."
- Optionally add "and below 20% even at the legal maximum".

### M8. The basis of the α-lac titer is inconsistent, and in one place it makes $1,848 look like the cost at 0.6 g/L.

**Where:**
- Discussion Q1: rep (§5.1 Q1), typ 2094: "$1,848 at its best public titer (0.6 g/L)".
- Q3: rep 1239, typ 1519: "against a best public titer of 0.4 g/L of human α-lac" (`d: 1`, no basis given).
- Table 6: rep 975: "0.4 g/L" (not labelled whole broth).
- Figure 3 marker: "0.386 g/L".
- Everywhere else the report says "0.6 g/L of supernatant, 0.39 g/L of broth".

**Evidence:** `academic/alac.design.titer` = 0.386, which is the whole-broth value that was costed.

**Fix:**
- Discussion Q1: "(0.6 g/L of supernatant, 0.39 g/L of broth)".
- Q3: `#fx(..., d: 2)` and append "of broth".
- Table 6: d: 2, or footnote "whole broth".
- make_figures.py marker: format `:.2f` so it reads 0.39.

## LOW

**L1. A stale count of proteins.**
- Where: rep (§4.3, "because no public fed-batch dataset for any of the six reports titer, rate and yield together"),
  typ 1376.
- Fix: "six" → "seven".

**L2. Figure 3 (fig1_cost_vs_titer): six defects in the α-lac panel and footnote.**
- (a) The rotated top-axis label "<< best public alpha-lac (Wang 2025; human; ethanol; whole broth): 0.386 g/L" runs
  into the lactoferrin panel's x-axis label and its "10" tick. Shorten it, e.g. "<< best public α-lac (Wang 2025,
  human): 0.39 g/L", or add row spacing.
- (b) The "<<" convention (a titer below the axis, drawn at its left edge) is explained neither in the caption nor
  the footnote. Add to the report caption (typ ~1205): "'<<' marks titers below the axis range, drawn at its left
  edge."
- (c) The footnote says "fermenters sized to each plant (200 m3 at 10 kt/yr; 100 m3 for lactoferrin and albumin)".
  Add "and α-lac".
- (d) The footnote's price-band list omits α-lac. Add "dairy α-lac market-report prices per kg of α-lac (grade C)".
- (e) The band label "$25-129/kg protein" should read "$25–129/kg α-lac".
- (f) The band label sits under the curves and is partly hidden ("alpha-lactalbumin" is overprinted). Move it to the
  lower-right of the band.

**L3. Figure 8 (fig3_required_titer): the footnote does not explain α-lac's targets.**
- The footnote says "Targets bracket each product's market (lactoferrin…; albumin's…)" and leaves α-lac out.
- Fix: add "α-lac's $25 and $130 are the ends of its band per kg of α-lac, $60 a midpoint".

**L4. Figure 12 (fig9_routes): two issues in the α-lac panel.**
- (a) No x-tick labels below $100, so the two points ($33.8, $41.4) and the band's low edge sit on an unlabelled
  stretch. Add $20/$50 ticks, as in the BLG panel.
- (b) The isolate row is still labelled "isolate: ammonium-sulfate precipitation". R14-L11 asked for "model's generic
  isolate route (not GFI's >99% chromatography grade)". The text (rep 1537–1540) covers this, but the figure does not.

**L5. The heme table drops the unit for Shao's whole-broth titer.**
- Where: rep (Table 18, "3.5 g/L of supernatant (2.2 of broth)"), typ 2048.
- Fix: "(2.2 g/L of broth)".

**L6. Q1 α-lac bullet: Zhu 2024 is human α-lac, and the order is reversed.**
- Where: rep 991–992, typ 1248.
- Zhu 2024 measured human, His-tagged α-lac, quantified after a Ni column (titers.csv row 117).
- Fix: "the next best are 0.12 g/L of human α-lac in a *B. subtilis* flask (Zhu et al. 2024, after a His-tag
  purification) and 0.11 g/L (human, *K. phaffii*; Deng et al. 2023, abstract)."

**L7. "3 L culture" is the vessel size, not the culture volume.**
- Where: rep 753, typ 961.
- Wang ran a 3 L bioreactor with a 0.9 L medium charge (alac.yaml:260).
- Fix: "in the supernatant of a *K. phaffii* culture in a 3 L bioreactor".

**L8. The ×0.64 whole-broth factor for Wang assumes the model's 107 g/L cells.**
- Where: typ 963.
- Wang reports only OD, and at pH 3 biomass was "suboptimal" (alac.yaml:283–285). With fewer cells the true
  whole-broth titer is between 0.39 and 0.6 g/L.
- Fix: add one clause: "Wang's cells grew poorly at pH 3, so this conversion probably over-discounts; the assay's
  proteolysis pushes the other way."

**L9. The basis of the 150 t/yr LegH market is unknown.**
- Where: rep (§4.11 first bullet), typ 2060–2062.
- heme.yaml:601–605 says the GFI/Volza 150 t may be tonnage of LegH Prep (6–9% LegH), not LegH protein.
- Fix: add "(of LegH protein or of the preparation; the source does not say)".

**L10. References.**
- (a) "Wang Y, et al. GCB Bioenergy 13:640 (2021) (recombinant αs1-casein in *E. coli*)." has no title and no DOI.
  It is now cited for a new number (1.13 g/L, §4.10). Add the title and DOI from the full text on disk.
- (b) Panchanawaporn et al. 2026 has no data/evidence entry carrying its full reference, only a titers.csv row
  (J Fungi 12:289, PMC13117078). The title and DOI 10.3390/jof12040289 cannot be checked against the repo. Add an
  evidence entry.
- (c) heme.yaml gives Chen et al. 2025 two different author lists. l.868 has "Chen H, Niu Y, Wang Y, Zhang L, Dai Z,
  Luo A, Du G, Zhao X", which the report uses. l.412 has "Chen HT, Niu YH, Zhang LX, et al.". Harmonise them.

  Checked and consistent with the evidence files (titles, journals, volumes, first pages, DOIs):
  - Wang X 2025, Viaene 1991, Deng 2023, Zhu Y 2024, Wang B 2024, Antuma 2025, Runthala 2023, Chen 2025 and Shao 2022.
  - Layman 2018, Green Queen 2026, FSANZ A1186, 21 CFR 73.520, GRN 737/763, Redbiotec WO 2023/002061, New Culture
    US 2023/0404098, Formo WO 2026/068856 and Standing Ovation EP 4 533 954.

  Every new in-text citation has an entry, and the list is alphabetical.

**L11. "the ends of its band" is off by $1.**
- Where: typ 973–974: "α-lac $25 and $130, the ends of its band".
- The band is $25–129.
- Fix: "$25 and $130 (the ends of its band, $25–129, rounded)".

**L12. Mixed decimals in the incumbent cell.**
- Table 1 and Table 6 show "$25.0–$129" (`usd(d: 0)` lower end vs `usd0`).
- Cosmetic; use "$25–$129" as in the prose.

**L13. Figure 1 (fig10) α-lac panel: the physical-limit row is not at the plant size in the panel title.**
- The row shows "$5 / $4" at 31.8 kt/yr (see M1) under a panel titled "1,000 t/yr".
- All panels share this convention, so no change is needed. M1's fix to the cap changes this row to about $5.

## Clarity (proposed rewrites)

**C1. §4.1 reads as a non-comparison** (rep 936–937, typ 1194–1195).
- Old: "at BLG's 10 kt/yr it would cost $21.2/kg, against $21.2 for BLG."
- New: "at BLG's 10 kt/yr it would cost the same as BLG, $21.2/kg."

**C2. §2.4: "whose" points at BLG** (typ 750).
- Old: "a tighter ultrafiltration membrane than BLG, whose lower flux is not modelled".
- New: "a tighter ultrafiltration membrane than BLG does, and that membrane's lower flux is not modelled".

**C3. Heme caveats: "too cheap / too dear" leaves unclear what is too cheap** (typ 2034–2035).
- New: "It is an estimate, not a bound. Leaving out lysis and debris removal makes it too low. Counting the drying of
  a product that is sold frozen makes it too high. …"

**C4. Cheese: the range is hard to parse** (typ 1958).
- Old: "We take 19%, over 16.7%–25%."
- New: "We take 19%, and show 16.7–25%."

**C5. Cheese: "pulled down" is unclear to a non-specialist** (typ 1966).
- Old: "is the casein least pulled down by acid or calcium".
- New: "is the casein least likely to precipitate with acid or calcium".

**C6. Heme: the sentence on loading is cryptic** (typ 2065).
- Old: "Only loaded globin colours and flavours."
- New: "Only globin that carries its heme gives colour and flavour."

**C7. Which end of the α-lac band applies to the modelled product** (summary 7, Q1).
- The modelled 90% isolate is the high-purity grade, whose price is the top of the band ($129 per kg of α-lac). The
  $25 end comes from a ~60% ingredient.
- Add to summary point 7: "…inside the reported $25–129 band per kg of α-lac (grade C); the isolate grade it matches
  sells at the top of that band."

**C8. Q3: the secretion rate behind the $25 target** (rep 1237–1238).
- $25/kg at 53 g/L in 72 h implies 9.4 mg/g/h. That is twice the base design rate and 4.5× the best demonstrated
  rate.
- Add one clause: "…at 53 g/L (a secretion rate of about 9 mg/g/h, twice the base design's)". This ties α-lac to the
  report's central secretion message.

**C9. Summary 8 and memo: "ex works" is jargon.**
- On first use, write "ex works (the factory-gate cost, before transport and margins)".
- The memo's "Heme … adds $1.09 per kg of beef analogue" needs "at 0.45% use, ex works".

**C10. Memo: "any secreted titer above 1 g/L" for α-lac.**
- The report's §5.5 target is a *bovine* α-lac titer above 1 g/L. Human α-lac is already at 0.6 g/L of supernatant,
  so a human result above 1 g/L would not address the dairy product.
- Fix in the memo: "for bovine α-lac, any secreted titer above 1 g/L".

## Typst rendering

- No stray `none`, raw code, "n/a" or doubled words in the new content.
- The "n/a" in Table 14 (Onego row) predates this round.
- Semicolons after `#func()` calls render correctly in the new sections (e.g. Table 1 caption, rep 151–156).
- Cross-references @sec-cheese and @sec-heme resolve to §4.10 and §4.11, and the TOC shows both.
