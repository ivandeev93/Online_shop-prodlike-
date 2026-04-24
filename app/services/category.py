from collections.abc import Sequence
from fastapi import HTTPException, status, Depends

from app.repositories.category import CategoryRepository

from app.models.categories import Category
from app.schemas import CategoryCreate


class CategoryService:

    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_all_categories(self, skip: int = 0, limit: int = 100) -> Sequence[Category]:
        return await self.category_repo.get_all(skip=skip, limit=limit)

    async def get_category_by_id(self, category_id: int) -> Category | None:
        return await self.category_repo.get_by_id(category_id)

    async def create_category(self, category: CategoryCreate) -> Category | None:
        existing_category = await self.category_repo.get_by_name(category.name)
        if existing_category:
            return None  # Возвращаем None, если категория с таким именем уже есть
        return await self.category_repo.create(category)

    async def update_category(self, category: CategoryCreate, category_id: int):
        existing_category = await self.category_repo.get_by_id(category_id)
        if not existing_category:
            return None
        category_with_same_name = await self.category_repo.get_by_name(category.name)

        if category_with_same_name and category_with_same_name.id != category_id:
            return None

        updated = await self.category_repo.update(category_id, category)

        if updated is None:
            return None

        return updated


    async def delete_category(self, category_id: int):
        existing_category = await self.category_repo.get_by_id(category_id)
        if not existing_category:
            return None

        return await self.category_repo.delete(category_id)




