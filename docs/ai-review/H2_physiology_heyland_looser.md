> AI reading pass (Claude, an AI model), 2026-09-27, run after the Phase F pre-review to read sources Pablo downloaded. Kept verbatim except local paths. Not a human review. Every finding acted on was re-checked against the source text, table images or workbook cells; decisions are in docs/REVIEW.md (follow-up section).

# Strain-physiology audit: Heyland 2010 and Looser 2015 vs `data/pf/base.yaml`

**Nothing was edited.** Scratch work (per-page text, table crops, `calc.py`) is in
`<scratch>/review/phys/`.

**Citation caveats, before anything else**
1. Heyland page numbers below are the **journal pages 357–368** (PDF page *n* = journal page 356+*n*). Safe to cite.
2. Looser is the **accepted manuscript**, not the typeset article. Its body pages are printed 1–18 (PDF 4–21) and its tables are on separate end pages (PDF 38–44). **These do not correspond to the journal's 1177–1193 pagination.** I cite as "ms. p.*n* (PDF p.*m*)" / "Table *k* (PDF p.*m*)". Anything that goes into `base.yaml` should be re-checked against the published version before a page number is asserted.
3. I have kept literal quotation short (copyright). Every figure below is reported **exactly as printed** at the location given; where I did the arithmetic I say so explicitly.

---

## 1. Heyland 2010 — extraction

| Item | Value as printed | Location |
|---|---|---|
| Host strain | *P. pastoris* SMD1168H (haploid); reference strain = untransformed SMD1168H | p.358 |
| Producing strain | BapABT3 | p.358 |
| Product | β-peptidyl aminopeptidase **BapA** (3-2W4) of *Sphingosinicella xenopeptidilytica*, codon-optimised | p.358 |
| Promoter / vector | **constitutive GAP**, vector pGAPZ A | p.358 |
| Carbon source | glucose, sole C and energy source; fed-batch feed **73% (w/v) glucose** | p.358 |
| Conditions | 30 °C, pH 5, pO₂ 30%, air + O₂ | p.358 |
| µ, batch (shake flask) | **0.28 h⁻¹** reference → **0.16 h⁻¹** recombinant | p.360 |
| Y_x/s, batch | **0.30** (ref) → **0.35** g_CDW/g_glucose (recomb.) | p.360 |
| µ, ¹³C fed-batch | **0.12 h⁻¹**, both strains, set by pump rate | p.363, Table I |
| Y_x/s, fed-batch | **0.55** (ref), **0.50** g/g (recomb.) | p.363, Table I |
| **q_glucose, fed-batch** | **1.2** (ref) and **1.4 mmol g⁻¹ h⁻¹** (recomb.) | p.363; Fig. 4 inset, p.365 |
| ATP regeneration | **4.8** (ref) → **7.6 mmol g⁻¹ h⁻¹** (recomb.) | p.363 |
| TCA flux (rel. to q_glucose) | batch 49% → 89%; fed-batch **55% → 75%** | p.360, p.363 |
| Respiration rate (rel.) | batch 192% → 306% | p.360 |
| HCD run | batch 25 g/L glucose, exhausted ~29 h; µ_max ~0.15 h⁻¹; fed-batch at **0.13 h⁻¹ for 36 h**; total **66 h** | p.363 |
| Growth ceiling observed | constant µ up to **~155 g_CDW/L**, decreasing thereafter; run aborted on **volume**, not on non-growing cells | p.363 |
| Final density | **218 g_CDW/L**; 570 g_CDW in 2.6 L; average Y_x/s **0.5 g/g** | p.363 |
| **Titer** | **~6.5 g/L BapA**, 0.13 U/mg_prot, **0.03 g_BapA/g_CDW** | p.364 |
| Scale caveat | those biomass concentrations are stated to be reachable only in small-scale fermenters, oxygen transfer and heat removal being limiting at larger scale | p.366 |
| Heat, 1,000 L illustration | 50 g/L, µ = 0.1 h⁻¹: **16 kW** glucose, 24 kW glycerol/methanol mix, **180 kW** methanol | p.366 |
| Yield on carbon | **16.5 g_CDW/Cmol** glucose vs **4.8 g_CDW/Cmol** methanol | p.366 |
| Carbon balance | measured CO₂ evolution rates **95 ± 3%** of the rates calculated by the flux model (CO₂ was *not* used as a constraint) | p.360 |
| Electron balance | none published. NADPH regeneration was *derived* from the fitted fluxes, not constrained (p.360). Fig. 4 (p.365) gives relative net NADH-dehydrogenase fluxes 297/131 (ref) and 392/141 (recomb.), cytosolic/mitochondrial, normalised to q_glucose = 100 |
| Growth vs production | the study reads the burden as a *cost*: recombinant production is said to raise NADH/ATP demand and redirect carbon to the TCA cycle "at the cost of growth and productivity" (p.367), and the batch data show the better producer growing **slower** (0.28 → 0.16 h⁻¹) | p.360, p.367 |

