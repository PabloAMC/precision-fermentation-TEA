"""Incumbent protein prices and literature titers, from the evidence files (no copied numbers).

Price per kg protein, in dollars of `money_year` (2025, like the model):
    unit value [currency / kg product] x FX [USD per EUR, ECB annual average of the same year]
    / protein fraction of the product x CPI-U(money_year) / CPI-U(year)
Trade unit values (UN Comtrade, Eurostat Comext) are official statistics but only proxies for
contract prices (prices.yaml). Series quoted per lb of product (USDA casein) carry `per: lb`. Spot quotes are USD/lb product (x 1/0.45359237 lb per kg) and are
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
    """{name: {label, compare_to: [products], series: {label: {year: $/kg protein}}, band: (lo, hi), latest, spot}}."""
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
            per = LB_PER_KG if s.get("per") == "lb" else 1.0     # USDA quotes are per lb of product
            series[s["key"]] = {int(y): float(val) * per * conv(int(y)) / pf * real(int(y)) for y, val in e["values"].items()
                                if y0 <= int(y) <= y1}
        allv = [x for s in series.values() for x in s.values()]
        latest = {k: s[max(s)] for k, s in series.items()}
        spot = [dict(label=s["label"], usd_kg_protein=ev[s["key"]]["value"] * LB_PER_KG / s["protein_frac"],
                     low=ev[s["key"]].get("low", ev[s["key"]]["value"]) * LB_PER_KG / s["protein_frac"],
                     high=ev[s["key"]].get("high", ev[s["key"]]["value"]) * LB_PER_KG / s["protein_frac"],
                     year=ev[s["key"]].get("year")) for s in c.get("spot", [])]
        cmp = c["compare_to"]
        out[name] = dict(label=c["label"], compare_to=[cmp] if isinstance(cmp, str) else list(cmp), protein_frac=pf, series=series,
                         band=(min(allv), max(allv)), years=(y0, y1), latest=latest, spot=spot, money_year=my)
    return out


def reported_prices() -> dict:
    """Price points for products with no trade code (benchmarks.yaml `reported_prices`), US$/kg.

    Each point is deflated from its year to the incumbents' money year with the CPI deflator when
    `deflate` is set (nominal values kept alongside). Returns {name: {label, compare_to, grade,
    points: [(year, low, high, key)], points_nominal, band: (lo, hi), band_nominal, comparators}}.
    """
    full = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())
    cfg, inc = full["reported_prices"], full["incumbents"]
    prices = {e["key"]: e for e in yaml.safe_load((ROOT / "data/evidence/prices.yaml").read_text())}
    cpi = {int(y): float(x) for y, x in prices[inc["deflator"]]["values"].items()}
    my = inc["money_year"]
    out = {}
    for name, c in cfg.items():
        ev = {e["key"]: e for e in yaml.safe_load((ROOT / f"data/evidence/{c['evidence']}.yaml").read_text())}
        nom = []
        for k in c["keys"]:
            e = ev[k]
            if e.get("values"):
                for y, x in e["values"].items():
                    lo, hi = (x, x) if isinstance(x, (int, float)) else x
                    nom.append((int(y), float(lo), float(hi), k))
            else:
                nom.append((e.get("year"), float(e.get("low", e["value"])), float(e.get("high", e["value"])), k))
        f = (lambda y: cpi[my] / cpi[y] if (c.get("deflate") and y in cpi) else 1.0)   # noqa: E731
        pts = [(y, lo * f(y), hi * f(y), k) for y, lo, hi, k in nom]
        comps = [dict(key=k, value=float(ev[k]["value"]), year=ev[k].get("year"), unit=ev[k]["unit"],
                      value_money_year=float(ev[k]["value"]) * f(ev[k].get("year")), deflator=f(ev[k].get("year")),
                      source=ev[k]["source"], ours=c.get("comparator_cases", {}).get(k), values=ev[k].get("values") or {})
                 for k in c.get("comparators", [])]
        out[name] = dict(label=c["label"], compare_to=c["compare_to"], grade=c["grade"], points=pts,
                         points_nominal=nom, band=(min(p[1] for p in pts), max(p[2] for p in pts)),
                         band_nominal=(min(p[1] for p in nom), max(p[2] for p in nom)), comparators=comps)
    return out


def context_prices() -> list[dict]:
    """Protein ingredients for context (benchmarks.yaml `context`): a $/kg-protein range per ingredient.

    Each row is either a reported range per kg protein (`basis: protein`, e.g. GFI 2025 ranges, nominal
    2024-2025 dollars), a range per kg product converted with a stated protein fraction
    (`basis: product`), or one of the incumbents' trade bands (`incumbent: whey|egg`, 2025 dollars).
    """
    full = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())
    ev = {e["key"]: e for e in yaml.safe_load((ROOT / "data/evidence/prices.yaml").read_text())}
    inc = None
    out = []
    for c in full.get("context", []):
        if c.get("incumbent"):
            inc = inc or incumbents()
            d = inc[c["incumbent"]]
            lo, hi, when = d["band"][0], d["band"][1], f"{d['years'][0]}-{d['years'][1]}, 2025$"
        else:
            e = ev[c["key"]]
            if c["basis"] == "protein":
                lo, hi = float(e["protein_low"]), float(e["protein_high"])
            else:
                lo, hi = float(e["low"]) / c["protein_frac"], float(e["high"]) / c["protein_frac"]
            when = c.get("when", "")
        out.append(dict(label=c["label"], lo=lo, hi=hi, when=when, grade=c["grade"], group=c.get("group", ""),
                        key=c.get("key") or c.get("incumbent"), note=c.get("note", "")))
    return out


def equivalents() -> dict:
    """Milk and egg equivalents of a protein price (benchmarks.yaml `equivalents`).

    For a source unit (a litre of milk, a large egg) holding t g of the target protein and a g of
    all protein:  cost of its target protein = MSP x t / 1000;  cost of replacing all its protein
    = MSP x a / 1000. The unit's own price, divided by a, is the protein price at which PF protein
    would cost as much as the natural source per gram of protein: an upper bound on the value
    of the protein, because fat, lactose, yolk and the rest carry part of the source's price
    (and whey is a by-product; see the report).
    Returns {name: {per, compare_to: [products], target_g: {product: g per unit}, all_protein_g,
    prices: {label: {year: $/unit}}, protein_equivalent: {label: {year: $/kg protein}}, money_year}}.
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
        out[name] = dict(per=c["per"], compare_to=list(c["compare_to"]),
                         target_g={k: float(comp[f]) for k, f in c["target_field"].items()},
                         all_protein_g=a_g, prices=prices, protein_equivalent=prot, money_year=my)
    return out


