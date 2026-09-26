"""Independent implementation of NREL 2011's DCF (App. B), written by the audit (R4).

It reproduces NREL's own ethanol worksheet (MESP $2.15/gal, including NREL's quirk of
discounting year 30 with the year-20 factor). Used only by tests to check finance.msp_dcf.
"""
MACRS7 = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]


def npv_nrel(sales, fci, var, fixed, *, irr=0.10, life=30, tax=0.35, wc_frac=0.05, debt=0.6, rate=0.08,
             n_loan=10, constr=(0.08, 0.60, 0.32)):
    """Equity NPV at irr. Years -2,-1,0 construction; 1..life operation; sales = full-year revenue."""
    ny = len(constr)
    v, bal = 0.0, 0.0
    for k, f in enumerate(constr):
        y = k - ny + 1
        bal += debt * fci * f
        out = (1 - debt) * fci * f + rate * bal
        if y == 0:
            out += wc_frac * fci
        v -= out * (1 + irr) ** (-y)
    loan = debt * fci
    pay = loan * rate / (1 - (1 + rate) ** -n_loan) if loan > 0 else 0.0
    lossf = 0.0
    for y in range(1, life + 1):
        interest = bal * rate if y <= n_loan else 0.0
        principal = pay - interest if y <= n_loan else 0.0
        bal -= principal
        rev, cost = (sales * 0.875, var * 0.9375 + fixed) if y == 1 else (sales, var + fixed)
        dep = fci * (MACRS7[y - 1] if y - 1 < len(MACRS7) else 0.0)
        taxable = rev - cost - dep - interest + lossf
        lossf, t = (taxable, 0.0) if taxable < 0 else (0.0, tax * taxable)
        cash = rev - cost - t - (interest + principal if y <= n_loan else 0.0)
        if y == life:
            cash += wc_frac * fci
        v += cash * (1 + irr) ** -y
    return v