### ⚠️ The single most important finding about this paper
**BapA is an intracellular product.** The vector is pGAPZ A (no α-factor secretion signal, p.358); activity was assayed "using cell crude extracts after sonification" (p.358); and the titer is derived from the **biomass crude extract** specific activity (p.363), i.e. 0.03 g/g × 218 g/L = 6.5 g/L. Heyland is therefore **not evidence for secreted productivity at all** — it is evidence about growth, yield, uptake, density and heat on glucose. Any use of its 6.5 g/L as a secreted-titer precedent would be wrong. *(Confidence: high.)*

**My arithmetic on Heyland**
- q_glucose: 1.2 mmol/g/h = **0.216 g/g/h**; 1.4 mmol/g/h = **0.252 g/g/h**. Cross-check µ/Y = 0.12/0.55 = 0.218 and 0.12/0.50 = 0.240 — so the published yields are *observed* (maintenance-inclusive) yields, consistent to ~5%.
- q_P (intracellular) = Y_p/x · µ = 0.03 × 0.12 = **3.6 mg/g/h**; at µ = 0.13, **3.9 mg/g/h**.
- Volumetric: 6.5 g/L / 65 h = **100 mg/L/h**; over the 36 h fed-batch only, 181 mg/L/h.
- q_O2 by electron balance on the model's own biomass formula (γ = 4.059 e⁻/C-mol, 25.20 g/C-mol): **≈ 2.4 mmol O₂/g/h** (ref) and **≈ 3.3 mmol O₂/g/h** (producer) at µ = 0.12. No measured OUR is published.
- **Validation of `fermenter.heat_per_o2_kJ = 460`:** reproducing Heyland's 1,000 L illustration (50 g/L, µ = 0.1, Y = 0.5) gives q_s = 0.20 g/g/h → q_O2 = 2.63 mmol/g/h → OUR = 132 mol O₂/m³/h → **16.8 kW/m³** against their printed **16 kW**. A 5% match, independently derived. Good news for the model's heat and electron bookkeeping.

---

## 2. Looser 2015 — extraction

**Growth (Table 2, PDF p.39; ms. p.4, PDF p.7)**
- Methanol µ_max: Mut⁺ **0.028–0.154 h⁻¹**, Mut^S **0.011–0.035 h⁻¹** (ms. p.4).
- Glucose batch: "µmax varied from 0.28 h⁻¹ to 0.16 h⁻¹ for strains differing with respect to productivity, whereas the best-producer strains grew slower" (ms. p.4, PDF p.7) — citing Heyland.
- Y_x/s: methanol **0.15–0.42 g/g**; glycerol **0.43–0.72 g/g** (the 0.72 row is footnoted as a **glucose** value, Paulova 2012, with µ_max 0.28).
- **m_s (maintenance): methanol 0.011–0.03 g g⁻¹ h⁻¹; glycerol 0.009–0.032 g g⁻¹ h⁻¹.** **No glucose maintenance coefficient is tabulated anywhere in the review.** The only m_s used in the review's own calculations is **0.016 g g⁻¹ h⁻¹ for methanol** (Zhang 2005), with Y_x/s 0.61 glycerol and 0.33 methanol (ms. p.13, PDF p.16; Fig. 5 legend).

