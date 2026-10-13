# AFRACANet Input Finance

Independent project for agricultural input finance. Do not copy underwriting,
Neo4j, GDS, or credentials from afracanet-green-path.

## Product boundary

Start with externally approved credit. Coordinate the farmer request, lender
approval, supplier invoice, verified payment, and recorded collection.
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
- Frontend: npm run build
- Browser: npm run test:ui (isolated test data, Edge on Windows; Chromium on Linux)
- Run relevant checks when transaction behavior changes.
- Commit titles use plain descriptions, without feat/fix/docs prefixes.
