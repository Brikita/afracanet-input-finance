from test_workflow import client

from backend.config import settings
from backend.integrations.paypal import PayPal


def test_unsigned_events_do_not_request_provider_verification(monkeypatch):
    monkeypatch.setattr(settings, "paypal_webhook", "test-webhook")

    def network(*args, **kwargs):
        raise AssertionError("Unsigned input must not trigger a provider request")

    monkeypatch.setattr(PayPal, "request", network)
    assert PayPal().verify({}, {"id": "WH-UNSIGNED"}) is False


def test_webhook_stream_is_bounded_and_id_is_nonempty(client, monkeypatch):
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    assert (
        client.post("/api/webhooks/paypal", content=b"x" * 256_001).status_code == 413
    )
    assert client.post("/api/webhooks/paypal", json={"id": ""}).status_code == 400