**Specific productivities of secreted products (Table 3, PDF p.41–42)** — q_p,max in mg g⁻¹ h⁻¹ at the optimal µ:

| Promoter / substrate | µ(q_p,max) range | q_p,max range |
|---|---|---|
| AOX1 / methanol (Mut⁺, Mut^S) | 0.002 – 0.14 h⁻¹ | **0.004 – 0.42** |
| AOX1 / methanol:glucose 40:60 | 0.07 h⁻¹ | **0.69** (trypsinogen, the table maximum) |
| **GAP / glucose** | **0.15 – 0.20 h⁻¹** | **0.05, 0.049, 0.15, 0.49** (Buchetics 2011 Fab 3H6; Maurer 2006 Fab 2F5; Rebnegger 2014 HSA; Khasa 2007 hG-CSF) |

So **the whole table spans 0.004–0.69 mg g⁻¹ h⁻¹**, and every GAP/glucose entry has its optimum at µ ≥ 0.15 h⁻¹.

**Growth-coupling statements** (these settle reviewer point (b) in the reviewers' favour)
- ms. p.6 (PDF p.9): GAP-controlled production of secreted proteins is growth-associated and typically increases linearly with µ up to close to µ_max.
- ms. p.5–6 (PDF p.8): for GAP strains, product formation increases with µ almost up to µ_max (citing Khasa 2007, Maurer 2006); for AOX1 Mut⁺ the optimum ranges from 0.002 h⁻¹ up to µ_max 0.14 h⁻¹, with negatively-growth-related kinetics only below µ_opt ≈ 0.004 h⁻¹.
- ms. p.14 (PDF p.17): "Maximum specific productivities within the range of 0.1 mg g⁻¹ h⁻¹ to 0.26 mg g⁻¹ h⁻¹ were reported at specific growth rates below 0.02 h⁻¹" — **this is the band the review itself puts on low-µ production, and it is AOX1/methanol.**
- ms. p.14: GAP processes reach specific rates comparable to AOX1 strains **but at µ near µ_max**.
- Fig. 3 (PDF p.32) states the growth-coupled relation used throughout: **q_p(µ) = µ · Y_p/x**.
- Optimal-strategy recommendation (ms. p.6 and p.14): grow fast to a high density first, then *decrease* µ during production; "a high initial concentration of biomass and a low specific growth rate during production are favourable" (ms. p.14) — note this is written about **AOX1/methanol**, whose kinetics are bell-shaped/negatively-coupled, not about GAP/glucose.

**Densities, titers, durations (Table 4, PDF p.43–44; ms. p.13–14)**
- CDW at the start of the induction/production phase in the literature: **20–100 g/L** (ms. p.13); Invitrogen recommends ~50 g_CDW/L; Zhang 2007 recommends **38–113 g_CDW/L** (ms. p.13).
- Highest final density: methanol fed-batch **150 g/L** (Curvers 2001a); glucose fed-batch **>200 g_CDW/L** (Heyland 2010) (ms. p.14). *(Heyland's own text, p.366, instead says 170 g/L for Curvers — the two papers disagree; minor.)*
- Highest titers: enzymes several g/L, top of table **19.55 g/L** glucose oxidase (168 h, 100 → 245 g/L, methanol/mannitol, AOX1); Fab fragments and hormones **1–4 g/L** (ms. p.13).
- Production-phase durations in Table 4: **25 h to 182 h** (median ~80 h).
- Scale/limits: "Oxygen and/or heat transfer are most often the limiting factors in high cell density *P. pastoris* cultivations" (ms. p.14, PDF p.17); high titres are attributed partly to high biomass and long production times (ms. p.13). The review gives **no industrial vessel size and no statement about m³-scale operation.**

**My arithmetic on Looser Table 4** (process-average q_P = c_p / (t · log-mean CDW); these are *averages*, not q_p,max)
| Row | q_P (mg/g/h) |
|---|---|
| glucose oxidase, AOX1, MeOH/mannitol (100→245 g/L, 168 h) | **0.72** |
| lipase/acetyltransferase, AOX1, MeOH (20→74 g/L, 119 h, µ 0.01) | **1.18** ← best internally consistent value |
| insulin precursor, AOX1, MeOH (56→59 g/L, 130 h) | 0.51 |
| IgG1, AOX1, MeOH (30→138 g/L, 182 h) | 0.13 |
| Fab 3H6, GAP, glucose (→100 g/L, ~25 h) | 1.5–3.3 depending on the unstated starting density |

⚠️ Looser's own tables are mutually inconsistent for Buchetics' Fab 3H6: Table 3 gives q_p,max = 0.05 mg/g/h (chemostat) while Table 4 implies 1.5–3.3 mg/g/h (fed-batch). Treat the Table-4-derived numbers as soft. *(Confidence: medium.)*

---

## 3. Assessment

### Q1 — Is Intelligen's design point inside the reported range?

**Outside, on both axes, and not marginally.** Intelligen runs **4.75 mg g⁻¹ h⁻¹ at µ = 0.0014 h⁻¹**.

| Comparator | Value | Intelligen / comparator (my arithmetic) |
|---|---|---|
| Looser Table 3 maximum, any promoter/substrate | 0.69 | **6.9×** |
| Looser Table 3 maximum, GAP/glucose (at µ = 0.20!) | 0.49 | **9.7×** |
| Looser Table 3 entry nearest µ = 0.0014 (Kobayashi hSA, µ_opt 0.002) | 0.26 | **18×** |
| Looser's own low-µ band ("below 0.02 h⁻¹") | 0.1–0.26 | **18–48×** |
| Best Table 4 process average (my arithmetic, Brunel lipase) | 1.18 | **4.0×** |
| Prielhofer 2018 (your note, glucose fed-batch, µ ≈ 0.1) | 2.1 | **2.3×** |
| Rebnegger 2024 VHH peak (already in `base.yaml`) | 0.64 | 7.4× |

Volumetrically the same gap appears: Intelligen's 30 g/L in 72 h = **417 mg L⁻¹ h⁻¹**, against **116 mg L⁻¹ h⁻¹** for the best process in Looser Table 4 — **3.6×** the best published space-time yield, at a growth rate 100× lower than any GAP/glucose optimum in the literature. The double bind is what matters: the design asks for the *highest* q_P ever reported **and** asks for it at the *lowest* growth rate ever reported, from a promoter class (GAP/glucose) whose kinetics both papers describe as growth-**proportional**.

**What I would call "demonstrated" for secreted proteins in K. phaffii fed-batch** *(confidence: medium-high for the bands, high for the ordering)*:
- **Glucose or glycerol (GAP):** q_p,max **0.05–0.5 mg g⁻¹ h⁻¹**, always at **µ = 0.15–0.20 h⁻¹** (Looser Table 3). Process averages from Table 4 stretch this to ~1–3 mg/g/h but rest on unstated starting densities. With Prielhofer 2018 (2.1 mg/g/h at µ ≈ 0.1) added, I would call **up to ~2 mg g⁻¹ h⁻¹ at µ ≈ 0.1–0.2 h⁻¹** the defensible ceiling, and **< 0.1 mg g⁻¹ h⁻¹ at µ < 0.01 h⁻¹** the defensible expectation, because on a GAP promoter q_P falls with µ.
- **Methanol (AOX1):** q_p,max **0.004–0.42 mg g⁻¹ h⁻¹** (0.69 for a methanol:glucose mix), process averages up to **~1.2 mg g⁻¹ h⁻¹**; here the *low*-µ end is genuinely productive (0.1–0.26 mg/g/h below µ = 0.02 h⁻¹), which is exactly the regime AOX1 processes are designed for and the regime GAP/glucose is not.
- **Intracellular, glucose:** ~3.6–3.9 mg g⁻¹ h⁻¹ at µ = 0.12–0.13 (Heyland, my arithmetic). Relevant only as an upper bound on total synthesis, not on secretion — secretion, not synthesis, is the bottleneck this model is pricing.

### Q2 — Is the production-phase maintenance consistent, and what q_s do production phases actually run at?

**The maintenance value is below every maintenance coefficient these two papers contain.** `m_s_prod = 0.00437 g g⁻¹ h⁻¹` sits under Looser Table 2's full range (**methanol 0.011–0.03; glycerol 0.009–0.032**) by a factor of 2–7, and under the 0.016 g/g/h the review itself uses for its worked protocols. **Neither paper reports a glucose maintenance coefficient**, so neither confirms nor refutes Rebnegger 2024 directly — but neither offers any support for a value that low either. *(Confidence: high on the fact, medium on the implication: Rebnegger's value is at near-zero µ, where retentostat data do show maintenance falling, and the substrate differs.)*

Heyland's single-µ data cannot fit a Pirt line, but it can be inverted against an assumed maximum yield, which is diagnostic:

| assumed Y_x/s^max | implied m_s, reference strain | implied m_s, **producing** strain |
|---|---|---|
| 0.5705 (the model's) | 0.006 | **0.042** |
| 0.61 (Looser, glycerol) | 0.020 | 0.056 |
| 0.72 (Looser Table 2, glucose row) | 0.050 | 0.086 |

At µ = 0.12 you simply cannot separate yield from maintenance — but on the model's own Y_max, the *producing* strain's uptake implies ~0.042 g/g/h, **ten times** the model's production-phase value. That is an upper bound contaminated by growth-associated burden, not a maintenance measurement; report it as a bracket, not a number. *(Confidence: medium; flag this derivation for your own check, it is exactly the kind of inversion that is sensitive to the assumed Y_max.)*

**What q_s production phases actually run at:**
- Heyland fed-batch, glucose, µ = 0.12–0.13: **0.216–0.252 g g⁻¹ h⁻¹** (measured).
- Looser GAP/glucose optima at µ = 0.15–0.20 with Y ≈ 0.5: **≈ 0.3–0.4 g g⁻¹ h⁻¹** (my arithmetic).
- Looser's AOX1 standard protocols, methanol, µ = 0.01–0.05: q_s = µ/0.33 + 0.016 = **0.046–0.17 g g⁻¹ h⁻¹**; at µ → 0 the floor is the maintenance term, **0.016 g g⁻¹ h⁻¹** (my arithmetic on the review's stated parameters).
- **Model's base production phase: q_s = 0.0014/0.5705 + 0.00437 + 0.00475/0.465 = 0.00245 + 0.00437 + 0.01022 = 0.0170 g g⁻¹ h⁻¹.**

So the reviewers' point (a) is **substantially upheld, with a nuance.** 0.017 g/g/h is 3–15× below any *measured* production-phase uptake in these papers, and below the 0.02–0.05 g/g/h band they proposed. It is *not* below the tabulated maintenance range in absolute terms (0.017 > 0.009 and > 0.011) — but that is the damning part rather than a defence: at 0.017 g/g/h, **essentially the entire carbon flux is maintenance plus product, with nothing left over**, and the model is simultaneously assuming the cell secretes at 7–18× the best published rate while eating at roughly bare-maintenance. The two assumptions pull in opposite directions. Physiologically, secretion is ATP-expensive (Heyland's own framing: production raises TCA flux and ATP regeneration by ~60%, p.363), so a *higher*-secreting cell should have a *higher*, not lower, non-growth uptake.

