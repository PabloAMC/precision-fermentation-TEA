"""Calibration anchor 1, software check: our port reproduces Humbird's baker's-yeast sheet.

Reference values are cached cells of Humbird (2021) SI sheet A.1, extracted by
scripts/extract_humbird_si.py into tests/fixtures/humbird_A1.json.
"""
import json
from pathlib import Path

import pytest

from pftea import humbird_yeast as hy
from pftea import thermo as th

FX = json.loads((Path(__file__).parent / "fixtures/humbird_A1.json").read_text())["cells"]


@pytest.fixture(scope="module")
def result():
    return hy.run()


def test_growth_stoichiometry_exact():
    m = th.GrowthModel(th.biomass(), th.get("Glucose (s)"), 30.0)
    assert m.growth.of("Glucose (s)") == pytest.approx(FX["A31"], rel=1e-12)
    assert m.growth.of("O2 (aq)") == pytest.approx(FX["A32"], rel=1e-12)
    assert m.dissipation == pytest.approx(FX["D26"], rel=1e-12)
    assert m.maint_extent == pytest.approx(FX["F70"], rel=1e-12)
    for e in ("C", "H", "O", "N"):
        assert abs(m.growth.residual(e)) < 1e-12


@pytest.mark.parametrize("ours,cell,tol", [
    (lambda r: r["sim"]["glc_kg"], "H282", 0.002),
    (lambda r: r["sim"]["comp_kWh"], "BD282", 0.002),
    (lambda r: r["sim"]["refr_kWh"], "BF282", 0.002),
    (lambda r: r["sim"]["F_end"], "J97", 0.002),
    (lambda r: r["annual_t"], "H102", 0.002),
    (lambda r: r["tci"], "I174", 0.001),
    (lambda r: r["per_kg"]["carbon"], "G261", 0.002),
    (lambda r: r["per_kg"]["electricity"], "G264", 0.002),
    (lambda r: r["fixed"]["labour"], "G268", 0.002),
    (lambda r: r["capital_per_kg"], "G272", 0.002),
    (lambda r: r["fte"], "G245", 1e-9),
])
def test_intermediates(result, ours, cell, tol):
    assert ours(result) == pytest.approx(FX[cell], rel=tol)


def test_cost_of_production(result):
    """Software check: COP within 0.1% of Humbird's $1.89/kg dry (2018$)."""
    assert result["cop"] == pytest.approx(FX["G274"], rel=1e-3)


def test_reality_check(result):
    """Reality check: within 25% of the ~$1.90/kg implied by baker's-yeast market prices."""
    implied = hy.load_case()["market_implied_cost_usd_kg"]["value"]
    assert abs(result["cop"] / implied - 1) < 0.25
