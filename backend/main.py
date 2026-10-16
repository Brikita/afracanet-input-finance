import csv
import hashlib
import io
import json
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Literal

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import assistant, db, management, notifications
from .config import ROOT, settings
from .paypal import PayPal, PaymentError, cancelled_without_payment, matching_invoice, payment_link, verified_payment

PERSONAS = {
    "farmer-amina": ("farmer", "Amina Wanjiku"),
    "farmer-kiptoo": ("farmer", "David Kiptoo"),
    "lender-demo": ("lender", "Demo Agricultural SACCO"),
    "supplier-demo": ("supplier", "Demo Green Valley Agrovet"),
}


@asynccontextmanager
async def lifespan(app):
    settings.validate()
    db.initialize()
    yield


app = FastAPI(title="AFRACANet Input Finance", version="0.1.0", lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)


@app.exception_handler(IntegrityError)
async def database_conflict(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=409, content={"detail": "A concurrent request changed this record. Refresh and retry."})


@app.exception_handler(PaymentError)
async def payment_error(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=502, content={"detail": str(exc)})


class Login(BaseModel):
    persona: str
    access_code: str = Field(max_length=256)


class ItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(ge=1, le=100)


class OrderRequest(BaseModel):
    client_request_id: str = Field(min_length=8, max_length=100)
    items: list[ItemRequest] = Field(min_length=1, max_length=10)


class AssistantRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CollectionRequest(BaseModel):
    code: str = Field(min_length=6, max_length=12)


class RecoveryRequest(BaseModel):
    invoice_id: str | None = Field(default=None, pattern=r"^INV2-[A-Z0-9-]{4,100}$")


class IssueRequest(BaseModel):
    client_request_id: str = Field(min_length=8, max_length=100)
    category: Literal["stock", "payment", "collection", "other"]
    detail: str = Field(min_length=5, max_length=1000)


class IssueResolution(BaseModel):
    resolution: str = Field(min_length=5, max_length=1000)


