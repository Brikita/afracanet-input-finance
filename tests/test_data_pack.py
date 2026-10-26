from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path

import pytest

from scripts.build_replay_dataset import build, validate
from scripts.fetch_public_weather import validate_weather

ROOT = Path(__file__).resolve().parents[1]


def test_replay_is_deterministic_reconciled_and_explicitly_not_training_evidence():
    pack = build()
    assert pack == build()
    counts = validate(pack)
    assert counts["farmers"] == 30 and counts["loans"] > 0 and counts["ledger_events"] > 100
    assert not pack["manifest"]["loan_model_training_allowed"]
    assert any(loan["outstanding_minor"] > 0 for loan in pack["loans"])
    assert any(loan["outstanding_minor"] == 0 for loan in pack["loans"])


@pytest.mark.parametrize("change", ["relabel-real", "broken-loan-total", "wrong-farmer", "future-event"])
def test_replay_rejects_false_provenance_and_inconsistent_financial_events(change):
    pack = deepcopy(build())
    if change == "relabel-real": pack["manifest"]["contains_real_financial_records"] = True
    if change == "broken-loan-total": pack["loans"][0]["repaid_minor"] += 1
    if change == "wrong-farmer": pack["ledger"][0]["farmer_id"] = "missing-farmer"
    if change == "future-event": pack["ledger"][0]["date"] = "2099-01-01"
    with pytest.raises(ValueError):
        validate(pack)


def test_weather_gaps_are_not_replaced_with_fake_values():
    start = end = date(2026, 9, 1)
    with pytest.raises(ValueError):
        validate_weather({"daily": {"time": ["2026-09-01"], "precipitation_sum": [None]}}, start, end)


def test_committed_public_snapshots_match_the_recorded_hash_and_date_range():
    path = ROOT / "datasets/public/weather"
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_kind"] == "public_weather_reanalysis"
    for snapshot in manifest["snapshots"]:
        data = (path / snapshot["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == snapshot["sha256"]
        assert validate_weather(json.loads(data), date.fromisoformat(manifest["start_date"]), date.fromisoformat(manifest["end_date"])) == snapshot["daily_records"]
