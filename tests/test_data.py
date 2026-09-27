"""Data-file integrity: every YAML parses, evidence entries share one schema, keys are unique."""
import csv
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = sorted((ROOT / "data/evidence").glob("*.yaml"))
FIELDS = {"key", "value", "unit", "grade", "source", "doi_or_url", "locator", "quote", "read", "note"}
GRADES = set("ABCDE")


@pytest.mark.parametrize("path", sorted((ROOT / "data").rglob("*.yaml")), ids=lambda q: str(q.relative_to(ROOT)))
def test_yaml_parses(path):
    yaml.safe_load(path.read_text())


@pytest.mark.parametrize("path", EVIDENCE, ids=lambda q: q.name)
def test_evidence_schema(path):
    for e in yaml.safe_load(path.read_text()):
        assert FIELDS <= set(e), (e.get("key"), FIELDS - set(e))
        assert str(e["grade"]) in GRADES, (e["key"], e["grade"])
        assert e["read"] in {"fulltext", "html", "abstract"}, (e["key"], e["read"])


def test_evidence_keys_unique():
    seen = {}
    for path in EVIDENCE:
        for e in yaml.safe_load(path.read_text()):
            assert e["key"] not in seen, f"{e['key']} in {path.name} and {seen.get(e['key'])}"
            seen[e["key"]] = path.name


def test_titers_csv():
    for r in csv.DictReader((ROOT / "data/titers.csv").open()):
        if r["titer_g_per_L"]:
            assert float(r["titer_g_per_L"]) >= 0, r["source_key"]
        assert r["evidence_grade"] in GRADES, r["source_key"]
        assert r["verified"] in {"yes", "no"}, r["source_key"]
        assert r["source_seen"] in {"fulltext", "abstract"}, r["source_key"]
