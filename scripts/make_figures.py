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
        lab_ = f"{tp} h production (ceiling {cx:.0f} g/L)" if cx else f"{tp} h production"
        ax.plot(x, y, color=CAT[k], marker="o", ms=3.5, label=lab_, zorder=3)
        if cx and cy:
            ax.plot([cx], [cy], marker="D", ms=6, color=CAT[k], mec=SURF, mew=1.2, zorder=4)
    x, y, _ = feasible_part(T, c["light_72h"], c["light_72h_feasible"])
    cx, cy = c.get("ceiling", [None, None, None])[1], c.get("light_72h_at_ceiling")
    if cx and cy:
        x, y = np.append(x, cx), np.append(y, cy)
    ax.plot(x, y, color=CAT[1], ls=(0, (3, 2)), lw=1.4, label="72 h production, design-report capital", zorder=3)
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
fig.text(0.01, -0.13, f"10 kt/yr, US Midwest, 200 m3 fermenters, {R['base']['blg']['design']['X_end']:.0f} g/L cells at harvest, glucose fed "
         "at 500 g/L, dried concentrate. Each line ends at the highest feasible titer in that production time (O2 transfer, heat "
         "removal, minimum fill, specific productivity); legend labels are for BLG.\n"
         f"Price bands: UN Comtrade and Eurostat export unit values of whey protein >80% (US, EU) and dried egg albumin (EU), "
         f"per kg protein ({inc['whey']['protein_frac']:.0%} and {inc['egg']['protein_frac']:.1%} protein), 2025 dollars. "
         "Top axis: published and claimed titers (data/titers.csv).", fontsize=7, color=MUTED)
save(fig, "fig1_cost_vs_titer.png")

# ------------------------------------------------------------------ Fig 2 bridge (horizontal waterfall)
steps = [b for b in R["bridge"] if b["kind"] == "step"]
variants = [b for b in R["bridge"] if b["kind"] == "variant"]
HARD = ("OUR", "heat", "reachable", "volume", "initial fill", "solubility", "energetic ceiling", "specific productivity",
        "did not reach")
infeasible = lambda b: any(k in f_ for f_ in b.get("flags", []) for k in HARD)   # noqa: E731
rows, prev = [], 0.0
for i, s in enumerate(steps):
    lab = s["step"] + (" \u2020" if infeasible(s) else "")
    if i == 0:
        rows.append((lab, 0.0, s["msp"], "total"))
    else:
        rows.append((lab, prev, s["msp"], "up" if s["msp"] > prev else "down"))
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
         "Start: NREL 2011 on-site cellulase, re-priced to 2025 with an NREL-style capital estimate."
         + ("\n\u2020 this step's design breaks a feasibility limit (NREL's design implies a specific productivity "
            "above our 40 mg/g/h ceiling); its cost is shown for the walk only." if any(infeasible(s) for s in steps) else ""),
         fontsize=7, color=MUTED)
save(fig, "fig2_bridge.png")

