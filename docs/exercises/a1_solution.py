"""Answer key for exercise A1 (rebuild Intelligen's $39/kg ovalbumin). SPOILERS.

Run:  .venv/bin/python docs/exercises/a1_solution.py

All inputs are quoted from intelligen_ovalbumin2025
(references/reports/Intelligen_2025_ovalbumin_TEA.pdf; printed page numbers, PDF page =
printed + 1) unless marked ASSUMPTION. The assumptions are the ones the exercise hands out
as hints; they are not stated in the paper.
"""

# ------------------------------------------------------------------ inputs (quoted)
OUTPUT_KG = 1_000_000          # kg powder / yr (p.16, Table 2)
BATCH_KG = 2_923.98            # kg powder / batch (Table 2)
MOISTURE, PURITY = 0.05, 0.99  # powder moisture; purity on a dry basis (p.9)
UF_REJECTION, UF_CF = 0.995, 5.0   # OVA rejection coefficient; ~5x concentration (p.8)
PRECIP, BASKET = 0.90, 0.99        # fraction precipitated; precipitate retained (pp.8-9)
SOLUBILITY_G_L = 50                # "practical solubility limit" of OVA (p.8)
AOC = 38_988_000               # $/yr operating cost (Table 2)
CREDITS = 2_662_212            # $/yr fertilizer credit (Table 2)
TCI = 91_996_000               # $ total capital investment (Table 2)
LANG = 4.0                     # DFC = 4 x purchased equipment cost (p.16)
STARTUP_FRAC = 0.05            # start-up and validation = 5% of DFC (p.17)
WC_DAYS = 30                   # working capital = 30 days of labour, materials, utilities,
                               # waste treatment (p.17)
PIE = {"facility": 0.44, "materials": 0.21, "utilities": 0.15, "labour": 0.07,
       "waste": 0.07, "consumables": 0.05, "qc": 0.01}          # Figure 6 (p.18)
MATERIALS = 8_122_940          # $/yr (Table 3)
GLUCOSE_KG_YR, GLUCOSE_USD = 13_021_171, 4_691_528             # Table 3
UTILITIES = 5_876_327          # $/yr (Table 4)
POWER_MWH = 27_077             # Table 4
CHILLED_T = 6_182_685          # t/yr chilled water (Table 4)
V_END_M3, TITER, DCW = 107.0, 30.0, 92.0   # broth m3, g/L OVA, g/L cells at harvest (p.7)
V_START_M3 = 41.523            # working volume at the start of the growth phase (p.6)
GROWTH_H = 36                  # growth phase, h (p.5); the expression phase is 72 h (p.6)
# Eq. (1) growth, per 100 g glucose reacted: -> 40 g cells, 54.56 g O2 consumed (p.7)
# Eq. (2) expression, per 100 g glucose: -> 8 g cells + 28 g OVA + 4 g HCP, 53.51 g O2 (p.7)
Y_X_GROWTH, O2_GROWTH = 0.40, 0.5456
Y_P_EXPR, Y_X_EXPR, O2_EXPR = 0.28, 0.08, 0.5351
CONVERSION = 0.99              # fraction of fed glucose that reacts (p.7)

# ------------------------------------------------------------ ASSUMPTIONS (hints)
DEPREC_YEARS, SALVAGE = 10, 0.05    # straight line; SuperPro-style default, not in paper
INSURANCE, LOCAL_TAX, FACTORY = 0.01, 0.02, 0.05   # fractions of DFC per year, same
HEAT_MJ_PER_MOL_O2 = 0.46           # textbook rule (see docs/PRIMER.md)
CP_WATER = 4.18                     # kJ/kg/K
# Humbird 2021 conventions (humbird2021 p.39 for the CCF, p.46 for the rest): CCF 7.5%,
# 10 y; maintenance 4% TCI; insurance + tax 5% TCI.
HUMBIRD_CCF = 0.075 / (1 - 1.075 ** -10)
HUMBIRD_MAINT, HUMBIRD_INS = 0.04, 0.05
NREL_USD_KG = 4.24                  # NREL on-site cellulase, $/kg protein, 2007$ (humbird2011 p.41)
MODEL_OTR_CAP = 150                 # the model's O2-transfer cap, mmol/L/h (data/pf/base.yaml)


