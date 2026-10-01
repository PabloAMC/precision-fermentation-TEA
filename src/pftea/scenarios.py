"""Scenario runs and the analyses behind the report figures.

Products: the keys of data/pf/products.yaml (PRODUCTS), each with data/products/<key>.yaml. Each
product's base case is base.yaml plus its block there (lactoferrin: its own design titer,
cation-exchange route and a market-sized plant; BLG and OVA: no change). Adding a product is a
data change: its product file, its products.yaml block, its scenario blocks and its dryer-feed
solids leaf (dsp.dryer_feed_solids_<key>).

Scenarios (docs/SCOPE.md; never merged): academic, industry, required (inverse),
physical-limit. Each is the product's base case plus the overrides in
data/pf/scenarios/<name>.yaml ('common', then the product block or a named variant block).

Analyses:
  cost_map       MSP over titer x production time, with feasibility per cell (Fig. 1)
  bridge         step-by-step walk from NREL's crude enzyme to a food-grade isolate (Fig. 2)
  required       titer needed for a target $/kg, per production time (Fig. 3)
  physical_limit search over cell density and production time, titer at its feasibility
                 ceiling (cost falls with titer until a limit binds) (Fig. 4)
  tornado        one-at-a-time low/high swings coloured by evidence grade; an end that breaks a
                 physical limit is moved to the feasibility boundary (Fig. 5)
  monte_carlo    triangular sampling of the scenario's uncertain parameters
  scale_curve    MSP vs annual output, US vs EU, both capital conventions (Fig. 6)

Feasibility: a design is infeasible if it breaks O2 transfer, heat removal, titer reachability,
the vessel volume or the minimum initial fill, product solubility, the energetic ceiling on the
yield, or the specific-productivity ceiling (HARD_LIMITS, matched against the plant's flags).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from . import params, plant
from . import product as pr
from .params import v

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "data/pf/scenarios"
PRODUCTS = tuple(yaml.safe_load((ROOT / "data/pf/products.yaml").read_text()))   # blg, ova, lf, ...
LIGHT = {"capital.basis": "nrel"}          # the design-report ('light', NREL-style) capital convention
ASEPTIC = {"capital.fermenter_quote": "acce_aseptic"}   # Humbird's aseptic cell-culture STR quotes (structural high)
HARD_LIMITS = ("OUR", "heat", "reachable", "volume", "initial fill", "solubility", "energetic ceiling",
               "specific productivity", "did not reach")   # flags that make a design physically infeasible


def is_feasible(r: plant.Result, extra: tuple = ()) -> bool:
    """False if the design breaks O2 transfer, heat removal, titer reachability or vessel volume."""
    return not any(k in f for f in r.flags for k in HARD_LIMITS + tuple(extra))


def load(name: str) -> dict:
    return yaml.safe_load((SCEN / f"{name}.yaml").read_text())


def product_base(product: str) -> dict:
    """The product's block in data/pf/products.yaml (changes to base.yaml)."""
    return yaml.safe_load((ROOT / "data/pf/products.yaml").read_text()).get(product) or {}


def unused_paths(p: dict) -> tuple[str, ...]:
    """Parameter-path prefixes that do not enter this plant: other products' dryer-feed solids and
    the leaves of downstream routes other than plant.spec (plant.evaluate reads them only on their
    route). The tornado skips them, so no zero bars."""
    key, spec = v(p, "plant.product"), v(p, "plant.spec")
    out = [f"dsp.dryer_feed_solids_{k}" for k in PRODUCTS if k != key]
    if spec != "cex":
        out.append("dsp.cex_")
    else:
        out.append("dsp.diafiltration_volumes")      # the cex route diafilters dsp.cex_diafiltration_volumes
    if spec != "isolate":
        out += ["dsp.isolate_", "dsp.ammonium_sulfate", "dsp.precip_recovery"]
    if spec != "concentrate":
        out.append("dsp.concentrate_target_frac_dry")
    if spec != "acid":
        out.append("dsp.acid_")
    else:                                            # the acid route concentrates by UF but does not diafilter
        out += ["dsp.df_flux", "dsp.diafiltration_"]
    return tuple(out)


def base_params(product: str, extra: dict | None = None, p: dict | None = None) -> dict:
    """The product's base case: base.yaml (or p) + its products.yaml block + extra."""
    return params.override(params.load() if p is None else p,
                           {"plant.product": product, **product_base(product), **(extra or {})})


