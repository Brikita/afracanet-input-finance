"""Bind the existing sandbox webhook to a verified callback-only test listener.

Only the existing webhook URL changes. Its previous configuration is retained
locally. --resend-paid-fixture replays the genuine paid event; no invoice or
payment is created and no buyer credentials are used.
"""

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

import httpx

from backend.config import ROOT, settings
from backend.integrations.paypal import PayPal


def connect(url, resend=False):
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("Provide the HTTPS origin of the callback-only listener.")
    origin = url.rstrip("/")
    response = httpx.get(origin + "/health", timeout=20)
    response.raise_for_status()
    if response.json() != {"status": "ok", "purpose": "paypal_sandbox_callback_only"}:
        raise ValueError("The target is not our callback-only listener.")
    if httpx.get(origin + "/api/session", timeout=20).status_code != 404:
        raise ValueError("The callback target must not expose workspace routes.")
    provider = PayPal()
    hooks = provider.request("GET", "/v1/notifications/webhooks").get("webhooks", [])
    hook = next((h for h in hooks if h["id"] == settings.paypal_webhook), None)
    if hook is None:
        raise ValueError("Configured webhook is absent from this sandbox app.")
    directory = ROOT / "data" / "provider-checks"
    directory.mkdir(exist_ok=True, parents=True)
    backup = directory / "webhook-before-sprint.json"
    if not backup.exists():
        backup.write_text(json.dumps(hook), encoding="utf-8")
    provider.request(
        "PATCH",
        f"/v1/notifications/webhooks/{hook['id']}",
        [{"op": "replace", "path": "/url", "value": origin + "/api/webhooks/paypal"}],
    )
    print("Existing sandbox webhook bound to the verified callback-only listener.")
    if resend:
        fixture = json.loads(
            (directory / "paypal-sandbox.json").read_text(encoding="utf-8")
        )
        events = provider.request(
            "GET",
            "/v1/notifications/webhooks-events?event_type=INVOICING.INVOICE.PAID&page_size=20",
        ).get("events", [])
        matching = [
            event
            for event in events
            if event.get("resource", {})
            .get("invoice", event.get("resource", {}))
            .get("id")
            == fixture["invoice_id"]
        ]
        if len(matching) != 1:
            raise ValueError(
                "Expected exactly one paid event for the persistent fixture."
            )
        event = matching[0]
        provider.request(
            "POST",
            f"/v1/notifications/webhooks-events/{event['id']}/resend",
            {"webhook_ids": [hook["id"]]},
        )
        (directory / "callback-context.json").write_text(
            json.dumps({"event_id": event["id"], "origin": origin}), encoding="utf-8"
        )
        print(
            "Genuine invoice-paid event resend requested. Verify its receipt and unchanged balances locally."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--resend-paid-fixture", action="store_true")
    args = parser.parse_args()
    try:
        connect(args.url, args.resend_paid_fixture)
    except Exception as exc:
        print("Callback setup stopped:", type(exc).__name__)
        raise SystemExit(1) from None
