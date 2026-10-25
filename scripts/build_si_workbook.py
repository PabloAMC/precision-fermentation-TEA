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
from pftea.labels import evidence, label  # noqa: E402

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
    if isinstance(x, dict) and any(k in x for k in ("us_midwest", "eu_nw")):    # location-keyed range end
        return f"US {x.get('us_midwest')} / EU {x.get('eu_nw')}"
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else (None if x is None else str(x))


# ---------------------------------------------------------------- README
ws = wb.active
ws.title = "README"
lines = [
    ("Supplementary workbook: the cost of precision-fermented BLG, OVA, ovomucoid, beta-casein, lactoferrin, serum albumin and alpha-lactalbumin (v4), with notes on rennet-cheese casein, heme, transferrin, binders and the metabolic floor", HDR),
    (f"Generated from results/analyses.json ({R['generated']}) and the data files of the pf-tea repository.", BODY),
    ("All sheets hold values exported by scripts/build_si_workbook.py, except 'Accounting', which is live (formulas).", BODY),
    ("Money: 2025 US dollars. Per kg = per kg of target protein unless the column says powder.", BODY),
    ("MSP_CCF: annual operating cost plus a capital charge (7.5%, 10 years = 14.6% of TCI per year), divided by output.", BODY),
    ("Capital conventions: 'humbird' = price-anchored capital (Humbird 2021 facility classes; base);", BODY),
    ("        'light' = design-report capital (NREL-style vendor-quote fermenters and ~2% fixed costs).", BODY),
    ("Kinds of evidence (stored as letters A-E): A measured/official, B published design or patent example, C company claim or survey, D analogy or judgment,", BODY),
    ("        E guess (listed in docs/VALIDATION.md and docs/AUDIT.md).", BODY),
    ("Sheets: Parameters, Scenarios, Results, Cost_breakdown, Capex_base, Cost_vs_titer, Required_titer, Claims,", BODY),
    ("        Convention_steps, Base_sensitivities, Constants, Best_design_base, Ceiling_limits, Tornado, MonteCarlo,", BODY),
    ("        Scale, Bridge, Calibration, Equivalents, Lactoferrin, Lactoferrin_reconciliation, Market_context, Titers,", BODY),
    ("        Evidence_* (one per evidence file), Accounting (live).", BODY),
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
                 num(x.get("eu_nw")), num(x.get("low")), num(x.get("high")), x.get("unit", ""), evidence(x.get("grade", "")),
                 x.get("source", x.get("note", ""))])
sheet("Parameters", ["path", "label", "value (US)", "value (EU)", "low", "high", "unit", "evidence", "source"], rows,
      [34, 30, 14, 12, 10, 10, 12, 7, 110], note="data/pf/base.yaml, every parameter with its range, kind of evidence and source.")

# ---------------------------------------------------------------- Scenarios
rows = []
for name in ("academic", "industry", "physical_limit", "lactoferrin", "casein", "albumin", "cheese", "heme", "transferrin", "binder"):
    s = yaml.safe_load((ROOT / f"data/pf/scenarios/{name}.yaml").read_text())
    for blk, body in s.items():
        if blk in ("description", "search", "mc_paths"):
            continue
        if not isinstance(body or {}, dict):
            continue
        for k, x in (body or {}).items():
            rows.append([name, blk, k, json.dumps(x) if isinstance(x, dict) else num(x)])
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
rows += [res_row(f"lactoferrin/{k}", d) for k, d in R["lactoferrin"]["cases"].items()]
rows += [res_row(f"casein/{k}", d) for k, d in R.get("casein", {}).get("cases", {}).items()]
rows += [res_row(f"albumin/{k}", d) for k, d in R.get("albumin", {}).get("cases", {}).items()]
rows += [res_row(f"alac/{k}", R["alac"][k]) for k in ("at_10kt", "at_10kt_industry") if k in R.get("alac", {})]
rows += [res_row(f"cheese/alpha-s1/{k}", d) for k, d in R.get("cheese", {}).get("as1", {}).items()]
rows += [res_row(f"cheese/{r}/share {s}/{t} g/L", d) for r, rr in R.get("cheese", {}).get("kap", {}).items()
         for s, dd in rr.items() for t, d in dd.items()]
