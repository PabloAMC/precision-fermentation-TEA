# A physicist's primer on precision-fermentation economics

Phase A reading, about 75 minutes. Written for someone who knows transport physics and
thermodynamics but not bioprocess engineering. It explains how a precision-fermentation (PF)
plant works, which physical quantities set its cost, and how a techno-economic analysis
(TEA) turns those quantities into dollars per kilogram.

**Conventions.** g/L = kg/m³; mmol/L/h = mol/m³/h; t = metric tonne; kt/yr = thousand
tonnes per year. Every computed number here is reproduced by
[`docs/primer_numbers.py`](primer_numbers.py) (section numbers in brackets, e.g. [§2]).
Numbers are either quoted from a source on disk (key from
[`references/INDEX.md`](../references/INDEX.md)) or flagged. *Illustrative* marks a
typical value chosen only to teach. *(textbook)* marks a standard reference value quoted
from memory. Where the model needs such a value, Phase B sourced it separately in
`data/evidence/` (for example the heat per mol of O₂, §3.3). Neither kind is ever a model
input.

The running example is NREL's on-site cellulase plant (`humbird2011`, §3.4, printed pp.
36–43). It is the best-documented public design of a plant that secretes a protein from a
fungus, and every number in it can be checked. Exercise A1 then applies the same ideas to
Intelligen's ovalbumin plant, so this primer deliberately leaves that one alone.

---

## 1. What is being made

**Precision fermentation** means an engineered microbe that secretes one defined protein
into its growth liquid (the *broth*). The product is the protein, not the cells. That
distinguishes it from *biomass fermentation* (the cells are the food: mycoprotein,
single-cell protein) and from cultivated meat (animal cells, much slower and more fragile;
see Humbird 2021).

Our two products:

| | β-lactoglobulin (BLG) | Ovalbumin (OVA) |
|---|---|---|
| Natural source | Main whey protein: 2–3 g/L in cow's milk, 7–9% of milk protein (`FDA-GRN1056`) | Main egg-white protein: 54% of egg-white protein; egg white is ~11% protein (`intelligen_ovalbumin2025`, p.1) |
| Size | 162 residues, ~18.4 kDa (`FDA-GRN1056`) | 386 residues, ~45 kDa, glycosylated at Asn292 (`intelligen_ovalbumin2025`, pp.3–4) |
| Incumbent it replaces | Whey protein concentrate (WPC80, 80% protein) and isolate (WPI, ≥90%) | Dried egg white |
| Companies (public filings) | Remilk (*K. phaffii*, GRN 1056), Perfect Day (*T. reesei*, GRN 863), Vivici | EVERY (*K. phaffii*), Onego Bio (*T. reesei*) |

**Hosts.** *Komagataella phaffii* (formerly *Pichia pastoris*) is a yeast that is
*Crabtree-negative*: given excess sugar it keeps respiring instead of switching to
ethanol, which lets it reach very high cell densities. Its classic promoter (AOX1) is
switched on by methanol, but glucose-driven promoters exist. *Trichoderma reesei* is the
filamentous fungus behind industrial cellulase. It secretes its own enzymes at very high
titers (on the order of 100 g/L is often quoted; to verify, `cherry2003` in the fetch
list). Its mycelium makes the broth viscous, which matters for oxygen transfer (§5).

**What a real product looks like.** Remilk's FDA filing specifies ≥70 wt% protein, with
≥80% of that protein being BLG, and ≤7% moisture. The process is: separate the cells,
filter, ultrafilter and diafilter, then dry. There is no chromatography and no
precipitation (`FDA-GRN1056`, §2.2–2.3). So the realistic commercial product is a
*concentrate*, not a 99% isolate, and that choice decides the downstream train (§6).

## 2. The plant in one picture

```
sugar + NH₃ + salts + air
 └► media prep + sterilisation ► seed train ► production fermenters ► remove cells
                                  1:10 steps     100–300 m³, aerobic      centrifuge or
                                                 fed-batch, 4–7 days      filter press
    ► ultrafilter (concentrate, wash) ► [purify: precipitate or chromatograph] ► spray-dry ► powder
                                                                                   
 side streams: spent cells (feed/fertiliser or waste) · wastewater · heat and CO₂ from the fermenters
 utilities:    compressed air · chilled + cooling water · steam (sterilisation) · clean-in-place chemicals
```

- **Seed train.** A vial of cells is grown through a series of vessels, each about 10×
  larger, to inoculate the production fermenter. NREL uses 0.3, 3 and 30 m³ ahead of 300 m³.
- **Production fermenter.** A stainless steel tank, stirred and sparged with air, cooled,
  and kept sterile for days. This is where most of the capital and energy go.
- **Downstream processing (DSP).** Everything after the fermenter. It turns a dilute broth
  (a few % protein plus cells, salts and sugars) into a dry powder.

The running example in numbers (`humbird2011`, printed pp. 37–41):

