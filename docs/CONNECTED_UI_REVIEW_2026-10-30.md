# Connected workflow UI review — 30 October 2026

This records the UI extension for the authorized signed connection and loaded,
labelled development data (plan items 1 and 2). It is an ordinary extension of
the two incumbent interfaces. Whole-platform visual unification remains later
work. No new visual world or shared design system was approved in this pass.

## Incumbent systems preserved

The input-finance extension follows [DESIGN.md](../DESIGN.md), its
[existing sidecar](../.impeccable/design.json), and the visual direction in the
[reviewed handoff surface brief](../.impeccable/surfaces/src-features-approvals-approvalhandoff-tsx.md).
The shipped handoff keeps Waterline's dark teal header, pale blue ground, flat
white bordered working surfaces, DM Sans controls, Manrope headings, compact
labelled records, and Lucide outline icons. It uses the existing palette and
control language for signed deliveries, manual review, farmer mapping, and
revocation. The brief's manual-review story remains applicable to the fallback;
signed delivery is an additional path documented here.

The credit-intelligence extension retains its own green OKLCH palette, Plus
Jakarta Sans typography, light background, white cards, and incumbent desktop
sidebar. Source comparison included sibling `src/styles.css` and
`src/components/AppSidebar.tsx`, alongside the shipped
`src/features/credit/CaseReview.tsx` and `credit.css`. The desktop sidebar still
contains Lender review and Decision history; the phone layout exposes those
destinations through text navigation. This pass did not restyle that module as
Waterline or treat the two systems as visually unified.

Root source comparison included `src/styles/approvals.css`,
`src/styles/management.css`, `ApprovalHandoff.tsx`, and the connected browser
journey. The root DESIGN.md, sidecar, surface brief, tokens, and source code were
preserved by this documentation pass. No shipping raster assets were introduced;
the captures below are review evidence.

## Extension states, navigation, and labels

Credit review now presents a lender-scoped application queue, search and status
controls, retrieved graph context, separately attributed public weather context,
and an explicit lender-authority confirmation before recording a decision.
Graph evidence and optional AI summaries remain advisory. Recorded decisions
show their reference, officer, delivery attempts, acknowledgment or next retry,
and revocation state. Historical replay decisions remain distinguishable from
current authorized decisions.

The continuation link carries a decision reference into input finance. The
receiving workspace signs in independently; the link transfers no browser
session or private key. Recorded decisions appear before the manual mapping and
review forms, with transfer method, provenance, source application/officer,
receiving lender, amount, and references. “Signed lender service” identifies
service-attested delivery. Manual files still require separate lender review
and retain their source officer as a claim. Loading, history-load error/retry,
current allocation, revocation review, and revoked states remain explicit.

Input-finance search and pagination support the loaded profiles. Its persistent
simulation and illustrative-USD labels remain visible. Approval permits an input
request; verified supplier payment is still required before collection.
Revocation does not erase historical payments, reservations, or collection
records and requires their separate reconciliation.

## Viewports and browser evidence

The six fresh captures were inspected against the source and incumbent systems:

| Capture | Viewport | Evidence |
| --- | --- | --- |
| [Credit desktop](../.impeccable/review/connected-credit-desktop.png) | 1440 × 900 | Sidebar, queue/case columns, graph and public-context labels, lender decision form |
| [Credit tablet](../.impeccable/review/connected-credit-tablet.png) | 768 × 1024 | Retained sidebar, stacked queue/case, single-column decision fields |
| [Credit mobile](../.impeccable/review/connected-credit-mobile.png) | 390 × 844 | Text navigation, stacked records/fields, wrapped evidence and authority text |
| [Input desktop](../.impeccable/review/connected-input-desktop.png) | 1440 × 900 | Signed record, transfer disclosures, manual fallback, search and allocation table |
| [Input mobile](../.impeccable/review/connected-input-mobile.png) | 390 × 844 | Single-column handoff facts/forms and wrapped full-reference revocation review action |
| [Input mobile confirmation](../.impeccable/review/connected-input-confirm-mobile.png) | 390 × 844 | Full-UUID reason label and confirmation action remain within the viewport; visible field focus |

These are full-page captures; their image heights exceed the viewport heights.
Long operational pages and contained table scrolling remain part of the
incumbent interfaces.

The implementation session reran the isolated Edge connected journey after the
two review fixes and reported it passing. Its executable evidence is
[`tests/connected-browser/workflow.spec.ts`](../tests/connected-browser/workflow.spec.ts),
using [`playwright.connected.config.ts`](../playwright.connected.config.ts).
It covers officer sign-in, graph/public-context retrieval, explicit approval,
signed delivery acknowledgment, reference continuation, independent receiving
workspace entry, the signed $180.00 illustrative allocation, and delivered
source revocation reflected at the receiver. Fresh temporary application stores,
officer accounts, and signing keys isolate the journey; loaded graph/context
data is accessed read-only.

The test checks document overflow at all three credit widths and input mobile.
It separately checks the right bounds of both full-UUID mobile revocation
buttons, opens the reason/confirmation state, then keeps the decision before
testing source-side revocation. It does not claim to submit the receiving manual
revocation in that browser journey. This documentation pass inspected evidence
and test source; it did not rerun tests or providers.

## Review disposition and existing drift

The first full review found the extension consistent with both incumbent
systems and required two corrections: wrap full mobile revocation references
and bring PRODUCT.md's connected-workflow facts up to date. The implementation
session applied both and reran the isolated Edge journey, including the action
bounds checks. The final reviewer confirmed both resolved, found no regressions
introduced by those fixes, and returned **ship for those two scored fixes** with
no remaining required correction in that follow-up. The initial full review had
reached its functional-scope review ceiling. This disposition is not an
unqualified whole-product design, accessibility, security, or production
certification; visual unification was excluded throughout.

The existing single detector result,
[connected-detector.json](../.impeccable/review/connected-detector.json), contains
two advisory entries and no primary finding: the pre-existing management fill
`#f5f9fa` and `12px` type. The latter is already described for supporting text in
DESIGN.md prose although absent from its machine-readable role ramp. Neither
value was added to normative tokens, canonized, or repaired in this ordinary
extension. The detector was not rerun by the documenter.

## Identity, provider, and data limits

Product facts are maintained in
[CONNECTED_PLATFORM_2026-10-30.md](CONNECTED_PLATFORM_2026-10-30.md) and the
updated [PRODUCT.md](../PRODUCT.md). The local signing service attests an
authenticated, authorized officer action within enrolled lender/officer scopes;
it is not an officer-held personal signing certificate. Receiving browser
sessions remain labelled shared-code demonstrations. Production identity and
SSO remain additional work.

The loaded farmer and financial histories are authored synthetic replay.
Historical approvals and payments do not activate execution credit or establish
PayPal evidence. Public weather is attributed reanalysis attached to fictional
reference-region assignments, not verified farm locations. KES histories and
illustrative USD allocations remain separate. GDS has not been run on this pack;
no calibrated score, predictive validation, or observed lending outcome is
claimed.

Real PayPal sandbox, AI-provider, and SMS integration verification remains
outstanding. The combined workflow check used explicitly simulated payment and
zero provider calls. Neither screenshots, delivery success, invoice status,
graph retrieval, nor deterministic parsing establishes provider payment, AI
execution, permission to collect, or production readiness.
