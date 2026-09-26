"""Aerobic fed-batch fermentation: kinetics, gas balance, O2 transfer and power.

Port of the time-stepping simulator in Humbird (2021) SI sheet A.1 (rows 278-320),
generalised so that the kinetics (growth only, or growth plus product) can be swapped.
Sheet columns are given in brackets so every line can be audited against the workbook.

State per step: time t, dry cells F [kg], broth volume W [L]. For a step of length dt at
specific growth rate mu:
    F_r = F_{r-1} exp(mu dt)                                                     [F]
    rates of every species from the kinetics (Herbert-Pirt), kmol/h            [G..O]
    feed water  = -glucose/w_s (1 - w_s), w_s = substrate mass fraction of feed [P]
    water stripped by off-gas = -y_w (N2 + O2 + CO2 out)/(1 - y_w) MW_H2O       [Q]
      with y_w = p_vap(T)/p_back (Raoult)
    W_r = W_{r-1} - dt avg(glc/w_s (1-w_s) + stripped + produced water) + dF    [W]
      (A.1's exact volume update; see VALIDATION.md for its sign convention)
Gas side, for air inflow D [kmol/h]:
    N2 out = 0.79 D; O2 out = 0.21 D + q_O2; CO2 out = q_CO2; x_O2,out = O2/total  [AE-AJ]
    C*_bottom = p_btm 0.21 H_O2 M_O2; C*_top = p_back x_O2,out H_O2 M_O2 [mg/L]   [AM,AN]
    DO_top fixed; DO_btm = DO_top p_btm/p_back                                  [AO,AP]
    dC_LM = ((C*_b - DO_b) - (C*_t - DO_t)) / ln(...) / M_O2          [mmol/L]  [AQ]
    OUR = -q_O2 / (W (1 - phi)) 1e6, phi = cell volume fraction       [mol/m3/h][AD]
    kLa needed = OUR / dC_LM / 3600                                        [1/s] [AY]
    kLa (bubble column) = a Us^b c^(T-20) visc^d, Us the mean superficial velocity
      of inlet (at p_btm) and outlet (at p_back) gas                         [AZ]
    broth viscosity (Krieger-Dougherty) = (1 - phi/phi_m)^(-2.5 phi_m) mu_water  [AX]
Controls solved each step (A.1 stores the values its VBA solver found):
    mu = mu_max unless that makes OUR exceed OTR_max; then mu such that OUR = OTR_max.
    D such that kLa(correlation) = kLa(needed).
    The last step is shortened so the working volume ends exactly at its maximum.
Power:
    compressor [kW] = D 2.205 379.4/60 (77+460)/8130/1.4 (p_btm,max^1.4 - 1) 0.7457/0.8  [BD]
    refrigeration electricity [kW] = rt (heat of reaction + agitation + evaporation)  [BF]
      heat of reaction = -sum_i r_i dHf_i; evaporation = stripped water x 2410 kJ/kg
      rt = kW electricity per kW refrigeration (1.24 hp/ton, Couper)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from . import thermo as th

MW_O2 = 31.9988
MW_H2O = 18.0152
H2O_VAP_HEAT = 2410.0  # kJ/kg (Phys!B56)


def xround(x: float, n: int = 0) -> float:
    """Excel ROUND (half away from zero), needed to reproduce Humbird's sheet exactly."""
    m = 10.0 ** n
    return float(np.sign(x) * np.floor(abs(x) * m + 0.5) / m)


def bisect(f: Callable[[float], float], lo: float, hi: float, tol: float = 1e-10,
           maxit: int = 200) -> float:
    flo = f(lo)
    for _ in range(maxit):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < tol * max(1.0, abs(mid)):
            break
    return 0.5 * (lo + hi)


@dataclass
class Broth:
    T_C: float = 30.0
    p_back_bar: float = 1.33
    y_O2_air: float = 0.21
    DO_top_frac: float = 0.1258          # DO at top as fraction of air saturation at 1 atm [C92]
    henry_O2_298: float = 1.3            # mmol/(L bar) [Phys!B54]
    henry_O2_Tdep: float = 1700.0        # K [Phys!B55]
    cell_wet_pg: float = 60.0            # [C66]
    cell_dry_frac: float = 0.3           # [C67]
    phi_max: float = 0.626               # Krieger-Dougherty max packing [Phys!C78]
    substrate_wt_frac: float = 0.3       # sugar mass fraction of the feed [C84]

    @property
    def henry(self) -> float:  # mmol/(L bar)                                     [F91]
        return self.henry_O2_298 * np.exp(self.henry_O2_Tdep * (1 / (self.T_C + 273) - 1 / 298))

    @property
    def p_vap_bar(self) -> float:  # Antoine, water                                 [F80]
        return 10 ** (8.07131 - 1730.63 / (self.T_C + 233.426)) / 760 * 1.01325

    @property
    def y_water(self) -> float:  # [F81]
        return self.p_vap_bar / self.p_back_bar

    @property
    def mu_water_cp(self) -> float:  # [F82]
        return 0.02414 * 10 ** (247.8 / (self.T_C + 133))

    @property
    def DO_top_mgL(self) -> float:  # [F92]
        return 0.21 * self.henry * MW_O2 * self.DO_top_frac

    def cell_volume_fraction(self, X_gL: float) -> float:  # [AC, AW]
        cells_per_mL_millions = X_gL / 1000 / (self.cell_wet_pg * self.cell_dry_frac) * 1e12 / 1e6
        return cells_per_mL_millions * self.cell_wet_pg / 1e6


