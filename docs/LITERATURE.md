# Literature map: what exists, what does not

First written 2026-09-18, after the first systematic sweep (three parallel searches:
TEAs and method templates; peer-reviewed BLG/OVA expression; company patents). Updated
2026-09-26 for the full texts fetched since: Aro 2023, Li 2026, Yao 2026, Nielsen 2025/26
and the Järviö 2021 main paper. Keys refer to references/INDEX.md. Numbers quoted here are
copied from the extracted text in references/text/. Nothing enters the base case until its
row in data/titers.csv is marked `verified: yes` (quote checked against the full text on
disk). The rows for the four new full texts have not been updated yet.

## 1. TEAs of precision-fermented food proteins

**No dedicated peer-reviewed TEA of BLG, OVA, casein or leghemoglobin exists.**
David et al. 2026 (a TEA/LCA review in Trends Food Sci Technol) is relevant but not on
disk (paywalled; references/INDEX.md), so nothing here rests on it. What does exist:

| key | what it is | why it matters |
|---|---|---|
| voutilainen2021 | VTT; three SCPs + one "generalized recombinant protein" from straw sugar. Full SI workbook (balances, capex, opex, DCF) on disk | Calibration anchor 4 (plan v2). GFI 2025 cites its $11.2/kg (spray-dried, 90% purity) as the lowest published PF COP |
| humbird2011 (NREL) Area 400 | On-site T. reesei cellulase plant: 300 m3 reactors, **50 g/L titer, 0.24 kg protein/kg glucose, 120 h on + 48 h off** (Table 18); $4.24/kg protein (2007$), crude | Best fully public anchor for cheap crude secreted fungal protein. Calibration anchor 2 (plan v2); the primer's running example |
| kleinmarcuschamer2012 | Cellulase production TEA (LBNL): T. reesei on poplar, $10.14/kg enzyme at baseline | Cross-check for crude secreted fungal protein, with sensitivities to feedstock price and fermentation time. Not a calibration anchor in plan v2 |
| intelligen_ovalbumin2025 | SuperPro example: yeast, 30 g/L in 4.5 d, 1000 t/yr, ammonium-sulfate precipitation | Closest thing to an OVA TEA. **On disk since 2026-09-26** (reports/Intelligen_2025_ovalbumin_TEA.pdf): $38.99/kg gross, $36.33 net, TCI $92M, 92 g/L DCW. Calibration anchor 3 and exercise A1 |
| intelligen_lactoferrin2024 | 10 g/L, 5 d, 250 t/yr, two DSP cases (UF/DF + spray-dry vs CEX) | The $292/kg target in the old tests; optional DSP check in plan v2. Not on disk |
| gfi2025costs | GFI + Hawkwood; survey of published TEMs vs private-sector data | Source of the 24 g/L (published avg) vs 42 g/L (private avg) benchmark, sec 1.3.2 |
| gfieurope2025 | GFI Europe + ADL archetype cost models, $24-33/kg PF protein | Industry-side comparator, grade C |
| risner2023 | Mycoprotein (biomass fermentation) TEM | Structure and sensitivity pattern to copy; not a PF product |
| yamanie2026 | K. phaffii fed-batch vs continuous TEA | Host-level cost structure, batch times |
| behm2022, jarvio2021 (main paper and SI) | VTT LCAs of BLG and OVA in T. reesei | Process inventories (media, energy per kg) for a fungal process |
| puetz2019 | Industrial vs pharma recombinant protein pricing review | Price-vs-titer envelope across industrial enzymes |

## 2. Method templates on disk
humbird2021 (+ SI workbook), humbird2011, Towler & Sinnott (textbook, not on disk).
cortespena2020 (BioSTEAM) is open access but bot-walled; docs are online.

## 3. BLG titers (peer-reviewed)
Highest, now read in full: **13.88 g/L in K. phaffii** (Yao2026, Food Bioscience
82:109383). The run is a 5-L stirred tank (3 L working volume) in a rich medium (yeast
extract, tryptone): glucose fed-batch growth, then an ethanol-induction phase with sodium
glutamate feeding. The titer is by HPLC, at 489 g/L wet cells. The same group's **5.14 g/L
on glucose** (Li2026, Metabolic Engineering 99:102555) is a 5-L fed-batch, quantified by
SDS-PAGE. The model's `academic` scenario still uses 5.14 g/L
(data/pf/scenarios/academic.yaml). Older anchors: >1 g/L Pichia fed-batch (Kim1997); 1 g/L
T. reesei in a 1 L bioreactor (Aro2023, full text). Every other host (S. cerevisiae,
K. lactis, L. lactis, L. casei) is in the mg/L to ug/L range. Nielsen2025 (A. oryzae
industrial strain; Industrial Biotechnology 22(2), 2026) reports only relative gains in
Ambr 250 bioreactors: +79% product amount and +73% carbon yield over its centre point. It
gives no absolute titer or yield.

