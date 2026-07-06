import uuid

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """API input — user sends plain text only."""

    message: str = Field(..., min_length=1, max_length=2000, description="Natural language message from the user")
    session_id: str | None = Field(None, description="Return from previous response to continue the conversation")

    @field_validator("message", mode="before")
    @classmethod
    def strip_message(cls, v: str) -> str:
        stripped = str(v).strip()
        if not stripped:
            raise ValueError("message must not be blank")
        return stripped

    @field_validator("session_id", mode="before")
    @classmethod
    def validate_session_id(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("session_id must be a valid UUID")
        return v


class ChatResponseModel(BaseModel):
    """API response."""

    reply: str
    session_id: str
    data: dict | list | None = None
    actions: list[str] = Field(default_factory=list)
