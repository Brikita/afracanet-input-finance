"""Catalogue behavior; API dependencies are supplied by the route layer."""

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from .. import assistant, db, management
from ..auth import require
from ..schemas import AssistantRequest


def product_save(product_id: str, body: management.ProductEdit, user):
    require(user, "supplier")
    import re
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", product_id):
        raise HTTPException(422, "Use a product ID with lowercase letters, numbers, and hyphens (up to 80 characters).")
    return management.save_product(product_id, body, user)


def interpret_request(body: AssistantRequest, user):
    require(user, "farmer")
    with db.engine.connect() as conn:
        catalogue = [dict(row) for row in conn.execute(select(db.products)).mappings()]
    try:
        return assistant.interpret(body.text, catalogue)
    except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
        raise HTTPException(502, "The assistant could not interpret this request. Please use the catalogue.") from exc
