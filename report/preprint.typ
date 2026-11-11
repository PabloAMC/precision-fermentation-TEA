// Short preprint: the core of the full report (report/pf_tea_report.typ) for reviewers and databases.
// Compile from the repo root:  typst compile --root . report/preprint.typ
// Every number is read from results/analyses.json (report/common.typ); none is typed here except
// numbers quoted from sources, which carry their citation.
#import "common.typ": *

#let O(p) = R.options.at(p)
#let PC = R.plant_cost_check
#let YE = R.calibration.bakers_yeast

#set document(title: "What precision-fermented food proteins cost: an open model", author: "Pablo Antonio Moreno Casares")
#set page(paper: "a4", margin: (x: 2.3cm, y: 2.3cm), numbering: "1")
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10.5pt, lang: "en")
#set par(justify: true, leading: 0.62em, spacing: 1.0em)
#set heading(numbering: "1.")
#show heading.where(level: 1): it => { v(0.5em); text(size: 12.5pt, it); v(0.15em) }
#show figure.caption: set text(size: 9pt)
#set table(stroke: none, inset: (x: 5pt, y: 3.2pt))
#show table: set text(size: 8.8pt)
#let hline = table.hline(stroke: 0.5pt + rgb("#c3c2b7"))
#let note(body) = block(fill: rgb("#f3f2ec"), inset: 9pt, radius: 3pt, width: 100%, text(size: 9pt, body))

#align(center)[
  #text(size: 16pt, weight: "bold")[What precision-fermented food proteins cost: an open model]
  #v(0.2em)
  #text(size: 11pt)[Seven proteins on an equal footing, with every input sourced]
  #v(0.5em)
  Pablo Antonio Moreno Casares
  #v(0.1em)
  #text(size: 9pt, fill: rgb("#52514e"))[Preprint draft · numbers generated #R.generated · code and data: repository `precision-fermentation-tea` · full report: `report/pf_tea_report.pdf`]
]

#v(0.4em)
#note[
  *Views.* The views expressed are purely those of the author and may not in any circumstances be regarded as stating an official position of the European Commission.

  *Status.* No human expert has reviewed this work yet. The author built the model and this text with
  an AI assistant (Claude, Anthropic), and independent AI reviewers audited it over 17 rounds
  (`docs/AUDIT.md`). The model computes every number here; the full report gives the methods in detail.
]

#heading(level: 1, numbering: none)[Summary]

Precision fermentation (PF) uses an engineered microbe to make one animal protein and release (secrete)
it into the liquid it grows in, the broth. We estimate what seven food proteins cost to make this way,
from public data only, and what it would take to match the prices of the proteins they replace.

*Terms.* _Titer_: grams of protein per litre of broth at harvest. _Secretion rate_: mg of protein that each
gram of cells secretes per hour (mg/g/h). _Capital charge_: the yearly payment that repays the plant's
investment over #pv("finance.ccf_life_y") years at #pct(pv("finance.ccf_rate"), d: 1) interest,
#pct(CRF, d: 1) of the investment a year. _Minimum selling price_: the cost per kg including the capital
charge, before any profit margin, sales or transport; a cost, not a market price.

*Method.* We follow Humbird's (2021) cost model for cultivated meat and add a secreted product and its
purification. The model balances every element and electron, checks that the fermenter can supply the
oxygen and remove the heat, and prices capital with Humbird's factors. With them, his baker's-yeast
model reproduces that product's market-implied cost (#usd(YE.cop, d: 2) against #usd(YE.market_implied, d: 2)
per kg), and ours lands within #sgn(calrel("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)"))
of a published PF design (Intelligen 2025). Every input has a source and a stated kind of evidence.

*Results.* At the design titer of published PF plants (30 g/L; lactoferrin 10 g/L), the minimum
selling price is *#plist(p => R.base.at(p).msp_ccf)* per kg of protein. The commodity proteins (whey, egg
white, casein) then sit at or above the top of their market prices. They reach the middle of those prices
only at the industry benchmark, the 42 g/L that companies' own cost models assume. Two scarce milk proteins are already competitive: lactoferrin costs #money(lfb.msp_ccf)/kg
against #money(MKT("lf").at(0))–#money(MKT("lf").at(1)) for the dairy product, and α-lactalbumin sits inside its
price range. Serum albumin for cultivated-meat media does not: its purification columns cost too much.

