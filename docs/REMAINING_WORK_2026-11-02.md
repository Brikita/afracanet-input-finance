# AFRACANet AI: remaining implementation and release work

Audit date: **2 November 2026**, Africa/Nairobi. Source baseline: **67b0184**.
Scope: the unified repository, both active applications, graph/data tooling,
provider integrations, operational readiness, and presentation/submission assets.

**Later sprint updates:** the owner authorized MIT licensing, the SMS CLI was
repaired, a compact judge profile was generated, and real PageRank/Louvain results
were computed on its separate graph. See [the execution record](SPRINT_2026-11-02.md)
for current completion/verification; the sections below preserve the initial audit.

This is a source-and-record audit. Historical passing checks below are recorded
evidence, not a fresh execution of every suite or a fresh provider verification.
No payment, lender decision, collection, SMS send, or AI call was initiated by
this audit. One operator-command failure was reproduced safely with `--help`.

## Assessment

The connected local prototype is substantially implemented. Repository
consolidation, the signed lender handoff, transactional input finance, the public
product page, and the Waterline working interfaces do not need rebuilding.

The largest implementation gap against the original AFRACANet vision is the
**active graph-analytics pipeline**. The current credit API retrieves connected
evidence and produces provider-backed advisory summaries. It explicitly returns
no calibrated credit score. The large development graph has not had GDS
algorithms run against it. The public-page graph is a teaching illustration,
not the working lender's GDS result.

Other material gaps are a reproducible complete judge environment, one continuous
provider-backed demonstration, persistent hosting/operations, broader independent
AI verification, operational identity, and authentic partner-data ingestion.

Do not assign a single completion percentage: a local demonstration, a convincing
graph-intelligence prototype, and a live lending pilot have different completion
criteria. A synthetic graph can demonstrate correct analytics without validating
creditworthiness.

## 1. Implemented baseline: retain and verify

| Area                   | Implemented evidence                                                                                                                                                 | Limit that remains                                                                                          |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| One source repository  | Credit under `modules/credit-intelligence/`; root execution/API/UI; shared setup, checks and supervisor                                                              | Two UIs/APIs remain separate services by design; credentials and sessions remain separate                   |
| Repository restructure | Root routes/contracts/services/adapters and frontend feature boundaries; significant unused credit dependencies removed                                              | Legacy credit research entry points and old instructions still need a clear quarantine/deprecation route    |
| Credit review          | Persistent lender-scoped applications, officer accounts, evidence/source inspection, decision history                                                                | No calibrated score; no production identity or partner onboarding                                           |
| Lender authorization   | Explicit authenticated decision, integer USD limits and expiry, reasons, rejection and revocation                                                                    | No autonomous lending authority; evidence/model snapshot selection should be made explicit at decision time |
| Cross-module delivery  | Ed25519 signing, scoped receiver trust, explicit farmer mappings, durable outbox, receipts, bounded retry and deduplication                                          | Production key lifecycle, monitoring and deployed worker supervision remain                                 |
| Input requests         | Catalogue, farmer confirmation, server role/subject checks, atomic credit/stock reservations, cancellation                                                           | Production catalogue onboarding and safe reservation-expiry policy remain                                   |
| Supplier payment       | Actual PayPal sandbox invoice/payment verification, payment-record matching, signed callback verification, reconciliation                                            | Existing actual payment evidence is an isolated fixture; broader provider recovery scenarios remain         |
| Collection/issues      | Separate collection code and handover event; issue holds and lender-only resolution; financial event handling continues under holds                                  | Tested collection uses simulated payments; no actual physical delivery claim                                |
| Operational views      | Lender queues, filters, dealer catalogue edits, timelines and CSV reconciliation                                                                                     | No complete operational monitoring console or repayment-servicing product                                   |
| AI request assistant   | Actual Gemini structured interpretation; 24/24 labelled development cases recorded                                                                                   | Prompt-tuning set, not unseen accuracy; more language/adversarial evaluation remains                        |
| Credit AI summary      | Actual Gemini summaries for three cases; citations, numeric checks, stored evaluation results                                                                        | Advisory only; currently restricted to labelled synthetic cases; broader semantic review remains            |
| Development data       | 10,000 fictional farmers, 24 months, matching graph/relational identities and provenance                                                                             | No real chama/SACCO/merchant/repayment feeds                                                                |
| Public context         | 60 attributed public weather records at two reference regions                                                                                                        | Historical reference context, not continuously refreshed farm measurements                                  |
| Product website        | New hero, licensed contextual photographs/fonts, spacious story, graph teaching and controllable automatic tours                                                     | Not a live transaction dashboard; finish checks must be repeated against the deployed build                 |
| Verification           | Last consolidation record: 150 root/workspace tests, 16 credit tests, signed workflow, 11 input/public browser cases, one connected browser case, both builds/checks | Existing tests do not establish production readiness or independent model performance                       |

