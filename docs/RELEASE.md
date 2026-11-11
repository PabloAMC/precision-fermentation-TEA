# Release (Phase G)

Status (2026-11-11): Pablo has decided to make the work public. Licences are confirmed (below).
The page, report, memo and preprint state that the views are the author's own and not the
European Commission's. Pablo wants the commit author emails hidden in the public history, which
decides how step 2 is done (see "Hiding the commit emails"). Posting the preprint still needs his
go-ahead.

Before that (2026-10-30): v4.1 was on `main` and the release files were ready, with the
repository private.

## Checked

2026-10-30, on `main` (v4.1):
- The 195 tests pass.
- The report, memo and preprint recompile from `results/analyses.json` to the same text as the
  committed PDFs.
- Not redone since 2026-09-27: a fresh-clone install and the history scan below. Redo both
  before step 2.

2026-09-27, on the `audit-fixes` branch (v2, since merged):
- A fresh clone installed with the README commands and passed the tests (55 at the time).
- The report compiled from that clone to the same text as the committed PDF.
- The git history held no third-party files except Humbird's SI workbook. It is CC BY (Europe
  PMC, PMC8362201) and is redistributed unmodified with attribution
  (`references/papers/NOTICE.md`). Papers, patents and text dumps were never committed.
- The history contained no keys or personal paths (the USDA URLs use the public `DEMO_KEY`).
- The pre-registered priors are scored (report section 7).

## Decisions for Pablo

1. **Licences.** Confirmed 2026-11-11: MIT for code and CC BY 4.0 for data, text and figures
   (`LICENSE`, `LICENSE-DATA.md`).
2. **Authorship and AI disclosure.** Proposed: sole author, with the report's existing statement
   that the model and text were built with an AI assistant under the author's direction.
3. **Timing.** Release before or after the human review (Phase F)? Recommendation: after at
   least one human reviewer has answered. The fermentation assumptions (the product yield and
   the minimum starting fill) have been checked least and move the headline numbers most.
4. **Venue.** engrXiv, as planned (Humbird's report is there too).

## Hiding the commit emails (done 2026-11-11)

Pablo chose to rewrite this repository in place, then rename it `precision-fermentation-tea`.
- `git filter-repo --mailmap` mapped both of his Gmail addresses to his GitHub noreply address
  (`20182937+PabloAMC@users.noreply.github.com`) in all 16 branches; all were force-pushed with
  leases on their old commits. A fresh clone holds no Gmail address in any commit, message or file.
- GitHub keeps each pull request's original commits (`refs/pull/1-12/head`). These still carry the
  old addresses and cannot be removed by a push. Before or right after going public, ask GitHub
  Support to remove them (support.github.com, "Removing sensitive data": list the 12 PR refs and
  ask them to purge cached views and unreachable commits).
- Other clones made before 2026-11-11 hold the old history: re-clone them rather than pull.
- For future commits: GitHub Settings, Emails, "Keep my email addresses private" and "Block command
  line pushes that expose my email"; set `git config user.email` to the noreply address.

## Steps once approved

Claude can do steps 1–2 on request. Steps 3–5 need Pablo's accounts.

1. Redo the fresh-clone install and the history scan on `main`, then tag `v0.4.1` (the version in
   `CITATION.cff`).
2. Make the repository public:
   `gh repo edit PabloAMC/precision-fermentation-tea --visibility public --accept-visibility-change-consequences`.
3. Optional: archive the tag on Zenodo for a DOI (GitHub integration).
4. Submit `report/pf_tea_report.pdf` (or the short `report/preprint.pdf`) to engrXiv with:
   - the title;
   - the abstract (from the report's Summary);
   - keywords: precision fermentation, techno-economic analysis, β-lactoglobulin, α-lactalbumin,
     ovalbumin, ovomucoid, β-casein, lactoferrin, serum albumin, *Komagataella phaffii* (as in
     `CITATION.cff`);
   - licence CC BY 4.0;
   - the repository link.
5. Submit to GFI's fermentation TEA database (gfi.org/fermentation-tea, 'Submit a TEA'; an Airtable
   form whose DOI/URL field is required, so after step 2 or 4). Every field is drafted in
   `docs/GFI_SUBMISSION.md` (regenerate with `scripts/gfi_submission.py`); set `date-released` in
   `CITATION.cff` on release day.
6. Share the explorer and the memo. For the explorer, use the artifact link, or GitHub Pages
   serving `docs/explorer.html`.