*What it would take.* Glucose is about a fifth of the price and the plant over half, and the plant's cost
per kg is set by how fast the cells secrete (box below). So the gap lies in the strain, not the sugar:
cheap commodity protein needs cells that secrete several times faster than the best published strains. If secretion falls as growth slows, as the published data suggest, a strain at the
best measured rate makes β-lactoglobulin at about #money(O("blg").demonstrated.msp_ccf)/kg.

#note[#core-relation]

= Method in eight steps

The model is a chain; each step hands its result to the next. Full equations are in the code's
docstrings (`src/pftea/`) and in the full report.

+ *Reaction.* Element and electron balances give the glucose, ammonia and oxygen of growth, maintenance
  and protein formation. Protein formulas come from their amino-acid sequences.
+ *Sugar and oxygen.* Growth, maintenance and product share the substrate (Pirt equation; Heijnen and
  Tijhuis correlations, as Humbird).
+ *One batch.* A two-phase fed-batch: cells grow at up to 0.2 per hour, then secrete the protein for a
  set time while barely growing.
+ *Limits.* Oxygen transfer is capped at 200 mol per m³ of liquid per hour and heat removal at 25 kW
  per m³; a batch must start at least 30% full. A design that breaks a limit is never priced.
+ *Purification.* Centrifuges, membranes and a spray dryer; chromatography columns for lactoferrin and
  albumin; acid precipitation for casein.
+ *Scale.* Batches per year set the number of fermenters (200 m³ for the base plant); utilities are
  sized on the plant's combined peak.
+ *Capital.* Equipment prices times Humbird's factors for a food-grade plant give the investment.
+ *Money.* Running costs, fixed costs (9% of investment a year) and a capital charge (7.5% over 10
  years) give the minimum selling price.

= Results

