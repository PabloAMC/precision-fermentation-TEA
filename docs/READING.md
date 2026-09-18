# Reading list, in order

Aim: learn just enough bioprocess accounting to build and defend the model.
About 15 hours. Skip anything marked optional on a first pass.

## 1. Method templates (read fully)
- Humbird 2021, Scale-up economics for cultured meat. You know it. Reread only
  the Supplementary Information: it is the accounting template (equipment list,
  scaling exponents, installation factors, labour, depreciation).
- Voutilainen, Pihlajaniemi & Parviainen 2021, Bioresource Technology Reports,
  economic comparison of food protein production with single-cell organisms.
  This is the $11.2/kg recombinant-protein model. Your first validation target.
  Extract every input into a table.
- Intelligen (SuperPro Designer) white papers on lactoferrin and collagen
  peptide production (Da Gama Ferreira et al. 2024a, 2024b). Free PDFs. They
  show a full DSP train with per-step recoveries. Second validation target.

## 2. The benchmark you are filling (read fully)
- GFI 2025, Driving down costs (doi 10.62468/trxj5734). Section 1.3 and
  Table 2 give the private-sector titer and volume ranges. Section 2.4 gives a
  worked sensitivity analysis to copy.
- Eastham & Leman 2024 (GFI), fermentation titer benchmarks. Cited in the
  above; find it for titer priors.

## 3. Cost estimation basics (skim, then use as reference)
- Towler & Sinnott, Chemical Engineering Design, chapter on capital cost
  estimation. Cost curves, six-tenths rule, Lang factors. ~20 pages.
- Humbird et al. 2011, NREL cellulosic ethanol design report. The gold standard
  for a transparent TEA. Read the executive summary and the costing appendix.
  Optional but formative.

## 4. Bioprocess sizing (reference only)
- Doran, Bioprocess Engineering Principles, chapters on oxygen transfer (kLa)
  and reactor scale-up. You need one equation: OTR = kLa*(C* - C).
- Any review of Komagataella phaffii (Pichia) fed-batch protein production for
  typical batch times, cell densities and secretion.

## 5. Product-specific data (search, do not read cover to cover)
- Papers on recombinant beta-lactoglobulin expression in Pichia and
  Trichoderma. Record titer, host, purity.
- Papers on recombinant ovalbumin in Pichia. Same.
- Patents from Perfect Day, Remilk, The EVERY Company. Titers appear in
  examples. Treat as upper bounds, not typical values.

## 6. Tools
- BioSTEAM paper (Cortes-Peña et al. 2020, ACS Sust. Chem. Eng.) and docs.
  Use its cost correlations to cross-check yours. Do not build on it.

## Skip on a first pass
- Metabolic modelling, strain engineering, glycosylation biochemistry.
- LCA literature.
- Cultivated-meat media literature; different cost structure.