| Quantity | NREL on-site cellulase |
|---|---|
| Production fermenters | 9 × 300 m³, height/diameter = 2, 80% full at the end |
| Cycle | 24 h growth + 96 h production + 48 h drain/clean/refill = 168 h |
| Titer at harvest | 50 g/L |
| Yield on glucose | 0.24 kg protein / kg glucose |
| Volumetric productivity | 0.30 g/L/h [§4] |
| Output | 490 kg/h of protein to hydrolysis (≈4.1 kt/yr at 8,410 h/yr), plus 10% for media prep. The $4.24/kg below rests on ~580 kg/h (≈4.9 kt/yr) [§4b] |
| Electricity | 5.3 MW in the area; NREL states 9 kWh per kg protein (Table 21; basis not stated, but 5,340 kW ÷ 9 ≈ 590 kg/h, close to the ~580 kg/h behind $4.24/kg) [§4b] |
| Cost | $4.24/kg protein (2007$): glucose 57%, capital 21%, electricity 13%, other nutrients 5%, fixed 4% |
| Not included | Any downstream processing, formulation, transport, licensing |

Keep the last row in mind. A crude enzyme used on site is not a food ingredient. The
distance from $4/kg to the ~$41/kg of a purified, dried food protein (per kg of protein;
$39/kg of powder, gross, before a by-product credit) is Part 3 of exercise A1.

## 3. Biology as chemistry

### 3.1 The black box

For costing purposes, a cell is a catalyst that turns glucose, ammonia and oxygen into
more cells, product, CO₂ and water, releasing heat. Engineers write every species per
**C-mole** (per carbon atom), because carbon is conserved and elemental formulas become
comparable:

| Species | C-mol formula | Mass per C-mol | Degree of reduction γ |
|---|---|---|---|
| Glucose | CH₂O | 30.0 g | 4.00 |
| Cellulase protein (NREL) | CH₁.₅₉N₀.₂₄O₀.₄₂S₀.₀₁ | 24.0 g | 4.03 |
| *T. reesei* cells (NREL) | CH₁.₆₄₅O₀.₄₄₅N₀.₂₀₅S₀.₀₀₅ | 23.8 g | 4.14 |
| Generic cells (textbook) | CH₁.₈O₀.₅N₀.₂ | 24.6 g | 4.20 |

[§1] (The formulas are from `humbird2011`, p.38; sulfur is ignored in γ because it moves
it by <2%.)

### 3.2 Two conservation laws do most of the work

**Carbon.** Every carbon atom of glucose ends up in cells, product or CO₂.

**Electrons.** The *degree of reduction* γ counts the electrons per C-mole available for
transfer to oxygen, taking CO₂, H₂O and NH₃ as the zero reference: C = +4, H = +1,
O = −2, N = −3. Glucose has γ = 4. Proteins and cells are slightly more reduced. Every O₂
molecule accepts 4 electrons. Per C-mole of glucose consumed:

$$\gamma_S \;=\; Y_{X}\,\gamma_X \;+\; Y_{P}\,\gamma_P \;+\; 4\,n_{O_2}$$

where $Y_X$ and $Y_P$ are the C-moles of cells and product formed and $n_{O_2}$ is the moles
of O₂ consumed. It is a redox (electron) balance, a linear combination of the C, H, O and
N element balances, so strictly it is mass conservation. Electrons not stored in cells or
product were passed to oxygen to power the cell. Thornton's rule (§3.3) turns this into an
energy balance too.

**Worked example (NREL).** NREL states that glucose carbon ends up 31% in protein, 4% in
cells and 65% in CO₂ [§2]:

- Carbon balance: 0.31 + 0.04 + 0.65 = 1.00.
- Yield: 0.31 × 24.0 / 30.0 = **0.248 g protein/g glucose**. NREL quotes 0.24.
- Oxygen from the electron balance: $n_{O_2}$ = (4 − 0.31×4.03 − 0.04×4.14)/4 = 0.646 mol
  per C-mol glucose, i.e. **87 mol O₂ per kg protein** (2.8 kg O₂/kg).
- NREL's own design uses 8.4 kmol O₂/h for a reactor making 100 kg protein per online
  hour: **84 mol/kg**. The balance and the design differ by 3.3%.
- Respiratory quotient (CO₂ out / O₂ in) = 0.65/0.646 = 1.01, as expected on glucose.

The lesson: **once you know the yield and the formulas, you know the oxygen demand**. The
oxygen demand then sets the air compressor, the agitators and the chillers (§5). The
stoichiometry is the backbone of the whole model.

### 3.3 Heat

Respiration releases about **0.46 MJ per mol of O₂** consumed, nearly independent of
organism or substrate. This is Thornton's rule: burning organic matter releases roughly
110–115 kJ per mole of electrons passed to oxygen, and each O₂ takes four.
The 460 kJ/mol figure is now sourced (grade A in `data/evidence/engineering.yaml`): it is
Roels' (1983) value, as quoted by Almeida Benalcázar et al. (2025). Calorimetry averages
455 ± 15 kJ/mol (Maskow et al. 2010). Cooney et al. (1969), as generalised by Shuler and
Kargi, give ~0.50 MJ/mol.

