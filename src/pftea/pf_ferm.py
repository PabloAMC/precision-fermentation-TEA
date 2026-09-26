"""Precision-fermentation production fermenter: stirred tank, two-phase fed-batch.

Built on Humbird's methods (SI sheets A.1 and Fig1.3) with a secreted product added.

Vessel (STR, as Humbird's Fig1.3 microbial fermenters):
    geometry from volume and H/D; impeller diameter D/3; n Rushton impellers, power
    number Np; ungassed agitator power P = Np rho N^3 D_i^5 n.
    kLa = a (P/V)^b Us^c k^(T-20)   (van 't Riet, non-coalescing; Fig1.3!C11:F11)
    dC_LM between bottom (C* at p_btm, inlet air) and top (C* at p_back, exit gas
    x_O2), with DO held at a setpoint (A.1 method, gas-side O2 depletion included).
Aeration optimum (Humbird Fig1.3 solves the same two unknowns): for a demanded OUR,
    choose air rate D; Us follows; the kLa needed fixes P/V. Minimise
        compressor(D) + (1 + rt) agitator(P/V)
    (agitator power becomes heat that the chillers must remove), subject to
    P/V <= PV_max and Us_top <= Us_max. OTR_max(vessel) is the largest OUR that satisfies
    the constraints. A literature cap otr_cap (if given) also applies:
        OTR_max = min(physics, cap).
Kinetics (per C-mol biomass per hour; thermo and product modules):
    growth + maintenance: Herbert-Pirt with Heijnen/Tijhuis thermodynamics (as A.1);
    product: q_p [g product/g DCW/h] through the product reaction at yield Y_ps.
Two phases:
    1. Growth at mu_max (reduced so OUR <= OTR_max and net heat <= heat_max) until X = X_prod [g DCW/L].
    2. Production for t_prod hours at mu_prod with q_p constant.
    The initial fill W0 is solved so the broth ends exactly at fill_max. In titer mode q_p
    is solved so the final titer equals the target.
Mass balance (liquid ~1 kg/L):
    dM/dt = glucose feed/w_s + NH3 feed/w_N + O2 absorbed - CO2 released - water evaporated
Heat: -sum r_i dHf_i + agitation - evaporation; chiller electricity = rt x heat. Cooney's
    rule (0.46 MJ/mol O2) is reported alongside as a check.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from functools import lru_cache

import numpy as np

from . import fermentation as fm
from . import product as pr
from . import thermo as th

RHO = 1000.0            # kg/m3 broth
MW = {"glc": 180.1572, "O2": 31.9988, "CO2": 44.0098, "NH3": 17.0304, "H2O": 18.0152}


@dataclass(frozen=True)
class STR:
    volume_m3: float
    h_to_d: float = 2.0              # STRFERM geometry (Equip Table10: 196 m3, D 5 m)
    fill_max: float = 0.8            # [Fig1.3!C8]
    impeller_ratio: float = 3.0      # tank:impeller [Fig1.3!G17]
    power_number: float = 5.0        # Rushton [A.1!C78]
    n_impellers: int = 2             # [Fig1.3 column AC]
    kla_a: float = 0.002             # van 't Riet non-coalescing [Fig1.3!C11:F11]
    kla_b: float = 0.7
    kla_c: float = 0.2
    kla_k: float = 1.025
    kla_factor: float = 1.0          # <1 for viscous (fungal) broths
    pv_max: float = 3000.0           # W/m3 liquid
    us_max: float = 0.10             # m/s at top
    p_back_bar: float = 1.33         # [A.1!C81]
    otr_cap: float | None = None     # mol/m3/h literature cap, None = physics only
    heat_max_kW_m3: float | None = None  # max heat removal (jacket + coils), None = unlimited

    @property
    def diameter(self) -> float:
        return (4 * self.volume_m3 / (np.pi * self.h_to_d)) ** (1 / 3)

    @property
    def area(self) -> float:
        return np.pi * self.diameter ** 2 / 4

    @property
    def height(self) -> float:
        return self.h_to_d * self.diameter

    def p_btm(self, liquid_m3: float) -> float:
        return self.p_back_bar + liquid_m3 / self.area * 9.8 * RHO / 1e5

    def kla(self, pv: float, us: float, T_C: float) -> float:
        return self.kla_factor * self.kla_a * pv ** self.kla_b * us ** self.kla_c * self.kla_k ** (T_C - 20)

    def agitator_kW(self, rpm: float, liquid_m3: float) -> float:
        di = self.diameter / self.impeller_ratio
        return self.power_number * RHO * (rpm / 60) ** 3 * di ** 5 * self.n_impellers / 1000


@dataclass(frozen=True)
class Conditions:
    T_C: float = 30.0
    DO_top_frac: float = 0.1258      # [A.1!C92]
    rt_refrig: float = 0.2629248030187212   # kW electricity / kW refrigeration [RawUtil!BY4]


def aerate(v: STR, c: Conditions, our: float, liquid_m3: float, co2_per_o2: float = 1.0) -> dict | None:
    """Power-optimal air rate and agitation for a demanded OUR [mol/m3/h]. None if infeasible."""
    if our <= 0:
        return dict(D=0.0, pv=0.0, comp_kW=0.0, agit_kW=0.0, feasible=True, us=0.0)
    b = fm.Broth(T_C=c.T_C, p_back_bar=v.p_back_bar, DO_top_frac=c.DO_top_frac)
    H = b.henry
    p_b = v.p_btm(liquid_m3)
    p_max = v.p_btm(v.fill_max * v.volume_m3)
    qO2 = our * liquid_m3 / 1000                                   # kmol/h consumed
    do_t = b.DO_top_mgL / fm.MW_O2                                 # mmol/L
    do_b = do_t * p_b / v.p_back_bar
    cs_b = p_b * 0.21 * H
    T_K = c.T_C + 273

    def state(D):
        n2, o2, co2 = 0.79 * D, 0.21 * D - qO2, qO2 * co2_per_o2
        h2o = b.y_water / (1 - b.y_water) * (n2 + o2 + co2)
        tot = n2 + o2 + co2 + h2o
        x = o2 / tot
        cs_t = v.p_back_bar * x * H
        d_b, d_t = cs_b - do_b, cs_t - do_t
        if d_t <= 0:
            return None
        dclm = (d_b - d_t) / np.log(d_b / d_t) if abs(d_b - d_t) > 1e-12 else d_b
        us_top = tot * 0.08314 * T_K / v.p_back_bar / 3600 / v.area
        us_avg = 0.5 * (D * 0.08314 * T_K / p_b + tot * 0.08314 * T_K / v.p_back_bar) / 3600 / v.area
        kla_need = our / dclm / 3600
        pv = (kla_need / (v.kla_factor * v.kla_a * us_avg ** v.kla_c * v.kla_k ** (c.T_C - 20))) ** (1 / v.kla_b)
        comp = fm.compressor_kW(D, p_max)
        agit = pv * liquid_m3 / 1000
        return dict(D=D, pv=pv, us=us_top, comp_kW=comp, agit_kW=agit, dclm=dclm,
                    cost=comp + agit * (1 + c.rt_refrig))

    # air must at least carry the O2 plus the DO driving force; search above that
    D_lo = qO2 / 0.21 * 1.02
    # largest D allowed by the superficial-velocity limit
    D_hi = D_lo
    while True:
        s = state(D_hi * 1.5)
        if s is None or s["us"] > v.us_max:
            break
        D_hi *= 1.5
        if D_hi > 1e7:
            break
    grid = np.geomspace(D_lo, max(D_hi, D_lo * 1.0001), 40)
    best = None
    for D in grid:
        s = state(D)
        if s is None or s["us"] > v.us_max * 1.0001 or s["pv"] > v.pv_max:
            continue
        if best is None or s["cost"] < best["cost"]:
            best = s
    if best is None:
        return None
    best["feasible"] = True
    return best


@lru_cache(maxsize=256)
def otr_max(v: STR, c: Conditions) -> float:
    """Largest feasible OUR [mol/m3/h] at max fill: aeration and (if set) heat removal.

    Heat per mol O2 is taken as 0.46 MJ (Cooney's rule, PRIMER sec. 3.3); agitation heat adds
    P/V. The heat limit binds when OUR x 0.46/3600 + P/V > heat_max_kW_m3.
    """
    liq = v.fill_max * v.volume_m3

    def ok(our):
        a = aerate(v, c, our, liq)
        if a is None:
            return False
        if v.heat_max_kW_m3 is not None:
            heat = our * 460.0 / 3600 + a["agit_kW"] / liq
            return heat <= v.heat_max_kW_m3
        return True

    lo, hi = 1.0, 2000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            lo = mid
        else:
            hi = mid
    phys = lo
    return min(phys, v.otr_cap) if v.otr_cap else phys


@lru_cache(maxsize=256)
def aeration_table(v: STR, c: Conditions, n: int = 30):
    """Electric power per m3 [kW/m3] vs OUR at max fill, for fast interpolation."""
    liq = v.fill_max * v.volume_m3
    top = otr_max(v, c)
    ours = np.linspace(0.0, top, n)
    comp, agit, air = [], [], []
    for o in ours:
        a = aerate(v, c, max(o, 1e-6), liq)
        comp.append(a["comp_kW"] / liq if a else np.nan)
        agit.append(a["agit_kW"] / liq if a else np.nan)
        air.append(a["D"] / liq if a else np.nan)
    return ours, np.array(comp), np.array(agit), np.array(air)


@dataclass
class Host:
    bio: th.Species
    mu_max: float
    T_C: float = 30.0
    maint_factor: float = 1.0        # multiplies Tijhuis maintenance

    @property
    def growth(self) -> th.GrowthModel:
        return _growth_model(self.bio, self.T_C)


@lru_cache(maxsize=16)
def _growth_model(bio: th.Species, T_C: float) -> th.GrowthModel:
    return th.GrowthModel(bio, th.get("Glucose (s)"), T_C)


@dataclass
class Strain:
    product: pr.Protein
    Y_ps: float                      # g product / g glucose through the product reaction
    X_prod: float                    # g DCW/L at the start of production
    mu_prod: float                   # 1/h during production
    t_prod: float                    # h of production
    q_p: float | None = None         # g/g/h; solved in titer mode
    X_max: float = 150.0             # g DCW/L: growth stops here (feed-limited plateau)


@dataclass
class Batch:
    ok: bool
    reason: str
    t_growth: float
    t_total: float
    W0: float                        # m3 initial
    W_end: float                     # m3 final
    titer: float                     # g/L
    X_end: float
    q_p: float
    product_kg: float
    cells_kg: float
    glucose_kg: float
    nh3_kg: float
    o2_kmol: float
    co2_kmol: float
    evap_kg: float
    feed_water_kg: float
    comp_kWh: float
    agit_kWh: float
    heat_kWh: float                  # heat removed by chillers (thermal)
    heat_cooney_kWh: float
    our_max: float
    heat_max_kW_m3: float
    comp_max_kW: float
    air_max_kmol_h: float
    series: dict = field(default_factory=dict)


def _rates(host: Host, strain: Strain, mu: float, qp: float, F: float):
    """kmol/h of glucose, O2, CO2, NH3, H2O and the heat [kW] for cells F kg."""
    g = host.growth
    cmol = F / g.bio.mw
    glc = th.get("Glucose (s)")
    out = {}
    for name in ("Glucose (s)", "O2 (aq)", "CO2 (aq)", "NH3 (aq)", "H2O (l)"):
        out[name] = (g.growth.of(name) * mu + host.maint_factor * g.maint.of(name)) * cmol
    heat = -(sum(out[n] * th.get(n).dHf for n in out) + mu * cmol * g.bio.dHf) * 1000 / 3600
    if qp > 0:
        p = strain.product
        rx = pr.product_reaction(p, glc, strain.Y_ps)
        pcmol = qp * F / p.species.mw                  # kmol C-mol product/h
        for name in out:
            out[name] += rx.of(name) * pcmol
        heat += -(sum(rx.of(n) * th.get(n).dHf for n in out) + p.species.dHf) * pcmol * 1000 / 3600
    return out, heat


def _heat_density(host, strain, b, mu, F, W, dt, omax, ours_tab, agit_tab, air_tab) -> float:
    """Net heat to remove [kW/m3] in a growth step at rate mu (reaction + agitation - evaporation)."""
    r, heat = _rates(host, strain, mu, 0.0, F * np.exp(mu * dt / 2))
    our = -r["O2 (aq)"] / W * 1000
    agit = np.interp(min(our, omax), ours_tab, agit_tab) * W
    air = np.interp(min(our, omax), ours_tab, air_tab) * W
    evap = b.y_water / (1 - b.y_water) * (air + r["O2 (aq)"] + r["CO2 (aq)"]) * MW["H2O"]
    return (heat + agit - evap / 3600 * fm.H2O_VAP_HEAT) / W


def simulate(v: STR, c: Conditions, host: Host, strain: Strain, W0: float, X0: float, qp: float,
             w_s: float = 0.5, w_nh3: float = 0.25, dt_g: float = 0.25, dt_p: float = 1.0,
             keep_series: bool = False) -> Batch:
    """Run one batch from initial broth W0 [m3] at X0 [g/L]."""
    b = fm.Broth(T_C=c.T_C, p_back_bar=v.p_back_bar)
    omax = otr_max(v, c)
    ours_tab, comp_tab, agit_tab, air_tab = aeration_table(v, c)
    t, F, P, M = 0.0, W0 * X0, 0.0, W0 * RHO
    acc = dict(glc=0.0, nh3=0.0, o2=0.0, co2=0.0, evap=0.0, feedw=0.0, comp=0.0, agit=0.0, heat=0.0, cooney=0.0)
    our_peak = heat_peak = comp_peak = air_peak = 0.0
    phase, t_growth = 1, None
    ser = {k: [] for k in ("t", "X", "titer", "our", "W")} if keep_series else {}
    t_end_prod = None
    ok, reason = True, ""
    while True:
        W = M / RHO
        if not np.isfinite(W) or W <= 0.001 * v.volume_m3:
            ok, reason = False, "broth volume collapsed"
            break
        X = F / W
        if phase == 1 and X >= strain.X_prod:
            phase, t_growth = 2, t
            t_end_prod = t + strain.t_prod
        if phase == 2 and t >= t_end_prod - 1e-9:
            break
        if t > 1000:
            ok, reason = False, "growth phase did not reach X_prod"
            break
        dt = dt_g if phase == 1 else min(dt_p, t_end_prod - t)
        if phase == 1:
            mu, q = host.mu_max, 0.0
            r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2))
            our = -r["O2 (aq)"] / W * 1000
            if our > omax:
                # O2-limited growth: scale mu so OUR = OTR_max (maintenance still paid)
                r0, _ = _rates(host, strain, 0.0, 0.0, F)
                our0 = -r0["O2 (aq)"] / W * 1000
                mu = max(0.0, host.mu_max * (omax - our0) / max(our - our0, 1e-12))
                r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2))
                our = -r["O2 (aq)"] / W * 1000
            if v.heat_max_kW_m3 and _heat_density(host, strain, b, mu, F, W, dt, omax, ours_tab, agit_tab,
                                                   air_tab) > v.heat_max_kW_m3:
                # heat-limited growth: otr_max budgets 460 kJ/mol O2, but growth releases a little more
                # (formation enthalpies), so the cooling cap can bind first. Heat is nearly linear in mu:
                # secant steps from (0, h0), kept on the safe side of the cap
                hd = lambda m_: _heat_density(host, strain, b, m_, F, W, dt, omax, ours_tab, agit_tab,  # noqa: E731
                                              air_tab) - v.heat_max_kW_m3
                m0, h0, m1, h1 = 0.0, hd(0.0), mu, hd(mu)
                for _ in range(6):
                    if h0 >= 0:            # even maintenance alone breaks the cap: no growth
                        m1 = 0.0
                        break
                    m2 = m0 + (m1 - m0) * (-h0) / (h1 - h0) if h1 != h0 else m0
                    h2 = hd(m2)
                    if abs(h2) < 1e-4 * v.heat_max_kW_m3:
                        m1 = m2
                        break
                    if h2 > 0:
                        m1, h1 = m2, h2
                    else:
                        m0, h0 = m2, h2
                mu = min(m0, m1) if hd(m1) > 0 else m1
                r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2))
                our = -r["O2 (aq)"] / W * 1000
        else:
            mu, q = (strain.mu_prod if X < strain.X_max else 0.0), qp
            r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2))
            our = -r["O2 (aq)"] / W * 1000
            if our > omax * 1.0001:
                ok, reason = False, f"production OUR {our:.0f} > OTR_max {omax:.0f} mol/m3/h"
        # aeration power per m3 from the precomputed optimum (at max fill: conservative)
        comp = np.interp(min(our, omax), ours_tab, comp_tab) * W
        agit = np.interp(min(our, omax), ours_tab, agit_tab) * W
        air = np.interp(min(our, omax), ours_tab, air_tab) * W
        evap = b.y_water / (1 - b.y_water) * (air + r["O2 (aq)"] + r["CO2 (aq)"]) * MW["H2O"]
        heat_total = heat + agit - evap / 3600 * fm.H2O_VAP_HEAT
        glc_kg_h = -r["Glucose (s)"] * MW["glc"]
        nh3_kg_h = -r["NH3 (aq)"] * MW["NH3"]
        dM = (glc_kg_h / w_s + nh3_kg_h / w_nh3 + (-r["O2 (aq)"]) * MW["O2"]
              - r["CO2 (aq)"] * MW["CO2"] - evap)
        acc["glc"] += glc_kg_h * dt
        acc["nh3"] += nh3_kg_h * dt
        acc["o2"] += -r["O2 (aq)"] * dt
        acc["co2"] += r["CO2 (aq)"] * dt
        acc["evap"] += evap * dt
        acc["feedw"] += (glc_kg_h / w_s * (1 - w_s) + nh3_kg_h / w_nh3 * (1 - w_nh3)) * dt
        acc["comp"] += comp * dt
        acc["agit"] += agit * dt
        acc["heat"] += heat_total * dt
        acc["cooney"] += (-r["O2 (aq)"]) * 460.0 * 1000 / 3600 * dt
        our_peak = max(our_peak, our)
        heat_peak = max(heat_peak, heat_total / W)
        comp_peak = max(comp_peak, comp)
        air_peak = max(air_peak, air)
        if keep_series:
            ser["t"].append(t); ser["X"].append(X); ser["titer"].append(P / W); ser["our"].append(our); ser["W"].append(W)
        growth = np.exp(mu * dt)
        P += q * F * ((growth - 1) / (mu * dt) if mu * dt > 1e-9 else 1.0) * dt
        F *= growth
        M += dM * dt
        t += dt
    W = M / RHO
    return Batch(ok=ok, reason=reason, t_growth=t_growth or t, t_total=t, W0=W0, W_end=W, titer=P / W,
                 X_end=F / W, q_p=qp, product_kg=P, cells_kg=F, glucose_kg=acc["glc"],
                 nh3_kg=acc["nh3"], o2_kmol=acc["o2"], co2_kmol=acc["co2"], evap_kg=acc["evap"],
                 feed_water_kg=acc["feedw"], comp_kWh=acc["comp"], agit_kWh=acc["agit"],
                 heat_kWh=acc["heat"], heat_cooney_kWh=acc["cooney"], our_max=our_peak,
                 heat_max_kW_m3=heat_peak, comp_max_kW=comp_peak, air_max_kmol_h=air_peak, series=ser)


def secant(f, x0, x1, tol=1e-6, maxit=40):
    f0, f1 = f(x0), f(x1)
    for _ in range(maxit):
        if abs(f1 - f0) < 1e-15:
            break
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        x0, f0 = x1, f1
        x1, f1 = x2, f(x2)
        if abs(f1) < tol:
            break
    return x1


def _bisect(f, lo, hi, n=40, log=False, rtol=1e-4):
    """Root of an increasing function on [lo, hi] by the Illinois (bracketed false-position)
    method; returns an end of the bracket if there is no sign change."""
    x0, x1 = (np.log(lo), np.log(hi)) if log else (lo, hi)
    g = (lambda x: f(np.exp(x))) if log else f
    f0, f1 = g(x0), g(x1)
    if f0 >= 0:
        return lo
    if f1 <= 0:
        return hi
    side = 0
    for _ in range(n):
        x = (x0 * f1 - x1 * f0) / (f1 - f0)
        fx = g(x)
        if abs(fx) < 1e-12 or abs(x1 - x0) < rtol * max(1.0, abs(x)):
            break
        if fx > 0:
            x1, f1 = x, fx
            if side == -1:
                f0 *= 0.5
            side = -1
        else:
            x0, f0 = x, fx
            if side == 1:
                f1 *= 0.5
            side = 1
    return float(np.exp(x)) if log else float(x)


def run_batch(v: STR, c: Conditions, host: Host, strain: Strain, X0: float, titer: float | None = None,
              w_s: float = 0.5, keep_series: bool = False) -> Batch:
    """Solve W0 (end exactly at fill_max) and, in titer mode, q_p (end at the target titer).

    Both unknowns enter monotonically, so bracketed bisection is used: W_end rises with W0,
    and titer rises with q_p. If a target cannot be met inside the brackets, the batch comes
    back with ok=False and the reason.
    """
    V_end = v.fill_max * v.volume_m3

    def w_end(w0, qp):
        return simulate(v, c, host, strain, w0, X0, qp, w_s).W_end - V_end

    def solve_W0(qp):
        return _bisect(lambda w0: w_end(w0, qp), 0.02 * V_end, 0.98 * V_end, n=40, rtol=1e-5)

    if titer is None:
        qp = strain.q_p
        b = simulate(v, c, host, strain, solve_W0(qp), X0, qp, w_s, keep_series=keep_series)
    else:
        def h(qp):
            return simulate(v, c, host, strain, solve_W0(qp), X0, qp, w_s).titer - titer
        qp = _bisect(h, 1e-6, 1.0, n=40, log=True, rtol=1e-5)
        b = simulate(v, c, host, strain, solve_W0(qp), X0, qp, w_s, keep_series=keep_series)
        if abs(b.titer - titer) > 0.02 * titer:
            b.ok = False
            b.reason = (b.reason + "; " if b.reason else "") + f"titer {titer} g/L not reachable (got {b.titer:.1f})"
    if abs(b.W_end - V_end) > 0.03 * V_end:
        b.ok = False
        b.reason = (b.reason + "; " if b.reason else "") + "broth volume does not close at max fill"
    return b
