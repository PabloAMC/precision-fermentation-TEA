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
    "alac": rows_ok(
    lambda: case("Best public titer (Wang 2025; human alpha-lac, ethanol-fed, priced as glucose; 0.6 g/L)", SC["academic/alac"],
         SC["academic/alac/light"], SC.get("academic/alac/aseptic")),
    lambda: case("Base case (Intelligen's design point), UF/DF concentrate, 1 kt/yr", R["base"]["alac"],
         R["base_light"]["alac"], R["base_aseptic"]["alac"]),
    lambda: case("Same, at BLG's 10 kt/yr", R["alac"]["at_10kt"]),
    lambda: case("Industry benchmark: titer assumed in private cost models", SC["industry/alac"], SC["industry/alac/light"],
         SC.get("industry/alac/aseptic")),
    lambda: case("Physical-limit best case, 32 kt/yr (secretion at 40 mg/g/h)", PLR["alac/humbird"], PLR["alac/light"]),
    lambda: case("Same, at the best secretion demonstrated on glucose (2.1 mg/g/h)", PLR["alac/humbird/q_p_max_2.1"])),
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
NAMES = {"blg": "&beta;-lactoglobulin", "ova": "Ovalbumin", "ovd": "Ovomucoid", "cas": "&beta;-casein", "lf": "Lactoferrin", "alb": "Serum albumin", "alac": "&alpha;-lactalbumin"}
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
    reported_market("lf", "Dairy lactoferrin (reports and trade press; company claims or surveys)", LFP,
                    [dict(label="Intelligen's model, " + {"lf": "cation exchange", "lf_ufdf_only": "UF/DF only"}[c["ours"]],
                          value=c["value_money_year"],
                          ours=R["lactoferrin"].get("reconciliation", {}).get(c["ours"], {}).get("cop"))
                     for c in LFP.get("comparators", []) if c.get("ours")])
if "alac" in PRODS:
    reported_market("alac", "Dairy alpha-lactalbumin (market reports; company claims or surveys)", R["alac"]["reported_prices"])
if "alb" in PRODS:
    reported_market("alb", "Bulk serum albumin (technical BSA trade values; company claims or surveys)", R["albumin"]["reported_prices"])
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

import sys as _sys
_sys.path.insert(0, str(ROOT / "src"))
from pftea import params as _params  # noqa: E402
from pftea import scenarios as _sc  # noqa: E402
ROUTE = {"concentrate": "centrifuges, membrane filtration and a spray dryer",
         "cex": "centrifuges, a cation-exchange column, membranes and a spray dryer",
         "acid": "centrifuges, acid precipitation (as dairy casein) and a dryer",
         "isolate": "centrifuges, membranes, precipitation and a spray dryer"}
WALK = {}
for p_ in PRODS:
    b_, q_ = R["base"][p_], _sc.base_params(p_)
    d_, ph_ = b_["design"], b_["physical"]
    spec_ = _params.v(q_, "plant.spec")
    WALK[p_] = dict(titer=d_["titer"], t_growth=d_["t_growth_h"], t_prod=d_["t_total_h"] - d_["t_growth_h"],
                    qp=d_["q_p_mg_g_h"], glucose=ph_["glucose_kg"], o2=ph_["o2_kg"], yield_=ph_["overall_yield_g_g"],
                    cells=ph_["cells_kg"], recovery=d_["recovery"], batches=d_["n_batches"], fermenters=d_["N_prod_int"],
                    vol=_params.v(q_, "fermenter.volume_m3"), tpy=d_["n_batches"] * d_["target_per_batch_kg"] / 1000,
                    tci=b_["tci"], msp=b_["msp_ccf"], lang=d_["lang_effective"],
                    capital=(b_["per_kg"]["capital charge"] + b_["per_kg"]["maintenance"] + b_["per_kg"]["insurance"]) / b_["msp_ccf"],
                    glucose_share=b_["per_kg"]["glucose"] / b_["msp_ccf"],
                    route=ROUTE.get(spec_, spec_ + " route"))
OPT = {}
for p_ in PRODS:
    o_ = R.get("options", {}).get(p_)
    if o_:
        OPT[p_] = dict(base=o_["base"]["msp_ccf"], loss=o_["yield_loss"]["0.065"]["msp_ccf"],
                       coupled=o_["coupled_titer"]["msp_ccf"], q_need=o_["coupled_titer"]["design"]["q_ref_mg_g_h"],
                       demo=o_["demonstrated"]["msp_ccf"] if o_["demonstrated"] else None,
                       demo_titer=o_["demonstrated"]["design"]["titer"] if o_["demonstrated"] else None,
                       cont=o_["continuous"]["msp_ccf"] if o_["continuous"] else None)
PRESET = {}
for p_ in PRODS:
    a_ = SC.get("academic/" + p_)
    if a_:
        q_ = _sc.scenario_params("academic", p_)
        PRESET[p_] = dict(titer=a_["design"]["titer"], t_prod=a_["design"]["t_total_h"] - a_["design"]["t_growth_h"],
                          X_prod=_params.v(q_, "strain.X_prod_g_L"), msp=a_["msp_ccf"],
                          host=_params.v(q_, "strain.host"))
