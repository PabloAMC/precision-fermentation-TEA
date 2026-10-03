// The cost of precision-fermented dairy, egg and serum proteins: techno-economic analysis, v4 (seven proteins).
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
#let cas = R.base.cas
#let lfb = R.base.lf
#let alb = R.base.alb
#let ALB = R.albumin
#let alac = R.base.alac
#let AL = R.alac
#let CH = R.cheese
#let HM = R.heme
#let PRODS = R.base.keys()
#let NAME = (blg: "BLG", ova: "OVA", ovd: "ovomucoid", cas: "β-casein", lf: "lactoferrin", alb: "albumin", alac: "α-lac")
#let LONG = (blg: "β-lactoglobulin", ova: "ovalbumin", ovd: "ovomucoid", cas: "β-casein", lf: "lactoferrin", alb: "serum albumin", alac: "α-lactalbumin")
// each product's market band per kg protein (2025$): its incumbent's trade values, or reported prices (lactoferrin, albumin, α-lac)
#let REPORTED = (lf: "lactoferrin", alb: "albumin", alac: "alac")
#let MKT(p) = {
  let m = inc.values().find(d => d.compare_to.contains(p))
  if m != none { m.band } else { R.at(REPORTED.at(p)).reported_prices.band }
}
#let money(x) = if x == none { "—" } else if x >= 100 { usd0(x) } else { usd(x) }
// "$x (BLG), $y (OVA), ..." over every product, for a function of the product key
#let plist(f, ps: none) = (if ps == none { PRODS } else { ps }).map(p => money(f(p)) + " (" + NAME.at(p) + ")").join(", ")
#let COMMODITY = PRODS.filter(p => p not in REPORTED)
// "BLG inside its incumbent's band, OVA above it, ..." for a function of the product key
#let wlist(f, ps: none) = {
  // grouped by placement: "all four inside their incumbents' bands", "BLG and OVA inside ...; casein above ..."
  let ps = if ps == none { COMMODITY } else { ps }
  let groups = (:)
  for p in ps { let w = where(f(p), MKT(p)); groups.insert(w, groups.at(w, default: ()) + (NAME.at(p),)) }
  groups.pairs().map(((w, names)) => (if names.len() == ps.len() and ps.len() > 1 { "all " + ("", "one", "two", "three", "four", "five", "six", "seven").at(names.len()) }
    else { names.join(", ", last: " and ") }) + " " + w + " " + (if names.len() == 1 { "its incumbent's band" } else { "their incumbents' bands" })).join("; ")
}
#let xband(f, ps: none) = (if ps == none { COMMODITY } else { ps }).map(p => NAME.at(p) + " " + fx(f(p) / MKT(p).at(1), d: 1) + "–" + fx(f(p) / MKT(p).at(0), d: 1) + "×").join(", ")
#let tpy(d) = d.design.n_batches * d.design.target_per_batch_kg / 1000
// fermenter size of a result (m3): every batch ends at the maximum fill (scenarios.size_fermenter picks the size)
#let vol(d) = d.design.W_end_m3 / pv("fermenter.fill_max")
#let CAS = R.casein
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
#set document(title: "The cost of precision-fermented dairy, egg and serum proteins", author: "Pablo Antonio Moreno Casares")
#set page(paper: "a4", margin: (x: 2.3cm, y: 2.4cm), numbering: "1",
  header: context { if counter(page).get().first() > 1 [
    #set text(size: 8pt, fill: rgb("#898781"))
    Precision-fermented dairy, egg and serum proteins: techno-economic analysis #h(1fr) v4 (seven proteins), #R.generated
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
  #text(size: 17pt, weight: "bold")[The cost of precision-fermented dairy, egg and serum proteins]
  #v(0.2em)
  #text(size: 12pt)[A Humbird-style techno-economic analysis of β-lactoglobulin, ovalbumin, ovomucoid, \
  β-casein, lactoferrin, serum albumin and α-lactalbumin, from stoichiometry to the physical limit, \
  with notes on casein for rennet cheese and on heme]
  #v(0.6em)
  Pablo Antonio Moreno Casares
  #v(0.1em)
  #text(size: 9pt, fill: rgb("#52514e"))[Version 4 (seven proteins; v2.1 audited and AI pre-reviewed) for human review · numbers generated #R.generated · repository `pf-tea`]
]

#v(0.6em)
#note[
  *Status.* Not yet peer-reviewed. The model code, the evidence extraction and this text were
  produced with an AI assistant (Claude, Anthropic) under the author's direction. Version 1 was
  audited by eight independent AI reviewers, each owning one area and required to support every
  finding with a computation, quote or code line; version 2 was then read by four simulated expert
  reviewers (a fermentation scientist, a bioprocess engineer, a sceptic and the method's author's
  perspective), also AI. Every finding, decision and effect is logged in `docs/AUDIT.md` and
  `docs/REVIEW.md`, and version 2.1 implements them. Version 3 adds ovomucoid and β-casein and puts
  lactoferrin on the same footing as BLG and OVA; those additions were audited by three further AI reviewers (`docs/AUDIT.md`,
  v3 audit) but not by the simulated expert pre-review. Version 4 follows an independent AI review of the method against the
  published state of the art: methanol-induced production phases are now modelled, vessels are sized to the plant, and the
  Monte Carlo reports rank correlations; it adds serum albumin for cultivated-meat media and α-lactalbumin, and notes on
  casein for rennet cheese (α#sub[s1]- plus κ-casein) and on heme, audited by AI reviewers only (`docs/AUDIT.md`, v4). No human expert has reviewed the analysis yet.
  Every number is computed by the model and read from `results/analyses.json` at compile time;
  every input traces to a source and an evidence grade in `data/` (Appendix A). Inputs graded E are
  guesses; they are listed in @sec-limits.
]

// ---------------------------------------------------------------- abstract
#heading(level: 1, numbering: none)[Summary]

Precision fermentation (PF) uses an engineered microbe to secrete a single animal protein. We
estimate what seven proteins cost to make, and what performance would bring them to the
price of the proteins they replace: β-lactoglobulin (BLG, the main whey protein), α-lactalbumin (α-lac, the
second whey protein, sold enriched for infant formula), ovalbumin (OVA, the
main egg-white protein), ovomucoid (another egg-white protein, about 11% of it, sold by EVERY as a
heat-stable ingredient), β-casein (one of the two main caseins, the proteins of cheese curd), lactoferrin (a
scarce, high-value milk protein) and serum albumin, the carrier protein of the serum-free media in which
cultivated meat is grown, the one medium protein that would be needed by the thousand tonnes. The method is Humbird's (2021): element- and
electron-balanced black-box stoichiometry, an oxygen-transfer-limited fed-batch fermenter, and his
capital factors and fixed costs, with which his baker's-yeast workbook lands on that product's
market-implied cost. We add a secreted product, a methanol-induced production phase and three downstream
routes (membranes, isoelectric precipitation and ion exchange), and check the model against three
published designs.

The base case is a secreting *Komagataella phaffii* strain at 30 g/L after a 72 h production phase,
the design point of Intelligen's (2025) OVA process, in 200 m³ industrial fermenters making 10 kt/yr
of protein in the US Midwest (2025 dollars). Lactoferrin runs on its own published design (10 g/L,
cation exchange) at 250 t/yr, the size of its market, and albumin on the base design point with the
two-column train of the industrial recombinant-albumin process (cation-exchange capture, anion-exchange
polish) at 1 kt/yr, over a quarter of the lowest of GFI's 2030 demand scenarios and about the size of
today's whole human-albumin market. α-Lactalbumin runs BLG's membrane route at its isolate purity at
1 kt/yr, about a quarter of its high-purity market; small plants use smaller fermenters. With a capital charge of 14.6% of investment
per year the minimum selling price per kg of target protein is *#plist(p => R.base.at(p).msp_ccf)*.
With the lighter accounting of NREL-style design reports it is #plist(p => R.base_light.at(p).msp_ccf).
At the average titer that private companies' cost models assume (42 g/L, GFI 2025, a survey average
over unnamed proteins) it is #plist(p => S("industry/" + p).msp_ccf, ps: COMMODITY). At the best public
titers it is #plist(p => S("academic/" + p).msp_ccf) (@tab-key). Per kg of protein, in 2015–2025 and 2025
dollars, whey protein traded at #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0), dried
egg white (the incumbent for OVA and ovomucoid) at #usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0) and casein at
#usd(inc.casein.band.at(0), d: 0)–#usd(inc.casein.band.at(1), d: 0)\; dairy lactoferrin was reported at
#usd0(MKT("lf").at(0))–#usd0(MKT("lf").at(1)), bulk bovine serum albumin (our reading of GFI's
"high-value albumins" in trade data) at
#usd(MKT("alb").at(0), d: 0)–#usd(MKT("alb").at(1), d: 0) and dairy α-lactalbumin at
#usd(MKT("alac").at(0), d: 0)–#usd0(MKT("alac").at(1)) per kg of α-lac (all three grade C).

Eight results stand out:
1. *Cheap protein needs fast secretion more than high titer.* At the base cell density, \$20/kg BLG
   needs #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0)–#fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L
   in 48–72 h, a specific productivity of #fx(req("blg/humbird", 20, tpi(72)).q_p_mg_g_h, d: 0)–#fx(req("blg/humbird", 20, tpi(48)).q_p_mg_g_h, d: 0)
   mg protein per g cells per hour against #fx(blg.design.q_p_mg_g_h, d: 1) in the base design. With
   today's biology and capital, the cheapest design the model finds costs
   #usd(BD(40).msp_ccf)/kg if cells could secrete #fx(BD(40).design.q_p_mg_g_h, d: 0) mg/g/h (the ceiling we allow),
   and #usd(BD(10).msp_ccf) at 10 mg/g/h. No published *K. phaffii* process is near either rate. At the
   best rate demonstrated in a public glucose fed-batch, 2.1 mg/g/h (Prielhofer et al. 2018), the
   cheapest design costs #usd(BD(2.1).msp_ccf)/kg, and even the best case of point 3
   #usd(QP(2.1).msp_ccf)/kg, #where(QP(2.1).msp_ccf, inc.whey.band) the whey price band. The same holds
   for every protein here: none has a published secretion rate of its own.
2. *The titer ceiling is a design ceiling.* With Intelligen's 500 g/L glucose feed and a batch that
   must start at least 30% full, a 200 m³ fermenter at 107 g/L cells reaches about
   #fx(CEIL72, d: 0) g/L in a 72 h production phase; with a 600 g/L feed, about #fx(CEIL600, d: 0) g/L.
3. *A best case, not a floor.* With every assumed limit at its best at once, 400 m³ vessels and
   100 kt/yr, the cost per kg is #plist(p => PL(p + "/humbird").msp_ccf, ps: COMMODITY)\; lactoferrin,
   capped at its largest market estimate, #usd(PL("lf/humbird").msp_ccf). That assumes secretion at #fx(PL("blg/humbird").design.q_p_mg_g_h, d: 0) mg/g/h;
   at 10 mg/g/h the BLG case costs #usd(QP(10).msp_ccf), at 5 mg/g/h #usd(QP(5).msp_ccf).
4. *Capital: the vessel price and the fixed-cost rule.* Aseptic cell-culture vessels instead of
   industrial ones would add #usd(R.base_aseptic.blg.msp_ccf - blg.msp_ccf)/kg to the base BLG; the lighter
   design-report accounting would remove #usd(blg.msp_ccf - R.base_light.blg.msp_ccf), mostly through
   fixed costs of under 2% of investment a year instead of Humbird's 9%. Published NREL-style designs
   come out #pubratio×
   cheaper than our model of the same process, for those reasons; Intelligen's food-PF design comes
   out within #sgn(calrel("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)")) of ours.
5. *The market decides more than the process.* The same fermentation and accounting put the
   commodity proteins at #fx(calc.min(..COMMODITY.map(p => R.base.at(p).msp_ccf / MKT(p).at(1))), d: 1)–#fx(calc.max(..COMMODITY.map(p => R.base.at(p).msp_ccf / MKT(p).at(1))), d: 1)×
   the top of their incumbents' price bands at the base titer, and lactoferrin
   #where(lfb.msp_ccf, MKT("lf")) its reported range at its design titer, because dairy lactoferrin is
   scarce rather than a by-product. For casein the downstream route changes the product itself:
   precipitated, as dairy casein is, it reaches the 90% protein of the one precipitated PF casein on
   file at #usd(cas.msp_ccf)/kg, while the only public *K. phaffii* casein process uses membranes alone
   and makes a powder that is about 6% β-casein (@sec-routes).
6. *Albumin for cultivated meat: the columns, not the strain, set the cost.* Purified to a cell-culture
   grade by the minimal train of the industrial process (cation-exchange capture, then an anion-exchange
   polish), albumin costs #money(alb.msp_ccf)/kg at the base titer and #money(S("industry/alb").msp_ccf) at
   42 g/L, against #usd(MKT("alb").at(0), d: 0)–#usd(MKT("alb").at(1), d: 0) for bulk bovine albumin and the
   \$#ALB.cm.gfi_target_usd_kg/kg that GFI's cultivated-meat cost targets assume. Resin and the low recovery
   of the capture step (56%) carry most of it, at the most favourable resin life on record: capture
   alone would cost #money(ALB.cases.at("alb_capture_only/humbird").msp_ccf), a \$100/L polymeric resin on both
   columns #money(ALB.resin.at("dsp.cex_resin_usd_L=100")), and membranes alone
   #money(ALB.cases.at("alb_ufdf_only/humbird").msp_ccf), but they reach only 77% albumin, short of the
   96% grade. At
   #fx(ALB.cm.g_per_kg_cm.at(0), d: 0)–#fx(ALB.cm.g_per_kg_cm.at(2), d: 0) g of albumin per kg of
   cultivated meat that is #usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(0) / 1000, d: 2)–#usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(2) / 1000, d: 2)
   per kg of meat at the base cost (@sec-equiv).
7. *α-Lactalbumin: a whey protein whose strains are far behind.* On BLG's membrane route at its
   isolate purity it costs #money(alac.msp_ccf)/kg at the base titer on a 1 kt/yr plant
   (#money(AL.at_10kt.msp_ccf) at BLG's 10 kt/yr), #where(alac.msp_ccf, MKT("alac")) the reported
   #usd(MKT("alac").at(0), d: 0)–#usd0(MKT("alac").at(1)) band per kg of α-lac (grade C). The best public titer is
   0.6 g/L of human α-lac in the supernatant, #fx(S("academic/alac").design.titer, d: 2) g/L of broth (Wang et al. 2025; bovine
   α-lac in yeast: 2 mg/L), which costs #money(S("academic/alac").msp_ccf)/kg (@sec-q1).
