> AI reading pass (Claude, an AI model), 2026-09-27, run after the Phase F pre-review to read sources Pablo downloaded. Kept verbatim except local paths. Not a human review. Every finding acted on was re-checked against the source text, table images or workbook cells; decisions are in docs/REVIEW.md (follow-up section).

# Intelligen lactoferrin report (Feb 2026) vs our lactoferrin case

**Conventions**
- **Pages.** "p." is the report's printed page number. PDF page = printed + 1. The cover and the two flowsheets (PDF pp. 38–39) are unnumbered.
- **Lines.** "L" is the line number in `references/text/Lactoferrin_Feb2026_Version.txt`, so every figure can be pasted verbatim into the evidence file.
- **Quoting.** Numbers are exactly as printed. Surrounding wording is paraphrased to keep quotation minimal; there is one direct quote, in §5.
- **(c)** marks my own arithmetic, with the working shown.
- **Abbreviations.** LF = lactoferrin. MP = Intelligen's powder stream. PA = our price-anchored capital (the default). DR = design-report capital (`capital.basis: nrel`). COP = our operating cost plus 10-year straight-line depreciation of TCI.
- **Repo untouched.** I edited nothing in either repo. Scripts and outputs are in `<scratch>/review/lf/`: `run_lf.py`, `categories.py`, `bridge.py`, `matched.py`, the `*.json`/`*.out` results, and the rendered figures in `img/` and `png/`.

## Bottom line
1. **The report's own figures (2024 prices, Tables 2–3, p.18):**
   - Case a (UF/DF only): unit production cost **$262.43/kg of powder**, which is **$290.7/kg LF** (c: 262.43/0.9028, the flowsheet LF fraction).
   - Case b (cation exchange): **$406.95/kg of powder**, which is **$429.9/kg LF** (c: 406.95/0.9467).
2. **GFI's "$292/kg" is case a converted to a per-kg-protein basis.**
   - GFI's own Figure 11 (GFI p.29) prints $260/kg for lactoferrin and $940/kg for collagen.
   - Its text gives $292 and $1,043, which are both the chart values ÷ 0.90 (c).
   - So $292 is the UF/DF-only case. Our CEX route (`lf`) has to be compared with case b, about $430/kg LF.
3. **Our comparator is COP, not MSP_CCF.** SuperPro's unit cost includes depreciation (inside "facility-dependent") and no return on capital.
   - Our COPs: `lf_ufdf_only` $106.8 (PA) / $74.8 (DR); `lf` $179.3 (PA) / $131.2 (DR), all per kg LF.
   - Intelligen is **2.7× / 3.9×** our UF/DF-only case and **2.4× / 3.3×** our CEX case.
4. **Process design explains almost none of the gap.** I fed Intelligen's design inputs into our model: their output, 6 × 100 m³ fermenters, $0.10/kWh and 5 diavolumes.
   - Our UF/DF-only case then reproduces their recovery (88.2% vs 88.2%) and their schedule (322 vs 328 batches/yr), and costs $105/kg LF against their $291.
   - The gap sits in unit prices and cost rules: raw materials (glycerol at about $1.8/kg), capital, labour, consumables, utilities and QC.
   - For CEX, the one design input that matters is resin life (their 150 cycles vs our 1,000): **+$69 to +$120/kg LF**.
5. **Three statements in our evidence files are contradicted by the primary source.** They are the "9 fermenters", the "0.837 recovery", and "$262.43 is GFI's normalisation". Details are in §4b.

## 1. Extracted figures

