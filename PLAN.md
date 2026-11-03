# Project plan (v2, 2026-09-26)

**Purpose.** A public techno-economic analysis of precision-fermented whey (β-lactoglobulin)
and egg-white (ovalbumin) proteins, at the standard of Humbird's 2021 cultivated-meat TEA.
Audience: the alt-protein community, funders and EU policy. Deliverables: a report and
preprint, code and workbook as supplementary information, an interactive explorer, and a
one-page memo.

**The question** is fixed in [docs/SCOPE.md](docs/SCOPE.md): cost today, cost at the
physical limits, and the performance needed for price parity.

**Method.** A physics-bounded process model rather than a factored top-down one:
1. Element-balanced stoichiometry gives sugar, O₂ and heat per kg of protein.
2. Fermenter transport limits (O₂ transfer, cooling, viscosity) give the feasible
   productivity for each vessel size.
3. From those, size the plant and its schedule, the downstream train and the utilities.
4. Cost the capital bottom-up with facility-class factors, then the operating costs and
   the financing.
5. Calibrate the method against real prices before it is allowed to say anything new.

## Honesty protocol (binding for every phase)

1. **Four scenarios, never merged:**
   - `academic`: grade A/B data only;
   - `industry`: adds grade C survey data and company claims;
   - `required`: inverse, the performance frontier for $10, $20 and $50/kg;
   - `physical-limit`: the floor at physical and stoichiometric limits.

   The headline figure is `required`.
2. **Evidence grade on every parameter:** A peer-reviewed, B patent example, C company
   claim, D analogy, E guess. Tornado charts are coloured by grade.
3. **No tuning to calibration targets.** Structural parameters (cost curves, installation
   factors, labour and utility models) are fixed once. Every anchor must pass with only
   its own process inputs changed. Record failures in docs/VALIDATION.md before fixing
   them.
4. **Quotes, not numbers.** Every titers.csv row carries a verbatim quote and a locator.
   Nothing enters the base case until the quote has been checked against the full text on
   disk (`verified: yes`). Pablo audits by exception.
