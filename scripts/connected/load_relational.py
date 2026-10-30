"""Stream the replay registry into an empty, isolated PostgreSQL schema."""

import hashlib
import json
import sqlite3
import time
from pathlib import Path

import psycopg
from psycopg import sql

TABLES = (
    "entities",
    "relationships",
    "loans",
    "installments",
    "ledger",
    "allocations",
    "input_orders",
)


def verify_pack(pack):
    manifest = json.loads((pack / "manifest.json").read_text())
    if (
        manifest.get("source_kind") != "synthetic_replay"
        or manifest.get("contains_real_people") is not False
    ):
        raise ValueError("Only explicitly synthetic packs are accepted by this loader.")
    for item in manifest["files"]:
        path = pack / item["file"]
        if path.parent.resolve() != pack.resolve():
            raise ValueError("Manifest path leaves dataset directory.")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != item["sha256"] or path.stat().st_size != item["bytes"]:
            raise ValueError("Dataset checksum mismatch: " + item["file"])
    return manifest


def verify_overlay(pack, overlay):
    report = json.loads((overlay / "report.json").read_text())
    fingerprint = hashlib.sha256((pack / "manifest.json").read_bytes()).hexdigest()
    if report.get("base_manifest_sha256") != fingerprint:
        raise ValueError("Overlay belongs to a different historical pack.")
    expected = {"workflow.sqlite", "workflow-nodes.csv", "workflow-relationships.csv"}
    if {item["file"] for item in report["files"]} != expected:
        raise ValueError("Unexpected overlay file set.")
    for item in report["files"]:
        path = overlay / item["file"]
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if path.stat().st_size != item["bytes"] or actual != item["sha256"]:
            raise ValueError("Overlay checksum mismatch: " + item["file"])
    return report


def load(pack, overlay, url):
    started = time.perf_counter()
    manifest = verify_pack(pack)
    verify_overlay(pack, overlay)
    fingerprint = hashlib.sha256((pack / "manifest.json").read_bytes()).hexdigest()
    with psycopg.connect(url) as target:
        if target.execute("SELECT to_regclass('replay.entities')").fetchone()[0]:
            raise ValueError("Replay schema already exists; choose a fresh database.")
        target.execute("CREATE SCHEMA replay")
        target.execute("SET search_path TO replay")
        schema = Path(__file__).parents[1].joinpath("synthetic/schema.sql").read_text()
        schema = schema.replace("PRAGMA foreign_keys = ON;", "").replace(
            "id INTEGER PRIMARY KEY, source_id", "id BIGINT PRIMARY KEY, source_id"
        )
        target.execute(schema)
        with sqlite3.connect(
            f"file:{(pack / 'scenario.sqlite').as_posix()}?mode=ro", uri=True
        ) as source:
            counts, totals = {}, {}
            for table in TABLES:
                with target.cursor().copy(
                    sql.SQL("COPY {} FROM STDIN").format(sql.Identifier(table))
                ) as writer:
                    for row in source.execute(f"SELECT * FROM {table}"):
                        writer.write_row(row)
                counts[table] = target.execute(
                    sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
                ).fetchone()[0]
                if counts[table] != manifest["counts"][table]:
                    raise ValueError("Row count mismatch: " + table)
            for table, columns in {
                "loans": ("principal_minor", "repaid_minor", "outstanding_minor"),
                "ledger": ("amount_minor",),
                "allocations": ("limit_minor", "reserved_minor", "spent_minor"),
                "input_orders": ("amount_minor", "replay_paid_minor"),
            }.items():
                sums = ",".join(f"sum({column})" for column in columns)
                expected = source.execute(f"SELECT {sums} FROM {table}").fetchone()
                actual = target.execute(
                    sql.SQL(f"SELECT {sums} FROM {table}")
                ).fetchone()
                if expected != actual:
                    raise ValueError("Monetary totals mismatch: " + table)
                totals[table] = dict(zip(columns, actual))
        target.execute("CREATE INDEX entity_kind_tenant ON entities(kind,tenant_id)")
        target.execute("CREATE INDEX relationship_source ON relationships(source_id)")
        target.execute("CREATE INDEX relationship_target ON relationships(target_id)")
        target.execute("CREATE INDEX ledger_farmer ON ledger(farmer_id)")
        target.execute("CREATE INDEX loan_farmer ON loans(farmer_id)")
        target.execute(
            "CREATE TABLE dataset_manifest(fingerprint TEXT PRIMARY KEY, manifest TEXT NOT NULL)"
        )
        target.execute(
            "INSERT INTO dataset_manifest VALUES (%s,%s)",
            (fingerprint, json.dumps(manifest)),
        )
        target.execute(
            "CREATE TABLE review_cases(id TEXT PRIMARY KEY,farmer_id TEXT REFERENCES entities(id),lender_id TEXT,status TEXT,created_at TEXT,provenance TEXT)"
        )
        target.execute(
            "CREATE TABLE inventory(product_id TEXT PRIMARY KEY REFERENCES entities(id),supplier_id TEXT REFERENCES entities(id),tenant_id TEXT,opening_units INTEGER,stock_units INTEGER,reserved_units INTEGER,fulfilled_units INTEGER,CHECK(opening_units=stock_units+fulfilled_units),CHECK(stock_units>=reserved_units AND reserved_units>=0))"
        )
        with sqlite3.connect(overlay / "workflow.sqlite") as source:
            for table in ("review_cases", "inventory"):
                with target.cursor().copy(
                    sql.SQL("COPY {} FROM STDIN").format(sql.Identifier(table))
                ) as writer:
                    for row in source.execute(f"SELECT * FROM {table}"):
                        writer.write_row(row)
                counts[table] = target.execute(
                    sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(table))
                ).fetchone()[0]
        target.execute("ANALYZE")
    return {
        "counts": counts,
        "totals_minor_units": totals,
        "manifest_sha256": fingerprint,
        "seconds": round(time.perf_counter() - started, 2),
        "source_kind": "synthetic_replay",
    }
