"""Versioned descriptive GDS results, never a lending score or authorization."""

import json
import time
import uuid

from fastapi import HTTPException
from sqlalchemy import Column, MetaData, String, Table, Text, insert, select

from . import store

metadata = MetaData()
runs = Table(
    "graph_analytics_runs",
    metadata,
    Column("id", String, primary_key=True),
    Column("lender_id", String, nullable=False, index=True),
    Column("created_at", String, nullable=False),
    Column("manifest_sha256", String, nullable=False),
    Column("result", Text, nullable=False),
)

NODE_SCOPE = "n.tenant_id=$tenant AND (n:Farmer OR n:SavingsGroup OR n:Cooperative)"
PROJECTION = """
MATCH (source:Entity)
WHERE source.tenant_id=$tenant AND (source:Farmer OR source:SavingsGroup OR source:Cooperative)
OPTIONAL MATCH (source)-[r:MEMBER_OF]->(target:Entity)
WHERE target.tenant_id=$tenant AND (target:SavingsGroup OR target:Cooperative)
WITH gds.graph.project($name,source,target,{relationshipType:'MEMBERSHIP'},
  {undirectedRelationshipTypes:['*'],readConcurrency:1}) AS g
RETURN g.graphName AS graphName,g.nodeCount AS nodeCount,g.relationshipCount AS relationshipCount
"""
LIMITS = {"nodes": 10000, "relationships": 50000, "algorithm_bytes": 64 * 1024 * 1024}


def compute(session, lender_id):
    started = time.perf_counter()
    version = session.run("RETURN gds.version() AS version").single()["version"]
    manifest = session.run(
        "MATCH (d:JudgeDataset) RETURN d.fingerprint AS fingerprint,d.as_of AS as_of"
    ).single()
    if not manifest:
        raise ValueError(
            "This runner requires an explicitly loaded, fingerprinted judge dataset."
        )
    counts = session.run(
        f"MATCH (n:Entity) WHERE {NODE_SCOPE} RETURN count(n) AS nodes",
        tenant=lender_id,
    ).single()
    edges = session.run(
        "MATCH (a:Entity)-[r:MEMBER_OF]->(b:Entity) WHERE a.tenant_id=$tenant AND b.tenant_id=$tenant AND a:Farmer AND (b:SavingsGroup OR b:Cooperative) RETURN count(r) AS edges",
        tenant=lender_id,
    ).single()["edges"]
    if (
        not counts["nodes"]
        or counts["nodes"] > LIMITS["nodes"]
        or edges * 2 > LIMITS["relationships"]
    ):
        raise ValueError("Projection is empty or exceeds the bounded judge limits.")
    run_id = str(uuid.uuid4())
    graph_name = "afracanet_" + run_id.replace("-", "")
    projected = False
    try:
        projection = dict(
            session.run(PROJECTION, name=graph_name, tenant=lender_id).single()
        )
        projected = True
        estimates = {}
        for algorithm in ("pageRank", "louvain"):
            estimate = dict(
                session.run(
                    f"CALL gds.{algorithm}.stream.estimate($name,{{concurrency:1}}) YIELD bytesMin,bytesMax RETURN bytesMin,bytesMax",
                    name=graph_name,
                ).single()
            )
            if estimate["bytesMax"] > LIMITS["algorithm_bytes"]:
                raise ValueError("GDS algorithm exceeds the configured memory budget.")
            estimates[algorithm] = estimate
        ranks = {
            row["id"]: row["score"]
            for row in session.run(
                "CALL gds.pageRank.stream($name,{concurrency:1,dampingFactor:0.85,maxIterations:20,tolerance:0.000001}) YIELD nodeId,score RETURN gds.util.asNode(nodeId).id AS id,score",
                name=graph_name,
            )
        }
        communities = {
            row["id"]: row["community"]
            for row in session.run(
                "CALL gds.louvain.stream($name,{concurrency:1}) YIELD nodeId,communityId RETURN gds.util.asNode(nodeId).id AS id,communityId AS community",
                name=graph_name,
            )
        }
        nodes = [
            dict(row)
            for row in session.run(
                f"MATCH (n:Entity) WHERE {NODE_SCOPE} RETURN n.id AS id,labels(n) AS labels,n.properties AS properties ORDER BY n.id",
                tenant=lender_id,
            )
        ]
        links = [
            dict(row)
            for row in session.run(
                "MATCH (a:Entity:Farmer)-[:MEMBER_OF]->(b:Entity) WHERE a.tenant_id=$tenant AND b.tenant_id=$tenant AND (b:SavingsGroup OR b:Cooperative) RETURN a.id AS source,b.id AS target ORDER BY source,target",
                tenant=lender_id,
            )
        ]
        return {
            "id": run_id,
            "lender_id": lender_id,
            "created_at": store.now(),
            "manifest_sha256": manifest["fingerprint"],
            "gds_version": version,
            "source_kind": "synthetic_replay",
            "calibrated_credit_score": None,
            "authority": "descriptive_analytics_only",
            "projection": projection,
            "parameters": {
                "relationship": "MEMBER_OF",
                "orientation": "UNDIRECTED",
                "weights": "unweighted",
                "concurrency": 1,
                "pageRank": {
                    "dampingFactor": 0.85,
                    "maxIterations": 20,
                    "tolerance": 0.000001,
                },
                "louvain": {"concurrency": 1, "community_ids": "run_specific"},
            },
            "as_of": manifest["as_of"],
            "memory_estimates": estimates,
            "limits": LIMITS,
            "seconds": round(time.perf_counter() - started, 3),
            "nodes": [
                {
                    "id": node["id"],
                    "labels": node["labels"],
                    "name": json.loads(node["properties"]).get(
                        "display_name", node["id"]
                    ),
                    "page_rank": ranks[node["id"]],
                    "community": communities[node["id"]],
                }
                for node in nodes
            ],
            "links": links,
            "limits_explanation": "Unweighted membership connectivity and computed communities in an authored graph. Neither centrality nor community membership establishes income, default risk, lending approval or payment. No temporal filtering or outcome calibration is inferred.",
        }
    finally:
        if projected:
            session.run(
                "CALL gds.graph.drop($name,false) YIELD graphName RETURN graphName",
                name=graph_name,
            ).consume()


def save(result):
    metadata.create_all(store.engine)
    with store.engine.begin() as conn:
        conn.execute(
            insert(runs).values(
                id=result["id"],
                lender_id=result["lender_id"],
                created_at=result["created_at"],
                manifest_sha256=result["manifest_sha256"],
                result=json.dumps(result, sort_keys=True),
            )
        )


def latest(farmer_id, lender_id, run_id=None):
    # Table creation belongs to startup/operator commands, never an evidence read.
    with store.engine.connect() as conn:
        row = conn.execute(
            select(runs.c.result)
            .where(
                runs.c.lender_id == lender_id,
                *([runs.c.id == run_id] if run_id else []),
            )
            .order_by(runs.c.created_at.desc(), runs.c.id.desc())
            .limit(1)
        ).scalar_one_or_none()
    if row is None:
        return {"available": False, "reason": "No computed GDS run for this lender."}
    result = json.loads(row)
    selected = next((node for node in result["nodes"] if node["id"] == farmer_id), None)
    if selected is None:
        return {
            "available": False,
            "reason": "Farmer is absent from this GDS projection.",
        }
    return {"available": True, "selected": selected, **result}


def read(farmer_id, lender_id, run_id=None):
    try:
        return latest(farmer_id, lender_id, run_id)
    except Exception:
        raise HTTPException(
            503, "Graph analytics unavailable. No metrics were substituted."
        ) from None
