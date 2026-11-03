# Industrial enzyme prices per kg product and per kg protein: public evidence

Compiled 2026-11-03 for pf-tea (benchmark for the secreted-protein cost model).

## How this was gathered: read this first

- **No full-text reads were possible.** The session's network policy blocked direct fetches.
  - `ec.europa.eu` (Eurostat Comext API) and `pmc.ncbi.nlm.nih.gov` both failed DNS resolution in WebFetch.
  - curl was refused by the egress proxy for every host tried, including comtradeapi.un.org, api.census.gov, novonesis.com, gfi.org and osti.gov.
  - To verify these entries, `ec.europa.eu`, `wits.worldbank.org`, `pmc.ncbi.nlm.nih.gov`, `efsa.onlinelibrary.wiley.com`, `osti.gov` and `gfi.org` have to be allowed in the session's network settings.
- **Every quote below comes from a web-search result snippet, not from the document itself.** Each entry is marked `read: search-snippet`. Some quotes are paraphrases written by the search tool rather than verbatim text, and those are labelled `quote_status: paraphrase`.
- **Treat every value as grade C at best until someone opens the source.** The URL and locator given are where to check.
- **Derived values are plain division only.** A `kind: derived` entry divides two numbers that the same source reports in the same row. No other number in this file is estimated.
- **Terms used in this file:**
  - price = what a buyer pays.
  - cost = a producer's cost, or a modelled cost of production.
  - model_output = a number produced by a TEA or model.
  - trade_unit_value = customs value divided by customs quantity. It is per kg of shipped product (liquid, granulate or powder), not per kg of protein.

---

## 1. Prices and trade unit values per kg product

