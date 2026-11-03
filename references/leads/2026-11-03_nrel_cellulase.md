# Research: real-price anchor for secreted fungal protein (cellulase)

Date: 2026-11-03. Researcher: Claude (subagent).

## Access status (read this first)

I could NOT open any primary full text in this session. The environment's network policy blocks:
- www.nrel.gov, docs.nrel.gov, docs.nlr.gov (NREL's new domain), www.osti.gov,
  web.archive.org, webarchive.library.unt.edu (curl: proxy 403 on CONNECT; WebFetch: host not resolved).
- I stopped trying more hosts after that, as the environment asks. mdpi.com, ipo.lbl.gov,
  Wiley and the ECUST PDF were not tried.
- The local copies listed in references/INDEX.md (reports/NREL_2011_Humbird_TP-5100-47764_...pdf,
  papers/KleinMarcuschamer2012_enzyme_cost_lbl.pdf, papers/Puetz2019_...pdf) are NOT on disk in
  this checkout. They are gitignored and were never committed.

So none of the "quote" fields below is a verbatim quote I checked against a primary PDF. Every entry
says where its text came from: (a) WebSearch result summaries, which are paraphrased by the search
tool and are not verbatim, or (b) earlier pf-tea notes in the repo, which a past session says it read
from the full text. I re-checked neither against the PDF. Nothing here should go into
data/pf/base.yaml until someone with access re-reads the page.

To finish the job, allow www.nrel.gov (or docs.nrel.gov / docs.nlr.gov), mdpi.com and ipo.lbl.gov
in the environment's network settings, or put the three PDFs into references/ again.

## Entries

### 1. NREL 2011 (humbird2011, NREL/TP-5100-47764)

- key: humbird2011_enzyme_cost_per_gal
  value: 0.34
  unit: USD per gallon of ethanol
  basis: enzyme cost contribution to MESP, on-site T. reesei cellulase (Area 400)
  year: 2007 USD
  kind: model estimate (NREL design-case output; not a market price)
  source: Humbird et al. 2011, NREL/TP-5100-47764
  url: https://www.nrel.gov/docs/fy11osti/47764.pdf (blocked here)
  locator: NOT VERIFIED. Repo note data/calibration/nrel2011_cellulase.yaml uses "0.34 $/gal" with the p.41 $4.24/kg
  quote: none verbatim. A WebSearch summary of a secondary paper reads: "lower enzyme cost of 4.24 USD/kg
    (in 2007 dollars), which resulted in a cost contribution of 0.34 USD/gal ethanol at a loading of
    0.02 g enzyme protein/g cellulose" (secondary, paraphrased, unverified)
  note: NREL's 2012 state-of-technology report (docs.nrel.gov/docs/fy14osti/61563.pdf) shows an
    "Enzyme contribution ($/gal ethanol)" row running $0.39 to $0.34 across years (search summary).
    That backs the $0.34 figure.

- key: humbird2011_vs_enzyme_makers_comparison
  value: NOT FOUND
  unit: -
  basis: -
  year: -
  kind: -
  source: Humbird et al. 2011
  url: as above
  locator: not located
  quote: none
  note: I could not verify the passage comparing NREL's cost with Genencor/Novozymes estimates
    ("~$0.50 vs $0.34/gal"). Neither search returned it, and I cannot open the PDF. I do not know whether
    $0.50 is right. Do not use it until someone reads the page. Searches did turn up a 2010 NREL fact sheet
    on the Genencor/Novozymes subcontracts: enzyme cost fell from "$4-$5/gallon" by more than the
    10x goal. That is a different document and a different era.

- key: humbird2011_usd_per_kg_protein
  value: 4.24
  unit: USD per kg enzyme protein
  basis: per kg protein produced, crude whole broth (no downstream processing)
  year: 2007 USD
  kind: model estimate
  source: Humbird et al. 2011
  url: as above
  locator: printed p.41 (repo note; PDF page = printed + 10 per references/INDEX.md)
  quote: repo note only: "works out to $4.24/kg protein" (data/calibration/nrel2011_cellulase.yaml).
    My exact-phrase web search did NOT find this sentence. Liu, Zhang & Bao 2016 do list 4.24 $/kg protein
    as the NREL-derived case (search summary).
  note: probably right (two independent pointers), but the wording and page are unverified.

- key: humbird2011_enzyme_loading
  value: 20 (reported by secondary sources as 0.02 g/g)
  unit: mg enzyme protein per g cellulose
  basis: saccharification loading
  year: -
  kind: design assumption
  source: Humbird et al. 2011 (via secondary sources)
  url: as above
  locator: NOT VERIFIED (no page)
  quote: none verbatim from NREL. Secondary summaries: "0.02 g enzyme protein/g cellulose"; "a baseline of 20 mg/g"
  note: confirm the page in the full text.

- key: humbird2011_ethanol_yield_gal_per_dry_ton
  value: NOT FOUND
  unit: gal per dry US ton
  basis: -
  year: -
  kind: -
  source: Humbird et al. 2011
  url: as above
  locator: -
  quote: none
  note: not found. I know a value from memory but I will not give it unverified.

- key: humbird2011_glucan_content
  value: NOT FOUND
  unit: wt% dry corn stover
  note: not found. Look for the feedstock composition table in the full text.

- key: humbird2011_annual_ethanol
  value: 61.0 (repo note only)
  unit: MM gal/yr
  note: Comes from the repo's own arithmetic (data/calibration/nrel2011_cellulase.yaml delivered_fraction:
    "0.34 $/gal x 61.0 MMgal / 4.24 / 8,410 h = ~580 kg/h"). Not checked against a page. That check
    already ties $0.34/gal to $4.24/kg (about 580 kg/h of protein).