Graph counts in the committed verification record are **928,163 nodes** and
**1,886,728 relationships**. These are development-store counts from the recorded
load, not a live measurement taken for this report.

## 2. Confirmed defect and documentation debt

### R01 — Repair the SMS dispatch entry point

**Classification:** implementation defect. **Priority:** next repair; mandatory
before including SMS dispatch in a demonstration or deployment.

`scripts/dispatch_sms.py` imports `notifications` directly from `backend`, while
the active implementation is `backend/services/notifications.py`. The safe check
`.venv/Scripts/python.exe scripts/dispatch_sms.py --help` fails with `ImportError`.
The API adapter/service tests do not exercise that CLI import path.

Implement the correct service import and check operator entry-point startup in
isolation. Verify `--help` has no provider/database effects, then exercise an
isolated labelled preview dispatch. Keep sandbox acceptance separate from
handset delivery. This audit records the defect; it does not change SMS code.

### R02 — Replace obsolete operational instructions

**Classification:** documentation and maintainability work. **Priority:** before
judge handoff.

The root README and `docs/MONOREPO.md` describe the current platform. Several
dated documents still describe a sibling checkout or list completed work as
pending. The credit `Backend/README.md` describes legacy Flask/scoring and tells
operators to run a seeder that clears graph data. It is not an accurate setup
guide for the active FastAPI workflow.

Keep dated evidence historical, but place clear supersession links on old setup
pages. Replace the active backend setup instructions with the supported route;
clearly mark legacy Flask, telecom and destructive seeding tools as inactive
research. Correct the submission checklist and remove wording suggesting the
already implemented signed handoff is future work. Preserve provenance/history.

**Done when:** a fresh reader can identify one supported setup path, no current
instruction requires an archived code checkout, and destructive research tools
are not presented as normal startup steps.

## 3. Core graph intelligence still to implement

### R03 — Safe, reproducible GDS analytics

**Classification:** substantial implementation. **Priority:** highest product
capability gap; stage it without blocking the minimum eligible submission.

There are legacy `gds.*` calls in `Backend/databaseSeed.py`; their existence does
not mean the active connected application has a working GDS pipeline. Do not run
that destructive seeder against the loaded development graph.

Implement within the credit module:

1. A GDS capability/version check and bounded memory estimate before any run.
2. Explicit, tenant-scoped projections with named relationship types, directions,
   time windows and weighting rules. Exclude generic reference/weather nodes
   from financial trust calculations unless a documented analysis needs them.
3. A compact repeatable fixture first, then a measured larger run if resources
   permit. Start with PageRank and community detection; add similarity only when
   its relationship meaning and computational bounds are clear.
4. Deterministic run configuration where supported, a run ID, dataset fingerprint,
   as-of time, algorithm/version/parameters, counts and runtime/resource metrics.
5. Separate persisted analytics results keyed by entity/run, without overwriting
   source records, lender decisions, allocations or payment records.
6. Explicit unavailable/failed/stale states, safe reruns, and temporary projection
   cleanup. No fabricated fallback values.
7. Tests for known small-graph behavior, tenant isolation, missing data and reruns.

**Done when:** one command produces real, inspectable GDS outputs from a labelled
dataset and records reproducible provenance without resetting source data.

Centrality is a network property. It does not establish income or credit quality;
community membership is not a default-risk label. Synthetic repayment labels
must not be used to imply real-world predictive validation.

### R04 — Bring computed analytics into the working lender experience

**Classification:** backend/UI implementation, dependent on R03.

The working evidence screen already has relationship counts, filters, repayment
totals and source-record inspection. Add the computed analytics and a bounded
interactive case graph to that working screen, with readable relationships,
selected-node details, source links, algorithm/run date and missing-data notices.
Provide a table/text alternative and usable mobile navigation.