def line(label, value, unit="", fmt="{:,.2f}"):
    print(f"  {label:58s} {fmt.format(value):>14s} {unit}")


print("PART 1 - accounting")
print(" 1.1 Figure 6 slices")
slices = {k: v * AOC for k, v in PIE.items()}
for k, v in slices.items():
    line(f"{k}", v / 1e6, f"M$/yr  = {v / OUTPUT_KG:5.2f} $/kg")
line("check: raw materials, Table 3 vs pie", MATERIALS / slices["materials"], "ratio", "{:.3f}")
line("check: utilities, Table 4 vs pie", UTILITIES / slices["utilities"], "ratio", "{:.3f}")

print(" 1.2 capital chain")
wc = WC_DAYS / 365 * (slices["labour"] + MATERIALS + UTILITIES + slices["waste"])
dfc = (TCI - wc) / (1 + STARTUP_FRAC)
pec = dfc / LANG
line("working capital (30/365 of labour+materials+utilities+waste)", wc / 1e6, "M$")
line("direct fixed capital DFC = (TCI - WC)/1.05", dfc / 1e6, "M$")
line("purchased equipment cost PEC = DFC/4", pec / 1e6, "M$")

print(" 1.3 facility-dependent cost from DFC")
deprec = dfc * (1 - SALVAGE) / DEPREC_YEARS
fixed = dfc * (INSURANCE + LOCAL_TAX + FACTORY)
maint = slices["facility"] - deprec - fixed
line("depreciation (10 y, 5% salvage)", deprec / 1e6, "M$/yr")
line("insurance 1% + local tax 2% + factory expense 5% of DFC", fixed / 1e6, "M$/yr")
line("maintenance needed to close to 44% of AOC", maint / 1e6, "M$/yr")
line("  = as % of PEC", 100 * maint / pec, "%/yr", "{:.1f}")
line("  = as % of DFC", 100 * maint / dfc, "%/yr", "{:.1f}")

print(" 1.4 Humbird's conventions instead of SuperPro's facility-dependent cost")
humbird_fac = TCI * (HUMBIRD_CCF + HUMBIRD_MAINT + HUMBIRD_INS)
recast = (AOC - slices["facility"] + humbird_fac) / OUTPUT_KG
line(f"capital charge {HUMBIRD_CCF:.3f} + maint 0.04 + ins/tax 0.05 of TCI", humbird_fac / 1e6, "M$/yr")
line("unit cost, Humbird convention", recast, "$/kg powder")
line("change vs $38.99", 100 * (recast / (AOC / OUTPUT_KG) - 1), "%", "{:+.0f}")

print(" 1.5 per kg of protein")
ova_frac = (1 - MOISTURE) * PURITY
line("OVA mass fraction of powder", ova_frac, "", "{:.3f}")
line("gross unit cost per kg OVA", AOC / OUTPUT_KG / ova_frac, "$/kg OVA")
line("net of fertilizer credit, per kg OVA", (AOC - CREDITS) / OUTPUT_KG / ova_frac, "$/kg OVA")
line("Humbird convention, per kg OVA", recast / ova_frac, "$/kg OVA")

print("\nPART 2 - balances")
batches = OUTPUT_KG / BATCH_KG
ova_broth = TITER * V_END_M3                     # kg per batch (g/L == kg/m3)
ova_product = BATCH_KG * ova_frac
line("batches per year", batches, "", "{:.0f}")
line("2.1 OVA in broth per batch", ova_broth, "kg", "{:,.0f}")
line("    pure OVA in powder per batch", ova_product, "kg", "{:,.0f}")
line("    overall downstream recovery", ova_product / ova_broth, "", "{:.3f}")
uf_yield = UF_CF ** -(1 - UF_REJECTION)       # retained fraction when concentrating CF-fold
line("    UF retention at 5x (rejection 0.995)", uf_yield, "", "{:.3f}")
steps = uf_yield * PRECIP * BASKET
line("    UF x precipitation x basket", steps, "", "{:.3f}")
line("    unaccounted for: overall / listed steps", ova_product / ova_broth / steps, "", "{:.3f}")
line("    harvest volume that would close the balance", ova_product / (steps * TITER),
     "m3 (paper: 'approximately 107')", "{:.1f}")

