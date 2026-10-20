# Audit R13: compiled v4 report (pf_tea_report.pdf, memo.pdf), 2026-10-02

I spot-checked more than 60 numbers against results/analyses.json, and they all match. Albumin: base 215.48, light 185.23, aseptic 231.40, pioneer 234.38, EU +10.08, industry 205.23/177.49, academic 423.66/345.02 (8.74 g/L), Zhu 2018 514.1 (4.43 g/L), patent 997.1, capture-only 143.17, UF/DF 34.31, methanol +6.00. Resin cases: 125 cycles 940.9; $100/L 114.3; $2,000/L 281.5; loading 50 g/L 196.4; capture recovery 40%/86% 269.7/169.6. Scale 308/215/203; physical limit 171.6/153.0; physical limit at 2.1 mg/g/h 210.6; Monte Carlo 265 (171–377, 43%); ρ 0.60/−0.49/−0.35; tornado 205–931, 104–271, 205–327. Table 5 albumin column: resin $103.6, TCI $311M, 13 × 100 m³, recovery 50%, 18.5 kg glucose. All 21 cells of Table 15 (g/kg × $/kg / 1000) are right. Methanol: ceiling 0.531, yield 0.428, biomass yield 0.47; 19 kg made (38.07 per kg sold × 0.497 recovery); 58/19 = 3.1×. Pioneer BLG 24.43, lactoferrin 192.45. Lactoferrin 8 × 100 m³. The albumin ceiling at 72 h is 69.5 g/L and costs $194.5 there, so "none of its targets" holds; "10× BLG", "8×", "1.0–1.2×" and "all four below" also hold.

The albumin physics is sound. Resin ≈ $59 on the capture column (1/(0.56×0.94) kg loaded per kg sold × $31.25/kg loaded) plus ≈ $44 on the polish column ($41.7/kg loaded × 1.06) = $104. That cost does not depend on titer. Fitting the rest as F/titer gives F ≈ 1,050 $·g/L/kg from the 30→42 g/L drop. At 8.74 g/L that predicts ≈ $300, plus methanol (≈ $35) and the 192 h batch, which makes $424 plausible.

## HIGH
**H1. Figure 3, albumin panel: the markers sit at supernatant titers.** The "best public rHSA (Zhu 2021…)" line is drawn at 17.47 g/L and Zhu 2018 at 8.86 g/L. The model's basis is whole broth: 8.74 and 4.43 g/L (JSON academic/alb titer 8.74). Read off the curve at the marker, a reader gets about $250, against $424 in Table 1. The curves are also glucose at 48–120 h, while the academic case is methanol at 192 h. The figure footer also says "200 m3 fermenters", but lactoferrin and albumin use 100 m³.
Fix: place the markers at 8.74 and 4.43 with the label "(whole broth; 17.47 g/L of supernatant)". Add "academic case on methanol, 192 h: $424 (Table 1)". Change the footer to "200 m³ fermenters (lactoferrin and albumin 100 m³)".

**H2. Wording left from when albumin had one column.** In each place below, replace the old text with the new:
- Summary: "albumin on the base design point with the cation-exchange capture of the industrial recombinant-albumin process" → "…with the two-column train of the industrial process (cation-exchange capture, anion-exchange polish)".
- Summary: "three downstream routes (membranes, isoelectric precipitation and cation exchange)" → "…and ion exchange".
- Figure 2 caption: "lactoferrin and albumin add cation exchange before it" → "lactoferrin adds cation exchange before it, albumin cation then anion exchange".
- Table 5 caption: "lactoferrin and albumin: cation exchange" → "lactoferrin: cation exchange; albumin: cation exchange then anion-exchange polish".
- Q3: "out of reach of any titer with cation exchange" → "with column purification".
- Limitations: "Chromatography is one capture column, for lactoferrin and albumin" → "one capture column for lactoferrin; capture plus an anion-exchange polish for albumin".
- Q8 answer "with its column" and Q3 answer "the column's cost" → "columns".

**H3. Typst swallows a semicolon written straight after `#func(...)`.** This happens at report.typ lines 1251, 1790 and 1796, and memo.typ line 91. The PDF text shows the damage:
- "loading 50 instead of 40 g/L $196 the capture recovery…"
- "UF/DF alone $34.3 but albumin…"
- "+$0.9 lactoferrin with cation exchange"
- memo: "cheap resin $114 membranes alone, $34.3, reach only 77% albumin"

Fix: write `\;` (as line 766 already does). The memo bullet also needs rewording: "capture alone would cost $143 and a $100/L resin $114; membranes alone ($34.3) reach only 77% albumin."

**H4. The polish parameters have no evidence entry.** In base.yaml, `polish_dbc_g_L` and `polish_recovery` cite `albumin.yaml hsa_delta_aex_polish`. That key does not exist: data/evidence/albumin.yaml has no AEX, polish or "110%" entry at all. This breaks the "every number traces to a source" rule. Separately, products.yaml `alb.plant.spec` still says a "≥96% [spec] is taken to need the capture step only". Fix: add the evidence entry with the verbatim US 6,638,740 quotes, and correct the note.

## MEDIUM
**M1. The "favourable end" claim is wrong for recovery.** Q8 says: "the base sits at the favourable end of resin life, recovery and purification". But capture recovery 0.56 is the midpoint of 46–66%, and the tested range is 0.40–0.86. Change to "at the favourable end of resin life and purification, and mid-range on recovery".

**M2. Tornado text (Section 4.3).**
- "Their own downstream inputs rank lower" is false for lactoferrin and albumin: the resin inputs rank 1 for both. Change to "For β-casein its own downstream input ranks lower…; for lactoferrin and albumin the column inputs lead".
- Resin life is graded A (Pires 2025, whey lactoferrin), and Figure 6 colours albumin's top bar A. Yet the text calls it "the softest number… borrowed". For albumin it is an analogy: override the grade to D in products.yaml.
- In Figure 6, "polish_dbc_g_L" is an unlabelled raw key, and the values "1e+03", "2e+03" and "3e+03" need formatting.

