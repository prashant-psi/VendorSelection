import httpx
from config import settings

async def get(path: str, params: dict = {}) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BACKEND_URL}{path}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

async def post(path: str, data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.BACKEND_URL}{path}", json=data, timeout=30)
        response.raise_for_status()
        return response.json()
