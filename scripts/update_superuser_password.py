"""
Update the superuser's password in the database using Argon2.
"""

from app.core.db import engine
from sqlmodel import Session, select
from app.modules.users.model.user import User
from app.core.security import pwd_context
from app.core.config import settings

with Session(engine) as session:
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if user:
        user.hashed_password = pwd_context.hash(settings.FIRST_SUPERUSER_PASSWORD)
        session.add(user)
        session.commit()
        print("Superuser password rehashed with Argon2.")
    else:
        print("Superuser not found.")
