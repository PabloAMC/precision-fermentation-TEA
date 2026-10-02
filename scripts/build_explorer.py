"""Build docs/explorer.html: a self-contained explorer over precomputed model runs.

Reads results/explorer_grid.json (scripts/explorer_grid.py) and results/analyses.json and
injects them into a dependency-free HTML/JS/SVG page. The page only looks values up: every
number it shows is a model run, never a JavaScript re-implementation.
Run:  .venv/bin/python scripts/build_explorer.py
"""
import json
import sys

import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
arg = lambda k, d: Path(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d   # noqa: E731  (preview builds)
G = json.loads(arg("--grid", ROOT / "results/explorer_grid.json").read_text())
R = json.loads(arg("--results", ROOT / "results/analyses.json").read_text())
OUT = arg("--out", ROOT / "docs/explorer.html")

inc = R["benchmarks"]["incumbents"]
SC = R["scenarios"]
PLR = R["physical_limit"]


def case(label, d, light=None, aseptic=None, titer=None, note=""):
    return dict(label=label, titer=titer if titer is not None else d["design"]["titer"], humbird=d["msp_ccf"],
                light=light["msp_ccf"] if light else None, aseptic=aseptic["msp_ccf"] if aseptic else None, note=note)


def rows_ok(*makers):
    """Reference rows whose results exist (a preview build may run on partial results)."""
    out = []
    for mk in makers:
        try:
            out.append(mk())
        except (KeyError, TypeError):
            pass
    return out


ref = {"blg": rows_ok(
    lambda: case("Best public academic strain (Yao 2026; ethanol-fed production, priced as glucose)", SC["academic/blg"],
         SC["academic/blg/light"], SC.get("academic/blg/aseptic")),
    lambda: case("Best public titer on glucose (Li 2026)", SC["academic/blg_li2026"], SC["academic/blg_li2026/light"]),
    lambda: case("Base case (Intelligen's design point)", R["base"]["blg"], R["base_light"]["blg"], R["base_aseptic"]["blg"], titer=30.0),
    lambda: case("Industry benchmark: titer assumed in private cost models", SC["industry/blg"], SC["industry/blg/light"],
         SC.get("industry/blg/aseptic")),
    lambda: case("Physical-limit best case, 100 kt/yr (secretion at 40 mg/g/h)", PLR["blg/humbird"], PLR["blg/light"],
         PLR.get("blg/humbird/aseptic")),
    lambda: case("Same, secretion capped at 10 mg/g/h", PLR["blg/humbird/q_p_max_10"]),
    lambda: case("Same, at the best secretion demonstrated on glucose (2.1 mg/g/h)", PLR["blg/humbird/q_p_max_2.1"])),
    "ova": rows_ok(
    lambda: case("Best public academic strain (Aro 2023, T. reesei; full-length + clipped)", SC["academic/ova"],
         SC["academic/ova/light"], SC.get("academic/ova/aseptic")),
    lambda: case("Same, intact OVA only (1 g/L, judgment)", SC["academic/ova_intact_1gL"]),
    lambda: case("Base case (Intelligen's design point)", R["base"]["ova"], R["base_light"]["ova"], R["base_aseptic"]["ova"], titer=30.0),
    lambda: case("Industry benchmark: titer assumed in private cost models", SC["industry/ova"], SC["industry/ova/light"],
         SC.get("industry/ova/aseptic")),
    lambda: case("Physical-limit best case, 100 kt/yr (secretion at 40 mg/g/h)", PLR["ova/humbird"], PLR["ova/light"]),
    lambda: case("Same, at the best secretion demonstrated on glucose (2.1 mg/g/h)", PLR["ova/humbird/q_p_max_2.1"])),
    "ovd": rows_ok(
    lambda: case("Best peer-reviewed titer (Kim 2025; glycerol fed-batch, 60 h)", SC["academic/ovd"],
         SC["academic/ovd/light"], SC.get("academic/ovd/aseptic")),
    lambda: case("Best public titer (EVERY patent example, 30 g/L)", SC["academic/ovd_patent"], SC["academic/ovd_patent/light"]),
    lambda: case("Base case (Intelligen's design point), UF/DF concentrate as cleared (GRN 967)", R["base"]["ovd"],
         R["base_light"]["ovd"], R["base_aseptic"]["ovd"]),
    lambda: case("Industry benchmark: titer assumed in private cost models", SC["industry/ovd"], SC["industry/ovd/light"],
         SC.get("industry/ovd/aseptic")),
    lambda: case("Physical-limit best case, 100 kt/yr (secretion at 40 mg/g/h)", PLR["ovd/humbird"], PLR["ovd/light"]),
    lambda: case("Same, at the best secretion demonstrated on glucose (2.1 mg/g/h)", PLR["ovd/humbird/q_p_max_2.1"])),
    "cas": rows_ok(
    lambda: case("Best peer-reviewed beta-casein in K. phaffii (Choi 1996; intracellular, costed as if secreted)", SC["academic/cas"],
         SC["academic/cas/light"], SC.get("academic/cas/aseptic")),
    lambda: case("Best public casein titer (Standing Ovation patent; E. coli, intracellular)", SC["academic/cas_patent"],
         SC["academic/cas_patent/light"]),
    lambda: case("Base case (Intelligen's design point), isoelectric precipitation", R["base"]["cas"], R["base_light"]["cas"],
         R["base_aseptic"]["cas"]),
    lambda: case("Same, UF/DF only (Eden Brew; ~6% beta-casein in the powder)", R["casein"]["cases"]["cas_ufdf_edenbrew/humbird"],
         R["casein"]["cases"]["cas_ufdf_edenbrew/light"]),
    lambda: case("Industry benchmark: titer assumed in private cost models", SC["industry/cas"], SC["industry/cas/light"],
         SC.get("industry/cas/aseptic")),
    lambda: case("Physical-limit best case, 100 kt/yr (secretion at 40 mg/g/h)", PLR["cas/humbird"], PLR["cas/light"]),
    lambda: case("Same, at the best secretion demonstrated on glucose (2.1 mg/g/h)", PLR["cas/humbird/q_p_max_2.1"])),
    "lf": rows_ok(
    lambda: case("Design titer, cation exchange (Intelligen's design)", R["base"]["lf"],
         R["base_light"]["lf"], R["base_aseptic"]["lf"]),
    lambda: case("Design titer, UF/DF only (optimistic)", R["lactoferrin"]["cases"]["lf_ufdf_only/humbird"],
         R["lactoferrin"]["cases"]["lf_ufdf_only/light"]),
    lambda: case("Best public methanol-free titer (porcine LF, Yen 2024)", SC["academic/lf"],
         SC["academic/lf/light"], SC.get("academic/lf/aseptic")),
    lambda: case("Best public secreted titer (human LF, Lv 2023; methanol, ELISA)", SC["academic/lf_lv2023"],
         SC["academic/lf_lv2023/light"]),
    lambda: case("Industry benchmark: titer assumed in private cost models", SC["industry/lf"], SC["industry/lf/light"],
         SC.get("industry/lf/aseptic")),
    lambda: case("Physical-limit best case, 1.6 kt/yr (secretion at 40 mg/g/h)", PLR["lf/humbird"], PLR["lf/light"]),
    lambda: case("Same, at the best secretion demonstrated on glucose (2.1 mg/g/h)", PLR["lf/humbird/q_p_max_2.1"])),
    "alb": rows_ok(
    lambda: case("Best public rHSA titer (Zhu 2021; 8.7 g/L of whole broth, 17.5 of supernatant, after 192 h of methanol induction)", SC["academic/alb"],
         SC["academic/alb/light"], SC.get("academic/alb/aseptic")),
    lambda: case("Zhu 2018 (about 4.4 g/L of whole broth after 96 h of methanol induction)", SC["academic/alb_zhu2018"], SC["academic/alb_zhu2018/light"]),
    lambda: case("Best methanol-free titer (Delta/Recombumin patent, S. cerevisiae, 1.5 g/L)", SC["academic/alb_patent"],
         SC["academic/alb_patent/light"]),
    lambda: case("Base case (Intelligen's design point), cation exchange + anion-exchange polish, 1 kt/yr", R["base"]["alb"],
         R["base_light"]["alb"], R["base_aseptic"]["alb"]),
    lambda: case("Same, cation-exchange capture only (optimistic)", R["albumin"]["cases"]["alb_capture_only/humbird"],
         R["albumin"]["cases"]["alb_capture_only/light"]),
    lambda: case("Same, methanol-induced production phase", R["albumin"]["cases"]["alb_methanol/humbird"],
         R["albumin"]["cases"]["alb_methanol/light"]),
    lambda: case("Same, UF/DF only (77% albumin, below the cell-culture spec)", R["albumin"]["cases"]["alb_ufdf_only/humbird"],
         R["albumin"]["cases"]["alb_ufdf_only/light"]),
    lambda: case("Industry benchmark: titer assumed in private cost models", SC["industry/alb"], SC["industry/alb/light"],
         SC.get("industry/alb/aseptic")),
    lambda: case("Physical-limit best case, 100 kt/yr (secretion at 40 mg/g/h)", PLR["alb/humbird"], PLR["alb/light"]),
    lambda: case("Same, at the best secretion demonstrated on glucose (2.1 mg/g/h)", PLR["alb/humbird/q_p_max_2.1"]))}
PRODS = list(R["base"])                       # products in results order (data/pf/products.yaml)
if list(G["axes"]["product"]) != PRODS:          # a stale grid would mislabel products silently (audit R11-10)
    sys.exit(f"explorer grid products {G['axes']['product']} != results products {PRODS}: rerun scripts/explorer_grid.py")
# each product's base point on the grid: its base-case titer and production time (lactoferrin 10 g/L, 83 h)
_base = yaml.safe_load((ROOT / "data/pf/base.yaml").read_text())["strain"]
_prod = yaml.safe_load((ROOT / "data/pf/products.yaml").read_text())
BASE_POINT = {p: dict(titer=(_prod.get(p) or {}).get("strain.titer_g_L", {}).get("value", _base["titer_g_L"]["value"]),
                      t_prod=(_prod.get(p) or {}).get("strain.t_prod_h", {}).get("value", _base["t_prod_h"]["value"]))
              for p in PRODS}
NAMES = {"blg": "&beta;-lactoglobulin", "ova": "Ovalbumin", "ovd": "Ovomucoid", "cas": "&beta;-casein", "lf": "Lactoferrin", "alb": "Serum albumin"}
LFP = R.get("lactoferrin", {}).get("reported_prices", {"band": [0, 0], "points": []})
SERIES_LABEL = {"whey_protein_gt80_us_export_unit_value": "US exports", "whey_protein_gt80_eu_export_unit_value": "EU exports",
                "egg_albumin_dried_eu_export_unit_value": "EU exports", "casein_food_eu_export_unit_value": "EU exports",
                "casein_acid_us_dmn_annual": "US imports, acid casein", "casein_rennet_us_dmn_annual": "US imports, rennet casein"}
MKT_LABEL = {"whey": "Whey protein (WPC80/WPI)", "egg": "Dried egg white", "casein": "Casein (acid, rennet, caseinates)"}
market = {}
for name, d in inc.items():
    spot = [dict(label=f"{x['label']} (USDA)", year=x.get("year"), value=x["usd_kg_protein"]) for x in d["spot"][:1]]
    for prod in d["compare_to"]:
        market[prod] = dict(label=MKT_LABEL.get(name, d["label"]), frac=d["protein_frac"],
                            series=[dict(label=SERIES_LABEL.get(k, k), pts=v) for k, v in d["series"].items()],
                            spot=spot, band=d["band"], years=d["years"])


def reported_market(key, label, rp, comparators=()):
    """A market entry from reported price points (benchmarks.reported_prices): per-year low and high."""
    lo_, hi_ = {}, {}
    for y, lo, hi, _ in rp["points"]:
        if y:
            lo_[y], hi_[y] = min(lo, lo_.get(y, lo)), max(hi, hi_.get(y, hi))
    yrs = sorted(lo_)
    market[key] = dict(label=label, frac=1.0,     # reported per kg of product, read as per kg protein (as in the report)
                       series=[dict(label="reported low", pts={str(y): lo_[y] for y in yrs}),
                               dict(label="reported high", pts={str(y): hi_[y] for y in yrs})],
                       spot=[], band=rp["band"], years=[yrs[0], yrs[-1]] if yrs else [2013, 2025],
                       comparators=list(comparators))


if "lf" in PRODS:
    reported_market("lf", "Dairy lactoferrin (reports and trade press, grade C)", LFP,
                    [dict(label="Intelligen's model, " + {"lf": "cation exchange", "lf_ufdf_only": "UF/DF only"}[c["ours"]],
                          value=c["value_money_year"],
                          ours=R["lactoferrin"].get("reconciliation", {}).get(c["ours"], {}).get("cop"))
                     for c in LFP.get("comparators", []) if c.get("ours")])
if "alb" in PRODS:
    reported_market("alb", "Bulk serum albumin (technical BSA trade values, grade C)", R["albumin"]["reported_prices"])
powder_frac = {p: R["base"][p]["per_kg_powder"] / R["base"][p]["msp_ccf"] for p in PRODS}
EQ = R["equivalents"]["sources"]


def src_band(name, label):
    ser = EQ[name]["prices"][label]
    yr = max(ser, key=int)
    return dict(label=label, lo=min(ser.values()), hi=max(ser.values()), last=ser[yr], year=int(yr), pts=ser)


EQ_BANDS = {"milk": ["US farm milk (all-milk price)", "US retail whole milk"],
            "egg": ["US wholesale eggs (New York, Grade A large)", "US retail eggs (Grade A large)"]}
EQ_WHAT = {"milk": ("litre of milk", "all the protein in a litre of milk"), "egg": ("egg", "the egg-white protein of one large egg")}
equiv = {}
for name, src in EQ.items():
    for prod in src["compare_to"]:
        equiv[prod] = dict(per=EQ_WHAT[name][0], grams=src["all_protein_g"], what=EQ_WHAT[name][1],
                           bands=[src_band(name, b) for b in EQ_BANDS[name]])

DATA = {
    "grid": G,
    "products": PRODS,
    "base_point": BASE_POINT,
    "bands": {p: dict(label=m["label"], lo=m["band"][0], hi=m["band"][1], years=m["years"],
                      spot=m["spot"][0]["value"] if m["spot"] else None) for p, m in market.items()},
    "ceiling": {p: dict(zip(map(str, R["required_t_prods"]), R["titer_ceiling"][p])) for p in PRODS},
    "equiv": equiv,
    "scale_t": {p: round(R["base"][p]["design"]["n_batches"] * R["base"][p]["design"]["target_per_batch_kg"] / 1000) for p in PRODS},
    "ref": ref,
    "market": market,
    "context": R["benchmarks"].get("context", []),
    "powder_frac": powder_frac,
    "generated": R["generated"],
}
PROD_RADIOS = "\n".join(f'            <input type="radio" name="product" id="p-{k}" value="{i}"{" checked" if i == 0 else ""}>'
                        f'<label for="p-{k}">{NAMES.get(k, k)}</label>' for i, k in enumerate(PRODS))
REF_RADIOS = "\n".join(f'        <input type="radio" name="refp" id="r-{k}" value="{k}"{" checked" if i == 0 else ""}>'
                       f'<label for="r-{k}">{NAMES.get(k, k)}</label>' for i, k in enumerate(PRODS))

HTML = r"""<title>Precision Fermentation Cost Explorer</title>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root {
  --bg: #f4f6f4; --surface: #fcfcfb; --ink: #111513; --ink-2: #4b534e; --muted: #7b837e;
  --rule: #dde2dd; --grid: #e6e9e5; --axis: #c3c8c3;
  --accent: #1d6a86; --accent-soft: #e2eef3; --accent-ink: #ffffff;
  --band-blg: #e3edf9; --band-ova: #fbe6dc; --band-ovd: #fbe6dc; --band-cas: #e6f4ec; --band-lf: #efe9f7; --spot: #898781;
  --good: #0a7d0a; --good-bg: #e5f3e5; --bad: #b3322f; --bad-bg: #f8e4e3; --warn: #9a5a0c; --warn-bg: #fbeedd;
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4; --s6: #008300;
  --shadow: 0 1px 2px rgba(17, 21, 19, .06);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #0e1110; --surface: #171a19; --ink: #f1f4f2; --ink-2: #c3c9c5; --muted: #8b928d;
    --rule: #2a302d; --grid: #242927; --axis: #383d3a;
    --accent: #62b3d2; --accent-soft: #1b2e36; --accent-ink: #0e1110;
    --band-blg: #1b293a; --band-ova: #38251d; --band-ovd: #38251d; --band-cas: #1d3328; --band-lf: #2e2639; --spot: #9a9f9b;
    --good: #5cc45c; --good-bg: #16261a; --bad: #ef7a77; --bad-bg: #331a1a; --warn: #f0a85a; --warn-bg: #33261a;
    --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #008300;
    --shadow: none;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0e1110; --surface: #171a19; --ink: #f1f4f2; --ink-2: #c3c9c5; --muted: #8b928d;
  --rule: #2a302d; --grid: #242927; --axis: #383d3a;
  --accent: #62b3d2; --accent-soft: #1b2e36; --accent-ink: #0e1110;
  --band-blg: #1b293a; --band-ova: #38251d; --band-ovd: #38251d; --band-cas: #1d3328; --band-lf: #2e2639; --spot: #9a9f9b;
  --good: #5cc45c; --good-bg: #16261a; --bad: #ef7a77; --bad-bg: #331a1a; --warn: #f0a85a; --warn-bg: #33261a;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --s6: #008300;
  --shadow: none;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 15px/1.5 "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif; }
.wrap { max-width: 1120px; margin: 0 auto; padding-inline: 20px; padding-block: 28px 48px; }
h1 { font: 600 clamp(26px, 4vw, 34px)/1.1 "IBM Plex Sans Condensed", "IBM Plex Sans", system-ui, sans-serif; margin: 0; text-wrap: balance; letter-spacing: -0.01em; }
h2 { font: 600 13px/1.3 "IBM Plex Sans", system-ui, sans-serif; text-transform: uppercase; letter-spacing: .08em; color: var(--ink-2); margin: 0 0 10px; }
p { margin: 0; }
.lede { color: var(--ink-2); max-width: 68ch; margin-top: 8px; }
.num { font-family: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace; font-variant-numeric: tabular-nums; }
header { display: grid; gap: 4px; margin-bottom: 22px; }
.summary { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 16px; margin-bottom: 18px; }
.panel { background: var(--surface); border: 1px solid var(--rule); border-radius: 10px; padding: 18px; box-shadow: var(--shadow); min-width: 0; }
.price { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; }
.price .big { font: 600 clamp(44px, 7vw, 64px)/1 "IBM Plex Sans Condensed", "IBM Plex Sans", sans-serif; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
.price .unit { color: var(--ink-2); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px; font-size: 13px; font-weight: 500; border: 1px solid transparent; }
.chip.good { color: var(--good); background: var(--good-bg); }
.chip.bad { color: var(--bad); background: var(--bad-bg); }
.chip.warn { color: var(--warn); background: var(--warn-bg); }
.chip.plain { color: var(--ink-2); background: transparent; border-color: var(--rule); }
.chip svg { width: 14px; height: 14px; flex: none; }
.compare { display: grid; gap: 10px; align-content: start; }
.compare .row { display: grid; grid-template-columns: 1fr auto; gap: 12px; align-items: baseline; border-bottom: 1px dashed var(--rule); padding-bottom: 8px; }
.compare .row:last-child { border-bottom: 0; padding-bottom: 0; }
.compare .k { color: var(--ink-2); font-size: 14px; }
.compare .v { font-weight: 500; }
.main { display: grid; grid-template-columns: minmax(0, 330px) minmax(0, 1fr); gap: 16px; align-items: start; }
form { display: grid; gap: 18px; }
fieldset { border: 0; padding: 0; margin: 0; display: grid; gap: 8px; min-width: 0; }
legend { font-size: 13px; font-weight: 600; color: var(--ink-2); margin-bottom: 6px; padding: 0; }
.seg { display: grid; grid-auto-flow: column; grid-auto-columns: 1fr; border: 1px solid var(--rule); border-radius: 8px; overflow: hidden; }
.seg input { position: absolute; opacity: 0; pointer-events: none; }
.seg label { text-align: center; padding: 7px 6px; font-size: 14px; cursor: pointer; color: var(--ink-2); border-left: 1px solid var(--rule); user-select: none; }
.seg label:first-of-type { border-left: 0; }
.seg input:checked + label { background: var(--accent); color: var(--accent-ink); font-weight: 500; }
.seg input:focus-visible + label { outline: 2px solid var(--accent); outline-offset: -3px; }
.slider { display: grid; gap: 4px; }
.slider .top { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.slider label { font-size: 14px; color: var(--ink); }
.slider output { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 14px; color: var(--accent); font-weight: 500; }
.slider .ticks { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); font-family: "IBM Plex Mono", ui-monospace, monospace; }
input[type=range] { width: 100%; accent-color: var(--accent); margin: 0; }
input[type=range]:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 4px; }
.hint { font-size: 12.5px; color: var(--muted); }
.charts { display: grid; gap: 16px; min-width: 0; }
.chart-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 6px 14px; margin-bottom: 6px; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 12.5px; color: var(--ink-2); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.sw { width: 12px; height: 12px; border-radius: 3px; flex: none; display: inline-block; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex: none; display: inline-block; }
svg.chart { width: 100%; height: auto; display: block; overflow: visible; }
svg.chart text { font-family: "IBM Plex Sans", system-ui, sans-serif; font-size: 11px; fill: var(--muted); }
svg.chart .lbl { fill: var(--ink-2); }
.tip { position: absolute; pointer-events: none; background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; padding: 6px 9px; font-size: 12.5px; box-shadow: 0 4px 14px rgba(0,0,0,.12); white-space: nowrap; }
.chartbox { position: relative; }
.bar { display: flex; height: 26px; border-radius: 5px; overflow: hidden; gap: 2px; background: var(--surface); }
.bar div { min-width: 2px; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--rule); }
th { font-size: 12px; font-weight: 600; color: var(--ink-2); text-transform: uppercase; letter-spacing: .06em; }
td.r, th.r { text-align: right; font-family: "IBM Plex Mono", ui-monospace, monospace; font-variant-numeric: tabular-nums; }
.tablewrap { overflow-x: auto; }
details { margin-top: 10px; }
summary { cursor: pointer; color: var(--accent); font-size: 13.5px; }
summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.notes { margin-top: 18px; display: grid; gap: 8px; color: var(--ink-2); font-size: 13.5px; max-width: 80ch; }
.yourprice { display: grid; gap: 6px; border-top: 1px solid var(--rule); padding-top: 10px; }
.yourprice label { font-size: 14px; color: var(--ink-2); }
.yourprice .in { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.yourprice input { width: 7.5em; font: 500 15px "IBM Plex Mono", ui-monospace, monospace; padding: 5px 8px; border: 1px solid var(--rule); border-radius: 6px; background: var(--surface); color: var(--ink); }
.yourprice input:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
.yourprice output { font-size: 14px; }
.panel-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px 16px; margin-bottom: 10px; }
.panel-head h2 { margin: 0; }
.seg.small label { padding: 5px 10px; font-size: 13px; }
tr.mkt td { color: var(--ink-2); background: var(--accent-soft); }
.notes b { color: var(--ink); font-weight: 600; }
@media (max-width: 860px) {
  .summary, .main { grid-template-columns: minmax(0, 1fr); }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap">
  <header>
    <h1>Precision Fermentation Cost Explorer</h1>
    <p class="lede">Food-grade &beta;-lactoglobulin (the main whey protein), ovalbumin and ovomucoid (egg-white proteins), &beta;-casein
    (the main cheese protein), lactoferrin, and serum albumin for cultivated-meat growth media, made by a secreting <i>K.&nbsp;phaffii</i>
    strain in fed-batch fermenters of up to 200&nbsp;m&sup3; and dried: 10&nbsp;kt of protein a year (lactoferrin 250&nbsp;t, the size of its market;
    albumin 1&nbsp;kt). Each protein has its own purification: membranes for BLG, ovalbumin and ovomucoid, isoelectric precipitation for casein,
    cation exchange for lactoferrin and albumin.
    Move the strain levers and see the minimum selling price, whether a real fermenter can run the design, and how the price compares with whey, egg white, casein, lactoferrin, bulk albumin, milk and eggs.</p>
  </header>

  <section class="summary" aria-live="polite">
    <div class="panel">
      <h2>Minimum selling price</h2>
      <div class="price"><span class="big num" id="msp">$0</span><span class="unit" id="msp-unit">per kg protein, 2025 dollars</span></div>
      <div class="chips" id="chips"></div>
    </div>
    <div class="panel compare">
      <h2 style="margin:0 0 2px" id="compare-h">Against the market</h2>
      <div class="compare" id="compare"></div>
      <div class="yourprice">
        <label for="yourprice">Have a price in mind? Enter it to see the titer this design would need to reach it.</label>
        <div class="in"><span class="num" id="yp-cur">$</span><input id="yourprice" type="number" inputmode="decimal" min="0" step="any" placeholder="e.g. 12"><span class="hint" id="yp-unit">per kg protein</span></div>
        <output id="yp-out" class="hint" aria-live="polite"></output>
      </div>
    </div>
  </section>

  <section class="main">
    <div class="panel">
      <form id="controls" onsubmit="return false">
        <fieldset>
          <legend>Protein</legend>
          <div class="seg" role="radiogroup">
__PRODRADIOS__
          </div>
        </fieldset>
        <fieldset>
          <legend>Capital estimate</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="convention" id="c-h" value="0" checked><label for="c-h">Price-anchored (base)</label>
            <input type="radio" name="convention" id="c-l" value="1"><label for="c-l">Design-report</label>
            <input type="radio" name="convention" id="c-a" value="2"><label for="c-a">Aseptic vessels</label>
          </div>
          <p class="hint">Price-anchored (base): industrial fermenters at a vendor quote, with Humbird's facility factors and fixed costs (9% of investment a year); with the same factors his baker's-yeast workbook lands in the market-implied cost band. Design-report: NREL's installation factors and fixed costs under 2% a year, as in NREL-style design reports. Aseptic vessels: the base with Humbird's cell-culture-grade fermenter prices, about 2.9 times the vendor quote (a high case).</p>
        </fieldset>
        <fieldset>
          <legend>Show the price</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="unit" id="u-kg" value="0" checked><label for="u-kg">per kg protein</label>
            <input type="radio" name="unit" id="u-pow" value="2"><label for="u-pow">per kg powder</label>
            <input type="radio" name="unit" id="u-src" value="1"><label for="u-src" id="u-src-l">per litre of milk</label>
          </div>
          <p class="hint" id="u-hint"></p>
        </fieldset>
        <fieldset>
          <legend>Plant site</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="site" id="s-us" value="0" checked><label for="s-us">US Midwest</label>
            <input type="radio" name="site" id="s-eu" value="1"><label for="s-eu">North-west Europe</label>
          </div>
        </fieldset>
        <fieldset>
          <legend>Strain performance</legend>
          <div class="slider"><div class="top"><label for="titer">Titer at harvest</label><output id="o-titer" for="titer"></output></div>
            <input type="range" id="titer" min="0" max="10" step="1"><div class="ticks" id="t-titer"></div></div>
          <div class="slider"><div class="top"><label for="t_prod">Production phase</label><output id="o-t_prod" for="t_prod"></output></div>
            <input type="range" id="t_prod" min="0" max="5" step="1"><div class="ticks" id="t-t_prod"></div></div>
          <div class="slider"><div class="top"><label for="X_prod">Cell density in production</label><output id="o-X_prod" for="X_prod"></output></div>
            <input type="range" id="X_prod" min="0" max="2" step="1"><div class="ticks" id="t-X_prod"></div></div>
          <div class="slider"><div class="top"><label for="Y_ps">Product yield on glucose</label><output id="o-Y_ps" for="Y_ps"></output></div>
            <input type="range" id="Y_ps" min="0" max="2" step="1"><div class="ticks" id="t-Y_ps"></div></div>
          <p class="hint">Sliders step through the values that were run through the full model. Everything else stays at the base case.</p>
        </fieldset>
        <button type="button" id="reset" class="chip plain" style="justify-self:start;cursor:pointer;font:inherit;font-size:13px">Reset to base case</button>
      </form>
    </div>

    <div class="charts">
      <div class="panel">
        <div class="chart-head"><h2 style="margin:0">Price against titer, other levers as set</h2>
          <div class="legend">
            <span><i class="dot" style="background:var(--accent)"></i>achievable</span>
            <span><i class="dot" style="border:2px solid var(--bad);background:transparent"></i>breaks a physical limit</span>
            <span><i class="sw" id="band-sw"></i><span id="band-lg"></span></span>
          </div>
        </div>
        <div class="chartbox" id="chartbox"><svg class="chart" id="chart" viewBox="0 0 640 300" role="img" aria-label="Minimum selling price against titer"></svg><div class="tip" id="tip" hidden></div></div>
        <details><summary>Show the numbers behind the chart</summary><div class="tablewrap"><table id="chart-table"></table></div></details>
      </div>
      <div class="panel">
        <div class="chart-head"><h2 style="margin:0" id="mkt-h">Market prices by year, and this design</h2>
          <div class="legend" id="mkt-legend"></div>
        </div>
        <div class="chartbox"><svg class="chart" id="mkt" viewBox="0 0 640 260" role="img" aria-label="Market prices by year against this design's cost"></svg></div>
        <p class="hint" id="mkt-note"></p>
        <details><summary>Show the market prices</summary><div class="tablewrap"><table id="mkt-table"></table></div></details>
        <details><summary>Other protein ingredients, for context</summary><div class="tablewrap"><table id="ctx-table"></table></div>
          <p class="hint" style="margin-top:6px">$ per kg protein. Export unit values: 2015–2025 in 2025 dollars. GFI 2025 ranges: nominal, about 2024–2025 (industry data, grade C).</p></details>
      </div>
      <div class="panel">
        <h2>What the price is made of</h2>
        <div class="bar" id="bar" aria-hidden="true"></div>
        <div class="tablewrap" style="margin-top:10px"><table id="breakdown"></table></div>
      </div>
    </div>
  </section>

  <section class="panel" style="margin-top:16px">
    <div class="panel-head"><h2>Reference cases from the report</h2>
      <div class="seg small" role="radiogroup" aria-label="Protein shown in the table">
__REFRADIOS__
      </div>
    </div>
    <div class="tablewrap"><table id="ref"></table></div>
    <p class="hint" id="ref-note" style="margin-top:8px"></p>
  </section>

  <section class="notes">
    <p><b>What this is.</b> A cost with a capital charge of 14.6% of investment a year (7.5% over 10 years), not a market price. It excludes R&amp;D, licences, regulatory work, sales and first-of-a-kind premiums.</p>
    <p><b>Limits.</b> A 200&nbsp;m&sup3; fermenter transfers at most 200&nbsp;mol&nbsp;O&#8322; per m&sup3; of cell-free liquid per hour (about 130 per m&sup3; of broth at the base cell density; Humbird's air-sparged value) and removes at most 25&nbsp;kW/m&sup3; of heat; a batch must start at least 30% full, with glucose fed at 500&nbsp;g/L; and cells secrete at most 40&nbsp;mg of protein per gram per hour, a judgment about 8 times the base design and above any published <i>K.&nbsp;phaffii</i> value. A design that breaks any of these is marked; its price is shown but cannot be achieved as designed. The minimum fill and the feed concentration are design choices: with a 600&nbsp;g/L feed the ceiling rises (report, Q3).</p>
    <p><b>Market prices.</b> Export unit values from UN&nbsp;Comtrade and Eurostat, deflated to 2025 dollars. Per kg of protein they assume 80% protein for whey (the minimum for its trade code; more isolate in the mix would lower the per-protein price) and 81.1% for egg white; "per kg powder" compares the same export prices per kg of product with our powder's cost per kg. The 2026 whey spot is from USDA Dairy Market News narrative quotes. Lactoferrin prices are reported ranges (trade press and reports, grade C). Our figures are production costs with a return on capital, not selling prices: a seller would add margin, sales and distribution.</p>
    <p><b>Milk and egg equivalents.</b> The price of replacing the protein of a litre of milk (33.7&nbsp;g) or of one egg's white (3.64&nbsp;g) with PF protein, beside what the litre or the egg costs. This flatters PF: charging the whole price of milk or eggs to their protein makes them look dearer per gram, when fat, lactose and yolk carry part of that price. The same egg white bought as dried egg white cost __EGGWHITE__ in 2015–2025, and a litre's whey protein bought as WPC80/WPI __WHEYSHARE__ of the farm milk price in the same year.</p>
    <p class="hint" id="gen"></p>
  </section>
</div>

<script>
const D = __DATA__;
const G = D.grid, AX = G.axes, ORDER = G.order;
const LABELS = {product: D.products, convention: ["humbird", "light", "aseptic"], site: ["us_midwest", "eu_nw"]};
const BASE = {product: 0, convention: 0, site: 0, titer: AX.titer.indexOf(30), t_prod: AX.t_prod.indexOf(72), X_prod: AX.X_prod.indexOf(107), Y_ps: AX.Y_ps.indexOf(0.465)};
// each product's own base point (lactoferrin: 10 g/L, 83 h); falls back to 30 g/L, 72 h if not on the grid
const baseFor = i => { const bp = D.base_point[D.products[i]] || {}, ti = AX.titer.indexOf(bp.titer), tp = AX.t_prod.indexOf(bp.t_prod);
  return Object.assign({}, BASE, {product: i}, ti >= 0 ? {titer: ti} : {}, tp >= 0 ? {t_prod: tp} : {}); };
let S = baseFor(0);
let UNIT = 0;   // 0: $/kg protein; 1: per litre of milk (BLG) or per egg (OVA); 2: per kg powder
let REFP = "blg";   // protein shown in the reference table
const EQV = () => D.equiv[prodKey()] || null;   // lactoferrin has no milk or egg unit
const MKT = () => D.market[prodKey()];
// model cost ($/kg protein) -> the unit shown; market price ($/kg protein) -> the unit shown
const conv = () => UNIT === 1 ? EQV().grams / 1000 : UNIT === 2 ? D.powder_frac[prodKey()] : 1;
const mconv = () => UNIT === 2 ? MKT().frac : 1;
const unitWord = () => UNIT === 1 ? "per " + EQV().per : UNIT === 2 ? "per kg powder" : "per kg protein";
const fmtU = x => x < 1 ? "$" + x.toFixed(3) : money(x);      // a value already in the shown unit
const moneyU = (x, d) => UNIT === 0 ? money(x, d) : fmtU(x * conv());
function marketNow() {
  // the incumbent's prices in the shown unit: ingredient export prices, or milk and egg prices (per unit)
  if (UNIT === 1) {
    const e = EQV();
    return {label: e.bands[0].label, series: e.bands.map(b => ({label: b.label, pts: b.pts})), spot: [],
            band: [e.bands[0].lo, e.bands[0].hi], years: [2015, e.bands[0].year]};
  }
  const m = MKT(), k = mconv();
  const sc = pts => Object.fromEntries(Object.entries(pts).map(([y, x]) => [y, x * k]));
  return {label: m.label, series: m.series.map(s => ({label: s.label, pts: sc(s.pts)})),
          spot: m.spot.map(p => Object.assign({}, p, {value: p.value * k})), band: [m.band[0] * k, m.band[1] * k], years: m.years};
}
const feasible = f => f === 0 || f === 2;
function titerFor(price) {
  // titer at which this design (other levers as set) reaches `price` (shown unit): log-log interpolation on the grid
  const k = conv();
  const pts = AX.titer.map((t, i) => { const v = at(Object.assign({}, S, {titer: i})); return v ? {t, v: v[0] * k, f: v[1]} : null; }).filter(Boolean);
  if (!pts.length || !(price > 0)) return null;
  if (pts[0].v <= price) return {t: pts[0].t, ok: feasible(pts[0].f), first: true};
  for (let j = 1; j < pts.length; j++) {
    if (pts[j].v <= price) {
      const a = pts[j - 1], b = pts[j], w = (Math.log(a.v) - Math.log(price)) / (Math.log(a.v) - Math.log(b.v));
      return {t: Math.exp(Math.log(a.t) + w * (Math.log(b.t) - Math.log(a.t))), ok: feasible(a.f) && feasible(b.f)};
    }
  }
  return null;
}
function titerText(r, price) {
  if (!r) return `Not reached below ${AX.titer[AX.titer.length - 1]} g/L with these settings.`;
  if (r.first) return `Already below ${fmtU(price)} at ${r.t} g/L, the lowest titer shown.`;
  return `About ${r.t < 10 ? r.t.toFixed(1) : Math.round(r.t)} g/L with these settings` +
    (r.ok ? ", which a 200 m³ fermenter can run." : ", beyond what the fermenter can run with these settings.");
}
const SERIES = ["--s1", "--s2", "--s3", "--s4", "--s5", "--s6"];
const FLAG = {
  0: ["good", "Achievable in a 200 m³ fermenter", "M3 8l3 3 7-7"],
  1: ["bad", "Breaks a physical limit (O₂, heat, fill or productivity)", "M4 4l8 8M12 4l-8 8"],
  2: ["warn", "Above an assumed solubility", "M8 3v6M8 12v1"],
  3: ["bad", "Yield above the energetic ceiling", "M4 4l8 8M12 4l-8 8"],
};
const $ = id => document.getElementById(id);
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const money = (x, d) => "$" + (x >= 100 ? Math.round(x).toLocaleString("en-US") : x.toFixed(d === undefined ? (x < 10 ? 2 : 1) : d));

function at(sel) {
  let k = 0;
  for (const a of ORDER) k = k * AX[a].length + sel[a];
  return G.values[k];
}
const prodKey = () => LABELS.product[S.product];

function fmtAxis(a, v) {
  if (a === "titer") return v + " g/L";
  if (a === "t_prod") return v + " h";
  if (a === "X_prod") return v + " g/L";
  if (a === "Y_ps") return v.toFixed(2) + " g/g";
  return String(v);
}

function chip(flag) {
  const f = FLAG[flag];
  return `<span class="chip ${f[0]}"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="${f[2]}" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/></svg>${f[1]}</span>`;
}

function render() {
  const hasEq = !!EQV();                       // the per-litre/per-egg unit exists for this protein?
  $("u-src").disabled = !hasEq;
  if (!hasEq && UNIT === 1) { UNIT = 0; $("u-kg").checked = true; }
  for (const a of ["titer", "t_prod", "X_prod", "Y_ps"]) { $(a).value = S[a]; $("o-" + a).textContent = fmtAxis(a, AX[a][S[a]]); }
  const v = at(S);
  const band = D.bands[prodKey()];
  const chips = [];
  if (!v) {
    $("msp").textContent = "n/a";
    chips.push(`<span class="chip plain">The model found no working batch at these settings</span>`);
  } else {
    $("msp").textContent = moneyU(v[0]);
    chips.push(chip(v[1]));
    const tp = AX.t_prod[S.t_prod], ceil = D.ceiling[prodKey()][String(tp)];
    if (ceil && AX.X_prod[S.X_prod] === 107 && AX.Y_ps[S.Y_ps] === 0.465) chips.push(`<span class="chip plain">Feasibility ceiling at ${tp} h: about ${Math.round(ceil)} g/L</span>`);
  }
  $("chips").innerHTML = chips.join("");
  const eq = EQV() || {per: "litre of milk", what: "", grams: 0, bands: []};
  $("msp-unit").textContent = UNIT === 1 ? `per ${eq.per} (PF protein replacing ${eq.what}), 2025 dollars`
    : UNIT === 2 ? "per kg of powder, 2025 dollars" : "per kg protein, 2025 dollars";
  $("u-src-l").textContent = "per " + eq.per;
  $("u-hint").textContent = UNIT === 1 ? `Multiplies $/kg by ${eq.grams.toFixed(2)} g / 1000.`
    : UNIT === 2 ? `Our powder is ${Math.round(100 * D.powder_frac[prodKey()])}% target protein; market prices per kg of product (${Math.round(100 * MKT().frac)}% protein).` : "";
  // comparison panel: in the shown unit throughout
  const base = at(Object.assign({}, baseFor(S.product), {convention: S.convention, site: S.site}));
  const mk = marketNow(), rows = [];
  if (v) {
    const cur = v[0] * conv(), [lo, hi] = mk.band;
    const pos = cur < lo ? "below the whole range" : cur <= hi ? "inside the range" : cur < 1.05 * hi ? "at the top edge of the range" : (cur / hi).toFixed(1) + "× the top of the range";
    if (UNIT === 1) {
      for (const b of eq.bands) rows.push([`${b.label}, ${b.year} (2015–${b.year} range)`, `$${b.last.toFixed(2)} ($${b.lo.toFixed(2)}–${b.hi.toFixed(2)})`]);
      rows.push(["This design", fmtU(cur)]);
    } else {
      const all = mk.series.flatMap(s => Object.values(s.pts));
      const avg = all.reduce((a, b) => a + b, 0) / all.length;
      rows.push([`${mk.label}, ${mk.years[0]}–${mk.years[1]} market prices`, `${fmtU(lo)}–${fmtU(hi)}`]);
      rows.push(["This design", pos]);
      rows.push(["Years this design would have been cheaper", `${all.filter(p => p >= cur).length} of ${all.length} annual prices`]);
      for (const p of mk.spot) rows.push([p.label, fmtU(p.value) + (cur <= p.value ? ", undercut" : ", not reached")]);
      const r = titerFor(avg);
      rows.push([`Titer to match the ${mk.years[0]}–${mk.years[1]} average (${fmtU(avg)})`,
                 r ? (r.first ? `≤ ${r.t} g/L` : `${Math.round(r.t)} g/L${r.ok ? "" : " (not runnable)"}`) : "not reached"]);
    }
    if (base) rows.push(["Change from the base case", (v[0] >= base[0] ? "+" : "−") + moneyU(Math.abs(v[0] - base[0]))]);
  }
  $("compare-h").textContent = UNIT === 1 ? "Against milk and eggs" : "Against the market";
  $("compare").innerHTML = rows.map(r => `<div class="row"><span class="k">${r[0]}</span><span class="v${/^[+−]?\$[\d.,–$]+$/.test(r[1]) ? " num" : ""}">${r[1]}</span></div>`).join("");
  $("yp-unit").textContent = unitWord();
  yourPrice();
  drawChart(band);
  drawMarket(v);
  drawBreakdown(v);
}

function drawBreakdown(v) {
  const bar = $("bar"), tb = $("breakdown");
  if (!v) { bar.innerHTML = ""; tb.innerHTML = ""; return; }
  const tot = v[2].reduce((a, b) => a + b, 0);
  bar.innerHTML = v[2].map((x, i) => `<div style="flex:${Math.max(x, 0)} 0 0;background:var(${SERIES[i]})" title="${G.groups[i]}: ${money(x)}"></div>`).join("");
  tb.innerHTML = `<thead><tr><th>Cost item</th><th class="r">$ ${unitWord()}</th><th class="r">Share</th></tr></thead><tbody>` +
    v[2].map((x, i) => `<tr><td><span style="display:inline-flex;align-items:center;gap:8px"><i class="sw" style="background:var(${SERIES[i]})"></i>${G.groups[i]}</span></td><td class="r">${moneyU(x)}</td><td class="r">${(100 * x / tot).toFixed(0)}%</td></tr>`).join("") +
    `<tr><td><b>Total</b></td><td class="r"><b>${moneyU(v[0])}</b></td><td class="r">100%</td></tr></tbody>`;
}

function drawChart(band0) {
  let band = band0;
  const svg = $("chart"), W = 640, H = 300, m = {l: 52, r: 16, t: 14, b: 38};
  const k = conv();
  const pts = AX.titer.map((t, i) => { const v0 = at(Object.assign({}, S, {titer: i})); return {t, i, v: v0 ? [v0[0] * k, v0[1], v0[2]] : null}; }).filter(p => p.v);
  { const mk = marketNow(); band = {label: mk.label, lo: mk.band[0], hi: mk.band[1], spot: mk.spot.length ? mk.spot[0].value : null, years: mk.years}; }
  const ys = pts.map(p => p.v[0]).concat([band.lo, band.hi]);
  let y0 = Math.min(...ys) * 0.8, y1 = Math.max(...ys) * 1.15;
  y0 = Math.max(y0, UNIT === 1 ? 0.005 : 1); y1 = Math.min(Math.max(y1, band.hi * 1.3), UNIT === 1 ? 100 : 3000);
  const lx = Math.log, X = t => m.l + (lx(t) - lx(2)) / (lx(110) - lx(2)) * (W - m.l - m.r);
  const Y = y => H - m.b - (lx(y) - lx(y0)) / (lx(y1) - lx(y0)) * (H - m.t - m.b);
  let s = "";
  const bandCol = `var(--band-${prodKey()})`;
  $("band-sw").style.background = bandCol;
  $("band-lg").textContent = band.label + " price band";
  s += `<rect x="${m.l}" y="${Y(Math.min(band.hi, y1))}" width="${W - m.l - m.r}" height="${Math.max(0, Y(Math.max(band.lo, y0)) - Y(Math.min(band.hi, y1)))}" fill="${bandCol}"/>`;
  for (const t of [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000]) {
    if (t < y0 || t > y1) continue;
    s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(t)}" y2="${Y(t)}" stroke="var(--grid)" stroke-width="1"/>`;
    s += `<text x="${m.l - 8}" y="${Y(t) + 4}" text-anchor="end">$${t}</text>`;
  }
  for (const t of [2, 5, 10, 20, 50, 100]) {
    s += `<line x1="${X(t)}" x2="${X(t)}" y1="${m.t}" y2="${H - m.b}" stroke="var(--grid)" stroke-width="1"/>`;
    s += `<text x="${X(t)}" y="${H - m.b + 16}" text-anchor="middle">${t}</text>`;
  }
  s += `<line x1="${m.l}" x2="${W - m.r}" y1="${H - m.b}" y2="${H - m.b}" stroke="var(--axis)"/>`;
  s += `<text x="${(m.l + W - m.r) / 2}" y="${H - 4}" text-anchor="middle" class="lbl">titer at harvest (g/L, log scale)</text>`;
  if (band.spot && band.spot <= y1 && band.spot >= y0) {
    s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(band.spot)}" y2="${Y(band.spot)}" stroke="var(--spot)" stroke-dasharray="4 3"/>`;
    s += `<text x="${W - m.r - 4}" y="${Y(band.spot) - 5}" text-anchor="end" class="lbl">spot price, 2026</text>`;
  }
  const ok = pts.filter(p => p.v[1] === 0 || p.v[1] === 2);
  // connect the leading run of achievable points
  let run = [];
  for (const p of pts) { if (p.v[1] === 0 || p.v[1] === 2) run.push(p); else break; }
  if (run.length > 1) s += `<polyline fill="none" stroke="var(--accent)" stroke-width="2" points="${run.map(p => X(p.t) + "," + Y(p.v[0])).join(" ")}"/>`;
  for (const p of pts) {
    const good = p.v[1] === 0 || p.v[1] === 2, cur = p.i === S.titer;
    if (cur) s += `<circle cx="${X(p.t)}" cy="${Y(p.v[0])}" r="9" fill="none" stroke="var(--ink)" stroke-width="1.5"/>`;
    s += good ? `<circle cx="${X(p.t)}" cy="${Y(p.v[0])}" r="4.5" fill="var(--accent)" stroke="var(--surface)" stroke-width="2"/>`
              : `<circle cx="${X(p.t)}" cy="${Y(p.v[0])}" r="4" fill="var(--surface)" stroke="var(--bad)" stroke-width="2"/>`;
    s += `<circle cx="${X(p.t)}" cy="${Y(p.v[0])}" r="14" fill="transparent" data-i="${p.i}" class="hit"/>`;
  }
  svg.innerHTML = s;
  // hover tooltip
  const tip = $("tip"), box = $("chartbox");
  svg.querySelectorAll(".hit").forEach(c => {
    const p = pts.find(q => q.i === +c.dataset.i);
    c.addEventListener("mouseenter", () => {
      tip.innerHTML = `<b>${p.t} g/L</b>: ${fmtU(p.v[0])} ${unitWord()}<br>${FLAG[p.v[1]][1]}`;
      tip.hidden = false;
      const r = svg.getBoundingClientRect(), k = r.width / W;
      const x = X(p.t) * k, y = Y(p.v[0]) * k;
      tip.style.left = Math.min(Math.max(0, x - 70), r.width - 170) + "px";
      tip.style.top = Math.max(0, y - 58) + "px";
    });
    c.addEventListener("mouseleave", () => { tip.hidden = true; });
    c.addEventListener("click", () => { S.titer = p.i; render(); });
  });
  $("chart-table").innerHTML = `<thead><tr><th class="r">Titer g/L</th><th class="r">$ ${unitWord()}</th><th>Status</th></tr></thead><tbody>` +
    pts.map(p => `<tr><td class="r">${p.t}</td><td class="r">${fmtU(p.v[0])}</td><td>${FLAG[p.v[1]][1]}</td></tr>`).join("") + "</tbody>";
}

function yourPrice() {
  const x = parseFloat($("yourprice").value);
  $("yp-out").textContent = x > 0 ? titerText(titerFor(x), x) : "";
}

function drawMarket(v) {
  const svg = $("mkt"), W = 640, H = 260, m = {l: 52, r: 120, t: 14, b: 30};
  const mk = marketNow(), cur = v ? v[0] * conv() : null;
  const cols = ["var(--s1)", "var(--s2)", "var(--s3)"];
  const Y0 = 2015, Y1 = 2026;
  const vals = mk.series.flatMap(s_ => Object.values(s_.pts)).concat(mk.spot.map(p => p.value));
  const top = Math.max(...vals, cur || 0) * 1.12;
  const step = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500].find(x => top / x <= 6) || 1000;
  const y1 = Math.ceil(top / step) * step;
  const X = y => m.l + (y - Y0) / (Y1 - Y0) * (W - m.l - m.r);
  const Y = x => H - m.b - x / y1 * (H - m.t - m.b);
  const fmtT = x => x === 0 ? "$0" : x < 1 ? "$" + x.toFixed(2) : "$" + Math.round(x);
  let s = "";
  for (let t = 0; t <= y1 + 1e-9; t += step) {
    s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(t)}" y2="${Y(t)}" stroke="var(--grid)"/>`;
    s += `<text x="${m.l - 8}" y="${Y(t) + 4}" text-anchor="end">${fmtT(t)}</text>`;
  }
  for (let y = Y0; y <= Y1; y++) if (y % 2 === 1 || y === Y1) s += `<text x="${X(y)}" y="${H - m.b + 16}" text-anchor="middle">${y}</text>`;
  s += `<line x1="${m.l}" x2="${W - m.r}" y1="${H - m.b}" y2="${H - m.b}" stroke="var(--axis)"/>`;
  mk.series.forEach((ser, i) => {
    const pts = Object.entries(ser.pts).map(([y, x]) => [+y, x]).sort((a, b) => a[0] - b[0]);
    s += `<polyline fill="none" stroke="${cols[i % 3]}" stroke-width="2" points="${pts.map(p => X(p[0]) + "," + Y(p[1])).join(" ")}"/>`;
    for (const p of pts) s += `<circle cx="${X(p[0])}" cy="${Y(p[1])}" r="3.5" fill="${cols[i % 3]}" stroke="var(--surface)" stroke-width="1.5"><title>${ser.label} ${p[0]}: ${fmtU(p[1])}</title></circle>`;
  });
  for (const p of mk.spot) {
    const x = X(p.year), y = Y(p.value);
    s += `<path d="M${x} ${y - 6}L${x + 6} ${y}L${x} ${y + 6}L${x - 6} ${y}Z" fill="var(--spot)"><title>${p.label}: ${fmtU(p.value)}</title></path>`;
  }
  if (cur != null) {
    s += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(cur)}" y2="${Y(cur)}" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="6 4"/>`;
    s += `<text x="${W - m.r + 6}" y="${Y(cur) + 4}" class="lbl">this design ${fmtU(cur)}</text>`;
  }
  svg.innerHTML = s;
  $("mkt-legend").innerHTML = mk.series.map((ser, i) => `<span><i class="sw" style="background:${cols[i % 3]}"></i>${ser.label}</span>`).join("") +
    (mk.spot.length ? `<span><i class="sw" style="background:var(--spot);transform:rotate(45deg);width:9px;height:9px"></i>spot 2026</span>` : "") +
    `<span><i class="sw" style="background:transparent;border-top:2px dashed var(--ink);height:0;width:14px;border-radius:0"></i>this design</span>`;
  $("mkt-h").textContent = UNIT === 1 ? `${EQV().per === "egg" ? "Egg" : "Milk"} prices by year, and this design` : "Market prices by year, and this design";
  const all = mk.series.flatMap(s_ => Object.values(s_.pts));
  $("mkt-note").textContent = cur == null ? "" : UNIT === 1
    ? `Prices of the natural source, ${unitWord()}, 2025 dollars; the design is the cost of replacing its protein.`
    : `${mk.label}, ${unitWord()}, 2025 dollars. This design would have been cheaper than ${all.filter(p => p >= cur).length} of ${all.length} annual export prices.`;
  const curP = v ? v[0] : null;   // $/kg protein, whatever the unit shown
  $("ctx-table").innerHTML = `<thead><tr><th>Ingredient</th><th class="r">$/kg protein</th><th>Source</th><th>This design</th></tr></thead><tbody>` +
    D.context.map(c => `<tr><td>${c.label}</td><td class="r">${money(c.lo)}–${money(c.hi)}</td><td>${c.when || "grade " + c.grade}</td><td>${curP == null ? "–" : curP < c.lo ? "cheaper" : curP <= c.hi ? "within the range" : curP < 1.05 * c.hi ? "at the top edge" : (curP / c.hi).toFixed(1) + "× the top"}</td></tr>`).join("") + "</tbody>";
  const yrs = [...new Set(mk.series.flatMap(s_ => Object.keys(s_.pts)))].sort();
  $("mkt-table").innerHTML = `<thead><tr><th>Year</th>${mk.series.map(s_ => `<th class="r">${s_.label}</th>`).join("")}</tr></thead><tbody>` +
    yrs.map(y => `<tr><td>${y}</td>${mk.series.map(s_ => `<td class="r">${s_.pts[y] == null ? "–" : fmtU(s_.pts[y])}</td>`).join("")}</tr>`).join("") +
    mk.spot.map(p => `<tr><td>${p.year} (spot)</td><td class="r" colspan="${mk.series.length}">${fmtU(p.value)}</td></tr>`).join("") + "</tbody>";
}

function drawRef() {
  const rows = D.ref[REFP], mk = D.market[REFP], [lo, hi] = mk.band;
  const pos = x => x == null ? "–" : x < lo ? "below" : x <= hi ? "inside" : x < 1.05 * hi ? "at the top edge" : (x / hi).toFixed(1) + "× the top";
  const dash = x => x == null ? "–" : money(x);
  let h = `<thead><tr><th>Case</th><th class="r">Titer g/L</th><th class="r">Price-anchored $/kg</th><th class="r">Design-report $/kg</th><th class="r">Aseptic vessels $/kg</th><th>Vs market range</th></tr></thead><tbody>`;
  h += rows.map(r => `<tr><td>${r.label}</td><td class="r">${+r.titer.toFixed(2)}</td><td class="r">${money(r.humbird)}</td><td class="r">${dash(r.light)}</td><td class="r">${dash(r.aseptic)}</td><td>${pos(r.humbird)}</td></tr>`).join("");
  (mk.comparators || []).forEach(c => { h += `<tr class="mkt"><td>${c.label}</td><td class="r">10</td><td class="r" colspan="3">cost of production ${money(c.value)} (ours: ${dash(c.ours)})</td><td>${pos(c.value)}</td></tr>`; });
  const yrs = mk.years ? `${mk.years[0]}–${mk.years[1]}` : "2013–2025";
  h += `<tr class="mkt"><td>Market: ${mk.label}, ${yrs}</td><td></td><td class="r" colspan="3">${money(lo)}–${money(hi)} per kg protein</td><td></td></tr></tbody>`;
  $("ref").innerHTML = h;
  $("ref-note").textContent = REFP === "lf"
    ? "Lactoferrin: 250 t/yr (a world market of roughly 0.3–1.6 kt/yr); reported dairy prices in 2025 dollars. Intelligen's figures are costs of production (depreciation, no return on capital), set against ours; the report reconciles them line by line."
    : "10 kt/yr, US Midwest unless noted; $/kg of protein, 2025 dollars. 'Vs market range' places the price-anchored cost against the 2015–2025 export unit values per kg protein.";
}

function init() {
  for (const a of ["titer", "t_prod", "X_prod", "Y_ps"]) {
    const vals = AX[a];
    $("t-" + a).innerHTML = [vals[0], vals[vals.length - 1]].map(x => `<span>${a === "Y_ps" ? x.toFixed(2) : x}</span>`).join("");
    $(a).addEventListener("input", e => { S[a] = +e.target.value; render(); });
  }
  for (const a of ["product", "convention", "site"]) {
    document.querySelectorAll(`input[name=${a}]`).forEach(el => el.addEventListener("change", e => {
      S[a] = +e.target.value;
      if (a === "product") {                         // jump to the protein's own base point; the table follows the protein
        S = Object.assign(baseFor(S.product), {convention: S.convention, site: S.site});
        REFP = prodKey(); $("r-" + REFP).checked = true; drawRef();
      }
      render();
    }));
  }
  document.querySelectorAll("input[name=unit]").forEach(el => el.addEventListener("change", e => { UNIT = +e.target.value; render(); }));
  document.querySelectorAll("input[name=refp]").forEach(el => el.addEventListener("change", e => { REFP = e.target.value; drawRef(); }));
  $("yourprice").addEventListener("input", yourPrice);
  $("reset").addEventListener("click", () => {
    S = baseFor(S.product);
    document.querySelectorAll("input[type=radio]").forEach(el => { if (el.name !== "refp") el.checked = +el.value === (el.name === "unit" ? UNIT : S[el.name]); });
    render();
  });
  $("gen").textContent = `Model runs generated ${D.generated}. Grid: ${G.values.length.toLocaleString("en-US")} runs of the full model (repository pf-tea).`;
  drawRef();
  render();
}
init();
</script>
"""

ING = R["equivalents"].get("ingredient_per_unit")
egg_rng = (f"${min(ING['dried_egg_white_per_egg'].values()):.3f}–{max(ING['dried_egg_white_per_egg'].values()):.3f} per egg"
           if ING else "(not yet computed)")
whey_rng = (f"was {min(ING['whey_share_of_farm_milk'].values()):.0%}–{max(ING['whey_share_of_farm_milk'].values()):.0%}"
            if ING else "(not yet computed)")
out = OUT
out.write_text(HTML.replace("__DATA__", json.dumps(DATA, separators=(",", ":"))).replace("__PRODRADIOS__", PROD_RADIOS)
               .replace("__REFRADIOS__", REF_RADIOS).replace("__EGGWHITE__", egg_rng)
               .replace("__WHEYSHARE__", whey_rng))
print("wrote", out, f"{out.stat().st_size / 1e3:.0f} kB")
