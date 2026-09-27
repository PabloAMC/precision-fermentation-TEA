<!-- Simulated review. Written by an AI model (Claude) instructed to review as a bioprocess engineer (enzyme/dairy industry).
It is not the opinion of any person and has not been checked by one. Kept verbatim (local file paths redacted) as delivered on
2026-09-27 against commit 5cbf9bc; responses and changes are in docs/REVIEW.md (AI pre-review log). -->

> **Simulated AI review (BE): bioprocess engineer (enzyme/dairy industry).** Not a human expert's opinion. Verbatim; line and page
> references are to commit 5cbf9bc (v2). Responses: [docs/REVIEW.md](../REVIEW.md#ai-pre-review-phase-f).

# Simulated AI review: Reviewer B (bioprocess engineer, industrial-enzyme and dairy plant design and estimating)

*This is a simulated review by an AI (Claude), not a human expert.* I recomputed every number below on branch `audit-fixes`. The base case reproduces MSP_CCF $29.3694, TCI $847.7M, 33 × 200 m³ fermenters and 121.75 FTE. My scratch scripts are in `<scratch>/review/be/` (for example `anchor_test.py`, `decomp.py`, `ceil2.py`, `heat_div.py`, `intel.py`, `vout.py`). Nothing in the repo was written; `git status` is clean and the `.pyc` files are older than my runs.

**Bottom line.** The plant model is arithmetically sound and unusually transparent. Three problems carry the headline:
1. The "price-anchored" base prices each fermenter at 3.2× the vessel cost the baker's-yeast anchor used. The anchor therefore does not support the base; it supports vendor-quote-level vessel prices.
2. The "50 wt% glucose feed" behind the 74 g/L ceiling is really 500 g/L (≈42 wt%). A real 50 wt% feed lifts the 72 h ceiling to ~115 g/L and makes $10/kg reachable with price-anchored capital.
3. The fixed-cost rule, 9% of TCI per year labelled "maintenance, insurance and local tax", is high, has no range, and is hidden inside the capital-convention bar.

Applying all my suggestions, I get ≈$24/kg for base BLG (plausible range $21–28; confidence ~50%). That compares with $29.4 on the price-anchored basis and $16.1 on the design-report basis.

---

## Comments (most severe first)

### BE-1: major, unsupported/overclaimed. "Price-anchored" does not cover the fermenter cost, the item that drives the headline
**Where:**
- Report: Summary p.1 ("capital estimate tied to the market price of baker's yeast"), §2.5 p.6–7, §3 p.9 ("the only convention tied to a real product price"), §5.2 p.18.
- `docs/VALIDATION.md:76–79, 157–159, 171–172`.
- `src/pftea/equipment.py:21–22, 42–47`; `src/pftea/plant.py:303–305`; `src/pftea/humbird_yeast.py:174–176, 188–190, 232–233`.
- `data/calibration/humbird_bakers_yeast.yaml:32, 52–53, 91–92`.

**Comment.** The capital elements that make the base expensive are not the ones Humbird's A.1 used when it reproduced the baker's-yeast price.

| Element | A.1 (the anchor) | PF base |
|---|---|---|
| Production vessel (~200 m³, 2018$) | ACCE bubble column, $0.78M (Equip!BT6) | ACCE STRFERM, $2.50M (3.2×) |
| Factor method | Single Lang factor 4.5 on PEC, 20% missing allowance | 4FB facility-class method, 10% missing allowance |
| Capital charge | 10% over 20 yr (CCF 11.7%/yr) | 7.5% over 10 yr (14.6%/yr) |
| Fixed costs | 9% of TCI | 9% of TCI |

Only the 9% fixed-cost rule is shared.

Installed at 1.111 × 2.4, each PF fermenter has a direct cost of $6.66M (2018$). That is numerically Humbird's *installed ASME-BPE aseptic cell-culture bioreactor* at 200 m³ ($6.8M; Humbird 2021 Table 3.3, where bare cost is $2.4M). Fermenters (production plus seed) are 69% of PEC.

AUDIT R7-Q6 kept the name with a caveat about Humbird's assumed 33% margin. That fix is incomplete: the bigger weakness is that the configuration which was anchored is not the one the base uses.

**What I checked.**
- Humbird SI, Equip sheet rows 6 and 30 ("316SS Bioreactors, From ACCE V10"):
  - BCR 200,000: 198.7 m³, $717,200 (2016$) = $779k (2018$).
  - STRFERM 200,000: 196.5 m³, $2,269,500 (2016$) = $2.466M (2018$).
- Re-ran the A.1 port with swaps:

  | A.1 variant | Baker's-yeast cost |
  |---|---|
  | As published | $1.890/kg |
  | STRFERM production vessels | $2.582/kg (+37%) |
  | STRFERM plus the PF CCF (7.5%/10 yr) | $2.789/kg: the top of the $2.20–2.80 wholesale range, i.e. zero margin |
  | NREL's vendor quote scaled to 199 m³ ($0.85M) | $1.918/kg (+1.5%) |

- NREL's quote is a real vendor quote: a 300 m³ 316SS vessel from Mueller with internal cooling coils, plus an 800 hp agitator from Lotus (NREL 2011 §3.4.3, Table 19). That exceeds the ~150 kW the model's own aeration optimum needs at OUR 150.
- Independent anchors, re-run with NREL's quote escalated by the heavy-gauge-tank PPI:
  - Intelligen: TCI $118M versus their $92M (it is $147M with STRFERM); cost $42.68/kg powder versus $43.52 (+13.7% with STRFERM).
  - Voutilainen: TCI €141M versus their €128M FCI (+10%; +59% with STRFERM).
- Decomposition of the gap between the conventions ($29.37 → $16.06):

  | Step | Change in $/kg | Share of gap |
  |---|---|---|
  | Fermenter quote | −$8.05 | 60% |
  | Installation and indirect factors | −$2.36 | 18% |
  | Fixed-cost rules | −$2.90 | 22% |

**Suggested fix.** Rename the STRFERM-based estimate "ACCE-based (conservative)" and keep it as the high case. Make the central case a vendor-quote fermenter escalated with a vessel index (BE-5). Either use A.1's CCF or state the change.

Effects, with Humbird factors and 9% fixed costs unless noted:

| Case | Now | With vendor quote |
|---|---|---|
| Base BLG, quote × CEPCI | $29.37 | $21.3 |
| Base BLG, quote × vessel PPI | $29.37 | $23.2 |
| Base OVA, quote × vessel PPI | $29.45 | $23.3 |
| Industry case, 42 g/L | $21.9 | $17.4 |
| Physical-limit floor | $6.11 | $5.07 |

CCF 10%/20 yr alone moves the base from $29.37 to $26.98.

### BE-2: major, error. The glucose feed is mislabelled, and the ceiling and the "$10/kg not reachable" claim depend on it
**Where:**
- Report: Summary item 1 p.1; §2.3 p.5 ("glucose as 50 wt% solution"); §4.4 p.13–14 (Table 6 "$10/kg price-anchored: —" at every production time; Table 7 row "glucose feed 65 wt%"); §5.5 and §6 p.19.
- Memo bullet 4 and "What $20/kg requires".
- `report/pf_tea_report.typ:158, 374, 809–810, 828, 1090, 1105`; `report/memo.typ:57`; `data/pf/base.yaml:91`; `scripts/run_analyses.py:198`.

**Comment.** The model tracks volume at 1 kg/L, so feed_glucose_wt 0.5 means 500 g/L. That is ≈42 wt% (AUDIT R6-M2), not 50 wt%. A real 50 wt% solution holds ≈615 g/L, 65 wt% ≈850 g/L and 70 wt% DE95 syrup ≈940 g/L (CRC Handbook densities, ±2%; confidence 85%). The Table 7 row "65 wt%" is 650 g/L, about 52 wt%.

R6-M2 was only "documented"; the report text now states the ceiling in wt%, so the fix is incomplete. Concentrated feeds are normal practice:
- Shemesh 2024 (in the repo, the source of X_max) fed "a 60% dextrose solution" to K. phaffii.
- Impossible US 9,938,327 feeds 850 g/L glycerol.
- DE95 syrup arrives at ~70% dry solids and is stored warm.

**What I checked.** Ceiling at 72 h (`max_feasible_titer`):

| Feed | 72 h ceiling | What binds |
|---|---|---|
| 500 g/L (model base) | 74.3 g/L | Minimum fill |
| 615 g/L (real 50 wt%) | 115 g/L | Minimum fill |
| 615 g/L with ammonia at its real density | 112 g/L | Minimum fill |
| 650 g/L (reproduces Table 7) | 126.7 g/L | Minimum fill |
| 850 g/L (real 65 wt%) | 170 g/L | Secretion ceiling |

- $10/kg with price-anchored capital at 615 g/L:
  - Reachable at 36 h (92.8 g/L, q_p 36.5 mg/g/h) and 48 h (104 g/L, q_p 32.9). Both are 7–8× Intelligen's q_p.
  - Not reachable at 72–96 h ($10.10 and $11.24 at the ceiling).
- At 850 g/L, $10/kg is reachable at 36–96 h (98–138 g/L).
- The base at 30 g/L barely moves: $29.37 → $29.80 at 615 g/L, because more cells are carried per batch.
- Physical limit at its optimum (80 g/L cells, 72 h), with a 650–700 g/L feed: ceiling 133–137 g/L, floor $6.11 → $5.78–5.71 (not re-optimised).

**Suggested fix.**
- Write "500 g/L (≈42 wt%, Intelligen)" everywhere and express the feed in g/L.
- Report the ceiling at a real 50–70 wt% feed; use that for the physical limit.
- Revise "$10/kg is not reachable with price-anchored capital" in the memo, §4.4 and §5.1 Q3.
- Also minor: 30% aqueous ammonia is also counted at 1 kg/L; its real density is 0.89, so the model understates its volume by 11%.

### BE-3: major, judgment call and mislabel. Fixed costs of 9% of TCI
**Where:** §2.5 p.7; Table 5 p.9; §5.2 p.18; `data/pf/base.yaml:274–275`; `src/pftea/plant.py:443–445`.

**Comment.**
- Humbird (2021) takes *insurance* alone as 5% of TCI per year. Relabelled as "insurance plus local tax", it is still 2–5× typical values: insurance 0.4–1% of FCI, local taxes 1–4% (Peters, Timmerhaus & West, *Plant Design and Economics for Chemical Engineers*, 5th ed., 2003, ch. 6; confidence 75% on the ranges). It is only defensible as a catch-all for plant overhead, which the model otherwise lacks.
- It costs $7.63/kg (26% of MSP).
- It has no range, so it is not in the tornado or the Monte Carlo.
- It sits inside the capital-convention bar, so readers cannot see that 22% of the 1.8× gap between conventions is a fixed-cost rule rather than capital.
- For comparison:
  - Intelligen's SuperPro run carries roughly 10% of DFC per year in non-depreciation facility costs. That is my back-calculation from 44% of $39.0M opex, assuming 10-year straight-line depreciation on ≈$86M DFC; the depreciation rule is my assumption.
  - NREL's rule (1.85% of TCI here) omits property tax and overhead.
- Humbird's 4% maintenance "includes CIP chemicals", which the model also costs separately: a $0.17/kg double count.

**What I checked.**
- Maintenance 3.5% plus insurance/tax 2.5% (6% total): $26.83 (−$2.54). 5% total: $25.98.
- The same 6% rule applied to both conventions: $26.83 versus $17.74, a ratio of 1.51 instead of 1.83.
- `params.bounds()` returns None for maintenance_frac_tci, insurance_tax_frac_tci, ccf_rate and missing_frac.

**Suggested fix.** Split the charge into maintenance, insurance, local tax and plant overhead (the last as a percentage of labour). Use the same rule in both conventions. Grade it with a range (total about 5–10%) and put it in the tornado. Effect at 6%: about −$2.5/kg.

### BE-4: minor, judgment call (pushes costs up). The equipment list is short; the 10% missing allowance is low
**Where:** §2.5 p.6; `src/pftea/plant.py:305–345`; `data/pf/base.yaml:256`.

**Comment.** Humbird's own 4FB list, the source of the facility classes and the 10% allowance, includes items the PF port omits:
- CIP tanks (4FB-020 row 222: 12 × 42 m³).
- A dedicated feed tank per bioreactor (row 209).
- Sterile filter housings (row 210). `equipment.filter_housing` exists but is never used.

Also missing:
- A glucose tank farm (~300 t/day).
- Sterile feed distribution.
- Coils or external heat-exchange loops on the fermenters (BE-6).
- Inactivation and dewatering of the GM biomass (~500–700 t/day wet).
- Powder handling and packing.
- Pretreatment of ~5,000–7,000 m³/day of effluent.

The whole plant has three 77 m³ media and feed tanks. A.1 uses a 20% allowance on its abbreviated list.

**What I checked.** Listed PEC is $164.5M (2025$); the allowance adds $18.3M. My estimate of the unlisted items is $25–50M PEC (judgment, confidence 50%). With missing_frac 0.2 the base goes from $29.37 to $31.58, and the design-report case from $16.06 to $16.73.

**Suggested fix.** List the main items, or use 20% with a range of 10–25%.

### BE-5: minor, judgment call (pushes costs up). Escalation index for the vessels
**Where:** §2.5 p.6; `data/pf/base.yaml:237–238`; tornado §4.3 p.12.

**Comment.** Fermenters are 69% of PEC but are escalated with composite CEPCI (1.33 for 2018→2025). The repo's BLS index for heavy-gauge metal tanks (PCU332420332420, in `prices.yaml`) gives 1.92, and the tornado range (1.23–1.52) excludes it. CEPCI's heat-exchangers-and-tanks sub-index would be the natural alternative.

**What I checked.** STRFERM × 1.92 gives $34.84. The vendor quote × 1.92 gives $23.21. This index is why my central is ~$23 rather than ~$21.

**Suggested fix.** Escalate vessels with a vessel index, or widen the range for the fermenter share.

### BE-6: minor, error (sizing inconsistency). The heat-removal chain
**Where:** `src/pftea/plant.py:284–285, 338–341`; `data/pf/base.yaml:87–88`; REVIEW.md B6.

**Comment.**
- Chillers are sized as if all 29.2 online fermenters sat at their growth peak at once: 29.2 × 2,679 kW = 78 MW, as 7 units.
- With batch starts every 3.4 h, the coincident plant load is only 24.8 MW on average and 25.8 MW at peak.
- AUDIT R3-F9 fixed the per-vessel peak but kept this non-coincident sum, so that fix is incomplete. Air compressors are sized the same way.
- Conversely, no heat-transfer hardware on the fermenters is costed. STRFERM is a jacketed vessel. base.yaml says external exchangers are needed, and at the physical limit (400 m³, 36 kW/m³ peak) they certainly are. NREL's quote includes internal coils.

**What I checked.** I superposed the batch heat profile (`keep_series`) at the model's start interval.
- Resizing chillers to 1.25 × the coincident peak (3 units of 10.8 MW) saves $7.7M PEC, $33M TCI, $0.78/kg.
- Coils or loops at ~$0.2M per vessel (judgment) add about $30M TCI, ~$0.7/kg.
- The net is about zero, but each line is wrong on its own.

**Suggested fix.** Size chillers and compressors on the coincident staggered peak plus a margin, and add a heat-transfer item per fermenter.

### BE-7: minor, overclaimed or judgment. O2 transfer and aeration power
**Where:** §2.3 p.5–6 ("aeration physics alone would allow about 376"); `data/pf/base.yaml:82–84`; `data/pf/scenarios/physical_limit.yaml` (the "head pressure" justification).

**Comment.**
- The power-optimal aeration at OUR 150 is 0.53 vvm and 952 W/m³ (152 kW), with superficial gas velocity 0.056 m/s. It rests on van 't Riet's non-coalescing correlation, which was fitted on far smaller vessels and water-like liquids.
- In a yeast broth at ~100 g/L dry cells (≈33% wet cells by volume, with antifoam), I would expect 2–3 kW/m³ and about 1 vvm at OUR 150 with air. Sources: Garcia-Ochoa & Gomez, "Bioreactor scale-up and oxygen transfer rate in microbial processes: an overview", Biotechnol Adv 2009 (confidence 80%); on antifoams lowering kLa, Routledge, Comput Struct Biotechnol J 2012 (confidence 70%).
- "376" should not be presented as a physical limit.
- I agree with the per-m³-of-broth basis (AUDIT R2-1 is not re-raised). I would still design to 100–120 mmol/L/h with air, and treat 150 as needing 1–1.5 barg head pressure or O2 enrichment.
- The physical limit's cap of 250 cites head pressure, but p_back stays at 1.33 bar, so neither the pressure nor O2 enrichment is costed.

**What I checked.** OTR limit: 186 with the heat ceiling, 376 without. MSP under alternative O2 limits:

| O2 limit | MSP | Notes |
|---|---|---|
| 150 per m³ broth (base) | $29.37 | |
| Cap per cell-free liquid | $30.95 | 37 fermenters, growth phase 40.8 h |
| Cap 120 | $30.16 | |
| Cap 100 | $32.11 | |
| kLa × 0.5 | $29.71 | |

**Suggested fix.** A central cap of 120 (range 100–150), or keep 150 and cost the pressure. Effect: +$0.8/kg.

### BE-8: minor, judgment call (audit fixes incomplete). Membranes and dryer
**Where:** §2.4 p.6; `data/pf/base.yaml:127, 176–177, 190–191`; `src/pftea/plant.py:323–325`.

**Comment.**
- **Diafiltration flux.** The only diafiltration flux on file (EVERY US 2025/0134130, Table 8) is 5 ± 2 L/m²/h at 10 ± 5 °C, measured while diafiltering a *resolubilised ammonium-sulfate precipitate* at ~50 g/L. The model applies it to a clarified broth and to the whole final concentration, where it sizes 85% of the 24,279 m² of UF area (R3-F2 follow-up).
- **Membrane skid cost ($263/m²).** Mercier-Bouchard's figure is labelled "Installation capital investment", which the P-1 evidence note itself calls probably installed. The model multiplies it by the full ISBL chain (×4.6), so installation is counted twice.
- **No CIP downtime.** Membrane and centrifuge sizing assumes 7,920 h/yr of filtration with no cleaning downtime.
- **Dryer high case.** The high end divides a turnkey dairy dryer price by the full TCI/PEC factor of 4.6, which includes buildings and E&C, so even the high end is low.

**What I checked.**
- Diafiltration at 10 L/m²/h: −$0.48; at 15: −$0.64.
- Skid at $110/m² ($263 ÷ 2.4): −$0.69. Both changes together: −$0.94.
- 80% uptime: +$0.36. OVA results are similar.

**Suggested fix.** Split the fluxes: diafiltration at 10 L/m²/h (range 5–20), final concentration at 5. Treat the skid as installed. Add ~15–20% CIP downtime. Net about −$0.5/kg.

### BE-9: minor, error (inconsistency; P-5 fix incomplete). Spent-cell disposal
**Where:** §2.4 p.6; `data/pf/base.yaml:212–213`; `src/pftea/plant.py:184–186`.

**Comment.**
- The fee is converted at 20% dry solids, but the model's own centrifuge paste is ≈15% (300 kg dry per m³ of wet cells × 0.5).
- Neither a decanter nor inactivation is costed.
- At 35 kt dry matter per year, landfill is also an unlikely central route; large producers send inactivated biomass to fertiliser or biogas.

**What I checked.** $62.28 per short ton ÷ 0.9072 ÷ 0.2 = $343/t dry, so the arithmetic is right. At 15% solids ($458/t): +$0.40/kg. At zero cost: −$1.20/kg.

**Suggested fix.** Cost dewatering and inactivation, or use 15%. Make the digestion or fertiliser route ($0–160/t dry) central and landfill the high case.

### BE-10: minor, missing items. Labour and plant overhead
**Where:** §2.6 p.7; `data/pf/base.yaml:220–234`.

**Comment.**
- Humbird's attention model counts shift operators and supervisors only: 121.75 FTE, or 12.2 per kt/yr.
- A 10 kt/yr food-ingredient plant also has 30–60 salaried staff: management, QA/QC, engineering, EHS, logistics. The exception is if the 5% "insurance" in BE-3 is meant to cover them, in which case say so.
- Per-lot release testing and packaging are also absent; by my judgment they add $0.1–0.3/kg.

**What I checked.** The labour arithmetic is right: (24.6 operators + 2.46 supervisors × 1.4) × 4.5 shifts × $60,430 × 2 = $15.25M. Doubling the burden adds $0.76/kg.

**Suggested fix.** Add an overhead line at 50–70% of operating labour (Peters et al.) and a QC and packaging line: about +$0.8–1.1/kg.

### BE-11: minor, missing items. Start-up, working capital and batch failures
**Where:** §2.6 p.7; `src/pftea/plant.py:450–454`.

**Comment.** MSP_CCF excludes three items that a plant estimate would normally carry:
- Start-up and commissioning: Intelligen and Petrides use 5% of DFC.
- Working capital: it appears only in the DCF.
- Contaminated or failed batches: 1–3% is normal at scale.

**What I checked.**

| Item | Effect on base |
|---|---|
| Start-up (5% × TCI × CCF) | +$0.62/kg |
| Working capital (5% of TCI carried at 7.5%) | +$0.32/kg |
| 2% failed batches (0.98 × operating days, which buys a 34th vessel, plus 2% of variable cost) | +$0.67/kg |
| **Total** | **≈+$1.6/kg** |

**Suggested fix.** Add these three costs, or state them as exclusions next to the headline number.

### BE-12: minor, error in the rationale for a guessed (grade E) parameter. Lactoferrin ion-exchange cycle time
**Where:** §4.9 p.17; `data/pf/base.yaml:146–147`; `src/pftea/plant.py:196, 332–334`.

**Comment.** The 3.5 h cycle assumes "16 buffer + ~1.5 load" column volumes. But the column sits between microfiltration and UF, so it is loaded with dilute microfiltered broth: about 26 column volumes per cycle. At the guess's own 5 column volumes per hour, that is ~8 h per cycle. At 2.9 g/L and the medium's conductivity, a binding capacity of 75 g/L (a patent design statement) is also optimistic.

**What I checked.** Per batch: 518 m³ loaded, 1,511 kg lactoferrin (2.92 g/L), 20.2 m³ of resin-cycles, 25.7 column volumes per cycle. A cycle of 8 h raises the lactoferrin MSP from $215.9 to $232.6 (+8%); 12 h gives $247.5.

**Suggested fix.** Put UF before the column (concentrate ~10× and adjust conductivity), or load at big-bead flow rates (≥15 column volumes per hour). Either way, recompute the cycle. The conclusion still holds.

### BE-13: editorial. The convention ratios are mixed up
**Where:** Summary item 3 p.1; §3 p.8; `docs/REVIEW.md:52–53`; `docs/VALIDATION.md:165`; memo ("1.8×").

**Comment.**
- Within the model, the two conventions differ by 1.83× (base BLG), 1.87× (NREL anchor) and 1.97× (Voutilainen).
- The 2.4–2.5× figure is our model versus the published designs; even with their conventions, +23% to +36% of that gap remains.
- REVIEW.md B1 is therefore wrong to say the base "gives costs about 2.4–2.5× the NREL-style convention".
- The Lang factor is given as ~5.1 in REVIEW, 5.2 in the report and 5.15 in the model.
- "External exchangers above ~114 m³" (REVIEW B6) comes from Gregory & Green's statement about a *jacket alone*, not a jacket plus coils.

**Suggested fix.** Use 1.8× when comparing conventions, and 2.4–2.5× only for the model versus publications. State that about 1.25–1.35× of it is not convention.

---

## Answers to REVIEW.md section B (my judgment)

- **B1. Capital conventions.** Neither is right as implemented.
  - *Building the plant:* TCI/PEC ≈5 on a complete equipment list is realistic for a US greenfield food-grade plant. Humbird's factor chain (ISBL 2.4, E&C 50%, fees and contingency 15%) is conventional. The errors are the fermenter PEC basis (BE-1) and the short list (BE-4).
  - *Running it:* 9% of TCI is high unless it includes overhead, and NREL's ~1.9% is too low. I would use ~5–6% plus an overhead line.
  - My central is ≈$24/kg; my estimate is that design-report capital ($16.1) is too low (confidence 70%) and $29.4 somewhat high (60%).
- **B2. Fermenters.** Closer to NREL's vendor quote than to ACCE STRFERM. NREL × CEPCI is probably 20–40% low for 2025: stainless prices rose, Table 19 gives 1 atm operating pressure, and SIP rating is not stated. My range for a 200 m³ 316L SIP-rated production fermenter with a 1–1.5 MW drive and coils is $1.5–2.5M purchased (2025$), against $1.14M (NREL) and $3.32M (STRFERM). Humbird's own ACCE run prices a 199 m³ 316SS bubble column at $0.78M (2018$). Confidence 50–55%.
- **B3. O2 transfer.** Quoting per m³ of broth is the industry convention. I would design to 100–120 mmol/L/h with air at ~100 g/L dry cells, and 150–200 only with 1–2 barg head pressure or O2 enrichment at 2–3 kW/m³. Cost effect +$0.8 to +$1.6/kg. Confidence 60%.
- **B4. Diafiltration.** For whey-protein UF at 45–50 °C with 10 kDa PES spirals, I would expect ~10–20 L/m²/h at ~5% protein and ~5–10 near 25% solids. Cold operation roughly halves that (Cheryan, *Ultrafiltration and Microfiltration Handbook*, 1998, has whey data; confidence 60%). So 5 is conservative for diafiltration and about right for final concentration. Leverage is small (−$0.5/kg).
- **B5. Dryer feed.** The right direction: dairy concentrates above 60% protein are dried from membrane retentate, not evaporated. WPC80 and WPI retentates are commonly 20–25% solids, up to ~30% with high-concentration UF, so 30% for BLG is the upper end (25% is a safer central). 23% for OVA fits egg-white practice. Leverage ≈$0.1/kg. Confidence 65%.
- **B6. Heat removal.** 25 kW/m³ is a reasonable ceiling at 200 m³ with a jacket plus internal coils or tube baffles on 5–8 °C chilled water. My estimate: ~150 m² of jacket at U ≈ 0.5 plus ~100 m² of baffles at U ≈ 1 kW/m²K, with ΔT ≈ 20 K, removes ~3.5 MW, ≈22 kW/m³. External loops are needed above that and at 400 m³. The base peaks at 21 kW/m³, so it is fine, but cost the hardware and fix the chiller sizing (BE-6). Confidence 60%.
- **B7. Labour, cleaning and spent cells.** None is off by a large cost factor.
  - Operator numbers look right; salaried staff are missing (BE-10).
  - Cleaning at 7.3 kg/kg, scaled from a 1 kt/yr, five-fermenter plant, is probably 2–4× low for 33 fermenters and 31,000 m² of membrane. It is cost-trivial: tripling it adds $0.39/kg.
  - Disposal at $343/t dry is a defensible US landfill figure but inconsistent with the model's own paste solids (BE-9).
  - Confidence 60%.

## Checked and found correct
- **Base case:**
  - MSP_CCF $29.3694, COP $25.50, MSP_DCF $28.51 (consistent with the capital charge), TCI $847.7M, effective Lang factor 5.15.
  - 33 × 200 m³ fermenters, 111.5 h cycle, 4,299 kg per batch.
  - Capital charge factor at 7.5% over 10 years = 0.14569.
- **Capital chain:** matches Humbird's Equip facility-class table (ISBL 1.4, OSBL 1.25, E&C 0.5, fees and contingency 0.15, bioreactor install factor 1).
  - STRFERM coefficients match Equip!BN23:BT30, and the 0.69 exponent matches Equip!BM74.
  - Items are escalated once, and the location factor is applied to TCI in both conventions.
  - The NREL quote goes $0.987M (2007$) → $1.133M (2018$), giving 2.9× at 300 m³.
- **Downstream arithmetic:** the paste-loss factor is 0.176, so recovery through the two centrifuge stages is 0.969. Membrane areas are 6,883 m² (microfiltration) and 24,279 m² (UF). UF retention is 0.967, overall recovery 0.896. Dryer inlet solids are 29.3%, one dryer evaporating 3,656 kg/h of water.
- **Fermenter physics:** OUR is capped at 150; peak heat is 21.4 kW/m³ against a ceiling of 25; the heat-limited OTR is 186; superficial gas velocity is 0.056 m/s against a limit of 0.10.
- **Seed train:** 11 units per stage, consistent with a 3.4 h start interval.
- **Utilities, all conservative and documented:** the compressor formula (≈1.6× too high) and the chiller COP of 3.8.
- **Other checks:**
  - Steam priced from natural gas, and the sterilisation steam load, are reasonable.
  - The disposal arithmetic is correct.
  - The EU location factor of 1.09 is plausible.
- **Calibration anchors:** they are honest checks. Misses of +154%, +143% and +13.7% are recorded and diagnosed, not tuned away, and the by-construction matches are disclosed. The one gap is the scope of anchor 1 (BE-1).
