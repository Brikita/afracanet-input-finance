# Provider checks â€” 31 October 2026

The input-finance backend now runs locally with `PAYMENT_MODE=sandbox` and
`AI_MODE=gemini`. Credentials and the generated workspace access code stay in
the ignored root `.env`. The credit-module AI summary is not enabled by this
change; credentials were not copied between repositories.

## PayPal sandbox

Actual provider checks passed for OAuth authentication, Invoicing API access,
draft creation, existing-draft recovery, invoice sending, and matching the
invoice's supplier, buyer, reference, amount and currency. The buyer completed
the USD 18 sandbox payment, and actual PayPal payment records were verified.
The local order is now `READY_FOR_COLLECTION`. Reserved credit is zero, spent
credit is 1,800 cents, and exactly one `PAYMENT_CONFIRMED` event exists. Repeating
reconciliation preserved the order, pickup code, credit, inventory and event
count. No real money has moved and no collection has been recorded.
[Sanitized payment-check evidence](../datasets/reports/paypal-sandbox-2026-10-31.json).

The check uses its own persistent SQLite database under ignored
`data/provider-checks/`. Its seeded credit and catalogue are explicitly synthetic
fixtures, not upstream lender decisions. The 10,000-farmer execution database was
not allocated credit or charged by these checks.

Enabling Invoicing in the sandbox REST app resolved an initial HTTP 403. A second
check exposed a minimal invoice-create response containing a self link instead
of an invoice object or nested links. The adapter now accepts these forms and
validates the invoice reference. The existing remote draft was recovered and
sent; no second invoice was created. Regression coverage includes malformed and
non-sandbox invoice links.

The configured webhook ID belongs to the same REST app, uses HTTPS, and includes
`INVOICING.INVOICE.PAID`. A genuine event was subsequently resent by PayPal to
an isolated callback-only listener and its signature verified through PayPal.
Repeated delivery preserved one event receipt and one payment effect. The
payment had already been confirmed by authenticated manual reconciliation;
the callback check did not initiate a payment or first confirm its state.
[Sanitized callback evidence](../datasets/reports/paypal-callback-2026-10-31.json).

The temporary Cloudflare URL exposes only `/health` and `/api/webhooks/paypal`.
It is not stable hosting. See [callback setup](CALLBACK_SETUP.md) before restarting
or replacing it. Physical collection has not been recorded in this provider fixture.

Use a separate `PAYPAL_INVOICE_PREFIX` for each database sharing a sandbox app.
Keep a store's prefix unchanged once it has invoices. The empty main local store
now uses `AFCDEV`; the first historical check fixture retains `AFC`. New check
fixtures persist a separate generated prefix. This avoids consuming the same
invoice number in two independent stores.

```powershell
# Creates/sends one isolated test invoice; does not automatically pay it.
.venv/Scripts/python.exe scripts/check_paypal_sandbox.py --create
# Reuses that store and verifies provider records after manual sandbox payment.
.venv/Scripts/python.exe scripts/check_paypal_sandbox.py
```

Keep this database if an invoice was created. An uncertain creation remains held
for recovery; the runner does not blindly recreate an unrecorded invoice.

## Gemini

The configured older model returned HTTP 404 with an explanation that it was
unavailable to new users. Model discovery and Google's pricing page identified
`gemini-3.5-flash-lite` as an accessible model with a free tier. It is now the
default model for new configuration.

Initial evaluation found guesses for missing quantities and pack sizes, plus
request failures. The prompt now explicitly requires the missing information,
and the evaluator supports spacing calls and records HTTP status codes without
provider bodies or credentials. The final run made actual API calls and passed
**24/24** English, Swahili and mixed-language labelled development cases.
[Per-case evidence](../evaluations/results/gemini-2026-10-31.json).

This small set guided prompt changes and is not an independent test set. Native
speaker review, broader unseen examples, repeated evaluations and real-user
validation remain outstanding. The assistant suggests catalogue items; server
code sets prices and enforces credit, authorization and payment requirements.
The farmer must confirm the proposed order.

## Remaining provider evidence

- Exercise paid recovery, cancellation and refund scenarios against the provider.
- Broaden unseen-language request evaluation and independent review of AI summaries.
- Verify SMS delivery if retained in the demonstration.
- Replace the ephemeral callback with a stable hosted HTTPS endpoint.

Local regression verification passed: **145 backend tests** and **six Edge browser
journeys** with isolated test data. The provider runner additionally passed
actual paid reconciliation and duplicate-effect checks. The credit module's
separate Gemini key produced three schema/citation-checked summaries; that small
check is not an accuracy study. Its backend passed 16 tests. A connected Edge
journey verified scoped evidence inspection, explicit lender authorization,
signed delivery, independent receiving sign-in and revocation.

Provider references: [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing),
[PayPal invoicing quickstart](https://developer.paypal.com/api/invoicing),
[invoice creation reference](https://developer.paypal.com/api/invoicing/v2/invoices-create/).
