from typing import Optional, Any
from fastapi import Depends, Request
from fastapi_users import BaseUserManager
from src.models import User
from src.auth.db import get_user_db
from src.config import SECRET_KEY
from fastapi_users.exceptions import InvalidID


class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"Пользователь {user.id} зарегистрирован")

    def parse_id(self, value: Any) -> int:
        try:
            return int(value)
        except ValueError:
            raise InvalidID()


def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