### Q3 — What a growth-coupled production phase would imply (all arithmetic mine)

Using Looser's own growth-coupled relation **q_P = µ · Y_p/x** (Fig. 3, PDF p.32), so the integrated titer over a phase is simply **c_p = Y_p/x · ΔX**.

**Step 1 — the hard constraint nobody has flagged.** Starting at 107 g/L with `X_max = 150 g/L`, a 72 h phase admits at most **µ = ln(150/107)/72 = 0.0047 h⁻¹**. Running at µ = 0.02 for 72 h would take 107 → 450 g/L; at µ = 0.05, 107 → 3,900 g/L. **A growth-coupled phase at µ = 0.02–0.1 h⁻¹ is arithmetically incompatible with starting at 107 g/L for 72 h.** Reaching 150 g/L after 72 h requires starting at 35.5 g/L (µ = 0.02), 4.1 g/L (µ = 0.05) or 0.11 g/L (µ = 0.1). So "grow and produce simultaneously" is not a tweak to this design, it is a different plant.

**Step 2 — titers.** Y_p/x from the literature: 0.26 mg/g (Maurer Fab 2F5 and Buchetics Fab 3H6, 0.049/0.19 and 0.05/0.19), 1.0 mg/g (Rebnegger 2014 HSA), 2.45 mg/g (Khasa hG-CSF), 21 mg/g (Prielhofer 2018, 2.1/0.1).

