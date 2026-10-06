"""Metabolic floor: the least substrate, ammonia, O2 and heat that a process needs per kg of product at the
host's energetic ceiling, and the fermenter productivity that O2 transfer and heat removal allow even with
perfect cells.

1. Yield ceiling. Y* = plant.energetic_ceiling(p): the ATP of polymerisation, amino-acid synthesis and
   sulfate assimilation paid by respiring the substrate (product.py, section 4). Transport, secretion,
   folding and turnover are not counted, so Y* is an upper bound on yield and everything below is a
   lower bound on use, for this host's P/O ratio (hosts.<host>.po_ratio, a model value): a host making more
   ATP per O2 would need slightly less.
2. Product reaction at Y* (product.product_reaction, element-balanced on C, H, O, N), per C-mol of
   protein: substrate -nu_s, NH3 -nu_N, O2 -nu_O2, reaction enthalpy dH_r (kJ, negative = released).
   Per kg of protein multiply by n = 1000 / M_p (C-mol per kg; M_p = g per C-mol):
       m_s = -nu_s n M_s / 1000 [kg],   m_N = -nu_N n M_NH3 / 1000 [kg],
       n_O2 = -nu_O2 n [mol],           Q = -dH_r n / 1000 [MJ].
   With no cells there is no growth or maintenance: these are the inputs of the product alone.
3. Input floor, $/kg:
       c_in = m_s c_s + m_N c_NH3 + n_O2 / 1000 * E_O2 * c_e
   E_O2 (kWh per kmol O2: compressor, agitator and chilling) is the base vessel's (plant.py block 4); it is an
   engineering number, not a metabolic one, and the term is a few cents.
4. Productivity bound, kg protein per m3 per hour, with every mole of O2 and every joule going to product:
       P_O2 = OTR_max / n_O2,    P_heat = 3.6 q_max / Q,    P_max = min(P_O2, P_heat)
   (OTR_max in mol/m3/h; q_max in kW/m3, 3.6 MJ per kWh). The product reaction releases Q/n_O2 ~ 580 kJ per
   mol O2 for BLG, more than respiration alone (~460), because making the protein also releases heat (its
   enthalpy is a grade-D analogy, product.py), so cooling binds slightly before O2 transfer. P_heat is also
   given at the bounds of q_max. OTR_max is per m3 of cell-free liquid in the model; with no cells it is per m3
   of broth. Real cells must also respire for their own maintenance and cannot be packed without limit, so
   real productivity sits well below P_max: it bounds capital from below only loosely.
"""
from __future__ import annotations

from . import plant
from . import product as pr
from . import thermo as th
from . import params
from .params import v


def metabolic_floor(p: dict, csource: str = "Glucose (s)", price_usd_kg: float | None = None) -> dict:
    """Inputs per kg of product at the energetic ceiling and the O2/heat productivity bound (docstring)."""
    y = plant.energetic_ceiling(p, csource)
    prot = pr.protein(v(p, "plant.product"))
    rx = pr.product_reaction(prot, th.get(csource), y)
    n = 1000.0 / prot.species.mw
    o2 = next(name for name in ("O2 (aq)", "O2 (g)") if rx.of(name) != 0)
    m_s = -rx.of(csource) * n * th.get(csource).mw / 1000
    m_n = -rx.of("NH3 (aq)") * n * th.get("NH3 (aq)").mw / 1000
    n_o2 = -rx.of(o2) * n
    heat_MJ = -rx.dH * n / 1000
    r = plant.evaluate(p)
    b = r.batch
    e_o2 = (b.comp_kWh + b.agit_kWh + b.heat_kWh * v(p, "utilities.rt_refrig")) / b.o2_kmol   # kWh/kmol O2
    c_s = v(p, "utilities.glucose_usd_kg") if price_usd_kg is None else price_usd_kg
    cost = {"substrate": m_s * c_s, "ammonia": m_n * v(p, "utilities.ammonia_usd_kg"),
            "aeration and cooling electricity": n_o2 / 1000 * e_o2 * v(p, "utilities.electricity_usd_kWh")}
    p_o2 = v(p, "fermenter.otr_cap_mol_m3_h") / n_o2
    p_heat = 3.6 * v(p, "fermenter.heat_removal_max_kW_m3") / heat_MJ
    q_lo, q_hi = params.bounds(p, "fermenter.heat_removal_max_kW_m3") or (v(p, "fermenter.heat_removal_max_kW_m3"),) * 2
    p_rng = tuple(min(3.6 * q / heat_MJ, p_o2) for q in (q_lo, q_hi))          # the binding limit at each end of q_max's range
    return dict(p_max_heat_range_kg_m3_h=(3.6 * q_lo / heat_MJ, 3.6 * q_hi / heat_MJ), p_max_range_kg_m3_h=p_rng, yield_g_g=y, substrate_kg=m_s, nh3_kg=m_n, o2_mol=n_o2, heat_MJ=heat_MJ, kWh_per_kmol_o2=e_o2,
                cost=cost, total=sum(cost.values()), p_max_o2_kg_m3_h=p_o2, p_max_heat_kg_m3_h=p_heat,
                p_max_kg_m3_h=min(p_o2, p_heat))
