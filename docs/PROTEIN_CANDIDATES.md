# Candidate proteins after BLG, OVA and lactoferrin

**Status (2026-10-01): survey, not model input.** It was compiled by AI research passes (Claude) to
choose the next products for pf-tea. No number here enters `data/pf/base.yaml` or `data/evidence/`
until its quote has been checked against the full text on disk (honesty protocol, point 4). Values
marked **[DERIV]** are the surveyor's own arithmetic: check them before relying on them. The
probabilities are the surveyor's judgement (grade E), recorded so they can be scored later; they are
not pre-registered priors for any model run.

The downloaded sources (FDA and EFSA files, FSANZ A1186, GFI and CE Delft reports, PMC full texts)
are in `references/inbox/protein_survey_2026-10-01/` in the main working copy (git-ignored, like
all of `references/inbox/`). File them into `references/` with an INDEX row before citing them.

**Proposed next step (for Pablo):**
1. The egg-white protein mix centred on ovomucoid, as a parameter swap on the OVA model. Eggs have
   the highest welfare leverage of anything PF replaces outright.
2. Food-grade recombinant serum albumin for cultivated-meat media, which ties pf-tea to Humbird
   2021 and GFI 2023.
3. Casein stays queued for v2.
4. Heme gets a cost-in-use paragraph, not a product line.

Adding any of these is a scope change: record it in docs/SCOPE.md and the PLAN.md decisions log first.

**Update 2026-10-02 (v4):** serum albumin (`alb`) is now a product (data/evidence/albumin.yaml): cation-exchange
capture at cell-culture purity, 1 kt/yr; the column, not the titer, sets its cost. Next in Pablo's order,
one at a time: α-lactalbumin (a membrane-route whey protein, a data change), then κ-/αs1-casein (mostly a
required-titer case: the only κ-casein titer is 0.24 mg/L), then a heme cost-in-use note.

**Update 2026-10-02 (v4, later):** done. α-lactalbumin (`alac`) is a product; α<sub>s1</sub>/κ-casein are a
rennet-cheese blend analysis (report §"Casein for rennet cheese"; best κ titers 4.14 mg/L peer-reviewed,
~0.25 g/L in a patent); heme is a cost-in-use note on secreted LegH (report §"Heme"). Evidence:
data/evidence/alac.yaml, heme.yaml, casein.yaml (α<sub>s1</sub>/κ section). The §1 heme notes below predate
the full-text reads (Shao 2022 and Chen 2025 are now read in full).

**Update 2026-10-01:** β-casein (`cas`) and ovomucoid (`ovd`) are now products, with their evidence in
`data/evidence/casein.yaml` and `ovomucoid.yaml`; §5 and §6 below are the earlier, unverified notes.
Corrections from the full texts: no secreted casein titer is public for any yeast or fungus (Choi's
yeast numbers are intracellular); GRN 1104 is ovalbumin, not an egg-white mix; and a white-protein
product displaces about 275 eggs per kg of egg-white protein, i.e. about 2.5 lives per kg on the
Faunalytics basis (0.85 direct), roughly twice the whole-egg figure used below, because the yolk is a
co-product a white-protein replacement does not displace (ovomucoid.yaml ovd_eggs_per_kg_egg_white_protein).

---


Compiled 2026-10-01. Downloaded copies: see the status note above.

## How to read the tags

**Evidence grade:**

| Tag | Meaning |
|---|---|
| A | Peer-reviewed |
| B | Patent example or regulatory dossier (FDA GRN, EFSA, FSANZ, CFR) |
| C | Company claim, press, catalogue price, market report or consultant model |
| D | Analogy, or derived by me (always marked **[DERIV]**; check these) |
| E | Guess or judgement |

**Where I saw it:**

| Tag | Meaning |
|---|---|
| FT | Full text |
| Abs | Abstract only |
| Press | Press article |
| Snip | Search-engine snippet only, not verified on the page |

**Source keys.** On-disk sources use the repo's `references/text/` keys, for example `GFI_2023_growth_factor...`. Everything else has a URL or DOI.

**Animals per kg.** I use Faunalytics (2023), *Impact of Replacing Animal Products*, as processed by Our World in Data (OWID):
- https://ourworldindata.org/grapher/animal-lives-lost-total
- https://ourworldindata.org/grapher/animal-lives-lost-direct

"Total" includes pre-slaughter deaths, male chicks and feed fish. "Direct" counts only animals slaughtered. Both are US-based and count lives, not welfare-weighted suffering. Grade C for the dataset (a methodology is on OSF).

| Product | Lives per kg, total | Lives per kg, direct | kg meat per animal |
|---|---|---|---|
| Beef | 0.003 | 0.0027 | 364 |
| Chicken | 0.665 | 0.576 | 1.74 |
| Pork | 0.419 (mostly feed fish) | 0.0104 | 96 |
| Eggs | 0.163 | 0.0546 | 18.3 kg eggs per hen |
| Farmed fish | 2.27 | 0.229 | 4.4 |
| Shrimp | 94.3 | 61.0 | 0.016 |
| Cheese | 0.0004 | 0.0002 | — |

I did not pull Faunalytics' days-of-suffering figures. If the model weights animals by suffering-days rather than lives, eggs and dairy rise relative to beef.

**Leverage formula.** Animals spared per kg of PF protein = (lives per kg of food displaced) ÷ (inclusion fraction of the protein in that food) × s.
- s is the substitution rate: kg of animal product displaced per kg of alternative sold.
- I use **s = 1 as an upper bound.**
- In practice s is much lower. Peacock (Rethink Priorities, 2023; *Appetite*, 2026) reviews choice experiments: at equal price and taste, only about 11–27% of consumers pick the plant-based option. In a real dining hall, offering Impossible gave "only a 19 percentage point decline in steak burritos". https://rethinkpriorities.org/research-area/price-taste-and-convenience-competitive-plant-based-meat-would-not-currently-replace-meat/ [A/C, FT summary]

---

## 0. Five things the brief should change

1. **Growth factors are not the main cost driver in Humbird 2021.** In Humbird's fed-batch base case (Table 4.4 and the cost summary, `Humbird2021_cultured_meat.txt`, lines ~3423–3550 [A, FT]):
   - Micronutrients (insulin, transferrin, FGF, TGF-β) cost **$3.13 of $36.79/kg**, which is 8.5% **[DERIV]**.
   - Amino acids ("macronutrients") cost **$19.08/kg**, which is 52% **[DERIV]**.
   - Humbird: "growth factors contribute about $3–4/kg wet cell mass at the 100 kTA scale. At much larger scale, their contribution vanishes entirely."
   - His medium (Essential 8) contains **no albumin**, which GFI 2023 flags (footnote 4).
   - The claim "growth factors are the main cost" holds only at **today's catalogue prices**:
     - Specht/GFI 2020: growth factors are "over 99%" of E8 medium cost [C, FT].
     - CE Delft 2021: recombinant proteins and growth factors are ">99%" of medium cost [C, FT].
