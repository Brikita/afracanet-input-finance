from typing import Literal

from pydantic import BaseModel, Field


class ContactRequest(BaseModel):
    phone: str = Field(pattern=r"^\+254[17][0-9]{8}$")
    language: Literal["en", "sw"] = "en"
    consent: bool


class VerifyRequest(BaseModel):
    code: str = Field(pattern=r"^[0-9]{6}$")
