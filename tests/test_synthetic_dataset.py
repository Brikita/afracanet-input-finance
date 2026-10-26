import csv
import json
import shutil
import sqlite3
from datetime import date

import pytest

from scripts.synthetic.generator import build_database, generate, validate_database

AS_OF = date(2026, 10, 26)


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    output = tmp_path_factory.mktemp("synthetic") / "pack"
    generate(output, farmers=100)
    return output


def test_graph_and_relational_exports_are_the_same_labelled_world(dataset):
    manifest = json.loads((dataset / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source_kind"] == "synthetic_replay"
    assert manifest["provider_calls"] == 0
    assert not manifest["loan_model_training_allowed"]
    assert not manifest["contains_real_financial_records"]
    nodes = {
        row["id:ID"]: row
        for row in csv.DictReader((dataset / "graph-nodes.csv").open(encoding="utf-8"))
    }
    edges = list(
        csv.DictReader((dataset / "graph-relationships.csv").open(encoding="utf-8"))
    )
    ledger = list(csv.DictReader((dataset / "ledger.csv").open(encoding="utf-8")))
    assert len(nodes) == manifest["counts"]["entities"]
    assert len(edges) == manifest["counts"]["relationships"]
    assert len(ledger) == manifest["counts"]["ledger"]
    assert all(
        edge[":START_ID"] in nodes and edge[":END_ID"] in nodes for edge in edges
    )
    assert all(
        row["id"] in nodes
        and json.loads(nodes[row["id"]]["properties:string"])["amount_minor"]
        == int(row["amount_minor"])
        for row in ledger
    )
    with sqlite3.connect(dataset / "scenario.sqlite") as conn:
        assert {
            row[0] for row in conn.execute("SELECT distinct status FROM input_orders")
        } == {
            "REQUESTED",
            "APPROVED",
            "INVOICING",
            "AWAITING_PAYMENT",
            "PAYMENT_REVIEW",
            "READY_FOR_COLLECTION",
            "COLLECTED",
            "CANCELLED",
        }
        assert (
            conn.execute(
                "SELECT count(*) FROM loans WHERE outstanding_minor > 0"
            ).fetchone()[0]
            > 0
        )
        assert (
            conn.execute(
                "SELECT count(*) FROM loans WHERE outstanding_minor = 0"
            ).fetchone()[0]
            > 0
        )
        assert (
            conn.execute(
                "SELECT count(*) FROM installments WHERE paid_on > due_on"
            ).fetchone()[0]
            > 0
        )


def test_reproduction_changes_neither_ids_nor_financial_history(tmp_path):
    first, second = tmp_path / "one", tmp_path / "two"
    generate(first, farmers=8)
    generate(second, farmers=8)
    for filename in (
        "graph-nodes.csv",
        "graph-relationships.csv",
        "ledger.csv",
        "loans.csv",
        "installments.csv",
        "input_orders.csv",
    ):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()
    with pytest.raises(FileExistsError):
        generate(first, farmers=8)


@pytest.mark.parametrize(
    "corruption,expected",
    [
        (
            "UPDATE ledger SET amount_minor=amount_minor+1 WHERE kind='loan_repayment'",
            "loan repayment mismatch",
        ),
        ("UPDATE ledger SET occurred_on='2099-01-01'", "future financial event"),
        (
            "UPDATE entities SET tenant_id='OTHER' WHERE kind='Farmer'",
            "cross-tenant relationship",
        ),
        ("DELETE FROM entities WHERE kind='LedgerEvent'", "Broken entity"),
        ("UPDATE allocations SET reserved_minor=0", "allocation reservation mismatch"),
    ],
)
def test_validation_rejects_broken_evidence_and_accounting(
    dataset, tmp_path, corruption, expected
):
    broken = tmp_path / "broken.sqlite"
    shutil.copyfile(dataset / "scenario.sqlite", broken)
    with sqlite3.connect(broken) as conn:
        conn.execute(corruption)
    with pytest.raises(ValueError, match=expected):
        validate_database(broken, AS_OF)


def test_large_pack_configuration_rejects_unbounded_parameters(tmp_path):
    with pytest.raises(ValueError):
        build_database(tmp_path / "bad.sqlite", farmers=2_000_000)
    assert not (tmp_path / "bad.sqlite").exists()
