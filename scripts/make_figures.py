"""Report figures from results/analyses.json -> docs/figures/*.png (light theme, 200 dpi).

Palette: dataviz reference palette (validated with its script, light mode): categorical
slots in fixed order; ordinal blue ramp for evidence grades; neutral inks for chrome.
Rules: one y-axis per chart, thin lines, >=8 px markers, direct labels plus a legend for
>=2 series, text in ink colours (never the series colour). No numbers are typed here:
everything is read from results/analyses.json.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pftea.labels import label as plabel  # noqa: E402

R = json.loads((ROOT / "results/analyses.json").read_text())
OUT = ROOT / "docs/figures"
OUT.mkdir(parents=True, exist_ok=True)

SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]
ORD = {"A": "#104281", "B": "#1c5cab", "C": "#2a78d6", "D": "#5598e7", "E": "#86b6ef", "": "#c3c2b7"}
BAND = {"whey": "#e3edf9", "egg": "#fbe6dc"}
PROD = {"blg": "beta-lactoglobulin (whey protein)", "ova": "ovalbumin (egg-white protein)"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9, "axes.facecolor": SURF, "figure.facecolor": SURF, "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK, "legend.frameon": False,
    "lines.linewidth": 2.0, "savefig.dpi": 200, "savefig.bbox": "tight", "text.parse_math": False,
})


def save(fig, name):
    fig.savefig(OUT / name)
    plt.close(fig)
    print("wrote", name)


def money(axis):
    axis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}" if x >= 1 else f"${x:.1f}"))


def plain(axis, ticks):
    axis.set_major_locator(matplotlib.ticker.FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
    axis.set_minor_formatter(NullFormatter())


def feasible_part(xs, ys, feas):
    """Leading feasible run of a curve (feasibility is lost once, as titer rises)."""
    xs, ys, feas = np.array(xs, float), np.array(ys, float), np.array(feas, bool)
    k = len(feas) if feas.all() else int(np.argmin(feas))
    return xs[:k], ys[:k], k


# ------------------------------------------------------------------ Fig 1 cost vs titer
inc = R["benchmarks"]["incumbents"]
marks = R["benchmarks"]["titer_markers"]
fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.0), sharey=True)
for ax, prod in zip(axes, ("blg", "ova")):
    c = R["cost_vs_titer"][prod]
    T = np.array(c["titers"], float)
    name = "whey" if prod == "blg" else "egg"
    lo, hi = inc[name]["band"]
    ax.axhspan(lo, hi, color=BAND[name], zorder=0, lw=0)
    y0, y1 = inc[name]["years"]
    ax.text(2.1, lo * 1.07, f"{inc[name]['label']}, export unit values\n{y0}-{y1}: ${lo:.0f}-{hi:.0f}/kg protein",
            fontsize=7, color=INK2, va="bottom", ha="left")
    for s_ in inc[name]["spot"][:1]:
        ax.axhline(s_["usd_kg_protein"], color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)
        ax.text(165, s_["usd_kg_protein"] * 1.05, f"whey spot {s_['year']}: ${s_['usd_kg_protein']:.0f}",
                fontsize=7, color=INK2, va="bottom", ha="right")
    for k, tp in enumerate(c["t_prods"]):
        x, y, n_ok = feasible_part(T, c["msp"][k], c["feasible"][k])
        cx, cy = c.get("ceiling", [None] * 3)[k], c.get("msp_at_ceiling", [None] * 3)[k]
        if cx and cy and (len(x) == 0 or cx > x[-1]):
            x, y = np.append(x, cx), np.append(y, cy)
        lab_ = f"{tp} h production (O2 limit at {cx:.0f} g/L)" if cx else f"{tp} h production"
        ax.plot(x, y, color=CAT[k], marker="o", ms=3.5, label=lab_, zorder=3)
        if cx and cy:
            ax.plot([cx], [cy], marker="D", ms=6, color=CAT[k], mec=SURF, mew=1.2, zorder=4)
    x, y, _ = feasible_part(T, c["light_72h"], c["light_72h_feasible"])
    cx, cy = c.get("ceiling", [None, None, None])[1], c.get("light_72h_at_ceiling")
    if cx and cy:
        x, y = np.append(x, cx), np.append(y, cy)
    ax.plot(x, y, color=CAT[1], ls=(0, (3, 2)), lw=1.4, label="72 h production, light capital", zorder=3)
    ax.plot([], [], marker="D", ms=6, color=INK2, ls="none", label="cheapest feasible design at that time")
    for t, lab in marks[prod]:
        ax.axvline(t, color=AXIS, lw=0.8, zorder=0)
        ax.text(t, 1.012, f"{lab}: {t:g} g/L", transform=ax.get_xaxis_transform(), rotation=60, ha="left",
                va="bottom", fontsize=6.6, color=INK2, rotation_mode="anchor")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1.8, 170); ax.set_ylim(3, 700)
    plain(ax.xaxis, [2, 5, 10, 20, 50, 100, 150])
    money(ax.yaxis)
    ax.set_xlabel("titer at harvest (g/L)")
    ax.text(160, 560, PROD[prod], ha="right", va="top", fontsize=10, fontweight="bold", color=INK)
axes[0].set_ylabel("minimum selling price ($/kg target protein, 2025)")
h, l_ = axes[0].get_legend_handles_labels()
fig.legend(h, l_, loc="lower center", ncol=3, fontsize=7.2, bbox_to_anchor=(0.5, -0.06))
fig.text(0.01, -0.13, "10 kt/yr, US Midwest, 200 m3 fermenters at 80 g/L cells, dried concentrate. Each line ends at the highest "
         "titer the fermenter can reach in that production time (O2 transfer or heat removal); legend labels are for BLG.\n"
         "Price bands: UN Comtrade and Eurostat export unit values of whey protein >80% (US, EU) and dried egg albumin (EU), "
         "per kg protein (80% and 78% protein). Top axis: published and claimed titers (data/titers.csv).",
         fontsize=7, color=MUTED)
save(fig, "fig1_cost_vs_titer.png")

# ------------------------------------------------------------------ Fig 2 bridge (horizontal waterfall)
steps = [b for b in R["bridge"] if b["kind"] == "step"]
variants = [b for b in R["bridge"] if b["kind"] == "variant"]
rows, prev = [], 0.0
for i, s in enumerate(steps):
    if i == 0:
        rows.append((s["step"], 0.0, s["msp"], "total"))
    else:
        rows.append((s["step"], prev, s["msp"], "up" if s["msp"] > prev else "down"))
    prev = s["msp"]
base_total = prev
rows.append(("our base case: BLG concentrate, 10 kt/yr, US", 0.0, base_total, "total"))
for v_ in variants:
    rows.append((f"variant: {v_['step']}", base_total, v_["msp"], "variant"))
fig, ax = plt.subplots(figsize=(9.5, 5.4))
n = len(rows)
for i, (lab, a, b, kind) in enumerate(rows):
    y = n - 1 - i
    col = {"total": INK2, "up": CAT[1], "down": CAT[2], "variant": AXIS}[kind]
    ax.barh(y, b - a, left=a, color=col, height=0.62)
    txt = f"${b:.1f}" if kind == "total" else f"{'+' if b > a else '-'}${abs(b - a):.1f}"
    ax.text(max(a, b) + 0.4, y, txt + (f"  (= ${b:.1f})" if kind == "variant" else ""), va="center", fontsize=8, color=INK)
    if i > 0 and kind in ("up", "down"):
        ax.plot([a, a], [y + 1 - 0.31, y + 0.31], color=MUTED, lw=0.7)
ax.set_yticks(range(n))
ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=7.8)
money(ax.xaxis)
ax.set_xlabel("minimum selling price ($/kg target protein, 2025)")
ax.set_title(f"From a ${steps[0]['msp']:.0f}/kg crude enzyme to a ${base_total:.0f}/kg food protein: what each change adds")
ax.grid(axis="y", visible=False)
ax.set_xlim(0, max(r[2] for r in rows) * 1.18)
ax.legend(handles=[Patch(color=CAT[1], label="adds cost"), Patch(color=CAT[2], label="removes cost"),
                   Patch(color=INK2, label="total"), Patch(color=AXIS, label="product variant (from the base case)")],
          fontsize=7.5, loc="upper right")
fig.text(0.01, -0.03, "Changes are applied cumulatively, top to bottom; the size of each step depends on the order. "
         "Start: NREL 2011 on-site cellulase, re-priced to 2025 with an NREL-style capital estimate.",
         fontsize=7, color=MUTED)
save(fig, "fig2_bridge.png")

# ------------------------------------------------------------------ Fig 3 design space
tps = np.array(R["required_t_prods"], float)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), sharey=True)
for ax, prod in zip(axes, ("blg", "ova")):
    ceil = np.array([c if c else np.nan for c in R["titer_ceiling"][prod]], float)
    ax.fill_between(tps, ceil, 400, color="#efeee9", zorder=0, lw=0)
    ax.plot(tps, ceil, color=INK2, lw=1.2, zorder=2)
    ax.text(tps[-1] - 1, ceil[-1] * 1.12, "O2/heat limit, 200 m3 fermenter at 80 g/L cells", fontsize=7, color=INK2,
            va="bottom", ha="right")
    for k, tg in enumerate(("10", "20", "50")):
        for basis, ls in (("humbird", "-"), ("light", (0, (3, 2)))):
            rows_ = R["required"][f"{prod}/{basis}"][tg]
            xs = [t for t, r_ in zip(tps, rows_) if r_["titer"]]
            ys = [r_["titer"] for r_ in rows_ if r_["titer"]]
            if xs:
                ax.plot(xs, ys, color=CAT[k], ls=ls, lw=1.8, marker="o", ms=4, zorder=3,
                        label=f"${tg}/kg, {'Humbird' if basis == 'humbird' else 'light'} capital")
    if prod == "ova":
        ax.axhline(50, color=CAT[1], lw=0.9, ls=(0, (1, 2)))
        ax.text(31, 46, "OVA practical solubility, 50 g/L (Intelligen's assumption)", fontsize=6.8, color=INK2, va="top")
    ax.set_yscale("log")
    ax.set_ylim(4, 400)
    plain(ax.yaxis, [5, 10, 20, 50, 100, 200, 400])
    ax.set_xlim(30, 125)
    ax.set_xlabel("production phase (h)")
    ax.set_title(PROD[prod])
axes[0].set_ylabel("titer needed (g/L)")
h, l_ = axes[0].get_legend_handles_labels()
fig.legend(h, l_, loc="lower center", ncol=4, fontsize=7.2, bbox_to_anchor=(0.5, -0.07))
missing = [f"${tg}/kg ({b})" for tg in ("10", "20", "50") for b in ("humbird", "light")
           if not any(r_["titer"] for r_ in R["required"][f"blg/{b}"][tg])]
fig.text(0.01, -0.12, "Lines: titer at which the minimum selling price equals the target (10 kt/yr, US), searched only "
         "below the O2/heat ceiling; grey: designs the fermenter cannot run."
         + (f"\nNot reachable at any production time with 80 g/L cells and base yield: {', '.join(missing)}." if missing else ""),
         fontsize=7, color=MUTED)
save(fig, "fig3_required_titer.png")

# ------------------------------------------------------------------ Fig 4 breakdown
groups = [("capital charge", ["capital charge"]), ("maintenance + insurance", ["maintenance", "insurance & tax"]),
          ("labour", ["labour"]), ("glucose", ["glucose"]),
          ("other raw materials", ["ammonia", "salts & other media", "DSP chemicals"]),
          ("utilities", ["electricity", "natural gas & steam", "water & wastewater"]),
          ("membranes + waste", ["membranes", "biomass disposal"])]
rows = [("base case, BLG (30 g/L)", R["base"]["blg"]), ("base case, OVA (30 g/L)", R["base"]["ova"]),
        ("industry benchmark, BLG (42 g/L)", R["scenarios"]["industry/blg"]),
        ("industry benchmark, OVA (42 g/L)", R["scenarios"]["industry/ova"])]
for k in ("blg/humbird", "ova/humbird", "blg/light", "ova/light"):
    if k in R["physical_limit"]:
        prod, basis = k.split("/")
        d = R["physical_limit"][k]
        rows.append((f"physical limit, {prod.upper()} ({d['titer']:g} g/L){', light capital' if basis == 'light' else ''}", d))
XCUT = 36
fig, ax = plt.subplots(figsize=(9.5, 4.8))
for i, (lab, d) in enumerate(rows[::-1]):
    left = 0
    for g, (gname, keys) in enumerate(groups):
        w = sum(d["per_kg"].get(k2, 0) for k2 in keys)
        ax.barh(i, w, left=left, color=CAT[g], height=0.62, edgecolor=SURF, linewidth=1.5,
                label=gname if i == 0 else None)
        left += w
    ax.text(min(left, XCUT - 4) + 0.4, i, f"${left:.1f}" + (" (bar cut)" if left > XCUT else ""), va="center",
            fontsize=8, color=INK)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=8)
money(ax.xaxis)
ax.set_xlim(0, XCUT)
ax.set_xlabel("$/kg target protein, 2025 (capital charge 14.6%/yr of total capital investment)")
ax.set_title("What the cost is made of, from today's benchmarks to the physical floor")
ax.legend(fontsize=7.5, ncol=4, loc="upper center", bbox_to_anchor=(0.45, -0.14))
ax.grid(axis="y", visible=False)
save(fig, "fig4_breakdown.png")

# ------------------------------------------------------------------ Fig 5 tornado
tor = [t for t in R["tornado"] if t["swing"] > 0.05][:14]
base_v = tor[0]["base"]
fig, ax = plt.subplots(figsize=(8.8, 5.2))
for i, t in enumerate(tor[::-1]):
    col = ORD.get(t["grade"], ORD[""])
    for val, par, feas in ((t["msp_low"], t["low"], t.get("feasible_low", True)),
                           (t["msp_high"], t["high"], t.get("feasible_high", True))):
        ax.barh(i, val - base_v, left=base_v, color=col, height=0.6, hatch=None if feas else "////",
                edgecolor=SURF if feas else INK2, linewidth=0.0 if feas else 0.5)
        ax.text(val + (0.25 if val >= base_v else -0.25), i, f"{par:g}" + ("" if feas else "*"),
                ha="left" if val >= base_v else "right", va="center", fontsize=6.8, color=INK2)
ax.axvline(base_v, color=INK, lw=1)
ax.set_yticks(range(len(tor)))
ax.set_yticklabels([plabel(t["path"]) for t in tor[::-1]], fontsize=7.8)
money(ax.xaxis)
lo_all = min(min(t["msp_low"], t["msp_high"]) for t in tor)
hi_all = max(max(t["msp_low"], t["msp_high"]) for t in tor)
ax.set_xlim(lo_all - 3, hi_all + 3)
ax.legend(handles=[Patch(color=ORD[g], label=f"grade {g}") for g in "ABCDE"], fontsize=7.5, ncol=5,
          loc="upper center", bbox_to_anchor=(0.45, -0.1))
ax.set_title(f"Industry-benchmark BLG (${base_v:.1f}/kg): one parameter at a time, coloured by evidence grade")
ax.set_xlabel("$/kg target protein; numbers at the bar ends are the parameter values tested")
ax.grid(axis="y", visible=False)
if any(not (t.get("feasible_low", True) and t.get("feasible_high", True)) for t in tor):
    fig.text(0.01, -0.07, "* hatched: that parameter value breaks the O2/heat limit at the benchmark titer and "
             "production time; its cost is not achievable as designed.", fontsize=7, color=MUTED)
save(fig, "fig5_tornado.png")

# ------------------------------------------------------------------ Fig 6 scale
sc_ = R["scale"]
fig, ax = plt.subplots(figsize=(7.4, 4.2))
styles = {"US, Humbird capital": (CAT[0], "-"), "EU, Humbird capital": (CAT[1], "-"),
          "US, light capital": (CAT[0], (0, (3, 2))), "EU, light capital": (CAT[1], (0, (3, 2)))}
X = np.array(sc_["outputs"]) / 1000
for lab, ys in sc_["curves"].items():
    col, ls = styles[lab]
    ax.plot(X, ys, color=col, ls=ls, marker="o", ms=4, label=lab)
    ax.text(X[-1] * 1.08, ys[-1], f"{lab}: ${ys[-1]:.1f}", fontsize=7.2, color=INK2, va="center")
ax.set_xscale("log")
plain(ax.xaxis, [1, 2.5, 5, 10, 25, 50, 100])
ax.set_xlabel("plant output (kt target protein per year)")
ax.set_ylabel("$/kg target protein, 2025")
money(ax.yaxis)
ax.set_xlim(0.85, 420)
ax.set_title("Industry-benchmark BLG: plant scale and siting")
ax.legend(fontsize=7.5, loc="upper right")
fig.text(0.01, -0.04, "Above ~10 kt/yr the plant adds 200 m3 fermenters rather than larger ones, so fermentation "
         "stops getting cheaper per kg; only downstream and utilities keep scaling.", fontsize=7, color=MUTED)
save(fig, "fig6_scale.png")

# ------------------------------------------------------------------ Fig 7 Monte Carlo intervals
mc = R["monte_carlo"]
fig, ax = plt.subplots(figsize=(8, 3.0))
order = ["academic/ova", "academic/blg", "industry/ova", "industry/blg"]
for i, k in enumerate(order):
    d = mc[k]
    col = CAT[0 if "blg" in k else 1]
    ms = np.array(d["msp"]); fe = np.array(d.get("feasible", [True] * len(ms)), bool)
    jit = (np.random.default_rng(0).random(len(ms)) - 0.5) * 0.25
    ax.scatter(ms[fe], i + jit[fe], s=5, color=col, alpha=0.25, lw=0, zorder=2)
    ax.plot([d["p10"], d["p90"]], [i, i], color=col, lw=3, solid_capstyle="round", zorder=3)
    ax.plot(d["p50"], i, "o", color=col, ms=8, mec=SURF, mew=2, zorder=4)
    ax.text(np.nanmax(ms[fe]) * 1.12, i, f"median ${d['p50']:.0f}, p10-p90 ${d['p10']:.0f}-{d['p90']:.0f}; "
            f"{100 * d['feasible_frac']:.0f}% of {d.get('n', len(ms))} draws feasible", va="center", fontsize=7.2,
            color=INK2)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([{"academic": "academic best", "industry": "industry benchmark"}[k.split("/")[0]] + ", "
                    + k.split("/")[1].upper() for k in order], fontsize=8)
ax.set_xscale("log"); money(ax.xaxis)
ax.set_xlim(8, 4000)
ax.set_title("Uncertainty from the evidence ranges (feasible plants only)")
ax.set_xlabel("$/kg target protein, 2025 (dots: individual feasible draws)")
ax.grid(axis="y", visible=False)
save(fig, "fig7_montecarlo.png")

# ------------------------------------------------------------------ Fig 0 flowsheet (base case, per kg BLG)
from matplotlib.patches import FancyBboxPatch  # noqa: E402

b0 = R["base"]["blg"]
ph, de = b0["physical"], b0["design"]
fig, ax = plt.subplots(figsize=(10.5, 3.9))
ax.set_xlim(0, 105); ax.set_ylim(0, 40); ax.axis("off")


def box(x, y, w, h, title, sub, fill="#eef3fb"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fill, ec=AXIS, lw=0.8))
    ax.text(x + w / 2, y + h - 2.2, title, ha="center", va="top", fontsize=8, color=INK, fontweight="bold")
    ax.text(x + w / 2, y + h - 6.4, sub, ha="center", va="top", fontsize=6.6, color=INK2, linespacing=1.35)


def arrow(x0, y0, x1, y1, text="", dy=1.2, ha="center"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.9))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + dy, text, ha=ha, va="bottom", fontsize=6.6, color=INK2)


n_ferm = int(de["N_prod_int"])
box(1, 16, 14, 14, "Media and seed", "glucose 50 wt% feed\nNH3, salts, antifoam\nsterilised; 3 seed stages")
box(21, 16, 19, 14, "Production fermenters",
    f"{n_ferm} x 200 m3 stirred tanks\ngrowth {de['t_growth_h']:.0f} h + production {de['t_total_h'] - de['t_growth_h']:.0f} h\n"
    f"{de['X_end']:.0f} g/L cells, {de['titer']:.0f} g/L protein\nO2 transfer {de['otr_max']:.0f} mol/m3/h (cap)")
box(46, 16, 14, 14, "Cell removal", f"dilute to 45 g/L cells\n2-stage disk-stack\ncentrifuges; MF polish\n({de['mf_m2']:,.0f} m2)")
box(66, 16, 14, 14, "Concentration", f"ultrafiltration\n+ diafiltration\n({de['uf_m2']:,.0f} m2)\nconcentration x{de['CF']:.1f}")
box(86, 16, 17, 14, "Spray dryer", f"{de['evap_kg_h']:,.0f} kg/h water\nevaporated\npowder: {100 * de['purity_dry']:.0f}% BLG (dry),\n5% moisture",
    fill="#eaf6f0")
arrow(15.6, 23, 20.4, 23)
arrow(40.6, 23, 45.4, 23)
arrow(60.6, 23, 65.4, 23)
arrow(80.6, 23, 85.4, 23)
arrow(94.5, 15.4, 94.5, 8.5)
ax.text(94.5, 7.8, f"1 kg BLG in {1 / (de['purity_dry'] * 0.95):.2f} kg powder\n"
        f"overall recovery {100 * de['recovery']:.0f}%", ha="center", va="top", fontsize=7, color=INK)
arrow(30.5, 36.5, 30.5, 30.6)
ax.text(30.5, 37.2, f"air: {ph['o2_kg']:.1f} kg O2 per kg BLG", ha="center", va="bottom", fontsize=6.8, color=INK2)
arrow(8, 36.5, 8, 30.6)
ax.text(8, 37.2, f"glucose: {ph['glucose_kg']:.1f} kg per kg BLG", ha="center", va="bottom", fontsize=6.8, color=INK2)
arrow(53, 15.4, 53, 8.5)
ax.text(53, 7.8, f"spent cells: {ph['cells_kg']:.1f} kg dry\nper kg BLG", ha="center", va="top", fontsize=6.8, color=INK2)
arrow(73, 15.4, 73, 8.5)
ax.text(73, 7.8, "permeate: salts, sugars,\nsmall molecules", ha="center", va="top", fontsize=6.8, color=INK2)
arrow(36, 30.6, 42, 36.5)
ax.text(43, 37.2, "CO2 + water vapour", ha="left", va="bottom", fontsize=6.8, color=INK2)
ax.text(1, 3.2, f"Utilities: air compressors, chillers (peak heat {de['heat_peak_kW_m3']:.0f} kW/m3), cooling tower, boiler, "
        f"water treatment. Electricity {ph['electricity_kWh']:.1f} kWh and natural gas {ph['natural_gas_MJ']:.0f} MJ per kg BLG. "
        f"{de['fte']:.0f} staff.", fontsize=7, color=INK2)
ax.text(1, 0.4, "Base case: K. phaffii, 30 g/L beta-lactoglobulin, 10 kt/yr of protein, US Midwest. "
        "All numbers from results/analyses.json.", fontsize=7, color=MUTED)
save(fig, "fig0_flowsheet.png")
