"""Reproduce every computed number quoted in docs/PRIMER.md.

Run:  .venv/bin/python docs/primer_numbers.py

Every input is either QUOTED from a source on disk (key from references/INDEX.md plus a
page) or marked ILLUSTRATIVE: a textbook-typical value used only to teach. Illustrative
values are not model inputs and must never be copied into data/assumptions.yaml.
Page numbers are the printed page numbers of each document.
"""
import math

# ---------------------------------------------------------------- constants
MW = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007, "S": 32.06}  # g/mol
# Degree of reduction per atom with CO2, H2O and NH3 as the reference state.
# Sulfur (0.005-0.01 per C) is ignored: it moves gamma by <2%.
GAMMA = {"C": 4, "H": 1, "O": -2, "N": -3}
HEAT_PER_MOL_O2_MJ = 0.46   # ILLUSTRATIVE textbook rule: Doran (2013) ~460 kJ/mol O2;
                            # Cooney et al. (1969) 0.12 kcal/mmol ~ 0.50 MJ/mol. Verify in B.
P_ATM = 101325.0            # Pa


def cmol_mass(f):
    """Mass of one C-mole (formula normalised to one carbon)."""
    return sum(MW[e] * n for e, n in f.items())


def gamma(f):
    return sum(GAMMA.get(e, 0) * n for e, n in f.items())


def header(t):
    print(f"\n=== {t}")


# ------------------------------------------------ 1. stoichiometry (NREL 2011)
# humbird2011 p.38: elemental compositions used in NREL's Area 400 design.
GLUCOSE = {"C": 1, "H": 2, "O": 1}                              # CH2O
PROTEIN = {"C": 1, "H": 1.59, "N": 0.24, "O": 0.42, "S": 0.01}  # cellulase
CELLS = {"C": 1, "H": 1.645, "O": 0.445, "N": 0.205, "S": 0.005}  # T. reesei
GENERIC_CELLS = {"C": 1, "H": 1.8, "O": 0.5, "N": 0.2}          # textbook average biomass

header("1. C-mole masses and degrees of reduction")
for name, f in [("glucose", GLUCOSE), ("cellulase protein", PROTEIN),
                ("T. reesei cells", CELLS), ("generic cells CH1.8O0.5N0.2", GENERIC_CELLS)]:
    print(f"{name:30s} M = {cmol_mass(f):6.2f} g/C-mol   gamma = {gamma(f):.2f}")

# humbird2011 p.38: overall molar selectivity of glucose carbon:
# 31% protein, 4% cell mass, 65% CO2; "yielding 0.24 kg enzyme protein/kg glucose".
s_p, s_x, s_co2 = 0.31, 0.04, 0.65
header("2. NREL electron balance -> yield and O2 demand")
y_gg = s_p * cmol_mass(PROTEIN) / cmol_mass(GLUCOSE)
# electrons in = electrons in products + 4 per O2
n_o2 = (gamma(GLUCOSE) - s_p * gamma(PROTEIN) - s_x * gamma(CELLS)) / 4  # mol O2 / C-mol glucose
o2_per_kg = n_o2 / (s_p * cmol_mass(PROTEIN)) * 1000                   # mol O2 / kg protein
print(f"carbon balance: {s_p + s_x + s_co2:.2f} (should be 1.00)")
print(f"yield from selectivity: {y_gg:.3f} g protein / g glucose (NREL states 0.24)")
print(f"O2 from electron balance: {n_o2:.3f} mol O2 / C-mol glucose "
      f"-> {o2_per_kg:.1f} mol O2 / kg protein = {o2_per_kg * 32 / 1000:.2f} kg O2 / kg")
print(f"respiratory quotient CO2/O2 = {s_co2 / n_o2:.2f}")
# humbird2011 p.38: 8.4 kmol/h O2 for a reactor making 12,000 kg protein in 120 h online.
o2_nrel = 8.4e3 / (12000 / 120)
print(f"NREL's own figure: 8.4 kmol/h / {12000 / 120:.0f} kg/h = {o2_nrel:.0f} mol O2 / kg "
      f"(balance differs by {100 * (o2_per_kg / o2_nrel - 1):+.1f}%)")

