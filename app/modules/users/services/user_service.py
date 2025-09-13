import uuid
from typing import Any

from sqlmodel import Session

from app.modules.users.crud.crud_user import user
from app.modules.users.model.user import User
from app.modules.users.schema.user import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def create_user(*, session: Session, user_create: UserCreate) -> User:
        return user.create(session=session, obj_in=user_create)

    @staticmethod
    def get_user(session: Session, user_id: uuid.UUID) -> User | None:
        return user.get(session=session, id=user_id)

    @staticmethod
    def get_user_by_email(*, session: Session, email: str) -> User | None:
        return user.get_by_email(session=session, email=email)

    @staticmethod
    def get_users(session: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
        return user.get_multi(session=session, skip=skip, limit=limit)

    @staticmethod
    def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
        return user.update(session=session, db_obj=db_user, obj_in=user_in)

    @staticmethod
    def authenticate_user(
        *, session: Session, email: str, password: str
    ) -> User | None:
        return user.authenticate(session=session, email=email, password=password)

    @staticmethod
    def is_active(user: User) -> bool:
        return user.is_active

    @staticmethod
    def is_superuser(user: User) -> bool:
        return user.is_superuser

    @staticmethod
    def count_users(session: Session) -> int:
        return user.count(session=session)


user_service = UserService()
