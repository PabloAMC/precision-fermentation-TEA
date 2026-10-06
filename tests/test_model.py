"""Model invariants (audit R4-18): parameter semantics, conservation laws, derivations and
scenario identities. Each test states the physics or bookkeeping it guards."""
import math

import numpy as np
import pytest

from pftea import params, plant
from pftea import pf_ferm as pf
from pftea import product as pr
from pftea import scenarios as sc
from pftea import thermo as th
from pftea.params import v

BASE = params.load()


@pytest.fixture(scope="module")
def blg():
    p = params.override(BASE, {"plant.product": "blg"})
    return p, plant.evaluate(p)


# ---------------------------------------------------------------- parameters
def test_location_keyed_ranges():
    us = params.override(BASE, {"plant.location": "us_midwest"})
    eu = params.override(BASE, {"plant.location": "eu_nw"})
    assert params.bounds(us, "utilities.electricity_usd_kWh") == (0.072, 0.1014)
    assert params.bounds(eu, "utilities.electricity_usd_kWh") == (0.1297, 0.1631)
    lo, hi = params.bounds(eu, "utilities.electricity_usd_kWh")
    assert lo <= v(eu, "utilities.electricity_usd_kWh") <= hi


def test_override_resolves_location_first():
    """A location-keyed override lands on the new location whatever the key order (R4-11)."""
    a = params.override(BASE, {"utilities.glucose_usd_kg": 0.9, "plant.location": "eu_nw"})
    b = params.override(BASE, {"plant.location": "eu_nw", "utilities.glucose_usd_kg": 0.9})
    assert v(a, "utilities.glucose_usd_kg") == v(b, "utilities.glucose_usd_kg") == 0.9
    assert v(params.override(a, {"plant.location": "us_midwest"}), "utilities.glucose_usd_kg") == 0.40


def test_sample_refuses_out_of_range_mode():
    p = params.override(BASE, {"strain.X_prod_g_L": 35.0})            # below the 40-150 range
    with pytest.raises(ValueError):
        params.sample(p, np.random.default_rng(0), ["strain.X_prod_g_L"])


def test_sample_degenerate_range_returns_mode():
    p = params.override(BASE, {"strain.titer_g_L": {"low": 13.88, "high": 13.88, "value": 13.88}})
    q = params.sample(p, np.random.default_rng(0), ["strain.titer_g_L"])
    assert v(q, "strain.titer_g_L") == 13.88


def test_every_ranged_value_inside_its_range():
    for loc in params.LOCATIONS:
        p = params.override(BASE, {"plant.location": loc})
        for path in params.ranged_leaves(p):
            lo, hi = params.bounds(p, path)
            assert lo - 1e-12 <= v(p, path) <= hi + 1e-12, (loc, path)


# ---------------------------------------------------------------- stoichiometry and derivations
@pytest.mark.parametrize("key", ["blg", "ova"])
def test_product_reaction_element_balance(key):
    rx = pr.product_reaction(pr.protein(key), th.get("Glucose (s)"), v(BASE, "strain.Y_ps_g_g"))
    for e in ("C", "H", "O", "N"):
        assert abs(rx.residual(e)) < 1e-9


def test_y_ps_reproduces_intelligen_eq2():
    """base Y_ps closes Intelligen's Eq. 2: glucose per g rOVA in expression = 100/28, given the
    model's growth yield, the measured production-phase m_s and Intelligen's q_p (base.yaml)."""
    f = v(BASE, "hosts.kphaffii.biomass_formula")
    host = pf.Host(bio=th.biomass(f["C"], f["H"], f["O"], f["N"]), mu_max=0.2, T_C=30)
    g = host.growth
    Yx = g.bio.mw / (-g.growth.of("Glucose (s)") * pf.MW["glc"])
    P, F_end = 30 * 107.0, 92 * 107.0
    F0 = F_end - 8 / 28 * P
    qp = P / ((F_end - F0) * 72 / math.log(F_end / F0))      # q_p = P / integral of F dt (exponential growth)
    inv = 100 / 28 - (8 / 28) / Yx - v(BASE, "hosts.kphaffii.m_s_prod_g_g_h") / qp
    assert 1 / inv == pytest.approx(v(BASE, "strain.Y_ps_g_g"), rel=0.005)
    assert math.log(F_end / F0) / 72 == pytest.approx(v(BASE, "strain.mu_prod_per_h"), rel=0.05)


def test_production_maintenance_uses_measured_ms():
    f = v(BASE, "hosts.kphaffii.biomass_formula")
    host = pf.Host(bio=th.biomass(f["C"], f["H"], f["O"], f["N"]), mu_max=0.2, T_C=30, maint_factor=1.0,
                   m_s_prod=0.00437)
    assert host.maint(prod=False) == 1.0
    assert host.maint(prod=True) * host.m_s_tijhuis == pytest.approx(0.00437, rel=1e-12)


