"""Validated API request shapes; no persistence or provider calls."""

from typing import Literal

from pydantic import BaseModel, Field


class Login(BaseModel):
    persona: str
    access_code: str = Field(max_length=256)


class ItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(ge=1, le=100)


class OrderRequest(BaseModel):
    client_request_id: str = Field(min_length=8, max_length=100)
    items: list[ItemRequest] = Field(min_length=1, max_length=10)


class AssistantRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CollectionRequest(BaseModel):
    code: str = Field(min_length=6, max_length=12)


class RecoveryRequest(BaseModel):
    invoice_id: str | None = Field(default=None, pattern=r"^INV2-[A-Z0-9-]{4,100}$")


class IssueRequest(BaseModel):
    client_request_id: str = Field(min_length=8, max_length=100)
    category: Literal["stock", "payment", "collection", "other"]
    detail: str = Field(min_length=5, max_length=1000)


class IssueResolution(BaseModel):
    resolution: str = Field(min_length=5, max_length=1000)