```yaml
- key: hs350790_world_exporters_2023_wits
  value: null
  unit: "US$ thousand (trade value) and kg (quantity), per reporter, exports to World"
  basis: "per kg PRODUCT as declared to customs (mixed liquid/granulate/powder; protein content unknown)"
  year: 2023
  money_year: "2023 nominal USD"
  kind: trade_unit_value (inputs)
  source: "World Bank WITS, UN Comtrade mirror, HS 350790 'Enzymes; prepared enzymes n.e.s.' (HS 1988/92 nomenclature), exports by country"
  url: "https://wits.worldbank.org/trade/comtrade/en/country/ALL/year/2023/tradeflow/Exports/partner/WLD/product/350790"
  locator: "page summary sentence 'Top exporters ...' and the exporter table"
  quote: "In 2023, Top exporters of Enzymes; prepared enzymes (not elsewhere specif are European Union ($2,159,096.98K), United States ($1,561,447.37K, 53,533,400 Kg), Denmark ($1,342,445.20K, 100,268,000 Kg), Netherlands"
  other_rows_from_snippet: "Netherlands 749,210.18K / 70,521,000 kg; China 527,964.65K / 105,179,000 kg; France 428,610.45K / (qty not in snippet); Finland 309,534.57K / 50,571,200 kg; Japan 272,698.20K / 4,139,850 kg; Brazil 71,743.05K / 6,233,220 kg; India 67,962.62K / 3,719,550 kg"
  read: search-snippet
  quote_status: "verbatim for EU/US/DK; other rows were reported by the search tool without column labels (assumed value in US$K, quantity in kg)"
  note: "The EU row has no quantity in the snippet. Comtrade quantities are sometimes estimated by UNSD, so check the quantity flag on the page."

- key: hs350790_export_unit_value_2023_by_country
  value: {Denmark: 13.39, Netherlands: 10.62, China: 5.02, Finland: 6.12, Brazil: 11.51, India: 18.27, United States: 29.17, Japan: 65.87}
  unit: "USD/kg product"
  basis: "per kg PRODUCT (customs weight). Protein content unknown"
  year: 2023
  money_year: "2023 nominal USD"
  kind: derived (value / quantity from the entry above; division only)
  source: "as hs350790_world_exporters_2023_wits"
  url: "https://wits.worldbank.org/trade/comtrade/en/country/ALL/year/2023/tradeflow/Exports/partner/WLD/product/350790"
  locator: "same rows"
  quote: "see entry above"
  note: >
    Denmark is the natural 'Novonesis proxy': Danish enzyme exports are dominated by Novonesis (formerly Novozymes).
    This last point is general knowledge and is not stated by WITS. Danish exports come to ~USD 13/kg product.
    China (~5/kg) and Finland (~6/kg; AB Enzymes/IFF Genencor sites, feed and technical enzymes) are lower.
    The US (29/kg) and Japan (66/kg) are high and may include specialty, diagnostic or pharma enzymes.
    HS 3507.90 also covers non-fermentation enzymes (e.g., papain, pancreatin), so it is not a pure secreted-microbial-enzyme series.
    Reported country totals differ by source: OEC gives Denmark ~USD 1.65 B for 2023, because it uses the BACI reconciliation and covers all of heading 3507.

- key: denmark_hs350790_exports_partner_examples_2023
  value: {Poland: "53.9 M USD / 4.13 M kg", South_Africa: "22.9 M USD / 2.45 M kg", Norway: "4.9 M USD / 224,845 kg", Slovakia: "3.5 M USD / 380,859 kg"}
  unit: "USD and kg"
  basis: "per kg product"
  year: 2023
  kind: trade_unit_value (inputs)
  source: "WITS partner pages, HS 350790"
  url: "https://wits.worldbank.org/trade/comtrade/en/country/All/year/2023/tradeflow/Exports/partner/POL/product/350790 (and /ZAF/, /NOR/, /SVK/)"
  locator: "Denmark row"
  quote: "(paraphrase by search tool) Poland: about 4.13 million kg (about $53.9 million) ... South Africa: about 2.45 million kg (about $22.9 million)"
  read: search-snippet
  quote_status: paraphrase
  note: "These imply roughly 9-22 USD/kg depending on destination, so partner mix matters. Rounded numbers; verify before use."

- key: cn35079030_eu_import_avg_price
  value: 112.13
  unit: "EUR/kg product"
  basis: "per kg product, CN 3507 90 30 (lipoprotein lipase; Aspergillus alkaline protease), EU imports"
  year: "2022-2025 aggregate (as displayed by site)"
  kind: trade_unit_value
  source: "thetradehub.eu (re-publishes Eurostat Comext)"
  url: "https://www.thetradehub.eu/en/customs/trade/35079030"
  locator: "summary panel"
  quote: "(paraphrase by search tool) shows exports of €53.1M compared to €25.4M in imports for 2022-2025, with an average price of €112.13/kg on the import side"
  read: search-snippet
  quote_status: paraphrase
  note: "Niche specialty subheading, not a bulk benchmark. The same site states heading 3507 as a whole at €8.8B and 601.2M kg (implied ~14.6 EUR/kg), but the period is unclear. Verify against Comext DS-045409, which the repo already uses for casein."

- key: china_bulk_vs_specialty_enzyme_price_marketreport
  value: null
  low: 2500
  high: 3500
  unit: "USD/tonne product (bulk detergent and starch enzymes); specialty food enzymes 4000-6000 USD/t"
  basis: "per tonne product, China market"
  year: "not stated (page ~2025)"
  kind: price (market-research claim)
  source: "Markspark Solutions, 'China industrial enzymes market' report page"
  url: "https://marksparksolutions.com/reports/china-industrial-enzymes-market"
  locator: "report summary"
  quote: "Bulk enzymes used in detergents and starch processing typically cost between USD 2,500 and USD 3,500 per ton, while specialty enzymes used in food processing and advanced applications range from USD 4,000 to USD 6,000 per ton."
  read: search-snippet
  note: "No methodology. Grade D. Consistent in order of magnitude with China's HS 350790 export unit value (~5 USD/kg)."

- key: china_feed_enzyme_output_and_value_2022
  value: null
  quantity_t: 229000
  value_rmb: 3.491e9
  unit: "tonnes product; RMB (output value)"
  basis: "feed enzymes (compound feed enzymes 131,500 t + phytase 97,500 t), per tonne product"
  year: 2022
  kind: "industry statistics (output value at producer level)"
  source: "Quantity: Zhiyan Consulting (chyxx.com). Value: Guanyan Tianxia (chinabaogao.com). Two different consultancies."
  url: "https://www.chyxx.com/industry/1159149.html ; https://www.chinabaogao.com/baogao/202408/725825.html"
  locator: "text"
  quote: "据统计,截至2022年我国饲料酶制剂产量约为22.9万吨;细分来看,2022年我国饲料复合酶产量约为13.15万吨,饲料植酸酶产量约为9.75万吨。 / 2015-2022年我国饲料酶制剂行业产值从15.2亿元增长至34.91亿元左右。"
  read: search-snippet
  note: "Dividing the two gives ~15,200 RMB/t (~15 RMB/kg product), but the numerator and denominator come from different consultancies, so I did not compute a USD figure and the ratio should not be relied on. Grade D."

- key: zhuang2007_cellulase_market_price
  value: 90.0
  unit: "USD/kg (basis 'kg' of cellulase, undefined: product vs protein not stated in snippet)"
  basis: "unclear"
  year: "2004 USD"
  kind: price (quoted market price in a TEA)
  source: "Zhuang J, Marchant MA, Nokes SE, Strobel HJ. Economic analysis of cellulase production methods for bio-ethanol. Applied Engineering in Agriculture 23(5) (2007)"
  url: "https://uknowledge.uky.edu/bae_facpub/102"
  locator: "abstract"
  quote: "the corresponding market price was over $90.00/kg"
  read: search-snippet
  note: "The 2004 working-paper version (ageconsearch.umn.edu/record/31982) gives a market price of $36.00/kg instead. Same paper's model costs: $15.67/kg (solid-state) and $40.36/kg (submerged) -> kind: model_output. Old, ambiguous basis, grade C-/D."

- key: puetz2019_cellulase_price
  value: 10.0
  unit: "USD/kg"
  basis: "not stated in snippet (Table 1 of review; 'per kg' of product or protein to be checked)"
  year: "2019 review (money year not stated)"
  kind: price (review table)
  source: "Puetz J, Wurm FM. Recombinant proteins for industrial versus pharmaceutical purposes: a review of process and pricing. Processes 7(8):476 (2019). doi:10.3390/pr7080476"
  url: "https://www.mdpi.com/2227-9717/7/8/476"
  locator: "Table 1 (cellulase, T. reesei, fuel ethanol)"
  quote: "(paraphrase by search tool) The paper's Table 1 lists cellulase from T. reesei for fuel ethanol at $10.00/kg."
  read: search-snippet
  quote_status: paraphrase
  note: "Already in references as puetz2019. Check Table 1 for its own source; it may trace back to Klein-Marcuschamer 2012, which is a model cost, not a price."

- key: retail_and_b2b_listings_phytase_protease
  value: null
  unit: "various (INR/kg, USD/kg, USD/t), small lots"
  basis: "per kg product, activity-specified (e.g., 5000 U/g phytase)"
  year: "undated listings, ~2025-2026"
  kind: price (catalogue/B2B listing)
  source: "IndiaMART, TradeIndia, Made-in-China, enzymes.bio, Alibaba listings"
  url: "https://m.indiamart.com/impcat/phytase.html ; https://www.madeinchina.com/mall/show-493787.html ; https://enzymes.bio/product/food-grade-phytase-enzyme/"
  locator: "listing pages"
  quote: "(paraphrase by search tool) Made-in-China listing shows a price of $3000.00 with a minimum order of 1 Ton ... enzymes.bio food-grade phytase US$116.99 for 1 kg ... one alkaline protease granule listing is $3-4 with a 100 kg minimum order"
  read: search-snippet
  note: "Not usable as a benchmark: units ambiguous, lots small, quality unknown. Listed only to show the spread (~3 to >100 USD/kg)."
```