@dataclass
class BubbleColumn:
    volume_L: float
    diameter_m: float
    kla_a: float = 0.32      # kLa = a Us^b c^(T-20) visc^d  [C95:F95]
    kla_b: float = 0.7
    kla_c: float = 1.025
    kla_d: float = -0.84

    @property
    def area_m2(self) -> float:
        return self.diameter_m ** 2 * np.pi / 4

    def kla(self, us_avg: float, T_C: float, visc_cp: float) -> float:
        return self.kla_a * us_avg ** self.kla_b * self.kla_c ** (T_C - 20) * visc_cp ** self.kla_d


@dataclass
class Rates:
    """Species rates in kmol/h (negative = consumed); dcw in kg/h."""
    dcw_kg_h: float
    kmol_h: dict[th.Species, float] = field(default_factory=dict)

    def get(self, name: str) -> float:
        return sum(v for s, v in self.kmol_h.items() if s.name == name)

    def heat_kW(self, dcw_species: th.Species) -> float:
        """Heat released by the reactions: -sum r_i dHf_i, in kW."""
        h = sum(v * s.dHf for s, v in self.kmol_h.items())
        h += self.dcw_kg_h / dcw_species.mw * dcw_species.dHf
        return -h * 1000 / 3600


class GrowthKinetics:
    """Growth plus maintenance on one carbon source (Herbert-Pirt, thermo.GrowthModel)."""

    def __init__(self, model: th.GrowthModel):
        self.m = model
        self.species = [s for s in model.growth.coef if s is not model.bio]

    def rates(self, mu: float, F_kg: float) -> Rates:
        cmol = F_kg / self.m.bio.mw                       # kmol C-mol biomass
        out = {s: (self.m.growth.coef.get(s, 0.0) * mu + self.m.maint.coef.get(s, 0.0)) * cmol
               for s in self.species}
        return Rates(dcw_kg_h=mu * F_kg, kmol_h=out)


@dataclass
class Step:
    t: float
    dt: float
    mu: float
    D: float
    F: float
    W: float
    rates: Rates
    glc_kg_h: float
    water_prod_kg_h: float
    stripped_kg_h: float
    gas: dict


