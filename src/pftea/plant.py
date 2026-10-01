"""A precision-fermentation plant, from strain performance to $/kg of target protein.

Blocks (data in data/pf/base.yaml; equations in each block's comments):
1. Production batch (pf_ferm.run_batch): titer, cells, glucose, O2, power, heat.
2. Downstream, per batch (Intelligen's OVA design, with sourced performance, dsp.yaml):
   a. Cell removal with n wash stages (two-stage disk-stack centrifugation, Intelligen p.7):
      the broth is diluted to C_x g/L cells; each stage separates a paste of volume
      Vp = V_wc / (1 - e), with V_wc = cells / (1000 x 0.3) the wet-cell volume [Humbird A.1
      cell model] and e the extracellular-liquid fraction of the paste (Petrides: 40-60% v/v);
      the paste is re-diluted to the same feed volume V1 and spun again. The fraction of
      product trapped per stage is phi = e Vp / (V1 - V_wc), so recovery = 1 - phi^n,
      clarified liquid = n (V1 - Vp) and wash water = (n - 1)(V1 - Vp).
   b. Microfiltration polish at J_MF, recovery R_MF.
   c. Ultrafiltration: concentrate at J_UF to the diafiltration concentration C_DF, diafilter
      N_DV volumes at J_DF, then concentrate to the end volume at J_DF (flux at high
      concentration). Retention over the whole step = CF^-(1-sigma) exp(-N_DV (1-sigma)).
      Concentrate: the end volume holds the dryer-feed solids s_in (dairy/egg-white practice,
      membranes rather than evaporators): water = solids (1 - s_in)/s_in. Isolate: the UF ends
      at Intelligen's 50 g/L before precipitation.
   c'. 'cex' spec only (lactoferrin): cation-exchange capture between MF and UF. Protein loaded
      L = P R_cell R_MF; resin used per batch (m3 resin-cycles) = L / q (dynamic capacity).
      Per resin-cycle: CV_tot column volumes of buffer (water and wastewater), elution CV_elu at
      1 M NaCl (the eluate goes to UF/DF, which washes the salt out), CIP with NaOH and
      regeneration with 20% ethanol. Loading takes q / c_load column volumes (c_load = protein
      concentration of the MF permeate), so the cycle time is (CV_tot + q / c_load) / flow.
      Resin replaced per year = resin-cycles / life; resin volume installed = resin-cycles per
      hour x cycle time (first fill added to TCI unfactored); column hardware per litre of resin.
      Recovery R_cex.
   d. Isolate only: ammonium-sulfate precipitation and washed basket centrifuges; the dryer is
      fed the cake (solids fraction s_cake).
   d'. 'acid' spec only (casein): isoelectric precipitation of the MF permeate, no UF/DF (the dairy
      acid-casein line; Formo GRN 1312). Acid: H3PO4 = a_acid x V_perm (the permeate's buffer
      capacity, per m3). Heat-and-hold at T_p for t_hold: steam = V_perm rho cp (T_p - T_ferm)
      (1 - h_rec) / dH_vap. Curd recovery R_acid. Countercurrent washes in n_w decanter passes,
      wash water = w x casein (L/kg); the acid whey and the wash water go to wastewater. The curd
      (solids s_curd) is redissolved with NaOH (b x casein solids) to the caseinate dryer feed s_in,
      adding water = solids (1/s_in - 1/s_curd). Decanters are costed on the disk-stack centrifuge
      curve (analogy: no decanter quote on file) for the feed V_perm + n_w x wash; the heater on the
      HTST sterilizer curve; holding and dissolving tanks for their residence times.
   e. Spray dryer: water evaporated = solids (1 - s_in)/s_in; recovery R_dry.
   f. Cleaning in place (all specs): CIP solution per kg product (Intelligen), counted as water,
      wastewater and chemicals (the chemicals only in the design-report convention: Humbird's 4%
      maintenance includes them).
3. Scale: batches/yr = annual target protein / target per batch. Fermenters needed
   N = batches/yr x (batch time + turnaround) / operating hours; capital is costed for
   ceil(N) whole vessels.
4. Seed train: 10:1 volume steps down to lab scale; seed cells grown on the growth
   stoichiometry; units per stage from occupancy.
5. Utilities: compressors and chillers sized on the coincident plant peak: batches start every
   H / n_batches hours, so the plant load at time t is the sum of one batch's air or heat
   profile at t, t + interval, t + 2 interval, ... (its maximum over one interval). Cooling
   tower, boiler (sterilisation steam), water.
6. Capital, two conventions (fermenters from the vendor-quote curve in both unless
   capital.fermenter_quote = acce_aseptic, Humbird's aseptic cell-culture STR quotes):
   - price-anchored (Humbird 2021 facility-class method, 'commodity aerobic'):
       ISBL TDC = PEC_ISBL (1 + m) (1 + f_ISBL);  OSBL TDC = PEC_OSBL (1 + m) (1 + f_OSBL)
       buildings = sum(area x levels x $/m2 by class)
       TDC = ISBL + OSBL + buildings; TPC = TDC (1 + E&C); TCI = TPC (1 + fees & contingency)
     with m = missing-capital allowance (m = 0.1/0.9). All 2018$ x cost index x location factor.
   - design-report ('light', NREL 2011 style): NREL installation factors, site development on
     ISBL, indirect costs on TDC; same buildings except the warehouse (inside NREL's site factor).
7. Operating costs: raw materials, utilities, consumables, waste; labour (Humbird's operator
   attention model with supervisors at 1.4x salary); maintenance and insurance by convention.
8. Money: COP (operating + straight-line depreciation), MSP_CCF (capital charge),
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


def _opt(p, path, default=None):
    """Optional parameter: its value if the leaf exists and is not null, else default."""
    node = p
    for k in path.split("."):
        if not isinstance(node, dict) or k not in node:
            return default
        node = node[k]
    try:
        val = v(p, path)
    except (KeyError, TypeError):
        return default
    return default if val is None else val


def _host(p) -> pf.Host:
    h = f"hosts.{v(p, 'strain.host')}"
    f = v(p, f"{h}.biomass_formula")
    return pf.Host(bio=th.biomass(f["C"], f["H"], f["O"], f["N"]), mu_max=v(p, f"{h}.mu_max_per_h"),
                   T_C=v(p, f"{h}.temperature_C"), maint_factor=v(p, f"{h}.maint_factor"),
                   m_s_prod=_opt(p, f"{h}.m_s_prod_g_g_h"))


def _vessel(p, volume=None) -> pf.STR:
    h = f"hosts.{v(p, 'strain.host')}"
    return pf.STR(volume_m3=volume or v(p, "fermenter.volume_m3"), h_to_d=v(p, "fermenter.h_to_d"),
                  fill_max=v(p, "fermenter.fill_max"), kla_factor=v(p, f"{h}.kla_factor"),
                  pv_max=v(p, "fermenter.pv_max_W_m3"), us_max=v(p, "fermenter.us_max_m_s"),
                  otr_cap=v(p, "fermenter.otr_cap_mol_m3_h"),
                  otr_cap_basis=_opt(p, "fermenter.otr_cap_basis", "broth"),
                  heat_max_kW_m3=v(p, "fermenter.heat_removal_max_kW_m3"),
                  heat_per_o2_kJ=v(p, "fermenter.heat_per_o2_kJ"),
                  min_fill=_opt(p, "fermenter.min_initial_fill"),
                  kla_k=v(p, "fermenter.kla_temperature_factor"),
                  compressor_formula=_opt(p, "fermenter.compressor_formula", "adiabatic"),
                  compressor_eff=v(p, "fermenter.compressor_efficiency"))


def _conditions(p) -> pf.Conditions:
    return pf.Conditions(T_C=_host(p).T_C, rt_refrig=v(p, "utilities.rt_refrig"),
                         DO_top_frac=v(p, "fermenter.DO_top_frac"))


def batch(p, keep_series=False) -> pf.Batch:
    host = _host(p)
    c = _conditions(p)
    strain = pf.Strain(product=pr.protein(v(p, "plant.product")), Y_ps=v(p, "strain.Y_ps_g_g"),
                       X_prod=v(p, "strain.X_prod_g_L"), mu_prod=v(p, "strain.mu_prod_per_h"),
                       t_prod=v(p, "strain.t_prod_h"), X_max=v(p, "strain.X_max_g_L"))
    return pf.run_batch(_vessel(p), c, host, strain, X0=v(p, "strain.X0_g_L"),
                        titer=v(p, "strain.titer_g_L"), c_s=v(p, "fermenter.feed_glucose_g_L"),
                        c_nh3=v(p, "fermenter.nh3_feed_g_L"), keep_series=keep_series)


def atp_per_residue(p) -> float:
    """ATP charged per residue by the energetic ceiling: the peptide bond, the net cost of making
    the amino acid from glucose and NH4+ (Stouthamer), and sulfate assimilation for the protein's
    sulfur (activation ATP plus its 8 electrons at the host's P/O ratio)."""
    h = f"hosts.{v(p, 'strain.host')}"
    po = v(p, f"{h}.po_ratio")
    prot = pr.protein(v(p, "plant.product"))
    s_per_res = prot.formula.get("S", 0.0) / prot.residues
    e = "energetics"
    return (v(p, f"{e}.atp_per_peptide_bond") + v(p, f"{e}.atp_aa_synthesis_per_residue")
            + s_per_res * (v(p, f"{e}.sulfur_atp_per_S") + v(p, f"{e}.sulfur_electrons_per_S") / 2 * po))


def energetic_ceiling(p) -> float:
    """Upper bound on the product-reaction yield [g/g]: the ATP of atp_per_residue paid by
    respiring glucose at the host's P/O ratio (product.energetic_ceiling). Transport, secretion,
    folding and turnover costs are not counted, so this stays an upper bound."""
    h = f"hosts.{v(p, 'strain.host')}"
    atp_glc = v(p, "energetics.substrate_atp_per_glucose") + 12 * v(p, f"{h}.po_ratio")
    return pr.energetic_ceiling(pr.protein(v(p, "plant.product")), th.get("Glucose (s)"),
                                atp_per_residue(p), atp_glc)


def _coincident_peak(prof_t, prof_v, t_total: float, interval: float) -> float:
    """Peak of the summed load of identical batches started every `interval` hours; each batch
    follows the step profile (step start times prof_t, values prof_v) until t_total."""
    t, val = np.asarray(prof_t, float), np.asarray(prof_v, float)
    if t.size == 0:
        return 0.0
    if not (np.isfinite(interval) and interval > 0):
        return float(val.max())
    n_on = int(np.ceil(t_total / interval)) + 1
    grid = np.arange(0.0, interval, min(interval / 64, 0.05))
    taus = grid[:, None] + interval * np.arange(n_on)[None, :]
    i = np.searchsorted(t, taus, side="right") - 1
    load = np.where((i >= 0) & (taus < t_total), val[np.clip(i, 0, None)], 0.0)
    return float(load.sum(axis=1).max())


def evaluate(p, keep_series=False) -> Result:
    flags = []
    idx = v(p, "capital.cost_index_2018_to_2025") * v(p, "capital.location_factor")
    b = batch(p, keep_series)
    if not b.ok:
        flags.append(b.reason)
    vessel = _vessel(p)
    c = _conditions(p)
    omax = pf.otr_max(vessel, c, v(p, "strain.X_prod_g_L"))
    heat_cap = v(p, "fermenter.heat_removal_max_kW_m3")
    if heat_cap and b.heat_max_kW_m3 > heat_cap * 1.02:
        flags.append(f"heat {b.heat_max_kW_m3:.1f} > {heat_cap} kW/m3 removable")
    key = v(p, "plant.product")
    sol = pr.load(key).get("solubility_practical_g_L", {}) or {}
    if isinstance(p.get("plant", {}).get("solubility_override_g_L"), dict):   # sensitivity runs only
        sol = {"value": p["plant"]["solubility_override_g_L"]["value"]}
    if sol.get("value") and v(p, "strain.titer_g_L") > sol["value"] * 1.0001:
        flags.append(f"titer above practical solubility ({sol['value']} g/L)")
    ceiling = energetic_ceiling(p)
    if v(p, "strain.Y_ps_g_g") > ceiling:
        flags.append(f"Y_ps above the energetic ceiling {ceiling:.2f} g/g")
    qmax = _opt(p, "strain.q_p_max_mg_g_h")
    if qmax and np.isfinite(b.q_p) and b.q_p * 1000 > qmax * 1.001:
        flags.append(f"specific productivity {b.q_p * 1000:.1f} > {qmax:g} mg/g/h")

    # ---------------------------------------------------------------- 2. downstream per batch
    spec = v(p, "plant.spec")
    W = b.W_end                                            # m3 broth
    X = b.X_end                                            # kg/m3 cells
    P_in = b.product_kg
    if not (np.isfinite(P_in) and P_in > 0):
        raise ValueError("batch makes no product")
    crude = spec == "crude"
    n_st = int(v(p, "dsp.centrifuge_stages"))
    resin_cyc = buffer_m3 = nacl_kg = naoh_kg = etoh_kg = 0.0     # cation exchange ('cex' spec only)
    load_cv = cex_cycle_h = 0.0
    if crude:                                              # whole broth used as is (NREL on-site enzyme)
        dil, V1, V_clar, V_wash, R_cell = 1.0, W, W, 0.0, 1.0
        R_mf = R_uf = 1.0
        V_ret, CF, N_dv, perm_c, perm_df, df_water = W, 1.0, 0.0, 0.0, 0.0, 0.0
        target, purity, V_uf = P_in, 1.0, W
    else:
        # a. cell removal with n wash stages
        dil = max(X / v(p, "dsp.dilution_to_g_L_cells"), 1.0)
        V1 = W * dil                                       # m3 per stage feed
        V_wc = b.cells_kg / (1000 * pf.CELL_DRY_FRAC)      # m3 wet cells
        e = v(p, "dsp.paste_extracellular_frac")
        Vp = V_wc / (1 - e)                                # m3 paste per stage
        phi = min(e * Vp / max(V1 - V_wc, 1e-9), 1.0)      # product fraction trapped per stage
        R_cell = _opt(p, "dsp.recovery_cell_removal_override") or 1 - phi ** n_st
        V_clar = n_st * (V1 - Vp)
        V_wash = (n_st - 1) * (V1 - Vp)
        # b. microfiltration polish
        R_mf = v(p, "dsp.mf_recovery")
        # c'. cation-exchange capture ('cex' spec)
        P_uf, V_uf = P_in * R_cell * R_mf, V_clar          # kg and m3 into UF
        if spec == "cex":
            load_cv = v(p, "dsp.cex_dbc_g_L") / (P_uf / V_clar)   # column volumes of MF permeate per load
            cex_cycle_h = (v(p, "dsp.cex_cv_per_cycle") + load_cv) / v(p, "dsp.cex_flow_cv_per_h")
            resin_cyc = P_uf / v(p, "dsp.cex_dbc_g_L")      # m3 resin-cycles per batch
            V_uf = v(p, "dsp.cex_elution_cv") * resin_cyc   # eluate
            buffer_m3 = v(p, "dsp.cex_cv_per_cycle") * resin_cyc
            nacl_kg = resin_cyc * (v(p, "dsp.cex_elution_cv") * v(p, "dsp.cex_elution_nacl_kg_m3")
                                   + v(p, "dsp.cex_regen_cv") * v(p, "dsp.cex_regen_nacl_kg_m3"))
            naoh_kg = resin_cyc * v(p, "dsp.cex_cip_cv") * v(p, "dsp.cex_cip_naoh_kg_m3")
            etoh_kg = resin_cyc * v(p, "dsp.cex_regen_cv") * v(p, "dsp.cex_regen_etoh_kg_m3")
            P_uf *= v(p, "dsp.cex_recovery")
        # c. ultrafiltration + diafiltration (not on the 'acid' route: the permeate is precipitated)
        sigma = v(p, "dsp.uf_rejection")
        C_in = P_uf / V_uf                                 # kg/m3 into UF
        purity = v(p, {"isolate": "dsp.isolate_target_frac_dry", "cex": "dsp.cex_target_frac_dry",
                       "acid": "dsp.acid_target_frac_dry"}.get(spec, "dsp.concentrate_target_frac_dry"))
        if spec == "acid":
            V_ret = V_uf
        elif spec == "isolate":
            V_ret = P_uf / v(p, "dsp.isolate_uf_end_g_L")
        else:                                              # end volume holds the dryer-feed solids
            s_in = v(p, f"dsp.dryer_feed_solids_{key}")
            V_ret = P_uf / purity * (1 - s_in) / s_in / 1000
        if sol.get("value"):
            V_ret = max(V_ret, P_uf / sol["value"])        # cannot concentrate above solubility
        V_ret = min(V_ret, V_uf)
        CF = V_uf / V_ret
        if spec == "acid":                                 # no membrane concentration
            N_dv = perm_c = df_water = perm_df = 0.0
            R_uf = 1.0
        else:
            C_df = min(v(p, "dsp.diafiltration_conc_g_L"), P_uf / V_ret)
            V_df = max(min(P_uf / C_df, V_uf), V_ret)      # volume while diafiltering
            N_dv = v(p, "dsp.cex_diafiltration_volumes" if spec == "cex" else "dsp.diafiltration_volumes")
            perm_c = V_uf - V_df                           # concentration to C_df, at J_UF
            df_water = N_dv * V_df
            perm_df = df_water + (V_df - V_ret)            # diafiltration + final concentration, at J_DF
            R_uf = CF ** -(1 - sigma) * math.exp(-N_dv * (1 - sigma))
        target = P_uf * R_uf
    permeate = perm_c + perm_df
    if spec == "isolate":
        R_pre = v(p, "dsp.precip_recovery")
        target *= R_pre
        AS_kg = v(p, "dsp.ammonium_sulfate_kg_per_m3") * V_ret * (1 - v(p, "dsp.ammonium_sulfate_recycled_frac"))
        wash_m3 = v(p, "dsp.isolate_wash_volumes") * V_ret
    else:
        AS_kg, wash_m3 = 0.0, 0.0
    acid_kg = acid_steam_kg = whey_m3 = dissolve_m3 = 0.0   # isoelectric precipitation ('acid' spec only)
    if spec == "acid":
        target *= v(p, "dsp.acid_precip_recovery")
        acid_kg = v(p, "dsp.acid_h3po4_kg_per_m3") * V_ret
        dT = v(p, "dsp.acid_precip_temperature_C") - v(p, f"hosts.{v(p, 'strain.host')}.temperature_C")
        acid_steam_kg = V_ret * 1000 * 4.1868 * dT / 2410 * (1 - v(p, "dsp.acid_heat_recovery"))
        whey_m3 = V_ret                                    # acid whey (the precipitated permeate)
        wash_m3 = v(p, "dsp.acid_wash_L_per_kg") * target / purity / 1000
        naoh_kg += v(p, "dsp.acid_naoh_kg_per_kg") * target / purity
        dissolve_m3 = target / purity / 1000 * (1 / v(p, f"dsp.dryer_feed_solids_{key}") - 1 / v(p, "dsp.acid_curd_solids"))
    if crude:
        purity, water_evap = target / (target + b.cells_kg), 0.0
        powder = target
    else:
        solids = target / purity                           # kg dry solids to the dryer
        if spec == "isolate":
            dryer_in_solids = v(p, "dsp.isolate_cake_solids")     # washed precipitate cake
        elif spec == "acid":
            dryer_in_solids = v(p, f"dsp.dryer_feed_solids_{key}")    # redissolved caseinate
        else:
            dryer_in_solids = solids / (V_ret * 1000 + solids)    # UF/NF end volume
        water_evap = solids / dryer_in_solids * (1 - dryer_in_solids)
        target *= v(p, "dsp.dryer_recovery")
        powder = target / purity / (1 - v(p, "dsp.powder_moisture"))
    R_total = target / P_in
    cip_kg = v(p, "dsp.cip_solution_kg_per_kg") * target  # kg CIP solution per batch

    # ---------------------------------------------------------------- 3. scale
    H = v(p, "plant.operating_days") * 24
    annual_target_kg = v(p, "plant.annual_target_protein_t") * 1000
    n_batches = annual_target_kg / target
    cycle = b.t_total + v(p, "fermenter.turnaround_h")
    N_prod = n_batches * cycle / H
    if not np.isfinite(N_prod) or N_prod <= 0:
        raise ValueError(f"no feasible batch: {b.reason}")
    N_int = math.ceil(N_prod - 1e-9)                       # whole vessels are bought
    running = n_batches * b.t_total / H                    # fermenters online on average

    # ---------------------------------------------------------------- 4. seed train
    host = _host(p)
    g = host.growth
    glc = th.get("Glucose (s)")
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
    per_start = cycle / N_prod                             # h between batch starts
    seed_units = [max(1, math.ceil(t_seed / per_start)) for _ in seeds]

    # ---------------------------------------------------------------- 5. utilities sizing
    interval = H / n_batches                                # h between batch starts
    air_acmh = _coincident_peak(b.profile["t"], b.profile["air"], b.t_total, interval) * 0.08314 * 298
    heat_peak_kW = _coincident_peak(b.profile["t"], b.profile["heat"], b.t_total, interval)
    heat_avg_kW = n_batches * b.heat_kWh / H
    comp_avg_kW = n_batches * (b.comp_kWh + b.agit_kWh) / H
    cw_L_s = (heat_avg_kW * (1 + c.rt_refrig) + comp_avg_kW) / (4.1868 * v(p, "utilities.cooling_water_dT_C"))
    steril_L_h = (n_batches * b.W_end) / H * 1000 * v(p, "utilities.sterilizer_peak_factor")
    steam_kg_batch = 0.015184926543637378 * (vessel.volume_m3 * 1000 + sum(s * 1000 for s in seeds))  # SIP [A.1]
    steam_kg_batch += b.W0 * 1000 * 4.1868 * 105 / 2410 * 0.1   # media heat-up, 90% HTST heat recovery
    steam_kg_batch += acid_steam_kg                         # casein precipitation heater ('acid' spec)
    cip_m3 = cip_kg / 1000
    dilution_m3 = W * (dil - 1)
    proc_water_m3_batch = (b.feed_water_kg / 1000 + b.W0 + dilution_m3 + V_wash + df_water + wash_m3 + cip_m3
                           + buffer_m3 + dissolve_m3)
    water_m3_h = n_batches * proc_water_m3_batch / H

    # ---------------------------------------------------------------- 6. capital (2018$)
    isbl, osbl = {}, {}
    basis = v(p, "capital.basis")
    nb = v(p, "capital.nrel_basis")
    vf = v(p, "capital.vendor_fermenter")
    exp_above = v(p, "capital.fermenter_exponent_above_table")
    quote = _opt(p, "capital.fermenter_quote", "vendor")
    ferm_cost = ((lambda V: vf["cost_2018usd_300m3"] * (V / 300) ** vf["exponent"])
                 if basis == "nrel" or quote == "vendor" else (lambda V: eq.fermenter(V, exp_above)))
    isbl["production fermenters"] = ferm_cost(vessel.volume_m3) * N_int
    seed_quote = _opt(p, "capital.seed_fermenter_quote")       # sensitivity: seeds on another curve
    seed_cost = ((lambda V: eq.fermenter(V, exp_above)) if seed_quote == "acce_aseptic" else ferm_cost)
    isbl["seed fermenters"] = sum(seed_cost(s) * n for s, n in zip(seeds, seed_units))
    n_ster, st_size = eq.units(steril_L_h, eq.MAX["sterilizer_L_h"])
    isbl["media sterilizers"] = eq.sterilizer(st_size) * n_ster
    media_tank = max(b.W0, 1.0)
    isbl["media + feed tanks"] = eq.tank(min(media_tank, 100)) * math.ceil(media_tank / 100) * 3
    removal = "none" if crude else v(p, f"hosts.{v(p, 'strain.host')}.cell_removal")
    if removal == "centrifuge":
        cent_flow_gpm = n_batches * V1 * n_st * 1000 / 3.785 / (H * 60)
        n_c, gpm = eq.units(cent_flow_gpm, eq.MAX["centrifuge_gpm"])
        isbl["centrifuges"] = eq.centrifuge(gpm) * n_c
    elif removal != "none":
        solids_kg_h = n_batches * b.cells_kg / H
        n_c, kgh = eq.units(solids_kg_h, eq.MAX["rvf_kg_h"])
        isbl["filters (RVF/press)"] = eq.rvf(kgh) * n_c
    if crude:
        mf_m2 = uf_m2 = 0.0
    else:
        mf_m2 = n_batches * V_clar / (v(p, "dsp.mf_flux_LMH") / 1000 * H)
        uf_m2 = n_batches * (perm_c / v(p, "dsp.uf_flux_LMH") + perm_df / v(p, "dsp.df_flux_LMH")) * 1000 / H
    # the skid price is an installed cost (Mercier-Bouchard's 'installation capital investment'):
    # back it out to a purchased cost with the convention's installation factor (review BE-8)
    skid_inst = v(p, "capital.nrel_basis")["other_install"] if basis == "nrel" else \
        1 + v(p, "capital.facility_classes")[v(p, "capital.facility_class")]["isbl"]
    isbl["MF + UF skids"] = eq.membrane_skid(mf_m2 + uf_m2, v(p, "dsp.membrane_skid_usd_m2") / skid_inst)
    isbl["harvest + hold tanks"] = eq.tank(100) * math.ceil(2 * W / 100) * 2
    evap_kg_h = n_batches * water_evap / H
    if evap_kg_h > 0:
        n_d, dsize = eq.units(evap_kg_h, v(p, "dsp.spray_dryer_max_kg_h"))
        isbl["spray dryers"] = eq.spray_dryer(dsize, v(p, "dsp.spray_dryer_cost_2018usd"), v(p, "dsp.spray_dryer_ref_kg_h"),
                                              v(p, "dsp.spray_dryer_exponent")) * n_d
    resin_m3 = n_batches * resin_cyc / H * cex_cycle_h if spec == "cex" else 0.0   # installed resin
    if spec == "cex":
        isbl["CEX columns and skids"] = resin_m3 * 1000 * v(p, "dsp.cex_hardware_usd_per_L_resin")
    if spec == "isolate":
        isbl["precipitation + basket centrifuges"] = (eq.tank(min(V_ret, 100)) * 2
                                                      + eq.centrifuge(min(150, V_ret * 1000 / 3.785 / 60 / 4)) * 3)
    if spec == "acid":                                     # heater, holding tank, decanters, caseinate tank
        perm_m3_h = n_batches * V_ret / H
        n_h, h_size = eq.units(perm_m3_h * 1000, eq.MAX["sterilizer_L_h"])
        dec_gpm = n_batches * (V_ret + v(p, "dsp.acid_wash_stages") * wash_m3) * 1000 / 3.785 / (H * 60)
        n_dc, dc = eq.units(dec_gpm, eq.MAX["centrifuge_gpm"])
        tanks = lambda V: eq.tank(min(V, 100)) * math.ceil(V / 100)   # noqa: E731
        sol_m3_h = n_batches * target / purity / v(p, f"dsp.dryer_feed_solids_{key}") / 1000 / H
        isbl["precipitation heater + decanters"] = (eq.sterilizer(h_size) * n_h + eq.centrifuge(dc) * n_dc
                                                    + tanks(max(perm_m3_h * v(p, "dsp.acid_hold_h"), 1.0))
                                                    + tanks(max(sol_m3_h * v(p, "dsp.acid_dissolve_h"), 1.0)))
    n_ac, ac = eq.units(air_acmh, eq.MAX["compressor_acmh"])
    osbl["air compressors"] = eq.compressor(ac) * n_ac
    n_ch, chs = eq.units(heat_peak_kW, eq.MAX["chiller_kW"])
    osbl["chillers"] = eq.chiller(chs) * n_ch
    osbl["cooling tower"] = eq.cooling_tower(max(cw_L_s, 1.0))
    steam_kg_h = n_batches * steam_kg_batch / H * v(p, "utilities.boiler_peak_factor")
    osbl["boiler"] = eq.boiler(max(steam_kg_h, 1000))
    osbl["water treatment"] = eq.water_purification(max(water_m3_h, 1.0))
    m = v(p, "capital.missing_frac") / (1 - v(p, "capital.missing_frac"))
    isbl_pec, osbl_pec = sum(isbl.values()), sum(osbl.values())
    ferm_pec = isbl["production fermenters"] + isbl["seed fermenters"]
    fcl = v(p, "capital.facility_classes")[v(p, "capital.facility_class")]
    if basis == "nrel":
        isbl_inst = (ferm_pec * nb["fermenter_install"] + (isbl_pec - ferm_pec) * nb["other_install"]) * (1 + m)
        isbl_tdc = isbl_inst * (1 + nb["site_frac_isbl"])
        osbl_tdc = osbl_pec * (1 + m) * nb["other_install"]
    else:
        isbl_tdc = isbl_pec * (1 + m) * (1 + fcl["isbl"])
        osbl_tdc = osbl_pec * (1 + m) * (1 + fcl["osbl"])
    # buildings
    bu = v(p, "capital.building_usd_m2_level_2018")
    fp = vessel.area * N_int + sum(math.pi / 4 * ((4 * s / (math.pi * 2)) ** (1 / 3)) ** 2 * n for s, n in zip(seeds, seed_units))
    ferm_area = fp / v(p, "capital.packing_factor")
    levels = max(1, math.ceil(vessel.height * 1.5 / 6))
    pb = fcl["process_building"]
    areas = {"fermentation": (ferm_area, levels, pb),
             "downstream": (0.0 if crude else v(p, "capital.dsp_area_factor") * ferm_area, 2, pb),
             "labs": (v(p, "capital.lab_m2"), 1, "lab"),
             "shop": (v(p, "capital.shop_area_frac") * ferm_area, 1, "shop")}
    if basis != "nrel":                                    # NREL's site factor includes a warehouse
        areas["warehouse"] = (v(p, "capital.warehouse_area_frac") * ferm_area, 1, "warehouse")

    # ---------------------------------------------------------------- 7. labour (Humbird model)
    L = "labour"
    batch_fte = (v(p, f"{L}.attention_production") * N_prod + v(p, f"{L}.attention_seed") * sum(seed_units)) / v(p, f"{L}.worker_efficiency")
    cont = v(p, f"{L}.continuous_fte_per_shift")
    skip = {"isolate_extra", "chromatography"} | ({"centrifuges", "membranes", "dryer"} if crude else set())
    cont_fte = (sum(val for k, val in cont.items() if k not in skip) + (cont["isolate_extra"] if spec in ("isolate", "acid") else 0)
                + (cont.get("chromatography", 0.0) if spec == "cex" else 0))
    trains = max(1.0, N_prod / v(p, f"{L}.fermenters_per_continuous_crew"))
    operators = batch_fte + cont_fte * trains
    supervisors = operators / v(p, f"{L}.employees_per_supervisor")
    per_shift = operators + supervisors
    fte = per_shift * v(p, f"{L}.shifts_per_position")
    salary = v(p, f"{L}.operator_salary_usd")
    labour_usd = (operators + supervisors * v(p, f"{L}.supervisor_factor")) * v(p, f"{L}.shifts_per_position") \
        * salary * (1 + v(p, f"{L}.burden"))
    areas["office"] = (v(p, "capital.office_m2_per_employee") * per_shift, 1, "office")
    areas["compressor building"] = (v(p, "capital.compressor_building_m2_each") * n_ac, 2, "compressor")
    total_area = sum(a for a, _, _ in areas.values())
    buildings = sum(a * lv * bu[cls] for a, lv, cls in areas.values()) + total_area * bu["slab"]
    tdc = isbl_tdc + osbl_tdc + buildings
    if basis == "nrel":
        tpc = tdc * (1 + nb["indirect_frac_tdc"])
        tci = tpc * idx
    else:
        tpc = tdc * (1 + fcl["ec"])
        tci = tpc * (1 + fcl["fc"]) * idx
    resin_fill = resin_m3 * 1000 * v(p, "dsp.cex_resin_usd_L")    # traded consumable: unfactored, not location-scaled
    tci += resin_fill
    capex = {**{f"ISBL: {k}": val * idx for k, val in isbl.items()},
             **{f"OSBL: {k}": val * idx for k, val in osbl.items()},
             "ISBL installation & missing": (isbl_tdc - isbl_pec) * idx,
             "OSBL installation & missing": (osbl_tdc - osbl_pec) * idx,
             "buildings": buildings * idx,
             "engineering & construction": (tpc - tdc) * idx,
             "fees & contingency": tci - resin_fill - tpc * idx,
             "CEX resin first fill": resin_fill}

    # ---------------------------------------------------------------- 8. operating costs ($/yr)
    U = "utilities"
    glc_kg = n_batches * (b.glucose_kg + seed_glc)
    elec_kWh = n_batches * (b.comp_kWh + b.agit_kWh + b.heat_kWh * c.rt_refrig + seed_kWh)
    if not crude:
        elec_kWh += n_batches * (v(p, "dsp.centrifuge_kWh_m3") * (V1 * n_st + (V_ret + v(p, "dsp.acid_wash_stages") * wash_m3
                                                                  if spec == "acid" else 0.0))
                                 + v(p, "dsp.membrane_kWh_m3_permeate") * (permeate + V_clar)
                                 + v(p, "dsp.dryer_fan_kWh_kg_water") * water_evap)
    elec_kWh += total_area * v(p, f"{U}.building_W_m2") / 1000 * H
    gas_GJ = n_batches * water_evap * v(p, "dsp.dryer_MJ_per_kg_water") / 1000
    steam_t = n_batches * steam_kg_batch / 1000
    steam_price = _opt(p, f"{U}.steam_usd_t") or v(p, f"{U}.natural_gas_usd_GJ") * v(p, f"{U}.steam_gas_GJ_per_t")
    cw_makeup_m3 = (heat_avg_kW * (1 + c.rt_refrig) * H * 3600 / 2400 / 1000) * 1.3
    water_m3 = n_batches * proc_water_m3_batch + cw_makeup_m3
    ww_m3 = n_batches * (permeate + wash_m3 + cip_m3 + buffer_m3 + whey_m3 - (V_uf if spec == "cex" else 0.0))
    # membrane permeates, cake wash, CIP and the column buffers other than the eluate (which goes to UF)
    cells_t = 0.0 if crude else n_batches * b.cells_kg / 1000   # crude broth keeps its cells (used on site)
    nb_maint = (isbl_tdc * idx * nb["maintenance_frac_isbl"] + tci * nb.get("maintenance_frac_fci", 0.0))
    rule = _opt(p, "finance.fixed_cost_rule") or ("nrel" if basis == "nrel" else "humbird")   # maintenance + insurance
    cip_chem = 0.0 if (rule == "humbird" and _opt(p, "finance.maintenance_includes_cip_chemicals", False)) else 1.0
    annual = {
        "glucose": glc_kg * v(p, f"{U}.glucose_usd_kg"),
        "ammonia": n_batches * b.nh3_kg * v(p, f"{U}.ammonia_usd_kg"),
        "salts & other media": n_batches * (v(p, "media.salts_kg_per_m3") * W * v(p, "media.salts_price_usd_kg")
                                            + v(p, "media.h3po4_kg_per_kg_cells") * b.cells_kg * v(p, "media.h3po4_price_usd_kg")
                                            + v(p, "media.antifoam_kg_per_m3") * W * v(p, "media.antifoam_price_usd_kg")
                                            + v(p, "media.methanol_kg_per_kg_product") * P_in * v(p, "media.methanol_price_usd_kg")),
        "DSP chemicals": n_batches * (AS_kg * v(p, "dsp.ammonium_sulfate_usd_kg") + cip_chem * cip_kg * v(p, "dsp.cip_price_usd_kg")
                                      + nacl_kg * v(p, "dsp.nacl_usd_kg") + naoh_kg * v(p, "dsp.naoh_usd_kg")
                                      + etoh_kg * v(p, "dsp.ethanol_usd_kg") + acid_kg * v(p, "media.h3po4_price_usd_kg")),
        "chromatography resin": (n_batches * resin_cyc / v(p, "dsp.cex_resin_life_cycles") * 1000
                                 * v(p, "dsp.cex_resin_usd_L")) if spec == "cex" else 0.0,
        "membranes": (mf_m2 + uf_m2) * v(p, "dsp.membrane_price_usd_m2") / v(p, "dsp.membrane_life_y"),
        "electricity": elec_kWh * v(p, f"{U}.electricity_usd_kWh"),
        "natural gas & steam": gas_GJ * v(p, f"{U}.natural_gas_usd_GJ") + steam_t * steam_price,
        "water & wastewater": water_m3 * v(p, f"{U}.water_usd_m3") + ww_m3 * v(p, f"{U}.wastewater_usd_m3"),
        "biomass disposal": cells_t * v(p, f"{U}.biomass_disposal_usd_t_dry"),
        "labour": labour_usd,
        "maintenance": (nb_maint if rule == "nrel" else tci * v(p, "finance.maintenance_frac_tci")),
        "insurance": (tci * nb["insurance_frac_fci"] if rule == "nrel"
                      else tci * v(p, "finance.insurance_tax_frac_tci")),
    }
    variable = sum(val for k, val in annual.items() if k not in ("labour", "maintenance", "insurance"))
    # (maintenance and insurance are charged on TCI including the resin first fill)
    fixed = annual["labour"] + annual["maintenance"] + annual["insurance"]
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
        "fermenter_m3_per_kt": N_int * vessel.volume_m3 / (annual_target_kg / 1e6),
        "fte_per_kt": fte / (annual_target_kg / 1e6),
    }
    design = dict(N_prod=N_prod, N_prod_int=N_int, n_batches=n_batches, cycle_h=cycle,
                  t_growth_h=b.t_growth, t_total_h=b.t_total, W0_m3=b.W0, W_end_m3=W, X_end=X, titer=b.titer,
                  q_p_mg_g_h=b.q_p * 1000, recovery=R_total, recovery_cell_removal=R_cell,
                  target_per_batch_kg=target, product_made_kg=P_in, o2_kmol_batch=b.o2_kmol,
                  powder_per_batch_kg=powder, purity_dry=purity, otr_max=omax, our_peak=b.our_max,
                  heat_peak_kW_m3=b.heat_max_kW_m3, seeds_m3=seeds, seed_units=seed_units, mf_m2=mf_m2,
                  uf_m2=uf_m2, CF=CF, evap_kg_h=evap_kg_h, resin_m3=resin_m3, cex_cycle_h=cex_cycle_h, cex_load_cv=load_cv,
                  acid_kg_batch=acid_kg, acid_steam_kg_batch=acid_steam_kg, whey_m3_batch=whey_m3,
                  wash_m3_batch=wash_m3, dissolve_m3_batch=dissolve_m3, naoh_kg_batch=naoh_kg,
                  heat_plant_peak_kW=heat_peak_kW, heat_sum_of_peaks_kW=running * b.heat_max_kW,
                  dryer_inlet_solids=(0.0 if crude else dryer_in_solids),
                  fte=fte, area_m2=total_area, lang_effective=tci / (idx * (isbl_pec + osbl_pec)),
                  y_ps_over_ceiling=v(p, "strain.Y_ps_g_g") / ceiling, energetic_ceiling=ceiling,
                  effective_yield_production=(b.product_kg / b.glucose_prod_kg if b.glucose_prod_kg > 0 else float("nan")),
                  building_to_pec=buildings / (isbl_pec + osbl_pec))
    return Result(ok=not flags, flags=flags, per_kg=per_kg, cop=cop, msp_ccf=msp_ccf, msp_dcf=msp_dcf,
                  per_kg_powder=msp_ccf * powder_frac, tci=tci, capex=capex, annual=annual,
                  physical=physical, design=design, batch=b)