DET = yaml.safe_load((ROOT / "data/pf/scenarios/detailed.yaml").read_text())
Q_DEMO = DET["demonstrated"]["strain.q_ref_mg_g_h"]
MU_REF = _params.v(_params.load(), "strain.qp_mu_ref_per_h")
DATA = {
    "grid": G,
    "walk": WALK,
    "checks": dict(
        yeast=[R["calibration"]["bakers_yeast"]["cop"], R["calibration"]["bakers_yeast"]["market_implied"]],
        intelligen=R["calibration"]["intelligen2025_ova"]["usd_per_kg_powder (Humbird convention)"],
        nrel=R["calibration"]["nrel2011_cellulase"]["usd_per_kg_protein (DCF, NREL financing)"],
        vout=R["calibration"]["voutilainen2021_case"]["EUR_per_t_protein (their DCF)"],
        o2_nrel=R["calibration"]["nrel2011_cellulase"]["o2_mol_per_kg"],
        plant=[R["plant_cost_check"]["model_per_m3"], R["plant_cost_check"]["ll_scaled_per_m3"]["0.5"],
               R["plant_cost_check"]["ll_scaled_per_m3"]["0.7"]]),
    "preset": PRESET,
    "industry_titer": _params.v(_sc.scenario_params("industry", "blg"), "strain.titer_g_L"),
    "options": OPT,
    "q_demo": Q_DEMO,
    "mu_ref": MU_REF,
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
ol.walk { margin: 12px 0 0; padding-left: 22px; display: grid; gap: 8px; max-width: 86ch; }
.steps { display: grid; gap: 6px; margin-top: 12px; max-width: 90ch; }
details.step { border-top: 1px solid var(--rule); padding: 8px 0 2px; }
details.step > summary { color: var(--ink); font-size: 14.5px; list-style-position: outside; }
details.step > summary b { font-weight: 600; }
details.step .body { display: grid; gap: 8px; padding: 8px 0 10px 18px; color: var(--ink-2); font-size: 14px; }
details.step .eq { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 13px; color: var(--ink); background: var(--accent-soft); padding: 6px 10px; border-radius: 6px; overflow-x: auto; white-space: pre; }
details.step .vs { font-size: 13px; color: var(--muted); }
details.step table { font-size: 13px; }
.def { font-size: 12.5px; color: var(--ink-2); margin: 0; max-width: 60ch; }
.verdict { margin-top: 14px; font-size: 15px; color: var(--ink); max-width: 52ch; text-wrap: pretty; }
.seg.pills { display: flex; flex-wrap: wrap; gap: 6px; border: 0; overflow: visible; }
.seg.pills label { border: 1px solid var(--rule); border-radius: 999px; padding: 5px 12px; flex: 0 0 auto; }
.seg.pills label:first-of-type { border-left: 1px solid var(--rule); }
.start { margin-bottom: 16px; display: grid; gap: 8px; }
.start-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.start-k { font-size: 13px; font-weight: 600; color: var(--ink-2); margin-right: 4px; }
.pick { font: 500 14px "IBM Plex Sans", system-ui, sans-serif; color: var(--accent); background: var(--accent-soft); border: 1px solid transparent; border-radius: 999px; padding: 6px 14px; cursor: pointer; }
.pick:hover { border-color: var(--accent); }
.pick:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.pick[aria-pressed="true"] { background: var(--accent); color: var(--accent-ink); }
details.learn { margin-bottom: 16px; }
details.learn > summary { font-weight: 600; font-size: 15px; }
details.more { margin-top: 2px; }
details.more > summary { font-size: 12.5px; }
ol.walk li { color: var(--ink-2); }
ol.walk li b { color: var(--ink); font-weight: 600; }
fieldset[disabled] { opacity: .45; }
@media (max-width: 860px) {
  .summary, .main { grid-template-columns: minmax(0, 1fr); }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap">
  <header>
    <h1>Precision Fermentation Cost Explorer</h1>
    <p class="lede">What does it cost to make a milk or egg protein with an engineered yeast? Pick a protein, move the strain's
    performance, and see the price per kg, whether a real fermenter could run the design, and how the price compares with the
    protein it would replace. The price is a production cost that includes a return on the money spent building the plant; it is
    not a market price.</p>
    <p class="lede">The model follows Humbird's (2021) cost model for cultivated meat. The yeast (<i>K.&nbsp;phaffii</i>) secretes the protein
    in fermenters of up to 200&nbsp;m&sup3;; the plant makes 10,000&nbsp;t a year (lactoferrin 250&nbsp;t, albumin and &alpha;-lactalbumin 1,000&nbsp;t).
    New to this? Start with one of the buttons below, then open "How the price is built" for the calculation step by step.</p>
  </header>

  <section class="summary" aria-live="polite">
    <div class="panel">
      <h2>Minimum selling price</h2>
      <div class="price"><span class="big num" id="msp">$0</span><span class="unit" id="msp-unit">per kg protein, 2025 dollars</span></div>
      <p class="def">The price that pays every cost of the plant plus a 14.6% yearly return on what it cost to build. No profit margin, sales or transport.</p>
      <div class="chips" id="chips"></div>
      <p class="verdict" id="verdict" aria-live="polite"></p>
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

  <section class="panel start" aria-label="Starting points">
    <div class="start-row">
      <span class="start-k">Start from</span>
      <button type="button" class="pick" id="pre-best">The best published strain</button>
      <button type="button" class="pick" id="pre-base">A published plant design</button>
      <button type="button" class="pick" id="pre-ind">What companies assume</button>
      <button type="button" class="pick" id="pre-lim">The fermenter's limit</button>
    </div>
    <p class="hint" id="pre-note">Each button sets the levers below to one well-known case for the chosen protein. Then move them yourself.</p>
  </section>

  <details class="panel learn" id="learn">
    <summary><span id="walk-h">New here? How the price is built, in eight steps</span></summary>
    <p class="hint" style="margin-top:10px">Each step hands its result to the next. Open a step for the idea behind it, its equation and how Humbird's cultivated-meat model does the same. Numbers are this protein's base case.</p>
    <div class="steps" id="walk"></div>
  </details>

  <details class="panel learn" id="method">
    <summary>How the model was built and checked</summary>
    <div class="steps" id="method-body"></div>
  </details>

  <section class="main">
    <div class="panel">
      <form id="controls" onsubmit="return false">
        <fieldset>
          <legend>Protein</legend>
          <div class="seg pills" role="radiogroup">
__PRODRADIOS__
          </div>
        </fieldset>
        <fieldset>
          <legend>Model</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="physics" id="m-s" value="0" checked><label for="m-s">Simple (base)</label>
            <input type="radio" name="physics" id="m-d" value="1"><label for="m-d">Detailed</label>
          </div>
          <p class="hint" id="phys-hint">Simple: cells secrete steadily while barely growing, as published plant designs assume. Detailed: secretion falls as growth slows, as measured in labs.</p>
          <details class="more"><summary>More</summary><p class="hint">Detailed also takes 6.5% off the cells' growth yield in a large tank, where sugar and oxygen mix unevenly (George et al. 1998). It runs with the base capital estimate and the US site, so those choices are locked. It tells you how fast the strain would have to secrete to reach the titer you set.</p></details>
        </fieldset>
        <fieldset id="fs-capital">
          <legend>Capital estimate</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="convention" id="c-h" value="0" checked><label for="c-h">Price-anchored (base)</label>
            <input type="radio" name="convention" id="c-l" value="1"><label for="c-l">Design-report</label>
            <input type="radio" name="convention" id="c-a" value="2"><label for="c-a">Aseptic vessels</label>
          </div>
          <p class="hint">How the cost of building the plant is estimated.</p>
          <details class="more"><summary>More</summary><p class="hint"><b>Price-anchored</b> (base): Humbird's factors and fixed costs of 9% of the investment a year. With them his model reproduces the real cost of baker's yeast. <b>Design-report</b>: the lighter factors and fixed costs (under 2% a year) of NREL-style design reports. <b>Aseptic vessels</b>: pharmaceutical-grade fermenters, about 2.9 times the price of industrial ones.</p></details>
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
        <fieldset id="fs-site">
          <legend>Plant site</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="site" id="s-us" value="0" checked><label for="s-us">US Midwest</label>
            <input type="radio" name="site" id="s-eu" value="1"><label for="s-eu">North-west Europe</label>
          </div>
        </fieldset>
        <fieldset>
          <legend>Strain performance</legend>
          <div class="slider"><div class="top"><label for="titer">Titer at harvest</label><output id="o-titer" for="titer"></output></div>
            <p class="def">Grams of protein per litre of broth when the batch ends. The strain's main number.</p>
            <input type="range" id="titer" min="0" max="10" step="1"><div class="ticks" id="t-titer"></div></div>
          <div class="slider"><div class="top"><label for="t_prod">Production phase</label><output id="o-t_prod" for="t_prod"></output></div>
            <p class="def">Hours the cells spend making the protein, after they have grown. Shorter means more batches a year.</p>
            <input type="range" id="t_prod" min="0" max="5" step="1"><div class="ticks" id="t-t_prod"></div></div>
          <div class="slider"><div class="top"><label for="X_prod">Cell density in production</label><output id="o-X_prod" for="X_prod"></output></div>
            <p class="def">Grams of dry yeast per litre while they make the protein. More cells make more protein, but use more oxygen.</p>
            <input type="range" id="X_prod" min="0" max="2" step="1"><div class="ticks" id="t-X_prod"></div></div>
          <div class="slider"><div class="top"><label for="Y_ps">Product yield on glucose</label><output id="o-Y_ps" for="Y_ps"></output></div>
            <p class="def">Grams of protein the protein-making reaction gets from 1 g of sugar. <span id="y-effect"></span></p>
            <input type="range" id="Y_ps" min="0" max="2" step="1"><div class="ticks" id="t-Y_ps"></div></div>
          <p class="hint">Each step is a value the full model was run at. Everything else stays at the protein's base case.</p>
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
          <p class="hint" style="margin-top:6px">$ per kg protein. Export unit values: 2015–2025 in 2025 dollars. GFI 2025 ranges: nominal, about 2024–2025 (industry data; company claims or surveys).</p></details>
      </div>
      <div class="panel">
        <h2>What the price is made of</h2>
        <div class="bar" id="bar" aria-hidden="true"></div>
        <div class="tablewrap" style="margin-top:10px"><table id="breakdown"></table></div>
      </div>
    </div>
  </section>

  <section class="panel" style="margin-top:16px">
    <div class="panel-head"><h2 id="opt-h">Simple or detailed: what the extra physics changes</h2></div>
    <div class="tablewrap"><table id="opt"></table></div>
    <p class="hint" id="opt-note" style="margin-top:8px"></p>
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
    <p><b>Limits.</b> A design marked in red breaks a physical limit (step 4 of "How the price is built"): its price is shown, but no real fermenter could run it as set. The model also caps secretion at 40&nbsp;mg of protein per g of cells per hour, a judgment above any published <i>K.&nbsp;phaffii</i> strain.</p>
    <p><b>Market prices.</b> Export unit values from UN&nbsp;Comtrade and Eurostat, deflated to 2025 dollars. Per kg of protein they assume 80% protein for whey (the minimum for its trade code; more isolate in the mix would lower the per-protein price) and 81.1% for egg white; "per kg powder" compares the same export prices per kg of product with our powder's cost per kg. The 2026 whey spot is from USDA Dairy Market News narrative quotes. Lactoferrin prices are reported ranges (trade press and reports; company claims or surveys). Our figures are production costs with a return on capital, not selling prices: a seller would add margin, sales and distribution.</p>
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
let PHYS = 0;   // 0: simple (base); 1: detailed physics (sub-grid: base convention and site, base yield)
const DG = G.detailed || null;
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
  0: ["good", "A real fermenter can run this", "M3 8l3 3 7-7"],
  1: ["bad", "Breaks a physical limit (O₂, heat, fill or productivity)", "M4 4l8 8M12 4l-8 8"],
  2: ["warn", "Above an assumed solubility", "M8 3v6M8 12v1"],
  3: ["bad", "Yield above the energetic ceiling", "M4 4l8 8M12 4l-8 8"],
};
const $ = id => document.getElementById(id);
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const money = (x, d) => "$" + (x >= 100 ? Math.round(x).toLocaleString("en-US") : x.toFixed(d === undefined ? (x < 10 ? 2 : 1) : d));

function at(sel) {
  let k = 0;
  if (PHYS === 1 && DG) {
    for (const a of DG.order) k = k * AX[a].length + sel[a];
    return DG.values[k];
  }
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
  { // how much the yield moves this design's price, over its whole range (simple model only)
    const y0 = PHYS === 0 ? at(Object.assign({}, S, {Y_ps: 0})) : null, y1 = PHYS === 0 ? at(Object.assign({}, S, {Y_ps: AX.Y_ps.length - 1})) : null;
    $("y-effect").textContent = y0 && y1 ? `Over its whole range it moves this design's price by only ${moneyU(Math.abs(y0[0] - y1[0]))}: most sugar goes to the cells, not the protein.` : "";
  }
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
    if (PHYS === 0 && ceil && AX.X_prod[S.X_prod] === 107 && AX.Y_ps[S.Y_ps] === 0.465) chips.push(`<span class="chip plain">The fermenter can reach at most about ${Math.round(ceil)} g/L in ${tp} hours</span>`);
    if (PHYS === 1 && v[3] != null) {
      const x = v[3] / D.q_demo;
      chips.push(`<span class="chip ${x > 1.5 ? "warn" : "good"}">Needs cells that secrete ${v[3].toFixed(1)} mg of protein per g per hour while growing at ${Math.round(100 * D.mu_ref)}% an hour: ${x < 1 ? "less than" : x.toFixed(1) + " times"} the best published strain (${D.q_demo})</span>`);
    }
  }
  $("chips").innerHTML = chips.join("");
  const eq = EQV() || {per: "litre of milk", what: "", grams: 0, bands: []};
  $("msp-unit").textContent = UNIT === 1 ? `per ${eq.per} (PF protein replacing ${eq.what}), 2025 dollars`
    : UNIT === 2 ? "per kg of powder, 2025 dollars" : "per kg protein, 2025 dollars";
  $("u-src-l").textContent = "per " + eq.per;
  $("u-hint").textContent = UNIT === 1 ? `Multiplies $/kg by ${eq.grams.toFixed(2)} g / 1000.`
    : UNIT === 2 ? `Our powder is ${Math.round(100 * D.powder_frac[prodKey()])}% target protein; market prices per kg of product (${Math.round(100 * MKT().frac)}% protein).` : "";
  // comparison panel: in the shown unit throughout
  // the base case to compare with: the simple model's, also when the detailed physics are on
  const phys0 = PHYS; PHYS = 0;
  const base = at(Object.assign({}, baseFor(S.product), {convention: S.convention, site: S.site}));
  PHYS = phys0;
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
      rows.push([`Yearly prices it would have beaten (${mk.series.map(x => x.label).join(" and ")}, ${mk.years[0]}–${mk.years[1]})`, `${all.filter(p => p >= cur).length} of ${all.length}`]);
      for (const p of mk.spot) rows.push([`${p.label}: one recent quote, far above the 2015–2025 range`, fmtU(p.value) + (cur <= p.value ? ", undercut" : ", not reached")]);
      const r = titerFor(avg);
      rows.push([`Titer to match the ${mk.years[0]}–${mk.years[1]} average price (${fmtU(avg)}), estimated between runs`,
                 r ? (r.first ? `≤ ${r.t} g/L` : `${Math.round(r.t)} g/L${r.ok ? "" : " (not runnable)"}`) : "not reached"]);
    }
    if (base && Math.abs(v[0] - base[0]) >= 0.005) rows.push([PHYS === 1 ? "Change from the simple base case" : "Change from the base case", (v[0] >= base[0] ? "+" : "−") + moneyU(Math.abs(v[0] - base[0]))]);
  }
  $("compare-h").textContent = UNIT === 1 ? "Against milk and eggs" : "Against the market";
  $("verdict").textContent = verdict(v);
  $("compare").innerHTML = rows.map(r => `<div class="row"><span class="k">${r[0]}</span><span class="v${/^[+−]?\$[\d.,–$]+$/.test(r[1]) ? " num" : ""}">${r[1]}</span></div>`).join("");
  $("yp-unit").textContent = unitWord();
  yourPrice();
  drawChart(band);
  drawMarket(v);
  drawBreakdown(v);
  drawWalk();
  drawOptions();
}