def actor(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Choose a demo participant to sign in.")
    token_hash = hashlib.sha256(authorization[7:].encode()).hexdigest()
    with db.engine.connect() as conn:
        session = conn.execute(select(db.sessions).where(
            db.sessions.c.token_hash == token_hash,
            db.sessions.c.expires_at > db.now(),
        )).mappings().first()
    if not session:
        raise HTTPException(401, "Your session expired. Please sign in again.")
    return dict(session)


def require(user, role):
    if user["role"] != role:
        raise HTTPException(403, f"This action requires the {role} role.")


def scoped_orders(user):
    column = {"farmer": db.orders.c.farmer_id, "lender": db.orders.c.lender_id,
              "supplier": db.orders.c.supplier_id}[user["role"]]
    return column == user["subject"]


def get_order(conn, order_id, user, lock=False):
    if lock:
        # A real row write serializes issue/collection decisions on SQLite and PostgreSQL.
        conn.execute(update(db.orders).where(db.orders.c.id == order_id, scoped_orders(user)).values(updated_at=db.now()))
    row = conn.execute(select(db.orders).where(
        db.orders.c.id == order_id, scoped_orders(user),
    )).mappings().first()
    if not row:
        raise HTTPException(404, "Order not found.")
    return dict(row)


def serialize_order(row, user, issues=None):
    result = dict(row)
    result["issues"] = issues or []
    if user["role"] != "farmer":
        result.pop("pickup_code", None)
    if user["role"] != "lender":
        result.pop("payment_url", None)
    if any(issue["resolved_at"] is None for issue in result["issues"]):
        result.pop("pickup_code", None)
        result.pop("payment_url", None)
    result["reference"] = f"AFC-{row['id']:06d}"
    return result


def require_no_issues(conn, order_id):
    if conn.execute(select(db.issues.c.id).where(db.issues.c.order_id == order_id, db.issues.c.resolved_at.is_(None)).limit(1)).first():
        raise HTTPException(409, "An open issue needs lender resolution before this action.")


def transition(conn, order, from_status, to_status):
    changed = conn.execute(update(db.orders).where(
        db.orders.c.id == order["id"], db.orders.c.status == from_status,
    ).values(status=to_status, updated_at=db.now()))
    if changed.rowcount != 1:
        raise HTTPException(409, "The order has changed. Refresh before continuing.")


def release_reservations(conn, order):
    conn.execute(update(db.farmers).where(db.farmers.c.id == order["farmer_id"]).values(
        reserved_cents=db.farmers.c.reserved_cents - order["amount_cents"],
    ))
    for item in sorted(order["items"], key=lambda item: item["product_id"]):
        conn.execute(update(db.products).where(db.products.c.id == item["product_id"]).values(
            reserved=db.products.c.reserved - item["quantity"],
        ))


@app.get("/api/health")
def health():
    return {"status": "ok", "payment_mode": settings.payment_mode, "ai_mode": settings.ai_mode,
            "currency": "USD", "prototype": True}


@app.get("/api/personas")
def personas():
    # Public demo choices are limited to seeded examples; imported people need a session.
    return [{"id": key, "role": value[0], "name": value[1]} for key, value in PERSONAS.items()]


def participant(persona):
    if persona in PERSONAS and PERSONAS[persona][0] != "farmer":
        return PERSONAS[persona]
    with db.engine.connect() as conn:
        name = conn.execute(select(db.farmers.c.name).where(db.farmers.c.id == persona)).scalar_one_or_none()
    return ("farmer", name) if name else None


@app.get("/api/participants")
def participant_choices(user=Depends(actor)):
    # Demonstration switching uses a shared code, not separate production identities.
    with db.engine.connect() as conn:
        farmers = conn.execute(select(db.farmers.c.id, db.farmers.c.name).order_by(db.farmers.c.name)).mappings().all()
    return [{"id": key, "name": value[1]} for key, value in PERSONAS.items() if value[0] != "farmer"] + [dict(row) for row in farmers]


@app.post("/api/session")
def login(body: Login):
    if not secrets.compare_digest(body.access_code, settings.access_code):
        raise HTTPException(401, "Invalid participant or access code.")
    identity = participant(body.persona)
    if not identity:
        raise HTTPException(401, "Invalid participant or access code.")
    token = secrets.token_urlsafe(32)
    role, name = identity
    with db.engine.begin() as conn:
        conn.execute(insert(db.sessions).values(
            token_hash=hashlib.sha256(token.encode()).hexdigest(), role=role, subject=body.persona,
            expires_at=(datetime.now(timezone.utc) + timedelta(hours=8)).isoformat(),
        ))
    return {"token": token, "role": role, "subject": body.persona, "name": name}


@app.delete("/api/session")
def logout(user=Depends(actor)):
    from sqlalchemy import delete
    with db.engine.begin() as conn:
        conn.execute(delete(db.sessions).where(db.sessions.c.token_hash == user["token_hash"]))
    return {"ok": True}


@app.get("/api/state")
def state(user=Depends(actor)):
    with db.engine.connect() as conn:
        if user["role"] == "farmer":
            people = conn.execute(select(db.farmers).where(db.farmers.c.id == user["subject"])).mappings().all()
        elif user["role"] == "lender":
            people = conn.execute(select(db.farmers).where(db.farmers.c.lender_id == user["subject"])).mappings().all()
        else:
            # Dealers see farmer names on their own orders, not farmers' credit data.
            ids = select(db.orders.c.farmer_id).where(scoped_orders(user))
            people = conn.execute(select(db.farmers.c.id, db.farmers.c.name, db.farmers.c.location).where(
                db.farmers.c.id.in_(ids),
            )).mappings().all()
        catalogue_query = select(db.products).order_by(db.products.c.id)
        if user["role"] == "supplier":
            catalogue_query = catalogue_query.where(db.products.c.supplier_id == user["subject"])
        catalogue = conn.execute(catalogue_query).mappings().all()
        order_rows = conn.execute(select(db.orders).where(scoped_orders(user)).order_by(db.orders.c.id.desc())).mappings().all()
        issue_rows = conn.execute(select(db.issues).where(
            db.issues.c.order_id.in_(select(db.orders.c.id).where(scoped_orders(user))),
        ).order_by(db.issues.c.id)).mappings().all()
        by_order = {}
        for issue in issue_rows:
            by_order.setdefault(issue["order_id"], []).append(dict(issue))
    return {
        "user": {"role": user["role"], "subject": user["subject"], "name": participant(user["subject"])[1]},
        "farmers": [dict(row) for row in people],
        "products": [{**dict(row), "revision": management.product_revision(row)} for row in catalogue],
        "orders": [serialize_order(row, user, by_order.get(row["id"], [])) for row in order_rows],
        "payment_mode": settings.payment_mode, "ai_mode": settings.ai_mode,
    }


@app.post("/api/approvals/import")
def approval_import(body: management.ApprovalImport, user=Depends(actor)):
    require(user, "lender")
    return management.import_approvals(body, user)


@app.put("/api/products/{product_id}")
def product_save(product_id: str, body: management.ProductEdit, user=Depends(actor)):
    require(user, "supplier")
    import re
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", product_id):
        raise HTTPException(422, "Use a product ID with lowercase letters, numbers, and hyphens (up to 80 characters).")
    return management.save_product(product_id, body, user)


@app.get("/api/sms")
def sms_preferences(user=Depends(actor)):
    require(user, "farmer")
    return notifications.preferences(user)


@app.put("/api/sms/contact")
def sms_contact(body: notifications.ContactRequest, user=Depends(actor)):
    require(user, "farmer")
    return notifications.save_contact(user, body)


@app.post("/api/sms/verify")
def sms_verify(body: notifications.VerifyRequest, user=Depends(actor)):
    require(user, "farmer")
    return notifications.verify_contact(user, body)


@app.post("/api/sms/dispatch")
def sms_dispatch(user=Depends(actor)):
    require(user, "farmer")
    count = notifications.dispatch_pending(user["subject"], limit=1)
    return {"message": f"Processed {count} queued SMS update(s). Check its recorded status; acceptance is not delivery."}


@app.post("/api/assistant")
def interpret_request(body: AssistantRequest, user=Depends(actor)):
    require(user, "farmer")
    with db.engine.connect() as conn:
        catalogue = [dict(row) for row in conn.execute(select(db.products)).mappings()]
    try:
        return assistant.interpret(body.text, catalogue)
    except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
        raise HTTPException(502, "The assistant could not interpret this request. Please use the catalogue.") from exc


@app.post("/api/orders", status_code=201)
def create_order(body: OrderRequest, user=Depends(actor)):
    require(user, "farmer")
    if len({item.product_id for item in body.items}) != len(body.items):
        raise HTTPException(422, "Combine duplicate products into one line item.")
    with db.engine.begin() as conn:
        existing = conn.execute(select(db.orders).where(
            db.orders.c.farmer_id == user["subject"],
            db.orders.c.client_request_id == body.client_request_id,
        )).mappings().first()
        if existing:
            original = {item["product_id"]: item["quantity"] for item in existing["items"]}
            if original != {item.product_id: item.quantity for item in body.items}:
                raise HTTPException(409, "This request reference belongs to a different order.")
            issues = [dict(row) for row in conn.execute(select(db.issues).where(db.issues.c.order_id == existing["id"])).mappings()]
            return serialize_order(existing, user, issues)
        farmer = conn.execute(select(db.farmers).where(db.farmers.c.id == user["subject"])).mappings().one()
        items = []
        suppliers = set()
        for item in body.items:
            product = conn.execute(select(db.products).where(db.products.c.id == item.product_id)).mappings().first()
            if not product:
                raise HTTPException(422, "Choose a product from the approved catalogue.")
            items.append({"product_id": product["id"], "name": product["name"], "unit": product["unit"],
                          "quantity": item.quantity, "price_cents": product["price_cents"]})
            suppliers.add(product["supplier_id"])
        if len(suppliers) != 1:
            raise HTTPException(422, "Each order must use one approved supplier.")
        amount = sum(item["quantity"] * item["price_cents"] for item in items)
        # A conditional UPDATE reserves funds atomically on both SQLite and PostgreSQL.
        reserved = conn.execute(update(db.farmers).where(
            db.farmers.c.id == user["subject"], db.farmers.c.expires_at > db.now(),
            db.farmers.c.limit_cents - db.farmers.c.spent_cents - db.farmers.c.reserved_cents >= amount,
        ).values(reserved_cents=db.farmers.c.reserved_cents + amount))
        if reserved.rowcount != 1:
            raise HTTPException(409, "This request exceeds available credit, or the approval has expired.")
        for item in sorted(items, key=lambda item: item["product_id"]):
            stock = conn.execute(update(db.products).where(
                db.products.c.id == item["product_id"],
                db.products.c.stock - db.products.c.reserved >= item["quantity"],
            ).values(reserved=db.products.c.reserved + item["quantity"]))
            if stock.rowcount != 1:
                raise HTTPException(409, "There is insufficient available stock. Your credit was not reserved.")
        order_id = conn.execute(insert(db.orders).values(
            farmer_id=user["subject"], lender_id=farmer["lender_id"], supplier_id=next(iter(suppliers)),
            client_request_id=body.client_request_id, items=items, amount_cents=amount,
            currency="USD", status="REQUESTED", payment_mode=settings.payment_mode,
            created_at=db.now(), updated_at=db.now(),
        )).inserted_primary_key[0]
        db.record(conn, order_id, user["subject"], "REQUESTED",
                  "Farmer confirmed catalogue items and total. Credit and inventory reserved.")
        return serialize_order(get_order(conn, order_id, user), user)


@app.post("/api/orders/{order_id}/approve")
def approve(order_id: int, user=Depends(actor)):
    require(user, "lender")
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user, lock=True)
        if order["status"] == "APPROVED":
            return {"ok": True}
        if order["status"] != "REQUESTED":
            raise HTTPException(409, "Only a requested order can be approved.")
        require_no_issues(conn, order_id)
        approval = conn.execute(select(db.farmers).where(db.farmers.c.id == order["farmer_id"])).mappings().one()
        if approval["expires_at"] <= db.now():
            raise HTTPException(409, "The farmer's credit approval has expired.")
        transition(conn, order, "REQUESTED", "APPROVED")
        db.record(conn, order_id, user["subject"], "APPROVED", "Lender approved the input order for supplier invoicing.")
    return {"ok": True}


