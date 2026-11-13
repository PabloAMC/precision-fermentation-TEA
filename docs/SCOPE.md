# Question and scope

Phase A deliverable, v1 (2026-09-26). This fixes what the analysis must answer, so that
the model, the data collection and the figures all serve one question. Change it only by
editing this file and recording the change in PLAN.md.

## The question

*Changed 2026-10-01 at Pablo's request (PLAN.md decisions log): ovomucoid, β-casein and lactoferrin
are products on the same footing as BLG and OVA, in every question below. Changed 2026-10-02 (v4, Pablo:
take the candidates "one by one, in priority order"): serum albumin for cultivated-meat media added on
the same footing; α-lactalbumin added the same day on the same footing, and two notes outside the product
list (casein for rennet cheese: α<sub>s1</sub>- plus κ-casein; heme: soy leghemoglobin). The original BLG/OVA wording is kept for the pre-registered priors, which were written
against it; no priors were registered for albumin, α-lactalbumin or the notes before their first outputs.*

> What does it cost to make food-grade β-lactoglobulin, ovalbumin, ovomucoid, β-casein and lactoferrin,
> and serum albumin for cultivated-meat media, by precision fermentation, with today's public strain
> performance and at the physical limits of aerobic fermentation? And what combination of titer, rate,
> yield, downstream design and plant scale would bring them to price parity with the whey, egg-white,
> casein, lactoferrin and bulk albumin they would replace?

Original (v1):

> What does it cost to make food-grade β-lactoglobulin (the main whey protein) and
> ovalbumin (the main egg-white protein) by precision fermentation, with today's public
> strain performance and at the physical limits of aerobic fermentation? And what
> combination of titer, rate, yield, downstream design and plant scale would bring them to
> price parity with whey and egg-white proteins?

| # | Sub-question | Answered by |
|---|---|---|
| Q1 | What do BLG and OVA cost at public (academic) and claimed (industry) performance? | Cost vs titer × rate map with every public and claimed data point |
| Q2 | What drives the cost, and how good is the evidence for each driver? | Tornado coloured by evidence grade; cost bridge from $4/kg crude enzyme to purified OVA |
| Q3 | Which combinations of performance and scale reach $10 and $20 per kg protein (lactoferrin: $100–400, across its market; albumin: $10–100)? | "What must be true" frontier |
| Q4 | What is the cost at the physical limits? | Physical-limit best case (v2.1: shown against the secretion ceiling it assumes) |
| Q5 | Are published company claims consistent with O₂-transfer and cooling limits? | Claims plotted against the feasible region |
| Q6 | How much do siting (US vs EU) and scale (1–100 kt/yr) matter? | Scale curve; US vs EU comparison |

## Decisions this should inform

- **Funders:** where the next public or philanthropic R&D dollar cuts cost most (titer,
  yield, rate, downstream processing, or shared scale-up capacity). Also whether PF dairy
  and egg proteins are a plausible route to displacing animal proteins at scale, or a
  premium niche.
- **EU policy:** the size of the cost gap at EU sugar and energy prices, and which
  infrastructure matters.

## Products and specifications

| | BLG | OVA |
|---|---|---|
| Base spec: *concentrate* | ≥70 wt% protein, ≥80% of protein is BLG, ≤7% moisture (`FDA-GRN1056`) | Same by analogy (grade D until an OVA GRAS spec is on disk) |
| Base downstream train | Remove cells, filter, UF/DF, dry (GRN 1056 says "dried"; we assume spray-drying) | Same |
| Variant spec: *isolate* | ≥90% target protein, dry basis; adds precipitation or chromatography | 99% dry basis via ammonium-sulfate precipitation (`intelligen_ovalbumin2025`) |

