# Backend structure

- `main.py`: application setup and API entry points; provider orchestration is
  progressively moving into focused services.
- `schemas.py`: validated request models.
- `auth.py`: session checks, role requirements, and subject scoping.
- `services/orders.py`: scoped order access, presentation, and reservation helpers.
- `db.py`: database metadata, engine, and existing demonstration initialization.
- `management.py`: approval imports and catalogue management.
- `api/approvals.py`: lender-only routes for CSV import, farmer mappings, decision
  preview/authorization, history, and revocation.
- `handoffs.py`: versioned reviewed-decision contract, replay/order checks,
  allocation updates, revocation, and immutable order-audit linkage.
- `paypal.py`, `assistant.py`, `notifications.py`: integration behavior.

Transaction helpers use the caller's existing transaction. Keep provider network
calls outside it. Do not split a credit reservation from its stock reservation
while extracting services. API visibility never replaces server authorization.

The offline dataset tooling under `scripts/synthetic` owns its own schema and
output directory. It never initializes or resets the application database and
cannot provide genuine PayPal payment evidence.
