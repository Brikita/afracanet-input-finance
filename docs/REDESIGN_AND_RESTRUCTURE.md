# AFRACANet product redesign and restructuring brief

Draft for flow confirmation, 26 October 2026. This describes planned work, not
completed implementation or an approved visual direction.

## Outcome

One recognizable AFRACANet product, with a public explanation of the service and
distinct farmer, lender, and dealer workspaces. A visitor understands the product;
an operator understands the next action, its consequences, and the evidence behind
it. Keep the existing React/TypeScript and FastAPI stacks.

The visual direction will be developed using Taste and Impeccable. Marketing
pages may be expressive; transaction screens prioritize legibility, speed, and
accessible controls. Capture current screens before replacement and compare the
result at desktop, tablet, and phone widths. Do not invent impact figures,
customers, testimonials, payment confirmations, or AI confidence.

## Journeys to design

| Person  | Journey                                                                                                                  | Essential information                                                                              |
| ------- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Visitor | Understand problem → follow a labelled example → enter demonstration                                                     | Who pays whom, lender responsibility, prototype boundaries                                         |
| Farmer  | Apply → see decision → request inputs → confirm quote → track progress → collect → obtain help                           | Available allocation, expiry, quantities, total, next responsible person                           |
| Lender  | Review application → examine evidence → record decision and terms → review input order → pay invoice → reconcile         | Evidence provenance, missing information, officer authority, invoice/payment/collection references |
| Dealer  | Review approved request → confirm availability → issue invoice → verify readiness → record handover → resolve exceptions | Stock and reservations, payment verification, collection restrictions                              |

The main interaction is a linked case record: application, decision, allocation,
order, invoice, verified payment, and collection remain separately identifiable.
The graph answers a specific evidence question for the lender; it is not a
decorative wall of nodes. Search, filters, neighborhood expansion, relationship
dates, source records, and missing evidence should make it interpretable.

Design empty, loading, stale, unavailable, rejected, expired, held, cancelled,
partially paid, recovered, and completed states. Explain who can resolve each
exception. Farmer screens favor short mobile tasks; lender/dealer screens favor
queues and a selected record. Maintain keyboard access, visible focus, touch
targets, clear form errors, reduced motion, and an English/Swahili content plan.
Do not imply the entire application is translated until verified.

## Refactoring sequence

The current execution frontend concentrates approximately 53 KB in `src/main.tsx`;
the backend concentrates approximately 33 KB in `backend/main.py`. Size identifies
review targets, not proof that every line is redundant.

1. Map routes, dependencies, data ownership, and existing tests in both repositories.
2. Extract shared frontend domain types, API transport, formatting, and accessible
   primitives; organize screens by applications, allocations, orders, catalogue,
   reconciliation, issues, and notifications. Keep the entry file as composition.
3. Extract backend request schemas, authentication dependencies, API routers, and
   transaction services. Preserve atomic transaction boundaries while moving code.
4. Keep provider adapters, persistence, and synthetic fixtures explicit. Replace
   silent fallback data with honest unavailable states outside demonstration mode.
5. Add a versioned lender-authorized handoff contract between the modules. Keep
   underwriting and graph internals owned by the credit-intelligence module.
6. Remove code only after proving it unused, duplicated, superseded, or misleading.
   Introduce no speculative framework layers or wholesale dependency migration.

Keep the repositories modular initially. A unified product does not require an
immediate monorepo migration. Revisit packaging after mapping deployment and
Lovable integration constraints. Preserve pushed Git history.

Each extraction is a small reviewable commit. Validate role isolation, duplicate
requests, reservation accounting, payment verification, issue holds, and collection
before and after transactional changes. Run the frontend build and relevant
browser journeys after screen changes.

## Dataset design

Replace the small replay pack with a deterministic, configurable generator that
exports one coherent world to graph files and relational import files. Stable IDs
connect records across stores. Never generate each database independently.

Proposed profiles (targets to implement and measure, not generated counts):

| Profile     | Farmers | History   | Intended use                                        |
| ----------- | ------: | --------- | --------------------------------------------------- |
| Walkthrough |     100 | 24 months | Understandable stories and fast browser fixtures    |
| Development |  10,000 | 24 months | Graph exploration, pagination, realistic density    |
| Stress      | 100,000 | 36 months | Multi-million-event throughput and query benchmarks |

Event and edge counts must follow scenario parameters and be reported from actual
output. Stream large exports in batches; store generated bulk artifacts outside Git
with manifests and checksums. Benchmark on available hardware before promising
load times. Do not send bulk synthetic data to paid AI or payment services.

Include fictional farmers, households, farms, crop seasons, cooperatives, groups,
lenders, officers, dealers, products, memberships, applications, decisions,
allocations, orders, invoices, payment events, collections, issues, and repayment
histories. Record dates, units, currency, tenant ownership, and provenance.

Cover thin histories, disconnected farmers, overlapping memberships, seasonal
income, late repayments, partial payments, stock shortages, cancellations,
expired allocations, missing weather, delayed callbacks, duplicate events, and
cross-tenant rejection cases. Keep intentionally invalid cases in a separate
negative-test pack rather than contaminating the normal dataset.

Validate identity uniqueness, relationship endpoints, temporal ordering,
principal/repayment reconciliation, nonnegative stock and credit, legal workflow
transitions, and consistent totals across exports. Include temporal evaluation
splits and avoid generating outcomes directly from the score being evaluated.
Synthetic outcomes test software and scenario handling; they do not validate
real-world creditworthiness or default prediction.

Retain public weather snapshots as separately attributed contextual evidence.
Fictional farm assignments do not turn those histories into real farmer records.
Keep historical KES records separate from illustrative USD PayPal testing.
Generated payment events remain replay events and must never satisfy the genuine
PayPal verification path.

## Delivery order and completion evidence

1. Confirm journeys and first design surface; capture baseline screens.
2. Develop visual options, then implement the chosen system and complete role flows.
3. Restructure in tested slices, separating cosmetic and financial behavior changes.
4. Generate, validate, import, and benchmark the three dataset profiles in isolated
   stores; prove matching IDs and totals across graph and relational views.
5. Verify the connected application-to-collection flow with actual provider test
   accounts, then finish the public site, presentation, and submission materials.

Completion requires rendered comparisons, working exception paths, passing checks,
reproducible dataset manifests, measured query behavior, and accurate integration
labels. A polished screenshot or a large row count alone is insufficient.

## Design references

- Taste: local `taste-skill` v2, including its app-screen workflow.
- [Impeccable skill](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/SKILL.md)
- [Impeccable Shape](https://github.com/pbakaus/impeccable/blob/main/.agents/skills/impeccable/reference/shape.md)

Impeccable was read from its official repository; its local launcher is not
installed. No detector, visual direction selection, or browser design review has
yet been run for this redesign.
