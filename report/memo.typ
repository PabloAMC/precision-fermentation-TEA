// One-page memo for funders. Compile: typst compile --root . report/memo.typ
// Numbers are read from results/analyses.json, like the report.
#let R = json("../results/analyses.json")
#let fx(x, d: 0) = {
  let s = str(calc.round(x, digits: d))
  if d > 0 and not s.contains(".") { s = s + "." + "0" * d }
  s
}
#let usd(x, d: 0) = if x == none { "n/a" } else { "$" + fx(x, d: d) }
#let S(k) = R.scenarios.at(k)
#let PL(k) = R.physical_limit.at(k)
#let inc = R.benchmarks.incumbents
#let req(key, tg, t) = R.required.at(key).at(str(tg)).at(R.required_t_prods.position(x => x == t))
#let blg = R.base.blg

#set page(paper: "a4", margin: (x: 2cm, y: 1.7cm))
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10pt)
#set par(justify: true, leading: 0.55em, spacing: 0.8em)
#set table(stroke: none, inset: (x: 4pt, y: 2.5pt))
#show table: set text(size: 8.8pt)

#text(size: 13pt, weight: "bold")[Precision-fermented whey and egg proteins: what they cost, and where funding helps]
#v(-0.3em)
#text(size: 8.5pt, fill: rgb("#52514e"))[Memo · draft v1 (#R.generated) · Pablo Antonio Moreno Casares · techno-economic model `pf-tea`,
Humbird (2021) method, calibrated against NREL, Intelligen and Voutilainen designs]

*Bottom line.*
- *Today's public strains are an order of magnitude too expensive.* Food-grade β-lactoglobulin (BLG,
  whey) and ovalbumin (OVA, egg) cost #usd(S("academic/blg").msp_ccf) and #usd(S("academic/ova").msp_ccf)
  per kg protein at the best published titers. Whey protein trades at #usd(inc.whey.band.at(0))–#usd(inc.whey.band.at(1))
  and dried egg white at #usd(inc.egg.band.at(0))–#usd(inc.egg.band.at(1)) per kg protein (2015–2025).
- *Industry-level strains are close but not there.* At the 42 g/L private-sector average titer, the
  cost is #usd(S("industry/blg").msp_ccf, d: 1) (BLG) with a conservative capital estimate and
  #usd(S("industry/blg/light").msp_ccf, d: 1) with the lighter one used by published studies. That
  undercuts whey only in spike years like 2026 (about #usd(inc.whey.spot.at(0).usd_kg_protein)/kg protein),
  or, with light capital, at mid-range whey prices.
- *Physics caps the titer, and capital dominates the cost.* Oxygen transfer and cooling limit a 200 m³
  fermenter to about #fx(R.titer_ceiling.blg.at(R.required_t_prods.position(x => x == 72))) g/L in a
  72 h production phase. Capital-related costs are
  #(fx(100 * (blg.per_kg.at("capital charge") + blg.per_kg.maintenance + blg.per_kg.at("insurance & tax")) / blg.msp_ccf) + "%")
  of the base-case price; sugar is #(fx(100 * blg.per_kg.glucose / blg.msp_ccf) + "%").
- *The physical floor is low.* With everything at its best at once, the cost is
  #usd(PL("blg/humbird").msp_ccf, d: 1) (BLG) and #usd(PL("ova/humbird").msp_ccf, d: 1) (OVA) per kg,
  or #usd(PL("blg/light").msp_ccf, d: 1) and #usd(PL("ova/light").msp_ccf, d: 1) with light capital.
  The gap between today and the floor is engineering and biology, not thermodynamics.

#table(
  columns: (2.3fr, 0.9fr, 1fr, 1fr, 1fr, 1fr),
  align: (left, center, right, right, right, right),
  table.header([*\$/kg protein, 10 kt/yr, US*], [*titer g/L*], [*BLG*], [*BLG light*], [*OVA*], [*OVA light*]),
  table.hline(stroke: 0.5pt + rgb("#c3c2b7")),
  [best public academic strain], [5 / 2], [#usd(S("academic/blg").msp_ccf)], [#usd(S("academic/blg/light").msp_ccf)],
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
phase, or #fx(req("blg/humbird", 20, 72).titer) g/L in 72 h, with conservative capital. That is at
the private-sector average and near the oxygen ceiling. With light capital, #fx(req("blg/light", 20, 48).titer)–#fx(req("blg/light", 20, 72).titer) g/L.
#let r10l = R.required.at("blg/light").at("10").filter(r => r.titer != none).map(r => r.titer)
\$10/kg is not reachable with conservative capital at today's cell densities and yields.
#if r10l.len() > 0 [With light capital it needs #fx(calc.min(..r10l))–#fx(calc.max(..r10l)) g/L in
4–5 days, right at the oxygen ceiling.] Beyond that, cell density, production time, cheaper capital
and scale must move together. Product yield and vessel size, perhaps surprisingly, matter little.

*Where the next dollar helps most*, in our judgment:
+ *Open fed-batch data.* Measured titer, productivity and sugar yield *together*, at 1–10 m³, for BLG
  and OVA. No public dataset has all three. This is the largest evidence gap, and every cost
  estimate, ours included, rests on company averages.
+ *Productivity per hour of fermenter time, not titer alone.* Near the oxygen ceiling, extra titer
  helps only if it does not take longer.
+ *Capital-light capacity.* Capital is the largest cost item in every scenario. Conversions of
  existing ethanol or enzyme fermenters, and shared scale-up plants, attack it directly.
+ *Downstream data.* Membrane fluxes and recoveries at scale (today: one patent example) are the next
  largest uncertainty.

*EU.* At EU sugar and energy prices the same plant costs about
#usd(R.base_eu.blg.msp_ccf - blg.msp_ccf, d: 1)/kg more, mostly because of sugar. The cost of capital
matters more than energy subsidies.

#text(size: 8.5pt, fill: rgb("#52514e"))[*Caveats.* A production cost with a 14.6%/yr capital charge,
not a market price. Excludes R&D, licensing, regulatory, sales and first-of-a-kind premiums. Strain
parameters rest on design values and company-reported averages (evidence grades B–C). OVA results depend on an
assumed 50 g/L practical solubility. Full report, calibration record and data: `pf-tea` repository.]
