import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import httpx

from ..config import settings

BASE = "https://api-m.sandbox.paypal.com"


class PaymentError(Exception):
    pass


def invoice_number(order_id):
    prefix = settings.paypal_invoice_prefix
    if not re.fullmatch(r"[A-Z0-9-]{1,12}", prefix):
        raise PaymentError(
            "Use an invoice prefix of 1–12 uppercase letters, digits, or hyphens."
        )
    return f"{prefix}-{order_id:06d}"


def invoice_reference(result):
    """PayPal returns either an invoice representation or a minimal self link."""
    if isinstance(result, dict):
        identifier = result.get("id")
        if isinstance(identifier, str) and re.fullmatch(
            r"INV2-[A-Z0-9-]{4,100}", identifier
        ):
            return identifier
        links = result.get("links", [])
        links = links if isinstance(links, list) else []
        for link in [result, *links]:
            if not isinstance(link, dict) or link.get("rel") != "self":
                continue
            href = link.get("href")
            if not isinstance(href, str):
                continue
            try:
                parsed = urlparse(href)
                identifier = parsed.path.removeprefix("/v2/invoicing/invoices/")
                if (
                    parsed.scheme == "https"
                    and parsed.netloc == "api-m.sandbox.paypal.com"
                    and not parsed.query
                    and not parsed.fragment
                    and re.fullmatch(r"INV2-[A-Z0-9-]{4,100}", identifier)
                ):
                    return identifier
            except ValueError:
                continue
    raise PaymentError(
        "PayPal did not return a valid invoice reference. Review before retrying."
    )


def payment_link(invoice):
    detail = invoice.get("detail") if isinstance(invoice, dict) else None
    metadata = detail.get("metadata") if isinstance(detail, dict) else None
    url = metadata.get("recipient_view_url") if isinstance(metadata, dict) else None
    if not isinstance(url, str):
        raise PaymentError(
            "PayPal did not return a recipient payment link. Review the invoice."
        )
    try:
        parsed = urlparse(url)
        valid = (
            parsed.scheme == "https"
            and parsed.hostname in {"www.sandbox.paypal.com", "sandbox.paypal.com"}
            and not parsed.username
            and not parsed.password
            and parsed.port in {None, 443}
        )
    except ValueError:
        valid = False
    if not valid:
        raise PaymentError(
            "PayPal returned a non-sandbox payment link. Review the invoice."
        )
    return url


def matching_invoice(invoice, order):
    """Verify correlation before attaching a manually recovered remote invoice."""
    if not isinstance(invoice, dict):
        return False
    detail = invoice.get("detail", {})
    amount = invoice.get("amount", {})
    recipients = invoice.get("primary_recipients", [])
    invoicer = invoice.get("invoicer", {})
    if (
        not isinstance(detail, dict)
        or not isinstance(amount, dict)
        or not isinstance(invoicer, dict)
        or not isinstance(recipients, list)
        or len(recipients) != 1
        or not isinstance(recipients[0], dict)
        or not isinstance(recipients[0].get("billing_info"), dict)
    ):
        return False
    merchant = invoicer.get("email_address")
    lender = recipients[0]["billing_info"].get("email_address")
    if not isinstance(merchant, str) or not isinstance(lender, str):
        return False
    return (
        invoice.get("id") == order["invoice_id"]
        and detail.get("invoice_number") == invoice_number(order["id"])
        and detail.get("reference") == f"AFRACANet order {order['id']}"
        and amount.get("currency_code") == order["currency"]
        and cents(amount.get("value")) == order["amount_cents"]
        and bool(settings.paypal_merchant)
        and bool(settings.paypal_lender)
        and merchant.casefold() == settings.paypal_merchant.casefold()
        and lender.casefold() == settings.paypal_lender.casefold()
    )


