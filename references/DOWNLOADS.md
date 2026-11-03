# Documents to download (for Pablo)

**Status 2026-11-03.** Received, filed and read: 6 (Jin 2024), 9, 11, 12, 17, 22 (Yao 2026 SI, as
`papers/Yao2026_blg_yeast_SI.docx`), 27, 28, 29, 31, 34, 35, 40, 41, 42, 49, 50 (Kobayashi 2006 only)
and 51. What each changed is in the evidence entries (all now `read: fulltext`) and INDEX.md
section 6. Corrections: item 11 (Takors 2012) contains no OTR requirement (the >120 mmol/L/h is
Takors 2025); the Jin 2024 titer row now records the secreted 8 mg/L, not the 132 mg/L total.
Still open: 44 (Balasubramanian 2025; casein.yaml already cites a full-text read), 50 Ohya 2005,
the free items (7, 10, 13, 16, 18-20, 23, 24, 30, 39, 43, 45), books 33, 37, 38 (no library
access) and P3. None of them is used by a base case or a headline scenario.

**Status 2026-10-05 (titer check).** 43 of 134 rows in data/titers.csv are not verified in full text. No base case and
no headline scenario uses any of them. Four uses do, so these three papers come first (all paywalled):
**15** Liu 2026 (lactoferrin marker, report Figure 3), **32** Hu 2025 (lactoferrin marker, report Figure 3) and **48** Zhu 2018 (albumin
marker and the `alb_zhu2018` variant). Their chart labels now say "abstract only". The other 39 rows are literature
context (P3) and change nothing.
**2026-10-06:** 15 (Liu 2026), 32 (Hu 2025) and 48 (Zhu 2018) received, read and verified; their rows are now
`verified: yes` and the 'abstract only' labels are gone. Still worth having: P1c 22 (Yao 2026 Supplementary data).

**Status 2026-09-27.**
- Received and filed: 1 (Li), 2 (Yao), 3 (Aro), 4 (Järviö, article and Supplementary
  Information), 5 (Nielsen), FDA GRN 1056, plus Shukla 2026, Behm 2022, Zhang 2024, Yamanie 2026,
  Risner 2023, Puetz 2019, Klein-Marcuschamer 2012 and Voutilainen 2021 with its SI.
- Received and read on 2026-09-27: Heyland 2010 and Looser 2015 (P4 25–26), Humbird, Davis &
  McMillan 2017 (aeration), Intelligen's lactoferrin report (February 2026; P1b 14 / P5 36), Lv 2023
  (Green Chem), Prielhofer 2018, Rebnegger 2014, and the Li 2026 Supplementary data (P1c 21). What
  each changed is in docs/REVIEW.md (follow-up section).
- Still needed, in order of usefulness: **P1c** 22 (Yao 2026 Supplementary data: feed amounts, for a
  second measured BLG yield on sugar), P5 35, the rest of **P4**, P1b 15 (Liu 2026), 6 (Jin 2024), 7 (the
  other FDA GRAS notices), P2 (8–13), P5 37–38 (books, library). P3 is optional.

Save PDFs into `references/papers/` (articles) or `references/reports/` (FDA notices), with
the filename given. Both folders are git-ignored, so nothing copyrighted is published. DOIs
were checked against Crossref on 2026-09-26. Supplementary files: save next to the paper
with the suffix `_SI`.

## P1 — changes or verifies model inputs

