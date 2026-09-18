Read PLAN.md and README.md first. We are in Phase 1 (data table). Phase 0 reading runs in parallel.
Rules:
- Every number goes in data/assumptions.yaml with a source. Never hardcode.
- Equations go in module docstrings before code.
- Run pytest before and after every change.
- Do not add dependencies beyond pyproject.toml without asking.
- Do not invent parameter values. If a value is unknown, mark source: guess and tell me.
- Keep diffs small. One module or one phase step per turn.