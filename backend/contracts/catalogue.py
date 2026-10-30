from pydantic import BaseModel, Field, field_validator


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
