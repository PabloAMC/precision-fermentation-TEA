# Audit R12: pf-tea v4 (model-v4 @ 97a64d5 + working tree), 2026-10-02

Read-only. Checks ran with `PYTHONPATH=src .venv/bin/python` and scratch scripts. The v4 tests pass (`-k "methanol or siz or rank or alb"`: 15 passed). Unless stated otherwise, every MSP below is $/kg on the CCF basis, computed by me.

## HIGH

**H1. Capture-only purity (≥96%) for albumin is unsupported, and it decides the headline (E, D).**
- The patent says what the step after CEX is for: affinity "further purifies the rHA with respect to a 45 kD N-terminal albumin fragment, yeast antigens and pigment" (US 5,728,553).
- The only public ">96%" Pichia result used Cibacron Blue affinity, not CEX (Zhu 2018).
- InVitria's 96% spec is for a rice-expressed product purified with several steps.
- The same patent family has a minimal two-column train: US 6,638,740 Ex. 4, "Cation Exchange Followed Directly by Anion Exchange".
- Recovery alone moves the cost: a polish step at 0.8 recovery gives 0.56×0.8 → **$177**; at 0.65 (DE-FF ">65%") → **$214**. This is before the second resin's own cost, which at a similar load (DE-FF 35±15 g/L) roughly doubles the $59/kg resin line.
- **Fix:** add `alb_two_step` (CEX → AEX, as in Ex. 4) and make it the base, or present the base as an optimistic bound. Keep capture-only as a variant.

**H2. Resin life (1000 cycles) sits at the top of its range and was borrowed from whey lactoferrin (D).**
- base.yaml: `cex_resin_life_cycles: {value: 1000, low: 125, high: 1000, grade: A}`, sourced from industrial lactoferrin ("After over a thousand cycles").
- Albumin's CEX loads crude, pigmented yeast centrate at pH 4.5. The patent gives no number, only "used for multiple cycles". Intelligen's own lactoferrin design uses 150 (`lactoferrin.yaml: dsp.cex_resin_life_cycles: 150`).
- Resin is the largest cost line: $59.4/kg of $143.2.
- Lower lives: 300 cycles → **$281.8**; 125 → **$559.1**.
- **Fix:** give albumin its own life (grade C/D, mode well below 1000) or show the life band next to the $143. The claim that the column sets the cost holds; the $143 figure does not.

## MEDIUM

**M1. The tornado bar for vessel volume is wrong for sized products (C).**
- Both lf and alb are sized to 100 m³, which equals `volume_m3.low`.
- The high end, 500 m³, is above `volume_cap_m3` (200) and above the physical-limit vessel (400).
- lf industry: 100 m³ → 105.8, 500 m³ → 179.2. That is a one-sided $73 swing, probably lf's largest bar. It shows a design choice as an uncertainty: by construction every other size costs more. alb: 132.9 → 144.5.
- **Fix:** when `sizing == cheapest`, drop `fermenter.volume_m3` from the tornado, or plot min/max over `size_choices_m3`.

**M2. Methanol uptake is probably low by about 2× (A).**
- `m_s_prod_methanol = 0.016 × 0.31` is my-derivation-type scaling (grade D).
- Academic alb (17.47 g/L, 192 h) consumes about 1.3 g/L/h of methanol, 10.3 kg per kg made.
- The repo's own K. phaffii induction feeds are higher: 3.4 g/L/h (`casein.yaml:924` quote), 2.01, and about 3.0 (6.09 of 50%).
- At 0.016 the cost is **$243.8** (vs $227.4) and the run flags "initial fill 29% below minimum".
- **Fix:** calibrate q_s,MeOH against those feed rates, or use 0.016 as the base for multi-day inductions.

**M3. Proteolysis during the pH-4.5 hold is not modelled (E).**
- The plant runs 839 batches/yr, so each batch's centrate is processed over about 9.9 h (mean hold about 5 h if acidified in bulk).
- Kobayashi 2000 reports rHSA degradation of 660 mg/L/h at pH 4.3 in Pichia broth (abstract).
- Scaled to the 3.1× diluted load (9.7 g/L), that is about 2%/h, or about 10% extra loss.
- The 0.56 recovery comes from S. cerevisiae with 5 mM octanoate and a <15 °C hold, neither of which is costed.
- **Fix:** state in-line acidification and cost the chilling and octanoate, or use a lower recovery for K. phaffii. At 0.45 the cost is about $177.

**M4. A calibration anchor silently lost its methanol cost, and the lactoferrin reconciliation is inconsistent (A).**
- `data/calibration/intelligen2025_ova.yaml:36` still sets `media.methanol_kg_per_kg_product: 0.30`, but plant.py no longer reads that leaf (now `b.methanol_kg × price`). This is a dead override worth about $0.27/kg.
- base.yaml cites "Intelligen's lactoferrin design" as a methanol_frac=1 example, yet `lf_intelligen_a/b` stay at 0, while Intelligen reports 4.2 kg methanol per kg LF (`lactoferrin.yaml:593`).
- **Fix:** delete or replace the override, and set `strain.methanol_frac_prod: 1` in the lf_intelligen variants (or say why not).

## LOW

**L1. The methanol energetic ceiling leaves out the ATP cost of XuMP assimilation (A). Please check this derivation.**
- Fixing carbon through XuMP is 3 HCHO + 3 ATP → triose-P. Glycolysis gives 1 ATP per triose-P. That is about 0.67 extra ATP per C-mol assimilated.
- Stouthamer's cost "from glucose for both" (plant.py docstring) misses it.
- Using alb's ATP need of 0.98 per C-mol product: the ceiling falls from 0.531 to about 0.454, the ratio to glucose from 0.921 to about 0.79, and Y_ps,MeOH from 0.4285 to about 0.366.
- Cost effect is small (alb_methanol $149.2 → $149.9) because maintenance dominates.
- **Fix:** add `energetics.xump_atp_per_C` to `energetic_ceiling(p, "Methanol")`.

