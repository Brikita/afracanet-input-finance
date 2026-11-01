# AFRACANet AI — Unified Repository

This is the canonical AFRACANet AI repository. Credit intelligence lives in
`modules/credit-intelligence/`; input finance and PayPal execution live in root
`src/` and `backend/`. Graph/Neo4j/GDS internals stay inside the credit module.
Connect the services through the explicit, lender-authorized signed handoff.
Never merge provider credentials, officer sessions or private signing keys.
Module `.env` files and operator-local data stay ignored. Never copy credentials
from the historical source repository. Preserve published Git history; imported
credit history was sanitized privately before its additive merge.

## Product boundary

Start with externally approved credit. Coordinate the farmer request, lender
approval, supplier invoice, verified payment, and recorded collection.
An upstream AI recommendation is not a lender approval, a credit allocation,
a payment, or permission to collect. Label manual and automated handoffs accurately.
Do not represent simulated payment or deterministic parsing as PayPal or AI.
Do not claim escrow, guaranteed delivery, eliminated default, or production readiness.

## Implementation

- React/TypeScript frontend, FastAPI backend, SQLAlchemy data layer.
- Integer cents for amounts; USD sandbox examples are illustrative.
- Server-side role and subject checks on every transaction action.
- Credit and stock reservations must remain atomic and nonnegative.
- Keep network calls outside database transactions.
- Require actual PayPal payment records; invoice status alone is insufficient.
- Duplicate requests/events must not duplicate business effects.
- Never commit credentials, databases, session tokens, or local environments.

## Verification

- Python: .venv/Scripts/python.exe -m pytest -q (Windows)
- Both backends and signed handoff: npm run test:backend
- Frontends: npm run check:all and npm run build:all
- Connected browser: npm run test:connected (requires configured local graph)
- Browser: npm run test:ui (isolated test data, Edge on Windows; Chromium on Linux)
- Run relevant checks when transaction behavior changes.
- Commit titles use plain descriptions, without feat/fix/docs prefixes.