### 1a. Design basis
| Item | As printed (numbers verbatim) | Page (L) |
|---|---|---|
| Host, induction | *Pichia pastoris*; expression induced by methanol; glycerol in the growth phase, methanol in expression; LF secreted | p.4 L164–167; p.5 L210 |
| Titer, time | 10 g/L after 5 days of culture | p.4 L167–168 |
| Phases | Growth 72 h at 1 VVM; expression 48 h at 1.5 VVM; 30 °C, pH 5; 30% w/w aqueous ammonia (also the N source) | p.5 L213–215, L228–232 |
| Main fermenters | **6** staggered 100 m³ fermentors (FR-101a–f); the main fermentation takes a little over 5 days | p.4 L169; p.11 L480–481 |
| As drawn on the flowsheets | FR-101a 100.60 m³, cycle duration 132.58 h (a) / 132.83 h (b); outlet 78.18 m³/batch at 10.03 g/L | flowsheets, PDF pp.38–39 |
| Start volume, inoculum | ~40,000 L at the start of growth; inoculum 5% | p.5 L234–236 |
| Seed train | Working volumes ~5 L, 100 L and 2000 L; 16 h each. Vessels 6.31 L, 126.26 L, 2.53 m³. Seed broth 17.36–17.79 g/L biomass | p.5 L237–238; p.6 L246; PDF p.38 |
| Medium (Table 1) | Glycerol 40 g/L; CaSO₄ 0.93 g/L; H₃PO₄ 2.67% v/v; MgSO₄·7H₂O 14.9 g/L; KOH 4.13 g/L; K₂SO₄ 18.2 g/L | p.5 L217–225 |
| Feeds per batch (both cases) | Glycerol 85%: 18.94 m³; methanol: 4000.00 L; aqueous ammonia: 3.72 m³; basal medium 2X: 18.30 m³ | PDF pp.38–39 |
| Stoichiometry | Eq. 1: 100 glycerol → 40 biomass (95% conversion in the seeds). Eq. 2: 100 methanol → 8 biomass + 32 LF (84% conversion). Cell death 5% | p.6 L260–279 |
| Harvest | ~80 m³ broth, ~10 g/L LF, almost 100 g/L dry biomass | p.6 L281–283 |
| Schedule | One batch every 24 h (recipe cycle time); overall batch time ~9 days | p.7 L299; p.11 L463–466 |
| Output | 251 MT/yr powder (a) and 216 MT/yr (b). Batch 766.17 / 657.17 kg MP. Annual 251,304 / 215,551 kg MP | p.4 L175, L179–180; p.18 |
| Derived | 328 batches/yr (c: 251,304/766.17); 784.1 kg LF made per batch (c: 78.18 × 10.03); 7,872 h/yr (c) | — |

### 1b. Downstream
| Step | As printed | Page (L) |
|---|---|---|
| Cell removal | Two centrifuges: 20 h centrifugation + 95 min CIP per batch. The first underflow is diluted 1:1 (a: with UF permeate; b: with fresh water) and overflow/retentate is recycled. **No whole-broth pre-dilution.** First-centrifuge overflow ~9 g/L LF | p.7 L290–300, L307; p.8 L363–367 |
| Microfiltration, case a | MF/DF: concentrate 10×, diafilter 5 volumes, concentrate 5×. Rejection 1 (biomass), 0.99 (debris), 0 (everything else). Flux 25–35 L/m²/h; 60 m² per unit, 3 units | p.7 L310–314; p.8 L344–350 |
| Microfiltration, case b | Feed-and-bleed, 95% recovery, retentate recycled. 35 L/m²/h, 100 m², 22.86 h + 1 h CIP. Permeate ~8 g/L LF | p.8–9 L368–385, L395 |
| CEX (case b only) — buffers | Equilibration 10 bed volumes (25 mM sodium phosphate, pH 6.5); wash 5 BV (+1.6% NaCl); elution 5 BV (+5% NaCl); regeneration 5 BV (+10% NaCl) | p.9 L401–407 |
| CEX — binding | LF retention 97%; retention of other proteins 5%; binding capacity 100 g/L | p.9 L401–407 |
| CEX — operation | 500 cm/h (SP Sepharose Big Beads); bed 25 cm; bed/column height 0.83; overdesign 1.11; loading 33 min; cycle 108 min | p.10 L420–424 |
| CEX — columns | 4 staggered columns, 200.15 L each | p.10 L426; PDF p.39 |
| CEX — resin (screenshot) | $1000.00/L, life 150 cycles | Fig. 14, p.31 |
| UF/DF | a: concentrate 10×, 5 diavolumes of purified water, then to 100 g/L. b: to 61 g/L, 5 diavolumes, then to 100 g/L. Both: rejection 0.995 (LF), 0.75 (other proteins), 0.50 (other impurities). 100 g/L is called the protein's solubility limit (no citation). Membranes: a 160 m² × 3 units at 10–20 L/m²/h; b 250 m², 8 h cycles, 3 per batch | p.7 L317–321; p.8 L345–346; p.10 L434–437, L444–449 |
| Product | a: 90% LF, 4% other proteins, 5% moisture; 31.9 kg/h. b: 94.7% LF, 0.3% NaCl, 5% moisture; 27.4 kg/h. Flowsheets: 90.28% / 94.67% LF; dryer feed 10.06% / 10.05% LF | p.7 L324–326; p.10 L441–442; PDF pp.38–39 |
| Recoveries (c) | Overall: **88.2% (a)** = 766.17 × 0.9028 / 784.1; **79.3% (b)** = 657.17 × 0.9467 / 784.1. UF/DF from the stated rejection: 96.2% (a), 96.7% (b) (CF^−0.005 · e^−0.025). CEX: 97% (stated). Clarification by difference: ~91.7% (a), ~84.6% (b) | — |

