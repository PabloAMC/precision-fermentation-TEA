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
#let alac = R.base.alac
#let CH = R.cheese
#let HM = R.heme
#let PRODS = R.base.keys()
#let NAME = (blg: "BLG", ova: "OVA", ovd: "ovomucoid", cas: "β-casein", lf: "lactoferrin", alb: "albumin", alac: "α-lac")
#let MKT(p) = {
  let m = inc.values().find(d => d.compare_to.contains(p))
  if m != none { m.band } else { R.at((lf: "lactoferrin", alb: "albumin", alac: "alac").at(p)).reported_prices.band }
}
#let where(x, band) = {
  let (lo, hi) = (band.at(0), band.at(1))
  if x < lo { "below" } else if x <= hi { "inside" } else { "above" }
}
#let IB = LF.reported_prices.comparators.find(c => c.key == "lf_cost_intelligen2026_case_b_cex")
#let wheyobs = inc.whey.series.values().map(s => s.values()).flatten()
#let above(x) = wheyobs.filter(p => p >= x).len()

#set page(paper: "a4", margin: (x: 1.8cm, y: 1.0cm))
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 9.6pt)
#set par(justify: true, leading: 0.5em, spacing: 0.7em)
#set table(stroke: none, inset: (x: 4pt, y: 2.3pt))
#show table: set text(size: 8.6pt)

#let BD(q) = R.best_design_base.at(str(q), default: none)
// the price in one equation: capital-related charges are fixed fractions of the investment (report/common.typ, CORE)
#let P = yaml("../data/pf/base.yaml")
#let CRF = { let i = P.finance.ccf_rate.value; i / (1 - calc.pow(1 + i, -P.finance.ccf_life_y.value)) }
#let FIXED = P.finance.maintenance_frac_tci.value + P.finance.insurance_tax_frac_tci.value
#let CAP = blg.per_kg.at("capital charge") + blg.per_kg.maintenance + blg.per_kg.insurance
#let QP(q) = R.physical_limit.at("blg/humbird/q_p_max_" + str(q), default: none)

#text(size: 13pt, weight: "bold")[Precision-fermented dairy, egg and serum proteins: what they cost, and where evidence would help]
#v(-0.3em)
#text(size: 8.5pt, fill: rgb("#52514e"))[Memo · v4.1, seven proteins (#R.generated) · Pablo Antonio Moreno Casares · techno-economic model `pf-tea`,
Humbird (2021) method, checked against NREL, Intelligen and Voutilainen designs · prepared with an AI assistant; not yet reviewed by human experts · the views expressed are the author's own and do not represent the views of the European Commission]

*How the price works.* Figures are minimum selling prices: costs per kg of protein including a capital charge that repays
the plant over #P.finance.ccf_life_y.value years at #fx(100 * P.finance.ccf_rate.value, d: 1)% (#fx(100 * CRF, d: 1)% of the investment a year), not market prices.
Base β-lactoglobulin, #money(blg.msp_ccf)/kg: sugar #money(blg.per_kg.glucose), the plant #money(CAP) (that charge plus #fx(100 * FIXED)%/yr maintenance and insurance,
over what each m³ of fermenter makes), the rest #money(blg.msp_ccf - CAP - blg.per_kg.glucose). Each m³ makes more when cells secrete faster
(mg of protein per g of cells per hour); the _titer_ is grams per litre at harvest.

*Bottom line.*
- *Today's public strains cost far too much.* At the best peer-reviewed titers, β-lactoglobulin
  (BLG, whey), ovalbumin (OVA), ovomucoid (both egg white) and β-casein cost #money(S("academic/blg").msp_ccf),
  #money(S("academic/ova").msp_ccf), #money(S("academic/ovd").msp_ccf) and #money(S("academic/cas").msp_ccf) per kg
  of protein. The proteins they replace sold for #usd(inc.whey.band.at(0))–#usd(inc.whey.band.at(1)) (whey),
  #usd(inc.egg.band.at(0))–#usd(inc.egg.band.at(1)) (dried egg white) and #usd(inc.casein.band.at(0))–#usd(inc.casein.band.at(1))
  (casein) per kg of protein in 2015–2025 (2025 dollars). Only one public titer comes near the design point,
  and a company reports it: EVERY's 30 g/L ovomucoid patent example, at #money(S("academic/ovd_patent").msp_ccf).
- *At the titers in companies' own cost models, the commodity proteins near their markets.* At
  42 g/L, BLG costs #money(S("industry/blg").msp_ccf) (#money(S("industry/blg/light").msp_ccf) with
  design-report capital, NREL-style), OVA #money(S("industry/ova").msp_ccf), ovomucoid
  #money(S("industry/ovd").msp_ccf) and β-casein #money(S("industry/cas").msp_ccf). Whey sold above the BLG figure
  in #above(S("industry/blg").msp_ccf) of #wheyobs.len() annual export prices in 2015–2025. Casein has the thinnest
  evidence: no secreted casein titer is public.
