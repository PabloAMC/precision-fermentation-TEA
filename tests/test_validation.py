"""Reproduce published models. These tests are the model's licence to speak.

Fill the input dicts from the papers in Phase 2. Until then they xfail.
"""
import copy
import pytest
from pftea import params, pipeline

RAW = params.load()


def test_runs_at_base():
    r = pipeline.run(params.base(RAW))
    assert 1 < r["msp_usd_kg"] < 1000


def test_cost_falls_with_titer():
    p = params.base(RAW)
    lo = copy.deepcopy(p); lo["strain"]["titer_g_per_L"] = 5
    hi = copy.deepcopy(p); hi["strain"]["titer_g_per_L"] = 50
    assert pipeline.run(lo)["msp_usd_kg"] > pipeline.run(hi)["msp_usd_kg"]


@pytest.mark.xfail(reason="Phase 2: fill inputs from Voutilainen 2021 Table X")
def test_voutilainen_2021():
    p = params.base(RAW)
    # TODO set titer, volume, yield, purity, sugar price from the paper
    r = pipeline.run(p)
    assert abs(r["cop_usd_kg"] - 11.2) / 11.2 < 0.20


@pytest.mark.xfail(reason="Phase 2: fill inputs from Intelligen lactoferrin white paper")
def test_intelligen_lactoferrin():
    p = params.base(RAW)
    r = pipeline.run(p)
    assert abs(r["cop_usd_kg"] - 292) / 292 < 0.30
