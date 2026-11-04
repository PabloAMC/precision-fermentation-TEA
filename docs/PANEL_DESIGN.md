# Model panel: design from first principles

Draft of 2026-11-03 (Claude, for Pablo's review). This plans the interactive panel (`docs/panel.html`)
from scratch, without reference to the current explorer. It states what the panel must do, then the
structure, then how each number on it is produced and checked.

## 1. Who reads it, and what they must leave with

Two readers:
- **A newcomer** (funder, policy, journalist). They want the answer: what does this protein cost, against
  what price, and why.
- **A checker** (reviewer, Pablo). They want to see that every number follows from stated inputs by stated
  arithmetic, and that the inputs come from sources.

The panel must let both get what they need without reading the report.

## 2. Desiderata

Ranked. A lower one never overrides a higher one.

1. **Honest.** The panel shows only numbers the model produced, or exact arithmetic on them. It never shows
   a price for a design that breaks a physical limit. The four scenarios are never merged. Interpolated
   values are marked as such. Exclusions (R&D, royalties, first-of-a-kind) are stated next to the answer.
2. **The answer first.** One protein, one cost, one price to beat, and the conditions the cost rests on
   (titer, time, yield, scale). PLAN.md: "no point estimate without its titer, rate and yield stated next to it".
3. **The mechanism is visible.** A reader should see why the cost is what it is. The model's core is a
   chain: strain performance sets fermenter output; fermenter output sets the number of fermenters; that
   sets the capital; capital, spread over output, is the largest cost. The panel shows this chain as
   numbered steps.
4. **Every step can be checked.** Each step shows its equation, the numbers substituted and the result.
   The page redoes the arithmetic itself and compares it with the model's own value (a tick or a cross).
   Each input links to its row in the inputs table, with its source and kind of evidence.
5. **Costs are quantity times price.** Each cost line is a physical amount per kg (kg sugar, kWh, salary-years,
   dollars of plant) times a unit price. The reader can change a price and see the exact effect.
6. **What would change the answer.** Levers for what the report says matters most: titer, production time,
   plant scale, sugar price, capital charge, location. A map of titer against time shows where the cost
   meets the price to beat, and where the fermenter cannot supply the oxygen or remove the heat.
7. **How sure.** The kind of evidence of each input; the tornado; the Monte Carlo range of the scenarios.
8. **Practical.** One static file. No install, no network. Works at phone width. A link can encode the
   state (protein and levers), so a reviewer can cite one exact view.

Non-goals: running the full model in the browser (one plant takes ~1 s of Python); editing every one of the
~190 parameters; replacing the report.

## 3. What the browser can compute exactly

This decides the interaction design.
- **Strain and scale levers need a new simulation.** Titer, production time and scale change the batch
  and the plant. These come from a precomputed grid of full model runs. Sliders step from run to run, so
  every value shown is an exact run. No interpolation between runs, except the parity contour on the map
  (marked as interpolated).
- **Prices enter linearly.** For a fixed plant, each cost line is a sum of amount x unit price. Changing a
  price, or the capital charge rate, is exact arithmetic. The location switch is a set of price changes
  (electricity, gas, sugar, water, wages, cell disposal and the construction location factor) on the same
  plant. The model's own EU base re-sizes the vessels; the panel shows how far the two differ (a check).
- **Physical-limit, best-published and industry cases** change many inputs at once. They are separate
  exact runs, shown as fixed points, not as lever settings.

## 4. Structure, top down

0. **Bar.** Protein selector. Case selector: base case, best published strain, industry benchmark,
   physical-limit best case, or "your settings". A reset button. A link to this view.
1. **The answer.** Cost per kg protein (minimum selling price, Humbird's capital charge). The price to beat
   (incumbent band, 2015-2025) and the ratio. One line of conditions: host, titer, production time, yield,
   scale, location. One line of exclusions. A small strip: the four cases on one price axis against the band.
2. **Where the money goes.** One bar in three parts: the plant (capital charge, maintenance, insurance),
   sugar, and everything else. Under it, a table: line, amount per kg, unit price (editable), $/kg.
3. **Why: the chain.** Numbered steps from titer to price (section 5). Each step: equation, substituted
   numbers, result, check mark, links to inputs.
4. **What if.** Sliders: titer, production time, scale (run grid); sugar price, capital charge rate,
   location (exact). The map of titer against time at the current scale and prices: cost by colour,
   the price-to-beat contour, infeasible cells hatched with the binding limit, published titers marked.
   Sections 1-3 and 5 follow the levers.
5. **Physical limits.** One bar per limit: O2 demand against supply in production, heat against removal
   capacity, secretion rate against its ceiling, yield against the energetic ceiling, initial fill against the
   minimum, cells against the maximum density. Shows the headroom.
6. **Mass balance.** Where the sugar goes per kg protein: growing cells, maintenance, making the protein,
   seed train, protein lost downstream. The carbon balance gap of the batch.
7. **Uncertainty.** Tornado coloured by kind of evidence (run on the industry-benchmark case, as in the report);
   Monte Carlo p10-p90 for the best-published and industry cases. Both come from `results/analyses.json`.
8. **Inputs.** Every parameter the plant reads: value, range, unit, kind of evidence, source. Searchable.
   Rows the product changes from base.yaml are marked.
9. **Reproduce.** The one-line Python call that gives the current view's numbers.

Sections 0-3 are open. Sections 4-9 open on demand.

## 5. The chain (section 3 of the page)

The model's price, as eleven steps. Symbols as on the page.

| # | Step | Equation |
|---|---|---|
| 1 | Protein made per batch | P = titer x broth at harvest |
| 2 | Protein sold per batch | S = P x R, R = product of the step recoveries |
| 3 | Batch cycle | c = growth + production + turnaround |
| 4 | Fermenter output | S / (c x V), kg per m3 of vessel per hour |
| 5 | Batches per year | n = annual output / S |
| 6 | Fermenters needed | N = n x c / operating hours; whole vessels bought |
| 7 | Fermenter purchase cost | ceil(N) x price of one vessel |
| 8 | Plant investment | TCI = equipment x installation, plus buildings, engineering and fees, x cost index x location |
| 9 | Plant cost per kg | TCI x (capital charge + maintenance + insurance) / annual output |
| 10 | Sugar per kg | glucose per kg x glucose price |
| 11 | Price | plant + sugar + everything else |

Steps 1-7 and 9-11 are arithmetic the page redoes. Step 8 is a sum of the capital table, which the page
also redoes. The fermentation simulation (growth time, broth volume, glucose use) is the one model output
the page takes as given; section 6 checks its sugar and carbon balance.

**Pablo, check:** the capital charge factor, CCF = r (1+r)^n / ((1+r)^n - 1) with r = 7.5% and n = 10 years,
is 0.1457 per year. The page shows this arithmetic too.

## 6. How the panel's data are made

- `src/pftea/plant.py` now builds each operating cost line from terms (amount x unit price), and the
  totals are summed from these terms, so the ledger and the price cannot disagree. The base results are
  unchanged (a test compares them with `results/analyses.json`).
- `src/pftea/chain.py` turns one plant run into the panel's record: the ledger, the chain, the limits
  and the balances. Its tests redo each step's arithmetic.
- `scripts/panel_data.py` runs the grid (titer x production time x scale, per protein) and the cases, and
  writes `results/panel_data.json`.
- `scripts/build_panel.py` writes `docs/panel.html` with the data inlined.

## 7. Choices to review

- The grid's titer axis (1-100 g/L) and time axis (24-168 h) are common to all proteins, plus each
  protein's base values. Scale steps are 0.1x, 0.3x, 1x, 3x and 10x the protein's base plant.
- Titer and time changes keep the base plant's vessel size, as the model's scenarios do; scale changes
  re-size it (the model's convention, base.yaml `fermenter.sizing`).
- The location switch keeps the US plant design and changes prices. The model's own EU base re-sizes.
  The panel shows the difference.
- The old explorer (`docs/explorer.html`) is kept until Pablo decides to replace it.

## 8. What the page checks, and what it cannot

Checked live on every view: the eleven steps against the model's numbers; the ledger at the model's prices
against the model's price; the sugar uses against the simulator's total (about 1% apart by design); the
batch's carbon balance; the location switch against the model's own EU base; the physical-limit case rebuilt
from its stored optimum. `tests/test_panel.py` checks the same identities in Python.

Not checked by the page: the fermentation simulation itself (growth time, glucose, O2, heat). The page takes
these as model outputs. They are checked by `tests/test_model.py` (element and carbon balances, the Intelligen
inversion) and by the calibration anchors (`docs/VALIDATION.md`).

## 9. Second version (2026-11-03): lessons from the cultivated-meat page

After a side-by-side comparison with `PabloAMC/Cultivated_meat`'s `interactive.html`:
- **All seven proteins at a glance** opens the page: five findings, computed from the stored cases, and one row per
  protein with its cases against its own price to beat. The findings do not follow the levers.
- **The price in one line:** four boxes in the answer (titer, output per m3 of fermenter, fermenters and plant
  cost, price), each linked to its step in the chain.
- **Checks against reality:** the calibration anchors (`docs/VALIDATION.md`), each labelled a reality check
  (market price or real plant) or a consistency check (another model), with MATCHES, AGREES or DIFFERS. The
  tolerances are the anchors' own (`data/calibration/*.yaml`).
- **The kind of evidence beside each input:** a small tag on every lever and every source link.
- **The levers sit right below the answer,** and the header shows the live price on wide screens.
- The page title is the question: "Precision fermentation: what does each protein cost to make?"

## 10. Third version (2026-11-04): presented for a newcomer

Pablo's review: the page assumed too much knowledge and used abbreviations (LF, BLG). It did not centre on the
numbers a newcomer understands and cares about. The cultivated-meat page does this better. The presentation
was rethought around a newcomer's questions, in this order:
1. **Is it cheaper than the animal version?** The headline unit is now "times the animal price": the cost
   divided by the top of the 2015-2025 price range of the same protein from cows or hens. The title asks the
   question. One paragraph says what precision fermentation is. Five findings ("The short answer") follow, then
   one chart of every protein's cost as a multiple of its animal price, with a line at 1×.
2. **Why does it cost that?** For the chosen protein: four tiles (cost, times the animal price, protein per
   litre with the amount needed to match, plant cost). Then four plain steps: one tank and one batch, the
   plant, cost per kg, against the animal version. The 11 checked steps stay, at the end.
3. **What would make it cheaper?** The map of protein per litre against hours, coloured by multiple of the
   animal price.
4. **Where the money goes; how sure; does the model get known things right?** The same content as before, in
   plain words. The reality checks open with a count of tests passed.
5. **Check the model in detail:** the 11 steps, physical limits, sugar balance, inputs and reproduction, closed.

The controls moved to a side panel, as on the cultivated-meat page, with plain names ("protein per litre of
broth", not "titer"). The scenarios became starting points: today's published designs, best strain in a
published paper, companies' own figures, best case. Proteins carry their full name and an everyday name
everywhere ("lactoferrin, rare milk protein"). Abbreviations inside model labels are spelled out on display.
The display names live in `scripts/panel_data.py` (`DISPLAY`); `scripts/build_panel.py` applies them, so a
wording change does not need the grid rerun. The numbers and checks are unchanged.
