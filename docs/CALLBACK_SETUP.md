# Sandbox callback setup

The 31 October check received a genuine PayPal invoice-paid event and verified
its signature. Repeated delivery left one persisted receipt and one payment
effect. This uses the already-paid isolated fixture; it does not create another
invoice, pay it, or record physical collection.

Use separate terminals from the input-finance repository:

```powershell
# Terminal 1: expose only the callback app, using the preserved check fixture.
$env:WEBHOOK_CHECK_FIXTURE='1'
.venv/Scripts/python.exe -m uvicorn scripts.webhook_listener:app --host 127.0.0.1 --port 8013
```

```powershell
# Terminal 2: official cloudflared binary, installed locally outside source.
data/tools/cloudflared.exe tunnel --url http://127.0.0.1:8013 --no-autoupdate
```

```powershell
# Terminal 3: use the newly printed HTTPS origin, without a path.
.venv/Scripts/python.exe -m scripts.connect_paypal_callback https://YOUR-ORIGIN.trycloudflare.com --resend-paid-fixture
# Independently recheck actual payment records and unchanged balances.
.venv/Scripts/python.exe scripts/check_paypal_sandbox.py
```

The connection helper verifies the callback-only health response and that
`/api/session` returns 404 before changing the existing sandbox webhook URL.
It preserves the old configuration in ignored
`data/provider-checks/webhook-before-sprint.json`; it never creates a second hook
or changes subscriptions. Callback signatures are verified through PayPal;
invalid headers are rejected before outbound verification. Requests are bounded
to 256,000 bytes. Failed provider verification returns a retryable error.

The fixture database and its invoice prefix must remain paired. Do not delete
them to reset an invoice, copy credentials between modules, or tunnel the main
workspace instead. An ephemeral tunnel stops when its process stops, and a new
run may have a different URL. Stable hosting and persistent storage remain
necessary for a reliable shared demonstration. For the main execution store,
omit `WEBHOOK_CHECK_FIXTURE` and use its own preserved invoice prefix.

The sanitized committed report is
[paypal-callback-2026-10-31.json](../datasets/reports/paypal-callback-2026-10-31.json).
Raw provider IDs and local configuration stay in ignored runtime files.