For NREL [§3]: 84 mol O₂/kg × 0.46 MJ/mol = **39 MJ of heat per kg protein** (10.7 kWh
thermal). One 300 m³ reactor at full rate releases **1.07 MW**. All of it must be removed
at 28–30 °C, which is barely above cooling-tower water temperature. That is why
fermentation plants buy refrigeration (chillers) and why cooling shows up as a major
utility bill.

### 3.4 Why real yields are far below the ceiling

A cell spends sugar on three things: building more cells (growth), staying alive
(maintenance) and making product. A standard way to write this is the Pirt equation for
the specific sugar uptake rate:

$$q_S \;=\; \frac{\mu}{Y_{XS}^{\max}} \;+\; m_S \;+\; \frac{q_P}{Y_{PS}^{\max}}$$

with growth rate μ (1/h), maintenance coefficient $m_S$ (g sugar per g cells per h) and
specific productivity $q_P$ (g product per g cells per h). In fed-batch operation (§4) you
choose μ through the feed rate. That is a trade-off. Fast growth makes more cells and so
costs yield. Slow growth over a long batch lets maintenance eat the sugar.

**Ceilings** [§2, §2b]:
- If every electron of glucose ended up in NREL's cellulase, the yield would be
  **0.79 g/g**. For BLG it is 0.70 and for OVA 0.72. This is impossible, because making
  protein costs energy.
- Charging only the energy of joining amino acids brings the cellulase value to
  **~0.6 g/g**. This assumes ~4.3 ATP per peptide bond, supplied by burning more glucose, a
  mean residue of 110 g/mol and a P/O ratio of 1.0–1.5 (all textbook). This is a rough
  estimate; the real ceiling is lower once amino-acid synthesis is costed.
- The model (`energetic_ceiling` in `src/pftea/product.py`) charges 4 ATP per peptide
  bond. It takes ATP per glucose from the *K. phaffii* P/O ratio of 1.48 (Chung et al.
  2010): 4 + 12 × 1.48 = 21.8 (4 ATP from glycolysis and the TCA cycle, plus 1.48 for each
  of the 12 O atoms that take glucose's 24 electrons). That gives about **0.58 g/g for BLG
  and 0.59 for OVA**. The energy of amino-acid synthesis beyond carbon and electrons is not
  counted, so this is an upper bound.

**Reality.** NREL assumes 0.24 g/g overall. GFI's private-sector survey reports
0.03–0.17 g/g (`gfi2025costs`, Table 2). Most of the gap between ~0.1 and ~0.6 is sugar
spent growing and maintaining the catalyst. Exercise A1 shows how large that share is in
a real design.

### 3.5 The sugar floor

Whatever else happens, each kilogram of product costs at least sugar price ÷ (yield ×
downstream recovery). In $/kg protein, at 85% recovery [§12]:

| Yield (g/g) | glucose $0.25/kg | $0.36/kg | $0.40/kg | $0.57/kg |
|---|---|---|---|---|
| 0.08 | 3.68 | 5.29 | 5.88 | 8.36 |
| 0.15 | 1.96 | 2.82 | 3.14 | 4.46 |
| 0.24 | 1.23 | 1.76 | 1.96 | 2.79 |
| 0.40 | 0.74 | 1.06 | 1.18 | 1.67 |

Glucose prices:
- $0.25/kg: a contract price (`humbird2021`, p.40).
- $0.36/kg: "glucose syrup" of unstated concentration (`intelligen_ovalbumin2025`,
  Table 3).
- $0.40/kg: DE95 glucose in GFI's single-cell-protein model (`gfi2025costs`, Table 6).
- $0.57/kg: NREL's price in 2007 dollars (`humbird2011`, Table 29).

With whey protein at $10–20/kg protein, sugar alone is survivable. It becomes the binding
constraint only once capital and downstream costs have been squeezed. NREL's crude enzyme
has no downstream processing and large, cheap vessels, so sugar is already 57% of its cost.
That is $0.57/kg glucose ÷ 0.24 = $2.37/kg protein, against the $2.42 in its Figure 10
[§12].

## 4. Fed-batch operation and the TRY triangle

**Why fed-batch.** If you dump all the sugar in at the start, the cells grow as fast as
they can. Oxygen demand then outruns what the tank can supply. Many yeasts overflow to
by-products such as ethanol or acetate, and high sugar inhibits growth. So you start with
a modest batch and then *feed* concentrated sugar. The feed rate sets the growth rate μ,
which sets the O₂ demand and the heat release. **The feed pump is the throttle on the
whole thermodynamics of the vessel.** A typical recipe is: batch growth, then fed-batch
growth to high cell density, then a production (induction) phase, then harvest. The
turnaround (drain, clean-in-place, sterilise, refill) takes roughly 12–48 h (textbook);
NREL takes 48 h.

**TRY: titer, rate, yield.** These are the three strain-and-process numbers that dominate
cost:

| Number | Definition | What it sizes | Cost it drives |
|---|---|---|---|
| **Titer** T | g product per L of broth at harvest | Broth volume per kg = 1/T | Volume-driven DSP (clarification, UF area, water, waste) |
| **Rate** r | T / (batch time + turnaround), g/L/h | Fermenter volume per (kg/h) = 1/r | Fermentation capital, labour, agitation energy |
| **Yield** Y | g product per g sugar | Sugar and O₂ per kg | Sugar bill, aeration and cooling energy |

For NREL: r = 12,000 kg / (240 m³ × 168 h) = 0.30 g/L/h [§4].

**They are coupled.** Pushing titer usually means longer batches, so rate need not
improve. Growing more cells raises rate but lowers yield. A company quoting "30 g/L"
without a batch time or a yield has told you one third of what you need.

## 5. Transport physics: oxygen and heat

This is where Humbird's cultivated-meat analysis found its hard limits, and it is where
ours will too.

### 5.1 Oxygen barely dissolves

Air-saturated fresh water at 30 °C holds about **7.6 mg/L = 0.24 mmol/L** of O₂, and
dissolved salts lower this by roughly 10–20% (textbook) [§5]. NREL's peak O₂ uptake rate
(OUR) is 56 mmol/L/h [§4]. At that rate a saturated broth would run out of dissolved O₂
in about **15 seconds**, and one held at NREL's setpoint of 30% saturation in about 4
seconds. Oxygen must therefore be transferred continuously from bubbles:

$$\text{OTR} \;=\; k_La\,\left(C^* - C_L\right)$$

where OTR is the oxygen transfer rate, $k_La$ the volumetric mass-transfer coefficient
(1/h), $C^*$ the saturation concentration (set by Henry's law and the local O₂ partial
pressure) and $C_L$ the dissolved concentration you keep, typically 20–30% of saturation
(textbook). Two things vary up a tall tank. The hydrostatic head raises $C^*$ at the
bottom, and the rising bubbles lose O₂, which lowers $C^*$ at the top. Designers use a
log-mean driving force between bottom and top; it is really built for the second effect.
Raising the head pressure is a real lever, because C* scales with pressure.

**NREL numbers** [§5]: at 50% fill the liquid is 5.8 m deep, so the bottom sits at
1.56 atm. With C* = 0.21 mmol/L at the top and C_L = 0.063 mmol/L, the log-mean driving
force is 0.20 mmol/L. Supplying 56 mmol/L/h then needs **kLa ≈ 280 1/h**. NREL's
method counts pressure only. Its air carries 3–5× the O₂ consumed, so the exit gas is
15–16% O₂. Counting that depletion raises the kLa needed to **≈330–360 1/h**.

A units trap worth noticing: NREL's text gives Henry's coefficient for O₂ as "1.3
atm/(mmol/L)". That is the solubility, 1.3 mmol/(L·atm), with its units inverted. Their
design value of 1 atm/(mmol/L) is a reasonable broth figure, so the design is fine, but
even gold-standard reports need unit checks.

### 5.2 How a stirred tank delivers kLa, and at what price

kLa rises with power input per volume P/V and superficial gas velocity $u_s$ (gas flow
divided by the tank cross-section). The classic van 't Riet (1979) correlations (SI units;
*illustrative*):

