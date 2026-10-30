"""Individual local officer accounts. Provisioning is an operator CLI action."""
import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException
from sqlalchemy import delete, insert, select, update
from . import store

def password_hash(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return base64.b64encode(salt + digest).decode()

def matches(password, encoded):
    raw = base64.b64decode(encoded)
    return hmac.compare_digest(hashlib.scrypt(password.encode(), salt=raw[:16], n=16384, r=8, p=1), raw[16:])

def provision(officer_id, lender_id, password):
    if len(password) < 16:
        raise ValueError("Use an individual password of at least 16 characters.")
    store.initialize()
    with store.engine.begin() as conn:
        conn.execute(insert(store.officers).values(id=officer_id, lender_id=lender_id, password_hash=password_hash(password)))

def login(officer_id, password):
    # Expensive password work is outside a write transaction.
    with store.engine.connect() as conn:
        officer = conn.execute(select(store.officers).where(store.officers.c.id == officer_id)).mappings().first()
    valid = matches(password, officer["password_hash"] if officer else password_hash("invalid-account-password"))
    if not officer or not officer["enabled"] or officer["locked_until"] > store.now():
        raise HTTPException(401, "Invalid account, password, or locked account.")
    if not valid:
        with store.engine.begin() as conn:
            conn.execute(update(store.officers).where(store.officers.c.id == officer_id).values(
                failures=store.officers.c.failures + 1,
                locked_until=(datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat() if officer["failures"] >= 4 else ""))
        raise HTTPException(401, "Invalid account, password, or locked account.")
    token = secrets.token_urlsafe(32)
    with store.engine.begin() as conn:
        conn.execute(update(store.officers).where(store.officers.c.id == officer_id).values(failures=0, locked_until=""))
        conn.execute(insert(store.sessions).values(token_hash=hashlib.sha256(token.encode()).hexdigest(), officer_id=officer_id,
            expires_at=(datetime.now(timezone.utc) + timedelta(hours=4)).isoformat()))
    return {"token": token, "officer_id": officer_id, "lender_id": officer["lender_id"]}

def actor(authorization: str = Header(default="")):
    token = authorization.removeprefix("Bearer ")
    with store.engine.connect() as conn:
        row = conn.execute(select(store.officers).join(store.sessions, store.sessions.c.officer_id == store.officers.c.id).where(
            store.sessions.c.token_hash == hashlib.sha256(token.encode()).hexdigest(),
            store.sessions.c.expires_at > store.now(), store.officers.c.enabled == 1)).mappings().first()
    if not row or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in with your officer account.")
    return dict(row)

def logout(authorization):
    with store.engine.begin() as conn:
        conn.execute(delete(store.sessions).where(store.sessions.c.token_hash == hashlib.sha256(authorization.removeprefix("Bearer ").encode()).hexdigest()))
