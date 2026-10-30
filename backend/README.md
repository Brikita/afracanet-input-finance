# Backend structure

`main.py` composes the application, lifespan, middleware, error handlers, feature
routers, and optional built frontend. It contains no transaction orchestration.

| Boundary        | Ownership                                                          |
| --------------- | ------------------------------------------------------------------ |
| `api/`          | HTTP routes, dependency injection, transport parsing               |
| `contracts/`    | Validated request shapes, including the versioned approval handoff |
| `services/`     | Scoped reads, authorization, transactions and management audit     |
| `integrations/` | PayPal sandbox, Gemini and SMS sandbox HTTP adapters               |
| `auth.py`       | Session validation and role/subject scoping                        |
| `db.py`         | Metadata, engine, initialization and audit/outbox coordination     |
| `config.py`     | Environment configuration and startup validation                   |

Feature routes cover sessions, state, catalogue/interpretation, allocations and
handoffs, orders, payments/recovery, issues, reconciliation, notifications, and
PayPal webhooks. Services retain their own authorization guards.

Transaction helpers use the caller's existing transaction. Keep provider network
calls outside it. Do not split a credit reservation from its stock reservation
while extracting services. API visibility never replaces server authorization.

The offline dataset tooling under `scripts/synthetic` owns its own schema and
output directory. It never initializes or resets the application database and
cannot provide genuine PayPal payment evidence.

`services/payments.py` owns invoice/recovery orchestration and the one funding
transition reused by verified webhooks. SMS outbox writes still participate in
the business transaction; dispatch is separate. Shared management audit writes
are in `services/audit.py`. Tests patch canonical `backend.integrations.*` paths.

Install development checks with `pip install -r backend/requirements-dev.txt`.
On Windows:

```powershell
.venv/Scripts/python.exe -m ruff check --select F,I backend
.venv/Scripts/python.exe -m ruff format --check backend
.venv/Scripts/python.exe -m pytest -q
```