@app.post("/api/orders/{order_id}/cancel")
def cancel(order_id: int, user=Depends(actor)):
    if user["role"] not in {"farmer", "lender"}:
        raise HTTPException(403, "Only the farmer or lender can cancel before invoicing.")
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user)
        if order["status"] == "CANCELLED":
            return {"ok": True}
        if order["status"] not in {"REQUESTED", "APPROVED"}:
            raise HTTPException(409, "An invoiced or paid order needs operator review before cancellation.")
        transition(conn, order, order["status"], "CANCELLED")
        release_reservations(conn, order)
        db.record(conn, order_id, user["subject"], "CANCELLED", "Order cancelled; credit and inventory reservations released.")
    return {"ok": True}


@app.post("/api/orders/{order_id}/invoice")
def invoice(order_id: int, user=Depends(actor)):
    require(user, "supplier")
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user, lock=True)
        if order["status"] == "AWAITING_PAYMENT":
            return {"ok": True}
        if order["status"] != "APPROVED":
            raise HTTPException(409, "The lender must approve this order before invoicing.")
        require_no_issues(conn, order_id)
        if order["payment_mode"] != settings.payment_mode:
            raise HTTPException(409, "This order uses a different payment mode. Create a new order.")
        approval = conn.execute(select(db.farmers.c.expires_at).where(
            db.farmers.c.id == order["farmer_id"],
        )).scalar_one()
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
                conn.execute(update(db.orders).where(db.orders.c.id == order_id).values(invoice_id=invoice_id))
            payment_url = provider.send(invoice_id)
        with db.engine.begin() as conn:
            conn.execute(update(db.orders).where(
                db.orders.c.id == order_id, db.orders.c.status == "INVOICING",
            ).values(invoice_id=invoice_id, payment_url=payment_url, status="AWAITING_PAYMENT", updated_at=db.now()))
            db.record(conn, order_id, user["subject"], "INVOICED",
                      "Supplier confirmed stock and price; invoice sent to lender." if order["payment_mode"] == "sandbox"
                      else "Supplier confirmed stock and price; simulated invoice created. No PayPal API call.")
    except PaymentError:
        with db.engine.begin() as conn:
            changed = conn.execute(update(db.orders).where(
                db.orders.c.id == order_id, db.orders.c.status == "INVOICING",
            ).values(status="PAYMENT_REVIEW", updated_at=db.now()))
            if changed.rowcount == 1:
                db.record(conn, order_id, "system", "PAYMENT_REVIEW",
                          "Invoice creation or sending could not be confirmed. Review provider records before retrying.")
        raise
    return {"ok": True}


