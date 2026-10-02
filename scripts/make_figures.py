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


PRODS = list(R["base"])                      # products in results order (data/pf/products.yaml)
PROD = {"blg": "beta-lactoglobulin (whey protein)", "ova": "ovalbumin (egg-white protein)",
        "ovd": "ovomucoid (egg-white protein)", "cas": "beta-casein (milk casein)", "lf": "lactoferrin (milk)",
        "alb": "serum albumin (cell-culture media)"}
SHORT = {"blg": "BLG", "ova": "OVA", "ovd": "ovomucoid", "cas": "casein", "lf": "lactoferrin", "alb": "albumin"}
BAND = {"blg": "#e3edf9", "ova": "#fbe6dc", "ovd": "#fbe6dc", "cas": "#e6f4ec", "lf": "#efe9f7", "alb": "#f6efd9", "whey": "#e3edf9", "egg": "#fbe6dc"}
PCOL = {k: CAT[i] for i, k in enumerate(PRODS)}
inc = R["benchmarks"]["incumbents"]
REPORTED = {d["compare_to"]: d for d in [R.get(s_, {}).get("reported_prices") for s_ in ("lactoferrin", "albumin")] if d}


def market(prod):
    """The product's price band per kg protein (2025$): its incumbent's trade values, or reported prices."""
    for d in inc.values():
        if prod in d["compare_to"]:
            y0, y1 = d["years"]
            return dict(lo=d["band"][0], hi=d["band"][1], spot=d.get("spot", []), text=f"{d['label']}, {y0}-{y1}")
    d = REPORTED.get(prod)
    if d:
        return dict(lo=d["band"][0], hi=d["band"][1], spot=[], text=d["label"])
    return None


def tpy(d):
    """Plant output of a result, t target protein per year."""
    return d["design"]["n_batches"] * d["design"]["target_per_batch_kg"] / 1000


def grid(n, w=10.5, h=4.4, **kw):
    """n panels on a 2-column grid; unused cells switched off."""
    nr = (n + 1) // 2
    fig, axes = plt.subplots(nr, 2, figsize=(w, h * nr), **kw)
    axes = np.atleast_1d(axes).ravel()
    for ax in axes[n:]:
        ax.axis("off")
    return fig, axes[:n]


SCALES = ", ".join(f"{SHORT[k]} {tpy(R['base'][k]):,.0f} t/yr" for k in PRODS)


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

# ------------------------------------------------------------------ Fig 1 cost vs titer
marks = R["benchmarks"]["titer_markers"]
fig, axes = grid(len(PRODS), h=5.6, gridspec_kw=dict(hspace=1.25, wspace=0.22))
for ax, prod in zip(axes, PRODS):
    c = R["cost_vs_titer"][prod]
    T = np.array(c["titers"], float)
    m = market(prod)
    ys_all = []
    if m:
        ax.axhspan(m["lo"], m["hi"], color=BAND[prod], zorder=0, lw=0)
        ax.text(2.1, m["hi"] * 0.93, f"{m['text']}:\n${m['lo']:,.0f}-{m['hi']:,.0f}/kg protein", fontsize=6.6, color=INK2,
                va="top", ha="left")
        ys_all += [m["lo"], m["hi"]]
        for s_ in m["spot"][:1]:
            ax.axhline(s_["usd_kg_protein"], color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)
            ax.text(165, s_["usd_kg_protein"] * 1.05, f"{s_['label']}: ${s_['usd_kg_protein']:.0f}",
                    fontsize=6.6, color=INK2, va="bottom", ha="right")
    for k, tp in enumerate(c["t_prods"]):
        x, y, n_ok = feasible_part(T, c["msp"][k], c["feasible"][k])
        cx, cy = c.get("ceiling", [None] * 3)[k], c.get("msp_at_ceiling", [None] * 3)[k]
        if cx and cy and (len(x) == 0 or cx > x[-1]):
            x, y = np.append(x, cx), np.append(y, cy)
        lab_ = f"{tp} h production" + (f" (ceiling {cx:.0f} g/L)" if cx else "")
        ax.plot(x, y, color=CAT[k], marker="o", ms=3.5, label=lab_, zorder=3)
        ys_all += list(y)
        if cx and cy:
            ax.plot([cx], [cy], marker="D", ms=6, color=CAT[k], mec=SURF, mew=1.2, zorder=4)
    x, y, _ = feasible_part(T, c["light_72h"], c["light_72h_feasible"])
    cx, cy = c.get("ceiling", [None, None, None])[1], c.get("light_72h_at_ceiling")
    if cx and cy:
        x, y = np.append(x, cx), np.append(y, cy)
    ax.plot(x, y, color=CAT[1], ls=(0, (3, 2)), lw=1.4, label="72 h production, design-report capital", zorder=3)
    ax.plot([], [], marker="D", ms=6, color=INK2, ls="none", label="cheapest feasible design at that time")
    for t, lab in marks.get(prod, []):
        ax.axvline(t, color=AXIS, lw=0.8, zorder=0)
        ax.text(t, 1.012, f"{lab}: {t:.3g} g/L", transform=ax.get_xaxis_transform(), rotation=60, ha="left",
                va="bottom", fontsize=6.2, color=INK2, rotation_mode="anchor")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(1.8, 170)
    ys_all = [v_ for v_ in ys_all if v_ and np.isfinite(v_)]
    ax.set_ylim(min(ys_all) * 0.6, max(ys_all) * 2.0)
    plain(ax.xaxis, [2, 5, 10, 20, 50, 100, 150])
    money(ax.yaxis)
    ax.set_xlabel("titer at harvest (g/L)")
    ax.set_ylabel("$/kg target protein, 2025")
    ax.text(0.98, 0.97, f"{PROD[prod]}\n{tpy(R['base'][prod]):,.0f} t/yr", transform=ax.transAxes, ha="right", va="top",
            fontsize=9, fontweight="bold", color=INK)
