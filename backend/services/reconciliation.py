"""Reconciliation behavior; API dependencies are supplied by the route layer."""

import csv
import io
from fastapi.responses import Response
from sqlalchemy import select
from .. import db
from ..auth import require, scoped_orders


def export_csv(user):
    require(user, "lender")
    with db.engine.connect() as conn:
        rows = conn.execute(select(db.orders).where(scoped_orders(user)).order_by(db.orders.c.id)).mappings().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["order", "farmer", "amount", "currency", "status", "invoice", "payment_reference", "payment_mode"])
    for row in rows:
        writer.writerow([f"AFC-{row['id']:06d}", row["farmer_id"], f"{row['amount_cents']/100:.2f}",
                         row["currency"], row["status"], row["invoice_id"], row["payment_reference"], row["payment_mode"]])
    return Response(output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="afracanet-reconciliation.csv"'})
