"""Data for the model panel (docs/panel.html): results/panel_data.json.

For each product:
- a grid of full model runs over titer x production time x plant scale (base convention, US Midwest).
  Scale steps re-size the vessel (scenarios.base_params); titer and time keep that plant's vessel, as the
  model's scenarios do. Each run is stored as arrays aligned with the product's schema (ledger terms,
  capital items, chain numbers, limit values), so every number on the panel is an exact run;
- the sugar balance of each distinct batch (vessel, titer, time), which does not depend on scale;
- the cases: base, best published strain (academic), industry benchmark, physical-limit best case
  (rebuilt from results/analyses.json's optimum and checked against it), and the model's own EU base;
- the price to beat, published titers, and (from results/analyses.json) tornado, Monte Carlo and the
  required titers;
- every parameter of base.yaml with its range, unit, kind of evidence and source, and the product's changes.

Run: .venv/bin/python scripts/panel_data.py [--fast] [--products blg,ova] [--workers 4]
"""
from __future__ import annotations

import argparse
import json
import math
import pickle
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pftea import benchmarks, chain, labels, params, plant  # noqa: E402
from pftea import scenarios as sc  # noqa: E402
from pftea.params import v  # noqa: E402

OUT = ROOT / "results/panel_data.json"
TITERS = [1, 2, 3, 5, 7, 10, 15, 20, 30, 42, 60, 80, 100]          # g/L; 42 = the industry benchmark
T_PRODS = [24, 36, 48, 72, 96, 120, 168]                            # h of production
SCALES = [0.1, 0.3, 1, 3, 10]                                       # x the product's base plant
CHAIN_KEYS = None                                                    # set from the first record


def _sized(args):
    product, scale = args
    base = sc.base_params(product)
    A = v(base, "plant.annual_target_protein_t") * scale
    p = sc.base_params(product, {"plant.annual_target_protein_t": A})
    return product, scale, p


def _run(args):
    """One grid run -> (key, record) or an error record; the sugar balance only if asked (one per batch)."""
    key, p, with_sugar = args
    try:
        r = plant.evaluate(p)
    except ValueError as e:
        return key, dict(ok=False, flags=[str(e)], msp=None, error=True, sugar=None)
    rec = chain.record(p, r, with_sugar=with_sugar)
    rec["feasible"] = sc.is_feasible(r)
    return key, rec


def _case(args):
    name, p = args
    r = plant.evaluate(p)
    rec = chain.record(p, r)
    rec["feasible"] = sc.is_feasible(r)
    rec["inputs"].update(titer=v(p, "strain.titer_g_L"), t_prod=v(p, "strain.t_prod_h"),
                         X_prod=v(p, "strain.X_prod_g_L"), annual_t=v(p, "plant.annual_target_protein_t"))
    rec["prices"] = {t["path"]: t["price"] for t in r.ledger}
    return name, rec


def schema(recs: list[dict]) -> dict:
    """Column order per product: ledger terms (line, item), capital items, chain keys, limit keys."""
    full = [r for r in recs if not r.get("error")]
    terms, capex, lim = {}, {}, {}
    for r in full:
        for t in r["ledger"]:
            terms.setdefault((t[0], t[1]), dict(line=t[0], item=t[1], unit=t[3], price=t[4], path=t[5]))
        for k in r["capex"]:
            capex.setdefault(k, None)
        for x in r["limits"]:
            lim.setdefault(x["key"], {k: x[k] for k in ("key", "name", "limit", "unit", "kind", "path")})
    return dict(terms=list(terms.values()), capex=list(capex), chain=list(full[0]["chain"]), limits=list(lim.values()),
                recovery=list(full[0]["recovery_steps"]))


def compact(rec: dict, s: dict) -> list:
    """[ok, feasible, msp, flags, amounts, capex, chain, limits, recovery] aligned with the schema."""
    if rec.get("error"):
        return [False, False, None, rec["flags"], None, None, None, None, None]
    amt = {(t[0], t[1]): t[2] for t in rec["ledger"]}
    lim = {x["key"]: x["value"] for x in rec["limits"]}
    return [rec["ok"], rec["feasible"], rec["msp"], rec["flags"],
            [amt.get((t["line"], t["item"]), 0.0) for t in s["terms"]],
            [rec["capex"].get(k, 0.0) for k in s["capex"]],
            [rec["chain"].get(k) for k in s["chain"]],
            [lim.get(x["key"]) for x in s["limits"]],
            [rec["recovery_steps"].get(k, 1.0) for k in s["recovery"]]]