rows += [res_row(f"heme/{k}", d) for k, d in R.get("heme", {}).get("cases", {}).items()]
rows += [res_row(f"transferrin/{k}", d) for k, d in R.get("transferrin", {}).get("cases", {}).items()]
sheet("Results", ["case", "titer g/L", "MSP_CCF $/kg", "COP $/kg", "MSP_DCF $/kg", "MSP_CCF $/kg powder", "TCI $",
                  "glucose kg/kg", "electricity kWh/kg", "feasible", "flags"], rows,
      [30, 10, 13, 11, 13, 16, 16, 13, 16, 9, 60])

cases = {**{f"base/{k}": d for k, d in R["base"].items()}, **{f"base_light/{k}": d for k, d in R["base_light"].items()},
         **R["scenarios"], **{f"physical_limit/{k}": d for k, d in R["physical_limit"].items()}}
items = list(R["base"]["blg"]["per_kg"].keys())
sheet("Cost_breakdown", ["case"] + items + ["total"],
      [[k] + [d["per_kg"].get(i, 0.0) for i in items] + [d["msp_ccf"]] for k, d in cases.items()],
      [30] + [14] * (len(items) + 1), note="$/kg target protein by cost item.")
CAPEX_ITEMS = list(dict.fromkeys(k for d in R["base"].values() for k in d["capex"]))   # union, first-seen order
sheet("Capex_base", ["item"] + [f"{k} $" for k in R["base"]],
      [[k] + [d["capex"].get(k) for d in R["base"].values()] for k in CAPEX_ITEMS],
      [40] + [16] * len(R["base"]), note="Base case capital of each product, 2025$ (purchased equipment, installation, "
                                         "buildings, indirects); blank = the item is not on that product's route.")

# ---------------------------------------------------------------- analyses
rows = []
for prod, c in R["cost_vs_titer"].items():
    for i, tp in enumerate(c["t_prods"]):
        for T, m, f in zip(c["titers"], c["msp"][i], c["feasible"][i]):
            rows.append([prod, "humbird", tp, T, m, f])
    for T, m, f in zip(c["titers"], c["light_72h"], c["light_72h_feasible"]):
        rows.append([prod, "light", 72, T, m, f])
sheet("Cost_vs_titer", ["product", "convention", "t_prod h", "titer g/L", "MSP_CCF $/kg", "feasible (all limits)"], rows,
      [10, 12, 10, 10, 14, 18])

rows = []
for key, d in R["required"].items():
    for tg, lst in d.items():
        for tp, r in zip(R["required_t_prods"], lst):
            rows.append([key, float(tg), tp, r["titer"], r.get("ceiling"), r["feasible"], r.get("q_p_mg_g_h")])
sheet("Required_titer", ["product/convention", "target $/kg", "t_prod h", "titer needed g/L", "feasibility ceiling g/L",
                         "reachable", "specific productivity mg/g/h"], rows, [26, 12, 10, 16, 20, 10, 16],
      note="Titer at which MSP_CCF equals the target, searched only below the feasibility ceiling (blank = not reachable); "
           "'/feed600' rows use a 600 g/L glucose feed.")
sheet("Claims", ["claim", "titer g/L", "host", "product", "cells g/L", "own t_prod h", "feasible then", "MSP then (price-anchored)",
                 "MSP then (design-report)", "shortest feasible t_prod h", "MSP there (price-anchored)", "MSP there (design-report)",
                 "q_p there mg/g/h"],
      [[c["label"], c["titer"], c["host"], c["product"], c["X_prod"], c["t_prod_own"], c["feasible_own"],
        c.get("msp_own_humbird"), c.get("msp_own_light"), c["t_prod_min"], c.get("msp_humbird"), c.get("msp_light"),
        c.get("q_p_mg_g_h")] for c in R["claims"]], [52, 10, 10, 9, 10, 12, 12, 16, 16, 18, 16, 16, 14],
      note="Each claim at its own production time (72 h where the source gives none), then at the shortest feasible "
           "production phase, where specific productivity runs at its 40 mg/g/h ceiling (a best case).")