$$k_La = 0.026\,(P/V)^{0.4}\,u_s^{0.5}\ \ \text{(coalescing, water-like)}\qquad k_La = 0.002\,(P/V)^{0.7}\,u_s^{0.2}\ \ \text{(non-coalescing, salty)}$$

Take NREL's maximum agitation (600 kW, which we assume coincides with 50% fill, so
4 kW/m³) and 3.3 cm/s of gas. The correlations give **470–1,210 1/h** [§6], above the
330–360 needed, which is **94–242 mmol/L/h** of transfer capacity at NREL's driving force.

Treat that as an order of magnitude only:
- Van 't Riet fitted his correlations on vessels of a few m³, so using them at 150 m³ is an
  extrapolation. NREL makes the same caveat about its own correlation.
- Viscous fungal broths do worse than either correlation, which is why NREL used a
  fungal-specific one.

Production-scale OTR ceilings of order 100–250 mmol/L/h are the working range here
(illustrative). The model's sourced cap is 150 mmol/L/h (range 100–200, grade B;
`fermenter.otr_cap_mol_m3_h` in `data/pf/base.yaml`). Humbird (2021) puts about 200 as the
practical maximum in fermentation.

Oxygen costs electricity twice:
- **Compressing air.** Isentropic work is
  $W = \frac{\kappa}{\kappa-1}\,p_1 Q\left[(p_2/p_1)^{(\kappa-1)/\kappa}-1\right]$,
  where κ = 1.4 is the heat-capacity ratio of air and p₁, p₂ the inlet and outlet
  pressures. NREL's 7.5 Nm³/s of air compressed to 3 atm gives 0.98 MW isentropic.
  At an illustrative 70% efficiency that is 1.40 MW. With a 20 °C inlet and the seed
  reactors' extra 10% of air it is 1.65 MW [§7]. NREL reports 1.41 MW, which implies a
  compressor efficiency of about 0.76–0.82. The physics accounts for the number, but not to
  the percent.
- **Agitation.** NREL's agitators draw 2.3 MW.

Add refrigeration and you get NREL's 9 kWh per kg protein.

