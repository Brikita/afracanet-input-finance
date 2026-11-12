# AFRACANet AI — submission copy

## Current copy, 12 November 2026

Use [DEVPOST_STORY.md](DEVPOST_STORY.md) for the current public project story and
[HOSTED_WALKTHROUGH.md](HOSTED_WALKTHROUGH.md) for hosted judge instructions.
The expanded video is https://www.youtube.com/watch?v=YEZz_objHR0; the complete
pitch and working evidence end at 2:50, followed by the detailed walkthrough.
The hosted paid/collected order is **AFC-000002**, not AFC-000001.
Supply scoped demonstration access only in the private Devpost testing field.
Never copy provider credentials, officer sessions or signing keys into that field.

## Historical draft, 3 November 2026

The draft below records the earlier local release and 175-second film. Its
upload, hosting and video-specific statements are historical and are superseded
by the current copy linked above; it is retained for provenance.

Draft for the final submission. Video and testing-access fields remain to be
completed with verified links/access details. Do not submit placeholder values.

## Project name

AFRACANet AI

## Tagline

Connect alternative financial evidence to lender-approved farm inputs and verified PayPal payments.

## Inspiration

A farmer can have useful financial history in a chama, cooperative or SACCO and
still struggle to present it in a lender's conventional assessment process.
Approval alone also does not put seed or fertilizer in that farmer's hands.
Someone must coordinate the request, supplier stock, invoice, payment and pickup.

We built AFRACANet AI around that whole journey: help an officer inspect connected
evidence, preserve the lender's decision, and carry authorized terms into a
traceable input-finance workflow. Our first intended audience is agricultural
lenders, farmers and agro-dealers. Access to a willing pilot partner remains a
next step; the prototype does not claim a deployed customer programme.

## What it does

An officer opens a lender-scoped case, follows connected source records and
inspects descriptive graph analytics. Neo4j GDS computes PageRank and Louvain
communities on a bounded synthetic membership graph. Gemini can summarize the
retrieved evidence with citations and explicit missing information. These
measurements and summaries do not decide creditworthiness or approve credit.

An authenticated officer explicitly records authorized terms. A durable outbox
sends an Ed25519-signed decision to the input-finance service. The receiver checks
sender/lender/officer policy, farmer mapping, expiry and terms before activating
the allocation. Revocations and retries preserve existing commitments and history.

The farmer requests catalogue items, with English/Swahili AI interpretation and
clarification available, then confirms the proposed order. The server reserves
credit and stock atomically. The lender approves the input order; the dealer
issues the supplier invoice; the buyer pays through PayPal sandbox.

Collection stays blocked until authenticated PayPal payment records match the
invoice, amount and currency. The farmer then obtains a collection code and the
dealer records handover. Issues can pause forward actions while incoming verified
payments are still reconciled. Timelines and reconciliation exports preserve the
distinction between approval, payment and collection.

## How we built it

One repository contains two React/TypeScript frontends and two FastAPI services.
SQLAlchemy owns transactional workflow data; PostgreSQL and Neo4j support the
larger local development registry/graph. The compact judge profile uses separate
SQLite workflow stores and a read-only authored replay registry with its own
Neo4j instance. Neither runtime imports replayed payments as PayPal evidence.

PayPal Invoicing REST APIs create/send supplier invoices and retrieve actual
payment records. The webhook adapter verifies signatures through PayPal and
deduplicates events. Authenticated reconciliation provides an independent recovery
route. Provider requests stay outside database transactions.

Gemini uses structured outputs for request interpretation and evidence-cited
advisory summaries. Server validation constrains catalogue IDs/quantities,
citations and numeric claims. Money and stock rules remain server-controlled;
the farmer confirms the request and the officer explicitly owns the decision.

The public product page explains the journey with credited Kenyan photographs,
graph teaching illustrations and controllable automatic tours. Working screens
use the shared Waterline design. The teaching diagram and computed working GDS
results are labelled separately.

## Challenges we ran into

The difficult boundary was turning evidence into execution without turning an AI
explanation into lending authority. We made the handoff signed, scoped, durable
and retryable, with revocation and exactly-once business effects.

Remote outcomes can be uncertain. During the connected sandbox rehearsal, PayPal
created a draft but its self-link used the second canonical sandbox API hostname.
The workflow held the order for review. We correlated and recovered that existing
draft instead of creating a duplicate, then sent it and verified the owner's
sandbox buyer payment. Both host formats now have parser coverage.

Missing evidence also needs care: absent weather must remain unavailable rather
than appearing as zero rainfall, and stored summaries must retain the exact
evidence references reviewed. Provider timeouts remain visible instead of being
replaced with invented success.