sheet("Convention_steps", ["step", "MSP_CCF $/kg (base BLG)"], [[d["step"], d["msp"]] for d in R["convention_steps"]],
      [70, 22], note="The gap between the capital conventions, taken one rule at a time.")
base_ = R["base"]["blg"]["msp_ccf"]
sheet("Base_sensitivities", ["one change to the base BLG", "MSP_CCF $/kg", "change $/kg"],
      [[k_, x, x - base_] for k_, x in R.get("base_sensitivities", {}).items()], [70, 14, 14],
      note="One change at a time on the base BLG (run_analyses.s_base); quoted in the report text.")


def _flat(d, pre=""):
    for k_, x in d.items():
        if isinstance(x, dict):
            yield from _flat(x, f"{pre}{k_}.")
        elif isinstance(x, list):
            yield [pre + k_, ", ".join(f"{y:.4g}" if isinstance(y, (int, float)) else str(y) for y in x)]
        else:
            yield [pre + k_, x]


sheet("Constants", ["model-derived constant", "value"], list(_flat(R.get("constants", {}))), [60, 24],
      note="Values quoted in the report (run_analyses.constants): yields, O2 caps per m3 of broth, vessel prices, the "
           "energetic ceiling, aeration energy per kg O2, seed-train share, the production-maintenance bound.")
BDB = {"blg": R["best_design_base"], **{k: x for k, x in R.get("best_design_base_by_product", {}).items() if k != "blg"}}
sheet("Best_design_base", ["product", "secretion ceiling mg/g/h", "MSP_CCF $/kg", "cells g/L", "t_prod h", "titer g/L", "binding"],
      [[prod, float(q), d["msp_ccf"], d["X_prod"], d["t_prod"], d["titer"], ", ".join(d["binding"])]
       for prod, bd in BDB.items() for q, d in bd.items()], [10, 22, 14, 10, 10, 10, 50],
      note="Cheapest design of each product with base biology, capital, vessel and scale; only cell density, production "
           "time and titer free (review SC-1). Other products at the best demonstrated secretion (2.1 mg/g/h).")
sheet("Ceiling_limits", ["case", "t_prod h", "ceiling g/L", "limit that fails above it"],
      [[k, r_["t_prod"], r_["ceiling"], r_["limit"]] for k, rows_ in R["ceiling_limits"].items() for r_ in rows_],
      [44, 10, 12, 30])
sheet("Tornado", ["product", "parameter", "label", "evidence", "low", "high", "MSP at low", "MSP at high", "base", "swing",
                  "low truncated to feasibility", "high truncated to feasibility"],
      [[prod, t["path"], label(t["path"]), evidence(t["grade"]), num(t["low"]), num(t["high"]), t["msp_low"], t["msp_high"], t["base"],
        t["swing"], t.get("truncated_low"), t.get("truncated_high")]
       for prod, tor_ in (R.get("tornado_by_product") or {"blg": R["tornado"]}).items() for t in tor_],
      [10, 38, 32, 9, 12, 12, 12, 12, 10, 10, 16, 16],
      note="Industry benchmark of each product, one parameter at a time. An end that breaks a physical limit is replaced by the last "
           "feasible value (truncated = TRUE). 'capital.basis' (conventions) and 'capital.fermenter_quote' (vendor quote vs "
           "aseptic cell-culture vessels) are structural bars.")
