# A1 answer key (spoilers)

Numbers come from [`a1_solution.py`](a1_solution.py) and reproduce by running it. Paper
references are printed pages of `intelligen_ovalbumin2025`. Items marked *assumption* are
the hint factors from the *Inputs* sheet, not statements in the paper.

"$39/kg" in this exercise is the **gross** unit production cost ($38.99/kg). Intelligen's
headline figure of $36/kg is net of the fertiliser credit ($36.33/kg, Table 2).

## Part 1: accounting

**1.1 Where the money goes** ($/kg of powder; the plant makes 1,000 t/yr):

| Slice | Share | $/kg |
|---|---|---|
| Facility-dependent | 44% | 17.15 |
| Raw materials | 21% | 8.19 (Table 3: 8.12, a 0.99 ratio) |
| Utilities | 15% | 5.85 (Table 4: 5.88) |
| Labour-dependent | 7% | 2.73 |
| Waste treatment/disposal | 7% | 2.73 |
| Consumables | 5% | 1.95 |
| Laboratory/QC/QA | 1% | 0.39 |
| **Total** | | **38.99** |

At 1 kt/yr, capital-driven cost is the largest single slice. Sugar is only $4.69/kg,
about 12% of the total.

**1.2 Capital chain.**
- Working capital: 30/365 × (labour + materials + utilities + waste) = $1.60 M.
- DFC = (TCI − working capital)/1.05 = **$86.1 M**.
- PEC = DFC/4 = **$21.5 M**.

Working capital is under 2% of TCI, so it can be ignored in back-of-envelope work.

**1.3 The facility-dependent slice.**
- Depreciation (10 years, 5% salvage; *assumption*) = $8.18 M/yr.
- Insurance, local tax and factory expense (1%, 2% and 5% of DFC; *assumption*) = $6.89 M/yr.
- The residual, which we *solved for*, is maintenance: **$2.09 M/yr, 9.7% of PEC** (2.4%
  of DFC).

This is a consistency check, not a test. 9.7% sits at the high end of the usual 2–10%/yr
for equipment upkeep, so the hint factors are *compatible* with the 44% slice, but nothing
here confirms they are the ones SuperPro used.

The lesson: SuperPro's "unit production cost" includes depreciation and overheads, but
**no return on capital**. It is a cost of production, not a selling price.

**1.4 Humbird's convention.**
- The capital charge factor at 7.5% over 10 years is 0.146.
- Add 4% maintenance and 5% insurance and tax: 23.6% of TCI, or $21.7 M/yr, replacing the
  $17.15 M/yr facility-dependent slice.
- Unit cost becomes **$43.52/kg (+12%)** with no engineering change at all.

This is why Phase D puts every anchor on one convention before comparing anything.

**1.5 Per kg of protein.**
- The powder is 95% dry and 99% ovalbumin, so it is 0.941 ovalbumin by mass.
- That gives **$41.45/kg ovalbumin**, or $38.62 net of the fertiliser credit and $46.27 in
  Humbird's convention.
- All three sit in the upper-middle of GFI's egg-white band ($15.6–59.4 per kg protein).
  The band is wide mainly because it spans products of different purity (GFI p.31).

## Part 2: balances

**2.1 Recovery.** There are 342 batches per year.
- Broth ovalbumin: 30 g/L × 107 m³ = 3,210 kg per batch.
- Product: 2,924 × 0.941 = 2,750 kg per batch.
- Overall recovery: **0.857**.

The listed purification steps give **0.884**:
- UF retains 5^(−0.005) = 0.992. The 0.995 is a rejection coefficient, not a step yield;
  concentrating 5-fold keeps CF^−(1−σ).
- Precipitation catches 0.90.
- The basket centrifuge keeps 0.99.

The remaining ~3% (0.857/0.884 = 0.969) is unaccounted for, within the rounding of the
stated volumes. Intelligen gives no recovery for clarification or drying, and a harvest of
103.7 m³ instead of "approximately 107 m³" (p.7) would close the balance.

**2.2 Glucose.**
- The expression phase needs 3,210/0.28 = 11,464 kg of glucose per batch, and makes
  917 kg of cells on the side.
- The harvest holds 92 g/L × 107 m³ = 9,844 kg of cells. The growth phase must have made
  the other 8,927 kg, which took 22,317 kg of glucose.
- So **66% of the glucose goes into growing the catalyst**.
- Fed glucose is 34,123 kg per batch at 99% conversion, so the overall yield is
  **0.094 g/g**, against 0.28 in the expression phase alone.
- Annual glucose from this balance is 11,670 t, against Table 3's 13,021 t (**0.90**).
  The missing 10% is plausibly the seed train, the 2% cell-death reaction, or syrup that
  is not pure glucose. The paper does not let us tell.

The lesson: **yield is dominated by how many cells you grow per kg of product**. Here that
is 92 g/L of yeast to make 30 g/L of ovalbumin. The largest yield lever is higher
*specific* productivity (more product per cell), not a better expression-phase reaction.

