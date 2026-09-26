// The cost of precision-fermented whey and egg proteins: techno-economic analysis, v1 draft.
// Compile from the repo root:  typst compile --root . report/pf_tea_report.typ
// Every number is read at compile time from results/analyses.json (scripts/run_analyses.py)
// or from the data files. Nothing numeric is typed into this document except fixed definitions.

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

// ---------------------------------------------------------------- document style
#set document(title: "The cost of precision-fermented whey and egg proteins", author: "Pablo Antonio Moreno Casares")
#set page(paper: "a4", margin: (x: 2.3cm, y: 2.4cm), numbering: "1",
  header: context { if counter(page).get().first() > 1 [
    #set text(size: 8pt, fill: rgb("#898781"))
    Precision-fermented BLG and OVA: techno-economic analysis #h(1fr) Draft v1 for review, #R.generated
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
  text(size: 9pt)[*Check (Pablo):* #body])

// ---------------------------------------------------------------- title
#align(center)[
  #text(size: 17pt, weight: "bold")[The cost of precision-fermented whey and egg proteins]
  #v(0.2em)
  #text(size: 12pt)[A Humbird-style techno-economic analysis of β-lactoglobulin and ovalbumin, \
  from stoichiometry to the physical limit]
  #v(0.6em)
  Pablo Antonio Moreno Casares
  #v(0.1em)
  #text(size: 9pt, fill: rgb("#52514e"))[Draft v1 for review · numbers generated #R.generated · repository `pf-tea`]
]

#v(0.6em)
#note[
  *Status.* Draft for the author's review; not yet peer-reviewed. The model code, the evidence
  extraction and this draft were produced with an AI assistant (Claude, Anthropic) under the author's
  direction. Every number in this document is computed by the model and read from
  `results/analyses.json` when the document is compiled. Every input traces to a source and an
  evidence grade in `data/` (Appendix A). Inputs graded E are placeholders; they are listed in @sec-limits.
]

// ---------------------------------------------------------------- abstract
#heading(level: 1, numbering: none)[Summary]

Precision fermentation (PF) uses an engineered microbe to secrete a single animal protein. It is the
main route to animal-free dairy and egg proteins. We estimate what food-grade β-lactoglobulin (BLG,
the main whey protein) and ovalbumin (OVA, the main egg-white protein) cost to make, and what
performance would bring them to price parity. The method is Humbird's (2021): element- and
electron-balanced black-box stoichiometry, an oxygen-transfer-limited fed-batch fermenter, and a
capital estimate anchored to the market price of baker's yeast. We extend it with a secreted
product and a downstream train, and calibrate it against three published designs.