### 1c. Economics
| Item | Case a | Case b | Page (L) |
|---|---|---|---|
| TCI | 122,525,000 $ | 146,623,000 $ | p.18; p.17 L615–616 |
| What TCI includes | Equipment and installation, piping, instrumentation, buildings, engineering; start-up and validation; working capital. SuperPro multipliers "adjusted" to food grade. **Not reported: DFC, equipment cost or list, fermenter cost, Lang factor, start-up and working-capital amounts** | same | p.17 L617–620 |
| Capital added by CEX | Columns plus buffer preparation and holding tanks plus buffer sterile filters; +$24.1M TCI over case a (c) | — | p.17 L627–629 |
| Annual operating cost | 65,950,000 $/yr | 87,718,000 $/yr | p.18–19 |
| Raw materials | 22,303,000 (33.82%) | 24,567,000 (28.01%) | p.19 |
| Labour-dependent | 9,159,000 (13.89%) | 9,389,000 (10.70%) | p.19 |
| Facility-dependent | 20,176,000 (30.59%) | 24,372,000 (27.79%) | p.19 |
| Lab/QC/QA | 2,564,000 (3.89%) | 2,625,000 (2.99%) | p.19 |
| Consumables | 6,560,000 (9.95%) | 20,851,000 (23.77%) | p.19 |
| Waste treatment | 1,425,000 (2.16%) | 2,199,000 (2.51%) | p.19 |
| Utilities | 3,763,000 (5.71%) | 3,714,000 (4.23%) | p.19 |
| Unit production cost | 262.43 $/kg MP | 406.95 $/kg MP | p.18 |
| Selling price assumed | 600 $/kg MP; revenue 150,782,000 $/yr | 1,000 $/kg MP; revenue 215,551,000 $/yr | p.18; p.17 L638–640 |
| Profitability | Gross margin 56.26%; ROI 50.01%; payback 2.00 yr; IRR 37.84%; NPV at 9% 264,712,000 $ | 59.31%; 60.83%; 1.64 yr; 44.86%; 416,556,000 $ | p.18 |
| Unit prices shown in dialog screenshots | Glycerol 85% 1.865329 $/L (Fig. 10, p.27); aqueous waste 10 $/MT (Fig. 11, p.28); electricity 0.1000 $/kWh (Fig. 12, p.29); steam 30 $/MT (Fig. 13, p.30); resin as above (Fig. 14, p.31); electricity use 17,446,922.19 kWh/yr = 1,744,692.22 $/yr (Fig. 16, p.33; case not stated) | | |
| Not reported | Labour hours, operator count, labour rate; itemised raw materials; how consumables split; depreciation basis. No quantified sensitivity analysis, only a qualitative caveat (p.20 L782–786) | | |
| Derived (c) | Facility-dependent = **16.47% (a) / 16.62% (b) of TCI per year**. Lab/QC = **28.0% of labour**. Glycerol ≈ 18,940 L × $1.865329 × 328 = **$11.59M/yr**, 52% of case a's raw materials (about $1.80/kg of pure glycerol, assuming a density of 1.22 kg/L). Glycerol use ≈ 28 kg/kg LF (a); methanol ≈ 4.6 kg/kg LF. Electricity ≈ **77 kWh/kg LF**. Case a membrane consumables ≈ **$9,900 per m² installed per year** (6.56M / 660 m²) | | |

