"""assumptions -> results. The only entry point the notebooks should call."""
import argparse
from . import params, upstream, downstream, capex, opex, economics


def run(p: dict) -> dict:
    rec = downstream.overall_recovery(p)
    up = upstream.run(p, rec)
    cx = capex.run(p, up.n_fermenters)
    ox = opex.run(p, up.sugar_kg, up.broth_m3, cx.total_installed)
    ec = economics.run(p, ox, cx.total_installed)
    return {
        "overall_recovery": rec,
        "n_fermenters": up.n_fermenters,
        "broth_m3": up.broth_m3,
        "sugar_kg": up.sugar_kg,
        "installed_capex_usd": cx.total_installed,
        "opex_usd_yr": ox.total,
        "cop_usd_kg": ec.cop_usd_kg,
        "msp_usd_kg": ec.msp_usd_kg,
        "breakdown_usd_kg": ec.breakdown_usd_kg,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--titer", type=float, help="override titer g/L")
    a = ap.parse_args()
    p = params.base(params.load())
    if a.titer:
        p["strain"]["titer_g_per_L"] = a.titer
    r = run(p)
    print(f"titer {p['strain']['titer_g_per_L']} g/L  ->  COP ${r['cop_usd_kg']:.1f}/kg, "
          f"MSP ${r['msp_usd_kg']:.1f}/kg, {r['n_fermenters']} fermenters")
    for k, v in r["breakdown_usd_kg"].items():
        print(f"  {k:20s} {v:6.2f}")


if __name__ == "__main__":
    main()
