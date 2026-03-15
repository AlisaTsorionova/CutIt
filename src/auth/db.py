from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session

from src.db import get_db
from src.models import User


def get_user_db(session: Session = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)
