"""Parameters: load data/pf/base.yaml, apply scenario overrides, read values, sample ranges.

A leaf is a dict with `value` (or location keys such as `us_midwest`/`eu_nw`) plus optional
`low`/`high` (triangular sampling), `unit`, `grade` and `source`. Paths are dotted, e.g.
"strain.titer_g_L". Overrides replace `value` (or a whole leaf) at a path.
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


def v(p: dict, path: str):
    """Value at a dotted path, resolving location-keyed leaves."""
    node = _leaf(p, path)
    if isinstance(node, dict):
        if "value" in node:
            return node["value"]
        loc = p.get("plant", {}).get("location", {}).get("value", "us_midwest")
        if loc in node:
            return node[loc]
        if any(k in node for k in LOCATIONS):
            return node[LOCATIONS[0]]
    return node


def grade(p: dict, path: str) -> str:
    node = _leaf(p, path)
    return node.get("grade", "") if isinstance(node, dict) else ""


def override(p: dict, changes: dict) -> dict:
    """Deep copy of p with {dotted.path: value or leaf-dict} applied."""
    q = copy.deepcopy(p)
    for path, val in changes.items():
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
                loc = q.get("plant", {}).get("location", {}).get("value", "us_midwest")
                leaf[loc] = val
        else:
            node[keys[-1]] = {"value": val}
    return q


def ranged_leaves(p: dict, prefix: str = "") -> list[str]:
    """Dotted paths of every leaf with a numeric low/high range."""
    out = []
    for k, node in p.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(node, dict):
            if "low" in node and "high" in node and isinstance(node.get("low"), (int, float)):
                out.append(path)
            elif "value" not in node:
                out += ranged_leaves(node, path)
    return out


def sample(p: dict, rng: np.random.Generator, paths: list[str] | None = None) -> dict:
    """Triangular(low, mode=value, high) draw for each ranged leaf in `paths`."""
    paths = paths if paths is not None else ranged_leaves(p)
    ch = {}
    for path in paths:
        node = _leaf(p, path)
        mode = v(p, path)
        lo, hi = node["low"], node["high"]
        mode = min(max(mode, lo), hi)
        ch[path] = float(rng.triangular(lo, mode, hi)) if hi > lo else mode
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