## 2. Prices or values per kg PROTEIN (direct)

```yaml
- key: lynd2017_amylase_corn_ethanol_value_per_kg_protein
  value: 25
  unit: "USD/kg protein"
  basis: "per kg PROTEIN; amylase (mature technology) bought in bulk by the US corn-ethanol industry"
  year: "2017 paper (money year not stated)"
  kind: "price indicator (authors' stated valuation, primary source not given in snippet)"
  source: "Lynd LR, Liang X, Biddy MJ, et al. Cellulosic ethanol: status and innovation. Curr Opin Biotechnol 45:202-211 (2017). doi:10.1016/j.copbio.2017.03.008"
  url: "https://www.osti.gov/servlets/purl/1364156"
  locator: "section on enzyme cost (author manuscript)"
  quote: "(paraphrase by search tool) enzymes from mature technology bought in bulk by the corn ethanol industry are valued at about $25/kg protein ... The cost of at-site enzyme production is estimated by Klein-Marcuschamer et al. [10] to be $10/kg protein."
  read: search-snippet
  quote_status: "paraphrase; second sentence appears verbatim"
  note: >
    The closest thing found to a public per-kg-PROTEIN market value for a bulk secreted enzyme. The authors also use $15/kg protein for cellulase in a calculation (-> ~$1.82/gal at 10 mg protein/g dry solids). 
    Must verify the exact wording and whether a source is cited. Grade B/C once read.

- key: liu2016_purchased_cellulase_price_range
  value: null
  low: 1.25
  high: 23.30
  unit: "USD/kg protein"
  basis: "per kg PROTEIN; low = soy-protein floor, high = 'open industrial list price' per search summary"
  year: "2015/2016"
  kind: "price assumptions used in a TEA sensitivity"
  source: "Liu G, Zhang J, Bao J. Cost evaluation of cellulase enzyme for industrial-scale cellulosic ethanol production based on rigorous Aspen Plus modeling. Bioprocess Biosyst Eng 39(1):133-140 (2016). doi:10.1007/s00449-015-1497-1"
  url: "https://sklbe.ecust.edu.cn/BiomassLab/ckfinder/userfiles/files/BPBSE-2016-39-133-140-Cost evaluation of cellulase enzyme for industrial scale cellulosic ethanol production based on rigorous Aspen plus modeling.pdf"
  locator: "enzyme price section/table (not located)"
  quote: "(paraphrase by search tool) The authors tested purchased-enzyme prices from about $1.25 to $23.30 per kg protein ... its highest is an open industrial list price."
  read: search-snippet
  quote_status: paraphrase
  note: "A targeted search for '$23.30' did NOT reproduce it, so treat as unverified until the PDF is read. Same paper's model costs: on-site 3.80-6.75, off-site 4.00-8.80 USD/kg protein (kind: model_output; these may originate in Hong et al. 2013, BBB doi:10.1002/bbb.1393)."
```