h, l_ = axes[0].get_legend_handles_labels()
fig.legend(h, [x.split(" (ceiling")[0] for x in l_], loc="lower center", ncol=3, fontsize=7.2, bbox_to_anchor=(0.5, -0.02))
fig.text(0.01, -0.06, f"Each product's base case ({SCALES}), US Midwest, fermenters sized to each plant (200 m3 at 10 kt/yr; 100 m3 for lactoferrin and albumin), glucose fed at 500 g/L. Each line ends "
         "at the highest feasible titer in that production time (O2 transfer, heat removal, minimum fill, specific productivity).\n"
         "Price bands, per kg protein in 2025 dollars: export unit values of whey protein >80% and dried egg albumin (OVA and ovomucoid), casein export and "
         "US import prices, reported dairy lactoferrin prices and bulk albumin trade values (grade C). Top axis: published and claimed titers (data/titers.csv).",
         fontsize=7, color=MUTED)
save(fig, "fig1_cost_vs_titer.png")

# ------------------------------------------------------------------ Fig 3 design space
tps = np.array(R["required_t_prods"], float)
fig, axes = grid(len(PRODS), h=4.1, gridspec_kw=dict(hspace=0.45, wspace=0.2))
missing = []
for j, (ax, prod) in enumerate(zip(axes, PRODS)):
    ceil = np.array([c if c else np.nan for c in R["titer_ceiling"][prod]], float)
    ax.fill_between(tps, ceil, 400, color="#efeee9", zorder=0, lw=0)
    ax.plot(tps, ceil, color=INK2, lw=1.2, zorder=2)
    if j == 0:
        ax.text(tps[0] + 1, 330, "grey: above the feasibility ceiling (solid line)\ndotted: the ceiling with a 600 g/L feed",
                fontsize=6.4, color=INK2, va="top", ha="left", linespacing=1.3)
    cf = np.array([c if c else np.nan for c in R.get("titer_ceiling_feed600", {}).get(prod, [])], float)
    if cf.size:
        ax.plot(tps, cf, color=INK2, lw=0.9, ls=(0, (1, 2)), zorder=2)
    ys = list(ceil[np.isfinite(ceil)])
    for k, tg in enumerate(R["required_targets"][prod]):
        tg = str(tg)
        for basis, ls in (("humbird", "-"), ("light", (0, (3, 2)))):
            rows_ = R["required"][f"{prod}/{basis}"][tg]
            xs = [t for t, r_ in zip(tps, rows_) if r_["titer"]]
            yv = [r_["titer"] for r_ in rows_ if r_["titer"]]
            ys += yv
            if xs:
                ax.plot(xs, yv, color=CAT[k], ls=ls, lw=1.8, marker="o", ms=4, zorder=3,
                        label=f"${tg}/kg" + (", design-report capital" if basis == "light" else ""))
            else:
                missing.append(f"{SHORT[prod]} ${tg}/kg ({'price-anchored' if basis == 'humbird' else 'design-report'} capital)")
    if prod == "ova":
        ax.axhline(50, color=CAT[1], lw=0.9, ls=(0, (1, 2)))
        ax.text(124, 50 * 0.97, "50 g/L:\nIntelligen's\nassumed\nsolubility", fontsize=6.2, color=INK2,
                va="top", ha="left", linespacing=1.2)
    ax.set_yscale("log")
    ax.set_ylim(min([4.0] + ys) * 0.7, 400)
    plain(ax.yaxis, [t for t in (1, 2, 5, 10, 20, 50, 100, 200, 400) if t >= min([4.0] + ys) * 0.7])
    ax.set_xlim(30, 138 if prod == "ova" else 125)
    ax.set_xlabel("production phase (h)")
    ax.set_ylabel("titer needed (g/L)")
    ax.set_title(f"{PROD[prod]}, {tpy(R['base'][prod]):,.0f} t/yr", fontsize=9)
    ax.legend(fontsize=6.4, loc="best", ncol=2)
