import pytest

from backend.config import settings
from backend.integrations.paypal import PaymentError, PayPal, invoice_number

REFERENCE = "INV2-ABCD-1234-EFGH-5678"
LINK = {
    "href": "https://api-m.sandbox.paypal.com/v2/invoicing/invoices/" + REFERENCE,
    "rel": "self",
    "method": "GET",
}


def test_separate_stores_can_use_distinct_invoice_namespaces(monkeypatch):
    monkeypatch.setattr(settings, "paypal_invoice_prefix", "AFCTEST")
    assert invoice_number(1) == "AFCTEST-000001"
    monkeypatch.setattr(settings, "paypal_invoice_prefix", "AFCDEV")
    assert invoice_number(1) == "AFCDEV-000001"


@pytest.mark.parametrize("response", [{"id": REFERENCE}, LINK, {"links": [LINK]}])
def test_create_keeps_reference_from_full_or_minimal_paypal_response(
    monkeypatch, response
):
    monkeypatch.setattr(PayPal, "request", lambda *args, **kwargs: response)
    result = PayPal().create({"id": 1, "currency": "USD", "items": []})
    assert result == REFERENCE


@pytest.mark.parametrize(
    "response",
    [
        None,
        {"id": "INV2-ABCD/send"},
        {"links": [None, {"rel": "self", "href": 123}]},
        {
            **LINK,
            "href": LINK["href"].replace("api-m.sandbox.paypal.com", "example.com"),
        },
        {**LINK, "href": LINK["href"] + "/send"},
        {**LINK, "rel": "send"},
    ],
)
def test_create_rejects_unusable_invoice_references(monkeypatch, response):
    monkeypatch.setattr(PayPal, "request", lambda *args, **kwargs: response)
    with pytest.raises(PaymentError):
        PayPal().create({"id": 1, "currency": "USD", "items": []})
