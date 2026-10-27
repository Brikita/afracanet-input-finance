from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib

import pytest
from sqlalchemy import func, insert, select, update

from backend import db
from test_management import approval_csv
from test_workflow import auth, client, prepared, request


def decision(**changes):
    now = datetime.now(timezone.utc)
    return {"schema_version": 1, "source_system": "afracanet-credit", "source_application_id": "APP-101",
            "source_farmer_id": "F-101", "farmer_id": "farmer-amina", "lender_id": "lender-demo",
            "approval_reference": "DECISION-101", "approved_by": "officer-12", "decision": "LENDER_APPROVED",
            "limit_cents": 18000, "currency": "USD", "approved_at": (now - timedelta(minutes=10)).isoformat(),
            "expires_at": (now + timedelta(days=60)).isoformat(), "data_provenance": "synthetic", **changes}


def mapping(client, lender, body):
    return client.post("/api/approval-mappings", headers=lender, json={k: body[k] for k in (
        "source_system", "source_farmer_id", "farmer_id")})


def preview(client, lender, body):
    return client.post("/api/approval-handoffs/preview", headers=lender, json=body)


def apply(client, lender, body, revision=None, confirmation=True):
    if revision is None:
        result = preview(client, lender, body)
        assert result.status_code == 200, result.text
        revision = result.json()["allocation_revision"]
    return client.post("/api/approval-handoffs", headers=lender, json={
        "handoff": body, "allocation_revision": revision, "confirm_lender_authorization": confirmation})


def linked(client, body=None):
    lender = auth(client, "lender-demo")
    body = body or decision()
    assert mapping(client, lender, body).status_code == 200
    return lender, body


def event_count(action):
    with db.engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(db.management_events).where(
            db.management_events.c.action == action)).scalar_one()


def farmer_state(client, lender):
    return next(f for f in client.get("/api/state", headers=lender).json()["farmers"] if f["id"] == "farmer-amina")


def test_mapping_is_explicit_scoped_immutable_and_idempotent(client):
    lender, body = linked(client)
    assert mapping(client, lender, body).status_code == 200
    assert event_count("APPROVAL_MAPPING_CONFIRMED") == 1
    assert mapping(client, lender, {**body, "source_farmer_id": "F-OTHER"}).status_code == 409
    assert mapping(client, lender, {**body, "farmer_id": "farmer-kiptoo"}).status_code == 409
    assert mapping(client, lender, {**body, "farmer_id": "farmer-missing"}).status_code == 404
    with db.engine.begin() as conn:
        conn.execute(update(db.farmers).where(db.farmers.c.id == "farmer-kiptoo").values(lender_id="other"))
    assert mapping(client, lender, {**body, "farmer_id": "farmer-kiptoo"}).status_code == 404
    assert len(client.get("/api/approval-mappings", headers=lender).json()) == 1


@pytest.mark.parametrize("persona", ["farmer-amina", "supplier-demo"])
def test_handoff_routes_require_the_lender_role(client, persona):
    headers = auth(client, persona)
    body = decision()
    for response in [client.get("/api/approval-mappings", headers=headers), mapping(client, headers, body),
                     preview(client, headers, body), client.get("/api/approval-handoffs", headers=headers),
                     apply(client, headers, body, "a" * 64),
                     client.post("/api/approval-handoffs/unknown/revoke", headers=headers, json={"reason": "Review required"})]:
        assert response.status_code == 403
    assert client.get("/api/approval-handoffs").status_code == 401


@pytest.mark.parametrize("change", [
    {"decision": "AI_APPROVED"}, {"decision": "REVOKED"}, {"currency": "KES"},
    {"limit_cents": True}, {"limit_cents": "18000"}, {"limit_cents": 18000.5}, {"limit_cents": 0},
    {"schema_version": True}, {"schema_version": 2}, {"approved_by": " "},
    {"approved_at": "2026-01-01T12:00:00"}, {"data_provenance": "verified"}, {"ai_recommendation": "approve"},
])
def test_handoff_rejects_recommendations_currency_coercion_and_unknown_fields(client, change):
    lender, body = linked(client)
    assert preview(client, lender, {**body, **change}).status_code == 422