## 2. Side by side

All our runs are the current worktree, US Midwest. Costs are $M/yr with **$/kg LF** in brackets.

| | Intelligen a (UF/DF) | Ours `lf_ufdf_only` PA | Ours `lf_ufdf_only` DR | Intelligen b (CEX) | Ours `lf` PA | Ours `lf` DR |
|---|---|---|---|---|---|---|
| t LF/yr (t powder/yr) | 226.9 (251.3) (c) | 250 (292.4) | same | 204.1 (215.6) (c) | 250 (292.4) | same |
| Production fermenters | 6 × 100 m³ | 3 × 200 m³ | same | 6 × 100 m³ | 4 × 200 m³ | same |
| Broth per batch; batches/yr | 78.18 m³; 328 | 160 m³; 175.4 | same | 78.18 m³; 328 | 160 m³; 210.0 | same |
| LF made per batch | 784.1 kg | 1,600 kg | same | 784.1 kg | 1,600 kg | same |
| LF out per batch (powder) | 691.7 kg (766.17) | 1,425 kg (1,667) | same | 622.1 kg (657.17) | 1,190 kg (1,392) | same |
| Overall recovery | 88.2% (c) | 89.1% | same | 79.3% (c) | 74.4% | same |
| Carbon source per kg LF | ~28 kg glycerol + 4.6 kg methanol (c) | 29.5 kg glucose | same | ~32 + 5.1 (c) | 35.3 kg glucose | same |
| TCI, $M | 122.5 | 87.5 | 71.1 | 146.6 | 133.2 | 109.4 |
| Production fermenters, purchase $M (2025$) | not reported | 3.40 | 3.40 | not reported | 4.54 | 4.54 |
| Total equipment purchase, $M | not reported | 14.8 | 14.9 | not reported | 22.1 | 22.2 |
| Installed resin; price; life | — | — | — | ~0.66 m³ (c); $1000/L; 150 cycles | 4.45 m³; $1250/L; 1000 cycles | same |
| Raw materials | 22.30 (98.3) | 3.63 (14.5) | 3.67 (14.7) | 24.57 (120.4) | 6.76 (27.1) | 6.80 (27.2) |
| Labour | 9.16 (40.4) | 4.18 (16.7), 33.4 FTE | same | 9.39 (46.0) | 4.85 (19.4), 38.7 FTE | same |
| Facility-dependent (ours = maintenance + insurance + TCI/10) | 20.18 (88.9) | 16.62 (66.5) | 8.59 (34.4) | 24.37 (119.4) | 25.31 (101.3) | 13.25 (53.0) |
| Lab/QC/QA | 2.56 (11.3) | 0 | 0 | 2.63 (12.9) | 0 | 0 |
| Consumables (resin + membranes) | 6.56 (28.9) | 0.13 (0.5) | 0.13 (0.5) | 20.85 (102.2), resin ≈ 15.9 (c) | 5.41 (21.7), resin 5.29 | same |
| Waste | 1.43 (6.3) | 1.44 (5.8) | 1.44 (5.8) | 2.20 (10.8) | 1.69 (6.8) | 1.69 (6.8) |
| Utilities | 3.76 (16.6) | 0.70 (2.8) | 0.69 (2.8) | 3.71 (18.2) | 0.79 (3.2) | 0.78 (3.1) |
| **Unit cost / COP, $/kg LF** ($/kg powder) | **290.7 (262.43)** | **106.8 (91.3)** | **74.8 (64.0)** | **429.9 (406.95)** | **179.3 (153.3)** | **131.2 (112.1)** |
| Our MSP_CCF, $/kg LF | — | 122.8 | 87.8 | — | 203.6 | 151.2 |
| Electricity, kWh/kg LF | ~77 (c, Fig. 16) | 30.8 | 30.6 | — | 35.0 | 34.8 |

How I mapped our lines onto SuperPro's categories:
- Raw materials = glucose + ammonia + salts + DSP chemicals + process water.
- Waste = biomass disposal + wastewater.
- Utilities = electricity + gas/steam.
- Our category sums reproduce our COP exactly.