| Y_p/x | µ = 0.02 (ΔX 114 g/L) | µ = 0.05 (ΔX 146 g/L) | µ = 0.1 (ΔX 150 g/L) | 107→150 g/L (ΔX 43) |
|---|---|---|---|---|
| 0.26 mg/g | 0.03 g/L | 0.04 | 0.04 | 0.01 |
| 1.0 | 0.11 | 0.15 | 0.15 | 0.04 |
| 2.45 | 0.28 | 0.36 | 0.37 | 0.11 |
| **21 (Prielhofer)** | **2.40** | **3.06** | **3.15** | **0.90** |

To hit the design's **30 g/L**, Y_p/x must be **200–262 mg/g** (µ = 0.02–0.1), or **698 mg/g** if you insist on staying inside the 107→150 g/L window. That is **10–33× Prielhofer** and **~800–2,700× Maurer/Buchetics**. *(Confidence: high — this is robust to every comparator choice.)*

**Step 3 — effective product yield on glucose**, µ = 0.05, X 4.1 → 150 g/L over 72 h, using `base.yaml`'s Y_x = 0.5705, growth-phase maintenance 0.0174 and Y_ps = 0.465; ∫X dt = ΔX/µ = 2,918 g·h/L:
- Prielhofer-like Y_p/x = 21 mg/g → titer **3.06 g/L**; glucose = 256 (biomass) + 51 (maintenance) + 6.6 (product) = **313 g/L** → **effective yield 0.0098 g/g**.
- Y_p/x = 205 mg/g (the value that would give 30 g/L) → glucose = 256 + 51 + 64.5 = **371 g/L** → **effective yield 0.081 g/g**.
- For comparison, Intelligen's decoupled expression phase is 28 g product per 100 g glucose = **0.28 g/g**, because it charges almost no glucose to new biomass (8 g cells per 28 g product).

