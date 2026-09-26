"""Calibration anchors 2-4 (docs/VALIDATION.md). Structure frozen; anchors change inputs only.

Mass and energy balances must agree with each anchor. Total costs agree only under the
anchor's own (light) capital convention; with the base (Humbird) convention the recorded
misses are asserted to stay inside their documented bands, so a change that silently moves
them fails the suite and forces an update of VALIDATION.md.

Recorded 2026-09-26 after the sourced prices, cost index (CEPCI family) and DSP evidence.
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
    """Base convention: +174% recorded; must stay within +140%..+210%."""
    assert 1.40 < rel(nrel["usd_per_kg_protein (DCF, NREL financing)"]) < 2.10


def test_nrel_cost_light_convention():
    """NREL's own capital convention: +43% recorded; band +20%..+65%."""
    o = cal.run("nrel2011_cellulase", cal.LIGHT)["compare"]
    assert 0.20 < rel(o["usd_per_kg_protein (DCF, NREL financing)"]) < 0.65


def test_intelligen_total_within_30pct(intelligen):
    assert abs(rel(intelligen["usd_per_kg_powder (Humbird convention)"])) < 0.30


def test_intelligen_capital_documented(intelligen):
    """Our capital is higher (Humbird factors vs Lang 4): recorded +60%, band +40..+80%."""
    assert 0.40 < rel(intelligen["TCI_usd"]) < 0.80


def test_voutilainen_sugar(vout):
    assert abs(rel(vout["sugar_kg_per_kg_protein"])) < 0.10


def test_voutilainen_cost_documented_miss(vout):
    """Base convention: +182% recorded; band +150..+215%."""
    assert 1.50 < rel(vout["EUR_per_t_protein (their DCF)"]) < 2.15


def test_voutilainen_cost_light_convention():
    """Their fixed costs + NREL-style capital: +37% recorded; band +15..+60%."""
    o = cal.run("voutilainen2021_case", cal.voutilainen_conventions("nrel"))["compare"]
    assert 0.15 < rel(o["EUR_per_t_protein (their DCF)"]) < 0.60