function verdict(v) {
  // one plain sentence: where this design lands, and what it would take to reach the market
  if (!v) return "No working batch exists at these settings: the fermenter cannot reach this titer.";
  const mk = marketNow(), cur = v[0] * conv(), [lo, hi] = mk.band;
  const where = cur < lo ? "below even the lowest of" : cur <= hi ? "inside the range of" : `${(cur / hi).toFixed(1)} times the highest of`;
  const what = mk.label.split(" (")[0];
  let s = `This design costs ${fmtU(cur)} ${unitWord()}, ${where} the ${mk.years[0]}–${mk.years[1]} prices of ${what.charAt(0).toLowerCase() + what.slice(1)}.`;
  if (!feasible(v[1])) return s + " But a real fermenter could not run it as set: it breaks a physical limit.";
  if (cur > hi && UNIT !== 1) {
    const r = titerFor(hi);
    s += r ? (r.first ? "" : ` To match the top of that range it would need about ${r.t < 10 ? r.t.toFixed(1) : Math.round(r.t)} g/L (estimated between the model's runs)${r.ok ? "" : ", which the fermenter cannot run with these settings"}.`)
           : " No titer on this chart gets it there with these settings.";
  }
  return s;
}

function snap(axis, x) {
  // index of the grid value nearest to x (log distance for titer, linear otherwise)
  const vals = AX[axis], d = axis === "titer" ? (a => Math.abs(Math.log(a) - Math.log(x))) : (a => Math.abs(a - x));
  return vals.reduce((best, a, i) => d(a) < d(vals[best]) ? i : best, 0);
}