| | Ovomucoid (added 2026-10-01) | β-casein (added 2026-10-01) | Lactoferrin (equal footing 2026-10-01) |
|---|---|---|---|
| Base spec | EVERY's GRN 967: ≥75% protein, 66–74% ovomucoid in the powder (~0.76 of dry matter), ≤10% moisture | ≥90% protein, >97% casein of protein, ≤5% moisture, by analogy with Formo's αs1-casein (FDA GRN 1312), sold as sodium caseinate | ≥90% protein, ≥95% lactoferrin, ≤4.5% moisture (FDA GRN 1284) |
| Base downstream train | Remove cells, filter, UF/DF, dry (GRN 967: no chromatography) | Remove cells, filter, UF to skim-milk casein concentration, isoelectric precipitation (pH 4.5, 90 °C), decanter washes, NaOH to caseinate, spray dry | Remove cells, filter, cation exchange, UF/DF, spray dry |
| Variant | Ammonium-sulfate isolate (patent route) | UF/DF only (Eden Brew, FSANZ A1342): ~6% β-casein in the powder | UF/DF only (Intelligen case a) |
| Plant | 10 kt/yr | 10 kt/yr, as BLG and OVA | 250 t/yr (Intelligen's design; world market ~0.3–1.6 kt/yr) |

| | Serum albumin (added 2026-10-02) |
|---|---|
| Base spec | Cell-culture grade recombinant HSA: ≥96% albumin, ≤1 EU/mg endotoxin (InVitria Cellastim S; no food- or media-grade spec exists) |
| Base downstream train | Remove cells, filter, cation-exchange capture at pH 4.5 then anion-exchange polish (Delta/Recombumin minimal train), UF/DF, spray dry |
| Variants | Capture only (optimistic); methanol-induced production; capture recovery 0.40/0.86; UF/DF only (77% albumin, below spec) |
| Plant | 1 kt/yr (design choice: ~today's human-albumin market; GFI's 2030 CM scenarios 3.6–100 kt/yr) |
| Incumbent | Bulk bovine serum albumin, technical grade ($40–70/kg, grade C); GFI target $10/kg; catalogue rHSA $43–55k/kg |

| | α-Lactalbumin (added 2026-10-02) |
|---|---|
| Base spec | Dairy α-lac isolate, FDA GRN 763 (Agropur): ≥95% protein, ≥90% of it α-lac, i.e. ~90% of dry matter |
| Base downstream train | BLG's membrane route (MF, UF/DF, spray dry); GFI Europe/ADL's food-grade route |
| Academic | Wang 2025, 0.60 g/L human α-lac (supernatant), ethanol-fed >90 h, priced as glucose |
| Plant | 1 kt/yr (design choice: about 5% of the α-lac market, ~19 kt/yr of α-lac; GFI Europe 2025, C; audit R15-M1) |
| Incumbent | Dairy α-lac, $15–123/kg (GFI Europe/ADL; FMI $31–86; grade C) |

Notes outside the product list (run on existing routes by analogy; data/pf/scenarios/cheese.yaml, heme.yaml,
transferrin.yaml, binder.yaml):
- *Casein for rennet cheese:* α<sub>s1</sub>-casein (base design point, β-casein's acid route) blended with κ-casein
  from its own strain and plant at 12–19% κ (Antuma 2025); output: the blend's cost against κ titer, and the κ
  titer at which the blend costs ≤10% more than α<sub>s1</sub> alone.
- *Heme:* soy leghemoglobin from the best published secreting strains (Chen 2025, Shao 2022) on the membrane
  route at LegH Prep's purity; cost per kg LegH and per kg of beef analogue at 0.45% use. The commercial
  route (intracellular, lysed, frozen liquid) is not modelled.
- *Transferrin (v4.1):* recombinant human transferrin on albumin's plant and two-column route with its own column
  data (Novozymes), at the design point and the best published titer (Finnis 2010), at ~10 and ~100 t/yr; cost per kg
  of cultivated meat at 0.075-1.19 g/kg (data/pf/scenarios/transferrin.yaml).
- *Ovalbumin as a binder (v4.1):* PF ovalbumin's cost per kg of plant-based meat analogue at egg-white-protein use
  levels, against methylcellulose and dried egg white (data/pf/scenarios/binder.yaml). No new process.
- *Feedstock against feed (v4.1):* the metabolic floor (src/pftea/floor.py) beside the incumbent animals' feed bill and
  farm-gate cost per kg of edible protein, US and EU (data/evidence/feed.yaml).

Vessel size (v4): the designer takes the cheapest feasible plant over 50–200 m³ vessels (cap 200 m³),
so the small plants (lactoferrin, albumin) use smaller vessels. First-of-a-kind: a pioneer-plant case
(capital x 1.28, RAND R-2569) is shown separately, never in the base.

**Functional unit:** 1 kg of target protein in a spray-dried powder that meets the spec.
Results are reported per kg of protein and per kg of powder.

**Comparators.** Wholesale, protein-adjusted (`gfi2025costs`, p.31):
- WPC80/WPI $10.3–19.9 per kg protein;
- casein $9.6–12.2;
- egg white $15.6–59.4;
- GFI's commodity target band $5–20/kg.

Phase B replaced these with 2015–2025 trade unit values (UN Comtrade, Eurostat) and 2026
USDA spot quotes (`data/evidence/prices.yaml`, `data/pf/benchmarks.yaml`). The GFI ranges
are kept as grade-C context. Parity at production cost is
necessary but not sufficient for commercial parity. Margins, functionality and
cost-in-use are outside the model and are stated as such.

## Process and plant basis

- **Hosts:** *K. phaffii* is the base (Remilk GRN 1056, EVERY, Intelligen's design).
  *T. reesei* is a variant (Perfect Day GRN 863, Onego Bio, VTT's Aro 2023); its viscous
  broth changes the O₂ physics. *E. coli* is a variant for β-casein only (added 2026-11-13: Formo GRN 1312,
  Fermify GRN 1228, Standing Ovation): the protein stays inside the cell and is recovered by acid-heat
  extraction (`plant.product_location: intracellular`, scenario `cas_ecoli`). Its growth is sourced; its
  purification yields and cell density are guesses, because the public dossiers state none, so its price is
  conditional on them (report Q8; VALIDATION check 8).
- **Mode:** aerobic fed-batch on glucose. Continuous operation only if data allow.
- **Plant:** greenfield, single-product, nth-of-a-kind. Base is 10 kt/yr of protein, swept
  from 1 to 100 kt/yr. A first-of-a-kind case is shown separately, never mixed in: capital x
  1/0.78 = 1.28, the mean cost growth of pioneer process plants (RAND R-2569, Merrow et al. 1981; no
  fermentation-specific premium is on file).
- **Facility class:** food-grade, "commodity aerobic" in the classes of Humbird's
  equipment database. Built to food CGMP (21 CFR 117, as in GRN 1056), not pharmaceutical
  cGMP.
- **Location:** US Midwest base (dextrose, comparability with NREL and Humbird) plus an EU
  variant in north-west Europe. The exact site and prices are fixed in Phase B.
- **Money:** 2025 US dollars. EUR at a stated rate.

**Open design questions**, settled in Phase C on evidence rather than here:
- methanol-induced vs methanol-free expression;
- precipitation vs chromatography for the isolate;
- production vessel size;
- what happens to spent cells (feed, fertiliser or waste).

## Cost boundary

**Included:** raw materials, utilities, consumables, waste treatment net of co-product
credit, labour, maintenance, insurance and local taxes, and a charge on capital.

**Excluded, and stated with every result:** R&D, strain licensing and royalties,
regulatory approval, sales, marketing and distribution, land, the first-of-a-kind premium,
and carbon pricing (the EU variant may add it as a sensitivity).

## Metrics

- **COP** ($/kg protein): operating cost plus depreciation, no return on capital.
- **MSP_CCF**, the headline for comparability with Humbird: operating cost plus a capital
  charge of 7.5% over 10 years, i.e. 14.6% of TCI per year.
- **MSP_DCF**, the investor view: NREL-style discounted cash flow at a 10% internal rate
  of return, with taxes and depreciation schedules.
- **Physical intensities per kg protein:** sugar, O₂, electricity, water, cells produced.
  Also fermenter m³ per kt/yr and jobs per kt/yr.

## Scenarios (never merged)

| Scenario | Inputs allowed |
|---|---|
| `academic` | Titers from peer-reviewed full texts (grade A). Where no product-specific value exists (product yield, maintenance, most process values) the base values are kept, which include design values (B) and a few analogies and guesses (D, E). |
| `industry` | The base case with one grade-C input: the private-sector average titer (GFI 2025). |
| `required` | Inverse: the titer needed for $10, $20 and $50 per kg protein at each production time. |
| `physical-limit` | A best case at assumed limits, not a floor: product yield at 95% of the energetic ceiling (peptide bonds, amino-acid synthesis and sulfate assimilation); the lowest measured maintenance; no growth in production; a 600 g/L glucose feed; rate limited by the O₂ cap (250 mol/m³/h per m³ of cell-free liquid, head pressure not costed), cooling (40 kW/m³), the minimum initial fill and a secretion ceiling (40 mg/g/h, grade D; also shown at 5–120) in 400 m³ vessels; 8 h turnaround; a 90% concentrate; contract sugar; 100 kt/yr. |

*Changed 2026-09-27 (audit R8-m4):* the definitions above now describe what runs; the v1 text
promised "grades A and B only" for `academic` and a "stoichiometric maximum yield" for
`physical-limit`, which the model did not do. Logged in PLAN.md.

*Changed 2026-09-27 (Phase F AI pre-review, docs/REVIEW.md):* `physical-limit` is described as a best
case conditional on the secretion ceiling (review SC-2, FS-3); its yield, feed and O₂ basis follow
the review changes (FS-1, FS-2, HM-3). The scenario keeps its pre-registered name.

## Out of scope for v1

- Micelle formation, κ-casein and casein phosphorylation (v2). *Changed 2026-10-01 at Pablo's
  request:* β-casein as a single protein is now a product on the same footing as BLG and OVA
  (base.yaml's design point; isoelectric precipitation to sodium caseinate), compared with dairy
  casein. Whether a cheese made from it performs like dairy cheese is outside the model.
- Other products. *Added 2026-09-26 at Pablo's request:* lactoferrin as a high-value contrast
  case (report Q8), and milk and egg equivalents of the costs (report Q7).
- Strain engineering.
- Full LCA; only the physical intensities above are reported.
- Market forecasts, company-specific costs, private data.

## Pre-registered priors

Recorded before any model output (Phase C/E) exists, and informed only by the published
anchors. They are for scoring at release, never for tuning. Claude, 2026-09-26:
1. MSP_CCF (Humbird's convention) from our model, with 80% intervals:
   - **1a.** Intelligen's configuration (*K. phaffii*, 30 g/L, 99% isolate, 1 kt/yr):
     **$38–60 per kg OVA**.
   - **1b.** Base case (*K. phaffii*, 30 g/L, Intelligen-like cell density, concentrate
     spec, 10 kt/yr): **$28–50 per kg protein**.
   - *Superseded the same day, kept for scoring:* "at ~30 g/L and 1–10 kt/yr, purified
     BLG/OVA costs $20–40 per kg protein". That interval excluded the only in-repo anchor.
     Intelligen recast in Humbird's convention gives $46/kg OVA at 1 kt/yr (exercise A1,
     step 1.4), so the prior was too optimistic.
2. P(physical-limit floor < $10/kg protein) ≈ 0.65.
3. P(a public BLG/OVA yield on sugar turns up in Phase B) ≈ 0.20.
4. P(calibration within tolerance on the first try, without tuning): baker's yeast 0.6,
   NREL cellulase 0.6, Intelligen OVA 0.5.
5. P(public v1 by 2027-04-30) ≈ 0.5; by 2027-07-31 ≈ 0.8.

Pablo, add your own before reading Phase C results (optional):
-

## Sign-off

- [ ] Pablo agrees with the question, scope and defaults (date: ______)