def scenario_params(name: str, product: str, extra: dict | None = None, variant: str | None = None) -> dict:
    """The product's base case + the scenario's 'common' block + its product block (or a named variant)."""
    s = load(name)
    return params.override(base_params(product),
                           {**s.get("common", {}), **s.get(variant or product, {}), **(extra or {})})


def run(name: str, product: str, extra: dict | None = None, variant: str | None = None) -> plant.Result:
    return plant.evaluate(scenario_params(name, product, extra, variant))


def mc_config(name: str, product: str) -> tuple[list[str], dict]:
    """Uncertain parameters and scenario ranges for one product (host-specific; audit R4-4)."""
    s = load(name)
    paths, ranges = s.get("mc_paths", []), s.get("mc_ranges", {})
    if isinstance(paths, dict):
        paths = paths.get("common", []) + paths.get(product, [])
    if ranges and any(k in ranges for k in ("common",) + PRODUCTS):
        ranges = {**ranges.get("common", {}), **ranges.get(product, {})}
    return paths, ranges


def cost_map(p: dict, titers, t_prods) -> dict:
    Z = np.full((len(t_prods), len(titers)), np.nan)
    feas = np.zeros_like(Z, dtype=bool)
    rate = np.zeros_like(Z)
    for i, tp in enumerate(t_prods):
        for j, T in enumerate(titers):
            try:
                r = plant.evaluate(params.override(p, {"strain.titer_g_L": float(T), "strain.t_prod_h": float(tp)}))
            except ValueError:
                continue
            Z[i, j] = r.msp_ccf
            feas[i, j] = is_feasible(r)
            rate[i, j] = T / (r.design["t_total_h"] + v(p, "fermenter.turnaround_h"))
    return dict(titers=np.array(titers), t_prods=np.array(t_prods), msp=Z, feasible=feas, rate=rate)


def required_titer(p: dict, target: float, t_prod: float, lo: float = 2.0, hi: float = 400.0) -> float | None:
    """Titer [g/L] at which MSP_CCF equals target for a given production time (None if unreachable)."""
    def f(T):
        return plant.evaluate(params.override(p, {"strain.titer_g_L": T, "strain.t_prod_h": t_prod})).msp_ccf - target
    if f(hi) > 0:
        return None
    if f(lo) < 0:
        return lo
    for _ in range(40):
        mid = np.sqrt(lo * hi)
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
        if hi / lo < 1.01:
            break
    return float(np.sqrt(lo * hi))


def max_feasible_titer(p: dict, t_prod: float, lo: float = 1.0, hi: float = 400.0) -> float | None:
    """Highest titer [g/L] reachable within the O2/heat/volume limits at a production time (log bisection)."""
    def ok(T):
        try:
            return is_feasible(plant.evaluate(params.override(p, {"strain.titer_g_L": T, "strain.t_prod_h": t_prod})))
        except ValueError:
            return False
    if not ok(lo):
        return None
    if ok(hi):
        return hi
    while hi / lo > 1.01:
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return float(lo)


def min_feasible_t_prod(p: dict, titer: float, lo: float = 12.0, hi: float = 480.0) -> float | None:
    """Shortest production phase [h] in which a titer is reachable within the O2/heat/volume limits."""
    def ok(tp):
        try:
            return is_feasible(plant.evaluate(params.override(p, {"strain.titer_g_L": titer, "strain.t_prod_h": tp})))
        except ValueError:
            return False
    # feasibility is not monotonic in t_prod: too short breaks O2/heat, too long breaks the vessel
    # volume (feed accumulates), so scan upward and refine the first feasible step
    step = 12.0
    prev = lo
    if ok(lo):
        return lo
    t = lo + step
    while t <= hi:
        if ok(t):
            a, b_ = prev, t
            while b_ - a > 1.0:
                mid = 0.5 * (a + b_)
                a, b_ = (a, mid) if ok(mid) else (mid, b_)
            return float(b_)
        prev, t = t, t + step
    return None


