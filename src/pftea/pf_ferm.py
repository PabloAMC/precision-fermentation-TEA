"""Precision-fermentation production fermenter: stirred tank, two-phase fed-batch.

Built on Humbird's methods (SI sheets A.1 and Fig1.3) with a secreted product added.

Vessel (STR, as Humbird's Fig1.3 microbial fermenters): geometry from volume and H/D.
    kLa = a (P/V)^b Us^c k^(T-20)   (van 't Riet, non-coalescing; Fig1.3!C11:F11)
    with P/V the gassed agitator power per m3 of broth [W/m3], Us the superficial gas velocity
    [m/s] (mean of bottom and top), kLa in 1/s. The agitator power drawn is that P/V times the
    broth volume (no motor-efficiency loss, as in Fig1.3).
    dC_LM between bottom (C* at p_btm, inlet air) and top (C* at p_back, exit gas x_O2), with
    DO held at a setpoint (A.1 method, gas-side O2 depletion included).
Aeration optimum (Humbird Fig1.3 solves the same two unknowns): for a demanded OUR, choose the
    air rate D; Us follows; the kLa needed fixes P/V. Minimise
        compressor(D) + (1 + rt) agitator(P/V)
    (agitator power becomes heat that the chillers must remove), subject to P/V <= PV_max and
    Us_top <= Us_max. The physical OTR_max is the largest OUR that satisfies the constraints and
    the heat-removal limit.
O2-transfer cap: a literature design cap otr_cap also applies, OTR_max = min(physics, cap).
    OUR and the cap are per m3 of BROTH (the usual industrial basis). Humbird's A.1 applies its
    150 mol/m3/h per m3 of cell-free liquid, OUR = -qO2 / (W (1 - phi)), phi = X / (1000 x 0.3)
    [A.1!C66:C67]; otr_cap_basis = "cell_free_liquid" reproduces that basis as a sensitivity.
Heat per mol O2: the OTR_max heat check budgets `heat_per_o2_kJ` (Roels, 460 kJ/mol O2); the
    batch itself computes heat from formation enthalpies of the dissolved species, which gives
    about 480-510 kJ/mol O2, so growth is also slowed directly to the heat-removal limit.
Kinetics (per C-mol biomass per hour; thermo and product modules):
    growth + maintenance: Herbert-Pirt with Heijnen/Tijhuis thermodynamics (as A.1). In the
    production phase (mu ~ 0) the maintenance can instead be set to a measured m_s_prod
    [g glucose/g DCW/h]: maintenance falls at near-zero growth (Rebnegger 2016: 3x below the
    chemostat estimate), so a chemostat-level Tijhuis value overstates it there;
    product: q_p [g product / g DCW / h] through the product reaction at yield Y_ps (the yield of
    the product-forming reaction alone; maintenance and growth are added separately).
Two phases:
    1. Growth at mu_max, slowed so that OUR <= OTR_max and net heat <= heat_max, until
       X = X_prod [g DCW/L] (the last step is shortened to land on X_prod).
    2. Production for t_prod hours at mu_prod with q_p constant. No product is made during
       growth (a simplification for constitutive promoters; stated in the report).
    The initial fill W0 is solved so the broth ends exactly at fill_max. In titer mode q_p is
    solved so the final titer equals the target. A design whose W0 is below the minimum
    working fill is flagged.
Mass balance (liquid ~1 kg/L):
    dM/dt = glucose feed/w_s + NH3 feed/w_N + O2 absorbed - CO2 released - water evaporated
Heat: -sum r_i dHf_i + agitation - evaporation; chiller electricity = rt x heat.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from . import fermentation as fm
from . import product as pr
from . import thermo as th

RHO = 1000.0            # kg/m3 broth
MW = {"glc": 180.1572, "O2": 31.9988, "CO2": 44.0098, "NH3": 17.0304, "H2O": 18.0152}
CELL_DRY_FRAC = fm.Broth().cell_dry_frac   # 0.3 g dry / g wet cells [A.1!C67]


@dataclass(frozen=True)
class STR:
    volume_m3: float
    h_to_d: float = 2.0              # STRFERM geometry (Equip Table10: 196 m3, D 5 m)
    fill_max: float = 0.8            # [Fig1.3!C8]
    kla_a: float = 0.002             # van 't Riet non-coalescing [Fig1.3!C11:F11]
    kla_b: float = 0.7
    kla_c: float = 0.2
    kla_k: float = 1.025
    kla_factor: float = 1.0          # <1 for viscous (fungal) broths
    pv_max: float = 3000.0           # W/m3 broth
    us_max: float = 0.10             # m/s at top
    p_back_bar: float = 1.33         # [A.1!C81]
    otr_cap: float | None = None     # mol/m3/h design cap, None = physics only
    otr_cap_basis: str = "broth"     # "broth" or "cell_free_liquid" (Humbird A.1)
    heat_max_kW_m3: float | None = None  # max heat removal, None = unlimited
    heat_per_o2_kJ: float = 460.0    # kJ/mol O2 for the OTR_max heat check (Roels)
    min_fill: float | None = None    # minimum initial working fill (fraction of volume)

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

    def cap_per_broth(self, X_gL: float) -> float | None:
        """The design cap expressed per m3 of broth at cell density X."""
        if not self.otr_cap:
            return None
        if self.otr_cap_basis == "cell_free_liquid":
            return self.otr_cap * max(0.0, 1.0 - X_gL / (1000 * CELL_DRY_FRAC))
        return self.otr_cap


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
    # largest D allowed by the superficial-velocity limit: expand, then solve us_top = us_max
    D_hi = D_lo
    while True:
        s = state(D_hi * 1.5)
        if s is None or s["us"] > v.us_max:
            break
        D_hi *= 1.5
        if D_hi > 1e7:
            break
    a_, b_ = D_hi, D_hi * 1.5
    for _ in range(40):
        m_ = 0.5 * (a_ + b_)
        s = state(m_)
        if s is not None and s["us"] <= v.us_max:
            a_ = m_
        else:
            b_ = m_
    D_hi = max(D_hi, a_)
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
def otr_physical(v: STR, c: Conditions) -> float:
    """Largest OUR [mol/m3 broth/h] at max fill allowed by aeration and (if set) heat removal.

    Heat is budgeted at heat_per_o2_kJ per mol O2 plus the agitation power; the heat limit binds
    when OUR x heat_per_o2/3600 + P/V > heat_max_kW_m3. The batch checks heat again with
    formation enthalpies (see simulate).
    """
    liq = v.fill_max * v.volume_m3

    def ok(our):
        a = aerate(v, c, our, liq)
        if a is None:
            return False
        if v.heat_max_kW_m3 is not None:
            heat = our * v.heat_per_o2_kJ / 3600 + a["agit_kW"] / liq
            return heat <= v.heat_max_kW_m3
        return True

    lo, hi = 1.0, 2000.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def otr_max(v: STR, c: Conditions, X_gL: float = 0.0) -> float:
    """OTR_max [mol/m3 broth/h] = min(physics, design cap expressed per m3 of broth at X)."""
    phys = otr_physical(v, c)
    cap = v.cap_per_broth(X_gL)
    return min(phys, cap) if cap else phys


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
    maint_factor: float = 1.0        # multiplies Tijhuis maintenance (growth phase; both phases if m_s_prod is None)
    m_s_prod: float | None = None    # g glucose/g DCW/h in the production phase (measured, near-zero growth)

    @property
    def growth(self) -> th.GrowthModel:
        return _growth_model(self.bio, self.T_C)

    @property
    def m_s_tijhuis(self) -> float:
        """Tijhuis maintenance at T [g glucose/g DCW/h]."""
        g = self.growth
        return -g.maint.of("Glucose (s)") * MW["glc"] / g.bio.mw

    def maint(self, prod: bool) -> float:
        """Multiplier on the Tijhuis maintenance reaction in the given phase."""
        if prod and self.m_s_prod is not None:
            return self.m_s_prod / self.m_s_tijhuis
        return self.maint_factor


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
    glucose_prod_kg: float           # glucose used in the production phase
    nh3_kg: float
    o2_kmol: float
    co2_kmol: float
    evap_kg: float
    feed_water_kg: float
    comp_kWh: float
    agit_kWh: float
    heat_kWh: float                  # heat removed by chillers (thermal)
    heat_ref_kWh: float              # heat at heat_per_o2_kJ per mol O2, for comparison
    our_max: float
    heat_max_kW_m3: float
    heat_max_kW: float               # peak total heat load of one fermenter
    comp_max_kW: float
    air_max_kmol_h: float
    series: dict = field(default_factory=dict)


def _rates(host: Host, strain: Strain, mu: float, qp: float, F: float, prod: bool = False):
    """kmol/h of glucose, O2, CO2, NH3, H2O and the heat [kW] for cells F kg."""
    g = host.growth
    cmol = F / g.bio.mw
    glc = th.get("Glucose (s)")
    out = {}
    km = host.maint(prod)
    for name in ("Glucose (s)", "O2 (aq)", "CO2 (aq)", "NH3 (aq)", "H2O (l)"):
        out[name] = (g.growth.of(name) * mu + km * g.maint.of(name)) * cmol
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
    ours_tab, comp_tab, agit_tab, air_tab = aeration_table(v, c)
    t, F, P, M = 0.0, W0 * X0, 0.0, W0 * RHO
    acc = dict(glc=0.0, glc_p=0.0, nh3=0.0, o2=0.0, co2=0.0, evap=0.0, feedw=0.0, comp=0.0, agit=0.0, heat=0.0, ref=0.0)
    our_peak = heat_peak = heat_peak_kW = comp_peak = air_peak = 0.0
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
        if phase == 1 and X >= strain.X_prod * (1 - 1e-9):
            phase, t_growth = 2, t
            t_end_prod = t + strain.t_prod
        if phase == 2 and t >= t_end_prod - 1e-9:
            break
        if t > 1000:
            ok, reason = False, "growth phase did not reach X_prod"
            break
        omax = otr_max(v, c, X)
        dt = dt_g if phase == 1 else min(dt_p, t_end_prod - t)
        if phase == 1:
            mu, q = host.mu_max, 0.0
            r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2))
            our = -r["O2 (aq)"] / W * 1000
            if our > omax:
                # O2-limited growth: OUR is linear in mu at fixed cells; two fixed-point passes
                # on the midpoint cell mass put OUR on the cap (maintenance still paid)
                r0, _ = _rates(host, strain, 0.0, 0.0, F)
                our0 = -r0["O2 (aq)"] / W * 1000
                for _ in range(2):
                    Fm = F * np.exp(mu * dt / 2)
                    r1, _ = _rates(host, strain, 1.0, 0.0, Fm)
                    r0m, _ = _rates(host, strain, 0.0, 0.0, Fm)
                    slope = (-r1["O2 (aq)"] + r0m["O2 (aq)"]) / W * 1000          # OUR per unit mu
                    base = -r0m["O2 (aq)"] / W * 1000
                    mu = max(0.0, min(host.mu_max, (omax - base) / max(slope, 1e-12)))
                if our0 >= omax:
                    mu = 0.0
                r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2))
                our = -r["O2 (aq)"] / W * 1000
            if v.heat_max_kW_m3 and _heat_density(host, strain, b, mu, F, W, dt, omax, ours_tab, agit_tab,
                                                   air_tab) > v.heat_max_kW_m3:
                # heat-limited growth: formation-enthalpy heat can bind before the OTR_max heat
                # budget; heat rises with mu, so solve for the limit (Illinois false position)
                mu = _bisect(lambda m_: _heat_density(host, strain, b, m_, F, W, dt, omax, ours_tab, agit_tab,
                                                      air_tab) - v.heat_max_kW_m3, 0.0, mu, n=60, rtol=1e-7)
                r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2))
                our = -r["O2 (aq)"] / W * 1000
            if mu > 1e-12 and X * np.exp(mu * dt) > strain.X_prod:
                # land the last growth step on X_prod (feed dilution ignored within the step)
                dt = max(np.log(strain.X_prod / X) / mu, 1e-6)
        else:
            mu, q = (strain.mu_prod if X < strain.X_max else 0.0), qp
            r, heat = _rates(host, strain, mu, q, F * np.exp(mu * dt / 2), prod=True)
            our = -r["O2 (aq)"] / W * 1000
            if our > omax * 1.0001:
                ok, reason = False, f"production OUR {our:.0f} > OTR_max {omax:.0f} mol/m3/h"
        # aeration power per m3 from the precomputed optimum (at max fill)
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
        if phase == 2:
            acc["glc_p"] += glc_kg_h * dt
        acc["nh3"] += nh3_kg_h * dt
        acc["o2"] += -r["O2 (aq)"] * dt
        acc["co2"] += r["CO2 (aq)"] * dt
        acc["evap"] += evap * dt
        acc["feedw"] += (glc_kg_h / w_s * (1 - w_s) + nh3_kg_h / w_nh3 * (1 - w_nh3)) * dt
        acc["comp"] += comp * dt
        acc["agit"] += agit * dt
        acc["heat"] += heat_total * dt
        acc["ref"] += (-r["O2 (aq)"]) * v.heat_per_o2_kJ * 1000 / 3600 * dt
        our_peak = max(our_peak, our)
        heat_peak = max(heat_peak, heat_total / W)
        heat_peak_kW = max(heat_peak_kW, heat_total)
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
                 X_end=F / W, q_p=qp, product_kg=P, cells_kg=F, glucose_kg=acc["glc"], glucose_prod_kg=acc["glc_p"],
                 nh3_kg=acc["nh3"], o2_kmol=acc["o2"], co2_kmol=acc["co2"], evap_kg=acc["evap"],
                 feed_water_kg=acc["feedw"], comp_kWh=acc["comp"], agit_kWh=acc["agit"],
                 heat_kWh=acc["heat"], heat_ref_kWh=acc["ref"], our_max=our_peak,
                 heat_max_kW_m3=heat_peak, heat_max_kW=heat_peak_kW, comp_max_kW=comp_peak,
                 air_max_kmol_h=air_peak, series=ser)


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
    x = x0
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
              w_s: float = 0.5, w_nh3: float = 0.25, keep_series: bool = False) -> Batch:
    """Solve W0 (end exactly at fill_max) and, in titer mode, q_p (end at the target titer).

    Both unknowns enter monotonically, so bracketed root finding is used: W_end rises with W0,
    and titer rises with q_p. If a target cannot be met inside the brackets, or the initial
    fill is below the minimum working fill, the batch comes back with ok=False and the reason.
    """
    V_end = v.fill_max * v.volume_m3

    def sim(w0, qp, keep=False):
        return simulate(v, c, host, strain, w0, X0, qp, w_s, w_nh3, keep_series=keep)

    def solve_W0(qp):
        return _bisect(lambda w0: sim(w0, qp).W_end - V_end, 0.02 * V_end, 0.98 * V_end, n=40, rtol=1e-5)

    if titer is None:
        qp = strain.q_p
        b = sim(solve_W0(qp), qp, keep_series)
    else:
        qp = _bisect(lambda q: sim(solve_W0(q), q).titer - titer, 1e-6, 1.0, n=40, log=True, rtol=1e-5)
        b = sim(solve_W0(qp), qp, keep_series)
        if abs(b.titer - titer) > 0.02 * titer:
            b.ok = False
            b.reason = (b.reason + "; " if b.reason else "") + f"titer {titer} g/L not reachable (got {b.titer:.1f})"
    if abs(b.W_end - V_end) > 0.03 * V_end:
        b.ok = False
        b.reason = (b.reason + "; " if b.reason else "") + "broth volume does not close at max fill"
    if v.min_fill and b.W0 < v.min_fill * v.volume_m3 * 0.999:
        b.ok = False
        b.reason = (b.reason + "; " if b.reason else "") + (
            f"initial fill {b.W0 / v.volume_m3:.0%} below minimum working fill {v.min_fill:.0%}")
    return b
