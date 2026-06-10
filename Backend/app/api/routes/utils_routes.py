from fastapi import APIRouter
from app.services import utils_service


router = APIRouter()

#All utils routes

@router.get("/countries")
def get_countries():
    return utils_service.get_countries()