def test_energetic_ceiling_below_electron_ceiling():
    for key in ("blg", "ova"):
        p = params.override(BASE, {"plant.product": key})
        assert 0.5 < plant.energetic_ceiling(p) < pr.electron_ceiling(pr.protein(key), th.get("Glucose (s)"))


# ---------------------------------------------------------------- conservation
def test_batch_carbon_balance(blg):
    """Carbon in (glucose + inoculum) = carbon out (cells + product + CO2), within 0.5%."""
    p, r = blg
    b = r.batch
    host = plant._host(p)
    prot = pr.protein("blg")
    c_in = b.glucose_kg / pf.MW["glc"] * 6 + b.W0 * v(p, "strain.X0_g_L") / host.growth.bio.mw
    c_out = b.cells_kg / host.growth.bio.mw + b.product_kg / prot.species.mw + b.co2_kmol
    assert c_out == pytest.approx(c_in, rel=0.005)


def test_paste_recovery_matches_hand_calculation(blg):
    """Two-stage centrifugation: recovery = 1 - phi^2, phi = e Vp / (V1 - V_wc) (plant.py block 2a)."""
    p, r = blg
    b = r.batch
    dil = max(b.X_end / v(p, "dsp.dilution_to_g_L_cells"), 1.0)
    V1 = b.W_end * dil
    V_wc = b.cells_kg / (1000 * 0.3)
    e = v(p, "dsp.paste_extracellular_frac")
    phi = e * (V_wc / (1 - e)) / (V1 - V_wc)
    assert r.design["recovery_cell_removal"] == pytest.approx(1 - phi ** 2, rel=1e-12)


def test_recovery_is_product_of_steps(blg):
    p, r = blg
    d = r.design
    sigma, N = v(p, "dsp.uf_rejection"), v(p, "dsp.diafiltration_volumes")
    R_uf = d["CF"] ** -(1 - sigma) * math.exp(-N * (1 - sigma))
    expect = d["recovery_cell_removal"] * v(p, "dsp.mf_recovery") * R_uf * v(p, "dsp.dryer_recovery")
    assert d["recovery"] == pytest.approx(expect, rel=1e-9)


def test_dryer_feed_solids_as_specified(blg):
    p, r = blg
    assert r.design["dryer_inlet_solids"] == pytest.approx(v(p, "dsp.dryer_feed_solids_blg"), abs=0.02)


def test_whole_fermenters_costed(blg):
    """Whole vessels at the vendor-quote curve (base), or at Humbird's aseptic quotes (sensitivity)."""
    p, r = blg
    n = r.design["N_prod_int"]
    assert n == math.ceil(r.design["N_prod"] - 1e-9)
    vf = v(p, "capital.vendor_fermenter")
    V = v(p, "fermenter.volume_m3")
    idx = v(p, "capital.cost_index_2018_to_2025") * v(p, "capital.location_factor")
    assert r.capex["ISBL: production fermenters"] == pytest.approx(
        vf["cost_2018usd_300m3"] * (V / 300) ** vf["exponent"] * n * idx, rel=1e-12)
    ra = plant.evaluate(params.override(p, sc.ASEPTIC))
    per = plant.eq.fermenter(V, v(p, "capital.fermenter_exponent_above_table"))
    assert ra.capex["ISBL: production fermenters"] == pytest.approx(per * ra.design["N_prod_int"] * idx, rel=1e-12)


def test_coincident_peak_of_staggered_batches():
    """Batches of 10 h at load 1 (first 2 h at 5) started every 4 h: 3 overlap, so the peak is 5 + 1 + 1."""
    t, val = [0.0, 2.0], [5.0, 1.0]
    assert plant._coincident_peak(t, val, 10.0, 4.0) == pytest.approx(7.0)
    assert plant._coincident_peak(t, val, 10.0, 100.0) == pytest.approx(5.0)     # no overlap


def test_utilities_sized_below_sum_of_peaks(blg):
    p, r = blg
    assert r.design["heat_plant_peak_kW"] < r.design["heat_sum_of_peaks_kW"]
    assert r.design["heat_plant_peak_kW"] >= r.batch.heat_kWh / r.batch.t_total * r.design["N_prod"] * 0.5


def test_feed_volume_follows_concentration(blg):
    """A 500 g/L glucose feed adds 2 L per kg of glucose (1 kg of water per kg of glucose here)."""
    p, r = blg
    b = r.batch
    c_s, c_n = v(p, "fermenter.feed_glucose_g_L"), v(p, "fermenter.nh3_feed_g_L")
    expect = b.glucose_kg * (1000 / c_s - 1) + b.nh3_kg * (1000 / c_n - 1)
    assert b.feed_water_kg == pytest.approx(expect, rel=1e-9)


