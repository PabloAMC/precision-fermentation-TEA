# pf-tea: is the modelling approach state of the art? (review, 2026-10-02)

Independent, read-only review of branch `protein-candidates`, using about 12 web requests (Europe PMC) and the texts on disk. Numbers marked "model" come from `results/analyses.json`. Numbers marked "my arithmetic" are mine; please check them.

## 1. Verdict

**At or above the published state of the art for a public, multi-protein screening TEA.** P ≈ 0.85.

There is little to beat. GFI's 2025 survey says "published PF TEMs are extremely limited, with only four models focused on food proteins" (*Driving down costs*, §1.3.1). Those are SuperPro flowsheets or one-offs. Arthur D. Little/GFI Europe 2025 calls its own model "a tool for obtaining directional estimates" (p.30), with a fixed yield and fixed DSP recoveries.

- **No artificial complexity.** Every piece pf-tea adds beyond SuperPro serves the feasibility question at the centre of the report.
- **What remains is data and conventions, not structure.** P ≈ 0.85 that no structural change below moves base $/kg for BLG, OVA, ovomucoid or β-casein by more than 10%. Conventions alone move base BLG ($21.2/kg) by −22% (design-report capital) to +46% (aseptic vessels) (model).
- **Albumin is the exception.** It needs one model change (methanol) and one exposed design choice (vessel size).

## 2. Where pf-tea is at or above the state of the art

