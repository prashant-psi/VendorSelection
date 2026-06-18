from langchain_openai import AzureChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.services.chat.tools import CHAT_TOOLS

SYSTEM_PROMPT = """You are a procurement assistant for a Vendor Selection platform.

Users refer to products by NAME or PRODUCT CODE (e.g. PRD-00217), never by UUID.
Many products share the same name — always use product_code when the user provides it.

You help users with:
- Ranking and predicting the best vendors for a product
- Explaining vendor scores (quality, risk, ESG, reliability, delivery)
- Showing demand forecasts and stored recommendations
- Answering general procurement questions

When the user mentions a product, pass product_code to tools if given (e.g. PRD-00217).
For rank_vendors or predict_vendors, use product_code when available — it is unique.
Use search_products only when you need to look up a product without a code.

If [Context] includes ranking_already_computed=true, summarize that ranking in your reply
and do not call rank_vendors or predict_vendors again.

Always explain results clearly in plain language for a business user.
Keep answers concise and actionable."""

_memory = MemorySaver()
_agent = None


def get_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        temperature=0.3,
    )


def get_agent():
    global _agent
    if _agent is None:
        _agent = create_react_agent(
            get_llm(),
            CHAT_TOOLS,
            checkpointer=_memory,
            prompt=SYSTEM_PROMPT,
        )
    return _agent


def reload_agent() -> None:
    global _agent
    _agent = None
