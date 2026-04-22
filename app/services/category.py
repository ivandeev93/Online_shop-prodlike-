# CategoryService
from collections.abc import Sequence
from decimal import Decimal
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.core.dependencies import get_async_db

from app.models.categories import Category
from app.repositories.category import CategoryRepository

from app.schemas import Category as CategorySchema, CategoryCreate


class CategoryService:

    @staticmethod
    async def get_all_categories(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Category]:
        return await CategoryRepository.get_all(db, skip=skip, limit=limit)

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> Category | None:
        return await CategoryRepository.get_by_id(db, category_id)

    @staticmethod
    async def create_category(db: AsyncSession, category: CategoryCreate) -> Category | None:
        existing_category = await CategoryRepository.get_by_name(db, category.name)
        if existing_category:
            return None  # Возвращаем None, если категория с таким именем уже есть
        return await CategoryRepository.create(db, name=category.name)

    @staticmethod
    async def update_category():
        pass

    @staticmethod
    async def delete_category():
        pass