fig.text(0.01, -0.03, "Lines: titer at which the minimum selling price equals the target (each product's base plant, US; solid "
         "price-anchored, dashed design-report capital), searched only below the feasibility ceiling; grey: designs the fermenter "
         "cannot run. Targets bracket each product's market (lactoferrin sells for hundreds of $/kg; albumin's run from GFI's $10/kg target to $100/kg)."
         + (f"\nNot reachable at any production time with the base cells and yield: {', '.join(missing)}." if missing else ""),
         fontsize=7, color=MUTED, wrap=True)
save(fig, "fig3_required_titer.png")

# ------------------------------------------------------------------ Fig 4 breakdown
groups = [("capital charge", ["capital charge"]), ("maintenance + insurance", ["maintenance", "insurance"]),
          ("labour", ["labour"]), ("glucose", ["glucose"]),
          ("other raw materials", ["ammonia", "salts & other media", "DSP chemicals"]),
          ("utilities", ["electricity", "natural gas & steam", "water & wastewater"]),
          ("membranes, resin + waste", ["membranes", "chromatography resin", "biomass disposal"])]
fig, axes = grid(len(PRODS), w=11.5, h=2.6, gridspec_kw=dict(hspace=0.65, wspace=0.75))
for ax, prod in zip(axes, PRODS):
    rows = [(f"base ({R['base'][prod]['design']['titer']:.0f} g/L)", R["base"][prod]),
            (f"industry benchmark ({R['scenarios'][f'industry/{prod}']['design']['titer']:.0f} g/L)",
             R["scenarios"][f"industry/{prod}"])]
    for basis in ("humbird", "light"):
        d = R["physical_limit"].get(f"{prod}/{basis}")
        if d:
            rows.append((f"physical limit ({d['titer']:.0f} g/L)" + (", design-report" if basis == "light" else ""), d))
    top = 0
    for i, (lab, d) in enumerate(rows[::-1]):
        left = 0
        for g, (gname, keys) in enumerate(groups):
            w = sum(d["per_kg"].get(k2, 0) for k2 in keys)
            ax.barh(i, w, left=left, color=CAT[g], height=0.62, edgecolor=SURF, linewidth=1.2,
                    label=gname if (i == 0 and prod == PRODS[0]) else None)
            left += w
        top = max(top, left)
        ax.text(left * 1.01 + 0.2, i, f"${left:,.1f}", va="center", fontsize=7.5, color=INK)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.5)
    money(ax.xaxis)
    ax.set_xlim(0, top * 1.25)
    ax.set_title(f"{PROD[prod]}, {tpy(R['base'][prod]):,.0f} t/yr", fontsize=9, loc="left")
    ax.grid(axis="y", visible=False)
h, l_ = axes[0].get_legend_handles_labels()
fig.legend(h, l_, fontsize=7.5, ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.06))
fig.text(0.01, -0.1, "$/kg target protein, 2025; capital charge 14.6%/yr of total capital investment. Physical limit: each "
         "product at 100 kt/yr (lactoferrin at its largest market estimate; albumin at GFI's high 2030 demand).", fontsize=7, color=MUTED)
