"""Scoped order access, presentation, and reservation transitions.

Call mutation helpers inside the caller-owned database transaction. They never
perform network calls or create a second transaction.
"""

import secrets

from fastapi import HTTPException
from sqlalchemy import insert, select, update

from .. import db
from ..auth import require, scoped_orders
from ..config import settings
from ..contracts.requests import CollectionRequest, OrderRequest
from . import handoffs


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


def create_order(body: OrderRequest, user):
    require(user, "farmer")
    if len({item.product_id for item in body.items}) != len(body.items):
        raise HTTPException(422, "Combine duplicate products into one line item.")
    with db.engine.begin() as conn:
        existing = (
            conn.execute(
                select(db.orders).where(
                    db.orders.c.farmer_id == user["subject"],
                    db.orders.c.client_request_id == body.client_request_id,
                )
            )
            .mappings()
            .first()
        )
        if existing:
            original = {
                item["product_id"]: item["quantity"] for item in existing["items"]
            }
            if original != {item.product_id: item.quantity for item in body.items}:
                raise HTTPException(
                    409, "This request reference belongs to a different order."
                )
            issues = [
                dict(row)
                for row in conn.execute(
                    select(db.issues).where(db.issues.c.order_id == existing["id"])
                ).mappings()
            ]
            return serialize_order(existing, user, issues)
        farmer = (
            conn.execute(select(db.farmers).where(db.farmers.c.id == user["subject"]))
            .mappings()
            .one()
        )
        items = []
        suppliers = set()
        for item in body.items:
            product = (
                conn.execute(
                    select(db.products).where(db.products.c.id == item.product_id)
                )
                .mappings()
                .first()
            )
            if not product:
                raise HTTPException(
                    422, "Choose a product from the approved catalogue."
                )
            items.append(
                {
                    "product_id": product["id"],
                    "name": product["name"],
                    "unit": product["unit"],
                    "quantity": item.quantity,
                    "price_cents": product["price_cents"],
                }
            )
            suppliers.add(product["supplier_id"])
        if len(suppliers) != 1:
            raise HTTPException(422, "Each order must use one approved supplier.")
        amount = sum(item["quantity"] * item["price_cents"] for item in items)
        # A conditional UPDATE reserves funds atomically on both SQLite and PostgreSQL.
        reserved = conn.execute(
            update(db.farmers)
            .where(
                db.farmers.c.id == user["subject"],
                db.farmers.c.expires_at > db.now(),
                db.farmers.c.limit_cents
                - db.farmers.c.spent_cents
                - db.farmers.c.reserved_cents
                >= amount,
            )
            .values(reserved_cents=db.farmers.c.reserved_cents + amount)
        )
        if reserved.rowcount != 1:
            raise HTTPException(
                409,
                "This request exceeds available credit, or the approval has expired.",
            )
        for item in sorted(items, key=lambda item: item["product_id"]):
            stock = conn.execute(
                update(db.products)
                .where(
                    db.products.c.id == item["product_id"],
                    db.products.c.stock - db.products.c.reserved >= item["quantity"],
                )
                .values(reserved=db.products.c.reserved + item["quantity"])
            )
            if stock.rowcount != 1:
                raise HTTPException(
                    409,
                    "There is insufficient available stock. Your credit was not reserved.",
                )
        order_id = conn.execute(
            insert(db.orders).values(
                farmer_id=user["subject"],
                lender_id=farmer["lender_id"],
                supplier_id=next(iter(suppliers)),
                client_request_id=body.client_request_id,
                items=items,
                amount_cents=amount,
                currency="USD",
                status="REQUESTED",
                payment_mode=settings.payment_mode,
                created_at=db.now(),
                updated_at=db.now(),
            )
        ).inserted_primary_key[0]
        db.record(
            conn,
            order_id,
            user["subject"],
            "REQUESTED",
            "Farmer confirmed catalogue items and total. Credit and inventory reserved."
            + handoffs.allocation_trace(conn, user["subject"]),
        )
        return serialize_order(get_order(conn, order_id, user), user)


def approve(order_id: int, user):
    require(user, "lender")
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user, lock=True)
        if order["status"] == "APPROVED":
            return {"ok": True}
        if order["status"] != "REQUESTED":
            raise HTTPException(409, "Only a requested order can be approved.")
        require_no_issues(conn, order_id)
        approval = (
            conn.execute(
                select(db.farmers)
                .where(db.farmers.c.id == order["farmer_id"])
                .with_for_update()
            )
            .mappings()
            .one()
        )
        if approval["expires_at"] <= db.now():
            raise HTTPException(409, "The farmer's credit approval has expired.")
        transition(conn, order, "REQUESTED", "APPROVED")
        db.record(
            conn,
            order_id,
            user["subject"],
            "APPROVED",
            "Lender approved the input order for supplier invoicing.",
        )
    return {"ok": True}


def cancel(order_id: int, user):
    if user["role"] not in {"farmer", "lender"}:
        raise HTTPException(
            403, "Only the farmer or lender can cancel before invoicing."
        )
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user)
        if order["status"] == "CANCELLED":
            return {"ok": True}
        if order["status"] not in {"REQUESTED", "APPROVED"}:
            raise HTTPException(
                409,
                "An invoiced or paid order needs operator review before cancellation.",
            )
        transition(conn, order, order["status"], "CANCELLED")
        release_reservations(conn, order)
        db.record(
            conn,
            order_id,
            user["subject"],
            "CANCELLED",
            "Order cancelled; credit and inventory reservations released.",
        )
    return {"ok": True}


def collect(order_id: int, body: CollectionRequest, user):
    require(user, "supplier")
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user, lock=True)
        if order["status"] == "COLLECTED":
            return {"ok": True, "message": "Collection was already recorded."}
        if order["status"] != "READY_FOR_COLLECTION":
            raise HTTPException(409, "Collection requires a confirmed full payment.")
        require_no_issues(conn, order_id)
        if not secrets.compare_digest(body.code, order["pickup_code"] or ""):
            raise HTTPException(422, "The collection code does not match.")
        transition(conn, order, "READY_FOR_COLLECTION", "COLLECTED")
        for item in order["items"]:
            conn.execute(
                update(db.products)
                .where(db.products.c.id == item["product_id"])
                .values(
                    stock=db.products.c.stock - item["quantity"],
                    reserved=db.products.c.reserved - item["quantity"],
                )
            )
        db.record(
            conn,
            order_id,
            user["subject"],
            "COLLECTED",
            "Dealer recorded handover with the farmer's collection code. This does not certify product quality.",
        )
    return {"ok": True}


def timeline(order_id: int, user):
    with db.engine.connect() as conn:
        get_order(conn, order_id, user)
        rows = conn.execute(
            select(db.audit)
            .where(db.audit.c.order_id == order_id)
            .order_by(db.audit.c.id)
        ).mappings()
        return [dict(row) for row in rows]
