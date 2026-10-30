# Execution-module restructure

30 October 2026. The user moved completion of the repository restructure ahead
of the cross-module connection. This record covers `afracanet-input-finance`.
The separate credit-intelligence repository was inspected/cloned for the next
integration task; its code has not been changed by this restructure.

## Completed boundaries

- Backend composition is 68 lines, down from 570. Feature routers delegate to
  guarded services; transaction orchestration is outside the app entry point.
- Request contracts, external provider adapters, and business transactions have
  distinct packages. CSV allocations, handoffs, stock management, notifications,
  issues, recovery, and webhook funding retain their own responsibilities.
  Shared management audit writes have one implementation.
- Frontend composition is 172 lines, down from 1,286. Sign-in, shell, farmer
  requests, queues/details, management, approval forms/history, and catalogue
  editing have explicit feature modules. Session/polling behavior has one
  controller; drafts belong to the farmer feature and survive tab changes.
- Walkthrough choices live under `src/demo/`. This makes their scope explicit;
  it does not claim that operational identity/onboarding is implemented.
- The stylesheet is an ordered manifest over ten focused files. All 309
  top-level rules retain their semantic order. The production CSS content hash
  matches the pre-restructure build (`index-CnWU7Tj8.css`).
- Confirmed unused Python imports were removed. TypeScript unused-local and
  unused-parameter checks and Python import/format checks now run in CI.

Original monolithic files are replaced, not kept behind wrappers. Dataset tooling
retains its own isolated schema/output. Underwriting and graph internals remain
in the credit-intelligence repository.

## Verification

All 124 backend/data tests and all six browser journeys pass. The browser suite
also checks that a farmer's selected quantities survive leaving and returning to
the request tab. Production build, unused-code checks, Prettier, and Ruff pass.

A one-time AST comparison against `d7bac13` confirms unchanged bodies for 13
order/payment/issue/webhook functions, including reservation, funding, recovery,
and collection. No provider network call moved inside a database transaction.
Stylesheet comparison confirms the same 309-rule semantic sequence. This is
structural work, with no visual redesign or live-provider verification claim.

## Next integration work

The original goal remains: durable authenticated source decisions, an automatic
sender/receiver handoff, shared references/navigation, and cross-module tests.
Those behavior changes follow this structural checkpoint. Provider modes and
the manual handoff boundary are unchanged.
