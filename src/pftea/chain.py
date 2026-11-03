"""One plant run as a record for the model panel (docs/panel.html): the price as checkable steps.

The panel shows a run as a chain of hand-checkable steps, a cost ledger, the physical limits and the
sugar balance. This module builds that record from plant.evaluate's Result. It adds no physics: every
number is the model's own, and the steps below are identities the model satisfies (tests/test_panel.py).

The chain (symbols as on the panel; A = annual output of target protein, H = operating hours per year):
     1  P = titer x W_end                              protein made per batch [kg] (g/L x m3 = kg)
     2  S = P x R,  R = prod(step recoveries)          protein sold per batch [kg]
     3  c = t_growth + t_prod + t_turnaround           batch cycle [h]
     4  y = S / (c V)                                  fermenter output [kg per m3 of vessel per h]
     5  n = A / S                                      batches per year
     6  N = n c / H,  N_bought = ceil(N)               fermenters needed and bought
     7  C_ferm = N_bought x price of one vessel        fermenter purchase cost [$]
     8  TCI = sum(capital table)                       plant investment [$]: equipment, installation,
                                                       buildings, engineering, fees (x cost index x location)
     9  plant $/kg = TCI (CCF + f_maint + f_ins) / A   CCF = r (1+r)^L / ((1+r)^L - 1)
    10  sugar $/kg = (glucose per kg) x glucose price
    11  price = plant + sugar + everything else         = sum of the ledger
Step 9 holds for Humbird's fixed-cost rule (the base). The location switch on the panel scales the part
of TCI that carries the location factor: TCI' = (TCI - resin first fill) f'/f + resin first fill
(plant.py block 6: the resin fill is a traded consumable, not location-scaled).

Ledger: Result.ledger, one term per (line, item): amount per kg of target protein x unit price; the
lines sum to MSP_CCF exactly (plant.py block 8).

Limits: each as (value, limit). O2: the peak production-phase OUR / OTR_max (pf_ferm, o2_use_prod;
growth is slowed to stay within it). Heat: peak heat density / heat-removal cap. Secretion: peak q_p /
q_p_max. Yield: Y_ps / energetic ceiling. Initial fill: W0 / V against the minimum fill (a lower bound).
Cell density: X at harvest against X_max (a cap the model holds, not a violation). Solubility: titer
against the practical solubility, where one is set. The verdict is the model's own flags.

Sugar balance (balances.batch_balances): the batch's glucose by use, per kg of protein sold
(per batch / S), with the protein-making share split into what is sold (x R) and what is lost
downstream (x (1 - R)), plus the seed train (glucose_seed_kg_batch / S). Their sum differs from the
simulator's total by the trapezoid error of the split (about 1%), which the panel shows.
"""
from __future__ import annotations

import math

from . import balances, plant
from . import product as pr
from .params import v


def _f(x, sig: int = 6):
    """Float rounded to sig significant digits (JSON size); non-finite -> None."""
    x = float(x)
    if not math.isfinite(x):
        return None
    return float(f"{x:.{sig}g}")


def limits(p: dict, r: plant.Result) -> list[dict]:
    d = r.design
    out = [dict(key="o2", name="O2 demand in production / O2 the tank can supply", value=d["o2_use_prod"], limit=1.0,
                unit="", kind="max", path="fermenter.otr_cap_mol_m3_h"),
           dict(key="heat", name="peak heat / heat the tank can remove", value=d["heat_peak_kW_m3"],
                limit=v(p, "fermenter.heat_removal_max_kW_m3"), unit="kW/m3", kind="max",
                path="fermenter.heat_removal_max_kW_m3")]
    qmax = plant._opt(p, "strain.q_p_max_mg_g_h")
    if qmax:
        out.append(dict(key="qp", name="secretion rate / assumed ceiling", value=d["q_p_mg_g_h"], limit=qmax,
                        unit="mg/g/h", kind="max", path="strain.q_p_max_mg_g_h"))
    out.append(dict(key="yield", name="product yield / energetic ceiling", value=v(p, "strain.Y_ps_g_g"),
                    limit=d["energetic_ceiling"], unit="g/g", kind="max", path="strain.Y_ps_g_g"))
    mf = plant._opt(p, "fermenter.min_initial_fill")
    if mf:
        out.append(dict(key="fill", name="initial fill / minimum working fill", value=d["W0_frac"], limit=mf,
                        unit="", kind="min", path="fermenter.min_initial_fill"))
    out.append(dict(key="cells", name="cells at harvest / maximum density", value=d["X_end"],
                    limit=v(p, "strain.X_max_g_L"), unit="g/L", kind="cap", path="strain.X_max_g_L"))
    sol = (pr.load(v(p, "plant.product")).get("solubility_practical_g_L") or {}).get("value")
    if sol:
        out.append(dict(key="sol", name="titer / practical solubility", value=v(p, "strain.titer_g_L"), limit=sol,
                        unit="g/L", kind="max", path="plant.product"))
    for x in out:
        x["value"], x["limit"] = _f(x["value"]), _f(x["limit"])
    return out


