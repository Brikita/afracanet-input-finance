from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


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
