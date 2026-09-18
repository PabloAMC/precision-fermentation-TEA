"""Sample every parameter with low/high from triangular(low, base, high),
run the pipeline N times, return a DataFrame of outputs plus sampled inputs.
Fixed-value parameters (no low/high) stay at base.
"""
import copy
import numpy as np
import pandas as pd
from . import params, pipeline


def _sample_block(block, rng):
    if isinstance(block, dict) and "value" in block and "low" in block:
        return float(rng.triangular(block["low"], block["value"], block["high"]))
    return block["value"] if isinstance(block, dict) and "value" in block else block


def sample(raw: dict, rng) -> dict:
    p = {}
    for section, prm in raw.items():
        if section == "downstream":
            p[section] = {
                "steps": [{"name": s["name"], "recovery": _sample_block(s["recovery"], rng)}
                          for s in prm["steps"]],
                "dsp_capex_multiplier": _sample_block(prm["dsp_capex_multiplier"], rng),
            }
        elif isinstance(prm, dict):
            p[section] = {k: _sample_block(v, rng) for k, v in prm.items()}
        else:
            p[section] = prm
    return p


def run(n: int = 2000, seed: int = 0, raw: dict | None = None) -> pd.DataFrame:
    raw = raw or params.load()
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        p = sample(raw, rng)
        r = pipeline.run(p)
        rows.append({"titer": p["strain"]["titer_g_per_L"],
                     "yield": p["strain"]["yield_g_per_g_sugar"],
                     "recovery": r["overall_recovery"],
                     "sugar_price": p["opex"]["sugar_price_usd_kg"],
                     "cop": r["cop_usd_kg"], "msp": r["msp_usd_kg"]})
    return pd.DataFrame(rows)


def summary(df: pd.DataFrame) -> pd.Series:
    return df["msp"].quantile([0.1, 0.5, 0.9]).rename({0.1: "p10", 0.5: "p50", 0.9: "p90"})