def sugar(p: dict, r: plant.Result) -> dict | None:
    """Glucose per kg protein sold, by use; None for a methanol-fed production phase."""
    bal = balances.batch_balances(p)
    S, R = r.design["target_per_batch_kg"], r.design["recovery"]
    out = dict(carbon_gap=_f(bal["carbon"]["gap"]), total=_f(r.physical["glucose_kg"]), uses=None)
    if bal["split"] is None:
        return out
    g = {k: x / S for k, x in bal["split"]["glucose_kg"].items()}
    make = g.pop("making the protein")
    uses = {**g, "making the protein sold": make * R, "making protein lost downstream": make * (1 - R),
            "seed train": r.design["glucose_seed_kg_batch"] / S}
    out["uses"] = {k: _f(x) for k, x in uses.items()}
    return out


def record(p: dict, r: plant.Result | None = None, with_sugar: bool = True) -> dict:
    """The panel's record of one run (module docstring)."""
    r = r or plant.evaluate(p)
    d, A = r.design, v(p, "plant.annual_target_protein_t") * 1000
    rule = plant._opt(p, "finance.fixed_cost_rule") or ("nrel" if v(p, "capital.basis") == "nrel" else "humbird")
    chain = dict(titer=d["titer"], W_end=d["W_end_m3"], P=d["product_made_kg"], R=d["recovery"],
                 S=d["target_per_batch_kg"], t_growth=d["t_growth_h"], t_prod=d["t_total_h"] - d["t_growth_h"],
                 t_turn=d["turnaround_h"], cycle=d["cycle_h"], V=d["volume_m3"], A=A, n=d["n_batches"],
                 H=d["operating_h"], N=d["N_prod"], N_bought=d["N_prod_int"], unit_cost=d["fermenter_unit_cost"],
                 C_ferm=r.capex["ISBL: production fermenters"], tci=r.tci, resin_fill=d["resin_fill"],
                 ccf=d["ccf"], f_maint=v(p, "finance.maintenance_frac_tci"), f_ins=v(p, "finance.insurance_tax_frac_tci"),
                 location_factor=d["location_factor"], cost_index=d["cost_index"],
                 glucose_per_kg=r.physical["glucose_kg"], glucose_price=v(p, "utilities.glucose_usd_kg"),
                 ccf_rate=v(p, "finance.ccf_rate"), ccf_life=v(p, "finance.ccf_life_y"),
                 X_prod=v(p, "strain.X_prod_g_L"), q_p=d["q_p_mg_g_h"], Y_ps=v(p, "strain.Y_ps_g_g"),
                 W0=d["W0_m3"], salary_years=d["salary_years"])
    rec = dict(ok=r.ok, flags=r.flags, msp=_f(r.msp_ccf), cop=_f(r.cop), dcf=_f(r.msp_dcf), per_kg_powder=_f(r.per_kg_powder),
               rule=rule, per_kg={k: _f(x) for k, x in r.per_kg.items()},
               ledger=[[t["line"], t["item"], _f(t["amount"] / A), t["unit"], _f(t["price"]), t["path"]]
                       for t in r.ledger if t["amount"] != 0],
               capex={k: _f(x) for k, x in r.capex.items() if x},
               recovery_steps={k: _f(x) for k, x in d["recovery_steps"].items()},
               chain={k: _f(x) for k, x in chain.items()}, limits=limits(p, r),
               inputs=dict(host=v(p, "strain.host"), spec=v(p, "plant.spec"), location=v(p, "plant.location"),
                           methanol=bool(plant._opt(p, "strain.methanol_frac_prod", 0.0))),
               physical={k: _f(x) for k, x in r.physical.items()})
    if with_sugar:
        rec["sugar"] = sugar(p, r)
    return rec
