"""Scenario runs and the analyses behind the report figures.

Scenarios (docs/SCOPE.md; never merged): academic, industry, required (inverse),
physical-limit. Each is base.yaml plus the overrides in data/pf/scenarios/<name>.yaml
('common' plus the product block).

Analyses:
  cost_map       MSP over titer x production time, with O2/heat feasibility per cell (Fig. 1)
  bridge         step-by-step walk from NREL's crude enzyme to a food-grade isolate (Fig. 2)
  required       titer needed for a target $/kg, per production time (Fig. 3)
  physical_limit grid search over cell density, production time and titer (Fig. 4)
  tornado        one-at-a-time low/high swings coloured by evidence grade (Fig. 5)
  monte_carlo    triangular sampling of the scenario's uncertain parameters
  scale_curve    MSP vs annual output, US vs EU, both capital conventions (Fig. 6)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml

from . import params, plant
from .params import v

ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "data/pf/scenarios"
LIGHT = {"capital.basis": "nrel"}          # the published-TEA ('light') capital convention
HARD_LIMITS = ("OUR", "heat", "reachable", "volume")   # flags that make a design physically infeasible


def is_feasible(r: plant.Result, extra: tuple = ()) -> bool:
    """False if the design breaks O2 transfer, heat removal, titer reachability or vessel volume."""
    return not any(k in f for f in r.flags for k in HARD_LIMITS + tuple(extra))


def load(name: str) -> dict:
    return yaml.safe_load((SCEN / f"{name}.yaml").read_text())


def scenario_params(name: str, product: str, extra: dict | None = None) -> dict:
    s = load(name)
    ch = {"plant.product": product, **s.get("common", {}), **s.get(product, {}), **(extra or {})}
    return params.override(params.load(), ch)


def run(name: str, product: str, extra: dict | None = None) -> plant.Result:
    return plant.evaluate(scenario_params(name, product, extra))


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


def physical_limit(product: str, extra: dict | None = None) -> dict:
    s = load("physical_limit")
    p = scenario_params("physical_limit", product, extra)
    qmax = s["q_p_max_mg_g_h"] / 1000
    best = None
    for X in s["search"]["X_prod_g_L"]:
        for tp in s["search"]["t_prod_h"]:
            for T in s["search"]["titer_g_L"]:
                q = params.override(p, {"strain.X_prod_g_L": X, "strain.t_prod_h": tp, "strain.titer_g_L": T})
                r = plant.evaluate(q)
                if r.design["q_p_mg_g_h"] / 1000 > qmax * 1.001:
                    continue
                if not is_feasible(r, extra=("solubility",)):
                    continue
                if best is None or r.msp_ccf < best["result"].msp_ccf:
                    best = dict(result=r, X_prod=X, t_prod=tp, titer=T, params=q)
    return best


def tornado(p: dict, paths: list[str]) -> list[dict]:
    base = plant.evaluate(p).msp_ccf
    out = []
    for path in paths:
        node = params._leaf(p, path)
        lo, hi = node.get("low"), node.get("high")
        if lo is None or hi is None:
            continue
        r_lo = plant.evaluate(params.override(p, {path: lo}))
        r_hi = plant.evaluate(params.override(p, {path: hi}))
        out.append(dict(path=path, low=lo, high=hi, msp_low=r_lo.msp_ccf, msp_high=r_hi.msp_ccf, base=base,
                        feasible_low=is_feasible(r_lo), feasible_high=is_feasible(r_hi),
                        grade=node.get("grade", ""), swing=abs(r_hi.msp_ccf - r_lo.msp_ccf)))
    return sorted(out, key=lambda d: -d["swing"])


def monte_carlo(p: dict, paths: list[str], n: int = 500, seed: int = 0, ranges: dict | None = None) -> dict:
    """Triangular sampling of `paths`. `ranges` overrides low/high per path for the scenario.

    Draws that break a physical limit (O2 transfer, heat, reachable titer, volume) are kept
    in the record but excluded from the percentiles, which describe feasible plants only.
    The feasible fraction is reported alongside.
    """
    if ranges:
        p = params.override(p, {k: dict(val) for k, val in ranges.items()})
    rng = np.random.default_rng(seed)
    msp, feas = [], []
    for _ in range(n):
        try:
            r = plant.evaluate(params.sample(p, rng, paths))
        except ValueError:
            continue
        msp.append(r.msp_ccf)
        feas.append(is_feasible(r))
    msp, feas = np.array(msp), np.array(feas)
    ok = msp[feas] if feas.any() else msp
    return dict(msp=msp, feasible=feas, p10=float(np.percentile(ok, 10)), p50=float(np.percentile(ok, 50)),
                p90=float(np.percentile(ok, 90)))


def scale_curve(p: dict, outputs_t) -> dict:
    out = {}
    for label, ch in [("US, Humbird capital", {}), ("EU, Humbird capital", {"plant.location": "eu_nw"}),
                      ("US, light capital", LIGHT), ("EU, light capital", {**LIGHT, "plant.location": "eu_nw"})]:
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
        ("capital: Humbird convention (price-anchored)", reset("capital.basis")),
        ("food-grade indoor sanitary plant", reset("capital.facility_class")),
        ("host: K. phaffii stoichiometry and broth (no maintenance)", {"strain.host": "kphaffii",
                                                                     "hosts.kphaffii.maint_factor": 0.0,
                                                                     "hosts.treesei.maint_factor": BASE}),
        ("high-density yeast process: 80 g/L cells, yeast media (no maintenance)",
         reset("strain.X_prod_g_L", "strain.X0_g_L", "strain.mu_prod_per_h", "strain.Y_ps_g_g",
               "media.salts_kg_per_m3", "media.salts_price_usd_kg", "media.antifoam_kg_per_m3",
               "media.antifoam_price_usd_kg")),
        ("maintenance energy at 80 g/L cells (Tijhuis)", reset("hosts.kphaffii.maint_factor")),
        ("schedule and vessel: 72 h production, 12 h turnaround, 200 m3",
         reset("strain.t_prod_h", "fermenter.turnaround_h", "fermenter.seed_time_h", "fermenter.volume_m3",
               "plant.operating_days")),
        (f"titer {t0:g} -> {t1:g} g/L", reset("strain.titer_g_L")),
        (f"scale {s0:.1f} -> {s1:g} kt/yr", reset("plant.annual_target_protein_t")),
        ("product: BLG, downstream to a dried concentrate", reset("plant.product", "plant.spec", "strain.host")),
    ]


VARIANTS = [("ovalbumin concentrate", {"plant.product": "ova"}),
            ("ovalbumin isolate (ammonium-sulfate precipitation)", {"plant.product": "ova", "plant.spec": "isolate"})]


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
