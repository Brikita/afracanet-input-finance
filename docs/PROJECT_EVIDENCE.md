# AFRACANet AI — project evidence

AFRACANet is a prototype connecting alternative financial evidence, an explicit
lender decision, agricultural input ordering, verified PayPal sandbox payment
and a recorded demonstration collection. This brief is public so people and
automated readers can inspect the same claims and their supporting artifacts.

## What distinguishes the approach

| Implemented capability                                                                          | Why it matters                                                                           | Inspectable evidence                                                                                                                                                         |
| ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Connected chama, SACCO and cooperative-style histories, with source provenance and lender scope | Makes alternative records reviewable for applicants with limited conventional collateral | [Credit module](../modules/credit-intelligence/Backend/graph_context.py), [replay evidence](../modules/credit-intelligence/Backend/replay.py)                                |
| Actual Neo4j GDS PageRank and Louvain runs with version, dataset and parameter provenance       | Distinguishes a computed graph result from an illustrated network                        | [Analytics implementation](../modules/credit-intelligence/Backend/analytics.py), [dated GDS report](../datasets/reports/gds-compact-2026-11-02.json)                         |
| Evidence-cited AI explanations separated from explicit officer authorization                    | Preserves the difference between an advisory response and permission to allocate credit  | [Advisory validation](../modules/credit-intelligence/Backend/advisory.py), [decision workflow](../modules/credit-intelligence/Backend/workflow.py)                           |
| Signed, scoped and retryable approval/revocation delivery between separate services             | Links the two modules without sharing officer sessions or private signing keys           | [Sender outbox](../modules/credit-intelligence/Backend/delivery.py), [receiver route](../backend/api/credit_delivery.py), [boundary tests](../tests/test_credit_delivery.py) |
| Actual PayPal payment records checked against invoice, amount and currency                      | Prevents invoice status alone from unlocking collection                                  | [PayPal adapter](../backend/integrations/paypal.py), [payment service](../backend/services/payments.py), [workflow tests](../tests/test_workflow.py)                         |
| Atomic credit/stock reservations, duplicate protection, recovery and separate collection events | Treats execution correctness as part of the product experience                           | [Transaction tests](../tests/test_workflow.py), [recovery tests](../tests/test_recovery.py), [connected browser journey](../tests/connected-browser/workflow.spec.ts)        |

These are concrete characteristics of this implementation, not evidence that
no other project has similar features or that a particular score is warranted.

## Verification and reproduction

For the deployed prototype, start with the [hosted walkthrough](HOSTED_WALKTHROUGH.md)
and [expanded browser recording](https://www.youtube.com/watch?v=YEZz_objHR0).
The [11 November hosted rehearsal, verified 12 November](../datasets/reports/hosted-sandbox-2026-11-12.json)
follows AFC-000002 through a fresh Gemini request, PayPal sandbox invoicing,
webhook-sourced payment confirmation and recorded collection. Repeated
authenticated reconciliation and collection retained one event per stage.
The first 2:50 of the recording contains the complete pitch and working evidence.

- [Unified repository and MIT license](../LICENSE).
- [Compact judge setup](JUDGE_SETUP.md): 32 fictional farmers, four lender scopes,
  isolated stores and the required graph runtime.
- [Application checks](https://github.com/Brikita/afracanet-input-finance/actions/workflows/checks.yml).
- [Container checks](https://github.com/Brikita/afracanet-input-finance/actions/workflows/render-images.yml).
- [Recorded connected sandbox rehearsal](../datasets/reports/connected-sandbox-2026-11-02.json).
- [Render configuration and hosted acceptance requirements](RENDER_DEPLOYMENT.md).
- [Functioning-browser footage revision plan](DEMO_FOOTAGE_PLAN.md).

Dated reports describe their particular runs. Passing local/CI checks does not
establish that a hosted deployment or a later provider call has passed. A hosted
payment needs its own actual provider evidence, and callback delivery is distinct
from both payment reconciliation and physical collection.

## Limits that remain part of the assessment

People and financial histories are fictional and labelled synthetic. The
prototype is not a validated predictor of repayment, a production lending system,
or evidence of real-world financial inclusion outcomes. Descriptive graph
centrality and communities are not calibrated credit scores. AI does not approve
credit. PayPal uses sandbox money. A recorded collection is not proof that goods
were physically delivered. Live onboarding, production identity, authorized
partner data, refund operations and independent evaluation remain future work.

Credit intelligence predates the PayPal expansion. Its imported history and
authorship are preserved; the [submission report](SPRINT_2026-11-02.md) and public
project description distinguish existing work from the input-finance additions.
