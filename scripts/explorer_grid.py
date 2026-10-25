"""Precompute the explorer's grid: MSP and cost structure over the main levers.

The explorer (docs/explorer.html) never re-implements the model in JavaScript: it looks up
this grid, so every number it shows is a real model run. Grid:
    product x capital convention x site x titer x production time x cell density x yield.
Each product runs on its own base case (data/pf/products.yaml: lactoferrin at 250 t/yr with cation
exchange; BLG and OVA at 10 kt/yr); the grid axes override titer, time, cells and yield.
Run:  .venv/bin/python scripts/explorer_grid.py   (parallel; writes results/explorer_grid.json)
      .venv/bin/python scripts/explorer_grid.py --detailed   (adds the 'detailed' sub-grid to the existing file)
The 'detailed' sub-grid runs the same strain levers with the optional physics of
data/pf/scenarios/detailed.yaml ('common': secretion tied to growth, large-tank yield loss), at the
base capital convention, site and product yield only; each run also returns the secretion rate q_ref (at the
scenario's reference growth rate) that the titer needs.
"""
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pftea.scenarios import PRODUCTS  # noqa: E402

AXES = {
    "product": list(PRODUCTS),
    "convention": ["humbird", "light", "aseptic"],
    "site": ["us_midwest", "eu_nw"],
    "titer": [2, 3, 5, 8, 12, 20, 30, 42, 60, 80, 110],
    "t_prod": [36, 48, 72, 96, 120, 168],
    "X_prod": [40, 80, 107, 140],
    "Y_ps": [0.28, 0.40, 0.465, 0.535],
}
# every product's base point is on the grid (lactoferrin: its own titer and production time; products.yaml)
import yaml  # noqa: E402
_base = yaml.safe_load((ROOT / "data/pf/base.yaml").read_text())["strain"]
_prod = yaml.safe_load((ROOT / "data/pf/products.yaml").read_text())
for _k in PRODUCTS:
    _b = _prod.get(_k) or {}
    for _ax, _leaf in (("titer", "titer_g_L"), ("t_prod", "t_prod_h")):
        _x = _b.get(f"strain.{_leaf}", {}).get("value", _base[_leaf]["value"])
        if _x not in AXES[_ax]:
            AXES[_ax] = sorted(AXES[_ax] + [_x])
GROUPS = {"capital": ["capital charge"], "maintenance + insurance": ["maintenance", "insurance"],
          "labour": ["labour"], "glucose": ["glucose"],
          "other materials": ["ammonia", "salts & other media", "DSP chemicals", "membranes", "chromatography resin",
                              "biomass disposal"],
          "utilities": ["electricity", "natural gas & steam", "water & wastewater"]}


_VESSEL: dict = {}


DETAILED_AXES = ["product", "titer", "t_prod", "X_prod"]   # yield at its base value: with secretion tied to growth it matters little


def run_detailed(point):
    """One run of the detailed sub-grid: base convention and site, detailed.yaml 'common' physics."""
    from pftea import scenarios as sc
    prod, T, tp, X = point
    Y = _base["Y_ps_g_g"]["value"]
    return run((prod, "humbird", "us_midwest", T, tp, X, Y), extra=sc.load("detailed")["common"])


def run(point, extra=None):
    from pftea import params, plant
    from pftea import scenarios as sc
    prod, conv, site, T, tp, X, Y = point
    if prod not in _VESSEL:            # the product's base-case plant (scenarios.size_fermenter), kept over the grid
        _VESSEL[prod] = params.v(sc.base_params(prod), "fermenter.volume_m3")
    ch = {"plant.product": prod, "plant.location": site, "strain.titer_g_L": float(T), "strain.t_prod_h": float(tp),
          "strain.X_prod_g_L": float(X), "strain.Y_ps_g_g": float(Y),
          "fermenter.sizing": "fixed", "fermenter.volume_m3": _VESSEL[prod], **(extra or {})}
    if conv == "light":
        ch.update(sc.LIGHT)
    elif conv == "aseptic":
        ch.update(sc.ASEPTIC)
    try:
        r = plant.evaluate(sc.base_params(prod, ch))
    except ValueError:
        return None
    if not (r.msp_ccf == r.msp_ccf) or r.msp_ccf <= 0:   # NaN guard
        return None
    g = [round(sum(r.per_kg.get(k, 0.0) for k in keys), 3) for keys in GROUPS.values()]
    flag = 0 if sc.is_feasible(r) else 1
    if any("solubility" in f for f in r.flags):
        flag = 2 if flag == 0 else flag
    if any("energetic ceiling" in f for f in r.flags):
        flag = 3
    out = [round(r.msp_ccf, 3), flag, g]
    if extra:                                          # detailed physics: the secretion the design needs
        out.append(round(r.design["q_ref_mg_g_h"], 2))
    return out


if __name__ == "__main__" and "--detailed" in sys.argv:
    t0 = time.time()
    path = ROOT / "results/explorer_grid.json"
    grid = json.loads(path.read_text())
    points = list(itertools.product(*(AXES[a] for a in DETAILED_AXES)))
    with Pool(8) as pool:
        out = pool.map(run_detailed, points, chunksize=8)
    grid["detailed"] = {"order": DETAILED_AXES, "values": out, "physics": __import__("pftea.scenarios", fromlist=["load"]).load("detailed")["common"],
                        "generated": time.strftime("%Y-%m-%d %H:%M")}
    path.write_text(json.dumps(grid, separators=(",", ":")))
    print(f"detailed: {len(points)} points in {time.time() - t0:.0f}s; failed {sum(o is None for o in out)}")
elif __name__ == "__main__":
    t0 = time.time()
    points = list(itertools.product(*AXES.values()))
    with Pool(8) as pool:
        out = pool.map(run, points, chunksize=16)
    grid = {"axes": AXES, "groups": list(GROUPS), "flags": {"0": "feasible",
            "1": "breaks a physical limit (O2 transfer, heat removal, minimum fill or specific productivity)",
            "2": "above an assumed solubility", "3": "yield above the energetic ceiling"},
            "values": out, "order": list(AXES), "generated": time.strftime("%Y-%m-%d %H:%M")}
    (ROOT / "results/explorer_grid.json").write_text(json.dumps(grid, separators=(",", ":")))
    print(f"{len(points)} points in {time.time() - t0:.0f}s; failed {sum(o is None for o in out)}")