**M3. Section 4.7 (Q6, scale) disagrees with Table 1.**
- "Lactoferrin… industry benchmark costs $98 at 250 t/yr", while Tables 1 and 6 give $106 at the same 250 t/yr. The scale curve re-sizes the vessels, while the table keeps 2 × 100 m³. Add "(the scale curve re-sizes vessels; $106 in Table 1 keeps the base plant's 100 m³)".
- Albumin is quoted as "base case… $308/$215/$203", but Figure 10 plots industry benchmarks ($294/$205/$192). Quote the plotted series, or say which one the text uses.

**M4. Pioneer factor (please check this derivation).** RAND gives the mean of estimate/actual as 0.78 (SD 0.194). Taking 1/0.78 is not the mean cost growth, because E[1/r] > 1/E[r] (Jensen's inequality). My delta-method estimate is (1/0.78)(1 + (0.194/0.78)²) ≈ 1.36. "Conservative" is therefore not established. Also, "all capital × 1.28" is not what the model does: the resin first fill is not scaled (albumin TCI ×1.258, lactoferrin ×1.278).
Fix: "1/0.78 = 1.28, the reciprocal of RAND's mean ratio (the mean of the reciprocals would be about 1.36); resin first fill unscaled". Drop "conservative".

**M5. The methanol-maintenance "independent check" doesn't check what it claims.** Tomàs-Gamisans' non-growth ATP demand is fitted in growing chemostats. So its 0.0048 g/g/h parallels Dietzsch's unscaled 0.016, not the ×0.31 near-zero-growth value. That it lands on 0.0050 suggests 0.016 is high; it does not confirm the scaling. Rewrite: "Methanol chemostats give a lower non-growth demand, 0.0048 g/g/h (…), which supports the scaled value, though for a different reason."

**M6. Monte Carlo and Spearman.**
- `polish_dbc_g_L` and `polish_recovery` are not sampled: they are missing from input_means, but the tornado varies them.
- There are about 170–200 feasible draws, so the noise floor for ρ is about 0.075. The second and third entries (0.26–0.37) cannot be ordered, and albumin's yield has ρ = +0.12 with the wrong sign.
- Add: "|ρ| < 0.15 is indistinguishable from zero."
- "22 on no plant (model error)" reads like a bug. Explain what it means, or rename it.

**M7. Figure 12 (fig9_routes).**
- Capture-only is shown at "96% of dry matter" with no caveat. Relabel it "capture only (96% assumed; optimistic)".
- β-casein shows 92% there but 93% in Table 5 and the Q8 answer.

## LOW
- 5.5: "without… a $1,000/L resin": the base resin is $1,250/L.
- Rounding: physical-limit albumin is "$171.6 and $153.0" in the Q4 text and answer, but $172/$153 in the tables.
- "the polish column adds more" → "the polish column adds $44 (30 g/L loading)".
- Overall recovery is 0.4975, so "fermented and clarified almost twice" → "twice".
- "0.576 for albumin (0.582 and 0.590 counting peptide bonds alone…)" reads as albumin's figures; they are BLG's and OVA's. Write "(BLG 0.582, OVA 0.590…)".
- "a quarter of the lowest of GFI's… scenarios": 1/3.6 = 28%, so "over a quarter".
- Summary: "bulk bovine serum albumin at $40–$70" is our reading of GFI's "high-value albumins… public trade databases". Add "(our reading)".
- Table 15: "$2064.04" → "$2,064".
- Section 4.2: "inside the band… and inside it with design-report capital" → "inside the band with either capital convention".
- Figure 8: the lactoferrin legend covers the $400/kg lines.
- References are out of alphabetical order:
  - CE Delft should come before Chezan.
  - Iaria should come before InVitria.
  - Kim should come before Kleerebezem.
  - Li should come before Liu.
  - Tomàs-Gamisans should come after Tijhuis, not after Wang.
  - Yver should come before Zhu.
  - In the text, "Shemesh et al. 2024" vs "Shemesh and Fishman 2024": use one form.
  - Every v4 source is in the list: Zhu 2018/2021, Delta, Dietzsch, Tomàs-Gamisans, Kleerebezem, Merrow, GFI 2023/2026, CE Delft, FDA Wildtype, InVitria, Sartorius, Shemesh.
  - "abstract read" is attached to Zhu 2018 only, which is correct.
- docs/AUDIT.md v4 row G6 still reads "Not done… capture-only" (superseded by R12-H1). Add a pointer.

## Clarity (rewrites)
- Section 4.8: "the base case is not a negligible input, and GFI's $10/kg would make it one" → "at the base cost albumin adds $2–10 per kg of meat, a material share of a few-dollar product; at GFI's $10/kg it would add $0.09–0.47, which is negligible."
- Section 2.2, the methanol "carbon" bullet → "Methanol carries more electrons per carbon (γ = 6) than protein (≈ 4.1), so making protein from it leaves surplus electrons, not surplus carbon. All product carbon comes from methanol and the extra electrons go to O₂; yeasts do not use them to fix CO₂."
- Section 2.4: "on the same resin and recipe" → "at the capture column's resin price, resin life and buffer volumes".
- Section 2.5: "over 50, 100, 150, 200 m³ vessels, up to 200 m³ (the base vessel…)" → "over 50, 100, 150 and 200 m³ vessels (200 m³ is the base…)".
- Summary item 6: "a polymeric resin at $100/L $114" → "a $100/L polymeric resin on both columns $114".
