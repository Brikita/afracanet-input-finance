"""Compare identities, products, inventory and balances across isolated stores."""

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path

import psycopg
from dotenv import dotenv_values
from neo4j import GraphDatabase
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]


def digest(rows):
    return hashlib.sha256(
        json.dumps(sorted([list(row) for row in rows]), separators=(",", ":")).encode()
    ).hexdigest()


def run(credit_repo):
    inputs = dotenv_values(ROOT / ".env")
    credit = dotenv_values(credit_repo / ".env")
    with (
        create_engine(inputs["DATABASE_URL"]).connect() as execution,
        create_engine(credit["CREDIT_DATABASE_URL"]).connect() as workflow,
        psycopg.connect(credit["REPLAY_DATABASE_URL"]) as replay,
        GraphDatabase.driver(
            credit["WORKFLOW_NEO4J_URI"],
            auth=(credit["WORKFLOW_NEO4J_USER"], credit["WORKFLOW_NEO4J_PASSWORD"]),
        ) as graph,
        graph.session() as session,
    ):
        registry_ids = replay.execute(
            "SELECT id,tenant_id FROM replay.entities WHERE kind='Farmer' ORDER BY id"
        ).fetchall()
        execution_ids = execution.execute(
            text("SELECT id,lender_id FROM farmers ORDER BY id")
        ).all()
        workflow_ids = workflow.execute(
            text("SELECT farmer_id,lender_id FROM applications ORDER BY farmer_id")
        ).all()
        graph_ids = [
            tuple(r)
            for r in session.run(
                "MATCH (f:Entity:Farmer) RETURN f.id AS id,f.tenant_id AS tenant ORDER BY id"
            )
        ]
        hashes = {
            name: digest(rows)
            for name, rows in {
                "replay": registry_ids,
                "execution": execution_ids,
                "workflow": workflow_ids,
                "graph": graph_ids,
            }.items()
        }
        if len(set(hashes.values())) != 1:
            raise ValueError("Farmer ID/lender mapping differs between stores.")
        inventory = replay.execute(
            "SELECT product_id,stock_units,reserved_units,fulfilled_units FROM replay.inventory ORDER BY product_id"
        ).fetchall()
        graph_inventory = []
        for row in session.run(
            "MATCH (n:Entity:Inventory)-[:FOR_PRODUCT]->(p:Product) RETURN p.id AS id,n.properties AS properties ORDER BY id"
        ):
            p = json.loads(row["properties"])
            graph_inventory.append(
                (row["id"], p["stock_units"], p["reserved_units"], p["fulfilled_units"])
            )
        if inventory != graph_inventory:
            raise ValueError(
                "Replay inventory differs between graph and relational registry."
            )
        products = {
            row["id"]: json.loads(row["properties"])["price_minor"]
            for row in session.run(
                "MATCH (n:Entity:Product) RETURN n.id AS id,n.properties AS properties"
            )
        }
        actual = dict(
            execution.execute(text("SELECT id,price_cents FROM products")).all()
        )
        if products != actual:
            raise ValueError("Product IDs or illustrative USD prices differ.")
        active = dict(
            execution.execute(
                text(
                    "SELECT count(*) AS farmers,coalesce(sum(limit_cents),0) AS limit_cents,coalesce(sum(reserved_cents),0) AS reserved_cents,coalesce(sum(spent_cents),0) AS spent_cents FROM farmers"
                )
            )
            .mappings()
            .one()
        )
        loan_totals = replay.execute(
            "SELECT sum(principal_minor),sum(repaid_minor),sum(outstanding_minor) FROM replay.loans"
        ).fetchone()
        if loan_totals[0] != loan_totals[1] + loan_totals[2]:
            raise ValueError("KES loan history does not reconcile.")
        timings = []
        for farmer, tenant in registry_ids[:50]:
            started = time.perf_counter()
            session.run(
                "MATCH (f:Entity:Farmer {id:$id,tenant_id:$tenant})-[r]-() RETURN count(r) AS degree",
                id=farmer,
                tenant=tenant,
            ).single()
            timings.append((time.perf_counter() - started) * 1000)
        counts = session.run("MATCH (n:Entity) RETURN count(n) AS count").single()[
            "count"
        ]
        edges = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()[
            "count"
        ]
        public = session.run(
            "MATCH (n:PublicWeather) RETURN count(n) AS count"
        ).single()["count"]
        if (counts, edges, public) != (928163, 1886728, 60):
            raise ValueError(
                "Graph totals do not match the pinned connected-v1 pack plus public context."
            )
        roles_readonly = (
            replay.execute(
                "SELECT has_table_privilege(current_user,'replay.loans','INSERT')"
            ).fetchone()[0]
            is False
        )
        if not roles_readonly:
            raise ValueError("Credit registry account must be read-only.")
    return {
        "result": "passed",
        "farmer_count": len(registry_ids),
        "farmer_lender_id_sha256": hashes,
        "products_verified": len(products),
        "inventory_rows_verified": len(inventory),
        "graph_nodes": counts,
        "graph_relationships": edges,
        "public_weather_records": public,
        "historical_loans_minor_KES": {
            "principal": loan_totals[0],
            "repaid": loan_totals[1],
            "outstanding": loan_totals[2],
        },
        "initial_execution_balances_minor_USD": active,
        "replay_reader_has_no_insert_permission": roles_readonly,
        "graph_query_benchmark": {
            "samples": len(timings),
            "median_ms": round(statistics.median(timings), 2),
            "p95_ms": round(sorted(timings)[47], 2),
            "scope": "Local indexed farmer neighborhood queries; no production throughput claim.",
        },
        "gds_algorithms_run": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--credit-repo", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.credit_repo.resolve())
    args.report.write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
