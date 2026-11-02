"""Run bounded PageRank/Louvain against an isolated labelled judge graph."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True, type=Path)
    parser.add_argument("--lender", required=True)
    args = parser.parse_args()
    os.environ["CREDIT_ENV_FILE"] = str(args.env_file.resolve())
    load_dotenv(args.env_file, override=True)
    from Backend import analytics

    with (
        GraphDatabase.driver(
            os.environ["WORKFLOW_NEO4J_URI"],
            auth=(
                os.environ["WORKFLOW_NEO4J_USER"],
                os.environ["WORKFLOW_NEO4J_PASSWORD"],
            ),
            connection_timeout=5,
        ) as driver,
        driver.session(
            database=os.getenv("WORKFLOW_NEO4J_DATABASE", "neo4j")
        ) as session,
    ):
        result = analytics.compute(session, args.lender)
    analytics.save(result)
    print(
        json.dumps(
            {
                "id": result["id"],
                "lender_id": args.lender,
                "gds_version": result["gds_version"],
                "nodes": len(result["nodes"]),
                "links": len(result["links"]),
                "seconds": result["seconds"],
                "authority": result["authority"],
            }
        )
    )


if __name__ == "__main__":
    main()
