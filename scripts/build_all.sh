#!/usr/bin/env bash
# One command to rebuild everything from the data files:
#   tests -> results/analyses.json -> figures -> explorer -> SI workbook -> report and memo PDFs.
# Usage: scripts/build_all.sh [--fast]    (--fast: coarse Monte Carlo and physical-limit search)
# Needs: .venv with the project installed (README), typst on PATH. About 1.5 h in full.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
export PYTHONPATH=src:tests
$PY -m pytest -q
$PY scripts/run_analyses.py "$@"
$PY scripts/make_figures.py
$PY scripts/explorer_grid.py
$PY scripts/build_explorer.py
$PY scripts/build_si_workbook.py
typst compile --root . report/pf_tea_report.typ
typst compile --root . report/memo.typ
echo "built: results/, docs/figures/, docs/explorer.html, report/*.pdf, report/pf_tea_SI.xlsx"
