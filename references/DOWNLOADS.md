# Documents to download (for Pablo)

**Status 2026-09-26 evening.**
- Received and filed: 1 (Li), 2 (Yao), 3 (Aro), 4 main article (Järviö), 5 (Nielsen), plus a review
  (Shukla 2026, *Applied Food Research* 6:102015).
- Still needed: 4 **Supplementary Information** (Järviö), 6 (Jin 2024), 7 (the FDA GRAS notices),
  and P2 (8–13). P3 is optional.

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

## P2 — engineering cross-checks

| # | Document | DOI | Save as | Why |
|---|---|---|---|---|
| 8 | Humbird D, Davis R, McMillan JD. Aeration costs in stirred-tank and bubble column bioreactors. Biochem Eng J 127:161–166 (2017) | 10.1016/j.bej.2017.08.006 | `papers/Humbird2017_aeration_costs.pdf` | Basis of the O₂-transfer cap and aeration cost |
| 9 | Garcia-Ochoa F, Gomez E. Bioreactor scale-up and oxygen transfer rate in microbial processes: an overview. Biotechnol Adv 27:153–176 (2009) | 10.1016/j.biotechadv.2008.10.006 | `papers/GarciaOchoa2009_otr_scaleup.pdf` | kLa correlations and typical OTRs |
| 10 | Crater JS, Lievense JC. Scale-up of industrial microbial processes. FEMS Microbiol Lett 365:fny138 (2018). Open access | 10.1093/femsle/fny138 | `papers/Crater2018_scaleup.pdf` | Industrial vessel sizes, OTR and heat limits |
| 11 | Takors R. Scale-up of microbial processes: impacts, tools and open questions. J Biotechnol 160:3–9 (2012) | 10.1016/j.jbiotec.2011.12.010 | `papers/Takors2012_scaleup.pdf` | Cited for the >120 mmol/L/h OTR requirement |
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

More items will be added here if the placeholder-parameter search finds paywalled sources.
