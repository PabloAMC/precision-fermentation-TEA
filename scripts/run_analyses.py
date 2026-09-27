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
import yaml

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
    res["base_aseptic"] = {prod: ev({"plant.product": prod, **sc.ASEPTIC}) for prod in ("blg", "ova")}
    # the gap between the conventions, step by step (review SC-3/BE-3): fixed-cost rates, then factors
    steps = [("price-anchored (base)", {}),
             ("+ NREL fixed-cost rates (maintenance 3% of installed ISBL, insurance 0.7%)", {"finance.fixed_cost_rule": "nrel"}),
             ("+ NREL factors = design-report convention", sc.LIGHT)]
    dec = [dict(step=label, msp=plant.evaluate(params.override(BASE, {"plant.product": "blg", **ch})).msp_ccf)
           for label, ch in steps]
    res["convention_steps"] = dec
    res["base_eu"] = {prod: ev({"plant.product": prod, "plant.location": "eu_nw"}) for prod in ("blg", "ova")}
    res["base_isolate"] = {prod: ev({"plant.product": prod, "plant.spec": "isolate"}) for prod in ("blg", "ova")}
    res["benchmarks"] = {"incumbents": bm.incumbents(), "titer_markers": bm.titer_markers(), "context": bm.context_prices()}
    # one-change sensitivities of the base BLG quoted in the text and the review log
    vf = params.v(BASE, "capital.vendor_fermenter")
    esc = next(e for e in yaml.safe_load((ROOT / "data/evidence/prices.yaml").read_text())
               if e["key"] == "escalation_factors_summary")["values"]
    tank = esc["PPI_PCU332420332420_2018_2025"] / params.v(BASE, "capital.cost_index_2018_to_2025")  # BLS heavy-gauge tanks
    sens = {"fermenters escalated with the heavy-gauge tank PPI": {"capital.vendor_fermenter": {"value": {
                "cost_2018usd_300m3": vf["cost_2018usd_300m3"] * tank, "exponent": vf["exponent"]}}},
            "aseptic cell-culture vessels (ACCE)": sc.ASEPTIC,
            "missing-equipment allowance 10% (v2)": {"capital.missing_frac": 0.10},
            "O2 cap 150 per m3 of broth (v2 basis)": {"fermenter.otr_cap_basis": "broth", "fermenter.otr_cap_mol_m3_h": 150.0},
            "glucose feed 600 g/L": {"fermenter.feed_glucose_g_L": 600.0},
            "NREL fixed-cost rule": {"finance.fixed_cost_rule": "nrel"},
            "capital charge 10%/20 yr (Humbird A.1)": {"finance.ccf_rate": 0.10, "finance.ccf_life_y": 20},
            "spent cells free (feed or fertiliser outlet)": {"utilities.biomass_disposal_usd_t_dry": 0.0},
            "compressor power as in Humbird's workbook (k in place of (k-1)/k)": {"fermenter.compressor_formula": "humbird_a1"},
            "dissolved O2 held at 50% of air saturation": {"fermenter.DO_top_frac": 0.5},
            "kLa without the temperature factor (Humbird 2017 Eq. 2)": {"fermenter.kla_temperature_factor": 1.0},
            "seed fermenters priced on Humbird's aseptic curve": {"capital.seed_fermenter_quote": "acce_aseptic"}}
    res["base_sensitivities"] = {k: plant.evaluate(params.override(BASE, {"plant.product": "blg", **ch})).msp_ccf
                                 for k, ch in sens.items()}
    res["labels"] = LABELS
    res["constants"] = constants()