save(fig, "fig4_breakdown.png")

# ------------------------------------------------------------------ Fig 5 tornado
TOR = R.get("tornado_by_product") or {"blg": R["tornado"]}
ORD["structural"] = INK2


def tlabel(par, trunc):
    txt = {"design-report (NREL-style)": "design-report", "price-anchored (Humbird)": "price-anchored",
           "vendor quote (base)": "vendor quote", "aseptic cell-culture STR (ACCE)": "aseptic STR"}.get(par, None)
    txt = txt or ((f"{par:,.0f}" if abs(par) >= 1000 else f"{par:.3g}") if isinstance(par, (int, float)) else f"{par}")
    return txt + (" \u2020" if trunc else "")


tprods = [k for k in PRODS if k in TOR]
NT = 10
fig, axes = plt.subplots(len(tprods), 1, figsize=(8.8, 3.3 * len(tprods)), gridspec_kw=dict(hspace=0.45))
axes = np.atleast_1d(axes)
trunc_any = False
for ax, prod in zip(axes, tprods):
    tor = [t for t in TOR[prod] if t["swing"] > 0.005 * t["base"]][:NT]
    base_v = tor[0]["base"]
    for i, t in enumerate(tor[::-1]):
        col = ORD.get(t["grade"], ORD[""])
        for val, par, trunc in ((t["msp_low"], t["low"], t.get("truncated_low", False)),
                                (t["msp_high"], t["high"], t.get("truncated_high", False))):
            trunc_any |= bool(trunc)
            ax.barh(i, val - base_v, left=base_v, color=col, height=0.6, linewidth=0.0)
            other = t["msp_high"] if val == t["msp_low"] else t["msp_low"]
            tol = 0.004 * base_v
            right = val > base_v + tol or (abs(val - base_v) <= tol and other < base_v)
            ax.text(val + (1 if right else -1) * 0.012 * base_v, i, tlabel(par, trunc),
                    ha="left" if right else "right", va="center", fontsize=6.4, color=INK2)
    ax.axvline(base_v, color=INK, lw=1)
    ax.set_yticks(range(len(tor)))
    ax.set_yticklabels([plabel(t["path"]) for t in tor[::-1]], fontsize=7.4)
    money(ax.xaxis)
    lo_all = min(min(t["msp_low"], t["msp_high"]) for t in tor)
    hi_all = max(max(t["msp_low"], t["msp_high"]) for t in tor)
    pad = 0.12 * (hi_all - lo_all)
    ax.set_xlim(lo_all - pad, hi_all + pad)
    ax.set_title(f"{PROD[prod]}: industry benchmark, ${base_v:,.1f}/kg", fontsize=9, loc="left")
    ax.grid(axis="y", visible=False)
axes[-1].set_xlabel("$/kg target protein; numbers at the bar ends are the parameter values tested")
fig.legend(handles=[Patch(color=ORD[g], label=f"grade {g}") for g in "ABCDE"]
           + [Patch(color=ORD["structural"], label="convention")], fontsize=7.5, ncol=6,
           loc="lower center", bbox_to_anchor=(0.5, -0.02))
fig.text(0.01, -0.05, "One parameter at a time over its evidence range, coloured by evidence grade; the ten largest swings per "
         "product. Each product on its own plant (lactoferrin 250 t/yr, albumin 1 kt/yr)."
         + ("\n\u2020 the end of the evidence range breaks a physical limit; the bar stops at the last feasible value shown."
            if trunc_any else ""), fontsize=7, color=MUTED)
save(fig, "fig5_tornado.png")

# ------------------------------------------------------------------ Fig 6 scale
SCB = R.get("scale_by_product") or {"blg": R["scale"]}
styles = {"US, price-anchored": (CAT[0], "-"), "EU, price-anchored": (CAT[1], "-"),
          "US, design-report": (CAT[0], (0, (3, 2))), "EU, design-report": (CAT[1], (0, (3, 2)))}
NAMES = {"US, price-anchored": "US, price-anchored", "EU, price-anchored": "EU (NL), price-anchored",
         "US, design-report": "US, design-report", "EU, design-report": "EU (NL), design-report"}
