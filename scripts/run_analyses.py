"""Run every analysis behind the report and cache it to results/analyses.json.

Run:  .venv/bin/python scripts/run_analyses.py [--fast] [--only section,section]
All numbers in the report, figures and explorer come from this file. `--only` recomputes the
named sections and keeps the rest of an existing results/analyses.json.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pftea import benchmarks as bm  # noqa: E402
from pftea import calibration as cal  # noqa: E402
from pftea import humbird_yeast as hy  # noqa: E402
from pftea import params, plant  # noqa: E402
from pftea import scenarios as sc  # noqa: E402
from pftea.labels import LABELS  # noqa: E402

FAST = "--fast" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
BASE = params.load()
P_IND = sc.scenario_params("industry", "blg")


def summary(r: plant.Result) -> dict:
    d = {k: (float(x) if isinstance(x, (int, float, np.floating)) else x) for k, x in r.design.items()
         if k != "seeds_m3"}
    return dict(ok=r.ok, flags=r.flags, msp_ccf=r.msp_ccf, cop=r.cop, msp_dcf=r.msp_dcf, per_kg_powder=r.per_kg_powder,
                tci=r.tci, per_kg={k: float(x) for k, x in r.per_kg.items()},
                capex={k: float(x) for k, x in r.capex.items()},
                physical={k: float(x) for k, x in r.physical.items()}, design=d, feasible=sc.is_feasible(r))


def ev(changes: dict, p: dict = BASE) -> dict:
    return summary(plant.evaluate(params.override(p, changes)))


def clean(x):
    """JSON-safe copy: NaN/inf -> None (strict JSON, readable by Typst and the explorer)."""
    if isinstance(x, dict):
        return {str(k): clean(val) for k, val in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(val) for val in x]
    if isinstance(x, (float, np.floating)):
        return float(x) if np.isfinite(x) else None
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


# ---------------------------------------------------------------- sections
def s_base(res):
    res["base"] = {prod: ev({"plant.product": prod}) for prod in ("blg", "ova")}
    res["base_light"] = {prod: ev({"plant.product": prod, **sc.LIGHT}) for prod in ("blg", "ova")}
    res["base_eu"] = {prod: ev({"plant.product": prod, "plant.location": "eu_nw"}) for prod in ("blg", "ova")}
    res["base_isolate"] = {prod: ev({"plant.product": prod, "plant.spec": "isolate"}) for prod in ("blg", "ova")}
    res["benchmarks"] = {"incumbents": bm.incumbents(), "titer_markers": bm.titer_markers()}
    res["labels"] = LABELS


def s_scenarios(res):
    res["scenarios"] = {}
    for name in ("academic", "industry"):
        for prod in ("blg", "ova"):
            res["scenarios"][f"{name}/{prod}"] = summary(sc.run(name, prod))
            res["scenarios"][f"{name}/{prod}/light"] = summary(sc.run(name, prod, sc.LIGHT))
            res["scenarios"][f"{name}/{prod}/eu"] = summary(sc.run(name, prod, {"plant.location": "eu_nw"}))


def s_physical_limit(res):
    res["physical_limit"] = {}
    for prod in ("blg", "ova"):
        for label, extra in (("humbird", {}), ("light", sc.LIGHT)):
            pl = sc.physical_limit(prod, extra)
            if pl:
                res["physical_limit"][f"{prod}/{label}"] = dict(summary(pl["result"]), X_prod=pl["X_prod"],
                                                               t_prod=pl["t_prod"], titer=pl["titer"])
    # sensitivity: OVA if its practical solubility were not 50 g/L (Intelligen's assumption) but BLG-like
    ul = float(params.v(BASE, "dsp.uf_end_g_L"))
    for label, extra in (("humbird", {}), ("light", sc.LIGHT)):
        pl = sc.physical_limit("ova", {**extra, "plant.solubility_override_g_L": ul, "dsp.uf_end_g_L": ul})
        if pl:
            res["physical_limit"][f"ova/{label}/solubility_{ul:g}"] = dict(
                summary(pl["result"]), X_prod=pl["X_prod"], t_prod=pl["t_prod"], titer=pl["titer"])


def s_cost_vs_titer(res):
    """Fig. 1: MSP over titer, per production time, with feasibility."""
    titers = [2, 3, 5, 8, 12, 20, 30, 42, 60, 80, 110, 150]
    t_prods = [48, 72, 120]
    res["cost_vs_titer"] = {}
    for prod in ("blg", "ova"):
        p = params.override(BASE, {"plant.product": prod})
        m = sc.cost_map(p, titers, t_prods)
        ml = sc.cost_map(params.override(p, sc.LIGHT), titers, [72])
        # the end of each curve: the highest feasible titer (O2/heat ceiling) and its cost
        ceil = [sc.max_feasible_titer(p, tp) for tp in t_prods]
        at = lambda q, c, tp: (plant.evaluate(params.override(q, {"strain.titer_g_L": c, "strain.t_prod_h": tp})).msp_ccf  # noqa: E731
                               if c else None)
        res["cost_vs_titer"][prod] = dict(titers=titers, t_prods=t_prods, msp=m["msp"].tolist(),
                                          feasible=m["feasible"].tolist(), light_72h=ml["msp"][0].tolist(),
                                          light_72h_feasible=ml["feasible"][0].tolist(), ceiling=ceil,
                                          msp_at_ceiling=[at(p, c, tp) for c, tp in zip(ceil, t_prods)],
                                          light_72h_at_ceiling=at(params.override(p, sc.LIGHT), ceil[t_prods.index(72)], 72))


def s_bridge(res):
    res["bridge"] = sc.bridge()


def s_required(res):
    """Fig. 3 and table: titer needed for a target price, and the O2/heat titer ceiling, per production time."""
    t_prods = [36, 48, 60, 72, 96, 120]
    targets = [10, 20, 50]
    res["required_t_prods"] = t_prods
    res["required"], res["titer_ceiling"] = {}, {}
    for prod in ("blg", "ova"):
        p0 = params.override(BASE, {"plant.product": prod})
        res["titer_ceiling"][prod] = [sc.max_feasible_titer(p0, tp) for tp in t_prods]
        for label, extra in (("humbird", {}), ("light", sc.LIGHT)):
            p = params.override(p0, extra)
            out = {}
            for tg in targets:
                rows = []
                for tp, ceil in zip(t_prods, res["titer_ceiling"][prod]):
                    # search only the feasible range: past the O2/heat ceiling the cost curve is not physical
                    T = sc.required_titer(p, tg, tp, hi=ceil) if ceil else None
                    rows.append(dict(titer=T, feasible=T is not None, ceiling=ceil))
                out[str(tg)] = rows
            res["required"][f"{prod}/{label}"] = out


def s_claims(res):
    """Q5: shortest production phase in which each claimed titer is feasible, and the MSP there."""
    acad = sc.load("academic")["ova"]
    res["claims"] = []
    for c in bm.claims():
        ch = {"plant.product": c["model_product"], "strain.host": c["model_host"]}
        if c["model_host"] == "treesei":
            ch.update({k: acad[k] for k in ("strain.X_prod_g_L",)})
        p = params.override(BASE, ch)
        tp = sc.min_feasible_t_prod(p, c["titer"])
        row = dict(label=c["label"], titer=c["titer"], host=c["model_host"], product=c["model_product"],
                   X_prod=float(params.v(p, "strain.X_prod_g_L")), t_prod_min=tp)
        if tp is not None:
            for lab, extra in (("humbird", {}), ("light", sc.LIGHT)):
                r = plant.evaluate(params.override(p, {"strain.titer_g_L": c["titer"], "strain.t_prod_h": tp, **extra}))
                row[f"msp_{lab}"] = r.msp_ccf
            row["q_p_mg_g_h"] = float(r.design["q_p_mg_g_h"])   # specific productivity the claim then implies
        res["claims"].append(row)


def s_policy(res):
    """EU policy levers on the base BLG plant: what closes the US-EU gap, and what cheaper capital does."""
    eu = {"plant.product": "blg", "plant.location": "eu_nw"}
    us_price = lambda k: params.v(params.override(BASE, {"plant.location": "us_midwest"}), k)  # noqa: E731
    energy = {k: us_price(k) for k in ("utilities.electricity_usd_kWh", "utilities.natural_gas_usd_GJ",
                                       "utilities.steam_usd_t")}
    cases = {
        "EU base": {},
        "EU with US energy prices": energy,
        "EU with US glucose price": {"utilities.glucose_usd_kg": us_price("utilities.glucose_usd_kg")},
        "EU, capital at 4%/10 yr": {"finance.ccf_rate": 0.04},
        "EU, capital at 4%/20 yr": {"finance.ccf_rate": 0.04, "finance.ccf_life_y": 20},
    }
    res["policy"] = {k: plant.evaluate(params.override(BASE, {**eu, **ch})).msp_ccf for k, ch in cases.items()}
    res["policy"]["US base"] = plant.evaluate(params.override(BASE, {"plant.product": "blg"})).msp_ccf


def s_tornado(res):
    """Industry-benchmark BLG; the scenario's own ranges (mc_ranges) replace base ranges where given."""
    p = params.override(P_IND, {k: dict(val) for k, val in sc.load("industry").get("mc_ranges", {}).items()})
    paths = [x for x in params.ranged_leaves(p) if not x.startswith(("plant.", "hosts.treesei"))]
    res["tornado"] = sc.tornado(p, paths)


