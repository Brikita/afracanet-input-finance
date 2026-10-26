"""Scoped order access, presentation, and reservation transitions.

Call mutation helpers inside the caller-owned database transaction. They never
perform network calls or create a second transaction.
"""

from fastapi import HTTPException
from sqlalchemy import select, update

from .. import db
from ..auth import scoped_orders


def get_order(conn, order_id, user, lock=False):
    if lock:
        # A real row write serializes issue/collection decisions on SQLite and PostgreSQL.
        conn.execute(
            update(db.orders)
            .where(db.orders.c.id == order_id, scoped_orders(user))
            .values(updated_at=db.now())
        )
    row = (
        conn.execute(
            select(db.orders).where(
                db.orders.c.id == order_id,
                scoped_orders(user),
            )
        )
        .mappings()
        .first()
    )
    if not row:
        raise HTTPException(404, "Order not found.")
    return dict(row)


def serialize_order(row, user, issues=None):
    result = dict(row)
    result["issues"] = issues or []
    if user["role"] != "farmer":
        result.pop("pickup_code", None)
    if user["role"] != "lender":
        result.pop("payment_url", None)
    if any(issue["resolved_at"] is None for issue in result["issues"]):
        result.pop("pickup_code", None)
        result.pop("payment_url", None)
    result["reference"] = f"AFC-{row['id']:06d}"
    return result


def require_no_issues(conn, order_id):
    if conn.execute(
        select(db.issues.c.id)
        .where(db.issues.c.order_id == order_id, db.issues.c.resolved_at.is_(None))
        .limit(1)
    ).first():
        raise HTTPException(
            409, "An open issue needs lender resolution before this action."
        )


def transition(conn, order, from_status, to_status):
    changed = conn.execute(
        update(db.orders)
        .where(
            db.orders.c.id == order["id"],
            db.orders.c.status == from_status,
        )
        .values(status=to_status, updated_at=db.now())
    )
    if changed.rowcount != 1:
        raise HTTPException(409, "The order has changed. Refresh before continuing.")


def release_reservations(conn, order):
    conn.execute(
        update(db.farmers)
        .where(db.farmers.c.id == order["farmer_id"])
        .values(
            reserved_cents=db.farmers.c.reserved_cents - order["amount_cents"],
        )
    )
    for item in sorted(order["items"], key=lambda item: item["product_id"]):
        conn.execute(
            update(db.products)
            .where(db.products.c.id == item["product_id"])
            .values(
                reserved=db.products.c.reserved - item["quantity"],
            )
        )
