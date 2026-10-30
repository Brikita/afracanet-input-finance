from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import update

from backend import db
from backend.config import settings
from backend.integrations.paypal import PaymentError, payment_link
from test_workflow import auth, client, request, valid_invoice


def stranded(client, monkeypatch, saved=True):
    farmer, lender, supplier = [auth(client, p) for p in ["farmer-amina", "lender-demo", "supplier-demo"]]
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    monkeypatch.setattr(settings, "paypal_merchant", "supplier@example.test")
    monkeypatch.setattr(settings, "paypal_lender", "lender@example.test")
    order_id = request(client, farmer).json()["id"]
    with db.engine.begin() as conn:
        conn.execute(update(db.orders).where(db.orders.c.id == order_id).values(
            status="PAYMENT_REVIEW", invoice_id="INV2-TEST" if saved else None,
        ))
    return order_id, farmer, lender, supplier


def remote_invoice(order_id, status="SENT"):
    result = valid_invoice()
    result.update({"status": status, "detail": {
        "invoice_number": f"AFC-{order_id:06d}", "reference": f"AFRACANet order {order_id}",
        "metadata": {"recipient_view_url": "https://www.sandbox.paypal.com/invoice/p/#test"}},
        "invoicer": {"email_address": "supplier@example.test"},
        "primary_recipients": [{"billing_info": {"email_address": "lender@example.test"}}]})
    if status != "PAID":
        result["payments"] = {"transactions": []}
    return result


def test_recovers_missing_reference_without_creating_an_invoice(client, monkeypatch):
    order_id, farmer, lender, supplier = stranded(client, monkeypatch, saved=False)
    monkeypatch.setattr("backend.integrations.paypal.PayPal.get", lambda *args: remote_invoice(order_id))
    def forbidden(*args):
        pytest.fail("Recovery must never create or send an invoice")
    monkeypatch.setattr("backend.integrations.paypal.PayPal.create", forbidden)
    monkeypatch.setattr("backend.integrations.paypal.PayPal.send", forbidden)
    assert client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={"invoice_id": "INV2-TEST"}).status_code == 200
    state = client.get("/api/state", headers=lender).json()
    assert state["orders"][0]["status"] == "AWAITING_PAYMENT"
    assert state["orders"][0]["payment_url"].startswith("https://www.sandbox.paypal.com/")
    assert state["farmers"][0]["reserved_cents"] == 9000


@pytest.mark.parametrize("field", ["reference", "invoice_number", "amount", "supplier", "lender", "id", "currency"])
def test_recovery_rejects_mismatched_invoice(client, monkeypatch, field):
    order_id, farmer, lender, supplier = stranded(client, monkeypatch, saved=False)
    remote = remote_invoice(order_id)
    if field in {"reference", "invoice_number"}: remote["detail"][field] = "wrong"
    if field == "amount": remote["amount"]["value"] = "89.99"
    if field == "supplier": remote["invoicer"]["email_address"] = "other@example.test"
    if field == "lender": remote["primary_recipients"][0]["billing_info"]["email_address"] = "other@example.test"
    if field == "id": remote["id"] = "INV2-OTHER"
    if field == "currency": remote["amount"]["currency_code"] = "EUR"
    monkeypatch.setattr("backend.integrations.paypal.PayPal.get", lambda *args: remote)
    assert client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={"invoice_id": "INV2-TEST"}).status_code == 409
    assert client.get("/api/state", headers=farmer).json()["orders"][0]["invoice_id"] is None


def test_recovered_payment_funds_once_and_draft_holds_credit(client, monkeypatch):
    order_id, farmer, lender, supplier = stranded(client, monkeypatch)
    remote = remote_invoice(order_id, "DRAFT")
    monkeypatch.setattr("backend.integrations.paypal.PayPal.get", lambda *args: remote)
    result = client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={})
    assert result.status_code == 200 and "draft linked" in result.json()["message"]
    assert client.get("/api/state", headers=farmer).json()["farmers"][0]["reserved_cents"] == 9000
    remote.update(remote_invoice(order_id, "PAID"))
    assert client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={}).status_code == 200
    assert client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={}).status_code == 409
    state = client.get("/api/state", headers=farmer).json()
    assert state["orders"][0]["status"] == "READY_FOR_COLLECTION"
    assert state["farmers"][0]["spent_cents"] == 9000 and state["farmers"][0]["reserved_cents"] == 0


