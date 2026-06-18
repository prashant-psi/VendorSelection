from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """API input — user sends plain text only."""

    message: str = Field(..., min_length=1 , description="Natural language message from the user")
    session_id: str | None = Field(None, description="Return from previous response to continue the conversation")


class ChatResponseModel(BaseModel):
    """API response."""

    reply: str
    session_id: str
    data: dict | list | None = None
    actions: list[str] = Field(default_factory=list)
