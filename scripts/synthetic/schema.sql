PRAGMA foreign_keys = ON;
CREATE TABLE entities (
    id TEXT PRIMARY KEY, kind TEXT NOT NULL, tenant_id TEXT NOT NULL,
    properties TEXT NOT NULL, source_kind TEXT NOT NULL CHECK(source_kind = 'synthetic_replay')
);
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES entities(id),
    target_id TEXT NOT NULL REFERENCES entities(id), kind TEXT NOT NULL,
    occurred_on TEXT NOT NULL, properties TEXT NOT NULL
);
CREATE TABLE loans (
    id TEXT PRIMARY KEY REFERENCES entities(id), farmer_id TEXT NOT NULL REFERENCES entities(id),
    principal_minor INTEGER NOT NULL CHECK(principal_minor > 0),
    repaid_minor INTEGER NOT NULL CHECK(repaid_minor >= 0),
    outstanding_minor INTEGER NOT NULL CHECK(outstanding_minor >= 0),
    currency TEXT NOT NULL CHECK(currency = 'KES'),
    originated_on TEXT NOT NULL, final_due_on TEXT NOT NULL,
    CHECK(principal_minor = repaid_minor + outstanding_minor)
);
CREATE TABLE installments (
    loan_id TEXT NOT NULL REFERENCES loans(id), sequence INTEGER NOT NULL,
    due_on TEXT NOT NULL, paid_on TEXT,
    due_minor INTEGER NOT NULL CHECK(due_minor > 0),
    paid_minor INTEGER NOT NULL CHECK(paid_minor >= 0 AND paid_minor <= due_minor),
    PRIMARY KEY(loan_id, sequence)
);
CREATE TABLE ledger (
    id TEXT PRIMARY KEY REFERENCES entities(id), farmer_id TEXT NOT NULL REFERENCES entities(id),
    counterparty_id TEXT NOT NULL REFERENCES entities(id), loan_id TEXT REFERENCES loans(id),
    kind TEXT NOT NULL, amount_minor INTEGER NOT NULL CHECK(amount_minor > 0),
    currency TEXT NOT NULL CHECK(currency = 'KES'), occurred_on TEXT NOT NULL
);
CREATE TABLE allocations (
    id TEXT PRIMARY KEY REFERENCES entities(id), farmer_id TEXT NOT NULL REFERENCES entities(id),
    limit_minor INTEGER NOT NULL CHECK(limit_minor > 0),
    reserved_minor INTEGER NOT NULL CHECK(reserved_minor >= 0),
    spent_minor INTEGER NOT NULL CHECK(spent_minor >= 0),
    currency TEXT NOT NULL CHECK(currency = 'USD'), expires_on TEXT NOT NULL,
    CHECK(reserved_minor + spent_minor <= limit_minor)
);
CREATE TABLE input_orders (
    id TEXT PRIMARY KEY REFERENCES entities(id), farmer_id TEXT NOT NULL REFERENCES entities(id),
    allocation_id TEXT NOT NULL REFERENCES allocations(id), supplier_id TEXT NOT NULL REFERENCES entities(id),
    status TEXT NOT NULL CHECK(status IN ('REQUESTED','APPROVED','INVOICING','AWAITING_PAYMENT','PAYMENT_REVIEW','READY_FOR_COLLECTION','COLLECTED','CANCELLED')),
    amount_minor INTEGER NOT NULL CHECK(amount_minor > 0), currency TEXT NOT NULL CHECK(currency = 'USD'),
    payment_evidence_kind TEXT NOT NULL CHECK(payment_evidence_kind = 'synthetic_replay'),
    replay_paid_minor INTEGER NOT NULL CHECK(replay_paid_minor >= 0),
    created_on TEXT NOT NULL, collected_on TEXT,
    CHECK(replay_paid_minor <= amount_minor),
    CHECK((status IN ('READY_FOR_COLLECTION','COLLECTED') AND replay_paid_minor = amount_minor)
       OR status NOT IN ('READY_FOR_COLLECTION','COLLECTED')),
    CHECK((status = 'COLLECTED' AND collected_on IS NOT NULL) OR (status != 'COLLECTED' AND collected_on IS NULL))
);