def constants() -> dict:
    """Model-derived constants quoted in the report text (so none is typed there)."""
    import dataclasses

    from pftea import equipment as eq
    from pftea import pf_ferm as pf
    from pftea import product as pr
    from pftea import thermo as th
    v_ = params.v
    f = v_(BASE, "hosts.kphaffii.biomass_formula")
    host = pf.Host(bio=th.biomass(f["C"], f["H"], f["O"], f["N"]), mu_max=v_(BASE, "hosts.kphaffii.mu_max_per_h"),
                   T_C=v_(BASE, "hosts.kphaffii.temperature_C"))
    g = host.growth
    vessel = plant._vessel(BASE)
    cond = plant._conditions(BASE)
    nrel = cal.load("nrel2011_cellulase")["overrides"]
    to2007 = nrel["capital.cost_index_2018_to_2025"]
    vf = v_(BASE, "capital.vendor_fermenter")
    r = plant.evaluate(params.override(BASE, {"plant.product": "blg"}))
    cap = {f"cap_per_broth_{x}": vessel.cap_per_broth(x) for x in (80, 107, 150)}
    ceil = {}
    for k in ("blg", "ova"):
        q = params.override(BASE, {"plant.product": k})
        ceil[k] = dict(atp_per_residue=plant.atp_per_residue(q), ceiling=plant.energetic_ceiling(q),
                       polymerisation_only=pr.energetic_ceiling(pr.protein(k), th.get("Glucose (s)"),
                                                                v_(BASE, "energetics.atp_per_peptide_bond"),
                                                                v_(BASE, "energetics.substrate_atp_per_glucose")
                                                                + 12 * v_(BASE, "hosts.kphaffii.po_ratio")))
    # the most production-phase maintenance the base expression phase can carry with the product made
    # at the energetic ceiling (review H2): same glucose per hour, m_s + q_p/Y_ps = m_max + q_p/ceiling
    ms_max = {}
    for k in ("blg", "ova"):
        rk = r if k == "blg" else plant.evaluate(params.override(BASE, {"plant.product": k}))
        qp = rk.design["q_p_mg_g_h"] / 1000
        ms_max[k] = (v_(BASE, "hosts.kphaffii.m_s_prod_g_g_h")
                     + qp * (1 / v_(BASE, "strain.Y_ps_g_g") - 1 / ceil[k]["ceiling"]))
    # aeration energy per kg O2 transferred in the base batch, and with the workbook's compressor formula
    def aer(res_):
        return (res_.batch.comp_kWh + res_.batch.agit_kWh) / (res_.batch.o2_kmol * 32)
    r_wb = plant.evaluate(params.override(BASE, {"plant.product": "blg", "fermenter.compressor_formula": "humbird_a1"}))
    r_do = plant.evaluate(params.override(BASE, {"plant.product": "blg", "fermenter.DO_top_frac": 0.5}))
    # compressor + agitator power per kg O2 at OUR 150 in the base vessel at maximum fill, with each
    # compressor formula (Humbird's Fig1.3 sheet gives 0.501 with his; engineering.yaml)
    liq = vessel.fill_max * vessel.volume_m3
    aer150 = {}
    for form in ("adiabatic", "humbird_a1"):
        a_ = pf.aerate(dataclasses.replace(vessel, compressor_formula=form), cond, 150.0, liq)
        aer150[form] = (a_["comp_kW"] + a_["agit_kW"]) / (150.0 * liq * 0.032)
    seed = r.capex["ISBL: seed fermenters"]
    ferm = r.capex["ISBL: production fermenters"] + seed
    return dict(
        ms_prod_max_at_ceiling=ms_max, aeration_our150=aer150,
        aeration_kWh_per_kg_o2=aer(r), aeration_kWh_per_kg_o2_workbook_compressor=aer(r_wb),
        aeration_kWh_per_kg_o2_do50=aer(r_do),
        compressor_share_of_aeration=r.batch.comp_kWh / (r.batch.comp_kWh + r.batch.agit_kWh),
        aeration_electricity_usd_per_kg=(r.batch.comp_kWh + r.batch.agit_kWh) * r.design["n_batches"]
        * v_(BASE, "utilities.electricity_usd_kWh") / (v_(BASE, "plant.annual_target_protein_t") * 1000),
        seeds_m3=r.design["seeds_m3"], seed_units=r.design["seed_units"], seed_share_of_fermenter_cost=seed / ferm,
        seed_acce_over_vendor=eq.fermenter(r.design["seeds_m3"][0], v_(BASE, "capital.fermenter_exponent_above_table"))
        / (vf["cost_2018usd_300m3"] * (r.design["seeds_m3"][0] / 300) ** vf["exponent"]),
        Yx_max=g.bio.mw / (-g.growth.of("Glucose (s)") * pf.MW["glc"]),
        m_s_tijhuis=host.m_s_tijhuis,
        gamma_biomass=g.bio.gamma, gamma_blg=pr.protein("blg").species.gamma, gamma_ova=pr.protein("ova").species.gamma,
        atp_per_glucose=v_(BASE, "energetics.substrate_atp_per_glucose") + 12 * v_(BASE, "hosts.kphaffii.po_ratio"),
        otr_aeration_only=pf.otr_physical(dataclasses.replace(vessel, heat_max_kW_m3=None), cond),
        otr_with_heat=pf.otr_physical(vessel, cond),
        **cap,
        strferm_300m3_2007usd=eq.fermenter(300, v_(BASE, "capital.fermenter_exponent_above_table")) * to2007,
        nrel_fermenter_300m3_2007usd=vf["cost_2018usd_300m3"] * to2007,
        vendor_200m3_2025usd=vf["cost_2018usd_300m3"] * (200 / 300) ** vf["exponent"] * v_(BASE, "capital.cost_index_2018_to_2025"),
        strferm_200m3_2025usd=eq.fermenter(200, v_(BASE, "capital.fermenter_exponent_above_table"))
        * v_(BASE, "capital.cost_index_2018_to_2025"),
        o2_mol_per_kg_made=r.batch.o2_kmol * 1000 / r.batch.product_kg,
        energetic=ceil,
        heat_plant_peak_kW=r.design["heat_plant_peak_kW"], heat_sum_of_peaks_kW=r.design["heat_sum_of_peaks_kW"],
        qs_production_g_g_h=r.batch.glucose_prod_kg / (r.batch.cells_kg * v_(BASE, "strain.t_prod_h")),
        # an alternative, non-bounding estimate (review FS-2): Heijnen's growth dissipation applied to the
        # protein as if it were biomass
        heijnen_protein_yield={k: (lambda gm: pr.protein(k).species.mw / (-gm.growth.of("Glucose (s)") * pf.MW["glc"]))(
            th.GrowthModel(pr.protein(k).species, th.get("Glucose (s)"), v_(BASE, "hosts.kphaffii.temperature_C")))
            for k in ("blg", "ova")},
    )


