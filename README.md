# pf-tea: an open cost model for precision-fermented food proteins

pf-tea estimates what food proteins made by precision fermentation (PF) cost to produce. It uses public
data only, and you can rerun and check every number.

It covers seven proteins on an equal footing:

| Protein | What it is |
|---|---|
| β-lactoglobulin (BLG) | the main whey protein |
| α-lactalbumin | the second whey protein, used in infant formula |
| ovalbumin (OVA) | the main egg-white protein |
| ovomucoid | another egg-white protein, sold as a heat-stable ingredient |
| β-casein | one of the two main proteins of cheese curd |
| lactoferrin | a scarce, high-value milk protein |
| serum albumin | a protein in the growth media of cultivated meat |

Short notes cover casein for rennet cheese, heme (soy leghemoglobin), transferrin and ovalbumin as a
binder. A last section compares the sugar a PF plant needs with the feed that animals eat.

**Start here:** the one-page memo (`report/memo.pdf`), then the five-page preprint
(`report/preprint.pdf`); the full report (`report/pf_tea_report.pdf`) has every method and result. `docs/GFI_SUBMISSION.md` lists the base-case numbers per protein.

**Status.** No human expert has reviewed this work yet. The author built it with an AI assistant
(Claude, Anthropic), and independent AI reviewers audited each version. `docs/AUDIT.md` and
`docs/REVIEW.md` record every finding and every fix.

## How it works

A few words first. Precision fermentation grows an engineered microbe in a large tank (a *fermenter*) and
has it release (*secrete*) one protein into the liquid, the *broth*. The *titer* is the grams of protein per
litre of broth when the batch ends; the *secretion rate* is how many mg of protein each gram of cells
releases per hour.

**The price in one line.** Per kg of protein, a plant pays for sugar, for the plant itself, and for
everything else (purification, energy, waste, staff). The plant is the largest part: each year it costs a
fixed share of what it took to build (a *capital charge* that repays the investment with interest, plus
maintenance and insurance), and that cost is spread over the protein each fermenter makes. How much each
fermenter makes is set by how fast the cells secrete, how many cells each litre holds, and how much of the
time the tank spends making protein rather than growing cells or being cleaned. That is why the strain's
secretion rate matters more than the sugar price. The report and the explorer show this split with the
model's numbers.

The model follows Humbird's (2021) method for cultivated meat and applies it to a microbe that secretes
a protein:

1. **Fermentation.** The model balances every element and every electron in the reaction. It then
   checks that the fermenter can supply enough oxygen and remove enough heat. It never costs a design
   that breaks these limits.
2. **Purification.** Membranes, precipitation or chromatography columns turn the broth into a dry powder.
3. **Plant and money.** The model sizes the whole plant, prices the equipment, and adds labour, energy,
   materials and the capital charge. The result is a *minimum selling price*: a cost per kg that repays the
   plant, before any profit margin; not a market price.

It compares a *base case* (the design point of published plants, 30 g/L) with four scenarios and never
mixes them. The *best published strain* (`academic`) uses the best titers in peer-reviewed papers. The
*industry benchmark* (`industry`) uses the average titer in companies' cost models, 42 g/L. *Required* asks
what titer would reach a target price. The *physical-limit best case* sets every assumed limit at its best
at once.

## How it differs from published cost models

Only a handful of public cost models exist for PF food proteins. Most are single-protein flowsheets
built in commercial software (SuperPro Designer), such as Intelligen's ovalbumin and lactoferrin
models. pf-tea differs in five ways:

- **It checks the physics.** It balances elements and electrons, and it tests oxygen transfer, heat
  removal and vessel volume. Most published models assume a titer and a yield and never ask whether a
  real fermenter could reach them.
- **It shows where each number comes from.** Every input has a source, a short quote from that source
  and the kind of evidence: measured, published design, company claim or survey, analogy or judgment,
  or guess. The uncertainty charts are coloured by kind of evidence.
