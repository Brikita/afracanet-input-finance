import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select, update

from backend import db, notifications
from backend.config import settings
from test_workflow import auth, client, prepared, request


def register(client, farmer, phone="+254700000001", language="en", consent=True):
    return client.put("/api/sms/contact", headers=farmer, json={"phone": phone, "language": language, "consent": consent})


def preview_code(client, farmer):
    assert client.post("/api/sms/dispatch", headers=farmer).status_code == 200
    state = client.get("/api/sms", headers=farmer).json()
    message = next(row for row in state["messages"] if row["action"] == "VERIFY_CONTACT" and row["status"] == "SIMULATED")
    return re.search(r"\b([0-9]{6})\b", message["body"]).group(1)


def verified(client, farmer):
    assert register(client, farmer).status_code == 200
    code = preview_code(client, farmer)
    assert client.post("/api/sms/verify", headers=farmer, json={"code": code}).status_code == 200


def test_notifications_require_opt_in_and_phone_verification(client):
    farmer = auth(client, "farmer-amina")
    assert register(client, farmer, consent=False).status_code == 200
    assert client.get("/api/sms", headers=farmer).json()["messages"] == []
    assert request(client, farmer, quantity=1).status_code == 201
    assert client.get("/api/sms", headers=farmer).json()["messages"] == []
    # No transaction messages are sent while the contact remains unverified.
    with db.engine.begin() as conn:
        conn.execute(update(db.contacts).values(updated_at=(datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()))
    assert register(client, farmer).status_code == 200
    assert request(client, farmer, quantity=1, key="second-request-01").status_code == 201
    messages = client.get("/api/sms", headers=farmer).json()["messages"]
    assert len(messages) == 1 and messages[0]["action"] == "VERIFY_CONTACT" and "body" not in messages[0]


def test_demo_verification_and_preferences_are_farmer_scoped(client):
    farmer = auth(client, "farmer-amina")
    verified(client, farmer)
    assert client.get("/api/sms", headers=farmer).json()["contact"]["verified_at"]
    assert client.get("/api/sms", headers=auth(client, "farmer-kiptoo")).json()["contact"] is None
    for persona in ["lender-demo", "supplier-demo"]:
        headers = auth(client, persona)
        for method, path, body in [("get", "/api/sms", None), ("put", "/api/sms/contact", {"phone": "+254700000001", "language": "en", "consent": True}), ("post", "/api/sms/dispatch", {})]:
            assert getattr(client, method)(path, headers=headers, **({"json": body} if body is not None else {})).status_code == 403
    other = auth(client, "farmer-kiptoo")
    assert register(client, other).status_code == 409
    assert register(client, farmer, phone="0700000001").status_code == 422


def test_wrong_verification_attempts_persist_and_expired_codes_fail(client):
    farmer = auth(client, "farmer-amina")
    assert register(client, farmer).status_code == 200
    code = preview_code(client, farmer)
    for _ in range(5):
        assert client.post("/api/sms/verify", headers=farmer, json={"code": "000000"}).status_code == 422
    assert client.post("/api/sms/verify", headers=farmer, json={"code": code}).status_code == 422
    assert register(client, farmer).status_code == 429
    with db.engine.begin() as conn:
        conn.execute(update(db.contacts).values(verification_attempts=0, verification_expires_at=(datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()))
    assert client.post("/api/sms/verify", headers=farmer, json={"code": code}).status_code == 422


def test_payment_message_is_deduplicated_and_held_codes_are_not_dispatched(client):
    farmer = auth(client, "farmer-amina")
    verified(client, farmer)
    order_id, farmer, lender, supplier = prepared(client)
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    code = client.get("/api/state", headers=farmer).json()["orders"][0]["pickup_code"]
    issue = client.post(f"/api/orders/{order_id}/issues", headers=farmer, json={"client_request_id": "sms-issue-request-01", "category": "collection", "detail": "The collection date needs checking."}).json()
    notifications.dispatch_pending()
    messages = client.get("/api/sms", headers=farmer).json()["messages"]
    paid = [m for m in messages if m["action"] == "PAYMENT_CONFIRMED"]
    assert len(paid) == 1 and paid[0]["status"] == "SIMULATED"
    assert code not in paid[0]["body"] and "[DEMO]" in paid[0]["body"]
    assert client.post(f"/api/orders/{order_id}/issues/{issue['id']}/resolve", headers=lender, json={"resolution": "Dealer and farmer agreed a new collection date."}).status_code == 200
    notifications.dispatch_pending()
    messages = client.get("/api/sms", headers=farmer).json()["messages"]
    resolved = next(m for m in messages if m["action"] == "ISSUE_RESOLVED")
    assert code in resolved["body"] and "[DEMO]" in resolved["body"]


def test_opt_out_suppresses_pending_messages_without_changing_orders(client):
    farmer = auth(client, "farmer-amina")
    verified(client, farmer)
    assert request(client, farmer).status_code == 201
    assert register(client, farmer, consent=False).status_code == 200
    notifications.dispatch_pending()
    messages = client.get("/api/sms", headers=farmer).json()["messages"]
    assert next(m for m in messages if m["action"] == "REQUESTED")["status"] == "SUPPRESSED"
    state = client.get("/api/state", headers=farmer).json()
    assert state["farmers"][0]["reserved_cents"] == 9000


def test_uncertain_send_is_not_retried_and_cannot_rollback_payment(client, monkeypatch):
    farmer = auth(client, "farmer-amina")
    verified(client, farmer)
    monkeypatch.setattr(settings, "sms_mode", "sandbox")
    order_id, farmer, lender, supplier = prepared(client)
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    calls = []
    def uncertain(*args):
        calls.append(args)
        return "UNCERTAIN", None, "Review sandbox provider records."
    monkeypatch.setattr(notifications, "sandbox_send", uncertain)
    notifications.dispatch_pending()
    notifications.dispatch_pending()
    assert len(calls) == 1
    state = client.get("/api/state", headers=farmer).json()
    assert state["orders"][0]["status"] == "READY_FOR_COLLECTION" and state["farmers"][0]["spent_cents"] == 9000
    assert all("body" not in m for m in client.get("/api/sms", headers=farmer).json()["messages"])


def test_concurrent_dispatch_claims_a_message_once(client, monkeypatch):
    farmer = auth(client, "farmer-amina")
    verified(client, farmer)
    monkeypatch.setattr(settings, "sms_mode", "sandbox")
    assert request(client, farmer).status_code == 201
    with db.engine.connect() as conn:
        message_id = conn.execute(select(db.sms_outbox.c.id).where(db.sms_outbox.c.action == "REQUESTED")).scalar_one()
    calls = []
    def accepted(*args):
        calls.append(args)
        return "ACCEPTED", "AT-TEST-01", "Sandbox accepted."
    monkeypatch.setattr(notifications, "sandbox_send", accepted)
    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(notifications.dispatch_one, [message_id, message_id]))
    assert sorted(result) == [False, True] and len(calls) == 1


def test_sandbox_adapter_uses_fixed_host_and_distinguishes_acceptance(client, monkeypatch):
    calls = []
    def post(self, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(201, request=httpx.Request("POST", url), json={"SMSMessageData": {"Recipients": [{"number": "+254700000001", "statusCode": 101, "messageId": "AT-TEST-01"}]}})
    monkeypatch.setattr(httpx.Client, "post", post)
    monkeypatch.setattr(settings, "sms_key", "test-only-key")
    status, reference, _ = notifications.sandbox_send("+254700000001", "Test message")
    assert status == "ACCEPTED" and reference == "AT-TEST-01"
    assert calls[0][0] == "https://api.sandbox.africastalking.com/version1/messaging"
    assert calls[0][1]["data"]["username"] == "sandbox"