The base case is a secreting *Komagataella phaffii* strain at 30 g/L in a 72 h production phase,
in 200 m³ fermenters, making 10 kt/yr of protein in the US Midwest (2025 dollars). Its minimum
selling price, with a capital charge of 14.6% of investment per year, is
*#usd(blg.msp_ccf)/kg BLG* and *#usd(ova.msp_ccf)/kg OVA*. With the lighter capital convention used by
the published PF studies it is #usd(R.base_light.blg.msp_ccf) and #usd(R.base_light.ova.msp_ccf).
At the best public academic titers (#fx(S("academic/blg").design.titer, d: 1) g/L BLG,
#fx(S("academic/ova").design.titer, d: 0) g/L OVA) the price is #usd0(S("academic/blg").msp_ccf) and
#usd0(S("academic/ova").msp_ccf)/kg. At the private-sector average titer reported to GFI (42 g/L)
it is #usd(S("industry/blg").msp_ccf)–#usd(S("industry/ova").msp_ccf)/kg. For comparison, whey
protein traded at #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0) per kg protein in
2015–2025 (export unit values), and near #usd(inc.whey.spot.at(0).usd_kg_protein, d: 0) at the 2026 spot
peak. Dried egg white traded at #usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0).

Three results stand out:
1. *Oxygen transfer and heat removal set a titer ceiling.* A 200 m³ fermenter at 80 g/L cells
   reaches at most ~#fx(R.titer_ceiling.blg.at(tpi(72)), d: 0) g/L of BLG in a 72 h production phase.
   Within that wall, \$20/kg needs about #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0)–#fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L
   in 48–72 h. \$10/kg is out of reach with the base capital convention.
2. *The physical-limit floor* (yield near the energetic ceiling, lowest maintenance, O₂-limited rate, 100 kt/yr)
   is #usd(PL("blg/humbird").msp_ccf) per kg BLG and #usd(PL("ova/humbird").msp_ccf) per kg OVA,
   or #usd(PL("blg/light").msp_ccf) and #usd(PL("ova/light").msp_ccf) with light capital.
3. *Capital conventions are the largest structural uncertainty.* Our mass and energy balances match
   the published designs within a few percent. Their costs are 2.7–2.8× lower than ours, because
   of lighter capital and fixed-cost conventions, not better biology.

EU sugar and energy prices add #usd(R.base_eu.blg.msp_ccf - blg.msp_ccf)/kg to the base case.

// ---------------------------------------------------------------- key numbers table
#figure(
  table(
    columns: (2.2fr, 0.9fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, center, right, right, right, right),
    table.header([*Scenario*], [*Titer (g/L)*], [*BLG, Humbird*], [*BLG, light*], [*OVA, Humbird*], [*OVA, light*]),
    hline,
    [Best public academic strain], [#fx(S("academic/blg").design.titer, d: 1) / #fx(S("academic/ova").design.titer, d: 0)],
      [#usd0(S("academic/blg").msp_ccf)], [#usd0(S("academic/blg/light").msp_ccf)],
      [#usd0(S("academic/ova").msp_ccf)], [#usd0(S("academic/ova/light").msp_ccf)],
    [Base case (72 h production)], [30], [#usd(blg.msp_ccf)], [#usd(R.base_light.blg.msp_ccf)],
      [#usd(ova.msp_ccf)], [#usd(R.base_light.ova.msp_ccf)],
    [Industry benchmark (GFI private average)], [42], [#usd(S("industry/blg").msp_ccf)], [#usd(S("industry/blg/light").msp_ccf)],
      [#usd(S("industry/ova").msp_ccf)], [#usd(S("industry/ova/light").msp_ccf)],
    [Physical limit (100 kt/yr)], [#fx(PL("blg/humbird").titer, d: 0) / #fx(PL("ova/humbird").titer, d: 0)],
      [#usd(PL("blg/humbird").msp_ccf)], [#usd(PL("blg/light").msp_ccf)],
      [#usd(PL("ova/humbird").msp_ccf)], [#usd(PL("ova/light").msp_ccf)],
    hline,
    [Incumbent, per kg protein (2015–2025)], [], table.cell(colspan: 2)[whey #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0)],
      table.cell(colspan: 2)[egg white #usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0)],
  ),
  caption: [Minimum selling price (\$/kg target protein, 2025) with a capital charge of 14.6% of total
  capital investment per year. "Humbird" and "light" are the two capital conventions of @sec-capital.
  10 kt/yr and US Midwest unless noted. Incumbent prices: export unit values per kg protein (@sec-q1).],
) <tab-key>

#outline(depth: 2, indent: 1.2em)
#pagebreak()

// ================================================================ 1
= Question and approach

PF companies now sell BLG (Perfect Day, Remilk) and OVA (EVERY), and others are entering the market (Vivici, Onego Bio). Whether these proteins
can displace animal proteins at scale, or stay a premium niche, depends on what they cost to make.
Published estimates disagree by a factor of several. Company claims are rarely checked against the
physics of aerobic fermentation. This study asks:

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
    [Q5], [Are published company claims consistent with O₂-transfer and cooling limits?], [@sec-q5, @tab-claims],
    [Q6], [How much do siting (US vs EU) and scale (1–100 kt/yr) matter?], [@sec-q6, @fig-scale],
  ),
  caption: [The six sub-questions fixed before any model output existed (`docs/SCOPE.md`).],
)

*Why Humbird's method.* Humbird's (2021) cultured-meat analysis builds costs from conservation
laws: element and electron balances, oxygen transfer, heat removal. Its capital estimate is tied to a
real product price, baker's yeast at about \$1.90/kg. We port his baker's-yeast workbook exactly
(@sec-cal) and extend it with three additions: a secreted protein, a downstream train, and the
specifics of *K. phaffii* and *Trichoderma reesei*.

*Rules we followed.* The analysis was run under a written honesty protocol (`PLAN.md`):
- Four scenarios are never merged: academic, industry, required and physical limit.
- Every input carries an evidence grade, A to E.
- The model structure was frozen before the calibration anchors were run. Calibration misses are
  recorded, not tuned away.
- Priors about the results were written down before the model existed; they are scored in @sec-priors.
- Model-to-model agreement is treated as a consistency check, not as validation.

// ================================================================ 2
= Methods

== Plant, products and functional unit

The functional unit is 1 kg of target protein in a spray-dried powder that meets the product
specification. The base specification is a *concentrate*, following Remilk's GRAS notice for BLG
(FDA GRN 1056): at least 70 wt% protein, at least 80% of it BLG, at most 7% moisture. OVA uses the
same specification by analogy. The *isolate* variant (97–99% target protein, dry basis) adds an
ammonium-sulfate precipitation, following the Intelligen (2025) OVA design.

The plant is greenfield, single-product and nth-of-a-kind. It is built to food, not pharmaceutical,
good manufacturing practice. The base is 10 kt/yr of protein in the US Midwest, swept from 1 to
100 kt/yr, with a north-west Europe variant. Money is 2025 US dollars. Excluded costs: R&D, strain
licences, regulatory approval, sales and distribution, land, first-of-a-kind premiums and carbon
pricing. @fig-flow shows the base-case plant.

#figure(image("../docs/figures/fig0_flowsheet.png", width: 100%),
  caption: [Base-case process: *K. phaffii* secreting BLG at 30 g/L; flows per kg of BLG.]) <fig-flow>

== Stoichiometry and energetics

Each metabolic process is written as one element-balanced "black-box" reaction on C, H, O and N:
glucose + NH#sub[3] + O#sub[2] → biomass (or protein) + CO#sub[2] + H#sub[2]O. Electrons are
tracked through the degree of reduction γ (glucose 4, biomass ~4.2, protein ~4.3 per C-mol). This
closes the O#sub[2] and CO#sub[2] balances once the carbon split is fixed.

*Growth.* Biomass yield comes from the Gibbs-energy dissipation correlation of Heijnen and van Dijken
(1992), as in Humbird's workbook. The energy dissipated per C-mol of biomass formed is

$ D = 200 + 18 (6 - c)^(1.8) + exp{[(3.8 - γ_s)^2]^(0.16) (3.6 + 0.4 c)} quad "kJ/C-mol", $

where $c$ and $γ_s$ are the carbon number and degree of reduction of the substrate. The catabolic
reaction (glucose to CO#sub[2]) is run just enough to supply $D$. For glucose this gives a maximum
biomass yield of about 0.52 g/g. The measured *K. phaffii* yield is 0.50–0.58 g/g
(`data/evidence/hosts.yaml`, grade A).

*Maintenance.* Maintenance uses Tijhuis et al. (1993),
$m_G = 4.5 exp[-69 000 / R (1/T - 1/298)]$ kJ per C-mol biomass per hour. At 30 °C this is about
0.018 g glucose per g cells per hour. The measured *K. phaffii* range is 0.002–0.029 g/g/h (grade A).
The base keeps Humbird's value.

*Product.* The protein's elemental formula comes from its mature UniProt sequence:
- BLG: C#sub[817]H#sub[1312]N#sub[206]O#sub[248]S#sub[9], 18.3 kDa;
- OVA: C#sub[1901]H#sub[2997]N#sub[499]O#sub[575]S#sub[22], 42.8 kDa.

The product reaction makes protein from glucose and ammonia. It respires enough extra glucose to pay
for synthesis, so the product yield on glucose, $Y_(p s)$, fixes its O#sub[2] demand. An energetic
ceiling follows from counting ATP: 4 ATP per peptide bond plus amino-acid synthesis, paid by
respiration at up to 28 ATP per glucose. For BLG the ceiling is about 0.6 g/g. The base yield,
#fx(pv("strain.Y_ps_g_g"), d: 2) g/g (Intelligen's assumption, grade B), is
#pct(blg.design.y_ps_over_ceiling) of it. No measured BLG or OVA yield on sugar was found
(@sec-priors, prior 3).

*Heat.* Heat release is computed from formation enthalpies. It is cross-checked against the
empirical 460 kJ per mol O#sub[2] (Roels; grade A in `engineering.yaml`).

#check[The dissipation formula and its units; the conversion of $m_G$ to 0.018 g/g/h; the ATP
ceiling (`src/pftea/product.py`, `energetic_ceiling`). These are the derivations the whole cost
structure rests on, and none has been checked by a second person.]

== The fed-batch fermenter and the oxygen wall

Each production batch has two phases:
1. *Growth* at the maximum specific rate, slowed so that the oxygen uptake rate (OUR) never exceeds
   what the vessel can transfer and the heat never exceeds what it can remove, up to the production
   cell density $X_"prod"$
   (base 80 g/L; Intelligen 83 g/L).
2. *Production* for $t_"prod"$ hours, with a small residual growth and a constant specific
   productivity $q_p$.

The initial liquid volume is solved so that the broth ends at 80% of the vessel. $q_p$ is solved so
that the harvest titer equals the target. A liquid mass balance tracks feed, O#sub[2] uptake, CO#sub[2]
release and evaporation.

*Oxygen transfer.* The volumetric transfer coefficient follows van 't Riet's correlation for
non-coalescing broths, $k_L a = 0.002 (P\/V)^(0.7) U_s^(0.2) 1.025^(T - 20)$ (s#super[−1], SI units),
as in Humbird's microbial fermenters. The driving force is a log-mean between the bottom
(hydrostatic pressure, fresh air) and the top (back-pressure, depleted gas). For each demanded OUR,
the model picks the air rate and agitation power that minimise
$"compressor" + (1 + "refrigeration factor") times "agitator"$ power. Agitator power ends up as heat
that the chillers must remove. The transferable maximum is then capped at the design value
Humbird uses, #fx(pv("fermenter.otr_cap_mol_m3_h"), d: 0) mol O#sub[2]/m³/h. Humbird notes that
200 mol/m³/h "is about as high as it gets" in fermentation. The heat load is capped at
#fx(pv("fermenter.heat_removal_max_kW_m3"), d: 0) kW/m³ (grade D; @sec-limits).

*The oxygen wall.* The production phase's O#sub[2] demand is set by the titer and the time. If the
peak demand exceeds the cap, the design is flagged *infeasible*. We never cost it as if it worked. A
rough scale shows why this binds. Each kg of BLG costs about
#fx(blg.physical.o2_kg * 1000 / 32, d: 0) mol O#sub[2] across the whole batch, including cell growth
and maintenance. So 30 kg/m³ of product needs about
#fx(30 * blg.physical.o2_kg * 1000 / 32 / 1000, d: 1) kmol O#sub[2] per m³. Spread over the
#fx(blg.design.t_total_h, d: 0) h batch, that is a mean of
#fx(30 * blg.physical.o2_kg * 1000 / 32 / blg.design.t_total_h, d: 0) mol/m³/h, against a cap of
#fx(pv("fermenter.otr_cap_mol_m3_h"), d: 0). The peak comes at the end of growth and is higher.
Doubling the titer in the same time pushes it past the cap: at 72 h the ceiling is
#fx(R.titer_ceiling.blg.at(tpi(72)), d: 0) g/L. Halving the time brings it close: at 36 h the ceiling
is #fx(R.titer_ceiling.blg.at(tpi(36)), d: 0) g/L.

== Downstream processing

The downstream train (@fig-flow) follows Intelligen's OVA design, with evidence-graded
performance (`data/evidence/dsp.yaml`):
- *Cell removal.* Dilute to 45 g/L cells, then two-stage disk-stack centrifuges (97% recovery).
- *Microfiltration polish* at #fx(pv("dsp.mf_flux_LMH"), d: 0) L/m²/h (EVERY patent example, grade B).
- *Ultrafiltration and diafiltration* at #fx(pv("dsp.uf_flux_LMH"), d: 0) L/m²/h. Rejection is 0.995.
  BLG is concentrated to 150 g/L, OVA to its practical solubility of 50 g/L. Three diafiltration
  volumes are used.
- *Spray dryer* at 4.87 MJ per kg of water evaporated (industry survey, grade A).
- *Isolate only:* ammonium-sulfate precipitation (350 g/L; 89% recovery), then washed basket centrifuges.

The target protein share of the concentrate powder is 85% on a dry basis (grade D; the GRN 1056
minimum is 56%). The base overall recovery is #pct(blg.design.recovery).

== Capital: two conventions <sec-capital>

*Humbird convention (base).*
- Purchased equipment costs come from Humbird's cost curves (Aspen quotes, 2018 dollars).
- Costs are escalated to 2025 with a factor of #fx(pv("capital.cost_index_2018_to_2025"), d: 2)
  (CEPCI and the BLS machinery price index; grade B, range 1.23–1.52).
- Installation, buildings, engineering, fees and contingency use Humbird's "commodity aerobic"
  facility class: a food-grade plant with the process inside a sanitary building. The effective
  Lang factor (investment over equipment cost) is #fx(blg.design.lang_effective, d: 1).
- Maintenance is 4% and insurance plus local tax 5% of total capital investment (TCI) per year.
- This convention is the one tied to a market price (anchor 1).

*Light convention (sensitivity).* This is the convention of NREL's 2011 design report, which the
published PF studies resemble:
- vendor-quote fermenters, over 3× cheaper than Humbird's curve at 300 m³;
- NREL's installation factors plus indirect costs of 60% of direct cost;
- maintenance of 3% of inside-battery-limits (process-area) direct cost, and insurance of 0.7% of
  fixed capital.

We report both conventions throughout. Their ratio is the largest structural uncertainty in the
study.

== Operating costs, labour and money

*Operating costs.* Raw materials, utilities and consumables come from the mass and energy balance and
the prices in Appendix A. Prices are grade A–B: EIA, Eurostat and BLS statistics, trade unit values
and published designs.

*Labour.* Labour follows Humbird's operator-attention model. Operators are assigned per fermenter by
the fraction of time a batch needs attention. Continuous areas (media, centrifuges, membranes, dryer,
utilities, maintenance, QC) have fixed staffing. There are 4.5 shifts per position, a supervisor for
every ten staff at 1.4× salary, and 100% overhead. The base plant employs #fx(blg.design.fte, d: 0)
people.

*Headline metric.* The minimum selling price is MSP#sub[CCF]: annual operating cost plus a capital
charge, divided by annual output. The charge is the capital recovery factor
$i \/ (1 - (1+i)^(-n)) = 0.146$ per year at $i = 7.5%$ and $n = 10$ years (Humbird). It is a cost with
a return on capital, not a market price. Margins, functionality and cost-in-use are outside the model.

*Other metrics.* We also compute:
- the cost of production (COP): operating cost plus depreciation, no return;
- an NREL-style discounted-cash-flow price, MSP#sub[DCF]: 10% IRR, 30 years, 21% tax, 7-year MACRS.

For the base BLG case these are #usd(blg.cop) (COP) and #usd(blg.msp_dcf) (MSP#sub[DCF]).

== Evidence grades, scenarios and uncertainty

Every parameter and evidence item is graded (@tab-grades). The four scenarios combine grades
differently and are never averaged:
- *academic:* best public strain performance. BLG is 5.14 g/L in *K. phaffii* (Li et al. 2026) and
  OVA is 2 g/L in *T. reesei* (Aro et al. 2023). Both come from abstracts; the full texts are not
  yet read.
- *industry:* the private-sector average titer that companies reported to GFI (2025): 42 g/L
  (grade C), with 100 g/L cells and a yield of 0.30 g/g.
- *required:* the inverse problem. It finds the titer needed for \$10, \$20 and \$50/kg at each
  production time.
- *physical limit:* a product yield of 0.50 g/g (82% of the energetic ceiling), the lowest measured
  maintenance, no growth during production, and 400 m³ vessels. O#sub[2] transfer is capped at
  250 mol/m³/h, which assumes head pressure, and heat removal at 40 kW/m³. Sugar is at contract
  price (\$0.25/kg) and the plant makes 100 kt/yr. Specific productivity is at most 40 mg/g/h. A grid
  search over cell density, production time and titer finds the cheapest feasible design.

#figure(
  table(
    columns: (0.4fr, 3fr),
    table.header([*Grade*], [*Meaning*]),
    hline,
    [A], [Measured, primary source or official statistic (peer-reviewed data, EIA, Eurostat, BLS, USDA)],
    [B], [Design value or patent example from a named source (NREL, Intelligen, Humbird, patents)],
    [C], [Company claim, press release, industry survey, secondary transcription],
    [D], [Derived by analogy or calculation from graded inputs],
    [E], [Placeholder guess; flagged for replacement],
  ),
  caption: [Evidence grades (`data/evidence/README.md`).],
) <tab-grades>

*Uncertainty.* Two tools are used:
- *Tornado.* Each parameter with a graded range is moved to its low and high value, one at a time.
- *Monte Carlo.* Triangular draws are taken over each scenario's uncertain parameters. Draws that
  break a physical limit are kept in the record but excluded from the percentiles, which therefore
  describe feasible plants only. The feasible fraction is reported alongside.

// ================================================================ 3
= Calibration <sec-cal>

The structure was frozen first. Each anchor then changes only its own process inputs, prices, cost
year and financing. Misses are recorded in `docs/VALIDATION.md` before anything changes.
`tests/test_calibration.py` asserts each one inside a documented band, so a change that moves a
result cannot pass silently.

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
    [], [cost, \$/kg protein (2007), Humbird capital],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)").at(0), d: 2)],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)").at(1), d: 2)],
      [#sgn(calrel("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)"))],
    [], [cost, NREL's own capital convention],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]").at(0), d: 2)],
      [#fx(cal("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]").at(1), d: 2)],
      [#sgn(calrel("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]"))],
    hline,
    [3. Intelligen 2025 OVA (consistency)], [cost, \$/kg powder, Humbird convention],
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
    [4. Voutilainen 2021 recombinant case (consistency)], [sugar, kg/kg protein],
      [#fx(cal("voutilainen2021_case", "sugar_kg_per_kg_protein").at(0), d: 2)], [#fx(cal("voutilainen2021_case", "sugar_kg_per_kg_protein").at(1), d: 2)],
      [#sgn(calrel("voutilainen2021_case", "sugar_kg_per_kg_protein"), d: 1)],
    [], [cost, €/t protein, their DCF, Humbird capital], [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF)").at(0))],
      [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF)").at(1))], [#sgn(calrel("voutilainen2021_case", "EUR_per_t_protein (their DCF)"))],
    [], [cost, their fixed costs + light capital], [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]").at(0))],
      [#thou(cal("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]").at(1))],
      [#sgn(calrel("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]"))],
  ),
  caption: [Calibration anchors. Anchor 1 is Humbird's own workbook, ported line by line; anchors 2–4
  are other models run on their own inputs. Details and diagnoses: `docs/VALIDATION.md`.],
) <tab-cal>

*What the anchors say.*
1. *The port is exact.* It reproduces Humbird's baker's-yeast cost to 0.004%. That cost sits on the
   market-implied ~\$1.90/kg, so the method is anchored to a real price (with the caveat that the
   33% margin is Humbird's assumption).
2. *The mass and energy balances agree with all three published PF and enzyme designs.* Sugar agrees
   within 4% and O#sub[2] within about 1% of NREL. Electricity is lower than theirs. Our aeration is
   power-optimised; NREL sizes agitators for peak load, and Intelligen aerates at 1.2–1.6 vvm and
   runs a fertiliser section.
3. *Total costs differ by convention, not by biology.* On the same process, the published costs are
   2.7–2.8× lower than ours (NREL, Voutilainen). The differences are:
   - vendor-quote fermenters instead of Aspen-based curves;
   - Lang factors of 2.7–4 instead of about 5;
   - fixed costs of 1.5–2% of capital per year instead of 9%.

   With their conventions our model still lands above theirs, by
   #sgn(calrel("voutilainen2021_case", "EUR_per_t_protein (their DCF) [light convention]")) (Voutilainen)
   and #sgn(calrel("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing) [light convention]")) (NREL).
   The remainder is mostly labour and buildings.
4. *Intelligen's total agrees* (#sgn(calrel("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)"))).
   Part of the agreement comes from differences that cancel: our capital is higher, and our glucose
   and electricity are lower. It is a weak pass.

Humbird's convention is the only one anchored to a real product price, so it is our base. It is
also the more conservative. The light convention is shown everywhere as a named structural
sensitivity, not as an error band. The NREL report itself notes that enzyme producers quoted costs
about 47% above its estimate.

A port finding: Humbird's compressor formula gives about 1.6× the ideal adiabatic power at 2.1 bar.
We keep it for fidelity to anchor 1. The effect on PF costs is about \$0.1/kg.

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
    [insurance and local tax], [#usd(blg.per_kg.at("insurance & tax"), d: 2)], [#usd(ova.per_kg.at("insurance & tax"), d: 2)], [],
      [electricity], [#fx(blg.physical.electricity_kWh, d: 1) kWh],
    [glucose], [#usd(blg.per_kg.glucose, d: 2)], [#usd(ova.per_kg.glucose, d: 2)], [],
      [natural gas (drying, steam)], [#fx(blg.physical.natural_gas_MJ, d: 0) MJ],
    [labour], [#usd(blg.per_kg.labour, d: 2)], [#usd(ova.per_kg.labour, d: 2)], [],
      [spent cells (dry)], [#fx(blg.physical.cells_kg, d: 1) kg],
    [electricity], [#usd(blg.per_kg.electricity, d: 2)], [#usd(ova.per_kg.electricity, d: 2)], [],
      [overall yield on glucose], [#fx(blg.physical.overall_yield_g_g, d: 3) g/g],
    [media, ammonia, DSP chemicals],
      [#usd(blg.per_kg.at("salts & other media") + blg.per_kg.ammonia + blg.per_kg.at("DSP chemicals"), d: 2)],
      [#usd(ova.per_kg.at("salts & other media") + ova.per_kg.ammonia + ova.per_kg.at("DSP chemicals"), d: 2)], [],
      [fermenter volume], [#fx(blg.physical.fermenter_m3_per_kt, d: 0) m³ per kt/yr],
    [utilities other, membranes],
      [#usd(blg.per_kg.at("natural gas & steam") + blg.per_kg.at("water & wastewater") + blg.per_kg.membranes, d: 2)],
      [#usd(ova.per_kg.at("natural gas & steam") + ova.per_kg.at("water & wastewater") + ova.per_kg.membranes, d: 2)], [],
      [staff], [#fx(blg.physical.fte_per_kt, d: 1) per kt/yr],
    hline,
    [*MSP#sub[CCF]*], [*#usd(blg.msp_ccf, d: 2)*], [*#usd(ova.msp_ccf, d: 2)*], [], [total capital investment], [#musd(blg.tci)],
    [per kg powder], [#usd(blg.per_kg_powder, d: 2)], [#usd(ova.per_kg_powder, d: 2)], [], [production fermenters], [#fx(blg.design.N_prod_int, d: 0) × 200 m³],
  ),
  caption: [Base case: *K. phaffii*, 30 g/L, 72 h production, 10 kt/yr, US Midwest, Humbird capital convention.],
) <tab-base>

Capital dominates the base case. The capital charge, maintenance and insurance together are
#pct((blg.per_kg.at("capital charge") + blg.per_kg.maintenance + blg.per_kg.at("insurance & tax")) / blg.msp_ccf)
of the BLG price. Glucose is #pct(blg.per_kg.glucose / blg.msp_ccf).
- *Why so much capital.* A 10 kt/yr plant at 30 g/L needs #fx(blg.design.N_prod_int, d: 0) production
  fermenters of 200 m³. Every batch occupies a vessel for about #fx(blg.design.cycle_h, d: 0) h, including
  turnaround, and yields #thou(blg.design.target_per_batch_kg) kg of protein.
- *Why glucose is modest.* The overall yield of protein on glucose is only
  #fx(blg.physical.overall_yield_g_g, d: 3) g/g: the cells, their maintenance and the product
  reaction all consume sugar. Even so, at \$#fx(pv("utilities.glucose_usd_kg"), d: 2)/kg glucose costs
  less than a fifth of the price.

This is the first lever the rest of the paper explores: the product made per m³ of fermenter per hour.

== Q1: cost against titer, with every public and claimed data point <sec-q1>

#figure(image("../docs/figures/fig1_cost_vs_titer.png", width: 100%),
  caption: [Minimum selling price against harvest titer, for three production times.
  Vertical lines mark the best public titers, the published-TEA and private-sector averages (GFI 2025),
  and design or claimed titers. Lines end where the O#sub[2] or heat limit of the fermenter is exceeded.]) <fig-titer>

Cost falls roughly as 1/titer until the O#sub[2] wall (@fig-titer):
- *Best public academic strains:* BLG at #fx(S("academic/blg").design.titer, d: 2) g/L costs
  #usd0(S("academic/blg").msp_ccf)/kg; OVA at #fx(S("academic/ova").design.titer, d: 0) g/L in
  *T. reesei* costs #usd0(S("academic/ova").msp_ccf)/kg. That is an order of magnitude above both
  incumbents.
- *Private-sector average (42 g/L):* #usd(S("industry/blg").msp_ccf) (BLG) and
  #usd(S("industry/ova").msp_ccf) (OVA), or #usd(S("industry/blg/light").msp_ccf) and
  #usd(S("industry/ova/light").msp_ccf) with light capital.

*The incumbents.* We use official trade unit values, not quotes, because they form a consistent
2015–2025 series:
- *Whey protein >80%* (WPC80 and WPI mixed; US and EU exports): #usd(inc.whey.band.at(0), d: 0)–#usd(inc.whey.band.at(1), d: 0)
  per kg protein.
- *Dried egg albumin* (EU exports): #usd(inc.egg.band.at(0), d: 0)–#usd(inc.egg.band.at(1), d: 0).
- *2026 whey spike.* WPC80 and WPI prices rose to about #usd(inc.whey.spot.at(0).usd_kg_protein, d: 0)
  per kg protein at the 2026 peak (USDA Dairy Market News), a record year driven by protein demand.
  At that price both the base case (#usd(blg.msp_ccf)) and the industry benchmark
  (#usd(S("industry/blg").msp_ccf)) would undercut whey. At 2015–2025 prices neither would with
  Humbird capital; with light capital the benchmark (#usd(S("industry/blg/light").msp_ccf)) is
  #where(S("industry/blg/light").msp_ccf, inc.whey.band) the band.

Parity at production cost is necessary but not sufficient for commercial parity. PF proteins also
compete on functionality and on price per unit of function.

== Q2: what drives the cost <sec-q2>

#figure(image("../docs/figures/fig2_bridge.png", width: 100%),
  caption: [From NREL's on-site cellulase to our base case, one change at a time. The start is NREL's
  2011 design re-priced to 2025 with an NREL-style capital estimate.]) <fig-bridge>

*Why a food protein costs more than an industrial enzyme.* @fig-bridge walks from an NREL-style
crude enzyme (#usd(R.bridge.at(0).msp)/kg) to our base BLG concentrate (#usd(blg.msp_ccf)/kg). The
largest steps are:
- *The capital convention:* #dusd(R.bridge.at(1).msp - R.bridge.at(0).msp).
- *The titer drop from 50 to 30 g/L:* #dusd(R.bridge.at(7).msp - R.bridge.at(6).msp).
- *Downstream processing and drying:* #dusd(R.bridge.at(9).msp - R.bridge.at(8).msp). NREL's enzyme is
  used as whole broth.
- *Two savings:* moving to a fast yeast process with a 12 h turnaround
  (#dusd(R.bridge.at(6).msp - R.bridge.at(5).msp)), and scale
  (#dusd(R.bridge.at(8).msp - R.bridge.at(7).msp)).
- *The ovalbumin isolate variant* adds precipitation and a second recovery loss:
  #dusd(R.bridge.at(11).msp - blg.msp_ccf) over the BLG concentrate.

The order of the steps changes their sizes but not the total.

#figure(image("../docs/figures/fig5_tornado.png", width: 92%),
  caption: [One-at-a-time sensitivity around the industry benchmark (BLG, 42 g/L), coloured by the
  evidence grade of each parameter's range. Hatched bars break a physical limit.]) <fig-tornado>

*Tornado* (@fig-tornado). Around the industry benchmark, the largest swings come from:
#for (i, t) in R.tornado.slice(0, 6).enumerate() [
  + #lab(t.path): #usd(calc.min(t.msp_low, t.msp_high))–#usd(calc.max(t.msp_low, t.msp_high)) (grade #t.grade)
]

Strain performance leads: titer, production time and cell density. They set how much protein a
fermenter makes per hour, and so how much capital each kg carries. Turnaround time, the sugar price
and the equipment cost index follow.

Two levers matter less than one might expect:
- *Product yield on sugar* (0.20–0.45 g/g) moves the price by only
  #usd(swing("strain.Y_ps_g_g"), d: 1) (rank #torrank("strain.Y_ps_g_g")). Most of the sugar makes
  and maintains the cells, not the product, so cell density drives sugar use more than yield does.
  A low yield matters more for oxygen: at 0.20 g/g the benchmark breaks the O#sub[2] limit.
- *Vessel size* (100–500 m³) moves it by #usd(swing("fermenter.volume_m3"), d: 1)
  (rank #torrank("fermenter.volume_m3")). Humbird's fermenter cost curve and installation factors
  leave little economy of scale per m³ beyond 200 m³.

Few strain-performance ranges are grade A. They rest on company-reported averages and design
assumptions, because no public BLG or OVA fed-batch data report titer, rate and yield together.
The membrane skid cost is still a grade-E placeholder, yet ranks #torrank("dsp.membrane_skid_usd_m2"):
it is the most valuable single number to source next.

#figure(image("../docs/figures/fig7_montecarlo.png", width: 92%),
  caption: [Monte Carlo over each scenario's evidence ranges (triangular), feasible plants only.]) <fig-mc>

*Monte Carlo* (@fig-mc). Over the evidence ranges, the industry benchmark's median is
#usd(MC("industry/blg").p50, d: 0) for BLG (p10–p90 #usd(MC("industry/blg").p10, d: 0)–#usd(MC("industry/blg").p90, d: 0)).
Only #pct(MC("industry/blg").feasible_frac) of the draws are feasible: combinations of high titer and
short production time break the O#sub[2] limit. For the academic strains the whole distribution sits
above #usd0(MC("academic/blg").p10)/kg.

== Q3: what must be true for \$10 and \$20 per kg <sec-q3>

#figure(image("../docs/figures/fig3_required_titer.png", width: 100%),
  caption: [Titer needed for a target price, against production time. Grey: designs the fermenter
  cannot run (O#sub[2] or heat limit, 80 g/L cells).]) <fig-required>

#let reqcell(key, tg, i) = {
  let r = req(key, tg, i)
  if r.titer == none { [—] } else { fx(r.titer, d: 0) }
}
#figure(
  table(
    columns: (1.9fr,) + R.required_t_prods.map(_ => 1fr),
    align: (left,) + R.required_t_prods.map(_ => right),
    table.header([*Production phase (h)*], ..R.required_t_prods.map(t => [*#t*])),
    hline,
    [O₂/heat ceiling, BLG], ..R.titer_ceiling.blg.map(c => if c == none [—] else [#fx(c, d: 0)]),
    hline,
    ..for tg in (10, 20, 50) {
      ([\$#tg/kg, Humbird], ..range(R.required_t_prods.len()).map(i => reqcell("blg/humbird", tg, i)))
    },
    hline,
    ..for tg in (10, 20, 50) {
      ([\$#tg/kg, light], ..range(R.required_t_prods.len()).map(i => reqcell("blg/light", tg, i)))
    },
  ),
  caption: [BLG titer (g/L) needed for each target price, searched only below the O#sub[2]/heat
  ceiling (first row). — means the target is not reachable at that production time in a 200 m³
  vessel at 80 g/L cells and base yield. OVA needs slightly more. With Humbird capital, \$20/kg of
  OVA needs at least
  #fx(calc.min(..R.required.at("ova/humbird").at("20").filter(r => r.titer != none).map(r => r.titer)), d: 0) g/L,
  above OVA's assumed practical solubility of 50 g/L (`results/analyses.json`, key `required`).],
) <tab-required>

@fig-required and @tab-required answer the inverse question:
#let r50 = R.required.at("blg/humbird").at("50").filter(r => r.titer != none).map(r => r.titer)
- *\$50/kg* needs #fx(calc.min(..r50), d: 0)–#fx(calc.max(..r50), d: 0) g/L, depending on production time.
  That is #fx(calc.min(..r50) / S("academic/blg").design.titer, d: 1)–#fx(calc.max(..r50) / S("academic/blg").design.titer, d: 1)×
  the best public academic BLG titer, and well within today's industrial claims.
- *\$20/kg* needs about #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0)–#fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L
  in 48–72 h under the Humbird convention. That is at or above the private-sector average and close
  to the ceiling. The light convention needs only #fx(req("blg/light", 20, tpi(48)).titer, d: 0)–#fx(req("blg/light", 20, tpi(72)).titer, d: 0) g/L.
#let r10l = R.required.at("blg/light").at("10").enumerate().filter(x => x.at(1).titer != none)
- *\$10/kg is not reachable with Humbird capital* at the base yield and cell density: the titer it
  would need lies above the O#sub[2]/heat ceiling at every production time.
  #if r10l.len() > 0 [With light capital it needs
  #fx(r10l.first().at(1).titer, d: 0)–#fx(r10l.last().at(1).titer, d: 0) g/L in
  #R.required_t_prods.at(r10l.first().at(0))–#R.required_t_prods.at(r10l.last().at(0)) h, just under the ceiling.] else [Nor is it reachable with light capital.]

Titer alone is therefore not enough for \$10/kg. The other levers are yield, cell density,
production time, vessel size, the capital convention and scale; the physical-limit scenario pulls
them all at once.

== Q4: the physical-limit floor <sec-q4>

#figure(image("../docs/figures/fig4_breakdown.png", width: 100%),
  caption: [Cost structure from today's benchmarks to the physical limit. The best academic strain
  (#usd0(S("academic/blg").msp_ccf)/kg BLG) is off this scale.]) <fig-breakdown>

The physical-limit search (@fig-breakdown) picks the cheapest feasible design. The best BLG design
has #fx(PL("blg/humbird").X_prod, d: 0) g/L cells, a #fx(PL("blg/humbird").t_prod, d: 0) h
production phase and #fx(PL("blg/humbird").titer, d: 0) g/L. Its specific productivity is
#fx(PL("blg/humbird").design.q_p_mg_g_h, d: 0) mg/g/h against the 40 mg/g/h cap.

The floor is #usd(PL("blg/humbird").msp_ccf)/kg BLG with Humbird capital and
#usd(PL("blg/light").msp_ccf) with light capital. For OVA it is #usd(PL("ova/humbird").msp_ccf) and
#usd(PL("ova/light").msp_ccf).
- *Capital still dominates at the floor.* Capital-related costs are
  #pct((PL("blg/humbird").per_kg.at("capital charge") + PL("blg/humbird").per_kg.maintenance + PL("blg/humbird").per_kg.at("insurance & tax")) / PL("blg/humbird").msp_ccf)
  of the BLG floor. Glucose (#usd(PL("blg/humbird").per_kg.glucose, d: 2)) is the largest
  non-capital item.
- *Why OVA's floor is higher.* OVA is held to its practical solubility of 50 g/L, in both the broth
  and the ultrafiltration retentate. That limit is Intelligen's assumption, not a measurement. If OVA
  could be concentrated like BLG, its floor would be #usd(PL("ova/humbird/solubility_150").msp_ccf)
  (#usd(PL("ova/light/solubility_150").msp_ccf) light). The OVA floor is therefore mostly a statement
  about that one number.

The floor is not a forecast. It is what physics and stoichiometry allow once every biological
parameter is at its best measured or theoretical value, all at the same time. The BLG floor is
#where(PL("blg/humbird").msp_ccf, inc.whey.band) the 2015–2025 whey band
(#usd(inc.whey.band.at(0), d: 1)–#usd(inc.whey.band.at(1), d: 1)). The OVA floor is
#where(PL("ova/humbird").msp_ccf, inc.egg.band) the egg-white band.

== Q5: company claims against the physics <sec-q5>

#figure(
  table(
    columns: (2.5fr, 0.6fr, 0.9fr, 0.9fr, 0.8fr, 0.8fr, 0.8fr),
    align: (left, right, left, right, right, right, right),
    table.header([*Claim or benchmark*], [*Titer*], [*Modelled as*], [*Shortest feasible production phase*],
      [*Implied $q_p$ (mg/g/h)*], [*MSP, Humbird*], [*MSP, light*]),
    hline,
    ..for c in R.claims {
      ([#c.label], [#fx(c.titer, d: 0) g/L],
       [#(if c.host == "treesei" [_T. reesei_] else [_K. phaffii_]), #fx(c.X_prod, d: 0) g/L cells],
       [#(if c.t_prod_min == none [not reachable] else [#fx(c.t_prod_min, d: 0) h])],
       [#(if c.at("q_p_mg_g_h", default: none) == none [—] else [#fx(c.q_p_mg_g_h, d: 0)])],
       [#usd(c.at("msp_humbird", default: none))], [#usd(c.at("msp_light", default: none))])
    },
  ),
  caption: [Claimed titers checked against O#sub[2] transfer and heat removal in a 200 m³ fermenter:
  the shortest production phase in which each titer is reachable, the specific productivity that
  then implies, and the cost there. The check is physical only. Whether a strain can sustain that
  productivity is a separate, biological question; our base case assumes about
  #fx(blg.design.q_p_mg_g_h, d: 0) mg/g/h.],
) <tab-claims>

#let reach = R.claims.filter(c => c.t_prod_min != none)
#let noreach = R.claims.filter(c => c.t_prod_min == none)
#let qps = reach.filter(c => c.at("q_p_mg_g_h", default: none) != none).map(c => c.q_p_mg_g_h)
Of the #R.claims.len() claims and benchmarks, #reach.len() can be reached within the O#sub[2] and
cooling limits if the production phase is long enough (@tab-claims). The price of a high titer is
time, and time is fermenter capacity, so a claimed titer alone does not settle the cost.

Physics does not rule the claims out. Reaching them as fast as physics allows, though, implies
specific productivities of #fx(calc.min(..qps), d: 0)–#fx(calc.max(..qps), d: 0) mg per g of cells
per hour, against #fx(blg.design.q_p_mg_g_h, d: 0) in our base case. The *T. reesei* claims need
the highest. At 35 g/L cells, a fungus must secrete about
#fx(calc.max(..qps), d: 0) mg/g/h for #fx(reach.sorted(key: c => c.titer).last().t_prod_min / 24, d: 0) days to reach
#fx(reach.sorted(key: c => c.titer).last().titer, d: 0) g/L. Whether a strain can sustain that is the open question, and no
public data answer it.
#if noreach.len() > 0 [
  #noreach.map(c => c.label).join("; ") cannot be reached in our model at any production time up to
  20 days. Either the O#sub[2] demand of that much protein exceeds what a viscous fungal broth can
  take up, or the broth outgrows the vessel before the titer is reached. Such claims need either
  much better O#sub[2] transfer than our *T. reesei* assumptions (a k#sub[L]a half that of yeast
  broth, grade D), or a different process: continuous or repeated fed-batch, or cell recycle.
  None of these is modelled here.
]

== Q6: scale and siting <sec-q6>

#figure(image("../docs/figures/fig6_scale.png", width: 82%),
  caption: [Industry-benchmark BLG against plant output, US Midwest and north-west Europe, both capital conventions.]) <fig-scale>

*Scale* (@fig-scale):
- Going from 1 to 10 kt/yr cuts the price by
  #usd(R.scale.curves.at("US, Humbird capital").at(0) - R.scale.curves.at("US, Humbird capital").at(3)).
- Going from 10 to 100 kt/yr saves only a further
  #usd(R.scale.curves.at("US, Humbird capital").at(3) - R.scale.curves.at("US, Humbird capital").at(6)).
- The reason: beyond about 10 kt/yr the plant adds more 200 m³ fermenters rather than bigger ones.
  Only the downstream train and the utilities keep scaling.
- Larger vessels help little: 100 to 500 m³ moves the benchmark by #usd(swing("fermenter.volume_m3"), d: 1)/kg
  (@fig-tornado).

*Siting.* A north-west Europe plant costs #usd(R.base_eu.blg.msp_ccf - blg.msp_ccf)/kg more than
the US Midwest in the base case. The difference comes from:
- glucose: \$#fx(P.utilities.glucose_usd_kg.eu_nw, d: 2) against \$#fx(P.utilities.glucose_usd_kg.us_midwest, d: 2) per kg;
- electricity: \$#fx(P.utilities.electricity_usd_kWh.eu_nw, d: 3) against \$#fx(P.utilities.electricity_usd_kWh.us_midwest, d: 3) per kWh;
- gas: \$#fx(P.utilities.natural_gas_usd_GJ.eu_nw, d: 1) against \$#fx(P.utilities.natural_gas_usd_GJ.us_midwest, d: 1) per GJ.

Labour is slightly cheaper in the Netherlands on our basis. Construction costs are assumed equal
(@sec-limits).

// ================================================================ 5
= Discussion

== Answers, in brief

- *Q1.* Today's public strains make BLG and OVA at #usd0(S("academic/blg").msp_ccf) and
  #usd0(S("academic/ova").msp_ccf) per kg: not competitive. The private-sector average titer gives
  #usd(S("industry/blg").msp_ccf)–#usd(S("industry/ova").msp_ccf), or
  #usd(S("industry/blg/light").msp_ccf)–#usd(S("industry/ova/light").msp_ccf) with light capital.
  Against 2015–2025 prices:
  - with Humbird capital, BLG is #where(S("industry/blg").msp_ccf, inc.whey.band) the whey band and
    OVA #where(S("industry/ova").msp_ccf, inc.egg.band) the egg-white band;
  - with light capital, BLG is #where(S("industry/blg/light").msp_ccf, inc.whey.band) the whey band and
    OVA #where(S("industry/ova/light").msp_ccf, inc.egg.band) the egg-white band.
- *Q2.* Fermenter productivity (titer per hour of vessel time) and the capital convention drive the
  cost. Sugar and energy prices come second. The evidence for the strain parameters is the weakest
  link. It consists of design values (grade B) and survey averages (grade C), because no public
  fed-batch dataset reports titer, rate and yield together.
- *Q3.* Under our base convention, \$20/kg needs #fx(req("blg/humbird", 20, tpi(48)).titer, d: 0) g/L
  at 48 h or #fx(req("blg/humbird", 20, tpi(72)).titer, d: 0) g/L at 72 h, close to the O#sub[2] ceiling.
  \$10/kg needs more than titer.
- *Q4.* The physical floor is #usd(PL("blg/humbird").msp_ccf) (BLG) and #usd(PL("ova/humbird").msp_ccf) (OVA) per kg.
- *Q5.* #reach.len() of #R.claims.len() claimed titers are physically reachable in our fed-batch
  model, some only with long production phases, which cost capital.
  #if noreach.len() > 0 [The highest claims (#noreach.map(c => str(int(c.titer)) + " g/L").join(", ")) are not, under our *T. reesei* assumptions.]
- *Q6.* Scale matters up to about 10 kt/yr. EU siting adds about #usd(R.base_eu.blg.msp_ccf - blg.msp_ccf, d: 0)/kg.

== Why published PF costs are lower

Published PF cost estimates for food proteins span roughly \$12–39/kg:
- GFI Europe and Arthur D. Little (2025): \$24–33/kg for their "P1" molecules today, and \$12/kg for
  α-lactalbumin after improvements;
- Intelligen (2025): \$39/kg for an OVA isolate at 1 kt/yr.

Where we can reproduce the process (NREL, Voutilainen), our calibration shows that the gap to our
base is mostly accounting, not biology. Their fermenters are priced from vendor quotes, their installation
and indirect factors are lighter, and their fixed costs are 1.5–2% of capital instead of Humbird's 9%.

Neither convention is "correct". Humbird's is anchored to the price of a real fermented commodity.
The light one matches how the process industry quotes greenfield enzyme plants. A buyer of capital
equipment in 2026 will probably land between them. We therefore read our base as a conservative
central estimate and the light convention as an optimistic one, not as a confidence interval.

== For funders

In order of expected cost reduction per unit of evidence gained:
1. *Public fed-batch data.* Titer, productivity and yield measured *together* at 1–10 m³ for BLG and
   OVA, in *K. phaffii* and *T. reesei*. No public dataset reports all three.
2. *Productivity, not only titer.* Faster production raises capacity per vessel. Near the O#sub[2]
   wall, extra titer is only useful if it comes without extra time.
3. *Shared scale-up and capital-light plants.* Capital is the largest cost item in every scenario.
   Conversions of existing fermentation capacity (ethanol, enzymes) would move a plant toward the
   light convention.
4. *Downstream data.* Membrane skid costs (a grade-E placeholder, rank
   #torrank("dsp.membrane_skid_usd_m2") in the tornado), ultrafiltration end concentrations and
   fluxes, and microfiltration flux (one patent example). After strain performance, these are the
   largest evidence gaps.

On the evidence here, PF BLG undercuts whey on production cost in spike years like 2026. At
2015–2025 prices it needs both the private-sector average titer and light capital
(#usd(S("industry/blg/light").msp_ccf), #where(S("industry/blg/light").msp_ccf, inc.whey.band) the band).
With Humbird's capital estimate, even the O#sub[2] ceiling at 72 h gives
#usd(R.cost_vs_titer.blg.msp_at_ceiling.at(1)), #where(R.cost_vs_titer.blg.msp_at_ceiling.at(1), inc.whey.band)
the band. PF OVA faces a similar gap.
Egg-white prices spiked in 2022–2023 with avian influenza (EU export unit value up to
#usd(inc.egg.band.at(1), d: 0)/kg protein), which is when OVA's case is strongest.

#check[Author's judgment, not a model output (please revise): the probability that a PF plant built
with 2026 technology makes BLG below \$10/kg protein is about 0.15, with low confidence. The
physical-limit case shows \$10 is physically possible, but only if every lever moves at once.]

== For EU policy

At EU sugar, electricity and gas prices, the same plant costs
#usd(POL.at("EU base") - POL.at("US base"))/kg more than in the US Midwest (base BLG):
- US-level glucose would remove #usd(POL.at("EU base") - POL.at("EU with US glucose price")) of the gap.
- US-level energy prices would remove #usd(POL.at("EU base") - POL.at("EU with US energy prices")).
- Cheaper, longer capital does more than either. A capital charge at 4% over 20 years instead of 7.5% over
  10 cuts #usd(POL.at("EU base") - POL.at("EU, capital at 4%/20 yr")), more than the whole
  transatlantic gap. At 4% over 10 years it cuts #usd(POL.at("EU base") - POL.at("EU, capital at 4%/10 yr")).

The infrastructure that matters most is not fermenters per se, but the combination of:
- cheap fermentable sugar next to the plant;
- chilled water and power for aeration;
- membrane and drying capacity.

The cost and form of capital matter more than siting. Instruments that lower the cost of capital, or
enable conversions of existing plants, move the cost more than energy subsidies would.

== What would change these conclusions

- A peer-reviewed BLG or OVA fed-batch at ≥40 g/L in ≤48 h with a yield of ≥0.3 g/g would put
  \$20/kg inside the Humbird-convention feasible region.
- Evidence that production-scale O#sub[2] transfer routinely exceeds 200 mol/m³/h (pressurised
  vessels) would move the wall up.
- Real capital costs of recent PF plants (for example Liberation Labs, 600 m³) would settle the
  convention question.

// ================================================================ 6
= Limitations <sec-limits>

- *Strain parameters.* Only a few are grade A. Yields and specific productivities are design
  assumptions (Intelligen) or survey averages (GFI). The academic titers come from abstracts;
  #n_unverified titer rows are not yet verified in full text (`data/titers.csv`).
- *OVA solubility* of 50 g/L is Intelligen's practical assumption. If OVA stays soluble higher, the
  OVA ceiling rises.
- *Heat removal* above 114 m³ needs external exchangers; the 25 kW/m³ cap is grade D. No source gives
  a production-scale ceiling.
- *Construction costs* are the same in the EU and the US. No sourced location factor is on disk.
- *Continuous processes* and cell recycle are not modelled. Nor are methanol-induced expression and
  chromatography for high-purity isolates.
- *Spent cells* are costed at zero (no credit, no disposal cost; grade E, range −\$50 to +\$100 per t).
- *Humbird's compressor formula* overstates compressor power by ~1.6×. We keep it for fidelity; the
  effect is about \$0.1/kg.
- *Grade-E inputs* (placeholders) remain for:
  #flat(P, "").filter(x => x.at(1).at("grade", default: "") == "E").map(x => raw(x.at(0))).join(", ").
  See Appendix A.

// ================================================================ 7 (priors)
= Scoring the pre-registered priors <sec-priors>

The priors were written in `docs/SCOPE.md` before any model output existed.

#figure(
  table(
    columns: (2.6fr, 1.2fr, 1.6fr, 0.8fr),
    align: (left, left, left, left),
    table.header([*Prior (2026-09-26)*], [*Stated*], [*Outcome*], [*Score*]),
    hline,
    [1a. Intelligen configuration, \$/kg OVA (80% interval)], [\$38–60],
      [#usd(R.calibration.intelligen2025_ova.msp_ccf_per_kg_target)/kg OVA],
      [#(if R.calibration.intelligen2025_ova.msp_ccf_per_kg_target >= 38 and R.calibration.intelligen2025_ova.msp_ccf_per_kg_target <= 60 [inside] else [outside])],
    [1b. Base case, \$/kg protein (80% interval)], [\$28–50], [#usd(blg.msp_ccf) (BLG), #usd(ova.msp_ccf) (OVA)],
      [#(if blg.msp_ccf >= 28 and ova.msp_ccf <= 50 [inside, near the low end] else [outside])],
    [1 (superseded). Purified BLG/OVA at 30 g/L], [\$20–40], [as above],
      [#(if blg.msp_ccf >= 20 and ova.msp_ccf <= 40 [inside] else [outside])],
    [2. P(physical floor < \$10/kg)], [0.65],
      [BLG #usd(PL("blg/humbird").msp_ccf) (#(if PL("blg/humbird").msp_ccf < 10 [yes] else [no])); OVA #usd(PL("ova/humbird").msp_ccf) (#(if PL("ova/humbird").msp_ccf < 10 [yes] else [no]))],
      [Brier #fx(calc.pow((if PL("blg/humbird").msp_ccf < 10 {1} else {0}) - 0.65, 2), d: 2) / #fx(calc.pow((if PL("ova/humbird").msp_ccf < 10 {1} else {0}) - 0.65, 2), d: 2)],
    [3. P(a public BLG/OVA yield on sugar turns up)], [0.20], [none found (an LCA inventory value only)], [Brier 0.04],
    [4. P(first-try calibration within tolerance): yeast / NREL / Intelligen], [0.6 / 0.6 / 0.5],
      [yes / no (+136%) / yes (−3.6%)], [Brier 0.16 / 0.36 / 0.25],
    [5. P(public v1 by 2027-04-30 / 2027-07-31)], [0.5 / 0.8], [open], [—],
  ),
  caption: [Pre-registered priors and outcomes. Prior 4 is scored on the first run (2026-09-26),
  before the evidence updates recorded in `docs/VALIDATION.md`.],
)

The interval priors were well placed but wide. The base case landed near the low end of both. The
calibration prior was about right on average; the NREL miss came from capital conventions, which the
prior did not anticipate.

// ================================================================ 8
= Reproducibility

```
.venv/bin/python -m pytest                      # 22 tests: Humbird port, calibration bands
.venv/bin/python scripts/run_analyses.py        # all results -> results/analyses.json
.venv/bin/python scripts/make_figures.py        # docs/figures/*.png
typst compile --root . report/pf_tea_report.typ # this document
```

Inputs are in `data/pf/base.yaml` (every value with a range, grade and source), with scenario
overrides in `data/pf/scenarios/`. The evidence files are `data/evidence/*.yaml`, with verbatim
quotes and locators. Calibration cases are in `data/calibration/`.

// ================================================================ references
#heading(level: 1, numbering: none)[References]
#set par(justify: false)
#text(size: 9pt)[
- Aro N, et al. Production of bovine β-lactoglobulin and hen egg ovalbumin by _Trichoderma reesei_ … Food Res Int 163:112131 (2023). doi:10.1016/j.foodres.2022.112131
- Beck F, Noll P, Schweiggert-Weisz U, Henkel M. Scientific and technological challenges of recombinant egg protein production. BMC Biotechnol 25 (2025). doi:10.1186/s12896-025-01002-3
- Behm K, et al. Comparison of carbon footprint and water scarcity footprint of milk protein produced by cellular agriculture and the dairy industry. Int J LCA 27:1017 (2022). doi:10.1007/s11367-022-02087-0
- Da Gama Ferreira R, Misailidis N, Parisis V, Petrides D. Egg white protein (ovalbumin) via precision fermentation: TEA using SuperPro Designer. Intelligen (2025). doi:10.13140/RG.2.2.29080.87048
- FDA. GRAS Notice 1056: non-animal whey protein (β-lactoglobulin) from _Komagataella phaffii_ (Remilk, 2023).
- GFI & Hawkwood Biotech. Driving down costs of fermentation-derived ingredients (2025). doi:10.62468/trxj5734
- GFI Europe & Arthur D. Little. Pathfinding towards precision fermentation viability (2025).
- Heijnen JJ, van Dijken JP. In search of a thermodynamic description of biomass yields for the chemotrophic growth of microorganisms. Biotechnol Bioeng 39:833 (1992).
- Humbird D. Scale-up economics for cultured meat. Biotechnol Bioeng 118:3239 (2021). doi:10.1002/bit.27848 (and SI workbook)
- Humbird D, Davis R, Tao L, et al. Process design and economics for biochemical conversion of lignocellulosic biomass to ethanol. NREL/TP-5100-47764 (2011).
- Li Y, et al. Transcriptional reprogramming with endogenous cis- and trans-elements for efficient food protein expression from safe substrates in _Komagataella phaffii_. Metab Eng (2026). doi:10.1016/j.ymben.2026.102555
- Liu WC, et al. Scaling-up fermentation of _Pichia pastoris_ to demonstration-scale using new methanol-feeding strategy and increased air pressure instead of pure oxygen supplement. Sci Rep 6:18439 (2016).
- Tijhuis L, van Loosdrecht MCM, Heijnen JJ. A thermodynamically based correlation for maintenance Gibbs energy requirements in aerobic and anaerobic chemotrophic growth. Biotechnol Bioeng 42:509 (1993).
- van 't Riet K. Review of measuring methods and results in nonviscous gas-liquid mass transfer in stirred vessels. Ind Eng Chem Process Des Dev 18:357 (1979).
- Voutilainen E, Pihlajaniemi V, Parviainen T. Economic comparison of food protein production with single-cell organisms from lignocellulose side-streams. Bioresour Technol Rep 14:100683 (2021).
- Price and wage statistics: US EIA, Eurostat (nrg_pc_203/205, lc_lci_lev, earn_ses22, Comext DS-045409), US BLS (OEWS May 2025, PPI), UN Comtrade, USDA AMS Dairy Market News, ECB. Full locators in `data/evidence/prices.yaml`.
]

// ================================================================ appendix
#pagebreak()
#set heading(numbering: "A.1")
#counter(heading).update(0)
= Parameters (generated from `data/pf/base.yaml`)

#let showv(x) = {
  if type(x) == int or type(x) == float { str(x) } else if type(x) == str { x } else { [(table in file)] }
}
#let showleaf(x) = {
  if "us_midwest" in x [US #showv(x.us_midwest); EU #showv(x.eu_nw)] else if "value" in x [#showv(x.value)] else []
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
    ..for f in ("hosts", "dsp", "engineering", "prices") {
      let c = gcount("../data/evidence/" + f + ".yaml")
      ([`data/evidence/`#f`.yaml`], ..("A", "B", "C", "D", "E").map(g => str(c.at(g))),
       str(c.values().sum()))
    },
  ),
  caption: [Evidence entries by grade. Each entry carries a source, a locator and, where a document
  was read, a verbatim quote.],
)
