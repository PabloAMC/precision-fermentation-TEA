"""Finance: capital charge, NREL-style DCF and the Voutilainen-style DCF (docs/AUDIT.md R4-5, R4-6)."""
import pytest

from pftea import finance as fin
from reference_nrel_dcf import npv_nrel


def test_capital_recovery_factor():
    assert fin.ccf(0.075, 10) == pytest.approx(0.14569, abs=1e-5)       # Humbird 2021: ~14.6%/yr


def test_macrs_table_sums_to_one():
    assert sum(fin.MACRS7) == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("debt", [0.0, 0.6])
def test_dcf_matches_independent_nrel_implementation(debt):
    """NREL App. B ethanol case, simplified (no steam-plant depreciation, no land, by-product netted)."""
    fci, var, fixed, gal = 160245385 / 0.4, 26693969 + 45201122 - 6565742, 10655826, 131425440 / 2.15
    ours = fin.msp_dcf(fci, var, fixed, gal, irr=0.10, life=30, tax=0.35, wc_frac=0.05,
                       debt_frac=debt, loan_rate=0.08, loan_years=10)
    lo, hi = 0.1, 10.0                                  # independent root find on the reference NPV
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if npv_nrel(mid * gal, fci, var, fixed, debt=debt) > 0:
            hi = mid
        else:
            lo = mid
    assert ours == pytest.approx(0.5 * (lo + hi), rel=1e-6)


def test_voutilainen_dcf_reproduces_their_price():
    """Their inputs (voutilainen2021.yaml): FCI 128.18 MEUR, variable 5.95, fixed 5.07, 2,508 t,
    by-product credit 0.336 MEUR/yr, opex 11.02 -> 13.10 over years 1-20; their MPSP is 9,007 EUR/t."""
    p = fin.msp_dcf_voutilainen(128.18e6, 5.95e6, 5.07e6, 2508e3, rate=0.05, life=20, tax=0.20,
                                capital_factor=1.03, inflation=0.01, opex_growth=(13.10 / 11.02) ** (1 / 19) - 1,
                                startup_revenue=0.5, startup_variable=0.5, byproduct=0.336e6)
    assert p * 1000 == pytest.approx(9007, rel=0.002)
