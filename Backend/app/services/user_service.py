from typing import Any
from app.repositories import users

#Users Details
def get_users(page:int =1 , page_size:int =20) -> dict[str, Any]:
    return users.get_users(page=page, page_size=page_size)

def get_user(user_id: str) -> list[dict[str, Any]]:
    return users.get_user(user_id=user_id)