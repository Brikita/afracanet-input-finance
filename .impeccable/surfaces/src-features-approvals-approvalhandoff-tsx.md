---
version: 1
slug: "src-features-approvals-approvalhandoff-tsx"
primary_target: "src/features/approvals/ApprovalHandoff.tsx"
related_targets: ["src/features/approvals/DecisionEntry.tsx", "src/styles.css"]
---

# Reviewed decision handoff

Mode: Operate. Ordinary extension of the selected Waterline system. The lender
needs to preserve a source decision and authorize its allocation without treating
model output, file metadata, or a navigation link as authority.

## Direction contract

THESIS: Make the farmer link and lender confirmation explicit before changing
credit. The operator enters decision terms through a form, with file input as an
optional alternative; the review is a separate step with a positive attestation.

OWN-WORLD: Preserve Waterline's teal navigation, pale blue ground, white ruled
working surfaces, DM Sans controls, Manrope headings, and small Lucide icons.

STORY: Confirm the farmer mapping, enter the recorded terms, inspect the preview,
authorize, and retain the decision alongside its provenance and revocation state.

FIRST VIEWPORT: The existing header and credit-allocation title lead to one
working region. Transfer/authentication limits and farmer-mapping controls appear
first. The decision form and its preview follow in a responsive two-column field
grid that becomes one column on phones. History sits below the review.

FORM: Inherit the user-approved Waterline direction, seed:0bf6610d1698eecb.
The meaningful transition is a validated, unchanged preview becoming a durable
record only after lender confirmation. Input edits invalidate that preview.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Evidence boundary

No upstream graph or underwriting logic is copied. This is manual lender review,
with demonstration receiving identities and unverified source officer/provenance
claims. No shipping rasters. A revoked allocation cannot fund a new request;
historical reservations and paid records remain visible and separately reconciled.