def fund(conn, order, reference, who):
    changed = conn.execute(update(db.orders).where(
        db.orders.c.id == order["id"],
        db.orders.c.status.in_(["AWAITING_PAYMENT", "PAYMENT_REVIEW", "INVOICING"]),
    ).values(status="READY_FOR_COLLECTION", payment_reference=reference,
             pickup_code=str(secrets.randbelow(900000) + 100000), updated_at=db.now()))
    if changed.rowcount != 1:
        return False
    conn.execute(update(db.farmers).where(db.farmers.c.id == order["farmer_id"]).values(
        reserved_cents=db.farmers.c.reserved_cents - order["amount_cents"],
        spent_cents=db.farmers.c.spent_cents + order["amount_cents"],
    ))
    db.record(conn, order["id"], who, "PAYMENT_CONFIRMED",
              "PayPal payment reconciled against invoice amount and currency." if order["payment_mode"] == "sandbox"
              else "Simulated payment confirmed. No money moved.")
    return True


@app.post("/api/orders/{order_id}/recover-invoice")
def recover_invoice(order_id: int, body: RecoveryRequest, user=Depends(actor)):
    require(user, "supplier")
    with db.engine.connect() as conn:
        order = get_order(conn, order_id, user)
    if settings.payment_mode != "sandbox" or order["payment_mode"] != "sandbox":
        raise HTTPException(409, "Recovery requires the matching PayPal sandbox configuration.")
    if order["status"] not in {"PAYMENT_REVIEW", "INVOICING", "AWAITING_PAYMENT"}:
        raise HTTPException(409, "Only an unresolved invoice can be recovered.")
    if order["status"] == "INVOICING" and datetime.fromisoformat(order["updated_at"]) > datetime.now(timezone.utc) - timedelta(minutes=2):
        raise HTTPException(409, "Invoice preparation may still be running. Wait two minutes before recovery.")
    if order["invoice_id"] and body.invoice_id and body.invoice_id != order["invoice_id"]:
        raise HTTPException(409, "Use the invoice already linked to this order.")
    invoice_id = order["invoice_id"] or body.invoice_id
    if not invoice_id:
        raise HTTPException(422, "Find the existing invoice in the supplier's PayPal records and enter its INV2 reference.")
    candidate = {**order, "invoice_id": invoice_id}
    remote = PayPal().get(invoice_id)
    if not matching_invoice(remote, candidate):
        raise HTTPException(409, "The invoice does not match this order's reference, supplier, lender, amount, and currency.")
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
        if current["status"] != order["status"] or current["invoice_id"] != order["invoice_id"] or current["updated_at"] != order["updated_at"]:
            raise HTTPException(409, "The order changed during recovery. Refresh and retry.")
        target = "CANCELLED" if cancelled else "AWAITING_PAYMENT" if awaiting else "PAYMENT_REVIEW"
        changed = conn.execute(update(db.orders).where(
            db.orders.c.id == order_id, db.orders.c.status == order["status"],
            db.orders.c.updated_at == order["updated_at"],
        ).values(invoice_id=invoice_id, payment_url=url, status=target, updated_at=db.now()))
        if changed.rowcount != 1:
            raise HTTPException(409, "The order changed during recovery. Refresh and retry.")
        if cancelled:
            release_reservations(conn, order)
        elif reference:
            fund(conn, candidate, reference, user["subject"])
        db.record(conn, order_id, user["subject"], "INVOICE_RECOVERED",
                  f"Existing PayPal invoice {invoice_id} verified; provider status {remote.get('status')}. No new invoice created.")
    if cancelled:
        message = "PayPal cancellation and zero payment verified. Reservations released."
    elif reference:
        message = "Full PayPal payment verified. Inputs are ready for collection."
    elif awaiting:
        message = "Existing invoice restored. The lender can open its PayPal payment link."
    elif remote.get("status") == "DRAFT":
        message = "Existing draft linked. Send this invoice from the supplier's PayPal dashboard, then check recovery again."
    else:
        message = "Invoice linked, but its payment state requires review. Reservations remain held."
    return {"message": message}


