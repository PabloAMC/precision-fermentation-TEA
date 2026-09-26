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
    out = {}
    for name in ("prices", "milk_egg"):
        out.update({e["key"]: e for e in yaml.safe_load((ROOT / f"data/evidence/{name}.yaml").read_text())})
    return out


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


def reported_prices() -> dict:
    """Price points for products with no trade code (benchmarks.yaml `reported_prices`), nominal US$/kg.

    Returns {name: {label, compare_to, grade, points: [(year or None, low, high, key)], band: (lo, hi)}}.
    """
    cfg = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())["reported_prices"]
    out = {}
    for name, c in cfg.items():
        ev = {e["key"]: e for e in yaml.safe_load((ROOT / f"data/evidence/{c['evidence']}.yaml").read_text())}
        pts = []
        for k in c["keys"]:
            e = ev[k]
            if e.get("values"):
                for y, x in e["values"].items():
                    lo, hi = (x, x) if isinstance(x, (int, float)) else x
                    pts.append((int(y), float(lo), float(hi), k))
            else:
                pts.append((e.get("year"), float(e.get("low", e["value"])), float(e.get("high", e["value"])), k))
        out[name] = dict(label=c["label"], compare_to=c["compare_to"], grade=c["grade"], points=pts,
                         band=(min(p[1] for p in pts), max(p[2] for p in pts)))
    return out


def equivalents() -> dict:
    """Milk and egg equivalents of a protein price (benchmarks.yaml `equivalents`).

    For a source unit (a litre of milk, a large egg) holding t g of the target protein and a g of
    all protein:  cost of its target protein = MSP x t / 1000;  cost of replacing all its protein
    = MSP x a / 1000. The unit's own price, divided by a, is the protein price at which PF protein
    would cost as much as the natural source per gram of protein: an upper bound on the value
    of the protein, because fat, lactose, yolk and the rest carry part of the source's price
    (and whey is a by-product; see the report).
    Returns {name: {per, compare_to, target_g, all_protein_g, prices: {label: {year: $/unit}},
    protein_equivalent: {label: {year: $/kg protein}}, money_year}}.
    """
    cfg = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())
    inc = cfg["incumbents"]
    ev = _evidence()
    comp = ev[cfg["equivalents"]["evidence_key"]]["values"]
    fx = {int(y): float(x) for y, x in ev["eurusd_annual_average"]["values"].items()}
    cpi = {int(y): float(x) for y, x in ev[inc["deflator"]]["values"].items()}
    my, (y0, y1) = int(inc["money_year"]), inc["years"]
    out = {}
    for name, c in cfg["equivalents"].items():
        if name == "evidence_key":
            continue
        rho = float(ev[c["density_key"]]["value"]) if "density_key" in c else None
        per_unit = {"usd_per_cwt": lambda x, y: x / 45.359237 * rho,        # 1 cwt = 100 lb = 45.36 kg
                    "eur_per_100kg": lambda x, y: x / 100 * rho * fx[y],
                    "usd_per_gal": lambda x, y: x / 3.785411784,            # US gallon
                    "usc_per_doz": lambda x, y: x / 100 / 12,
                    "usd_per_doz": lambda x, y: x / 12}
        a_g = float(comp[c["all_protein_field"]])
        prices, prot = {}, {}
        for s_ in c["prices"]:
            vals = ev[s_["key"]]["values"]
            series = {int(y): per_unit[s_["unit"]](float(x), int(y)) * cpi[my] / cpi[int(y)]
                      for y, x in vals.items() if str(y).isdigit() and y0 <= int(y) <= y1}
            prices[s_["label"]] = series
            prot[s_["label"]] = {y: x / a_g * 1000 for y, x in series.items()}
        out[name] = dict(per=c["per"], compare_to=c["compare_to"], target_g=float(comp[c["target_field"]]),
                         all_protein_g=a_g, prices=prices, protein_equivalent=prot, money_year=my)
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
