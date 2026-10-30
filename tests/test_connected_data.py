import sqlite3

import pytest
from sqlalchemy import func, select

from backend import db
from scripts.connected.cohorts import build_overlay
from scripts.connected.load_execution import load_execution
from scripts.connected.load_relational import verify_overlay, verify_pack
from scripts.synthetic.generator import generate


@pytest.fixture
def pack(tmp_path):
    folder = tmp_path / "pack"
    generate(folder, farmers=32, months=12)
    return folder


def test_review_cohorts_and_inventory_are_reconciled_and_checksums_recorded(
    pack, tmp_path
):
    output = tmp_path / "overlay"
    report = build_overlay(pack, output)
    assert report["cases"] == {"PENDING": 16, "REJECTED": 8, "REPLAY_APPROVED": 8}
    assert {row["file"] for row in report["files"]} == {
        "workflow.sqlite",
        "workflow-nodes.csv",
        "workflow-relationships.csv",
    }
    assert verify_overlay(pack, output)["cases"] == report["cases"]
    with sqlite3.connect(output / "workflow.sqlite") as conn:
        assert (
            conn.execute(
                "SELECT count(*) FROM inventory WHERE stock_units<reserved_units OR opening_units!=stock_units+fulfilled_units"
            ).fetchone()[0]
            == 0
        )
        assert (
            conn.execute(
                "SELECT count(*) FROM review_cases WHERE provenance!='synthetic'"
            ).fetchone()[0]
            == 0
        )
    with pytest.raises(FileExistsError):
        build_overlay(pack, output)
    with (output / "workflow-nodes.csv").open("a") as stream:
        stream.write("tampered\n")
    with pytest.raises(ValueError, match="Overlay checksum mismatch"):
        verify_overlay(pack, output)


def test_pack_loader_rejects_tampered_data(pack):
    assert verify_pack(pack)["farmers"] == 32
    with (pack / "ledger.csv").open("a") as stream:
        stream.write("tampered\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_pack(pack)


def test_execution_import_never_activates_replay_credit_or_payments(
    pack, tmp_path, monkeypatch
):
    engine = db.build_engine(f"sqlite:///{tmp_path / 'execution.db'}")
    monkeypatch.setattr(db, "engine", engine)
    try:
        report = load_execution(pack, tmp_path)
        assert report["farmers"] == 32
        with engine.connect() as conn:
            assert (
                conn.execute(select(func.sum(db.farmers.c.limit_cents))).scalar_one()
                == 0
            )
            assert (
                conn.execute(select(func.count()).select_from(db.orders)).scalar_one()
                == 0
            )
            assert (
                conn.execute(
                    select(func.count()).select_from(db.approval_handoffs)
                ).scalar_one()
                == 0
            )
            assert (
                conn.execute(
                    select(func.count()).select_from(db.approval_mappings)
                ).scalar_one()
                == 32
            )
            assert all(
                r.stock == 200 and r.reserved == 0
                for r in conn.execute(select(db.products))
            )
        with pytest.raises(ValueError, match="empty"):
            load_execution(pack, tmp_path)
    finally:
        engine.dispose()
