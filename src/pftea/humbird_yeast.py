"""Calibration anchor 1: Humbird's baker's-yeast plant (SI sheet A.1), ported cell by cell.

This is the software check of the method we build on. Given the same inputs
(data/calibration/humbird_bakers_yeast.yaml) it must reproduce Humbird's cost of
production. It then serves as a reality check against the market-implied cost.

Structure, following the sheet:
1. Fed-batch simulation of one production bubble column (fermentation.FedBatch).
2. Seed train, rows 107-133. Each seed stage makes the starting cells of the next with the
   same number of doublings; splits 3, 2, 1, 1, ... Stages are classed by volume: large seed
   above 5,000 L, small seed above 100 L, lab above 0.001 kg of cells.
3. Equipment sizing and purchased costs, rows 142-174. Abbreviated list plus a 20%
   allowance for missing items; TCI = Lang factor 4.5 x purchased cost.
4. Variable costs per batch: sugar, ammonia, water, electricity, steam, wastewater.
   Seed-train consumption is added by scaling production-vessel integrals by
   (1 + initial cells / net cell growth).
5. Labour: operator attention per batch plus continuous-area staff and supervisors,
   x 4.5 hires per 24/7 position, x 2 for burden.
6. Fixed costs: maintenance 4% and insurance+tax 5% of TCI per year. Capital charge
   CCF = i / (1 - (1+i)^-n) with i = 10%, n = 20 years.
Cost of production (COP) = (variable + fixed + capital charge) / annual output.
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import yaml

from . import fermentation as fm
from . import thermo as th
from .fermentation import xround

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "data/calibration/humbird_bakers_yeast.yaml"


def _v(x):
    return x["value"] if isinstance(x, dict) and "value" in x else x


@lru_cache(maxsize=None)
def load_case(path: str = str(CASE)) -> dict:
    return yaml.safe_load(Path(path).read_text())


def ceiling(x: float) -> int:
    return int(math.ceil(x - 1e-12))


def simulate(case: dict) -> dict:
    """Run the production fed-batch and return the time integrals and maxima A.1 uses."""
    bio_f = case["biology"]["biomass_formula"]
    model = th.GrowthModel(th.biomass(bio_f["C"], bio_f["H"], bio_f["O"], bio_f["N"]),
                           th.get(case["biology"]["carbon_source"]), _v(case["biology"]["temperature_C"]))
    f = case["fermenter"]
    k = f["kla_consts"]
    vessel = fm.BubbleColumn(_v(f["volume_L"]), _v(f["diameter_m"]), k["a"], k["b"], k["c"], k["d"])
    broth = fm.Broth(T_C=_v(case["biology"]["temperature_C"]), p_back_bar=_v(f["back_pressure_bar"]),
                     DO_top_frac=_v(f["DO_top_frac_of_air_sat"]),
                     cell_wet_pg=_v(case["biology"]["cell_wet_mass_pg"]),
                     cell_dry_frac=_v(case["biology"]["cell_dry_fraction"]),
                     substrate_wt_frac=_v(f["substrate_wt_frac"]))
    fb = fm.FedBatch(vessel, broth, fm.GrowthKinetics(model), W0_L=_v(f["start_volume_L"]),
                     X0_gL=_v(f["start_density_gL"]),
                     mu_max=np.log(2) / _v(case["biology"]["doubling_time_h"]),
                     otr_max=_v(f["otr_max_mol_m3_h"]), wv_max=_v(f["max_working_volume"]))
    steps = fb.run()
    rt = _v(case["prices_2018"]["rt_refrig_kW_per_kW"])
    p_max = max(s.gas["p_btm"] for s in steps)
    comp = [fm.compressor_kW(s.D, p_max) for s in steps]
    refr = [fm.refrigeration_kW(s, model.bio, rt) for s in steps]
    t_end = steps[-1].t
    return dict(
        steps=steps, model=model,
        glc_kg=fm.integrate(steps, [s.glc_kg_h for s in steps]),                 # H282
        nh3_kmol=fm.integrate(steps, [s.rates.get("NH3 (aq)") for s in steps]),  # M282
        water_prod_kg=fm.integrate(steps, [s.water_prod_kg_h for s in steps]),   # O282
        stripped_kg=fm.integrate(steps, [s.stripped_kg_h for s in steps]),       # Q282
        comp_kWh=fm.integrate(steps, comp),                                      # BD282
        refr_kWh=fm.integrate(steps, refr),                                      # BF282
        refr_avg_kW=fm.integrate(steps, refr) / t_end,                           # BF283
        refr_max_kW=max(refr),                                                   # BF286
        p_btm_max=p_max,                                                         # Z286
        W_max=max(s.W for s in steps),                                           # W286
        scfm_max=max(s.D * 2.2 / 60 * 359 for s in steps),                       # BI286
        glc_max_kg_h=max(-s.glc_kg_h for s in steps),                            # BL286
        D_max=max(s.D for s in steps),                                           # D286
        F0=steps[0].F, F_end=steps[-1].F, t_end=t_end,
        X_end=max(s.gas["X"] for s in steps),                                    # AA286
    )


def seed_train(case: dict, sim: dict) -> list[dict]:
    p, f = case["plant"], case["fermenter"]
    V = _v(f["volume_L"])
    D0 = _v(f["start_volume_L"]) / V
    X0 = _v(f["start_density_gL"])
    H = _v(f["max_working_volume"])
    I = sim["X_end"]
    n_prod = _v(p["production_fermenters"])
    online, turn = sim["t_end"], _v(p["turnaround_h"])
    C = V * D0 * X0 / 1000
    G = V * H * I / 1000
    doublings = math.log(G / C) / math.log(2)
    eq = case["equipment"]["bcr_seed"]
    rows = [dict(kind="Production", B=V, C=C, G=G, K=n_prod, J=None)]
    splits = list(_v(p["seed_splits"]))
    for i in range(26):  # rows 108-133
        J = splits[i] if i < len(splits) else 1
        prev = rows[-1]
        G_r = prev["C"] * J
        C_r = G_r / math.exp(doublings * math.log(2))
        B_r = G_r * 1000 / I / H
        K_r = math.ceil(prev["K"] / J - 1e-12)
        kind = ("Large seed" if B_r > _v(p["large_seed_min_L"]) else
                "Small seed" if B_r > _v(p["small_seed_min_L"]) else
                "Lab" if C_r > _v(p["lab_min_kg"]) else "")
        rows.append(dict(kind=kind, B=B_r, C=C_r, G=G_r, K=K_r, J=J))
    att = case["labour"]["attention"]
    for r in rows:
        r["capex"] = (xround(r["B"] ** eq["n"] * eq["A"], -3) * r["K"]
                      if r["kind"] not in ("", "Lab") else 0.0)
        r["O"] = xround(turn + online) if r["kind"] else 0
        r["Q"] = r["K"] * online / r["O"] * r["B"] / V if r["O"] else 0.0
        frac = {"Production": att["production"] * r["O"], "Large seed": att["large_seed"] * r["O"],
                "Small seed": att["small_seed"] * r["O"], "Lab": att["lab_min_per_step"] / 60}.get(r["kind"], 0.0)
        r["T"] = frac * r["K"] / n_prod
    return rows


def run(case: dict | None = None) -> dict:
    case = case or load_case()
    sim = simulate(case)
    rows = seed_train(case, sim)
    p, f, eq, pr, lab, fin = (case["plant"], case["fermenter"], case["equipment"],
                              case["prices_2018"], case["labour"], case["finance"])
    out: dict = {"sim": sim, "seed": rows}
    n_prod = _v(p["production_fermenters"])
    O107 = rows[0]["O"]
    batches = ceiling(1 / O107 * 24 * _v(p["operating_days"]) * n_prod)                 # H101
    annual_t = batches * sim["F_end"] / 1000                                            # H102
    Q134 = sum(r["Q"] for r in rows)
    G136 = O107 / n_prod
    G137 = _v(p["shift_h"]) / G136
    trains = 1 if G137 <= _v(p["train_threshold_batches_per_shift"]) else ceiling(
        G137 / _v(p["train_threshold_batches_per_shift"]))
    ws = _v(f["substrate_wt_frac"])
    # ------------------------------------------------------------ sizing (rows 142-158)
    past_Lh = sim["glc_max_kg_h"] / ws * Q134 / trains                                  # C144
    n_past = ceiling(past_Lh / eq["pasteurizer"]["max"])                                # F144
    tank_m3 = sim["glc_max_kg_h"] / ws * _v(p["prep_residence_h"]) / 1000 * Q134 / trains  # F145
    comp_acmh = Q134 * sim["D_max"] * 0.08314 * 298 / trains                            # C146
    n_comp = ceiling(comp_acmh / eq["compressor"]["max"])                               # F146
    solids_kg_h = sim["F_end"] / _v(p["centrifuge_h_per_batch"])                        # C148
    cent_kg_h = sim["W_max"] / _v(p["centrifuge_h_per_batch"])                          # E149
    n_cent = ceiling(cent_kg_h / eq["centrifuge"]["max_kg_h"])                          # G149
    rvf_kg_h = solids_kg_h / _v(p["centrifuge_solids"])                                 # E150
    rvf_m2 = rvf_kg_h * eq["rvf"]["area_m2_h_kg"]                                       # C150
    n_rvf = ceiling(rvf_kg_h / eq["rvf"]["max_kg_h"])                                   # G150
    rvf_water = solids_kg_h / _v(p["rvf_solids"]) * (1 - _v(p["rvf_solids"]))           # K150
    steam_past = sim["W_max"] * 4.1868 * _v(p["pasteurizer_dT_C"]) / fm.H2O_VAP_HEAT     # E152
    steam_sip = _v(eq["steam_per_L_vessel_kg"]) * (
        _v(f["volume_L"]) + sum(r["B"] / r["J"] for r in rows[1:24]))                   # E153
    steam = steam_past + steam_sip                                                      # E154
    rt = _v(pr["rt_refrig_kW_per_kW"])
    chill_avg_GJ_h = sim["refr_avg_kW"] / rt * Q134 * 3600 / 1e6                        # E156
    past_cool_GJ_h = past_Lh * 4.1868 * _v(p["pasteurizer_dT_C"]) / 1e6                 # E157
    cw_kcal_s = (chill_avg_GJ_h + past_cool_GJ_h) / 3600 * 238845.89663                 # G158
    cw_L_s = cw_kcal_s / _v(p["cooling_water_dT_C"])                                    # I158
    # ------------------------------------------------------------ equipment (rows 164-174)
    bcr = xround(_v(f["bcr_quote_2018usd"]) + eq["sparger"]["a"] + eq["sparger"]["b"] * sim["scfm_max"], -3)
    items = {
        "production_bioreactor": bcr * n_prod,
        "seed_fermenters": sum(r["capex"] for r in rows[1:]),
        "pasteurizer": xround((past_Lh / n_past) ** eq["pasteurizer"]["n"] * eq["pasteurizer"]["A"], -3)
                       * n_past * trains,
        "prep_tank": xround(tank_m3 ** eq["tank"]["n"] * eq["tank"]["A"], -3) * trains,
        "air_compressor": xround(comp_acmh / n_comp * eq["compressor"]["slope"]
                                 + eq["compressor"]["intercept"], -3) * n_comp * trains,
        "centrifuge": xround(eq["centrifuge"]["A"] * (cent_kg_h / 3.785 / 60 / n_cent) ** eq["centrifuge"]["n"], -3)
                      * n_cent * trains,
        "rvf": xround(eq["rvf"]["A"] * (rvf_kg_h / n_rvf) ** eq["rvf"]["n"], -3) * n_rvf,
    }
    listed = sum(items.values())                                                        # I171
    missing = xround(listed / (1 - _v(p["missing_capital_frac"])) * _v(p["missing_capital_frac"]), -3)
    pec = listed + missing                                                              # I173
    tci = _v(p["lang_factor"]) * pec                                                    # I174
    # ------------------------------------------------------------ variable costs per batch
    seedf = 1 + sim["F0"] / (sim["F_end"] - sim["F0"])                                  # 1 + F287/F284
    ferm_water = (sim["W_max"] + sim["stripped_kg"] - sim["water_prod_kg"] - sim["F_end"]) * seedf  # C178
    end_water = sim["W_max"] - sim["F_end"]                                             # C187
    ww = end_water - rvf_water                                                          # C189
    wash = ww * _v(p["wash_water_frac"])                                                # C179
    proc_water = ferm_water + wash + steam_sip                                          # C181
    evap_kg_h = cw_kcal_s * 4.1868 * 3600 / fm.H2O_VAP_HEAT                             # E183
    well_kg = (evap_kg_h + cw_L_s * 3600 * _v(p["blowdown_frac"])) * G136               # C185
    wastewater_m3 = (ww + wash) / 1000                                                  # C191/1000
    kWh = {"compressor": sim["comp_kWh"] * seedf,                                       # C193
           "chiller": sim["refr_kWh"] * seedf,                                          # C194
           "centrifuge": eq["centrifuge_kWh_m3"]["value"] * sim["W_max"] / 1000,        # C196
           "rvf": rvf_m2 ** eq["rvf_power"]["n"] * eq["rvf_power"]["A"] * n_rvf * rvf_m2 * G136}  # C197
    F286 = sim["F_end"]
    per_kg = {
        "carbon": sim["glc_kg"] * seedf * _v(pr["molasses_glc_equiv_usd_kg"]) / F286,
        "nitrogen": sim["nh3_kmol"] * 17 * seedf * _v(pr["ammonia_usd_kg"]) / F286,
        "water": (proc_water + well_kg) / 1000 * _v(pr["well_water_usd_kg"]) * 1000 / F286,
        "electricity": sum(kWh.values()) * _v(pr["electricity_usd_kWh"]) / F286,
        "steam": steam / 1000 * _v(pr["lp_steam_usd_t"]) / F286,
        "wastewater": wastewater_m3 * _v(pr["wastewater_usd_m3"]) / F286,
    }
    # ------------------------------------------------------------ labour (rows 227-247)
    eff, shift = _v(lab["worker_efficiency"]), _v(p["shift_h"])
    batch_fte = {}
    for kind in ("Lab", "Small seed", "Large seed", "Production"):
        h = sum(r["T"] for r in rows if r["kind"] == kind) / eff
        batch_fte[kind] = xround(h / shift * G137, 1)
    cont = lab["continuous_fte"]
    cont_fte = (xround(trains * cont["media_prep_per_train"], 1) + xround(trains * cont["centrifuge_per_train"], 1)
                + xround(n_rvf * cont["rvf_each"], 1) + xround(1 * cont["boiler_each"], 1)
                + xround(trains * cont["maintenance_per_train"], 1))
    batch_total = sum(batch_fte.values())
    sup = (cont_fte + batch_total) / _v(lab["employees_per_supervisor"])
    per_shift = xround((batch_total + cont_fte) * _v(lab["operator_salary"]) + sup * _v(lab["supervisor_salary"]), -3)
    all_shifts = xround(per_shift * _v(lab["shifts_per_position"]), -3)
    labour = all_shifts + xround(all_shifts * _v(lab["burden"]), -3)
    fte_total = (batch_total + cont_fte + sup) * _v(lab["shifts_per_position"])
    maint = xround(_v(fin["maintenance_frac_tci"]) * tci, -3)
    ins = xround(_v(fin["insurance_tax_frac_tci"]) * tci, -3)
    i, n = _v(fin["irr"]), _v(fin["lifetime_y"])
    ccf = i / (1 - (1 + i) ** -n)
    annual_kg = annual_t * 1000
    fixed = {"labour": labour / annual_kg, "maintenance": maint / annual_kg, "insurance_tax": ins / annual_kg}
    capital = tci * ccf / annual_kg
    cop = sum(per_kg.values()) + sum(fixed.values()) + capital
    out.update(batches=batches, annual_t=annual_t, trains=trains, Q134=Q134, items=items, pec=pec, tci=tci,
               per_kg=per_kg, fixed=fixed, capital_per_kg=capital, ccf=ccf, cop=cop, fte=fte_total,
               kWh=kWh, steam_kg=steam, sizing=dict(past_Lh=past_Lh, tank_m3=tank_m3, comp_acmh=comp_acmh,
               cent_kg_h=cent_kg_h, rvf_m2=rvf_m2, cw_L_s=cw_L_s, well_kg=well_kg, proc_water=proc_water))
    return out


if __name__ == "__main__":
    r = run()
    print(f"COP ${r['cop']:.3f}/kg dry (Humbird A.1: $1.89); TCI ${r['tci']/1e6:.2f}M; "
          f"{r['annual_t']:.0f} t/yr; FTE {r['fte']:.1f}")