def s_monte_carlo(res):
    n = 60 if FAST else 400
    res["monte_carlo"] = {}
    for name in ("academic", "industry"):
        for prod in ("blg", "ova"):
            p = sc.scenario_params(name, prod)
            mc = sc.monte_carlo(p, sc.load(name)["mc_paths"], n=n, seed=1, ranges=sc.load(name).get("mc_ranges"))
            res["monte_carlo"][f"{name}/{prod}"] = dict(p10=mc["p10"], p50=mc["p50"], p90=mc["p90"], n=int(len(mc["msp"])),
                                                       feasible_frac=float(mc["feasible"].mean()),
                                                       msp=[float(x) for x in mc["msp"]],
                                                       feasible=[bool(x) for x in mc["feasible"]])


def s_scale(res):
    res["scale"] = sc.scale_curve(P_IND, [1000, 2500, 5000, 10000, 25000, 50000, 100000])


def s_calibration(res):
    res["calibration"] = {"bakers_yeast": {"cop": hy.run()["cop"], "humbird": 1.8899, "market_implied": 1.90}}
    for name, light in (("nrel2011_cellulase", cal.LIGHT), ("intelligen2025_ova", cal.LIGHT),
                        ("voutilainen2021_case", cal.voutilainen_conventions("nrel"))):
        o = cal.run(name)
        res["calibration"][name] = {k: [float(a), float(b)] for k, (a, b) in o["compare"].items()}
        res["calibration"][name]["msp_ccf_per_kg_target"] = float(o["result"].msp_ccf)
        k0, (a0, b0) = next(iter(cal.run(name, light)["compare"].items()))
        res["calibration"][name][k0 + " [light convention]"] = [float(a0), float(b0)]


SECTIONS = {"base": s_base, "scenarios": s_scenarios, "physical_limit": s_physical_limit,
            "cost_vs_titer": s_cost_vs_titer, "bridge": s_bridge, "required": s_required, "claims": s_claims,
            "policy": s_policy,
            "tornado": s_tornado,
            "monte_carlo": s_monte_carlo, "scale": s_scale, "calibration": s_calibration}

if __name__ == "__main__":
    t0 = time.time()
    path = OUT / "analyses.json"
    res = json.loads(path.read_text()) if ONLY and path.exists() else {}
    for name, fn in SECTIONS.items():
        if ONLY and name not in ONLY:
            continue
        fn(res)
        print(f"{name} done {time.time() - t0:.0f}s", flush=True)
    res.update(generated=time.strftime("%Y-%m-%d %H:%M"), fast=FAST if not ONLY else res.get("fast", FAST))
    res["runtime_s"] = time.time() - t0
    path.write_text(json.dumps(clean(res), indent=1, default=float, allow_nan=False))
    print(f"wrote results/analyses.json in {res['runtime_s']:.0f}s")
