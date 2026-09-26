# Calibration record

Protocol (PLAN.md, honesty rules 3 and 7):
- The model's structure is frozen before any anchor is run: cost curves, installation
  factors, labour model, maintenance and insurance fractions.
- Each anchor changes only its own process inputs, prices, cost year and financing.
- Misses are recorded here **before** anything is changed, with their diagnosis.
- An anchor is either a **reality check** (a market price) or a **consistency check**
  (another model).

Reproduce everything with:
- `.venv/bin/python -m pytest tests/test_humbird_yeast.py tests/test_calibration.py`
- `.venv/bin/python -m pftea.calibration`

## Anchor 1: Humbird 2021 baker's yeast (software check + reality check)

Our port of the SI sheet A.1 (`src/pftea/humbird_yeast.py`) reproduces Humbird's cost of
production: **$1.8899 vs $1.8899/kg dry (+0.004%)**, 2018$. All 35 intermediate quantities
(glucose, air, power, equipment, labour, capital) are within 0.1%.
- *Software check:* **pass**.
- *Reality check:* Humbird infers ~$1.90/kg actual cost from a $2.20–2.80/kg wholesale
  price and a 33% margin (App. A). The method sits on that price: **pass**, with the
  caveat that the margin is his assumption.

Findings from the port:
1. **Volume balance.** A.1's broth-volume update (column W) *adds* water stripped by
   the off-gas and *subtracts* metabolic water (−dt × avg(stripped + produced)). The
   physical balance has the opposite signs. We reproduce it exactly in the port. Our
   PF fermenter (`pf_ferm.py`) uses a full liquid mass balance instead. The effect on
   Humbird's batch length is a few percent. We do not claim it is an error without asking
   him; it may be a sign convention we have not understood.
2. **Solver tolerance.** Humbird's VBA solver stops at OUR ≈ 149.9 against the 150 cap. Our
   exact solve gives μ 0.1% higher; this explains the residual differences.
3. **Compressor power** (found by the engineering evidence search). A.1's compressor formula
   (column BD) raises the bottom pressure to the power 1.4 and divides by 1.4. An ideal
   adiabatic compression uses the exponent (k−1)/k = 0.286 and the prefactor k/(k−1) = 3.5.
   At 2.1 bar Humbird's form gives about 1.6× the adiabatic power at 80% efficiency. We keep
   it (fidelity to anchor 1), so our compressor power is conservative. The effect is small:
   compressors are ~0.2 of 1.1 kW/m³ of aeration power at OTR 150, i.e. roughly $0.1/kg
   protein in the PF base case.

## Anchor 2: NREL 2011 on-site cellulase (consistency check)

Case file: `data/calibration/nrel2011_cellulase.yaml`, in 2007$, with NREL financing: 60%
debt at 8% (drawn during construction, with construction interest), 35% tax, 10% IRR, 30
years. Our 2018$ equipment costs are deflated to 2007 with CEPCI (525.4/603.1 = 0.871), the
index NREL itself uses. NREL's own prices are used where NREL states them (ammonia, operator
salary, 90% labour burden, Area 400 nutrients). NREL's $4.24/kg is per kg of protein
*produced* (audit R4-3), so no delivered-fraction correction is applied.

| Quantity | Ours | NREL | Difference |
|---|---|---|---|
| Glucose, kg/kg protein | 3.87 | 4.17 | −7.1% |
| O₂, mol/kg protein | 83.1 | 84 | −1.0% |
| Electricity, kWh/kg | 5.4 | 9 | −40% |
| **Cost, $/kg protein, price-anchored (Humbird) capital** | **10.78** | **4.24** | **+154%, miss** |
| Cost with NREL's own (design-report) capital convention | 5.75 | 4.24 | +36% |

**Diagnosis.** Sugar and O₂ agree within 7%; electricity does not (below). The cost miss is
capital structure:
- **Fermenter purchase cost.** Humbird's ACCE STRFERM quotes, extrapolated above 196 m³ with
  their own power-fit exponent 0.69, price a 300 m³ vessel with agitator at $2.9M (2007$).
  NREL's vendor quotes (App. A, F-400 + A-400) are $0.99M: **2.9× lower**.
