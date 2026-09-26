"""Extract the constants and reference values we use from Humbird's SI workbook.

Run:  .venv/bin/python scripts/extract_humbird_si.py
Reads references/papers/Humbird2021_cultured_meat_SI.xlsm (cached values) and writes:
  data/thermo/compounds.yaml        compound table (sheet Phys, rows 8-50)
  tests/fixtures/humbird_A1.json    cached values of sheet A.1 used by the replication test
Every value keeps its sheet!cell locator so it can be audited against the workbook.
"""
import json
import warnings
from pathlib import Path

import yaml
from openpyxl import load_workbook

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
SI = ROOT / "references/papers/Humbird2021_cultured_meat_SI.xlsm"
wv = load_workbook(SI, data_only=True)

# ---------------------------------------------------------------- compounds (Phys sheet)
phys = wv["Phys"]
compounds = {}
for r in range(8, 51):
    name = phys.cell(r, 1).value
    if not name:
        continue
    rec = {k: (phys.cell(r, c).value or 0) for k, c in
           [("C", 3), ("H", 4), ("O", 5), ("N", 6), ("S", 7), ("charge", 9)]}
    rec["gamma"] = phys.cell(r, 10).value
    rec["dHf_kJ_mol"] = phys.cell(r, 11).value
    rec["dGf_kJ_mol"] = phys.cell(r, 12).value
    rec["mw"] = phys.cell(r, 2).value
    rec["locator"] = f"Phys!A{r}:L{r}"
    compounds[name] = rec
header = ("# Compound table copied from Humbird (2021) SI workbook, sheet Phys (rows 8-50):\n"
          "# elemental formula, degree of reduction (gamma, per molecule, NH3/CO2/H2O reference),\n"
          "# standard enthalpy and Gibbs energy of formation (kJ/mol, aqueous or solid state as named).\n"
          "# Humbird's own sources for these are listed in the sheet (Guan & Kemp, Alberty, Aspen,\n"
          "# Atkins, Burnham, eQuilibrator, Battley). Grade B (published design basis).\n")
(ROOT / "data/thermo/compounds.yaml").write_text(header + yaml.safe_dump(compounds, sort_keys=False))

# ---------------------------------------------------------------- A.1 reference values
a1 = wv["A.1"]
cells = {
    # stoichiometry
    "anab": ["A7", "A8", "A9", "A10", "A11", "A12", "A13"],
    "combined": ["A31", "A32", "A33", "A34", "A35", "A36", "A37"],
    "misc": ["C3", "H3", "I3", "J3", "K3", "D26", "D27", "J14", "J22", "F69", "F70", "F80",
             "F81", "F82", "F91", "F92", "F75", "F76", "J94", "J95", "J96", "J97",
             "H101", "H102", "G135", "G136", "G137", "Q134", "K135", "K136", "K137",
             "C144", "F145", "C146", "E149", "C150", "E150", "K150", "E152", "E153", "E154",
             "C155", "C156", "E157", "E158", "I158", "M164", "H164", "I164", "I165", "H166",
             "H167", "H168", "I168", "H169", "I169", "H170", "I170", "I171", "I172", "I173",
             "I174", "C178", "C179", "C180", "C181", "C185", "C191", "C193", "C194", "C196",
             "C197", "D200", "D201", "D202", "D203", "H200", "H201", "H202", "H203", "D207",
             "H207", "H212", "H213", "H214", "H215", "G228", "G229", "G230", "G231", "G232",
             "G240", "G242", "G244", "G245", "I245", "I247", "I249", "I250", "D258", "E258",
             "G261", "G262", "G263", "G264", "G265", "G266", "G267", "G268", "G269", "G270",
             "G271", "G272", "G274", "N2", "N4", "N7", "N8", "N10", "N11", "N12", "N13", "N14",
             "H282", "M282", "O282", "Q282", "BD282", "BF282", "BF283", "BF286", "Z286",
             "W286", "BI286", "BL286", "D286", "F284", "F287"],
}
out = {"source": "Humbird 2021 SI, sheet A.1 (cached values)", "cells": {}}
for group in cells.values():
    for c in group:
        out["cells"][c] = a1[c].value
seed = {}
for r in range(107, 134):
    seed[r] = {col: a1[f"{col}{r}"].value for col in "ABCDEFGHIJKLMNOPQRT"}
out["seed_table"] = seed
sim_cols = ["A", "B", "C", "D", "F", "G", "H", "K", "L", "M", "O", "Q", "W", "X", "Y", "Z", "AA",
            "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AM", "AN", "AP", "AQ", "AR", "AS", "AU",
            "AV", "AW", "AX", "AY", "AZ", "BA", "BD", "BF", "BI", "BK", "BL"]
out["sim"] = [{c: a1[f"{c}{r}"].value for c in sim_cols} for r in range(287, 321)]
(ROOT / "tests/fixtures/humbird_A1.json").write_text(json.dumps(out, indent=1))
print("wrote compounds.yaml and humbird_A1.json:", len(compounds), "compounds,", len(out["sim"]), "sim rows")
