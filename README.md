# pf-tea — open techno-economic model for precision-fermented food proteins

Goal: a transparent, public-data-only cost model for beta-lactoglobulin (whey) and
ovalbumin (egg white) made by precision fermentation. Output is a cost *distribution*
as a function of strain performance, not a single number.

Design rules
1. Every equation lives in plain Python in `src/pftea/`. No hidden cost engine.
2. Every number lives in `data/assumptions.yaml` with a source and a range.
3. Two validation tests reproduce published models before any new claim is made.
4. Results are reported as distributions (Monte Carlo), with titer shown explicitly.

Layout
```
data/assumptions.yaml   all parameters: base, low, high, unit, source
data/titers.csv         every public titer/yield data point you collect
src/pftea/params.py     load + validate assumptions
src/pftea/upstream.py   mass balance, fermenter sizing
src/pftea/downstream.py per-step recovery, purity, DSP sizing
src/pftea/capex.py      equipment cost curves, installation factors
src/pftea/opex.py       feedstock, utilities, labour, fixed costs
src/pftea/economics.py  cost of production, minimum selling price
src/pftea/montecarlo.py sample assumptions, run pipeline N times
src/pftea/pipeline.py   one function: assumptions -> results
tests/                  reproduce Voutilainen 2021 and Intelligen lactoferrin
notebooks/              figures for the write-up
docs/READING.md         what to read, in order
docs/LITERATURE.md      what exists in the literature and what does not
references/INDEX.md     every source with DOI, role and status (PDFs not committed)
PLAN.md                 phases, milestones, exit criteria
```

Run
```
uv venv --python 3.12 .venv && uv pip install -p .venv/bin/python -e ".[dev]"
.venv/bin/python -m pytest
python -m pftea.pipeline --product blg
```