- **Installation and indirect factors.** Humbird's least expensive (outdoor) class gives an
  effective Lang factor of 4.4; NREL's installation factors plus Table 27 indirects give ~3.1
  (our light convention, which keeps Humbird's buildings and missing-capital allowance, 3.8).
- **Maintenance plus insurance.** 9% of TCI per year in Humbird's convention, against about
  2% for NREL (3% of ISBL maintenance, 0.7% of FCI insurance).
- **Result.** Capital-related cost is $7.6/kg (Humbird convention) against $2.5/kg with
  NREL's convention; the rest of the +36% is labour ($0.45/kg), buildings and our cleaning
  (CIP) cost, which NREL does not itemise.

Electricity is lower because our aeration is power-optimal (about 0.3–0.5 vvm, 1–2 kW/m³);
NREL's 800 hp agitators are sized for peak.

**What this means.** We do not tune. NREL is a design report, not a price. NREL itself
reports that Genencor and Novozymes quoted enzyme costs ~47% above its figure ($0.50 vs
$0.34 per gallon of ethanol, i.e. ~$6.2/kg). Humbird's method is the one anchored to a real
price (anchor 1), although that anchor rests on one product and an assumed 33% margin.

The gap shows that **capital conventions alone move the cost of a crude secreted protein by
a factor of ~2**. The results therefore carry a named structural sensitivity, *capital
convention*:
- price-anchored (Humbird/ACCE; base);
- design-report (NREL-style): vendor-quote fermenters, lighter factors, ~2% fixed costs.

It appears as a bar in the tornado and as a step in the cost bridge.

## Anchor 3: Intelligen 2025 ovalbumin (consistency check)

Case file: `data/calibration/intelligen2025_ova.yaml`, in 2025$. Intelligen's own result,
recast into Humbird's capital convention, is $43.52/kg powder (exercise A1, step 1.4).
Caution: the base product yield and production-phase maintenance are *derived from this
anchor's* Eq. 2 (base.yaml, audit R2-Q2/R6-C2), so its expression-phase glucose matches by
construction; the growth phase, downstream and costs are independent.

| Quantity | Ours | Intelligen | Difference |
|---|---|---|---|
| **Cost, $/kg powder (Humbird convention)** | **49.47** | **43.52** | **+13.7%** |
| Total capital investment | $147M | $92M | +60% |
| Glucose, kg/kg powder | 10.5 | 13.0 (syrup) | −19% |
| Electricity, kWh/kg powder | 10.1 | 27.1 | −63% |

**Diagnosis.** The differences trace to stated assumptions on one side or the other:
- **Whole fermenters.** Our downstream recovers 0.82 of the protein against Intelligen's
  0.86 (we keep Behm's 97.5% MF recovery and a 2% dryer loss), so the plant needs 5.07
  vessel-equivalents: 6 whole fermenters against Intelligen's 5. With 5 (4.6 more operating
  days per year) the miss is +6.8%.
- **Capital.** Ours is higher: Humbird's facility factors give an effective Lang factor of ~5
  against Intelligen's 4.
- **Glucose.** Ours is lower in the growth phase: our thermodynamic growth yield (0.57 g/g
  maximum, ~0.53 effective with maintenance; the measured *K. phaffii* value is 0.50–0.56) beats
  Intelligen's assumed 0.40 g/g (Eq. 1). Intelligen's "glucose syrup" may also not be pure
  glucose.
- **Electricity.** Ours is lower. Intelligen aerates at 1.2–1.6 vvm and runs a fertiliser
  section (evaporator plus rotary dryer). SuperPro's standard power also excludes chilled
  water, which Intelligen prices separately, whereas ours includes chiller electricity.

This is a consistency check with compensating differences, not a validation of the cost.

## Anchor 4: Voutilainen 2021, recombinant case (consistency check)

Sources:
- Extraction: `data/calibration/voutilainen2021.yaml`. Every value carries its Sheet!Cell or
  page+quote. Their DCF is reproduced exactly: 9,007 €/t.
- Model inputs: `data/calibration/voutilainen2021_case.yaml`.

Basis and method:
- Money is 2019 €, converted at FX 1.12 in both directions, so FX cancels.
- Finance is theirs (audit R4-6): 5% on after-tax (revenue − opex), no depreciation, capital
  1.03 × FCI, a start-up year at 50% revenue and variable cost, revenue +1%/yr, opex rising
  from 11.02 to 13.10 M€.
- Their sugar use (a process input) is matched by solving for the product yield: Y_ps = 0.217.
  The sugar row therefore agrees by construction.
- Their UF concentrates to 28% dry matter before the spray dryer.

| Quantity | Ours | Voutilainen | Difference |
|---|---|---|---|
| Sugar, kg/kg protein | 6.37 | 6.15 | +3.7% (by construction) |
| Capital (ours TCI vs their FCI incl. sugar section) | 204 M€ | 128 M€ | +59% |
| **Cost, €/t protein (their DCF)** | **21,880** | **9,007** | **+143%, miss** |

**Diagnosis.** As for NREL, the conventions differ:

| Convention change | Result (€/t) |
|---|---|
| Our model as is | 21,880 |
| Their fixed costs instead of Humbird's 9% of TCI (maintenance 1.5% of FCI, no insurance) | 15,610 |
| Plus the NREL-style capital basis | **11,100 (+23%)** |

The remaining gap is mostly labour: 5.6 M€ in our Humbird attention model against their
3.15 M€ (45 people). A further difference is their unitemised equipment list: 31.5 M€,
multiplied by 4.07.

## Summary: what the four anchors say

1. **Our method is exactly Humbird's.** It reproduces his baker's-yeast cost to 0.004%, and
   that cost sits on the market-implied price (anchor 1; one product, and the margin is his
   assumption).
2. **Sugar and O₂ agree with the two designs that state them independently** (NREL within
   7% and 1%; Voutilainen's sugar is matched by construction; Intelligen's expression phase is
   matched by construction and its growth phase differs by design). **Electricity does not**:
   ours is 40–63% lower, for the reasons given under each anchor. These are consistency
   checks, not calibration fits (audit R7-M6).
3. **Published PF costs are 2.3–2.5× lower than our base on the same process.** The reason is
   lighter capital and fixed-cost conventions (vendor-quote fermenters, Lang ~3–4, fixed costs
   of 1.5–2% of capital), not different biology. With the light conventions our model still
   lands above theirs, by +23% (Voutilainen) and +36% (NREL): the rest is our labour model,
   buildings and cleaning. We are within 14% of Intelligen's total (7% with its five whole
   fermenters), which uses Lang 4 and heavy SuperPro overheads.
