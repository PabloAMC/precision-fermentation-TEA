# Audit R14: α-lactalbumin, rennet-cheese casein, heme (data and logic)

Scope: only the v4-continued additions (PLAN.md top entry). Read-only. Scratch runs:
`scratchpad/cheese.py`, `scratchpad/misc.py`, `scratchpad/formula.py`, `scratchpad/qcheck.py`, `scratchpad/qfuzzy.py`
(no repo file touched, run_analyses/explorer_grid not run).

Verified and correct (no action): the four elemental formulas and masses (recomputed from the sequences:
alac C626H958N162O196S9 14,178.0; cas1 C1035H1587N265O317S5 22,974.9; kap C849H1321N223O262S4 18,972.4;
legh C702H1096N176O212 15,393.5), each sequence equal to the UniProt mature chain on disk, and the kappa
disulfide at mature 11–88 (precursor 32–109). These quotes or numbers match the local full texts:
- Wang 2025: 0.60 g/L (abstract l.27–28, Fig. 5E l.723) and "sustained for over 90 h" (l.415–416).
- Viaene 1991: 0.5 and 2 mg/L (l.343–346), and the pH 7 buffering (l.458).
- Antuma 2025: 162.3/127.4/123.8 Pa; Table 1 shares 25.5–11.6% κ.
- New Culture Ex. 9: 21/7, 22.4/5.6 and 23.4/4.6 mg/mL, i.e. 3:1–5:1 (the 5:1 actual is 16.4%, nominal 16.7%).
- Redbiotec WO2023002061: "about 0.25 g/L" (patents/WO2023002061A2.txt l.808).
- Panchanawaporn 2026: 4.14 ± 0.12 mg/L by ELISA.
- Chen 2025: "6.0 g/L in 102 h". Shao 2022: Table 2, 3.5 g/L and 93%.
- 21 CFR 73.520(c) 0.8%. FSANZ A1186 0.45%/0.25%.
- GRN 737 Table 1 (LegH 6.28–6.95%, solids 12.55–18.44%). GRN 763 (≥95% protein, ≥90% α-lac).
- GFI Europe appendix (462 / 31,828 / 15 / 24 and 462 / 3,740 / 123 / 100). P1 chart $32/78/122 (l.576–590).

Evidence schema: every field the README requires is present in all 118 new entries, all grades are in A–E,
and no keys are duplicated. A trigram check of quotes against the local texts gave ≥0.7 for every fulltext or
abstract quote; the lower scores come from two-column PDF interleaving, and the ones I spot-checked were verbatim.
The html-only quotes (FMI, 21st.BIO, Arla, Krackeler, CIRS) have no local copy, so they are unverifiable.

## HIGH

**H1. κ-casein runs alone on the pH-4.5 acid route. Its own evidence entry says this route is implausible
for κ on its own.**
- What: cheese.yaml:27–30 runs kap on `plant.spec: acid`, in its own strain and plant, with recovery 0.78.
  The entry it cites, casein.yaml:1462–1491 (`kappa_acid_route_feasibility`, D), says otherwise. κ is
  calcium-insensitive. Unphosphorylated κ has a computed pI of 5.85 and carries net charge +4.4 at pH 4.6.
  A recombinant κ "would likely need precipitation at pH ~5.5-6, NOT 4.5, if it precipitates cleanly at
  all" (l.1482). The acid route is "plausible for kappa only as part of an alpha-s1 + kappa
  co-precipitate". A stand-alone κ "should be modelled with a chromatographic capture … or left as a
  required-titer analysis". The 0.78 recovery is that entry's "at best" figure with grade E. It is not a
  recovery for κ alone. The acid route also holds at 90 °C (base.yaml:218), and κ is the casein that
  fibrillates and aggregates on heating.
- Why it matters: every κ cost in s_cheese, and so the "κ titer for a blend within 10%", rests on a unit
  operation the evidence calls unsupported. Run at s = 0.15 and 1.5 kt/yr, κ costs $35.2/kg at 30 g/L,
  against α-s1 at $22.2/kg at the same titer.
- Fix: choose one of the following and say which in cheese.yaml.
  - (a) Cost the κ plant on the `cex` route with lactoferrin's column leaves, graded D. Positive charge
    below pH 5.8 is that entry's own suggestion.
  - (b) Model the blend as two fermentation trains feeding one shared acid line (co-precipitation). This
    needs code.
  - (c) Keep the acid route but call every κ cost a lower bound, and show recovery 0.5–0.78 as a sweep.
  - In every case, add a sentence to the cheese.yaml header and to the report saying κ on this route is
    a judgment (E), not an analogy.