Places where their numbers agree with ours (no change needed):
- Titer 10 g/L.
- Total culture time: our 121 h against their 72 h growth + 48 h expression.
- Final biomass: our 103.8 g/L against their ~100 g/L.
- Turnaround: our 12 h against their 12.6 h (c: 132.58 − 120).
- Operating hours: our 7,920 h against their 7,872 h.

## 3. Causes of the cost difference ($/kg LF, COP, price-anchored capital)

### 3a. CEX route: Intelligen case b ($429.9) vs our `lf` ($179.3). Gap $250.6
**Step 0: their design inputs in our model** (cumulative, all computed; the net is **+$31.6**, giving $210.9 with 6 × 100 m³, 330 batches/yr and 77.3% recovery):
- Adds cost: resin life 150 cycles **+68.9**; clarification like theirs +3.9; 25 buffer volumes per cycle +1.8; 5 diavolumes and $0.10/kWh +1.0.
- Cuts cost: 97% CEX retention −18.1; 20 column volumes/h −16.5; 90 g/L loading −6.1; resin at $1000/L −3.2.
- Scale (204 t, +11.6) and 6 × 100 m³ fermenters (−11.6) cancel.

**Residual after step 0: $219.0**, largest first:
1. **Raw materials +96.7.**
   - Glycerol alone is about $56.8/kg LF against our glucose at $13.6, so about +43.
   - Methanol adds about +4.6, if priced at $0.910/kg as in Intelligen's OVA report; the LF report gives no price.
   - About +49 is not itemised in the report.
2. **Resin replacement: +69 after their other CEX inputs, +120 alone on our base.**
   - Their 150 cycles at $1000/L implies about $15.9M/yr, or $78/kg LF.
   - Working (c): 14,313 cycles/yr × 166 L / 150 cycles. Cycles = 328 batches × 24 h × 60 / 33 min; 166 L = 200.15 L × 0.83.
   - This is consistent with the +$14.3M/yr consumables step from case a to case b. Ours is $21.2/kg LF.
3. **Capital (facility-dependent) +48.6.**
   - At matched design their TCI is 1.93× ours ($146.6M vs $76.1M). At their 16.6%/yr rate that is +58; our higher rate (19%/yr) offsets −9.
   - At our base the TCI gap looks small ($146.6M vs $133.2M) only because our grade-E CEX flow rate (5 CV/h) inflates installed resin by about 6×.
4. **Labour +21.1:** $9.39M against our $5.08M per year.
5. **Consumables other than resin +20.7:** membranes and filter cartridges.
6. **Utilities +14.8.** Their electricity per kg is about 2.4× ours because they aerate at a fixed 1–1.5 VVM. They also buy chilled water and steam, which our model prices as chiller electricity.
7. **Lab/QC/QA +12.9:** 28% of their labour; we have no such line.
8. **Waste +4.2.**

### 3b. UF/DF only: Intelligen case a ($290.7) vs our `lf_ufdf_only` ($106.8). Gap $183.9
Step 0 (their output, 6 × 100 m³, $0.10/kWh, 5 diavolumes) nets **−$1.6**, giving $105.2. Recovery is then 88.2%, equal to theirs. Residual **$185.5**, largest first:
1. **Raw materials +83.6.** Glycerol +39 (51.1 vs 11.9), methanol about +4, about +40 not itemised.
2. **Consumables +28.3.** They spend about $9,900 per installed m² of membrane per year; we spend $90 ($45/m², 6-month life).
3. **Capital +27.8.** TCI is 1.68× ours (+36); our higher rate offsets −8.
4. **Labour +20.8.**
5. **Utilities +13.3.**
6. **Lab/QC/QA +11.3.**
7. **Waste +0.4.**

On design-report capital the capital item grows to +57.6 (case a) and +83.1 (case b). The raw-material, consumables, labour and QC levels are SuperPro-style inputs with no stated basis in the report. They show what a SuperPro-default costing gives; they are not evidence against our sourced values.

## 4. Recommended changes

### 4a. Parameters
Effects are one at a time on our base COP, PA unless noted (c).

