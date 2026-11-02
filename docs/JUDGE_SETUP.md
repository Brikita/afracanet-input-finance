# Compact judge environment

This profile runs the actual AFRACANet services against **32 fictional farmers**,
12 months of authored histories, four lender scopes and a separate Neo4j graph.
It creates zero active credit, orders or payments. A new officer decision is
required. It does not need the historical repository or existing local databases.
The default parser is deterministic and payments are simulated; configured
provider mode is a separate explicit choice.

## Prerequisites and preparation

Install Python 3.13, Node.js 22.16+, Java 21, and Neo4j Community 5.26. Obtain the
compatible GDS 2.13.4 plugin from the [official release](https://github.com/neo4j/graph-data-science/releases/tag/2.13.4).
See [Neo4j/GDS compatibility](https://neo4j.com/docs/graph-data-science/current/installation/supported-neo4j-versions/).
The runtimes/plugin are external prerequisites and are not committed to this repo.
Do not point at or reset an existing Neo4j data directory.

From a fresh clone at the repository root:

```powershell
npm run setup
npm run judge:prepare
npm run judge:start -- --neo4j-home C:/tools/neo4j-community-5.26 --java-home C:/tools/jdk-21 --gds-jar C:/tools/neo4j-graph-data-science-2.13.4.jar
```

Use actual extracted runtime paths. On Linux/macOS, use their absolute runtime
paths with the same commands. Existing profiles are never overwritten; use
`--name another-name` on both commands for a new independent scenario.
Profiles use graph Bolt 27687/HTTP 27474, APIs 28000/28001, public/input UI 25173
and credit UI 25174. Occupied ports cause startup to stop before importing data.
The graph and application processes are owned by the supervisor; Ctrl+C stops
them. From another terminal, `npm run judge:start -- --stop` requests shutdown.

Generated files are ignored and private:

- `data/judge/compact/inputs.env`: execution-store configuration and generated demo access code.
- `data/judge/compact/input-access.json`: the same local demonstration access code, for the operator.
- `modules/credit-intelligence/data/judge/compact/credit.env`: credit store, graph and signing settings.
- `modules/credit-intelligence/data/judge/compact/local-officer-accounts.json`: four individual local officer accounts.
- The signing private key and read-only replay registry stay in the credit profile;
  only public verification material reaches input finance.

Open `http://127.0.0.1:25174/`, sign in with the first generated officer and inspect
`farmer-synth-000001`. It is in lender `SYN-LENDER-000`. Graph relationships and
repayment evidence are actual queries against labelled authored records. Missing
AI remains unavailable; no fake summary is generated.

The input UI is `http://127.0.0.1:25173/`, product page `/about`. Use the generated
access code for the shared demonstration login, then select the appropriate
synthetic participant. This is explicitly demonstration identity.

## Compute actual GDS

While the profile graph is running, from the repository root:

```powershell
.venv/Scripts/python.exe modules/credit-intelligence/scripts/run_graph_analytics.py --env-file modules/credit-intelligence/data/judge/compact/credit.env --lender SYN-LENDER-000
```

On Linux/macOS use `.venv/bin/python`. Repeat for another lender scope if needed.
The runner checks graph size and algorithm memory estimates, uses only that
lender's Farmer/SavingsGroup/Cooperative membership network, runs PageRank and
Louvain, saves results with dataset/run/version/parameter provenance, and drops
its temporary in-memory projection. It does not alter source graph properties,
decisions, allocations or payments. Community IDs are run-specific. These are
descriptive synthetic graph results, not default-risk groups or calibrated scores.

In the officer case, choose **Load computed GDS**. The graph, node selector and
accessible table show actual saved results. Selecting that run for review and
recording a decision preserves its ID and manifest reference in the decision's
terms. An AI summary, when available, similarly records its evaluation ID.

## Configured provider rehearsal

First configure each service's own ignored environment file with its own Gemini
settings; configure PayPal sandbox in the root environment. See the root README
and `MONOREPO.md`. Do not copy provider credentials into generated profiles or
share an officer session/signing key. Existing operator-local env path references
remain optional; a fresh installation uses the module's own `.env`.

Restart the judge profile with the same arguments plus `--providers`. Each API
loads its own existing provider env file, while its isolated profile retains DB,
graph, signing, URL and demo-access settings. Root execution uses sandbox/Gemini;
SMS remains a labelled local preview. Invoice prefixes are generated per store
and must remain unchanged after a remote invoice exists.

Explicit stages from the repository root:

```powershell
.venv/Scripts/python.exe scripts/rehearse_judge.py inspect
.venv/Scripts/python.exe scripts/rehearse_judge.py create-invoice
# Manually pay that specific invoice with the configured sandbox buyer.
.venv/Scripts/python.exe scripts/rehearse_judge.py reconcile
.venv/Scripts/python.exe scripts/rehearse_judge.py collect
```

Pass `--name another-name` consistently for a named profile. `inspect` retrieves
evidence only; the other stages explicitly exercise synthetic lender/order
actions. `create-invoice` uses actual Gemini summaries/request interpretation,
explicit officer authorization, signed handoff and PayPal sandbox invoicing. It
never pays on the buyer's behalf. It preserves shared references in the ignored
`rehearsal.json` and will not blindly repeat uncertain invoice creation.
`collect` records a demonstration handover only after actual full payment is
verified. It is not observed physical delivery of real goods.

Do not delete an invoice-associated store or change its prefix to reset a demo.
Inspect `PAYMENT_REVIEW`/`INVOICING` and use the existing correlated recovery UI.
Repeated reconciliation/collection must preserve exactly one business effect.
Stable public callbacks/hosting are a separate deployment task; this loopback
profile uses authenticated reconciliation when callbacks cannot reach it.

## Checks and limitations

`npm run test:backend` covers profile generation, tenant-scoped read-only replay,
operator startup, analytics authorization and transaction behavior. Both frontend
builds and browser suites remain separate root commands. Add `--check` to judge
startup for a startup-and-shutdown smoke check; it requires all profile ports free.
Use `--analytics --check` to compute actual GDS and inspect graph/replay/results
through the scoped officer API before shutdown. CI repeats this from a clean
Linux checkout after dependency installation and checksum-verified runtime fetch.
Confirm the actual run before claiming its new graph step passed.

Local development runtimes have been used for initial verification. A successful
local compact run does not claim a clean-machine installation or a deployed
prototype. Record actual clean-environment results before claiming those gates.
The million-node development pack, authentic partner records, live handset SMS,
production identity and predictive model validation are outside this compact demo.
