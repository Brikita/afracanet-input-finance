"""Workspace behavior; API dependencies are supplied by the route layer."""

from sqlalchemy import select

from .. import db
from ..auth import scoped_orders
from ..config import settings
from .catalogue import product_revision
from .orders import serialize_order
from .sessions import participant


def health():
    return {
        "status": "ok",
        "payment_mode": settings.payment_mode,
        "ai_mode": settings.ai_mode,
        "currency": "USD",
        "prototype": True,
    }


def state(user):
    with db.engine.connect() as conn:
        if user["role"] == "farmer":
            people = (
                conn.execute(
                    select(db.farmers).where(db.farmers.c.id == user["subject"])
                )
                .mappings()
                .all()
            )
        elif user["role"] == "lender":
            people = (
                conn.execute(
                    select(db.farmers).where(db.farmers.c.lender_id == user["subject"])
                )
                .mappings()
                .all()
            )
        else:
            # Dealers see farmer names on their own orders, not farmers' credit data.
            ids = select(db.orders.c.farmer_id).where(scoped_orders(user))
            people = (
                conn.execute(
                    select(
                        db.farmers.c.id, db.farmers.c.name, db.farmers.c.location
                    ).where(
                        db.farmers.c.id.in_(ids),
                    )
                )
                .mappings()
                .all()
            )
        catalogue_query = select(db.products).order_by(db.products.c.id)
        if user["role"] == "supplier":
            catalogue_query = catalogue_query.where(
                db.products.c.supplier_id == user["subject"]
            )
        catalogue = conn.execute(catalogue_query).mappings().all()
        order_rows = (
            conn.execute(
                select(db.orders)
                .where(scoped_orders(user))
                .order_by(db.orders.c.id.desc())
            )
            .mappings()
            .all()
        )
        issue_rows = (
            conn.execute(
                select(db.issues)
                .where(
                    db.issues.c.order_id.in_(
                        select(db.orders.c.id).where(scoped_orders(user))
                    ),
                )
                .order_by(db.issues.c.id)
            )
            .mappings()
            .all()
        )
        by_order = {}
        for issue in issue_rows:
            by_order.setdefault(issue["order_id"], []).append(dict(issue))
    return {
        "user": {
            "role": user["role"],
            "subject": user["subject"],
            "name": participant(user["subject"])[1],
        },
        "farmers": [dict(row) for row in people],
        "products": [
            {**dict(row), "revision": product_revision(row)} for row in catalogue
        ],
        "orders": [
            serialize_order(row, user, by_order.get(row["id"], []))
            for row in order_rows
        ],
        "payment_mode": settings.payment_mode,
        "ai_mode": settings.ai_mode,
    }