@app.post("/api/orders/{order_id}/demo-pay")
def demo_pay(order_id: int, user=Depends(actor)):
    require(user, "lender")
    if settings.payment_mode != "mock":
        raise HTTPException(403, "Simulated payment is disabled in PayPal sandbox mode.")
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


@app.post("/api/orders/{order_id}/reconcile")
def reconcile(order_id: int, user=Depends(actor)):
    if user["role"] not in {"lender", "supplier"}:
        raise HTTPException(403, "Reconciliation requires a lender or supplier.")
    with db.engine.connect() as conn:
        order = get_order(conn, order_id, user)
    if order["payment_mode"] != "sandbox" or not order["invoice_id"]:
        raise HTTPException(409, "This order has no PayPal sandbox invoice.")
    reference = verified_payment(PayPal().get(order["invoice_id"]), order)
    if not reference:
        return {"confirmed": False, "message": "A full PayPal payment has not yet been verified."}
    with db.engine.begin() as conn:
        fund(conn, order, reference, user["subject"])
    return {"confirmed": True, "message": "Full PayPal payment verified."}


@app.post("/api/orders/{order_id}/collect")
def collect(order_id: int, body: CollectionRequest, user=Depends(actor)):
    require(user, "supplier")
    with db.engine.begin() as conn:
        order = get_order(conn, order_id, user, lock=True)
        if order["status"] == "COLLECTED":
            return {"ok": True, "message": "Collection was already recorded."}
        if order["status"] != "READY_FOR_COLLECTION":
            raise HTTPException(409, "Collection requires a confirmed full payment.")
        require_no_issues(conn, order_id)
        if not secrets.compare_digest(body.code, order["pickup_code"] or ""):
            raise HTTPException(422, "The collection code does not match.")
        transition(conn, order, "READY_FOR_COLLECTION", "COLLECTED")
        for item in order["items"]:
            conn.execute(update(db.products).where(db.products.c.id == item["product_id"]).values(
                stock=db.products.c.stock - item["quantity"], reserved=db.products.c.reserved - item["quantity"],
            ))
        db.record(conn, order_id, user["subject"], "COLLECTED",
                  "Dealer recorded handover with the farmer's collection code. This does not certify product quality.")
    return {"ok": True}


