# AFRACANet AI — Credit Intelligence

AFRACANet AI connects agricultural credit evidence, lender decisions, input
finance, supplier payment and recorded collection. This repository owns credit
context and lender decisions; [input finance](https://github.com/Brikita/afracanet-input-finance)
owns execution. The two modules are presented as one product.

The active application provides a persistent lender queue, individually
provisioned local officer accounts, scoped graph retrieval, optional AI evidence
summaries, immutable lender decisions and a signed delivery outbox. The receiving
module verifies authority and farmer mappings before creating an allocation.
Recommendations, lender approvals, payments and collection are separate facts.

See [the connected workflow and setup](docs/CONNECTED_WORKFLOW.md) for commands,
configuration, data provenance and verification. The frontend uses React,
TypeScript, TanStack Start and Vite; the API uses FastAPI and SQLAlchemy. Graph
ownership and Neo4j queries remain here.

The local development graph contains 10,000 fictional farmers across 24 months
of authored histories, 928,163 nodes and 1,886,728 relationships, including
separately attributed public weather context. PostgreSQL stores the matching
history. These datasets support workflow and load testing; they do not establish
real creditworthiness, observed financial outcomes or payment evidence.

No calibrated score or GDS result is invented when unavailable. Live AI-provider
checks, verified USSD intake, production identity integration and whole-platform
visual unification remain further work. PayPal sandbox checks belong to input
finance and require its own credentials. No credentials are copied between repos.

Legacy graph/telecom/LLM research remains in `Backend/app.py`, `Backend/at.py`,
`Backend/databaseSeed.py` and `Featherless_LLM/`. The active application does not
launch those entry points. Do not run the legacy destructive graph seeder against
an existing database. The project remains connected to Lovable; preserve published
Git history.