**H2. The α-lac price band is per kg of ingredient, not per kg of α-lac. The $15 low end and the $15
required target are understated about 1.7×.**
- What: alac.yaml:830 says "Per kg of the molecule, so comparable with the model's $/kg target protein".
  GFI Europe's own cost-in-use table (references/text/GFIEurope_2025_…txt l.1028–1066, p.33) contradicts
  this. It prices the conventional grades at 60% purity ($15), 80% ($29) and 95% ($123), and its arithmetic
  works only per kg of ingredient:
  - General food: 3.6% / 0.60 = 60 g/kg ("61"), and 0.061 × $15 = $0.9 (as printed). Per kg of molecule it
    would be 0.036 × 15 = $0.54.
  - Sports nutrition: 25% / 0.80 = 313 g, and 0.313 × $29 = $9.1 (printed $9).
  - So $15/kg is for a ~60%-α-lac ingredient, which is $25/kg of α-lac. $123/kg at 95% is $129/kg of α-lac.
  - The column header says "USD/kg molecule", but the numbers don't follow it.
  - The appendix rows carry the same $462 M market value at two volumes, so 31,828 × 15 and 3,740 × 123
    are two cuts of one number, not independent observations. alac.yaml:493 notices this.
- Effect: benchmarks.yaml:149 `alac: [15, 60, 120]` sets a $15 target. That is ~$25/kg on a per-α-lac
  basis, so the required titer at the bottom target is overstated. The band's low end against the model's
  $33.8/kg base (my run) also looks worse than it is.
- Fix:
  - Restate `alac_price_points_gfieurope2025` as low 25, high 129, unit "US$/kg α-lac (GFI's $15 at 60%
    and $123 at 95% purity, ingredient basis, divided by purity; derived)", with the p.33 arithmetic in
    the note.
  - Set required_targets to [25, 60, 130], or keep 15 but call it "per kg of 60% ingredient".
  - Mark FMI's $31–86 as basis unknown (already noted) and keep it only as context, or drop it from the band.

## MEDIUM

**M1. The κ-share range misreads Antuma 2025's molar ratios and is graded A for a phosphorylated system.**
- What: cheese.yaml:10–11 and casein.yaml:1385 say firmness "levelled off below a calcium-sensitive:kappa
  molar ratio of 2.7–4.0, i.e. near 15–19% kappa by mass". Antuma Table 1 pairs the ratios with samples:
  4.0 = α:κ 71:19, 2.7 = 61:26, 5.3 = 75:15, 7.3 = 80:12.
- So the plateau runs from 19% to 26% κ, not 15–19%. Firmness rose from 127.4 Pa at 12% κ to 162.3 Pa at 19%.
- The caseins were dairy and phosphorylated. For unphosphorylated recombinant blends, the only evidence is
  New Culture's 16.7–25% (grade B). Antuma 2023 found that dephosphorylated casein gives 6% of native curd
  firmness.
- Fix: kappa_share value 0.19, low 0.167, high 0.25, grade B, sourced to New Culture Ex. 9 for the
  recombinant range. Cite Antuma for the firmness maximum at ~19% and milk's 12% as context, and correct
  the "15–19%" text in both files.
- Effect: small on the needed κ titer (26–29 g/L across s; see M3). At low κ titers the blend cost scales
  with s.

**M2. One kappa grid point is computed at the wrong titer and comes back infeasible.**
- What: cheese.yaml:13 puts Panchanawaporn's 0.00414 g/L on the kappa grid. pf_ferm.py:553 brackets q_p at
  ≥1e-6 g/g/h. At X ≈ 107 g/L for 72 h, that floor alone gives ~0.0074 g/L.
- The run therefore simulates 0.00743 g/L (verified: `design['titer']` = 0.00743, q_p = 0.001 mg/g/h), sets
  the flag "titer 0.00414 g/L not reachable", and returns $98,411/kg with 28,013 vessels.
- That is about 1.8× too cheap for the titer it is labelled with: about $175k/kg if cost ∝ 1/titer from the
  0.25 g/L point.
- s_cheese stores it with no feasibility filter (run_analyses.py:684–690). The same floor would hit any
  titer below ~0.007 g/L, for example Viaene's 0.002 g/L.
