# Connected platform and data — 30 October 2026

This implements plan items **1: connect credit intelligence to input finance**
and **2: load and connect the labelled development data**. The repos remain
separate modules of AFRACANet AI. This is a working local prototype, not a live
lending deployment or a completed hackathon submission.

## What now works

| Area | Implemented result |
| --- | --- |
| Credit applications | Persistent SQLAlchemy records, lender-scoped queues, search, status filters and real decision history |
| Officer authority | Individual local accounts with scrypt hashes, expiring bearer sessions, disabled-account checks, explicit authorization and server-derived officer/lender identity |
| Decisions | Immutable per-application approval/rejection records with integer USD cents, expiry, reason and provenance; AI summaries remain advisory |
| Automatic connection | Durable outbox, Ed25519 service signature, lender/officer public-key policy, timestamp checks, explicit farmer mapping, delivery receipts and bounded retry backoff |
| Duplicate/race handling | Stable delivery bodies/IDs, atomic receiver effects, durable receipts, reference locks and nonnegative commitment checks |
| Revocation | Source-side revocation outbox, unsent approval supersession, receiver tombstones for out-of-order messages, no restoration through retries or manual fallback |
| Navigation | Decision-reference continuation link; receiving workspace signs in independently and opens the scoped record. No token or private key in the URL |
| Payment boundary | Approval opens input requests; collection still requires payment evidence. Revocation preserves paid commitments and collection history |
| Workflow screens | Working officer review/history and delivery states; signed/manual labels in input finance; searchable, paginated credit records |

The legacy unauthenticated credit approve/reject/evaluate/queue/USSD endpoints
return 410. The in-memory queue, fallback farmer/score, hardcoded UI ledger and
approval message inviting collection were removed from the active workflow.
Verified USSD intake is deliberately not claimed. Input-finance contact and SMS
updates remain separately configured.

The sending private key stays in the credit module. Input finance receives only
public verification material. The local signing service is explicitly enrolled
for four synthetic lender/officer scopes; this is service attestation of the
authenticated officer action, not an officer-held personal signing certificate.
The receiving browser still uses labelled demonstration sessions with a shared
access code. Production identity/SSO integration remains additional work.

## Data loaded, rather than just exported

| Store | Actual local content |
| --- | --- |
| Neo4j Community 5.26.32 | **928,163 nodes; 1,886,728 relationships**; indexed entity IDs and tenant ownership |
| PostgreSQL 16.15 replay registry | 918,043 base entities, 1,876,548 base relationships, 784,656 ledger entries, 12,496 loans, 74,976 installments, 10,000 historical allocations and orders |
| Current-review overlay | 5,000 pending, 2,500 rejected, 2,500 historical approved cases; 60 inventory balance rows |
| Credit workflow database | 10,000 corresponding current-review cases; historical approvals have no delivery authority; four individual local officer accounts |
| Input-finance database | 10,000 mapped profiles and 60 products; initial active credit, orders and payment records all **zero** |
| Public context | 60 attributed Open-Meteo/ERA5 daily records attached to two reference regions |

All farmer and financial histories are authored synthetic replay. Public weather
is a separately labelled reanalysis source under CC BY 4.0. Reference-region
assignments are fictional; they are not verified farm locations. KES histories
and illustrative USD input amounts stay separate, with no exchange-rate
conversion. Replayed payments never enter the PayPal verification path.

The overlay supplements earlier historical approvals with current review
cohorts; it does not rewrite historical approvals as current lender decisions.
Historical inventory reconciles opening, fulfilled, remaining and reserved
units. Active execution uses separately labelled fresh illustrative stock.

The credit API reads replay history using a dedicated PostgreSQL SELECT-only
role. Each application database has a distinct owner account. Runtime
credentials, private keys, datasets and database files remain ignored and local.
The earlier application database is preserved; no existing graph/database was
cleared or overwritten. Development servers exclude runtime/dataset directories
from file watching.

## Evidence

- [Relational load report](../datasets/reports/connected-v1-relational.json):
  every base file checksum validated before loading; row counts and monetary
  sums agree with the original registry. Load took 349.93 seconds locally.
- [Overlay manifest](../datasets/reports/connected-v1-overlay.json): authored
  cohort counts, stock balances, parent manifest fingerprint and file hashes.
- [Cross-store verification](../datasets/reports/connected-v1-store-verification.json):
  all 10,000 farmer/lender pairs have the same digest across Neo4j, replay,
  credit workflow and input finance. All 60 product prices and replay inventory
  records agree. The replay reader has no INSERT permission.
