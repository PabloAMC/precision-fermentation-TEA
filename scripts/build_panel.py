"""Write docs/panel.html: scripts/panel_template.html with results/panel_data.json inlined (no network needed).

Run: .venv/bin/python scripts/build_panel.py [--data results/panel_data.json] [--out docs/panel.html]
Design: docs/PANEL_DESIGN.md. The data come from scripts/panel_data.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(data: Path, out: Path) -> int:
    tpl = (ROOT / "scripts/panel_template.html").read_text()
    js = data.read_text().replace("</", "<\\/")          # keep the JSON from closing its <script> element
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