Explain what each measurement shows and its limits. Display the authored
demonstration communities on the public page accurately unless replaced with
recorded actual analytics; do not relabel that illustration as live GDS.

Pin the reviewed evidence/analytics snapshot and, when used, the advisory
evaluation reference to the officer's decision record. Existing summaries are
stored by application, but the decision record does not explicitly select the
particular evaluation reviewed. Keep lender authorization independent of whether
AI/GDS is available; an absent summary must not invent an approval.

**Done when:** an officer can inspect an actual run, open its evidence, record a
decision, and later recover the same reviewed snapshot through shared references.

### R05 — Validated alternative credit scoring

**Classification:** research, data partnership and later implementation. **Priority:**
required for a real credit-scoring claim; not a hackathon submission prerequisite.

The active API returns `credit_score: None` and recommendation unavailable while
providing graph context. This is accurate current behavior. To introduce a
predictive score, first define the lending outcome and horizon with a lender,
obtain authorized observed histories, prevent temporal/borrower leakage, and
compare a transparent baseline against graph-derived features.

Evaluate held-out/time-based performance, calibration, missing-data behavior,
group disparities, explanation quality and human review. Version training data,
features, models and policies; define monitoring, review/appeal and rollback.
No unvalidated number should become an automatic approval or payment instruction.

**Done when:** an independently reviewed evaluation supports the precise claim
being made. Synthetic data alone cannot satisfy this requirement.

## 4. Data realism and remaining hardcoded fixtures

### R06 — Explicit demo seeding and incremental ingestion

**Classification:** implementation. **Priority:** before a non-demo deployment;
compact demo packaging is important for judges now.

Large reproducible generators, checksummed exports and safe development loaders
already exist. We do not need another enormous synthetic pack simply to increase
record counts. Root database initialization still inserts two illustrative
farmers, credit limits and three catalogue products when empty. Session choices
also include named demo participants. Defaults include simulated payments and a
deterministic request parser, explicitly labelled in the walkthrough.

Remaining work:

- Make demo bootstrapping an explicit profile/command. A non-demo database must
  start without invented farmers, credit allocations or prices.
- Provide a small complete connected scenario with reproducible dates, IDs,
  tenant mappings, graph and relational records. It should run on modest hardware
  and never activate historical replay approvals or payments.
- Define versioned import contracts for chama contributions, SACCO repayments,
  dealer purchases, membership and farm records. Add validation previews,
  deduplication, tenant ownership, correction/retraction and rejected-row reports.
- Support safe incremental batches and source freshness/quality summaries across
  graph and relational stores, including reconciliation after partial failures.
- Add public-weather refresh/failure/freshness handling with attribution and
  location confidence. Missing measurements remain missing.
- For partner ingestion later, add authorization, retention/deletion, provenance
  and permitted-use controls before enabling real records in AI prompts.

The credit summary currently rejects non-synthetic cases deliberately. Removing
that restriction is not a shortcut to a real-data product; it needs an authorized
data-processing path and evaluation first.

**Done when:** fixtures are opt-in; a compact labelled world runs from a fresh
checkout; a supported batch can be imported twice without duplicated business
effects; invalid or unavailable data stays visible.

### R07 — Authentic partner data and customer validation

**Classification:** external dependency plus integration work. **Priority:** pilot.

No partner has been secured. Establish one narrowly scoped agricultural lender,
chama/SACCO or dealer relationship before designing a universal connector. Agree
on record definitions, permission, access, coverage, corrections and ownership.
Validate mapping quality on an authorized sample. Observe actual officer/farmer/
dealer use, task completion and failure points. Do not replace missing partner
evidence with invented testimonials or synthetic repayment accuracy.

Keep anonymous, non-live sandbox fixtures separate from real partner records.
Historical KES records and illustrative USD execution remain separate: there is
no implemented FX conversion or validated Kenyan price catalogue.

## 5. Payments, recovery and dependable execution

### R08 — One continuous provider-backed sandbox demonstration

**Classification:** integration verification and small supporting tooling;
the core journey is already implemented. **Priority:** before final recording.

Create one new isolated, labelled case through the actual working UIs/services:
graph evidence → actual AI summary → explicit officer approval → signed receipt →
farmer request/confirmation → order approval → supplier invoice → manual buyer
payment in PayPal sandbox → actual payment-record verification → collection code →
dealer records a simulated physical handover.