- The same report records 50 indexed neighborhood queries: median **14.81 ms**,
  p95 **88.98 ms** on this laptop. This is a local query measurement, not a
  production throughput claim. The offline graph import took 196.21 seconds.
- [Combined workflow check](../datasets/reports/connected-workflow-check.json):
  both real FastAPI apps with isolated stores, real signing/verification, a lost
  acknowledgment, safe retry, blocked unpaid collection, revocation and preserved
  paid collection. Payment was explicitly simulated; zero provider calls.
- Automated Edge browser checks cover the two-module approval/delivery/link/
  independent sign-in/revocation journey and desktop/tablet/mobile layout.

GDS algorithms have **not** been run on this development pack. No calibrated
credit score, observed repayment outcomes or predictive validation is claimed.
The actual context API returns a missing score explicitly, while providing
retrieved graph relationships and public context. Optional AI summaries require
a configured provider and do not substitute a deterministic verdict.

## Run and inspect

Input finance: `http://127.0.0.1:5173/` (API 8000).
Credit intelligence: `http://127.0.0.1:5174/` (API 8001).
Neo4j browser: `http://127.0.0.1:17474/` (Bolt 17687).
PostgreSQL listens only on loopback port 15432.

Local officer sign-in details are in the credit repo's ignored
`data/local-officer-accounts.json`; do not paste them into chat or commit them.
Input finance uses its existing local demonstration access code. After opening
the workspace, select a synthetic lender, supplier or farmer through **View as**.

For a walkthrough, sign in as the first synthetic lender officer, search for
`farmer-synth-000001`, review graph context, and record an explicitly authorized
illustrative USD decision. Follow its delivery receipt and continuation link.
Sign into the matching receiving lender workspace. Request/approve inputs,
issue an invoice and verify payment before recording collection. Default payment
mode remains explicitly simulated until PayPal sandbox is configured.

The active credit-module commands/configuration are documented in
[its connected workflow](https://github.com/Brikita/afracanet-green-path/blob/main/docs/CONNECTED_WORKFLOW.md).
Windows portable runtimes were taken from the official
[Neo4j deployment center](https://neo4j.com/deployment-center/),
[Microsoft OpenJDK downloads](https://learn.microsoft.com/java/openjdk/download)
and [EDB PostgreSQL binaries](https://www.enterprisedb.com/download-postgresql-binaries).
These are user processes, not installed Windows services.

Loader and verification entry points:

```powershell
# Fresh setup only: refuses existing populated stores/graph instances.
.venv/Scripts/python.exe scripts/connected/bootstrap_local.py --credit-repo ../afracanet-green-path
# Scripts are importable so an operator can select fresh dataset/DB targets:
# scripts.connected.cohorts.build_overlay
# scripts.connected.load_relational.load
# scripts.connected.load_execution.load_execution
# credit module: scripts/load_workflow_cases.py, load_replay_graph.py, attach_public_weather.py

.venv/Scripts/python.exe -m pip install -r scripts/requirements-connected.txt
.venv/Scripts/python.exe scripts/check_connected_workflow.py --credit-repo ../afracanet-green-path
.venv/Scripts/python.exe scripts/check_connected_stores.py --credit-repo ../afracanet-green-path --report data/store-check.json
.venv/Scripts/python.exe -m pytest -q
npm run build
npm run test:ui
npm run test:connected
```

The connected browser check uses fresh temporary databases, officer accounts and
signing keys, with read-only access to the loaded graph/context registry. It
expects the sibling checkout and local graph to be available. Existing UI checks
can use `UI_TEST_API_PORT`/`UI_TEST_PORT` to avoid the running modules' ports.

## Remaining after these two items

1. Configure and verify real PayPal sandbox, AI-provider and SMS integrations;
   credentials remain module-specific. No live-provider pass is asserted here.
2. Decide and evaluate the actual credit-model/GDS pipeline with proper missing
   data, calibration, explainability and authorized lending partners.
3. Finish the whole-product visual unification and user-flow refinement. The
   input-finance Waterline system and incumbent credit-module green system are
   both preserved in this functional connection pass.
4. Deployment/production identity and operations, partner-data onboarding, the
   product information page, demonstration video and Devpost submission package.

An embedded legacy telecom key was removed from source. Its owner should rotate
it if active; removing source does not revoke a credential retained in history.
