# Literature map: what exists, what does not

Status as of 2026-09-18, after the first systematic sweep (three parallel searches:
TEAs and method templates; peer-reviewed BLG/OVA expression; company patents).
Keys refer to references/INDEX.md. Numbers quoted here are copied from the
extracted text in references/text/ and still need `verified_by_pablo`.

## 1. TEAs of precision-fermented food proteins

**No dedicated peer-reviewed TEA of BLG, OVA, casein or leghemoglobin exists.**
David et al. 2026 (review, tifs) says the same. What does exist:

| key | what it is | why it matters |
|---|---|---|
| voutilainen2021 | VTT; three SCPs + one "generalized recombinant protein" from straw sugar. Full SI workbook (balances, capex, opex, DCF) on disk | Calibration anchor 4 (plan v2). GFI 2025 cites its $11.2/kg (spray-dried, 90% purity) as the lowest published PF COP |
| humbird2011 (NREL) Area 400 | On-site T. reesei cellulase plant: 300 m3 reactors, **50 g/L titer, 0.24 kg protein/kg glucose, 120 h on + 48 h off** (Table 18); $4.24/kg protein (2007$), crude | Best fully public anchor for cheap crude secreted fungal protein. Calibration anchor 2 (plan v2); the primer's running example |
| kleinmarcuschamer2012 | Cellulase production TEA (LBNL) | Second crude-protein anchor; gives $/kg protein and its sensitivity to titer and yield |
| intelligen_ovalbumin2025 | SuperPro example: yeast, 30 g/L in 4.5 d, 1000 t/yr, ammonium-sulfate precipitation | Closest thing to an OVA TEA. **On disk since 2026-09-26** (reports/Intelligen_2025_ovalbumin_TEA.pdf): $38.99/kg gross, $36.33 net, TCI $92M, 92 g/L DCW. Calibration anchor 3 and exercise A1 |
| intelligen_lactoferrin2024 | 10 g/L, 5 d, 250 t/yr, two DSP cases (UF/DF + spray-dry vs CEX) | The $292/kg target in the old tests; optional DSP check in plan v2. Not on disk |
| gfi2025costs | GFI + Hawkwood; survey of published TEMs vs private-sector data | Source of the 24 g/L (published avg) vs 42 g/L (private avg) benchmark, sec 1.3.2 |
| gfieurope2025 | GFI Europe + ADL archetype cost models, $24-33/kg PF protein | Industry-side comparator, grade C |
| risner2023 | Mycoprotein (biomass fermentation) TEM | Structure and sensitivity pattern to copy; not a PF product |
| yamanie2026 | K. phaffii fed-batch vs continuous TEA | Host-level cost structure, batch times |
| behm2022, jarvio2021 (SI only) | VTT LCAs of BLG and OVA in T. reesei | Process inventories (media, energy per kg) for a fungal process |
| puetz2019 | Industrial vs pharma recombinant protein pricing review | Price-vs-titer envelope across industrial enzymes |

## 2. Method templates on disk
humbird2021 (+ SI workbook), humbird2011, Towler & Sinnott (textbook, not on disk).
cortespena2020 (BioSTEAM) is open access but bot-walled; docs are online.

## 3. BLG titers (peer-reviewed)
Highest verifiable: **5.14 g/L in K. phaffii on glucose** (Li2026, abstract).
An unverified lead of 13.88 g/L from the same group (Yao2026) has no retrievable
abstract; do not enter until the PDF is read. Older anchors: >1 g/L Pichia fed-batch
(Kim1997); 1 g/L T. reesei (Aro2023). Every other host (S. cerevisiae, K. lactis,
L. lactis, L. casei) is in the mg/L to ug/L range. Nielsen2025 (A. oryzae) is
blocked and may be relevant.

## 4. OVA titers (peer-reviewed)
Most defensible: **2 g/L in T. reesei** (Aro2023). Chicken OVA in yeast is stuck at
5 to 132 mg/L (Jin2024, Yoon2026), mostly intracellular. The 5.45 g/L quail-OVA
shake-flask figure (Yang2009) is a ~1000x outlier and should not be used as a prior.
Beck2025 (review) cites 3.7 g/L in E. coli EcN, intracellular. OVA is roughly an
order of magnitude harder than BLG in yeast; Trichoderma is the only host with a
real bioreactor number.

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
- Any yield on sugar (g protein / g glucose) for BLG or OVA in any host. The only
  public yields are for cellulase (0.24, NREL 2011) and GFI's survey range.
- Any per-step DSP recovery for a food-grade (non-chromatographic) BLG/OVA train.
- Any casein titer in g/L.
- Batch time and cell density for BLG/OVA at production scale (patent envelopes only).

## 7. Still to fetch
See references/TO_FETCH.md (full list with DOIs, priorities and filenames).
Old list:
Aro2023 (full text), Eastham2024, Nielsen2024, Nielsen2025, David2026, David2026lca,
CortesPena2020, Jarvio2021 accepted manuscript, the three Intelligen white papers
(ovalbumin fetched 2026-09-26), Yao2026 (needs institutional access), DSM WO2022269549.

## 8. Recommendations for the plan
Status 2026-09-26: items 1 and 2 were adopted in PLAN.md v2. The anchors are now baker's
yeast (Humbird App. A, real price), NREL 2011 Area 400, Intelligen OVA 2025 and
Voutilainen 2021.
1. Add NREL 2011 Area 400 as validation target 1 (all inputs public, incl. yield).
2. Swap the Intelligen lactoferrin target for the Intelligen ovalbumin 2025 model
   once its PDF is obtained; keep lactoferrin as the high-purity DSP check.
3. `academic` scenario priors: BLG 1-5 g/L (K. phaffii), OVA 1-2 g/L (T. reesei).
   `industry` scenario: 24-42 g/L (gfi2025costs), 30 g/L (intelligen_ovalbumin2025).
4. Yield prior for the `academic` scenario has no product-specific evidence; use
   cellulase 0.24 as the ceiling and GFI's 0.03-0.17 as the range, grade D.
