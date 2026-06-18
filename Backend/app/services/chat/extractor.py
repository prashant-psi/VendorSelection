import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.constants import RANKING_KEYWORDS
from app.models.chat_extraction_model import LlmExtractedFields
from app.services.chat.llm import get_llm
from app.services.procurement.builder import (
    extract_budget_usd,
    extract_product_name,
    extract_required_quantity,
    extract_result_limit,
    wants_vendor_ranking,
)
from app.services.procurement.resolver import extract_product_code

from app.prompts.extraction_prompt import EXTRACTION_SYSTEM


def extract_fields_from_message(message: str,previous: dict[str, Any]) ->LlmExtractedFields:
    try:
        llm = get_llm().with_structured_output(
            LlmExtractedFields
        )
        messages = [
            SystemMessage(content=EXTRACTION_SYSTEM),
            HumanMessage(
                content=f"""
                        Previous extracted fields:
                                {json.dumps(previous, default=str, indent=2)}

                        Current user message:
                                {message}

                        Update the extracted fields using the previous values and the current message.
                        """
                    ),
            ]

        result = llm.invoke(messages)
        extracted = (
            result if isinstance(result, LlmExtractedFields)
            else LlmExtractedFields.model_validate(result)
        )

        return _regex_enrich(extracted, message)

    except Exception as e:
        return _regex_only_extract(message)


def _regex_enrich(extracted: LlmExtractedFields, message: str) -> LlmExtractedFields:
    updates: dict[str, Any] = {}
    if not extracted.product_code:
        code = extract_product_code(message)
        if code:
            updates["product_code"] = code
    if not extracted.product_name:
        name = extract_product_name(message)
        if name:
            updates["product_name"] = name
    if not extracted.required_quantity:
        qty = extract_required_quantity(message, None)
        if qty:
            updates["required_quantity"] = qty
    if extracted.budget_usd is None:
        budget = extract_budget_usd(message, None)
        if budget is not None:
            updates["budget_usd"] = budget
    if not extracted.run_ranking and wants_vendor_ranking(message):
        updates["run_ranking"] = True
        updates["intent"] = "vendor_ranking"
    if extracted.result_limit is None:
        limit = extract_result_limit(message, None)
        if limit:
            updates["result_limit"] = limit
    return extracted.model_copy(update=updates) if updates else extracted


def _regex_only_extract(message: str) -> LlmExtractedFields:
    run_ranking = wants_vendor_ranking(message)
    return LlmExtractedFields(
        intent="vendor_ranking" if run_ranking else "unknown",
        run_ranking=run_ranking,
        product_code=extract_product_code(message),
        product_name=extract_product_name(message),
        required_quantity=extract_required_quantity(message, None),
        result_limit=extract_result_limit(message, None),
        budget_usd=extract_budget_usd(message, None),
    )


def to_session_fields(extracted: LlmExtractedFields, message: str) -> dict[str, Any]:
    fields = extracted.model_dump(exclude={"follow_up_question"}, exclude_none=True)
    fields["last_message"] = message
    return fields


def wants_ranking(fields: dict[str, Any]) -> bool:
    return bool(fields.get("run_ranking") or fields.get("intent") in ("vendor_ranking", "vendor_prediction"))


def missing_for_ranking(fields: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if not (fields.get("product_name") or fields.get("product_id")):
        missing.append("product name")
    if not fields.get("required_quantity"):
        missing.append("quantity (how many units)")
    return missing


def build_follow_up(missing: list[str], llm_question: str | None) -> str:
    if llm_question and llm_question.strip():
        return llm_question.strip()
    items = "\n".join(f"- {m}" for m in missing)
    return f"I need a little more information:\n{items}"


def build_product_choice_reply(error: dict[str, Any]) -> str:
    matches = error.get("matches") or []
    lines = [
        f"Multiple products match '{error.get('search_term', 'that name')}'. "
        "Please tell me which product code you mean:"
    ]
    for match in matches[:5]:
        code = match.get("product_code", "?")
        name = match.get("product_name", "")
        category = match.get("category", "")
        lines.append(f"  • {code} — {name} ({category})")
    lines.append("\nReply with the product code, e.g. PRD-00001")
    return "\n".join(lines)
