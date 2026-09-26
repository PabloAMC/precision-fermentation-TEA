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
    p, r = blg
    n = r.design["N_prod_int"]
    assert n == math.ceil(r.design["N_prod"] - 1e-9)
    per = plant.eq.fermenter(v(p, "fermenter.volume_m3"), v(p, "capital.fermenter_exponent_above_table"))
    idx = v(p, "capital.cost_index_2018_to_2025") * v(p, "capital.location_factor")
    assert r.capex["ISBL: production fermenters"] == pytest.approx(per * n * idx, rel=1e-12)


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
    p = sc.scenario_params("lactoferrin", "lf")
    r1 = plant.evaluate(p)
    r2 = plant.evaluate(params.override(p, {"dsp.cex_cycle_h": 7.0}))
    for k in ("chromatography resin", "DSP chemicals", "water & wastewater"):
        assert r2.annual[k] == pytest.approx(r1.annual[k], rel=1e-9)
    assert r2.design["resin_m3"] == pytest.approx(2 * r1.design["resin_m3"], rel=1e-9)
    assert r2.tci > r1.tci


def test_cex_recovery_in_total(blg):
    p = sc.scenario_params("lactoferrin", "lf")
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
    assert e["egg"]["target_g"] == pytest.approx(1.96)
