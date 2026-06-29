from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from app.core.serialization import serialize_response
from app.models.chat_extraction_model import LlmExtractedFields
from app.models.chat_model import ChatResponseModel
from app.services.chat.context import set_chat_context
from app.services.chat.extractor import (
    build_follow_up,
    extract_fields_from_message,
    missing_for_ranking,
    should_attempt_ranking,
    to_session_fields,
)
from app.services.chat.llm import get_agent
from app.services.chat.ranking_service import rank_vendors
from app.services.chat.session_state import merge_session_fields
from app.services.chat.state import ChatState
from app.services.chat.tool_tracker import get_tool_tracking, reset_tool_tracking


def extract_node(state: ChatState) -> dict[str, Any]:
    message = state["message"]
    previous = state["previous_fields"]
    session_id = state["session_id"]

    extracted = extract_fields_from_message(message, previous)
    merged = merge_session_fields(session_id, to_session_fields(extracted, message))
    should_rank = should_attempt_ranking(message, extracted, previous)
    missing = missing_for_ranking(merged) if should_rank else []

    return {
        "extracted": extracted.model_dump(),
        "merged_fields": merged,
        "should_rank": should_rank,
        "missing_fields": missing,
    }


def route(state: ChatState) -> Literal["ask_missing", "rank", "agent"]:
    if not state["should_rank"]:
        return "agent"
    if state["missing_fields"]:
        return "ask_missing"
    return "rank"


def ask_missing_node(state: ChatState) -> dict[str, Any]:
    extracted = LlmExtractedFields(**state["extracted"])
    reply = build_follow_up(state["missing_fields"], extracted.follow_up_question)
    merge_session_fields(state["session_id"], {"ranking_in_progress": True})
    return {
        "response": ChatResponseModel(
            reply=reply,
            session_id=state["session_id"],
            data={"collected": state["merged_fields"], "missing_fields": state["missing_fields"]},
            actions=["awaiting_fields"],
        )
    }


def rank_node(state: ChatState) -> dict[str, Any]:
    merge_session_fields(state["session_id"], {"ranking_in_progress": False})
    response = rank_vendors(state["merged_fields"], state["session_id"], state["message"])
    return {"response": response}


def agent_node(state: ChatState) -> dict[str, Any]:
    fields = state["merged_fields"]
    message = state["message"]
    session_id = state["session_id"]

    set_chat_context(
        fields.get("product_id"),
        None,
        None,
        product_name=fields.get("product_name"),
        product_code=fields.get("product_code"),
        user_message=message,
    )
    reset_tool_tracking()
    merge_session_fields(session_id, {"ranking_in_progress": False})

    context_parts = []
    if fields.get("product_code"):
        context_parts.append(f"product_code={fields['product_code']}")
    if fields.get("product_name"):
        context_parts.append(f"product_name={fields['product_name']}")
    user_content = message
    if context_parts:
        user_content += f"\n\n[Context: {', '.join(context_parts)}]"

    try:
        result = get_agent().invoke(
            {"messages": [HumanMessage(content=user_content)]},
            config={"configurable": {"thread_id": session_id}},
        )
        messages = result.get("messages", [])
        reply = next(
            (m.content for m in reversed(messages) if isinstance(m, AIMessage) and m.content),
            "I could not generate a response.",
        )
    except Exception:
        reply = "How can I help you with vendor selection or procurement?"

    tool_actions, tool_data = get_tool_tracking()
    return {
        "response": ChatResponseModel(
            reply=reply,
            session_id=session_id,
            data=serialize_response(tool_data),
            actions=tool_actions,
        )
    }


def _build_graph():
    graph = StateGraph(ChatState)


    # graph nodes
    graph.add_node("extract", extract_node)
    graph.add_node("ask_missing", ask_missing_node)
    graph.add_node("rank", rank_node)
    graph.add_node("agent", agent_node)

    #graph edges
    graph.add_edge(START, "extract")
    graph.add_conditional_edges("extract", route)
    graph.add_edge("ask_missing", END)
    graph.add_edge("rank", END)
    graph.add_edge("agent", END)

    #compile the graph
    return graph.compile()


_chat_graph = None


def get_chat_graph():
    global _chat_graph
    if _chat_graph is None:
        _chat_graph = _build_graph()
    return _chat_graph
