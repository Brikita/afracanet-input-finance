"""Exercise both real FastAPI apps with isolated stores and a lost HTTP response.

Payment is explicitly simulated in this check. It is not a PayPal sandbox result.
"""

import argparse
import base64
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
from sqlalchemy import select, update

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def run(credit_repo):
    sys.path.insert(0, str(credit_repo))
    os.environ["CREDIT_DELIVERY_WORKER"] = "0"
    from Backend import delivery, identity, store
    from backend import db
    from backend.config import settings
    from Backend.main import app as credit_app
    from backend.main import app as input_app

    with tempfile.TemporaryDirectory(prefix="afracanet-connected-") as directory:
        temp = Path(directory)
        db.engine = db.build_engine(f"sqlite:///{temp / 'inputs.db'}")
        store.engine = store.make_engine(f"sqlite:///{temp / 'credit.db'}")
        settings.payment_mode = "mock"
        settings.ai_mode = "demo"
        settings.sms_mode = "demo"
        settings.access_code = "isolated-connected-check"
        key = Ed25519PrivateKey.generate()
        key_file = temp / "private.pem"
        key_file.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
        public = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        trust = temp / "public.json"
        trust.write_text(
            json.dumps(
                {
                    "connected-test": {
                        "enabled": True,
                        "public_key": base64.b64encode(public).decode(),
                        "lender_id": "lender-demo",
                        "officer_ids": ["connected-officer"],
                    }
                }
            )
        )
        settings.credit_trust_file = str(trust)
        os.environ.update(
            CREDIT_SIGNING_KEY_FILE=str(key_file),
            CREDIT_SIGNING_KEY_ID="connected-test",
            CREDIT_SIGNING_KEY_IDS="{}",
            INPUT_FINANCE_URL="http://127.0.0.1:8000",
        )
        with TestClient(input_app) as inputs, TestClient(credit_app) as credit:
            identity.provision(
                "connected-officer", "lender-demo", "isolated-officer-test-password"
            )

            def input_auth(persona):
                response = inputs.post(
                    "/api/session",
                    json={"persona": persona, "access_code": settings.access_code},
                )
                assert response.status_code == 200, response.text
                return {"Authorization": "Bearer " + response.json()["token"]}

            lender, farmer, supplier = [
                input_auth(p) for p in ("lender-demo", "farmer-amina", "supplier-demo")
            ]
            assert (
                inputs.post(
                    "/api/approval-mappings",
                    headers=lender,
                    json={"source_farmer_id": "F-101", "farmer_id": "farmer-amina"},
                ).status_code
                == 200
            )
            officer = credit.post(
                "/api/session",
                json={
                    "officer_id": "connected-officer",
                    "password": "isolated-officer-test-password",
                },
            ).json()
            headers = {"Authorization": "Bearer " + officer["token"]}
            application = credit.post(
                "/api/applications",
                headers=headers,
                json={
                    "farmer_id": "F-101",
                    "input_farmer_id": "farmer-amina",
                    "provenance": "synthetic",
                    "request_id": "connected-check-application",
                },
            ).json()
            decision = credit.post(
                f"/api/applications/{application['id']}/decisions",
                headers=headers,
                json={
                    "decision": "APPROVED",
                    "reason": "Lender reviewed test terms",
                    "confirm_lender_authorization": True,
                    "limit_cents": 18000,
                    "expires_at": (
                        datetime.now(timezone.utc) + timedelta(days=60)
                    ).isoformat(),
                },
            )
            assert decision.status_code == 200, decision.text
            reference = decision.json()["id"]
            with store.engine.connect() as conn:
                event = conn.execute(select(store.outbox)).mappings().one()
            calls = []

            def receiver(request):
                response = inputs.post(
                    "/api/credit-deliveries",
                    content=request.content,
                    headers=dict(request.headers),
                )
                calls.append(response.status_code)
                if len(calls) == 1:
                    assert response.status_code == 200, response.text
                    raise httpx.ReadTimeout("Acknowledgment lost", request=request)
                return httpx.Response(response.status_code, json=response.json())

            transport = httpx.MockTransport(receiver)
            assert (
                delivery.dispatch(event["id"], "lender-demo", transport)["status"]
                == "RETRY"
            )
            with store.engine.begin() as conn:
                conn.execute(update(store.outbox).values(next_attempt=""))
            assert (
                delivery.dispatch(event["id"], "lender-demo", transport)["status"]
                == "DELIVERED"
            )
            assert len(inputs.get("/api/approval-handoffs", headers=lender).json()) == 1
            order = inputs.post(
                "/api/orders",
                headers=farmer,
                json={
                    "client_request_id": "connected-order-check",
                    "items": [{"product_id": "dap-50", "quantity": 2}],
                },
            ).json()
            identifier = order["id"]
            assert (
                inputs.post(
                    f"/api/orders/{identifier}/approve", headers=lender
                ).status_code
                == 200
            )
            assert (
                inputs.post(
                    f"/api/orders/{identifier}/invoice", headers=supplier
                ).status_code
                == 200
            )
            assert (
                inputs.post(
                    f"/api/orders/{identifier}/collect",
                    headers=supplier,
                    json={"code": "000000"},
                ).status_code
                == 409
            )
            assert (
                inputs.post(
                    f"/api/orders/{identifier}/demo-pay", headers=lender
                ).status_code
                == 200
            )
            assert (
                credit.post(
                    f"/api/decisions/{reference}/revoke",
                    headers=headers,
                    json={"reason": "Withdraw new allocation authority"},
                ).status_code
                == 200
            )
            with store.engine.connect() as conn:
                revoke = (
                    conn.execute(
                        select(store.outbox).where(store.outbox.c.kind == "revocation")
                    )
                    .mappings()
                    .one()
                )
            assert (
                delivery.dispatch(revoke["id"], "lender-demo", transport)["status"]
                == "DELIVERED"
            )
            assert (
                inputs.post(
                    "/api/orders",
                    headers=farmer,
                    json={
                        "client_request_id": "after-revocation-check",
                        "items": [{"product_id": "dap-50", "quantity": 1}],
                    },
                ).status_code
                == 409
            )
            state = inputs.get("/api/state", headers=farmer).json()
            pickup = state["orders"][0]["pickup_code"]
            assert state["farmers"][0]["spent_cents"] == 9000
            assert (
                inputs.post(
                    f"/api/orders/{identifier}/collect",
                    headers=supplier,
                    json={"code": pickup},
                ).status_code
                == 200
            )
            assert (
                delivery.dispatch(event["id"], "lender-demo", transport)["status"]
                == "DELIVERED"
            )
            final = inputs.get("/api/state", headers=farmer).json()
            assert final["farmers"][0]["spent_cents"] == 9000
            assert final["orders"][0]["status"] == "COLLECTED"
            timeline = inputs.get(
                f"/api/orders/{identifier}/timeline", headers=lender
            ).json()
            assert (
                application["id"] in timeline[0]["detail"]
                and "signed_lender_decision" in timeline[0]["detail"]
            )
        db.engine.dispose()
        store.engine.dispose()
    return {
        "result": "passed",
        "modules": 2,
        "signed_deliveries": 2,
        "lost_acknowledgment_retry": "passed",
        "duplicate_allocations": 0,
        "unpaid_collection_blocked": True,
        "revocation_blocks_new_orders": True,
        "paid_collection_preserved": True,
        "payment_mode": "explicit_simulation",
        "real_provider_calls": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--credit-repo", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = run(args.credit_repo.resolve())
    if args.report:
        args.report.write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