def s_scenarios(res):
    res["scenarios"] = {}
    for name in ("academic", "industry"):
        for prod in ("blg", "ova"):
            res["scenarios"][f"{name}/{prod}"] = summary(sc.run(name, prod))
            res["scenarios"][f"{name}/{prod}/light"] = summary(sc.run(name, prod, sc.LIGHT))
            res["scenarios"][f"{name}/{prod}/aseptic"] = summary(sc.run(name, prod, sc.ASEPTIC))
            res["scenarios"][f"{name}/{prod}/eu"] = summary(sc.run(name, prod, {"plant.location": "eu_nw"}))
    # academic BLG on glucose (Li 2026) beside the ethanol-induced best titer (Yao 2026)
    res["scenarios"]["academic/blg_li2026"] = summary(sc.run("academic", "blg", variant="blg_li2026"))
    res["scenarios"]["academic/blg_li2026/light"] = summary(sc.run("academic", "blg", sc.LIGHT, variant="blg_li2026"))
    res["scenarios"]["academic/ova_intact_1gL"] = summary(sc.run("academic", "ova", variant="ova_intact_1gL"))


def s_physical_limit(res):
    """Cost floors, their binding constraints, and the sensitivities to the limits that bind."""
    res["physical_limit"] = {}

    def put(key, pl):
        if pl:
            res["physical_limit"][key] = dict(summary(pl["result"]), X_prod=pl["X_prod"], t_prod=pl["t_prod"],
                                              titer=pl["titer"], binding=pl["binding"])
    for prod in ("blg", "ova"):
        for label, extra in (("humbird", {}), ("light", sc.LIGHT)):
            put(f"{prod}/{label}", sc.physical_limit(prod, extra, fast=FAST))
    # the specific-productivity ceiling (grade D) that binds at the floor (review FS-3/SC-2: from the
    # base design's rate, 5, to NREL's implied 120), the feed, and Intelligen's unsourced OVA solubility
    for q in (5, 10, 20, 120):
        put(f"blg/humbird/q_p_max_{q}", sc.physical_limit("blg", {"strain.q_p_max_mg_g_h": q}, fast=True))
    put("blg/humbird/feed_500", sc.physical_limit("blg", {"fermenter.feed_glucose_g_L": 500.0}, fast=True))
    put("blg/humbird/aseptic", sc.physical_limit("blg", sc.ASEPTIC, fast=True))
    put("ova/humbird/solubility_50", sc.physical_limit("ova", {"plant.solubility_override_g_L": 50.0}, fast=FAST))
    # what process design alone can do with base biology, capital and scale (review SC-1): cell
    # density, production time and titer free, everything else at base; by secretion ceiling
    res["best_design_base"] = {}
    for q in (5, 10, 20, 40):
        pl = sc.best_design(params.override(BASE, {"plant.product": "blg", "strain.q_p_max_mg_g_h": float(q)}), fast=True)
        if pl:
            res["best_design_base"][str(q)] = dict(summary(pl["result"]), X_prod=pl["X_prod"], t_prod=pl["t_prod"],
                                                   titer=pl["titer"], binding=pl["binding"])