- **Fermentation.** pf-tea has element- and electron-balanced stoichiometry, Heijnen dissipation, Herbert–Pirt/Tijhuis maintenance and a measured near-zero-growth maintenance. Humbird 2021 (doi:10.1002/bit.27848) does this for growth only; SuperPro TEAs use lumped equations (Intelligen OVA Eq. 1–3).
- **Feasibility.** O₂ transfer (van 't Riet, aeration optimum), heat removal, minimum fill and a volume balance are all checked, and infeasible designs are never costed. Only Humbird 2021 is comparable. NREL 2011 sizes equipment for the peak.
- **Utilities** are sized on the coincident plant peak, not the sum of single-batch peaks.
- **Evidence** carries A–E grades with verbatim quotes, and the tornado is coloured by grade. I found no published equivalent.
- **Validation** uses one market-price anchor and three consistency anchors, with misses recorded rather than tuned. Most TEAs validate nothing.
- **Finance** shows the capital charge (CCF) and an NREL-style discounted cash flow (DCF), each under two capital conventions.

## 3. Gaps that matter, ranked

**G1. Methanol (and ethanol) are costed but missing from the O₂ and heat balance.**
- `base.yaml:121`: "Cost only: its O2 and heat are not added to the stoichiometry". The effect is small today (methanol-free base) but large for albumin (§4).
- *Physics:* methanol carries 6 electrons per carbon, against glucose's 4, so it needs 1.5 mol O₂ per mol to burn, against 1.0 per C-mol of glucose. Heat follows O₂ at about 460 kJ/mol. Alcohol oxidase passes electrons to O₂ without making ATP, so methanol costs more O₂ and heat per unit of growth or maintenance.
- *Fix:* `data/thermo/compounds.yaml` already holds methanol, ethanol and glycerol, and `thermo.GrowthModel` takes any substrate. Add a production-phase substrate choice used in `pf_ferm._rates` (`pf_ferm.py:317`), with its own maintenance coefficient. Looser 2015's methanol range, 0.009–0.032 g/g/h, is already noted (`docs/REVIEW.md:277`).

**G2. Vessel size is fixed at 200 m³ even for small plants.**
- Lactoferrin at 250 t/yr needs 3.5 vessels and buys 4. In the tornado run, 100 m³ vessels cut MSP by 13% ($122 → $106) and 500 m³ raises it 47% (model). Real designs choose the vessel for the scale; Intelligen uses 5 × 136 m³ at 1 kt/yr.
- *Fix:* for each plant, pick the volume with the lowest MSP from a sourced discrete set, reusing the `best_design` search in `scenarios.py`.

**G3. Secretion is decoupled from growth.**
- The production phase is q_p = αμ + β with α = 0 and β solved from the titer (`pf_ferm.py:410`). Maurer et al. 2006 (doi:10.1186/1475-2859-5-37) say q_P "is not constant at varying specific growth rates" and fit q_P = q_Pmax·μ/(k_q + μ), which goes to zero as growth stops. REVIEW.md:280 records that "secretion rises with µ".
- *Effect:* none on the base, which solves q_p from the titer. It does affect Q3/Q4, where the report finds "the gate is q_p" against a grade-D ceiling of 40 mg/g/h.
- *Physics (please check):* with purely growth-coupled secretion, titer ≈ α × X_max ≈ (2.1/0.1 mg/g) × 150 g/L ≈ 3 g/L (my arithmetic). So 30 g/L needs a large β, which no public glucose strain shows.
- *Fix:* an optional `strain.alpha_mg_g` leaf, default 0, used in the academic glucose cases.

**G4. No global sensitivity measure.** Draws are independent triangulars (`params.py:113`, `scenarios.py:315`) and the tornado is one-at-a-time. The Guest group's practice is Monte Carlo plus "Spearman's rank order correlation coefficients" (Bhagwat et al. 2026, doi:10.1038/s41467-026-75285-1). *Fix:* about 20 lines on the existing draws. No change to $/kg.

**G5. The first-of-a-kind penalty is promised but missing.** `docs/SCOPE.md:82` says "A first-of-a-kind penalty is shown separately", and nothing implements it. NREL's nth-plant convention assumes "several plants using the same technology have already been built and are operating" (NREL 2011 §1.4). Funders will be judging first plants. *Fix:* one labelled sensitivity sourced from Merrow et al. 1981 (RAND R-2569-DOE; not on disk, so its numbers must not be guessed), or delete the promise.

**G6. Chromatography is a single column.** That is enough for lactoferrin, whose top tornado bars (resin life: $148/kg swing; price; binding capacity) are data, not structure. Generalise `plant.py:249-259/417-419/533` to several steps only if albumin needs a second column worth more than about 10% of MSP.

**Not worth it (artificial complexity at screening level):** mechanistic chromatography (CADET), CFD or viscosity-corrected k_La (already a stated caveat), genome-scale models, continuous or perfusion operation, Sobol indices, learning curves beyond a FOAK band, rebuilding in SuperPro or BioSTEAM.

## 4. Recombinant serum albumin for cultivated-meat media

**What exists.** No process TEA of recombinant albumin was found. GFI 2023 assumes the cost: "We set the lowest cost tier for albumin at $10/kg protein". Humbird 2021 forecasts recombinant-protein prices from a price-volume regression. A bottom-up cost would therefore be new; check it against Humbird's regression (his Fig. 3.4b).

**Process data.**
- *Titer:* Mallem 2014 (doi:10.1002/btpr.1990) used a slow-methanol-use (Mut^s) strain with "lower specific growth rates (0.0022-0.0024/h) during methanol induction phase", reaching "10 g/L". Zhu 2021 (doi:10.1016/j.pep.2021.105831) reports "17.47 g/L HSA in the supernatant within a 192 h induction".
- *Purification:* Zhu 2021's three-step purification "recovered two thirds". Zhu 2018 (doi:10.1016/j.pep.2018.02.003) reports "58% recovery" at ">96% purity" by dye-affinity chromatography.
- *Impurities:* the pharmaceutical process tracked "Pichia yeast component, DNA and mannan" (Kobayashi 2006, doi:10.1016/j.biologicals.2005.08.021).

**What the model needs.**
1. **G1 (methanol) is required.** Public albumin data come from slow-growth methanol inductions lasting days, where maintenance dominates substrate use.
   - Substrate per kg product ≈ m_s × average cell density × induction time ÷ titer (please check).
   - Illustrative values (0.013 g/g/h, 100 g/L, 192 h, 17 g/L) give about 15 g of methanol per g of albumin (my arithmetic).
   - Pricing that as glucose at the base 0.0044 g/g/h understates both cost and O₂ demand. P ≈ 0.55 that skipping G1 misstates albumin $/kg by more than 15%.
2. **Downstream is mostly a data change on `cex`:**
   - overall recovery 0.58–0.67;
   - a media-grade spec (no food-grade spec exists; the cell-culture endotoxin spec is ≤1.0 EU/mg, `PROTEIN_CANDIDATES.md:307`);
   - extra column volumes for a polishing step.

   Prefer cation exchange to dye affinity, because the dye can leach into a food input. Add G6 only if the polish is material.
3. **Small scale needs G2.** The repo's own forecast is P(demand > 1 kt/yr in 2035) ≈ 0.08. QC release testing (now excluded) matters more at small scale; add it only with a sourced figure.
4. **Methanol-safe handling** need not be modelled: state it as inside the 20% missing-equipment allowance.

**A state-of-the-art albumin TEA would include:**
- a methanol induction phase in the O₂ and heat balance;
- measured methanol maintenance;
- capture and polish chromatography with graded resin data;
- a media-grade spec;
- vessels sized for the scale;
- a price-volume cross-check.

pf-tea reaches that with G1, G2 and data.

**Other proteins.** α-lactalbumin is a data change on the concentrate route (ADL: 20 g/L, 0.13 g/g, 87% DSP yield). κ- and αs1-casein are data changes on `acid`. Heme needs a note only.

## 5. Recommendations (ordered)

1. **G2, vessel size per plant scale.** *Do now* (lactoferrin moves about 13%); also needed for albumin.
2. **G5, a sourced FOAK sensitivity, or delete the SCOPE promise.** *Do now.*
3. **G4, Spearman ρ on the existing Monte Carlo draws.** *Do now.*
4. **G3, optional α (default 0).** *Do now, small.*
5. **G1, methanol and ethanol stoichiometry.** *Do with albumin*; it also fixes the Yao 2026 and Intelligen lactoferrin caveats.
6. **Albumin as data on `cex`, plus a check against Humbird's price-volume regression.** *Do with albumin*; G6 only if material.
7. **Fit Bhagwat's MPSP = a + b/yield + c/titer + d/(yield·titer).** *Optional.* The authors warn the fit may be poor for "proteins".
8. **Everything in the "not worth it" list.** *Not worth it.*