2. **Cultivated-meat (CM) firms are designing recombinant proteins out of their media.**
   - Wildtype's FDA file says FGF2 "is the only growth factor used". It also says insulin, IGF, albumin and transferrin are "no longer used in the production process" (FDA CCC 000005 Scientific Memo, p.13–14, https://www.fda.gov/media/186753/download) [B, FT, checked locally].
   - GFI's 2026 State of the Industry report for CM says firms are "frequently eliminating the most costly media components such as insulin, transferrin, and albumin" [C, FT].
3. **Pharma insulin API costs ~$24,750/kg, not ~$25/kg.** The subagent summary had a slip here; the source is Gotham, Barber & Hill (2018), BMJ Glob Health, doi:10.1136/bmjgh-2018-000850 [A, Abs].
4. **There is still no FDA "no questions" letter for any PF casein.**
   - GRN 1312 (Formo/NewMilkBuzz, αS1-casein from *E. coli*) is still pending.
   - GRN 1228 (Fermify) was withdrawn on 13 Jun 2025 [B].
5. **Byproduct proteins have weak welfare leverage. This also applies to the BLG and lactoferrin already in the model.**
   - Gelatin is a slaughter byproduct.
   - USDA ERS (Marti et al. 2011, LDP-M-209-01) says byproducts are ">10 percent of the value for cattle and more than 6 percent of the value for hogs" [B, FT].
   - **[DERIV, D]** By analogy, whey is a cheese byproduct, so displacing whey proteins moves dairy-cow numbers much less than displacing casein or milk. The repo should state this when it frames BLG's welfare relevance. I found no quantitative source for whey's share of milk value.

---

## 1. Heme proteins (meat flavour and colour)

### 1a. Soy leghemoglobin (LegH): Impossible Foods

**Function.** LegH supplies the "meaty" flavour and aroma (heme is released when the meat is cooked) and red-to-brown colour.
- The EU classes it as a **colour additive**.
- The US lists it as a colour additive (21 CFR 73.520) and has also accepted it as GRAS for flavour (GRN 737).
- EFSA GMO Panel 2024, §3.7.2: it helps "recreate the flavour and aroma… through denaturation of soy leghemoglobin and release of the haem B moiety" [B, FT].

**Inclusion rate.**

| Item | Value | Source | Grade |
|---|---|---|---|
| US legal maximum | ≤0.8% of uncooked ground-beef analogue | 21 CFR 73.520(c); GRN 737 letter p.1: "up to 0.8% soybean leghemoglobin protein" (`Impossible_GRN737...txt` l.22) | B, FT |
| **Actual use level** | **0.45% in beef analogue; 0.25% in pork analogue** | FSANZ application A1186 (2019), §D.1: "up to 0.45%… pork analogue products at up to 0.25%" (local `a1186.txt` l.460) | B, FT |
| EU typical level | ≈0.45% **[DERIV]**: 0.8% × 4.1/7.3 mg/kg bw/d (typical-use vs maximum-use exposure) | EFSA FAF Panel, doi:10.2903/j.efsa.2024.8822 | D |
| Singapore limit | ≤0.45% w/w | — | B (secondary, via EFSA FAF) |
| Consistency check | 0.45% × 113 g ≈ 0.51 g LegH ≈ 1.8 mg Fe **[DERIV]**, matching A1186's "approximately 2 mg [heme iron] per serving" | — | D |

**Incumbent.** No animal source makes LegH. Its job is to imitate beef myoglobin, which is 0.8–1.8% of beef (EFSA FAF §1.2, citing Health Canada) [B, via secondary].

**Animal-welfare leverage (upper bound, s = 1) [DERIV]:**
- **Beef:** 1 kg LegH ÷ 0.45% = 222 kg of beef analogue. That spares 222 × 0.003 = **0.67 cattle lives**.
- **Pork:** 1 kg LegH ÷ 0.25% = 400 kg of pork analogue. That spares 4.2 pigs (direct), or 168 lives counting feed fish.
- **Conclusion:** per kg of protein, the reach in kg of food is very high, but beef is the least animal-dense meat.

**Titers and hosts:**

| Host | Titer | Form | Scale | Feed / inducer | Source | Grade |
|---|---|---|---|---|---|---|
| *K. phaffii* | **3.5 g/L, 93% heme bound** | Secreted | 10 L | Abstract mentions "inducible and constitutive" promoters; probably methanol-induced (AOX1), not confirmed | Shao 2022, Bioresour Technol 363:127884, doi:10.1016/j.biortech.2022.127884 (`titers.csv`) | A, Abs |
| *K. marxianus* | **7.27 g/L LBA; heme 66.32 mg/L** | Intracellular | 5 L | Glucose, methanol-free | `Leghemoglobin2023_kmarxianus.txt` | A, FT |
| Same strain, heme loading | ≈24% **[DERIV]**: 0.108 mM heme ÷ 0.45 mM globin at ~16 kDa | — | — | — | — | D |
| *K. marxianus*, process-optimised | **10.1 g/L**; 0.026 g/g glucose | Not stated | 5 L | Glucose, methanol-free | Biotechnol J 2026, doi:10.1002/biot.70239 | A, Abs |
| *K. marxianus* | 1.02 g/L, 73% heme bound | Secreted | 5 L | — | Bioresour Technol 2026, doi:10.1016/j.biortech.2026.134275 | A, Abs |
| Impossible's commercial strain MXY0541 | **Not public** | — | — | Methanol-induced. EFSA GMO §3.3.1: Aox1-deleted (Mut^s) host, Mxr1 overexpressed, LGB2 at AOX2. Methanol is a monitored process parameter (GRN 737 §2.6.2, A1186 §B.4.4). EFSA FAF found no detectable methanol in the product. | Patent US9938327 gives relative yields only (`titers.csv`) | B |

**Regulatory status:**

| Jurisdiction | Status | Grade |
|---|---|---|
| US, GRAS | GRN 540 withdrawn in 2015; **GRN 737** "no questions" on 23 Jul 2018 | B |
| US, colour additive | 21 CFR 73.520 (84 FR 37573, 1 Aug 2019; stay lifted 19 Dec 2019). Petition CAP 5C0336 (Mar 2025) to extend it to poultry and fish analogues and whole cuts is still pending | B |
| EU | Two EFSA opinions: FAF Panel e8822 (May 2024, "does not raise a safety concern" at 0.8%) and GMO Panel e9060 (Oct 2024, safe). **No Commission authorisation as of 2026-10-01.** Impossible launched at UK Tesco on 23 Sep 2026 **without heme** (Green Queen) | B; launch C |
| UK | FSA RP-735 "In progress" | B |
| Canada, Australia/NZ, Singapore | Approved 2020–21 | B |