function unpress() { document.querySelectorAll(".pick").forEach(el => el.setAttribute("aria-pressed", "false")); }

function preset(kind) {
  const k = prodKey(), b = baseFor(S.product), keep = {convention: S.convention, site: S.site};
  const note = $("pre-note"), pr = D.preset[k];
  document.querySelectorAll(".pick").forEach(el => el.setAttribute("aria-pressed", "false"));
  $("pre-" + kind).setAttribute("aria-pressed", "true");
  if (kind === "base") {
    S = Object.assign(b, keep);
    note.textContent = "The design point of a published plant design (Intelligen's): the base case of this page.";
  } else if (kind === "ind") {
    S = Object.assign(b, keep, {titer: snap("titer", D.industry_titer)});
    note.textContent = `${D.industry_titer} g/L: the average titer in companies' own cost models (GFI 2025, a survey over unnamed proteins).`;
  } else if (kind === "lim") {
    const c = (D.ceiling[k] || {})[String(AX.t_prod[b.t_prod])];
    S = Object.assign(b, keep, {titer: c ? snap("titer", c * 0.97) : AX.titer.length - 2});
    note.textContent = c ? `About ${Math.round(c)} g/L is the most this fermenter can reach in ${AX.t_prod[b.t_prod]} hours before the batch would have to start too empty.` : "Near the highest titer the fermenter can run.";
  } else if (pr) {
    S = Object.assign(b, keep, {titer: snap("titer", pr.titer), t_prod: snap("t_prod", pr.t_prod), X_prod: snap("X_prod", pr.X_prod)});
    const below = pr.titer < AX.titer[0];
    note.textContent = `The best published strain reaches ${pr.titer < 10 ? pr.titer.toFixed(pr.titer < 1 ? 2 : 1) : Math.round(pr.titer)} g/L in about ${Math.round(pr.t_prod)} hours` +
      (pr.host !== "kphaffii" ? " in a different host (T. reesei)" : "") + `. The model costs it at ${money(pr.msp)}/kg.` +
      (below ? ` That is below this chart's lowest titer, so the levers show ${AX.titer[0]} g/L.` : " The levers show the nearest model runs.");
  }
  render();
}

