"""Catalogue behavior; API dependencies are supplied by the route layer."""

import hashlib
import json

import httpx
from fastapi import HTTPException
from sqlalchemy import insert, select, update

from .. import db
from ..auth import require
from ..contracts.catalogue import ProductEdit
from ..contracts.requests import AssistantRequest
from ..integrations import assistant
from .audit import log


def product_save(product_id: str, body: ProductEdit, user):
    require(user, "supplier")
    import re

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,79}", product_id):
        raise HTTPException(
            422,
            "Use a product ID with letters, numbers, and hyphens (up to 80 characters).",
        )
    return save_product(product_id, body, user)


def interpret_request(body: AssistantRequest, user):
    require(user, "farmer")
    with db.engine.connect() as conn:
        query = select(db.products)
        if body.supplier_id is not None:
            query = query.where(db.products.c.supplier_id == body.supplier_id)
        catalogue = [dict(row) for row in conn.execute(query).mappings()]
    if not catalogue:
        raise HTTPException(404, "The selected supplier has no catalogue items.")
    if len({p["supplier_id"] for p in catalogue}) != 1:
        raise HTTPException(422, "Choose a supplier before interpreting your request.")
    try:
        return assistant.interpret(body.text, catalogue)
    except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
        raise HTTPException(
            502,
            "The assistant could not interpret this request. Please use the catalogue.",
        ) from exc


def product_revision(row):
    return hashlib.sha256(json.dumps(dict(row), sort_keys=True).encode()).hexdigest()


def save_product(product_id, body, user):
    with db.engine.begin() as conn:
        existing = (
            conn.execute(select(db.products).where(db.products.c.id == product_id))
            .mappings()
            .first()
        )
        if existing and existing["supplier_id"] != user["subject"]:
            raise HTTPException(404, "Product not found.")
        if existing:
            if body.revision != product_revision(existing):
                raise HTTPException(
                    409,
                    "Inventory changed since you opened this edit. Close and reopen the product, then retry.",
                )
            changed = conn.execute(
                update(db.products)
                .where(
                    db.products.c.id == product_id,
                    db.products.c.supplier_id == user["subject"],
                    db.products.c.reserved <= body.stock,
                    *[db.products.c[key] == value for key, value in existing.items()],
                )
                .values(**body.model_dump(exclude={"revision"}))
            )
            if changed.rowcount != 1:
                raise HTTPException(
                    409,
                    "On-hand stock cannot be lower than stock reserved for existing orders.",
                )
        else:
            if body.revision is not None:
                raise HTTPException(
                    409, "The product no longer exists. Refresh the inventory."
                )
            conn.execute(
                insert(db.products).values(
                    id=product_id,
                    supplier_id=user["subject"],
                    **body.model_dump(exclude={"revision"}),
                )
            )
        log(
            conn,
            user,
            "PRODUCT_SAVED",
            {"product_id": product_id, **body.model_dump(exclude={"revision"})},
        )
    return {"message": "Catalogue saved. Existing order prices remain unchanged."}
