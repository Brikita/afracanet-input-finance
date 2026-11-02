# AFRACANet AI

**From credit intelligence to inputs in a farmer's hands.**

One repository for credit intelligence, lender decisions, agricultural input
finance, PayPal execution and recorded collection. The credit service lives in
[modules/credit-intelligence](modules/credit-intelligence); the input-finance
frontend and API remain in `src/` and `backend/`. Both services retain separate
credentials, data ownership and explicit lender-authorized handoffs.

The public information route is `/about` (or the built `/about.html` entry).
It explains alternative credit assessment, chama/SACCO records, connected
evidence and graph data science, with an interactive teaching graph and a
preserved PayPal sandbox check. Its Aether Flow hero, public fonts and credited
Kenyan photographs form a separate public visual world; the working application
retains Waterline. See [the product-page record](docs/PRODUCT_PAGE_2026-11-01.md)
and [public design authority](src/features/product/DESIGN.md).
It needs no sign-in and makes no authenticated, AI or payment API calls.

## Repository layout

| Area                                                    | Location                       |
| ------------------------------------------------------- | ------------------------------ |
| Credit frontend, API and graph ownership                | `modules/credit-intelligence/` |
| Input-finance frontend and public product page          | `src/`                         |
| Input-finance API and PayPal execution                  | `backend/`                     |
| Shared synthetic/public reference datasets              | `datasets/`                    |
| Shared setup, process supervisor and integration checks | `scripts/`                     |
| Tests, CI, submission and platform documentation        | `tests/`, `.github/`, `docs/`  |

A single clone contains both modules. Each frontend keeps its own lockfile because
credit uses TanStack Start/Vite 8 while input finance uses Vite 6. The root shared
Python lock covers both active FastAPI services. See [monorepo setup](docs/MONOREPO.md)
and [migration provenance](docs/provenance/credit-import.json).

**Integration status:** the credit module now persists applications and individual
local officer decisions, then sends signed, retryable approvals and revocations.
This module verifies the sender's configured public key, lender/officer scope,
explicit farmer mapping and decision terms before activating credit. Manual
review and CSV import remain distinct fallback paths. See the
[connected-platform report](docs/CONNECTED_PLATFORM_2026-10-30.md) for setup,
verification and remaining work, and the [manual handoff reference](docs/APPROVAL_HANDOFF.md).

The [redesign and restructuring brief](docs/REDESIGN_AND_RESTRUCTURE.md) tracks
the new UX work. Frontend domain/transport/feature modules and backend
validation/authentication/transaction helpers now have explicit boundaries.
The execution-module restructure separates routes, contracts, services, provider
adapters, feature screens, and ordered styles. See the
[restructure record](docs/RESTRUCTURE_2026-10-30.md);
the selected Waterline direction is implemented in the working input-finance
workspace. It includes a scoped credit breakdown, searchable request queue,
selected-case actions, and responsive role screens. See the
[Waterline review](docs/WATERLINE_REVIEW.md), [frontend layout](src/README.md),
and [backend layout](backend/README.md).

For larger isolated graph and relational scenarios, use the
[scalable synthetic generator](datasets/SYNTHETIC.md). The development profile
contains 10,000 farmers and 24 months of authored history. Generated database and
CSV artifacts remain outside Git. The local connected development setup now loads
the pack into isolated Neo4j and PostgreSQL stores, while starting active
execution credit at zero; fresh checkouts still use the small demo until explicitly loaded.

## Current status

The [2 November completion sprint](docs/SPRINT_2026-11-02.md) tracks current
work, including the 175-second narrated demo. For a separate compact connected
environment, see [judge setup](docs/JUDGE_SETUP.md). Older dated reports retain
the state at their checkpoint.

The local demonstration works without service credentials. It includes:

- Farmer, lender, and agro-dealer workspaces with two illustrative farmer accounts.
- Catalogue orders, atomic credit/inventory reservations, and cancellation.
- Lender approval, supplier invoice creation, simulated payment, and collection.
- Transaction timelines and CSV reconciliation export.
- Server-side role and participant checks.
- PayPal **sandbox-only** invoicing and webhook adapter.
- Gemini structured request interpretation adapter.

