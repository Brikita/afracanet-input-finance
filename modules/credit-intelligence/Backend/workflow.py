"""An AI recommendation never creates a lender decision or a payment."""
import json
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import insert, select, update
from . import store

def scoped_application(conn, identifier, officer):
    row = conn.execute(select(store.applications).where(store.applications.c.id == identifier,
        store.applications.c.lender_id == officer["lender_id"]).with_for_update()).mappings().first()
    if not row:
        raise HTTPException(404, "Application not found in your lender workspace.")
    return row

def enqueue(conn, decision_id, officer, kind, handoff=None, reason=None):
    event_id = str(uuid.uuid4())
    payload = {"event_id": event_id, "kind": kind, "lender_id": officer["lender_id"],
        "officer_id": officer["id"], "approval_reference": decision_id,
        "handoff": handoff, "reason": reason}
    conn.execute(insert(store.outbox).values(id=event_id, decision_id=decision_id,
        lender_id=officer["lender_id"], kind=kind, body=json.dumps(payload, sort_keys=True, separators=(",", ":")),
        status="QUEUED", attempts=0, next_attempt=store.now(), lease_until=""))
    return event_id

def create_application(body, officer):
    values = {"id": str(uuid.uuid4()), "farmer_id": body.farmer_id, "input_farmer_id": body.input_farmer_id,
        "lender_id": officer["lender_id"], "status": "PENDING", "provenance": body.provenance,
        "created_at": store.now(), "request_id": body.request_id}
    with store.engine.begin() as conn:
        old = conn.execute(select(store.applications).where(store.applications.c.lender_id == officer["lender_id"],
            store.applications.c.request_id == body.request_id)).mappings().first()
        if old:
            if any(old[k] != values[k] for k in ("farmer_id", "input_farmer_id", "provenance")):
                raise HTTPException(409, "Request ID already has different application details.")
            return dict(old)
        conn.execute(insert(store.applications).values(**values))
    return values

def decide(identifier, body, officer):
    with store.engine.begin() as conn:
        application = scoped_application(conn, identifier, officer)
        old = conn.execute(select(store.decisions).where(store.decisions.c.application_id == identifier)).mappings().first()
        terms = body.model_dump(mode="json")
        encoded = json.dumps(terms, sort_keys=True)
        if old:
            if old["terms"] != encoded:
                raise HTTPException(409, "Application already decided. Create a new application for new terms.")
            return dict(old)
        if application["status"] != "PENDING":
            raise HTTPException(409, "Application is no longer pending.")
        if body.decision == "APPROVED" and (not body.limit_cents or not body.expires_at or body.expires_at <= datetime.now(timezone.utc)):
            raise HTTPException(422, "Approval needs an integer USD cent limit and future expiry.")
        if body.decision == "REJECTED" and (body.limit_cents is not None or body.expires_at is not None):
            raise HTTPException(422, "Rejected decisions cannot carry an allocation.")
        changed = conn.execute(update(store.applications).where(store.applications.c.id == identifier,
            store.applications.c.status == "PENDING").values(status=body.decision))
        if changed.rowcount != 1:
            raise HTTPException(409, "Application changed during review.")
        decision_id = str(uuid.uuid4())
        values = {"id": decision_id, "application_id": identifier, "lender_id": officer["lender_id"],
            "officer_id": officer["id"], "decision": body.decision, "terms": encoded,
            "reason": body.reason, "created_at": store.now(), "revoked_at": None, "revocation_reason": None}
        conn.execute(insert(store.decisions).values(**values))
        if body.decision == "APPROVED":
            handoff = {"schema_version": 1, "source_system": "afracanet-credit", "source_application_id": identifier,
                "source_farmer_id": application["farmer_id"], "farmer_id": application["input_farmer_id"],
                "lender_id": officer["lender_id"], "approval_reference": decision_id, "approved_by": officer["id"],
                "decision": "LENDER_APPROVED", "limit_cents": body.limit_cents, "currency": "USD",
                "approved_at": values["created_at"], "expires_at": body.expires_at.isoformat(),
                "data_provenance": application["provenance"]}
            enqueue(conn, decision_id, officer, "approval", handoff=handoff)
    return values

def revoke(identifier, reason, officer):
    with store.engine.begin() as conn:
        row = conn.execute(select(store.decisions).where(store.decisions.c.id == identifier,
            store.decisions.c.lender_id == officer["lender_id"]).with_for_update()).mappings().first()
        if not row:
            raise HTTPException(404, "Decision not found in your lender workspace.")
        if row["decision"] != "APPROVED":
            raise HTTPException(409, "Only an approved decision can be revoked.")
        if row["revoked_at"]:
            return {"status": "REVOKED"}
        changed = conn.execute(update(store.decisions).where(store.decisions.c.id == identifier,
            store.decisions.c.revoked_at.is_(None)).values(revoked_at=store.now(), revocation_reason=reason))
        if changed.rowcount == 1:
            conn.execute(update(store.applications).where(store.applications.c.id == row["application_id"]).values(status="REVOKED"))
            enqueue(conn, identifier, officer, "revocation", reason=reason)
    return {"status": "REVOKED"}