| # | Parameter | Current | Proposed | Basis in the report | Effect ($/kg LF) |
|---|---|---|---|---|---|
| 1 | `fermenter.volume_m3` in the lactoferrin `common` block | 200 (from base) | **100** (grade B) | 6 staggered 100 m³ fermentors (p.4 L169; p.11 L480) | −7.8 (`lf`), −9.3 (ufdf). Reproduces their 6 vessels and ~330 batches/yr. Mostly because harvest, hold and media tanks are sized per batch (harvest + hold tanks $5.5M → $2.8M purchase), a model-structure effect |
| 2 | `dsp.cex_flow_cv_per_h` | 5 (grade E, a guess) | **20** (grade B; c: 500 cm/h ÷ 25 cm bed) | p.10 L420–422 | −20.6 PA / −11.2 DR; TCI −$27.2M. **Only together with #3** |
| 3 | New CEX buffer-system capital (prep/hold tanks, sterile filters) | absent | add | p.17 L627–629. Their CEX adds +$24.1M TCI (c); their case b flowsheet shows tanks of 10.3–24.4 m³ and filters of 10/20 m² | With #2 alone our CEX would add only ~$9M TCI (c); today it adds ~$36M through the resin guess |
| 4 | `dsp.cex_recovery` high end | 0.95 (judgment) | **0.97** (B) | LF retention 97% (p.9 L403) | base unchanged |
| 5 | `dsp.diafiltration_volumes` (LF override) and `dsp.cex_diafiltration_volumes` | 3 (D) and 4 (D) | 5 and 5 (B) | 5 diavolumes (p.7 L318–319; p.10 L435) | +0.7 each |
| 6 | `dsp.dryer_feed_solids_lf` low end, or record `solubility_practical_g_L` | low 0.20; solubility null | low **0.10** | 100 g/L called the solubility limit (p.7 L319–320; p.10 L436), no citation; dryer feed ~10.6% solids (c, flowsheets) | at 0.10: +1.1 (`lf`), +1.5 (ufdf) |
| 7 | `lf_ufdf_only` purity (`dsp.concentrate_target_frac_dry`) | 0.90 on a dry basis = 85.5% LF in the powder | 0.947 to mirror case a (90% LF as sold), or relabel the variant | p.7 L324–325 | 0 per kg LF; changes $/kg powder |
| 8 | Source for `strain.titer_g_L` 10 | David 2026 | cite the primary source, p.4 L167–168, and note that it is a **methanol-induced** design (p.4 L165) that our methanol-free case borrows | — | — |
| 9 | `dsp.dilution_to_g_L_cells` for LF | 45 (from the OVA report) | keep; flag it and run 80 g/L as a sensitivity | The LF design does not pre-dilute (p.7 L292–294; liquor 9 g/L at L307, 8 g/L at p.9 L395; ours 2.92 g/L) | At 80 g/L we reproduce their 84.6% clarification and a 7.0 g/L CEX feed: −6.7 (`lf`), +7.0 (ufdf) |

**Keep ours (do not adopt):**
- **Resin life 150** (Fig. 14): our 1,000 cycles is grade A (Pires 2025), and our low of 125 already covers theirs. Adopting 150 would add +120.
- **Resin price $1000/L:** optional; −5.1.
- **Binding capacity 100 g/L:** already our high end.
- **25 buffer volumes per cycle:** could become the high end; +6.9 if used as base.
- **Glycerol + methanol medium:** not adopted; we model a methanol-free process as in GRN 1219/1284.
- **$0.10/kWh:** ours is the EIA 2025 average (grade A).
- **Their labour, consumables and utilities levels:** no stated basis.

**Decision for Pablo:** add a Lab/QC/QA line (28% of labour, derived from Tables 4–5) in the design-report convention? That would add +4.7 (ufdf) / +5.4 (`lf`) per kg LF.

### 4b. Evidence corrections
1. **`data/evidence/lactoferrin.yaml` `lf_intelligen_derived_checks` is contradicted by the report:**
   - Fermenters: 9 → **6**. The 216 h used to get 9 vessels is the ~9-day *batch* time (p.11 L463); a fermenter's cycle is 132.58 h.
   - Broth: 82.3 → **78.18 m³**.
   - Recovery: 0.837 → **0.882 (a) / 0.793 (b)**.
   - The base case uses **glycerol** (Table 1), not glucose. David 2026's glycerol column (784.7 kg/batch) matches the flowsheet's 784.1; his glucose column is his own variant.
