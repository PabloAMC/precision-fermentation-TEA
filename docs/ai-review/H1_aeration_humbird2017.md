> AI reading pass (Claude, an AI model), 2026-09-27, run after the Phase F pre-review to read sources Pablo downloaded. Kept verbatim except local paths. Not a human review. Every finding acted on was re-checked against the source text, table images or workbook cells; decisions are in docs/REVIEW.md (follow-up section).

# Humbird, Davis & McMillan 2017 (aeration costs) vs our aeration model

**How to read the sources.** "p.N" is the PDF page; the printed manuscript page is N−1. "L" is the line number in `references/text/humbird2017.txt`. The paper's statements are paraphrased, with one short direct quote, to limit copying. Every number is given exactly as printed with its location, so each can be checked quickly.

Where a number did not come from the paper's text, it carries one of these tags:
- **[fig]**: read off Fig. 3 by pixel analysis of the embedded image, calibrated on the tick marks. Error is about ±0.01 kWh/kg O2 on panel a and ±$0.003/kg O2 on panel b.
- **[calc]**: my own arithmetic.
- **[run]**: our model in the audit worktree. Variants were changed in memory only; no files were edited.
- **[SI]**: cell values from Humbird's 2021 supplementary workbook, `references/papers/Humbird2021_cultured_meat_SI.xlsm` (read-only).

## Bottom line

- **What the paper gives, and what it doesn't.** It reports only the *total system* power per kg O2 delivered and the cost per kg O2, both against OUR. It gives no air rate (vvm), no agitator power per volume (P/V), no compressor/agitator split, no compressor efficiency and no headspace pressure.
- **kLa constants.** Ours (0.002, 0.7, 0.2) are exactly its Eq. 2.
- **Where our numbers sit.**
  - Our compressor + agitator energy at OUR 150 in a 200 m³ vessel is 0.50 kWh/kg O2 (2.40 kW/m³) [run].
  - That matches Humbird's own 2021 spreadsheet redo of this same analysis to within 1% [SI].
  - It is about 2.1× below what the 2017 simulations imply once the chilling of the reaction heat is removed: about 1.16 kWh/kg O2, or about 5.6 kW/m³ [calc].
  - On total power including all chilling, we are 27% below their 200 m³ stirred tank: 1.60 vs 2.21 kWh/kg O2.
- **Most likely cause (about 60% confidence).** The 2017 model could not set the dissolved O2 (DO) level. If I hold DO at about 50% of air saturation, our equations reproduce the 2017 200 m³ stirred-tank curve to within 0.03 kWh/kg O2 at all seven OURs I checked (10 to 150) [run]. The paper itself says real plants keep DO near zero. So the 2017 figure is a pessimistic bound, not a better base case.
- **Two defects in our code:**
  - **Compressor formula.** It is copied faithfully from Humbird 2021 SI cell A.1!BD287, but it uses 1.4 as both exponent and divisor where adiabatic compression uses (k−1)/k = 0.286. That overstates compressor power 1.6× at our pressure and about 2.1× at 1 barg back pressure.
  - **`aerate()` search.** It fails silently at DO setpoints of 50% of air saturation and above.
- **Effect on price.** The minimum selling price barely moves: even the full 2017 energy level adds $0.31/kg (+1.5%) [run].

## 1. What Humbird 2017 finds (paraphrased; every number exact)

### Method and assumptions