**Step 4 — it also breaks the oxygen budget.** q_O2 from the electron balance: at µ = 0.05 and 150 g/L, **OUR = 223 mol O₂/m³ of broth/h**; at µ = 0.1, **359**. Against `otr_cap_mol_m3_h = 200` on a *cell-free-liquid* basis (≈ 129 per m³ of broth at 107 g/L), a growth-coupled production phase at µ ≥ 0.05 is oxygen-infeasible at these densities — which is precisely Looser's ms. p.14 point about O₂ and heat being the usual limits, and Heyland's p.366 point that 200 g/L is a small-scale-only achievement.

**Bottom line for Q3:** the reviewers are right that K. phaffii secretion is growth-coupled, but "just run it growth-coupled" does not rescue the design — it makes the economics dramatically **worse** (yield on glucose 0.01–0.08 vs 0.28 g/g, titer 3 g/L vs 30), and runs into the OTR ceiling. The honest reading is that **Intelligen's 30 g/L in 72 h has no physiological support in either direction**: not as a decoupled near-zero-µ phase (q_P 7–18× the literature) and not as a growth-coupled phase (Y_p/x 10–33× the literature, plus an O₂ wall). This is a titer/productivity problem, not a maintenance problem.

### Q4 — Other `base.yaml` numbers these papers bear on

