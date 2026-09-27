// One-page memo for funders. Compile: typst compile --root . report/memo.typ
// Numbers are read from results/analyses.json, like the report.
#let R = json("../results/analyses.json")
#let fx(x, d: 0) = {
  let s = str(calc.round(x, digits: d))
  if d > 0 and not s.contains(".") { s = s + "." + "0" * d }
  s
}
#let usd(x, d: 0) = if x == none { "n/a" } else { "$" + fx(x, d: d) }
#let thou(n) = {
  let s = str(int(calc.round(n)))
  let out = ""
  for (i, c) in s.clusters().enumerate() { if i > 0 and calc.rem(s.len() - i, 3) == 0 { out += "," }; out += c }
  out
}
#let S(k) = R.scenarios.at(k)
#let PL(k) = R.physical_limit.at(k)
#let inc = R.benchmarks.incumbents
#let req(key, tg, t) = R.required.at(key).at(str(tg)).at(R.required_t_prods.position(x => x == t))
#let blg = R.base.blg
#let LF = R.lactoferrin
#let where(x, band) = {
  let (lo, hi) = (band.at(0), band.at(1))
  if x < lo { "below" } else if x <= hi { "inside" } else { "above" }
}
#let IB = LF.reported_prices.comparators.find(c => c.key == "lf_cost_intelligen2026_case_b_cex")
#let wheyobs = inc.whey.series.values().map(s => s.values()).flatten()
#let above(x) = wheyobs.filter(p => p >= x).len()

#set page(paper: "a4", margin: (x: 2cm, y: 1.6cm))
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10pt)
#set par(justify: true, leading: 0.55em, spacing: 0.8em)
#set table(stroke: none, inset: (x: 4pt, y: 2.5pt))
#show table: set text(size: 8.8pt)

#let BD(q) = R.best_design_base.at(str(q), default: none)
#let QP(q) = R.physical_limit.at("blg/humbird/q_p_max_" + str(q), default: none)

#text(size: 13pt, weight: "bold")[Precision-fermented whey and egg proteins: what they cost, and where evidence would help]
#v(-0.3em)
#text(size: 8.5pt, fill: rgb("#52514e"))[Memo · v2.1, audited and AI pre-reviewed (#R.generated) · Pablo Antonio Moreno Casares · techno-economic model `pf-tea`,
Humbird (2021) method, checked against NREL, Intelligen and Voutilainen designs · prepared with an AI assistant; not yet reviewed by human experts]

*Bottom line.*
- *Today's public strains are far too expensive.* Food-grade β-lactoglobulin (BLG, whey) and
  ovalbumin (OVA, egg) cost #usd(S("academic/blg").msp_ccf) and #usd(S("academic/ova").msp_ccf) per kg
  protein at the best published titers. Whey protein traded at #usd(inc.whey.band.at(0))–#usd(inc.whey.band.at(1))
  and dried egg white at #usd(inc.egg.band.at(0))–#usd(inc.egg.band.at(1)) per kg protein in 2015–2025
  (2025 dollars).
- *At the titers companies' cost models assume, BLG is near whey.* At 42 g/L it costs
  #usd(S("industry/blg").msp_ccf, d: 1) (#usd(S("industry/blg/light").msp_ccf, d: 1) with the lighter
  accounting of NREL-style design reports); #above(S("industry/blg").msp_ccf) of #wheyobs.len() annual
  whey export prices in 2015–2025 were above the first figure.
