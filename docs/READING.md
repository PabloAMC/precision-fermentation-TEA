# Reading guide: Phase A (about 6 hours plus the 2-hour exercise)

The aim is to learn enough bioprocess engineering and TEA accounting to check the model's
derivations, make its judgement calls, and defend it to a sceptical engineer. Read in
this order. Each item says where to look, what to look for, and gives questions to answer
afterwards. Answers are folded underneath.

All files are on disk. **Printed page ≠ PDF page**, so both are given.

| # | Item | Time | Status |
|---|---|---|---|
| 1 | [PRIMER.md](PRIMER.md) (includes a self-check) | 75 min | ☐ |
| 2 | NREL 2011: on-site enzyme plant and process economics | 85 min | ☐ |
| 3 | Humbird 2021: the method we are copying | 150 min | ☐ |
| 4 | Intelligen 2025 ovalbumin, then [exercise A1](exercises/A1_intelligen_rebuild.md) | 45 min + 2 h | ☐ |
| 5 | GFI 2025: public vs private benchmarks and incumbent prices | 15 min | ☐ |
| 6 | [LITERATURE.md](LITERATURE.md): what exists and what does not | 10 min | ☐ |

---

## 2. NREL 2011, *Process design and economics for biochemical conversion of lignocellulosic biomass to ethanol* (`humbird2011`)

File: `references/reports/NREL_2011_Humbird_TP-5100-47764_biochemical_ethanol.pdf`
(PDF page = printed + 10). Same first author as the cultivated-meat TEA. This is the
field's reference for a transparent design report.

- **§3.4 Area 400, cellulase enzyme production**, printed pp. 36–42 (PDF 46–52), 35 min.
  A complete secreted-protein fermentation in seven pages: design basis (Table 18),
  stoichiometry, oxygen transfer, vessel specifications, nutrients, electricity (Table
  21), cost breakdown (Figure 10). The primer's running example.
- **§4 Process economics**, printed pp. 57–68 (PDF 67–78), 50 min. Focus on:
  - how purchased cost becomes total capital investment (Tables 27–28);
  - variable vs fixed operating costs (Tables 30–31);
  - the discounted cash flow parameters (Table 33).

  Skim the ethanol-specific parts.

Questions:
1. Table 18 lists five design assumptions. Which one does NREL say is actually
   *computed*, and from what?
2. Why is the peak O₂ uptake rate at the *start* of the production phase?
3. What does the $4.24/kg enzyme cost leave out?
4. Which capital add-ons are percentages of ISBL, and which of TDC?
5. In Table 33, which parameter would you expect to move the selling price of a
   capital-heavy plant most?

<details><summary>Answers</summary>

1. The yield, 0.24 kg/kg. It follows from the protein's elemental composition and the
   assumed carbon split between protein and cells (p.37–38).
2. The absolute O₂ demand is fixed by the protein production rate, but at 50% fill it is
   spread over the smallest liquid volume. So the per-litre rate peaks, at 56 mmol/L/h.
3. Concentration, stabilisation, formulation and transport of the enzyme, and licensing
   fees for the strain (p.40).
4. Warehouse, site development and additional piping are % of ISBL. Prorateable costs,
   field expenses, home office and construction, contingency and other costs are % of TDC
   (Table 27).
5. The discount rate (internal rate of return). For capital-heavy plants the capital
   charge dominates, and it is very sensitive to the rate.

</details>

## 3. Humbird 2021, *Scale-up economics for cultured meat* (`humbird2021`)

File: `references/papers/Humbird2021_cultured_meat.pdf`, the engrXiv version (PDF page =
printed + 5). The whole point of this project is to do for PF proteins what this did for
cultivated meat. Skip the animal-cell biology and read for **method**.

- **§1.2 Industrial scale-up perspectives**, printed pp. 3–8 (PDF 8–13), 20 min.
  Figure 1.3, the cost of transferring O₂ vs vessel size and OUR, is the intuition behind
  §5 of the primer.
- **§2.3 Bioreactor design principles and limitations**, printed pp. 22–30 (PDF 27–35),
  40 min. How O₂ transfer, CO₂ removal and vessel geometry set a maximum cell density for
  each vessel size. Our physical-limit scenario does the same for productivity.
- **§3.1 Capital costs**, printed pp. 34–38 (PDF 39–43), 25 min. Facility classes
  (Table 3.1), double-dipping, costing vessels with process-industry software.
- **§3.2, proteins only**, 5 min. Figure 3.4b is on printed p. 42 (PDF 47); the paragraph
  on proteins and the regression Eq. 3.4 are on printed p. 44 (PDF 49). This is the
  price-volume relation for industrial enzymes and therapeutics, a top-down cross-check
  for us.
- **§3.3 Fixed operating costs**, printed pp. 46–47 (PDF 51–52), 10 min. The labour model.
- **Appendix A, baker's yeast analysis**, printed pp. 89–98 (PDF 94–103), 35 min.
  Calibration against a real market price. This is the part we copy most directly.
- **§5.1–5.2 Summary and recommendations**, printed pp. 70–73 (PDF 75–78), 15 min. How to
  write conclusions a sceptical reader will accept.
- Optional: open the SI workbook (`references/papers/Humbird2021_cultured_meat_SI.xlsm`)
  and look at sheets `A.1` (his yeast simulator) and `Equip` (equipment costs by facility
  class). Phase C1 ports these to Python.

