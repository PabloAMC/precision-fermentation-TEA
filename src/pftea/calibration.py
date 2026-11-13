"""Calibration anchors 2-4: run the model on each anchor's own process inputs.

Structure (cost curves, installation factors, labour model, maintenance and insurance fractions)
is never changed here: only the process inputs, prices, cost year and financing of the anchor,
listed in data/calibration/<anchor>.yaml. Anchor 1 (baker's yeast) is humbird_yeast.py.
Results and misses are recorded in docs/VALIDATION.md before anything is fixed.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from . import finance as fin
from . import params, plant
from .params import v

ROOT = Path(__file__).resolve().parents[2]


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / f"data/calibration/{name}.yaml").read_text())


# The anchors' own ('light') conventions, for the convention rows of docs/VALIDATION.md.
LIGHT = {"capital.basis": "nrel"}   # NREL-style capital basis and fixed costs


def voutilainen_conventions(capital_basis: str) -> dict:
    """Voutilainen's fixed costs (maintenance 1.5% of FCI, no insurance) on either capital basis."""
    nb = dict(params.load()["capital"]["nrel_basis"]["value"], maintenance_frac_isbl=0.0, maintenance_frac_fci=0.015,
              insurance_frac_fci=0.0)
    if capital_basis == "nrel":
        return {"capital.basis": "nrel", "capital.nrel_basis": {"value": nb}}
    return {"finance.maintenance_frac_tci": 0.015, "finance.insurance_tax_frac_tci": 0.0}


def run(name: str, extra: dict | None = None) -> dict:
    """Run one anchor; `extra` overrides are applied on top of the case (convention rows only)."""
    case = load(name)
    p = params.override(params.load(), {**case["overrides"], **(extra or {})})
    r = plant.evaluate(p)
    out = {"result": r, "case": case, "params": p}
    if name == "nrel2011_cellulase":
        d = case["finance_debt"]
        variable = sum(val for k, val in r.annual.items()
                       if k not in ("labour", "maintenance", "insurance", "capital charge"))
        fixed = r.annual["labour"] + r.annual["maintenance"] + r.annual["insurance"]
        kg = v(p, "plant.annual_target_protein_t") * 1000
        msp = fin.msp_dcf(r.tci, variable, fixed, kg, irr=v(p, "finance.dcf_irr"), life=v(p, "finance.dcf_life_y"),
                          tax=v(p, "finance.tax_rate"), wc_frac=v(p, "finance.working_capital_frac_fci"),
                          debt_frac=d["debt_frac"], loan_rate=d["loan_rate"], loan_years=d["loan_years"])
        per_delivered = msp / case["delivered_fraction"]["value"]
        tg = case["target"]
        out["compare"] = {
            "usd_per_kg_protein (DCF, NREL financing)": (per_delivered, tg["usd_per_kg_protein"]["value"]),
            "glucose_kg_per_kg": (r.physical["glucose_kg"] / case["delivered_fraction"]["value"], tg["glucose_kg_per_kg"]["value"]),
            "electricity_kWh_per_kg": (r.physical["electricity_kWh"], tg["electricity_kWh_per_kg"]["value"]),
            "o2_mol_per_kg": (r.physical["o2_kg"] * 1000 / 32, tg["o2_mol_per_kg"]["value"]),
        }
    elif name == "intelligen2025_ova":
        tg = case["target"]
        out["compare"] = {
            "usd_per_kg_powder (Humbird convention)": (r.per_kg_powder, tg["usd_per_kg_powder_humbird_convention"]["value"]),
            "TCI_usd": (r.tci, tg["tci_usd"]["value"]),
            "glucose_kg_per_kg_powder": (r.physical["glucose_kg"] * r.per_kg_powder / r.msp_ccf,
                                         tg["glucose_kg_per_kg_powder"]["value"]),
            "electricity_kWh_per_kg_powder": (r.physical["electricity_kWh"] * r.per_kg_powder / r.msp_ccf,
                                              tg["electricity_kWh_per_kg_powder"]["value"]),
        }
    elif name == "voutilainen2021_case":
        fx = case["fx_usd_per_eur"]
        target_ratio = case["sugar_per_kg_protein_in_broth"]
        # match the anchor's stated sugar use (a process input) by solving the product-reaction yield
        lo, hi = 0.12, 0.6
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            b = plant.batch(params.override(p, {"strain.Y_ps_g_g": mid}))
            if b.glucose_kg / b.product_kg > target_ratio:
                lo = mid
            else:
                hi = mid
        p = params.override(p, {"strain.Y_ps_g_g": 0.5 * (lo + hi)})
        r = plant.evaluate(p)
        out.update(result=r, params=p)
        f = case["finance"]
        variable = sum(val for k, val in r.annual.items()
                       if k not in ("labour", "maintenance", "insurance", "capital charge"))
        fixed = r.annual["labour"] + r.annual["maintenance"] + r.annual["insurance"]
        kg = v(p, "plant.annual_target_protein_t") * 1000
        msp = fin.msp_dcf_voutilainen(r.tci, variable, fixed, kg, rate=f["rate"], life=f["life"], tax=f["tax"],
                                      capital_factor=f["capital_factor"], inflation=f["inflation"],
                                      opex_growth=f["opex_growth"], startup_revenue=f["startup_revenue"],
                                      startup_variable=f["startup_variable"], byproduct=f["byproduct"])
        tg = case["target"]
        out["compare"] = {
            "EUR_per_t_protein (their DCF)": (msp / fx * 1000, tg["eur_per_t_protein_dcf"]["value"]),
            "sugar_kg_per_kg_protein": (r.physical["glucose_kg"], tg["sugar_kg_per_kg_protein"]["value"]),
            "TCI vs their FCI (EUR)": (r.tci / fx, tg["fci_eur"]["value"]),
        }
        out["solved_Y_ps"] = 0.5 * (lo + hi)
    out["tolerance"] = case["target"]["tolerance"]
    return out


