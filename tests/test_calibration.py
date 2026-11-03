"""Calibration anchors 2-4 (docs/VALIDATION.md). Structure frozen; anchors change inputs only.

These are consistency checks, not fits (audit R7-M6): the mass balances should agree; costs are
recorded misses. Each recorded value is asserted within +/-5 points, so any change that moves
an anchor fails the suite and forces an update of VALIDATION.md (the v1 bands were wide enough
to hide the R4-3/R4-5/R4-8 errors; audit R4-18).

Recorded 2026-09-26 after audit batch 2 (paste-model DSP, measured production-phase maintenance
with the Intelligen-derived product yield, NREL per-kg-produced basis and own prices,
Voutilainen's own DCF conventions). Re-recorded 2026-09-27 after the Phase F review: vendor-quote
fermenters in both conventions, 20% missing capital, O2 cap 200 per m3 of cell-free liquid,
coincident-peak utilities, CIP chemicals inside Humbird's maintenance (docs/VALIDATION.md).
Re-recorded again 2026-09-27 after the follow-up reading: textbook adiabatic compressor (Humbird's
workbook puts k where (k-1)/k belongs), inoculum and seed density from Intelligen's flowsheet (the
Voutilainen anchor pins its own 10% seed train), and the other v2.1 follow-up changes.
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
    """Price-anchored (Humbird) capital: +84.2% recorded (v2, aseptic-spec fermenters: +154.2%)."""
    assert rel(nrel["usd_per_kg_protein (DCF, NREL financing)"]) == pytest.approx(0.842, abs=0.05)


def test_nrel_cost_light_convention():
    """NREL's own (design-report) capital convention: +43.4% recorded (v2: +35.6%)."""
    o = cal.run("nrel2011_cellulase", cal.LIGHT)["compare"]
    assert rel(o["usd_per_kg_protein (DCF, NREL financing)"]) == pytest.approx(0.434, abs=0.05)


def test_nrel_electricity_documented(nrel):
    """-45.3% recorded (-40.0% with the workbook's compressor formula)."""
    assert rel(nrel["electricity_kWh_per_kg"]) == pytest.approx(-0.453, abs=0.05)


def test_intelligen_total_documented(intelligen):
    """Target already recast into the Humbird convention (A1 step 1.4): -3.5% recorded (v2: +13.7%)."""
    assert rel(intelligen["usd_per_kg_powder (Humbird convention)"]) == pytest.approx(-0.035, abs=0.05)


def test_intelligen_capital_documented(intelligen):
    """Our capital is higher (Humbird factors vs SuperPro's Lang factor 4): +24.3% recorded (v2: +59.9%)."""
    assert rel(intelligen["TCI_usd"]) == pytest.approx(0.243, abs=0.05)


def test_intelligen_glucose_documented(intelligen):
    """-18.9%: our growth yield (Heijnen, ~0.53 g/g effective) beats Intelligen's Eq. 1 (0.40 g/g)."""
    assert rel(intelligen["glucose_kg_per_kg_powder"]) == pytest.approx(-0.189, abs=0.05)


def test_voutilainen_sugar(vout):
    """Matched by construction (Y_ps solved to their sugar use; audit R7-M6)."""
    assert abs(rel(vout["sugar_kg_per_kg_protein"])) < 0.10


def test_voutilainen_cost_documented_miss(vout):
    """Price-anchored capital, their DCF conventions: +81.5% recorded (v2: +142.9%); our TCI is
    within 2% of their FCI, so the remaining gap is the fixed-cost rule and financing."""
    assert rel(vout["EUR_per_t_protein (their DCF)"]) == pytest.approx(0.815, abs=0.05)
    assert rel(vout["TCI vs their FCI (EUR)"]) == pytest.approx(0.018, abs=0.05)


def test_voutilainen_cost_light_convention():
    """Their fixed costs (maintenance 1.5% of FCI) + NREL-style capital: +26.8% recorded (v2: +23.2%)."""
    o = cal.run("voutilainen2021_case", cal.voutilainen_conventions("nrel"))["compare"]
    assert rel(o["EUR_per_t_protein (their DCF)"]) == pytest.approx(0.268, abs=0.05)


# --- Predictions of measured K. phaffii physiology (docs/VALIDATION.md, added 2026-11-03) ---
# Recorded, not tuned: each pin is the relative difference model/measurement - 1 (against the band's
# nearest edge for banded rows), +/- 0.05, so a change to the growth model shows up here.
@pytest.fixture(scope="module")
def physiology():
    return {r["key"]: r for r in cal.physiology_record()}


def _gap(r):
    if "band" in r:
        lo, hi = r["band"]
        return 0.0 if lo <= r["ours"] <= hi else (r["ours"] / (hi if r["ours"] > hi else lo) - 1)
    return r["ours"] / r["value"] - 1


@pytest.mark.parametrize("key,gap", [
    ("yxs_glucose", 0.0),        # inside the three chemostat values: pass
    ("heat_per_o2", 0.012),      # just above Cooney's 500 kJ/mol O2: near miss
    ("yxs_fedbatch", 0.014),     # just above Shemesh's best fed-batch strain: near miss
    ("yxs_methanol", 0.0),       # an input since 2026-11-03 (Heijnen gave +12%)
    ("qo2_methanol", -0.066),    # not fitted: -21% with Heijnen, -7% with the measured yield
    ("yxs_glycerol", -0.26),     # Heijnen on glycerol: far low (no case uses glycerol)
    ("qo2_glycerol", 1.03),      # and O2 uptake twice the measured
])
def test_physiology_record(physiology, key, gap):
    assert _gap(physiology[key]) == pytest.approx(gap, abs=0.05)


def test_blair_plant_check_recorded():
    """VALIDATION check 7: the base BLG plant's capital per m3 sits about 15% below the Blair band (recorded, not tuned)."""
    from pftea import benchmarks as bm
    from pftea import params, plant
    from pftea import scenarios as sc
    p = sc.base_params("blg")
    r = plant.evaluate(p)
    o = bm.plant_cost_check(r.tci, r.design["N_prod_int"] * params.v(p, "fermenter.volume_m3"), params.v(p, "plant.annual_target_protein_t"))
    lo = min(o["blair_scaled_per_m3"].values())
    assert o["model_per_m3"] / lo - 1 == pytest.approx(-0.153, abs=0.05)
