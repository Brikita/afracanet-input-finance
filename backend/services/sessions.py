"""Sessions behavior; API dependencies are supplied by the route layer."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import insert, select

from .. import db
from ..config import settings
from ..contracts.requests import Login

PERSONAS = {
    "farmer-amina": ("farmer", "Amina Wanjiku"),
    "farmer-kiptoo": ("farmer", "David Kiptoo"),
    "lender-demo": ("lender", "Demo Agricultural SACCO"),
    "supplier-demo": ("supplier", "Demo Green Valley Agrovet"),
}


def participant(persona):
    if persona in PERSONAS and PERSONAS[persona][0] != "farmer":
        return PERSONAS[persona]
    with db.engine.connect() as conn:
        organization = (
            conn.execute(
                select(db.workspace_participants).where(
                    db.workspace_participants.c.id == persona
                )
            )
            .mappings()
            .first()
        )
        if organization:
            return organization["role"], organization["name"]
        name = conn.execute(
            select(db.farmers.c.name).where(db.farmers.c.id == persona)
        ).scalar_one_or_none()
    return ("farmer", name) if name else None


def participant_choices(user):
    # Demonstration switching uses a shared code, not separate production identities.
    with db.engine.connect() as conn:
        farmers = (
            conn.execute(
                select(db.farmers.c.id, db.farmers.c.name).order_by(db.farmers.c.name)
            )
            .mappings()
            .all()
        )
        organizations = (
            conn.execute(
                select(
                    db.workspace_participants.c.id, db.workspace_participants.c.name
                ).order_by(db.workspace_participants.c.name)
            )
            .mappings()
            .all()
        )
    return (
        [
            {"id": key, "name": value[1]}
            for key, value in PERSONAS.items()
            if value[0] != "farmer"
        ]
        + [dict(row) for row in organizations]
        + [dict(row) for row in farmers]
    )


def login(body: Login):
    if not secrets.compare_digest(body.access_code, settings.access_code):
        raise HTTPException(401, "Invalid participant or access code.")
    identity = participant(body.persona)
    if not identity:
        raise HTTPException(401, "Invalid participant or access code.")
    token = secrets.token_urlsafe(32)
    role, name = identity
    with db.engine.begin() as conn:
        conn.execute(
            insert(db.sessions).values(
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                role=role,
                subject=body.persona,
                expires_at=(
                    datetime.now(timezone.utc) + timedelta(hours=8)
                ).isoformat(),
            )
        )
    return {"token": token, "role": role, "subject": body.persona, "name": name}


def logout(user):
    from sqlalchemy import delete

    with db.engine.begin() as conn:
        conn.execute(
            delete(db.sessions).where(db.sessions.c.token_hash == user["token_hash"])
        )
    return {"ok": True}


def personas():
    # Public demo choices are limited to seeded examples; imported people need a session.
    return [
        {"id": key, "role": value[0], "name": value[1]}
        for key, value in PERSONAS.items()
    ]
