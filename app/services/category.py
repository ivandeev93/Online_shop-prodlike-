# CategoryService
from collections.abc import Sequence
from fastapi import HTTPException, status, Depends

from app.auth import get_current_user

from app.models.categories import Category
from app.repositories.category import CategoryRepository

from app.schemas import Category as CategorySchema, CategoryCreate


class CategoryService:
# ДОБАВИТЬ SELF
    @staticmethod
    async def get_all_categories(skip: int = 0, limit: int = 100) -> Sequence[Category]:
        return await CategoryRepository.get_all(skip=skip, limit=limit)

    @staticmethod
    async def get_category_by_id(category_id: int) -> Category | None:
        return await CategoryRepository.get_by_id(category_id)

    @staticmethod
    async def create_category(category: CategoryCreate) -> Category | None:
        existing_category = await CategoryRepository.get_by_name(category.name)
        if existing_category:
            return None  # Возвращаем None, если категория с таким именем уже есть
        return await CategoryRepository.create(category)

    @staticmethod
    async def update_category(category: CategoryCreate, category_id):
        existing_category = await CategoryRepository.get_by_id(category.id)
        if not existing_category:
            return None
        return await CategoryRepository.update(category, category_id=category_id)

    @staticmethod
    async def delete_category(category_id):
        existing_category = await CategoryRepository.get_by_id(category_id)
        if not existing_category:
            return None
        return await CategoryRepository.delete(category_id)