sprods = [k for k in PRODS if k in SCB]
fig, axes = grid(len(sprods), h=3.9, gridspec_kw=dict(hspace=0.5, wspace=0.45))
for ax, prod in zip(axes, sprods):
    sc_ = SCB[prod]
    X = np.array(sc_["outputs"]) / 1000
    for lab, ys in sc_["curves"].items():
        col, ls = styles[lab]
        ax.plot(X, ys, color=col, ls=ls, marker="o", ms=3.5, label=NAMES[lab])
        ax.text(X[-1] * 1.1, ys[-1], f"${ys[-1]:,.1f}", fontsize=6.8, color=INK2, va="center")
    ax.set_xscale("log")
    plain(ax.xaxis, [t for t in (0.1, 0.25, 0.5, 1, 2.5, 5, 10, 25, 50, 100) if X[0] <= t <= X[-1]])
    ax.set_xlim(X[0] * 0.85, X[-1] * 2.2)
    ax.set_xlabel("plant output (kt target protein per year)")
    ax.set_ylabel("$/kg target protein, 2025")
    money(ax.yaxis)
    ax.set_title(f"{PROD[prod]}: industry benchmark", fontsize=9, loc="left")
axes[0].legend(fontsize=7, loc="upper right")
fig.text(0.01, -0.03, "Above ~10 kt/yr a plant adds 200 m3 fermenters rather than larger ones, so fermentation stops getting "
         "cheaper per kg; only downstream and utilities keep scaling. Lactoferrin's range spans its market (~0.3-1.6 kt/yr).",
         fontsize=7, color=MUTED)
save(fig, "fig6_scale.png")

# ------------------------------------------------------------------ Fig 7 Monte Carlo intervals
mc = R["monte_carlo"]
order = [f"{s_}/{k}" for k in PRODS[::-1] for s_ in ("industry", "academic") if f"{s_}/{k}" in mc]
fig, ax = plt.subplots(figsize=(8.6, 0.42 * len(order) + 1.3))
lo_x, hi_x = np.inf, 0
for i, k in enumerate(order):
    d = mc[k]
    col = PCOL[k.split("/")[1]]
    ms = np.array(d["msp"]); fe = np.array(d.get("feasible", [True] * len(ms)), bool)
    jit = (np.random.default_rng(0).random(len(ms)) - 0.5) * 0.25
    ax.scatter(ms[fe], i + jit[fe], s=5, color=col, alpha=0.25, lw=0, zorder=2)
    ax.plot([d["p10"], d["p90"]], [i, i], color=col, lw=3, solid_capstyle="round", zorder=3)
    ax.plot(d["p50"], i, "o", color=col, ms=8, mec=SURF, mew=2, zorder=4)
    if d.get("base"):
        ax.plot(d["base"], i, marker="|", ms=14, mew=2, color=INK, zorder=5)
    right = np.nanmax(ms[fe]) if fe.any() else d["p90"]
    ax.text(right * 1.12, i, f"median ${d['p50']:,.0f}, p10-p90 ${d['p10']:,.0f}-{d['p90']:,.0f}; "
            f"{100 * d['feasible_frac']:.0f}% of {d.get('n', len(ms))} draws feasible", va="center", fontsize=6.8,
            color=INK2)
    lo_x, hi_x = min(lo_x, np.nanmin(ms[fe]) if fe.any() else d["p10"]), max(hi_x, right)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([{"academic": "academic best", "industry": "industry benchmark"}[k.split("/")[0]] + ", "
                    + SHORT[k.split("/")[1]] for k in order], fontsize=8)
ax.set_xscale("log"); money(ax.xaxis)
ax.set_xlim(lo_x * 0.6, hi_x * 60)
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
for ax, name in zip(axes, ("milk", "egg")):
    src = eqv["sources"][name]
    unit = src["all_protein_g"] / 1000                       # $/kg protein -> $ per litre or per egg
    for prod in src["compare_to"]:
        c = R["cost_vs_titer"][prod]
        k72 = c["t_prods"].index(72)
        T, y, _ = feasible_part(c["titers"], c["msp"][k72], c["feasible"][k72])
        cx, cy = c["ceiling"][k72], c["msp_at_ceiling"][k72]
        if cx and cy:
            T, y = np.append(T, cx), np.append(y, cy)
        ax.plot(T, y * unit, color=PCOL[prod], marker="o", ms=3.5, zorder=3,
                label=f"PF {SHORT[prod]} replacing the {src['all_protein_g']:.1f} g of "
                      f"{'milk' if name == 'milk' else 'egg-white'} protein, 72 h production")
    for j, (lab, ser) in enumerate(src["prices"].items()):
        vals = list(ser.values())
        yr = max(ser, key=int)                                 # JSON keys are strings
        last = ser[yr]
        ax.axhspan(min(vals), max(vals), color=[BAND["whey"], BAND["egg"], BAND["cas"]][j % 3], zorder=0, lw=0)
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
    ax.legend(fontsize=6.6, loc="upper right")
