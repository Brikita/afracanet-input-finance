## Inspiration

A farmer can have years of chama savings, SACCO repayments and cooperative records yet little conventional asset collateral. Approval alone also does not put seed or fertilizer in their hands. AFRACANet connects evidence review to accountable execution.

## What it does

An officer inspects lender-scoped financial histories, source records and descriptive graph analytics. Neo4j GDS computes PageRank and Louvain communities; Gemini provides evidence-cited advisory explanations and highlights missing information. The lender explicitly owns the credit decision. A signed authorization carries approved terms into the separate input-finance service.

The farmer requests catalogue inputs in English or Swahili, reviews the AI-interpreted quote and confirms it. The server reserves credit and supplier stock atomically. The lender separately approves the input order, the supplier issues a PayPal invoice, and collection stays blocked until actual PayPal payment records match the invoice, amount and currency. The dealer records demonstration handover using the farmer's collection code.

## How we built it

One MIT-licensed repository contains two React/TypeScript frontends and two FastAPI services. SQLAlchemy manages transactional state; PostgreSQL/SQLite and Neo4j support workflow and evidence stores. Ed25519-signed approval/revocation delivery preserves service boundaries without sharing officer sessions or private signing keys. Gemini uses structured outputs with server validation. PayPal sandbox Invoicing, verified webhooks and authenticated reconciliation support payment execution and recovery. The hosted workspaces run on Render.

## Challenges

Recommendations, lending authority, payment and pickup are different events. Remote invoice outcomes can also be uncertain. In an earlier linked rehearsal we recovered the same existing PayPal draft instead of creating a duplicate. In the new hosted rehearsal, unpaid collection remained blocked until payment was verified. Missing evidence and provider timeouts remain visible.

## Accomplishments

The new browser recording follows **AFC-000002**, one 2 kg pack of maize seed priced at **USD 18**, through a fresh Gemini catalogue request, order confirmation, lender order approval, supplier invoicing, owner-completed PayPal sandbox payment and recorded collection. Its timeline identifies the PayPal webhook as the source of payment confirmation.

The same order retains references to the existing officer authorization and signed handoff. Separate authenticated repeat checks returned successfully while preserving one payment-confirmed event and one collection event. Actual bounded GDS runs retain dataset/version/parameter provenance.

The earlier release baseline passed 179 backend tests, both frontend builds, browser journeys and a fresh Linux compact judge rehearsal. Those are dated release results, not a new test count for this documentation update. See the [hosted evidence record](https://github.com/Brikita/afracanet-input-finance/blob/main/datasets/reports/hosted-sandbox-2026-11-12.json).

## What we learned

Reliable automation requires traceable evidence and explicit authority. Synthetic histories demonstrate workflow controls, but do not establish repayment prediction or real-world impact.

## Existing work and new contributions

Credit-intelligence code predates this PayPal expansion. Hackathon additions include input ordering, atomic credit/stock reservations, supplier invoicing, payment verification/reconciliation, collection and issue controls, signed cross-module authorization, connected tests and unified release tooling. Ownership/contributor permissions for MIT release were confirmed; prior authorship and third-party notices remain intact.

## Disclosures and limitations

People and financial histories are fictional. Payments use actual PayPal sandbox APIs and test funds; no real-money payment or physical delivery of goods is claimed. A recorded collection does not certify product quality. GDS results are descriptive, not calibrated credit scores. AI remains advisory and cannot approve credit.

The video inspects a recorded Gemini advisory pinned to an existing officer decision, then makes a fresh catalogue request. It is not a fresh independent credit-AI evaluation. Earlier weather/provider limitations and development-set results remain documented in the repository; no independent model-accuracy claim is made. Buyer login and checkout setup were omitted while recording was paused. Repeat reconciliation/collection checks were separate from the filmed clicks.

Codex assisted development, testing, documentation and video assembly. Gemini powers product interpretation and advisory summaries. The expanded video uses Rekam Basic's Michael narration. The local master is 8:00 at 1080p/30 fps; YouTube/Devpost display 8:01. **The first 2:50 contains the complete project pitch and working evidence**, followed by the detailed walkthrough.

## Try the hosted prototype

- [Product and context](https://afracanet-inputs.onrender.com/about)
- [Credit officer workspace](https://afracanet-credit.onrender.com/)
- [Input-finance workspace](https://afracanet-inputs.onrender.com/)
- [Hosted judge walkthrough](https://github.com/Brikita/afracanet-input-finance/blob/main/docs/HOSTED_WALKTHROUGH.md)
- [Source code and MIT license](https://github.com/Brikita/afracanet-input-finance)

Use the demonstration access supplied in the private testing instructions. Start with **farmer-synth-000001 / SYN-LENDER-000**, then inspect **AFC-000002** in input finance. Its recorded payment and collection can be inspected without making another purchase. AFC-000001 is the older unpaid order.

For an isolated local reproduction, use [compact judge setup](https://github.com/Brikita/afracanet-input-finance/blob/main/docs/JUDGE_SETUP.md). Local default mode uses deterministic parsing and simulated payments; configured provider mode is separate. Hosted users do not need their own Gemini keys, PayPal API secrets, graph passwords or signing keys.

## What is next

A willing lender/dealer pilot using authorized records, independent evaluation and workflow feedback. Production identity, live messaging, merchant onboarding and refund operations remain subsequent work.
