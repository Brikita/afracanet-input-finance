"""Payments behavior; API dependencies are supplied by the route layer."""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select, update

from .. import db
from ..auth import require
from ..config import settings
from ..contracts.requests import RecoveryRequest
from ..integrations.paypal import (
    PaymentError,
    PayPal,
    cancelled_without_payment,
    matching_invoice,
    payment_link,
    verified_payment,
)
from .orders import get_order, release_reservations, require_no_issues, transition


def invoice(order_id: int, user):
    require(user, "supplier")
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user, lock=True)
        if order["status"] == "AWAITING_PAYMENT":
            return {"ok": True}
        if order["status"] != "APPROVED":
            raise HTTPException(
                409, "The lender must approve this order before invoicing."
            )
        require_no_issues(conn, order_id)
        if order["payment_mode"] != settings.payment_mode:
            raise HTTPException(
                409, "This order uses a different payment mode. Create a new order."
            )
        approval = conn.execute(
            select(db.farmers.c.expires_at)
            .where(
                db.farmers.c.id == order["farmer_id"],
            )
            .with_for_update()
        ).scalar_one()
        if approval <= db.now():
            raise HTTPException(409, "The farmer's credit approval has expired.")
        transition(conn, order, "APPROVED", "INVOICING")
    try:
        if order["payment_mode"] == "mock":
            invoice_id, payment_url = f"DEMO-INV-{order_id:06d}", None
        else:
            provider = PayPal()
            invoice_id = provider.create(order)
            # Persist the remote reference before sending, for recovery after send failure.
            with db.engine.begin() as conn:
                conn.execute(
                    update(db.orders)
                    .where(db.orders.c.id == order_id)
                    .values(invoice_id=invoice_id)
                )
            payment_url = provider.send(invoice_id)
        with db.engine.begin() as conn:
            conn.execute(
                update(db.orders)
                .where(
                    db.orders.c.id == order_id,
                    db.orders.c.status == "INVOICING",
                )
                .values(
                    invoice_id=invoice_id,
                    payment_url=payment_url,
                    status="AWAITING_PAYMENT",
                    updated_at=db.now(),
                )
            )
            db.record(
                conn,
                order_id,
                user["subject"],
                "INVOICED",
                "Supplier confirmed stock and price; invoice sent to lender."
                if order["payment_mode"] == "sandbox"
                else "Supplier confirmed stock and price; simulated invoice created. No PayPal API call.",
            )
    except PaymentError:
        with db.engine.begin() as conn:
            changed = conn.execute(
                update(db.orders)
                .where(
                    db.orders.c.id == order_id,
                    db.orders.c.status == "INVOICING",
                )
                .values(status="PAYMENT_REVIEW", updated_at=db.now())
            )
            if changed.rowcount == 1:
                db.record(
                    conn,
                    order_id,
                    "system",
                    "PAYMENT_REVIEW",
                    "Invoice creation or sending could not be confirmed. Review provider records before retrying.",
                )
        raise
    return {"ok": True}


def fund(conn, order, reference, who):
    changed = conn.execute(
        update(db.orders)
        .where(
            db.orders.c.id == order["id"],
            db.orders.c.status.in_(["AWAITING_PAYMENT", "PAYMENT_REVIEW", "INVOICING"]),
        )
        .values(
            status="READY_FOR_COLLECTION",
            payment_reference=reference,
            pickup_code=str(secrets.randbelow(900000) + 100000),
            updated_at=db.now(),
        )
    )
    if changed.rowcount != 1:
        return False
    conn.execute(
        update(db.farmers)
        .where(db.farmers.c.id == order["farmer_id"])
        .values(
            reserved_cents=db.farmers.c.reserved_cents - order["amount_cents"],
            spent_cents=db.farmers.c.spent_cents + order["amount_cents"],
        )
    )
    db.record(
        conn,
        order["id"],
        who,
        "PAYMENT_CONFIRMED",
        "PayPal payment reconciled against invoice amount and currency."
        if order["payment_mode"] == "sandbox"
        else "Simulated payment confirmed. No money moved.",
    )
    return True