fig.text(0.01, -0.06, "The natural source's price divided by its protein is an upper bound on what that protein is worth: fat, lactose "
         "and yolk carry part of the price, and whey is a by-product of cheese (report section on equivalents). Price-anchored "
         "capital, each product's base plant (10 kt/yr), US; milk and egg prices deflated to 2025 dollars with CPI-U. Lactoferrin "
         "(~0.1-0.2 g per litre of milk) has no per-unit equivalent.", fontsize=7, color=MUTED, wrap=True)
save(fig, "fig8_equivalents.png")

# ------------------------------------------------------------------ Fig 9 downstream route and purity
LFX = R.get("lactoferrin", {})
ROUTES = {   # (label, result) per product: the base route first, then its alternatives
    "blg": [("UF/DF concentrate (base)", R["base"].get("blg")), ("isolate: ammonium-sulfate precipitation", R["base_isolate"].get("blg"))],
    "ova": [("UF/DF concentrate (base)", R["base"].get("ova")), ("isolate: ammonium-sulfate precipitation", R["base_isolate"].get("ova"))],
    "ovd": [("UF/DF concentrate (base; EVERY's cleared route)", R["base"].get("ovd")),
            ("isolate: ammonium-sulfate precipitation", R["base_isolate"].get("ovd"))],
    "cas": [("isoelectric precipitation to caseinate (base)", R["base"].get("cas")),
            ("UF/DF only (Eden Brew, FSANZ A1342)", R.get("casein", {}).get("cases", {}).get("cas_ufdf_edenbrew/humbird"))],
    "lf": [("cation exchange (base)", R["base"].get("lf")),
           ("UF/DF only (Intelligen case a)", LFX.get("cases", {}).get("lf_ufdf_only/humbird"))],
    "alb": [("cation exchange + anion-exchange polish (base)", R["base"].get("alb")),
            ("capture only (96% assumed; optimistic)", R.get("albumin", {}).get("cases", {}).get("alb_capture_only/humbird")),
            ("UF/DF only (77% albumin; below spec)", R.get("albumin", {}).get("cases", {}).get("alb_ufdf_only/humbird"))],
}
rprods = [k for k in PRODS if k in ROUTES]
fig, axes = grid(len(rprods), w=12, h=2.5, gridspec_kw=dict(hspace=0.8, wspace=1.0))
for ax, prod in zip(axes, rprods):
    rows = [(lab, d) for lab, d in ROUTES[prod] if d]
    m = market(prod)
    xs = []
    if m:
        ax.axvspan(m["lo"], m["hi"], color=BAND[prod], zorder=0, lw=0)
        xs += [m["lo"], m["hi"]]
    for i, (lab, d) in enumerate(rows[::-1]):
        tp, pw = d["msp_ccf"], d["per_kg_powder"]
        ax.plot([pw, tp], [i, i], color=AXIS, lw=2, zorder=2)
        ax.plot([tp], [i], "o", ms=7, color=PCOL[prod], zorder=3)
        ax.plot([pw], [i], "o", ms=7, mfc=SURF, mec=PCOL[prod], mew=1.6, zorder=3)
        ax.text(max(tp, pw) * 1.12, i, f"${tp:,.1f}/kg {SHORT[prod]}; ${pw:,.2f}/kg powder; "
                f"{int(100 * d['design']['purity_dry'] + 0.5)}% of dry matter", fontsize=6.6, color=INK2, va="center")
        xs += [tp, pw]
    if prod == "lf":                                   # Intelligen's own model: cost of production, not MSP
        for c_ in LFX.get("reported_prices", {}).get("comparators", []):
            i = {"lf": len(rows) - 1, "lf_ufdf_only": len(rows) - 2}.get(c_["ours"])
            if i is not None and i >= 0:
                ax.plot([c_["value_money_year"]], [i + 0.3], marker="*", ms=8, color=INK2, ls="none", zorder=4)
                xs.append(c_["value_money_year"])
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=7.4)
    ax.set_xscale("log"); money(ax.xaxis)
    ax.set_xlim(min(xs) * 0.5, max(xs) * 30)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_title(f"{PROD[prod]}", fontsize=9, loc="left")
    ax.grid(axis="y", visible=False)
