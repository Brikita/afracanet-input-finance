# Reviewed lender decision handoff

Implemented 27 October 2026 in the input-finance module. This is a **manual,
lender-reviewed bridge**. Automatic export from the credit-intelligence portal,
authenticated service-to-service transfer, and production officer identities
remain outstanding. A prepared file is data, not a trusted sender or approval.

## Operator journey

1. Sign in as the lender and open **Credit allocations**. If the farmer is
   missing, use the existing lender-approved profile CSV import first.
2. Confirm the upstream opaque farmer reference against the local farmer record.
   Names, phone numbers, and national IDs never establish this mapping. Links
   belong to the signed-in lender and cannot be reassigned through this API.
3. Enter the terms of an existing lender approval: source application, decision
   reference, source officer, total USD ceiling, decision time, expiry, and
   assessment provenance. A prepared version 1 JSON file is an optional input.
4. Preview the farmer link, current/proposed ceiling, reserved/paid amount, source
   claims, and dates. Preview changes no credit. Editing inputs clears it.
5. Explicitly confirm lender authorization and record the allocation. The server
   rechecks ownership, mapping, dates, revision, and committed credit atomically.
6. Find the durable record under **Recorded lender decisions**. New input orders
   retain the allocation reference, handoff ID, and source application in their
   request audit event, even if the allocation later changes.

The source officer and data provenance are claims retained from the reviewed
decision. The recorded actor is the input-finance lender session, separately
stored. Current authentication uses demonstration personas and a shared access
code; it does not establish individual production officer authority.

## Version 1 contract

`POST /api/approval-handoffs/preview` accepts:

| Field                   | Required value or meaning                                         |
| ----------------------- | ----------------------------------------------------------------- |
| `schema_version`        | Integer `1`                                                       |
| `source_system`         | `afracanet-credit`                                                |
| `source_application_id` | Opaque application reference, up to 100 characters                |
| `source_farmer_id`      | Registered opaque source reference, up to 100 characters          |
| `farmer_id`             | Existing local `farmer-*` ID in the signed-in lender's scope      |
| `lender_id`             | Must match the authenticated session subject                      |
| `approval_reference`    | Stable, immutable lender decision reference                       |
| `approved_by`           | Source officer claim, distinct from the receiving actor           |
| `decision`              | Exactly `LENDER_APPROVED`; model verdicts are rejected            |
| `limit_cents`           | Strict positive integer, at most 100,000,000; total ceiling       |
| `currency`              | Exactly `USD`; KES is never relabelled or automatically converted |
| `approved_at`           | ISO timestamp with timezone, no later than receipt                |
| `expires_at`            | ISO timestamp with timezone, after decision and receipt           |
| `data_provenance`       | `synthetic`, `real`, `mixed`, or `unavailable`; a source claim    |

Opaque application/farmer references use letters, digits, underscores, periods,
colons, or hyphens and begin with a letter or digit. Unknown fields and amount
coercion are rejected. The executable schema is in `backend/handoffs.py` and the
API's `/openapi.json`; this document does not override it.

The preview returns `allocation_revision`, current and committed amounts,
`already_recorded`, `revoked`, `transfer_method: manual_lender_review`, and
`source_authentication: not_verified`.

`POST /api/approval-handoffs` takes an object containing the same `handoff`, its
preview `allocation_revision`, and the actual boolean
`confirm_lender_authorization: true`. A preview is useful context, not a promise
of later availability; all checks run again on apply. It records no payment and
creates no input order.

## Other endpoints and persistence

All routes require a lender session and enforce its subject on the server:

- `GET/POST /api/approval-mappings`: list or explicitly confirm immutable links.
- `GET /api/approval-handoffs`: the lender's latest 100 durable decisions.
- `POST /api/approval-handoffs/{id}/revoke`: reasoned, idempotent revocation.

