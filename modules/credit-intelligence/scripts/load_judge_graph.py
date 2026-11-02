"""Online import into a fresh judge graph. Never clears or replaces any graph."""

import hashlib
import json
import re
import sqlite3


def chunks(rows, size=300):
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def load(session, pack, overlay):
    fingerprint = hashlib.sha256((pack / "manifest.json").read_bytes()).hexdigest()
    previous = session.run(
        "MATCH (d:JudgeDataset) RETURN d.fingerprint AS fingerprint"
    ).single()
    if previous:
        if previous["fingerprint"] != fingerprint:
            raise ValueError(
                "Judge graph belongs to another dataset; no data was changed."
            )
        return {"status": "existing", "manifest_sha256": fingerprint}
    if session.run("MATCH (n) RETURN count(n) AS count").single()["count"]:
        raise ValueError("Judge import requires an empty graph; nothing was deleted.")
    session.run(
        "CREATE CONSTRAINT judge_entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE"
    ).consume()
    for database, node_table, edge_table in [
        (pack / "scenario.sqlite", "entities", "relationships"),
        (overlay / "workflow.sqlite", "nodes", "edges"),
    ]:
        with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as conn:
            kinds = [
                row[0]
                for row in conn.execute(f"SELECT DISTINCT kind FROM {node_table}")
            ]
            for kind in kinds:
                if not re.fullmatch(r"[A-Za-z]+", kind):
                    raise ValueError("Invalid entity label")
                rows = conn.execute(
                    f"SELECT id,tenant_id,properties,source_kind FROM {node_table} WHERE kind=?",
                    (kind,),
                )
                for batch in chunks(rows):
                    session.run(
                        f"UNWIND $rows AS row CREATE (n:Entity:{kind}) SET n=row",
                        rows=[
                            dict(
                                zip(
                                    ("id", "tenant_id", "properties", "source_kind"),
                                    row,
                                )
                            )
                            for row in batch
                        ],
                    ).consume()
            kinds = [
                row[0]
                for row in conn.execute(f"SELECT DISTINCT kind FROM {edge_table}")
            ]
            for kind in kinds:
                if not re.fullmatch(r"[A-Z_]+", kind):
                    raise ValueError("Invalid relationship type")
                rows = conn.execute(
                    f"SELECT source_id,target_id,occurred_on,properties FROM {edge_table} WHERE kind=?",
                    (kind,),
                )
                for batch in chunks(rows):
                    session.run(
                        f"UNWIND $rows AS row MATCH (a:Entity {{id:row.source}}), (b:Entity {{id:row.target}}) CREATE (a)-[r:{kind}]->(b) SET r.occurred_on=row.occurred_on,r.properties=row.properties",
                        rows=[
                            dict(
                                zip(
                                    ("source", "target", "occurred_on", "properties"),
                                    row,
                                )
                            )
                            for row in batch
                        ],
                    ).consume()
    session.run(
        "CREATE CONSTRAINT judge_entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE"
    ).consume()
    session.run(
        "CREATE INDEX judge_tenant IF NOT EXISTS FOR (n:Entity) ON (n.tenant_id)"
    ).consume()
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    session.run(
        "CREATE (d:JudgeDataset {fingerprint:$fingerprint,as_of:$as_of,source_kind:'synthetic_replay'})",
        fingerprint=fingerprint,
        as_of=manifest["as_of"],
    ).consume()
    result = dict(session.run("MATCH (n:Entity) RETURN count(n) AS nodes").single())
    result.update(
        dict(session.run("MATCH ()-[r]->() RETURN count(r) AS relationships").single())
    )
    return {**result, "status": "loaded", "manifest_sha256": fingerprint}
