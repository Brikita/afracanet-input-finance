"""Management audit writes participate in the caller-owned transaction."""

from sqlalchemy import insert

from .. import db


def log(conn, user, action, detail):
    conn.execute(
        insert(db.management_events).values(
            actor=user["subject"],
            action=action,
            detail=detail,
            created_at=db.now(),
        )
    )