def price_to_beat(product: str) -> dict:
    """The incumbent the product is compared with (benchmarks.yaml compare_to): trade series, else reported prices."""
    for d in benchmarks.incumbents().values():
        if product in d["compare_to"]:
            return dict(label=d["label"], band=list(d["band"]), when=f"{d['years'][0]}-{d['years'][1]} trade unit values, "
                        f"{d['money_year']} US$ per kg protein", grade="A", spot=d["spot"])
    for d in benchmarks.reported_prices().values():
        cmp = d["compare_to"]
        if product == cmp or product in (cmp if isinstance(cmp, list) else []):
            return dict(label=d["label"], band=list(d["band"]), when="reported prices, 2025 US$ per kg protein",
                        grade=d["grade"], spot=[])
    raise KeyError(f"no price to beat for {product}")


def parameters(base: dict) -> list[dict]:
    """Every leaf of base.yaml: path, label, value (US and EU where keyed), range, unit, kind of evidence, source."""
    out = []

    def walk(node, pre):
        for k, x in node.items():
            path = f"{pre}.{k}" if pre else k
            if not isinstance(x, dict):
                continue
            leafish = "value" in x or any(l in x for l in params.LOCATIONS)
            if not leafish:
                walk(x, path)
                continue
            val = x.get("value") if "value" in x else {l: x.get(l) for l in params.LOCATIONS}
            if isinstance(val, dict) and not any(l in val for l in params.LOCATIONS):
                val = json.dumps(val)                                 # e.g. a formula or a table
            out.append(dict(path=path, label=labels.label(path), value=val, low=x.get("low"), high=x.get("high"),
                            unit=x.get("unit", ""), grade=x.get("grade", ""),
                            source=x.get("source") or x.get("note") or ""))
    walk(base, "")
    return out


def analyses_extract(product: str, a: dict) -> dict:
    """Tornado, Monte Carlo and required titers for the product from results/analyses.json (if present)."""
    if not a:
        return {}
    out = dict(generated=a.get("generated"))
    out["tornado"] = [dict(path=t["path"], label=labels.label(t["path"]), grade=t["grade"], kind=labels.evidence(t["grade"]),
                           low=t["low"], high=t["high"], msp_low=t["msp_low"], msp_high=t["msp_high"], base=t["base"],
                           feasible_low=t["feasible_low"], feasible_high=t["feasible_high"])
                      for t in a.get("tornado_by_product", {}).get(product, [])]
    out["monte_carlo"] = {s: {k: a["monte_carlo"][f"{s}/{product}"].get(k) for k in ("p10", "p50", "p90", "n")}
                          for s in ("academic", "industry") if f"{s}/{product}" in a.get("monte_carlo", {})}
    req = a.get("required", {}).get(f"{product}/humbird")
    if req:
        out["required"] = dict(t_prods=a["required_t_prods"],
                               targets={k: [x["titer"] if x["feasible"] else None for x in xs] for k, xs in req.items()},
                               ceiling=[x["ceiling"] for x in next(iter(req.values()))])
    return out


def reality_checks(a: dict) -> list[dict]:
    """The calibration anchors and the real-plant check (docs/VALIDATION.md), for the panel's 'Checks against
    reality' box. kind: 'reality' (a market price or a real plant) or 'consistency' (another model; agreement is
    not validation, PLAN.md honesty rule 7). Tolerances are the anchors' own (data/calibration/*.yaml); the
    baker's-yeast band is Humbird's market-implied cost under both readings of his 33% margin."""
    c = a.get("calibration") or {}
    cal = lambda name: yaml.safe_load((ROOT / f"data/calibration/{name}.yaml").read_text())   # noqa: E731
    out = []
    if "bakers_yeast" in c:
        st = c["bakers_yeast_stacks"]
        band = [min(st["market band, 33% margin on price"][0], st["market band, 33% margin on cost"][0]),
                max(st["market band, 33% margin on price"][1], st["market band, 33% margin on cost"][1])]
        ours = c["bakers_yeast"]["cop"]
        out.append(dict(name="Baker's yeast, Humbird's method", kind="reality", unit="$/kg (2018)", ours=ours, band=band,
                        ok=band[0] <= ours <= band[1],
                        note="Market price less a profit margin. The margin is Humbird's assumption. Same method as this model, not the same product."))
    pc = a.get("plant_cost_check")
    if pc:
        band = [min(pc["ll_scaled_per_m3"].values()), max(pc["ll_scaled_per_m3"].values())]
        out.append(dict(name="Capital cost of a real plant (Liberation Labs)", kind="reality", unit="$ per m3 of fermenter",
                        ours=pc["model_per_m3"], band=band, ok=band[0] <= pc["model_per_m3"] <= band[1],
                        note="Company figures for an unfinished plant, scaled to the model's size. Likely a floor."))
    rows = [("nrel2011_cellulase", "usd_per_kg_protein (DCF, NREL financing)", "NREL 2011 enzyme plant design", "$/kg (2007)",
             "Same process, lighter accounting: lower fixed costs and installation factors."),
            ("intelligen2025_ova", "usd_per_kg_powder (Humbird convention)", "Intelligen 2025 ovalbumin design", "$/kg powder",
             "Partly agrees by construction: the base yield was derived from this design."),
            ("voutilainen2021_case", "EUR_per_t_protein (their DCF)", "Voutilainen 2021 protein plant design", "€/t",
             "Capital differs by {cap}. Their fixed costs and labour are lower.")]
    for key, metric, name, unit, note in rows:
        if key in c and metric in c[key]:
            ours, theirs = c[key][metric]
            tol = cal(key)["target"]["tolerance"]
            if "{cap}" in note:
                co, ct = c[key]["TCI vs their FCI (EUR)"]
                note = note.format(cap=f"{co / ct - 1:+.0%}")
            out.append(dict(name=name, kind="consistency", unit=unit, ours=ours, theirs=theirs, tolerance=tol,
                            ok=abs(ours / theirs - 1) <= tol, note=note))
    return out


