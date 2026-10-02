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
#let money(x) = if x == none { "—" } else if x >= 100 { "$" + thou(x) } else { usd(x, d: 1) }
#let S(k) = R.scenarios.at(k)
#let PL(k) = R.physical_limit.at(k)
#let inc = R.benchmarks.incumbents
#let req(key, tg, t) = R.required.at(key).at(str(tg)).at(R.required_t_prods.position(x => x == t))
#let blg = R.base.blg
#let cas = R.base.cas
#let lfb = R.base.lf
#let alb = R.base.alb
#let LF = R.lactoferrin
#let ALB = R.albumin
#let PRODS = R.base.keys()
#let NAME = (blg: "BLG", ova: "OVA", ovd: "ovomucoid", cas: "β-casein", lf: "lactoferrin", alb: "albumin")
#let MKT(p) = {
  let m = inc.values().find(d => d.compare_to.contains(p))
  if m != none { m.band } else { R.at((lf: "lactoferrin", alb: "albumin").at(p)).reported_prices.band }
}
#let where(x, band) = {
  let (lo, hi) = (band.at(0), band.at(1))
  if x < lo { "below" } else if x <= hi { "inside" } else { "above" }
}
#let IB = LF.reported_prices.comparators.find(c => c.key == "lf_cost_intelligen2026_case_b_cex")
#let wheyobs = inc.whey.series.values().map(s => s.values()).flatten()
#let above(x) = wheyobs.filter(p => p >= x).len()

#set page(paper: "a4", margin: (x: 2cm, y: 1.5cm))
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 9.8pt)
#set par(justify: true, leading: 0.52em, spacing: 0.75em)
#set table(stroke: none, inset: (x: 4pt, y: 2.3pt))
#show table: set text(size: 8.6pt)

#let BD(q) = R.best_design_base.at(str(q), default: none)
#let QP(q) = R.physical_limit.at("blg/humbird/q_p_max_" + str(q), default: none)

#text(size: 13pt, weight: "bold")[Precision-fermented dairy, egg and serum proteins: what they cost, and where evidence would help]
#v(-0.3em)
#text(size: 8.5pt, fill: rgb("#52514e"))[Memo · v4, six proteins (#R.generated) · Pablo Antonio Moreno Casares · techno-economic model `pf-tea`,
Humbird (2021) method, checked against NREL, Intelligen and Voutilainen designs · prepared with an AI assistant; not yet reviewed by human experts]

*Bottom line.*
- *Today's public strains are far too expensive.* At the best peer-reviewed titers, β-lactoglobulin
  (BLG, whey), ovalbumin (OVA), ovomucoid (both egg white) and β-casein cost #money(S("academic/blg").msp_ccf),
  #money(S("academic/ova").msp_ccf), #money(S("academic/ovd").msp_ccf) and #money(S("academic/cas").msp_ccf) per kg
  protein. Whey protein, dried egg white and casein traded at #usd(inc.whey.band.at(0))–#usd(inc.whey.band.at(1)),
  #usd(inc.egg.band.at(0))–#usd(inc.egg.band.at(1)) and #usd(inc.casein.band.at(0))–#usd(inc.casein.band.at(1))
  per kg protein in 2015–2025 (2025 dollars). The one public titer near the design point is a company's own:
  EVERY's 30 g/L ovomucoid patent example, at #money(S("academic/ovd_patent").msp_ccf).
- *At the titers companies' cost models assume, the commodity proteins near their markets.* At
  42 g/L BLG costs #money(S("industry/blg").msp_ccf) (#money(S("industry/blg/light").msp_ccf) with the lighter
  accounting of NREL-style design reports), OVA #money(S("industry/ova").msp_ccf), ovomucoid
  #money(S("industry/ovd").msp_ccf) and β-casein #money(S("industry/cas").msp_ccf)\; #above(S("industry/blg").msp_ccf) of #wheyobs.len() annual whey export
  prices in 2015–2025 were above the BLG figure. Casein has the thinnest evidence: no company discloses
  a titer, and no secreted casein titer is public for any yeast or fungus.