Preserve application/decision/order/invoice references throughout. Confirm unpaid
collection is blocked and repeated callback/reconciliation has one effect. Record
the local collection event only after completing that demonstration step; it is
not evidence of physical delivery of real agricultural goods.

The existing USD 18 payment and genuine resent callback are separate evidence;
their fixture has no recorded collection. Do not splice them into another order
and imply they form one transaction. A new sandbox invoice requires its own buyer
action; the software must not impersonate lender payment authorization.

**Done when:** a linked evidence bundle supports the complete recorded scenario,
including actual provider facts and an accurately labelled handover demonstration.

### R09 — Broaden provider recovery and implement missing policies

**Classification:** mixed verification and implementation. **Priority:** focused
verification before submission; complete policies before a partner pilot.

Recovery controls already cover reference recovery, uncertain creation, draft
holds, verified unpaid cancellation, duplicate events and nonregression after
concurrent payment. Unit coverage is not the same as exercising every scenario
against PayPal.

Verify delayed/duplicate callbacks, unpaid cancellation, interrupted sends and
paid recovery against provider sandbox records. Implement a defined partial
payment/refund/return workflow with explicit actor permissions, verified provider
records, accounting rules and reconciliation states. A refund must not simply
release credit/stock because a user clicked a button.

Define safe abandoned-reservation expiry. Never release a reservation whose
invoice creation/payment outcome is uncertain without reconciliation. Provide
operator escalation for held cases and visible aging/reason information.

**Done when:** each exception has an owned state, documented recovery route and
tested money/stock invariants, including process restart and concurrency.

### R10 — Background jobs and operational visibility

**Classification:** implementation and deployment configuration. **Priority:** hosted
demonstration reliability first, pilot hardening afterwards.

Signed credit delivery already has a durable leased outbox and optional polling
worker. Do not rebuild it as though absent. Add supervised deployment, visible
backlog/age/failures and alerts. Provider invoicing/reconciliation is currently
synchronous; SMS dispatch is explicit, with uncertain sends held for review.

Add bounded reconciliation scheduling, supervised SMS dispatch if included,
operator actions for uncertain outcomes, privacy-safe correlation logs, dependency
readiness checks and restart behavior. Avoid blanket retries of invoice creation
or uncertain messages. Network calls must remain outside database transactions.

**Done when:** pending work survives restart, operators can identify blocked
records, and replay/retry cannot duplicate money, stock or notification effects.

## 6. Identity, messaging and commercial scope

### R11 — Production identities and account lifecycle

**Classification:** implementation. **Priority:** before untrusted external use.

Credit officers already have individual local passwords, hashed expiring tokens,
account disabling and a failed-login lock. Input finance uses a shared demo code
and selectable personas; it is not production identity.

Implement independently authenticated farmer/lender/dealer accounts, invitations,
organization membership, recovery/revocation, appropriate privileged-account
protection, rate limiting, and tenant-scoped administration. Preserve server role/
subject checks on all actions. Shared branding or future SSO does not justify
sharing bearer tokens or private signing keys between services.

Add signing-key enrollment/rotation/revocation and least-privilege hosted secrets.
Complete focused authorization, enumeration and abuse testing before exposure.

**Done when:** a real user cannot obtain another role or borrow another farmer's
identity by choosing a demonstration persona.

### R12 — SMS/USSD, if retained as a product capability

**Classification:** optional submission scope; implementation and external-provider
verification before a low-connectivity pilot.

Consent, number-verification challenges, preview/sandbox adapter, outbox and stale
message suppression already exist. Real handset delivery is not supported by
the current adapter. The active legacy USSD route returns 410; verified USSD
intake is not an implemented connected customer journey.

After R01, verify provider sandbox acceptance if showing it. For actual messaging,
add the selected provider's production route, delivery receipts, owned scheduling,
cost/consent controls and uncertain-delivery handling. USSD requires separately
verified sessions/callbacks, farmer identity, replay/timeout handling and order
status integration; it must not bypass authorization or disclose collection codes.

**Done when:** the demonstrated delivery/intake path has provider evidence. Until
then show the browser journey and label SMS previews accurately.

### R13 — Multiple organizations, merchants and country/payment suitability

**Classification:** product design, partner validation and later implementation.

