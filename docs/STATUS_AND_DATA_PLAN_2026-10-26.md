# AFRACANet AI: comprehensive status and data plan

Assessment date: 26 October 2026. User direction: one AFRACANet AI product,
incorporating the existing credit-intelligence project and the PayPal input-finance
module. No data partner is currently available; begin with public context and a
clearly labelled replay dataset.

## 1. Current assessment

The input-finance module has a tested local transaction journey. The AI module
has reviewed source for application intake and credit intelligence. The unified
product narrative is now documented and branded, but an automatic, trusted
approval handoff and a verified full-platform demonstration are still missing.

This is a substantial prototype foundation. It is not yet a demonstrated live
lending service or a completed hackathon submission. Avoid assigning a percentage
complete: passing execution tests do not measure provider connectivity, scoring
validity, user demand, or readiness of the other module.

Reviewed execution commit: `feaf6b9`. Reviewed AI commit: `fb8e3e1`; the remote AI
head was unchanged when checked. Latest confirmed pre-data-pack
[CI evidence](https://github.com/Brikita/afracanet-input-finance/actions/runs/40384405760)
shows the same 80 backend tests passing on SQLite and PostgreSQL, four browser
journeys passing, and a successful frontend build. These checks cover the
input-finance repository, not a live combination of both projects.

The local configuration remains `PAYMENT_MODE=mock`, `AI_MODE=demo`, and
`SMS_MODE=demo`. PayPal credentials/account emails/webhook ID, the Gemini key,
Africa's Talking sandbox key, and a unique demo access code are unconfigured.
Configuration was checked for presence only; no secrets are reproduced here.

## 2. What is already implemented

| Area                            | Implemented evidence                                                                      | Remaining boundary                                                                                |
| ------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Product identity                | AFRACANet AI umbrella brand, unified brief, combined submission outline                   | Unified navigation and actual runtime integration                                                 |
| Farmer/lender/dealer experience | Responsive workspaces; imported farmer choices; scoped server actions                     | Shared-code demonstration identities need stronger hosted access                                  |
| Credit allocations              | CSV preview/import, expiry, preservation of spent/reserved credit                         | Automated authenticated handoff and durable source-decision history                               |
| Catalogue                       | Dealer editing, quoted-price snapshots, stale-edit checks                                 | Genuine dealer records and multi-merchant onboarding                                              |
| Order integrity                 | Atomic credit/stock reservations; pre-invoice cancellation                                | Reservation expiry and broader recovery operations                                                |
| PayPal                          | Sandbox invoice adapter, signature verification, reconciliation, recovery                 | Actual credential-based invoice/pay/webhook evidence                                              |
| Collection/support              | Collection codes, repeated-collection safety, issue holds and lender resolutions          | Real-user trials and policy for paid refunds/reversals                                            |
| SMS                             | Consent, verification, language preferences, durable outbox, local/provider-sandbox modes | Provider verification, scheduled dispatch, receipt handling; real handset delivery is not enabled |
| Assistant                       | Gemini adapter, strict output validation, 24 synthetic labelled requests                  | Live model evaluation and native-speaker review                                                   |
| Persistence/testing             | Local SQLite, PostgreSQL CI coverage, automated checks                                    | Migrations, backups/restore, hosted operations and monitoring                                     |

## 3. Work required to connect the product

**Highest priority: a lender-authorized allocation must cross the module boundary.**

The intended flow is application → assessment → officer decision → allocation →
input order → supplier invoice/payment → collection. The source review found an
upstream farmer-ID approval operation and in-memory queue, rather than the full
allocation contract needed by execution. See [the platform review](PLATFORM.md).

Implement these together:

1. A durable application/decision ID, lender identity, approving officer, amount,
   currency, approval/expiry timestamps, decision reference, and data provenance.
2. Explicit mapping between upstream and execution farmer IDs. Names are not keys.
3. An authenticated handoff endpoint/adapter with validation, replay protection,
   stable retry IDs, and rejection of expired or unauthorized allocations.
4. A persistent decision/handoff record linking the application to later orders,
   invoices, payments, collection, and revisions. Preserve already committed credit.
5. Officer navigation to input finance with the linked allocation visible; a URL
   parameter alone must never create credit.
6. A communication sequence that reserves collection instructions for verified
   payment. Upstream approval messages currently invite collection too early.
7. Cross-module tests: duplicate handoff, wrong lender/farmer, expired approval,
   changed limits, missing upstream data, and revocation after an invoice/payment.

The current CSV import is a usable manual bridge. It must be demonstrated as
manual and does not yet retain every field in the proposed integration contract.
An AI recommendation never becomes an authorized allocation automatically.

## 4. Immediate security and reliability findings

These are observed source findings, not a generic risk checklist:

- The AI backend includes a hardcoded Africa's Talking credential. Its owner must
  revoke/rotate it if active, and keep replacement keys in that service's own environment.
- Some upstream requests disable TLS verification; restore certificate verification.
- Protect upstream evaluation and approval actions with lender authorization before
  they are trusted to trigger financial execution.
- Persist the upstream application queue/decisions so a restart does not erase state.
- Label unavailable/fallback graph evidence. Missing facts cannot silently become
  an illustrative applicant record that appears genuine.
- The upstream graph seeder's setup deletes graph nodes. Isolate it to a disposable
  demonstration database; use non-destructive, validated ingestion for real records.

The input-finance access model also needs abuse limits and a hosted identity design.
The demonstrated role checks should not be described as production identity proof.

## 5. Hardcoded and simulated data inventory

| Current item                                                | What it really is                             | Replacement or explicit treatment                                                             |
| ----------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Seed farmer names, locations, limits, expiry and references | Illustrative database initialization          | Explicit fixture mode; blank operational start; onboarding and lender import                  |
| Fixed lender/dealer personas and displayed supplier name    | Demonstration organization identities         | Organization/account records and order-linked display values                                  |
| Initial product prices and stock                            | Illustrative USD catalogue                    | Authorized dealer input/import with currency, source and last-confirmed time                  |
| AI graph farmers, memberships, guarantees and transactions  | Seeded scenarios                              | Real partner records or a separately labelled replay; compute graph features from those links |
| Upstream fallback applicant/graph values                    | Substituted demonstration context             | Fail with unavailable status or show an explicitly labelled fixture path                      |
| Climate thresholds and default risk value                   | Handwritten risk policy, not field validation | Real weather context, missing-data flags, and a versioned reviewed policy                     |
| Credit-score weights and thresholds                         | Rule-based heuristic                          | Versioned configuration; evaluated model/policy only when real labelled outcomes support it   |
| SIM-age or other unavailable personal indicators            | Unsupported without a verified source         | Leave unknown or omit; do not infer invented values                                           |
| Deterministic parser                                        | A limited local walkthrough tool              | Verified live model mode, with catalogue/manual ordering available if interpretation fails    |
| Mock payment IDs/events                                     | Local application simulation                  | Actual sandbox API/event records, clearly labelled as sandbox                                 |
| SMS preview/acceptance                                      | Local simulation or gateway acceptance        | Actual permitted channel integration and receipt states; acceptance is not delivery           |
| Example evaluation requests                                 | Synthetic test cases                          | Retain as tests; add consented/de-identified real user utterances and human-reviewed labels   |

Keep validation limits, fixed trusted provider hosts, protocol constants, and
test fixtures where they serve a clear purpose. The objective is to remove invented
business facts from normal operation and make each displayed fact traceable.

## 6. Data options and their limits

**A. Public environmental context — available now.**

Use [Open-Meteo historical weather](https://open-meteo.com/en/docs/historical-weather-api)
for dated gridded temperature/rainfall context. Retain units, coordinates, source,
retrieval time, attribution, and missing-data flags. Model/reanalysis output is not
an on-farm measurement or a validated credit-risk penalty. Check the hosted
[API usage terms](https://open-meteo.com/en/pricing) for commercial deployment.

[CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3) is another primary rainfall
source for regional/seasonal context. Its gridded estimates also require careful
geographic and temporal interpretation; they do not establish repayment ability.

**B. Public surveys and market context — research, not borrower identity.**

The [KNBS KIHBS 2015–2016 catalogue](https://statistics.knbs.or.ke/nada/index.php/catalog/13)
provides a historical household-survey route. The
[World Bank LSMS catalogue](https://microdata.worldbank.org/index.php/catalog/lsms)
provides other household/agricultural research datasets. Check study-level access,
licensing and redistribution conditions. Older studies or other-country records
are not a current Kenyan loan-performance dataset, nor can their respondents be
treated as our applicants or linked to invented social networks.

The Ministry's [KAMIS description](https://kilimo.go.ke/wp-content/uploads/2024/12/Kilimo-Bulletin-Issue-II-December.pdf)
supports market-price context. The live site was not reachable through the review
tool, so no working feed is claimed. Commodity market prices do not establish a
dealer's fertilizer quote or stock availability.

**C. Labelled replay — selected now while no partner is available.**

Generate fictional but internally consistent memberships, dated events, repayment
scenarios, allocations, and orders. Model missing history, arrears, normal
completion, and interrupted flows. Preserve chronology and reconcile amounts.
This tests ingestion, UI, graph processing and exceptions. It cannot validate
prediction, fairness, customer demand, defaults or lending outcomes.

The first pack is now present in [datasets](../datasets/README.md): 30 synthetic
farmers, 522 synthetic ledger events, 12 fictional loan histories and 54 membership
links, plus a separate actual public-weather snapshot of 60 daily records. The
data pack has not yet been wired into the running apps or the upstream graph.

**D. Consented first-party records — next source of genuine operations.**

Real farmer/organization onboarding, actual dealer quotations, user-submitted
requests, officer decisions and collection confirmations can be recorded through
the product. Establish permission, access controls and the purpose of collection;
use the minimum information needed. A few volunteers can test usability, but
cannot supply a statistically representative repayment history.

**E. A lender/cooperative/agro-dealer partner — needed for genuine financial history.**

Seek a small authorized export containing pseudonymous customer IDs, dated
membership/delivery/purchase records, loan schedules, disbursements and repayments,
and applicable decision references. Keep the re-identification mapping with its
authorized owner. Begin with CSV exports; a production API is not a prerequisite.
No partner is currently secured and no such dataset has been ingested.

Public sources cannot verify our own applicants' current approvals, guarantees,
repayments, dealer stock, or collection. Obtain those facts from the authorized
participants or their systems. Do not fabricate the missing relationships.

## 7. Keep real data, derived facts and sandbox records distinct

For every imported batch retain source, owner/license or permission reference,
source record ID, event time, retrieval/import time, schema/version, currency/units,
quality status, and environment/provenance. Derived features should reference their
input batch and algorithm/policy version. A raw record can be genuine while an
LLM-generated assessment remains an unvalidated interpretation.

Use distinct provenance states such as public context, partner observation,
first-party entry, derived feature, synthetic replay and provider sandbox. Use
live/stale/missing as freshness states separately. The full per-record tracking
and UI presentation are proposed work, not yet implemented across the platform.

PayPal's [testing agreement](https://www.paypal.com/us/legalhub/paypal/devtest-agreement)
requires anonymous, non-live sandbox data. A genuine PayPal API response can still
describe a simulated transaction with no real money. Keep future private partner
records out of sandbox payloads and public Git; use separate non-live fixtures.
The hackathon's sandbox requirement does not call for a live-money loan pilot.

Keep KES business context and illustrative USD allocations distinct. Relabelling
KES as USD is not conversion. Any eventual real-currency/payment route needs its
own supported integration and documented conversion/settlement policy.

## 8. Recommended work order with completion evidence

| Order | Work package                                                     | Evidence that it is complete                                                                                                       |
| ----- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Isolate seeds/fallbacks and make ingestion non-destructive       | A blank operational profile starts with no fictional approvals; missing upstream data stays missing; replay is explicitly selected |
| 2     | Secure/persist upstream decisions and build the approval handoff | One officer-authorized allocation crosses modules with matching IDs, amount, expiry, provenance and retry protection               |
| 3     | Load the selected public/replay pack through adapters            | Source labels survive ingestion; graph relationships reconcile; current dataset/version is visible                                 |
| 4     | Verify PayPal, model and SMS sandbox adapters                    | Stored successful and failed provider cases; real sandbox payment proof; real model results; correct SMS processing states         |
| 5     | Validate the unified experience                                  | Same reference links application, approval, order, invoice, payment and collection; meaningful exception demonstrated              |
| 6     | Prepare hosted operation                                         | Access controls, abuse limits, migrations, backup/restore, HTTPS/configuration and logs; reproducible deployment                   |
| 7     | Gather user evidence                                             | Recorded lender/dealer/farmer feedback, clear limitations, and a concrete pilot hypothesis                                         |
| 8     | Build presentation assets and submit                             | Product page/flow graphics, concise pitch, public video, tested judge route and verified Devpost entry                             |

Credentials/account setup, key rotation and partner permissions need the respective
account owners. Adapter code, ingestion controls, tests, packaging and presentation
can progress without pasting credentials or private data into chat. Work packages
can overlap where they do not depend on unavailable external access.

## 9. Demonstration and submission evidence still required

The engineering gates are the priority. Then produce the requested product page
with an animated flow, a concise deck, architecture/evaluation evidence, a pilot
proposal and the public demonstration video. Show a working purchase plus an
exception, clear source labels and actual provider records rather than invented
activity counters. Keep motion accessible and usable on the presentation device.

The [official rules](https://paypalaihackathon.devpost.com/rules) permit significantly
updated existing work subject to organizer determination; explain the earlier AI
foundation and new PayPal contributions. They require a functional test route,
public licensed source, and a public YouTube video under three minutes. A hosted
URL is optional when complete runnable instructions are supplied. Confirm ownership
and source licensing for the AI repository as well as this MIT-licensed module.

For competitiveness, map evidence to the five equally weighted criteria:
implementation, design, impact, innovation and presentation. The integration,
data provenance, and real transaction demonstration are currently stronger
priorities than adding unrelated services or unsupported outcome claims.

The internal 30 October target is four days away. A useful conditional sequence
is integration/data controls first, provider verification next, then combined
deployment/rehearsal and presentation/submission. No date guarantee is warranted
while credentials and the cross-module connection remain outstanding. The official
deadline is 12 November 2026 at 23:00 Africa/Nairobi.

## 10. Later pilot work

Before genuine lending or real customer operations, address live merchant and
payment onboarding, local-currency settlement, real handset messaging, privacy and
data-retention responsibilities, repayment servicing boundaries, reconciliation
operations and independent assessment of the credit policy. Add multiple lenders/
dealers, automated reservation expiry, robust refund/reversal handling, scheduled
workers, delivery receipt reconciliation and recovery procedures as the operating
model requires. Validate scoring on suitable observed outcomes before making
credit-performance claims. These are distinct from completing a credible sandbox
prototype and should not all be forced into the current submission.
