from datetime import datetime, timedelta, timezone
import json
import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from Backend import store, identity, delivery
from Backend.main import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = store.make_engine(f"sqlite:///{tmp_path / 'credit.db'}")
    monkeypatch.setattr(store, "engine", engine)
    monkeypatch.setenv("CREDIT_DELIVERY_WORKER", "0")
    store.initialize()
    identity.provision("officer-a", "lender-a", "individual-password-a")
    identity.provision("officer-b", "lender-b", "individual-password-b")
    with TestClient(app) as client:
        yield client
    engine.dispose()

def auth(client, officer="a"):
    response = client.post("/api/session", json={"officer_id": "officer-" + officer, "password": "individual-password-" + officer})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["token"]}

def application(client, headers):
    response = client.post("/api/applications", headers=headers, json={"farmer_id": "F-101", "input_farmer_id": "farmer-amina", "provenance": "synthetic", "request_id": "application-request-001"})
    assert response.status_code == 201, response.text
    return response.json()

def terms():
    return {"decision": "APPROVED", "reason": "Lender reviewed illustrative terms", "limit_cents": 18000,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat(), "confirm_lender_authorization": True}

def test_officer_scope_persistence_and_immutable_decision(client):
    headers = auth(client)
    record = application(client, headers)
    assert application(client, headers)["id"] == record["id"]
    assert client.get("/api/workspace").status_code == 401
    assert client.post(f"/api/applications/{record['id']}/decisions", headers=auth(client, "b"), json=terms()).status_code == 404
    body = terms()
    first = client.post(f"/api/applications/{record['id']}/decisions", headers=headers, json=body)
    assert first.status_code == 200, first.text
    assert client.post(f"/api/applications/{record['id']}/decisions", headers=headers, json=body).json()["id"] == first.json()["id"]
    assert client.post(f"/api/applications/{record['id']}/decisions", headers=headers, json={**body, "limit_cents": 19000}).status_code == 409
    state = client.get("/api/workspace", headers=headers).json()
    assert len(state["decisions"]) == len(state["deliveries"]) == 1
    assert state["decisions"][0]["officer_id"] == "officer-a"
    assert client.get("/api/workspace", headers=auth(client, "b")).json()["applications"] == []
    with TestClient(app) as restarted:
        assert len(restarted.get("/api/workspace", headers=headers).json()["decisions"]) == 1

def test_rejection_never_queues_a_handoff(client):
    headers = auth(client)
    record = application(client, headers)
    response = client.post(f"/api/applications/{record['id']}/decisions", headers=headers,
        json={"decision": "REJECTED", "reason": "Insufficient supporting evidence", "confirm_lender_authorization": True})
    assert response.status_code == 200
    assert client.get("/api/workspace", headers=headers).json()["deliveries"] == []

def test_revocation_is_durable_and_scoped(client):
    headers = auth(client)
    record = application(client, headers)
    decision = client.post(f"/api/applications/{record['id']}/decisions", headers=headers, json=terms()).json()
    path = f"/api/decisions/{decision['id']}/revoke"
    assert client.post(path, headers=auth(client, "b"), json={"reason": "Withdraw authorization"}).status_code == 404
    for _ in range(2):
        assert client.post(path, headers=headers, json={"reason": "Withdraw authorization"}).status_code == 200
    state = client.get("/api/workspace", headers=headers).json()
    assert state["applications"][0]["status"] == "REVOKED"
    assert len(state["deliveries"]) == 2

def test_invalid_confirmation_and_legacy_routes(client):
    headers = auth(client)
    record = application(client, headers)
    body = terms()
    for value in [False, 1, "true"]:
        assert client.post(f"/api/applications/{record['id']}/decisions", headers=headers, json={**body, "confirm_lender_authorization": value}).status_code == 422
    assert client.post("/api/approve", json={"farmer_id": "F-101"}).status_code == 410
    assert client.post("/api/session", json={"officer_id": "officer-a", "password": "wrong"}).status_code == 401

def test_failed_delivery_retains_payload_and_can_retry(client, monkeypatch):
    headers = auth(client)
    record = application(client, headers)
    client.post(f"/api/applications/{record['id']}/decisions", headers=headers, json=terms())
    with store.engine.connect() as conn:
        event = conn.execute(select(store.outbox)).mappings().one()
    monkeypatch.setenv("INPUT_FINANCE_URL", "http://127.0.0.1:8000")
    monkeypatch.setattr(delivery, "headers", lambda raw: {})
    failed = httpx.MockTransport(lambda req: httpx.Response(503))
    assert delivery.dispatch(event["id"], "lender-a", failed)["status"] == "RETRY"
    with store.engine.begin() as conn:
        assert conn.execute(select(store.outbox.c.body)).scalar_one() == event["body"]
        conn.execute(update(store.outbox).values(next_attempt=""))
    received = []
    def accept(req):
        received.append(json.loads(req.content))
        return httpx.Response(200, json={"event_id": event["id"], "status": "recorded", "handoff_id": "received-001"})
    assert delivery.dispatch(event["id"], "lender-a", httpx.MockTransport(accept))["status"] == "DELIVERED"
    assert delivery.dispatch(event["id"], "lender-a", httpx.MockTransport(accept))["status"] == "DELIVERED"
    assert len(received) == 1
    assert delivery.dispatch(event["id"], "lender-b", failed) is None

def test_unavailable_graph_is_explicit(client, monkeypatch):
    headers = auth(client)
    record = application(client, headers)
    monkeypatch.delenv("WORKFLOW_NEO4J_URI", raising=False)
    result = client.get(f"/api/applications/{record['id']}/context", headers=headers)
    assert result.status_code == 503
    assert "fallback" in result.json()["detail"]
