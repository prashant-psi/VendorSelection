from fastapi import APIRouter

from app.models.chat_model import ChatRequest, ChatResponseModel
from app.services.chat.handle_chat import handle_chat

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponseModel)
async def chat(body: ChatRequest) -> ChatResponseModel:
    """
    Send natural language in JSON:

      { "message": "suggest vendors for Resistors Grade-A, 50 items" }

    Continue a conversation:

      { "message": "missing fields", "session_id": "<from previous response>" }
    """
    return handle_chat(body)
