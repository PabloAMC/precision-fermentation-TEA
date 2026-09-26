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
#let wheyobs = inc.whey.series.values().map(s => s.values()).flatten()
#let above(x) = wheyobs.filter(p => p >= x).len()

#set page(paper: "a4", margin: (x: 2cm, y: 1.6cm))
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10pt)
#set par(justify: true, leading: 0.55em, spacing: 0.8em)
#set table(stroke: none, inset: (x: 4pt, y: 2.5pt))
#show table: set text(size: 8.8pt)

#text(size: 13pt, weight: "bold")[Precision-fermented whey and egg proteins: what they cost, and where evidence would help]
#v(-0.3em)
#text(size: 8.5pt, fill: rgb("#52514e"))[Memo · v2, audited (#R.generated) · Pablo Antonio Moreno Casares · techno-economic model `pf-tea`,
Humbird (2021) method, checked against NREL, Intelligen and Voutilainen designs · prepared with an AI assistant; not yet peer-reviewed]

*Bottom line.*
- *Today's public strains are several times too expensive.* Food-grade β-lactoglobulin (BLG, whey) and
  ovalbumin (OVA, egg) cost #usd(S("academic/blg").msp_ccf) and #usd(S("academic/ova").msp_ccf) per kg
  protein at the best published titers. Whey protein traded at #usd(inc.whey.band.at(0))–#usd(inc.whey.band.at(1))
  and dried egg white at #usd(inc.egg.band.at(0))–#usd(inc.egg.band.at(1)) per kg protein in 2015–2025
  (2025 dollars).
- *Industry-level titers are close but not there.* At the 42 g/L private-sector average, BLG costs
  #usd(S("industry/blg").msp_ccf, d: 1) with our base (price-anchored) capital estimate and
  #usd(S("industry/blg/light").msp_ccf, d: 1) with the lighter one most published studies use. That
  undercuts whey in spike years like 2026 (about #usd(inc.whey.spot.at(0).usd_kg_protein)/kg protein);
  in 2015–2025, only #above(S("industry/blg/light").msp_ccf) of #wheyobs.len() annual export prices were
  above even the lighter estimate.
- *Whey is the hardest benchmark.* It is a by-product of cheese, priced at what clears the market.
  Lactoferrin, a scarce milk protein, shows the other side: the same model puts PF lactoferrin at
  #usd(LF.cases.at("lf/light").msp_ccf)–#usd(LF.cases.at("lf/humbird").msp_ccf)/kg (lighter to base capital), against
  #usd(LF.reported_prices.band.at(0))–\$#thou(LF.reported_prices.band.at(1))/kg reported for the dairy product.
- *A feasibility ceiling and capital dominate.* A higher titer needs more sugar feed, and a 200 m³
  fermenter that must start at least 30% full with a 50% glucose feed reaches about
  #fx(R.titer_ceiling.blg.at(R.required_t_prods.position(x => x == 72))) g/L in a 72 h production phase.
  Both are design choices; relaxed, the secretion rate and O#sub[2] transfer set the ceiling instead, near
  #fx(R.ceiling_limits.at("minimum fill 0.20").at(1).ceiling) g/L. Capital-related costs are
  #(fx(100 * (blg.per_kg.at("capital charge") + blg.per_kg.maintenance + blg.per_kg.at("insurance & tax")) / blg.msp_ccf) + "%")
  of the base-case price; sugar is #(fx(100 * blg.per_kg.glucose / blg.msp_ccf) + "%").
- *The physical floor is low.* With every biological parameter at its best at once, the cost is
  #usd(PL("blg/humbird").msp_ccf, d: 1) (BLG) and #usd(PL("ova/humbird").msp_ccf, d: 1) (OVA) per kg,
  or #usd(PL("blg/light").msp_ccf, d: 1) and #usd(PL("ova/light").msp_ccf, d: 1) with the lighter capital
  estimate. The gap between today and the floor is engineering and biology, not thermodynamics.

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
  [physical limit (100 kt/yr)], [#fx(PL("blg/humbird").titer) / #fx(PL("ova/humbird").titer)],
    [#usd(PL("blg/humbird").msp_ccf, d: 1)], [#usd(PL("blg/light").msp_ccf, d: 1)],
    [#usd(PL("ova/humbird").msp_ccf, d: 1)], [#usd(PL("ova/light").msp_ccf, d: 1)],
)

*What \$20/kg requires.* About #fx(req("blg/humbird", 20, 48).titer) g/L of BLG in a 48 h production
phase, or #fx(req("blg/humbird", 20, 72).titer) g/L in 72 h, with price-anchored capital; with the
lighter estimate, #fx(req("blg/light", 20, 48).titer)–#fx(req("blg/light", 20, 72).titer) g/L.
#let r10h = R.required.at("blg/humbird").at("10").filter(r => r.titer != none).map(r => r.titer)
#let r10l = R.required.at("blg/light").at("10").filter(r => r.titer != none).map(r => r.titer)
#if r10h.len() == 0 [\$10/kg is not reachable with price-anchored capital at the base cell density and yield.]
#if r10l.len() > 0 [With the lighter estimate it needs #fx(calc.min(..r10l))–#fx(calc.max(..r10l)) g/L, near the ceiling.]
Beyond that, yield, cell density, production time, capital and scale must move together.

*Where evidence would help most*, in our judgment:
+ *Open fed-batch data.* Measured titer, productivity and sugar yield *together*, at 1–10 m³, for BLG
  and OVA. No public dataset has all three; the product yield in every cost estimate, ours included,
  is a design value.
+ *Productivity per hour of fermenter time, not titer alone.* Near the ceiling, extra titer helps
  only if it takes neither longer nor more feed; the workable starting volume and feed concentration at
  scale would move the ceiling itself.
+ *Real capital costs.* Capital is the largest cost item in every scenario, and the two estimating
  conventions differ by #fx(R.base.blg.msp_ccf / R.base_light.blg.msp_ccf, d: 1)×; published costs of
  recent plants would settle it.
+ *Downstream data.* Diafiltration flux at scale (one patent value sizes most of the membrane area).

*EU.* At Dutch sugar, energy, wage and construction prices the same plant costs about
#usd(R.policy.at("EU base") - R.policy.at("US base"), d: 1)/kg more. A capital charge at 4% over 20 years
instead of 7.5% over 10 would cut #usd(R.policy.at("EU base") - R.policy.at("EU, capital at 4%/20 yr"), d: 1)/kg;
US-level sugar #usd(R.policy.at("EU base") - R.policy.at("EU with US glucose price"), d: 1). These are cost
effects on one plant, not policy recommendations.

#text(size: 8.5pt, fill: rgb("#52514e"))[*Caveats.* A production cost with a 14.6%/yr capital charge, not a
market price. Excludes R&D, licensing, regulatory, sales and first-of-a-kind premiums. Strain parameters
rest on design values and company-reported averages (evidence grades B–C). The best public BLG titer
uses an ethanol-fed production phase, priced here as glucose. Full report, audit log, calibration
record and data: `pf-tea` repository.]