def feed_bills() -> dict:
    """The incumbent animals' feed bill and farm-gate cost per kg of edible crude protein (benchmarks.yaml `feed_bills`).

    Per animal and region, from data/evidence/feed.yaml (derived entries, grade D):
        feed  F = feed bill per kg edible protein x a,   a = share of the farm's output value that is the food
                  itself (co-products such as cull cows carry the rest; 1 where no credit is taken)
        total C = F / s,   s = feed share of the farm's total cost (feed / all costs, incl. a return on capital and
                  unpaid labour where the source counts them)
        other   = C - F    (housing, labour, young stock, energy, vets, capital: the animal's "conversion bill")
    low/high of C pair the low feed bill with the high feed share and vice versa. Nominal dollars of the
    entry's year (2025, the model's money year); low/high span other years. Farm gate: a live bird, a shell
    egg, raw milk, before slaughter, grading or processing; PF costs are ex works for a purified ingredient.
    Returns {animal: {label, regions: {location: {feed, feed_low, feed_high, share, share_low, share_high,
    alloc, total, total_low, total_high, other, year, grades, keys}}}}; share, total and other are None where
    the config gives no feed share (no comparable farm cost).
    """
    cfg = yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())["feed_bills"]
    ev = {e["key"]: e for e in yaml.safe_load((ROOT / "data/evidence/feed.yaml").read_text())}

    def num(ref):
        """(value, low, high, grade, key) of a literal {value, low, high, grade} or an evidence {key}; `pick: high`
        uses the entry's high as a point value (where it, not the central, matches the feed bill's scope)."""
        e = ev[ref["key"]] if "key" in ref else ref
        if "pick" in ref:
            x = float(e[ref["pick"]])
            return x, x, x, str(e.get("grade", "")), ref.get("key", "")
        x = float(e["value"])
        return x, float(e.get("low", x)), float(e.get("high", x)), str(e.get("grade", "")), ref.get("key", "")
    out = {}
    for name, c in cfg.items():
        regions = {}
        for loc, r in c["regions"].items():
            f, flo, fhi, gf, kf = num(r["feed"])
            a, _, _, ga, ka = num(r.get("allocation", {"value": 1.0}))   # no co-product credit by default
            d = dict(feed=f * a, feed_low=flo * a, feed_high=fhi * a, alloc=a, year=r.get("year"), share=None, total=None,
                     total_low=None, total_high=None, other=None)
            ks, gs = "", ""
            if "feed_share" in r:                                         # else: no comparable farm cost
                s, slo, shi, gs, ks = num(r["feed_share"])
                d.update(share=s, share_low=slo, share_high=shi, total=f * a / s, total_low=flo * a / shi,
                         total_high=fhi * a / slo, other=f * a / s - f * a)
            d.update(grades=dict(feed=gf, share=gs, allocation=ga), keys=[k for k in (kf, ks, ka) if k])
            regions[loc] = d
        out[name] = dict(label=c["label"], regions=regions)
    return out


def titer_markers() -> dict:
    """{product: [(titer g/L, label)]} from data/titers.csv; a marker's optional `factor` converts the reported
    titer to the model's basis (whole broth), e.g. a supernatant titer."""
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
            out[prod].append((max(vals) * m.get("factor", 1.0), m["label"]))   # factor: e.g. supernatant -> whole broth
    return out


def required_targets() -> dict:
    """{product: [target $/kg target protein]} for the required-titer analysis (benchmarks.yaml)."""
    return yaml.safe_load((ROOT / "data/pf/benchmarks.yaml").read_text())["required_targets"]


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