@app.post("/api/orders/{order_id}/issues", status_code=201)
def report_issue(order_id: int, body: IssueRequest, user=Depends(actor)):
    detail = body.detail.strip()
    if len(detail) < 5:
        raise HTTPException(422, "Describe the issue in at least five characters.")
    with db.engine.begin() as conn:
        get_order(conn, order_id, user, lock=True)
        existing = conn.execute(select(db.issues).where(
            db.issues.c.order_id == order_id, db.issues.c.client_request_id == body.client_request_id,
        )).mappings().first()
        if existing:
            if existing["detail"] != detail or existing["category"] != body.category or existing["reported_by"] != user["subject"]:
                raise HTTPException(409, "This issue reference belongs to a different report.")
            return {"id": existing["id"], "message": "Issue already recorded."}
        issue_id = conn.execute(insert(db.issues).values(
            order_id=order_id, client_request_id=body.client_request_id, category=body.category,
            detail=detail, reported_by=user["subject"], created_at=db.now(),
        )).inserted_primary_key[0]
        db.record(conn, order_id, user["subject"], "ISSUE_REPORTED", f"{body.category}: {detail}")
    return {"id": issue_id, "message": "Issue recorded. The lender must resolve it before further approval, invoicing, payment initiation, or collection."}


@app.post("/api/orders/{order_id}/issues/{issue_id}/resolve")
def resolve_issue(order_id: int, issue_id: int, body: IssueResolution, user=Depends(actor)):
    require(user, "lender")
    resolution = body.resolution.strip()
    if len(resolution) < 5:
        raise HTTPException(422, "Record the resolution in at least five characters.")
    with db.engine.begin() as conn:
        get_order(conn, order_id, user, lock=True)
        issue = conn.execute(select(db.issues).where(db.issues.c.id == issue_id, db.issues.c.order_id == order_id)).mappings().first()
        if not issue:
            raise HTTPException(404, "Issue not found.")
        if issue["resolved_at"]:
            if issue["resolution"] != resolution:
                raise HTTPException(409, "This issue already has a recorded resolution.")
            return {"message": "Issue already resolved."}
        conn.execute(update(db.issues).where(db.issues.c.id == issue_id).values(
            resolved_by=user["subject"], resolved_at=db.now(), resolution=resolution,
        ))
        db.record(conn, order_id, user["subject"], "ISSUE_RESOLVED", f"Issue {issue_id}: {resolution}")
    return {"message": "Resolution recorded. Financial and collection status still follow their verified transaction records."}


