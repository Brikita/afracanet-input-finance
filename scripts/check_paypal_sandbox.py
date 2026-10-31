"""Create or inspect one persistent, isolated PayPal sandbox test order.

The seeded credit is a labelled demonstration fixture, not an upstream lender
decision. This check never debits the buyer, simulates payment, or records pickup.
Pay the hosted invoice yourself with the separate personal sandbox account.
"""

import argparse
import json
import sys
import uuid
from pathlib import Path

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend import db
from backend.config import settings
from backend.integrations.paypal import PayPal, matching_invoice
from backend.main import app

DIRECTORY = ROOT / "data" / "provider-checks"
DATABASE = DIRECTORY / "paypal-sandbox.sqlite"
REPORT = DIRECTORY / "paypal-sandbox.json"


def require_success(response):
    if not response.is_success:
        # Never print provider bodies, credentials, or session tokens.
        raise RuntimeError(f"Local workflow HTTP {response.status_code}")
    return response.json()


def run(create=False):
    settings.payment_mode = "sandbox"
    settings.sms_mode = "demo"
    settings.validate()
    with httpx.Client(timeout=25) as client:
        response = client.get(
            "https://api-m.sandbox.paypal.com/v2/invoicing/invoices?page_size=1",
            headers={"Authorization": "Bearer " + PayPal().token()},
        )
        if response.status_code != 200:
            print(
                f"PayPal Invoicing preflight HTTP {response.status_code}. No order or invoice created by this run."
            )
            raise RuntimeError(
                "Enable Invoicing for the supplier sandbox app before continuing."
            )
    if not create and not DATABASE.exists():
        raise ValueError("Run with --create to prepare the isolated sandbox order.")
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    context_file = DIRECTORY / "paypal-sandbox-context.json"
    if context_file.exists():
        context = json.loads(context_file.read_text(encoding="utf-8"))
    else:
        # Retain the first historical fixture's reference. New fixtures receive
        # a separate namespace so they cannot consume the main app's numbers.
        context = {
            "invoice_prefix": "AFC"
            if DATABASE.exists()
            else "AFCTEST" + uuid.uuid4().hex[:4].upper()
        }
        context_file.write_text(json.dumps(context), encoding="utf-8")
    settings.paypal_invoice_prefix = context["invoice_prefix"]
    db.engine = db.build_engine(f"sqlite:///{DATABASE.as_posix()}")
    with TestClient(app) as client:

        def login(persona):
            data = require_success(
                client.post(
                    "/api/session",
                    json={
                        "persona": persona,
                        "access_code": settings.access_code,
                    },
                )
            )
            return {"Authorization": "Bearer " + data["token"]}

        farmer = login("farmer-amina")
        lender = login("lender-demo")
        supplier = login("supplier-demo")
        try:
            if create:
                order = require_success(
                    client.post(
                        "/api/orders",
                        headers=farmer,
                        json={
                            "client_request_id": "isolated-paypal-sandbox-check-v1",
                            "items": [{"product_id": "seed-2", "quantity": 1}],
                        },
                    )
                )
            else:
                with db.engine.connect() as conn:
                    row = conn.execute(select(db.orders)).mappings().first()
                    if row is None:
                        raise ValueError("No test order exists yet.")
                    order = dict(row)
            identifier = order["id"]
            if create and order["status"] == "REQUESTED":
                require_success(
                    client.post(f"/api/orders/{identifier}/approve", headers=lender)
                )
                order["status"] = "APPROVED"
            if create and order["status"] == "APPROVED":
                require_success(
                    client.post(f"/api/orders/{identifier}/invoice", headers=supplier)
                )
            with db.engine.connect() as conn:
                order = dict(
                    conn.execute(select(db.orders).where(db.orders.c.id == identifier))
                    .mappings()
                    .one()
                )
            if not order["invoice_id"]:
                raise ValueError(
                    "No provider invoice recorded. Inspect the isolated order before retrying."
                )
            remote = PayPal().get(order["invoice_id"])
            if not matching_invoice(remote, order):
                raise ValueError(
                    "Provider invoice does not match this order and configured accounts."
                )
            if order["status"] == "INVOICE_ERROR":
                # Recover only the already persisted invoice; never create another.
                require_success(
                    client.post(
                        f"/api/orders/{identifier}/recover-invoice",
                        headers=supplier,
                        json={},
                    )
                )
            result = require_success(
                client.post(f"/api/orders/{identifier}/reconcile", headers=lender)
            )
            state = require_success(client.get("/api/state", headers=lender))
            order = next(row for row in state["orders"] if row["id"] == identifier)
            blocked = (
                client.post(
                    f"/api/orders/{identifier}/demo-pay", headers=lender
                ).status_code
                == 403
            )
            if not blocked:
                raise ValueError("Sandbox must reject simulated payment.")
            report = {
                "checked_at": db.now(),
                "scope": "Isolated synthetic credit fixture; actual PayPal sandbox API. No real money or collection.",
                "order_id": identifier,
                "invoice_prefix": settings.paypal_invoice_prefix,
                "amount_cents": order["amount_cents"],
                "currency": order["currency"],
                "invoice_id": order["invoice_id"],
                "provider_status": remote.get("status"),
                "invoice_matches": True,
                "payment_verified": result["confirmed"],
                "order_status": order["status"],
                "simulated_payment_disabled": blocked,
                "payment_url": order.get("payment_url"),
                "database": str(DATABASE),
            }
            REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2))
        finally:
            for headers in (farmer, lender, supplier):
                client.delete("/api/session", headers=headers)
    db.engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create/send the single test invoice; never automatically pay it.",
    )
    args = parser.parse_args()
    try:
        run(args.create)
    except Exception as exc:
        print("Sandbox check stopped:", type(exc).__name__)
        print(
            "No automated payment was attempted. Inspect the isolated order/provider invoice before retrying."
        )
        raise SystemExit(1) from None
