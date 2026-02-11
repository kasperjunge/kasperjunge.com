from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactSubmissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    message: str = Field(min_length=1, max_length=5000)
    website: str | None = Field(default=None, max_length=255)

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_required_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("must not be empty")
            return stripped
        return value

    @field_validator("website", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value


class ContactSubmissionResponse(BaseModel):
    ok: bool = True
    id: int | None = None
    created_at: datetime | None = None