Questions:
1. Why does the cost per kg of O₂ transferred fall with both vessel size and OUR
   (Figure 1.3)?
2. What two operating limits does he impose on sparging and agitation, and why are they
   much looser for yeast?
3. What is double-dipping, and how large is the spread in the purchased cost of a 20 m³
   vessel across facility classes?
4. How does he estimate labour for a batch plant without a detailed schedule?
5. What is the calibration logic of Appendix A, in two sentences?
6. What does "necessary but insufficient" refer to in his conclusions?

<details><summary>Answers</summary>

1. Bigger vessels spread vessel, compressor, chiller and operator costs over more
   capacity. Higher OUR uses the same capital more intensely.
2. A superficial gas velocity of about 0.006 m/s (roughly 0.1 vvm at 20 m³), and an
   agitation limit keeping turbulent eddies larger than a cell. Both protect fragile
   animal cells from bubble and eddy damage. Microbes with cell walls tolerate far more,
   which is why industrial fermentations run at around 1 vvm and several kW/m³.
3. Applying installation factors to an equipment price that already includes installation,
   for example a piped and instrumented skid. The 20 m³ vessel ranges from $133k (lysine
   class) to $1.96M (cGMP skid), about 15× (Table 3.1).
4. Operator attention per batch step: lab passages, a percentage of online and offline
   time for seed and production vessels, 80% efficiency. That gives FTE per shift, plus
   continuous-area staff and supervisors, times 4.5 hires per around-the-clock position.
5. Model a real, priced commodity bioprocess (baker's yeast; wholesale $2.20–2.80/kg,
   implying ~$1.90/kg cost after a 33% margin) with the same method. If the method
   reproduces it, its answers for the new process deserve some trust.
6. Metabolic efficiency improvements and low-cost plant-hydrolysate media. Together they
   get the fed-batch design just below his $25/kg target; it is the only scenario that
   does. But the hydrolysate's price and suitability are "somewhat speculative". In his
   words they are "necessary but insufficient conditions for the measurable displacement
   of conventional meat by cultured meat" (Executive Summary).

</details>

## 4. Intelligen 2025, *Egg white protein (ovalbumin) production via precision fermentation* (`intelligen_ovalbumin2025`)

File: `references/reports/Intelligen_2025_ovalbumin_TEA.pdf` (PDF page = printed + 1).
Read printed pp. 5–19 in 45 minutes: process description, scheduling, cost analysis.
Then do [exercise A1](exercises/A1_intelligen_rebuild.md).

Questions:
1. Which downstream step does most of the purification, and what does it cost in raw
   materials?
2. Where does the fertiliser credit come from?
3. Why does one batch take 196 hours when a batch is finished every 24 hours?

<details><summary>Answers</summary>

1. Ammonium-sulfate precipitation at pH 4.5: 90% of the ovalbumin precipitates, 15% of
   host-cell protein. Ammonium sulfate is 20% of the raw-material bill ($1.66 M/yr), even
   though most of it is recovered into fertiliser.
2. Spent yeast and ammonium sulfate from the waste streams are neutralised, evaporated and
   dried into a fertiliser containing ~71% ammonium sulfate.
3. Five fermenters are staggered, and downstream units run semi-continuously. The batch
   *time* (196 h, from media prep to drying) and the *cycle* time (24 h between batches)
   are different things.

</details>

## 5. GFI 2025, *Driving down costs of fermentation-derived ingredients* (`gfi2025costs`)

File: `references/reports/GFI_2025_driving_down_costs_fermentation.pdf`. Read PDF pp.
30–31 in 15 minutes: Table 2 (public vs private benchmarks) and §1.3.3 (incumbent prices).
The sensitivity analysis in §2.4.3 (PDF p. 58) is for single-cell protein, not PF.

Questions:
1. Public vs private averages for titer, plant size and yield?
2. WPC80/WPI and egg-white prices per kg of *protein*?

<details><summary>Answers</summary>

1. Titer: public 24 g/L, private 42 g/L. Volume: public 50–2,500 t/yr, private
   2,500–25,000+ t/yr. Yield: public 0.01–0.20, private 0.03–0.17 g/g.
2. WPC80/WPI $10.3–19.9; egg white $15.6–59.4, wide because it depends on purity.

</details>

---

## Later, for reference only (not Phase A)

| When | Item | Why |
|---|---|---|
| Phase B | Garcia-Ochoa & Gomez 2009; Crater & Lievense 2018; Doran 2013 (mass transfer) | Sources for OTR ceilings, maximum vessel sizes and the heat-per-O₂ rule. On the fetch list. |
| Phase B | Towler & Sinnott 2013, ch. 7 | Cost curves, cost indices, Lang factors |
| Phase C | Humbird SI workbook, sheets `A.1`–`A.3`, `Equip`, `RawUtil`, `Phys` | The simulator and cost database we port |
| Phase D | Voutilainen et al. 2021 (+ SI workbook) | Calibration anchor 4 |
| Phase D | BioSTEAM documentation (Cortés-Peña 2020) | Cross-check of cost correlations only |

Skip on any pass: metabolic modelling, strain engineering, glycosylation biochemistry,
the cultivated-meat media literature.
