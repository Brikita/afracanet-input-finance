# AFRACANet Input Finance — execution plan

Started: 13 October 2026. Internal submission target: **30 October 2026**.
Official deadline: 12 November 2026, 23:00 Africa/Nairobi.
The internal target is a planning goal, not a scheduled automation or a guarantee.

## Product

Help Kenyan agricultural lenders turn existing credit approvals into traceable
input orders, supplier payments, and farmer collection records.

Initial customer hypothesis: one agricultural SACCO. Users: farmers, lender
staff, and verified agro-dealers. Initial catalogue: a few seed and fertilizer
products. Choose the county and crop through access to a willing pilot partner.

Credit scoring, underwriting, loan origination, interest calculations, and
repayment servicing remain with the lender. The platform coordinates execution.

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

External-service adapters require credentials and real end-to-end verification.
Their existence in the code does not mean those integrations have been demonstrated.

## Remaining before submission

- Configure supplier-owned PayPal sandbox app and lender sandbox buyer account.
- Confirm real invoice request payload, payer experience, payment records, and webhook.
- Configure Gemini and evaluate English, Swahili, code-switching, and ambiguity.
- Add SMS channel through Africa's Talking; document any simulator honestly.
- Improve demo access controls for a hosted demonstration and add abuse limits.
- Add approval import, editable dealer catalogue, issue reporting, and recovery UI.
- Verify PostgreSQL execution before recommending it for hosted use.
- Document invoice failure recovery, refund/cancellation handling, and restart recovery.
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

1. Working demonstration: one successful transaction and one meaningful exception.
2. Short deck: evidence, customer, workflow, competition, business model, pilot ask.
3. Technical brief: architecture, access, payment verification, evaluation, limitations.
4. Pilot proposal: participants, responsibilities, measures, budget, expansion gates.