@app.get("/api/orders/{order_id}/timeline")
def timeline(order_id: int, user=Depends(actor)):
    with db.engine.connect() as conn:
        get_order(conn, order_id, user)
        rows = conn.execute(select(db.audit).where(db.audit.c.order_id == order_id).order_by(db.audit.c.id)).mappings()
        return [dict(row) for row in rows]


@app.get("/api/reconciliation.csv")
def export(user=Depends(actor)):
    require(user, "lender")
    with db.engine.connect() as conn:
        rows = conn.execute(select(db.orders).where(scoped_orders(user)).order_by(db.orders.c.id)).mappings().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["order", "farmer", "amount", "currency", "status", "invoice", "payment_reference", "payment_mode"])
    for row in rows:
        writer.writerow([f"AFC-{row['id']:06d}", row["farmer_id"], f"{row['amount_cents']/100:.2f}",
                         row["currency"], row["status"], row["invoice_id"], row["payment_reference"], row["payment_mode"]])
    return Response(output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="afracanet-reconciliation.csv"'})


@app.post("/api/webhooks/paypal")
async def paypal_webhook(request: Request):
    if settings.payment_mode != "sandbox":
        raise HTTPException(403, "PayPal webhooks are disabled in simulated mode.")
    body = await request.body()
    if len(body) > 1_000_000:
        raise HTTPException(413, "Event is too large.")
    try:
        event = json.loads(body)
    except ValueError as exc:
        raise HTTPException(400, "Invalid event.") from exc
    if not isinstance(event, dict) or not isinstance(event.get("id"), str):
        raise HTTPException(400, "Event ID is required.")
    # Network operations stay off the async event loop.
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(process_webhook, dict(request.headers), event)


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


if (ROOT / "dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "dist", html=True), name="frontend")