# ------------------------------------------------------------------ Fig 3 design space
tps = np.array(R["required_t_prods"], float)
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), sharey=True)
for ax, prod in zip(axes, ("blg", "ova")):
    ceil = np.array([c if c else np.nan for c in R["titer_ceiling"][prod]], float)
    ax.fill_between(tps, ceil, 400, color="#efeee9", zorder=0, lw=0)
    ax.plot(tps, ceil, color=INK2, lw=1.2, zorder=2)
    ax.text(tps[0] + 1, 330, "grey: above the feasibility ceiling (solid line; with\na 500 g/L glucose feed, set by the minimum starting volume)\n"
            "dotted: the ceiling with a 600 g/L feed (Shemesh 2024)",
            fontsize=6.6, color=INK2, va="top", ha="left", linespacing=1.3)
    cf = np.array([c if c else np.nan for c in R.get("titer_ceiling_feed600", {}).get(prod, [])], float)
    if cf.size:
        ax.plot(tps, cf, color=INK2, lw=0.9, ls=(0, (1, 2)), zorder=2)
    for k, tg in enumerate(("10", "20", "50")):
        for basis, ls in (("humbird", "-"), ("light", (0, (3, 2)))):
            rows_ = R["required"][f"{prod}/{basis}"][tg]
            xs = [t for t, r_ in zip(tps, rows_) if r_["titer"]]
            ys = [r_["titer"] for r_ in rows_ if r_["titer"]]
            if xs:
                ax.plot(xs, ys, color=CAT[k], ls=ls, lw=1.8, marker="o", ms=4, zorder=3,
                        label=f"${tg}/kg, {'price-anchored' if basis == 'humbird' else 'design-report'} capital")
    if prod == "ova":
        ax.axhline(50, color=CAT[1], lw=0.9, ls=(0, (1, 2)))
        ax.text(124, 50 * 0.97, "50 g/L:\nIntelligen's\nassumed\nsolubility\n(sensitivity)", fontsize=6.4, color=INK2,
                va="top", ha="left", linespacing=1.2)
    ax.set_yscale("log")
    ax.set_ylim(4, 400)
    plain(ax.yaxis, [5, 10, 20, 50, 100, 200, 400])
    ax.set_xlim(30, 138 if prod == "ova" else 125)
    ax.set_xlabel("production phase (h)")
    ax.set_title(PROD[prod])
axes[0].set_ylabel("titer needed (g/L)")
h, l_ = axes[0].get_legend_handles_labels()
fig.legend(h, l_, loc="lower center", ncol=4, fontsize=7.2, bbox_to_anchor=(0.5, -0.07))
missing = [f"${tg}/kg ({'price-anchored' if b == 'humbird' else 'design-report'} capital)" for tg in ("10", "20", "50")
           for b in ("humbird", "light") if not any(r_["titer"] for r_ in R["required"][f"blg/{b}"][tg])]
fig.text(0.01, -0.12, "Lines: titer at which the minimum selling price equals the target (10 kt/yr, US), searched only "
         "below the feasibility ceiling; grey: designs the fermenter cannot run."
         + (f"\nNot reachable at any production time with the base cells and yield: {', '.join(missing)}." if missing else ""),
         fontsize=7, color=MUTED)
save(fig, "fig3_required_titer.png")

# ------------------------------------------------------------------ Fig 4 breakdown
groups = [("capital charge", ["capital charge"]), ("maintenance + insurance", ["maintenance", "insurance"]),
          ("labour", ["labour"]), ("glucose", ["glucose"]),
          ("other raw materials", ["ammonia", "salts & other media", "DSP chemicals"]),
          ("utilities", ["electricity", "natural gas & steam", "water & wastewater"]),
          ("membranes, resin + waste", ["membranes", "chromatography resin", "biomass disposal"])]
rows = [("base case, BLG (30 g/L)", R["base"]["blg"]), ("base case, OVA (30 g/L)", R["base"]["ova"]),
        ("industry benchmark, BLG (42 g/L)", R["scenarios"]["industry/blg"]),
        ("industry benchmark, OVA (42 g/L)", R["scenarios"]["industry/ova"])]
for k in ("blg/humbird", "ova/humbird", "blg/light", "ova/light"):
    if k in R["physical_limit"]:
        prod, basis = k.split("/")
        d = R["physical_limit"][k]
        rows.append((f"physical limit, {prod.upper()} ({d['titer']:.0f} g/L){', design-report capital' if basis == 'light' else ''}", d))
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
tor = [t for t in R["tornado"] if t["swing"] > 0.05][:16]
base_v = tor[0]["base"]
ORD["structural"] = INK2
fig, ax = plt.subplots(figsize=(8.8, 5.6))


def tlabel(par, trunc):
    txt = {"design-report (NREL-style)": "design-report", "price-anchored (Humbird)": "price-anchored",
           "vendor quote (base)": "vendor quote", "aseptic cell-culture STR (ACCE)": "aseptic STR"}.get(par, None)
    txt = txt or (f"{par:.3g}" if isinstance(par, float) else f"{par}")
    return txt + (" \u2020" if trunc else "")


