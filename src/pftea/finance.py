"""From capital and operating costs to $/kg: cost of production and minimum selling prices.

Capital charge (Humbird 2021, eq. 3.2):
    CCF = i / (1 - (1 + i)^-n)
    MSP_CCF = (operating cost + CCF x TCI) / annual output
    where operating cost already includes maintenance and insurance (fractions of TCI).
Discounted cash flow (NREL 2011, Table 33, simplified to an unlevered project):
    Capital is spent over the construction years (8/60/32%), and working capital
    (fraction of FCI) at start-up. Revenue = price x output. In the first operating year,
    3 months of start-up give revenue at 50%, variable cost at 75% and fixed cost at 100%.
    Taxable income = revenue - costs - MACRS depreciation of FCI (7-year, half-year
    convention); tax = rate x taxable income (losses carried forward).
    MSP_DCF is the price that makes NPV at the target IRR zero. Working capital is
    recovered in the last year.
Cost of production (COP) = (operating cost + straight-line depreciation of FCI over n) / output.
"""
from __future__ import annotations

MACRS7 = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]
CONSTRUCTION = [0.08, 0.60, 0.32]


def ccf(i: float, n: int) -> float:
    return i / (1 - (1 + i) ** -n)


def msp_dcf(fci: float, var_cost: float, fixed_cost: float, output_kg: float, irr: float = 0.10,
            life: int = 30, tax: float = 0.21, wc_frac: float = 0.05,
            construction: list[float] = CONSTRUCTION, depreciation: list[float] = MACRS7,
            debt_frac: float = 0.0, loan_rate: float = 0.08, loan_years: int = 10) -> float:
    """Price [$/kg] at which the equity NPV at `irr` is zero. Costs are annual $ at full output.

    With debt_frac > 0 (NREL 2011: 60% debt, 8%, 10 years), that share of FCI is borrowed at
    start-up and repaid as an annuity; interest is tax-deductible; equity funds the rest.
    """
    ny = len(construction)
    loan = debt_frac * fci
    pay = loan * loan_rate / (1 - (1 + loan_rate) ** -loan_years) if loan > 0 else 0.0

    def npv(price: float) -> float:
        v = 0.0
        for k, frac in enumerate(construction):                   # years -ny+1 .. 0
            v -= fci * (1 - debt_frac) * frac / (1 + irr) ** (k - ny + 1)
        wc = wc_frac * fci
        v -= wc / (1 + irr) ** 1
        loss_cf, balance = 0.0, loan
        for y in range(1, life + 1):
            interest = balance * loan_rate if y <= loan_years else 0.0
            principal = (pay - interest) if y <= loan_years else 0.0
            balance -= principal
            if y == 1:
                rev = price * output_kg * (0.25 * 0.5 + 0.75)
                var = var_cost * (0.25 * 0.75 + 0.75)
            else:
                rev, var = price * output_kg, var_cost
            dep = fci * depreciation[y - 1] if y - 1 < len(depreciation) else 0.0
            ebt = rev - var - fixed_cost - dep - interest
            taxable = ebt + loss_cf
            if taxable < 0:
                loss_cf, t = taxable, 0.0
            else:
                loss_cf, t = 0.0, tax * taxable
            cash = rev - var - fixed_cost - t - (interest + principal)
            if y == life:
                cash += wc
            v += cash / (1 + irr) ** y
        return v

    lo, hi = 0.0, 1.0
    while npv(hi) < 0:
        hi *= 2
        if hi > 1e7:
            return float("inf")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if npv(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)