def s_demonstrated(res):
    """The best demonstrated secretion rate for a secreted protein in a K. phaffii glucose fed-batch
    (Prielhofer et al. 2018: q_P,max 2.1 mg/g/h near mu 0.1/h; data/evidence/hosts.yaml), as a secretion
    ceiling for the best-case and base-biology searches (added after the Phase F review)."""
    q = 2.1
    pl = sc.physical_limit("blg", {"strain.q_p_max_mg_g_h": q}, fast=True)
    if pl:
        res.setdefault("physical_limit", {})[f"blg/humbird/q_p_max_{q}"] = dict(
            summary(pl["result"]), X_prod=pl["X_prod"], t_prod=pl["t_prod"], titer=pl["titer"], binding=pl["binding"])
    bd = sc.best_design(params.override(BASE, {"plant.product": "blg", "strain.q_p_max_mg_g_h": q}), fast=True)
    if bd:
        res.setdefault("best_design_base", {})[str(q)] = dict(summary(bd["result"]), X_prod=bd["X_prod"], t_prod=bd["t_prod"],
                                                              titer=bd["titer"], binding=bd["binding"])


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
    """Fig. 3 and table: titer needed for a target price, and the titer ceiling, per production time.

    Also: the ceiling on Humbird A.1's OTR basis (cap per m3 of cell-free liquid; audit R2-1) and
    how the 72 h ceiling moves with the yield and the production-phase maintenance (audit R7-C1).
    """
    t_prods = [36, 48, 60, 72, 96, 120]
    targets = [10, 20, 50]
    res["required_t_prods"] = t_prods
    res["required"], res["titer_ceiling"], res["titer_ceiling_v2basis"], res["titer_ceiling_feed600"] = {}, {}, {}, {}
    v2 = {"fermenter.otr_cap_basis": "broth", "fermenter.otr_cap_mol_m3_h": 150.0}
    f600 = {"fermenter.feed_glucose_g_L": 600.0}

    def rows_for(p, tg, ceilings):
        rows = []
        for tp, ceil in zip(t_prods, ceilings):
            # search only the feasible range: past the ceiling the cost curve is not physical
            T = sc.required_titer(p, tg, tp, hi=ceil) if ceil else None
            qp = (plant.evaluate(params.override(p, {"strain.titer_g_L": T, "strain.t_prod_h": float(tp)})).design["q_p_mg_g_h"]
                  if T else None)
            rows.append(dict(titer=T, feasible=T is not None, ceiling=ceil, q_p_mg_g_h=qp))
        return rows
    for prod in ("blg", "ova"):
        p0 = params.override(BASE, {"plant.product": prod})
        res["titer_ceiling"][prod] = [sc.max_feasible_titer(p0, tp) for tp in t_prods]
        res["titer_ceiling_v2basis"][prod] = [sc.max_feasible_titer(params.override(p0, v2), tp) for tp in t_prods]
        res["titer_ceiling_feed600"][prod] = [sc.max_feasible_titer(params.override(p0, f600), tp) for tp in t_prods]
        for label, extra in (("humbird", {}), ("light", sc.LIGHT)):
            p = params.override(p0, extra)
            res["required"][f"{prod}/{label}"] = {str(tg): rows_for(p, tg, res["titer_ceiling"][prod]) for tg in targets}
            res["required"][f"{prod}/{label}/feed600"] = {
                str(tg): rows_for(params.override(p, f600), tg, res["titer_ceiling_feed600"][prod]) for tg in (10, 20)}
    p0 = params.override(BASE, {"plant.product": "blg"})
    yields = [0.28, 0.35, 0.40, 0.465, 0.50, 0.535]
    maint = [0.0023, 0.00437, 0.008, 0.0161]
    res["ceiling_vs"] = {
        "Y_ps_g_g": dict(values=yields, ceiling_72h=[sc.max_feasible_titer(params.override(p0, {"strain.Y_ps_g_g": y}), 72)
                                                     for y in yields]),
        "m_s_prod_g_g_h": dict(values=maint, ceiling_72h=[sc.max_feasible_titer(
            params.override(p0, {"hosts.kphaffii.m_s_prod_g_g_h": m}), 72) for m in maint]),
    }


