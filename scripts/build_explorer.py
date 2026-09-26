"""Build docs/explorer.html: a self-contained explorer over precomputed model runs.

Reads results/explorer_grid.json (scripts/explorer_grid.py) and results/analyses.json and
injects them into a dependency-free HTML/JS/SVG page. The page only looks values up: every
number it shows is a model run, never a JavaScript re-implementation.
Run:  .venv/bin/python scripts/build_explorer.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G = json.loads((ROOT / "results/explorer_grid.json").read_text())
R = json.loads((ROOT / "results/analyses.json").read_text())

inc = R["benchmarks"]["incumbents"]
ref = []
for label, key, prod in [("Best public academic strain (BLG: Yao 2026, ethanol-induced)", "academic/blg", "blg"),
                         ("Best public academic strain (T. reesei)", "academic/ova", "ova"),
                         ("Industry benchmark, 42 g/L", "industry/blg", "blg"), ("Industry benchmark, 42 g/L", "industry/ova", "ova")]:
    ref.append(dict(label=label, product=prod, titer=R["scenarios"][key]["design"]["titer"],
                    humbird=R["scenarios"][key]["msp_ccf"], light=R["scenarios"][key + "/light"]["msp_ccf"]))
for prod in ("blg", "ova"):
    ref.insert(2 if prod == "blg" else 3, dict(label="Base case, 30 g/L (Intelligen design)", product=prod, titer=30.0,
                                              humbird=R["base"][prod]["msp_ccf"], light=R["base_light"][prod]["msp_ccf"]))
for prod in ("blg", "ova"):
    h, l_ = R["physical_limit"][f"{prod}/humbird"], R["physical_limit"][f"{prod}/light"]
    ref.append(dict(label="Physical limit, 100 kt/yr", product=prod, titer=h["titer"], humbird=h["msp_ccf"], light=l_["msp_ccf"]))
L = R["lactoferrin"]["cases"]
ref.append(dict(label="Contrast: lactoferrin, 250 t/yr, cation exchange", product="lf", titer=L["lf/humbird"]["design"]["titer"],
                humbird=L["lf/humbird"]["msp_ccf"], light=L["lf/light"]["msp_ccf"]))
EQ = R["equivalents"]["sources"]


def src_band(name, label):
    ser = EQ[name]["prices"][label]
    yr = max(ser, key=int)
    return dict(label=label, lo=min(ser.values()), hi=max(ser.values()), last=ser[yr], year=int(yr))

DATA = {
    "grid": G,
    "bands": {"blg": dict(label="Whey protein (WPC80/WPI)", lo=inc["whey"]["band"][0], hi=inc["whey"]["band"][1],
                          years=inc["whey"]["years"],
                          spot=(inc["whey"]["spot"][0]["usd_kg_protein"] if inc["whey"]["spot"] else None)),
              "ova": dict(label="Dried egg white", lo=inc["egg"]["band"][0], hi=inc["egg"]["band"][1],
                          years=inc["egg"]["years"], spot=None)},
    "ceiling": {p: dict(zip(map(str, R["required_t_prods"]), R["titer_ceiling"][p])) for p in ("blg", "ova")},
    "equiv": {"blg": dict(per="litre of milk", grams=EQ["milk"]["all_protein_g"], what="all the protein in a litre of milk",
                          bands=[src_band("milk", "US farm milk (all-milk price)"), src_band("milk", "US retail whole milk")]),
              "ova": dict(per="egg", grams=EQ["egg"]["all_protein_g"], what="the egg-white protein of one large egg",
                          bands=[src_band("egg", "US wholesale eggs (New York, Grade A large)"),
                                 src_band("egg", "US retail eggs (Grade A large)")])},
    "ref": ref,
    "generated": R["generated"],
}

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
  --band-blg: #e3edf9; --band-ova: #fbe6dc; --spot: #898781;
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
    --band-blg: #1b293a; --band-ova: #38251d; --spot: #9a9f9b;
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
  --band-blg: #1b293a; --band-ova: #38251d; --spot: #9a9f9b;
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
.notes b { color: var(--ink); font-weight: 600; }
@media (max-width: 860px) {
  .summary, .main { grid-template-columns: minmax(0, 1fr); }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap">
  <header>
    <h1>Precision Fermentation Cost Explorer</h1>
    <p class="lede">Food-grade &beta;-lactoglobulin (the main whey protein) and ovalbumin (the main egg-white protein), made by a secreting
    <i>K.&nbsp;phaffii</i> strain in 200&nbsp;m&sup3; fed-batch fermenters, 10&nbsp;kt of protein a year, dried to a concentrate.
    Move the strain levers and see the minimum selling price, whether a real fermenter can run the design, and how the price compares with whey, egg white, milk and eggs.</p>
  </header>

  <section class="summary" aria-live="polite">
    <div class="panel">
      <h2>Minimum selling price</h2>
      <div class="price"><span class="big num" id="msp">$0</span><span class="unit" id="msp-unit">per kg protein, 2025 dollars</span></div>
      <div class="chips" id="chips"></div>
    </div>
    <div class="panel compare" id="compare"></div>
  </section>

  <section class="main">
    <div class="panel">
      <form id="controls" onsubmit="return false">
        <fieldset>
          <legend>Protein</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="product" id="p-blg" value="0" checked><label for="p-blg">&beta;-lactoglobulin</label>
            <input type="radio" name="product" id="p-ova" value="1"><label for="p-ova">Ovalbumin</label>
          </div>
        </fieldset>
        <fieldset>
          <legend>Capital estimate</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="convention" id="c-h" value="0" checked><label for="c-h">Price-anchored (base)</label>
            <input type="radio" name="convention" id="c-l" value="1"><label for="c-l">Design-report</label>
          </div>
          <p class="hint">Price-anchored: Humbird's facility factors, which reproduce the market price of baker's yeast. Design-report: vendor-quote fermenters and the smaller fixed costs of NREL-style studies, as in most published PF analyses.</p>
        </fieldset>
        <fieldset>
          <legend>Show the price</legend>
          <div class="seg" role="radiogroup">
            <input type="radio" name="unit" id="u-kg" value="0" checked><label for="u-kg">per kg protein</label>
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
        <h2>What the price is made of</h2>
        <div class="bar" id="bar" aria-hidden="true"></div>
        <div class="tablewrap" style="margin-top:10px"><table id="breakdown"></table></div>
      </div>
    </div>
  </section>

  <section class="panel" style="margin-top:16px">
    <h2>Reference cases from the report</h2>
    <div class="tablewrap"><table id="ref"></table></div>
  </section>

  <section class="notes">
    <p><b>What this is.</b> A cost with a capital charge of 14.6% of investment a year (7.5% over 10 years), not a market price. It excludes R&amp;D, licences, regulatory work, sales and first-of-a-kind premiums.</p>
    <p><b>Physical limits.</b> A 200&nbsp;m&sup3; fermenter transfers at most 150&nbsp;mol&nbsp;O&#8322;/m&sup3;/h (a design cap) and removes at most 25&nbsp;kW/m&sup3; of heat; a batch must start at least 30% full, and cells secrete at most 40&nbsp;mg of protein per gram per hour. A design that breaks any of these is marked; its price is shown but cannot be achieved as designed.</p>
    <p><b>Incumbent prices.</b> Export unit values from UN&nbsp;Comtrade and Eurostat, per kg of protein (80% protein for whey, 81.1% for egg white), in 2025 dollars. The 2026 whey spot is from USDA Dairy Market News.</p>
    <p><b>Milk and egg equivalents.</b> The price of replacing the protein of a litre of milk (33.7&nbsp;g) or of one egg's white (3.64&nbsp;g) with PF protein, beside what the litre or the egg costs. This flatters milk and eggs as competitors: fat, lactose and yolk carry part of their price, and whey is a by-product of cheese.</p>
    <p class="hint" id="gen"></p>
  </section>
</div>

<script>
const D = __DATA__;
const G = D.grid, AX = G.axes, ORDER = G.order;
const LABELS = {product: ["blg", "ova"], convention: ["humbird", "light"], site: ["us_midwest", "eu_nw"]};
const BASE = {product: 0, convention: 0, site: 0, titer: AX.titer.indexOf(30), t_prod: AX.t_prod.indexOf(72), X_prod: AX.X_prod.indexOf(107), Y_ps: AX.Y_ps.indexOf(0.465)};
let S = Object.assign({}, BASE);
let UNIT = 0;   // 0: $/kg protein; 1: per litre of milk (BLG) or per egg (OVA)
const conv = () => UNIT ? D.equiv[prodKey()].grams / 1000 : 1;
const moneyU = (x, d) => UNIT ? "$" + (x * conv()).toFixed(x * conv() < 1 ? 3 : 2) : money(x, d);
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
  const eq = D.equiv[prodKey()];
  $("msp-unit").textContent = UNIT ? `per ${eq.per} (PF protein replacing ${eq.what}), 2025 dollars` : "per kg protein, 2025 dollars";
  $("u-src-l").textContent = "per " + eq.per;
  $("u-hint").textContent = UNIT ? `Multiplies $/kg by ${eq.grams.toFixed(2)} g / 1000.` : "";
  // comparison panel
  const base = at(Object.assign({}, BASE, {product: S.product}));
  const rows = [];
  if (v) {
    let pos;
    if (v[0] < band.lo) pos = "below the whole band";
    else if (v[0] <= band.hi) pos = "inside the band";
    else pos = (v[0] / band.hi).toFixed(1) + "× the top of the band";
    if (!UNIT) {
      rows.push([`${band.label}, ${band.years[0]}–${band.years[1]} trade prices`, `${money(band.lo, 1)}–${money(band.hi, 1)}`]);
      rows.push(["This design", pos]);
      if (band.spot) rows.push(["Whey spot price, 2026 peak (USDA)", money(band.spot, 0) + (v[0] <= band.spot ? ", undercut" : ", not reached")]);
    } else {
      for (const b of eq.bands) rows.push([`${b.label}, ${b.year} (2015–${b.year} range)`, `$${b.last.toFixed(2)} ($${b.lo.toFixed(2)}–${b.hi.toFixed(2)})`]);
      rows.push(["This design", moneyU(v[0])]);
    }
    if (base) rows.push(["Change from the base case", (v[0] >= base[0] ? "+" : "−") + moneyU(Math.abs(v[0] - base[0]))]);
  }
  $("compare").innerHTML = `<h2 style="margin:0 0 2px">${UNIT ? "Against milk and eggs" : "Against the incumbent"}</h2>` +
    rows.map(r => `<div class="row"><span class="k">${r[0]}</span><span class="v${/^[+−]?\$[\d.,–$]+$/.test(r[1]) ? " num" : ""}">${r[1]}</span></div>`).join("");
  drawChart(band);
  drawBreakdown(v);
}

function drawBreakdown(v) {
  const bar = $("bar"), tb = $("breakdown");
  if (!v) { bar.innerHTML = ""; tb.innerHTML = ""; return; }
  const tot = v[2].reduce((a, b) => a + b, 0);
  bar.innerHTML = v[2].map((x, i) => `<div style="flex:${Math.max(x, 0)} 0 0;background:var(${SERIES[i]})" title="${G.groups[i]}: ${money(x)}"></div>`).join("");
  tb.innerHTML = `<thead><tr><th>Cost item</th><th class="r">${UNIT ? "$ per " + D.equiv[prodKey()].per : "$/kg"}</th><th class="r">Share</th></tr></thead><tbody>` +
    v[2].map((x, i) => `<tr><td><span style="display:inline-flex;align-items:center;gap:8px"><i class="sw" style="background:var(${SERIES[i]})"></i>${G.groups[i]}</span></td><td class="r">${moneyU(x)}</td><td class="r">${(100 * x / tot).toFixed(0)}%</td></tr>`).join("") +
    `<tr><td><b>Total</b></td><td class="r"><b>${moneyU(v[0])}</b></td><td class="r">100%</td></tr></tbody>`;
}

function drawChart(band0) {
  let band = band0;
  const svg = $("chart"), W = 640, H = 300, m = {l: 52, r: 16, t: 14, b: 38};
  const k = conv();
  const pts = AX.titer.map((t, i) => { const v0 = at(Object.assign({}, S, {titer: i})); return {t, i, v: v0 ? [v0[0] * k, v0[1], v0[2]] : null}; }).filter(p => p.v);
  if (UNIT) { const b0 = D.equiv[prodKey()].bands[0]; band = {label: b0.label, lo: b0.lo, hi: b0.hi, spot: null, years: [2015, b0.year]}; }
  const ys = pts.map(p => p.v[0]).concat([band.lo, band.hi]);
  let y0 = Math.min(...ys) * 0.8, y1 = Math.max(...ys) * 1.15;
  y0 = Math.max(y0, UNIT ? 0.005 : 1); y1 = Math.min(Math.max(y1, band.hi * 1.3), UNIT ? 100 : 3000);
  const lx = Math.log, X = t => m.l + (lx(t) - lx(2)) / (lx(110) - lx(2)) * (W - m.l - m.r);
  const Y = y => H - m.b - (lx(y) - lx(y0)) / (lx(y1) - lx(y0)) * (H - m.t - m.b);
  let s = "";
  const bandCol = prodKey() === "blg" ? "var(--band-blg)" : "var(--band-ova)";
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
    s += `<text x="${W - m.r - 4}" y="${Y(band.spot) - 5}" text-anchor="end" class="lbl">whey spot, 2026</text>`;
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
      tip.innerHTML = `<b>${p.t} g/L</b>: ${UNIT ? "$" + p.v[0].toFixed(3) + " per " + D.equiv[prodKey()].per : money(p.v[0]) + "/kg"}<br>${FLAG[p.v[1]][1]}`;
      tip.hidden = false;
      const r = svg.getBoundingClientRect(), k = r.width / W;
      const x = X(p.t) * k, y = Y(p.v[0]) * k;
      tip.style.left = Math.min(Math.max(0, x - 70), r.width - 170) + "px";
      tip.style.top = Math.max(0, y - 58) + "px";
    });
    c.addEventListener("mouseleave", () => { tip.hidden = true; });
    c.addEventListener("click", () => { S.titer = p.i; render(); });
  });
  $("chart-table").innerHTML = `<thead><tr><th class="r">Titer g/L</th><th class="r">${UNIT ? "$ per " + D.equiv[prodKey()].per : "$/kg"}</th><th>Status</th></tr></thead><tbody>` +
    pts.map(p => `<tr><td class="r">${p.t}</td><td class="r">${UNIT ? "$" + p.v[0].toFixed(3) : money(p.v[0])}</td><td>${FLAG[p.v[1]][1]}</td></tr>`).join("") + "</tbody>";
}

function drawRef() {
  const PN = {blg: "β-lactoglobulin", ova: "Ovalbumin", lf: "Lactoferrin"};
  $("ref").innerHTML = `<thead><tr><th>Case</th><th>Protein</th><th class="r">Titer g/L</th><th class="r">Price-anchored $/kg</th><th class="r">Design-report $/kg</th></tr></thead><tbody>` +
    D.ref.map(r => `<tr><td>${r.label}</td><td>${PN[r.product]}</td><td class="r">${+r.titer.toFixed(2)}</td><td class="r">${money(r.humbird)}</td><td class="r">${money(r.light)}</td></tr>`).join("") + "</tbody>";
}

function init() {
  for (const a of ["titer", "t_prod", "X_prod", "Y_ps"]) {
    const vals = AX[a];
    $("t-" + a).innerHTML = [vals[0], vals[vals.length - 1]].map(x => `<span>${a === "Y_ps" ? x.toFixed(2) : x}</span>`).join("");
    $(a).addEventListener("input", e => { S[a] = +e.target.value; render(); });
  }
  for (const a of ["product", "convention", "site"]) {
    document.querySelectorAll(`input[name=${a}]`).forEach(el => el.addEventListener("change", e => { S[a] = +e.target.value; render(); }));
  }
  document.querySelectorAll("input[name=unit]").forEach(el => el.addEventListener("change", e => { UNIT = +e.target.value; render(); }));
  $("reset").addEventListener("click", () => {
    S = Object.assign({}, BASE, {product: S.product});
    document.querySelectorAll("input[type=radio]").forEach(el => { el.checked = +el.value === (el.name === "unit" ? UNIT : S[el.name]); });
    render();
  });
  $("gen").textContent = `Model runs generated ${D.generated}. Grid: ${G.values.length.toLocaleString("en-US")} runs of the full model (repository pf-tea).`;
  drawRef();
  render();
}
init();
</script>
"""

out = ROOT / "docs/explorer.html"
out.write_text(HTML.replace("__DATA__", json.dumps(DATA, separators=(",", ":"))))
print("wrote", out.relative_to(ROOT), f"{out.stat().st_size / 1e3:.0f} kB")
