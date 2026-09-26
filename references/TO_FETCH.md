# Documents to fetch by hand

Drop each file in the folder given, with the filename given (no spaces). Claude will then
run `pdftotext`, extract numbers with quotes, and update INDEX.md, titers.csv and
LITERATURE.md. If a link is dead, any copy of the same DOI is fine.

Priority: **P1** needed for validation or for the academic-scenario priors ·
**P2** improves a parameter or a review section · **P3** nice to have.

Confidence: items marked *(verify)* are ones Claude recalls from memory but could not
confirm online during the sweep; if the search turns up nothing, skip them and say so.

## A. Validation targets and TEAs

| P | key | citation | DOI / where | folder / filename |
|---|---|---|---|---|
| ✅ done 2026-09-26 | intelligen_ovalbumin2025 | Da Gama Ferreira R, Misailidis N, Parisis V, Petrides D. Egg white protein (ovalbumin) production via precision fermentation: process modeling and techno-economic assessment using SuperPro Designer. Intelligen Inc., 2025 | 10.13140/RG.2.2.29080.87048 (ResearchGate) | reports/Intelligen_2025_ovalbumin_TEA.pdf |
| P2 (was P1; plan v2 makes it optional) | intelligen_lactoferrin2024 | Da Gama Ferreira R, Misailidis N, Petrides D. Lactoferrin production via precision fermentation: process modeling and techno-economic assessment using SuperPro Designer. Intelligen Inc., 2024 | researchgate.net/publication/382686507 | reports/Intelligen_2024_lactoferrin_TEA.pdf |
| P2 | intelligen_collagen2024 | Da Gama Ferreira R, Misailidis N, Petrides D. Production of human collagen via fermentation (bio-collagen): techno-economic assessment using SuperPro Designer. Intelligen Inc., 2024 | researchgate.net/publication/380458369 | reports/Intelligen_2024_collagen_TEA.pdf |
| P1 | ellila2017 | Ellilä S, Fonseca L, Uchima C, et al. Development of a low-cost cellulase production process using Trichoderma reesei for Brazilian biorefineries. Biotechnol Biofuels 10:30 (2017) | 10.1186/s13068-017-0717-0 | papers/Ellila2017_lowcost_cellulase_treesei.pdf |
| P2 | johnson2016 *(verify)* | Johnson E. Integrated enzyme production lowers the cost of cellulosic ethanol. Biofuels Bioprod Bioref 10(2):164-174 (2016) | 10.1002/bbb.1634 | papers/Johnson2016_integrated_enzyme_cost.pdf |
| P2 | david2026 | David LH, Juliano P, Ridoutt B. The role of techno-economic analysis and life cycle assessment in guiding precision fermentation. Trends Food Sci Technol 168:105488 (2026) | 10.1016/j.tifs.2025.105488 | papers/David2026_TEA_LCA_precision_fermentation_review.pdf |
| P2 | david2026lca | David LH, Wollborn D, Ferreira RG, et al. Ex-ante life cycle assessment of recombinant human lactoferrin via precision fermentation. Int J Life Cycle Assess (2026) | 10.1007/s11367-026-02671-8 | papers/David2026_lactoferrin_exante_LCA.pdf |
| P2 | jarvio2021 | Järviö N, Parviainen T, Maljanen NL, et al. Ovalbumin production using Trichoderma reesei culture and low-carbon energy could mitigate the environmental impacts of chicken-egg-derived ovalbumin. Nature Food 2:1005-1013 (2021) (main text; SI already on disk) | 10.1038/s43016-021-00418-2 | papers/Jarvio2021_ovalbumin_LCA.pdf |
| P2 | perfectday_lca2021 *(verify)* | WSP / Perfect Day. Comparative life cycle assessment of Perfect Day whey protein production to dairy protein (2021). Company-commissioned LCA; gives feedstock per kg protein | perfectday.com (PDF) | reports/PerfectDay_2021_WSP_LCA_whey_protein.pdf |
| P2 | upcraft2021 *(verify)* | Upcraft T, Tu WC, Johnson R, et al. Protein from renewable resources: mycoprotein production from agricultural residues. Green Chem 23:5150 (2021) | 10.1039/D1GC01021B | papers/Upcraft2021_mycoprotein_TEA.pdf |
| P3 | humbird2021_journal | Humbird D. Scale-up economics for cultured meat. Biotechnol Bioeng 118:3239-3250 (2021), journal version | 10.1002/bit.27848 | papers/Humbird2021_cultured_meat_journal.pdf |
| P3 | cortespena2020 | Cortés-Peña Y, Kumar D, Singh V, Guest JS. BioSTEAM: a fast and flexible platform for the design, simulation, and techno-economic analysis of biorefineries under uncertainty. ACS Sustain Chem Eng 8:3302-3310 (2020) | 10.1021/acssuschemeng.9b07040 | papers/CortesPena2020_biosteam.pdf |
| P3 | humbird_fei2016 *(verify)* | Humbird D, Fei Q. Scale-up considerations for biofuels. In: Biotechnology for Biofuel Production and Optimization, Elsevier (2016), ch. 20 | 10.1016/B978-0-444-63475-7.00020-0 | papers/Humbird2016_scaleup_biofuels_chapter.pdf |

