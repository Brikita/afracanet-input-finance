"""Attach attributed public reanalysis to reference regions, never farm locations."""

import argparse
import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


def load(folder):
    manifest = json.loads((folder / "manifest.json").read_text())
    rows = []
    for index, snapshot in enumerate(manifest["snapshots"]):
        path = folder / snapshot["file"]
        if (
            path.parent.resolve() != folder.resolve()
            or hashlib.sha256(path.read_bytes()).hexdigest() != snapshot["sha256"]
        ):
            raise ValueError("Public weather checksum or path mismatch.")
        data = json.loads(path.read_text(encoding="utf-8"))
        region = {
            "meru-reference": "SYN-REGION-00",
            "machakos-reference": "SYN-REGION-01",
        }[snapshot["location"]["id"]]
        for n, day in enumerate(data["daily"]["time"]):
            properties = {
                "date": day,
                "reference_point": snapshot["location"]["name"],
                "precipitation_mm": data["daily"]["precipitation_sum"][n],
                "temperature_max_c": data["daily"]["temperature_2m_max"][n],
                "temperature_min_c": data["daily"]["temperature_2m_min"][n],
                "attribution": manifest["attribution"],
                "license": manifest["license"],
                "source_url": snapshot["source_url"],
                "fetched_at_utc": manifest["fetched_at_utc"],
                "limits": manifest["limits"],
                "snapshot_sha256": snapshot["sha256"],
            }
            rows.append(
                {
                    "id": "PUBLIC-WEATHER-" + snapshot["location"]["id"] + "-" + day,
                    "region": region,
                    "properties": json.dumps(properties),
                }
            )
    with (
        GraphDatabase.driver(
            os.environ["WORKFLOW_NEO4J_URI"],
            auth=(
                os.environ["WORKFLOW_NEO4J_USER"],
                os.environ["WORKFLOW_NEO4J_PASSWORD"],
            ),
        ) as driver,
        driver.session() as session,
    ):
        result = session.run(
            """UNWIND $rows AS row MATCH (region:Entity:ReferenceRegion {id:row.region})
        MERGE (w:Entity:PublicWeather {id:row.id}) SET w.tenant_id='context',w.source_kind='public_weather_reanalysis',w.properties=row.properties
        MERGE (region)-[:HAS_PUBLIC_CONTEXT]->(w) RETURN count(w) AS count""",
            rows=rows,
        ).single()["count"]
        if result != len(rows):
            raise ValueError("Public context reference-region mapping incomplete.")
    return {
        "public_daily_records": result,
        "reference_regions": 2,
        "source_kind": manifest["source_kind"],
        "attribution": manifest["attribution"],
        "license": manifest["license"],
        "limits": manifest["limits"],
    }


if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    print(json.dumps(load(parser.parse_args().folder.resolve())))