## 4. OVA titers (peer-reviewed)
Most defensible: **2 g/L in T. reesei** (Aro2023, now read in full: a 1 L glucose
fed-batch bioreactor, with a protease inhibitor added at 72 h). The 2 g/L is two SDS-PAGE
bands combined by densitometry: full-length OVA at 42 kDa and a C-terminally clipped form
at 36 kDa. Intact OVA is therefore below 2 g/L. Chicken OVA in yeast is stuck at 5 to
132 mg/L (Jin2024, Yoon2026), mostly intracellular. The 5.45 g/L quail-OVA shake-flask
figure (Yang2009) is a ~1000x outlier and should not be used as a prior. OVA is roughly an
order of magnitude harder than BLG in yeast. Trichoderma is not the only host with a
bioreactor number: Beck2025 (review, citing Liu et al. 2024) gives 3.7 g/L in E. coli EcN
in a 3 L fed-batch, intracellular, and Jin2024 (abstract) 132 mg/L of total OVA in an
S. cerevisiae glucose-limited fed-batch.

## 5. Patents (19 on disk)
**No company patent example discloses a numeric BLG titer.** Perfect Day, Remilk and
Vivici give process envelopes only (T. reesei harvest at 20-50 g DCW/L after >=120 h;
Pichia at OD600 600-800, glycerol feed 6 g/L/h, >=100 h; 7-day fermentation; >80-85%
purity). No numeric OVA titer either. The single bioreactor titer found is EVERY's
**30.19 g/L ovomucoid** (Every2024-HY, Example 9, ~140 h), a smaller protein than OVA;
treat as a best-run upper bound (grade B). Missing: DSM WO2022269549 (the BLG
fermentation Vivici cross-references), any Onego Bio filing under that assignee.

## 6. Measurements that do not exist publicly
- Any company BLG or OVA titer at >1 m3 scale.
- Any measured yield on sugar (g protein / g glucose) for BLG or OVA in any host. The
  public values are design or derived numbers: BLG 0.223 g/g (behm2022, a T. reesei
  design), OVA 0.28 g/g (intelligen_ovalbumin2025, a design, expression phase only) and
  OVA 0.39 g/g (Jarvio2021, derived from an LCA inventory; being re-checked). Beyond these
  there are cellulase (0.24, NREL 2011, also a design), GFI's survey range and
  Nielsen2025's relative carbon-yield gain.
- Any per-step DSP recovery for a food-grade (non-chromatographic) BLG/OVA train.
- Any casein titer in g/L.
- Batch time and cell density for BLG/OVA at production scale (patent envelopes only).

## 7. Still to fetch
See references/TO_FETCH.md (full list with DOIs, priorities and filenames).
Old list, still open: Eastham2024, Nielsen2024, David2026, David2026lca, CortesPena2020,
the Intelligen lactoferrin and collagen white papers, DSM WO2022269549. Fetched on
2026-09-26: Aro2023, Li2026, Yao2026 and Nielsen2025 (full texts), the Järviö 2021 main
paper and the Intelligen ovalbumin paper.

## 8. Recommendations for the plan
Status 2026-09-26: items 1 and 2 were adopted in PLAN.md v2. The anchors are now baker's
yeast (Humbird App. A, real price), NREL 2011 Area 400, Intelligen OVA 2025 and
Voutilainen 2021. Items 3 and 4 were adopted in modified form:
- the `academic` scenario uses the single best public titers, BLG 5.14 g/L (Li2026) and
  OVA 2 g/L in T. reesei (Aro2023), not yet updated for Yao2026's 13.88 g/L;
- the `industry` scenario uses GFI's private-sector average of 42 g/L (range 24-60), and
  the base case 30 g/L;
- for yield, the model sets the product-reaction yield (0.28 g/g from Intelligen's Eq. 2
  in the base and `academic` runs, 0.30 in `industry`) and computes the overall yield from
  growth and maintenance. Its ceiling is the energetic one in src/pftea/product.py, not
  cellulase's 0.24.

The original recommendations (2026-09-18):
1. Add NREL 2011 Area 400 as validation target 1 (all inputs public, incl. yield).
2. Swap the Intelligen lactoferrin target for the Intelligen ovalbumin 2025 model
   once its PDF is obtained; keep lactoferrin as the high-purity DSP check.
3. `academic` scenario priors: BLG 1-5 g/L (K. phaffii), OVA 1-2 g/L (T. reesei).
   `industry` scenario: 24-42 g/L (gfi2025costs), 30 g/L (intelligen_ovalbumin2025).
4. Yield prior for the `academic` scenario has no product-specific evidence; use
   cellulase 0.24 as the ceiling and GFI's 0.03-0.17 as the range, grade D.
