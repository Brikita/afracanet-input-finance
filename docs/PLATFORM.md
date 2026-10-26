# AFRACANet AI — unified product brief

Product direction agreed: 26 October 2026.

## Positioning

**AFRACANet AI helps agricultural lenders move from credit intelligence to
verified input payments and recorded farmer collection.**

Present one farmer journey under one AFRACANet AI brand. The credit-intelligence
and input-finance services are modules of that product, with clear ownership of
decisions and transaction facts. Keeping modular repositories supports this
direction without requiring duplicated underwriting code or shared credentials.

The target buyer remains an agricultural lender. Farmers and agro-dealers use
the same transaction journey. Business value to validate: staff time, fewer
reconciliation discrepancies, clearer status, and collection completion. Do not
claim reduced default, improved yields, unique market leadership, or production
readiness without evidence.

## Product modules

| Module                 | Responsibility                                                                | Source and current boundary                                                                                                    |
| ---------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Credit intelligence    | Application intake, graph/context assessment, AI rationale for officer review | [afracanet-green-path](https://github.com/Brikita/afracanet-green-path); reviewed source, not a newly verified live deployment |
| Lender decision        | Officer-authorized allocation, amount, expiry, and reference                  | Must be explicit; a model recommendation is not authorization                                                                  |
| Input finance          | Catalogue requests, lender order approval, reservations, dealer invoice       | This repository; manual CSV allocation import already exists                                                                   |
| PayPal execution       | Supplier invoice, lender payment, verified reconciliation                     | Adapter implemented; live sandbox verification remains outstanding                                                             |
| Collection and support | Farmer code, dealer handover, issues, audit/export, SMS updates               | Tested demonstration; external SMS verification remains outstanding                                                            |

## The combined journey

1. The farmer applies through the AI module's intake flow.
2. The officer reviews available credit intelligence and its provenance.
3. The lender authorizes a specific allocation and expiry.
4. That allocation is transferred to input finance against a mapped farmer ID.
5. The farmer confirms catalogue items and the quoted total.
6. The lender approves the order; the dealer confirms stock and issues an invoice.
7. The lender pays the supplier through PayPal sandbox; the server verifies payment.
8. The farmer receives collection instructions/code; the dealer records handover.
9. The lender reconciles decision, order, payment, and collection references.

Application approval, input-order approval, payment confirmation, and collection
are separate facts. Payment does not certify product quality or repayment.

## Review of the current connection point

Reviewed the AI repository at commit
[`fb8e3e1`](https://github.com/Brikita/afracanet-green-path/tree/fb8e3e175fcb5f0cdf5c164ea38855db3af91c0a)
on 26 October 2026. In its
[backend](https://github.com/Brikita/afracanet-green-path/blob/fb8e3e175fcb5f0cdf5c164ea38855db3af91c0a/Backend/main.py):

- `/api/approve` accepts a farmer ID, updates an in-memory queue, and queues SMS.
- It does not supply a monetary allocation or expiry for this module.
- Its approval SMS currently invites collection before a payment step exists.
- Assessment can fall back to illustrative graph data when its upstream is unavailable.

Consequently, an automatic, verified cross-module flow has not been demonstrated.
The website could not be inspected through the review tool; source review is not
runtime verification. This repository's passing checks apply to its own scope.

## Concrete integration plan

### 1. Establish one lender-authorized allocation

Use one synthetic demonstration farmer in both modules. Maintain a mapping such
as upstream `F-101` to execution `farmer-amina`; names alone must not establish
identity. Register which lender owns that mapping and allocation.

The proposed handoff contains:

| Field                            | Meaning                                                  |
| -------------------------------- | -------------------------------------------------------- |
| `approval_reference`             | Unique, stable lender decision reference                 |
| `source_application_id`          | AI portal application reference                          |
| `source_farmer_id` / `farmer_id` | Explicit cross-module identity mapping                   |
| `lender_id` / `approved_by`      | Authorized lender and officer identity                   |
| `limit_cents` / `currency`       | Total allocated ceiling and its actual currency          |
| `expires_at` / `approved_at`     | Timezone-aware expiry and decision timestamp             |
| `decision`                       | An explicit lender approval, not the AI verdict          |
| `data_provenance`                | Whether upstream assessment used real or fallback inputs |

This is a proposed contract, not a currently implemented API. Add validation,
lender authentication, stable retry keys, replay handling, and persistence before
exposing a direct integration. Never accept model prose as authorization.

### 2. Use the existing manual import as the first demonstrable bridge

The lender reviews the decision, assigns an illustrative USD sandbox allocation,
and imports the existing CSV columns:
`farmer_id,name,location,limit_cents,expires_at,approval_reference`.

This format does not carry every proposed contract field. An explicit handoff
record must retain the source application, officer, mapping, and provenance.
Label the bridge as manual until a tested automatic adapter replaces it.

Keep a stable allocation reference: an update must preserve spent/reserved credit.
Do not convert a historic KES amount into USD by relabelling its currency. Set an
explicit illustrative sandbox amount or implement a separately validated conversion.

### 3. Connect the officer experience

After approval, the AI portal should offer **Continue to input finance**, showing
the approved amount, expiry, and linked reference. The execution service must
independently validate authorization; a browser link or query parameter alone
cannot create credit. Do not put tokens or national IDs in the URL.

Keep the lender's credit decision distinct from approval of the subsequent
catalogue order. A first combined demo may use labelled manual transfer; a future
shared dashboard should navigate both modules without asking judges to infer links.

### 4. Correct the communication sequence

- After intake: application received, awaiting lender review.
- After lender decision: allocation approved; proceed to request/review inputs.
- After verified supplier payment: collection instructions/code, subject to issue holds.
- After handover: collection recorded; provide the support route.

Reuse the existing USSD application capability upstream where it is verified.
Payment status and collection access through USSD require integration work; the
execution module currently supports app interaction and outbound SMS previews.

### 5. Verify one continuous story

Demonstrate a source application, an officer approval, the mapped allocation,
an input order, a PayPal invoice/payment, and collection. Retain the corresponding
references and distinguish simulated/fallback modes at each stage. Test expiry,
replayed handoff, wrong farmer/lender mapping, revoked approval, and payment failure.
An approval revocation must not silently undo an already-paid transaction.

## Engineering findings to address before live connection

The reviewed AI backend contains a hardcoded Africa's Talking credential and
disabled TLS verification for some outbound requests. Revoke/rotate any active
exposed key, load fresh credentials from that service's own environment, and use
certificate verification. No credential values are reproduced here.

Its approval/evaluation endpoints need lender authentication and its decision
queue needs durable storage before it can authorize execution. Upstream fallback
assessment must be labelled and must not silently create a genuine credit decision.
Avoid sending national identity numbers in routine progress messages.

These findings do not change the financial integrity rules in this execution
module. They are concrete connection work, not evidence that the modules already
share trusted identities or a production security boundary.

## Presentation and submission

Use **AFRACANet AI** as the project name, with **Credit Intelligence** and
**Input Finance powered by PayPal** as module descriptions. The new story is
the expansion from assessed credit to verified input-finance execution.

Explain the existing AI foundation and newly built PayPal functionality separately.
The [official hackathon rules](https://paypalaihackathon.devpost.com/rules) allow
significantly updated existing projects, subject to organizer determination, and
require PayPal to be central. Confirm rights/licensing across both repositories
and provide one reproducible setup or working demonstration.

The product information page, animations, deck, and video should use this shared
journey after the core connection and external integrations are demonstrated.
See [submission preparation](SUBMISSION.md) for the combined demo outline.