for i, t in enumerate(tor[::-1]):
    col = ORD.get(t["grade"], ORD[""])
    for val, par, trunc in ((t["msp_low"], t["low"], t.get("truncated_low", False)),
                            (t["msp_high"], t["high"], t.get("truncated_high", False))):
        ax.barh(i, val - base_v, left=base_v, color=col, height=0.6, edgecolor=SURF, linewidth=0.0)
        other = t["msp_high"] if val == t["msp_low"] else t["msp_low"]
        right = val > base_v + 0.05 or (abs(val - base_v) <= 0.05 and other < base_v)
        ax.text(val + (0.25 if right else -0.25), i, tlabel(par, trunc),
                ha="left" if right else "right", va="center", fontsize=6.8, color=INK2)
ax.axvline(base_v, color=INK, lw=1)
ax.set_yticks(range(len(tor)))
ax.set_yticklabels([plabel(t["path"]) for t in tor[::-1]], fontsize=7.8)
money(ax.xaxis)
lo_all = min(min(t["msp_low"], t["msp_high"]) for t in tor)
hi_all = max(max(t["msp_low"], t["msp_high"]) for t in tor)
ax.set_xlim(lo_all - 3, hi_all + 3)
ax.legend(handles=[Patch(color=ORD[g], label=f"grade {g}") for g in "ABCDE"]
          + [Patch(color=ORD["structural"], label="convention")], fontsize=7.5, ncol=6,
          loc="upper center", bbox_to_anchor=(0.45, -0.1))
ax.set_title(f"Industry-benchmark BLG (${base_v:.1f}/kg): one parameter at a time, coloured by evidence grade")
ax.set_xlabel("$/kg target protein; numbers at the bar ends are the parameter values tested")
ax.grid(axis="y", visible=False)
if any(t.get("truncated_low") or t.get("truncated_high") for t in tor):
    fig.text(0.01, -0.07, "\u2020 the end of the evidence range breaks a physical limit at the benchmark titer and production "
             "time; the bar stops at the last feasible value shown.", fontsize=7, color=MUTED)
save(fig, "fig5_tornado.png")

# ------------------------------------------------------------------ Fig 6 scale
sc_ = R["scale"]
fig, ax = plt.subplots(figsize=(7.4, 4.2))
styles = {"US, price-anchored": (CAT[0], "-"), "EU, price-anchored": (CAT[1], "-"),
          "US, design-report": (CAT[0], (0, (3, 2))), "EU, design-report": (CAT[1], (0, (3, 2)))}
NAMES = {"US, price-anchored": "US, price-anchored capital", "EU, price-anchored": "EU (NL), price-anchored capital",
         "US, design-report": "US, design-report capital", "EU, design-report": "EU (NL), design-report capital"}
X = np.array(sc_["outputs"]) / 1000
for lab, ys in sc_["curves"].items():
    col, ls = styles[lab]
    ax.plot(X, ys, color=col, ls=ls, marker="o", ms=4, label=NAMES[lab])
    ax.text(X[-1] * 1.08, ys[-1], f"{NAMES[lab]}: ${ys[-1]:.1f}", fontsize=7.2, color=INK2, va="center")
ax.set_xscale("log")
plain(ax.xaxis, [1, 2.5, 5, 10, 25, 50, 100])
ax.set_xlabel("plant output (kt target protein per year)")
ax.set_ylabel("$/kg target protein, 2025")
money(ax.yaxis)
ax.set_xlim(0.85, 900)
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
    if d.get("base"):
        ax.plot(d["base"], i, marker="|", ms=14, mew=2, color=INK, zorder=5)
    ax.text(np.nanmax(ms[fe]) * 1.12, i, f"median ${d['p50']:.0f}, p10-p90 ${d['p10']:.0f}-{d['p90']:.0f}; "
            f"{100 * d['feasible_frac']:.0f}% of {d.get('n', len(ms))} draws feasible", va="center", fontsize=7.2,
            color=INK2)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([{"academic": "academic best", "industry": "industry benchmark"}[k.split("/")[0]] + ", "
                    + k.split("/")[1].upper() for k in order], fontsize=8)
