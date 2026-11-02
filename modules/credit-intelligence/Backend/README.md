# Credit-intelligence API

The supported application is **FastAPI**, composed in `main.py`. Start both
AFRACANet modules from the repository root using `npm run dev:all`; see the
[root setup guide](../../../README.md) and [service configuration](../../../docs/MONOREPO.md).
Provision an individual officer using `npm run credit:provision -- OFFICER_ID LENDER_ID`.
Keep provider credentials and the signing private key separate from input finance.
Graph, replay and AI must be explicitly configured; missing sources stay unavailable.

The API retrieves lender-scoped graph context and attributed source records,
supports advisory evidence-cited summaries, and records explicit lender decisions.
Approved decisions and revocations cross to input finance through a signed durable
outbox. AI summaries never approve a loan, allocate money or authorize collection.
The active service currently provides no calibrated credit score.

## Verification

From the repository root, `npm run test:backend` runs both backend suites and the
signed handoff check. `npm run test:connected` additionally requires a configured
development graph and replay registry. See the [implementation audit](../../../docs/REMAINING_WORK_2026-11-02.md).

## Historical research code

`app.py`, `at.py`, `databaseSeed.py` and `Featherless_LLM/` are historical research,
not supported startup commands. **Do not run `databaseSeed.py` on an existing
graph: it clears data.** Legacy scoring examples do not establish a working active
GDS pipeline or predictive credit validation. Source history/attribution is retained.
