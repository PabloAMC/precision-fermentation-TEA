"""Mass balances of one batch, split by use, for checking the model by hand (explorer, report).

Sugar and oxygen are split into what growth, maintenance and product formation take, per phase:
    growth       (cells grown) / mw_cell x (glucose or O2 per C-mol of cells grown)       [Heijnen growth reaction]
    maintenance  k x integral of cells dt / mw_cell x (glucose or O2 per C-mol cells per h) [Tijhuis reaction, scaled
                 by the phase's maintenance factor k = Host.maint(prod)]
    product      protein made / mw_protein x (glucose or O2 per C-mol protein)            [product reaction at Y_ps]
The growth and maintenance terms are integrated over the batch's time series (trapezoid rule), so
their sum differs from the simulator's own step-by-step totals by about 1%; the totals reported are
the simulator's. A large-tank yield loss (Host.growth_yield_loss) is counted with maintenance.

Carbon balance: carbon in (glucose + inoculum cells) against carbon out (cells + protein + CO2),
all in kmol of carbon; the relative gap is reported.

Only glucose-fed production phases are split (a methanol-fed phase returns split = None).
"""
from __future__ import annotations

import numpy as np

from . import params, plant
from . import pf_ferm as pf
from . import product as pr
from . import thermo as th

O2 = "O2 (aq)"


def batch_balances(p: dict) -> dict:
    """Per-batch flows, the sugar and oxygen split by use, and the carbon balance for parameters p."""
    b = plant.batch(p, keep_series=True)
    host = plant._host(p)
    prot = pr.protein(params.v(p, "plant.product"))
    g = host.growth
    mw_cell, MWG = g.bio.mw, pf.MW["glc"]
    t = np.array(b.series["t"])
    F = np.array(b.series["X"]) * np.array(b.series["W"])            # kg cells
    cells = F / mw_cell                                               # kmol C-mol cells
    grow = t <= b.t_growth
    integ = lambda m: float(np.trapezoid(cells[m], t[m])) if m.sum() > 1 else 0.0   # noqa: E731
    F0, Fs, Fe = F[0], float(np.interp(b.t_growth, t, F)), F[-1]
    flows = dict(product_kg=b.product_kg, cells_kg=b.cells_kg, glucose_kg=b.glucose_kg, nh3_kg=b.nh3_kg,
                 o2_kg=b.o2_kmol * pf.MW["O2"], co2_kg=b.co2_kmol * pf.MW["CO2"], water_evaporated_kg=b.evap_kg,
                 feed_water_kg=b.feed_water_kg, broth_start_m3=b.W0, broth_end_m3=b.W_end,
                 heat_removed_kWh=b.heat_kWh, growth_h=b.t_growth, total_h=b.t_total, titer_g_L=b.titer)
    split = None
    if params.v(p, "strain.methanol_frac_prod") == 0:
        coef = lambda rx, name: -rx.of(name)                           # noqa: E731  (consumption > 0)
        rx_p = pr.product_reaction(prot, th.get(pf.GLC), params.v(p, "strain.Y_ps_g_g"))
        L = host.growth_yield_loss
        loss = L / (1 - L) if L > 0 else 0.0                            # extra catabolism per unit of growth substrate
        m_g, m_p = host.maint(False), host.maint(True)

        def use(name, scale):
            grown_g, grown_p = (Fs - F0) / mw_cell, (Fe - Fs) / mw_cell
            gr = coef(g.growth, name)
            maint_extra = loss * coef(g.growth, pf.GLC) / coef(g.maint, pf.GLC) * coef(g.maint, name)
            return {"growing the cells": grown_g * gr * scale,
                    "maintenance while growing": (m_g * integ(grow) * coef(g.maint, name) + grown_g * maint_extra) * scale,
                    "slow growth during production": grown_p * gr * scale,
                    "maintenance during production": (m_p * integ(~grow) * coef(g.maint, name) + grown_p * maint_extra) * scale,
                    "making the protein": b.product_kg / prot.species.mw * coef(rx_p, name) * scale}
        split = dict(glucose_kg=use(pf.GLC, MWG), o2_kg=use(O2, pf.MW["O2"]))
    c_in = b.glucose_kg / MWG * 6 + F0 / mw_cell
    c_out = b.cells_kg / mw_cell + b.product_kg / prot.species.mw + b.co2_kmol
    return dict(flows=flows, split=split,
                carbon=dict(in_kmol=c_in, out_kmol=c_out, gap=(c_out - c_in) / c_in))
