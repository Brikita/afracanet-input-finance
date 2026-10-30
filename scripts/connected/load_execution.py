"""Import identifiers and fresh stock, never replay payments or credit authority."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from sqlalchemy import insert, select


def load_execution(pack, overlay):
    from backend import db

    db.metadata.create_all(db.engine)
    counts = {"Farmer": 0, "Product": 0}
    with db.engine.begin() as target:
        if target.execute(select(db.farmers.c.id).limit(1)).first():
            raise ValueError(
                "Execution store must be empty. Existing accounts are not overwritten."
            )
        with sqlite3.connect(
            f"file:{(pack / 'scenario.sqlite').as_posix()}?mode=ro", uri=True
        ) as source:
            for identifier, kind, tenant, raw in source.execute(
                "SELECT id,kind,tenant_id,properties FROM entities WHERE kind IN ('Lender','Dealer','Farmer','Product')"
            ):
                properties = json.loads(raw)
                if kind in counts:
                    counts[kind] += 1
                if kind in {"Lender", "Dealer"}:
                    target.execute(
                        insert(db.workspace_participants).values(
                            id=identifier,
                            role="lender" if kind == "Lender" else "supplier",
                            name=properties["display_name"],
                            source_kind="synthetic_replay",
                        )
                    )
                elif kind == "Farmer":
                    target.execute(
                        insert(db.farmers).values(
                            id=identifier,
                            name=properties["display_name"],
                            location=properties["reference_region"]
                            + " Â· fictional reference region",
                            lender_id=tenant,
                            limit_cents=0,
                            reserved_cents=0,
                            spent_cents=0,
                            expires_at="2026-01-01T00:00:00+00:00",
                            approval_reference="UNAPPROVED-SYNTHETIC-PROFILE",
                        )
                    )
                    target.execute(
                        insert(db.approval_mappings).values(
                            id=str(uuid.uuid4()),
                            lender_id=tenant,
                            source_system="afracanet-credit",
                            source_farmer_id=identifier,
                            farmer_id=identifier,
                            recorded_by="isolated_dataset_operator",
                            created_at=datetime.now(timezone.utc).isoformat(),
                        )
                    )
                else:
                    supplier = identifier.replace("SYN-PRODUCT-", "SYN-DEALER-").rsplit(
                        "-", 1
                    )[0]
                    target.execute(
                        insert(db.products).values(
                            id=identifier,
                            supplier_id=supplier,
                            name={
                                "dap": "DAP fertilizer",
                                "seed": "Maize seed",
                                "can": "CAN fertilizer",
                            }[properties["name"]],
                            category="Seed"
                            if properties["name"] == "seed"
                            else "Fertilizer",
                            unit=properties["unit"],
                            price_cents=properties["price_minor"],
                            stock=200,
                            reserved=0,
                        )
                    )
    return {
        "farmers": counts["Farmer"],
        "products": counts["Product"],
        "active_allocations": 0,
        "orders": 0,
        "payment_records": 0,
        "stock_basis": "Fresh illustrative 200 units per product; replay inventory remains separate.",
        "mapping_basis": "Explicit same-ID mapping from checksum-verified synthetic registry, enrolled by local dataset operator.",
    }