# upper bound on yield: every electron of glucose ends up in protein, no energy cost
y_electron_max = gamma(GLUCOSE) * cmol_mass(PROTEIN) / (gamma(PROTEIN) * cmol_mass(GLUCOSE))
print(f"electron-limited ceiling (no ATP cost): {y_electron_max:.2f} g/g")
# rough ATP correction (ILLUSTRATIVE, to be redone properly in Phase C2):
atp_per_residue = 4.3          # ATP equivalents per peptide bond (textbook)
residue_mass = 110.0           # g/mol, mean amino-acid residue
atp_per_g_protein = atp_per_residue / residue_mass            # mol ATP / g protein
for po, atp_per_glc in [(1.0, 16.0), (1.5, 22.0)]:            # ATP per glucose respired
    glc_for_atp = atp_per_g_protein / atp_per_glc * 180.16    # g glucose / g protein
    y = 1 / (1 / y_electron_max + glc_for_atp)
    print(f"  with polymerisation cost only, P/O~{po}: ~{y:.2f} g/g")

header("3. Heat released per kg protein (NREL basis)")
heat_mj = o2_nrel * HEAT_PER_MOL_O2_MJ
print(f"{o2_nrel:.0f} mol O2/kg x {HEAT_PER_MOL_O2_MJ} MJ/mol = {heat_mj:.1f} MJ/kg "
      f"= {heat_mj / 3.6:.1f} kWh(thermal)/kg protein")
q_reactor_mw = 8.4e3 * HEAT_PER_MOL_O2_MJ / 3600               # MJ/h -> MW
print(f"one 300 m3 reactor at 8.4 kmol O2/h: {q_reactor_mw:.2f} MW of metabolic heat")

header("4. Productivity and O2 uptake rate (NREL)")
v_total, v_frac_end, v_frac_start = 300.0, 0.80, 0.50   # humbird2011 p.37
cycle_h = 24 + 96 + 48                                     # growth + production + offline
prod = 12000 / (v_total * v_frac_end * cycle_h)            # kg/m3/h == g/L/h
print(f"volumetric productivity = 12,000 kg / ({v_total * v_frac_end:.0f} m3 x {cycle_h} h) "
      f"= {prod:.2f} g/L/h (NREL states 0.30)")
our_max = 8.4e3 / (v_total * v_frac_start)                 # mol/m3/h == mmol/L/h
print(f"peak OUR at 50% fill = 8.4 kmol/h / {v_total * v_frac_start:.0f} m3 = {our_max:.0f} mmol/L/h")
print(f"peak production rate = {our_max:.0f} / {o2_nrel:.0f} mol/kg = {our_max / o2_nrel:.2f} g/L/h "
      f"(vs {prod:.2f} averaged over the whole 168 h cycle)")
otr_ceiling = 150  # ILLUSTRATIVE OTR ceiling, mmol/L/h (Phase B will source the range)
print(f"O2-limited ceiling at an illustrative OTR of {otr_ceiling} mmol/L/h: "
      f"{otr_ceiling / o2_nrel:.2f} g/L/h")

header("5. Dissolved O2: solubility and the kLa needed")
# ILLUSTRATIVE: O2 solubility in air-saturated fresh water at 30 C, 1 atm ~7.56 mg/L.
c_star_30 = 7.56 / 32
print(f"C* (air, 30 C, fresh water) ~ {c_star_30:.3f} mmol/L; salts lower it by ~10-20% (textbook)")
print(f"dissolved O2 lasts {c_star_30 / our_max * 3600:.0f} s at saturation, "
      f"{0.063 / our_max * 3600:.0f} s at NREL's 30%-of-saturation setpoint (OUR {our_max:.0f})")
