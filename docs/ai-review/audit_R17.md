# Audit R17: cold read of the whole compiled report and memo (v4.1, branch v4.1, 2026-10-06)

Scope: the whole of `report/pf_tea_report.pdf` (generated 2026-10-06 10:38) and `report/memo.pdf`, read as a hostile but
fair bioprocess / techno-economics expert would. Earlier rounds (R12–R16) each checked one new section; this one checks
cross-section consistency, calibration of claims, the first objections an expert would raise, numbers, clarity for a
policy / funder reader, figures and references.

Mode: read-only. No tracked file was touched. run_analyses, make_figures and the build scripts were not run.

What I did run:
- `pdftotext -layout` of the report and memo (.preview/rep17.txt, .preview/memo17.txt; body only: .preview/body17.txt)
- scratch reads of results/analyses.json (.preview/r17_check.py, r17_check2–6.py)
- greps of the Typst sources, make_figures.py, data/titers.csv, data/pf/scenarios/*.yaml, data/evidence/hosts.yaml and
  references/text/GFI_2025_driving_down_costs_fermentation.txt
- a visual read of fig1, fig2, fig3, fig9, fig10 and fig12 (report Figures 3, 5, 8, 12, 1, 13)

References:
- "rep NNNN" = line of `.preview/rep17.txt`
- "typ NNNN" = line of `report/pf_tea_report.typ`
- "memo NN" = line of `.preview/memo17.txt`; "memo.typ NN" = line of `report/memo.typ`

## Numbers checked

About 120 numbers across the summary, Table 1, the results, the discussion, the memo and the figures, at the rounding
shown. **All match results/analyses.json.** One matches the JSON but states a physical bound wrongly (M1).

**Headline costs (Table 1, summary, memo table, 5.1)**
- Base MSP_CCF: BLG 21.17, OVA 21.28, ovd 21.35, cas 22.05, lf 167.79, alb 215.48, alac 33.81 → "$21.2 … $33.8". ✓
- Design-report: 16.42 / 16.49 / 16.54 / 16.99 / 129.86 / 185.23 / 24.98 → "$16.4 … $25.0". ✓
- Industry: 15.84 / 15.95 / 16.02 / 16.39 / 105.84 / 205.23 / 28.22. ✓
- Academic: 42.96 / 227.18 / 478.68 / 803.47 / 413.15 / 423.66 / 1848.46. ✓ Variants: Li 2026 106.9, OVA intact 451.9,
  Lv 2023 278.6, Zhu 2018 514.1, EVERY patent 23.74, casein patent 197.6, Delta patent 997.1. ✓
- Physical limit: 4.10 / 4.23 / 4.26 / 4.45 / 56.92 / 171.57 / 5.16; light 3.30 / 3.42 / 3.44 / 3.49 / 48.54 / 153.0 / 3.96. ✓
- At 2.1 mg/g/h: 24.52 / 24.59 / 24.62 / 25.38 / 83.75 / 210.6 / 25.45. ✓ q_p 5/10/20/120: 12.11 / 8.09 / 5.42 / 3.38. ✓
  500 g/L feed 4.53, aseptic 5.67, OVA at 50 g/L 8.33. ✓
- Aseptic 30.95 (+9.8), pioneer 24.43 … 39.73, EU 24.32 … ✓; light gap 4.75 → "$4.7". ✓

**Base case (Table 5, §4.1, §2.6, §2.3)**
- Per-kg lines (7.14, 1.96, 2.45, 4.11, 1.55, 1.60, 0.81, 0.64, 0.91). ✓ Capital-related 54.6% → "55%"; glucose 19.4%; disposal 7.6% → "8%". ✓
- COP 18.93, DCF 20.71; TCI $490M; FTE 123.7 → "124"; 12.4 staff/kt; Lang 6.50; cycle 121.1 h; 4,299 kg/batch;
  overall yield 0.0973; q_p 4.66 → "4.7"; Y_ps/ceiling 0.825 → "83%"; effective yield 0.277. ✓
- 133 mol O2 and 9.2 kg glucose per kg made (636.85 kmol / 4,800 kg; 10.28 × 0.8956). ✓
- Ceilings 76/74/72/70/65/60; 600 g/L feed 97/109/107/105/102/98. ✓
- Best designs: 7.06 / 8.74 / 12.05 / 18.64 / 36.21. ✓

**Drivers, uncertainty, scale, siting**
- Tornado ranks 1–7 (25.9–12.9, 15.8–22.9, 12.0–17.3, 14.5–18.5, 12.3–15.8, 15.6–17.8, 15.3–17.5); yield rank 20 ($0.7); vessel rank 10 ($1.8). ✓
- Bridge: 7.57 → +2.74, +1.44, −0.14, +0.59, +0.52, −1.92, +5.12, −1.74, +6.99 → 21.17; lactoferrin +40.17; OVA isolate +4.85. ✓
- Monte Carlo BLG: 400 draws, 196 feasible (49%), 164/22/18 infeasible; p50 17.66, p10–p90 14.3–22.6; all-draw 19.4 (15.2–24.5);
  X_prod 111 vs 83; μ 0.0090 vs 0.0049. Other products' medians and feasible shares. ✓ Spearman: titer −0.80, paste +0.27, t_prod +0.26. ✓
- Scale: 27.8 − 15.8 = 12.0; 15.84 − 14.56 = 1.3. Lactoferrin 98.5 / 62.6 / 55.4. α-lac 113.9 / 27.8 / 15.8. Albumin 308 / 215 / 203. ✓
- Siting: +3.15; glucose 2.16; energy 0.82; construction 1.04; wages −0.03; disposal −0.86; 4%/20 yr 3.85; 7.5%/20 yr 2.54; 4%/10 yr 1.20. ✓
- Claims (Table 14): 15.8/12.3/13 h/38/12.3; 25.9/20.1/12 h/21/19.9; 13.5/9.9/48 h/40/10.2; 143 h/40/8.7; Onego unreachable. ✓

**Incumbents and equivalents**
- Whey 21 annual export prices: 3 above 15.84, 8 above 12.3 (memo and §5.3). ✓ Egg white cheaper than mean whey in 5 of 11 years (2017, 2019, 2021, 2024, 2025). ✓
- Multiples of band: BLG 2.4–5.0×. ✓ α-lac 14× top of band; GFI 20 g/L = 33× 0.6 g/L. ✓
- Milk/egg: $0.71, $0.74, $0.077, $0.078; break-even 48 / 50 / 24 / 24 g/L; whey share 11–21%; farm milk protein $14–$19; eggs $26–$86. ✓

**Albumin, lactoferrin, notes**
- Albumin: capture only 143.2, UF/DF 34.3, methanol +6.0, recovery 0.40/0.86 → 270/170, $100/L 114, $2,000/L 281, 125 cycles 941,
  50 g/L loading 196; $1.95–$10.23 per kg meat (9.04 and 47.46 g/kg). ✓
- Lactoferrin: UF/DF 110.5; 125 cycles 316; COP 97.1 / 150.6; their design 105.2 / 206.8; Intelligen 3.08× / 2.93×. ✓
- Cheese: κ titer for 10%: 28.1–29.2 g/L; blend $567 / $573 at 0.25 g/L; 25–26× α-s1. ✓
- Heme: 242.7 / 172.6 / 372.4; $1.09 (0.61–1.94); $1.68; $0.16 at 1 kt; 7.2% and 11% of $15.26. ✓
- Transferrin: 948.5 / 1,938.9 / 313.9 / 1,217.8; $0.35 (0.07–1.13), $0.12, $80.55 at 0.37 g/kg; "40× smaller" dose (15 vs 0.37 g/kg). ✓
- Binder: MC $0.067 (0.018–0.79), OVA $0.85 (0.51–1.36), industry $0.64, physical limit $0.17; 12.7× → "13", 2.5×. ✓

**Floor and animals (§4.10, summary point 9, Answers, memo)**
- 1.77 kg, 0.19 kg, 11.7 mol, 6.8 MJ, $0.88 / $0.71 / $1.28; 13.2 kg/m³/h; cells cap 6.0; physical limit 140/109.4 h = 1.3; base 0.27. ✓
- US feed 6.57 / 4.69 / 5.98; totals 8.85 / 6.75 / 14.23; other 2.28 / 2.06 / 8.26 → "$2–$8"; ratios 6.6–9.3 → "7–9×". ✓
- EU feed 8.87 / 7.88, totals 12.91 / 11.59, milk 4.88; cattle credit 1 − 0.903 → "10%". ✓
- **"8–21 over our range of cooling limits"**: matches `p_max_heat_range_kg_m3_h` (7.95, 21.19) but is not the vessel bound (M1).

## HIGH

None. Every headline number reproduces from analyses.json, and nothing below changes a conclusion.

## MEDIUM

### M1. The vessel bound's range "8–21 kg/m³/h" quotes the heat limit alone. Above about 32 kW/m³, O2 transfer binds, so the bound is 8–17.

**Where:** §4.10 "The floor", rep 1652–1654, typ 2003.

**Evidence:**
- floor.py returns `p_max_heat_range_kg_m3_h` = (7.95, 21.19) for 15–40 kW/m³. It is not capped by `p_max_o2_kg_m3_h` = 17.10.
- The sentence states the bound ("could make at most 13 … cooling binds first; 8–21 over our range of cooling limits").
  At 40 kW/m³ cooling no longer binds, and the vessel is capped at 17.1 by O2.
- The crossover is at 25 × 17.10 / 13.25 ≈ 32 kW/m³.
- R16 M4's fix text said "8–17". The implementation reports the uncapped heat value.

**Why it matters:** this is a physics bound in the section that argues the vessel is not what limits cost. A reviewer who checks
it finds an error in a number the text calls a limit.

**Fix:**
- typ 2003: print `calc.min(P_heat_range.at(1), F0.floor.p_max_o2_kg_m3_h)` as the upper end.
- New wording: "(cooling binds first; 8–17 over our range of cooling limits, O2 transfer taking over above about 32 kW/m³)".
- Or return the capped range from floor.py. Do not type the numbers.

### M2. The "industry benchmark" headline never says the secretion rate it needs: about 7 mg/g/h for 72 h, 3.3× the best demonstrated.

**Where:**
- Summary, rep 54–60 (typ 224).
- §4.2, rep 1014–1015 (typ 1277): "all four inside their incumbents' bands".
- 5.1 Q1, rep 1897–1900.
- 5.3, rep 1999–2001.
- Memo bullet 2 ("At the titers companies' cost models assume, the commodity proteins near their markets", memo 10–13, memo.typ 66–71).

**Evidence:**
- `claims[0].q_p_own` = 6.96 mg/g/h. That is 42 g/L in a 72 h production phase at 107 g/L cells.
- The best demonstrated K. phaffii glucose fed-batch is 2.1 mg/g/h (Prielhofer), and the best public BLG run is about 1.
- GFI 2025 Table 2 gives a titer (42 g/L, average) and a yield (0.03–0.17 g/g) but no fermentation time or productivity
  (checked in references/text/GFI_2025_…txt). The 72 h is the model's choice, not GFI's.
- The text does say elsewhere that $20/kg needs 5–7 mg/g/h (point 1; Table 8). It never says that the $15.8 industry case
  itself sits at the top of that range. In the memo the reassuring bullet ("near their markets") comes before the bullet
  that undercuts it.
- An expert reads "42 g/L in 72 h" as a productivity claim, and this is the first number they would attack.

**Fix:**
- Summary, after "(42 g/L, GFI 2025, a survey average over unnamed proteins)": add "which GFI gives without a fermentation time;
  in our 72 h production phase it implies secretion at #fx(R.claims.at(0).q_p_own, d: 0) mg/g/h, about three times the best
  demonstrated".
- §4.2 bullet: "… all four inside their incumbents' bands, if a strain secretes about 7 mg/g/h for three days (Section 4.4)."
- Memo bullet 2: append "; that needs about 7 mg/g/h of secretion over 72 h, about three times the best published rate (next bullet)."
- Read every value from `R.claims` (or `S("industry/blg").design.q_p_mg_g_h`).

### M3. The evidence for the 40 mg/g/h secretion ceiling is stated three different ways.

**Where:**
- §2.3, rep 543–545: "compiled maxima for secreted proteins are below 1 (Looser 2015)".
- §4.4, rep 1258–1260 (typ 1546): "Fungal cellulase processes … roughly 5–20 mg/g/h (our arithmetic)".
- Limitations, rep 2056–2057 (typ 2490): 40 is "about 2.5 times the highest specific secretion rate we found published
  for any protein (15–16 mg/g/h, A. niger glucoamylase)".

**Evidence:**
- 20 mg/g/h (cellulase, §4.4) is above the "highest we found published" (15–16).
- "Below 1" (§2.3) is a K. phaffii compilation. It reads as a general statement ("secreted proteins").
- The 5–20 is an estimate from volumetric productivity and an assumed 20–50 g/L of cells, not a measured specific rate. The text
  says "our arithmetic", but the Limitations bullet does not reconcile it.

**Why it matters:** the secretion ceiling sets the physical-limit case ($4.1) and Table 10. A sceptic will set these three
sentences side by side.

**Fix:**
- §2.3: "compiled maxima for proteins secreted by K. phaffii are below 1 (Looser et al. 2015)".
- Limitations: "about 2.5 times the highest *measured* specific secretion rate we found for any protein (15–16 mg/g/h, A. niger
  glucoamylase, chemostat and pH auxostat), and 2–8 times what industrial cellulase processes imply at assumed cell densities
  (5–20 mg/g/h, Section 4.4; native enzymes)".

### M4. The Q2 answer says productivity "drives the cost of every protein". For lactoferrin and albumin, the tornado and Table 7 say the column does.

**Where:** 5.1 Q2, rep 1911–1915, typ 2327–2330.

**Evidence:**
- Lactoferrin: the top three tornado bars and the top three ρ are all resin and column inputs (rep 1135–1138, 1174–1177).
- §4.3 itself says "for lactoferrin and albumin the column's inputs lead instead".
- The sentence ranks "fermenter productivity …, then the capital basis …; sugar and energy prices come second". "Then … come
  second" reads as two second places.

**Fix:** "Fermenter productivity (protein per hour of vessel time) drives the cost of BLG, OVA, ovomucoid, β-casein and α-lac,
followed by the capital basis (vessel prices and fixed-cost rule); sugar and energy prices come third. For lactoferrin and
albumin the column (resin price, life and loading, and the capture recovery) leads (Figure 6, Table 7)." Then delete the
last sentence of the bullet.

### M5. The lactoferrin "easy case" rests on a methanol-induced design titer that is costed on glucose and not demonstrated methanol-free. "The size of its market" overstates a 250 t/yr plant.

**Where:**
- Summary, rep 45–46 (typ 217): "on its own published design (10 g/L, cation exchange) at 250 t/yr, the size of its market".
- Memo bullet "Scarce proteins are the easy case" (memo 23–25).
- §4.9, rep 1607–1610.

**Evidence:**
- §4.9 says Intelligen's design reaches 10 g/L by "glycerol growth and methanol induction". The base case runs
  `methanol_frac_prod` = 0 (base.yaml note: Intelligen's split "it does not state, so its variants keep 0"). The model's own
  methanol penalty is +12% on BLG (AUDIT v4 G1) and +$6/kg on albumin.
- The best methanol-free lactoferrin titer is 2.8 g/L (porcine), 3.6× below 10. At that titer the cost is $413, inside the
  dairy range.
- 250 t/yr is below the low end of the world market quoted in §1 (0.3–1.6 kt/yr).
- The memo bullet gives neither caveat. "Easy" is the strongest word in the memo.

**Fix:**
- Summary: "Lactoferrin runs on the design point of Intelligen's published process (10 g/L, cation exchange; their strain is
  methanol-induced, costed here on glucose) at 250 t/yr, near the low end of its 0.3–1.6 kt/yr market".
- Memo: "*Scarce proteins are the easier case.* At the 10 g/L of Intelligen's (methanol-induced) design and a 250 t/yr plant,
  PF lactoferrin costs $130–$168/kg, below the $250–$1,585/kg reported for the dairy product; at the best public methanol-free
  titer (2.8 g/L) $413, inside it. …"
- Optional: add an `lf_methanol` variant (methanol_frac_prod 1) and quote its cost.

## LOW

**L1. "Eight results stand out:" introduces nine items** (rep 66, typ 235). Point 9 (feedstock) was added in v4.1. Fix this
first, because it is the most-read paragraph. "Nine results stand out:", or better, count the list in Typst.

**L2. Stale version labels.**
- Title line "Version 4 (seven proteins; v2.1 audited and AI pre-reviewed)" (typ 173). Running head and typ 1 say "v4" for a
  v4.1 document; memo.typ 55 says "v4".
- Table 2's last row (typ 404) says "Notes: Added in v4 … rennet curd … heme" and points to §4.11–4.12 only. §4.10, §4.13 and
  §4.14 (v4.1) are missing.
- Priors table header "Outcome (v2)" (typ 2566) shows current (v4.1) outcomes.
- Memo caveats (memo.typ 144) list the v3 and v4 additions, not v4.1's (feed comparison, transferrin, binder).
- Fix: "Version 4.1 (seven proteins …)"; the running head "v4.1"; Notes row "Added in v4 and v4.1: … rennet curd …, heme …,
  transferrin …, binders; and how PF's feedstock compares with the animals' feed" → §4.10–4.14; "Outcome (v4.1)"; memo caveat
  "…, and the feed, transferrin and binder notes in version 4.1".
- Outside the report: docs/SCOPE.md still describes the α-lac plant as "~27% of the high-purity market, 3% of the food-grade
  one", which R15 M1 replaced with "about 5% of the α-lac market".

**L3. The sign of the Intelligen comparison is reversed in the prose.**
- Summary point 4 (rep 84–85, typ 260): "Intelligen's food-PF design comes out within −4% of ours". §5.2 (rep 1951–1952,
  typ 2376) is similar.
- Table 4's −4% is ours relative to theirs (42.00 vs 43.52), so Intelligen comes out about 4% *above* ours.
- Fix: "our model of Intelligen's food-PF design comes within 4% of their cost (ours 3.5% lower)".

**L4. Summary point 9 mixes units** (rep 122–123, typ 307): "its glucose floor, 1.8 kg per kg of protein, is several times
below them", where "them" are feed bills in dollars. Fix: "its glucose floor, 1.8 kg ($0.71) per kg of protein, is 7–9 times
below them".

**L5. The spent-cell disposal choice is conservative, and the sensitivity is computed but never quoted.**
- Landfill at $458/t dry cells is $1.60/kg, 8% of the BLG cost. `base_sensitivities["spent cells free (feed or fertiliser
  outlet)"]` = $19.57 (−$1.6).
- An expert will note that spent yeast is usually sold as feed.
- Fix: §2.4 (typ 825) "…would make it free ($19.6/kg BLG) or a credit", and the same figure in the §4.1 sentence on disposal.

**L6. The albumin resin arithmetic does not add up as written** (rep 934–937, typ 1204).
- "$104 per kg (… $31 per kg loaded on the capture column, and the polish column adds about $44 more)": 31 + 44 ≠ 104.
- The missing step is that about 1.9 kg is loaded on the capture column per kg sold (recovery 50% overall, 56% capture), so the
  capture costs about $59.
- typ 1204 also types `/ 0.040` (the binding capacity) instead of reading `dsp.cex_dbc_g_L`.
- Fix: "…$31 per kg loaded on the capture column, and about 1.9 kg is loaded per kg sold ($59); the polish adds about $44";
  read the loading from the parameters.

**L7. Figure 12 (fig9_routes.png) puts cost-of-production stars beside MSP_CCF dots.**
- The stars are Intelligen's COP ($299, $441). The lactoferrin dots are our MSP_CCF ($111, $168), not our COP ($97, $151).
- The visual gap (about 2.6–2.7×) differs from the text's 3.1× and 2.9×.
- Fix: plot our COP beside the stars (or as a second marker), or caption: "Stars: Intelligen's cost of production, which
  carries no return on capital; compare with our cost of production in Table 16, not with the dots".

**L8. Figure 5 (fig2_bridge.png) title "From a $8/kg crude enzyme …" while the text and bar say $7.6** (make_figures.py 147,
`:.0f`). Use `:.1f` for the start.

**L9. Figure 3 (fig1_cost_vs_titer.png) layout.**
- The marker labels collide:
  - BLG: "42 g/L" and "50 g/L (Behm 2022; NREL)".
  - β-casein: three labels at the left edge.
  - Lactoferrin: three labels at the left edge.
  - Albumin: the 8.74 and 14.8 labels.
- The panel grid fills only about the left half of a 3,653 px canvas, leaving the right half and the bottom blank, so the
  figure prints small.
- Fix: tighten the figsize and bbox, and stagger or shorten the marker labels (for example a numbered key in the footnote).

**L10. Typed numbers in make_figures.py** (rule: everything read from results or base.yaml).
- Academic labels (l. 561–571: 13.9, 30, 3, 0.6, 8.7, 4.4, 1.5 g/L).
- "industry benchmark, 42 g/L" (578), "2.1 mg/g/h" (580), "40 mg/g/h" (156, 582), "14.6%/yr" (297, 625).
- Fig. 2 flowsheet "glucose feed 500 g/L", "x 200 m3", "45 g/L", "5% moisture" (432–438), and "200 m3 at 10 kt/yr; 100 m3 for …"
  (212).
- All are correct today. The academic labels and vessel sizes would silently drift if a scenario changed.
- Fix: format them from `R["scenarios"][…]["design"]["titer"]`, `pv(...)` and the design keys.

**L11. References.**
- Entries never cited in the body:
  - Choi and Jiménez-Flores 2001
  - Fermify WO 2024/200234
  - Nestec US 4,075,196
  - Liu WC et al. 2016
- Entries cited only indirectly:
  - Iaria et al. 2026 ("a 2026 review calls the highest reported", rep 1011: name it)
  - Swift 1998 and Withers 1998 (Limitations point to kinetic.yaml: name them)
  - Kuo 2020 and Chen 2011 ("B8", "Essential 8": add the citations)
  - Future Market Insights ("a market-research page")
  - Hy-Line, Aviagen, National Chicken Council, van Horne (Wageningen), European Milk Board (§4.10 says "breeder targets,
    industry averages … Wageningen costings": cite by name)
- Hu 2025 and Liu 2026 appear only as Figure 3 markers. That is acceptable, or mention them in the lactoferrin bullet of §4.2.
- Two different "Wang et al. 2025" (α-lac, J Agric Food Chem; OVA solubility, Gels) are cited without disambiguation (rep 643,
  765). Use 2025a/2025b.
- No citation in the text lacks an entry among the ~80 I spot-checked.

**L12. Clarity for policy and funder readers.**
- Terms used before they are defined, or never defined:
  - "titer" (summary, first line of point 1; never defined)
  - "UF/DF" (§2.1, defined only by context in §2.4)
  - "DSP" (Table 5)
  - kLa
  - IRR and MACRS (§2.6)
  - HTST (§2.4)
  - p10–p90 (§4.3)
  - Brier (Table 21)
  - GFI's "P1 molecules" (§5.2)
  - "Essential 8, B8, Beefy-9" (§4.13)
- Fix: a six-line glossary box after the Summary: titer (g of protein per L of broth at harvest), specific productivity /
  secretion rate (mg protein per g dry cells per h), UF/DF, DSP, MSP_CCF vs COP vs MSP_DCF, price-anchored vs design-report
  capital. Also expand HTST, IRR and MACRS at first use.

**L13. Wording.**
- "a 84 h production phase" (typ 1607): "an".
- "the 1 kt/yr plants 100 m³ (albumin) and 100 m³ (α-lac)" (rep 666): "the 1 kt/yr albumin and α-lac plants 100 m³".

## The first things a hostile bioprocess expert would attack: are they acknowledged where the claim is made?

| Objection | Where the claim is made | Acknowledged there? |
|---|---|---|
| Production-phase secretion without growth | Summary, Table 1, memo | **Yes**: a dedicated summary paragraph (rep 124–132), memo bullet 3 and funders item 1. Good. |
| Minimum fill / titer ceiling | Summary point 2, §2.3, §4.4 | **Yes**: "a design ceiling", with Table 11 showing 0.20–0.50 fills. |
| Industry 42 g/L in 72 h = ~7 mg/g/h | Summary, §4.2, memo bullet 2 | **No** (M2). |
| Product yield derived by inverting Intelligen's Eq. 2 | §2.2; drives the ceiling | Yes in §2.2 and Limitations; the summary does not need it, since yield moves cost by only $0.7 at a fixed titer. |
| Capital conventions and vessel price | Summary point 4, every table in brackets | **Yes**: shown everywhere as a named structural sensitivity. |
| Cell density 107 g/L and O2 cap 200 mol/m³/h per m³ of cell-free liquid | §2.3 | Yes (review BE-7's 100–120 per m³ of broth is quoted). |
| DSP recovery (90%) and 85% purity by membranes alone | §2.4 | Partly: the purity is graded D and "as open as for BLG" (α-lac); purity does not change the membrane-route cost. Acceptable. |
| Spent-cell disposal as landfill | Table 5 (8% of cost) | Partly: the outlet is named but its $1.6 effect is not quoted (L5). |
| Lactoferrin design titer is methanol-induced | Summary, memo | **No** (M5). |
| Secretion ceiling 40 mg/g/h | Physical-limit headline | Yes ("assumed", Table 13 at 2.1–120), but its evidence is stated inconsistently (M3). |

## Checked and correct (logic)

- Every headline number in the summary, memo and 5.1 is computed from analyses.json in Typst. Prose and tables agree with one
  another (summary ↔ Table 1 ↔ §4.x ↔ 5.1 ↔ memo), including the $4.7–$6.6 feed bills after R16 M2.
- R16 fixes all present and not regressed: the "with all the feed charged to protein" qualifier (summary 9, §4.10, Answers,
  memo), "no K. phaffii process" (not "no cell"), the cells' 6 kg/m³/h against the vessel bound, the pricing bases in
  Limitations, EU hens 2.00 vs 1.96, EIC non-feed cost, the cattle credit by milk/(milk + cattle), 2024 dollars for the EU,
  2–3 c/MJ, Figure 13 labels and whiskers above the bars.
- "A best case, not a floor": the physical-limit language is consistent in the summary, §4.5, memo and Table 12. Prior 2 keeps
  its pre-registered word "floor", explained in the caption.
- Prior scoring arithmetic (Brier 0.1225, 0.04/0.64, 0.16/0.36/0.25) is right.
- Figure 13 (fig12) and Figure 1 (fig10) match the tables. Figure 8 (fig3) albumin panel is empty by design, and the footnote
  says why.
- Scale-curve vs Table 1 differences (lactoferrin $98 vs $106; α-lac $27.8 vs $28.2) are explained in the text (vessel re-sizing).
