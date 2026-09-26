"""Calibration anchors 2-4 (docs/VALIDATION.md). Structure frozen; anchors change inputs only.

These are consistency checks, not fits (audit R7-M6): the mass balances should agree; costs are
recorded misses. Each recorded value is asserted within +/-5 points, so any change that moves
an anchor fails the suite and forces an update of VALIDATION.md (the v1 bands were wide enough
to hide the R4-3/R4-5/R4-8 errors; audit R4-18).

Recorded 2026-09-26 after audit batch 2 (paste-model DSP, measured production-phase maintenance
with the Intelligen-derived product yield, NREL per-kg-produced basis and own prices,
Voutilainen's own DCF conventions).
"""
import pytest

from pftea import calibration as cal


@pytest.fixture(scope="module")
def nrel():
    return cal.run("nrel2011_cellulase")["compare"]


@pytest.fixture(scope="module")
def intelligen():
    return cal.run("intelligen2025_ova")["compare"]


@pytest.fixture(scope="module")
def vout():
    return cal.run("voutilainen2021_case")["compare"]


def rel(pair):
    ours, theirs = pair
    return ours / theirs - 1


def test_nrel_mass_balance(nrel):
    assert abs(rel(nrel["glucose_kg_per_kg"])) < 0.10
    assert abs(rel(nrel["o2_mol_per_kg"])) < 0.10


def test_nrel_cost_documented_miss(nrel):
    """Price-anchored (Humbird) capital: +154.2% recorded."""
    assert rel(nrel["usd_per_kg_protein (DCF, NREL financing)"]) == pytest.approx(1.542, abs=0.05)


def test_nrel_cost_light_convention():
    """NREL's own (design-report) capital convention: +35.6% recorded."""
    o = cal.run("nrel2011_cellulase", cal.LIGHT)["compare"]
    assert rel(o["usd_per_kg_protein (DCF, NREL financing)"]) == pytest.approx(0.356, abs=0.05)


def test_nrel_electricity_documented(nrel):
    assert rel(nrel["electricity_kWh_per_kg"]) == pytest.approx(-0.400, abs=0.05)


def test_intelligen_total_documented(intelligen):
    """Target already recast into the Humbird convention (A1 step 1.4): +13.7% recorded."""
    assert rel(intelligen["usd_per_kg_powder (Humbird convention)"]) == pytest.approx(0.137, abs=0.05)


def test_intelligen_capital_documented(intelligen):
    """Our capital is higher (Humbird factors vs SuperPro's Lang factor): +59.9% recorded."""
    assert rel(intelligen["TCI_usd"]) == pytest.approx(0.599, abs=0.05)


def test_intelligen_glucose_documented(intelligen):
    """-19.1%: our growth yield (Heijnen, ~0.53 g/g effective) beats Intelligen's Eq. 1 (0.40 g/g)."""
    assert rel(intelligen["glucose_kg_per_kg_powder"]) == pytest.approx(-0.191, abs=0.05)


def test_voutilainen_sugar(vout):
    """Matched by construction (Y_ps solved to their sugar use; audit R7-M6)."""
    assert abs(rel(vout["sugar_kg_per_kg_protein"])) < 0.10


def test_voutilainen_cost_documented_miss(vout):
    """Price-anchored capital, their DCF conventions: +142.9% recorded."""
    assert rel(vout["EUR_per_t_protein (their DCF)"]) == pytest.approx(1.429, abs=0.05)


def test_voutilainen_cost_light_convention():
    """Their fixed costs (maintenance 1.5% of FCI) + NREL-style capital: +23.2% recorded."""
    o = cal.run("voutilainen2021_case", cal.voutilainen_conventions("nrel"))["compare"]
    assert rel(o["EUR_per_t_protein (their DCF)"]) == pytest.approx(0.232, abs=0.05)