def physiology_record(p: dict | None = None) -> list[dict]:
    """Predictions of measured K. phaffii physiology from the model's first principles (none of these
    measurements is an input). Recorded in docs/VALIDATION.md, 'Predictions of measured physiology'.

    The growth model is thermo.GrowthModel (Heijnen dissipation, Tijhuis maintenance) on the host's biomass
    formula at its temperature:
        Y_max      = M_x / (-y_S M_S)                      biomass per substrate, growth reaction alone [g/g]
        Y_XS(mu)   = mu M_x / (q_S(mu) M_S)                with maintenance (Herbert-Pirt), as a chemostat at D = mu
        q_O2(mu)   = -q_O2 / M_x                           [mmol O2 / g DCW / h]
        heat/O2    = -dH_growth / (O2 used by growth)      formation enthalpies [kJ/mol O2]
    Growth models are the host's (Host.growth_on): on methanol the dissipation comes from the measured yield
    (thermo step 9, since 2026-11-03), so that row is an input and the methanol O2 uptake is the test.
        Y_fedbatch = cells grown / glucose used in the growth phase of the base batch (balances.batch_balances)
    Measured values are read from data/evidence/hosts.yaml and engineering.yaml by key. 'band' is the
    measured range (several studies, or a stated +/-); 'value' a single measurement. ok = inside the band,
    or within the stated uncertainty of a single value."""
    import numpy as np

    from . import balances
    from . import thermo as th
    from .scenarios import base_params

    p = p or base_params("blg")
    host = plant._host(p)
    bio = host.growth.bio
    ev = {e["key"]: e for f in ("hosts", "engineering")
          for e in yaml.safe_load((ROOT / f"data/evidence/{f}.yaml").read_text())}
    MU = 0.1                                       # 1/h: the dilution rate of the chemostat measurements below
    gm = {cs: host.growth_on(cs) for cs in ("Glucose (s)", "Glycerol", "Methanol")}   # as the model uses them

    def y_at(cs, mu):
        return mu * bio.mw / (-gm[cs].q(cs, mu) * th.get(cs).mw)

    def qo2_at(cs, mu):
        return -gm[cs].q("O2 (aq)", mu) / bio.mw * 1000

    g = gm["Glucose (s)"].growth
    heat_o2 = -g.dH / -g.of("O2 (aq)")
    b = plant.batch(p, keep_series=True)
    t, F = np.array(b.series["t"]), np.array(b.series["X"]) * np.array(b.series["W"])
    split = balances.batch_balances(p)["split"]["glucose_kg"]
    y_fb = (float(np.interp(b.t_growth, t, F)) - F[0]) / (split["growing the cells"] + split["maintenance while growing"])
    yk = ("kphaffii_yxs_glucose_chemostat_maurer2006", "kphaffii_yxs_max_glucose_rebnegger2016", "kphaffii_yxs_max_glucose_rebnegger2024")
    oxy, cooney = ev["oxycaloric_equivalent"], ev["heat_per_o2_shuler_kargi_cooney"]
    fb, gly, meoh, qo2 = (ev["kphaffii_yxs_glucose_fedbatch_shemesh2024"], ev["kphaffii_yxs_glycerol_chemostat_tomasgamisans2018"],
                          ev["kphaffii_yxs_methanol_chemostat_tomasgamisans2018"], ev["kphaffii_qo2_methanol_vs_glycerol_tomasgamisans2018"])
    ec = plant._host(params.override(p, {"strain.host": "ecoli"}))      # E. coli (check 8): yield at 0.1/h is an input
    gec = ec.growth

    def y_ec(mu):
        return mu * gec.bio.mw / (-gec.q("Glucose (s)", mu) * th.get("Glucose (s)").mw)
    mar, val = ev["ecoli_fedbatch_growth_rate_and_yield_marisch2013"], ev["ecoli_yxs_chemostat_valgepea2010"]
    rows = [
        dict(key="yxs_glucose", name="Cell yield on glucose, upper limit", unit="g cells / g glucose", ours=gm["Glucose (s)"].max_yield,
             band=[min(ev[k]["value"] for k in yk), max(ev[k]["value"] for k in yk)], sources=list(yk),
             note="Three chemostat studies of producing and non-producing strains. Sets how much sugar growth takes."),
        dict(key="heat_per_o2", name="Heat released per mol of O₂, growing cells", unit="kJ/mol O2", ours=heat_o2,
             band=[-oxy["high"], cooney["value"] * 1000], sources=["oxycaloric_equivalent", "heat_per_o2_shuler_kargi_cooney"],
             note="Measured on many organisms. Sets how hard the tank must be cooled."),
        dict(key="yxs_fedbatch", name="Cell yield on glucose in a fed-batch", unit="g cells / g glucose", ours=y_fb,
             band=[fb["low"], fb["high"]], sources=["kphaffii_yxs_glucose_fedbatch_shemesh2024"],
             note="Three strains in fed-batch; theirs made some ethanol. The model's base batch, growth phase."),
        dict(key="yxs_methanol", name="Cell yield on methanol (chemostat)", unit="g cells / g methanol", ours=y_at("Methanol", MU),
             value=meoh["value"], sources=["kphaffii_yxs_methanol_chemostat_tomasgamisans2018"], by_construction=True,
             note="A model input since 2026-11-03 (Heijnen's correlation gave 0.447). The O2 uptake below is the test."),
        dict(key="qo2_methanol", name="O₂ uptake on methanol at 0.1/h", unit="mmol O2 / g cells / h", ours=qo2_at("Methanol", MU),
             value=qo2["value"], stated=qo2["value_sd"], sources=["kphaffii_qo2_methanol_vs_glycerol_tomasgamisans2018"],
             note="Not fitted. Was 21% low with Heijnen's correlation; the measured yield brings it within 7%. Methanol-fed cases only."),
        dict(key="yxs_glycerol", name="Cell yield on glycerol (chemostat)", unit="g cells / g glycerol", ours=y_at("Glycerol", MU),
             band=[gly["low"], gly["high"]], sources=["kphaffii_yxs_glycerol_chemostat_tomasgamisans2018"],
             note="No case uses glycerol. The miss shows the Heijnen correlation does not carry over to every feed."),
        dict(key="yxs_ecoli_fedbatch", name="E. coli cell yield on glucose, fed-batch at 0.1/h", unit="g cells / g glucose",
             ours=y_ec(0.1), value=mar["value"], sources=["ecoli_fedbatch_growth_rate_and_yield_marisch2013"], by_construction=True,
             note="A model input (Heijnen's correlation gave 0.478, 20% above). The chemostat row below is the test."),
        dict(key="yxs_ecoli_chemostat", name="E. coli cell yield on glucose, chemostat at 0.24/h", unit="g cells / g glucose",
             ours=y_ec(0.24), band=[val["low"], val["high"]], sources=["ecoli_yxs_chemostat_valgepea2010"],
             note="Not fitted: below acetate overflow (0.27/h), where the model, which makes no acetate, applies. 37 C."),
        dict(key="qo2_glycerol", name="O₂ uptake on glycerol at 0.1/h", unit="mmol O2 / g cells / h", ours=qo2_at("Glycerol", MU),
             value=qo2["high"], stated=qo2["high_sd"], sources=["kphaffii_qo2_methanol_vs_glycerol_tomasgamisans2018"],
             note="No case uses glycerol. The model's O2 use is about twice the measured."),
    ]
    for r in rows:
        r["ours"] = float(r["ours"])
        if "band" in r:
            r["band"] = [float(x) for x in r["band"]]
            r["ok"] = bool(r["band"][0] <= r["ours"] <= r["band"][1])
        else:
            r["ok"] = bool(abs(r["ours"] - r["value"]) <= r.get("stated", 0.0))
    return rows


def report(name: str) -> str:
    o = run(name)
    lines = [f"{name}: flags {o['result'].flags or 'none'}"]
    for k, (ours, theirs) in o["compare"].items():
        lines.append(f"  {k:42s} ours {ours:14.4g}  anchor {theirs:14.4g}  {100 * (ours / theirs - 1):+6.1f}%")
    return "\n".join(lines)


if __name__ == "__main__":
    for n in ("nrel2011_cellulase", "intelligen2025_ova", "voutilainen2021_case"):
        print(report(n))
