"""Read-only replay evidence; never imported as PayPal payment records."""

import os

import psycopg
from fastapi import HTTPException


def farmer_history(farmer_id, lender_id):
    url = os.getenv("REPLAY_DATABASE_URL", "")
    if not url:
        return {
            "available": False,
            "reason": "Replay history connection is not configured.",
        }
    try:
        with psycopg.connect(
            url, connect_timeout=5, options="-c default_transaction_read_only=on"
        ) as conn:
            row = conn.execute(
                "SELECT count(*),coalesce(sum(l.principal_minor),0),coalesce(sum(l.repaid_minor),0),coalesce(sum(l.outstanding_minor),0) FROM replay.loans l JOIN replay.entities e ON e.id=l.farmer_id WHERE e.id=%s AND e.tenant_id=%s",
                (farmer_id, lender_id),
            ).fetchone()
        return {
            "available": True,
            "source_kind": "synthetic_replay",
            "currency": "KES",
            "loan_count": row[0],
            "principal_minor": row[1],
            "repaid_minor": row[2],
            "outstanding_minor": row[3],
            "observed_real_outcomes": False,
        }
    except Exception:
        return {
            "available": False,
            "reason": "Replay history is unavailable; no totals were substituted.",
        }


def summary(lender_id):
    url = os.getenv("REPLAY_DATABASE_URL", "")
    if not url:
        raise HTTPException(503, "Replay registry is not configured.")
    try:
        with psycopg.connect(
            url, connect_timeout=5, options="-c default_transaction_read_only=on"
        ) as conn:
            kinds = dict(
                conn.execute(
                    "SELECT kind,count(*) FROM replay.entities WHERE tenant_id=%s GROUP BY kind",
                    (lender_id,),
                ).fetchall()
            )
            loans = conn.execute(
                "SELECT coalesce(sum(principal_minor),0),coalesce(sum(repaid_minor),0),coalesce(sum(outstanding_minor),0) FROM replay.loans l JOIN replay.entities e ON e.id=l.farmer_id WHERE e.tenant_id=%s",
                (lender_id,),
            ).fetchone()
            inventory = conn.execute(
                "SELECT count(*),coalesce(sum(stock_units),0),coalesce(sum(reserved_units),0),coalesce(sum(fulfilled_units),0) FROM replay.inventory WHERE tenant_id=%s",
                (lender_id,),
            ).fetchone()
            fingerprint = conn.execute(
                "SELECT fingerprint FROM replay.dataset_manifest"
            ).fetchone()[0]
        return {
            "lender_id": lender_id,
            "source_kind": "synthetic_replay",
            "nodes_by_kind": kinds,
            "loan_history": {
                "currency": "KES",
                "principal_minor": loans[0],
                "repaid_minor": loans[1],
                "outstanding_minor": loans[2],
            },
            "replay_inventory": {
                "products": inventory[0],
                "stock_units": inventory[1],
                "reserved_units": inventory[2],
                "fulfilled_units": inventory[3],
            },
            "manifest_sha256": fingerprint,
            "calibrated": False,
            "provider_payment_evidence": False,
            "boundary": "Authored histories for workflow and graph testing. Historical KES loans and illustrative USD input allocations are separate. No exchange rate, observed loan outcomes, or verified PayPal payments are inferred.",
        }
    except Exception:
        raise HTTPException(
            503, "Replay registry unavailable. No replacement totals were generated."
        ) from None