ax.set_xscale("log"); money(ax.xaxis)
ax.set_xlim(8, 4000)
ax.set_title("Uncertainty from the evidence ranges (feasible plants only)")
ax.set_xlabel("$/kg target protein, 2025 (dots: individual feasible draws; black tick: the scenario's own value)")
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
box(1, 16, 14, 14, "Media and seed", "glucose feed 500 g/L\nNH3, salts, antifoam\nsterilised; 3 seed stages")
box(21, 16, 19, 14, "Production fermenters",
    f"{n_ferm} x 200 m3 stirred tanks\ngrowth {de['t_growth_h']:.0f} h + production {de['t_total_h'] - de['t_growth_h']:.0f} h\n"
    f"{de['X_end']:.0f} g/L cells, {de['titer']:.0f} g/L protein\nO2 transfer {de['otr_max']:.0f} mol/m3/h (cap)")
box(46, 16, 14, 14, "Cell removal", f"dilute to 45 g/L cells\n2-stage disk-stack\ncentrifuges; MF polish\n({de['mf_m2']:,.0f} m2)")
box(66, 16, 14, 14, "Concentration", f"ultrafiltration\n+ diafiltration\n({de['uf_m2']:,.0f} m2)\nto {100 * de['dryer_inlet_solids']:.0f}% solids")
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

# ------------------------------------------------------------------ Fig 8 milk and egg equivalents
eqv = R["equivalents"]
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
for ax, (name, prod) in zip(axes, (("milk", "blg"), ("egg", "ova"))):
    src = eqv["sources"][name]
    c = R["cost_vs_titer"][prod]
    k72 = c["t_prods"].index(72)
    T, y, _ = feasible_part(c["titers"], c["msp"][k72], c["feasible"][k72])
    cx, cy = c["ceiling"][k72], c["msp_at_ceiling"][k72]
    if cx and cy:
        T, y = np.append(T, cx), np.append(y, cy)
    unit = src["all_protein_g"] / 1000                       # $/kg protein -> $ per litre or per egg
    ax.plot(T, y * unit, color=CAT[0], marker="o", ms=3.5, zorder=3,
            label=f"PF {prod.upper()} replacing the {src['all_protein_g']:.1f} g of "
                  f"{'milk' if name == 'milk' else 'egg-white'} protein, 72 h production")
    for j, (lab, ser) in enumerate(src["prices"].items()):
        vals = list(ser.values())
        yr = max(ser, key=int)                                 # JSON keys are strings
        last = ser[yr]
        ax.axhspan(min(vals), max(vals), color=[BAND["whey"], BAND["egg"], "#e6f4ec"][j % 3], zorder=0, lw=0)
        ax.axhline(last, color=MUTED, lw=0.8, ls=(0, (4, 3)), zorder=1)
        below = name == "egg" and j == 0                     # wholesale sits just under retail: label it below
        ax.text(2.1, last * (0.96 if below else 1.04), f"{lab}: {yr} ${last:.2f}; 2015-{yr} ${min(vals):.2f}-{max(vals):.2f}",
                fontsize=6.6, color=INK2, va="top" if below else "bottom")
    ax.set_xscale("log"); ax.set_yscale("log")
    plain(ax.xaxis, [2, 5, 10, 20, 50, 100])
    ax.set_xlim(1.8, 120)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x_, _: f"${x_:.2f}"))
    ax.set_xlabel("titer at harvest (g/L)")
    ax.set_ylabel(f"$ per {src['per']} (2025)")
    ax.set_title({"milk": "Protein in a litre of milk", "egg": "Egg-white protein in one egg"}[name])
    ax.legend(fontsize=6.8, loc="upper right")
fig.text(0.01, -0.06, "The natural source's price divided by its protein is an upper bound on what that protein is worth: fat, lactose "
         "and yolk carry part of the price, and whey is a by-product of cheese (report section on equivalents). Price-anchored "
         "capital, 10 kt/yr, US; milk and egg prices deflated to 2025 dollars with CPI-U.", fontsize=7, color=MUTED)
save(fig, "fig8_equivalents.png")

