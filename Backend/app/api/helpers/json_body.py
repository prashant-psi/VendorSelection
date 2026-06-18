import json

from fastapi import HTTPException, Request


async def parse_json_body(request: Request) -> dict:
    """
    Parse JSON body from the request.

    Handles Postman sending JSON with Content-Type: text/plain.
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
        try:
            parsed = json.loads(parsed)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail='Body must be a JSON object, e.g. {"message": "Hi"}')

    return parsed


# async def parse_chat_body(request: Request) -> dict:
    """Parse chat body — supports JSON object or plain text message."""
    content_type = request.headers.get("content-type", "")

    if "text/plain" in content_type:
        raw = (await request.body()).decode("utf-8").strip()
        if not raw:
            raise HTTPException(status_code=400, detail="Message text is empty")
        return {"message": raw}

    body = await parse_json_body(request)
    if isinstance(body, dict) and "message" not in body and len(body) == 1:
        only_value = next(iter(body.values()))
        if isinstance(only_value, str):
            return {"message": only_value}
    return body
