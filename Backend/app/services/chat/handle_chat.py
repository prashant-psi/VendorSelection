import uuid

from app.models.chat_model import ChatRequest, ChatResponseModel
from app.services.chat.graph import get_chat_graph
from app.services.chat.session_state import get_session_fields


def handle_chat(request: ChatRequest) -> ChatResponseModel:
    session_id = request.session_id or str(uuid.uuid4())
    previous = get_session_fields(session_id)

    result = get_chat_graph().invoke({
        "session_id": session_id,
        "message": request.message,
        "previous_fields": previous,
        "extracted": {},
        "merged_fields": {},
        "missing_fields": [],
        "should_rank": False,
        "response": None,
    })

    return result["response"]