- **It tests itself first.** Before any new claim, the model reproduces the market cost of baker's
  yeast with Humbird's workbook and rebuilds three published designs (NREL 2011, Intelligen 2025,
  Voutilainen 2021). `docs/VALIDATION.md` records the misses instead of tuning them away.
- **It treats seven proteins the same way.** The same plant, prices and accounting apply to every
  protein, so you can compare them directly.
- **It is open.** All code, data and results are in this repository. Published models usually give
  results, but not the files you would need to rerun them.

Its costs often come out higher than published NREL-style designs, mainly because of accounting.
Humbird's method charges about 9% of the investment a year for maintenance and insurance; NREL-style
design reports charge under 2%. The report shows both. Published costs differ from pf-tea's in both
directions: Intelligen's ovalbumin design lands within a few percent of it, and Intelligen's
lactoferrin model comes out higher. Section 5.2 of the report ("Why published PF costs are lower")
traces the differences line by line.

## Simple or detailed

The base case is the simple model. Three switches in `data/pf/base.yaml` turn on more physics;
each is off by default, so the base numbers do not change:

| Switch | Simple (base) | Detailed |
|---|---|---|
| `strain.secretion_model` | `constant`: one secretion rate in production, none while growing | `growth_coupled`: secretion falls as growth slows (Maurer 2006 shape, Rebnegger 2024 floor) |
| `fermenter.growth_yield_loss` | `0`: a large tank behaves like a lab one | `0.065`: gradients in a large tank cost 6.5% of the growth yield (George 1998) |
| `fermenter.mode` | `fed_batch` | `continuous`: production runs as a chemostat for 10 days (Yamanie 2026) |

The scenario `data/pf/scenarios/detailed.yaml` switches them on together. A fourth check,
`benchmarks.plant_cost_check`, compares the model's capital with a real plant (`docs/VALIDATION.md`).

## What you get

| What | Where |
|---|---|
| One-page memo | `report/memo.pdf` |
| Short preprint (5 pages) | `report/preprint.pdf` (source `report/preprint.typ`) |
| Full report (preprint draft) | `report/pf_tea_report.pdf` (source `report/pf_tea_report.typ`) |
| Workbook with every parameter and result | `report/pf_tea_SI.xlsx` |
| Interactive explorer (no install) | `docs/explorer.html` |
| Model panel: the price step by step, with checks (no install; draft redesign) | `docs/panel.html` (design: `docs/PANEL_DESIGN.md`) |
| Figures | `docs/figures/*.png` |
| Checks against published models | `docs/VALIDATION.md` |
| Audit log and AI reviews | `docs/AUDIT.md`, `docs/REVIEW.md`, `docs/ai-review/` |
| Entry for GFI's fermentation cost-model database | `docs/GFI_SUBMISSION.md` |

New to bioprocessing? Read `docs/PRIMER.md` first.

## Design rules

1. Plain Python in `src/pftea/` holds every equation, and each module's docstring states them. No
   hidden cost engine exists.
2. `data/pf/base.yaml` holds every number, with a range, the kind of evidence and a source.
   `data/evidence/*.yaml` holds the evidence, with quotes and page locators.
3. The model passed its checks against baker's yeast and three published models before it made any new
   claim. `docs/VALIDATION.md` records the misses.
4. The four scenarios stay separate. A tornado chart, coloured by the kind of evidence, and a Monte Carlo
   over feasible plants show the uncertainty.

`docs/SCOPE.md` states the question, and `PLAN.md` the phases.

## Layout

