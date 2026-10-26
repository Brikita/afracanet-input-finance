# AFRACANet AI — input-finance execution plan

Started: 13 October 2026. Internal submission target: **30 October 2026**.
Official deadline: 12 November 2026, 23:00 Africa/Nairobi.
The internal target is a planning goal, not a scheduled automation or a guarantee.

## Product

Present one AFRACANet AI platform: credit intelligence and officer review in
afracanet-green-path, followed by traceable input orders, supplier payments, and
collection in this module. See [the unified platform brief](PLATFORM.md).

Initial customer hypothesis: one agricultural SACCO. Users: farmers, lender
staff, and verified agro-dealers. Initial catalogue: a few seed and fertilizer
products. Choose the county and crop through access to a willing pilot partner.

The AI module supports credit assessment; the lender owns the credit decision,
terms, and repayment servicing. This module coordinates execution after approval.
Do not treat an AI recommendation as an authorized allocation or completed payment.

## Delivery gates

| Target           | Gate                            | Acceptance evidence                                                                                                    |
| ---------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 13–16 Oct        | Independent runnable foundation | Three roles, persistent orders, credit/stock reservation, simulated lifecycle, automated checks                        |
| 17–20 Oct        | External services               | Real PayPal sandbox invoice paid by the lender and reconciled; Gemini ambiguity handling measured on labelled examples |
| 21–24 Oct        | Access and workflow refinement  | SMS integration, real-user feedback, understandable exceptions, working hosted build or complete local setup           |
| 25–27 Oct        | Demonstration and documentation | Repeatable end-to-end sandbox demo, public code/license, AI/tool disclosure, technical brief                           |
| 28–30 Oct        | Submission                      | Public YouTube video under three minutes, Devpost description and testing instructions, final submission review        |
| After submission | Pilot preparation               | Named lender/dealer interest, operational responsibilities, payment route and data handling validated                  |

## First slice implemented

- Four illustrative participant personas: two farmers, one lender, one dealer.
- Persistent catalogue, pre-approved allocations, orders, and timeline records.
- Atomic reservation; cancellation releases reservations.
- Lender approval, dealer invoice, payment confirmation, collection code.
- Authenticated role/subject checks within the demonstration access model.
- CSV reconciliation export.
- Explicit demo parser and simulated payment modes.
- PayPal sandbox adapter and Gemini structured-output adapter.
- Backend financial integrity tests and browser journey checks.
- CSV approval preview/import, including new farmer demo participants.
- Dealer catalogue editing with reservation protection and stale-edit checks.
- Existing invoice recovery with correlation checks and unpaid-cancellation safeguards.
- Participant issue reporting, lender resolutions, and collection holds.
- Opted-in, verified farmer SMS updates with a durable outbox and demo/sandbox modes.
- A labelled bilingual evaluation runner, with strict model-output validation.
- An isolated PostgreSQL CI job alongside the existing SQLite checks.

External-service adapters require credentials and real end-to-end verification.
Their existence in the code does not mean those integrations have been demonstrated.

## Remaining before submission

- Connect the two modules through a lender-authorized allocation with a shared
  farmer mapping and reference; existing CSV import is the manual starting point.
- Update upstream approval SMS so it does not invite collection before payment.
- Explain prior AI work versus the new PayPal expansion in the combined submission.
- Configure supplier-owned PayPal sandbox app and lender sandbox buyer account.
- Confirm real invoice request payload, payer experience, payment records, and webhook.
- Configure Gemini and evaluate English, Swahili, code-switching, and ambiguity.
- Verify Africa's Talking sandbox sends. Current channel covers outbound updates;
  real handset delivery, SMS ordering, and USSD remain beyond this prototype slice.
- Improve demo access controls for a hosted demonstration and add abuse limits.
- Review PostgreSQL CI evidence before recommending a hosted configuration;
  migrations, backups, and deployment operations still need implementation.
- Validate documented invoice recovery and unpaid cancellation against real PayPal sandbox records; paid refunds remain an operator workflow.
- Prepare hosted deployment, judge instructions, public YouTube video, and submission.

## Discovery and commercial evidence

Interview roughly two lender staff, three dealers, and five farmers. Record the
current order, payment, and reconciliation process; delays; errors; and willingness
to try a supervised pilot. This is directional research, not a representative survey.

Existing examples include Apollo Agriculture and DigiFarm/Sidian input financing.
Differentiation is a hypothesis around adoption by existing lenders, integration,
bilingual assistance, and reconciliation. Do not claim existing products lack
these capabilities without investigation.

Revenue hypothesis: lender subscription with implementation/support and usage
tiers. Test willingness to pay and cost to serve before setting prices.

Pilot hypothesis: one lender, two or three dealers, 25–50 farmers, subject to
partner agreement and production-readiness review. Measure processing time,
staff effort, reconciliation discrepancies, abandonment, support cost, and
collection completion. Default and yield outcomes require longer observation.

## Presentation package

After core workflow completion, build a public product information page with
an animated explanation of the farmer, lender, and dealer flow. Keep this behind
core features, external-service verification, and exception handling in priority.

1. Working demonstration: one successful transaction and one meaningful exception.
2. Short deck: evidence, customer, workflow, competition, business model, pilot ask.
3. Technical brief: architecture, access, payment verification, evaluation, limitations.
4. Pilot proposal: participants, responsibilities, measures, budget, expansion gates.
