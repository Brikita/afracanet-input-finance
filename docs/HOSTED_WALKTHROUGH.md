# Hosted prototype walkthrough

- [Product and context](https://afracanet-inputs.onrender.com/about)
- [Credit officer workspace](https://afracanet-credit.onrender.com/)
- [Input finance workspace](https://afracanet-inputs.onrender.com/)
- [Recorded browser demonstration](https://www.youtube.com/watch?v=YEZz_objHR0)
- [Source evidence and limitations](PROJECT_EVIDENCE.md)

The project owner supplies demonstration access separately. You do not need a
Gemini key, PayPal API secret, graph password or signing key to use the hosted
screens. All people and histories are fictional. The services use Gemini and
PayPal sandbox; SMS remains a labelled demonstration preview.

## Quick inspection of the recorded case

The video gives a complete pitch and working evidence in the first **2:50**,
then continues with the detailed walkthrough. Its local master is eight minutes;
YouTube/Devpost display it as 8:01. No new purchase is needed to inspect the
existing evidence.

- Credit case: `WORKFLOW-farmer-synth-000001`, lender `SYN-LENDER-000`.
- Input order: **AFC-000002**, one 2 kg pack of maize seed, **USD 18**.
- Recorded result: **COLLECTED**, after a PayPal-webhook payment confirmation.
- Open the order timeline to inspect request, approval, invoice, payment and
  collection as separate events. Inspect its invoice and payment references.
- **AFC-000001 is the older unpaid order.** It is not the paid case in this video.

These are the results observed in the November rehearsal, not a promise that a
later refund or other authorized action cannot change the displayed state.
The application's current status and provider records remain authoritative.
See the [dated evidence record](../datasets/reports/hosted-sandbox-2026-11-12.json).

## Review connected evidence

1. Sign into credit review with the supplied individual demonstration officer
   account. The first account belongs to `SYN-LENDER-000`.
2. Select **All statuses** and open `farmer-synth-000001` to inspect the recorded
   hosted rehearsal. Use **Load graph context** to inspect connected records and
   their sources, including authored repayment history.
3. Use **Load computed GDS**, select a node, and open run provenance. The hosted
   fixture has 32 fictional farmers across four lender partitions. This lender's
   computed membership projection has 11 nodes; it is not a million-node GDS run
   or a calibrated credit score.
4. On the approved case, **Read recorded AI summary** retrieves the advisory
   evaluation pinned to the decision. It does not generate a replacement answer
   or silently update the decision's evidence. Pending cases can request fresh
   Gemini advice, subject to provider availability.
5. Inspect the officer, allocation, decision reference and **Delivery to input
   finance** acknowledgment. This is signed service delivery. The AI summary
   cannot grant credit, pay an invoice or authorize collection.

## Follow input finance

1. Open input finance and enter the separately supplied demonstration access
   code. The sign-in cards identify the actual configured synthetic participants.
2. Select the farmer experience for **Synthetic Farmer 000001**. Choose the
   supplier before requesting interpretation. For the hosted rehearsal this is
   **Synthetic Dealer 1**.
3. A request such as “I need one 2 kg pack of maize seed” is interpreted against
   that supplier's catalogue. Inspect the supplier, item, quantity and USD total
   before confirming. These USD prices are illustrative and separate from KES
   historical loan records.
4. Confirming reserves available credit and stock atomically; it does not pay.
   The lender separately approves the input order, then the supplier confirms
   stock and issues the PayPal sandbox invoice.
5. Inspect **AFC-000002** for the paid and collected hosted rehearsal and its timeline.
   Its displayed status is authoritative. Payment is not established by an
   invoice link or this guide. A genuine PayPal payment record must match the
   invoice, amount and currency before collection becomes eligible.
6. New sandbox checkout requires a Personal sandbox buyer account. The project
   owner can assist with that step; no real-money checkout is enabled. Existing
   verified records can be inspected without performing another payment.
7. Collection is a separate dealer action using the farmer's collection code,
   available only after full payment verification. A recorded demonstration
   handover does not establish physical delivery of real goods.

**View as** switches fictional participants using the current demonstration
access code. The code is not retained when the page reloads. If a switch then
requires authentication, sign out and enter the supplied code again. Officer
and input-finance sessions are independent; neither is transferred between
modules.

For the simplest review, inspect AFC-000002 first in the farmer, lender and
supplier views. Creating another order is optional and produces a different
reference; do not present its invoice or payment as evidence for AFC-000002.
Do not reset the store, change an invoice prefix or overwrite the recorded case.

## Boundaries and troubleshooting

- Provider delays or errors are shown explicitly. No deterministic parser is
  substituted for Gemini and no simulated payment substitutes for PayPal here.
- An unpaid order must remain ineligible for collection. Partial payments,
  refunds and uncertain preparation require review; do not create a second
  invoice to work around an uncertain response. Use the existing recovery flow.
- Retrying reconciliation or collection must preserve one business effect.
- The public product page's teaching graph and preserved payment-proof example
  are explanatory material. They do not execute the authenticated workflow.
- This is a temporary prototype deployment with synthetic data, shared input
  demonstration identity and individual local officer accounts. Production
  identity, real partner records and independent lending evaluation remain future
  work. See [deployment status](RENDER_DEPLOYMENT.md) and
  [local reproduction](JUDGE_SETUP.md).