```
data/pf/base.yaml           all parameters: value, range, kind of evidence, source (US and EU prices)
data/pf/scenarios/          academic, industry, physical_limit, lactoferrin, casein, albumin, cheese, heme, transferrin, binder,
                            detailed (the three optional physics switches on)
data/pf/benchmarks.yaml     incumbent prices and literature titers shown on the figures
data/evidence/              hosts, dsp, engineering, prices, placeholders, milk_egg, lactoferrin, casein,
                            ovomucoid, albumin, alac, heme, feed, kinetic, transferrin, binder, plants:
                            sourced evidence with quotes
data/calibration/           the four calibration cases
data/prices/                one-series CSVs behind prices.yaml
data/titers.csv             every public titer/yield data point
data/products/              BLG, OVA, ovomucoid, beta-casein, lactoferrin, albumin, alpha-lac, alpha-s1/kappa-casein,
                            leghemoglobin, cellulase: sequences and formulas
src/pftea/thermo.py         black-box stoichiometry, Heijnen dissipation, Tijhuis maintenance
src/pftea/fermentation.py   Humbird's A.1 fermenter (bubble column), compressor, chillers
src/pftea/humbird_yeast.py  anchor 1: exact port of Humbird's baker's-yeast workbook
src/pftea/product.py        protein formulas, product reaction, energetic ceiling
src/pftea/pf_ferm.py        PF fed-batch stirred tank: aeration optimum, O2 and heat limits
src/pftea/equipment.py      equipment cost curves (Humbird/ACCE)
src/pftea/plant.py          whole plant: batch -> DSP -> scale -> capital -> costs -> MSP
src/pftea/finance.py        capital charge, DCF
src/pftea/calibration.py    anchors 2-4
src/pftea/scenarios.py      scenarios, cost maps, bridge, required titer, tornado, Monte Carlo
src/pftea/benchmarks.py     incumbent prices per kg protein, titer markers, claims, real-plant capital check
src/pftea/floor.py          metabolic floor: least sugar, O2 and heat per kg of protein; productivity bound
src/pftea/balances.py       one batch's sugar and O2 split by use, for checking by hand
src/pftea/chain.py          one run as the model panel's record: cost ledger, step-by-step chain, limits, sugar
src/pftea/params.py         loads base.yaml, applies scenario overrides, samples ranges
src/pftea/labels.py         readable names for parameter paths (text only)
scripts/run_analyses.py     every result -> results/analyses.json (--only to rerun sections)
scripts/make_figures.py     docs/figures/*.png
scripts/explorer_grid.py    results/explorer_grid.json (parallel)
scripts/build_explorer.py   docs/explorer.html
scripts/panel_data.py       results/panel_data.json: run grid and cases for the model panel (parallel)
scripts/build_panel.py      docs/panel.html (template scripts/panel_template.html)
scripts/build_si_workbook.py report/pf_tea_SI.xlsx
scripts/gfi_submission.py   docs/GFI_SUBMISSION.md, one row per protein for GFI's database
scripts/extract_humbird_si.py constants and reference values from Humbird's SI workbook
tests/                      Humbird port (exact), calibration records, model invariants
docs/                       SCOPE, PRIMER, READING, exercises, LITERATURE, VALIDATION, AUDIT, REVIEW
scripts/build_all.sh        one command: tests, analyses, figures, explorer, SI, PDFs
references/INDEX.md         every source with DOI, role and status (PDFs not committed)
PLAN.md                     phases, honesty protocol, decisions log
```

## Run

```
uv venv --python 3.12 .venv && uv pip install -p .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/python scripts/run_analyses.py        # a few hours; --fast for a quick pass
.venv/bin/python scripts/make_figures.py
.venv/bin/python scripts/explorer_grid.py && .venv/bin/python scripts/build_explorer.py
.venv/bin/python scripts/panel_data.py && .venv/bin/python scripts/build_panel.py   # about 30 min on 4 cores
.venv/bin/python scripts/build_si_workbook.py
typst compile --root . report/pf_tea_report.typ && typst compile --root . report/memo.typ && typst compile --root . report/preprint.typ
```

Never run `uv run` inside the repo without `--no-project`: it re-syncs `.venv` and strips
the dev extras.

Or all of it at once: `scripts/build_all.sh` (a few hours; `--fast` for a quick pass).

## Licence

Code: MIT (`LICENSE`). Data, text and figures: CC BY 4.0 (`LICENSE-DATA.md`). Cite as in
`CITATION.cff`. (Proposed licences; the author confirms them at public release.)