2. **`lf_cost_intelligen2024_via_gfi2025` and the note in `blf_price_range_gfi2025`:**
   - $262.43 is Intelligen's own figure, per kg of powder, at 2024 prices. It is not a GFI normalisation.
   - $292 = 262.43/0.90 (c).
   - The note "Intelligen's own report is not on disk" is out of date.
3. **`data/pf/benchmarks.yaml` comparators:** add case b, $406.95/kg powder = $430/kg LF, as the comparator for our CEX route.
4. **`data/evidence/dsp.yaml` `iex_lactoferrin_output_with_cex_intelligen`:** 213/249 t (older web page) → 216/251 MT (p.4).
5. **`fermenter.seed_final_X_g_L` 60 (grade D):** their seed broth is 17.4–17.8 g/L, so X0 ≈ 0.9 g/L. For LF this adds +6.5 (ufdf, a fourth vessel) and 0 (`lf`). Record as evidence; don't change the base, which also sets BLG and OVA.
6. **Review SC-6's "capital is similar"** holds only at our base, and only because of the grade-E CEX flow rate. At their design inputs their TCI is 1.7× (a) and 1.9× (b) ours.

## 5. Pricing
- **Market price.** The report says bovine LF is "currently selling for US$ 600-2000 per kilogram" (p.3 L113–114). It cites a TurtleTree web page, ref [14], accessed June 2024.
  - TurtleTree sells precision-fermented LF and is already the source of the $750–1,500 point in our band, so this is not independent.
  - If added (grade C, flagged as an interested party), it would raise the top of our nominal band from $1,500 to $2,000/kg.
- **Selling prices assumed** (p.17 L638–640; Tables 2–3): $600/kg for the 90% case a powder and $1,000/kg for the 94.7% case b powder, which they position for infant formula. These are assumptions, not market data, but they imply a purity premium of about $400/kg.
  - Our powder is 85.5% LF as sold, below both of their products. Which price tier it would earn is thinly evidenced.
- **Market size.** More than 600 MT/yr (their inference from Westland's ~10% share after tripling from 20 MT).
  - Capacity moves: Morinaga to 170 MT/yr (€15M); FrieslandCampina from 20 to 80 MT (€80M); Westland NZ$70M.
  - Infant formula is 61–80% of use; growth 15.7%/yr for 2024–29, from market-research reports (all p.3).
  - All of this sits inside our 0.3–1.6 kt/yr range. One 250 t/yr plant would be about 40% of a 600 t market (c), so it would move the price.

## 6. Could not verify
- **Capital detail.** Their equipment list and costs, DFC, Lang factor or multipliers, start-up and working-capital amounts, and depreciation basis are not reported. So I cannot split the 1.7–1.9× capital gap into equipment versus factors.
- **Labour detail.** No hours, operator count or rate.
- **Raw-material itemisation.**
  - The glycerol price comes from a dialog screenshot in the emissions-modelling section (Fig. 10). Its CO₂ factor, 1.7 = 0.85 × 2.0 from Table 6, suggests it is from this model, but the report does not say so.
  - I assumed the methanol price ($0.910/kg, from the OVA report).
  - About $40–49/kg LF remains unexplained. At the OVA report's unit prices, the visible flows would not reach it (rough estimate).
- **Resin screenshot (Fig. 14).** Its CO₂ factor (3,200 kg/m³) differs from Table 6 (4,500 kg CO₂eq/m³ for ion-exchange resin), so it may predate the final model. Its $1000/L and 150 cycles are consistent with the +$14.3M/yr consumables step.
- **Fig. 16 (17.45 GWh/yr).** The case is not stated; it fits case a's emissions electricity share better than case b's.
- **Clarification step recoveries** are by difference; the rounded stream tags carry about ±2 points.
- **The August 2024 version** that GFI cited was not read. GFI's appendix row equals Table 2 exactly, so the economics probably did not change.
- **The 100 g/L solubility** is asserted without a citation.
- **David 2026** was not read; everything about it comes from our evidence file.