function drawWalk() {
  const w = D.walk[prodKey()], label = $("p-" + prodKey()).nextElementSibling.textContent;
  const name = label.charAt(0).toLowerCase() + label.slice(1);       // lower case inside a sentence
  if (!w) { $("walk").innerHTML = ""; return; }
  const n0 = x => Math.round(x).toLocaleString("en-US"), n1 = x => x.toFixed(1), pc = x => Math.round(100 * x) + "%";
  $("walk-h").textContent = `New here? How the price of ${name} is built, in eight steps`;
  const ceil72 = (D.ceiling[prodKey()] || {})["72"];
  const step = (n, title, line, body, eq, vs) => `<details class="step"><summary><b>${n}. ${title}.</b> ${line}</summary><div class="body">` +
    body.map(x => `<p>${x}</p>`).join("") + (eq ? `<div class="eq">${eq}</div>` : "") + (vs ? `<p class="vs"><b>Humbird:</b> ${vs}</p>` : "") + `</div></details>`;
  $("walk").innerHTML = [
    step(1, "The cell as a chemical reaction",
      `Making 1 kg of ${name} takes ${n1(w.glucose)} kg of glucose and ${n1(w.o2)} kg of oxygen in all.`,
      ["For costing, a cell is a black box: glucose, ammonia and oxygen go in; cells, protein, CO₂, water and heat come out.",
       "Two conservation laws fix most of the flows. Carbon is conserved, and so are electrons: the electrons that leave glucose either stay in the protein or pass to oxygen.",
       "The model writes every species per carbon atom. The protein's formula comes from its amino-acid sequence."],
      "per carbon atom of glucose:  4 = Y × γ + 4 × O₂\nY = carbon atoms of protein made; γ = the protein's spare electrons per carbon atom (C +4, H +1, O −2, N −3); O₂ = moles of oxygen used",
      "the same balance, with the cells as the product."),
    step(2, "Where the sugar goes",
      `Most of it builds and maintains the cells: ${n1(w.cells)} kg of yeast for every kg of ${name}. The overall yield is ${w.yield_.toFixed(3)} g/g.`,
      ["A cell spends sugar on three things: growing, staying alive (maintenance) and making the protein.",
       "The protein-making reaction alone would give about 0.47 g of protein per g of sugar. The whole batch gives far less, because the cells must first be grown and then kept alive for days.",
       "So sugar is not the expensive part: glucose is " + pc(w.glucose_share) + " of the price."],
      "sugar per g of cells per hour = growth rate ÷ cell yield + upkeep + secretion rate ÷ protein yield   (the Pirt equation)",
      "the same equation and correlations (Heijnen, Tijhuis). For cultivated meat the cells are the product, and the medium, not sugar, is the costly input."),
    step(3, "One batch through time",
      `Cells grow for ${n0(w.t_growth)} hours, then secrete for ${n0(w.t_prod)} hours, reaching ${n1(w.titer)} g/L.`,
      ["The batch starts with little broth. A pump feeds concentrated glucose as the cells need it, which sets how fast they grow (fed-batch).",
       "Phase one grows the cells to their working density. Phase two makes the protein while the cells barely grow; feeding raises the broth to 80% of the vessel.",
       `The model solves for the starting volume and for the secretion rate that hits the target titer: here ${w.qp.toFixed(1)} mg of protein per g of cells per hour. The best published glucose process reaches ${D.q_demo}.`],
      "secretion rate ≈ protein made / (average cells × production hours)",
      "only the growth phase for baker's yeast; cultivated-meat batches last days to weeks."),
    step(4, "The physical limits",
      "The fermenter must supply the oxygen, remove the heat and hold the broth. A design that cannot is marked in red.",
      ["Oxygen dissolves poorly, so air must deliver it as fast as the cells use it. Stirred tanks top out near 200 mol of O₂ per m³ of liquid per hour.",
       "Respiration releases about 460 kJ per mol of O₂, removed at 30 °C. The model allows 25 kW per m³.",
       "A batch must start at least 30% full. A higher titer needs more sugar feed, so the batch must start emptier." + (ceil72 ? ` This caps the titer at about ${Math.round(ceil72)} g/L in a 72-hour production phase.` : "")],
      "oxygen transfer = kLa × (C* − C)\nkLa = how fast the vessel mixes gas into the liquid; C* = oxygen the liquid could hold; C = oxygen it holds",
      "his Figure 1.3 prices oxygen transfer against vessel size. Animal cells have far tighter limits: bubbles and stirring damage them."),
    step(5, "Purification",
      `${w.route.charAt(0).toUpperCase() + w.route.slice(1)} keep ${pc(w.recovery)} of the protein.`,
      ["Each step keeps a fraction of the protein, and the fractions multiply.",
       "Centrifuges lose protein in the liquid trapped in the cell paste. Membranes leak a little each time liquid passes. The dryer loses a little in its filters.",
       "Membrane area is sized from the litres to filter per year and how fast liquid passes each square metre."],
      "fraction kept = cell removal × microfiltration × ultrafiltration × drying",
      "almost none: in cultivated meat the cells are the product, so harvest is the purification."),
    step(6, "Scale",
      `${n0(w.tpy)} t a year takes ${n0(w.batches)} batches in ${w.fermenters} fermenters of ${n0(w.vol)} m³.`,
      ["Batches per year = annual output ÷ protein per batch. Fermenters = batches × hours per batch ÷ operating hours, rounded up to whole vessels.",
       "Batches start at staggered times, so the plant's compressors and chillers are sized for its combined peak, not the sum of every vessel's peak.",
       "Staff follow Humbird's rule: operator time per batch step, plus fixed crews and supervisors."],
      "fermenters = batches per year × (batch time + turnaround) / operating hours",
      "the same occupancy arithmetic and labour model."),
    step(7, "Capital",
      `Equipment times Humbird's factors gives a $${n0(w.tci / 1e6)} million investment.`,
      ["Each piece of equipment is priced from a quote at a reference size. Cost grows more slowly than size: twice the volume costs about 1.6 times as much.",
       `Factors then add what a plant needs beyond its equipment: missing items, installation, buildings, engineering, fees and contingency. Overall the investment is ${w.lang.toFixed(1)} times the equipment.`,
       "This is the model's biggest choice. Lighter NREL-style factors give a cheaper plant; pharmaceutical-grade vessels a much dearer one (the Capital estimate control)."],
      "cost = reference cost × (size / reference size)^0.7",
      "the same factors, from his table of facility classes. Cultivated meat sits in the costlier cell-culture classes."),
    step(8, "Money",
      `Running costs plus a capital charge give $${w.msp >= 100 ? n0(w.msp) : w.msp.toFixed(2)} per kg; paying for the plant is ${pc(w.capital)} of it.`,
      ["The capital charge is the yearly payment that repays the investment with a return: 7.5% over 10 years means 14.6% of the investment every year.",
       "Maintenance and insurance add 9% of the investment a year (Humbird). Running costs cover sugar, ammonia, energy, water, waste and staff.",
       "The minimum selling price divides it all by the output. It includes a return on capital but no profit margin."],
      "price = (running costs + fixed costs + 0.146 × investment) / kg made per year",
      "exactly the same money step."),
  ].join("");
}

