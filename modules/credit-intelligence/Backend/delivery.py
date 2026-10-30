"""Durable, leased deliveries. Signing and HTTP calls never hold DB transactions."""
import base64
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import httpx
from cryptography.hazmat.primitives import serialization
from sqlalchemy import select, update
from . import store

def headers(body):
    key = serialization.load_pem_private_key(Path(os.environ["CREDIT_SIGNING_KEY_FILE"]).read_bytes(), password=None)
    timestamp = str(int(time.time()))
    signature = key.sign(b"AFRACANET-CREDIT-V1\nPOST\n/api/credit-deliveries\n" + timestamp.encode() + b"\n" + body)
    return {"Content-Type": "application/json", "X-Credit-Key": json.loads(os.environ.get("CREDIT_SIGNING_KEY_IDS", "{}" )).get(json.loads(body)["lender_id"], os.environ.get("CREDIT_SIGNING_KEY_ID", "")),
        "X-Credit-Time": timestamp, "X-Credit-Signature": base64.b64encode(signature).decode()}

def dispatch(event_id, lender_id, transport=None):
    now = store.now()
    with store.engine.begin() as conn:
        claimed = conn.execute(update(store.outbox).where(store.outbox.c.id == event_id,
            store.outbox.c.lender_id == lender_id, store.outbox.c.status != "DELIVERED",
            store.outbox.c.next_attempt <= now, store.outbox.c.lease_until < now).values(
                lease_until=(datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat(), attempts=store.outbox.c.attempts + 1))
        row = conn.execute(select(store.outbox).where(store.outbox.c.id == event_id, store.outbox.c.lender_id == lender_id)).mappings().first()
        if not row:
            return None
        if claimed.rowcount != 1:
            return {"status": row["status"], "event_id": event_id, "retry_at": row["next_attempt"]}
    try:
        raw = row["body"].encode()
        url = os.environ["INPUT_FINANCE_URL"].rstrip("/")
        if not (url.startswith("https://") or url.startswith("http://127.0.0.1:") or url.startswith("http://localhost:")):
            raise ValueError("Use HTTPS or a loopback development receiver.")
        with httpx.Client(timeout=20, transport=transport, follow_redirects=False) as client:
            response = client.post(url + "/api/credit-deliveries", content=raw, headers=headers(raw))
        response.raise_for_status()
        receipt = response.json()
        if receipt.get("event_id") != event_id or receipt.get("status") != ("recorded" if row["kind"] == "approval" else "revoked"):
            raise ValueError("Receiver acknowledgment does not match delivery.")
        values = {"status": "DELIVERED", "receipt": json.dumps(receipt), "last_error": None, "lease_until": ""}
    except Exception as exc:
        # Do not persist URLs, keys, raw provider bodies, or credential-bearing errors.
        code = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
        error = f"Receiver HTTP {code}" if code else type(exc).__name__
        values = {"status": "RETRY", "last_error": error, "lease_until": "",
            "next_attempt": (datetime.now(timezone.utc) + timedelta(seconds=min(3600, 5 * 2 ** min(row["attempts"], 9)))).isoformat()}
    with store.engine.begin() as conn:
        conn.execute(update(store.outbox).where(store.outbox.c.id == event_id).values(**values))
    return {"event_id": event_id, "status": values["status"], "error": values.get("last_error")}

def tick():
    with store.engine.connect() as conn:
        rows = conn.execute(select(store.outbox.c.id, store.outbox.c.lender_id).where(
            store.outbox.c.status != "DELIVERED", store.outbox.c.next_attempt <= store.now(),
            store.outbox.c.lease_until < store.now()).limit(20)).all()
    for event_id, lender_id in rows:
        dispatch(event_id, lender_id)