def test_preview_does_not_create_credit_and_requires_mapping_lender_and_current_dates(client):
    lender = auth(client, "lender-demo")
    body = decision()
    assert preview(client, lender, body).status_code == 409
    assert mapping(client, lender, body).status_code == 200
    assert preview(client, lender, {**body, "lender_id": "other"}).status_code == 403
    now = datetime.now(timezone.utc)
    for changed in [{"expires_at": (now - timedelta(minutes=1)).isoformat()},
                    {"approved_at": (now + timedelta(minutes=1)).isoformat()},
                    {"expires_at": body["approved_at"]}]:
        assert preview(client, lender, {**body, **changed}).status_code == 422
    result = preview(client, lender, body).json()
    assert result["source_authentication"] == "not_verified"
    assert result["transfer_method"] == "manual_lender_review"
    assert farmer_state(client, lender)["limit_cents"] == 15000
    assert client.get("/api/approval-handoffs", headers=lender).json() == []


def test_apply_preserves_paid_and_reserved_credit_and_records_actor_and_source(client):
    order_id, farmer, lender, supplier = prepared(client)
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    assert request(client, farmer, quantity=1, key="second-request", product="seed-2").status_code == 201
    body = decision()
    assert mapping(client, lender, body).status_code == 200
    response = apply(client, lender, body)
    assert response.status_code == 200, response.text
    record = response.json()["record"]
    assert record["recorded_by"] == "lender-demo" and record["payload"]["approved_by"] == "officer-12"
    assert record["payload"]["data_provenance"] == "synthetic"
    assert record["transfer_method"] == "manual_lender_review"
    current = farmer_state(client, lender)
    assert (current["limit_cents"], current["reserved_cents"], current["spent_cents"]) == (18000, 1800, 9000)
    assert apply(client, lender, body).json()["already_recorded"] is True
    assert event_count("APPROVAL_HANDOFF_RECORDED") == 1
    assert len(client.get("/api/approval-handoffs", headers=lender).json()) == 1
    assert preview(client, lender, {**body, "limit_cents": 19000}).status_code == 409
    assert client.post("/api/approvals/import", headers=lender, json={
        "csv_text": approval_csv(("farmer-amina", "Amina", 20000)), "preview": False}).status_code == 409


@pytest.mark.parametrize("confirmation", [False, 1, "true", None])
def test_apply_requires_explicit_boolean_confirmation(client, confirmation):
    lender, body = linked(client)
    assert apply(client, lender, body, confirmation=confirmation).status_code == 422
    assert event_count("APPROVAL_HANDOFF_RECORDED") == 0


def test_apply_rechecks_allocation_revision_and_intervening_reservations(client):
    lender, body = linked(client, decision(limit_cents=5000))
    revision = preview(client, lender, body).json()["allocation_revision"]
    assert request(client, auth(client, "farmer-amina")).status_code == 201
    assert apply(client, lender, body, revision).status_code == 409
    body = {**body, "limit_cents": 18000}
    revision = preview(client, lender, body).json()["allocation_revision"]
    with db.engine.begin() as conn:
        conn.execute(update(db.farmers).where(db.farmers.c.id == "farmer-amina").values(limit_cents=16000))
    assert apply(client, lender, body, revision).status_code == 409
    assert event_count("APPROVAL_HANDOFF_RECORDED") == 0