# NREL assumptions, p.38: C* = pO2 / H with H = 1 atm/(mmol/L); DO setpoint 0.063 mmol/L;
# top at 1 atm, bottom adds hydrostatic head. Geometry from Table 19: D = 5.75 m.
area = math.pi * 5.75 ** 2 / 4
h_liq = v_total * v_frac_start / area
p_btm = 1 + 1000 * 9.81 * h_liq / P_ATM
c_top, c_btm, c_l = 0.21, 0.21 * p_btm, 0.063
lm = ((c_btm - c_l) - (c_top - c_l)) / math.log((c_btm - c_l) / (c_top - c_l))
kla_needed = our_max / lm
print(f"liquid height at 50% fill {h_liq:.1f} m -> bottom pressure {p_btm:.2f} atm")
print(f"log-mean driving force {lm:.3f} mmol/L -> kLa needed = {kla_needed:.0f} 1/h "
      f"({kla_needed / 3600:.3f} 1/s)  [NREL's method: pressure only]")
# NREL's method ignores O2 depletion in the rising gas. Air supplied (p.39): 0.83 Nm3/s per
# reactor averaged over the whole cycle incl. 48 h offline; online flow is 168/120 higher.
for label, air in [("cycle-average air", 0.83), ("online air", 0.83 * 168 / 120)]:
    n_air = air * 3600 / 22.414                       # kmol/h
    o2_in = 0.2095 * n_air
    util = 8.4 / o2_in
    y_out = (o2_in - 8.4) / n_air                      # RQ ~1: total moles roughly unchanged
    c_top_d = y_out / 0.2095 * c_top
    lm_d = ((c_btm - c_l) - (c_top_d - c_l)) / math.log((c_btm - c_l) / (c_top_d - c_l))
    print(f"  with gas-side depletion ({label}: O2 utilisation {util:.0%}, exit gas "
          f"{100 * y_out:.1f}% O2): kLa needed = {our_max / lm_d:.0f} 1/h")

header("6. What a stirred tank can deliver: van't Riet (1979) correlations")
# ILLUSTRATIVE textbook correlations, SI units (kLa 1/s, P/V W/m3, u_s m/s):
#   coalescing (water-like):        kLa = 0.026 (P/V)^0.4 u_s^0.5
#   non-coalescing (salty media):   kLa = 0.002 (P/V)^0.7 u_s^0.2
# van 't Riet fitted these on vessels up to a few m3 and P/V 500-10,000 W/m3: using them at
# 150 m3 is an extrapolation. Pairing the 600 kW maximum (p.39) with 50% fill is our inference.
pv = 600e3 / (v_total * v_frac_start)   # NREL max agitator 600 kW, assumed at 50% fill
us = 2.0 / 60                            # NREL superficial gas velocity 200 cm/min (p.39)
kla_c = 0.026 * pv ** 0.4 * us ** 0.5 * 3600
kla_nc = 0.002 * pv ** 0.7 * us ** 0.2 * 3600
print(f"P/V = {pv:.0f} W/m3, u_s = {us:.3f} m/s")
print(f"kLa coalescing {kla_c:.0f} 1/h, non-coalescing {kla_nc:.0f} 1/h "
      f"(needed {kla_needed:.0f}; viscous fungal broth delivers less than either)")
for kla in (kla_c, kla_nc):
    print(f"  OTR at kLa {kla:.0f} 1/h and the NREL driving force: {kla * lm:.0f} mmol/L/h")

header("7. Air compressor power check (NREL Table 21: 1,408 kW)")
q_air = 9 * 0.83                 # 9 reactors x 0.83 standard m3/s average (p.39)
k = 1.4                          # ratio of heat capacities for air
eta = 0.70                       # ILLUSTRATIVE isentropic efficiency
w_isen = k / (k - 1) * P_ATM * q_air * ((3.0) ** ((k - 1) / k) - 1)  # to 3 atm (p.40)
print(f"air {q_air:.2f} Nm3/s compressed 1 -> 3 atm: isentropic {w_isen / 1e3:.0f} kW, "
      f"at eta {eta}: {w_isen / eta / 1e3:.0f} kW")
# Sensitivity: the formula wants the actual inlet volume (0 C standard m3 understates it at
# 20 C), and seed reactors take another 10% of the production air (p.39).
w_hi = w_isen * 293.15 / 273.15 * 1.10 / eta
print(f"with a 20 C inlet and seed-train air: {w_hi / 1e3:.0f} kW at eta {eta}; matching NREL's "
      f"1,408 kW needs eta = {w_isen * 1.10 / 1.408e6:.2f} (0 C) to {w_isen * 293.15 / 273.15 * 1.10 / 1.408e6:.2f} (20 C)")

