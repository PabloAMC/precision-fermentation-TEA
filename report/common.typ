// Shared data and helpers for the report and the preprint (both import this file).
// Every number is read from results/analyses.json or the data files.

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
// kinds of evidence: the data files store them as letters A-E (data/evidence/README.md)
#let EVW = (A: "measured", B: "published design", C: "company claim or survey", D: "analogy or judgment", E: "guess", structural: "modelling choice")
#let evword(g) = EVW.at(g, default: g)
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
#let PRD = yaml("../data/pf/products.yaml")
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