sheet("MonteCarlo", ["scenario", "draws", "feasible fraction", "p10", "p50", "p90", "p10 all draws", "p50 all draws",
                     "p90 all draws", "scenario value", "its percentile", "why draws fail"],
      [[k, d.get("n"), d["feasible_frac"], d["p10"], d["p50"], d["p90"], d.get("p10_all"), d.get("p50_all"), d.get("p90_all"),
        d.get("base"), d.get("base_percentile"),
        "; ".join(f"{a}: {b}" for a, b in (d.get("infeasible_reasons") or {}).items())]
       for k, d in R["monte_carlo"].items()],
      [18, 8, 16, 10, 10, 10, 12, 12, 12, 14, 14, 40],
      note="Triangular draws over each scenario's ranges; p10-p90 over feasible draws, and over all draws with a cost; "
           "draws the model cannot build count as infeasible.")
sheet("MonteCarlo_rank", ["scenario", "parameter", "label", "Spearman rho", "rho squared"],
      sorted([[k, par, label(par), rho, rho * rho] for k, d in R["monte_carlo"].items()
              for par, rho in (d.get("rank_corr") or {}).items() if rho is not None], key=lambda r: (r[0], -abs(r[3]))),
      [18, 40, 36, 14, 12],
      note="Spearman rank correlation of each sampled input with MSP over the feasible draws (review G4). The inputs are drawn "
           "independently, so rho squared approximates each input's share of the rank variance of MSP: the global counterpart "
           "of the one-at-a-time tornado.")
SCB = R.get("scale_by_product") or {"blg": R["scale"]}
sheet("Scale", ["product", "kt/yr"] + list(R["scale"]["curves"].keys()),
      [[prod, o / 1000] + [c["curves"][k][i] for k in c["curves"]] for prod, c in SCB.items() for i, o in enumerate(c["outputs"])],
      [10, 10, 22, 22, 22, 22], note="Each product's industry benchmark, MSP_CCF $/kg.")
sheet("Bridge", ["step", "kind", "MSP_CCF $/kg after the step"], [[b["step"], b["kind"], b["msp"]] for b in R["bridge"]],
      [70, 10, 26], note="Cumulative changes from NREL 2011 on-site cellulase (2025 prices, NREL-style capital) to the base case.")
rows = [["bakers_yeast", "COP $/kg dry cells (2018$)", R["calibration"]["bakers_yeast"]["cop"],
         R["calibration"]["bakers_yeast"]["humbird"]]]
for name in ("nrel2011_cellulase", "intelligen2025_ova", "voutilainen2021_case"):
    for k, x in R["calibration"][name].items():
        if isinstance(x, list):
            rows.append([name, k, x[0], x[1]])
for k, x in R["calibration"].get("bakers_yeast_stacks", {}).items():
    rows.append(["bakers_yeast (A.1 variants)", k, x if not isinstance(x, list) else f"{x[0]:.2f}-{x[1]:.2f}", None])
sheet("Calibration", ["anchor", "quantity", "ours", "theirs"], rows, [26, 66, 14, 14],
      note="docs/VALIDATION.md has the diagnosis of every difference.")

E_ = R["equivalents"]
rows = []
for name, src in E_["sources"].items():
    for lab, ser in src["prices"].items():
        for yr, x in sorted(ser.items()):
            rows.append([name, lab, int(yr), x, src["protein_equivalent"][lab][yr]])
sheet("Equivalents", ["source", "price series", "year", f"$ per unit (2025$)", "$ per kg of its protein (2025$)"], rows,
      [8, 44, 8, 18, 26], note="Milk: per litre (33.7 g protein, 3.3 g BLG); eggs: per US large egg (3.64 g egg-white protein, "
                               "1.96 g OVA). data/evidence/milk_egg.yaml; the protein price is an upper bound on its value.")
L_ = R["lactoferrin"]
rows = [[k, d["design"]["titer"], d["msp_ccf"], d["cop"], d["per_kg_powder"], d["tci"]] for k, d in L_["cases"].items()]
rows += [[f"titer {T} g/L (price-anchored)", T, m, None, None, None] for T, m in zip(L_["cost_vs_titer"]["titers"], L_["cost_vs_titer"]["msp"])]
rows += [[f"scale {x} t/yr (price-anchored)", 10, m, None, None, None]
         for x, m in zip(R["scale_lf"]["outputs"], R["scale_lf"]["curves"]["US, price-anchored"])]