# ------------------------------------------------------------------ Fig 9 lactoferrin contrast case
lf = R["lactoferrin"]
fig, ax = plt.subplots(figsize=(7.4, 4.3))
lo, hi = lf["reported_prices"]["band"]
ax.axhspan(lo, hi, color=BAND["egg"], zorder=0, lw=0)
ax.text(1.05, hi * 0.92, f"dairy bovine lactoferrin, reported prices 2013-2025 (2025 dollars): ${lo:,.0f}-{hi:,.0f}/kg (grade C)",
        fontsize=7, color=INK2, va="top")
ROUTE = {"lf": "cation exchange", "lf_ufdf_only": "UF/DF only"}
for c_, dx, mk in zip(lf["reported_prices"].get("comparators", []), (0.93, 1.07), ("*", "P")):
    ours = lf["reconciliation"][c_["ours"]]["cop"]
    ax.plot([10 * dx], [c_["value_money_year"]], marker=mk, ms=9, color=INK2, ls="none", zorder=5,
            label=f"Intelligen's model, {ROUTE[c_['ours']]}: ${c_['value_money_year']:.0f}/kg cost of production "
                  f"(ours: ${ours:.0f})")
ax.plot(lf["cost_vs_titer"]["titers"], lf["cost_vs_titer"]["msp"], color=CAT[0], marker="o", ms=4, zorder=3,
        label="PF lactoferrin, cation exchange, price-anchored capital (250 t/yr)")
pts = [("lf/humbird", "design titer 10 g/L (Intelligen)", CAT[0], "D"), ("lf/light", "same, design-report capital", CAT[0], "s"),
       ("lf_academic/humbird", "best public titer 2.8 g/L (Yen 2024)", CAT[1], "D"),
       ("lf_ufdf_only/humbird", "10 g/L, UF/DF only (optimistic)", CAT[2], "D")]
DX = {"lf/light": 0.965, "lf_ufdf_only/humbird": 1.035}     # side by side at 10 g/L, so no marker hides another
for key, lab, col, mk in pts:
    d = lf["cases"][key]
    ax.plot([d["design"]["titer"] * DX.get(key, 1.0)], [d["msp_ccf"]], marker=mk, ms=7, color=col, mec=SURF, mew=1.2,
            ls="none", zorder=4, label=f"{lab}: ${d['msp_ccf']:.0f}/kg")
ax.set_xscale("log"); ax.set_yscale("log")
plain(ax.xaxis, [1, 2, 5, 10, 20, 30])
ax.set_xlim(0.9, 35)
ax.set_ylim(60, 2200)
ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([100, 200, 300, 500, 1000, 1500]))
ax.yaxis.set_minor_formatter(NullFormatter())
money(ax.yaxis)
ax.set_xlabel("titer at harvest (g/L)")
ax.set_ylabel("$/kg lactoferrin, 2025")
_m = lf["cases"]["lf/humbird"]["msp_ccf"]
_pos = "below" if _m < lo else ("inside" if _m <= hi else "above")
ax.set_title(f"A high-value contrast: at a design titer, PF lactoferrin costs {_pos} the reported dairy price range")
ax.legend(fontsize=6.8, loc="lower left")
fig.text(0.01, -0.05, "K. phaffii without methanol (as FDA GRN 1219 and 1284), 90% lactoferrin powder. No PF lactoferrin price is public; "
         "the world market is ~0.3-1.6 kt/yr, so a 10 kt plant would not fit it.", fontsize=7, color=MUTED)
save(fig, "fig9_lactoferrin.png")

