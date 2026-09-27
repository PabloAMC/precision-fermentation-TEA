"""Calibration anchors 2-4: run the model on each anchor's own process inputs.

Structure (cost curves, installation factors, labour model, maintenance and insurance fractions)
is never changed here: only the process inputs, prices, cost year and financing of the anchor,
listed in data/calibration/<anchor>.yaml. Anchor 1 (baker's yeast) is humbird_yeast.py.
Results and misses are recorded in docs/VALIDATION.md before anything is fixed.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from . import finance as fin
from . import params, plant
from .params import v

ROOT = Path(__file__).resolve().parents[2]


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / f"data/calibration/{name}.yaml").read_text())


# The anchors' own ('light') conventions, for the convention rows of docs/VALIDATION.md.
LIGHT = {"capital.basis": "nrel"}   # NREL-style capital basis and fixed costs


def voutilainen_conventions(capital_basis: str) -> dict:
    """Voutilainen's fixed costs (maintenance 1.5% of FCI, no insurance) on either capital basis."""
    nb = dict(params.load()["capital"]["nrel_basis"]["value"], maintenance_frac_isbl=0.0, maintenance_frac_fci=0.015,
              insurance_frac_fci=0.0)
    if capital_basis == "nrel":
        return {"capital.basis": "nrel", "capital.nrel_basis": {"value": nb}}
    return {"finance.maintenance_frac_tci": 0.015, "finance.insurance_tax_frac_tci": 0.0}


def run(name: str, extra: dict | None = None) -> dict:
    """Run one anchor; `extra` overrides are applied on top of the case (convention rows only)."""
    case = load(name)
    p = params.override(params.load(), {**case["overrides"], **(extra or {})})
    r = plant.evaluate(p)
    out = {"result": r, "case": case, "params": p}
    if name == "nrel2011_cellulase":
        d = case["finance_debt"]
        variable = sum(val for k, val in r.annual.items()
                       if k not in ("labour", "maintenance", "insurance", "capital charge"))
        fixed = r.annual["labour"] + r.annual["maintenance"] + r.annual["insurance"]
        kg = v(p, "plant.annual_target_protein_t") * 1000
        msp = fin.msp_dcf(r.tci, variable, fixed, kg, irr=v(p, "finance.dcf_irr"), life=v(p, "finance.dcf_life_y"),
                          tax=v(p, "finance.tax_rate"), wc_frac=v(p, "finance.working_capital_frac_fci"),
                          debt_frac=d["debt_frac"], loan_rate=d["loan_rate"], loan_years=d["loan_years"])
        per_delivered = msp / case["delivered_fraction"]["value"]
        tg = case["target"]
        out["compare"] = {
            "usd_per_kg_protein (DCF, NREL financing)": (per_delivered, tg["usd_per_kg_protein"]["value"]),
            "glucose_kg_per_kg": (r.physical["glucose_kg"] / case["delivered_fraction"]["value"], tg["glucose_kg_per_kg"]["value"]),
            "electricity_kWh_per_kg": (r.physical["electricity_kWh"], tg["electricity_kWh_per_kg"]["value"]),
            "o2_mol_per_kg": (r.physical["o2_kg"] * 1000 / 32, tg["o2_mol_per_kg"]["value"]),
        }
    elif name == "intelligen2025_ova":
        tg = case["target"]
        out["compare"] = {
            "usd_per_kg_powder (Humbird convention)": (r.per_kg_powder, tg["usd_per_kg_powder_humbird_convention"]["value"]),
            "TCI_usd": (r.tci, tg["tci_usd"]["value"]),
            "glucose_kg_per_kg_powder": (r.physical["glucose_kg"] * r.per_kg_powder / r.msp_ccf,
                                         tg["glucose_kg_per_kg_powder"]["value"]),
            "electricity_kWh_per_kg_powder": (r.physical["electricity_kWh"] * r.per_kg_powder / r.msp_ccf,
                                              tg["electricity_kWh_per_kg_powder"]["value"]),
        }
    elif name == "voutilainen2021_case":
        fx = case["fx_usd_per_eur"]
        target_ratio = case["sugar_per_kg_protein_in_broth"]
        # match the anchor's stated sugar use (a process input) by solving the product-reaction yield
        lo, hi = 0.12, 0.6
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            b = plant.batch(params.override(p, {"strain.Y_ps_g_g": mid}))
            if b.glucose_kg / b.product_kg > target_ratio:
                lo = mid
            else:
                hi = mid
        p = params.override(p, {"strain.Y_ps_g_g": 0.5 * (lo + hi)})
        r = plant.evaluate(p)
        out.update(result=r, params=p)
        f = case["finance"]
        variable = sum(val for k, val in r.annual.items()
                       if k not in ("labour", "maintenance", "insurance", "capital charge"))
        fixed = r.annual["labour"] + r.annual["maintenance"] + r.annual["insurance"]
        kg = v(p, "plant.annual_target_protein_t") * 1000
        msp = fin.msp_dcf_voutilainen(r.tci, variable, fixed, kg, rate=f["rate"], life=f["life"], tax=f["tax"],
                                      capital_factor=f["capital_factor"], inflation=f["inflation"],
                                      opex_growth=f["opex_growth"], startup_revenue=f["startup_revenue"],
                                      startup_variable=f["startup_variable"], byproduct=f["byproduct"])
        tg = case["target"]
        out["compare"] = {
            "EUR_per_t_protein (their DCF)": (msp / fx * 1000, tg["eur_per_t_protein_dcf"]["value"]),
            "sugar_kg_per_kg_protein": (r.physical["glucose_kg"], tg["sugar_kg_per_kg_protein"]["value"]),
            "TCI vs their FCI (EUR)": (r.tci / fx, tg["fci_eur"]["value"]),
        }
        out["solved_Y_ps"] = 0.5 * (lo + hi)
    out["tolerance"] = case["target"]["tolerance"]
    return out


def report(name: str) -> str:
    o = run(name)
    lines = [f"{name}: flags {o['result'].flags or 'none'}"]
    for k, (ours, theirs) in o["compare"].items():
        lines.append(f"  {k:42s} ours {ours:14.4g}  anchor {theirs:14.4g}  {100 * (ours / theirs - 1):+6.1f}%")
    return "\n".join(lines)


if __name__ == "__main__":
    for n in ("nrel2011_cellulase", "intelligen2025_ova", "voutilainen2021_case"):
        print(report(n))