## B. Fermenter scale-up, oxygen transfer, capital cost (for the OTR test and CapEx curves)

| P | key | citation | DOI | folder / filename |
|---|---|---|---|---|
| P1 | crater2018 | Crater JS, Lievense JC. Scale-up of industrial microbial processes. FEMS Microbiol Lett 365(13):fny138 (2018) | 10.1093/femsle/fny138 | papers/Crater2018_scaleup_industrial_microbial.pdf |
| P1 | garciaochoa2009 | Garcia-Ochoa F, Gomez E. Bioreactor scale-up and oxygen transfer rate in microbial processes: an overview. Biotechnol Adv 27:153-176 (2009) | 10.1016/j.biotechadv.2008.10.006 | papers/GarciaOchoa2009_OTR_scaleup_review.pdf |
| P2 | junker2004 | Junker BH. Scale-up methodologies for Escherichia coli and yeast fermentation processes. J Biosci Bioeng 97(6):347-364 (2004) | 10.1016/S1389-1723(04)70218-2 | papers/Junker2004_scaleup_ecoli_yeast.pdf |
| P2 | towler_sinnott_ch7 | Towler G, Sinnott R. Chemical Engineering Design, 2nd ed., Elsevier (2013), ch. 7 "Capital cost estimating" (cost curves, Lang factors, six-tenths rule) | 10.1016/B978-0-08-096659-5.00007-9 | papers/TowlerSinnott2013_ch7_capital_cost.pdf |
| P3 | doran_ch10 *(chapter number may differ)* | Doran PM. Bioprocess Engineering Principles, 2nd ed., Academic Press (2013), chapter on mass transfer / oxygen transfer (kLa) | 10.1016/B978-0-12-220851-5.00010-1 | papers/Doran2013_mass_transfer_chapter.pdf |

## C. Host-level production benchmarks (batch time, cell density, titers, yields)

