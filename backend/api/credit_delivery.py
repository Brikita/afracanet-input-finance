"""Authenticated service channel. Public keys are lender-scoped operator config."""

import base64
import hashlib
import json
import time
from pathlib import Path
from typing import Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import insert, select, text, update

from .. import db
from ..config import settings
from ..contracts.handoffs import Handoff, HandoffApply, Revocation
from ..services import handoffs

router = APIRouter(prefix="/api/credit-deliveries", tags=["Signed credit decisions"])


class Delivery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(pattern=r"^[a-zA-Z0-9-]{16,80}$")
    kind: Literal["approval", "revocation"]
    lender_id: str = Field(min_length=1, max_length=100)
    officer_id: str = Field(min_length=1, max_length=100)
    approval_reference: str = Field(min_length=1, max_length=100)
    handoff: Handoff | None = None
    reason: str | None = Field(default=None, min_length=5, max_length=500)


def verify(raw, headers):
    if not settings.credit_trust_file:
        raise HTTPException(503, "The signed credit channel is not configured.")
    try:
        registry = json.loads(Path(settings.credit_trust_file).read_text())
        key = registry[headers.get("x-credit-key", "")]
        timestamp = headers["x-credit-time"]
        if abs(time.time() - int(timestamp)) > 300 or not key.get("enabled", False):
            raise ValueError()
        public = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(key["public_key"], validate=True)
        )
        message = (
            b"AFRACANET-CREDIT-V1\nPOST\n/api/credit-deliveries\n"
            + timestamp.encode()
            + b"\n"
            + raw
        )
        public.verify(
            base64.b64decode(headers["x-credit-signature"], validate=True), message
        )
        return key
    except (KeyError, ValueError, InvalidSignature):
        raise HTTPException(
            401, "Invalid, disabled, or expired service signature."
        ) from None


@router.post("")
async def receive(request: Request):
    raw = b""
    async for chunk in request.stream():
        raw += chunk
        if len(raw) > 16384:
            raise HTTPException(413, "Decision delivery exceeds the size limit.")
    key = verify(raw, request.headers)
    try:
        body = Delivery.model_validate_json(raw)
    except ValidationError:
        raise HTTPException(422, "Invalid decision delivery contract.") from None
    if body.lender_id != key["lender_id"] or body.officer_id not in key["officer_ids"]:
        raise HTTPException(
            403, "The signing service is not authorized for this lender/officer."
        )
    if body.kind == "approval":
        d = body.handoff
        if not d or (d.lender_id, d.approved_by, d.approval_reference) != (
            body.lender_id,
            body.officer_id,
            body.approval_reference,
        ):
            raise HTTPException(422, "Envelope and lender decision must agree.")
    elif not body.reason or body.handoff is not None:
        raise HTTPException(
            422, "Revocation requires a reason and no approval payload."
        )
    digest = hashlib.sha256(raw).hexdigest()
    user = {"role": "lender", "subject": body.lender_id}
    with db.engine.begin() as conn:
        receipt = (
            conn.execute(
                select(db.credit_receipts).where(
                    db.credit_receipts.c.event_id == body.event_id
                )
            )
            .mappings()
            .first()
        )
        if receipt:
            if receipt["body_hash"] != digest or receipt["lender_id"] != body.lender_id:
                raise HTTPException(
                    409, "Delivery ID already contains different content."
                )
            return receipt["response"]
        # Reserve the receipt before reading business state. SQLite writers serialize;
        # PostgreSQL also serializes approval/revocation for the same reference.
        conn.execute(
            insert(db.credit_receipts).values(
                event_id=body.event_id,
                lender_id=body.lender_id,
                body_hash=digest,
                response={},
                received_at=db.now(),
            )
        )
        if conn.dialect.name == "postgresql":
            lock_id = int.from_bytes(
                hashlib.sha256(
                    (body.lender_id + "\0" + body.approval_reference).encode()
                ).digest()[:8],
                "big",
                signed=True,
            )
            conn.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_id})
        revoked = (
            conn.execute(
                select(db.credit_revocations).where(
                    db.credit_revocations.c.lender_id == body.lender_id,
                    db.credit_revocations.c.approval_reference
                    == body.approval_reference,
                )
            )
            .mappings()
            .first()
        )
        if body.kind == "approval":
            if revoked:
                raise HTTPException(
                    409, "This decision was revoked; a new lender decision is required."
                )
            result = handoffs.apply_in_transaction(
                conn,
                HandoffApply(
                    handoff=body.handoff,
                    allocation_revision="0" * 64,
                    confirm_lender_authorization=True,
                ),
                user,
                authenticated=True,
            )
            response = {
                "event_id": body.event_id,
                "status": "recorded",
                "handoff_id": result["record"]["id"],
                "source_authentication": "signed_service",
            }
        else:
            if not revoked:
                conn.execute(
                    insert(db.credit_revocations).values(
                        lender_id=body.lender_id,
                        approval_reference=body.approval_reference,
                        reason=body.reason,
                        officer_id=body.officer_id,
                        received_at=db.now(),
                    )
                )
            record = (
                conn.execute(
                    select(db.approval_handoffs).where(
                        db.approval_handoffs.c.lender_id == body.lender_id,
                        db.approval_handoffs.c.approval_reference
                        == body.approval_reference,
                        db.approval_handoffs.c.source_system == "afracanet-credit",
                    )
                )
                .mappings()
                .first()
            )
            if record:
                handoffs.revoke_in_transaction(
                    conn, record["id"], Revocation(reason=body.reason), user
                )
            response = {
                "event_id": body.event_id,
                "status": "revoked",
                "handoff_id": record["id"] if record else None,
            }
        conn.execute(
            update(db.credit_receipts)
            .where(db.credit_receipts.c.event_id == body.event_id)
            .values(response=response)
        )
        return response