def test_cip_chemicals_inside_humbird_maintenance(blg):
    p, r = blg
    rn = plant.evaluate(params.override(p, {"finance.fixed_cost_rule": "nrel"}))
    cip = rn.annual["DSP chemicals"] - r.annual["DSP chemicals"]
    assert cip == pytest.approx(rn.design["n_batches"] * v(p, "dsp.cip_solution_kg_per_kg")
                                * rn.design["target_per_batch_kg"] * v(p, "dsp.cip_price_usd_kg"), rel=1e-6)


def test_energetic_ceiling_components():
    """ATP per residue = peptide bond + amino-acid synthesis + sulfate assimilation (3 ATP + 8 e- at P/O)."""
    p = params.override(BASE, {"plant.product": "blg"})
    prot = pr.protein("blg")
    s_res = prot.formula["S"] / prot.residues
    po = v(p, "hosts.kphaffii.po_ratio")
    assert plant.atp_per_residue(p) == pytest.approx(4 + 0.29 + s_res * (3 + 4 * po), rel=1e-12)
    assert plant.energetic_ceiling(p) < pr.energetic_ceiling(prot, th.get("Glucose (s)"), 4, 4 + 12 * po)


def test_compressor_is_textbook_adiabatic():
    """P = (D/3600) R T (r^a - 1)/(a eta), a = (k-1)/k, equals the US-unit form hp = scfm T[R]/(8130 a)
    (r^a - 1) within 0.5% (8130 vs 8102 from 379.4 scf/lbmol); Humbird's A.1 cell, with k where a
    belongs, gives ~1.6x at r = 2.12 (review H1)."""
    from pftea import fermentation as fm
    D, r = 100.0, 2.12
    a = 0.4 / 1.4
    us = D * 2.205 * 379.4 / 60 * (77 + 460) / (8130 * a) * (r ** a - 1) * 0.7457 / 0.8
    si = fm.compressor_kW_adiabatic(D, r * 1.01325, 0.8)
    assert si == pytest.approx(us, rel=0.005)
    assert fm.compressor_kW(D, r) / si == pytest.approx(1.59, abs=0.02)


def test_aeration_search_crosses_the_lean_gas_region():
    """At a high DO setpoint the exit gas is too lean below some air rate (no solution there); the
    search must widen through that region, not stop (review H1: it returned None at DO 0.5)."""
    vessel = plant._vessel(BASE)
    lo = pf.aerate(vessel, pf.Conditions(T_C=30.0, DO_top_frac=0.1258), 129.0, 0.8 * vessel.volume_m3)
    hi = pf.aerate(vessel, pf.Conditions(T_C=30.0, DO_top_frac=0.5), 129.0, 0.8 * vessel.volume_m3)
    assert lo is not None and hi is not None
    assert hi["D"] > lo["D"] and hi["comp_kW"] + hi["agit_kW"] > lo["comp_kW"] + lo["agit_kW"]


def test_seed_fermenter_quote_switch(blg):
    p, r = blg
    ra = plant.evaluate(params.override(p, {"capital.seed_fermenter_quote": "acce_aseptic"}))
    assert ra.capex["ISBL: seed fermenters"] > r.capex["ISBL: seed fermenters"]
    assert ra.capex["ISBL: production fermenters"] == pytest.approx(r.capex["ISBL: production fermenters"], rel=1e-12)


def test_crude_broth_has_no_disposal_or_dryer():
    p = params.override(BASE, {"plant.spec": "crude"})
    r = plant.evaluate(p)
    assert r.annual["biomass disposal"] == 0.0
    assert r.physical["natural_gas_MJ"] == 0.0


# ---------------------------------------------------------------- feasibility and scenarios
def test_minimum_fill_makes_design_infeasible():
    p = params.override(BASE, {"fermenter.min_initial_fill": 0.99})
    r = plant.evaluate(p)
    assert not sc.is_feasible(r)
    assert any("initial fill" in f for f in r.flags)


def test_ceiling_is_the_feasibility_edge():
    p = params.override(BASE, {"plant.product": "blg"})
    c = sc.max_feasible_titer(p, 72)
    assert sc.is_feasible(plant.evaluate(params.override(p, {"strain.titer_g_L": c})))
    assert not sc.is_feasible(plant.evaluate(params.override(p, {"strain.titer_g_L": c * 1.03})))


def test_required_titer_hits_target():
    p = params.override(BASE, {"plant.product": "blg"})
    T = sc.required_titer(p, 25.0, 72, hi=sc.max_feasible_titer(p, 72))
    assert plant.evaluate(params.override(p, {"strain.titer_g_L": T})).msp_ccf == pytest.approx(25.0, rel=0.01)


def test_bridge_ends_at_base():
    steps = [s for s in sc.bridge() if s["kind"] == "step"]
    assert steps[-1]["msp"] == pytest.approx(plant.evaluate(BASE).msp_ccf, rel=1e-12)


def test_tornado_truncates_infeasible_ends():
    p = params.override(BASE, {"strain.titer_g_L": {"low": 5, "high": 300, "value": 30}})
    row = next(r for r in sc.tornado(p, ["strain.titer_g_L"], capital_bar=False))
    assert row["truncated_high"] and row["high"] < 300
    assert sc.is_feasible(plant.evaluate(params.override(p, {"strain.titer_g_L": row["high"]})))


