"""From capital and operating costs to $/kg: cost of production and minimum selling prices.

Capital charge (Humbird 2021, eq. 3.2):
    CCF = i / (1 - (1 + i)^-n)
    MSP_CCF = (operating cost + CCF x TCI) / annual output
    where operating cost already includes maintenance and insurance (fractions of TCI).

Discounted cash flow (NREL 2011, App. B and Table 33):
    Construction years -2, -1, 0 spend 8/60/32% of FCI. Working capital (fraction of FCI) is
    spent at year 0 and recovered in the last year. With debt (NREL: 60% at 8%, 10 years),
    the loan is drawn in step with construction spending and the interest on the drawn
    balance is paid by equity during construction (NREL p.65); from year 1 the loan is
    repaid as an annuity and interest is tax-deductible.
    In the first operating year, 3 months of start-up give revenue at 50%, variable cost at
    75% and fixed cost at 100%. Taxable income = revenue - costs - MACRS depreciation of FCI
    (7-year, half-year convention) - interest; tax = rate x taxable income, with losses
    carried forward. MSP_DCF is the price at which the equity NPV at the target IRR is zero.
    (NREL's own worksheet discounts year 30 with the year-20 factor; we do not copy that.)

Voutilainen-style DCF (Voutilainen et al. 2021 SI 'DCF'; data/calibration/voutilainen2021.yaml),
used only for that calibration anchor:
    sum_{t=0..n} (1 - tax) (revenue_t - opex_t) / (1 + r)^t = k_cap x FCI
    t = 0 is a start-up year (revenue and variable cost at their start-up fractions, fixed cost
    100%); from t = 1 the price inflates at `inflation` per year and operating cost escalates
    at `opex_growth` per year; no depreciation, no working capital; capital k_cap x FCI at t = 0.

Cost of production (COP) = (operating cost + straight-line depreciation of FCI over n) / output.
"""
from __future__ import annotations

MACRS7 = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]   # IRS table A-1, NREL App. B
CONSTRUCTION = [0.08, 0.60, 0.32]                                          # NREL 2011 Table 33


def ccf(i: float, n: int) -> float:
    return i / (1 - (1 + i) ** -n)


def _solve_price(npv, hi: float = 1.0) -> float:
    lo = 0.0
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


def msp_dcf(fci: float, var_cost: float, fixed_cost: float, output_kg: float, irr: float = 0.10,
            life: int = 30, tax: float = 0.21, wc_frac: float = 0.05,
            construction: list[float] = CONSTRUCTION, depreciation: list[float] = MACRS7,
            debt_frac: float = 0.0, loan_rate: float = 0.08, loan_years: int = 10) -> float:
    """Price [$/kg] at which the equity NPV at `irr` is zero. Costs are annual $ at full output."""
    ny = len(construction)
    loan = debt_frac * fci
    pay = loan * loan_rate / (1 - (1 + loan_rate) ** -loan_years) if loan > 0 else 0.0
    wc = wc_frac * fci

    def npv(price: float) -> float:
        v, drawn = 0.0, 0.0
        for k, frac in enumerate(construction):                   # years -ny+1 .. 0
            y = k - ny + 1
            drawn += loan * frac
            out = fci * (1 - debt_frac) * frac + loan_rate * drawn  # equity share + construction interest
            if y == 0:
                out += wc
            v -= out / (1 + irr) ** y
        loss_cf, balance = 0.0, drawn
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

    return _solve_price(npv)


def msp_dcf_voutilainen(fci: float, var_cost: float, fixed_cost: float, output_kg: float, rate: float,
                        life: int, tax: float, capital_factor: float, inflation: float, opex_growth: float,
                        startup_revenue: float, startup_variable: float, byproduct: float = 0.0) -> float:
    """Price [per kg, same currency as the costs] that closes Voutilainen's DCF identity."""
    def npv(price: float) -> float:
        s = 0.0
        for t in range(0, life + 1):
            if t == 0:
                rev = startup_revenue * (price * output_kg + byproduct)
                opex = startup_variable * var_cost + fixed_cost
            else:
                rev = price * output_kg * (1 + inflation) ** (t - 1) + byproduct
                opex = (var_cost + fixed_cost) * (1 + opex_growth) ** (t - 1)
            s += (1 - tax) * (rev - opex) / (1 + rate) ** t
        return s - capital_factor * fci

    return _solve_price(npv)
