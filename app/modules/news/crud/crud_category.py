import uuid
from typing import List, Optional

from sqlalchemy import and_
from sqlmodel import Session, select

from app.modules.news.model.category import Category
from app.modules.news.schema.category import CategoryCreate, CategoryUpdate
from app.shared.crud.base import CRUDBase


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    """CRUD operations for news categories"""

    def get_by_slug(self, session: Session, *, slug: str) -> Optional[Category]:
        """Get category by slug"""
        statement = select(Category).where(Category.slug == slug)
        return session.exec(statement).first()

    def get_active_categories(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get active categories"""
        statement = (
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.sort_order)
        )
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_featured_categories(
        self, session: Session, *, skip: int = 0, limit: int = 20
    ) -> List[Category]:
        """Get featured categories"""
        statement = (
            select(Category)
            .where(and_(Category.is_active == True, Category.is_featured == True))  # type: ignore
            .order_by(Category.sort_order)
        )
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_parent_categories(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get parent categories (top-level)"""
        statement = (
            select(Category)
            .where(Category.parent_id == None)
            .order_by(Category.sort_order)
        )
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_child_categories(
        self, session: Session, *, parent_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get child categories for a parent"""
        statement = (
            select(Category)
            .where(Category.parent_id == parent_id)
            .order_by(Category.sort_order)
        )
        return list(session.exec(statement.offset(skip).limit(limit)))

    def get_by_news_count(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get categories ordered by news count"""
        statement = (
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.news_count.desc())  # type: ignore
        )
        return list(session.exec(statement.offset(skip).limit(limit)))

    def increment_news_count(
        self, session: Session, *, category_id: uuid.UUID
    ) -> Optional[Category]:
        """Increment news count for category"""
        category = self.get(session=session, id=category_id)
        if category:
            category.increment_news_count()
            session.add(category)
            session.commit()
            session.refresh(category)
        return category

    def decrement_news_count(
        self, session: Session, *, category_id: uuid.UUID
    ) -> Optional[Category]:
        """Decrement news count for category"""
        category = self.get(session=session, id=category_id)
        if category:
            category.decrement_news_count()
            session.add(category)
            session.commit()
            session.refresh(category)
        return category


# Create singleton instance
category = CRUDCategory(Category)
