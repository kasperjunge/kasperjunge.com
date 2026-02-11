from pydantic import BaseModel, Field, field_validator


class PageviewCreate(BaseModel):
    path: str = Field(min_length=1, max_length=2048)
    title: str | None = Field(default=None, max_length=255)
    referrer: str | None = Field(default=None, max_length=2048)
    session_id: str | None = Field(default=None, max_length=128)

    @field_validator("path", mode="before")
    @classmethod
    def normalize_path(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("must not be empty")
            return stripped
        return value

    @field_validator("title", "referrer", "session_id", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value
