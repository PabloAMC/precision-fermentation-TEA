# Release (Phase G)

Status (2026-09-27): the release files are ready and nothing is public. Making the repository
public and posting the preprint both need Pablo's explicit go-ahead.

## Checked (2026-09-27)

- A fresh clone of `audit-fixes` installs with the README commands and passes the tests (55).
- The report compiles from that clone to the same text as the committed PDF.
- The git history holds no third-party files except Humbird's SI workbook. It is CC BY (Europe
  PMC, PMC8362201) and is redistributed unmodified with attribution
  (`references/papers/NOTICE.md`). Papers, patents and text dumps were never committed.
- The history contains no keys or personal paths (the USDA URLs use the public `DEMO_KEY`).
- The pre-registered priors are scored (report section 7).

## Decisions for Pablo

1. **Licences.** Proposed: MIT for code and CC BY 4.0 for data, text and figures
   (`LICENSE`, `LICENSE-DATA.md`).
2. **Authorship and AI disclosure.** Proposed: sole author, with the report's existing statement
   that the model and text were built with an AI assistant under the author's direction.
3. **Timing.** Release before or after the human review (Phase F)? Recommendation: after at
   least one human reviewer has answered. The fermentation assumptions (the product yield and
   the minimum starting fill) have been checked least and move the headline numbers most.
4. **Venue.** engrXiv, as planned (Humbird's report is there too).

## Steps once approved

Claude can do steps 1–2 on request. Steps 3–5 need Pablo's accounts.

1. Merge `audit-fixes` into `main` through a pull request, and tag `v0.2.0`.
2. Make the repository public:
   `gh repo edit PabloAMC/pf-tea --visibility public --accept-visibility-change-consequences`.
3. Optional: archive the tag on Zenodo for a DOI (GitHub integration).
4. Submit `report/pf_tea_report.pdf` to engrXiv with:
   - the title;
   - the abstract (from the report's Summary);
   - keywords: precision fermentation, techno-economic analysis, β-lactoglobulin, ovalbumin,
     *Komagataella phaffii*;
   - licence CC BY 4.0;
   - the repository link.
5. Share the explorer and the memo. For the explorer, use the artifact link, or GitHub Pages
   serving `docs/explorer.html`.
