import uuid
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from app.models.chat_model import ChatRequestModel, ChatResponseModel
from app.services import llm_service
from app.services.chat_context import set_chat_context
from app.services.chat_tools import get_tool_tracking, reset_tool_tracking
from app.services.product_resolver import extract_product_code
from app.services.chat_tools import _serialize as serialize_data


def handle_chat(request: ChatRequestModel) -> ChatResponseModel:
    """
    Main entry point for POST /chat.

    Flow (LangGraph):
      user query -> LLM -> tool (scoring/ML) -> LLM -> reply + structured data
    """
    session_id = request.session_id or str(uuid.uuid4())

    # Pass names/ids to tools — users type product names, not UUIDs
    product_code = request.product_code or extract_product_code(request.message)

    set_chat_context(
        request.product_id,
        request.vendor_id,
        request.request_id,
        product_name=request.product_name,
        vendor_name=request.vendor_name,
        product_code=product_code,
        user_message=request.message,
    )
    reset_tool_tracking()

    user_content = request.message
    context_parts = []
    if request.product_name:
        context_parts.append(f"product_name={request.product_name}")
    if product_code:
        context_parts.append(f"product_code={product_code}")
    if request.product_id:
        context_parts.append(f"product_id={request.product_id}")
    if request.vendor_name:
        context_parts.append(f"vendor_name={request.vendor_name}")
    if request.vendor_id:
        context_parts.append(f"vendor_id={request.vendor_id}")
    if request.request_id:
        context_parts.append(f"request_id={request.request_id}")
    if context_parts:
        user_content += f"\n\n[Context: {', '.join(context_parts)}]"

    agent = llm_service.get_agent()

    # LangGraph uses thread_id to remember conversation per session
    config = {"configurable": {"thread_id": session_id}}
    result = agent.invoke(
        {"messages": [HumanMessage(content=user_content)]},
        config=config,
    )

    reply = _extract_reply(result.get("messages", []))
    actions, tool_data = get_tool_tracking()

    return ChatResponseModel(
        reply=reply,
        session_id=session_id,
        data=serialize_data(tool_data),
        actions=actions,
    )


def _extract_reply(messages: list[Any]) -> str:
    """Get the final assistant text message from the LangGraph result."""
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            content = message.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                text_parts = [
                    part.get("text", "")
                    for part in content
                    if isinstance(part, dict) and part.get("type") == "text"
                ]
                if text_parts:
                    return "".join(text_parts)
    return "I could not generate a response."
