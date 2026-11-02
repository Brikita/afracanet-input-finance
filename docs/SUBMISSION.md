# Submission preparation

Status: **not submitted. PayPal sandbox payment, genuine callback and initial
Gemini checks passed; hosting, video and submission packaging remain.**
See [the current completion sprint](SPRINT_2026-11-02.md) and [compact judge setup](JUDGE_SETUP.md).

## Unified project description draft

**AFRACANet AI â€” from credit intelligence to agricultural inputs.**

AFRACANet AI brings credit assessment and input finance into one platform for
farmers, agricultural lenders, and agro-dealers. Its credit-intelligence module
supports loan officers with alternative-data assessment. A lender-authorized
allocation then enables the input-finance journey: the farmer requests catalogue
items, the lender approves the order and pays the supplier's PayPal invoice,
and the dealer records collection using the farmer's code.

The new input-finance module adds credit and inventory reservations, supplier
invoicing, verified payment reconciliation, collection controls, issue resolution,
and bilingual request-assistance/SMS adapters. The intended combined experience
connects the application, decision, payment, and handover through shared references.

**Current evidence boundary:** one repository contains both product modules. A lender-authorized
signed service handoff, isolated connected browser journey and synthetic data
stores are implemented. Actual Gemini request parsing and evidence summaries,
an actual USD 18 PayPal sandbox payment and a genuine verified callback have
separate check records. Do not present these separate fixtures as one real
customer transaction. Collection is tested with labelled simulated payments;
the 31 October fixture has no collection. On 2 November, a separate continuous synthetic scenario completed actual GDS/Gemini, signed approval, a new USD 18 PayPal sandbox payment and a recorded demonstration handover. It does not establish physical delivery of real goods. See [the linked verification](../datasets/reports/connected-sandbox-2026-11-02.json).

## Existing work and new contributions

The credit-intelligence codebase predates this PayPal expansion. Identify its
existing contributors and capabilities separately from work added during the
hackathon: the input-finance module, PayPal adapter/reconciliation, collection,
issues, and the implemented signed cross-module handoff. Link the single canonical repository, identify the imported credit module and
new PayPal work, and use the root setup route. The owner confirmed ownership and contributor permissions on 2 November 2026; both modules now include MIT licenses, with prior authorship and third-party notices retained.

The official rules allow significantly updated existing projects and require an
explanation of updates made during the submission period; the organizers decide
whether a change is significant. PayPal must be central to the project. See
[Project Requirements, New & Existing](https://paypalaihackathon.devpost.com/rules).

## Claims to support before finalizing

- Meaningful AI: Gemini interprets real English/Swahili requests and asks for
  clarification, with evaluation evidence. Demo parsing alone is not AI.
- Meaningful PayPal: show a real sandbox invoice payment and verified
  reconciliation. Simulated payments alone are not PayPal integration.
- Usability: report actual user feedback; distinguish hypotheses from evidence.
- Impact: report measured workflow outcomes, not assumed reductions in defaults.

## Demonstration sequence (175 seconds / 2:55, with AI voiceover and captions)

- 0:00–0:15: Farmer problem and audience.
- 0:15–0:45: Actual graph evidence, computed descriptive analytics and cited advisory AI.
- 0:45–1:05: Explicit lender decision and signed delivery receipt.
- 1:05–1:25: Farmer request, clarification, quote confirmation and reservation.
- 1:25–2:05: Supplier invoice, manual PayPal sandbox buyer payment and verified reconciliation.
- 2:05–2:30: Collection code, recorded demonstration handover and linked timeline.
- 2:30–2:55: Contribution, architecture, evidence limits and pilot ask.

The total includes opening/closing graphics. Preserve one scenario's references;
label recovery/time jumps and any separate fixtures. See the sprint plan for the
recording gate. No audio or final video is claimed until generated and reviewed.

## Checklist

- [x] Input-finance source repository and MIT license.
- [x] Both modules licensed under MIT with owner confirmation and retained notices.
- [ ] Final prior-work/new-work disclosure and submission description reviewed.
- [x] Lender-authorized approval handoff demonstrated across both modules.
- [x] Shared setup/start/check commands and compact profile generation.
- [x] One continuous linked provider-backed scenario with recorded demonstration collection.
- [ ] Complete clean-environment judge rehearsal.
- [x] Complete local setup instructions and runnable simulated workflow.
- [x] Explicit distinction between demonstration and external integrations.
- [x] Real PayPal sandbox payment and genuine signed callback verified in an isolated fixture.
- [x] Actual Gemini behavior and initial development-set/schema-citation results.
- [ ] Judge instructions tested from a clean checkout.
- [ ] Hosted demo or verified complete local-run route.
- [ ] Public YouTube demonstration under three minutes.
- [ ] Final tools/model disclosure and project description.
- [ ] Devpost submission completed and verified.

Early eligibility-review target: 5 November 2026, per the organizer email supplied on 2 November. The email gives no cutoff time. Do not report completion until
Devpost confirms the submitted entry and all required links are accessible.
