"""Transactional SMS outbox. No real handset delivery; demo or AT sandbox only."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import insert, select, update

from . import db
from .config import settings


class ContactRequest(BaseModel):
    phone: str = Field(pattern=r"^\+254[17][0-9]{8}$")
    language: Literal["en", "sw"] = "en"
    consent: bool


class VerifyRequest(BaseModel):
    code: str = Field(pattern=r"^[0-9]{6}$")


def queue(conn, farmer_id, phone, action, body, event_key, order_id=None):
    conn.execute(insert(db.sms_outbox).values(
        farmer_id=farmer_id, order_id=order_id, event_key=event_key, action=action,
        phone=phone, body=body, mode=settings.sms_mode, status="QUEUED",
        created_at=db.now(), updated_at=db.now(),
    ))


def save_contact(user, body):
    farmer_id = user["subject"]
    with db.engine.begin() as conn:
        existing = conn.execute(select(db.contacts).where(db.contacts.c.farmer_id == farmer_id)).mappings().first()
        verified = existing and existing["phone"] == body.phone and existing["verified_at"] and existing["consented_at"] and existing["verification_mode"] == settings.sms_mode
        if body.consent and not verified and existing and existing["updated_at"] > (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat():
            raise HTTPException(429, "Wait one minute before requesting another verification code.")
        values = {"phone": body.phone, "language": body.language, "consented_at": db.now() if body.consent else None,
                  "verified_at": existing["verified_at"] if verified and body.consent else None,
                  "verification_hash": None, "verification_expires_at": None, "verification_attempts": 0,
                  "verification_mode": settings.sms_mode, "updated_at": db.now()}
        code = None
        if body.consent and not verified:
            code = str(secrets.randbelow(900000) + 100000)
            values.update(verification_hash=hashlib.sha256(code.encode()).hexdigest(),
                          verification_expires_at=(datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat())
        if existing:
            conn.execute(update(db.contacts).where(db.contacts.c.farmer_id == farmer_id).values(**values))
        else:
            conn.execute(insert(db.contacts).values(farmer_id=farmer_id, **values))
        conn.execute(update(db.sms_outbox).where(db.sms_outbox.c.farmer_id == farmer_id, db.sms_outbox.c.status == "QUEUED").values(
            status="SUPPRESSED", detail="Contact settings changed.", updated_at=db.now(),
        ))
        if code:
            text = f"AFRACANet: nambari ya kuthibitisha {code}. Inaisha baada ya dakika 10." if body.language == "sw" else f"AFRACANet: your verification code is {code}. Expires in 10 minutes."
            queue(conn, farmer_id, body.phone, "VERIFY_CONTACT", text, "verify:" + secrets.token_hex(16))
        conn.execute(insert(db.management_events).values(actor=farmer_id, action="SMS_CONTACT_UPDATED",
            detail={"language": body.language, "consent": body.consent, "verification_required": bool(code)}, created_at=db.now()))
    return {"message": "Verification SMS queued. Dispatch it, then enter its code." if code else "SMS preferences saved."}


def verify_contact(user, body):
    # Failed attempts must commit rather than roll back with the HTTP error.
    error = None
    with db.engine.begin() as conn:
        conn.execute(update(db.contacts).where(db.contacts.c.farmer_id == user["subject"]).values(
            verification_attempts=db.contacts.c.verification_attempts + 1,
        ))
        contact = conn.execute(select(db.contacts).where(db.contacts.c.farmer_id == user["subject"])).mappings().first()
        if not contact or contact["verification_mode"] != settings.sms_mode or not contact["consented_at"] or not contact["verification_hash"] or not contact["verification_expires_at"] or contact["verification_expires_at"] <= db.now():
            error = "Request a new, unexpired verification code."
        elif contact["verification_attempts"] > 5:
            error = "Too many attempts. Request a new verification code."
        elif not secrets.compare_digest(contact["verification_hash"], hashlib.sha256(body.code.encode()).hexdigest()):
            error = "The verification code does not match."
        else:
            conn.execute(update(db.contacts).where(db.contacts.c.farmer_id == user["subject"]).values(
                verified_at=db.now(), verification_hash=None, verification_expires_at=None,
            ))
    if error:
        raise HTTPException(422, error)
    return {"message": "Phone verified. Future order updates can be queued for this number."}


def render_event(conn, order, action, language):
    reference = f"AFC-{order['id']:06d}"
    held = conn.execute(select(db.issues.c.id).where(db.issues.c.order_id == order["id"], db.issues.c.resolved_at.is_(None)).limit(1)).first()
    prefix = "AFRACANet " + reference + ": " + ("[DEMO] " if order["payment_mode"] == "mock" else "[PAYPAL SANDBOX] ")
    if action in {"PAYMENT_CONFIRMED", "ISSUE_RESOLVED"} and order["status"] == "READY_FOR_COLLECTION" and not held:
        if language == "sw":
            return prefix + f"malipo yamethibitishwa. Nambari ya kuchukua pembejeo: {order['pickup_code']}. Mpe muuzaji unapochukua."
        return prefix + f"payment confirmed. Collection code: {order['pickup_code']}. Share with the dealer when collecting."
    messages = {
        "REQUESTED": ("request received; awaiting lender approval.", "ombi limepokelewa; subiri idhini ya mkopeshaji."),
        "APPROVED": ("order approved; awaiting supplier invoice.", "ombi limeidhinishwa; subiri ankara ya muuzaji."),
        "PAYMENT_CONFIRMED": ("payment recorded. An issue needs lender review before collection.", "malipo yamerekodiwa. Tatizo linahitaji ukaguzi wa mkopeshaji kabla ya kuchukua."),
        "ISSUE_REPORTED": ("an issue was reported. Contact your lender; collection is on hold.", "tatizo limeripotiwa. Wasiliana na mkopeshaji; kuchukua pembejeo kumesitishwa."),
        "ISSUE_RESOLVED": ("an issue resolution was recorded. Check your order for the next step.", "suluhisho la tatizo limerekodiwa. Angalia hatua inayofuata katika ombi lako."),
        "CANCELLED": ("order cancelled; reserved credit released.", "ombi limeghairiwa; mkopo uliotengwa umerudishwa."),
        "COLLECTED": ("the dealer recorded collection. Report any problem in your workspace.", "muuzaji amerekodi uchukuaji. Ripoti tatizo lolote kwenye akaunti yako."),
    }
    if action not in messages:
        return None
    text = messages[action][1 if language == "sw" else 0]
    # Every message clearly identifies simulated financial events.
    return prefix + text


def enqueue_event(conn, order_id, event_id, action):
    order = conn.execute(select(db.orders).where(db.orders.c.id == order_id)).mappings().one()
    contact = conn.execute(select(db.contacts).where(db.contacts.c.farmer_id == order["farmer_id"])).mappings().first()
    if not contact or not contact["consented_at"] or not contact["verified_at"] or contact["verification_mode"] != settings.sms_mode:
        return
    body = render_event(conn, order, action, contact["language"])
    if body:
        queue(conn, order["farmer_id"], contact["phone"], action, body, f"audit:{event_id}", order_id)


def sandbox_send(phone, body):
    try:
        with httpx.Client(timeout=20) as client:
            response = client.post("https://api.sandbox.africastalking.com/version1/messaging",
                headers={"apiKey": settings.sms_key, "Accept": "application/json"},
                data={"username": "sandbox", "to": phone, "message": body, "bulkSMSMode": 1,
                      **({"from": settings.sms_sender} if settings.sms_sender else {})})
        response.raise_for_status()
        recipients = response.json()["SMSMessageData"]["Recipients"]
        if len(recipients) != 1 or recipients[0]["number"] != phone:
            return "UNCERTAIN", None, "Unexpected provider recipient response. Review the sandbox dashboard."
        recipient = recipients[0]
        if recipient.get("statusCode") != 101:
            return "REJECTED", None, "Provider rejected the message. Review configuration before a new send."
        if not isinstance(recipient.get("messageId"), str) or not recipient["messageId"]:
            return "UNCERTAIN", None, "Provider acceptance reference missing. Do not retry automatically."
        return "ACCEPTED", recipient["messageId"], "Accepted by the sandbox gateway; this is not handset delivery."
    except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError):
        return "UNCERTAIN", None, "The send outcome could not be confirmed. Review provider records before another send."


def dispatch_one(message_id, farmer_id=None):
    with db.engine.begin() as conn:
        filters = [db.sms_outbox.c.id == message_id, db.sms_outbox.c.status == "QUEUED"]
        if farmer_id:
            filters.append(db.sms_outbox.c.farmer_id == farmer_id)
        claimed = conn.execute(update(db.sms_outbox).where(*filters).values(status="SENDING", updated_at=db.now()))
        if claimed.rowcount != 1:
            return False
        message = dict(conn.execute(select(db.sms_outbox).where(db.sms_outbox.c.id == message_id)).mappings().one())
        contact = conn.execute(select(db.contacts).where(db.contacts.c.farmer_id == message["farmer_id"])).mappings().one()
        reason = None
        if message["mode"] != settings.sms_mode:
            reason = "Message mode differs from current configuration."
        elif not contact["consented_at"] or contact["phone"] != message["phone"]:
            reason = "Consent or phone number changed."
        elif message["action"] == "VERIFY_CONTACT":
            if not contact["verification_hash"] or contact["verification_expires_at"] <= db.now():
                reason = "Verification expired or is no longer needed."
        elif not contact["verified_at"] or contact["verification_mode"] != settings.sms_mode:
            reason = "Phone has not been verified."
        else:
            order = conn.execute(select(db.orders).where(db.orders.c.id == message["order_id"])).mappings().one()
            expected = {"REQUESTED": "REQUESTED", "APPROVED": "APPROVED", "COLLECTED": "COLLECTED", "CANCELLED": "CANCELLED"}
            if message["action"] == "PAYMENT_CONFIRMED" and order["status"] != "READY_FOR_COLLECTION":
                reason = "The order has moved past payment readiness."
            if message["action"] == "ISSUE_REPORTED" and not conn.execute(select(db.issues.c.id).where(db.issues.c.order_id == order["id"], db.issues.c.resolved_at.is_(None)).limit(1)).first():
                reason = "The reported issues have been resolved."
            if message["action"] in expected and order["status"] != expected[message["action"]]:
                reason = "The order has moved past this update."
            else:
                message["body"] = render_event(conn, order, message["action"], contact["language"])
        if reason:
            conn.execute(update(db.sms_outbox).where(db.sms_outbox.c.id == message_id).values(status="SUPPRESSED", detail=reason, updated_at=db.now()))
            return True
        conn.execute(update(db.sms_outbox).where(db.sms_outbox.c.id == message_id).values(body=message["body"]))
    # Do not hold a database transaction over provider requests.
    if settings.sms_mode == "demo":
        status, provider_id, detail = "SIMULATED", None, "Local preview only. No SMS API call or handset delivery."
    else:
        status, provider_id, detail = sandbox_send(message["phone"], message["body"])
    with db.engine.begin() as conn:
        conn.execute(update(db.sms_outbox).where(db.sms_outbox.c.id == message_id, db.sms_outbox.c.status == "SENDING").values(
            status=status, provider_id=provider_id, detail=detail, updated_at=db.now(),
        ))
    return True


def dispatch_pending(farmer_id=None, limit=20):
    with db.engine.connect() as conn:
        query = select(db.sms_outbox.c.id).where(db.sms_outbox.c.status == "QUEUED").order_by(db.sms_outbox.c.id).limit(limit)
        if farmer_id:
            query = query.where(db.sms_outbox.c.farmer_id == farmer_id)
        ids = conn.execute(query).scalars().all()
    return sum(dispatch_one(message_id, farmer_id) for message_id in ids)


def preferences(user):
    with db.engine.connect() as conn:
        contact = conn.execute(select(db.contacts).where(db.contacts.c.farmer_id == user["subject"])).mappings().first()
        rows = conn.execute(select(db.sms_outbox).where(db.sms_outbox.c.farmer_id == user["subject"]).order_by(db.sms_outbox.c.id.desc()).limit(30)).mappings().all()
    public = {key: contact[key] for key in ["phone", "language", "consented_at", "verified_at"]} if contact else None
    if public and contact["verification_mode"] != settings.sms_mode:
        public["verified_at"] = None
    messages = []
    for row in rows:
        item = dict(row)
        item.pop("phone")
        # Codes are shown in local previews only; sandbox verification must use the simulator.
        if settings.sms_mode != "demo" or row["mode"] != "demo" or row["status"] != "SIMULATED":
            item.pop("body")
        messages.append(item)
    return {"contact": public, "messages": messages, "mode": settings.sms_mode}