**Contradicted or strained**
1. **`strain.q_p_max_mg_g_h = 40` (grade D).** Looser's compilation maxes at **0.69** (Table 3) and ~1.2 (Table 4, my arithmetic). A 40 mg/g/h ceiling is **~33–60× anything ever measured for a secreted protein in this host**. As a "physiological ceiling" it constrains nothing.
2. **`fermenter.feed_glucose_g_L` high = 600.** Heyland fed **730 g/L** (73% w/v, p.358). Lab scale, and probably heated, but it is a real published feed strength above your high.
3. **`hosts.kphaffii.mu_max_per_h` = 0.20 (0.15–0.25).** Heyland p.360 measured **0.28 h⁻¹** for the non-producing strain and **0.16 h⁻¹** for the producer; Looser Table 2 lists 0.28 on glucose. Your `high` should be 0.28, and — more useful for the model — **both papers say the better producer is the slower grower**, which is an argument against combining µ_max = 0.20 with a record q_P in the same strain.
4. **`hosts.kphaffii.m_s_prod_g_g_h` high = 0.0161.** Looser Table 2 goes to **0.032** (hG-CSF, glycerol) and 0.03 (methanol). Your high is half the published spread.
5. **`strain.X_prod_g_L = 107`** sits **above** the 20–100 g/L that Looser reports as literature practice (ms. p.13), though inside Zhang 2007's recommended 38–113 g/L. Defensible, but it is at the extreme, and both papers warn the record densities are lab-scale artefacts.
6. **`strain.mu_prod_per_h` high = 0.02** is infeasible *within the model's own constraints* (see Q3 Step 1): from 107 g/L over 72 h, X_max = 150 caps µ at 0.0047 h⁻¹. The tornado's high end is exploring an impossible corner.

**Supported / validated**
7. **`fermenter.heat_per_o2_kJ = 460`** — independently reproduces Heyland's 16 kW illustration to 5% (my arithmetic above). Nice confirmation of the whole heat/electron chain, including the biomass formula.
8. **Methanol-free base** — strongly supported: Heyland p.366 quantifies the methanol penalty as 180 kW vs 16 kW, and Y 4.8 vs 16.5 g_CDW/Cmol.
9. **`hosts.kphaffii.biomass_formula`** (Carnicer) gives γ = 4.059 e⁻/C-mol, which closes Heyland's yields and heat correctly. No contradiction.
10. **`strain.X_max_g_L = 150` (high 200)** — Looser ms. p.14 gives 150 g/L (methanol) and >200 g/L (glucose); Heyland reached 218 g/L but growth *already decelerated above ~155 g/L* (p.363) and he states the density is not scalable (p.366). Your value and range are well chosen; I would add the deceleration observation to the source note.
11. **`hosts.kphaffii.maint_factor` = 1.0 on Tijhuis 0.0174** — bracketed by Looser Table 2's 0.009–0.032, albeit on glycerol/methanol. Reasonable.
12. **`strain.t_prod_h = 72`** — Looser Table 4 spans 25–182 h, so 72 h is inside but at the short end; combined with a record q_P it is the aggressive corner of both variables at once.
13. **`strain.titer_g_L = 30`** — the highest **secreted** titer in Looser's compilation is **19.55 g/L**, and that took **168 h at 100→245 g/L on methanol/mannitol**. Nothing in either paper supports 30 g/L in 72 h.