#let pair(h, l) = if h == none [—] else [#money(h.msp_ccf)#if l != none [ (#money(l.msp_ccf))]]
#figure(
  table(
    columns: (2.1fr,) + PRODS.map(_ => 1fr),
    align: (left,) + PRODS.map(_ => right),
    table.header([*\$/kg protein*], ..PRODS.map(p => [*#NAME.at(p)*])),
    hline,
    [Best published strain], ..PRODS.map(p => [#money(S("academic/" + p).msp_ccf)]),
    [Base case: design titer], ..PRODS.map(p => pair(R.base.at(p), R.base_light.at(p))),
    [Industry benchmark (42 g/L)], ..PRODS.map(p => pair(S("industry/" + p), S("industry/" + p + "/light"))),
    [Physical-limit best case], ..PRODS.map(p => [#money(PL(p + "/humbird").msp_ccf)]),
    hline,
    [Market price], ..PRODS.map(p => [#money(MKT(p).at(0))–#money(MKT(p).at(1))]),
    [Plant output, t/yr], ..PRODS.map(p => [#thou(tpy(R.base.at(p)))]),
  ),
  caption: [Minimum selling price, 2025 dollars, US Midwest; in brackets with design-report capital
  (NREL-style: lighter installation factors and fixed costs under 2% a year). Market prices: trade values 2015–2025 for whey, dried egg white and
  casein; reported prices for lactoferrin, bulk serum albumin and α-lactalbumin (company or survey
  figures). The best case assumes secretion at 40 mg per g of cells per hour, far above any published
  strain.],
) <tab-key>

#figure(image("../docs/figures/fig10_price_ladder.png", width: 100%),
  caption: [Every case against its market, one panel per protein. Model figures are minimum selling
  prices: costs including the capital charge, so not market prices.]) <fig-ladder>

Three findings stand out.

- *Scarce proteins pay; commodity proteins do not yet.* Lactoferrin comes out below its market price and
  α-lactalbumin inside its price range, on modest plants. Whey, egg-white and casein proteins need titers near
  42 g/L to reach the middle of their price bands.
- *The plant, not sugar, sets the price.* For β-lactoglobulin, glucose is
  #pct(blg.per_kg.glucose / blg.msp_ccf) of the cost; the capital charge, maintenance and insurance
  together are #pct(capshare(blg)). Halving the glucose price saves about
  #usd(blg.per_kg.glucose / 2)/kg.
- *The fermenter caps the titer.* Sugar arrives dissolved, so every gram of protein brings feed liquid
  with it, and a batch can end at most 80% full; a higher titer needs a batch that starts emptier. With a
  500 g/L glucose feed and a start at least 30% full, a 200 m³ vessel reaches about #fx(CEIL72, d: 0) g/L
  in a 72-hour production phase.

= What would change the answer

*Secretion rate.* At the base cell density, \$20/kg β-lactoglobulin needs cells to secrete
#fx(req("blg/humbird", 20, tpi(72)).q_p_mg_g_h, d: 0)–#fx(req("blg/humbird", 20, tpi(48)).q_p_mg_g_h, d: 0)
mg per g of cells per hour; the base design assumes #fx(blg.design.q_p_mg_g_h, d: 1). With today's
biology and capital, the best design costs #usd(BD(10).msp_ccf)/kg at 10 mg/g/h and #usd(BD(40).msp_ccf)
at 40. The best published glucose fed-batch reaches 2.1 (Prielhofer et al. 2018).

*Secretion that needs growth.* Published *K. phaffii* data show secretion rising with growth and
falling as growth stops (Maurer et al. 2006; Rebnegger et al. 2014, 2024). The base case, like
Intelligen's design, assumes steady secretion without growth. An optional model switches this on, with
a large-tank yield loss and a continuous mode; all are off in the base:

#figure(
  table(
    columns: (2.6fr,) + PRODS.map(_ => 1fr),
    align: (left,) + PRODS.map(_ => right),
    table.header([*\$/kg protein*], ..PRODS.map(p => [*#NAME.at(p)*])),
    hline,
    [Base case], ..PRODS.map(p => [#money(O(p).base.msp_ccf)]),
    [Large-tank yield loss of 6.5% (George et al. 1998)], ..PRODS.map(p => [#money(O(p).yield_loss.at("0.065").msp_ccf)]),
    [Secretion tied to growth, base titer], ..PRODS.map(p => [#money(O(p).coupled_titer.msp_ccf)]),
    [#h(1em)secretion the strain then needs at 0.1/h, mg/g/h], ..PRODS.map(p => [#fx(O(p).coupled_titer.design.q_ref_mg_g_h, d: 0)]),
    [Best measured secretion (2.1 mg/g/h), best fed-batch design], ..PRODS.map(p => [#money(O(p).demonstrated.msp_ccf)]),
    [#h(1em)titer it reaches, g/L], ..PRODS.map(p => [#fx(O(p).demonstrated.design.titer, d: 1)]),
    [Same strain, best continuous design], ..PRODS.map(p => [#money(O(p).continuous.msp_ccf)]),
  ),
  caption: [The model's optional physics (`data/pf/scenarios/detailed.yaml`). Secretion tied to growth
  follows Maurer et al.'s (2006) saturating curve with a floor from Rebnegger et al. (2024); both come
  from single strains, so these rows are sensitivities, not a new base case.],
) <tab-options>

Tied to growth, the base titer needs a strain that secretes about
#fx(O("blg").coupled_titer.design.q_ref_mg_g_h, d: 0) mg/g/h at a growth rate of 0.1 per hour, about
#fx(O("blg").coupled_titer.design.q_ref_mg_g_h / 2.1, d: 0) times the best measured. With the best
measured strain the titer falls to about #fx(O("blg").demonstrated.design.titer, d: 0) g/L, and the price
rises several-fold for every protein except lactoferrin, which stays inside its market band.

*Accounting.* Humbird's fixed costs (9% of investment a year) are heavy. NREL-style design reports
charge under 2%; with design-report capital the base β-lactoglobulin costs #money(R.base_light.blg.msp_ccf)/kg.
Aseptic, pharmaceutical-grade vessels would raise it to #money(R.base_aseptic.blg.msp_ccf).

= How we checked it

#figure(
  table(
    columns: (2.6fr, 1fr, 1fr),
    align: (left, right, right),
    table.header([*Check*], [*pf-tea*], [*Published*]),
    hline,
    [Baker's yeast, cost per kg (Humbird's workbook; market price less a 33% margin)], [#usd(YE.cop, d: 2)], [#usd(YE.market_implied, d: 2)],
    [Intelligen 2025 ovalbumin, \$ per kg powder], [#usd(cal("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)").at(0))],
      [#usd(cal("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)").at(1))],
    [NREL 2011 cellulase, \$ per kg protein], [#usd(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)").at(0), d: 2)],
      [#usd(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)").at(1), d: 2)],
    [Voutilainen 2021 ovalbumin, € per t protein], [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF)").at(0))],
      [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF)").at(1))],
    [Capital per m³ of fermenter, \$ (Liberation Labs, scaled to our plant)], [#thou(PC.model_per_m3)],
      [#thou(PC.ll_scaled_per_m3.at("0.5"))–#thou(PC.ll_scaled_per_m3.at("0.7"))],
  ),
  caption: [Each published design is rebuilt from its own inputs. Mass balances match well; costs
  differ mostly through accounting (NREL and Voutilainen charge far lighter fixed costs). The real-plant
  check scales Liberation Labs' disclosed \$115M for 600 m³ (company figure) to our 7,200 m³ with cost
  exponents of 0.5–0.7 (`docs/VALIDATION.md`).],
) <tab-checks>

= Limits

- The price is a minimum selling price for a mature plant: a cost including the capital charge. It leaves out R&D,
  licensing, regulatory approval, sales, start-up, failed batches and the extra cost of a first plant.
- Strain performance rests on design values and company-reported averages; few strain parameters are
  measured. Casein and lactoferrin titers are borrowed from other proteins or species.
- Secretion is held constant during production in the base case; the optional model above shows how
  much that matters.
- Protein modifications (phosphorylation, glycosylation) are not costed.
- No human expert has reviewed the model yet.

= Data and code

All code, data, results and the full report are in the `pf-tea` repository. Inputs, with sources and
quotes, are in `data/`; every result is regenerated by `scripts/run_analyses.py`; the tests check the
mass balances and the published-design checks. Code: MIT licence. Data and text: CC BY 4.0.

#heading(level: 1, numbering: none)[References]
#set text(size: 9pt)
- George S, Larsson G, Olsson K, Enfors S-O (1998). Comparison of the baker's yeast process performance in laboratory and production scale. Bioprocess Eng 18:135–142.
- Humbird D (2021). Scale-up economics for cultured meat. Biotechnol Bioeng 118:3239–3250.
- Humbird D, Davis R, Tao L, et al. (2011). Process design and economics for biochemical conversion of lignocellulosic biomass to ethanol. NREL/TP-5100-47764.
- Intelligen: Da Gama Ferreira R, Misailidis N, Parisis V, Petrides D (2025). Egg white protein (ovalbumin) production via precision fermentation: techno-economic assessment using SuperPro Designer.
- Maurer M, Kühleitner M, Gasser B, Mattanovich D (2006). Versatile modeling and optimization of fed batch processes for the production of secreted heterologous proteins with Pichia pastoris. Microb Cell Fact 5:37.
- Prielhofer R, et al. (2018). Superior protein titers in half the fermentation time: promoter and process engineering for the glucose-regulated GTH1 promoter of Pichia pastoris. Biotechnol Bioeng 115:2479–2488.
- Rebnegger C, et al. (2014). In Pichia pastoris, growth rate regulates protein synthesis and secretion, mating and stress response. Biotechnol J 9:511–525.
- Rebnegger C, et al. (2024). Microb Cell Fact 23:44, doi:10.1186/s12934-024-02314-3 (chemostat and retentostat secretion data).
- Voutilainen E, Pihlajaniemi V, Parviainen T (2021). Economic comparison of food protein production with single-cell organisms from lignocellulose side-streams. Bioresour Technol Rep 14:100683.
- GFI and Hawkwood Biotech (2025). Driving down costs of fermentation-derived ingredients.
