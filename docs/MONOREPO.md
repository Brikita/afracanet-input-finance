# AFRACANet AI: one repository

Both working modules now live in this checkout. Root `src/`, `backend/`, `tests/`
and `datasets/` retain input-finance and shared data responsibilities. Credit
intelligence, its UI and graph ownership are in `modules/credit-intelligence/`.
The signed lender-authorized service handoff remains the integration boundary.
This consolidation does not create a shared officer session or turn a model
recommendation into an approval, payment or collection authorization.

## Setup and operation

Use Python 3.13 and Node.js 22.16+ with npm. From the repository root:

```powershell
npm run setup
# Create these only when absent; configure each independently.
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path modules/credit-intelligence/.env)) { Copy-Item modules/credit-intelligence/.env.example modules/credit-intelligence/.env }
npm run dev:all
```

`setup` installs both frontend lockfiles and the shared pinned Python runtime in
root `.venv`. `dev:all` starts the two APIs (8000 input, 8001 credit) and two UIs
(5173 public/input, 5174 credit). It checks for occupied ports before launching,
terminates its own children on failure/interrupt, and never starts legacy Flask,
telecom or graph-seeder entry points. Stop older development servers before using
it. Existing PostgreSQL and Neo4j services remain independently managed.

Each service starts with an isolated environment. Provider/signing/database
variables inherited from another service are removed before its own environment
file is loaded. Frontend children receive only public continuation/API settings
from the supervisor. No private key or officer session is shared between apps.

A new credit installation needs an officer account before sign-in:

```powershell
npm run credit:provision -- OFFICER_ID LENDER_ID
```

The root command uses the same private configuration paths as the supervisor.
The password is requested privately. Replace IDs with the lender scope being
configured. Graph/replay data and AI summaries require their documented separate
connections; unavailable sources remain visibly unavailable. No partner dataset
or calibrated credit score is introduced by this migration.

## Existing local configuration and data

Consolidation imports tracked code only. It does not copy `.env`, databases,
session tokens, installed environments or the large generated graph into Git.
The existing operator can retain private files in their current locations using
ignored `data/workspace.local.json`:

```json
{
  "credit_env_file": "C:/operator/credit.env",
  "credit_data_dir": "C:/operator/credit-data"
}
```

Only paths are accepted. These references are local conveniences, not a second
source checkout requirement. A fresh clone defaults to the module's own `.env`
and `data/`. Existing environment values containing absolute signing-key or
runtime paths keep referring to those files. `CREDIT_ENV_FILE` can explicitly
override the credit configuration file for a service or CLI. Do not remove an
older local directory while it still holds referenced private files or databases.
Reprovision credentials in their intended service when moving to a new machine.

## Checks

```powershell
npm run check:all
npm run build:all
npm run test:backend
npm run check:startup
npm run test:ui
npm run test:connected
```

Backend checks run each module in a separate process with isolated SQLite stores,
empty provider keys and no credit worker, then exercise actual signing, retry,
deduplication and revocation between the two FastAPI apps. Payments in these
checks are explicitly simulated. `test:ui` uses isolated execution data.
`test:connected` also inspects the configured development Neo4j/replay records;
it requires those local stores to be available and does not invent a replacement
graph. Its defaults now point inside this repository. GitHub CI installs both
frontends and the shared Python lock, checks both APIs and TypeScript projects,
builds both frontends, checks all four services, and runs the signed handoff and
isolated public/input journeys.

Separate frontend lockfiles preserve TanStack Start/Vite 8 and Vite 6 compatibility.
The shared Python lock retains input-finance pins where the module locks overlap;
the original credit lock remains in its folder as import provenance. Root
`npm run build` remains the input-only build; use `build:all` for the whole product.

## Imported history and current source

The credit source branch contained 97 commits. A private bare copy was scanned
with checksum-verified Gitleaks 8.30.1. Three historical secret findings were
removed before a history-preserving additive merge under the module prefix.
Authors, messages and commit relationships remain; hashes change with the prefix
and sanitation. The original published source history was not amended, rebased
or force-pushed. The 76-file source HEAD was verified byte-identical at import.

See [import provenance](provenance/credit-import.json) and [commit mapping](provenance/credit-history-map.tsv).
The old GitHub repository remains a historical source; this repository is the
canonical place for new work. The old Lovable connection was not silently
reconfigured to point at the monorepo. Imported credit licensing remains recorded
in [its notice](../modules/credit-intelligence/NOTICE.md).

Older dated records describe the two-repository arrangement at their checkpoints.
This document and the root README supersede those setup paths. Stable hosting,
provider edge-case checks, model validation and submission are still separate work.
