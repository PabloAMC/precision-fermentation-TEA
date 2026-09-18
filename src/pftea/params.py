"""Load assumptions.yaml into a flat dict of base values.

Each parameter block has value/low/high. `base()` returns the base values;
`sample()` (in montecarlo.py) draws from triangular(low, value, high).
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "data" / "assumptions.yaml"


def load(path: Path = DEFAULT) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _val(block):
    return block["value"] if isinstance(block, dict) and "value" in block else block


def base(raw: dict) -> dict:
    """Flatten to {section: {name: base_value}} plus downstream steps list."""
    out = {}
    for section, params in raw.items():
        if section == "downstream":
            out[section] = {
                "steps": [{"name": s["name"], "recovery": _val(s["recovery"])}
                          for s in params["steps"]],
                "dsp_capex_multiplier": _val(params["dsp_capex_multiplier"]),
            }
        elif isinstance(params, dict):
            out[section] = {k: _val(v) for k, v in params.items()}
        else:
            out[section] = params
    return out


def guesses(raw: dict) -> list[str]:
    """List parameters whose source is 'guess'. Phase 1 wants this short."""
    def is_guess(v):
        return isinstance(v, dict) and str(v.get("source", "")).startswith("guess")
    found = []
    for section, params in raw.items():
        if not isinstance(params, dict):
            continue
        if section == "downstream":
            found += [f"downstream.{s['name']}" for s in params["steps"] if is_guess(s)]
            found += [f"downstream.{k}" for k, v in params.items() if k != "steps" and is_guess(v)]
        else:
            found += [f"{section}.{k}" for k, v in params.items() if is_guess(v)]
    return found