**2.3 Oxygen and heat.**
- O₂ per batch: 18.3 t, i.e. **178 mol O₂ per kg ovalbumin**, about 2.1× NREL's 84.
- Metabolic heat per batch: 263 GJ, an average of **677 kW per fermenter** over the
  108-hour culture.

The biomass-heavy recipe roughly doubles aeration and cooling per kg of product compared
with NREL's cellulase design.

**2.4 Chilled water.** Each batch uses 18,078 t of chilled water. A temperature rise of
**3.5 K** would carry exactly the metabolic heat. Chilled-water loops typically run
5–10 K (textbook), so the chilled water carries *more* than the metabolic heat. That is
consistent: agitator power ends up as heat too, and the 15 °C precipitation step is also
chilled.

**2.5 Electricity.** Intelligen uses **27 kWh per kg of powder**, against NREL's 9 per kg
protein. The like-for-like gap is even larger than 3×, because NREL's 9 includes its
chillers (rated at 0.56 kW per ton of refrigeration, a COP of about 6.3; NREL p.55, PRIMER
§5.3) while Intelligen prices chilled water separately. The reasons:
- 2.1× more O₂ per kg;
- aeration at 1.2–1.6 vvm against NREL's ~0.3, and compressor work scales with air volume;
- centrifuges, filtration pumps and the spray-dryer and evaporator fans.

**Rebuild check** (workbook rows R0–R5). Take a mid-range maintenance rate of 6% of PEC
rather than the 9.7% solved for in 1.3, and take glucose from your own balance, which is
$0.49/kg below Table 3. The rebuilt unit cost is then **$37.66/kg (−3.4%)**, within the
20% criterion. Swapping only the maintenance rate gives $38.19 (−2.0%).

Treat this as a bookkeeping check, not a test. R1–R4 reuse the paper's own totals, which
fix $32.17 of the $38.99. R5 therefore stays within 20% for any maintenance rate from 0 to
48% of PEC per year (with the balance glucose), and for any annual glucose from 0 to 37 kt
(at 6% maintenance). The glucose check against Table 3 (0.90 in 2.2) is the diagnostic
one.

## Part 3: rough what-ifs

These are my estimates, with the assumptions in `a1_solution.py`. Your numbers can
legitimately differ. They use Intelligen's own accounting: SuperPro costs at 1 kt/yr, with
a 44% facility slice and equipment scaled by the six-tenths rule. The full model answers
the same questions at 10 kt/yr, sometimes differently; each item says where.

**3.1 Titer doubles at the same batch time and yield.** First, the physics, phase by
phase.

The growth phase is the hard one. It burns 22,317 kg of glucose in 36 h, which takes
0.5456 × 22,317 kg = 12,176 kg (380.5 kmol) of O₂. Even spread over the full 107 m³
harvest volume, that is **≈99 mmol/L/h**. The real volume is smaller, so the true average
is higher: 255 at the 41.5 m³ start. That already exceeds the ≈53 a jacket can cool at
136 m³ on PRIMER §5.3's illustrative numbers, so Intelligen's design needs internal coils
or an external loop as it stands. At the same overall yield and stoichiometry, doubling the
titer doubles the cells, and with them the growth-phase uptake: at least **≈198 mmol/L/h**.
That is above the 150 mmol/L/h cap the model uses, and close to the ~200 that Humbird
(2021) calls about the practical maximum. And 60 g/L is 1.2× the ~50 g/L that Intelligen
calls ovalbumin's practical solubility limit (p.8), although that figure has no source and
OVA dissolves at far higher concentrations (report, section 2.4).

As posed, the what-if is **probably infeasible**. The realistic versions are twice the
titer at the same *rate* (longer batches), or a cooling and O₂ upgrade that costs money.
The full model frames it differently. It keeps the cell density and lets each cell secrete
more (4.7 → 11 mg/g/h), so 60 g/L in 72 h stays feasible: its ceiling at 72 h is about
74 g/L, set by the vessel's volume (more product needs more sugar feed, and a batch must
start at least 30% full), not by O₂ (report, section Q3). Whether a strain can double its
specific productivity is the biological question the what-if hides.

If it were feasible anyway: about **$33/kg (−15%)**, range $31–35.
- What falls: fermentation and clarification capital (half the broth volume, at the
  0.6 scaling exponent), volume-driven materials, consumables and waste.
- What stays: sugar (yield unchanged), ammonium sulfate (it scales with product, not
  broth), utilities (same O₂ per kg, more power per mol), drying, most labour and
  overheads.

