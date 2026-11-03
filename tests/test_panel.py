"""The model panel's data: the cost ledger (plant.py block 8), the chain record (chain.py) and the
identities the panel's checks rely on."""
import math

import pytest

from pftea import chain, finance, params, plant
from pftea import scenarios as sc


@pytest.fixture(scope="module")
def blg():
    p = sc.base_params("blg")
    return p, plant.evaluate(p)


@pytest.fixture(scope="module")
def blg_rec(blg):
    return chain.record(*blg)


def _ledger_closes(r):
    for line, total in r.annual.items():
        terms = sum(t["amount"] * t["price"] for t in r.ledger if t["line"] == line)
        assert terms == pytest.approx(total, rel=1e-12, abs=1e-6), line
    assert sum(r.per_kg.values()) == pytest.approx(r.msp_ccf, rel=1e-12)


@pytest.mark.parametrize("case", ["cex", "acid", "isolate", "nrel", "crude", "methanol"])
def test_ledger_reproduces_every_cost_line(case, blg):
    p = {"cex": lambda: sc.base_params("lf"), "acid": lambda: sc.base_params("cas"),
         "isolate": lambda: params.override(blg[0], {"plant.spec": "isolate"}),
         "nrel": lambda: params.override(blg[0], sc.LIGHT),
         "crude": lambda: params.override(blg[0], {"plant.spec": "crude"}),
         "methanol": lambda: sc.scenario_params("academic", "lf", variant="lf_lv2023")}[case]()
    _ledger_closes(plant.evaluate(p))


def test_ledger_base(blg):
    _ledger_closes(blg[1])


def test_recovery_steps_multiply_to_total(blg):
    d = blg[1].design
    assert math.prod(d["recovery_steps"].values()) == pytest.approx(d["recovery"], rel=1e-12)
    d = plant.evaluate(sc.base_params("alb")).design            # capture + polish columns
    assert "polish column" in d["recovery_steps"]
    assert math.prod(d["recovery_steps"].values()) == pytest.approx(d["recovery"], rel=1e-12)


def test_chain_identities(blg, blg_rec):
    """The eleven steps of chain.py's docstring hold on the model's own numbers."""
    p, r = blg
    c = blg_rec["chain"]
    rel = 1e-5                                                  # the record keeps 6 significant digits
    assert c["P"] == pytest.approx(c["titer"] * c["W_end"], rel=rel)
    assert c["S"] == pytest.approx(c["P"] * c["R"], rel=rel)
    assert c["cycle"] == pytest.approx(c["t_growth"] + c["t_prod"] + c["t_turn"], rel=rel)
    assert c["n"] == pytest.approx(c["A"] / c["S"], rel=rel)
    assert c["N"] == pytest.approx(c["n"] * c["cycle"] / c["H"], rel=rel)
    assert c["N_bought"] == math.ceil(c["N"])
    assert c["C_ferm"] == pytest.approx(c["N_bought"] * c["unit_cost"], rel=rel)
    assert c["tci"] == pytest.approx(sum(r.capex.values()), rel=rel)
    plant_kg = r.per_kg["capital charge"] + r.per_kg["maintenance"] + r.per_kg["insurance"]
    assert c["tci"] * (c["ccf"] + c["f_maint"] + c["f_ins"]) / c["A"] == pytest.approx(plant_kg, rel=rel)
    assert c["glucose_per_kg"] * c["glucose_price"] == pytest.approx(r.per_kg["glucose"], rel=rel)
    rate, life = c["ccf_rate"], c["ccf_life"]
    assert rate * (1 + rate) ** life / ((1 + rate) ** life - 1) == pytest.approx(c["ccf"], rel=rel)
    assert c["ccf"] == pytest.approx(finance.ccf(rate, life), rel=rel)


def test_location_switch_is_price_arithmetic(blg):
    """The panel's location switch: same plant, EU prices, TCI scaled by the location factor."""
    p, r = blg
    q = params.override(p, {"plant.location": "eu_nw"})          # vessel already sized: same design
    e = plant.evaluate(q)
    A = params.v(p, "plant.annual_target_protein_t") * 1000
    f, f_eu = r.design["location_factor"], e.design["location_factor"]
    tci_eu = (r.tci - r.design["resin_fill"]) * f_eu / f + r.design["resin_fill"]
    assert tci_eu == pytest.approx(e.tci, rel=1e-9)
    price_eu = {t["path"]: t["price"] for t in e.ledger}
    total = 0.0
    for t in r.ledger:
        amount = tci_eu if t["unit"] == "$" else t["amount"]
        total += amount * price_eu[t["path"]]
    assert total / A == pytest.approx(e.msp_ccf, rel=1e-9)


def test_sugar_uses_close_to_simulator_total(blg_rec):
    s = blg_rec["sugar"]
    assert sum(s["uses"].values()) == pytest.approx(s["total"], rel=0.02)
    assert abs(s["carbon_gap"]) < 0.005


def test_limits_base_within_and_infeasible_flagged(blg, blg_rec):
    for x in blg_rec["limits"]:
        if x["kind"] == "max":
            assert x["value"] <= x["limit"] * 1.001, x
        elif x["kind"] == "min":
            assert x["value"] >= x["limit"] * 0.999, x
    q = params.override(blg[0], {"strain.titer_g_L": 100, "strain.t_prod_h": 24})
    r = plant.evaluate(q)
    assert not sc.is_feasible(r)
    o2 = {x["key"]: x for x in chain.limits(q, r)}["o2"]
    assert o2["value"] > 1.0 or any("reachable" in f or "initial fill" in f for f in r.flags)


def test_panel_data_compact_round_trip(blg, blg_rec):
    """scripts/panel_data.py stores a run as arrays aligned with a schema; the panel rebuilds the price from
    them as sum(amount x price), with the plant lines from TCI per kg."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("panel_data", Path(__file__).parents[1] / "scripts/panel_data.py")
    pd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pd)
    rec = {**blg_rec, "feasible": True}
    s = pd.schema([rec])
    row = pd.compact(rec, s)
    assert row[2] == blg_rec["msp"]
    total = sum(a * t["price"] for a, t in zip(row[4], s["terms"]))
    assert total == pytest.approx(blg[1].msp_ccf, rel=1e-4)
    chain_row = dict(zip(s["chain"], row[6]))
    assert chain_row["tci"] == pytest.approx(blg[1].tci, rel=1e-5)
    assert pd.compact(dict(ok=False, flags=["x"], msp=None, error=True), s)[4] is None