**EU mechanics, for Pablo.** LegH needs two parallel authorisations:
- one as a new **food additive** (colour), under Regs 1331/2008 and 1333/2008;
- one as **GM food**, under Reg 1829/2003, because the product contains recombinant DNA (EFSA GMO §3.6.2).

After the EFSA opinions, the Commission drafts implementing acts and puts them to member states in the PAFF Committee. GM-food votes usually end in "no opinion", after which the Commission may adopt the act itself. The delay is therefore political and procedural, not scientific.

**Prices, costs and volumes:**

| Item | Value | Source | Grade |
|---|---|---|---|
| Public cost or price from Impossible | Not found | — | — |
| Modelled PF cost, ADL "P1" archetype (LegH, myoglobin, brazzein, monellin) | **$32 / $78 / $122 per kg** (low / mid / high) | GFI Europe & Arthur D. Little 2025, slide 20 (`GFIEurope_2025...txt` l.576–590) | C, FT; titer inputs not disclosed |
| ADL "market" for LegH | 150 t/yr at $275/kg | Appendix (l.1492) | C. Probably trade data on Impossible's own product. Do not use as an incumbent price. |
| Implied beef-analogue volume | 150 t ÷ 0.45% ≈ 33 kt/yr **[DERIV]** | — | D |
| Peer-reviewed heme TEA | Not found | — | — |

**Cost-in-use [DERIV, D].** At 0.45% inclusion, LegH adds $0.14 / $0.35 / $0.55 per kg of analogue at $32 / $78 / $122 per kg protein. Even at $275/kg it adds $1.24/kg. **Cutting heme's production cost barely changes the analogue's price.** Heme's value lies in taste and in getting regulatory approval, not in cost.

**Companies.**
- Impossible Foods (commercial).
- Motif's heme assets were bought by Impossible in the September 2024 settlement.
- Chinese academic groups (Jiangnan) work on *K. marxianus*.

