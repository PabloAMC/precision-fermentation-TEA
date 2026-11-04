"""Write docs/panel.html: scripts/panel_template.html with results/panel_data.json inlined (no network needed).

Run: .venv/bin/python scripts/build_panel.py [--data results/panel_data.json] [--out docs/panel.html]
Design: docs/PANEL_DESIGN.md. The data come from scripts/panel_data.py.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(data: Path, out: Path) -> int:
    tpl = (ROOT / "scripts/panel_template.html").read_text()
    d = json.loads(data.read_text())
    spec = importlib.util.spec_from_file_location("panel_data", ROOT / "scripts/panel_data.py")
    pd = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pd)
    for prod, x in d["products"].items():                # display names: edited without rerunning the grid
        x.pop("short", None)
        x.update(pd.pr_info(prod))
    js = json.dumps(d, separators=(",", ":"), allow_nan=False, ensure_ascii=False)
    js = js.replace("</", "<\\/")                        # keep the JSON from closing its <script> element
    assert tpl.count("/*DATA*/") == 1
    html = tpl.replace("/*DATA*/", js)
    out.write_text(html)
    return len(html.encode())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "results/panel_data.json"))
    ap.add_argument("--out", default=str(ROOT / "docs/panel.html"))
    a = ap.parse_args()
    n = build(Path(a.data), Path(a.out))
    print(f"wrote {a.out} ({n / 1e6:.1f} MB)")