- *Secretion, not titer, is the gate.* To reach \$20/kg, cells must secrete about
  #fx(req("blg/humbird", 20, 72).q_p_mg_g_h)–#fx(req("blg/humbird", 20, 48).q_p_mg_g_h) mg of protein per g of
  cells per hour at the base cell density. The base design secretes #fx(blg.design.q_p_mg_g_h, d: 1). With
  today's biology and capital, the best design reaches #money(BD(40).msp_ccf)/kg BLG at 40 mg/g/h and
  #money(BD(10).msp_ccf) at 10. No published *K. phaffii* process comes near either rate; the best glucose
  fed-batch we found reached 2.1.
- *Sugar is not the problem.* The base case's glucose (#usd(R.floor.products.blg.us_midwest.glucose_usd, d: 1)/kg BLG) costs no more than an animal's
  feed per kg of protein, with all the feed charged to protein (#usd(calc.min(..R.floor.animals.values().map(a => a.regions.us_midwest.feed)), d: 1)–#usd(calc.max(..R.floor.animals.values().map(a => a.regions.us_midwest.feed)), d: 1)
  in the US). The gap is everything but the feedstock: #usd(R.floor.products.blg.us_midwest.other, d: 0)/kg in the plant, against
  #usd(calc.min(..R.floor.animals.values().map(a => a.regions.us_midwest.other)), d: 0)–#usd(calc.max(..R.floor.animals.values().map(a => a.regions.us_midwest.other)), d: 0) on the farm.
- *A best case, not a floor.* Set every assumed limit at its best, with 400 m³ vessels and 100 kt/yr. If
  cells secrete 40 mg/g/h, BLG, OVA, ovomucoid and β-casein then cost #money(PL("blg/humbird").msp_ccf),
  #money(PL("ova/humbird").msp_ccf), #money(PL("ovd/humbird").msp_ccf) and #money(PL("cas/humbird").msp_ccf) per kg.
  At 10 mg/g/h BLG costs #money(QP(10).msp_ccf)\; at the best rate shown so far (2.1 mg/g/h), #money(QP(2.1).msp_ccf).
- *Scarce proteins are the easier case.* Intelligen's lactoferrin design reaches 10 g/L with methanol. At that
  titer, a 250 t/yr plant makes lactoferrin for #money(R.base_light.lf.msp_ccf)–#money(lfb.msp_ccf)/kg
  (#money(LF.cases.at("lf_methanol/humbird").msp_ccf) costed on methanol). That is #where(lfb.msp_ccf, MKT("lf")) the
  #money(MKT("lf").at(0))–#money(MKT("lf").at(1))/kg reported for dairy lactoferrin. At the best public methanol-free
  titer (2.8 g/L) it costs #money(S("academic/lf").msp_ccf), #where(S("academic/lf").msp_ccf, MKT("lf")) that range.
- *The route can change the product.* Precipitated, as dairy casein is, β-casein reaches dairy purity at
  #money(cas.msp_ccf)/kg. The only public yeast casein process uses membranes alone. Its powder is about
  6% β-casein and mostly yeast carbohydrate.
- *For cultivated-meat albumin, the columns set the cost.* We use the industrial process's minimal train
  (cation exchange, then anion exchange), cell-culture purity and a 1 kt/yr plant. Albumin then costs
  #money(alb.msp_ccf)/kg (#money(S("industry/alb").msp_ccf) at 42 g/L; #money(S("academic/alb").msp_ccf) at the
  best public titer, 8.7 g/L of broth made with methanol). Bulk bovine albumin sells for
  #usd(MKT("alb").at(0))–#usd(MKT("alb").at(1)), and GFI targets \$#ALB.cm.gfi_target_usd_kg/kg. Capture alone
  would cost #money(ALB.cases.at("alb_capture_only/humbird").msp_ccf), and a \$100/L resin
  #money(ALB.resin.at("dsp.cex_resin_usd_L=100")). Membranes alone cost #money(ALB.cases.at("alb_ufdf_only/humbird").msp_ccf)
  but reach only 77% albumin. At the base cost, albumin adds #usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(0) / 1000, d: 2)–#usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(2) / 1000, d: 2)
  per kg of cultivated meat, and leading firms are removing it from their media.
