# Submission preparation

## Current package, 12 November 2026

The [Devpost entry](https://devpost.com/software/afracanet-ai) is already submitted.
The current update aligns its video, public links and private testing instructions
with the hosted browser rehearsal. Saving the revised fields and verifying the
public entry remain distinct from organizer acceptance.

- Video: https://www.youtube.com/watch?v=YEZz_objHR0. The local master is 480.000
  seconds at 1920×1080/30 fps; YouTube/Devpost display 8:01. The owner explicitly
  selected the expanded upload for submission. The form says only the first
  three minutes will be reviewed; the complete pitch and working evidence end
  at **2:50**. This is not a claim of a duration waiver or organizer approval.
- Public story: [DEVPOST_STORY.md](DEVPOST_STORY.md).
- Hosted inspection: [HOSTED_WALKTHROUGH.md](HOSTED_WALKTHROUGH.md).
- Recorded case: `farmer-synth-000001`, lender `SYN-LENDER-000`, order **AFC-000002**.
- Existing paid/collected records can be reviewed without another sandbox purchase.
- Local reproduction remains available through [JUDGE_SETUP.md](JUDGE_SETUP.md);
  its default deterministic parser/simulated payment mode is distinct from the
  hosted Gemini/PayPal sandbox configuration.
- [Dated hosted evidence](../datasets/reports/hosted-sandbox-2026-11-12.json)
  records the observed payment, collection, duplicate checks and export verification.
- Demo officer credentials and the input access code belong in the private
  testing field. Provider keys, sessions and signing secrets remain operator-local.

The 8 November reviewer asked for footage of the functioning project. The new
film contains actual browser operation. Confirm the saved YouTube embed and
public links after the final form update; do not equate this with re-review.

## Historical preparation snapshot, 3 November 2026

The following plan/checklist describes the earlier release and film. Its
pre-submission and 175-second-video statements are retained as historical context
and are superseded by the current package above.

Status: **not submitted. Core release checks passed. The narrated 175-second MP4
is exported and technically verified; public upload and submission remain.**
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
recording gate. The owner approved rendering on 3 November. The final MP4 measures
175.000 seconds at 1920×1080/30 fps; full decoding, seven scene audio samples and
the payment narration range passed verification. The decoded contact sheet was
inspected. See [export verification](../datasets/reports/video-export-2026-11-03.json).

## Checklist

- [x] Input-finance source repository and MIT license.
- [x] Both modules licensed under MIT with owner confirmation and retained notices.
- [ ] Final prior-work/new-work disclosure and submission description reviewed.
- [x] Lender-authorized approval handoff demonstrated across both modules.
- [x] Shared setup/start/check commands and compact profile generation.
- [x] One continuous linked provider-backed scenario with recorded demonstration collection.
- [x] Clean Linux compact judge rehearsal, including actual GDS, passed in CI at f6b5447.
- [x] Complete local setup instructions and runnable simulated workflow.
- [x] Explicit distinction between demonstration and external integrations.
- [x] Real PayPal sandbox payment and genuine signed callback verified in an isolated fixture.
- [x] Actual Gemini behavior and initial development-set/schema-citation results.
- [x] Automated setup/run route tested from a clean checkout; see CI run 41518097793.
- [x] Verified local-run route supplied; hosted functional demo remains optional work.
- [ ] Public YouTube demonstration under three minutes.
- [ ] Final tools/model disclosure and project description.
- [ ] Devpost submission completed and verified.

The [3 November release plan](RELEASE_2026-11-03.md) sets today's finish line.
[Devpost-ready copy](DEVPOST_COPY.md) is prepared for final review and link completion.

Early eligibility-review target: 5 November 2026, per the organizer email supplied on 2 November. The email gives no cutoff time. Do not report completion until
Devpost confirms the submitted entry and all required links are accessible.
