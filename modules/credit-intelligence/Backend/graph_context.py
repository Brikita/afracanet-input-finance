"""Graph ownership stays here. Synthetic evidence is never silently replaced."""

import json
import os

from fastapi import HTTPException
from neo4j import GraphDatabase


def context(farmer_id, lender_id):
    uri = os.getenv("WORKFLOW_NEO4J_URI", "")
    if not uri:
        raise HTTPException(
            503,
            "Graph connection is unavailable. No fallback farmer or score was generated.",
        )
    auth = (os.environ["WORKFLOW_NEO4J_USER"], os.environ["WORKFLOW_NEO4J_PASSWORD"])
    try:
        with GraphDatabase.driver(uri, auth=auth, connection_timeout=5) as driver:
            with driver.session(
                database=os.getenv("WORKFLOW_NEO4J_DATABASE", "neo4j")
            ) as session:
                record = session.run(
                    "MATCH (f:Entity:Farmer {id:$id,tenant_id:$tenant}) RETURN f.properties AS properties, f.source_kind AS provenance",
                    id=farmer_id,
                    tenant=lender_id,
                ).single()
                if not record:
                    raise HTTPException(
                        404, "Farmer is absent from your lender's graph partition."
                    )
                degree = session.run(
                    "MATCH (f:Entity:Farmer {id:$id,tenant_id:$tenant})-[r]-() RETURN count(r) AS degree",
                    id=farmer_id,
                    tenant=lender_id,
                ).single()["degree"]
                neighbors = [
                    dict(r)
                    for r in session.run(
                        "MATCH (f:Entity:Farmer {id:$id,tenant_id:$tenant})-[r]-(n:Entity) WHERE n.tenant_id IN [$tenant,'context'] RETURN n.id AS id, labels(n) AS labels, type(r) AS relationship, n.properties AS properties LIMIT 40",
                        id=farmer_id,
                        tenant=lender_id,
                    )
                ]
                weather = [
                    json.loads(r["properties"])
                    for r in session.run(
                        "MATCH (f:Entity:Farmer {id:$id,tenant_id:$tenant})-[:OPERATES_FARM]->(:Farm)-[:ASSIGNED_REFERENCE_REGION]->(:ReferenceRegion)-[:HAS_PUBLIC_CONTEXT]->(w:PublicWeather) RETURN w.properties AS properties ORDER BY w.id DESC LIMIT 30",
                        id=farmer_id,
                        tenant=lender_id,
                    )
                ]
        return {
            "farmer_id": farmer_id,
            "profile": json.loads(record["properties"]),
            "public_weather_context": weather,
            "provenance": record["provenance"],
            "relationship_count": degree,
            "neighbors": [
                {**r, "properties": json.loads(r["properties"])} for r in neighbors
            ],
            "credit_score": None,
            "recommendation": "UNAVAILABLE",
            "explanation": "Retrieved graph context. No calibrated score or lender approval has been inferred.",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            503, "Graph service unavailable. No synthetic fallback was substituted."
        ) from None
