"""Webhooks behavior; API dependencies are supplied by the route layer."""

from fastapi import HTTPException
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from .. import db
from ..paypal import PayPal, verified_payment
from .payments import fund


def process_webhook(headers, event):
    provider = PayPal()
    if not provider.verify(headers, event):
        raise HTTPException(401, "Webhook signature could not be verified.")
    with db.engine.connect() as conn:
        if conn.execute(select(db.webhook_events.c.id).where(db.webhook_events.c.id == event["id"])).first():
            return {"ok": True, "duplicate": True}
        resource = event.get("resource", {})
        # Invoicing webhook resources can wrap the invoice under resource.invoice.
        resource = resource.get("invoice", resource)
        row = conn.execute(select(db.orders).where(
            db.orders.c.invoice_id == resource.get("id"), db.orders.c.payment_mode == "sandbox",
        )).mappings().first()
        order = dict(row) if row else None
    reference = None
    if order and event.get("event_type") == "INVOICING.INVOICE.PAID":
        reference = verified_payment(provider.get(order["invoice_id"]), order)
    try:
        with db.engine.begin() as conn:
            conn.execute(insert(db.webhook_events).values(id=event["id"], received_at=db.now()))
            if reference:
                fund(conn, order, reference, "paypal-webhook")
    except IntegrityError:
        return {"ok": True, "duplicate": True}
    return {"ok": True}
