# Scalable synthetic scenario packs

These packs are fictional, uncalibrated workflow and graph-exploration material.
Every entity carries `source_kind=synthetic_replay`. They use no customer data,
network calls, AI calls, phone numbers, national identifiers, or real payment
references. Outcomes are authored scenarios, not observed credit labels.

## Generate

From the repository root on Windows:

```powershell
.venv/Scripts/python.exe scripts/generate_synthetic.py --profile walkthrough --output data/synthetic/walkthrough-v1
.venv/Scripts/python.exe scripts/generate_synthetic.py --profile development --output data/synthetic/development-v1
.venv/Scripts/python.exe scripts/generate_synthetic.py --profile stress --output data/synthetic/stress-v1
```

Use `.venv/bin/python` on Linux. All commands require a new output directory and
refuse to overwrite one. Bulk artifacts stay under ignored `data/`; never commit
generated databases. A failure can leave an incomplete directory for inspection;
only a pack with a completed `manifest.json` has passed validation and export.

| Profile     | Farmers | Monthly context |
| ----------- | ------: | --------------: |
| walkthrough |     100 |       24 months |
| development |  10,000 |       24 months |
| stress      | 100,000 |       36 months |

`--farmers`, `--months`, `--seed`, and `--as-of` override defaults. The reproducible
default snapshot date is 26 October 2026. Event counts follow scenarios: new
members and thin files deliberately have fewer records. Larger packs need disk
space for the database and CSV exports; measure before choosing the stress size.

## One world, multiple representations

- `scenario.sqlite`: a populated, isolated relational dataset with foreign keys,
  financial constraints, and indexes. It is not the execution app database schema.
- `graph-nodes.csv`: stable entity IDs, type labels, tenant, structured properties
  encoded as a JSON string, and synthetic provenance.
- `graph-relationships.csv`: stable endpoints, relationship types, dates, and
  structured properties. Its endpoints match the relational entity registry.
- `ledger.csv`, `loans.csv`, `installments.csv`, `allocations.csv`, and
  `input_orders.csv`: relational exports carrying the same IDs and monetary facts.
- `manifest.json`: configuration, actual row counts by entity/relationship type,
  provenance, byte sizes, and SHA-256 hashes of completed files.

The graph CSV headers use Neo4j-style ID, label, relationship, and string-property
annotations. Structured `properties` remain a JSON string until an importer
deliberately maps them. No Neo4j database has been loaded or benchmarked by these
tools. Choose a new isolated graph database and review schema mapping before
import; do not use the upstream destructive seeder. PostgreSQL import also needs
an explicit adapter rather than assuming the execution schema matches this pack.

Entities cover farmers, households, farms, reference regions, crop types, seasons,
cooperatives, savings groups, lenders, officers, dealers, catalogue products,
loans, ledger events, applications, decisions, allocations, input orders,
invoices, replay payments, collections, and issues. Graph counts include ledger
events as entities; they are not counts of unique people.

Tenant-owned counterparties stay within the farmer's lender partition; shared
crop and reference-region entities are contextual. This is useful permission-test
material but does not establish authorization in a running service.

## Scenario and accounting boundaries

Scenarios include regular histories, late installments, partial repayment, new
members, thin files, sparse networks, seasonal receipts, and missing context.
Input orders span requested, approved, invoicing, awaiting payment, payment
review, ready for collection, collected, and cancelled states. Partial replay
payments stay under review; full replay payment is required for replay collection.

The current snapshot assigns an approved demonstration allocation per farmer.
It does not yet cover rejected/pending application cohorts, full inventory
accounting, repayment servicing, or authentic external provider failures. Current
ledger events describe fictional historical receipts and purchases, not a complete
double-entry accounting system. Invalid/cross-tenant cases are introduced in
isolated automated tests, not silently mixed into valid demonstration records.

Historical KES loan and ledger amounts are fictional. USD allocations/catalogue
quotes are separately assigned examples, not currency conversions or real Kenyan
dealer prices. `REPLAY-INVOICE` and `REPLAY-PAYMENT` identifiers are visibly
synthetic. This data never enters the application's PayPal verification path.

Public weather is not invented or embedded. Reference-region assignments are
fictional; joining attributed weather later does not establish actual farm
exposure. The generator uses no credit score to construct repayment histories.
It still cannot establish real-world predictive accuracy or statistical realism.

## Validation and measurements

Generation checks relationship endpoints, entity provenance, currency boundaries,
past event dates, tenant consistency, loan disbursements and repayments,
installment totals, allocation ownership, reservation/spend totals, and collection
payment requirements. Tests deliberately corrupt copies to verify rejection.

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_synthetic_dataset.py
.venv/Scripts/python.exe scripts/benchmark_synthetic.py data/synthetic/development-v1 --output data/synthetic/development-benchmark.json
```

The benchmark uses read-only local SQLite and reports actual query plans and
timings for a bounded farmer history, graph neighborhood, pending-order queue,
and loan history. Results do not measure Neo4j/GDS, network latency, concurrent
requests, frontend rendering, or production capacity.
