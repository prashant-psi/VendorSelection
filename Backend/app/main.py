from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Vendor Selection API", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")