def test_ova_solubility_sensitivity_caps_titer():
    p = params.override(BASE, {"plant.product": "ova", "plant.solubility_override_g_L": 50.0,
                               "strain.titer_g_L": 55.0})
    assert not sc.is_feasible(plant.evaluate(p))


# ---------------------------------------------------------------- lactoferrin and equivalents
def test_lactoferrin_formula_from_uniprot():
    """Mature P24627 (689 aa, 16 disulfides): C3358 H5251 N945 O1002 S38, 76,111 Da (lactoferrin.yaml)."""
    p = pr.protein("lf")
    assert p.residues == 689
    assert {k: round(x) for k, x in p.formula.items()} == {"C": 3358, "H": 5251, "N": 945, "O": 1002, "S": 38}
    assert p.mw_molecule == pytest.approx(76111, abs=1)


def test_cex_buffers_scale_with_throughput_not_resin_volume():
    """Resin replacement and buffers depend on protein / capacity only; the cycle time sets capital."""
    p = sc.base_params("lf")
    r1 = plant.evaluate(p)
    r2 = plant.evaluate(params.override(p, {"dsp.cex_flow_cv_per_h": v(p, "dsp.cex_flow_cv_per_h") / 2}))
    for k in ("chromatography resin", "DSP chemicals", "water & wastewater"):
        assert r2.annual[k] == pytest.approx(r1.annual[k], rel=1e-9)
    assert r2.design["resin_m3"] == pytest.approx(2 * r1.design["resin_m3"], rel=1e-9)
    assert r2.tci > r1.tci


def test_cex_cycle_includes_loading():
    """Cycle = (buffer CVs + load CVs) / flow, load CVs = capacity / feed concentration (review BE-12)."""
    p = sc.base_params("lf")
    d = plant.evaluate(p).design
    assert d["cex_cycle_h"] == pytest.approx((v(p, "dsp.cex_cv_per_cycle") + d["cex_load_cv"])
                                             / v(p, "dsp.cex_flow_cv_per_h"), rel=1e-12)
    assert d["cex_load_cv"] > 10


def test_cex_recovery_in_total(blg):
    p = sc.base_params("lf")
    r = plant.evaluate(p)
    d = r.design
    sigma, N = v(p, "dsp.uf_rejection"), v(p, "dsp.cex_diafiltration_volumes")
    R_uf = d["CF"] ** -(1 - sigma) * math.exp(-N * (1 - sigma))
    expect = (d["recovery_cell_removal"] * v(p, "dsp.mf_recovery") * v(p, "dsp.cex_recovery") * R_uf
              * v(p, "dsp.dryer_recovery"))
    assert d["recovery"] == pytest.approx(expect, rel=1e-9)


def test_equivalents_units():
    from pftea import benchmarks as bm
    e = bm.equivalents()
    milk = e["milk"]["prices"]["US farm milk (all-milk price)"]
    assert milk[2025] == pytest.approx(21.19 / 45.359237 * 1.0313, rel=1e-9)     # $/cwt -> $/L, 2025$
    assert e["egg"]["target_g"]["ova"] == pytest.approx(1.96) and e["milk"]["target_g"]["cas"] == pytest.approx(9.2)


# ---------------------------------------------------------------- products on an equal footing
def test_product_base_cases():
    """BLG and OVA run on base.yaml unchanged; lactoferrin on its own design (products.yaml)."""
    for k in ("blg", "ova"):
        assert sc.product_base(k) == {}
    p = sc.base_params("lf")
    assert (v(p, "plant.product"), v(p, "plant.spec")) == ("lf", "cex")
    assert v(p, "strain.titer_g_L") == 10 and v(p, "plant.annual_target_protein_t") == 250
    assert params.bounds(p, "plant.annual_target_protein_t") is None      # no range outside the market


def test_scenarios_apply_on_the_product_base():
    """Each scenario changes only what its product block says: the lactoferrin industry case keeps
    the cation-exchange route and the market-sized plant; the physical limit caps it at the market."""
    ind = sc.scenario_params("industry", "lf")
    assert v(ind, "strain.titer_g_L") == 42 and v(ind, "plant.spec") == "cex"
    assert v(ind, "plant.annual_target_protein_t") == 250 and v(ind, "strain.t_prod_h") == 83
    assert v(sc.scenario_params("physical_limit", "lf"), "plant.annual_target_protein_t") == 1588
    assert v(sc.scenario_params("physical_limit", "blg"), "plant.annual_target_protein_t") == 100000
    acad = sc.scenario_params("academic", "lf")
    assert v(acad, "strain.titer_g_L") == 2.8 and v(acad, "plant.spec") == "cex"