function drawMethod() {
  const c = D.checks, m = x => money(x), k = x => Math.round(x).toLocaleString("en-US");
  const step = (title, line, body) => `<details class="step"><summary><b>${title}.</b> ${line}</summary><div class="body">${body}</div></details>`;
  $("method-body").innerHTML = [
    step("Where the numbers come from", "Public data only, each with a source and a note of the kind of evidence.",
      `<p>The prices on this page come straight from the model in the report, run at every lever setting the sliders offer, so they match the report and can be reproduced from the repository. The titers needed to reach a price are estimated between those runs, and the starting-point buttons move to the nearest run.</p>
       <p>Every input has a range and a source: a measurement, a published plant design or patent, a company claim or survey, an analogy or engineering judgment, or a guess. Guesses are few and listed in the report.</p>
       <p>Market prices are trade statistics (UN Comtrade, Eurostat, USDA) for whey, egg white and casein, and reported prices for the scarce proteins.</p>`),
    step("The scenarios", "Four cases, never mixed: the best published strain, the base design, what companies assume, and a best case.",
      `<p><b>Best published strain:</b> the highest titer in peer-reviewed papers. <b>Base design:</b> Intelligen's published plant design (30 g/L in 72 hours). <b>What companies assume:</b> the 42 g/L average in companies' own cost models (GFI 2025). <b>Best case:</b> every assumed limit at its best at once, on a larger plant; not a floor, and far above any published strain. It needs a different plant from the one the levers describe, so it appears in the reference table, not on the levers.</p>`),
    step("How the model was checked", `It reproduces the real cost of baker's yeast (${m(c.yeast[0])} against ${m(c.yeast[1])} per kg) and lands within ${Math.round(100 * Math.abs(c.intelligen[0] / c.intelligen[1] - 1))}% of a published PF design.`,
      `<div class="tablewrap"><table><thead><tr><th>Check</th><th class="r">This model</th><th class="r">Published</th></tr></thead><tbody>
       <tr><td>Baker's yeast, cost per kg (Humbird's model; market price less a 33% margin)</td><td class="r">${m(c.yeast[0])}</td><td class="r">${m(c.yeast[1])}</td></tr>
       <tr><td>Intelligen 2025 ovalbumin design, $ per kg powder</td><td class="r">${m(c.intelligen[0])}</td><td class="r">${m(c.intelligen[1])}</td></tr>
       <tr><td>NREL 2011 enzyme plant, oxygen per kg protein (mol)</td><td class="r">${k(c.o2_nrel[0])}</td><td class="r">${k(c.o2_nrel[1])}</td></tr>
       <tr><td>NREL 2011 enzyme plant, $ per kg protein</td><td class="r">${m(c.nrel[0])}</td><td class="r">${m(c.nrel[1])}</td></tr>
       <tr><td>Voutilainen 2021 ovalbumin design, € per t protein</td><td class="r">${k(c.vout[0])}</td><td class="r">${k(c.vout[1])}</td></tr>
       <tr><td>Capital per m³ of fermenter, $ (Liberation Labs, scaled to this plant)</td><td class="r">${k(c.plant[0])}</td><td class="r">${k(c.plant[1])}–${k(c.plant[2])}</td></tr>
       </tbody></table></div>
       <p>The mass balances match the published designs well. The money differs mostly through accounting: NREL and Voutilainen charge far lighter fixed costs. Each design is rebuilt from its own inputs; misses are recorded, not tuned away.</p>`),
    step("What the model leaves out", "R&D, licences, approval, sales, start-up, failed batches and the extra cost of a first plant.",
      `<p>Secretion is held steady in the simple model; the Detailed mode ties it to growth. Protein modifications such as phosphorylation are not priced. Few strain parameters are measured; most come from published designs and company averages.</p>
       <p>The author built the model with an AI assistant, and AI reviewers audited it; no human expert has reviewed it yet. Code, data and the full report are in the open pf-tea repository.</p>`),
  ].join("");
}