**Default payments are simulated and the default parser is deterministic.**
Fictional starter people/credit/products require `SEED_DEMO_DATA=1`, explicitly
enabled by `.env.example` for the small walkthrough. Leave it off for empty or
loaded environments; compact judge profiles always disable starter seeding.
No money moves and no AI model is called in the default walkthrough.
PayPal sandbox authentication, invoice creation, sending, and draft recovery have
been checked with actual API calls. A USD 18 buyer sandbox payment was verified
and reconciled exactly once. A genuine resent callback was signature-verified and deduplicated. Gemini passed 24/24 synthetic development cases on 31 October 2026;
this is not a production accuracy claim. See the [provider check record](docs/PROVIDER_CHECKS_2026-10-31.md).
This version is a development prototype, not a submitted entry or a live lending service.

## Run the whole platform locally

Prerequisites: Python 3.13 and Node.js 22.16+.

```powershell
git clone https://github.com/Brikita/afracanet-input-finance.git
cd afracanet-input-finance
npm run setup
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path modules/credit-intelligence/.env)) { Copy-Item modules/credit-intelligence/.env.example modules/credit-intelligence/.env }
npm run dev:all
```

The supervisor starts four services and stops them together on Ctrl+C:

| Surface                       | Address                     |
| ----------------------------- | --------------------------- |
| Public product page           | http://127.0.0.1:5173/about |
| Input-finance workspace       | http://127.0.0.1:5173/      |
| Credit-intelligence workspace | http://127.0.0.1:5174/      |
| Input-finance API             | http://127.0.0.1:8000/      |
| Credit-intelligence API       | http://127.0.0.1:8001/      |

Create each environment file only if it does not already exist. Never copy one
module's credentials into the other. The default input access code is
`afracanet-demo`; credit officers must be provisioned individually. Graph and AI
context remain explicitly unavailable until configured. See [the complete setup,
existing local-state references and officer provisioning](docs/MONOREPO.md).
On macOS/Linux use `cp` for the two example-file copies; the npm commands are the same.

```powershell
npm run check:all       # both TypeScript projects
npm run build:all       # both frontends, sequentially
npm run test:backend    # both backend suites and signed cross-module check
npm run check:startup   # start/check/stop all four local services
npm run test:ui         # isolated input/public Edge journeys
npm run test:connected  # connected browser journey; configured local graph required
```

`npm run dev` and `npm run build` remain input-finance-only commands. Credit-only
commands can run with `npm --prefix modules/credit-intelligence run dev` or `build`.
Generated databases remain ignored; never delete an invoice-associated database.
The root API serves `dist/` after `npm run build` and an API restart.

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
Draft recovery has been verified against an actual sandbox invoice. Paid-payment
recovery, refunds, and cancellation still need provider-based validation. See PayPal's [invoice details reference](https://developer.paypal.com/api/invoicing/v2/invoices-get).

## Connect Gemini