axes[0].plot([], [], "o", color=INK2, label="per kg target protein")
axes[0].plot([], [], "o", mfc=SURF, mec=INK2, mew=1.6, label="per kg powder")
if "lf" in rprods:
    axes[0].plot([], [], "*", color=INK2, ms=8, label="Intelligen's lactoferrin model (cost of production)")
fig.legend(*axes[0].get_legend_handles_labels(), fontsize=7.2, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.05))
fig.text(0.01, -0.09, "Price-anchored capital, each product's base plant, US. The downstream route sets how much of the powder is "
         "the target protein, so the cost per kg of protein and per kg of powder can rank routes differently. Bands: market prices "
         "per kg protein, as in Fig. 1.", fontsize=7, color=MUTED, wrap=True)
save(fig, "fig9_routes.png")

# ------------------------------------------------------------------ Fig 10 price ladder: every case against its market
SC_, PL_ = R["scenarios"], R["physical_limit"]
ACAD = {"blg": [("best public strain, 13.9 g/L (Yao 2026)", "academic/blg"), ("best public on glucose (Li 2026)", "academic/blg_li2026")],
        "ova": [("best public strain (Aro 2023, T. reesei)", "academic/ova")],
        "ovd": [("best peer-reviewed (Kim 2025)", "academic/ovd"),
                ("EVERY patent example, 30 g/L", "academic/ovd_patent")],
        "cas": [("best peer-reviewed in K. phaffii, intracellular (Choi 1996)", "academic/cas"),
                ("best public casein, 3 g/L (E. coli patent)", "academic/cas_patent")],
        "lf": [("best public methanol-free (Yen 2024)", "academic/lf"), ("best public secreted (Lv 2023; methanol)", "academic/lf_lv2023")],
        "alb": [("best public rHSA, 8.7 g/L of broth in 192 h (Zhu 2021; methanol)", "academic/alb"),
                ("4.4 g/L of broth in 96 h (Zhu 2018; methanol)", "academic/alb_zhu2018"),
                ("best methanol-free, 1.5 g/L (Delta patent)", "academic/alb_patent")]}


def ladder(prod):
    rows = [(lab, SC_[k], SC_.get(f"{k}/light")) for lab, k in ACAD.get(prod, []) if k in SC_]
    b = R["base"][prod]
    rows.append((f"base case, {b['design']['titer']:.0f} g/L", b, R["base_light"][prod]))
    rows.append(("industry benchmark, 42 g/L", SC_[f"industry/{prod}"], SC_.get(f"industry/{prod}/light")))
    if f"{prod}/humbird/q_p_max_2.1" in PL_:
        rows.append(("best case at demonstrated secretion (2.1 mg/g/h)", PL_[f"{prod}/humbird/q_p_max_2.1"], None))
    if f"{prod}/humbird" in PL_:
        rows.append(("physical-limit best case (40 mg/g/h)", PL_[f"{prod}/humbird"], PL_.get(f"{prod}/light")))
    return rows


panels = [(k, ladder(k)) for k in PRODS]
fig, axes = plt.subplots(len(panels), 1, figsize=(9.2, 0.42 * sum(len(r) for _, r in panels) + 1.2 * len(panels)),
                         gridspec_kw=dict(height_ratios=[len(r) + 1.2 for _, r in panels], hspace=0.6))
