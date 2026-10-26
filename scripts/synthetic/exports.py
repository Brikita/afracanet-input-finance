"""Streaming CSV exports and hashes for graph and relational representations."""

import csv
import hashlib
import sqlite3


def export_files(path, output):
    with sqlite3.connect(path) as conn:
        exports = {
            "graph-nodes.csv": (
                (
                    "id:ID",
                    "kind:LABEL",
                    "tenant_id:string",
                    "properties:string",
                    "source_kind:string",
                ),
                "SELECT * FROM entities ORDER BY rowid",
            ),
            "graph-relationships.csv": (
                (
                    ":START_ID",
                    ":END_ID",
                    ":TYPE",
                    "occurred_on:string",
                    "properties:string",
                ),
                "SELECT source_id,target_id,kind,occurred_on,properties FROM relationships ORDER BY id",
            ),
        }
        for table in ("loans", "installments", "ledger", "allocations", "input_orders"):
            cursor = conn.execute(f"SELECT * FROM {table}")
            exports[f"{table}.csv"] = (
                tuple(item[0] for item in cursor.description),
                f"SELECT * FROM {table}",
            )
        for name, (header, query) in exports.items():
            with (output / name).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(header)
                writer.writerows(conn.execute(query))


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
