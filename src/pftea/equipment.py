"""Purchased equipment costs (2018$ unless noted), escalated to the cost year by an index.

Sources: Humbird (2021) SI sheet Equip (ACCE V10, SuperPro, Couper), unless the entry says
otherwise. Each function returns the purchased cost of ONE unit of the given size; `units`
splits a duty over identical units no larger than the maximum size.

Fermenters use Humbird's microbial STR quotes (Table10 "STRFERM", 1-196 m3), interpolated
log-log between quotes. Beyond 196 m3 the curve is extrapolated with the exponent of the last
segment (0.89): big fermenters are heavy, so the economy of scale is weak (conservative).
"""
from __future__ import annotations

import math

import numpy as np

STRFERM = [(0.984, 58996.1), (2.0, 86049.6), (5.0, 138961.4), (10.0, 212081.8), (20.0, 325293.4),
           (50.0, 710886.8), (100.0, 1256953.9), (196.462, 2465776.5)]      # Equip!BN23:BT30
CHILLER = [(1000, 486853.7), (1750, 787809.9), (2500, 885267.5), (4000, 1028792.1), (5000, 1104846.1),
           (6500, 1201543.2), (8000, 1284007.3), (10000, 1378966.1)]        # Equip!AL6:AN13


def _loglog(table, x):
    xs = np.log([a for a, _ in table]); ys = np.log([b for _, b in table])
    lx = math.log(x)
    if lx <= xs[0]:
        n = (ys[1] - ys[0]) / (xs[1] - xs[0]); return math.exp(ys[0] + n * (lx - xs[0]))
    if lx >= xs[-1]:
        n = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]); return math.exp(ys[-1] + n * (lx - xs[-1]))
    return float(math.exp(np.interp(lx, xs, ys)))


def units(duty: float, max_size: float) -> tuple[int, float]:
    n = max(1, math.ceil(duty / max_size - 1e-9))
    return n, duty / n


def fermenter(volume_m3: float) -> float:
    """Microbial STR, vessel + agitator, bare (ACCE via Humbird Table10 STRFERM)."""
    return _loglog(STRFERM, volume_m3)


def tank(volume_m3: float) -> float:
    """Agitated jacketed 316L tank (Equip!CH21:CJ21 power fit, 1-100 m3)."""
    return 56820.52633840857 * volume_m3 ** 0.48121713530163496


def sterilizer(L_h: float) -> float:
    """HTST continuous sterilizer (Equip!N21, P21; SuperPro), max 100,000 L/h."""
    return 712.0575456258753 * L_h ** 0.5914644208211489


def compressor(acmh: float) -> float:
    """Air compressor (Equip!U20, U21; ACCE), linear, max 52,500 ACMH per unit."""
    return 29.50373779419718 * acmh + 207444.11060818314


def chiller(kW_duty: float) -> float:
    """Chilled-water system (Equip!AL6:AN13; ACCE), per unit up to 12,000 kW."""
    return _loglog(CHILLER, kW_duty)


def cooling_tower(L_s: float) -> float:
    """Cooling tower, field assembled (Equip!BC21, BE21; ACCE)."""
    return 3838.9275023917103 * L_s ** 0.7451758797007376


def boiler(kg_h: float) -> float:
    """Packaged natural-gas boiler (Equip!AS20, AS21; ACCE), max 360,000 kg/h."""
    return 7.199989943232405 * kg_h + 127926.26092798891


def water_purification(m3_h: float) -> float:
    """Demineraliser + UF/RO (Equip!CB20, CB21; ACCE)."""
    return 5173.368965432751 * m3_h + 101878.7106030444


def centrifuge(gpm: float) -> float:
    """Disk-stack centrifuge (Equip!AB21, AD21; Couper), max 150 gpm (34,065 kg/h)."""
    return 68407.87631591759 * gpm ** 0.52


def rvf(kg_h_solids: float) -> float:
    """Rotary vacuum filter (Equip!AG21, AI21; ACCE), max 12,000 kg/h."""
    return 6631.875973155951 * kg_h_solids ** 0.4216808506848345


def filter_housing(m2: float) -> float:
    """Sterile filter housing (Equip!CO20, CO21; SuperPro)."""
    return 3063.05042767042 * m2 + 8859.027157791672


def membrane_skid(m2: float, usd_per_m2_2018: float) -> float:
    """MF/UF skid, linear in membrane area (placeholder basis; see data/pf/base.yaml)."""
    return usd_per_m2_2018 * m2


def spray_dryer(kg_water_h: float, ref_cost_2018: float = 2.5e6, ref_kg_h: float = 2000.0,
                exponent: float = 0.6) -> float:
    """Spray dryer incl. air heater, cyclones, bag filter (power law; basis in base.yaml)."""
    return ref_cost_2018 * (kg_water_h / ref_kg_h) ** exponent


# largest single units (Equip sheet)
MAX = dict(sterilizer_L_h=100000, compressor_acmh=52500, chiller_kW=12000, boiler_kg_h=360000,
           centrifuge_gpm=150, rvf_kg_h=12000, tank_m3=500, dryer_kg_h=10000)
