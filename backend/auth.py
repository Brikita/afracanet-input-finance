"""Session validation and server-side role/subject scoping."""

import hashlib

from fastapi import Header, HTTPException
from sqlalchemy import select

from . import db


def actor(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Choose a demo participant to sign in.")
    token_hash = hashlib.sha256(authorization[7:].encode()).hexdigest()
    with db.engine.connect() as conn:
        session = (
            conn.execute(
                select(db.sessions).where(
                    db.sessions.c.token_hash == token_hash,
                    db.sessions.c.expires_at > db.now(),
                )
            )
            .mappings()
            .first()
        )
    if not session:
        raise HTTPException(401, "Your session expired. Please sign in again.")
    return dict(session)


def require(user, role):
    if user["role"] != role:
        raise HTTPException(403, f"This action requires the {role} role.")


def scoped_orders(user):
    column = {
        "farmer": db.orders.c.farmer_id,
        "lender": db.orders.c.lender_id,
        "supplier": db.orders.c.supplier_id,
    }[user["role"]]
    return column == user["subject"]