Credit data supports lender scopes, but the receiving sign-in and PayPal supplier/
buyer configuration remain illustrative. This is not merchant onboarding for a
multi-supplier marketplace. Validate the target lender's and supplier's actual
country/currency/settlement needs before promising live Kenyan operations.

Add organization/merchant onboarding, per-merchant credential ownership, supported
currency/price rules and tenant administration only against that defined scope.
Preserve service and merchant secret isolation. Assess whether an additional
payment rail is needed rather than representing PayPal USD sandbox as a local
KES settlement product.

Repayment servicing is currently the lender's responsibility. If it is added to
AFRACANet later, design schedules, postings, adjustments, reconciliation and
reporting as a separate explicit capability. Supplier payment is not loan repayment.

## 7. Deployment, reproduction and maintenance

### R14 — Complete judge setup from a genuinely clean environment

**Classification:** packaging plus verification. **Priority:** submission blocker
unless a fully working hosted route is supplied instead.

Shared clean dependency installation, both builds, startup and isolated journeys
are implemented. The archive check reused an installed Python runtime. It did not
prove that an unfamiliar judge can create the full graph/replay environment.

Provide a supported fresh setup for the compact connected dataset, officer
provisioning, signing/public trust enrollment, database bootstrapping and expected
ports. Offer explicit credential-free demo and configured provider-backed modes;
do not silently replace missing graph/AI/provider results with simulated success.
Remove operator-specific private paths from the documented fresh-install route.

Test without the historical checkout, its `.env`, installed stores or local path
references. Record platform/prerequisites, commands, startup time, expected states,
shutdown/reset rules and troubleshooting. Never delete an invoice-associated
database as a convenient reset. Add a small connected CI smoke scenario when the
graph dependency is packaged; current CI does not run the externally configured
connected graph browser suite.

**Done when:** another person or clean environment can follow the instructions
and complete the intended journey without undocumented local state.

### R15 — Stable hosted presentation build

**Classification:** deployment implementation/configuration. **Priority:** strongly
preferred for judge/partner access, but not mandatory if R14 is satisfied.

No supported deployment manifest/container/provisioned hosting route was found
in the tracked repository audit. `dev:all` is a local supervisor, not a production
process manager. The prior callback tunnel is temporary.

Deploy both frontend runtimes and APIs with explicit public URLs, correct route
rewrites (including `/about`), CORS/host configuration, persistent stores and
stable HTTPS callback. Keep provider secrets server-side, private keys credit-side,
and graph/database ports private. Run owned workers under supervision. Ensure
private judge access and usable phone layouts from another device/network.

For the judge build, choose a compact data profile rather than assuming the full
local million-node graph fits free hosting. Preserve anonymous sandbox fixtures.
Document operating costs/quotas and maintain availability through judging.

**Done when:** deployed sign-in, evidence, handoff, payment reconciliation and
recorded collection work after restart, and external callbacks reach the intended
environment without exposing the development workspace.

### R16 — Migrations, backups, diagnostics and dependency maintenance

**Classification:** implementation/operations. **Priority:** minimum backup and restore
before valuable hosted state; full operational controls before a pilot.

Both application stores use SQLAlchemy `metadata.create_all`; no versioned
migration system was found. Add versioned schema changes and safe deployment/
rollback instructions. Establish backups and a tested restoration procedure for
SQL stores, graph data and signing/trust configuration, with separate key handling.

Add structured redacted diagnostics, application/worker/dependency health, incident
runbooks, retained audit exports and appropriate audit integrity controls. Extend
format/lint/entry-point coverage across supported credit code and tools. Review
upstream development-tool notices without forcing incompatible framework upgrades.
Do not remove legacy code or dependencies merely because they look unfamiliar;
first establish whether an active path uses them.

**Done when:** an upgrade/restore is rehearsed and does not lose invoice references,
decision provenance, payment deduplication or financial invariants.

## 8. Independent evaluation and user-flow finish

### R17 — Broader AI evaluation

**Classification:** evaluation tooling and independent review. **Priority:** bounded
honest evidence before recording; broader validation before pilot claims.

Keep the current development set separate from a new unseen set. Cover English,
Swahili/code-switching, spelling, local product names, ambiguous pack size,
multiple products, unavailable catalogue items, instruction injection, malformed
model output and unavailable/quota-limited providers. Measure correct accepted
requests, appropriate clarification, unsafe guesses, latency and failure rates.
Have a fluent reviewer assess Swahili; do not call automated schema success
language-quality validation.