### 5.3 Heat removal, and why big tanks run out of it

Cooling capacity is $Q = U A \Delta T$, where U is the overall heat-transfer coefficient
and ΔT the temperature difference between broth and coolant. For geometrically similar
vessels the wall area grows like $V^{2/3}$, so **cooling per unit volume falls like
$V^{-1/3}$**. The table assumes a cooling jacket on the wetted wall only (*illustrative*:
U = 500 W/m²/K, chilled water 15 K colder than the broth, height/diameter 2, 80% full)
[§9]. Agitator power ends up as heat too; NREL's peaks at 4 kW/m³:

| Vessel (m³) | 1 | 10 | 50 | 100 | 136 | 300 | 1000 |
|---|---|---|---|---|---|---|---|
| Jacket cooling (kW per m³ broth) | 34.9 | 16.2 | 9.5 | 7.5 | 6.8 | 5.2 | 3.5 |
| Max OUR, metabolic heat only (mmol/L/h) | 273 | 127 | 74 | 59 | 53 | 41 | 27 |
| Max OUR with 2 kW/m³ of agitation heat | 257 | 111 | 58 | 43 | 37 | 25 | 12 |

A process that runs happily in a 1 m³ pilot can be cooling-limited at 300 m³. NREL's
design therefore puts chilled-water coils inside the vessel. Fermentation at ~30 °C with
cooling-tower water at 25–30 °C leaves almost no ΔT, hence chillers. NREL's chiller draw
(1.59 MW) against ~9.2 MW of heat implies a coefficient of performance of about 5.8 [§8].
NREL itself states 0.56 kW of electricity per ton of refrigeration (`humbird2011`, p.55),
a COP of 6.3, at which 1.59 MW removes about 10 MW [§8]. Our 9.2 MW is a rough estimate
that ignores the seed reactors.

### 5.4 The productivity ceiling in one line

At steady state the O₂ supplied equals the O₂ consumed. So the maximum rate at which a
vessel can make product is

$$r_{\max} \;\approx\; \frac{\text{OTR}_{\max}}{\text{mol O}_2\text{ per kg product}}$$

With NREL's 84 mol O₂/kg and an illustrative OTR ceiling of 150 mmol/L/h, production is
capped near **1.8 g/L/h** [§4], and heat removal may bind first. Compare like with like:
NREL's *peak* production rate is 56/84 = 0.67 g/L/h. Its 0.30 g/L/h is the average over a
cycle that includes 48 h offline. This is
how the model will test claims. "X g/L in Y hours" implies X/Y g/L/h. Combine that with
the O₂ per kg from the stoichiometry, then compare with what a vessel of that size can
transfer and cool. Humbird did exactly this for animal cells.

### 5.5 Other limits, briefly

- **CO₂.** It accumulates in tall tanks and inhibits cells.
- **Viscosity.** Fungal mycelium and very dense yeast broths both reduce kLa and mixing.
- **Gradients.** Mixing times in large tanks are tens of seconds, so cells cycle through
  sugar-rich and oxygen-poor zones.
- **Foam.** It needs antifoam, which can interfere with downstream steps.
- **Vessel size.** Industrial aerobic fermenters run at 200–1,000 m³, and Humbird puts the
  largest practical stirred tank at ~1,000 m³ (Humbird 2021; `data/evidence/engineering.yaml`).
  The model's base vessel is 200 m³ (range 100–500).
- **Shear.** Unlike for animal cells, this is rarely binding for microbes.

## 6. Downstream processing

The broth leaves the fermenter as a few percent protein, a lot of cells, salts, leftover
sugar, host-cell proteins and DNA. DSP makes it a food ingredient. The units and their
governing physics:

| Unit | Physics | Sizing variable | Notes |
|---|---|---|---|
| Disk-stack centrifuge | Stokes settling under gravity, $v_g = d^2\Delta\rho\,g/(18\mu)$; the bowl's speed and geometry (ω²r) are lumped into Σ | Throughput Q ≈ $v_g$ Σ, with Σ the equivalent settling area | Yeast; fungi go to filter presses or rotary vacuum filters |
| Microfiltration (MF) | Sieving of cells and debris | Membrane area = volume / (flux × time) | Polishes the clarified broth |
| Ultrafiltration (UF) | Membrane retains protein, passes water and salts | Area from flux (Intelligen assumes 30 L/m²/h) | Concentrates the product (Intelligen: 5× to 50 g/L) |
| Diafiltration (DF) | Wash with water at constant volume | Diavolumes N; a freely passing solute falls as $e^{-N}$ | Removes salts and sugars |
| Precipitation | Salting-out or isoelectric pH | Reagent per kg; residence time | Cheap purification; the salt must be washed out |
| Chromatography | Selective binding to resin | Resin capacity (50–100 g protein per L resin, `Every2024-purif`) | Buys purity at the price of resin and cycles |
| Spray dryer | Evaporation | Water evaporated per hour | ≥2.3 MJ per kg water (latent heat) plus losses, so concentrate first |