def s_ceiling(res):
    """What sets the titer ceiling: the limit that fails just above it, and how the ceiling moves when
    the design choices behind it move (minimum starting volume, feed concentration, O2-cap basis)."""
    p0 = params.override(BASE, {"plant.product": "blg"})
    cases = {"base": {},
             "glucose feed 600 g/L": {"fermenter.feed_glucose_g_L": 600.0},
             "80 g/L cells at the start of production": {"strain.X_prod_g_L": 80.0},
             "minimum fill 0.20": {"fermenter.min_initial_fill": 0.20},
             "minimum fill 0.35": {"fermenter.min_initial_fill": 0.35},
             "minimum fill 0.40": {"fermenter.min_initial_fill": 0.40},
             "minimum fill 0.50 (NREL)": {"fermenter.min_initial_fill": 0.50},
             "no minimum fill": {"fermenter.min_initial_fill": 0.01},
             "no minimum fill, O2 cap 150 (bubble column)": {"fermenter.min_initial_fill": 0.01,
                                                             "fermenter.otr_cap_mol_m3_h": 150.0}}
    kinds = (("initial fill", "minimum starting volume"), ("OUR", "O2 transfer"), ("heat", "heat removal"),
             ("productivity", "secretion ceiling"), ("reachable", "titer not reachable"))
    out = {}
    for label, ch in cases.items():
        p = params.override(p0, ch)
        rows = []
        for tp in (36, 72, 120):
            c = sc.max_feasible_titer(p, tp)
            lim = None
            if c:
                r = plant.evaluate(params.override(p, {"strain.t_prod_h": float(tp), "strain.titer_g_L": c * 1.03}))
                lim = next((name for key, name in kinds if any(key in f for f in r.flags)), "; ".join(r.flags))
            rows.append(dict(t_prod=tp, ceiling=c, limit=lim))
        out[label] = rows
    res["ceiling_limits"] = out


def s_claims(res):
    """Q5: shortest production phase in which each claimed titer is feasible, and the MSP there."""
    acad = sc.load("academic")["ova"]
    res["claims"] = []
    for c in bm.claims():
        ch = {"plant.product": c["model_product"], "strain.host": c["model_host"]}
        if c["model_host"] == "treesei":
            ch.update({k: acad[k] for k in ("strain.X_prod_g_L", "strain.mu_prod_per_h")})
        p = params.override(BASE, ch)
        t_own = float(c.get("t_prod_h", 72))                  # the claim's own production time, else 72 h
        row = dict(label=c["label"], titer=c["titer"], host=c["model_host"], product=c["model_product"],
                   X_prod=float(params.v(p, "strain.X_prod_g_L")), t_prod_own=t_own,
                   ceiling_own=sc.max_feasible_titer(p, t_own))
        r = plant.evaluate(params.override(p, {"strain.titer_g_L": c["titer"], "strain.t_prod_h": t_own}))
        row["feasible_own"] = sc.is_feasible(r)
        if row["feasible_own"]:
            row["msp_own_humbird"] = r.msp_ccf
            row["msp_own_light"] = plant.evaluate(params.override(p, {"strain.titer_g_L": c["titer"],
                                                                         "strain.t_prod_h": t_own, **sc.LIGHT})).msp_ccf
            row["q_p_own"] = float(r.design["q_p_mg_g_h"])
        # best case: the shortest feasible production phase, where q_p runs at its ceiling
        tp = sc.min_feasible_t_prod(p, c["titer"])
        row["t_prod_min"] = tp
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
    energy = {k: us_price(k) for k in ("utilities.electricity_usd_kWh", "utilities.natural_gas_usd_GJ")}
    cases = {
        "EU base": {},
        "EU with US energy prices": energy,
        "EU with US glucose price": {"utilities.glucose_usd_kg": us_price("utilities.glucose_usd_kg")},
        "EU with US construction cost": {"capital.location_factor": 1.0},
        "EU with US wages": {"labour.operator_salary_usd": us_price("labour.operator_salary_usd")},
        "EU with US spent-cell disposal fee": {"utilities.biomass_disposal_usd_t_dry": us_price("utilities.biomass_disposal_usd_t_dry")},
        "EU with US water prices": {"utilities.water_usd_m3": us_price("utilities.water_usd_m3"),
                                    "utilities.wastewater_usd_m3": us_price("utilities.wastewater_usd_m3")},
        "EU, capital at 4%/10 yr": {"finance.ccf_rate": 0.04},
        "EU, capital at 7.5%/20 yr": {"finance.ccf_life_y": 20},
        "EU, capital at 4%/20 yr": {"finance.ccf_rate": 0.04, "finance.ccf_life_y": 20},
    }
    res["policy"] = {k: plant.evaluate(params.override(BASE, {**eu, **ch})).msp_ccf for k, ch in cases.items()}
    res["policy"]["US base"] = plant.evaluate(params.override(BASE, {"plant.product": "blg"})).msp_ccf


