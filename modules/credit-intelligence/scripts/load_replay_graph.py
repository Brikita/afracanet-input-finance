"""Initial offline import into a fresh local Neo4j instance; never clears a graph.

Graph queries and the graph runtime stay in the credit-intelligence module.
Requires Neo4j Community 5.26 and Java 21, with bounded memory on small laptops.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import time
from pathlib import Path


def verify(path, expected):
    with path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
            raise ValueError("Graph CSV checksum mismatch: " + path.name)


def run(pack, overlay, neo4j_home, java_home, instance):
    from dotenv import set_key
    from neo4j import GraphDatabase

    root = Path(__file__).resolve().parents[1]
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,80}", instance):
        raise ValueError("Use an instance directory name, not a path.")
    folder = root / "data" / instance
    if folder.exists():
        raise FileExistsError(
            "Choose a fresh graph instance. Existing graphs are never overwritten."
        )
    manifest = json.loads((pack / "manifest.json").read_text())
    if manifest.get("source_kind") != "synthetic_replay":
        raise ValueError("This loader only accepts labelled synthetic packs.")
    for item in manifest["files"]:
        if item["file"] in {"graph-nodes.csv", "graph-relationships.csv"}:
            verify(pack / item["file"], item["sha256"])
    overlay_report = json.loads((overlay / "report.json").read_text())
    if (
        overlay_report["base_manifest_sha256"]
        != hashlib.sha256((pack / "manifest.json").read_bytes()).hexdigest()
    ):
        raise ValueError("Workflow overlay belongs to a different base pack.")
    for item in overlay_report["files"]:
        if item["file"] not in {
            "workflow.sqlite",
            "workflow-nodes.csv",
            "workflow-relationships.csv",
        }:
            raise ValueError("Unexpected overlay filename.")
        verify(overlay / item["file"], item["sha256"])
    conf = folder / "conf"
    conf.mkdir(parents=True)
    for name in ("store", "logs", "run", "transactions"):
        (folder / name).mkdir()
    (conf / "neo4j.conf").write_text(
        "\n".join(
            [
                f"server.directories.data={(folder / 'store').as_posix()}",
                f"server.directories.logs={(folder / 'logs').as_posix()}",
                f"server.directories.run={(folder / 'run').as_posix()}",
                f"server.directories.transaction.logs.root={(folder / 'transactions').as_posix()}",
                "server.memory.heap.initial_size=256m",
                "server.memory.heap.max_size=512m",
                "server.memory.pagecache.size=128m",
                "server.default_listen_address=127.0.0.1",
                "server.bolt.listen_address=:17687",
                "server.http.listen_address=:17474",
                "server.bolt.advertised_address=127.0.0.1:17687",
                "server.http.advertised_address=127.0.0.1:17474",
                "server.https.enabled=false",
                "dbms.security.auth_enabled=true",
                "dbms.usage_report.enabled=false",
            ]
        )
        + "\n"
    )
    env = {
        **os.environ,
        "JAVA_HOME": str(java_home),
        "NEO4J_HOME": str(neo4j_home),
        "NEO4J_CONF": str(conf),
    }
    hidden = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    admin = neo4j_home / "bin/neo4j-admin.bat"
    password = secrets.token_urlsafe(24)
    with (folder / "admin.log").open("w") as log:
        result = subprocess.run(
            [str(admin), "dbms", "set-initial-password", password],
            env=env,
            stdout=log,
            stderr=log,
            **hidden,
        )
        if result.returncode:
            raise RuntimeError(
                "Neo4j initialization failed; inspect the local admin log."
            )
    started = time.perf_counter()
    args = [
        str(admin),
        "database",
        "import",
        "full",
        "--nodes=Entity=" + str(pack / "graph-nodes.csv"),
        "--nodes=Entity=" + str(overlay / "workflow-nodes.csv"),
        "--relationships=" + str(pack / "graph-relationships.csv"),
        "--relationships=" + str(overlay / "workflow-relationships.csv"),
        "--auto-skip-subsequent-headers=true",
        "--strict=true",
        "--max-off-heap-memory=256M",
        "--threads=2",
        "--report-file=" + str(folder / "import-report.txt"),
        "neo4j",
    ]
    with (folder / "import.log").open("w") as log:
        result = subprocess.run(args, env=env, stdout=log, stderr=log, **hidden)
    if result.returncode:
        raise RuntimeError(
            "Graph import failed; inspect import.log. No existing graph was overwritten."
        )
    import_seconds = time.perf_counter() - started
    with (folder / "console.log").open("w") as log:
        process = subprocess.Popen(
            [str(neo4j_home / "bin/neo4j.bat"), "console"],
            env=env,
            stdout=log,
            stderr=log,
            **hidden,
        )
    (folder / "local-runtime.json").write_text(
        json.dumps(
            {
                "pid": process.pid,
                "password": password,
                "neo4j_home": str(neo4j_home),
                "java_home": str(java_home),
                "conf": str(conf),
            }
        )
    )
    driver = GraphDatabase.driver(
        "bolt://127.0.0.1:17687", auth=("neo4j", password), connection_timeout=3
    )
    deadline = time.monotonic() + 90
    while True:
        try:
            driver.verify_connectivity()
            break
        except Exception:
            if time.monotonic() > deadline:
                raise RuntimeError(
                    "Imported graph did not start; inspect console.log."
                ) from None
            time.sleep(2)
    with driver, driver.session() as session:
        session.run(
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE"
        ).consume()
        session.run(
            "CREATE INDEX entity_tenant IF NOT EXISTS FOR (n:Entity) ON (n.tenant_id)"
        ).consume()
        session.run("CALL db.awaitIndexes(60)").consume()
        counts = session.run("MATCH (n:Entity) RETURN count(n) AS count").single()[
            "count"
        ]
        edges = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()[
            "count"
        ]
        by_kind = {
            r["kind"]: r["count"]
            for r in session.run(
                "MATCH (n:Entity) UNWIND labels(n) AS kind WITH kind,count(*) AS count WHERE kind <> 'Entity' RETURN kind,count"
            )
        }
        overlay_rows = json.loads((overlay / "report.json").read_text())
        expected_nodes = (
            manifest["counts"]["entities"]
            + sum(overlay_rows["cases"].values())
            + overlay_rows["inventory_products"]
        )
        expected_edges = (
            manifest["counts"]["relationships"]
            + sum(overlay_rows["cases"].values())
            + 2 * overlay_rows["inventory_products"]
        )
        if (counts, edges) != (expected_nodes, expected_edges):
            raise ValueError("Imported graph counts do not match source datasets.")
        sample = session.run(
            "MATCH (f:Farmer:Entity {id:'farmer-synth-000001'})-[r]-(n) RETURN count(r) AS count"
        ).single()["count"]
    for key, value in {
        "WORKFLOW_NEO4J_URI": "bolt://127.0.0.1:17687",
        "WORKFLOW_NEO4J_USER": "neo4j",
        "WORKFLOW_NEO4J_PASSWORD": password,
    }.items():
        set_key(root / ".env", key, value)
    report = {
        "nodes": counts,
        "relationships": edges,
        "nodes_by_kind": by_kind,
        "sample_farmer_relationships": sample,
        "import_seconds": round(import_seconds, 2),
        "source_kind": "synthetic_replay",
        "gds_algorithms_run": False,
        "boundary": "Indexed graph context and relationships; no calibrated credit score or real-world outcome validation.",
    }
    (folder / "verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("pack", "overlay", "neo4j-home", "java-home"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--instance", default="graph-runtime-v1")
    args = parser.parse_args()
    run(
        args.pack.resolve(),
        args.overlay.resolve(),
        args.neo4j_home.resolve(),
        args.java_home.resolve(),
        args.instance,
    )
