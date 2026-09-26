"""Parameters: load data/pf/base.yaml, apply scenario overrides, read values, sample ranges.

A leaf is a dict with `value` (or location keys such as `us_midwest`/`eu_nw`) plus optional
`low`/`high` (triangular sampling), `unit`, `grade` and `source`. `low`/`high` may themselves be
keyed by location. Paths are dotted, e.g. "strain.titer_g_L". Overrides replace `value` (or a
whole leaf) at a path; a `plant.location` override is applied first, so location-keyed leaves
resolve against the new location whatever the key order.
"""
from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "data/pf/base.yaml"
LOCATIONS = ("us_midwest", "eu_nw")


def load(path: Path | str = BASE) -> dict:
    return yaml.safe_load(Path(path).read_text())


def _leaf(p: dict, path: str):
    node = p
    for k in path.split("."):
        node = node[k]
    return node


def location(p: dict) -> str:
    return p.get("plant", {}).get("location", {}).get("value", "us_midwest")


def _by_location(p: dict, x):
    """A number, or a dict keyed by location resolved for p's location."""
    if isinstance(x, dict) and any(k in x for k in LOCATIONS):
        return x.get(location(p), x[LOCATIONS[0]])
    return x


def v(p: dict, path: str):
    """Value at a dotted path, resolving location-keyed leaves."""
    node = _leaf(p, path)
    if isinstance(node, dict):
        if "value" in node:
            return node["value"]
        if any(k in node for k in LOCATIONS):
            return _by_location(p, node)
    return node


def bounds(p: dict, path: str) -> tuple[float, float] | None:
    """(low, high) of a ranged leaf for p's location, or None."""
    node = _leaf(p, path)
    if not isinstance(node, dict) or "low" not in node or "high" not in node:
        return None
    lo, hi = _by_location(p, node["low"]), _by_location(p, node["high"])
    if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
        return None
    return float(lo), float(hi)


def grade(p: dict, path: str) -> str:
    node = _leaf(p, path)
    return node.get("grade", "") if isinstance(node, dict) else ""


def override(p: dict, changes: dict) -> dict:
    """Deep copy of p with {dotted.path: value or leaf-dict} applied (plant.location first)."""
    q = copy.deepcopy(p)
    order = sorted(changes, key=lambda k: k != "plant.location")
    for path in order:
        val = changes[path]
        keys = path.split(".")
        node = q
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        leaf = node.get(keys[-1])
        if isinstance(val, dict):
            node[keys[-1]] = {**(leaf if isinstance(leaf, dict) else {}), **val}
        elif isinstance(leaf, dict) and ("value" in leaf or any(k in leaf for k in LOCATIONS)):
            if "value" in leaf or not any(k in leaf for k in LOCATIONS):
                leaf["value"] = val
            else:
                leaf[location(q)] = val
        else:
            node[keys[-1]] = {"value": val}
    return q


def ranged_leaves(p: dict, prefix: str = "") -> list[str]:
    """Dotted paths of every leaf with a numeric low/high range."""
    out = []
    for k, node in p.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(node, dict):
            if "low" in node and "high" in node:
                if _has_numeric_range(node):
                    out.append(path)
            elif "value" not in node and not any(k in node for k in LOCATIONS):
                out += ranged_leaves(node, path)
    return out


def _has_numeric_range(node: dict) -> bool:
    ok = lambda x: isinstance(x, (int, float)) or (isinstance(x, dict) and all(isinstance(x.get(k), (int, float)) for k in x))
    return ok(node["low"]) and ok(node["high"])


def sample(p: dict, rng: np.random.Generator, paths: list[str] | None = None) -> dict:
    """Triangular(low, mode=value, high) draw for each ranged leaf in `paths`.

    A mode outside its range is an error (a scenario moved the value without moving the range);
    a degenerate range (low == high) returns the mode.
    """
    paths = paths if paths is not None else ranged_leaves(p)
    ch = {}
    for path in paths:
        b = bounds(p, path)
        if b is None:
            raise ValueError(f"{path} has no numeric range")
        lo, hi = b
        mode = v(p, path)
        if not lo - 1e-12 <= mode <= hi + 1e-12:
            raise ValueError(f"{path}: value {mode} outside its range [{lo}, {hi}]")
        ch[path] = float(rng.triangular(lo, mode, hi)) if hi > lo else float(mode)
    return override(p, ch)


def guesses(p: dict, prefix: str = "") -> list[str]:
    """Leaves graded E (guesses); SCOPE's Phase B exit wants fewer than 3 in the base case."""
    out = []
    for k, node in p.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(node, dict):
            if node.get("grade") == "E":
                out.append(path)
            elif "value" not in node and "grade" not in node:
                out += guesses(node, path)
    return out
