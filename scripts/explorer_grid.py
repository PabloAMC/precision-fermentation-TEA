"""Precompute the explorer's grid: MSP and cost structure over the main levers.

The explorer (docs/explorer.html) never re-implements the model in JavaScript: it looks up
this grid, so every number it shows is a real model run. Grid:
    product x capital convention x site x titer x production time x cell density x yield.
Each product runs on its own base case (data/pf/products.yaml: lactoferrin at 250 t/yr with cation
exchange; BLG and OVA at 10 kt/yr); the grid axes override titer, time, cells and yield.
Run:  .venv/bin/python scripts/explorer_grid.py   (parallel; writes results/explorer_grid.json)
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
GROUPS = {"capital": ["capital charge"], "maintenance + insurance": ["maintenance", "insurance"],
          "labour": ["labour"], "glucose": ["glucose"],
          "other materials": ["ammonia", "salts & other media", "DSP chemicals", "membranes", "chromatography resin",
                              "biomass disposal"],
          "utilities": ["electricity", "natural gas & steam", "water & wastewater"]}


def run(point):
    from pftea import params, plant
    from pftea import scenarios as sc
    prod, conv, site, T, tp, X, Y = point
    ch = {"plant.product": prod, "plant.location": site, "strain.titer_g_L": float(T), "strain.t_prod_h": float(tp),
          "strain.X_prod_g_L": float(X), "strain.Y_ps_g_g": float(Y)}
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
    return [round(r.msp_ccf, 3), flag, g]


if __name__ == "__main__":
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