@pytest.mark.parametrize("name", ["academic", "industry"])
@pytest.mark.parametrize("prod", sc.PRODUCTS)
def test_monte_carlo_config_samples(name, prod):
    """Every product's Monte Carlo paths have ranges that contain the scenario's value."""
    paths, ranges = sc.mc_config(name, prod)
    p = params.override(sc.scenario_params(name, prod), {k: dict(x) for k, x in ranges.items()})
    params.sample(p, np.random.default_rng(0), paths)


def test_lactoferrin_scenarios_feasible():
    for name in ("academic", "industry"):
        assert sc.is_feasible(sc.run(name, "lf"))
    assert sc.is_feasible(plant.evaluate(sc.base_params("lf")))


@pytest.mark.parametrize("prod", sc.PRODUCTS)
def test_unused_paths_do_not_enter_the_plant(prod):
    """Every ranged leaf the tornado skips as off-route leaves the product's MSP unchanged."""
    p = sc.base_params(prod)
    base = plant.evaluate(p).msp_ccf
    skipped = [x for x in params.ranged_leaves(p) if x.startswith(sc.unused_paths(p))]
    assert skipped                                   # each product has off-route leaves
    for x in skipped:
        hi = params.bounds(p, x)[1]
        assert plant.evaluate(params.override(p, {x: hi})).msp_ccf == pytest.approx(base, rel=1e-12), x


def test_products_come_from_products_yaml():
    import yaml
    keys = tuple(yaml.safe_load((sc.ROOT / "data/pf/products.yaml").read_text()))
    assert sc.PRODUCTS == keys and {"blg", "ova", "lf"} <= set(keys)
    for k in keys:                                  # each product has a product file and a dryer-feed leaf
        assert (sc.ROOT / f"data/products/{k}.yaml").exists()
        v(sc.base_params(k), f"dsp.dryer_feed_solids_{k}")


# ---------------------------------------------------------------- casein: isoelectric precipitation ('acid')
def test_casein_formula_from_uniprot():
    """Mature P02666 A2 (209 aa, no Cys): C1080 H1692 N268 O310 S6, 23,583 Da unphosphorylated (casein.yaml)."""
    p = pr.protein("cas")
    assert p.residues == 209
    assert {k: round(x) for k, x in p.formula.items()} == {"C": 1080, "H": 1692, "N": 268, "O": 310, "S": 6}
    assert p.mw_molecule == pytest.approx(23583, abs=1)


@pytest.fixture(scope="module")
def cas():
    p = sc.base_params("cas")
    return p, plant.evaluate(p)


def test_acid_route_recovery_and_concentration(cas):
    """The permeate is ultrafiltered (no diafiltration) to skim milk's casein concentration, then precipitated:
    recovery = cell removal x MF x UF retention CF^-(1-sigma) x precipitation x dryer, and the precipitation
    feed holds the casein that entered UF at the target concentration (audit R9-1)."""
    p, r = cas
    d = r.design
    sigma = v(p, "dsp.uf_rejection")
    expect = (d["recovery_cell_removal"] * v(p, "dsp.mf_recovery") * d["CF"] ** -(1 - sigma)
              * v(p, "dsp.acid_precip_recovery") * v(p, "dsp.dryer_recovery"))
    assert d["recovery"] == pytest.approx(expect, rel=1e-12)
    P_uf = d["product_made_kg"] * d["recovery_cell_removal"] * v(p, "dsp.mf_recovery")
    assert d["whey_m3_batch"] == pytest.approx(P_uf / v(p, "dsp.acid_precip_feed_g_L"), rel=1e-12)
    assert d["CF"] > 1 and d["uf_m2"] > 0 and d["mf_m2"] > 0
    assert d["dryer_inlet_solids"] == v(p, "dsp.dryer_feed_solids_cas")
    assert sc.is_feasible(r) and v(p, "plant.spec") == "acid"


def test_acid_route_streams(cas):
    """Acid and whey scale with the permeate volume; wash water and NaOH with the casein; the heater's
    steam is the permeate's sensible heat net of regeneration; redissolving water takes the curd to the
    dryer-feed solids."""
    p, r = cas
    d = r.design
    V = d["whey_m3_batch"]
    solids = d["target_per_batch_kg"] / v(p, "dsp.dryer_recovery") / d["purity_dry"]   # casein solids before the dryer
    assert d["acid_kg_batch"] == pytest.approx(v(p, "dsp.acid_h3po4_kg_per_m3") * V, rel=1e-12)
    assert d["wash_m3_batch"] == pytest.approx(v(p, "dsp.acid_wash_L_per_kg") * solids / 1000, rel=1e-12)
    assert d["naoh_kg_batch"] == pytest.approx(v(p, "dsp.acid_naoh_kg_per_kg") * solids, rel=1e-12)
    dT = v(p, "dsp.acid_precip_temperature_C") - v(p, "hosts.kphaffii.temperature_C")
    assert d["acid_steam_kg_batch"] == pytest.approx(V * 1000 * 4.1868 * dT / 2410 * (1 - v(p, "dsp.acid_heat_recovery")),
                                                     rel=1e-12)
    assert d["dissolve_m3_batch"] == pytest.approx(
        solids / 1000 * (1 / v(p, "dsp.dryer_feed_solids_cas") - 1 / v(p, "dsp.acid_curd_solids")), rel=1e-12)
    # doubling the acid dose adds exactly its cost to the DSP chemicals line
    r2 = plant.evaluate(params.override(p, {"dsp.acid_h3po4_kg_per_m3": 2 * v(p, "dsp.acid_h3po4_kg_per_m3")}))
    extra = d["n_batches"] * d["acid_kg_batch"] * v(p, "media.h3po4_price_usd_kg")
    assert r2.annual["DSP chemicals"] - r.annual["DSP chemicals"] == pytest.approx(extra, rel=1e-9)