- Fix: lower the q_p bracket to 1e-9 (a code change, with a test that 0.004 g/L is reachable). Otherwise,
  drop the point and quote the scaled estimate. Either way, filter infeasible points before interpolating
  or reporting.

**M3. The s_cheese interpolation is correct but fragile, and its baseline is inconsistent.**
- (i) The algebra is right. Blend ≤ 1.1·c_as1 ⇔ c_kap ≤ c_as1(1 + 0.1/s) (run_analyses.py:688).
  Interpolating in log-log with reversed arrays is right while cost falls monotonically with titer. My
  grid run confirms that for kap (s = 0.15: 2,890 → 28.0 $/kg from 0.25 → 42 g/L).
- (ii) Monotonicity is assumed, not checked. Whole-vessel rounding already makes cost non-monotonic in
  scale: α-s1 costs $22.16 at 8.5 kt but $22.43 at 8.8 kt. np.interp silently returns garbage on a
  non-monotone xp, so add `assert np.all(np.diff(ck) < 0)` on the feasible points.
- (iii) c_as1 always comes from the α-s1 plant at tot·(1 − s0) = 8.5 kt (l.678, 683). The s_lo and s_hi
  blends should use tot·(1 − s) for each s, and "α-s1 alone" should arguably be the 10 kt plant (computed
  as "base/10kt", $22.06). The effect is ≤1–2%; fix it for consistency.
- (iv) The industry case hard-codes `{"strain.titer_g_L": 42.0}` (l.677) instead of reading
  industry.yaml `cas` (42, grade C). That breaks the "never hardcode" rule. Read it from the scenario file.
- Result: s = 0.12 needs ~26 g/L, s = 0.15 ~28 g/L and s = 0.19 ~29 g/L, i.e. essentially α-s1's own
  30 g/L design titer (see D2).

**M4. Supernatant titers are taken as whole broth for α-lac and LegH. Albumin was corrected for this.**
- What: academic.yaml:84 (Wang, 0.60 g/L supernatant), heme.yaml:13 (Chen, 6.0 g/L supernatant) and
  heme.yaml:19 (Shao, 3.5 g/L supernatant) all enter as whole-broth titers. Audit R12 corrected albumin to
  whole broth (factor 0.50, benchmarks.yaml albumin marker).
- The model's own cell-volume convention (plant.py: V_wc = X/(1000·0.3)) gives a wet-cell fraction of 0.36
  at 107 g/L. Supernatant × 0.64 then equals whole broth.
- Effect (my runs): α-lac academic $1,191 → $1,858/kg. LegH Chen at 1 kt/yr $116 → $173/kg.
- Fix: either apply (1 − X/300) with the stated cell density, graded D, or state in each scenario comment
  and in the report that these are optimistic by about 1.5× for this reason. The α-lac evidence's "do not
  stack" argument (proteolysis underestimate) is not a number, and albumin was not treated that way.

**M5. The Impossible Burger price in the heme scenario comes from an entry with quote: null and unverified
pages.**
- What: heme.yaml:28 `analogue_usd_kg` 19.93–29.36 (C) comes from `impossible_burger_retail_price_us_2026`
  (heme.yaml evidence l.623). That entry has quote: null, and the retailer pages were "blocked … NOT
  verified". The README says that without a quote "the entry is not usable".
- Fix: verify one retailer page by hand and add the quote, or drop the analogue price from the scenario and
  keep beef (BLS, A) as the only comparator.

**M6. The heme note is not a bound in either direction, but it is called one.**
- What: heme.yaml:1–5 says "a bound" and "omits lysis and overstates drying". Those errors have opposite
  signs. The secreted titers (3.5–6 g/L supernatant) are also not the commercial intracellular ones
  (K. marxianus 10.1 g/L intracellular).
- Fix: call it "an estimate on the best published secreted processes; sign of the error unknown". In the
  report, list the omissions with their signs: lysis and debris removal (+), drying a product sold frozen
  (−), supernatant basis (+, M4), unknown heme loading for Chen (+, per functional protein).

## LOW

- **L1. The α-lac purity derivation is wrong.**
  - products.yaml:106 says "protein ≥95%, α-lac ≥90% of protein, i.e. ~0.90 of dry matter". That gives
    0.855; alac.yaml's recommendation uses 0.95 × 0.95 instead.
  - Cost effect: nil (0.855 → $33.84, 0.90 → $33.81).
  - Fix: write "0.855 at the spec minimum; 0.90 at the typical 95% α-lac (90–96%)".