| P | key | citation | DOI | folder / filename |
|---|---|---|---|---|
| P1 | liu2019_hcd *(verify)* | Liu WC, Gong T, Wang QH, et al. Fed-batch high-cell-density fermentation strategies for Pichia pastoris growth and production. Crit Rev Biotechnol 39(2):258-271 (2019) | 10.1080/07388551.2018.1554620 | papers/Liu2019_pichia_fedbatch_HCD_review.pdf |
| P1 | yang2018_pichia *(verify)* | Yang Z, Zhang Z. Engineering strategies for enhanced production of protein and bio-products in Pichia pastoris: a review. Biotechnol Adv 36:182-195 (2018) | 10.1016/j.biotechadv.2017.11.002 | papers/Yang2018_pichia_engineering_review.pdf |
| P2 | karbalaei2020 | Karbalaei M, Rezaee SA, Farsiani H. Pichia pastoris: a highly successful expression system for optimal synthesis of heterologous proteins. J Cell Physiol 235:5867-5881 (2020) | 10.1002/jcp.29583 | papers/Karbalaei2020_pichia_review.pdf |
| P1 | nevalainen2014 | Nevalainen H, Peterson R. Making recombinant proteins in filamentous fungi: are we expecting too much? Front Microbiol 5:75 (2014) | 10.3389/fmicb.2014.00075 | papers/Nevalainen2014_filamentous_fungi_expectations.pdf |
| P1 | landowski2015 | Landowski CP, Huuskonen A, Wahl R, et al. Enabling low cost biopharmaceuticals: a systematic approach to delete proteases from a well-known protein production host Trichoderma reesei. PLoS ONE 10(8):e0134723 (2015) | 10.1371/journal.pone.0134723 | papers/Landowski2015_treesei_protease_deletion.pdf |
| P2 | cherry2003 *(verify the "100 g/L" claim lives here)* | Cherry JR, Fidantsef AL. Directed evolution of industrial enzymes: an update. Curr Opin Biotechnol 14:438-443 (2003) | 10.1016/S0958-1669(03)00099-5 | papers/Cherry2003_industrial_enzymes_update.pdf |
| P2 | nielsen2024 | Nielsen MB, Meyer AS, Arnau J. The next food revolution is here: recombinant microbial production of milk and egg proteins by precision fermentation. Annu Rev Food Sci Technol 15:173-187 (2024) | 10.1146/annurev-food-072023-034256 | papers/Nielsen2024_milk_egg_proteins_review.pdf |
| P2 | eastham2024 | Eastham JL, Leman AR. Precision fermentation for food proteins: ingredient innovations, bioprocess considerations, and outlook. Curr Opin Food Sci 58:101194 (2024) | 10.1016/j.cofs.2024.101194 | papers/Eastham2024_PF_food_proteins_minireview.pdf |
| P2 | hilgendorf2024 *(verify)* | Hilgendorf K, Wang Y, Miller MJ, Jin YS. Precision fermentation for improving the quality, flavor, safety, and sustainability of foods. Curr Opin Biotechnol 86:103084 (2024) | 10.1016/j.copbio.2024.103084 | papers/Hilgendorf2024_PF_review.pdf |
| P3 | kelley2009 | Kelley B. Industrialization of mAb production technology: the bioprocessing industry at a crossroads. mAbs 1(5):443-452 (2009). Chromatographic DSP cost structure, upper anchor | 10.4161/mabs.1.5.9448 | papers/Kelley2009_mAb_industrialization.pdf |
| P3 | farid2007 | Farid SS. Process economics of industrial monoclonal antibody manufacture. J Chromatogr B 848:8-18 (2007) | 10.1016/j.jchromb.2006.07.037 | papers/Farid2007_mAb_process_economics.pdf |

## D. BLG expression papers (full text; abstracts already extracted)

| P | key | citation | DOI | folder / filename |
|---|---|---|---|---|
| P1 | Yao2026 | Yao C, Zhu H, An Q, Zhang M, Zheng Y, Cai M. Omics-guided global rewiring of yeast metabolism enables high-level production of β-lactoglobulin. Food Biosci 82:109383 (2026) | 10.1016/j.fbio.2026.109383 | papers/Yao2026_blg_omics_kphaffii.pdf |
| P1 | Li2026 | Li Y, Yang J, Tao L, Liu Q, Zheng Y, Cai M. Transcriptional reprogramming with endogenous cis- and trans-elements for efficient food protein production in Komagataella phaffii (ESPRIT). Metab Eng (2026) | 10.1016/j.ymben.2026.102555 | papers/Li2026_esprit_blg_kphaffii.pdf |
| P1 | Aro2023 | Aro N, Ercili-Cura D, Andberg M, et al. Production of bovine beta-lactoglobulin and hen egg ovalbumin by Trichoderma reesei using precision fermentation technology and testing of their techno-functional properties. Food Res Int 163:112131 (2023) | 10.1016/j.foodres.2022.112131 | papers/Aro2023_treesei_blg_ova.pdf |
| P1 | Nielsen2025 | Nielsen MB, Meyer AS, Hansen K, Arnau J. Enhanced production of bovine β-lactoglobulin in an industrial Aspergillus oryzae host. Ind Biotechnol (2025/2026) | 10.1177/15509087251398318 | papers/Nielsen2025_blg_aspergillus_oryzae.pdf |
| P2 | Kim1997 | Kim TR, Goto Y, Hirota N, et al. High-level expression of bovine β-lactoglobulin in Pichia pastoris and characterization of its physical properties. Protein Eng 10(11):1339-1345 (1997) | 10.1093/protein/10.11.1339 | papers/Kim1997_pichia_blg.pdf |
| P2 | Invernizzi2008 | Invernizzi G, Šamalikova M, Brocca S, et al. In vivo aggregation of bovine β-lactoglobulin is affected by Cys at position 121. Protein Expr Purif 62:111-115 (2008) | 10.1016/j.pep.2008.06.012 | papers/Invernizzi2008_blg_pichia_ecoli.pdf |
| P3 | Totsuka1990 | Totsuka M, Katakura Y, Shimizu M, et al. Expression and secretion of bovine β-lactoglobulin in Saccharomyces cerevisiae. Agric Biol Chem 54(12):3111-3116 (1990) | 10.1080/00021369.1990.10870482 | papers/Totsuka1990_blg_scerevisiae.pdf |
| P3 | Rocha1996 | Rocha TL, Paterson G, Crimmins K, et al. Expression and secretion of recombinant ovine β-lactoglobulin in Saccharomyces cerevisiae and Kluyveromyces lactis. Biochem J 313:927-932 (1996) | 10.1042/bj3130927 | papers/Rocha1996_ovine_blg_yeasts.pdf |
| P3 | Nouaille2005 | Nouaille S, Bermúdez-Humarán LG, Adel-Patient K, et al. Improvement of bovine β-lactoglobulin production and secretion by Lactococcus lactis. Braz J Med Biol Res 38(3):353-359 (2005) | 10.1590/s0100-879x2005000300005 | papers/Nouaille2005_blg_lactococcus.pdf |