def test_casein_scenarios():
    """Casein runs the base design point on its own route; the Eden Brew variant is a low-purity UF/DF concentrate."""
    assert v(sc.scenario_params("academic", "cas"), "strain.titer_g_L") == 1.0
    assert v(sc.scenario_params("academic", "cas", variant="cas_patent"), "strain.titer_g_L") == 3.0
    assert v(sc.scenario_params("industry", "cas"), "plant.spec") == "acid"
    eb = sc.run("casein", "cas", variant="cas_ufdf_edenbrew")
    assert eb.design["purity_dry"] == pytest.approx(0.058) and eb.design["uf_m2"] > 0
    for name in ("academic", "industry"):
        assert sc.is_feasible(sc.run(name, "cas"))


# ---------------------------------------------------------------- ovomucoid (UF/DF concentrate as EVERY's GRN 967)
def test_ovomucoid_formula_from_uniprot():
    """Mature P01005 (186 aa, 9 disulfides): C840 H1306 N240 O292 S20, 20,080 Da (ovomucoid.yaml)."""
    p = pr.protein("ovd")
    assert p.residues == 186
    assert {k: round(x) for k, x in p.formula.items()} == {"C": 840, "H": 1306, "N": 240, "O": 292, "S": 20}
    assert p.mw_molecule == pytest.approx(20080, abs=1)


def test_ovomucoid_base_case():
    """Ovomucoid runs base.yaml's design point on the membrane route with its own dossier purity; the egg
    incumbent and the egg equivalent serve OVA and ovomucoid alike."""
    from pftea import benchmarks as bm
    p = sc.base_params("ovd")
    assert (v(p, "plant.spec"), v(p, "strain.titer_g_L")) == ("concentrate", v(BASE, "strain.titer_g_L"))
    assert v(p, "dsp.concentrate_target_frac_dry") == pytest.approx(0.76)
    r = plant.evaluate(p)
    assert sc.is_feasible(r) and r.design["purity_dry"] == pytest.approx(0.76)
    assert "ovd" in bm.incumbents()["egg"]["compare_to"] and "ova" in bm.incumbents()["egg"]["compare_to"]
    assert bm.equivalents()["egg"]["target_g"]["ovd"] == pytest.approx(0.40)
    for name in ("academic", "industry"):
        assert sc.is_feasible(sc.run(name, "ovd"))


# ---------------------------------------------------------------- v4: methanol, vessel sizing, rank correlations
@pytest.mark.parametrize("f", [0.0, 0.5, 1.0])
def test_methanol_blend_conserves_carbon_and_electrons(f):
    """Production-phase rates on a glucose/methanol blend (review G1) close the carbon and the
    electron (degree-of-reduction) balances: substrates in = cells + product + CO2 (+ O2 for
    electrons), whatever the methanol fraction."""
    p = params.override(BASE, {"plant.product": "blg"})
    host = plant._host(p)
    strain = pf.Strain(product=pr.protein("blg"), Y_ps=v(p, "strain.Y_ps_g_g"), X_prod=100, mu_prod=0.002,
                       t_prod=72, meoh_frac=f, Y_ps_meoh=plant.methanol_yield(p))
    F, mu, qp = 1000.0, 0.002, 0.004
    r, _ = pf._rates(host, strain, mu, qp, F, prod=True)
    bio, prot = host.growth.bio, strain.product.species
    made = {"bio": mu * F / bio.mw, "prot": qp * F / prot.mw}                  # kmol C-mol/h
    sp = {n: th.get(n) for n in r}
    carbon = sum(r[n] * sp[n].C for n in r) + made["bio"] * bio.C + made["prot"] * prot.C
    electrons = sum(r[n] * sp[n].gamma for n in r) + made["bio"] * bio.gamma + made["prot"] * prot.gamma   # O2: gamma -4
    scale = -r[pf.GLC] * 6 - r[pf.MEOH]
    assert abs(carbon) < 1e-9 * scale
    assert abs(electrons) < 1e-6 * scale * 4
    assert (r[pf.MEOH] < 0) == (f > 0) and (r[pf.GLC] < 0) == (f < 1)