## 3. Model costs (NOT prices), for context only

```yaml
- key: kleinmarcuschamer2012_cellulase_cost
  value: 10.14
  unit: "USD/kg enzyme (protein)"
  basis: "per kg enzyme protein (paper equates 10 FPU/g cellulose to ~20 mg enzyme/g)"
  year: "2010/2011 USD"
  kind: model_output
  source: "Klein-Marcuschamer D et al. Biotechnol Bioeng 109(4):1083-1087 (2012). doi:10.1002/bit.24370"
  url: "https://ipo.lbl.gov/wp-content/uploads/sites/8/2014/08/2678pub2.pdf"
  locator: "abstract"
  quote: "baseline production cost of enzyme was found to be $10.14/kg"
  read: search-snippet
  note: "Already in repo (kleinmarcuschamer2012). Re-listed only to make clear that Lynd 2017's '$10/kg protein' is this model output, not a price."

- key: zhuang2007_cellulase_unit_costs
  value: null
  low: 15.67
  high: 40.36
  unit: "USD/kg (SSC / SmF)"
  year: "2004 USD"
  kind: model_output
  source: "Zhuang et al. 2007 (see above)"
  url: "https://ageconsearch.umn.edu/record/31982/files/sp040450.pdf"
  locator: "abstract"
  quote: "unit costs of $15.67 per kilogram ($/kg) and $40.36/kg, for the SSC and SmF methods, respectively"
  read: search-snippet
```

## 4. Protein (or TOS) content of commercial enzyme products

