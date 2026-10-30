# Connected credit workflow — 30 October 2026

AFRACANet AI is one product with separate credit-intelligence and input-finance
modules. This module owns graph evidence, optional AI summaries, durable
applications, individual local officer accounts, and lender decisions. The
[input-finance module](https://github.com/Brikita/afracanet-input-finance) owns
allocation execution, input orders, verified supplier payment, and collection.

## Active application

Run the API from this repository root:

```powershell
.venv/Scripts/python.exe -m pip install -r Backend/requirements.txt
.venv/Scripts/python.exe -m uvicorn Backend.main:app --host 127.0.0.1 --port 8001
npm ci
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5174 --strictPort
```

Use `.env.example` for configuration. Local setup generated four distinct officer
accounts in ignored `data/local-officer-accounts.json`. These are local prototype
accounts, not SSO or a production identity service. For a new individual account,
run `python scripts/provision_officer.py OFFICER_ID LENDER_ID`; the password is
requested privately in the terminal. Password hashes use scrypt; bearer sessions
expire after four hours and disabled accounts lose existing session access.

The database-backed queue supports search and status filters over all imported
cases, while rendering at most 100 matching rows. A selected case remains visible
after approval removes it from the pending queue. History is backed by actual
decision records; the previous hardcoded disbursement ledger is removed.

The existing green visual system is retained for this functional extension.
Whole-platform visual unification with the input-finance Waterline system is a
separate remaining design pass.

## Authority and delivery

1. An authenticated officer creates or selects a lender-scoped application.
2. Graph context is retrieved from that lender's Neo4j partition. Missing graph
   or AI-provider access returns an explicit unavailable state. No fallback
   farmer, credit score, recommendation, or approval is substituted.
3. The officer explicitly confirms lender authorization, sets integer USD cents
   and an expiry, and records a reason. The server derives officer and lender
   identity from the session. A recommendation never calls this action.
4. Approval and a serialized outbox event commit together. Rejections create no
   allocation or delivery. Each application has one immutable decision; new
   terms require a new application.
5. The delivery worker leases due events, closes its transaction, signs the exact
   body with Ed25519, and posts to `/api/credit-deliveries`. It stores the receipt
   or schedules a bounded exponential retry. Retry payload/event IDs stay stable;
   timestamps/signatures are renewed. Receiver conflicts remain visible for
   operator correction, rather than being treated as successful delivery.
6. The receiver validates the configured public key, lender/officer policy,
   timestamp and payload, then checks an explicit farmer mapping. No officer
   password, session token, or private signing key crosses into input finance.
7. The continuation link contains only a decision reference. Users authenticate
   separately in the receiving workspace; the link grants no authority.

Revocation creates a durable event and supersedes unsent approvals. A revocation
arriving before its approval creates a receiver tombstone, blocking a late
delivery or manual fallback from activating that reference. Paid commitments and
collection records remain intact; revocation is not a refund or invoice
cancellation. Approval does not tell farmers to collect; input finance owns
contact verification and updates about verified payment/collection readiness.

Unauthenticated legacy approve/reject/evaluate/pending/USSD routes now return 410.
USSD intake needs a separately verified provider adapter before re-enablement.
`Backend/app.py`, `Backend/at.py`, and `Featherless_LLM/` remain legacy research
entry points; they are not launched by the active application. An embedded
telecom key was removed from active and legacy orchestration code. If that old
key is still active, its owner must rotate it; deleting source does not revoke
credentials already present in Git history.

## Data ownership and provenance

The shared development pack has 10,000 fictional farmers and 24 months of
authored histories. An overlay adds 5,000 pending, 2,500 rejected and 2,500
historically approved review cases, plus 60 inventory rows. Historical approved
cases are labelled `REPLAY_APPROVED` and have no signing/delivery authority.

`scripts/load_replay_graph.py` verifies the supplied CSV hashes and imports into
a fresh Neo4j instance, with unique Entity IDs and an index on tenant ownership.
It refuses an existing instance and never runs the legacy destructive seeder.
The connected graph contains 928,163 nodes and 1,886,728 relationships, including
60 public weather records attached by `scripts/attach_public_weather.py`.
Public ERA5/Open-Meteo context is attributed under CC BY 4.0 and attached only to
reference regions. Those regions are fictional assignments for farmers, not
verified farm locations. Historical KES balances and illustrative USD input
amounts remain separate; there is no currency conversion.

`Backend/replay.py` reads the isolated PostgreSQL registry through a SELECT-only
account. The UI shows lender-scoped historical balances and provenance, separate
from active input credit. GDS algorithms have not been run on this pack; no
calibrated credit score, observed repayment outcome, or predictive validation is
claimed. A large graph establishes software scale, not lending-model validity.

## Verification

```powershell
.venv/Scripts/python.exe -m pytest -q Backend/tests
npm run build
npx tsc --noEmit
```

The sibling input-finance repository also provides:

- `scripts/check_connected_workflow.py --credit-repo ../afracanet-green-path`:
  both FastAPI apps, isolated databases, actual signing/verification, a lost
  acknowledgment, retry deduplication, revocation and preserved paid collection.
  Payment in this check is explicitly simulated.
- `scripts/check_connected_stores.py`: full farmer/lender ID comparison across
  all four stores, product/inventory parity and local query measurements.
- `playwright.connected.config.ts`: isolated two-module browser journey in Edge,
  graph/public-context reads, approval delivery, a token-free continuation link,
  separate receiving sign-in and revocation; desktop/tablet/mobile captures.

Real PayPal, AI-provider and telecom checks remain dependent on credentials.