- *For α-lactalbumin and κ-casein, the strains are missing.* α-Lac, the infant-formula whey protein, costs
  #money(alac.msp_ccf)/kg at the base titer on a 1 kt/yr plant. Reports put α-lac at
  #usd(MKT("alac").at(0))–#money(MKT("alac").at(1)) per kg (market reports). At its best public titer (0.6 g/L of
  supernatant, human α-lac) it costs #money(S("academic/alac").msp_ccf). Rennet cheese needs κ-casein at about
  #fx(100 * CH.kappa_share.at(1))% of its casein. At the best κ titer (0.25 g/L), an α#sub[s1] + κ blend costs
  #money(CH.blend.kap.at(str(CH.kappa_share.at(1))).at(0))–#money(CH.blend.kap_cex.at(str(CH.kappa_share.at(1))).at(0))/kg.
  To add under 10%, κ co-precipitated with α#sub[s1] must reach roughly α#sub[s1]'s design titer. Heme from the
  best secreting strain, used at 0.45%, adds
  #usd(HM.cases.at("legh_chen2025/150/humbird").msp_ccf * HM.use.beef_analogue_frac.value, d: 2) per kg of
  beef analogue at the factory gate.

#table(
  columns: (2.1fr,) + PRODS.map(_ => 1fr),
  align: (left,) + PRODS.map(_ => right),
  table.header([*\$/kg protein, US*], ..PRODS.map(p => [*#NAME.at(p)*])),
  table.hline(stroke: 0.5pt + rgb("#c3c2b7")),
  [best published strain], ..PRODS.map(p => [#money(S("academic/" + p).msp_ccf)]),
  [base case (30 g/L; lactoferrin 10 g/L)], ..PRODS.map(p => [#money(R.base.at(p).msp_ccf)]),
  [base case, design-report capital], ..PRODS.map(p => [#money(R.base_light.at(p).msp_ccf)]),
  [industry benchmark (42 g/L)], ..PRODS.map(p => [#money(S("industry/" + p).msp_ccf)]),
  [physical-limit best case], ..PRODS.map(p => [#money(PL(p + "/humbird").msp_ccf)]),
  table.hline(stroke: 0.5pt + rgb("#c3c2b7")),
  [incumbent, 2025\$ per kg protein], ..PRODS.map(p => [#money(MKT(p).at(0))–#money(MKT(p).at(1))]),
)
#text(size: 8pt, fill: rgb("#52514e"))[Plants: 10 kt/yr (lactoferrin 250 t/yr, albumin and α-lac 1 kt/yr); physical limit at 100 kt/yr (lactoferrin 1.6 kt/yr, α-lac about 19 kt/yr). Albumin's incumbent: bulk bovine albumin (technical grade).]

*Where evidence would help most*, in our judgment:
+ *Secretion without growth.* How much protein does a strain secrete per g of cells per hour when it
  barely grows, over days, at 1–10 m³? This rate sets both today's cost and the best case, for every protein here.
+ *Open fed-batch data.* Titer, productivity and sugar yield, measured *together*. For casein: any
  secreted titer above a few g/L, and whether the unphosphorylated protein makes cheese like dairy casein.
  For bovine α-lac and κ-casein: any secreted titer above 1 g/L.
+ *Real plant costs.* The capital, staff and running costs of recent PF plants would settle the vessel
  price and the fixed-cost rule. Aseptic vessels would add #usd(R.base_aseptic.blg.msp_ccf - blg.msp_ccf, d: 1)/kg,
  and the two accounting conventions differ by #usd(blg.msp_ccf - R.base_light.blg.msp_ccf, d: 1)/kg on BLG.
+ *The design ceiling.* Workable starting volumes, feed concentrations and O#sub[2] transfer at scale.

*Animal welfare.* The cost model does not say which protein matters most for animals, but the
products differ. Whey is a by-product of cheese, so replacing it mostly lowers the whey price. Casein
is what people buy milk for. Egg white (OVA, ovomucoid) carries far more animal-years per kg of protein than either.

*EU.* At Dutch prices for sugar, energy, wages and construction, the BLG plant costs about
#usd(R.policy.at("EU base") - R.policy.at("US base"), d: 1)/kg more. Capital at 4% over 20 years,
instead of 7.5% over 10, would cut #usd(R.policy.at("EU base") - R.policy.at("EU, capital at 4%/20 yr"), d: 1)/kg.
These are cost effects on one plant, not policy recommendations.

#text(size: 8.3pt, fill: rgb("#52514e"))[*Caveats.* Costs exclude R&D, licensing, regulation, sales, start-up, failed batches and the premium of a
first plant. Strain parameters rest on published designs and company-reported averages.
The casein and lactoferrin titers come from other proteins or species. Only AI reviewers have audited the work since
version 2. Full report, audit log and data: the `pf-tea` repository.]