```yaml
- key: ctec2_protein_kjeldahl_138
  value: 138
  unit: "mg protein / mL product"
  basis: "Cellic CTec2 (Novozymes), liquid; Kjeldahl N x 6.09, non-protein N subtracted"
  year: "2014 (paper)"
  kind: measurement
  source: "Biotechnol Biofuels 2014, 7:71/72 (PMC4029885), Table 4 'Enzyme nomenclatures, descriptions, protein concentrations, and nitrogen factors'"
  url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC4029885/table/T4"
  locator: "Table 4"
  quote: "| Cellic® CTec2 | Blend of cellulase, high level of β-glucosidase, and hemicellulases | 138 | 6.09 |"
  read: search-snippet
  note: "Same table: Cellic HTec2 157 mg/mL (N factor 6.58); Multifect Pectinase 72 mg/mL. A Frontiers Microbiol 2022 paper (10.3389/fmicb.2022.844287) quotes 'Cellic® CTec2 (138 mg protein/ml, batch number VCNI 0001)' determined by Kjeldahl minus non-protein N."

- key: ctec2_protein_other_reports
  value: null
  low: 138
  high: 257
  unit: "mg protein / mL product"
  basis: "Cellic CTec2, various lots and methods"
  year: "2010s"
  kind: measurement (multiple)
  source: >
    (a) US20150275254A1 patent: 190 mg/mL by total Kjeldahl N after TCA precipitation.
    (b) Another Kjeldahl-based study: 192 mg/mL.
    (c) BioResources paper on oil-palm empty fruit bunches: 237.2 mg/mL (BCA), which cites a 161-257 mg/mL range from earlier reports.
    (d) Bioresour Bioprocess 2017 (s40643-017-0147-7) Table 1: 87.3, 75.8, 46.7 mg/mL for 'Cellic CTec 2.0' samples, method unstated.
  url: "https://patents.google.com/patent/US20150275254 ; https://bioresources.cnr.ncsu.edu/resources/evaluation-of-commercial-cellulase-preparations-for-the-efficient-hydrolysis-of-hydrothermally-pretreated-empty-fruit-bunches/ ; https://bioresourcesbioprocessing.springeropen.com/articles/10.1186/s40643-017-0147-7/tables/1"
  locator: "methods / Table 1"
  quote: "The enzyme protein contents were determined by the total Kjeldahl nitrogen analysis after trichloroacetic acid (TCA) precipitation. ... The protein concentration and FPA of Cellic® CTec2 were measured to be 237.2 mg/mL and 0.54 FPU/mg protein"
  read: search-snippet
  note: "Spread is roughly 2x, depending on lot and assay. The 46-87 mg/mL values may be diluted samples."

- key: ctec2_density
  value: null
  low: 1.0
  high: 1.3
  typical: 1.15
  unit: "g/mL"
  basis: "Sigma-Aldrich SAE0020 (Cellic CTec2 resold), lot-specific"
  kind: specification
  source: "Sigma-Aldrich product page SAE0020; Avantor listing"
  url: "https://www.sigmaaldrich.com/US/en/product/sigma/sae0020"
  locator: "properties / FAQ"
  quote: "The density range is 1.0 - 1.3 g/mL."
  read: search-snippet
  note: "Needed to turn mg/mL into wt% (mg/mL / density / 10). The ~1.15 'typical' figure is the search tool's reading of the page. Alcalase 2.4L: Sigma Q&A gives density 1.17 g/mL at 20 °C but no protein content (url: https://www.sigmaaldrich.com/US/en/product/sigma/p4860)."

- key: efsa_glucoamylase_nzymbf_protein_tos
  value: null
  protein_pct: [8.9, 9.6]
  tos_pct: [11.4, 13.0]
  unit: "% w/w of food enzyme batch"
  basis: "Novozymes glucoamylase from GM A. niger NZYM-BF, liquid concentrate batches intended for commercialisation"
  year: 2018
  kind: measurement (applicant batch data in regulatory opinion)
  source: "EFSA CEP Panel. Safety of the food enzyme glucoamylase from a genetically modified Aspergillus niger (strain NZYM-BF). EFSA Journal 2018;16(10):5450"
  url: "https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2018.5450"
  locator: "Table 1 (composition of food enzyme batches)"
  quote: "The average Total Organic Solids (TOS) content of the three commercial enzyme batches was 11.9%"
  read: search-snippet
  note: "Protein range is the search tool's reading of the batch table; only the TOS sentence is verbatim. Protein/TOS ~0.75-0.8 here."

- key: efsa_glucoamylase_amylase_nzymbx_protein_tos
  value: null
  protein_pct: [8.4, 9.4]
  tos_pct: [11.0, 12.8]
  unit: "% w/w"
  basis: "Novozymes glucan 1,4-α-glucosidase + α-amylase, A. niger NZYM-BX, liquid batches"
  year: 2021
  kind: measurement
  source: "EFSA Journal 2021;19(4):6563"
  url: "https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2021.6563"
  locator: "Table 1"
  quote: "total organic solids (TOS) of the three food enzyme batches for commercialisation are 12.1%"
  read: search-snippet

- key: efsa_xylanase_dpnzd66_protein_tos
  value: null
  protein_pct: [12.3, 10.4, 8.4, 15.7]
  tos_pct: [14.6, 12.1, 10.2, 15.2]
  unit: "% w/w"
  basis: "Genencor/IFF endo-1,4-β-xylanase, T. reesei DP-Nzd66, four batches"
  year: 2026
  kind: measurement
  source: "EFSA Journal 2026;24:10018 (PMC13093323)"
  url: "https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2026.10018"
  locator: "Table 1"
  quote: "(values read by search tool from batch table)"
  read: search-snippet
  quote_status: paraphrase

- key: efsa_xylanase_rf5703_dried_protein_tos
  value: null
  protein_pct: [60, 69]
  tos_avg_pct: 91.4
  unit: "% w/w"
  basis: "AB Enzymes xylanase, T. reesei RF5703; batches are a DRIED (high-solids) food enzyme"
  year: 2020
  kind: measurement
  source: "EFSA Journal 2020;18(1):5974"
  url: "https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2020.5974"
  locator: "Table 1"
  quote: "the average Total Organic Solids (TOS) of the three food enzyme batches for commercialisation was 91.4%"
  read: search-snippet
  note: "Shows that 'per kg product' can mean ~9% protein (liquid) or ~65% protein (dried), a ~7x swing."

- key: efsa_formulation_tos_example
  value: 4.7
  unit: "% w/w TOS"
  basis: "a B. licheniformis food enzyme (strain not identified in snippet)"
  kind: measurement
  source: "EFSA opinion (unidentified in search result)"
  url: "n/a"
  locator: "n/a"
  quote: "average TOS of 4.7% w/w"
  read: search-snippet
  note: "Unattributed; listed only as a lead. EFSA batch data usually describe the unformulated food enzyme concentrate. Sold liquid products can be further diluted with stabilisers (glycerol, sorbitol, salt), so commercial-product protein % may be lower than these figures."
```

