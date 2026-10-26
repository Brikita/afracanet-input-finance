"""Cross-record validation for generated fictional histories."""

import sqlite3


def validate_database(path, as_of):
    """Check cross-store referential, temporal and accounting invariants in SQL."""
    with sqlite3.connect(path) as conn:
        if conn.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Broken entity, relationship or ledger reference.")
        checks = {
            "future financial event": (
                "SELECT count(*) FROM ledger WHERE occurred_on > ?",
                (str(as_of),),
            ),
            "future graph event": (
                "SELECT count(*) FROM relationships WHERE occurred_on > ?",
                (str(as_of),),
            ),
            "loan repayment mismatch": (
                "SELECT count(*) FROM loans l WHERE l.repaid_minor != COALESCE((SELECT sum(amount_minor) FROM ledger x WHERE x.loan_id=l.id AND x.kind='loan_repayment'),0)",
                (),
            ),
            "loan disbursement mismatch": (
                "SELECT count(*) FROM loans l WHERE l.principal_minor != COALESCE((SELECT sum(amount_minor) FROM ledger x WHERE x.loan_id=l.id AND x.kind='loan_disbursement'),0)",
                (),
            ),
            "installment mismatch": (
                "SELECT count(*) FROM loans l WHERE l.principal_minor != (SELECT sum(due_minor) FROM installments i WHERE i.loan_id=l.id) OR l.repaid_minor != (SELECT sum(paid_minor) FROM installments i WHERE i.loan_id=l.id)",
                (),
            ),
            "repayment before origination": (
                "SELECT count(*) FROM ledger x JOIN loans l ON x.loan_id=l.id WHERE x.occurred_on < l.originated_on OR x.farmer_id != l.farmer_id",
                (),
            ),
            "allocation reservation mismatch": (
                "SELECT count(*) FROM allocations a WHERE a.reserved_minor != COALESCE((SELECT sum(amount_minor) FROM input_orders o WHERE o.allocation_id=a.id AND o.status IN ('REQUESTED','APPROVED','INVOICING','AWAITING_PAYMENT','PAYMENT_REVIEW')),0) OR a.spent_minor != COALESCE((SELECT sum(amount_minor) FROM input_orders o WHERE o.allocation_id=a.id AND o.status IN ('READY_FOR_COLLECTION','COLLECTED')),0)",
                (),
            ),
            "cross-tenant relationship": (
                "SELECT count(*) FROM relationships r JOIN entities s ON r.source_id=s.id JOIN entities t ON r.target_id=t.id WHERE s.tenant_id != t.tenant_id AND s.tenant_id != 'context' AND t.tenant_id != 'context'",
                (),
            ),
            "wrong allocation farmer": (
                "SELECT count(*) FROM input_orders o JOIN allocations a ON o.allocation_id=a.id WHERE o.farmer_id != a.farmer_id",
                (),
            ),
            "unlabelled entity": (
                "SELECT count(*) FROM entities WHERE source_kind != 'synthetic_replay'",
                (),
            ),
        }
        for label, (sql, params) in checks.items():
            if conn.execute(sql, params).fetchone()[0]:
                raise ValueError(label)
        return {
            table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in (
                "entities",
                "relationships",
                "ledger",
                "loans",
                "installments",
                "allocations",
                "input_orders",
            )
        }