def cancelled_without_payment(invoice, order):
    # Never release on a cancelled status alone: a partial payment may still exist.
    payments = invoice.get("payments", {})
    due = invoice.get("due_amount", {})
    refunds = invoice.get("refunds", {})
    if not all(isinstance(value, dict) for value in [payments, due, refunds]):
        return False
    if not isinstance(payments.get("paid_amount", {}), dict):
        return False
    return (
        invoice.get("status") == "CANCELLED"
        and not payments.get("transactions")
        and not refunds.get("transactions")
        and cents(payments.get("paid_amount", {}).get("value", "0")) == 0
        and due.get("currency_code") == order["currency"]
        and cents(due.get("value")) == order["amount_cents"]
    )


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
                raise PaymentError(
                    "PayPal sandbox authentication failed. Check server configuration."
                )
            return response.json()["access_token"]

    def request(self, method, path, payload=None):
        try:
            with httpx.Client(timeout=25) as client:
                response = client.request(
                    method,
                    BASE + path,
                    headers={
                        "Authorization": f"Bearer {self.token()}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if not response.is_success:
                    raise PaymentError(
                        "PayPal could not complete this action. Operator review is required."
                    )
                return response.json() if response.content else {}
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise PaymentError(
                "PayPal could not be reached or returned an unexpected response."
            ) from exc

    def create(self, order):
        payload = {
            "detail": {
                "invoice_number": invoice_number(order["id"]),
                "currency_code": order["currency"],
                "reference": f"AFRACANet order {order['id']}",
                "note": "Sandbox demonstration: approved agricultural input finance.",
                "payment_term": {"term_type": "DUE_ON_RECEIPT"},
            },
            "invoicer": {"email_address": settings.paypal_merchant},
            "primary_recipients": [
                {"billing_info": {"email_address": settings.paypal_lender}}
            ],
            "items": [
                {
                    "name": item["name"],
                    "description": item["unit"],
                    "quantity": str(item["quantity"]),
                    "unit_amount": {
                        "currency_code": order["currency"],
                        "value": f"{item['price_cents'] / 100:.2f}",
                    },
                }
                for item in order["items"]
            ],
            "configuration": {
                "partial_payment": {"allow_partial_payment": False},
                "allow_tip": False,
            },
        }
        result = self.request("POST", "/v2/invoicing/invoices", payload)
        return invoice_reference(result)

    def send(self, invoice_id):
        self.request(
            "POST",
            f"/v2/invoicing/invoices/{invoice_id}/send",
            {
                "send_to_recipient": True,
                "send_to_invoicer": False,
            },
        )
        details = self.get(invoice_id)
        return payment_link(details)

    def get(self, invoice_id):
        return self.request("GET", f"/v2/invoicing/invoices/{invoice_id}")

    def verify(self, headers, event):
        if not settings.paypal_webhook:
            return False
        required = (
            "paypal-auth-algo",
            "paypal-cert-url",
            "paypal-transmission-id",
            "paypal-transmission-sig",
            "paypal-transmission-time",
        )
        if any(
            not isinstance(headers.get(name), str)
            or not 1 <= len(headers[name]) <= 4096
            for name in required
        ):
            return False
        payload = {
            "auth_algo": headers.get("paypal-auth-algo"),
            "cert_url": headers.get("paypal-cert-url"),
            "transmission_id": headers.get("paypal-transmission-id"),
            "transmission_sig": headers.get("paypal-transmission-sig"),
            "transmission_time": headers.get("paypal-transmission-time"),
            "webhook_id": settings.paypal_webhook,
            "webhook_event": event,
        }
        if not all(payload[key] for key in payload):
            return False
        return (
            self.request(
                "POST", "/v1/notifications/verify-webhook-signature", payload
            ).get("verification_status")
            == "SUCCESS"
        )


def cents(amount):
    try:
        value = Decimal(str(amount))
        if (
            not value.is_finite()
            or value < 0
            or value * 100 != (value * 100).to_integral_value()
        ):
            return None
        return int(value * 100)
    except (InvalidOperation, ValueError, TypeError):
        return None


def verified_payment(invoice, order):
    """A PAID status alone can include manual/external payments; require PayPal records."""
    if not isinstance(invoice, dict):
        return None
    amount = invoice.get("amount", {})
    if invoice.get("id") != order["invoice_id"] or invoice.get("status") != "PAID":
        return None
    if (
        not isinstance(amount, dict)
        or amount.get("currency_code") != order["currency"]
        or cents(amount.get("value")) != order["amount_cents"]
    ):
        return None
    payments, refunds = invoice.get("payments", {}), invoice.get("refunds", {})
    if (
        not isinstance(payments, dict)
        or not isinstance(refunds, dict)
        or refunds.get("transactions")
    ):
        return None
    transactions = payments.get("transactions", [])
    if not isinstance(transactions, list) or any(
        not isinstance(tx, dict) for tx in transactions
    ):
        return None
    legitimate = [
        tx
        for tx in transactions
        if tx.get("type") == "PAYPAL"
        and isinstance(tx.get("payment_id"), str)
        and tx["payment_id"]
        and isinstance(tx.get("amount"), dict)
        and tx.get("amount", {}).get("currency_code") == order["currency"]
        and cents(tx.get("amount", {}).get("value")) is not None
    ]
    # Refunded invoices and partially paid invoices fail the status check above.
    if (
        len({tx["payment_id"] for tx in legitimate}) != len(legitimate)
        or sum(cents(tx["amount"]["value"]) for tx in legitimate)
        != order["amount_cents"]
    ):
        return None
    return ",".join(sorted({tx["payment_id"] for tx in legitimate}))