For summaries, independently check whether each cited fact actually supports
the statement, whether important missing evidence is disclosed and whether the
text overstates causality or creditworthiness. Numeric/citation membership guards
are useful but insufficient. Record model/prompt/dataset versions. Keep core
catalogue/order entry usable when AI is unavailable.

**Done when:** a frozen unseen evaluation and human review have recorded results,
with failures and limits reported rather than edited out of the score.

### R18 — User testing and deployed UI/accessibility verification

**Classification:** validation and targeted fixes. **Priority:** presentation polish
now; partner usability before a pilot.

The public page and working Waterline interfaces are implemented and have
responsive/browser evidence. No whole-site redesign remains necessary.

Watch representative users complete the officer decision, farmer request and
dealer handover tasks. Check terminology, currency, role transitions, error and
empty states, long records, slow connections, keyboard/focus, reduced motion and
phone readability. Review actual deployed fonts/images/routes rather than relying
only on local screenshots. Fix observed friction; do not add ornamental animation
that hides payment or authorization state.

**Done when:** concrete task results and remaining issues are documented. Do not
claim farmer adoption, lender validation or measured impact without evidence.

## 9. AI voiceover, video and submission

### R19 — AI voiceover and recorded demonstration

**Classification:** presentation assets. **Priority:** submission blocker.

The user has chosen an **AI voiceover**. This report records that requirement;
no narration audio or final video has been generated yet. Target approximately
**175 seconds (2:55)** total, including titles/outro; this is the user-selected runtime.
Use an original/licensed synthetic voice and no impersonation. Prefer a clear
English narration with readable captions and careful pronunciation of AFRACANet,
chama, SACCO and product names.

Proposed shot plan, to be finalized against the functioning recorded build:

| Time      | Screen/action                                                   | Narration purpose                                                                          |
| --------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 0:00–0:15 | Farmer/dealer context and product                               | Explain who needs inputs and why asset-collateral requirements can exclude them            |
| 0:15–0:45 | Working case, connected records and actual AI summary           | Show alternative evidence, citations and missing information; show GDS only if implemented |
| 0:45–1:05 | Explicit officer decision and signed delivery receipt           | Establish lender authorization and shared references                                       |
| 1:05–1:25 | Farmer request, clarification and quote confirmation            | Show AI assistance with the farmer remaining in control                                    |
| 1:25–2:05 | Supplier invoice, buyer PayPal sandbox action, verified payment | Prove PayPal's central role and actual matched payment records                             |
| 2:05–2:30 | Collection code and dealer records demonstration handover       | Separate payment confirmation from collection; show the timeline                           |
| 2:30–2:55 | Linked record, concise architecture/limits and pilot ask        | Explain what was built, what is synthetic, and the next partner opportunity                |

Capture real screen actions and valid states. Cut loading/setup while retaining
honest chronology/references; label time jumps and any separate fixtures. Do not
show a successful GDS run, physical customer delivery, live SMS or predictive
score that the build does not provide. Display sandbox/synthetic status clearly.

Finish the narration script after locking actual claims and shot durations;
generate voiceover, check pronunciation/pacing, sync captions and mix sound.
Music is optional. Export and watch the complete result at normal speed on a
phone, upload publicly to YouTube early, and verify accessible playback and length.
Retain script/captions, media rights/credits, render settings and the source cut.

**Done when:** the public video shows the functioning product, has intelligible
AI narration/captions, stays under three minutes and matches the submission text.

### R20 — Licensing, prior-work attribution and Devpost entry

**Classification:** rights confirmation, writing and submission action.
**Priority:** eligibility blocker.

The root input-finance code has an MIT license. The imported credit HEAD had no
license file, and its `NOTICE.md` explicitly does not extend root MIT to that
prior work. Obtain the relevant ownership/contributor confirmation, then document
the applicable license and retained third-party notices. This cannot be solved
by silently changing a heading or deleting the notice.

Describe existing credit work separately from hackathon additions, including
signed delivery, input-finance execution, PayPal verification, collection controls,
AI integrations, data/UX work and consolidation as supported by history. Finalize
tool/model disclosures, source/media/data credits, problem/audience, testing
instructions, limits and a concrete pilot hypothesis.