def s_tornado(res):
    """Industry-benchmark BLG; the scenario's own ranges (mc_ranges) replace base ranges where given."""
    p = params.override(P_IND, {k: dict(val) for k, val in sc.load("industry").get("mc_ranges", {}).items()})
    skip = ("plant.", "hosts.treesei", "dsp.cex_", "dsp.dryer_feed_solids_ova", "dsp.dryer_feed_solids_lf", "energetics.")
    paths = [x for x in params.ranged_leaves(p) if not x.startswith(skip)]
    res["tornado"] = sc.tornado(p, paths)


def s_monte_carlo(res):
    n = 60 if FAST else 400
    res["monte_carlo"] = {}
    for name in ("academic", "industry"):
        for prod in ("blg", "ova"):
            p = sc.scenario_params(name, prod)
            paths, ranges = sc.mc_config(name, prod)
            mc = sc.monte_carlo(p, paths, n=n, seed=1, ranges=ranges)
            base = plant.evaluate(p).msp_ccf
            ok = mc["msp"][mc["feasible"]]
            res["monte_carlo"][f"{name}/{prod}"] = dict(p10=mc["p10"], p50=mc["p50"], p90=mc["p90"], n=int(len(mc["msp"])),
                                                       p10_all=mc["p10_all"], p50_all=mc["p50_all"], p90_all=mc["p90_all"],
                                                       infeasible_reasons=mc["infeasible_reasons"], input_means=mc["input_means"],
                                                       feasible_frac=float(mc["feasible"].mean()), base=base,
                                                       base_percentile=float((ok < base).mean() * 100) if ok.size else None,
                                                       msp=[float(x) for x in mc["msp"]],
                                                       feasible=[bool(x) for x in mc["feasible"]])


def s_scale(res):
    res["scale"] = sc.scale_curve(P_IND, [1000, 2500, 5000, 10000, 25000, 50000, 100000])


def s_calibration(res):
    res["calibration"] = {"bakers_yeast": {"cop": hy.run()["cop"], "humbird": 1.8899, "market_implied": 1.90}}
    # what the yeast anchor can and cannot tell apart (review SC-3/HM-2): Humbird's A.1 with other
    # capital charges and a lighter, NREL-like stack (TCI 3.2 x listed equipment, fixed costs 1.2% + 0.7%)
    import copy
    c0 = hy.load_case()

    def a1(ch):
        c = copy.deepcopy(c0)
        for (sec, k), x in ch.items():
            node = c[sec][k]
            if isinstance(node, dict):
                node["value"] = x
            else:
                c[sec][k] = x
        return hy.run(c)["cop"]
    res["calibration"]["bakers_yeast_stacks"] = {
        "as published (Lang 4.5, 20% missing, 4% + 5% of TCI, 10%/20 yr)": hy.run(c0)["cop"],
        "with the PF capital charge (7.5%/10 yr)": a1({("finance", "irr"): 0.075, ("finance", "lifetime_y"): 10}),
        "Humbird factors, NREL-like fixed costs (1.5% + 0.7%)": a1({("finance", "maintenance_frac_tci"): 0.015,
                                                                      ("finance", "insurance_tax_frac_tci"): 0.007}),
        "NREL-like stack (TCI 3.2 x listed, 1.2% + 0.7%)": a1({("plant", "lang_factor"): 2.56,
                                                                 ("finance", "maintenance_frac_tci"): 0.012,
                                                                 ("finance", "insurance_tax_frac_tci"): 0.007}),
        "market band, 33% margin on price": [2.20 * 0.67, 2.80 * 0.67],
        "market band, 33% margin on cost": [2.20 / 1.33, 2.80 / 1.33]}
    for name, light in (("nrel2011_cellulase", cal.LIGHT), ("intelligen2025_ova", None),
                        ("voutilainen2021_case", cal.voutilainen_conventions("nrel"))):
        o = cal.run(name)
        res["calibration"][name] = {k: [float(a), float(b)] for k, (a, b) in o["compare"].items()}
        res["calibration"][name]["msp_ccf_per_kg_target"] = float(o["result"].msp_ccf)
        res["calibration"][name]["design"] = {"n_fermenters": int(o["result"].design["N_prod_int"]),
                                              "recovery": float(o["result"].design["recovery"]),
                                              "t_growth_h": float(o["result"].design["t_growth_h"])}
        if light:    # Intelligen's target is already recast into the Humbird convention (A1 step 1.4)
            k0, (a0, b0) = next(iter(cal.run(name, light)["compare"].items()))
            res["calibration"][name][k0 + " [light convention]"] = [float(a0), float(b0)]
    o = cal.run("voutilainen2021_case", cal.voutilainen_conventions("humbird"))
    k0, (a0, b0) = next(iter(o["compare"].items()))
    res["calibration"]["voutilainen2021_case"][k0 + " [their fixed costs, Humbird capital]"] = [float(a0), float(b0)]