function drawOptions() {
  const o = D.options[prodKey()];
  if (!o) { $("opt").innerHTML = ""; $("opt-note").textContent = ""; return; }
  const row = (k, x, note) => `<tr><td>${k}</td><td class="r">${x == null ? "–" : money(x)}</td><td>${note || ""}</td></tr>`;
  $("opt").innerHTML = `<thead><tr><th>Case (base titer unless noted)</th><th class="r">$/kg protein</th><th>What it means</th></tr></thead><tbody>` +
    row("Simple model (base case)", o.base, "steady secretion while barely growing, as in published plant designs") +
    row("Large tank loses 6.5% of its growth yield", o.loss, "mixing gradients in big vessels (George et al. 1998, baker's yeast)") +
    row("Secretion tied to growth", o.coupled, `the cells must secrete ${o.q_need.toFixed(1)} mg per g per hour while growing at ${Math.round(100 * D.mu_ref)}% an hour: ${(o.q_need / D.q_demo).toFixed(1)} times the best published strain`) +
    row(`Best published strain (${D.q_demo} mg/g/h), best fed-batch design`, o.demo, o.demo_titer ? `the titer then reaches only ${o.demo_titer.toFixed(1)} g/L` : "") +
    row("Same strain, run continuously", o.cont, "fed and harvested continuously for 10 days instead of in batches") + "</tbody>";
  $("opt-note").textContent = "Detailed rows are sensitivities: the growth link and the tank loss come from single published strains. The Model switch above shows the detailed physics across all titers and production times.";
}

