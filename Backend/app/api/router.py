from fastapi import APIRouter

from app.api.endpoints import chat, model, users, utils, vendors

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(vendors.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(model.router)