Prepare screenshots and the public repository/video links. Supply scoped judge
access through an appropriate private route; never publish provider secrets,
private signing keys or personal records. Verify required Devpost fields and the
actual submitted-entry confirmation. Do not mark a saved draft as submitted.

The organizer email supplied by the user sets **Thursday, 5 November 2026** as
the early eligibility-check target; it gives no cutoff time. Do not invent one.
The published final deadline is **12 November 2026, 12:00 PST / 23:00 Nairobi**.
The official rules allow a complete local-run route instead of hosting, require
a public licensed repository and public YouTube demo under three minutes, and
allow significantly updated prior projects with disclosure. Consult the
[official rules](https://paypalaihackathon.devpost.com/rules) before submission.

## 10. Recommended execution order

This is a proposed sequence, not a promise that all product/pilot work will finish
before 5 November. Rights confirmation, provider buyer actions, user feedback,
hosting access and partner data involve the owner or external parties.

| Order | Deliverable                                                                                                             | Gate / fallback                                                                                                         |
| ----- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 1     | Repair R01; correct supported setup/submission instructions under R02; seek credit licensing confirmation               | Do not block engineering work while rights confirmation is pending; do not claim complete open-source coverage          |
| 2     | Compact clean connected setup and judge rehearsal (R06/R14)                                                             | This is the fallback if stable hosting is not ready                                                                     |
| 3     | Continuous sandbox scenario and linked evidence (R08); bounded AI/provider exception checks (R09/R17)                   | Requires actual buyer action; never simulate it while calling it PayPal                                                 |
| 4     | Narrow, non-destructive GDS pipeline and working-screen results (R03/R04)                                               | Valuable to the complete product; keep it on a separate branch/release scope if it threatens the early submission build |
| 5     | Hosted build and external-device/callback verification if feasible (R10/R15/R18)                                        | A verified complete local route satisfies the functional-build requirement                                              |
| 6     | Lock recording build, produce AI narration/captions/video and finalize Devpost (R19/R20)                                | Submit for the 5 November early check once eligibility assets are ready                                                 |
| 7     | Address organizer feedback and focused defects before final deadline                                                    | Avoid reopening the visual direction or adding unverified feature claims                                                |
| 8     | Partner-pilot work: real identities/data, exception policies, operations and model validation (R05/R07/R09–R13/R16–R18) | Separate acceptance criteria and partner access; not a three-day hackathon sprint                                       |

For an eligible entry, full GDS, real partner data, live SMS, production identity,
multi-merchant onboarding and calibrated scoring are not all prerequisites.
They remain real product gaps and must not appear as completed features in the
video. For the larger AFRACANet vision, R03–R07 are central rather than decorative.

## 11. Evidence and audit references

- [Current platform setup](MONOREPO.md) and [consolidation verification](MONOREPO_MIGRATION_2026-11-01.md).
- [Connected platform/data record](CONNECTED_PLATFORM_2026-10-30.md) and [cross-store report](../datasets/reports/connected-v1-store-verification.json).
- [Provider verification](PROVIDER_CHECKS_2026-10-31.md), [payment report](../datasets/reports/paypal-sandbox-2026-10-31.json), [callback report](../datasets/reports/paypal-callback-2026-10-31.json).
- [Actual assistant development evaluation](../evaluations/results/gemini-2026-10-31.json).
- Active [graph context](../modules/credit-intelligence/Backend/graph_context.py), [advisory summary](../modules/credit-intelligence/Backend/advisory.py), [decision workflow](../modules/credit-intelligence/Backend/workflow.py), [delivery outbox](../modules/credit-intelligence/Backend/delivery.py).
- [SMS CLI](../scripts/dispatch_sms.py), [SMS service](../backend/services/notifications.py), [database initialization](../backend/db.py), [execution configuration](../backend/config.py).
- [Public-page finish review](PRODUCT_SITE_FINISH_REVIEW_2026-11-01.md) and [credit source notice](../modules/credit-intelligence/NOTICE.md).

The source audit inspected active service composition, graph/summary/identity/
decision/delivery paths, environment modes, seeding, operator scripts, UI evidence,
CI, test names and tracked deployment/migration/media-file presence. It did not
constitute an independent penetration test, full performance benchmark, new
provider certification, or complete model-validation study.