glc_expr = ova_broth / Y_P_EXPR                  # glucose reacted in expression phase
cells_expr = glc_expr * Y_X_EXPR
cells_growth = DCW * V_END_M3 - cells_expr       # cell death (2%) and seed train ignored
glc_growth = cells_growth / Y_X_GROWTH
glc_fed = (glc_expr + glc_growth) / CONVERSION
line("2.2 glucose reacted, expression phase", glc_expr, "kg/batch", "{:,.0f}")
line("    glucose reacted, growth phase", glc_growth, "kg/batch", "{:,.0f}")
line("    share of glucose spent on growing cells", glc_growth / (glc_growth + glc_expr), "", "{:.2f}")
line("    glucose fed (99% conversion)", glc_fed, "kg/batch", "{:,.0f}")
line("    overall yield, OVA in broth / glucose fed", ova_broth / glc_fed, "g/g", "{:.3f}")
line("    annual glucose, this balance", glc_fed * batches / 1e3, "t/yr", "{:,.0f}")
line("    annual glucose syrup, Table 3", GLUCOSE_KG_YR / 1e3, "t/yr", "{:,.0f}")
line("    ratio balance / Table 3", glc_fed * batches / GLUCOSE_KG_YR, "", "{:.2f}")
line("    glucose cost per kg powder (Table 3)", GLUCOSE_USD / OUTPUT_KG, "$/kg")

o2_kg = O2_GROWTH * glc_growth + O2_EXPR * glc_expr
o2_mol = o2_kg / 32 * 1000
line("2.3 O2 consumed per batch", o2_kg, "kg", "{:,.0f}")
line("    O2 per kg OVA in broth", o2_mol / ova_broth, "mol/kg (NREL: 84)", "{:.0f}")
heat_gj = o2_mol * HEAT_MJ_PER_MOL_O2 / 1000
line("    metabolic heat per batch", heat_gj, "GJ", "{:,.0f}")
line("    average duty over the 108 h culture", heat_gj * 1e9 / (108 * 3600) / 1e3, "kW", "{:,.0f}")

chilled_kg_batch = CHILLED_T * 1000 / batches
dT = heat_gj * 1e6 / (chilled_kg_batch * CP_WATER)
line("2.4 chilled water per batch", chilled_kg_batch / 1e3, "t", "{:,.0f}")
line("    temperature rise that carries exactly the metabolic heat", dT, "K", "{:.1f}")

line("2.5 electricity per kg powder", POWER_MWH * 1000 / OUTPUT_KG, "kWh/kg (NREL: 9)", "{:.1f}")

print("\nREBUILD (workbook rows R0-R5), maintenance at a typical 6% of PEC")
R0 = 0.06
r1 = glc_fed * batches * 0.36 + (MATERIALS - GLUCOSE_USD)
r2 = deprec + fixed + R0 * pec
r4 = slices["labour"] + slices["waste"] + slices["consumables"] + slices["qc"]
r5 = (r1 + r2 + UTILITIES + r4) / OUTPUT_KG
line("R1 raw materials, glucose from the balance", r1 / 1e6, "M$/yr")
line("R2 facility-dependent", r2 / 1e6, "M$/yr")
line("R5 rebuilt unit cost", r5, f"$/kg ({100 * (r5 / (AOC / OUTPUT_KG) - 1):+.1f}%)")
swap = (AOC - slices["facility"] + r2) / OUTPUT_KG
line("  swapping only maintenance to 6% of PEC", swap, f"$/kg ({100 * (swap / (AOC / OUTPUT_KG) - 1):+.1f}%)")
# How much can R5 test? R1-R4 reuse the paper's totals; only the maintenance rate and the
# glucose tonnage are the student's own. Solve for the range that keeps R5 within +-20%.
fixed_r5 = (MATERIALS - GLUCOSE_USD) + deprec + fixed + UTILITIES + r4
hi_r5 = 1.2 * AOC
line("  part of R5 fixed by the paper's totals", fixed_r5 / OUTPUT_KG, "$/kg")
line("  R5 stays within 20% for maintenance up to",
     (hi_r5 - fixed_r5 - glc_fed * batches * 0.36) / pec, "of PEC/yr (glucose from the balance)",
     "{:.2f}")