5. **Public data only.** No private disclosures, and no citing the model's own outputs.
6. **Pre-registered priors** (docs/SCOPE.md) are scored at release and never used to tune.
7. **Agreement with another model is consistency, not validation.** Only real market
   prices (baker's yeast, enzymes) anchor the method to reality. Say which kind of check
   each one is.

## Phases

| Phase | Weeks | Deliverables | Exit criterion |
|---|---|---|---|
| **A. Frame and learn** | 2 | docs/SCOPE.md, docs/PRIMER.md, docs/READING.md, exercise A1 | Pablo signs off SCOPE; reading and primer self-check done; A1 unit cost within 20% of $38.99/kg |
| **B. Evidence** (parallel with A) | 2–3 | Remaining P1 items fetched; 31 titer rows verified; Intelligen inputs extracted to `data/validation/`; price series for whey, egg white, dextrose and energy (US + EU); sources for OTR ceilings, maximum vessel size and heat per O₂ | Every parameter sourced and graded; fewer than 3 base-case guesses |
| **C. Process model** | ~8 | C1: port Humbird's yeast simulator (SI sheets A.1–A.3, Equip, RawUtil, Phys) and reproduce it. C2: product-formation reactions for both hosts and the maximum yield. C3: cooling and viscosity limits, giving feasible productivity vs vessel size. C4: downstream train sized from fluxes and capacities. C5: plant integration, schedule, utilities, waste; finance as capital charge and DCF. | Every module tested with its equations in the docstring; Humbird's baker's-yeast result reproduced within 1% (software check) |
| **D. Calibration** (overlaps C) | 2 | Frozen structure run on four anchors; docs/VALIDATION.md | Baker's yeast within ±25% of the market-implied cost (reality check); NREL cellulase ±20%; Intelligen OVA ±30%; Voutilainen ±30%. Misses explained, not tuned away. |
| **E. Results** | 3 | Four scenarios; Monte Carlo with correlated inputs (*as built: independent draws, since no data set the correlations; the feasibility filter is the only coupling, and Spearman rank correlations report each input's share; report, "Uncertainty"*); the SCOPE figures (cost map, cost bridge, frontier, floor, tornado, scale and siting) | All figures regenerate from one command. Sanity: industry-benchmark inputs outside $10–200/kg means look for an accounting error first. |
| **F. Review** | ~4, mostly waiting | Assumptions and figures sent to a GFI fermentation scientist, an enzyme-industry bioprocess engineer and a known sceptic (optionally Humbird); docs/REVIEW.md | Every comment answered or fixed |
| **G. Release** | 2 | Report plus engrXiv preprint, SI (code, YAML, exported workbook), explorer (cultivated-meat pattern), one-page memo, scored priors | Public |

**Status (2026-10-30).** v4.1 is on `main`: seven products on an equal footing, four notes (rennet-cheese
casein, heme, transferrin, ovalbumin as a binder), the metabolic floor against the animals' feed bill, three
optional physics switches (off in the base) and an explorer with a detailed mode. Phases B–E are built and
the Phase G files are ready.
- **Checked today:** the 195 tests pass on `main`; the report, memo and preprint recompile from
  `results/analyses.json` to the same text as the committed PDFs.
- **Evidence:** 94 of 134 titers.csv rows verified in full text; the 40 unverified rows feed no scenario
  and no chart marker. `data/pf/base.yaml` holds 8 guesses (grade E). Five apply to every plant
  (`dsp_area_factor`, `sterilizer_peak_factor`, `boiler_peak_factor`, `fermenters_per_continuous_crew`,
  `compressor_building_m2_each`), so Phase B's exit criterion (fewer than 3 base-case guesses) is not met.
  Only `dsp_area_factor` has a range; it moves the BLG tornado by about $0.6/kg. The other three are
  route- or host-specific (CEX hardware, casein heat recovery, *T. reesei* μ_max).
- **Audits:** AI audits R1–R17 (`docs/AUDIT.md`) and a simulated expert pre-review (`docs/REVIEW.md`).
- **Open, all Pablo's:** the human review (Phase F proper); the release decisions and go-ahead
  (`docs/RELEASE.md`; the repository is private); the SCOPE sign-off, Phase A reading and the audit of
  verified quotes by exception, moved to the review of the finished draft (decision of 2026-09-26).

Earlier status notes, kept for the record:

**Status (2026-09-27, evening).** v2.1: the v2 draft was pre-reviewed by four simulated expert
reviewers (AI; `docs/ai-review/`), every comment answered in `docs/REVIEW.md`, and the resulting
changes made (`docs/AUDIT.md`, Phase F section), then checked against five further sources (decisions
log below). The human review (Phase F proper) waits on Pablo's
emails; the release (Phase G) waits on his go-ahead (`docs/RELEASE.md`).

**Status (2026-09-27).** v1 was audited (docs/AUDIT.md) and v2 implements the findings; phases
F (review packet) and G (release files) are being prepared. Earlier status, kept for the record:

**Status (2026-09-26, end of day).** A v1 draft of phases B–E and G is built and awaits
Pablo's review.
- **B:** four evidence files, 369 graded entries: hosts, downstream, engineering, prices.
- **C:** the process model, with Humbird's baker's yeast reproduced to 0.004%.
- **D:** the calibration record, with misses recorded (`docs/VALIDATION.md`).
- **E:** all analyses and figures, from one command.
- **G drafts:** report, memo, SI workbook and explorer.

Phase F (external review) has not started. Open items:
- 15 titer rows are not yet verified in full text.
- Pablo's SCOPE sign-off and the Phase A reading are pending.
- 9 parameters are still grade E (listed in the report's limitations).

## Decisions log

- **2026-11-03, physiology checks and the methanol fix (Pablo: "consider if there are other data that we can
  successfully predict"; then "take the best possible decisions"; Claude, for Pablo's review):**
  - New check 6 in docs/VALIDATION.md: the growth model's predictions of measured K. phaffii physiology. Glucose
    yield passes; heat per O2 and fed-batch yield are near misses at the edge of the measured spread; methanol
    missed by 12-21%; glycerol misses badly (unused).
  - Methanol fixed with the measured yield (base.yaml hosts.kphaffii.yx_methanol_g_g, grade A; thermo step 9). The
    O2 uptake, not fitted, moves from -21% to -7%. Methanol-fed results move by under 1%.
  - Not changed: glycerol (no case uses it), heat per O2 (inside the spread of Cooney's measurement), the fed-batch
    yield (the measured strains made ethanol).
  - Research for new checks (VALIDATION checks 6-7): NREL's enzyme-maker figure verified; Novozymes Blair says the
    model's capital per m3 may be low by 15-27% (recorded, not tuned); enzyme prices are context only; chymosin unusable.
  - Results rerun for the methanol-touching sections only (scenarios, Monte Carlo of the two methanol-fed cases,
    equivalents, lactoferrin, casein, albumin, heme) and checked: no glucose-fed number changed. Figures, SI, GFI entry
    and PDFs rebuilt; the PDFs with typst 0.15.0 (Python package; the committed ones were 0.15.1), same page counts,
    text differs only in the methanol-fed numbers and the rewritten methanol paragraph.

- **2026-11-03, model panel redesign (Pablo: "redesign the interactive panel to more easily convey the key information
  and make it easy to understand and verify the model", planned from first principles without the current explorer;
  Claude built it, for Pablo's review):**
  - Design in `docs/PANEL_DESIGN.md`: the answer first, then the cost as amount x price, then the price as eleven
    numbered steps that the page recomputes and checks against the model. Levers step between exact model runs.
  - `plant.evaluate` now builds every cost line from terms (amount x unit price, `Result.ledger`); results unchanged
    (largest relative difference 4e-16 on 18 cases). The batch reports its peak production O2 use (`o2_use_prod`).
  - New: `src/pftea/chain.py`, `scripts/panel_data.py` (3,250 runs, ~30 min on 4 cores), `scripts/build_panel.py`,
    `docs/panel.html`, `tests/test_panel.py`. The old explorer stays until Pablo chooses.

- **2026-10-25, optional physics, plain-language evidence labels and a short preprint (Pablo: "implement them, and
  add the option to keep it simple or more complex"; "grade is internal slang"; "focus on the cleanups"; Claude built
  it, for Pablo's review):**
  - Three switches, all off by default (base results unchanged to the cent): growth-coupled secretion
    (`strain.secretion_model`; Maurer 2006 shape, Rebnegger 2024 floor), a large-tank growth-yield loss
    (`fermenter.growth_yield_loss`; George 1998, Bylund 1998) and continuous production (`fermenter.mode`; Yamanie
    2026 run length). Preset `scenarios/detailed.yaml`; analysis section `options`. Result: tied to growth, the base
    titer needs ~19 mg/g/h at 0.1/h (9x the best measured); at the best measured rate BLG costs ~$136/kg
    (fed-batch) or ~$106 (continuous), and lactoferrin stays inside its market band.
  - Real-plant capital check (`data/evidence/plants.yaml`, `benchmarks.plant_cost_check`, VALIDATION check 5):
    $68k per m3 of fermenter against $55-91k from Liberation Labs scaled to 7,200 m3.
  - Readers now see the kind of evidence in words (measured, published design, company claim or survey, analogy or
    judgment, guess, modelling choice); the data files keep the letters A-E.
  - `report/preprint.typ`: a five-page preprint sharing the report's helpers (`report/common.typ`).
  - Candidate list: osteopontin, sweet proteins, food enzymes (`docs/PROTEIN_CANDIDATES.md`).

- **2026-10-06, v4.1: three full texts, transferrin and binder notes (Pablo: downloaded the three papers; "I'd do both
  proteins"; Claude built it, for Pablo's review):**
  - Liu 2026, Hu 2025 and Zhu 2018 read in full: titers.csv rows verified (40 of 134 rows remain unverified, none in a
    scenario); chart labels no longer say "abstract only". Hu's lactoferrin was grown on cellulose and bran.
  - Transferrin (`tf`, P02787) as a NOTE, not a product (demand is tens of t/yr; Wildtype dropped it): albumin's route with
    Novozymes' transferrin column data (capture 70%, borate polish 93%); best titer 2.29 g/L of supernatant in S. cerevisiae
    (Finnis 2010). Result: $314-1,939/kg rTf; $0.12-0.35 per kg cultivated meat at 0.37 g/kg, against ~$81 at catalogue price.
  - Ovalbumin as a binder: cost-in-use only. At 4% protein PF OVA costs ~$0.85/kg analogue (base), about dried egg white,
    ~13x methylcellulose ($0.07; India's MC tariff line, the only one that isolates MC). Evidence: data/evidence/binder.yaml.
  - Report: two notes, summary items 8-9, answers, limitations, references (also for the floor section), evidence table.

- **2026-10-05, metabolic floor and the animals' feed bill (Pablo, 2026-10-02: evaluate the price better, no
  forecasting; 2026-10-05: "do all of that"; Claude built it, for Pablo's review):**
  - src/pftea/floor.py: substrate, NH3, O2 and heat per kg of protein at the energetic yield ceiling, their cost,
    and the productivity bound from O2 transfer and heat removal. BLG: 1.77 kg glucose, $0.88/kg of inputs
    ($0.71 of it glucose at $0.40/kg; EU $1.28), at most ~13 kg/m3/h (cooling-limited; the base case makes 0.27).
  - data/evidence/feed.yaml (US and EU, 58 entries): feed per kg of edible protein and its cost, parent and pullet
    feed included, US broiler feed plus a sourced delivered-feed adder (~$53/t), milk credited for its cattle sales by
    value. Feed shares from Wageningen's model farms (EU and US poultry) and USDA ERS (US milk) turn a feed bill into
    a farm-gate cost. EU milk is a lower bound (forage at specific costs) and gets no farm cost.
  - Result (run_analyses.s_floor, docs/figures/fig12_feed_vs_floor.png = report Figure 13, report section "Feedstock
    against feed", memo bullet, SI sheet Floor_vs_feed): with ALL the animal's feed charged to its protein, the base case's
    glucose ($4.1/kg BLG US, 19% of its cost) costs no more than the animals' feed ($4.7-6.6 US, $7.9-8.9 EU poultry); for
    milk and eggs an energy split would put their protein's feed below PF's glucose (audit R16-M1). PF's gap is everything
    else ($17 vs $2-8 on the farm, which may understate the farm's). The glucose floor is 7-9x below the feed bills.
  - Secretion ceiling: data/evidence/kinetic.yaml (39 entries) brackets strain.q_p_max_mg_g_h = 40 between the highest
    secretion rate ever measured (15-16 mg/g/h, A. niger glucoamylase) and the translational capacity of K. phaffii.
    Value unchanged (no result changes); base.yaml's source text now cites it. A flaw in its growth-law arithmetic
    (the inactive ribosome reserve counted as translating) was corrected; the bracket is 18-41 mg/g/h at mu 0.2/h.
  - Audit R16 (AI, docs/AUDIT.md): no HIGH findings; six MEDIUM and the LOW fixed. Titer check: 43 of 134 titers.csv rows
    unverified, none in a base case or headline scenario; four uses (one albumin variant, three chart markers) rest on
    three paywalled papers, now labelled 'abstract only' and first on references/DOWNLOADS.md.

- **2026-10-02, v4: model review and serum albumin (Pablo: take the candidates "one by one, in priority
  order"; "consider if this is the best possible model ... no artificial complexity, but SOTA or close";
  Claude built it, for Pablo's review):**
  - An independent AI review compared the method with published PF and cultivated-meat TEAs (gaps G1-G6;
    docs/AUDIT.md, v4). Verdict: at or above the published state of the art for a multi-protein screening
    TEA (its estimate P ~0.85); its uncertainty is strain data and accounting conventions, not missing
    physics. Done: G1 methanol production phase (pf_ferm, thermo.anabolic, plant.methanol_yield); G2
    vessel sizing (scenarios.size_fermenter, 50-200 m3 up to the 200 m3 cap); G4 Spearman rank
    correlations in the Monte Carlo. G5 first-of-a-kind: no sourced premium on file, so SCOPE now excludes
    it explicitly (RAND R-2569 requested). Not done, by decision: G3 growth-coupled secretion (an unused
    knob that changes no result; stated as a limitation), G6 multi-column chromatography (albumin's
    capture-only route is a stated judgment), and everything the review called artificial complexity
    (mechanistic chromatography, CFD, genome-scale models, rebuilding in SuperPro/BioSTEAM).
  - Serum albumin (`alb`, HSA P02768) on the cation-exchange route with Delta/Recombumin column data,
    cell-culture purity (96%), 1 kt/yr. Evidence: data/evidence/albumin.yaml (52 entries). Academic: Zhu
    2021, 17.47 g/L in 192 h of methanol induction (abstract; full text requested), costed on methanol.
    Incumbent: bulk bovine serum albumin ($40-70/kg, grade C); GFI's $10/kg target and catalogue prices as
    context; cost per kg of cultivated meat in report Q7.
  - Methanol-induced academic cases (lactoferrin Lv 2023, beta-casein Choi 1996) now costed on methanol.
  - After audit R12 and Pablo's downloads (Zhu 2021, RAND R-2569): albumin's base is the patent's minimal
    two-column train (CEX + AEX polish), ~$216/kg (capture-only $143 as the optimistic case); its academic
    titer is per whole broth (8.74 g/L; 17.47 is per litre of supernatant); membranes alone reach only 77%
    albumin; a pioneer-plant case (capital x 1.28, RAND) is shown separately. docs/AUDIT.md, R12.

- **2026-10-02, v4 continued: α-lactalbumin, rennet-cheese casein and heme (Pablo: "let's do the missing
  proteins you have in the queue"):**
  - Evidence by research subagents, checked here: data/evidence/alac.yaml, heme.yaml, and an α<sub>s1</sub>/κ
    section of casein.yaml; 23 rows added to data/titers.csv (3 abstract rows replaced by full-text ones).
  - α-Lactalbumin (`alac`, bovine P00711) is a main product: BLG's membrane route at the GRN 763 isolate purity
    (0.90 of dry matter), 1 kt/yr, base design point; academic Wang 2025 (0.60 g/L human α-lac, ethanol,
    priced as glucose); incumbent band $15–123/kg (C). Physical limit capped at the food-grade market (31.8 kt).
  - α<sub>s1</sub>- and κ-casein are NOT main products (α<sub>s1</sub> on the acid route repeats β-casein within ~1%;
    κ has no market of its own): run_analyses.s_cheese costs a two-strain blend (data/pf/scenarios/cheese.yaml).
  - Heme is a note, not a product (as planned): run_analyses.s_heme bounds secreted LegH on the membrane route.
  - Code: scenarios.unused_paths skips every other product's dryer leaf (off-list products have leaves too);
    make_figures marks titer markers below the axis at its left edge.

- **2026-10-02, full texts from Pablo (Chezan 2026, Kim 2025):** casein precipitated at pH 4.5 (its
  solubility minimum); precipitation recovery low end 0.78 (assay), central 0.95 kept; ovomucoid academic
  titer verified (0.929 g/L, 60 h, methanol-free). docs/AUDIT.md, v3 follow-up.
- **2026-10-01 (night), ovomucoid added and casein evidence corrected (Claude, working overnight at
  Pablo's request; for his review):**
  - Ovomucoid (`ovd`, UniProt P01005), chosen first in docs/PROTEIN_CANDIDATES.md. Evidence:
    data/evidence/ovomucoid.yaml (36 entries). EVERY's GRN 967 is a single-protein ovomucoid made in
    methanol-induced *K. phaffii* by UF/DF alone (no chromatography); GRN 1104 is ovalbumin, not a mix.
    Base: base.yaml's design point on the membrane route, with the dossier's purity (0.76 of dry matter,
    A) and egg-white dryer feed (23%, C; EVERY dries from 5-6%, the low end). Academic: EVERY's 30.19 g/L
    patent example (B; the best public titer); variant: Kim 2025's 0.93 g/L (abstract only). Incumbent and
    egg equivalent shared with OVA (`compare_to` may now list several products).
  - Casein, after reading Choi 1996/2001, Iaria 2026, Balasubramanian 2025 and the NewMilkBuzz/Fermify
    patents: no secreted casein titer is public for any yeast or fungus; Choi's 0.7-1.0 g/L is
    intracellular and 0.245 g/L was one glycoform in a lysate (cas_kphaffii now 1.0 g/L, flagged); the
    recombinant beta-casein pI is ~5.5, higher than milk casein's (the report had the direction wrong);
    acid_precip_recovery low 0.85 -> 0.67 (Chezan 2026); titers.csv: Chung 1991 corrected, 9 rows added.
- **2026-10-01, all proteins on an equal footing in figures and report (Pablo: "all proteins in
  equal footing insofar that is possible"; Claude built it, for Pablo's review):**
  - SCOPE.md's question now covers β-casein and lactoferrin; Q8 becomes "how the downstream route
    changes the product and its cost" (Fig. 9, routes and purity per product).
  - Figures 1, 3, 4, 5, 6, 7 and 10 have one panel or row per product, read from the results; each
    product on its own base plant and against its own incumbent. Lactoferrin differs only where its
    market forces it: its own price axis, a 250 t/yr plant, targets of $100/200/400.
  - run_analyses: scale curves, the demonstrated-secretion best case and the milk/egg equivalents
    now run for every product (casein against a litre of milk); the bridge ends with a casein variant.
  - The explorer and the SI workbook cover the four products. The report is rewritten as version 3.
- **2026-10-01, β-casein added (Pablo: "casein was the next"; Claude built it, for Pablo's review):**
  - Product `cas`: bovine β-casein A2 (UniProt P02666), *K. phaffii*, methanol-free, secreted, as in
    Eden Brew's FSANZ A1342. Evidence in `data/evidence/casein.yaml` (29 entries) and 18 titer rows.
  - Base case: base.yaml's design point (30 g/L, 72 h, 10 kt/yr), as for BLG, on a new downstream
    route `acid`: isoelectric precipitation of the MF permeate (pH 4, H₃PO₄, 90 °C), decanter
    washes, sodium caseinate, spray drying from 20% solids. Spec by analogy with Formo's GRN 1312
    (≥90% protein, >97% casein of protein), the only public PF casein that precipitates. The UF/DF-only
    route (Eden Brew: 22% protein, ~5.6% β-casein in the powder) is the variant `cas_ufdf_edenbrew`.
  - Scenarios: academic 3 g/L (Standing Ovation patent, *E. coli*, intracellular: the best public casein
    titer in any host, used as an analogy); variant 0.245 g/L (best *K. phaffii* β-casein, methanol);
    industry 42 g/L (flagged: no company discloses a casein titer); physical limit at 100 kt/yr.
  - Grade D/E inputs to check: the acid dose (milk's buffer capacity per m³, D), the precipitation
    recovery (95%, D) and the heater's heat recovery (90%, E). Together they move the base by less than
    $3/kg. Decanters are costed on the disk-stack centrifuge curve (no decanter quote on file).
  - Incumbent: casein trade and USDA import series (`benchmarks.yaml`; USDA quotes per lb now read
    with `per: lb`).
  - `PRODUCTS` is now read from `data/pf/products.yaml`, and the tornado's off-route parameters are
    derived from each product's route (a test checks that every skipped leaf leaves the price unchanged).
- **2026-10-01, lactoferrin and the next proteins (Claude; for Pablo's review):**
  - Lactoferrin now runs through every analysis that BLG and OVA do, on its own base case
    (`data/pf/products.yaml`: Intelligen's 10 g/L design, cation exchange, 250 t/yr). The figures
    and report text still treat it as the Q8 contrast case, and SCOPE.md has not changed.
  - [docs/PROTEIN_CANDIDATES.md](docs/PROTEIN_CANDIDATES.md) surveys what to add next (branch
    `protein-candidates`). Its proposal: the egg-white mix centred on ovomucoid, then food-grade
    albumin for cultivated-meat media; casein stays in v2; heme gets a cost-in-use note only.
    Nothing from it enters the model until its quotes are verified and SCOPE.md records the change.
- **2026-09-27, follow-up reading after the pre-review (Claude; for Pablo's review):**
  - Five sources Pablo downloaded were read (Humbird 2017 aeration; Heyland 2010 and Looser 2015
    physiology; Intelligen's lactoferrin report; Lv 2023), three of them by AI reading passes
    whose findings were checked against the texts, table images and workbook cells.
  - Corrected: the compressor formula (Humbird's workbook puts k where (k−1)/k belongs; the PF
    model now uses the textbook form, the A.1 port keeps his); a latent failure of the aeration
    search at high DO; the lactoferrin comparison (Intelligen's figures are costs of production,
    $292 is its UF/DF-only case; now reconciled by category); the cation-exchange flow (Intelligen's
    20 CV/h replaces a guess); seed density and inoculum (Intelligen's flowsheet, 17.6 and 0.88 g/L).
  - Kept, with reasons (REVIEW.md, follow-up section): the 40 mg/g/h secretion ceiling of the
    best case, the production-maintenance range, our lactoferrin design and prices.
  - Added: `tests/test_data.py` (every data file parses; evidence schema and unique keys), after
    a malformed evidence entry was found.

- **2026-09-27, Phase F AI pre-review (Claude, under the "no mistakes" mandate; for Pablo's review):**
  - Four simulated reviewers (fermentation scientist, bioprocess engineer, sceptic, method author's
    perspective) reviewed v2; each comment was re-checked before acting (`docs/REVIEW.md`).
  - Fermenters are now priced from NREL's industrial vendor quote in both conventions; Humbird's
    aseptic cell-culture vessel prices, used in v2, are a named high case. This moves the base BLG
    from $29.4 to about $21/kg; see AUDIT.md for the evidence.
  - Humbird's air-sparged STR O₂ value (200 mol/m³/h per m³ of cell-free liquid) replaces the
    bubble-column 150 per m³ of broth; missing-equipment allowance 20% (his A.1 value).
  - The physical-limit scenario is presented as a best case conditional on an assumed secretion
    rate; "secretion without growth" is the report's lead caveat.
  - Kept, with reasons: Humbird's 9% fixed-cost rule, Intelligen's 500 g/L feed as the base, and the
    exclusion of start-up, working capital and failed batches.

- **2026-09-26/27, audit and v2 (Claude, at Pablo's request "make sure there are no mistakes",
  then "close the gaps"; for Pablo's review):**
  - Eight independent reviewers (R1–R8) audited v1; every finding, decision and effect is in
    `docs/AUDIT.md`, implemented in three commits on branch `audit-fixes`.
  - A research pass sourced the grade-E placeholders (P-1 to P-13); six guesses remain, four of them
    formerly hidden constants in the code.
  - Production-phase stoichiometry: the product yield is derived from Intelligen's Eq. 2 with a
    measured production-phase maintenance (AUDIT, decision on R2-Q2/R6-C2).
  - OVA's 50 g/L "practical solubility" is no longer a limit (P-8); it is a sensitivity.
  - Capital conventions renamed: "price-anchored capital (Humbird method)" and "design-report
    capital (NREL-style)" (Pablo, 2026-09-26).
  - Added at Pablo's request: milk and egg equivalents; a lactoferrin contrast case.
  - SCOPE's scenario definitions rewritten to match what runs (R8-m4).

- **2026-09-26, working mode:** Pablo reviews the finished v1 rather than gating each phase.
  Claude builds B through G as a complete draft. Gates that need Pablo move to that review:
  the SCOPE sign-off, the Phase A reading, and auditing the verified quotes by exception.
  The honesty protocol is unchanged.
- **2026-09-26** (defaults accepted by Pablo):
  - Products: BLG + OVA in v1; casein in v2.
  - Hosts: *K. phaffii* base, *T. reesei* variant.
  - Plant: nth-of-a-kind, 10 kt/yr base, swept 1–100 kt/yr; US Midwest base plus an EU
    variant.
  - Output: report + preprint. This replaces v1's "not a paper".
  - `openpyxl` added as a dev dependency.
  - Product specs: the GRN 1056-style concentrate is the base; the isolate is a variant.
- **2026-09-26, v1 build (Claude; for Pablo's review):**
  - *Escalation 2018→2025:* 1.33 (CEPCI and the BLS machinery PPI), replacing the placeholder 1.25.
    Humbird's own index (PPI chemicals, 1.23) is the low end; pumps and compressors (1.52) the
    high end. For consistency, the NREL anchor is deflated to 2007 with CEPCI (0.871), NREL's
    own index. This moved the recorded misses (see VALIDATION, record of changes).
  - *Cost bridge:* one change per step, ending exactly at the base case (asserted in code).
    OVA concentrate and isolate are shown as variants from the base.
  - *Feasibility:* designs past the O₂ or heat limit are never costed as if they worked.
    Required titers are searched only below the feasible ceiling. Tornado and Monte Carlo
    mark infeasible draws.
  - *OVA:* its practical solubility of 50 g/L (Intelligen's assumption) caps its titer and
    floor. A sensitivity with the cap lifted is reported next to the base.
  - *EU variant:* NL electricity (Eurostat band IF), EU gas (band I4), EU glucose proxies (C),
    NL wages (derived, B). Construction costs are the same as the US: no sourced location
    factor is on disk.
- **2026-09-26:** Calibration anchors changed:
  - add baker's yeast (reality check), NREL 2011 cellulase and Intelligen OVA 2025;
  - Voutilainen 2021 moves from anchor 1 to anchor 4;
  - Intelligen lactoferrin 2024 becomes an optional downstream check (not on disk).

  `tests/test_validation.py` is updated in Phase D.
- **2026-09-18:** Honesty protocol points 1–5 (then called amendments).

## What not to do

- No point estimate without its titer, rate and yield stated next to it.
- No more than two products in v1. *(Superseded: β-casein and lactoferrin joined on 2026-10-01, ovomucoid
  the same night, serum albumin and α-lactalbumin on 2026-10-02; decisions log.)*
- No BioSTEAM or SuperPro as the core model. BioSTEAM may cross-check capital costs; the
  SuperPro trial may only be used to read Intelligen's example file.
- No claim that cannot be traced to a row in data/pf/base.yaml or data/evidence/.
- No first-of-a-kind penalty mixed into the base case; it is shown separately (v4: RAND's pioneer-plant
  capital growth, x 1.28).
- No teaching numbers (docs/PRIMER.md, exercises) copied into the model; they are
  illustrative.

## History

v1 (2026-09-18) had phases 0–5. They map to v2 as follows:
- 0 (learn) → A
- 1 (data) → B
- 2 (deterministic model) → C + D
- 3 (uncertainty) → E
- 4 (review) → F
- 5 (release) → G

v1's "model additions queued for Phase 2" (O₂ feasibility test, per-unit downstream
sizing, labour scaled with fermenter count, correlated titer and batch-time sampling) are
now part of C3–C5 and E.
