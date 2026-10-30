"""Seed current review cohorts without authorizing a single live allocation."""

import argparse
import hashlib
import json
import secrets
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import insert, select


def load(overlay):
    manifest = json.loads((overlay / "report.json").read_text())
    entry = next(row for row in manifest["files"] if row["file"] == "workflow.sqlite")
    if (
        hashlib.sha256((overlay / "workflow.sqlite").read_bytes()).hexdigest()
        != entry["sha256"]
    ):
        raise ValueError("Workflow cohort checksum mismatch.")
    from Backend import identity, store

    store.initialize()
    with store.engine.begin() as target:
        if target.execute(select(store.applications.c.id).limit(1)).first():
            raise ValueError("Credit store is not empty; choose a fresh database.")
        with sqlite3.connect(overlay / "workflow.sqlite") as source:
            rows = source.execute("SELECT * FROM review_cases")
            for identifier, farmer, lender, status, created, provenance in rows:
                target.execute(
                    insert(store.applications).values(
                        id=identifier,
                        farmer_id=farmer,
                        input_farmer_id=farmer,
                        lender_id=lender,
                        status=status,
                        provenance=provenance,
                        created_at=created,
                        request_id=identifier,
                    )
                )
                if status != "PENDING":
                    reference = "REPLAY-DECISION-" + farmer
                    target.execute(
                        insert(store.decisions).values(
                            id=reference,
                            application_id=identifier,
                            lender_id=lender,
                            officer_id="synthetic_replay_author",
                            decision=status,
                            terms=json.dumps(
                                {
                                    "basis": "authored_workflow_cohort",
                                    "authority": "none",
                                }
                            ),
                            reason="Authored synthetic review outcome; no live lender authorization or delivery.",
                            created_at=created,
                        )
                    )
    accounts = []
    for index in range(4):
        account = {
            "officer_id": f"officer-synthetic-{index:03d}",
            "lender_id": f"SYN-LENDER-{index:03d}",
            "password": secrets.token_urlsafe(24),
        }
        identity.provision(
            account["officer_id"], account["lender_id"], account["password"]
        )
        accounts.append(account)
    from Backend.store import ROOT

    (ROOT / "data/local-officer-accounts.json").write_text(
        json.dumps(accounts, indent=2)
    )
    return {
        "applications": 10000,
        "individual_local_officers": 4,
        "queued_deliveries": 0,
        "active_authorizations": 0,
        "source_kind": "synthetic_replay",
    }


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("overlay", type=Path)
    print(json.dumps(load(parser.parse_args().overlay)))
