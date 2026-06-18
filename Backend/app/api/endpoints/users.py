from fastapi import APIRouter

from app.api.pagination import PaginationDep
from app.services import user_service

router = APIRouter(tags=["users"])


@router.get("/users")
def get_users(pagination: PaginationDep):
    return user_service.get_users(page=pagination.page, page_size=pagination.page_size)


@router.get("/users/{user_id}")
def get_user(user_id: str):
    return user_service.get_user(user_id=user_id)