**Tractability for pf-tea: medium-low.**
- The commercial product is a **cell lysate**: bead-mill lysis, centrifugation and microfiltration, then UF, NaCl and ascorbate. It is sold as a **frozen liquid concentrate with 6–9% LegH at ≥65% purity**. Five 2016 batches measured 71–86% purity (GRN 737 full notice, Table 1, https://www.fda.gov/media/124351/download) [B, FT].
- The EU specification is ≥4% LegH and adds a heat-treatment step (EFSA) [B].
- It is **not secreted and not spray-dried**, so modelling it needs a lysis plus frozen-liquid downstream variant.
- The cofactor is heme. The host overexpresses its 8 native heme-pathway enzymes. Academic strains instead feed hemin (an animal-derived input, which adds raw-material cost and a regulatory question).

### 1b. Bovine and other myoglobins: Motif (defunct) and Paleo

| Item | Value | Source | Grade |
|---|---|---|---|
| Function | Colour and "bleed" in beef and pork analogues; heme flavour | — | — |
| Use level (Motif) | **Typical 1–1.25%**, maximum 2% | FDA **GRN 1001** letter p.3 (closed 3 Dec 2021), https://www.fda.gov/media/155001/download. FDA states it is "not an approval for use as a color additive" | B, FT |
| Process (Motif) | *K. phaffii* lysate, UF, frozen liquid ≥3% myoglobin at ≥65% purity; unfolds at 40 °C | GRN 1001 | B |
| Titer: porcine myoglobin, *K. phaffii* | **285 mg/L** secreted, constitutive promoter, **150 mg/L hemin fed**, 0.22 mol heme per mol protein | J Agric Food Chem 2021, doi:10.1021/acs.jafc.1c04124 | A, Abs |
| Titer: mammalian hemoglobins, Pichia | 100–377 mg/L, methanol plus hemin | Fermentation 2024, 10:208 | A, Snip |
| Paleo titers | Not disclosed. Claims a cost cut "by a factor of 613" and scale ">10 m³" (Green Queen, 2 Sep 2026) | — | C |
| Paleo regulatory | GRAS dossier "in preparation" | — | C |
| Paleo products | Beef, chicken, pork, lamb and tuna myoglobins; rodent and rabbit myoglobins for pet food | — | C |
| ADL "market" | 528 t at $187/kg (Alibaba) | GFI Europe appendix | C |
| Motif history | Shut down Sep 2024 after the Impossible patent fight. PTAB had found claims of US 9,943,096 unpatentable in Jun 2024 | Green Queen; AgFunderNews | C/B |

**Leverage [DERIV].**
- Beef at 1.25%: 80 kg of analogue per kg protein, which spares about 0.24 cattle lives.
- Paleo's chicken and tuna myoglobins *could* reach more animal-dense species, but those analogues need little heme.

**Tractability: low-medium.** Public titers are 10–30× below LegH. Hemin feeding is common, and the product is a lysate.

---

## 2. Binders and texturisers for meat analogues (replacing methylcellulose or egg)

**Function.** Hold minced or textured protein together. Binders gel on heating and keep the product juicy.

| Option | Use level | Price | Source | Grade |
|---|---|---|---|---|
| Methylcellulose (MC), the incumbent | 1.5–4%; "3% MC… ideal" | **Bulk food-grade price not found.** Industrial HPMC/MC ~$2.2–3.2/kg; Alibaba food-grade quotes $3–9/kg; Tridge customs values $1.2/kg (mixed grades). Mark as `source: guess` | Bakhsh 2021 Foods 10:560 (PMC8000783) | A, FT (use); C (price) |
| Egg white in Quorn | Under ~9% by difference **[DERIV]**; the label lists mycoprotein 91% | Not stated | quorn.co.uk. Quorn says egg whites help products "keep their shape and texture" (VegNews, 18 Aug 2025); its vegan line uses potato protein | C |
| PF ovalbumin (Onego Bioalbumen, *T. reesei*) | **Meat analogs: 10% maximum** (Table 1); listed functions "foaming, gelling, and binding agent"; spec "≥75% protein… ≥80% ovalbumin" | — | **GRN 1249**, closed 16 Sep 2025 (local `grn1249.txt` l.70) | B, FT |
| PF egg-white protein (EVERY, *K. phaffii*) | Use in plant-based meat at cGMP levels | — | **GRN 1104**, closed 17 Oct 2023 | B |
| EVERY × The Vegetarian Butcher (Unilever) | Wanted to get "methylcellulose out of their formulations"; claims "twice the gelling power" of egg white | — | Press release, 15 May 2024 | C |
| Patatin (potato) | 1–15 wt% (prefer 2–10%) as an MC-free binder | Potato protein bulk $7–12/kg (Snip); Solanic retail ~€67/kg | Avebe EP3944769A1 | B; price C/weak |
| Patatin by PF, *K. phaffii* | 1.42 g/L (5 L), gels at a lower temperature than native | — | Dai 2022 Food Res Int 162:111925 | A, Abs |
| Patatin by PF, *K. phaffii* | 3.2 g/L (5 L) | — | Huang 2025 Synth Syst Biotechnol, doi:10.1016/j.synbio.2025.01.003 | A, Abs |
| RuBisCO (plant extract, not PF): Plantible/ICL | Claims it "outperforms methylcellulose", works at 4%, contracts in the hundreds of t/yr | — | AgFunder 2023 | C |
| Recombinant actin / myosin fragment, *E. coli* | 326 / 572 mg/L at 69–73% purity; improves chewiness | — | Dolgin & Kaplan 2026, ACS Biomater Sci Eng, doi:10.1021/acsbiomaterials.6c00392 | A, Abs; early-stage |

**Leverage [DERIV, D].** Plant-based chicken nuggets are the high-leverage case (0.665 lives per kg).
- A binder at 3–10% gives 10–33 kg of analogue per kg protein, i.e. **6.6–22 chicken lives** at s = 1.
- But the **counterfactual binder already exists**: MC, potato protein, RuBisCO. The *incremental* animals spared from a PF binder come only from better products (clean label, texture). That is plausibly a small fraction of the headline number.
- The exception is egg white in vegetarian products such as Quorn, where PF OVA directly displaces hens. The volume is unknown.

**Cost-in-use [DERIV, D].**
- OVA at 3–10% × $20/kg = $0.6–2.0/kg of analogue.
- MC at 1.5–4% × $3–9/kg (guess) = $0.05–0.36/kg.
- So PF OVA must win on function or label, not on cost. **The OVA cost the model already computes is the right input. No new protein model is needed, only a cost-in-use comparison.**

**Tractability: high.** OVA is already in the model. Patatin would be a new product with a poor titer and a cheap plant incumbent, so it is not worth adding.

---

## 3. Collagen and gelatin

**Function.** Gelling agent (confectionery, desserts), collagen peptides (supplements), and casings.

**Incumbent volumes:**
- World gelatine demand was 620 kt in 2019 (EFSA J 2024, doi:10.2903/j.efsa.2024.8883, §3.3.2.1, a secondary citation inside EFSA) [B, FT].
- IMARC gives 477 kt for 2025 [C].
- EU production is 120–125 kt/yr of gelatine and collagen peptides [B, FT].

**Raw materials:**
- World: pig skin 46%, bovine hide 29.4%, bone 23.1%, fish and poultry ~1.5% [B].
- EU edible gelatine: about 80% from pork skins (GME, the industry association) [C].

**Prices:**
- IMARC, Q2 2026: US $6,576/t; Germany $6,580/t; China $7,152/t [C].
- GFI 2025: food-grade hydrolysed collagen and gelatin "$6.5 to $9.3/kg" at >90% protein (`GFI_2025_driving_down_costs...txt` l.1217) [C, FT].
- ADL: collagen 680 kt at $8/kg [C].

**Welfare leverage: about zero at the margin (D).**
- Gelatin is a slaughter **byproduct**. Byproducts are >6% of hog value and >10% of cattle value; hides account for most of the cattle byproduct value, and hides contribute "very little" to hogs (USDA ERS 2011) [B, FT].
- No elasticity of slaughter with respect to gelatin demand was found.
- EFSA notes that EU gelatine volumes fluctuate with raw-material availability, i.e. supply follows slaughter.
- The welfare case rests on vegan, halal and kosher demand, not on reducing slaughter.

**Titers:**

| Product / host | Titer | Source | Grade |
|---|---|---|---|
| Non-hydroxylated gelatin, *P. pastoris* | 14.8 g/L | Werten 1999, Yeast 15:1087 | A, Abs |
| Recombinant humanised type I collagen, *P. pastoris* | **15.3 g/L at 500 L** | Zhang 2026, Appl Microbiol Biotechnol, doi:10.1007/s00253-026-13862-6 | A, Abs |
| Hydroxylated collagen (co-expressed prolyl-4-hydroxylase, P4H) | 0.5–2.5 g/L | Ma 2025, doi:10.1007/s00253-025-13566-3; Nokelainen 2001 | A, Abs |

**Gelling requires hydroxylation.** de Bruin 2002 FEMS Yeast Res: "prolyl 4-hydroxylation is essential for the gel-forming capacity of gelatin" [A, Abs]. Werten 2009 shows designed non-hydroxylated block polymers can gel at ~37 °C [A, Abs].

**PF companies and TEAs:**
- **Geltor:** GRN 1171 ("no questions" 22 Oct 2024). It is an *E. coli* chicken collagen XXI fragment (17.9 kDa, ≥80% protein, used at 2–95%), a **non-gelling polypeptide, not gelatin** [B, FT]. Gelzen is Geltor's former name.
- **Chinese recombinant collagen:** cosmetic and medical grade at about 10–20 t/yr per firm (e.g. Giant Biogene 10.9 t/yr capacity) [C].
- **Intelligen bio-collagen TEA:** 17.5 g/L, 5 days, 50 t/yr, acetone precipitation, ion exchange and freeze-drying (`INDEX.md`). GFI 2025 cites its cost as **$1,043/kg** "collagen peptide" at ~90% purity (`GFI_2025...txt` l.1113) [C, FT of GFI; the Intelligen report itself is not on disk]. GFI's Table 2 row shows 938.96 in a cost column; the unit is ambiguous, so check against the Intelligen PDF.

**Tractability: low.**
- The target price is ~$7/kg against a byproduct incumbent, with near-zero welfare leverage.
- Hydroxylation complexity applies if gelling is needed.
- The secreted, non-hydroxylated product is easy to make but does not gel.

---

## 4. Cultivated-meat growth-medium proteins

### Demand and targets (on disk)

**GFI 2023** (`GFI_2023_growth_factor...txt`) [C, FT]:
- Volume shares: "96.6% of production volume… albumin, 2.42% to transferrin, 0.97% to insulin, and only 0.02% to all other growth factors" (l.92–99).
- Albumin demand of 3,600–100,000 t/yr in 2030 scenarios (l.409).
- Current transferrin production "only 0.2 to 0.3 metric tons annually" (l.410).
- Cost targets: albumin **$10/kg**, insulin and transferrin **$1,000/kg**, growth factors **$100,000/kg**, so that recombinant proteins are about $1 of a $10/kg meat (l.117–126).
- The implied average albumin concentration is ≈**1.1 g/L** **[DERIV]**: 3,600 t ÷ (0.4 Mt × 8 L/kg) = 1.125 g/L, and the high scenario gives 1.13 g/L. The exact value is in the GFI supplementary spreadsheet, Tab 1.

**CE Delft 2021 TEA** (Annex B) [C, FT]: total recombinant protein of 1.0 / 7.1 / 50 g per kg CM at 8 / 13.4 / 41.7 L/kg (low / mid / high).

**Humbird 2021** [A, FT]:
- Price-volume regression for proteins (Eq 3.4): log P = −0.861 log V + 4.90.
- Reaching $1,000/kg requires ~160 t/yr.
- Insulin demand of 13–39 t/yr at 100 kt/yr of CM.

### Per protein

| Protein | Dose in medium | Price today | Best microbial titer | Tractability | Being substituted? |
|---|---|---|---|---|---|
| **Serum albumin (HSA/BSA)** | Beefy-9: 0.8 g/L (Stout 2022 Commun Biol, doi:10.1038/s42003-022-03423-8) [A, FT]; Kolkmann 5 g/L, "approximate cost of 163 USD/L only for HSA" (as cited in Schenzle 2025 Sci Rep) [A, FT] | Cellastim S (rice): $548/10 g, $4,349/100 g = **$43–55k/kg [DERIV]** [C, FT]. GFI 2025 says "high-value albumins ranged from $40 to $70/kg in public trade databases" (l.1238), presumably plasma-derived bovine; the grade is unclear [C]. ADL: 85 t at $485/kg [C] | ***K. phaffii*: 17.47 g/L secreted after 192 h of methanol induction** (Zhu 2021, Protein Expr Purif 181:105831, doi:10.1016/j.pep.2021.105831) [A, Abs]; 10 g/L (Mallem 2014); 8.86 g/L at >96% purity, 58% recovery (Zhu 2018) [A, Abs]. *S. cerevisiae* Recombumin (methanol-free, cGMP): titer not public | **High.** Secreted, **no N-glycans**, 17 disulfides (UniProt P02768). The cell-culture endotoxin spec is ≤1.0 EU/mg (InVitria); no food-grade spec exists | **Yes, strongly:** rapeseed protein isolate at 0.4 g/L ("input cost… $0.002" per L, Stout 2023 Beefy-R preprint) [A, FT]; methylcellulose at 0.11 g/L matches 0.8 g/L HSA (Schenzle 2025) [A, FT]; cyclodextrins (Wildtype; Pasitka 2024 Nat Food) [B/A] |
| **Transferrin** | E8: 10.7 mg/L; B8: 20 mg/L, reducible to 5 (Kuo 2020, doi:10.1016/j.stemcr.2019.12.007) [A, FT] | Optiferrin: $2,177/10 g = $218k/kg [C]; CE Delft: $246/g [C] | ***S. cerevisiae*, non-glycosylated N413Q/N611Q mutant: 2.29 g/L, methanol-free, cGMP** (Finnis 2010, Microb Cell Fact 9:87) [A, FT]. Pichia: 20–30 mg/L | Medium: 19 disulfides and 2 N-glycans (removable); iron loading | Yes: hinokitiol (Ajinomoto, Apr 2026) [C]; Wildtype dropped it [B] |
| **Insulin** | 19.4–20 mg/L | Pharma API **$24,750/kg** (Gotham 2018) [A, Abs]; cell-culture Sigma ~$2,700/g **[DERIV]** [C] | *K. phaffii*: ~3 g/L precursor, ~1.5 g/L 99% insulin, methanol (Gurramkonda 2010, Microb Cell Fact 9:31) [A, Abs]. Novo's *S. cerevisiae* process: not public | Medium: precursor plus enzymatic processing; already a mature PF product | Yes: dropped (Wildtype); IGF-1 can replace it |
| **FGF2** | 40–100 ng/mL | 2019: $2.0M/g (Specht) [C]; Qkine FGF2-G3 £880/mg [C]; in-house *E. coli* CAD$10.22/mg (Venkatesan 2022) [A] | *E. coli* FGF2-G3: 2.95 g/L batch bioreactor, intracellular (Manavalan 2026 PEP, doi:10.1016/j.pep.2026.106894) [A, Abs]; 115 mg/L purified at 500 L (Li 2023) [A, Abs]; Pichia secreted ~150 mg/L (Mu 2008) [A, Abs] | Easy molecule (no disulfides, no glycans), but **tonnage is tiny** (Humbird: ~70–200 kg/yr at 100 kt/yr CM) | Partly: autocrine FGF2 cell lines (Stout 2023) [A, Abs]. Still used by Wildtype |
| **TGF-β** | 0.1–2 ng/mL | 2019: $80.9M/g (CHO-made) [C] | *E. coli* TGF-β3: 300 mg/L monomer, needs refolding (Zhou 2019) [A, Abs] | Hard (disulfide-linked dimer), but only kg/yr needed | Often omitted |
| **IGF-1 / LR3** | ng/mL | Not gathered | *E. coli* 1.26 g/L, inclusion bodies (Ranjbari 2015); Pichia ~0.5–1 g/L as a fusion (Lu 2023) [A, Abs] | Medium | — |

**Cost of the medium today [C/A]:**
- E8 at catalogue prices: $376.80/L, of which "over 99%" is growth factors (Specht/GFI 2020).
- Beefy-9 bulk: $46–74/L; drivers are FGF2, rAlbumin and insulin (Stout 2022).
- Beefy-R: $49.7/L, with FGF2 ">60%" (Stout 2023).
- Firms claim ≤$0.20/L (GFI SOTI 2026) or ≤$1/L (Lever VC 2025). These are unverifiable [C].

**What PF cost would matter? [DERIV, D]:**
- Albumin at ~9–14 g per kg CM (1.1 g/L × 8–13 L/kg):
  - catalogue price ($45k/kg) gives **$400–630/kg CM**;
  - $100/kg gives $0.9–1.4/kg CM;
  - $10/kg gives $0.09–0.14/kg CM.
- **The model would answer one question: whether food-grade PF albumin from a 1–10 kt/yr plant lands nearer $10 or $100/kg.** That decides whether keeping albumin is a viable media strategy. Across that band, albumin goes from negligible to about 5–10% of a $15/kg CM cost.

**Welfare leverage [DERIV].** If CM chicken displaces chicken 1:1 and albumin is used at 9–14 g/kg, 1 kg of albumin enables 70–110 kg of CM, i.e. **47–74 chicken lives**. This is conditional on (i) CM reaching scale and (ii) albumin staying in the medium. Both are in doubt.

**Regulatory status:**
- No FDA GRAS notice or EFSA dossier exists for recombinant albumin, transferrin, insulin or growth factors as CM inputs.
- UPSIDE's FDA file (CCC 000002) lists "bovine serum albumin, growth factors" with identities kept confidential [B].
- Rice-made rHSA (Healthgen) was approved by China's NMPA as a drug in 2025 [C, Snip].

**Companies:**
- Albumin and transferrin: InVitria (rice), Sartorius/Albumedix (*S. cerevisiae*), Healthgen/Oryzogen (rice).
- Growth factors: Qkine (*E. coli*), ORF Genetics (barley), Core Biogenesis (camelina), BioBetter (tobacco), Future Fields (Drosophila).
- Media: Multus.
- Media and transferrin replacement: Ajinomoto.
- Protein-free media: Meatly, PARIMA.

**Market context [C]:**
- Only Wildtype, GOOD Meat and Vow had sustained sales in 2025.
- Vow runs at 20,000 L.
- CM investment was $73.9M in 2025, down from $144M in 2024 (GFI SOTI 2026).
- Believer shut down in December 2025.

---

## 5. Casein (queued for v2): status note

- **Function:** micelles, curd and melt in cheese. This is where plant-based dairy is weakest.
- **Use level:** Formo's GRN 1312 proposes up to 25 g/100 g in cheese analogues [B].
- **Regulatory:**
  - US: no "no questions" letter yet. GRN 1312 (Formo/NewMilkBuzz, *E. coli* αS1) is pending; GRN 1228 (Fermify) was withdrawn on 13 Jun 2025 [B]. New Culture, Those Vegan Cowboys and AuX Labs are self-GRAS [C].
  - Australia/NZ: Eden Brew's β-casein from *K. phaffii* (FSANZ A1342) is under assessment and was "accepted" in Dec 2025 (`GFI_2026_state_of_industry...txt` l.2572) [B/C].
- **Titers:** public titers are poor. Bacteria reach ≤1.45 g/L (αs1-casein, *E. coli*) and yeast ≤1 g/L (β-casein, Pichia) (Mora Vásquez 2025 Biomolecules, doi:10.3390/biom15071031) [A, FT, secondary]. *B. subtilis* αs1 reached 56.9 mg/L [A, Abs]. Company titers are not public.
- **Phosphorylation:** yeasts lack the Fam20C kinase, so phosphorylation is incomplete. Non-phosphorylated β-casein still forms acid gels (GFI SOTI 2026) [C].
- **Incumbent price:** USDA Dairy Market News (Sep 2026) gives acid casein $4.25–5.25/lb = **$9.37–11.57/kg [DERIV]** and rennet casein $9.48–12.02/kg [B, FT]. ADL: 486 kt at $7/kg [C].
- **Welfare [DERIV]:** cheese at 25% casein gives 4 kg cheese per kg casein × 0.0004 lives/kg ≈ 0.002 lives. It is very low on lives, but casein is the main lever on dairy cows' suffering-days and on the dairy business model (whey is a byproduct of cheese).
- **Keep it queued.** It is tractable in the same model (secreted from Pichia or *T. reesei*, spray-dried; the *E. coli* route would need an intracellular variant), but its cost floor is demanding at ~$10/kg.

---

## 6. Other candidates with welfare leverage

| Candidate | Key evidence | Verdict |
|---|---|---|
| **Ovomucoid / egg-white protein mix (EVERY)** | GRN 967 (ovomucoid, K. phaffii GSD-1209, closed 9 Sep 2021) [B]. **30.19 g/L ovomucoid** broth titer, EVERY patent US20240209383 Ex. 9 (`titers.csv`) [B, FT]. 3.2 g/L at 168 h (Beck 2025 Table 2) [A secondary]. Ovomucoid is ~11% of egg-white protein. ADL price $966/kg, which looks like a niche or lab price [C] | **Add.** Highest-welfare product line (eggs), data are good, and it fits the existing OVA model |
| Lysozyme (egg white, 3.4% of EW protein) | *K. phaffii* 3.5 g/L at 15 L (Beck Table 2, Cui 2022) [A sec]; price $100–500/kg in listings [C]; ADL 1,763 t at $280/kg [C]. Primary source for $280/kg not found | Niche preservative; welfare ≈ 0 (byproduct of egg breaking). Skip |
| Ovotransferrin | Pichia 97 mg/L [A sec]; ADL price $789,700/kg is spurious [C] | Skip |
| Pet food (Bond Pet Foods) | **Whole-cell** *S. cerevisiae* biomass, 90 g/L DM; the target chicken protein is "10–15%" of biomass; 53% crude protein (Smola 2025 Front Vet Sci, PMC12278293) [A, FT, Bond co-authors]. 10 t delivered; FDA Center for Veterinary Medicine review pending [C]. US pets eat ~25% of US animal-derived energy **[DERIV]** from Okin 2017 ("33% ± 9%" relative to humans) [A, Abs] | High leverage but **out of scope** (no purification; a biomass-like process). Worth a "no-DSP whole-cell" variant later. Implied target-protein titer ~9–14 g/L **[DERIV, D]**, check |
| Fish / seafood PF proteins | Nothing commercial found. Cultivated-seafood firms (Wildtype, BlueNalu) are not PF | Fish and shrimp have the highest lives per kg, but there is no PF data. Watch only |
| Recombinant myofibrillar proteins | Actin 326 mg/L, myosin-tail fragment 572 mg/L in *E. coli* (Dolgin 2026) [A, Abs] | Too early |

---

## 7. Comparison table

All per-kg leverage figures are **[DERIV, D]** upper bounds at s = 1. "Cost-in-use" is the PF protein's cost per kg of final food. Grades refer to the underlying inputs.

| Protein | Function | Inclusion | Food displaced → lives per kg PF protein | Incumbent $/kg (t/yr) | Best public titer (host, mode) | Regulatory | Cost-in-use sensitivity | Tractability in pf-tea |
|---|---|---|---|---|---|---|---|---|
| Soy LegH | Flavour, colour | 0.45% beef, 0.25% pork [B] | Beef: 0.67; pork: 4.2 direct | None (ADL "market" 150 t @ $275 [C]) | 3.5 g/L secreted Kp (meth?) [A Abs]; 10.1 g/L Km methanol-free [A Abs] | GRN 737; 21 CFR 73.520; EFSA positive, EU decision pending | **Low:** $0.14–0.55/kg at $32–122/kg | Med-low: lysate, frozen liquid, heme |
| Myoglobin | Colour, bleed | 1–1.25% [B] | Beef: ~0.24 | ADL 528 t @ $187 [C] | 285 mg/L Kp + hemin [A Abs] | GRN 1001 (Motif, defunct) | Low | Low |
| OVA / egg white as binder | Binding, gelling | ≤10% (GRN 1249) [B]; 3–10% | Chicken analogue: 6.6–22 (mostly counterfactual MC) | MC $3–9 (guess); egg white $15.6–59.4 per kg protein [C] | Already modelled | GRN 1104, 1249 | Medium: competes with cheap MC | **Done** (OVA). Add cost-in-use only |
| **Ovomucoid / EW mix** | Egg replacement (baking, beverages) | Up to 100% of egg-protein function | Eggs: ~1.3 total / 0.43 direct (7.9 kg egg per kg protein at 12.6% protein, Beck 2025) | Egg white $15.6–59.4 per kg protein [C] | **30 g/L Kp** [B]; 3.2 g/L [A sec] | GRN 967, 1104 | **High:** the protein is the product | **High:** same as OVA |
| Gelatin / collagen | Gelling, peptides | ~100% (the product) | ≈0 at the margin (byproduct) | **$6.5–9.3**, ~480–620 kt [B/C] | 14.8–15.3 g/L non-hydroxylated Kp [A Abs]; hydroxylated ≤2.5 g/L | Geltor GRN 1171 (non-gelling) | High, but the target is ~$7/kg | Low: hydroxylation for gelling |
| **Serum albumin (CM)** | Carrier in cell medium | ~1.1 g/L, ~9–14 g/kg CM | CM chicken: 47–74 (conditional on CM scale and albumin use) | $43–55k/kg catalogue; $40–70 trade [C]; 85 t (ADL) | **17.5 g/L Kp methanol** [A Abs] | None for CM | **Very high** between $10 and $1,000/kg | **High:** secreted, non-glycosylated; needs low-endotoxin DSP variant |
| Transferrin | Iron carrier | 5–20 mg/L | Tiny tonnage | $218k/kg [C]; 0.2–0.3 t/yr | 2.29 g/L *S. cerevisiae* methanol-free [A FT] | None | Medium; substitutable | Medium |
| Insulin | Growth signal | ~20 mg/L | Tiny tonnage | API $24,750/kg [A]; RHI ~3.2 t/yr (Humbird) | ~1.5 g/L Kp [A Abs] | Pharma | Low (being dropped) | Medium (processing) |
| FGF2 / TGF-β / IGF-1 | Growth factors | ng/mL | kg/yr | $0.9–80M/kg [C] | FGF2 2.95 g/L *E. coli* intracellular [A Abs] | None | Low per kg CM at ≤$100/g | **Poor fit:** kg/yr, pharma-like DSP |
| Casein (v2) | Cheese structure | ~25% of cheese analogue [B] | Cheese: ~0.002 (dairy suffering-days matter more) | $9.4–12/kg [B]; ~486 kt [C] | ≤1.45 g/L *E. coli*; ≤1 g/L Pichia [A sec] | No GRAS "no questions" yet | High | Medium (phosphorylation, micelles) |

---

## 8. Ranked recommendation

**Scoring.** Each candidate is scored on animal-welfare leverage × cost sensitivity (whether a PF cost cut would change displacement) × data availability × tractability in an aerobic fed-batch, membrane or chromatography, spray-dried model. All probabilities below are my judgement (grade E) and are meant to be scored later.

### 1. Ovomucoid and egg-white protein mixes (OVA + ovomucoid ± lysozyme)

**Why:**
- Eggs carry the highest lives and suffering per kg of any product that PF can directly replace at 100% "inclusion". The protein *is* the product, so cost directly drives displacement.
- The data are the best of any candidate: 30 g/L ovomucoid patent example [B], two GRAS notices (967, 1104) [B], and the EVERY patents already on disk.
- It is a parameter swap on the existing OVA model, with a different molecular weight, titer, yield and spec.

**Forecasts:**
- P(nth-plant PF egg-white protein cost < $20/kg protein, public-data base case, by 2035) ≈ 0.35.
- P(< $40/kg) ≈ 0.65.
- These depend on what the OVA model already shows; update them from its results.

### 2. Food-grade recombinant serum albumin for CM media (transferrin as a cheap add-on)

**Why:**
- It is the only CM medium protein with real tonnage (96.6% of recombinant-protein volume, GFI 2023).
- It is model-tractable: secreted, no glycans, 9–17 g/L in Pichia [A Abs]. Only the endotoxin and purity variant is new.
- **It is the protein whose PF cost spans "decisive" to "negligible" for CM cost.**
- It links the TEA directly to Humbird and GFI 2023, and tests GFI's $10/kg target.

**Caveat:** demand is being designed out (Wildtype; rapeseed protein, MC and cyclodextrin substitutes). Its welfare value is conditional on CM scaling and on albumin staying in the medium.

**Forecasts:**
- P(food-grade PF albumin nth-plant cost < $10/kg by 2035) ≈ 0.10.
- P(< $50/kg) ≈ 0.45.
- P(recombinant albumin demand for CM > 1 kt/yr in 2035) ≈ 0.08.
- P(the median scaled CM medium in 2030 contains no recombinant albumin) ≈ 0.6. The CM subagent put the analogous probability, covering albumin, transferrin and insulin together, at 0.65.

**Still worth doing because:**
- It is cheap given the existing model.
- The result ("PF albumin floor is about $X/kg at Y kt/yr") is a direct input to the media-design choice and to every CM TEA.

### 3. Casein (keep queued as v2)

**Why:**
- Large volume (~0.5 Mt/yr).
- Cost-sensitive: it is the bulk ingredient, with a ~$10/kg incumbent.
- It enables cheese, the weakest plant-based category.

**Weaknesses:**
- Low lives per kg.
- Public titers ≤1.5 g/L.
- Phosphorylation and micelle formation are hard.

**Forecast:** P(PF casein nth-plant cost < $12/kg by 2035) ≈ 0.15.

### 4. Heme (LegH, myoglobin): cost-in-use bound plus a lysate downstream variant, not a full product line

**Why:**
- It is important for beef and pork analogue taste and regulation.
- But at 0.25–1.25% inclusion, **its cost barely affects analogue price** ($0.14–0.55/kg at ADL's $32–122/kg).
- Beef has the lowest lives per kg.

**Effort:** a one-page cost-in-use calculation plus an optional "intracellular, lysis, UF, frozen-liquid concentrate" downstream variant (GRN 737 spec). Data: 3.5 g/L secreted, 7–10 g/L intracellular [A Abs/FT].

**Forecast:** P(PF LegH production cost < $100/kg today at Impossible's scale) ≈ 0.6. Weak evidence: the ADL mid estimate is $78/kg [C], and the Shao and K. marxianus titers are well above 1 g/L.

### Not recommended now

| Candidate | Reason |
|---|---|
| Collagen / gelatin | Byproduct incumbent at ~$7/kg, near-zero marginal welfare effect, hydroxylation needed. P(PF gelling gelatin < $7/kg by 2035) ≈ 0.03 |
| FGF2 / TGF-β / IGF-1 / insulin | kg/yr tonnage and pharma-like downstream do not fit a 1–100 kt/yr food plant model. Insulin and transferrin are being dropped |
| Patatin, lysozyme, ovotransferrin | Cheap plant incumbent, byproduct, or a spurious market |
| Pet-food whole-cell (Bond) and fish proteins | Out of scope or no data. Revisit as a "no-DSP" variant |

**Context forecast.** P(any CM product sold at > 1 kt/yr and at a production cost < $20/kg by 2035) ≈ 0.10. This bounds the value of item 2.

---

## 9. Documents worth downloading

Items marked (S) are in `references/inbox/protein_survey_2026-10-01/`. They are in `references/inbox/protein_survey_2026-10-01/` and could be filed into `references/`.

### Heme

1. Shao et al. 2022, *Bioresour Technol* 363:127884, doi:10.1016/j.biortech.2022.127884. Full-text methanol regime, time, yield (paywalled; already in TO_FETCH).
2. Impossible GRN 737 **full notice**, https://www.fda.gov/media/124351/download (S: `grn737_notice.pdf`). Batch purity and process.
3. EFSA FAF 2024, doi:10.2903/j.efsa.2024.8822 (S: `faf*.pdf`), and EFSA GMO 2024, doi:10.2903/j.efsa.2024.9060 (S: `efsa_gmo.pdf`). EU spec, strain, exposure.
4. FSANZ A1186 application (S: `a1186.pdf`). The only public actual use levels (0.45% / 0.25%).
5. Motif GRN 1001 letter (S: `grn1001_letter.pdf`) and its full notice (FDA inventory).
6. *K. marxianus* LegH 10.1 g/L, *Biotechnol J* 2026, doi:10.1002/biot.70239. Methanol-free yield on glucose.

### CM media proteins

7. Zhu et al. 2021, *Protein Expr Purif* 181:105831, doi:10.1016/j.pep.2021.105831; Mallem 2014, doi:10.1002/btpr.1990; Zhu 2018, doi:10.1016/j.pep.2018.02.003. rHSA titer, time, recovery, purity: the core inputs for item 2.
8. Finnis et al. 2010, *Microb Cell Fact* 9:87 (open access). Transferrin in *S. cerevisiae*.
9. Gurramkonda et al. 2010, *Microb Cell Fact* 9:31 (open access). Insulin in Pichia.
10. GFI 2023 growth-factor report, **supplementary spreadsheet** (gfi.org). Exact albumin concentrations (Tab 1).
11. CE Delft 2021 cultivated-meat TEA with corrigendum (S: `cedelft.pdf`); Specht/GFI 2020 medium cost analysis (S: `gfi_specht.pdf`); GFI 2026 SOTI cultivated (S: `gfi_soti2026.pdf`).
12. Stout et al. 2022 *Commun Biol* (Beefy-9, open access); Stout 2023 *Biomaterials* 296 (Beefy-R); Kuo 2020 *Stem Cell Rep* (B8, open access; S: `kuo.txt`); Schenzle 2025 *Sci Rep*, doi:10.1038/s41598-025-99603-7 (S); Pasitka 2024 *Nat Food*, doi:10.1038/s43016-024-01022-w.
13. FDA CCC 000005 Wildtype memo (S: `fda_wildtype_sci.pdf`) and CCC 000002 UPSIDE (S). Evidence that media proteins are being designed out.
14. Negulescu et al. 2023, *Biotechnol Bioeng* 120:1055, doi:10.1002/bit.28324. Second CM TEA alongside Humbird.
15. Gotham, Barber & Hill 2018, *BMJ Glob Health*, doi:10.1136/bmjgh-2018-000850. Insulin API cost.

### Egg

16. FDA GRN 967 and GRN 1104 **full notices**, and GRN 1249 (Onego; S: `grn1249.pdf`). Specs, use levels, process. GRN 967 and 1104 are already in TO_FETCH.

### Collagen / gelatin

17. EFSA 2024 gelatine/collagen BSE opinion, doi:10.2903/j.efsa.2024.8883. Volumes and raw-material split.
18. Werten 1999 *Yeast* 15:1087; de Bruin 2002 *FEMS Yeast Res*; Zhang 2026, doi:10.1007/s00253-026-13862-6.
19. Intelligen bio-collagen TEA (ResearchGate 380458369). Its cost number; GFI's $1,043/kg is second-hand.

### Welfare framing

20. USDA ERS LDP-M-209-01 (Marti, Johnson & Mathews 2011), "Where's the (Not) Meat?" (S: `ldpm.txt`). Byproduct value shares; relevant to gelatin *and* to BLG/whey framing.
21. Faunalytics Animal Product Impact Scales, OSF data and method (https://faunalytics.org/animal-product-impact-scales/). Lives and suffering-days per kg, with documentation.
22. Peacock 2023 (Rethink Priorities) / *Appetite* 2026. Substitution-rate evidence.
23. Okin 2017 *PLoS One*, doi:10.1371/journal.pone.0181301. Pet share of animal products.

### Casein and other

24. Mora Vásquez 2025 *Biomolecules*, doi:10.3390/biom15071031 (open access). Casein titer table.
25. FDA GRN 1312 (Formo) once FDA responds. The first PF casein specification.
26. Smola 2025 *Front Vet Sci* (Bond; PMC12278293). Whole-cell PF economics, if a no-DSP variant is ever added.

---

## Known gaps (not found)

**Heme:**
- Impossible's LegH tonnage, titer and cost.
- Public LegH or myoglobin $/kg beyond ADL's model.
- Shao 2022 full-text process details.

**Binders and casein:**
- Bulk food-grade methylcellulose price.
- Company casein titers.

**Collagen and egg proteins:**
- Intelligen collagen cost from the primary source.
- Primary source for lysozyme $280/kg.

**CM media proteins:**
- A food-grade purity or endotoxin spec for CM media proteins.
- Recombumin and Novo insulin industrial titers.
- A scaled, peer-reviewed TEA of microbial production of any CM medium protein (none exists, which is itself a reason for item 2).

**Welfare:**
- Faunalytics days-of-suffering per kg (not extracted).
- A quantitative elasticity of slaughter with respect to byproduct (gelatin or whey) demand.