line("  R5 stays within 20% for annual glucose up to",
     (hi_r5 - fixed_r5 - R0 * pec) / 0.36 / 1e6, "kt/yr (maintenance 6% of PEC)", "{:.0f}")
line("  R5 with zero maintenance and zero glucose", fixed_r5 / OUTPUT_KG,
     f"$/kg ({100 * (fixed_r5 / AOC - 1):+.1f}%, still within 20%)")

print("\nPART 3 - rough what-ifs (see A1_SOLUTION.md for the reasoning)")
unit = AOC / OUTPUT_KG
# 3.1 titer 60 g/L, same batch time and overall yield. First the physics, phase by phase. The
# growth phase burns most of the O2 in a third of the time. The broth grows from 41.5 m3 towards
# the 107 m3 harvest volume, so dividing by 107 m3 gives a lower bound on its average uptake.
o2_growth_kmol = O2_GROWTH * glc_growth / 32
our_growth_lo = o2_growth_kmol * 1000 / GROWTH_H / V_END_M3
line("3.1 growth-phase O2 per batch (Eq. 1)", o2_growth_kmol,
     f"kmol = {O2_GROWTH * glc_growth:,.0f} kg", "{:,.1f}")
line("    growth-phase OUR over the 107 m3 harvest volume", our_growth_lo,
     "mmol/L/h (a lower bound)", "{:.0f}")
line("    ... over the 41.5 m3 starting volume", o2_growth_kmol * 1000 / GROWTH_H / V_START_M3,
     "mmol/L/h", "{:.0f}")
line("    growth OUR at twice the titer (2x cells), 107 m3", 2 * our_growth_lo,
     "mmol/L/h (a lower bound)", "{:.0f}")
line("    the model's O2-transfer cap (data/pf/base.yaml)", MODEL_OTR_CAP, "mmol/L/h", "{:.0f}")
line("    jacket limit at 136 m3 (PRIMER sec. 5.3, no agitation heat)", 53, "mmol/L/h", "{:.0f}")
line("    60 g/L vs OVA practical solubility (p.8)", 60 / SOLUBILITY_G_L, "x the limit", "{:.1f}")
# If it were feasible anyway. ASSUMPTIONS: fermentation + clarification carry ~55% of capital
# and scale with broth volume at exponent 0.6; volume-driven materials (everything except
# glucose and ammonium sulfate) halve; utilities unchanged (same O2 per kg, more power per
# mol O2 at higher OUR); labour -10%, waste -30%, consumables -40%.
fac_titer = slices["facility"] * (0.45 + 0.55 * 0.5 ** 0.6)
mat_titer = GLUCOSE_USD + 1_659_807 + 0.5 * (MATERIALS - GLUCOSE_USD - 1_659_807)
t31 = (fac_titer + mat_titer + 1.0 * UTILITIES + 0.9 * slices["labour"] + 0.7 * slices["waste"]
       + 0.6 * slices["consumables"] + slices["qc"]) / OUTPUT_KG
line("    titer x2 if it were feasible, rough", t31, f"$/kg ({100 * (t31 / unit - 1):+.0f}%)")
# 3.2 scale x10. ASSUMPTIONS: capital exponent 0.8 overall (fermenters numbered up,
# DSP scaled up); labour x3; QC x3; everything else per-kg unchanged.
t32 = (slices["facility"] * 10 ** (0.8 - 1) + MATERIALS + UTILITIES + slices["labour"] * 0.3
       + slices["waste"] + slices["consumables"] + slices["qc"] * 0.3) / OUTPUT_KG
line("3.2 scale x10, rough", t32, f"$/kg ({100 * (t32 / unit - 1):+.0f}%)")
variable = (MATERIALS + UTILITIES + slices["waste"] + slices["consumables"]) / OUTPUT_KG
line("    materials + utilities + waste + consumables (do not scale)", variable, "$/kg")
# 3.3 the gap to NREL, per kg of protein on both sides (step 1.5 for Intelligen)
ova_usd_kg = AOC / OUTPUT_KG / ova_frac
line("3.3 gap per kg protein: Intelligen OVA - NREL cellulase", ova_usd_kg - NREL_USD_KG, "$/kg")
line("    ratio", ova_usd_kg / NREL_USD_KG, "x", "{:.1f}")