def s_equivalents(res):
    """Milk and egg equivalents: modelled $/kg protein per litre of milk and per egg, beside the
    prices of milk and eggs, and the titer at which PF protein matches them (72 h production)."""
    eq = bm.equivalents()
    out = {"sources": eq, "cases": {}, "break_even_titer_72h": {}}
    for name, prod in (("milk", "blg"), ("egg", "ova")):
        d = eq[name]
        cases = {"base": {}, "base, design-report capital": sc.LIGHT}
        rows = {}
        for label, extra in cases.items():
            msp = plant.evaluate(params.override(BASE, {"plant.product": prod, **extra})).msp_ccf
            rows[label] = dict(msp=msp, target_per_unit=msp * d["target_g"] / 1000,
                               all_protein_per_unit=msp * d["all_protein_g"] / 1000)
        for scen in ("industry", "academic"):
            msp = sc.run(scen, prod).msp_ccf
            rows[scen] = dict(msp=msp, target_per_unit=msp * d["target_g"] / 1000,
                              all_protein_per_unit=msp * d["all_protein_g"] / 1000)
        out["cases"][name] = rows
        p = params.override(BASE, {"plant.product": prod})
        ceil = sc.max_feasible_titer(p, 72)
        be = {}
        for lab, series in d["protein_equivalent"].items():
            for tag, target in (("2025", series[max(series)]), ("band low", min(series.values())),
                                ("band high", max(series.values()))):
                T = sc.required_titer(p, target, 72, hi=ceil) if ceil else None
                be[f"{lab} [{tag}]"] = dict(target_usd_kg=target, titer=T)
        out["break_even_titer_72h"][name] = dict(ceiling=ceil, rows=be)
    # what the same protein costs bought as the incumbent ingredient, per unit and year (review SC-10):
    # dried egg white per egg, and a litre's whey protein at WPC80/WPI prices as a share of the
    # farm milk price in the same year
    comp = next(e for e in yaml.safe_load((ROOT / "data/evidence/milk_egg.yaml").read_text())
                if e["key"] == "derived_protein_per_litre_and_per_egg")["values"]
    inc = bm.incumbents()
    by_year = lambda d: {y: np.mean([s_[y] for s_ in d["series"].values() if y in s_])  # noqa: E731
                         for y in sorted({y for s_ in d["series"].values() for y in s_})}
    whey, egg = by_year(inc["whey"]), by_year(inc["egg"])
    farm = eq["milk"]["prices"]["US farm milk (all-milk price)"]
    out["ingredient_per_unit"] = dict(
        whey_g_per_L=comp["milk_whey_protein_g_per_L"], egg_white_g_per_egg=comp["egg_white_protein_g_per_large_egg"],
        whey_per_litre={y: x * comp["milk_whey_protein_g_per_L"] / 1000 for y, x in whey.items()},
        whey_share_of_farm_milk={y: x * comp["milk_whey_protein_g_per_L"] / 1000 / farm[y] for y, x in whey.items() if y in farm},
        dried_egg_white_per_egg={y: x * comp["egg_white_protein_g_per_large_egg"] / 1000 for y, x in egg.items()},
        # egg white against whey, $/kg protein by year (review SC-9: egg white is not always dearer)
        egg_vs_whey={y: dict(egg=egg[y], whey=whey[y]) for y in egg if y in whey})
    res["equivalents"] = out