def case_changes(prod: str, a: dict) -> dict:
    """What each case changes from the product's base case: the scenario file's common and product blocks
    (physical limit: plus the optimum's cell density, production time and titer)."""
    out = {}
    for name in ("academic", "industry", "physical_limit"):
        s = sc.load(name)
        ch = {**s.get("common", {}), **s.get(prod, {})}
        out[name] = {k: (x.get("value") if isinstance(x, dict) else x) for k, x in ch.items()}
    pl = a.get("physical_limit", {}).get(f"{prod}/humbird")
    if pl:
        out["physical_limit"].update({"strain.X_prod_g_L": pl["X_prod"], "strain.t_prod_h": pl["t_prod"], "strain.titer_g_L": pl["titer"]})
    out["eu_model"] = {"plant.location": "eu_nw"}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="coarse grid, for a quick check")
    ap.add_argument("--products", default=",".join(sc.PRODUCTS))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--cache", help="pickle of the runs: reused if present, written after the runs (a crash in the "
                    "write step then costs no rerun)")
    args = ap.parse_args()
    products = args.products.split(",")
    titers, t_prods, scales = (TITERS, T_PRODS, SCALES) if not args.fast else ([3, 10, 30, 60], [48, 72, 120], [0.1, 1, 10])
    t0 = time.time()
    a_path = ROOT / "results/analyses.json"
    a = json.loads(a_path.read_text()) if a_path.exists() else {}
    cache = Path(args.cache) if args.cache else None
    if cache and cache.exists():
        sized, axes, sugar_jobs, grid, case_out = pickle.loads(cache.read_bytes())
        print(f"runs read from {cache}", flush=True)
    else:
        sized, axes, sugar_jobs, grid, case_out = run_all(products, titers, t_prods, scales, a, args.workers, t0)
        if cache:
            cache.write_bytes(pickle.dumps((sized, axes, sugar_jobs, grid, case_out)))
    write(products, sized, axes, sugar_jobs, grid, case_out, a, args.fast, t0)


def run_all(products, titers, t_prods, scales, a, workers, t0):
    with Pool(workers) as pool:
        sized = {(prod, s): p for prod, s, p in pool.map(_sized, [(prod, s) for prod in products for s in scales])}
        print(f"sized {len(sized)} plants in {time.time() - t0:.0f} s", flush=True)
        axes, jobs, sugar_jobs = {}, [], {}
        for prod in products:
            base = sized[(prod, 1)]
            Ts = sorted(set(titers) | {v(base, "strain.titer_g_L")})
            ts = sorted(set(t_prods) | {v(base, "strain.t_prod_h")})
            axes[prod] = dict(titer=Ts, t_prod=ts, scale=scales,
                              annual_t=[v(sized[(prod, s)], "plant.annual_target_protein_t") for s in scales],
                              volume=[v(sized[(prod, s)], "fermenter.volume_m3") for s in scales])
            for k, s in enumerate(scales):
                for i, T in enumerate(Ts):
                    for j, t in enumerate(ts):
                        q = params.override(sized[(prod, s)], {"strain.titer_g_L": float(T), "strain.t_prod_h": float(t)})
                        batch_key = (prod, v(q, "fermenter.volume_m3"), i, j)
                        jobs.append(((prod, k, i, j), q, batch_key not in sugar_jobs))
                        sugar_jobs.setdefault(batch_key, (prod, k, i, j))
        cases = []
        for prod in products:
            cases += [((prod, "base"), sized[(prod, 1)]),
                      ((prod, "academic"), sc.scenario_params("academic", prod)),
                      ((prod, "industry"), sc.scenario_params("industry", prod)),
                      ((prod, "eu_model"), sc.base_params(prod, {"plant.location": "eu_nw"}))]
            pl = a.get("physical_limit", {}).get(f"{prod}/humbird")
            if pl and pl.get("feasible"):
                q = params.override(sc.scenario_params("physical_limit", prod),
                                    {"strain.X_prod_g_L": pl["X_prod"], "strain.t_prod_h": pl["t_prod"], "strain.titer_g_L": pl["titer"]})
                cases.append(((prod, "physical_limit"), q))
        print(f"{len(jobs)} grid runs, {len(sugar_jobs)} sugar balances, {len(cases)} cases", flush=True)
        grid = dict(pool.imap_unordered(_run, jobs, chunksize=4))
        print(f"grid done at {time.time() - t0:.0f} s", flush=True)
        case_out = dict(pool.imap_unordered(_case, cases))
    print(f"all runs done at {time.time() - t0:.0f} s", flush=True)
    return sized, axes, sugar_jobs, grid, case_out


