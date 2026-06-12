from fastapi import APIRouter

from app.api.routes import utils_routes
from app.api.routes import user_routes
from app.api.routes import vendor_routes

api_router = APIRouter()
api_router.include_router(vendor_routes.router, tags=["vendors"])
api_router.include_router(user_routes.router, tags=["users"])
api_router.include_router(utils_routes.router, tags=["utils"])
