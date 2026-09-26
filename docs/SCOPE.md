# Question and scope

Phase A deliverable, v1 (2026-09-26). This fixes what the analysis must answer, so that
the model, the data collection and the figures all serve one question. Change it only by
editing this file and recording the change in PLAN.md.

## The question

> What does it cost to make food-grade β-lactoglobulin (the main whey protein) and
> ovalbumin (the main egg-white protein) by precision fermentation, with today's public
> strain performance and at the physical limits of aerobic fermentation? And what
> combination of titer, rate, yield, downstream design and plant scale would bring them to
> price parity with whey and egg-white proteins?

| # | Sub-question | Answered by |
|---|---|---|
| Q1 | What do BLG and OVA cost at public (academic) and claimed (industry) performance? | Cost vs titer × rate map with every public and claimed data point |
| Q2 | What drives the cost, and how good is the evidence for each driver? | Tornado coloured by evidence grade; cost bridge from $4/kg crude enzyme to purified OVA |
| Q3 | Which combinations of performance and scale reach $10 and $20 per kg protein? | "What must be true" frontier |
| Q4 | What is the cost at the physical limits? | Physical-limit floor |
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
  broth changes the O₂ physics.
- **Mode:** aerobic fed-batch on glucose. Continuous operation only if data allow.
- **Plant:** greenfield, single-product, nth-of-a-kind. Base is 10 kt/yr of protein, swept
  from 1 to 100 kt/yr. A first-of-a-kind penalty is shown separately, never mixed in.
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
| `academic` | Evidence grades A and B only (peer-reviewed measurements, patent examples) |
| `industry` | Adds grade C (company claims, GFI private-sector benchmarks) |
| `required` | Inverse: the performance needed for $10, $20 and $50 per kg protein |
| `physical-limit` | Stoichiometric maximum yield; O₂- and cooling-limited rate in the largest practical vessel; minimal downstream processing for the spec; contract sugar; 100 kt/yr |

## Out of scope for v1

- Casein and micelle formation (v2).
- Other products. Lactoferrin appears only as a downstream calibration case.
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