| # | Document | DOI / where | Save as | Why |
|---|---|---|---|---|
| 1 | Li Y, Yang J, Tao L, et al. Transcriptional reprogramming with endogenous cis- and trans-elements for efficient food protein expression from safe substrates in *Komagataella phaffii*. Metabolic Engineering (2026; print 2027) | 10.1016/j.ymben.2026.102555 | `papers/Li2026_blg_kphaffii.pdf` | Sets the academic BLG scenario (5.14 g/L, abstract only so far). Need time, cell density, yield, scale |
| 2 | Yao C, Zhu H, An Q, et al. Omics-guided global rewiring of yeast metabolism enables high-level production of β-lactoglobulin. Food Bioscience 82:109383 (2026) | 10.1016/j.fbio.2026.109383 | `papers/Yao2026_blg_yeast.pdf` | Possibly a higher public BLG titer than Li 2026 |
| 3 | Aro N, Ercili-Cura D, Andberg M, et al. Production of bovine β-lactoglobulin and hen egg ovalbumin by *Trichoderma reesei*… Food Research International 163:112131 (2023). Open access | 10.1016/j.foodres.2022.112131 | `papers/Aro2023_trichoderma_blg_ova.pdf` | Sets the academic OVA scenario (2 g/L) |
| 4 | Järviö N, Parviainen T, Maljanen NL, et al. Ovalbumin production using *Trichoderma reesei* culture and low-carbon energy… Nature Food 2 (2021), **with its Supplementary Information** | 10.1038/s43016-021-00418-2 | `papers/Jarvio2021_ova_lca.pdf`, `papers/Jarvio2021_ova_lca_SI.pdf` | The only public OVA process inventory (titer, yield, time); our 0.39 g/g is derived from it and must be checked |
| 5 | Nielsen MB, Meyer AS, Hansen K, Arnau J. Enhanced production of bovine β-lactoglobulin in an industrial *Aspergillus oryzae* host. Industrial Biotechnology (2025) | 10.1177/15509087251398318 | `papers/Nielsen2025_blg_aoryzae.pdf` | May contain the only public BLG yield on sugar (">70% carbon yield" in the abstract is ambiguous) |
| 6 | Jin KC, Seo SO, Kim SK. Animal-free production of hen egg ovalbumin in engineered *Saccharomyces cerevisiae* via precision fermentation. Int J Biol Macromol 271:132479 (2024) | 10.1016/j.ijbiomac.2024.132479 | `papers/Jin2024_ova_scerevisiae.pdf` | Public OVA titer and process |
| 7 | FDA GRAS notices (free). Take the **full notice**, not only the FDA response letter, from the GRAS Notice Inventory (hfpappexternal.fda.gov/scripts/fdcc/?set=GRASNotices): GRN **1104** (egg-white protein from *K. phaffii*, EVERY, 2023); GRN **1249** (ovalbumin from *T. reesei*, 2025); GRN **863** (BLG from *T. reesei*, Perfect Day, 2020); GRN **1200** (BLG from *K. phaffii* VIPLA, 2025); GRN **1241** and **1145** (BLG from *A. oryzae*); GRN **1247** (BLG from *K. lactis*, 2025) | FDA inventory | `reports/FDA-GRN<number>.pdf` | Product specifications (our OVA spec is "by analogy"), process descriptions, sometimes yields |

## P1b — lactoferrin (contrast case) and milk/egg composition (added 2026-09-26)