| Item | Value in paper | Location |
|---|---|---|
| Power users counted | Air compressor, air cooler, agitator (stirred tanks only), circulation pump, chiller scaled by cooling duty. Cooling tower excluded. | p.7, L297–305 |
| Stirred-tank kLa (Eq. 2; van 't Riet & Tramper 1991, "non-viscous") | kLa [1/s] = 0.002 (P/V [W/m³])^0.7 (u_s [m/s])^0.2, **with no temperature term**. The authors call the pre-factor and exponents adjustable per system, and note vessels above 100 m³ are outside the original fit range. | p.8, L324–354 |
| Bubble-column kLa (Eq. 3; Heijnen & van 't Riet 1984) | kLa = 0.32 u_s^0.7 µ_eff[cP]^−0.84 × 1.025^(T−20) | p.9, L360–368 |
| Scope | Bubble columns not normally recommended above 2 cP; the study is limited to non-viscous (aqueous) systems. | p.9, L370–374 |
| Reaction heat | About 110 kcal per mol O2, using glucose combustion as a stand-in for metabolism. | p.9, L382–386 |
| Optimisation | Stirred tank: agitation and gas velocity varied together to minimise total power. Bubble column: only one gas velocity fits each OUR. | p.9, L396–404 |
| Pressures | Compressor discharge is set by the liquid head plus line losses; no values given. Design pressure 45 psig and full vacuum is mechanical design only. **Headspace pressure and compressor efficiency are not stated.** | p.10, L414–416; p.23 |
| Other conditions | Inlet air 70% water-saturated; broth at 32 °C; pump-around loop with a 20 °C exchanger outlet. The chiller removes reaction heat plus agitator heat (applied power minus drive and bearing losses). Chiller electricity uses 1.24 hp per ton of refrigeration (Couper 2010). | p.10, L416–434 |
| Dissolved O2 | The steady-state DO is "implicitly a function of OUR and thus cannot be set independently". They add that real fed-batch operation controls aeration and agitation to hold DO near zero, where transfer is most efficient. | p.10, L442–450 |
| Working volume | Fixed 80% ungassed. | p.11, L469 |
| Cost basis | Installation factor 2.3; 13% annual capital charge; 8,400 h/y; electricity $0.06/kWh; maintenance 6% of installed capital; glucose excluded. | p.13–14, L574–603 |

### Vessel sizes and maximum OTR

- **Sizes studied:** 200, 500 and 1,000 m³ (p.6–7, L241–276).
  - Industry contacts put the largest stirred tanks in operation at 500 m³ or less, with an ultimate size around 1,000 m³.
  - Bubble columns up to 1,000 m³ are known to operate (p.6, L249–259).
- **Table 2 (p.23, L964–989):**
  - Stirred tank 200 m³: diameter 15 ft × tangent-to-tangent 40 ft, i.e. 4.57 × 12.19 m (H/D 2.67). 500 m³: 21 × 51 ft. 1,000 m³: 26 × 66.5 ft.
  - Bubble column 200 m³: 11.5 × 69 ft.
  - Agitator capital cost is plotted over 10–2,500 hp.
  - Bare-vessel cost (2014$): stirred tanks $442,000 / $974,000 / $1,631,000; bubble columns $412,000 / $905,000 / $1,691,000.
- **Maximum OTR:**
  - Simulations cover OUR 10–150 mmol/L-h for both reactor types.
  - Bubble columns are not considered above 150 because of jet flooding at high gas velocity (p.12, L536–540).
  - **No stirred-tank maximum is stated.**
  - The conclusions recommend 500–1,000 m³ and OTR 50–150 (p.15–16, L696–702).

### Results text

- **Stirred tanks:** specific power is nearly flat against OUR, partly thanks to the optimisation. 500 and 1,000 m³ differ by less than 5% (p.12, L541–548).
- **Bubble columns:** power rises more steeply with OTR, and is about 10% lower at 1,000 than at 500 m³ at high OTR (p.12–13, L548–558).
- **Scale:** system power is roughly linear in liquid volume, so economies of scale come from capital, not power (p.13, L558–566).
- **Bubble column vs stirred tank:**
  - Bubble columns are always cheaper to operate than same-size stirred tanks, by 10–20%, provided the process suits a bubble column.
  - Cost per kg O2 flattens out by about 50–75 mmol/L-h.
  - Scaling 200 → 500 m³ gives a significant saving; 500 → 1,000 m³ a smaller one (p.14, L609–631).
- **Where bubble columns don't fit:** the stirred-tank optimum is about 500 m³ at OTR above 50 (p.15, L670–674).

### Figure 3 (p.21; caption L911–913), digitized [fig]

Panel (a): specific **total** power, kWh/kg O2, including the chiller.

| OUR | STR 200 | STR 500 | STR 1000 | BCR 200 | BCR 500 | BCR 1000 |
|---|---|---|---|---|---|---|
| 10 | 1.97 | 1.87 | 1.80 | 1.52 | 1.44 | 1.43 |
| 50 | 2.09 | 1.97 | 1.89 | 1.88 | 1.65 | 1.55 |
| 100 | 2.17 | 2.02 | 1.94 | 2.15 | 1.83 | 1.67 |
| 129 | 2.19 | 2.05 | 1.96 | 2.28 | 1.91 | 1.73 |
| 150 | 2.21 | 2.06 | 1.97 | 2.35 | 1.96 | 1.76 |

Panel (b): cost per kg O2 (2014$) at OUR 10 / 50 / 100 / 150.

| Vessel | OUR 10 | OUR 50 | OUR 100 | OUR 150 |
|---|---|---|---|---|
| STR 200 | 0.89 | 0.33 | 0.25 | 0.22 |
| STR 500 | 0.69 | 0.26 | 0.20 | 0.19 |
| STR 1000 | 0.55 | 0.22 | 0.18 | 0.17 |
| BCR 200 | 0.72 | 0.26 | 0.21 | 0.20 |
| BCR 500 | 0.55 | 0.20 | 0.17 | 0.16 |
| BCR 1000 | 0.48 | 0.18 | 0.15 | 0.14 |

Panel (c): annual cost per m³ of reactor at OUR 150. Stirred tanks: about $8,280 / 7,045 / 6,190. Bubble columns: $7,635 / 6,015 / 5,240 (200 / 500 / 1,000 m³).

**Derived [calc]:**
- **Total power per volume.** At OUR 150 the 200 m³ stirred tank draws 2.21 × 4.8 kg O2/m³/h = 10.6 kW/m³ of liquid.
- **Chilling of the reaction heat** in their bookkeeping:
  - 110 kcal/mol = 460 kJ/mol O2 = 4.00 kWh of heat per kg O2.
  - At 0.263 kWe per kW of refrigeration (1.24 hp/ton), that costs 1.05 kWh of electricity per kg O2.
- **So the rest is roughly 1.16 kWh/kg O2** at OUR 150, i.e. 5.6 kW/m³, and 1.14 kWh/kg (4.7 kW/m³) at OUR 129. "The rest" means compressor + agitator + chilling of agitator heat + pump + air cooler.
- **I'm about 85% confident Fig. 3a includes this chilling.** The text calls it total system power and lists the chiller among the users. Also, all bubble-column curves converge at OUR 10 to about 1.43, which fits 1.05 of chilling plus a small compression term.

## 2. Comparison at 200 m³

| Quantity | Humbird 2017, stirred tank 200 m³ | Humbird 2021 SI "Cost of Aeration Figure" (Fig1.3), 200 m³ | **Ours, 200 m³** |
|---|---|---|---|
| Total incl. all chilling, kWh/kg O2, OUR 150 | 2.21 [fig] | 1.49 [SI row 197]; about 1.63 once a units slip in its refrigeration column is fixed¹ [calc] | **1.60** [run+calc]; 1.64 averaged over the base batch [run] |
| Compressor + agitator, kWh/kg O2, OUR 150 (with agitator heat chilled) | about 1.16 (includes pump and air cooler) [calc] | 0.50 (0.56) | **0.50 (0.55)** [run] |
| Same, kW/m³ liquid, OUR 150 / 129 | about 5.6 / 4.7 [calc] | 2.40 / 2.06 (at OUR 130) | **2.40 / 2.04** [run] |
| Compressor + agitator across OUR 10 / 50 / 100 / 129 / 150, kWh/kg O2 (with agitator heat chilled) | 0.92 / 1.04 / 1.12 / 1.14 / 1.16 [calc] | 0.43 / 0.47 / 0.49 / 0.50 / 0.50 (without) | 0.47 / 0.52 / 0.54 / 0.55 / 0.55 [run] |
| Air rate, OUR 150 | not reported | 0.41 vvm | **0.48 vvm** (0 °C basis; 0.53 at 30 °C, the figure BE-7 quotes) |
| Agitator P/V, OUR 150 | not reported | 1,148 W/m³ | **952 W/m³** |
| Compressor : agitator split | not reported | 52 : 48 | **60 : 40** |
| Stirred-tank kLa | 0.002, 0.7, 0.2, no temperature factor | same × 1.025^(T−20) (Fig1.3!C11:F11) | same as 2021 |
| Temperature / pressure | 32 °C; head + line losses | 30 °C; 1.33 bar + head | same as 2021 |
| Dissolved O2 | not controlled | 12.58% of air saturation at the top | same as 2021 |
| Compressor model | Aspen, efficiency not stated | 1.4-exponent formula, 80% | same as 2021 |
| Extra power users | pump, air cooler, agitator drive losses | none | none |

¹ Fig1.3 column AN (refrigeration) divides kmol/h of glucose and water by their molar masses as if they were kg/h. That gives 417 instead of 477.5 kJ of reaction heat per mol O2. Our model does not use that cell.

**Verdict.** We are within Humbird 2021 but **not within the 2017 stirred-tank range**:
- On totals we are 27% below their 200 m³ stirred tank and 19% below their 1,000 m³ one. We land inside their 500–1,000 m³ bubble-column band (1.73–1.96).
- The aeration part alone is about 2.1× lower than theirs.

**Why, in order of importance [run]:**
1. **Dissolved O2.** Reconstructing the 2017 setup with our equations: their 200 m³ geometry, 1 atm headspace, 32 °C, Eq. 2 without the temperature factor, and my assumed adiabatic compressor at 72% with 0.2 bar line loss.
   - At our 12.6% DO this gives only 0.51–0.63 kWh/kg O2.
   - At 50% DO it gives 0.94 / 1.03 / 1.07 / 1.10 / 1.13 / 1.15 / 1.16 at OUR 10 / 30 / 50 / 75 / 100 / 129 / 150. The paper implies 0.92 / 1.00 / 1.04 / 1.09 / 1.12 / 1.14 / 1.16.
   - The reconstructed OUR-150 point runs at 1.14 vvm, 2,447 W/m³ and a top gas velocity of 0.22 m/s.
   - My confidence that DO is the main driver is about 60%: the compressor settings are my assumptions, and pump and air-cooler loads are left out.
2. **kLa temperature factor.** Humbird 2021 added 1.025^(T−20); the 2017 Eq. 2 has none. It raises kLa by 28% at 30 °C. Removing it raises our aeration energy by 17%.
3. **Pump, air cooler and agitator drive losses.** The 2017 model counts these (p.7, p.10); we don't. They are small.
4. **Compressor formula.** This pushes the other way. Ours overstates compressor work about 1.6×; with the textbook formula at 80% efficiency our aeration energy would be 23% lower still (0.385 kWh/kg at OUR 150).
5. **Geometry, 1 atm headspace, 32 °C.** Small: 0.60 vs 0.58 kWh/kg O2.

## 3. BE-7's claim (2–3 kW/m³ and about 1 vvm at OUR 150 in a dense yeast broth)

- **The paper cannot test BE-7's mechanism.** It covers non-viscous liquids only (p.9) and reports no P/V or vvm.
- **Our broth is outside its regime.** Our own Krieger-Dougherty viscosity (Humbird A.1 constants) gives 3.0 cP at 107 g/L and 2.4 cP at the 94 g/L end of the batch [run]. Both are above the paper's 2 cP limit for bubble columns.
- **Numerically, the 2017 stirred-tank energy matches BE-7's operating point:**
  - Their implied figure at OUR 150 is about 5.6 kW/m³.
  - BE-7's point would draw 2–3 kW/m³ of agitation plus about 2.7 kW/m³ of compression at 1 vvm with our formula, so 4.7–5.7 kW/m³ in total [calc].
  - My reconstruction of the 2017 point lands at about 1.1 vvm and 2.4 kW/m³ of agitation.
- **But the paper gets there for a different reason.** On my reconstruction, it is a high, uncontrolled DO in a water-like liquid, which the authors say is not how production runs.
- **Net:** the paper supports BE-7's magnitude only as a pessimistic case, gives no support for the dense-broth reason, and does not contradict it.
- **BE-7 compared agitator power with a total.** Its "952 W/m³" is agitator only. Our total aeration draw at OUR 150 is 2.40 kW/m³, already inside BE-7's "2–3 kW/m³" if BE-7 meant total power.
- **BE-7's price table is out of date.** Its base minimum selling price was $29.37/kg; the current base is $20.72 [run].

## 4. Stirred tank vs bubble column for this duty

- **The paper's bubble-column advantage has conditions.** Bubble columns save 10–20% (p.3, p.14) only if the process suits one. They are capped at OUR 150 by jet flooding (p.12) and at 2 cP (p.9).
- **Our duty fails both conditions:**
  - Base-batch OUR peaks at 173 per m³ of broth during growth [run]; the cap 200 × (1 − X/300) equals 173 at X ≈ 40 g/L [calc].
  - Production runs at up to 129 per m³ of broth.
  - The broth is 2.4–3.0 cP.
  - So a **stirred tank is the correct choice**.
- **Even in the paper, the 200 m³ bubble column uses more power than the stirred tank at OUR 150:** 2.35 vs 2.21 kWh/kg O2, crossing over near OUR 103 [fig]. It keeps only a small cost edge from cheaper capital: $0.20 vs $0.22/kg O2 [fig].
- **The paper prefers 500 m³ stirred tanks** (p.15). Going 200 → 500 m³ cuts cost per kg O2 by about 15% (0.22 → 0.19) and power by about 7% at OUR 150 [fig]. This is relevant to `fermenter.volume_m3`: base 200 m³, high case 500 m³.

## 5. Recommendation

**Change: two errors.**
- **R1. Compressor formula** (`src/pftea/fermentation.py`, `compressor_kW`, L271–275).
  - The 8130 constant is the US-unit form of adiabatic compression work: hp = scfm × T1[°R] / (8130·a) × (r^a − 1), with a = (k−1)/k.
    - My check: 520 °R × 33,000 / 2,116 ≈ 8,110.
    - With a = 0.286 it matches the SI adiabatic work, 3.5·R·T·(r^0.286 − 1), to 0.3%.
  - A.1!BD287 and Fig1.3!AL27 put k = 1.4 where a should be. The result is:
    - 1.59× the adiabatic power at r = 2.12, i.e. an effective 50% efficiency instead of the stated 80%;
    - 2.1× at 1 barg back pressure;
    - 5.3× at r = 10.
  - I'm about 95% sure this is an error.
  - Fix: use a = 0.4/1.4 and r = (p_btm_max + Δp_line)/1.013. Put the efficiency (0.80 now, from A.1) and a line loss (guess, base 0) in `base.yaml` with sources.
  - Effect: compressor power −37%, aeration energy −23%, price −$0.02/kg [run].
  - It must be fixed before any head-pressure scenario, i.e. `physical_limit.yaml`, or BE-7's advice to cost the pressure.
- **R2. `aerate()` search** (`src/pftea/pf_ferm.py`, L153–160).
  - The loop that widens the air-rate range reads `state() is None` as "too much air". In fact None means too little air: the top driving force is negative.
  - At DO setpoints of 50% or more the function returns None and the physical OTR limit collapses to about 1, so a DO sensitivity silently makes the plant infeasible. A brute-force scan finds valid optima: 0.74 kWh/kg at 50% DO and OUR 129 [run].
  - Fix: keep widening while the state is None; stop only when the top gas velocity exceeds its limit. Add a test at DO 0.5. The base DO of 12.58% is unaffected.

**Parameters: no change to base values.**
- **kLa constants:** already identical to Eq. 2.
- **Temperature factor `kla_k` = 1.025:** keep it (Humbird 2021 Fig1.3!F11), but move it into `base.yaml` with a low value of 1.0 citing 2017 Eq. 2. That case costs +17% aeration energy and +$0.07/kg [run]. Note in the docstring that the factor is a 2021 addition.
- **DO 12.58%:** keep it. It matches the paper's own statement that practice holds DO near zero.
- **OTR cap:** no change from this paper. It states no stirred-tank limit, and the cap question (BE-7) needs other sources.

**Caveat for the report.**
- Humbird's 2017 Aspen model implies about 2× our aeration energy per kg O2, most plausibly because its DO was not controlled. Our model matches his 2021 redo to within 1%.
- The kLa correlation is for non-viscous liquids, and our broth is about 3 cP.
- Carry BE-7's dense-broth concern through the `kla_factor` scenario with its own sources, not through Humbird 2017.

**Minimum selling price (CCF basis) under each variant [run]:**

| Case | $/kg | Change |
|---|---|---|
| Base | 20.72 | — |
| `kla_k` = 1.0 | 20.79 | +0.07 |
| Textbook compressor, 80% | 20.70 | −0.02 |
| Both, with 72% compressor efficiency | 20.77 | +0.05 |
| DO 50% | 20.99 | +0.27 |
| DO 50% + `kla_k` = 1.0 | 21.09 | +0.37 |
| Compressor + agitator power ×2.3 (2017 level) | 21.03 | +0.31 |

## Files

- Scratch folder: `<scratch>/review/aer/`
  - `humbird2017_fig3_digitized.csv` — the digitized Fig. 3 values
  - `img-003.png` — the Fig. 3 image
  - `digitize.py`, `sens.py`, `scan.py`, `msp.py`, `msp2.py` — the scripts behind the numbers above
- Humbird 2021 SI cells: A.1!BD287, Fig1.3!C11:F11, Fig1.3!AL27, Fig1.3 row 197, in `<repo>/references/papers/Humbird2021_cultured_meat_SI.xlsm`
- Model code: `<repo>/src/pftea/fermentation.py` and `<repo>/src/pftea/pf_ferm.py`
- No repository files were edited. Running Python may have refreshed `__pycache__` in `src/pftea`.