- *The gate is secretion, not titer.* \$20/kg needs about #fx(req("blg/humbird", 20, 72).q_p_mg_g_h)–#fx(req("blg/humbird", 20, 48).q_p_mg_g_h)
  mg protein per g of cells per hour at the base cell density (the base design: #fx(blg.design.q_p_mg_g_h, d: 1)).
  With today's biology and capital, design alone reaches #usd(BD(40).msp_ccf, d: 1)/kg at 40 mg/g/h
  and #usd(BD(10).msp_ccf, d: 1) at 10. No published *K. phaffii* process is near either rate: compiled
  secretion rates stay below 1 mg/g/h and peak while cells grow fast, the best glucose fed-batch we found
  reached 2.1, and in the one near-zero-growth study, secretion fell as growth slowed.
- *Best case, not a floor.* With every assumed limit at its best, 400 m³ vessels and 100 kt/yr, BLG
  costs #usd(PL("blg/humbird").msp_ccf, d: 1) and OVA #usd(PL("ova/humbird").msp_ccf, d: 1) per kg, if cells
  secrete 40 mg/g/h; at 10 mg/g/h BLG costs #usd(QP(10).msp_ccf, d: 1), and at the best rate demonstrated in a
  public glucose fed-batch (2.1 mg/g/h) #usd(QP(2.1).msp_ccf, d: 1).
- *Lactoferrin shows the other side.* At a design titer of 10 g/L, PF lactoferrin costs
  #usd(LF.cases.at("lf/light").msp_ccf)–#usd(LF.cases.at("lf/humbird").msp_ccf)/kg, against
  #usd(LF.reported_prices.band.at(0))–\$#thou(LF.reported_prices.band.at(1))/kg reported for the dairy product.
  Intelligen's own model of the same route costs #fx(IB.value_money_year / LF.reconciliation.lf.cop, d: 1)×
  ours to produce, mostly through its unit prices; even so it sits #where(IB.value_money_year, LF.reported_prices.band)
  that range.

#table(
  columns: (2.3fr, 0.9fr, 1fr, 1fr, 1fr, 1fr),
  align: (left, center, right, right, right, right),
  table.header([*\$/kg protein, 10 kt/yr, US*], [*titer g/L*], [*BLG*], [*BLG light*], [*OVA*], [*OVA light*]),
  table.hline(stroke: 0.5pt + rgb("#c3c2b7")),
  [best public academic strain], [#fx(S("academic/blg").design.titer, d: 1) / #fx(S("academic/ova").design.titer)],
    [#usd(S("academic/blg").msp_ccf)], [#usd(S("academic/blg/light").msp_ccf)],
    [#usd(S("academic/ova").msp_ccf)], [#usd(S("academic/ova/light").msp_ccf)],
  [base case], [30], [#usd(blg.msp_ccf, d: 1)], [#usd(R.base_light.blg.msp_ccf, d: 1)], [#usd(R.base.ova.msp_ccf, d: 1)],
    [#usd(R.base_light.ova.msp_ccf, d: 1)],
  [industry benchmark], [42], [#usd(S("industry/blg").msp_ccf, d: 1)], [#usd(S("industry/blg/light").msp_ccf, d: 1)],
    [#usd(S("industry/ova").msp_ccf, d: 1)], [#usd(S("industry/ova/light").msp_ccf, d: 1)],
  [physical-limit best case (100 kt/yr)], [#fx(PL("blg/humbird").titer) / #fx(PL("ova/humbird").titer)],
    [#usd(PL("blg/humbird").msp_ccf, d: 1)], [#usd(PL("blg/light").msp_ccf, d: 1)],
    [#usd(PL("ova/humbird").msp_ccf, d: 1)], [#usd(PL("ova/light").msp_ccf, d: 1)],
)

*Capital.* Fermenters are priced at an industrial vendor quote; the aseptic cell-culture vessels of
our first version would add #usd(R.base_aseptic.blg.msp_ccf - blg.msp_ccf, d: 1)/kg to the base. The two accounting conventions
differ by #usd(blg.msp_ccf - R.base_light.blg.msp_ccf, d: 1)/kg, mostly because Humbird charges 9% of investment a
year for maintenance, insurance and overheads and NREL-style reports under 2%.

*Where evidence would help most*, in our judgment:
+ *Secretion without growth.* How much BLG or OVA a strain secretes per g of cells per hour when it
  barely grows, over days, at 1–10 m³. It sets both today's cost and the best case.
+ *Open fed-batch data.* Titer, productivity and sugar yield measured *together*; the product yield in
  every cost estimate, ours included, is a design value.
+ *Real plant costs.* Capital, staffing and running costs of recent PF plants would settle the vessel
  price basis and the fixed-cost rule.
+ *The design ceiling.* Workable starting volumes, feed concentrations and O#sub[2] transfer at scale.

*EU.* At Dutch sugar, energy, wage and construction prices the same plant costs about
#usd(R.policy.at("EU base") - R.policy.at("US base"), d: 1)/kg more. A capital charge at 4% over 20 years
instead of 7.5% over 10 would cut #usd(R.policy.at("EU base") - R.policy.at("EU, capital at 4%/20 yr"), d: 1)/kg;
US-level sugar #usd(R.policy.at("EU base") - R.policy.at("EU with US glucose price"), d: 1). These are cost
effects on one plant, not policy recommendations.

#text(size: 8.5pt, fill: rgb("#52514e"))[*Caveats.* A production cost with a 14.6%/yr capital charge, not a
market price. Excludes R&D, licensing, regulatory, sales, start-up, failed batches and first-of-a-kind
premiums. Strain parameters rest on design values and company-reported averages (evidence grades B–C).
The best public BLG titer uses an ethanol-fed production phase, priced here as glucose. Full report,
audit log, simulated expert reviews and data: `pf-tea` repository.]
