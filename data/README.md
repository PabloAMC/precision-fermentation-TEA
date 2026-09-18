# data/

## titers.csv — every public titer/yield/purity data point
One row per reported number. Columns:
- product: blg | ova | leghemoglobin | lactoferrin | casein | other
- host: organism, e.g. "K. phaffii", "T. reesei"
- titer_g_per_L, yield_g_per_g (g protein / g sugar), purity (fraction), scale_L
- mode: shake | batch | fed-batch | unknown
- source_key: key in references/INDEX.md
- quote: verbatim text (<=30 words) the number is taken from
- locator: abstract / Table N / Example N / page
- source_seen: abstract | fulltext  (what was actually read)
- evidence_grade: A peer-reviewed measurement · B patent example (best run, upper bound) ·
  C company claim / survey self-report · D analogy from another protein · E guess
- verified: yes | no  — yes once the quote has been checked against the full text on
  disk (not just an abstract). Nothing enters the base case with "no".

## assumptions.yaml — every model parameter
Fields: value, low, high, unit, source, note. `source` must be a citation key
or "guess". Add `grade: A-E` (same scale as above) to every block in Phase 1.
