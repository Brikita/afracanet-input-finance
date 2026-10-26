"""Measure bounded read queries against a completed offline scenario pack."""

import argparse
import json
import sqlite3
import time
from pathlib import Path
from statistics import median


def benchmark(directory, repetitions=7):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("source_kind") != "synthetic_replay":
        raise ValueError("Expected a completed synthetic scenario pack.")
    path = (directory / "scenario.sqlite").resolve()
    queries = {
        "farmer_recent_ledger": (
            "SELECT id,kind,amount_minor,currency,occurred_on FROM ledger WHERE farmer_id=? ORDER BY occurred_on DESC LIMIT 24",
            ("farmer-synth-000001",),
        ),
        "farmer_graph_neighborhood": (
            "SELECT r.kind,e.id,e.kind FROM relationships r JOIN entities e ON e.id=r.target_id WHERE r.source_id=? LIMIT 100",
            ("farmer-synth-000001",),
        ),
        "pending_order_queue": (
            "SELECT id,farmer_id,amount_minor,currency FROM input_orders WHERE status=? LIMIT 50",
            ("REQUESTED",),
        ),
        "farmer_loans": (
            "SELECT id,principal_minor,repaid_minor,outstanding_minor FROM loans WHERE farmer_id=?",
            ("farmer-synth-000001",),
        ),
    }
    results = {}
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as conn:
        for name, (sql, params) in queries.items():
            plan = [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params)]
            measurements = []
            for _ in range(repetitions):
                started = time.perf_counter()
                rows = conn.execute(sql, params).fetchall()
                measurements.append((time.perf_counter() - started) * 1000)
            results[name] = {
                "returned_rows": len(rows),
                "median_ms": round(median(measurements), 3),
                "max_ms": round(max(measurements), 3),
                "query_plan": plan,
            }
    return {
        "source_kind": "synthetic_replay",
        "database_counts": manifest["counts"],
        "repetitions": repetitions,
        "scope": "Local SQLite read queries; operating-system cache may be warm. No Neo4j, GDS, network, concurrency, or production throughput measurement.",
        "queries": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = benchmark(args.directory)
    content = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    print(content)


if __name__ == "__main__":
    main()