def write(products, sized, axes, sugar_jobs, grid, case_out, a, fast, t0):
    base_yaml = params.load()
    out = dict(generated=time.strftime("%Y-%m-%d %H:%M"), fast=fast,
               labels={"evidence": labels.EVIDENCE}, parameters=parameters(base_yaml),
               analyses_generated=a.get("generated"), reality_checks=reality_checks(a), products={})
    prod_names = yaml.safe_load((ROOT / "data/pf/products.yaml").read_text())
    for prod in products:
        ax = axes[prod]
        recs = [grid[(prod, k, i, j)] for k in range(len(ax["scale"])) for i in range(len(ax["titer"])) for j in range(len(ax["t_prod"]))]
        s = schema(recs)
        vols = sorted({vv for vv in ax["volume"]})
        sug = {}
        for (pp, V, i, j), gk in sugar_jobs.items():
            if pp == prod:
                sug[f"{vols.index(V)}/{i}/{j}"] = grid[gk].get("sugar")
        pl_check = None
        if (prod, "physical_limit") in case_out:
            pl = a["physical_limit"][f"{prod}/humbird"]
            pl_check = dict(stored=pl["msp_ccf"], rebuilt=case_out[(prod, "physical_limit")]["msp"])
        p_base = sized[(prod, 1)]
        info = pr_info(prod)
        out["products"][prod] = dict(
            name=info["name"], short=info["short"], what=info["what"], host=v(p_base, "strain.host"), spec=v(p_base, "plant.spec"),
            axes=ax, vessel_choices=vols, schema=s,
            grid=[compact(r, s) for r in recs],                 # index = ((k * nT) + i) * nt + j
            sugar=sug, cases={c: rec for (pp, c), rec in case_out.items() if pp == prod},
            physical_limit_check=pl_check, price_to_beat=price_to_beat(prod),
            targets=benchmarks.required_targets().get(prod),
            markers=[dict(titer=t, label=l) for t, l in benchmarks.titer_markers().get(prod, [])],
            overrides={k: (x if isinstance(x, dict) else {"value": x}) for k, x in sc.product_base(prod).items()},
            case_changes=case_changes(prod, a), unused=list(sc.unused_paths(p_base)),
            prices_eu={t["path"]: t["price"] for t in plant.evaluate(params.override(p_base, {"plant.location": "eu_nw"})).ledger},
            location_factor_eu=v(params.override(p_base, {"plant.location": "eu_nw"}), "capital.location_factor"),
            analyses=analyses_extract(prod, a))
    OUT.write_text(json.dumps(clean(out), separators=(",", ":"), allow_nan=False, ensure_ascii=False))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB) in {time.time() - t0:.0f} s")


DISPLAY = {   # plain names and one line on what each protein is (README's table)
    "blg": ("β-lactoglobulin", "BLG", "the main whey protein"),
    "alac": ("α-lactalbumin", "α-lac", "the second whey protein, used in infant formula"),
    "ova": ("ovalbumin", "OVA", "the main egg-white protein"),
    "ovd": ("ovomucoid", "OVD", "an egg-white protein sold as a heat-stable ingredient"),
    "cas": ("β-casein", "β-casein", "one of the two main proteins of cheese curd"),
    "lf": ("lactoferrin", "LF", "a scarce, high-value milk protein"),
    "alb": ("serum albumin", "albumin", "a protein in the growth media of cultivated meat"),
}


def pr_info(prod: str) -> dict:
    name, short, what = DISPLAY.get(prod, (prod, prod, ""))
    return dict(name=name, short=short, what=what)


def clean(x):
    """NaN and infinities -> None, recursively (strict JSON)."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: clean(y) for k, y in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(y) for y in x]
    return x


if __name__ == "__main__":
    main()
