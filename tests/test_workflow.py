from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.schema import CreateSchema, DropSchema

from backend import db
from backend.config import settings
from backend.main import app
from backend.paypal import PaymentError, verified_payment


@pytest.fixture
def client(tmp_path, monkeypatch):
    postgres_url = os.getenv("TEST_POSTGRES_URL")
    base = db.build_engine(postgres_url or f"sqlite:///{tmp_path / 'test.db'}")
    schema = "test_afracanet_" + uuid.uuid4().hex if postgres_url else None
    if schema:
        with base.begin() as conn:
            conn.execute(CreateSchema(schema))
        engine = base.execution_options(schema_translate_map={None: schema})
    else:
        engine = base
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(settings, "payment_mode", "mock")
    monkeypatch.setattr(settings, "ai_mode", "demo")
    monkeypatch.setattr(settings, "sms_mode", "demo")
    monkeypatch.setattr(settings, "access_code", "afracanet-demo")
    try:
        with TestClient(app) as result:
            yield result
    finally:
        if schema:
            # Only this fixture's randomly named test schema is removed, never public.
            with base.begin() as conn:
                conn.execute(DropSchema(schema, cascade=True))
        base.dispose()


def auth(client, persona):
    response = client.post("/api/session", json={"persona": persona, "access_code": "afracanet-demo"})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["token"]}


def request(client, headers, quantity=2, key="request-001", product="dap-50"):
    return client.post("/api/orders", headers=headers, json={
        "client_request_id": key, "items": [{"product_id": product, "quantity": quantity}],
    })


def prepared(client):
    farmer, lender, supplier = [auth(client, p) for p in ["farmer-amina", "lender-demo", "supplier-demo"]]
    response = request(client, farmer)
    assert response.status_code == 201
    order_id = response.json()["id"]
    assert client.post(f"/api/orders/{order_id}/approve", headers=lender).status_code == 200
    assert client.post(f"/api/orders/{order_id}/invoice", headers=supplier).status_code == 200
    return order_id, farmer, lender, supplier


def test_complete_workflow_keeps_payment_and_collection_separate(client):
    order_id, farmer, lender, supplier = prepared(client)
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    farmer_state = client.get("/api/state", headers=farmer).json()
    order = farmer_state["orders"][0]
    assert order["status"] == "READY_FOR_COLLECTION"
    assert farmer_state["farmers"][0]["reserved_cents"] == 0
    assert farmer_state["farmers"][0]["spent_cents"] == 9000
    assert "pickup_code" not in client.get("/api/state", headers=supplier).json()["orders"][0]
    collected = client.post(f"/api/orders/{order_id}/collect", headers=supplier, json={"code": order["pickup_code"]})
    assert collected.status_code == 200
    final = client.get("/api/state", headers=supplier).json()
    assert final["orders"][0]["status"] == "COLLECTED"
    dap = next(p for p in final["products"] if p["id"] == "dap-50")
    assert dap["stock"] == 38 and dap["reserved"] == 0
    events = client.get(f"/api/orders/{order_id}/timeline", headers=farmer).json()
    assert [e["action"] for e in events] == ["REQUESTED", "APPROVED", "INVOICED", "PAYMENT_CONFIRMED", "COLLECTED"]


def test_retries_do_not_duplicate_credit_payment_or_inventory(client):
    order_id, farmer, lender, supplier = prepared(client)
    retry = request(client, farmer)
    assert retry.status_code == 201 and retry.json()["id"] == order_id
    assert client.post(f"/api/orders/{order_id}/invoice", headers=supplier).status_code == 200
    for _ in range(2):
        assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    data = client.get("/api/state", headers=farmer).json()
    assert len(data["orders"]) == 1 and data["farmers"][0]["spent_cents"] == 9000
    events = client.get(f"/api/orders/{order_id}/timeline", headers=lender).json()
    assert len([e for e in events if e["action"] == "PAYMENT_CONFIRMED"]) == 1


def test_same_request_reference_cannot_change_items(client):
    farmer = auth(client, "farmer-amina")
    assert request(client, farmer).status_code == 201
    assert request(client, farmer, quantity=1).status_code == 409