The additive `approval_mappings` and `approval_handoffs` tables are created by
the existing metadata initializer. Existing farmer/order tables are preserved.
Normalized payloads and hashes support replay checks; management audit events
record mappings, authorization, and revocation. No network call occurs in these
transactions. Approval routes now live in `backend/api/approvals.py`.

## Retry, ordering, and balance rules

- A lender/source/decision reference is unique. An exact retry returns the same
  record without restoring any old limit, extending expiry, or undoing revocation.
  Conflicting terms require a new reference and receive a conflict response.
- New decisions must be later than the farmer's last recorded decision. Reusing
  an older decision under a new key cannot roll the allocation back.
- A changed allocation revision requires a fresh preview. Concurrent reservations
  are checked against the proposed ceiling inside the update. Paid and reserved
  amounts are never reset. Concurrent conflicts are safe to refresh and retry.
- Once a farmer has a linked decision, the legacy CSV importer cannot overwrite
  its terms; another reviewed handoff is required. CSV and decision updates share
  farmer locking and conditional updates.
- Revocation expires an allocation only if that decision is still current.
  Revoking an older record does not expire its successor. Repeated revocation
  produces one business/audit effect.

## Revocation and existing transactions

Expiry/revocation blocks new input requests, further order approval, and invoice
creation. Unused credit becomes unavailable in the UI; historical limits,
reservations, and paid amounts remain visible. The allocation graphic reconciles
that unavailable remainder separately.

Revocation does **not** cancel existing invoices, reverse or suppress actual
payment evidence, release reservations, undo collection, or claim that an
external payment is prevented. An invoice operation already sent to the provider
can finish; reconcile it separately. Confirmed paid orders can still be collected
subject to the existing issue holds. A new, later lender decision is needed to
renew the allocation. No automatic repayment or collection authority is implied.

## Connection still required upstream

The credit-intelligence module remains separately maintained. It needs durable
officer decisions with amount, expiry, provenance, and authenticated lender
identity before automatic transfer is enabled. Implement a sender using this
contract, establish independently configured service trust and tenant mapping,
then test both deployed modules together. Do not copy credentials between repos,
trust a browser query string, or treat model prose as an authorization token.

The current tests prove this receiver and reviewed workflow using isolated
synthetic records. They do not prove an automated end-to-end portal connection,
production authentication, or live PayPal payment.

## Verification and visual review

27 October checks: **124 backend/data tests**, **six browser journeys**, and the
production frontend build pass. The new journey exercises mapping, decision
entry, a disabled authorization button before attestation, recording, history,
reasoned revocation, malformed-file recovery, and expired-farmer blocking.
Captures at 1440, 768, and 390 pixels show no horizontal page overflow.

Fresh Impeccable review: `ship`, with no material fixes requested for this
extension. The single mechanical detector pass returned no primary findings;
advisories concern incumbent literal type/color values outside the design
frontmatter, including sizes already described in its prose. They were not
silently waived or repaired as part of the feature.

Taste production inspection: **0 failures, 1 warning**, for the user-approved
colored header occupying roughly 13% of the first phone screen. The initial
numeric-alignment/tabular-figure warnings were corrected and the final inspection
confirms they are cleared. No claim of comprehensive accessibility certification
or operator usability research follows from these checks.

### Taste critique — final round

**Seen in one second:** this lender workspace links a farmer and records a
reviewed decision. **Idea:** make the identity link and authorization explicit
instead of treating a file as trust. **Live thing:** preview revalidation,
attestation, durable source references, and reasoned revocation drive real state
changes against the isolated application database.

**Layout:** inherited Waterline surfaces group identity, terms, preview, and
history. Desktop uses paired fields; phone uses one column. This is a dense
operational form, with prepared-file import secondary to the normal entry flow.

**Scores (subjective):** design 7.5/10, usability 7.5/10, creativity 7/10,
content 8/10; average 7.5/10. **Caps and next three improvements:** validate the
form length with actual lender operators, establish production officer/service
identity upstream, and connect a durable sender so repeated manual entry is no
longer necessary. These are follow-on work, not demonstrated capabilities.
