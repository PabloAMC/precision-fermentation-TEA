"""Downstream processing: per-step recovery and overall recovery.

Overall recovery = product of step recoveries. Chromatography is skipped when
the purity target is below 0.7 (crude concentrate). DSP capital is modelled,
for now, as a multiple of fermentation purchased cost; replace with per-unit
sizing in Phase 2 once the Intelligen white papers have been extracted.
"""


def steps_for(p: dict) -> list[dict]:
    steps = p["downstream"]["steps"]
    if p["plant"]["purity_target"] < 0.7:
        steps = [s for s in steps if s["name"] != "chromatography"]
    return steps


def overall_recovery(p: dict) -> float:
    r = 1.0
    for s in steps_for(p):
        r *= s["recovery"]
    return r
