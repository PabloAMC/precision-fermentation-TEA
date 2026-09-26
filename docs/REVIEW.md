# Review (Phase F)

Phase F sends the assumptions and results to outside experts and answers every comment
(PLAN.md). This file is the packet, the question list and the comment log.

Status (2026-09-27): human review not started. Pablo contacts the reviewers; the drafts below are
ready to send. An AI pre-review (three simulated reviewers, clearly labelled as AI) has been run
so that the obvious objections are answered before anyone's time is spent; its comments and our
responses are in the log at the end.

## What to send

1. `report/pf_tea_report.pdf` (the analysis, about 30 pages; the Summary and Results sections
   Q1–Q8 are the core).
2. `report/memo.pdf` (one page).
3. `docs/explorer.html` (self-contained; opens in a browser).
4. `report/pf_tea_SI.xlsx` (every parameter with its source, all result tables, a live accounting
   sheet).
5. `docs/AUDIT.md` (what the internal audit found and changed) and `docs/VALIDATION.md` (the
   calibration record).
6. Repository access (private until release; invite the reviewer on GitHub, or send a zip).

## Questions by reviewer

Each question points to where the assumption lives, so a reviewer can answer "yes / no, because".

### A. Fermentation scientist (for example GFI's fermentation science team)

1. **Production-phase stoichiometry.** No measured BLG or OVA yield on sugar exists. We derive the
   product-reaction yield (0.465 g/g, 80% of the energetic ceiling) so that the model reproduces
   Intelligen's lumped expression-phase stoichiometry, with a measured low-growth maintenance of
   0.0044 g/g/h (Rebnegger 2024). Is the production-phase glucose use of a real *K. phaffii* PF
   process closer to this (effective yield ~0.28 g/g) or to chemostat-level maintenance (~0.11 g/g)?
   Report, Methods 2.2; `data/pf/base.yaml` `strain.Y_ps_g_g`, `hosts.kphaffii.m_s_prod_g_g_h`.
2. **Secretion ceiling.** We cap specific productivity at 40 mg protein/g cells/h (a judgment,
   grade D). It binds at the physical limit. What is the highest sustained q_p you have seen for a
   secreted food protein in yeast or fungi? Report, Results Q4.
3. **Cell density.** 107 g/L at the start of production (Intelligen's design, derived with a volume
   balance), 150 g/L maximum. Realistic for industrial *K. phaffii* on glucose?
4. **Minimum starting volume and feed concentration.** A batch may not start below 30% of the
   vessel (Intelligen's design), and glucose is fed at 50 wt%. Together these set the base titer
   ceiling (~74 g/L at 72 h): with a 20% start or a 65% feed it rises to ~125 g/L. What starting
   volume (impeller submergence) and feed concentration do you use at scale?
5. **OVA solubility.** We dropped Intelligen's 50 g/L "practical solubility" as a limit (OVA dissolves
   at 200 g/L in water; egg white is ultrafiltered to ~110 g/L OVA). Do you know of a lower limit at
   pH 5–6 in fermentation broth?
6. **Titers.** Are the public titers in `data/titers.csv` the right ones? We know of no peer-reviewed
   BLG above 13.88 g/L (Yao 2026, ethanol-fed) or 5.14 g/L on glucose (Li 2026).

### B. Bioprocess engineer from the enzyme or dairy industry

