# pf-tea — open techno-economic model for precision-fermented food proteins

A transparent, public-data-only cost model for β-lactoglobulin (whey) and ovalbumin
(egg white) made by precision fermentation. It uses Humbird's (2021) method: element- and
electron-balanced stoichiometry, an O₂-limited fed-batch fermenter, and capital anchored to
the market price of baker's yeast. It is calibrated against NREL 2011, Intelligen 2025 and
Voutilainen 2021.

**Status (2026-09-26):** v1 draft complete, awaiting the author's review. Start with the
report.

## Deliverables

| What | Where |
|---|---|
| Report (preprint draft) | `report/pf_tea_report.pdf` (source `report/pf_tea_report.typ`) |
| One-page funder memo | `report/memo.pdf` |
| Supplementary workbook | `report/pf_tea_SI.xlsx`: parameters, evidence, all result tables, one live accounting sheet |
| Interactive explorer | `docs/explorer.html`: about 4,800 precomputed model runs, no install needed |
| Figures | `docs/figures/*.png` |
| Calibration record | `docs/VALIDATION.md` |

## Design rules

1. Every equation lives in plain Python in `src/pftea/`, with the equations in each module's
   docstring. There is no hidden cost engine.
2. Every number lives in `data/pf/base.yaml` with a range, an evidence grade (A–E) and a
   source. The evidence behind it is in `data/evidence/*.yaml`, with verbatim quotes and
   locators.
3. The method was calibrated before any new claim: against a market price (baker's yeast)
   and three published models. Misses are recorded, not tuned away (`docs/VALIDATION.md`).
4. Four scenarios are never merged: academic, industry, required and physical limit.
   Uncertainty is shown as a tornado coloured by evidence grade and as a Monte Carlo over
   feasible plants.

Start with [docs/SCOPE.md](docs/SCOPE.md) (the question) and [PLAN.md](PLAN.md) (phases).
New to bioprocessing? Read [docs/PRIMER.md](docs/PRIMER.md).

## Layout

```
data/pf/base.yaml           all parameters: value, range, grade, source (US and EU prices)
data/pf/scenarios/          academic, industry, physical_limit overrides
data/pf/benchmarks.yaml     incumbent prices and literature titers shown on the figures
data/evidence/              hosts, dsp, engineering, prices: graded evidence with quotes
data/calibration/           the four calibration cases
data/prices/                one-series CSVs behind prices.yaml
data/titers.csv             every public titer/yield data point
data/products/              BLG, OVA, cellulase: sequences and formulas
src/pftea/thermo.py         black-box stoichiometry, Heijnen dissipation, Tijhuis maintenance
src/pftea/fermentation.py   Humbird's A.1 fermenter (bubble column), compressor, chillers
src/pftea/humbird_yeast.py  anchor 1: exact port of Humbird's baker's-yeast workbook
src/pftea/product.py        protein formulas, product reaction, energetic ceiling
src/pftea/pf_ferm.py        PF fed-batch stirred tank: aeration optimum, O2 wall
src/pftea/equipment.py      equipment cost curves (Humbird/ACCE)
src/pftea/plant.py          whole plant: batch -> DSP -> scale -> capital -> costs -> MSP
src/pftea/finance.py        capital charge, DCF
src/pftea/calibration.py    anchors 2-4
src/pftea/scenarios.py      scenarios, cost maps, bridge, required titer, tornado, Monte Carlo
src/pftea/benchmarks.py     incumbent prices per kg protein, titer markers, claims
scripts/run_analyses.py     every result -> results/analyses.json (--only to rerun sections)
scripts/make_figures.py     docs/figures/*.png
scripts/explorer_grid.py    results/explorer_grid.json (parallel)
scripts/build_explorer.py   docs/explorer.html
scripts/build_si_workbook.py report/pf_tea_SI.xlsx
tests/                      Humbird port (exact) and calibration bands
docs/                       SCOPE, PRIMER, READING, exercises, LITERATURE, VALIDATION
references/INDEX.md         every source with DOI, role and status (PDFs not committed)
PLAN.md                     phases, honesty protocol, decisions log
```

## Run

```
uv venv --python 3.12 .venv && uv pip install -p .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/python scripts/run_analyses.py        # about 15 min; --fast for a quick pass
.venv/bin/python scripts/make_figures.py
.venv/bin/python scripts/explorer_grid.py && .venv/bin/python scripts/build_explorer.py
.venv/bin/python scripts/build_si_workbook.py
typst compile --root . report/pf_tea_report.typ && typst compile --root . report/memo.typ
```

Never run `uv run` inside the repo without `--no-project`: it re-syncs `.venv` and strips
the dev extras.