```dotenv
AI_MODE=gemini
GEMINI_API_KEY=<your-key>
GEMINI_MODEL=gemini-3.5-flash-lite
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

Early eligibility-review submission target: **5 November 2026**
([organizer update](https://paypalaihackathon.devpost.com/updates)).

1. Replace the verified ephemeral PayPal callback with stable HTTPS hosting and broaden independent AI evaluation.
2. Verify the SMS sandbox channel and evaluate the workflow with real users.
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

## Farmer SMS updates

The farmer's **SMS updates** tab accepts an opted-in Kenyan mobile number and
English/Kiswahili preference. A six-digit code verifies the number before future
order updates are queued. Codes expire after ten minutes and permit five attempts;
requesting another code has a one-minute cooldown. Opting out suppresses queued
updates. Contacts and message previews are visible only in the farmer's own view.
The demo still uses shared-code identities; this is not production identity proof.

`SMS_MODE=demo` creates clearly labelled local previews without contacting a
gateway. Use **Preview next queued SMS**, read its code, and verify the number.
Order, issue, collection, and cancellation updates then enter a durable outbox.
Messages describing simulated payments carry a DEMO label. The dispatcher checks
open issues before preparing collection codes; messages already in flight or sent
cannot be recalled, and the collection endpoint enforces the hold again.

For the Africa's Talking simulator, configure:

```dotenv
SMS_MODE=sandbox
AFRICASTALKING_API_KEY=<your-sandbox-key>
AFRICASTALKING_SENDER_ID=<optional-sandbox-sender>
```

Restart the backend, request a fresh verification SMS, and select **Send next SMS
to sandbox**. Read the code in Africa's Talking's simulator. This adapter uses
only its fixed sandbox API host and `sandbox` username, following the provider's
[official SDK](https://github.com/AfricasTalkingLtd/africastalking-python/blob/master/africastalking/SMS.py).
Real handset delivery, SMS ordering, and USSD are not enabled.
Local demo verification does not carry over to sandbox mode; reverify the number.

To process queued jobs outside the browser, run:

```powershell
.\.venv\Scripts\python.exe scripts/dispatch_sms.py --limit 20
```

The worker claims each job once and calls the provider outside the transaction.
`SIMULATED` means no API call; `ACCEPTED` means sandbox acceptance, not delivery.
`REJECTED`, `UNCERTAIN`, and interrupted `SENDING` jobs require operator review;
there is no automatic retry that could duplicate a message. Queue processing is
an explicit command or browser action; a continuously running worker and delivery
receipt reconciliation remain future work. Never treat SMS status as payment proof.

## Evaluate the assistant

The labelled synthetic set in `evaluations/assistant-cases.json` covers English,
Swahili, mixed language, multiple inputs, unit/count ambiguity, unknown products,
and attempts to bypass the assistant's boundaries. Native-speaker and real-user
review remain necessary. The scorer requires exact product/count matches or an
actual clarification with no proposed items.

```powershell
# Local parser baseline; no model calls. Multi-product cases intentionally fail.
.\.venv\Scripts\python.exe scripts/evaluate_assistant.py --mode demo
# Calls the configured model using your local key; start with a small check.
.\.venv\Scripts\python.exe scripts/evaluate_assistant.py --mode gemini --limit 4
# Full labelled set after configuration is verified.
.\.venv\Scripts\python.exe scripts/evaluate_assistant.py --mode gemini --interval 3
```

Reports are saved under ignored `data/evaluations/` with mode/model, per-case
results, timing, and language/category breakdowns. The command exits with code 1
when a case fails. Demo baseline scores are never labelled as Gemini performance.
Gemini 3.5 Flash-Lite passed 24/24 cases with actual API calls on 31 October 2026.
The [recorded results](evaluations/results/gemini-2026-10-31.json) are a small
development-set check; they do not establish reliability on unseen farmer requests.

The demo parser is deliberately limited to one supported catalogue item at a time.
It asks for missing quantities and unknown products instead of using pack weight
as quantity or silently discarding the second item. Model output is also checked
for strict integer quantities, duplicate lines, unknown products, and extra fields.

## PostgreSQL integrity checks

CI runs the backend suite against SQLite and a PostgreSQL 16 service. Each
PostgreSQL test uses its own randomly named `test_afracanet_…` schema, then removes
only that schema. To run against a locally prepared PostgreSQL test database:

```powershell
$env:TEST_POSTGRES_URL='postgresql+psycopg://test_user:test_password@localhost:5432/test_database'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:TEST_POSTGRES_URL
```

Use a dedicated test account/database with schema-creation permissions. These
checks do not supply migrations, backups, or production operations procedures.

## License

Original input-finance code: [MIT](LICENSE), copyright 2026 Brikita. Credit code
is also released under [MIT](modules/credit-intelligence/LICENSE), following the
owner's permissions confirmation on 2 November 2026; see [its notice](modules/credit-intelligence/NOTICE.md). Photographs and
fonts retain separate licenses; see [sources and credits](docs/PRODUCT_SITE_CREDITS.md),
[the photographic asset manifest](docs/PRODUCT_SITE_ASSETS.json) and the font
notices in `public/licenses/`.
