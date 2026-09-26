"""Supplementary workbook: report/pf_tea_SI.xlsx.

An export, not a live model: parameters (data/pf/base.yaml), scenario overrides, evidence
files, and every result table in results/analyses.json, as values. One sheet ('Accounting')
is live: it recomputes the base-case MSP_CCF from the annual cost items with formulas, so a
reader can see the capital-charge arithmetic and change the rate or life.

Run:  .venv/bin/python scripts/build_si_workbook.py
"""
import csv
import json
import sys
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pftea.labels import label  # noqa: E402

R = json.loads((ROOT / "results/analyses.json").read_text())
P = yaml.safe_load((ROOT / "data/pf/base.yaml").read_text())
OUT = ROOT / "report/pf_tea_SI.xlsx"

FONT = "Arial"
HDR = Font(name=FONT, bold=True)
BODY = Font(name=FONT)
BLUE = Font(name=FONT, color="0000FF")
GREY = Font(name=FONT, color="808080", italic=True)
FILL = PatternFill("solid", fgColor="EEF3FB")
WRAP = Alignment(wrap_text=True, vertical="top")

wb = Workbook()


def sheet(title, header, rows, widths=None, note=None):
    ws = wb.create_sheet(title)
    r0 = 1
    if note:
        ws.cell(1, 1, note).font = GREY
        r0 = 3
    for j, h in enumerate(header, 1):
        c = ws.cell(r0, j, h)
        c.font, c.fill = HDR, FILL
    for i, row in enumerate(rows, r0 + 1):
        for j, x in enumerate(row, 1):
            c = ws.cell(i, j, x)
            if isinstance(x, str) and x[:1] in ("=", "+", "@"):   # text, never a formula
                c.data_type = "s"
            c.font = BODY
            if isinstance(x, str) and len(x) > 60:
                c.alignment = WRAP
    for j, w in enumerate(widths or [], 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(r0 + 1, 1)
    return ws


def num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else (None if x is None else str(x))


# ---------------------------------------------------------------- README
ws = wb.active
ws.title = "README"
lines = [
    ("Supplementary workbook: the cost of precision-fermented BLG and OVA (draft v1)", HDR),
    (f"Generated from results/analyses.json ({R['generated']}) and the data files of the pf-tea repository.", BODY),
    ("All sheets hold values exported by scripts/build_si_workbook.py, except 'Accounting', which is live (formulas).", BODY),
    ("Money: 2025 US dollars. Per kg = per kg of target protein unless the column says powder.", BODY),
    ("MSP_CCF: annual operating cost plus a capital charge (7.5%, 10 years = 14.6% of TCI per year), divided by output.", BODY),
    ("Conventions: 'humbird' = Humbird 2021 facility-class capital (base); 'light' = NREL-style capital and fixed costs.", BODY),
    ("Evidence grades: A measured/official, B design value or patent example, C claim or survey, D derived, E placeholder.", BODY),
    ("Sheets: Parameters, Scenarios, Results, Cost_breakdown, Capex_base, Cost_vs_titer, Required_titer, Claims,", BODY),
    ("        Tornado, MonteCarlo, Scale, Bridge, Calibration, Titers, Evidence_hosts, Evidence_dsp,", BODY),
    ("        Evidence_engineering, Evidence_prices, Accounting (live).", BODY),
]
for i, (t, f) in enumerate(lines, 1):
    ws.cell(i, 1, t).font = f
ws.column_dimensions["A"].width = 120


# ---------------------------------------------------------------- Parameters
def flat(d, pre=""):
    for k, x in d.items():
        if isinstance(x, dict):
            if any(key in x for key in ("value", "us_midwest", "grade")):
                yield pre + k, x
            else:
                yield from flat(x, pre + k + ".")


rows = []
for path, x in flat(P):
    val = x.get("value", x.get("us_midwest"))
    rows.append([path, label(path), num(val) if not isinstance(val, (dict, list)) else json.dumps(val),
                 num(x.get("eu_nw")), num(x.get("low")), num(x.get("high")), x.get("unit", ""), x.get("grade", ""),
                 x.get("source", x.get("note", ""))])
sheet("Parameters", ["path", "label", "value (US)", "value (EU)", "low", "high", "unit", "grade", "source"], rows,
      [34, 30, 14, 12, 10, 10, 12, 7, 110], note="data/pf/base.yaml, every parameter with its range, grade and source.")

# ---------------------------------------------------------------- Scenarios
rows = []
for name in ("academic", "industry", "physical_limit"):
    s = yaml.safe_load((ROOT / f"data/pf/scenarios/{name}.yaml").read_text())
    for blk in ("common", "blg", "ova"):
        for k, x in (s.get(blk) or {}).items():
            rows.append([name, blk, k, num(x)])
    for k, x in (s.get("mc_ranges") or {}).items():
        rows.append([name, "mc_ranges", k, json.dumps(x)])
sheet("Scenarios", ["scenario", "block", "parameter", "override"], rows, [16, 12, 40, 20],
      note="Overrides applied on top of base.yaml (data/pf/scenarios/*.yaml). Comments with sources are in the files.")


# ---------------------------------------------------------------- Results
def res_row(name, d):
    return [name, num(d["design"].get("titer")), d["msp_ccf"], d["cop"], d["msp_dcf"], d["per_kg_powder"], d["tci"],
            d["physical"]["glucose_kg"], d["physical"]["electricity_kWh"], d.get("feasible", True), "; ".join(d["flags"])]


rows = [res_row(f"base/{k}", d) for k, d in R["base"].items()]
rows += [res_row(f"base_light/{k}", d) for k, d in R["base_light"].items()]
rows += [res_row(f"base_eu/{k}", d) for k, d in R["base_eu"].items()]
rows += [res_row(f"base_isolate/{k}", d) for k, d in R["base_isolate"].items()]
rows += [res_row(k, d) for k, d in R["scenarios"].items()]
rows += [res_row(f"physical_limit/{k}", d) for k, d in R["physical_limit"].items()]
sheet("Results", ["case", "titer g/L", "MSP_CCF $/kg", "COP $/kg", "MSP_DCF $/kg", "MSP_CCF $/kg powder", "TCI $",
                  "glucose kg/kg", "electricity kWh/kg", "feasible", "flags"], rows,
      [30, 10, 13, 11, 13, 16, 16, 13, 16, 9, 60])

cases = {**{f"base/{k}": d for k, d in R["base"].items()}, **{f"base_light/{k}": d for k, d in R["base_light"].items()},
         **R["scenarios"], **{f"physical_limit/{k}": d for k, d in R["physical_limit"].items()}}
items = list(R["base"]["blg"]["per_kg"].keys())
sheet("Cost_breakdown", ["case"] + items + ["total"],
      [[k] + [d["per_kg"].get(i, 0.0) for i in items] + [d["msp_ccf"]] for k, d in cases.items()],
      [30] + [14] * (len(items) + 1), note="$/kg target protein by cost item.")
sheet("Capex_base", ["item", "BLG $", "OVA $"],
      [[k, R["base"]["blg"]["capex"][k], R["base"]["ova"]["capex"].get(k)] for k in R["base"]["blg"]["capex"]],
      [40, 16, 16], note="Base case capital, 2025$ (purchased equipment, installation, buildings, indirects).")

# ---------------------------------------------------------------- analyses
rows = []
for prod, c in R["cost_vs_titer"].items():
    for i, tp in enumerate(c["t_prods"]):
        for T, m, f in zip(c["titers"], c["msp"][i], c["feasible"][i]):
            rows.append([prod, "humbird", tp, T, m, f])
    for T, m, f in zip(c["titers"], c["light_72h"], c["light_72h_feasible"]):
        rows.append([prod, "light", 72, T, m, f])
sheet("Cost_vs_titer", ["product", "convention", "t_prod h", "titer g/L", "MSP_CCF $/kg", "feasible (O2/heat)"], rows,
      [10, 12, 10, 10, 14, 18])

rows = []
for key, d in R["required"].items():
    for tg, lst in d.items():
        for tp, r in zip(R["required_t_prods"], lst):
            rows.append([key, float(tg), tp, r["titer"], r.get("ceiling"), r["feasible"]])
sheet("Required_titer", ["product/convention", "target $/kg", "t_prod h", "titer needed g/L", "O2/heat ceiling g/L",
                         "reachable"], rows, [20, 12, 10, 16, 18, 10],
      note="Titer at which MSP_CCF equals the target, searched only below the O2/heat ceiling (blank = not reachable).")
sheet("Claims", ["claim", "titer g/L", "host", "product", "cells g/L", "shortest feasible t_prod h", "MSP humbird",
                 "MSP light"],
      [[c["label"], c["titer"], c["host"], c["product"], c["X_prod"], c["t_prod_min"], c.get("msp_humbird"),
        c.get("msp_light")] for c in R["claims"]], [52, 10, 10, 9, 10, 22, 13, 12])
sheet("Tornado", ["parameter", "label", "grade", "low", "high", "MSP at low", "MSP at high", "base", "swing",
                  "feasible at low", "feasible at high"],
      [[t["path"], label(t["path"]), t["grade"], t["low"], t["high"], t["msp_low"], t["msp_high"], t["base"], t["swing"],
        t.get("feasible_low"), t.get("feasible_high")] for t in R["tornado"]],
      [38, 32, 7, 10, 10, 12, 12, 10, 10, 14, 14], note="Industry-benchmark BLG, one parameter at a time.")
sheet("MonteCarlo", ["scenario", "draws", "feasible fraction", "p10", "p50", "p90"],
      [[k, d.get("n"), d["feasible_frac"], d["p10"], d["p50"], d["p90"]] for k, d in R["monte_carlo"].items()],
      [18, 8, 16, 10, 10, 10], note="Triangular draws over each scenario's ranges; percentiles over feasible draws only.")
sheet("Scale", ["kt/yr"] + list(R["scale"]["curves"].keys()),
      [[o / 1000] + [R["scale"]["curves"][k][i] for k in R["scale"]["curves"]] for i, o in enumerate(R["scale"]["outputs"])],
      [10, 22, 22, 22, 22], note="Industry-benchmark BLG, MSP_CCF $/kg.")
sheet("Bridge", ["step", "kind", "MSP_CCF $/kg after the step"], [[b["step"], b["kind"], b["msp"]] for b in R["bridge"]],
      [70, 10, 26], note="Cumulative changes from NREL 2011 on-site cellulase (2025 prices, NREL-style capital) to the base case.")
rows = [["bakers_yeast", "COP $/kg dry cells (2018$)", R["calibration"]["bakers_yeast"]["cop"],
         R["calibration"]["bakers_yeast"]["humbird"]]]
for name in ("nrel2011_cellulase", "intelligen2025_ova", "voutilainen2021_case"):
    for k, x in R["calibration"][name].items():
        if isinstance(x, list):
            rows.append([name, k, x[0], x[1]])
sheet("Calibration", ["anchor", "quantity", "ours", "theirs"], rows, [22, 58, 14, 14],
      note="docs/VALIDATION.md has the diagnosis of every difference.")

# ---------------------------------------------------------------- data
with (ROOT / "data/titers.csv").open() as fh:
    t = list(csv.reader(fh))
sheet("Titers", t[0], t[1:], [14, 14, 10, 10, 8, 10, 12, 20, 6, 50, 20, 12, 8, 8, 50])
for f in ("hosts", "dsp", "engineering", "prices"):
    E = yaml.safe_load((ROOT / f"data/evidence/{f}.yaml").read_text())
    rows = [[e.get("key"), num(e.get("value")) if not isinstance(e.get("value"), (dict, list)) else json.dumps(e.get("value")),
             num(e.get("low")), num(e.get("high")), e.get("unit", ""), e.get("grade", ""), e.get("source", ""),
             str(e.get("doi_or_url", "")), str(e.get("locator", "")), str(e.get("quote", "")), str(e.get("note", ""))]
            for e in E]
    sheet(f"Evidence_{f}", ["key", "value", "low", "high", "unit", "grade", "source", "doi/url", "locator", "quote", "note"],
          rows, [34, 12, 9, 9, 18, 6, 40, 30, 24, 60, 50], note=f"data/evidence/{f}.yaml")

# ---------------------------------------------------------------- Accounting (live)
ws = wb.create_sheet("Accounting")
b = R["base"]["blg"]
ws["A1"] = "Live: base-case BLG MSP_CCF from its annual cost items (blue = inputs exported from the model; change them)."
ws["A1"].font = GREY
ws["A3"], ws["B3"] = "Input", "Value"
ws["A3"].font = ws["B3"].font = HDR
inputs = [("annual output, kg target protein", float(P["plant"]["annual_target_protein_t"]["value"]) * 1000,
           "data/pf/base.yaml plant.annual_target_protein_t x 1000"),
          ("total capital investment (TCI), $", b["tci"], "results/analyses.json base.blg.tci"),
          ("capital charge rate i", float(P["finance"]["ccf_rate"]["value"]), "Humbird 2021 p.39"),
          ("capital charge life n, years", float(P["finance"]["ccf_life_y"]["value"]), "Humbird 2021 p.39")]
for i, (k, x, src) in enumerate(inputs, 4):
    ws.cell(i, 1, k).font = BODY
    c = ws.cell(i, 2, x)
    c.font = BLUE
    c.comment = Comment(f"Source: {src}", "pf-tea")
ws["A9"], ws["B9"] = "Annual operating cost item, $/yr", "Value"
ws["A9"].font = ws["B9"].font = HDR
op_items = [k for k in b["per_kg"] if k != "capital charge"]
r = 10
for k in op_items:
    ws.cell(r, 1, k).font = BODY
    c = ws.cell(r, 2, b["per_kg"][k] * inputs[0][1])
    c.font = BLUE
    c.comment = Comment("Source: results/analyses.json base.blg.per_kg x annual output", "pf-tea")
    r += 1
last = r - 1
ws.cell(r + 1, 1, "Calculation").font = HDR
calc = [("capital recovery factor, 1/yr", "=B6/(1-(1+B6)^(-B7))"),
        ("capital charge, $/yr", f"=B5*B{r + 2}"),
        ("operating cost, $/yr", f"=SUM(B10:B{last})"),
        ("MSP_CCF, $/kg", f"=(B{r + 3}+B{r + 4})/B4"),
        ("model value, $/kg (check)", b["msp_ccf"])]
for i, (k, f) in enumerate(calc, r + 2):
    ws.cell(i, 1, k).font = BODY
    ws.cell(i, 2, f).font = BODY if isinstance(f, str) else BLUE
    ws.cell(i, 2).number_format = "0.0000" if i == r + 2 else "#,##0.00"
for i in range(4, r):
    ws.cell(i, 2).number_format = "#,##0.00"
ws.column_dimensions["A"].width = 44
ws.column_dimensions["B"].width = 20

for w in wb.worksheets:
    for row in w.iter_rows():
        for c in row:
            if c.font is None or c.font.name != FONT:
                c.font = Font(name=FONT, bold=c.font.bold if c.font else False)
wb.save(OUT)
print("wrote", OUT.relative_to(ROOT), "sheets:", len(wb.worksheets))
