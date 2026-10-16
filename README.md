# AFRACANet Input Finance

**From approved agricultural credit to inputs in a farmer's hands.**

An independent prototype for Kenyan agricultural input finance. Farmers request
approved catalogue items, lenders approve and pay supplier invoices, and dealers
record collection. Each transaction connects credit, inventory, payment, and
fulfilment in one traceable record.

This repository is separate from
[afracanet-green-path](https://github.com/Brikita/afracanet-green-path).
It starts with existing credit approvals and has no underwriting, Neo4j, or GDS
dependency. All code here was created independently for this execution workflow.

## Current status

The local demonstration works without service credentials. It includes:

- Farmer, lender, and agro-dealer workspaces with two illustrative farmer accounts.
- Catalogue orders, atomic credit/inventory reservations, and cancellation.
- Lender approval, supplier invoice creation, simulated payment, and collection.
- Transaction timelines and CSV reconciliation export.
- Server-side role and participant checks.
- PayPal **sandbox-only** invoicing and webhook adapter.
- Gemini structured request interpretation adapter.

**Default payments are simulated and the default parser is deterministic.**
No money moves and no AI model is called in the default walkthrough.
External PayPal and Gemini adapters still require credential-based verification.
This version is a development prototype, not a submitted entry or a live lending service.

## Run locally

Prerequisites: Python 3.13 and Node.js 22.

From a fresh checkout, on Windows PowerShell:

```powershell
git clone https://github.com/Brikita/afracanet-input-finance.git
cd afracanet-input-finance
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock.txt
npm ci
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Keep the backend terminal open. In a second terminal, from the project root:

```powershell
npm run dev
```

Open **http://127.0.0.1:5173/**. The default demo access code is
**afracanet-demo**. The app's access code must match DEMO_ACCESS_CODE in .env.

On macOS/Linux, use python3 -m venv .venv and .venv/bin/python in place of
the Windows Python executable. The other commands are the same; copy the
environment example with cp .env.example .env.

The backend creates an ignored local SQLite database under data/.
Do not delete a database associated with real sandbox invoices: retain the
order and provider references for reconciliation.

### Built frontend

Run npm run build, then start/restart the backend. When dist/ exists at backend
startup, FastAPI also serves the application at http://127.0.0.1:8000/.

## Demonstrate the complete journey

1. Choose **Farmer experience** and open the workspace.
2. Enter **Need 2 bags of DAP**. Interpret it; the demo parser asks for bag size.
3. Replace the request with **Nahitaji mifuko 2 ya DAP ya kilo 50**.
4. Interpret and review the two 50 kg bags, then confirm the request.
5. Close the transaction drawer. Use **View as** to choose the lender.
6. Open the order and approve it.
7. Switch to the dealer. Confirm stock and issue the simulated invoice.
8. Switch to the lender and simulate payment.
9. Switch to Amina. Open the order and read the collection code.
10. Switch to the dealer, enter that code, and record collection.
11. Inspect the timeline and export the lender's reconciliation records.

All identities, prices, stock, and credit limits are illustrative.
USD values are sandbox examples, not current Kenyan agricultural prices.

## Connect PayPal sandbox

Set these values in your ignored .env file:

```dotenv
PAYMENT_MODE=sandbox
DEMO_ACCESS_CODE=<unique-code-at-least-16-characters>
PAYPAL_CLIENT_ID=<supplier-business-sandbox-app-client-id>
PAYPAL_CLIENT_SECRET=<supplier-business-sandbox-app-secret>
PAYPAL_MERCHANT_EMAIL=<that-supplier-business-sandbox-account-email>
PAYPAL_LENDER_EMAIL=<lender-personal-sandbox-account-email>
PAYPAL_WEBHOOK_ID=<optional-until-public-webhook-endpoint-is-configured>
```

Restart the backend and create a **new order** in sandbox mode. Old simulated
orders cannot be paid through the sandbox adapter.

Credentials must belong to the supplier's sandbox business account. This initial
version supports one controlled supplier account, not third-party merchant
onboarding. The lender signs into its separate sandbox buyer account and pays
the hosted invoice; the server does not automatically debit the lender.

To receive notifications, expose the backend through an HTTPS endpoint and
register /api/webhooks/paypal on the same PayPal REST app. Subscribe to
INVOICING.INVOICE.PAID and set PAYPAL_WEBHOOK_ID. The authenticated
**Check PayPal payment status** action can also reconcile a completed payment.

The server rejects partial, pending, mismatched, and externally recorded invoice
payments. It verifies full PayPal transaction records before unlocking collection.
Simulated payment endpoints are disabled in sandbox mode.

If invoice creation/sending is uncertain, the order stays under operator review
and its credit remains reserved. In the dealer's transaction drawer, use
**Recover an existing invoice** with the saved reference or the `INV2-…` ID
found in the supplier's PayPal sandbox dashboard. Recovery fetches provider
records and checks the order number, reference, supplier, lender, amount, and
currency. It never creates another invoice or sends one automatically.
For an interrupted `INVOICING` request, wait at least two minutes.

A sent/unpaid invoice restores the lender's payment link. A full, verified PayPal
payment unlocks collection. A draft remains under review: send that same invoice
from PayPal's dashboard, then recover again. A cancelled invoice releases
reservations only when its provider records also establish zero payment and the
full original amount still due. Partial payments, refunds, uncertain or missing
records remain held for operator review; automated refunds are not implemented.
The recovery adapter is covered by controlled-response tests and still needs
live sandbox validation. See PayPal's [invoice details reference](https://developer.paypal.com/api/invoicing/v2/invoices-get).

## Connect Gemini

```dotenv
AI_MODE=gemini
GEMINI_API_KEY=<your-key>
GEMINI_MODEL=gemini-2.5-flash
```

Restart the backend. Request interpretation calls Gemini with a structured
schema and a catalogue containing product identifiers, names, and units.
Farmer identity and credit data are not included in the interpretation prompt.
Unknown catalogue items are rejected; application code determines prices and
enforces credit limits. The farmer confirms the proposed order.

Model availability and language quality must be evaluated with your actual key.
The demo parser is a limited walkthrough aid, not a model-quality evaluation.

Keep credentials on the server and out of chat, browser source, and Git.
Run the configuration checker to view presence checks without exposing values:

```powershell
.\.venv\Scripts\python.exe scripts/check_configuration.py
```

## Checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm run build
npm run test:ui
```

Browser tests start isolated servers on ports 8001 and 5174 and use temporary
data; they do not reset the development database. Edge is used on Windows.
On Linux/macOS install Chromium with npx playwright install chromium first.
PLAYWRIGHT_CHANNEL may override the browser channel.

The checks cover financial limits, concurrency, role isolation, cancellation,
idempotent payment/collection effects, unsafe payment records, webhook verification/replay,
approval imports, stale catalogue edits, invoice recovery, issue holds/resolutions,
the three-role browser journey, and mobile management and overspending scenarios.
They use controlled provider responses and do **not** replace real sandbox testing.

## Project structure

```text
backend/             FastAPI, database, PayPal and assistant adapters
src/                 React application and responsive styles
tests/               Backend integrity and browser workflow checks
scripts/             Configuration check and isolated browser server
docs/BUILD_PLAN.md    Delivery gates and pilot/commercial hypotheses
docs/ARCHITECTURE.md  State transitions, data rules, access, limitations
docs/SUBMISSION.md    Demo outline and submission checklist
```

## Next delivery gates

Internal submission target: **30 October 2026**.

1. Verify real PayPal sandbox payment and Gemini interpretation.
2. Add SMS access and evaluate the workflow with real users.
3. Validate PostgreSQL, improve hosted access, and prepare a hosted demonstration.
4. Record the public demonstration, finalize evidence, and submit through Devpost.

See [the build plan](docs/BUILD_PLAN.md) and
[submission checklist](docs/SUBMISSION.md). The project must not be presented as
ready for judging until its PayPal and AI functionality has actually been verified.

## Manage approvals and catalogue

In the lender's **Credit allocations** tab, download the CSV template, then upload
or paste externally approved allocations. Preview validates the complete batch;
Import revalidates and saves all rows in one transaction. Columns, in order:
`farmer_id,name,location,limit_cents,expires_at,approval_reference`.
IDs start with `farmer-`; limits use whole USD cents; expiry includes a timezone.
The limit is a total allocation, including already reserved and paid credit.
Imports preserve these balances and cannot transfer a farmer between lenders.
Repeated imports update the allocation; they do not replenish spent credit.
New farmers appear in the authenticated demo **View as** switcher. This remains
a shared-code demonstration identity model, not individual farmer authentication.

In the dealer's **Inventory** tab, add products or edit names, packs, prices,
and total on-hand stock. Existing orders retain their quoted prices. Stock cannot
fall below reservations. An edit opened before stock or catalogue changes must
be reopened before saving, so stale forms cannot overwrite newer changes.
Management changes are recorded in the `management_events` database table.

## Handle issues

Any participant can report a stock, payment, collection, or other issue from the
transaction drawer. The report is visible to the participants on that order.
Open issues pause further approval, invoice creation, payment initiation through
the app, and collection. Existing external payments can still arrive; verified
payments are reconciled and recorded while collection remains on hold.
Previously opened PayPal links cannot be revoked by an application issue hold.

The lender records a resolution after checking with the participants. Resolving
an issue never refunds money, releases credit, or marks collection by itself.
Those actions continue to use their transaction rules and provider evidence.
Pre-invoice cancellation remains available and releases reservations once.
Issue reports and resolutions remain in the transaction timeline. Retrying an
identical issue report or a completed collection does not repeat its effects.

## License

[MIT](LICENSE). Copyright 2026 Brikita.
