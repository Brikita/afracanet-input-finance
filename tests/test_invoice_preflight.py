import pytest
from sqlalchemy import select
from test_workflow import auth, request
from test_workflow import client as workflow_client

from backend import db
from backend.config import settings
from backend.integrations.paypal import PayPal

client = workflow_client


def test_invalid_namespace_never_enters_invoicing_or_calls_paypal(client, monkeypatch):
    farmer, lender, dealer = [
        auth(client, persona)
        for persona in ("farmer-amina", "lender-demo", "supplier-demo")
    ]
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    order = request(client, farmer).json()
    assert (
        client.post(f"/api/orders/{order['id']}/approve", headers=lender).status_code
        == 200
    )
    monkeypatch.setattr(settings, "paypal_invoice_prefix", "J123456789012")

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid local configuration must not call PayPal")

    monkeypatch.setattr(PayPal, "create", forbidden)
    response = client.post(f"/api/orders/{order['id']}/invoice", headers=dealer)
    assert response.status_code == 502
    with db.engine.connect() as conn:
        saved = (
            conn.execute(select(db.orders).where(db.orders.c.id == order["id"]))
            .mappings()
            .one()
        )
        assert saved["status"] == "APPROVED"
        assert saved["invoice_id"] is None
        actions = (
            conn.execute(
                select(db.audit.c.action).where(db.audit.c.order_id == order["id"])
            )
            .scalars()
            .all()
        )
        assert "PAYMENT_REVIEW" not in actions


def test_invalid_namespace_is_rejected_at_startup(monkeypatch):
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    monkeypatch.setattr(settings, "paypal_invoice_prefix", "x" * 13)
    with pytest.raises(RuntimeError, match="invoice prefix"):
        settings.validate()
