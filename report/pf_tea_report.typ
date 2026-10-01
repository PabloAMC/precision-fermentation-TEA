// The cost of precision-fermented whey and egg proteins: techno-economic analysis, v2 (audited).
// Compile from the repo root:  typst compile --root . report/pf_tea_report.typ
// Every number is read at compile time from results/analyses.json (scripts/run_analyses.py)
// or from the data files. Nothing numeric is typed into this document except fixed definitions
// and numbers quoted from sources, which carry their citation.

#let R = json("../results/analyses.json")
#let P = yaml("../data/pf/base.yaml")

// ---------------------------------------------------------------- formatting helpers
#let fx(x, d: 1) = {
  let r = calc.round(x, digits: d)
  let s = str(r)
  if d > 0 {
    if not s.contains(".") { s = s + "." + "0" * d } else {
      let k = s.split(".").at(1).len()
      if k < d { s = s + "0" * (d - k) }
    }
  }
  s
}
#let thou(n) = {
  let s = str(int(calc.round(n)))
  let out = ""
  let L = s.len()
  for (i, c) in s.clusters().enumerate() {
    if i > 0 and calc.rem(L - i, 3) == 0 { out += "," }
    out += c
  }
  out
}
#let usd(x, d: 1) = if x == none { "n/a" } else { "$" + fx(x, d: d) }
#let usd0(x) = if x == none { "n/a" } else { "$" + thou(x) }
#let musd(x) = "$" + thou(x / 1e6) + "M"
#let pct(x, d: 0) = fx(100 * x, d: d) + "%"
#let sgn(x, d: 0) = (if x >= 0 { "+" } else { "−" }) + fx(calc.abs(100 * x), d: d) + "%"
#let dusd(x, d: 1) = (if x >= 0 { "+$" } else { "−$" }) + fx(calc.abs(x), d: d)
#let where(x, band) = {
  let (lo, hi) = (band.at(0), band.at(1))
  if x < lo * 0.95 { "below" } else if x < lo * 1.05 { "at the bottom edge of" }
  else if x <= hi * 0.95 { "inside" } else if x <= hi * 1.05 { "at the top edge of" } else { "above" }
}
#let POL = R.policy
#let TT = csv("../data/titers.csv", row-type: dictionary)
#let n_unverified = TT.filter(r => r.verified == "no").len()
#let S(k) = R.scenarios.at(k)
#let PL(k) = R.physical_limit.at(k)
#let MC(k) = R.monte_carlo.at(k)
#let lab(path) = R.labels.at(path, default: path.split(".").last())
#let cal(name, key) = R.calibration.at(name).at(key)
#let calrel(name, key) = { let v = cal(name, key); v.at(0) / v.at(1) - 1 }
#let inc = R.benchmarks.incumbents
#let pv(path) = {
  // base.yaml value (location-keyed leaves: US value)
  let node = P
  for k in path.split(".") { node = node.at(k) }
  if "value" in node { node.value } else { node.us_midwest }
}
#let pveu(path) = { let node = P; for k in path.split(".") { node = node.at(k) }; node.eu_nw }
#let is-leaf(x) = type(x) == dictionary and ("value" in x or "us_midwest" in x or "grade" in x)
#let flat(d, pre) = {
  let out = ()
  for (k, x) in d {
    if type(x) == dictionary {
      if is-leaf(x) { out.push((pre + k, x)) } else { out += flat(x, pre + k + ".") }
    }
  }
  out
}
#let blg = R.base.blg
#let ova = R.base.ova
#let req(key, tg, i) = R.required.at(key).at(str(tg)).at(i)
#let tpi(t) = R.required_t_prods.position(x => x == t)
#let tor(path) = R.tornado.find(t => t.path == path)
#let torrank(path) = R.tornado.position(t => t.path == path) + 1
#let swing(path) = { let t = tor(path); calc.abs(t.msp_high - t.msp_low) }
#let capshare(d) = (d.per_kg.at("capital charge") + d.per_kg.maintenance + d.per_kg.at("insurance")) / d.msp_ccf
#let LF = R.lactoferrin
#let LFC(k) = ((
  // lactoferrin cases: base and academic runs sit with BLG and OVA's; route variants in R.lactoferrin
  "lf/humbird": R.base.lf, "lf/light": R.base_light.lf,
  "lf_academic/humbird": R.scenarios.at("academic/lf"), "lf_academic/light": R.scenarios.at("academic/lf/light"),
) + LF.cases).at(k)
#let REC(k) = LF.reconciliation.at(k)
#let IA = LF.reported_prices.comparators.find(c => c.key == "lf_cost_intelligen2026_case_a_ufdf")
#let IB = LF.reported_prices.comparators.find(c => c.key == "lf_cost_intelligen2026_case_b_cex")
// Intelligen's operating-cost category per kg lactoferrin, 2025 dollars
#let ipk(c, k) = c.values.at(k) / (c.values.powder_kg_per_yr * c.values.lf_frac_powder) * c.deflator
#let EQ = R.equivalents
#let CEIL72 = R.titer_ceiling.blg.at(tpi(72))
#let K = R.constants
#let ratio(name, key) = { let v = cal(name, key); v.at(0) / v.at(1) }
// a range of two numbers, or one number when both ends round alike
#let rng(a, b, d: 1) = if fx(a, d: d) == fx(b, d: d) { fx(a, d: d) } else { fx(a, d: d) + "–" + fx(b, d: d) }
#let pubratio = { let r = (ratio("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)"),
  ratio("voutilainen2021_case", "EUR_per_t_protein (their DCF)")); rng(calc.min(..r), calc.max(..r)) }
#let CL(case, t) = R.ceiling_limits.at(case).find(r => r.t_prod == t)
#let wheyobs = inc.whey.series.values().map(s => s.values()).flatten()
#let BS = R.base_sensitivities
#let BD(q) = R.best_design_base.at(str(q), default: none)
#let QP(q) = R.physical_limit.at("blg/humbird/q_p_max_" + str(q), default: none)
#let conv = R.convention_steps
#let STK = R.calibration.bakers_yeast_stacks
#let CEIL600 = R.titer_ceiling_feed600.blg.at(tpi(72))
#let AER21 = yaml("../data/evidence/engineering.yaml").find(e => e.key == "aeration_power_humbird2021_fig13_200m3").value

// ---------------------------------------------------------------- document style
#set document(title: "The cost of precision-fermented whey and egg proteins", author: "Pablo Antonio Moreno Casares")
#set page(paper: "a4", margin: (x: 2.3cm, y: 2.4cm), numbering: "1",
  header: context { if counter(page).get().first() > 1 [
    #set text(size: 8pt, fill: rgb("#898781"))
    Precision-fermented BLG and OVA: techno-economic analysis #h(1fr) v2.1 (audited, AI pre-reviewed), #R.generated
  ] })
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10.5pt, lang: "en")
#set par(justify: true, leading: 0.62em, spacing: 1.1em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => { v(0.6em); text(size: 13pt, it); v(0.2em) }
#show heading.where(level: 2): it => { v(0.3em); text(size: 11pt, it) }
#show figure.caption: set text(size: 9pt)
#show figure: set block(breakable: false)
#set table(stroke: none, inset: (x: 5pt, y: 3.5pt))
#show table: set text(size: 8.8pt)
#let hline = table.hline(stroke: 0.5pt + rgb("#c3c2b7"))
#let note(body) = block(fill: rgb("#f3f2ec"), inset: 9pt, radius: 3pt, width: 100%, text(size: 9pt, body))
#let check(body) = block(stroke: (left: 2pt + rgb("#eb6834")), inset: (left: 9pt, y: 5pt), width: 100%,
  text(size: 9pt)[*Check (reader):* #body])

// ---------------------------------------------------------------- title
#align(center)[
  #text(size: 17pt, weight: "bold")[The cost of precision-fermented whey and egg proteins]
  #v(0.2em)
  #text(size: 12pt)[A Humbird-style techno-economic analysis of β-lactoglobulin and ovalbumin, \
  from stoichiometry to the physical limit, with a lactoferrin contrast case]
  #v(0.6em)
  Pablo Antonio Moreno Casares
  #v(0.1em)
  #text(size: 9pt, fill: rgb("#52514e"))[Version 2.1 (audited; AI pre-reviewed) for human review · numbers generated #R.generated · repository `pf-tea`]
]

#v(0.6em)
#note[
  *Status.* Not yet peer-reviewed. The model code, the evidence extraction and this text were
  produced with an AI assistant (Claude, Anthropic) under the author's direction. Version 1 was
  audited by eight independent AI reviewers, each owning one area and required to support every
  finding with a computation, quote or code line; version 2 was then read by four simulated expert
  reviewers (a fermentation scientist, a bioprocess engineer, a sceptic and the method's author's
  perspective), also AI. Every finding, decision and effect is logged in `docs/AUDIT.md` and
  `docs/REVIEW.md`, and this version implements them. No human expert has reviewed the analysis yet.
  Every number is computed by the model and read from `results/analyses.json` at compile time;
  every input traces to a source and an evidence grade in `data/` (Appendix A). Inputs graded E are
  guesses; they are listed in @sec-limits.
]

// ---------------------------------------------------------------- abstract
#heading(level: 1, numbering: none)[Summary]

Precision fermentation (PF) uses an engineered microbe to secrete a single animal protein. We
estimate what food-grade β-lactoglobulin (BLG, the main whey protein) and ovalbumin (OVA, the main
egg-white protein) cost to make, and what performance would bring them to the price of the
proteins they replace. The method is Humbird's (2021): element- and electron-balanced black-box
stoichiometry, an oxygen-transfer-limited fed-batch fermenter, and his capital factors and fixed
costs, with which his baker's-yeast workbook lands on that product's market-implied cost. We add a
secreted product, a downstream train and a cation-exchange step, and check the model against three
published designs.

The base case is a secreting *Komagataella phaffii* strain at 30 g/L after a 72 h production phase,
the design point of Intelligen's (2025) OVA process, in 200 m³ industrial fermenters making 10 kt/yr
of protein in the US Midwest (2025 dollars). With a capital charge of 14.6% of investment per year
its minimum selling price is *#usd(blg.msp_ccf)/kg BLG* and *#usd(ova.msp_ccf)/kg OVA*. With the
lighter accounting of NREL-style design reports it is #usd(R.base_light.blg.msp_ccf) and
#usd(R.base_light.ova.msp_ccf)\; with the aseptic, cell-culture-grade fermenters that version 2 priced,
#usd(R.base_aseptic.blg.msp_ccf) and #usd(R.base_aseptic.ova.msp_ccf). At the average titer that
private companies' cost models assume (42 g/L, GFI 2025) BLG costs #usd(S("industry/blg").msp_ccf)/kg.
At the best public titers it costs #usd0(S("academic/blg").msp_ccf)/kg BLG
(#fx(S("academic/blg").design.titer, d: 1) g/L, with an ethanol-fed production phase that the model
prices as glucose) and #usd0(S("academic/ova").msp_ccf)/kg OVA (#fx(S("academic/ova").design.titer, d: 0) g/L,
partly clipped). Whey protein traded at #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0)
per kg protein in 2015–2025 (export unit values in 2025 dollars) and dried egg white at
#usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0).

Five results stand out:
1. *Cheap protein needs fast secretion more than high titer.* At the base cell density, \$20/kg BLG
   needs #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0)–#fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L
   in 48–72 h, a specific productivity of #fx(req("blg/humbird", 20, tpi(72)).q_p_mg_g_h, d: 0)–#fx(req("blg/humbird", 20, tpi(48)).q_p_mg_g_h, d: 0)
   mg protein per g cells per hour against #fx(blg.design.q_p_mg_g_h, d: 1) in the base design. With
   today's biology and capital, the cheapest design the model finds costs
   #usd(BD(40).msp_ccf)/kg if cells could secrete #fx(BD(40).design.q_p_mg_g_h, d: 0) mg/g/h (the ceiling we allow),
   and #usd(BD(10).msp_ccf) at 10 mg/g/h. No published *K. phaffii* process is near either rate. At the
   best rate demonstrated in a public glucose fed-batch, 2.1 mg/g/h (Prielhofer et al. 2018), the
   cheapest design costs #usd(BD(2.1).msp_ccf)/kg, and even the best case of point 3
   #usd(QP(2.1).msp_ccf)/kg, #where(QP(2.1).msp_ccf, inc.whey.band) the whey price band.
2. *The titer ceiling is a design ceiling.* With Intelligen's 500 g/L glucose feed and a batch that
   must start at least 30% full, a 200 m³ fermenter at 107 g/L cells reaches about
   #fx(CEIL72, d: 0) g/L in a 72 h production phase; with a 600 g/L feed, about #fx(CEIL600, d: 0) g/L.