header("8. Implied chiller efficiency (NREL Table 21: chiller 1,587 kW)")
online = 120 / 168
heat_per_reactor_mw = q_reactor_mw * online + 0.26    # metabolic (time-averaged) + 260 kW agitation
heat_total = 9 * heat_per_reactor_mw
print(f"heat to remove ~ 9 x ({q_reactor_mw:.2f} x {online:.2f} + 0.26) = {heat_total:.1f} MW "
      f"-> implied chiller COP ~ {heat_total / 1.587:.1f} (seed reactors ignored)")

header("9. Why big vessels run out of cooling: jacket-limited OUR vs size")
# ILLUSTRATIVE: H/D = 2 (NREL geometry), 80% fill, jacket on the wetted wall only,
# U = 500 W/m2/K, chilled water with a 15 K mean temperature difference, and all heat
# metabolic (agitation heat ignored, which flatters large vessels).
U, dT = 500.0, 15.0
AGIT = 2000.0   # ILLUSTRATIVE agitation power, W per m3 of broth (NREL peaks at 4,000)
print(f"{'vessel m3':>10s} {'D m':>6s} {'wall m2':>8s} {'kW/m3':>7s} {'max OUR':>8s} "
      f"{'with 2 kW/m3 agitation':>23s}")
for v in (1, 10, 50, 100, 136, 300, 1000):
    d = (2 * v / math.pi) ** (1 / 3)
    wall = math.pi * d * (2 * d) * 0.8
    q_per_m3 = U * wall * dT / (0.8 * v)                        # W per m3 of broth
    our = q_per_m3 / (HEAT_PER_MOL_O2_MJ * 1e6) * 3600          # mol/m3/h
    our_ag = max(q_per_m3 - AGIT, 0) / (HEAT_PER_MOL_O2_MJ * 1e6) * 3600
    print(f"{v:10.0f} {d:6.2f} {wall:8.1f} {q_per_m3 / 1e3:7.1f} {our:8.0f} {our_ag:23.0f}")
print("-> per-volume cooling falls as V^(-1/3); big vessels need internal coils or "
      "external loops, which is what NREL specifies (p.37).")

header("10. Capital charge factor CCF = i / (1 - (1+i)^-n)")
for i, n, who in [(0.075, 10, "Humbird 2021"), (0.10, 10, ""), (0.10, 20, ""), (0.10, 30, "")]:
    ccf = i / (1 - (1 + i) ** -n)
    print(f"i = {i:.1%}, n = {n:2d} y: {ccf:.3f} of capital per year  {who}")

header("11. Six-tenths rule")
for ratio in (2, 10):
    print(f"x{ratio} capacity -> x{ratio ** 0.6:.2f} cost -> cost per unit capacity "
          f"x{ratio ** 0.6 / ratio:.2f}")

header("11b. Downstream recovery compounds")
print(f"five steps at 95% each: {0.95 ** 5:.2f} overall")

header("12. Sugar floor = sugar price / (yield x downstream recovery)")
# glucose prices: humbird2021 p.40 contract ~$0.25/kg; intelligen_ovalbumin2025 Table 3
# "glucose syrup" $0.36/kg (concentration not stated); gfi2025costs Table 6 DE95 $0.40/kg
# (used in its single-cell-protein model, p.58); humbird2011 Table 29 $0.2579/lb (2007$).
prices = (0.25, 0.36, 0.40, 0.2579 / 0.45359)
print(f"{'yield g/g':>10s}" + "".join(f"{p:>10.2f}" for p in prices) + "   ($/kg glucose)")
for y in (0.08, 0.15, 0.24, 0.40):
    print(f"{y:10.2f}" + "".join(f"{p / (y * 0.85):10.2f}" for p in prices)
          + "   $/kg protein at 85% recovery")
print(f"NREL's own sugar term (no downstream losses): {prices[3]:.3f} / 0.24 = "
      f"${prices[3] / 0.24:.2f}/kg protein; 57% of $4.24 = ${0.57 * 4.24:.2f}")