1. **Capital conventions.** Our base (Humbird's facility factors, Lang ~5.1, 9%/yr fixed costs) gives
   costs about 2.4–2.5× the NREL-style convention on the same process. Which is closer to what a food
   PF plant costs to build and run today? Report, Methods 2.5 and Calibration.
2. **Fermenters.** Humbird's ACCE quote curve prices a 300 m³ fermenter with agitator 2.9× above
   NREL's vendor quote. Which matches your experience?
3. **O₂ transfer.** We cap transfer at 150 mol O₂/m³/h per m³ of broth (Humbird's design value;
   aeration physics alone would allow ~376). Humbird's own workbook applies the cap per m³ of
   cell-free liquid (~97 per m³ of broth at our cell density). In the base the vessel volume, not
   O₂, sets the titer ceiling; once that is relaxed, O₂ and the secretion rate take over. Which
   basis, and which number, would you design to? Report, Methods 2.3 and Results Q3.
4. **Diafiltration.** One patent value (5 L/m²/h at 50 g/L protein) sizes most of our membrane area.
   What diafiltration and final-concentration fluxes do whey or enzyme plants achieve?
5. **Dryer feed.** We feed the dryer at 30% solids (BLG) and 23% (OVA), concentrated by membranes,
   following dairy practice for >60%-protein concentrates. Right?
6. **Heat removal.** 25 kW/m³ with external exchangers above ~114 m³ (grade D). Reasonable?
7. **Labour, cleaning and spent cells.** Humbird's attention model gives ~120 staff for 10 kt/yr;
   cleaning 7.3 kg solution per kg product; spent cells landfilled at $343/t dry (US). Any of these
   off by a large factor?

### C. A sceptic of PF cost claims

1. Is the "physical limit" framing meaningful, or does it overstate what is achievable?
2. Is whey the right benchmark for BLG? We argue it is the right *price* benchmark and the wrong
   *impact* benchmark (report, section 1 and Results Q7).
3. Where does the analysis overclaim? The internal audit removed several overclaims (AUDIT R7);
   which remain?
4. The calibration anchors are models, not plants. What real cost data could test the model?

### D. Optionally, David Humbird (author of the method)

1. Does the port of the baker's-yeast workbook and its extension to a secreted protein respect the
   method? (Report sections 2–3; `src/pftea/humbird_yeast.py` reproduces A.1 to 0.004%.)
2. A.1 applies the 150 mol/m³/h cap per m³ of cell-free liquid; we apply it per m³ of broth. Which
   did you intend for high-density fermenters?
3. The compressor formula in A.1 (exponent 1.4) and the broth-volume update signs (VALIDATION.md,
   anchor 1 findings 1 and 3): are these intended?

## Email drafts (for Pablo to send; placeholders in brackets)

**To a fermentation scientist**

> Subject: Request for a critical read: open cost model of precision-fermented BLG and OVA
>
> Dear [Name],
>
> I have built an open techno-economic model of food-grade β-lactoglobulin and ovalbumin made by
> precision fermentation, following Humbird's 2021 method, with every input sourced and graded. Its
> weakest point is the strain physiology: no measured product yield on sugar exists, so I derive it
> from Intelligen's design with a measured low-growth maintenance, and I cap secretion at
> 40 mg/g/h. Would you be willing to spend an hour telling me where the fermentation assumptions are
> wrong? The six questions are on one page (attached, section A); the report and an interactive
> explorer are attached too. Everything is public data; I will credit reviewers who wish it and
> answer every comment in the repository.
>
> Best regards, Pablo Antonio Moreno Casares

**To a bioprocess engineer**

> Subject: Capital and downstream assumptions for a precision-fermentation cost model
>
> Dear [Name],
>
> I am checking an open cost model of precision-fermented whey and egg proteins against people who
> build and run such plants. Its largest uncertainty is how to estimate capital: Humbird's factors
> and NREL-style vendor quotes differ by about 2.5× on the same process. The seven questions in
> section B of the attached page (fermenter costs, O₂ transfer design basis, diafiltration flux,
> dryer feed, heat removal, labour) are where your experience would change the answer most. Could
> you spare an hour? I will credit you if you wish and answer every comment publicly.
>
> Best regards, Pablo Antonio Moreno Casares

**To a sceptic**

> Subject: Please try to break this precision-fermentation cost analysis
>
> Dear [Name],
>
> I have written an open analysis of what precision-fermented BLG and OVA cost, and I would value a
> hostile read before it is public. It concludes that whey is hard to beat on price, that a
> "physical limit" floor sits around $6/kg, and that lactoferrin already costs less than most
> reported dairy prices. Where is it wrong or overclaimed? The questions in section C and the report are attached; the full audit log
> of what has already been corrected is in the repository.
>
> Best regards, Pablo Antonio Moreno Casares

## Comment log

| # | Reviewer | Comment | Response | Change |
|---|---|---|---|---|
| — | — | Human review not started | — | — |

AI pre-review (simulated reviewers; not a substitute for the human review above): see the section
below once run.