for ax, (key, cases) in zip(np.atleast_1d(axes), panels):
    n = len(cases)
    m = market(key)
    lo, hi = (m["lo"], m["hi"]) if m else (np.nan, np.nan)
    if m:
        ax.axvspan(lo, hi, color=BAND[key], zorder=0, lw=0)
        ax.text(lo * 1.03, n - 0.35, f"market: ${lo:,.0f}-{hi:,.0f}", fontsize=7, color=INK2, va="top")
        if m["spot"]:
            sp = m["spot"][0]["usd_kg_protein"]
            ax.axvline(sp, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)
            ax.text(sp * 1.03, -0.75, f"spot {m['spot'][0].get('year') or ''}: ${sp:.0f}", fontsize=6.8, color=INK2, va="bottom")
    for i, (lab, h, l_) in enumerate(cases):
        y = n - 1 - i
        ax.plot([h["msp_ccf"]], [y], "o", ms=6.5, color=PCOL[key], zorder=3)
        if l_ is None:
            ax.text(h["msp_ccf"] * 1.08, y, f"${h['msp_ccf']:,.0f}", fontsize=6.8, color=INK2, va="center")
            continue
        a_, b_ = sorted([h["msp_ccf"], l_["msp_ccf"]])
        ax.plot([a_, b_], [y, y], color=AXIS, lw=2, zorder=2)
        ax.plot([l_["msp_ccf"]], [y], "o", ms=6.5, mfc=SURF, mec=PCOL[key], mew=1.6, zorder=3)
        ax.text(max(h["msp_ccf"], l_["msp_ccf"]) * 1.08, y, f"${h['msp_ccf']:,.0f} / ${l_['msp_ccf']:,.0f}", fontsize=6.8,
                color=INK2, va="center")
    ax.set_yticks(range(n))
    ax.set_yticklabels([c[0] for c in cases][::-1], fontsize=7.4)
    ax.set_xscale("log")
    ax.set_ylim(-1, n)
    ax.set_title(f"{PROD[key]}, {tpy(R['base'][key]):,.0f} t/yr", fontsize=9, loc="left", color=INK)
    ax.grid(axis="y", visible=False)
    vals = [x["msp_ccf"] for _, h, l_ in cases for x in (h, l_) if x] + ([lo, hi] if m else [])
    ax.set_xlim(min(vals) * 0.6, max(vals) * 2.6)
    money(ax.xaxis)
np.atleast_1d(axes)[-1].set_xlabel("$/kg protein, 2025 (log scale)")
ax0 = np.atleast_1d(axes)[0]
ax0.plot([], [], "o", color=INK2, label="price-anchored capital (base)")
ax0.plot([], [], "o", mfc=SURF, mec=INK2, mew=1.6, label="design-report capital")
ax0.legend(fontsize=7, loc="lower right", frameon=False)
fig.text(0.01, 0.0, "Model figures are production costs with a 14.6%/yr capital charge (not selling prices); market figures are "
         "per kg protein, 2025 dollars, as in Fig. 1. Each product on its own base plant (" + SCALES + "); US Midwest.",
         fontsize=6.8, color=MUTED, wrap=True)
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
    LS = ["-", (0, (4, 2)), (0, (1, 2)), (0, (6, 2, 1, 2)), (0, (2, 1))]
    marks = [(f"{SHORT[k]} base", R["base"][k]["msp_ccf"]) for k in PRODS if k not in REPORTED and R["base"][k]["msp_ccf"] < 150]
    marks += [("BLG, 42 g/L", R["scenarios"]["industry/blg"]["msp_ccf"]),
              ("BLG best case", R["physical_limit"]["blg/humbird"]["msp_ccf"])]
    for j, (lab, x) in enumerate(marks):
        ax.axvline(x, color=INK, lw=1.1, ls=LS[j % len(LS)], zorder=3)
        ax.text(x, len(rows) - 0.3 + 0.5 * j, f"{lab} ${x:.1f}", fontsize=6.6, color=INK, ha="center", va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(2.5, 150)
    ax.set_ylim(-0.7, len(rows) + 0.6 + 0.5 * len(marks))
    money(ax.xaxis)
    ax.set_xlabel("$ per kg protein (log scale)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Protein ingredients, per kg of protein, against our modelled costs", fontsize=9.5, loc="left")
    fig.text(0.01, -0.02, "Bars: market prices. Export unit values are 2015-2025 in 2025 dollars (grade A); GFI 2025 ranges are nominal, "
             "about 2024-2025 (grade C). Lines: this model's production costs (price-anchored capital, 10 kt/yr; best case at "
             "100 kt/yr), which include a return on capital but no margin, sales or distribution. Lactoferrin and albumin, "
             "which are not food-ingredient commodities, are in Figs 1 and 10.", fontsize=6.8, color=MUTED, wrap=True)
    save(fig, "fig11_protein_context.png")
