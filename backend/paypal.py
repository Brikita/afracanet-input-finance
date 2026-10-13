from decimal import Decimal, InvalidOperation

import httpx

from .config import settings

BASE = "https://api-m.sandbox.paypal.com"


class PaymentError(Exception):
    pass


class PayPal:
    """Sandbox only. The server never accepts a caller-supplied API base or merchant."""

    def token(self):
        with httpx.Client(timeout=25) as client:
            response = client.post(
                f"{BASE}/v1/oauth2/token",
                auth=(settings.paypal_client_id, settings.paypal_secret),
                data={"grant_type": "client_credentials"},
            )
            if response.status_code != 200:
                raise PaymentError("PayPal sandbox authentication failed. Check server configuration.")
            return response.json()["access_token"]

    def request(self, method, path, payload=None):
        try:
            with httpx.Client(timeout=25) as client:
                response = client.request(
                    method, BASE + path,
                    headers={"Authorization": f"Bearer {self.token()}", "Content-Type": "application/json"},
                    json=payload,
                )
                if not response.is_success:
                    raise PaymentError("PayPal could not complete this action. Operator review is required.")
                return response.json() if response.content else {}
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise PaymentError("PayPal could not be reached or returned an unexpected response.") from exc

    def create(self, order):
        payload = {
            "detail": {
                "invoice_number": f"AFC-{order['id']:06d}",
                "currency_code": order["currency"],
                "reference": f"AFRACANet order {order['id']}",
                "note": "Sandbox demonstration: approved agricultural input finance.",
                "payment_term": {"term_type": "DUE_ON_RECEIPT"},
            },
            "invoicer": {"email_address": settings.paypal_merchant},
            "primary_recipients": [{"billing_info": {"email_address": settings.paypal_lender}}],
            "items": [
                {"name": item["name"], "description": item["unit"],
                 "quantity": str(item["quantity"]),
                 "unit_amount": {"currency_code": order["currency"], "value": f"{item['price_cents'] / 100:.2f}"}}
                for item in order["items"]
            ],
            "configuration": {"partial_payment": {"allow_partial_payment": False}, "allow_tip": False},
        }
        result = self.request("POST", "/v2/invoicing/invoices", payload)
        invoice_id = result.get("id")
        if not invoice_id:
            invoice_id = next(
                (link["href"].rstrip("/").split("/")[-1]
                 for link in result.get("links", []) if link.get("rel") == "self"), None,
            )
        if not invoice_id or not invoice_id.startswith("INV2-"):
            raise PaymentError("PayPal did not return a valid invoice reference. Review before retrying.")
        return invoice_id

    def send(self, invoice_id):
        self.request("POST", f"/v2/invoicing/invoices/{invoice_id}/send", {
            "send_to_recipient": True, "send_to_invoicer": False,
        })
        details = self.get(invoice_id)
        url = details.get("detail", {}).get("metadata", {}).get("recipient_view_url")
        if not url:
            raise PaymentError("PayPal did not return a recipient payment link. Review the invoice.")
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {"www.sandbox.paypal.com", "sandbox.paypal.com"}:
            raise PaymentError("PayPal returned a non-sandbox payment link. Review the invoice.")
        return url

    def get(self, invoice_id):
        return self.request("GET", f"/v2/invoicing/invoices/{invoice_id}")

    def verify(self, headers, event):
        if not settings.paypal_webhook:
            return False
        payload = {
            "auth_algo": headers.get("paypal-auth-algo"),
            "cert_url": headers.get("paypal-cert-url"),
            "transmission_id": headers.get("paypal-transmission-id"),
            "transmission_sig": headers.get("paypal-transmission-sig"),
            "transmission_time": headers.get("paypal-transmission-time"),
            "webhook_id": settings.paypal_webhook, "webhook_event": event,
        }
        if not all(payload[key] for key in payload):
            return False
        return self.request("POST", "/v1/notifications/verify-webhook-signature", payload).get(
            "verification_status"
        ) == "SUCCESS"


def cents(amount):
    try:
        value = Decimal(str(amount))
        if not value.is_finite() or value < 0 or value * 100 != (value * 100).to_integral_value():
            return None
        return int(value * 100)
    except (InvalidOperation, ValueError, TypeError):
        return None


def verified_payment(invoice, order):
    """A PAID status alone can include manual/external payments; require PayPal records."""
    amount = invoice.get("amount", {})
    if invoice.get("id") != order["invoice_id"] or invoice.get("status") != "PAID":
        return None
    if amount.get("currency_code") != order["currency"] or cents(amount.get("value")) != order["amount_cents"]:
        return None
    transactions = invoice.get("payments", {}).get("transactions", [])
    legitimate = [
        tx for tx in transactions
        if tx.get("type") == "PAYPAL" and tx.get("payment_id")
        and tx.get("amount", {}).get("currency_code") == order["currency"]
        and cents(tx.get("amount", {}).get("value")) is not None
    ]
    # Refunded invoices and partially paid invoices fail the status check above.
    if sum(cents(tx["amount"]["value"]) for tx in legitimate) != order["amount_cents"]:
        return None
    return ",".join(sorted({tx["payment_id"] for tx in legitimate}))
