"""Build docs/exercises/A1_intelligen_rebuild.xlsx, the fill-in workbook for exercise A1.

Run:  .venv/bin/python docs/exercises/build_a1_workbook.py
Every number on the Inputs sheet is quoted from intelligen_ovalbumin2025 (printed page
numbers; PDF page = printed + 1) or is a labelled hint. The answer key is a1_solution.py.
"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

OUT = Path(__file__).with_name("A1_intelligen_rebuild.xlsx")
FONT = "Arial"
BLUE, GREEN, BLACK, GREY = "0000FF", "008000", "000000", "666666"
YELLOW = PatternFill("solid", fgColor="FFFF00")
HEAD = PatternFill("solid", fgColor="D9D9D9")
SRC = "Intelligen 2025"

# (id, quantity, value, unit, number format, source)
INPUTS = [
    ("Plant and product", None, None, None, None),
    ("I1", "Annual output of powder", 1_000_000, "kg/yr", "#,##0", f"{SRC}, Table 2, p.16"),
    ("I2", "Batch size (powder)", 2923.98, "kg/batch", "#,##0.00", f"{SRC}, Table 2, p.16"),
    ("I3", "Recipe cycle time (a batch every)", 24, "h", "0", f"{SRC}, p.11"),
    ("I4", "Moisture in powder", 0.05, "fraction", "0.00", f"{SRC}, p.9"),
    ("I5", "Purity, dry basis", 0.99, "fraction", "0.00", f"{SRC}, p.9"),
    ("I6", "Assumed selling price", 50, "$/kg", "0.00", f"{SRC}, p.17"),
    ("Fermentation", None, None, None, None),
    ("I7", "Production fermenter vessel volume", 136, "m3", "0", f"{SRC}, p.5"),
    ("I8", "Number of production fermenters", 5, "-", "0", f"{SRC}, p.11"),
    ("I9", "Working volume at start of growth", 41.523, "m3", "0.000", f"{SRC}, p.5"),
    ("I10", "Broth volume at harvest", 107, "m3", "0", f"{SRC}, p.7"),
    ("I11", "OVA titer at harvest", 30, "g/L = kg/m3", "0", f"{SRC}, p.7"),
    ("I12", "Cell density at harvest (dry)", 92, "g/L = kg/m3", "0", f"{SRC}, p.7"),
    ("I13", "Growth phase", 36, "h", "0", f"{SRC}, p.5"),
    ("I14", "Expression phase", 72, "h", "0", f"{SRC}, p.6"),
    ("I15", "Aeration, growth phase", 1.2, "vvm", "0.0", f"{SRC}, p.5"),
    ("I16", "Aeration, expression phase", 1.6, "vvm", "0.0", f"{SRC}, p.6"),
    ("Stoichiometry, per 100 g glucose reacted", None, None, None, None),
    ("I17", "Growth: cells formed", 40, "g", "0.00", f"{SRC}, Eq. (1), p.7"),
    ("I18", "Growth: O2 consumed", 54.56, "g", "0.00", f"{SRC}, Eq. (1), p.7"),
    ("I19", "Expression: OVA formed", 28, "g", "0.00", f"{SRC}, Eq. (2), p.7"),
    ("I20", "Expression: cells formed", 8, "g", "0.00", f"{SRC}, Eq. (2), p.7"),
    ("I21", "Expression: host-cell protein formed", 4, "g", "0.00", f"{SRC}, Eq. (2), p.7"),
    ("I22", "Expression: O2 consumed", 53.51, "g", "0.00", f"{SRC}, Eq. (2), p.7"),
    ("I23", "Fraction of fed glucose that reacts", 0.99, "fraction", "0.00", f"{SRC}, p.7"),
    ("Downstream", None, None, None, None),
    ("I24", "Ultrafiltration: rejection coefficient of OVA", 0.995, "fraction", "0.000",
     f"{SRC}, p.8 (a rejection coefficient, not a step yield)"),
    ("I25", "Precipitation: fraction of OVA precipitated", 0.90, "fraction", "0.00", f"{SRC}, p.8"),
    ("I26", "Basket centrifuge: precipitate retained", 0.99, "fraction", "0.00", f"{SRC}, p.8-9"),
    ("Economics", None, None, None, None),
    ("I27", "Total capital investment (TCI)", 91_996_000, "$", "$#,##0", f"{SRC}, Table 2, p.16"),
    ("I28", "Lang factor (DFC / purchased equipment)", 4, "-", "0.0", f"{SRC}, p.16"),
    ("I29", "Start-up and validation", 0.05, "fraction of DFC", "0.00", f"{SRC}, p.17"),
    ("I30", "Working capital covers", 30, "days of labour+materials+utilities+waste", "0",
     f"{SRC}, p.17"),
    ("I31", "Annual operating cost (AOC)", 38_988_000, "$/yr", "$#,##0", f"{SRC}, Table 2, p.16"),
    ("I32", "Fertilizer credit", 2_662_212, "$/yr", "$#,##0", f"{SRC}, Table 2, p.16"),
    ("I33", "Unit production cost", 38.99, "$/kg powder", "0.00", f"{SRC}, Table 2, p.16"),
    ("I34", "Net unit production cost", 36.33, "$/kg powder", "0.00", f"{SRC}, Table 2, p.16"),
    ("Operating cost shares", None, None, None, None),
    ("I35", "Facility-dependent", 0.44, "share of AOC", "0%", f"{SRC}, Figure 6, p.18"),
    ("I36", "Raw materials", 0.21, "share of AOC", "0%", f"{SRC}, Figure 6, p.18"),
    ("I37", "Utilities", 0.15, "share of AOC", "0%", f"{SRC}, Figure 6, p.18"),
    ("I38", "Labour-dependent", 0.07, "share of AOC", "0%", f"{SRC}, Figure 6, p.18"),
    ("I39", "Waste treatment/disposal", 0.07, "share of AOC", "0%", f"{SRC}, Figure 6, p.18"),
    ("I40", "Consumables", 0.05, "share of AOC", "0%", f"{SRC}, Figure 6, p.18"),
    ("I41", "Laboratory/QC/QA", 0.01, "share of AOC", "0%", f"{SRC}, Figure 6, p.18"),
    ("Raw materials and utilities", None, None, None, None),
    ("I42", "Raw materials, total", 8_122_940, "$/yr", "$#,##0", f"{SRC}, Table 3, p.18"),
    ("I43", "Glucose syrup used", 13_021_171, "kg/yr", "#,##0", f"{SRC}, Table 3, p.18"),
    ("I44", "Glucose syrup price", 0.36, "$/kg", "0.00", f"{SRC}, Table 3, p.18"),
    ("I45", "Glucose syrup cost", 4_691_528, "$/yr", "$#,##0", f"{SRC}, Table 3, p.18"),
    ("I46", "Ammonium sulfate used", 9_221_148, "kg/yr", "#,##0", f"{SRC}, Table 3, p.18"),
    ("I47", "Ammonium sulfate cost", 1_659_807, "$/yr", "$#,##0", f"{SRC}, Table 3, p.18"),
    ("I48", "Utilities, total", 5_876_327, "$/yr", "$#,##0", f"{SRC}, Table 4, p.19"),
    ("I49", "Electricity used", 27_077, "MWh/yr", "#,##0", f"{SRC}, Table 4, p.19"),
    ("I50", "Electricity price", 90, "$/MWh", "0", f"{SRC}, Table 4, p.19"),
    ("I51", "Chilled water used", 6_182_685, "t/yr", "#,##0", f"{SRC}, Table 4, p.19"),
    ("I52", "Chilled water price", 0.40, "$/t", "0.00", f"{SRC}, Table 4, p.19"),
    ("Hints: assumptions NOT stated in the paper", None, None, None, None),
    ("H1", "Depreciation period (straight line)", 10, "yr", "0",
     "Assumption: common SuperPro default (Petrides); not stated in the paper"),
    ("H2", "Salvage value", 0.05, "fraction of DFC", "0.00", "Assumption: same"),
    ("H3", "Insurance", 0.01, "fraction of DFC per yr", "0.00", "Assumption: same"),
    ("H4", "Local taxes", 0.02, "fraction of DFC per yr", "0.00", "Assumption: same"),
    ("H5", "Factory expense", 0.05, "fraction of DFC per yr", "0.00", "Assumption: same"),
    ("H6", "Heat released per mol O2 consumed", 0.46, "MJ/mol", "0.00",
     "Textbook rule, docs/PRIMER.md sec. 3"),
    ("H7", "Heat capacity of water", 4.18, "kJ/kg/K", "0.00", "Standard value"),
    ("H8", "Humbird: rate of return i", 0.075, "fraction", "0.000", "Humbird 2021, p.39"),
    ("H9", "Humbird: plant life n", 10, "yr", "0", "Humbird 2021, p.39"),
    ("H10", "Humbird: maintenance", 0.04, "fraction of TCI per yr", "0.00", "Humbird 2021, p.46"),
    ("H11", "Humbird: insurance + tax", 0.05, "fraction of TCI per yr", "0.00",
     "Humbird 2021, p.46 and App. A"),
    ("H12", "NREL: O2 demand", 84, "mol O2/kg protein", "0", "docs/PRIMER.md sec. 3 (NREL 2011, p.38)"),
    ("H13", "NREL: electricity", 9, "kWh/kg protein", "0", "NREL 2011, Table 21, p.40"),
    ("H14", "GFI: egg-white protein, low", 15.6, "$/kg protein", "0.0", "GFI 2025, p.31"),
    ("H15", "GFI: egg-white protein, high", 59.4, "$/kg protein", "0.0", "GFI 2025, p.31"),
]

# (id, quantity, unit, hint)
STEPS = [
    ("Part 1 - accounting", None, None, None),
    ("1.1a", "Facility-dependent cost", "$/yr", "share (I35) x AOC (I31)"),
    ("1.1b", "Labour-dependent cost", "$/yr", "I38 x I31"),
    ("1.1c", "Waste treatment/disposal", "$/yr", "I39 x I31"),
    ("1.1d", "Consumables", "$/yr", "I40 x I31"),
    ("1.1e", "Laboratory/QC/QA", "$/yr", "I41 x I31"),
    ("1.1f", "Raw materials: Table 3 total / Figure 6 slice", "ratio", "should be close to 1"),
    ("1.2a", "Working capital", "$", "I30/365 x (labour + raw materials + utilities + waste)"),
    ("1.2b", "Direct fixed capital (DFC)", "$", "TCI = DFC + start-up (I29 x DFC) + working capital"),
    ("1.2c", "Purchased equipment cost (PEC)", "$", "DFC / Lang factor"),
    ("1.3a", "Depreciation", "$/yr", "DFC x (1 - H2) / H1"),
    ("1.3b", "Insurance + local taxes + factory expense", "$/yr", "DFC x (H3 + H4 + H5)"),
    ("1.3c", "Maintenance that closes the gap to 1.1a", "$/yr", "1.1a - 1.3a - 1.3b"),
    ("1.3d", "... as a fraction of PEC per year", "fraction/yr", "plausible? equipment upkeep is typically a few % to ~10%/yr"),
    ("1.4a", "Humbird capital charge factor", "fraction/yr", "i / (1 - (1+i)^-n) with H8, H9"),
    ("1.4b", "Humbird facility costs", "$/yr", "TCI x (1.4a + H10 + H11)"),
    ("1.4c", "Unit cost in Humbird's convention", "$/kg powder", "(AOC - 1.1a + 1.4b) / output"),
    ("1.5a", "OVA mass fraction of the powder", "fraction", "(1 - moisture) x purity"),
    ("1.5b", "Unit cost per kg of OVA", "$/kg OVA", "compare with GFI's egg-white band (H14-H15)"),
    ("Part 2 - mass and energy balances", None, None, None),
    ("2.1a", "Batches per year", "-", "output / batch size"),
    ("2.1b", "OVA in broth per batch", "kg", "titer x harvest volume (g/L = kg/m3)"),
    ("2.1c", "Pure OVA in powder per batch", "kg", "batch size x 1.5a"),
    ("2.1d", "Overall downstream recovery", "fraction",
     "2.1c / 2.1b; compare with UF retention 5^-(1-I24) at ~5x concentration, x I25 x I26"),
    ("2.2a", "Glucose reacted, expression phase", "kg/batch", "OVA made / (I19/100)"),
    ("2.2b", "Cells made, expression phase", "kg/batch", "2.2a x I20/100"),
    ("2.2c", "Cells made, growth phase", "kg/batch", "harvest cells (I12 x I10) - 2.2b; ignore cell death and seed train"),
    ("2.2d", "Glucose reacted, growth phase", "kg/batch", "2.2c / (I17/100)"),
    ("2.2e", "Glucose fed per batch", "kg/batch", "(2.2a + 2.2d) / I23"),
    ("2.2f", "Overall yield on glucose", "g OVA / g glucose", "2.1b / 2.2e; the expression phase alone gives 0.28"),
    ("2.2g", "Annual glucose", "kg/yr", "compare with Table 3 (I43)"),
    ("2.3a", "O2 consumed per batch", "kg", "2.2a x I22/100 + 2.2d x I18/100"),
    ("2.3b", "O2 per kg of OVA in broth", "mol/kg", "compare with NREL (H12)"),
    ("2.3c", "Metabolic heat per batch", "GJ", "mol O2 x H6"),
    ("2.3d", "Average cooling duty per fermenter", "kW", "over the 108 h culture (I13 + I14)"),
    ("2.4a", "Chilled water per batch", "kg", "I51 x 1000 / batches"),
    ("2.4b", "Temperature rise that carries exactly the metabolic heat", "K",
     "heat / (mass x H7); chilled-water loops typically run 5-10 K (textbook)"),
    ("2.5a", "Electricity per kg of powder", "kWh/kg", "compare with NREL (H13); why different?"),
    ("Rebuild of the unit cost (used by the Check sheet)", None, None, None),
    ("R0", "Your maintenance rate for the rebuild", "fraction of PEC/yr", "pick a typical value; do not copy 1.3d"),
    ("R1", "Raw materials", "$/yr", "2.2g x I44 + (I42 - I45)"),
    ("R2", "Facility-dependent", "$/yr", "1.3a + 1.3b + R0 x PEC"),
    ("R3", "Utilities", "$/yr", "Table 4 total (I48)"),
    ("R4", "Labour + waste + consumables + QC", "$/yr", "1.1b + 1.1c + 1.1d + 1.1e"),
    ("R5", "Rebuilt unit cost", "$/kg powder", "(R1 + R2 + R3 + R4) / output"),
]

PART3 = [
    ("3.1", "Titer doubles to 60 g/L at the same batch time and the same overall yield. First: "
            "is that physically possible? (O2 uptake per m3 vs PRIMER sec. 5.3-5.4; ovalbumin "
            "solubility, paper p.8.) Then: which slices of Figure 6 move, and roughly how much? "
            "Estimate the new $/kg."),
    ("3.2", "The plant is 10x larger (10,000 t/yr). Same questions. Remember the fermenters are "
            "already 136 m3: do you scale up or number up?"),
    ("3.3", "NREL's crude on-site cellulase costs $4.24/kg protein (2007$); Intelligen's purified "
            "ovalbumin $38.99/kg powder (2025$). List every difference between the two plants and "
            "rank them by how much of the ~9x gap you think each explains."),
    ("3.4", "Which three input numbers would you most want to verify before trusting $39/kg, and why?"),
]


def font(color=BLACK, bold=False, italic=False, size=10):
    return Font(name=FONT, color=color, bold=bold, italic=italic, size=size)


def widths(ws, cols):
    for i, w in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def header_row(ws, row, labels):
    for j, lab in enumerate(labels, start=1):
        c = ws.cell(row=row, column=j, value=lab)
        c.font, c.fill = font(bold=True), HEAD


wb = Workbook()

# ------------------------------------------------------------------ README
ws = wb.active
ws.title = "README"
widths(ws, [110])
lines = [
    ("Exercise A1 - Rebuild Intelligen's $39/kg ovalbumin", font(bold=True, size=14)),
    ("", None),
    ("Instructions: docs/exercises/A1_intelligen_rebuild.md. Source: "
     "references/reports/Intelligen_2025_ovalbumin_TEA.pdf (printed page n = PDF page n+1).", font()),
    ("Time: about 2 hours. Answer key: docs/exercises/A1_SOLUTION.md (open it after you finish).", font()),
    ("", None),
    ("How to work: fill each yellow cell on 'Workings' with a formula that references 'Inputs' "
     "or earlier answers.", font()),
    ("Row 4 of 'Workings' is a pre-filled example of the expected format. "
     "'Check' updates itself as you go.", font()),
    ("", None),
    ("Legend", font(bold=True)),
    ("Blue text: a number quoted from a source (do not edit).", font(color=BLUE)),
    ("Yellow cell: your answer.", font()),
    ("Black text: a formula.", font()),
    ("Green text: a formula that pulls from another sheet.", font(color=GREEN)),
    ("", None),
    ("Hints H1-H15 on 'Inputs' are assumptions or outside benchmarks, not numbers from the paper.",
     font(italic=True)),
]
for i, (text, f) in enumerate(lines, start=1):
    c = ws.cell(row=i, column=1, value=text)
    if f:
        c.font = f
ws.cell(row=11, column=1).fill = YELLOW

# ------------------------------------------------------------------ Inputs
wi = wb.create_sheet("Inputs")
widths(wi, [7, 46, 16, 34, 62])
header_row(wi, 1, ["ID", "Quantity", "Value", "Unit", "Source"])
addr = {}
r = 2
for item in INPUTS:
    if item[1] is None:                                  # section title
        c = wi.cell(row=r, column=1, value=item[0])
        c.font = font(bold=True)
        r += 1
        continue
    iid, qty, val, unit, fmt, src = item
    wi.cell(row=r, column=1, value=iid).font = font()
    wi.cell(row=r, column=2, value=qty).font = font()
    v = wi.cell(row=r, column=3, value=val)
    v.font, v.number_format = font(color=BLUE), fmt
    wi.cell(row=r, column=4, value=unit).font = font()
    wi.cell(row=r, column=5, value=src).font = font(color=GREY if iid.startswith("H") else BLACK)
    addr[iid] = f"Inputs!$C${r}"
    r += 1
wi.freeze_panes = "A2"

# ------------------------------------------------------------------ Workings
ww = wb.create_sheet("Workings")
widths(ww, [7, 52, 18, 20, 70])
header_row(ww, 1, ["Step", "Quantity", "Your answer", "Unit", "Hint"])
ww.cell(row=2, column=1, value="Fill the yellow cells with formulas. Blank cells are fine: "
        "Check only reports what you have filled.").font = font(italic=True, color=GREY)
# row 4: worked example of the expected format
ww.cell(row=4, column=1, value="Ex.").font = font(italic=True)
ww.cell(row=4, column=2, value="Example: glucose cost per kg of powder").font = font(italic=True)
ex = ww.cell(row=4, column=3, value=f"={addr['I45']}/{addr['I1']}")
ex.font, ex.number_format = font(color=GREEN), "0.00"
ww.cell(row=4, column=4, value="$/kg powder").font = font(italic=True)
ww.cell(row=4, column=5, value="Glucose cost (I45) / output (I1), typed as references to the "
        "Inputs sheet").font = font(italic=True)
step_addr = {}
r = 6
for sid, qty, unit, hint in STEPS:
    if qty is None:
        ww.cell(row=r, column=1, value=sid).font = font(bold=True)
        r += 1
        continue
    ww.cell(row=r, column=1, value=sid).font = font()
    ww.cell(row=r, column=2, value=qty).font = font()
    a = ww.cell(row=r, column=3)
    a.fill = YELLOW
    a.font = font()
    a.number_format = "0.000" if ("fraction" in unit or unit in ("ratio", "g OVA / g glucose")) else "#,##0.00"
    ww.cell(row=r, column=4, value=unit).font = font()
    h = ww.cell(row=r, column=5, value=hint)
    h.font, h.alignment = font(color=GREY), Alignment(wrap_text=True)
    step_addr[sid] = f"Workings!$C${r}"
    r += 1
ww.freeze_panes = "A2"

# ------------------------------------------------------------------ Check
wc = wb.create_sheet("Check")
widths(wc, [52, 18, 18, 14, 24])
header_row(wc, 1, ["Check (against the paper's own numbers)", "Yours", "Paper", "Difference", "Verdict"])
checks = [
    ("Sum of the seven cost slices ($/yr) vs AOC",
     f"=IF(COUNT({step_addr['1.1a']},{step_addr['1.1b']},{step_addr['1.1c']},{step_addr['1.1d']},"
     f"{step_addr['1.1e']})<5,\"\",{step_addr['1.1a']}+{step_addr['1.1b']}+{step_addr['1.1c']}+"
     f"{step_addr['1.1d']}+{step_addr['1.1e']}+{addr['I42']}+{addr['I48']})", f"={addr['I31']}", 0.02),
    ("TCI rebuilt from your DFC and working capital ($)",
     f"=IF(COUNT({step_addr['1.2a']},{step_addr['1.2b']})<2,\"\",{step_addr['1.2b']}*(1+{addr['I29']})"
     f"+{step_addr['1.2a']})", f"={addr['I27']}", 0.02),
    ("Annual glucose from your balance (kg/yr) vs Table 3",
     f"=IF({step_addr['2.2g']}=\"\",\"\",{step_addr['2.2g']})", f"={addr['I43']}", 0.20),
    ("Rebuilt unit cost ($/kg powder)  <- the exit criterion",
     f"=IF({step_addr['R5']}=\"\",\"\",{step_addr['R5']})", f"={addr['I33']}", 0.20),
]
for i, (label, mine, paper, tol) in enumerate(checks, start=2):
    wc.cell(row=i, column=1, value=label).font = font()
    m = wc.cell(row=i, column=2, value=mine)
    p = wc.cell(row=i, column=3, value=paper)
    for c in (m, p):
        c.font, c.number_format = font(color=GREEN), "#,##0.00"
    d = wc.cell(row=i, column=4, value=f"=IF(B{i}=\"\",\"\",B{i}/C{i}-1)")
    d.font, d.number_format = font(), "0.0%"
    v = wc.cell(row=i, column=5,
                value=f"=IF(D{i}=\"\",\"not filled yet\",IF(ABS(D{i})<={tol},\"within {tol:.0%}\","
                      f"\"outside {tol:.0%}: recheck\"))")
    v.font = font()
wc.cell(row=7, column=1, value="Tolerances: 2% for pure bookkeeping identities, 20% for "
        "reconstructions.").font = font(italic=True, color=GREY)

# ------------------------------------------------------------------ Part 3
w3 = wb.create_sheet("Part3")
widths(w3, [6, 70, 70])
header_row(w3, 1, ["Q", "Question (no spreadsheet needed; reason from the slices)", "Your notes"])
for i, (q, text) in enumerate(PART3, start=2):
    w3.cell(row=i, column=1, value=q).font = font()
    t = w3.cell(row=i, column=2, value=text)
    t.font, t.alignment = font(), Alignment(wrap_text=True, vertical="top")
    n = w3.cell(row=i, column=3)
    n.fill, n.font, n.alignment = YELLOW, font(), Alignment(wrap_text=True, vertical="top")
    w3.row_dimensions[i].height = 75

wb.save(OUT)
print(f"wrote {OUT}")