rows += [[f"sensitivity {k}", 10, m, None, None, None] for k, m in L_["resin"].items()]
sheet("Lactoferrin", ["case", "titer g/L", "MSP_CCF $/kg LF", "cost of production $/kg LF", "$/kg powder", "TCI $"], rows,
      [52, 10, 16, 16, 14, 16],
      note=f"Lactoferrin route variants, cost vs titer at the design time, scale and resin levers; base case 250 t/yr, cation "
           f"exchange (data/pf/products.yaml; variants in data/pf/scenarios/lactoferrin.yaml). Reported dairy bLF prices "
           f"${L_['reported_prices']['band'][0]:,.0f}-{L_['reported_prices']['band'][1]:,.0f}/kg in 2025 dollars (company claims or surveys); "
           + "; ".join(f"{c_['key']}: ${c_['value_money_year']:.0f}/kg (a cost of production, 2025$)" for c_ in L_['reported_prices'].get('comparators', [])))
C_ = R.get("casein")
if C_:
    rows = [[k, d["design"]["titer"], d["msp_ccf"], d["cop"], d["per_kg_powder"], d["design"]["purity_dry"]] for k, d in C_["cases"].items()]
    rows += [[f"lever {k}", None, m, None, None, None] for k, m in C_["levers"].items()]
    sheet("Casein", ["case", "titer g/L", "MSP_CCF $/kg casein", "cost of production $/kg", "$/kg powder", "casein share of dry matter"],
          rows, [52, 10, 18, 18, 14, 18],
          note="Beta-casein: the UF/DF-only route (Eden Brew, FSANZ A1342) and the precipitation inputs with the weakest evidence "
               "(acid dose, recovery, heat recovery, wash water) at the ends of their ranges, on the base case (data/pf/products.yaml; "
               "data/pf/scenarios/casein.yaml; data/evidence/casein.yaml).")
A_ = R.get("albumin")
if A_:
    rows = [[k, d["design"]["titer"], d["msp_ccf"], d["cop"], d["per_kg_powder"], d["design"]["purity_dry"]] for k, d in A_["cases"].items()]
    rows += [[f"lever {k}", None, m, None, None, None] for k, m in A_["resin"].items()]
    rows += [[f"base case at {o:,.0f} t/yr", None, m, None, None, None]
             for o, m in zip(A_["scale"]["outputs"], A_["scale"]["curves"]["US, price-anchored"])]
    cm = A_["cm"]
    rows += [[f"$ per kg cultivated meat at {g:.1f} g albumin/kg ({L} L medium/kg x {cm['conc_g_L']} g/L), base case", None,
              R["base"]["alb"]["msp_ccf"] * g / 1000, None, None, None] for g, L in zip(cm["g_per_kg_cm"], cm["medium_L_per_kg"])]
    sheet("Albumin", ["case", "titer g/L", "MSP_CCF $/kg albumin", "cost of production $/kg", "$/kg powder", "albumin share of dry matter"],
          rows, [62, 10, 18, 18, 14, 18],
          note=f"Serum albumin for cultivated-meat media: methanol induction, CEX recovery and UF/DF-only variants, resin levers, plant "
               f"size, and the cost per kg of cultivated meat at GFI 2023's medium use (data/pf/products.yaml; data/pf/scenarios/albumin.yaml; "
               f"data/evidence/albumin.yaml). Bulk albumin ${A_['reported_prices']['band'][0]:,.0f}-{A_['reported_prices']['band'][1]:,.0f}/kg "
               f"(technical BSA, company or survey figures); GFI's target ${cm['gfi_target_usd_kg']}/kg; research-catalogue rHSA "
               f"${cm['catalogue_usd_kg'][0]:,.0f}-{cm['catalogue_usd_kg'][1]:,.0f}/kg.")
# Intelligen's lactoferrin model against ours, SuperPro categories, $/kg LF (report tab-lf-rec; review L)
CATS = [("raw materials", "raw_materials"), ("labour", "labour"), ("facility", "facility"), ("lab/QC/QA", "lab_qc_qa"),
        ("consumables", "consumables"), ("waste", "waste"), ("utilities", "utilities")]