def test_credit_limit_enforced_by_server(client):
    farmer = auth(client, "farmer-kiptoo")
    assert request(client, farmer).status_code == 409
    data = client.get("/api/state", headers=farmer).json()
    assert data["farmers"][0]["reserved_cents"] == 0 and data["orders"] == []


def test_cancellation_releases_reservations_once(client):
    farmer = auth(client, "farmer-amina")
    order_id = request(client, farmer).json()["id"]
    for _ in range(2):
        assert client.post(f"/api/orders/{order_id}/cancel", headers=farmer).status_code == 200
    data = client.get("/api/state", headers=farmer).json()
    assert data["farmers"][0]["reserved_cents"] == 0
    assert next(p for p in data["products"] if p["id"] == "dap-50")["reserved"] == 0


def test_stock_failure_rolls_back_credit(client):
    with db.engine.begin() as conn:
        conn.execute(update(db.products).where(db.products.c.id == "dap-50").values(stock=1))
    farmer = auth(client, "farmer-amina")
    assert request(client, farmer).status_code == 409
    assert client.get("/api/state", headers=farmer).json()["farmers"][0]["reserved_cents"] == 0


def test_expired_approval_cannot_reserve_credit(client):
    with db.engine.begin() as conn:
        conn.execute(update(db.farmers).where(db.farmers.c.id == "farmer-amina").values(expires_at="2000-01-01"))
    assert request(client, auth(client, "farmer-amina")).status_code == 409


def test_permissions_and_farmer_isolation(client):
    farmer = auth(client, "farmer-amina")
    other = auth(client, "farmer-kiptoo")
    order_id = request(client, farmer).json()["id"]
    assert client.post(f"/api/orders/{order_id}/approve", headers=farmer).status_code == 403
    assert client.post(f"/api/orders/{order_id}/invoice", headers=farmer).status_code == 403
    assert client.post(f"/api/orders/{order_id}/cancel", headers=other).status_code == 404
    assert client.get(f"/api/orders/{order_id}/timeline", headers=other).status_code == 404
    assert client.get("/api/state", headers=other).json()["orders"] == []
    assert client.get("/api/reconciliation.csv", headers=farmer).status_code == 403
    assert client.get("/api/state").status_code == 401


def test_collection_requires_payment_and_correct_code(client):
    order_id, farmer, lender, supplier = prepared(client)
    assert client.post(f"/api/orders/{order_id}/collect", headers=supplier, json={"code": "000000"}).status_code == 409
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    assert client.post(f"/api/orders/{order_id}/collect", headers=supplier, json={"code": "000000"}).status_code == 422
    assert client.post(f"/api/orders/{order_id}/cancel", headers=farmer).status_code == 409


def test_concurrent_orders_cannot_overspend(client):
    farmer = auth(client, "farmer-amina")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda key: request(client, farmer, key=key), ["concurrent-1", "concurrent-2"]))
    assert sorted(r.status_code for r in results) == [201, 409]
    data = client.get("/api/state", headers=farmer).json()
    assert data["farmers"][0]["reserved_cents"] == 9000 and len(data["orders"]) == 1


def test_demo_parser_clarifies_unit_size_and_parses_swahili(client):
    farmer = auth(client, "farmer-amina")
    ambiguous = client.post("/api/assistant", headers=farmer, json={"text": "Need 2 bags of DAP"}).json()
    assert ambiguous["clarification"] and ambiguous["items"] == []
    parsed = client.post("/api/assistant", headers=farmer, json={"text": "Nahitaji mifuko 2 ya DAP ya kilo 50"}).json()
    assert parsed["items"] == [{"product_id": "dap-50", "quantity": 2}]
    assert parsed["mode"] == "demo"
    assert client.get("/api/state", headers=farmer).json()["orders"] == []


def test_sandbox_mode_cannot_use_simulated_payment(client, monkeypatch):
    order_id, farmer, lender, supplier = prepared(client)
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 403


