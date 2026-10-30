"""Batch lender allocations; preview and apply share validation and preserve commitments."""

import csv
import io

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import insert, select, update

from .. import db
from ..contracts.allocations import Approval
from .audit import log


def import_approvals(body, user):
    reader = csv.DictReader(io.StringIO(body.csv_text.lstrip("\ufeff")), strict=True)
    fields = list(Approval.model_fields)
    parsed = []
    seen = set()
    try:
        if reader.fieldnames != fields:
            raise HTTPException(422, "CSV columns must be: " + ",".join(fields))
        for index, row in enumerate(reader, start=2):
            if len(parsed) >= 1000:
                raise HTTPException(422, "Import at most 1,000 farmers at a time.")
            if None in row or any(value is None for value in row.values()):
                raise HTTPException(
                    422, f"CSV row {index} has missing or extra fields."
                )
            try:
                if not row["limit_cents"].isascii() or not row["limit_cents"].isdigit():
                    raise ValueError("limit_cents must be whole cents")
                entry = Approval.model_validate(row)
            except (ValidationError, ValueError) as exc:
                raise HTTPException(
                    422,
                    f"CSV row {index}: check the farmer ID, text fields, whole-cent limit, and future expiry with timezone.",
                ) from exc
            if entry.farmer_id in seen:
                raise HTTPException(422, f"CSV row {index}: duplicate farmer ID.")
            seen.add(entry.farmer_id)
            parsed.append(entry)
    except csv.Error as exc:
        raise HTTPException(
            422, "Malformed CSV. Check quotation marks and separators."
        ) from exc
    if not parsed:
        raise HTTPException(422, "Include at least one farmer approval.")
    summaries = []
    # Apply revalidates everything in one transaction; previews cannot promise later availability.
    with db.engine.begin() as conn:
        for entry in sorted(parsed, key=lambda item: item.farmer_id):
            existing = (
                conn.execute(
                    select(db.farmers)
                    .where(db.farmers.c.id == entry.farmer_id)
                    .with_for_update()
                )
                .mappings()
                .first()
            )
            if existing and existing["lender_id"] != user["subject"]:
                raise HTTPException(403, "An approval belongs to another lender.")
            linked = conn.execute(
                select(db.approval_handoffs.c.id)
                .where(
                    db.approval_handoffs.c.farmer_id == entry.farmer_id,
                )
                .limit(1)
            ).first()
            if linked:
                raise HTTPException(
                    409,
                    "This allocation has a linked lender decision. Use a new reviewed handoff to change it.",
                )
            committed = (
                (existing["reserved_cents"] + existing["spent_cents"])
                if existing
                else 0
            )
            if entry.limit_cents < committed:
                raise HTTPException(
                    409,
                    f"{entry.farmer_id}: limit cannot be below reserved and already paid credit ({committed} cents).",
                )
            values = entry.model_dump(exclude={"farmer_id"})
            values["expires_at"] = entry.expires_at.isoformat()
            summaries.append(
                {
                    "farmer_id": entry.farmer_id,
                    "name": entry.name,
                    "change": "update" if existing else "create",
                    "limit_cents": entry.limit_cents,
                    "committed_cents": committed,
                    "expires_at": values["expires_at"],
                }
            )
            if body.preview:
                continue
            if existing:
                changed = conn.execute(
                    update(db.farmers)
                    .where(
                        db.farmers.c.id == entry.farmer_id,
                        db.farmers.c.lender_id == user["subject"],
                        db.farmers.c.limit_cents == existing["limit_cents"],
                        db.farmers.c.expires_at == existing["expires_at"],
                        db.farmers.c.approval_reference
                        == existing["approval_reference"],
                        db.farmers.c.reserved_cents + db.farmers.c.spent_cents
                        <= entry.limit_cents,
                    )
                    .values(**values)
                )
                if changed.rowcount != 1:
                    raise HTTPException(
                        409, "Credit changed during import. Preview and retry."
                    )
            else:
                conn.execute(
                    insert(db.farmers).values(
                        id=entry.farmer_id, lender_id=user["subject"], **values
                    )
                )
        if not body.preview:
            log(
                conn,
                user,
                "APPROVAL_IMPORT",
                {
                    "farmers": [entry.farmer_id for entry in parsed],
                    "count": len(parsed),
                },
            )
    return {
        "preview": body.preview,
        "rows": summaries,
        "message": f"{len(parsed)} approval(s) {'validated. Review before importing.' if body.preview else 'imported.'}",
    }