IC = {c_["ours"]: c_ for c_ in L_["reported_prices"].get("comparators", [])}
REC_ = L_.get("reconciliation", {})
rows = []
for ours, theirs_design in (("lf_ufdf_only", "lf_intelligen_a"), ("lf", "lf_intelligen_b")):
    c_ = IC.get(ours)
    if not c_ or theirs_design not in REC_:
        continue
    kg = c_["values"]["powder_kg_per_yr"] * c_["values"]["lf_frac_powder"]
    for lab_, ik in CATS:
        rows.append([c_["key"], lab_, c_["values"][ik] / kg * c_["deflator"], REC_[theirs_design]["per_kg"][lab_],
                     REC_[ours]["per_kg"][lab_]])
    rows.append([c_["key"], "total (cost of production)", c_["value_money_year"], REC_[theirs_design]["cop"], REC_[ours]["cop"]])
    rows.append([c_["key"], "total capital investment $", c_["values"]["tci_usd"] * c_["deflator"], REC_[theirs_design]["tci"],
                 REC_[ours]["tci"]])
sheet("Lactoferrin_reconciliation", ["Intelligen case", "category", "Intelligen $/kg LF (2025$)", "ours at their design inputs",
                                     "ours, base design"], rows, [36, 28, 22, 22, 18],
      note="Intelligen's 2024 costs (Feb 2026 report, Tables 2-5) per kg lactoferrin, deflated to 2025$; ours = cost of production "
           "(operating + 10-yr depreciation) in the same categories. Their design inputs: data/pf/scenarios/lactoferrin.yaml "
           "lf_intelligen_a/b. data/evidence/lactoferrin.yaml lf_cost_intelligen2026_case_a_ufdf and _case_b_cex.")

sheet("Market_context", ["ingredient", "low $/kg protein", "high $/kg protein", "basis", "evidence", "evidence key"],
      [[c["label"], c["lo"], c["hi"], c["when"] or "2015-2025, 2025$", evidence(c["grade"]), c["key"]] for c in R["benchmarks"].get("context", [])],
      [42, 16, 16, 24, 8, 36], note="Protein ingredients for context (report Q1, fig 11). GFI 2025 ranges are nominal; export unit "
                                    "values are deflated to 2025 dollars. data/evidence/prices.yaml.")

CH = R.get("cheese")
if CH:
    rows = []
    for route in CH["routes"]:
        for x in CH["kappa_share"]:
            k = f"{x:g}"
            rows += [[f"{route}, kappa share {k}, kappa {t} g/L", float(t), d["msp_ccf"], CH["blend"][route][k][i], d["feasible"]]
                     for i, (t, d) in enumerate(CH["kap"][route][k].items())]
            rows.append([f"{route}, kappa share {k}: kappa titer for a blend 10% above alpha-s1 alone",
                         CH["kappa_titer_for_10pct"][route][k], None, None, None])
    rows += [[f"alpha-s1, {k}", CH["as1"][k]["design"]["titer"], CH["as1"][k]["msp_ccf"], None, CH["as1"][k]["feasible"]]
             for k in CH["as1"]]
    sheet("Cheese", ["case", "titer g/L", "MSP_CCF $/kg (kappa or alpha-s1)", "blend $/kg", "feasible"], rows, [62, 10, 20, 14, 10],
          note="Rennet-cheese casein: alpha-s1 (base design point, acid route) blended with kappa-casein from its own strain and "
               "plant at each kappa share of a 10 kt/yr casein blend; kappa co-precipitated (acid route, 'kap') or on its own "
               "cation-exchange column ('kap_cex'). Blend = (1 - s) x alpha-s1 + s x kappa (data/pf/scenarios/cheese.yaml).")