4. **We therefore report two capital conventions throughout.**
   - *Price-anchored capital (Humbird method, base)*: anchored to one real product price.
   - *Design-report capital (NREL-style)*: the convention of the published PF and enzyme TEAs.

   Their spread is the largest structural uncertainty in PF protein economics.

## Record of changes

Misses are re-recorded, never tuned away. Each entry says what moved and why.

**2026-09-26, after the Phase B evidence (prices, engineering, downstream).** Structure unchanged.

| Anchor | Before | After | Cause |
|---|---|---|---|
| NREL, Humbird convention | +136% | +174% | Deflator 2018→2007 changed from Humbird's PPI (0.70) to CEPCI (0.87), NREL's own index |
| NREL, light convention | +31% | +43% | Same |
| Intelligen, total | −3.6% | +9.9% | Base cost index 1.25 → 1.33 (CEPCI family, sourced), ~+5 points; DSP evidence (MF flux 10 L/m²/h, membrane life 0.5 yr, UF-fed dryer), ~+5 points |
| Intelligen, TCI | +35% | +60% | Same |
| Voutilainen, Humbird convention | +161% | +182% | DSP evidence and sourced utility prices; the index barely moves (2019 vs 2018) |
| Voutilainen, light convention | +24% | +37% | Same |

The mass balances did not move. Test bands in `tests/test_calibration.py` were re-centred on
the new values, and light-convention tests were added.

**2026-09-26, model fix: growth throttled by heat as well as O₂.** `pf_ferm.otr_max` budgets
heat at 460 kJ/mol O₂. Growth, computed from formation enthalpies, releases about 490 kJ/mol. So
with an O₂ cap above ~180 mol/m³/h, the growth phase broke the 25 kW/m³ cooling cap and the
design was flagged infeasible. Growth is now also slowed to the cooling cap. The base case, all
four anchors and all tests are unchanged, because at the 150 cap heat never binds. The change
affects the tornado's high O₂-cap end and Monte Carlo draws with high caps.

**2026-09-27, audit batch 2 (docs/AUDIT.md).** Model structure changed by the audit decisions;
anchors re-run, misses re-recorded, test bands tightened to ±5 points.

| Anchor | Before | After | Cause |
|---|---|---|---|
| NREL, Humbird convention | +174% | +154% | Per kg produced, not delivered (R4-3, −25 points); construction interest on the loan (R4-5, +); NREL's own prices (ammonia, salary, burden, nutrients); CIP; fermenter exponent 0.69 above 196 m³ (R3-F3) |
| NREL, light convention | +43% | +36% | Same, plus NREL's own 2007$ fermenter quote (R4-17) |
| NREL, glucose | +2.2% | −7.1% | Per-produced basis (R4-8) |
| Intelligen, total | +9.9% | +13.7% | Isolate dryer fed the cake (R3-F4, −); two-stage centrifuge wash (R3-F1, +); whole fermenters, 6 vs 5 (R3-F8, ~+7 points); spent-cell disposal (+2.5 points); CIP; production stoichiometry derived from this anchor |
| Intelligen, glucose | −28% | −19% | Production-phase stoichiometry now reproduces Eq. 2 |
| Voutilainen, Humbird convention | +182% | +143% | Their own DCF conventions (R4-6); membranes and skid from sourced dairy costs (P-1); UF to their 28% dry matter |
| Voutilainen, light convention | +37% | +23% | Same, plus maintenance on FCI rather than ISBL (R4-7) |
