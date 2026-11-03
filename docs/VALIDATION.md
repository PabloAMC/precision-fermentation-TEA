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
   At 2.1 bar Humbird's form gives about 1.6× the adiabatic power at 80% efficiency (the US-unit
   constant 8130 belongs to hp = scfm·T₁/(8130·a)·(r^a − 1) with a = (k−1)/k; the cell puts k where
   a belongs). The port keeps it, to reproduce the workbook. Since the follow-up review (H1) the PF
   model uses the textbook form (`fermentation.compressor_kW_adiabatic`, tested against the US-unit
   form); the workbook formula is kept as `fermenter.compressor_formula: humbird_a1` and changes the
   PF cost by about $0.02/kg (review HM-7 had estimated it at about zero; v2 said ~$0.1/kg).
4. **kLa exponent in print.** The paper prints Eq. A.8 with a superficial-velocity exponent of 0.2;
   the workbook (A.1!C95:F95) and our port use 0.7. The port follows the workbook (review HM, D1).
5. **What the anchor constrains** (review SC-3/HM-2). Capital-related charges are less than half
   of the yeast cost, and the market band depends on how Humbird's 33% margin is read ($1.47–1.88
   if a share of the price, $1.65–2.11 if a mark-up). With a lighter, NREL-like capital set
   (investment 3.2× listed equipment, fixed costs 1.2% + 0.7% a year) the workbook gives $1.37,
   below both bands; with Humbird's factors and NREL-like fixed costs, $1.62. The anchor therefore
   favours Humbird's factors and fixed costs, loosely, and says nothing about fermenter prices
   beyond its own bubble column ($779k per 199 m³, 2018$). `results/analyses.json`,
   `calibration.bakers_yeast_stacks`.

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
| Electricity, kWh/kg | 4.9 | 9 | −45% |
| **Cost, $/kg protein, price-anchored (Humbird) capital** | **7.81** | **4.24** | **+84%, miss** |
| Cost with NREL's own (design-report) capital convention | 6.08 | 4.24 | +43% |

**Diagnosis.** Sugar and O₂ agree within 7%; electricity does not (below). Since the Phase F review
both conventions use NREL's own fermenter quote (App. A, F-400 + A-400, $0.99M per 300 m³ in 2007$;
v2 priced Humbird's aseptic ACCE vessel at 2.9× that). The remaining cost miss is:
- **Installation and indirect factors.** Humbird's least expensive (outdoor) class gives an
  effective Lang factor of 5.1 here (with the 20% missing-equipment allowance); NREL's installation
  factors plus Table 27 indirects give ~3.1 (our light convention, which keeps Humbird's buildings
  and missing-capital allowance, 4.2).
- **Maintenance plus insurance.** 9% of TCI per year in Humbird's convention, against about
  2% for NREL (3% of ISBL maintenance, 0.7% of FCI insurance).
- **Result.** Capital-related cost is $4.6/kg (Humbird convention) against $2.8/kg with
  NREL's convention; the rest of the +42% is labour ($0.45/kg), buildings, the 20%
  missing-equipment allowance and our cleaning (CIP) cost, which NREL does not itemise.

Electricity is lower because our aeration is power-optimal (about 0.3–0.5 vvm, 1–2 kW/m³);
NREL's 800 hp agitators are sized for peak.

**What this means.** We do not tune. NREL is a design report, not a price. NREL itself
reports (p.40) that in February 2010 Genencor and Novozymes, announcing new cellulase products, "both cited an
enzyme cost contribution of approximately $0.50/gal ethanol", against its own $0.34 ($4.24/kg protein): about
$6.2/kg protein at NREL's loading (derived). NREL explains the gap (p.42): transport, a standalone plant's overheads
and a higher return. *Verified in the OSTI copy of the report on 2026-11-03; data/calibration/nrel2011_cellulase.yaml.*
Against that company figure our Humbird-convention cost is +25% and the design-report convention -3% (the panel
shows it as a 'company figure' check). Humbird's method is the one anchored to a real
price (anchor 1), although that anchor rests on one product and an assumed 33% margin.

The gap shows that **accounting conventions alone move the cost of a crude secreted protein by
about 1.3×** once the fermenters are priced alike (2× in v2, when the aseptic vessel price was part
of the gap). The results therefore carry two named structural sensitivities:
- *capital convention*: price-anchored (Humbird factors and fixed costs; base) or design-report
  (NREL-style factors, ~2% fixed costs);
