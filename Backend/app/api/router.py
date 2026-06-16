from fastapi import APIRouter

from app.api.routes import chat_routes
from app.api.routes import ranking_routes
from app.api.routes import scoring_routes
from app.api.routes import utils_routes
from app.api.routes import user_routes
from app.api.routes import vendor_routes

api_router = APIRouter()
api_router.include_router(vendor_routes.router, tags=["vendors"])
api_router.include_router(user_routes.router, tags=["users"])
api_router.include_router(utils_routes.router, tags=["utils"])
api_router.include_router(ranking_routes.router, tags=["rank"])
api_router.include_router(scoring_routes.router, tags=["scoring"])
api_router.include_router(chat_routes.router, tags=["chat"])
