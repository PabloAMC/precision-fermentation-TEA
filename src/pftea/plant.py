"""A precision-fermentation plant, from strain performance to $/kg of target protein.

Blocks (data in data/pf/base.yaml; equations in each block's comments):
1. Production batch (pf_ferm.run_batch): titer, cells, glucose, O2, power, heat.
2. Downstream, per batch: cell removal (dilute to 45 g/L cells, disk-stack centrifuges
   or filter press) -> MF polish -> UF concentrate + diafiltration -> [precipitation for
   the isolate] -> spray dryer. Target protein out = in x product of step recoveries.
   UF retention = CF^-(1-sigma) exp(-N_DV (1-sigma)).
3. Scale: batches/yr = annual target protein / target per batch. Production fermenters
   N = batches/yr x (batch time + turnaround) / operating hours; kept continuous for smooth
   curves, integer count reported.
4. Seed train: 10:1 volume steps down to lab scale; seed cells grown on the growth
   stoichiometry; units per stage from occupancy.
5. Utilities: compressors (peak air of running fermenters), chillers (peak heat), cooling
   tower (heat rejected), boiler (sterilisation steam), water treatment.
6. Capital (Humbird 2021 facility-class method, 'commodity aerobic'):
       ISBL TDC = PEC_ISBL (1 + m) (1 + f_ISBL);  OSBL TDC = PEC_OSBL (1 + m) (1 + f_OSBL)
       buildings = sum(area x levels x $/m2 by class)
       TDC = ISBL + OSBL + buildings; TPC = TDC (1 + E&C); TCI = TPC (1 + fees & contingency)
   with m = missing-capital allowance (m = 0.1/0.9). All 2018$ x cost index.
7. Operating costs: raw materials, utilities, consumables, waste; labour (Humbird's operator
   attention model); maintenance 4% and insurance + tax 5% of TCI.
8. Money: COP (operating + straight-line depreciation), MSP_CCF (Humbird capital charge),
   MSP_DCF (NREL-style DCF). Reported per kg target protein and per kg powder.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from . import equipment as eq
from . import finance as fin
from . import pf_ferm as pf
from . import product as pr
from . import thermo as th
from .params import v

HEAT_PER_MOL_O2_KJ = 460.0


@dataclass
class Result:
    ok: bool
    flags: list
    per_kg: dict                      # $/kg target protein by category (MSP_CCF basis)
    cop: float
    msp_ccf: float
    msp_dcf: float
    per_kg_powder: float
    tci: float
    capex: dict
    annual: dict                      # annual $ by category
    physical: dict                    # intensities per kg target protein
    design: dict                      # sizes and counts
    batch: pf.Batch = field(repr=False, default=None)


def _host(p) -> pf.Host:
    h = f"hosts.{v(p, 'strain.host')}"
    f = v(p, f"{h}.biomass_formula")
    return pf.Host(bio=th.biomass(f["C"], f["H"], f["O"], f["N"]), mu_max=v(p, f"{h}.mu_max_per_h"),
                   T_C=v(p, f"{h}.temperature_C"), maint_factor=v(p, f"{h}.maint_factor"))


def _vessel(p, volume=None) -> pf.STR:
    h = f"hosts.{v(p, 'strain.host')}"
    return pf.STR(volume_m3=volume or v(p, "fermenter.volume_m3"), h_to_d=v(p, "fermenter.h_to_d"),
                  fill_max=v(p, "fermenter.fill_max"), kla_factor=v(p, f"{h}.kla_factor"),
                  pv_max=v(p, "fermenter.pv_max_W_m3"), us_max=v(p, "fermenter.us_max_m_s"),
                  otr_cap=v(p, "fermenter.otr_cap_mol_m3_h"),
                  heat_max_kW_m3=v(p, "fermenter.heat_removal_max_kW_m3"))


def batch(p, keep_series=False) -> pf.Batch:
    host = _host(p)
    c = pf.Conditions(T_C=host.T_C, rt_refrig=v(p, "utilities.rt_refrig"))
    strain = pf.Strain(product=pr.protein(v(p, "plant.product")), Y_ps=v(p, "strain.Y_ps_g_g"),
                       X_prod=v(p, "strain.X_prod_g_L"), mu_prod=v(p, "strain.mu_prod_per_h"),
                       t_prod=v(p, "strain.t_prod_h"), X_max=v(p, "strain.X_max_g_L"))
    return pf.run_batch(_vessel(p), c, host, strain, X0=v(p, "strain.X0_g_L"),
                        titer=v(p, "strain.titer_g_L"), w_s=v(p, "fermenter.feed_glucose_wt"),
                        keep_series=keep_series)


def evaluate(p, keep_series=False) -> Result:
    flags = []
    idx = v(p, "capital.cost_index_2018_to_2025")
    b = batch(p, keep_series)
    if not b.ok:
        flags.append(b.reason)
    vessel = _vessel(p)
    c = pf.Conditions(T_C=_host(p).T_C, rt_refrig=v(p, "utilities.rt_refrig"))
    omax = pf.otr_max(vessel, c)
    heat_cap = v(p, "fermenter.heat_removal_max_kW_m3")
    if heat_cap and b.heat_max_kW_m3 > heat_cap * 1.02:
        flags.append(f"heat {b.heat_max_kW_m3:.1f} > {heat_cap} kW/m3 removable")
    key = v(p, "plant.product")
    sol = pr.load(key).get("solubility_practical_g_L", {}) or {}
    if isinstance(p.get("plant", {}).get("solubility_override_g_L"), dict):   # sensitivity runs only
        sol = {"value": p["plant"]["solubility_override_g_L"]["value"]}
    if sol.get("value") and v(p, "strain.titer_g_L") > sol["value"]:
        flags.append(f"titer above practical solubility ({sol['value']} g/L)")
    glc = th.get("Glucose (s)")
    ceiling = pr.energetic_ceiling(pr.protein(key), glc, 4.0, 28)   # most permissive: 4 ATP/bond (sourced), P/O-high
    if v(p, "strain.Y_ps_g_g") > ceiling:
        flags.append(f"Y_ps above the energetic ceiling {ceiling:.2f} g/g")

    # ---------------------------------------------------------------- 2. downstream per batch
    spec = v(p, "plant.spec")
    W = b.W_end                                            # m3 broth
    X = b.X_end                                            # kg/m3 cells
    P_in = b.product_kg
    if not (np.isfinite(P_in) and P_in > 0):
        raise ValueError("batch makes no product")
    dil = max(X / v(p, "dsp.dilution_to_g_L_cells"), 1.0)
    V_cent = W * dil                                       # m3 to centrifuges
    R_cell = v(p, "dsp.recovery_cell_removal")
    V_clar = V_cent * (1 - X / dil / 1000 / v(p, "dsp.wet_cells_solids") * 1.0)  # liquid after solids
    R_mf = v(p, "dsp.mf_recovery")
    sigma = v(p, "dsp.uf_rejection")
    C_in = P_in * R_cell * R_mf / V_clar                   # kg/m3
    C_end = v(p, "dsp.uf_end_g_L")
    if key == "ova":
        C_end = min(C_end, sol.get("value") or C_end)
    CF = max(C_end / max(C_in, 1e-9), 1.0)
    V_ret = V_clar / CF
    N_dv = v(p, "dsp.diafiltration_volumes")
    R_uf = CF ** -(1 - sigma) * math.exp(-N_dv * (1 - sigma))
    permeate = (V_clar - V_ret) + N_dv * V_ret             # m3 incl. DF
    target = P_in * R_cell * R_mf * R_uf
    if spec == "crude":                                   # whole broth used as is (NREL on-site enzyme)
        R_cell = R_mf = R_uf = 1.0
        V_cent = V_clar = V_ret = W
        permeate, CF, dil = 0.0, 1.0, 1.0
        target = P_in
    if spec == "isolate":
        R_pre = v(p, "dsp.precip_recovery")
        target *= R_pre
        AS_kg = v(p, "dsp.ammonium_sulfate_kg_per_m3") * V_ret * (1 - v(p, "dsp.ammonium_sulfate_recycled_frac"))
        wash_m3 = 6 * V_ret
        purity = v(p, "dsp.isolate_target_frac_dry")
    else:
        AS_kg, wash_m3 = 0.0, 0.0
        purity = v(p, "dsp.concentrate_target_frac_dry")
    if spec == "crude":
        purity, water_evap = target / (target + b.cells_kg), 0.0
        powder = target
    else:
        solids = target / purity                           # kg dry solids to dryer
        dryer_in_solids = max(v(p, "dsp.dryer_inlet_solids"), solids / (V_ret * 1000 + solids))   # UF retentate
        water_evap = solids / dryer_in_solids * (1 - dryer_in_solids)
        target *= v(p, "dsp.dryer_recovery")
        powder = target / purity / (1 - v(p, "dsp.powder_moisture"))
    R_total = target / P_in

    # ---------------------------------------------------------------- 3. scale
    H = v(p, "plant.operating_days") * 24
    annual_target_kg = v(p, "plant.annual_target_protein_t") * 1000
    n_batches = annual_target_kg / target
    cycle = b.t_total + v(p, "fermenter.turnaround_h")
    N_prod = n_batches * cycle / H
    running = n_batches * b.t_total / H                    # fermenters online on average

    # ---------------------------------------------------------------- 4. seed train
    host = _host(p)
    g = host.growth
    ratio = v(p, "fermenter.seed_ratio")
    X_seed = v(p, "fermenter.seed_final_X_g_L")
    F0 = b.W0 * v(p, "strain.X0_g_L")                      # kg cells to inoculate
    seeds, vol = [], F0 / X_seed / v(p, "fermenter.fill_max")
    while vol >= 0.05:
        seeds.append(vol)
        vol *= ratio
    mu_s = 0.75 * host.mu_max
    glc_per_kg_cells = -(g.q("Glucose (s)", mu_s) / mu_s) * glc.mw / g.bio.mw
    o2_per_kg_cells = -(g.q("O2 (aq)", mu_s) / mu_s) / g.bio.mw * 1000       # mol/kg
    seed_cells = F0 * (1 + ratio)                                          # all stages
    seed_glc = seed_cells * glc_per_kg_cells
    seed_o2_kmol = seed_cells * o2_per_kg_cells / 1000
    kwh_per_kmol_o2 = (b.comp_kWh + b.agit_kWh + b.heat_kWh * c.rt_refrig) / b.o2_kmol
    seed_kWh = seed_o2_kmol * kwh_per_kmol_o2
    t_seed = v(p, "fermenter.seed_time_h") + v(p, "fermenter.turnaround_h")
    if not np.isfinite(N_prod) or N_prod <= 0:
        raise ValueError(f"no feasible batch: {b.reason}")
    per_start = cycle / max(N_prod, 1e-9)                  # h between batch starts
    seed_units = [max(1, math.ceil(t_seed / per_start)) for _ in seeds]

    # ---------------------------------------------------------------- 5. utilities sizing
    air_acmh = running * b.air_max_kmol_h * 0.08314 * 298
    heat_peak_kW = running * b.heat_max_kW_m3 * W + len(seeds) * 0.0
    heat_avg_kW = n_batches * b.heat_kWh / H
    comp_avg_kW = n_batches * (b.comp_kWh + b.agit_kWh) / H
    cw_L_s = (heat_avg_kW * (1 + c.rt_refrig) + comp_avg_kW) / (4.1868 * v(p, "utilities.cooling_water_dT_C"))
    feed_m3_yr = n_batches * (b.W_end - b.W0 + b.evap_kg / 1000)
    steril_L_h = (n_batches * b.W_end) / H * 1000 * 2       # media + feed through HTST, peaking x2
    steam_kg_batch = 0.015184926543637378 * (vessel.volume_m3 * 1000 + sum(s * 1000 for s in seeds))  # SIP
    steam_kg_batch += b.W0 * 1000 * 4.1868 * 105 / 2410 * 0.1   # media heat-up, 90% HTST heat recovery
    proc_water_m3_batch = (b.feed_water_kg / 1000 + b.W0 + W * (dil - 1) + N_dv * V_ret + wash_m3)
    water_m3_h = n_batches * proc_water_m3_batch / H

    # ---------------------------------------------------------------- 6. capital (2018$)
    isbl, osbl = {}, {}
    basis = v(p, "capital.basis")
    nb = v(p, "capital.nrel_basis")
    ferm_cost = ((lambda V: nb["fermenter_2018usd_300m3"] * (V / 300) ** nb["fermenter_exponent"])
                 if basis == "nrel" else eq.fermenter)
    isbl["production fermenters"] = ferm_cost(vessel.volume_m3) * N_prod
    isbl["seed fermenters"] = sum(ferm_cost(s) * n for s, n in zip(seeds, seed_units))
    n_st, st_size = eq.units(steril_L_h, eq.MAX["sterilizer_L_h"])
    isbl["media sterilizers"] = eq.sterilizer(st_size) * n_st
    media_tank = max(b.W0, 1.0)
    isbl["media + feed tanks"] = eq.tank(min(media_tank, 100)) * math.ceil(media_tank / 100) * 3
    cent_flow_gpm = n_batches * V_cent * 1000 / 3.785 / (H * 60) * v(p, "dsp.centrifuge_stages")
    removal = "none" if spec == "crude" else v(p, f"hosts.{v(p, 'strain.host')}.cell_removal")
    if removal == "none":
        pass
    elif removal == "centrifuge":
        n_c, gpm = eq.units(cent_flow_gpm, eq.MAX["centrifuge_gpm"])
        isbl["centrifuges"] = eq.centrifuge(gpm) * n_c
    else:
        solids_kg_h = n_batches * X * W / H
        n_c, kgh = eq.units(solids_kg_h, eq.MAX["rvf_kg_h"])
        isbl["filters (RVF/press)"] = eq.rvf(kgh) * n_c
    mf_m2 = n_batches * V_clar / (v(p, "dsp.mf_flux_LMH") / 1000 * H)
    uf_m2 = n_batches * permeate / (v(p, "dsp.uf_flux_LMH") / 1000 * H)
    if spec == "crude":
        mf_m2 = uf_m2 = 0.0
    isbl["MF + UF skids"] = eq.membrane_skid(mf_m2 + uf_m2, v(p, "dsp.membrane_skid_usd_m2"))
    isbl["harvest + hold tanks"] = eq.tank(100) * math.ceil(2 * W / 100) * 2
    evap_kg_h = n_batches * water_evap / H
    if evap_kg_h > 0:
        n_d, dsize = eq.units(evap_kg_h, eq.MAX["dryer_kg_h"])
        isbl["spray dryers"] = eq.spray_dryer(dsize) * n_d
    if spec == "isolate":
        isbl["precipitation + basket centrifuges"] = (eq.tank(min(V_ret, 100)) * 2
                                                      + eq.centrifuge(min(150, V_ret * 1000 / 3.785 / 60 / 4)) * 3)
    n_ac, ac = eq.units(air_acmh, eq.MAX["compressor_acmh"])
    osbl["air compressors"] = eq.compressor(ac) * n_ac
    n_ch, chs = eq.units(heat_peak_kW, eq.MAX["chiller_kW"])
    osbl["chillers"] = eq.chiller(chs) * n_ch
    osbl["cooling tower"] = eq.cooling_tower(max(cw_L_s, 1.0))
    steam_kg_h = n_batches * steam_kg_batch / H * 3
    osbl["boiler"] = eq.boiler(max(steam_kg_h, 1000))
    osbl["water treatment"] = eq.water_purification(max(water_m3_h, 1.0))
    m = v(p, "capital.missing_frac") / (1 - v(p, "capital.missing_frac"))
    isbl_pec, osbl_pec = sum(isbl.values()), sum(osbl.values())
    fcl = v(p, "capital.facility_classes")[v(p, "capital.facility_class")]
    if basis == "nrel":
        isbl_tdc = isbl_pec * (1 + m) * nb["other_install"] * (1 + nb["site_frac_isbl"])
        osbl_tdc = osbl_pec * (1 + m) * nb["other_install"]
    else:
        isbl_tdc = isbl_pec * (1 + m) * (1 + fcl["isbl"])
        osbl_tdc = osbl_pec * (1 + m) * (1 + fcl["osbl"])
    # buildings
    bu = v(p, "capital.building_usd_m2_level_2018")
    fp = vessel.area * N_prod + sum(math.pi / 4 * ((4 * s / (math.pi * 2)) ** (1 / 3)) ** 2 * n for s, n in zip(seeds, seed_units))
    ferm_area = fp / v(p, "capital.packing_factor")
    levels = max(1, math.ceil(vessel.height * 1.5 / 6))
    pb = fcl["process_building"]
    areas = {"fermentation": (ferm_area, levels, pb),
             "downstream": (0.0 if spec == "crude" else v(p, "capital.dsp_area_factor") * ferm_area, 2, pb),
             "labs": (v(p, "capital.lab_m2"), 1, "lab"),
             "shop": (0.25 * ferm_area, 1, "shop"),
             "warehouse": (0.25 * ferm_area, 1, "warehouse")}
    # ---------------------------------------------------------------- 7. labour (Humbird model)
    L = "labour"
    att = v(p, f"{L}.attention_production") * cycle * N_prod / cycle      # FTE-equivalents busy
    batch_fte = (v(p, f"{L}.attention_production") * N_prod + v(p, f"{L}.attention_seed") * sum(seed_units)) / v(p, f"{L}.worker_efficiency")
    cont = v(p, f"{L}.continuous_fte_per_shift")
    skip = {"isolate_extra"} | ({"centrifuges", "membranes", "dryer"} if spec == "crude" else set())
    cont_fte = sum(val for k, val in cont.items() if k not in skip) + (cont["isolate_extra"] if spec == "isolate" else 0)
    trains = max(1.0, N_prod / 12)                                          # one continuous crew per ~12 fermenters
    per_shift = batch_fte + cont_fte * trains
    per_shift += per_shift / v(p, f"{L}.employees_per_supervisor")
    fte = per_shift * v(p, f"{L}.shifts_per_position")
    salary = v(p, f"{L}.operator_salary_usd")
    labour_usd = fte * salary * (1 + v(p, f"{L}.burden"))
    areas["office"] = (v(p, "capital.office_m2_per_employee") * per_shift * 1.5, 1, "office")
    areas["compressor building"] = (20.0 * n_ac, 2, "compressor")
    total_area = sum(a for a, _, _ in areas.values())
    buildings = sum(a * lv * bu[cls] for a, lv, cls in areas.values()) + total_area * bu["slab"]
    tdc = isbl_tdc + osbl_tdc + buildings
    if basis == "nrel":
        tpc = tdc * (1 + nb["indirect_frac_tdc"])
        tci = tpc * idx
    else:
        tpc = tdc * (1 + fcl["ec"])
        tci = tpc * (1 + fcl["fc"]) * idx
    capex = {**{f"ISBL: {k}": val * idx for k, val in isbl.items()},
             **{f"OSBL: {k}": val * idx for k, val in osbl.items()},
             "ISBL installation & missing": (isbl_tdc - isbl_pec) * idx,
             "OSBL installation & missing": (osbl_tdc - osbl_pec) * idx,
             "buildings": buildings * idx,
             "engineering & construction": (tpc - tdc) * idx,
             "fees & contingency": tci - tpc * idx}

    # ---------------------------------------------------------------- 8. operating costs ($/yr)
    U = "utilities"
    glc_kg = n_batches * (b.glucose_kg + seed_glc)
    elec_kWh = n_batches * (b.comp_kWh + b.agit_kWh + b.heat_kWh * c.rt_refrig + seed_kWh)
    elec_kWh += n_batches * (1.35 * V_cent * v(p, "dsp.centrifuge_stages")
                             + v(p, "dsp.membrane_kWh_m3_permeate") * (permeate + V_clar)
                             + 0.1 * water_evap)                            # dryer fans
    elec_kWh += total_area * v(p, f"{U}.building_W_m2") / 1000 * H
    gas_GJ = n_batches * water_evap * v(p, "dsp.dryer_MJ_per_kg_water") / 1000
    steam_t = n_batches * steam_kg_batch / 1000
    cw_makeup_m3 = (heat_avg_kW * (1 + c.rt_refrig) * H * 3600 / 2400 / 1000) * 1.3
    water_m3 = n_batches * proc_water_m3_batch + cw_makeup_m3
    ww_m3 = n_batches * (permeate + W * (dil - 1) + V_cent * 0.1 + wash_m3)
    cells_t = n_batches * b.cells_kg / 1000
    annual = {
        "glucose": glc_kg * v(p, f"{U}.glucose_usd_kg"),
        "ammonia": n_batches * b.nh3_kg * v(p, f"{U}.ammonia_usd_kg"),
        "salts & other media": n_batches * (v(p, "media.salts_kg_per_m3") * W * v(p, "media.salts_price_usd_kg")
                                            + v(p, "media.h3po4_kg_per_kg_cells") * b.cells_kg * v(p, "media.h3po4_price_usd_kg")
                                            + v(p, "media.antifoam_kg_per_m3") * W * v(p, "media.antifoam_price_usd_kg")
                                            + v(p, "media.methanol_kg_per_kg_product") * P_in * v(p, "media.methanol_price_usd_kg")),
        "DSP chemicals": n_batches * AS_kg * v(p, "dsp.ammonium_sulfate_usd_kg"),
        "membranes": (mf_m2 + uf_m2) * v(p, "dsp.membrane_price_usd_m2") / v(p, "dsp.membrane_life_y"),
        "electricity": elec_kWh * v(p, f"{U}.electricity_usd_kWh"),
        "natural gas & steam": gas_GJ * v(p, f"{U}.natural_gas_usd_GJ") + steam_t * v(p, f"{U}.steam_usd_t"),
        "water & wastewater": water_m3 * v(p, f"{U}.water_usd_m3") + ww_m3 * v(p, f"{U}.wastewater_usd_m3"),
        "biomass disposal": cells_t * v(p, f"{U}.biomass_disposal_usd_t_dry"),
        "labour": labour_usd,
        "maintenance": (isbl_tdc * idx * nb["maintenance_frac_isbl"] if basis == "nrel"
                        else tci * v(p, "finance.maintenance_frac_tci")),
        "insurance & tax": (tci * nb["insurance_frac_fci"] if basis == "nrel"
                            else tci * v(p, "finance.insurance_tax_frac_tci")),
    }
    variable = sum(val for k, val in annual.items() if k not in ("labour", "maintenance", "insurance & tax"))
    fixed = annual["labour"] + annual["maintenance"] + annual["insurance & tax"]
    ccf = fin.ccf(v(p, "finance.ccf_rate"), v(p, "finance.ccf_life_y"))
    annual["capital charge"] = tci * ccf
    per_kg = {k: val / annual_target_kg for k, val in annual.items()}
    msp_ccf = sum(per_kg.values())
    cop = (variable + fixed + tci / v(p, "finance.ccf_life_y")) / annual_target_kg
    msp_dcf = fin.msp_dcf(tci, variable, fixed, annual_target_kg, irr=v(p, "finance.dcf_irr"),
                          life=v(p, "finance.dcf_life_y"), tax=v(p, "finance.tax_rate"),
                          wc_frac=v(p, "finance.working_capital_frac_fci"))
    powder_frac = target / powder
    physical = {
        "glucose_kg": glc_kg / annual_target_kg,
        "o2_kg": n_batches * (b.o2_kmol + seed_o2_kmol) * 32 / annual_target_kg,
        "electricity_kWh": elec_kWh / annual_target_kg,
        "natural_gas_MJ": gas_GJ * 1000 / annual_target_kg,
        "water_m3": water_m3 / annual_target_kg,
        "cells_kg": cells_t * 1000 / annual_target_kg,
        "overall_yield_g_g": annual_target_kg / glc_kg,
        "fermenter_m3_per_kt": N_prod * vessel.volume_m3 / (annual_target_kg / 1e6),
        "fte_per_kt": fte / (annual_target_kg / 1e6),
    }
    design = dict(N_prod=N_prod, N_prod_int=math.ceil(N_prod - 1e-9), n_batches=n_batches, cycle_h=cycle,
                  t_growth_h=b.t_growth, t_total_h=b.t_total, W0_m3=b.W0, W_end_m3=W, X_end=X, titer=b.titer,
                  q_p_mg_g_h=b.q_p * 1000, recovery=R_total, target_per_batch_kg=target, powder_per_batch_kg=powder,
                  purity_dry=purity, otr_max=omax, our_peak=b.our_max, heat_peak_kW_m3=b.heat_max_kW_m3,
                  seeds_m3=seeds, seed_units=seed_units, mf_m2=mf_m2, uf_m2=uf_m2, CF=CF, evap_kg_h=evap_kg_h,
                  fte=fte, area_m2=total_area, lang_effective=tci / (idx * (isbl_pec + osbl_pec)),
                  y_ps_over_ceiling=v(p, "strain.Y_ps_g_g") / ceiling)
    return Result(ok=not flags, flags=flags, per_kg=per_kg, cop=cop, msp_ccf=msp_ccf, msp_dcf=msp_dcf,
                  per_kg_powder=msp_ccf * powder_frac, tci=tci, capex=capex, annual=annual,
                  physical=physical, design=design, batch=b)