## E. OVA expression papers (full text)

| P | key | citation | DOI | folder / filename |
|---|---|---|---|---|
| P1 | Jin2024 | Jin KC, Seo SO, Kim SK. Animal-free production of hen egg ovalbumin in engineered Saccharomyces cerevisiae via precision fermentation. Int J Biol Macromol 271:132479 (2024) | 10.1016/j.ijbiomac.2024.132479 | papers/Jin2024_ova_scerevisiae.pdf |
| P2 | Ito2005 | Ito K, Matsudomi N. Structural characteristics of hen egg ovalbumin expressed in yeast Pichia pastoris. Biosci Biotechnol Biochem 69(4):755-761 (2005) | 10.1271/bbb.69.755 | papers/Ito2005_ova_pichia.pdf |
| P2 | Yang2009 | Yang S, Chen G, Yu X, Li M, Wang J. Cloning of a novel ovalbumin gene from quail oviduct and its heterologous expression in Pichia pastoris. J Basic Microbiol 49(S1):S73-S78 (2009) | 10.1002/jobm.200900018 | papers/Yang2009_quail_ova_pichia.pdf |
| P3 | Beck2025, GarciaCalvo2025, Yoon2026, Shemesh2024, Lv2025, Hazebrouck2007 | Full text already on disk from Europe PMC (references/text/*.fulltext.txt). PDFs optional | see INDEX.md | papers/<key>.pdf |

## F. Analogue proteins (full text)

| P | key | citation | DOI | folder / filename |
|---|---|---|---|---|
| P2 | Shao2022 | Shao Y, Xue C, Liu W, et al. High-level secretory production of leghemoglobin in Pichia pastoris through enhanced globin expression and heme biosynthesis. Bioresour Technol 363:127884 (2022) | 10.1016/j.biortech.2022.127884 | papers/Shao2022_leghemoglobin_pichia.pdf |
| P2 | Liu2026 | Liu K, Fan X, Tong Z, et al. Reprogrammed Komagataella phaffii for enhanced secretory expression of human lactoferrin. J Biotechnol (2026) | 10.1016/j.jbiotec.2026.07.011 | papers/Liu2026_hLF_kphaffii.pdf |
| P2 | Madler2026 | Mädler AK, Hosseini AF, Noack CE, Dadmohammadi Y, Abbaspourrad A. Extracellular expression of recombinant bovine lactoferrin in Pichia pastoris. Food Res Int (2026) | 10.1016/j.foodres.2026.119759 | papers/Madler2026_bLF_pichia.pdf |

## G. Regulatory filings (free, FDA GRAS inventory; process descriptions, purity, sometimes yields)

Search the FDA GRAS Notice Inventory (hfpappexternal.fda.gov/scripts/fdcc/?set=GRASNotices)
for these; numbers are from memory *(verify)*. Save the full notice PDF, not just the letter.

| P | key | notice | folder / filename |
|---|---|---|---|
| P1 | FDA-GRN863 | Perfect Day, β-lactoglobulin from Trichoderma reesei (GRN 863, 2020) | reports/FDA-GRN863_PerfectDay_BLG.pdf |
| P1 | FDA-GRN967 | Clara Foods, ovomucoid from Pichia pastoris (GRN 967, 2021) | reports/FDA-GRN967_Clara_ovomucoid.pdf |
| P1 | FDA-GRN1104 | The EVERY Company, ovalbumin from Komagataella phaffii (GRN 1104, ~2022-23) | reports/FDA-GRN1104_Every_ovalbumin.pdf |
| P2 | FDA-GRN737 full | Impossible Foods, soy leghemoglobin (GRN 737; only the FDA letter is on disk) | reports/Impossible_GRN737_full_notice.pdf |
| P2 | Vivici / Bon Vivant / Onego / Formo / New Culture | Any BLG, ovalbumin or casein GRAS notice filed 2023-2026 | reports/FDA-GRN<number>_<company>_<protein>.pdf |
| P2 | EFSA | Any EFSA novel-food opinion on recombinant BLG or ovalbumin (check the EFSA Journal 2024-2026) | reports/EFSA_<year>_<company>_<protein>.pdf |

## H. Patents still missing

| P | key | document | where | folder / filename |
|---|---|---|---|---|
| P1 | DSM2022 | WO 2022/269549 A2, DSM IP Assets, extended/recombinant β-lactoglobulin fermentation (the process Vivici's WO2025046004 cross-references, Example 1) | patents.google.com or Espacenet | patents/DSM_WO2022269549_blg-fermentation.pdf |
| P2 | Onego | Any Onego Bio / VTT ovalbumin patent (search assignees "Onego Bio", "Teknologian tutkimuskeskus VTT" with "ovalbumin") | Espacenet | patents/Onego_<number>_ovalbumin.pdf |

## J. After the v1 build (2026-09-26): what would most change the results

| P | item | why |
|---|---|---|
| P1 | Full texts of the unverified titer sources: Aro2023, Kim1997, Li2026, Yao2026, Rocha1996, Totsuka1990, Nouaille2005, Invernizzi2008, Nielsen2025, Jin2024, Yang2009, Shao2022, Liu2026 | 15 titers.csv rows rest on abstracts; Li 2026 (5.14 g/L BLG) and Aro 2023 (2 g/L OVA) set the academic scenario |
| P1 | Any BLG or OVA fed-batch with titer, productivity and sugar yield reported together | none exists in public; strain parameters are grade C |
| P1 | Jarvio 2021 SI (T. reesei OVA inventory, yield 0.39 derived) | the only public OVA yield-like number; check how it was derived |
| P2 | Garcia-Ochoa & Gomez 2009 tables; Humbird 2017 (bubble column vs STR) full text | kLa and max-OTR cross-checks (engineering.yaml has them as quote: null) |
| P2 | A heat-transfer coefficient for large fermenter jackets and coils | the 25 kW/m3 heat cap is grade D |
| P2 | Construction location factor, NW Europe vs US Midwest | EU capital is assumed equal to the US |
| P2 | Capital cost of a recent PF plant (e.g. Liberation Labs, 600 m3) | would settle the Humbird vs light convention question |
| P2 | Ovalbumin solubility at production conditions | the 50 g/L cap sets the OVA floor |
| P2 | USDA ERS dextrose price table (XLSX); USDA dried-albumen prices (PDF); CEPCI 2024-2025 (paywalled) | price evidence gaps listed in prices.yaml |

## I. Market and price data (not papers; CSV or PDF, into references/reports/)

| P | item | source | filename |
|---|---|---|---|
| done | WPC80 and WPI price series, US and EU | trade unit values 2015-2025 + USDA 2026 narratives in data/evidence/prices.yaml, data/prices/ | - |
| P1 | Dried egg white (albumen powder) price series, 2015-2026 | Urner Barry (paywalled) or USDA AMS Egg Market News weekly | reports/prices_egg_white_powder.csv |
| P1 | Dextrose / corn syrup (DE95) industrial price, US Midwest, and EU glucose syrup | USDA ERS Sugar and Sweeteners Yearbook, Table 8/9 | reports/prices_glucose.csv |
| done | Industrial electricity and natural gas, US and EU | EIA and Eurostat in data/evidence/prices.yaml | - |