## 5. Company-level data

```yaml
- key: novozymes_2022_sales_gross_margin
  value: null
  sales_dkk_m: 17553
  gross_margin_pct: 54.6
  gross_margin_2021_pct: 57.7
  unit: "DKK million; %"
  year: 2022
  money_year: "2022 nominal DKK"
  kind: company financials (reported)
  source: "Novozymes full-year 2022 results announcement (Feb 2023)"
  url: "https://www.novonesis.com/en/news/novozymes-delivers-historically-strong-full-year-results"
  locator: "key figures table"
  quote: "sales was DKK 17,553 million compared to DKK 14,951 million a year ago ... Gross margin % 54.6 57.7 ... Gross margin impacted by higher input, logistics and energy costs, partly offset by productivity improvements and price increases."
  read: search-snippet
  note: "Last full year of a mostly-enzymes company (it also sold microbes and some bioag). A third-party data site gives cost of revenue DKK 7,963 m (not verified). No tonnage disclosed, so a cost per tonne cannot be derived."

- key: novonesis_2025_sales_gross_margin
  value: null
  sales_eur_m_2025: 4157.6
  sales_eur_m_2024: 3833.5
  gm_ifrs_pct_2025: 53.9
  gm_ifrs_pct_2024: 47.2
  gm_adjusted_pct_2025: 59.1
  gm_adjusted_pct_2024: 56.8
  unit: "EUR million; %"
  year: 2025
  kind: company financials (reported)
  source: "Novonesis company announcement 'Novonesis delivered strong organic sales growth of 7% in 2025' (25 Feb 2026)"
  url: "https://www.novonesis.com/en/news/novonesis-delivered-strong-organic-sales-growth-7-2025"
  locator: "headline + financial table"
  quote: "Adjusted gross margin at 59.1% (Q4: 59.9%) up by 240bps ... Net sales 4,157.6 3,833.5 3,945.5"
  read: search-snippet
  note: "From 2024 Novonesis includes Chr. Hansen (cultures, probiotics). It is not an enzymes-only business, and enzymes are not split out by tonnage."

- key: feed_enzyme_alliance_sales_2024
  value: 300
  unit: "EUR million annual net sales (divested activities)"
  year: 2024
  kind: company financials (reported)
  source: "dsm-firmenich press release, 11 Feb 2025: sale of stake in Feed Enzymes Alliance to Novonesis for EUR 1.5 bn"
  url: "https://our-company.dsm-firmenich.com/en/our-company/news/press-releases/2025/dsm-firmenich-to-sell-stake-in-feed-enzymes-alliance-to-its-partner-novonesis-for-1-5-billion.html"
  locator: "press release body"
  quote: "The divested activities represented in 2024 approximately €300 million in total annual net sales."
  read: search-snippet
  note: "No volumes, so a per-kg figure cannot be derived."

- key: company_production_volumes
  value: null
  kind: not_found
  note: "No Novozymes/Novonesis, DSM or IFF document found that states enzyme production tonnage or fermentation capacity in m3. Novozymes sustainability reports give absolute water, energy and CO2 figures, but no product tonnage was found in the snippets."
```

