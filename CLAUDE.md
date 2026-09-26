Read PLAN.md, docs/SCOPE.md and README.md first. Working mode (2026-09-26): Claude builds the
complete v1 (phases B-G); Pablo reviews the finished product. Pablo is new to bioprocess
engineering: explain physics-first and flag every derivation he should check.
Rules:
- Every number goes in data/pf/base.yaml (or a scenario/calibration file) with a source and grade. Never hardcode.
- Equations go in module docstrings before code.
- Run pytest before and after every change.
- Do not add dependencies beyond pyproject.toml without asking.
- Do not invent parameter values. If a value is unknown, mark source: guess and tell me.
- Keep diffs reviewable: one module at a time, each with its tests.
- Never run `uv run` inside the repo without `--no-project`: it re-syncs .venv and strips the
  dev extras. Use `.venv/bin/python`.
- Numbers in docs/PRIMER.md and docs/exercises/ are for teaching (reproduced by the scripts
  next to them). Never copy them into data/pf/base.yaml.