def test_methanol_fraction_zero_is_the_glucose_model(blg):
    p, r = blg
    r0 = plant.evaluate(params.override(p, {"strain.methanol_frac_prod": 0.0}))
    r1 = plant.evaluate(params.override(p, {"strain.methanol_frac_prod": 1.0}))
    assert r0.msp_ccf == pytest.approx(r.msp_ccf, rel=1e-12) and r0.physical["methanol_kg"] == 0
    # methanol replaces production-phase glucose and costs more O2 per kg (C1 carbon, alcohol oxidase)
    assert r1.physical["methanol_kg"] > 0 and r1.physical["glucose_kg"] < r.physical["glucose_kg"]
    assert r1.physical["o2_kg"] > r.physical["o2_kg"]


def test_vessel_sizing_cheapest_up_to_cap():
    """size_fermenter (review G2): commodity plants keep the 200 m3 cap; the 250 t/yr lactoferrin
    plant sizes down and is cheaper than in 200 m3 vessels; fixed sizing leaves the vessel alone."""
    assert v(sc.base_params("blg"), "fermenter.volume_m3") == 200
    p = sc.base_params("lf")
    assert v(p, "fermenter.volume_m3") < 200
    fixed = sc.base_params("lf", {"fermenter.sizing": "fixed"})
    assert v(fixed, "fermenter.volume_m3") == 200
    assert plant.evaluate(p).msp_ccf < plant.evaluate(fixed).msp_ccf


def test_monte_carlo_rank_correlation_sign():
    """Spearman rho (review G4): higher titer lowers cost, so its rho is strongly negative."""
    p = sc.base_params("blg")
    mc = sc.monte_carlo(p, ["strain.titer_g_L", "utilities.glucose_usd_kg"], n=40, seed=3)
    assert mc["rank_corr"]["strain.titer_g_L"] < -0.8
    assert mc["rank_corr"]["utilities.glucose_usd_kg"] > 0


def test_methanol_anabolism_fixes_no_co2():
    """Methanol is more reduced than biomass: all cell and product carbon comes from it, the surplus
    electrons go to O2 (Heijnen), and no CO2 is fixed; the carbon cap on the protein yield is then
    M_protein,C-mol / M_methanol (~0.70 g/g). Glucose anabolism is unchanged (releases CO2)."""
    meoh, glc = th.get("Methanol"), th.get("Glucose (s)")
    a = th.anabolic(th.biomass(), meoh)
    assert a.of("CO2 (aq)") == 0 and a.of("O2 (aq)") < 0 and a.of("Methanol") == pytest.approx(-1.0)
    assert th.anabolic(th.biomass(), glc).of("CO2 (aq)") > 0
    prot = pr.protein("blg")
    assert pr.electron_ceiling(prot, meoh) == pytest.approx(prot.species.mw / meoh.mw, rel=1e-9)
    p = params.override(BASE, {"plant.product": "blg"})
    assert plant.methanol_yield(p) < plant.energetic_ceiling(p, "Methanol") < pr.electron_ceiling(prot, meoh)


# ---------------------------------------------------------------- alpha-lactalbumin, rennet-cheese casein, heme
@pytest.mark.parametrize("key, n, formula, mw", [
    ("alac", 123, {"C": 626, "H": 958, "N": 162, "O": 196, "S": 9}, 14178),     # P00711 20-142, 4 disulfides (alac.yaml)
    ("cas1", 199, {"C": 1035, "H": 1587, "N": 265, "O": 317, "S": 5}, 22975),   # P02662 16-214, unphosphorylated (casein.yaml)
    ("kap", 169, {"C": 849, "H": 1321, "N": 223, "O": 262, "S": 4}, 18972),     # P02668 22-190, 1 disulfide
    ("legh", 144, {"C": 702, "H": 1096, "N": 176, "O": 212, "S": 0}, 15394),    # P02236 2-145, globin without heme
    ("tf", 679, {"C": 3306, "H": 5096, "N": 912, "O": 1002, "S": 47}, 75157)])  # P02787 20-698, 19 disulfides; 75,156 in transferrin.yaml (derived, rounded)
def test_new_protein_formulas_from_uniprot(key, n, formula, mw):
    """Mature-chain formulas cross-checked against UniProt's molWeight in the evidence files."""
    p = pr.protein(key)
    assert p.residues == n
    assert {k: round(x) for k, x in p.formula.items()} == formula
    assert p.mw_molecule == pytest.approx(mw, abs=1)


def test_alac_base_case():
    """Alpha-lac runs BLG's membrane route at its isolate purity on a 1 kt/yr plant, and is feasible."""
    p = sc.base_params("alac")
    assert (v(p, "plant.spec"), v(p, "plant.annual_target_protein_t")) == ("concentrate", 1000)
    assert v(p, "dsp.concentrate_target_frac_dry") == 0.90
    assert sc.is_feasible(plant.evaluate(p))


