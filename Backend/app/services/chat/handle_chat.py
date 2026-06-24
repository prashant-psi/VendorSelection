import uuid
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from app.core.serialization import serialize_response
from app.models.chat_model import ChatRequest, ChatResponseModel
from app.services.chat.context import set_chat_context
from app.services.chat.extractor import (
    build_follow_up,
    extract_fields_from_message,
    missing_for_ranking,
    to_session_fields,
    wants_ranking,
)
from app.services.chat.llm import get_agent
from app.services.chat.session_state import get_session_fields, merge_session_fields
from app.services.chat.tool_tracker import get_tool_tracking, reset_tool_tracking
from app.services.chat.ranking_service import rank_vendors


def handle_chat(request: ChatRequest) -> ChatResponseModel:
    session_id = request.session_id or str(uuid.uuid4())

    previous = get_session_fields(session_id)

    extracted_fields = extract_fields_from_message(request.message, previous)

    fields = merge_session_fields(session_id, to_session_fields(extracted_fields, request.message))

    if wants_ranking(fields):
        missing = missing_for_ranking(fields)
        if missing:
            return ChatResponseModel(
                reply=build_follow_up(missing, extracted_fields.follow_up_question),
                session_id=session_id,
                data={"collected": fields, "missing_fields": missing},
                actions=["awaiting_fields"],
            )

        ranking_response = rank_vendors(fields, session_id, request.message)
        if ranking_response:
            return ranking_response

    return _general_chat_reply(request.message, fields, session_id)


def _general_chat_reply(message: str, fields: dict[str, Any], session_id: str) -> ChatResponseModel:
    set_chat_context(
        fields.get("product_id"),
        None,
        None,
        product_name=fields.get("product_name"),
        product_code=fields.get("product_code"),
        user_message=message,
    )
    reset_tool_tracking()

    try:
        context = []
        if fields.get("product_code"):
            context.append(f"product_code={fields['product_code']}")
        if fields.get("product_name"):
            context.append(f"product_name={fields['product_name']}")
        user_content = message
        if context:
            user_content += f"\n\n[Context: {', '.join(context)}]"

        result = get_agent().invoke(
            {"messages": [HumanMessage(content=user_content)]},
            config={"configurable": {"thread_id": session_id}},
        )
        messages = result.get("messages", [])
        reply = next((m.content for m in reversed(messages) if isinstance(m, AIMessage) and m.content), "I could not generate a response.")
    except Exception:
        reply = "How can I help you with vendor selection or procurement?"

    tool_actions, tool_data = get_tool_tracking()
    return ChatResponseModel(
        reply=reply,
        session_id=session_id,
        data=serialize_response(tool_data),
        actions=tool_actions,
    )
