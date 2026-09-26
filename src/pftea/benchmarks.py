"""Incumbent protein prices and literature titers, from the evidence files (no copied numbers).

Price per kg protein, in dollars of `money_year` (2025, like the model):
    unit value [currency / kg product] x FX [USD per EUR, ECB annual average of the same year]
    / protein fraction of the product x CPI-U(money_year) / CPI-U(year)
Trade unit values (UN Comtrade, Eurostat Comext) are official statistics but only proxies for
contract prices (prices.yaml). Spot quotes are USD/lb product (x 1/0.45359237 lb per kg) and are
kept in their own year's dollars (2026), which is stated wherever they are shown.
"""
from __future__ import annotations

import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
LB_PER_KG = 1 / 0.45359237


def _evidence() -> dict:
    return {e["key"]: e for e in yaml.safe_load((ROOT / "data/evidence/prices.yaml").read_text())}


def incumbents() -> dict:
    """{name: {label, compare_to, series: {label: {year: $/kg protein}}, band: (lo, hi), latest, spot}}."""
    cfg = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())
    ev = _evidence()
    fx = {int(y): float(x) for y, x in ev["eurusd_annual_average"]["values"].items()}
    y0, y1 = cfg["incumbents"]["years"]
    my = int(cfg["incumbents"]["money_year"])
    cpi = {int(y): float(x) for y, x in ev[cfg["incumbents"]["deflator"]]["values"].items()}
    real = lambda y: cpi[my] / cpi[y]   # noqa: E731  nominal -> money_year dollars
    out = {}
    for name, c in cfg["incumbents"].items():
        if name in ("years", "money_year", "deflator"):
            continue
        pf = c["protein_frac"]["value"]
        series = {}
        for s in c["trade_series"]:
            e = ev[s["key"]]
            conv = (lambda y: fx[y]) if s["currency"] == "EUR" else (lambda y: 1.0)
            series[s["key"]] = {int(y): float(val) * conv(int(y)) / pf * real(int(y)) for y, val in e["values"].items()
                                if y0 <= int(y) <= y1}
        allv = [x for s in series.values() for x in s.values()]
        latest = {k: s[max(s)] for k, s in series.items()}
        spot = [dict(label=s["label"], usd_kg_protein=ev[s["key"]]["value"] * LB_PER_KG / s["protein_frac"],
                     low=ev[s["key"]].get("low", ev[s["key"]]["value"]) * LB_PER_KG / s["protein_frac"],
                     high=ev[s["key"]].get("high", ev[s["key"]]["value"]) * LB_PER_KG / s["protein_frac"],
                     year=ev[s["key"]].get("year")) for s in c.get("spot", [])]
        out[name] = dict(label=c["label"], compare_to=c["compare_to"], protein_frac=pf, series=series,
                         band=(min(allv), max(allv)), years=(y0, y1), latest=latest, spot=spot, money_year=my)
    return out


def titer_markers() -> dict:
    """{product: [(titer g/L, label)]} from data/titers.csv."""
    cfg = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())["titer_markers"]
    rows = list(csv.DictReader((ROOT / "data/titers.csv").open()))
    out = {}
    for prod, marks in cfg.items():
        out[prod] = []
        for m in marks:
            vals = [float(r["titer_g_per_L"]) for r in rows if r["product"] == m["product"]
                    and r["source_key"] == m["source_key"] and r["host"] == m["host"] and r["titer_g_per_L"]]
            if not vals:
                raise KeyError(f"no titer row for {m}")
            out[prod].append((max(vals), m["label"]))
    return out


def claims() -> list[dict]:
    """Claimed titers (data/titers.csv via data/pf/benchmarks.yaml) with the host/product to model them."""
    cfg = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())["claims"]
    rows = list(csv.DictReader((ROOT / "data/titers.csv").open()))
    out = []
    for c in cfg:
        vals = [float(r["titer_g_per_L"]) for r in rows if r["product"] == c["product"]
                and r["source_key"] == c["source_key"] and r["host"] == c["host"] and r["titer_g_per_L"]]
        if not vals:
            raise KeyError(f"no titer row for {c}")
        out.append(dict(c, titer=max(vals)))
    return out


if __name__ == "__main__":
    for k, d in incumbents().items():
        print(k, d["label"], "band", [round(x, 2) for x in d["band"]], {a: round(b, 2) for a, b in d["latest"].items()},
              [(s["label"], round(s["usd_kg_protein"], 1)) for s in d["spot"]])
    print(titer_markers())
