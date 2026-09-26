# data/evidence/ — sourced parameter candidates (Phase B)

Research output, one YAML per topic. The model never reads these files directly. A value
moves into data/assumptions.yaml (or a host/product/calibration file) only after its
quote has been checked, keeping the same source fields.

Each entry:

```yaml
- key: otr_max_production_scale        # snake_case, unique within the file
  value: 150                            # central value as stated by the source (no conversion unless noted)
  low: 100                              # optional range stated or implied by the source
  high: 250
  unit: mmol/L/h
  grade: A                              # see below
  source: "Garcia-Ochoa F, Gomez E. Biotechnol Adv 27:153-176 (2009)"
  doi_or_url: 10.1016/j.biotechadv.2008.10.006
  locator: "Table 3, p.160"             # page/table/section; 'abstract' if only the abstract was read
  quote: "verbatim text, <=40 words, that contains the number"
  read: fulltext | abstract | html      # what was actually read
  note: "context: organism, scale, conditions; conversions made"
```

Grades for engineering and economic parameters:
- A: measured or reported data in a peer-reviewed paper, a standard engineering
  textbook or handbook, or official statistics.
- B: a design-basis assumption in a credible third-party TEA or design report (NREL,
  Intelligen, Humbird), or a patent example.
- C: a company claim, vendor marketing figure or industry survey.
- D: an analogy from a different organism, product or scale.
- E: a guess or rule of thumb without a traceable source.

No quote means the entry is not usable: write `quote: null` and explain in `note`.