**L2. The neat-methanol volume balance mixes volume and mass (A).**
- `w_m = 791/1000` adds methanol by volume (1.264 L/kg), while O₂ and CO₂ go in and out by mass.
- Per kg of methanol burned, M rises by 1.389 kg against 1.125 kg of real water.
- With c_meoh = 1000, MSP goes from 149.17 to 149.90.
- **Fix:** put every feed on a mass basis (`w_m = 1` for neat methanol), or document it.

**L3. Wrong provenance note on the albumin buffer costs, plus missing chemicals (B).**
- The note on `cex_elution_nacl_kg_m3` says "a few cents per kg albumin". In fact 13.6 × 8.5 / 40 = 2.9 kg of acetate per kg loaded, and zeroing the line moves MSP by $1.02 even at the NaCl price.
- The acetate price has no leaf.
- Not costed: wash/equilibration buffer recipe 1 (3.69 g/L × 15.5 CV ≈ 1.4 kg/kg), acetic acid for the pH-4.5 load, and 5 mM octanoate. My rough guess for the total is $1–5/kg (source: guess).
- **Fix:** add acetate and octanoate leaves priced from Comtrade (HS 2915.29 / 2915.90) and correct the note.

**L4. `cex_cv_per_cycle: 34` is a maximum, not a typical value (B).**
- The arithmetic is right: 4+11.5+2+6.5+3.5+3+3+0.5 = 34.
- But Table 4's "Vol" column is an override: steps end "when the predetermined volume is reached or before if one of three monitor signals passes".
- At 16 CV the cost is $129.8 (−$13).
- Similarly, `elution_cv 8.5` is used as the eluate volume (`V_uf`), but only step 5 (≤6.5 CV, ending at A280 0.6) is collected. At 6.5 the cost is $142.6.
- **Fix:** note these as upper bounds, and split buffer CV from eluate CV.

**L5. Load conductivity is not checked (E).**
- The patent requires centrate "<5.5 mS cm⁻¹".
- The load is diluted only 3.1× (load_cv 4.12, 9.7 g/L), carrying about 7 g/L of medium salts (22.3 kg/m³ ÷ 3.1). Extra dilution would be needed.
- About +2–4 CV gives about +$2–3. The 6× extreme (+20.6 CV) gives $158.
- **Fix:** add a conductivity-driven load dilution.

**L6. Spearman rho is spurious for inputs held constant (C).**
- `rank = argsort(argsort(a))` turns a constant input into ranks in draw order. My test gave rho = 0.031, not None.
- The six academic cases have `titer low == high`.
- Rho is also computed only over feasible draws, which is a conditioning bias.
- **Fix:** return None when `np.ptp(vals) == 0`, and document the conditioning.

**L7. Re-sizing is inconsistent with the base.yaml note (C).**
- `evp(prod, changes)` calls `base_params(prod, changes)`, so base_light, base_eu, base_aseptic and base_isolate each re-size, contradicting "Sized once on the product's base case".
- It has no effect today (I checked: the vessels are identical in all four cases) but could diverge silently.
- **Fix:** size first, then apply the overrides.

**L8. The recovery value and the column table come from different examples (B).**
- 0.46–0.66 is US 6,638,740 **Ex. 4** (octanoate elution). Table 4 (Ex. 2, acetate pH step) says ">40%" with different assays in and out.
- **Fix:** acceptable at grade B; add one sentence saying so.

## Checked and fine
- **Element balances:** C, H, O, N residuals are 0 for methanol growth, anabolism and the product reaction. The S residual of about 0.01 was there before v4.
- **Methanol anabolism:** fixes no CO₂ (CH₃OH −1, O₂ −0.432 per C-mol DCW). Y_x,max = 0.435 g/g, which is plausible.
- **Maintenance multiplier:** 0.005 / 0.01371 = 0.365, dimensionally right (mol/C-mol/h × MW_meoh / MW_bio).
- **Heat:** the sign convention matches glucose. dHf(aq) is −245.9 kJ/mol, which includes the heat of mixing.
- **Blend:** applied only when `prod=True`. Growth and heat-limited branches stay on glucose; production OUR and heat are flagged.
- **Yield ceilings:** Y_ps,MeOH (0.43) ≤ ceiling (0.53) < carbon ceiling (0.706), and the product of ratios cannot exceed it.
- **Seed train:** costed on glucose, which is acceptable (real runs use glycerol).
- **Calibration anchors:** they set the vessel explicitly and `plant.evaluate` never re-sizes, so they are unaffected.
- **Sizing cache and runtime:** the json cache key is correct; sizing takes about 3.5–4.5 s per product.
- **Albumin numbers verified against the sources:**
  - dbc 40±10, Table 4 CVs, 13.6 g/L NaOAc·3H₂O, 117 g/L NaCl (recipe 3, named "DBA Eluent", used as the salt wash), 0.5 M NaOH = 20.0 g/L.
  - Titers: 1.5 g/L (US 5,728,553 Ex. 1 "rHA>1.5 g/L culture"), 17.47 g/L / 192 h (abstract).
  - Dryer feed: 20% w/v (Recombumin datasheet, line 265).
  - Prices: Comtrade NL 42.45 and US 57.80 $/kg (recomputed from json); GFI 2025 "$40 to $70/kg" (p.31 text); GFI 2023 "$10/kg".
  - Medium use: 8/13/42 L/kg; 1.125 and 1.134 g/L arithmetic.