@dataclass
class FedBatch:
    vessel: BubbleColumn
    broth: Broth
    kinetics: GrowthKinetics
    W0_L: float
    X0_gL: float
    mu_max: float
    otr_max: float               # mol/m3/h [C93]
    wv_max: float = 0.6          # [C87]
    csource: str = "Glucose (s)"
    first_dt: float = 0.01
    dt: float = 0.5

    # ----------------------------------------------------------------- one state
    def _state(self, prev: Step | None, dt: float, mu: float, D: float) -> Step:
        b, v = self.broth, self.vessel
        F = self.W0_L * self.X0_gL / 1000 if prev is None else prev.F * np.exp(mu * dt)
        r = self.kinetics.rates(mu, F)
        glc = r.get(self.csource) * th.get(self.csource).mw          # kg/h, negative
        water = r.get("H2O (l)") * MW_H2O                              # kg/h produced
        qO2, qCO2 = r.get("O2 (aq)"), r.get("CO2 (aq)")
        n2, o2, co2 = D * (1 - b.y_O2_air), D * b.y_O2_air + qO2, qCO2
        stripped = -b.y_water * (n2 + o2 + co2) / (1 - b.y_water) * MW_H2O
        ws = b.substrate_wt_frac
        if prev is None:
            W = self.W0_L
        else:
            W = prev.W - dt * (0.5 * (prev.glc_kg_h + glc) / ws * (1 - ws)
                               + 0.5 * (prev.stripped_kg_h + stripped)
                               + 0.5 * (prev.water_prod_kg_h + water)) + (F - prev.F)
        h2o_out = -stripped / MW_H2O
        total_out = n2 + o2 + h2o_out + co2
        x_o2 = o2 / total_out
        height = W / 1000 / v.area_m2
        p_btm = b.p_back_bar + height * 9.8 * 1000 / 100000
        X = F * 1000 / W
        phi = b.cell_volume_fraction(X)
        our = -qO2 / (W * (1 - phi)) * 1e6
        cs_b = p_btm * b.y_O2_air * b.henry * MW_O2
        cs_t = b.p_back_bar * x_o2 * b.henry * MW_O2
        do_t = b.DO_top_mgL
        do_b = do_t * p_btm / b.p_back_bar
        d_b, d_t = cs_b - do_b, cs_t - do_t
        if d_b > 0 and d_t > 0:
            dclm = ((d_b - d_t) / np.log(d_b / d_t) if abs(d_b - d_t) > 1e-12 else d_b) / MW_O2
        else:
            dclm = 0.0          # infeasible gas rate: no driving force left at the top
        T_K = b.T_C + 273
        gas_in = D * 0.08314 * T_K / p_btm
        gas_out = total_out * 0.08314 * T_K / b.p_back_bar
        us_avg = 0.5 * (gas_in + gas_out) / 3600 / v.area_m2
        visc = (1 - phi / b.phi_max) ** (-2.5 * b.phi_max) * b.mu_water_cp
        kla_need = our / dclm / 3600 if dclm > 0 else np.inf
        kla_corr = v.kla(us_avg, b.T_C, visc)
        gas = dict(p_btm=p_btm, X=X, phi=phi, OUR=our, x_o2_out=x_o2, dCLM=dclm, us_avg=us_avg,
                   visc=visc, kla_need=kla_need, kla_corr=kla_corr, wv=W / v.volume_L,
                   n2=n2, o2=o2, co2=co2, h2o=h2o_out)
        return Step(t=(0.0 if prev is None else prev.t + dt), dt=dt, mu=mu, D=D, F=F, W=W,
                    rates=r, glc_kg_h=glc, water_prod_kg_h=water, stripped_kg_h=stripped, gas=gas)

    def _solve_D(self, prev, dt, mu) -> Step:
        def f(D):
            s = self._state(prev, dt, mu, D)
            return s.gas["kla_corr"] - s.gas["kla_need"]
        # lower bracket: just enough air to supply the O2 consumed
        F = self.W0_L * self.X0_gL / 1000 if prev is None else prev.F * np.exp(mu * dt)
        qO2 = -self.kinetics.rates(mu, F).get("O2 (aq)")
        lo = qO2 / self.broth.y_O2_air * 1.0001
        hi = lo * 50
        D = bisect(f, lo, hi)
        return self._state(prev, dt, mu, D)

    def _solve_step(self, prev, dt) -> Step:
        s = self._solve_D(prev, dt, self.mu_max)
        if s.gas["OUR"] <= self.otr_max:
            return s
        mu = bisect(lambda m: self._solve_D(prev, dt, m).gas["OUR"] - self.otr_max, 0.0, self.mu_max)
        return self._solve_D(prev, dt, mu)

    def run(self) -> list[Step]:
        steps = [self._solve_step(None, 0.0)]
        dts = [self.first_dt, self.dt - self.first_dt]
        while True:
            dt = dts.pop(0) if dts else self.dt
            s = self._solve_step(steps[-1], dt)
            if s.gas["wv"] >= self.wv_max:
                prev = steps[-1]
                dt_end = bisect(lambda d: self._solve_step(prev, d).gas["wv"] - self.wv_max, 1e-6, dt)
                steps.append(self._solve_step(prev, dt_end))
                return steps
            steps.append(s)


def integrate(steps: list[Step], values: list[float]) -> float:
    """Trapezoidal time integral (Humbird's CurveIntegration), returned as a magnitude."""
    t = np.array([s.t for s in steps])
    return float(abs(np.trapezoid(np.array(values), t)))


def compressor_kW(D_kmol_h: float, p_btm_max_bar: float) -> float:
    """A.1 column BD: air compressor power for D kmol/h delivered at p_btm_max."""
    return (D_kmol_h * 2.205 * 379.4 / 60 * (77 + 460) / 8130 / 1.4
            * (p_btm_max_bar ** 1.4 - 1) * 0.7457 / 0.8)


def refrigeration_kW(step: Step, dcw: th.Species, rt_refrig: float, agitator_kW: float = 0.0) -> float:
    """A.1 column BF: refrigeration electricity for reaction heat + agitation - evaporation."""
    heat = step.rates.heat_kW(dcw) + agitator_kW + step.stripped_kg_h / 3600 * H2O_VAP_HEAT
    return heat * rt_refrig