**Recovery compounds.** Overall recovery is the product of step recoveries: five steps
at 95% each give 77% [§11b]. Every kilogram lost downstream carries its full upstream cost, so
recovery divides everything in the cost equation (§8).

**The specification chooses the train.** A concentrate (Remilk: remove cells, filter,
UF/DF, dry) skips the purification box entirely. An isolate adds precipitation or
chromatography. Food grade is not pharma grade: there is no viral clearance, no clean
rooms in the pharma sense, and yeast and fungi carry none of the endotoxin problem of
*E. coli*. Specifications do still limit host-cell protein, DNA, heavy metals and microbes.

## 7. The accounting

### 7.1 What a TEA number is worth

At the conceptual stage, estimates are AACE Class 5 or 4 (AACE 18R-97; quoted from
memory). Class 5 runs −20 to −50% on the low side and +30 to +100% on the high side;
Class 4 runs −15 to −30% and +20 to +50%. NREL claims ±25% for its capital estimate
(`humbird2011`, p.68). Relative statements ("titer X is worth $Y/kg") are far more robust
than absolute ones. That is one reason we report cost as a function of performance rather
than as one number.

### 7.2 Capital

The chain runs from purchased equipment cost (PEC), to installed cost, to total direct
cost (TDC), then adds indirect costs to reach fixed capital investment (FCI), and finally
adds working capital to reach total capital investment (TCI).

- **Lang factor.** TCI (or FCI) as a multiple of PEC. Petrides' classes as tabulated by
  Humbird (`humbird2021`, Table 3.1): 4.7 for an outdoor lysine plant, 6.1 for sanitary
  (beer), 7.1 for aseptic (lactase), 8.8 for cGMP microbial (insulin) and 10.9 for cGMP
  cell culture (antibodies). Food-grade PF sits between the first three.
  - Intelligen uses 4 (`intelligen_ovalbumin2025`, p.16).
  - Humbird also warns about **double-dipping**: applying installation factors to an
    already piped-and-instrumented skid price counts installation twice.
- **NREL's itemised version** (`humbird2011`, Table 27, printed p.61). Per-equipment
  installation factors give the inside-battery-limits (ISBL) cost. Then add:
  - warehouse 4% of ISBL;
  - site development 9% of ISBL;
  - additional piping 4.5% of ISBL;
  - prorateable costs, field expenses, contingency and other costs at 10% of TDC each;
  - home office and construction at 20% of TDC.

  For the ethanol plant (feedstock handling and wastewater excluded) this comes to a Lang
  factor of 3.1 (FCI over purchased equipment; Table 28, printed p.62). Definitions differ:
  Humbird's factors are TCI/PEC, NREL's is FCI/PEC and Intelligen's is DFC/PEC.
- **Scaling.** Cost ∝ capacity^n with n ≈ 0.6 (the "six-tenths rule"). Doubling capacity
  multiplies cost by 1.52, so cost per unit capacity falls 24%. A 10× increase cuts unit
  capital cost to 0.40× [§11]. This only holds while you can build bigger. Past the
  largest practical fermenter you **number up**, and the fermentation section's exponent
  tends to 1.
- **Cost indices.** The Chemical Engineering Plant Cost Index (CEPCI) moves costs between
  years. All our results will be in 2025 dollars.

### 7.3 Operating costs

- **Variable costs** scale with output: raw materials, utilities, consumables such as
  membranes and resin, and waste treatment.
- **Fixed costs** do not:
  - Labour. Humbird's model counts operator attention per batch; $50k/yr per operator,
    supervisors at 1.4×, a 100% burden, and 4.5 hires per around-the-clock position
    (`humbird2021` §3.3).
  - Maintenance. Humbird uses 4% of TCI per year.
  - Insurance and taxes. Humbird uses 5% of TCI per year.
  - Plant overheads.

### 7.4 From capital to $/kg

A plant costs its TCI once but must recover it every year. Two conventions:

- **Depreciation** (accounting): fixed capital spread over the plant's life, with no
  return. Working capital and land are not depreciated. This
  gives a **cost of production (COP)**. SuperPro Designer's "unit production cost"
  (Intelligen) is of this kind, plus some overheads.
- **Capital charge** (economics): the annuity that repays TCI *with* a return i over n
  years, $\text{CCF} = i/[1-(1+i)^{-n}]$. This gives a **minimum selling price (MSP)** [§10]:

| Return i | Life n | CCF (fraction of TCI per year) |
|---|---|---|
| 7.5% | 10 y | 0.146 (Humbird 2021) |
| 10% | 10 y | 0.163 |
| 10% | 20 y | 0.117 |
| 10% | 30 y | 0.106 |

NREL goes one step further with a full **discounted cash flow** analysis. It finds the
selling price at which net present value is zero at a 10% internal rate of return. Its
assumptions (`humbird2011`, Table 33): 30-year life, 35% tax, 40% equity with an 8% loan
over 10 years, 7-year accelerated depreciation, 3-year construction, and working capital
of 5% of FCI.

