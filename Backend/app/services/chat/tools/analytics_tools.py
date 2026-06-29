import json

from langchain_core.tools import tool

from app.services import utils_service, vendor_service
from app.services.chat.context import get_chat_context
from app.services.chat.tools._helpers import _save_tool_result


@tool
def get_recommendations(request_id: str = "") -> str:
    """Get stored vendor recommendations for a procurement request ID. Use when user asks to see previous recommendations."""
    ctx = get_chat_context()
    rid = request_id or ctx.get("request_id")
    if not rid:
        return json.dumps({"error": "request_id is required"})
    return _save_tool_result("get_recommendations", vendor_service.get_recommendations_by_request(rid))


@tool
def get_weather_logistics_impact(event_types: list[str]) -> str:
    """Get weather and logistics disruption impact for given event types (e.g. ['flood', 'storm', 'hurricane']). Use when user asks about supply chain risks from weather."""
    if not event_types:
        return json.dumps({"error": "event_types is required, e.g. ['flood', 'storm']"})
    return _save_tool_result("get_weather_logistics_impact", utils_service.weather_logistics_impact(event_types))


@tool
def get_compliance_certifications() -> str:
    """Get all compliance certifications available in the system — ISO, safety, quality standards. Use when user asks what certifications vendors can have."""
    return _save_tool_result("get_compliance_certifications", utils_service.get_compilance_certificates())


@tool
def get_weight_configs() -> str:
    """Get all scoring weight configurations — how quality, risk, ESG, reliability are weighted. Use when user asks how vendors are scored or wants to understand scoring criteria."""
    return _save_tool_result("get_weight_configs", utils_service.get_weight_configs())