---

## 4. Recommendations

| # | Parameter | Current | Proposed | Source / basis | Confidence |
|---|---|---|---|---|---|
| R1 | `strain.q_p_max_mg_g_h` | 40 (5–40), grade D | **5** (2–10), grade **B** | Looser Table 3 max 0.69; Table 4 process averages ≤ ~1.2 (my arithmetic); Prielhofer 2018 2.1. 5 keeps headroom for an engineered strain without being 40× off the record | high |
| R2 | `strain.q_p_max` **low** | 5 | **2** | With low = 5 the feasibility floor already excludes the base case's 4.75 only marginally; 2 mg/g/h is the honest "best demonstrated" anchor | medium |
| R3 | `hosts.kphaffii.m_s_prod_g_g_h` **high** | 0.0161 | **0.032** | Looser Table 2, hG-CSF/glycerol (0.032) and methanol α-galactosidase (0.03) | high |
| R4 | `m_s_prod` **value** | 0.00437 | **keep**, but re-grade the note | Neither paper has a glucose m_s; Rebnegger 2024 remains the only direct evidence. Add: "below every maintenance coefficient in Looser 2015 Table 2 (0.009–0.032 g/g/h, glycerol and methanol)" so the reader sees the tension | high |
| R5 | `strain.mu_prod_per_h` **high** | 0.02 | **0.0047** *or* make the tornado respect X_max | ln(150/107)/72; at 0.02 the phase would need 450 g/L of cells | high |
| R6 | `hosts.kphaffii.mu_max_per_h` **high** | 0.25 | **0.28** | Heyland p.360; Looser Table 2 (glucose, Paulova) | high |
| R7 | `fermenter.feed_glucose_g_L` **high** | 600 | **730** (or note it) | Heyland p.358, 73% w/v | medium (lab scale) |
| R8 | **New feasibility check** | — | assert **q_s,prod ≥ m_s** and report q_s in the design table | The base case runs at 0.0170 g/g/h total uptake, of which 0.0044 is maintenance; making q_s a reported output would have surfaced this in review | high |
| R9 | **Source note on `strain.titer_g_L`** | cites Intelligen + patents | add the literature ceiling | Looser Table 4: best secreted titer 19.55 g/L in 168 h at 100→245 g/L; Fabs and hormones 1–4 g/L. The base case is 3.6× the best published volumetric productivity | high |
| R10 | **Do not cite Heyland for titer or q_P** | — | — | BapA is intracellular (pGAPZ A, crude-extract assay); its 6.5 g/L is not a secreted titer. Cite it for density, Y_x/s, q_s, µ_max, heat and the methanol comparison only | high |
| R11 | `strain.X_max_g_L` source note | — | add the deceleration datum | Heyland p.363: constant µ only up to ~155 g/L; and p.366 that such densities are small-scale-only | high |
| R12 | Citation hygiene | — | re-check Looser page numbers against the typeset article (1177–1193) before they enter `base.yaml` | the PDF on file is the accepted manuscript | high |

**Caveat I would carry into the report.** The two reviewers' objections are both well-founded on the evidence, but they do not combine into a fix. Correcting (a) — raising production-phase uptake to a physiologically plausible 0.02–0.05 g/g/h — makes the glucose bill worse at unchanged titer. Correcting (b) — making secretion growth-coupled — collapses the titer by an order of magnitude and hits the OTR cap. The parameter actually doing the work in this design is **`titer_g_L = 30` combined with `t_prod_h = 72`**, and that pair is where I would put the sensitivity and the honesty about evidence grade, rather than in the maintenance coefficient. *(Confidence: high on the direction; the specific factors above are mine and worth your check, particularly the Pirt inversion in Q2 and the Y_p/x table in Q3.)*
