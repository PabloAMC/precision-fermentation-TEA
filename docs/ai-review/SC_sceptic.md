<!-- Simulated review. Written by an AI model (Claude) instructed to review as a sceptic of precision-fermentation cost claims.
It is not the opinion of any person and has not been checked by one. Kept verbatim (local file paths redacted) as delivered on
2026-09-27 against commit 5cbf9bc; responses and changes are in docs/REVIEW.md (AI pre-review log). -->

> **Simulated AI review (SC): sceptic of precision-fermentation cost claims.** Not a human expert's opinion. Verbatim; line and page
> references are to commit 5cbf9bc (v2). Responses: [docs/REVIEW.md](../REVIEW.md#ai-pre-review-phase-f).

# Simulated AI review: a sceptic of PF cost claims (reviewer "SC")

**How I checked.** I read the report text and its typst source, the memo, README, REVIEW, AUDIT, VALIDATION, SCOPE and PLAN, the scenario, benchmark and evidence files, and `results/analyses.json`.

I re-ran the model from the audit worktree (`PYTHONPATH=pf-tea-audit/src`). The base case reproduces $29.3694. My runs used `PYTHONDONTWRITEBYTECODE`, and `git status` is clean, so nothing in the repo was modified. The scripts and outputs are in `<scratch>/review/sc/`:
- `base_search.py` and `req_x.py`
- `short_tprod.py` and `minfill.py`
- `pl_decomp.py` and `pl_qp5.py` (results in the `.json` files of the same name)
- `mc_flags.py` (results in `mc_*.json`)

I re-raise only three items that AUDIT.md lists as addressed: R7-Q6, R7-M7 and the q_p sensitivity from R7-C2. In each case I say why the fix is incomplete.

---

## Comments (most severe first)

### SC-1: major, error. "$10/kg needs every lever" is contradicted by the model; the real gate is specific productivity

**Where**
- §4.4, p.14 (typ 831–832): "Titer alone is therefore not enough for $10/kg: yield, cell density, production time, vessel size, the capital convention and scale must move too".
- §5.3 check box, p.18 (typ 1069–1072): "only if every lever moves at once".
- Memo, typ 85–92: "Beyond that, yield, cell density, production time, capital and scale must move together."
- Also Summary item 1 (typ 157–163) and Table 6 / Fig. 6.

**Comment.** Two changes are enough to get below $10/kg:
- lower the cell density at the start of production;
- let the titer rise.

Everything else stays at base: yield 0.465, maintenance, 200 m³ vessels, 10 kt/yr, US prices and price-anchored capital. So yield, vessel size, capital convention and scale do not need to move.

What must move is specific productivity (q_p), to about 8× the base design. That is close to the 40 mg/g/h ceiling, which is a grade-D judgment. The Q3 frontier hides this because Table 6 and Fig. 6 fix the cell density at Intelligen's 107 g/L (`s_required` uses the base parameters).

For the same reason, the Summary's "a 200 m³ fermenter reaches about 74 g/L" describes that cell density, not the vessel. With 70–80 g/L cells the same vessel reaches 100–106 g/L at 72 h.

**What I checked**
- Runs changing only cell density, production time and titer:
  - 80 g/L cells, 60 h, 101 g/L gives **$9.19/kg**. It is feasible with no flags, q_p is 38.4 mg/g/h, the batch starts at 30.2% fill and uptake sits at the 150 cap.
  - 70 g/L cells, 72 h, 105.5 g/L gives **$9.40** (q_p 39.4).
  - Design-report capital gives $5.4–5.5 for these designs.
- The report's own sentence holds at 107 g/L cells. The cheapest design at 12–48 h is $10.41 (30 h).
- Required titers (cells 60/80/107 g/L, 48/72 h), in q_p terms:

| Target | Titer needed | Implied q_p |
|---|---|---|
| $20/kg, price-anchored | 32–47 g/L | 8–13 mg/g/h |
| $10/kg, price-anchored | 87–100 g/L | 32–38 mg/g/h |
| $10/kg, design-report | 41–53 g/L | 9–13 mg/g/h |

- For comparison:
  - the base design runs at q_p 4.65 and the industry benchmark at 6.9;
  - base.yaml says K. phaffii secreted-protein q_p is "typically 0.1-5 mg/g/h";
  - the best public K. phaffii secreted titer is 30.7 g/L (glucose oxidase, methanol-induced; hosts.yaml, Lv 2025);
  - the best methanol-free titer is 2.49 g/L.
- The sub-$10 designs imply an overall sugar yield of 0.29 g/g. Private companies' own cost models use 0.03–0.17 g/g (GFI 2025 Table 2).
- The tornado agrees: at a fixed titer, fewer cells are cheaper ($17.4 at 40 g/L cells, against $21.9).

**Suggested fix**
- §4.4: "At the base yield, vessel, scale and price-anchored capital, the model reaches $10/kg only if specific productivity nears its assumed 40 mg/g/h ceiling (32–38 mg/g/h, about 8× the base design and above any published K. phaffii value). That means fewer cells at induction (60–90 g/L) and 90–105 g/L in 48–72 h. Yield, vessel size, capital convention and scale are secondary."
- Check box: replace "every lever at once" with "an eightfold rise in specific productivity".
- Express the "required" frontier in q_p terms, or optimise cell density. PLAN.md rule 1 makes this the headline figure; today the Summary leads with the base case instead.
- Qualify the 74 g/L ceiling with "at 107 g/L cells".

### SC-2: major, overclaim. The "physical-limit floor" is set by a judgment, not by physics or measured biology

**Where**
- Summary item 2 (typ 164–167): "with every biological parameter at its best measured or theoretical value at once".
- §4.5, p.15 (typ 858–861): "what physics and stoichiometry allow".
- Memo, typ 63–66: "The gap between today and the floor is engineering and biology, not thermodynamics."
- §2.7 and Table 1.

**Comment.** At the floor the binding biological parameter is the 40 mg/g/h secretion ceiling (q_p 39.7). It is grade D: "judgment… No K. phaffii measurement near it". The sensitivity the report shows (20 and 120 mg/g/h) lies entirely above the measured range, and the floor moves almost one-for-one with this assumption.

Four more problems:
- **Yield.** The physical-limit yield of 0.55 is at or above the report's own corrected energetic ceiling.
- **Binding constraints.** All three are judgments or design choices: O₂ at 250 mol/m³/h (grade D), q_p (grade D) and the minimum fill (a design choice).
- **Non-biological levers.** Several are relaxed as well; the Summary mentions only "100 kt/yr".
- **Not a lower bound.** Relaxed design choices, continuous operation and design-report capital ($3.6) all give lower costs.

**What I checked**
- JSON `physical_limit`: BLG floor $6.107, binding constraints [O2 transfer, specific productivity, minimum initial fill]. The q_p 20 and 120 sensitivities give $8.24 and $4.56.
- My `physical_limit` searches with a lower q_p ceiling:
  - 10 mg/g/h gives **$11.54** (130 g/L cells, 81 h, 72 g/L).
  - 5 mg/g/h (the top of base.yaml's "typical" range) gives **$16.70**, or $8.81 with design-report capital.
  - So the floor crosses $10 somewhere between a 10 and 20 mg/g/h ceiling, and at 5 it sits inside the whey band.
- Yield: the energetic ceiling is 0.5824 (BLG) and 0.590 (OVA).
  - §2.2 says the ceiling omits 5–7% (amino-acid synthesis); AUDIT R1-F11 adds 1.3–1.6% (sulfate reduction).
  - Corrected ceilings are 0.533–0.546 (BLG) and 0.540–0.553 (OVA).
  - 0.55 is therefore 99–103% of the corrected ceiling, not "about 95%".
- Levers changed in `physical_limit.yaml`: 400 m³, O₂ cap 250, 40 kW/m³, 8 h turnaround, $0.31 sugar, 100 kt/yr and 90% purity. The last two are missing from the §2.7 list.
  - Best biology with base engineering and commercial settings gives $8.39 (my run).
  - Base biology with q_p free gives $9.2 (SC-1).
  - So about $2.3 of the step down to $6.1 comes from engineering and scale.
- The floor designs imply an overall sugar yield of 0.36 g/g, twice the top of the private models' range.

**Suggested fix**
- Rename it a "best-case design point".
- Summary: "$6.1/kg BLG ($3.6 design-report) in 400 m³ vessels at 100 kt/yr, with contract sugar, O₂ transfer at 250 mol/m³/h, best yield and maintenance, and cells secreting 40 mg/g/h. That secretion rate is a judgment about 8× the base design, and no K. phaffii measurement is near it. At 10 mg/g/h the result is $11.5; at 5 it is $16.7."
- Add the floor-versus-q_p-ceiling curve to §4.5 and the memo.
- Call the yield "at the corrected energetic ceiling".
- List every changed lever in §2.7.
- Memo: replace "not thermodynamics" with "mostly an assumed secretion rate".

### SC-3: major, judgment call (R7-Q6 fix incomplete). "Price-anchored" capital cannot distinguish the two conventions

**Where**
- Summary paragraph 1 (typ 138–140).
- §1 "Why Humbird's method" (typ 254–258).
- §2.5 (typ 457–458): "with these factors Humbird's baker's-yeast workbook reproduces a market price".
- §3, p.9 (typ 613–616): "the only convention tied to a real product price".
- §5.2 (typ 1045): "conservative central estimate".
- Explorer hint (`build_explorer.py:199`).

**Comment**
- **(a) Different factors.** The workbook does not use "these factors". A.1 uses a flat Lang factor of 4.5 on an abbreviated equipment list with a 20% missing-items allowance, and a **10%/20-year** capital charge (CCF 11.75%). The PF base uses the facility-class chain and 7.5%/10 years (CCF 14.57%). With the PF base's charge, the yeast cost becomes **$2.00/kg**.
- **(b) The anchor cannot discriminate.** Humbird's own inputs ($2.20–2.80/kg wholesale, 33% margin) imply a cost of $1.47–1.88; the port's $1.89 sits at the top edge. Capital-related charges are 44% of the yeast cost, so any capital burden between about half and all of Humbird's fits the range.
- **(c) Half the gap is fixed-cost rates.** Of the $13.31 gap between conventions for base BLG, capital charge is $6.43 (48%). The other $6.88 (52%) is maintenance plus insurance: 4% + 5% of investment per year, which Humbird §3.3 "takes" without a source. NREL uses 3% of installed process cost plus 0.7% of fixed capital.
- **(d) Intelligen matches the lighter capital.** Its total capital investment ($92.0M) matches our design-report estimate for its configuration ($87.0M), not our price-anchored one ($147.1M).
- **(e) Our own DCF is lighter.** The report's discounted-cash-flow price at a 10% return over 30 years ($28.5) is below the headline figure ($29.4).

**What I checked**
- `humbird_bakers_yeast.yaml`: `lang_factor` 4.5 (A.1!D160), `lifetime_y` 20 (A.1!B256), `irr` 0.10 (A.1!B257).
- `humbird_yeast.run()`: $1.8899 = variable $0.921 + labour $0.143 + maintenance $0.159 + insurance $0.199 + capital $0.468. The same run at 7.5%/10 years gives $2.0024.
- Humbird 2021 Appendix A quote on the wholesale range and margin.
- `calibration.run('intelligen2025_ova', LIGHT)`: TCI $87.0M, $29.24 per kg powder.
- The base with A.1's own capital charge: BLG $26.98, industry benchmark $20.12.
- I could not run NREL-style factors on the yeast port. Whether that convention itself lands inside the $1.47–1.88 range is uncertain (about 60% confidence); my extrapolation gives about $1.34, slightly below.

**Suggested fix**
- Call it the "Humbird convention".
- §2.5: "With a flat Lang factor of 4.5 and a 10%/20-year charge, Humbird's yeast workbook lands at the top of the cost range implied by the yeast price ($1.47–1.88/kg). That check cannot separate our two conventions, because capital-related charges are 44% of the yeast cost. Half the gap between conventions is the 9%/yr maintenance-and-insurance rate."
- Drop "the only convention tied to a real product price" and the word "central".
- Show headline costs as a range across the two conventions ($16–29/kg for base BLG).

### SC-4: minor, error plus one-sided sensitivity. What sets the titer ceiling

**Where**
- Summary item 1 (typ 157–163): "with a 20% start or a 65% feed the ceiling rises to about 125 g/L, where the secretion rate or O₂ transfer binds instead".
- Memo typ 59: "relaxed, the secretion rate and O₂ transfer set the ceiling instead".
- §5.5 (typ 1090–1092): "O₂ transfer (150–200 mol/m³/h, on either basis) would set it".
- docs/REVIEW.md lines 42 and 60; docs/AUDIT.md line 324.

**Comment.** The report's own Table 7 says otherwise. At 72 h the ceiling after either relaxation (125–126 g/L) is **still set by the minimum starting volume**:
- the secretion ceiling binds only when the fill limit is removed entirely (129 g/L);
- O₂ binds only on Humbird's cell-free basis (112 g/L), never on the base (per-broth) basis.

The sensitivity is also one-sided. Only relaxations are shown, yet the base fill (30%) is the most permissive end of its sourced range (0.30–0.50).

**What I checked**
- JSON `ceiling_limits` at 72 h:

| Case | Ceiling | Binding limit |
|---|---|---|
| minimum fill 0.20 | 124.8 g/L | minimum starting volume |
| glucose feed 65 wt% | 126.3 g/L | minimum starting volume |
| no minimum fill | 128.6 g/L | secretion ceiling |
| no minimum fill, cell-free O₂ basis | 112.4 g/L | O₂ transfer |

- My runs at 107 g/L cells, tightening the fill:
  - 35% gives a 72 h ceiling of 49 g/L;
  - 40% gives 23.6 g/L, and the base design itself becomes infeasible (it starts at 38.7% of the vessel);
  - 50% (NREL's start) gives no feasible titer at 36–120 h.
- Re-optimising cell density restores feasibility ($10.4 at 40% fill, $11.8 at 50%).
- The tornado truncates the fill parameter at 0.363 with a $0.00 swing (rank 49, not shown in Fig. 4). The Monte Carlo does not sample it.

**Suggested fix**
- Summary: "…rises to about 125 g/L, still set by the starting volume. With no volume limit, the secretion ceiling binds at 129 g/L (O₂ at 112 g/L on Humbird's basis). The other way, it falls to 49 g/L at a 35% start, and at 40% the base design cannot run."
- Add rows for 0.35, 0.40 and 0.50 fill, and for 80 g/L cells, to Table 7.
- Correct the memo, §5.5, REVIEW A4/B3 and AUDIT.
- Mark the fill bar in the tornado "benchmark infeasible above 0.36".

### SC-5: minor, overgeneralised. "Published costs are 2.4–2.5× lower" and "most published PF studies"

**Where**
- Summary item 3 (typ 168–170) and typ 147.
- §2.5 (typ 461), §5.2 (typ 1039–1041: "Where we can reproduce the process (NREL, Voutilainen)").
- Memo typ 48, the explorer, REVIEW 52–53 and 116, VALIDATION 165.

**Comment**
- 2.4–2.5× comes from NREL's 2011 on-site cellulase (2.54×) and Voutilainen's lignocellulose case (2.43×).
- The one food-protein PF design the report rebuilds, Intelligen's OVA, is only 1.14× lower than ours on the recast basis, or 1.27× lower against its own $38.99/kg powder. Its total capital investment matches our design-report estimate.
- §5.2 leaves the rebuilt Intelligen design out.
- No survey in the repo supports "most published PF studies".
- Even on NREL and Voutilainen, a +36% / +23% gap remains after switching conventions, so conventions explain about two-thirds to three-quarters of the gap in log terms.
- Inconsistent figures elsewhere:
  - VALIDATION says "2.3–2.5×";
  - REVIEW B1 says "2.4–2.5× the NREL-style convention on the same process", whereas within the model the two conventions differ by 1.83×, and gives Lang "~5.1" against the report's 5.2;
  - the engineer email says "about 2.5×".

**What I checked.** JSON `calibration`, and my Intelligen runs under both conventions ($49.47 and $29.24 per kg powder).

**Suggested fix**
- "On the two designs we can rebuild from their own inputs (NREL's on-site cellulase and Voutilainen's recombinant case), published costs are 2.4–2.5× lower than ours, about two-thirds to three-quarters of that from conventions. Intelligen's OVA design lies between our two conventions ($39/kg powder against our $29–49)."
- Replace "most published PF studies" with "NREL-style design reports".
- Align REVIEW and VALIDATION.

### SC-6: minor, selective comparison. Lactoferrin: the only published PF-lactoferrin cost is omitted, and our model sits at about half of it

**Where**
- Summary item 4 (typ 171–176).
- §4.9 (typ 1000–1007), §5.1 Q8 (typ 1033), §5.3 (typ 1065–1066), memo bullet 3.

**Comment**
- The 10 g/L design titer comes from Intelligen's 2024 lactoferrin design. That design's own cost of production is **$292/kg** (GFI 2025 p.31). GFI's appendix (row 177) normalises it to $262.43/kg at 251.3 t/yr, with operating cost $65.95M/yr and capital $122.53M, for UF/DF only.
- Our identical configuration (`lf_ufdf_only`) comes to $147 including the 14.6% capital charge. Its cost of production is $126 and its capital $115M. Our cation-exchange route gives $216.
- So for lactoferrin the model is about half the published design, while for OVA it is 14–27% above Intelligen. Capital is similar, so the difference is operating and fixed cost: our labour is $4.2M/yr against their $66M/yr total operating cost, and we have no QC/QA operating line. About 70% confidence on that cause; Intelligen's breakdown is not on disk.
- The upper half of the price band ($750–1,500/kg) comes from TurtleTree, itself a PF-lactoferrin seller (2023), and a "retail costs" figure (Green Queen 2025). The band is in nominal dollars, unlike whey and egg.
- The conclusion survives anyway:
  - Intelligen's $292 is below 7 of the 8 reported price points;
  - our academic-titer cost of $531 is below 6 of 8.
- "Already" rests on a design titer. The best public methanol-free secreted lactoferrin is 2.8 g/L (porcine), which costs $531.

**Suggested fix**
- Add the "Intelligen 2024 design (their model): $292/kg" row to Table 9.
- State the gap relative to OVA and check the fixed-cost model at 250 t/yr.
- Summary: "At a 10 g/L design titer (not yet public for bovine lactoferrin), PF lactoferrin costs less than most reported dairy prices, in our model and in Intelligen's ($292/kg)."
- Deflate the band to 2025 dollars, or say it is nominal, and flag the interested-party source.

### SC-7: minor, inconsistency (R7-M7 fix incomplete). The claims table undercuts the report's own benchmark

**Where**
- Table 8 and text, p.15 (typ 863–898).
- Summary typ 148 and memo typ 46 ("Industry-level titers").
- Fig. 7 title "today's benchmarks".

**Comment**
- Table 8 prices each claim at its *shortest* feasible production phase. That forces q_p to 38–40 mg/g/h, the judgment ceiling.
- The GFI 42 g/L row therefore costs **$14.8 / $9.5** (12.75 h). The report's own industry benchmark at the same titer costs **$21.9 / $12.1** (72 h).
- R7-M7 asked to "reconcile or unify" the two costs for 42 g/L. Both are still shown, with no reconciliation, and the gap has widened (v1: $22.8 against $18.5).
- Behm's 50 g/L is priced at 48 h ($13.3 / $7.3). Behm's own design runs 120 h, which gives $20.0 / $9.6.
- The 24 g/L row's 12 h is the search's lower bound (`lo=12`), not a physical result.
- The Onego quote is "their platform can reach titers of up to 120 g/L", with the protein unspecified (titers.csv note). The table calls it an "ovalbumin claim" and "concerns OVA at 120 g/L".
- The 42 g/L is an average over private companies' cost models ("industry TEM data…, not measurements", titers.csv), not an achieved titer.

**What I checked.** JSON `claims`, and my runs of Behm's design at 96 and 120 h.

**Suggested fix**
- Price claims at their own production time (Behm 120 h) or at 72 h.
- Keep the shortest-time cost as a separate, labelled "best case at q_p ≈ 40" column.
- Add one sentence reconciling $14.8 with $21.9.
- Relabel the row "Onego platform claim (protein not specified; tested as OVA)".
- Describe the 42 g/L as "the average titer assumed in private companies' cost models".

### SC-8: minor, error. Monte Carlo: wrong explanation of infeasibility, optimistic conditioning, tornado grade

**Where**
- §4.3, p.13 (typ 750): "51% of draws are feasible: combinations of high titer and short production time break the limits".
- Fig. 5; tornado bar 1.

**Comment.** I reproduced the industry-BLG draws exactly (seed 1, n = 400: 203 feasible).
- Of the 197 infeasible draws, **193 fail the minimum-fill limit** and 4 raise errors.
- They are driven by high cell density (mean 111.7 against 83.2 g/L) and production-phase growth (0.0091 against 0.0049 per h).
- Their production phases are *longer* (82.0 against 76.5 h), and titer barely differs (43.0 against 41.3 g/L).
- Infeasible draws cost more: median $26.9 against $24.2. Over all finite draws, p10/p50/p90 are $19.8/$25.8/$33.8, against the reported $18.8/$24.2/$32.1.
- Academic BLG sits at the 1.6th percentile because the base range for cell density (40–150 g/L) is applied around the scenario's 50 g/L. 149 of those draws are infeasible, 145 on the fill limit.
- The Monte Carlo does not sample the fill limit, the q_p ceiling, the fixed-cost rates or the capital convention.
- Tornado bar 1 (titer 24–60 g/L) is graded B. Its range is GFI survey data (grade C) plus an unsourced 60 g/L; GFI's public-model range tops out at 54.

**Suggested fix**
- "Half the draws cannot be built, almost all because high cell densities and production-phase growth need so much feed that the batch would start below 30% full. Those draws cost more, so feasible-only percentiles understate the median by about $1.6."
- Grade the titer bar C, and source or drop the 60 g/L end.

### SC-9: minor, judgment call. Incumbent price benchmarks

**Where**
- §1 (typ 247), §4.2 (typ 687–697), Summary item 4 (typ 174–176).
- §5.3 (typ 1061–1067) and memo bullets 2–3.

**Comment**
- **(a) Protein fraction.** Whey is converted to $/kg protein at 0.80, the minimum for HS 3502.20 (WPC80 and WPI mixed). The band's own graded range is 0.76–0.88.
  - At 0.85 the band becomes $8.1–16.8, and "9 of 21" export prices above the design-report benchmark becomes 7.
  - At 0.88 it becomes 5.
  - The 9 is also knife-edge: EU 2017 is $12.068 against a benchmark of $12.072.
- **(b) Egg white is not always dearer than whey.** "Egg white is dearer than whey" and "whey is the hardest price to beat" do not hold every year.
  - Dried egg white was cheaper than the average whey price in 5 of 11 years, including 2024 ($11.17 against $12.87) and 2025 ($9.74 against $15.53).
  - In 2025 the industry benchmark BLG was 1.2–1.7× whey, while OVA was 2.3× egg white.
  - The egg band also silently excludes US trade data at $3–4/kg product, which prices.yaml marks low-confidence.
- **(c) "Spike years like 2026".** The 2026 value is a narrative midpoint from domestic USDA reports; prices.yaml says it is "not a formal price series… do not use as a steady-state price". No year in 2015–2025 exceeded $17.8/kg protein, so the plural "years" is unsupported.

**Suggested fix**
- Show the band at protein fractions of 0.80–0.88.
- "OVA sits closer to parity over 2015–2025 mainly because of egg-white price peaks (2015, 2022–23); in 2024–25 dried egg white was cheaper than whey."
- Drop the superlatives.
- Say "in a spike year such as 2026".

### SC-10: minor, error and framing. Milk and egg equivalents; the explorer states the bias backwards

**Where.** Explorer (`build_explorer.py:261` → `explorer.html:206`); §4.8 (typ 934–958).

**Comment**
- **(a) Reversed statement.** The explorer says "This flatters milk and eggs as competitors: fat, lactose and yolk carry part of their price". Charging the whole price of milk or eggs to their protein makes them look dearer per gram, so it flatters PF. The report correctly calls these "upper bounds".
- **(b) The egg bound is very loose.** It is 1.6–8.8× the dried-egg-white price per kg protein in the same year (2025: $85.5 against $9.74). So "$0.107 against $0.311 per egg" reads like parity when it is not. The same white bought as dried egg white cost $0.035–0.077.
- **(c) Whey share mixes years.** "9%–25% of the farm milk price" pairs extreme years from each series. Matching years gives 11–21%, and that is still at WPC80/WPI prices, which include concentration and drying.

**Suggested fix**
- Explorer: "This flatters PF."
- Add the dried-egg-white cost per egg ($0.035–0.077) next to $0.107.
- Use the year-matched 11–21%.

### SC-11: minor, error. The cost bridge costs designs the report calls infeasible

**Where.** Fig. 3 and §4.3, p.11 (typ 704–715), against §2.3 (typ 391): designs above 40 mg/g/h are "never costed as if it worked".

**Comment**
- JSON `bridge` flags the start and the next three bars "specific productivity 117.3 > 40 mg/g/h" (117.9 at the host step).
- The +$7.8, +$1.7 and −$0.2 steps are therefore computed on infeasible designs, and Fig. 3 does not flag them.
- This also shows that NREL's cellulase design, the one industrial design among the anchors, implies about 3× the cap. That is relevant to SC-2.

**Suggested fix.** Flag those bars (†) or start from a q_p-capped NREL case.

### SC-12: minor, scoring. Prior 2 is scored against an outcome set by a later judgment

**Where.** §7 Table 10 (typ 1142–1144).

**Comment**
- P(floor < $10) = 0.65 is scored "yes", Brier 0.12 / 0.12.
- But the outcome depends on the q_p ceiling chosen during the audit (R7-C2, grade D), in a scenario redefined after the prior (R8-m4).
- At a 10 mg/g/h ceiling the floor is $11.5 ("no", Brier 0.42).
- BLG and OVA are one event, scored twice.

**Suggested fix.** Score it as conditional ("yes if the secretion ceiling is at least about 15 mg/g/h") or as unresolvable, and count it once.

### SC-13: editorial. Wording and consistency
1. "Several times" (typ 682; memo typ 41) understates the gap: BLG at $64 is 3.6–7.4× whey, and OVA at $390 is 18–40× egg white.
2. "A hundred times the price of whey" (typ 965–966): the reported range is 11–170×, typically 40–60×.
3. Memo "45–63 g/L, near the ceiling" (typ 91): that is 55–97% of the ceiling, and near it only at 96–120 h.
4. §5.4 "Cheaper capital is the biggest single lever" mixes two changes. A 20-year recovery alone cuts $4.4; 4% alone cuts $2.1, about the same as US glucose ($2.2).
5. §4.7 siting effects sum to $4.8 against a $4.1 gap. The missing item is EU spent-cell disposal, which is $0.65/kg cheaper ($158/t against $343/t); add it.
6. §2.7 omits the physical limit's 8 h turnaround and 90% purity.
7. The withdrawn "O₂ wall" wording survives in:
   - the SI headers "feasible (O2/heat)" and "O2/heat ceiling" (`build_si_workbook.py:158,166–168`);
   - README line 58 ("O2 wall").
8. Fig. 2 labels Beck 2025 (3.7 g/L, intracellular E. coli) "best published OVA", while Table 1 uses 2 g/L. Say "best public secreted OVA titer".
9. §5.2 "conservative central": conservative and central are two different claims; pick one.

---

## Claims I checked and found supported
- **Base case.** $29.37 / $29.45 per kg, and $16.06 / $16.11 with design-report capital. My independent run reproduces the base. The other base-case figures in the text also match JSON:
  - capital-related share 68%, glucose 14%;
  - 33 × 200 m³ fermenters, 112 h cycle, 4,299 kg per batch;
  - overall yield 0.098 g/g, 122 staff;
  - cost of production $25.5 and discounted-cash-flow price $28.5.
- **Scenarios.** Academic $64 / $164 / $390; industry $21.9 / $22.0 ($12.1 design-report).
- **Incumbent bands.** Whey $8.65–17.80 and egg white $9.74–21.25, recomputed from the CSVs and CPI. 9 of 21 annual prices are at or above $12.07; none are above $21.9. The 2026 spot is $34.4.
- **Required frontier.** Every Table 6 cell and every ceiling matches JSON. "$10/kg is not reachable at the base cell density" holds even at 12–30 h (minimum $10.41).
- **Table 7 values.** They match JSON, including 81/74/65 g/L at 36/72/120 h.
- **Physical limit, as defined.** $6.1 / $6.2 ($3.6 / $3.6); 80 g/L cells, 72 h, 119 g/L; the binding list; the q_p 20/120 and 50 g/L solubility sensitivities; capital at 67% of the floor.
- **Tornado text.** Top 7 ranges, yield $0.3 (rank 30), vessel size $2.3, cost exponent $0.1, capital convention $9.8.
- **Monte Carlo numbers.** All reproduced exactly; only the explanation is wrong (SC-8).
- **Siting and policy.** $4.1, $2.2, $0.8, $1.8, wages ≈ 0, $6.7, $2.1; scale $15.5 and $1.3.
- **Milk and egg composition and costs.**
  - 33.7 / 3.3 g per litre and 3.64 / 1.96 g per egg;
  - $0.99 against $0.48 and $1.07; $0.107 against $0.311;
  - $14–19 and $26–86 per kg protein, break-evens at 70 and 34 g/L;
  - the 6.6 g whey protein figure, and 35 ÷ 0.6 ≈ 58 animal-years.
- **Lactoferrin.** $216 / $134, $531 / $283, $147 / $84, $364 at 125 resin cycles, the scale series, and "below most reported prices". The last holds even using Intelligen's $292.
- **Sources checked against the files on disk.**
  - Calibration table.
  - NREL's "47%" (Genencor/Novozymes $0.50 against $0.34 per gallon, NREL 2011 p.40).
  - Humbird's "200 mol O₂/m³-h is about as high as it gets", 5,000 W/m³ and ~2 vvm.
  - Humbird's 4% maintenance and 5% insurance.
  - GFI Europe's $24–33/kg (P1) and $12/kg (α-lactalbumin).
  - GRN 1219 / 1284 "no questions".
- **Memo** "capital is the largest cost item in every scenario": true in all 36 cases in JSON.
- **Explorer grid** matches JSON at all 5 points I checked, and figure convention names are consistent.
- **Academic titer choices** are the best public *secreted* values and are flagged, so I found no cherry-picking there.
- **Grade-E guesses** do not drive results; the largest is the downstream area factor at $0.52 (rank 20).
- **Consistency versus validation.** The report keeps "consistency, not validation" for anchors 2–4. Anchor 1's "reality" label overstates (SC-3).
- **Section 7 arithmetic** for priors 1a, 1b and 4 is correct; 10 titer rows are unverified and 8 parameters are graded E, as stated.

## Answers to docs/REVIEW.md section C

**C1. Is the "physical limit" meaningful?** Not as a "physical limit" or a "floor". Its binding constraints are:
- a grade-D secretion ceiling of 40 mg/g/h, about 8× any K. phaffii measurement;
- a grade-D O₂ cap of 250 mol/m³/h;
- a design choice (the 30% minimum fill).

Its yield is at or above the corrected energetic ceiling, and about $2.3 of it comes from engineering and scale levers. The floor tracks the q_p assumption: $16.7 at 5, $11.5 at 10, $8.2 at 20, $6.1 at 40 and $4.6 at 120 mg/g/h. It is meaningful only as a conditional best case, presented with that curve (SC-2). It is not a lower bound either (SC-4).

**C2. Is whey the right benchmark?** It is the right *price* benchmark for a WPC80/WPI-type ingredient, with three caveats:
- The 0.80 protein fraction lifts the band by up to 10% (SC-9a).
- Whey is a by-product with supply fixed by cheese demand, so PF displacement at scale would push its price down toward the cost of concentrating whey protein. WPC34 protein traded at $6.1–12.2/kg protein (2025$) in `wpc34_us_dmn.csv`, so parity at historical WPC80/WPI prices is not durable parity.
- Egg white is not reliably dearer than whey (SC-9b).

I agree it is the wrong *impact* benchmark. Year-matched, whey protein is 11–21% of farm-milk value even at processed-ingredient prices, so egg white is the stronger welfare lever.

**C3. Where does the analysis still overclaim?**
- $10/kg "needs every lever": it needs about 8× q_p (SC-1).
- "Physical floor" and "every biological parameter at its best measured or theoretical value" (SC-2).
- "Price-anchored… the only convention tied to a real product price" (SC-3).
- "Published costs are 2.4–2.5× lower" and "most published PF studies" (SC-5).
- Lactoferrin "can already compete", with the published comparator omitted (SC-6).
- "Industry-level titers", which are really cost-model assumptions, and Table 8 costs at q_p ≈ 40 (SC-7).
- "Whey is the hardest price to beat" (SC-9).
- The explorer's reversed equivalents caveat (SC-10).

**C4. What real cost data could test the model?**
- Market prices of secreted recombinant proteins sold at commodity scale, such as industrial enzymes, feed phytase and fermentation-produced chymosin. These include secretion, clarification, UF and drying, so they anchor far better than baker's yeast. NREL's Genencor/Novozymes quote on disk is one such point.
- Contract-fermentation tolling fees per m³-hour. These embed capital recovery, maintenance, insurance and labour: exactly the disputed half of the convention gap.
- Disclosed capital, staffing and utilities for built PF or enzyme plants, from company filings, grant or loan award documents and local permit or tax-abatement filings (for example the Liberation Labs Richmond plant cited in §5.5).
- Dairy or egg processors' disclosed capital for UF, chromatography and spray-drying plants, to test the downstream and building factors.
- Measured fed-batch runs reporting titer, q_p and sugar yield together. Given SC-1 and SC-2, a demonstrated q_p above 10 mg/g/h in K. phaffii for BLG or OVA is the single number that would move the conclusions most.

**What I could not check.** Intelligen's lactoferrin cost breakdown (not on disk), NREL-style factors applied to the yeast port, and the 2026 market-news figures (external). Where these affect a comment, I give my confidence in that comment.
