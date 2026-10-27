# Redesign and restructuring: first implementation slice

26 October 2026. The product brief was confirmed with “let's start”. This records
the first implementation slice. See the 27 October update below for the selected
visual direction; cross-module integration remains unfinished.

## 27 October update

The user selected **Waterline** after requesting color, useful icons, and
visualizations. Its working React implementation replaces the previous shell
and lender overview, with shared styling across farmer, dealer, management,
issues, and notification screens. Figures come from scoped application records.
The queue supports search, status filtering, case selection, and existing
transaction actions. Mobile selection transfers keyboard focus to the case;
dialogs trap focus and restore it on close.

The production build passes. Browser verification covers five journeys. A fresh
Impeccable reviewer requested the narrow-screen focus correction and returned
`ship` after verification. Taste inspection reports no failures and two warnings
about small metadata and colored header area. See [the review](WATERLINE_REVIEW.md).

Remaining work includes the secure lender-authorized cross-module handoff,
further workspace/API extraction, isolated graph/PostgreSQL loading, explicit
runtime data modes, and broader scenario coverage. Marketing-page design and
motion are deferred until core features are complete, as requested.

## Completed structure work

- The frontend entry point now mounts the application and loads styles/fonts.
  Shared types, status vocabulary, API transport, formatting, and presentation
  primitives have explicit modules. Management, issues, and notifications live
  under feature folders.
- Backend request models, session/role/subject checks, and scoped order helpers
  are extracted. Reservation helpers still execute inside the caller's original
  transaction; provider orchestration and API contracts are preserved.
- The larger application composition and API route files remain further
  extraction work. Their remaining size is visible rather than hidden by wrappers.

## Initial design exploration (superseded by the update above)

Taste's app draw produced **Achromatic ledger**, seed **1190266030**, with the
existing type/palette retained as input and the brand green mapped to the data
accent. No redraw was made. Its proposed shell is top navigation with a focused
content column. This is a candidate foundation, not a final design approval.

Impeccable's official skill and Windows engine were loaded from a reference
checkout under ignored `data/tools`. Product context is captured in `PRODUCT.md`.
The direction round produced `seed:0bf6610d1698eecb`.

Grounded candidates considered, in order: cooperative register, county field
index, agricultural extension sheet, crop-label typography, community bulletin,
delivery record, and seed-certification record. The assigned delivery-record
candidate and cooperative-register alternative are presented alongside the
competitive evidence-atlas direction and a conventional finance alternative.
The atlas lends evidence hierarchy, not a literal star map.

Before screenshots were captured at 1440, 768, and 390 pixels. Four desktop HTML
composition previews were rendered and visually inspected; layout corrections
brought the primary action into the first viewport and made the evidence-atlas
preview visibly different. They use synthetic examples and disclose unavailable
upstream evidence. Preview files and screenshots are local development artifacts.

At this initial checkpoint the composition had not yet been built as working
React screens, so no final Taste score, detector pass, or Impeccable finish-review
verdict was claimed. The 27 October update records the subsequent implementation
and review. Marketing-page art direction, motion, and deeper farmer/dealer flow
refinement remain outstanding.

## Generated data

The development pack was actually generated and validated locally:

| Record type                             | Actual count |
| --------------------------------------- | -----------: |
| Farmers                                 |       10,000 |
| Graph entities, including ledger events |      918,043 |
| Graph relationships                     |    1,876,548 |
| Financial ledger events                 |      784,656 |
| Loan histories                          |       12,496 |
| Installments                            |       74,976 |
| Illustrative USD allocations            |       10,000 |
| Input orders                            |       10,000 |

It includes 4 lenders, 12 officers, 20 dealers, 80 cooperatives, 250 savings
groups, 12 reference regions, 60 illustrative catalogue products, and 24 months
of configurable authored context. Eight order states and multiple repayment and
evidence scenarios are represented. All application allocations in this first
pack are approved examples; rejected/pending cohorts and full stock accounting
remain additions, as detailed in `datasets/SYNTHETIC.md`.

The 100-farmer walkthrough pack was also generated. The generator supports the
100,000-farmer / 36-month stress profile, which has not been generated or measured.

The populated SQLite database and matching CSV exports are under ignored
`data/synthetic/development-v1`. Only the small manifest and measurement report
are tracked in `datasets/reports`. Generation uses bounded writes and streaming
exports; loan and allocation lookup indexes prevent repeated full-table scans
during validation.

Local read-query measurements covered bounded farmer history, one-hop graph
neighbors, a pending-order queue, and loan history. All four used indexes. These
measurements concern a possibly warm local SQLite cache, not Neo4j/GDS,
concurrency, deployed performance, or predictive accuracy.

## Checks and next slices

The initial local verification was 95 backend/data tests, a production frontend
build, and four browser journeys (now five). Corruption tests exercise broken references,
future events, crossed tenant ownership, and mismatched financial totals.

Next after the completed Waterline case-flow slice: extract the remaining
workspace screens and API routers; connect a secure
lender-authorized handoff; map the generated world into isolated graph/PostgreSQL
stores; replace runtime demo fallbacks with explicit data modes; extend scenario
coverage. The generated pack has not been loaded into either running app or an
upstream graph service.