| # | Document | DOI / where | Save as | Why |
|---|---|---|---|---|
| 14 | Da Gama Ferreira R, Misailidis N, Petrides D. Lactoferrin production via precision fermentation: process modeling and techno-economic assessment using SuperPro Designer. Intelligen (2024). No DOI | ResearchGate publication 382686507 (also shipped in SuperPro Designer's Examples folder) | `reports/Intelligen_2024_lactoferrin_TEA.pdf` | Design basis for lactoferrin (10 g/L, 5 days, 250 t/yr) and two downstream options |
| 15 | Liu K, Fan X, Tong Z, et al. Reprogrammed *Komagataella phaffii* for enhanced secretory expression of human lactoferrin. J Biotechnol (2026) (moved up from P3) | 10.1016/j.jbiotec.2026.07.011 | `papers/Liu2026_lactoferrin.pdf` | Best public lactoferrin titer in K. phaffii (~2.2 g/L) |
| 16 | Iglesias-Figueroa B, et al. High-level expression of recombinant bovine lactoferrin in *Pichia pastoris* with antimicrobial activity. Int J Mol Sci 17:902 (2016). Open access | 10.3390/ijms17060902 | `papers/IglesiasFigueroa2016_blf_pichia.pdf` | Bovine lactoferrin in yeast |
| 17 | Ward PP, Piddington CS, Cunningham GA, et al. A system for production of commercial quantities of human lactoferrin: a broad spectrum natural antibiotic. Bio/Technology 13:498 (1995) | 10.1038/nbt0595-498 | `papers/Ward1995_hlf_aspergillus.pdf` | Classic Aspergillus lactoferrin process |
| 18 | EFSA NDA Panel. Scientific opinion on bovine lactoferrin. EFSA Journal 10(5):2701 (2012). Open access | 10.2903/j.efsa.2012.2701 | `reports/EFSA2012_bovine_lactoferrin.pdf` | Food-grade lactoferrin specification |
| 19 | FDA GRAS notices on lactoferrin made by fermentation: search the inventory for "lactoferrin" (the site returned errors on 2026-09-26) | FDA GRAS Notice Inventory | `reports/FDA-GRN<number>.pdf` | Spec and process of commercial PF lactoferrin |
| 20 | Abeyrathne EDNS, Lee HY, Ahn DU. Egg white proteins and their potential use in food processing or as nutraceutical and pharmaceutical agents — a review. Poult Sci 92:3292 (2013). Open access | 10.3382/ps.2013-03391 | `papers/Abeyrathne2013_egg_white_proteins.pdf` | Ovalbumin share of egg-white protein (for the per-egg equivalent) |

## P1c — supplementary files that hold the missing process data (added 2026-09-26 night)

| # | Document | Where | Save as | Why |
|---|---|---|---|---|
| 21 | Li et al. 2026 (Metab Eng 99:102555) **Supplementary data**, especially Table S4 (glucose feed profile) | "Supplementary data" link on the ScienceDirect article page (doi 10.1016/j.ymben.2026.102555) | `papers/Li2026_blg_kphaffii_SI.pdf` (or .docx) | The only route to a public BLG yield on glucose |
| 22 | Yao et al. 2026 (Food Biosci 82:109383) **Supplementary data** (Figs S7, S10) | ScienceDirect article page (doi 10.1016/j.fbio.2026.109383) | `papers/Yao2026_blg_yeast_SI.pdf` | Feed amounts for the 13.88 g/L run |
| 23 | Järviö et al. 2021 (Nature Food) **Supplementary Data** file (the model-input spreadsheet, not the Supplementary Information PDF, which is already on disk) | Nature Food article page, "Supplementary information" section (doi 10.1038/s43016-021-00418-2) | `papers/Jarvio2021_ova_lca_SD.xlsx` | Titer, time and biomass behind the inventory |
| 24 | Nelisse P et al. (DSM). WO2022269549A2 (2022): extended β-lactoglobulin fermentation | patents.google.com/patent/WO2022269549A2 (free) | `patents/DSM_WO2022269549_blg-fermentation.pdf` | A. niger BLG process data (Vivici's lineage) |

## P4 — sources behind v2 values that were read only as abstracts (added 2026-09-27)

Each is cited in `data/evidence/` with `read: abstract` (or as an unverified lead). With the full
text we can check the quote, or replace the value. DOIs checked against Crossref on 2026-09-27.

| # | Document | DOI | Save as | Why |
|---|---|---|---|---|
| 25 | Heyland J, Fu J, Blank LM, Schmid A. Quantitative physiology of *Pichia pastoris* during glucose-limited high-cell density fed-batch cultivation for recombinant protein production. Biotechnol Bioeng 107:357–368 (2010) | 10.1002/bit.22836 | `papers/Heyland2010_pichia_fedbatch_physiology.pdf` | Fed-batch maintenance of a producing strain on glucose: checks the production-phase maintenance that sets the product yield (report Methods 2.2) |
| 26 | Looser V, Bruhlmann B, Bumbak F, et al. Cultivation strategies to enhance productivity of *Pichia pastoris*: a review. Biotechnol Adv 33:1177–1193 (2015) | 10.1016/j.biotechadv.2015.05.008 | `papers/Looser2015_pichia_cultivation_review.pdf` | Tabulated maintenance and productivity values across studies |
| 27 | Tsai LS, Ijichi K, Harris MW. Concentration of egg white by ultrafiltration. J Food Prot 40(7):449–455 (1977) | 10.4315/0362-028X-40.7.449 | `papers/Tsai1977_egg_white_UF.pdf` | Basis for the OVA dryer-feed solids and for dropping the 50 g/L solubility limit |
| 28 | Froning GW, Wehling RL, Ball HR, Hill RM. Effect of ultrafiltration and reverse osmosis on the composition and functional properties of egg white. Poult Sci 66:1168–1173 (1987) | 10.3382/ps.0661168 | `papers/Froning1987_egg_white_UF_RO.pdf` | Same question; currently an unverified lead |
| 29 | Garnica-Garcia F, Lal N, Marcellin E. Primary challenges in the upcycling of genetically modified spent microbial biomass. New Biotechnol 94:172–183 (2026) | 10.1016/j.nbt.2026.05.008 | `papers/GarnicaGarcia2026_spent_biomass.pdf` | Spent-cell disposal route (base: sterilise and landfill) |
| 30 | Pires MC, Jungbauer A, Lau D, et al. Column ageing of agarose-based chromatography in industrial lactoferrin purification. J Chromatogr A 1760:466274 (2025). Open access (CC BY) | 10.1016/j.chroma.2025.466274 | `papers/Pires2025_lactoferrin_column_ageing.pdf` | Resin lifetime in the lactoferrin case |
| 31 | Wang X, Liao Y, Guo X, Xing D, et al. Comparative study of cation-exchange resins for high-efficiency preparation of bovine lactoferrin and its N-glycomic analysis by HILIC-MS/MS. J Agric Food Chem 74(7):6488–6504 (2026) | 10.1021/acs.jafc.5c12835 | `papers/Wang2026_lactoferrin_cex_resins.pdf` | Binding capacity of the capture resin |
| 32 | Hu C, Shen W, Xia Y, Zhou L, Yang H, Chen X. Efficient production of the recombinant human lactoferrin in an engineered *Trichoderma reesei*. J Agric Food Chem 73:32795–32806 (2025) | 10.1021/acs.jafc.5c11534 | `papers/Hu2025_lactoferrin_treesei.pdf` | Lactoferrin titer table |
| 33 | Towler G, Sinnott R. Chemical Engineering Design, 2nd ed. Elsevier (2013), ch. 7 "Capital cost estimating" (a library copy is fine) | 10.1016/B978-0-08-096659-5.00007-9 | `papers/TowlerSinnott2013_ch7_capital_cost.pdf` | Location factors and installation factors, a textbook cross-check of the capital conventions |
| 34 | Huntington JA, Stein PE. Structure and properties of ovalbumin. J Chromatogr B 756:189–198 (2001) | 10.1016/S0378-4347(01)00108-6 | `papers/Huntington2001_ovalbumin_structure.pdf` | Optional: ovalbumin properties (currently an unverified lead) |

## P5 — raised by the Phase F AI pre-review (added 2026-09-27)

| # | Document | DOI / where | Save as | Why |
|---|---|---|---|---|
| 35 | Lv X, Cui S, Chen J, et al. Cascaded de novo biosynthesis of lacto-proteins from CO₂ by engineered *Pichia pastoris*. Green Chemistry 25:5460–5469 (2023). (The file saved as `papers/Lv2023.pdf` on 2026-09-27 is a different paper by the same group, on lactoferricin; it can stay but is not this one.) | 10.1039/d3gc00867c | `papers/Lv2023_lacto-proteins_greenchem.pdf` | A review cites "P_AOX1 lacto-protein 5.4 g/L" from it; if that protein is BLG it is the highest public BLG titer (methanol-induced) |
| 36 | Da Gama Ferreira R, Misailidis N, Petrides D. Lactoferrin production via precision fermentation (Intelligen, 2024) — same as item 14, now more useful | ResearchGate 382686507 | `reports/Intelligen_2024_lactoferrin_TEA.pdf` | Their cost of production is $292/kg against our $123–203; their operating-cost breakdown would show where the models differ |
| 37 | Cheryan M. Ultrafiltration and Microfiltration Handbook. Technomic (1998), chapters on whey and on diafiltration (library copy) | ISBN 978-1566765985 | `papers/Cheryan1998_UF_MF_handbook_excerpt.pdf` | Whey-protein UF and diafiltration fluxes at scale; the reviewer's 10–20 L/m²/h would replace our single patent value (5) |
| 38 | Peters MS, Timmerhaus KD, West RE. Plant Design and Economics for Chemical Engineers, 5th ed. McGraw-Hill (2003), ch. 6 (library copy) | ISBN 978-0072392661 | `papers/Peters2003_ch6_cost_estimation.pdf` | Standard ranges for maintenance, insurance, local taxes and plant overhead, to test Humbird's 9% rule |

## P2 — engineering cross-checks

| # | Document | DOI | Save as | Why |
|---|---|---|---|---|
| 8 | Humbird D, Davis R, McMillan JD. Aeration costs in stirred-tank and bubble column bioreactors. Biochem Eng J 127:161–166 (2017) | 10.1016/j.bej.2017.08.006 | `papers/Humbird2017_aeration_costs.pdf` | Basis of the O₂-transfer cap and aeration cost |
| 9 | Garcia-Ochoa F, Gomez E. Bioreactor scale-up and oxygen transfer rate in microbial processes: an overview. Biotechnol Adv 27:153–176 (2009) | 10.1016/j.biotechadv.2008.10.006 | `papers/GarciaOchoa2009_otr_scaleup.pdf` | kLa correlations and typical OTRs |
| 10 | Crater JS, Lievense JC. Scale-up of industrial microbial processes. FEMS Microbiol Lett 365:fny138 (2018). Open access | 10.1093/femsle/fny138 | `papers/Crater2018_scaleup.pdf` | Industrial vessel sizes, OTR and heat limits |
| 11 | Takors R. Scale-up of microbial processes: impacts, tools and open questions. J Biotechnol 160:3–9 (2012) | 10.1016/j.jbiotec.2011.12.010 | `papers/Takors2012_scaleup.pdf` | **Received 2026-11-03.** No OTR number (the >120 mmol/L/h is Takors 2025); gives large-scale mixing times and head pressures |
| 12 | Knoll A, Maier B, Tscherrig H, Büchs J. The oxygen mass transfer, carbon dioxide inhibition, heat removal, and the energy and cost efficiencies of high pressure fermentation. Adv Biochem Eng Biotechnol 92:77–99 (2005) | 10.1007/b98918 | `papers/Knoll2005_pressure_fermentation.pdf` | Heat removal as the limit under pressure |
| 13 | Liu WC, Gong T, Wang QH, et al. Scaling-up fermentation of *Pichia pastoris* to demonstration-scale… Sci Rep 6:18439 (2016). Open access | 10.1038/srep18439 | `papers/Liu2016_pichia_pressure.pdf` | Head-pressure gain used by the physical-limit scenario |

## P3 — completeness of the titer table (not used in scenarios)

| Document | DOI | Save as |
|---|---|---|
| Kim TR et al. High-level expression of bovine β-lactoglobulin in *Pichia pastoris*… Protein Eng 10:1339 (1997) | 10.1093/protein/10.11.1339 | `papers/Kim1997_blg_pichia.pdf` |
| Totsuka M et al. Expression and secretion of bovine β-lactoglobulin in *S. cerevisiae*. Agric Biol Chem 54:3111 (1990) | 10.1080/00021369.1990.10870482 | `papers/Totsuka1990_blg_scerevisiae.pdf` |
| Rocha TL et al. Expression and secretion of recombinant ovine β-lactoglobulin in *S. cerevisiae* and *K. lactis*. Biochem J 313:927 (1996). Open access | 10.1042/bj3130927 | `papers/Rocha1996_blg_klactis.pdf` |
| Nouaille S et al. Improvement of bovine β-lactoglobulin production and secretion by *Lactococcus lactis*. Braz J Med Biol Res 38:353 (2005). Open access | 10.1590/s0100-879x2005000300005 | `papers/Nouaille2005_blg_llactis.pdf` |
| Invernizzi G et al. In vivo aggregation of bovine β-lactoglobulin is affected by Cys at position 121. Protein Expr Purif 62 (2008) | 10.1016/j.pep.2008.06.012 | `papers/Invernizzi2008_blg_ecoli.pdf` |
| Yang S et al. Cloning of a novel ovalbumin gene from quail oviduct and its heterologous expression in *Pichia pastoris*. J Basic Microbiol 49:S73 (2009) | 10.1002/jobm.200900018 | `papers/Yang2009_ova_pichia.pdf` |
| Shao Y et al. High-level secretory production of leghemoglobin in *Pichia pastoris*… Bioresour Technol 363:127884 (2022) | 10.1016/j.biortech.2022.127884 | `papers/Shao2022_leghemoglobin.pdf` |
| Liu K et al. Reprogrammed *Komagataella phaffii* for enhanced secretory expression of human lactoferrin. J Biotechnol (2026) | 10.1016/j.jbiotec.2026.07.011 | `papers/Liu2026_lactoferrin.pdf` |

Items 25–34 came from the v2 placeholder and lactoferrin searches. More will be added if the review finds gaps.

## P6 — casein (added 2026-10-01; for the β-casein product)

Save patents in `references/patents/`, articles in `references/papers/` (both git-ignored).

| # | Document | Where | Save as | Why |
|---|---|---|---|---|
| 39 | NewMilkBuzz patent family: WO2024256611A1, WO2023242273A1, EP4623075A1, EP4676233A1, WO2025109136A1 | patents.google.com/patent/<number>/en ("Download PDF") | `patents/NewMilkBuzz_<number>.pdf` | Most likely public source of a yeast or fungal casein titer and a casein purification route |
| 40 | Choi BK, Jiménez-Flores R. J Agric Food Chem 44:358 (1996) | 10.1021/jf950339i | `papers/Choi1996_bcasein_pichia.pdf` | Best β-casein titer in *K. phaffii* (0.7–1.0 g/L), read only as an abstract |
| 41 | Choi BK, Jiménez-Flores R. J Agric Food Chem (2001) | 10.1021/jf001298f | `papers/Choi2001_bcasein_pichia_phospho.pdf` | The only yeast casein reported phosphorylated like milk casein; the academic variant (0.245 g/L) |
| 42 | Animal-free caseins by precision fermentation: technical challenges and perspectives. Trends Food Sci Technol (2026) | 10.1016/j.tifs.2026.105878 | `papers/TIFS2026_animal_free_caseins.pdf` | Best single review of the field |
| 43 | Fermify WO2024200234A1 (non-micellar casein gel) | patents.google.com | `patents/Fermify_WO2024200234A1.pdf` | Cheese without micelles: does unphosphorylated casein work? |
| 44 | Balasubramanian et al. Trends Biotechnol 43:2304 (2025) | journal page | `papers/Balasubramanian2025_phospho_as1_ecoli.pdf` | Fully phosphorylated αs1-casein in *E. coli*; may give a titer |
| 45 | FDA GRN 967 and GRN 1104 full notices (EVERY: ovomucoid; egg-white protein) | FDA GRAS Notice Inventory | `reports/FDA-GRN967_ovomucoid.pdf`, `reports/FDA-GRN1104_egg-white.pdf` | Specs and process for the next product (ovomucoid / egg-white mix) |

## P7 — albumin and the v4 model review (added 2026-10-02)

Save articles in `references/papers/`, reports in `references/reports/` (both git-ignored). In order of value:

| # | Document | DOI / where | Save as | Why |
|---|---|---|---|---|
| 46 | **Received 2026-10-02.** Zhu W, Xu R, Gong G, et al. Medium optimization for high yield production of human serum albumin in *Pichia pastoris* and its efficient purification. Protein Expr Purif 181:105831 (2021) | 10.1016/j.pep.2021.105831 | `papers/Zhu2021_hsa_pichia.pdf` | Albumin's academic titer (17.47 g/L, 192 h, methanol), read only as an abstract: needs scale, cell density, methanol use and the 3-step purification |
| 47 | **Received 2026-10-02 (OCR'd: references/text/RAND_R2569.txt).** Merrow EW, Phillips KE, Myers CW. Understanding cost growth and performance shortfalls in pioneer process plants. RAND R-2569-DOE (1981). Free | rand.org/pubs/reports/R2569.html (blocks scripts; download in a browser) | `reports/RAND_R2569_pioneer_plants.pdf` | The only sourced basis for a first-of-a-kind premium (SCOPE promises it as a separate sensitivity) |
| 48 | Zhu W, Gong G, Pan J, et al. High level expression and purification of recombinant human serum albumin in *Pichia pastoris*. Protein Expr Purif 147:61 (2018) | 10.1016/j.pep.2018.02.003 | `papers/Zhu2018_hsa_pichia.pdf` | Albumin variant (8.86 g/L in 96 h); time course, recovery 58% |
| 49 | Mallem M, et al. Biotechnol Prog (2014): rHSA in Mut-s *K. phaffii* at 10 g/L | 10.1002/btpr.1990 | `papers/Mallem2014_hsa_muts.pdf` | Induction length, specific productivity and growth rate (two weeks at mu ~0.002/h?) |
| 50 | Kobayashi K, et al. Biologicals 34:55 (2006); Ohya T, et al. Biotechnol Bioeng 90:876 (2005) | 10.1016/j.biologicals.2005.08.021 | `papers/Kobayashi2006_medway.pdf`, `papers/Ohya2005_medway.pdf` | The Mitsubishi (Medway) industrial rHSA process: commercial titer and purification |
| 51 | Sun et al. Industrial recombinant HSA review. Biotechnol Adv 90:108914 (2026) | 10.1016/j.biotechadv.2026.108914 | `papers/Sun2026_rhsa_review.pdf` | Current industrial titers and trains in one place |