FLR = R.get("floor")
if FLR:
    rows = []
    for prod, by in FLR["products"].items():
        for loc, d in by.items():
            f = d["floor"]
            rows.append([f"PF {prod} (floor)", loc, f["substrate_kg"], f["cost"]["substrate"], f["total"] - f["cost"]["substrate"],
                         f["total"], None, f["p_max_kg_m3_h"]])
            rows.append([f"PF {prod} (base case)", loc, d["glucose_kg"], d["glucose_usd"], d["other"], d["msp"], None, None])
            rows[-2] += [None] * 9
            rows[-1] += [None] * 9
    for name, a in FLR["animals"].items():
        for loc, d in a["regions"].items():
            rows.append([f"{a['label']} (farm gate)", loc, None, d["feed"], d["other"], d["total"], d["share"], None,
                         d["feed_low"], d["feed_high"], d["total_low"], d["total_high"], d["alloc"], d["year"],
                         f"feed {evidence(d['grades']['feed'])}, share {evidence(d['grades']['share']) if d['grades']['share'] else '-'}", ", ".join(d["keys"]), None])
    sheet("Floor_vs_feed", ["case", "location", "glucose kg/kg protein", "feedstock $/kg protein", "everything else $/kg",
                            "total $/kg", "feed share of farm cost", "productivity bound kg/m3/h", "feed low", "feed high",
                            "total low", "total high", "share of farm value charged (co-product credit)", "year", "evidence",
                            "evidence keys (data/evidence/feed.yaml)", ""], rows,
          [40, 12, 14, 14, 14, 12, 14, 16, 10, 10, 10, 10, 14, 8, 16, 60, 2],
          note="Metabolic floor (src/pftea/floor.py), each product's base case split into glucose and the rest, and the incumbent "
               "animals' feed bill and farm-gate cost per kg of edible protein (data/evidence/feed.yaml; our derivation). Report section "
               "'Feedstock against feed'.")

# ---------------------------------------------------------------- data
with (ROOT / "data/titers.csv").open() as fh:
    t = list(csv.reader(fh))
sheet("Titers", t[0], t[1:], [14, 14, 10, 10, 8, 10, 12, 20, 6, 50, 20, 12, 8, 8, 50])
for f in ("hosts", "dsp", "engineering", "prices", "placeholders", "milk_egg", "lactoferrin", "casein", "ovomucoid", "albumin", "alac", "heme",
          "feed", "kinetic", "transferrin", "binder"):
    E = yaml.safe_load((ROOT / f"data/evidence/{f}.yaml").read_text())
    rows = [[e.get("key"), num(e.get("value")) if not isinstance(e.get("value"), (dict, list)) else json.dumps(e.get("value")),
             num(e.get("low")), num(e.get("high")), e.get("unit", ""), evidence(e.get("grade", "")), e.get("source", ""),
             str(e.get("doi_or_url", "")), str(e.get("locator", "")), str(e.get("quote", "")), str(e.get("note", ""))]
            for e in E]
    sheet(f"Evidence_{f}", ["key", "value", "low", "high", "unit", "evidence", "source", "doi/url", "locator", "quote", "note"],
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
op_items = [k for k in b["per_kg"] if k not in ("capital charge", "maintenance", "insurance")]
r = 10
for k in op_items:
    ws.cell(r, 1, k).font = BODY
    c = ws.cell(r, 2, b["per_kg"][k] * inputs[0][1])
    c.font = BLUE
    c.comment = Comment("Source: results/analyses.json base.blg.per_kg x annual output", "pf-tea")
    r += 1
for k, frac, src in (("maintenance", "maintenance_frac_tci", "Humbird 2021 p.46: 4% of TCI"),
                     ("insurance", "insurance_tax_frac_tci", "Humbird 2021 p.46: 5% of TCI")):
    ws.cell(r, 1, f"{k} (fraction of TCI in column C)").font = BODY
    cf = ws.cell(r, 3, float(P["finance"][frac]["value"]))
    cf.font = BLUE
    cf.comment = Comment(f"Source: {src}", "pf-tea")
    ws.cell(r, 2, f"=C{r}*B5").font = BODY          # live: follows TCI
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