## Accomplishments

- One continuous fictional case connected actual Gemini, explicit synthetic
  officer authorization, signed delivery, a new USD 18 PayPal sandbox payment and
  a recorded demonstration collection.
- Repeated reconciliation and collection retained one payment-confirmed event
  and one collection event with unchanged balances/stock.
- Actual PageRank/Louvain results have run/version/dataset provenance and can be
  inspected in the working officer screen. Decisions retain selected graph and
  AI evaluation references.
- The larger labelled development world contains 10,000 fictional farmers over
  24 months, with recorded graph counts of 928,163 nodes and 1,886,728 relationships.
  The compact GDS run is separate from that larger pack.
- The release baseline passed 179 backend tests, 12 local browser journeys,
  both frontend builds and a fresh Linux compact-graph/GDS CI rehearsal.

## What we learned

Reliable automation depends on clear authority and evidence. A recommendation,
an officer decision, a provider payment and a pickup record are different events.
Keeping those boundaries explicit made retries, recovery and explanations easier
to inspect. Synthetic data is useful for demonstrating these controls, but it
does not establish real repayment prediction or commercial impact.

## What's next

Work with one willing lender/dealer partner on authorized data and workflow
validation. Broaden unseen bilingual AI evaluation and independent factual review.
Validate any future credit model against observed outcomes before making scoring
claims. Production identity, merchant onboarding, live messaging, refund policies
and hosted operations are subsequent pilot work.

## Existing work and hackathon contributions

AFRACANet's credit-intelligence code existed before the PayPal expansion. It was
imported with sanitized, history-preserving provenance into the unified repository.
The PayPal expansion added input orders, atomic credit/inventory reservation,
supplier invoicing, actual payment verification/reconciliation, collection and
issue controls, signed approval/revocation delivery, connected checks and shared
release tooling. The recent sprint added the compact judge profile, active GDS
pipeline, reviewed evidence references and unified presentation work.

The owner confirmed ownership/contributor permissions for MIT release of the
credit module. Both modules include MIT licenses; third-party dependencies,
photographs and fonts retain their own notices/terms.

## Tools and AI disclosure

- Product AI: Gemini structured request interpretation and evidence-cited summaries;
  inference only, with no model training or autonomous lending/payment authority.
- Graph analytics: Neo4j Graph Data Science PageRank and Louvain on labelled
  synthetic membership data; descriptive results, not calibrated credit scores.
- Payments: PayPal sandbox OAuth, Invoicing REST APIs, payment-record retrieval,
  signature verification and authenticated reconciliation.
- Application: React, TypeScript, FastAPI, SQLAlchemy, PostgreSQL/SQLite,
  Neo4j, Ed25519 signing and Playwright/GitHub Actions verification.
- Development assistance: OpenAI Codex assisted implementation, refactoring,
  testing and documentation. Gemini assisted product functions as described above.
  Narration was generated using Rekam Basic's Michael voice through its official
  no-account interface. The final narrated MP4 was exported and technically
  verified at 175.000 seconds, 1920×1080 and 30 fps.
- Data: fictional generated histories; separately attributed Open-Meteo/ERA5
  historical reference weather. No live partner chama/SACCO/merchant feed.

## Testing access and required links

Repository: https://github.com/Brikita/afracanet-input-finance

Working-build instructions: https://github.com/Brikita/afracanet-input-finance/blob/main/docs/JUDGE_SETUP.md

Verified release CI: https://github.com/Brikita/afracanet-input-finance/actions/runs/41518097793

Public video: **175-second MP4 exported locally; public YouTube upload and playback verification pending**.

Hosted functional demo: **not yet supplied**. Use the complete local-run route;
loopback addresses are available only on the machine running the services.
Provider-backed testing requires separately configured sandbox/model access.
Provide scoped test-access instructions privately where needed. Never publish
provider secrets, signing private keys or real personal/financial records.

## Evidence limits

The linked rehearsal uses fictional people/histories and actual sandbox APIs.
No real money or agricultural goods are claimed to have moved. The 31 October
genuine callback verification is a separate fixture from the 2 November linked
payment/collection scenario. Initial Gemini results include a 24-case development
set used in prompt refinement and a few cited summaries; these are not independent
accuracy studies. The project is a functioning development prototype.

The stored advisory shown in the recording predates the missing-weather
correction and contains a known zero-rainfall statement. Its reviewed record is
preserved rather than rewritten; the video labels this limitation. Current code
preserves missing weather as unavailable. The later provider attempt timed out,
so this is not claimed as an independently revalidated credit-AI evaluation.
