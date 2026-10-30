"""Add current review cohorts and stock to an immutable historical replay pack."""

import csv
import hashlib
import json
import sqlite3
from pathlib import Path


def build_overlay(pack: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    database = output / "workflow.sqlite"
    if database.exists():
        raise FileExistsError(
            "Choose a new overlay directory; existing datasets are immutable."
        )
    with (
        sqlite3.connect(
            f"file:{(pack / 'scenario.sqlite').as_posix()}?mode=ro", uri=True
        ) as source,
        sqlite3.connect(database) as target,
    ):
        target.executescript("""
        CREATE TABLE review_cases(id TEXT PRIMARY KEY,farmer_id TEXT UNIQUE,lender_id TEXT,status TEXT,created_at TEXT,provenance TEXT);
        CREATE TABLE inventory(product_id TEXT PRIMARY KEY,supplier_id TEXT,tenant_id TEXT,opening_units INTEGER,stock_units INTEGER,reserved_units INTEGER,fulfilled_units INTEGER,CHECK(stock_units>=reserved_units AND reserved_units>=0),CHECK(opening_units=stock_units+fulfilled_units));
        CREATE TABLE nodes(id TEXT PRIMARY KEY,kind TEXT,tenant_id TEXT,properties TEXT,source_kind TEXT);
        CREATE TABLE edges(source_id TEXT,target_id TEXT,kind TEXT,occurred_on TEXT,properties TEXT);
        """)
        counts = {"PENDING": 0, "REJECTED": 0, "REPLAY_APPROVED": 0}
        for index, (farmer, tenant) in enumerate(
            source.execute(
                "SELECT id,tenant_id FROM entities WHERE kind='Farmer' ORDER BY id"
            )
        ):
            status = ("PENDING", "PENDING", "REJECTED", "REPLAY_APPROVED")[
                (index // 4) % 4
            ]
            case = "WORKFLOW-" + farmer
            when = "2026-10-26T10:00:00+00:00"
            counts[status] += 1
            target.execute(
                "INSERT INTO review_cases VALUES (?,?,?,?,?,?)",
                (case, farmer, tenant, status, when, "synthetic"),
            )
            target.execute(
                "INSERT INTO nodes VALUES (?,?,?,?,?)",
                (
                    case,
                    "WorkflowApplication",
                    tenant,
                    json.dumps(
                        {
                            "status": status,
                            "provenance": "synthetic_replay",
                            "authority": "authored_workflow_cohort",
                            "created_at": when,
                        }
                    ),
                    "synthetic_replay",
                ),
            )
            target.execute(
                "INSERT INTO edges VALUES (?,?,?,?,?)",
                (farmer, case, "HAS_WORKFLOW_CASE", "2026-10-26", "{}"),
            )
        reservations = {}
        fulfilled = {}
        query = """SELECT r.target_id,o.status,json_extract(r.properties,'$.quantity') FROM relationships r JOIN input_orders o ON o.id=r.source_id WHERE r.kind='CONTAINS_PRODUCT'"""
        for product, status, units in source.execute(query):
            if status in {
                "REQUESTED",
                "APPROVED",
                "INVOICING",
                "AWAITING_PAYMENT",
                "PAYMENT_REVIEW",
            }:
                reservations[product] = reservations.get(product, 0) + units
            if status in {"READY_FOR_COLLECTION", "COLLECTED"}:
                fulfilled[product] = fulfilled.get(product, 0) + units
        for product, tenant in source.execute(
            "SELECT id,tenant_id FROM entities WHERE kind='Product' ORDER BY id"
        ):
            reserved, spent = reservations.get(product, 0), fulfilled.get(product, 0)
            opening = reserved + spent + 200
            supplier = product.replace("SYN-PRODUCT-", "SYN-DEALER-").rsplit("-", 1)[0]
            target.execute(
                "INSERT INTO inventory VALUES (?,?,?,?,?,?,?)",
                (product, supplier, tenant, opening, opening - spent, reserved, spent),
            )
            identifier = "INVENTORY-" + product
            properties = {
                "opening_units": opening,
                "stock_units": opening - spent,
                "reserved_units": reserved,
                "fulfilled_units": spent,
                "basis": "authored_replay_inventory",
            }
            target.execute(
                "INSERT INTO nodes VALUES (?,?,?,?,?)",
                (
                    identifier,
                    "Inventory",
                    tenant,
                    json.dumps(properties),
                    "synthetic_replay",
                ),
            )
            target.execute(
                "INSERT INTO edges VALUES (?,?,?,?,?)",
                (supplier, identifier, "HAS_INVENTORY", "2026-10-26", "{}"),
            )
            target.execute(
                "INSERT INTO edges VALUES (?,?,?,?,?)",
                (identifier, product, "FOR_PRODUCT", "2026-10-26", "{}"),
            )
        for filename, query, header in [
            (
                "workflow-nodes.csv",
                "SELECT * FROM nodes",
                [
                    "id:ID",
                    "kind:LABEL",
                    "tenant_id:string",
                    "properties:string",
                    "source_kind:string",
                ],
            ),
            (
                "workflow-relationships.csv",
                "SELECT * FROM edges",
                [
                    ":START_ID",
                    ":END_ID",
                    ":TYPE",
                    "occurred_on:string",
                    "properties:string",
                ],
            ),
        ]:
            with (output / filename).open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(header)
                writer.writerows(target.execute(query))
        report = {
            "source_kind": "synthetic_replay",
            "cases": counts,
            "inventory_products": target.execute(
                "SELECT count(*) FROM inventory"
            ).fetchone()[0],
            "boundary": "Current review cohorts supplement historical approvals. Historical replay payments are not provider evidence. Active execution starts with zero credit and fresh stock.",
        }
    report["base_manifest_sha256"] = hashlib.sha256(
        (pack / "manifest.json").read_bytes()
    ).hexdigest()
    report["files"] = [
        {
            "file": p.name,
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in sorted(output.iterdir())
        if p.suffix in {".sqlite", ".csv"}
    ]
    (output / "report.json").write_text(json.dumps(report, indent=2))
    return report