**Why this matters.** Two TEAs of the *same* plant can differ by up to ~2× through
accounting and costing choices alone, with the same biology:
- how capital is annualised moves Intelligen's cost by 12% (exercise A1, step 1.4);
- how capital is estimated as well moves our base case by 1.3×: $21.2/kg BLG with
  Humbird's price-anchored convention, $16.4 with the lighter design-report one (report,
  key-numbers table);
- published designs come out 1.8× below our model run on the same process (report,
  calibration table: NREL, Voutilainen).

Before comparing any two published numbers, put them on one convention. We report both
COP and MSP.

### 7.5 Nth-of-a-kind

TEAs usually cost the *nth* plant, built with mature designs and no learning pains. First
plants overrun cost and underrun performance. We model the nth plant and show a
first-of-a-kind penalty separately, never mixed in.

## 8. A one-screen cost model

Let P be annual output (kg protein/yr), R downstream recovery, T titer (kg/m³), r
productivity (kg/m³/h including turnaround), H operating hours per year, Y yield (kg/kg
sugar) and $p_s$ the sugar price. Then, per kg of product:

$$c \;\approx\; \underbrace{\frac{p_s}{Y R}}_{\text{sugar}} \;+\; \underbrace{\frac{\text{CCF}\cdot F\cdot c_V}{R\,r\,H}}_{\text{fermentation capital}} \;+\; \underbrace{\frac{e_{O_2}\,o(Y)}{R}}_{\text{O}_2\text{ and cooling}} \;+\; \underbrace{\frac{a}{R\,T} + b}_{\text{DSP}} \;+\; \underbrace{\frac{L}{P}}_{\text{fixed}}$$

where:
- CCF should here also cover the fixed costs proportional to capital (maintenance,
  insurance); Humbird adds 9% of TCI per year to his 14.6% capital charge;
- F is the installation (Lang-type) factor;
- $c_V$ is the purchased cost per m³ of working volume;
- $o(Y)$ is the mol O₂ per kg of product, which rises as yield falls because the extra
  sugar is burned;
- $e_{O_2}$ is the energy cost per mol O₂ transferred and removed as heat;
- a is the part of DSP that scales with broth volume, b the part that scales with product
  mass;
- L is the fixed cost (labour, overheads), with some scale economy.

| Improve… | Terms that shrink | Terms that don't move |
|---|---|---|
| Titer T | Volume-driven DSP (and fermentation capital, *if* rate rises with it) | Sugar, O₂ per kg, mass-driven DSP |
| Rate r | Fermentation capital, labour per kg | Sugar, O₂ per kg, DSP |
| Yield Y | Sugar, and O₂/cooling energy | Capital, DSP |
| Recovery R | Everything upstream | Mass-driven DSP after the loss |
| Scale P | Capital per kg (up to the largest vessel), fixed costs per kg | Sugar, O₂, consumables per kg |

NREL's $4.24/kg maps onto this directly. Glucose is 57% (the sugar term), capital 21%,
electricity 13% (O₂ and cooling), and other nutrients plus fixed costs 9%. There is no DSP
term because NREL has no DSP. Three habits follow:
1. The sugar term is a floor that neither titer nor scale can move.
2. Capital responds to *rate* (fermentation) and *titer* (volume-driven DSP), not to
   titer alone.
3. Yield enters twice, through sugar and through oxygen.

## 9. Physical limits: what the floor will be made of

Humbird's key move was to show that some aspirational inputs are physically impossible,
and to report the cost *at* the limits. Ours will be assembled from:
- the yield ceiling (§3.4; the model derives it per product in `src/pftea/product.py`);
- the O₂-transfer and cooling ceilings as functions of vessel size (§5);
- the largest practical vessel;
- the minimal DSP that meets the specification (§6);
- contract sugar (~$0.25/kg, `humbird2021` p.40);
- a scale large enough that fixed costs stop mattering.

His summary phrase applies to us too: some conditions will be **necessary but
insufficient**.

## 10. What the literature knows, and does not

See [`docs/LITERATURE.md`](LITERATURE.md). In brief:
- The best academic titers, now read in full text, are 5–14 g/L for BLG (*K. phaffii*,
  5 L bioreactors; Li 2026, Yao 2026) and 2 g/L for OVA (*T. reesei*, Aro 2023; two bands
  combined, one of them a clipped form).
- Companies claim 30 to 120 g/L. The EVERY patent reports 30 g/L for ovomucoid; Onego's
  claim is in the press.
- No measured BLG/OVA yield on sugar exists. The public values are design or derived
  numbers: BLG 0.223 g/g (Behm 2022, a *T. reesei* design), OVA 0.28 g/g (Intelligen, a
  design, expression phase only) and OVA 0.39 g/g (Järviö 2021, derived from an LCA
  inventory; being re-checked).
- No per-step food-grade DSP recovery has been published.
- No peer-reviewed TEA of BLG or OVA exists.

That is why the model is built from physics outward rather than fitted to data.

## 11. Glossary