- *fermenter price basis*: vendor quote (base) or Humbird's aseptic cell-culture vessels.

Both appear as bars in the tornado; the convention is also a step in the cost bridge.

## Anchor 3: Intelligen 2025 ovalbumin (consistency check)

Case file: `data/calibration/intelligen2025_ova.yaml`, in 2025$. Intelligen's own result,
recast into Humbird's capital convention, is $43.52/kg powder (exercise A1, step 1.4).
Caution: the base product yield and production-phase maintenance are *derived from this
anchor's* Eq. 2 (base.yaml, audit R2-Q2/R6-C2), so its expression-phase glucose matches by
construction; the growth phase, downstream and costs are independent.

| Quantity | Ours | Intelligen | Difference |
|---|---|---|---|
| **Cost, $/kg powder (Humbird convention)** | **42.00** | **43.52** | **−3.5%** |
| Total capital investment | $114M | $92M | +24% |
| Glucose, kg/kg powder | 10.6 | 13.0 (syrup) | −19% |
| Electricity, kWh/kg powder | 9.6 | 27.1 | −65% |

**Diagnosis.** The differences trace to stated assumptions on one side or the other:
- **Whole fermenters.** Our downstream recovers 0.82 of the protein against Intelligen's
  0.86 (we keep Behm's 97.5% MF recovery and a 2% dryer loss), so the plant needs 5.1
  vessel-equivalents: 6 whole fermenters against Intelligen's 5.
- **Capital.** Ours is higher: Humbird's facility factors and the 20% missing-equipment allowance
  give an effective Lang factor of 6.0 against Intelligen's 4. With vendor-quote fermenters the
  equipment itself is close to theirs; in v2, with aseptic vessel prices, our capital was +60%.
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
| Sugar, kg/kg protein | 6.28 | 6.15 | +2.2% (by construction) |
| Capital (ours TCI vs their FCI incl. sugar section) | 131 M€ | 128 M€ | +1.8% |
| **Cost, €/t protein (their DCF)** | **16,345** | **9,007** | **+81%, miss** |

**Diagnosis.** Capital now agrees within 2% (v2: +59%, from the aseptic fermenter prices). The
miss is the fixed-cost rule and the factors:

| Convention change | Result (€/t) |
|---|---|
| Our model as is | 16,345 |
| Their fixed costs instead of Humbird's 9% of TCI (maintenance 1.5% of FCI, no insurance) | 12,329 (+37%) |
| Plus the NREL-style capital basis | **11,423 (+27%)** |

The remaining gap is mostly labour: 5.6 M€ in our Humbird attention model against their
3.15 M€ (45 people). A further difference is their unitemised equipment list: 31.5 M€,
multiplied by 4.07.

## Check 5: capital against a real plant (added 2026-10-25)

**What it is.** A check of the base plant's capital against the one purpose-built precision-fermentation
plant that discloses its cost, fermentation volume and output: Liberation Labs, Richmond, Indiana
($115M, four 150 m3 fermenters, 600-1,200 t of protein a year; data/evidence/plants.yaml, grade C).
It is a check, not a calibration: no parameter is tuned to it. Code: `benchmarks.plant_cost_check`,
results key `plant_cost_check`.

**How.** The plant is 12 times smaller than the model's (600 against 7,200 m3), so its cost per m3 is
scaled with the six-tenths rule: per m3, cost/m3 x (7,200/600)^(n-1), with n = 0.5-0.7.

| | $ per m3 of fermentation volume | $ per (t/yr) of protein |
|---|---|---|
| Model, base BLG plant | 68,100 | 49,000 |
| Liberation Labs as disclosed | 192,000 | 96,000-192,000 |
| Liberation Labs scaled to 7,200 m3, n = 0.5 / 0.6 / 0.7 | 55,300 / 70,900 / 90,900 | 27,700-55,300 / 35,500-70,900 / 45,500-90,900 |

**What it says.** The model's capital per m3 sits inside the scaled band, near its middle at the
usual exponent of 0.6. Two cautions. Liberation Labs is unfinished and paused for funding, so its
$115M is likely a floor. And the band moves by about +/-30% over the exponent range. Solar Foods'
gas-fermentation Factory 02 (EUR 134M for 3.2 kt/yr of whole-cell protein, about $48,600 per t/yr)
lands near the model's $49,000 per t/yr, but it is a different process (hydrogen, no purification)
and the match is a coincidence. Whole-cell biomass plants cost far less per t/yr: Quorn's brownfield expansion about $9,800, Angel
Yeast's planned line about $6,800. They are a floor: they skip purification and sell wet or whole cells.

## Check 6: predictions of measured physiology (added 2026-11-03)

**What it is.** The growth model works out, from thermodynamics alone (Heijnen dissipation, Tijhuis maintenance,
element and electron balances), how much sugar becomes cells, how much O2 cells use and how much heat they
release. None of the measurements below is a model input, so each is a prediction. Code:
`calibration.physiology_record`; pinned in `tests/test_calibration.py`; shown in the panel's "Checks against
reality". Recorded before any change, as the protocol requires.

| Prediction (K. phaffii, 30 C) | Model | Measured | Result |
|---|---|---|---|
| Cell yield on glucose, upper limit (g/g) | 0.571 | 0.544-0.584 (Maurer 2006; Rebnegger 2016, 2024) | **pass** |
| Heat per mol O2, growing cells (kJ) | 506 | 430-480 (Gnaiger and Kemp, many organisms); 500 (Cooney) | near miss, +1% above the top |
| Cell yield on glucose, base fed-batch growth phase (g/g) | 0.507 | 0.37-0.50 (Shemesh 2024, three strains) | near miss, +1% |
| Cell yield on methanol, chemostat at 0.1/h (g/g) | 0.447 | 0.40 (Tomas-Gamisans 2018) | **miss, +12%** |
| O2 uptake on methanol at 0.1/h (mmol/g/h) | 6.46 | 8.22 +/- 0.37 | **miss, -21%** |
| Cell yield on glycerol, chemostat (g/g) | 0.466 | 0.63-0.71 | **miss, -26%** |
| O2 uptake on glycerol at 0.1/h (mmol/g/h) | 4.14 | 2.04 +/- 0.11 | **miss, +103%** |

**Diagnosis.**
- *Glucose passes.* Every product case grows and produces on glucose, so the result that matters most is
  inside the measured range. The heat per O2 is at the top of the measured spread, so the model's cooling
  load is, if anything, a few per cent conservative; in the base it binds during growth (24.4 of 25 kW/m3).
- *The fed-batch near miss* is expected: Shemesh's strains made ethanol (Crabtree effect), which lowers
  their yield; the model makes none.
- *Methanol missed by 12-21%* (as first recorded): Heijnen's dissipation gave a yield of 0.447 g/g and an O2
  uptake of 6.46 mmol/g/h. The element and electron balances are not at fault: the miss is the energy
  cost of growth, which the correlation sets. **Fixed the same day (Pablo: "take the best possible
  decisions")**: the growth energetics on methanol now come from K. phaffii's measured yield
  (base.yaml hosts.kphaffii.yx_methanol_g_g = 0.40; thermo step 9 solves the dissipation, 844 against
  Heijnen's 698 kJ/C-mol). The yield row is then an input, not a test. The O2 uptake, which is not
  fitted, moves from -21% to -7% (7.68 against 8.22 +/- 0.37): the fix is physical, not a curve fit.
  Effect on results (methanol-fed cases only: academic albumin, lactoferrin Lv 2023, beta-casein, the
  albumin and lactoferrin methanol variants, the two heme strains): +0.07% to +0.62% on the price, no
  change in feasibility; O2 use in production stays near 30% of supply. Sections rerun: scenarios,
  monte_carlo, equivalents, lactoferrin, casein, albumin, heme.
- *Glycerol misses badly* (K. phaffii is known for unusually high yields on glycerol). No case uses
  glycerol, so no result changes. It shows the Heijnen correlation does not carry over to every feed:
  agreement on glucose is a measured match, not a property of the method. Not fixed, by decision: a glycerol
  parameter would change no result (no artificial complexity). If a glycerol-fed case is ever added, set
  its yield from the same paper (0.67 g/g) as for methanol.

**Lactoferrin reconciliation as a consistency row.** The Intelligen lactoferrin comparison above (review L)
now appears in the panel next to the other model-to-model checks: ours is 64% (membranes only) and 52% (ion
exchange) below their cost of production with their design inputs. It has no tolerance of its own; the
panel borrows the Intelligen ovalbumin anchor's +/-30% and says so.

## Next checks that need new evidence

Status after the research pass of 2026-11-03 (notes in references/leads/, unverified unless stated):
1. **Food and feed enzyme prices per kg protein.** Done as far as public data allow (check 7): Lynd 2017, trade
   unit values and EFSA's protein contents, all read in full. They bound the price only within ~7x, because the
   product form behind a trade figure is unknown. Context, not a check.
2. **Enzyme makers' cellulase cost in NREL 2011.** Done: verified (anchor 2 above; a panel check).
3. **Recombinant chymosin.** Not usable: only small-pack distributor prices were found (about $20,000-30,000
   per kg chymosin protein), which say nothing about production cost.
4. **More real plant costs.** Done in part: Novozymes Blair (check 7). Amyris Barra Bonita: the cost is verified
   in the 2023 court filing ($155M estimated total; plants.yaml), but the fermentation volume (reported as 1,440 m3)
   is not, because Amyris's pages block automated readers; it becomes a check once the volume is read in a source.
5. **Pilot-scale O2 and heat data for K. phaffii.** Not available to the project.
6. **The pre-registered priors** (docs/SCOPE.md) are scored at release.

## Check 7: a second real plant, and a market value for secreted enzymes (added 2026-11-03)

**Novozymes Blair enzyme plant (2012).** The engineering contractor states "an investment of USD 200 million"
and "1,600 m 3 of fermentation capacity" (plants.yaml plant_capex_novozymes_blair_2012). Escalated with CEPCI
to 2023 (x1.365) and scaled to the model's 7,200 m3 as in check 5 (n = 0.5-0.7): $80,000-109,000 per m3. The
model's base BLG plant: $68,000. **Miss: 15% below the band** (27% below its middle, n = 0.6). With the model's
own first-plant factor (x1.28, a sensitivity) it is $87,000, inside. Cautions: Blair's cost grew during the
project (early estimates were half; unverified lead), it may count gross volume, and it is one plant. But it
makes liquid enzymes, with a lighter purification line than a food powder, so a food plant of the same volume
should cost at least as much. Together with check 5 (Liberation Labs, likely a floor, puts the model mid-band),
the two real plants say the model's capital is **not high, and may be low by up to about a quarter**. Not
tuned: recorded here; the capital factors stay frozen (honesty rule 3). If more finished plants agree, the
first-plant factor or the facility-class factors are the inputs to revisit, in a decision by Pablo.

**A market value for secreted protein (context, not a check).** Three sources, all read in full on 2026-11-03
(data/evidence/enzymes.yaml):
- Lynd et al. 2017 (Curr Opin Biotechnol 45:202, p.204): "amylase enzymes produced via mature technology and
  purchased in large amounts by the corn ethanol industry are valued at about $25/kg protein", citing Stephen et
  al. 2012. Second-hand (C) and a price, not a cost.
- Trade unit values for prepared enzymes (HS 3507.90, 2023, WITS): Denmark $13.4 per kg of product (mostly
  Novonesis), Netherlands $10.6, Finland $6.1, China $5.0, United States $29.2.
- EFSA batch tables give the protein in enzyme concentrates: liquid A. niger glucoamylases 8.4-9.6%, a dried
  T. reesei xylanase 60.3-69.1%. Trade data do not record the form, so Denmark's $13.4 per kg of product is
  $19-22 per kg protein if it were all dried and $140-160 if all liquid: too wide to test the model.
What they do say: a mature, bulk secreted enzyme sells for tens of dollars per kg of protein, above every
modelled on-site enzyme cost (NREL $4.24; ours $6.1-7.8) and at the level of our base food-protein cost ($21),
which is consistent with a margin plus formulation and logistics. **No check is possible without the product mix
behind a trade figure** (an annual report giving tonnes of enzyme protein sold would do).

## Summary: what the four anchors say

1. **The port is exact; the PF extension is Humbird-style.** The port reproduces his baker's-yeast
   cost to 0.004%, and that cost sits on the market-implied price (anchor 1; one product, and the
   margin is his assumption). The anchor favours his capital factors and fixed costs over a lighter
   set, loosely, and does not test fermenter prices (finding 5).
2. **Sugar and O₂ agree with the two designs that state them independently** (NREL within
   7% and 1%; Voutilainen's sugar is matched by construction; Intelligen's expression phase is
   matched by construction and its growth phase differs by design). **Electricity does not**:
   ours is 40–63% lower, for the reasons given under each anchor. These are consistency
   checks, not calibration fits (audit R7-M6).
3. **Published designs are 1.8× lower than our base on the same process (NREL, Voutilainen),
   and Intelligen's is within 4%.** With vendor-quote fermenters our capital matches Voutilainen's
   within 1% and Intelligen's within 24% (their Lang factor is 4). The rest is accounting: fixed
   costs of 1.5–2% of capital a year instead of Humbird's 9%, and lighter factors. With their
   conventions our model still lands above theirs, by +27% (Voutilainen) and +42% (NREL): our
   labour model, buildings, the missing-equipment allowance and cleaning.
4. **We therefore report two capital conventions and two fermenter price bases throughout.**
   - *Price-anchored capital (Humbird method, base)*: his factors and fixed costs, which his yeast
     workbook needs to land in the market band.
   - *Design-report capital (NREL-style)*: the convention of NREL-style design reports.
   - *Fermenter prices*: an industrial vendor quote (base) or Humbird's aseptic cell-culture
     vessels (v2's basis, a high case).

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

**2026-09-27, Phase F AI pre-review (docs/REVIEW.md, docs/AUDIT.md).** Structure changed by the review
decisions: vendor-quote fermenters in both conventions (BE-1/HM-2/SC-3), 20% missing-equipment
allowance (BE-4), O₂ cap 200 per m³ of cell-free liquid (HM-3), coincident-peak chillers and
compressors (BE-6), CIP chemicals inside Humbird's maintenance (HM-8), the membrane skid as an
installed cost (BE-8), disposal at the paste's 15% solids (BE-9), feeds in g/L with ammonia at its
density (FS-1/BE-2), inoculum 3 g/L (FS-11). Anchors re-run, misses re-recorded (±5-point test bands).

| Anchor | Before | After | Cause |
|---|---|---|---|
| NREL, Humbird convention | +154% | +82% | Vendor-quote fermenters (the v2 aseptic quotes were 2.9× dearer), partly offset by the 20% allowance |
| NREL, light convention | +36% | +42% | The 20% missing-equipment allowance (with 10% it is +35.5%) |
| Intelligen, total | +13.7% | −3.6% | Vendor-quote fermenters |
| Intelligen, TCI | +60% | +24% | Same |
| Voutilainen, Humbird convention | +143% | +81% | Vendor-quote fermenters; capital now within 1% of their FCI |
| Voutilainen, light convention | +23% | +27% | The 20% allowance |

The mass balances did not move (glucose −7.1% NREL, −18.9% Intelligen; O₂ −1.0%).

**2026-09-27, follow-up reading (docs/REVIEW.md, follow-up section).** Model changes: the PF model's
compressor is the textbook adiabatic one (Humbird's workbook formula, kept in the A.1 port, would add
$0.02/kg to the base BLG); the aeration
search no longer fails at high DO; inoculum 0.88 g/L from 17.6 g/L seed broth (Intelligen's
lactoferrin flowsheet; the Voutilainen anchor pins its own 10% seed train, 3 g/L from 30 g/L); cation
exchange at 20 column volumes per hour (lactoferrin only). Anchors re-run and re-recorded:

| Anchor | After |
|---|---|
| NREL, Humbird convention | +84.2% |
| NREL, light convention | +43.4% |
| NREL, electricity | −45.3% (the compressor correction) |
| Intelligen, total | −3.5% |
| Intelligen, TCI | +24.3% |
| Voutilainen, Humbird convention | +81.5% |
| Voutilainen, TCI vs FCI | +1.8% |
| Voutilainen, light convention | +26.8% |

**Aeration check (review H1).** With Humbird's compressor formula the model gives
0.501 kWh of compressor and agitator power per kg O₂ at OUR 150 in the 200 m³
vessel; his 2021 aeration sheet gives 0.501 (engineering.yaml aeration_power_humbird2021_fig13_200m3).
With the textbook compressor, 0.385. Humbird, Davis & McMillan (2017) imply about
twice his 2021 figure from process simulations without DO control (aeration_power_humbird2017_fig3).
Holding DO at 50% of saturation adds $0.26/kg to the base BLG.

**Lactoferrin reconciliation (review L).** Intelligen's own lactoferrin model gives unit production
costs of $299 (UF/DF only) and $441 (cation exchange) per kg lactoferrin
(2025$). Our cost of production on the same routes is $113 and $159; with their
stated design inputs, $105 and $212. The rest is their unit prices and cost
rules, category by category (report, lactoferrin reconciliation table; SI sheet
Lactoferrin_reconciliation). A consistency check, not a calibration: we keep our sourced prices.