def test_off_list_products_take_their_route_from_the_scenario_file():
    """Alpha-s1, kappa and LegH are not main products; their scenario blocks set the route and spec."""
    assert not {"cas1", "kap", "legh"} & set(sc.PRODUCTS)
    assert v(sc.scenario_params("cheese", "kap"), "plant.spec") == "acid"
    assert v(sc.scenario_params("cheese", "kap"), "dsp.acid_precip_recovery") == 0.78
    h = sc.scenario_params("heme", "legh", variant="legh_chen2025")
    assert (v(h, "plant.spec"), v(h, "dsp.concentrate_target_frac_dry"), v(h, "strain.titer_g_L")) == ("concentrate", 0.43, 3.86)


def test_blend_titer_needed():
    """c_blend <= 1.1 c_base  <=>  c(T) <= c_base (1 + 0.1/s); on c = 100/T with c_base 10 and s = 0.2, c(T) <= 15 at T = 6.67."""
    ts = [1, 2, 5, 10, 20]
    assert sc.blend_titer_needed(ts, [100 / t for t in ts], 10.0, 0.2) == pytest.approx(100 / 15, rel=1e-9)
    assert sc.blend_titer_needed(ts, [100 / t for t in ts], 1.0, 0.2) is None          # threshold off the grid
    with pytest.raises(ValueError):
        sc.blend_titer_needed(ts, [5, 4, 6, 3, 2], 10.0, 0.2)                          # cost must fall with titer


def test_unused_paths_keep_a_products_own_dryer_leaf():
    """cas's dryer leaf is a prefix of cas1's: cas1 must not skip its own (audit R14-L4)."""
    p = sc.scenario_params("cheese", "cas1")
    assert not any("dsp.dryer_feed_solids_cas1".startswith(u) for u in sc.unused_paths(p))


# ---------------------------------------------------------------- metabolic floor
@pytest.mark.parametrize("prod", ["blg", "alb"])
def test_metabolic_floor_balances(prod):
    """At the ceiling: substrate = 1/Y*, and electrons close: 24 per glucose = gamma_p per C-mol of protein + 4 per O2
    (NH3 as the N source, Roels' convention)."""
    from pftea import floor
    p = sc.base_params(prod)
    f = floor.metabolic_floor(p)
    assert f["substrate_kg"] == pytest.approx(1 / f["yield_g_g"], rel=1e-9)
    prot = pr.protein(prod)
    n = 1000 / prot.species.mw
    glc_mol = f["substrate_kg"] * 1000 / th.get("Glucose (s)").mw
    assert 24 * glc_mol == pytest.approx(prot.species.gamma * n + 4 * f["o2_mol"], rel=1e-6)
    assert f["p_max_kg_m3_h"] == min(f["p_max_o2_kg_m3_h"], f["p_max_heat_kg_m3_h"])
    assert f["total"] == pytest.approx(sum(f["cost"].values()))


def test_feed_bills_identity():
    """Farm-gate cost = allocated feed bill / feed share; 'other' is the rest; the ranges bracket the central."""
    from pftea import benchmarks as bm
    for animal in bm.feed_bills().values():
        for d in animal["regions"].values():
            if d["share"] is None:
                assert d["total"] is None and d["other"] is None and d["feed"] > 0
                continue
            assert d["total"] == pytest.approx(d["feed"] / d["share"], rel=1e-12)
            assert d["other"] == pytest.approx(d["total"] - d["feed"], rel=1e-12)
            assert d["total_low"] <= d["total"] <= d["total_high"] and 0 < d["share"] <= 1 and 0 < d["alloc"] <= 1


# ---------------------------------------------------------------- transferrin and binder notes
def test_transferrin_runs_on_albumins_route():
    """The transferrin note keeps albumin's route and plant and changes only the product and its column data."""
    cfg = sc.load("transferrin")
    common = {k: (x["value"] if isinstance(x, dict) else x) for k, x in cfg["common"].items()}
    p = sc.base_params("alb", common)
    assert v(p, "plant.product") == "tf" and v(p, "plant.spec") == v(sc.base_params("alb"), "plant.spec")
    assert v(p, "dsp.cex_recovery") == pytest.approx(0.70) and v(p, "dsp.polish_columns") == 1
    assert pr.protein("tf").species.mw > 0 and len(pr.load("tf")["mature_sequence"]) == 679
    r = plant.evaluate(p)
    assert sc.is_feasible(r) and r.msp_ccf > 0


def test_binder_cost_in_use_identity():
    """Cost per kg of analogue = dose x price; protein binders at the product dose x its protein fraction."""
    b = sc.load("binder")
    mc, dose, frac = b["use"]["mc_frac"], b["use"]["egg_protein_product_frac"], b["use"]["protein_frac_of_product"]
    assert mc["low"] <= mc["value"] <= mc["high"] and dose["low"] <= dose["value"] <= dose["high"]
    assert 0 < frac["value"] <= 1 and 0 < b["price"]["mc_usd_kg"]["value"]