def recover_invoice(order_id: int, body: RecoveryRequest, user):
    require(user, "supplier")
    with db.engine.connect() as conn:
        order = get_order(conn, order_id, user)
    if settings.payment_mode != "sandbox" or order["payment_mode"] != "sandbox":
        raise HTTPException(
            409, "Recovery requires the matching PayPal sandbox configuration."
        )
    if order["status"] not in {"PAYMENT_REVIEW", "INVOICING", "AWAITING_PAYMENT"}:
        raise HTTPException(409, "Only an unresolved invoice can be recovered.")
    if order["status"] == "INVOICING" and datetime.fromisoformat(
        order["updated_at"]
    ) > datetime.now(timezone.utc) - timedelta(minutes=2):
        raise HTTPException(
            409,
            "Invoice preparation may still be running. Wait two minutes before recovery.",
        )
    if (
        order["invoice_id"]
        and body.invoice_id
        and body.invoice_id != order["invoice_id"]
    ):
        raise HTTPException(409, "Use the invoice already linked to this order.")
    invoice_id = order["invoice_id"] or body.invoice_id
    if not invoice_id:
        raise HTTPException(
            422,
            "Find the existing invoice in the supplier's PayPal records and enter its INV2 reference.",
        )
    candidate = {**order, "invoice_id": invoice_id}
    remote = PayPal().get(invoice_id)
    if not matching_invoice(remote, candidate):
        raise HTTPException(
            409,
            "The invoice does not match this order's reference, supplier, lender, amount, and currency.",
        )
    reference = verified_payment(remote, candidate)
    cancelled = cancelled_without_payment(remote, candidate)
    awaiting = remote.get("status") in {"SENT", "UNPAID"}
    url = payment_link(remote) if awaiting else None
    with db.engine.begin() as conn:
        current = get_order(conn, order_id, user)
        if current["status"] in {"READY_FOR_COLLECTION", "COLLECTED"}:
            return {"message": "Payment was already confirmed."}
        if current["status"] == "CANCELLED":
            return {"message": "Cancellation was already confirmed."}
        if (
            current["status"] != order["status"]
            or current["invoice_id"] != order["invoice_id"]
            or current["updated_at"] != order["updated_at"]
        ):
            raise HTTPException(
                409, "The order changed during recovery. Refresh and retry."
            )
        target = (
            "CANCELLED"
            if cancelled
            else "AWAITING_PAYMENT"
            if awaiting
            else "PAYMENT_REVIEW"
        )
        changed = conn.execute(
            update(db.orders)
            .where(
                db.orders.c.id == order_id,
                db.orders.c.status == order["status"],
                db.orders.c.updated_at == order["updated_at"],
            )
            .values(
                invoice_id=invoice_id,
                payment_url=url,
                status=target,
                updated_at=db.now(),
            )
        )
        if changed.rowcount != 1:
            raise HTTPException(
                409, "The order changed during recovery. Refresh and retry."
            )
        if cancelled:
            release_reservations(conn, order)
            db.record(
                conn,
                order_id,
                user["subject"],
                "CANCELLED",
                "PayPal cancellation and zero payment verified; credit and inventory reservations released.",
            )
        elif reference:
            fund(conn, candidate, reference, user["subject"])
        db.record(
            conn,
            order_id,
            user["subject"],
            "INVOICE_RECOVERED",
            f"Existing PayPal invoice {invoice_id} verified; provider status {remote.get('status')}. No new invoice created.",
        )
    if cancelled:
        message = (
            "PayPal cancellation and zero payment verified. Reservations released."
        )
    elif reference:
        message = "Full PayPal payment verified. Inputs are ready for collection."
    elif awaiting:
        message = (
            "Existing invoice restored. The lender can open its PayPal payment link."
        )
    elif remote.get("status") == "DRAFT":
        message = "Existing draft linked. Send this invoice from the supplier's PayPal dashboard, then check recovery again."
    else:
        message = "Invoice linked, but its payment state requires review. Reservations remain held."
    return {"message": message}


def demo_pay(order_id: int, user):
    require(user, "lender")
    if settings.payment_mode != "mock":
        raise HTTPException(
            403, "Simulated payment is disabled in PayPal sandbox mode."
        )
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user, lock=True)
        if order["payment_mode"] != "mock":
            raise HTTPException(403, "This is not a simulated order.")
        if order["status"] in {"READY_FOR_COLLECTION", "COLLECTED"}:
            return {"ok": True}
        if order["status"] != "AWAITING_PAYMENT":
            raise HTTPException(409, "An invoice must exist before payment.")
        require_no_issues(conn, order_id)
        fund(conn, order, f"DEMO-PAY-{order_id:06d}", user["subject"])
    return {"ok": True}


def reconcile(order_id: int, user):
    if user["role"] not in {"lender", "supplier"}:
        raise HTTPException(403, "Reconciliation requires a lender or supplier.")
    with db.engine.connect() as conn:
        order = get_order(conn, order_id, user)
    if order["payment_mode"] != "sandbox" or not order["invoice_id"]:
        raise HTTPException(409, "This order has no PayPal sandbox invoice.")
    reference = verified_payment(PayPal().get(order["invoice_id"]), order)
    if not reference:
        return {
            "confirmed": False,
            "message": "A full PayPal payment has not yet been verified.",
        }
    with db.engine.begin() as conn:
        fund(conn, order, reference, user["subject"])
    return {"confirmed": True, "message": "Full PayPal payment verified."}
