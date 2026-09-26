# Exercise A1: rebuild Intelligen's $39/kg ovalbumin (about 2 hours)

**Why this exercise.** Every techno-economic analysis makes the same three moves: a mass
and energy balance, a capital estimate, and an operating-cost roll-up. Intelligen's 2025
study is the only complete public design of a precision-fermentation egg-protein plant.
Rebuilding its $38.99/kg by hand teaches all three moves on the product we are modelling.
That figure is the gross unit cost; Intelligen's headline $36/kg is net of a fertiliser
credit.
It is also calibration anchor 3 in Phase D, so you will end up knowing it inside out.

**You need**
- The paper: [`references/reports/Intelligen_2025_ovalbumin_TEA.pdf`](../../references/reports/Intelligen_2025_ovalbumin_TEA.pdf).
  Read printed pp. 5–10 (process) and 16–19 (costs) first. Printed page n is PDF page n+1.
- The workbook: [`A1_intelligen_rebuild.xlsx`](A1_intelligen_rebuild.xlsx), which opens in
  Numbers or Excel. Its formulas compute when you open it.
  - Fill in the yellow cells on *Workings*. Every quoted number is on *Inputs* with its page.
  - Row 4 is a worked example of the expected format.
  - *Check* grades you against the paper's own numbers as you go.
- [`docs/PRIMER.md`](../PRIMER.md) §3 (stoichiometry and heat) and §7 (accounting).
- If you prefer Python, do it there instead. The answer key
  [`a1_solution.py`](a1_solution.py) shows the structure, but open it only at the end.

**Exit criterion for Phase A.**
- The rebuilt unit cost (row R5) lands within 20% of $38.99/kg. This checks your
  bookkeeping only: rows R1–R4 reuse the paper's own totals, so R5 stays within 20% for any
  maintenance rate from 0 to 48% of PEC per year (with your glucose), or for any annual
  glucose up to 37 kt (at 6% maintenance).
- Your annual glucose lands within 20% of Table 3. This is the check that tests your
  reconstruction. The *Check* sheet reports both.
- More important than either: you can answer question 3.3 in your own words.

## Part 1: the accounting (about 50 minutes)

| Step | Task | What it teaches |
|---|---|---|
| 1.1 | Turn the seven Figure 6 slices into $/yr. Check raw materials and utilities against Tables 3 and 4. | Where the money goes. At 1 kt/yr, capital-related costs dominate. |
| 1.2 | Back out the capital chain: working capital, then direct fixed capital (DFC), then purchased equipment cost (PEC = DFC/4). | The capital pyramid, and how small working capital is |
| 1.3 | Rebuild the 44% facility-dependent slice from DFC using the hint factors H1–H5, then solve for the maintenance rate that closes the gap. Is it plausible? | What a SuperPro "unit production cost" contains (depreciation and overheads, but no return on capital) |
| 1.4 | Recast in Humbird's convention (capital charge + 4% maintenance + 5% insurance and tax, all on TCI). | How far accounting conventions alone move an answer |
| 1.5 | Convert $/kg of powder to $/kg of ovalbumin and place it in GFI's egg-white band (H14–H15). | Always compare per kg of *protein* |

## Part 2: the balances (about 50 minutes)

| Step | Task | What it teaches |
|---|---|---|
| 2.1 | Ovalbumin leaving the fermenter per batch, pure ovalbumin in the product, and overall downstream recovery. Careful: UF's 0.995 is a *rejection coefficient*; concentrating CF-fold keeps CF^−(1−σ). | Recovery, and where losses happen |
| 2.2 | Glucose per batch from Eq. (1) and (2): how much goes into cells and how much into product? Overall yield. Compare annual glucose with Table 3. | Why overall yields are far below the expression-phase stoichiometry |
| 2.3 | O₂ per batch and per kg of ovalbumin; metabolic heat (0.46 MJ/mol O₂); average cooling duty per fermenter. Compare with NREL's 84 mol O₂/kg. | Yield sets the oxygen and cooling bill |
| 2.4 | Chilled water per batch, and the temperature rise that would carry exactly the metabolic heat. Plausible? | Reading a utility table physically |
| 2.5 | Electricity per kg of powder against NREL's 9 kWh/kg. Why the difference? | Energy per kg is a design fingerprint |

Then fill rows R0 to R5. Pick a *typical* maintenance rate in R0 rather than the one you
solved for in 1.3, so R5 does not simply return your own algebra. R5 still cannot test
much: R1–R4 carry the paper's totals. The glucose check is the diagnostic one.

## Part 3: think like a TEA analyst (about 20 minutes, no spreadsheet)

Write short answers on the *Part3* sheet.

- **3.1** Titer doubles to 60 g/L, with the same batch time and the same overall yield.
  First, is that physically possible? Check the O₂ uptake per m³ in each phase (growth and
  expression) against PRIMER §5.3–5.4, and read what Intelligen says about ovalbumin's
  solubility (p.8). Then: which slices move, and roughly how much? Estimate the new $/kg.
- **3.2** The plant is 10× larger. Same questions. The fermenters are already 136 m³: do
  you scale up or number up?
- **3.3** NREL's crude on-site cellulase costs $4.24/kg of protein (2007$). Intelligen's
  purified ovalbumin costs $38.99/kg of powder (2025$); put it per kg of protein first
  (step 1.5). List every difference between the two plants and rank them by how much of
  the ~9.8× gap per kg of protein you think each explains. The report's cost bridge
  (Figure 3) answers the same question with the full model.
- **3.4** Which three input numbers would you most want to verify before trusting $39/kg?

## When you are done

Open [`A1_SOLUTION.md`](A1_SOLUTION.md). Note anything that surprised you at the bottom of
this file. Those notes feed the Phase C design.

### Your notes

-