def test_cancelled_invoice_only_releases_after_zero_payment_verified(client, monkeypatch):
    order_id, farmer, lender, supplier = stranded(client, monkeypatch)
    remote = remote_invoice(order_id, "CANCELLED")
    remote["due_amount"] = {"currency_code": "USD", "value": "90.00"}
    remote["payments"]["transactions"] = [{"type": "PAYPAL", "amount": {"currency_code": "USD", "value": "10.00"}}]
    monkeypatch.setattr("backend.integrations.paypal.PayPal.get", lambda *args: remote)
    assert client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={}).status_code == 200
    assert client.get("/api/state", headers=farmer).json()["farmers"][0]["reserved_cents"] == 9000
    remote["payments"]["transactions"] = []
    assert client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={}).status_code == 200
    assert client.post(f"/api/orders/{order_id}/recover-invoice", headers=supplier, json={}).status_code == 409
    state = client.get("/api/state", headers=farmer).json()
    assert state["orders"][0]["status"] == "CANCELLED" and state["farmers"][0]["reserved_cents"] == 0
    assert next(p for p in state["products"] if p["id"] == "dap-50")["reserved"] == 0


def test_recovery_blocks_active_invoice_and_cross_role_and_replacement(client, monkeypatch):
    order_id, farmer, lender, supplier = stranded(client, monkeypatch)
    path = f"/api/orders/{order_id}/recover-invoice"
    assert client.post(path, headers=lender, json={}).status_code == 403
    assert client.post(path, headers=farmer, json={}).status_code == 403
    assert client.post(path, headers=supplier, json={"invoice_id": "INV2-OTHER"}).status_code == 409
    with db.engine.begin() as conn:
        conn.execute(update(db.orders).where(db.orders.c.id == order_id).values(status="INVOICING", updated_at=db.now()))
    assert client.post(path, headers=supplier, json={}).status_code == 409
    with db.engine.begin() as conn:
        conn.execute(update(db.orders).where(db.orders.c.id == order_id).values(updated_at=(datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat()))
    monkeypatch.setattr("backend.integrations.paypal.PayPal.get", lambda *args: remote_invoice(order_id))
    assert client.post(path, headers=supplier, json={}).status_code == 200


def test_invoice_send_failure_cannot_regress_a_concurrent_verified_payment(client, monkeypatch):
    from backend.services.payments import fund
    order_id, farmer, lender, supplier = stranded(client, monkeypatch)
    with db.engine.begin() as conn:
        conn.execute(update(db.orders).where(db.orders.c.id == order_id).values(status="APPROVED", invoice_id=None))
    monkeypatch.setattr("backend.integrations.paypal.PayPal.create", lambda *args: "INV2-TEST")
    def paid_then_disconnected(self, invoice_id):
        with db.engine.begin() as conn:
            order = dict(conn.execute(db.orders.select().where(db.orders.c.id == order_id)).mappings().one())
            assert fund(conn, order, "VERIFIED-WEBHOOK-TX", "paypal-webhook")
        raise PaymentError("Response lost after sending.")
    monkeypatch.setattr("backend.integrations.paypal.PayPal.send", paid_then_disconnected)
    assert client.post(f"/api/orders/{order_id}/invoice", headers=supplier).status_code == 502
    state = client.get("/api/state", headers=farmer).json()
    assert state["orders"][0]["status"] == "READY_FOR_COLLECTION"
    assert state["farmers"][0]["spent_cents"] == 9000 and state["farmers"][0]["reserved_cents"] == 0


@pytest.mark.parametrize("url", ["http://sandbox.paypal.com/x", "https://evil.test/x", "https://user@sandbox.paypal.com/x", "https://sandbox.paypal.com:8443/x"])
def test_recovery_rejects_unsafe_payment_links(url):
    with pytest.raises(PaymentError):
        payment_link({"detail": {"metadata": {"recipient_view_url": url}}})


@pytest.mark.parametrize("change", ["duplicate-reference", "refund", "null-amount", "null-payments", "invalid-transaction", "null-refunds"])
def test_payment_verification_rejects_duplicate_or_malformed_records(change):
    from copy import deepcopy
    from backend.integrations.paypal import verified_payment
    remote = valid_invoice()
    if change == "duplicate-reference":
        remote["payments"]["transactions"][0]["amount"]["value"] = "45.00"
        remote["payments"]["transactions"].append(deepcopy(remote["payments"]["transactions"][0]))
    if change == "refund": remote["refunds"] = {"transactions": [{"refund_id": "REF-001"}]}
    if change == "null-amount": remote["amount"] = None
    if change == "null-payments": remote["payments"] = None
    if change == "invalid-transaction": remote["payments"]["transactions"] = [None]
    if change == "null-refunds": remote["refunds"] = None
    assert verified_payment(remote, {"invoice_id": "INV2-TEST", "currency": "USD", "amount_cents": 9000}) is None
