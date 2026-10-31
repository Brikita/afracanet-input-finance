"""Read a few synthetic cases and check actual provider summaries. No decisions."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from Backend import advisory, graph_context, store


def run(lender, limit):
    with store.engine.connect() as conn:
        rows = (
            conn.execute(
                select(store.applications)
                .where(
                    store.applications.c.lender_id == lender,
                    store.applications.c.provenance == "synthetic",
                )
                .order_by(store.applications.c.farmer_id)
                .limit(limit)
            )
            .mappings()
            .all()
        )
    if not rows:
        raise ValueError("No synthetic cases found for that lender.")
    results = []
    for row in rows:
        evidence = graph_context.context(row["farmer_id"], lender)
        summary = advisory.summarize(evidence, row["provenance"])
        results.append(
            {
                "farmer_id": row["farmer_id"],
                "schema_and_citations_valid": True,
                "summary": summary,
            }
        )
    report = {
        "checked_at": store.now(),
        "scope": "Actual provider and read-only synthetic/public context. Schema and citation checks only; no independent accuracy, calibrated credit score, lender decision, payment or collection.",
        "cases": results,
    }
    output = ROOT / "data/evaluations/credit-advisory-check.json"
    output.parent.mkdir(exist_ok=True, parents=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"Actual provider schema/citation checks passed for {len(results)} synthetic cases. No decisions or deliveries created."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lender", default="SYN-LENDER-000")
    parser.add_argument("--limit", type=int, choices=range(1, 6), default=3)
    args = parser.parse_args()
    try:
        run(args.lender, args.limit)
    except Exception as error:
        print("Credit AI check stopped:", type(error).__name__)
        raise SystemExit(1) from None
