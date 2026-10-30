import base64
import json
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from backend.config import settings
from test_handoffs import decision, linked, farmer_state
from test_workflow import client, auth


@pytest.fixture
def channel(client, tmp_path, monkeypatch):
    key = Ed25519PrivateKey.generate()
    trust = tmp_path / "public-trust.json"
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    trust.write_text(json.dumps({"test-key": {"enabled": True, "public_key": base64.b64encode(public).decode(),
        "lender_id": "lender-demo", "officer_ids": ["officer-12"]}}))
    monkeypatch.setattr(settings, "credit_trust_file", str(trust))
    lender, body = linked(client)
    event = {"event_id": str(uuid.uuid4()), "kind": "approval", "lender_id": "lender-demo",
        "officer_id": "officer-12", "approval_reference": body["approval_reference"], "handoff": body, "reason": None}
    def send(payload, timestamp=None, tamper=False):
        raw = json.dumps(payload, sort_keys=True).encode()
        ts = str(timestamp if timestamp is not None else int(time.time()))
        signed = b"AFRACANET-CREDIT-V1\nPOST\n/api/credit-deliveries\n" + ts.encode() + b"\n" + raw
        headers = {"X-Credit-Key": "test-key", "X-Credit-Time": ts,
            "X-Credit-Signature": base64.b64encode(key.sign(signed)).decode()}
        return client.post("/api/credit-deliveries", content=raw + (b" " if tamper else b""), headers=headers)
    return lender, event, send


def test_signed_delivery_is_authenticated_and_exactly_once(client, channel):
    lender, event, send = channel
    first = send(event)
    assert first.status_code == 200, first.text
    assert send(event).json() == first.json()
    state = farmer_state(client, lender)
    assert state["approval_reference"] == event["approval_reference"]
    history = client.get("/api/approval-handoffs", headers=lender).json()
    assert len(history) == 1
    assert history[0]["transfer_method"] == "signed_lender_decision"
    assert send({**event, "reason": "Changed content"}).status_code == 409
    assert send(event, tamper=True).status_code == 401
    assert send(event, timestamp=1).status_code == 401
    assert send({**event, "officer_id": "unapproved-officer"}).status_code == 403
    assert send({**event, "lender_id": "other-lender"}).status_code == 403
    assert client.post("/api/credit-deliveries", json=event, headers=lender).status_code == 401


def test_revocation_arriving_first_blocks_late_approval(client, channel):
    lender, event, send = channel
    revoke = {**event, "event_id": str(uuid.uuid4()), "kind": "revocation", "handoff": None, "reason": "Lender withdrew authorization"}
    assert send(revoke).status_code == 200
    assert send(event).status_code == 409
    assert client.get("/api/approval-handoffs", headers=lender).json() == []


def test_revocation_does_not_allow_retry_to_restore_limit(client, channel):
    lender, event, send = channel
    assert send(event).status_code == 200
    revoke = {**event, "event_id": str(uuid.uuid4()), "kind": "revocation", "handoff": None, "reason": "Lender withdrew authorization"}
    assert send(revoke).status_code == 200
    before = farmer_state(client, lender)
    assert send(event).status_code == 200  # Historical receipt, no business effect.
    assert send({**event, "event_id": str(uuid.uuid4())}).status_code == 409
    assert farmer_state(client, lender) == before


def test_concurrent_deliveries_record_one_handoff(client, channel):
    lender, event, send = channel
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: send(event), range(2)))
    assert all(r.status_code in (200, 409) for r in results)
    assert send(event).status_code == 200
    assert len(client.get("/api/approval-handoffs", headers=lender).json()) == 1


def test_channel_disabled_without_trust_file(client, monkeypatch):
    monkeypatch.setattr(settings, "credit_trust_file", "")
    assert client.post("/api/credit-deliveries", json={}).status_code == 503
