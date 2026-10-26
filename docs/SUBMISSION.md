# Submission preparation

Status: **not submitted; external PayPal and AI verification remains outstanding.**

## Unified project description draft

**AFRACANet AI — from credit intelligence to agricultural inputs.**

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

**Current evidence boundary:** these are two repositories within one product.
The execution module has a tested local demonstration and a manual approval import.
Automatic transfer from the AI portal, live provider verification, and a complete
cross-module demonstration remain outstanding. The default payment/parser/SMS
modes are simulations; describe the exact demonstrated mode in the final entry.

## Existing work and new contributions

The credit-intelligence codebase predates this PayPal expansion. Identify its
existing contributors and capabilities separately from work added during the
hackathon: the input-finance module, PayPal adapter/reconciliation, collection,
issues, and the eventual cross-module handoff. Include both source locations and
one clear setup route. Check the AI module's ownership and open-source licensing;
the MIT license in this repository does not automatically license the other repo.

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

## Demonstration sequence (approximately 2:40)

- 0:00–0:15: One farmer journey, from access to credit to inputs.
- 0:15–0:40: AI assessment in the officer portal and explicit lender decision.
- 0:40–0:55: Show the allocation reaching input finance, labelling any manual import.
- 0:55–1:15: Farmer request and clarification; confirm quote and reserve credit/stock.
- 1:15–1:55: Dealer invoice; lender pays in PayPal sandbox; reconcile actual payment.
- 1:55–2:20: Farmer collection code; dealer handover; show linked records and an issue hold.
- 2:20–2:40: Customer evidence, commercial hypothesis, pilot ask, and new PayPal contribution.

## Checklist

- [x] Input-finance source repository and MIT license.
- [ ] Prior-work/new-work disclosure and complete source licensing for both modules.
- [ ] Lender-authorized approval handoff demonstrated across both modules.
- [ ] One reproducible combined setup and shared-reference demonstration.
- [x] Complete local setup instructions and runnable simulated workflow.
- [x] Explicit distinction between demonstration and external integrations.
- [ ] Real PayPal sandbox transaction recorded end-to-end.
- [ ] Actual Gemini behavior and evaluation results.
- [ ] Judge instructions tested from a clean checkout.
- [ ] Hosted demo or verified complete local-run route.
- [ ] Public YouTube demonstration under three minutes.
- [ ] Final tools/model disclosure and project description.
- [ ] Devpost submission completed and verified.

Internal submission target: 30 October 2026. Do not report completion until
Devpost confirms the submitted entry and all required links are accessible.
