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
debt at 8%, 35% tax, 10% IRR, 30 years. Our 2018$ equipment costs are deflated to 2007 with
CEPCI (525.4/603.1 = 0.871), the index NREL itself uses.

| Quantity | Ours | NREL | Difference |
|---|---|---|---|
| Glucose, kg/kg protein | 4.26 | 4.17 | +2.2% |
| O₂, mol/kg protein | 83.1 | 84 | −1.1% |
| Electricity, kWh/kg | 5.5 | 9 | −38% |
| **Cost, $/kg protein delivered** | **11.61** | **4.24** | **+174%, miss** |
| Cost with NREL's own capital convention | 6.05 | 4.24 | +43% |

**Diagnosis.** The stoichiometry and mass balance agree within 3%. The whole miss is
capital structure:
- **Fermenter purchase cost.** Our fermenter cost curve (Humbird's ACCE STRFERM quotes)
  prices a 300 m³ vessel at about $3.3M (2007$). NREL's vendor quotes (Appendix A) are
  $400,500 for the vessel plus $580,000 for its 800 hp agitator, about $0.9M in 2007$. That is
  **~3.5× lower**.
- **Installation and indirect factors.** Humbird's factors for the least expensive
  (outdoor) class give an effective Lang factor of 4.4. NREL's installation factors plus
  Table 27 indirects give about 2.7.
- **Maintenance plus insurance.** 9% of TCI per year in Humbird's convention, against
  about 2% for NREL (3% of ISBL maintenance, 0.7% of FCI insurance).
- **Result.** Our capital-related cost is $8.1/kg against NREL's ~$1.1/kg ($2.6/kg with
  NREL's convention; the rest of the +43% is our higher labour and building costs).

Electricity is lower because our aeration is power-optimal (about 0.3–0.5 vvm, 1–2 kW/m³);
NREL's 800 hp agitators are sized for peak.

**What this means.** We do not tune. NREL is a design report, not a price. NREL itself
reports that Genencor and Novozymes quoted enzyme costs ~47% above its figure ($0.50 vs
$0.34 per gallon of ethanol, i.e. ~$6.2/kg). Humbird's method is the one anchored to a real
price (anchor 1).

The gap does show that **capital conventions alone move the cost of a crude secreted
protein by a factor of ~2**. The results therefore carry a named structural sensitivity,
*capital basis*:
- Humbird/ACCE (base);
- NREL-style: vendor-quote fermenters, lighter factors, 2% fixed costs.

It appears in the tornado and the cost bridge.

## Anchor 3: Intelligen 2025 ovalbumin (consistency check)

Case file: `data/calibration/intelligen2025_ova.yaml`, in 2025$. Intelligen's own result,
recast into Humbird's capital convention, is $43.52/kg powder (exercise A1, step 1.4).

| Quantity | Ours | Intelligen | Difference |
|---|---|---|---|
| **Cost, $/kg powder (Humbird convention)** | **47.82** | **43.52** | **+9.9%, pass (±30%)** |
| Total capital investment | $147M | $92M | +60% |
| Glucose, kg/kg powder | 9.4 | 13.0 (syrup) | −28% |
| Electricity, kWh/kg powder | 11.3 | 27.1 | −58% |

**Diagnosis.** The total agrees partly through **compensating differences**, so it is a
weak pass:
- **Capital.** Ours is higher: Humbird's facility factors give an effective Lang factor
  of ~5 against Intelligen's 4. Intelligen does not state its microfiltration flux; ours is
  10 L/m²/h (EVERY patent, grade B), which needs a large membrane area.
- **Glucose.** Ours is lower, because our thermodynamic growth yield (0.52 g/g, which
  matches the measured K. phaffii 0.50–0.58 in `data/evidence/hosts.yaml`) is higher than
  Intelligen's assumed 0.40 g/g. Also, Intelligen's "glucose syrup" may not be pure glucose.
- **Electricity.** Ours is lower. Intelligen aerates at 1.2–1.6 vvm and runs a fertiliser
  section (evaporator plus rotary dryer). SuperPro's standard power also excludes chilled
  water, which Intelligen prices separately, whereas ours includes chiller electricity.

Each difference traces to a stated assumption on one side or the other; none is a bug.

## Anchor 4: Voutilainen 2021, recombinant case (consistency check)

Sources:
- Extraction: `data/calibration/voutilainen2021.yaml`. Every value carries its Sheet!Cell or
  page+quote. Their DCF is reproduced exactly: 9,007 €/t.
- Model inputs: `data/calibration/voutilainen2021_case.yaml`.

Basis and method:
- Money is 2019 €, converted at FX 1.12 in both directions, so FX cancels.
- Finance is theirs: 5%, 20 years, 20% tax, no depreciation.
- Their sugar use (a process input) is matched by solving for the product yield: Y_ps = 0.217.

| Quantity | Ours | Voutilainen | Difference |
|---|---|---|---|
| Sugar, kg/kg protein | 6.37 | 6.15 | +3.6% |
| Capital (ours TCI vs their FCI incl. sugar section) | 236 M€ | 128 M€ | +84% |
| **Cost, €/t protein (their DCF)** | **25,400** | **9,007** | **+182%, miss** |

**Diagnosis.** It is the same as NREL: the mass balance agrees, and the conventions differ.

| Convention change | Result (€/t) |
|---|---|
| Our model as is | 25,400 |
| Their fixed costs instead of Humbird's 9% of TCI (maintenance 1.5% of FCI, no insurance) | 18,200 |
| Plus the NREL-style capital basis | **12,400 (+37%)** |

The remaining gap is mostly labour: 5.4 M€ in our Humbird attention model against their
3.15 M€ (45 people). A further difference is their unitemised equipment list: 31.5 M€,
multiplied by 4.07.

## Summary: what the four anchors say

1. **Our method is exactly Humbird's.** It reproduces his baker's-yeast cost to 0.004%, and
   that cost sits on the market-implied price (anchor 1).
2. **Our mass and energy balances agree with all three published PF/enzyme designs.**
   Sugar is within 4%, and O₂ within 1% of NREL.
3. **Published PF costs are 2.7–2.8× lower than our base on the same process.** The reason is
   lighter capital and fixed-cost conventions (vendor-quote fermenters, Lang ~2.7–4, fixed
   costs of 1.5–2% of capital), not different biology. With the light conventions our model
   still lands above theirs, by +37% (Voutilainen) and +43% (NREL): the rest is our labour
   model and buildings. We are within 10% of Intelligen's total, which uses Lang 4 and heavy
   SuperPro overheads.
4. **We therefore report two capital conventions throughout.**
   - *Humbird (base)*: anchored to a real product price.
   - *Light (NREL-style)*: the convention of the published PF and enzyme TEAs.

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