# ------------------------------------------------------------------ Fig 10 price ladder: every case against its market
SC_, PL_, LF_ = R["scenarios"], R["physical_limit"], R["lactoferrin"]
panels = [
    ("blg", "Beta-lactoglobulin vs whey protein", inc["whey"], [
        ("best public strain (Yao 2026)", SC_["academic/blg"], SC_["academic/blg/light"]),
        ("best public, on glucose (Li 2026)", SC_["academic/blg_li2026"], SC_["academic/blg_li2026/light"]),
        ("base case, 30 g/L", R["base"]["blg"], R["base_light"]["blg"]),
        ("industry benchmark, 42 g/L", SC_["industry/blg"], SC_["industry/blg/light"]),
        ("best case at demonstrated secretion (2.1 mg/g/h)", PL_["blg/humbird/q_p_max_2.1"], None),
        ("physical-limit best case (40 mg/g/h)", PL_["blg/humbird"], PL_["blg/light"])]),
    ("ova", "Ovalbumin vs dried egg white", inc["egg"], [
        ("best public strain (Aro 2023)", SC_["academic/ova"], SC_["academic/ova/light"]),
        ("base case, 30 g/L", R["base"]["ova"], R["base_light"]["ova"]),
        ("industry benchmark, 42 g/L", SC_["industry/ova"], SC_["industry/ova/light"]),
        ("physical-limit best case (40 mg/g/h)", PL_["ova/humbird"], PL_["ova/light"])]),
    ("lf", "Lactoferrin vs dairy lactoferrin", None, [
        ("best public titer, 2.8 g/L (Yen 2024)", LF_["cases"]["lf_academic/humbird"], LF_["cases"]["lf_academic/light"]),
        ("design titer 10 g/L, cation exchange", LF_["cases"]["lf/humbird"], LF_["cases"]["lf/light"]),
        ("design titer 10 g/L, UF/DF only", LF_["cases"]["lf_ufdf_only/humbird"], LF_["cases"]["lf_ufdf_only/light"])]),
]
fig, axes = plt.subplots(3, 1, figsize=(9.2, 8.0), gridspec_kw=dict(height_ratios=[7, 5, 4.2], hspace=0.55))
for ax, (key, title, incd, cases) in zip(axes, panels):
    n = len(cases)
    if incd is not None:
        lo, hi = incd["band"]
        ylab = f"market, {incd['years'][0]}-{incd['years'][1]}"
        col = BAND["whey" if key == "blg" else "egg"]
    else:
        lo, hi = LF_["reported_prices"]["band"]
        ylab = "market, reported 2013-2025"
        col = BAND["egg"]
    ax.axvspan(lo, hi, color=col, zorder=0, lw=0)
    ax.text(lo * 1.03, n - 0.35, f"{ylab}: ${lo:,.0f}-{hi:,.0f}", fontsize=7, color=INK2, va="top")
    if incd is not None and incd.get("spot"):
        sp = incd["spot"][0]["usd_kg_protein"]
        ax.axvline(sp, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)
        ax.text(sp * 1.03, -0.75, f"spot 2026: ${sp:.0f}", fontsize=6.8, color=INK2, va="bottom")
    if key == "lf":
        rows = {"lf": 1, "lf_ufdf_only": 0}          # rows of the cation-exchange and UF/DF-only cases
        for c_ in LF_["reported_prices"].get("comparators", []):
            y_ = rows[c_["ours"]] + 0.38
            ax.plot([c_["value_money_year"]], [y_], marker="*", ms=9, color=INK2, ls="none", zorder=4)
            route = {"lf": "cation exchange", "lf_ufdf_only": "UF/DF only"}[c_["ours"]]
            ax.text(c_["value_money_year"] * 1.06, y_, f"Intelligen's model, {route} (cost of production)", fontsize=6.6,
                    color=INK2, va="center")
    for i, (lab, h, l_) in enumerate(cases):
        y = n - 1 - i
        ax.plot([h["msp_ccf"]], [y], "o", ms=6.5, color=CAT[0], zorder=3)
        if l_ is None:          # price-anchored only (the design-report case is not computed)
            ax.text(h["msp_ccf"] * 1.08, y, f"${h['msp_ccf']:,.0f}", fontsize=6.8, color=INK2, va="center")
            continue
        a_, b_ = sorted([h["msp_ccf"], l_["msp_ccf"]])
        ax.plot([a_, b_], [y, y], color=AXIS, lw=2, zorder=2)
        ax.plot([l_["msp_ccf"]], [y], "o", ms=6.5, mfc=SURF, mec=CAT[0], mew=1.6, zorder=3)
        ax.text(max(h["msp_ccf"], l_["msp_ccf"]) * 1.08, y, f"${h['msp_ccf']:,.0f} / ${l_['msp_ccf']:,.0f}", fontsize=6.8,
                color=INK2, va="center")
    ax.set_yticks(range(n))
    ax.set_yticklabels([c[0] for c in cases][::-1], fontsize=7.6)
    ax.set_xscale("log")
    ax.set_ylim(-1, n)
    ax.set_title(title, fontsize=9, loc="left", color=INK)
    ax.grid(axis="y", visible=False)
    lo_x = min(min(h["msp_ccf"], (l_ or h)["msp_ccf"]) for _, h, l_ in cases)
    hi_x = max(max(h["msp_ccf"], (l_ or h)["msp_ccf"]) for _, h, l_ in cases)
    ax.set_xlim(min(lo_x, lo) * 0.6, max(hi_x, hi) * 2.2)
    money(ax.xaxis)
