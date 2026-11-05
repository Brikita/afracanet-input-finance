"""Import a verified compact synthetic fixture into a fresh private graph only.

One graph transaction commits all data and its marker. Retry preserves a completed
import; existing unrelated graphs are rejected and never cleared or overwritten.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def grouped(path, kind_column):
    result = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            kind = row[kind_column]
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", kind):
                raise ValueError("Unexpected graph label or relationship type.")
            result[kind].append(row)
    return result


def seed(fixture):
    from scripts.connected.load_relational import verify_overlay, verify_pack

    pack, overlay = fixture / "pack", fixture / "overlay"
    verify_pack(pack)
    verify_overlay(pack, overlay)
    manifest = json.loads((pack / "manifest.json").read_text())
    if (
        manifest.get("source_kind") != "synthetic_replay"
        or manifest.get("farmers") != 32
    ):
        raise ValueError("Only the compact synthetic fixture is accepted.")
    fingerprint = hashlib.sha256((pack / "manifest.json").read_bytes()).hexdigest()
    nodes, edges = defaultdict(list), defaultdict(list)
    for path in (pack / "graph-nodes.csv", overlay / "workflow-nodes.csv"):
        for kind, rows in grouped(path, "kind:LABEL").items():
            nodes[kind].extend(rows)
    for path in (
        pack / "graph-relationships.csv",
        overlay / "workflow-relationships.csv",
    ):
        for kind, rows in grouped(path, ":TYPE").items():
            edges[kind].extend(rows)
    with (
        GraphDatabase.driver(
            os.environ["WORKFLOW_NEO4J_URI"],
            auth=(
                os.environ["WORKFLOW_NEO4J_USER"],
                os.environ["WORKFLOW_NEO4J_PASSWORD"],
            ),
            connection_timeout=10,
        ) as driver,
        driver.session(
            database=os.getenv("WORKFLOW_NEO4J_DATABASE", "neo4j")
        ) as session,
    ):
        session.run(
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE"
        ).consume()
        session.run(
            "CREATE CONSTRAINT hosted_fixture_id IF NOT EXISTS FOR (n:HostedFixture) REQUIRE n.id IS UNIQUE"
        ).consume()
        session.run(
            "CREATE INDEX entity_tenant IF NOT EXISTS FOR (n:Entity) ON (n.tenant_id)"
        ).consume()
        return session.execute_write(import_transaction, fingerprint, nodes, edges)


def import_transaction(tx, fingerprint, nodes, edges):
    # The unique singleton also serializes two simultaneous initialization attempts.
    tx.run("MERGE (m:HostedFixture {id:'compact-v1'}) SET m.locked=true").consume()
    marker = tx.run(
        "MATCH (m:HostedFixture {id:'compact-v1'}) RETURN m.fingerprint AS fingerprint"
    ).single()["fingerprint"]
    if marker is not None:
        if marker != fingerprint:
            raise ValueError(
                "Graph belongs to another fixture; explicit migration required."
            )
        return {"preserved": True, "manifest_sha256": fingerprint}
    count = tx.run(
        "MATCH (n) WHERE NOT n:HostedFixture RETURN count(n) AS count"
    ).single()["count"]
    if count:
        raise ValueError("Graph is not empty. No existing records were changed.")
    for kind, rows in nodes.items():
        data = [
            {
                "id": row["id:ID"],
                "tenant_id": row["tenant_id:string"],
                "properties": row["properties:string"],
                "source_kind": row["source_kind:string"],
            }
            for row in rows
        ]
        tx.run(
            f"UNWIND $rows AS row CREATE (n:Entity:`{kind}`) SET n=row", rows=data
        ).consume()
    for kind, rows in edges.items():
        data = [
            {
                "source": row[":START_ID"],
                "target": row[":END_ID"],
                "occurred_on": row["occurred_on:string"],
                "properties": row["properties:string"],
            }
            for row in rows
        ]
        tx.run(
            f"UNWIND $rows AS row MATCH (a:Entity {{id:row.source}}),(b:Entity {{id:row.target}}) CREATE (a)-[r:`{kind}`]->(b) SET r.occurred_on=row.occurred_on,r.properties=row.properties",
            rows=data,
        ).consume()
    total_nodes = tx.run("MATCH (n:Entity) RETURN count(n) AS count").single()["count"]
    total_edges = tx.run(
        "MATCH (:Entity)-[r]->(:Entity) RETURN count(r) AS count"
    ).single()["count"]
    if (total_nodes, total_edges) != (
        sum(map(len, nodes.values())),
        sum(map(len, edges.values())),
    ):
        raise ValueError(
            "Graph counts differ from the verified fixture; import rolled back."
        )
    tx.run(
        "MATCH (m:HostedFixture {id:'compact-v1'}) SET m.fingerprint=$fingerprint REMOVE m.locked",
        fingerprint=fingerprint,
    ).consume()
    return {
        "nodes": total_nodes,
        "relationships": total_edges,
        "preserved": False,
        "source_kind": "synthetic_replay",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    print(json.dumps(seed(parser.parse_args().fixture.resolve())))