- key: humbird2011_cellulase_design_basis (already in repo, for context)
  value: 50 g/L titer, 0.24 kg enzyme/kg glucose, 300 m3 vessels
  kind: design assumption
  locator: Table 18, printed p.37 (PDF p.47), per data/titers.csv
  quote (repo): "Reactor size 300,000 L @ 80% final working volume Enzyme titer at harvest 50 g/L Mass yield of enzyme from glucose 0.24 kg enzyme/kg glucose"
  note: titers.csv also flags that Appendix C (printed p.106) shows "Protein harvest titer (g/L) 40".

### 2. Other published cellulase cost or price figures

- key: kleinmarcuschamer2012_enzyme_cost
  value: 10.14 (repo note: docs/LITERATURE.md "$10.14/kg enzyme at baseline"); 0.68 and 1.47
  unit: USD per kg enzyme (protein basis per Liu 2016's table) / USD per gallon of ethanol
  basis: $/kg: probably per kg protein, unverified. $/gal: enzyme contribution
  year: money year not verified (the paper is 2012; check its cost-year statement)
  kind: model estimate (LBNL TEA of T. reesei cellulase production)
  source: Klein-Marcuschamer D, Oleskowicz-Popiel P, Simmons BA, Blanch HW. Biotechnol Bioeng 109(4):1083-1087 (2012)
  url: https://doi.org/10.1002/bit.24370 ; author manuscript https://ipo.lbl.gov/wp-content/uploads/sites/8/2014/08/2678pub2.pdf
  locator: not verified
  quote: none verbatim. Abstract (search summary): the cost "was much higher than that commonly assumed in
    the literature". Secondary (Biofuels Digest, summarised): $0.68/gal at maximum theoretical sugar yield,
    $1.47/gal in the less favourable scenario.
  note: my searches did not find $10.14. Liu 2016's price table (search summary) lists 10.14 $/kg protein
    among its cases, which fits a Klein-Marcuschamer origin.

- key: puetz2019_cellulase_price
  value: ~10 (search summary of the table; not verified)
  unit: USD per kg
  basis: unclear (product or protein); check the table
  year: unclear; check
  kind: listed as a price (retail/market-type) in a review table; check the authors' own source for it
  source: Puetz J, Wurm FM. Processes 7(8):476 (2019), CC BY
  url: https://doi.org/10.3390/pr7080476 ; https://www.mdpi.com/2227-9717/7/8/476
  locator: price table (number not verified)
  quote: abstract (search summary, near-verbatim): industrial proteins "often have a retail price in the
    tens of dollars per kilogram". Cellulase row: not verified.
  note: GFI 2023 footnote (already in data/evidence/albumin.yaml, quoted there) cites it as "Lowest price
    found for a recombinant protein - cellulase (Puetz and Wurm 2019)". The same GFI page has "Bulk ordering
    of common food enzymes at 200-1000kg scales were quoted from Novozymes at costs between $12-25/kg"
    (GFI 2023 p.14; a company quote passed on second-hand, food enzymes in general, not cellulase).

- key: liu2016_cellulase_cost_cases
  value: 1.25, 5.07, 6.27, 10.14, 23.30, 4.24 (search summary of a table)
  unit: USD per kg protein
  basis: per kg protein
  year: not verified
  kind: compilation of other sources' estimates/prices used as cases, plus their own on-site model
  source: Liu G, Zhang J, Bao J. Cost evaluation of cellulase enzyme for industrial-scale cellulosic ethanol production based on rigorous Aspen Plus modeling. Bioprocess Biosyst Eng 39(1):133-140 (2016)
  url: https://doi.org/10.1007/s00449-015-1497-1 ; author PDF on sklbe.ecust.edu.cn (see summary links)
  locator: price table (number not verified)
  quote: none verbatim. Search summary: the enzyme cost range for bioethanol is "0.10 $ to 1.47$ per gallon
    of ethanol", and NREL's $0.34/gal is "relatively low compared with other reports".
  note: the best place to get every case with its origin in one table. Get the full text.

## Confidence

- $0.34/gal and $4.24/kg protein (2007$, NREL model estimates): medium-high. Repo notes, a secondary
  paper and NREL's 2012 SOT report agree. Page and wording are not re-verified.
- Genencor/Novozymes comparison ("$0.50"): not verified, unknown.
- Loading 20 mg/g: medium (secondary sources only).
- Ethanol yield per dry ton and glucan content: not found.
- Klein-Marcuschamer $10.14/kg, Puetz ~$10/kg, Liu 2016 table: low to medium (search summaries and repo
  notes only).
- No actual market price for cellulase per kg protein turned up. Puetz's figure is the only candidate for
  a "price", and its own source and basis need checking.