def test_old_retry_cannot_overwrite_newer_terms_or_a_revocation(client):
    lender, body = linked(client)
    first = apply(client, lender, body).json()["record"]
    newer = {**body, "approval_reference": "DECISION-102", "limit_cents": 20000,
             "approved_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()}
    second = apply(client, lender, newer).json()["record"]
    assert apply(client, lender, body).json()["already_recorded"] is True
    assert farmer_state(client, lender)["limit_cents"] == 20000
    assert preview(client, lender, {**body, "approval_reference": "OLD-NEW-KEY"}).status_code == 409
    assert client.post(f"/api/approval-handoffs/{first['id']}/revoke", headers=lender,
                       json={"reason": "Superseded decision"}).status_code == 200
    assert request(client, auth(client, "farmer-amina"), quantity=1).status_code == 201
    assert client.post(f"/api/approval-handoffs/{second['id']}/revoke", headers=lender,
                       json={"reason": "Lender withdrew allocation"}).status_code == 200
    assert apply(client, lender, newer).json()["record"]["revoked_at"]
    assert request(client, auth(client, "farmer-amina"), key="after-revoke").status_code == 409
    assert preview(client, lender, newer).json()["revoked"] is True


def test_revocation_blocks_new_actions_but_preserves_payment_and_collection(client):
    order_id, farmer, lender, supplier = prepared(client)
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    pickup = client.get("/api/state", headers=farmer).json()["orders"][0]["pickup_code"]
    lender, body = linked(client)
    record = apply(client, lender, body).json()["record"]
    requested = request(client, farmer, quantity=1, key="before-revoke", product="seed-2").json()
    approved = request(client, farmer, quantity=1, key="approved-before-revoke", product="seed-2").json()
    assert client.post(f"/api/orders/{approved['id']}/approve", headers=lender).status_code == 200
    endpoint = f"/api/approval-handoffs/{record['id']}/revoke"
    for _ in range(2):
        assert client.post(endpoint, headers=lender, json={"reason": "Lender review required"}).status_code == 200
    assert event_count("APPROVAL_HANDOFF_REVOKED") == 1
    assert request(client, farmer, key="new-after-revoke").status_code == 409
    assert client.post(f"/api/orders/{requested['id']}/approve", headers=lender).status_code == 409
    assert client.post(f"/api/orders/{approved['id']}/invoice", headers=supplier).status_code == 409
    assert client.post(f"/api/orders/{order_id}/collect", headers=supplier, json={"code": pickup}).status_code == 200
    assert farmer_state(client, lender)["spent_cents"] == 9000
    trace = client.get(f"/api/orders/{requested['id']}/timeline", headers=lender).json()
    assert record["id"] in trace[0]["detail"] and "APP-101" in trace[0]["detail"]


def test_tenant_cannot_read_or_revoke_another_lenders_decision(client):
    lender, body = linked(client)
    record = apply(client, lender, body).json()["record"]
    token = "isolated-other-lender-test-session"
    with db.engine.begin() as conn:
        conn.execute(insert(db.sessions).values(token_hash=hashlib.sha256(token.encode()).hexdigest(),
            role="lender", subject="lender-other", expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()))
    other = {"Authorization": "Bearer " + token}
    assert client.get("/api/approval-mappings", headers=other).json() == []
    assert client.get("/api/approval-handoffs", headers=other).json() == []
    assert preview(client, other, body).status_code == 403
    assert mapping(client, other, body).status_code == 404
    assert client.post(f"/api/approval-handoffs/{record['id']}/revoke", headers=other,
                       json={"reason": "Foreign revocation"}).status_code == 404


def test_concurrent_confirmations_cannot_duplicate_credit_or_audit_effects(client):
    lender, body = linked(client)
    revision = preview(client, lender, body).json()["allocation_revision"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: apply(client, lender, body, revision), range(2)))
    assert all(r.status_code in (200, 409) for r in results)
    assert any(r.status_code == 200 for r in results)
    assert apply(client, lender, body, revision).json()["already_recorded"] is True
    assert event_count("APPROVAL_HANDOFF_RECORDED") == 1
    assert len(client.get("/api/approval-handoffs", headers=lender).json()) == 1
