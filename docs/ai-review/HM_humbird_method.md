<!-- Simulated review. Written by an AI model (Claude) instructed to review as a the method's author's perspective (not David Humbird's opinion).
It is not the opinion of any person and has not been checked by one. Kept verbatim (local file paths redacted) as delivered on
2026-09-27 against commit 5cbf9bc; responses and changes are in docs/REVIEW.md (AI pre-review log). -->

> **Simulated AI review (HM): the method's author's perspective (not David Humbird's opinion).** Not a human expert's opinion. Verbatim; line and page
> references are to commit 5cbf9bc (v2). Responses: [docs/REVIEW.md](../REVIEW.md#ai-pre-review-phase-f).

# Simulated AI review from the perspective of the method's author (D. Humbird, 2021)

**This is a simulated AI review. It is not David Humbird's opinion.** It covers:
- whether the A.1 port is faithful;
- the extension to a secreted protein;
- the two capital conventions;
- the logic of the titer ceiling;
- the questions in REVIEW.md §D.

**Setup and sources**
- All model runs use the audit-fixes worktree with `PYTHONPATH=src:tests` and the pf-tea `.venv` interpreter. The base case reproduced at msp_ccf = 29.3694.
- Humbird 2021 was read from the text file and the PDF. Page numbers below are the printed page numbers (PDF page − 5).
- His SI workbook (`Humbird2021_cultured_meat_SI.xlsm`) was read cell by cell with openpyxl.
- Scratch scripts are in `<scratch>/review/hm/`.
- Nothing in the repo was modified; `git status` is clean.

---

## Comments (most severe first)

### HM-1: major. Error in a label, with headline consequences
**The "50 wt%" glucose feed is actually Intelligen's 500 g/L solution (about 42 wt%), and the titer ceiling is very sensitive to this.**

**Where**
- Summary item 1, p.1: "with a 50% glucose feed … about 74 g/L"; "with a 20% start or a 65% feed … about 125 g/L".
- §2.3, p.5: "glucose as 50 wt% solution".
- §4.4, p.13–14: the text, the Table 7 row "glucose feed 65 wt%", the caption "50 wt% glucose feed", and "$10/kg is not reachable with price-anchored capital…".
- §5.1 Q3, §5.5 and §6.
- REVIEW.md:40–41 (question A4).
- Code and data:
  - `data/pf/base.yaml:91`: `feed_glucose_wt` 0.5, sourced as "500 g/L … tracks volume at 1 kg/L".
  - `src/pftea/pf_ferm.py:408`: feed mass is glc/w_s and volume is mass/1000.
  - `scripts/run_analyses.py:197`: `"glucose feed 65 wt%": {"fermenter.feed_glucose_wt": 0.65}`.

**Comment**
- Volume is booked at 1 kg/L, so `w_s` is in effect kg of glucose per litre of feed.
- 0.5 correctly represents Intelligen's 500 g/L solution, but that solution is about 42 wt%.
  - A true 50 wt% feed is about 616 g/L.
  - The report's "65 wt%" case is 650 g/L, which is about 52 wt%.
- AUDIT R6-M2 noticed the 0.42 w/w and chose "Document". That fix is incomplete:
  - the main text, Table 7 and REVIEW question A4 still speak in wt%;
  - the "65 wt%" sensitivity added in v2 inherits the wrong label.

**What changes in the model** (base 30 g/L case is unaffected)

72 h titer ceiling by feed strength:

| Feed | 72 h ceiling | Limit that binds |
|---|---|---|
| 500 g/L (current base) | 74 g/L | minimum fill |
| 616 g/L (true 50 wt%) | 115 g/L | minimum fill |
| 650 g/L (report's "65 wt%") | 126 g/L | minimum fill |
| ≈861 g/L (true 65 wt%) | 171 g/L | secretion cap |
| ≈950 g/L (70 wt% DE95 syrup) | 179 g/L | secretion cap |

The "$10/kg is not reachable with price-anchored capital" conclusion:
- At 500 g/L it holds, but only just: MSP at the 36 h ceiling is $10.89.
- At a true 50 wt% feed, $10/kg becomes feasible:
  - 93 g/L at 36 h gives $9.84, at q_p 36.6 mg/g/h;
  - 104.5 g/L at 48 h gives $9.99, at q_p 33.0 mg/g/h.
- Those q_p values are 7–8× the base (4.65 mg/g/h) and above any *K. phaffii* value cited in base.yaml, but they pass the 40 mg/g/h feasibility cap.

Physical-limit floor (same fast search in each case):

| Feed | Floor | Optimum (cells, titer) |
|---|---|---|
| 500 g/L | $6.11/kg | 80 g/L, 119 g/L |
| 616 g/L | $5.60/kg | 100 g/L, 145 g/L |
| ≈950 g/L | $4.78/kg | 150 g/L, 215 g/L |

**What I checked**
- Glucose solution densities, from a partial specific volume of 0.622 mL/g:
  - 42 wt%: 1.187 kg/L, so 499 g/L;
  - 50 wt%: 1.232 kg/L, so 616 g/L;
  - 65 wt%: 1.325 kg/L, so 861 g/L;
  - 70 wt%: 1.359 kg/L, so 951 g/L.
  - I did not consult a density table; confidence 90% to within ±2%.
- Model runs:
  - `max_feasible_titer` at 72 h;
  - `required_titer` and `evaluate` for the $10/kg rows;
  - `physical_limit(fast=True)` with the feed override.
- Scripts: `feed.py`, `req10.py`, `qp10.py`, `plim_feed.py`.

**Fix**
- Relabel the base as "500 g/L (≈42 wt%, Intelligen)" and the sensitivity as "650 g/L (≈52 wt%)". Alternatively, re-parametrise the feed as a mass fraction plus a density.
- Add a "70 wt% glucose syrup (≈950 g/L)" row to Table 7, and use it in the physical-limit case (a physical limit should use the most concentrated practical feed).
- Restate Summary item 1 and §4.4: once the feed is at least about 600 g/L, what stands between the base and $10/kg with price-anchored capital is the secretion rate (a grade-D judgment cap), not the vessel.
- Reword REVIEW A4 to use g/L and wt% correctly.

### HM-2: major. Unsupported or overclaimed
**"Price-anchored" is true of the factor stack, not of the fermenter price that drives most of the gap between conventions; and Humbird's A.1 workbook does not use "these factors".**

**Where**
- Summary (report.typ:139): "a capital estimate tied to the market price of baker's yeast".
- §1, p.3 (:255): "Its capital estimate reproduces the market price".
- §2.5, p.6–7 (:457): "with these factors Humbird's baker's-yeast workbook reproduces a market price".
- §3, p.9 (:613): "the only convention tied to a real product price".
- §5.2 (:1043).
- VALIDATION.md:157 ("Our method is exactly Humbird's") and :172.
- base.yaml:241 and plant.py:303–304.

**Comment**

1. **The anchor plant is not the base plant.**
   - The anchor plant (A.1):
     - fermenters are 6 × 200 m³ bubble columns at $818k each, "bare equipment" (Table A.1, p.93; Equip!Table10 "BCR 200,000" is $779k plus the sparger);
     - capital uses a flat "Lang factor = 4.5" (p.93) on equipment cost including 20% missing capital, i.e. total capital investment (TCI) = 5.63 × listed equipment cost.
   - The base PF plant:
     - fermenters come from the STRFERM curve, the bare vessel plus agitator of Humbird's aseptic ASME BPE-2016, full-vacuum 316L STR (p.36–37, Table 3.3);
     - that is $2.47M at 196 m³, three times the anchor's vessel.
   - NREL's vendor-quote curve scaled to 200 m³ gives $0.85M, within 4% of the anchor's bubble column.
   - The "commodity aerobic" column (Equip!E5:J20, Table14) is referenced by no formula anywhere in the workbook:
     - every class-based sheet (4FB-*, 4P-*) uses "cGMP biopharm";
     - A.1–A.3 and Fig1.3 use a flat Lang factor of 4.5.

2. **The anchor tests the factors and fixed costs, not the vessel price.**
   - Capital moves the yeast cost only weakly: the capital charge is $0.47 and maintenance plus insurance $0.36 of $1.89/kg.
   - Humbird's band ($2.20–2.80 wholesale with a 33% margin, p.89) is $1.65–2.11 if the margin is on cost, or $1.47–1.88 if it is on price. Lang factors from 3.2 to 5.7 fit the first band.
   - The anchor does reject NREL's lighter stack, a point in the report's favour that it never makes:
     - A.1 with TCI = 3.1 × listed equipment and fixed costs of 1.15% + 0.7% gives $1.36/kg, below both bands;
     - the PF factor set (5.15×) with 9% fixed costs gives $1.82/kg, inside.
   - It says nothing about the STR vessel premium. Decomposition of the base BLG gap ($29.37 → $16.06):

     | Step | MSP | Change |
     |---|---|---|
     | Base (price-anchored) | $29.37 | |
     | Swap only the fermenter curve to the NREL vendor curve (about the anchor's own vessel price) | $21.32 | −$8.05 |
     | Then switch to NREL-style fixed costs | $17.70 | −$3.62 |
     | Then the remaining factors (full design-report convention) | $16.06 | −$1.65 |

   - About 60% of the gap is the vessel price basis, which the anchor does not test.

3. **Both conventions are Humbird's.**
   - NREL/TP-5100-47764 is Humbird et al. (2011).
   - Part of the 2.9× vessel gap is a difference in design basis:
     - NREL's F-400 is listed as "80,000 gal, 1 atm, 28 °C, Internal coil, SS316", with a separate agitator quote;
     - STRFERM is priced to the cell-culture aseptic specification.
   - The report never discusses which basis a food-grade PF fermenter that must be sterilised in place needs.

4. **The p.3 claim.** It is the full cost of production that reproduces the market-implied cost (p.5: "This cost can be reproduced with a first-principles TEA model"). The capital charge is only 25% of it.

**What I checked**
- Workbook, via openpyxl:
  - Table14 is not referenced by any formula;
  - class selections G187:G191 in every 4FB/4P sheet;
  - A.1!D160 = 4.5; Fig1.3!D20 = 4.5 and AX27 = SUM(AU:AW)×$D$20;
  - the Table10 rows.
- Port reruns with the Lang factor and fixed-cost fractions changed (`anchor_sens.py`, `anchor_nrel.py`).
- Decomposition by patching `equipment.fermenter` and the finance fractions (`decomp2.py`).

**Fix**
- Name each convention by what actually differs: "ACCE aseptic STR + facility factors (Humbird 2021)" versus "vendor-quote vessels + NREL factors (Humbird et al. 2011)".
- State that the yeast anchor supports Humbird's factor level and 9% fixed costs, and rejects the lighter stack for a yeast plant, but does not test the STR vessel price.
- Add a third, anchor-consistent case: vendor- or bubble-column-level vessel prices with Humbird's factors, which gives $21.3/kg for base BLG.
- Say that the commodity-aerobic column is tabulated in the workbook but never used by Humbird.
- In VALIDATION.md:157, replace "Our method is exactly Humbird's" with "the port is exact; the PF extension is Humbird-style".

### HM-3: minor. Misattribution of the O2 cap
**The 150 mol/m³/h cap is Humbird's bubble-column limit, and his cell-free basis is defined in the paper itself (Eq. 4.2). For a stirred tank his text supports about 200 on that basis, which in this model reproduces the base case.**

**Where**
- §2.3, p.5–6 (report.typ:385–389).
- Table 6 row "cap per cell-free liquid", the Fig. 6 caption, the last row of Table 7.
- §5.3 item 2 and §5.5.
- base.yaml:82; pf_ferm.py:18–21; REVIEW B3 and D2.

**Comment**
- Humbird's own words:
  - p.91: "Bubble columns have a practical OTR limit of 150 mol O2/m3-h before excessive foaming or jet flooding occurs."
  - p.28: "an OTR approaching 200 mol O2/m3-h is common in an air-sparged STR fermentor".
  - p.5: kLa upper limits "~800 h-1 in fermentation".
- The cell-free basis is Eq. 4.2 (p.49): OUR = qO2 / (cell-free liquid volume). A.1 cites Eq. 4.2 (p.91), so it is not a workbook quirk.
- The report pairs "Humbird's cap, 150 per m³ broth" with "Humbird's basis, 150 per m³ cell-free liquid". Both use a bubble-column number for a stirred tank.
- Effect in this model:
  - Base (150 per m³ broth): $29.37 and a 74 g/L ceiling at 72 h.
  - Humbird's stirred-tank statement on his own basis (200 per m³ cell-free liquid, ≈129 per m³ broth at 107 g/L): $29.11 and 73 g/L.
  - The "Humbird basis" sensitivity (150 per m³ cell-free liquid): $30.95 and 68 g/L, more pessimistic than the method implies for a stirred tank.
- The claim "aeration physics alone would allow about 376 mol/m³/h" needs kLa ≈ 2,150 h⁻¹ at about 5 kW/m³, which is 2.7× Humbird's stated limit. kLa = 800 h⁻¹ corresponds to OUR ≈ 200 here (796 h⁻¹ at 200).
- The physical-limit floor is insensitive to a cap of 200 versus 250 ($6.10 vs $6.11), so no headline number changes.

**What I checked**
- A.1!AD287 = −K/(W(1−AW))×1e6, i.e. OUR per cell-free liquid.
- `d2.py`, `kla2.py`, `plim.py`.

**Fix**
- Attribute the 150 to bubble columns, and cite Eq. 4.2 for the basis.
- Relabel the sensitivity "A.1 bubble-column cap (150 per m³ cell-free liquid)".
- Add a "200 per m³ cell-free liquid" case, or adopt it as the base: it is neutral here and penalises very dense designs by itself.
- Present the 376 as van 't Riet extrapolated beyond Humbird's kLa limit.

### HM-4: minor. Judgment call
**The method limits cell density by broth viscosity; the extension dropped that limit.**

**Where**
- pf_ferm.py:94–95: the stirred-tank kLa has no viscosity term.
- The A.1 port (fermentation.py:123) does include η^−0.84.
- base.yaml:50: `kla_factor` 1.0, "water-like (Humbird Fig1.3)".
- X_prod 107 g/L and X_max 150 g/L.

**Comment**
- In Humbird's method, the fed-batch endpoint is "determined by a final viscosity (2 cp)" (p.92), which he translates into a practical maximum of 70 g/L for baker's yeast.
- With the model's own Krieger–Dougherty constants, the broth is:
  - 1.9 cP at 80 g/L;
  - 3.0 cP at 107 g/L;
  - 9.8 cP at 150 g/L.
- Industrial *K. phaffii* fed-batches in stirred tanks do reach 100 g/L or more, so these densities are defensible; but kLa falls with viscosity.
- Applying a viscosity penalty to kLa over the whole batch:
  - factor 0.55: +$0.27/kg;
  - factor 0.33 (A.1's exponent at 107 g/L): +$0.86/kg;
  - the base stays feasible, with peak heat 23.0 kW/m³.
- This matters most for the 150 g/L designs that the concentrated feeds in HM-1 unlock.

**What I checked:** `visc.py`, `kla.py`.

**Fix**
- State the omission.
- Add a viscosity-corrected kLa sensitivity.
- Flag X_max = 150 g/L as beyond the method's viscosity endpoint.

### HM-5: minor. Documentation
**The "ISBL non-bioreactor" installation factor is applied to the fermenters, unlike Humbird's calculation chain; the result is defensible but not documented.**

**Where**
- base.yaml:250–255: the facility-class source reads "ISBL non-bioreactor DC x PEC".
- plant.py:355 multiplies all ISBL equipment, fermenters included, by (1+m)(1+1.4).
- AUDIT.md:63 (R3) says "the 4FB capital chain match Humbird's sheets".

**Comment**
- Humbird's chain:
  - Table14 has a separate "Bioreactor install factor", equal to 1 in every class.
  - In 4FB-020, bioreactors enter at their installed ACCE cost with no factor (I204).
  - The 1.3× installation factor applies only to other ISBL equipment plus missing capital (I214; Table 4.1 note b, p.55; p.38: "No additional installation costs are applied").
- The model instead multiplies the bare quote by 2.67:
  - That gives $6.66M per 200 m³ (2018$), 0.90× Humbird's own installed aseptic STR ($7.38M, Table10 "STR 200,000"; Table 3.3 gives $6.8M).
  - A literal 4FB chain with that installed cost would give $9.35M.
- So this is not double-counting; the result sits between Fig1.3 (bare × 4.5) and the literal 4FB chain. But a reader who checks the label against Table14 will think it is double-counting.

**Fix**
- Document the choice and its check against Table 3.3.
- Correct the base.yaml source text and the R3 statement in AUDIT.md.

### HM-6: minor. Interpretation of the yield
**The derived product yield absorbs Intelligen's 4 g of host-cell protein (HCP).**

**Where:** §2.2, p.4–5 ("80% of [the ceiling]"); §2.7 (0.55 = "about 95%"); base.yaml:30.

**Comment**
- Intelligen's Eq. 2 is 100 g glucose → 28 g OVA + 8 g cells + 4 g HCP. The derivation charges the HCP glucose to the target protein.
- If the HCP are made by the same reaction, the implied yield is 0.4648 × 32/28 = 0.531, which is 0.90 of the OVA ceiling (0.590), not 0.80.
- At the physical-limit yield of 0.55 per g of target, co-secreting HCP at Intelligen's ratio would need 0.63, above the ceiling. The physical limit therefore implicitly assumes no HCP.
- There is no effect on costs.

**What I checked:** `prod.py`. The derivation 3.5714 − 0.5008 − 0.9192 = 2.1514 gives 0.4648; ceilings are 0.5824 (BLG) and 0.5900 (OVA).

**Fix:** State both points explicitly.

### HM-7: editorial. Compressor-formula effect
**The effect on MSP is about zero, not "about $0.1/kg".**

**Where:** §6, p.19 (:1114); VALIDATION finding 3; pf_ferm.py:141.

**Comment**
- With the adiabatic form (k/(k−1) = 3.5, exponent 0.286):
  - electricity falls by $0.047/kg;
  - MSP rises by $0.014, because the optimiser shifts to more air and compressor capital rises.
- Fidelity to the original formula is only needed in the anchor port.

**What I checked:** `comp.py`.

**Fix:** Use the corrected formula in pf_ferm (keep the port as it is), or restate the effect.

### HM-8: editorial. CIP chemicals counted twice
**Where:** plant.py:432, together with 4% maintenance.

**Comment**
- Humbird p.46: maintenance at 4% of TCI "is assumed to include CIP chemicals".
- The model adds CIP chemicals separately: $0.169/kg of base BLG (0.6%).

**Fix:** Drop CIP chemicals under the price-anchored convention, or note the double count.

### HM-9: editorial. Heat per mol O2
**Where:** §2.2, p.5 ("about 480–510 kJ per mol O2").

**Comment**
- Growth (506) and maintenance (478 kJ/mol O2) are in the stated range.
- The product reaction releases more, because the protein's formation enthalpy comes from the biomass correlation:
  - 527 (BLG) and 524 (OVA) kJ/mol O2 at Y_ps 0.465;
  - 570 and 561 at 0.55.
- The implied heat of combustion is about 24.4 kJ/g (N→N2, CO2 as gas), close to the usual ~23.6 kJ/g for protein, so the numbers are plausible. I did not verify the latter value; confidence 80%.
- There is no cost effect: production heat is about 4–8 kW/m³.

**Fix:** Give the product-reaction range separately.

---

## REVIEW.md §D: simulated answers (not Humbird's)

**D1. Does the port and extension respect the method?** (Confidence about 70%.)
- **The port: yes.**
  - A.1 cells W287 (volume), AD287 (OUR per cell-free liquid) and BD287 (compressor) are reproduced exactly (fermentation.py:199–201, :209, :271–274).
  - `test_humbird_yeast` passes 14/14; the port gives $1.8899/kg.
  - One point worth stating in VALIDATION: the paper prints Eq. A.8 as 0.32 u_s^**0.2** η^−0.84 (p.91), while the workbook (A.1!C95:F95) and the port use **0.7**. The port is right to follow the workbook.
- **The stoichiometric and O2-limited fed-batch core: yes.** Details are under "Checked and found correct" below.
- **Departures to state:**
  - HM-2 (capital), HM-3 (O2 cap), HM-4 (viscosity), HM-5 (installation factor).
  - Replacing Tijhuis maintenance with measured production-phase maintenance fits the method's Herbert–Pirt structure and is well motivated. It comes from a strain secreting at low productivity, though; secretion burden at 5–40 mg/g/h could raise it (a question for the fermentation reviewer).
  - Calibrating Y_ps to a design, rather than a measurement, is circular for anchor 3; the report already says so.

**D2. Cap per cell-free liquid or per broth?** (Confidence about 75% on what the paper implies; I cannot speak to intent.)
- The paper's basis is cell-free liquid (Eq. 4.2, cited in A.1).
- 150 is the bubble-column value. For an air-sparged stirred tank, the text supports about 200, with kLa ≤ ~800 h⁻¹.
- "200 per m³ cell-free liquid" is equivalent to the base at 107 g/L ($29.11 vs $29.37; 73 vs 74 g/L), and falls to about 100 per m³ broth at 150 g/L.
- I recommend it as the method-consistent base.

**D3. The compressor exponent and the broth-volume signs** (confidence 90% and 80% that they are unintended)
- **Compressor.** Column BD uses (p^1.4 − 1)/1.4, where the adiabatic form is 3.5 × (p^0.286 − 1).
  - It overstates power by 1.58× at 2.1 bar and 1.74× at A.1's bottom pressure of 2.43 bar.
  - Correcting it moves the anchor −1.7%, to $1.857/kg.
- **Volume signs.** A.1!W287 adds the water stripped by the off-gas and subtracts the metabolic water; both signs are reversed physically.
  - With A.1's plant configuration held fixed (one train), correcting them moves the anchor −2.3%, to $1.846/kg.
  - Under A.1's integer train rule, the shorter batch (14.45 h instead of 15.67 h) rounds the turnaround to 22 h. That gives 2.18 batches per shift, above the threshold of 2, so the plant flips to two trains and the cost to $2.014/kg (+6.6%). This is an artefact of the rule.
- Both corrections keep the anchor inside the market-implied band.
- Scripts: `a1fix.py`, `a1vol.py`.

---

## Checked and found correct
- **Thermodynamics.**
  - Heijnen dissipation for glucose is 236.1 kJ/C-mol.
  - Catabolic ΔG and ΔH are −2,921.5 and −2,865.4 kJ/mol, matching the paper's Eq. A.2 (−2,922 and −2,865).
  - Tijhuis maintenance is 0.01744 g/g/h at 30 °C; maximum yield is 0.5705 g/g.
- **Product reaction.**
  - C/H/O/N and electron balances close to ≤1e-15 at Y_ps 0.28, 0.465 and 0.55.
  - Electron ceilings are 0.7025 and 0.716.
  - Energetic ceilings are 0.5824 and 0.5900 (4 ATP per bond, 21.76 ATP per glucose).
  - O2 use is 24.2 mol/kg BLG at Y_ps 0.465.
- **O2 and heat bookkeeping in production.** Product O2 enters the production OUR check (pf_ferm.py:396–399); heat includes product formation (:314–320); liquid mass-balance signs are physical (:408–409).
- **Ceiling logic** (consistent with A.1's volume-closure logic):
  - growth runs at the cap (peak OUR 150.0);
  - production OUR is 27–30 mol/m³/h in the base and 39–57 at the 74 g/L ceiling, against a cap of 150;
  - the limit that fails just above the ceiling is the 30% minimum start.
- **Finance and capital figures.**
  - Capital charge factor is 0.1457 (7.5%, 10 years; p.39).
  - Maintenance and insurance are 4% + 5% of TCI (p.46).
  - The effective Lang factor is 5.15.
  - STRFERM extrapolated to 300 m³ is 2.9× NREL's F-400 plus A-400 (2007$).
  - The cell-free cap is 96.5 per m³ broth at 107 g/L.
- **Stirred-tank inputs.** The van 't Riet constants and the 0.8 fill match Fig1.3!C11:F11 and C8.
- **Physical-limit floor.** It is insensitive to an O2 cap of 200 versus 250.