- *The gate is secretion, not titer.* \$20/kg needs about #fx(req("blg/humbird", 20, 72).q_p_mg_g_h)–#fx(req("blg/humbird", 20, 48).q_p_mg_g_h)
  mg protein per g of cells per hour at the base cell density (the base design: #fx(blg.design.q_p_mg_g_h, d: 1)).
  With today's biology and capital, design alone reaches #money(BD(40).msp_ccf)/kg BLG at 40 mg/g/h
  and #money(BD(10).msp_ccf) at 10. No published *K. phaffii* process is near either rate: the best glucose
  fed-batch we found reached 2.1, and in the one near-zero-growth study secretion fell as growth slowed.
- *Best case, not a floor.* With every assumed limit at its best, 400 m³ vessels and 100 kt/yr, BLG,
  OVA, ovomucoid and β-casein cost #money(PL("blg/humbird").msp_ccf), #money(PL("ova/humbird").msp_ccf),
  #money(PL("ovd/humbird").msp_ccf) and #money(PL("cas/humbird").msp_ccf) per kg if cells secrete 40 mg/g/h; at 10 mg/g/h BLG costs
  #money(QP(10).msp_ccf), and at the best rate demonstrated (2.1 mg/g/h) #money(QP(2.1).msp_ccf).
- *Scarce proteins are the easy case.* At its design titer (10 g/L) and a market-sized plant
  (250 t/yr), PF lactoferrin costs #money(R.base_light.lf.msp_ccf)–#money(lfb.msp_ccf)/kg,
  #where(lfb.msp_ccf, MKT("lf")) the #money(MKT("lf").at(0))–#money(MKT("lf").at(1))/kg reported for the dairy
  product; Intelligen's own model of the same route costs #fx(IB.value_money_year / LF.reconciliation.lf.cop, d: 1)×
  ours to produce.
- *The route can change the product.* Precipitated, as dairy casein is, β-casein reaches dairy purity
  at #money(cas.msp_ccf)/kg; the only public yeast casein process (membranes only) makes a powder that
  is about 6% β-casein, mostly yeast carbohydrate.
- *Albumin for cultivated-meat media: the column sets the cost.* With the cation-exchange capture of
  the industrial process, at cell-culture purity and 1 kt/yr, albumin costs #money(alb.msp_ccf)/kg
  (#money(S("industry/alb").msp_ccf) at 42 g/L; #money(S("academic/alb").msp_ccf) at the record 17.5 g/L, made with
  methanol), against #usd(MKT("alb").at(0))–#usd(MKT("alb").at(1)) for bulk bovine albumin and GFI's
  \$#ALB.cm.gfi_target_usd_kg/kg target. Cheap resin brings it to #money(ALB.resin.at("dsp.cex_resin_usd_L=100")) and
  membranes alone, if they reached the purity, #money(ALB.cases.at("alb_ufdf_only/humbird").msp_ccf). At the base cost it adds
  #usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(0) / 1000, d: 2)–#usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(2) / 1000, d: 2) per kg of cultivated meat, while leading firms are removing albumin from their media.

#table(
  columns: (2.1fr,) + PRODS.map(_ => 1fr),
  align: (left,) + PRODS.map(_ => right),
  table.header([*\$/kg protein, US*], ..PRODS.map(p => [*#NAME.at(p)*])),
  table.hline(stroke: 0.5pt + rgb("#c3c2b7")),
  [best public academic strain], ..PRODS.map(p => [#money(S("academic/" + p).msp_ccf)]),
  [base case (30 g/L; lactoferrin 10 g/L)], ..PRODS.map(p => [#money(R.base.at(p).msp_ccf)]),
  [base case, design-report capital], ..PRODS.map(p => [#money(R.base_light.at(p).msp_ccf)]),
  [industry benchmark (42 g/L)], ..PRODS.map(p => [#money(S("industry/" + p).msp_ccf)]),
  [physical-limit best case], ..PRODS.map(p => [#money(PL(p + "/humbird").msp_ccf)]),
  table.hline(stroke: 0.5pt + rgb("#c3c2b7")),
  [incumbent, 2025\$ per kg protein], ..PRODS.map(p => [#money(MKT(p).at(0))–#money(MKT(p).at(1))]),
)
#text(size: 8pt, fill: rgb("#52514e"))[Plants: 10 kt/yr (lactoferrin 250 t/yr, albumin 1 kt/yr); physical limit at 100 kt/yr (lactoferrin 1.6 kt/yr). Albumin's incumbent: bulk bovine albumin (technical grade).]

*Where evidence would help most*, in our judgment:
+ *Secretion without growth.* How much protein a strain secretes per g of cells per hour when it
  barely grows, over days, at 1–10 m³. It sets both today's cost and the best case, for every protein here.
+ *Open fed-batch data.* Titer, productivity and sugar yield measured *together*; for casein, any
  secreted titer above a few g/L, and whether the unphosphorylated protein makes cheese like dairy casein.
+ *Real plant costs.* Capital, staffing and running costs of recent PF plants would settle the vessel
  price basis and the fixed-cost rule (aseptic vessels would add #usd(R.base_aseptic.blg.msp_ccf - blg.msp_ccf, d: 1)/kg;
  the two accounting conventions differ by #usd(blg.msp_ccf - R.base_light.blg.msp_ccf, d: 1)/kg on BLG).
+ *The design ceiling.* Workable starting volumes, feed concentrations and O#sub[2] transfer at scale.

*Animal welfare.* The cost model does not say which protein matters most for animals, but the
products differ: whey is a by-product of cheese, so displacing it mostly lowers the whey price; casein
is what milk is bought for, and egg white (OVA, ovomucoid) carries far more animal-years per kg of protein than either.

*EU.* At Dutch sugar, energy, wage and construction prices the BLG plant costs about
#usd(R.policy.at("EU base") - R.policy.at("US base"), d: 1)/kg more; a capital charge at 4% over 20 years
instead of 7.5% over 10 would cut #usd(R.policy.at("EU base") - R.policy.at("EU, capital at 4%/20 yr"), d: 1)/kg.
Cost effects on one plant, not policy recommendations.

#text(size: 8.3pt, fill: rgb("#52514e"))[*Caveats.* A production cost with a 14.6%/yr capital charge, not a
market price. Excludes R&D, licensing, regulatory, sales, start-up, failed batches and first-of-a-kind
premiums. Strain parameters rest on design values and company-reported averages (evidence grades B–C);
casein and lactoferrin titers are borrowed from other proteins or species. Ovomucoid and β-casein were
added in version 3 and albumin in version 4; they have been audited by AI reviewers only (docs/AUDIT.md). Full report, audit log, simulated expert reviews and
data: `pf-tea` repository.]