def s_lactoferrin(res):
    """Contrast case: bovine lactoferrin at 250 t/yr (data/pf/scenarios/lactoferrin.yaml)."""
    out = {"reported_prices": bm.reported_prices()["lactoferrin"], "cases": {}}
    for var in ("lf", "lf_academic", "lf_ufdf_only"):
        for label, extra in (("humbird", {}), ("light", sc.LIGHT)):
            out["cases"][f"{var}/{label}"] = summary(sc.run("lactoferrin", "lf", extra, variant=var))
    p = sc.scenario_params("lactoferrin", "lf")
    titers = [1, 2.8, 5, 10, 20, 30]
    out["cost_vs_titer"] = dict(titers=titers, msp=[plant.evaluate(params.override(p, {"strain.titer_g_L": float(T)})).msp_ccf
                                                    for T in titers])
    scales = [100, 250, 1000, 2500]
    out["cost_vs_scale"] = dict(t_per_yr=scales, msp=[plant.evaluate(params.override(p, {"plant.annual_target_protein_t": float(x)})).msp_ccf
                                                       for x in scales])
    out["resin"] = {f"{k}={x}": plant.evaluate(params.override(p, {k: x})).msp_ccf
                    for k, xs in (("dsp.cex_resin_life_cycles", (125, 1000)), ("dsp.cex_resin_usd_L", (100, 2000)),
                                  ("dsp.cex_hardware_usd_per_L_resin", (300, 3000))) for x in xs}
    # reconciliation with Intelligen's own model (review L). SuperPro reports a unit production cost:
    # operating cost with depreciation inside 'facility-dependent' and no return on capital, so it is set
    # against our cost of production, in its categories, per kg lactoferrin; ours on the same route, and
    # with their stated design inputs (lactoferrin.yaml lf_intelligen_a/b)
    def superpro(p_):
        r_ = plant.evaluate(p_)
        a, kg = r_.annual, params.v(p_, "plant.annual_target_protein_t") * 1000
        water = r_.physical["water_m3"] * kg * params.v(p_, "utilities.water_usd_m3")
        cats = {"raw materials": a["glucose"] + a["ammonia"] + a["salts & other media"] + a["DSP chemicals"] + water,
                "labour": a["labour"],
                "facility": a["maintenance"] + a["insurance"] + r_.tci / params.v(p_, "finance.ccf_life_y"),
                "lab/QC/QA": 0.0,
                "consumables": a["chromatography resin"] + a["membranes"],
                "waste": a["biomass disposal"] + a["water & wastewater"] - water,
                "utilities": a["electricity"] + a["natural gas & steam"]}
        assert abs(sum(cats.values()) / kg - r_.cop) < 1e-6 * r_.cop, (sum(cats.values()) / kg, r_.cop)
        return dict(cop=r_.cop, msp_ccf=r_.msp_ccf, tci=r_.tci, per_kg={k: x / kg for k, x in cats.items()},
                    n_fermenters=r_.design["N_prod_int"], recovery=r_.design["recovery"], feasible=sc.is_feasible(r_))
    out["reconciliation"] = {var: superpro(sc.scenario_params("lactoferrin", "lf", variant=var))
                             for var in ("lf", "lf_ufdf_only", "lf_intelligen_a", "lf_intelligen_b")}
    res["lactoferrin"] = out


SECTIONS = {"base": s_base, "scenarios": s_scenarios, "physical_limit": s_physical_limit, "demonstrated": s_demonstrated,
            "cost_vs_titer": s_cost_vs_titer, "bridge": s_bridge, "required": s_required, "ceiling": s_ceiling,
            "claims": s_claims,
            "policy": s_policy,
            "tornado": s_tornado,
            "monte_carlo": s_monte_carlo, "scale": s_scale, "calibration": s_calibration,
            "equivalents": s_equivalents, "lactoferrin": s_lactoferrin}

if __name__ == "__main__":
    t0 = time.time()
    path = OUT / "analyses.json"
    res = json.loads(path.read_text()) if ONLY and path.exists() else {}
    part = OUT / "analyses.partial.json"          # checkpoint after each section (resume with --only)
    for name, fn in SECTIONS.items():
        if ONLY and name not in ONLY:
            continue
        fn(res)
        part.write_text(json.dumps(clean(res), indent=1, default=float, allow_nan=False))
        print(f"{name} done {time.time() - t0:.0f}s", flush=True)
    res.update(generated=time.strftime("%Y-%m-%d %H:%M"), fast=FAST if not ONLY else res.get("fast", FAST))
    res["runtime_s"] = time.time() - t0
    path.write_text(json.dumps(clean(res), indent=1, default=float, allow_nan=False))
    part.unlink(missing_ok=True)
    print(f"wrote results/analyses.json in {res['runtime_s']:.0f}s")
