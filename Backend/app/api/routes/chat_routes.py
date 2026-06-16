import json

from fastapi import APIRouter, HTTPException, Request

from app.models.chat_model import ChatRequestModel, ChatResponseModel
from app.services import chat_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponseModel)
async def chat(request: Request):
    """
    Chat with the procurement assistant.

    The assistant can answer questions and return scores, rankings, and predictions
    by calling the same scoring services used by the REST API.

    Send session_id from the previous response to continue the conversation.

    Postman: Body -> raw -> JSON (not Text). Header must be Content-Type: application/json
    """
    body = await _parse_json_body(request)
    chat_request = ChatRequestModel(**body)
    return chat_service.handle_chat(chat_request)


async def _parse_json_body(request: Request) -> dict:
    """
    Parse JSON body from the request.

    Postman sometimes sends valid JSON with Content-Type: text/plain, which makes
    FastAPI pass a string instead of a dict. This helper handles both cases.
    """
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            parsed = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc
    else:
        raw = await request.body()
        if not raw:
            raise HTTPException(status_code=400, detail="Request body is empty")
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Body must be valid JSON. In Postman: Body -> raw -> select JSON "
                    "(not Text), and use format: {\"message\": \"Hi\"}"
                ),
            ) from exc

    if isinstance(parsed, str):
        # Double-encoded JSON string — parse again
        try:
            parsed = json.loads(parsed)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=400,
            detail='Body must be a JSON object, e.g. {"message": "Hi"}',
        )

    return parsed
