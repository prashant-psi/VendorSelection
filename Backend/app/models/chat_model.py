from pydantic import BaseModel, Field


class ChatRequestModel(BaseModel):
    """Request body from the UI chat screen."""

    message: str = Field(..., description="User question or command")
    session_id: str | None = Field(None, description="Optional session id to keep conversation context")
    # Optional — users normally type names in message; IDs only if UI already has them
    product_id: str | None = Field(None, description="Product UUID (optional)")
    product_name: str | None = Field(None, description="Product name (optional)")
    product_code: str | None = Field(None, description="Product code e.g. PRD-00217 (optional)")
    vendor_id: str | None = Field(None, description="Vendor UUID (optional)")
    vendor_name: str | None = Field(None, description="Vendor name (optional)")
    request_id: str | None = Field(None, description="Procurement request id in context")


class ChatResponseModel(BaseModel):
    """Response sent back to the UI."""

    reply: str = Field(..., description="Natural language answer from the assistant")
    session_id: str = Field(..., description="Session id — send this back on the next message")
    data: dict | list | None = Field(None, description="Structured scores, rankings, or predictions when available")
    actions: list[str] = Field(default_factory=list, description="Which backend actions were run, e.g. rank_vendors")