8. *Two notes: casein for cheese and heme.* A rennet cheese needs κ-casein at about
   #pct(CH.kappa_share.at(1)) of its casein. Made by its own strain, κ must reach roughly α#sub[s1]'s own design
   titer for the blend to cost within 10% of α#sub[s1]-casein alone (#money(CH.as1.base.msp_ccf)/kg); at the best published
   κ titer, a 0.25 g/L patent example, the blend costs #money(CH.blend.kap.at(str(CH.kappa_share.at(1))).at(0))–#money(CH.blend.kap_cex.at(str(CH.kappa_share.at(1))).at(0))/kg (@sec-cheese).
   Soy leghemoglobin from the best published secreting strain costs
   #money(HM.cases.at("legh_chen2025/150/humbird").msp_ccf)/kg on a 150 t/yr plant: at Impossible's 0.45% use
   level that is #usd(HM.cases.at("legh_chen2025/150/humbird").msp_ccf * HM.use.beef_analogue_frac.value, d: 2)
   per kg of beef analogue ex works, equal to #pct(HM.cases.at("legh_chen2025/150/humbird").msp_ccf * HM.use.beef_analogue_frac.value / HM.use.beef_usd_kg.value)
   of US ground beef's retail price (@sec-heme).

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
#let pair(h, l) = if h == none [—] else [#money(h.msp_ccf)#if l != none [ (#money(l.msp_ccf))]]
#figure(
  table(
    columns: (2.0fr,) + PRODS.map(_ => 1fr),
    align: (left,) + PRODS.map(_ => right),
    table.header([*Scenario*], ..PRODS.map(p => [*#NAME.at(p)*])),
    hline,
    [Best public academic strain], ..PRODS.map(p => pair(S("academic/" + p), S("academic/" + p + "/light"))),
    [Base case (72 h production; lactoferrin #fx(lfb.design.t_total_h - lfb.design.t_growth_h, d: 0) h)], ..PRODS.map(p => pair(R.base.at(p), R.base_light.at(p))),
    [Industry benchmark (42 g/L, titer in private cost models)], ..PRODS.map(p => pair(S("industry/" + p), S("industry/" + p + "/light"))),
    [Best case at the best demonstrated secretion (2.1 mg/g/h)], ..PRODS.map(p => pair(R.physical_limit.at(p + "/humbird/q_p_max_2.1", default: none), none)),
    [Physical-limit best case (secretion 40 mg/g/h)], ..PRODS.map(p => pair(PL(p + "/humbird"), PL(p + "/light"))),
    [Base case with aseptic cell-culture vessels], ..PRODS.map(p => pair(R.base_aseptic.at(p), none)),
    [Base case as a pioneer plant (capital × 1.28, RAND)], ..PRODS.map(p => pair(R.base_pioneer.at(p), none)),
    hline,
    [Incumbent, per kg protein (2025\$)], ..PRODS.map(p => [#money(MKT(p).at(0))–#money(MKT(p).at(1))]),
    [Plant output (base), t/yr], ..PRODS.map(p => [#thou(tpy(R.base.at(p)))]),
  ),
  caption: [Minimum selling price (\$/kg target protein, 2025) with a capital charge of 14.6% of total
  capital investment per year: price-anchored capital, with design-report capital in brackets
  (@sec-capital). US Midwest; physical-limit cases at 100 kt/yr (lactoferrin at its largest market
  estimate; for albumin, GFI's high 2030 demand scenario). Best public titers: BLG #fx(S("academic/blg").design.titer, d: 1) g/L (Yao et al. 2026, ethanol-fed
  production priced as glucose; on glucose, Li et al. 2026, 5.14 g/L: #usd0(S("academic/blg_li2026").msp_ccf)/kg);
  OVA #fx(S("academic/ova").design.titer, d: 0) g/L in *T. reesei*, full-length and clipped summed (1 g/L
  of intact OVA: #usd0(S("academic/ova_intact_1gL").msp_ccf)/kg); ovomucoid #fx(S("academic/ovd").design.titer, d: 2) g/L
  (Kim et al. 2025; EVERY's 30 g/L patent example: #money(S("academic/ovd_patent").msp_ccf)/kg); β-casein
  #fx(S("academic/cas").design.titer, d: 1) g/L made inside *K. phaffii* cells and costed as if secreted (Choi and
  Jiménez-Flores 1996; a 3 g/L *E. coli* patent example: #money(S("academic/cas_patent").msp_ccf)/kg); lactoferrin #fx(S("academic/lf").design.titer, d: 1) g/L,
  porcine, the best methanol-free; albumin #fx(S("academic/alb").design.titer, d: 1) g/L of whole broth (17.47 g/L of
  supernatant) after 192 h of methanol induction, costed on methanol (Zhu et al. 2021; the best methanol-free, 1.5 g/L in a *S. cerevisiae* patent:
  #money(S("academic/alb_patent").msp_ccf)/kg)\; α-lac #fx(S("academic/alac").design.titer, d: 2) g/L of whole broth (0.6 g/L of human α-lac
  in the supernatant) after #fx(S("academic/alac").design.t_total_h - S("academic/alac").design.t_growth_h, d: 0) h on ethanol, priced as glucose (Wang et al. 2025).
  α-lac's plant is 1 kt/yr; its physical limit is capped at the food-grade α-lac market, 31.8 kt/yr. Incumbents: whey protein, dried egg white and casein trade unit
  values 2015–2025; lactoferrin, reported prices 2013–2025; albumin, bulk bovine serum albumin trade values
  (2023–2025); α-lac, market-report prices (2025; all three grade C where reported).],
) <tab-key>

#figure(image("../docs/figures/fig10_price_ladder.png", width: 100%),
  caption: [Every case against its market, one panel per protein: filled dots use price-anchored
  capital (the base), hollow dots design-report capital; the shaded band is the incumbent's price
  range in 2025 dollars. Model figures are production costs with a return on capital, not selling
  prices.]) <fig-ladder>

#outline(depth: 2, indent: 1.2em)
#pagebreak()

// ================================================================ 1
= Question and approach

PF companies now sell BLG (Perfect Day, Remilk, Vivici), OVA (EVERY) and lactoferrin (TurtleTree,
All G), others are entering (Onego Bio), and the first PF caseins are before regulators (Eden Brew in
Australia and New Zealand, Formo in the US). Recombinant serum albumin is already made in yeast and rice
for cell-culture media and drugs (Sartorius/Albumedix, InVitria, Healthgen), at catalogue prices of tens
of thousands of dollars per kg, and α-lactalbumin is in development (21st.BIO with Novonesis). Whether these proteins can displace animal proteins at scale or stay a premium niche
depends on what they cost to make. Published estimates disagree by a factor of several, and company
claims are rarely checked against the physics of aerobic fermentation. This study asks:

#quote(block: true)[
  What does it cost to make food-grade BLG, α-lactalbumin, OVA, ovomucoid, β-casein and lactoferrin, and serum albumin for
  cultivated-meat media, by precision fermentation with today's public strain performance, and at the
  physical limits of aerobic fermentation? What combination of titer, rate, yield, downstream design and
  scale would bring them to price parity with the whey, egg-white, casein, lactoferrin and bulk albumin
  they would replace?
]

#figure(
  table(
    columns: (0.3fr, 2.6fr, 1.8fr),
    align: (left, left, left),
    table.header([*\#*], [*Sub-question*], [*Answered in*]),
    hline,
    [Q1], [What do the proteins cost at public (academic) and claimed (industry) performance?], [@sec-q1, @fig-titer],
    [Q2], [What drives the cost, and how good is the evidence for each driver?], [@sec-q2, @fig-bridge, @fig-tornado, @fig-mc],
    [Q3], [Which combinations of performance reach price targets across each market (\$10–50 per kg protein; lactoferrin \$100–400; albumin \$10–100; α-lac \$25–130)?], [@sec-q3, @fig-required],
    [Q4], [What is the cost at the physical limits?], [@sec-q4, @fig-breakdown],
    [Q5], [Are published company claims consistent with the fermenter's limits?], [@sec-q5, @tab-claims],
    [Q6], [How much do siting (US vs EU) and scale (1–100 kt/yr) matter?], [@sec-q6, @fig-scale],
    hline,
    [Q7], [_Added after v1:_ what do these costs mean per litre of milk, per egg and (albumin) per kg of cultivated meat?], [@sec-equiv, @fig-equiv],
    [Q8], [_Added after v1:_ how does the downstream route change the product and its cost?], [@sec-routes, @fig-routes],
    hline,
    [Notes], [_Added in v4:_ what does casein that sets a rennet curd cost, and what does heme add to a plant-based burger?], [@sec-cheese, @sec-heme],
  ),
  caption: [Q1–Q6 were fixed for BLG and OVA before any model output existed (`docs/SCOPE.md`);
  Q7–Q8 were added at the author's request after the first draft; version 3 extends every question
  to ovomucoid, β-casein and lactoferrin, and version 4 to serum albumin and α-lactalbumin.],
)

*Why these benchmarks.* BLG is the main protein of whey, and the PF BLG on the market is sold as a
whey-protein ingredient for bars, drinks and dairy analogues (FDA GRN 1056 specifies a concentrate of
at least 70% protein). A buyer's alternative is whey protein concentrate or isolate, so their price
is the one PF BLG must meet; the same logic sets dried egg white against OVA and ovomucoid, dairy casein and
caseinates against β-casein, and dairy lactoferrin and α-lactalbumin against their PF versions. α-Lac is
fractionated from whey into enriched ingredients (about 45% of the protein) and isolates (90–96%) for
infant formula, which it brings closer to human milk; it has no trade code, so its price comes from
market reports (grade C). For whey it is a hard
comparison. Whey is a by-product of cheese, sold for whatever clears the market
once cheese has paid for the milk, and it is among the cheapest animal proteins; if PF displaced
much of it, its price would fall further.
Casein is the opposite case: it is what cheese is made of, and the milk is
bought largely for it, so displacing casein would cut milk output far more than displacing whey
(@sec-equiv). Lactoferrin is scarce (about 0.3–1.6 kt/yr worldwide) and sells for hundreds of dollars
per kg. Two consequences follow. Price parity is not the only commercial route: pure, animal-free or
functional proteins can sell at a premium. And the products differ in what displacing them would do
to animal numbers, which a cost model cannot settle but should state (@sec-equiv).
Albumin is different again: it is not a food. Cultivated-meat media use it at about 1 g/L
(GFI 2023), and recombinant proteins are almost all of a serum-free medium's cost at today's prices.
Its incumbent is bovine serum albumin, a slaughter by-product traded in bulk at tens of dollars per kg
for technical grades; GFI's cost targets for cultivated meat assume \$#ALB.cm.gfi_target_usd_kg/kg. Its
leverage on animals is indirect, through making cultivated meat cheaper, and it is shrinking as firms
remove albumin from their media (Wildtype's FDA file says it is "no longer used"; rapeseed protein,
methylcellulose and cyclodextrins replace it in published media).

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
ammonium-sulfate precipitation, following Intelligen's (2025) OVA design. Ovomucoid follows the
cleared product itself, EVERY's GRN 967: a UF/DF concentrate of at least 75% protein, 66–74% of the
powder ovomucoid (87.6–92.6% of its protein; the rest is yeast protein). β-casein follows the only
precipitated PF casein on file, Formo's α#sub[s1]-casein (FDA GRN 1312, pending): at least 90% protein,
more than 97% of it the casein, at most 5% moisture, sold here as sodium caseinate. Lactoferrin
follows the stricter of the recombinant bovine lactoferrin notices, All G's FDA GRN 1284: at least 90%
protein, at least 95% of it lactoferrin (TurtleTree's GRN 1219 allows 80% protein). Albumin has no
food-grade or media-grade specification; we use the cell-culture grade of recombinant human albumin
(InVitria's Cellastim S: at least 96% pure, at most 1 endotoxin unit per mg, the latter not modelled
because yeasts make no endotoxin). α-Lactalbumin follows the one high-purity α-lac specification in
the GRAS inventory, Agropur's dairy isolate (FDA GRN 763): at least 95% protein, at least 90% of it
α-lac, so 85.5% of the powder at the minimum and 90% at its typical 95% α-lac, which we use.

The plant is greenfield, single-product and nth-of-a-kind, built to food (not pharmaceutical) good
manufacturing practice. The base is 10 kt/yr of protein in the US Midwest, swept from 1 to
100 kt/yr, with a north-west Europe (Netherlands) variant. Lactoferrin's base is 250 t/yr, its
published design's output (Intelligen), swept from 0.1 to 10 kt/yr; a 10 kt/yr lactoferrin plant
would exceed the world market several times over. Albumin's base is 1 kt/yr (a design choice, grade D):
about today's whole human-albumin market and over a quarter of the lowest of GFI's 2030 cultivated-meat demand
scenarios (3.6–100 kt/yr). α-Lac's base is also 1 kt/yr (grade D): about a quarter of the
high-purity α-lac market (3.7 kt/yr) and 3% of the food-grade one (32 kt/yr; GFI Europe 2025, C).
Money is 2025 US dollars. Excluded costs:
R&D, strain licences, regulatory approval, sales and distribution, land, first-of-a-kind premiums
(shown separately: @sec-capital),
carbon pricing, start-up and commissioning, working capital (except in the discounted-cash-flow
price), failed batches, per-lot release testing and packaging. A reviewer (AI) put the last four at
roughly \$1–2/kg together. @fig-flow shows the base-case plant.

#figure(image("../docs/figures/fig0_flowsheet.png", width: 100%),
  caption: [Base-case process: *K. phaffii* secreting BLG at 30 g/L; flows per kg of BLG. α-Lac, OVA and ovomucoid use
  the same train; β-casein replaces the membrane concentration with isoelectric precipitation, and
  lactoferrin adds cation exchange before it and albumin cation then anion exchange (@sec-dsp, @fig-routes).]) <fig-flow>

== Stoichiometry and energetics

Each metabolic process is one element-balanced "black-box" reaction on C, H, O and N:
glucose + NH#sub[3] + O#sub[2] → biomass (or protein) + CO#sub[2] + H#sub[2]O. Electrons are
tracked through the degree of reduction γ per C-mol (glucose 4, *K. phaffii* biomass
#fx(K.gamma_biomass, d: 2), BLG #fx(K.gamma_blg, d: 2), OVA #fx(K.gamma_ova, d: 2), ovomucoid
#fx(K.gamma_ovd, d: 2), β-casein
#fx(K.gamma_cas, d: 2), lactoferrin #fx(K.gamma_lf, d: 2), albumin #fx(K.gamma_alb, d: 2), α-lac #fx(K.gamma_alac, d: 2)). This closes the O#sub[2] and CO#sub[2] balances once the carbon split is fixed.

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
- hen ovomucoid (P01005, 186 residues, 9 disulfides): C#sub[840]H#sub[1306]N#sub[240]O#sub[292]S#sub[20], 20.1 kDa;
- bovine β-casein, A2 variant (P02666, 209 residues): C#sub[1080]H#sub[1692]N#sub[268]O#sub[310]S#sub[6], 23.6 kDa;
- bovine lactoferrin (P24627, 689 residues): C#sub[3358]H#sub[5251]N#sub[945]O#sub[1002]S#sub[38], 76.1 kDa;
- human serum albumin (P02768, 585 residues, 17 disulfides, no N-glycan): C#sub[2936]H#sub[4590]N#sub[786]O#sub[889]S#sub[41], 66.4 kDa
  (bovine albumin is within 0.5% of it in composition);
- bovine α-lactalbumin (P00711, 123 residues, 4 disulfides): C#sub[626]H#sub[958]N#sub[162]O#sub[196]S#sub[9], 14.2 kDa
  (human α-lac, the protein of every *K. phaffii* titer, is within 0.5% in carbon and 3% in nitrogen);
- for the notes, bovine α#sub[s1]-casein (P02662, 199 residues): C#sub[1035]H#sub[1587]N#sub[265]O#sub[317]S#sub[5], 23.0 kDa;
  bovine κ-casein (P02668, 169 residues, 1 disulfide): C#sub[849]H#sub[1321]N#sub[223]O#sub[262]S#sub[4], 19.0 kDa; and
  soy leghemoglobin (P02236, 144 residues, without its heme): C#sub[702]H#sub[1096]N#sub[176]O#sub[212], 15.4 kDa.

Glycans and phosphates are left out of the formulas: 3–6% of the mass of glycosylated OVA and
5–10% of lactoferrin, which changes the mass balance by less than 1%. Milk β-casein carries five
phosphoserines (1.7% of its mass); yeasts and bacteria do not add them without a co-expressed milk kinase
(they lack Fam20C, which does): Formo's *E. coli* casein had none (GRN 1312), nor had a *K. phaffii*
β-casein without the kinase (NewMilkBuzz).

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
#fx(K.energetic.blg.ceiling, d: 3) g/g for BLG, #fx(K.energetic.ova.ceiling, d: 3) for OVA,
#fx(K.energetic.ovd.ceiling, d: 3) for ovomucoid,
#fx(K.energetic.cas.ceiling, d: 3) for β-casein, #fx(K.energetic.lf.ceiling, d: 3) for lactoferrin,
#fx(K.energetic.alb.ceiling, d: 3) for albumin and #fx(K.energetic.alac.ceiling, d: 3) for α-lac
(BLG #fx(K.energetic.blg.polymerisation_only, d: 3) and OVA #fx(K.energetic.ova.polymerisation_only, d: 3)
counting peptide bonds alone, as in version 2). Membrane transport, secretion, folding and turnover
are not counted, so it stays an upper bound. The base yield is #pct(blg.design.y_ps_over_ceiling) of
it. A different estimate, which treats protein synthesis as if it dissipated energy like growth
(Heijnen's correlation applied to the protein), gives #fx(K.heijnen_protein_yield.blg, d: 2) g/g for
BLG; it is not a bound, but it suggests the real ceiling sits below the ATP count.

*Methanol (version 4).* Many published titers come from strains induced with methanol (*AOX1*
promoter), among them every recombinant albumin titer above about 1.5 g/L. Version 3 priced those
production phases as glucose. The production phase can now run a fraction of its reactions on
methanol (`strain.methanol_frac_prod`: 0 in every base case, 1 for the methanol-induced academic
cases). Four pieces of physics change:
- *Carbon.* Methanol carries more electrons per carbon (γ = 6) than protein or biomass (γ ≈ 4.1), so
  making protein from it leaves surplus electrons, not surplus carbon. Every carbon of the product comes
  from methanol and the extra electrons go to O#sub[2]; yeasts do not use them to fix CO#sub[2] (Heijnen and
  van Dijken 1992; Kleerebezem and van Loosdrecht 2010). That caps the product yield at about 0.70 g per g
  methanol on carbon alone.
- *Energy.* The first step, alcohol oxidase, hands methanol's first two electrons to O#sub[2] as hydrogen
  peroxide and conserves no energy; only the formaldehyde and formate dehydrogenases feed respiration,
  so a methanol yields #pv("energetics.methanol_respired_O") × P/O ATP, against
  #fx(K.atp_per_glucose / 6, d: 2) per carbon of glucose. The product yield on methanol is set at the same
  fraction of its energetic ceiling as the glucose yield (an assumption, grade D): albumin's ceiling on
  methanol is #fx(K.energetic.alb.ceiling_methanol, d: 3) g/g and its yield
  #fx(K.energetic.alb.y_ps_methanol, d: 3) g/g. Without maintenance the biomass yield on methanol comes out
  at #fx(K.Yx_max_methanol, d: 2) g/g, just above the 0.40 g/g measured in methanol chemostats
  (Tomàs-Gamisans et al. 2018) and the 0.43 of a pilot fed-batch (Gao et al. 2023, via Shemesh and
  Fishman 2024), which include maintenance; on glucose the model gives #fx(K.Yx_max, d: 2) against a measured 0.50–0.56.
- *Maintenance* is measured, not derived, because the alcohol-oxidase loss is invisible to a
  Gibbs-energy correlation: 0.016 g methanol per g cells per hour in a methanol fed-batch (Dietzsch et al.
  2011), scaled by the same threefold fall at near-zero growth that the glucose value carries (Rebnegger
  et al. 2016): #fx(pv("hosts.kphaffii.m_s_prod_methanol_g_g_h"), d: 4) g/g/h (grade D; the measured 0.016 is the
  high end). Per unit of Gibbs energy that is about 1.5–1.7× the glucose maintenance, roughly the share of
  methanol's energy that alcohol oxidase wastes. Methanol chemostats fitted with a genome-scale model
  give a lower non-growth demand, 0.44 mmol ATP per g cells per hour (Tomàs-Gamisans et al. 2018), i.e.
  #fx(0.44 / (2 * pv("hosts.kphaffii.po_ratio")) * 32.042 / 1000, d: 4) g/g/h at #fx(2 * pv("hosts.kphaffii.po_ratio"), d: 2) ATP per methanol (our arithmetic). That
  supports a value well below the measured 0.016, though for a different reason than the near-zero-growth
  scaling: it does not confirm the scaling itself.
- *Feed and heat.* Methanol is fed neat (#pv("fermenter.feed_methanol_g_L") g/L), with no water, at
  \$#fx(pv("media.methanol_price_usd_kg"), d: 2)/kg. Heat and O#sub[2] follow from the formation enthalpies
  as for glucose; per mol of O#sub[2] they are nearly the same for both substrates, so methanol costs
  more through its price per electron, its extra O#sub[2] per kg of product and its maintenance.
Element and electron balances close for any methanol fraction (`tests/test_model.py`). Ethanol, which
one BLG strain is fed (Yao et al. 2026), is still priced as glucose. The flammable-solvent handling a
methanol plant needs is inside the missing-equipment allowance, not costed separately.

*Heat.* Heat release is computed from formation enthalpies of the dissolved species: about
480–510 kJ per mol O#sub[2] for growth and maintenance and 520–570 for the product reaction. The
fermenter uses its own computed heat when it slows growth to the heat-removal limit and when a
design's peak heat is checked; the 460 kJ per mol O#sub[2] of Roels (1983, via Almeida Benalcázar et
al. 2025; calorimetry gives 455 ± 15, Maskow et al. 2010) only screens the O#sub[2] limit.

#check[The dissipation formula and its units; the conversion of $m_G$ to 0.0174 g/g/h; the $Y_(p s)$
derivation (`tests/test_model.py::test_y_ps_reproduces_intelligen_eq2`); the ATP ceiling
(`src/pftea/plant.py`, `atp_per_residue`; `tests/test_model.py::test_energetic_ceiling_components`); the
methanol anabolism, which fixes no CO#sub[2], and the 2 × P/O ATP per methanol (`src/pftea/thermo.py`,
`anabolic`; `src/pftea/plant.py`, `methanol_yield`). The cost structure rests on these.]

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

== Downstream processing <sec-dsp>

Each protein has its own route (the specification sets it); all share cell removal, microfiltration
and spray drying. The membrane train (@fig-flow) follows Intelligen's OVA design, with
evidence-graded performance (`data/evidence/dsp.yaml`, `ovomucoid.yaml`, `casein.yaml`, `lactoferrin.yaml`, `albumin.yaml`, `alac.yaml`):
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
  We use #pct(pv("dsp.dryer_feed_solids_blg")) for BLG, #pct(pv("dsp.dryer_feed_solids_ova")) for OVA,
  #pct(pv("dsp.dryer_feed_solids_ovd")) for ovomucoid (which dissolves clear at 300 g/L; EVERY's own patents
  dry it from 5–6% solids, the low end of its range) and
  #pct(pv("dsp.dryer_feed_solids_lf")) for lactoferrin, #pct(pv("dsp.dryer_feed_solids_alb")) for albumin
  (sold as 20% solutions, Recombumin) and #pct(pv("dsp.dryer_feed_solids_alac")) for α-lac (by analogy with BLG:
  α-lac is soluble from pH 2 to 9, Layman et al. 2018; at 14.2 kDa it needs a tighter ultrafiltration membrane than BLG, whose lower
  flux is not modelled). Sodium caseinate is so viscous that dairy plants
  dry it from about #pct(pv("dsp.dryer_feed_solids_cas")) solids (Tetra Pak), so casein evaporates
  the most water per kg.
- *Spray dryer* at 4.87 MJ per kg water evaporated (industry survey, grade A); purchase cost from a
  supplier-based SuperPro model (Yver et al. 2012).
- *Isolate only:* ammonium-sulfate precipitation (350 g/L; 89% recovery), washed basket centrifuges;
  the dryer is fed the 20%-solids cake.
- *β-casein: concentration, then isoelectric precipitation.* Casein is least soluble near its
  isoelectric point, which is how dairy acid casein is made (pH 4.6). Formo recovers its PF
  α#sub[s1]-casein the same way, at pH 4 with phosphoric acid, from an extract of its cells (GRN 1312).
  Recombinant β-casein, without its phosphates, has a higher isoelectric point (5.5 by zeta potential),
  but it is least soluble at pH 4.5, where it behaves like milk β-casein: 22% of it stayed dissolved
  against 21% for the native protein, while at pH 4 half stayed dissolved (Chezan et al. 2026, a
  dilute, unheated assay). The model therefore precipitates at pH 4.5. The microfiltered broth is first
  ultrafiltered, without diafiltration, to the casein concentration of skim milk
  (#pv("dsp.acid_precip_feed_g_L") g/L), so that dairy data apply to a similar feed. It is then
  acidified with H#sub[3]PO#sub[4] at #pv("dsp.acid_h3po4_kg_per_m3") kg/m³ (milk's buffer capacity per m³ from
  pH 6.6 to 4.6, an analogy, grade D; range #P.dsp.acid_h3po4_kg_per_m3.low–#P.dsp.acid_h3po4_kg_per_m3.high),
  heated to #pv("dsp.acid_precip_temperature_C") °C for 20 min (in Standing Ovation's patent recombinant
  β-casein precipitated only partly at 40 °C and fully at 90 °C) with #pct(pv("dsp.acid_heat_recovery"))
  regenerative heat recovery (a guess), recovered at #pct(pv("dsp.acid_precip_recovery")) (dairy recovers
  essentially all its casein; grade D; the assay's 78% is the low end), washed in
  #pv("dsp.acid_wash_stages") countercurrent decanter stages with #pv("dsp.acid_wash_L_per_kg") L of water
  per kg, redissolved with #pct(pv("dsp.acid_naoh_kg_per_kg"), d: 0) NaOH by weight (Tetra Pak) and
  spray-dried as sodium caseinate (a design choice: drying the curd as acid casein, as Formo sells it,
  would be cheaper). Decanters are costed on the disk-stack centrifuge curve (no decanter quote on
  file); the heater on the HTST sterilizer curve.
- *Lactoferrin: cation-exchange capture* between microfiltration and ultrafiltration, as in the dairy
  process and every commercial PF lactoferrin: binding capacity #pv("dsp.cex_dbc_g_L") g/L of resin and
  #pv("dsp.cex_cv_per_cycle") column volumes of buffer per cycle (EVERY patent), elution at 1 M NaCl,
  #pct(pv("dsp.cex_recovery"), d: 1) step recovery, and resin at \$#thou(pv("dsp.cex_resin_usd_L"))/L
  (Petrides) lasting #thou(pv("dsp.cex_resin_life_cycles")) cycles (industrial lactoferrin columns,
  Pires et al. 2025). The column is loaded with dilute microfiltered broth,
  #fx(lfb.design.cex_load_cv, d: 0) column volumes per cycle, so a cycle takes
  #fx(lfb.design.cex_cycle_h, d: 1) h at #pv("dsp.cex_flow_cv_per_h") column volumes per hour, the flow of
  Intelligen's design. The column hardware per litre of resin is a guess (grade E).
- *Albumin: cation-exchange capture* on the same equipment, with the column data of the industrial
  recombinant-albumin process (Delta Biotechnology's, now Sartorius's Recombumin; US 5,728,553 and
  US 6,638,740, grade B). Albumin (isoelectric point about 5) binds a cation exchanger when the clarified
  broth is brought to pH 4.5, where most yeast proteins and pigments do not, and elutes at pH 5.5 in
  dilute acetate (priced as NaCl), then a 2 M NaCl strip and 0.5 M NaOH: loading
  40 g/L, 34 column volumes of buffer per cycle (the patent's maximum step volumes), and a recovery of
  56% over the step, the midpoint of the patent's "anticipated" 46–66% (every public
  recombinant-albumin train recovers 46–68% overall; one dye-affinity capture step recovered 86%, Zhu et
  al. 2021, the high end). The capture eluate still holds a 45 kDa albumin fragment, yeast antigens and
  pigment, which the pharmaceutical train removes with dye affinity, gel filtration and anion exchange
  for 99.9% purity. For the cell-culture grade (96%) we take the patent's minimal claimed train, the
  capture followed by an *anion-exchange polish*, loaded at 30 g/L with no loss (the patent reports
  about 110% monomer yield over it, as dimers revert), at the capture column's resin price, resin life and
  buffer volumes (grade D); whether
  two columns suffice is a judgment, and capture alone is shown as the optimistic case (audit R12). The
  acid for the pH step, the octanoate of the patent's recipe and protease losses while broth waits at
  pH 4.5 are not costed.
- *Cleaning in place* (#fx(pv("dsp.cip_solution_kg_per_kg"), d: 1) kg solution per kg product,
  Intelligen; its chemicals are inside Humbird's maintenance charge) and *spent-cell disposal*
  (#usd0(pv("utilities.biomass_disposal_usd_t_dry"))/t dry cells in the US, a landfill tipping fee;
  #usd0(pveu("utilities.biomass_disposal_usd_t_dry"))/t in the EU, an anaerobic-digestion gate fee;
  both per wet tonne converted at the 15% dry solids of the model's centrifuge paste, with no
  dewatering or inactivation costed). Sale as feed or fertiliser would make it free or a credit.

The target protein share of the concentrate powder is 85% on a dry basis (grade D; the GRN 1056
minimum is 56%), and #pct(alac.design.purity_dry) for α-lac (the GRN 763 isolate; whether membranes alone reach it
past yeast protein and mannans is as open as for BLG); of the caseinate, #pct(pv("dsp.acid_target_frac_dry"))\; of the lactoferrin powder,
#pct(pv("dsp.cex_target_frac_dry"))\; of the albumin powder, #pct(alb.design.purity_dry). The base overall recovery is
#pct(blg.design.recovery) for BLG, #pct(R.base.ovd.design.recovery) for ovomucoid, #pct(cas.design.recovery)
for β-casein, #pct(lfb.design.recovery) for lactoferrin, #pct(alb.design.recovery) for albumin and
#pct(alac.design.recovery) for α-lac.

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

*Vessel size (version 4).* Capital buys whole fermenters, so a small plant in large vessels pays for
idle volume. The designer therefore picks the cheapest feasible plant over
#P.fermenter.size_choices_m3.value.map(str).join(", ", last: " and ") m³ vessels, at most #pv("fermenter.volume_cap_m3") m³
(the base vessel; published food-PF designs use 100–150 m³), on each product's base case, and keeps
that plant in its scenarios, tornado and Monte Carlo; the scale curve re-sizes at each output. The
commodity plants at 10 kt/yr keep 200 m³ (larger vessels would be cheaper still: 500 m³ is a
sensitivity); lactoferrin's 250 t/yr plant takes #fx(vol(lfb), d: 0) m³ vessels, as in
Intelligen's design, and the 1 kt/yr plants #fx(vol(alb), d: 0) m³ (albumin) and #fx(vol(alac), d: 0) m³ (α-lac).

*Pioneer plants (version 4).* The base is an nth-of-a-kind plant. RAND's study of 44 pioneer process
plants found that their estimates averaged 0.78 of the actual capital cost, excluding inflation and other
external causes (106 estimates; Merrow et al. 1981), and that they produced 72% of
design capacity in months 7–12 after start-up (94% for plants with no new process steps). We show a
pioneer case with capital × 1/0.78 = 1.28 (the reciprocal of RAND's mean ratio; the mean of the
reciprocals, the average overrun, would be about 1.36 by a first-order estimate, ours: please check), all
capital except the resin's first fill, separately and never in the base: #plist(p => R.base_pioneer.at(p).msp_ccf)
(@tab-key). RAND's regression would predict less cost growth for a plant of commercially proven unit
operations; the start-up shortfall is not modelled.

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
  a lower bound on its sugar use. Ovomucoid: the best peer-reviewed titer is 0.93 g/L in a 60 h
  glycerol fed-batch without methanol, at 176 g/L of cells in a 2.5 L vessel (Kim et al. 2025). EVERY's patent example, 30.19 g/L at about 140 h
  (B; vessel, cell density and feeding not stated), is shown as a variant; it is the only traceable
  number above 1 g/L (a 3.2 g/L figure in a 2025 review has no traceable source). β-casein: no company
  discloses a titer, and no secreted casein titer has been published for any yeast or fungus. In
  *K. phaffii*, β-casein made with methanol reached 0.7–1.0 g/L inside the cells, with only 1/20,000 of
  that secreted (Choi and Jiménez-Flores 1996), and a recent patent family found that *K. phaffii*
  secretes β-casein only once a milk kinase (Fam20C) is co-expressed, without giving a titer
  (NewMilkBuzz, EP 4 623 075). The academic case costs the #fx(S("academic/cas").design.titer, d: 1) g/L
  as if secreted, an analogy. A patent example in which *E. coli* makes 3 g/L of β-casein inside its
  cells (Standing Ovation, quantified by eye on a gel) is shown as a variant. Lactoferrin: 2.8 g/L of porcine lactoferrin in *K. phaffii* without
  methanol (Yen et al. 2024), an analogy for bovine; 5.4 g/L of human lactoferrin with methanol,
  measured by ELISA only (Lv et al. 2023), is a variant. Albumin: the highest recombinant-albumin titer
  published, 17.47 g/L after 192 h of methanol induction in a 5 L vessel (Zhu et al. 2021), is per litre of
  supernatant; the cells fill half the culture, and the paper's 21.84 g in 2.5 L gives 8.74 g/L of whole
  broth, the model's basis. The same group's 8.86 g/L of supernatant in 96 h (Zhu et al. 2018; abstract
  only), scaled by the same ratio to 4.4 g/L, is a variant, as is the best methanol-free titer, 1.5 g/L in an 8 m³
  *S. cerevisiae* sucrose fed-batch (Delta's patent, B; costed as *K. phaffii* on glucose). Version 4
  costs every methanol-induced academic case on methanol (albumin; lactoferrin, Lv et al.; β-casein, Choi
  and Jiménez-Flores) instead of as glucose. α-Lactalbumin: the best titer in any host is 0.60 g/L of human
  α-lac, His-tagged, in the supernatant of a 3 L *K. phaffii* culture fed ethanol for over 90 h at pH 3, which
  suppressed proteases (Wang et al. 2025); it is converted to whole broth with the model's cell volume at the base
  cell density (×0.64, D; only OD was reported) and costed on glucose. The authors say their assay underestimates the
  titer through proteolysis, by an amount not given. Bovine α-lac, the dairy protein, has reached 2 mg/L in yeast (Viaene et al. 1991):
  the protein unfolds and sticks to cells below pH 5.5, so solubility and protease control pull the culture pH
  in opposite directions. Yield and maintenance keep the base values: no
  measured product yield exists.
- *industry:* 42 g/L, the average that Hawkwood computed over private companies' models of
  unspecified secreted proteins for GFI (2025) (grade C), with everything else at each product's base
  case. It is not a measured titer for any of the seven, and least informative for casein, lactoferrin
  and α-lac, whose public titers are one to two orders of magnitude lower.
- *required:* the inverse problem: the titer needed for \$10, \$20 and \$50/kg (lactoferrin \$100,
  \$200 and \$400; albumin \$10, GFI's target, \$50, inside the bulk-albumin band, and \$100; α-lac \$25
  and \$130, the ends of its band per kg of α-lac, and \$60) at each production time.
- *physical limit:* a best case at assumed limits, not a floor set by physics. Every lever moved
  from the base: product yield #yaml("../data/pf/scenarios/physical_limit.yaml").common.at("strain.Y_ps_g_g") g/g (95% of
  BLG's energetic ceiling); the lowest measured maintenance in both phases; no growth in production; a
  600 g/L glucose feed (Shemesh and Fishman 2024; 730 g/L has been fed in a 2.6 L laboratory vessel, Heyland
  et al. 2010, which would raise the ceiling somewhat further); 400 m³ vessels; O#sub[2] transfer capped at 250 mol/m³/h
  per m³ of cell-free liquid (head pressure, not costed; grade D) and heat removal at 40 kW/m³
  (external exchangers, not costed; grade D); an 8 h turnaround; a 90% concentrate; contract sugar;
  and 100 kt/yr (lactoferrin: 1,588 t/yr, the larger of two world-market estimates; α-lac: 31.8 kt/yr,
  its food-grade market; for albumin, 100 kt/yr is GFI's high 2030 demand scenario). The yield is
  the same for every protein; it is #pct(yaml("../data/pf/scenarios/physical_limit.yaml").common.at("strain.Y_ps_g_g") / K.energetic.cas.ceiling) of β-casein's ceiling, the
  lowest. A search over cell density and production time puts the titer at its feasibility
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
  basis, minimum fill, secretion ceiling) are not sampled; they are shown one at a time. Version 4
  adds the global counterpart of the tornado: the rank correlation (Spearman's ρ) of each sampled input
  with the cost over the feasible draws. With independent inputs, ρ² approximates each input's share of
  the spread in the cost's ranks.

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

#let items = (
  ("capital charge (14.6%/yr)", ("capital charge",)), ("maintenance", ("maintenance",)),
  ("insurance (Humbird's 5%, all overheads)", ("insurance",)), ("glucose", ("glucose",)), ("labour", ("labour",)),
  ("spent-cell disposal", ("biomass disposal",)), ("electricity", ("electricity",)),
  ("media, ammonia and DSP chemicals", ("salts & other media", "ammonia", "DSP chemicals")),
  ("gas, steam, water, membranes, resin", ("natural gas & steam", "water & wastewater", "membranes", "chromatography resin")),
)
#figure(
  table(
    columns: (2.4fr,) + PRODS.map(_ => 1fr),
    align: (left,) + PRODS.map(_ => right),
    table.header([*Cost item, \$/kg protein*], ..PRODS.map(p => [*#NAME.at(p)*])),
    hline,
    ..for (label, keys) in items {
      ([#label], ..PRODS.map(p => [#usd(keys.map(k => R.base.at(p).per_kg.at(k, default: 0)).sum(), d: 2)]))
    },
    hline,
    [*MSP#sub[CCF]*], ..PRODS.map(p => [*#usd(R.base.at(p).msp_ccf, d: 2)*]),
    [per kg powder], ..PRODS.map(p => [#usd(R.base.at(p).per_kg_powder, d: 2)]),
    [target protein, % of powder (dry)], ..PRODS.map(p => [#pct(R.base.at(p).design.purity_dry)]),
    [overall recovery], ..PRODS.map(p => [#pct(R.base.at(p).design.recovery)]),
    [plant output, t/yr], ..PRODS.map(p => [#thou(tpy(R.base.at(p)))]),
    [titer, g/L], ..PRODS.map(p => [#fx(R.base.at(p).design.titer, d: 0)]),
    [production fermenters], ..PRODS.map(p => [#fx(R.base.at(p).design.N_prod_int, d: 0) × #fx(vol(R.base.at(p)), d: 0) m³]),
    [total capital investment], ..PRODS.map(p => [#musd(R.base.at(p).tci)]),
    [glucose, kg per kg protein], ..PRODS.map(p => [#fx(R.base.at(p).physical.glucose_kg, d: 1)]),
    [electricity, kWh per kg], ..PRODS.map(p => [#fx(R.base.at(p).physical.electricity_kWh, d: 1)]),
    [natural gas, MJ per kg], ..PRODS.map(p => [#fx(R.base.at(p).physical.natural_gas_MJ, d: 0)]),
    [spent cells, kg dry per kg], ..PRODS.map(p => [#fx(R.base.at(p).physical.cells_kg, d: 1)]),
    [staff per kt/yr], ..PRODS.map(p => [#fx(R.base.at(p).physical.fte_per_kt, d: 1)]),
  ),
  caption: [Base case: *K. phaffii*, 72 h production (lactoferrin #fx(lfb.design.t_total_h - lfb.design.t_growth_h, d: 0) h), US Midwest, vendor-quote
  fermenters, price-anchored capital. BLG, OVA, ovomucoid and α-lac: UF/DF concentrate; β-casein:
  UF then isoelectric precipitation to sodium caseinate; lactoferrin: cation exchange; albumin: cation
  exchange then an anion-exchange polish.
  Fermenters are sized to each plant (@sec-capital).],
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
- *Why the commodity proteins differ so little.* BLG, OVA, ovomucoid and β-casein share the
  fermentation; they differ only in their downstream route, purity and recovery. Ovomucoid costs
  #dusd(R.base.ovd.msp_ccf - ova.msp_ccf) against OVA on the same membrane route: its cleared product
  is a less pure concentrate (#pct(R.base.ovd.design.purity_dry) against #pct(ova.design.purity_dry) of dry
  matter), so more solids are dried per kg of ovomucoid. β-casein costs
  #usd(cas.msp_ccf - blg.msp_ccf) more than BLG: the precipitation plant and its heater add capital,
  the caseinate dries from a dilute feed, and the acid is a new chemical line, while diafiltration
  is saved. Lactoferrin costs #fx(lfb.msp_ccf / blg.msp_ccf, d: 0)× BLG: one third of
  the titer, a longer batch, a cation-exchange step and a plant 40 times smaller.
- *Why albumin costs #fx(alb.msp_ccf / blg.msp_ccf, d: 0)× BLG at the same titer.* Its columns are the
  cost: resin alone is #usd(alb.per_kg.at("chromatography resin"), d: 0) per kg (a \$#thou(pv("dsp.cex_resin_usd_L"))/L
  resin lasting #thou(pv("dsp.cex_resin_life_cycles")) cycles at 40 g of albumin per litre loaded is
  \$#fx(pv("dsp.cex_resin_usd_L") / pv("dsp.cex_resin_life_cycles") / 0.040, d: 0) per kg loaded on the capture column, and
  the polish column adds about \$44 more at its 30 g/L loading), and with the capture step's 56% recovery
  only half of what is fermented is sold. The plant is also ten times smaller than BLG's. Resin life is the
  softest number: the base takes the one industrial measurement, over 1,000 cycles on whey lactoferrin,
  for a column fed pigmented yeast broth; at 125 cycles the base costs
  #usd0(ALB.resin.at("dsp.cex_resin_life_cycles=125"))/kg.
- *Why α-lac costs more than BLG on the same route.* Its plant is ten times smaller: at BLG's 10 kt/yr
  it would cost #money(AL.at_10kt.msp_ccf)/kg, against #money(blg.msp_ccf) for BLG. On the membrane route the
  model does not charge for purity: the target share only sets how much other dry matter travels to the
  dryer with the protein, so α-lac's range, #pct(float(AL.purity.keys().at(0))) to #pct(float(AL.purity.keys().at(1))) of dry matter,
  moves it only from #money(AL.purity.values().at(0)) to #money(AL.purity.values().at(1)). Whether membranes alone reach
  the isolate's 90% past yeast protein and mannans is the open question, not what it costs.

The product made per m³ of fermenter per hour is the lever the rest of the paper explores.

== Q1: cost against titer, with every public and claimed data point <sec-q1>

#figure(image("../docs/figures/fig1_cost_vs_titer.png", width: 100%),
  caption: [Minimum selling price against harvest titer for three production times, one panel per
  protein on its own base plant. Vertical lines mark the best public titers, the average titers
  assumed in published and private cost models (GFI 2025), and design or claimed titers. Lines end at
  the feasibility ceiling of the fermenter. Bands: each incumbent's price range.]) <fig-titer>

Cost falls roughly as 1/titer until the ceiling (@fig-titer). At the best public titers and at the
titer private cost models assume:

#figure(
  table(
    columns: (2.6fr, 1fr, 1fr, 1fr, 1.4fr),
    align: (left, right, right, right, right),
    table.header([*Protein*], [*Best public titer*], [*\$/kg there*], [*\$/kg at 42 g/L*], [*Incumbent, \$/kg protein*]),
    hline,
    ..for p in PRODS {
      ([#LONG.at(p)], [#fx(S("academic/" + p).design.titer, d: 1) g/L], [#money(S("academic/" + p).msp_ccf)],
       [#money(S("industry/" + p).msp_ccf) (#money(S("industry/" + p + "/light").msp_ccf))],
       [#money(MKT(p).at(0))–#money(MKT(p).at(1))])
    },
  ),
  caption: [The academic and industry scenarios against each incumbent (price-anchored capital;
  design-report in brackets). The best public titers and their caveats are in @tab-key.],
) <tab-q1>

- *Best public academic strains* leave each commodity protein at a multiple of its incumbent's band:
  #xband(p => S("academic/" + p).msp_ccf). The patent examples are far closer: EVERY's 30 g/L
  ovomucoid costs #money(S("academic/ovd_patent").msp_ccf)/kg
  (#fx(S("academic/ovd_patent").msp_ccf / MKT("ovd").at(1), d: 1)–#fx(S("academic/ovd_patent").msp_ccf / MKT("ovd").at(0), d: 1)×
  the egg-white band, the only public titer near the design point), and Standing Ovation's 3 g/L casein
  #money(S("academic/cas_patent").msp_ccf). BLG on glucose (Li et al. 2026, 5.14 g/L) costs #usd0(S("academic/blg_li2026").msp_ccf)/kg.
  Lactoferrin at its best methanol-free titer costs #usd0(S("academic/lf").msp_ccf)/kg,
  #where(S("academic/lf").msp_ccf, MKT("lf")) its reported price range; at 5.4 g/L (Lv et al. 2023,
  methanol, ELISA) #usd0(S("academic/lf_lv2023").msp_ccf). Albumin at the record titer (8.7 g/L of whole broth after
  192 h of methanol induction) costs #money(S("academic/alb").msp_ccf)/kg, at Zhu et al.'s 2018 titer
  #money(S("academic/alb_zhu2018").msp_ccf), and at the best methanol-free titer (1.5 g/L)
  #money(S("academic/alb_patent").msp_ccf). The model's methanol use in the record case,
  #fx(S("academic/alb").physical.methanol_kg * S("academic/alb").design.recovery, d: 0) kg per kg of albumin made, is
  #fx(58 / (S("academic/alb").physical.methanol_kg * S("academic/alb").design.recovery), d: 1)× less than the 58 kg that Zhu et al. fed, because their cells kept growing on methanol, to about 500 g/L
  of wet cells, while the model's barely grow in production: optimistic for this case.
- *α-Lactalbumin's strains are the furthest behind.* Its best public titer, 0.6 g/L of human α-lac in the supernatant
  (#fx(S("academic/alac").design.titer, d: 2) g/L of broth) on ethanol (Wang et al. 2025), costs #money(S("academic/alac").msp_ccf)/kg on
  #thou(S("academic/alac").design.N_prod_int) fermenters, #fx(S("academic/alac").msp_ccf / MKT("alac").at(1), d: 0)× the top of
  its reported band; the next best are 0.11 g/L (human, *K. phaffii*; Deng et al. 2023, abstract) and 0.12 g/L
  in a *Bacillus subtilis* flask (Zhu et al. 2024). The dairy (bovine) protein has reached 2 mg/L in yeast, and
  1 mg/L in *B. subtilis* (Wang et al. 2024). The GFI Europe/Arthur D. Little α-lac case assumes 20 g/L at
  0.13 g/g, about 33× the best public titer in the supernatant, and costs it at \$24/kg (membranes, food grade) and \$100/kg (with
  chromatography, above 99% pure). No company discloses a titer; 21st.BIO and Novonesis announced a bovine
  α-lac programme in 2025.
- *After α-lac, casein has the weakest public titers.* No company discloses one, and no secreted
  casein titer has been published for any yeast or fungus. In *K. phaffii* the best is
  #fx(S("academic/cas").design.titer, d: 1) g/L inside the cells (#usd0(S("academic/cas").msp_ccf)/kg costed as if
  secreted, on #thou(S("academic/cas").design.N_prod_int) fermenters); the best peer-reviewed casein titer in any
  host, which a 2026 review calls the highest reported, is 1.45 g/L of human α#sub[s1]-casein in *E. coli*.
  The base and industry cases for casein therefore borrow titers from other proteins.
- *The titer private cost models assume (42 g/L)* brings the commodity proteins to
  #plist(p => S("industry/" + p).msp_ccf, ps: COMMODITY) per kg: #wlist(p => S("industry/" + p).msp_ccf).

*The incumbents.* Official trade unit values form a consistent series, deflated to 2025 dollars with
the US consumer price index:
- *Whey protein >80%* (WPC80 and WPI mixed; US and EU exports): #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0)
  per kg protein in 2015–2025, taking the traded product as 80% protein, the minimum for its trade
  code. If the mix averaged 88% (more isolate), the band would be
  #usd(inc.whey.band.at(0) * 0.80 / 0.88, d: 0)–#usd(inc.whey.band.at(1) * 0.80 / 0.88, d: 0).
- *Dried egg albumin* (EU exports; 81.1% protein, USDA): #usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0).
- *Casein and caseinates* (EU exports; US import prices of acid and rennet casein, USDA Dairy Market
  News; 85.4% protein as sold, Southward): #usd(inc.casein.band.at(0), d: 0)–#usd(inc.casein.band.at(1), d: 0),
  and #usd(calc.min(..inc.casein.latest.values()), d: 1)–#usd(calc.max(..inc.casein.latest.values()), d: 1) in 2025.
- *Bulk serum albumin.* Albumins other than egg and milk albumin share one trade code, which mixes
  feed-grade plasma at \$3–5/kg with high-grade albumin at hundreds of dollars. The US and Dutch export
  unit values (\$42–58/kg in 2023) match GFI's (2025) "\$40 to \$70/kg in public trade databases", which we
  read as technical bovine serum albumin: #usd(MKT("alb").at(0), d: 0)–#usd(MKT("alb").at(1), d: 0) per kg
  (2025 dollars; grade C). Cell-culture recombinant albumin sells at
  #usd0(ALB.cm.catalogue_usd_kg.at(0))–#usd0(ALB.cm.catalogue_usd_kg.at(1)) per kg in 10–100 g packs (InVitria, 2026).
- *Dairy α-lactalbumin* has no trade code either. GFI Europe and Arthur D. Little (2025) give \$15/kg for
  food grade and \$123/kg for high purity, from online listings. Their own cost-in-use arithmetic shows these are per kg of
  ingredient at 60% and 95% α-lac, so per kg of α-lac the band is #usd(MKT("alac").at(0), d: 0)–#usd0(MKT("alac").at(1)) (grade C;
  our conversion). A market-research page gives \$31–86/kg for food grade, on an unstated basis; we show it as context only.
- *Dairy lactoferrin* has no trade code; reports and trade press give #usd0(MKT("lf").at(0))–#usd0(MKT("lf").at(1))
  per kg (2013–2025, deflated; grade C), partly from a PF seller, and the price is volatile (about
  \$200/kg nominal in the 2016 glut).
  #let evw = EQ.ingredient_per_unit.egg_vs_whey
  #let cheaper = evw.keys().filter(y => evw.at(y).egg < evw.at(y).whey)
  Egg white is not always dearer than whey: per kg of protein it was cheaper than the average whey
  export price in #cheaper.len() of #evw.len() years (#cheaper.join(", ")).
- *A 2026 whey spike.* WPC80 and WPI rose to about #usd(inc.whey.spot.at(0).usd_kg_protein, d: 0) per kg
  protein at the 2026 peak (USDA Dairy Market News narrative quotes, not a formal series). At that
  price the base case (#usd(blg.msp_ccf)) #if blg.msp_ccf < inc.whey.spot.at(0).usd_kg_protein [would undercut whey] else [would not undercut whey], as
  #if S("industry/blg").msp_ccf < inc.whey.spot.at(0).usd_kg_protein [would] else [would not] the industry
  benchmark (#usd(S("industry/blg").msp_ccf)). Against 2015–2025 prices, the industry benchmark is
  #{ let a = where(S("industry/blg").msp_ccf, inc.whey.band); let b = where(S("industry/blg/light").msp_ccf, inc.whey.band)
     if a == b [#a the band with either capital convention.] else [#a the band with price-anchored capital and #b it with design-report capital.] }

*Other protein ingredients* (@fig-context). Per kg of protein, plant protein concentrates and isolates
trade far below whey and egg white (#usd(R.benchmarks.context.find(c => c.key == "pea_protein_price_range_gfi2025").lo, d: 1)–#usd(R.benchmarks.context.find(c => c.key == "pea_protein_price_range_gfi2025").hi, d: 1)
for pea and soy, GFI 2025), and casein, gelatin and collagen sit around
#usd(R.benchmarks.context.find(c => c.key == "casein_price_range_gfi2025").lo, d: 0)–#usd(R.benchmarks.context.find(c => c.key == "casein_price_range_gfi2025").hi, d: 0).
PF proteins do not compete with plant proteins on price per gram of protein; they compete with the
dairy and egg ingredients whose functions (gelling, foaming, whipping, curd formation) they reproduce.

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
#let bvar(word) = R.bridge.filter(b => b.kind == "variant" and b.step.contains(word)).first()
The same plant making the other products, at the same titer, time and scale: OVA concentrate
#dusd(bvar("ovalbumin concentrate").msp - blg.msp_ccf)\; the OVA isolate, which adds precipitation and a second
recovery loss, #dusd(bvar("isolate").msp - blg.msp_ccf)\; β-casein by isoelectric precipitation
#dusd(bvar("casein").msp - blg.msp_ccf)\; lactoferrin with cation exchange #dusd(bvar("lactoferrin").msp - blg.msp_ccf).
The order of the steps changes their sizes, not the total.
#let infeas = R.bridge.filter(b => b.kind == "step" and b.flags.any(f => f.contains("productivity") or f.contains("OUR") or f.contains("initial fill")))
#if infeas.len() > 0 [The first #infeas.len() designs of the walk (marked † in @fig-bridge) break our
secretion ceiling: NREL's design makes 50 g/L of cellulase with only 6.6 g/L of cells, which implies
about #fx(float(infeas.at(0).flags.at(0).split(" ").at(2)), d: 0) mg/g/h. Their costs are shown for the walk only.]

#figure(image("../docs/figures/fig5_tornado.png", width: 92%),
  caption: [One-at-a-time sensitivity around each protein's industry benchmark (42 g/L, on its own
  plant), coloured by the evidence grade of each parameter's range; the ten largest swings per
  protein. † marks an end moved to the feasibility boundary.]) <fig-tornado>

*Tornado* (@fig-tornado). Around the BLG industry benchmark the largest swings are:
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

The other proteins share the ranking at the top, because they share the fermentation. Their three
largest swings:
#for p in PRODS.filter(p => p != "blg") [
  - *#LONG.at(p)* (industry benchmark #money(R.tornado_by_product.at(p).first().base)/kg):
    #R.tornado_by_product.at(p).slice(0, 3).map(t => lab(t.path) + " " + money(calc.min(t.msp_low, t.msp_high)) + "–" + money(calc.max(t.msp_low, t.msp_high))).join("; ").
]
Their own downstream inputs: for β-casein they rank lower, the largest being
#{ let t = R.tornado_by_product.cas.find(t => t.path.starts-with("dsp.acid_") or t.path == "dsp.dryer_feed_solids_cas"); if t == none [not in the ten largest] else [#lab(t.path) (#usd(calc.abs(t.msp_high - t.msp_low)), grade #t.grade)] },
for lactoferrin
#{ let t = R.tornado_by_product.lf.find(t => t.path.starts-with("dsp.cex_")); if t == none [not in the ten largest] else [#lab(t.path) (#usd0(calc.abs(t.msp_high - t.msp_low)), grade #t.grade)] },
and for albumin, where the column inputs lead,
#{ let t = R.tornado_by_product.alb.find(t => t.path.starts-with("dsp.cex_")); if t == none [not in the ten largest] else [#lab(t.path) (#usd0(calc.abs(t.msp_high - t.msp_low)), grade #t.grade, rank #(R.tornado_by_product.alb.position(x => x.path == t.path) + 1))] }.

Few strain-performance ranges are grade A; they rest on design values and company-reported averages,
because no public fed-batch dataset for any of the six reports titer, rate and yield together.

#figure(image("../docs/figures/fig7_montecarlo.png", width: 92%),
  caption: [Monte Carlo over each scenario's evidence ranges (triangular), feasible plants only; the
  black tick is the scenario's own value.]) <fig-mc>

*Monte Carlo* (@fig-mc). Over the evidence ranges the industry benchmark's median is
#usd(MC("industry/blg").p50, d: 0) for BLG (p10–p90 #usd(MC("industry/blg").p10, d: 0)–#usd(MC("industry/blg").p90, d: 0))
over feasible plants, and #usd(MC("industry/blg").p50_all, d: 0) (#usd(MC("industry/blg").p10_all, d: 0)–#usd(MC("industry/blg").p90_all, d: 0))
over all draws with a cost. #pct(MC("industry/blg").feasible_frac) of draws are feasible.
#let why = MC("industry/blg").infeasible_reasons
#let im = MC("industry/blg").input_means
#let whys = ("initial fill": " on the initial fill", "OUR": " on oxygen transfer (OUR)")
The rest fail as follows: #why.pairs().map(((k, n)) => str(n) + whys.at(k, default: " because " + k)).join(", "). The
failing draws are those with many cells at the start of production
(#fx(im.at("strain.X_prod_g_L").infeasible, d: 0) against #fx(im.at("strain.X_prod_g_L").feasible, d: 0) g/L on
average) and fast growth in production (#fx(im.at("strain.mu_prod_per_h").infeasible, d: 4) against
#fx(im.at("strain.mu_prod_per_h").feasible, d: 4)/h): they need so much feed that the batch would
have to start below 30% full. The scenario values sit at these percentiles of their own feasible
distributions: industry BLG #fx(MC("industry/blg").base_percentile, d: 0), industry OVA
#fx(MC("industry/ova").base_percentile, d: 0), academic BLG #fx(MC("academic/blg").base_percentile, d: 0),
academic OVA #fx(MC("academic/ova").base_percentile, d: 0). For the academic strains the p10 is
#usd0(MC("academic/blg").p10) (BLG) and #usd0(MC("academic/ova").p10) (OVA). For the other proteins the
industry medians (p10–p90, share of draws feasible) are
#PRODS.filter(p => p != "blg" and p != "ova").map(p => money(MC("industry/" + p).p50) + " for " + NAME.at(p) + " (" + money(MC("industry/" + p).p10) + "–" + money(MC("industry/" + p).p90) + ", " + pct(MC("industry/" + p).feasible_frac) + ")").join("; ").

#let rho3(k) = MC(k).at("rank_corr", default: (:)).pairs().filter(x => x.at(1) != none).sorted(key: x => -calc.abs(x.at(1))).slice(0, 3)
#figure(
  table(
    columns: (1.2fr, 3.4fr),
    align: (left, left),
    table.header([*Protein*], [*Largest rank correlations with cost, industry benchmark (ρ)*]),
    hline,
    ..for p in PRODS {
      ([#LONG.at(p)], [#rho3("industry/" + p).map(x => lab(x.at(0)) + " " + (if x.at(1) >= 0 { "+" } else { "−" }) + fx(calc.abs(x.at(1)), d: 2)).join("; ")])
    },
  ),
  caption: [The global counterpart of the tornado: Spearman's ρ between each sampled input and the cost over
  the feasible Monte Carlo draws of each industry benchmark. The sign says which way the input moves the cost;
  ρ² approximates its share of the spread. With about 150–250 feasible draws per case, |ρ| below about 0.15
  cannot be told from zero and close second and third entries cannot be ordered. Full lists: SI workbook,
  sheet MonteCarlo_rank.],
) <tab-rho>

*Which uncertainties matter jointly* (@tab-rho). Ranked by their correlation with cost across the draws,
the titer comes first for #PRODS.filter(p => rho3("industry/" + p).len() > 0 and rho3("industry/" + p).at(0).at(0) == "strain.titer_g_L").len() of the
#PRODS.len() proteins; for #PRODS.filter(p => rho3("industry/" + p).len() > 0 and rho3("industry/" + p).at(0).at(0) != "strain.titer_g_L").map(p => NAME.at(p)).join(" and ") the
column's inputs lead instead, as in the tornado.

== Q3: what must be true for price parity <sec-q3>

#figure(image("../docs/figures/fig3_required_titer.png", width: 100%),
  caption: [Titer needed for a target price, against production time, at the base cell density, one
  panel per protein on its own plant; targets bracket each market. Grey: designs the fermenter cannot
  run with a 500 g/L glucose feed. Dotted: the ceiling with a 600 g/L feed.]) <fig-required>

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

#let rq(p, tg) = { let r = R.required.at(p + "/humbird").at(str(tg)).at(tpi(72)); if r.titer == none [—] else [#fx(r.titer, d: 0)] }
#figure(
  table(
    columns: (2.2fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right, right),
    table.header([*Protein*], [*Targets (\$/kg)*], [*Lowest*], [*Middle*], [*Highest*], [*Ceiling*]),
    hline,
    ..for p in PRODS {
      let tg = R.required_targets.at(p)
      ([#LONG.at(p)], [#tg.map(str).join(", ")], rq(p, tg.at(0)), rq(p, tg.at(1)), rq(p, tg.at(2)),
       [#{ let c = R.titer_ceiling.at(p).at(tpi(72)); if c == none [—] else [#fx(c, d: 0)] }])
    },
  ),
  caption: [Titer (g/L) each protein needs for its three target prices with a 72 h production phase,
  price-anchored capital and each product's base plant, against the feasibility ceiling; — means not
  reachable below the ceiling. Lactoferrin's targets bracket its reported price range.],
) <tab-required-all>

The other proteins follow BLG (@tab-required-all): OVA, ovomucoid and β-casein need about the same
titers, β-casein slightly more because its downstream costs a little more. Lactoferrin reaches
\$#R.required_targets.lf.at(1)/kg at #rq("lf", R.required_targets.lf.at(1)) g/L, against a best public
methanol-free titer of #fx(S("academic/lf").design.titer, d: 1) g/L.
#let rqv(p, tg) = R.required.at(p + "/humbird").at(str(tg)).at(tpi(72)).titer
#let ta = R.required_targets.alb
For albumin, with its columns, cost flattens out as titer rises: at 72 h
#if ta.all(tg => rqv("alb", tg) == none) [none of its targets (#ta.map(tg => "$" + str(tg)).join(", ")/kg) is reached at any titer below the ceiling.] else [it reaches #ta.filter(tg => rqv("alb", tg) != none).map(tg => "$" + str(tg) + "/kg at " + fx(rqv("alb", tg), d: 0) + " g/L").join(" and ")#if ta.any(tg => rqv("alb", tg) == none) [, and #ta.filter(tg => rqv("alb", tg) == none).map(tg => "$" + str(tg)).join(" and ")/kg at no titer below the ceiling].] GFI's
\$#ta.at(0)/kg #if rqv("alb", ta.at(0)) == none [is out of reach of any titer with column purification.] else [needs #fx(rqv("alb", ta.at(0)), d: 0) g/L.]
#let tl = R.required_targets.alac
α-Lac, on BLG's route but a 1 kt/yr plant, #if rqv("alac", tl.at(0)) == none [cannot reach \$#tl.at(0)/kg, the low end of its reported band, at any titer below the ceiling;] else [reaches \$#tl.at(0)/kg, the low end of its reported band, at #fx(rqv("alac", tl.at(0)), d: 0) g/L;]
#if rqv("alac", tl.at(1)) != none [\$#tl.at(1)/kg needs #fx(rqv("alac", tl.at(1)), d: 1) g/L and] \$#tl.at(2)/kg, the high-purity price,
#if rqv("alac", tl.at(2)) == none [is out of reach] else [#fx(rqv("alac", tl.at(2)), d: 1) g/L], against a best public titer of
#fx(S("academic/alac").design.titer, d: 1) g/L of human α-lac.

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
  caption: [Cost structure from today's benchmarks to the physical-limit best case, one panel per
  protein (each on its own scale). The best academic strains are off these scales.]) <fig-breakdown>

The search (@fig-breakdown) finds the cheapest feasible design once every lever listed in
@sec-scen is at its assumed best. For BLG it has #fx(PL("blg/humbird").X_prod, d: 0) g/L cells,
a #fx(PL("blg/humbird").t_prod, d: 0) h production phase and #fx(PL("blg/humbird").titer, d: 0) g/L, at a
specific productivity of #fx(PL("blg/humbird").design.q_p_mg_g_h, d: 0) mg/g/h. The limits active there
are #PL("blg/humbird").binding.join(", ").

#figure(
  table(
    columns: (1.6fr, 1fr, 1fr, 0.8fr, 0.8fr, 0.8fr, 2fr),
    align: (left, right, right, right, right, right, left),
    table.header([*Protein*], [*Price-anchored*], [*Design-report*], [*Cells (g/L)*], [*Production (h)*], [*Titer (g/L)*], [*Limits that bind*]),
    hline,
    ..for p in PRODS {
      let d = PL(p + "/humbird")
      ([#LONG.at(p)], [#money(d.msp_ccf)], [#money(PL(p + "/light").msp_ccf)], [#fx(d.X_prod, d: 0)],
       [#fx(d.t_prod, d: 0)], [#fx(d.titer, d: 0)], [#d.binding.join(", ")])
    },
  ),
  caption: [The physical-limit best case of each protein: 100 kt/yr (lactoferrin 1,588 t/yr; α-lac
  31.8 kt/yr; for albumin, GFI's high 2030 demand scenario), 400 m³ vessels, secretion up to 40 mg/g/h, \$/kg target
  protein (2025).],
) <tab-pl-all>

It costs #usd(PL("blg/humbird").msp_ccf)/kg BLG with price-anchored capital and
#usd(PL("blg/light").msp_ccf) with design-report capital; for OVA #usd(PL("ova/humbird").msp_ccf) and
#usd(PL("ova/light").msp_ccf), for β-casein #usd(PL("cas/humbird").msp_ccf) and #usd(PL("cas/light").msp_ccf),
for lactoferrin at its market's size #usd(PL("lf/humbird").msp_ccf) and #usd(PL("lf/light").msp_ccf),
for α-lac at its food-grade market's size #usd(PL("alac/humbird").msp_ccf) and #usd(PL("alac/light").msp_ccf),
and for albumin #money(PL("alb/humbird").msp_ccf) and #money(PL("alb/light").msp_ccf), with its columns unchanged
(@tab-pl-all).
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
external heat-exchange loops that are not costed. For β-casein the O#sub[2] limit is more generous
still: at #fx(PL("cas/humbird").titer, d: 0) g/L the broth holds casein close to the concentration
above which dairy caseinate solutions become "very viscous" (about 150 g/L, Southward), which the model does
not represent. The
best cases are #wlist(p => PL(p + "/humbird").msp_ccf), lactoferrin's is
#where(PL("lf/humbird").msp_ccf, MKT("lf")) its reported range, α-lac's
#where(PL("alac/humbird").msp_ccf, MKT("alac")) its reported band, and albumin's is
#where(PL("alb/humbird").msp_ccf, MKT("alb")) the bulk-albumin band and
#if PL("alb/humbird").msp_ccf > ALB.cm.gfi_target_usd_kg [above] else [below] GFI's \$#ALB.cm.gfi_target_usd_kg/kg.

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
No casein or lactoferrin company discloses a titer, and EVERY's ovomucoid titer is a patent example
(the academic case), so the claims tested are for BLG, OVA or unnamed proteins. Of the #R.claims.len() claims and benchmarks, #reach.len() are feasible if the production phase is
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
  caption: [Each protein's industry benchmark against plant output, US Midwest and north-west Europe,
  both capital conventions. Lactoferrin's range spans its market; albumin's and α-lac's run from 0.1 to 10 kt/yr.]) <fig-scale>

*Scale* (@fig-scale). Going from 1 to 10 kt/yr cuts the price by
#usd(R.scale.curves.at("US, price-anchored").at(0) - R.scale.curves.at("US, price-anchored").at(3)), and going
from 10 to 100 kt/yr saves a further
#usd(R.scale.curves.at("US, price-anchored").at(3) - R.scale.curves.at("US, price-anchored").at(6)). Beyond about
10 kt/yr the plant adds 200 m³ fermenters rather than larger ones, so only the downstream train and
utilities keep scaling; larger vessels are a separate lever (@sec-q2). OVA, ovomucoid and β-casein follow the same
curve. For lactoferrin scale is the main lever: its industry benchmark costs
#usd0(R.scale_by_product.lf.curves.at("US, price-anchored").at(1)) at 250 t/yr (the scale curve re-sizes the vessels at
each output; @tab-key keeps the base plant),
#usd0(R.scale_by_product.lf.curves.at("US, price-anchored").at(4)) at 1,588 t/yr (the larger market
estimate) and #usd0(R.scale_by_product.lf.curves.at("US, price-anchored").last()) at 10 kt/yr, a plant
the market could not absorb. Albumin's base case (30 g/L; @fig-scale plots its industry benchmark) costs
#money(ALB.scale.curves.at("US, price-anchored").at(0)) at 100 t/yr,
#money(ALB.scale.curves.at("US, price-anchored").at(3)) at 1 kt/yr and
#money(ALB.scale.curves.at("US, price-anchored").last()) at 10 kt/yr: past about 1 kt/yr its resin, a cost per
kg that does not scale, dominates. α-Lac's industry benchmark follows BLG's curve shifted to smaller plants:
#money(R.scale_by_product.alac.curves.at("US, price-anchored").at(0)) at 100 t/yr,
#money(R.scale_by_product.alac.curves.at("US, price-anchored").at(3)) at 1 kt/yr and
#money(R.scale_by_product.alac.curves.at("US, price-anchored").last()) at 10 kt/yr.

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

The one-at-a-time effects need not add up to the gap exactly, because the inputs interact. For the
other proteins the Netherlands adds #PRODS.filter(p => p != "blg").map(p => usd(R.base_eu.at(p).msp_ccf - R.base.at(p).msp_ccf) + " (" + NAME.at(p) + ")").join(", ")
per kg on their base cases.

== Q7: milk, egg and cultivated-meat equivalents <sec-equiv>

#let beM = EQ.break_even_titer_72h.at("milk/blg")
#let beE = EQ.break_even_titer_72h.at("egg/ova")
#let milkfarm = EQ.sources.milk.prices.at("US farm milk (all-milk price)")
#let eggwh = EQ.sources.egg.prices.at("US wholesale eggs (New York, Grade A large)")
#let lastv(ser) = ser.at(ser.keys().sorted().last())
#figure(image("../docs/figures/fig8_equivalents.png", width: 100%),
  caption: [The cost of replacing the protein of a litre of milk with PF BLG or β-casein (left) and the
  egg-white protein of an egg with PF OVA or ovomucoid (right), against titer (72 h production, price-anchored
  capital), beside milk and egg prices in 2025 dollars. Lactoferrin (0.1–0.2 g per litre of milk) has
  no such unit; albumin's, per kg of cultivated meat, is in @tab-cm.]) <fig-equiv>

A litre of cow's milk holds 33.7 g of protein, 3.3 g of it BLG and about 27 g casein; a large egg
holds 3.64 g of egg-white protein, 1.96 g of it OVA (`data/evidence/milk_egg.yaml`). At the base cost,
the PF protein needed to replace all the protein of a litre of milk costs
#usd(EQ.cases.at("milk/blg").base.all_protein_per_unit, d: 2) as BLG and
#usd(EQ.cases.at("milk/cas").base.all_protein_per_unit, d: 2) as β-casein, against #usd(lastv(milkfarm), d: 2) for the litre
at the US farm gate in 2025 and #usd(lastv(EQ.sources.milk.prices.at("US retail whole milk")), d: 2) at
retail. Replacing one egg's white costs #usd(EQ.cases.at("egg/ova").base.all_protein_per_unit, d: 3) as OVA
and #usd(EQ.cases.at("egg/ovd").base.all_protein_per_unit, d: 3) as ovomucoid, against
#usd(lastv(eggwh), d: 3) per egg wholesale in 2025, a year of avian-influenza prices
(#usd(calc.min(..eggwh.values()), d: 3)–#usd(calc.max(..eggwh.values()), d: 3) over 2015–2025).

Dividing a source's price by its protein gives the price per kg of protein at which PF would match it:
US farm milk sold its protein at #usd(calc.min(..EQ.sources.milk.protein_equivalent.at("US farm milk (all-milk price)").values()), d: 0)–#usd(calc.max(..EQ.sources.milk.protein_equivalent.at("US farm milk (all-milk price)").values()), d: 0)/kg
in 2015–2025, and wholesale eggs their egg-white protein at
#usd(calc.min(..EQ.sources.egg.protein_equivalent.at("US wholesale eggs (New York, Grade A large)").values()), d: 0)–#usd(calc.max(..EQ.sources.egg.protein_equivalent.at("US wholesale eggs (New York, Grade A large)").values()), d: 0)/kg.
With a 72 h production phase (ceiling #fx(beM.ceiling, d: 0) g/L), BLG matches the 2025 farm-milk
protein price at
#{ let r = beM.rows.at("US farm milk (all-milk price) [2025]"); if r.titer == none [no feasible titer] else [#fx(r.titer, d: 0) g/L] }
and β-casein at
#{ let r = EQ.break_even_titer_72h.at("milk/cas").rows.at("US farm milk (all-milk price) [2025]"); if r.titer == none [no feasible titer] else [#fx(r.titer, d: 0) g/L] },
and OVA matches the lowest egg-white protein price of the decade at
#{ let r = beE.rows.at("US wholesale eggs (New York, Grade A large) [band low]"); if r.titer == none [no feasible titer] else [#fx(r.titer, d: 0) g/L] },
ovomucoid at
#{ let r = EQ.break_even_titer_72h.at("egg/ovd").rows.at("US wholesale eggs (New York, Grade A large) [band low]"); if r.titer == none [no feasible titer] else [#fx(r.titer, d: 0) g/L] }.

These are upper bounds on what the protein is worth: charging the whole price of milk or eggs to
their protein makes them look dearer per gram than they are, since fat and lactose carry much of the
milk price and the yolk part of the egg's. Bought as the incumbent ingredient, the same protein is
much cheaper: the white of one egg, as dried egg white, cost
#usd(calc.min(..EQ.ingredient_per_unit.dried_egg_white_per_egg.values()), d: 3)–#usd(calc.max(..EQ.ingredient_per_unit.dried_egg_white_per_egg.values()), d: 3)
in 2015–2025. Whey is a by-product of cheese: the whey protein of a litre of milk
(#fx(EQ.ingredient_per_unit.whey_g_per_L, d: 1) g) at WPC80/WPI prices was worth
#pct(calc.min(..EQ.ingredient_per_unit.whey_share_of_farm_milk.values()))–#pct(calc.max(..EQ.ingredient_per_unit.whey_share_of_farm_milk.values()))
of the US farm milk price in the same year, so replacing whey protein cuts milk output far less than
the "litre of milk" framing suggests. Casein is different: it is about four-fifths of milk protein and
what cheese is made of, so a cheese maker buying PF casein instead of milk removes demand for the
milk itself. For animal welfare, egg white (OVA, ovomucoid) is the strongest lever per kg of target protein: it involves
roughly 50–60 times more animal-years than whey BLG (about 0.6 kg OVA per hen-year against about 35 kg
BLG per cow-year). A cow yields about eight times more casein than BLG (about 280 kg a year at the same
milk yield), so per kg casein involves fewer cow-years than BLG; but displacing casein removes demand
for milk, while displacing whey, a by-product, mostly lowers the whey price. These figures are our
order-of-magnitude arithmetic, not model outputs, and they ignore substitution: one kg of PF protein
sold need not displace one kg of the animal product.

*Albumin, per kg of cultivated meat.* Albumin's unit is the meat its medium grows. GFI's (2023) demand
scenarios imply about #fx(ALB.cm.conc_g_L, d: 2) g of albumin per litre of medium (our arithmetic from its
tonnages), and 8–42 litres of medium per kg of cultivated meat (GFI 2023, after CE Delft 2021), so
#fx(ALB.cm.g_per_kg_cm.at(0), d: 0)–#fx(ALB.cm.g_per_kg_cm.at(2), d: 0) g of albumin per kg of meat:

#let cmrow(label, x) = ([#label], [#money(x)], ..ALB.cm.g_per_kg_cm.map(g => [#(if x * g / 1000 >= 100 { usd0(x * g / 1000) } else { usd(x * g / 1000, d: 2) })]))
#figure(
  table(
    columns: (2.6fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right),
    table.header([*Albumin at*], [*\$/kg albumin*], ..ALB.cm.medium_L_per_kg.zip(ALB.cm.g_per_kg_cm).map(((L, g)) => [*#L L/kg (#fx(g, d: 0) g)*])),
    hline,
    ..cmrow("GFI's target", ALB.cm.gfi_target_usd_kg),
    ..cmrow("bulk bovine albumin, low", MKT("alb").at(0)),
    ..cmrow("UF/DF only (optimistic route)", ALB.cases.at("alb_ufdf_only/humbird").msp_ccf),
    ..cmrow("industry benchmark (42 g/L)", S("industry/alb").msp_ccf),
    ..cmrow("base case (30 g/L)", alb.msp_ccf),
    ..cmrow("best public titer (methanol)", S("academic/alb").msp_ccf),
    ..cmrow("research catalogue (InVitria, 100 g)", ALB.cm.catalogue_usd_kg.at(0)),
  ),
  caption: [Albumin's cost per kg of cultivated meat (2025 \$), at GFI's implied #fx(ALB.cm.conc_g_L, d: 2) g/L and
  three medium uses. Model rows: price-anchored capital, 1 kt/yr.],
) <tab-cm>

At the base cost, albumin adds #usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(0) / 1000, d: 2)–#usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(2) / 1000, d: 2) per kg of
meat, a material share of a meat that must sell for a few dollars per kg; at GFI's \$10/kg it would add
#usd(10 * ALB.cm.g_per_kg_cm.at(0) / 1000, d: 2)–#usd(10 * ALB.cm.g_per_kg_cm.at(2) / 1000, d: 2), which is negligible, and at catalogue prices hundreds of
dollars (@tab-cm). That is the case for keeping albumin in media; the case against is that the leading
firms are removing it (@sec-limits). Its leverage on animals is indirect: if cultivated chicken
displaced chicken one for one, a kg of albumin would grow #fx(1000 / ALB.cm.g_per_kg_cm.at(2), d: 0)–#fx(1000 / ALB.cm.g_per_kg_cm.at(0), d: 0)
kg of meat (our arithmetic), conditional on cultivated meat reaching scale with albumin in its medium.

== Q8: the downstream route, the product and its cost <sec-routes>

#figure(image("../docs/figures/fig9_routes.png", width: 100%),
  caption: [Each protein's base route against its alternative: cost per kg of target protein (filled)
  and per kg of powder (hollow), with the target protein's share of the powder's dry matter. Stars:
  Intelligen's own lactoferrin model (costs of production; @tab-lf-rec). Bands: market prices per kg
  protein.]) <fig-routes>

The specification fixes the route, and the route can change what is sold more than what it costs
(@fig-routes, @sec-dsp):
- *BLG, OVA and ovomucoid.* A UF/DF concentrate (#pct(blg.design.purity_dry) target protein, dry basis;
  ovomucoid #pct(R.base.ovd.design.purity_dry), as EVERY's cleared product) against an ammonium-sulfate
  isolate (99%): the isolate adds #dusd(R.base_isolate.blg.msp_ccf - blg.msp_ccf)/kg for BLG,
  #dusd(R.base_isolate.ova.msp_ccf - ova.msp_ccf) for OVA and #dusd(R.base_isolate.ovd.msp_ccf - R.base.ovd.msp_ccf)
  for ovomucoid. EVERY's ovalbumin product adds chromatography (GRN 1104) and its ovomucoid product does
  not (GRN 967). α-Lac's concentrate is its isolate grade (#pct(alac.design.purity_dry)), as the dairy isolate and
  GFI Europe's membrane-only case are; precipitating it with ammonium sulfate adds
  #dusd(R.base_isolate.alac.msp_ccf - alac.msp_ccf)/kg. GFI Europe's above-99% grade adds a chromatography
  step, not modelled; in their numbers it raises the cost from \$24 to \$100/kg.
- *β-casein.* The only public *K. phaffii* casein process, Eden Brew's (FSANZ A1342), clarifies the
  broth and uses membranes alone. Its powder is 22% protein, of which about a quarter is β-casein, and
  68% yeast carbohydrate (cell-wall mannans and glucans): about 6% β-casein. In our model that route
  costs #usd(CAS.cases.at("cas_ufdf_edenbrew/humbird").per_kg_powder, d: 2)/kg of powder but
  #usd(CAS.cases.at("cas_ufdf_edenbrew/humbird").msp_ccf)/kg of β-casein, against
  #usd(cas.msp_ccf)/kg by precipitation. That comparison holds only at low titer: the variant keeps Eden
  Brew's composition, and at 30 g/L of casein the broth could not carry the yeast carbohydrate that
  composition implies (several hundred g/L; audit R10-5), so a 30 g/L strain's membrane-only powder would
  be purer and cheaper than shown. At 3 g/L the two routes cost about the same per kg of casein. What
  holds at any titer is that precipitation gives a dairy-casein grade product and the membrane route an
  ingredient of a different composition. Casein's own
  physics makes the precipitation route possible: it is insoluble near its isoelectric point, and,
  having almost no folded structure, survives heating to 90 °C, which denatures host proteins.
  Of the precipitation inputs with the weakest evidence, the acid dose and the heat recovery move the
  base little, but the recovery does not: at the ends of their ranges
  #CAS.levers.pairs().map(((k, v)) => lab(k.split("=").at(0)) + " " + k.split("=").at(1) + ": " + usd(v)).join("; ").
  No PF casein recovery is published; it is the input to measure first.
- *Lactoferrin.* Cation exchange (#pct(lfb.design.purity_dry) lactoferrin) against UF/DF alone
  (Intelligen's case a, purity by assumption): #money(lfb.msp_ccf) against
  #money(LF.cases.at("lf_ufdf_only/humbird").msp_ccf)/kg. Resin life is the largest downstream lever:
  at 125 cycles (biopharma practice) the base costs #usd0(LF.resin.at("dsp.cex_resin_life_cycles=125")).
- *Albumin.* Two columns (#pct(alb.design.purity_dry) albumin) cost #money(alb.msp_ccf)/kg, the capture
  column alone #money(ALB.cases.at("alb_capture_only/humbird").msp_ccf), and UF/DF alone
  #money(ALB.cases.at("alb_ufdf_only/humbird").msp_ccf)\; but albumin is only 77% of the protein in the best
  public broth (Zhu et al. 2021), so membranes alone make a different, below-specification product, as
  for casein. The columns' inputs decide where between: a
  polymeric resin at \$100/L on both columns gives #money(ALB.resin.at("dsp.cex_resin_usd_L=100")), resin at
  \$2,000/L #money(ALB.resin.at("dsp.cex_resin_usd_L=2000")), a resin lasting 125 cycles
  #money(ALB.resin.at("dsp.cex_resin_life_cycles=125")), loading 50 instead of 40 g/L
  #money(ALB.resin.at("dsp.cex_dbc_g_L=50"))\; the capture recovery at 40% or 86% gives
  #money(ALB.cases.at("alb_recovery_low/humbird").msp_ccf) or #money(ALB.cases.at("alb_recovery_high/humbird").msp_ccf).
  Inducing the base design with methanol instead of glucose adds
  #dusd(ALB.cases.at("alb_methanol/humbird").msp_ccf - alb.msp_ccf)/kg. A purification route as cheap as a food protein's, not a
  better strain, is what albumin near \$10/kg needs; on today's evidence the base sits at the favourable
  end of resin life and purification, and mid-range on recovery.

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
    [Our base design], [], [#usd(REC("lf_ufdf_only").cop, d: 1)], [], [#usd(REC("lf").cop, d: 1)],
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

At its design titer PF lactoferrin costs #usd0(LFC("lf/light").msp_ccf)–#usd0(LFC("lf/humbird").msp_ccf)
per kg (design-report to price-anchored capital), #where(LFC("lf/humbird").msp_ccf, LF.reported_prices.band) the
reported range for dairy lactoferrin in 2025 dollars (@sec-q1).

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
has been disclosed, so this is a cost comparison only.

== Casein for rennet cheese: α#sub[s1]- plus κ-casein <sec-cheese>

Our β-casein product is an acid-casein or caseinate grade. A rennet cheese is different: chymosin sets
the curd by cutting κ-casein, the casein on the micelle surface, so a casein without κ makes no rennet
curd. With fully recombinant, unphosphorylated proteins a patent example made rennet curds at 16.7–25% κ
(New Culture, US 2023/0404098, grade B); with dairy caseins, curds were firmest near 19% κ (Antuma et al.
2025), and milk casein is 12% κ (Runthala et al. 2023). We take #pct(CH.kappa_share.at(1)), over
#pct(CH.kappa_share.at(0), d: 1)–#pct(CH.kappa_share.at(2)). Formo makes a stretched-curd analogue from
α#sub[s1]-casein alone, by acid and calcium and without rennet (WO 2026/068856), so κ is needed for rennet
cheese, not for every cheese.

We cost the blend as two strains and two plants (`data/pf/scenarios/cheese.yaml`): α#sub[s1]-casein at the base
design point on β-casein's precipitation route, and κ-casein from its own strain, each plant sized for its share
of #thou(CH.casein_t_per_yr) t/yr of casein. How κ would be recovered is not known: no source measures it, and
unphosphorylated κ (computed isoelectric point 5.85) is the casein least pulled down by acid or calcium. Two cases
bracket it: κ *co-precipitated* with α#sub[s1], as milk κ is, costed on the precipitation route at a 78%
recovery (optimistic, grade E), and κ on *its own cation-exchange column*, on lactoferrin's column data (D).
Per kg of blend at κ share $s$,
$ c_"blend" = (1 - s) c_(alpha s 1) + s c_kappa (T_kappa). $
For the blend to cost at most 10% more than α#sub[s1] alone (a threshold we chose), $s (c_kappa - c_(alpha s 1)) <= 0.1 c_(alpha s 1)$,
i.e. $c_kappa <= c_(alpha s 1)(1 + 0.1 \/ s)$: at $s$ = #CH.kappa_share.at(1), κ may cost up to
#fx(1 + 0.1 / CH.kappa_share.at(1), d: 2)× α#sub[s1]. One strain secreting both in proportion would avoid
the second plant; it would cost what α#sub[s1] costs at the combined titer, provided κ is secreted at its share
of it, which no public strain shows.

#check[The blend cost is a mass-weighted average of two plants' costs; the 10% threshold and the
factor $1 + 0.1 \/ s$ follow from it in one line.]

#let s0 = str(CH.kappa_share.at(1))
#let kp(r, i) = CH.kap.at(r).at(s0).values().at(i)
#figure(
  table(
    columns: (1.4fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right),
    table.header([*κ-casein titer (g/L)*], [*κ co-precipitated, \$/kg*], [*Blend, \$/kg*], [*κ by column, \$/kg*], [*Blend, \$/kg*]),
    hline,
    ..for (i, t) in CH.grid.enumerate() {
      ([#fx(t, d: 2)#if i == 0 [ (best published)]],
       [#money(kp("kap", i).msp_ccf)], [#money(CH.blend.kap.at(s0).at(i))],
       [#money(kp("kap_cex", i).msp_ccf)], [#money(CH.blend.kap_cex.at(s0).at(i))])
    },
    hline,
    [α#sub[s1]-casein alone], table.cell(colspan: 4)[#money(CH.as1_by_share.at(s0))/kg on #thou(CH.casein_t_per_yr * (1 - CH.kappa_share.at(1))) t/yr; #money(CH.as1.at("base/10kt").msp_ccf) on #thou(CH.casein_t_per_yr) t/yr (β-casein: #money(cas.msp_ccf))],
  ),
  caption: [Rennet-cheese casein at #pct(CH.kappa_share.at(1)) κ: κ-casein made by its own strain and plant
  (#thou(CH.casein_t_per_yr * CH.kappa_share.at(1)) t/yr), on the two routes that bracket its unknown recovery, and the blend with
  α#sub[s1]-casein at its base case (price-anchored capital, US). κ titers from 0.25 g/L, the best published (a
  *K. lactis* flask in a patent), are costed as *K. phaffii* on glucose in 72 h.],
) <tab-cheese>

#let need(r, i) = CH.kappa_titer_for_10pct.at(r).at(str(CH.kappa_share.at(i)))
- *α#sub[s1]-casein costs what β-casein costs.* At the base design point it is #money(CH.as1.base.msp_ccf)/kg
  (#money(CH.as1.at("base/light").msp_ccf) with design-report capital) and #money(CH.as1.industry.msp_ccf) at 42 g/L, against
  #money(cas.msp_ccf) for β-casein: the two differ in their formula by about 1%. At the best peer-reviewed bovine
  α#sub[s1] titer, 1.13 g/L inside *E. coli* cells in a 15 mL flask (Wang et al. 2021), costed as if secreted, it is
  #money(CH.as1.academic.msp_ccf)/kg, and at half of a patent example's 5 g/L α#sub[s1] + β mix (Standing Ovation,
  EP 4 533 954) #money(CH.as1.patent.msp_ccf)/kg.
- *κ sets the blend's cost at today's κ titers.* The best published κ titer is about 0.25 g/L, secreted by
  *Kluyveromyces lactis* in a flask and measured by Western blot (Redbiotec, WO 2023/002061); the best peer-reviewed
  one is 4.14 mg/L, secreted by *Aspergillus oryzae* (Panchanawaporn et al. 2026), below what the model's batch can
  resolve. At 0.25 g/L the blend costs #money(CH.blend.kap.at(s0).at(0))–#money(CH.blend.kap_cex.at(s0).at(0))/kg,
  #fx(CH.blend.kap.at(s0).at(0) / CH.as1_by_share.at(s0), d: 0)–#fx(CH.blend.kap_cex.at(s0).at(0) / CH.as1_by_share.at(s0), d: 0)× α#sub[s1]
  alone. No company discloses a κ titer; κ from milk sells only as a laboratory reagent, at
  \$#thou(CH.kappa_lab_price_usd_g)/g.
- *The κ titer the blend needs.* Within 10% of α#sub[s1] alone, co-precipitated κ needs about
  #fx(need("kap", 1), d: 0) g/L (#fx(need("kap", 0), d: 0)–#fx(need("kap", 2), d: 0) g/L over the κ range), roughly
  α#sub[s1]'s own design titer, because κ's plant is smaller and its recovery lower;
  #if need("kap_cex", 1) == none [on its own column no titer up to 42 g/L is enough.] else [on its own column, #fx(need("kap_cex", 1), d: 0) g/L.]
  That design titer is itself assumed: the best peer-reviewed bovine α#sub[s1] titer is 1.13 g/L.

So casein for rennet cheese is gated by κ-casein: its best titer is over 100× below the design point, and
nothing public says how a recombinant, unphosphorylated κ would be recovered.

== Heme: a cost-in-use note <sec-heme>

Soy leghemoglobin (LegH) is the heme protein of Impossible Foods' beef analogue. The US lists it as a
colour additive at up to 0.8% of the uncooked analogue (21 CFR 73.520); Impossible uses 0.45% in beef and
0.25% in pork analogues (FSANZ A1186). What it sells, LegH Prep, is a frozen liquid concentrate of a cell
lysate: 6–9% LegH, at least 65% of its protein LegH (80% on average in five batches), LegH 38–51% of its
dry matter, made inside *K. phaffii* cells and released by bead milling (FDA GRN 737). The model has
secreted-protein routes only, so this note estimates the cost from the best published *secreting* processes
on the membrane route at LegH Prep's purity (43% of dry matter; `data/pf/scenarios/heme.yaml`). It is an
estimate, not a bound: lysis and debris removal are left out (too cheap), drying a product sold frozen is
counted (too dear), the published titers are per litre of supernatant, converted here to whole broth with the
model's cell volume (×0.64, D), and one strain's heme loading is unknown.

#let hcase(v, t) = HM.cases.at(v + "/" + str(t) + "/humbird")
#let use = HM.use.beef_analogue_frac
#figure(
  table(
    columns: (2.6fr,) + HM.scales.map(_ => 1fr) + (1.4fr,),
    align: (left,) + HM.scales.map(_ => right) + (right,),
    table.header([*Process*], ..HM.scales.map(t => [*#thou(t) t/yr, \$/kg LegH*]),
      [*\$/kg beef analogue at #pct(use.value, d: 2) (#pct(use.low, d: 2)–#pct(use.high, d: 1))*]),
    hline,
    ..for (v, label) in (("legh_chen2025", [Chen et al. 2025: 6.0 g/L of supernatant (#fx(hcase("legh_chen2025", HM.scales.at(0)).design.titer, d: 1) g/L of broth) in 102 h, methanol, hemin fed; heme loading not measured]),
                         ("legh_shao2022", [Shao et al. 2022: 3.5 g/L of supernatant (#fx(hcase("legh_shao2022", HM.scales.at(0)).design.titer, d: 1) of broth), methanol, no hemin; 93% heme-loaded]),
                         ("legh", [the base design point (30 g/L, 72 h, glucose)])) {
      ([#label], ..HM.scales.map(t => [#money(hcase(v, t).msp_ccf)]),
       [#usd(hcase(v, HM.scales.at(0)).msp_ccf * use.value, d: 2) (#usd(hcase(v, HM.scales.at(0)).msp_ccf * use.low, d: 2)–#usd(hcase(v, HM.scales.at(0)).msp_ccf * use.high, d: 2))])
    },
  ),
  caption: [Secreted leghemoglobin on the membrane route at LegH Prep's purity (price-anchored capital, US;
  ex-works cost in use at the #thou(HM.scales.at(0)) t/yr cost). An estimate for comparison, not the commercial route (intracellular,
  lysed, sold frozen).],
) <tab-heme>

- *Cost per kg of LegH.* The best published secreted titer (Chen et al. 2025) costs
  #money(hcase("legh_chen2025", HM.scales.at(0)).msp_ccf)/kg on a #thou(HM.scales.at(0)) t/yr plant, about the size of
  the LegH market GFI Europe and Arthur D. Little estimate from trade data, and
  #money(hcase("legh_chen2025", HM.scales.at(1)).msp_ccf) at 1 kt/yr. Their own cost range for heme proteins is \$24–33/kg in
  their text and \$32–122/kg in their chart (the report gives both); the \$275/kg they list as the "conventional"
  price is a customs value, most likely of Impossible's own shipments.
- *Per kg of heme-loaded protein.* Only loaded globin colours and flavours. Shao et al. measured 93% loading, so their
  cost barely changes; Chen et al. did not measure it, and their feed carried hemin, a blood-derived
  heme source not costed here, covering at most about 41% of what full loading would need (our arithmetic).
- *Per kg of burger.* At 0.45% the best secreted process adds
  #usd(hcase("legh_chen2025", HM.scales.at(0)).msp_ccf * use.value, d: 2) per kg of analogue, an ex-works cost equal to
  #pct(hcase("legh_chen2025", HM.scales.at(0)).msp_ccf * use.value / HM.use.beef_usd_kg.value) of US ground beef's
  retail price (\$#fx(HM.use.beef_usd_kg.value, d: 2)/kg, BLS, August 2026). At the design point on a 1 kt/yr plant it
  would add #usd(hcase("legh", HM.scales.at(1)).msp_ccf * use.value, d: 2).

Heme is therefore a small part of a plant-based burger's cost, even made from today's best published secreting
strains. Whether it is worth that cost is a question about taste that we found no consumer study isolating, and
Impossible launched in the UK in September 2026 without it (Green Queen 2026).

// ================================================================ 5
= Discussion

== Answers, in brief

- *Q1.* Today's best public titers give #plist(p => S("academic/" + p).msp_ccf, ps: COMMODITY) per kg:
  not competitive. Only a company's patent example comes close: EVERY's 30 g/L ovomucoid,
  #money(S("academic/ovd_patent").msp_ccf)/kg. The titer
  private cost models assume gives #plist(p => S("industry/" + p).msp_ccf, ps: COMMODITY)
  (#plist(p => S("industry/" + p + "/light").msp_ccf, ps: COMMODITY) with design-report capital):
  #wlist(p => S("industry/" + p).msp_ccf). Lactoferrin at its design titer
  (#money(lfb.msp_ccf)) is #where(lfb.msp_ccf, MKT("lf")) its reported range; at the best public
  methanol-free titer (#money(S("academic/lf").msp_ccf)) #where(S("academic/lf").msp_ccf, MKT("lf")) it.
  Albumin costs #money(alb.msp_ccf) at the base titer and #money(S("academic/alb").msp_ccf) at the record
  titer, #where(alb.msp_ccf, MKT("alb")) the bulk-albumin band and far below catalogue prices. α-Lac costs
  #money(alac.msp_ccf) at the base titer on a 1 kt/yr plant, #where(alac.msp_ccf, MKT("alac")) its reported band, but
  #money(S("academic/alac").msp_ccf) at its best public titer (0.6 g/L).
- *Q2.* Fermenter productivity (protein per hour of vessel time) drives the cost of every protein,
  then the capital basis (vessel prices and fixed-cost rule); sugar and energy prices come second. The
  product yield acts mainly through the feasibility ceiling. The strain parameters are the weakest
  evidence: design values (B) and survey averages (C), and for casein and lactoferrin titers borrowed
  from other proteins or species. For albumin the column (resin price, life and loading, and the
  capture recovery) matters as much as the fermentation.
- *Q3.* With price-anchored capital, \$20/kg BLG needs #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0) g/L
  at 48 h or #fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L at 72 h at the base cell density, and
  OVA, ovomucoid and β-casein about as much (@tab-required-all). What \$10/kg needs above all is secretion: with
  today's biology and capital, process design alone reaches #usd(BD(40).msp_ccf) at 40 mg/g/h and
  #usd(BD(10).msp_ccf) at 10. Albumin at GFI's \$#ALB.cm.gfi_target_usd_kg/kg needs a route without the
  columns' cost, not a better strain.
- *Q4.* The physical-limit best case is #plist(p => PL(p + "/humbird").msp_ccf, ps: COMMODITY) and
  #usd(PL("lf/humbird").msp_ccf) (lactoferrin, at its market's size) and #money(PL("alb/humbird").msp_ccf) (albumin) per kg, bound by
  #PL("blg/humbird").binding.join(", ")\; at a secretion ceiling of 10 mg/g/h the BLG case is #usd(QP(10).msp_ccf).
  α-Lac's, at its food-grade market's size, is #money(PL("alac/humbird").msp_ccf).
- *Q5.* #reach.len() of #R.claims.len() claimed titers are feasible in our fed-batch model, some only with
  long production phases or secretion near the ceiling. No casein or lactoferrin titer has been claimed.
- *Q6.* Scale matters up to about 10 kt/yr for the commodity proteins and is the main lever for
  lactoferrin, whose market caps its plant; albumin's cost flattens past about 1 kt/yr. EU siting adds about #usd(POL.at("EU base") - POL.at("US base"), d: 1)/kg to BLG.
- *Q7.* Replacing the protein of a litre of milk costs #usd(EQ.cases.at("milk/blg").base.all_protein_per_unit, d: 2)
  as BLG and #usd(EQ.cases.at("milk/cas").base.all_protein_per_unit, d: 2) as β-casein, while the litre costs
  #usd(lastv(milkfarm), d: 2) at the farm gate; bought as WPC80/WPI the same whey protein is a fraction of that.
  Albumin at the base cost adds #usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(0) / 1000, d: 2)–#usd(alb.msp_ccf * ALB.cm.g_per_kg_cm.at(2) / 1000, d: 2)
  per kg of cultivated meat.
- *Q8.* The route sets the product: precipitated β-casein is #pct(cas.design.purity_dry) of its
  powder, membrane-only β-casein (Eden Brew) about 6%, in a powder that is mostly yeast carbohydrate. Intelligen's lactoferrin model costs
  #fx(IB.value_money_year / REC("lf").cop, d: 1)× ours to produce. Albumin by UF/DF alone would cost
  #money(ALB.cases.at("alb_ufdf_only/humbird").msp_ccf) against #money(alb.msp_ccf) with its columns, but membranes alone reach only 77% albumin.
- *Notes.* Casein for rennet cheese needs κ-casein at about #pct(CH.kappa_share.at(1)) of it; at today's best κ titer
  (0.25 g/L, a patent example) the blend costs #money(CH.blend.kap.at(str(CH.kappa_share.at(1))).at(0))–#money(CH.blend.kap_cex.at(str(CH.kappa_share.at(1))).at(0))/kg,
  and κ must reach roughly α#sub[s1]'s own design titer for the blend to cost within 10% of α#sub[s1]-casein alone (@sec-cheese). Secreted leghemoglobin at the best published titer costs #money(HM.cases.at("legh_chen2025/150/humbird").msp_ccf)/kg on a
  150 t/yr plant, #usd(HM.cases.at("legh_chen2025/150/humbird").msp_ccf * HM.use.beef_analogue_frac.value, d: 2) per kg of beef analogue (@sec-heme).

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
2. *Public fed-batch data.* Titer, productivity and yield measured *together* for any of these
   proteins; no public dataset reports all three, and the product yield is currently derived, not
   measured. For casein even the titer is missing: no secreted casein titer above 1 g/L is public in
   any yeast or fungus, and every company keeps its titer confidential.
3. *The design ceiling.* The workable starting volume, the most concentrated feed and O#sub[2] transfer
   at production scale and cell density move the titer ceiling itself.
4. *Real capital and fixed costs.* Published capital, staffing and running costs of recent PF plants
   (for example Liberation Labs' 600 m³ Richmond plant) would settle the fermenter price basis and the
   fixed-cost rule.
5. *Downstream data.* Diafiltration flux at scale (one patent value, 5 L/m²/h, sizes most of the
   membrane area), dryer-feed solids for PF proteins, and for casein the solubility of the
   unphosphorylated protein against pH and calcium, which sets the precipitation route.
6. *Function.* Whether unphosphorylated PF casein forms curd and melts like dairy casein in cheese.
   The evidence is mixed (New Culture's patent reports near-normal cheese yields; dephosphorylated
   casein forms micelles poorly), and the cost model cannot answer it.
7. *Albumin's purification and its demand.* What purity cultivated-meat cells actually need from
   albumin, whether a cheaper route than chromatography (membranes, precipitation, a high-capacity
   polymeric resin) reaches it, and the capture recovery at scale; and whether media will keep
   albumin at all, which the leading firms' choices currently argue against.
8. *α-Lactalbumin and κ-casein strains.* Both are three orders of magnitude short of a commodity
   design point in public data (bovine α-lac 2 mg/L in yeast; κ-casein 4 mg/L peer-reviewed). For α-lac the
   culture pH is the known conflict: the protein needs neutral pH to stay soluble, proteases need low pH
   to be suppressed. For κ, whether a recombinant κ co-precipitates with α#sub[s1] decides whether rennet
   casein can use the cheap route at all.

#let beats = wheyobs.filter(x => x >= S("industry/blg/light").msp_ccf).len()
On the evidence here, PF BLG at the titer private cost models assume
#if S("industry/blg").msp_ccf < inc.whey.spot.at(0).usd_kg_protein [would undercut whey in a spike year such as 2026.] else [would not undercut even the 2026 whey peak.]
With design-report capital (#usd(S("industry/blg/light").msp_ccf)) it would have undercut whey in
#beats of the #wheyobs.len() annual export prices of 2015–2025; with price-anchored capital
(#usd(S("industry/blg").msp_ccf)) in #wheyobs.filter(x => x >= S("industry/blg").msp_ccf).len(). High-value
proteins such as lactoferrin cost less than most reported incumbent prices at a design titer. OVA's
position against egg white depends on the year, because egg-white prices swing more than whey's.
β-casein sits close to BLG in cost but faces a cheaper incumbent than egg white; it is the protein
whose displacement would most directly reduce milk demand (@sec-equiv), and the one with the least
public strain data.

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

- A strain that secretes ≥10 mg/g/h of any of these proteins over days at near-zero growth, or
  evidence that it cannot, would move both today's cost and the best case more than any other single
  result.
- A peer-reviewed fed-batch at ≥40 g/L in ≤48 h with a measured yield would test the derived product
  yield and the ceiling; for casein, any secreted titer above a few g/L.
- The ceiling rests on design choices: a 30% minimum starting volume, a 500 g/L glucose feed and
  107 g/L of cells. Industrial practice with lower starts, denser feeds or fewer cells lifts it; then
  secretion and O#sub[2] transfer set it.
- Published capital and running costs of recent PF plants would settle the fermenter price basis and
  the fixed-cost rule.
- Measured OVA solubility at pH 5, and protease control for OVA in *T. reesei*.
- For albumin: a published purification for cell-culture-grade albumin without affinity or a
  \$1,250/L resin, or a capture recovery near 80%; and a methanol-free titer above a few g/L.
- For α-lac: a secreted bovine titer above 1 g/L, and whether membranes alone reach the 90% isolate.
- For rennet casein: a secreted κ-casein titer above a few g/L, or one strain secreting α#sub[s1] and κ together.

// ================================================================ 6
= Limitations <sec-limits>

- *Strain parameters.* Few are grade A. The product yield is derived from a design's lumped
  stoichiometry, not measured; specific productivities are design values or survey averages, and
  the base production phase assumes secretion without growth (@sec-ferm).
  #n_unverified titer rows in `data/titers.csv` are not yet verified in full text.
- *Carbon sources.* Methanol-induced production phases are modelled (version 4), with a measured
  maintenance scaled to near-zero growth (D) and a product yield set at the glucose yield's share of its
  energetic ceiling (D); no product yield on methanol is measured. The ethanol-fed BLG case is still
  priced as glucose, which understates its O#sub[2] and heat. Methanol's safety equipment is inside the
  missing-equipment allowance.
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
- *β-casein* (added in version 3; AI-audited only): its titers are borrowed (the base design point, an
  *E. coli* patent example for the academic case); the acid dose is milk's buffer capacity applied
  per m³ of broth (grade D), the precipitation recovery an analogy with dairy (D) and the heater's
  heat recovery a guess (E); decanters are priced on the disk-stack centrifuge curve; phosphorylation,
  micelle formation and the casein's function in cheese are outside the model; and at the
  physical-limit titer the broth's viscosity would lower O#sub[2] transfer, which the model ignores.
  Whether secreted casein stays dissolved at fermentation pH is contested (Perfect Day's patent says
  caseins precipitate in the fermenter; Eden Brew's dossier says its β-casein stays soluble), and so
  is whether *K. phaffii* secretes β-casein at all without a co-expressed milk kinase (NewMilkBuzz).
  The base case assumes a secreting strain at the titer of the other proteins; no public one exists.
- *Continuous processes* and cell recycle are not modelled.
- *Chromatography* is one capture column for lactoferrin, and a capture plus an anion-exchange polish for
  albumin, with guessed column hardware
  (the flow rate is Intelligen's design value) and no itemised buffer tanks (inside the
  missing-equipment allowance). Lactoferrin's academic titer is porcine lactoferrin, and its market
  size and prices are grade C and disagree by about five times between sources.
- *Albumin* (added in version 4; AI-audited only, audit R12): no food- or media-grade specification
  exists, and whether two columns reach a cell-culture grade is a judgment; its column data are from a
  1990s pharmaceutical patent (maximum step volumes, and recovery and step tables from different
  examples); resin life is borrowed from whey lactoferrin, the favourable end for a yeast-broth feed;
  protease losses at pH 4.5 and the acid, acetate and octanoate are not costed; its methanol use is well
  below what the record run fed (@sec-q1); the methanol yield leaves out the ATP of assimilating methanol's
  carbon (about +\$1/kg); its 2018 titer is scaled to whole broth by analogy; the bulk-albumin price is a
  technical grade, not a cell-culture one; the plant size is a design choice; and its demand depends on
  media that the leading firms are moving away from (Wildtype's FDA file; GFI 2026). No priors were
  registered for albumin before its first model outputs.
- *α-Lactalbumin* (added in version 4; AI-audited only): its best titer is human α-lac, measured in the
  supernatant after a His-tag purification, on ethanol priced as glucose; its market prices are online listings
  and market-research pages (C), and its low end is close to whey protein's own price; its dryer feed is
  borrowed from BLG (D), and the tighter ultrafiltration membrane its 14 kDa size needs is not costed; the
  plant size is a design choice. No priors were registered for it.
- *The rennet-cheese and heme notes* use products outside the main list, each run on an existing route
  by analogy: κ-casein on two routes that bracket its unknown recovery (co-precipitation at an assumed 78%, E;
  its own column on lactoferrin's data, D), and leghemoglobin on the membrane route although the commercial
  product is an intracellular lysate (no lysis or bead mill is modelled, and the drying is extra). The κ share
  for unphosphorylated recombinant caseins rests on one patent example. The supernatant titers of α-lac and LegH
  are converted to whole broth with the model's cell volume (D). Hemin fed to the best LegH strain is not costed.
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
- 21st.BIO. 21st.BIO launches precision fermentation program for bovine alpha-lactalbumin, press release (10 July 2025).
- Almeida Benalcázar E, et al. Single cell protein production from ethanol: model-based bioreactor operation at industrial scale. Biotechnol Bioeng 122:1441 (2025). doi:10.1002/bit.28969 (reports Roels 1983: 460 kJ per mol O#sub[2]).
- Antuma LJ, Boom RM, Keppler JK. Tuning the structure and coagulation behaviour of artificial casein micelles by varying the casein composition. Food Hydrocoll 163:111136 (2025). doi:10.1016/j.foodhyd.2025.111136
- Antuma LJ, Steiner I, Garamus VM, Boom RM, Keppler JK. Engineering artificial casein micelles for future food: is casein phosphorylation necessary? Food Res Int 173:113315 (2023). doi:10.1016/j.foodres.2023.113315
- Aro N, et al. Production of bovine β-lactoglobulin and hen egg ovalbumin by _Trichoderma reesei_ using precision fermentation technology and testing of their techno-functional properties. Food Res Int 163:112131 (2023). doi:10.1016/j.foodres.2022.112131
- Behm K, et al. Comparison of carbon footprint and water scarcity footprint of milk protein produced by cellular agriculture and the dairy industry. Int J LCA 27:1017 (2022). doi:10.1007/s11367-022-02087-0
- Carnicer M, et al. Macromolecular and elemental composition analysis and extracellular metabolite balances of _Pichia pastoris_ growing at different oxygen levels. Microb Cell Fact 8:65 (2009). doi:10.1186/1475-2859-8-65
- CE Delft (Sinke P, Vergeer R, Odegard I). TEA of cultivated meat: future projections of different scenarios, corrigendum (2021).
- Chen H, Niu Y, Wang Y, Zhang L, Dai Z, Luo A, Du G, Zhao X. The optimized signal peptide and feeding strategy to enhance secretory expression of LegH in _Komagataella phaffii_. Process Biochem 156:255 (2025). doi:10.1016/j.procbio.2025.06.005
- Chezan D, Fuhrmann PL, Bender D, et al. Physicochemical properties of native and precision fermentation-derived bovine β-casein: structural and functional insights. Food Hydrocolloids 171:111797 (2026). doi:10.1016/j.foodhyd.2025.111797
- Choi BK, Jiménez-Flores R. Expression and purification of glycosylated bovine β-casein (L70S/P71S) in _Pichia pastoris_. J Agric Food Chem 49:1761 (2001). doi:10.1021/jf001298f
- Choi BK, Jiménez-Flores R. Study of putative glycosylation sites in bovine β-casein introduced by PCR-based site-directed mutagenesis. J Agric Food Chem 44:358 (1996). doi:10.1021/jf950339i
- Chung BKS, et al. Genome-scale metabolic reconstruction and in silico analysis of methylotrophic yeast _Pichia pastoris_ for strain improvement. Microb Cell Fact 9:50 (2010). doi:10.1186/1475-2859-9-50
- Clara Foods Co. (The EVERY Company). Systems and methods for high yielding recombinant microorganisms, US 2024/0209383 A1 (2024); Protein compositions and consumable products thereof, US 12,096,784 B2 (2024).
- Da Gama Ferreira R, Misailidis N, Parisis V, Petrides D. Egg white protein (ovalbumin) production via precision fermentation: process modeling and cost analysis using SuperPro Designer. Intelligen (2025). doi:10.13140/RG.2.2.29080.87048
- Da Gama Ferreira R, Misailidis N, Petrides D. Lactoferrin production via precision fermentation: process modeling and evaluation using SuperPro Designer. Intelligen, February 2026 version.
- Delta Biotechnology Ltd (Goodey AR, Sleep D, et al.). High purity albumin and method of producing, US 5,728,553 A (1998); Process of high purity albumin production, US 6,638,740 B1 (2003).
- Deng M, Wu Y, Lv X, Liu L, Li J, Du G, Chen J, Liu Y. Heterologous single-strand DNA-annealing and binding protein enhance CRISPR-based genome editing efficiency in _Komagataella phaffii_. ACS Synth Biol 12:3443 (2023). doi:10.1021/acssynbio.3c00494 (abstract read)
- Dietzsch C, Spadiut O, Herwig C. A dynamic method based on the specific substrate uptake rate to set up a feeding strategy for _Pichia pastoris_. Microb Cell Fact 10:14 (2011). doi:10.1186/1475-2859-10-14
- Ellilä S, Fonseca L, Uchima C, et al. Development of a low-cost cellulase production process using _Trichoderma reesei_ for Brazilian biorefineries. Biotechnol Biofuels 10:30 (2017). doi:10.1186/s13068-017-0717-0
- FDA GRAS Notices 737 (soy leghemoglobin, Impossible Foods), 763 (α-lactalbumin, Agropur), 967 (ovomucoid, EVERY), 1056 (β-lactoglobulin, Remilk), 1104 (ovalbumin, EVERY), 1219 (bovine lactoferrin, TurtleTree), 1284 (bovine lactoferrin, All G) and 1312 (α#sub[s1]-casein, Formo and NewMilkBuzz; pending).
- FDA. Scientific memorandum, cultured cell consultation CCC 000005 (Wildtype, coho salmon cells), 28 May 2025.
- Fermify GmbH. Non-micellar casein emulsion gel and production thereof, WO 2024/200234 A1 (2024).
- Formo Foods GmbH, NewMilkBuzz BV. Edible products comprising alpha-S1-casein variants A and B and methods for producing the same, WO 2026/068856 A1 (2026).
- FSANZ. Application A1186: soy leghemoglobin in meat analogue products (Impossible Foods, 2019).
- FSANZ. Application A1342: β-casein protein preparation from GM _Komagataella phaffii_ (Eden Brew), application and supporting documents (2026).
- Future Market Insights. Alpha-lactalbumin market size, trends and forecast 2025 to 2035, summary page (accessed 2026-10-02).
- Garrigós-Martínez J, Nieto-Taype MA, Gasset-Franch A, et al. Specific growth rate governs _AOX1_ gene expression, affecting the production kinetics of _Pichia pastoris_ (_Komagataella phaffii_) P#sub[AOX1]-driven recombinant producer strains with different target gene dosage. Microb Cell Fact 18:187 (2019). doi:10.1186/s12934-019-1240-8
- GFI & Hawkwood Biotech. Driving down costs of fermentation-derived ingredients (2025). doi:10.62468/trxj5734
- GFI (Swartz E, et al.). Anticipated growth factor and recombinant protein costs and volumes for cost-competitive cultivated meat (2023).
- GFI Europe & Arthur D. Little. Pathfinding towards precision fermentation viability (2025).
- GFI. 2025 State of the industry report: cultivated meat, seafood and ingredients (2026).
- Green Queen. At long last, the Impossible Burger lands in the UK (23 September 2026).
- Heijnen JJ, van Dijken JP. In search of a thermodynamic description of biomass yields for the chemotrophic growth of microorganisms. Biotechnol Bioeng 39:833 (1992).
- Heyland J, Fu J, Blank LM, Schmid A. Quantitative physiology of _Pichia pastoris_ during glucose-limited high-cell density fed-batch cultivation for recombinant protein production. Biotechnol Bioeng 107:357 (2010). doi:10.1002/bit.22836
- Humbird D, Davis R, McMillan JD. Aeration costs in stirred-tank and bubble column bioreactors. Biochem Eng J 127:161 (2017). doi:10.1016/j.bej.2017.08.006
- Humbird D, Davis R, Tao L, et al. Process design and economics for biochemical conversion of lignocellulosic biomass to ethanol. NREL/TP-5100-47764 (2011).
- Humbird D. Scale-up economics for cultured meat. Biotechnol Bioeng 118:3239 (2021). doi:10.1002/bit.27848 (and SI workbook)
- Iaria L, Bijl E, Hettinga K, Werten MWT. Animal-free caseins by precision fermentation: technical challenges and perspectives. Trends Food Sci Technol 175:105878 (2026). doi:10.1016/j.tifs.2026.105878
- IEAGHG (Amec Foster Wheeler). Effects of plant location on the costs of CO#sub[2] capture. Technical Report 2018/04 (2018).
- InVitria. Cellastim S recombinant human albumin, product page (accessed 2026-10-02).
- Kim H, Jin KC, Kim SK. Systematic engineering of _Komagataella phaffii_ for the production of hen egg ovomucoid. Int J Biol Macromol 320:145813 (2025). doi:10.1016/j.ijbiomac.2025.145813
- Kleerebezem R, van Loosdrecht MCM. A generalized method for thermodynamic state analysis of environmental systems. Crit Rev Environ Sci Technol 40:1 (2010). doi:10.1080/10643380802000974
- Layman DK, Lönnerdal B, Fernstrom JD. Applications for α-lactalbumin in human nutrition. Nutr Rev 76:444 (2018). doi:10.1093/nutrit/nuy004
- Li Y, et al. Transcriptional reprogramming with endogenous cis- and trans-elements for efficient food protein expression from safe substrates in _Komagataella phaffii_. Metab Eng (2026). doi:10.1016/j.ymben.2026.102555
- Liu WC, et al. Scaling-up fermentation of _Pichia pastoris_ to demonstration-scale using new methanol-feeding strategy and increased air pressure instead of pure oxygen supplement. Sci Rep 6:18439 (2016).
- Looser V, Bruhlmann B, Bumbak F, et al. Cultivation strategies to enhance productivity of _Pichia pastoris_: a review. Biotechnol Adv 33:1177 (2015). doi:10.1016/j.biotechadv.2015.05.008
- Lv X, et al. Cascaded de novo biosynthesis of lacto-proteins from CO#sub[2] by engineered _Pichia pastoris_. Green Chem 25:5460 (2023). doi:10.1039/d3gc00867c
- Martin WF, et al. ATP requirements for growth reveal the bioenergetic impact of mitochondrial symbiosis. Biochim Biophys Acta Bioenerg (2025). doi:10.1016/j.bbabio.2025.149564
- Maskow T, Kemp R, Buchholz F, et al. What heat is telling us about microbial conversions in nature and technology. Microb Biotechnol 3:269 (2010).
- Maurer M, et al. Versatile modeling and optimization of fed batch processes for the production of secreted heterologous proteins with _Pichia pastoris_. Microb Cell Fact 5:37 (2006).
- Mercier-Bouchard D, et al. Process efficiency of casein separation from milk using polymeric spiral-wound microfiltration membranes. J Dairy Sci 100:8838 (2017). doi:10.3168/jds.2017-13015
- Merrow EW, Phillips KE, Myers CW. Understanding cost growth and performance shortfalls in pioneer process plants. RAND R-2569-DOE (1981).
- Nestec SA. Production of casein and caseinates, US 4,075,196 (1978).
- New Culture Inc. Dairy-like compositions and related methods, US 2023/0404098 A1 (2023).
- NewMilkBuzz BV. Improved casein secretion by non-mammalian host cells, EP 4 623 075 A1 (2025); Enrichment of a casein in a composition, EP 4 676 233 A1 (2026); and WO 2023/242273, WO 2024/256611, WO 2025/109136.
- Nieto-Taype MA, Garcia-Ortega X, Garrigós-Martínez J, et al. Rationale-based selection of optimal operating strategies and gene dosage impact on recombinant protein production in _Komagataella phaffii_ (_Pichia pastoris_). Microb Biotechnol 13:315 (2020). doi:10.1111/1751-7915.13498
- Panchanawaporn S, et al. Two-step engineering of food-grade _Aspergillus oryzae_ via endogenous signal peptides and vesicle trafficking proteins to enhance carrier-free protein secretion. J Fungi 12:289 (2026). doi:10.3390/jof12040289
- Perfect Day Inc. Compositions comprising a casein and methods of producing the same, US 11,457,649 B2 (2022).
- Petrides D. Bioprocess design and economics. In Harrison RG, et al., Bioseparations Science and Engineering, 2nd ed. Oxford University Press (2015), ch. 11 (Intelligen web version).
- Pires MC, et al. Column ageing of agarose-based chromatography in industrial lactoferrin purification. J Chromatogr A 1760:466274 (2025).
- Price, wage and trade statistics: US EIA, Eurostat (nrg_pc_203/205, lc_lci_lev, earn_ses22, Comext DS-045409), US BLS (OEWS, PPI, CPI-U, average retail prices), USDA (NASS, ERS, AMS Dairy Market News, FoodData Central), UN Comtrade, ECB, EC agri-food portal, WRAP and EREF. Full locators in `data/evidence/`.
- Prielhofer R, Reichinger M, Wagner N, et al. Superior protein titers in half the fermentation time: promoter and process engineering for the glucose-regulated _GTH1_ promoter of _Pichia pastoris_. Biotechnol Bioeng 115:2479 (2018). doi:10.1002/bit.26800
- Rebnegger C, et al. _Pichia pastoris_ exhibits high viability and a low maintenance energy requirement at near-zero specific growth rates. Appl Environ Microbiol 82:4570 (2016).
- Rebnegger C, et al. Protein production dynamics and physiological adaptation of recombinant _Komagataella phaffii_ at near-zero growth rates. Microb Cell Fact 23:44 (2024).
- Rebnegger C, Graf AB, Valli M, et al. In _Pichia pastoris_, growth rate regulates protein synthesis and secretion, mating and stress response. Biotechnol J 9:511 (2014). doi:10.1002/biot.201300334
- Redbiotec AG. Recombinant host cells and methods for producing casein proteins, WO 2023/002061 A2 (2023).
- Runthala A, Mbye M, Ayyash M, Xu Y, Kamal-Eldin A. Caseins: versatility of their micellar organization in relation to the functional and nutritional properties of milk. Molecules 28:2023 (2023). doi:10.3390/molecules28052023
- Sartorius (Albumedix). Recombumin product datasheet (2021).
- Shao Y, Xue C, Liu W, Zuo S, Wei P, Huang L, et al. High-level secretory production of leghemoglobin in _Pichia pastoris_ through enhanced globin expression and heme biosynthesis. Bioresour Technol 363:127884 (2022). doi:10.1016/j.biortech.2022.127884
- Shemesh P, Fishman A. Optimal fermentation conditions for growth and recombinant protein production in _Pichia pastoris_: strain selection, ploidy level and carbon source. Curr Res Food Sci 9:100840 (2024). doi:10.1016/j.crfs.2024.100840
- Southward CR. Casein products. New Zealand Institute of Chemistry, Chemical Processes in New Zealand, III-Dairy-E.
- Standing Ovation. Method for producing casein and uses thereof, US 2024/0251812 A1 (2024); EP 4 533 954 A1 (priority 2023).
- Tetra Pak. Dairy Processing Handbook (online), chapters 7.6, 18 and 19.
- The EVERY Company (Kale A, Patnaik R). Purified protein compositions and methods of production, US 2024/0083940 A1; Recombinant protein recovery methods, US 2025/0134130 A1; Ovalbumin protein compositions, US 12,096,784 B2.
- Tijhuis L, van Loosdrecht MCM, Heijnen JJ. A thermodynamically based correlation for maintenance Gibbs energy requirements in aerobic and anaerobic chemotrophic growth. Biotechnol Bioeng 42:509 (1993).
- Tomàs-Gamisans M, Ferrer P, Albiol J. Fine-tuning the _P. pastoris_ iMT1026 genome-scale metabolic model for improved prediction of growth on methanol or glycerol as sole carbon sources. Microb Biotechnol 11:224 (2018). doi:10.1111/1751-7915.12871
- Tsai LS, Ijichi K, Harris MW. Concentration of egg white by ultrafiltration. J Food Prot 40:449 (1977).
- US Code of Federal Regulations. 21 CFR 73.520, Soy leghemoglobin (84 FR 37576, 2019).
- van 't Riet K. Review of measuring methods and results in nonviscous gas-liquid mass transfer in stirred vessels. Ind Eng Chem Process Des Dev 18:357 (1979).
- Viaene A, Volckaert G, Joniau M, De Baetselier A, Van Cauwelaert F. Efficient expression of bovine α-lactalbumin in _Saccharomyces cerevisiae_. Eur J Biochem 202:471 (1991). doi:10.1111/j.1432-1033.1991.tb16396.x
- Voutilainen E, Pihlajaniemi V, Parviainen T. Economic comparison of food protein production with single-cell organisms from lignocellulose side-streams. Bioresour Technol Rep 14:100683 (2021).
- Wang B, Wu Y, Lv X, Liu L, Li J, Du G, Chen J, Liu Y. Synergistic regulation of chassis cell growth and screening of promoters, signal peptides and fusion protein linkers for enhanced recombinant protein expression in _Bacillus subtilis_. Int J Biol Macromol 280:136037 (2024). doi:10.1016/j.ijbiomac.2024.136037 (abstract read)
- Wang L, et al. The thermodynamic and gelation properties of ovalbumin and lysozyme. Gels 11:470 (2025).
- Wang X, Zhang X, Mao Y, Wu Y, Lv X, Liu L, Han W, Yin S, Wu R, Chen J, Liu Y. Ethanol-inducible bioproduction of human α-lactalbumin in _Komagataella phaffii_. J Agric Food Chem 73:9246 (2025). doi:10.1021/acs.jafc.5c01338
- Wang Y, et al. GCB Bioenergy 13:640 (2021) (recombinant α#sub[s1]-casein in _E. coli_).
- Yao C, Zhu H, An Q, Zhang M, Zheng Y, Cai M. Omics-guided global rewiring of yeast metabolism enables high-level production of β-lactoglobulin. Food Biosci 82:109383 (2026).
- Yen CC, Wu PY, Ou-Yang H, et al. Production of bioactive porcine lactoferrin through a novel glucose-inducible expression system in _Pichia pastoris_. Int J Mol Sci 25:1818 (2024).
- Yver AL, et al. Fractionation of whey protein isolate with supercritical carbon dioxide: process modeling and cost estimation. Int J Mol Sci 13:240 (2012).
- Zhu W, Gong G, Pan J, et al. High level expression and purification of recombinant human serum albumin in _Pichia pastoris_. Protein Expr Purif 147:61 (2018). doi:10.1016/j.pep.2018.02.003 (abstract read)
- Zhu W, Xu R, Gong G, Xu L, Hu Y, Xie L. Medium optimization for high yield production of human serum albumin in _Pichia pastoris_ and its efficient purification. Protein Expr Purif 181:105831 (2021). doi:10.1016/j.pep.2021.105831
- Zhu Y, Sun P, Li C, Zhang Y, Wang Y, Li J, Liu Y, Chen J, Deng Y. Enhanced extracellular production of α-lactalbumin from _Bacillus subtilis_ through signal peptide and promoter screening. Food Sci Hum Wellness 13:2310 (2024). doi:10.26599/FSHW.2022.9250192
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
    ..for f in ("hosts", "dsp", "engineering", "prices", "placeholders", "milk_egg", "lactoferrin", "casein", "ovomucoid", "albumin", "alac", "heme") {
      let c = gcount("../data/evidence/" + f + ".yaml")
      ([`data/evidence/`#f`.yaml`], ..("A", "B", "C", "D", "E").map(g => str(c.at(g))),
       str(c.values().sum()))
    },
  ),
  caption: [Evidence entries by grade. Each entry carries a source, a locator and, where a document
  was read, a verbatim quote.],
)
