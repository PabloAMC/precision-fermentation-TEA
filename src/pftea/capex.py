"""Capital cost.

Purchased fermenter cost by the power law
  C = C_ref * (V / V_ref) ** n
DSP purchased cost = multiplier * fermentation purchased cost (placeholder).
Total installed capital = Lang factor * total purchased cost.
"""
from dataclasses import dataclass


@dataclass
class CapexResult:
    fermenters_purchased: float
    dsp_purchased: float
    total_purchased: float
    total_installed: float


def run(p: dict, n_fermenters: int) -> CapexResult:
    f = p["fermenter"]
    one = f["purchase_cost_ref_usd"] * (f["working_volume_m3"] / f["ref_volume_m3"]) ** f["scale_exponent"]
    ferm = n_fermenters * one
    dsp = p["downstream"]["dsp_capex_multiplier"] * ferm
    purchased = ferm + dsp
    return CapexResult(ferm, dsp, purchased, p["capex"]["lang_factor"] * purchased)
