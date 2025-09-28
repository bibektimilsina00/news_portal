from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.models import *  # Import all models to register them with SQLAlchemy
from app.modules.users.crud.crud_user import crud_user
from app.modules.users.model.user import User
from app.modules.users.schema.user import UserCreate
from app.shared.enums.account_type import AccountType

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        # Extract username from email (part before @)
        username = settings.FIRST_SUPERUSER.split("@")[0]
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            username=username,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            full_name="Super User",
            account_type=AccountType.personal,
        )
        user = crud_user.create(session=session, obj_in=user_in)