const GROUP_NAME = {"capital": "Capital charge (repaying the plant)", "maintenance + insurance": "Maintenance and insurance",
  "labour": "Staff", "glucose": "Glucose", "other materials": "Other materials and waste disposal", "utilities": "Energy and water"};
const gname = g => GROUP_NAME[g] || g;
function drawBreakdown(v) {
  const bar = $("bar"), tb = $("breakdown");
  if (!v) { bar.innerHTML = ""; tb.innerHTML = ""; return; }
  const tot = v[2].reduce((a, b) => a + b, 0);
  bar.innerHTML = v[2].map((x, i) => `<div style="flex:${Math.max(x, 0)} 0 0;background:var(${SERIES[i]})" title="${gname(G.groups[i])}: ${money(x)}"></div>`).join("");
  tb.innerHTML = `<thead><tr><th>Cost item</th><th class="r">$ ${unitWord()}</th><th class="r">Share</th></tr></thead><tbody>` +
    v[2].map((x, i) => `<tr><td><span style="display:inline-flex;align-items:center;gap:8px"><i class="sw" style="background:var(${SERIES[i]})"></i>${gname(G.groups[i])}</span></td><td class="r">${moneyU(x)}</td><td class="r">${(100 * x / tot).toFixed(0)}%</td></tr>`).join("") +
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
  s += `<text x="${(m.l + W - m.r) / 2}" y="${H - 4}" text-anchor="middle" class="lbl">titer at harvest (g/L; log scale: equal steps are equal multiples)</text>`;
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
    D.context.map(c => `<tr><td>${c.label}</td><td class="r">${money(c.lo)}–${money(c.hi)}</td><td>${c.when || ({A: "measured", B: "published design", C: "company claim or survey", D: "analogy or judgment", E: "guess"}[c.grade] || c.grade)}</td><td>${curP == null ? "–" : curP < c.lo ? "cheaper" : curP <= c.hi ? "within the range" : curP < 1.05 * c.hi ? "at the top edge" : (curP / c.hi).toFixed(1) + "× the top"}</td></tr>`).join("") + "</tbody>";
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
    $(a).addEventListener("input", e => { S[a] = +e.target.value; unpress(); render(); });
  }
  for (const a of ["product", "convention", "site"]) {
    document.querySelectorAll(`input[name=${a}]`).forEach(el => el.addEventListener("change", e => {
      S[a] = +e.target.value;
      unpress();
      if (a === "product") {                         // jump to the protein's own base point; the table follows the protein
        S = Object.assign(baseFor(S.product), {convention: S.convention, site: S.site});
        REFP = prodKey(); $("r-" + REFP).checked = true; drawRef();
      }
      render();
    }));
  }
  document.querySelectorAll("input[name=unit]").forEach(el => el.addEventListener("change", e => { UNIT = +e.target.value; render(); }));
  if (!DG) { $("m-d").disabled = true; $("phys-hint").textContent += " (Detailed runs are not in this build.)"; }
  document.querySelectorAll("input[name=physics]").forEach(el => el.addEventListener("change", e => {
    PHYS = +e.target.value;
    const det = PHYS === 1;
    $("fs-capital").disabled = det; $("fs-site").disabled = det; $("Y_ps").disabled = det;
    if (det) { S.convention = 0; S.site = 0; S.Y_ps = baseFor(S.product).Y_ps; $("c-h").checked = true; $("s-us").checked = true; }
    render();
  }));
  document.querySelectorAll("input[name=refp]").forEach(el => el.addEventListener("change", e => { REFP = e.target.value; drawRef(); }));
  for (const k of ["best", "base", "ind", "lim"]) $("pre-" + k).addEventListener("click", () => preset(k));
  $("yourprice").addEventListener("input", yourPrice);
  $("reset").addEventListener("click", () => {
    S = baseFor(S.product);
    document.querySelectorAll("input[type=radio]").forEach(el => { if (el.name !== "refp" && el.name !== "physics") el.checked = +el.value === (el.name === "unit" ? UNIT : S[el.name]); });
    render();
  });
  drawMethod();
  $("gen").textContent = `Model results generated ${D.generated}. The page holds ${G.values.length.toLocaleString("en-US")} simple-model runs${DG ? " and " + DG.values.length.toLocaleString("en-US") + " detailed-model runs" : ""} (repository pf-tea).`;
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
