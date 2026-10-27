"""Reviewed lender handoffs. Source assertions are retained, never authenticated by a file."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import insert, select, update

from . import db
from .management import log

SOURCE = "afracanet-credit"


class MappingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    source_system: Literal["afracanet-credit"] = SOURCE
    source_farmer_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
    farmer_id: str = Field(pattern=r"^farmer-[a-z0-9][a-z0-9-]{0,59}$")


class Handoff(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    schema_version: int = Field(strict=True, ge=1, le=1)
    source_system: Literal["afracanet-credit"]
    source_application_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
    source_farmer_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
    farmer_id: str = Field(pattern=r"^farmer-[a-z0-9][a-z0-9-]{0,59}$")
    lender_id: str = Field(min_length=1, max_length=100)
    approval_reference: str = Field(min_length=1, max_length=100)
    approved_by: str = Field(min_length=1, max_length=100)
    decision: Literal["LENDER_APPROVED"]
    limit_cents: int = Field(strict=True, ge=1, le=100_000_000)
    currency: Literal["USD"]
    approved_at: datetime
    expires_at: datetime
    data_provenance: Literal["synthetic", "real", "mixed", "unavailable"]

    @field_validator("lender_id", "approval_reference", "approved_by")
    @classmethod
    def nonblank(cls, value):
        if not value:
            raise ValueError("Must not be blank")
        return value

    @field_validator("approved_at", "expires_at")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None:
            raise ValueError("Use a timestamp with a timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def ordered_dates(self):
        if self.expires_at <= self.approved_at:
            raise ValueError("Expiry must follow the lender decision")
        return self


class HandoffApply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Handoff
    allocation_revision: str = Field(pattern=r"^[a-f0-9]{64}$")
    confirm_lender_authorization: Literal[True]

    @field_validator("confirm_lender_authorization", mode="before")
    @classmethod
    def explicit_confirmation(cls, value):
        if value is not True:
            raise ValueError("Explicit lender confirmation is required")
        return value


class Revocation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    reason: str = Field(min_length=5, max_length=500)


def allocation_revision(farmer):
    # Reservations can change after preview; compare them atomically at apply.
    fields = ("id", "lender_id", "limit_cents", "expires_at", "approval_reference")
    return hashlib.sha256(json.dumps({k: farmer[k] for k in fields}, sort_keys=True).encode()).hexdigest()


def payload_hash(body):
    return hashlib.sha256(json.dumps(body.model_dump(mode="json"), sort_keys=True).encode()).hexdigest()


def check_lender(body, user):
    if body.lender_id != user["subject"]:
        raise HTTPException(403, "The decision must belong to your signed-in lender.")


def mapped_farmer(conn, body, user, *, lock=False):
    mapping = conn.execute(select(db.approval_mappings).where(
        db.approval_mappings.c.lender_id == user["subject"],
        db.approval_mappings.c.source_system == body.source_system,
        db.approval_mappings.c.source_farmer_id == body.source_farmer_id,
        db.approval_mappings.c.farmer_id == body.farmer_id,
    )).mappings().first()
    if not mapping:
        raise HTTPException(409, "Confirm this source farmer's mapping before reviewing a decision.")
    query = select(db.farmers).where(
        db.farmers.c.id == body.farmer_id, db.farmers.c.lender_id == user["subject"],
    )
    farmer = conn.execute(query.with_for_update() if lock else query).mappings().first()
    if not farmer:
        raise HTTPException(404, "Mapped farmer not found in your lender workspace.")
    return mapping, farmer


def existing_handoff(conn, body, user):
    existing = conn.execute(select(db.approval_handoffs).where(
        db.approval_handoffs.c.lender_id == user["subject"],
        db.approval_handoffs.c.source_system == body.source_system,
        db.approval_handoffs.c.approval_reference == body.approval_reference,
    )).mappings().first()
    if existing and existing["payload_hash"] != payload_hash(body):
        raise HTTPException(409, "That decision reference already contains different terms. Use a new lender decision.")
    return existing


def validate_current(conn, body, farmer):
    now = datetime.now(timezone.utc)
    if body.approved_at > now or body.expires_at <= now:
        raise HTTPException(422, "Use an existing lender decision and a future expiry.")
    committed = farmer["reserved_cents"] + farmer["spent_cents"]
    if body.limit_cents < committed:
        raise HTTPException(409, "The allocation cannot be below reserved and already paid credit.")
    latest = conn.execute(select(db.approval_handoffs.c.approved_at).where(
        db.approval_handoffs.c.farmer_id == farmer["id"],
    ).order_by(db.approval_handoffs.c.approved_at.desc()).limit(1)).scalar_one_or_none()
    if latest and body.approved_at <= datetime.fromisoformat(latest):
        raise HTTPException(409, "A newer or simultaneous decision is already recorded for this farmer.")


def mappings(user):
    with db.engine.connect() as conn:
        return [dict(row) for row in conn.execute(select(db.approval_mappings).where(
            db.approval_mappings.c.lender_id == user["subject"],
        ).order_by(db.approval_mappings.c.created_at.desc())).mappings()]


def save_mapping(body, user):
    with db.engine.begin() as conn:
        farmer = conn.execute(select(db.farmers.c.id).where(
            db.farmers.c.id == body.farmer_id, db.farmers.c.lender_id == user["subject"],
        )).first()
        if not farmer:
            raise HTTPException(404, "Choose an existing farmer in your lender workspace. Import their profile first if needed.")
        existing = conn.execute(select(db.approval_mappings).where(
            db.approval_mappings.c.lender_id == user["subject"],
            db.approval_mappings.c.source_system == body.source_system,
            (db.approval_mappings.c.source_farmer_id == body.source_farmer_id)
            | (db.approval_mappings.c.farmer_id == body.farmer_id),
        )).mappings().first()
        if existing:
            if existing["source_farmer_id"] != body.source_farmer_id or existing["farmer_id"] != body.farmer_id:
                raise HTTPException(409, "One of these IDs is already mapped. Mappings cannot be silently reassigned.")
            return dict(existing)
        values = {"id": str(uuid.uuid4()), **body.model_dump(), "lender_id": user["subject"],
                  "recorded_by": user["subject"], "created_at": db.now()}
        conn.execute(insert(db.approval_mappings).values(**values))
        log(conn, user, "APPROVAL_MAPPING_CONFIRMED", values)
        return values


def preview(body, user):
    check_lender(body, user)
    with db.engine.connect() as conn:
        _, farmer = mapped_farmer(conn, body, user)
        existing = existing_handoff(conn, body, user)
        if not existing:
            validate_current(conn, body, farmer)
        return {"handoff": body.model_dump(mode="json"), "farmer_name": farmer["name"],
                "allocation_revision": allocation_revision(farmer), "already_recorded": bool(existing),
                "revoked": bool(existing and existing["revoked_at"]),
                "current_limit_cents": farmer["limit_cents"],
                "committed_cents": farmer["reserved_cents"] + farmer["spent_cents"],
                "transfer_method": "manual_lender_review", "source_authentication": "not_verified"}


def apply(body, user):
    decision = body.handoff
    check_lender(decision, user)
    with db.engine.begin() as conn:
        mapping, farmer = mapped_farmer(conn, decision, user, lock=True)
        existing = existing_handoff(conn, decision, user)
        # Exact retries never restore an old limit, extend expiry, or undo revocation.
        if existing:
            return {"record": dict(existing), "already_recorded": True,
                    "message": "Decision already recorded. The current allocation was not changed."}
        if body.allocation_revision != allocation_revision(farmer):
            raise HTTPException(409, "The allocation changed after preview. Review the decision again.")
        validate_current(conn, decision, farmer)
        changed = conn.execute(update(db.farmers).where(
            db.farmers.c.id == farmer["id"], db.farmers.c.lender_id == user["subject"],
            db.farmers.c.limit_cents == farmer["limit_cents"],
            db.farmers.c.approval_reference == farmer["approval_reference"],
            db.farmers.c.expires_at == farmer["expires_at"],
            db.farmers.c.reserved_cents + db.farmers.c.spent_cents <= decision.limit_cents,
        ).values(limit_cents=decision.limit_cents, expires_at=decision.expires_at.isoformat(),
                 approval_reference=decision.approval_reference))
        if changed.rowcount != 1:
            raise HTTPException(409, "Credit changed during confirmation. Preview and retry.")
        values = {"id": str(uuid.uuid4()), "mapping_id": mapping["id"], "lender_id": user["subject"],
                  "farmer_id": decision.farmer_id, "source_system": decision.source_system,
                  "approval_reference": decision.approval_reference, "approved_at": decision.approved_at.isoformat(),
                  "payload_hash": payload_hash(decision), "payload": decision.model_dump(mode="json"),
                  "transfer_method": "manual_lender_review", "recorded_by": user["subject"], "received_at": db.now(),
                  "revoked_at": None, "revoked_by": None, "revocation_reason": None}
        conn.execute(insert(db.approval_handoffs).values(**values))
        log(conn, user, "APPROVAL_HANDOFF_RECORDED", {"handoff_id": values["id"],
            "approval_reference": decision.approval_reference, "farmer_id": decision.farmer_id,
            "source_authentication": "not_verified", "transfer_method": values["transfer_method"]})
        return {"record": values, "already_recorded": False,
                "message": "Lender-reviewed decision recorded. Reserved and paid credit were preserved."}


def history(user):
    with db.engine.connect() as conn:
        return [dict(row) for row in conn.execute(select(db.approval_handoffs).where(
            db.approval_handoffs.c.lender_id == user["subject"],
        ).order_by(db.approval_handoffs.c.received_at.desc()).limit(100)).mappings()]


def allocation_trace(conn, farmer_id):
    farmer = conn.execute(select(db.farmers).where(db.farmers.c.id == farmer_id)).mappings().one()
    linked = conn.execute(select(db.approval_handoffs).where(
        db.approval_handoffs.c.farmer_id == farmer_id,
        db.approval_handoffs.c.lender_id == farmer["lender_id"],
        db.approval_handoffs.c.approval_reference == farmer["approval_reference"],
    )).mappings().first()
    detail = f" Allocation reference: {farmer['approval_reference']}."
    if linked:
        detail += (f" Reviewed handoff: {linked['id']}; source application: "
                   f"{linked['payload']['source_application_id']}; manual lender review; source file not independently authenticated.")
    return detail


def revoke(handoff_id, body, user):
    with db.engine.begin() as conn:
        row = conn.execute(select(db.approval_handoffs).where(
            db.approval_handoffs.c.id == handoff_id, db.approval_handoffs.c.lender_id == user["subject"],
        )).mappings().first()
        if not row:
            raise HTTPException(404, "Decision not found in your lender workspace.")
        # Use the same farmer lock order as apply; re-read the revocation after it.
        conn.execute(select(db.farmers.c.id).where(db.farmers.c.id == row["farmer_id"]).with_for_update()).first()
        changed = conn.execute(update(db.approval_handoffs).where(
            db.approval_handoffs.c.id == handoff_id, db.approval_handoffs.c.revoked_at.is_(None),
        ).values(revoked_at=db.now(), revoked_by=user["subject"], revocation_reason=body.reason))
        if changed.rowcount == 1:
            conn.execute(update(db.farmers).where(
                db.farmers.c.id == row["farmer_id"], db.farmers.c.lender_id == user["subject"],
                db.farmers.c.approval_reference == row["approval_reference"],
            ).values(expires_at=db.now()))
            log(conn, user, "APPROVAL_HANDOFF_REVOKED", {"handoff_id": handoff_id, "reason": body.reason})
    return {"message": "Decision revoked. New requests and further approvals/invoicing are blocked for its current allocation. Existing invoices and payments need separate reconciliation; paid credit and collection records are preserved."}
