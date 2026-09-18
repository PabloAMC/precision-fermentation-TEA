"""Operating cost, USD/yr, by category."""
from dataclasses import dataclass


@dataclass
class OpexResult:
    sugar: float
    media_other: float
    utilities: float
    labour: float
    maintenance: float
    other_fixed: float

    @property
    def variable(self):
        return self.sugar + self.media_other + self.utilities

    @property
    def fixed(self):
        return self.labour + self.maintenance + self.other_fixed

    @property
    def total(self):
        return self.variable + self.fixed


def run(p: dict, sugar_kg: float, broth_m3: float, installed_capex: float) -> OpexResult:
    o = p["opex"]
    return OpexResult(
        sugar=sugar_kg * o["sugar_price_usd_kg"],
        media_other=broth_m3 * o["media_other_usd_per_m3"],
        utilities=broth_m3 * o["utilities_usd_per_m3"],
        labour=o["labour_usd_per_yr"],
        maintenance=o["maintenance_frac_capex"] * installed_capex,
        other_fixed=o["other_fixed_frac_capex"] * installed_capex,
    )
