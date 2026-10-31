# Connected prototype checkpoint â€” 31 October 2026

The connected core now has real provider evidence and a shared Waterline working
interface. The public product page is a separate, approved design in progress;
this checkpoint does not mark hosting or submission complete.

## Completed and checked

| Area                   | Result and evidence boundary                                                                                                                                                                                          |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PayPal payment         | Actual USD 18 sandbox payment, authenticated reconciliation, unchanged balances on repeat verification. Isolated synthetic allocation fixture, not a live loan.                                                       |
| Signed callback        | Genuine PayPal event resent to a callback-only HTTPS listener; signature verified; one receipt and one payment effect after repeat delivery. Payment was already reconciled.                                          |
| Credit summary         | Separate Gemini configuration produced three structured evidence-cited summaries. Unknown citations, unsupported numeric claims and unauthorized cases are rejected. No score, approval or money action is generated. |
| Credit evidence        | Scoped relationship filters, directly connected source-record inspection, authored KES repayment history and separately attributed reference weather. Missing context stays explicit.                                 |
| Shared working UI      | Waterline navigation, queue, case, evidence, decision and history; desktop, tablet and phone captures reviewed. Reviewer disposition: ship, no material fixes.                                                        |
| Cleanup                | Removed unused starter component wrappers and 41 unused direct dependencies in credit. Kept required TanStack/Lovable route composition and preserved Git history.                                                    |
| Dependency maintenance | Credit runtime audit: zero reported vulnerabilities; full audit: 14 moderate development-tool findings. No high/critical findings. No forced incompatible major upgrade.                                              |

The existing development pack contains 10,000 fictional farmers over 24 months,
with 928,163 graph nodes and 1,886,728 relationships. This sprint improves access
to those records; it does not turn synthetic histories into observed outcomes.

## Verification

- Input-finance backend: **145 tests passed**.
- Credit backend: **16 tests passed**.
- Input-finance browser: **six Edge journeys passed**, isolated data/provider modes.
- Connected browser: **one Edge journey passed**, including record inspection,
  explicit lender authorization, signed delivery, independent receiving sign-in,
  revocation and responsive captures. AI is deliberately unavailable in this
  isolated check; actual provider calls are separately reported.
- Both frontend production builds and credit TypeScript check passed.

See [provider evidence](PROVIDER_CHECKS_2026-10-31.md),
[callback setup](CALLBACK_SETUP.md), and the
[existing connected data/authority report](CONNECTED_PLATFORM_2026-10-30.md).

Manual output review found and corrected a minor-unit interpretation error in
an initial AI summary. Three actual provider cases passed again after formatting
amounts before the model and rejecting unsupported numeric claims. These bounded
checks do not establish semantic accuracy.

## Demonstrate without mixing evidence

1. Open credit intelligence at `http://127.0.0.1:5174/`. Use a privately provisioned
   local officer account; select a fictional farmer in that lender's scope.
2. Load graph context, inspect a connected record and its provenance, then request
   an advisory summary. Keep missing facts visible and historical KES amounts
   distinct from illustrative USD input amounts.
3. Record a decision only with explicit lender authorization. Show its delivery
   receipt and open the receiving decision reference. Sign in independently to
   input finance at `http://127.0.0.1:5173/`.
4. Continue the input request, supplier invoice and payment workflow according to
   the visible provider mode. A new sandbox invoice requires a separate manual
   buyer payment; a prior fixture payment does not pay a new order.
5. Present the preserved USD 18 provider-check record as separate payment evidence.
   Its physical collection has not been recorded. Automated tests exercise
   collection controls with explicitly simulated payments.

## Remaining before presentation and submission

- Finish the approved public payment-proof page, its interactions and review.
- Set up stable HTTPS hosting, durable stores and a permanent callback URL; test
  access from another device. Existing local tunnels are temporary.
- Verify SMS delivery if included, and broaden provider recovery/refund scenarios.
- Test a clean-checkout setup and give judges a private, scoped access route.
- Review prior-work attribution/licensing across both repositories, finalize the
  tool/model disclosure, record the public video and complete Devpost submission.

Partner data, farmer trials, production identity, independent model evaluation,
credit calibration and production operations remain beyond this prototype.