def binding(r: plant.Result, p: dict, tol: float = 0.02) -> list[str]:
    """Constraints within `tol` of their limit in a design (for the physical-limit optimum)."""
    d, out = r.design, []
    if d["our_peak"] >= d["otr_max"] * (1 - tol):
        out.append("O2 transfer")
    cap = v(p, "fermenter.heat_removal_max_kW_m3")
    if cap and d["heat_peak_kW_m3"] >= cap * (1 - tol):
        out.append("heat removal")
    qmax = plant._opt(p, "strain.q_p_max_mg_g_h")
    if qmax and d["q_p_mg_g_h"] >= qmax * (1 - tol):
        out.append("specific productivity")
    mf = plant._opt(p, "fermenter.min_initial_fill")
    if mf and d["W0_m3"] <= mf * v(p, "fermenter.volume_m3") * (1 + tol):
        out.append("minimum initial fill")
    if d["X_end"] >= v(p, "strain.X_max_g_L") * (1 - tol):
        out.append("maximum cell density")
    return out


def _best_titer(p: dict, X: float, tp: float, hi: float) -> dict | None:
    """Cheapest design at cell density X and production time tp: the titer at its feasibility ceiling."""
    q = params.override(p, {"strain.X_prod_g_L": float(X), "strain.t_prod_h": float(tp)})
    T = max_feasible_titer(q, tp, lo=1.0, hi=hi)
    if T is None:
        return None
    q = params.override(q, {"strain.titer_g_L": T})
    r = plant.evaluate(q)
    return dict(result=r, X_prod=float(X), t_prod=float(tp), titer=T, params=q) if is_feasible(r) else None


def physical_limit(product: str, extra: dict | None = None, fast: bool = False) -> dict | None:
    """The physical-limit scenario's cheapest design (best_design on its parameters)."""
    return best_design(scenario_params("physical_limit", product, extra), fast=fast)


def best_design(p: dict, fast: bool = False) -> dict | None:
    """Minimise MSP_CCF over cell density and production time; the titer sits at its ceiling.

    Everything else stays as in p (the physical-limit scenario, or the base case to ask what
    process design alone can do; review SC-1). A coarse grid over (X_prod, t_prod) from
    physical_limit.yaml is followed by two rounds of coordinate refinement (audit R4-1/R7-C2:
    the v1 grid left optima on its edges).
    """
    s = load("physical_limit")
    product = v(p, "plant.product")
    sols = [plant._opt(p, "plant.solubility_override_g_L"),
            (pr.load(product).get("solubility_practical_g_L") or {}).get("value")]
    t_hi = min([400.0] + [x for x in sols if x])
    X_max = v(p, "strain.X_max_g_L")
    Xs = [x for x in s["search"]["X_prod_g_L"] if x <= X_max] + [X_max]
    ts = s["search"]["t_prod_h"]
    if fast:
        Xs, ts = Xs[::2] + [X_max], ts[::2]
    best = None
    for X in sorted(set(Xs)):
        for tp in ts:
            c = _best_titer(p, X, tp, t_hi)
            if c and (best is None or c["result"].msp_ccf < best["result"].msp_ccf):
                best = c
    if best is None:
        return None
    dX, dt = 0.25 * best["X_prod"], 0.25 * best["t_prod"]
    for _ in range(1 if fast else 2):
        for key, step, lo_b, hi_b in (("X_prod", dX, 10.0, X_max), ("t_prod", dt, 6.0, 400.0)):
            for x in (best[key] - step, best[key] - step / 2, best[key] + step / 2, best[key] + step):
                x = min(max(x, lo_b), hi_b)
                X, tp = (x, best["t_prod"]) if key == "X_prod" else (best["X_prod"], x)
                c = _best_titer(p, X, tp, t_hi)
                if c and c["result"].msp_ccf < best["result"].msp_ccf:
                    best = c
        dX, dt = dX / 3, dt / 3
    best["binding"] = binding(best["result"], best["params"])
    return best


def _boundary(p: dict, path: str, x0: float, x1: float, n: int = 8) -> float:
    """Last feasible value on the way from a feasible x0 towards an infeasible x1 (bisection)."""
    a, b_ = x0, x1
    for _ in range(n):
        mid = 0.5 * (a + b_)
        try:
            ok = is_feasible(plant.evaluate(params.override(p, {path: mid})))
        except ValueError:
            ok = False
        a, b_ = (mid, b_) if ok else (a, mid)
    return a