- **L2. LegH purity 0.45 slightly exceeds its source.** The mapping onto `dsp.concentrate_target_frac_dry`
  is semantically right: plant.py:293 makes it the target's share of dry solids, used only for drying and
  powder mass. The five GRN 737 batches give a mean ratio of 43.0% (ratio of means 42.4%), not 0.45.
  Part of those solids is added NaCl and ascorbate. Cost effect <1% (0.45 → 0.90: $116.2 → $115.4).
  Fix: value 0.43, low 0.38, high 0.51.
- **L3. The hemin coverage in the Chen flag is an upper bound.** heme.yaml:16 and evidence l.890 say
  100 mg/L hemin "covers ~41%". Chen's 100 mg/L is per litre of methanol feed (Chen l.158), not of broth,
  so 41% holds only if ≥1 L of feed went in per L of broth. Fix: write "≤41%, likely much less".
- **L4. `unused_paths` hides cas1's own dryer leaf.** The leaves are matched by prefix (run_analyses.py:444
  uses startswith), so for key `cas1` the entry `dsp.dryer_feed_solids_cas` matches
  `dsp.dryer_feed_solids_cas1` (verified: True). No tornado runs for cas1 today. Fix: emit exact paths, or
  append a terminator and match on equality.
- **L5. cas1.yaml points to a missing file.** Lines 3 and 14 cite "data/evidence/casein2.yaml", which does
  not exist (it is .preview/casein2/casein2.yaml). Point to casein.yaml instead.
- **L6. Off-list products depend on their scenario file for the route.** `sc.base_params("kap")` alone falls
  back to base.yaml's `concentrate` route with a caseinate dryer leaf. The test covers only the scenario
  path. Fix: add a one-line guard, or say so in the docstring.
- **L7. Kappa grid titers come from other hosts.** The 0.25 g/L point is K. lactis on galactose in a shake
  flask (semi-quantitative Western, glycosylated κ). The 0.00414 g/L point is A. oryzae with ELISA. Both
  are costed as K. phaffii on glucose at 72 h. Fix: say so in cheese.yaml:13.
- **L8. The α-lac titer marker label omits the basis.** benchmarks.yaml (alac marker, Wang2025) has no
  factor and does not say "supernatant". Fix: add "(supernatant)" to the label, consistent with M4.
- **L9. Several quotes are over 40 words**, against the README limit: as1_acid_route_summary,
  plant_seed_casein_expression_nobell, alac_carbon_source_and_feed_rates_wang2025 and
  newculture_recombinant_as1_kappa_micelle_cheese.
- **L10. `scale_L` is inconsistent in the new titers.csv rows.** It is the working volume for Wang (0.9)
  and Deng 2022 (0.9) but the vessel size for Deng 2023 (3).
- **L11. The α-lac "isolate" alternative is the wrong high-purity route.** make_figures shows
  ammonium-sulfate precipitation, but GFI's high-purity route is one chromatography step (0.70 DSP yield).
  Fix: label it as the model's generic isolate route, not the high-purity grade.
- **L12. No tests cover the new analysis code.** Nothing tests the s_cheese algebra, the interpolation
  direction or tiny-titer reachability. Add one cheap unit test of the 10% threshold on a synthetic
  monotone curve.

## D. Framing that would mislead a reader

- **D1 (α-lac price basis).** See H2. Also, the model's α-lac is bovine but the academic titer is human
  α-lac, and it is set against a bovine dairy band. The scenario flags this; the report must too.
- **D2 (needed κ titer).** "κ titer for the blend within 10%" ≈ 26–29 g/L. That is about α-s1's own
  assumed 30 g/L design point, which no α-s1 has shown either: the best is 1.13 g/L, intracellular, in
  E. coli. Present it as "κ must reach roughly the α-s1 design titer on the same route, given the H1
  caveat". Do not present it as an absolute requirement. The 10% threshold is a design choice and should
  be labelled as one.
  - For scale: at Redbiotec's 0.25 g/L, the blend at s = 0.15 costs (0.85 × 22.2 + 0.15 × 2,890) ≈
    $452/kg, which is 20× α-s1 alone.
- **D3 (heme cost in use).** LegH at 0.45% × $116–269/kg comes to $0.5–1.2 per kg of analogue. That is an
  ex-works cost compared with retail beef ($15.26/kg). Label it as such. A per-functional-heme basis would
  divide by loading (Chen's loading is unknown).
