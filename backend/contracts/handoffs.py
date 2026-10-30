from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SOURCE = "afracanet-credit"


class MappingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    source_system: Literal["afracanet-credit"] = SOURCE
    source_farmer_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
    farmer_id: str = Field(pattern=r"^farmer-[a-z0-9][a-z0-9-]{0,59}$")


class Handoff(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    schema_version: int = Field(strict=True, ge=1, le=1)
    source_system: Literal["afracanet-credit"]
    source_application_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
    source_farmer_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
    farmer_id: str = Field(pattern=r"^farmer-[a-z0-9][a-z0-9-]{0,59}$")
    lender_id: str = Field(min_length=1, max_length=100)
    approval_reference: str = Field(min_length=1, max_length=100)
    approved_by: str = Field(min_length=1, max_length=100)
    decision: Literal["LENDER_APPROVED"]
    limit_cents: int = Field(strict=True, ge=1, le=100_000_000)
    currency: Literal["USD"]
    approved_at: datetime
    expires_at: datetime
    data_provenance: Literal["synthetic", "real", "mixed", "unavailable"]

    @field_validator("lender_id", "approval_reference", "approved_by")
    @classmethod
    def nonblank(cls, value):
        if not value:
            raise ValueError("Must not be blank")
        return value

    @field_validator("approved_at", "expires_at", mode="before")
    @classmethod
    def timezone_required(cls, value):
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Use an ISO timestamp with a timezone") from exc
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise ValueError("Use an ISO timestamp with a timezone")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def ordered_dates(self):
        if self.expires_at <= self.approved_at:
            raise ValueError("Expiry must follow the lender decision")
        return self


class HandoffApply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Handoff
    allocation_revision: str = Field(pattern=r"^[a-f0-9]{64}$")
    confirm_lender_authorization: Literal[True]

    @field_validator("confirm_lender_authorization", mode="before")
    @classmethod
    def explicit_confirmation(cls, value):
        if value is not True:
            raise ValueError("Explicit lender confirmation is required")
        return value


class Revocation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    reason: str = Field(min_length=5, max_length=500)