def tornado(p: dict, paths: list[str], capital_bar: bool = True) -> list[dict]:
    """One-at-a-time swings. An end that breaks a physical limit is replaced by the feasibility
    boundary (flagged `truncated_*`), so no bar quotes the cost of an impossible plant
    (audit R7-M1). The capital convention is added as a structural bar."""
    r0 = plant.evaluate(p)
    base = r0.msp_ccf
    out = []
    for path in paths:
        b = params.bounds(p, path)
        if b is None:
            continue
        x0 = float(v(p, path))
        row = dict(path=path, base=base, grade=params.grade(p, path))
        for side, x in (("low", b[0]), ("high", b[1])):
            try:
                r = plant.evaluate(params.override(p, {path: x}))
                ok = is_feasible(r)
            except ValueError:
                r, ok = None, False
            trunc = False
            if not ok and x != x0:
                x = _boundary(p, path, x0, x)
                r, trunc = plant.evaluate(params.override(p, {path: x})), True
            row.update({side: x, f"msp_{side}": r.msp_ccf if r else base, f"truncated_{side}": trunc,
                        f"feasible_{side}": True})
        row["swing"] = abs(row["msp_high"] - row["msp_low"])
        out.append(row)
    if capital_bar:
        light = plant.evaluate(params.override(p, LIGHT)).msp_ccf
        out.append(dict(path="capital.basis", base=base, grade="structural", low="design-report (NREL-style)",
                        high="price-anchored (Humbird)", msp_low=light, msp_high=base, truncated_low=False,
                        truncated_high=False, feasible_low=True, feasible_high=True, swing=abs(base - light)))
        asep = plant.evaluate(params.override(p, ASEPTIC)).msp_ccf
        out.append(dict(path="capital.fermenter_quote", base=base, grade="structural", low="vendor quote (base)",
                        high="aseptic cell-culture STR (ACCE)", msp_low=base, msp_high=asep, truncated_low=False,
                        truncated_high=False, feasible_low=True, feasible_high=True, swing=abs(asep - base)))
    return sorted(out, key=lambda d: -d["swing"])


def monte_carlo(p: dict, paths: list[str], n: int = 500, seed: int = 0, ranges: dict | None = None) -> dict:
    """Triangular sampling of `paths`. `ranges` overrides low/high per path for the scenario.

    Draws that break a physical limit, or for which the model cannot build a plant (ValueError),
    count as infeasible (audit R4-10). Percentiles are given for feasible plants and for every
    draw with a cost (review SC-8: infeasible draws cost more), with the limit each infeasible
    draw breaks first and the mean of each sampled input in feasible and infeasible draws.
    """
    if ranges:
        p = params.override(p, {k: dict(val) for k, val in ranges.items()})
    rng = np.random.default_rng(seed)
    msp, feas, why, x = [], [], [], {k: [] for k in paths}
    for _ in range(n):
        q = params.sample(p, rng, paths)
        for k in paths:
            x[k].append(float(v(q, k)))
        try:
            r = plant.evaluate(q)
            msp.append(r.msp_ccf)
            feas.append(is_feasible(r))
            why.append(None if feas[-1] else next((k for f in r.flags for k in HARD_LIMITS if k in f), "other"))
        except ValueError:
            msp.append(np.nan)
            feas.append(False)
            why.append("no plant (model error)")
    msp, feas = np.array(msp), np.array(feas)
    ok, fin = msp[feas], msp[np.isfinite(msp)]
    pct = lambda a, q_: float(np.percentile(a, q_)) if a.size else float("nan")   # noqa: E731
    reasons = {}
    for w in why:
        if w:
            reasons[w] = reasons.get(w, 0) + 1
    means = {k: dict(feasible=float(np.mean(np.array(vals)[feas])) if feas.any() else None,
                     infeasible=float(np.mean(np.array(vals)[~feas])) if (~feas).any() else None)
             for k, vals in x.items()}
    return dict(msp=msp, feasible=feas, p10=pct(ok, 10), p50=pct(ok, 50), p90=pct(ok, 90),
                p10_all=pct(fin, 10), p50_all=pct(fin, 50), p90_all=pct(fin, 90),
                infeasible_reasons=reasons, input_means=means)