| Term | Meaning |
|---|---|
| AOX1 | Methanol-inducible promoter of *K. phaffii* |
| C-mole | Amount of a substance containing one mole of carbon atoms |
| CCF | Capital charge factor: annual charge per $ of capital |
| CEPCI | Chemical Engineering Plant Cost Index, for moving costs between years |
| CIP / SIP | Clean-in-place / sterilise-in-place |
| COP / MSP | Cost of production (no return on capital) / minimum selling price (with return) |
| DCW | Dry cell weight (g/L of dry cells) |
| DF | Diafiltration: washing a retained protein with water through a membrane |
| DFC / FCI / TCI | Direct fixed capital (Intelligen's term) / fixed capital investment / total capital investment |
| DSP / USP | Downstream / upstream processing |
| Fed-batch | Culture fed with substrate during the run, harvested at the end |
| GRAS | "Generally recognised as safe": the US FDA route for new food ingredients |
| HCP | Host-cell proteins, the microbe's own proteins, an impurity |
| ISBL | Inside battery limits: the process units proper, excluding site infrastructure |
| kLa | Volumetric O₂ mass-transfer coefficient (1/h) |
| Lang factor | Ratio of plant capital to purchased equipment cost |
| MF / UF | Microfiltration (retains cells) / ultrafiltration (retains proteins) |
| OUR / OTR | O₂ uptake rate by cells / O₂ transfer rate from gas (mmol/L/h) |
| PEC | Purchased equipment cost |
| Titer | Product concentration in the broth at harvest (g/L) |
| TRY | Titer, rate, yield |
| vvm | Gas volumes per liquid volume per minute |
| WPC80 / WPI | Whey protein concentrate (80% protein) / isolate (≥90%) |
| γ | Degree of reduction: electrons per C-mole relative to CO₂, H₂O, NH₃ |

## 12. Self-check

Answer without looking back. Answers are below.

1. Which of titer, rate and yield sets (a) the sugar bill, (b) the number of fermenters,
   (c) the volume of broth downstream?
2. Why does a 300 m³ fermenter need internal cooling coils when a 1 m³ one does not?
3. Using the electron balance, explain why a process that grows more cells per kg of
   product also needs more O₂ per kg of product.
4. Why is the heat released per mol of O₂ nearly the same for any organism and substrate?
5. A company reports 60 g/L. What else do you need before you can check it against
   oxygen-transfer physics?
6. What is the difference between COP and MSP? Why can two honest TEAs of one plant
   differ so much?
7. Titer doubles at fixed batch time and yield. Which cost terms halve and which do not?
8. Why does downstream recovery multiply every upstream cost?
9. What is the sugar floor at Y = 0.15 g/g, glucose at $0.36/kg and 85% recovery?
10. Intelligen assumes a Lang factor of 4. Against which benchmark would you question it,
    and what should you check first?

<details><summary>Answers</summary>

1. (a) Yield; (b) rate, i.e. titer ÷ cycle time; (c) titer.
2. Heat to remove scales with volume, V, but jacket area only with V^(2/3), so cooling per
   m³ falls as V^(−1/3). At 300 m³ a jacket supports only ~40 mmol/L/h of OUR, or ~25
   once agitation heat is counted, against ~270 at 1 m³ (§5.3).
3. More cells means more glucose per kg product. The electrons of that extra glucose not
   stored in cells go to O₂ to make the ATP that builds them, so O₂ per kg product rises.
4. Thornton's rule: combustion enthalpy per electron transferred to O₂ is nearly constant
   (~110–115 kJ per mol of electrons) across organic compounds, and O₂ takes 4 electrons.
5. Batch time (for rate), yield or cell density (for O₂ per kg), vessel size and pressure
   (for OTR and cooling capacity).
6. COP recovers capital without a return; MSP includes a return on capital (capital charge
   or DCF). Conventions on depreciation, overheads, maintenance and insurance alone move
   Intelligen's result by 12% (exercise A1, step 1.4). Add how capital itself is estimated
   (equipment prices, installation factors, fixed-cost rates) and our base case moves by
   1.3×; published designs sit 1.8× below our model run on the same process (§7.4).
7. Volume-driven DSP roughly halves. So does fermentation capital, because at fixed batch
   time the rate doubles too, provided the tank can supply twice the O₂ and cooling per m³
   (§5.4). Sugar, O₂ per kg and mass-driven DSP do not move.
8. Every kg lost downstream was paid for upstream (sugar, O₂, fermenter time). So each
   upstream cost per kg of *product* is divided by R.
9. 0.36 / (0.15 × 0.85) = $2.82/kg protein.
10. Against two benchmarks. Petrides' facility classes in Humbird's Table 3.1 run from 4.7
    for an outdoor lysine plant up to 7.1 for aseptic lactase. NREL's itemised estimate
    gives 3.1 for its ethanol plant (`humbird2011` Table 28, p.62). So 4 sits between an
    enzyme design report and Petrides' lightest class. Our model brackets it with two
    conventions: Humbird's price-anchored one (effective Lang factor ~6.5) and a light
    design-report one (the published designs use 2.7–4; report, sections 2.5 and 3). First check
    the definition (DFC, FCI or TCI over PEC) and what the purchased cost includes: a bare
    vessel or a piped, instrumented skid. A skid carries part of the installation already,
    and applying the full factor to it is double-dipping.

</details>