3. *A best case, not a floor.* With every assumed limit at its best at once, 400 m³ vessels and
   100 kt/yr, BLG costs #usd(PL("blg/humbird").msp_ccf)/kg and OVA #usd(PL("ova/humbird").msp_ccf)/kg
   (#usd(PL("blg/light").msp_ccf) and #usd(PL("ova/light").msp_ccf) with design-report accounting). That
   assumes secretion at #fx(PL("blg/humbird").design.q_p_mg_g_h, d: 0) mg/g/h; at 10 mg/g/h the BLG
   case costs #usd(QP(10).msp_ccf), at 5 mg/g/h #usd(QP(5).msp_ccf).
4. *Capital: the vessel price and the fixed-cost rule.* Aseptic cell-culture vessels instead of
   industrial ones would add #usd(R.base_aseptic.blg.msp_ccf - blg.msp_ccf)/kg to the base; the lighter
   design-report accounting would remove #usd(blg.msp_ccf - R.base_light.blg.msp_ccf), mostly through
   fixed costs of under 2% of investment a year instead of Humbird's 9%. Published NREL-style designs
   come out #pubratio×
   cheaper than our model of the same process, for those reasons; Intelligen's food-PF design comes
   out within #sgn(calrel("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)")) of ours.
5. *A high-value contrast.* At a design titer of 10 g/L, PF lactoferrin costs
   #usd0(LFC("lf/light").msp_ccf)–#usd0(LFC("lf/humbird").msp_ccf)/kg, #where(LFC("lf/humbird").msp_ccf, LF.reported_prices.band)
   the reported range for dairy lactoferrin (#usd0(LF.reported_prices.band.at(0))–#usd0(LF.reported_prices.band.at(1))/kg in
   2025 dollars). Intelligen's own model of the same route costs
   #fx(IB.value_money_year / REC("lf").cop, d: 1)× ours to produce, mostly through its unit prices
   (@tab-lf-rec). For high-value proteins PF can compete on cost if that titer is reached; the
   commodity proteins are the hard case.

The least-tested assumption is secretion without growth. The production phase follows Intelligen's
design, whose cells secrete #fx(blg.design.q_p_mg_g_h, d: 1) mg/g/h while barely growing. In the one
near-zero-growth study we found (a *K. phaffii* strain secreting an antibody fragment), secretion fell
as growth slowed and settled about five times below the trend at faster growth (Rebnegger et al.
2024, who link part of the fall to the promoter used). Across the literature *K. phaffii* secretes
fastest while growing: a review compiles maximal rates of 0.004–0.69 mg/g/h, those on glucose peaking
at growth rates of 0.15–0.20/h (Looser et al. 2015), and the best glucose fed-batch we found reached
2.1 mg/g/h near 0.1/h (Prielhofer et al. 2018). Growing while producing does not rescue the design:
at that strain's ratio, 21 mg of protein per g of new cells, #pv("strain.titer_g_L") g/L would need
#fx(pv("strain.titer_g_L") / 21, d: 1) kg of new cells per litre. No public study we found shows
secretion at the design rate without growth.

// ---------------------------------------------------------------- key numbers table
#figure(
  table(
    columns: (2.2fr, 0.9fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, center, right, right, right, right),
    table.header([*Scenario*], [*Titer (g/L)*], [*BLG, price-anchored*], [*BLG, design-report*], [*OVA, price-anchored*], [*OVA, design-report*]),
    hline,
    [Best public academic strain], [#fx(S("academic/blg").design.titer, d: 1) / #fx(S("academic/ova").design.titer, d: 0)],
      [#usd0(S("academic/blg").msp_ccf)], [#usd0(S("academic/blg/light").msp_ccf)],
      [#usd0(S("academic/ova").msp_ccf)], [#usd0(S("academic/ova/light").msp_ccf)],
    [Base case (72 h production)], [30], [#usd(blg.msp_ccf)], [#usd(R.base_light.blg.msp_ccf)],
      [#usd(ova.msp_ccf)], [#usd(R.base_light.ova.msp_ccf)],
    [Industry benchmark (titer in private cost models)], [42], [#usd(S("industry/blg").msp_ccf)], [#usd(S("industry/blg/light").msp_ccf)],
      [#usd(S("industry/ova").msp_ccf)], [#usd(S("industry/ova/light").msp_ccf)],
    [Physical-limit best case (100 kt/yr, secretion 40 mg/g/h)], [#fx(PL("blg/humbird").titer, d: 0) / #fx(PL("ova/humbird").titer, d: 0)],
      [#usd(PL("blg/humbird").msp_ccf)], [#usd(PL("blg/light").msp_ccf)],
      [#usd(PL("ova/humbird").msp_ccf)], [#usd(PL("ova/light").msp_ccf)],
    [Base case with aseptic cell-culture vessels (v2's basis)], [30], [#usd(R.base_aseptic.blg.msp_ccf)], [—],
      [#usd(R.base_aseptic.ova.msp_ccf)], [—],
    hline,
    [Incumbent, per kg protein (2015–2025, 2025\$)], [], table.cell(colspan: 2)[whey #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0)],
      table.cell(colspan: 2)[egg white #usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0)],
  ),
  caption: [Minimum selling price (\$/kg target protein, 2025) with a capital charge of 14.6% of total
  capital investment per year. The capital conventions and the vessel price basis are defined in
  @sec-capital. 10 kt/yr and US Midwest unless noted. Academic BLG: Yao et al. (2026), whose
  production phase runs on ethanol (priced as glucose); on glucose, Li et al. (2026) reach 5.14 g/L
  (#usd0(S("academic/blg_li2026").msp_ccf)/kg). Academic OVA sums full-length and clipped protein; at
  1 g/L of intact OVA it costs #usd0(S("academic/ova_intact_1gL").msp_ccf)/kg.],
) <tab-key>

#figure(image("../docs/figures/fig10_price_ladder.png", width: 100%),
  caption: [Every case against its market, on one axis: filled dots use price-anchored capital (the
  base), hollow dots design-report capital; the shaded band is the incumbent's price range in 2025
  dollars. Model figures are production costs with a return on capital, not selling prices.]) <fig-ladder>

#outline(depth: 2, indent: 1.2em)
#pagebreak()

// ================================================================ 1
= Question and approach

PF companies now sell BLG (Perfect Day, Remilk, Vivici) and OVA (EVERY), and others are entering
(Onego Bio). Whether these proteins can displace animal proteins at scale or stay a premium niche
depends on what they cost to make. Published estimates disagree by a factor of several, and company
claims are rarely checked against the physics of aerobic fermentation. This study asks:

#quote(block: true)[
  What does it cost to make food-grade BLG and OVA by precision fermentation with today's public
  strain performance, and at the physical limits of aerobic fermentation? What combination of titer,
  rate, yield, downstream design and scale would bring them to price parity with whey and egg-white
  proteins?
]

#figure(
  table(
    columns: (0.3fr, 2.6fr, 1.8fr),
    align: (left, left, left),
    table.header([*\#*], [*Sub-question*], [*Answered in*]),
    hline,
    [Q1], [What do BLG and OVA cost at public (academic) and claimed (industry) performance?], [@sec-q1, @fig-titer],
    [Q2], [What drives the cost, and how good is the evidence for each driver?], [@sec-q2, @fig-bridge, @fig-tornado, @fig-mc],
    [Q3], [Which combinations of performance reach \$10 and \$20 per kg protein?], [@sec-q3, @fig-required],
    [Q4], [What is the cost at the physical limits?], [@sec-q4, @fig-breakdown],
    [Q5], [Are published company claims consistent with the fermenter's limits?], [@sec-q5, @tab-claims],
    [Q6], [How much do siting (US vs EU) and scale (1–100 kt/yr) matter?], [@sec-q6, @fig-scale],
    hline,
    [Q7], [_Added after v1:_ what do these costs mean per litre of milk and per egg?], [@sec-equiv, @fig-equiv],
    [Q8], [_Added after v1:_ how does a high-value protein (lactoferrin) compare?], [@sec-lf, @fig-lf],
  ),
  caption: [Q1–Q6 were fixed before any model output existed (`docs/SCOPE.md`); Q7–Q8 were added at
  the author's request after the first draft.],
)

*Why whey and egg white are the benchmarks.* BLG is the main protein of whey, and the PF BLG on the
market is sold as a whey-protein ingredient for bars, drinks and dairy analogues (FDA GRN 1056
specifies a concentrate of at least 70% protein). A buyer's alternative is whey protein concentrate
or isolate, so their price is the one PF BLG must meet; the same logic sets dried egg white against
OVA. It is a hard comparison. Whey is a by-product of cheese, sold for whatever clears the market
once cheese has paid for the milk, and it is among the cheapest animal proteins; if PF displaced
much of it, its price would fall further.
Two consequences follow. Price parity is not the only commercial route: pure, animal-free or
functional proteins can sell at a premium, as the lactoferrin case shows (@sec-lf). And displacing
whey changes milk output far less than one-for-one, because whey carries only a small part of the
milk's value (@sec-equiv).

*Why Humbird's method.* Humbird's (2021) cultured-meat analysis builds costs from conservation
laws: element and electron balances, oxygen transfer, heat removal. His full cost model reproduces
the market-implied cost of one fermented commodity, baker's yeast at about \$1.90/kg; capital-related
charges are less than half of that cost, so the check constrains his capital factors only loosely
(@sec-cal). We port his baker's-yeast workbook exactly and extend it with a secreted protein, a
downstream train, and the specifics of *K. phaffii* and *Trichoderma reesei*.

*Rules we followed* (written protocol, `PLAN.md`):
- Four scenarios are never merged: academic, industry, required and physical limit.
- Every input carries an evidence grade, A to E.
- The model structure is frozen before the calibration anchors are run; misses are recorded, not tuned away.
- Priors about the results were written down before the model existed; they are scored in @sec-priors.
- Model-to-model agreement is a consistency check, not validation.
- After the first draft, eight independent reviewers audited it; their findings and every resulting
  change are logged in `docs/AUDIT.md` (R1–R8, P-1 to P-13). Version 2 was then read by four
  simulated expert reviewers (AI); their reviews are kept verbatim in `docs/ai-review/` and answered
  comment by comment in `docs/REVIEW.md`.

// ================================================================ 2
= Methods

== Plant, products and functional unit

The functional unit is 1 kg of target protein in a spray-dried powder that meets the product
specification. The base specification is a *concentrate*, following Remilk's GRAS notice for BLG
(FDA GRN 1056): at least 70 wt% protein, at least 80% of it BLG, at most 7% moisture. OVA uses the
same specification by analogy. The *isolate* variant (99% target protein, dry basis) adds an
ammonium-sulfate precipitation, following Intelligen's (2025) OVA design. The lactoferrin contrast
case follows the recombinant bovine lactoferrin notices (FDA GRN 1219 and 1284): at least 90%
protein, at least 95% of it lactoferrin.

The plant is greenfield, single-product and nth-of-a-kind, built to food (not pharmaceutical) good
manufacturing practice. The base is 10 kt/yr of protein in the US Midwest, swept from 1 to
100 kt/yr, with a north-west Europe (Netherlands) variant. Money is 2025 US dollars. Excluded costs:
R&D, strain licences, regulatory approval, sales and distribution, land, first-of-a-kind premiums,
carbon pricing, start-up and commissioning, working capital (except in the discounted-cash-flow
price), failed batches, per-lot release testing and packaging. A reviewer (AI) put the last four at
roughly \$1–2/kg together. @fig-flow shows the base-case plant.

#figure(image("../docs/figures/fig0_flowsheet.png", width: 100%),
  caption: [Base-case process: *K. phaffii* secreting BLG at 30 g/L; flows per kg of BLG.]) <fig-flow>

== Stoichiometry and energetics

Each metabolic process is one element-balanced "black-box" reaction on C, H, O and N:
glucose + NH#sub[3] + O#sub[2] → biomass (or protein) + CO#sub[2] + H#sub[2]O. Electrons are
tracked through the degree of reduction γ per C-mol (glucose 4, *K. phaffii* biomass
#fx(K.gamma_biomass, d: 2), BLG #fx(K.gamma_blg, d: 2), OVA #fx(K.gamma_ova, d: 2)). This closes the O#sub[2] and CO#sub[2] balances once the carbon split is fixed.

*Growth.* Biomass yield comes from the Gibbs-energy dissipation correlation of Heijnen and van Dijken
(1992), as in Humbird's workbook. The energy dissipated per C-mol of biomass formed is

$ D = 200 + 18 (6 - c)^(1.8) + exp{[(3.8 - γ_s)^2]^(0.16) (3.6 + 0.4 c)} quad "kJ/C-mol", $

where $c$ and $γ_s$ are the carbon number and degree of reduction per C-mol of the substrate (valid
for $1 <= c <= 6$). The catabolic reaction (glucose to CO#sub[2]) is run just enough to supply $D$.
For glucose and our *K. phaffii* biomass formula (Carnicer et al. 2009) this gives a maximum biomass
yield of #fx(K.Yx_max, d: 2) g/g; the measured value is 0.50–0.56 g/g (`data/evidence/hosts.yaml`,
grade A). Biomass is counted as ash-free organic matter; ignoring the ~7% ash overstates the yield per g
of dry cells, but the same convention understates maintenance per g, and the two nearly cancel in
glucose per g of cells (audit R1-F3).

*Maintenance.* In the growth phase maintenance follows Tijhuis et al. (1993),
$m_G = 4.5 exp[-69 000 \/ R (1\/T - 1\/298)]$ kJ per C-mol biomass per hour:
#fx(K.m_s_tijhuis, d: 4) g glucose per g cells per hour at 30 °C, close to the 0.0147–0.0161 measured
for protein-producing *K. phaffii* in glucose chemostats (Maurer et al. 2006; Rebnegger et al. 2016).
In the production phase, where cells barely grow, maintenance falls: Rebnegger et al. (2016) found it
threefold lower at near-zero growth. We use the value measured for a protein-secreting strain at low
growth, #fx(pv("hosts.kphaffii.m_s_prod_g_g_h"), d: 4) g/g/h (Rebnegger et al. 2024; range
#P.hosts.kphaffii.m_s_prod_g_g_h.low–#P.hosts.kphaffii.m_s_prod_g_g_h.high).

*Product.* The protein's elemental formula comes from its mature UniProt sequence:
- BLG (P02754, 162 residues): C#sub[817]H#sub[1312]N#sub[206]O#sub[248]S#sub[9], 18.3 kDa;
- OVA (P01012, 385 residues): C#sub[1901]H#sub[2997]N#sub[499]O#sub[575]S#sub[22], 42.75 kDa;
- bovine lactoferrin (P24627, 689 residues): C#sub[3358]H#sub[5251]N#sub[945]O#sub[1002]S#sub[38], 76.1 kDa.

Glycans and phosphates are left out of the formulas: 3–6% of the mass of glycosylated OVA and
5–10% of lactoferrin, which changes the mass balance by less than 1%.

The product reaction makes protein from glucose and ammonia and respires enough extra glucose to pay
for synthesis, so the product-reaction yield $Y_(p s)$ fixes its O#sub[2] demand. *No measured BLG or
OVA yield on sugar exists*; the design values are lumped yields that already include maintenance and
some growth (Intelligen 0.28 g/g; Behm et al. 2022 0.223 g/g). We therefore derive $Y_(p s)$ so that
the model reproduces Intelligen's expression phase (their Eq. 2: 100 g glucose → 28 g OVA + 8 g
cells + 4 g host proteins):

$ 1 / Y_(p s) = 100/28 - (8\/28) / Y_x - m_(s,"prod") / q_p = 3.571 - 0.501 - 0.919 $

with our growth yield $Y_x = 0.5705$ g/g and Intelligen's specific productivity
$q_p = 0.00475$ g/g/h, giving $Y_(p s) = #fx(pv("strain.Y_ps_g_g"), d: 3)$ g/g. The growth rate in
production (#fx(pv("strain.mu_prod_per_h"), d: 4)/h) and the cell density at its start
(#fx(pv("strain.X_prod_g_L"), d: 0) g/L) follow from the same design and its volume balance. With
chemostat-level maintenance Intelligen's Eq. 2 would be impossible: maintenance alone would use all
of its glucose. Three cautions:
- *The inversion is sensitive to maintenance.* Maintenance and product enter as a ratio against a
  total of only 3.571: at the low end of the measured maintenance (0.0023 g/g/h) it gives
  $Y_(p s) = 0.39$, and above about 0.0146 it has no solution. With the product made at the
  energetic ceiling (below), Intelligen's expression phase leaves room for at most
  #fx(K.ms_prod_max_at_ceiling.ova, d: 4) g/g/h of production-phase maintenance: above the one
  measurement at near-zero growth (#fx(pv("hosts.kphaffii.m_s_prod_g_g_h"), d: 4), for a strain secreting
  far less) and below every maintenance coefficient compiled for growing cultures on methanol or
  glycerol, 0.009–0.032 (Looser et al. 2015, which gives none for glucose).
- *It charges Intelligen's host-cell protein to the target.* Read with the 4 g of host protein as
  product, the same equation gives 0.53 g/g.
- *It assumes secretion without growth.* The base production phase takes up glucose at only
  #fx(K.qs_production_g_g_h, d: 3) g per g cells per hour, a few times maintenance, while secreting
  #fx(blg.design.q_p_mg_g_h, d: 1) mg/g/h. In the *K. phaffii* chemostat studies on file, secretion
  rises with growth rate, linearly or up to an optimum near 0.08–0.1/h (Rebnegger et al. 2014;
  Garrigós-Martínez et al. 2019; Nieto-Taype et al. 2020). The best glucose fed-batch we found, run
  with a glucose-regulated promoter, peaked at 2.1 mg/g/h near 0.1/h (Prielhofer et al. 2018: 6.4 g/L
  in 60 h). A review of *K. phaffii* cultivation compiles maximal secretion rates of 0.004–0.69
  mg/g/h; its four entries on glucose (0.05–0.49) all peak at growth rates of 0.15–0.20/h, and it calls
  such secretion growth-associated (Looser et al. 2015). In the one near-zero-growth study we found secretion settled about fivefold
  below the trend at faster growth (Rebnegger et al. 2024, 0.02 mg/g/h at doubling times of two
  months, partly attributed to the promoter). Intelligen's design point is not a measurement.

The model's production phase then runs at an effective yield of
#fx(blg.design.effective_yield_production, d: 3) g/g at the base design point, close to
Intelligen's 0.28. The effective yield is an output: it rises with productivity, to
#fx(S("industry/blg").design.effective_yield_production, d: 2) at 42 g/L and
#fx(PL("blg/humbird").design.effective_yield_production, d: 2) in the physical-limit case, and neither
is anchored to data. The v1 reading (0.28 as the reaction yield, plus maintenance and growth on top)
is the low end of the yield range.

*Energetic ceiling.* Counting ATP gives an upper bound on $Y_(p s)$. Each residue costs the peptide
bond (#pv("energetics.atp_per_peptide_bond") ATP; Martin et al. 2025), the net cost of making the
amino acid from glucose and ammonium (#pv("energetics.atp_aa_synthesis_per_residue") ATP on
average: Stouthamer 1973 as recomputed by Martin et al. 2025, whose note is that the common amino
acids yield ATP) and, for the protein's sulfur, sulfate assimilation (#pv("energetics.sulfur_atp_per_S")
ATP plus 8 electrons per S). That is #fx(K.energetic.blg.atp_per_residue, d: 2) ATP per residue for BLG,
paid by respiring glucose at #pv("energetics.substrate_atp_per_glucose") + 12 × P/O ATP per glucose,
with P/O = #pv("hosts.kphaffii.po_ratio") for *K. phaffii* (a genome-scale-model value, Chung et al.
2010), i.e. #fx(K.atp_per_glucose, d: 1) ATP per glucose. The ceiling is
#fx(K.energetic.blg.ceiling, d: 3) g/g for BLG and #fx(K.energetic.ova.ceiling, d: 3) for OVA
(#fx(K.energetic.blg.polymerisation_only, d: 3) and #fx(K.energetic.ova.polymerisation_only, d: 3)
counting peptide bonds alone, as in version 2). Membrane transport, secretion, folding and turnover
are not counted, so it stays an upper bound. The base yield is #pct(blg.design.y_ps_over_ceiling) of
it. A different estimate, which treats protein synthesis as if it dissipated energy like growth
(Heijnen's correlation applied to the protein), gives #fx(K.heijnen_protein_yield.blg, d: 2) g/g for
BLG; it is not a bound, but it suggests the real ceiling sits below the ATP count.

*Heat.* Heat release is computed from formation enthalpies of the dissolved species: about
480–510 kJ per mol O#sub[2] for growth and maintenance and 520–570 for the product reaction. The
fermenter uses its own computed heat when it slows growth to the heat-removal limit and when a
design's peak heat is checked; the 460 kJ per mol O#sub[2] of Roels (1983, via Almeida Benalcázar et
al. 2025; calorimetry gives 455 ± 15, Maskow et al. 2010) only screens the O#sub[2] limit.

#check[The dissipation formula and its units; the conversion of $m_G$ to 0.0174 g/g/h; the $Y_(p s)$
derivation (`tests/test_model.py::test_y_ps_reproduces_intelligen_eq2`); the ATP ceiling
(`src/pftea/plant.py`, `atp_per_residue`; `tests/test_model.py::test_energetic_ceiling_components`).
The cost structure rests on these.]

== The fed-batch fermenter and its feasibility ceiling <sec-ferm>

Each production batch has two phases:
1. *Growth* from an inoculum of #fx(pv("strain.X0_g_L"), d: 2) g/L (5% of seed broth at
   #fx(pv("fermenter.seed_final_X_g_L"), d: 1) g/L, the density in Intelligen's lactoferrin flowsheet) at
   the maximum specific rate, slowed so that the oxygen uptake rate (OUR) never exceeds
   what the vessel can transfer and the heat never exceeds what it can remove, up to the production
   cell density $X_"prod"$.
2. *Production* for $t_"prod"$ hours at a small growth rate and a constant specific productivity $q_p$.
   No product is made during growth, a simplification for constitutive promoters.

The initial liquid volume is solved so that the broth ends at 80% of the vessel, and $q_p$ so that
the harvest titer equals the target. A volume balance tracks the feeds (glucose at
#pv("fermenter.feed_glucose_g_L") g/L, about 42 wt%, Intelligen's feed; ammonia at 30 wt%, i.e.
#pv("fermenter.nh3_feed_g_L") g/L), O#sub[2] uptake, CO#sub[2] release and evaporation.

*Oxygen transfer.* The transfer coefficient follows van 't Riet's correlation for non-coalescing
broths, $k_L a = 0.002 (P\/V)^(0.7) U_s^(0.2) 1.025^(T - 20)$ (s#super[−1], SI units), as in Humbird's
microbial fermenters, with a log-mean driving force between the bottom (hydrostatic pressure, fresh
air) and the top (back-pressure, depleted gas). For each demanded OUR the model picks the air rate
and agitation power that minimise compressor plus refrigeration-weighted agitator power, within
#thou(pv("fermenter.pv_max_W_m3")) W/m³ and a superficial gas velocity of #pv("fermenter.us_max_m_s") m/s
(grade D). In the base vessel the correlation alone would allow about #fx(K.otr_aeration_only, d: 0)
mol O#sub[2]/m³/h, but that extrapolates it well beyond the k#sub[L]a of about 800 h#super[−1] that
Humbird gives as the practical upper end; the #fx(pv("fermenter.heat_removal_max_kW_m3"), d: 0) kW/m³
heat-removal ceiling allows about #fx(K.otr_with_heat, d: 0). The design cap is Humbird's value for
an air-sparged stirred tank, "an OTR approaching 200 mol O#sub[2]/m³-h is common", on his own basis,
per m³ of cell-free liquid (his Eq. 4.2): #fx(K.cap_per_broth_107, d: 0) mol/m³/h per m³ of broth at the
base cell density, #fx(K.cap_per_broth_80, d: 0) at 80 g/L and #fx(K.cap_per_broth_150, d: 0) at 150 g/L.
Growth runs at it. (Version 2 used 150 per m³ of broth; 150 is Humbird's limit for bubble columns.)
An industrial designer may plan on 100–120 per m³ of broth with air at these cell densities (review
BE-7), and our aeration power is lower than NREL's and Intelligen's (@sec-cal).

*Compressor, and a check on aeration power.* The compressor raises the air adiabatically to the
bottom pressure at #pct(pv("fermenter.compressor_efficiency")) efficiency. Humbird's workbook formula puts
$k = 1.4$ where $(k-1)\/k = 0.286$ belongs and gives about 1.6× that power; we keep it only in the port of
his workbook, and in our model it would add #usd(BS.at("compressor power as in Humbird's workbook (k in place of (k-1)/k)") - blg.msp_ccf, d: 2)/kg
(review H1). With his formula, our aeration reproduces his own 2021 aeration sheet:
#fx(K.aeration_our150.humbird_a1, d: 2) kWh of compressor and agitator power per kg O#sub[2] at
150 mol/m³/h in a 200 m³ vessel, against his #fx(AER21, d: 2)\; with the corrected formula,
#fx(K.aeration_our150.adiabatic, d: 2). Humbird, Davis and McMillan's (2017) process simulations imply
about twice his 2021 figure (their Fig. 3 total less the chilling of reaction heat, our reading of a
chart); their model could not hold dissolved O#sub[2] down, as production plants do. Aeration
electricity costs #usd(K.aeration_electricity_usd_per_kg, d: 2) per kg of protein in the base, so
doubling it would add about as much; holding dissolved O#sub[2] at 50% of air saturation adds
#usd(BS.at("dissolved O2 held at 50% of air saturation") - blg.msp_ccf, d: 2)/kg, and leaving out the
temperature term of the k#sub[L]a correlation, as the 2017 paper does,
#usd(BS.at("kLa without the temperature factor (Humbird 2017 Eq. 2)") - blg.msp_ccf, d: 2)/kg.

*Other limits.* A design is *infeasible*, and never costed as if it worked, when it needs more O#sub[2]
or cooling than above, starts below #pct(pv("fermenter.min_initial_fill")) of the vessel volume (the
lowest start in a published design, Intelligen's 30.5%), secretes more than
#fx(pv("strain.q_p_max_mg_g_h"), d: 0) mg of protein per g of cells per hour (a judgment, grade D;
the base runs at #fx(blg.design.q_p_mg_g_h, d: 1), and no published *K. phaffii* process is near 40;
compiled maxima for secreted proteins are below 1, Looser et al. 2015),
exceeds the product's solubility, or has a yield above the energetic ceiling.

*Why a ceiling exists.* Each kg of BLG made costs about #fx(K.o2_mol_per_kg_made, d: 0) mol
O#sub[2] and #fx(blg.physical.glucose_kg * blg.design.recovery, d: 1) kg of glucose across the batch,
including growth and maintenance. The broth must end at 80% of the vessel, so every extra kg of
product means more feed and a batch that starts emptier. In the base design (107 g/L cells, a
500 g/L feed) that, not O#sub[2], is what caps the titer: at #fx(CEIL72, d: 0) g/L (72 h) the batch
would have to start below #pct(pv("fermenter.min_initial_fill")) of the vessel. Longer production
phases lower the ceiling (#fx(R.titer_ceiling.blg.at(tpi(36)), d: 0) g/L at 36 h,
#fx(R.titer_ceiling.blg.at(tpi(120)), d: 0) g/L at 120 h), because maintenance keeps consuming feed.
The ceiling depends on the design choices behind it (@sec-q3).

*What the fermenter model leaves out.* Broth viscosity and foam do not lower k#sub[L]a: the
correlation is for water-like broths at every cell density and titer, while Humbird's own method
stops a fed-batch at a viscosity (2 cP) his broth model reaches near 80 g/L cells. At the high cell
densities and titers of the best cases the O#sub[2] limit is therefore generous (review FS-6, HM-4).
Specific productivity is constant through the production phase, whereas real secreting cultures
often lose productivity after two or three days; and no product is made during growth, which is
conservative for constitutive promoters.

== Downstream processing

The train (@fig-flow) follows Intelligen's OVA design, with evidence-graded performance
(`data/evidence/dsp.yaml`):
- *Cell removal.* Dilute to #pv("dsp.dilution_to_g_L_cells") g/L cells, then two disk-stack centrifuge
  stages with re-dilution of the paste. Each paste holds #pct(pv("dsp.paste_extracellular_frac"))
  extracellular liquid by volume (Petrides: 40–60%), so a fraction
  $φ = e V_p \/ (V_1 - V_"wc")$ of the product is trapped per stage and the recovery is $1 - φ^2$
  (#pct(blg.design.recovery_cell_removal, d: 1) in the base). The wash water is counted.
- *Microfiltration polish* at #pv("dsp.mf_flux_LMH") L/m²/h (grade D, range
  #P.dsp.mf_flux_LMH.low–#P.dsp.mf_flux_LMH.high) and #pct(pv("dsp.mf_recovery"), d: 1) recovery
  (Behm et al. 2022).
- *Ultrafiltration and diafiltration.* Concentrate at #pv("dsp.uf_flux_LMH") L/m²/h to
  #pv("dsp.diafiltration_conc_g_L") g/L, diafilter #pv("dsp.diafiltration_volumes") volumes there at
  #pv("dsp.df_flux_LMH") L/m²/h (the only diafiltration flux on file, EVERY patent US 2025/0134130,
  measured on a redissolved precipitate at 10 °C, so probably conservative for clarified broth), then
  concentrate to the spray-dryer feed at the same low flux. Rejection #pv("dsp.uf_rejection"). Skids
  cost \$#pv("dsp.membrane_skid_usd_m2") per m² of membrane installed (a dairy plant, Mercier-Bouchard
  et al. 2017), converted to a purchase cost before the installation factors are applied.
- *Dryer feed.* Dairy plants feed high-protein whey concentrates to the dryer at 27–37% solids by
  membranes, not evaporators (Tetra Pak); egg white is ultrafiltered to about 23% (Tsai et al. 1977).
  We use #pct(pv("dsp.dryer_feed_solids_blg")) for BLG and #pct(pv("dsp.dryer_feed_solids_ova")) for OVA.
- *Spray dryer* at 4.87 MJ per kg water evaporated (industry survey, grade A); purchase cost from a
  supplier-based SuperPro model (Yver et al. 2012).
- *Isolate only:* ammonium-sulfate precipitation (350 g/L; 89% recovery), washed basket centrifuges;
  the dryer is fed the 20%-solids cake.
- *Lactoferrin only:* cation-exchange capture between microfiltration and ultrafiltration, as in the
  dairy process and every commercial PF lactoferrin (@sec-lf).
- *Cleaning in place* (#fx(pv("dsp.cip_solution_kg_per_kg"), d: 1) kg solution per kg product,
  Intelligen; its chemicals are inside Humbird's maintenance charge) and *spent-cell disposal*
  (#usd0(pv("utilities.biomass_disposal_usd_t_dry"))/t dry cells in the US, a landfill tipping fee;
  #usd0(pveu("utilities.biomass_disposal_usd_t_dry"))/t in the EU, an anaerobic-digestion gate fee;
  both per wet tonne converted at the 15% dry solids of the model's centrifuge paste, with no
  dewatering or inactivation costed). Sale as feed or fertiliser would make it free or a credit.

The target protein share of the concentrate powder is 85% on a dry basis (grade D; the GRN 1056
minimum is 56%). The base overall recovery is #pct(blg.design.recovery).

*OVA solubility.* Intelligen stops its ultrafiltration at 50 g/L, "its practical solubility limit",
without a source; vendor data sheets give 40–50 mg/mL as quality-control concentrations. OVA dissolves
at 200 g/L in water (Wang et al. 2025) and is processed at about 110 g/L in ultrafiltered egg white
(Tsai et al. 1977). We therefore do not treat 50 g/L as a limit, and show it as a sensitivity. No data
exist at pH 5, the fermentation pH, which is close to OVA's isoelectric point.

== Capital: vessel prices and two accounting conventions <sec-capital>

*Fermenter prices.* Fermenters are the largest equipment item. The base prices them from a vendor
quote: NREL 2011's 300 m³ stainless fermenter with internal cooling coils and an agitator,
\$#fx(K.nrel_fermenter_300m3_2007usd / 1e6, d: 2)M in 2007 dollars, scaled with exponent 0.7, i.e.
#musd(K.vendor_200m3_2025usd) per 200 m³ in 2025 dollars. It is an industrial enzyme-plant vessel, the
closest public analogue of a food-grade PF fermenter. It is also at the vessel price level of
Humbird's own baker's-yeast workbook, whose 200 m³ bubble column costs about \$0.8M (2018), and
consistent with Intelligen's food-PF design (@sec-cal). Version 2 used Humbird's quote curve for the
aseptic stirred tank he designed for cultured meat: 316L, full vacuum, built to the ASME bioprocessing
standard. That vessel costs #musd(K.strferm_200m3_2025usd) per 200 m³ (2025 dollars),
#fx(K.strferm_300m3_2007usd / K.nrel_fermenter_300m3_2007usd, d: 1)× the vendor quote. Humbird himself
separates aseptic industrial fermentation, which tolerates a few foreign organisms, from aseptic
animal-cell culture, which does not. We keep his aseptic vessels as a named high case ("aseptic
vessels", #dusd(R.base_aseptic.blg.msp_ccf - blg.msp_ccf)/kg on the base BLG). Seed fermenters
(#fx(K.seeds_m3.at(0), d: 1) and #fx(K.seeds_m3.at(1), d: 2) m³, #K.seed_units.at(0) of each so that a batch can
start every few hours) are priced on the same curve, scaled far below its quote. They are
#pct(K.seed_share_of_fermenter_cost, d: 1) of fermenter cost; Humbird's aseptic quotes, which do cover
that size, are #fx(K.seed_acce_over_vendor, d: 1)× the curve there and would add
#usd(BS.at("seed fermenters priced on Humbird's aseptic curve") - blg.msp_ccf, d: 2)/kg.

*Price-anchored capital (Humbird method; base).*
- Other equipment comes from Humbird's cost curves (Aspen ACCE quotes, 2018 dollars). Costs are
  escalated to 2025 with a factor of #fx(pv("capital.cost_index_2018_to_2025"), d: 2) (CEPCI and the
  BLS machinery price index; grade B, range 1.23–1.52). The BLS index for heavy-gauge metal tanks rose
  1.92× over the same years; escalating the fermenters with it would add
  #usd(BS.at("fermenters escalated with the heavy-gauge tank PPI") - blg.msp_ccf, d: 1)/kg.
- The equipment list is abbreviated (it omits CIP and feed tanks per fermenter, sterile filter
  housings, sugar storage, biomass inactivation, powder packing and effluent pretreatment), so we add
  #pct(pv("capital.missing_frac")) for missing items, the allowance of Humbird's yeast workbook for its
  own abbreviated list (his fuller cell-culture sheets use 10%).
- Installation, buildings, engineering, fees and contingency follow the "commodity aerobic" facility
  class that Humbird tabulates (a food-grade plant with the process in a sanitary building). None of
  his own sheets uses that class: his cultured-meat sheets use the cGMP biopharmaceutical class and
  his yeast workbook a flat Lang factor of 4.5. The effective Lang factor (investment over equipment
  cost) here is #fx(blg.design.lang_effective, d: 1), high because buildings are costed by floor area
  while the fermenters are now cheaper.
- Maintenance is 4% of total capital investment (TCI) per year, including CIP chemicals, and insurance
  5%, Humbird's whole fixed-cost rule. There is no separate plant-overhead, quality-control or
  local-tax line, so the 9% stands for all of them; insurance alone is usually well under 1%.
- What the anchor supports: with these factors and fixed costs Humbird's yeast workbook lands in the
  cost band implied by the market price (@sec-cal), and a lighter, NREL-like set does not. Capital-related
  charges are less than half of the yeast cost, so the check is loose: it favours Humbird's set but
  cannot pin it.

*Design-report capital (NREL-style; sensitivity).* The convention of NREL's 2011 design report
(whose lead author is also Humbird): the same fermenter quote; NREL's installation factors (1.7 for
fermenters, 1.8 otherwise) plus indirect costs of 60% of direct cost; no separate warehouse;
maintenance of 3% of installed process-area cost and insurance of 0.7% of fixed capital.

On the base BLG plant the two conventions differ by #usd(conv.at(0).msp - conv.at(2).msp)/kg:
#usd(conv.at(0).msp - conv.at(1).msp) of it comes from the fixed-cost rule alone, and
#usd(conv.at(1).msp - conv.at(2).msp) from the installation and indirect factors.

A Netherlands plant costs #fx(pveu("capital.location_factor"), d: 2)× the same plant in the US Midwest
(IEAGHG 2018, same plants costed in both places), applied to capital in both conventions.

== Operating costs, labour and money

*Operating costs.* Raw materials, utilities and consumables come from the mass and energy balance and
the prices in Appendix A: EIA, Eurostat and BLS statistics, trade unit values and published designs
(grades A–B).

*Labour.* Humbird's operator-attention model: operators per fermenter by the fraction of time a batch
needs attention, fixed staffing for continuous areas, 4.5 shifts per position, one supervisor per ten
staff at 1.4× salary, and a 100% labour burden (Humbird). The base plant employs
#fx(blg.design.fte, d: 0) people, operators and supervisors only; salaried staff are inside the fixed-cost
rule (@sec-capital).

*Headline metric.* MSP#sub[CCF]: annual operating cost plus a capital charge, divided by annual
output. The charge is the capital recovery factor $i \/ (1 - (1+i)^(-n)) = 0.146$ per year at
$i = 7.5%$ and $n = 10$ years (Humbird). It is a cost with a return on capital, not a market price.
We also compute the cost of production (COP: operating cost plus depreciation, no return) and an
NREL-style discounted-cash-flow price MSP#sub[DCF] (10% IRR, 30 years, 21% tax, 7-year MACRS,
construction over three years, working capital). For base BLG these are #usd(blg.cop) and
#usd(blg.msp_dcf).

== Evidence grades, scenarios and uncertainty <sec-scen>

Every parameter and evidence item is graded (@tab-grades). The four scenarios combine grades
differently and are never averaged:
- *academic:* the best public strain performance, read in full text. BLG: 13.88 g/L in *K. phaffii*
  (Yao et al. 2026), whose production phase runs on ethanol with glutamate feeding; the model has one
  carbon source and prices it as glucose (per electron the two cost about the same), so this case is
  flagged: ethanol is more reduced than glucose, so the O#sub[2] demand and heat per kg of product
  are higher than modelled, and the feasibility check is not conservative for this case. The modelled
  batch ends at #fx(S("academic/blg").design.X_end, d: 0) g/L cells against about 120 in Yao's run, because
  the model's volume balance dilutes; it is a cost estimate for 13.88 g/L in 108 h, not a simulation of
  that run. On glucose, Li et al. (2026) reach 5.14 g/L in 132 h. Their feed table (supplementary
  Table S4) gives the only public check on a BLG yield on glucose: 1–2% overall, depending on whether
  its feed rates refer to the starting or the current broth volume (our arithmetic; the volume profile
  is not reported). Our model of that run gives
  #pct(S("academic/blg_li2026").physical.overall_yield_g_g, d: 1)#if S("academic/blg_li2026").physical.overall_yield_g_g > 0.02 [, so it is, if
  anything, optimistic on sugar there.] else [, inside that range.] OVA: 2 g/L in *T. reesei* (Aro et al. 2023),
  with no growth in production. That is the sum of full-length and clipped OVA, and the purified
  product was mostly the clipped 36 kDa form, so intact OVA was probably well under 2 g/L; a 1 g/L
  variant is shown. The *T. reesei* production phase uses the yeast maintenance correlation, which is
  a lower bound on its sugar use. Yield and maintenance keep the base values: no measured product
  yield exists.
- *industry:* 42 g/L, the average that Hawkwood computed over private companies' models of
  unspecified secreted proteins for GFI (2025) (grade C), with everything else at the base case.
- *required:* the inverse problem: the titer needed for \$10, \$20 and \$50/kg at each production time.
- *physical limit:* a best case at assumed limits, not a floor set by physics. Every lever moved
  from the base: product yield #yaml("../data/pf/scenarios/physical_limit.yaml").common.at("strain.Y_ps_g_g") g/g (95% of
  BLG's energetic ceiling); the lowest measured maintenance in both phases; no growth in production; a
  600 g/L glucose feed (Shemesh et al. 2024; 730 g/L has been fed in a 2.6 L laboratory vessel, Heyland
  et al. 2010, which would raise the ceiling somewhat further); 400 m³ vessels; O#sub[2] transfer capped at 250 mol/m³/h
  per m³ of cell-free liquid (head pressure, not costed; grade D) and heat removal at 40 kW/m³
  (external exchangers, not costed; grade D); an 8 h turnaround; a 90% concentrate; contract sugar;
  and 100 kt/yr. A search over cell density and production time puts the titer at its feasibility
  ceiling, where cost is lowest, and reports which limits bind. Secretion stays capped at
  #fx(pv("strain.q_p_max_mg_g_h"), d: 0) mg/g/h, and the result is shown against that cap from 5 to
  120 mg/g/h.

#figure(
  table(
    columns: (0.4fr, 3fr),
    table.header([*Grade*], [*Meaning*]),
    hline,
    [A], [Measured, primary source or official statistic (peer-reviewed data, EIA, Eurostat, BLS, USDA)],
    [B], [Design value or patent example from a named source (NREL, Intelligen, Humbird, patents)],
    [C], [Company claim, press release, industry survey, secondary transcription],
    [D], [Analogy, judgment or calculation from graded inputs],
    [E], [Guess; listed in @sec-limits],
  ),
  caption: [Evidence grades (`data/evidence/README.md`).],
) <tab-grades>

*Uncertainty.* Two tools:
- *Tornado.* Each parameter with a graded range moves to its low and high value, one at a time. An end
  that breaks a physical limit is moved to the last feasible value, so no bar quotes the cost of an
  impossible plant. The accounting convention and the fermenter price basis are shown as their own
  (structural) bars.
- *Monte Carlo.* Triangular draws over each scenario's uncertain parameters, with host-specific ranges.
  Draws that break a physical limit, or for which no plant can be built, count as infeasible; we
  report the feasible fraction, the limit each infeasible draw breaks, and percentiles over feasible
  plants and over all draws with a cost. Draws are independent: no data exist to set correlations,
  and the feasibility filter is the only coupling. Structural choices (conventions, vessel price
  basis, minimum fill, secretion ceiling) are not sampled; they are shown one at a time.

// ================================================================ 3
= Calibration <sec-cal>

The structure was frozen first. Each anchor then changes only its own process inputs, prices, cost
year and financing, and misses are recorded in `docs/VALIDATION.md`. `tests/test_calibration.py` pins
each recorded value to within five points, so a change that moves an anchor cannot pass silently.

#figure(
  table(
    columns: (2.1fr, 2.2fr, 0.9fr, 0.9fr, 0.8fr),
    align: (left, left, right, right, right),
    table.header([*Anchor (type)*], [*Quantity*], [*Ours*], [*Theirs*], [*Diff.*]),
    hline,
    [1. Humbird baker's yeast (software + reality)], [cost, \$/kg dry cells (2018)],
      [#fx(R.calibration.bakers_yeast.cop, d: 3)], [#fx(R.calibration.bakers_yeast.humbird, d: 3)],
      [#sgn(R.calibration.bakers_yeast.cop / R.calibration.bakers_yeast.humbird - 1, d: 2)],
    hline,
    [2. NREL 2011 on-site cellulase (consistency)], [glucose, kg/kg protein],
      [#fx(cal("nrel2011_cellulase", "glucose_kg_per_kg").at(0), d: 2)], [#fx(cal("nrel2011_cellulase", "glucose_kg_per_kg").at(1), d: 2)],
      [#sgn(calrel("nrel2011_cellulase", "glucose_kg_per_kg"), d: 1)],
    [], [O₂, mol/kg protein], [#fx(cal("nrel2011_cellulase", "o2_mol_per_kg").at(0), d: 1)], [#fx(cal("nrel2011_cellulase", "o2_mol_per_kg").at(1), d: 0)],
      [#sgn(calrel("nrel2011_cellulase", "o2_mol_per_kg"), d: 1)],
    [], [electricity, kWh/kg], [#fx(cal("nrel2011_cellulase", "electricity_kWh_per_kg").at(0), d: 1)], [#fx(cal("nrel2011_cellulase", "electricity_kWh_per_kg").at(1), d: 0)],
      [#sgn(calrel("nrel2011_cellulase", "electricity_kWh_per_kg"))],
    [], [cost, \$/kg protein (2007), price-anchored],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)").at(0), d: 2)],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)").at(1), d: 2)],
      [#sgn(calrel("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)"))],
    [], [cost, design-report (NREL's own) capital],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]").at(0), d: 2)],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]").at(1), d: 2)],
      [#sgn(calrel("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]"))],
    hline,
    [3. Intelligen 2025 OVA (consistency)], [cost, \$/kg powder, price-anchored],
      [#fx(cal("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)").at(0), d: 2)],
      [#fx(cal("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)").at(1), d: 2)],
      [#sgn(calrel("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)"))],
    [], [total capital investment], [#musd(cal("intelligen2025_ova", "TCI_usd").at(0))], [#musd(cal("intelligen2025_ova", "TCI_usd").at(1))],
      [#sgn(calrel("intelligen2025_ova", "TCI_usd"))],
    [], [glucose, kg/kg powder], [#fx(cal("intelligen2025_ova", "glucose_kg_per_kg_powder").at(0), d: 1)],
      [#fx(cal("intelligen2025_ova", "glucose_kg_per_kg_powder").at(1), d: 1)], [#sgn(calrel("intelligen2025_ova", "glucose_kg_per_kg_powder"))],
    [], [electricity, kWh/kg powder], [#fx(cal("intelligen2025_ova", "electricity_kWh_per_kg_powder").at(0), d: 1)],
      [#fx(cal("intelligen2025_ova", "electricity_kWh_per_kg_powder").at(1), d: 1)], [#sgn(calrel("intelligen2025_ova", "electricity_kWh_per_kg_powder"))],
    hline,
    [4. Voutilainen 2021 recombinant case (consistency)], [sugar, kg/kg protein (by construction)],
      [#fx(cal("voutilainen2021_case", "sugar_kg_per_kg_protein").at(0), d: 2)], [#fx(cal("voutilainen2021_case", "sugar_kg_per_kg_protein").at(1), d: 2)],
      [#sgn(calrel("voutilainen2021_case", "sugar_kg_per_kg_protein"), d: 1)],
    [], [cost, €/t protein, their DCF, price-anchored], [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF)").at(0))],
      [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF)").at(1))], [#sgn(calrel("voutilainen2021_case", "EUR_per_t_protein (their DCF)"))],
    [], [their fixed costs, price-anchored capital], [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF) [their fixed costs, Humbird capital]").at(0))],
      [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF) [their fixed costs, Humbird capital]").at(1))],
      [#sgn(calrel("voutilainen2021_case", "EUR_per_t_protein (their DCF) [their fixed costs, Humbird capital]"))],
    [], [their fixed costs, design-report capital], [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]").at(0))],
      [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]").at(1))],
      [#sgn(calrel("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]"))],
  ),
  caption: [Calibration anchors. Anchor 1 is Humbird's own workbook, ported line by line; anchors 2–4
  are other models run on their own inputs. Diagnoses: `docs/VALIDATION.md`.],
) <tab-cal>

*What the anchors say.*
1. *The port is exact.* It reproduces Humbird's baker's-yeast cost to 0.004%, and that cost sits on
   his market-implied ~\$1.90/kg. The market band itself depends on how his 33% margin is read:
   #usd(STK.at("market band, 33% margin on price").at(0), d: 2)–#usd(STK.at("market band, 33% margin on price").at(1), d: 2)/kg
   if it is a share of the price, #usd(STK.at("market band, 33% margin on cost").at(0), d: 2)–#usd(STK.at("market band, 33% margin on cost").at(1), d: 2)
   if it is a mark-up on cost. With a lighter, NREL-like capital set (investment 3.2× listed equipment,
   fixed costs 1.9% a year) the workbook gives
   #usd(STK.at("NREL-like stack (TCI 3.2 x listed, 1.2% + 0.7%)"), d: 2)/kg, below both bands; with
   Humbird's factors but NREL-like fixed costs,
   #usd(STK.at("Humbird factors, NREL-like fixed costs (1.5% + 0.7%)"), d: 2)\; with our PF capital charge
   (7.5% over 10 years instead of his 10% over 20),
   #usd(STK.at("with the PF capital charge (7.5%/10 yr)"), d: 2). The anchor favours Humbird's
   factors and fixed costs, loosely. It says nothing about fermenter prices beyond its own bubble
   column.
2. *Sugar and O#sub[2] agree with the design that states them independently* (NREL,
   #sgn(calrel("nrel2011_cellulase", "glucose_kg_per_kg")) and #sgn(calrel("nrel2011_cellulase", "o2_mol_per_kg"))).
   Voutilainen's sugar is matched by construction, and Intelligen's expression phase is, too, because
   our product yield is derived from it; its growth phase uses 0.40 g/g, below our 0.53 effective and
   the measured 0.50–0.56. *Electricity does not agree*: ours is
   #fx(-100 * calc.max(calrel("nrel2011_cellulase", "electricity_kWh_per_kg"), calrel("intelligen2025_ova", "electricity_kWh_per_kg_powder")), d: 0)–#fx(-100 * calc.min(calrel("nrel2011_cellulase", "electricity_kWh_per_kg"), calrel("intelligen2025_ova", "electricity_kWh_per_kg_powder")), d: 0)%
   lower, because our aeration is
   power-optimised while NREL sizes agitators for peak load and Intelligen aerates at 1.2–1.6 vvm and
   runs a fertiliser section; a real plant may need more aeration power than ours. These are
   consistency checks, not calibration fits.
3. *Capital now agrees; fixed costs do not.* With vendor-quote fermenters our investment for
   Voutilainen's plant is within #sgn(calrel("voutilainen2021_case", "TCI vs their FCI (EUR)")) of theirs,
   and for Intelligen's #sgn(calrel("intelligen2025_ova", "TCI_usd")) above (their Lang factor is 4, ours
   higher). Their total costs are still
   #pubratio×
   lower than ours (NREL, Voutilainen), mainly because their fixed costs are 1.5–2% of capital per year
   instead of 9%, and their capital charges lighter. With their conventions our model still lands
   above theirs, by #sgn(calrel("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]"))
   (Voutilainen) and #sgn(calrel("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]")) (NREL);
   the rest is mostly labour, buildings and cleaning.
4. *Intelligen's total is within #sgn(calrel("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)"))*
   (their cost recast into our capital charge and fixed costs), with compensating differences: our
   capital is higher and our plant needs #R.calibration.intelligen2025_ova.design.n_fermenters whole fermenters where theirs has five; our glucose and
   electricity are lower.

We keep Humbird's factors and fixed costs as the base because his workbook with them lands in the
yeast market band and a lighter set does not; that is a loose test, and the design-report convention
is shown everywhere as a named structural sensitivity, not as an error band. NREL itself notes that
enzyme producers quoted costs about 47% above its estimate.

// ================================================================ 4
= Results

== Base case

#figure(
  table(
    columns: (2fr, 1fr, 1fr, 0.2fr, 2.2fr, 1fr),
    align: (left, right, right, center, left, right),
    table.header([*Cost item, \$/kg protein*], [*BLG*], [*OVA*], [], [*Physical intensity, per kg BLG*], []),
    hline,
    [capital charge (14.6%/yr)], [#usd(blg.per_kg.at("capital charge"), d: 2)], [#usd(ova.per_kg.at("capital charge"), d: 2)], [],
      [glucose], [#fx(blg.physical.glucose_kg, d: 1) kg],
    [maintenance], [#usd(blg.per_kg.maintenance, d: 2)], [#usd(ova.per_kg.maintenance, d: 2)], [],
      [oxygen], [#fx(blg.physical.o2_kg, d: 1) kg],
    [insurance (Humbird's 5%, all overheads)], [#usd(blg.per_kg.at("insurance"), d: 2)], [#usd(ova.per_kg.at("insurance"), d: 2)], [],
      [electricity], [#fx(blg.physical.electricity_kWh, d: 1) kWh],
    [glucose], [#usd(blg.per_kg.glucose, d: 2)], [#usd(ova.per_kg.glucose, d: 2)], [],
      [natural gas (drying, steam)], [#fx(blg.physical.natural_gas_MJ, d: 0) MJ],
    [labour], [#usd(blg.per_kg.labour, d: 2)], [#usd(ova.per_kg.labour, d: 2)], [],
      [spent cells (dry)], [#fx(blg.physical.cells_kg, d: 1) kg],
    [spent-cell disposal], [#usd(blg.per_kg.at("biomass disposal"), d: 2)], [#usd(ova.per_kg.at("biomass disposal"), d: 2)], [],
      [overall yield on glucose], [#fx(blg.physical.overall_yield_g_g, d: 3) g/g],
    [electricity], [#usd(blg.per_kg.electricity, d: 2)], [#usd(ova.per_kg.electricity, d: 2)], [],
      [fermenter volume], [#fx(blg.physical.fermenter_m3_per_kt, d: 0) m³ per kt/yr],
    [media, ammonia and DSP chemicals],
      [#usd(blg.per_kg.at("salts & other media") + blg.per_kg.ammonia + blg.per_kg.at("DSP chemicals"), d: 2)],
      [#usd(ova.per_kg.at("salts & other media") + ova.per_kg.ammonia + ova.per_kg.at("DSP chemicals"), d: 2)], [],
      [staff], [#fx(blg.physical.fte_per_kt, d: 1) per kt/yr],
    [gas, steam, water, membranes],
      [#usd(blg.per_kg.at("natural gas & steam") + blg.per_kg.at("water & wastewater") + blg.per_kg.membranes, d: 2)],
      [#usd(ova.per_kg.at("natural gas & steam") + ova.per_kg.at("water & wastewater") + ova.per_kg.membranes, d: 2)], [],
      [total capital investment], [#musd(blg.tci)],
    hline,
    [*MSP#sub[CCF]*], [*#usd(blg.msp_ccf, d: 2)*], [*#usd(ova.msp_ccf, d: 2)*], [], [production fermenters], [#fx(blg.design.N_prod_int, d: 0) × 200 m³],
    [per kg powder], [#usd(blg.per_kg_powder, d: 2)], [#usd(ova.per_kg_powder, d: 2)], [], [harvest], [#fx(blg.design.X_end, d: 0) g/L cells],
  ),
  caption: [Base case: *K. phaffii*, 30 g/L, 72 h production, 10 kt/yr, US Midwest, vendor-quote fermenters,
  price-anchored capital.],
) <tab-base>

Capital-related charges (capital charge, maintenance and insurance) are #pct(capshare(blg)) of the BLG
price; glucose is #pct(blg.per_kg.glucose / blg.msp_ccf) and spent-cell disposal
#pct(blg.per_kg.at("biomass disposal") / blg.msp_ccf).
- *Why so much capital.* At 30 g/L the plant needs #fx(blg.design.N_prod_int, d: 0) production
  fermenters of 200 m³. Each batch occupies a vessel for about #fx(blg.design.cycle_h, d: 0) h
  including turnaround and yields #thou(blg.design.target_per_batch_kg) kg of protein.
- *Why glucose is modest.* The overall yield of protein on glucose is only
  #fx(blg.physical.overall_yield_g_g, d: 3) g/g, because the cells, their maintenance and the product
  reaction all consume sugar; at \$#fx(pv("utilities.glucose_usd_kg"), d: 2)/kg glucose it is still
  only #pct(blg.per_kg.glucose / blg.msp_ccf) of the price.

The product made per m³ of fermenter per hour is the lever the rest of the paper explores.

== Q1: cost against titer, with every public and claimed data point <sec-q1>

#figure(image("../docs/figures/fig1_cost_vs_titer.png", width: 100%),
  caption: [Minimum selling price against harvest titer for three production times. Vertical lines mark
  the best public titers, the average titers assumed in published and private cost models (GFI 2025), and design or
  claimed titers. Lines end at the feasibility ceiling of the fermenter.]) <fig-titer>

Cost falls roughly as 1/titer until the ceiling (@fig-titer):
- *Best public academic strains:* BLG at #fx(S("academic/blg").design.titer, d: 2) g/L costs
  #usd0(S("academic/blg").msp_ccf)/kg (ethanol-fed production priced as glucose), and
  #usd0(S("academic/blg_li2026").msp_ccf)/kg at 5.14 g/L on glucose. OVA at
  #fx(S("academic/ova").design.titer, d: 0) g/L in *T. reesei* costs #usd0(S("academic/ova").msp_ccf)/kg.
  BLG is then #fx(S("academic/blg").msp_ccf / inc.whey.band.at(1), d: 1)–#fx(S("academic/blg").msp_ccf / inc.whey.band.at(0), d: 1)×
  the whey band and OVA #fx(S("academic/ova").msp_ccf / inc.egg.band.at(1), d: 0)–#fx(S("academic/ova").msp_ccf / inc.egg.band.at(0), d: 0)×
  the egg-white band.
- *The titer private cost models assume (42 g/L):* #usd(S("industry/blg").msp_ccf) (BLG) and
  #usd(S("industry/ova").msp_ccf) (OVA), or #usd(S("industry/blg/light").msp_ccf) (BLG) and
  #usd(S("industry/ova/light").msp_ccf) (OVA) with design-report capital.

*The incumbents.* Official trade unit values form a consistent series, deflated to 2025 dollars with
the US consumer price index:
- *Whey protein >80%* (WPC80 and WPI mixed; US and EU exports): #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0)
  per kg protein in 2015–2025, taking the traded product as 80% protein, the minimum for its trade
  code. If the mix averaged 88% (more isolate), the band would be
  #usd(inc.whey.band.at(0) * 0.80 / 0.88, d: 0)–#usd(inc.whey.band.at(1) * 0.80 / 0.88, d: 0).
- *Dried egg albumin* (EU exports; 81.1% protein, USDA): #usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0).
  #let evw = EQ.ingredient_per_unit.egg_vs_whey
  #let cheaper = evw.keys().filter(y => evw.at(y).egg < evw.at(y).whey)
  Egg white is not always dearer than whey: per kg of protein it was cheaper than the average whey
  export price in #cheaper.len() of #evw.len() years (#cheaper.join(", ")).
- *A 2026 whey spike.* WPC80 and WPI rose to about #usd(inc.whey.spot.at(0).usd_kg_protein, d: 0) per kg
  protein at the 2026 peak (USDA Dairy Market News narrative quotes, not a formal series). At that
  price the base case (#usd(blg.msp_ccf)) #if blg.msp_ccf < inc.whey.spot.at(0).usd_kg_protein [would undercut whey] else [would not undercut whey], as
  #if S("industry/blg").msp_ccf < inc.whey.spot.at(0).usd_kg_protein [would] else [would not] the industry
  benchmark (#usd(S("industry/blg").msp_ccf)). Against 2015–2025 prices, the industry benchmark is
  #where(S("industry/blg").msp_ccf, inc.whey.band) the band with price-anchored capital and
  #where(S("industry/blg/light").msp_ccf, inc.whey.band) it with design-report capital.

*Other protein ingredients* (@fig-context). Per kg of protein, plant protein concentrates and isolates
trade far below whey and egg white (#usd(R.benchmarks.context.find(c => c.key == "pea_protein_price_range_gfi2025").lo, d: 1)–#usd(R.benchmarks.context.find(c => c.key == "pea_protein_price_range_gfi2025").hi, d: 1)
for pea and soy, GFI 2025), and casein, gelatin and collagen sit around
#usd(R.benchmarks.context.find(c => c.key == "casein_price_range_gfi2025").lo, d: 0)–#usd(R.benchmarks.context.find(c => c.key == "casein_price_range_gfi2025").hi, d: 0).
PF BLG and OVA do not compete with plant proteins on price per gram of protein; they compete with the
dairy and egg ingredients whose functions (gelling, foaming, whipping) they reproduce.

#figure(image("../docs/figures/fig11_protein_context.png", width: 100%),
  caption: [Protein ingredients per kg of protein against this model's costs. Bars: market prices (export
  unit values, 2015–2025 in 2025 dollars; GFI 2025 ranges, nominal). Lines: modelled production costs.]) <fig-context>

Parity in production cost is necessary but not sufficient for commercial parity: PF proteins also
compete on functionality and price per unit of function.

== Q2: what drives the cost <sec-q2>

#figure(image("../docs/figures/fig2_bridge.png", width: 100%),
  caption: [From NREL's on-site cellulase to our base case, one change at a time. The start is NREL's
  2011 design re-priced to 2025 with design-report capital.]) <fig-bridge>

*Why a food protein costs more than an industrial enzyme.* @fig-bridge walks from an NREL-style crude
enzyme (#usd(R.bridge.at(0).msp)/kg) to the base BLG concentrate (#usd(blg.msp_ccf)/kg). The steps:
#for i in range(1, R.bridge.filter(b => b.kind == "step").len()) [
  - #R.bridge.at(i).step: #dusd(R.bridge.at(i).msp - R.bridge.at(i - 1).msp)
]
The OVA isolate variant adds precipitation and a second recovery loss:
#dusd(R.bridge.filter(b => b.kind == "variant").last().msp - blg.msp_ccf) over the BLG concentrate.
The order of the steps changes their sizes, not the total.
#let infeas = R.bridge.filter(b => b.kind == "step" and b.flags.any(f => f.contains("productivity") or f.contains("OUR") or f.contains("initial fill")))
#if infeas.len() > 0 [The first #infeas.len() designs of the walk (marked † in @fig-bridge) break our
secretion ceiling: NREL's design makes 50 g/L of cellulase with only 6.6 g/L of cells, which implies
about #fx(float(infeas.at(0).flags.at(0).split(" ").at(2)), d: 0) mg/g/h. Their costs are shown for the walk only.]

#figure(image("../docs/figures/fig5_tornado.png", width: 92%),
  caption: [One-at-a-time sensitivity around the industry benchmark (BLG, 42 g/L), coloured by the
  evidence grade of each parameter's range. † marks an end moved to the feasibility boundary.]) <fig-tornado>

*Tornado* (@fig-tornado). Around the industry benchmark the largest swings are:
#for t in R.tornado.slice(0, 7) [
  + #lab(t.path): #usd(calc.min(t.msp_low, t.msp_high))–#usd(calc.max(t.msp_low, t.msp_high))
    (#if t.grade == "structural" [a convention] else [grade #t.grade])#if t.truncated_low or t.truncated_high [, one end truncated at the feasibility boundary]
]

What sets fermenter productivity leads: titer, production time and cell density decide how much
protein a vessel makes per hour and so how much capital each kg carries. Three points deserve
emphasis:
- *Yield matters through the ceiling, not the sugar bill.* At a fixed titer the product yield moves
  the price by #usd(swing("strain.Y_ps_g_g"), d: 1) (rank #torrank("strain.Y_ps_g_g")), because most
  sugar goes to making and maintaining cells. But it sets the sugar feed (and O#sub[2]) each gram of
  protein needs, and so the ceiling: at 72 h the ceiling is
  #R.ceiling_vs.Y_ps_g_g.values.zip(R.ceiling_vs.Y_ps_g_g.ceiling_72h).map(((y, c)) => fx(c, d: 0) + " g/L at " + fx(y, d: 2)).join(", ") g/g.
- *Vessel size.* 100–500 m³ moves the benchmark by #usd(swing("fermenter.volume_m3"), d: 1)
  (rank #torrank("fermenter.volume_m3")).
- *The structural choices.* The fermenter price basis (vendor quote against aseptic cell-culture
  vessels) moves it by #usd(swing("capital.fermenter_quote"), d: 1) (rank #torrank("capital.fermenter_quote")),
  and the accounting convention by #usd(swing("capital.basis"), d: 1) (rank #torrank("capital.basis")).
- *The minimum starting volume* does not appear: raising it above
  #fx(tor("fermenter.min_initial_fill").high, d: 2) makes the benchmark design infeasible, so its bar
  is truncated to almost nothing; @sec-q3 shows what it does to the ceiling.

Few strain-performance ranges are grade A; they rest on design values and company-reported averages,
because no public BLG or OVA fed-batch dataset reports titer, rate and yield together.

#figure(image("../docs/figures/fig7_montecarlo.png", width: 92%),
  caption: [Monte Carlo over each scenario's evidence ranges (triangular), feasible plants only; the
  black tick is the scenario's own value.]) <fig-mc>

*Monte Carlo* (@fig-mc). Over the evidence ranges the industry benchmark's median is
#usd(MC("industry/blg").p50, d: 0) for BLG (p10–p90 #usd(MC("industry/blg").p10, d: 0)–#usd(MC("industry/blg").p90, d: 0))
over feasible plants, and #usd(MC("industry/blg").p50_all, d: 0) (#usd(MC("industry/blg").p10_all, d: 0)–#usd(MC("industry/blg").p90_all, d: 0))
over all draws with a cost. #pct(MC("industry/blg").feasible_frac) of draws are feasible.
#let why = MC("industry/blg").infeasible_reasons
#let im = MC("industry/blg").input_means
The rest fail as follows: #why.pairs().map(((k, n)) => str(n) + " on " + k).join(", "). The
failing draws are those with many cells at the start of production
(#fx(im.at("strain.X_prod_g_L").infeasible, d: 0) against #fx(im.at("strain.X_prod_g_L").feasible, d: 0) g/L on
average) and fast growth in production (#fx(im.at("strain.mu_prod_per_h").infeasible, d: 4) against
#fx(im.at("strain.mu_prod_per_h").feasible, d: 4)/h): they need so much feed that the batch would
have to start below 30% full. The scenario values sit at these percentiles of their own feasible
distributions: industry BLG #fx(MC("industry/blg").base_percentile, d: 0), industry OVA
#fx(MC("industry/ova").base_percentile, d: 0), academic BLG #fx(MC("academic/blg").base_percentile, d: 0),
academic OVA #fx(MC("academic/ova").base_percentile, d: 0). For the academic strains the p10 is
#usd0(MC("academic/blg").p10) (BLG) and #usd0(MC("academic/ova").p10) (OVA).

== Q3: what must be true for \$10 and \$20 per kg <sec-q3>

#figure(image("../docs/figures/fig3_required_titer.png", width: 100%),
  caption: [Titer needed for a target price, against production time, at the base cell density. Grey:
  designs the fermenter cannot run with a 500 g/L glucose feed. Dotted: the ceiling with a 600 g/L
  feed.]) <fig-required>

#let reqcell(key, tg, i) = {
  let r = req(key, tg, i)
  if r.titer == none { [—] } else { fx(r.titer, d: 0) }
}
#let qpcell(key, tg, i) = {
  let r = req(key, tg, i)
  if r.titer == none { [—] } else { text(fill: rgb("#52514e"))[#fx(r.q_p_mg_g_h, d: 0)] }
}
#figure(
  table(
    columns: (2.1fr,) + R.required_t_prods.map(_ => 1fr),
    align: (left,) + R.required_t_prods.map(_ => right),
    table.header([*Production phase (h)*], ..R.required_t_prods.map(t => [*#t*])),
    hline,
    [Ceiling, 500 g/L feed (base)], ..R.titer_ceiling.blg.map(c => if c == none [—] else [#fx(c, d: 0)]),
    [Ceiling, 600 g/L feed], ..R.titer_ceiling_feed600.blg.map(c => if c == none [—] else [#fx(c, d: 0)]),
    hline,
    ..for tg in (10, 20, 50) {
      ([\$#tg/kg, price-anchored], ..range(R.required_t_prods.len()).map(i => reqcell("blg/humbird", tg, i)))
    },
    [#text(fill: rgb("#52514e"))[\$20/kg: implied q#sub[p] (mg/g/h)]], ..range(R.required_t_prods.len()).map(i => qpcell("blg/humbird", 20, i)),
    [\$10/kg, price-anchored, 600 g/L feed], ..range(R.required_t_prods.len()).map(i => { let r = R.required.at("blg/humbird/feed600").at("10").at(i); if r.titer == none [—] else [#fx(r.titer, d: 0)] }),
    [#text(fill: rgb("#52514e"))[#h(0.5em) implied q#sub[p] (mg/g/h)]], ..range(R.required_t_prods.len()).map(i => { let r = R.required.at("blg/humbird/feed600").at("10").at(i); if r.titer == none [—] else [#text(fill: rgb("#52514e"))[#fx(r.q_p_mg_g_h, d: 0)]] }),
    hline,
    ..for tg in (10, 20, 50) {
      ([\$#tg/kg, design-report], ..range(R.required_t_prods.len()).map(i => reqcell("blg/light", tg, i)))
    },
  ),
  caption: [BLG titer (g/L) needed for each target price at the base cell density
  (#fx(pv("strain.X_prod_g_L"), d: 0) g/L), searched only below the feasibility ceiling; grey rows give
  the specific productivity that titer implies (the base design runs at #fx(blg.design.q_p_mg_g_h, d: 1)).
  — means the target is not reachable at that production time (`results/analyses.json`, key `required`).],
) <tab-required>

@fig-required and @tab-required answer the inverse question at the base cell density:
#let r50 = R.required.at("blg/humbird").at("50").filter(r => r.titer != none).map(r => r.titer)
- *\$50/kg* needs #fx(calc.min(..r50), d: 0)–#fx(calc.max(..r50), d: 0) g/L depending on production
  time: #fx(calc.min(..r50) / S("academic/blg_li2026").design.titer, d: 1)–#fx(calc.max(..r50) / S("academic/blg_li2026").design.titer, d: 1)×
  the best public BLG titer on glucose.
- *\$20/kg* needs about #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0)–#fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L
  in 48–72 h with price-anchored capital (design-report:
  #fx(req("blg/light", 20, tpi(48)).titer, d: 0)–#fx(req("blg/light", 20, tpi(72)).titer, d: 0) g/L), a
  specific productivity of #fx(req("blg/humbird", 20, tpi(72)).q_p_mg_g_h, d: 0)–#fx(req("blg/humbird", 20, tpi(48)).q_p_mg_g_h, d: 0) mg/g/h.
#let r10h = R.required.at("blg/humbird").at("10").enumerate().filter(x => x.at(1).titer != none)
#let r10f = R.required.at("blg/humbird/feed600").at("10").enumerate().filter(x => x.at(1).titer != none)
#let r10l = R.required.at("blg/light").at("10").enumerate().filter(x => x.at(1).titer != none)
- *\$10/kg* #if r10h.len() == 0 [is not reachable with price-anchored capital at the base cell density
  and a 500 g/L feed: the titer it would need lies above the ceiling at every production time.] else [needs
  #fx(r10h.first().at(1).titer, d: 0)–#fx(r10h.last().at(1).titer, d: 0) g/L with price-anchored capital.]
  #if r10f.len() > 0 [With a 600 g/L feed it needs #fx(r10f.first().at(1).titer, d: 0)–#fx(r10f.last().at(1).titer, d: 0) g/L in
  #R.required_t_prods.at(r10f.first().at(0))–#R.required_t_prods.at(r10f.last().at(0)) h, at
  #fx(calc.min(..r10f.map(x => x.at(1).q_p_mg_g_h)), d: 0)–#fx(calc.max(..r10f.map(x => x.at(1).q_p_mg_g_h)), d: 0) mg/g/h.] else [Nor with a 600 g/L feed.]
  #if r10l.len() > 0 [With design-report capital it needs
  #fx(r10l.first().at(1).titer, d: 0)–#fx(r10l.last().at(1).titer, d: 0) g/L in
  #R.required_t_prods.at(r10l.first().at(0))–#R.required_t_prods.at(r10l.last().at(0)) h.] else [Nor is it reachable with design-report capital.]

*The gate is secretion.* Cell density is a free design choice, and at a fixed titer fewer cells cost
less; what fewer cells cannot escape is the specific productivity. @tab-best lets the model choose
cell density, production time and titer freely, with everything else at the base (yield, maintenance,
200 m³ vessels, 10 kt/yr, price-anchored capital), for four secretion ceilings. With secretion at
40 mg/g/h the cheapest BLG design costs #usd(BD(40).msp_ccf)/kg; at
#fx(BD(10).design.q_p_mg_g_h, d: 0) mg/g/h it costs #usd(BD(10).msp_ccf). The base design runs at
#fx(blg.design.q_p_mg_g_h, d: 1) mg/g/h, Intelligen's design value; the best public BLG fed-batch implies
about 1 (Yao et al. 2026: 13.88 g/L in 108 h at roughly 120 g/L cells). Fungal cellulase processes make
0.2–0.4 g protein per litre per hour (Ellilä et al. 2017), which at the 20–50 g/L of cells such
processes run is roughly 5–20 mg/g/h (our arithmetic), for native enzymes, not animal proteins.

#figure(
  table(
    columns: (1.4fr, 1fr, 1fr, 1fr, 1fr, 2.2fr),
    align: (left, right, right, right, right, left),
    table.header([*Secretion ceiling (mg/g/h)*], [*\$/kg BLG*], [*Cells (g/L)*], [*Production (h)*], [*Titer (g/L)*], [*Limits that bind*]),
    hline,
    ..for q in (40, 20, 10, 5, 2.1) {
      let d = BD(q)
      if d == none { ([#q], [—], [], [], [], []) } else {
        ([#q#if q == 2.1 [ (best demonstrated)]], [#usd(d.msp_ccf)], [#fx(d.X_prod, d: 0)], [#fx(d.t_prod, d: 0)], [#fx(d.titer, d: 0)], [#d.binding.join(", ")])
      }
    },
  ),
  caption: [What process design alone can do: the cheapest BLG design with base biology, vessel,
  scale and price-anchored capital, when cell density, production time and titer are free, for five
  secretion ceilings (a coarse search; review SC-1). 2.1 mg/g/h is the best secretion rate we found
  demonstrated in a *K. phaffii* glucose fed-batch (Prielhofer et al. 2018).],
) <tab-best>

*How firm is the ceiling?* It is a design ceiling, not a law of physics (@tab-ceiling). In the base it
comes from the vessel's volume: the minimum starting volume (30%, the lowest start in a published
design), the glucose feed (500 g/L, Intelligen's) and the cell density at the start of production
(107 g/L) are all design choices. A 600 g/L feed lifts the 72 h ceiling to
#fx(CL("glucose feed 600 g/L", 72).ceiling, d: 0) g/L (#CL("glucose feed 600 g/L", 72).limit); 80 g/L of
cells lifts it to #fx(CL("80 g/L cells at the start of production", 72).ceiling, d: 0) g/L; a 20% start
to #fx(CL("minimum fill 0.20", 72).ceiling, d: 0) g/L, still set by the #CL("minimum fill 0.20", 72).limit.
Only with no volume limit at all does another limit take over:
#CL("no minimum fill", 72).limit at #fx(CL("no minimum fill", 72).ceiling, d: 0) g/L. The other way, a
35% start brings the 72 h ceiling down to #if CL("minimum fill 0.35", 72).ceiling == none [nothing feasible] else [#fx(CL("minimum fill 0.35", 72).ceiling, d: 0) g/L],
and at 40% #if CL("minimum fill 0.40", 72).ceiling == none [no titer is feasible at the base cell density] else [#fx(CL("minimum fill 0.40", 72).ceiling, d: 0) g/L]
(NREL's design starts at 50%). The ceiling also rises with the product yield (@sec-q2) and with lower
production-phase maintenance: at 72 h it is
#R.ceiling_vs.m_s_prod_g_g_h.values.zip(R.ceiling_vs.m_s_prod_g_g_h.ceiling_72h).map(((m, c)) => if c == none { "none at " + str(m) } else { fx(c, d: 0) + " g/L at " + str(m) }).join(", ") g/g/h.

#figure(
  table(
    columns: (2.6fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right),
    table.header([*Design choice*], [*36 h*], [*72 h*], [*120 h*]),
    hline,
    ..for (case, rows) in R.ceiling_limits {
      ([#case], ..rows.map(r => if r.ceiling == none [—] else [#fx(r.ceiling, d: 0) g/L #text(size: 7.5pt, fill: rgb("#52514e"))[(#r.limit)]]))
    },
  ),
  caption: [BLG titer ceiling (g/L) by production time, and the limit that fails just above it. Base:
  107 g/L cells, a 30% minimum start, a 500 g/L glucose feed, and an O#sub[2] cap of 200 mol/m³/h per
  m³ of cell-free liquid.],
) <tab-ceiling>

== Q4: the physical-limit best case <sec-q4>

#figure(image("../docs/figures/fig4_breakdown.png", width: 100%),
  caption: [Cost structure from today's benchmarks to the physical-limit best case. The best academic
  strains are off this scale.]) <fig-breakdown>

The search (@fig-breakdown) finds the cheapest feasible design once every lever listed in
@sec-scen is at its assumed best. For BLG it has #fx(PL("blg/humbird").X_prod, d: 0) g/L cells,
a #fx(PL("blg/humbird").t_prod, d: 0) h production phase and #fx(PL("blg/humbird").titer, d: 0) g/L, at a
specific productivity of #fx(PL("blg/humbird").design.q_p_mg_g_h, d: 0) mg/g/h. The limits active there
are #PL("blg/humbird").binding.join(", ").

It costs #usd(PL("blg/humbird").msp_ccf)/kg BLG with price-anchored capital and
#usd(PL("blg/light").msp_ccf) with design-report capital; for OVA #usd(PL("ova/humbird").msp_ccf) and
#usd(PL("ova/light").msp_ccf).
- *It is set by an assumed secretion rate.* The binding biological limit is the
  #fx(pv("strain.q_p_max_mg_g_h"), d: 0) mg/g/h ceiling, a judgment (grade D) about
  #fx(pv("strain.q_p_max_mg_g_h") / blg.design.q_p_mg_g_h, d: 0)× the base design and above any
  published *K. phaffii* value. @tab-plq shows the case at other ceilings.
- *Capital still dominates:* #pct(capshare(PL("blg/humbird"))) of the BLG case. Glucose
  (#usd(PL("blg/humbird").per_kg.glucose, d: 2)) is the largest non-capital item.
- *Engineering levers are part of it.* 400 m³ vessels, 100 kt/yr, contract sugar and the 600 g/L feed
  are not biology. With the base 500 g/L feed the BLG case costs
  #usd(R.physical_limit.at("blg/humbird/feed_500").msp_ccf)\; with aseptic cell-culture vessels,
  #usd(R.physical_limit.at("blg/humbird/aseptic").msp_ccf).
- *OVA and the 50 g/L question.* If Intelligen's 50 g/L were a real solubility limit at fermentation pH,
  the OVA case would cost #usd(PL("ova/humbird/solubility_50").msp_ccf) instead of #usd(PL("ova/humbird").msp_ccf).

#figure(
  table(
    columns: (1.6fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right),
    table.header([*Secretion ceiling (mg/g/h)*], [*\$/kg BLG*], [*Cells (g/L)*], [*Production (h)*], [*Titer (g/L)*]),
    hline,
    ..for q in (2.1, 5, 10, 20, 40, 120) {
      let d = if q == 40 { PL("blg/humbird") } else { QP(q) }
      if d == none { ([#q], [—], [], [], []) } else {
        ([#q#if q == 40 [ (assumed)] else if q == 120 [ (NREL's design, implied)] else if q == 2.1 [ (best demonstrated)]], [#usd(d.msp_ccf)], [#fx(d.X_prod, d: 0)], [#fx(d.t_prod, d: 0)], [#fx(d.titer, d: 0)])
      }
    },
  ),
  caption: [The BLG physical-limit case at other secretion ceilings (price-anchored capital; the
  sensitivities use a coarser search). The base design runs at #fx(blg.design.q_p_mg_g_h, d: 1) mg/g/h.],
) <tab-plq>

The case is not a forecast and not a lower bound: design-report accounting, continuous operation or
further relaxed design choices would all go lower. It is what the model gives once every assumed
limit is at its best at the same time. Its yield sits at 95% of an energetic ceiling that leaves out
transport, secretion and turnover costs. Its O#sub[2] limit assumes water-like broth at
#fx(PL("blg/humbird").X_prod, d: 0) g/L cells and #fx(PL("blg/humbird").titer, d: 0) g/L of dissolved
protein, where viscosity and foam would lower k#sub[L]a. And its heat removal (up to
#fx(pv("fermenter.heat_removal_max_kW_m3"), d: 0)–40 kW/m³, i.e. about 16 MW per 400 m³ vessel) needs
external heat-exchange loops that are not costed. The BLG case is
#where(PL("blg/humbird").msp_ccf, inc.whey.band) the 2015–2025 whey band; the OVA case is
#where(PL("ova/humbird").msp_ccf, inc.egg.band) the egg-white band.

== Q5: claimed titers against the fermenter's limits <sec-q5>

#figure(
  table(
    columns: (2.4fr, 0.6fr, 1fr, 0.9fr, 0.9fr, 0.9fr, 0.8fr, 0.9fr),
    align: (left, right, left, right, right, right, right, right),
    table.header([*Claim or benchmark*], [*Titer*], [*Modelled as*], [*At its own time: \$/kg*],
      [*Design-report*], [*Shortest feasible time*], [*q#sub[p] there*], [*\$/kg there*]),
    hline,
    ..for c in R.claims {
      ([#c.label], [#fx(c.titer, d: 0) g/L],
       [#(if c.host == "treesei" [_T. reesei_] else [_K. phaffii_]), #fx(c.X_prod, d: 0) g/L cells],
       [#(if c.feasible_own [#usd(c.msp_own_humbird) (#fx(c.t_prod_own, d: 0) h)] else [infeasible at #fx(c.t_prod_own, d: 0) h])],
       [#(if c.feasible_own [#usd(c.msp_own_light)] else [—])],
       [#(if c.t_prod_min == none [not reachable] else [#fx(c.t_prod_min, d: 0) h])],
       [#(if c.at("q_p_mg_g_h", default: none) == none [—] else [#fx(c.q_p_mg_g_h, d: 0)])],
       [#usd(c.at("msp_humbird", default: none))])
    },
  ),
  caption: [Claimed and benchmark titers in a 200 m³ vessel: the cost at the claim's own production
  time (Behm's design: 120 h; otherwise 72 h), and the shortest production phase in which the titer is
  feasible (O#sub[2] transfer, heat removal, minimum starting volume, 40 mg/g/h secretion ceiling), with
  the specific productivity and price-anchored cost there. The shortest-time columns are a best case:
  secretion runs at or near its ceiling. The Onego figure is a platform claim for an unnamed protein,
  tested as OVA.],
) <tab-claims>

#let reach = R.claims.filter(c => c.t_prod_min != none)
#let noreach = R.claims.filter(c => c.t_prod_min == none)
#let gfi42 = R.claims.find(c => c.titer == 42)
Of the #R.claims.len() claims and benchmarks, #reach.len() are feasible if the production phase is
right (@tab-claims). The price of a high titer is time or secretion rate: at its own 72 h the 42 g/L
average costs #usd(gfi42.at("msp_own_humbird", default: none)), the industry benchmark of @sec-q1; squeezed into the
shortest feasible production phase it costs #usd(gfi42.at("msp_humbird", default: none)), but only by secreting
#fx(gfi42.at("q_p_mg_g_h", default: 0), d: 0) mg/g/h. A claimed titer alone therefore does not settle the cost. The
check is physical; whether a strain can sustain the implied productivity is a separate, biological
question.
#if noreach.len() > 0 [
  #noreach.map(c => c.label).join("; ") cannot be reached at any production phase up to 20 days in our
  model: either the O#sub[2] demand exceeds what the broth can take up, or the batch would have to start
  below 30% of the vessel because the feed fills it first. Such claims need better O#sub[2] transfer
  than our assumptions (for *T. reesei*, a k#sub[L]a half that of yeast broth, grade D), a denser feed,
  or a different process (continuous, repeated fed-batch or cell recycle), none of which is modelled here.
]

== Q6: scale and siting <sec-q6>

#figure(image("../docs/figures/fig6_scale.png", width: 82%),
  caption: [Industry-benchmark BLG against plant output, US Midwest and north-west Europe, both capital conventions.]) <fig-scale>

*Scale* (@fig-scale). Going from 1 to 10 kt/yr cuts the price by
#usd(R.scale.curves.at("US, price-anchored").at(0) - R.scale.curves.at("US, price-anchored").at(3)), and going
from 10 to 100 kt/yr saves a further
#usd(R.scale.curves.at("US, price-anchored").at(3) - R.scale.curves.at("US, price-anchored").at(6)). Beyond about
10 kt/yr the plant adds 200 m³ fermenters rather than larger ones, so only the downstream train and
utilities keep scaling; larger vessels are a separate lever (@sec-q2).

*Siting.* A Netherlands plant costs #usd(POL.at("EU base") - POL.at("US base"))/kg more than one in
the US Midwest (base BLG). One at a time, US-level inputs would remove:
- glucose (\$#fx(pveu("utilities.glucose_usd_kg"), d: 2) against \$#fx(pv("utilities.glucose_usd_kg"), d: 2)/kg):
  #usd(POL.at("EU base") - POL.at("EU with US glucose price"))\;
- electricity and gas (\$#fx(pveu("utilities.electricity_usd_kWh"), d: 3) against
  \$#fx(pv("utilities.electricity_usd_kWh"), d: 3)/kWh; \$#fx(pveu("utilities.natural_gas_usd_GJ"), d: 1) against
  \$#fx(pv("utilities.natural_gas_usd_GJ"), d: 1)/GJ): #usd(POL.at("EU base") - POL.at("EU with US energy prices"))\;
- construction cost (#fx(pveu("capital.location_factor"), d: 2)×): #usd(POL.at("EU base") - POL.at("EU with US construction cost"))\;
- wages: #if calc.abs(POL.at("EU base") - POL.at("EU with US wages")) < 0.05 [nothing (Dutch and Iowa operator pay are within a few per cent)] else [#usd(POL.at("EU base") - POL.at("EU with US wages"))];
- spent-cell disposal (anaerobic digestion in the EU against US landfill): #dusd(POL.at("EU base") - POL.at("EU with US spent-cell disposal fee")), i.e. the EU is cheaper here;
- water and wastewater: #dusd(POL.at("EU base") - POL.at("EU with US water prices")).

The one-at-a-time effects need not add up to the gap exactly, because the inputs interact.

== Q7: milk and egg equivalents <sec-equiv>

#let beM = EQ.break_even_titer_72h.milk
#let beE = EQ.break_even_titer_72h.egg
#let milkfarm = EQ.sources.milk.prices.at("US farm milk (all-milk price)")
#let eggwh = EQ.sources.egg.prices.at("US wholesale eggs (New York, Grade A large)")
#let lastv(ser) = ser.at(ser.keys().sorted().last())
#figure(image("../docs/figures/fig8_equivalents.png", width: 100%),
  caption: [The cost of replacing the protein of a litre of milk (left) and the egg-white protein of an
  egg (right) with PF protein, against titer (72 h production, price-anchored capital), beside milk and
  egg prices in 2025 dollars.]) <fig-equiv>

A litre of cow's milk holds 33.7 g of protein, 3.3 g of it BLG; a large egg holds 3.64 g of egg-white
protein, 1.96 g of it OVA (`data/evidence/milk_egg.yaml`). At the base cost, the PF protein needed to
replace all the protein of a litre of milk costs
#usd(EQ.cases.milk.base.all_protein_per_unit, d: 2), against #usd(lastv(milkfarm), d: 2) for the litre
at the US farm gate in 2025 and #usd(lastv(EQ.sources.milk.prices.at("US retail whole milk")), d: 2) at
retail. Replacing one egg's white costs #usd(EQ.cases.egg.base.all_protein_per_unit, d: 3), against
#usd(lastv(eggwh), d: 3) per egg wholesale in 2025, a year of avian-influenza prices
(#usd(calc.min(..eggwh.values()), d: 3)–#usd(calc.max(..eggwh.values()), d: 3) over 2015–2025).

Dividing a source's price by its protein gives the price per kg of protein at which PF would match it:
US farm milk sold its protein at #usd(calc.min(..EQ.sources.milk.protein_equivalent.at("US farm milk (all-milk price)").values()), d: 0)–#usd(calc.max(..EQ.sources.milk.protein_equivalent.at("US farm milk (all-milk price)").values()), d: 0)/kg
in 2015–2025, and wholesale eggs their egg-white protein at
#usd(calc.min(..EQ.sources.egg.protein_equivalent.at("US wholesale eggs (New York, Grade A large)").values()), d: 0)–#usd(calc.max(..EQ.sources.egg.protein_equivalent.at("US wholesale eggs (New York, Grade A large)").values()), d: 0)/kg.
With a 72 h production phase (ceiling #fx(beM.ceiling, d: 0) g/L), BLG matches the 2025 farm-milk
protein price at
#{ let r = beM.rows.at("US farm milk (all-milk price) [2025]"); if r.titer == none [no feasible titer] else [#fx(r.titer, d: 0) g/L] },
and OVA matches the lowest egg-white protein price of the decade at
#{ let r = beE.rows.at("US wholesale eggs (New York, Grade A large) [band low]"); if r.titer == none [no feasible titer] else [#fx(r.titer, d: 0) g/L] }.

These are upper bounds on what the protein is worth: charging the whole price of milk or eggs to
their protein makes them look dearer per gram than they are, since fat and lactose carry much of the
milk price and the yolk part of the egg's. Bought as the incumbent ingredient, the same protein is
much cheaper: the white of one egg, as dried egg white, cost
#usd(calc.min(..EQ.ingredient_per_unit.dried_egg_white_per_egg.values()), d: 3)–#usd(calc.max(..EQ.ingredient_per_unit.dried_egg_white_per_egg.values()), d: 3)
in 2015–2025. Whey is a by-product of cheese: the whey protein of a litre of milk
(#fx(EQ.ingredient_per_unit.whey_g_per_L, d: 1) g) at WPC80/WPI prices was worth
#pct(calc.min(..EQ.ingredient_per_unit.whey_share_of_farm_milk.values()))–#pct(calc.max(..EQ.ingredient_per_unit.whey_share_of_farm_milk.values()))
of the US farm milk price in the same year, so replacing whey protein cuts milk output far less than
the "litre of milk" framing suggests. For animal welfare, egg white is the stronger lever: per kg of
target protein it involves roughly 50–60 times more animal-years than whey BLG (about 0.6 kg OVA per
hen-year against about 35 kg BLG per cow-year). These last two figures are our order-of-magnitude
arithmetic, not model outputs.

== Q8: a high-value contrast, lactoferrin <sec-lf>

Lactoferrin, an iron-binding milk protein, sells as a supplement and infant-formula ingredient at
tens of times the price of whey (#fx(LF.reported_prices.band.at(0) / inc.whey.band.at(1), d: 0)–#fx(LF.reported_prices.band.at(1) / inc.whey.band.at(0), d: 0)×
across the two price ranges). Two recombinant bovine lactoferrins made in *K. phaffii* without
methanol have FDA "no questions" letters (GRN 1219 TurtleTree, 2025; GRN 1284 All G, 2026). We model
it at 250 t/yr (Intelligen's design makes 251 t/yr of powder; the world market is roughly 0.3–1.6 kt/yr,
and sources disagree by five times), with the dairy downstream route: microfiltration, cation exchange,
UF/DF and spray drying to #pct(pv("dsp.cex_target_frac_dry")) lactoferrin. The chromatography step
uses a binding capacity of #pv("dsp.cex_dbc_g_L") g/L of resin and #pv("dsp.cex_cv_per_cycle") column
volumes of buffer per cycle (EVERY patent), elution at 1 M NaCl, #pct(pv("dsp.cex_recovery"), d: 1)
step recovery, and resin at \$#thou(pv("dsp.cex_resin_usd_L"))/L (Petrides) lasting
#thou(pv("dsp.cex_resin_life_cycles")) cycles (industrial lactoferrin columns, Pires et al. 2025). The
column is loaded with dilute microfiltered broth, #fx(LFC("lf/humbird").design.cex_load_cv, d: 0) column
volumes per cycle, so a cycle takes #fx(LFC("lf/humbird").design.cex_cycle_h, d: 1) h at
#pv("dsp.cex_flow_cv_per_h") column volumes per hour, the flow of Intelligen's design (500 cm/h through a
25 cm bed of a fast-flow agarose resin; version 2.1 guessed 5). One guess (grade E) remains: the column
hardware per litre of resin.

#figure(image("../docs/figures/fig9_lactoferrin.png", width: 82%),
  caption: [Lactoferrin cost against titer, the reported dairy lactoferrin price range (2025 dollars),
  and Intelligen's own unit production costs for its 10 g/L design, with and without chromatography
  (costs of production, not selling prices; @tab-lf-rec).]) <fig-lf>

#figure(
  table(
    columns: (2.6fr, 0.8fr, 1fr, 1fr),
    align: (left, right, right, right),
    table.header([*Case (250 t/yr)*], [*Titer (g/L)*], [*Price-anchored*], [*Design-report*]),
    hline,
    [Design titer, cation exchange (Intelligen's design)], [#fx(LFC("lf/humbird").design.titer, d: 0)],
      [#usd0(LFC("lf/humbird").msp_ccf)], [#usd0(LFC("lf/light").msp_ccf)],
    [Best public methanol-free titer (porcine LF, Yen 2024)], [#fx(LFC("lf_academic/humbird").design.titer, d: 1)],
      [#usd0(LFC("lf_academic/humbird").msp_ccf)], [#usd0(LFC("lf_academic/light").msp_ccf)],
    [Design titer, UF/DF only (optimistic)], [#fx(LFC("lf_ufdf_only/humbird").design.titer, d: 0)],
      [#usd0(LFC("lf_ufdf_only/humbird").msp_ccf)], [#usd0(LFC("lf_ufdf_only/light").msp_ccf)],
    hline,
    [Intelligen's model, cost of production, UF/DF only (case a)], [10], table.cell(colspan: 2)[#usd0(IA.value_money_year) per kg],
    [Intelligen's model, cost of production, cation exchange (case b)], [10], table.cell(colspan: 2)[#usd0(IB.value_money_year) per kg],
    [Dairy lactoferrin, reported 2013–2025 (grade C; 2025 \$)], [], table.cell(colspan: 2)[#usd0(LF.reported_prices.band.at(0))–#usd0(LF.reported_prices.band.at(1)) per kg],
  ),
  caption: [Lactoferrin, \$/kg lactoferrin (2025). Resin life is the largest downstream lever: at 125
  cycles (biopharma practice) the design case costs #usd0(LF.resin.at("dsp.cex_resin_life_cycles=125")).
  Scale: #R.scale_lf.outputs.zip(R.scale_lf.curves.at("US, price-anchored")).map(((x, m)) => usd0(m) + " at " + str(x) + " t/yr").join(", ").],
) <tab-lf>

#let recrow(label, k, ik) = ([#label], [#usd(ipk(IA, ik), d: 1)], [#usd(REC("lf_intelligen_a").per_kg.at(k), d: 1)],
  [#usd(ipk(IB, ik), d: 1)], [#usd(REC("lf_intelligen_b").per_kg.at(k), d: 1)])
#figure(
  table(
    columns: (2.2fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right),
    table.header([*\$/kg lactoferrin (2025)*], [*Intelligen a*], [*Ours, their design a*], [*Intelligen b*], [*Ours, their design b*]),
    hline,
    ..recrow("Raw materials", "raw materials", "raw_materials"),
    ..recrow("Labour", "labour", "labour"),
    ..recrow("Facility (maintenance, insurance, depreciation)", "facility", "facility"),
    ..recrow("Laboratory, QC and QA", "lab/QC/QA", "lab_qc_qa"),
    ..recrow("Consumables (resin, membranes)", "consumables", "consumables"),
    ..recrow("Waste treatment", "waste", "waste"),
    ..recrow("Utilities", "utilities", "utilities"),
    hline,
    [*Cost of production*], [*#usd(IA.value_money_year, d: 1)*], [*#usd(REC("lf_intelligen_a").cop, d: 1)*],
      [*#usd(IB.value_money_year, d: 1)*], [*#usd(REC("lf_intelligen_b").cop, d: 1)*],
    [Our base design (@tab-lf)], [], [#usd(REC("lf_ufdf_only").cop, d: 1)], [], [#usd(REC("lf").cop, d: 1)],
    [Total capital investment], [#musd(IA.values.tci_usd * IA.deflator)], [#musd(REC("lf_intelligen_a").tci)],
      [#musd(IB.values.tci_usd * IB.deflator)], [#musd(REC("lf_intelligen_b").tci)],
  ),
  caption: [Intelligen's lactoferrin model against ours, in SuperPro's operating-cost categories.
  Intelligen's figures are its 2024 costs (Tables 2–5 of the report) per kg of lactoferrin, deflated
  to 2025; "ours, their design" runs our model with the design inputs their report states (scale, six
  100 m³ fermenters, diavolumes, column flow, loading and buffers, step recovery, resin at \$1,000/L
  lasting 150 cycles, electricity at \$0.10/kWh) and our own unit prices. Our facility line is
  maintenance, insurance and ten-year depreciation. `data/pf/scenarios/lactoferrin.yaml`, variants
  `lf_intelligen_a` and `lf_intelligen_b`; review L.],
) <tab-lf-rec>

At the design titer PF lactoferrin costs #usd0(LFC("lf/light").msp_ccf)–#usd0(LFC("lf/humbird").msp_ccf)
per kg (design-report to price-anchored capital), #where(LFC("lf/humbird").msp_ccf, LF.reported_prices.band) the
reported range for dairy lactoferrin in 2025 dollars. That range comes from reports and trade press,
partly from a PF-lactoferrin seller (TurtleTree, 2023), and the price is volatile (it fell to about
\$200/kg nominal in the 2016 glut).

*Against Intelligen's own model.* Intelligen published the design our case takes its titer from
(Da Gama Ferreira et al. 2026): six 100 m³ fermenters, glycerol growth and methanol induction to
10 g/L, and two downstream routes. Its unit production costs, per kg of lactoferrin in 2025 dollars,
are #usd0(IA.value_money_year) without chromatography and #usd0(IB.value_money_year) with cation
exchange. They include depreciation and no return on capital, so they compare with our cost of
production, #usd0(REC("lf_ufdf_only").cop) and #usd0(REC("lf").cop): theirs are
#fx(IA.value_money_year / REC("lf_ufdf_only").cop, d: 1)× and #fx(IB.value_money_year / REC("lf").cop, d: 1)×
ours. Their design inputs explain a small part of the gap. With their output, vessels, diavolumes, column
flow and loading, buffers, step recovery, resin price and life, and electricity price, our cost of
production becomes #usd0(REC("lf_intelligen_a").cop) and #usd0(REC("lf_intelligen_b").cop)
(@tab-lf-rec); the largest single input is their short resin life (150 cycles against our 1,000).
The rest is their unit costs, category by category: raw materials (glycerol at about \$1.8/kg, and a
part of the line that the report does not itemise), capital (their investment is
#fx(IB.values.tci_usd * IB.deflator / REC("lf_intelligen_b").tci, d: 1)× ours for the same design; their
equipment list is not published), labour, membranes, utilities, and a quality-control line that we do
not have. We keep our sourced prices; theirs are SuperPro inputs without a stated basis. Our cost
sits #where(LFC("lf/humbird").msp_ccf, LF.reported_prices.band) the reported price range and Intelligen's
#where(IB.value_money_year, LF.reported_prices.band) it, but only at the design titer: at the best public
methanol-free titer the cost is #usd0(LFC("lf_academic/humbird").msp_ccf)/kg. No PF lactoferrin price
has been disclosed, so this is a cost comparison only. The contrast with BLG is the point: the same
fermentation and accounting that leave the base BLG #where(blg.msp_ccf, inc.whey.band) the whey band put
lactoferrin #where(LFC("lf/humbird").msp_ccf, LF.reported_prices.band) its incumbent's range at a design
titer, because that incumbent is scarce rather than a by-product.

// ================================================================ 5
= Discussion

== Answers, in brief

- *Q1.* Today's public strains make BLG and OVA at #usd0(S("academic/blg").msp_ccf) and
  #usd0(S("academic/ova").msp_ccf) per kg: not competitive. The titer private cost models assume gives
  #usd(S("industry/blg").msp_ccf) (BLG) and #usd(S("industry/ova").msp_ccf) (OVA), or
  #usd(S("industry/blg/light").msp_ccf) and #usd(S("industry/ova/light").msp_ccf) with design-report capital.
  Against 2015–2025 prices, BLG is then #where(S("industry/blg").msp_ccf, inc.whey.band) the whey band
  (#where(S("industry/blg/light").msp_ccf, inc.whey.band) it with design-report capital) and OVA
  #where(S("industry/ova").msp_ccf, inc.egg.band) the egg-white band.
- *Q2.* Fermenter productivity (protein per hour of vessel time) drives the cost, then the capital
  basis (vessel prices and fixed-cost rule); sugar and energy prices come second. The product yield
  acts mainly through the feasibility ceiling. The strain parameters are the weakest evidence: design
  values (B) and survey averages (C).
- *Q3.* With price-anchored capital, \$20/kg needs #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0) g/L
  at 48 h or #fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L at 72 h at the base cell density. What
  \$10/kg needs above all is secretion: with today's biology and capital, process design alone reaches
  #usd(BD(40).msp_ccf) at 40 mg/g/h and #usd(BD(10).msp_ccf) at 10.
- *Q4.* The physical-limit best case is #usd(PL("blg/humbird").msp_ccf) (BLG) and
  #usd(PL("ova/humbird").msp_ccf) (OVA) per kg, bound by #PL("blg/humbird").binding.join(", "); at a
  secretion ceiling of 10 mg/g/h the BLG case is #usd(QP(10).msp_ccf).
- *Q5.* #reach.len() of #R.claims.len() claimed titers are feasible in our fed-batch model, some only with
  long production phases or secretion near the ceiling.
- *Q6.* Scale matters up to about 10 kt/yr. EU siting adds about #usd(POL.at("EU base") - POL.at("US base"), d: 1)/kg.
- *Q7.* The base BLG replaces the protein of a litre of milk for #usd(EQ.cases.milk.base.all_protein_per_unit, d: 2),
  while the litre costs #usd(lastv(milkfarm), d: 2) at the farm gate; bought as WPC80/WPI the same whey
  protein is a fraction of that.
- *Q8.* At a design titer, PF lactoferrin costs #usd0(LFC("lf/humbird").msp_ccf)/kg,
  #where(LFC("lf/humbird").msp_ccf, LF.reported_prices.band) the reported range for dairy lactoferrin;
  Intelligen's own model costs #fx(IB.value_money_year / REC("lf").cop, d: 1)× ours to produce.

== Why published PF costs are lower

Published PF cost estimates for food proteins span roughly \$12–39/kg: GFI Europe and Arthur D.
Little (2025) give \$24–33/kg for their "P1" molecules today and \$12/kg for α-lactalbumin after
improvements; Intelligen (2025) \$39/kg for an OVA isolate at 1 kt/yr. Of the designs we can rebuild
from their own inputs, Intelligen's OVA comes within
#sgn(calrel("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)")) of our model once recast into
our capital charge; NREL's cellulase and Voutilainen's recombinant case come out
#pubratio×
lower. With vendor-quote fermenters our capital matches theirs; the gap is mostly accounting:
fixed costs of 1.5–2% of capital a year instead of Humbird's 9%, and lighter capital charges.
Intelligen's lactoferrin model runs the other way: its cost of production is
#fx(IB.value_money_year / REC("lf").cop, d: 1)× ours, through its unit prices for raw materials,
labour and consumables and a capital estimate #fx(IB.values.tci_usd * IB.deflator / REC("lf_intelligen_b").tci, d: 1)×
ours for the same design (@tab-lf-rec). Published costs differ from ours in both directions, for
reasons that can be traced line by line.

Neither convention is "correct". Humbird's reproduces the cost of one fermented commodity in his
own workbook; the design-report one matches how process-design studies cost greenfield enzyme
plants. We read our base as a central estimate on Humbird's method and design-report capital as an
optimistic one, not as a confidence interval.

== For funders

In order of expected cost reduction per unit of evidence gained (our judgment):
1. *Secretion rate without growth.* How much BLG or OVA a strain secretes per gram of cells per hour
   when it barely grows, over a production phase of two to five days at 1–10 m³. It sets both today's
   cost and the best case; the one near-zero-growth study we found saw secretion fall with growth, and
   every compiled glucose process secretes fastest at 0.1–0.2/h (Looser et al. 2015; Prielhofer et al. 2018).
2. *Public fed-batch data.* Titer, productivity and yield measured *together* for BLG and OVA; no
   public dataset reports all three, and the product yield is currently derived, not measured.
3. *The design ceiling.* The workable starting volume, the most concentrated feed and O#sub[2] transfer
   at production scale and cell density move the titer ceiling itself.
4. *Real capital and fixed costs.* Published capital, staffing and running costs of recent PF plants
   (for example Liberation Labs' 600 m³ Richmond plant) would settle the fermenter price basis and the
   fixed-cost rule.
5. *Downstream data.* Diafiltration flux at scale (one patent value, 5 L/m²/h, sizes most of the
   membrane area) and dryer-feed solids for PF proteins.

#let beats = wheyobs.filter(x => x >= S("industry/blg/light").msp_ccf).len()
On the evidence here, PF BLG at the titer private cost models assume
#if S("industry/blg").msp_ccf < inc.whey.spot.at(0).usd_kg_protein [would undercut whey in a spike year such as 2026.] else [would not undercut even the 2026 whey peak.]
With design-report capital (#usd(S("industry/blg/light").msp_ccf)) it would have undercut whey in
#beats of the #wheyobs.len() annual export prices of 2015–2025; with price-anchored capital
(#usd(S("industry/blg").msp_ccf)) in #wheyobs.filter(x => x >= S("industry/blg").msp_ccf).len(). High-value
proteins such as lactoferrin cost less than most reported incumbent prices at a design titer. OVA's
position against egg white depends on the year, because egg-white prices swing more than whey's.

#check[A judgment, not a model output, written by the AI assistant and not yet endorsed by the
author (please revise): the probability that a PF plant built with 2026 technology makes BLG below
\$10/kg protein is about 0.15, with low confidence (unchanged from version 2: the cheaper vessels
raise it, the secretion requirement lowers it). The model reaches \$10 only if cells secrete several
times faster than any published *K. phaffii* process, sustained over days, or with the lighter
design-report accounting and high titers together.]

== For EU policy

At Dutch sugar, energy, wage and construction prices the base BLG plant costs
#usd(POL.at("EU base") - POL.at("US base"))/kg more than in the US Midwest. Cheaper capital is a large
lever: a capital charge at 4% over 20 years instead of 7.5% over 10 cuts
#usd(POL.at("EU base") - POL.at("EU, capital at 4%/20 yr")) from the EU cost; of that, a 20-year
recovery alone cuts #usd(POL.at("EU base") - POL.at("EU, capital at 7.5%/20 yr")) and a 4% rate alone
#usd(POL.at("EU base") - POL.at("EU, capital at 4%/10 yr")). US-level glucose would remove
#usd(POL.at("EU base") - POL.at("EU with US glucose price")) and US-level energy
#usd(POL.at("EU base") - POL.at("EU with US energy prices")). These are cost effects on one plant; the
model says nothing about which instruments would deliver them.

== What would change these conclusions

- A BLG or OVA strain that secretes ≥10 mg/g/h over days at near-zero growth, or evidence that it
  cannot, would move both today's cost and the best case more than any other single result.
- A peer-reviewed BLG or OVA fed-batch at ≥40 g/L in ≤48 h with a measured yield would test the
  derived product yield and the ceiling.
- The ceiling rests on design choices: a 30% minimum starting volume, a 500 g/L glucose feed and
  107 g/L of cells. Industrial practice with lower starts, denser feeds or fewer cells lifts it; then
  secretion and O#sub[2] transfer set it.
- Published capital and running costs of recent PF plants would settle the fermenter price basis and
  the fixed-cost rule.
- Measured OVA solubility at pH 5, and protease control for OVA in *T. reesei*.

// ================================================================ 6
= Limitations <sec-limits>

- *Strain parameters.* Few are grade A. The product yield is derived from a design's lumped
  stoichiometry, not measured; specific productivities are design values or survey averages, and
  the base production phase assumes secretion without growth (@sec-ferm).
  #n_unverified titer rows in `data/titers.csv` are not yet verified in full text.
- *One carbon source.* Methanol-induced and ethanol-fed production phases are priced as glucose; for
  ethanol this understates O#sub[2] and heat.
- *The feasibility limits are design choices*: the minimum starting volume (30%), the feed
  concentration (500 g/L glucose) and the cell density, which together set the base ceiling; the
  O#sub[2] cap and its basis (200 mol/m³/h per m³ of cell-free liquid); the heat-removal ceiling
  (25 kW/m³, grade D); and the secretion ceiling (40 mg/g/h), a judgment.
- *Directions of the simplifications.* k#sub[L]a ignores viscosity and foam (optimistic at high cell
  density and titer); specific productivity is constant for up to 120 h (optimistic for long
  production phases); no product is made during growth (conservative for constitutive promoters);
  the energetic ceiling leaves out transport, secretion and turnover (optimistic).
- *OVA* at fermentation pH: solubility is unmeasured (50 g/L is shown as a sensitivity), and
  *T. reesei* clips much of it.
- *Continuous processes* and cell recycle are not modelled.
- *Chromatography* is modelled only for lactoferrin, with guessed column hardware (the flow rate is
  Intelligen's design value) and no itemised buffer tanks (inside the missing-equipment allowance).
- *Not costed:* start-up and commissioning, working capital (except in the DCF price), failed
  batches, QC release testing, packaging, dewatering and inactivation of spent cells, and external
  heat-exchange loops for the largest vessels.
- *EU wastewater* is priced as in the US; the Dutch levy is per kg of oxygen demand, which is not
  modelled.
- *Guesses (grade E)* remain for:
  #flat(P, "").filter(x => x.at(1).at("grade", default: "") == "E").map(x => raw(x.at(0))).join(", ").

// ================================================================ 7 (priors)
= Scoring the pre-registered priors <sec-priors>

The priors were written in `docs/SCOPE.md` by the AI assistant (Claude) on 2026-09-26, before any
model output existed, and before the author had seen them. They were committed to git together with
the first outputs, so the repository cannot prove the order; the session record shows it but is not
public.

#let pi = R.calibration.intelligen2025_ova.msp_ccf_per_kg_target
#let inb(x, lo, hi) = x >= lo and x <= hi
#figure(
  table(
    columns: (2.6fr, 1.1fr, 1.8fr, 0.9fr),
    align: (left, left, left, left),
    table.header([*Prior (2026-09-26)*], [*Stated*], [*Outcome (v2)*], [*Score*]),
    hline,
    [1a. Intelligen configuration, \$/kg OVA (80% interval)], [\$38–60], [#usd(pi)/kg OVA],
      [#(if inb(pi, 38, 60) [inside] else [outside])],
    [1b. Base case, \$/kg protein (80% interval)], [\$28–50], [#usd(blg.msp_ccf) (BLG), #usd(ova.msp_ccf) (OVA)],
      [#(if inb(blg.msp_ccf, 28, 50) and inb(ova.msp_ccf, 28, 50) [inside, near the low end] else [outside])],
    [1 (superseded). Purified BLG/OVA at \~30 g/L and 1–10 kt/yr], [\$20–40],
      [10 kt/yr: #usd(blg.msp_ccf) concentrate, #usd(R.base_isolate.ova.msp_ccf) OVA isolate; 1 kt/yr: #usd(pi) (Intelligen configuration)],
      [#(if inb(pi, 20, 40) [inside] else [inside at 10 kt/yr, outside at 1 kt/yr])],
    [2. P(physical floor < \$10/kg)], [0.65],
      [BLG #usd(PL("blg/humbird").msp_ccf) at the assumed 40 mg/g/h (#(if PL("blg/humbird").msp_ccf < 10 [yes] else [no])); at 10 mg/g/h #usd(QP(10).msp_ccf) (#(if QP(10).msp_ccf < 10 [yes] else [no]))],
      [conditional: Brier #fx(calc.pow((if PL("blg/humbird").msp_ccf < 10 {1} else {0}) - 0.65, 2), d: 2) if secretion reaches 40 mg/g/h, #fx(calc.pow((if QP(10).msp_ccf < 10 {1} else {0}) - 0.65, 2), d: 2) if only 10],
    [3. P(a public BLG/OVA yield on sugar turns up)], [0.20],
      [no measured yield; design values exist (Behm 0.223, Intelligen 0.28 lumped)],
      [Brier 0.04 (measured); 0.64 if design values count],
    [4. P(first-try calibration within tolerance): yeast / NREL / Intelligen], [0.6 / 0.6 / 0.5],
      [yes / no (+136%) / yes (−3.6%)], [Brier 0.16 / 0.36 / 0.25],
    [5. P(public v1 by 2027-04-30 / 2027-07-31)], [0.5 / 0.8], [open], [—],
  ),
  caption: [Pre-registered priors and outcomes. Prior 4 is scored on the first run (2026-09-26),
  before the changes recorded in `docs/VALIDATION.md` and `docs/AUDIT.md`. Prior 3 meant a measured
  strain yield; both readings are scored. Prior 2 is scored once (BLG and OVA are one event), and its
  outcome depends on the secretion ceiling chosen during the audit, so it is scored conditionally.],
)

#if inb(blg.msp_ccf, 28, 50) [The interval priors were well placed but wide, and the base case landed near their low end.] else [The base-case interval prior missed low: after the review moved the fermenters from aseptic cell-culture prices to an industrial vendor quote, the base case (#usd(blg.msp_ccf)) fell below the \$28–50 interval; with aseptic vessels it would be #usd(R.base_aseptic.blg.msp_ccf), inside.]
The superseded prior was too optimistic at 1 kt/yr, as its replacement said. The calibration prior
was about right on average; the NREL miss came from capital conventions, which it did not anticipate.

// ================================================================ 8
= Reproducibility

```
.venv/bin/python -m pytest                      # model, calibration and invariant tests
.venv/bin/python scripts/run_analyses.py        # all results -> results/analyses.json
.venv/bin/python scripts/make_figures.py        # docs/figures/*.png
typst compile --root . report/pf_tea_report.typ # this document
```

Inputs are in `data/pf/base.yaml` (every value with a range, grade and source), with scenario
overrides in `data/pf/scenarios/`. The evidence files are `data/evidence/*.yaml`, with verbatim quotes
and locators. Calibration cases are in `data/calibration/`. The audit is `docs/AUDIT.md`.

// ================================================================ references
#heading(level: 1, numbering: none)[References]
#set par(justify: false)
#text(size: 9pt)[
- Almeida Benalcázar E, et al. Single cell protein production from ethanol: model-based bioreactor operation at industrial scale. Biotechnol Bioeng 122:1441 (2025). doi:10.1002/bit.28969 (reports Roels 1983: 460 kJ per mol O#sub[2]).
- Aro N, et al. Production of bovine β-lactoglobulin and hen egg ovalbumin by _Trichoderma reesei_ using precision fermentation technology and testing of their techno-functional properties. Food Res Int 163:112131 (2023). doi:10.1016/j.foodres.2022.112131
- Behm K, et al. Comparison of carbon footprint and water scarcity footprint of milk protein produced by cellular agriculture and the dairy industry. Int J LCA 27:1017 (2022). doi:10.1007/s11367-022-02087-0
- Carnicer M, et al. Macromolecular and elemental composition analysis and extracellular metabolite balances of _Pichia pastoris_ growing at different oxygen levels. Microb Cell Fact 8:65 (2009). doi:10.1186/1475-2859-8-65
- Chung BKS, et al. Genome-scale metabolic reconstruction and in silico analysis of methylotrophic yeast _Pichia pastoris_ for strain improvement. Microb Cell Fact 9:50 (2010). doi:10.1186/1475-2859-9-50
- Da Gama Ferreira R, Misailidis N, Parisis V, Petrides D. Egg white protein (ovalbumin) production via precision fermentation: process modeling and cost analysis using SuperPro Designer. Intelligen (2025). doi:10.13140/RG.2.2.29080.87048
- Da Gama Ferreira R, Misailidis N, Petrides D. Lactoferrin production via precision fermentation: process modeling and evaluation using SuperPro Designer. Intelligen, February 2026 version.
- The EVERY Company (Kale A, Patnaik R). Purified protein compositions and methods of production, US 2024/0083940 A1; Recombinant protein recovery methods, US 2025/0134130 A1; Ovalbumin protein compositions, US 12,096,784 B2.
- Ellilä S, Fonseca L, Uchima C, et al. Development of a low-cost cellulase production process using _Trichoderma reesei_ for Brazilian biorefineries. Biotechnol Biofuels 10:30 (2017). doi:10.1186/s13068-017-0717-0
- FDA GRAS Notices 1056 (β-lactoglobulin, Remilk), 1219 (bovine lactoferrin, TurtleTree) and 1284 (bovine lactoferrin, All G).
- GFI & Hawkwood Biotech. Driving down costs of fermentation-derived ingredients (2025). doi:10.62468/trxj5734
- GFI Europe & Arthur D. Little. Pathfinding towards precision fermentation viability (2025).
- Garrigós-Martínez J, Nieto-Taype MA, Gasset-Franch A, et al. Specific growth rate governs _AOX1_ gene expression, affecting the production kinetics of _Pichia pastoris_ (_Komagataella phaffii_) P#sub[AOX1]-driven recombinant producer strains with different target gene dosage. Microb Cell Fact 18:187 (2019). doi:10.1186/s12934-019-1240-8
- Heijnen JJ, van Dijken JP. In search of a thermodynamic description of biomass yields for the chemotrophic growth of microorganisms. Biotechnol Bioeng 39:833 (1992).
- Heyland J, Fu J, Blank LM, Schmid A. Quantitative physiology of _Pichia pastoris_ during glucose-limited high-cell density fed-batch cultivation for recombinant protein production. Biotechnol Bioeng 107:357 (2010). doi:10.1002/bit.22836
- Humbird D. Scale-up economics for cultured meat. Biotechnol Bioeng 118:3239 (2021). doi:10.1002/bit.27848 (and SI workbook)
- Humbird D, Davis R, McMillan JD. Aeration costs in stirred-tank and bubble column bioreactors. Biochem Eng J 127:161 (2017). doi:10.1016/j.bej.2017.08.006
- Humbird D, Davis R, Tao L, et al. Process design and economics for biochemical conversion of lignocellulosic biomass to ethanol. NREL/TP-5100-47764 (2011).
- IEAGHG (Amec Foster Wheeler). Effects of plant location on the costs of CO#sub[2] capture. Technical Report 2018/04 (2018).
- Li Y, et al. Transcriptional reprogramming with endogenous cis- and trans-elements for efficient food protein expression from safe substrates in _Komagataella phaffii_. Metab Eng (2026). doi:10.1016/j.ymben.2026.102555
- Liu WC, et al. Scaling-up fermentation of _Pichia pastoris_ to demonstration-scale using new methanol-feeding strategy and increased air pressure instead of pure oxygen supplement. Sci Rep 6:18439 (2016).
- Looser V, Bruhlmann B, Bumbak F, et al. Cultivation strategies to enhance productivity of _Pichia pastoris_: a review. Biotechnol Adv 33:1177 (2015). doi:10.1016/j.biotechadv.2015.05.008
- Martin WF, et al. ATP requirements for growth reveal the bioenergetic impact of mitochondrial symbiosis. Biochim Biophys Acta Bioenerg (2025). doi:10.1016/j.bbabio.2025.149564
- Maskow T, Kemp R, Buchholz F, et al. What heat is telling us about microbial conversions in nature and technology. Microb Biotechnol 3:269 (2010).
- Maurer M, et al. Versatile modeling and optimization of fed batch processes for the production of secreted heterologous proteins with _Pichia pastoris_. Microb Cell Fact 5:37 (2006).
- Nieto-Taype MA, Garcia-Ortega X, Garrigós-Martínez J, et al. Rationale-based selection of optimal operating strategies and gene dosage impact on recombinant protein production in _Komagataella phaffii_ (_Pichia pastoris_). Microb Biotechnol 13:315 (2020). doi:10.1111/1751-7915.13498
- Mercier-Bouchard D, et al. Process efficiency of casein separation from milk using polymeric spiral-wound microfiltration membranes. J Dairy Sci 100:8838 (2017). doi:10.3168/jds.2017-13015
- Petrides D. Bioprocess design and economics. In Harrison RG, et al., Bioseparations Science and Engineering, 2nd ed. Oxford University Press (2015), ch. 11 (Intelligen web version).
- Pires MC, et al. Column ageing of agarose-based chromatography in industrial lactoferrin purification. J Chromatogr A 1760:466274 (2025).
- Prielhofer R, Reichinger M, Wagner N, et al. Superior protein titers in half the fermentation time: promoter and process engineering for the glucose-regulated _GTH1_ promoter of _Pichia pastoris_. Biotechnol Bioeng 115:2479 (2018). doi:10.1002/bit.26800
- Rebnegger C, Graf AB, Valli M, et al. In _Pichia pastoris_, growth rate regulates protein synthesis and secretion, mating and stress response. Biotechnol J 9:511 (2014). doi:10.1002/biot.201300334
- Rebnegger C, et al. _Pichia pastoris_ exhibits high viability and a low maintenance energy requirement at near-zero specific growth rates. Appl Environ Microbiol 82:4570 (2016).
- Rebnegger C, et al. Protein production dynamics and physiological adaptation of recombinant _Komagataella phaffii_ at near-zero growth rates. Microb Cell Fact 23:44 (2024).
- Tetra Pak. Dairy Processing Handbook (online), chapters 7.6, 18 and 19.
- Tijhuis L, van Loosdrecht MCM, Heijnen JJ. A thermodynamically based correlation for maintenance Gibbs energy requirements in aerobic and anaerobic chemotrophic growth. Biotechnol Bioeng 42:509 (1993).
- Tsai LS, Ijichi K, Harris MW. Concentration of egg white by ultrafiltration. J Food Prot 40:449 (1977).
- van 't Riet K. Review of measuring methods and results in nonviscous gas-liquid mass transfer in stirred vessels. Ind Eng Chem Process Des Dev 18:357 (1979).
- Voutilainen E, Pihlajaniemi V, Parviainen T. Economic comparison of food protein production with single-cell organisms from lignocellulose side-streams. Bioresour Technol Rep 14:100683 (2021).
- Wang L, et al. The thermodynamic and gelation properties of ovalbumin and lysozyme. Gels 11:470 (2025).
- Yao C, Zhu H, An Q, Zhang M, Zheng Y, Cai M. Omics-guided global rewiring of yeast metabolism enables high-level production of β-lactoglobulin. Food Biosci 82:109383 (2026).
- Yen CC, Wu PY, Ou-Yang H, et al. Production of bioactive porcine lactoferrin through a novel glucose-inducible expression system in _Pichia pastoris_. Int J Mol Sci 25:1818 (2024).
- Yver AL, et al. Fractionation of whey protein isolate with supercritical carbon dioxide: process modeling and cost estimation. Int J Mol Sci 13:240 (2012).
- Price, wage and trade statistics: US EIA, Eurostat (nrg_pc_203/205, lc_lci_lev, earn_ses22, Comext DS-045409), US BLS (OEWS, PPI, CPI-U), USDA (NASS, ERS, AMS Dairy Market News, FoodData Central), UN Comtrade, ECB, EC agri-food portal, WRAP and EREF. Full locators in `data/evidence/`.
]

// ================================================================ appendix
#pagebreak()
#set heading(numbering: "A.1")
#counter(heading).update(0)
= Parameters (generated from `data/pf/base.yaml`)

#let showv(x) = {
  if x == none { "—" } else if type(x) == bool { if x { "yes" } else { "no" } }
  else if type(x) == int or type(x) == float { str(x) } else if type(x) == str { x }
  else if type(x) == dictionary and "us_midwest" in x [US #str(x.us_midwest) / EU #str(x.eu_nw)]
  else { [(table in file)] }
}
#let showleaf(x) = {
  if "us_midwest" in x [US #showv(x.us_midwest)\; EU #showv(x.eu_nw)] else if "value" in x [#showv(x.value)] else []
}
#set text(size: 7pt)
#table(
  columns: (1.9fr, 0.9fr, 0.8fr, 0.3fr, 3fr),
  inset: (x: 3pt, y: 2pt),
  table.header([*Parameter*], [*Value*], [*Range*], [*Gr.*], [*Source*]),
  hline,
  ..for (path, x) in flat(P, "") {
    ([#text(font: "DejaVu Sans Mono", size: 6pt, path.replace(".", ".\u{200b}").replace("_", "_\u{200b}"))], showleaf(x),
     [#(if "low" in x and "high" in x [#showv(x.low)–#showv(x.high)] else [])],
     [#x.at("grade", default: "")], [#x.at("source", default: x.at("note", default: ""))])
  },
)
#set text(size: 10.5pt)

= Evidence base

#let gcount(file) = {
  let c = (A: 0, B: 0, C: 0, D: 0, E: 0)
  for e in yaml(file) { let g = e.at("grade", default: ""); if g in c { c.insert(g, c.at(g) + 1) } }
  c
}
#figure(
  table(
    columns: (1.6fr, 0.6fr, 0.6fr, 0.6fr, 0.6fr, 0.6fr, 0.7fr),
    align: (left,) + (right,) * 6,
    table.header([*Evidence file*], [*A*], [*B*], [*C*], [*D*], [*E*], [*Total*]),
    hline,
    ..for f in ("hosts", "dsp", "engineering", "prices", "placeholders", "milk_egg", "lactoferrin", "casein") {
      let c = gcount("../data/evidence/" + f + ".yaml")
      ([`data/evidence/`#f`.yaml`], ..("A", "B", "C", "D", "E").map(g => str(c.at(g))),
       str(c.values().sum()))
    },
  ),
  caption: [Evidence entries by grade. Each entry carries a source, a locator and, where a document
  was read, a verbatim quote.],
)