def scale_curve(p: dict, outputs_t) -> dict:
    out = {}
    for label, ch in [("US, price-anchored", {}), ("EU, price-anchored", {"plant.location": "eu_nw"}),
                      ("US, design-report", LIGHT), ("EU, design-report", {**LIGHT, "plant.location": "eu_nw"})]:
        q = params.override(p, ch)
        out[label] = [plant.evaluate(params.override(q, {"plant.annual_target_protein_t": float(o)})).msp_ccf
                      for o in outputs_t]
    return dict(outputs=list(outputs_t), curves=out)


# ---------------------------------------------------------------- cost bridge (Fig. 2)
BASE = None   # in a bridge step: drop the override so the base.yaml value returns


def bridge_steps() -> list[tuple[str, dict]]:
    """Cumulative changes from NREL's on-site cellulase (2025 prices) to the base BLG concentrate.

    Every step either sets a switch or returns a group of parameters to base.yaml, so the walk
    ends exactly at the base case (asserted in bridge()). Step sizes depend on the order.
    """
    nrel = yaml.safe_load((ROOT / "data/calibration/nrel2011_cellulase.yaml").read_text())["overrides"]
    start = {k: val for k, val in nrel.items()
             if not k.startswith(("utilities.", "labour.", "capital.cost_index", "finance."))}
    start.update({"capital.basis": "nrel"})
    b = params.load()
    t0, t1 = nrel["strain.titer_g_L"], v(b, "strain.titer_g_L")
    s0, s1 = nrel["plant.annual_target_protein_t"] / 1000, v(b, "plant.annual_target_protein_t") / 1000
    reset = lambda *keys: {k: BASE for k in keys}   # noqa: E731
    return [
        ("NREL on-site cellulase (T. reesei), 2025 prices, NREL-style capital", start),
        ("capital: price-anchored convention (Humbird factors and fixed costs)", reset("capital.basis")),
        ("food-grade indoor sanitary plant", reset("capital.facility_class")),
        ("host: K. phaffii stoichiometry and broth (no maintenance)", {"strain.host": "kphaffii",
                                                                     "hosts.kphaffii.maint_factor": 0.0,
                                                                     "hosts.kphaffii.m_s_prod_g_g_h": 0.0,
                                                                     "hosts.treesei.maint_factor": BASE}),
        ("high-density yeast process: 107 g/L cells, yeast media (no maintenance)",
         reset("strain.X_prod_g_L", "strain.X0_g_L", "strain.mu_prod_per_h", "strain.Y_ps_g_g",
               "media.salts_kg_per_m3", "media.salts_price_usd_kg", "media.antifoam_kg_per_m3",
               "media.antifoam_price_usd_kg")),
        ("maintenance energy (Tijhuis in growth, measured m_s in production)",
         reset("hosts.kphaffii.maint_factor", "hosts.kphaffii.m_s_prod_g_g_h")),
        ("schedule and vessel: 72 h production, 12 h turnaround, 200 m3",
         reset("strain.t_prod_h", "fermenter.turnaround_h", "fermenter.seed_time_h", "fermenter.volume_m3",
               "plant.operating_days")),
        (f"titer {t0:g} -> {t1:g} g/L", reset("strain.titer_g_L")),
        (f"scale {s0:.1f} -> {s1:g} kt/yr", reset("plant.annual_target_protein_t")),
        ("product: BLG, downstream to a dried concentrate", reset("plant.product", "plant.spec", "strain.host")),
    ]


VARIANTS = [("ovalbumin concentrate", {"plant.product": "ova"}),
            ("ovalbumin isolate (ammonium-sulfate precipitation)", {"plant.product": "ova", "plant.spec": "isolate"}),
            ("beta-casein, isoelectric precipitation to caseinate", {"plant.product": "cas", "plant.spec": "acid"}),
            ("lactoferrin, cation exchange (same titer, time and scale)", {"plant.product": "lf", "plant.spec": "cex"})]


def bridge() -> list[dict]:
    p = params.load()
    out, ch = [], {}
    for label, delta in bridge_steps():
        for k, val in delta.items():
            if val is BASE:
                ch.pop(k, None)
            else:
                ch[k] = val
        r = plant.evaluate(params.override(p, ch))
        out.append(dict(step=label, msp=r.msp_ccf, flags=r.flags, kind="step"))
    assert not ch, f"bridge does not end at the base case: {ch}"
    for label, delta in VARIANTS:
        r = plant.evaluate(params.override(p, delta))
        out.append(dict(step=label, msp=r.msp_ccf, flags=r.flags, kind="variant"))
    return out