**In Intelligen's accounting, doubling titer does not halve cost.** The what-if fixes the
overall yield, and the 44% facility slice shrinks only with the six-tenths power of the
broth volume. The full model gives a different answer at 10 kt/yr: cost falls roughly as 1/titer until
the feasibility ceiling (report, section Q1). Doubling BLG titer from 30 to 60 g/L in a 72 h
production phase cuts the price by nearly half ($21.2 → $11.9/kg, −44%). There, fermenters
are numbered up, so their number halves with the broth volume, and at a fixed cell density
fewer cells are grown per kg of product. In both
views, doubling titer *at the same batch time* runs into the limits of PRIMER §5.

**3.2 Ten times the scale:** about **$30/kg (−22%)**, range $27–33.
- Fermenters are numbered up (50 × 136 m³), while downstream equipment scales up. An
  overall capital exponent of ~0.8 cuts facility cost per kg by ~37%. Labour per kg falls
  ~70%.
- Materials, utilities, waste and consumables are **$18.7/kg in this design and do not
  move with scale**.

So in Intelligen's accounting at 1 kt/yr, what scale leaves behind is set by yield (sugar,
O₂, cooling) and by downstream chemistry (ammonium sulfate, waste, membranes). That is a
property of this design and its accounting, not a general rule. In the full model, with
Humbird's capital convention, capital-related costs (capital charge, maintenance,
insurance and tax) are ~68% of the base-case BLG price at 10 kt/yr (report, Table 5) and
~67% of the physical-limit floor at 100 kt/yr (report, section Q4). Scale helps little
beyond about 10 kt/yr, because the plant then adds fermenters rather than bigger ones
(report, section Q6). From there, capital per kg is set by productivity (g/L/h), not by scale.

**3.3 The bridge from $4 to $41 per kg of protein.** Compare per kg of protein on both
sides (step 1.5): $41.45 − $4.24 = **$37.21/kg, a 9.8× gap**. Below is my rough split for
Intelligen's design and accounting, per kg of powder. Each row is uncertain by ±50%. The
midpoints sum to $33.5/kg; on a protein basis, the powder's 94% ovalbumin content adds
~$2.5/kg, which brings the total close to the gap.

The report's cost bridge (section Q2) does this with the full model, from an NREL-style
cellulase ($7.6/kg in 2025$) to the base BLG concentrate at 10 kt/yr ($21.2/kg). Its
largest steps are downstream processing and drying (+$7.0), the titer drop from 50 to 30 g/L
(+$5.1) and the capital convention (+$2.7). The ovalbumin isolate adds $4.7 more than the
concentrate. Titer weighs more there than in my split (+$2–4): at 10 kt/yr and a fixed cell density, both
fermenter capital and the sugar spent on cells scale with 1/titer.

| Difference | NREL cellulase | Intelligen ovalbumin | Rough share of the gap |
|---|---|---|---|
| Purification and drying | None: whole broth used on site | Centrifuges, MF, UF, precipitation, washing, spray-drying, fertiliser section | +$11–16/kg: capital, ammonium sulfate, consumables, waste, drying energy |
| Scale, vessel size, accounting | ~4–5 kt/yr, 300 m³, capital recovered over 30 years in a DCF | 1 kt/yr, 136 m³, SuperPro-style facility cost (with the factory overhead in hint H5) | +$9–14/kg |
| Yield and oxygen | 0.24 g/g, 84 mol O₂/kg | 0.094 g/g, 178 mol O₂/kg | +$5–7/kg: about 3× the glucose per kg, twice the aeration and cooling |
| Titer | 50 g/L | 30 g/L | +$2–4/kg |
| Cost year | 2007$ | 2025$ | +$1–2/kg on capital and labour |
| Glucose price | $0.57/kg (2007$, NREL Table 29) | $0.36/kg | −$1 to −3/kg: this one works *in Intelligen's favour* |
| Product and host | Crude cellulase, *T. reesei* | Food-grade ovalbumin, *K. phaffii*, methanol-induced | Folded into the rows above; methanol adds a little |

**3.4 Three numbers to verify first.**
1. **Titer 30 g/L.** Its public basis is a patent maximum for *ovomucoid*. That is grade B
   evidence for ovomucoid but only grade D (an analogy) for ovalbumin, a different and
   larger protein.
2. **92 g/L of cells at harvest.** It sets two thirds of the glucose and the oxygen, and
   it is unsourced.
3. **Lang factor 4.** Intelligen sources it to GFI's review of Humbird (its ref. [31],
   p.16). It is below Petrides' 4.7 for an outdoor lysine plant (Humbird Table 3.1) but
   above NREL's 3.1 for its ethanol plant (NREL Table 28, p.62). The definitions
   differ: Intelligen's is DFC/PEC, NREL's FCI/PEC and Humbird's TCI/PEC. The full model
   brackets it with two conventions: Humbird's price-anchored one (effective Lang factor
   ~6.5) and a design-report one (the published designs use 2.7–4; report, sections 2.5
   and 3). If the right class is 5–6, capital and the 44% slice are understated by 25–50%.

The 99% purity from a single ammonium-sulfate precipitation is a close fourth.