axes[-1].set_xlabel("$/kg protein, 2025 (log scale)")
axes[0].plot([], [], "o", color=CAT[0], label="price-anchored capital (base)")
axes[0].plot([], [], "o", mfc=SURF, mec=CAT[0], mew=1.6, label="design-report capital")
axes[0].legend(fontsize=7, loc="lower right", frameon=False)
fig.text(0.01, 0.005, "Model figures are production costs with a 14.6%/yr capital charge (not selling prices); market figures are export unit "
         "values per kg protein (whey 80%, egg white 81.1% protein) or reported prices, deflated to 2025 dollars. BLG and OVA at "
         "10 kt/yr, lactoferrin at 250 t/yr; US Midwest.", fontsize=6.8, color=MUTED, wrap=True)
save(fig, "fig10_price_ladder.png")

# ------------------------------------------------------------------ Fig 11 protein ingredients for context
ctx = R["benchmarks"].get("context", [])
if ctx:
    rows = sorted(ctx, key=lambda c: (c["lo"] * c["hi"]) ** 0.5)
    fig, ax = plt.subplots(figsize=(9.2, 0.42 * len(rows) + 2.1))
    gcol = {"plant": CAT[2], "dairy": CAT[0], "egg": CAT[1], "animal": CAT[4]}
    for i, c in enumerate(rows):
        ax.plot([c["lo"], c["hi"]], [i, i], color=gcol.get(c["group"], MUTED), lw=7, solid_capstyle="butt", alpha=0.55)
        ax.text(c["hi"] * 1.07, i, f"${c['lo']:.1f}-{c['hi']:.1f}  ({c['when'] or 'grade ' + c['grade']})", fontsize=6.8,
                color=INK2, va="center")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([c["label"] for c in rows], fontsize=7.8)
    marks = [("BLG base", R["base"]["blg"]["msp_ccf"], "-"), ("BLG, 42 g/L", R["scenarios"]["industry/blg"]["msp_ccf"], (0, (4, 2))),
             ("OVA base", R["base"]["ova"]["msp_ccf"], (0, (1, 2))),
             ("BLG best case", R["physical_limit"]["blg/humbird"]["msp_ccf"], (0, (6, 2, 1, 2)))]
    for j, (lab, x, ls) in enumerate(marks):
        ax.axvline(x, color=INK, lw=1.1, ls=ls, zorder=3)
        ax.text(x, len(rows) - 0.3 + 0.55 * (j % 2), f"{lab} ${x:.1f}", fontsize=6.8, color=INK, ha="center", va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(2.5, 150)
    ax.set_ylim(-0.7, len(rows) + 0.9)
    money(ax.xaxis)
    ax.set_xlabel("$ per kg protein (log scale)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Protein ingredients, per kg of protein, against our modelled costs", fontsize=9.5, loc="left")
    fig.text(0.01, -0.02, "Bars: market prices. Export unit values are 2015-2025 in 2025 dollars (grade A); GFI 2025 ranges are nominal, "
             "about 2024-2025 (grade C). Lines: this model's production costs (price-anchored capital, 10 kt/yr; best case at "
             "100 kt/yr), which include a return on capital but no margin, sales or distribution.", fontsize=6.8, color=MUTED, wrap=True)
    save(fig, "fig11_protein_context.png")