def test_uncertain_invoice_never_retries_automatically(client, monkeypatch):
    farmer, lender, supplier = [auth(client, p) for p in ["farmer-amina", "lender-demo", "supplier-demo"]]
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    order_id = request(client, farmer).json()["id"]
    assert client.post(f"/api/orders/{order_id}/approve", headers=lender).status_code == 200
    def fail(*args):
        raise PaymentError("Connection outcome uncertain.")
    monkeypatch.setattr("backend.paypal.PayPal.create", fail)
    assert client.post(f"/api/orders/{order_id}/invoice", headers=supplier).status_code == 502
    assert client.post(f"/api/orders/{order_id}/invoice", headers=supplier).status_code == 409
    data = client.get("/api/state", headers=farmer).json()
    assert data["orders"][0]["status"] == "PAYMENT_REVIEW"
    assert data["farmers"][0]["reserved_cents"] == 9000


def valid_invoice():
    return {"id": "INV2-TEST", "status": "PAID", "amount": {"currency_code": "USD", "value": "90.00"},
            "payments": {"transactions": [{"type": "PAYPAL", "payment_id": "TX-001",
                                          "amount": {"currency_code": "USD", "value": "90.00"}}]}}


@pytest.mark.parametrize("change", ["pending", "partial", "external", "wrong-currency", "wrong-amount", "wrong-id", "no-reference", "nan"])
def test_payment_verification_rejects_unsafe_confirmation(change):
    invoice = valid_invoice()
    if change == "pending": invoice["status"] = "PAYMENT_PENDING"
    if change == "partial": invoice["payments"]["transactions"][0]["amount"]["value"] = "45.00"
    if change == "external": invoice["payments"]["transactions"][0]["type"] = "EXTERNAL"
    if change == "wrong-currency": invoice["amount"]["currency_code"] = "EUR"
    if change == "wrong-amount": invoice["amount"]["value"] = "89.99"
    if change == "wrong-id": invoice["id"] = "INV2-OTHER"
    if change == "no-reference": invoice["payments"]["transactions"][0].pop("payment_id")
    if change == "nan": invoice["payments"]["transactions"][0]["amount"]["value"] = "NaN"
    assert verified_payment(invoice, {"invoice_id": "INV2-TEST", "currency": "USD", "amount_cents": 9000}) is None


def test_payment_verification_accepts_full_paypal_payment():
    assert verified_payment(valid_invoice(), {"invoice_id": "INV2-TEST", "currency": "USD", "amount_cents": 9000}) == "TX-001"


def test_invalid_webhook_cannot_confirm_payment(client, monkeypatch):
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    monkeypatch.setattr("backend.paypal.PayPal.verify", lambda *args: False)
    assert client.post("/api/webhooks/paypal", json={"id": "WH-FAKE", "event_type": "INVOICING.INVOICE.PAID",
                                                   "resource": {"id": "INV2-TEST"}}).status_code == 401
    with db.engine.connect() as conn:
        assert conn.execute(select(db.webhook_events)).first() is None


def test_verified_webhook_replay_funds_once(client, monkeypatch):
    farmer, lender, supplier = [auth(client, p) for p in ["farmer-amina", "lender-demo", "supplier-demo"]]
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    order_id = request(client, farmer).json()["id"]
    assert client.post(f"/api/orders/{order_id}/approve", headers=lender).status_code == 200
    monkeypatch.setattr("backend.paypal.PayPal.create", lambda *args: "INV2-TEST")
    monkeypatch.setattr("backend.paypal.PayPal.send", lambda *args: "https://www.sandbox.paypal.com/invoice/p/#test")
    assert client.post(f"/api/orders/{order_id}/invoice", headers=supplier).status_code == 200
    monkeypatch.setattr("backend.paypal.PayPal.verify", lambda *args: True)
    monkeypatch.setattr("backend.paypal.PayPal.get", lambda *args: valid_invoice())
    event = {"id": "WH-REPLAY", "event_type": "INVOICING.INVOICE.PAID", "resource": {"invoice": {"id": "INV2-TEST"}}}
    assert client.post("/api/webhooks/paypal", json=event).status_code == 200
    assert client.post("/api/webhooks/paypal", json=event).json()["duplicate"]
    data = client.get("/api/state", headers=farmer).json()
    assert data["farmers"][0]["spent_cents"] == 9000
    assert data["orders"][0]["status"] == "READY_FOR_COLLECTION"
