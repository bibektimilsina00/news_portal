import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.users.schema.user import UserBase

if TYPE_CHECKING:
    from app.modules.news.model.item import Item


class User(UserBase, table=True):
    """User database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
