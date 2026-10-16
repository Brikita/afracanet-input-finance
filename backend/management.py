"""Lender-supplied approvals and supplier catalogue maintenance."""
import csv
import hashlib
import io
import json
from datetime import datetime, timezone

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import insert, select, update

from . import db


class Approval(BaseModel):
    farmer_id: str = Field(pattern=r"^farmer-[a-z0-9][a-z0-9-]{0,59}$")
    name: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=160)
    limit_cents: int = Field(ge=0, le=100_000_000)
    expires_at: datetime
    approval_reference: str = Field(min_length=1, max_length=100)

    @field_validator("name", "location", "approval_reference")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Must not be blank")
        return value.strip()

    @field_validator("expires_at")
    @classmethod
    def future_expiry(cls, value):
        if value.tzinfo is None or value <= datetime.now(timezone.utc):
            raise ValueError("Use a future date with a timezone")
        return value.astimezone(timezone.utc)


class ApprovalImport(BaseModel):
    csv_text: str = Field(min_length=1, max_length=200_000)
    preview: bool = True


class ProductEdit(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    unit: str = Field(min_length=1, max_length=80)
    price_cents: int = Field(strict=True, ge=1, le=100_000_000)
    stock: int = Field(strict=True, ge=0, le=1_000_000)
    revision: str | None = Field(default=None, max_length=64)

    @field_validator("name", "category", "unit")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Must not be blank")
        return value.strip()


def log(conn, user, action, detail):
    conn.execute(insert(db.management_events).values(
        actor=user["subject"], action=action, detail=detail, created_at=db.now(),
    ))


def product_revision(row):
    return hashlib.sha256(json.dumps(dict(row), sort_keys=True).encode()).hexdigest()


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
                raise HTTPException(422, f"CSV row {index} has missing or extra fields.")
            try:
                if not row["limit_cents"].isascii() or not row["limit_cents"].isdigit():
                    raise ValueError("limit_cents must be whole cents")
                entry = Approval.model_validate(row)
            except (ValidationError, ValueError) as exc:
                raise HTTPException(422, f"CSV row {index}: check the farmer ID, text fields, whole-cent limit, and future expiry with timezone.") from exc
            if entry.farmer_id in seen:
                raise HTTPException(422, f"CSV row {index}: duplicate farmer ID.")
            seen.add(entry.farmer_id)
            parsed.append(entry)
    except csv.Error as exc:
        raise HTTPException(422, "Malformed CSV. Check quotation marks and separators.") from exc
    if not parsed:
        raise HTTPException(422, "Include at least one farmer approval.")
    summaries = []
    # Apply revalidates everything in one transaction; previews cannot promise later availability.
    with db.engine.begin() as conn:
        for entry in sorted(parsed, key=lambda item: item.farmer_id):
            existing = conn.execute(select(db.farmers).where(db.farmers.c.id == entry.farmer_id)).mappings().first()
            if existing and existing["lender_id"] != user["subject"]:
                raise HTTPException(403, "An approval belongs to another lender.")
            committed = (existing["reserved_cents"] + existing["spent_cents"]) if existing else 0
            if entry.limit_cents < committed:
                raise HTTPException(409, f"{entry.farmer_id}: limit cannot be below reserved and already paid credit ({committed} cents).")
            values = entry.model_dump(exclude={"farmer_id"})
            values["expires_at"] = entry.expires_at.isoformat()
            summaries.append({"farmer_id": entry.farmer_id, "name": entry.name,
                              "change": "update" if existing else "create", "limit_cents": entry.limit_cents,
                              "committed_cents": committed, "expires_at": values["expires_at"]})
            if body.preview:
                continue
            if existing:
                changed = conn.execute(update(db.farmers).where(
                    db.farmers.c.id == entry.farmer_id, db.farmers.c.lender_id == user["subject"],
                    db.farmers.c.reserved_cents + db.farmers.c.spent_cents <= entry.limit_cents,
                ).values(**values))
                if changed.rowcount != 1:
                    raise HTTPException(409, "Credit changed during import. Preview and retry.")
            else:
                conn.execute(insert(db.farmers).values(id=entry.farmer_id, lender_id=user["subject"], **values))
        if not body.preview:
            log(conn, user, "APPROVAL_IMPORT", {"farmers": [entry.farmer_id for entry in parsed], "count": len(parsed)})
    return {"preview": body.preview, "rows": summaries,
            "message": f"{len(parsed)} approval(s) {'validated. Review before importing.' if body.preview else 'imported.'}"}


def save_product(product_id, body, user):
    with db.engine.begin() as conn:
        existing = conn.execute(select(db.products).where(db.products.c.id == product_id)).mappings().first()
        if existing and existing["supplier_id"] != user["subject"]:
            raise HTTPException(404, "Product not found.")
        if existing:
            if body.revision != product_revision(existing):
                raise HTTPException(409, "Inventory changed since you opened this edit. Close and reopen the product, then retry.")
            changed = conn.execute(update(db.products).where(
                db.products.c.id == product_id, db.products.c.supplier_id == user["subject"],
                db.products.c.reserved <= body.stock,
                *[db.products.c[key] == value for key, value in existing.items()],
            ).values(**body.model_dump(exclude={"revision"})))
            if changed.rowcount != 1:
                raise HTTPException(409, "On-hand stock cannot be lower than stock reserved for existing orders.")
        else:
            if body.revision is not None:
                raise HTTPException(409, "The product no longer exists. Refresh the inventory.")
            conn.execute(insert(db.products).values(id=product_id, supplier_id=user["subject"], **body.model_dump(exclude={"revision"})))
        log(conn, user, "PRODUCT_SAVED", {"product_id": product_id, **body.model_dump(exclude={"revision"})})
    return {"message": "Catalogue saved. Existing order prices remain unchanged."}