## 6. GFI 2023 "$12-25/kg" quote: primary source located, basis NOT stated

```yaml
- key: gfi2023_novozymes_food_enzyme_quote
  value: null
  low: 12
  high: 25
  unit: "USD/kg (basis not stated)"
  basis: "unknown: product form, protein content and which enzymes are NOT given in the retrieved text"
  year: "quote obtained before Jan 2023"
  kind: price (supplier quote reported by GFI)
  source: "Swartz E, Ravi A (GFI). Anticipated growth factor and recombinant protein costs and volumes necessary for cost-competitive cultivated meat (Jan 2023)"
  url: "https://gfi.org/wp-content/uploads/2023/01/GFI-report_Anticipated-growth-factor-and-recombinant-protein-costs-and-volumes-necessary-for-cost-competitive-cultivated-meat_2023-1.pdf"
  locator: "footnote 8"
  quote: "8 Bulk ordering of common food enzymes at 200-1000kg scales were quoted from Novozymes at costs between $12-25/kg."
  read: search-snippet
  note: "This is the primary source (a footnote in the GFI growth-factor report, used as a comparator for the $10/kg albumin target). Nothing retrieved says whether the $/kg is per kg of formulated product or per kg of protein. Given that it is a bulk commercial quote for 'common food enzymes', per kg of formulated product is the most likely reading, but this is an inference, not stated."
```

## Not found

- Eurostat Comext CN 3507 90 90 EU-extra export unit values: the API was blocked, so the series the repo already uses for casein could not be pulled. This is the best next step.
- US Census / USITC DataWeb unit values for HTS 3507.90: not found via search.
- A product data sheet that states protein % for a named commercial food or feed enzyme (phytase, xylanase granulates): not found. Suppliers state activity (FTU/g, U/g), not protein.
- The Kwiatkowski 2006 corn dry-grind model's enzyme prices: not in the snippets.
- Tufvesson 2011 (OPRD 15:266) enzyme cost per kg: not in the snippets. A 2024 TU Delft paper quotes "crude cell extract = 250 €/kg" as a Tufvesson-style assumption (kind: model assumption), which is unverified.
