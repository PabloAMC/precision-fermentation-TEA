"""Cost of production and minimum selling price.

COP  = (OpEx + straight-line depreciation) / output          [USD/kg product]
MSP  = (OpEx + capital recovery) / output, where
       capital recovery = installed_capex * CRF(r, n),
       CRF = r (1+r)^n / ((1+r)^n - 1).
MSP is what an investor needs to charge to earn rate r. COP ignores return
on capital and is what most published TEMs report. Report both.
"""
from dataclasses import dataclass


def crf(r: float, n: int) -> float:
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


@dataclass
class EconResult:
    output_kg: float
    cop_usd_kg: float
    msp_usd_kg: float
    breakdown_usd_kg: dict


def run(p: dict, opex, installed_capex: float) -> EconResult:
    c = p["capex"]
    output_kg = p["plant"]["annual_output_t"] * 1000
    depreciation = installed_capex / c["lifetime_years"]
    recovery = installed_capex * crf(c["discount_rate"], c["lifetime_years"])
    cop = (opex.total + depreciation) / output_kg
    msp = (opex.total + recovery) / output_kg
    breakdown = {
        "sugar": opex.sugar / output_kg,
        "media_other": opex.media_other / output_kg,
        "utilities": opex.utilities / output_kg,
        "labour": opex.labour / output_kg,
        "maintenance+fixed": (opex.maintenance + opex.other_fixed) / output_kg,
        "capital": recovery / output_kg,
    }
    return EconResult(output_kg, cop, msp, breakdown)
